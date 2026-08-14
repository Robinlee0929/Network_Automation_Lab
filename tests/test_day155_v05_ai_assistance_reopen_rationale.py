import copy
import json
from pathlib import Path

import day155_v05_ai_assistance_reopen_rationale as day155
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day155_report_answers_exactly_five_required_questions():
    report = day155.build_day155_v05_ai_assistance_reopen_rationale(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "REVIEW_READY"
    assert report["day"] == 155
    assert report["task"] == "v05-ai-assistance-reopen-rationale"
    assert report["mode"] == "docs-only / rationale-only / review-only / non-executable"
    assert report["agents_md_pre_read"] == "YES"
    assert report["agents_md_result"] == "FOUND_AND_READ"
    assert report["agents_md_modified"] is False
    assert report["validation_errors"] == []

    assert [item["question"] for item in report["rationale_questions"]] == [
        "Why is AI needed?",
        "Who does AI help?",
        "What data may AI read?",
        "What must AI never do?",
        "Under what conditions is AI Assistance allowed into the repo?",
    ]
    assert len(report["rationale_questions"]) == 5

    q1 = report["rationale_questions"][0]["answer"]
    assert "AI is needed to simplify and automate reviewer-side testing review steps." in q1
    assert "It must not replace human review." in q1

    q2 = report["rationale_questions"][1]["answer"]
    assert "Primary user: reviewer." in q2
    assert "Executor support is limited to recommendation-only guidance." in q2

    q3 = report["rationale_questions"][2]["answer"][0]
    assert "repo reports" in q3["allowed"]
    assert "pytest results" in q3["allowed"]
    assert "mock-only fixtures" in q3["allowed"]
    assert "secrets" in q3["forbidden"]
    assert "tokens" in q3["forbidden"]
    assert "live device configs" in q3["forbidden"]

    q4 = report["rationale_questions"][3]["answer"]
    assert "It must never directly issue commands." in q4
    assert "It must never activate providers." in q4
    assert "It must only provide templated review output." in q4

    q5 = report["rationale_questions"][4]["answer"]
    assert "reviewer-assistance only" in q5
    assert "executor recommendation-only" in q5
    assert "pytest passes" in q5
    assert "report-index has no new blocking issue" in q5
    assert "forbidden capability scan passes" in q5
    assert "safety boundary regression passes" in q5
    assert "next_phase_allowed remains false for this Day155 rationale package" in q5


def test_day155_report_keeps_all_execution_provider_and_next_phase_flags_false():
    report = day155.build_day155_v05_ai_assistance_reopen_rationale(PROJECT_ROOT)

    assert report["day154_closure_baseline_lock_respected"] is True
    assert report["reviewer_assistance_only"] is True
    assert report["executor_recommendation_only"] is True
    assert report["fixed_output_template_required"] is True
    assert report["human_reviewer_final_authority"] is True
    for field in day155.REQUIRED_FALSE_FIELDS:
        assert report[field] is False

    template = report["fixed_review_output_template"]
    assert template["output_type"] == "templated_review_output_only"
    assert template["live_command_field_present"] is False
    assert template["executor_action_field_present"] is False
    assert template["provider_activation_field_present"] is False
    assert template["secrets_field_present"] is False

    assert report["forbidden_capability_scan"]["status"] == "PASS"
    assert report["forbidden_capability_scan"]["provider_api_live_device_activation_found"] is False
    assert report["forbidden_capability_scan"]["direct_command_generation_found"] is False
    assert report["forbidden_capability_scan"]["secrets_access_found"] is False
    assert report["forbidden_capability_scan"]["executor_unlock_found"] is False
    assert report["safety_boundary_regression"]["status"] == "PASS"
    assert report["safety_boundary_regression"]["next_phase_allowed"] is False
    assert report["result_semantics"]["ai_execution_allowed"] is False
    assert report["result_semantics"]["provider_api_integration_allowed"] is False
    assert report["result_semantics"]["executor_can_act_on_ai_output"] is False
    assert report["result_semantics"]["next_phase_allowed"] is False


def test_day155_reference_records_cover_registration_surfaces():
    report = day155.build_day155_v05_ai_assistance_reopen_rationale(PROJECT_ROOT)

    surfaces = {record["surface"] for record in report["reference_records"]}
    assert surfaces == {
        "Day155 roadmap doc",
        "Day155 AI doc",
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


def test_day155_cli_does_not_execute_provider_network_runner_or_prior_day_tasks(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day155 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day155 must not load runner profile or config data")

    def fail_day154(*args, **kwargs):
        raise AssertionError("Day155 must not rerun Day154")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day154_post_closure_evidence_baseline_lock_review", fail_day154)

    exit_code = network_lab.main(
        ["--task", "v05-ai-assistance-reopen-rationale"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: YES" in output
    assert "AGENTS.md result: FOUND_AND_READ" in output
    assert "AGENTS.md modified: false" in output
    assert "Task slug: v05-ai-assistance-reopen-rationale" in output
    assert "day: 155" in output
    assert "status: REVIEW_READY" in output
    assert "reviewer_assistance_only: true" in output
    assert "executor_recommendation_only: true" in output
    assert "execution_allowed: false" in output
    assert "provider_allowed: false" in output
    assert "api_allowed: false" in output
    assert "openai_api_call_allowed: false" in output
    assert "external_api_call_allowed: false" in output
    assert "live_device_allowed: false" in output
    assert "command_execution_allowed: false" in output
    assert "executor_unlock_allowed: false" in output
    assert "phase_gate_approval: false" in output
    assert "next_phase_allowed: false" in output
    assert "rationale_question_count: 5" in output
    assert "forbidden_capability_scan: PASS" in output
    assert "safety_boundary_regression: PASS" in output
    assert "PASS does not mean AI execution is allowed." in output
    assert "[PASS] V05_AI_ASSISTANCE_REOPEN_RATIONALE_REVIEW_READY" in output


def test_day155_negative_validation_blocks_unsafe_or_missing_values():
    report = day155.build_day155_v05_ai_assistance_reopen_rationale(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)

    unsafe["agents_md_pre_read"] = "NO"
    unsafe["agents_md_result"] = "MISSING"
    unsafe["agents_md_modified"] = True
    unsafe["rationale_questions"] = unsafe["rationale_questions"][:4]
    unsafe["pass_semantics"] = []
    unsafe["fixed_review_output_template"]["live_command_field_present"] = True
    unsafe["forbidden_capability_scan"]["direct_command_generation_found"] = True
    unsafe["safety_boundary_regression"]["day154_closure_baseline_lock_respected"] = False
    unsafe["safety_boundary_regression"]["next_phase_allowed"] = True
    unsafe["result_semantics"]["ai_execution_allowed"] = True
    unsafe["reference_records"][0]["path_exists"] = False
    unsafe["reference_records"][0]["missing_fragments"] = ["next_phase_allowed: false"]

    for field in day155.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True
    for field in day155.REQUIRED_TRUE_FIELDS:
        unsafe[field] = False

    errors = day155.collect_validation_errors(unsafe)

    assert "agents_md_pre_read must be YES." in errors
    assert "agents_md_result must be FOUND_AND_READ." in errors
    assert "agents_md_modified must be false." in errors
    assert "rationale_questions must contain exactly five questions." in errors
    assert "pass_semantics must preserve the Day155 PASS boundaries." in errors
    assert "fixed_review_output_template.live_command_field_present must be false." in errors
    assert "forbidden_capability_scan unsafe findings must all be false." in errors
    assert "safety_boundary_regression.day154_closure_baseline_lock_respected must be true." in errors
    assert "safety_boundary_regression.next_phase_allowed must be false." in errors
    assert "result_semantics.ai_execution_allowed must be false." in errors
    assert "Day155 roadmap doc path must exist." in errors
    assert "Day155 roadmap doc must contain all required fragments." in errors
    for field in day155.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors
    for field in day155.REQUIRED_TRUE_FIELDS:
        assert f"{field} must be true." in errors


def test_day155_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "v05-ai-assistance-reopen-rationale"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "v05-ai-assistance-reopen-rationale"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("v05-ai-assistance-reopen-rationale", handlers)

    assert resolve_task_name("v05-ai-assistance-reopen-rationale") == "v05-ai-assistance-reopen-rationale"
    assert resolved.canonical_name == "v05-ai-assistance-reopen-rationale"
    assert callable(resolved.handler)
    assert task["task_id"] == "day155_v05_ai_assistance_reopen_rationale"
    assert task["day"] == "Day155"
    assert task["user_display_name"] == "v0.5 AI Assistance Reopen Rationale"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day155_v05_ai_assistance_reopen_rationale.py"
    assert "DOCS_ONLY" in task["notes"]
    assert "RATIONALE_ONLY" in task["notes"]
    assert "execution_allowed=false" in task["notes"]
    assert "provider_allowed=false" in task["notes"]
    assert "api_allowed=false" in task["notes"]
    assert "executor_unlock_allowed=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]

    report = day155.build_day155_v05_ai_assistance_reopen_rationale(PROJECT_ROOT)
    json_path, html_path = day155.write_day155_v05_ai_assistance_reopen_rationale_reports(tmp_path, report)
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["day"] == 155
    assert written["status"] == "REVIEW_READY"
    assert written["next_phase_allowed"] is False
    assert written["execution_allowed"] is False
    assert written["provider_allowed"] is False
    assert written["api_allowed"] is False
    assert len(written["rationale_questions"]) == 5
    assert "Day155" in index_html
    assert "v0.5 AI Assistance Reopen Rationale" in index_html
    assert "reports/lab-summary/day155_v05_ai_assistance_reopen_rationale.json" in index_html


def test_day155_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day155.__file__).read_text(encoding="utf-8").lower()

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


def test_day155_docs_preserve_rationale_scope_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day155_v05_ai_assistance_reopen_rationale.md").read_text(
        encoding="utf-8"
    )
    ai_doc = (PROJECT_ROOT / "docs/ai/day155_v05_ai_assistance_reopen_rationale.md").read_text(
        encoding="utf-8"
    )
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for doc in (roadmap, ai_doc):
        assert "v0.5 AI Assistance Reopen Rationale" in doc
        assert "Why is AI needed?" in doc
        assert "Who does AI help?" in doc
        assert "What data may AI read?" in doc
        assert "What must AI never do?" in doc
        assert "Under what conditions is AI Assistance allowed into the repo?" in doc
        assert "AI is needed to simplify and automate reviewer-side testing review steps." in doc
        assert "Primary user: reviewer." in doc
        assert "repo reports" in doc
        assert "secrets" in doc
        assert "It must never directly issue commands." in doc
        assert "reviewer-assistance only" in doc
        assert "executor recommendation-only" in doc
        assert "fixed output template" in doc
        assert "pytest passes" in doc
        assert "report-index has no new blocking issue" in doc
        assert "forbidden capability scan passes" in doc
        assert "safety boundary regression passes" in doc
        assert "PASS does not mean AI execution is allowed." in doc
        assert "PASS does not mean provider/API integration is allowed." in doc
        assert "PASS does not mean executor can act on AI output." in doc
        assert "execution_allowed: false" in doc
        assert "executor_unlock_allowed: false" in doc
        assert "provider_allowed: false" in doc
        assert "api_allowed: false" in doc
        assert "openai_api_call_allowed: false" in doc
        assert "external_api_call_allowed: false" in doc
        assert "live_device_allowed: false" in doc
        assert "secrets_allowed: false" in doc
        assert "phase_gate_approval: false" in doc
        assert "next_phase_allowed: false" in doc

    assert "## Day155" in ai_readme
    assert "## Current Release Status" in readme
    assert "Stage-0 Network Automation Lab" in readme
    assert "Workflow Version 2" in readme
    assert "DEFERRED_SECURITY_RESEARCH_BLOCKED" in readme
    assert "WF-01-03C through WF-01-03F" in readme
