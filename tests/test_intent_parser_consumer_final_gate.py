import ast
import json
from pathlib import Path

import intent_parser_consumer_final_gate as day110
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

## Standard Validation

```bash
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task <task-name>
```
"""


def write_agents(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(SAFE_AGENTS_TEXT, encoding="utf-8")
    return path


def ready_day109_report(**overrides):
    report = {
        "day": 109,
        "day_id": "Day109",
        "task": "parser-consumer-handoff-readiness-matrix",
        "overall_status": "PASS",
        "reviewer_status": "READY_FOR_REVIEW",
        "total_records": 1,
        "ready_count": 1,
        "needs_clarification_count": 0,
        "blocked_count": 0,
        "safety_summary": {
            "unsafe_flag_count": 0,
            "live_flag_count": 0,
            "ssh_flag_count": 0,
            "write_flag_count": 0,
            "command_execution_flag_count": 0,
            "mapped_task_execution_flag_count": 0,
            "blocking_condition_preserved": True,
        },
        "readiness_matrix": [
            {
                "record_id": "D110-T001",
                "consumer_name": "parser_contract_consumer",
                "handoff_status": "READY_FOR_REVIEW_HANDOFF",
                "readiness_status": "READY",
                "blocking_reasons": [],
                "clarification_items": [],
                "required_consumer_actions": ["Review report-only summary."],
                "evidence_refs": ["reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json"],
            }
        ],
        "validation_errors": [],
    }
    report.update(overrides)
    return report


def test_day110_default_report_locks_on_day109_blocked_records_and_shows_agents_pre_read(tmp_path):
    write_agents(tmp_path)

    report = day110.build_parser_consumer_final_gate_report(project_root=tmp_path)

    assert report["day"] == 110
    assert report["task"] == "parser-consumer-final-gate"
    assert report["overall_status"] == "PASS"
    assert report["final_gate_status"] == "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS"
    assert report["final_recommendation"] == "DO_NOT_ADVANCE_BLOCKED_RECORDS_PRESENT"
    assert report["next_phase_allowed"] is False
    assert "DAY109_BLOCKED_RECORDS_PRESENT" in report["gate_blockers"]
    assert report["agents_md_pre_read_evidence"]["agents_md_read_before_day110_work"] is True
    assert report["agents_md_pre_read_evidence"]["agents_md_pre_read_result"] == "PASS"
    assert report["validation_errors"] == []


def test_day110_all_ready_source_remains_review_only_and_does_not_unlock(tmp_path):
    write_agents(tmp_path)

    report = day110.build_parser_consumer_final_gate_report(
        ready_day109_report(),
        project_root=tmp_path,
    )

    assert report["final_gate_status"] == "FINAL_GATE_READY_FOR_REVIEW_ONLY_CONSUMER_USE"
    assert report["final_recommendation"] == "REVIEW_ONLY_CONSUMER_SUMMARY_READY"
    assert report["next_phase_allowed"] is False
    assert report["gate_blockers"] == []
    assert report["reviewer_decision_summary"]["ready_count"] == 1


def test_day110_needs_clarification_source_requires_reviewer_clarification(tmp_path):
    write_agents(tmp_path)
    source = ready_day109_report(
        reviewer_status="NEEDS_REVIEW",
        ready_count=0,
        needs_clarification_count=1,
        readiness_matrix=[
            {
                "record_id": "D110-T002",
                "handoff_status": "NEEDS_REVIEWER_CLARIFICATION",
                "readiness_status": "NEEDS_CLARIFICATION",
            }
        ],
    )

    report = day110.build_parser_consumer_final_gate_report(source, project_root=tmp_path)

    assert report["final_gate_status"] == "FINAL_GATE_REVIEWER_CLARIFICATION_REQUIRED"
    assert report["final_recommendation"] == "REVIEWER_CLARIFICATION_REQUIRED_BEFORE_CONSUMER_SIGNOFF"
    assert report["next_phase_allowed"] is False
    assert report["gate_blockers"] == ["DAY109_NEEDS_CLARIFICATION_RECORDS_PRESENT"]


def test_day110_missing_agents_pre_read_proof_fails_closed(tmp_path):
    write_agents(tmp_path)

    report = day110.build_parser_consumer_final_gate_report(
        ready_day109_report(),
        project_root=tmp_path,
        agents_md_pre_read=False,
    )

    assert report["overall_status"] == "FAIL"
    assert report["final_gate_status"] == "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS"
    assert report["next_phase_allowed"] is False
    assert report["agents_md_pre_read_evidence"]["agents_md_pre_read_result"] == "FAIL"
    assert "AGENTS_MD_PRE_READ_NOT_PROVEN" in report["gate_blockers"]
    assert "agents_md_pre_read_result must be PASS." in report["validation_errors"]


def test_day110_writer_outputs_json_and_html_with_agents_result(tmp_path):
    write_agents(tmp_path)
    report = day110.build_parser_consumer_final_gate_report(project_root=tmp_path)

    json_path, html_path = day110.write_parser_consumer_final_gate_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day110_parser_consumer_final_gate.json"
    assert html_path == tmp_path / "reports/lab-summary/day110_parser_consumer_final_gate.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day110 Parser Consumer Final Gate / Reviewer Decision Summary" in html
    assert "AGENTS.md Pre-read Evidence" in html
    assert "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS" in html
    assert "NO_LIVE_EXECUTION" in html
    assert "NO_SSH" in html
    assert "NO_WRITE" in html


def test_day110_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day110.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day110_runner_task_is_registered_and_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-consumer-final-gate")

    assert task["task_id"] == "day110_parser_consumer_final_gate"
    assert task["day"] == "Day110"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day110_parser_consumer_final_gate.json" in task["report_paths"]
    assert "docs/ai-intent/day110_parser_consumer_final_gate.md" in task["report_paths"]
    assert "agents_md_pre_read_result" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day110_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day110 final gate must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day110 final gate must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-consumer-final-gate"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day110 Parser Consumer Final Gate / Reviewer Decision Summary" in output
    assert "Task name: parser-consumer-final-gate" in output
    assert "Audit type: REPORT_ONLY" in output
    assert "final_gate_status: FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS" in output
    assert "next_phase_allowed: false" in output
    assert "agents_md_read_before_day110_work: true" in output
    assert "agents_md_pre_read_result: PASS" in output
    assert "JSON report: reports/lab-summary/day110_parser_consumer_final_gate.json" in output
    assert "HTML report: reports/lab-summary/day110_parser_consumer_final_gate.html" in output
    assert (tmp_path / "reports/lab-summary/day110_parser_consumer_final_gate.json").exists()
    assert (tmp_path / "reports/lab-summary/day110_parser_consumer_final_gate.html").exists()


def test_day110_report_index_visibility_includes_final_gate(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-final-gate"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Final Gate / Reviewer Decision Summary" in html
    assert "AGENTS.md pre-read result" in html
    assert "reports/lab-summary/day110_parser_consumer_final_gate.json" in html
    assert "reports/lab-summary/day110_parser_consumer_final_gate.html" in html
