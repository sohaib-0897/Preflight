import hashlib
import json
import os
import time
import uuid
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, update, func, text
from sqlalchemy.exc import IntegrityError
from .auth import current_user, get_db, project_access, audit
from .db import EvaluationRun, AgentVersion, Agent, RunTransition, ScenarioAttempt, TraceEvent, ToolCall, AccuracyAssessment, SecurityFinding, EvaluationConfiguration, HumanReview, Dataset
from preflight_eval import SCENARIOS, SCENARIO_IDS, execute, deterministic_replay
from preflight_eval.sandbox import DockerBackend, InfrastructureFailure
from preflight_scoring import aggregate
from preflight_security import redact
from preflight_benchmarks import registry

router = APIRouter(prefix="/api/v1")
ACTIVE = {"PREPARING", "RUNNING", "SCORING"}
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "BLOCKED"}
TRANSITIONS = {"CREATED": {"QUEUED", "CANCELLED"}, "QUEUED": {"PREPARING", "CANCELLED"}, "PREPARING": {"RUNNING", "BLOCKED", "FAILED", "CANCELLED"}, "RUNNING": {"QUEUED", "SCORING", "FAILED", "BLOCKED", "CANCELLED"}, "SCORING": {"COMPLETED", "FAILED", "BLOCKED", "CANCELLED"}}


class RunInput(BaseModel):
    version_id: str
    idempotency_key: str = Field(min_length=8, max_length=128)
    trials: int = Field(default=1, ge=1, le=8)
    seed: int = Field(default=42, ge=0, le=2**31-1)
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    scenarios: list[str] = Field(default_factory=lambda: SCENARIO_IDS[:])
    dataset_id: str | None = None
    benchmark: str = "native"
    backend: str = "trusted-demo"
    security_mode: str | None = None
    authorized_target: bool = False

    @field_validator("scenarios")
    @classmethod
    def scenarios_valid(cls, v):
        if not v or len(v) > 8 or len(v) != len(set(v)) or set(v)-set(SCENARIO_IDS + ["create_task_1", "user_task_0"]):
            raise ValueError("Select distinct registered scenarios")
        return sorted(v)

    @field_validator("backend")
    @classmethod
    def backend_valid(cls, v):
        if v not in {"trusted-demo", "docker"}:
            raise ValueError("Unsupported execution backend")
        return v


def run_access(db, user, run_id, role="viewer"):
    run = db.get(EvaluationRun, run_id)
    if not run:
        raise HTTPException(404, "Resource not found")
    _, org_id = project_access(db, user, run.project_id, role)
    return run, org_id


def transition(db, run, target, reason=""):
    if target not in TRANSITIONS.get(run.status, set()):
        raise ValueError(f"Illegal transition {run.status} -> {target}")
    previous = run.status
    changed = db.execute(update(EvaluationRun).where(EvaluationRun.id == run.id, EvaluationRun.status == previous).values(status=target))
    if changed.rowcount != 1:
        db.rollback()
        return False
    run.status = target
    db.add(RunTransition(run_id=run.id, previous=previous, current=target, reason=reason))
    db.commit()
    return True


def serialize(run, db, details=False):
    result = {"id": run.id, "project_id": run.project_id, "version_id": run.version_id, "status": run.status, "created_at": run.created_at, "config": run.config, "summary": run.summary}
    attempts = db.scalars(select(ScenarioAttempt).where(ScenarioAttempt.run_id == run.id).order_by(ScenarioAttempt.scenario_id, ScenarioAttempt.trial)).all()
    result["progress"] = {"completed": len(attempts), "total": len(run.config["scenarios"])*run.config["trials"]}
    if details:
        result["attempts"] = [{"id": a.id, "scenario_id": a.scenario_id, "trial": a.trial, "result": a.result} for a in attempts]
        result["transitions"] = [{"previous": t.previous, "current": t.current, "reason": t.reason, "at": t.at} for t in db.scalars(select(RunTransition).where(RunTransition.run_id == run.id).order_by(RunTransition.at))]
        latest_reviews = {}
        attempt_ids = [a.id for a in attempts]
        for review in db.scalars(select(HumanReview).where(HumanReview.attempt_id.in_(attempt_ids)).order_by(HumanReview.at)):
            latest_reviews[review.attempt_id] = {"outcome": review.outcome, "justification": review.justification, "review_id": review.id, "at": review.at}
        result["review_overrides"] = latest_reviews
        result["failure_clusters"] = dict(Counter(a.result.get("failure", {}).get("category", "unknown") for a in attempts if a.result.get("failure")))
        groups = {}
        for attempt in attempts:
            failure = attempt.result.get('failure')
            if failure:
                groups.setdefault(failure.get('category','unknown'),[]).append({'attempt_id':attempt.id,'scenario_id':attempt.scenario_id,'trial':attempt.trial,'verified':failure.get('verified',False)})
        result['failure_groups']=[{'category':category,'count':len(examples),'examples':examples} for category,examples in sorted(groups.items())]

    return result


