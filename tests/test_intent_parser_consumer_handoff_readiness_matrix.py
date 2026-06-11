import ast
import json
from pathlib import Path

import intent_parser_consumer_handoff_readiness_matrix as day109
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


def _ready_record(**overrides):
    record = {
        "record_id": "D109-T001",
        "consumer_name": "parser_contract_consumer",
        "handoff_status": "READY_FOR_REVIEW_HANDOFF",
        "required_consumer_actions": ("Review report-only handoff evidence.",),
        "evidence_refs": ("reports/lab-summary/day108_parser_contract_consumer_handoff.json",),
        "unsafe_flag": False,
        "live_flag": False,
        "ssh_flag": False,
        "write_flag": False,
        "command_execution_flag": False,
        "mapped_task_execution_flag": False,
    }
    record.update(overrides)
    return record


def test_day109_default_report_consumes_day108_records_and_classifies_all_statuses():
    report = day109.build_parser_consumer_handoff_readiness_matrix_report()

    assert report["day"] == 109
    assert report["task"] == "parser-consumer-handoff-readiness-matrix"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "BLOCKED_RECORDS_PRESENT"
    assert report["total_records"] == 3
    assert report["ready_count"] == 1
    assert report["needs_clarification_count"] == 1
    assert report["blocked_count"] == 1
    assert {row["readiness_status"] for row in report["readiness_matrix"]} == {
        "READY",
        "NEEDS_CLARIFICATION",
        "BLOCKED",
    }
    assert report["validation_errors"] == []


def test_day109_complete_safe_record_becomes_ready():
    row = day109.build_readiness_row_from_handoff_record(_ready_record())

    assert row.readiness_status == "READY"
    assert row.blocking_reasons == ()
    assert row.clarification_items == ()


def test_day109_unsafe_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(unsafe_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "UNSAFE_FLAG_SET" in row.blocking_reasons


def test_day109_live_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(live_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "LIVE_FLAG_SET" in row.blocking_reasons


def test_day109_ssh_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(ssh_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "SSH_FLAG_SET" in row.blocking_reasons


def test_day109_write_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(write_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "WRITE_FLAG_SET" in row.blocking_reasons


def test_day109_command_execution_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(command_execution_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "COMMAND_EXECUTION_FLAG_SET" in row.blocking_reasons


def test_day109_mapped_task_execution_flag_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(mapped_task_execution_flag=True))

    assert row.readiness_status == "BLOCKED"
    assert "MAPPED_TASK_EXECUTION_FLAG_SET" in row.blocking_reasons


def test_day109_missing_consumer_identity_blocks_row():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(consumer_name=""))

    assert row.readiness_status == "BLOCKED"
    assert "MISSING_CONSUMER_IDENTITY" in row.blocking_reasons


def test_day109_missing_evidence_refs_blocks_row_deterministically():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(evidence_refs=()))

    assert row.readiness_status == "BLOCKED"
    assert "MISSING_HANDOFF_EVIDENCE" in row.blocking_reasons


def test_day109_missing_required_consumer_actions_needs_clarification():
    row = day109.build_readiness_row_from_handoff_record(_ready_record(required_consumer_actions=()))

    assert row.readiness_status == "NEEDS_CLARIFICATION"
    assert row.blocking_reasons == ()
    assert "MISSING_REQUIRED_CONSUMER_ACTIONS" in row.clarification_items


def test_day109_blocked_rows_have_blocking_reasons():
    report = day109.build_parser_consumer_handoff_readiness_matrix_report(
        [_ready_record(unsafe_flag=True)]
    )

    row = report["readiness_matrix"][0]
    assert row["readiness_status"] == "BLOCKED"
    assert row["blocking_reasons"]


def test_day109_needs_clarification_rows_have_clarification_items():
    report = day109.build_parser_consumer_handoff_readiness_matrix_report(
        [_ready_record(required_consumer_actions=())]
    )

    row = report["readiness_matrix"][0]
    assert row["readiness_status"] == "NEEDS_CLARIFICATION"
    assert row["clarification_items"]


def test_day109_ready_rows_have_no_blockers_or_clarification_items():
    report = day109.build_parser_consumer_handoff_readiness_matrix_report([_ready_record()])

    row = report["readiness_matrix"][0]
    assert row["readiness_status"] == "READY"
    assert row["blocking_reasons"] == []
    assert row["clarification_items"] == []


def test_day109_json_report_safety_counts_are_correct():
    report = day109.build_parser_consumer_handoff_readiness_matrix_report(
        [
            _ready_record(record_id="D109-T001"),
            _ready_record(record_id="D109-T002", ssh_flag=True),
            _ready_record(record_id="D109-T003", mapped_task_execution_flag=True),
        ]
    )

    safety = report["safety_summary"]
    assert safety["unsafe_flag_count"] == 0
    assert safety["live_flag_count"] == 0
    assert safety["ssh_flag_count"] == 1
    assert safety["write_flag_count"] == 0
    assert safety["command_execution_flag_count"] == 0
    assert safety["mapped_task_execution_flag_count"] == 1
    assert safety["blocking_condition_preserved"] is True


def test_day109_report_writer_outputs_json_and_html(tmp_path):
    report = day109.build_parser_consumer_handoff_readiness_matrix_report()

    json_path, html_path = day109.write_parser_consumer_handoff_readiness_matrix_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json"
    assert html_path == tmp_path / "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day109 Parser Consumer Handoff Readiness Matrix" in html
    assert "READY" in html
    assert "NEEDS_CLARIFICATION" in html
    assert "BLOCKED" in html
    assert "REVIEW_ONLY" in html
    assert "NO_LIVE_EXECUTION" in html
    assert "NO_SSH" in html
    assert "NO_WRITE" in html


def test_day109_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day109.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day109_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks()
        if task["id"] == "parser-consumer-handoff-readiness-matrix"
    )

    assert task["task_id"] == "day109_parser_consumer_handoff_readiness_matrix"
    assert task["day"] == "Day109"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json" in task["report_paths"]
    assert "docs/ai-intent/day109_parser_consumer_handoff_readiness_matrix.md" in task["report_paths"]


def test_day109_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day109 readiness matrix must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day109 readiness matrix must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(
        ["--task", "parser-consumer-handoff-readiness-matrix"],
        project_root=tmp_path,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day109 Parser Consumer Handoff Readiness Matrix" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: BLOCKED_RECORDS_PRESENT" in output
    assert "total_records: 3" in output
    assert "ready_count: 1" in output
    assert "needs_clarification_count: 1" in output
    assert "blocked_count: 1" in output
    assert "mapped_task_execution_flag_count: 1" in output
    assert "blocking_condition_preserved: true" in output
    assert "JSON report: reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json" in output
    assert "HTML report: reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.html" in output
    assert (tmp_path / "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json").exists()
    assert (tmp_path / "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.html").exists()


def test_day109_report_index_visibility_includes_readiness_matrix(tmp_path):
    assert network_lab.main(["--task", "parser-consumer-handoff-readiness-matrix"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Handoff Readiness Matrix" in html
    assert "NO_LIVE_EXECUTION" in html
    assert "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json" in html
    assert "reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.html" in html
