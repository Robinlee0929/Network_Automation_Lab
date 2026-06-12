import ast
import json
from pathlib import Path

import intent_reviewer_evidence_intake_outcome_ledger as day119
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

REQUIRED_LEDGER_FIELDS = {
    "evidence_id",
    "day118_requirement_id",
    "evidence_name",
    "expected_from",
    "intake_status",
    "gap_status",
    "deferred_reason",
    "follow_up_action",
    "reviewer_note",
    "safety_boundary_impact",
    "acceptance_impact",
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


def build_day119_report(tmp_path):
    write_agents(tmp_path)
    return day119.build_reviewer_evidence_intake_outcome_ledger_report(project_root=tmp_path)


def test_day119_default_report_records_multiple_day118_evidence_rows(tmp_path):
    report = build_day119_report(tmp_path)

    assert report["overall_status"] == "INTAKE_LEDGER_READY"
    assert report["status"] == "INTAKE_LEDGER_READY"
    assert report["source_day"] == 118
    assert report["source_record_count"] == 7
    assert report["ledger_record_count"] == 7
    assert len(report["evidence_intake_outcome_ledger"]) == 7
    assert report["final_recommendation"] == "REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION"
    assert report["validation_errors"] == []


def test_day119_every_ledger_row_has_required_fields_and_allowed_statuses(tmp_path):
    report = build_day119_report(tmp_path)

    for item in report["evidence_intake_outcome_ledger"]:
        assert REQUIRED_LEDGER_FIELDS <= set(item)
        assert item["intake_status"] in day119.ALLOWED_INTAKE_STATUSES
        assert item["gap_status"] in day119.ALLOWED_GAP_STATUSES
        assert item["source_task"] == "deferred-action-review-sequence-runbook"
        assert item["source_artifact"] == "reports/lab-summary/day118_deferred_action_review_sequence_runbook.json"
        assert item["day118_required_evidence"]


def test_day119_ledger_preserves_gap_and_safety_blocked_follow_up_visibility(tmp_path):
    report = build_day119_report(tmp_path)
    ledger = report["evidence_intake_outcome_ledger"]

    assert report["open_or_deferred_gap_count"] >= 1
    assert report["safety_blocked_gap_count"] >= 1
    assert any(item["gap_status"] == "OPEN_GAP" for item in ledger)
    assert any(item["gap_status"] == "DEFERRED_GAP" for item in ledger)
    assert any(item["gap_status"] == "CLARIFICATION_REQUIRED" for item in ledger)
    assert any(item["gap_status"] == "SAFETY_BLOCKED_GAP" for item in ledger)
    assert any(item["blocked_by_safety_boundary"] is True for item in ledger)


def test_day119_no_acceptance_signoff_safety_release_or_execution_flags(tmp_path):
    report = build_day119_report(tmp_path)

    for flag in day119.SUMMARY_FALSE_FLAGS:
        assert report[flag] is False
        assert report["safety_invariants"][flag] is False

    for item in report["evidence_intake_outcome_ledger"]:
        for flag in day119.ROW_FALSE_FLAGS:
            assert item[flag] is False


def test_day119_source_alignment_preserves_day118_expected_items(tmp_path):
    report = build_day119_report(tmp_path)
    source_records = report["source_day118_checklist"]
    ledger = report["evidence_intake_outcome_ledger"]

    assert [item["review_sequence"] for item in source_records] == list(range(1, 8))
    assert [item["source_review_sequence"] for item in ledger] == list(range(1, 8))
    assert [item["deferred_action_id"] for item in source_records] == [
        item["source_deferred_action_id"] for item in ledger
    ]


def test_day119_validation_rejects_unsupported_status_and_unsafe_flags(tmp_path):
    report = build_day119_report(tmp_path)
    report["evidence_intake_outcome_ledger"][0]["intake_status"] = "APPROVED"
    report["allowed_to_execute"] = True
    report["safety_invariants"]["allowed_to_execute"] = True

    errors = day119.validate_reviewer_evidence_intake_outcome_ledger_report(report)

    assert any("intake_status is not allowed" in error for error in errors)
    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("safety_invariants.allowed_to_execute must be false" in error for error in errors)


def test_day119_writer_outputs_json_and_html(tmp_path):
    report = build_day119_report(tmp_path)

    json_path, html_path = day119.write_reviewer_evidence_intake_outcome_ledger_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.json"
    assert html_path == tmp_path / "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day119 Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log" in html
    assert "REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "POST" not in html


def test_day119_docs_describe_review_only_no_acceptance_no_execution_unlock():
    ai_doc = Path("docs/ai-intent/day119_reviewer_evidence_intake_outcome_ledger.md").read_text(
        encoding="utf-8"
    )
    roadmap_doc = Path("docs/roadmap/day119_reviewer_evidence_intake_outcome_ledger.md").read_text(
        encoding="utf-8"
    )
    readme = Path("docs/ai-intent/README.md").read_text(encoding="utf-8")
    combined = "\n".join([ai_doc, roadmap_doc, readme])

    assert "Day119 records evidence intake outcomes" in ai_doc
    assert "does not judge acceptance" in combined
    assert "does not produce reviewer sign-off" in combined
    assert "does not unlock execution" in combined
    assert "Deferred evidence remains deferred" in combined
    assert "Day118 expected evidence items" in combined
    assert "REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION" in combined
    assert "adapter invocation" in combined
    assert "broker handoff" in combined
    assert "SSH" in combined


def test_day119_module_has_no_live_external_or_nondeterministic_imports_or_calls():
    tree = ast.parse(Path(day119.__file__).read_text(encoding="utf-8"))
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


def test_day119_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "reviewer-evidence-intake-outcome-ledger"
    )

    assert task["task_id"] == "day119_reviewer_evidence_intake_outcome_ledger"
    assert task["day"] == "Day119"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.json" in task["report_paths"]
    assert "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.html" in task["report_paths"]
    assert "docs/ai-intent/day119_reviewer_evidence_intake_outcome_ledger.md" in task["report_paths"]
    assert "docs/roadmap/day119_reviewer_evidence_intake_outcome_ledger.md" in task["report_paths"]
    assert "overall_status=INTAKE_LEDGER_READY" in task["notes"]
    assert "acceptance_decision_made=false" in task["notes"]
    assert "reviewer_signoff_made=false" in task["notes"]
    assert "safety_boundary_released=false" in task["notes"]
    assert "allowed_to_execute=false" in task["notes"]
    assert "adapter_invocation_allowed=false" in task["notes"]
    assert "broker_handoff_allowed=false" in task["notes"]


