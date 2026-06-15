from pathlib import Path

import day159_v05_ai_assistance_safety_regression_matrix as day159
import network_lab


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day159_safety_regression_matrix_is_review_only_and_non_executable():
    report = day159.build_day159_v05_ai_assistance_safety_regression_matrix(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == 159
    assert report["task"] == "v05-ai-assistance-safety-regression-matrix"
    assert report["status_label"] == "V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_REVIEW_READY"
    assert report["contract_type"] == "safety_regression_matrix"
    assert report["provider_allowed"] is False
    assert report["api_allowed"] is False
    assert report["model_call_allowed"] is False
    assert report["live_device_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["secrets_allowed"] is False
    assert report["phase_gate_approval"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []


def test_day159_cli_is_report_only(capsys):
    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-safety-regression-matrix"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[PASS] V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_REVIEW_READY" in output
    assert "provider_allowed: false" in output
    assert "live_device_allowed: false" in output
    assert "command_execution_allowed: false" in output
    assert "next_phase_allowed: false" in output
