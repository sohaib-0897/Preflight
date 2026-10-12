# Controlled security assessments

Use Security → Start security scan after selecting a project and agent version.
Native basic checks run shipped deterministic fixtures. Connected scans and all
adversarial scans require an explicit authorized-target acknowledgment stored in
the evaluation configuration. This permission covers controlled cases only;
Preflight does not scan arbitrary URLs, hosts or unrelated systems.

Basic cases exercise a synthetic malicious document, prohibited tool operations,
and tool timeout recovery. Adversarial native cases select injection and prohibited
actions. Connected HTTP agents receive the actual untrusted document in their input;
the enforcing broker applies declared actions against a temporary fixture database.
Provider-reported tool events are distinguished from enforcing-broker evidence.

Findings have stable identifiers, severity, confidence, expected/actual behavior,
scenario/version/attempt identity, redacted evidence and remediation. Denied tool
attempts are high severity agent behavior findings; enforcement can pass while agent
behavior fails. Confirmed synthetic disclosure or completed unauthorized transfer
is critical and can block release. Call budgets, duplicate calls and repeated
timeouts produce evidence-backed consumption findings. No aggregate security
percentage is calculated.

Per-check statuses are PASSED, FAILED, INCONCLUSIVE, NOT_APPLICABLE and NOT_RUN.
Run security outcomes are PASS, FAIL or INCONCLUSIVE. Unknown provider usage,
unexecuted dependency scans and separate application tenant tests remain explicitly
unknown/unexecuted. Scanning is not a security certification or proof against novel
attacks. Categories use the [OWASP LLM application guidance](https://genai.owasp.org/llm-top-10/),
including prompt injection (LLM01), disclosure (LLM02), excessive agency (LLM06)
and unbounded consumption (LLM10).

## Official AgentDojo case

Install the pinned AgentDojo environment documented in benchmarks/UPSTREAM.md and
configure PREFLIGHT_AGENTDOJO_PYTHON on the trusted worker/API. Select Adversarial
and Official AgentDojo. The supported subset executes upstream banking user_task_0
with injection_task_0, injected bill content and actual upstream tool runtime/state
scorers. Accurate and unsafe native reference presets are scripted test agents.
The unsafe case makes a real synthetic attacker transfer while bill utility remains
successful. This becomes a critical finding. No real banking, hosted inference or
external agent scanning occurs. Native upstream attack success is preserved alongside
the transfer arguments. The pinned upstream scorer has a permissive service-subject
expression; Preflight discloses that limitation and retains actual service/recipient
arguments for inspection. Full official suite and LLM attack generation are unverified.

Run `.local/agentdojo-venv/bin/python scripts/verify_official.py agentdojo` and
`.venv/bin/python scripts/verify_official_platform.py agentdojo` to reproduce.
The first verifier prohibits outbound sockets during evaluation. CI runs both.

## Dependency advisories

From an attempt's Security tab, choose Scan supplied dependencies. Supply at most
20 exact PyPI/npm package versions and explicitly consent to sharing that metadata
with OSV. The backend contacts only the fixed HTTPS OSV batch API, without redirects,
credentials or environment proxies, with a 15-second request timeout and 2 MiB
response cap. It does not execute uploaded source or accept host filesystem paths.
The timestamped response is persisted as a tenant-authorized artifact. Advisory
identifiers are version matches, with exploitability and severity unassessed.
Pagination, unavailable service or malformed responses remain INCONCLUSIVE.
This separate artifact does not silently turn an agent dependency NOT_RUN check
into a pass or modify an existing release score. Review advisories before policy use.
API contract: [official OSV documentation](https://google.github.io/osv.dev/post-v1-querybatch/).
