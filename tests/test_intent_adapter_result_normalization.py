import ast
import json
from pathlib import Path

import dashboard_app as dashboard
import intent_adapter_result_normalization as day95
import network_lab


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


def test_day95_normalized_fake_adapter_result_schema_is_fixed_and_complete():
    report = day95.run_adapter_result_normalization()
    required = set(report["normalized_schema"]["required_top_level_fields"])

    assert report["normalized_schema"]["schema_version"] == "day95.adapter_result.v1"
    assert report["normalized_schema"]["status_source"] == "deterministic_fake_boundary"
    for result in report["normalized_result_records"]:
        assert set(result) == required
        assert result["schema_version"] == "day95.adapter_result.v1"
        assert result["result_kind"] == "normalized_fake_adapter_result"
        assert result["adapter_type"] == "fake"
        assert result["source_boundary"] == "guarded_fake_adapter_boundary"
        assert set(result["result_payload"]) == {
            "command_family",
            "readonly_intent",
            "simulated_output",
            "parser_ready",
        }
        assert set(result["safety"]) == {
            "real_adapter_result_present",
            "live_execution_result_present",
            "ssh_used",
            "device_access_used",
            "execution_unlocked",
        }
        assert set(result["evidence"]) == {
            "day93_guarded_fake_adapter_boundary_audit",
            "day94_adapter_boundary_regression_matrix",
            "normalization_applied",
        }


def test_day95_allowed_scenarios_produce_normalized_fake_adapter_results():
    report = day95.run_adapter_result_normalization()
    allowed = [
        record
        for record in report["scenario_records"]
        if record["guard_decision"] == day95.ALLOW
    ]

    assert allowed
    assert len(report["normalized_result_records"]) == len(allowed)
    for record in allowed:
        assert record["adapter_invoked"] is True
        assert record["adapter_result_present"] is True
        assert record["adapter_result"]["adapter_type"] == "fake"
        assert record["adapter_result"]["result_status"] == day95.DETERMINISTIC_FAKE_STATUS
        assert record["adapter_result"]["result_payload"]["parser_ready"] is True


def test_day95_rejected_scenarios_produce_no_adapter_result():
    report = day95.run_adapter_result_normalization()
    rejected = [
        record
        for record in report["scenario_records"]
        if record["guard_decision"] == day95.REJECT
    ]

    assert rejected
    assert len(report["rejection_records"]) == len(rejected)
    for record in rejected:
        assert record["adapter_invoked"] is False
        assert record["fake_adapter_invoked"] is False
        assert record["adapter_result"] is None
        assert record["adapter_result_present"] is False
        assert record["fake_boundary_result_status"] is None


def test_day95_result_counts_and_status_source_are_deterministic():
    first = day95.run_adapter_result_normalization()
    second = day95.run_adapter_result_normalization()
    summary = first["summary"]

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["overall_status"] == "PASS"
    assert summary["fake_adapter_result_count"] == summary["allowed_count"]
    assert summary["normalized_result_count"] == summary["allowed_count"]
    assert summary["real_adapter_result_count"] == 0
    assert summary["live_execution_result_count"] == 0
    assert summary["rejected_with_adapter_result"] == 0
    assert summary["result_status_values"] == [day95.DETERMINISTIC_FAKE_STATUS]
    assert summary["result_status_source"] == "deterministic_fake_boundary"
    assert day95.validate_report(first) == []


def test_day95_evidence_chain_references_day93_and_day94():
    report = day95.run_adapter_result_normalization()

    assert report["evidence_chain_summary"]["day93_guarded_fake_adapter_boundary_audit"] is True
    assert report["evidence_chain_summary"]["day94_adapter_boundary_regression_matrix"] is True
    assert report["references"]["day93"]["task"] == "guarded-fake-adapter-contract"
    assert report["references"]["day94"]["task"] == "adapter-boundary-regression-matrix"
    for result in report["normalized_result_records"]:
        assert result["evidence"]["day93_guarded_fake_adapter_boundary_audit"] is True
        assert result["evidence"]["day94_adapter_boundary_regression_matrix"] is True


def test_day95_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day95.run_adapter_result_normalization()
    json_path, html_path = day95.write_adapter_result_normalization_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day95_adapter_result_normalization.json"
    assert html_path == tmp_path / "reports/lab-summary/day95_adapter_result_normalization.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day95 Adapter Result Normalization" in html
    assert "real adapter result and live execution result are absent" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day95_runner_task_returns_pass_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day95 adapter result normalization must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day95 adapter result normalization must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "adapter-result-normalization"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day95 Adapter Result Normalization" in output
    assert "Task name: adapter-result-normalization" in output
    assert "PASS" in output
    assert "Total scenarios: 5" in output
    assert "Allowed count: 2" in output
    assert "Rejected count: 3" in output
    assert "Normalized result count: 2" in output
    assert "real_adapter_result_count = 0" in output
    assert "live_execution_result_count = 0" in output
    assert "evidence_chain_complete = true" in output
    assert "JSON report: reports/lab-summary/day95_adapter_result_normalization.json" in output
    assert "HTML report: reports/lab-summary/day95_adapter_result_normalization.html" in output


def test_day95_dashboard_remains_read_only_and_exposes_visibility(tmp_path):
    report = day95.run_adapter_result_normalization()
    day95.write_adapter_result_normalization_reports(tmp_path, report)

    rows = network_lab.discover_report_visibility(tmp_path)
    row = next(item for item in rows if item["day"] == "Day95")
    assert row["status"] == "FOUND"
    assert row["json"] == "reports/lab-summary/day95_adapter_result_normalization.json"
    assert row["html"] == "reports/lab-summary/day95_adapter_result_normalization.html"

    entries = dashboard.collect_dashboard_evidence(tmp_path, tmp_path / "reports")
    entry = next(item for item in entries if item.day == "Day95")
    assert entry.title == "Adapter Result Normalization"
    assert entry.status == "PASS"
    assert entry.json_view_path == "reports/lab-summary/day95_adapter_result_normalization.json"
    assert entry.html_view_path == "reports/lab-summary/day95_adapter_result_normalization.html"
    text = f"{entry.title} {entry.description} {entry.notes}".lower()
    assert "rejected scenarios produce no adapter result" in text
    assert "real_adapter_result_count remains 0" in text
    assert "live_execution_result_count remains 0" in text


def test_day95_no_unlock_flag_or_live_execution_path_exists():
    report = day95.run_adapter_result_normalization()

    assert report["dashboard_action_allowed"] is False
    assert report["safety_invariant_summary"]["no_execution_approval_mechanism"] is True
    assert report["safety_invariant_summary"]["no_dashboard_action"] is True
    for result in report["normalized_result_records"]:
        assert result["safety"]["execution_unlocked"] is False
        assert result["safety"]["ssh_used"] is False
        assert result["safety"]["device_access_used"] is False
        assert result["safety"]["real_adapter_result_present"] is False
        assert result["safety"]["live_execution_result_present"] is False


def test_day95_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day95.__file__)
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
