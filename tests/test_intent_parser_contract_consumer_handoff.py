import ast
import json
from pathlib import Path

import intent_parser_contract_consumer_handoff as day108
import intent_parser_reviewer_evidence_contract as day107
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


def test_day108_report_generation_succeeds_and_references_day107_contract():
    report = day108.build_parser_contract_consumer_handoff_report()

    assert report["day"] == 108
    assert report["task"] == "parser-contract-consumer-handoff"
    assert report["audit_type"] == "REPORT_ONLY"
    assert report["consumer_schema_version"] == day108.CONSUMER_HANDOFF_SCHEMA_VERSION
    assert report["source_contract"]["source_contract"] == day108.SOURCE_CONTRACT
    assert report["source_contract"]["source_contract_version"] == day107.SCHEMA_VERSION
    assert report["source_contract"]["source_task"] == day107.TASK_NAME
    assert report["overall_status"] == "PASS"
    assert report["validation_errors"] == []


def test_day108_sample_handoff_records_include_required_fields():
    report = day108.build_parser_contract_consumer_handoff_report()

    assert report["handoff_records"]
    for record in report["handoff_records"]:
        for field in day108.REQUIRED_HANDOFF_FIELDS:
            assert field in record
        assert record["source_contract"] == day108.SOURCE_CONTRACT
        assert record["consumer_schema_version"] == day108.CONSUMER_HANDOFF_SCHEMA_VERSION


def test_day108_valid_day107_style_source_record_becomes_handoff_ready():
    source = day108.build_sample_day107_style_records()[0]

    record = day108.build_handoff_record_from_day107_style_record(source)

    assert record["reviewer_decision"] == day108.READY_FOR_REVIEW_HANDOFF
    assert record["evidence_status"] == "ACCEPTABLE_FOR_REVIEW_ONLY_HANDOFF"
    assert record["handoff_ready"] is True
    assert record["handoff_blockers"] == []
    assert record["consumer_validation"]["errors"] == []


def test_day108_unsupported_or_degraded_parser_outcomes_are_not_ready():
    clarification = day108.build_sample_day107_style_records()[1]
    unsupported = day108.build_sample_day107_style_records()[2]

    clarification_record = day108.build_handoff_record_from_day107_style_record(clarification)
    unsupported_record = day108.build_handoff_record_from_day107_style_record(unsupported)

    assert clarification_record["reviewer_decision"] == day108.NEEDS_REVIEWER_CLARIFICATION
    assert clarification_record["handoff_ready"] is False
    assert "REVIEWER_DECISION_NOT_READY" in clarification_record["handoff_blockers"]

    assert unsupported_record["reviewer_decision"] == day108.BLOCKED_UNSAFE_OR_UNSUPPORTED
    assert unsupported_record["handoff_ready"] is False
    assert "PARSER_UNSUPPORTED" in unsupported_record["handoff_blockers"]
    assert "SAFETY_FLAG_MAPPED_TASK_EXECUTION_REQUESTED" in unsupported_record["handoff_blockers"]


def test_day108_unsafe_flags_always_block_handoff():
    for flag in day108.BLOCKING_SAFETY_FLAG_FIELDS:
        source = day108.build_sample_day107_style_records()[0]
        source["safety_flags"] = day108.build_default_safety_flags(**{flag: True})

        record = day108.build_handoff_record_from_day107_style_record(source)

        assert record["reviewer_decision"] == day108.BLOCKED_UNSAFE_OR_UNSUPPORTED
        assert record["handoff_ready"] is False
        assert f"SAFETY_FLAG_{flag.upper()}" in record["handoff_blockers"]


def test_day108_missing_source_contract_version_blocks_handoff():
    source = day108.build_sample_day107_style_records()[0]
    source["source_contract_version"] = ""

    record = day108.build_handoff_record_from_day107_style_record(source)

    assert record["handoff_ready"] is False
    assert "MISSING_SOURCE_CONTRACT_VERSION" in record["handoff_blockers"]
    assert "source_contract_version must be non-empty." in record["consumer_validation"]["errors"]


