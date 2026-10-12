# Preflight

Self-hosted evaluation for AI agent developers. Execute scenarios, verify actual outcomes, inspect traces, compare versions and enforce evidence-based release policies.

The offline native suite, Next.js interface, PostgreSQL/Redis worker and restricted Docker runner are exercised in GitHub Actions. Framework examples execute against pinned LangGraph, CrewAI and OpenAI Agents SDK packages. Official τ³/AgentDojo support is a small, authentic scripted smoke subset, **not full benchmark coverage or measured model quality**. See the [verification record](docs/implementation/VERIFICATION.md).

## Start locally

Use Ubuntu with Docker Engine and Compose, Git, and free host ports 3000/8000. Python 3.12 and Node 22 are needed only for development. Preserve the existing database password when reusing volumes.

```bash
git clone https://github.com/sohaib-0897/Preflight.git
cd Preflight
export POSTGRES_PASSWORD='your-private-url-safe-local-password'
docker compose -f infra/compose/compose.yaml up --build -d
docker compose -f infra/compose/compose.yaml ps
```

Open http://localhost:3000. Create your own account with a private passphrase of at least 12 characters; there is no default password. Registration creates an organization and workspace. Create a project, connect an **accurate native agent**, select the native suite and queue an evaluation. The Redis/ARQ worker executes it automatically. PostgreSQL persists results; reports download as JSON, HTML or a PDF overview.

No paid API, model weights or external dataset is required. Native fixture code is trusted demonstration code, not arbitrary-code isolation. The standard stack never mounts the Docker socket. Restricted Docker evaluations require an independently controlled host worker; missing readiness is disclosed. [Compose setup and limits](docs/operations/COMPOSE.md) · [First evaluation](docs/operations/FIRST_EVALUATION.md).

## Supported workflows

- Account sessions, Argon2id passwords, HttpOnly cookies, CSRF, organizations/workspaces and owner/admin/developer/viewer authorization.
- Agent registration, immutable versions, protected credential references and executable HTTP/Python/framework gateways. Endpoint origins require operator authorization; DNS/IP pinning, redirect rejection and request limits enforce the connection boundary.
- Durable Redis/ARQ jobs, separate native/Docker queues, bounded trials/concurrency, cancellation, leases, idempotency and explicit infrastructure failures.
- Eight offline native scenarios: real refund state, false completion, injection, timeout recovery, authorization denial, version regression, local factual evidence and measured latency.
- RealityCheck structured/tolerance assertions, bounded read-only SQL against fixture state, versioned factual sources and audited reviewer assignments/overrides.
- Controlled security scans with synthetic canaries, broker enforcement, severity/evidence/coverage and opt-in supplied-dependency advisory lookup.
- Correlated OpenTelemetry metadata, interactive event/parent-child explorer, deterministic broker replay and failure groups. No hidden reasoning is captured.
- Compatible paired comparisons with scenario sample counts/uncertainty, versioned release policies and PASS/FAIL/INCONCLUSIVE decisions. Missing mandatory evidence never silently passes.
- Authorized redacted reports, review history, benchmark/configuration provenance and integrity-checked artifact snapshots.

Usage/cost are unknown unless a provider reports valid values. An LLM judge, general natural-language fact extraction, hosted inference, S3 storage, OTLP export and microVM execution are not supplied as verified features. Scripted official presets do not yet evaluate arbitrary connected agents. Stronger isolation is required for public arbitrary-code execution; this deployment refuses that workload.

## Development and verification

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.lock
npm ci
npm ci --prefix apps/web
npm run build:offline
bash scripts/dev.sh  # development API, localhost:8000
# In another terminal:
npm --prefix apps/web run dev -- --port 3000
```

Use PREFLIGHT_PORT for a free development API port and PREFLIGHT_API_ORIGIN for Next routing. The older API-served interface remains a compatibility fallback. Hosted providers are opt-in behind an explicitly configured agent gateway; do not invoke billable endpoints without your own authorized budget.

```bash
bash scripts/check.sh  # all Python checks; live Docker tests require daemon access
PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run build
npm --prefix apps/web test
npx playwright install --with-deps chrome
npx playwright test -c playwright.next.config.ts
```

Local Codex cannot access this host's Docker socket. Actual container, PostgreSQL migration, Redis worker and Compose browser verification runs on Docker-enabled GitHub Actions; local tests are reported separately.

## Guides

- [Architecture](docs/architecture/001-modular-monolith.md) · [UI](docs/architecture/UI.md)
- [Operations and recovery](docs/operations/OPERATIONS.md) · [Compose](docs/operations/COMPOSE.md)
- [SDK](docs/operations/SDK.md) · [Agent connections](docs/architecture/AGENT-CONNECTIONS.md)
- [Custom suites](docs/benchmarks/AUTHORING.md) · [Official benchmarks](docs/benchmarks/UPSTREAM.md)
- [RealityCheck](docs/architecture/REALITYCHECK.md) · [Security assessments](docs/security/ASSESSMENTS.md)
- [Sandbox boundary](docs/security/SANDBOX.md) · [Tracing](docs/architecture/TRACING.md)
- [Comparison methodology](docs/architecture/COMPARISONS.md) · [Release CI](docs/operations/RELEASE_GATES.md)
- [API](docs/operations/API.md) · [Handover](docs/implementation/HANDOVER.md)

Open `/docs` or `/openapi.json` for the generated API contract. Set up TLS and secure cookies before nonlocal exposure. This is a developer evaluation platform, not a production security certification.

[Dependency audit and optional upstream risks](docs/security/DEPENDENCIES.md).

MIT licensed application. Bundled services and optional benchmarks retain their own licenses. [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md).
