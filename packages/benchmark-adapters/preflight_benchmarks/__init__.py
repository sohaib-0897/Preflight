"""Benchmark descriptors with explicit execution availability."""

from preflight_eval.native import SCENARIOS

NATIVE = {
    "id": "native",
    "name": "Preflight native",
    "version": "1.0.0",
    "source": "local",
    "license": "MIT",
    "task_types": ["state", "security", "accuracy", "recovery", "factual", "performance"],
    "interface": "native deterministic runner",
    "dependencies": ["Python >=3.12"],
    "credentials": [],
    "resources": {"cpu": 0.5, "memory_mb": 128},
    "status": "AVAILABLE",
    "scenarios": SCENARIOS,
    "cleanup": "Close per-attempt fixture database; Docker backend removes labeled container.",
}


def registry():
    import os
    from pathlib import Path
    from .execution import SPECS

    entries = [NATIVE]
    for key, name, source in [
        ("tau3", "τ³-bench", "https://github.com/sierra-research/tau2-bench"),
        ("agentdojo", "AgentDojo", "https://github.com/ethz-spylab/agentdojo"),
    ]:
        spec = SPECS[key]
        ready = (
            bool(os.environ.get(spec["env"])) and Path(os.environ.get(spec["env"], "")).is_file()
        )
        entries.append(
            {
                "id": key,
                "name": name,
                "version": spec["version"],
                "package_version": spec["package_version"],
                "source": source,
                "license": "MIT",
                "status": "AVAILABLE" if ready else "BLOCKED",
                "verification_level": "OFFICIAL_SMOKE_EXECUTED",
                "scenarios": [
                    {"id": spec["scenario"], "name": "Official offline scripted-agent smoke"}
                ],
                "credentials": [],
                "resources": {"cpu": 1, "memory_mb": 512},
                "reason": "Only the official offline smoke preset is implemented. Install isolated environment and configure operator worker interpreter; full suites and hosted agents are unverified.",
                "interface": "trusted scripted reference agent; not arbitrary agent or model benchmark coverage",
            }
        )
    return entries
