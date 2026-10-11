# Executable connections

Native agents remain credential-free offline fixtures. HTTP, Python, LangGraph,
CrewAI, OpenAI Agents SDK and custom agents run in operator-owned processes through
the SDK HTTP contract. Preflight never imports user-provided code in the public API.

Install the SDK with `pip install ./packages/python-sdk`. See
`examples/agents/python_agent.py` for an asynchronous callback and gateway setup.
`create_agent_app` exposes authenticated health and invocation routes, normalizes
accessible events, and applies a deadline. Configure an optional bearer token on
both gateway and a workspace credential reference. Tokens are encrypted with Fernet;
set `PREFLIGHT_CREDENTIAL_KEY` or persist the generated private key file with artifacts.
Back up that key separately. API responses contain credential metadata only.

Operator allowlists: `PREFLIGHT_AGENT_HOSTS` is a comma-separated list of authorized
HTTPS hostnames; `PREFLIGHT_AGENT_PRIVATE_ORIGINS` explicitly authorizes exact
`hostname:port` development gateways. Default access is denied. DNS is resolved once,
all answers are validated, and TCP connects to the approved IP while HTTPS preserves
hostname verification and SNI. Redirects and cloud metadata addresses are rejected.
Connection establishment retries are bounded; ambiguous HTTP POST failures are not
retried by the adapter. Async deadlines cancel local waits; remote execution may
continue and requires gateway-owned cancellation and side-effect idempotency.

Framework examples use actual installed framework execution with explicitly
identified deterministic offline models. These are contract and task-state tests,
not hosted-model performance measurements. No example downloads weights or calls a
paid endpoint. Credentials configured for real models must be managed by the
operator-owned gateway. Selecting a framework does not silently substitute a model.
Ollama and hosted-provider execution remain gateway responsibilities and have not
been verified against a live model server in this environment.

Isolated framework locks under `requirements/agents/` are mandatory: CrewAI 1.15.27
requires OpenAI SDK <3 while OpenAI Agents SDK 0.23.1 requires >=3. Example:

```sh
uv venv .local/langgraph --python 3.12
uv pip sync --python .local/langgraph/bin/python requirements/agents/langgraph.lock
.local/langgraph/bin/python scripts/framework_smoke.py langgraph
```

Use the corresponding lock for `crewai` or `openai-agents`. Framework smoke scripts
invoke all eight native scenarios, then validate action intents against the trusted
local broker. Only that broker applies fixture mutations. Reported framework events
are labeled agent-reported, distinct from enforced broker events.

Upstream references: [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview),
[CrewAI custom LLM](https://docs.crewai.com/en/learn/custom-llm),
[OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk).
Framework packages are optional and independently locked; inspect upstream licenses
before redistribution. Native runtime does not require them.
