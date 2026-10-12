# Verification record — current platform

# Platform phase 11 — final verification checkpoint

Completed repository-wide Python formatting/lint without disabling checks, targeted
Mypy for SDK/adapters/metrics/security/telemetry, installed SDK wheel verification,
actual framework/official smoke reruns, full available backend/browser checks,
Redis queue verification and dependency audits. CI now enforces static checks,
wheel invocation, all live Docker tests and every PR release gate. Main pushes and
PRs remain verified; duplicate branch-push runs are avoided. Sandbox Python patch
is 3.12.15; image references resolve once to an immutable inspected OCI ID, recorded
in results and asserted by the live tests. No isolation restriction was removed.

Local: 76 Python tests excluding the daemon-inaccessible suite; all ten desktop/mobile
Chromium journeys, four Vitest tests, legacy frontend checks, production Next build,
pip check, Ruff and targeted Mypy pass. Actual installed wheel gateway passes;
three frameworks each invoke eight scenarios; official pass/fail and AgentDojo
injection cases execute upstream scoring without outbound connections. Actual
private Redis 8.0.5 queue persists 32 attempts, rejects duplicate enqueue and
honors cancellation. Fifteen local Docker checks return prerequisite errors for
permission denied, not skips/passes. Compose configuration validates.

Dependency audits: core Python and both npm locks have no returned known advisories;
LangGraph/OpenAI Agents/AgentDojo isolated environments likewise. CrewAI ChromaDB
and tau2's constrained LiteLLM have unresolved advisory findings; see
security/DEPENDENCIES.md. These optional findings are not hidden by green CI.
Full async service conversion, general model/official-suite execution, stronger
arbitrary-code isolation and optional external storage/judging remain incomplete.

Latest fully verified remote checkpoint:
2ca10e708057f827d4e47752b582be3e12307838,
https://github.com/sohaib-0897/Preflight/actions/runs/38215112138 SUCCESS, all seven jobs:
89 Python including 15 live Docker, ten Next Chromium and two Compose Chromium
journeys, actual PostgreSQL migrations/persistence, Redis/native Docker queues,
three framework and both official integrations. Phase 11 remote verification now passed: 07c68dc63fa647f8ef438cbdf79ef8bd4e4e0ef5,
https://github.com/sohaib-0897/Preflight/actions/runs/38216348545, all seven jobs SUCCESS. Actual results: 91 Python tests including fifteen live Docker checks with immutable image identity; ten Next and two Compose Chromium journeys; SDK wheel/static checks, PostgreSQL migrations, Redis/native Docker execution and both official smoke integrations. Logs/artifacts are .local/final-ci.log and .local/final-ci-artifacts. Local Docker access remains denied.

## Executed checks and evidence

| Check | Observed status | Evidence |
|---|---|---|
| Backend/tenant/auth/worker/scoring/report unit and integration | 76 passed locally | .local/final-pytest.log |
| Live Docker isolation | BLOCKED locally; 15 passed at remote phase 11 | .local/final-local-docker-tests.log; Actions 38216348545 |
| Immutable OCI identity | Unit contract passed; actual live assertions passed in phase 11 CI | tests/security/test_image_identity.py; test_docker_live.py |
| Production Next build and strict TS | Passed | .local/final-next-build.log |
| Next desktop/mobile browser + axe/keyboard | 10 passed | .local/final-browser.log; test-results/* screenshots |
| React component tests | 4 passed | .local/final-vitest.log |
| Compose browser/PG/Redis/worker | 2 journeys passed remotely at phase 11 | Actions 38216348545, native-evidence |
| Real isolated Redis/ARQ | 32 persisted attempts; cancellation/duplicate routing passed | .local/final-queue.log |
| SDK wheel installation/invocation | Passed in fresh wheel-install environment | .local/final-sdk-build.log; scripts/verify_sdk.py |
| LangGraph/CrewAI/OpenAI Agents | 8 actual invocations per installed framework | .local/final-framework-smoke.log |
| Official tau2/AgentDojo | Authentic documented pass/fail subset + banking injection | .local/final-official-smoke.log; *-official-smoke.json |
| Release positive/negative | PASS exit 0, FAIL exit 1 | .local/final-native-report.json; final-regressed-report.json |
| Actual PR release rejection | Verified FAIL in closed/unmerged PR #1 | Actions 38212112251 |
| Ruff all Python source/tests/examples | Passed; no disabled rules | CI command and local terminal |
| Mypy SDK/adapters/metrics/security/telemetry | Passed, six files | .local/final-mypy-inventory.log |
| Core dependency compatibility | pip check passed | Local and CI |
| Dependency advisories | Core/npm clean; two optional environments have findings | security/DEPENDENCIES.md; .local/final-*-audit.json |
| Limited source hygiene | Passed | scripts/hygiene.py; not exhaustive secret detection |

Screenshots/PDF were rendered and reviewed; automated axe checks cover representative
flows and do not certify full WCAG conformance. Native synthetic fixtures are not
model-quality measurements. Benchmark normalization tests are separate from the
actual official runtime/scoring scripts. Remote CI performs all Docker checks; local
daemon prerequisite errors are an environmental limitation. No production security
certification, full official suite, hosted inference or cloud deployment is claimed.

See PROGRESS.md for milestone history and HANDOVER.md for supported scope/setup.
