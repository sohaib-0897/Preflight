# Platform phase 10 — reports, onboarding and current documentation

Implemented schema-versioned report identity/provenance, full assessment and human
review history, security coverage/findings, actual official scoring evidence and
reproduction limitations. Authorized JSON/HTML exports retain complete evidence;
PDF provides a bounded, offline overview with explicit Unicode escapes. Unknown
accuracy is UNASSESSED in exports and UI. Reports offers real download links;
onboarding uses actual project/agent/run state and mobile Settings permits logout.
Replaced obsolete setup/API/SDK/operations/frontend guides with current contracts.

Local verification: 74 non-Docker Python tests, including parsed PDF contents,
Unicode/unknown outcome handling and cross-tenant PDF rejection. Production Next
build passed; PDF first page rendered and reviewed at .local/phase10-pdf.png.
All ten sandboxed-Chromium desktop/mobile journeys passed, including PDF download, Reports links and mobile logout; four Vitest component tests passed. Reports screenshots reviewed. Legacy frontend checks, pip check, targeted Ruff and repository hygiene passed. Remote phase 10 verification pending push. CI artifact upload
explicitly includes only the whitelisted hidden report paths, never arbitrary .local.

Phase 9 remote confirmation: 16a733358a74e85909a764861606b1de3f5530cf,
https://github.com/sohaib-0897/Preflight/actions/runs/38213300603 SUCCESS (all seven jobs).
Actual remote evidence: 87 Python tests including 15 live Docker checks, ten Next
browser journeys, two desktop/mobile Compose journeys, real PostgreSQL migrations,
Redis queue dispatch and native Docker execution, three actual framework runtimes
and both official scripted smoke integrations. CI Compose screenshots reviewed.
Local daemon access remains denied; no local container success is claimed.

## Platform phase 9 — integrated Compose implementation

Added pinned multi-stage Next standalone image, web/API routing and health ordering,
real ARQ worker health check, non-root read-only application containers, temporary
storage and CPU/memory/PID limits. Data services remain unpublished; persistent
named volumes are preserved. No daemon socket is mounted. Python updates to 3.12.15,
Node is 22.23.3, PostgreSQL stays in major 17 at official patch 17.11. Ports can be
changed without changing internal routing. Compose now includes the complete safe
native web/API/PostgreSQL/Redis/worker stack.

Added actual full-stack desktop/mobile Chromium journey to CI's Compose verifier:
automatic queue execution, persistent results, release decision and report export.
Local Compose syntax, 72 backend tests, production Next build and ten
desktop/mobile journeys pass. Actual local Redis 8.0.5 verification executed 32
native attempts and demonstrated a Docker job staying in its separate queue;
Docker execution remains reserved for CI. Targeted Ruff and secret scan pass; container startup/build remains
IMPLEMENTED BUT UNVERIFIED locally because daemon access is denied. CI verification
pending this phase push. No local container success is claimed. Independent backend queues and actual worker readiness are implemented. Host Docker worker
setup and optional benchmark/gateway environments remain operator-managed;
see docs/operations/COMPOSE.md for precise limitations.

Phase 8 remote confirmation: 1a98d10dda653e3233ce59d312c8f3649a70ad85,
https://github.com/sohaib-0897/Preflight/actions/runs/38212003822 SUCCESS.
Actual negative CI verified in closed, unmerged draft PR #1:
https://github.com/sohaib-0897/Preflight/actions/runs/38212112251 failed release-gate
with exit 1 and uploaded FAIL report, 50% task success. This is intentional negative
verification, not a failing main baseline. Branch 0f60b02 changes only the candidate.

## Platform phase 8 — comparisons and evidence-required release gates

Expanded compatible paired comparisons with dimension-specific denominators,
scenario-cluster latency intervals, valid explicitly reported token/cost coverage,
latest human review statistics and security severity/coverage. Material differences
in security mode, custom assertions and source versions reject comparison. Added
mandatory security categories, high-finding limits and latest approval requirements;
missing evidence stays INCONCLUSIVE. Critical findings survive accuracy uncertainty
and human overrides. Concurrent policy version conflicts return 409. Offline CI
policies validate thresholds and lists rather than accepting invalid release limits.

Local evidence: 71 backend tests excluding daemon checks; targeted Ruff/Mypy;
production Next build and four component tests. All ten desktop/mobile Chromium journeys passed, including compatible version
regression, incompatible coverage rejection, metrics table, release FAIL, axe checks
and keyboard scrolling. Comparison screenshots were reviewed. A real mobile table
focus defect was fixed; no accessibility rule was disabled. CLI accurate PASS exit 0 and regressed FAIL exit 1 were
executed. Usage tests use clearly synthetic prices to verify math only; actual demo
usage remains unknown. Remote phase 8 verification pending push.

Phase 7 remote confirmation: 31a60a47d56afbaaadf0fa5e7b1e3045bc5df6ce,
https://github.com/sohaib-0897/Preflight/actions/runs/38210955553 SUCCESS,
all seven jobs, including native Docker/Compose, frameworks and official cases.
See docs/architecture/COMPARISONS.md for definitions and uncertainty limitations.

## Platform phase 7 — correlated tracing and deterministic diagnostics

Implemented real OpenTelemetry request→worker→attempt recording spans, persisted
correlation identities, metadata-only rotating JSON export, actual structured JSON
request logging and authenticated global metrics. Added interactive accessible trace
parent/child navigation, event filtering, structural run comparison and tenant-scoped
individual JSON export. Deterministic diagnosis retains evidence and distinguishes
suspected loops from verified failures; agent-reported denials are not broker proof.
No hidden reasoning or unconfigured LLM hypotheses are generated.

