import ast
from pathlib import Path

import intent_mock_ai_decision_pipeline as pipeline


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
}


def test_day73_mock_pipeline_produces_expected_scenarios_and_labels():
    records = pipeline.run_mock_ai_decision_pipeline()
    labels = {record["decision_label"] for record in records}

    assert len(records) == 5
    assert labels == {
        "DOCUMENTATION_ONLY",
        "REPORT_ONLY",
        "REVIEW_REQUIRED",
        "BLOCKED_LIVE_ACTION",
        "INVALID_INPUT_BLOCKED",
    }


def test_day73_decision_records_have_required_fields():
    for record in pipeline.run_mock_ai_decision_pipeline():
        for field in pipeline.REQUIRED_DECISION_FIELDS:
            assert field in record, record["scenario_id"]
        assert record["evidence"]
        assert record["safety_rationale"]
        assert record["next_reviewer_action"]


def test_day73_allowed_to_execute_is_always_false():
    records = pipeline.run_mock_ai_decision_pipeline()

    assert all(record["allowed_to_execute"] is False for record in records)


def test_day73_live_action_and_invalid_input_are_blocked():
    records = {
        record["scenario_id"]: record for record in pipeline.run_mock_ai_decision_pipeline()
    }

    live_action = records["day73-live-action-blocked"]
    invalid_input = records["day73-invalid-input"]

    assert live_action["validator_status"] == "BLOCKED"
    assert live_action["decision_label"] == "BLOCKED_LIVE_ACTION"
    assert live_action["blocked_reason"]
    assert live_action["allowed_to_execute"] is False

    assert invalid_input["validator_status"] == "INVALID"
    assert invalid_input["decision_label"] == "INVALID_INPUT_BLOCKED"
    assert invalid_input["blocked_reason"]
    assert invalid_input["allowed_to_execute"] is False


def test_day73_ambiguous_input_requires_manual_review():
    record = next(
        item
        for item in pipeline.run_mock_ai_decision_pipeline()
        if item["scenario_id"] == "day73-ambiguous-review"
    )

    assert record["decision_label"] == "REVIEW_REQUIRED"
    assert record["requires_manual_review"] is True
    assert record["allowed_to_execute"] is False


def test_day73_documentation_and_report_only_do_not_execute():
    records = [
        item
        for item in pipeline.run_mock_ai_decision_pipeline()
        if item["decision_label"] in {"DOCUMENTATION_ONLY", "REPORT_ONLY"}
    ]

    assert len(records) == 2
    assert all(record["validator_status"] == "VALID" for record in records)
    assert all(record["allowed_to_execute"] is False for record in records)
    assert all(not record["blocked_reason"] for record in records)


def test_day73_report_passes_safety_invariants():
    report = pipeline.build_mock_ai_decision_pipeline_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["validation_errors"] == []
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False


def test_day73_unsafe_imports_and_execution_surfaces_are_absent():
    source_path = Path(pipeline.__file__)
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
