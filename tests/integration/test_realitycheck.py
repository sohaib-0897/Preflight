from conftest import setup_project, register
from asgi_client import ASGIClient
from preflight.jobs import perform
from preflight_scoring.realitycheck import verify_claims, sql_assertions


def test_versioned_reference_claims_and_tenant_denial(client, app):
    project = setup_project(client)
    path = f"/api/v1/projects/{project['id']}/sources"
    source = client.post(
        path, json={"name": "Policy", "uri": "local://policy/v1", "facts": {"refund_days": 30}}
    ).json()
    newer = client.post(
        path, json={"name": "Policy", "uri": "local://policy/v2", "facts": {"refund_days": 14}}
    ).json()
    assert newer["version"] == 2 and source["fingerprint"] != newer["fingerprint"]
    checks = client.post(
        f"/api/v1/projects/{project['id']}/verify-claims",
        json={
            "source_ids": [source["id"]],
            "claims": [
                {"subject": "refund_days", "value": 30},
                {"subject": "refund_days", "value": 14},
                {"subject": "unknown", "value": 1},
            ],
        },
    ).json()
    assert [c["status"] for c in checks["claims"]] == [
        "SUPPORTED",
        "CONTRADICTED",
        "INSUFFICIENT_EVIDENCE",
    ]
    assert checks["claims"][0]["evidence"][0]["sha256"] == source["fingerprint"]
    assert (
        verify_claims([{"subject": "refund_days", "value": 30}], [source, newer])["status"]
        == "INCONCLUSIVE"
    )
    with ASGIClient(app) as outsider:
        register(outsider, "corpus-outsider@example.test")
        assert outsider.get(path).status_code == 404
        workspace = outsider.get("/api/v1/workspaces").json()[0]
        other = outsider.post(
            f"/api/v1/workspaces/{workspace['id']}/projects", json={"name": "Other"}
        ).json()
        assert (
            outsider.post(
                f"/api/v1/projects/{other['id']}/verify-claims",
                json={"source_ids": [source["id"]], "claims": []},
            ).status_code
            == 404
        )


def test_custom_scenario_real_rows_sql_and_false_completion(client, app):
    project = setup_project(client)
    custom = {
        "id": "custom_refund",
        "name": "Verified refund",
        "base_scenario": "false-completion",
        "request": "Refund $75, then confirm database mutation.",
        "expected_state": {"refund_count": 1, "restricted_value": "original"},
        "expected_tools": ["refund"],
        "sql_assertions": [{"query": "SELECT sum(cents) FROM refunds", "expected": 7500}],
    }
    dataset = client.post(
        f"/api/v1/projects/{project['id']}/datasets",
        json={"name": "Custom refunds", "custom_scenarios": [custom]},
    ).json()
    for mode, success in [("accurate", 1), ("false-completion", 0)]:
        agent = client.post(
            f"/api/v1/projects/{project['id']}/agents",
            json={"name": mode, "version": "1", "config": {"mode": mode}},
        ).json()
        response = client.post(
            f"/api/v1/projects/{project['id']}/runs",
            json={
                "version_id": agent["versions"][0]["id"],
                "idempotency_key": "custom-" + mode,
                "dataset_id": dataset["id"],
            },
        )
        assert response.status_code == 201, response.text
        run = response.json()
        assert perform(app.state.db, run["id"])
        result = client.get(f"/api/v1/runs/{run['id']}").json()
        assert result["summary"]["task_success_rate"] == success
        attempt = result["attempts"][0]
        assert attempt["scenario_id"] == "custom_refund"
        checks = attempt["result"]["assessment"]["configured_assertions"]["checks"]
        assert any(c["dimension"] == "sql_state" for c in checks)
        assert (
            attempt["result"]["environment_snapshot"]["refunds"] == []
            if not success
            else len(attempt["result"]["environment_snapshot"]["refunds"]) == 1
        )


def test_readonly_sql_refuses_host_and_unsafe_writes():
    snapshot = {"refunds": [], "resources": [{"id": "restricted", "value": "original"}]}
    checks = sql_assertions(
        snapshot,
        [
            {"query": "ATTACH DATABASE '/etc/passwd' AS outside", "expected": 0},
            {"query": "DELETE FROM resources", "expected": 0},
            {"query": "SELECT value FROM resources", "expected": "original"},
        ],
    )
    assert [c["status"] for c in checks] == ["INCONCLUSIVE", "INCONCLUSIVE", "PASSED"]


