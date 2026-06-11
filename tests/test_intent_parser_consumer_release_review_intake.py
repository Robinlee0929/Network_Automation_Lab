import ast
import json
from pathlib import Path

import intent_parser_consumer_release_review_intake as day112
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "routeros_api",
    "openai",
    "requests",
    "httpx",
    "socket",
    "subprocess",
    "time",
    "datetime",
    "random",
    "uuid",
}


SAFE_AGENTS_TEXT = """# AGENTS.md

## Project

This repository is a Network Automation Lab for safe reviewer-visible validation.

## Core Safety Rules

- Do not perform live device access.
- Do not use SSH or real network-device commands.
- Do not execute configuration-changing commands.
- Preserve safety gates and no-execution proof.
- Report-only work remains report-only.
"""


def write_agents(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(SAFE_AGENTS_TEXT, encoding="utf-8")
    return path


def test_day112_default_report_receives_day111_package_for_triage_only(tmp_path):
    write_agents(tmp_path)

    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_INTAKE_READY_NON_EXECUTABLE"
    assert report["intake_status"] == "ACCEPTED_FOR_REVIEW"
    assert report["triage_status"] == "BLOCKED_CONDITIONS_PRESERVED"
    assert report["blocked_condition_status"] == "PRESERVED"
    assert report["decision_route"] == "ACCEPT_FOR_REVIEW"
    assert report["final_recommendation"] == "REVIEW_INTAKE_ACCEPTED_DO_NOT_ADVANCE"
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["approve_next_phase_execution_supported"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []

    summary = report["triage_summary"]
    assert summary["source_day"] == "Day111"
    assert summary["source_task"] == "parser-consumer-release-package"
    assert summary["source_release_package_status"] == "FROZEN"
    assert summary["source_reviewer_status"] == "RELEASE_PACKAGE_READY_REVIEW_ONLY"
    assert summary["source_final_recommendation"] == "RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE"
    assert summary["source_next_phase_allowed"] is False
    assert summary["source_blocked_condition_preserved"] is True


def test_day112_triage_checklist_is_non_executable_and_has_no_failed_checks(tmp_path):
    write_agents(tmp_path)

    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)
    checklist = report["intake_triage_checklist"]

    assert [item["id"] for item in checklist] == list(day112.REQUIRED_CHECKLIST_IDS)
    assert len(checklist) == 10
    assert report["triage_summary"]["checklist_pass_count"] == 10
    assert report["triage_summary"]["checklist_total_count"] == 10
    assert report["triage_summary"]["failed_check_count"] == 0
    assert all(item["status"] == "PASS" for item in checklist)
    assert all(item["required"] is True for item in checklist)
    assert all(item["blocks_advancement_if_failed"] is True for item in checklist)
    for item in checklist:
        assert set(item) == {
            "id",
            "description",
            "status",
            "required",
            "evidence",
            "blocks_advancement_if_failed",
        }


def test_day112_decision_routes_disallow_unlock_and_next_phase(tmp_path):
    write_agents(tmp_path)

    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)
    routes = {route["route"]: route for route in report["decision_routes"]}

    assert list(routes) == [
        "ACCEPT_FOR_REVIEW",
        "HOLD_FOR_BLOCKED_RECORDS",
        "RETURN_FOR_CLARIFICATION",
        "REJECT_PACKAGE",
        "APPROVE_NEXT_PHASE_EXECUTION",
    ]
    assert routes["ACCEPT_FOR_REVIEW"]["allowed"] is True
    assert routes["HOLD_FOR_BLOCKED_RECORDS"]["allowed"] is True
    assert routes["RETURN_FOR_CLARIFICATION"]["allowed"] is True
    assert routes["REJECT_PACKAGE"]["allowed"] is True
    assert routes["APPROVE_NEXT_PHASE_EXECUTION"]["allowed"] is False
    assert all(route["next_phase_allowed"] is False for route in routes.values())
    assert report["triage_summary"]["allowed_reviewer_route_count"] == 4
    assert report["triage_summary"]["forbidden_reviewer_route_count"] == 1


def test_day112_safety_invariants_remain_review_only_report_only_and_non_executable(tmp_path):
    write_agents(tmp_path)

    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)
    safety = report["safety_invariants"]

    for field in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "approval_unlock_supported",
        "approve_next_phase_execution_supported",
        "execution_readiness_supported",
        "mapped_task_execution_allowed",
        "adapter_invocation_allowed",
        "broker_invocation_allowed",
        "execution_broker_unlock_allowed",
        "runner_invocation_allowed",
        "next_phase_execution_allowed",
    ):
        assert safety[field] is False
    assert safety["review_only"] is True
    assert safety["report_only"] is True
    assert safety["deterministic"] is True
    assert safety["source_package_frozen"] is True


