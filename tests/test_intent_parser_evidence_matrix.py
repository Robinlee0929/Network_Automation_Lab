import ast
import json

import intent_parser_evidence_matrix as day103
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


def test_day103_matrix_is_deterministic_and_ready():
    first = day103.build_parser_evidence_matrix_report()
    second = day103.build_parser_evidence_matrix_report()

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["reviewer_status"] == "MATRIX_READY"
    assert first["validation_errors"] == []


def test_day103_matrix_covers_day96_through_day102():
    report = day103.build_parser_evidence_matrix_report()
    summary = report["summary"]
    rows = report["matrix_rows"]

    assert summary["days_covered"] == [
        "Day96",
        "Day97",
        "Day98",
        "Day99",
        "Day100",
        "Day101",
        "Day102",
    ]
    assert summary["total_days_covered"] == 7
    assert {row["day"] for row in rows} == set(summary["days_covered"])


def test_day103_rows_have_required_traceability_fields_and_report_paths():
    report = day103.build_parser_evidence_matrix_report()
    required_fields = {
        "day",
        "evidence_source",
        "parser_gap",
        "fixture_or_evidence_id",
        "fixture_category",
        "expected_decision",
        "actual_result",
        "trace_status",
        "report_json_path",
        "report_html_path",
        "safety_boundary",
        "reviewer_note",
    }

    for row in report["matrix_rows"]:
        assert required_fields <= row.keys()
        assert all(row[field] for field in required_fields if field != "safety_boundary")
        assert isinstance(row["report_json_path"], str)
        assert isinstance(row["report_html_path"], str)
        assert row["report_json_path"].startswith("reports/")
        assert row["report_html_path"].startswith("reports/")
        assert row["report_json_path"].endswith(".json")
        assert row["report_html_path"].endswith(".html")
        assert row["trace_status"] in day103.TRACE_STATUSES


def test_day103_preserves_every_execution_boundary_on_each_row():
    report = day103.build_parser_evidence_matrix_report()

    for row in report["matrix_rows"]:
        assert row["execution_allowed"] is False
        assert row["adapter_invocation_allowed"] is False
        assert row["broker_handoff_allowed"] is False
        assert row["live_access_allowed"] is False
        assert row["ssh_allowed"] is False
        assert row["parser_capability_added"] is False
        for requirement in day103.SAFETY_BOUNDARY_REQUIREMENTS:
            assert row["safety_boundary"][requirement] is True


def test_day103_aggregate_counters_are_correct():
    report = day103.build_parser_evidence_matrix_report()
    rows = report["matrix_rows"]
    summary = report["summary"]

    assert summary["total_rows"] == len(rows)
    assert summary["trace_complete_count"] == sum(1 for row in rows if row["trace_status"] == "TRACE_COMPLETE")
    assert summary["review_required_count"] == sum(1 for row in rows if row["trace_status"] == "REVIEW_REQUIRED")
    assert summary["known_gap_count"] == sum(1 for row in rows if row["trace_status"] == "KNOWN_GAP")
    assert summary["blocked_by_safety_boundary_count"] == sum(
        1 for row in rows if row["trace_status"] == "BLOCKED_BY_SAFETY_BOUNDARY"
    )
    assert summary["trace_complete_count"] >= 1
    assert summary["review_required_count"] + summary["known_gap_count"] >= 1
    assert summary["execution_allowed_count"] == 0
    assert summary["adapter_invocation_allowed_count"] == 0
    assert summary["broker_handoff_allowed_count"] == 0
    assert summary["live_access_allowed_count"] == 0
    assert summary["ssh_allowed_count"] == 0
    assert summary["parser_capability_added_count"] == 0
    assert summary["overall_status"] == "PASS"
    assert summary["reviewer_status"] == "MATRIX_READY"


def test_day103_report_writer_outputs_json_and_html(tmp_path):
    report = day103.build_parser_evidence_matrix_report()

    json_path, html_path = day103.write_parser_evidence_matrix_reports(tmp_path, report)

    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day103 Parser Evidence Matrix / Gap Traceability" in html
    assert "MATRIX_READY" in html
    assert "reports/ai/day103_parser_evidence_matrix_gap_traceability.json" in html


def test_day103_module_has_no_live_or_external_tool_imports():
    tree = ast.parse(open(day103.__file__, encoding="utf-8").read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day103_runner_task_returns_pass_without_execution(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day103 parser evidence matrix must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day103 parser evidence matrix must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-evidence-matrix-gap-traceability"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day103 Parser Evidence Matrix / Gap Traceability" in output
    assert "Task name: parser-evidence-matrix-gap-traceability" in output
    assert "PASS / MATRIX_READY" in output
    assert "execution_allowed_count = 0" in output
    assert "adapter_invocation_allowed_count = 0" in output
    assert "broker_handoff_allowed_count = 0" in output
    assert "live_access_allowed_count = 0" in output
    assert "JSON report: reports/ai/day103_parser_evidence_matrix_gap_traceability.json" in output
    assert "HTML report: reports/ai/day103_parser_evidence_matrix_gap_traceability.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day103_report_index_visibility_includes_matrix(tmp_path):
    assert network_lab.main(["--task", "parser-evidence-matrix-gap-traceability"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Evidence Matrix / Gap Traceability" in html
    assert "reports/ai/day103_parser_evidence_matrix_gap_traceability.json" in html
    assert "reports/ai/day103_parser_evidence_matrix_gap_traceability.html" in html
