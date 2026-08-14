import copy
import json
from pathlib import Path

import day150_v04_ai_assistance_phase_gate_closure_review as day150
import network_lab
import network_lab_cli_dispatch
from ai_assistance_evidence_test_fixtures import build_deterministic_ai_assistance_evidence_root
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day150_report_contains_required_closure_conclusions_and_safety_flags(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(evidence_root)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "PHASE_GATE_CLOSED_REVIEW_ONLY"
    assert report["day"] == 150
    assert report["day_label"] == "Day150"
    assert report["task"] == "v04-ai-assistance-phase-gate-closure-review"
    assert report["title"] == "v0.4 AI Assistance Phase Gate Closure Review"
    assert report["mode"] == "REVIEW_ONLY_PHASE_GATE_CLOSURE"
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day150_work"] is True
    assert report["agents_md_modified"] is False
    assert report["review_scope"] == ["Day145", "Day146", "Day147", "Day148", "Day149"]
    assert report["final_constants"] == ["PHASE_GATE_CLOSED_REVIEW_ONLY", "NEXT_PHASE_ALLOWED_FALSE"]
    assert report["final_conclusions"] == ["PHASE_GATE_CLOSED_REVIEW_ONLY", "NEXT_PHASE_ALLOWED_FALSE"]
    assert report["human_readable_conclusion"] == (
        "v0.4 AI Assistance phase gate closed as review-only. Execution / provider / API remain disabled. "
        "Next phase remains blocked pending future explicit safety gate."
    )
    assert report["validation_errors"] == []

    for concept in day150.REQUIRED_CONCEPTS:
        assert concept in report["required_concepts"]

    for field in day150.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day150.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day150_real_agents_md_evidence_takes_precedence_over_required_true_defaults(tmp_path, monkeypatch):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    failure_like_agents_evidence = {
        "agents_md_pre_read_result": "FAIL",
        "agents_md_read_before_day150_work": False,
        "agents_md_found_and_read": False,
        "agents_md_not_modified": False,
        "agents_md_modified": True,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_WITHOUT_REQUIRED_MARKERS",
    }

    monkeypatch.setattr(day150, "build_agents_md_evidence", lambda project_root: failure_like_agents_evidence)

    report = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(evidence_root)

    assert report["agents_md_pre_read_result"] == "FAIL"
    assert report["agents_md_read_before_day150_work"] is False
    assert report["agents_md_found_and_read"] is False
    assert report["agents_md_not_modified"] is False
    assert report["agents_md_modified"] is True
    assert report["agents_md_status"] == "FOUND_WITHOUT_REQUIRED_MARKERS"
    assert "agents_md_pre_read_result must be PASS." in report["validation_errors"]
    assert "agents_md_read_before_day150_work must be true." in report["validation_errors"]
    assert "agents_md_found_and_read must be true." in report["validation_errors"]
    assert "agents_md_not_modified must be true." in report["validation_errors"]
    assert "agents_md_modified must be false." in report["validation_errors"]
    assert report["overall_status"] == "FAIL"
    assert report["status"] == "PHASE_GATE_CLOSURE_BLOCKED_REVIEW_ONLY"


def test_day150_prior_day_conclusions_are_referenced_and_preserved(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(evidence_root)

    expected_conclusions = {
        "Day145": "Day145 evidence freeze is complete.",
        "Day146": "Day146 non-advancement gate still holds.",
        "Day147": "Day147 deferred risk register still preserves blocked items.",
        "Day148": "Day148 demo / export / draft display consistency remains aligned.",
        "Day149": "Day149 docs / registry / report-index consistency remains aligned.",
    }
    assert [record["day_label"] for record in report["prior_day_conclusions"]] == list(expected_conclusions)
    for record in report["prior_day_conclusions"]:
        assert record["preserved_conclusion"] == expected_conclusions[record["day_label"]]
        assert record["preserved"] is True
        assert record["review_only"] is True
        assert record["report_only"] is True
        assert record["next_phase_allowed"] is False

    check_names = [check["name"] for check in report["closure_checks"]]
    assert "Day145-Day149 conclusions are referenced and preserved" in check_names
    assert "README remains a status summary and formal docs remain present" in check_names


def test_day150_cli_does_not_execute_provider_network_runner_or_prior_day_tasks(
    tmp_path, monkeypatch, capsys
):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day150 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day150 must not load runner profile or config data")

    def fail_day149(*args, **kwargs):
        raise AssertionError("Day150 must not rerun Day149")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(
        network_lab,
        "_run_day149_ai_assistance_docs_registry_report_index_consistency_audit",
        fail_day149,
    )

    exit_code = network_lab.main(
        ["--task", "v04-ai-assistance-phase-gate-closure-review"],
        project_root=evidence_root,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: PASS" in output
    assert "AGENTS.md status: AGENTS_MD_FOUND_AND_READ" in output
    assert "AGENTS.md modified: false" in output
    assert "Day150 task: v0.4 AI Assistance Phase Gate Closure Review" in output
    assert "Review scope: Day145, Day146, Day147, Day148, Day149" in output
    assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in output
    assert "NEXT_PHASE_ALLOWED_FALSE" in output
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
    assert "[PASS] PHASE_GATE_CLOSED_REVIEW_ONLY" in output


def test_day150_negative_validation_blocks_unsafe_flags_and_missing_closure_evidence(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(evidence_root)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["agents_md_read_before_day150_work"] = False
    unsafe["prior_day_conclusions"][0]["preserved"] = False
    unsafe["prior_day_conclusions"][0]["next_phase_allowed"] = True
    unsafe["closure_checks"][0]["status"] = "FAIL"
    unsafe["closure_findings"] = [{"finding_id": "DAY150-TEST"}]
    unsafe["closure_finding_count"] = 1
    unsafe["final_constants"] = ["PHASE_GATE_CLOSED_REVIEW_ONLY"]
    unsafe["final_conclusions"] = ["NEXT_PHASE_ALLOWED_FALSE"]

    for field in day150.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day150.collect_validation_errors(unsafe)

    assert "agents_md_pre_read_result must be PASS." in errors
    assert "agents_md_read_before_day150_work must be true." in errors
    assert "closure_findings must be empty for PASS." in errors
    assert "closure_finding_count must be 0 for PASS." in errors
    assert "DAY150-CLOSURE-001 status must be PASS." in errors
    assert "Day145 preserved must be true." in errors
    assert "Day145 next_phase_allowed must be false." in errors
    assert "final_constants must include PHASE_GATE_CLOSED_REVIEW_ONLY and NEXT_PHASE_ALLOWED_FALSE." in errors
    assert "final_conclusions must include PHASE_GATE_CLOSED_REVIEW_ONLY and NEXT_PHASE_ALLOWED_FALSE." in errors
    for field in day150.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day150_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "v04-ai-assistance-phase-gate-closure-review"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "v04-ai-assistance-phase-gate-closure-review"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("v04-ai-assistance-phase-gate-closure-review", handlers)

    assert resolve_task_name("v04-ai-assistance-phase-gate-closure-review") == (
        "v04-ai-assistance-phase-gate-closure-review"
    )
    assert resolved.canonical_name == "v04-ai-assistance-phase-gate-closure-review"
    assert callable(resolved.handler)
    assert task["task_id"] == "day150_v04_ai_assistance_phase_gate_closure_review"
    assert task["day"] == "Day150"
    assert task["user_display_name"] == "v0.4 AI Assistance Phase Gate Closure Review"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day150_v04_ai_assistance_phase_gate_closure_review.py"
    assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in task["notes"]
    assert "NEXT_PHASE_ALLOWED_FALSE" in task["notes"]
    assert "execution_enabled=false" in task["notes"]

    report = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(evidence_root)
    json_path, html_path = day150.write_day150_v04_ai_assistance_phase_gate_closure_review_reports(
        evidence_root,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=evidence_root)
    index_html = (evidence_root / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "PHASE_GATE_CLOSED_REVIEW_ONLY"
    assert written["final_conclusions"] == ["PHASE_GATE_CLOSED_REVIEW_ONLY", "NEXT_PHASE_ALLOWED_FALSE"]
    assert written["execution_enabled"] is False
    assert written["provider_enabled"] is False
    assert written["api_enabled"] is False
    assert written["model_calls_enabled"] is False
    assert written["device_access_enabled"] is False
    assert written["ssh_enabled"] is False
    assert written["netconf_enabled"] is False
    assert written["restconf_enabled"] is False
    assert written["secrets_enabled"] is False
    assert written["live_network_io_enabled"] is False
    assert written["next_phase_allowed"] is False
    assert "Day150" in index_html
    assert "v0.4 AI Assistance Phase Gate Closure Review" in index_html
    assert "reports/lab-summary/day150_v04_ai_assistance_phase_gate_closure_review.json" in index_html


def test_day150_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day150.__file__).read_text(encoding="utf-8").lower()

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


def test_day150_docs_and_readme_preserve_required_closure_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day150_v04_ai_assistance_phase_gate_closure_review.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day150_v04_ai_assistance_phase_gate_closure_review.md").read_text(
        encoding="utf-8"
    )
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "v0.4 AI Assistance Phase Gate Closure Review" in doc
        assert "PHASE_GATE_CLOSED_REVIEW_ONLY" in doc
        assert "NEXT_PHASE_ALLOWED_FALSE" in doc
        assert "Day145" in doc
        assert "Day146" in doc
        assert "Day147" in doc
        assert "Day148" in doc
        assert "Day149" in doc
        assert "review_only: true" in doc
        assert "report_only: true" in doc
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

    assert "## Day150" in ai_readme
    for fragment in (
        "## Current Release Status",
        "Stage-0 Network Automation Lab",
        "Workflow Version 2",
        "INACTIVE",
        "DEFERRED_SECURITY_RESEARCH_BLOCKED",
        "NOT INCLUDED IN RELEASE",
        "WF-01-03C through WF-01-03F",
        "Historical records describe the state and authorization boundary",
    ):
        assert fragment in readme
