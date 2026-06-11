import ast
import json
from pathlib import Path

import intent_parser_evidence_coverage_audit as day99
import intent_parser_phase_gate_review as day100
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


def test_day100_report_grades_parser_evidence_without_execution_authority():
    report = day100.build_parser_phase_gate_review_report()
    summary = report["summary"]

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "PHASE_GATE_REVIEW_READY"
    assert summary["final_readiness_decision"] == "UNDER_COVERED"
    assert summary["advance_ready_count"] >= 1
    assert summary["review_only_count"] >= 1
    assert summary["under_covered_count"] >= 1
    assert summary["blocked_count"] == 0
    assert summary["source_report_fail_count"] == 0
    assert summary["source_runtime_violation_count"] == 0
    assert summary["safety_violation_count"] == 0
    assert summary["parser_outputs_are_review_data_only"] is True
    assert report["validation_errors"] == []


def test_day100_decision_rows_include_all_required_classifications_and_locks():
    report = day100.build_parser_phase_gate_review_report()
    rows = report["decision_rows"]
    decisions = {row["readiness_decision"] for row in rows}

    assert {"ADVANCE_READY", "REVIEW_ONLY", "UNDER_COVERED"}.issubset(decisions)
    assert all(row["readiness_decision"] in day100.READINESS_DECISIONS for row in rows)
    assert all(row["next_action"] == day100.NEXT_ACTIONS[row["readiness_decision"]] for row in rows)
    assert all(row["review_data_only"] is True for row in rows)
    assert all(row["fixture_origin"] == "day100_static_day96_day99_phase_gate_review" for row in rows)
    assert all(row["review_mode"] == "readiness_decision_report_only" for row in rows)
    for row in rows:
        assert row["broker_boundary_allowed"] is False
        assert row["execution_allowed"] is False
        assert row["adapter_invocation_allowed"] is False
        assert row["executor_invocation_allowed"] is False
        assert row["ssh_allowed"] is False
        assert row["live_access_allowed"] is False


def test_day100_under_covered_and_blocked_decisions_are_deterministic():
    report = day100.build_parser_phase_gate_review_report()
    by_area = {row["evidence_area"]: row["readiness_decision"] for row in report["decision_rows"]}

    assert by_area["supported_key_value_parse"] == "ADVANCE_READY"
    assert by_area["supported_line_parse"] == "ADVANCE_READY"
    assert by_area["classification_traceability"] == "ADVANCE_READY"
    assert by_area["unsupported_command_family"] == "REVIEW_ONLY"
    assert by_area["ambiguous_output"] == "REVIEW_ONLY"
    assert by_area["parser_error_guarded"] == "REVIEW_ONLY"
    assert by_area["supported_table_parse"] == "UNDER_COVERED"

    unsafe_source = day99.build_parser_evidence_coverage_audit_report()
    unsafe_source["coverage_rows"][0]["execution_allowed"] = True
    blocked_report = day100.build_parser_phase_gate_review_report(unsafe_source)

    assert blocked_report["summary"]["final_readiness_decision"] == "BLOCKED"
    assert blocked_report["summary"]["blocked_count"] >= 1


def test_day100_safety_invariants_keep_parser_output_review_data_only():
    report = day100.build_parser_phase_gate_review_report()
    invariants = report["safety_invariants"]
    phase_gate = report["phase_gate_decision"]

    assert invariants["report_only"] is True
    assert invariants["static_phase_gate_review_only"] is True
    assert invariants["parser_output_is_authorization"] is False
    assert invariants["parser_capability_added"] is False
    assert invariants["broker_opened"] is False
    assert invariants["executor_opened"] is False
    for flag in day100.RUNTIME_DISABLED_FLAGS:
        assert invariants[flag] is False

    assert phase_gate["broker_boundary_allowed"] is False
    assert phase_gate["execution_allowed"] is False
    assert phase_gate["adapter_invocation_allowed"] is False
    assert phase_gate["executor_invocation_allowed"] is False
    assert phase_gate["ssh_allowed"] is False
    assert phase_gate["live_access_allowed"] is False
    assert phase_gate["parser_outputs_are_review_data_only"] is True


def test_day100_validator_rejects_any_unlocked_boundary_flag():
    report = day100.build_parser_phase_gate_review_report()
    report["decision_rows"][0]["broker_boundary_allowed"] = True

    errors = day100.validate_parser_phase_gate_review_report(report)

    assert any("broker_boundary_allowed must be false" in error for error in errors)


def test_day100_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day100.build_parser_phase_gate_review_report()
    json_path, html_path = day100.write_parser_phase_gate_review_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day100_parser_phase_gate_review.json"
    assert html_path == tmp_path / "reports/ai/day100_parser_phase_gate_review.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day100 Parser Phase Gate Review / Readiness Decision" in html
    assert "Final readiness decision" in html
    assert "UNDER_COVERED" in html
    assert "broker_boundary_allowed=false" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day100_runner_task_returns_pass_without_broker_executor_or_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day100 parser phase gate review must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day100 parser phase gate review must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-phase-gate-review"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day100 Parser Phase Gate Review / Readiness Decision" in output
    assert "Task name: parser-phase-gate-review" in output
    assert "PASS / PHASE_GATE_REVIEW_READY" in output
    assert "Final readiness decision: UNDER_COVERED" in output
    assert "ADVANCE_READY count:" in output
    assert "REVIEW_ONLY count:" in output
    assert "UNDER_COVERED count:" in output
    assert "BLOCKED count: 0" in output
    assert "broker_boundary_allowed = false" in output
    assert "execution_allowed = false" in output
    assert "adapter_invocation_allowed = false" in output
    assert "executor_invocation_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "live_access_allowed = false" in output
    assert "parser_outputs_are_review_data_only = true" in output
    assert "JSON report: reports/ai/day100_parser_phase_gate_review.json" in output
    assert "HTML report: reports/ai/day100_parser_phase_gate_review.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day100_report_index_visibility_includes_phase_gate_review(tmp_path):
    assert network_lab.main(["--task", "parser-phase-gate-review"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Parser Phase Gate Review / Readiness Decision" in html
    assert "parser phase gate readiness decision" in html
    assert "reports/ai/day100_parser_phase_gate_review.json" in html
    assert "reports/ai/day100_parser_phase_gate_review.html" in html
    assert "broker_boundary_allowed" in html


def test_day100_task_catalog_contains_phase_gate_metadata():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-phase-gate-review")

    assert task["task_id"] == "day100_parser_phase_gate_review"
    assert task["day"] == "Day100"
    assert task["display_name"] == "Day100 Parser Phase Gate Review / Readiness Decision"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day100_parser_phase_gate_review.json" in task["report_paths"]
    assert "reports/ai/day100_parser_phase_gate_review.html" in task["report_paths"]
    assert "docs/ai-intent/day100_parser_phase_gate_review.md" in task["report_paths"]
    assert "ADVANCE_READY" in task["notes"]
    assert "REVIEW_ONLY" in task["notes"]
    assert "UNDER_COVERED" in task["notes"]
    assert "BLOCKED" in task["notes"]
    assert "broker_boundary_allowed remains false" in task["notes"]
    assert "adapter_invocation_allowed remains false" in task["notes"]
    assert "live_access_allowed remains false" in task["notes"]


def test_day100_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day100.__file__)
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
