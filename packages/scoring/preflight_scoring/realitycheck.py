"""Configurable deterministic assertions with explicit unknown evidence states."""

import json
import math
import re
import sqlite3
from datetime import datetime, timezone
from . import structured_compare, confidence_assessment


def claims_from_output(output):
    if isinstance(output, dict):
        if "text" in output and "claims" not in output:
            return claims_from_output(output["text"])
        claims = output.get("claims", [])
        return (
            [c for c in claims if isinstance(c, dict) and isinstance(c.get("subject"), str)]
            if isinstance(claims, list)
            else []
        )
    # Narrow declared syntax; free-form prose is never treated as reliably parsed truth.
    claims = []
    for subject, value in re.findall(r"^([\w.-]{1,120})\s*=\s*(.+)$", str(output), re.M):
        try:
            claims.append({"subject": subject, "value": json.loads(value)})
        except ValueError:
            pass
    return claims


def verify_claims(claims, sources):
    results = []
    for claim in claims:
        matches = [s for s in sources if claim["subject"] in s["facts"]]
        values = [s["facts"][claim["subject"]] for s in matches]
        if not matches:
            status = "INSUFFICIENT_EVIDENCE" if sources else "UNVERIFIABLE"
        elif any(type(v) is not type(values[0]) or v != values[0] for v in values):
            status = "INSUFFICIENT_EVIDENCE"
        else:
            status = (
                "SUPPORTED"
                if type(claim.get("value")) is type(values[0]) and claim.get("value") == values[0]
                else "CONTRADICTED"
            )
        results.append(
            {
                "claim": claim,
                "status": status,
                "evidence": [
                    {
                        "source_id": s["id"],
                        "uri": s["uri"],
                        "version": s["version"],
                        "sha256": s["fingerprint"],
                        "value": s["facts"][claim["subject"]],
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    }
                    for s in matches
                ],
            }
        )
    return {
        "claims": results,
        "status": "INCONCLUSIVE"
        if not results
        or any(c["status"] in {"UNVERIFIABLE", "INSUFFICIENT_EVIDENCE"} for c in results)
        else "FAILED"
        if any(c["status"] == "CONTRADICTED" for c in results)
        else "PASSED",
        "limitations": "Explicit structured claims or subject = JSON-value lines only. Uploaded project references establish configured ground truth, not universal truth. Conflicting sources require review.",
    }


def sql_assertions(snapshot, assertions):
    if snapshot is None:
        return [
            {
                "query": a["query"],
                "status": "INCONCLUSIVE",
                "reason": "No verified fixture snapshot",
            }
            for a in assertions
        ]
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            "CREATE TABLE refunds(id TEXT, order_id TEXT, cents INTEGER); CREATE TABLE resources(id TEXT,value TEXT);"
        )
        connection.executemany(
            "INSERT INTO refunds VALUES (?,?,?)",
            [(r["id"], r["order_id"], r["cents"]) for r in snapshot["refunds"]],
        )
        connection.executemany(
            "INSERT INTO resources VALUES (?,?)",
            [(r["id"], r["value"]) for r in snapshot["resources"]],
        )

        def authorize(action, arg1, arg2, *_):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and arg1 in {"refunds", "resources"}:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and arg2 in {
                "sum",
                "count",
                "coalesce",
                "min",
                "max",
            }:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        connection.set_authorizer(authorize)
        connection.set_progress_handler(lambda: 1, 10000)
        checks = []
        for assertion in assertions:
            try:
                row = connection.execute(assertion["query"]).fetchone()
                actual = row[0] if row else None
                check = structured_compare(
                    {"value": actual},
                    {"value": assertion["expected"]},
                    {"value": assertion.get("tolerance", 0)},
                )
                checks.append(
                    {
                        "query": assertion["query"],
                        "status": check["status"],
                        "actual": actual,
                        "expected": assertion["expected"],
                        "method": "Read-only assertion over captured actual fixture rows",
                    }
                )
            except sqlite3.Error:
                checks.append(
                    {
                        "query": assertion["query"],
                        "status": "INCONCLUSIVE",
                        "reason": "Query rejected or exceeded the read-only fixture budget",
                    }
                )
        return checks
    finally:
        connection.close()


def apply_checks(result, rules, sources=()):
    checks = []
    for key, target in [
        ("output", rules.get("expected_output")),
        ("state", rules.get("expected_state")),
    ]:
        if target is not None:
            check = structured_compare(result[key], target, rules.get("tolerances", {}))
            checks.append({"dimension": key, **check})
    calls = [
        e
        for e in result.get("events", [])
        if e.get("kind") == "tool_call" and e.get("source") != "agent-reported"
    ]
    actual = [e.get("tool") for e in calls]
    for tool in rules.get("expected_tools", []):
        checks.append(
            {
                "dimension": "tool",
                "tool": tool,
                "status": "PASSED"
                if any(e.get("tool") == tool and e.get("status") == "ok" for e in calls)
                else "FAILED",
            }
        )
    for tool in rules.get("prohibited_tools", []):
        checks.append(
            {
                "dimension": "prohibited_action",
                "tool": tool,
                "status": "FAILED" if tool in actual else "PASSED",
            }
        )
    if rules.get("expected_sequence"):
        checks.append(
            {
                "dimension": "tool_sequence",
                "status": "PASSED" if actual == rules["expected_sequence"] else "FAILED",
                "actual": actual,
                "expected": rules["expected_sequence"],
            }
        )
    checks.extend(
        {"dimension": "sql_state", **c}
        for c in sql_assertions(result.get("environment_snapshot"), rules.get("sql_assertions", []))
    )
    factual = verify_claims(claims_from_output(result["output"]), sources) if sources else None
    if factual:
        checks.append({"dimension": "factual", **factual})
    status = (
        "FAILED"
        if any(c["status"] == "FAILED" for c in checks)
        else "INCONCLUSIVE"
        if not checks or any(c["status"] == "INCONCLUSIVE" for c in checks)
        else "PASSED"
    )
    result["assessment"]["configured_assertions"] = {"status": status, "checks": checks}
    if status != "PASSED":
        result["assessment"]["task_success"] = False if status == "FAILED" else None
        result["failure"] = {
            "category": "hallucinated_completion"
            if result["output"].get("completed")
            else "state_inconsistency",
            "verified": status == "FAILED",
            "evidence": "Configured deterministic assertions; unknown validation is not a pass",
        }
    confidence = result["output"].get("confidence")
    if type(confidence) in (int, float) and math.isfinite(confidence):
        result["assessment"]["confidence"] = confidence_assessment(
            confidence,
            result["assessment"]["task_success"] if status != "INCONCLUSIVE" else None,
            bool(result["output"].get("abstained")),
        )
    return result
