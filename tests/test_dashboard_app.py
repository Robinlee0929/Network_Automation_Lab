import json
from pathlib import Path

import pytest

import dashboard_app as dashboard


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_discover_reports_finds_json_and_html(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(reports_dir / "router1" / "day4_baseline_validation.json", {"result": "PASS"})
    (reports_dir / "router1" / "day4_baseline_validation.html").write_text(
        "<html></html>",
        encoding="utf-8",
    )

    reports = dashboard.discover_reports(reports_dir)

    filenames = {report.filename for report in reports}
    assert "day4_baseline_validation.json" in filenames
    assert "day4_baseline_validation.html" in filenames
    json_entry = next(report for report in reports if report.file_type == "JSON")
    assert json_entry.status == "PASS"
    assert json_entry.html_relative_path == "router1/day4_baseline_validation.html"
    html_entry = next(report for report in reports if report.file_type == "HTML")
    assert html_entry.status == "PASS"


def test_parse_report_status_from_common_status_field(tmp_path):
    report_path = tmp_path / "report.json"
    write_json(report_path, {"overall_status": "failed"})

    assert dashboard.parse_report_status(report_path) == "FAIL"


def test_parse_report_status_from_boolean_field(tmp_path):
    pass_path = tmp_path / "pass.json"
    fail_path = tmp_path / "fail.json"
    write_json(pass_path, {"success": True})
    write_json(fail_path, {"passed": False})

    assert dashboard.parse_report_status(pass_path) == "PASS"
    assert dashboard.parse_report_status(fail_path) == "FAIL"


def test_parse_report_status_handles_day9_nested_aggregate(tmp_path):
    report_path = tmp_path / "day9_performance_regression_report.json"
    write_json(report_path, {"aggregate": {"overall_result": "WARNING"}})

    assert dashboard.parse_report_status(report_path) == "WARNING"


def test_parse_report_status_handles_malformed_json(tmp_path):
    report_path = tmp_path / "broken.json"
    report_path.write_text("{not json", encoding="utf-8")

    assert dashboard.parse_report_status(report_path) == "MALFORMED"


def test_discover_reports_handles_missing_directory(tmp_path):
    assert dashboard.discover_reports(tmp_path / "missing") == []


def test_discover_reports_excludes_backup_folder(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(reports_dir / "Backup" / "day1" / "report.json", {"result": "FAIL"})
    write_json(reports_dir / "router1" / "day4_baseline_validation.json", {"result": "PASS"})

    reports = dashboard.discover_reports(reports_dir)

    assert {report.device for report in reports} == {"router1"}
    assert all(not report.relative_path.lower().startswith("backup/") for report in reports)


def test_classify_report_type_recognizes_day8_and_day9():
    assert (
        dashboard.classify_report_type("day8_iperf3_WAN_TO_LAN_DNAT_report.json")
        == "Day8 iperf3 performance"
    )
    assert (
        dashboard.classify_report_type("reports/router/performance_regression/archive.json")
        == "Day9 performance regression"
    )


def test_ai_review_checklist_documents_day11_controls():
    checklist = dashboard.ai_review_checklist()

    text = " ".join(
        f"{item['category']} {item['item']} {item['expected']} {item['evidence']}"
        for item in checklist
    )
    assert "Allowlist-only execution" in text
    assert "Day9 performance_regression.py should not run from the dashboard" in text
    assert "local system time" in text


def test_flask_routes_are_available(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "router1" / "day9_performance_regression_report.json",
        {"aggregate": {"overall_result": "PASS"}},
    )
    (reports_dir / "router1" / "day9_performance_regression_report.html").write_text(
        "<html>Day9</html>",
        encoding="utf-8",
    )

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    client = app.test_client()

    assert client.get("/").status_code == 200
    assert client.get("/reports").status_code == 200
    assert client.get("/commands").status_code == 200
    assert client.get("/commands/logs").status_code == 200
    checklist_response = client.get("/ai-checklist")
    assert checklist_response.status_code == 200
    assert b"AI Review Checklist" in checklist_response.data
    assert client.post("/commands/not_allowed/run").status_code == 404
    html_response = client.get("/reports/open/router1/day9_performance_regression_report.html")
    assert html_response.status_code == 200
