import io
from pathlib import Path
from pypdf import PdfReader
from integration.test_jobs import create_run
from asgi_client import ASGIClient
from conftest import register


def test_complete_report_provenance_review_history_and_pdf(client, app):
    _, _, run = create_run(client)
    detail = client.post(f"/api/v1/runs/{run['id']}/execute").json()
    attempt = detail["attempts"][0]
    client.post(
        f"/api/v1/runs/{run['id']}/attempts/{attempt['id']}/reviews",
        json={"outcome": "PASSED", "justification": "Verified fixture and captured evidence."},
    )
    client.post(f"/api/v1/runs/{run['id']}/release", json={})
    report = client.get(f"/api/v1/runs/{run['id']}/report.json").json()
    assert report["schema_version"] == "0.2.0" and report["agent"]["version"]
    assert report["benchmark"]["id"] == "native" and report["benchmark"]["license"] == "MIT"
    assert (
        len(report["assessment_history"]) == 8
        and report["human_review_history"][0]["outcome"] == "PASSED"
    )
    assert report["coverage"]["attempts_recorded"] == report["coverage"]["expected_attempts"] == 8
    assert report["release_decisions"][0]["decision"] == "PASS"
    response = client.get(f"/api/v1/runs/{run['id']}/report.pdf")
    assert response.status_code == 200, response.text[:300] if response.status_code != 200 else ""
    assert response.headers["content-type"] == "application/pdf"
    pdf = PdfReader(io.BytesIO(response.content))
    text = "\n".join(page.extract_text() for page in pdf.pages)
    assert run["id"] in text and "Scenario outcomes" in text and "PASS" in text
    assert "Security findings" in text and len(pdf.pages) < 80
    Path(".local").mkdir(exist_ok=True)
    Path(".local/phase10-report.pdf").write_bytes(response.content)
    with ASGIClient(app) as outsider:
        register(outsider, "report-pdf-outsider@example.test")
        assert outsider.get(f"/api/v1/runs/{run['id']}/report.pdf").status_code == 404


def test_pdf_unicode_escape_and_unknown_accuracy_not_failed():
    from preflight.pdf_report import render_pdf

    report = {
        "id": "fixture-unicode",
        "status": "COMPLETED",
        "agent": {"name": "Δ agent", "version": "1", "framework": "native"},
        "benchmark": {"id": "native", "version": "1"},
        "config": {},
        "summary": {},
        "attempts": [
            {
                "id": "a",
                "scenario_id": "unknown",
                "trial": 0,
                "result": {"kind": "agent", "assessment": {"task_success": None}},
            }
        ],
        "security_findings": [],
        "release_decisions": [],
        "reproduction": {},
        "limitations": [],
    }
    pdf = PdfReader(io.BytesIO(render_pdf(report)))
    text = "\n".join(p.extract_text() for p in pdf.pages)
    assert "\\u0394" in text and "UNASSESSED" in text
    assert "FAILED" not in text
