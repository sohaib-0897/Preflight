## Platform phase 6 — controlled security workflows

Added authorized basic/adversarial scan scheduling, tenant-scoped coverage reports,
actual connected-agent injection inputs and redacted input provenance, bounded
consumption findings, stable finding identities and optional persisted OSV advisory
lookups. Extended genuine official AgentDojo banking smoke with injection_task_0:
protected and deliberately unsafe scripted agents both achieve utility; only the
unsafe agent completes the attacker transfer and receives a critical release-blocking
finding. Upstream scoring and its subject-matching limitation remain disclosed.

Local evidence: 61 Python tests (live Docker excluded because socket permission is
denied); genuine AgentDojo utility and protected/vulnerable injection runtime checks;
API→worker→official scoring→persistent findings→release rejection; production Next
build, four component tests and ten desktop/mobile Chromium journeys. Actual connected
injection test uses a local HTTP server, no substituted adapter. Reviewed security
screenshots under ignored test-results/. Live opt-in OSV query for FastAPI 0.142.2
returned no known advisory; full dependency coverage is not claimed. Targeted Ruff, Mypy (new scan/advisory modules), secret detection and diff checks
passed. Critical findings remain release-blocking even when accuracy is unassessed.
Remote phase 6 verification pending push.

Phase 5 remote confirmation: bcee0a019bdd5980bd3c49cca1310dc7a7349c79,
https://github.com/sohaib-0897/Preflight/actions/runs/38181172885 SUCCESS.

Limitations: provider usage, source analysis, general adversarial generation, full
AgentDojo coverage and public arbitrary-code isolation are not verified capabilities.
NOT_RUN/INCONCLUSIVE coverage remains visible. Docker access is locally blocked;
mandatory live restrictions continue to run in CI without weakening configuration.
See docs/security/ASSESSMENTS.md for scope, statuses and reproduction.

## Current optional execution limits — 2026-10-12

Local Docker socket is permission denied; live isolation and Compose are verified by
remote CI. Official offline smoke execution is now implemented locally. Full official
hosted/model-driven suites are unverified and require compatible agent protocols,
provider setup and an authorized budget. No API charges were incurred. Default
Compose intentionally excludes optional benchmark environments. Historical blockers
below describe earlier checkpoints and are superseded where explicit evidence above
exists.

# Platform completion — phase 1

**Frontend foundation: COMPLETE AND VERIFIED locally for native workflows; remote CI pending this checkpoint.** Genuine Next.js App Router/React application now replaces the script wrapper. Locked dependencies include Tailwind, Radix Dialog, TanStack Query, React Hook Form, Zod, local open-source fonts and Vitest. Existing API/data contracts and FastAPI fallback are preserved. Module routes cover organizations/workspaces, projects, agents/versions, runs/evidence, benchmarks/datasets, reviews/security/traces, comparisons, policies, reports and settings. Non-native execution remains a later phase, not a frontend claim.

Evidence: production Next build passed; four Vitest tests passed; six sandboxed-Chrome desktop/mobile browser journeys passed (including all-module navigation, logout, real persisted native evaluation/export and axe checks). Screenshots reviewed at `test-results/journey-desktop.png` and `journey-mobile.png`; logs `.local/next-build.log` / `.local/next-browser.log` (ignored). Backend baseline remains independently verified by Docker-enabled CI; local Docker socket is inaccessible. No host groups, daemon permissions, existing service at port 8000 or user volumes were modified.

Development: run API with `PREFLIGHT_PORT=18000 bash scripts/dev.sh`, then `PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run dev -- --port 3000`. Production builds bake rewrite destination; set the origin when building. `npm ci --prefix apps/web`, `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npx playwright test -c playwright.next.config.ts` verify the new host. The test build uses API origin port 18000. Remote workflow now runs production Next build, Vitest and real browser journeys without disabling browser sandboxing.

Inventory: [INVENTORY.md](INVENTORY.md). Broader phases are pending; no official benchmark or external adapter execution is claimed yet. Earlier records below are historical.

# Infrastructure follow-up — 2026-10-12

Git identity/authentication and publishing now work. GitHub Actions verified the sandbox build, all 56 Python tests (14 live Docker), frontend checks and actual Compose/PostgreSQL/Redis/migrations/durable-worker execution. Four local desktop/mobile browser tests now pass with Chromium sandbox enabled on port 18000. The local Codex process still lacks daemon socket access; no host permissions or existing volumes were changed. Full evidence is in VERIFICATION.md.

The following original implementation record is historical. Broader incomplete features (Next.js stack, async persistence, ARQ runtime, official benchmark execution, framework dispatch, stronger isolation and optional services) remain outside this Docker/CI repair scope.

# Environment blockers
- Docker and Compose executables absent; no live container provisioning, isolation, resource or cleanup tests possible here.
- GitHub CLI reports invalid stored token for sohaib-0897. Supplied remote exists and advertises no refs. Cannot authenticate repository metadata changes or pushes.
- Git author identity absent. Phase commits cannot be created without fabricating identity. Phase changes and verification evidence remain local.
- Python 3.12 and uv absent; host Python is 3.14.4. Deployment compatibility remains separately unverified.
- Shell network disabled. Initial pip installation failed; npm registry query was interrupted after it stalled. Cached package recovery is permitted offline dependency installation, not a network bypass.
- Local listening sockets and netlink denied by sandbox. HTTP/browser server execution may be blocked; exercise ASGI in-process.
- Cached wheels recovered and runtime dependencies installed successfully offline. Root TypeScript/Playwright/axe tools and reproducible registry lock verified with offline npm ci.
- Next installation failed ENOTCACHED for missing dependency metadata. Next.js build/lock and the requested React/Tailwind/Radix/TanStack/RHF/Zod/Vitest application stack are incomplete.
- Chrome launch with Chromium sandbox enabled failed at setsockopt(Operation not permitted); no workaround disabling sandbox was attempted. Playwright webServer failed because localhost:8000 bind is denied. Browser visual/keyboard/a11y verification remains blocked.
- API/worker use synchronous SQLAlchemy fallback; async service migration is incomplete. ARQ/Redis bridge source is unverified; cached drivers/queue packages are unavailable.
- PostgreSQL, Compose, Python 3.12 and monitoring runtime unverified. No stronger microVM, S3/MinIO backend, PDF export or OTel exporter is implemented.
- External framework/HTTP adapters are source-level Python integrations and offline contract checks, not first-class verified worker dispatch. Optional providers/Ollama/credential storage, generalized uploaded benchmarks and prose factual retrieval remain incomplete.
- Live dependency vulnerability service lookup requires network. Consistency/static checks do not establish vulnerability absence.
