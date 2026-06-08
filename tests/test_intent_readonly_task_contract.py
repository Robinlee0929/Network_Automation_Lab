import ast
import json
from pathlib import Path

import intent_readonly_task_contract as contract


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
    "os",
}


def test_readonly_task_contract_report_is_deterministic():
    first = contract.build_readonly_task_contract_report()
    second = contract.build_readonly_task_contract_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == contract.CREATED_AT
    assert {item["created_at"] for item in first["contract_records"]} == {
        "2026-06-08T00:00:00Z"
    }


def test_readonly_task_contract_records_have_required_fields_and_invariants():
    report = contract.build_readonly_task_contract_report()
    records = report["contract_records"]

    assert len(records) == 5
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["readonly_eligible_values"] == [False, True]
    assert report["summary"]["execution_candidate_values"] == [False, True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]

    for record in records:
        assert set(contract.REQUIRED_CONTRACT_FIELDS).issubset(record)
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["safety_invariants"]["allowed_to_execute"] is False
        assert record["safety_invariants"]["dry_run_only"] is True
        assert record["safety_invariants"]["execution_unlock_supported"] is False


def test_readonly_eligible_candidate_never_allows_execution():
    records = contract.build_readonly_task_contract_records()
    candidate = next(record for record in records if record["readonly_eligible"] is True)

    assert candidate["requested_task"] == "show_interface_status"
    assert candidate["execution_candidate"] is True
    assert candidate["contract_result"] == "READONLY_CONTRACT_READY"
    assert candidate["allowed_to_execute"] is False


def test_blocked_destructive_unknown_and_manual_results_are_classified():
    rows = {
        record["requested_task"]: record
        for record in contract.build_readonly_task_contract_records()
    }

    assert rows["add_firewall_rule"]["contract_result"] == "BLOCKED_WRITE_ACTION"
    assert rows["factory_reset"]["contract_result"] == "BLOCKED_DESTRUCTIVE_ACTION"
    assert rows["unknown"]["contract_result"] == "UNKNOWN_TASK"
    assert rows["needs_manual_classification"]["contract_result"] == (
        "NEEDS_MANUAL_CLASSIFICATION"
    )
    assert rows["add_firewall_rule"]["readonly_eligible"] is False
    assert rows["factory_reset"]["execution_candidate"] is False
    assert rows["needs_manual_classification"]["requires_human_approval"] is True


def test_readonly_task_contract_validation_flags_unlock_attempts():
    records = contract.build_readonly_task_contract_records()
    records[0]["allowed_to_execute"] = True
    records[0]["dry_run_only"] = False
    records[0]["execution_unlock_supported"] = True
    records[0]["safety_invariants"]["execution_unlock_supported"] = True

    errors = contract.validate_readonly_task_contract_records(records)

    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("dry_run_only must be true" in error for error in errors)
    assert any("execution_unlock_supported must be false" in error for error in errors)
    assert any("invariant execution_unlock_supported must be false" in error for error in errors)


def test_readonly_task_contract_reports_are_written(tmp_path):
    report = contract.build_readonly_task_contract_report()
    json_path, html_path = contract.write_readonly_task_contract_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day79_readonly_task_contract.json"
    assert html_path == tmp_path / "reports/lab-summary/day79_readonly_task_contract.html"
    assert json_path.exists()
    assert html_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day79 Controlled Read-only Task Contract &amp; Allowlist" in html
    assert "BLOCKED_WRITE_ACTION" in html
    assert "BLOCKED_DESTRUCTIVE_ACTION" in html


def test_readonly_task_contract_module_does_not_introduce_unsafe_runtime_surfaces():
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
