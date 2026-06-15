import copy
import json
from pathlib import Path

import day154_post_closure_evidence_baseline_lock_review as day154
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day154_report_records_baseline_lock_and_sdd_contract():
    report = day154.build_day154_post_closure_evidence_baseline_lock_review(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "REVIEW_READY"
    assert report["day"] == 154
    assert report["task"] == "post-closure-evidence-baseline-lock-review"
    assert report["mode"] == "review-only / report-only"
    assert report["new_feature"] is False
    assert report["touches_execution"] is False
    assert report["touches_provider"] is False
    assert report["touches_api"] is False
    assert report["touches_model_call"] is False
    assert report["touches_live_device"] is False
    assert report["continues_day153"] is True
    assert report["day153_supplement"] is False
    assert report["next_day_feature"] is False
    assert report["next_phase_allowed"] is False
    assert report["agents_md_pre_read"] == "YES"
    assert report["agents_md_result"] == "FOUND_AND_READ"
    assert report["agents_md_modified"] is False
    assert report["validation_errors"] == []

    contract = report["sdd_operating_contract_draft"]
    assert contract["contract_type"] == "draft"
    assert contract["purpose"] == "operating contract for SDD-style review/report-only governance"
    assert contract["execution_allowed"] is False
    assert contract["provider_allowed"] is False
    assert contract["api_allowed"] is False
    assert contract["model_call_allowed"] is False
    assert contract["live_device_allowed"] is False
    assert contract["evidence_first_required"] is True
    assert contract["phase_gate_required"] is True
    assert contract["agents_md_pre_read_required"] is True
    assert contract["next_phase_allowed"] is False

    assert any("Day145" in item for item in report["frozen_evidence"])
    assert any("Day153" in item for item in report["frozen_evidence"])
    assert "execution" in report["forbidden_capabilities"]
    assert "provider" in report["forbidden_capabilities"]
    assert "API" in report["forbidden_capabilities"]
    assert "model call" in report["forbidden_capabilities"]
    assert any("Day155" in item for item in report["blocked_or_deferred_future_work"])


def test_day154_reference_records_cover_registration_surfaces():
    report = day154.build_day154_post_closure_evidence_baseline_lock_review(PROJECT_ROOT)

    surfaces = {record["surface"] for record in report["reference_records"]}
    assert surfaces == {
        "README",
        "AI intent README",
        "Day154 roadmap doc",
        "Day154 AI-intent doc",
        "task registry",
        "CLI dispatch",
        "network_lab task catalog and report-index",
    }
    for record in report["reference_records"]:
        assert record["path_exists"] is True
        assert record["all_required_fragments_present"] is True
        assert record["missing_fragments"] == []
        assert record["review_only"] is True
        assert record["report_only"] is True
        assert record["next_phase_allowed"] is False

    assert [check["status"] for check in report["lock_checks"]] == ["PASS"] * 5


def test_day154_cli_does_not_execute_provider_network_runner_or_prior_day_tasks(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day154 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day154 must not load runner profile or config data")

    def fail_day151(*args, **kwargs):
        raise AssertionError("Day154 must not rerun Day151")

    def fail_day152(*args, **kwargs):
        raise AssertionError("Day154 must not rerun Day152")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day151_v04_ai_assistance_closure_evidence_index", fail_day151)
    monkeypatch.setattr(network_lab, "_run_day152_post_closure_reference_integrity_audit", fail_day152)

    exit_code = network_lab.main(
        ["--task", "post-closure-evidence-baseline-lock-review"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: YES" in output
    assert "AGENTS.md result: FOUND_AND_READ" in output
    assert "AGENTS.md modified: false" in output
    assert "Task slug: post-closure-evidence-baseline-lock-review" in output
    assert "day: 154" in output
    assert "status: REVIEW_READY" in output
    assert "mode: review-only / report-only" in output
    assert "new_feature: false" in output
    assert "touches_execution: false" in output
    assert "touches_provider: false" in output
    assert "touches_api: false" in output
    assert "touches_model_call: false" in output
    assert "touches_live_device: false" in output
    assert "continues_day153: true" in output
    assert "day153_supplement: false" in output
    assert "next_day_feature: false" in output
    assert "next_phase_allowed: false" in output
    assert "contract_type: draft" in output
    assert "execution_allowed: false" in output
    assert "provider_allowed: false" in output
    assert "api_allowed: false" in output
    assert "model_call_allowed: false" in output
    assert "[PASS] POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY" in output


def test_day154_negative_validation_blocks_unsafe_or_missing_contract_values():
    report = day154.build_day154_post_closure_evidence_baseline_lock_review(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)

    unsafe["agents_md_pre_read"] = "NO"
    unsafe["agents_md_result"] = "MISSING"
    unsafe["agents_md_modified"] = True
    unsafe["sdd_operating_contract_draft"]["execution_allowed"] = True
    unsafe["sdd_operating_contract_draft"]["next_phase_allowed"] = True
    unsafe["reference_records"][0]["path_exists"] = False
    unsafe["reference_records"][0]["missing_fragments"] = ["POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY"]
    unsafe["lock_checks"][0]["status"] = "FAIL"
    unsafe["lock_checks"][0]["next_phase_allowed"] = True
    unsafe["frozen_evidence"] = []

    for field in day154.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True
    for field in day154.REQUIRED_TRUE_FIELDS:
        unsafe[field] = False

    errors = day154.collect_validation_errors(unsafe)

    assert "agents_md_pre_read must be YES." in errors
    assert "agents_md_result must be FOUND_AND_READ." in errors
    assert "agents_md_modified must be false." in errors
    assert "sdd_operating_contract_draft.execution_allowed must be False." in errors
    assert "sdd_operating_contract_draft.next_phase_allowed must be false." in errors
    assert "README path must exist." in errors
    assert "README must contain all required fragments." in errors
    assert "DAY154-LOCK-001 status must be PASS." in errors
    assert "DAY154-LOCK-001 next_phase_allowed must be false." in errors
    assert "frozen_evidence must be a non-empty list." in errors
    for field in day154.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors
    for field in day154.REQUIRED_TRUE_FIELDS:
        assert f"{field} must be true." in errors


def test_day154_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "post-closure-evidence-baseline-lock-review"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "post-closure-evidence-baseline-lock-review"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("post-closure-evidence-baseline-lock-review", handlers)

    assert resolve_task_name("post-closure-evidence-baseline-lock-review") == (
        "post-closure-evidence-baseline-lock-review"
    )
    assert resolved.canonical_name == "post-closure-evidence-baseline-lock-review"
    assert callable(resolved.handler)
    assert task["task_id"] == "day154_post_closure_evidence_baseline_lock_review"
    assert task["day"] == "Day154"
    assert task["user_display_name"] == "Post-Closure Evidence Baseline Lock Review"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day154_post_closure_evidence_baseline_lock_review.py"
    assert "POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY" in task["notes"]
    assert "day153_supplement=false" in task["notes"]
    assert "next_day_feature=false" in task["notes"]
    assert "touches_execution=false" in task["notes"]
    assert "touches_provider=false" in task["notes"]
    assert "touches_api=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]

    report = day154.build_day154_post_closure_evidence_baseline_lock_review(PROJECT_ROOT)
    json_path, html_path = day154.write_day154_post_closure_evidence_baseline_lock_review_reports(
        tmp_path,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["day"] == 154
    assert written["status"] == "REVIEW_READY"
    assert written["next_phase_allowed"] is False
    assert written["day153_supplement"] is False
    assert written["next_day_feature"] is False
    assert written["sdd_operating_contract_draft"]["contract_type"] == "draft"
    assert "Day154" in index_html
    assert "Post-Closure Evidence Baseline Lock Review" in index_html
    assert "reports/lab-summary/day154_post_closure_evidence_baseline_lock_review.json" in index_html


def test_day154_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day154.__file__).read_text(encoding="utf-8").lower()

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


def test_day154_docs_preserve_scope_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day154_post_closure_evidence_baseline_lock_review.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day154_post_closure_evidence_baseline_lock_review.md").read_text(
        encoding="utf-8"
    )
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_intent):
        assert "Post-Closure Evidence Baseline Lock Review" in doc
        assert "SDD Operating Contract Draft" in doc
        assert "day: 154" in doc
        assert "mode: review-only / report-only" in doc
        assert "new_feature: false" in doc
        assert "touches_execution: false" in doc
        assert "touches_provider: false" in doc
        assert "touches_api: false" in doc
        assert "touches_model_call: false" in doc
        assert "touches_live_device: false" in doc
        assert "continues_day153: true" in doc
        assert "day153_supplement: false" in doc
        assert "next_day_feature: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "contract_type: draft" in doc
        assert "execution_allowed: false" in doc
        assert "provider_allowed: false" in doc
        assert "api_allowed: false" in doc
        assert "model_call_allowed: false" in doc
        assert "live_device_allowed: false" in doc
        assert "evidence_first_required: true" in doc
        assert "phase_gate_required: true" in doc
        assert "agents_md_pre_read_required: true" in doc

    assert "## Day154" in ai_readme
    assert "Current project status after Day154" in readme
    assert "POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY" in readme
    assert "SDD Operating Contract Draft" in readme
