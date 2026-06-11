import ast
import json
from pathlib import Path

import intent_parser_fixture_expansion as day102
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


def test_day102_report_is_deterministic_and_fixture_only():
    first = day102.build_parser_fixture_expansion_report()
    second = day102.build_parser_fixture_expansion_report()

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["reviewer_status"] == "FIXTURE_EXPANSION_READY"
    assert first["parser_capability_added"] is False
    assert first["parser_ready_for_broker"] is False
    assert first["broker_handoff_allowed"] is False
    assert first["execution_allowed"] is False
    assert first["adapter_invocation_allowed"] is False
    assert first["live_device_access_allowed"] is False
    assert first["ssh_allowed"] is False
    assert first["config_change_allowed"] is False
    assert first["validation_errors"] == []


def test_day102_fixtures_cover_all_required_categories():
    report = day102.build_parser_fixture_expansion_report()
    counts = report["summary"]["category_counts"]

    assert set(counts) == {"ambiguous", "malformed", "negative", "positive", "unsafe"}
    assert all(count >= 3 for count in counts.values())
    assert report["summary"]["total_fixtures"] >= 15
    assert report["summary"]["required_categories_present"] is True
    assert report["summary"]["success_criteria_met"] is True


def test_day102_positive_fixtures_are_not_rejected():
    fixtures = [
        fixture
        for fixture in day102.build_day102_parser_fixture_cases()
        if fixture["category"] == "positive"
    ]

    assert fixtures
    assert all(fixture["accepted_by_fixture_contract"] is True for fixture in fixtures)
    assert all(fixture["expected_parser_status"] == "PARSED" for fixture in fixtures)
    assert all(fixture["fixture_classification"] == "accepted_readonly_report_only" for fixture in fixtures)
    assert all(fixture["reason"] is None for fixture in fixtures)
    assert all(fixture["executable_allowed"] is False for fixture in fixtures)
    assert all(fixture["broker_handoff_allowed"] is False for fixture in fixtures)


def test_day102_negative_fixtures_are_clearly_rejected():
    fixtures = [
        fixture
        for fixture in day102.build_day102_parser_fixture_cases()
        if fixture["category"] == "negative"
    ]

    assert fixtures
    assert all(fixture["accepted_by_fixture_contract"] is False for fixture in fixtures)
    assert all(fixture["expected_parser_status"] == "UNSUPPORTED_OUTPUT" for fixture in fixtures)
    assert all(fixture["fixture_classification"] == "rejected_unsupported" for fixture in fixtures)
    assert all(fixture["reason_present"] is True for fixture in fixtures)
    assert all(fixture["reviewer_action"] == "reject_with_unsupported_reason" for fixture in fixtures)


def test_day102_malformed_fixtures_do_not_crash_and_have_reason():
    fixtures = [
        fixture
        for fixture in day102.build_day102_parser_fixture_cases()
        if fixture["category"] == "malformed"
    ]

    assert fixtures
    assert all(fixture["accepted_by_fixture_contract"] is False for fixture in fixtures)
    assert all(fixture["expected_parser_status"] == "MALFORMED_INPUT" for fixture in fixtures)
    assert all(fixture["malformed_handled_without_exception"] is True for fixture in fixtures)
    assert all(fixture["reason_present"] is True for fixture in fixtures)
    assert any(fixture["raw_input_preview"] == "<missing>" for fixture in fixtures)


def test_day102_ambiguous_fixtures_are_not_silently_accepted():
    fixtures = [
        fixture
        for fixture in day102.build_day102_parser_fixture_cases()
        if fixture["category"] == "ambiguous"
    ]

    assert fixtures
    assert all(fixture["accepted_by_fixture_contract"] is False for fixture in fixtures)
    assert all(fixture["expected_parser_status"] == "AMBIGUOUS_OUTPUT" for fixture in fixtures)
    assert all(fixture["ambiguous_not_silently_accepted"] is True for fixture in fixtures)
    assert all(fixture["reason_present"] is True for fixture in fixtures)


def test_day102_unsafe_fixtures_block_live_mutating_ssh_and_config_intent():
    fixtures = [
        fixture
        for fixture in day102.build_day102_parser_fixture_cases()
        if fixture["category"] == "unsafe"
    ]
    marker_text = " ".join(
        marker
        for fixture in fixtures
        for marker in fixture["unsafe_intent_markers"]
    ).lower()

    assert fixtures
    assert all(fixture["accepted_by_fixture_contract"] is False for fixture in fixtures)
    assert all(fixture["expected_parser_status"] == "UNSAFE_INTENT_BLOCKED" for fixture in fixtures)
    assert all(fixture["unsafe_intent_blocked"] is True for fixture in fixtures)
    assert all(fixture["reason_present"] is True for fixture in fixtures)
    assert "ssh" in marker_text
    assert "config" in marker_text
    assert "apply" in marker_text
    assert all(fixture["ssh_allowed"] is False for fixture in fixtures)
    assert all(fixture["config_change_allowed"] is False for fixture in fixtures)
    assert all(fixture["live_device_access_allowed"] is False for fixture in fixtures)


