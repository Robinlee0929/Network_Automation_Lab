import ast
import json
from pathlib import Path

import intent_adapter_boundary_regression_matrix as day94


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "routeros_api",
    "librouteros",
    "socket",
    "subprocess",
    "requests",
    "telnetlib",
    "asyncssh",
}


def test_day94_matrix_has_required_size_and_unique_row_ids():
    rows = day94.build_regression_matrix()
    row_ids = [row.row_id for row in rows]

    assert len(rows) >= 12
    assert len(row_ids) == len(set(row_ids))
    assert {row.guard_decision for row in rows} == {day94.ALLOWED, day94.REJECTED}
    assert {row.adapter_target for row in rows} == {
        day94.FAKE_ADAPTER,
        day94.REAL_ADAPTER_BLOCKED,
    }


def test_day94_report_is_deterministic_and_passes_invariants():
    first = day94.run_adapter_boundary_regression_matrix()
    second = day94.run_adapter_boundary_regression_matrix()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 94
    assert first["task"] == "adapter-boundary-regression-matrix"
    assert first["overall_status"] == "PASS"
    assert first["mode"] == "FAKE_ADAPTER_BOUNDARY_EVIDENCE_ONLY"
    assert first["summary"]["total_rows"] >= 12
    assert first["summary"]["failed_rows"] == 0
    assert first["summary"]["adapter_invoked_for_rejected"] == 0
    assert first["summary"]["real_adapter_invocations"] == 0
    assert first["summary"]["live_execution_invocations"] == 0
    assert first["summary"]["overall_status"] == "PASS"
    assert day94.validate_report(first) == []


def test_day94_rejected_rows_never_invoke_fake_or_real_adapter():
    report = day94.run_adapter_boundary_regression_matrix()
    rejected = [
        row
        for row in report["matrix_rows"]
        if row["guard_decision"] == day94.REJECTED
    ]

    assert rejected
    for row in rejected:
        assert row["actual_fake_adapter_invoked"] is False
        assert row["actual_real_adapter_invoked"] is False
        assert row["live_execution_invoked"] is False
        assert row["live_execution_allowed"] is False
        assert row["regression_status"] == "PASS"


def test_day94_allowed_fake_rows_invoke_only_fake_boundary_evidence():
    report = day94.run_adapter_boundary_regression_matrix()
    allowed_fake = [
        row
        for row in report["matrix_rows"]
        if row["guard_decision"] == day94.ALLOWED
        and row["adapter_target"] == day94.FAKE_ADAPTER
    ]

    assert allowed_fake
    assert len(report["fake_adapter_invocation_evidence"]) == len(allowed_fake)
    for row in allowed_fake:
        assert row["expected_fake_adapter_invoked"] is True
        assert row["actual_fake_adapter_invoked"] is True
        assert row["actual_real_adapter_invoked"] is False
        assert row["boundary_result"] == "FAKE_BOUNDARY_EVIDENCE_RECORDED"
        assert row["invocation_id"] is not None
        assert row["invocation_evidence"]["boundary_use"] == "evidence_only"


def test_day94_real_adapter_and_live_execution_invocations_are_always_zero():
    report = day94.run_adapter_boundary_regression_matrix()

    for row in report["matrix_rows"]:
        assert row["expected_real_adapter_invoked"] is False
        assert row["actual_real_adapter_invoked"] is False
        assert row["live_execution_allowed"] is False
        assert row["live_execution_invoked"] is False
    assert report["summary"]["real_adapter_invocations"] == 0
    assert report["summary"]["live_execution_invocations"] == 0


def test_day94_reports_are_written_without_action_controls(tmp_path):
    report = day94.run_adapter_boundary_regression_matrix()
    json_path, html_path = day94.write_adapter_boundary_regression_matrix_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day94_adapter_boundary_regression_matrix.json"
    assert html_path == tmp_path / "reports/lab-summary/day94_adapter_boundary_regression_matrix.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert data["overall_status"] == "PASS"
    assert data["summary"]["adapter_invoked_for_rejected"] == 0
    assert "Adapter Boundary Regression Matrix" in html
    assert "fake-adapter-only, no SSH, no real device access, no live execution" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day94_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day94.__file__)
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
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
