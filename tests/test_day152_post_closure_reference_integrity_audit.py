import copy
import json
from pathlib import Path

import day152_post_closure_reference_integrity_audit as day152
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day152_report_audits_post_closure_references_without_reopening_safety():
    report = day152.build_day152_post_closure_reference_integrity_audit(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED"
    assert report["day"] == 152
    assert report["day_label"] == "Day152"
    assert report["task"] == "post-closure-reference-integrity-audit"
    assert report["title"] == "Post-Closure Reference Integrity Audit"
    assert report["mode"] == "REVIEW_ONLY_POST_CLOSURE_REFERENCE_AUDIT"
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day152_work"] is True
    assert report["agents_md_modified"] is False
    assert report["validation_errors"] == []
    assert report["assumed_day151_closure_facts"] == {
        "day151_closure_index_found_by_report_index": True,
        "day145_day150_indexed": True,
        "unsafe_flags_false": True,
        "next_phase_allowed": False,
        "source_task_rerun": False,
        "safety_judgment_reopened": False,
    }

    for concept in day152.REQUIRED_CONCEPTS:
        assert concept in report["required_concepts"]
    for field in day152.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day152.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day152_reference_records_cover_requested_surfaces():
    report = day152.build_day152_post_closure_reference_integrity_audit(PROJECT_ROOT)

    surfaces = {record["surface"] for record in report["reference_records"]}
    assert surfaces == {
        "README",
        "AI intent README",
        "Day151 roadmap doc",
        "Day151 AI-intent doc",
        "Day152 roadmap doc",
        "Day152 AI-intent doc",
        "task registry",
        "CLI dispatch",
        "network_lab task catalog and report-index",
    }
    for record in report["reference_records"]:
        assert record["path_exists"] is True
        assert record["all_required_fragments_present"] is True
        assert record["missing_fragments"] == []
        assert record["source_task_rerun"] is False
        assert record["next_phase_allowed"] is False

    assert [check["status"] for check in report["integrity_checks"]] == ["PASS"] * 6


def test_day152_cli_does_not_execute_provider_network_runner_or_closure_source_tasks(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day152 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day152 must not load runner profile or config data")

    def fail_day151(*args, **kwargs):
        raise AssertionError("Day152 must not rerun Day151")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day151_v04_ai_assistance_closure_evidence_index", fail_day151)

    exit_code = network_lab.main(
        ["--task", "post-closure-reference-integrity-audit"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: PASS" in output
    assert "Day152 task: Post-Closure Reference Integrity Audit" in output
    assert "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED" in output
    assert "DAY151_CLOSURE_INDEX_AUTHORITY_PRESERVED" in output
    assert "redoes_day145_day151_safety_judgment: false" in output
    assert "source_task_rerun: false" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "model_calls_enabled: false" in output
    assert "device_access_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED" in output


def test_day152_negative_validation_blocks_mismatches_and_unsafe_flags():
    report = day152.build_day152_post_closure_reference_integrity_audit(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["agents_md_read_before_day152_work"] = False
    unsafe["reference_records"][0]["path_exists"] = False
    unsafe["reference_records"][0]["missing_fragments"] = ["Day151 remains the closure evidence index authority"]
    unsafe["integrity_checks"][0]["status"] = "FAIL"
    unsafe["mismatch_findings"] = [{"finding_id": "DAY152-TEST"}]
    unsafe["mismatch_finding_count"] = 1
    unsafe["assumed_day151_closure_facts"]["safety_judgment_reopened"] = True
    unsafe["assumed_day151_closure_facts"]["source_task_rerun"] = True
    unsafe["assumed_day151_closure_facts"]["next_phase_allowed"] = True

    for field in day152.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day152.collect_validation_errors(unsafe)

    assert "agents_md_pre_read_result must be PASS." in errors
    assert "agents_md_read_before_day152_work must be true." in errors
    assert "Day152 must not reopen Day145-Day151 safety judgment." in errors
    assert "assumed source_task_rerun must be false." in errors
    assert "assumed next_phase_allowed must be false." in errors
    assert "mismatch_findings must be empty for PASS." in errors
    assert "mismatch_finding_count must be 0 for PASS." in errors
    assert "README path must exist." in errors
    assert "README must contain all required fragments." in errors
    assert "DAY152-REF-001 status must be PASS." in errors
    for field in day152.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day152_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "post-closure-reference-integrity-audit"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "post-closure-reference-integrity-audit"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("post-closure-reference-integrity-audit", handlers)

    assert resolve_task_name("post-closure-reference-integrity-audit") == (
        "post-closure-reference-integrity-audit"
    )
    assert resolved.canonical_name == "post-closure-reference-integrity-audit"
    assert callable(resolved.handler)
    assert task["task_id"] == "day152_post_closure_reference_integrity_audit"
    assert task["day"] == "Day152"
    assert task["user_display_name"] == "Post-Closure Reference Integrity Audit"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day152_post_closure_reference_integrity_audit.py"
    assert "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED" in task["notes"]
    assert "DAY151_CLOSURE_INDEX_AUTHORITY_PRESERVED" in task["notes"]
    assert "redoes_day145_day151_safety_judgment=false" in task["notes"]

    report = day152.build_day152_post_closure_reference_integrity_audit(PROJECT_ROOT)
    json_path, html_path = day152.write_day152_post_closure_reference_integrity_audit_reports(
        tmp_path,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED"
    assert written["redoes_day145_day151_safety_judgment"] is False
    assert written["source_task_rerun"] is False
    assert written["next_phase_allowed"] is False
    assert "Day152" in index_html
    assert "Post-Closure Reference Integrity Audit" in index_html
    assert "reports/lab-summary/day152_post_closure_reference_integrity_audit.json" in index_html


def test_day152_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day152.__file__).read_text(encoding="utf-8").lower()

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


def test_day152_docs_and_readme_preserve_post_closure_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day152_post_closure_reference_integrity_audit.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day152_post_closure_reference_integrity_audit.md").read_text(
        encoding="utf-8"
    )
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "Post-Closure Reference Integrity Audit" in doc
        assert "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED" in doc
        assert "Day151 remains the closure evidence index authority" in doc
        assert "redoes_day145_day151_safety_judgment: false" in doc
        assert "source_task_rerun: false" in doc
        assert "execution_enabled: false" in doc
        assert "provider_enabled: false" in doc
        assert "api_enabled: false" in doc
        assert "model_calls_enabled: false" in doc
        assert "device_access_enabled: false" in doc
        assert "ssh_enabled: false" in doc
        assert "netconf_enabled: false" in doc
        assert "restconf_enabled: false" in doc
        assert "secrets_enabled: false" in doc
        assert "live_network_io_enabled: false" in doc
        assert "next_phase_allowed: false" in doc

    assert "## Day152" in ai_readme
    for fragment in (
        "## Current Release Status",
        "Stage-0 Network Automation Lab",
        "Workflow Version 2",
        "DEFERRED_SECURITY_RESEARCH_BLOCKED",
        "WF-01-03C through WF-01-03F",
    ):
        assert fragment in readme
