# Live sandbox assertion follow-up

Strengthened the existing live cgroup test to inspect cpu.max, NoNewPrivs and Seccomp,
asserting the half-CPU quota, no-new-privileges and active filtering at runtime.
Memory/PID/capability/file-descriptor, memory exhaustion, disk, network and cleanup
checks remain mandatory. No security configuration or test was relaxed. Actual
remote execution is required; local daemon remains inaccessible.

# Final QA command follow-up

The root npm test:e2e command now selects the maintained Next browser configuration.
The prior default collected Next and Compose tests against the compatibility host.
The corrected command executed all ten desktop/mobile tests successfully (.local/final-default-browser.log). CI now invokes the same standard npm command. All ten Next tests remain required; Compose retains its separate actual stack CI
verifier. No failing scenario or security rule was removed. The underlying phase 11
code checkpoint passed all seven jobs in Actions 38216348545.

# Platform phase 11 — final verification checkpoint

Completed repository-wide Python formatting/lint without disabling checks, targeted
Mypy for SDK/adapters/metrics/security/telemetry, installed SDK wheel verification,
actual framework/official smoke reruns, full available backend/browser checks,
Redis queue verification and dependency audits. CI now enforces static checks,
wheel invocation, all live Docker tests and every PR release gate. Main pushes and
PRs remain verified; duplicate branch-push runs are avoided. Sandbox Python patch
is 3.12.15; image references resolve once to an immutable inspected OCI ID, recorded
in results and asserted by the live tests. No isolation restriction was removed.

Local: 76 Python tests excluding the daemon-inaccessible suite; all ten desktop/mobile
Chromium journeys, four Vitest tests, legacy frontend checks, production Next build,
pip check, Ruff and targeted Mypy pass. Actual installed wheel gateway passes;
three frameworks each invoke eight scenarios; official pass/fail and AgentDojo
injection cases execute upstream scoring without outbound connections. Actual
private Redis 8.0.5 queue persists 32 attempts, rejects duplicate enqueue and
honors cancellation. Fifteen local Docker checks return prerequisite errors for
permission denied, not skips/passes. Compose configuration validates.

Dependency audits: core Python and both npm locks have no returned known advisories;
LangGraph/OpenAI Agents/AgentDojo isolated environments likewise. CrewAI ChromaDB
and tau2's constrained LiteLLM have unresolved advisory findings; see
security/DEPENDENCIES.md. These optional findings are not hidden by green CI.
Full async service conversion, general model/official-suite execution, stronger
arbitrary-code isolation and optional external storage/judging remain incomplete.

Previous fully verified remote checkpoint:
2ca10e708057f827d4e47752b582be3e12307838,
https://github.com/sohaib-0897/Preflight/actions/runs/38215112138 SUCCESS, all seven jobs:
89 Python including 15 live Docker, ten Next Chromium and two Compose Chromium
journeys, actual PostgreSQL migrations/persistence, Redis/native Docker queues,
three framework and both official integrations. Phase 11 remote verification now passed: 07c68dc63fa647f8ef438cbdf79ef8bd4e4e0ef5,
https://github.com/sohaib-0897/Preflight/actions/runs/38216348545, all seven jobs SUCCESS. Actual results: 91 Python tests including fifteen live Docker checks with immutable image identity; ten Next and two Compose Chromium journeys; SDK wheel/static checks, PostgreSQL migrations, Redis/native Docker execution and both official smoke integrations. Logs/artifacts are .local/final-ci.log and .local/final-ci-artifacts. Local Docker access remains denied.

# Historical milestone log

Earlier pending/blocker statements below describe their checkpoints and are superseded by the current verification record.

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

## Platform phase 5 — configurable RealityCheck

