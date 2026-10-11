"""Optional official bridges. Contract fixtures are not official suite coverage."""
import importlib.metadata
import math
from preflight_security import redact


class BenchmarkUnavailable(RuntimeError):
    pass


def require_version(package, version):
    try:
        installed = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        raise BenchmarkUnavailable(f"Install {package}=={version} in an isolated supported environment")
    if installed != version:
        raise BenchmarkUnavailable(f"Expected {package}=={version}; installed {installed}")


class Tau3Adapter:
    benchmark_id = "tau3"
    version = "1.0.1"
    license = "MIT"

    def enumerate(self, domain="mock"):
        require_version("tau2-bench", self.version)
        from tau2.run import get_tasks
        return get_tasks(domain)

    def run(self, config, task, seed=42, *, allow_model_calls=False):
        if not allow_model_calls:
            raise BenchmarkUnavailable("Official execution is opt-in; configure local agents or an explicitly budgeted model provider first")
        require_version("tau2-bench", self.version)
        from tau2.run import run_single_task
        result = run_single_task(config, task, seed=seed)
        return self.normalize(result.model_dump(mode="json"))

    def normalize(self, result):
        reward = (result.get("reward_info") or {}).get("reward")
        if reward is not None and (type(reward) not in (int, float) or not math.isfinite(reward) or not 0 <= reward <= 1):
            raise ValueError("Invalid official reward")
        return redact({"benchmark": self.benchmark_id, "benchmark_version": self.version, "task_id": result.get("task_id"), "reward": reward, "status": "INCONCLUSIVE" if reward is None else "PASSED" if reward == 1 else "FAILED", "evidence": result, "limitations": "Official reward basis must be inspected; natural-language judges may introduce uncertainty."})


class AgentDojoAdapter:
    benchmark_id = "agentdojo"
    version = "0.1.35"
    license = "MIT"

    def run(self, suite, pipeline, user_task_id, injection_task_id=None, injections=None):
        require_version("agentdojo", self.version)
        user_task = suite.get_user_task_by_id(user_task_id)
        injection_task = suite.get_injection_task_by_id(injection_task_id) if injection_task_id else None
        utility, attack_success = suite.run_task_with_pipeline(agent_pipeline=pipeline, user_task=user_task, injection_task=injection_task, injections=injections or {}, verbose=False)
        return self.normalize(utility, attack_success, user_task_id, injection_task_id)

    def normalize(self, utility, attack_success, task_id, injection_id=None):
        if type(utility) is not bool or type(attack_success) is not bool:
            raise ValueError("Official utility and attack success must be booleans")
        return {"benchmark": self.benchmark_id, "package_version": self.version, "task_id": task_id, "utility_success": utility, "attack_success": attack_success if injection_id else None, "security_status": "FAILED" if attack_success else "PASSED" if injection_id else "NOT_APPLICABLE", "injection_id": injection_id, "limitations": "Tuple captures official utility and attack outcomes; trace capture requires a pipeline callback."}
