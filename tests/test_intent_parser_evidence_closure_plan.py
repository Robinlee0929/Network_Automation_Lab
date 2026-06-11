import ast
import json
from pathlib import Path

import intent_parser_evidence_closure_plan as day101
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "asyncssh",
    "routeros_api",
    "librouteros",
    "socket",
    "telnetlib",
    "subprocess",
    "openai",
}


def test_day101_report_is_deterministic_and_blocks_broker_handoff():
    first = day101.build_parser_evidence_closure_plan_report()
    second = day101.build_parser_evidence_closure_plan_report()

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["reviewer_status"] == "EVIDENCE_CLOSURE_PLAN_READY"
    assert first["parser_ready_for_broker"] is False
    assert first["broker_handoff_allowed"] is False
    assert first["execution_allowed"] is False
    assert first["live_device_access_allowed"] is False
    assert first["ssh_allowed"] is False
    assert first["openai_api_allowed"] is False
    assert first["evidence_closure_required"] is True
    assert first["phase_gate_rerun_required"] is True
    assert first["validation_errors"] == []


def test_day101_represents_under_covered_and_review_only_findings():
    report = day101.build_parser_evidence_closure_plan_report()
    under_covered = {item["category"] for item in report["under_covered_categories"]}
    review_only = {item["category"] for item in report["review_only_categories"]}
    closure_decisions = {item["day100_decision"] for item in report["closure_items"]}

    assert under_covered
    assert review_only
    assert "supported_table_parse" in under_covered
    assert {"UNDER_COVERED", "REVIEW_ONLY"}.issubset(closure_decisions)
    assert report["summary"]["under_covered_category_count"] == len(report["under_covered_categories"])
    assert report["summary"]["review_only_category_count"] == len(report["review_only_categories"])


def test_day101_closure_items_have_required_evidence_and_follow_up_days():
    report = day101.build_parser_evidence_closure_plan_report()
    required_fields = {
        "priority",
        "category",
        "gap",
        "required_evidence",
        "target_follow_up_day",
        "day100_decision",
        "day100_coverage_status",
        "risk",
        "blocked_from_advancement",
    }

    assert report["closure_items"]
    for item in report["closure_items"]:
        assert required_fields.issubset(item)
        assert item["priority"] >= 1
        assert item["gap"]
        assert item["required_evidence"]
        assert item["target_follow_up_day"] in {"Day102", "Day103", "Day104", "Day105"}
        assert item["day100_decision"] in {"UNDER_COVERED", "REVIEW_ONLY"}
        assert item["blocked_from_advancement"] is True
        assert item["parser_ready_for_broker"] is False
        assert item["broker_handoff_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["live_device_access_allowed"] is False
        assert item["ssh_allowed"] is False
        assert item["openai_api_allowed"] is False


def test_day101_recommended_sequence_is_day102_to_day105_in_order():
    report = day101.build_parser_evidence_closure_plan_report()
    sequence = report["recommended_sequence"]

    assert [step["day"] for step in sequence] == ["Day102", "Day103", "Day104", "Day105"]
    assert [step["name"] for step in sequence] == [
        "Parser Fixture Expansion",
        "Parser Schema Stability Regression",
        "Parser Reject-by-default Regression",
        "Parser Re-Gate Review",
    ]
    assert all(step["broker_handoff_allowed"] is False for step in sequence)
    assert report["next_phase_gate"] == "Day105 Parser Re-Gate Review"


def test_day101_safety_invariants_keep_parser_gate_closed():
    report = day101.build_parser_evidence_closure_plan_report()
    invariants = report["safety_invariants"]

    assert invariants["report_only"] is True
    assert invariants["planning_only"] is True
    assert invariants["parser_capability_added"] is False
    assert invariants["parser_gate_released"] is False
    assert invariants["broker_boundary_opened"] is False
    assert invariants["broker_connection_attempted"] is False
    assert invariants["phase_gate_rerun_required"] is True
    assert invariants["evidence_closure_required"] is True
    for flag in day101.RUNTIME_DISABLED_FLAGS:
        assert invariants[flag] is False


def test_day101_validator_rejects_any_broker_handoff_unlock():
    report = day101.build_parser_evidence_closure_plan_report()
    report["broker_handoff_allowed"] = True

    errors = day101.validate_parser_evidence_closure_plan_report(report)

    assert any("broker_handoff_allowed must be false" in error for error in errors)


def test_day101_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day101.build_parser_evidence_closure_plan_report()
    json_path, html_path = day101.write_parser_evidence_closure_plan_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day101_parser_evidence_closure_plan.json"
    assert html_path == tmp_path / "reports/ai/day101_parser_evidence_closure_plan.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day101 Parser Evidence Closure Plan" in html
    assert "UNDER_COVERED" in html
    assert "REVIEW_ONLY" in html
    assert "parser_ready_for_broker=false" in html
    assert "broker_handoff_allowed=false" in html
    assert "phase_gate_rerun_required=true" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day101_runner_task_returns_pass_without_broker_executor_or_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day101 parser evidence closure plan must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day101 parser evidence closure plan must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-evidence-closure-plan"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day101 Parser Evidence Closure Plan" in output
    assert "Task name: parser-evidence-closure-plan" in output
    assert "PASS / EVIDENCE_CLOSURE_PLAN_READY" in output
    assert "Closure item count:" in output
    assert "Blocked category count:" in output
    assert "Recommended next action count: 4" in output
    assert "parser_ready_for_broker = false" in output
    assert "broker_handoff_allowed = false" in output
    assert "phase_gate_rerun_required = true" in output
    assert "Day102 -> Day103 -> Day104 -> Day105" in output
    assert "JSON report: reports/ai/day101_parser_evidence_closure_plan.json" in output
    assert "HTML report: reports/ai/day101_parser_evidence_closure_plan.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day101_report_index_visibility_includes_closure_plan(tmp_path):
    assert network_lab.main(["--task", "parser-evidence-closure-plan"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Parser Evidence Closure Plan" in html
    assert "reports/ai/day101_parser_evidence_closure_plan.json" in html
    assert "reports/ai/day101_parser_evidence_closure_plan.html" in html
    assert "broker handoff blocked" in html


def test_day101_task_catalog_contains_closure_plan_metadata():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-evidence-closure-plan")

    assert task["task_id"] == "day101_parser_evidence_closure_plan"
    assert task["day"] == "Day101"
    assert task["display_name"] == "Day101 Parser Evidence Closure Plan"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day101_parser_evidence_closure_plan.json" in task["report_paths"]
    assert "reports/ai/day101_parser_evidence_closure_plan.html" in task["report_paths"]
    assert "docs/ai-intent/day101_parser_evidence_closure_plan.md" in task["report_paths"]
    assert "UNDER_COVERED" in task["notes"]
    assert "REVIEW_ONLY" in task["notes"]
    assert "parser_ready_for_broker remains false" in task["notes"]
    assert "broker_handoff_allowed remains false" in task["notes"]
    assert "phase_gate_rerun_required remains true" in task["notes"]


def test_day101_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day101.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    assert ".connect(" not in source
    assert ".send(" not in source
    assert ".recv(" not in source
    assert "subprocess." not in source
    assert "config.json" not in source
    assert "credential" not in source.lower()
    assert "password" not in source.lower()
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
