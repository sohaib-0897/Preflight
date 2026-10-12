import json
import threading
import pytest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from conftest import setup_project, register
from asgi_client import ASGIClient
from preflight.jobs import perform
from preflight_security import assess, CANARY


def test_scan_permissions_coverage_and_critical_gate(client, app):
    project = setup_project(client)
    path = f"/api/v1/projects/{project['id']}/security-scans"
    for mode in ["accurate", "unsafe"]:
        agent = client.post(
            f"/api/v1/projects/{project['id']}/agents",
            json={"name": mode, "version": "1", "config": {"mode": mode}},
        ).json()
        body = {"version_id": agent["versions"][0]["id"], "mode": "adversarial"}
        assert client.post(path, json=body).status_code == 422
        response = client.post(path, json={**body, "authorized_target": True})
        assert response.status_code == 201, response.text
        run = response.json()
        assert perform(app.state.db, run["id"])
        report = client.get(f"/api/v1/runs/{run['id']}/security").json()
        assert report["status"] == ("FAIL" if mode == "unsafe" else "INCONCLUSIVE")
        assert any(c["status"] == "NOT_RUN" for c in report["checks"])
        if mode == "unsafe":
            assert any(f["severity"] == "critical" for f in report["findings"])
            assert CANARY not in json.dumps(report)
            assert (
                client.post(f"/api/v1/runs/{run['id']}/release", json={}).json()["decision"]
                == "FAIL"
            )
        with ASGIClient(app) as outsider:
            register(outsider, mode + "-scan-outsider@example.test")
            assert outsider.get(f"/api/v1/runs/{run['id']}/security").status_code == 404
            assert outsider.post(path, json={**body, "authorized_target": True}).status_code == 404


@pytest.fixture
def injection_gateway():
    received = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            inputs = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["inputs"]
            received.append(inputs)
            injected = inputs["scenario_id"] == "prompt-injection"
            if injected:
                assert CANARY in inputs["retrieved_documents"][0]["text"]
            response = {
                "output": {"text": CANARY if injected else "Denied action requested"},
                "actions": [{"tool": "modify_restricted", "arguments": {}}],
            }
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, received
    finally:
        server.shutdown()
        thread.join(5)
        server.server_close()


def test_connected_scan_receives_actual_untrusted_content(
    client, app, monkeypatch, injection_gateway
):
    server, received = injection_gateway
    origin = f"127.0.0.1:{server.server_port}"
    monkeypatch.setenv("PREFLIGHT_AGENT_PRIVATE_ORIGINS", origin)
    project = setup_project(client)
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={
            "name": "Authorized gateway",
            "framework": "http",
            "version": "1",
            "config": {"endpoint": f"http://{origin}/invoke"},
        },
    ).json()
    path = f"/api/v1/projects/{project['id']}/security-scans"
    body = {"version_id": agent["versions"][0]["id"], "mode": "adversarial"}
    assert client.post(path, json=body).status_code == 422
    run = client.post(path, json={**body, "authorized_target": True}).json()
    assert perform(app.state.db, run["id"])
    result = client.get(f"/api/v1/runs/{run['id']}").json()
    assert len(received) == 2 and CANARY not in json.dumps(result)
    assert result["status"] == "COMPLETED"
    attempt = result["attempts"][0]["result"]
    assert attempt["state"]["restricted_value"] == "original"
    assert attempt["events"][0]["input"]["retrieved_documents"][0]["trust"] == "untrusted"
    assert any(f["category"] == "secret_exposure" for f in attempt["security_findings"])


def test_unknown_injection_and_excessive_retries_are_not_passes():
    findings, checks = assess({}, [], "prompt-injection")
    assert (
        not findings
        and next(c for c in checks if c["category"] == "prompt_injection")["status"]
        == "INCONCLUSIVE"
    )
    findings, checks = assess(
        {},
        [{"kind": "tool_call", "tool": str(i), "status": "timeout"} for i in range(3)],
        "tool-timeout",
    )
    assert any(f["category"] == "tool_loop" for f in findings)
    assert next(c for c in checks if c["category"] == "bounded_retries")["status"] == "FAILED"


def test_dependency_consent_preservation_and_artifact_authorization(client, app, monkeypatch):
    import preflight_security.dependencies as dependencies

    project = setup_project(client)
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={"name": "Fixture", "version": "1", "config": {"mode": "accurate"}},
    ).json()
    run = client.post(
        f"/api/v1/projects/{project['id']}/security-scans",
        json={"version_id": agent["versions"][0]["id"]},
    ).json()
    path = f"/api/v1/runs/{run['id']}/dependency-scan"
    body = {"packages": [{"name": "example", "version": "1", "ecosystem": "PyPI"}]}
    assert client.post(path, json=body).status_code == 422
    monkeypatch.setattr(
        dependencies,
        "query_dependencies",
        lambda packages: {
            "status": "INCONCLUSIVE",
            "complete": False,
            "packages": packages,
            "findings": [],
            "reason": "Offline fixture",
        },
    )
    response = client.post(path, json={**body, "share_package_metadata": True})
    assert response.status_code == 201, response.text
    record = response.json()
    assert record["status"] == "INCONCLUSIVE"
    artifact = f"/api/v1/artifacts/{record['artifact_id']}"
    assert client.get(artifact).json()["reason"] == "Offline fixture"
    with ASGIClient(app) as outsider:
        register(outsider, "dependencies-outsider@example.test")
        assert outsider.post(path, json={**body, "share_package_metadata": True}).status_code == 404
        assert outsider.get(artifact).status_code == 404


def test_critical_evidence_blocks_even_when_accuracy_unknown():
    from preflight_scoring import aggregate, release_decision, DEFAULT_POLICY

    summary = aggregate(
        [
            {
                "kind": "agent",
                "scenario_id": "unknown",
                "latency_ms": 1,
                "assessment": {"task_success": None},
                "security_findings": [{"severity": "critical", "confidence": "confirmed"}],
            }
        ]
    )
    assert summary["task_success_rate"] is None and summary["critical_security_findings"] == 1
    assert release_decision(summary, {"benchmark": "native"}, DEFAULT_POLICY)["decision"] == "FAIL"
