import copy
import json
from pathlib import Path

import day142_ai_summary_to_dry_run_draft_display_contract as day142
import intent_dry_run_draft_safety_diff_viewer as day143
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def safe_payload():
    return {
        "payload_id": "safe-display-payload",
        "payload_kind": "dry_run_draft_display_payload",
        "review_only": True,
        "display_only": True,
        "dry_run_only": True,
        "draft_title": "Safe payload",
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "openai_api_called": False,
        "live_device_enabled": False,
        "ssh_enabled": False,
        "draft_applied": False,
        "draft_saved": False,
        "side_effect_allowed": False,
        "secrets_present": False,
        "next_phase_allowed": False,
    }


def test_identical_safe_payloads_produce_no_safety_regression():
    payload = safe_payload()
    result = day143.compare_dry_run_draft_display_payloads(payload, copy.deepcopy(payload))

    assert result["safety_regressions_detected"] == 0
    assert result["unsafe_transitions_blocked"] == 0
    assert result["final_display_only_verdict"] == "DISPLAY_ONLY_DIFF_ACCEPTED"
    assert set(result["unchanged_safety_flags"]) == set(day143.SAFETY_SENSITIVE_FIELDS)


def test_added_display_only_metadata_is_informational_only():
    baseline = safe_payload()
    candidate = copy.deepcopy(baseline)
    candidate["reviewer_display_metadata"] = {"source": "fixture", "note_count": 1}

    result = day143.compare_dry_run_draft_display_payloads(baseline, candidate)
    added_rows = [row for row in result["diff_rows"] if row["change_type"] == "added"]

    assert result["safety_regressions_detected"] == 0
    assert result["unsafe_transitions_blocked"] == 0
    assert {row["classification"] for row in added_rows} == {"INFORMATIONAL_DISPLAY_DIFF"}
    assert all(row["blocker"] is False for row in added_rows)


def test_removed_safety_sensitive_field_is_review_required_blocker():
    baseline = safe_payload()
    candidate = copy.deepcopy(baseline)
    candidate.pop("execution_enabled")

    result = day143.compare_dry_run_draft_display_payloads(baseline, candidate)
    row = next(row for row in result["diff_rows"] if row["path"] == "execution_enabled")

    assert row["change_type"] == "removed"
    assert row["classification"] == "SAFETY_FIELD_MISSING"
    assert row["review_required"] is True
    assert row["blocker"] is True
    assert result["safety_regressions_detected"] == 1


def test_false_to_true_execution_enabled_is_blocker():
    assert_false_to_true_blocker("execution_enabled")


def test_false_to_true_provider_enabled_is_blocker():
    assert_false_to_true_blocker("provider_enabled")


def test_false_to_true_api_enabled_is_blocker():
    assert_false_to_true_blocker("api_enabled")


def test_false_to_true_openai_api_called_is_blocker():
    assert_false_to_true_blocker("openai_api_called")


def test_false_to_true_next_phase_allowed_is_blocker():
    assert_false_to_true_blocker("next_phase_allowed")


def assert_false_to_true_blocker(field):
    baseline = safe_payload()
    candidate = copy.deepcopy(baseline)
    candidate[field] = True

    result = day143.compare_dry_run_draft_display_payloads(baseline, candidate)
    row = next(row for row in result["diff_rows"] if row["path"] == field)

    assert row["classification"] == "UNSAFE_TRANSITION_BLOCKED"
    assert row["blocker"] is True
    assert row["review_required"] is True
    assert result["unsafe_transitions_blocked"] == 1


def test_inputs_are_not_mutated():
    baseline = safe_payload()
    candidate = copy.deepcopy(baseline)
    candidate["draft_title"] = "Candidate title"
    baseline_before = copy.deepcopy(baseline)
    candidate_before = copy.deepcopy(candidate)

    day143.compare_dry_run_draft_display_payloads(baseline, candidate)

    assert baseline == baseline_before
    assert candidate == candidate_before


