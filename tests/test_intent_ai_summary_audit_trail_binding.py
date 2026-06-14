import json
from pathlib import Path

import intent_ai_summary_audit_trail_binding as day131
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day131_report_is_deterministic_review_only_and_non_advancing():
    first = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)
    second = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["audit_status"] == "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY"
    assert first["day"] == "Day131"
    assert first["task"] == "ai-summary-audit-trail-binding"
    assert first["review_only"] is True
    assert first["non_advancing"] is True
    assert first["deterministic_only"] is True
    assert first["audit_record_count"] == 1
    assert first["validation_errors"] == []


def test_day131_required_references_are_present():
    report = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)
    record = report["audit_records"][0]

    assert report["schema_reference"]["schema_version"] == "day127.ai_reviewer_summary_schema_contract.v1"
    assert report["schema_reference"]["fixture_path"] == "fixtures/day127_ai_reviewer_summary.example.json"
    assert report["prompt_contract_reference"]["task"] == "ai-summary-prompt-contract"
    assert report["prompt_contract_reference"]["contract_scope"] == "REVIEWER_TEXT_ONLY"
    assert report["redaction_no_secret_policy_reference"]["task"] == (
        "ai-summary-redaction-and-no-secret-policy"
    )
    assert report["redaction_no_secret_policy_reference"]["source_text_omitted_from_audit"] is True
    assert record["summary_artifact_identity"]["summary_id"] == "day127-example-ai-reviewer-summary"
    assert record["fixture_renderer_reference"]["task"] == "ai-reviewer-summary-fixture-renderer"
    assert record["fixture_or_source_record_reference"]["primary_fixture_ref"] == (
        "fixtures/day127_ai_reviewer_summary.example.json"
    )


def test_day131_required_safety_flags_are_false():
    report = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)
    record_flags = report["audit_records"][0]["non_execution_safety_flags"]
    evidence = report["audit_records"][0]["no_execution_evidence"]

    for field in (
        "provider_api_enabled",
        "ai_execution_enabled",
        "ai_decision_enabled",
        "next_phase_allowed",
        "reviewer_approval_enabled",
        "mock_provider_enabled",
        "live_execution_enabled",
        "ssh_invocation_enabled",
        "device_invocation_enabled",
        "broker_invocation_enabled",
        "runner_invocation_enabled",
        "adapter_invocation_enabled",
    ):
        assert report[field] is False
        assert record_flags[field] is False

    assert record_flags["provider_enabled"] is False
    assert record_flags["api_enabled"] is False
    assert record_flags["openai_api_called"] is False
    assert record_flags["network_access_enabled"] is False
    assert all(value is False for value in evidence.values())


def test_day131_report_omits_day130_source_secret_like_text():
    report = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)
    serialized = json.dumps(report)

    assert "input_text" not in serialized
    assert "day130_fake_password_value" not in serialized
    assert "sk-day130-example-not-real-token-000000" not in serialized
    assert "access_token=day130_fake_access_token_000000" not in serialized


def test_day131_cli_task_reports_required_boundaries(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day131 audit binding must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day131 audit binding must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-summary-audit-trail-binding"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-summary-audit-trail-binding" in output
    assert "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY" in output
    assert "review_only: true" in output
    assert "non_advancing: true" in output
    assert "provider_api_enabled: false" in output
    assert "ai_execution_enabled: false" in output
    assert "ai_decision_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "reviewer_approval_enabled: false" in output
    assert "mock_provider_enabled: false" in output
    assert "live_execution_enabled: false" in output
    assert "ssh_invocation_enabled: false" in output
    assert "device_invocation_enabled: false" in output
    assert "broker_invocation_enabled: false" in output
    assert "runner_invocation_enabled: false" in output
    assert "adapter_invocation_enabled: false" in output
    assert "not_day132_reviewer_approval_gate: true" in output
    assert "not_day133_mock_provider_boundary: true" in output


def test_day131_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-summary-audit-trail-binding"
    )

    assert resolve_task_name("ai-summary-audit-trail-binding") == "ai-summary-audit-trail-binding"
    assert task["task_id"] == "day131_ai_summary_audit_trail_binding"
    assert task["day"] == "Day131"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_summary_audit_trail_binding.py"
    assert "Day132 AI Summary Dashboard Card Integration" in task["notes"]
    assert "Day133 mock provider boundary" in task["notes"]
    assert "provider/API" in task["notes"]
    assert "AI execution" in task["notes"]
    assert "AI decisions" in task["notes"]
    assert "next-phase approval" in task["notes"]


def test_day131_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-summary-audit-trail-binding"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-summary-audit-trail-binding", handlers)

    assert resolved.canonical_name == "ai-summary-audit-trail-binding"
    assert callable(resolved.handler)


def test_day131_write_reports_and_report_index_visibility(tmp_path):
    report = day131.build_ai_summary_audit_trail_binding_report(PROJECT_ROOT)
    json_path, html_path = day131.write_ai_summary_audit_trail_binding_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day131" in index_html
    assert "AI Summary Audit Trail Binding" in index_html


def test_day131_docs_exist_and_preserve_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day131_ai_summary_audit_trail_binding.md",
        PROJECT_ROOT / "docs/roadmap/day131_ai_summary_audit_trail_binding.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "review-only" in text
        assert "non-advancing" in text
        assert "not day132 ai summary dashboard card integration" in text
        assert "not day133 mock provider boundary" in text
        assert "does not enable execution / provider / api" in text
        assert "does not call openai api" in text
        assert "does not invoke ssh, device, broker, runner, or adapter paths" in text
        assert "does not infer reviewer approval" in text
        assert "does not unlock" in text


