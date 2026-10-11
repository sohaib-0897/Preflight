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
        return AgentOutput(await self.graph.ainvoke(inputs))


class CrewAIAdapter:
    capabilities = Capabilities()
    def __init__(self, crew):
        self.crew = crew

    async def invoke(self, inputs, seed=0):
        result = await self.crew.kickoff_async(inputs=inputs)
        return AgentOutput(result.raw)


class OpenAIAgentsAdapter:
    capabilities = Capabilities()
    def __init__(self, agent, runner=None):
        self.agent = agent
        self.runner = runner

    async def invoke(self, inputs, seed=0):
        if self.runner is None:
            from agents import Runner
            self.runner = Runner
        result = await self.runner.run(self.agent, input=inputs["prompt"], max_turns=16)
        return AgentOutput(result.final_output)


def validate_endpoint(url, approved_hosts=()):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("HTTPS endpoint without embedded credentials is required")
    if parsed.hostname not in approved_hosts:
        raise ValueError("Endpoint host requires operator authorization")
    addresses = socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError("Private, loopback, link-local and metadata destinations are forbidden")
    return parsed.hostname


class HTTPAdapter:
    capabilities = Capabilities(events=True, usage=True)
    def __init__(self, endpoint, approved_hosts=(), transport=None):
        self.endpoint = endpoint
        self.hosts = approved_hosts
        self.transport = transport

    async def invoke(self, inputs, seed=0):
        # Deployment MUST enforce destination policy at an egress proxy too (DNS rebinding).
        validate_endpoint(self.endpoint, self.hosts)
        import httpx
        async with httpx.AsyncClient(timeout=20, follow_redirects=False, trust_env=False, transport=self.transport) as client:
            async with client.stream("POST", self.endpoint, json={"inputs": inputs, "seed": seed}) as response:
                response.raise_for_status()
                buffer = bytearray()
                async for chunk in response.aiter_bytes():
                    buffer.extend(chunk)
                    if len(buffer) > 1024 * 1024:
                        raise ValueError("Agent response exceeds 1 MiB")
                import json
                data = json.loads(buffer)
        if not isinstance(data, dict) or "output" not in data:
            raise ValueError("Invalid adapter response")
        return AgentOutput(data["output"], data.get("events", []), data.get("usage", {}))
