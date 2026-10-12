# Contributing

Use Python 3.12 and Node 22. Install the committed requirements/npm locks in isolated environments. The maintained UI is Next App Router in apps/web/app and apps/web/components; apps/web/src is the compatibility interface. Preserve API contracts, migrations and stored schemas.

Run `bash scripts/check.sh`, `npm --prefix apps/web test`, the production Next build and Playwright with playwright.next.config.ts. Complete checks include actual TCP/TLS gateways, sandboxed Chromium and live Docker: do not disable security controls or mandatory tests to obtain a pass. Without daemon access, record that restriction and inspect the actual remote CI results.

Add scenarios with evidence validators, negative outcomes, version provenance and meaningful tests. Do not score infrastructure failures as agent failures. Enforce tenant authorization in backend services and artifact access. Unknown evidence stays unknown; repeated deterministic trials do not increase independent sample size.

Framework and official benchmark dependencies are isolated in requirements/agents and requirements/benchmarks. Run their actual smoke scripts; normalization fixtures alone are insufficient. Never invoke billable APIs automatically. Do not commit secrets, model binaries, downloaded wheels, generated datasets or artifacts. Record exact verification and limitations in docs/implementation. Use your configured Git identity.
