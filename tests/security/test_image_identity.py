"""Image-selection contract tests; actual OCI identity is separately tested live."""

import json
import subprocess
from unittest.mock import Mock
import pytest
from preflight_eval.sandbox import DockerBackend, InfrastructureFailure


def test_mutable_tag_resolves_to_immutable_execution_id(monkeypatch):
    image_id = "sha256:" + "a" * 64
    commands = []

    def run(args, **kwargs):
        commands.append(args)
        return subprocess.CompletedProcess(args, 0, (image_id + "\n").encode(), b"")

    process = Mock(returncode=0)
    process.communicate.return_value = (
        json.dumps({"assessment": {"task_success": True}}).encode(),
        b"",
    )
    popen = Mock(return_value=process)
    monkeypatch.setattr("preflight_eval.sandbox.subprocess.run", run)
    monkeypatch.setattr("preflight_eval.sandbox.subprocess.Popen", popen)
    monkeypatch.setattr("preflight_eval.sandbox.shutil.which", lambda _: "/operator/docker")
    result = DockerBackend().execute("refund", "accurate", 42)
    assert popen.call_args.args[0][-1] == image_id
    assert result["sandbox"]["image_id"] == image_id
    assert commands[0][-1] == "preflight-sandbox:0.1.0"
    assert commands[-1][1:3] == ["rm", "-f"]


def test_invalid_inspected_image_cannot_start_a_container(monkeypatch):
    monkeypatch.setattr("preflight_eval.sandbox.shutil.which", lambda _: "/operator/docker")
    monkeypatch.setattr(
        "preflight_eval.sandbox.subprocess.run",
        lambda args, **kw: subprocess.CompletedProcess(args, 0, b"arbitrary:latest\n", b""),
    )
    popen = Mock()
    monkeypatch.setattr("preflight_eval.sandbox.subprocess.Popen", popen)
    with pytest.raises(InfrastructureFailure, match="image identity"):
        DockerBackend().execute("refund", "accurate", 42)
    popen.assert_not_called()
