"""Metrics with explicit applicability and usage provenance."""

import math
import random
import statistics


def outcome(value):
    if not isinstance(value, dict):
        return None
    if type(value.get("passed")) is bool:
        return value["passed"]
    if value.get("status") in {"PASSED", "FAILED"}:
        return value["status"] == "PASSED"
    claims = value.get("claims", [])
    if claims and all(c.get("status") in {"SUPPORTED", "CONTRADICTED"} for c in claims):
        return all(c["status"] == "SUPPORTED" for c in claims)
    return None


def rate(values):
    available = [v for v in values if type(v) is bool]
    return {
        "value": sum(available) / len(available) if available else None,
        "samples": len(available),
        "unassessed_or_not_applicable": len(values) - len(available),
    }


def reported(value, integer=False):
    return (
        value
        if type(value) in ((int,) if integer else (int, float))
        and math.isfinite(value)
        and 0 <= value <= 10**12
        else None
    )


def metrics(results):
    attempts = [r for r in results if r.get("kind") != "infrastructure"]
    dimensions = {
        name: rate([outcome(r.get("assessment", {}).get(key)) for r in attempts])
        for name, key in [
            ("structured_accuracy", "ground_truth"),
            ("state_validation", "state_validation"),
            ("factual_correctness", "factual"),
        ]
    }
    tools = []
    for result in attempts:
        assertions = result.get("assessment", {}).get("configured_assertions", {}).get("checks", [])
        checks = [
            c
            for c in assertions
            if c.get("dimension") in {"tool", "tool_sequence", "prohibited_action"}
        ]
        calls = [
            e
            for e in result.get("events", [])
            if e.get("kind") == "tool_call" and e.get("source") != "agent-reported"
        ]
        tools.append(
            all(c["status"] == "PASSED" for c in checks)
            if checks and all(c["status"] in {"PASSED", "FAILED"} for c in checks)
            else all(e["status"] == "ok" for e in calls)
            if calls and all(e.get("status") in {"ok", "denied", "timeout", "error"} for e in calls)
            else None
        )
    dimensions["tool_execution"] = rate(tools)
    dimensions["recovery_success"] = rate(
        [r["assessment"]["task_success"] for r in attempts if r["scenario_id"] == "tool-timeout"]
    )
    dimensions["security_finding_rate"] = rate([bool(r.get("security_findings")) for r in attempts])
    dimensions["configured_accuracy"] = rate(
        [outcome(r.get("assessment", {}).get("configured_assertions")) for r in attempts]
    )
    tokens = []
    costs = []
    checks = {}
    severities = {}
    for result in attempts:
        usage = result.get("usage") or {}
        total = reported(usage.get("total_tokens"), True)
        incoming = reported(usage.get("input_tokens"), True)
        outgoing = reported(usage.get("output_tokens"), True)
        if total is None and incoming is not None and outgoing is not None:
            total = incoming + outgoing
        tokens.append(total)
        costs.append(
            reported(usage.get("estimated_cost_usd"))
            if usage.get("currency") == "USD" and usage.get("cost_source")
            else None
        )
        for check in result.get("security_checks", []):
            checks.setdefault(check["category"], []).append(check["status"])
        for finding in result.get("security_findings", []):
            severities[finding["severity"]] = severities.get(finding["severity"], 0) + 1
    all_tokens = bool(tokens) and all(v is not None for v in tokens)
    all_costs = bool(costs) and all(v is not None for v in costs)
    return {
        "dimensions": dimensions,
        "security_check_statuses": checks,
        "security_severities": severities,
        "token_usage": sum(tokens) if all_tokens else None,
        "token_reported_attempts": sum(t is not None for t in tokens),
        "estimated_cost": statistics.mean(costs) if all_costs else None,
        "estimated_total_cost": sum(costs) if all_costs else None,
        "cost_reported_attempts": sum(c is not None for c in costs),
        "cost_unit": "USD per task attempt; estimates explicitly reported by agent/provider",
        "usage_note": "Reported usage is not independently metered. Missing/invalid usage stays unknown; native fixtures do not synthesize tokens or prices.",
    }


def cluster_latency_interval(pairs, iterations=1000):
    grouped = {}
    for pair in pairs:
        grouped.setdefault(pair["scenario_id"], []).append(pair["latency_delta_ms"])
    values = [statistics.mean(v) for v in grouped.values()]
    if len(values) < 2:
        return {
            "mean_delta_ms": statistics.mean(values) if values else None,
            "interval_95_ms": None,
            "independent_scenarios": len(values),
            "status": "INCONCLUSIVE",
        }
    rng = random.Random(42)
    boot = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(iterations))
    return {
        "mean_delta_ms": statistics.mean(values),
        "interval_95_ms": [boot[int(0.025 * iterations)], boot[int(0.975 * iterations) - 1]],
        "independent_scenarios": len(values),
        "method": "Paired scenario-cluster percentile bootstrap, 1000 draws, seed 42; approximate small-sample interval",
        "status": "ESTIMATED",
    }
