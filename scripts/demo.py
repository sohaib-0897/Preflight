"""Offline native suite and machine-readable release check."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for package in ["evaluation-core", "scoring", "security"]:
    sys.path.insert(0, str(ROOT / "packages" / package))
from preflight_eval import SCENARIO_IDS, execute
from preflight_scoring import DEFAULT_POLICY, aggregate, release_decision


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["accurate", "regressed", "unsafe", "slow", "false-completion"], default="accurate")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--policy", type=Path)
    args = parser.parse_args()
    results = [execute(s, args.mode, 42) for s in SCENARIO_IDS]
    config = {"benchmark": "native", "benchmark_version": "1.0.0", "scenarios": SCENARIO_IDS, "seed": 42, "trials": 1, "backend": "trusted-demo"}
    summary = aggregate(results)
    policy = {**DEFAULT_POLICY, **(json.loads(args.policy.read_text()) if args.policy else {})}
    from preflight_scoring import validate_policy
    try:
        validate_policy(policy)
    except ValueError as exc:
        parser.error(str(exc))
    decision = release_decision(summary, config, policy)
    report = {"summary": summary, "config": config, "attempts": results, "release": decision}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({"summary": summary, "release": decision}, indent=2))
    return 0 if decision["decision"] == "PASS" else 1 if decision["decision"] == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
