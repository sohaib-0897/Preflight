import asyncio
import pytest
from types import SimpleNamespace
from preflight_adapters import (
    LangGraphAdapter,
    CrewAIAdapter,
    OpenAIAgentsAdapter,
    CustomAdapter,
    AgentOutput,
    validate_endpoint,
)
from preflight_benchmarks.external import Tau3Adapter, AgentDojoAdapter, BenchmarkUnavailable


def test_framework_contracts():
    class Graph:
        async def ainvoke(self, inputs):
            return {"answer": inputs["prompt"]}

    class Crew:
        async def kickoff_async(self, inputs):
            return SimpleNamespace(raw=inputs["prompt"])

    class Runner:
        @staticmethod
        async def run(agent, input, max_turns):
            return SimpleNamespace(final_output=input)

    async def custom(inputs, seed):
        return AgentOutput(inputs["prompt"])

    async def run():
        for adapter in [
            LangGraphAdapter(Graph()),
            CrewAIAdapter(Crew()),
            OpenAIAgentsAdapter(object(), Runner),
            CustomAdapter(custom),
        ]:
            output = await adapter.invoke({"prompt": "offline"}, 42)
            assert isinstance(output, AgentOutput)
            assert "offline" in str(output.output)

    asyncio.run(run())


def test_ssrf_fail_closed():
    for url in [
        "http://localhost",
        "https://169.254.169.254",
        "file:///etc/passwd",
        "https://user:pass@example.org",
    ]:
        with pytest.raises(ValueError):
            validate_endpoint(url)


def test_upstream_normalization_fixtures():
    assert (
        Tau3Adapter().normalize({"task_id": "fixture-only", "reward_info": {"reward": 1}})["status"]
        == "PASSED"
    )
    assert Tau3Adapter().normalize({"task_id": "unscored"})["status"] == "INCONCLUSIVE"
    assert (
        AgentDojoAdapter().normalize(True, True, "fixture-only", "synthetic-injection")[
            "security_status"
        ]
        == "FAILED"
    )
    assert (
        AgentDojoAdapter().normalize(True, False, "fixture-only")["security_status"]
        == "NOT_APPLICABLE"
    )
    with pytest.raises(BenchmarkUnavailable):
        Tau3Adapter().run(None, None)
    with pytest.raises(ValueError):
        AgentDojoAdapter().normalize("true", False, "x")
