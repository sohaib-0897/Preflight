# API reference

Prefix /api/v1. Generated /openapi.json and /docs are authoritative for request schemas. Register/login returns an opaque HttpOnly session and csrf_token; supply X-CSRF-Token on authenticated writes. HTTP/validation errors use standardized detail/error fields. The request body budget is 64 KiB. Authorization is enforced in backend queries/services.

| Resource | Operations |
|---|---|
| /auth/register, /auth/login, /auth/me, /auth/logout | Account and session |
| /organizations, /organizations/{id}/members, /organizations/{id}/audit | Organizations, roles, audit |
| /workspaces, /organizations/{id}/workspaces | Workspaces |
| /workspaces/{id}/projects | Project creation/list with offset/limit |
| /workspaces/{id}/credentials, /credentials/{id}/revoke | Protected reference creation/list/revocation |
| /projects/{id}/agents, /agents/{id}/versions, /agents/{id}/health | Native/connected registration, immutable versions, real connection check |
| /projects/{id}/datasets, /benchmarks | Versioned native/custom scenarios and official readiness |
| /projects/{id}/sources, /projects/{id}/verify-claims | Versioned local factual evidence |
| /projects/{id}/runs | Queue/list with status/offset/limit |
| /runs/{id}, /runs/{id}/cancel, /runs/{id}/execute | Evidence, cancellation, native development execution |
| /runs/{id}/events | Finite SSE transition snapshot; reconnect for updates |
| /execution-readiness | Actual configured worker queue readiness |
| /runs/{id}/attempts/{attempt}/trace, /trace.json | Trace graph/export |
| /runs/{id}/replay/{attempt}, /trace-comparisons | Recorded native broker replay, structural comparisons |
| /runs/{id}/attempts/{attempt}/realitycheck, /assessments | Configured validation and preserved assessment history |
| /projects/{id}/review-queue, /review-assignments/{id}/decision | Assigned review workflow |
| /runs/{id}/attempts/{attempt}/assign-review, /reviews | Assignment, append audited review |
| /projects/{id}/security-scans, /runs/{id}/security | Controlled scans and evidence/coverage |
| /runs/{id}/dependency-scan | Opt-in exact-package OSV lookup |
| /comparisons | Compatible paired run comparison |
| /projects/{id}/policies, /runs/{id}/release | Versioned policies and decisions |
| /runs/{id}/report.json, /report.html, /report.pdf | Authorized redacted exports |
| /runs/{id}/artifacts, /artifacts/{id} | Integrity-checked snapshots |

Paths abbreviated as /assessments, /trace.json and /report.html share the prefix on their row. Lists are bounded; project/run pagination and run-status filters are provided. Other lists use fixed limits and frontend search explicitly applies to loaded records. Complete arbitrary-field server sorting/pagination is not implemented. Connected framework gateways execute through the worker, never through the native synchronous demo endpoint. Official readiness requires pinned environments; scripted official presets are separately qualified in UPSTREAM.md.
