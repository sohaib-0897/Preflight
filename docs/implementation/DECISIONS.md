## Isolated framework environments

CrewAI and OpenAI Agents SDK have incompatible OpenAI package requirements. Separate hash-locked Python 3.12 environments preserve maintained versions and real runtime tests. Credential keys persist outside images; arbitrary code stays in operator-owned gateways.

# Platform completion — phase 1

**Frontend foundation: COMPLETE AND VERIFIED locally for native workflows; remote CI pending this checkpoint.** Genuine Next.js App Router/React application now replaces the script wrapper. Locked dependencies include Tailwind, Radix Dialog, TanStack Query, React Hook Form, Zod, local open-source fonts and Vitest. Existing API/data contracts and FastAPI fallback are preserved. Module routes cover organizations/workspaces, projects, agents/versions, runs/evidence, benchmarks/datasets, reviews/security/traces, comparisons, policies, reports and settings. Non-native execution remains a later phase, not a frontend claim.

Evidence: production Next build passed; four Vitest tests passed; six sandboxed-Chrome desktop/mobile browser journeys passed (including all-module navigation, logout, real persisted native evaluation/export and axe checks). Screenshots reviewed at `test-results/journey-desktop.png` and `journey-mobile.png`; logs `.local/next-build.log` / `.local/next-browser.log` (ignored). Backend baseline remains independently verified by Docker-enabled CI; local Docker socket is inaccessible. No host groups, daemon permissions, existing service at port 8000 or user volumes were modified.

Development: run API with `PREFLIGHT_PORT=18000 bash scripts/dev.sh`, then `PREFLIGHT_API_ORIGIN=http://127.0.0.1:18000 npm --prefix apps/web run dev -- --port 3000`. Production builds bake rewrite destination; set the origin when building. `npm ci --prefix apps/web`, `npm --prefix apps/web run build`, `npm --prefix apps/web test`, `npx playwright test -c playwright.next.config.ts` verify the new host. The test build uses API origin port 18000. Remote workflow now runs production Next build, Vitest and real browser journeys without disabling browser sandboxing.

Inventory: [INVENTORY.md](INVENTORY.md). Broader phases are pending; no official benchmark or external adapter execution is claimed yet. Earlier records below are historical.

# Decisions
2026-10-10: Modular monolith with separate worker, pure Python evaluation packages, FastAPI transport, SQLAlchemy persistence. Docker Compose targets Python 3.12; this host has 3.14. Native scenarios are deterministic and require no model credentials.

The restricted environment prohibits network sockets and lacks Docker. Use cached packages where available. SQLite is the executable local fallback; PostgreSQL is the deployment database. Trusted built-in demo execution is explicitly labeled and must never execute user code. Docker execution fails closed when unavailable. External adapters remain separately qualified.

Git identity must come from existing configuration. None is configured; do not invent an author to satisfy a phase commit.

- SQLAlchemy synchronous services were used for the executable offline fallback; async drivers/greenlet are not cached. FastAPI async transport endpoints avoid TestClient's prohibited cross-thread socket wakeups in this host. Production async persistence remains outstanding; sync work currently blocks each API process's event loop.
- Database polling is the executable durable queue; optional ARQ/Redis integration source is provided but not installed/verified. Redis enqueue failure retains the database job.
- Next.js 16.4.0 and React 19.3.0 metadata were verified through official npm registry; dependencies cannot be installed offline. Root TypeScript/Playwright/axe tools were installed from existing cached tarballs. The generated lock was normalized to the original registry tarball URLs with real cached integrity hashes; `npm ci --offline` subsequently passed.
- Browser launch retains Chromium sandboxing; denied socket operations were not bypassed. E2E startup also fails to bind localhost. No visual review or accessibility score is claimed.
- Human overrides affect release task scoring only when the immutable policy explicitly enables them. Critical findings and automatic evidence remain intact.
- Statistical inference clusters deterministic repetitions by scenario. Small native fixture runs are smoke evidence, not production accuracy estimates.
