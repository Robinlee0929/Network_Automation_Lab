import json
from pathlib import Path

import network_lab
import network_lab_cli_dispatch
import project_folder_organization_decision_gate as day137
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SAFETY_FALSE_FIELDS = (
    "moves_allowed",
    "deletes_allowed",
    "renames_allowed",
    "import_path_changes_allowed",
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "next_feature_allowed",
    "original_day137_ai_assistance_demo_allowed",
)


def test_day137_decision_gate_contains_required_safety_fields():
    report = day137.build_project_folder_organization_decision_gate_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "PROJECT_FOLDER_ORGANIZATION_DECISION_RECORDED"
    assert report["day"] == 137
    assert report["task"] == "project-folder-organization-decision-gate"
    assert report["mode"] == "DECISION_ONLY"
    assert report["decision_only"] is True
    assert report["report_only"] is True
    assert report["final_recommendation"] == "DO_NOT_REORGANIZE_YET_DECISION_ONLY"
    assert report["validation_errors"] == []
    assert report["agents_md_found"] is True
    assert report["agents_md_pre_read_before_changes"] is True
    assert report["agents_md_modified"] is False

    for field in SAFETY_FALSE_FIELDS:
        assert report[field] is False


def test_day137_lists_blocked_groups_and_coupled_paths():
    report = day137.build_project_folder_organization_decision_gate_report(PROJECT_ROOT)
    high_risk_groups = {
        item["group"]: item
        for item in report["folder_groups_high_risk_do_not_move_first"]
    }

    assert high_risk_groups["CLI entry point"]["paths"] == ["network_lab.py"]
    assert high_risk_groups["registry and dispatch modules"]["move_allowed_now"] is False
    assert high_risk_groups["report-index modules and templates"]["move_allowed_now"] is False
    assert high_risk_groups["AI reviewer and provider-disabled evidence"]["move_allowed_now"] is False
    assert high_risk_groups["tests"]["move_allowed_now"] is False
    assert high_risk_groups["generated reports and historical evidence"]["move_allowed_now"] is False

    coupled = {item["path"]: item["coupled_to"] for item in report["coupled_paths"]}
    assert "CLI" in coupled["network_lab.py"]
    assert "registry" in coupled["network_lab_task_registry.py"]
    assert "dispatch" in coupled["network_lab_cli_dispatch.py"]
    assert "report-index" in coupled["reports/**"]
    assert "Day136 stability" in coupled["ai_reviewer_export_package_integration.py"]


def test_day137_preserves_day134_day136_ai_reviewer_export_package_stability():
    report = day137.build_project_folder_organization_decision_gate_report(PROJECT_ROOT)
    stability = report["day134_day136_stability_evidence"]

    assert stability["source_day_range"] == "Day134-Day136"
    assert stability["source_count"] == 3
    assert stability["loaded_source_count"] == 3
    assert stability["preserved"] is True
    assert stability["errors"] == []
    assert [section["day"] for section in stability["sections"]] == [134, 135, 136]
    for section in stability["sections"]:
        assert section["read_only"] is True
        assert section["loaded"] is True
        assert section["overall_status"] == "PASS"
        assert section["dangerous_true_fields"] == []
        assert section["provider_enabled"] is False
        assert section["api_enabled"] is False
        assert section["execution_enabled"] is False


def test_day137_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day137 decision gate must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day137 decision gate must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "project-folder-organization-decision-gate"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: project-folder-organization-decision-gate" in output
    assert "This is not the next day's feature." in output
    assert "Original Day137 AI Assistance Review Demo Package is deferred." in output
    assert "Execution / provider / API remain disabled." in output
    assert "moves_allowed: false" in output
    assert "deletes_allowed: false" in output
    assert "renames_allowed: false" in output
    assert "import_path_changes_allowed: false" in output
    assert "execution_allowed: false" in output
    assert "provider_allowed: false" in output
    assert "api_allowed: false" in output
    assert "original_day137_ai_assistance_demo_allowed: false" in output
    assert "final_recommendation: \"DO_NOT_REORGANIZE_YET_DECISION_ONLY\"" in output
    assert "[PASS] PROJECT_FOLDER_ORGANIZATION_DECISION_RECORDED" in output


def test_day137_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "project-folder-organization-decision-gate"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "project-folder-organization-decision-gate"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("project-folder-organization-decision-gate", handlers)

    assert resolve_task_name("project-folder-organization-decision-gate") == (
        "project-folder-organization-decision-gate"
    )
    assert resolved.canonical_name == "project-folder-organization-decision-gate"
    assert callable(resolved.handler)
    assert task["task_id"] == "day137_project_folder_organization_decision_gate"
    assert task["day"] == "Day137"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "project_folder_organization_decision_gate.py"
    assert "DO_NOT_REORGANIZE_YET_DECISION_ONLY" in task["notes"]
    assert "does not implement the original Day137 AI Assistance Review Demo Package" in task["notes"]


def test_day137_write_reports_and_report_index_visibility(tmp_path):
    report = day137.build_project_folder_organization_decision_gate_report(PROJECT_ROOT)
    json_path, html_path = day137.write_project_folder_organization_decision_gate_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["final_recommendation"] == "DO_NOT_REORGANIZE_YET_DECISION_ONLY"
    assert "Day137" in index_html
    assert "Project Folder Organization Decision Gate" in index_html
    assert "reports/lab-summary/day137_project_folder_organization_decision_gate.json" in index_html


def test_day137_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day137.__file__).read_text(encoding="utf-8").lower()

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


def test_day137_docs_preserve_required_boundary_statements():
    doc = (PROJECT_ROOT / "docs/roadmap/day137_project_folder_organization_decision_gate.md").read_text(
        encoding="utf-8"
    )

    assert "AGENTS.md pre-read before changes | YES" in doc
    assert "This is not the next day's feature." in doc
    assert "This does not implement the original Day137 AI Assistance Review Demo Package." in doc
    assert "This does not open execution, provider behavior, API behavior" in doc
    assert "No files were moved, deleted, renamed, or import paths changed." in doc
    assert "Folder restructuring is deferred." in doc
    assert "Day137-Day140 should be used for folder organization decision and dry-run gates." in doc
    assert "Day141-Day144 may resume the original AI Assistance line" in doc
    assert "DO_NOT_REORGANIZE_YET_DECISION_ONLY" in doc
