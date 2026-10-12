# Python SDK and executable gateways

The installable package is preflight-agent-sdk in packages/python-sdk. From the checkout:

```bash
.venv/bin/pip install -e packages/python-sdk
```

```python
import getpass
from preflight_sdk import Client
client = Client("http://127.0.0.1:8000")
client.login("your-email@example.org", getpass.getpass())
workspace = client.request("GET", "/workspaces")[0]
project = client.request("POST", f"/workspaces/{workspace['id']}/projects", {"name": "Evaluation"})
agent = client.register_agent(project["id"], "Refund Agent")
run = client.evaluate(project["id"], agent["versions"][0]["id"], "first-sdk-run")
# Compose executes through Redis. Standalone native development can execute synchronously:
client.request("POST", f"/runs/{run['id']}/execute", {})
print(client.run(run["id"])["summary"])
```

For connected agents, use `client.credential(workspace_id, name, secret)` and `client.register_connection(project_id, name, endpoint, framework, credential_id)`. Secret values are protected server-side; responses contain only reference metadata. Registering a gateway requires operator-origin authorization. The SDK gateway exposes actual health/invoke routes with bounded execution and optional bearer authentication. See packages/python-sdk/examples and [connection contracts](../architecture/AGENT-CONNECTIONS.md).

Actual LangGraph 1.2.14, CrewAI 1.15.27 and OpenAI Agents SDK 0.23.1 examples execute offline against the installed frameworks. Hash-locked isolated environments and scripts/framework_smoke.py verify compatible invocation and normalization. Accessible tool events/usage vary by framework; no hidden reasoning is captured. These tests do not establish hosted-model or Ollama execution. Connect those providers through an explicitly configured gateway; they are never silently replaced by a mock.

Connected worker dispatch uses the real HTTP protocol, with fixed authorized origins, IP pinning, TLS identity, redirect/proxy rejection, timeouts and response budgets. Local private origins require an exact operator allowlist entry. Read the security and private-network setup before enabling egress. Connected arbitrary code is not run inside the native Docker fixture image.
