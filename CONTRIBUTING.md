# Contributing
Use Python 3.12 and Node 22. Create a virtual environment, install `requirements.lock`, and run `bash scripts/check.sh`. Keep runtime packages in the monorepo boundaries and publish reusable SDK packages separately. Tests use a real SQLite database and ASGI transport; no network sockets are required for backend integration coverage.

Add native scenarios with evidence validators, failure cases and replay tests. Preserve benchmark/configuration versions. Never convert infrastructure errors into failed agent tasks without an explicit policy. Require organization authorization before accessing projects, runs, reviews or artifacts.

Frontend source is `apps/web/src/app.ts`; regenerate its checked-in browser module with `npm run build:offline`. The Next host remains unverified until dependencies can be installed. Run `npm run test:e2e` on a machine that permits local sockets and a sandboxed Chrome launch. Do not disable OS security controls to make tests pass.

No fabricated benchmark results, synthetic usage presented as measured usage, secrets, generated datasets or model binaries in commits. Record exact verification and limitations in docs/implementation. Configure your own Git identity; do not invent contributor identities.
