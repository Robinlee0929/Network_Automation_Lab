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


def test_dashboard_evidence_surfaces_day88_design_report(tmp_path):
    reports_dir = tmp_path / "reports"
    write_json(
        reports_dir / "lab-summary" / "day88_real_readonly_executor_adapter_design.json",
        {
            "overall_status": "PASS",
            "phase_state": "DESIGN_ONLY",
            "execution_supported": False,
            "dashboard_execute_button_supported": False,
        },
    )
    (reports_dir / "lab-summary" / "day88_real_readonly_executor_adapter_design.html").write_text(
        "<html>Day88 design-only report</html>",
        encoding="utf-8",
    )

    entries = dashboard.collect_dashboard_evidence(tmp_path, reports_dir)

    day88 = next(entry for entry in entries if entry.day == "Day88")
    assert day88.title == "Real Read-only Executor Adapter Design Draft"
    assert day88.status == "PASS"
    assert day88.json_view_path == "reports/lab-summary/day88_real_readonly_executor_adapter_design.json"
    assert day88.html_view_path == "reports/lab-summary/day88_real_readonly_executor_adapter_design.html"
    day88_text = f"{day88.title} {day88.description} {day88.notes}".lower()
    assert "ssh_supported=false" in day88_text
    assert "routeros_connection_supported=false" in day88_text
    assert "live_command_supported=false" in day88_text


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


