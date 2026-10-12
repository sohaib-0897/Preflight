"""Live checks require Docker plus an already-built operator native runner image.
Missing daemon/image prerequisites fail explicitly when the Docker CLI exists.
Command construction tests do not substitute for isolation.
"""

import json
import os
import shutil
import subprocess
import uuid
import pytest
from preflight_eval import SCENARIO_IDS
from preflight_eval.sandbox import docker_command, DockerBackend, InfrastructureFailure

pytestmark = pytest.mark.skipif(
    not shutil.which("docker"), reason="Docker executable absent; live isolation not verified"
)


@pytest.fixture(scope="module", autouse=True)
def require_live_docker():
    for command in (
        ["docker", "info"],
        [
            "docker",
            "image",
            "inspect",
            os.environ.get("PREFLIGHT_SANDBOX_IMAGE", "preflight-sandbox:0.1.0"),
        ],
    ):
        result = subprocess.run(command, capture_output=True, timeout=20)
        assert result.returncode == 0, result.stderr.decode(errors="replace")


def run_python(source):
    name = "preflight-live-" + uuid.uuid4().hex
    image = os.environ.get("PREFLIGHT_SANDBOX_IMAGE", "preflight-sandbox:0.1.0")
    args = docker_command(name, image)
    args[-1:-1] = ["--entrypoint", "python"]
    args.extend(["-B", "-c", source])
    try:
        return subprocess.run(args, capture_output=True, timeout=20)
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)


@pytest.mark.parametrize("scenario", SCENARIO_IDS)
def test_live_native_fixture(scenario):
    result = DockerBackend().execute(scenario, "accurate", 42)
    assert result["assessment"]["task_success"]
    expected = (
        subprocess.run(
            [
                "docker",
                "image",
                "inspect",
                "--format",
                "{{.Id}}",
                result["sandbox"]["configured_image"],
            ],
            capture_output=True,
            timeout=10,
            check=True,
        )
        .stdout.decode()
        .strip()
    )
    assert result["sandbox"]["image_id"] == expected
    assert expected.startswith("sha256:")


def test_live_network_and_filesystem_boundaries():
    result = run_python("""import socket,os,json
out={'uid':os.getuid()}
try:
 open('/etc/preflight-probe','w').write('x')
 out['readonly']=False
except OSError: out['readonly']=True
out['network_denied']=True
for host in ['169.254.169.254','1.1.1.1']:
 s=socket.socket();s.settimeout(.2)
 try: s.connect((host,80));out['network_denied']=False
 except OSError: pass
 finally:s.close()
print(json.dumps(out))""")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data == {"uid": 10001, "readonly": True, "network_denied": True}


def test_live_cgroup_caps_and_process_limits():
    result = run_python("""import json,resource
from pathlib import Path
status=Path('/proc/self/status').read_text()
print(json.dumps({'memory':Path('/sys/fs/cgroup/memory.max').read_text().strip(),'pids':Path('/sys/fs/cgroup/pids.max').read_text().strip(),'caps':next(x for x in status.splitlines() if x.startswith('CapEff:')).split()[1],'nofile':resource.getrlimit(resource.RLIMIT_NOFILE)[0]}))""")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert int(data["memory"]) == 128 * 1024 * 1024 and int(data["pids"]) == 32
    assert int(data["caps"], 16) == 0 and data["nofile"] == 128


def test_live_memory_exhaustion_is_contained():
    result = run_python("value=bytearray(256*1024*1024);print(len(value))")
    assert result.returncode == 137, (result.returncode, result.stdout, result.stderr)


def test_live_disk_quota():
    result = run_python(
        "import sys,errno\nopen('/tmp/probe','wb').write(b'ok')\ntry:\n open('/tmp/large','wb').write(b'x'*(17*1024*1024))\nexcept OSError as exc:\n sys.exit(0 if exc.errno == errno.ENOSPC else 2)\nsys.exit(1)"
    )
    assert result.returncode == 0, result.stderr


def test_live_timeout_and_cleanup():
    before = sandbox_names()
    with pytest.raises(InfrastructureFailure, match="deadline exceeded"):
        DockerBackend().execute("latency", "slow", 42, timeout=0.001)
    assert sandbox_names() == before


def sandbox_names():
    result = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--format",
            "{{.Names}}",
            "--filter",
            "label=preflight.sandbox=true",
        ],
        capture_output=True,
        timeout=10,
        check=True,
    )
    return set(result.stdout.decode().splitlines())


def test_live_concurrent_execution_and_cleanup():
    from concurrent.futures import ThreadPoolExecutor

    before = sandbox_names()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda seed: DockerBackend().execute("refund", "accurate", seed), [42, 43])
        )
    assert all(result["assessment"]["task_success"] for result in results)
    assert sandbox_names() == before


def test_live_orchestrator_cancellation_cleans_container(monkeypatch):
    import time
    import preflight_eval.sandbox as sandbox

    original = sandbox.docker_command
    before = sandbox_names()

    def slow(name, image):
        args = original(name, image)
        args[-1:-1] = ["--entrypoint", "python"]
        return args + ["-B", "-c", "import time; time.sleep(30)"]

    monkeypatch.setattr(sandbox, "docker_command", slow)
    deadline = time.monotonic() + 1
    with pytest.raises(InfrastructureFailure, match="cancelled"):
        DockerBackend().execute(
            "refund", "accurate", 42, timeout=10, cancelled=lambda: time.monotonic() >= deadline
        )
    assert sandbox_names() == before
