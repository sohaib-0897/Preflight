from integration.test_jobs import create_run


def test_dataset_selection_preserves_version(client):
    project, body, _ = create_run(client)
    dataset = client.post(f'/api/v1/projects/{project["id"]}/datasets', json={"name":"Refund smoke","scenario_ids":["refund","false-completion"]}).json()
    assert dataset["benchmark_version"] == "1.0.0"
    run = client.post(f'/api/v1/projects/{project["id"]}/runs', json={**body,"dataset_id":dataset["id"],"idempotency_key":"dataset-test-01"}).json()
    result = client.post(f'/api/v1/runs/{run["id"]}/execute').json()
    assert result["summary"]["sample_size"] == 2
    assert result["config"]["dataset_fingerprint"] == dataset["fingerprint"]
    assert client.post(f'/api/v1/runs/{run["id"]}/release',json={}).json()["decision"] == "INCONCLUSIVE"
