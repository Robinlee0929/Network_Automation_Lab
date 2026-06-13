import json
from pathlib import Path

import pytest

import intent_thin_cli_regression_gate as day125
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import (
    UnknownTaskError,
    resolve_task_handler,
    resolve_task_name,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day125_agents_md_pre_read_evidence_passes():
    report = day125.build_thin_cli_regression_gate_report(PROJECT_ROOT)

    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day125_work"] is True
    assert report["agents_md_path"] == "AGENTS.md"


def test_day125_agents_md_missing_fails_without_claiming_pre_read(tmp_path):
    evidence = day125.build_agents_md_pre_read_evidence(tmp_path)

    assert evidence["agents_md_pre_read_result"] == "FAIL"
    assert evidence["agents_md_read_before_day125_work"] is False


def test_day125_thin_cli_invariant_keeps_day125_logic_out_of_network_lab():
    result = day125.build_thin_cli_check(PROJECT_ROOT)
    source = (PROJECT_ROOT / "network_lab.py").read_text(encoding="utf-8")

    assert result["result"] == "PASS"
    assert result["network_lab_py_role"] == "THIN_CLI_ENTRYPOINT_ONLY"
    assert "return cli_dispatch_main(" in source
    assert "from network_lab_cli_dispatch import _build_task_handlers" in source
    assert "build_thin_cli_regression_gate_report" not in source
    assert "write_thin_cli_regression_gate_reports" not in source
    assert "thin_cli_result" not in source


def test_day125_registry_invariant_and_unknown_task_rejection():
    result = day125.build_registry_check()

    assert result["result"] == "PASS"
    assert resolve_task_name("thin-cli-regression-gate") == "thin-cli-regression-gate"
    with pytest.raises(UnknownTaskError):
        resolve_task_name("unknown-network-lab-task")


def test_day125_dispatch_invariant_and_cli_task_runs_without_live_flags(capsys):
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "thin-cli-regression-gate"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("thin-cli-regression-gate", handlers)

    assert resolved.canonical_name == "thin-cli-regression-gate"
    assert callable(resolved.handler)
    exit_code = network_lab.main(["--task", "thin-cli-regression-gate"], project_root=PROJECT_ROOT)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "allowed_to_execute: false" in output
    assert "ssh_allowed: false" in output
    assert "live_command_allowed: false" in output
    assert "next_phase_allowed: false" in output
    assert "THIN_CLI_REGRESSION_GATE_READY" in output


def test_day125_safety_invariants_remain_locked():
    report = day125.build_thin_cli_regression_gate_report(PROJECT_ROOT)

    assert report["safety_helper_regression_result"] == "PASS"
    assert report["allowed_to_execute"] is False
    assert report["ssh_allowed"] is False
    assert report["live_command_allowed"] is False
    assert report["next_phase_allowed"] is False
    assert report["live_execution_added"] is False
    assert report["openai_api_added"] is False
    assert report["dashboard_execution_endpoint_added"] is False


def test_day125_report_shape_and_sub_gate_consistency():
    report = day125.build_thin_cli_regression_gate_report(PROJECT_ROOT)

    for field in day125.REQUIRED_REPORT_FIELDS:
        assert field in report
    assert report["overall_status"] == "PASS"
    for field in day125.SUB_GATE_FIELDS:
        assert report[field] == "PASS"
    assert report["final_recommendation"] == (
        "KEEP_THIN_CLI_AND_CONTINUE_REVIEW_ONLY_REGRESSION"
    )
    assert report["validation_errors"] == []


def test_day125_report_index_visibility_includes_thin_cli_gate(tmp_path):
    report = day125.build_thin_cli_regression_gate_report(PROJECT_ROOT)
    json_path, html_path = day125.write_thin_cli_regression_gate_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_path = tmp_path / "reports" / "report_index.html"
    index_html = index_path.read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day125" in index_html
    assert "Thin CLI Regression Gate" in index_html
