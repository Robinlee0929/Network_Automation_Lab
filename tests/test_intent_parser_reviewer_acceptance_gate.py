import ast
import json

import intent_parser_reviewer_acceptance_gate as day104
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
}


def _row(row_id, trace_status, required=True):
    return {
        "row_id": row_id,
        "day": "Day103",
        "trace_status": trace_status,
        "required": required,
        "reviewer_note": f"{trace_status} reviewer note",
    }


def _report(rows):
    return {"day_id": "Day103", "task": "parser-evidence-matrix-gap-traceability", "matrix_rows": rows}


def test_day104_all_trace_complete_allows_next_stage():
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([
            _row("R1", day104.TRACE_COMPLETE),
            _row("R2", day104.TRACE_COMPLETE),
        ])
    )

    assert report["acceptance_decision"] == "ACCEPTABLE_FOR_NEXT_STAGE"
    assert report["next_stage_allowed"] is True
    assert report["blocking_findings"] == []
    assert report["validation_errors"] == []


def test_day104_review_required_does_not_mark_full_acceptance():
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([
            _row("R1", day104.TRACE_COMPLETE),
            _row("R2", day104.REVIEW_REQUIRED),
        ])
    )

    assert report["acceptance_decision"] == "ACCEPTABLE_WITH_REVIEW_NOTES"
    assert report["acceptance_decision"] != "ACCEPTABLE_FOR_NEXT_STAGE"
    assert report["next_stage_allowed"] is False
    assert report["review_notes"]


def test_day104_known_gap_blocks_next_stage():
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([
            _row("R1", day104.TRACE_COMPLETE),
            _row("R2", day104.KNOWN_GAP),
        ])
    )

    assert report["acceptance_decision"] == "NOT_ACCEPTABLE_KNOWN_GAPS"
    assert report["next_stage_allowed"] is False
    assert report["blocking_findings"][0]["trace_status"] == day104.KNOWN_GAP


def test_day104_safety_boundary_blocks_next_stage():
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([
            _row("R1", day104.TRACE_COMPLETE),
            _row("R2", day104.BLOCKED_BY_SAFETY_BOUNDARY),
        ])
    )

    assert report["acceptance_decision"] == "NOT_ACCEPTABLE_SAFETY_BLOCKED"
    assert report["next_stage_allowed"] is False
    assert report["blocking_findings"][0]["trace_status"] == day104.BLOCKED_BY_SAFETY_BOUNDARY


def test_day104_safety_boundary_dominates_known_gap():
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([
            _row("R1", day104.KNOWN_GAP),
            _row("R2", day104.BLOCKED_BY_SAFETY_BOUNDARY),
        ])
    )

    assert report["acceptance_decision"] == "NOT_ACCEPTABLE_SAFETY_BLOCKED"
    assert report["next_stage_allowed"] is False
    assert report["required_matrix_state_counts"][day104.KNOWN_GAP] == 1
    assert report["required_matrix_state_counts"][day104.BLOCKED_BY_SAFETY_BOUNDARY] == 1


def test_day104_empty_or_malformed_matrix_requires_review():
    empty_report = day104.build_parser_reviewer_acceptance_gate_report(_report([]))
    malformed_report = day104.build_parser_reviewer_acceptance_gate_report({"matrix_rows": [{"row_id": "R1"}]})

    assert empty_report["acceptance_decision"] == "REVIEW_REQUIRED"
    assert empty_report["next_stage_allowed"] is False
    assert malformed_report["acceptance_decision"] == "REVIEW_REQUIRED"
    assert malformed_report["next_stage_allowed"] is False
    assert malformed_report["blocking_findings"][0]["reason"] == "Malformed or missing trace status."


def test_day104_default_day103_matrix_is_safety_blocked_gate_only():
    report = day104.build_parser_reviewer_acceptance_gate_report()

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_GATE_READY"
    assert report["mode"] == "REVIEW_GATE_ONLY"
    assert report["decision_mode"] == "ACCEPTANCE_DECISION_ONLY"
    assert report["acceptance_decision"] == "NOT_ACCEPTABLE_SAFETY_BLOCKED"
    assert report["next_stage_allowed"] is False
    assert report["matrix_state_counts"][day104.BLOCKED_BY_SAFETY_BOUNDARY] >= 1
    assert report["matrix_state_counts"][day104.KNOWN_GAP] >= 1
    assert report["validation_errors"] == []


def test_day104_all_safety_and_execution_flags_remain_false():
    report = day104.build_parser_reviewer_acceptance_gate_report()

    for flag in day104.SAFETY_FLAGS:
        assert report[flag] is False
        assert report["safety_flags"][flag] is False


def test_day104_report_writer_outputs_json_and_html(tmp_path):
    report = day104.build_parser_reviewer_acceptance_gate_report(
        _report([_row("R1", day104.TRACE_COMPLETE)])
    )

    json_path, html_path = day104.write_parser_reviewer_acceptance_gate_reports(tmp_path, report)

    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review" in html
    assert "ACCEPTABLE_FOR_NEXT_STAGE" in html
    assert "reports/lab-summary/day104_parser_reviewer_acceptance_gate.json" in html


def test_day104_module_has_no_live_or_external_tool_imports():
    tree = ast.parse(open(day104.__file__, encoding="utf-8").read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day104_runner_task_returns_pass_without_execution(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day104 parser reviewer gate must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day104 parser reviewer gate must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-reviewer-acceptance-gate"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review" in output
    assert "Task name: parser-reviewer-acceptance-gate" in output
    assert "Mode: REVIEW_GATE_ONLY / ACCEPTANCE_DECISION_ONLY" in output
    assert "PASS / REVIEW_GATE_READY" in output
    assert "Acceptance decision: NOT_ACCEPTABLE_SAFETY_BLOCKED" in output
    assert "next_stage_allowed = false" in output
    assert "parser_capability_added = false" in output
    assert "execution_unlocked = false" in output
    assert "broker_handoff_enabled = false" in output
    assert "adapter_connected = false" in output
    assert "ssh_allowed = false" in output
    assert "live_device_access_allowed = false" in output
    assert "live_command_allowed = false" in output
    assert "config_change_allowed = false" in output
    assert "JSON report: reports/lab-summary/day104_parser_reviewer_acceptance_gate.json" in output
    assert "HTML report: reports/lab-summary/day104_parser_reviewer_acceptance_gate.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day104_report_index_visibility_includes_acceptance_gate(tmp_path):
    assert network_lab.main(["--task", "parser-reviewer-acceptance-gate"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Reviewer Acceptance Gate / Matrix Decision Review" in html
    assert "reports/lab-summary/day104_parser_reviewer_acceptance_gate.json" in html
    assert "reports/lab-summary/day104_parser_reviewer_acceptance_gate.html" in html
