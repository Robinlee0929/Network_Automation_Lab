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


def test_dashboard_evidence_handles_empty_reports_directory(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    entries = dashboard.collect_dashboard_evidence(tmp_path, reports_dir)

    assert entries
    assert any(entry.status == "MISSING" for entry in entries)
    assert any(entry.title == "Day4 Baseline Validation" for entry in entries)


def test_dashboard_evidence_handles_sample_json_and_html_reports(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"overall_result": "PASS", "device_name": "Hex-s-2025-lab01"},
    )
    (reports_dir / "Hex-s-2025-lab01" / "day4_baseline_validation.html").write_text(
        "<html>Day4</html>",
        encoding="utf-8",
    )

    entries = dashboard.collect_dashboard_evidence(tmp_path, reports_dir)

    day4 = next(entry for entry in entries if entry.title == "Day4 Baseline Validation")
    assert day4.day == "Day4"
    assert day4.device == "Hex-s-2025-lab01"
    assert day4.report_type == "Multi-device baseline report"
    assert day4.status == "PASS"
    assert day4.json_view_path == "reports/Hex-s-2025-lab01/day4_baseline_validation.json"
    assert day4.html_view_path == "reports/Hex-s-2025-lab01/day4_baseline_validation.html"


def test_dashboard_evidence_missing_html_does_not_crash(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"overall_result": "WARN"},
    )

    entries = dashboard.collect_dashboard_evidence(tmp_path, reports_dir)

    day4 = next(entry for entry in entries if entry.title == "Day4 Baseline Validation")
    assert day4.status == "WARN"
    assert day4.html_view_path is None
    assert day4.html_path == "MISSING"


def test_dashboard_rejects_unsafe_report_paths(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    outside = tmp_path / "secret.json"
    outside.write_text('{"password": "secret"}', encoding="utf-8")
    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    client = app.test_client()

    assert client.get("/reports/json/../secret.json").status_code == 404
    assert client.get("/reports/open/../secret.html").status_code == 404


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


def test_ai_intent_reviewer_references_day57_to_day62():
    references = dashboard.ai_intent_reviewer_references()

    assert [item.day for item in references] == ["Day57", "Day58", "Day59", "Day60", "Day62", "Day66", "Day67"]
    text = " ".join(
        f"{item.title} {item.summary} {item.doc_path} {item.roadmap_path} "
        f"{' '.join(item.report_paths)}"
        for item in references
    )
    assert "AI intent mapping prototype" in text
    assert "Safety review gate" in text
    assert "Intent policy matrix" in text
    assert "Reviewer walkthrough" in text
    assert "Scenario pack / sample cases" in text
    assert "docs/ai/day57_intent_mapping_prototype.md" in text
    assert "reports/portfolio/day60_intent_workflow_demo.html" in text
    assert "docs/ai/intent_reviewer_scenario_pack.md" in text
    assert "docs/roadmap/day62_ai_intent_reviewer_scenario_pack.md" in text
    assert "Offline mock runtime skeleton" in text
    assert "docs/ai/intent_offline_mock_runtime_skeleton.md" in text
    assert "docs/roadmap/day66_offline_mock_runtime_skeleton.md" in text
    assert "reports/portfolio/day66_offline_mock_runtime_skeleton.html" in text
    assert "docs/ai/intent_offline_mock_runtime_contract.md" in text
    assert "docs/roadmap/day67_offline_mock_runtime_contract_safety_invariants.md" in text
    assert "reports/portfolio/day67_offline_mock_runtime_contract.html" in text


def test_ai_intent_reviewer_safety_boundaries_are_report_only():
    text = " ".join(dashboard.ai_intent_safety_boundaries())

    assert "Report-only reviewer entry point" in text
    assert "No OpenAI API calls" in text
    assert "No voice input" in text
    assert "No mapped runner task execution" in text
    assert "No SSH sessions" in text
    assert "No config.json requirement" in text
    assert "No NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration changes" in text
    assert "No automatic execution of mapped tasks from scenario examples" in text
    assert "Day66 mock runtime output is fixed offline evidence only" in text
    assert "Day67 validates contract and safety invariants" in text


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
    assert "day12_wireguard_vpn_automation_report.json" in text


def test_dashboard_json_preview_route_redacts_secrets(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {
            "overall_result": "PASS",
            "password": "super-secret",
            "client_config": "[Interface]\nPrivateKey = real-secret",
        },
    )
    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )

    response = app.test_client().get(
        "/reports/json/reports/Hex-s-2025-lab01/day4_baseline_validation.json"
    )

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert "PASS" in text
    assert "super-secret" not in text
    assert "real-secret" not in text
    assert "[REDACTED]" in text
    assert "PrivateKey: REDACTED" in text


