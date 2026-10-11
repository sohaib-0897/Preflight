"""Authentic tau2 mock-domain smoke; scripted offline agent, upstream ENV scorer."""

import importlib.metadata
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("TAU2_DATA_DIR", str(ROOT / ".local/upstream/tau2/data"))
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"


def run(mode="accurate", seed=42):
    from tau2.agent.base_agent import HalfDuplexAgent
    from tau2.user.user_simulator_base import HalfDuplexUser, STOP
    from tau2.data_model.message import AssistantMessage, UserMessage, ToolCall
    from tau2.data_model.simulation import TextRunConfig
    from tau2.evaluator.evaluator import EvaluationType
    from tau2.registry import registry
    from tau2.run import get_tasks, run_single_task

    class ScriptedAgent(HalfDuplexAgent):
        def get_init_state(self, message_history=None):
            return 0

        def generate_next_message(self, message, state):
            if state == 0 and mode == "accurate":
                return AssistantMessage(
                    role="assistant",
                    tool_calls=[
                        ToolCall(
                            id="create-1",
                            name="create_task",
                            arguments={"user_id": "user_1", "title": "Important Meeting"},
                        )
                    ],
                ), 1
            return AssistantMessage(role="assistant", content="The task is complete."), state + 1

    class ScriptedUser(HalfDuplexUser):
        def __init__(self, instructions=None, tools=None, **kwargs):
            super().__init__(instructions, tools)

        def get_init_state(self, message_history=None):
            return 0

        def generate_next_message(self, message, state):
            return UserMessage(
                role="user",
                content="Create a new task called 'Important Meeting' for user_1."
                if state == 0
                else STOP,
            ), state + 1

    registry.register_agent_factory(
        lambda tools, domain_policy, **kwargs: ScriptedAgent(tools, domain_policy),
        "preflight_offline_" + mode,
    )
    if "preflight_offline_user" not in registry.get_users():
        registry.register_user(ScriptedUser, "preflight_offline_user")
    task_id = "create_task_1"
    task = get_tasks("mock", task_ids=[task_id])[0]
    config = TextRunConfig(
        domain="mock",
        agent="preflight_offline_" + mode,
        user="preflight_offline_user",
        llm_agent="preflight/offline-scripted",
        llm_user="preflight/offline-scripted",
        max_steps=8,
    )
    start = time.perf_counter()
    result = run_single_task(config, task, seed=seed, evaluation_type=EvaluationType.ENV)
    data = result.model_dump(mode="json")
    return {
        "benchmark": "tau3",
        "package": "tau2",
        "package_version": importlib.metadata.version("tau2"),
        "revision": "fc0055dc4e0a316c3f83133267fbd6faaa770992",
        "task_id": task_id,
        "domain": "mock",
        "seed": seed,
        "model": "offline scripted reference agent",
        "hosted_model_called": False,
        "native_score": data["reward_info"]["reward"],
        "latency_ms": (time.perf_counter() - start) * 1000,
        "evaluation_type": "ENV",
        "upstream_result": data,
        "limitations": "One official mock-domain scenario using scripted agent and user. Official DB and environment assertion scoring only; no LLM natural-language judge, hosted agent, voice, or full suite coverage.",
    }


if __name__ == "__main__":
    print(
        json.dumps(
            run(
                sys.argv[1] if len(sys.argv) > 1 else "accurate",
                int(os.environ.get("PREFLIGHT_BENCHMARK_SEED", "42")),
            )
        )
    )
