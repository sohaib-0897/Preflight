from fastapi import HTTPException
from conftest import setup_project, register
from asgi_client import ASGIClient
from preflight.jobs import perform, claim, transition
from preflight.db import EvaluationRun, ScenarioAttempt
from sqlalchemy import select


def create_run(client, mode="accurate", backend="trusted-demo", trials=1):
    p = setup_project(client)
    a = client.post(f'/api/v1/projects/{p["id"]}/agents', json={"name": "Demo", "version": "1.0", "config": {"mode": mode}}).json()
    body = {"version_id": a["versions"][0]["id"], "idempotency_key": "idempotency-001", "backend": backend, "trials": trials}
    r = client.post(f'/api/v1/projects/{p["id"]}/runs', json=body)
    assert r.status_code == 201, r.text
    return p, body, r.json()


def test_full_native_run_and_idempotency(client):
    p, body, run = create_run(client, trials=2)
    duplicate = client.post(f'/api/v1/projects/{p["id"]}/runs', json=body).json()
    assert duplicate["id"] == run["id"]
    changed = {**body, "trials": 3}
    assert client.post(f'/api/v1/projects/{p["id"]}/runs', json=changed).status_code == 409
    completed = client.post(f'/api/v1/runs/{run["id"]}/execute')
    assert completed.status_code == 200, completed.text
    data = completed.json()
    assert data["status"] == "COMPLETED"
    assert data["summary"]["sample_size"] == 16
    assert data["summary"]["task_success_rate"] == 1
    assert [t["current"] for t in data["transitions"]] == ["QUEUED", "PREPARING", "RUNNING", "SCORING", "COMPLETED"]
    assert client.post(f'/api/v1/runs/{run["id"]}/execute').status_code == 409
    attempt = data["attempts"][0]
    assert client.post(f'/api/v1/runs/{run["id"]}/replay/{attempt["id"]}').json()["matches"]


def test_cancel_before_claim(client, app):
    _, _, run = create_run(client)
    assert client.post(f'/api/v1/runs/{run["id"]}/cancel').status_code == 200
    assert not perform(app.state.db, run["id"])
    assert client.get(f'/api/v1/runs/{run["id"]}').json()["status"] == "CANCELLED"


def test_infrastructure_is_not_agent_failure(client, app, monkeypatch):
    monkeypatch.setattr("preflight_eval.sandbox.shutil.which", lambda _: None)
    _, _, run = create_run(client, backend="docker")
    assert perform(app.state.db, run["id"])
    result = client.get(f'/api/v1/runs/{run["id"]}').json()
    assert result["status"] == "BLOCKED"
    assert result["summary"]["sample_size"] == 0
    assert result["summary"]["task_success_rate"] is None
    assert result["summary"]["infrastructure_failures"] == 8


def test_run_artifact_tenant_boundary(client, app):
    _, _, run = create_run(client)
    with ASGIClient(app) as outsider:
        register(outsider, "outsider@example.test")
        assert outsider.get(f'/api/v1/runs/{run["id"]}').status_code == 404
        assert outsider.post(f'/api/v1/runs/{run["id"]}/execute').status_code == 404


def test_review_audit(client):
    _, _, run = create_run(client)
    result = client.post(f'/api/v1/runs/{run["id"]}/execute').json()
    attempt = result["attempts"][0]["id"]
    assert client.post(f'/api/v1/runs/{run["id"]}/attempts/{attempt}/reviews', json={"outcome": "PASSED", "justification": "Verified transaction in trace and final state."}).status_code == 201
    assert len(client.get(f'/api/v1/runs/{run["id"]}/reviews').json()) == 1
