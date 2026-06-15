import copy
import json
from pathlib import Path

import network_lab
import network_lab_cli_dispatch
import intent_folder_move_compatibility_gate as day140
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SAFETY_FALSE_FIELDS = (
    "execution_allowed",
    "provider_enabled",
    "api_enabled",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "live_command_allowed",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "next_day_feature_implemented",
    "move_allowed_now",
)


COUNT_ZERO_FIELDS = (
    "files_moved_count",
    "folders_moved_count",
    "imports_modified_count",
)


def test_day140_reports_agents_md_pre_read_and_required_safety_fields():
    report = day140.build_folder_move_compatibility_gate_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "FOLDER_MOVE_COMPATIBILITY_GATE_READY_FOR_FUTURE_DOCS_ONLY_REVIEW"
    assert report["day"] == 140
    assert report["day_label"] == "Day140"
    assert report["task"] == "folder-move-compatibility-gate"
    assert report["title"] == "Folder Move Compatibility Gate"
    assert report["mode"] == "REVIEW_ONLY"
    assert report["agents_md_read_before_day140_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["review_only"] is True
    assert report["report_only"] is True
    assert report["dry_run_only"] is True
    assert report["docs_only"] is True
    assert report["first_batch_docs_only_move_review_allowed"] is True
    assert report["final_recommendation"] == "READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW"
    assert report["validation_errors"] == []

    for field in COUNT_ZERO_FIELDS:
        assert report[field] == 0
        assert report["safety_invariants"][field] == 0
    for field in SAFETY_FALSE_FIELDS:
        assert report[field] is False
        assert report["safety_invariants"][field] is False


def test_day140_only_evaluates_future_docs_only_review_and_never_move_permission():
    report = day140.build_folder_move_compatibility_gate_report(PROJECT_ROOT)

    assert report["docs_only_move_candidates_identifiable"] is True
    assert report["candidate_docs_isolated_enough_for_review"] is True
    assert report["import_sensitive_files_excluded_from_first_batch"] is True
    assert report["cli_task_test_report_index_references_identified"] is True
    assert "future docs-only move review may begin" in report["review_only_decision_statement"]

    for candidate in report["docs_only_move_candidates"]:
        assert candidate["current_path"].startswith("docs/")
        assert candidate["extension"] == ".md"
        assert candidate["isolated_enough_for_future_review"] is True
        assert candidate["review_allowed_now"] is True
        assert candidate["move_allowed_now"] is False

    for exclusion in report["import_sensitive_exclusions"]:
        assert exclusion["excluded_from_first_batch"] is True
        assert exclusion["import_sensitive"] is True

    for reference in report["cli_task_test_report_index_reference_audit"]:
        assert reference["modified_now"] is False
        assert reference["execution_surface"] is False


def test_day140_negative_validation_blocks_moves_import_changes_and_execution_unlocks():
    report = day140.build_folder_move_compatibility_gate_report(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["files_moved_count"] = 1
    unsafe["folders_moved_count"] = 1
    unsafe["imports_modified_count"] = 1
    unsafe["execution_allowed"] = True
    unsafe["provider_enabled"] = True
    unsafe["api_enabled"] = True
    unsafe["ssh_allowed"] = True
    unsafe["netconf_allowed"] = True
    unsafe["restconf_allowed"] = True
    unsafe["live_command_allowed"] = True
    unsafe["adapter_execution_allowed"] = True
    unsafe["broker_execution_allowed"] = True
    unsafe["runner_execution_allowed"] = True
    unsafe["next_day_feature_implemented"] = True
    unsafe["agents_md_read_before_day140_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"

    errors = day140.collect_validation_errors(unsafe)

    assert "files_moved_count must be 0." in errors
    assert "folders_moved_count must be 0." in errors
    assert "imports_modified_count must be 0." in errors
    assert "execution_allowed must be false." in errors
    assert "provider_enabled must be false." in errors
    assert "api_enabled must be false." in errors
    assert "ssh_allowed must be false." in errors
    assert "netconf_allowed must be false." in errors
    assert "restconf_allowed must be false." in errors
    assert "live_command_allowed must be false." in errors
    assert "adapter_execution_allowed must be false." in errors
    assert "broker_execution_allowed must be false." in errors
    assert "runner_execution_allowed must be false." in errors
    assert "next_day_feature_implemented must be false." in errors
    assert "agents_md_read_before_day140_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors


def test_day140_rejects_non_docs_candidates_and_unexcluded_import_sensitive_files():
    report = day140.build_folder_move_compatibility_gate_report(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["docs_only_move_candidates"][0]["current_path"] = "network_lab.py"
    unsafe["docs_only_move_candidates"][0]["extension"] = ".py"
    unsafe["docs_only_move_candidates"][0]["move_allowed_now"] = True
    unsafe["import_sensitive_exclusions"][0]["excluded_from_first_batch"] = False

    errors = day140.collect_validation_errors(unsafe)

    assert "current_path must stay docs-only: network_lab.py" in errors
    assert "network_lab.py must be a Markdown documentation file." in errors
    assert "network_lab.py move_allowed_now must be false." in errors
    assert "*.py must be excluded from first batch." in errors


def test_day140_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day140 compatibility gate must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day140 compatibility gate must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "folder-move-compatibility-gate"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: folder-move-compatibility-gate" in output
    assert "This is not the next-day feature implementation." in output
    assert "No files or folders are moved by Day140." in output
    assert "No execution, provider, or API is enabled." in output
    assert "agents_md_read_before_day140_work: true" in output
    assert "agents_md_pre_read_result: \"PASS\"" in output
    assert "first_batch_docs_only_move_review_allowed: true" in output
    assert "final_recommendation: \"READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW\"" in output
    for field in COUNT_ZERO_FIELDS:
        assert f"{field}: 0" in output
    for field in SAFETY_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] FOLDER_MOVE_COMPATIBILITY_GATE_READY_FOR_FUTURE_DOCS_ONLY_REVIEW" in output


def test_day140_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "folder-move-compatibility-gate")
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "folder-move-compatibility-gate"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("folder-move-compatibility-gate", handlers)

    assert resolve_task_name("folder-move-compatibility-gate") == "folder-move-compatibility-gate"
    assert resolved.canonical_name == "folder-move-compatibility-gate"
    assert callable(resolved.handler)
    assert task["task_id"] == "day140_folder_move_compatibility_gate"
    assert task["day"] == "Day140"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_folder_move_compatibility_gate.py"
    assert "compatibility decision only" in task["notes"]
    assert "files_moved_count=0" in task["notes"]
    assert "next-day feature is not implemented" in task["notes"]


def test_day140_write_reports_and_report_index_visibility(tmp_path):
    report = day140.build_folder_move_compatibility_gate_report(PROJECT_ROOT)
    json_path, html_path = day140.write_folder_move_compatibility_gate_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["final_recommendation"] == "READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW"
    assert written["files_moved_count"] == 0
    assert "Day140" in index_html
    assert "Folder Move Compatibility Gate" in index_html
    assert "reports/lab-summary/day140_folder_move_compatibility_gate.json" in index_html


def test_day140_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day140.__file__).read_text(encoding="utf-8").lower()

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


def test_day140_docs_preserve_required_boundary_statements():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day140_folder_move_compatibility_gate.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day140_folder_move_compatibility_gate.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "This is not the next-day feature implementation." in doc
        assert "No execution, provider, or API is enabled." in doc
        assert "folder-move-compatibility-gate" in doc
        assert "READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW" in doc
        assert "files_moved_count" in doc
        assert "folders_moved_count" in doc
        assert "imports_modified_count" in doc
        assert "next_day_feature_implemented" in doc
        assert "never authorizes moving files now" in doc

    assert "AGENTS.md read before Day140 work | YES" in roadmap
    assert "AGENTS.md pre-read result | PASS" in roadmap
