import ast
import json
from pathlib import Path

import intent_adapter_result_normalization as day95
import intent_readonly_output_parser_prototype as day96
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
}


def _day95_result_by_scenario(scenario_id: str):
    report = day95.run_adapter_result_normalization()
    return next(
        result
        for result in report["normalized_result_records"]
        if result["scenario_id"] == scenario_id
    )


def test_day96_parser_accepts_valid_day95_key_value_simulated_output():
    result = _day95_result_by_scenario("D95-S01-readonly-identity")
    parsed = day96.parse_normalized_fake_adapter_result(result)

    assert parsed["parser_status"] == "PARSED"
    assert parsed["source_kind"] == "fake_adapter_simulated_output"
    assert parsed["parser_mode"] == "parser_only"
    assert parsed["parsed_records"] == [
        {
            "record_type": "key_value",
            "line_number": 1,
            "key": "name",
            "value": "lab-router-simulated",
        }
    ]


def test_day96_parser_accepts_valid_day95_simple_text_lines():
    result = _day95_result_by_scenario("D95-S02-readonly-interfaces-multiline")
    parsed = day96.parse_normalized_fake_adapter_result(result)

    assert parsed["parser_status"] == "PARSED"
    assert [record["record_type"] for record in parsed["parsed_records"]] == [
        "text_line",
        "text_line",
        "text_line",
    ]
    assert parsed["parsed_records"][0]["text"] == "ether1 running"


def test_day96_parser_supports_fake_only_table_like_text_fixture():
    result = _day95_result_by_scenario("D95-S01-readonly-identity")
    result = json.loads(json.dumps(result))
    result["scenario_id"] = "D96-TEST-table-fixture"
    result["result_payload"]["simulated_output"] = "label  state\nalpha  ready\nbeta  review"

    parsed = day96.parse_normalized_fake_adapter_result(result)

    assert parsed["parser_status"] == "PARSED"
    assert parsed["parsed_records"] == [
        {
            "record_type": "table_row",
            "line_number": 2,
            "fields": {"label": "alpha", "state": "ready"},
        },
        {
            "record_type": "table_row",
            "line_number": 3,
            "fields": {"label": "beta", "state": "review"},
        },
    ]


def test_day96_parser_marks_missing_simulated_output_review_needed():
    result = _day95_result_by_scenario("D95-S01-readonly-identity")
    result = json.loads(json.dumps(result))
    del result["result_payload"]["simulated_output"]

    parsed = day96.parse_normalized_fake_adapter_result(result)

    assert parsed["parser_status"] == "REVIEW_NEEDED"
    assert parsed["parsed_records"] == []
    assert any("Missing simulated_output" in warning for warning in parsed["warnings"])
    assert parsed["live_fallback_attempted"] is False


def test_day96_parser_marks_unsupported_type_without_fallback():
    result = _day95_result_by_scenario("D95-S01-readonly-identity")
    result = json.loads(json.dumps(result))
    result["result_payload"]["simulated_output"] = {"not": "text"}

    parsed = day96.parse_normalized_fake_adapter_result(result)

    assert parsed["parser_status"] == "UNSUPPORTED"
    assert parsed["parsed_records"] == []
    assert parsed["unsupported_sections"][0]["section"] == "result_payload.simulated_output"
    assert parsed["live_fallback_attempted"] is False
    assert parsed["adapter_fallback_attempted"] is False
    assert parsed["runner_live_path_attempted"] is False


def test_day96_parser_safety_metadata_is_always_disabled():
    parsed = day96.parse_normalized_fake_adapter_result(
        _day95_result_by_scenario("D95-S01-readonly-identity")
    )

    assert parsed["live_read_enabled"] is False
    assert parsed["ssh_enabled"] is False
    assert parsed["routeros_enabled"] is False
    assert parsed["device_access_enabled"] is False
    assert parsed["not_verified_device_truth"] is True


