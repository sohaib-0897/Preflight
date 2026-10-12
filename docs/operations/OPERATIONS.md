# Operations
## Environment
Ubuntu prerequisites: Python 3.12 plus venv, Git with your real configured identity, Node 22/npm, and Docker Engine/Compose for containers. Use rootless Docker where supported. Installation requiring administrative privileges is a manual operator step; no sudo or host policy changes were performed by implementation.

Install runtime dependencies with `pip install -r requirements.lock` and verification tools with `npm ci`. The lock captures the cached, installed Python package versions; host Python 3.14 is verified while Python 3.12 deployment resolution remains unverified. The development requirements include pytest. Next dependencies have no lock because their resolution is blocked; do not claim a reproducible Next build yet.

| Variable | Purpose | Default / requirement |
|---|---|---|
| DATABASE_URL | SQLAlchemy database URL | sqlite:///./.local/preflight.sqlite; PostgreSQL uses postgresql+psycopg |
| PREFLIGHT_COOKIE_SECURE | Secure session cookies | false only for local HTTP; true with TLS |
| PREFLIGHT_SANDBOX_IMAGE | Operator native image | preflight-sandbox:0.1.0; immutable digest recommended |
| PREFLIGHT_ARTIFACT_ROOT | Private artifact directory | .local/artifacts |
| REDIS_URL | Optional ARQ queue | unset; default database worker remains available |
| PREFLIGHT_API_ORIGIN | Next API proxy target | http://127.0.0.1:8000 |
| POSTGRES_PASSWORD | Compose local database secret | required; do not commit |
| GRAFANA_PASSWORD | Optional monitoring profile | required when enabling monitoring |

Run `bash scripts/worker.sh` for queued jobs. It has a two-active-run per-project claim limit, 20 queued-run quota, 64 maximum selected attempts, 1–120 second run timeout, one retry for infrastructure failures and per-attempt persistent progress. Worker leases expire after 180 seconds. Expired execution becomes BLOCKED; create a new run to retry with explicit provenance. The trusted demo button runs bounded built-in jobs in-process for convenient offline use.

Optional Redis/ARQ bridge source is `preflight.arq_worker`. Install project queue extras in a network-enabled environment and launch `arq preflight.arq_worker.WorkerSettings`; this path is not verified locally. Enqueue failure retains a durable database job and logs the fallback. The sync SQLAlchemy service is a local fallback; a fully async persistence migration is outstanding.

## Migrations
`DATABASE_URL=... .venv/bin/alembic upgrade head`. Alembic's frozen initial migration defines 26 application tables; upgrade/downgrade and drift checks pass on SQLite. `Database.initialize` uses create_all only for development/in-process fixture startup. PostgreSQL and migration concurrency need verification before production. Compose API runs Alembic before serving.

## Backup and restore
Stop writes/workers before backups. For SQLite, use Python sqlite3 `Connection.backup` rather than copying an open file. Preserve the artifact directory with restrictive ownership and file modes. For PostgreSQL, use `pg_dump --format=custom` and `pg_restore` under your operator account. Store backups encrypted outside the public repository; verify restores in a separate database. Never put database passwords on shared command lines. PostgreSQL backup/restore has not been executed here.

## Observability
JSON request logs include generated request IDs, OpenTelemetry trace/span IDs, method, status and measured duration; they omit request bodies and cookies. Request, worker and attempt recording spans are implemented. Optional PREFLIGHT_TRACE_FILE exports allowlisted metadata to rotating local JSON logs. `/metrics` exposes global persisted-run count only with a configured PREFLIGHT_METRICS_TOKEN bearer credential; it otherwise returns 401. The monitoring overlay mounts that token for Prometheus. Its Compose configuration is checked, but Prometheus/Grafana runtime operation remains unverified. Do not expose monitoring publicly. See architecture/TRACING.md.

## Deployment considerations
Provider-neutral components are API, worker, relational database, optional Redis and private artifact store. Set TLS/secure cookies, enforce ingress/egress policy, cap request sizes and use isolated execution hosts. Do not expose arbitrary hostile code on Docker. S3-compatible storage has an interface boundary only; a concrete backend and MinIO deployment are outstanding. PDF export is not implemented. No cloud or paid services were provisioned.

## Troubleshooting
- `could not bind ... 8000`: active coding sandbox denies sockets. Run from an ordinary authorized terminal; do not change OS security policies.
- Next ENOTCACHED: Next/React/query/form/component dependencies are unavailable offline. Use the compiled FastAPI interface while completing the requested React stack on a network-enabled machine.
- Docker run BLOCKED: install/configure Docker through normal operator procedures, build the native runner, and launch a host worker. Do not mount the daemon socket in agents.
- Session 403: obtain csrf_token from `/auth/me`, and send X-CSRF-Token on writes. Expired sessions require a fresh login.
- INCONCLUSIVE gate: inspect missing_evidence; do not force missing tests to pass.
- Git commit refused: configure your own existing author identity. GitHub invalid token requires manual reauthentication; no credentials were printed or changed.
