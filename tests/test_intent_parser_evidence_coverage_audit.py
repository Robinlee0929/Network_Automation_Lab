import ast
import json
from pathlib import Path

import intent_parser_evidence_coverage_audit as day99
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "asyncssh",
    "routeros_api",
    "librouteros",
    "socket",
    "telnetlib",
    "subprocess",
    "openai",
}

REQUIRED_COVERAGE_AREAS = {
    "supported_key_value_parse",
    "supported_line_parse",
    "supported_table_parse",
    "unsupported_format",
    "unsupported_command_family",
    "empty_output",
    "malformed_input",
    "partial_output",
    "ambiguous_output",
    "degraded_duplicate_output",
    "encoding_anomaly",
    "parser_error_guarded",
    "classification_traceability",
}


def test_day99_report_returns_coverage_review_ready_with_allowed_gaps():
    report = day99.build_parser_evidence_coverage_audit_report()
    summary = report["summary"]

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "COVERAGE_REVIEW_READY"
    assert summary["required_coverage_areas_present"] is True
    assert summary["source_report_fail_count"] == 0
    assert summary["runtime_violation_count"] == 0
    assert summary["blocking_gap_count"] == 0
    assert summary["under_covered_allowed"] is True
    assert summary["under_covered_count"] >= 1
    assert summary["ready_for_day100_review"] is True
    assert report["validation_errors"] == []


def test_day99_coverage_rows_include_required_fields_and_static_sources():
    report = day99.build_parser_evidence_coverage_audit_report()
    required_fields = {
        "coverage_area",
        "source_days",
        "sample_refs",
        "observed_count",
        "minimum_expected",
        "coverage_status",
        "gap_note",
        "day100_readiness",
        "fixture_origin",
        "audit_mode",
        "report_only",
        "execution_allowed",
        "adapter_path_allowed",
        "broker_path_allowed",
        "ssh_allowed",
        "live_device_path_allowed",
    }

    assert {row["coverage_area"] for row in report["coverage_rows"]} == REQUIRED_COVERAGE_AREAS
    for row in report["coverage_rows"]:
        assert required_fields.issubset(row)
        assert row["source_days"]
        assert row["observed_count"] == len(row["sample_refs"])
        assert row["coverage_status"] in {"COVERED", "UNDER_COVERED"}
        assert row["day100_readiness"] in {"READY_FOR_DAY100", "REVIEW_IN_DAY100"}
        assert row["fixture_origin"] == "day99_static_day96_day98_report_audit"
        assert row["audit_mode"] == "report_only_coverage_audit"
        assert row["report_only"] is True
        assert row["execution_allowed"] is False
        assert row["adapter_path_allowed"] is False
        assert row["broker_path_allowed"] is False
        assert row["ssh_allowed"] is False
        assert row["live_device_path_allowed"] is False


def test_day99_sample_gap_register_is_non_blocking_day100_input():
    report = day99.build_parser_evidence_coverage_audit_report()
    gaps = report["sample_gap_register"]

    assert gaps
    assert {gap["gap_status"] for gap in gaps} == {"UNDER_COVERED"}
    assert all(gap["blocking_day99"] is False for gap in gaps)
    assert all(gap["day100_decision_needed"] is True for gap in gaps)
    assert {gap["coverage_area"] for gap in gaps} >= {
        "supported_table_parse",
        "degraded_duplicate_output",
        "encoding_anomaly",
    }
    assert report["phase_gate_readiness"]["next_day"] == "Day100"
    assert report["phase_gate_readiness"]["recommended_name"] == (
        "Parser Phase Gate Review / Readiness Decision"
    )
    assert report["phase_gate_readiness"]["ready_for_day100_review"] is True


def test_day99_safety_invariants_disable_runtime_paths():
    report = day99.build_parser_evidence_coverage_audit_report()
    invariants = report["safety_invariants"]

    assert invariants["report_only"] is True
    assert invariants["static_report_audit_only"] is True
    assert invariants["parser_capability_added"] is False
    assert invariants["phase_gate_decision_made"] is False
    for flag in day99.RUNTIME_DISABLED_FLAGS:
        assert invariants[flag] is False


def test_day99_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day99.build_parser_evidence_coverage_audit_report()
    json_path, html_path = day99.write_parser_evidence_coverage_audit_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day99_parser_evidence_coverage_audit.json"
    assert html_path == tmp_path / "reports/ai/day99_parser_evidence_coverage_audit.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day99 Parser Evidence Coverage / Sample Gap Audit" in html
    assert "COVERAGE_REVIEW_READY" in html
    assert "Sample Gap Audit" in html
    assert "UNDER_COVERED categories are allowed" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day99_runner_task_returns_pass_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day99 coverage audit must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day99 coverage audit must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-evidence-coverage-audit"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day99 Parser Evidence Coverage / Sample Gap Audit" in output
    assert "Task name: parser-evidence-coverage-audit" in output
    assert "PASS / COVERAGE_REVIEW_READY" in output
    assert "under_covered_allowed = true" in output
    assert "blocking_gap_count = 0" in output
    assert "runtime_violation_count = 0" in output
    assert "ready_for_day100_review = true" in output
    assert "execution_allowed = false" in output
    assert "adapter_path_allowed = false" in output
    assert "broker_path_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "live_device_path_allowed = false" in output
    assert "JSON report: reports/ai/day99_parser_evidence_coverage_audit.json" in output
    assert "HTML report: reports/ai/day99_parser_evidence_coverage_audit.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day99_report_index_visibility_includes_coverage_audit(tmp_path):
    assert network_lab.main(["--task", "parser-evidence-coverage-audit"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Parser Evidence Coverage / Sample Gap Audit" in html
    assert "coverage audit" in html
    assert "reports/ai/day99_parser_evidence_coverage_audit.json" in html
    assert "reports/ai/day99_parser_evidence_coverage_audit.html" in html


def test_day99_task_catalog_contains_coverage_audit_metadata():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-evidence-coverage-audit")

    assert task["task_id"] == "day99_parser_evidence_coverage_audit"
    assert task["day"] == "Day99"
    assert task["display_name"] == "Day99 Parser Evidence Coverage / Sample Gap Audit"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day99_parser_evidence_coverage_audit.json" in task["report_paths"]
    assert "reports/ai/day99_parser_evidence_coverage_audit.html" in task["report_paths"]
    assert "docs/ai-intent/day99_parser_evidence_coverage_audit.md" in task["report_paths"]
    assert "UNDER_COVERED" in task["notes"]
    assert "Day100" in task["notes"]
    assert "adapter" in task["notes"].lower()
    assert "broker" in task["notes"].lower()


def test_day99_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day99.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    assert ".connect(" not in source
    assert ".send(" not in source
    assert ".recv(" not in source
    assert "subprocess." not in source
    assert "config.json" not in source
    assert "credential" not in source.lower()
    assert "password" not in source.lower()
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
