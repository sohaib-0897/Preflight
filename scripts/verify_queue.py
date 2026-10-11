"""Real Redis/ARQ test on an isolated queue; does not flush operator keys."""

import asyncio
import os
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in [
    "apps/api",
    "packages/evaluation-core",
    "packages/agent-adapters",
    "packages/benchmark-adapters",
    "packages/scoring",
    "packages/security",
    "tests",
]:
    sys.path.insert(0, str(ROOT / folder))


async def main():
    from arq.connections import create_pool
    from arq.worker import Worker
    from preflight.arq_worker import settings, evaluate
    from preflight.db import Database, EvaluationRun
    from preflight.main import create_app
    from asgi_client import ASGIClient
    from conftest import setup_project

    queue = "preflight:verify:" + uuid.uuid4().hex
    pool = await create_pool(settings(), default_queue_name=queue)
    # API enqueue must not send test jobs into any shared default operator queue.
    old = os.environ.pop("REDIS_URL", None)
    try:
        with tempfile.TemporaryDirectory(prefix="preflight-queue-") as folder:
            database = Database("sqlite:///" + str(Path(folder) / "queue.sqlite"))
            app = create_app(database)

            def setup():
                with ASGIClient(app) as client:
                    project = setup_project(client)
                    agent = client.post(
                        f"/api/v1/projects/{project['id']}/agents",
                        json={
                            "name": "Queue test",
                            "version": "1.0",
                            "config": {"mode": "accurate"},
                        },
                    ).json()
                    runs = []
                    for index in range(3):
                        run = client.post(
                            f"/api/v1/projects/{project['id']}/runs",
                            json={
                                "version_id": agent["versions"][0]["id"],
                                "idempotency_key": f"real-queue-{index}",
                                "trials": 2,
                            },
                        ).json()
                        runs.append(run["id"])
                    assert client.post(f"/api/v1/runs/{runs[2]}/cancel").status_code == 200
                    return runs

            runs = await asyncio.to_thread(setup)
            jobs = [
                await pool.enqueue_job("evaluate", run_id, _job_id=f"{queue}:{run_id}")
                for run_id in runs
            ]
            assert await pool.enqueue_job("evaluate", runs[0], _job_id=f"{queue}:{runs[0]}") is None
            worker = Worker(
                [evaluate],
                redis_pool=pool,
                queue_name=queue,
                burst=True,
                max_jobs=2,
                handle_signals=False,
                ctx={"database": database, "stops": set()},
                keep_result=30,
            )
            await worker.async_run()
            assert worker.jobs_complete == 3 and worker.jobs_failed == 0
            assert await jobs[0].result(timeout=3) is True
            assert await jobs[1].result(timeout=3) is True
            assert await jobs[2].result(timeout=3) is False
            with database.sessions() as db:
                for run_id in runs[:2]:
                    run = db.get(EvaluationRun, run_id)
                    assert run.status == "COMPLETED" and run.summary["sample_size"] == 16
                assert db.get(EvaluationRun, runs[2]).status == "CANCELLED"
            # Delete only this script's random-prefix keys, never flush Redis.
            keys = [key async for key in pool.scan_iter(match=f"*{queue}*")]
            if keys:
                await pool.delete(*keys)
            await database.async_engine.dispose()
            database.engine.dispose()
            print(
                "Real Redis/ARQ: concurrent runs persisted 32 attempts, duplicate enqueue rejected, cancelled job not executed."
            )
    finally:
        if old:
            os.environ["REDIS_URL"] = old
        await pool.aclose()


if __name__ == "__main__":
    asyncio.run(main())
