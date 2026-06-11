import ast
import json
from pathlib import Path

import intent_parser_consumer_reviewer_triage_closure_summary as day115
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


REQUIRED_FALSE_FLAGS = (
    "next_phase_allowed",
    "execution_readiness_inferred",
    "readiness_inferred",
    "broker_handoff_allowed",
    "runner_execution_allowed",
    "adapter_access_allowed",
    "ssh_allowed",
    "live_access_allowed",
    "command_execution_allowed",
    "mapped_task_execution_allowed",
    "approval_unlock_allowed",
    "parser_capability_changed",
)


def write_agents(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(SAFE_AGENTS_TEXT, encoding="utf-8")
    return path


def test_day115_default_report_closes_chain_without_advancement(tmp_path):
    write_agents(tmp_path)

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)
    summary = report["closure_summary"]

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "TRIAGE_CLOSURE_AUDITED_NON_ADVANCING"
    assert report["closure_status"] == "CLOSED_WITH_BLOCKED_RECORDS_PRESERVED"
    assert report["final_recommendation"] == "DO_NOT_ADVANCE"
    assert report["triage_chain_conclusion"] == "TRIAGE_CHAIN_CLOSED_NON_ADVANCING"
    assert report["validation_errors"] == []
    assert summary["chain_days"] == ["Day112", "Day113", "Day114"]
    assert summary["day112_included"] is True
    assert summary["day113_included"] is True
    assert summary["day114_included"] is True
    assert summary["blocked_records_preserved"] is True
    assert summary["blocked_records_not_downgraded"] is True
    assert summary["downgraded_to_pass_count"] == 0
    assert summary["unsafe_flag_count"] == 0
    assert summary["next_phase_allowed"] is False
    assert summary["execution_readiness_inferred"] is False


def test_day115_all_execution_related_flags_remain_false(tmp_path):
    write_agents(tmp_path)

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)
    safety = report["safety_invariants"]

    for flag in REQUIRED_FALSE_FLAGS:
        assert report[flag] is False
    for flag in day115.EXECUTION_FALSE_FLAGS:
        assert safety[flag] is False
    for flag in day115.TRUE_SAFETY_FLAGS:
        assert safety[flag] is True


def test_day115_reviewer_chain_records_are_static_and_non_advancing(tmp_path):
    write_agents(tmp_path)

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)

    assert report["reviewer_chain"] == [
        {
            "day": "Day112",
            "role": "reviewer_intake",
            "status": "INTAKE_RECEIVED",
            "advancement_effect": "NONE",
        },
        {
            "day": "Day113",
            "role": "reviewer_triage",
            "status": "HOLD_DO_NOT_ADVANCE",
            "advancement_effect": "BLOCKS_ADVANCEMENT",
        },
        {
            "day": "Day114",
            "role": "traceability_blocked_record_preservation",
            "status": "BLOCKED_RECORDS_PRESERVED",
            "advancement_effect": "PRESERVES_BLOCK",
        },
    ]


def test_day115_blocked_records_remain_blocked_and_not_downgraded(tmp_path):
    write_agents(tmp_path)

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)
    blocked = report["blocked_record_closure_audit"]

    assert len(blocked) == 4
    for record in blocked:
        assert record["closure_record_status"] == "BLOCKED"
        assert record["blocked_record_preserved"] is True
        assert record["downgraded_to_pass"] is False
        assert record["source_evidence_status"] == "BLOCKED_EVIDENCE_VISIBLE_NON_EXECUTABLE"
        assert record["execution_readiness_inferred"] is False
        assert record["next_phase_allowed"] is False


def test_day115_evidence_markers_are_present(tmp_path):
    write_agents(tmp_path)

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)

    assert report["evidence_markers"] == list(day115.REQUIRED_EVIDENCE_MARKERS)
    for marker in (
        "NO_EXECUTION_READINESS_INFERRED",
        "NO_NEXT_PHASE_UNLOCK",
        "TRIAGE_CHAIN_CLOSED_NON_ADVANCING",
        "BLOCKED_RECORDS_PRESERVED",
        "BLOCKED_RECORDS_NOT_DOWNGRADED",
        "NO_BROKER_HANDOFF",
        "NO_RUNNER_EXECUTION",
        "NO_ADAPTER_ACCESS",
        "NO_SSH_ACCESS",
        "NO_LIVE_ACCESS",
        "NO_COMMAND_EXECUTION",
        "NO_MAPPED_TASK_EXECUTION",
        "NO_APPROVAL_UNLOCK",
    ):
        assert marker in report["evidence_markers"]


def test_day115_fails_closed_if_execution_flag_is_true(tmp_path):
    write_agents(tmp_path)
    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)

    report["safety_invariants"]["ssh_allowed"] = True

    errors = day115.validate_parser_consumer_reviewer_triage_closure_summary_report(report)

    assert "safety_invariants.ssh_allowed must be false." in errors


