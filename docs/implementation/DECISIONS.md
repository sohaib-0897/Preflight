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
