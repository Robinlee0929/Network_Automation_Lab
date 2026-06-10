import ast
import json
from pathlib import Path

import intent_parser_evidence_quality as day97
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

SAFETY_FLAGS = {
    "live_read_allowed",
    "ssh_allowed",
    "write_allowed",
    "command_execution_allowed",
    "raw_command_allowed",
    "device_contact_allowed",
    "approval_unlock_supported",
    "mapped_task_execution_allowed",
}


def test_day97_cases_are_static_fake_parser_cases():
    cases = day97.build_day97_parser_evidence_cases()

    assert len(cases) >= 14
    assert all(case["fixture_origin"] == "day97_static_fake_parser_case" for case in cases)
    assert all(case["is_static_fake_case"] is True for case in cases)
    assert {case["case_id"] for case in cases} >= {
        "D97-C01-empty-output",
        "D97-C02-whitespace-only-output",
        "D97-C03-unsupported-command-family",
        "D97-C04-unknown-adapter-source",
        "D97-C05-malformed-normalized-adapter-result",
        "D97-C06-missing-raw-output",
        "D97-C07-missing-command-family",
        "D97-C08-partial-output-headers-only",
        "D97-C09-mixed-supported-and-unsupported-sections",
        "D97-C10-supported-shape-missing-required-fields",
        "D97-C11-unexpected-encoding-characters",
        "D97-C12-repeated-duplicate-lines",
        "D97-C13-contradictory-parser-hints",
        "D97-C14-unsupported-not-failed-execution",
    }


def test_day97_cases_include_required_reviewer_evidence_fields():
    required_fields = {
        "case_id",
        "case_name",
        "input_source",
        "command_family",
        "raw_output_present",
        "parser_supported",
        "parser_status",
        "unsupported_reason",
        "evidence_quality",
        "reviewer_action",
        "safety_flags",
    }

    for case in day97.build_day97_parser_evidence_cases():
        assert required_fields.issubset(case)
        assert case["parser_status"] in {
            "PARSED",
            "UNSUPPORTED_OUTPUT",
            "INCOMPLETE_OUTPUT",
            "MALFORMED_INPUT",
            "EMPTY_OUTPUT",
            "AMBIGUOUS_OUTPUT",
        }
        assert case["evidence_quality"] in {"HIGH", "MEDIUM", "LOW", "NOT_APPLICABLE"}
        assert case["unsupported_reason"]
        assert case["reviewer_action"]


def test_day97_unsupported_and_degraded_outputs_are_classified_safely():
    cases = {case["case_id"]: case for case in day97.build_day97_parser_evidence_cases()}

    assert cases["D97-C01-empty-output"]["parser_status"] == "EMPTY_OUTPUT"
    assert cases["D97-C02-whitespace-only-output"]["parser_status"] == "EMPTY_OUTPUT"
    assert cases["D97-C03-unsupported-command-family"]["parser_status"] == "UNSUPPORTED_OUTPUT"
    assert cases["D97-C04-unknown-adapter-source"]["parser_status"] == "MALFORMED_INPUT"
    assert cases["D97-C05-malformed-normalized-adapter-result"]["parser_status"] == "MALFORMED_INPUT"
    assert cases["D97-C06-missing-raw-output"]["raw_output_present"] is False
    assert cases["D97-C06-missing-raw-output"]["parser_status"] == "MALFORMED_INPUT"
    assert cases["D97-C08-partial-output-headers-only"]["parser_status"] == "INCOMPLETE_OUTPUT"
    assert cases["D97-C09-mixed-supported-and-unsupported-sections"]["parser_status"] == "AMBIGUOUS_OUTPUT"
    assert cases["D97-C10-supported-shape-missing-required-fields"]["parser_status"] == "INCOMPLETE_OUTPUT"
    assert cases["D97-C13-contradictory-parser-hints"]["parser_status"] == "AMBIGUOUS_OUTPUT"
    assert cases["D97-C14-unsupported-not-failed-execution"]["parser_status"] == "UNSUPPORTED_OUTPUT"
    assert cases["D97-C14-unsupported-not-failed-execution"]["failed_execution_classification"] is False


def test_day97_safety_flags_are_always_false():
    report = day97.build_day97_parser_evidence_quality_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "HARDENED"
    assert report["summary"]["unsafe_flag_count"] == 0
    assert report["summary"]["failed_execution_count"] == 0
    assert report["validation_errors"] == []
    for case in report["scenario_cases"]:
        assert set(case["safety_flags"]) == SAFETY_FLAGS
        assert all(value is False for value in case["safety_flags"].values())
    for flag in SAFETY_FLAGS:
        assert report["safety_invariants"][flag] is False


def test_day97_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day97.build_day97_parser_evidence_quality_report()
    json_path, html_path = day97.write_day97_parser_evidence_quality_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day97_parser_evidence_quality_report.json"
    assert html_path == tmp_path / "reports/ai/day97_parser_evidence_quality_report.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day97 Parser Evidence Quality" in html
    assert "Unsupported parser output is not failed execution" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day97_runner_task_returns_pass_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day97 parser evidence quality must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day97 parser evidence quality must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-evidence-quality"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day97 Parser Evidence Quality" in output
    assert "Task name: parser-evidence-quality" in output
    assert "PASS / HARDENED" in output
    assert "Total cases: 14" in output
    assert "Parser-supported count: 2" in output
    assert "Unsupported/degraded count: 14" in output
    assert "Unsafe flag count: 0" in output
    assert "overall_status = PASS" in output
    assert "reviewer_status = HARDENED" in output
    assert "failed_execution_count = 0" in output
    assert "live_read_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "write_allowed = false" in output
    assert "command_execution_allowed = false" in output
    assert "approval_unlock_supported = false" in output
    assert "mapped_task_execution_allowed = false" in output
    assert "JSON report: reports/ai/day97_parser_evidence_quality_report.json" in output
    assert "HTML report: reports/ai/day97_parser_evidence_quality_report.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day97_report_index_visibility_includes_parser_evidence_quality(tmp_path):
    assert network_lab.main(["--task", "parser-evidence-quality"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Parser Evidence Quality" in html
    assert "static fake parser cases" in html
    assert "reports/ai/day97_parser_evidence_quality_report.json" in html
    assert "reports/ai/day97_parser_evidence_quality_report.html" in html
    assert "FAILED_EXECUTION" not in html


def test_day97_task_catalog_contains_parser_evidence_quality_metadata():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-evidence-quality")

    assert task["task_id"] == "day97_parser_evidence_quality"
    assert task["day"] == "Day97"
    assert task["display_name"] == "Day97 Parser Evidence Quality"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day97_parser_evidence_quality_report.json" in task["report_paths"]
    assert "reports/ai/day97_parser_evidence_quality_report.html" in task["report_paths"]
    assert "docs/ai/intent_parser_evidence_quality.md" in task["report_paths"]
    assert "unsupported output is classified" in task["notes"].lower()
    assert "live_read_allowed remains false" in task["notes"]
    assert "approval_unlock_supported remains false" in task["notes"]


def test_day97_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day97.__file__)
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
