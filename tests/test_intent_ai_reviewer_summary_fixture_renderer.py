import json
from pathlib import Path

import pytest

import intent_ai_reviewer_summary_fixture_renderer as day128
import intent_ai_reviewer_summary_schema_contract as day127
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day128_agents_md_pre_read_evidence_is_found_and_read():
    evidence = day128.build_agents_md_pre_read_evidence(PROJECT_ROOT)

    assert evidence["agents_md_pre_read_result"] == "FOUND_AND_READ"
    assert evidence["agents_md_read_before_code_changes"] is True


def test_day128_renderer_uses_day127_schema_fixture():
    fixture = day127.load_summary_fixture(PROJECT_ROOT)
    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["schema_source"].endswith(day127.SCHEMA_VERSION)
    assert report["fixture_source"] == day127.FIXTURE_PATH.as_posix()
    assert report["reused_day127_schema_fixture"] is True
    assert report["fixture_summary"]["summary_id"] == fixture["summary_id"]
    assert fixture["summary_id"] in report["rendered_text"]


def test_day128_renderer_output_is_deterministic():
    fixture = day127.load_summary_fixture(PROJECT_ROOT)

    assert day128.render_day127_summary_fixture(fixture) == day128.render_day127_summary_fixture(fixture)
    assert (
        day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)["rendered_text"]
        == day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)["rendered_text"]
    )


def test_day128_renderer_does_not_redefine_schema():
    assert not hasattr(day128, "REQUIRED_SUMMARY_FIELDS")
    assert not hasattr(day128, "REQUIRED_REPORT_FIELDS")
    assert not hasattr(day128, "SUMMARY_STATUSES")
    assert not hasattr(day128, "FINDING_SEVERITIES")

    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)
    assert report["redefined_schema"] is False


def test_day128_boundary_flags_remain_false():
    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)

    assert report["fixture_renderer_only"] is True
    assert report["report_only"] is True
    assert report["fixture_only"] is True
    assert report["non_executable"] is True
    for field in (
        "ai_decision_performed",
        "prompt_contract_defined",
        "redaction_policy_defined",
        "openai_api_called",
        "execution_unlock_added",
        "provider_enabled",
        "api_enabled",
        "next_day_feature_included",
        "next_phase_allowed",
    ):
        assert report[field] is False


def test_day128_report_serialization_has_no_enabled_api_provider_or_execution_unlock():
    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)
    serialized = json.dumps(report, sort_keys=True)

    assert '"openai_api_called": true' not in serialized
    assert '"provider_enabled": true' not in serialized
    assert '"api_enabled": true' not in serialized
    assert '"execution_unlock_added": true' not in serialized
    assert '"ai_decision_performed": true' not in serialized
    assert '"prompt_contract_defined": true' not in serialized
    assert '"redaction_policy_defined": true' not in serialized


def test_day128_missing_day127_fixture_blocks_without_fabricating_schema(tmp_path):
    (tmp_path / "AGENTS.md").write_text((PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8"), encoding="utf-8")

    report = day128.build_ai_reviewer_summary_fixture_renderer_report(tmp_path)

    assert report["overall_status"] == "BLOCKED"
    assert report["renderer_status"] == "DAY127_SCHEMA_FIXTURE_NOT_FOUND"
    assert report["reused_day127_schema_fixture"] is False
    assert report["redefined_schema"] is False


def test_day128_write_reports_are_stable_and_reviewable(tmp_path):
    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)
    json_path, html_path, text_path = day128.write_ai_reviewer_summary_fixture_renderer_reports(
        tmp_path,
        report,
    )

    written = json.loads(json_path.read_text(encoding="utf-8"))
    text = text_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")

    assert written["overall_status"] == "PASS"
    assert text == report["rendered_text"]
    assert "Day128 AI Reviewer Summary Fixture Renderer" in text
    assert "Fixture Renderer" in html


def test_day128_cli_runs_without_live_paths(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day128 fixture renderer must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day128 fixture renderer must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-reviewer-summary-fixture-renderer"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-reviewer-summary-fixture-renderer" in output
    assert 'agents_md_pre_read_result: "FOUND_AND_READ"' in output
    assert "ai_decision_performed: false" in output
    assert "prompt_contract_defined: false" in output
    assert "redaction_policy_defined: false" in output
    assert "openai_api_called: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "execution_unlock_added: false" in output
    assert "next_phase_allowed: false" in output
    assert "FIXTURE_RENDERED" in output


def test_day128_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-reviewer-summary-fixture-renderer"
    )

    assert resolve_task_name("ai-reviewer-summary-fixture-renderer") == (
        "ai-reviewer-summary-fixture-renderer"
    )
    assert task["task_id"] == "day128_ai_reviewer_summary_fixture_renderer"
    assert task["day"] == "Day128"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_reviewer_summary_fixture_renderer.py"
    assert "fixtures/day127_ai_reviewer_summary.example.json" in task["report_paths"]
    assert "does not redefine schema" in task["notes"]
    assert "OpenAI API" in task["notes"]
    assert "execution unlock" in task["notes"]


def test_day128_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-reviewer-summary-fixture-renderer"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-reviewer-summary-fixture-renderer", handlers)

    assert resolved.canonical_name == "ai-reviewer-summary-fixture-renderer"
    assert callable(resolved.handler)


def test_day128_report_index_visibility_includes_fixture_renderer(tmp_path):
    report = day128.build_ai_reviewer_summary_fixture_renderer_report(PROJECT_ROOT)
    json_path, html_path, _ = day128.write_ai_reviewer_summary_fixture_renderer_reports(
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
    assert "Day128" in index_html
    assert "AI Reviewer Summary Fixture Renderer" in index_html


def test_day128_docs_exist_and_preserve_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day128_ai_reviewer_summary_fixture_renderer.md",
        PROJECT_ROOT / "docs/roadmap/day128_ai_reviewer_summary_fixture_renderer.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "fixture renderer only" in text.lower()
        assert "not next-day" in text.lower() or "not a next-day" in text.lower()
        assert "does not open execution" in text.lower()
        assert "does not make an ai decision" in text.lower()
        assert "does not define a prompt contract" in text.lower()
        assert "does not define redaction policy" in text.lower()
        assert "does not call openai api" in text.lower()
        assert "does not add execution unlock" in text.lower()
