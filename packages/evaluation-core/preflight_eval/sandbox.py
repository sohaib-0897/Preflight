"""Restricted native runner. Arbitrary code and public hostile workloads are refused."""

import json
import os
import re
import shutil
import subprocess
import uuid
import time
from typing import Protocol


class InfrastructureFailure(Exception):
    pass


class ExecutionBackend(Protocol):
    def execute(self, scenario_id: str, mode: str, seed: int, timeout: float) -> dict: ...


def docker_command(name, image):
    if not re.fullmatch(r"preflight-sandbox:0\.1\.0|[a-zA-Z0-9./_-]+@sha256:[a-f0-9]{64}", image):
        raise InfrastructureFailure("Operator must pin the native runner image")
    return [
        "docker",
        "run",
        "--name",
        name,
        "--label",
        "preflight.sandbox=true",
        "--pull=never",
        "--rm",
        "--network=none",
        "--read-only",
        "--user",
        "10001:10001",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges:true",
        "--cpus=0.5",
        "--memory=128m",
        "--memory-swap=128m",
        "--pids-limit=32",
        "--ulimit",
        "nofile=128:128",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=16m,uid=10001,gid=10001",
        "-i",
        image,
    ]


class DockerBackend:
    def __init__(self, image=None):
        self.image = image or os.environ.get("PREFLIGHT_SANDBOX_IMAGE", "preflight-sandbox:0.1.0")

    def execute(self, scenario_id, mode, seed, timeout=20, cancelled=None):
        if not shutil.which("docker"):
            raise InfrastructureFailure("Docker unavailable; no sandbox was provisioned")
        name = "preflight-" + uuid.uuid4().hex
        process = None
        try:
            process = subprocess.Popen(
                docker_command(name, self.image),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            deadline = time.monotonic() + timeout
            payload = json.dumps({"scenario_id": scenario_id, "mode": mode, "seed": seed}).encode()
            while True:
                if cancelled and cancelled():
                    process.kill()
                    process.communicate()
                    raise InfrastructureFailure("Sandbox cancelled by orchestrator")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(process.args, timeout)
                try:
                    output, error = process.communicate(payload, timeout=min(0.2, remaining))
                    break
                except subprocess.TimeoutExpired:
                    payload = None

            if process.returncode:
                raise InfrastructureFailure("Native container exited unsuccessfully")
            if len(output) > 1024 * 1024:
                raise InfrastructureFailure("Container output budget exceeded")
            result = json.loads(output)
            if not isinstance(result, dict) or "assessment" not in result:
                raise InfrastructureFailure("Invalid runner output")
            return result
        except subprocess.TimeoutExpired:
            if process:
                process.kill()
                process.communicate()
            raise InfrastructureFailure("Sandbox execution deadline exceeded")
        except (OSError, ValueError) as exc:
            raise InfrastructureFailure("Sandbox infrastructure error") from exc
        finally:
            subprocess.run(
                ["docker", "rm", "-f", name], capture_output=True, timeout=10, check=False
            )

    def cleanup_abandoned(self):
        # Operator invokes only after stopping workers; avoids deleting active runs.
        result = subprocess.run(
            ["docker", "ps", "-aq", "--filter", "label=preflight.sandbox=true"],
            capture_output=True,
            timeout=10,
            check=True,
        )
        ids = result.stdout.decode().split()
        for container in ids:
            if re.fullmatch(r"[0-9a-f]{12,64}", container):
                subprocess.run(
                    ["docker", "rm", "-f", container], capture_output=True, timeout=10, check=True
                )
        return len(ids)


class StrongIsolationRequired:
    def execute(self, *args, **kwargs):
        raise InfrastructureFailure(
            "Arbitrary untrusted code requires a separately implemented stronger isolation backend"
        )
