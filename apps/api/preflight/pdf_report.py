"""Bounded PDF overview, with full evidence retained in JSON/HTML exports."""

import json
from fpdf import FPDF


def render_pdf(report):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_title("Preflight evaluation report")
    pdf.set_author("Preflight")
    pdf.add_page()

    def text(value, size=10):
        # Standard PDF fonts are Latin-only. Escape unsupported Unicode explicitly
        # rather than dropping glyphs or fetching a remote font.
        safe = str(value).encode("ascii", "backslashreplace").decode()
        pdf.set_font("Helvetica", size=size)
        pdf.multi_cell(w=0, h=6, text=safe, new_x="LMARGIN", new_y="NEXT")

    text("Preflight evaluation report", 18)
    text("Evidence summary; download JSON/HTML for complete traces and assertion history.")
    text(
        "Unsupported PDF font characters use explicit Unicode escapes. No external assets are fetched."
    )
    text("Run " + report["id"] + " | " + report["status"])
    text(
        "Agent: "
        + report["agent"]["name"]
        + " | "
        + report["agent"]["version"]
        + " | "
        + report["agent"]["framework"]
    )
    text("Benchmark: " + report["benchmark"]["id"] + " | " + report["benchmark"]["version"])
    text("Configuration", 13)
    config = {
        k: report["config"].get(k)
        for k in [
            "benchmark",
            "benchmark_version",
            "backend",
            "seed",
            "trials",
            "scenarios",
            "execution_label",
        ]
    }
    text(json.dumps(config, ensure_ascii=True, indent=2))
    text("Evidence dimensions and performance", 13)
    text(json.dumps(report["summary"], ensure_ascii=True, indent=2))
    text("Scenario outcomes", 13)
    for attempt in report["attempts"]:
        result = attempt["result"]
        success = result.get("assessment", {}).get("task_success")
        status = (
            "INFRASTRUCTURE"
            if result.get("kind") == "infrastructure"
            else "UNASSESSED"
            if success is None
            else "PASSED"
            if success
            else "FAILED"
        )
        text(
            f"{attempt['scenario_id']} | trial {attempt['trial'] + 1} | {status} | attempt {attempt['id']}"
        )
    text("Security findings", 13)
    for finding in report["security_findings"]:
        text(
            json.dumps(
                {
                    k: finding.get(k)
                    for k in [
                        "id",
                        "severity",
                        "category",
                        "confidence",
                        "scenario_id",
                        "attempt_id",
                        "remediation",
                    ]
                },
                ensure_ascii=True,
            )
        )
    if not report["security_findings"]:
        text("No observed findings; this is not proof that unexecuted security checks passed.")
    text("Release decisions", 13)
    for decision in report["release_decisions"]:
        text(
            json.dumps(
                {
                    k: decision.get(k)
                    for k in [
                        "decision",
                        "policy_id",
                        "policy_version",
                        "violations",
                        "missing_evidence",
                    ]
                },
                ensure_ascii=True,
            )
        )
    if not report["release_decisions"]:
        text("NOT_RUN")
    text("Reproduction and limitations", 13)
    text(json.dumps(report["reproduction"], ensure_ascii=True, indent=2))
    text(json.dumps(report["limitations"], ensure_ascii=True, indent=2))
    output = bytes(pdf.output())
    if len(output) > 2 * 1024 * 1024 or pdf.pages_count > 80:
        raise ValueError("PDF overview exceeded export budget; use JSON/HTML")
    return output
