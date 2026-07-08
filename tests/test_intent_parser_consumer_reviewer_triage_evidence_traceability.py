import ast
import json
from pathlib import Path

import intent_parser_consumer_reviewer_triage_evidence_traceability as day114
import network_lab
from report_file_utils import path_exists, read_text_with_long_path


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


def test_day114_default_report_audits_traceability_without_execution(tmp_path):
    write_agents(tmp_path)

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)
    summary = report["traceability_summary"]

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "TRACEABILITY_AUDITED_NON_EXECUTABLE"
    assert report["source_day112_intake_linked"] is True
    assert report["source_day113_triage_linked"] is True
    assert report["blocked_records_preserved"] is True
    assert report["next_phase_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["validation_errors"] == []
    assert summary["missing_trace_count"] == 0
    assert summary["downgrade_detected_count"] == 0
    assert summary["execution_readiness_inferred_count"] == 0
    assert summary["next_phase_allowed_count"] == 0
    assert summary["unsafe_flag_count"] == 0


def test_day114_traceability_records_schema_is_complete(tmp_path):
    write_agents(tmp_path)

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)

    assert report["traceability_record_fields"] == list(day114.TRACEABILITY_RECORD_FIELDS)
    assert len(report["traceability_records"]) == 10
    for record in report["traceability_records"]:
        assert tuple(record.keys()) == day114.TRACEABILITY_RECORD_FIELDS
        assert record["source_day"] == "Day112"
        assert record["source_intake_id"]
        assert record["day113_outcome_id"].startswith("D113-L")
        assert record["preservation_status"] == "preserved"
        assert record["reviewer_visibility"] == "visible"
        assert record["downgrade_detected"] is False
        assert record["missing_trace_detected"] is False
        assert record["execution_readiness_inferred"] is False
        assert record["next_phase_allowed"] is False


def test_day114_every_day112_intake_source_links_to_day113_outcome(tmp_path):
    write_agents(tmp_path)

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)
    source_ids = {record["source_intake_id"] for record in report["traceability_records"]}
    linked_outcomes = {record["day113_outcome_id"] for record in report["traceability_records"]}

    assert source_ids == set(day114.INTAKE_TO_OUTCOME_STAGE)
    assert report["traceability_summary"]["source_intake_record_count"] == 10
    assert report["traceability_summary"]["linked_day113_outcome_count"] == 10
    assert {"D113-L001", "D113-L003", "D113-L004", "D113-L005"} <= linked_outcomes


def test_day114_blocked_conditions_have_reason_evidence_and_preservation(tmp_path):
    write_agents(tmp_path)

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)
    blocked = [record for record in report["traceability_records"] if record["blocked_condition_id"]]

    assert len(blocked) == 4
    assert report["traceability_summary"]["blocked_condition_count"] == 4
    assert report["traceability_summary"]["preserved_blocked_record_count"] == 4
    for record in blocked:
        assert record["blocked_reason"] not in {"", "none"}
        assert record["evidence_status"] == "BLOCKED_EVIDENCE_VISIBLE_NON_EXECUTABLE"
        assert record["preservation_status"] == "preserved"
        assert record["reviewer_visibility"] == "visible"
        assert record["execution_readiness_inferred"] is False
        assert record["next_phase_allowed"] is False


def test_day114_all_safety_boundary_flags_remain_false(tmp_path):
    write_agents(tmp_path)

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)
    safety = report["safety_invariants"]

    for field in day114.FALSE_SAFETY_FLAGS:
        assert safety[field] is False
    for field in day114.TRUE_SAFETY_FLAGS:
        assert safety[field] is True


