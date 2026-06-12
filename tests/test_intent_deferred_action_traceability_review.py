import ast
import json
from copy import deepcopy
from pathlib import Path

import intent_deferred_action_traceability_review as day117
import intent_reviewer_deferred_action_register as day116
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "routeros_api",
    "openai",
    "requests",
    "httpx",
    "socket",
    "subprocess",
    "time",
    "datetime",
    "random",
    "uuid",
}

FORBIDDEN_CALL_NAMES = {
    "connect",
    "exec_command",
    "invoke",
    "handoff",
    "run",
    "check_call",
    "check_output",
    "Popen",
}

SAFE_AGENTS_TEXT = """# AGENTS.md

## Project

This repository is a Network Automation Lab for safe reviewer-visible validation.

## Core Safety Rules

- Do not perform live device access.
- Do not use SSH or real network-device commands.
- Do not execute configuration-changing commands.
- Preserve safety gates and no-execution proof.
- Report-only work remains report-only.
"""


def write_agents(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(SAFE_AGENTS_TEXT, encoding="utf-8")
    return path


def build_day117_report(tmp_path):
    write_agents(tmp_path)
    return day117.build_deferred_action_traceability_review_report(project_root=tmp_path)


def test_day117_default_report_records_seven_item_ownership_matrix(tmp_path):
    report = build_day117_report(tmp_path)
    summary = report["matrix_summary"]

    assert report["overall_status"] == "PASS"
    assert report["status"] == "DEFERRED_ACTION_TRACEABILITY_REVIEW_READY"
    assert report["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
    assert report["matrix_scope"] == "DAY116_DEFERRED_ACTION_TRACEABILITY_ONLY"
    assert report["source_day"] == "Day116"
    assert report["source_day116_deferred_item_count"] == 7
    assert report["validation_errors"] == []
    assert summary["total_deferred_items_reviewed"] == 7
    assert summary["ownership_matrix_status"] == "RECORDED"
    assert summary["traceability_status"] == "TRACEABLE_TO_DAY116"
    assert summary["review_sequence_count"] == 7
    assert summary["unsafe_flag_count"] == 0


def test_day117_every_matrix_item_has_required_ownership_follow_up_and_evidence_fields(tmp_path):
    report = build_day117_report(tmp_path)

    for item in report["follow_up_ownership_matrix"]:
        assert item["deferred_id"].startswith("D116-")
        assert item["source_day"] == "Day116"
        assert item["source_artifact"] == day116.REPORT_JSON.as_posix()
        assert item["deferred_summary"]
        assert item["owner_role"] in day117.ALLOWED_OWNER_ROLES
        assert item["follow_up_type"] in day117.ALLOWED_FOLLOW_UP_TYPES
        assert item["blocking_reason"]
        assert item["required_evidence"]
        assert item["closure_condition"]
        assert item["status"] == "DEFERRED_FOLLOW_UP_REVIEW_ONLY"


def test_day117_review_sequence_is_deterministic_and_covers_one_through_seven(tmp_path):
    first = build_day117_report(tmp_path)
    second = build_day117_report(tmp_path)

    assert [item["review_sequence"] for item in first["follow_up_ownership_matrix"]] == list(range(1, 8))
    assert [
        item["deferred_id"] for item in first["follow_up_ownership_matrix"]
    ] == [item["deferred_id"] for item in second["follow_up_ownership_matrix"]]


def test_day117_all_execution_and_advancement_flags_remain_false(tmp_path):
    report = build_day117_report(tmp_path)
    summary = report["matrix_summary"]

    for flag in day116.FALSE_QUEUE_FLAGS:
        assert report[flag] is False
        assert summary[flag] is False
    for item in report["follow_up_ownership_matrix"]:
        for flag in day116.FALSE_QUEUE_FLAGS:
            assert item[flag] is False


def test_day117_fails_closed_if_day116_source_count_is_not_seven(tmp_path):
    write_agents(tmp_path)
    day116_report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)
    day116_report["deferred_action_queue"] = day116_report["deferred_action_queue"][:6]

    report = day117.build_deferred_action_traceability_review_report(
        project_root=tmp_path,
        day116_report=day116_report,
    )

    assert report["overall_status"] == "FAIL"
    assert report["status"] == "DEFERRED_ITEM_COUNT_MISMATCH_REVIEW_REQUIRED"
    assert report["matrix_summary"]["total_deferred_items_reviewed"] == 6
    assert report["matrix_summary"]["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
    assert report["execution_allowed"] is False
    assert report["next_stage_allowed"] is False


def test_day117_fails_closed_if_any_matrix_item_allows_unsafe_flag(tmp_path):
    report = build_day117_report(tmp_path)
    report["follow_up_ownership_matrix"][0]["broker_allowed"] = True

    errors = day117.validate_deferred_action_traceability_review_report(report)

    assert any("broker_allowed must be false" in error for error in errors)


def test_day117_does_not_modify_or_downgrade_day116_deferred_decisions(tmp_path):
    write_agents(tmp_path)
    source = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)
    source_before = deepcopy(source["deferred_action_queue"])

    report = day117.build_deferred_action_traceability_review_report(
        project_root=tmp_path,
        day116_report=source,
    )

    assert source["deferred_action_queue"] == source_before
    assert [
        item["deferred_id"] for item in report["follow_up_ownership_matrix"]
    ] == [item["item_id"] for item in source_before]
    assert {item["source_item_status"] for item in report["follow_up_ownership_matrix"]} == {
        item["source_status"] for item in source_before
    }


def test_day117_writer_outputs_json_and_html(tmp_path):
    report = build_day117_report(tmp_path)

    json_path, html_path = day117.write_deferred_action_traceability_review_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day117_deferred_action_traceability_review.json"
    assert html_path == tmp_path / "reports/lab-summary/day117_deferred_action_traceability_review.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day117 Deferred Action Traceability Review / Follow-up Ownership Matrix" in html
    assert "REVIEW_ONLY_NON_ADVANCING" in html


def test_day117_module_has_no_live_external_or_nondeterministic_imports_or_calls():
    tree = ast.parse(Path(day117.__file__).read_text(encoding="utf-8"))
    imports = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                calls.add(function.id)
            elif isinstance(function, ast.Attribute):
                calls.add(function.attr)

    assert not (FORBIDDEN_IMPORTS & imports)
    assert not (FORBIDDEN_CALL_NAMES & calls)


def test_day117_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "deferred-action-traceability-review"
    )

    assert task["task_id"] == "day117_deferred_action_traceability_review"
    assert task["day"] == "Day117"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day117_deferred_action_traceability_review.json" in task["report_paths"]
    assert "reports/lab-summary/day117_deferred_action_traceability_review.html" in task["report_paths"]
    assert "docs/ai-intent/day117_deferred_action_traceability_review.md" in task["report_paths"]
    assert "docs/roadmap/day117_deferred_action_traceability_review.md" in task["report_paths"]
    assert "status=DEFERRED_ACTION_TRACEABILITY_REVIEW_READY" in task["notes"]
    assert "final_recommendation=REVIEW_ONLY_NON_ADVANCING" in task["notes"]
    assert "unsafe_flag_count=0" in task["notes"]
    assert "broker_allowed=false" in task["notes"]


