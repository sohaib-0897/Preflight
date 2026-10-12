# Integrated local deployment

From the repository root, configure a private URL-safe POSTGRES_PASSWORD in the
shell or untracked root .env. Existing PostgreSQL volumes retain the password used
when initialized: preserve that value; changing the environment does not rotate
an existing database role password. Never commit .env or provider credentials.

```
docker compose -f infra/compose/compose.yaml up --build -d
docker compose -f infra/compose/compose.yaml ps
```

Open http://localhost:3000 and create the first account with your own private
passphrase. No default user/password is installed. Create a project, connect a
native agent, select the native suite and queue an evaluation. The real Redis/ARQ
worker runs it automatically and PostgreSQL persists its attempts, traces and gate
results. Native demonstration code is trusted fixture code, not arbitrary-code
isolation. No hosted model or model download is required.

Next's versioned multi-stage image uses the standalone Node server and copies local
public/static assets, following the [official deployment guidance](https://docs.docker.com/guides/nextjs/).
Node 22.23.3 and Python 3.12.15 are pinned. PostgreSQL updates within major version
17 to patch 17.11, verified against the official Docker-library version metadata;
existing version-17 data volumes are preserved. Back up data before any upgrade.
Redis retains the verified 7.4.5 baseline and persistent AOF. Review its upstream
license for your deployment; bundled service licensing is independent of Preflight's
own open-source license.

API migration runs after PostgreSQL/Redis health; worker waits for API health; web
waits for API readiness. ARQ's health check verifies the worker health key, not
just Redis ping. API/worker/web run non-root, drop all capabilities, use no-new-
privileges, read-only roots and bounded temporary storage/CPU/memory/PIDs. PostgreSQL,
Redis and worker have no published ports. Web/API bind loopback by default. Named
volumes persist database, AOF, artifact data and encrypted credential key files.
Do not run `down --volumes` against user data. Ordinary `down` preserves volumes.

Existing development servers can occupy port 8000. Set PREFLIGHT_API_PORT to a free
host port and PREFLIGHT_WEB_PORT for the web port. Container routing stays api:8000;
the frontend never needs PostgreSQL or Redis credentials. Production TLS/reverse
proxy setup is manual; set PREFLIGHT_COOKIE_SECURE=true when serving HTTPS.

## Restricted Docker readiness

There is no Docker socket mount in web, public API, worker or agent containers.
Restricted Docker evaluations require a separately controlled operator host worker:

1. Build `docker build -f infra/docker/sandbox.Dockerfile -t preflight-sandbox:0.1.0 .`.
2. Configure that trusted worker's DATABASE_URL and REDIS_URL to reach the private
   services through an operator-managed private network or authenticated tunnel.
3. Start `.venv/bin/arq preflight.arq_worker.WorkerSettings` with
   PREFLIGHT_WORKER_BACKEND=docker. It consumes arq:queue:docker; the ordinary
   Compose worker consumes arq:queue. Database reconciliation routes each backend
   to its matching queue, and workers refuse mismatched jobs. Both workers can
   coexist. Do not expose raw database/Redis publicly or mount the daemon socket.
   Public arbitrary-code workloads remain refused.

Without a configured Docker host worker, Docker jobs remain queued awaiting that
capability. Native evaluations continue through the safe Compose worker. Optional
benchmark dependency environments and connected gateways require explicit operator
installation/network setup; registry readiness discloses missing official runtimes.

The default worker network is internal. For a connected gateway, place the authorized
service on that private network and explicitly configure the exact origin via
PREFLIGHT_AGENT_PRIVATE_ORIGINS. Public egress requires a separately reviewed trusted
worker network configuration and endpoint allowlist. The supported one-command stack
provides all offline native application features without privileged host access.

## Verification

`PREFLIGHT_COMPOSE_BROWSER=1 python scripts/verify_compose.py` creates a uniquely
named Compose project, starts all services, verifies migrations and ARQ result,
executes desktop/mobile Chromium user journeys against Next/PostgreSQL/Redis,
checks persistence after worker restart, and tears down containers without deleting
volumes. Run only where the chosen host ports are free. CI executes this check on
fresh data. The local Codex Docker socket restriction remains a separate blocker.
