import ast
import json
from pathlib import Path

import intent_parser_classification_matrix as day98


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

REQUIRED_CLASSIFICATIONS = {
    "parsed_supported",
    "parsed_partial",
    "unsupported_format",
    "unsupported_command_family",
    "empty_output",
    "ambiguous_output",
    "parser_error_guarded",
}


def test_day98_matrix_contains_required_classification_categories():
    report = day98.build_parser_classification_matrix()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "TRACEABILITY_READY"
    assert report["summary"]["required_categories_present"] is True
    assert set(report["summary"]["classification_values"]) == REQUIRED_CLASSIFICATIONS
    assert report["validation_errors"] == []


def test_day98_rows_include_complete_reviewer_traceability_fields():
    report = day98.build_parser_classification_matrix()
    required_fields = {
        "case_id",
        "source_day",
        "input_label",
        "raw_output_sample",
        "parser_classification",
        "parsed_fields",
        "unsupported_reason",
        "reviewer_action",
        "safety_invariant",
        "executable_allowed",
        "evidence_required",
        "trace_status",
    }

    for row in report["matrix_rows"]:
        assert required_fields.issubset(row)
        assert row["source_day"] in {"Day96", "Day97"}
        assert row["parser_classification"] in REQUIRED_CLASSIFICATIONS
        assert isinstance(row["parsed_fields"], dict)
        assert row["reviewer_action"]
        assert row["safety_invariant"]
        assert row["evidence_required"]
        assert row["trace_status"] in {"TRACE_COMPLETE", "TRACE_REVIEW_REQUIRED"}
        assert row["fixture_origin"] == "day98_static_parser_traceability_sample"
        assert row["no_live_command_execution"] is True
        assert row["no_external_runtime_state"] is True


def test_day98_unsupported_rows_have_reasons_and_no_row_is_executable():
    report = day98.build_parser_classification_matrix()

    for row in report["matrix_rows"]:
        assert row["executable_allowed"] is False
        if row["parser_classification"] == "parsed_supported":
            assert row["unsupported_reason"] is None
        else:
            assert row["unsupported_reason"]

    assert report["summary"]["unsupported_reasons_complete"] is True
    assert report["summary"]["executable_allowed_count"] == 0
    assert report["summary"]["reviewer_action_missing_count"] == 0
    assert report["summary"]["safety_invariant_missing_count"] == 0
    assert report["summary"]["external_runtime_dependency_count"] == 0


def test_day98_reviewer_actions_are_deterministic():
    rows = day98.build_parser_classification_matrix()["matrix_rows"]
    expected_actions = {
        "parsed_supported": "review_parsed_fields",
        "parsed_partial": "review_missing_fields",
        "unsupported_format": "reject_and_attach_sample",
        "unsupported_command_family": "reject_out_of_scope",
        "empty_output": "request_new_sample",
        "ambiguous_output": "manual_review_required",
        "parser_error_guarded": "reject_until_parser_fixed",
    }

    for row in rows:
        assert row["reviewer_action"] == expected_actions[row["parser_classification"]]


def test_day98_safety_invariants_keep_runtime_disabled():
    report = day98.build_parser_classification_matrix()
    invariants = report["safety_invariants"]

    assert invariants["parser_output_is_not_executable"] is True
    assert invariants["unsupported_output_is_blocked"] is True
    assert invariants["unknown_output_requires_review"] is True
    assert invariants["parser_error_fails_closed"] is True
    assert invariants["reviewer_action_required_before_any_future_runtime_use"] is True
    assert invariants["executable_allowed"] is False
    assert invariants["live_read_allowed"] is False
    assert invariants["ssh_allowed"] is False
    assert invariants["routeros_execution_allowed"] is False
    assert invariants["device_contact_allowed"] is False
    assert invariants["command_execution_allowed"] is False
    assert invariants["approval_unlock_supported"] is False
    assert invariants["dashboard_action_allowed"] is False
    assert invariants["external_runtime_state_required"] is False


def test_day98_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day98.build_parser_classification_matrix()
    json_path, html_path = day98.write_parser_classification_matrix_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day98_parser_classification_matrix.json"
    assert html_path == tmp_path / "reports/ai/day98_parser_classification_matrix.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day98 Parser Classification Matrix" in html
    assert "input sample -&gt; parser classification" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day98_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day98.__file__)
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
