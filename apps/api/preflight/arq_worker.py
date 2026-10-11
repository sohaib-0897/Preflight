"""Optional maintained Redis execution backend, unverified in offline host."""
import asyncio
import os
from arq.connections import RedisSettings, create_pool
from .db import Database
from .jobs import perform


async def enqueue(run_id):
    pool = await create_pool(RedisSettings.from_dsn(os.environ["REDIS_URL"]))
    try:
        return await pool.enqueue_job("evaluate",run_id,_job_id="preflight-"+run_id)
    finally:
        await pool.aclose()


async def startup(ctx):
    ctx["database"] = Database()
    ctx["database"].initialize()


async def shutdown(ctx):
    ctx["database"].engine.dispose()


async def evaluate(ctx,run_id):
    return await asyncio.to_thread(perform,ctx["database"],run_id)


class WorkerSettings:
    functions = [evaluate]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(os.environ.get("REDIS_URL","redis://127.0.0.1:6379/0"))
    max_jobs = 2
    job_timeout = 180
    keep_result = 86400