def test_day96_malformed_input_does_not_trigger_live_fallback():
    parsed = day96.parse_normalized_fake_adapter_result(
        {"result_payload": {"simulated_output": "name: malformed-fixture"}}
    )

    assert parsed["parser_status"] == "REVIEW_NEEDED"
    assert parsed["parsed_records"] == []
    assert parsed["live_fallback_attempted"] is False
    assert parsed["adapter_fallback_attempted"] is False
    assert parsed["runner_live_path_attempted"] is False
    assert any("Malformed normalized result" in warning for warning in parsed["warnings"])


def test_day96_report_builds_parser_only_safety_evidence():
    report = day96.build_day96_parser_report()

    assert report["overall_status"] == "PASS"
    assert report["phase"] == "PARSER_PROTOTYPE_READY"
    assert report["parsed_records_summary"]["parsed_case_count"] >= 2
    assert report["parsed_records_summary"]["review_needed_case_count"] >= 2
    assert report["parsed_records_summary"]["unsupported_case_count"] >= 1
    assert report["parsed_records_summary"]["live_fallback_attempts"] == 0
    assert report["parsed_records_summary"]["adapter_fallback_attempts"] == 0
    assert report["parsed_records_summary"]["device_access_attempts"] == 0
    assert report["evidence"]["all_inputs_fake_only_simulated_outputs"] is True
    assert report["evidence"]["live_read_enabled"] is False
    assert report["evidence"]["ssh_enabled"] is False
    assert report["evidence"]["routeros_enabled"] is False
    assert report["evidence"]["device_access_enabled"] is False
    assert report["validation_errors"] == []


def test_day96_json_and_html_reports_are_generated_without_action_controls(tmp_path):
    report = day96.build_day96_parser_report()
    json_path, html_path = day96.write_day96_parser_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day96_readonly_output_parser_prototype.json"
    assert html_path == tmp_path / "reports/lab-summary/day96_readonly_output_parser_prototype.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day96 Read-only Output Parser Prototype" in html
    assert "No RouterOS, no SSH, no live-read" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day96_runner_task_returns_pass_without_live_access(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day96 parser prototype must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day96 parser prototype must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "readonly-output-parser-prototype"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day96 Read-only Output Parser Prototype" in output
    assert "Task name: readonly-output-parser-prototype" in output
    assert "PASS / PARSER_PROTOTYPE_READY" in output
    assert "live_fallback_attempts = 0" in output
    assert "adapter_fallback_attempts = 0" in output
    assert "device_access_attempts = 0" in output
    assert "live_read_enabled = false" in output
    assert "ssh_enabled = false" in output
    assert "routeros_enabled = false" in output
    assert "device_access_enabled = false" in output
    assert "JSON report: reports/lab-summary/day96_readonly_output_parser_prototype.json" in output
    assert "HTML report: reports/lab-summary/day96_readonly_output_parser_prototype.html" in output
    assert not (tmp_path / "config.json").exists()


def test_day96_report_index_visibility_includes_parser_prototype(tmp_path):
    assert network_lab.main(["--task", "readonly-output-parser-prototype"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Read-only Output Parser Prototype" in html
    assert "parser-only" in html
    assert "reports/lab-summary/day96_readonly_output_parser_prototype.json" in html
    assert "reports/lab-summary/day96_readonly_output_parser_prototype.html" in html
    assert "FAIL" not in html


def test_day96_task_catalog_contains_parser_boundary_metadata():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "readonly-output-parser-prototype"
    )

    assert task["task_id"] == "day96_readonly_output_parser_prototype"
    assert task["day"] == "Day96"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day96_readonly_output_parser_prototype.json" in task["report_paths"]
    assert "docs/ai/readonly_output_parser_prototype.md" in task["report_paths"]
    assert "live_read_enabled remains false" in task["notes"]
    assert "routeros_enabled remains false" in task["notes"]


def test_day96_module_has_no_forbidden_runtime_imports_or_live_io():
    source_path = Path(day96.__file__)
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
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