def test_day117_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day117 traceability review must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day117 traceability review must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "deferred-action-traceability-review"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day117 Deferred Action Traceability Review / Follow-up Ownership Matrix" in output
    assert "overall_status: PASS" in output
    assert "status: DEFERRED_ACTION_TRACEABILITY_REVIEW_READY" in output
    assert "ownership_matrix_status: RECORDED" in output
    assert "traceability_status: TRACEABLE_TO_DAY116" in output
    assert "total_deferred_items_reviewed: 7" in output
    assert "review_sequence_count: 7" in output
    assert "unsafe_flag_count: 0" in output
    assert "execution_allowed: false" in output
    assert "broker_allowed: false" in output
    assert "runner_allowed: false" in output
    assert "adapter_allowed: false" in output
    assert "ssh_allowed: false" in output
    assert "live_access_allowed: false" in output
    assert "readiness_generated: false" in output
    assert "next_stage_allowed: false" in output
    assert "final_recommendation: REVIEW_ONLY_NON_ADVANCING" in output
    assert (tmp_path / "reports/lab-summary/day117_deferred_action_traceability_review.json").exists()
    assert (tmp_path / "reports/lab-summary/day117_deferred_action_traceability_review.html").exists()


def test_day117_report_index_visibility_includes_traceability_review(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "deferred-action-traceability-review"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Deferred Action Traceability Review / Follow-up Ownership Matrix" in html
    assert "DEFERRED_ACTION_TRACEABILITY_REVIEW_READY" in html
    assert "reports/lab-summary/day117_deferred_action_traceability_review.json" in html
    assert "reports/lab-summary/day117_deferred_action_traceability_review.html" in html
