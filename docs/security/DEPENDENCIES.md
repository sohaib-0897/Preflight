# Dependency audit — 2026-10-12

Executed pip-audit 2.10.1 against the exact core requirements and all five installed
isolated framework/benchmark environments, plus npm audit against both lockfiles.
These are advisory-database checks, not source review, exploit testing or proof of
security. Generated JSON evidence is ignored under .local/final-*-audit.json.

| Environment | Observed result |
|---|---|
| Core Python requirements | No known advisories returned |
| Root npm and Next npm locks | No known advisories returned |
| LangGraph (44 packages) | No known advisories returned |
| OpenAI Agents SDK (42 packages) | No known advisories returned |
| AgentDojo (71 packages) | No known advisories returned |
| CrewAI (138 packages) | ChromaDB 1.5.9 advisories; no fix version supplied |
| τ³ runtime (76 packages) | LiteLLM 1.82.6 advisories; upstream tau2 itself not available on PyPI for audit |

Advisory aliases can produce duplicate records: the generated reports preserve the
raw response. ChromaDB includes code-injection/authorization advisories such as
[GHSA-36p7-vc44-83pf](https://github.com/advisories/GHSA-36p7-vc44-83pf).
LiteLLM includes the upstream
[authentication advisory](https://github.com/BerriAI/litellm/security/advisories/GHSA-69x8-hrgq-fjj8)
and additional proxy advisories. Core application images do not install either
optional package. Offline CrewAI examples disable memory and do not start ChromaDB.
τ³ reference presets do not start LiteLLM Proxy or invoke provider APIs; official
smoke tests reject outbound connections during evaluation. This limits the tested
exposure, but does not remove package vulnerabilities.

The pinned official tau2 v1.0.1 and current upstream main both require
`litellm>=1.80.15,<1.82.7`. Patched versions in the audit exceed that bound. A
supported compatible security upgrade is therefore BLOCKED by upstream dependency
constraints. No dependency metadata was edited, advisory ignored or unsupported
upgrade presented as verified. Keep optional environments private/offline; do not
expose their proxy/database services. Upstream remediation and a fresh compatibility
run are required before extending those environments to production services.

No full OCI/OS-package vulnerability scan, SBOM attestation or supply-chain guarantee
is claimed. Review and repeat audits when changing dependencies; advisory data is
time-sensitive. Native evaluation needs none of these optional packages.
