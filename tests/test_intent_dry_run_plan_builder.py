import ast
from pathlib import Path

import intent_dry_run_plan_builder as builder


UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
}


def test_day74_builder_produces_expected_plans_and_statuses():
    plans = builder.build_dry_run_plans()
    statuses = {plan["plan_status"] for plan in plans}

    assert len(plans) == 5
    assert statuses == {
        "DRY_RUN_READY",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "INVALID_INPUT_BLOCKED",
    }


def test_day74_plan_records_have_required_fields():
    for plan in builder.build_dry_run_plans():
        for field in builder.REQUIRED_PLAN_FIELDS:
            assert field in plan, plan["plan_id"]
        assert plan["planned_steps"]
        assert plan["blocked_steps"]
        assert plan["reviewer_checks"]
        assert plan["safety_rationale"]
        assert plan["evidence"]
        assert plan["next_reviewer_action"]


def test_day74_allowed_to_execute_is_always_false_and_dry_run_only_is_true():
    plans = builder.build_dry_run_plans()

    assert all(plan["allowed_to_execute"] is False for plan in plans)
    assert all(plan["dry_run_only"] is True for plan in plans)


def test_day74_live_action_and_invalid_input_are_blocked():
    plans = {plan["source_scenario_id"]: plan for plan in builder.build_dry_run_plans()}

    live_action = plans["day73-live-action-blocked"]
    invalid_input = plans["day73-invalid-input"]

    assert live_action["decision_label"] == "BLOCKED_LIVE_ACTION"
    assert live_action["plan_status"] == "BLOCKED"
    assert any("live" in step.lower() for step in live_action["blocked_steps"])
    assert live_action["allowed_to_execute"] is False
    assert live_action["dry_run_only"] is True

    assert invalid_input["decision_label"] == "INVALID_INPUT_BLOCKED"
    assert invalid_input["plan_status"] == "INVALID_INPUT_BLOCKED"
    assert any("invalid input" in step.lower() for step in invalid_input["blocked_steps"])
    assert invalid_input["allowed_to_execute"] is False
    assert invalid_input["dry_run_only"] is True


def test_day74_review_required_plan_includes_reviewer_checks():
    plan = next(
        item
        for item in builder.build_dry_run_plans()
        if item["source_scenario_id"] == "day73-ambiguous-review"
    )

    assert plan["plan_status"] == "REVIEW_REQUIRED"
    assert plan["reviewer_checks"]
    assert any("clarify" in check.lower() for check in plan["reviewer_checks"])
    assert plan["allowed_to_execute"] is False
    assert plan["dry_run_only"] is True


def test_day74_documentation_and_report_only_are_preview_plans_only():
    plans = [
        item
        for item in builder.build_dry_run_plans()
        if item["decision_label"] in {"DOCUMENTATION_ONLY", "REPORT_ONLY"}
    ]

    assert len(plans) == 2
    assert all(plan["plan_status"] == "DRY_RUN_READY" for plan in plans)
    assert all(plan["allowed_to_execute"] is False for plan in plans)
    assert all(plan["dry_run_only"] is True for plan in plans)
    assert all("Execute mapped runner task." in plan["blocked_steps"] for plan in plans)


def test_day74_report_passes_safety_invariants():
    report = builder.build_dry_run_plan_builder_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["validation_errors"] == []
    assert report["summary"]["plan_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False


def test_day74_unsafe_imports_and_execution_surfaces_are_absent():
    source_path = Path(builder.__file__)
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
