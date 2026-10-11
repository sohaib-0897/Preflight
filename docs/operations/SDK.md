# Python client and agent bridges
The stdlib client can be used without SDK dependencies by putting `packages/python-sdk` on PYTHONPATH. Standalone packaging source is provided but wheel building remains unverified.

```python
import getpass
from preflight_sdk import Client
client = Client()
client.login("your-email@example.org", getpass.getpass())
workspaces = client.request("GET", "/workspaces")
project = client.request("POST", f"/workspaces/{workspaces[0]['id']}/projects", {"name": "Agent evaluation"})
agent = client.register_agent(project["id"], "Refund Agent")
run = client.evaluate(project["id"], agent["versions"][0]["id"], "my-first-evaluation")
client.request("POST", f"/runs/{run['id']}/execute", {})
print(client.run(run["id"])["summary"])
```

LangGraph adapter calls a supplied compiled graph's `ainvoke`, CrewAI a supplied crew's `kickoff_async`, OpenAI Agents a supplied agent via `Runner.run` with bounded max_turns, and CustomAdapter a coroutine returning AgentOutput. These wrappers are checked with offline contract objects; the actual optional frameworks are not installed and real provider execution is **not verified**. No wrapper claims access to hidden reasoning. Events and usage are returned only when accessible; simple framework wrappers capture final outputs only.

HTTPAdapter performs HTTPS POST with {inputs, seed}, expects {output, events?, usage?}, requires explicit operator host authorization, rejects private/reserved destinations and redirects, disables inherited proxy settings, and bounds response data. It is a Python integration only; web worker registration currently accepts native modes. Enforce an egress proxy against DNS rebinding before enabling it for tenant-controlled targets. Ollama, hosted provider credential references, remote side-effect bridging and first-class framework/HTTP run dispatch remain outstanding. No paid API is automatically invoked.
