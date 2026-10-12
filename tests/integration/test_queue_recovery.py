import asyncio
import threading
import time
from sqlalchemy import select
from preflight.db import ScenarioAttempt
from preflight.jobs import claim, perform
from preflight.arq_worker import pending
from test_jobs import create_run


def test_expired_native_resume_preserves_existing_attempts(client, app):
    _, _, run = create_run(client)
    with app.state.db.sessions() as db:
        claimed = claim(db, run["id"])
        claimed.lease_until = time.time() - 1
        db.commit()
    pending(app.state.db)
    assert client.get(f"/api/v1/runs/{run['id']}").json()["status"] == "QUEUED"
    assert perform(app.state.db, run["id"])
    with app.state.db.sessions() as db:
        attempts = list(
            db.scalars(select(ScenarioAttempt).where(ScenarioAttempt.run_id == run["id"]))
        )
    assert len(attempts) == 8
    assert not perform(app.state.db, run["id"])


def test_actual_concurrent_duplicate_claim_and_worker_stop(client, app, monkeypatch):
    _, _, run = create_run(client)
    from preflight.jobs import execute

    entered, release, stop = threading.Event(), threading.Event(), threading.Event()

    def slow(*args):
        entered.set()
        assert release.wait(5)
        return execute(*args)

    monkeypatch.setattr("preflight.jobs.execute", slow)
    errors = []

    def worker():
        try:
            perform(app.state.db, run["id"], stop)
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=worker)
    thread.start()
    assert entered.wait(5)
    assert not perform(app.state.db, run["id"])
    stop.set()
    release.set()
    thread.join(5)
    assert not thread.is_alive() and not errors
    result = client.get(f"/api/v1/runs/{run['id']}").json()
    assert result["status"] == "QUEUED"
    assert len(result["attempts"]) <= 1


def test_async_database_readiness_uses_real_driver(app):
    app.state.db.initialize()
    assert asyncio.run(app.state.db.readiness()) == 1


def test_queue_capabilities_and_readiness_without_daemon(client, app, monkeypatch):
    from preflight.arq_worker import queue_name, worker_backend, evaluate
    from integration.test_jobs import create_run
    import asyncio

    _, _, run = create_run(client, backend="docker")
    monkeypatch.setenv("PREFLIGHT_QUEUE_PREFIX", "fixture-isolated-queue")
    assert queue_name("docker") == "fixture-isolated-queue:docker"
    assert queue_name() == "fixture-isolated-queue"
    monkeypatch.setenv("PREFLIGHT_WORKER_BACKEND", "trusted-demo")
    assert worker_backend() == "trusted-demo"
    import pytest

    with pytest.raises(ValueError, match="mismatch"):
        asyncio.run(evaluate({"database": app.state.db, "stops": set()}, run["id"]))
    assert client.get(f"/api/v1/runs/{run['id']}").json()["status"] == "QUEUED"
    monkeypatch.delenv("REDIS_URL", raising=False)
    readiness = client.get("/api/v1/execution-readiness").json()
    assert readiness["docker"]["status"] == "BLOCKED"
    assert readiness["background_queue"]["status"] == "NOT_RUN"
