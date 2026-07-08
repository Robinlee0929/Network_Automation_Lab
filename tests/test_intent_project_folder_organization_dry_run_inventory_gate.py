import json
from copy import deepcopy
from pathlib import Path

import pytest

import network_lab
import network_lab_cli_dispatch
import intent_project_folder_organization_dry_run_inventory_gate as day138
from network_lab_task_registry import resolve_task_handler, resolve_task_name
from report_file_utils import path_exists, read_text_with_long_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


FORBIDDEN_ACTIONS = (
    "move",
    "delete",
    "rename",
    "import_path_change",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "ssh_allowed",
    "live_command_allowed",
)


@pytest.fixture(scope="module")
def day138_report_cache():
    return day138.build_project_folder_organization_dry_run_inventory_gate_report(PROJECT_ROOT)


@pytest.fixture
def day138_report(day138_report_cache):
    return deepcopy(day138_report_cache)


def test_day138_dry_run_inventory_gate_contains_required_safety_fields(day138_report):
    report = day138_report

    assert report["overall_status"] == "PASS"
    assert report["status"] == "PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_RECORDED"
    assert report["day"] == 138
    assert report["task"] == "project-folder-organization-dry-run-inventory-gate"
    assert report["mode"] == "DRY_RUN_INVENTORY_ONLY"
    assert report["report_only"] is True
    assert report["dry_run_only"] is True
    assert report["mock_safe"] is True
    assert report["agents_md_pre_read"] is True
    assert report["final_recommendation"] == "KEEP_DRY_RUN_INVENTORY_ONLY"
    assert report["next_phase_allowed"] is False
    assert report["not_next_day_feature_statement"] == "This is not the next day's feature."
    assert report["no_execution_provider_api_statement"] == "No execution, provider, or API is enabled."
    assert report["validation_errors"] == []

    for action in FORBIDDEN_ACTIONS:
        assert report["forbidden_actions"][action] is False
        assert report["explicit_no_change_proof"][action] is False


def test_day138_inventory_groups_include_required_groups_and_risk_levels(day138_report):
    report = day138_report
    groups = {group["group_name"]: group for group in report["inventory_groups"]}

    for group_name in day138.REQUIRED_GROUPS:
        assert group_name in groups
        assert isinstance(groups[group_name]["file_count"], int)
        assert isinstance(groups[group_name]["sample_files"], list)
        assert groups[group_name]["current_location"]
        assert groups[group_name]["risk_level"] in {"HIGH", "MEDIUM", "LOW"}
        assert groups[group_name]["reason"]

    assert groups["root CLI / entrypoint files"]["risk_level"] == "HIGH"
    assert groups["task registry / dispatch files"]["risk_level"] == "HIGH"
    assert groups["intent / task modules"]["risk_level"] == "HIGH"
    assert groups["tests"]["risk_level"] == "HIGH"
    assert groups["docs / roadmap"]["risk_level"] == "LOW"
    assert groups["docs / ai-intent"]["risk_level"] == "LOW"
    assert groups["reports / lab-summary"]["risk_level"] == "LOW"

    risks = {group["risk_level"] for group in report["inventory_groups"]}
    assert "HIGH" in risks
    assert "LOW" in risks


def test_day138_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    day138_report,
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day138 dry-run inventory gate must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day138 dry-run inventory gate must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(
        day138,
        "build_project_folder_organization_dry_run_inventory_gate_report",
        lambda project_root: deepcopy(day138_report),
    )

    exit_code = network_lab.main(
        ["--task", "project-folder-organization-dry-run-inventory-gate"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: project-folder-organization-dry-run-inventory-gate" in output
    assert "This is not the next day's feature." in output
    assert "No execution, provider, or API is enabled." in output
    assert "final_recommendation: \"KEEP_DRY_RUN_INVENTORY_ONLY\"" in output
    assert "next_phase_allowed: false" in output
    assert "agents_md_pre_read: true" in output
    for action in FORBIDDEN_ACTIONS:
        assert f"forbidden_actions.{action}: false" in output
    assert "[PASS] PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_RECORDED" in output


def test_day138_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "project-folder-organization-dry-run-inventory-gate"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "project-folder-organization-dry-run-inventory-gate"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("project-folder-organization-dry-run-inventory-gate", handlers)

    assert resolve_task_name("project-folder-organization-dry-run-inventory-gate") == (
        "project-folder-organization-dry-run-inventory-gate"
    )
    assert resolved.canonical_name == "project-folder-organization-dry-run-inventory-gate"
    assert callable(resolved.handler)
    assert task["task_id"] == "day138_project_folder_organization_dry_run_inventory_gate"
    assert task["day"] == "Day138"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_project_folder_organization_dry_run_inventory_gate.py"
    assert "KEEP_DRY_RUN_INVENTORY_ONLY" in task["notes"]
    assert "This is not the next day's feature" in task["notes"]
    assert "Does not move, delete, rename, change import paths" in task["notes"]


def test_day138_write_reports_and_report_index_visibility(day138_report, tmp_path):
    report = day138_report
    json_path, html_path = day138.write_project_folder_organization_dry_run_inventory_gate_reports(
        tmp_path,
        report,
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = read_text_with_long_path(tmp_path / "reports" / "report_index.html", encoding="utf-8")
    written = json.loads(read_text_with_long_path(json_path, encoding="utf-8"))

    assert exit_code == 0
    assert path_exists(json_path)
    assert path_exists(html_path)
    assert written["overall_status"] == "PASS"
    assert written["final_recommendation"] == "KEEP_DRY_RUN_INVENTORY_ONLY"
    assert written["next_phase_allowed"] is False
    assert "Day138" in index_html
    assert "Project Folder Organization Dry-Run Inventory Gate" in index_html
    assert "reports/lab-summary/day138_project_folder_organization_dry_run_inventory_gate.json" in index_html


def test_day138_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day138.__file__).read_text(encoding="utf-8").lower()

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


def test_day138_docs_preserve_required_boundary_statements():
    roadmap = (
        PROJECT_ROOT / "docs/roadmap/day138_project_folder_organization_dry_run_inventory_gate.md"
    ).read_text(encoding="utf-8")
    ai_intent = (
        PROJECT_ROOT / "docs/ai-intent/day138_project_folder_organization_dry_run_inventory_gate.md"
    ).read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "This is not the next day's feature." in doc
        assert "No execution, provider, or API is enabled." in doc
        assert "KEEP_DRY_RUN_INVENTORY_ONLY" in doc
        assert "next_phase_allowed" in doc
        assert "move" in doc
        assert "delete" in doc
        assert "rename" in doc
        assert "import_path_change" in doc or "import paths" in doc

    assert "AGENTS.md pre-read before changes | YES" in roadmap