def test_home_summary_includes_missing_wireguard_vpn_card():
    cards = dashboard.build_summary_cards([])

    card = next(card for card in cards if card["title"] == "WireGuard VPN")
    assert card["missing"] is True
    assert card["status"] == "UNKNOWN"


def test_home_summary_includes_vrrp_evidence_card(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "lab-summary" / "day35_vrrp_failover_validation.json",
        {"overall_status": "PASS"},
    )

    entries = dashboard.discover_reports(reports_dir)
    cards = dashboard.build_summary_cards(entries)

    card = next(card for card in cards if card["title"] == "HA / VRRP evidence")
    assert card["missing"] is False
    assert card["status"] == "PASS"


def test_dashboard_home_is_portfolio_demo_landing_page(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    app = dashboard.create_app(
        reports_dir=tmp_path / "reports",
        execution_logs_dir=tmp_path / "execution_logs",
    )

    response = app.test_client().get("/")

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert "Network Automation Lab - Portfolio Demo" in text
    assert "READY WITH NOTES" in text
    assert "This demo does not require live router access" in text
    assert "Unified Runner" in text
    assert "Safety Guard / AI Checklist" in text
    assert "Offline Demo Kit" in text
    assert "/reports" in text
    assert "/commands" in text
    assert "/ai-checklist" in text
    assert "/ai-intent-reviewer" in text


def test_ai_intent_reviewer_route_exposes_day57_to_day65_without_execution(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    app = dashboard.create_app(
        reports_dir=tmp_path / "reports",
        execution_logs_dir=tmp_path / "execution_logs",
    )

    response = app.test_client().get("/ai-intent-reviewer")

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert "AI Intent Reviewer Entry Point" in text
    assert "Day57" in text
    assert "Day58" in text
    assert "Day59" in text
    assert "Day60" in text
    assert "Day62" in text
    assert "Day66" in text
    assert "Day67" in text
    assert "Day63 Traceability Evidence Map" in text
    assert "Day64 Reviewer Acceptance Runbook" in text
    assert "Day65 Acceptance Sign-off Package" in text
    assert "Day66 Offline Mock Runtime Skeleton" in text
    assert "Day67 - Offline Mock Runtime Contract &amp; Safety Invariant Validation" in text
    assert "docs/ai/day57_intent_mapping_prototype.md" in text
    assert "reports/portfolio/day60_intent_workflow_demo.html" in text
    assert "docs/ai/intent_reviewer_scenario_pack.md" in text
    assert "docs/roadmap/day62_ai_intent_reviewer_scenario_pack.md" in text
    assert "docs/ai/intent_reviewer_traceability_evidence_map.md" in text
    assert "docs/roadmap/day63_ai_intent_reviewer_traceability_evidence_map.md" in text
    assert "docs/ai/intent_reviewer_acceptance_runbook.md" in text
    assert "docs/roadmap/day64_ai_intent_reviewer_acceptance_runbook.md" in text
    assert "docs/ai/intent_reviewer_acceptance_signoff_package.md" in text
    assert "docs/roadmap/day65_ai_intent_reviewer_acceptance_signoff_package.md" in text
    assert "docs/ai/intent_offline_mock_runtime_skeleton.md" in text
    assert "docs/roadmap/day66_offline_mock_runtime_skeleton.md" in text
    assert "reports/portfolio/day66_offline_mock_runtime_skeleton.json" in text
    assert "Scenario Pack" in text
    assert "trace each AI intent review concept back to Day57-Day62 evidence" in text
    assert "static, report-only runbook" in text
    assert "validation commands, and safety boundaries" in text
    assert "the current system is not a runtime AI executor" in text
    assert "Accepted with notes" in text
    assert "Deferred" in text
    assert "Rejected" in text
    assert "fixed offline mock runtime skeleton" in text
    assert "No action is executed from this page" in text
    assert "This page is report-only" in text
    assert "This page remains static and report-only" in text
    assert "Day65 is documentation/report-only/static dashboard work" in text
    assert "Day66 is offline mock / dry-run-only" in text
    assert "Mock execution means no real command" in text
    assert "Day67 safety boundary: no API, no voice, no SSH, no device access, no live execution, no mapped task execution, and no network configuration changes" in text
    assert "docs/ai/intent_offline_mock_runtime_contract.md" in text
    assert "reports/portfolio/day67_offline_mock_runtime_contract.html" in text
    assert "No OpenAI API calls" in text
    assert "No voice input" in text
    assert "No mapped runner task execution" in text
    assert "No SSH sessions" in text
    assert "No config.json requirement" in text
    assert "No automatic execution of mapped tasks from scenario examples" in text
    assert "Day66 mock runtime output is fixed offline evidence only" in text
    assert "No mapped task was executed. This is a dry-run reviewer walkthrough only." in text
    html = text.lower()
    assert "<form" not in html
    assert "<button" not in html
    assert "method=\"post\"" not in html
    assert "method='post'" not in html
    assert "action=" not in html
    assert "run task" not in html
    assert "execute intent" not in html
    assert "submit intent" not in html
    assert "post /" not in html
    assert "action runner" not in html
    assert "task runner endpoint" not in html
    assert "start task runner" not in html


def test_dashboard_reports_route_exposes_vrrp_evidence_group(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "lab-summary" / "day32_vrrp_readonly_precheck.json",
        {"overall_status": "PASS"},
    )
    doc_path = tmp_path / "docs" / "roadmap" / "ha_vrrp_topology_plan.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("# VRRP plan", encoding="utf-8")

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    response = app.test_client().get("/reports")

    assert response.status_code == 200
    text = response.data.decode("utf-8")
    assert "HA / VRRP Evidence" in text
    assert "HA / VRRP topology plan" in text
    assert "VRRP read-only precheck JSON" in text
    assert "FOUND" in text
    assert "NOT_GENERATED" in text


def test_dashboard_evidence_route_serves_safe_docs_and_rejects_json_raw(tmp_path):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    doc_path = tmp_path / "docs" / "roadmap" / "ha_vrrp_topology_plan.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("# VRRP plan", encoding="utf-8")
    write_json(tmp_path / "topology_profiles" / "day33_vrrp_topology_dry_run.json", {"password": "secret"})

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    client = app.test_client()

    assert client.get("/reports/evidence/docs/roadmap/ha_vrrp_topology_plan.md").status_code == 200
    assert client.get("/reports/evidence/topology_profiles/day33_vrrp_topology_dry_run.json").status_code == 404


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
    intent_reviewer_response = client.get("/ai-intent-reviewer")
    assert intent_reviewer_response.status_code == 200
    assert b"AI Intent Reviewer Entry Point" in intent_reviewer_response.data
    checklist_response = client.get("/ai-checklist")
    assert checklist_response.status_code == 200
    assert b"AI Review Checklist" in checklist_response.data
    assert client.post("/commands/not_allowed/run").status_code == 404
    html_response = client.get("/reports/open/router1/day9_performance_regression_report.html")
    assert html_response.status_code == 200
    json_response = client.get("/reports/json/router1/day9_performance_regression_report.json")
    assert json_response.status_code == 200
