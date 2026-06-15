from pathlib import Path

import day160_v05_ai_assistance_phase_gate_review as day160
import network_lab


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day160_phase_gate_review_is_not_phase_gate_approval():
    report = day160.build_day160_v05_ai_assistance_phase_gate_review(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == 160
    assert report["task"] == "v05-ai-assistance-phase-gate-review"
    assert report["status_label"] == "V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_READY"
    assert report["contract_type"] == "phase_gate_review"
    assert report["phase_gate_approval"] is False
    assert report["next_phase_allowed"] is False
    assert report["execution_allowed"] is False
    assert report["executor_unlock_allowed"] is False
    assert report["provider_allowed"] is False
    assert report["api_allowed"] is False
    assert report["model_call_allowed"] is False
    assert report["live_device_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["secrets_allowed"] is False
    assert report["validation_errors"] == []


def test_day160_cli_is_report_only(capsys):
    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-phase-gate-review"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[PASS] V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_READY" in output
    assert "phase_gate_approval: false" in output
    assert "execution_allowed: false" in output
    assert "executor_unlock_allowed: false" in output
    assert "next_phase_allowed: false" in output