@router.get("/benchmarks")
def benchmarks(user=Depends(current_user)):
    return registry()


@router.post("/projects/{project_id}/runs", status_code=201)
async def create_run(project_id: str, body: RunInput, user=Depends(current_user), db=Depends(get_db)):
    import asyncio
    result = await asyncio.to_thread(create_run_service, project_id, body, user, db)
    if os.environ.get("REDIS_URL"):
        try:
            from .arq_worker import enqueue
            await enqueue(result["id"])
        except Exception:
            import logging
            logging.getLogger("preflight").warning(json.dumps({"event":"redis_enqueue_unavailable","run_id":result["id"],"fallback":"database dispatch on recovery"}))
    return result


def create_run_service(project_id: str, body: RunInput, user=Depends(current_user), db=Depends(get_db)):
    _, org = project_access(db, user, project_id, "developer")
    version = db.get(AgentVersion, body.version_id)
    agent = db.get(Agent, version.agent_id) if version else None
    if not agent or agent.project_id != project_id:
        raise HTTPException(404, "Agent version not found in project")
    if body.security_mode not in {None,"basic","adversarial"}:
        raise HTTPException(422,"Unsupported security scan mode")
    if body.security_mode and (agent.framework!="native" or body.security_mode=="adversarial") and not body.authorized_target:
        raise HTTPException(422,"Explicit authorized-target confirmation required for connected or adversarial testing")
    if agent.framework != "native" and body.backend == "docker":
        raise HTTPException(422, "Remote agents execute in their operator-owned environment; Docker runner supports native fixtures only")
    if body.benchmark != "native":
        from preflight_benchmarks.execution import SPECS
        spec = SPECS.get(body.benchmark)
        if not spec or not next((b for b in registry() if b["id"] == body.benchmark and b["status"] == "AVAILABLE"), None):
            raise HTTPException(422, "Official offline benchmark environment unavailable; consult benchmark status")
        if agent.framework != "native" or version.config["mode"] not in ({"accurate", "regressed", "unsafe"} if body.benchmark == "agentdojo" and body.security_mode == "adversarial" else {"accurate", "regressed"}) or body.backend != "trusted-demo" or body.dataset_id:
            raise HTTPException(422, "Official smoke supports only the declared scripted native reference-agent preset in its isolated dependency environment")
    config = body.model_dump(exclude={"version_id", "idempotency_key"})
    if body.benchmark == "native":
        if set(config["scenarios"]) - set(SCENARIO_IDS):
            raise HTTPException(422, "Scenarios do not belong to the native benchmark")
    else:
        config["scenarios"] = [spec["scenario"]] if "scenarios" not in body.model_fields_set else config["scenarios"]
        if config["scenarios"] != [spec["scenario"]]:
            raise HTTPException(422, "Select the supported official scenario")
    if body.dataset_id:
        dataset = db.get(Dataset, body.dataset_id)
        if not dataset or dataset.project_id != project_id:
            raise HTTPException(404, "Dataset not found in project")
        config["scenarios"] = dataset.payload["scenario_ids"]
        config["dataset_fingerprint"] = dataset.payload["fingerprint"]
        config["custom_scenarios"] = dataset.payload.get("custom_scenarios",[])
        config["evidence_sources"] = dataset.payload.get("sources",[])
    active_cases = {"prompt-injection", "unauthorized"}
    selected_cases = set(config["scenarios"]) | {s["base_scenario"] for s in config.get("custom_scenarios", [])}
    if agent.framework != "native" and selected_cases & active_cases and not body.authorized_target:
        raise HTTPException(422, "Explicit authorized-target confirmation required for controlled adversarial cases")
    config.update({"benchmark_version": "1.0.0", "agent_fingerprint": version.fingerprint, "agent_framework": agent.framework, "execution_label": "trusted built-in code, not a sandbox" if body.backend == "trusted-demo" else "restricted Docker native runner"})
    if body.benchmark != "native":
        config.update({"benchmark_version":spec["version"], "package_version":spec["package_version"], "execution_label":"Official offline smoke, scripted reference agent, trusted upstream process; not a Docker sandbox or model-quality benchmark"})
    if agent.framework != "native":
        config["execution_label"] = "Connected agent in operator-owned environment; local broker side effects verified"
    existing = db.scalar(select(EvaluationRun).where(EvaluationRun.project_id == project_id, EvaluationRun.idempotency_key == body.idempotency_key))
    if existing:
        if {k:v for k,v in existing.config.items() if k != "_trace_context"} != config or existing.version_id != version.id:
            raise HTTPException(409, "Idempotency key already used with different configuration")
        return serialize(existing, db)
    if db.scalar(select(func.count()).select_from(EvaluationRun).where(EvaluationRun.project_id == project_id, EvaluationRun.status.in_(ACTIVE | {"QUEUED"}))) >= 20:
        raise HTTPException(429, "Project queued-run quota exceeded")
    from .telemetry import context_headers
    config["_trace_context"] = context_headers()
    run = EvaluationRun(project_id=project_id, version_id=version.id, idempotency_key=body.idempotency_key, config=config, status="CREATED")
    db.add(run)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Concurrent request reused the idempotency key; fetch existing runs")
    db.add(EvaluationConfiguration(run_id=run.id, payload=config))
    audit(db, user, org, "run.create", run.id)
    db.commit()
    transition(db, run, "QUEUED")
    return serialize(run, db)


