"""Evidence-first deterministic scoring and conservative release decisions."""
import math
import statistics
from datetime import datetime, timezone
import hashlib
import json


def structured_compare(actual, expected, tolerances=None):
    tolerances = tolerances or {}
    fields = []
    for key, target in expected.items():
        value = actual.get(key)
        tolerance = tolerances.get(key, 0)
        if isinstance(target, (float, int)) and not isinstance(target, bool):
            passed = type(value) in (int, float) and math.isfinite(value) and abs(value-target) <= tolerance
        else:
            passed = type(value) is type(target) and value == target
        fields.append({"field": key, "expected": target, "actual": value, "tolerance": tolerance, "passed": passed})
    return {"status": "PASSED" if all(f["passed"] for f in fields) else "FAILED", "fields": fields, "method": "deterministic structured comparison"}


CORPUS = {"earth_moons": 1, "water_freezes_celsius": 0, "refund_policy_days": 30}


def factual_verify(claims, corpus=None):
    corpus = CORPUS if corpus is None else corpus
    stamp = datetime.now(timezone.utc).isoformat()
    fingerprint = hashlib.sha256(json.dumps(corpus, sort_keys=True).encode()).hexdigest()
    results = []
    for claim in claims:
        key = claim.get("subject")
        state = "UNVERIFIABLE" if key not in corpus else "SUPPORTED" if type(claim.get("value")) is type(corpus[key]) and claim.get("value") == corpus[key] else "CONTRADICTED"
        results.append({"claim": claim, "status": state, "evidence": None if key not in corpus else {"source": "preflight://trusted-corpus/v1#"+key, "value": corpus[key], "sha256": fingerprint, "retrieved_at": stamp}})
    return {"claims": results, "supported": sum(r["status"] == "SUPPORTED" for r in results), "contradicted": sum(r["status"] == "CONTRADICTED" for r in results), "unverifiable": sum(r["status"] == "UNVERIFIABLE" for r in results), "limitations": "Only explicit structured claims against the authorized local reference corpus; no general web truth inference."}


def confidence_assessment(confidence, correct=None, abstained=False):
    if not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("Confidence must be finite and between 0 and 1")
    return {"status": "INCONCLUSIVE" if correct is None else "PASSED" if correct else "FAILED", "brier_score": None if correct is None else (confidence-int(correct))**2, "abstained": abstained, "ground_truth_available": correct is not None}


def wilson(successes, n):
    if n == 0:
        return [0.0, 1.0]
    z = 1.96
    p = successes/n
    denominator = 1+z*z/n
    center = (p+z*z/(2*n))/denominator
    margin = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return [max(0, center-margin), min(1, center+margin)]


def aggregate(results):
    scored = [r for r in results if r.get("kind") != "infrastructure" and r["assessment"]["task_success"] is not None]
    success = sum(r["assessment"]["task_success"] for r in scored)
    latencies = sorted(r["latency_ms"] for r in scored)
    findings = [f for r in scored for f in r["security_findings"]]
    by_scenario = {}
    for item in scored:
        by_scenario.setdefault(item["scenario_id"], []).append(item["assessment"]["task_success"])
    independent_successes = sum(all(values) for values in by_scenario.values())
    return {"sample_size": len(scored), "infrastructure_failures": sum(r.get("kind")=="infrastructure" for r in results), "unassessed_attempts": sum(r.get("kind")!="infrastructure" and r["assessment"]["task_success"] is None for r in results), "task_success_rate": success/len(scored) if scored else None, "successes": success, "effective_sample_size": len(by_scenario), "confidence_interval_95": wilson(independent_successes,len(by_scenario)), "confidence_interval_unit": "Distinct scenario passed every recorded trial; deterministic repetitions are not independent samples", "latency_mean_ms": statistics.mean(latencies) if latencies else None, "latency_p95_ms": latencies[max(0, math.ceil(.95*len(latencies))-1)] if latencies else None, "critical_security_findings": sum(f["severity"] == "critical" and f["confidence"] == "confirmed" for f in findings), "security_findings": len(findings), "token_usage": None, "estimated_cost": None, "usage_note": "Token usage and API cost unavailable unless explicitly reported; no synthetic measurements."}


