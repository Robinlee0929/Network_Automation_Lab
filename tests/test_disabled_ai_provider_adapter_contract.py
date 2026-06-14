import importlib
import json
from pathlib import Path

import disabled_ai_provider_adapter_contract as day134
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


DISABLED_FALSE_FIELDS = (
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "api_key_required",
    "live_backend_enabled",
    "next_phase_allowed",
    "provider_sdk_required",
    "provider_sdk_imported",
    "environment_config_required",
    "prompt_submission_enabled",
    "model_selection_enabled",
    "async_client_enabled",
    "subprocess_provider_enabled",
    "broker_runner_adapter_execution_enabled",
    "day135_feature_enabled",
)


def test_day134_adapter_contract_report_is_disabled_review_only_and_deterministic():
    first = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)
    second = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["result"] == "DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY"
    assert first["day"] == "Day134"
    assert first["task"] == "disabled-ai-provider-adapter-contract"
    assert first["adapter_contract_defined"] is True
    assert first["adapter_is_disabled"] is True
    assert first["review_only"] is True
    assert first["deterministic_response"] is True
    assert first["local_only"] is True
    assert first["report_only"] is True
    assert first["validation_errors"] == []


def test_day134_disabled_adapter_cannot_invoke_provider():
    contract = day134.build_disabled_ai_provider_adapter_contract()
    request = day134.DisabledAIProviderRequest()
    response = contract.summarize(request)

    assert response.status == "PASS"
    assert response.result == "DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY"
    assert response.provider_invoked is False
    assert response.api_called is False
    assert response.model_invoked is False
    assert response.network_called is False
    assert response.execution_path_reached is False
    assert response.next_phase_allowed is False


def test_day134_rejects_provider_payloads_before_any_execution_path():
    contract = day134.build_disabled_ai_provider_adapter_contract()
    request = day134.DisabledAIProviderRequest(provider_payload_allowed=True)

    try:
        contract.summarize(request)
    except RuntimeError as exc:
        assert str(exc) == "Provider payloads are disabled for Day134."
    else:
        raise AssertionError("Day134 must reject provider payloads")


def test_day134_required_provider_api_execution_flags_remain_false():
    report = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)

    for field in DISABLED_FALSE_FIELDS:
        assert report[field] is False

    assert all(value is False for value in report["no_execution_evidence"].values())
    assert report["api_key_required"] is False
    assert report["next_phase_allowed"] is False


def test_day134_no_provider_sdk_import_or_api_key_config_needed():
    report = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)
    module_source = Path(day134.__file__).read_text(encoding="utf-8")

    assert importlib.import_module("disabled_ai_provider_adapter_contract") is day134
    assert report["provider_sdk_required"] is False
    assert report["provider_sdk_imported"] is False
    assert report["environment_config_required"] is False
    assert "import openai" not in module_source.lower()
    assert "from openai" not in module_source.lower()
    assert "import anthropic" not in module_source.lower()
    assert "from anthropic" not in module_source.lower()
    assert "google.generativeai" not in module_source.lower()
    assert "os.environ" not in module_source


def test_day134_contract_text_is_not_next_day_feature():
    report = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)
    contract_text = "\n".join(report["contract_text"])

    assert report["not_next_day_feature"] is True
    assert report["contract_message"] == "Disabled AI provider adapter contract shape only."
    assert report["disabled_response_message"] == (
        "Provider adapter contract is defined, disabled, and not invoked."
    )
    assert "not the next day's feature" in contract_text
    assert "contract shape" in contract_text
    assert "No provider/API/model/network/execution path is enabled." in contract_text


def test_day134_agents_md_status_is_visible():
    report = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)

    assert report["agents_md_status"] == "FOUND_AND_READ"
    assert report["agents_md_read_before_day134_work"] is True
    assert report["agents_md_evidence"]["agents_md_status"] == "FOUND_AND_READ"


def test_day134_cli_task_reports_pass_and_no_execution_boundaries(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day134 disabled provider adapter contract must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day134 disabled provider adapter contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "disabled-ai-provider-adapter-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: disabled-ai-provider-adapter-contract" in output
    assert "AGENTS.md status: FOUND_AND_READ" in output
    assert "Disabled AI provider adapter contract shape only." in output
    assert "Provider adapter contract is defined, disabled, and not invoked." in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "execution_enabled: false" in output
    assert "model_invocation_enabled: false" in output
    assert "network_enabled: false" in output
    assert "api_key_required: false" in output
    assert "live_backend_enabled: false" in output
    assert "adapter_is_disabled: true" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY" in output


def test_day134_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "disabled-ai-provider-adapter-contract"
    )

    assert resolve_task_name("disabled-ai-provider-adapter-contract") == (
        "disabled-ai-provider-adapter-contract"
    )
    assert task["task_id"] == "day134_disabled_ai_provider_adapter_contract"
    assert task["day"] == "Day134"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "disabled_ai_provider_adapter_contract.py"
    assert "Disabled AI Provider Adapter Contract" in task["display_name"]
    assert "not the next day's feature" in task["notes"]
    assert "does not enable provider/API/model/network/execution" in task["notes"]


def test_day134_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "disabled-ai-provider-adapter-contract"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("disabled-ai-provider-adapter-contract", handlers)

    assert resolved.canonical_name == "disabled-ai-provider-adapter-contract"
    assert callable(resolved.handler)


def test_day134_write_reports_and_report_index_visibility(tmp_path):
    report = day134.build_disabled_ai_provider_adapter_contract_report(PROJECT_ROOT)
    json_path, html_path = day134.write_disabled_ai_provider_adapter_contract_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["result"] == "DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY"
    assert "Day134" in index_html
    assert "Disabled AI Provider Adapter Contract" in index_html


def test_day134_docs_exist_and_preserve_disabled_contract_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day134_disabled_ai_provider_adapter_contract.md",
        PROJECT_ROOT / "docs/roadmap/day134_disabled_ai_provider_adapter_contract.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "disabled ai provider adapter contract" in text
        assert "not the next day's feature" in text
        assert "provider_enabled: false" in text
        assert "api_enabled: false" in text
        assert "execution_enabled: false" in text
        assert "model_invocation_enabled: false" in text
        assert "network_enabled: false" in text
        assert "api_key_required: false" in text
        assert "live_backend_enabled: false" in text
        assert "adapter_is_disabled: true" in text
        assert "next_phase_allowed: false" in text
