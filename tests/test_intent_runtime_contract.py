import ast
from copy import deepcopy
from pathlib import Path

import intent_offline_mock_runtime as runtime
import intent_runtime_contract as contract


UNSAFE_IMPORTS = {
    "jsonschema",
    "netmiko",
    "openai",
    "paramiko",
    "requests",
    "socket",
    "speech",
    "subprocess",
}


def valid_runtime_result():
    return deepcopy(runtime.run_mock_runtime()[0])


def blocked_runtime_result():
    return next(
        deepcopy(result)
        for result in runtime.run_mock_runtime()
        if result["safety_category"] == "blocked_live_action"
    )


def test_valid_day66_mock_runtime_output_passes_contract_validation():
    results = runtime.run_mock_runtime()

    assert contract.validate_runtime_results(results) == []
    assert all(contract.is_contract_valid(result) for result in results)


def test_missing_required_field_fails():
    result = valid_runtime_result()
    result.pop("scenario_id")

    errors = contract.validate_runtime_result(result)

    assert any("missing required field: scenario_id" in error for error in errors)


def test_invalid_execution_mode_fails():
    result = valid_runtime_result()
    result["execution_mode"] = "live"

    errors = contract.validate_runtime_result(result)

    assert any("execution_mode must be one of" in error for error in errors)


def test_live_execution_allowed_true_fails():
    result = valid_runtime_result()
    result["live_execution_allowed"] = True

    errors = contract.validate_runtime_result(result)

    assert "live_execution_allowed must always be False." in errors


def test_mapped_task_executed_true_fails():
    result = valid_runtime_result()
    result["mapped_task_executed"] = True

    errors = contract.validate_runtime_result(result)

    assert "mapped_task_executed must always be False." in errors


def test_blocked_live_action_without_warning_fails():
    result = blocked_runtime_result()
    result["reviewer_warning"] = ""

    errors = contract.validate_runtime_result(result)

    assert any("non-empty reviewer_warning" in error for error in errors)


def test_blocked_live_action_without_evidence_references_fails():
    result = blocked_runtime_result()
    result["evidence_references"] = []

    errors = contract.validate_runtime_result(result)

    assert any("at least one evidence reference" in error for error in errors)


def test_evidence_references_must_be_list_of_non_empty_strings():
    result = valid_runtime_result()
    result["evidence_references"] = ["docs/ai/example.md", "", 42]

    errors = contract.validate_runtime_result(result)

    assert any("evidence_references[1]" in error for error in errors)
    assert any("evidence_references[2]" in error for error in errors)

    result["evidence_references"] = "docs/ai/example.md"
    errors = contract.validate_runtime_result(result)

    assert any("evidence_references must be a list" in error for error in errors)


def test_forbidden_runtime_surfaces_fail_if_true():
    result = valid_runtime_result()
    result["ssh_used"] = True
    result["mock_execution_record"]["device_access_used"] = True

    errors = contract.validate_runtime_result(result)

    assert "ssh_used must not be True." in errors
    assert "mock_execution_record.device_access_used must not be True." in errors


def test_contract_validator_uses_only_standard_library_behavior():
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
    assert "config.json" not in source
    assert "network_lab" not in source
