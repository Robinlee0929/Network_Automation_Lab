import json
from pathlib import Path

import intent_ai_summary_prompt_contract as day129
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day129_valid_reviewer_text_only_prompt_passes():
    validation = day129.validate_prompt_contract(day129.ALLOWED_PROMPT)

    assert validation["status"] == "PASS"
    assert validation["contract_scope"] == "REVIEWER_TEXT_ONLY"
    assert validation["reviewer_text_only"] is True
    assert validation["violations"] == []


def test_day129_prompt_requesting_execution_is_rejected():
    prompt = day129.ALLOWED_PROMPT + "\nExecute the generated command."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("execution" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_provider_api_openai_call_is_rejected():
    prompt = day129.ALLOWED_PROMPT + "\nConfigure provider setup and make an OpenAI API call."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("provider" in violation.lower() for violation in validation["violations"])
    assert any("openai api" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_ai_approval_decision_is_rejected():
    prompt = day129.ALLOWED_PROMPT + "\nApprove the next reviewer outcome."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("approval decision" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_pass_fail_decision_is_rejected():
    prompt = day129.ALLOWED_PROMPT + "\nMake a pass/fail decision."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("pass/fail decision" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_next_phase_unlock_is_rejected():
    prompt = day129.ALLOWED_PROMPT + "\nUnlock next phase when the summary looks good."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("next phase unlock" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_redaction_or_secret_masking_is_rejected_as_day130_scope():
    prompt = day129.ALLOWED_PROMPT + "\nApply redaction and mask secrets before returning text."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("redaction" in violation.lower() for violation in validation["violations"])


def test_day129_prompt_requesting_audit_trail_binding_is_rejected_as_day131_scope():
    prompt = day129.ALLOWED_PROMPT + "\nBind this output to the audit trail."

    validation = day129.validate_prompt_contract(prompt)

    assert validation["status"] == "FAIL"
    assert any("audit trail" in violation.lower() for violation in validation["violations"])


def test_day129_report_shape_and_locked_boundaries():
    report = day129.build_ai_summary_prompt_contract_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "PROMPT_CONTRACT_READY"
    assert report["day"] == 129
    assert report["task"] == "ai-summary-prompt-contract"
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day129_work"] is True
    assert report["contract_scope"] == "REVIEWER_TEXT_ONLY"
    assert report["reviewer_text_only"] is True
    assert report["contract_fixture_count"] == 1
    assert report["violations"] == []
    assert report["validation_errors"] == []
    assert report["next_phase_allowed"] is False
    for field in (
        "provider_enabled",
        "api_enabled",
        "execution_enabled",
        "tool_calling_enabled",
        "ai_decision_enabled",
        "redaction_policy_enabled",
        "audit_trail_binding_enabled",
        "openai_api_called",
    ):
        assert report[field] is False


def test_day129_cli_task_reports_next_phase_false_and_agents_pre_read(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day129 prompt contract must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day129 prompt contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-summary-prompt-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-summary-prompt-contract" in output
    assert 'agents_md_pre_read_result: "PASS"' in output
    assert "agents_md_read_before_day129_work: true" in output
    assert 'contract_scope: "REVIEWER_TEXT_ONLY"' in output
    assert "next_phase_allowed: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "execution_enabled: false" in output
    assert "tool_calling_enabled: false" in output
    assert "PROMPT_CONTRACT_READY" in output


def test_day129_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-summary-prompt-contract"
    )

    assert resolve_task_name("ai-summary-prompt-contract") == "ai-summary-prompt-contract"
    assert task["task_id"] == "day129_ai_summary_prompt_contract"
    assert task["day"] == "Day129"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_summary_prompt_contract.py"
    assert "Day130 redaction" in task["notes"]
    assert "Day131 audit" in task["notes"]
    assert "OpenAI API" in task["notes"]
    assert "execution unlock" in task["notes"]


def test_day129_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-summary-prompt-contract"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-summary-prompt-contract", handlers)

    assert resolved.canonical_name == "ai-summary-prompt-contract"
    assert callable(resolved.handler)


def test_day129_write_reports_and_report_index_visibility(tmp_path):
    report = day129.build_ai_summary_prompt_contract_report(PROJECT_ROOT)
    json_path, html_path = day129.write_ai_summary_prompt_contract_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day129" in index_html
    assert "AI Summary Prompt Contract for Reviewer Text Only" in index_html


def test_day129_docs_exist_and_preserve_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day129_ai_summary_prompt_contract.md",
        PROJECT_ROOT / "docs/roadmap/day129_ai_summary_prompt_contract.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "prompt contract only" in text.lower()
        assert "not the next day" in text.lower()
        assert "does not enable execution / provider / api" in text.lower()
        assert "does not call openai api" in text.lower()
        assert "does not implement redaction policy" in text.lower()
        assert "does not implement audit trail binding" in text.lower()
        assert "does not make ai decisions" in text.lower()
        assert "does not unlock next phase" in text.lower()
