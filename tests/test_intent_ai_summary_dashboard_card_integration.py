import json
from pathlib import Path

import intent_ai_summary_dashboard_card_integration as day132
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day132_dashboard_card_is_deterministic_display_only_and_non_advancing():
    first = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    second = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["display_status"] == "AI_SUMMARY_DASHBOARD_CARD_INTEGRATED_DISPLAY_ONLY"
    assert first["day"] == "Day132"
    assert first["task"] == "ai-summary-dashboard-card-integration"
    assert first["dashboard_card_id"] == "day132-ai-summary-dashboard-card"
    assert first["display_only"] is True
    assert first["review_only"] is True
    assert first["non_advancing"] is True
    assert first["deterministic_only"] is True
    assert first["validation_errors"] == []


def test_day132_agents_md_status_is_visible():
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)

    assert report["agents_md_status"] == "FOUND_AND_READ"
    assert report["agents_md_read_before_day132_work"] is True
    assert report["agents_md_evidence"]["agents_md_status"] == "FOUND_AND_READ"


def test_day132_required_chain_references_are_present():
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    input_refs = report["input_artifact_references"]
    input_days = {item["day"] for item in input_refs}

    assert {"Day127", "Day128", "Day129", "Day130", "Day131"}.issubset(input_days)
    assert report["summary_chain_status"] == "DAY127_DAY131_REFERENCES_VISIBLE"
    assert report["redaction_no_secret_reference"]["task"] == (
        "ai-summary-redaction-and-no-secret-policy"
    )
    assert report["audit_trail_binding_reference"]["task"] == "ai-summary-audit-trail-binding"
    assert report["dashboard_card"]["audit_trail_binding_status"] == (
        "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY"
    )


def test_day132_required_safety_flags_are_false():
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    card_flags = report["dashboard_card"]["non_execution_safety_flags"]
    evidence = report["dashboard_card"]["no_execution_evidence"]

    for field in (
        "provider_api_enabled",
        "ai_execution_enabled",
        "ai_decision_enabled",
        "reviewer_approval_enabled",
        "next_phase_allowed",
        "mock_provider_enabled",
        "live_execution_enabled",
        "ssh_invocation_enabled",
        "device_invocation_enabled",
        "broker_invocation_enabled",
        "runner_invocation_enabled",
        "adapter_invocation_enabled",
    ):
        assert report[field] is False
        assert card_flags[field] is False

    assert card_flags["provider_enabled"] is False
    assert card_flags["api_enabled"] is False
    assert card_flags["openai_api_called"] is False
    assert card_flags["network_access_enabled"] is False
    assert all(value is False for value in evidence.values())


def test_day132_is_not_day133_or_day134_and_opens_no_provider_api():
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    boundary_text = "\n".join(report["dashboard_card"]["boundary_text"])

    assert report["not_day133_disabled_ai_provider_interface_boundary"] is True
    assert report["not_day134_offline_ai_provider_adapter_contract"] is True
    assert report["not_provider_api_integration"] is True
    assert report["not_ai_execution"] is True
    assert report["not_ai_decision_making"] is True
    assert report["not_reviewer_approval"] is True
    assert report["not_next_phase_unlock"] is True
    assert "not Day133" in boundary_text
    assert "not Day134" in boundary_text
    assert "not provider/API integration" in boundary_text


def test_day132_report_omits_day130_source_secret_like_text():
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    serialized = json.dumps(report)

    assert "input_text" not in serialized
    assert "day130_fake_password_value" not in serialized
    assert "sk-day130-example-not-real-token-000000" not in serialized
    assert "access_token=day130_fake_access_token_000000" not in serialized


def test_day132_cli_task_reports_required_boundaries(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day132 dashboard card integration must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day132 dashboard card integration must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-summary-dashboard-card-integration"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md status: FOUND_AND_READ" in output
    assert "Task name: ai-summary-dashboard-card-integration" in output
    assert "AI_SUMMARY_DASHBOARD_CARD_INTEGRATED_DISPLAY_ONLY" in output
    assert "display_only: true" in output
    assert "review_only: true" in output
    assert "non_advancing: true" in output
    assert "provider_api_enabled: false" in output
    assert "ai_execution_enabled: false" in output
    assert "ai_decision_enabled: false" in output
    assert "reviewer_approval_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "mock_provider_enabled: false" in output
    assert "live_execution_enabled: false" in output
    assert "ssh_invocation_enabled: false" in output
    assert "device_invocation_enabled: false" in output
    assert "broker_invocation_enabled: false" in output
    assert "runner_invocation_enabled: false" in output
    assert "adapter_invocation_enabled: false" in output
    assert "not_day133_disabled_ai_provider_interface_boundary: true" in output
    assert "not_day134_offline_ai_provider_adapter_contract: true" in output


def test_day132_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-summary-dashboard-card-integration"
    )

    assert resolve_task_name("ai-summary-dashboard-card-integration") == (
        "ai-summary-dashboard-card-integration"
    )
    assert task["task_id"] == "day132_ai_summary_dashboard_card_integration"
    assert task["day"] == "Day132"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_summary_dashboard_card_integration.py"
    assert "Dashboard Card Integration" in task["display_name"]
    assert "Day133 Disabled AI Provider Interface Boundary" in task["notes"]
    assert "Day134 Offline AI Provider Adapter Contract" in task["notes"]
    assert "provider/API" in task["notes"]
    assert "AI execution" in task["notes"]
    assert "AI decision" in task["notes"]
    assert "reviewer approval" in task["notes"]
    assert "next-phase" in task["notes"]


def test_day132_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-summary-dashboard-card-integration"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-summary-dashboard-card-integration", handlers)

    assert resolved.canonical_name == "ai-summary-dashboard-card-integration"
    assert callable(resolved.handler)


def test_day132_write_reports_and_report_index_visibility(tmp_path):
    report = day132.build_ai_summary_dashboard_card_integration_report(PROJECT_ROOT)
    json_path, html_path = day132.write_ai_summary_dashboard_card_integration_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day132" in index_html
    assert "AI Summary Dashboard Card Integration" in index_html


def test_day132_docs_exist_and_preserve_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day132_ai_summary_dashboard_card_integration.md",
        PROJECT_ROOT / "docs/roadmap/day132_ai_summary_dashboard_card_integration.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "dashboard card integration" in text
        assert "display-only" in text
        assert "review-only" in text
        assert "non-advancing" in text
        assert "not day133 disabled ai provider interface boundary" in text
        assert "not day134 offline ai provider adapter contract" in text
        assert "does not enable execution / provider / api" in text
        assert "does not call openai api" in text
        assert "does not make ai decisions" in text
        assert "does not infer reviewer approval" in text
        assert "does not unlock" in text