def test_ai_intent_reviewer_references_day57_to_day85():
    references = dashboard.ai_intent_reviewer_references()

    assert [item.day for item in references] == [
        "Day57",
        "Day58",
        "Day59",
        "Day60",
        "Day62",
        "Day66",
        "Day67",
        "Day68",
        "Day69",
        "Day70",
        "Day71",
        "Day72",
        "Day73",
        "Day74",
        "Day75",
        "Day76",
        "Day77",
        "Day78",
        "Day79",
        "Day80",
        "Day81",
        "Day82",
        "Day83",
        "Day84",
        "Day85",
        "Day86",
        "Day87",
        "Day88",
    ]
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
    assert "Real Read-only Executor Adapter Design Draft" in text
    assert "docs/ai/intent_real_readonly_executor_adapter_design.md" in text
    assert "docs/roadmap/day88_real_readonly_executor_adapter_design.md" in text
    assert "reports/lab-summary/day88_real_readonly_executor_adapter_design.html" in text
    assert "Reviewer report quality and evidence trace" in text
    assert "docs/ai/intent_offline_mock_runtime_reviewer_report_quality.md" in text
    assert "docs/roadmap/day68_offline_mock_runtime_reviewer_report_quality.md" in text
    assert "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html" in text
    assert "Reviewer dashboard evidence drilldown" in text
    assert "docs/ai/intent_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md" in text
    assert "docs/roadmap/day69_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md" in text
    assert "AI runtime readiness gate" in text
    assert "docs/ai/intent_offline_mock_runtime_phase_exit_review.md" in text
    assert "docs/roadmap/day70_offline_mock_runtime_phase_exit_ai_readiness_gate.md" in text
    assert "Controlled AI runtime prototype entry design" in text
    assert "docs/ai/intent_controlled_ai_runtime_entry_design.md" in text
    assert "docs/roadmap/day71_controlled_ai_runtime_prototype_entry_design.md" in text
    assert "Controlled AI runtime input contract validator" in text
    assert "docs/ai/intent_controlled_ai_runtime_input_validator.md" in text
    assert "docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md" in text
    assert "Mock AI decision pipeline" in text
    assert "docs/ai/intent_mock_ai_decision_pipeline.md" in text
    assert "docs/roadmap/day73_mock_ai_decision_pipeline.md" in text
    assert "reports/lab-summary/day73_mock_ai_decision_pipeline.html" in text
    assert "Controlled dry-run plan builder" in text
    assert "docs/ai/intent_dry_run_plan_builder.md" in text
    assert "docs/roadmap/day74_dry_run_plan_builder.md" in text
    assert "reports/lab-summary/day74_dry_run_plan_builder.html" in text
    assert "Manual review approval envelope" in text
    assert "docs/ai/intent_manual_review_approval_envelope.md" in text
    assert "docs/roadmap/day75_manual_review_approval_envelope.md" in text
    assert "reports/lab-summary/day75_manual_review_approval_envelope.html" in text
    assert "Controlled runtime audit trail" in text
    assert "docs/ai/intent_runtime_audit_trail.md" in text
    assert "docs/roadmap/day76_runtime_audit_trail.md" in text
    assert "reports/lab-summary/day76_runtime_audit_trail.html" in text
    assert "Runtime safety gate" in text
    assert "docs/ai/intent_runtime_safety_gate.md" in text
    assert "docs/roadmap/day77_runtime_safety_gate.md" in text
    assert "reports/lab-summary/day77_runtime_safety_gate.html" in text
    assert "Controlled runtime safety case" in text
    assert "docs/ai/intent_runtime_safety_case.md" in text
    assert "docs/roadmap/day78_runtime_safety_case.md" in text
    assert "reports/lab-summary/day78_runtime_safety_case.html" in text
    assert "Controlled read-only task contract and allowlist" in text
    assert "docs/ai/intent_readonly_task_contract.md" in text
    assert "docs/roadmap/day79_readonly_task_contract.md" in text
    assert "reports/lab-summary/day79_readonly_task_contract.html" in text
    assert "Read-only execution broker skeleton" in text
    assert "docs/ai/intent_readonly_execution_broker.md" in text
    assert "docs/roadmap/day80_readonly_execution_broker_skeleton.md" in text
    assert "reports/lab-summary/day80_readonly_execution_broker.html" in text
    assert "Read-only broker review queue and decision state report" in text
    assert "docs/ai/intent_broker_review_queue.md" in text
    assert "docs/roadmap/day81_broker_review_queue.md" in text
    assert "reports/lab-summary/day81_broker_review_queue.html" in text
    assert "Reviewer decision audit summary and queue evidence export" in text
    assert "docs/ai/intent_reviewer_decision_audit_summary.md" in text
    assert "docs/roadmap/day82_reviewer_decision_audit_summary.md" in text
    assert "reports/lab-summary/day82_reviewer_decision_audit_summary.html" in text
    assert "Read-only executor readiness gate" in text
    assert "docs/ai/readonly_executor_readiness_gate.md" in text
    assert "docs/roadmap/day83_readonly_executor_readiness_gate.md" in text
    assert "reports/lab-summary/day83_readonly_executor_readiness_gate.html" in text
    assert "Read-only executor adapter interface contract" in text
    assert "docs/ai/intent_readonly_executor_adapter_contract.md" in text
    assert "docs/roadmap/day84_readonly_executor_adapter_interface_contract.md" in text
    assert "reports/lab-summary/day84_readonly_executor_adapter_contract.html" in text
    assert "Mock Adapter + Evidence Binding" in text
    assert "Controlled Runner Harness + Safety Regression" in text
    assert "docs/ai/intent_controlled_runner_harness.md" in text
    assert "reports/lab-summary/day86_controlled_runner_harness.html" in text
    assert "Compatibility Matrix stays internal validation only" in text
    assert "docs/ai/intent_mock_adapter_evidence_binding.md" in text
    assert "docs/roadmap/day85_mock_adapter_evidence_binding.md" in text
    assert "reports/lab-summary/day85_mock_adapter_evidence_binding.html" in text


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
    assert "Day68 reviews report quality and evidence traceability" in text
    assert "Day69 presents reviewer evidence drilldown only" in text
    assert "Day70 is an AI runtime readiness gate only" in text
    assert "no dashboard forms, no POST routes for AI intent review, and no action endpoints" in text
    assert "Day72 validates controlled AI runtime input payloads only" in text
    assert "Day72 adds no OpenAI API, voice, SSH, device access, live execution, mapped task execution, config changes, forms, POST routes, or action endpoints" in text
    assert "Day73 runs deterministic mock decisions after Day72 validation only" in text
    assert "Day73 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard POST/action endpoint, or network configuration change" in text
    assert "Day74 converts Day73 mock decisions into dry-run plan previews only" in text
    assert "Day74 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, or network configuration change" in text
    assert "Day75 wraps Day74 dry-run plans in record-only reviewer sign-off envelopes" in text
    assert "execution_unlock_supported remains false" in text
    assert "Day75 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approval surface, execution control, approval unlock, or network configuration change" in text
    assert "Day76 links Day73 decisions, Day74 dry-run plans, and Day75 approval envelopes into reviewer audit evidence only" in text
    assert "Day76 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, or network configuration change" in text
    assert "Day77 links Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, and Day76 audit records into locked runtime safety gate evidence only" in text
    assert "runtime_gate_state remains LOCKED" in text
    assert "Day77 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day78 links Day72 input validation, Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, Day76 audit records, and Day77 locked gates into end-to-end reviewer safety case evidence only" in text
    assert "final_recommendation remains REVIEW_ONLY" in text
    assert "Day78 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day79 defines the read-only task allowlist and capability definition layer after the Day72-Day78 runtime safety chain" in text
    assert "Day79 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day80 defines the read-only execution broker skeleton after the Day79 allowlist" in text
    assert "ssh_allowed remains false" in text
    assert "live_command_allowed remains false" in text
    assert "Day80 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day81 defines the read-only broker review queue and decision state report after Day80" in text
    assert "dashboard_action_allowed false" in text
    assert "Day81 adds no OpenAI API, AI SDK, real AI runtime, voice, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day82 summarizes Day81 queue decisions into reviewer audit evidence exports only" in text
    assert "ai_runtime_allowed false" in text
    assert "Day82 adds no OpenAI API, AI SDK runtime, real AI runtime, voice, SSH, device access, live execution, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change" in text