def compare_runs(left, right):
    keys = ["benchmark", "benchmark_version", "scenarios", "trials", "seed", "backend", "dataset_fingerprint"]
    incompatible = [k for k in keys if left["config"].get(k) != right["config"].get(k)]
    if incompatible:
        return {"compatible": False, "reason": "Different evaluation configurations", "fields": incompatible}
    def keyed(run):
        return {(a["scenario_id"], a["trial"]): a["result"] for a in run["attempts"] if a["result"].get("kind") != "infrastructure" and a["result"]["assessment"]["task_success"] is not None}
    l, r = keyed(left), keyed(right)
    if set(l) != set(r) or not l:
        return {"compatible": False, "reason": "Missing or infrastructure-failed paired attempts"}
    pairs = [{"scenario_id": k[0], "trial": k[1], "baseline_success": l[k]["assessment"]["task_success"], "candidate_success": r[k]["assessment"]["task_success"], "latency_delta_ms": r[k]["latency_ms"]-l[k]["latency_ms"]} for k in sorted(l)]
    wins = sum(not p["baseline_success"] and p["candidate_success"] for p in pairs)
    losses = sum(p["baseline_success"] and not p["candidate_success"] for p in pairs)
    # Infer on scenario clusters instead of counting correlated deterministic repetitions.
    grouped = {}
    for pair in pairs:
        grouped.setdefault(pair["scenario_id"], []).append(pair)
    scenario_wins = sum(all(not p["baseline_success"] and p["candidate_success"] for p in group) for group in grouped.values())
    scenario_losses = sum(all(p["baseline_success"] and not p["candidate_success"] for p in group) for group in grouped.values())
    discordant = scenario_wins+scenario_losses
    pvalue = min(1, 2*sum(math.comb(discordant,i) for i in range(min(scenario_wins,scenario_losses)+1))/2**discordant) if discordant else 1
    return {"compatible": True, "pairs": pairs, "sample_size": len(pairs), "success_delta": (wins-losses)/len(pairs), "wins": wins, "regressions": losses, "effective_sample_size": len(grouped), "paired_exact_pvalue": pvalue, "statistically_significant_95": pvalue < .05, "limitations": "Repeated deterministic trials are correlated; this small fixture suite does not estimate production performance."}


DEFAULT_POLICY = {"min_success": .8, "max_critical": 0, "max_latency_ms": 1000, "min_samples": 8, "required_scenarios": [], "required_benchmarks": ["native"], "required_reviews": 0, "max_cost": None, "regression_tolerance": None}


def release_decision(summary, config, policy, reviews=0, comparison=None, run_status="COMPLETED"):
    reasons, missing = [], []
    if run_status != "COMPLETED":
        missing.append("Run has not completed")
    if summary.get("unassessed_attempts",0):
        missing.append("Accuracy evidence is inconclusive for selected attempts")
    if summary.get("infrastructure_failures", 0):
        missing.append("Infrastructure failures leave evaluation coverage incomplete")
    if summary.get("effective_sample_size", summary.get("sample_size", 0)) < policy["min_samples"]:
        missing.append("Insufficient sample size")
    if summary.get("task_success_rate") is None:
        missing.append("No scored task results")
    elif summary["task_success_rate"] < policy["min_success"]:
        reasons.append("Task success below required threshold")
    if summary.get("critical_security_findings", 0) > policy["max_critical"]:
        reasons.append("Critical confirmed security findings exceed policy")
    if summary.get("latency_p95_ms") is None:
        missing.append("Latency unavailable")
    elif summary["latency_p95_ms"] > policy["max_latency_ms"]:
        reasons.append("P95 latency exceeds budget")
    if not set(policy["required_scenarios"]).issubset(config.get("scenarios", [])):
        missing.append("Required scenarios missing")
    if set(policy["required_benchmarks"]) - {config.get("benchmark")}:
        missing.append("Required benchmark suites missing")
    if reviews < policy["required_reviews"]:
        missing.append("Required human reviews missing")
    if policy["max_cost"] is not None:
        if summary.get("estimated_cost") is None:
            missing.append("Measured cost unavailable")
        elif summary["estimated_cost"] > policy["max_cost"]:
            reasons.append("Cost exceeds budget")
    if policy["regression_tolerance"] is not None:
        if not comparison or not comparison.get("compatible"):
            missing.append("Compatible baseline comparison required")
        elif comparison["success_delta"] < -policy["regression_tolerance"]:
            reasons.append("Regression exceeds tolerance")
    return {"decision": "FAIL" if reasons else "INCONCLUSIVE" if missing else "PASS", "violations": reasons, "missing_evidence": missing, "policy": policy, "limitations": "Threshold decision on recorded fixture evidence, not a production security guarantee."}
