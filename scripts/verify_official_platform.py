"""Real API -> worker -> official runtime -> persisted report, isolated temporary data."""

import os
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in [
    "apps/api",
    "packages/evaluation-core",
    "packages/benchmark-adapters",
    "packages/agent-adapters",
    "packages/scoring",
    "packages/security",
    "tests",
]:
    sys.path.insert(0, str(ROOT / folder))

def main():
    from preflight.db import Database
    from preflight.main import create_app
    from preflight.jobs import perform
    from conftest import setup_project
    from asgi_client import ASGIClient

    benchmark = sys.argv[1]
    env = "PREFLIGHT_TAU_PYTHON" if benchmark == "tau3" else "PREFLIGHT_AGENTDOJO_PYTHON"
    folder = "tau" if benchmark == "tau3" else "agentdojo"
    os.environ[env] = str(ROOT / f".local/{folder}-venv/bin/python")
    os.environ.pop("REDIS_URL", None)
    with tempfile.TemporaryDirectory(prefix="preflight-official-api-") as temporary:
        app = create_app(Database("sqlite:///" + str(Path(temporary) / "app.sqlite")))
        with ASGIClient(app) as client:
            project = setup_project(client)
            for mode in ["accurate", "regressed"]:
                agent = client.post(
                    f"/api/v1/projects/{project['id']}/agents",
                    json={"name": f"Official offline {mode}", "version": "1", "config": {"mode": mode}},
                ).json()
                response = client.post(
                    f"/api/v1/projects/{project['id']}/runs",
                    json={
                        "version_id": agent["versions"][0]["id"],
                        "benchmark": benchmark,
                        "idempotency_key": uuid.uuid4().hex,
                        "timeout_seconds": 60,
                    },
                )
                assert response.status_code == 201, response.text
                run = response.json()
                assert perform(app.state.db, run["id"])
                result = client.get(f"/api/v1/runs/{run['id']}").json()
                assert result["status"] == "COMPLETED", result
                assert result["summary"]["task_success_rate"] == int(mode == "accurate"), result
                official = result["attempts"][0]["result"]["official_evidence"]
                assert official["benchmark"] == benchmark and not official["hosted_model_called"]
                report = client.get(f"/api/v1/runs/{run['id']}/report.json").json()
                assert report["config"]["benchmark"] == benchmark, report.keys()
                # Minimum independent sample policy correctly refuses a one-case release.
                assert (
                    client.post(f"/api/v1/runs/{run['id']}/release", json={}).json()["decision"]
                    != "PASS"
                )
        app.state.db.engine.dispose()
    print(
        f"{benchmark}: official accurate/regressed worker runs persisted, report exported, insufficient release sample did not pass."
    )


if __name__ == "__main__":
    main()