def test_day112_agents_pre_read_evidence_is_visible_and_agents_unmodified(tmp_path):
    write_agents(tmp_path)

    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)

    assert report["agents_md_read_before_day112_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["agents_md_pre_read_evidence"]["agents_md_file_found"] is True
    assert report["agents_md_pre_read_evidence"]["agents_md_file_readable"] is True


def test_day112_fails_closed_if_day111_source_unlocks_next_phase(tmp_path):
    write_agents(tmp_path)
    source = {
        "overall_status": "PASS",
        "reviewer_status": "RELEASE_PACKAGE_READY_REVIEW_ONLY",
        "release_package_status": "FROZEN",
        "final_recommendation": "RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE",
        "next_phase_allowed": True,
        "blocked_condition_summary": {"blocked_condition_preserved": True},
        "release_manifest": {
            "execution_unlocks_included": False,
            "mapped_task_execution_included": False,
        },
        "safety_invariants": {
            "review_only": True,
            "report_only": True,
            "deterministic": True,
            "ssh_allowed": False,
            "live_device_access_allowed": False,
            "network_command_execution_allowed": False,
            "config_mutation_allowed": False,
            "openai_api_allowed": False,
            "voice_runtime_allowed": False,
            "cloud_runtime_allowed": False,
            "approval_unlock_supported": False,
            "approve_next_phase_execution_supported": False,
            "mapped_task_execution_allowed": False,
            "execution_broker_unlock_allowed": False,
            "next_phase_execution_allowed": False,
        },
    }

    report = day112.build_parser_consumer_release_review_intake_report(
        project_root=tmp_path,
        day111_report=source,
    )

    assert report["overall_status"] == "FAIL"
    assert report["next_phase_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["approve_next_phase_execution_supported"] is False
    assert "intake triage checks must all pass" in " ".join(report["validation_errors"])
    assert "triage_summary.source_next_phase_allowed must be false." in report["validation_errors"]


def test_day112_writer_outputs_json_and_html_intake_checklist(tmp_path):
    write_agents(tmp_path)
    report = day112.build_parser_consumer_release_review_intake_report(project_root=tmp_path)

    json_path, html_path = day112.write_parser_consumer_release_review_intake_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day112_parser_consumer_release_review_intake.json"
    assert html_path == tmp_path / "reports/lab-summary/day112_parser_consumer_release_review_intake.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day112 Parser Consumer Release Review Intake / Reviewer Triage Checklist" in html
    assert "Reviewer Triage Checklist" in html
    assert "Decision Routes" in html
    assert "APPROVE_NEXT_PHASE_EXECUTION" in html
    assert "NEXT_PHASE_ALLOWED_FALSE" in html
    assert "AGENTS.md Pre-read Evidence" in html


def test_day112_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day112.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day112_runner_task_is_registered_and_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-consumer-release-review-intake")

    assert task["task_id"] == "day112_parser_consumer_release_review_intake"
    assert task["day"] == "Day112"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day112_parser_consumer_release_review_intake.json" in task["report_paths"]
    assert "reports/lab-summary/day112_parser_consumer_release_review_intake.html" in task["report_paths"]
    assert "docs/ai-intent/day112_parser_consumer_release_review_intake.md" in task["report_paths"]
    assert "docs/ai-intent/reviewer/day112_parser_consumer_release_review_intake.md" in task["report_paths"]
    assert "docs/roadmap/day112_parser_consumer_release_review_intake.md" in task["report_paths"]
    assert "agents_md_read_before_day112_work" in task["notes"]
    assert "reviewer_status=REVIEW_INTAKE_READY_NON_EXECUTABLE" in task["notes"]
    assert "intake_status=ACCEPTED_FOR_REVIEW" in task["notes"]
    assert "triage_status=BLOCKED_CONDITIONS_PRESERVED" in task["notes"]
    assert "blocked_condition_status=PRESERVED" in task["notes"]
    assert "checklist_pass_count=10" in task["notes"]
    assert "checklist_total_count=10" in task["notes"]
    assert "allowed_reviewer_route_count=4" in task["notes"]
    assert "forbidden_reviewer_route_count=1" in task["notes"]
    assert "approve_next_phase_execution_supported=false" in task["notes"]
    assert "approval_unlock_allowed=false" in task["notes"]
    assert "execution_readiness_allowed=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day112_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day112 intake must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day112 intake must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-consumer-release-review-intake"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day112 Parser Consumer Release Review Intake / Reviewer Triage Checklist" in output
    assert "Task name: parser-consumer-release-review-intake" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: REVIEW_INTAKE_READY_NON_EXECUTABLE" in output
    assert "intake_status: ACCEPTED_FOR_REVIEW" in output
    assert "triage_status: BLOCKED_CONDITIONS_PRESERVED" in output
    assert "blocked_condition_status: PRESERVED" in output
    assert "final_recommendation: REVIEW_INTAKE_ACCEPTED_DO_NOT_ADVANCE" in output
    assert "approval_unlock_allowed: false" in output
    assert "execution_readiness_allowed: false" in output
    assert "approve_next_phase_execution_supported: false" in output
    assert "next_phase_allowed: false" in output
    assert "source_release_package_status: FROZEN" in output
    assert "source_blocked_condition_preserved: true" in output
    assert "checklist_pass_count: 10" in output
    assert "checklist_total_count: 10" in output
    assert "allowed_reviewer_route_count: 4" in output
    assert "forbidden_reviewer_route_count: 1" in output
    assert "failed_check_count: 0" in output
    assert "JSON report: reports/lab-summary/day112_parser_consumer_release_review_intake.json" in output
    assert "HTML report: reports/lab-summary/day112_parser_consumer_release_review_intake.html" in output
    assert (tmp_path / "reports/lab-summary/day112_parser_consumer_release_review_intake.json").exists()
    assert (tmp_path / "reports/lab-summary/day112_parser_consumer_release_review_intake.html").exists()


def test_day112_report_index_visibility_includes_reviewer_intake(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-release-review-intake"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Release Review Intake / Reviewer Triage Checklist" in html
    assert "reviewer intake" in html
    assert "reports/lab-summary/day112_parser_consumer_release_review_intake.json" in html
    assert "reports/lab-summary/day112_parser_consumer_release_review_intake.html" in html
