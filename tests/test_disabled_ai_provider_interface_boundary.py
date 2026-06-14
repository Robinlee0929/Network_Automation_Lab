import json
from pathlib import Path

import disabled_ai_provider_interface_boundary as day133
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


DISABLED_FALSE_FIELDS = (
    "provider_enabled",
    "execution_enabled",
    "api_enabled",
    "network_call_enabled",
    "secrets_required",
    "external_sdk_required",
    "live_ai_call_enabled",
    "adapter_contract_enabled",
    "day134_feature_enabled",
    "next_day_feature_enabled",
    "provider_adapter_enabled",
    "vendor_sdk_integration_enabled",
    "prompt_submission_enabled",
    "model_selection_enabled",
    "retry_rate_limit_timeout_behavior_enabled",
    "async_job_enabled",
)


def test_day133_boundary_report_is_disabled_review_only_and_deterministic():
    first = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)
    second = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["boundary_status"] == "AI_PROVIDER_INTERFACE_DISABLED"
    assert first["day"] == "Day133"
    assert first["task"] == "disabled-ai-provider-interface-boundary"
    assert first["provider_interface_boundary_created"] is True
    assert first["review_only"] is True
    assert first["deterministic_only"] is True
    assert first["local_only"] is True
    assert first["report_only"] is True
    assert first["validation_errors"] == []


def test_day133_required_provider_execution_api_flags_remain_false():
    report = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)

    for field in DISABLED_FALSE_FIELDS:
        assert report[field] is False

    assert all(value is False for value in report["no_execution_evidence"].values())


def test_day133_boundary_text_excludes_day134_and_execution_provider_api():
    report = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)
    boundary_text = "\n".join(report["boundary_text"])

    assert report["boundary_message"] == "This is not Day134 adapter contract."
    assert report["no_execution_message"] == "No execution/provider/API is enabled."
    assert "not Day134" in boundary_text
    assert "No execution/provider/API" in boundary_text
    assert "Day133 is not the next-day feature." in boundary_text


def test_day133_agents_md_status_is_visible():
    report = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)

    assert report["agents_md_status"] == "FOUND_AND_READ"
    assert report["agents_md_read_before_day133_work"] is True
    assert report["agents_md_evidence"]["agents_md_status"] == "FOUND_AND_READ"


def test_day133_cli_task_reports_pass_and_no_execution_boundaries(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day133 disabled provider boundary must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day133 disabled provider boundary must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "disabled-ai-provider-interface-boundary"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: disabled-ai-provider-interface-boundary" in output
    assert "AGENTS.md status: FOUND_AND_READ" in output
    assert "This is not Day134 adapter contract." in output
    assert "No execution/provider/API is enabled." in output
    assert "provider_enabled: false" in output
    assert "execution_enabled: false" in output
    assert "api_enabled: false" in output
    assert "network_call_enabled: false" in output
    assert "secrets_required: false" in output
    assert "live_ai_call_enabled: false" in output
    assert "adapter_contract_enabled: false" in output
    assert "day134_feature_enabled: false" in output
    assert "[PASS] AI_PROVIDER_INTERFACE_DISABLED" in output


def test_day133_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "disabled-ai-provider-interface-boundary"
    )

    assert resolve_task_name("disabled-ai-provider-interface-boundary") == (
        "disabled-ai-provider-interface-boundary"
    )
    assert task["task_id"] == "day133_disabled_ai_provider_interface_boundary"
    assert task["day"] == "Day133"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "disabled_ai_provider_interface_boundary.py"
    assert "Disabled AI Provider Interface Boundary" in task["display_name"]
    assert "not Day134 adapter contract" in task["notes"]
    assert "does not enable execution/provider/API" in task["notes"]


def test_day133_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "disabled-ai-provider-interface-boundary"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("disabled-ai-provider-interface-boundary", handlers)

    assert resolved.canonical_name == "disabled-ai-provider-interface-boundary"
    assert callable(resolved.handler)


def test_day133_write_reports_and_report_index_visibility(tmp_path):
    report = day133.build_disabled_ai_provider_interface_boundary_report(PROJECT_ROOT)
    json_path, html_path = day133.write_disabled_ai_provider_interface_boundary_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["boundary_status"] == "AI_PROVIDER_INTERFACE_DISABLED"
    assert "Day133" in index_html
    assert "Disabled AI Provider Interface Boundary" in index_html


def test_day133_docs_exist_and_preserve_disabled_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day133_disabled_ai_provider_interface_boundary.md",
        PROJECT_ROOT / "docs/roadmap/day133_disabled_ai_provider_interface_boundary.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "disabled ai provider interface boundary" in text
        assert "not day134 adapter contract" in text
        assert "no execution/provider/api is enabled" in text
        assert "provider_enabled: false" in text
        assert "execution_enabled: false" in text
        assert "api_enabled: false" in text
        assert "network_call_enabled: false" in text
        assert "secrets_required: false" in text
        assert "live_ai_call_enabled: false" in text
        assert "adapter_contract_enabled: false" in text
        assert "day134_feature_enabled: false" in text
        assert "next_day_feature_enabled: false" in text
        assert "review_only: true" in text
