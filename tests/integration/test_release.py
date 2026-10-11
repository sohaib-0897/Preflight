import pytest
from integration.test_jobs import create_run
from preflight_scoring import release_decision, DEFAULT_POLICY, compare_runs, wilson


def test_release_report_comparison(client):
    project, body, run = create_run(client)
    result = client.post(f'/api/v1/runs/{run["id"]}/execute').json()
    gate = client.post(f'/api/v1/runs/{run["id"]}/release', json={}).json()
    assert gate["decision"] == "PASS"
    assert client.get(f'/api/v1/runs/{run["id"]}/report.json').json()["reproduction"]["seed"] == 42
    assert "Scored attempts" in client.get(f'/api/v1/runs/{run["id"]}/report.html').text
    agents = client.get(f'/api/v1/projects/{project["id"]}/agents').json()
    version = client.post(f'/api/v1/agents/{agents[0]["id"]}/versions', json={"version": "2.0", "config": {"mode": "regressed"}}).json()
    candidate = client.post(f'/api/v1/projects/{project["id"]}/runs', json={**body, "version_id": version["id"], "idempotency_key": "candidate-002"}).json()
    client.post(f'/api/v1/runs/{candidate["id"]}/execute')
    compare = client.get(f'/api/v1/comparisons?baseline={run["id"]}&candidate={candidate["id"]}').json()
    assert compare["compatible"] and compare["regressions"] == 4
    assert compare["success_delta"] == -.5
    assert client.post(f'/api/v1/runs/{candidate["id"]}/release', json={}).json()["decision"] == "FAIL"
    policy = client.post(f'/api/v1/projects/{project["id"]}/policies', json={"name": "Production", "config": {"required_reviews": 1}}).json()
    assert client.post(f'/api/v1/runs/{run["id"]}/release', json={"policy_id": policy["id"]}).json()["decision"] == "INCONCLUSIVE"


def test_missing_coverage_never_passes():
    summary = {"sample_size": 8, "task_success_rate": 1, "latency_p95_ms": 1, "critical_security_findings": 0}
    config = {"benchmark": "native", "scenarios": []}
    assert release_decision(summary, config, DEFAULT_POLICY)["decision"] == "PASS"
    assert release_decision(summary, config, {**DEFAULT_POLICY, "min_samples": 9})["decision"] == "INCONCLUSIVE"
    assert release_decision(summary, config, {**DEFAULT_POLICY, "max_cost": .01})["decision"] == "INCONCLUSIVE"
    assert release_decision(summary, config, {**DEFAULT_POLICY, "required_benchmarks": ["native", "agentdojo"]})["decision"] == "INCONCLUSIVE"
    assert release_decision(summary, config, DEFAULT_POLICY, run_status="QUEUED")["decision"] == "INCONCLUSIVE"


def test_wilson_and_incompatibility():
    low, high = wilson(8,8)
    assert .6 < low < 1 and high == 1
    assert not compare_runs({"config": {"benchmark_version": "1"}}, {"config": {"benchmark_version": "2"}})["compatible"]
