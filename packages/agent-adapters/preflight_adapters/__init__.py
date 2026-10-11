"""Explicit adapters for accessible outputs; hidden reasoning is never requested."""

from dataclasses import dataclass, field
from typing import Protocol, Any
import asyncio
import ipaddress
import socket
from urllib.parse import urlparse


@dataclass(frozen=True)
class Capabilities:
    tools: bool = False
    events: bool = False
    usage: bool = False
    deterministic_seed: bool = False


@dataclass
class AgentOutput:
    output: Any
    events: list[dict] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    actions: list[dict] = field(default_factory=list)


class Adapter(Protocol):
    capabilities: Capabilities

    async def invoke(self, inputs: dict, seed: int) -> AgentOutput: ...


class CustomAdapter:
    capabilities = Capabilities()

    def __init__(self, invoke):
        self.function = invoke

    async def invoke(self, inputs, seed=0):
        result = await self.function(inputs, seed)
        if not isinstance(result, AgentOutput):
            raise TypeError("Adapter must return AgentOutput")
        return result


class LangGraphAdapter:
    capabilities = Capabilities(events=False)

    def __init__(self, graph):
        self.graph = graph

    async def invoke(self, inputs, seed=0):
        import time

        start = time.perf_counter()
        async with asyncio.timeout(20):
            output = await self.graph.ainvoke(inputs)
        return AgentOutput(
            output,
            [
                {
                    "kind": "agent_invocation",
                    "framework": "langgraph",
                    "duration_ms": (time.perf_counter() - start) * 1000,
                }
            ],
        )


class CrewAIAdapter:
    capabilities = Capabilities()

    def __init__(self, crew):
        self.crew = crew

    async def invoke(self, inputs, seed=0):
        import time

        start = time.perf_counter()
        async with asyncio.timeout(20):
            result = await self.crew.kickoff_async(inputs=inputs)
        return AgentOutput(
            result.raw,
            [
                {
                    "kind": "agent_invocation",
                    "framework": "crewai",
                    "duration_ms": (time.perf_counter() - start) * 1000,
                }
            ],
        )


class OpenAIAgentsAdapter:
    capabilities = Capabilities()

    def __init__(self, agent, runner=None):
        self.agent = agent
        self.runner = runner

    async def invoke(self, inputs, seed=0):
        if self.runner is None:
            from agents import Runner

            self.runner = Runner
        async with asyncio.timeout(20):
            result = await self.runner.run(self.agent, input=inputs["prompt"], max_turns=16)
        events = []
        for item in getattr(result, "new_items", []):
            if item.type in {"tool_call_item", "tool_call_output_item"}:
                raw = item.raw_item
                payload = raw.model_dump(mode="json") if hasattr(raw, "model_dump") else raw
                events.append({"kind": item.type, "payload": payload})
        for index, item in enumerate(getattr(result, "raw_responses", [])):
            events.append(
                {"kind": "model_invocation", "invocation": index, "response_id": item.response_id}
            )
        return AgentOutput(result.final_output, events)


