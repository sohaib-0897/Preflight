import html
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from .auth import current_user, get_db, project_access, audit, Name
from .jobs import run_access, serialize
from .db import (
    ReleasePolicy,
    ReleaseDecision,
    HumanReview,
    ScenarioAttempt,
    Artifact,
    AgentVersion,
    Agent,
    Project,
    AccuracyAssessment,
)
from preflight_scoring import DEFAULT_POLICY, release_decision, compare_runs
from preflight_security import redact

router = APIRouter(prefix="/api/v1")


class PolicyConfig(BaseModel):
    min_success: float = Field(default=0.8, ge=0, le=1, allow_inf_nan=False)
    max_critical: int = Field(default=0, ge=0, le=100)
    max_latency_ms: float = Field(default=1000, gt=0, allow_inf_nan=False)
    min_samples: int = Field(default=8, ge=1, le=100000)
    required_scenarios: list[str] = Field(default_factory=list, max_length=100)
    required_benchmarks: list[str] = Field(default_factory=lambda: ["native"], max_length=20)
    required_reviews: int = Field(default=0, ge=0, le=100000)
    max_cost: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    required_security_checks: list[str] = Field(default_factory=list, max_length=30)
    max_high: int | None = Field(default=None, ge=0, le=100000)
    required_review_approvals: int = Field(default=0, ge=0, le=100000)
    honor_human_overrides: bool = False
    regression_tolerance: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)


class PolicyInput(Name):
    config: PolicyConfig


@router.post("/projects/{project_id}/policies", status_code=201)
def create_policy(
    project_id: str, body: PolicyInput, user=Depends(current_user), db=Depends(get_db)
):
    _, org = project_access(db, user, project_id, "admin")
    existing = (
        db.scalar(
            select(func.max(ReleasePolicy.version)).where(
                ReleasePolicy.project_id == project_id, ReleasePolicy.name == body.name
            )
        )
        or 0
    )
    policy = ReleasePolicy(
        project_id=project_id, name=body.name, version=existing + 1, config=body.config.model_dump()
    )
    db.add(policy)
    from sqlalchemy.exc import IntegrityError

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent policy version creation; refresh and retry")
    audit(db, user, org, "release_policy.create", policy.id)
    db.commit()
    return {
        "id": policy.id,
        "name": policy.name,
        "version": policy.version,
        "config": policy.config,
    }


