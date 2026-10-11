# Implementation inventory — 2026-10-12

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