def resolve_target(url, approved_hosts=(), private_origins=()):
    """Resolve exactly once, validate every answer, then pin the connection to an IP."""
    parsed = urlparse(url)
    if (
        parsed.scheme not in {"https", "http"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.query
    ):
        raise ValueError("Endpoint must have no credentials, query or fragment")
    origin = f"{parsed.hostname}:{parsed.port or (443 if parsed.scheme == 'https' else 80)}"
    private = origin in private_origins
    if not private and (parsed.scheme != "https" or parsed.hostname not in approved_hosts):
        raise ValueError("HTTPS endpoint host requires operator authorization")
    addresses = socket.getaddrinfo(
        parsed.hostname,
        parsed.port or (443 if parsed.scheme == "https" else 80),
        type=socket.SOCK_STREAM,
    )
    if not addresses:
        raise ValueError("Endpoint has no resolvable addresses")
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if (
            ip.is_link_local
            or ip.is_multicast
            or ip.is_unspecified
            or (ip.is_reserved and not ip.is_loopback)
            or (not private and not ip.is_global)
        ):
            raise ValueError("Endpoint destination is forbidden by network policy")
    return parsed, addresses[0][4][0]


def validate_endpoint(url, approved_hosts=()):
    return resolve_target(url, approved_hosts)[0].hostname


class HTTPAdapter:
    capabilities = Capabilities(events=True, usage=True)

    def __init__(
        self,
        endpoint,
        approved_hosts=(),
        transport=None,
        *,
        private_origins=(),
        credential=None,
        auth_type="bearer",
        timeout=20,
        retries=0,
        verify=True,
    ):
        if not 0 < timeout <= 120 or not 0 <= retries <= 2:
            raise ValueError("Invalid invocation budget")
        self.endpoint, self.hosts, self.transport = endpoint, approved_hosts, transport
        self.private_origins, self.credential, self.auth_type = (
            private_origins,
            credential,
            auth_type,
        )
        self.timeout, self.retries, self.verify = timeout, retries, verify

    async def _request(self, method, path=None, payload=None, trace_id=""):
        import httpx
        import json

        async with asyncio.timeout(self.timeout):
            parsed, address = await asyncio.to_thread(
                resolve_target, self.endpoint, self.hosts, self.private_origins
            )
            target = httpx.URL(self.endpoint).copy_with(host=address)
            if path is not None:
                target = target.copy_with(path=path)
            # httpcore 1.0.9 explicitly supports SNI independently of the TCP origin.
            headers = {"Host": parsed.netloc, "X-Preflight-Trace-ID": trace_id}
            if self.credential:
                headers["Authorization" if self.auth_type == "bearer" else "X-API-Key"] = (
                    "Bearer " if self.auth_type == "bearer" else ""
                ) + self.credential
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
                verify=self.verify,
            ) as client:
                async with client.stream(
                    method,
                    target,
                    headers=headers,
                    json=payload,
                    extensions={"sni_hostname": parsed.hostname},
                ) as response:
                    if 300 <= response.status_code < 400:
                        raise ValueError("Agent redirects are forbidden")
                    response.raise_for_status()
                    buffer = bytearray()
                    async for chunk in response.aiter_bytes():
                        buffer.extend(chunk)
                        if len(buffer) > 1024 * 1024:
                            raise ValueError("Agent response exceeds 1 MiB")
                    return json.loads(buffer)

    async def health(self):
        data = await self._request("GET", path="/health")
        if not isinstance(data, dict) or data.get("status") != "ok":
            raise ValueError("Agent health contract failed")
        return {"status": "ok", "capabilities": self.capabilities.__dict__}

    async def invoke(self, inputs, seed=0):
        async with asyncio.timeout(self.timeout):
            return await self._invoke(inputs, seed)

    async def _invoke(self, inputs, seed=0):
        import httpx

        trace_id = inputs.get("trace_id", "")
        # Retry only connection establishment failures. Never replay ambiguous POSTs.
        for attempt in range(self.retries + 1):
            try:
                data = await self._request(
                    "POST",
                    payload={"inputs": inputs, "seed": seed, "trace_id": trace_id},
                    trace_id=trace_id,
                )
                break
            except (httpx.ConnectError, httpx.ConnectTimeout):
                if attempt == self.retries:
                    raise
                await asyncio.sleep(0.1 * (attempt + 1))
        if (
            not isinstance(data, dict)
            or "output" not in data
            or not isinstance(data.get("events", []), list)
            or not isinstance(data.get("usage", {}), dict)
            or not isinstance(data.get("actions", []), list)
        ):
            raise ValueError("Invalid agent response contract")
        if len(data.get("actions", [])) > 16 or len(data.get("events", [])) > 256:
            raise ValueError("Agent event/action budget exceeded")
        return AgentOutput(
            data["output"], data.get("events", []), data.get("usage", {}), data.get("actions", [])
        )
