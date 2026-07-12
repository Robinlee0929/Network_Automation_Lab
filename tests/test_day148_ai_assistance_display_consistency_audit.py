import copy
import json
from pathlib import Path

import day148_ai_assistance_display_consistency_audit as day148
import network_lab
import network_lab_cli_dispatch
from ai_assistance_evidence_test_fixtures import build_deterministic_ai_assistance_evidence_root
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day148_report_contains_scope_summary_and_required_safety_flags(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day148.build_day148_ai_assistance_display_consistency_audit(evidence_root)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY"
    assert report["day"] == 148
    assert report["day_label"] == "Day148"
    assert report["task"] == "ai-assistance-demo-export-draft-display-consistency-audit"
    assert report["title"] == "AI Assistance Demo / Export / Draft Display Consistency Audit"
    assert report["mode"] == "REVIEW_ONLY_CONSISTENCY_AUDIT"
    assert report["agents_md_pre_read"] == "YES"
    assert report["agents_md_read_before_day148_work"] is True
    assert report["agents_md_modified"] is False
    assert report["audit_scope"] == ["Day141", "Day136", "Day142", "Day143"]
    assert report["artifact_count"] == 4
    assert report["mismatch_findings"] == []
    assert report["mismatch_finding_count"] == 0
    assert report["final_recommendation"] == "KEEP_AI_ASSISTANCE_REVIEW_ONLY_AND_NEXT_PHASE_FALSE"
    assert report["validation_errors"] == []

    for field in day148.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day148.REQUIRED_FALSE_FIELDS:
        assert report[field] is False

    summary = report["consistency_summary"]
    assert summary["result_status"] == "PASS"
    assert summary["audit_scope"] == "Day141, Day136, Day142, Day143"
    assert summary["display_consistency"] == "PASS"
    assert summary["safety_semantic_consistency"] == "PASS"
    assert summary["next_phase_allowed"] is False
    assert summary["not_next_day_functionality"] is True


def test_day148_artifact_audits_cover_required_days_with_no_mismatches(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day148.build_day148_ai_assistance_display_consistency_audit(evidence_root)

    assert [artifact["day"] for artifact in report["artifact_audits"]] == [
        "Day141",
        "Day136",
        "Day142",
        "Day143",
    ]
    for artifact in report["artifact_audits"]:
        assert artifact["all_paths_exist"] is True
        assert artifact["loaded"] is True
        assert artifact["display_consistency"] == "PASS"
        assert artifact["safety_semantics"] == "PASS"
        assert artifact["review_only_wording_present"] is True
        assert artifact["no_misleading_execution_wording"] is True
        assert artifact["mismatch_findings"] == []
        assert artifact["mismatch_count"] == 0


def test_day148_cli_does_not_execute_provider_network_runner_or_prior_day_paths(
    tmp_path, monkeypatch, capsys
):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day148 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day148 must not load runner profile or config data")

    def fail_day141(*args, **kwargs):
        raise AssertionError("Day148 must not rerun Day141")

    def fail_day142(*args, **kwargs):
        raise AssertionError("Day148 must not rerun Day142")

    def fail_day143(*args, **kwargs):
        raise AssertionError("Day148 must not rerun Day143")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day141_ai_assistance_review_demo_package", fail_day141)
    monkeypatch.setattr(network_lab, "_run_day142_ai_summary_to_dry_run_draft_display_contract", fail_day142)
    monkeypatch.setattr(network_lab, "_run_day143_dry_run_draft_safety_diff_viewer", fail_day143)

    exit_code = network_lab.main(
        ["--task", "ai-assistance-demo-export-draft-display-consistency-audit"],
        project_root=evidence_root,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: YES" in output
    assert "Day148 task: AI Assistance Demo / Export / Draft Display Consistency Audit" in output
    assert "Audit scope: Day141, Day136, Day142, Day143" in output
    assert "Day148 is not next-day functionality." in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "model_call_enabled: false" in output
    assert "adapter_invoked: false" in output
    assert "broker_invoked: false" in output
    assert "runner_invoked: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY" in output


def test_day148_negative_validation_blocks_unsafe_flags_and_unrecorded_mismatch_state(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day148.build_day148_ai_assistance_display_consistency_audit(evidence_root)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_pre_read"] = "NO"
    unsafe["agents_md_read_before_day148_work"] = False
    unsafe["artifact_audits"][0]["mismatch_count"] = 1
    unsafe["artifact_audits"][0]["display_consistency"] = "FAIL"
    unsafe["artifact_audits"][0]["safety_semantics"] = "FAIL"
    unsafe["mismatch_findings"] = [
        {
            "finding_id": "DAY148-TEST",
            "source_day": "Day141",
            "category": "TEST",
            "severity": "BLOCKING",
            "description": "synthetic mismatch",
        }
    ]
    unsafe["consistency_summary"]["result_status"] = "FAIL"
    unsafe["consistency_summary"]["next_phase_allowed"] = True

    for field in day148.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day148.collect_validation_errors(unsafe)

    assert "agents_md_pre_read must be YES." in errors
    assert "agents_md_read_before_day148_work must be true." in errors
    assert "Day141 display_consistency must be PASS." in errors
    assert "Day141 safety_semantics must be PASS." in errors
    assert "Day141 mismatch_count must be 0 for PASS." in errors
    assert "consistency_summary.result_status must be PASS." in errors
    assert "consistency_summary.next_phase_allowed must be false." in errors
    assert "mismatch_findings must be empty for PASS." in errors
    for field in day148.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day148_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-assistance-demo-export-draft-display-consistency-audit"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-assistance-demo-export-draft-display-consistency-audit"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-assistance-demo-export-draft-display-consistency-audit", handlers)

    assert resolve_task_name("ai-assistance-demo-export-draft-display-consistency-audit") == (
        "ai-assistance-demo-export-draft-display-consistency-audit"
    )
    assert resolved.canonical_name == "ai-assistance-demo-export-draft-display-consistency-audit"
    assert callable(resolved.handler)
    assert task["task_id"] == "day148_ai_assistance_display_consistency_audit"
    assert task["day"] == "Day148"
    assert task["user_display_name"] == "AI Assistance Demo / Export / Draft Display Consistency Audit"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day148_ai_assistance_display_consistency_audit.py"
    assert "Day141 demo" in task["notes"]
    assert "Day136 export package" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]

    report = day148.build_day148_ai_assistance_display_consistency_audit(evidence_root)
    json_path, html_path = day148.write_day148_ai_assistance_display_consistency_audit_reports(evidence_root, report)
    exit_code = network_lab.main(["--report-index"], project_root=evidence_root)
    index_html = (evidence_root / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY"
    assert written["is_next_day_functionality"] is False
    assert written["execution_enabled"] is False
    assert written["provider_enabled"] is False
    assert written["api_enabled"] is False
    assert written["next_phase_allowed"] is False
    assert "Day148" in index_html
    assert "AI Assistance Demo / Export / Draft Display Consistency Audit" in index_html
    assert "reports/lab-summary/day148_ai_assistance_display_consistency_audit.json" in index_html


def test_day148_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day148.__file__).read_text(encoding="utf-8").lower()

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


def test_day148_docs_preserve_required_audit_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day148_ai_assistance_display_consistency_audit.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day148_ai_assistance_display_consistency_audit.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "AI Assistance Demo / Export / Draft Display Consistency Audit" in doc
        assert "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY" in doc
        assert "Day141" in doc
        assert "Day136" in doc
        assert "Day142" in doc
        assert "Day143" in doc
        assert "This is not next-day functionality" in doc
        assert "review_only: true" in doc
        assert "audit_only: true" in doc
        assert "is_next_day_functionality: false" in doc
        assert "execution_enabled: false" in doc
        assert "provider_enabled: false" in doc
        assert "api_enabled: false" in doc
        assert "device_access_enabled: false" in doc
        assert "ssh_enabled: false" in doc
        assert "netconf_enabled: false" in doc
        assert "restconf_enabled: false" in doc
        assert "cli_live_execution_enabled: false" in doc
        assert "model_call_enabled: false" in doc
        assert "adapter_invoked: false" in doc
        assert "broker_invoked: false" in doc
        assert "runner_invoked: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "KEEP_AI_ASSISTANCE_REVIEW_ONLY_AND_NEXT_PHASE_FALSE" in doc
