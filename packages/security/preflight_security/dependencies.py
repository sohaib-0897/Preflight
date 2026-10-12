"""Opt-in, bounded OSV version lookup. Does not execute uploaded source code."""

import json
from datetime import datetime, timezone
import httpx

ENDPOINT = "https://api.osv.dev/v1/querybatch"


def query_dependencies(packages):
    if not 1 <= len(packages) <= 20 or any(p["ecosystem"] not in {"PyPI", "npm"} for p in packages):
        raise ValueError("Unsupported package query")
    report = {
        "source": ENDPOINT,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "packages": packages,
        "coverage": "Only supplied exact package versions, known OSV advisories; no source analysis or security certification. Severity is unknown until advisory triage.",
        "findings": [],
    }
    try:
        queries = [
            {"package": {"name": p["name"], "ecosystem": p["ecosystem"]}, "version": p["version"]}
            for p in packages
        ]
        with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
            with client.stream("POST", ENDPOINT, json={"queries": queries}) as response:
                response.raise_for_status()
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > 2 * 1024 * 1024:
                        raise ValueError("OSV response exceeded budget")
        results = json.loads(data)["results"]
        if len(results) != len(packages):
            raise ValueError("Incomplete advisory response")
        incomplete = False
        for package, result in zip(packages, results):
            incomplete = incomplete or bool(result.get("next_page_token"))
            for advisory in result.get("vulns", []):
                report["findings"].append(
                    {
                        "package": package,
                        "advisory_id": advisory["id"],
                        "modified": advisory.get("modified"),
                        "severity": "unknown",
                        "confidence": "known advisory version match; exploitability unassessed",
                        "remediation": "Review the advisory and upgrade to a compatible fixed version.",
                    }
                )
        report["status"] = (
            "FAIL" if report["findings"] else "INCONCLUSIVE" if incomplete else "PASS"
        )
        report["complete"] = not incomplete
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        report.update(
            status="INCONCLUSIVE",
            complete=False,
            reason="OSV unavailable or incomplete response; no clean bill of health",
        )
    return report
