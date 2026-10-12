"""Trusted, fixed official smoke entry points in operator-installed environments."""

import json
import os
import subprocess
import time
from pathlib import Path
from preflight_eval.sandbox import InfrastructureFailure
from preflight_security import redact, finding

SPECS = {
    "tau3": {
        "scenario": "create_task_1",
        "version": "1.0.1",
        "package": "tau2",
        "package_version": "1.0.1",
        "env": "PREFLIGHT_TAU_PYTHON",
        "script": "tau3.py",
    },
    "agentdojo": {
        "scenario": "user_task_0",
        "version": "v1.2.2",
        "package": "agentdojo",
        "package_version": "0.1.35",
        "env": "PREFLIGHT_AGENTDOJO_PYTHON",
        "script": "dojo_runner.py",
    },
}


def execute_official(benchmark, scenario, mode, seed, timeout, cancelled=None, adversarial=False):
    spec = SPECS[benchmark]
    executable = os.environ.get(spec["env"])
    if not executable or not Path(executable).is_file():
        raise InfrastructureFailure("Official benchmark environment is not installed/configured")
    if scenario != spec["scenario"] or mode not in (
        {"accurate", "regressed", "unsafe"}
        if benchmark == "agentdojo" and adversarial
        else {"accurate", "regressed"}
    ):
        raise InfrastructureFailure("Only the declared official offline smoke preset is supported")
    root = Path(__file__).resolve().parents[3]
    # No provider credentials are inherited by this offline-only benchmark process.
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(root / ".local"),
        "TAU2_DATA_DIR": str(root / ".local/upstream/tau2/data"),
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "PREFLIGHT_BENCHMARK_SEED": str(seed),
    }
    process = subprocess.Popen(
        [executable, str(root / "scripts/benchmarks" / spec["script"]), mode]
        + (["adversarial"] if adversarial else []),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    deadline = time.monotonic() + timeout
    try:
        while True:
            if cancelled and cancelled():
                raise InfrastructureFailure("Official benchmark cancelled")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise InfrastructureFailure("Official benchmark deadline exceeded")
            try:
                output, error = process.communicate(timeout=min(0.2, remaining))
                break
            except subprocess.TimeoutExpired:
                pass
        if process.returncode or len(output) > 1024 * 1024:
            raise InfrastructureFailure(
                "Official benchmark process failed; inspect operator smoke diagnostics"
            )
        data = json.loads(output)
        if (
            data["package_version"] != spec["package_version"]
            or data["task_id"] != scenario
            or data["hosted_model_called"] is not False
        ):
            raise InfrastructureFailure("Official benchmark provenance contract failed")
        score = data["native_score"]
        if type(score) not in (int, float) or score not in (0, 1):
            raise InfrastructureFailure("Unsupported official score")
        events = data.get("events", [])
        if benchmark == "tau3":
            for message in data["upstream_result"]["messages"]:
                if message.get("role") == "assistant":
                    for call in message.get("tool_calls") or []:
                        events.append(
                            {
                                "kind": "tool_call",
                                "tool": call["name"],
                                "arguments": call["arguments"],
                                "source": "official upstream trajectory",
                            }
                        )
                if message.get("role") == "tool":
                    events.append(
                        {
                            "kind": "tool_result",
                            "result": message.get("content"),
                            "source": "official upstream trajectory",
                        }
                    )
        for index, event in enumerate(events):
            event.update({"sequence": index, "parent": None if index == 0 else 0})
        return redact(
            {
                "kind": "agent",
                "scenario_id": scenario,
                "seed": seed,
                "latency_ms": data["latency_ms"],
                "events": events,
                "state": data.get("state", {}),
                "output": {"official_reward": score},
                "assessment": {
                    "task_success": score == 1,
                    "ground_truth": {
                        "status": "PASSED" if score == 1 else "FAILED",
                        "method": "official upstream scorer",
                    },
                    "state_validation": {
                        "status": "PASSED" if score == 1 else "FAILED",
                        "method": "official environment state utility/ENV scoring",
                    },
                    "factual": {"status": "NOT_APPLICABLE"},
                    "confidence": {"status": "INCONCLUSIVE"},
                },
                "security_findings": [
                    finding(
                        "unauthorized_action",
                        "critical",
                        {
                            "completed": True,
                            "injection_task_id": data["injection_task_id"],
                            "events": [e for e in events if e.get("authorization")],
                        },
                    )
                ]
                if data.get("attack_success")
                else [],
                "security_checks": [
                    {
                        "category": "official_prompt_injection",
                        "status": data["security_status"],
                        "evidence": {
                            "upstream_attack_success": data["attack_success"],
                            "injection_task_id": data.get("injection_task_id"),
                        },
                    }
                ]
                if adversarial
                else [],
                "failure": None
                if score == 1
                else {"category": "missing_required_action", "verified": True},
                "official_evidence": data,
                "usage": None,
            }
        )
    except (ValueError, KeyError) as exc:
        raise InfrastructureFailure("Invalid official benchmark artifact") from exc
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
