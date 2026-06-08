import ast
import json
from pathlib import Path

import intent_runtime_safety_case as safety_case


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
    "os",
}


def test_runtime_safety_case_records_are_deterministic():
    first = safety_case.build_runtime_safety_case_report()
    second = safety_case.build_runtime_safety_case_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == safety_case.CREATED_AT
    assert {item["created_at"] for item in first["safety_case_records"]} == {
        "2026-06-08T00:00:00Z"
    }


def test_runtime_safety_case_records_link_full_day72_to_day77_chain():
    records = safety_case.build_runtime_safety_case_records()

    assert len(records) == 5
    for record in records:
        scenario_id = record["scenario_id"]
        assert record["input_validation_id"] == f"day72-validation-{scenario_id}"
        assert record["decision_id"] == f"day73-decision-{scenario_id}"
        assert record["dry_run_plan_id"] == f"day74-plan-{scenario_id}"
        assert record["approval_envelope_id"] == f"day75-envelope-{scenario_id}"
        assert record["audit_id"] == f"day76-audit-{scenario_id}"
        assert record["gate_id"] == f"day77-gate-{scenario_id}"
        assert record["evidence_chain_complete"] is True


def test_runtime_safety_case_evidence_chain_complete_calculates_missing_references():
    records = safety_case.build_runtime_safety_case_records(gate_records=[])

    assert records
    assert {record["evidence_chain_complete"] for record in records} == {False}
    assert {record["safety_case_result"] for record in records} == {"EVIDENCE_GAP"}
    assert all(record["gate_id"] == "" for record in records)


def test_runtime_safety_case_invariants_never_unlock_execution():
    report = safety_case.build_runtime_safety_case_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["runtime_gate_state_values"] == ["LOCKED"]
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["final_recommendation_values"] == ["REVIEW_ONLY"]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["runtime_gate_state_locked_all_records"] is True
    assert report["safety_invariants"]["final_recommendation_review_only_all_records"] is True
    assert report["safety_invariants"]["safety_case_results_do_not_unlock_execution"] is True

    for record in report["safety_case_records"]:
        assert record["runtime_gate_state"] == "LOCKED"
        assert record["final_recommendation"] == "REVIEW_ONLY"
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["safety_case_result"] in {
            "REVIEW_READY",
            "LOCKED_BY_POLICY",
            "BLOCKED_FOR_REVIEW",
            "EVIDENCE_GAP",
        }
        assert record["safety_invariants"][
            "execution_unlock_supported_by_safety_case_result"
        ] is False


def test_runtime_safety_case_validation_flags_execution_unlock_attempts():
    records = safety_case.build_runtime_safety_case_records()
    records[0]["runtime_gate_state"] = "UNLOCKED"
    records[0]["final_recommendation"] = "EXECUTE"
    records[0]["allowed_to_execute"] = True
    records[0]["safety_invariants"]["execution_unlock_supported_by_safety_case_result"] = True

    errors = safety_case.validate_runtime_safety_case_records(records)

    assert any("runtime_gate_state must be LOCKED" in error for error in errors)
    assert any("final_recommendation must be REVIEW_ONLY" in error for error in errors)
    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("safety case result must not support execution unlock" in error for error in errors)


def test_runtime_safety_case_module_does_not_introduce_unsafe_runtime_surfaces():
    source_path = Path(safety_case.__file__)
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
