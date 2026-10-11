"""Redis coordinates jobs; relational claims and immutable attempts remain authoritative."""

import asyncio
import os
import threading
import time
from arq import cron
from arq.connections import RedisSettings, create_pool
from arq.worker import Retry
from sqlalchemy import select
from .db import Database, EvaluationRun, AgentVersion, Agent, RunTransition
from .jobs import perform, transition, ACTIVE


def settings():
    return RedisSettings.from_dsn(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))


async def enqueue(run_id, pool=None):
    owned = pool is None
    pool = pool or await create_pool(settings())
    try:
        return await pool.enqueue_job("evaluate", run_id, _job_id="preflight-" + run_id)
    finally:
        if owned:
            await pool.aclose()


def pending(database):
    with database.sessions() as db:
        expired = db.scalars(
            select(EvaluationRun).where(
                EvaluationRun.status.in_(ACTIVE), EvaluationRun.lease_until < time.time()
            )
        ).all()
        for run in expired:
            version = db.get(AgentVersion, run.version_id)
            agent = db.get(Agent, version.agent_id)
            if agent.framework == "native":
                # Native fixtures are per-attempt databases; resuming cannot mutate outside state.
                previous = run.status
                run.status, run.worker_id, run.lease_until = "QUEUED", "", 0
                db.add(
                    RunTransition(
                        run_id=run.id,
                        previous=previous,
                        current="QUEUED",
                        reason="Expired native fixture lease; resume completed attempts without external side effects",
                    )
                )
                db.commit()
            else:
                transition(
                    db,
                    run,
                    "BLOCKED",
                    "Expired connected-agent lease; ambiguous external effects require explicit rerun",
                )
        return None


async def dispatch(ctx):
    await asyncio.to_thread(pending, ctx["database"])
    async with ctx["database"].async_sessions() as db:
        run_ids = list(
            await db.scalars(
                select(EvaluationRun.id)
                .where(EvaluationRun.status == "QUEUED")
                .order_by(EvaluationRun.created_at)
                .limit(100)
            )
        )
    for run_id in run_ids:
        await enqueue(run_id, ctx["redis"])


async def startup(ctx):
    ctx["database"] = Database()
    await asyncio.to_thread(ctx["database"].initialize)
    ctx["stops"] = set()
    await dispatch(ctx)


async def shutdown(ctx):
    for stop in ctx.get("stops", ()):
        stop.set()
    await ctx["database"].async_engine.dispose()
    ctx["database"].engine.dispose()


async def evaluate(ctx, run_id):
    stop = threading.Event()
    ctx.setdefault("stops", set()).add(stop)
    task = asyncio.create_task(asyncio.to_thread(perform, ctx["database"], run_id, stop))
    try:
        result = await asyncio.shield(task)
        with ctx["database"].sessions() as db:
            run = db.get(EvaluationRun, run_id)
            if run and run.status == "QUEUED":
                raise Retry(defer=1)
        return result
    except asyncio.CancelledError:
        # asyncio.to_thread cancellation alone does not stop a running executor thread.
        stop.set()
        await asyncio.shield(task)
        raise
    finally:
        ctx["stops"].discard(stop)


class WorkerSettings:
    functions = [evaluate]
    cron_jobs = [cron(dispatch, second=set(range(0, 60, 5)), run_at_startup=True)]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = settings()
    max_jobs = 2
    max_tries = 120
    job_timeout = 150
    job_completion_wait = 135
    keep_result = 10
    health_check_interval = 10
    health_check_key = "preflight:worker:health"
