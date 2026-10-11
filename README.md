# Preflight

Self-hosted, evidence-based evaluation for agent developers. Run deterministic offline agents, verify what actually changed, inspect tool events, compare versions, and apply release policies.

**Status: native evaluation and restricted Docker boundary verified; platform completion in progress.** Next.js/React workflows, PostgreSQL/Compose infrastructure, native releases and representative desktop/mobile accessibility checks are verified. Official benchmark execution and nonnative worker dispatch remain separately qualified. See the [verification matrix](docs/implementation/VERIFICATION.md).

## Working native features

- Registration, Argon2id passwords, expiring HttpOnly sessions, CSRF, organizations, workspaces, role enforcement, projects and audit records.
- Native agent registry with immutable version configurations and fingerprints; standalone Python client and framework adapter source.
- Durable jobs, state transitions, idempotency, bounded trials and concurrency, cancellation, worker leases and infrastructure failure separation.
- Eight offline scenarios: refunds, false completion, document injection, timeout recovery, unauthorized operations, version regression, trusted factual claims and measured latency.
- RealityCheck structured scoring, real SQLite side-effect checks, local evidence provenance, confidence/Brier scoring and audited reviews. Optional explicit review overrides preserve automatic evidence.
- Synthetic security findings, redacted event timelines/graphs, deterministic broker replay and trace comparison.
- Paired version comparisons, conservative uncertainty, immutable release policies and PASS/FAIL/INCONCLUSIVE decisions.
- Persisted results, integrity-checked artifact snapshots, authorized JSON/HTML exports, a functional TypeScript interface and CI examples.

No paid API or model download is needed for the native demo. No hidden model reasoning is captured.

## Quick start

From the local checkout, or after these sources have been published to the configured remote, use a normal Ubuntu development machine with network access, Python 3.12 and Node 22:

```bash
git clone https://github.com/sohaib-0897/Preflight.git
cd Preflight
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock
npm ci
npm run build:offline
bash scripts/dev.sh
```

Open http://127.0.0.1:8000. Choose **Create a new account**, enter your private passphrase (12+ characters), create a project, connect an accurate native agent, queue a native suite and select **Execute native demo**. There are no shared demo credentials or default account. See [first evaluation](docs/operations/FIRST_EVALUATION.md).

For the Next.js interface, install with `npm ci --prefix apps/web`, start the API, then run `npm --prefix apps/web run dev -- --port 3000`. Configure `PREFLIGHT_API_ORIGIN` for a nondefault backend. Existing services are preserved; use `PREFLIGHT_PORT` to choose a free API port.

Run the standalone core immediately without opening a port:

```bash
python3 scripts/demo.py --mode accurate --output .local/report.json
python3 scripts/demo.py --mode regressed --output .local/regression.json
```

Accurate demo exits 0; regressed demo exits 1 because the policy fails. These are native fixture outcomes, not official benchmark scores or production accuracy estimates. Unknown API cost and token usage remain null.

## Docker Compose

```bash
export POSTGRES_PASSWORD='choose-a-private-local-password'
docker compose -f infra/compose/compose.yaml up --build
```

The API is bound to localhost:8000, with PostgreSQL and Redis on an internal network. This Compose setup runs trusted native demonstrations; Redis/ARQ is optional and the default worker uses the durable database queue. Do not enter a real shared password into committed files. Compose service/migration/worker verification passes on Docker-enabled GitHub Actions. Local Codex daemon access remains blocked. The API image migrates schema before startup. Configure TLS and secure cookies before any nonlocal deployment.

For restricted Docker jobs, build the native sandbox image and run the operator host worker as described in the [sandbox model](docs/security/SANDBOX.md). The Compose worker does not mount a Docker socket.

## Verification and guides

```bash
bash scripts/check.sh
npm run test:e2e  # requires local sockets and sandboxed Chrome
```

- [Architecture and tradeoffs](docs/architecture/001-modular-monolith.md)
- [Environment and operations](docs/operations/OPERATIONS.md)
- [SDK and adapters](docs/operations/SDK.md)
- [Custom suites and scoring](docs/benchmarks/AUTHORING.md)
- [Official benchmark status](docs/benchmarks/UPSTREAM.md)
- [Security methodology](docs/security/METHODOLOGY.md)
- [Release gates and CI](docs/operations/RELEASE_GATES.md)
- [Testing and verified limits](docs/implementation/VERIFICATION.md)
- [API reference](docs/operations/API.md)

The FastAPI reference is available at `/docs` and `/openapi.json` after startup. The Next App Router host in `apps/web` is built and browser-tested with React/query/forms/Radix components. The older FastAPI-served interface remains a compatibility fallback.

MIT licensed. [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md).