@router.get("/projects/{project_id}/policies")
def policies(project_id: str, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    return [
        {"id": p.id, "name": p.name, "version": p.version, "config": p.config}
        for p in db.scalars(
            select(ReleasePolicy)
            .where(ReleasePolicy.project_id == project_id)
            .order_by(ReleasePolicy.version.desc())
            .limit(100)
        )
    ]


@router.get("/comparisons")
def comparison(baseline: str, candidate: str, user=Depends(current_user), db=Depends(get_db)):
    left, _ = run_access(db, user, baseline)
    right, _ = run_access(db, user, candidate)
    if left.project_id != right.project_id:
        raise HTTPException(422, "Comparison must remain within one project")
    return compare_runs(serialize(left, db, True), serialize(right, db, True))


@router.post("/runs/{run_id}/release")
def gate(run_id: str, body: dict, user=Depends(current_user), db=Depends(get_db)):
    run, org = run_access(db, user, run_id, "developer")
    policy = None
    if body.get("policy_id"):
        policy = db.get(ReleasePolicy, body["policy_id"])
        if not policy or policy.project_id != run.project_id:
            raise HTTPException(404, "Policy not found")
    config = policy.config if policy else DEFAULT_POLICY
    comparison = None
    if body.get("baseline_id"):
        baseline, _ = run_access(db, user, body["baseline_id"])
        if baseline.project_id != run.project_id:
            raise HTTPException(422, "Baseline must belong to the project")
        comparison = compare_runs(serialize(baseline, db, True), serialize(run, db, True))
    attempts = select(ScenarioAttempt.id).where(ScenarioAttempt.run_id == run_id)
    # Count unique reviewed attempts, not repeated override records.
    reviews = (
        db.scalar(
            select(func.count(func.distinct(HumanReview.attempt_id))).where(
                HumanReview.attempt_id.in_(attempts)
            )
        )
        or 0
    )
    summary = dict(run.summary)
    override_count = 0
    if config.get("honor_human_overrides"):
        data = serialize(run, db, True)
        outcomes = []
        for attempt in data["attempts"]:
            if attempt["result"].get("kind") == "infrastructure":
                continue
            review = data["review_overrides"].get(attempt["id"])
            if review:
                override_count += 1
                if review["outcome"] == "INCONCLUSIVE":
                    outcomes.append(None)
                else:
                    outcomes.append(review["outcome"] == "PASSED")
            else:
                outcomes.append(attempt["result"]["assessment"]["task_success"])
        if outcomes and None not in outcomes:
            summary["task_success_rate"] = sum(outcomes) / len(outcomes)
        else:
            summary["task_success_rate"] = None
    latest_reviews = serialize(run, db, True)["review_overrides"]
    approvals = sum(r["outcome"] == "PASSED" for r in latest_reviews.values())
    decision = release_decision(
        summary, run.config, config, reviews, comparison, run.status, approvals=approvals
    )
    decision["approved_attempts"] = approvals
    decision["human_overrides_applied"] = override_count
    decision["automatic_summary_preserved"] = run.summary
    decision.update(
        {
            "policy_id": policy.id if policy else None,
            "policy_version": policy.version if policy else 1,
            "run_id": run_id,
            "reviewed_attempts": reviews,
        }
    )
    db.add(ReleaseDecision(run_id=run_id, payload=decision))
    audit(db, user, org, "release.evaluate", run_id)
    db.commit()
    return decision


def report_data(run, db):
    data = serialize(run, db, True)
    data["release_decisions"] = [
        d.payload
        for d in db.scalars(
            select(ReleaseDecision)
            .where(ReleaseDecision.run_id == run.id)
            .order_by(ReleaseDecision.created_at)
        )
    ]
    version = db.get(AgentVersion, run.version_id)
    agent = db.get(Agent, version.agent_id)
    project = db.get(Project, run.project_id)
    data["schema_version"] = "0.2.0"
    data["agent"] = {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "framework": agent.framework,
        "version_id": version.id,
        "version": version.version,
        "fingerprint": version.fingerprint,
        "configuration": version.config,
    }
    data["project"] = {"id": project.id, "name": project.name, "workspace_id": project.workspace_id}
    from preflight_benchmarks import registry

    descriptor = next(b for b in registry() if b["id"] == run.config["benchmark"])
    data["benchmark"] = {
        k: descriptor.get(k) for k in ["id", "name", "source", "license", "verification_level"]
    }
    data["benchmark"].update(
        {
            "version": run.config["benchmark_version"],
            "package_version": run.config.get("package_version"),
        }
    )
    attempt_ids = [a["id"] for a in data["attempts"]]
    data["assessment_history"] = [
        {"attempt_id": a.attempt_id, "id": a.id, "created_at": a.created_at, **a.payload}
        for a in db.scalars(
            select(AccuracyAssessment)
            .where(AccuracyAssessment.attempt_id.in_(attempt_ids))
            .order_by(AccuracyAssessment.created_at)
        )
    ]
    data["human_review_history"] = [
        {
            "attempt_id": r.attempt_id,
            "review_id": r.id,
            "reviewer_id": r.user_id,
            "outcome": r.outcome,
            "justification": r.justification,
            "at": r.at,
        }
        for r in db.scalars(
            select(HumanReview)
            .where(HumanReview.attempt_id.in_(attempt_ids))
            .order_by(HumanReview.at)
        )
    ]
    data["security_findings"] = [
        {**f, "scenario_id": a["scenario_id"], "attempt_id": a["id"]}
        for a in data["attempts"]
        for f in a["result"].get("security_findings", [])
    ]
    data["coverage"] = {
        "selected_scenarios": run.config["scenarios"],
        "attempts_recorded": len(data["attempts"]),
        "expected_attempts": len(run.config["scenarios"]) * run.config["trials"],
        "security_checks": run.summary.get("security_check_statuses", {}),
        "accuracy_dimensions": run.summary.get("dimensions", {}),
    }
    data["official_results"] = [
        {"attempt_id": a["id"], **a["result"]["official_evidence"]}
        for a in data["attempts"]
        if "official_evidence" in a["result"]
    ]
    data["limitations"] = [
        "Recorded scenario evidence is not a production security certification.",
        "Missing usage, unassessed accuracy and unexecuted checks remain unknown.",
        "Native/official scripted fixtures do not estimate arbitrary model quality.",
        "Provider-reported events/usage are distinguished from independently captured broker evidence.",
    ]
    data["reproduction"] = {
        "agent_fingerprint": version.fingerprint,
        "agent_configuration": version.config,
        "suite_version": run.config["benchmark_version"],
        "seed": run.config["seed"],
        "trials": run.config["trials"],
        "execution": run.config["backend"],
        "instructions": "Register the recorded agent/gateway configuration, preserve benchmark version, scenario/dataset fingerprint and evidence source versions, seed and trials, then queue with a fresh idempotency key. Official presets require their pinned environments. Remote/stochastic reruns differ from recorded native broker replay. Latency varies.",
    }
    return redact(data)


@router.get("/runs/{run_id}/report.json")
def report_json(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id)
    return Response(
        json.dumps(report_data(run, db), indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="preflight-{run.id}.json"'},
    )


@router.get("/runs/{run_id}/report.html", response_class=HTMLResponse)
def report_html(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id)
    data = report_data(run, db)
    rows = "".join(
        f'<tr><th scope="row">{html.escape(a["scenario_id"])}</th><td>{a["trial"]}</td><td>{"INFRASTRUCTURE" if a["result"].get("kind") == "infrastructure" else "UNASSESSED" if a["result"]["assessment"]["task_success"] is None else "PASSED" if a["result"]["assessment"]["task_success"] else "FAILED"}</td></tr>'
        for a in data["attempts"]
    )
    content = f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Preflight evaluation report</title><style>body{{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;color:#18212b}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;padding:12px;border-bottom:1px solid #ccc}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f5f7;padding:20px}}</style><main><h1>Preflight evaluation report</h1><p>Run {run.id} · {run.status}</p><p>Recorded scenario evidence. This report does not certify production security.</p><h2>Identity and coverage</h2><pre>{html.escape(json.dumps({k: data[k] for k in ["agent", "project", "benchmark", "coverage"]}, indent=2))}</pre><h2>Summary</h2><pre>{html.escape(json.dumps(data["summary"], indent=2))}</pre><h2>Scenario results</h2><table><caption>Scored attempts</caption><thead><tr><th>Scenario</th><th>Trial</th><th>Outcome</th></tr></thead><tbody>{rows}</tbody></table><h2>Security findings</h2><pre>{html.escape(json.dumps(data["security_findings"], indent=2))}</pre><h2>Release decisions</h2><pre>{html.escape(json.dumps(data["release_decisions"], indent=2))}</pre><h2>Human review history</h2><pre>{html.escape(json.dumps(data["human_review_history"], indent=2))}</pre><h2>Complete evidence and reproduction</h2><pre>{html.escape(json.dumps(data, indent=2))}</pre></main></html>'
    return HTMLResponse(
        content,
        headers={
            "Content-Disposition": f'attachment; filename="preflight-{run.id}.html"',
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'",
        },
    )


@router.post("/runs/{run_id}/artifacts", status_code=201)
def persist_report(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, org = run_access(db, user, run_id, "developer")
    from .storage import LocalStore

    try:
        metadata = LocalStore().put(json.dumps(report_data(run, db), indent=2).encode())
    except ValueError as exc:
        raise HTTPException(413, str(exc))
    artifact = Artifact(run_id=run_id, payload=metadata)
    db.add(artifact)
    db.flush()
    audit(db, user, org, "artifact.export", artifact.id)
    db.commit()
    return {"id": artifact.id, "run_id": run_id, **metadata}


@router.get("/runs/{run_id}/artifacts")
def artifact_list(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run_access(db, user, run_id)
    return [
        {"id": a.id, "run_id": run_id, **a.payload}
        for a in db.scalars(select(Artifact).where(Artifact.run_id == run_id))
    ]


@router.get("/artifacts/{artifact_id}")
def download_artifact(artifact_id: str, user=Depends(current_user), db=Depends(get_db)):
    artifact = db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(404, "Artifact not found")
    run_access(db, user, artifact.run_id)
    from .storage import LocalStore
    import hashlib

    try:
        data = LocalStore().get(artifact.payload["key"])
    except (ValueError, OSError):
        raise HTTPException(404, "Artifact unavailable")
    if hashlib.sha256(data).hexdigest() != artifact.payload["sha256"]:
        raise HTTPException(409, "Artifact integrity verification failed")
    return Response(
        data,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="preflight-artifact-{artifact.id}.json"'
        },
    )


@router.get("/runs/{run_id}/report.pdf")
def report_pdf(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    from .pdf_report import render_pdf

    run, _ = run_access(db, user, run_id)
    try:
        data = render_pdf(report_data(run, db))
    except ValueError as exc:
        raise HTTPException(413, str(exc))
    return Response(
        data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="preflight-{run.id}.pdf"'},
    )
