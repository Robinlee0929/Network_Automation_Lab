import copy
import json
from pathlib import Path

import day149_ai_assistance_docs_registry_report_index_consistency_audit as day149
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name
from report_file_utils import path_exists, read_text_with_long_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day149_report_contains_required_scope_concepts_and_safety_flags():
    report = day149.build_day149_ai_assistance_docs_registry_report_index_consistency_audit(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "CONSISTENCY_AUDITED_REVIEW_ONLY"
    assert report["day"] == 149
    assert report["day_label"] == "Day149"
    assert report["task"] == "ai-assistance-docs-registry-report-index-consistency-audit"
    assert report["title"] == "AI Assistance Docs / Registry / Report Index Consistency Audit"
    assert report["mode"] == "REVIEW_ONLY_REPORT_ONLY_CONSISTENCY_AUDIT"
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day149_work"] is True
    assert report["agents_md_modified"] is False
    assert report["audit_scope"] == ["Day145", "Day146", "Day147", "Day148", "Day149"]
    assert report["required_concepts"] == list(day149.REQUIRED_CONCEPTS)
    assert report["mismatch_findings"] == []
    assert report["mismatch_finding_count"] == 0
    assert report["conclusion"] == "CONSISTENCY_AUDITED_REVIEW_ONLY"
    assert report["final_recommendation"] == (
        "KEEP_AI_ASSISTANCE_DOCS_REGISTRY_REPORT_INDEX_REVIEW_ONLY_AND_NEXT_PHASE_FALSE"
    )
    assert report["validation_errors"] == []

    for concept in (
        "NOT_NEXT_DAY_FUNCTIONALITY",
        "EXECUTION_PROVIDER_API_DISABLED",
        "REVIEW_ONLY",
        "REPORT_ONLY",
        "AGENTS_MD_FOUND_AND_READ",
        "AGENTS_MD_NOT_MODIFIED",
    ):
        assert concept in report["required_concepts"]
        assert concept in report["explicit_boundary_statements"]

    for field in day149.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day149.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day149_day_records_cover_day145_day149_without_mismatches():
    report = day149.build_day149_ai_assistance_docs_registry_report_index_consistency_audit(PROJECT_ROOT)

    assert [record["day_label"] for record in report["day_records"]] == [
        "Day145",
        "Day146",
        "Day147",
        "Day148",
        "Day149",
    ]
    for record in report["day_records"]:
        assert record["documentation_discoverable"] is True
        assert record["all_referenced_paths_exist_or_current_output"] is True
        assert record["day_label_consistency"] == "PASS"
        assert record["review_only"] is True
        assert record["report_only"] is True
        assert record["next_phase_allowed"] is False
        assert record["mismatch_findings"] == []
        assert record["mismatch_count"] == 0


def test_day149_cli_does_not_execute_provider_network_runner_or_prior_day_tasks(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day149 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day149 must not load runner profile or config data")

    def fail_day148(*args, **kwargs):
        raise AssertionError("Day149 must not rerun Day148")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day148_ai_assistance_display_consistency_audit", fail_day148)

    exit_code = network_lab.main(
        ["--task", "ai-assistance-docs-registry-report-index-consistency-audit"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md status: AGENTS_MD_FOUND_AND_READ" in output
    assert "AGENTS.md modified: false" in output
    assert "Day149 task: AI Assistance Docs / Registry / Report Index Consistency Audit" in output
    assert "Audit scope: Day145, Day146, Day147, Day148, Day149" in output
    assert "NOT_NEXT_DAY_FUNCTIONALITY" in output
    assert "EXECUTION_PROVIDER_API_DISABLED" in output
    assert "REVIEW_ONLY" in output
    assert "REPORT_ONLY" in output
    assert "AGENTS_MD_NOT_MODIFIED" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "model_call_enabled: false" in output
    assert "network_device_live_access_enabled: false" in output
    assert "adapter_broker_runner_enabled: false" in output
    assert "secrets_required: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] CONSISTENCY_AUDITED_REVIEW_ONLY" in output


def test_day149_negative_validation_blocks_unsafe_flags_and_mismatches():
    report = day149.build_day149_ai_assistance_docs_registry_report_index_consistency_audit(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["agents_md_read_before_day149_work"] = False
    unsafe["day_records"][0]["documentation_discoverable"] = False
    unsafe["day_records"][0]["mismatch_count"] = 1
    unsafe["consistency_checks"][0]["status"] = "FAIL"
    unsafe["mismatch_findings"] = [
        {
            "finding_id": "DAY149-TEST",
            "source_day": "Day145",
            "category": "TEST",
            "severity": "BLOCKING",
            "description": "synthetic mismatch",
        }
    ]
    unsafe["mismatch_finding_count"] = 1

    for field in day149.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day149.collect_validation_errors(unsafe)

    assert "agents_md_pre_read_result must be PASS." in errors
    assert "agents_md_read_before_day149_work must be true." in errors
    assert "mismatch_findings must be empty for PASS." in errors
    assert "mismatch_finding_count must be 0 for PASS." in errors
    assert "DAY149-CONSISTENCY-001 status must be PASS." in errors
    assert "Day145 documentation_discoverable must be true." in errors
    assert "Day145 mismatch_count must be 0." in errors
    for field in day149.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day149_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-assistance-docs-registry-report-index-consistency-audit"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-assistance-docs-registry-report-index-consistency-audit"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-assistance-docs-registry-report-index-consistency-audit", handlers)

    assert resolve_task_name("ai-assistance-docs-registry-report-index-consistency-audit") == (
        "ai-assistance-docs-registry-report-index-consistency-audit"
    )
    assert resolved.canonical_name == "ai-assistance-docs-registry-report-index-consistency-audit"
    assert callable(resolved.handler)
    assert task["task_id"] == "day149_ai_assistance_docs_registry_report_index_consistency_audit"
    assert task["day"] == "Day149"
    assert task["user_display_name"] == "AI Assistance Docs / Registry / Report Index Consistency Audit"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day149_ai_assistance_docs_registry_report_index_consistency_audit.py"
    assert "NOT_NEXT_DAY_FUNCTIONALITY" in task["notes"]
    assert "EXECUTION_PROVIDER_API_DISABLED" in task["notes"]
    assert "AGENTS_MD_FOUND_AND_READ" in task["notes"]

    report = day149.build_day149_ai_assistance_docs_registry_report_index_consistency_audit(PROJECT_ROOT)
    json_path, html_path = day149.write_day149_ai_assistance_docs_registry_report_index_consistency_audit_reports(
        tmp_path,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = read_text_with_long_path(tmp_path / "reports" / "report_index.html", encoding="utf-8")
    written = json.loads(read_text_with_long_path(json_path, encoding="utf-8"))

    assert exit_code == 0
    assert path_exists(json_path)
    assert path_exists(html_path)
    assert written["status"] == "CONSISTENCY_AUDITED_REVIEW_ONLY"
    assert written["is_next_day_functionality"] is False
    assert written["execution_enabled"] is False
    assert written["provider_enabled"] is False
    assert written["api_enabled"] is False
    assert written["next_phase_allowed"] is False
    assert "Day149" in index_html
    assert "AI Assistance Docs / Registry / Report Index Consistency Audit" in index_html
    assert "reports/lab-summary/day149_ai_assistance_docs_registry_report_index_consistency_audit.json" in index_html


def test_day149_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day149.__file__).read_text(encoding="utf-8").lower()

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
        "import ncclient",
        "routeros_api",
        "authorization:",
        "bearer ",
        "remove-item",
        "rmtree",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day149_docs_preserve_required_audit_boundaries():
    roadmap = (
        PROJECT_ROOT / "docs/roadmap/day149_ai_assistance_docs_registry_report_index_consistency_audit.md"
    ).read_text(encoding="utf-8")
    ai_intent = (
        PROJECT_ROOT / "docs/ai-intent/day149_ai_assistance_docs_registry_report_index_consistency_audit.md"
    ).read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "AI Assistance Docs / Registry / Report Index Consistency Audit" in doc
        assert "CONSISTENCY_AUDITED_REVIEW_ONLY" in doc
        assert "Day145" in doc
        assert "Day146" in doc
        assert "Day147" in doc
        assert "Day148" in doc
        assert "Day149" in doc
        assert "NOT_NEXT_DAY_FUNCTIONALITY" in doc
        assert "EXECUTION_PROVIDER_API_DISABLED" in doc
        assert "REVIEW_ONLY" in doc
        assert "REPORT_ONLY" in doc
        assert "AGENTS_MD_FOUND_AND_READ" in doc
        assert "AGENTS_MD_NOT_MODIFIED" in doc
        assert "review_only: true" in doc
        assert "report_only: true" in doc
        assert "audit_only: true" in doc
        assert "is_next_day_functionality: false" in doc
        assert "execution_enabled: false" in doc
        assert "provider_enabled: false" in doc
        assert "api_enabled: false" in doc
        assert "model_call_enabled: false" in doc
        assert "network_device_live_access_enabled: false" in doc
        assert "adapter_broker_runner_enabled: false" in doc
        assert "secrets_required: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "day150_implemented: false" in doc

    for day in ("Day145", "Day146", "Day147", "Day148", "Day149"):
        assert f"## {day}" in readme
