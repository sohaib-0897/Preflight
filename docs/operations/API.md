# API reference
Version prefix: /api/v1. Generated OpenAPI: /openapi.json; browser docs: /docs. Obtain an opaque cookie with auth/register or auth/login, obtain csrf_token from returned user/auth/me, and supply X-CSRF-Token on every authenticated write. API errors have detail and standardized error fields for HTTP/validation failures. Body budget is 64 KiB.

| Resource | Operations |
|---|---|
| /auth/register, /auth/login, /auth/me, /auth/logout | Register, sign in, session context, invalidate |
| /organizations, /organizations/{id}/members, /organizations/{id}/audit | Organization creation, membership, audit |
| /workspaces, /organizations/{id}/workspaces | Workspace list/create |
| /workspaces/{id}/projects | Project list/create; list supports offset/limit |
| /projects/{id}/agents, /agents/{id}/versions | Register native agents, append immutable versions |
| /projects/{id}/datasets | Immutable native scenario subsets |
| /benchmarks | Registry and explicit upstream availability |
| /projects/{id}/runs | Queue/list; status, offset and limit filters |
| /runs/{id}, /runs/{id}/cancel, /runs/{id}/execute | Evidence, cancel, bounded trusted demo execution |
| /runs/{id}/events | Finite SSE progress/transition snapshot; reconnect for new events |
| /runs/{id}/attempts/{attempt}/trace | Trace graph and diagnostics |
| /runs/{id}/replay/{attempt} | Deterministic tool replay |
| /runs/{id}/reviews, /runs/{id}/attempts/{attempt}/reviews | Review history/append |
| /comparisons | baseline/candidate run IDs |
| /trace-comparisons | baseline/candidate run and attempt IDs |
| /projects/{id}/policies, /runs/{id}/release | Immutable policy versions, release decision |
| /runs/{id}/report.json, /runs/{id}/report.html | Authorized redacted exports |
| /runs/{id}/artifacts, /artifacts/{id} | Snapshot creation/list, integrity-checked download |

Lists are intentionally bounded. Full list pagination/filter/sort support beyond projects/runs remains outstanding. Agent registry accepts only shipped native behaviors in worker dispatch. SDK bridge source is separately qualified; unsupported frameworks/suites return validation errors rather than fabricated successful runs.
