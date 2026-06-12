import ast
import json
from pathlib import Path

import intent_deferred_action_review_sequence_runbook as day118
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


def build_day118_report(tmp_path):
    write_agents(tmp_path)
    return day118.build_deferred_action_review_sequence_runbook_report(project_root=tmp_path)


def test_day118_default_report_records_seven_item_intake_checklist(tmp_path):
    report = build_day118_report(tmp_path)

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "INTAKE_CHECKLIST_READY_REVIEW_ONLY"
    assert report["source_day"] == 117
    assert report["source_record_count"] == 7
    assert report["checklist_record_count"] == 7
    assert report["review_only"] is True
    assert report["non_advancing"] is True
    assert report["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
    assert report["next_stage_allowed"] is False
    assert report["readiness_transition_allowed"] is False
    assert report["execution_unlock_supported"] is False
    assert report["validation_errors"] == []


def test_day118_review_sequence_is_deterministic_and_covers_one_through_seven(tmp_path):
    first = build_day118_report(tmp_path)
    second = build_day118_report(tmp_path)

    assert [item["review_sequence"] for item in first["evidence_intake_checklist"]] == list(range(1, 8))
    assert [
        item["deferred_action_id"] for item in first["evidence_intake_checklist"]
    ] == [item["deferred_action_id"] for item in second["evidence_intake_checklist"]]


def test_day118_every_checklist_item_has_required_owner_follow_up_and_intake_fields(tmp_path):
    report = build_day118_report(tmp_path)

    for item in report["evidence_intake_checklist"]:
        assert item["deferred_action_id"].startswith("D116-")
        assert item["owner"]
        assert item["follow_up_type"]
        assert item["blocking_reason"]
        assert item["evidence_intake_question"]
        assert item["required_evidence"]
        assert item["acceptable_evidence_examples"]
        assert item["reject_or_defer_if"]
        assert item["reviewer_checkpoints"]
        assert item["completion_state"] == "PENDING_EVIDENCE_REVIEW"


def test_day118_all_execution_live_and_advancement_flags_remain_false(tmp_path):
    report = build_day118_report(tmp_path)

    for flag in day118.AGGREGATE_FALSE_FLAGS:
        assert report[flag] is False
        assert report["safety_invariants"][flag] is False

    for item in report["evidence_intake_checklist"]:
        for flag in day118.RECORD_FALSE_FLAGS:
            assert item[flag] is False


def test_day118_source_count_and_alignment_preserve_day117_records(tmp_path):
    report = build_day118_report(tmp_path)
    source_records = report["source_day117_records"]
    checklist = report["evidence_intake_checklist"]

    assert len(source_records) == 7
    assert len(checklist) == 7
    assert [item["deferred_id"] for item in source_records] == [
        item["deferred_action_id"] for item in checklist
    ]
    assert [item["review_sequence"] for item in source_records] == [
        item["review_sequence"] for item in checklist
    ]
    assert [item["owner_role"] for item in source_records] == [item["owner"] for item in checklist]
    assert [item["follow_up_type"] for item in source_records] == [
        item["follow_up_type"] for item in checklist
    ]


def test_day118_fails_closed_if_day117_source_count_is_not_seven(tmp_path):
    report = build_day118_report(tmp_path)
    day117_report = {
        **report,
        "follow_up_ownership_matrix": report["source_day117_records"][:6],
    }

    failed = day118.build_deferred_action_review_sequence_runbook_report(
        project_root=tmp_path,
        day117_report=day117_report,
    )

    assert failed["overall_status"] == "FAIL"
    assert failed["status"] == "DAY117_SOURCE_RECORD_COUNT_MISMATCH_REVIEW_REQUIRED"
    assert failed["source_record_count"] == 6
    assert failed["checklist_record_count"] == 6
    assert failed["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
    assert failed["execution_unlock_supported"] is False
    assert failed["next_stage_allowed"] is False


def test_day118_validation_rejects_any_unsafe_flag(tmp_path):
    report = build_day118_report(tmp_path)
    report["evidence_intake_checklist"][0]["allows_broker"] = True
    report["broker_allowed"] = True

    errors = day118.validate_deferred_action_review_sequence_runbook_report(report)

    assert any("allows_broker must be false" in error for error in errors)
    assert any("broker_allowed must be false" in error for error in errors)


def test_day118_writer_outputs_json_and_html(tmp_path):
    report = build_day118_report(tmp_path)

    json_path, html_path = day118.write_deferred_action_review_sequence_runbook_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day118_deferred_action_review_sequence_runbook.json"
    assert html_path == tmp_path / "reports/lab-summary/day118_deferred_action_review_sequence_runbook.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day118 Deferred Action Review Sequence Runbook / Evidence Intake Checklist" in html
    assert "REVIEW_ONLY_NON_ADVANCING" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "POST" not in html


def test_day118_docs_describe_review_only_non_advancing_no_execution_unlock():
    ai_doc = Path("docs/ai-intent/day118_deferred_action_review_sequence_runbook.md").read_text(
        encoding="utf-8"
    )
    roadmap_doc = Path("docs/roadmap/day118_deferred_action_review_sequence_runbook.md").read_text(
        encoding="utf-8"
    )
    readme = Path("docs/ai-intent/README.md").read_text(encoding="utf-8")
    combined = "\n".join([ai_doc, roadmap_doc, readme])

    assert "reviewer intake checklist extension of Day117" in ai_doc
    assert "seven Day117 deferred ownership matrix records" in combined
    assert "REVIEW_ONLY_NON_ADVANCING" in combined
    assert "not readiness" in combined
    assert "does not unlock execution" in combined
    assert "live device access" in combined
    assert "SSH" in combined
    assert "broker" in combined
    assert "adapter" in combined
    assert "mapped task execution" in combined


def test_day118_module_has_no_live_external_or_nondeterministic_imports_or_calls():
    tree = ast.parse(Path(day118.__file__).read_text(encoding="utf-8"))
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


def test_day118_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "deferred-action-review-sequence-runbook"
    )

    assert task["task_id"] == "day118_deferred_action_review_sequence_runbook"
    assert task["day"] == "Day118"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day118_deferred_action_review_sequence_runbook.json" in task["report_paths"]
    assert "reports/lab-summary/day118_deferred_action_review_sequence_runbook.html" in task["report_paths"]
    assert "docs/ai-intent/day118_deferred_action_review_sequence_runbook.md" in task["report_paths"]
    assert "docs/roadmap/day118_deferred_action_review_sequence_runbook.md" in task["report_paths"]
    assert "reviewer_status=INTAKE_CHECKLIST_READY_REVIEW_ONLY" in task["notes"]
    assert "source_record_count=7" in task["notes"]
    assert "checklist_record_count=7" in task["notes"]
    assert "execution_unlock_supported=false" in task["notes"]
    assert "mapped_task_execution_allowed=false" in task["notes"]


def test_day118_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day118 intake checklist must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day118 intake checklist must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "deferred-action-review-sequence-runbook"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day118 Deferred Action Review Sequence Runbook / Evidence Intake Checklist" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: INTAKE_CHECKLIST_READY_REVIEW_ONLY" in output
    assert "source_record_count: 7" in output
    assert "checklist_record_count: 7" in output
    assert "review_sequence: [1, 2, 3, 4, 5, 6, 7]" in output
    assert "final_recommendation: REVIEW_ONLY_NON_ADVANCING" in output
    assert "execution_unlock_supported: false" in output
    assert "next_stage_allowed: false" in output
    assert "readiness_transition_allowed: false" in output
    assert "broker_allowed: false" in output
    assert "runner_allowed: false" in output
    assert "adapter_allowed: false" in output
    assert "ssh_allowed: false" in output
    assert "live_access_allowed: false" in output
    assert "mapped_task_execution_allowed: false" in output
    assert "openai_api_allowed: false" in output
    assert "voice_runtime_allowed: false" in output
    assert "device_access_allowed: false" in output
    assert (tmp_path / "reports/lab-summary/day118_deferred_action_review_sequence_runbook.json").exists()
    assert (tmp_path / "reports/lab-summary/day118_deferred_action_review_sequence_runbook.html").exists()


def test_day118_report_index_visibility_includes_intake_checklist(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "deferred-action-review-sequence-runbook"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Deferred Action Review Sequence Runbook / Evidence Intake Checklist" in html
    assert "INTAKE_CHECKLIST_READY_REVIEW_ONLY" in html
    assert "reports/lab-summary/day118_deferred_action_review_sequence_runbook.json" in html
    assert "reports/lab-summary/day118_deferred_action_review_sequence_runbook.html" in html
