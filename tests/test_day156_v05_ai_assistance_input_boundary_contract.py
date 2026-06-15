from pathlib import Path

import day156_v05_ai_assistance_input_boundary_contract as day156
import network_lab


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day156_input_boundary_contract_is_review_only_and_non_executable():
    report = day156.build_day156_v05_ai_assistance_input_boundary_contract(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == 156
    assert report["task"] == "v05-ai-assistance-input-boundary-contract"
    assert report["status_label"] == "V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY"
    assert report["contract_type"] == "input_boundary_contract"
    assert report["config_json_read_allowed"] is False
    assert report["credential_read_allowed"] is False
    assert report["execution_allowed"] is False
    assert report["provider_allowed"] is False
    assert report["api_allowed"] is False
    assert report["live_device_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["secrets_allowed"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []


def test_day156_cli_is_report_only(capsys):
    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-input-boundary-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[PASS] V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY" in output
    assert "execution_allowed: false" in output
    assert "provider_allowed: false" in output
    assert "api_allowed: false" in output
    assert "live_device_allowed: false" in output
    assert "next_phase_allowed: false" in output
