"""Verify a fresh, isolated Compose project; never reuse or delete operator volumes."""

import http.cookiejar
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = dict(os.environ, POSTGRES_PASSWORD=secrets.token_hex(24))
    compose = [
        "docker",
        "compose",
        "-p",
        "preflight-verify-" + uuid.uuid4().hex[:12],
        "-f",
        "infra/compose/compose.yaml",
    ]

    def command(*args):
        return subprocess.run(compose + list(args), cwd=ROOT, env=env, check=True, timeout=600)

    client = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )
    csrf = None

    def request(path, body=None):
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/v1" + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers=headers,
        )
        with client.open(req, timeout=10) as response:
            return json.load(response)

    try:
        command("config", "--quiet")
        command("up", "--build", "--wait", "--wait-timeout", "180")
        assert request("/health")["database"] == "ok"
        with urllib.request.urlopen("http://127.0.0.1:3000", timeout=10) as response:
            assert b"Preflight" in response.read()
        command("exec", "-T", "redis", "redis-cli", "ping")
        command("exec", "-T", "api", "alembic", "current", "--check-heads")
        command("exec", "-T", "api", "alembic", "check")
        account = request(
            "/auth/register",
            {"email": f"{uuid.uuid4().hex}@example.test", "password": secrets.token_urlsafe(32)},
        )
        csrf = account["csrf_token"]
        readiness = request("/execution-readiness")
        assert readiness["background_queue"]["status"] == "AVAILABLE", readiness
        assert readiness["docker"]["status"] == "BLOCKED", readiness
        workspace = request("/workspaces")[0]
        project = request(
            f"/workspaces/{workspace['id']}/projects", {"name": "Infrastructure verification"}
        )
        agent = request(
            f"/projects/{project['id']}/agents",
            {"name": "Native runner", "version": "1.0", "config": {"mode": "accurate"}},
        )
        run = request(
            f"/projects/{project['id']}/runs",
            {
                "version_id": agent["versions"][0]["id"],
                "idempotency_key": uuid.uuid4().hex,
                "backend": "trusted-demo",
                "trials": 2,
            },
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            result = request(f"/runs/{run['id']}")
            if result["status"] in {"COMPLETED", "BLOCKED", "FAILED", "CANCELLED"}:
                break
            time.sleep(0.5)
        assert result["status"] == "COMPLETED", result["status"]
        assert result["summary"]["sample_size"] == 16
        assert result["summary"]["task_success_rate"] == 1
        assert all(a["result"]["events"] for a in result["attempts"])
        assert [t["current"] for t in result["transitions"]] == [
            "QUEUED",
            "PREPARING",
            "RUNNING",
            "SCORING",
            "COMPLETED",
        ]
        probe = "\n".join(
            [
                "import asyncio",
                "from preflight.arq_worker import settings",
                "from arq.connections import create_pool",
                "from arq.jobs import Job",
                "async def check():",
                "    pool = await create_pool(settings())",
                f"    result = await Job({'preflight-' + run['id']!r}, pool).result(timeout=5)",
                "    assert result is True",
                "    await pool.aclose()",
                "asyncio.run(check())",
            ]
        )
        compile(probe, "compose-arq-probe", "exec")
        command("exec", "-T", "api", "python", "-c", probe)
        if os.environ.get("PREFLIGHT_COMPOSE_BROWSER") == "1":
            subprocess.run(
                ["npx", "playwright", "test", "-c", "playwright.compose.config.ts"],
                cwd=ROOT,
                env=env,
                check=True,
                timeout=180,
            )
        command("restart", "worker")
        assert request(f"/runs/{run['id']}")["summary"] == result["summary"]
        print(
            "Compose verified: healthy Next/PostgreSQL/Redis/API/worker, migrations without drift, "
            "durable worker completed 16 native attempts, persisted results after worker restart. "
            "Compose runs trusted-demo; restricted Docker execution is tested separately."
        )
    except Exception:
        command("logs", "--tail", "80", "web", "api", "worker", "postgres", "redis")
        raise
    finally:
        # No --volumes: named volumes, including any successful evidence, are preserved.
        command("down", "--timeout", "20")


if __name__ == "__main__":
    main()
