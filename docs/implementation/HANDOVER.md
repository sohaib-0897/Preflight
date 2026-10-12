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

# Platform completion — phase 1

**Frontend foundation: COMPLETE AND VERIFIED locally for native workflows; remote CI pending this checkpoint.** Genuine Next.js App Router/React application now replaces the script wrapper. Locked dependencies include Tailwind, Radix Dialog, TanStack Query, React Hook Form, Zod, local open-source fonts and Vitest. Existing API/data contracts and FastAPI fallback are preserved. Module routes cover organizations/workspaces, projects, agents/versions, runs/evidence, benchmarks/datasets, reviews/security/traces, comparisons, policies, reports and settings. Non-native execution remains a later phase, not a frontend claim.

Evidence: production Next build passed; four Vitest tests passed; six sandboxed-Chrome desktop/mobile browser journeys passed (including all-module navigation, logout, real persisted native evaluation/export and axe checks). Screenshots reviewed at `test-results/journey-desktop.png` and `journey-mobile.png`; logs `.local/next-build.log` / `.local/next-browser.log` (ignored). Backend baseline remains independently verified by Docker-enabled CI; local Docker socket is inaccessible. No host groups, daemon permissions, existing service at port 8000 or user volumes were modified.

Development: run API with `PREFLIGHT_PORT=18000 bash scripts/dev.sh`, then `PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run dev -- --port 3000`. Production builds bake rewrite destination; set the origin when building. `npm ci --prefix apps/web`, `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npx playwright test -c playwright.next.config.ts` verify the new host. The test build uses API origin port 18000. Remote workflow now runs production Next build, Vitest and real browser journeys without disabling browser sandboxing.

Inventory: [INVENTORY.md](INVENTORY.md). Broader phases are pending; no official benchmark or external adapter execution is claimed yet. Earlier records below are historical.

# Handover

Local path: `/home/sohaib/Desktop/Preflight`.
Configured remote: https://github.com/sohaib-0897/Preflight.
Branch: `main`. Published initial commit: `6f6b043a617422a34bd3e74341eca2458943a8cc`.
Existing Git identity and GitHub authentication are available. Infrastructure/CI repairs are verified on GitHub Actions at `1ddd13d4b82d1105ebb05bf95f8c77dcf04bda57` ([successful run](https://github.com/sohaib-0897/Preflight/actions/runs/38175877115)); current verification is recorded in [VERIFICATION.md](VERIFICATION.md).

Docker client/Compose work, but this Codex process lacks permission on the root:docker daemon socket. The user reports a successful hello-world in an ordinary terminal. Local containers and existing volumes were not modified. GitHub Actions provides the permitted live verification environment.

The executable deliverable is a native agent evaluation platform with an actual FastAPI service, SQLAlchemy/SQLite persistence, 26 relational application tables, authentication/organizations/roles, an enforcing broker, eight offline scenarios, durable workers, immutable datasets/versions/policies, RealityCheck/security evidence, traces/replay/comparisons, reviews/gates and artifact/report exports. The compiled TypeScript interface uses those APIs. See phase-by-phase PROGRESS.md; all areas with missing verification are explicitly partial.

Verification this session: remote CI passed all 56 Python tests, including 14 live Docker checks, and frontend checks. Real Compose services, PostgreSQL migrations/drift, Redis health and durable-worker completion/persistence passed on the runner. Locally 42 backend tests pass and 14 Docker prerequisites fail due socket access; four desktop/mobile browser tests pass at an isolated port after test/accessibility repairs. Refer to VERIFICATION.md for evidence and limitations.

## Start locally
```bash
cd /home/sohaib/Desktop/Preflight
python3 scripts/demo.py --mode accurate --output .local/report.json
bash scripts/dev.sh # optionally PREFLIGHT_PORT=18000 to avoid occupied port 8000
# Separate ordinary terminal for queued jobs:
bash scripts/worker.sh
```
The standalone core works in this session. The browser test attempt encountered an existing service on port 8000; that service was preserved. Open localhost:8000, create a private account, then create project -> connect native agent -> queue evaluation -> execute native demo -> inspect trace/state -> compare -> release/export. No shared password or demo account exists.

Docker Compose source:
```bash
# Set POSTGRES_PASSWORD privately in your terminal first.
docker compose -f infra/compose/compose.yaml up --build
```
Compose uses trusted-demo execution. Its service/worker smoke verification is separate from restricted sandbox tests. Build the sandbox image and configure the host worker as described in docs/security/SANDBOX.md to test restricted native containers. Never mount the Docker socket into agents.

Optional variables: PREFLIGHT_PORT, DATABASE_URL, REDIS_URL, PREFLIGHT_COOKIE_SECURE, PREFLIGHT_SANDBOX_IMAGE, PREFLIGHT_ARTIFACT_ROOT, PREFLIGHT_API_ORIGIN; Compose requires POSTGRES_PASSWORD, monitoring requires GRAFANA_PASSWORD. No hosted API key is required or configured.

## Remaining engineering priorities
1. Restore Docker access to the Codex session through normal operator procedures if local verification is desired. Do not change socket permissions to bypass controls.
2. Complete and lock the requested Next/React/query/forms/components/Tailwind/Vitest stack, then run visual, keyboard, responsive and axe reviews using sandboxed Chrome.
3. Migrate sync persistence to SQLAlchemy async and verify Redis/ARQ behavior, cancellation races, quotas and concurrent database workloads.
4. Install each upstream benchmark in isolated pinned Python environments, execute genuine authorized offline official scenarios, and preserve independent coverage qualifications. Integrate framework/HTTP/local-model execution and credential references safely.
5. Implement generalized custom task authoring/prose evidence retrieval, concrete S3/MinIO storage, OTel exporter instrumentation and optional reliable PDF exports; complete network-enabled dependency audits and load tests.
6. Configure required GitHub branch-protection checks manually after remote CI passes. Required historical phase messages remain in PROGRESS.md; no historical commits were fabricated.

Known limits: demo workloads only; no arbitrary code or microVM sandbox; no semantic judge; no hidden reasoning; cost/tokens unavailable; lists other than project/run lists are bounded without comprehensive pagination. Source and tests are not production security certification.

Repository hygiene: 101 tracked source paths passed the limited source-pattern and artifact-size check; staged whitespace check passed. Dependency/runtime/generated assets are ignored. This does not replace an exhaustive secret scan or a network-enabled vulnerability audit.
