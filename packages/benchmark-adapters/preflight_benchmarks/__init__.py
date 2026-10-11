"""Benchmark descriptors with explicit execution availability."""
from preflight_eval.native import SCENARIOS

NATIVE = {"id": "native", "name": "Preflight native", "version": "1.0.0", "source": "local", "license": "MIT", "task_types": ["state", "security", "accuracy", "recovery", "factual", "performance"], "interface": "native deterministic runner", "dependencies": ["Python >=3.12"], "credentials": [], "resources": {"cpu": .5, "memory_mb": 128}, "status": "AVAILABLE", "scenarios": SCENARIOS, "cleanup": "Close per-attempt fixture database; Docker backend removes labeled container."}


def registry():
    return [NATIVE, {"id": "tau3", "name": "τ³-bench", "version": "1.0.1", "source": "https://github.com/sierra-research/tau2-bench", "license": "MIT", "status": "BLOCKED", "reason": "Upstream requires Python >=3.12,<3.14 and isolated dependencies; host is 3.14. Official model-driven suites require opt-in credentials."}, {"id": "agentdojo", "name": "AgentDojo", "version": "0.1.35", "source": "https://github.com/ethz-spylab/agentdojo", "license": "MIT", "status": "BLOCKED", "reason": "Upstream package is unavailable in offline cache; official execution not verified."}]
