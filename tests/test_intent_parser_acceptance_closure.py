import ast
import json
from pathlib import Path

import intent_parser_acceptance_closure as day105
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
}


def test_day105_closure_is_summary_only_and_safety_blocked():
    report = day105.build_parser_acceptance_closure_report()

    assert report["day"] == 105
    assert report["phase_name"] == "Parser Acceptance Closure / Safety-Blocked Exit Summary"
    assert report["closure_type"] == "SUMMARY_ONLY"
    assert report["final_recommendation"] == "SAFETY_BLOCKED_REVIEW_ONLY"
    assert report["safety_blocked"] is True
    assert report["next_phase_allowed"] is False
    assert report["capability_added"] is False
    assert report["parser_capability_added"] is False
    assert report["validation_errors"] == []


def test_day105_all_execution_flags_remain_false():
    report = day105.build_parser_acceptance_closure_report()

    assert report["execution_flags"] == day105.EXECUTION_FLAGS
    for flag in (
        "execution_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "config_change_allowed",
        "mapped_task_execution_allowed",
        "openai_api_allowed",
        "voice_input_allowed",
    ):
        assert report[flag] is False
        assert report["execution_flags"][flag] is False


def test_day105_covered_days_are_exactly_day96_through_day104():
    report = day105.build_parser_acceptance_closure_report()

    assert report["covered_days"] == [96, 97, 98, 99, 100, 101, 102, 103, 104]
    assert report["covered_day_ids"] == [
        "Day96",
        "Day97",
        "Day98",
        "Day99",
        "Day100",
        "Day101",
        "Day102",
        "Day103",
        "Day104",
    ]
    assert [item["day"] for item in report["covered_day_summaries"]] == report["covered_day_ids"]


def test_day105_safety_reasons_and_next_phase_conditions_are_non_empty():
    report = day105.build_parser_acceptance_closure_report()

    assert report["closure_summary"]
    assert report["safety_blocking_reasons"]
    assert report["next_phase_entry_conditions"]
    assert all(item["satisfied_for_day105"] is False for item in report["next_phase_entry_conditions"])
    assert report["evidence_references"]


def test_day105_report_writer_outputs_json_and_html(tmp_path):
    report = day105.build_parser_acceptance_closure_report()

    json_path, html_path = day105.write_parser_acceptance_closure_reports(tmp_path, report)

    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day105 Parser Acceptance Closure / Safety-Blocked Exit Summary" in html
    assert "SUMMARY_ONLY" in html
    assert "SAFETY_BLOCKED_REVIEW_ONLY" in html
    assert "reports/lab-summary/day105_parser_acceptance_closure.json" in html


def test_day105_module_has_no_live_or_external_tool_imports():
    tree = ast.parse(Path(day105.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day105_runner_task_returns_pass_without_execution(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day105 parser acceptance closure must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day105 parser acceptance closure must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-acceptance-closure"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day105_parser_acceptance_closure.json"
    html_path = tmp_path / "reports/lab-summary/day105_parser_acceptance_closure.html"
    assert exit_code == 0
    assert "Day105 Parser Acceptance Closure / Safety-Blocked Exit Summary" in output
    assert "Task name: parser-acceptance-closure" in output
    assert "Closure type: SUMMARY_ONLY" in output
    assert "Final recommendation: SAFETY_BLOCKED_REVIEW_ONLY" in output
    assert "next_phase_allowed = false" in output
    assert "parser_capability_added = false" in output
    assert "execution_allowed = false" in output
    assert "live_device_access_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "config_change_allowed = false" in output
    assert "mapped_task_execution_allowed = false" in output
    assert "openai_api_allowed = false" in output
    assert "voice_input_allowed = false" in output
    assert "JSON report: reports/lab-summary/day105_parser_acceptance_closure.json" in output
    assert "HTML report: reports/lab-summary/day105_parser_acceptance_closure.html" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()


def test_day105_report_index_visibility_includes_acceptance_closure(tmp_path):
    assert network_lab.main(["--task", "parser-acceptance-closure"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Acceptance Closure / Safety-Blocked Exit Summary" in html
    assert "SAFETY_BLOCKED_REVIEW_ONLY" in html
    assert "reports/lab-summary/day105_parser_acceptance_closure.json" in html
    assert "reports/lab-summary/day105_parser_acceptance_closure.html" in html


def test_day105_task_catalog_metadata_is_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-acceptance-closure")

    assert task["task_id"] == "day105_parser_acceptance_closure"
    assert task["day"] == "Day105"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day105_parser_acceptance_closure.json" in task["report_paths"]
    assert "docs/reviewer/day105_parser_acceptance_closure.md" in task["report_paths"]
    assert "SAFETY_BLOCKED_REVIEW_ONLY" in task["notes"]
    assert "next_phase_allowed" in task["notes"]


def test_day105_docs_and_html_do_not_introduce_action_surfaces(tmp_path):
    report = day105.build_parser_acceptance_closure_report()
    _json_path, html_path = day105.write_parser_acceptance_closure_reports(tmp_path, report)
    checked_paths = [
        html_path,
        Path("docs/ai-intent/day105_parser_acceptance_closure.md"),
        Path("docs/reviewer/day105_parser_acceptance_closure.md"),
        Path("docs/reviewer/README.md"),
        Path("docs/roadmap/day105_parser_acceptance_closure.md"),
    ]

    for path in checked_paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "<form" not in text
        assert "<button" not in text
        assert "method=\"post\"" not in text
        assert "action=" not in text
        assert "http://" not in text
        assert "https://" not in text