Implemented immutable tenant-scoped reference source versions, evidence-backed claim
verification, custom scenario datasets, structured/tolerance/state/tool assertions,
read-only SQL over captured actual fixture rows, supplemental assessment history,
assigned developer reviews, justified decisions and disagreement tracking. Unknown
assertions remain unassessed accuracy and block release instead of scoring zero/pass.
Existing automated scores are preserved when supplemental/human evidence is added.

Local verification: 56 backend checks passed; four React unit checks; production
Next build; eight desktop/mobile Chromium journeys including source ingestion,
custom dataset evaluation and assigned review. Targeted Ruff and Mypy checks passed.
Actual browser screenshots reviewed at test-results/realitycheck-{desktop,mobile}.png.
Dialog focus restoration and hidden skip-link painting were corrected. Remote phase
verification pending push. Structured local references are supported; general prose
extraction, LLM semantic judges and arbitrary external SQL environments remain partial.

Phase 4 remote confirmation: commit e3c1ce9, Actions 38180292025 SUCCESS. Both genuine
official benchmark jobs executed accurate/regressed upstream scoring and worker
persistence; native Docker/Compose, framework matrix and frontend jobs also passed.

## Platform phase 4 — official offline smoke execution

Implemented pinned isolated official runtimes, fixed offline entry points, upstream
scoring preservation, API/worker integration and selectable installed presets.
τ³ mock create_task_1 and AgentDojo banking user_task_0 execute genuinely; accurate
and missing-action reference versions produce upstream 1/0. Real worker persistence,
reports and conservative gates verified locally. Network-denied runtime tests found
no outbound connections. Official CI matrix added; remote verification pending.

This is OFFICIAL_SMOKE_EXECUTED, not full-suite/model-quality verification. Compatible
arbitrary agent protocols, hosted suites and AgentDojo adversarial coverage remain
partial/unverified. See docs/benchmarks/UPSTREAM.md for installation and exact scope.

Phase 3 remote confirmation: commit a705713, Actions 38179576766 SUCCESS: 65 Python
checks including 15 live Docker checks, real Redis jobs, PostgreSQL-backed ARQ
Compose result and migrations; six Chromium checks, framework matrix all passed.
The initial Compose helper quoting failure was repaired without weakening tests.

## Platform phase 3 — durable orchestration (local verification)

Redis/ARQ integration, concurrent durable claims, reconciliation, native lease
recovery, cancellation-aware container lifecycle, bounded shutdown and safe handling
of ambiguous remote side effects are implemented. Compose uses the ARQ worker and
Redis dependencies. Actual queue smoke verified two concurrent evaluations with 32
persisted attempts, duplicate rejection, and cancellation without execution. Local
backend: 50 passed; Next browser: six passed; frontend unit/type checks passed.
Compose config validates locally. New live container cancellation check awaits CI.

Async SQLAlchemy readiness/dispatch use real drivers; retained synchronous services
run in FastAPI threads. Full async service conversion remains partial. Local Docker
socket remains permission denied; no host permissions changed. See JOBS.md.

## Platform phase 2 — executable connections (local verification)

Implemented HTTP/SDK gateways, actual LangGraph/CrewAI/OpenAI Agents runtimes,
workspace encrypted credential references, connection health, pinned DNS/TLS SSRF
controls, and connected-agent native scenario execution with broker state validation.
New migration is additive; existing agent interfaces and native execution remain.

Verification: 47 backend tests passed locally (14 live Docker checks excluded only
because this session cannot access the daemon); four frontend unit tests, production
Next.js build and six Chromium browser checks passed. Each of three isolated actual
framework runtimes executed all eight scenarios without hosted inference. Real TCP
HTTP invocation, SDK session invocation, TLS hostname preservation, DNS resolution
pinning and tenant credential isolation were exercised. CI runtime matrix added;
remote phase verification is pending until the commit is pushed.

Limitations: local Docker remains inaccessible; live Ollama/hosted models were not
called. Framework examples deliberately use deterministic offline inference. Remote
process termination after cancellation requires gateway cooperation. See
[connection architecture](../architecture/AGENT-CONNECTIONS.md).

