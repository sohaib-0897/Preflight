import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .auth import current_user, get_db
from .jobs import RunInput, create_run, run_access
from .db import ScenarioAttempt
from sqlalchemy import select

router = APIRouter(prefix="/api/v1")


class ScanInput(BaseModel):
    version_id: str
    mode: str = "basic"
    authorized_target: bool = False
    benchmark: str = "native"
    backend: str = "trusted-demo"
    trials: int = Field(default=1, ge=1, le=4)


@router.post("/projects/{project_id}/security-scans", status_code=201)
async def scan(project_id: str, body: ScanInput, user=Depends(current_user), db=Depends(get_db)):
    if body.mode not in {"basic", "adversarial"}:
        raise HTTPException(422, "Choose basic or adversarial")
    if body.benchmark not in {"native", "agentdojo"} or (
        body.benchmark == "agentdojo" and body.mode != "adversarial"
    ):
        raise HTTPException(422, "Official AgentDojo scan requires adversarial mode")
    request = RunInput(
        benchmark=body.benchmark,
        version_id=body.version_id,
        idempotency_key=uuid.uuid4().hex,
        security_mode=body.mode,
        authorized_target=body.authorized_target,
        backend=body.backend,
        trials=body.trials,
        scenarios=["user_task_0"]
        if body.benchmark == "agentdojo"
        else ["prompt-injection", "unauthorized", "tool-timeout"]
        if body.mode == "basic"
        else ["prompt-injection", "unauthorized"],
        timeout_seconds=60,
    )
    return await create_run(project_id, request, user, db)


@router.get("/runs/{run_id}/security")
def report(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id)
    attempts = list(db.scalars(select(ScenarioAttempt).where(ScenarioAttempt.run_id == run_id)))
    findings: list[dict] = []
    checks: list[dict] = []
    for attempt in attempts:
        findings.extend(
            {
                **finding,
                "agent_version": run.version_id,
                "scenario_id": attempt.scenario_id,
                "attempt_id": attempt.id,
            }
            for finding in attempt.result.get("security_findings", [])
        )
        checks.extend(
            {**check, "scenario_id": attempt.scenario_id, "attempt_id": attempt.id}
            for check in attempt.result.get("security_checks", [])
        )
    return {
        "run_id": run.id,
        "mode": run.config.get("security_mode"),
        "status": "FAIL"
        if findings or any(c["status"] == "FAILED" for c in checks)
        else "INCONCLUSIVE"
        if not checks
        or run.status != "COMPLETED"
        or any(c["status"] in {"INCONCLUSIVE", "NOT_RUN"} for c in checks)
        else "PASS",
        "findings": findings,
        "checks": checks,
        "limitations": "Coverage results per controlled test, no arbitrary security percentage. NOT_RUN or unknown evidence is not a pass. Native agents are scripted fixtures, connected targets require operator authorization.",
    }


class Dependency(BaseModel):
    name: str = Field(min_length=1, max_length=160, pattern=r"^[a-zA-Z0-9@/_.-]+$")
    version: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9+_.-]+$")
    ecosystem: str = "PyPI"


class DependencyInput(BaseModel):
    packages: list[Dependency] = Field(min_length=1, max_length=20)
    share_package_metadata: bool = False


@router.post("/runs/{run_id}/dependency-scan", status_code=201)
def dependency_scan(
    run_id: str, body: DependencyInput, user=Depends(current_user), db=Depends(get_db)
):
    import json
    from .auth import audit
    from .db import Artifact
    from .storage import LocalStore
    from preflight_security.dependencies import query_dependencies

    run, org = run_access(db, user, run_id, "developer")
    if not body.share_package_metadata:
        raise HTTPException(
            422, "Explicit consent to send package names/versions to OSV is required"
        )
    if any(p.ecosystem not in {"PyPI", "npm"} for p in body.packages):
        raise HTTPException(422, "Supported ecosystems are PyPI and npm")
    result = query_dependencies([p.model_dump() for p in body.packages])
    result["run_id"] = run.id
    metadata = LocalStore().put(json.dumps(result).encode())
    artifact = Artifact(run_id=run_id, payload={**metadata, "type": "dependency-scan"})
    db.add(artifact)
    db.flush()
    audit(db, user, org, "security.dependencies", artifact.id)
    db.commit()
    return {"artifact_id": artifact.id, **result}