def test_day69_reviewer_evidence_drilldown_is_static_and_complete():
    chain = dashboard.day69_evidence_chain()
    scenarios = dashboard.day69_scenario_evidence_drilldown()

    assert [item.day for item in chain] == ["Day66", "Day67", "Day68", "Day69"]
    assert chain[1].status == "PASS"
    assert chain[2].status == "REVIEW_READY"
    assert chain[3].status == "STATIC_REVIEW_READY"

    categories = {scenario.safety_category for scenario in scenarios}
    assert {
        "documentation_only",
        "report_only",
        "blocked_live_action",
        "needs_manual_review",
    }.issubset(categories)
    assert all(scenario.contract_status == "PASS" for scenario in scenarios)
    assert all(scenario.review_quality_status == "REVIEW_READY" for scenario in scenarios)
    assert all("Day66 mock_scenarios" in scenario.evidence_source for scenario in scenarios)
    assert all("No API" in scenario.safety_note for scenario in scenarios)
    assert all("reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json" in scenario.report_paths for scenario in scenarios)


def test_day70_ai_runtime_readiness_gate_is_static_and_explicit():
    gates = dashboard.day70_ai_runtime_readiness_gates()

    statuses_by_gate = {gate.gate: gate.status for gate in gates}

    assert statuses_by_gate == {
        "Offline mock runtime exists": "PASS",
        "Contract validation exists": "PASS",
        "Reviewer quality review exists": "PASS",
        "Dashboard evidence drilldown exists": "PASS",
        "Live execution boundary documented": "PASS",
        "Human review requirement documented": "PASS",
        "AI runtime implementation started": "NOT STARTED",
        "Voice integration started": "NOT STARTED",
        "Device access enabled": "NOT ENABLED",
        "OpenAI API enabled": "NOT ENABLED",
    }
    text = " ".join(f"{gate.gate} {gate.status} {gate.evidence}" for gate in gates)
    assert "Day70 is a readiness gate only, not runtime implementation" in text
    assert "No SSH, router, switch, firewall, VPN, or lab device access" in text
    assert "No OpenAI dependency, API key, environment variable, or API call" in text


