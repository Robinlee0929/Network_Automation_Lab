from pathlib import Path

import day157_v05_ai_assistance_output_template_contract as day157
import network_lab


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day157_output_template_contract_is_review_only_and_non_executable():
    report = day157.build_day157_v05_ai_assistance_output_template_contract(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == 157
    assert report["task"] == "v05-ai-assistance-output-template-contract"
    assert report["status_label"] == "V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY"
    assert report["contract_type"] == "output_template_contract"
    assert report["direct_command_generation_allowed"] is False
    assert report["execution_allowed"] is False
    assert report["executor_unlock_allowed"] is False
    assert report["provider_allowed"] is False
    assert report["api_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["secrets_allowed"] is False
    assert report["phase_gate_approval"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []


def test_day157_cli_is_report_only(capsys):
    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-output-template-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[PASS] V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY" in output
    assert "execution_allowed: false" in output
    assert "command_execution_allowed: false" in output
    assert "executor_unlock_allowed: false" in output
    assert "next_phase_allowed: false" in output
