import copy
import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from .auth import current_user, get_db, project_access, audit, Name, authorize, ROLE_RANK
from .jobs import run_access
from .db import (
    EvidenceSource,
    ReviewAssignment,
    ScenarioAttempt,
    EvaluationRun,
    User,
    Membership,
    HumanReview,
    AccuracyAssessment,
)
from preflight_scoring.realitycheck import apply_checks, verify_claims
from preflight_security import redact

router = APIRouter(prefix="/api/v1")


class Rules(BaseModel):
    expected_output: dict | None = None
    expected_state: dict | None = None
    tolerances: dict[str, float] = Field(default_factory=dict)
    expected_tools: list[str] = Field(default_factory=list, max_length=16)
    prohibited_tools: list[str] = Field(default_factory=list, max_length=16)
    expected_sequence: list[str] = Field(default_factory=list, max_length=16)
    sql_assertions: list[dict] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def valid(self):
        import math

        if any(not math.isfinite(v) or v < 0 for v in self.tolerances.values()):
            raise ValueError("Tolerances must be finite and non-negative")
        for item in self.sql_assertions:
            if (
                not isinstance(item.get("query"), str)
                or len(item["query"]) > 2048
                or "expected" not in item
            ):
                raise ValueError("SQL assertion requires a bounded query and expected value")
            if (
                type(item.get("tolerance", 0)) not in (int, float)
                or not math.isfinite(item.get("tolerance", 0))
                or item.get("tolerance", 0) < 0
            ):
                raise ValueError("Invalid SQL tolerance")
        return self


class SourceInput(Name):
    uri: str = Field(min_length=1, max_length=2048)
    facts: dict = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def valid(self):
        import math
        import re

        for key, value in self.facts.items():
            if (
                not re.fullmatch(r"[\w.-]{1,120}", key)
                or type(value) not in (str, int, float, bool)
                or isinstance(value, str)
                and len(value) > 2048
                or type(value) is float
                and not math.isfinite(value)
            ):
                raise ValueError("Facts must be bounded named scalar values")
        return self


def source_records(db, project_id, ids):
    records = []
    for source_id in ids:
        item = db.get(EvidenceSource, source_id)
        if not item or item.project_id != project_id:
            raise HTTPException(404, "Evidence source not found")
        records.append(
            {
                "id": item.id,
                "name": item.name,
                "version": item.version,
                "uri": item.uri,
                "facts": item.facts,
                "fingerprint": item.fingerprint,
                "created_at": item.created_at,
            }
        )
    return records


@router.post("/projects/{project_id}/sources", status_code=201)
def create_source(
    project_id: str, body: SourceInput, user=Depends(current_user), db=Depends(get_db)
):
    _, org = project_access(db, user, project_id, "admin")
    version = (
        db.scalar(
            select(func.max(EvidenceSource.version)).where(
                EvidenceSource.project_id == project_id, EvidenceSource.name == body.name
            )
        )
        or 0
    ) + 1
    fingerprint = hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True).encode()).hexdigest()
    item = EvidenceSource(
        project_id=project_id,
        name=body.name,
        version=version,
        uri=body.uri,
        facts=body.facts,
        fingerprint=fingerprint,
    )
    db.add(item)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent source version creation; retry")
    audit(db, user, org, "evidence_source.create", item.id)
    db.commit()
    return source_records(db, project_id, [item.id])[0]