def test_day108_invalid_reviewer_decision_enum_blocks_handoff():
    source = day108.build_sample_day107_style_records()[0]
    source["reviewer_decision"] = "APPROVE_AND_EXECUTE"

    record = day108.build_handoff_record_from_day107_style_record(source)

    assert record["handoff_ready"] is False
    assert "INVALID_REVIEWER_DECISION" in record["handoff_blockers"]
    assert "reviewer_decision is outside the allowed enum." in record["consumer_validation"]["errors"]


def test_day108_safety_invariants_keep_all_execution_and_unlock_flags_closed():
    report = day108.build_parser_contract_consumer_handoff_report()
    invariants = report["safety_invariants"]

    assert invariants["report_only"] is True
    assert invariants["dry_run_only"] is True
    for flag in (
        "live_execution_allowed",
        "ssh_allowed",
        "device_connection_allowed",
        "command_execution_allowed",
        "write_or_config_change_allowed",
        "approval_unlock_supported",
        "mapped_task_execution_allowed",
        "openai_api_used",
        "voice_input_used",
    ):
        assert invariants[flag] is False


def test_day108_output_is_deterministic_for_key_results():
    first = day108.build_parser_contract_consumer_handoff_report()
    second = day108.build_parser_contract_consumer_handoff_report()

    assert first["created_at"] == second["created_at"]
    assert first["summary"] == second["summary"]
    assert first["handoff_records"] == second["handoff_records"]
    assert first["validation_errors"] == second["validation_errors"]


def test_day108_report_writer_outputs_stable_json_and_html_paths(tmp_path):
    report = day108.build_parser_contract_consumer_handoff_report()

    json_path, html_path = day108.write_parser_contract_consumer_handoff_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day108_parser_contract_consumer_handoff.json"
    assert html_path == tmp_path / "reports/lab-summary/day108_parser_contract_consumer_handoff.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day108 Parser Contract Consumer / Reviewer Decision Handoff" in html
    assert "day107.parser_reviewer_evidence_contract" in html
    assert "reports/lab-summary/day108_parser_contract_consumer_handoff.json" in html


def test_day108_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day108.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day108_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks()
        if task["id"] == "parser-contract-consumer-handoff"
    )

    assert task["task_id"] == "day108_parser_contract_consumer_handoff"
    assert task["day"] == "Day108"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day108_parser_contract_consumer_handoff.json" in task["report_paths"]
    assert "docs/ai-intent/day108_parser_contract_consumer_handoff.md" in task["report_paths"]


def test_day108_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day108 parser contract consumer handoff must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day108 parser contract consumer handoff must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-contract-consumer-handoff"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day108 Parser Contract Consumer / Reviewer Decision Handoff" in output
    assert "Task name: parser-contract-consumer-handoff" in output
    assert "Audit type: REPORT_ONLY" in output
    assert "Source contract: day107.parser_reviewer_evidence_contract" in output
    assert "source_contract_version = day107.parser_reviewer_evidence_contract.v1" in output
    assert "handoff_ready_count = 1" in output
    assert "unsafe_flags_block_handoff = true" in output
    assert "live_execution_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "command_execution_allowed = false" in output
    assert "approval_unlock_supported = false" in output
    assert "mapped_task_execution_allowed = false" in output
    assert "JSON report: reports/lab-summary/day108_parser_contract_consumer_handoff.json" in output
    assert "HTML report: reports/lab-summary/day108_parser_contract_consumer_handoff.html" in output
    assert (tmp_path / "reports/lab-summary/day108_parser_contract_consumer_handoff.json").exists()
    assert (tmp_path / "reports/lab-summary/day108_parser_contract_consumer_handoff.html").exists()


def test_day108_report_index_visibility_includes_consumer_handoff(tmp_path):
    assert network_lab.main(["--task", "parser-contract-consumer-handoff"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Contract Consumer / Reviewer Decision Handoff" in html
    assert "CONSUMER_HANDOFF_READY_REPORT_ONLY" in html
    assert "reports/lab-summary/day108_parser_contract_consumer_handoff.json" in html
    assert "reports/lab-summary/day108_parser_contract_consumer_handoff.html" in html