def test_day102_success_criteria_match_fixture_expectations():
    report = day102.build_parser_fixture_expansion_report()

    assert set(report["success_criteria"]) == {
        "positive",
        "negative",
        "malformed",
        "ambiguous",
        "unsafe",
    }
    assert all(criteria["met"] is True for criteria in report["success_criteria"].values())
    assert report["summary"]["positive_not_rejected_count"] >= 3
    assert report["summary"]["unsupported_clear_rejection_count"] >= 3
    assert report["summary"]["malformed_no_crash_count"] >= 3
    assert report["summary"]["ambiguous_rejected_count"] >= 3
    assert report["summary"]["unsafe_blocked_count"] >= 3
    assert report["summary"]["reason_missing_count"] == 0
    assert report["summary"]["runtime_violation_count"] == 0


def test_day102_safety_invariants_keep_runtime_surfaces_disabled():
    report = day102.build_parser_fixture_expansion_report()
    invariants = report["safety_invariants"]

    assert invariants["report_only"] is True
    assert invariants["static_fixture_only"] is True
    assert invariants["fixture_expansion_only"] is True
    assert invariants["parser_output_is_review_data_only"] is True
    for flag in day102.RUNTIME_DISABLED_FLAGS:
        assert invariants[flag] is False


def test_day102_validator_rejects_missing_reason_for_rejected_fixture():
    report = day102.build_parser_fixture_expansion_report()
    rejected = next(fixture for fixture in report["fixture_cases"] if fixture["category"] == "negative")
    rejected["reason"] = ""
    rejected["reason_present"] = False

    errors = day102.validate_parser_fixture_expansion_report(report)

    assert any("rejected fixture must include a reason" in error for error in errors)


def test_day102_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day102.build_parser_fixture_expansion_report()
    json_path, html_path = day102.write_parser_fixture_expansion_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/ai/day102_parser_fixture_expansion.json"
    assert html_path == tmp_path / "reports/ai/day102_parser_fixture_expansion.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day102 Parser Fixture Expansion" in html
    assert "positive" in html
    assert "negative" in html
    assert "malformed" in html
    assert "ambiguous" in html
    assert "unsafe" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day102_runner_task_returns_pass_without_broker_executor_or_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day102 parser fixture expansion must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day102 parser fixture expansion must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-fixture-expansion"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day102 Parser Fixture Expansion" in output
    assert "Task name: parser-fixture-expansion" in output
    assert "PASS / FIXTURE_EXPANSION_READY" in output
    assert "Total fixtures: 15" in output
    assert "positive fixtures: 3" in output
    assert "negative fixtures: 3" in output
    assert "malformed fixtures: 3" in output
    assert "ambiguous fixtures: 3" in output
    assert "unsafe fixtures: 3" in output
    assert "success_criteria_met = true" in output
    assert "parser_capability_added = false" in output
    assert "broker_handoff_allowed = false" in output
    assert "ssh_allowed = false" in output
    assert "config_change_allowed = false" in output
    assert "JSON report: reports/ai/day102_parser_fixture_expansion.json" in output
    assert "HTML report: reports/ai/day102_parser_fixture_expansion.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day102_report_index_visibility_includes_fixture_expansion(tmp_path):
    assert network_lab.main(["--task", "parser-fixture-expansion"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Parser Fixture Expansion" in html
    assert "positive, negative, malformed, ambiguous, and unsafe" in html
    assert "reports/ai/day102_parser_fixture_expansion.json" in html
    assert "reports/ai/day102_parser_fixture_expansion.html" in html


def test_day102_task_catalog_contains_fixture_expansion_metadata():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-fixture-expansion")

    assert task["task_id"] == "day102_parser_fixture_expansion"
    assert task["day"] == "Day102"
    assert task["display_name"] == "Day102 Parser Fixture Expansion"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day102_parser_fixture_expansion.json" in task["report_paths"]
    assert "reports/ai/day102_parser_fixture_expansion.html" in task["report_paths"]
    assert "docs/ai-intent/day102_parser_fixture_expansion.md" in task["report_paths"]
    assert "positive, negative, malformed, ambiguous, and unsafe" in task["notes"]
    assert "parser_capability_added remains false" in task["notes"]
    assert "broker_handoff_allowed remains false" in task["notes"]
    assert "ssh_allowed remains false" in task["notes"]


def test_day102_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day102.__file__)
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
