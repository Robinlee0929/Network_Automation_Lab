import ast
import json
from pathlib import Path

import intent_real_readonly_executor_adapter_design as day88


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


def test_day88_design_report_is_deterministic_and_design_only():
    first = day88.build_real_readonly_executor_adapter_design_report()
    second = day88.build_real_readonly_executor_adapter_design_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 88
    assert first["title"] == "Real Read-only Executor Adapter Design Draft"
    assert first["overall_status"] == "PASS"
    assert first["phase_state"] == "DESIGN_ONLY"
    assert first["day87_transition"]["day87_redone"] is False
    assert first["day89_handoff"] == "Real Adapter Safety Boundary Spec"


def test_day88_required_execution_surfaces_remain_false():
    report = day88.build_real_readonly_executor_adapter_design_report()

    assert day88.validate_real_readonly_executor_adapter_design(report) == []
    for field in day88.REQUIRED_FALSE_FLAGS:
        assert report[field] is False
        assert report["safety_boundary"][field] is False

    assert report["adapter_design"]["connects_to_devices"] is False
    assert report["adapter_design"]["runs_commands"] is False
    assert report["safety_boundary"]["adapter_implementation_present"] is False
    assert report["safety_boundary"]["transport_implementation_present"] is False


def test_day88_command_allowlist_is_positive_and_deny_by_default():
    report = day88.build_real_readonly_executor_adapter_design_report()
    allowlist = report["command_allowlist_design"]

    assert allowlist["policy_type"] == "positive_allowlist"
    assert allowlist["blacklist_based"] is False
    assert allowlist["normalization_required"] is True
    assert allowlist["deny_by_default"] is True
    assert allowlist["dashboard_direct_command_input_supported"] is False
    assert allowlist["reviewer_approval_envelope_required_for_future_use"] is True
    assert {item["execution_enabled"] for item in allowlist["commands"]} == {False}
    assert "/system/resource/print" in allowlist["normalized_commands"]
    assert "export" not in allowlist["normalized_commands"]


def test_day88_forbidden_policy_contains_mutation_tokens_and_export():
    report = day88.build_real_readonly_executor_adapter_design_report()
    tokens = set(report["forbidden_command_policy"]["tokens"])

    for token in day88.FORBIDDEN_MUTATION_TOKENS:
        assert token in tokens

    assert "export" in tokens
    assert report["forbidden_command_policy"]["deny_result"] == "MUTATION_TOKEN_DETECTED"
    assert report["forbidden_command_policy"]["unknown_command_result"] == "COMMAND_NOT_ALLOWLISTED"


def test_day88_evidence_error_and_timeout_contracts_are_non_runtime():
    report = day88.build_real_readonly_executor_adapter_design_report()

    evidence = report["evidence_contract"]
    assert evidence["stdout_collection_state"] == "NOT_COLLECTED_DESIGN_ONLY"
    assert evidence["raw_output_policy"] == "not_collected_in_day88_example_only"
    assert evidence["example_record"]["stdout_digest"] is None
    assert evidence["example_record"]["stderr_digest"] is None
    assert evidence["example_record"]["raw_output_redacted"] == "NOT_COLLECTED_DESIGN_ONLY_EXAMPLE_ONLY"
    assert evidence["example_record"]["error_code"] == "ADAPTER_NOT_IMPLEMENTED"

    assert "ADAPTER_NOT_IMPLEMENTED" in report["error_contract"]["codes"]
    assert report["error_contract"]["day88_current_error_code"] == "ADAPTER_NOT_IMPLEMENTED"
    assert report["error_contract"]["day88_current_state"] == "DESIGN_ONLY"
    assert report["timeout_contract"]["retry_supported"] is False
    assert report["timeout_contract"]["retry_count"] == 0


def test_day88_reports_are_written_without_action_controls(tmp_path):
    report = day88.build_real_readonly_executor_adapter_design_report()
    json_path, html_path = day88.write_real_readonly_executor_adapter_design_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day88_real_readonly_executor_adapter_design.json"
    assert html_path == tmp_path / "reports/lab-summary/day88_real_readonly_executor_adapter_design.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Real Read-only Executor Adapter Design Draft" in html
    assert "PASS / DESIGN_ONLY" in html
    assert "ADAPTER_NOT_IMPLEMENTED / DESIGN_ONLY" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day88_module_has_no_forbidden_runtime_imports_or_dependencies():
    source_path = Path(day88.__file__)
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
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