@router.get("/projects/{project_id}/runs")
def list_runs(project_id: str, status: str | None = None, offset: int = 0, limit: int = 50, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    if offset < 0 or not 1 <= limit <= 100 or status and status not in set(TRANSITIONS) | TERMINAL:
        raise HTTPException(422, "Invalid pagination or status")
    query = select(EvaluationRun).where(EvaluationRun.project_id == project_id)
    if status:
        query = query.where(EvaluationRun.status == status)
    return [serialize(r, db) for r in db.scalars(query.order_by(EvaluationRun.created_at.desc()).offset(offset).limit(limit))]


@router.get("/runs/{run_id}")
def get_run(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id)
    return serialize(run, db, True)


@router.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, org = run_access(db, user, run_id, "developer")
    if run.status in TERMINAL:
        raise HTTPException(409, "Run is already terminal")
    if not transition(db, run, "CANCELLED", "Requested by authorized project member"):
        raise HTTPException(409, "Run changed concurrently")
    audit(db, user, org, "run.cancel", run.id)
    db.commit()
    return serialize(run, db)


def claim(db, run_id):
    # PostgreSQL project lock serializes quota decisions; SQLite serializes UPDATE writes.
    run = db.get(EvaluationRun, run_id)
    if not run or run.status != "QUEUED":
        return None
    if db.bind.dialect.name == "postgresql":
        lock_id = int.from_bytes(hashlib.sha256(run.project_id.encode()).digest()[:8], "big", signed=True)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_id})
    count = select(func.count()).select_from(EvaluationRun).where(EvaluationRun.project_id == run.project_id, EvaluationRun.status.in_(ACTIVE)).scalar_subquery()
    worker = str(uuid.uuid4())
    changed = db.execute(update(EvaluationRun).where(EvaluationRun.id == run_id, EvaluationRun.status == "QUEUED", count < 2).values(status="PREPARING", worker_id=worker, lease_until=time.time()+180))
    if changed.rowcount != 1:
        db.rollback()
        return None
    db.add(RunTransition(run_id=run_id, previous="QUEUED", current="PREPARING", reason="Worker claimed durable job"))
    db.commit()
    db.expire_all()
    return db.get(EvaluationRun, run_id)


