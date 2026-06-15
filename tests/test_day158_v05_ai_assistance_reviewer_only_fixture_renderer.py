from pathlib import Path

import day158_v05_ai_assistance_reviewer_only_fixture_renderer as day158
import network_lab


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day158_fixture_renderer_is_review_only_and_non_executable():
    report = day158.build_day158_v05_ai_assistance_reviewer_only_fixture_renderer(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == 158
    assert report["task"] == "v05-ai-assistance-reviewer-only-fixture-renderer"
    assert report["status_label"] == "V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_REVIEW_READY"
    assert report["contract_type"] == "reviewer_only_fixture_renderer"
    assert report["execution_allowed"] is False
    assert report["provider_allowed"] is False
    assert report["api_allowed"] is False
    assert report["model_call_allowed"] is False
    assert report["live_device_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["secrets_allowed"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []


def test_day158_cli_is_report_only(capsys):
    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-reviewer-only-fixture-renderer"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "[PASS] V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_REVIEW_READY" in output
    assert "execution_allowed: false" in output
    assert "provider_allowed: false" in output
    assert "live_device_allowed: false" in output
    assert "next_phase_allowed: false" in output
