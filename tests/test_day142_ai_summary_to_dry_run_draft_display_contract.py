import copy
import json
from pathlib import Path

import day142_ai_summary_to_dry_run_draft_display_contract as day142
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day142_report_maps_already_produced_summary_to_display_only_payload():
    report = day142.build_day142_ai_summary_to_dry_run_draft_display_contract(PROJECT_ROOT)
    payload = report["display_payload"]

    assert report["overall_status"] == "PASS"
    assert report["status"] == "AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_READY"
    assert report["day"] == 142
    assert report["day_label"] == "Day142"
    assert report["task"] == "ai-summary-to-dry-run-draft-display-contract"
    assert report["mode"] == "REVIEW_ONLY_DISPLAY_CONTRACT"
    assert report["agents_md_read_before_day142_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["source_summary_input_mode"] == "already_produced_reviewer_text_metadata"
    assert payload["source_summary_id"] == "day127-example-ai-reviewer-summary"
    assert payload["source_summary_status"] == "REVIEW_ONLY"
    assert payload["draft_display_title"] == "Dry-run Draft Review: day127-example-ai-reviewer-summary"
    assert payload["draft_display_sections"]
    assert payload["safety_banner"].startswith("REVIEW_ONLY_DISPLAY")
    assert payload["review_required"] is True
    assert payload["next_phase_allowed"] is False
    assert report["final_recommendation"] == "REVIEW_ONLY_DISPLAY_CONTRACT_KEEP_NEXT_PHASE_FALSE"
    assert report["validation_errors"] == []


def test_day142_required_safety_flags_remain_false_in_report_and_display_payload():
    report = day142.build_day142_ai_summary_to_dry_run_draft_display_contract(PROJECT_ROOT)

    for field in day142.REQUIRED_FALSE_FIELDS:
        assert report[field] is False
        assert report["display_payload"]["non_execution_guards"][field] is False

    for field in day142.REQUIRED_TRUE_FIELDS:
        assert report[field] is True


def test_day142_display_payload_excludes_execution_connection_secret_provider_and_apply_keys():
    report = day142.build_day142_ai_summary_to_dry_run_draft_display_contract(PROJECT_ROOT)
    payload_text = json.dumps(report["display_payload"], sort_keys=True).lower()

    assert day142._find_forbidden_display_payload_keys(report["display_payload"]) == []
    for forbidden_value in ("api_key", "password", "provider_credentials"):
        assert forbidden_value not in payload_text


def test_day142_negative_validation_blocks_enabled_paths_and_forbidden_payload_keys():
    report = day142.build_day142_ai_summary_to_dry_run_draft_display_contract(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_read_before_day142_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["display_payload"]["review_required"] = False
    unsafe["display_payload"]["next_phase_allowed"] = True
    unsafe["display_payload"]["non_execution_guards"]["provider_enabled"] = True
    unsafe["display_payload"]["device_connection_parameters"] = {"host": "192.0.2.10"}
    unsafe["display_payload"]["apply_actions"] = ["commit"]
    unsafe["day141_validation_fix_redone"] = True

    for field in day142.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day142.collect_validation_errors(unsafe)

    assert "agents_md_read_before_day142_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors
    assert "display_payload.review_required must be true." in errors
    assert "display_payload.next_phase_allowed must be false." in errors
    assert "display_payload.non_execution_guards.provider_enabled must be false." in errors
    assert "display_payload contains forbidden keys: apply_actions, device_connection_parameters, host" in errors
    assert "day141_validation_fix_redone must be false." in errors
    for field in day142.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day142_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_profile_load(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day142 display contract must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day142 display contract must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-summary-to-dry-run-draft-display-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-summary-to-dry-run-draft-display-contract" in output
    assert "Day142 treats AI summary input as already-produced reviewer text/metadata." in output
    assert "Day142 dry-run draft output is display-only and review-only." in output
    assert "Day142 enables no provider, API, or model invocation." in output
    assert "Day142 does not redo, extend, rename, or re-validate Day141." in output
    assert "display_payload.review_required: true" in output
    assert "display_payload.next_phase_allowed: false" in output
    for field in day142.REQUIRED_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_READY" in output


def test_day142_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-summary-to-dry-run-draft-display-contract"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-summary-to-dry-run-draft-display-contract"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-summary-to-dry-run-draft-display-contract", handlers)

    assert resolve_task_name("ai-summary-to-dry-run-draft-display-contract") == (
        "ai-summary-to-dry-run-draft-display-contract"
    )
    assert resolved.canonical_name == "ai-summary-to-dry-run-draft-display-contract"
    assert callable(resolved.handler)
    assert task["task_id"] == "day142_ai_summary_to_dry_run_draft_display_contract"
    assert task["day"] == "Day142"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day142_ai_summary_to_dry_run_draft_display_contract.py"
    assert "display-only" in task["notes"]
    assert "provider_enabled=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day142_write_reports_and_report_index_visibility(tmp_path):
    report = day142.build_day142_ai_summary_to_dry_run_draft_display_contract(
        PROJECT_ROOT,
        source_summary=day142.build_example_source_summary(),
    )
    json_path, html_path = day142.write_day142_ai_summary_to_dry_run_draft_display_contract_reports(
        tmp_path,
        report,
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["status"] == "AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_READY"
    assert written["provider_enabled"] is False
    assert written["next_phase_allowed"] is False
    assert "Day142" in index_html
    assert "AI Summary to Dry-run Draft Display Contract" in index_html
    assert "reports/lab-summary/day142_ai_summary_to_dry_run_draft_display_contract.json" in index_html


def test_day142_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day142.__file__).read_text(encoding="utf-8").lower()

    forbidden_fragments = (
        "import os",
        "os.environ",
        "getenv(",
        "import requests",
        "import urllib",
        "import http.client",
        "import socket",
        "import paramiko",
        "import netmiko",
        "import openai",
        "import subprocess",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day142_docs_preserve_required_boundary_statements():
    roadmap = (
        PROJECT_ROOT / "docs/roadmap/day142_ai_summary_to_dry_run_draft_display_contract.md"
    ).read_text(encoding="utf-8")
    ai_intent = (
        PROJECT_ROOT / "docs/ai-intent/day142_ai_summary_to_dry_run_draft_display_contract.md"
    ).read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "Day142 treats AI summary input as already-produced reviewer text/metadata." in doc
        assert "Day142 dry-run draft output is display-only and review-only." in doc
        assert "Day142 enables no provider, API, or model invocation." in doc
        assert "Day142 does not redo, extend, rename, or re-validate Day141." in doc
        assert "provider_enabled: false" in doc
        assert "api_enabled: false" in doc
        assert "model_invocation_enabled: false" in doc
        assert "execution_enabled: false" in doc
        assert "ssh_allowed: false" in doc
        assert "netconf_allowed: false" in doc
        assert "restconf_allowed: false" in doc
        assert "live_device_allowed: false" in doc
        assert "config_write_allowed: false" in doc
        assert "command_apply_allowed: false" in doc
        assert "adapter_invoked: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "REVIEW_ONLY_DISPLAY_CONTRACT_KEEP_NEXT_PHASE_FALSE" in doc

    assert "AGENTS.md read before Day142 work | YES" in roadmap
    assert "AGENTS.md pre-read result | PASS" in roadmap

