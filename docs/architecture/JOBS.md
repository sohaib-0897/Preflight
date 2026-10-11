# Durable execution

Redis 7.4.5 and ARQ 0.28.0 coordinate jobs. ARQ requires redis-py <6;
the runtime pins redis-py 5.3.1 rather than the incompatible former optional 6.4.0.
The database is authoritative: conditional claims and PostgreSQL project advisory
locks enforce two active executions per project and twenty queued/active runs.
Immutable unique scenario/trial attempts and run idempotency keys prevent duplicate
fixture mutations. Redis dispatch periodically reconciles queued database rows.

Only native fixtures automatically resume expired leases: their side effects belong
to fresh per-attempt fixture databases. Completed attempts are retained. Connected
agents with ambiguous external effects become BLOCKED and require an explicit new
run; they are never blindly re-posted after an infrastructure failure. HTTP retries
cover connection establishment only. Docker infrastructure retries remain bounded.

Cancellation is checked between attempts and during container execution. Container
cancellation kills the CLI process and removes the labeled container. Connected
invocation cancellation stops local waiting and suppresses local broker mutations;
it cannot guarantee remote process termination. ARQ shutdown signals executor
threads, waits for bounded execution, and preserves safe native work for resumption.
API native demo execution runs in FastAPI's threadpool, so progress and cancellation
requests can be served concurrently.

Existing synchronous relational service queries remain compatible and run in bounded
threads. SQLAlchemy async sessions with real aiosqlite/psycopg drivers are used for
readiness and Redis dispatch. This is an incremental migration; full asynchronous
service conversion has not been completed. The schema and stored artifacts are
preserved. Do not share an AsyncSession across concurrent tasks.

Verification: `python scripts/verify_queue.py` with REDIS_URL runs actual ARQ jobs
on a randomly named private queue. It verifies two concurrent evaluations (32
persisted attempts), duplicate enqueue rejection, and cancelled-job non-execution.
It removes only its own queue keys. CI runs this against Redis 7.4.5; Compose smoke
also reads the actual ARQ job result, checks PostgreSQL migrations and restarts the
worker while preserving results. Local verification used an isolated Ubuntu Redis
8.0.5 binary extracted under `.local`; no system service was installed.