def test_day143_does_not_call_or_rebuild_day142_summary_to_draft_logic(monkeypatch, capsys):
    def fail_day142_builder(*args, **kwargs):
        raise AssertionError("Day143 must not call Day142 summary-to-draft contract logic")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day143 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day143 must not load runner profile or config data")

    monkeypatch.setattr(day142, "build_dry_run_draft_display_payload", fail_day142_builder)
    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "dry-run-draft-safety-diff-viewer"], project_root=PROJECT_ROOT)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day143 task: dry-run-draft-safety-diff-viewer" in output
    assert "result: SAFETY_DIFF_VIEW_READY" in output
    assert "not_next_day_feature=true" in output
    assert "not_day144=true" in output
    assert "not_day142_redo=true" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "openai_api_called: false" in output
    assert "live_device_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "draft_applied: false" in output
    assert "draft_saved: false" in output
    assert "next_phase_allowed: false" in output


def test_report_preserves_not_next_day_not_day144_not_day142_flags_and_disabled_runtime_flags():
    report = day143.build_dry_run_draft_safety_diff_viewer_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "SAFETY_DIFF_VIEW_READY"
    assert report["not_next_day_feature"] is True
    assert report["not_day144"] is True
    assert report["not_day142_redo"] is True
    for field in day143.REQUIRED_FALSE_FIELDS:
        assert report[field] is False
    assert report["provider_runtime_invoked"] is False
    assert report["api_runtime_invoked"] is False
    assert report["day142_summary_to_draft_builder_called"] is False
    assert report["draft_persisted"] is False
    assert report["validation_errors"] == []


def test_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == "dry-run-draft-safety-diff-viewer")
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "dry-run-draft-safety-diff-viewer"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("dry-run-draft-safety-diff-viewer", handlers)

    assert resolve_task_name("dry-run-draft-safety-diff-viewer") == "dry-run-draft-safety-diff-viewer"
    assert resolved.canonical_name == "dry-run-draft-safety-diff-viewer"
    assert callable(resolved.handler)
    assert task["task_id"] == "day143_dry_run_draft_safety_diff_viewer"
    assert task["day"] == "Day143"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_dry_run_draft_safety_diff_viewer.py"
    assert "not_day142_redo=true" in task["notes"]
    assert "not_day144=true" in task["notes"]

    report = day143.build_dry_run_draft_safety_diff_viewer_report(PROJECT_ROOT)
    json_path, html_path = day143.write_dry_run_draft_safety_diff_viewer_reports(tmp_path, report)
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "SAFETY_DIFF_VIEW_READY"
    assert "Day143" in index_html
    assert "Dry-run Draft Safety Diff Viewer" in index_html
    assert "reports/lab-summary/day143_dry_run_draft_safety_diff_viewer.json" in index_html


def test_day143_module_does_not_import_network_provider_api_execution_or_day142_surfaces():
    source = Path(day143.__file__).read_text(encoding="utf-8").lower()

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
        "import day142",
        "day142_ai_summary_to_dry_run_draft_display_contract",
        "build_dry_run_draft_display_payload",
        "build_day142_ai_summary_to_dry_run_draft_display_contract",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day143_docs_preserve_required_boundary_statements():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day143_dry_run_draft_safety_diff_viewer.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day143_dry_run_draft_safety_diff_viewer.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "not_next_day_feature=true" in doc
        assert "not_day144=true" in doc
        assert "not_day142_redo=true" in doc
        assert "execution_enabled: false" in doc
        assert "provider_enabled: false" in doc
        assert "api_enabled: false" in doc
        assert "openai_api_called: false" in doc
        assert "live_device_enabled: false" in doc
        assert "ssh_enabled: false" in doc
        assert "draft_applied: false" in doc
        assert "draft_saved: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "Day143 compares two existing dry-run draft display payloads." in doc
