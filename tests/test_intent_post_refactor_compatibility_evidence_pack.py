import json
from pathlib import Path

import pytest

import intent_post_refactor_compatibility_evidence_pack as day126
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day126_agents_md_pre_read_evidence_passes():
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)

    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_read_before_day126_work"] is True
    assert report["agents_md_path"] == "AGENTS.md"


def test_day126_agents_md_missing_fails_without_claiming_pre_read(tmp_path):
    evidence = day126.build_agents_md_pre_read_evidence(tmp_path)

    assert evidence["agents_md_pre_read_result"] == "FAIL"
    assert evidence["agents_md_read_before_day126_work"] is False


def test_day126_report_shape_and_compatibility_records():
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)

    assert report["day"] == 126
    assert report["task"] == "post-refactor-compatibility-evidence-pack"
    assert report["overall_status"] == "PASS"
    assert report["compatibility_pack_status"] == "COMPATIBILITY_EVIDENCE_READY"
    assert report["post_refactor_scope"] == "DAY120_DAY125"
    assert [record["record_id"] for record in report["compatibility_records"]] == list(
        day126.COMPATIBILITY_RECORD_IDS
    )
    assert report["compatibility_record_count"] == 6
    assert report["compatible_record_count"] == 6
    assert report["regression_detected_count"] == 0
    assert all(record["compatibility_status"] == "COMPATIBLE" for record in report["compatibility_records"])
    assert all(record["execution_boundary_preserved"] is True for record in report["compatibility_records"])
    assert all(record["reviewer_boundary_preserved"] is True for record in report["compatibility_records"])
    assert all(record["regression_detected"] is False for record in report["compatibility_records"])
    assert report["validation_errors"] == []


def test_day126_thin_cli_snapshot_only_and_no_budget_gate():
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)
    thin_cli_records = [
        record
        for record in report["compatibility_records"]
        if record["record_id"] == "DAY125_THIN_CLI_REGRESSION_GATE_SNAPSHOT"
    ]

    assert len(thin_cli_records) == 1
    assert report["thin_cli_snapshot_included"] is True
    assert report["thin_cli_snapshot_count"] == 1
    assert report["thin_cli_budget_gate_added"] is False
    assert report["thin_cli_budget_enforcement_added"] is False
    assert report["long_term_numeric_budget_enforcement_added"] is False
    assert report["budget_blocking_policy_added"] is False
    assert report["numeric_budget_thresholds"] == []
    assert thin_cli_records[0]["evidence_type"] == "single snapshot evidence item"
    assert thin_cli_records[0]["details"]["snapshot_count"] == 1
    assert thin_cli_records[0]["details"]["numeric_budget_thresholds"] == []


def test_day126_safety_invariants_remain_locked():
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)

    assert report["reviewer_only"] is True
    assert report["report_only"] is True
    assert report["live_execution_introduced"] is False
    assert report["ssh_introduced"] is False
    assert report["device_connection_introduced"] is False
    assert report["configuration_change_introduced"] is False
    assert report["openai_or_voice_runtime_introduced"] is False
    assert report["mapped_task_execution_introduced"] is False
    assert report["dashboard_action_endpoint_introduced"] is False
    assert report["execution_unlock_introduced"] is False
    assert report["next_phase_allowed"] is False
    assert all(value is False for value in report["safety_invariants"].values())
    assert all(value is False for value in report["blocked_capabilities"].values())


def test_day126_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "post-refactor-compatibility-evidence-pack"
    )

    assert resolve_task_name("post-refactor-compatibility-evidence-pack") == (
        "post-refactor-compatibility-evidence-pack"
    )
    assert task["task_id"] == "day126_post_refactor_compatibility_evidence_pack"
    assert task["day"] == "Day126"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "intent_post_refactor_compatibility_evidence_pack.py" == task["related_script"]
    assert "budget gate" in task["notes"]
    assert "does not add" in task["notes"]


def test_day126_cli_runs_without_live_paths(tmp_path, monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day126 compatibility pack must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day126 compatibility pack must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "post-refactor-compatibility-evidence-pack"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: post-refactor-compatibility-evidence-pack" in output
    assert "agents_md_pre_read_result: \"PASS\"" in output
    assert "agents_md_read_before_day126_work: true" in output
    assert "compatibility_pack_status: \"COMPATIBILITY_EVIDENCE_READY\"" in output
    assert "thin_cli_snapshot_included: true" in output
    assert "thin_cli_snapshot_count: 1" in output
    assert "thin_cli_budget_gate_added: false" in output
    assert "thin_cli_budget_enforcement_added: false" in output
    assert "long_term_numeric_budget_enforcement_added: false" in output
    assert "numeric_budget_thresholds: []" in output
    assert "live_execution_introduced: false" in output
    assert "ssh_introduced: false" in output
    assert "openai_or_voice_runtime_introduced: false" in output
    assert "mapped_task_execution_introduced: false" in output
    assert "next_phase_allowed: false" in output
    assert "COMPATIBILITY_EVIDENCE_READY" in output


def test_day126_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "post-refactor-compatibility-evidence-pack"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("post-refactor-compatibility-evidence-pack", handlers)

    assert resolved.canonical_name == "post-refactor-compatibility-evidence-pack"
    assert callable(resolved.handler)


def test_day126_report_index_visibility_includes_compatibility_pack(tmp_path):
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)
    json_path, html_path = day126.write_post_refactor_compatibility_evidence_pack_reports(
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
    assert "Day126" in index_html
    assert "Post-Refactor Compatibility Evidence Pack" in index_html


def test_day126_docs_exist_and_reject_budget_gate():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day126_post_refactor_compatibility_evidence_pack.md",
        PROJECT_ROOT / "docs/roadmap/day126_post_refactor_compatibility_evidence_pack.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "Post-Refactor Compatibility Evidence Pack" in text
        assert "Thin CLI Responsibility Budget Gate" in text
        assert "Do not adopt" in text or "does not adopt" in text
        assert "snapshot" in text.lower()
        assert "numeric" in text.lower()
        assert "must not add" in text.lower() or "does not add" in text.lower()


@pytest.mark.parametrize("marker", day126.FORBIDDEN_BUDGET_MARKERS)
def test_day126_no_budget_threshold_markers_in_report(marker):
    report = day126.build_post_refactor_compatibility_evidence_pack(PROJECT_ROOT)

    assert marker not in json.dumps(report, sort_keys=True)
