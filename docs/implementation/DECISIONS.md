# Implementation decisions

- Preserve the modular monolith, original migration/history and API interfaces.
  Additive credential/source/review migrations coexist with stored native evidence.
- Next App Router is the maintained UI; FastAPI-served TypeScript remains a fallback.
  Data queries are tenant-scoped and all buttons invoke actual operations. Search
  states its loaded-record scope; unknown metrics are not fabricated.
- Durable relational jobs are the source of truth; Redis/ARQ coordinates separate
  native/Docker queues. Connected ambiguous side effects block unsafe blind retries.
- The safe Compose stack has no Docker socket mount. An independently controlled
  host worker executes prebuilt native images with retained restrictions, resolves
  immutable image identity and records actual OCI evidence. Public arbitrary-code
  execution is refused pending stronger isolation.
- Framework dependencies have isolated hash locks because CrewAI and OpenAI Agents
  require incompatible provider SDK versions. Actual offline framework execution is
  distinct from hosted inference. Protected credentials remain outside agent images.
- Official upstream scorers execute unchanged against small authentic scripted cases.
  Versions/scenario IDs/evidence are preserved. Normalization fixtures never establish
  official coverage. Unsupported full suites/model integrations remain explicit.
- Deterministic task/state/tool/fact verification takes precedence over response
  wording. Missing evidence is unknown; reviews preserve original assessments.
  Critical security findings survive human accuracy overrides.
- Paired comparisons require compatible configurations and count distinct scenarios;
  deterministic repeats are not independent samples. Missing mandatory coverage or
  usage makes release inconclusive; verified policy violations fail.
- OpenTelemetry records accessible metadata only. PDF is an offline bounded overview;
  JSON/HTML retain complete evidence. Unicode escapes avoid missing PDF glyphs.
- Advisory scans are separate from correctness CI. Known optional upstream findings
  are disclosed; unsupported dependency overrides are not presented as fixes.

See architecture documents and PROGRESS.md for the detailed milestone history.
