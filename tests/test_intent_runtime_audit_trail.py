import json
from pathlib import Path

import intent_runtime_audit_trail as audit


def test_runtime_audit_records_are_deterministic():
    first = audit.build_runtime_audit_trail_report()
    second = audit.build_runtime_audit_trail_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_runtime_audit_records_link_decision_plan_and_approval_envelope():
    records = audit.build_runtime_audit_records()

    assert len(records) == 5
    for record in records:
        scenario_id = record["scenario_id"]
        assert record["decision_id"] == f"day73-decision-{scenario_id}"
        assert record["dry_run_plan_id"] == f"day74-plan-{scenario_id}"
        assert record["approval_envelope_id"] == f"day75-envelope-{scenario_id}"
        assert record["evidence_chain"]["day73_mock_ai_decision"]["present"] is True
        assert record["evidence_chain"]["day74_dry_run_plan"]["present"] is True
        assert record["evidence_chain"]["day75_approval_envelope"]["present"] is True
        assert record["evidence_chain_complete"] is True


def test_runtime_audit_evidence_chain_complete_calculates_missing_references():
    records = audit.build_runtime_audit_records(approval_envelopes=[])

    assert records
    assert {record["evidence_chain_complete"] for record in records} == {False}
    assert {record["audit_result"] for record in records} == {"EVIDENCE_GAP"}
    assert all(record["approval_envelope_id"] == "" for record in records)


def test_runtime_audit_safety_invariants_never_unlock_execution():
    report = audit.build_runtime_audit_trail_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["audit_results_do_not_unlock_execution"] is True

    for record in report["audit_records"]:
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["final_runtime_policy"]["review_effect"] == "evidence_only_no_execution_unlock"
        assert "unlock execution" in record["final_runtime_policy"]["blocked_actions"]


def test_runtime_audit_validation_flags_unknown_result():
    records = audit.build_runtime_audit_records()
    records[0]["audit_result"] = "EXECUTE"

    errors = audit.validate_runtime_audit_records(records)

    assert any("unknown audit_result" in error for error in errors)


def test_runtime_audit_module_does_not_introduce_unsafe_runtime_imports():
    source = Path("intent_runtime_audit_trail.py").read_text(encoding="utf-8")

    forbidden = [
        "import subprocess",
        "import paramiko",
        "import netmiko",
        "import requests",
        "import openai",
        "import socket",
        "from subprocess",
        "from paramiko",
        "from netmiko",
        "from requests",
        "from openai",
        "from socket",
    ]
    assert all(item not in source.lower() for item in forbidden)
