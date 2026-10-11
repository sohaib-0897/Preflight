import pytest
from preflight_eval.sandbox import docker_command, DockerBackend, StrongIsolationRequired, InfrastructureFailure
from preflight_security import Broker, CANARY, redact


def test_docker_policy():
    args = docker_command("preflight-test", "preflight-sandbox:0.1.0")
    for flag in ["--network=none", "--read-only", "--cap-drop=ALL", "--pids-limit=32", "--security-opt=no-new-privileges:true"]:
        assert flag in args
    assert "--privileged" not in args and "-v" not in args
    with pytest.raises(InfrastructureFailure):
        docker_command("test", "user-arbitrary:latest")
    with pytest.raises(InfrastructureFailure):
        StrongIsolationRequired().execute()


def test_broker_boundary_and_idempotency():
    b = Broker()
    args = {"order_id": "order-001", "cents": 7500, "transaction_id": "refund-1"}
    b.call("refund", args)
    b.call("refund", args)
    assert b.state()["refund_cents"] == 7500
    assert b.call("modify_restricted", {"value": "evil"})["error"] == "unauthorized_tool"
    assert b.state()["restricted_value"] == "original"
    assert b.call("refund", {**args, "cents": "7500"})["error"] == "invalid_tool_parameters"
    b.close()


def test_redaction():
    value = redact({"api_key": "real", "text": CANARY + " Bearer abc123"})
    assert "real" not in str(value) and CANARY not in str(value) and "abc123" not in str(value)