def test_day115_fails_closed_if_final_recommendation_changes(tmp_path):
    write_agents(tmp_path)
    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)

    report["final_recommendation"] = "ADVANCE"

    errors = day115.validate_parser_consumer_reviewer_triage_closure_summary_report(report)

    assert 'final_recommendation must be "DO_NOT_ADVANCE".' in errors


def test_day115_fails_closed_if_blocked_record_is_downgraded_to_pass(tmp_path):
    write_agents(tmp_path)
    source_day114 = day115.build_parser_consumer_reviewer_triage_closure_summary_report(
        project_root=tmp_path
    )
    day114_report = {
        "overall_status": "PASS",
        "traceability_status": "DAY112_DAY113_TRACEABILITY_COMPLETE",
        "blocked_records_preserved": True,
        "final_recommendation": "TRACEABILITY_AUDITED_DO_NOT_ADVANCE",
        "next_phase_allowed": False,
        "traceability_records": [
            {
                "trace_id": "D114-T001",
                "source_intake_id": "day109_blocked_records_preserved",
                "blocked_condition_id": "D114-BLOCKED-DAY109",
                "blocked_reason": "blocked record must remain blocked",
                "evidence_status": "PASS_EVIDENCE_VISIBLE_NON_EXECUTABLE",
                "preservation_status": "preserved",
            }
        ],
    }

    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(
        project_root=tmp_path,
        day114_report=day114_report,
    )

    assert source_day114["closure_summary"]["blocked_records_preserved"] is True
    assert report["overall_status"] == "FAIL"
    assert report["next_phase_allowed"] is False
    assert report["execution_readiness_inferred"] is False
    assert report["closure_summary"]["downgraded_to_pass_count"] == 1
    assert any("must not be downgraded" in error for error in report["validation_errors"])


def test_day115_writer_outputs_json_and_html_closure_summary(tmp_path):
    write_agents(tmp_path)
    report = day115.build_parser_consumer_reviewer_triage_closure_summary_report(project_root=tmp_path)

    json_path, html_path = day115.write_parser_consumer_reviewer_triage_closure_summary_reports(
        tmp_path, report
    )

    assert json_path == tmp_path / "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.json"
    assert html_path == tmp_path / "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day115 Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit" in html
    assert "TRIAGE_CHAIN_CLOSED_NON_ADVANCING" in html
    assert "NO_EXECUTION_READINESS_INFERRED" in html
    assert "NO_NEXT_PHASE_UNLOCK" in html


def test_day115_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day115.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day115_runner_task_is_registered_and_report_only():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "parser-consumer-reviewer-triage-closure-summary"
    )

    assert task["task_id"] == "day115_parser_consumer_reviewer_triage_closure_summary"
    assert task["day"] == "Day115"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.json" in task["report_paths"]
    assert "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.html" in task["report_paths"]
    assert "docs/ai-intent/day115_parser_consumer_reviewer_triage_closure_summary.md" in task["report_paths"]
    assert "docs/roadmap/day115_parser_consumer_reviewer_triage_closure_summary.md" in task["report_paths"]
    assert "reviewer_status=TRIAGE_CLOSURE_AUDITED_NON_ADVANCING" in task["notes"]
    assert "closure_status=CLOSED_WITH_BLOCKED_RECORDS_PRESERVED" in task["notes"]
    assert "final_recommendation=DO_NOT_ADVANCE" in task["notes"]
    assert "NO_NEXT_PHASE_UNLOCK" in task["notes"]


def test_day115_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day115 closure summary must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day115 closure summary must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(
        ["--task", "parser-consumer-reviewer-triage-closure-summary"],
        project_root=tmp_path,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day115 Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: TRIAGE_CLOSURE_AUDITED_NON_ADVANCING" in output
    assert "closure_status: CLOSED_WITH_BLOCKED_RECORDS_PRESERVED" in output
    assert "final_recommendation: DO_NOT_ADVANCE" in output
    assert "next_phase_allowed: false" in output
    assert "execution_readiness_inferred: false" in output
    assert "broker_handoff_allowed: false" in output
    assert "runner_execution_allowed: false" in output
    assert "adapter_access_allowed: false" in output
    assert "ssh_allowed: false" in output
    assert "live_access_allowed: false" in output
    assert "command_execution_allowed: false" in output
    assert "mapped_task_execution_allowed: false" in output
    assert "approval_unlock_allowed: false" in output
    assert "TRIAGE_CHAIN_CLOSED_NON_ADVANCING" in output
    assert "BLOCKED_RECORDS_NOT_DOWNGRADED" in output
    assert (tmp_path / "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.json").exists()
    assert (tmp_path / "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.html").exists()


def test_day115_report_index_visibility_includes_closure_summary(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-reviewer-triage-closure-summary"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit" in html
    assert "TRIAGE_CLOSURE_AUDITED_NON_ADVANCING" in html
    assert "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.json" in html
    assert "reports/lab-summary/day115_parser_consumer_reviewer_triage_closure_summary.html" in html