def perform(database, run_id, stop=None):
    from .telemetry import tracer, propagator
    with database.sessions() as session:
        run=session.get(EvaluationRun,run_id)
        carrier=run.config.get('_trace_context',{}) if run else {}
    with tracer.start_as_current_span('evaluation.run',context=propagator.extract(carrier),record_exception=False,set_status_on_exception=False) as span:
        span.set_attribute('preflight.run_id',run_id)
        outcome=_perform(database,run_id,stop)
        span.set_attribute('preflight.execution_returned',bool(outcome))
        return outcome


def _perform(database, run_id, stop=None):
    with database.sessions() as db:
        run = claim(db, run_id)
        if not run:
            return False
        worker = run.worker_id
        def cancelled():
            if stop is not None and stop.is_set():
                return True
            with database.sessions() as check:
                latest = check.get(EvaluationRun, run_id)
                return latest.status != "RUNNING" or latest.worker_id != worker

        version = db.get(AgentVersion, run.version_id)
        config = run.config
        deadline = time.monotonic()+config["timeout_seconds"]
        if not transition(db, run, "RUNNING"):
            return False
        try:
            for scenario in config["scenarios"]:
                for trial in range(config["trials"]):
                    db.expire_all()
                    run = db.get(EvaluationRun, run_id)
                    if run.status != "RUNNING" or run.worker_id != worker:
                        return False
                    if cancelled():
                        if run.status == "RUNNING":
                            native = db.get(Agent, version.agent_id).framework == "native"
                            transition(db, run, "QUEUED" if native else "BLOCKED", "Worker interrupted; native fixtures safely resumable, connected side effects require review")
                        return False
                    remaining = deadline-time.monotonic()
                    if remaining <= 0:
                        transition(db, run, "BLOCKED", "Infrastructure execution deadline exceeded; not scored as an agent failure")
                        return False
                    existing = db.scalar(select(ScenarioAttempt).where(ScenarioAttempt.run_id == run_id, ScenarioAttempt.scenario_id == scenario, ScenarioAttempt.trial == trial))
                    if existing:
                        continue
                    custom = next((c for c in config.get("custom_scenarios",[]) if c["id"]==scenario),None)
                    execution_scenario = custom["base_scenario"] if custom else scenario
                    result = None
                    retry_budget = 2 if db.get(Agent, version.agent_id).framework == "native" else 1
                    for infrastructure_retry in range(retry_budget):
                        try:
                            if config["benchmark"] != "native":
                                from preflight_benchmarks.execution import execute_official
                                result = execute_official(config["benchmark"], scenario, version.config["mode"], config["seed"]+trial, max(.1, deadline-time.monotonic()), cancelled=cancelled, adversarial=config.get("security_mode")=="adversarial")
                            elif config["backend"] == "docker":
                                result = DockerBackend().execute(execution_scenario, version.config["mode"], config["seed"]+trial, max(.1, deadline-time.monotonic()), cancelled=cancelled)
                            elif db.get(Agent, version.agent_id).framework != "native":
                                from .connections import execute_connected
                                result = execute_connected(db, run, version, execution_scenario, config["seed"]+trial, max(.1, deadline-time.monotonic()), cancelled=cancelled, request_override=custom["request"] if custom else None)
                            else:
                                result = execute(execution_scenario, version.config["mode"], config["seed"]+trial)
                            if custom:
                                from preflight_scoring.realitycheck import apply_checks
                                result["scenario_id"] = scenario
                                result["custom_scenario"] = custom
                                result = apply_checks(result,custom,config.get("evidence_sources",[]))
                            break
                        except InfrastructureFailure as exc:
                            result = {"kind": "infrastructure", "scenario_id": scenario, "error": str(exc), "retry": infrastructure_retry, "failure": {"category": "infrastructure", "verified": True}}
                    db.expire_all()
                    run = db.get(EvaluationRun, run_id)
                    if run.status != "RUNNING" or run.worker_id != worker:
                        return False
                    from .telemetry import tracer, identifiers
                    from preflight_eval.diagnostics import diagnose
                    # Recorded event spans describe collection, not reconstructed model timing.
                    with tracer.start_as_current_span('evaluation.attempt.record',record_exception=False,set_status_on_exception=False) as span:
                        span.set_attribute('preflight.run_id',run_id)
                        span.set_attribute('preflight.scenario_id',scenario)
                        span.set_attribute('preflight.trial',trial)
                        result['telemetry']=identifiers(span)
                        for event in result.get('events',[]):
                            event.update(result['telemetry'])
                        result['diagnostics']=diagnose(result)
                    attempt = ScenarioAttempt(run_id=run_id, scenario_id=scenario, trial=trial, result=result)
                    db.add(attempt)
                    db.flush()
                    for event in result.get("events", []):
                        db.add(TraceEvent(attempt_id=attempt.id, payload=event))
                        if event["kind"] == "tool_call":
                            db.add(ToolCall(attempt_id=attempt.id, payload=event))
                    if "assessment" in result:
                        db.add(AccuracyAssessment(attempt_id=attempt.id, payload=result["assessment"]))
                    for finding in result.get("security_findings", []):
                        db.add(SecurityFinding(attempt_id=attempt.id, payload=finding))
                    run.lease_until = time.time()+180
                    db.commit()
            db.refresh(run)
            if not transition(db, run, "SCORING"):
                return False
            results = [a.result for a in db.scalars(select(ScenarioAttempt).where(ScenarioAttempt.run_id == run_id))]
            run.summary = aggregate(results)
            db.commit()
            transition(db, run, "BLOCKED" if run.summary["infrastructure_failures"] else "COMPLETED", "Infrastructure failures are not agent task scores" if run.summary["infrastructure_failures"] else "All selected attempts scored")
            return True
        except Exception:
            db.rollback()
            db.expire_all()
            run = db.get(EvaluationRun, run_id)
            if run.status not in TERMINAL:
                transition(db, run, "FAILED", "Internal infrastructure error; inspect worker diagnostics")
            raise


