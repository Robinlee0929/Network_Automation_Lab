import json
from pathlib import Path

import ai_reviewer_export_package_integration as day136
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


DISABLED_FIELDS = (
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "live_actions_enabled",
    "secret_or_env_access",
    "external_network_call",
    "adapter_broker_runner_invoked",
    "model_invocation_enabled",
    "ssh_enabled",
    "device_action_enabled",
    "next_day_functionality_enabled",
)


def test_day136_export_package_contains_required_review_only_fields():
    report = day136.build_ai_reviewer_export_package_integration_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "AI_REVIEWER_EXPORT_PACKAGE_READY"
    assert report["package_id"] == "day136-ai-reviewer-export-package"
    assert report["package_name"] == "day136-ai-reviewer-export-package"
    assert report["day"] == 136
    assert report["title"] == "AI Reviewer Export Package Integration"
    assert report["review_only"] is True
    assert report["report_only"] is True
    assert report["deterministic"] is True
    assert report["local_repo_evidence_only"] is True
    assert report["redaction_status"] == "REDACTION_REVIEW_READY"
    assert report["audit_binding_status"] == "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY"
    assert report["consumer_gate_status"] == "PASS"
    assert report["not_next_day_statement"] == "This is not next-day functionality."
    assert report["no_execution_provider_api_statement"] == "Execution / provider / API remain disabled."
    assert report["statement_present_not_next_day_functionality"] is True
    assert report["statement_present_no_execution_provider_api"] is True
    assert report["agents_md_found"] is True
    assert report["agents_md_pre_read_before_changes"] is True
    assert report["agents_md_modified"] is False
    assert report["validation_errors"] == []

    for field in DISABLED_FIELDS:
        assert report[field] is False


def test_day136_source_sections_cover_day127_through_day135():
    report = day136.build_ai_reviewer_export_package_integration_report(PROJECT_ROOT)
    days = [section["day"] for section in report["source_sections"]]

    assert days == list(range(127, 136))
    assert report["included_evidence"]["source_day_range"] == "Day127-Day135"
    assert report["included_evidence"]["source_count"] == 9
    assert report["included_evidence"]["loaded_source_count"] == 9
    assert all(section["loaded"] is True for section in report["source_sections"])
    assert all(section["read_only"] is True for section in report["source_sections"])


def test_day136_missing_agents_md_fails_closed(tmp_path):
    report = day136.build_ai_reviewer_export_package_integration_report(tmp_path)

    assert report["overall_status"] == "FAIL"
    assert report["status"] == "AI_REVIEWER_EXPORT_PACKAGE_BLOCKED"
    assert report["agents_md_found"] is False
    assert report["agents_md_pre_read_before_changes"] is False
    assert report["execution_enabled"] is False
    assert report["provider_enabled"] is False
    assert report["api_enabled"] is False
    assert report["live_actions_enabled"] is False
    assert any("AGENTS.md" in error for error in report["validation_errors"])


def test_day136_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day136 export package must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day136 export package must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-reviewer-export-package-integration"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-reviewer-export-package-integration" in output
    assert "This is not next-day functionality." in output
    assert "Execution / provider / API remain disabled." in output
    assert "review_only: true" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "live_actions_enabled: false" in output
    assert "secret_or_env_access: false" in output
    assert "external_network_call: false" in output
    assert "adapter_broker_runner_invoked: false" in output
    assert "[PASS] AI_REVIEWER_EXPORT_PACKAGE_READY" in output


def test_day136_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-reviewer-export-package-integration"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-reviewer-export-package-integration"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-reviewer-export-package-integration", handlers)

    assert resolve_task_name("ai-reviewer-export-package-integration") == (
        "ai-reviewer-export-package-integration"
    )
    assert resolved.canonical_name == "ai-reviewer-export-package-integration"
    assert callable(resolved.handler)
    assert task["task_id"] == "day136_ai_reviewer_export_package_integration"
    assert task["day"] == "Day136"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "ai_reviewer_export_package_integration.py"
    assert "This is not next-day functionality" in task["notes"]
    assert "Execution / provider / API remain disabled" in task["notes"]


def test_day136_write_reports_and_report_index_visibility(tmp_path):
    report = day136.build_ai_reviewer_export_package_integration_report(PROJECT_ROOT)
    json_path, html_path = day136.write_ai_reviewer_export_package_integration_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["status"] == "AI_REVIEWER_EXPORT_PACKAGE_READY"
    assert "Day136" in index_html
    assert "AI Reviewer Export Package Integration" in index_html
    assert "reports/lab-summary/day136_ai_reviewer_export_package_integration.json" in index_html


def test_day136_module_does_not_read_secrets_env_call_network_or_import_execution_surfaces():
    source = Path(day136.__file__).read_text(encoding="utf-8")

    forbidden_fragments = (
        "os.environ",
        "getenv(",
        "requests.",
        "urllib.",
        "http.client",
        "socket.",
        "paramiko",
        "netmiko",
        "openai",
        "subprocess",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source.lower()


def test_day136_docs_preserve_agents_pre_read_and_required_statements():
    doc = (PROJECT_ROOT / "docs/roadmap/day136_ai_reviewer_export_package_integration.md").read_text(
        encoding="utf-8"
    )

    assert "AGENTS.md found: YES" in doc
    assert "AGENTS.md pre-read before changes: YES" in doc
    assert "AGENTS.md modified: NO" in doc
    assert "This is not next-day functionality." in doc
    assert "Execution / provider / API remain disabled." in doc
    assert "execution_enabled: false" in doc
    assert "provider_enabled: false" in doc
    assert "api_enabled: false" in doc
    assert "live_actions_enabled: false" in doc