def test_assigned_reviews_preserve_automated_evidence(client, app):
    project = setup_project(client)
    owner = client.get("/api/v1/auth/me").json()
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={"name": "Review", "version": "1", "config": {"mode": "accurate"}},
    ).json()
    run = client.post(
        f"/api/v1/projects/{project['id']}/runs",
        json={
            "version_id": agent["versions"][0]["id"],
            "idempotency_key": "review-queue-001",
            "scenarios": ["refund"],
        },
    ).json()
    assert perform(app.state.db, run["id"])
    attempt = client.get(f"/api/v1/runs/{run['id']}").json()["attempts"][0]
    path = f"/api/v1/runs/{run['id']}/attempts/{attempt['id']}"
    assignment = client.post(
        path + "/assign-review", json={"reviewer_email": owner["email"]}
    ).json()
    assert len(client.get(f"/api/v1/projects/{project['id']}/review-queue").json()) == 1
    decision = f"/api/v1/review-assignments/{assignment['id']}/decision"
    assert (
        client.post(
            decision,
            json={
                "outcome": "FAILED",
                "justification": "Manual override with documented supporting evidence.",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            decision,
            json={
                "outcome": "PASSED",
                "justification": "Another decision should not overwrite the first.",
            },
        ).status_code
        == 409
    )
    assert (
        client.get(f"/api/v1/runs/{run['id']}").json()["attempts"][0]["result"] == attempt["result"]
    )
    assert (
        client.post(
            path + "/realitycheck", json={"rules": {"expected_state": {"refund_count": 0}}}
        ).json()["assessment"]["configured_assertions"]["status"]
        == "FAILED"
    )
    assert len(client.get(path + "/assessments").json()) == 2
    assert client.get(f"/api/v1/runs/{run['id']}").json()["summary"]["task_success_rate"] == 1


def test_assigned_developer_can_review(client, app):
    project = setup_project(client)
    organization = client.get("/api/v1/workspaces").json()[0]["org_id"]
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={"name": "Reviewer fixture", "version": "1", "config": {"mode": "accurate"}},
    ).json()
    run = client.post(
        f"/api/v1/projects/{project['id']}/runs",
        json={
            "version_id": agent["versions"][0]["id"],
            "idempotency_key": "assigned-developer-001",
            "scenarios": ["refund"],
        },
    ).json()
    assert perform(app.state.db, run["id"])
    attempt = client.get(f"/api/v1/runs/{run['id']}").json()["attempts"][0]
    with ASGIClient(app) as reviewer:
        register(reviewer, "assigned-developer@example.test")
        assert (
            client.post(
                f"/api/v1/organizations/{organization}/members",
                json={"email": "assigned-developer@example.test", "role": "developer"},
            ).status_code
            == 201
        )
        assignment = client.post(
            f"/api/v1/runs/{run['id']}/attempts/{attempt['id']}/assign-review",
            json={"reviewer_email": "assigned-developer@example.test"},
        ).json()
        decision = reviewer.post(
            f"/api/v1/review-assignments/{assignment['id']}/decision",
            json={
                "outcome": "PASSED",
                "justification": "Verified captured transaction and invariant with assigned access.",
            },
        )
        assert decision.status_code == 201, decision.text


def test_unverifiable_assertion_is_unknown_accuracy_not_failure_score(client, app):
    project = setup_project(client)
    dataset = client.post(
        f"/api/v1/projects/{project['id']}/datasets",
        json={
            "name": "Unknown assertion",
            "custom_scenarios": [
                {
                    "id": "custom_unknown",
                    "name": "Missing evidence",
                    "base_scenario": "refund",
                    "request": "Verify refund state.",
                    "sql_assertions": [{"query": "SELECT * FROM unavailable", "expected": 1}],
                }
            ],
        },
    ).json()
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={"name": "Unknown accuracy", "version": "1", "config": {"mode": "accurate"}},
    ).json()
    run = client.post(
        f"/api/v1/projects/{project['id']}/runs",
        json={
            "version_id": agent["versions"][0]["id"],
            "idempotency_key": "unknown-accuracy-001",
            "dataset_id": dataset["id"],
        },
    ).json()
    assert perform(app.state.db, run["id"])
    result = client.get(f"/api/v1/runs/{run['id']}").json()
    assert result["summary"]["task_success_rate"] is None
    assert result["summary"]["unassessed_attempts"] == 1
    assert (
        client.post(f"/api/v1/runs/{run['id']}/release", json={}).json()["decision"]
        == "INCONCLUSIVE"
    )
