import ast
import json
from pathlib import Path

import intent_runtime_safety_gate as gate


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
    "os",
}


def test_runtime_safety_gate_records_are_deterministic():
    first = gate.build_runtime_safety_gate_report()
    second = gate.build_runtime_safety_gate_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == gate.CREATED_AT
    assert {item["created_at"] for item in first["safety_gate_records"]} == {
        "2026-06-08T00:00:00+08:00"
    }


def test_runtime_safety_gate_records_link_full_day73_to_day76_chain():
    records = gate.build_runtime_safety_gate_records()

    assert len(records) == 5
    for record in records:
        scenario_id = record["scenario_id"]
        assert record["decision_id"] == f"day73-decision-{scenario_id}"
        assert record["dry_run_plan_id"] == f"day74-plan-{scenario_id}"
        assert record["approval_envelope_id"] == f"day75-envelope-{scenario_id}"
        assert record["audit_id"] == f"day76-audit-{scenario_id}"
        assert record["evidence_chain_complete"] is True


def test_runtime_safety_gate_evidence_chain_complete_calculates_missing_references():
    records = gate.build_runtime_safety_gate_records(audit_records=[])

    assert records
    assert {record["evidence_chain_complete"] for record in records} == {False}
    assert {record["gate_result"] for record in records} == {"EVIDENCE_GAP"}
    assert all(record["audit_id"] == "" for record in records)


def test_runtime_safety_gate_invariants_never_unlock_execution():
    report = gate.build_runtime_safety_gate_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["runtime_gate_state_values"] == ["LOCKED"]
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["runtime_gate_state_locked_all_records"] is True
    assert report["safety_invariants"]["gate_results_do_not_unlock_execution"] is True

    for record in report["safety_gate_records"]:
        assert record["runtime_gate_state"] == "LOCKED"
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["execution_policy"]["gate_effect"] == "locked_no_execution_unlock"
        assert record["execution_policy"]["allowed_actions"] == [
            "record_no_execution_gate_evidence"
        ]
        assert "unlock execution" in record["execution_policy"]["blocked_actions"]


def test_runtime_safety_gate_validation_flags_execution_unlock_attempts():
    records = gate.build_runtime_safety_gate_records()
    records[0]["runtime_gate_state"] = "UNLOCKED"
    records[0]["allowed_to_execute"] = True
    records[0]["execution_policy"]["gate_effect"] = "execute"

    errors = gate.validate_runtime_safety_gate_records(records)

    assert any("runtime_gate_state must be LOCKED" in error for error in errors)
    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("execution policy must keep the gate locked" in error for error in errors)


def test_runtime_safety_gate_module_does_not_introduce_unsafe_runtime_surfaces():
    source_path = Path(gate.__file__)
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