def test_day71_controlled_entry_design_is_static_and_explicit():
    design = dashboard.day71_controlled_ai_runtime_entry_design()

    assert design["day"] == 71
    assert design["title"] == "Controlled AI Runtime Prototype Entry Design"
    assert design["safety_stage"] == "design_only"
    assert design["execution_allowed"] is False
    assert design["api_integration_allowed"] is False
    assert design["voice_allowed"] is False
    assert design["device_access_allowed"] is False
    assert design["dashboard_action_surface_allowed"] is False
    assert design["mapped_task_execution_allowed"] is False
    assert design["live_execution_allowed"] is False
    assert design["required_reviewer_gate"] is True
    assert any(
        item["name"] == "execution_allowed" and "Always false" in item["requirement"]
        for item in design["input_contract"]
    )
    assert [item["name"] for item in design["safety_gate_sequence"]][-1] == (
        "future controlled execution consideration"
    )
    assert [item["day"] for item in design["reviewer_evidence_map"]] == [
        "Day57",
        "Day58",
        "Day59",
        "Day60",
        "Day61",
        "Day62",
        "Day63",
        "Day64",
        "Day65",
        "Day66",
        "Day67",
        "Day68",
        "Day69",
        "Day70",
    ]


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


def test_ai_intent_reviewer_route_exposes_day57_to_day82_without_execution(tmp_path):
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
    assert "Day68" in text
    assert "Day69" in text
    assert "Day70" in text
    assert "Day71" in text
    assert "Day72" in text
    assert "Day73" in text
    assert "Day74" in text
    assert "Day75" in text
    assert "Day76" in text
    assert "Day77" in text
    assert "Day78" in text
    assert "Day79" in text
    assert "Day80" in text
    assert "Day81" in text
    assert "Day82" in text
    assert "Day63 Traceability Evidence Map" in text
    assert "Day64 Reviewer Acceptance Runbook" in text
    assert "Day65 Acceptance Sign-off Package" in text
    assert "Day66 Offline Mock Runtime Skeleton" in text
    assert "Day67 - Offline Mock Runtime Contract &amp; Safety Invariant Validation" in text
    assert "Day68 - Reviewer Report Quality &amp; Evidence Trace Review" in text
    assert "Day69 Reviewer Evidence Drilldown" in text
    assert "Evidence chain: Day66 Offline Mock Runtime &rarr; Day67 Contract Validation / Safety Invariants &rarr; Day68 Reviewer Report Quality &rarr; Day69 Dashboard Evidence Drilldown" in text
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
    assert "docs/ai/intent_offline_mock_runtime_reviewer_report_quality.md" in text
    assert "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html" in text
    assert "docs/ai/intent_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md" in text
    assert "docs/roadmap/day69_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md" in text
    assert "Day70 AI Runtime Readiness Gate" in text
    assert "Day70 is a phase exit review for the Day66-Day69 offline mock runtime chain" in text
    assert "not AI runtime implementation" in text
    assert "Offline mock runtime exists" in text
    assert "Contract validation exists" in text
    assert "Reviewer quality review exists" in text
    assert "Dashboard evidence drilldown exists" in text
    assert "Live execution boundary documented" in text
    assert "Human review requirement documented" in text
    assert "AI runtime implementation started" in text
    assert "Voice integration started" in text
    assert "Device access enabled" in text
    assert "OpenAI API enabled" in text
    assert "PASS" in text
    assert "NOT STARTED" in text
    assert "NOT ENABLED" in text
    assert "Day70 is static, read-only, report-only, and reviewer-facing" in text
    assert "does not enable AI runtime, OpenAI API, voice, SSH, device access, live execution" in text
    assert "docs/ai/intent_offline_mock_runtime_phase_exit_review.md" in text
    assert "docs/roadmap/day70_offline_mock_runtime_phase_exit_ai_readiness_gate.md" in text
    assert "Day71 Controlled AI Runtime Prototype Entry Design" in text
    assert "Controlled AI runtime prototype entry design" in text
    assert "docs/ai/intent_controlled_ai_runtime_entry_design.md" in text
    assert "docs/roadmap/day71_controlled_ai_runtime_prototype_entry_design.md" in text
    assert "Day72 Controlled AI Runtime Input Contract Validator" in text
    assert "Controlled AI runtime input contract validator" in text
    assert "docs/ai/intent_controlled_ai_runtime_input_validator.md" in text
    assert "docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md" in text
    assert "validates structured intent payloads only" in text
    assert "execution_allowed</code> remains <code>false</code>" in text
    assert "validation-only and static from this dashboard" in text
    assert "no form, no POST route, no action endpoint" in text
    assert "Proposed Future Input Contract" in text
    assert "Proposed Future Output Contract" in text
    assert "Safety Gate Sequence" in text
    assert "Reviewer Evidence Mapping" in text
    assert "Day73 Mock AI Decision Pipeline" in text
    assert "deterministic mock decision stage after the Day72 validator" in text
    assert "DOCUMENTATION_ONLY" in text
    assert "REPORT_ONLY" in text
    assert "REVIEW_REQUIRED" in text
    assert "BLOCKED_LIVE_ACTION" in text
    assert "INVALID_INPUT_BLOCKED" in text
    assert "allowed_to_execute</code> remains <code>false</code>" in text
    assert "docs/ai/intent_mock_ai_decision_pipeline.md" in text
    assert "docs/roadmap/day73_mock_ai_decision_pipeline.md" in text
    assert "reports/lab-summary/day73_mock_ai_decision_pipeline.json" in text
    assert "reports/lab-summary/day73_mock_ai_decision_pipeline.html" in text
    assert "Day74 Controlled Dry-run Plan Builder" in text
    assert "dry-run plan previews" in text
    assert "DRY_RUN_READY" in text
    assert "dry_run_only</code> remains <code>true</code>" in text
    assert "docs/ai/intent_dry_run_plan_builder.md" in text
    assert "docs/roadmap/day74_dry_run_plan_builder.md" in text
    assert "reports/lab-summary/day74_dry_run_plan_builder.json" in text
    assert "reports/lab-summary/day74_dry_run_plan_builder.html" in text
    assert "Day75 Manual Review Approval Envelope" in text
    assert "manual review approval envelope" in text
    assert "approved_for_record_only" in text
    assert "rejected_for_review_gap" in text
    assert "requires_manual_follow_up" in text
    assert "blocked_live_action" in text
    assert "execution_unlock_supported</code> remains <code>false</code>" in text
    assert "docs/ai/intent_manual_review_approval_envelope.md" in text
    assert "docs/roadmap/day75_manual_review_approval_envelope.md" in text
    assert "reports/lab-summary/day75_manual_review_approval_envelope.json" in text
    assert "reports/lab-summary/day75_manual_review_approval_envelope.html" in text
    assert "Day76 Controlled Runtime Audit Trail" in text
    assert "controlled runtime audit trail" in text
    assert "REVIEW_READY" in text
    assert "BLOCKED_FOR_REVIEW" in text
    assert "EVIDENCE_GAP" in text
    assert "evidence_chain_complete</code> is <code>true</code>" in text
    assert "docs/ai/intent_runtime_audit_trail.md" in text
    assert "docs/roadmap/day76_runtime_audit_trail.md" in text
    assert "reports/lab-summary/day76_runtime_audit_trail.json" in text
    assert "reports/lab-summary/day76_runtime_audit_trail.html" in text
    assert "Day77 Runtime Safety Gate" in text
    assert "runtime safety gate" in text
    assert "LOCKED" in text
    assert "LOCKED_BY_POLICY" in text
    assert "docs/ai/intent_runtime_safety_gate.md" in text
    assert "docs/roadmap/day77_runtime_safety_gate.md" in text
    assert "reports/lab-summary/day77_runtime_safety_gate.json" in text
    assert "reports/lab-summary/day77_runtime_safety_gate.html" in text
    assert "Day78 Controlled Runtime Safety Case" in text
    assert "controlled runtime safety case" in text
    assert "REVIEW_ONLY" in text
    assert "docs/ai/intent_runtime_safety_case.md" in text
    assert "docs/roadmap/day78_runtime_safety_case.md" in text
    assert "reports/lab-summary/day78_runtime_safety_case.json" in text
    assert "reports/lab-summary/day78_runtime_safety_case.html" in text
    assert "Day79 Controlled Read-only Task Contract" in text
    assert "read-only task allowlist and capability definition layer" in text
    assert "READONLY_CONTRACT_READY" in text
    assert "BLOCKED_WRITE_ACTION" in text
    assert "BLOCKED_DESTRUCTIVE_ACTION" in text
    assert "docs/ai/intent_readonly_task_contract.md" in text
    assert "docs/roadmap/day79_readonly_task_contract.md" in text
    assert "reports/lab-summary/day79_readonly_task_contract.json" in text
    assert "reports/lab-summary/day79_readonly_task_contract.html" in text
    assert "no execution unlock" in text
    assert "no dashboard action surface" in text
    assert "Day80 Read-only Execution Broker Skeleton" in text
    assert "read-only broker skeleton" in text
    assert "MOCK_EXECUTION_REQUEST_PREPARED" in text
    assert "QUEUED_FOR_REVIEW" in text
    assert "REJECTED" in text
    assert "docs/ai/intent_readonly_execution_broker.md" in text
    assert "docs/roadmap/day80_readonly_execution_broker_skeleton.md" in text
    assert "reports/lab-summary/day80_readonly_execution_broker.json" in text
    assert "reports/lab-summary/day80_readonly_execution_broker.html" in text
    assert "live_command_allowed" in text
    assert "Day81" in text
    assert "broker review queue and decision state report" in text
    assert "review states and decision states" in text
    assert "docs/ai/intent_broker_review_queue.md" in text
    assert "docs/roadmap/day81_broker_review_queue.md" in text
    assert "reports/lab-summary/day81_broker_review_queue.json" in text
    assert "reports/lab-summary/day81_broker_review_queue.html" in text
    assert "dashboard_action_allowed" in text
    assert "Day82 Reviewer Decision Audit Summary / Queue Evidence Export" in text
    assert "docs/ai/intent_reviewer_decision_audit_summary.md" in text
    assert "docs/roadmap/day82_reviewer_decision_audit_summary.md" in text
    assert "reports/lab-summary/day82_reviewer_decision_audit_summary.json" in text
    assert "reports/lab-summary/day82_reviewer_decision_audit_summary.html" in text
    assert "network_change_allowed" in text
    assert "ai_runtime_allowed" in text
    assert "ai_intent_reviewer_controlled_runtime_entry" in text
    assert "execution_allowed=false" in text
    assert "api_integration_allowed=false" in text
    assert "voice_allowed=false" in text
    assert "device_access_allowed=false" in text
    assert "dashboard_action_surface_allowed=false" in text
    assert "user_intent_text" in text
    assert "requested_operation_type" in text
    assert "target_scope" in text
    assert "safety_level" in text
    assert "evidence_required" in text
    assert "reviewer_required" in text
    assert "normalized_intent" in text
    assert "mapped_category" in text
    assert "risk_level" in text
    assert "required_evidence" in text
    assert "reviewer_decision_required" in text
    assert "blocked_reason" in text
    assert "next_safe_step" in text
    assert "intent normalization" in text
    assert "task classification" in text
    assert "blocked-action screening" in text
    assert "offline mock validation" in text
    assert "explicit human confirmation" in text
    assert "STOPPED_BEFORE_EXECUTION" in text
    assert "Scenario Evidence Drilldown" in text
    assert "documentation_only" in text
    assert "report_only" in text
    assert "blocked_live_action" in text
    assert "needs_manual_review" in text
    assert "Decision: allowed_documentation_only" in text
    assert "Decision: allowed_report_only" in text
    assert "Decision: blocked" in text
    assert "Decision: manual_review_required" in text
    assert "Contract: PASS" in text
    assert "Review quality: REVIEW_READY" in text
    assert "Day66 mock_scenarios -&gt; Day67 contract validator -&gt; Day68 scenario_reviews" in text
    assert "Day69 is static/read-only/report-only" in text
    assert "reports/portfolio/day66_offline_mock_runtime_skeleton.json" in text
    assert "reports/portfolio/day67_offline_mock_runtime_contract.json" in text
    assert "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json" in text
    assert "reviewer-visible report quality" in text
    assert "contract validation proof" in text
    assert "no-device/network-change evidence" in text
    assert "Day68 is offline mock/report-only" in text
    assert "No OpenAI API calls" in text
    assert "No voice input" in text
    assert "No mapped runner task execution" in text
    assert "No SSH sessions" in text
    assert "No config.json requirement" in text
    assert "No automatic execution of mapped tasks from scenario examples" in text
    assert "Day66 mock runtime output is fixed offline evidence only" in text
    assert "Day69 presents reviewer evidence drilldown only" in text
    assert "Day72 validates controlled AI runtime input payloads only" in text
    assert "Day72 adds no OpenAI API, voice, SSH, device access, live execution, mapped task execution, config changes, forms, POST routes, or action endpoints" in text
    assert "Day73 runs deterministic mock decisions after Day72 validation only" in text
    assert "Day73 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard POST/action endpoint, or network configuration change" in text
    assert "Day74 converts Day73 mock decisions into dry-run plan previews only" in text
    assert "Day74 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, or network configuration change" in text
    assert "Day75 wraps Day74 dry-run plans in record-only reviewer sign-off envelopes" in text
    assert "Day75 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approval surface, execution control, approval unlock, or network configuration change" in text
    assert "Day76 links Day73 decisions, Day74 dry-run plans, and Day75 approval envelopes into reviewer audit evidence only" in text
    assert "Day76 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, or network configuration change" in text
    assert "Day77 links Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, and Day76 audit records into locked runtime safety gate evidence only" in text
    assert "Day77 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day78 links Day72 input validation, Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, Day76 audit records, and Day77 locked gates into end-to-end reviewer safety case evidence only" in text
    assert "Day78 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day79 defines the read-only task allowlist and capability definition layer after the Day72-Day78 runtime safety chain" in text
    assert "Day79 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day80 defines the read-only execution broker skeleton after the Day79 allowlist" in text
    assert "Day80 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day81 defines the read-only broker review queue and decision state report after Day80" in text
    assert "Day81 keeps allowed_to_execute false, dry_run_only true, execution_unlock_supported false, ssh_allowed false, device_connection_allowed false, live_command_allowed false, mapped_task_execution_allowed false, and dashboard_action_allowed false" in text
    assert "Day81 adds no OpenAI API, AI SDK, real AI runtime, voice, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day82 summarizes Day81 queue decisions into reviewer audit evidence exports only" in text
    assert "Day82 keeps allowed_to_execute false, dry_run_only true, execution_unlock_supported false, device_connection_allowed false, ssh_allowed false, live_command_allowed false, network_change_allowed false, ai_runtime_allowed false, and dashboard_action_allowed false" in text
    assert "Day82 adds no OpenAI API, AI SDK runtime, real AI runtime, voice, SSH, device access, live execution, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change" in text
    assert "Day83 marks future read-only executor adapter design readiness only" in text
    assert "Day84 defines the read-only executor adapter interface contract only" in text
    assert "Day85 remains Mock Adapter + Evidence Binding" in text
    assert "Compatibility Matrix is internal validation evidence only" in text
    assert "Day85 keeps every adapter record non-executing" in text
    assert "Day86 is a runner-level safety regression" in text
    assert "Day86 keeps allowed_to_execute false, ssh_allowed false, live_command_allowed false, mapped_task_executed false" in text
    assert "Day87 is a phase gate review" in text
    assert "Day87 keeps execution_allowed false, ssh_allowed false, live_command_allowed false, write_command_allowed false" in text
    assert "Day88 remains design-only" in text
    assert "Day88 is the Real Read-only Executor Adapter Design Draft only" in text
    assert "Day88 keeps execution_supported false, ssh_supported false, routeros_connection_supported false, live_command_supported false" in text
    assert "Day88 hands off to Day89 Real Adapter Safety Boundary Spec" in text
    assert "No mapped task was executed. This is a dry-run reviewer walkthrough only." in text
    html = text.lower()
    assert "<form" not in html
    assert "<button" not in html
    assert "method=\"post\"" not in html
    assert "method='post'" not in html
    assert "action=" not in html
    assert "fetch(" not in html
    assert "xmlhttprequest" not in html
    assert "run task" not in html
    assert "task trigger" not in html
    day79_section = html.split("<h2>day79 controlled read-only task contract", 1)[1]
    day79_section = day79_section.split("<section>", 1)[0]
    assert "<form" not in day79_section
    assert "<button" not in day79_section
    assert "method=\"post\"" not in day79_section
    assert "method='post'" not in day79_section
    assert "action=" not in day79_section
    assert "fetch(" not in day79_section
    assert "xmlhttprequest" not in day79_section
    assert "run task" not in day79_section
    assert "task trigger" not in day79_section
    day80_section = html.split("<h2>day80 read-only execution broker skeleton", 1)[1]
    day80_section = day80_section.split("<section>", 1)[0]
    assert "<form" not in day80_section
    assert "<button" not in day80_section
    assert "method=\"post\"" not in day80_section
    assert "method='post'" not in day80_section
    assert "action=" not in day80_section
    assert "fetch(" not in day80_section
    assert "xmlhttprequest" not in day80_section
    assert "run task" not in day80_section
    assert "task trigger" not in day80_section
    day81_section = html.split("<h2>day81 read-only broker review queue", 1)[1]
    day81_section = day81_section.split("<section>", 1)[0]
    assert "<form" not in day81_section
    assert "<button" not in day81_section
    assert "method=\"post\"" not in day81_section
    assert "method='post'" not in day81_section
    assert "action=" not in day81_section
    assert "fetch(" not in day81_section
    assert "xmlhttprequest" not in day81_section
    assert "run task" not in day81_section
    assert "task trigger" not in day81_section
    day82_section = html.split("<h2>day82 reviewer decision audit summary", 1)[1]
    day82_section = day82_section.split("<section>", 1)[0]
    assert "<form" not in day82_section
    assert "<button" not in day82_section
    assert "method=\"post\"" not in day82_section
    assert "method='post'" not in day82_section
    assert "action=" not in day82_section
    assert "fetch(" not in day82_section
    assert "xmlhttprequest" not in day82_section
    assert "run task" not in day82_section
    assert "task trigger" not in day82_section
    assert "execute intent" not in html
    assert "submit intent" not in html
    assert "execute buttons" not in html
    assert "post /" not in html
    assert "action runner" not in html
    assert "task runner endpoint" not in html
    assert "start task runner" not in html
    assert "openai api key" not in html

    ai_post_rules = [
        rule.rule
        for rule in app.url_map.iter_rules()
        if "POST" in rule.methods and ("ai" in rule.rule.lower() or "intent" in rule.rule.lower())
    ]
    assert ai_post_rules == []
    assert "live execution control" not in html
    assert "arbitrary command surface" not in html
    assert "ssh trigger" not in html
    assert "device access trigger" not in html
    assert "ai runtime trigger" not in html


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
