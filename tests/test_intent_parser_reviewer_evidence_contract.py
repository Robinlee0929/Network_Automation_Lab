import ast
import json
from pathlib import Path

import pytest

import intent_parser_reviewer_evidence_contract as day107
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


def test_day107_pass_path_accepts_review_only_continuation():
    report = day107.build_parser_reviewer_evidence_contract_report()

    assert report["day"] == 107
    assert report["task"] == "parser-reviewer-evidence-contract"
    assert report["phase_name"] == "Parser Reviewer Evidence Contract Consolidation"
    assert report["created_at"] == "2026-06-11T00:00:00+08:00"
    assert report["audit_type"] == "REPORT_ONLY"
    assert report["evidence_scope"] == "Day96-Day105"
    assert report["evidence_chain_complete"] is True
    assert report["overall_status"] == "PASS"
    assert report["final_recommendation"] == (
        "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION"
    )
    assert report["accepted_for_review_only_continuation"] is True
    assert report["accepted_for_live_execution"] is False
    assert report["validation_errors"] == []


def test_day107_missing_evidence_stage_creates_warn():
    items = [
        item for item in day107.build_default_evidence_items()
        if item["day"] != 100
    ]

    report = day107.build_parser_reviewer_evidence_contract_report(items)

    assert report["overall_status"] == "WARN"
    assert report["missing_evidence_days"] == [100]
    assert report["final_recommendation"] == (
        "PARSER_REVIEWER_EVIDENCE_CONTRACT_NEEDS_GAP_REVIEW"
    )
    assert report["accepted_for_review_only_continuation"] is False
    assert report["accepted_for_live_execution"] is False


@pytest.mark.parametrize(
    "flag",
    [
        "live_execution_allowed",
        "ssh_allowed",
        "device_connection_allowed",
        "config_mutation_allowed",
        "adapter_invocation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "rejected_intent_execution_allowed",
        "accepted_for_live_execution",
    ],
)
def test_day107_permission_unlock_creates_fail_and_output_flags_stay_false(flag):
    report = day107.build_parser_reviewer_evidence_contract_report(
        safety_overrides={flag: True}
    )

    assert report["overall_status"] == "FAIL"
    assert report["final_recommendation"] == (
        "PARSER_REVIEWER_EVIDENCE_CONTRACT_REJECTED_FOR_SAFETY_RISK"
    )
    assert flag in report["safety_violation_fields"]
    assert report["accepted_for_review_only_continuation"] is False
    assert report["accepted_for_live_execution"] is False
    for no_execution_flag in day107.ALL_NO_EXECUTION_FLAGS:
        assert report[no_execution_flag] is False
        assert report["no_execution_proof"][no_execution_flag] is False


def test_day107_evidence_item_execution_or_unlocked_boundary_creates_fail():
    items = day107.build_default_evidence_items()
    items[0]["execution_allowed"] = True

    execution_report = day107.build_parser_reviewer_evidence_contract_report(items)

    assert execution_report["overall_status"] == "FAIL"
    assert "Day96.execution_allowed" in execution_report["safety_violation_fields"]

    items = day107.build_default_evidence_items()
    items[1]["safety_boundary_locked"] = False

    boundary_report = day107.build_parser_reviewer_evidence_contract_report(items)

    assert boundary_report["overall_status"] == "FAIL"
    assert "Day97.safety_boundary_locked" in boundary_report["safety_violation_fields"]


def test_day107_report_contains_day96_through_day105_evidence_items():
    report = day107.build_parser_reviewer_evidence_contract_report()

    assert [item["day"] for item in report["evidence_items"]] == [
        96,
        97,
        98,
        99,
        100,
        101,
        102,
        103,
        104,
        105,
    ]
    assert "Day96-Day105" == report["evidence_scope"]


def test_day107_every_evidence_item_has_required_contract_fields():
    report = day107.build_parser_reviewer_evidence_contract_report()

    for item in report["evidence_items"]:
        for field in day107.REQUIRED_ITEM_FIELDS:
            assert field in item
        assert item["execution_allowed"] is False
        assert item["safety_boundary_locked"] is True
        assert item["reviewer_acceptance_relevance"]


def test_day107_report_writer_outputs_stable_json_and_html_paths(tmp_path):
    report = day107.build_parser_reviewer_evidence_contract_report()

    json_path, html_path = day107.write_parser_reviewer_evidence_contract_reports(
        tmp_path, report
    )

    assert json_path == tmp_path / "reports/lab-summary/day107_parser_reviewer_evidence_contract.json"
    assert html_path == tmp_path / "reports/lab-summary/day107_parser_reviewer_evidence_contract.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day107 Parser Reviewer Evidence Contract Consolidation" in html
    assert "reports/lab-summary/day107_parser_reviewer_evidence_contract.json" in html
    assert "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION" in html


def test_day107_writer_does_not_modify_agents_md(tmp_path):
    agents_path = tmp_path / "AGENTS.md"
    agents_text = "# AGENTS.md\n\nDo not modify this sentinel.\n"
    agents_path.write_text(agents_text, encoding="utf-8")

    day107.write_parser_reviewer_evidence_contract_reports(tmp_path)

    assert agents_path.read_text(encoding="utf-8") == agents_text


def test_day107_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day107.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day107_runner_task_is_registered_and_report_only():
    task = next(
        task for task in network_lab.list_tasks()
        if task["id"] == "parser-reviewer-evidence-contract"
    )

    assert task["task_id"] == "day107_parser_reviewer_evidence_contract"
    assert task["day"] == "Day107"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day107_parser_reviewer_evidence_contract.json" in task["report_paths"]
    assert "docs/ai-intent/day107_parser_reviewer_evidence_contract.md" in task["report_paths"]


def test_day107_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day107 parser reviewer evidence contract must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day107 parser reviewer evidence contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-reviewer-evidence-contract"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day107 Parser Reviewer Evidence Contract Consolidation" in output
    assert "Task name: parser-reviewer-evidence-contract" in output
    assert "Audit type: REPORT_ONLY" in output
    assert "evidence_chain_complete = true" in output
    assert "accepted_for_review_only_continuation = true" in output
    assert "accepted_for_live_execution = false" in output
    assert "live_execution_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "device_connection_allowed = false" in output
    assert "config_mutation_allowed = false" in output
    assert "openai_api_allowed = false" in output
    assert "voice_runtime_allowed = false" in output
    assert "adapter_invocation_allowed = false" in output
    assert "rejected_intent_execution_allowed = false" in output
    assert "JSON report: reports/lab-summary/day107_parser_reviewer_evidence_contract.json" in output
    assert "HTML report: reports/lab-summary/day107_parser_reviewer_evidence_contract.html" in output
    assert (tmp_path / "reports/lab-summary/day107_parser_reviewer_evidence_contract.json").exists()
    assert (tmp_path / "reports/lab-summary/day107_parser_reviewer_evidence_contract.html").exists()


def test_day107_report_index_visibility_includes_contract(tmp_path):
    assert network_lab.main(["--task", "parser-reviewer-evidence-contract"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Reviewer Evidence Contract Consolidation" in html
    assert "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION" in html
    assert "reports/lab-summary/day107_parser_reviewer_evidence_contract.json" in html
    assert "reports/lab-summary/day107_parser_reviewer_evidence_contract.html" in html
