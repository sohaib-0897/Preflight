"""Run in each isolated, locked framework environment. No hosted model requests."""

import asyncio
import importlib
import importlib.metadata
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in [
    "examples/agents",
    "packages/agent-adapters",
    "packages/python-sdk",
    "packages/evaluation-core",
    "packages/scoring",
    "packages/security",
]:
    sys.path.insert(0, str(ROOT / folder))


async def main():
    from preflight_adapters import AgentOutput
    from preflight_eval.connected import verify_response
    from preflight_eval import SCENARIOS
    framework = sys.argv[1]
    module = importlib.import_module(
        {
            "langgraph": "langgraph_agent",
            "crewai": "crewai_agent",
            "openai-agents": "openai_agents_agent",
        }[framework]
    )
    results = []
    for scenario in SCENARIOS:
        started = time.perf_counter()
        contract = await module.invoke(
            {"scenario_id": scenario["id"], "prompt": scenario["request"]}, 42
        )
        result = verify_response(
            scenario["id"],
            AgentOutput(
                contract["output"],
                contract.get("events", []),
                contract.get("usage", {}),
                contract.get("actions", []),
            ),
            42,
            (time.perf_counter() - started) * 1000,
        )
        assert result["assessment"]["task_success"], result
        assert result["events"]
        results.append(
            {
                "scenario_id": scenario["id"],
                "task_success": True,
                "events": result["events"],
                "state": result["state"],
            }
        )
    output = {
        "framework": framework,
        "package_version": importlib.metadata.version(framework),
        "inference": "offline deterministic example in actual framework runtime",
        "hosted_model_called": False,
        "scenarios": results,
    }
    (ROOT / ".local").mkdir(exist_ok=True)
    (ROOT / ".local" / f"{framework}-smoke.json").write_text(json.dumps(output, indent=2))
    print(
        f"{framework}: eight real framework invocations and broker validations passed; no hosted inference."
    )


asyncio.run(main())