def test_day114_fails_closed_if_trace_link_is_missing(tmp_path):
    write_agents(tmp_path)
    source_day113 = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(
        project_root=tmp_path
    )
    day113_report = {
        "selected_reviewer_outcome": "HOLD_FOR_BLOCKED_RECORDS",
        "final_recommendation": "TRIAGE_OUTCOME_LOGGED_DO_NOT_ADVANCE",
        "triage_outcome_log": [
            {"entry_id": "D113-L001", "stage": "source_intake_received"},
            {"entry_id": "D113-L003", "stage": "blocked_condition_reviewed"},
            {"entry_id": "D113-L004", "stage": "triage_outcome_selected"},
        ],
    }

    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(
        project_root=tmp_path,
        day113_report=day113_report,
    )

    assert source_day113["traceability_summary"]["source_day113_task"] == "parser-consumer-reviewer-triage-decision-log"
    assert report["overall_status"] == "FAIL"
    assert report["next_phase_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["traceability_summary"]["missing_trace_count"] > 0
    assert "traceability_summary.missing_trace_count must be 0." in report["validation_errors"]


def test_day114_writer_outputs_json_and_html_traceability_audit(tmp_path):
    write_agents(tmp_path)
    report = day114.build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root=tmp_path)

    json_path, html_path = day114.write_parser_consumer_reviewer_triage_evidence_traceability_reports(
        tmp_path, report
    )

    assert json_path == tmp_path / "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.json"
    assert html_path == tmp_path / "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.html"
    assert json.loads(read_text_with_long_path(json_path, encoding="utf-8")) == report
    html = read_text_with_long_path(html_path, encoding="utf-8")
    assert "Day114 Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit" in html
    assert "Traceability Records" in html
    assert "NO_EXECUTION_READINESS_INFERRED" in html
    assert "NO_NEXT_PHASE_UNLOCK" in html
    assert "BLOCKED_RECORDS_PRESERVED" in html


def test_day114_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day114.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day114_runner_task_is_registered_and_report_only():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "parser-consumer-reviewer-triage-evidence-traceability"
    )

    assert task["task_id"] == "day114_parser_consumer_reviewer_triage_evidence_traceability"
    assert task["day"] == "Day114"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.json" in task["report_paths"]
    assert "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.html" in task["report_paths"]
    assert "docs/ai-intent/day114_parser_consumer_reviewer_triage_evidence_traceability.md" in task["report_paths"]
    assert "docs/ai-intent/reviewer/day114_parser_consumer_reviewer_triage_evidence_traceability.md" in task["report_paths"]
    assert "docs/roadmap/day114_parser_consumer_reviewer_triage_evidence_traceability.md" in task["report_paths"]
    assert "reviewer_status=TRACEABILITY_AUDITED_NON_EXECUTABLE" in task["notes"]
    assert "source_day112_intake_linked=true" in task["notes"]
    assert "source_day113_triage_linked=true" in task["notes"]
    assert "blocked_records_preserved=true" in task["notes"]
    assert "NO_EXECUTION_READINESS_INFERRED" in task["notes"]
    assert "NO_NEXT_PHASE_UNLOCK" in task["notes"]


def test_day114_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day114 traceability audit must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day114 traceability audit must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(
        ["--task", "parser-consumer-reviewer-triage-evidence-traceability"],
        project_root=tmp_path,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day114 Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: TRACEABILITY_AUDITED_NON_EXECUTABLE" in output
    assert "source_day112_intake_linked: true" in output
    assert "source_day113_triage_linked: true" in output
    assert "blocked_records_preserved: true" in output
    assert "missing_trace_count: 0" in output
    assert "downgrade_detected_count: 0" in output
    assert "execution_readiness_inferred_count: 0" in output
    assert "next_phase_allowed: false" in output
    assert "NO_EXECUTION_READINESS_INFERRED" in output
    assert "NO_NEXT_PHASE_UNLOCK" in output
    assert "BLOCKED_RECORDS_PRESERVED" in output
    assert path_exists(tmp_path / "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.json")
    assert path_exists(tmp_path / "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.html")


def test_day114_report_index_visibility_includes_traceability_audit(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-reviewer-triage-evidence-traceability"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit" in html
    assert "traceability" in html
    assert "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.json" in html
    assert "reports/lab-summary/day114_parser_consumer_reviewer_triage_evidence_traceability.html" in html
