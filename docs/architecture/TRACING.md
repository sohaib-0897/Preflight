# Traces and failure diagnostics

Preflight uses the pinned OpenTelemetry Python SDK 1.45.1. HTTP request spans
propagate W3C traceparent to scheduled run configuration. Worker execution creates
an evaluation.run child span; each persisted attempt has a recording span whose
trace/span identity is attached to the recorded events. The scheduler preserves
idempotency by excluding internal trace context from configuration equality.
Recording spans measure event collection, not historical tool/model execution.
Real tool durations remain on captured events. Use a separate trace file per OS
process when running multiple API/worker processes; rotation is thread-safe within
a process. Native/Docker and official upstream
events are distinguished from connected agent-reported events.

Structured request logs contain correlation IDs, method, status and measured duration.
They do not log request/response bodies, cookies, authorization headers or raw exception
text. Setting PREFLIGHT_TRACE_FILE enables an actual local rotating JSON span exporter
(2 MiB with two backups) that allowlists metadata attributes. No exporter or external
telemetry service is contacted by default. OTLP collector integration remains optional
future work; do not claim it was deployed. Instrumentation follows the
[official OpenTelemetry SDK API](https://opentelemetry.io/docs/languages/python/instrumentation/).

The trace explorer presents the recorded parent graph as keyboard-operable nodes,
parent/child navigation, event-type filtering, expandable payloads, observed tool
latencies and deterministic analysis. Compare recorded trajectories from two runs
in the same project; timing and correlation identifiers are excluded from structural
diffs. Individual redacted trace JSON downloads enforce the same run/attempt ownership
as report access. The graph is a graph of accessible events, not hidden reasoning.

Diagnostics inspect enforcing-broker and upstream evidence for timeouts, invalid
parameters, unauthorized operations, exhausted budgets, missing actions, hallucinated
completion and synthetic disclosure. Captured assessments retain their original
verified categories. Repeated identical calls produce a suspected-loop hypothesis,
not a claimed infinite-loop diagnosis. Agent-reported denials alone are not verified
broker evidence. No LLM root-cause explanations are generated without a configured
and validated provider; that optional enhancement remains unimplemented.

Recorded broker replay reruns supported captured tool interactions against a fresh
fixture, excluding unverified agent-reported intentions. Official upstream tool
replay is explicitly refused by this native broker. It does not rerun a stochastic model or guarantee identical remote side effects.

Global `/metrics` requires PREFLIGHT_METRICS_TOKEN and a matching bearer header. The
monitoring overlay mounts its matching token for Prometheus. Keep both on a private
network. Compose syntax is verified; the optional monitoring service runtime is not.

Verification: real SDK in-memory and rotating-file exporters; request→worker→attempt
parent span identity; sanitized attributes; trace export tenant denial; unchanged
idempotent scheduling; desktop/mobile browser parent navigation, structural comparison,
trace download, keyboard activation and axe WCAG checks. See implementation/VERIFICATION.md
for the executed milestone counts and remote run.
