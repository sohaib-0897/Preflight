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
