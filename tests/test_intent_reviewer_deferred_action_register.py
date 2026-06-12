import ast
import json
from pathlib import Path

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


def test_day116_default_report_records_deferred_queue_without_advancement(tmp_path):
    write_agents(tmp_path)

    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)
    summary = report["register_summary"]

    assert report["overall_status"] == "PASS"
    assert report["status"] == "DEFERRED_ACTION_REGISTER_RECORDED"
    assert report["follow_up_queue_status"] == "FOLLOW_UP_QUEUE_RECORDED"
    assert report["day_range"] == "Day112-Day115"
    assert report["register_scope"] == "REVIEWER_DEFERRED_ACTIONS_ONLY"
    assert report["validation_errors"] == []
    assert summary["source_days_reviewed"] == 4
    assert summary["source_artifacts_reviewed"] == 4
    assert summary["deferred_item_count"] == 7
    assert summary["blocked_count"] == 4
    assert summary["hold_count"] == 1
    assert summary["do_not_advance_count"] == 2


def test_day116_source_trace_notes_include_day112_to_day115(tmp_path):
    write_agents(tmp_path)

    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)

    assert [note["source_day"] for note in report["source_trace_notes"]] == [
        "Day112",
        "Day113",
        "Day114",
        "Day115",
    ]
    for note in report["source_trace_notes"]:
        assert note["trace_id"]
        assert note["source_task"]
        assert note["source_artifacts"]["json"]
        assert note["source_artifacts"]["module"]
        assert note["trace_status"] == "SOURCE_REVIEWED_DEFERRED_ITEM_FOUND"


def test_day116_every_queue_item_has_required_traceability_and_false_flags(tmp_path):
    write_agents(tmp_path)

    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)

    for item in report["deferred_action_queue"]:
        assert item["origin_day"] in {112, 113, 114, 115}
        assert item["origin_task"]
        assert item["source_status"] in {
            "BLOCKED",
            "HOLD",
            "DO_NOT_ADVANCE",
            "NOT_ACCEPTABLE_SAFETY_BLOCKED",
        }
        assert item["source_artifact"]
        assert item["source_field"]
        assert item["source_value"]
        assert item["trace_note"] == "SOURCE_REVIEWED_DEFERRED_ITEM_FOUND"
        for flag in day116.FALSE_QUEUE_FLAGS:
            assert item[flag] is False


def test_day116_safety_flags_and_zero_counts_remain_fixed(tmp_path):
    write_agents(tmp_path)

    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)
    summary = report["register_summary"]

    for flag in day116.FALSE_QUEUE_FLAGS:
        assert report[flag] is False
        assert summary[flag] is False
    for count_name in day116.ZERO_SUMMARY_COUNTS:
        assert summary[count_name] == 0


def test_day116_status_does_not_use_readiness_wording(tmp_path):
    write_agents(tmp_path)

    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)

    for status in (report["status"], report["follow_up_queue_status"], report["register_summary"]["status"]):
        assert "READY" not in status.upper()
        assert "READINESS" not in status.upper()


def test_day116_fails_closed_if_any_queue_item_allows_execution(tmp_path):
    write_agents(tmp_path)
    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)
    report["deferred_action_queue"][0]["execution_allowed"] = True

    errors = day116.validate_reviewer_deferred_action_register_report(report)

    assert any("execution_allowed must be false" in error for error in errors)


def test_day116_writer_outputs_json_and_html(tmp_path):
    write_agents(tmp_path)
    report = day116.build_reviewer_deferred_action_register_report(project_root=tmp_path)

    json_path, html_path = day116.write_reviewer_deferred_action_register_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day116_reviewer_deferred_action_register.json"
    assert html_path == tmp_path / "reports/lab-summary/day116_reviewer_deferred_action_register.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day116 Reviewer Deferred Action Register / Blocked Follow-up Queue" in html
    assert "DEFERRED_ACTION_REGISTER_RECORDED" in html
    assert "FOLLOW_UP_QUEUE_RECORDED" in html


def test_day116_module_has_no_live_external_or_nondeterministic_imports_or_calls():
    tree = ast.parse(Path(day116.__file__).read_text(encoding="utf-8"))
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


def test_day116_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "reviewer-deferred-action-register"
    )

    assert task["task_id"] == "day116_reviewer_deferred_action_register"
    assert task["day"] == "Day116"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day116_reviewer_deferred_action_register.json" in task["report_paths"]
    assert "reports/lab-summary/day116_reviewer_deferred_action_register.html" in task["report_paths"]
    assert "docs/ai-intent/day116_reviewer_deferred_action_register.md" in task["report_paths"]
    assert "docs/roadmap/day116_reviewer_deferred_action_register.md" in task["report_paths"]
    assert "status=DEFERRED_ACTION_REGISTER_RECORDED" in task["notes"]
    assert "execution_allowed=false" in task["notes"]
    assert "broker_handoff_count=0" in task["notes"]


def test_day116_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day116 deferred action register must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day116 deferred action register must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "reviewer-deferred-action-register"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day116 Reviewer Deferred Action Register / Blocked Follow-up Queue" in output
    assert "overall_status: PASS" in output
    assert "status: DEFERRED_ACTION_REGISTER_RECORDED" in output
    assert "day_range: Day112-Day115" in output
    assert "register_scope: REVIEWER_DEFERRED_ACTIONS_ONLY" in output
    assert "source_days_reviewed: 4" in output
    assert "deferred_item_count: 7" in output
    assert "blocked_count: 4" in output
    assert "hold_count: 1" in output
    assert "do_not_advance_count: 2" in output
    assert "readiness_generated_count: 0" in output
    assert "execution_unlock_count: 0" in output
    assert "broker_handoff_count: 0" in output
    assert "runner_handoff_count: 0" in output
    assert "adapter_handoff_count: 0" in output
    assert "ssh_access_count: 0" in output
    assert "live_access_count: 0" in output
    assert "execution_allowed: false" in output
    assert "broker_allowed: false" in output
    assert "runner_allowed: false" in output
    assert "adapter_allowed: false" in output
    assert "ssh_allowed: false" in output
    assert "live_access_allowed: false" in output
    assert "readiness_generated: false" in output
    assert "next_stage_allowed: false" in output
    assert (tmp_path / "reports/lab-summary/day116_reviewer_deferred_action_register.json").exists()
    assert (tmp_path / "reports/lab-summary/day116_reviewer_deferred_action_register.html").exists()


def test_day116_report_index_visibility_includes_deferred_action_register(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "reviewer-deferred-action-register"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Reviewer Deferred Action Register / Blocked Follow-up Queue" in html
    assert "DEFERRED_ACTION_REGISTER_RECORDED" in html
    assert "reports/lab-summary/day116_reviewer_deferred_action_register.json" in html
    assert "reports/lab-summary/day116_reviewer_deferred_action_register.html" in html
