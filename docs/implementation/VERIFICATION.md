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
