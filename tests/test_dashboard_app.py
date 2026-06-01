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


def test_classify_report_type_recognizes_wireguard_vpn():
    assert (
        dashboard.classify_report_type("day12_wireguard_vpn_automation_report.json")
        == "WireGuard VPN automation"
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


def test_ai_review_checklist_contains_wireguard_vpn_safety_items():
    checklist = dashboard.ai_review_checklist()

    text = " ".join(
        f"{item['category']} {item['item']} {item['expected']} {item['evidence']}"
        for item in checklist
    )
    assert "Exported config stays local" in text
    assert "Dashboard does not read exports/wireguard" in text
    assert "shell=False" in text


def day12_report(private_key_line="PrivateKey = REDACTED"):
    return {
        "device_name": "Hex-s-2025-lab01",
        "overall_result": "PASS",
        "wireguard_summary": {
            "interface_name": "wg0",
            "peer_name": "pc-wg-day12",
            "client_address": "10.10.10.2/32",
            "exported_config_path": "exports/wireguard/robin-laptop-day12.conf",
        },
        "checks": {
            "handshake_seen": "PASS",
            "ping_lan_gateway": "PASS",
            "ping_lan_host": "PASS",
            "tcp_5201_reachable": "PASS",
        },
        "iperf_summary": {
            "forward_mbps": 192.0,
            "reverse_mbps": 284.0,
        },
        "sanitized_client_config_summary": f"[Interface]\n{private_key_line}\nAddress = 10.10.10.2/32",
    }


def test_day12_dashboard_summary_uses_report_json_only(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day12_wireguard_vpn_automation_report.json",
        day12_report(),
    )
    (reports_dir / "Hex-s-2025-lab01" / "day12_wireguard_vpn_automation_report.html").write_text(
        "<html>WireGuard</html>",
        encoding="utf-8",
    )
    exports_dir = tmp_path / "exports" / "wireguard"
    exports_dir.mkdir(parents=True)
    (exports_dir / "robin-laptop-day12.conf").write_text(
        "PrivateKey = should-never-be-read",
        encoding="utf-8",
    )

    summaries = dashboard.build_day12_dashboard_summaries(reports_dir)

    assert summaries[0]["overall_result"] == "PASS"
    assert summaries[0]["interface_name"] == "wg0"
    assert summaries[0]["peer_name"] == "pc-wg-vpn"
    assert summaries[0]["client_address"] == "10.10.10.2/32"
    assert summaries[0]["exported_config_path"] == "exports/wireguard/robin-laptop-vpn.conf"
    assert summaries[0]["iperf_forward_mbps"] == "192.0"
    assert summaries[0]["iperf_reverse_mbps"] == "284.0"
    assert "should-never-be-read" not in json.dumps(summaries)


def test_day12_dashboard_redacts_unredacted_private_key_from_report(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day12_wireguard_vpn_automation_report.json",
        day12_report("PrivateKey = real-secret"),
    )

    summaries = dashboard.build_day12_dashboard_summaries(reports_dir)

    assert "real-secret" not in json.dumps(summaries)
    assert summaries[0]["sanitized_client_config_summary"] == "PrivateKey: REDACTED"


def test_day12_dashboard_handles_missing_report_gracefully(tmp_path):
    assert dashboard.build_day12_dashboard_summaries(tmp_path / "missing") == []


def test_day12_dashboard_route_shows_fields_without_conf_content(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day12_wireguard_vpn_automation_report.json",
        day12_report(),
    )
    (reports_dir / "Hex-s-2025-lab01" / "day12_wireguard_vpn_automation_report.html").write_text(
        "<html>WireGuard</html>",
        encoding="utf-8",
    )

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    response = app.test_client().get("/reports")

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert "WireGuard VPN Automation" in text
    assert "exports/wireguard/robin-laptop-vpn.conf" in text
    assert "192.0" in text
    assert "284.0" in text
    assert "PrivateKey" not in text
    assert "[Interface]" not in text
    assert "Day12" not in text
    assert "day12_wireguard" not in text


def test_home_summary_includes_missing_wireguard_vpn_card():
    cards = dashboard.build_summary_cards([])

    card = next(card for card in cards if card["title"] == "WireGuard VPN")
    assert card["missing"] is True
    assert card["status"] == "UNKNOWN"


def test_readme_contains_day12_section_and_safety_notes():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## Day12 WireGuard VPN Automation" in readme
    assert "exports/wireguard/<filename>.conf" in readme
    assert "reports/<device_name>/day12_wireguard_vpn_automation_report.json" in readme
    assert "Reports must show `PrivateKey` as `REDACTED`" in readme
    assert "Dashboard must not display full `.conf` content" in readme



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
