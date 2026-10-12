# Current implementation inventory — phases 1–6

Phase 5 latest verified remote commit: bcee0a0, Actions 38181172885 SUCCESS.
Phase 6 local verified work awaits its own remote confirmation.

| Capability | Current evidence/status | Remaining scope |
|---|---|---|
| Next.js frontend | COMPLETE AND VERIFIED for 15 module navigation and native core workflow | Rich trace graph, integrated Compose, broader onboarding and QA |
| HTTP/Python/framework agents | COMPLETE AND VERIFIED for documented gateways and real installed offline framework examples | Hosted/Ollama invocation untested; framework dependency environments isolated |
| Native Docker isolation | COMPLETE AND VERIFIED remotely, 15 live checks | Local socket BLOCKED; arbitrary public code refused; no microVM implementation |
| PostgreSQL/Redis/ARQ | COMPLETE AND VERIFIED remotely, migrations, real concurrent queues, recovery | Full-stack Next Compose deployment pending phase 9 |
| Official τ³/tau2 | OFFICIAL SMOKE EXECUTED with actual upstream ENV scorer | Full suite and general connected-agent protocol unsupported |
| Official AgentDojo | OFFICIAL SMOKE EXECUTED; controlled banking injection locally verified in phase 6 | Remote attack verification pending; other tasks/LLM attacks unsupported |
| RealityCheck | COMPLETE AND VERIFIED for immutable facts, custom structured/state/SQL/tool assertions and assigned reviews | General prose semantics, LLM judges and external SQL remain partial |
| Controlled security workflows | Locally verified, remote CI pending | Broader attack generation and full dependency audit remain incomplete |
| Tracing/replay/comparisons/gates | Existing native evidence paths verified | OTel correlation, expanded metrics and richer interaction pending phases 7–8 |
| Reports/onboarding/operations | JSON/HTML, local artifacts and basic guides verified | Complete identity/provenance reports, optional PDF/S3 and final deployment guides pending |
| Async database | Async readiness/dispatch verified; bounded threaded sync services preserved | Full async service conversion PARTIALLY IMPLEMENTED |
| Comprehensive QA | Existing tests green through phase 5; expanded local phase 6 passing | Full-stack browser and final dependency/static/performance audit pending phase 11 |

Historical baseline inventory follows; its missing-feature rows describe the starting
commit and are superseded by the current table and milestone verification records.

# Initial implementation inventory — 2026-10-12

Baseline: main `08f96d55ea864af30198dc67965afe23ad22ec43`; remote Actions run 38176142524 succeeded. Inventory reviewed against source and tests, not the stale original environment notes.

| Capability | Evidence/status | Work required |
|---|---|---|
| Native scenarios and scoring | COMPLETE AND VERIFIED: eight fixtures, actual broker/database checks | Preserve; extend scenario authoring |
| Tenant auth/session/roles | COMPLETE AND VERIFIED for existing endpoints | Expose organization/member workflows in React |
| Docker native boundary | COMPLETE AND VERIFIED on CI: 14 live checks | Local socket permission still BLOCKED; arbitrary code refused |
| PostgreSQL migrations / Compose | COMPLETE AND VERIFIED on CI | Integrate Next service and Redis execution |
| Durable database worker | COMPLETE AND VERIFIED | Redis scheduling, crash recovery, cancellation |
| Traces/replay/comparisons/gates/exports | COMPLETE AND VERIFIED for native evidence | Rich UI, generalized agent metadata, observability |
| Next.js frontend | PARTIALLY IMPLEMENTED: wrapper around legacy script | Build genuine React App Router workflows |
| HTTP/framework adapters | PARTIALLY IMPLEMENTED: library bridges and doubles | Actual package execution, protected connections, worker dispatch |
| Python SDK | PARTIALLY IMPLEMENTED: source client | Installable distribution and examples |
| Official benchmarks | IMPLEMENTED BUT UNVERIFIED: normalization bridges only | Official isolated smoke executions and integration |
| General RealityCheck | PARTIALLY IMPLEMENTED: fixed corpus and native state | Project evidence corpus, custom assertions, review queue |
| Redis/ARQ | IMPLEMENTED BUT UNVERIFIED | Install, integrate and verify actual jobs |
| Async SQLAlchemy | NOT IMPLEMENTED | Preserve schema while introducing async-safe service execution |
| OTel / S3 / PDF | PARTIALLY IMPLEMENTED protocols or NOT IMPLEMENTED | Real optional backends with independently stated verification |
| Providers / Ollama | NOT IMPLEMENTED in worker | Explicit local/hosted connections; never silently substitute |

Unrelated untracked files `e HEAD` and `h -u origin main` are user-owned and preserved. No existing data or volumes are deleted. No paid model calls are authorized. Current Codex process still cannot access the Docker daemon; remote CI is the live-container verification path.