Phase 1 checkpoint `5052507`: [CI 38177616507](https://github.com/sohaib-0897/Preflight/actions/runs/38177616507) passed all native/Docker checks but caught a browser race when a dependent action preceded agent query loading. Fixed persistent layout query cache and action readiness; mandatory test unchanged, rerun pending.

# Platform completion — phase 1

**Frontend foundation: COMPLETE AND VERIFIED locally for native workflows; remote CI pending this checkpoint.** Genuine Next.js App Router/React application now replaces the script wrapper. Locked dependencies include Tailwind, Radix Dialog, TanStack Query, React Hook Form, Zod, local open-source fonts and Vitest. Existing API/data contracts and FastAPI fallback are preserved. Module routes cover organizations/workspaces, projects, agents/versions, runs/evidence, benchmarks/datasets, reviews/security/traces, comparisons, policies, reports and settings. Non-native execution remains a later phase, not a frontend claim.

Evidence: production Next build passed; four Vitest tests passed; six sandboxed-Chrome desktop/mobile browser journeys passed (including all-module navigation, logout, real persisted native evaluation/export and axe checks). Screenshots reviewed at `test-results/journey-desktop.png` and `journey-mobile.png`; logs `.local/next-build.log` / `.local/next-browser.log` (ignored). Backend baseline remains independently verified by Docker-enabled CI; local Docker socket is inaccessible. No host groups, daemon permissions, existing service at port 8000 or user volumes were modified.

Development: run API with `PREFLIGHT_PORT=18000 bash scripts/dev.sh`, then `PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run dev -- --port 3000`. Production builds bake rewrite destination; set the origin when building. `npm ci --prefix apps/web`, `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npx playwright test -c playwright.next.config.ts` verify the new host. The test build uses API origin port 18000. Remote workflow now runs production Next build, Vitest and real browser journeys without disabling browser sandboxing.

Inventory: [INVENTORY.md](INVENTORY.md). Broader phases are pending; no official benchmark or external adapter execution is claimed yet. Earlier records below are historical.

# Infrastructure follow-up — 2026-10-12

Git identity/authentication and publishing now work. GitHub Actions verified the sandbox build, all 56 Python tests (14 live Docker), frontend checks and actual Compose/PostgreSQL/Redis/migrations/durable-worker execution. Four local desktop/mobile browser tests now pass with Chromium sandbox enabled on port 18000. The local Codex process still lacks daemon socket access; no host permissions or existing volumes were changed. Full evidence is in VERIFICATION.md.

The following original implementation record is historical. Broader incomplete features (Next.js stack, async persistence, ARQ runtime, official benchmark execution, framework dispatch, stronger isolation and optional services) remain outside this Docker/CI repair scope.

# Phase status
Implementation date: 2026-10-10. Local branch main. No existing project files were overwritten. All phase commits/pushes are blocked by absent Git author identity and invalid GitHub CLI authentication. One commit attempt failed before creating a commit; no author was invented. Remote configured to the supplied repository URL.

| Phase | Status | Implemented / remaining |
|---|---|---|
| 0 Environment audit | Verified locally; Git blocked | Ubuntu 26.04.1, 8 CPUs, 15 GiB RAM, 416 GiB free, Python 3.14.4, Node 22.22.1, npm 9.2.0; repository initialized. Docker/uv absent; GitHub token invalid and identity absent. |
| 1 Foundation | Partial | FastAPI/Pydantic, SQLAlchemy, SQLite, frozen Alembic migration, health, structured logs, dependency locks, CI/Compose source. PostgreSQL/Redis/Compose runtime, Python 3.12 and async persistence unverified/outstanding. |
| 2 Authentication/workspaces | Backend verified | Registration/login, Argon2id, sessions, CSRF, organizations, workspaces, roles, projects, memberships and audit. Tenant/viewer/expiry/rate-limit tests pass. Browser flow blocked. |
| 3 Agent integrations | Partial | Native registry, immutable versions/fingerprints, Python client, HTTP and framework bridge source. Contract objects tested. Real framework packages, SDK packaging, HTTP worker dispatch, credentials and local model integration outstanding. |
| 4 Sandbox execution | Source/policy verified; live blocked | Restricted Docker native backend, timeout/cleanup, denying stronger-isolation policy, real enforcing SQLite broker. Six live Docker tests skipped; Docker absent. No arbitrary untrusted code execution. |
| 5 Native evaluations | Backend verified | Eight native scenarios, real state checks, durable workers/transitions, idempotency, bounded concurrency/trials/timeout, cancellation, infrastructure retries, immutable datasets/config snapshots, results/evidence persistence. SSE finite snapshots and actual UI polling. |
| 6 RealityCheck | Native methods verified; generalized coverage partial | Structured/tolerance ground truth, state/side effects, local structured factual evidence, confidence/Brier checks, audited review overrides. General prose claim extraction, semantic scoring and general evidence retrieval outstanding. |
| 7 Security health | Controlled native checks verified; broader scans partial | Synthetic canary, injection outcomes, broker denial, tool budgets/loops, redaction, tenant/session/artifact tests. Dependencies/remote API tests explicitly NOT_RUN. No live hostile-container security claim. |
| 8 Public benchmarks | Partial/blocked | Current upstream APIs/licenses reviewed, optional bridges and normalization fixtures tested. τ³/AgentDojo package installation and official scenario execution unverified; no official scores. |
| 9 Tracing/failure analysis | Native verified | Ordered accessible events, trace graphs, duplicates/retries/tool errors, deterministic replay/diffs and rule-based failure clusters. No hidden reasoning; optional LLM diagnostics not implemented. |
| 10 Comparisons/release | Backend/CLI verified | Compatible paired runs, regression detection, scenario-cluster statistics, immutable policies, PASS/FAIL/INCONCLUSIVE, reviewed overrides and CI source. GitHub checks/branch protection not remotely exercised. |
| 11 Frontend | Partial; visual acceptance blocked | Functional responsive TypeScript interface across product sections, real data/forms/evidence/export, strict typecheck and build. Next host source only. Requested full React/query/form/component stack and Vitest outstanding. Chrome/socket restrictions block browser/a11y reviews. |
| 12 Reports/operations | Core verified; optional backends partial | JSON/HTML reports, private integrity-checked local artifacts, API docs, operations/backup/security guides, metrics and monitoring source. PDF/S3/MinIO/OTel exporter implementation outstanding; monitoring runtime unverified. |
| 13 Hardening | Available verification passes; acceptance incomplete | Backend/ASGI, migrations, security, native scenarios, comparison/gates, TypeScript and utility tests. Docker, PostgreSQL, Redis/ARQ, browser/a11y, official suites and remote CI remain blocked/unverified. |

## Required commit checkpoints
All requested messages are recorded below for a future authorized Git session. No phase is marked complete through a nonexistent commit:

0 chore: initialize Preflight architecture and development environment
1 feat: establish application foundation and local infrastructure
2 feat: implement authentication and multi-tenant workspaces
3 feat: implement agent registry SDK and framework adapters
4 feat: implement isolated evaluation execution engine
5 feat: implement benchmark registry and evaluation orchestration
6 feat: implement RealityCheck accuracy validation
7 feat: implement agent security assessment engine
8 feat: integrate external agent evaluation benchmarks
9 feat: implement execution tracing and failure diagnostics
10 feat: implement agent comparisons and deployment quality gates
11 feat: complete accessible Preflight developer interface
12 feat: add reports observability and operational tooling
13 chore: harden and verify Preflight platform

Implementation units are preserved locally and staged after verification. Recovering separate historical phase commits would require reviewing/reconstructing logical units; do not fabricate a verified phase history or force-push.