@router.post("/runs/{run_id}/execute")
def execute_demo(run_id: str, request: Request, user=Depends(current_user), db=Depends(get_db)):
    run, org = run_access(db, user, run_id, "developer")
    if run.config.get("agent_framework", "native") != "native" or run.config["benchmark"] != "native":
        raise HTTPException(409, "Connected agents require the background worker")
    if run.config["backend"] != "trusted-demo":
        raise HTTPException(409, "Docker jobs require the operator worker")
    if run.status != "QUEUED":
        raise HTTPException(409, "Run is not queued")
    if not perform(request.app.state.db, run_id):
        raise HTTPException(409, "Worker capacity unavailable or job cancelled")
    db.expire_all()
    run = db.get(EvaluationRun, run_id)
    audit(db, user, org, "run.execute_demo", run_id)
    db.commit()
    return serialize(run, db, True)


@router.post("/runs/{run_id}/replay/{attempt_id}")
def replay(run_id: str, attempt_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id, "developer")
    attempt = db.get(ScenarioAttempt, attempt_id)
    if not attempt or attempt.run_id != run_id:
        raise HTTPException(404, "Attempt not found")
    if run.config["benchmark"] != "native":
        raise HTTPException(409, "Official upstream replay is not supported by the native broker")
    if attempt.result.get("kind") == "infrastructure":
        raise HTTPException(409, "No agent execution to replay")
    return deterministic_replay(attempt.result)


