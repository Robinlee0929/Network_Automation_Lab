import ast
from pathlib import Path

import intent_manual_review_approval_envelope as envelope


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
}


def test_day75_approval_envelopes_are_deterministic():
    first = envelope.build_approval_envelopes()
    second = envelope.build_approval_envelopes()

    assert first == second
    assert len(first) == 5
    assert {item["created_at"] for item in first} == {envelope.CREATED_AT}


def test_day75_approval_envelopes_have_required_fields_and_decisions():
    envelopes = envelope.build_approval_envelopes()
    decisions = {item["reviewer_decision"] for item in envelopes}

    assert decisions == {
        "approved_for_record_only",
        "rejected_for_review_gap",
        "requires_manual_follow_up",
        "blocked_live_action",
    }
    for item in envelopes:
        for field in envelope.REQUIRED_ENVELOPE_FIELDS:
            assert field in item, item["envelope_id"]
        assert item["required_review_items"]
        assert item["execution_policy"]["approval_effect"] == "record_only_no_execution_unlock"


def test_day75_invariants_never_unlock_execution():
    envelopes = envelope.build_approval_envelopes()

    assert all(item["allowed_to_execute"] is False for item in envelopes)
    assert all(item["dry_run_only"] is True for item in envelopes)
    assert all(item["execution_unlock_supported"] is False for item in envelopes)
    assert all(
        item["safety_invariants"]["allowed_to_execute"] is False for item in envelopes
    )
    assert all(item["safety_invariants"]["dry_run_only"] is True for item in envelopes)
    assert all(
        item["safety_invariants"]["execution_unlock_supported"] is False
        for item in envelopes
    )


def test_day75_reviewer_decisions_do_not_enable_execution():
    envelopes = envelope.build_approval_envelopes()

    by_decision = {item["reviewer_decision"]: item for item in envelopes}

    for decision in envelope.REVIEWER_DECISIONS:
        item = by_decision[decision]
        assert item["allowed_to_execute"] is False
        assert item["execution_unlock_supported"] is False
        assert item["execution_policy"]["allowed_actions"] == ["record_review_evidence"]
        assert "unlock execution" in item["execution_policy"]["blocked_actions"]


def test_day75_report_passes_safety_invariants():
    report = envelope.build_manual_review_approval_envelope_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["validation_errors"] == []
    assert report["summary"]["approval_envelope_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["approval_states_do_not_unlock_execution"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False


def test_day75_unsafe_imports_and_execution_surfaces_are_absent():
    source_path = Path(envelope.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)
    assert "subprocess.run" not in source
    assert "os.system" not in source
    assert "exec(" not in source
    assert "eval(" not in source
