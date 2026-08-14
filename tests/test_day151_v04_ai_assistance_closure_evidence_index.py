import copy
import json
from pathlib import Path

import day151_v04_ai_assistance_closure_evidence_index as day151
import network_lab
import network_lab_cli_dispatch
from ai_assistance_evidence_test_fixtures import build_deterministic_ai_assistance_evidence_root
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day151_report_indexes_closure_evidence_and_safety_flags(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day151.build_day151_v04_ai_assistance_closure_evidence_index(evidence_root)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_READY"
    assert report["day"] == 151
    assert report["day_label"] == "Day151"
    assert report["task"] == "v04-ai-assistance-closure-evidence-index"
    assert report["title"] == "v0.4 AI Assistance Closure Evidence Index"
    assert report["mode"] == "REVIEW_ONLY_CLOSURE_EVIDENCE_INDEX"
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day151_work"] is True
    assert report["agents_md_modified"] is False
    assert report["indexed_scope"] == ["Day145", "Day146", "Day147", "Day148", "Day149", "Day150"]
    assert report["evidence_item_count"] == 6
    assert report["final_constants"] == [
        "CLOSURE_EVIDENCE_INDEX_READY",
        "PHASE_GATE_CLOSED_REVIEW_ONLY",
        "NEXT_PHASE_ALLOWED_FALSE",
    ]
    assert report["human_readable_conclusion"] == (
        "v0.4 AI Assistance closure evidence is indexed for reviewer use only. "
        "The Day150 phase gate remains closed and the next phase remains blocked."
    )
    assert report["validation_errors"] == []

    for concept in day151.REQUIRED_CONCEPTS:
        assert concept in report["required_concepts"]
    for field in day151.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day151.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day151_evidence_items_cover_day145_through_day150_without_reruns(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day151.build_day151_v04_ai_assistance_closure_evidence_index(evidence_root)

    expected_roles = {
        "Day145": "Evidence freeze baseline",
        "Day146": "Non-advancement gate",
        "Day147": "Deferred risk register",
        "Day148": "Display consistency audit",
        "Day149": "Docs registry report-index consistency audit",
        "Day150": "Final review-only phase gate closure",
    }
    assert [item["day_label"] for item in report["evidence_items"]] == list(expected_roles)
    for item in report["evidence_items"]:
        assert item["index_role"] == expected_roles[item["day_label"]]
        assert item["required_static_paths_present"] is True
        assert item["json_readable_or_absent"] is True
        assert item["source_task_rerun"] is False
        assert item["review_only"] is True
        assert item["report_only"] is True
        assert item["next_phase_allowed"] is False

    check_names = [check["name"] for check in report["index_checks"]]
    assert "Day145-Day150 source evidence is indexed" in check_names
    assert "Day150 phase gate closure remains authoritative" in check_names


def test_day151_real_agents_md_evidence_takes_precedence_over_required_true_defaults(tmp_path, monkeypatch):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    failure_like_agents_evidence = {
        "agents_md_pre_read_result": "FAIL",
        "agents_md_read_before_day151_work": False,
        "agents_md_found_and_read": False,
        "agents_md_not_modified": False,
        "agents_md_modified": True,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_WITHOUT_REQUIRED_MARKERS",
    }

    monkeypatch.setattr(day151, "build_agents_md_evidence", lambda project_root: failure_like_agents_evidence)

    report = day151.build_day151_v04_ai_assistance_closure_evidence_index(evidence_root)

    assert report["agents_md_pre_read_result"] == "FAIL"
    assert report["agents_md_read_before_day151_work"] is False
    assert report["agents_md_found_and_read"] is False
    assert report["agents_md_not_modified"] is False
    assert report["agents_md_modified"] is True
    assert "agents_md_pre_read_result must be PASS." in report["validation_errors"]
    assert "agents_md_read_before_day151_work must be true." in report["validation_errors"]
    assert "agents_md_found_and_read must be true." in report["validation_errors"]
    assert "agents_md_not_modified must be true." in report["validation_errors"]
    assert "agents_md_modified must be false." in report["validation_errors"]
    assert report["overall_status"] == "FAIL"
    assert report["status"] == "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_BLOCKED"


def test_day151_cli_does_not_execute_provider_network_runner_or_source_tasks(
    tmp_path, monkeypatch, capsys
):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day151 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day151 must not load runner profile or config data")

    def fail_day150(*args, **kwargs):
        raise AssertionError("Day151 must not rerun Day150")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day150_v04_ai_assistance_phase_gate_closure_review", fail_day150)

    exit_code = network_lab.main(
        ["--task", "v04-ai-assistance-closure-evidence-index"],
        project_root=evidence_root,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: PASS" in output
    assert "AGENTS.md status: AGENTS_MD_FOUND_AND_READ" in output
    assert "AGENTS.md modified: false" in output
    assert "Day151 task: v0.4 AI Assistance Closure Evidence Index" in output
    assert "Indexed scope: Day145, Day146, Day147, Day148, Day149, Day150" in output
    assert "CLOSURE_EVIDENCE_INDEX_READY" in output
    assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in output
    assert "NEXT_PHASE_ALLOWED_FALSE" in output
    assert "source_task_rerun: false" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "model_calls_enabled: false" in output
    assert "device_access_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "netconf_enabled: false" in output
    assert "restconf_enabled: false" in output
    assert "secrets_enabled: false" in output
    assert "live_network_io_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_READY" in output


def test_day151_negative_validation_blocks_unsafe_flags_and_missing_index_evidence(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day151.build_day151_v04_ai_assistance_closure_evidence_index(evidence_root)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["agents_md_read_before_day151_work"] = False
    unsafe["evidence_items"][0]["required_static_paths_present"] = False
    unsafe["evidence_items"][0]["source_task_rerun"] = True
    unsafe["evidence_items"][0]["next_phase_allowed"] = True
    unsafe["index_checks"][0]["status"] = "FAIL"
    unsafe["index_findings"] = [{"finding_id": "DAY151-TEST"}]
    unsafe["index_finding_count"] = 1
    unsafe["final_constants"] = ["CLOSURE_EVIDENCE_INDEX_READY"]

    for field in day151.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day151.collect_validation_errors(unsafe)

    assert "agents_md_pre_read_result must be PASS." in errors
    assert "agents_md_read_before_day151_work must be true." in errors
    assert "index_findings must be empty for PASS." in errors
    assert "index_finding_count must be 0 for PASS." in errors
    assert "DAY151-INDEX-001 status must be PASS." in errors
    assert "Day145 required static paths must be present." in errors
    assert "Day145 source_task_rerun must be false." in errors
    assert "Day145 next_phase_allowed must be false." in errors
    assert "final_constants must include closure index ready, phase gate closed, and next phase false." in errors
    for field in day151.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day151_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "v04-ai-assistance-closure-evidence-index"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "v04-ai-assistance-closure-evidence-index"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("v04-ai-assistance-closure-evidence-index", handlers)

    assert resolve_task_name("v04-ai-assistance-closure-evidence-index") == (
        "v04-ai-assistance-closure-evidence-index"
    )
    assert resolved.canonical_name == "v04-ai-assistance-closure-evidence-index"
    assert callable(resolved.handler)
    assert task["task_id"] == "day151_v04_ai_assistance_closure_evidence_index"
    assert task["day"] == "Day151"
    assert task["user_display_name"] == "v0.4 AI Assistance Closure Evidence Index"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day151_v04_ai_assistance_closure_evidence_index.py"
    assert "CLOSURE_EVIDENCE_INDEX_READY" in task["notes"]
    assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in task["notes"]
    assert "source_task_rerun=false" in task["notes"]

    report = day151.build_day151_v04_ai_assistance_closure_evidence_index(evidence_root)
    json_path, html_path = day151.write_day151_v04_ai_assistance_closure_evidence_index_reports(
        evidence_root,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=evidence_root)
    index_html = (evidence_root / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_READY"
    assert written["final_constants"] == [
        "CLOSURE_EVIDENCE_INDEX_READY",
        "PHASE_GATE_CLOSED_REVIEW_ONLY",
        "NEXT_PHASE_ALLOWED_FALSE",
    ]
    assert written["source_task_rerun"] is False
    assert written["next_phase_allowed"] is False
    assert "Day151" in index_html
    assert "v0.4 AI Assistance Closure Evidence Index" in index_html
    assert "reports/lab-summary/day151_v04_ai_assistance_closure_evidence_index.json" in index_html


def test_day151_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day151.__file__).read_text(encoding="utf-8").lower()

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


def test_day151_docs_and_readme_preserve_required_closure_index_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day151_v04_ai_assistance_closure_evidence_index.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day151_v04_ai_assistance_closure_evidence_index.md").read_text(
        encoding="utf-8"
    )
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "v0.4 AI Assistance Closure Evidence Index" in doc
        assert "CLOSURE_EVIDENCE_INDEX_READY" in doc
        assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in doc
        assert "NEXT_PHASE_ALLOWED_FALSE" in doc
        assert "Day145" in doc
        assert "Day146" in doc
        assert "Day147" in doc
        assert "Day148" in doc
        assert "Day149" in doc
        assert "Day150" in doc
        assert "review_only: true" in doc
        assert "report_only: true" in doc
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

    assert "## Day151" in ai_readme
    assert "## Current Release Status" in readme
    assert "Stage-0 Network Automation Lab" in readme
    assert "Workflow Version 2" in readme
    assert "DEFERRED_SECURITY_RESEARCH_BLOCKED" in readme
    assert "WF-01-03C through WF-01-03F" in readme