Local verification: 66 backend tests excluding daemon-dependent checks; four React
component tests; production Next build; desktop/mobile Chromium trace navigation,
comparison, downloads and axe checks: all ten journeys passed. Desktop/mobile
trace screenshots were inspected. Exact dropdown labels and a review-navigation
race were corrected; broker replay excludes reported intentions and refuses
unsupported upstream tools.
Targeted Ruff and Mypy pass; pip check has no broken requirements. Monitoring overlay
Compose config validates with synthetic setup values. Runtime monitoring/OTLP remains
unverified. Optional trace output is local only. Remote phase 7 verification pending.

Phase 6 remote confirmation: 5b25b0a24bf13fa6c669936b7e36afb84e702ee2,
https://github.com/sohaib-0897/Preflight/actions/runs/38209723144 SUCCESS,
all seven jobs including genuine official injection, live Docker and Compose passed.
See docs/architecture/TRACING.md for semantics and remaining scope.

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

## Deterministic configurable RealityCheck

Captured fixture rows support SQL assertions in an in-memory read-only database with SQLite authorization and a VM-step budget, never the application/host database. Unknown evidence remains INCONCLUSIVE and unassessed attempts are excluded from accuracy denominators. Immutable project sources and dataset fingerprints preserve provenance. Supplemental assessments append evidence; release score changes require explicit configured assertions or justified human overrides.

## Official offline integration boundary

τ³ is installed as upstream package `tau2`, pinned to v1.0.1 commit fc0055dc4e0a316c3f83133267fbd6faaa770992. Its ENV scorer and AgentDojo banking utility scorer execute unchanged. Optional fixed trusted scripted-agent presets are exposed separately from general agent/model benchmarking. Environment-assertion cases can raise upstream exceptions on missing state; the verified tau create_task_1 DB-scoring case supplies both pass and fail evidence without inventing a score from exceptions. Full hosted/adversarial suites remain independently unverified.

## Isolated framework environments

CrewAI and OpenAI Agents SDK have incompatible OpenAI package requirements. Separate hash-locked Python 3.12 environments preserve maintained versions and real runtime tests. Credential keys persist outside images; arbitrary code stays in operator-owned gateways.

# Platform completion — phase 1

**Frontend foundation: COMPLETE AND VERIFIED locally for native workflows; remote CI pending this checkpoint.** Genuine Next.js App Router/React application now replaces the script wrapper. Locked dependencies include Tailwind, Radix Dialog, TanStack Query, React Hook Form, Zod, local open-source fonts and Vitest. Existing API/data contracts and FastAPI fallback are preserved. Module routes cover organizations/workspaces, projects, agents/versions, runs/evidence, benchmarks/datasets, reviews/security/traces, comparisons, policies, reports and settings. Non-native execution remains a later phase, not a frontend claim.

Evidence: production Next build passed; four Vitest tests passed; six sandboxed-Chrome desktop/mobile browser journeys passed (including all-module navigation, logout, real persisted native evaluation/export and axe checks). Screenshots reviewed at `test-results/journey-desktop.png` and `journey-mobile.png`; logs `.local/next-build.log` / `.local/next-browser.log` (ignored). Backend baseline remains independently verified by Docker-enabled CI; local Docker socket is inaccessible. No host groups, daemon permissions, existing service at port 8000 or user volumes were modified.

Development: run API with `PREFLIGHT_PORT=18000 bash scripts/dev.sh`, then `PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run dev -- --port 3000`. Production builds bake rewrite destination; set the origin when building. `npm ci --prefix apps/web`, `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npx playwright test -c playwright.next.config.ts` verify the new host. The test build uses API origin port 18000. Remote workflow now runs production Next build, Vitest and real browser journeys without disabling browser sandboxing.

Inventory: [INVENTORY.md](INVENTORY.md). Broader phases are pending; no official benchmark or external adapter execution is claimed yet. Earlier records below are historical.

# Decisions
2026-10-10: Modular monolith with separate worker, pure Python evaluation packages, FastAPI transport, SQLAlchemy persistence. Docker Compose targets Python 3.12; this host has 3.14. Native scenarios are deterministic and require no model credentials.

The restricted environment prohibits network sockets and lacks Docker. Use cached packages where available. SQLite is the executable local fallback; PostgreSQL is the deployment database. Trusted built-in demo execution is explicitly labeled and must never execute user code. Docker execution fails closed when unavailable. External adapters remain separately qualified.

Git identity must come from existing configuration. None is configured; do not invent an author to satisfy a phase commit.

- SQLAlchemy synchronous services were used for the executable offline fallback; async drivers/greenlet are not cached. FastAPI async transport endpoints avoid TestClient's prohibited cross-thread socket wakeups in this host. Production async persistence remains outstanding; sync work currently blocks each API process's event loop.
- Database polling is the executable durable queue; optional ARQ/Redis integration source is provided but not installed/verified. Redis enqueue failure retains the database job.
- Next.js 16.4.0 and React 19.3.0 metadata were verified through official npm registry; dependencies cannot be installed offline. Root TypeScript/Playwright/axe tools were installed from existing cached tarballs. The generated lock was normalized to the original registry tarball URLs with real cached integrity hashes; `npm ci --offline` subsequently passed.
- Browser launch retains Chromium sandboxing; denied socket operations were not bypassed. E2E startup also fails to bind localhost. No visual review or accessibility score is claimed.
- Human overrides affect release task scoring only when the immutable policy explicitly enables them. Critical findings and automatic evidence remain intact.
- Statistical inference clusters deterministic repetitions by scenario. Small native fixture runs are smoke evidence, not production accuracy estimates.