def test_day119_runner_and_alias_write_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day119 intake ledger must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day119 intake ledger must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "reviewer-evidence-intake-outcome-ledger"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day119 Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log" in output
    assert "overall_status: INTAKE_LEDGER_READY" in output
    assert "source_day: 118" in output
    assert "source_record_count: 7" in output
    assert "ledger_record_count: 7" in output
    assert "final_recommendation: REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION" in output
    assert "acceptance_decision_made: false" in output
    assert "reviewer_signoff_made: false" in output
    assert "safety_boundary_released: false" in output
    assert "allowed_to_execute: false" in output
    assert "ssh_allowed: false" in output
    assert "live_command_allowed: false" in output
    assert "adapter_invocation_allowed: false" in output
    assert "broker_handoff_allowed: false" in output
    assert "parser_capability_changed: false" in output
    assert (tmp_path / "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.json").exists()
    assert (tmp_path / "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.html").exists()

    assert network_lab.main(["--task", "deferred-evidence-collection-log"], project_root=tmp_path) == 0


def test_day119_report_index_visibility_includes_intake_outcome_ledger(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "reviewer-evidence-intake-outcome-ledger"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log" in html
    assert "INTAKE_LEDGER_READY" in html
    assert "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.json" in html
    assert "reports/lab-summary/day119_reviewer_evidence_intake_outcome_ledger.html" in html