@router.get("/projects/{project_id}/sources")
def sources(project_id: str, q: str = "", user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    ids = list(
        db.scalars(
            select(EvidenceSource.id)
            .where(
                EvidenceSource.project_id == project_id,
                EvidenceSource.name.ilike("%" + q[:120] + "%"),
            )
            .order_by(EvidenceSource.created_at.desc())
            .limit(100)
        )
    )
    return source_records(db, project_id, ids)


class ClaimInput(BaseModel):
    claims: list[dict] = Field(max_length=64)
    source_ids: list[str] = Field(max_length=16)

    @model_validator(mode="after")
    def valid(self):
        if any(not isinstance(c.get("subject"), str) or "value" not in c for c in self.claims):
            raise ValueError("Explicit subject/value claims required")
        return self


@router.post("/projects/{project_id}/verify-claims")
def claims(project_id: str, body: ClaimInput, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id, "developer")
    return redact(verify_claims(body.claims, source_records(db, project_id, body.source_ids)))


class AssessmentInput(BaseModel):
    rules: Rules
    source_ids: list[str] = Field(default_factory=list, max_length=16)


@router.post("/runs/{run_id}/attempts/{attempt_id}/realitycheck", status_code=201)
def assess_attempt(
    run_id: str,
    attempt_id: str,
    body: AssessmentInput,
    user=Depends(current_user),
    db=Depends(get_db),
):
    run, org = run_access(db, user, run_id, "developer")
    attempt = db.get(ScenarioAttempt, attempt_id)
    if not attempt or attempt.run_id != run.id:
        raise HTTPException(404, "Attempt not found")
    if attempt.result.get("kind") == "infrastructure":
        raise HTTPException(409, "No agent evidence available")
    result = apply_checks(
        copy.deepcopy(attempt.result),
        body.rules.model_dump(),
        source_records(db, run.project_id, body.source_ids),
    )
    payload = {
        "method": "supplemental configurable RealityCheck",
        "rules": body.rules.model_dump(),
        "source_ids": body.source_ids,
        "assessment": result["assessment"],
        "original_automated_assessment_preserved": True,
    }
    item = AccuracyAssessment(attempt_id=attempt.id, payload=redact(payload))
    db.add(item)
    db.flush()
    audit(db, user, org, "realitycheck.assess", attempt.id)
    db.commit()
    return {"id": item.id, **item.payload}


@router.get("/runs/{run_id}/attempts/{attempt_id}/assessments")
def assessments(run_id: str, attempt_id: str, user=Depends(current_user), db=Depends(get_db)):
    run_access(db, user, run_id)
    attempt = db.get(ScenarioAttempt, attempt_id)
    if not attempt or attempt.run_id != run_id:
        raise HTTPException(404, "Attempt not found")
    return [
        {"id": item.id, "created_at": item.created_at, **item.payload}
        for item in db.scalars(
            select(AccuracyAssessment)
            .where(AccuracyAssessment.attempt_id == attempt_id)
            .order_by(AccuracyAssessment.created_at)
        )
    ]


class AssignInput(BaseModel):
    reviewer_email: str = Field(max_length=254)


@router.post("/runs/{run_id}/attempts/{attempt_id}/assign-review", status_code=201)
def assign(
    run_id: str, attempt_id: str, body: AssignInput, user=Depends(current_user), db=Depends(get_db)
):
    run, org = run_access(db, user, run_id, "admin")
    attempt = db.get(ScenarioAttempt, attempt_id)
    reviewer = db.scalar(select(User).where(User.email == body.reviewer_email.lower().strip()))
    membership = (
        db.scalar(
            select(Membership).where(Membership.org_id == org, Membership.user_id == reviewer.id)
        )
        if reviewer
        else None
    )
    if not attempt or attempt.run_id != run.id or not membership:
        raise HTTPException(404, "Eligible reviewer or attempt not found")
    if ROLE_RANK[membership.role] < ROLE_RANK["developer"]:
        raise HTTPException(422, "Reviewer requires developer or higher role")
    item = ReviewAssignment(attempt_id=attempt_id, reviewer_id=reviewer.id, assigned_by=user.id)
    db.add(item)
    db.flush()
    audit(db, user, org, "review.assign", item.id)
    db.commit()
    return {"id": item.id, "status": item.status}


@router.get("/projects/{project_id}/review-queue")
def queue(project_id: str, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    items = db.scalars(
        select(ReviewAssignment)
        .join(ScenarioAttempt, ReviewAssignment.attempt_id == ScenarioAttempt.id)
        .join(EvaluationRun, ScenarioAttempt.run_id == EvaluationRun.id)
        .where(EvaluationRun.project_id == project_id)
        .order_by(ReviewAssignment.created_at.desc())
        .limit(100)
    )
    return [
        {
            "id": a.id,
            "attempt_id": a.attempt_id,
            "run_id": db.get(ScenarioAttempt, a.attempt_id).run_id,
            "reviewer": db.get(User, a.reviewer_id).email,
            "status": a.status,
            "assigned_at": a.created_at,
            "disagreement": len(
                set(
                    db.scalars(
                        select(HumanReview.outcome).where(HumanReview.attempt_id == a.attempt_id)
                    )
                )
            )
            > 1,
        }
        for a in items
    ]


class DecisionInput(BaseModel):
    outcome: str
    justification: str = Field(min_length=10, max_length=2000)

    @model_validator(mode="after")
    def valid(self):
        if (
            self.outcome not in {"PASSED", "FAILED", "INCONCLUSIVE"}
            or len(self.justification.strip()) < 10
        ):
            raise ValueError("Review outcome and justification required")
        return self


@router.post("/review-assignments/{assignment_id}/decision", status_code=201)
def decide(assignment_id: str, body: DecisionInput, user=Depends(current_user), db=Depends(get_db)):
    item = db.get(ReviewAssignment, assignment_id)
    attempt = db.get(ScenarioAttempt, item.attempt_id) if item else None
    if not attempt:
        raise HTTPException(404, "Review assignment not found")
    run, org = run_access(db, user, attempt.run_id, "developer")
    membership = authorize(db, user, org)
    if item.reviewer_id != user.id and ROLE_RANK[membership.role] < ROLE_RANK["admin"]:
        raise HTTPException(403, "Assignment belongs to another reviewer")
    if item.status != "OPEN":
        raise HTTPException(409, "Assignment already completed")
    changed = db.execute(
        update(ReviewAssignment)
        .where(ReviewAssignment.id == item.id, ReviewAssignment.status == "OPEN")
        .values(status="COMPLETED")
    )
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Assignment changed concurrently")
    item.status = "COMPLETED"
    review = HumanReview(
        attempt_id=attempt.id,
        user_id=user.id,
        outcome=body.outcome,
        justification=redact(body.justification.strip()),
    )
    db.add(review)
    db.flush()
    audit(db, user, org, "review.decision", item.id)
    db.commit()
    return {
        "id": review.id,
        "outcome": review.outcome,
        "original_automated_assessment_preserved": True,
    }
