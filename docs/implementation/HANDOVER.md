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
