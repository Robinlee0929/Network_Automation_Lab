import ast
from copy import deepcopy
import json
from pathlib import Path

import intent_readonly_executor_adapter_contract as contract


UNSAFE_IMPORTS = {
    "paramiko",
    "netmiko",
    "asyncssh",
    "socket",
    "telnetlib",
    "requests",
    "httpx",
    "openai",
    "subprocess",
    "os",
    "fabric",
    "scrapli",
}


def test_readonly_executor_adapter_contract_report_is_deterministic():
    first = contract.build_readonly_executor_adapter_contract_report()
    second = contract.build_readonly_executor_adapter_contract_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == contract.CREATED_AT
    assert first["overall_status"] == "PASS"
    assert first["reviewer_status"] == "REVIEW_READY"
    assert first["contract_state"] == contract.CONTRACT_STATE


def test_readonly_executor_adapter_contract_preserves_locked_safety_flags():
    report = contract.build_readonly_executor_adapter_contract_report()
    flags = report["adapter_safety_flags"]

    assert flags["read_only_only"] is True
    assert flags["dry_run_only"] is True
    assert flags["allowed_to_execute"] is False
    assert flags["ssh_allowed"] is False
    assert flags["device_access_allowed"] is False
    assert flags["live_command_allowed"] is False
    assert flags["approval_unlock_supported"] is False
    assert flags["execution_unlock_supported"] is False
    assert flags["ai_api_allowed"] is False
    assert flags["adapter_implementation_present"] is False

    for field in contract.REQUIRED_TRUE_FLAGS:
        assert flags[field] is True
        assert report["safety_invariants"][field] is True
    for field in contract.REQUIRED_FALSE_FLAGS:
        assert flags[field] is False
        assert report["safety_invariants"][field] is False


def test_no_ssh_device_live_command_or_unlock_capability_exists():
    report = contract.build_readonly_executor_adapter_contract_report()
    declaration = report["adapter_capability_declaration_shape"]

    assert declaration["supported_transports"] == ["none_contract_only"]
    assert declaration["runnable_entrypoint"] is None
    assert declaration["implementation_module"] is None
    assert declaration["safety_flags"]["ssh_allowed"] is False
    assert declaration["safety_flags"]["device_access_allowed"] is False
    assert declaration["safety_flags"]["live_command_allowed"] is False
    assert declaration["safety_flags"]["approval_unlock_supported"] is False
    assert declaration["safety_flags"]["execution_unlock_supported"] is False
    assert declaration["safety_flags"]["ai_api_allowed"] is False
    assert declaration["safety_flags"]["adapter_implementation_present"] is False


def test_request_and_response_shapes_are_contract_only():
    report = contract.build_readonly_executor_adapter_contract_report()
    request = report["adapter_request_shape"]
    response = report["adapter_response_shape"]

    assert contract.validate_adapter_request_shape(request) == []
    assert contract.validate_adapter_response_shape(response) == []
    assert request["target_scope"]["target_address"] is None
    assert request["target_scope"]["credentials_ref"] is None
    assert request["input_payload"]["command_text"] is None
    assert request["input_payload"]["raw_device_command"] is None
    assert response["execution_result"] is None
    assert response["commands_executed"] == []
    assert response["device_session"] is None


def test_contract_report_contains_day84_evidence_fields():
    report = contract.build_readonly_executor_adapter_contract_report()

    assert report["day"] == "Day84"
    assert report["task_name"] == "readonly-executor-adapter-contract"
    assert report["adapter_boundary"]["boundary_type"] == "contract_only_boundary"
    assert report["adapter_boundary"]["implements_executor"] is False
    assert report["adapter_boundary"]["implements_adapter"] is False
    assert report["validation_result_shape"]["status"] == "PASS"
    assert report["validation_errors"] == []
    assert report["summary"]["request_shape_count"] == 1
    assert report["summary"]["response_shape_count"] == 1
    assert report["summary"]["capability_declaration_count"] == 1
    assert report["summary"]["evidence_reference_count"] == 1
    assert report["summary"]["adapter_implementation_present_values"] == [False]
    assert "adapter_request_shape" in report["example_fixtures"]
    assert "adapter_response_shape" in report["example_fixtures"]
    traceability_text = json.dumps(report["traceability_map"], sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82", "Day83", "Day84"):
        assert day in traceability_text


def test_readonly_executor_adapter_contract_reports_are_written(tmp_path):
    report = contract.build_readonly_executor_adapter_contract_report()
    json_path, html_path = contract.write_readonly_executor_adapter_contract_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day84_readonly_executor_adapter_contract.json"
    assert html_path == tmp_path / "reports/lab-summary/day84_readonly_executor_adapter_contract.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day84 Read-only Executor Adapter Interface Contract" in html
    assert "Adapter implementation present values" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_contract_validation_rejects_unsafe_capability_declarations():
    declaration = contract.build_adapter_capability_declaration_shape()
    unsafe = deepcopy(declaration)
    unsafe["supported_transports"] = ["none_contract_only", "ssh"]
    unsafe["runnable_entrypoint"] = "adapters.readonly_executor.run"
    unsafe["implementation_module"] = "adapters.readonly_executor"
    unsafe["capability_kind"] = "runtime_adapter"
    unsafe["safety_flags"]["ssh_allowed"] = True
    unsafe["safety_flags"]["device_access_allowed"] = True
    unsafe["safety_flags"]["live_command_allowed"] = True
    unsafe["safety_flags"]["adapter_implementation_present"] = True

    errors = contract.validate_adapter_capability_declaration(unsafe)

    assert any("forbidden transports: ssh" in error for error in errors)
    assert any("runnable_entrypoint must stay null" in error for error in errors)
    assert any("implementation_module must stay null" in error for error in errors)
    assert any("capability_kind must be interface_contract_only" in error for error in errors)
    assert any("ssh_allowed must be false" in error for error in errors)
    assert any("device_access_allowed must be false" in error for error in errors)
    assert any("live_command_allowed must be false" in error for error in errors)
    assert any("adapter_implementation_present must be false" in error for error in errors)


def test_readonly_executor_adapter_contract_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(contract.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "subprocess.run" not in source
    assert "os.system" not in source
    assert "exec(" not in source
    assert "eval(" not in source
