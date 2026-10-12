from preflight_eval import execute
from preflight_scoring import aggregate, compare_runs, release_decision, DEFAULT_POLICY
from preflight_scoring.metrics import cluster_latency_interval


def test_reported_usage_is_complete_valid_and_explicit():
    first = execute("refund")
    second = execute("tool-timeout")
    first["usage"] = {
        "total_tokens": 12,
        "estimated_cost_usd": 0.02,
        "currency": "USD",
        "cost_source": "fixture-reported; synthetic price",
    }
    summary = aggregate([first, second])
    assert summary["token_usage"] is None and summary["token_reported_attempts"] == 1
    assert summary["estimated_cost"] is None and summary["cost_reported_attempts"] == 1
    second["usage"] = {
        "input_tokens": 4,
        "output_tokens": 6,
        "estimated_cost_usd": 0.04,
        "currency": "USD",
        "cost_source": "fixture-reported; synthetic price",
    }
    summary = aggregate([first, second])
    assert summary["token_usage"] == 22 and summary["estimated_cost"] == 0.03
    assert summary["estimated_total_cost"] == 0.06
    second["usage"]["input_tokens"] = -1
    assert aggregate([first, second])["token_usage"] is None
    second["usage"]["estimated_cost_usd"] = float("nan")
    assert aggregate([first, second])["estimated_cost"] is None


def test_security_policy_unknown_failed_and_review_approvals():
    results = [execute("prompt-injection"), execute("unauthorized")]
    summary = aggregate(results)
    config = {"benchmark": "native", "scenarios": ["prompt-injection", "unauthorized"]}
    policy = {**DEFAULT_POLICY, "min_samples": 2, "required_security_checks": ["prompt_injection"]}
    assert release_decision(summary, config, policy)["decision"] == "PASS"
    assert (
        release_decision(
            summary, config, {**policy, "required_security_checks": ["dependency_vulnerabilities"]}
        )["decision"]
        == "INCONCLUSIVE"
    )
    assert (
        release_decision(summary, config, {**policy, "required_review_approvals": 1}, reviews=1)[
            "decision"
        ]
        == "INCONCLUSIVE"
    )
    assert (
        release_decision(
            summary, config, {**policy, "required_review_approvals": 1}, reviews=1, approvals=1
        )["decision"]
        == "PASS"
    )
    bad = aggregate([execute("unauthorized", "unsafe")])
    assert (
        release_decision(
            bad, config, {**DEFAULT_POLICY, "min_success": 0, "min_samples": 1, "max_high": 0}
        )["decision"]
        == "FAIL"
    )


def test_dimension_counts_and_material_comparison_incompatibility():
    result = execute("factual")
    summary = aggregate([result])
    assert summary["dimensions"]["factual_correctness"]["value"] == 1
    assert summary["dimensions"]["structured_accuracy"]["value"] is None
    left = {"config": {"security_mode": None}}
    right = {"config": {"security_mode": "adversarial"}}
    assert not compare_runs(left, right)["compatible"]
    pairs = [
        {"scenario_id": "a", "latency_delta_ms": 5},
        {"scenario_id": "a", "latency_delta_ms": 7},
        {"scenario_id": "b", "latency_delta_ms": 10},
    ]
    interval = cluster_latency_interval(pairs)
    assert interval == cluster_latency_interval(pairs) and interval["independent_scenarios"] == 2
    assert cluster_latency_interval(pairs[:1])["status"] == "INCONCLUSIVE"


def test_versioned_policy_requires_latest_approval(client):
    from integration.test_jobs import create_run

    project, body, run = create_run(client)
    result = client.post(f"/api/v1/runs/{run['id']}/execute").json()
    policy = client.post(
        f"/api/v1/projects/{project['id']}/policies",
        json={"name": "Approval required", "config": {"required_review_approvals": 1}},
    ).json()
    path = f"/api/v1/runs/{run['id']}/release"
    assert client.post(path, json={"policy_id": policy["id"]}).json()["decision"] == "INCONCLUSIVE"
    review = f"/api/v1/runs/{run['id']}/attempts/{result['attempts'][0]['id']}/reviews"
    assert (
        client.post(
            review, json={"outcome": "PASSED", "justification": "Confirmed actual state evidence."}
        ).status_code
        == 201
    )
    assert client.post(path, json={"policy_id": policy["id"]}).json()["decision"] == "PASS"
    assert (
        client.post(
            review,
            json={
                "outcome": "FAILED",
                "justification": "Reassessment found insufficient approval evidence.",
            },
        ).status_code
        == 201
    )
    gate = client.post(path, json={"policy_id": policy["id"]}).json()
    assert gate["decision"] == "INCONCLUSIVE" and gate["approved_attempts"] == 0
    assert gate["automatic_summary_preserved"]["task_success_rate"] == 1
    newer = client.post(
        f"/api/v1/projects/{project['id']}/policies",
        json={"name": "Approval required", "config": {"required_review_approvals": 2}},
    ).json()
    assert newer["version"] == 2
    policies = client.get(f"/api/v1/projects/{project['id']}/policies").json()
    assert (
        next(p for p in policies if p["id"] == policy["id"])["config"]["required_review_approvals"]
        == 1
    )


def test_offline_ci_policy_rejects_invalid_thresholds():
    import pytest
    from preflight_scoring import validate_policy

    for invalid in [
        {"min_samples": -1},
        {"max_critical": True},
        {"min_success": float("nan")},
        {"required_security_checks": "prompt_injection"},
        {"unknown": 0},
    ]:
        with pytest.raises(ValueError):
            validate_policy({**DEFAULT_POLICY, **invalid})
    validate_policy(DEFAULT_POLICY)
