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

## Phase 2 remote confirmation

Commit `45068452c06a8e2061fe0ab6dbb2a6e581ac9d0b`: [Actions 38178902913](https://github.com/sohaib-0897/Preflight/actions/runs/38178902913) SUCCESS. 61 Python tests including 14 live Docker checks; Compose PostgreSQL/Redis health, additive migration without drift and durable worker; six Chromium checks; four React unit checks; three actual framework jobs, eight scenarios each. No hosted inference called.

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

# Docker/CI verification — 2026-10-12

- Docker client 29.9.0 and Compose 5.6.0 are installed. This Codex process cannot access `/var/run/docker.sock` (root:docker, mode 0660; process lacks docker group). User reports ordinary-terminal hello-world succeeded. Host permissions were not modified.
- Root-context sandbox build attempted and blocked by daemon permission. Compose configuration validates with a disposable validation-only password; existing local services/volumes were not started or modified.
- Local TypeScript typecheck/build, two frontend utility assertions, pip consistency and compileall passed. Accurate CLI PASS/exit 0 and regressed CLI FAIL/exit 1. Browser test startup blocked by an existing service on port 8000, preserved without modification.
- Full local Pytest: **42 passed, 14 prerequisite errors**, all errors from live Docker tests. These are failures of access, not passing isolation evidence. Memory/timeout tests now require successful daemon and image checks, preventing startup failures from masquerading as containment.
- Original published GitHub run [38174859491](https://github.com/sohaib-0897/Preflight/actions/runs/38174859491): five failures because sandbox image was never built. Workflow repaired to build from repository root before the full test suite, then exercise a fresh Compose project.
- Added real Compose smoke verification: PostgreSQL/Redis/API health, Alembic head/drift, queued durable-worker execution, traces, 16 attempts, persisted results after worker restart. Uses a unique project and ephemeral generated credentials; never removes volumes. First repaired remote run [38175700997](https://github.com/sohaib-0897/Preflight/actions/runs/38175700997) verified the sandbox build and all **56 Python tests (14 live Docker)** plus frontend checks. Its Compose test found a healthy API unreachable through host-published ports on the internal-only network. Added a trusted API ingress bridge; worker/data services remain internal and sandbox networking remains disabled. Retest [38175877115](https://github.com/sohaib-0897/Preflight/actions/runs/38175877115) **PASSED** at commit `1ddd13d4b82d1105ebb05bf95f8c77dcf04bda57`: both native and frontend jobs succeeded.


## Verified infrastructure evidence

| Check | Observed result |
|---|---|
| Sandbox root-context build | Passed on GitHub runner; image `preflight-sandbox:0.1.0`, ID `sha256:a443395079e219915606774d275114b61210884bc68098a3e70f0c40fab1ab3c` |
| Full Python suite on Python 3.12.15 | **56 passed, no skips**, including all 14 live Docker tests |
| Live isolation tests | Eight actual native scenarios, non-root/read-only/network denial, memory/PID/capability/file limits, OOM exit 137, tmpfs ENOSPC, deadline cleanup, concurrent execution/cleanup |
| Compose | Fresh isolated project built and started; PostgreSQL, Redis and API healthy |
| Database | API SELECT 1 succeeds; Alembic `d701ca032ccb (head)` and `No new upgrade operations detected` |
| Redis | Real `redis-cli ping` returned PONG; ARQ dispatch is not exercised (durable database worker used) |
| Durable worker | Queued run completed without calling synchronous execute endpoint; 16 attempts, full transitions and traces, 100% fixture task success |
| Persistence | Completed run summary unchanged after worker restart; volumes preserved, no `down --volumes` |
| Frontend | GitHub npm clean install, strict typecheck/build and two utility assertions passed |
| Release gate | Accurate CLI exit 0/PASS; regressed CLI exit 1/FAIL |
| Local browser suite | Four tests passed on desktop/mobile with real sandboxed Chrome at port 18000: account/project/agent/evaluation, RealityCheck, release policy, JSON export, keyboard checks and axe WCAG checks on result page |

Browser verification uncovered and fixed a CSP-incompatible axe injection method and keyboard-inaccessible scrollable evidence blocks. The app CSP remains unchanged. These representative browser checks are not an exhaustive WCAG certification. Port selection is now configurable without taking over an existing service:

```bash
PREFLIGHT_PORT=18000 DATABASE_URL=sqlite:///.local/browser-infrastructure.sqlite npm run test:e2e
```

Remote Docker evidence applies to the GitHub runner, not the inaccessible local daemon. Docker remains a restricted native-demo boundary, not protection sufficient for arbitrary hostile code. No production deployment, paid model invocation or official benchmark execution is claimed. Local logs/screenshots/traces remain ignored in `.local/` and `test-results/`.

The historical matrix below records the earlier environment only; its Docker, Git and publishing blockers have changed as described above. Broader product limitations remain unchanged.

# Historical verification matrix (2026-10-10)
Verified on 2026-10-10 using Ubuntu 26.04.1, Python 3.14.4, Node 22.22.1. No paid model APIs, large models/datasets, cloud resources, third-party adversarial scans or host security changes were used.

| Check | Observed result |
|---|---|
| `bash scripts/check.sh` | Exit 0; output saved to ignored .local/final-check.log |
| Pytest | **42 passed, 6 skipped**, 6.87 seconds in final run |
| Six live Docker checks | SKIPPED because Docker executable is absent; not isolation evidence |
| Root `npm ci --offline` | Passed against real cached tarballs and generated registry-URL integrity lock |
| `npm run typecheck` | Passed with strict TypeScript checking |
| `npm run build:offline` | Passed; generated apps/web/public/app.js |
| `npm run test:web` | Frontend escape/missing-metric utility assertions passed; Node reports one test file passed |
| SQLite Alembic | Upgrade, drift check, downgrade to base and re-upgrade passed; 26 app tables plus revision table |
| Native accurate CLI | Eight scenarios, 100% fixture task success; policy PASS; exit 0 |
| Native regressed CLI | Eight scenarios, 50% fixture task success; policy FAIL; exit 1 as required |
| Scenario latency | Real elapsed durations measured. Slow native mode >=20ms and more broker calls verified |
| Tokens and cost | Null/unavailable; no model calls or fabricated pricing values |
| Runtime dependency consistency | `pip check`: No broken requirements found |
| Python static syntax | compileall passed; AST parsed 24 source files |
| Ruff/Mypy/Vitest | Unavailable offline; not run. Syntax/TypeScript checks are not substitutes for all these tools |
| `scripts/dev.sh` | App startup succeeds; localhost:8000 bind denied, exits 3 |
| `npm run test:e2e` | BLOCKED: configured webServer cannot bind localhost:8000 |
| Sandboxed Chrome probe | BLOCKED: setsockopt Operation not permitted, browser exits SIGTRAP |
| Visual/keyboard/axe/WCAG review | Not completed; supplied browser tests were not able to execute |
| Next install/build | Offline install ENOTCACHED; build and Next dependency lock unavailable |
| Docker/Compose/PostgreSQL/Redis/ARQ | Not available/executed; configuration/bridge source only |
| τ³/AgentDojo | Upstream API/license review and authored normalization fixtures pass; zero official suites executed |
| Framework bridges | Offline contract objects pass; actual frameworks/provider execution untested |
| `pip-audit` | Tool installed from cache; scan FAILED due DNS resolution for pypi.org. Vulnerability status unknown |
| Git phase commit | Rejected because no configured author identity; no commit SHA exists |
| GitHub publishing | Stored CLI token invalid; no pushes, visibility changes or remote CI claimed |

## Backend security evidence
Passing tests exercise different organizations, inaccessible foreign workspaces/runs/artifacts, viewer write denial, CSRF denial, expired sessions, login throttling, HttpOnly/SameSite cookies, strict broker arguments, unauthorized tool denial, idempotent refund side effects, call budget enforcement, synthetic canary detection/redaction, SSRF URL rejection, request body budget, artifact tamper detection, review audit and policy overrides. These tests do not establish resistance to arbitrary hostile containers, production scale, DNS rebinding or unknown vulnerabilities.

## Local demonstration acceptance
| Criterion | Status |
|---|---|
| 1 Sign in | ASGI verified; browser unverified |
| 2 Workspace/project creation | ASGI verified |
| 3 Agent registration | Native verified; nonnative worker dispatch incomplete |
| 4 Native suite selection | Verified |
| 5 Restricted environment startup | **Blocked: Docker unavailable** |
| 6 Evaluation completion | Trusted native backend verified |
| 7 Tool/event inspection | API/event artifacts verified; visual review blocked |
| 8 Ground truth/state validation | Verified against actual SQLite fixtures |
| 9 Basic security tests | Native broker/canary tests verified |
| 10 Persistent results | Real database verified |
| 11 Version comparison | Identical native sets and regression verified |
| 12 Correct release decisions | PASS/FAIL/INCONCLUSIVE verified |
| 13 Report export | JSON/HTML and integrity-checked snapshots verified |
| 14 Workspace authorization | Organization boundary and roles verified |
| 15 Navigable/accessible UI | Source/typecheck verified; browser/a11y acceptance **not complete** |
| 16 No paid API | Standalone native demo verified; browser demo blocked |
| 17 CI tests | Same local commands verified; remote Actions untested |
| 18 Setup instructions | Provided with observed environment blockers |

**Complete local-demo acceptance and production readiness are not achieved.** Official benchmarks have separate unverified status. Detailed phase progress and incomplete scope are in PROGRESS.md/BLOCKERS.md.

Ignored local evidence: final-check.log, native/regression JSON reports, dependency-audit.log, Playwright failure output. Generated benchmark reports are not public benchmark scores and are excluded from Git. Source-level hygiene checking is recorded in HANDOVER.md; it is a limited pattern check, not an exhaustive secret audit.

Final repository checks: `git diff --cached --check` passed. `scripts/hygiene.py` passed for 101 tracked source paths; no tracked .local/.venv/node_modules/wheels/databases/private-key markers or probable token prefixes were found by this limited check. Generated artifacts and local logs are ignored. Source remains staged and uncommitted because the author identity blocker persists.
