# Docker/CI verification — 2026-10-12

- Docker client 29.9.0 and Compose 5.6.0 are installed. This Codex process cannot access `/var/run/docker.sock` (root:docker, mode 0660; process lacks docker group). User reports ordinary-terminal hello-world succeeded. Host permissions were not modified.
- Root-context sandbox build attempted and blocked by daemon permission. Compose configuration validates with a disposable validation-only password; existing local services/volumes were not started or modified.
- Full local Pytest: **42 passed, 14 prerequisite errors**, all errors from live Docker tests. These are failures of access, not passing isolation evidence. Memory/timeout tests now require successful daemon and image checks, preventing startup failures from masquerading as containment.
- Original published GitHub run [38174859491](https://github.com/sohaib-0897/Preflight/actions/runs/38174859491): five failures because sandbox image was never built. Workflow repaired to build from repository root before the full test suite, then exercise a fresh Compose project.
- Added real Compose smoke verification: PostgreSQL/Redis/API health, Alembic head/drift, queued durable-worker execution, traces, 16 attempts, persisted results after worker restart. Uses a unique project and ephemeral generated credentials; never removes volumes. Remote execution pending.

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
