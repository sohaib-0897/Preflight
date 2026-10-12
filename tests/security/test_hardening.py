import time
from preflight.db import Session
from preflight.auth import digest
from conftest import register
from integration.test_jobs import create_run


def test_expired_session_rejected(client, app):
    register(client)
    with app.state.db.sessions() as db:
        session = db.get(Session, digest(client.cookies["preflight_session"]))
        session.expires = time.time() - 1
        db.commit()
    assert client.get("/api/v1/auth/me").status_code == 401


def test_login_rate_limit(client):
    for i in range(20):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.test", "password": "incorrect-passphrase"},
        )
        assert response.status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.test", "password": "incorrect-passphrase"},
        ).status_code
        == 429
    )


def test_reviewer_override_preserves_automatic_score(client):
    project, _, run = create_run(client, "regressed")
    data = client.post(f"/api/v1/runs/{run['id']}/execute").json()
    for attempt in data["attempts"]:
        if not attempt["result"]["assessment"]["task_success"]:
            assert (
                client.post(
                    f"/api/v1/runs/{run['id']}/attempts/{attempt['id']}/reviews",
                    json={
                        "outcome": "PASSED",
                        "justification": "Synthetic reviewer override to exercise audit and policy.",
                    },
                ).status_code
                == 201
            )
    policy = client.post(
        f"/api/v1/projects/{project['id']}/policies",
        json={"name": "Explicit review policy", "config": {"honor_human_overrides": True}},
    ).json()
    decision = client.post(
        f"/api/v1/runs/{run['id']}/release", json={"policy_id": policy["id"]}
    ).json()
    assert decision["decision"] == "PASS"
    assert decision["human_overrides_applied"] == 4
    assert decision["automatic_summary_preserved"]["task_success_rate"] == 0.5
    assert client.get(f"/api/v1/runs/{run['id']}").json()["summary"]["task_success_rate"] == 0.5
