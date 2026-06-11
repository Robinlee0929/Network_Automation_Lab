import ast
import json
from pathlib import Path

import intent_parser_consumer_release_package as day111
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


def test_day111_default_report_freezes_day107_to_day110_and_stays_locked(tmp_path):
    write_agents(tmp_path)

    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "RELEASE_PACKAGE_READY_REVIEW_ONLY"
    assert report["release_package_status"] == "FROZEN"
    assert report["final_recommendation"] == "RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE"
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []
    assert [record["day"] for record in report["source_days"]] == [107, 108, 109, 110]
    assert report["release_manifest"]["source_day_count"] == 4
    assert report["release_manifest"]["frozen_evidence_count"] == 4
    assert len(report["frozen_evidence_chain"]) == 4
    assert all(record["frozen"] is True for record in report["frozen_evidence_chain"])
    assert all(record["execution_allowed"] is False for record in report["frozen_evidence_chain"])


def test_day111_preserves_day109_blocked_records_and_day110_final_gate(tmp_path):
    write_agents(tmp_path)

    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)
    blocked = report["blocked_condition_summary"]

    assert blocked["day109_observed_status"] == "BLOCKED_RECORDS_PRESENT"
    assert blocked["day109_ready_count"] == 1
    assert blocked["day109_needs_clarification_count"] == 1
    assert blocked["day109_blocked_count"] == 1
    assert blocked["day109_blocking_condition_preserved"] is True
    assert blocked["day110_observed_status"] == "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS"
    assert blocked["day110_final_recommendation"] == "DO_NOT_ADVANCE_BLOCKED_RECORDS_PRESENT"
    assert blocked["day110_next_phase_allowed"] is False
    assert blocked["blocked_condition_preserved"] is True


def test_day111_safety_invariants_are_review_only_report_only_and_non_executable(tmp_path):
    write_agents(tmp_path)

    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)
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
        "mapped_task_execution_allowed",
        "execution_broker_unlock_allowed",
        "next_phase_execution_allowed",
    ):
        assert safety[field] is False
    assert safety["review_only"] is True
    assert safety["report_only"] is True
    assert safety["deterministic"] is True
    assert report["traceability_summary"]["safety_invariant_result"] == "PASS"


def test_day111_agents_pre_read_evidence_is_visible_and_agents_unmodified(tmp_path):
    write_agents(tmp_path)

    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)

    assert report["agents_md_read_before_day111_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["agents_md_pre_read_evidence"]["agents_md_file_found"] is True
    assert report["agents_md_pre_read_evidence"]["agents_md_file_readable"] is True


def test_day111_report_paths_match_expected_outputs(tmp_path):
    write_agents(tmp_path)

    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)

    assert report["report_paths"] == {
        "json": "reports/lab-summary/day111_parser_consumer_release_package.json",
        "html": "reports/lab-summary/day111_parser_consumer_release_package.html",
    }
    assert report["release_manifest"]["generated_reports"] == report["report_paths"]


def test_day111_writer_outputs_json_and_html_release_package(tmp_path):
    write_agents(tmp_path)
    report = day111.build_parser_consumer_release_package_report(project_root=tmp_path)

    json_path, html_path = day111.write_parser_consumer_release_package_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day111_parser_consumer_release_package.json"
    assert html_path == tmp_path / "reports/lab-summary/day111_parser_consumer_release_package.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day111 Parser Consumer Evidence Freeze / Release Package" in html
    assert "Day107-Day110 Source Chain" in html
    assert "Frozen Evidence Status" in html
    assert "Blocked Condition Preserved" in html
    assert "RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE" in html
    assert "AGENTS.md Pre-read Evidence" in html


def test_day111_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day111.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day111_runner_task_is_registered_and_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-consumer-release-package")

    assert task["task_id"] == "day111_parser_consumer_release_package"
    assert task["day"] == "Day111"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day111_parser_consumer_release_package.json" in task["report_paths"]
    assert "reports/lab-summary/day111_parser_consumer_release_package.html" in task["report_paths"]
    assert "docs/ai-intent/day111_parser_consumer_release_package.md" in task["report_paths"]
    assert "docs/ai-intent/reviewer/day111_parser_consumer_release_package.md" in task["report_paths"]
    assert "docs/roadmap/day111_parser_consumer_release_package.md" in task["report_paths"]
    assert "agents_md_read_before_day111_work" in task["notes"]
    assert "blocked_condition_preserved=true" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day111_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day111 release package must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day111 release package must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-consumer-release-package"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day111 Parser Consumer Evidence Freeze / Release Package" in output
    assert "Task name: parser-consumer-release-package" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: RELEASE_PACKAGE_READY_REVIEW_ONLY" in output
    assert "release_package_status: FROZEN" in output
    assert "final_recommendation: RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE" in output
    assert "next_phase_allowed: false" in output
    assert "agents_md_read_before_day111_work: true" in output
    assert "agents_md_pre_read_result: PASS" in output
    assert "agents_md_modified: false" in output
    assert "source_day_count: 4" in output
    assert "frozen_evidence_count: 4" in output
    assert "blocked_condition_preserved: true" in output
    assert "safety_invariant_result: PASS" in output
    assert "JSON report: reports/lab-summary/day111_parser_consumer_release_package.json" in output
    assert "HTML report: reports/lab-summary/day111_parser_consumer_release_package.html" in output
    assert (tmp_path / "reports/lab-summary/day111_parser_consumer_release_package.json").exists()
    assert (tmp_path / "reports/lab-summary/day111_parser_consumer_release_package.html").exists()


def test_day111_report_index_visibility_includes_release_package(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-release-package"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Evidence Freeze / Release Package" in html
    assert "Day107-Day110" in html
    assert "reports/lab-summary/day111_parser_consumer_release_package.json" in html
    assert "reports/lab-summary/day111_parser_consumer_release_package.html" in html
