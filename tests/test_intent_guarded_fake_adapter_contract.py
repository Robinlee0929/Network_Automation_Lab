import ast
import json
from pathlib import Path

import intent_guarded_fake_adapter_contract as day93


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "routeros_api",
    "librouteros",
    "socket",
    "subprocess",
    "requests",
    "telnetlib",
    "asyncssh",
}


def test_day93_scenario_catalog_contains_allowed_and_rejected_cases():
    scenarios = day93.build_scenario_catalog()
    allowed = [scenario for scenario in scenarios if scenario.expected_guard_result == day93.ALLOWED]
    rejected = [scenario for scenario in scenarios if scenario.expected_guard_result == day93.REJECTED]

    assert {scenario.scenario_id for scenario in allowed} == {
        "readonly_show_identity",
        "readonly_show_interfaces",
        "readonly_export_terse",
    }
    assert {scenario.scenario_id for scenario in rejected} >= {
        "mutating_set_ip_address",
        "mutating_disable_interface",
        "reboot_device",
        "reset_configuration",
        "live_ssh_command",
        "unknown_task",
    }
    assert allowed
    assert rejected


def test_day93_report_is_deterministic_and_passes_fake_only_contract():
    first = day93.run_guarded_fake_adapter_contract()
    second = day93.run_guarded_fake_adapter_contract()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 93
    assert first["task"] == "guarded-fake-adapter-contract"
    assert first["overall_status"] == "PASS"
    assert first["mode"] == "FAKE_ADAPTER_ONLY"
    assert first["allowed_count"] > 0
    assert first["rejected_count"] > 0
    assert first["fake_adapter_invocations"] == first["allowed_count"]
    assert first["rejected_adapter_invocations"] == 0
    assert first["real_adapter_invocations"] == 0
    assert first["guard_ordering_violations"] == 0
    assert first["safety_violations"] == 0
    assert first["audit_chain_complete"] is True
    assert first["adapter_boundary_verified"] is True
    assert first["final_recommendation"] == "KEEP_FAKE_ONLY"
    assert day93.validate_report(first) == []


def test_day93_allowed_scenarios_invoke_fake_adapter_exactly_once_each():
    report = day93.run_guarded_fake_adapter_contract()
    allowed = [
        record
        for record in report["scenario_records"]
        if record["guard_result"] == day93.ALLOWED
    ]

    assert len(report["adapter_invocation_evidence"]) == len(allowed)
    assert [record["invocation_id"] for record in allowed] == [
        f"day93-fake-invocation-{index:03d}"
        for index in range(1, len(allowed) + 1)
    ]
    for record in allowed:
        assert record["adapter_invocation_attempted"] is True
        assert record["adapter_boundary_entered"] is True
        assert record["fake_adapter_invoked"] is True
        assert record["adapter_type"] == "fake"
        assert record["real_adapter_invoked"] is False
        assert record["audit_chain_complete"] is True
        assert record["evidence_status"] == "PASS"


def test_day93_rejected_scenarios_never_enter_adapter_boundary():
    report = day93.run_guarded_fake_adapter_contract()
    rejected = [
        record
        for record in report["scenario_records"]
        if record["guard_result"] == day93.REJECTED
    ]

    assert rejected
    for record in rejected:
        assert record["adapter_invocation_attempted"] is False
        assert record["adapter_boundary_entered"] is False
        assert record["fake_adapter_invoked"] is False
        assert record["real_adapter_invoked"] is False
        assert record["invocation_id"] is None
        assert record["adapter_type"] is None
        assert record["audit_chain_complete"] is True
        assert record["evidence_status"] == "PASS"


def test_day93_safety_flags_are_locked_false_for_every_record():
    report = day93.run_guarded_fake_adapter_contract()

    for record in report["scenario_records"]:
        assert record["guard_evaluated_before_adapter"] is True
        assert record["real_adapter_invoked"] is False
        assert record["ssh_allowed"] is False
        assert record["device_access_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["side_effects_allowed"] is False


def test_day93_reports_are_written_without_action_controls(tmp_path):
    report = day93.run_guarded_fake_adapter_contract()
    json_path, html_path = day93.write_guarded_fake_adapter_contract_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day93_guarded_fake_adapter_contract.json"
    assert html_path == tmp_path / "reports/lab-summary/day93_guarded_fake_adapter_contract.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert data["overall_status"] == "PASS"
    assert data["mode"] == "FAKE_ADAPTER_ONLY"
    assert data["rejected_adapter_invocations"] == 0
    assert data["real_adapter_invocations"] == 0
    assert "Guarded Fake Adapter Contract" in html
    assert "FAKE_ADAPTER_ONLY" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day93_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day93.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    assert ".connect(" not in source
    assert ".send(" not in source
    assert ".recv(" not in source
    assert "subprocess." not in source
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
