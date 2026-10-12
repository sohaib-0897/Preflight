# Operations

Use [Compose](COMPOSE.md) for the complete supported native stack and [README](../../README.md) for development prerequisites. Python 3.12 container/CI execution and Node 22 builds use pinned requirements/npm locks. Local host tests also run on Python 3.14. No host security settings or group memberships were changed.

| Variable | Purpose |
|---|---|
| DATABASE_URL | SQLite development URL or postgresql+psycopg URL |
| REDIS_URL | Redis/ARQ coordination; Compose sets it |
| POSTGRES_PASSWORD | Private URL-safe Compose secret; preserve existing initialized value |
| PREFLIGHT_COOKIE_SECURE | Set true under HTTPS; false for loopback development |
| PREFLIGHT_API_ORIGIN | Next server-side API proxy origin |
| PREFLIGHT_API_PORT / PREFLIGHT_WEB_PORT | Override loopback Compose published ports |
| PREFLIGHT_PORT | Development API port |
| PREFLIGHT_WORKER_BACKEND | trusted-demo or independently controlled docker host worker |
| PREFLIGHT_QUEUE_PREFIX | Optional separate operator queue namespace |
| PREFLIGHT_SANDBOX_IMAGE | Prebuilt native image tag or digest |
| PREFLIGHT_ARTIFACT_ROOT | Private local artifact directory |
| PREFLIGHT_CREDENTIAL_KEY | Optional protected encryption key; otherwise private persisted key file |
| PREFLIGHT_AGENT_HOSTS / PREFLIGHT_AGENT_PRIVATE_ORIGINS | Explicit gateway origin allowlists; see connection guide for exact format |
| PREFLIGHT_TAU_PYTHON / PREFLIGHT_AGENTDOJO_PYTHON | Optional pinned official benchmark runtimes |
| PREFLIGHT_TRACE_FILE | Optional metadata-only rotating JSON trace export |
| PREFLIGHT_METRICS_TOKEN | Bearer credential required for global metrics |
| GRAFANA_PASSWORD | Optional monitoring profile secret |

ARQ reconciles durable database jobs into backend-specific Redis queues. Claims, idempotency and leases prevent duplicate ownership. Two active runs and twenty queued runs per project, sixty-four selected attempts and bounded deadlines limit work. Native expired jobs resume persisted progress; ambiguous connected side effects become BLOCKED rather than blindly rerunning a POST. Cancellation is checked between attempts and during supported Docker/subprocess execution. The native development execute endpoint is restricted to trusted built-in fixtures. The legacy database-poll worker remains available.

## Migrations and recovery

Run `.venv/bin/alembic upgrade head` with DATABASE_URL configured. Compose migrates before API startup. Additive migrations preserve original entities; SQLite and actual PostgreSQL migration/worker persistence checks run in CI. Most existing service transactions remain synchronous, while readiness/queue persistence has real SQLAlchemy async integration; this is not a full async conversion.

Stop writes/workers before backups. For SQLite use sqlite3 Connection.backup; preserve private artifact and credential-key directories. For PostgreSQL use pg_dump custom format and pg_restore into a separate database. Keep passwords outside shared command lines, encrypt backups and verify restoration. Automated production backup/restore remains operator-managed and has not been certified here. Never use down --volumes against user data.

## Observability and deployment

Structured JSON logs omit bodies/cookies and correlate requests, workers and attempt-recording spans. PREFLIGHT_TRACE_FILE exports allowlisted metadata; no automatic external collector is contacted. Metrics require the configured token. Optional monitoring Compose syntax is checked; Prometheus/Grafana runtime remains unverified. S3/MinIO and OTLP export are not implemented. Local artifact snapshots and JSON/HTML/PDF exports work without those services.

Before nonlocal deployment configure TLS, secure cookies, protected credentials, ingress/egress policy and independent execution hosts. Docker is an initial boundary; arbitrary public hostile code is refused until a stronger backend exists. No paid cloud infrastructure was provisioned.

## Troubleshooting

- Port occupied: select a free host port using the variables above; preserve existing processes.
- Docker permission denied: operator must provide authorized access or use verified CI. Do not change host permissions or mount the socket into application/agent containers.
- Queue waiting: inspect Settings readiness, the correct backend queue and actual worker health key.
- Official benchmark BLOCKED: install its documented pinned runtime and configure the path. Native evaluations remain available.
- HTTP connection denied: inspect exact origin authorization; do not broaden private/network allowlists indiscriminately.
- Session 403: refresh csrf_token via auth/me and supply X-CSRF-Token on writes; expired sessions require login.
- INCONCLUSIVE release: inspect missing_evidence rather than forcing a pass.
