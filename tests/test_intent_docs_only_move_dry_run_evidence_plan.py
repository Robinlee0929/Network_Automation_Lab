import json
from pathlib import Path

import network_lab
import network_lab_cli_dispatch
import intent_docs_only_move_dry_run_evidence_plan as day139
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


SAFETY_FALSE_FIELDS = (
    "files_moved",
    "files_renamed",
    "imports_modified",
    "source_import_paths_modified",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "adapter_enabled",
    "ssh_enabled",
    "live_command_enabled",
    "next_phase_allowed",
)


def test_day139_docs_only_move_dry_run_evidence_plan_contains_required_safety_fields():
    report = day139.build_docs_only_move_dry_run_evidence_plan_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_RECORDED"
    assert report["day"] == "Day139"
    assert report["task"] == "docs-only-move-dry-run-evidence-plan"
    assert report["title"] == "Docs-Only Move Dry-Run Evidence Plan"
    assert report["mode"] == "REVIEW_ONLY"
    assert report["based_on_day"] == "Day138"
    assert report["source_scope"] == "docs-only"
    assert report["agents_md_read_before_day139_work"] is True
    assert report["dry_run_only"] is True
    assert report["review_only"] is True
    assert report["docs_only"] is True
    assert report["not_next_day_feature"] is True
    assert report["not_day140"] is True
    assert report["final_recommendation"] == "KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET"
    assert report["validation_errors"] == []

    for field in SAFETY_FALSE_FIELDS:
        assert report[field] is False
        assert report["safety_invariants"][field] is False


def test_day139_docs_only_move_pairs_and_diff_preview_are_docs_only_and_not_allowed():
    report = day139.build_docs_only_move_dry_run_evidence_plan_report(PROJECT_ROOT)

    assert report["hypothetical_docs_target_folders"]
    assert report["docs_only_dry_run_move_pairs"]
    assert report["proposal_diff_preview"]
    assert report["affected_doc_paths"]
    assert report["affected_doc_links"]
    assert report["affected_report_index_paths"]

    for pair in report["docs_only_dry_run_move_pairs"]:
        assert pair["current_path"].startswith("docs/")
        assert pair["hypothetical_target_path"].startswith("docs/")
        assert pair["source_scope"] == "docs-only"
        assert pair["move_allowed_now"] is False
        assert pair["dry_run_only"] is True

    for preview in report["proposal_diff_preview"]:
        assert preview["applied"] is False
        assert "DRY-RUN ONLY" in preview["preview"]


def test_day139_migration_risk_matrix_blocks_all_migrations():
    report = day139.build_docs_only_move_dry_run_evidence_plan_report(PROJECT_ROOT)
    risks = {row["risk_id"]: row for row in report["migration_risk_matrix"]}

    for risk_id, *_rest in day139.RISK_CATEGORIES:
        assert risk_id in risks
        assert risks[risk_id]["migration_allowed_now"] is False
        assert risks[risk_id]["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
        assert risks[risk_id]["mitigation"]


def test_day139_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day139 docs-only dry-run evidence plan must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day139 docs-only dry-run evidence plan must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "docs-only-move-dry-run-evidence-plan"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: docs-only-move-dry-run-evidence-plan" in output
    assert "This is not the next-day feature implementation." in output
    assert "This is not Day140." in output
    assert "No execution, provider, or API is enabled." in output
    assert "agents_md_read_before_day139_work: true" in output
    assert "final_recommendation: \"KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET\"" in output
    for field in SAFETY_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_RECORDED" in output


def test_day139_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "docs-only-move-dry-run-evidence-plan"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "docs-only-move-dry-run-evidence-plan"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("docs-only-move-dry-run-evidence-plan", handlers)

    assert resolve_task_name("docs-only-move-dry-run-evidence-plan") == (
        "docs-only-move-dry-run-evidence-plan"
    )
    assert resolved.canonical_name == "docs-only-move-dry-run-evidence-plan"
    assert callable(resolved.handler)
    assert task["task_id"] == "day139_docs_only_move_dry_run_evidence_plan"
    assert task["day"] == "Day139"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_docs_only_move_dry_run_evidence_plan.py"
    assert "KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET" in task["notes"]
    assert "not Day140" in task["notes"]
    assert "docs-only" in task["notes"]


def test_day139_write_reports_and_report_index_visibility(tmp_path):
    report = day139.build_docs_only_move_dry_run_evidence_plan_report(PROJECT_ROOT)
    json_path, html_path = day139.write_docs_only_move_dry_run_evidence_plan_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["final_recommendation"] == "KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET"
    assert written["next_phase_allowed"] is False
    assert "Day139" in index_html
    assert "Docs-Only Move Dry-Run Evidence Plan" in index_html
    assert "reports/lab-summary/day139_docs_only_move_dry_run_evidence_plan.json" in index_html


def test_day139_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day139.__file__).read_text(encoding="utf-8").lower()

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


def test_day139_docs_preserve_required_boundary_statements():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day139_docs_only_move_dry_run_evidence_plan.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day139_docs_only_move_dry_run_evidence_plan.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "This is not the next-day feature implementation." in doc
        assert "This is not Day140." in doc
        assert "No execution, provider, or API is enabled." in doc
        assert "docs-only-move-dry-run-evidence-plan" in doc
        assert "KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET" in doc
        assert "next_phase_allowed" in doc
        assert "files_moved" in doc or "Do not move files." in doc
        assert "imports_modified" in doc or "Do not modify import statements." in doc

    assert "AGENTS.md read before Day139 work | YES" in roadmap
