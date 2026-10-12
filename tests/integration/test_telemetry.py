import json
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace import TracerProvider
from preflight.jobs import perform
from preflight_eval.diagnostics import diagnose
from asgi_client import ASGIClient
from conftest import setup_project, register


def test_actual_request_worker_parent_spans_and_redaction(client, app, monkeypatch):
    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    provider = TracerProvider()
    provider.add_span_processor(processor)
    monkeypatch.setattr("preflight.telemetry.tracer", provider.get_tracer("preflight-test"))
    project = setup_project(client)
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={"name": "Fixture", "version": "1", "config": {"mode": "accurate"}},
    ).json()
    path = f"/api/v1/projects/{project['id']}/runs"
    body = {
        "version_id": agent["versions"][0]["id"],
        "idempotency_key": "telemetry-idempotent",
        "scenarios": ["tool-timeout"],
    }
    response = client.post(path, json=body)
    trace_id = response.headers["x-trace-id"]
    run = response.json()
    assert client.post(path, json=body).json()["id"] == run["id"]
    assert perform(app.state.db, run["id"])
    detail = client.get(f"/api/v1/runs/{run['id']}").json()
    attempt = detail["attempts"][0]
    spans = exporter.get_finished_spans()
    evaluation = next(s for s in spans if s.name == "evaluation.run")
    record = next(s for s in spans if s.name == "evaluation.attempt.record")
    assert format(evaluation.context.trace_id, "032x") == trace_id
    assert record.parent.span_id == evaluation.context.span_id
    assert attempt["result"]["telemetry"]["span_id"] == format(record.context.span_id, "016x")
    assert all(e["trace_id"] == trace_id for e in attempt["result"]["events"])
    assert "password" not in json.dumps([dict(s.attributes) for s in spans]).lower()
    trace = f"/api/v1/runs/{run['id']}/attempts/{attempt['id']}/trace.json"
    assert client.get(trace).json()["diagnostics"]["findings"][0]["category"] == "tool_timeout"
    with ASGIClient(app) as outsider:
        register(outsider, "trace-outsider@example.test")
        assert outsider.get(trace).status_code == 404
    exporter.clear()
    processor.shutdown()


def test_metadata_metrics_require_operator_token(client, monkeypatch):
    assert client.get("/metrics").status_code == 401
    monkeypatch.setenv("PREFLIGHT_METRICS_TOKEN", "synthetic-monitoring-token")
    assert client.get("/metrics", headers={"authorization": "Bearer incorrect"}).status_code == 401
    response = client.get(
        "/metrics", headers={"authorization": "Bearer synthetic-monitoring-token"}
    )
    assert response.status_code == 200 and "preflight_runs_total" in response.text


def test_diagnostics_do_not_invent_infinite_loop_or_trust_reported_denials():
    result = {
        "events": [
            {
                "sequence": i,
                "kind": "tool_call",
                "tool": "lookup",
                "arguments": {},
                "source": "enforcing-broker",
            }
            for i in range(5)
        ]
    }
    findings = diagnose(result)["findings"]
    assert findings[0]["category"] == "suspected_loop" and findings[0]["verified"] is False
    result = {
        "events": [
            {
                "sequence": 0,
                "source": "agent-reported",
                "status": "denied",
                "result": {"error": "unauthorized_tool"},
            }
        ]
    }
    assert diagnose(result)["findings"] == []


def test_actual_json_exporter_metadata_allowlist(tmp_path):
    from preflight.telemetry import JsonSpanExporter

    destination = tmp_path / "traces.jsonl"
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(JsonSpanExporter(destination)))
    with provider.get_tracer("test").start_as_current_span("http.request") as span:
        span.set_attribute("preflight.request_id", "fixture-id")
        span.set_attribute("authorization", "synthetic-sensitive-value")
        span.set_attribute("user.email", "private-fixture@example.test")
    provider.shutdown()
    record = json.loads(destination.read_text())
    assert record["attributes"] == {"preflight.request_id": "fixture-id"}
    assert record["end_ns"] >= record["start_ns"] and record["trace_id"]


def test_broker_replay_ignores_agent_reported_tool_intentions():
    from preflight_eval.native import deterministic_replay

    result = {
        "events": [
            {
                "kind": "tool_call",
                "tool": "refund",
                "arguments": {
                    "order_id": "order-001",
                    "cents": 7500,
                    "transaction_id": "reported-only",
                },
                "source": "agent-reported",
            }
        ],
        "state": {"refund_cents": 0, "refund_count": 0, "restricted_value": "original"},
    }
    assert deterministic_replay(result)["matches"] is True
