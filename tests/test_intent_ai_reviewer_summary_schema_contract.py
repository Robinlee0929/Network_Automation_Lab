import json
from copy import deepcopy
from pathlib import Path

import pytest

import intent_ai_reviewer_summary_schema_contract as day127
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day127_agents_md_pre_read_evidence_passes():
    report = day127.build_ai_reviewer_summary_schema_contract_report(PROJECT_ROOT)

    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day127_work"] is True
    assert report["agents_md_path"] == "AGENTS.md"


def test_day127_agents_md_missing_fails_without_claiming_pre_read(tmp_path):
    evidence = day127.build_agents_md_pre_read_evidence(tmp_path)

    assert evidence["agents_md_pre_read_result"] == "FAIL"
    assert evidence["agents_md_read_before_day127_work"] is False


def test_day127_example_fixture_matches_generated_contract_and_validates():
    fixture = day127.load_summary_fixture(PROJECT_ROOT)
    generated = day127.build_example_ai_reviewer_summary_fixture()
    validation = day127.validate_ai_reviewer_summary_contract(fixture)

    assert fixture == generated
    assert validation["status"] == "PASS"
    assert validation["errors"] == []
    assert validation["forbidden_future_scope_fields"] == []
    assert fixture["schema_version"] == day127.SCHEMA_VERSION
    assert set(day127.REQUIRED_SUMMARY_FIELDS).issubset(fixture)


def test_day127_rejects_missing_required_summary_field():
    fixture = day127.build_example_ai_reviewer_summary_fixture()
    fixture.pop("reviewer_findings")

    validation = day127.validate_ai_reviewer_summary_contract(fixture)

    assert validation["status"] == "FAIL"
    assert "reviewer_findings is missing." in validation["errors"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("renderer_template", "<section></section>"),
        ("prompt_text", "Summarize this report."),
        ("redaction_policy", {"mode": "future"}),
        ("execution_unlock", True),
    ],
)
def test_day127_rejects_future_scope_fields(field, value):
    fixture = day127.build_example_ai_reviewer_summary_fixture()
    fixture[field] = value

    validation = day127.validate_ai_reviewer_summary_contract(fixture)

    assert validation["status"] == "FAIL"
    assert field in validation["forbidden_future_scope_fields"]


def test_day127_report_shape_and_scope_guards():
    report = day127.build_ai_reviewer_summary_schema_contract_report(PROJECT_ROOT)

    assert report["day"] == 127
    assert report["task"] == "ai-reviewer-summary-schema-contract"
    assert report["overall_status"] == "PASS"
    assert report["schema_contract_status"] == "SCHEMA_CONTRACT_READY"
    assert report["fixture_validation_status"] == "PASS"
    assert report["example_fixture_path"] == "fixtures/day127_ai_reviewer_summary.example.json"
    assert report["validation_errors"] == []
    assert report["renderer_implemented"] is False
    assert report["day128_renderer_implemented"] is False
    assert report["prompt_text_contract_implemented"] is False
    assert report["day129_prompt_contract_implemented"] is False
    assert report["redaction_policy_implemented"] is False
    assert report["day130_redaction_policy_implemented"] is False
    assert report["execution_unlock_added"] is False
    assert report["next_phase_allowed"] is False


def test_day127_safety_invariants_remain_locked():
    report = day127.build_ai_reviewer_summary_schema_contract_report(PROJECT_ROOT)

    assert report["reviewer_only"] is True
    assert report["report_only"] is True
    assert report["live_execution_introduced"] is False
    assert report["ssh_introduced"] is False
    assert report["device_connection_introduced"] is False
    assert report["configuration_change_introduced"] is False
    assert report["openai_or_voice_runtime_introduced"] is False
    assert report["mapped_task_execution_introduced"] is False
    assert report["dashboard_action_endpoint_introduced"] is False
    assert all(value is False for value in report["safety_invariants"].values())
    assert all(value is False for value in report["blocked_capabilities"].values())


def test_day127_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-reviewer-summary-schema-contract"
    )

    assert resolve_task_name("ai-reviewer-summary-schema-contract") == (
        "ai-reviewer-summary-schema-contract"
    )
    assert task["task_id"] == "day127_ai_reviewer_summary_schema_contract"
    assert task["day"] == "Day127"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_reviewer_summary_schema_contract.py"
    assert "fixtures/day127_ai_reviewer_summary.example.json" in task["report_paths"]
    assert "Day128 renderer" in task["notes"]
    assert "Day129 prompt text contract" in task["notes"]
    assert "Day130 redaction policy" in task["notes"]
    assert "execution unlock" in task["notes"]


def test_day127_cli_runs_without_live_paths(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day127 schema contract must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day127 schema contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-reviewer-summary-schema-contract"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-reviewer-summary-schema-contract" in output
    assert "agents_md_pre_read_result: \"PASS\"" in output
    assert "agents_md_read_before_day127_work: true" in output
    assert "schema_contract_status: \"SCHEMA_CONTRACT_READY\"" in output
    assert "fixture_validation_status: \"PASS\"" in output
    assert "renderer_implemented: false" in output
    assert "prompt_text_contract_implemented: false" in output
    assert "redaction_policy_implemented: false" in output
    assert "execution_unlock_added: false" in output
    assert "day128_renderer_implemented: false" in output
    assert "day129_prompt_contract_implemented: false" in output
    assert "day130_redaction_policy_implemented: false" in output
    assert "SCHEMA_CONTRACT_READY" in output


def test_day127_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-reviewer-summary-schema-contract"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-reviewer-summary-schema-contract", handlers)

    assert resolved.canonical_name == "ai-reviewer-summary-schema-contract"
    assert callable(resolved.handler)


def test_day127_report_index_visibility_includes_schema_contract(tmp_path):
    report = day127.build_ai_reviewer_summary_schema_contract_report(PROJECT_ROOT)
    json_path, html_path = day127.write_ai_reviewer_summary_schema_contract_reports(
        tmp_path,
        report,
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day127" in index_html
    assert "AI Reviewer Summary Schema Contract Integration" in index_html


def test_day127_docs_exist_and_preserve_future_day_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day127_ai_reviewer_summary_schema_contract.md",
        PROJECT_ROOT / "docs/roadmap/day127_ai_reviewer_summary_schema_contract.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "AI Reviewer Summary Schema Contract Integration" in text
        assert "Day128" in text
        assert "Day129" in text
        assert "Day130" in text
        assert "not implement" in text.lower() or "does not implement" in text.lower()
        assert "execution unlock" in text.lower()


def test_day127_report_does_not_contain_renderer_prompt_or_redaction_implementation():
    report = day127.build_ai_reviewer_summary_schema_contract_report(PROJECT_ROOT)
    serialized = json.dumps(report, sort_keys=True)

    assert "renderer_template" not in serialized
    assert "rendered_html" not in serialized
    assert "prompt_text\": \"Summarize" not in serialized
    assert "system_prompt" not in serialized
    assert "user_prompt" not in serialized
    assert "redaction_rules" not in serialized
    assert "secret_patterns" not in serialized
    assert "execution_unlock\": true" not in serialized


def test_day127_validation_fails_when_fixture_unlocks_execution():
    fixture = deepcopy(day127.build_example_ai_reviewer_summary_fixture())
    fixture["safety_boundary"]["execution_unlock_added"] = True

    validation = day127.validate_ai_reviewer_summary_contract(fixture)

    assert validation["status"] == "FAIL"
    assert "safety_boundary.execution_unlock_added must be false." in validation["errors"]