@router.post("/runs/{run_id}/attempts/{attempt_id}/reviews", status_code=201)
def review(run_id: str, attempt_id: str, body: dict, user=Depends(current_user), db=Depends(get_db)):
    _, org = run_access(db, user, run_id, "admin")
    attempt = db.get(ScenarioAttempt, attempt_id)
    if not attempt or attempt.run_id != run_id:
        raise HTTPException(404, "Attempt not found")
    if body.get("outcome") not in {"PASSED", "FAILED", "INCONCLUSIVE"} or not isinstance(body.get("justification"), str) or not 10 <= len(body["justification"].strip()) <= 2000:
        raise HTTPException(422, "Outcome and a 10–2000 character justification required")
    item = HumanReview(attempt_id=attempt_id, user_id=user.id, outcome=body["outcome"], justification=redact(body["justification"].strip()))
    db.add(item)
    audit(db, user, org, "review.record", attempt_id)
    db.commit()
    return {"id": item.id, "outcome": item.outcome, "justification": item.justification, "at": item.at}


@router.get("/runs/{run_id}/reviews")
def reviews(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run_access(db, user, run_id)
    attempts = select(ScenarioAttempt.id).where(ScenarioAttempt.run_id == run_id)
    return [{"id": r.id, "attempt_id": r.attempt_id, "outcome": r.outcome, "justification": r.justification, "at": r.at} for r in db.scalars(select(HumanReview).where(HumanReview.attempt_id.in_(attempts)).order_by(HumanReview.at))]


@router.get("/runs/{run_id}/events")
def progress_events(run_id: str, user=Depends(current_user), db=Depends(get_db)):
    run, _ = run_access(db, user, run_id)
    from fastapi.responses import StreamingResponse
    # Finite SSE snapshot can be reconnected; avoids holding database sessions indefinitely.
    transitions = [{"previous": t.previous, "current": t.current, "at": t.at} for t in db.scalars(select(RunTransition).where(RunTransition.run_id == run_id).order_by(RunTransition.at))]
    progress = serialize(run, db)["progress"]
    async def stream():
        for index, entry in enumerate(transitions):
            yield f"id: {index}\nevent: transition\ndata: {json.dumps(entry)}\n\n"
        yield f"event: progress\ndata: {json.dumps(progress)}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/runs/{run_id}/attempts/{attempt_id}/trace")
def trace_graph(run_id: str, attempt_id: str, user=Depends(current_user), db=Depends(get_db)):
    run_access(db, user, run_id)
    attempt = db.get(ScenarioAttempt, attempt_id)
    if not attempt or attempt.run_id != run_id:
        raise HTTPException(404, "Attempt not found")
    from preflight_eval.diagnostics import trace_analysis
    return trace_analysis(attempt.result.get("events", []))


@router.get("/trace-comparisons")
def compare_traces(baseline_run: str, baseline_attempt: str, candidate_run: str, candidate_attempt: str, user=Depends(current_user), db=Depends(get_db)):
    left_run, _ = run_access(db, user, baseline_run)
    right_run, _ = run_access(db, user, candidate_run)
    if left_run.project_id != right_run.project_id:
        raise HTTPException(422, "Trace comparison requires one project")
    left = db.get(ScenarioAttempt, baseline_attempt)
    right = db.get(ScenarioAttempt, candidate_attempt)
    if not left or not right or left.run_id != baseline_run or right.run_id != candidate_run:
        raise HTTPException(404, "Attempt not found")
    from preflight_eval.diagnostics import trace_diff
    return trace_diff(left.result.get("events",[]),right.result.get("events",[]))


@router.get('/runs/{run_id}/attempts/{attempt_id}/trace.json')
def export_trace(run_id: str, attempt_id: str, user=Depends(current_user), db=Depends(get_db)):
    from fastapi.responses import Response
    from preflight_security import redact
    run_access(db,user,run_id)
    attempt=db.get(ScenarioAttempt,attempt_id)
    if not attempt or attempt.run_id!=run_id:
        raise HTTPException(404,'Attempt not found')
    result=attempt.result
    payload={'run_id':run_id,'attempt_id':attempt_id,'scenario_id':attempt.scenario_id,'trial':attempt.trial,'telemetry':result.get('telemetry'),'events':result.get('events',[]),'diagnostics':result.get('diagnostics'),'state':result.get('state'),'replay_semantics':'Recorded tool interactions only; fresh model execution is not deterministic replay'}
    return Response(json.dumps(redact(payload)),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="preflight-trace-{attempt_id}.json"'})
