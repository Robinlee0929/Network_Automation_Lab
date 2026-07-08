import copy
from pathlib import Path

import network_lab
import phase_2c_06_next_slice_final_selection_gate as phase_2c_06
import phase_2c_07_next_slice_implementation_kickoff_gate as phase_2c_07
import phase_2c_08_next_slice_implementation as phase_2c_08
import phase_2c_09_post_next_slice_acceptance_review as phase_2c_09
import phase_2c_10_next_slice_decision_gate_authorization_review as phase_2c_10
from report_file_utils import path_exists, read_text_with_long_path, write_text_with_parents


DOC_PATH = Path("docs/phase_2c/phase_2c_10_next_slice_decision_gate_authorization_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _write_placeholder(path: Path) -> None:
    write_text_with_parents(path, f"fixture for {path.as_posix()}\n", encoding="utf-8")


def _materialize_phase_2c_09_acceptance(project_root: Path) -> None:
    for artifact in (
        *phase_2c_06.EXISTING_ARTIFACTS_REFERENCED,
        *phase_2c_07.EXISTING_ARTIFACTS_REFERENCED,
        *phase_2c_08.EXISTING_ARTIFACTS_REFERENCED,
        *phase_2c_09.EXISTING_ARTIFACTS_REVIEWED,
        *phase_2c_10.EXISTING_ARTIFACTS_REVIEWED,
    ):
        path = project_root / artifact
        if not path_exists(path):
            _write_placeholder(path)

    phase_2c_06.write_phase_2c_06_next_slice_final_selection_gate_reports(project_root)
    phase_2c_07.write_phase_2c_07_next_slice_implementation_kickoff_gate_reports(project_root)
    phase_2c_08.write_phase_2c_08_next_slice_implementation_reports(project_root)
    phase_2c_09.write_phase_2c_09_post_next_slice_acceptance_review_reports(project_root)


def test_agents_md_is_not_modified_for_phase_2c_10():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-10 Next-Slice Decision Gate" not in agents_text
    assert "phase_2c_10_next_slice_decision_gate_authorization_review" not in agents_text


def test_phase_2c_10_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-10 Next-Slice Decision Gate / Authorization Review - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts Reviewed",
        "## Implementation Boundary",
        "## Phase 2C-09 Acceptance Status",
        "## Non-Duplication Check Against Phase 2C-03",
        "## Non-Duplication Check Against Day1-Day160",
        "## Decision",
        "## Deferred Work",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "AGENTS.md_FOUND: YES",
        "AGENTS.md_READ_BEFORE_ACTION: YES",
        "AGENTS.md_MODIFIED: NO",
        "SCOPE_CONFIRMATION_WRITTEN: YES",
        "NEEDS_SCOPE_CONFIRMATION: NO",
        "PHASE_2C_09_ACCEPTANCE_CONFIRMED: YES",
        "PHASE_2C_09_DECISION: ACCEPT",
        "ALLOW_NEXT_PLANNING: YES",
        "NEXT_ALLOWED_PHASE: Phase 2C-11 Next-Slice Candidate Inventory - Planning Only",
        "DUPLICATES_PHASE_2C_03: PATTERN_REUSE_ONLY",
        "DUPLICATES_DAY1_DAY160: REFERENCE_ONLY",
        "NEXT_SLICE_CANDIDATES_LISTED: NO",
        "NEXT_SLICE_SELECTED: NO",
        "NEXT_IMPLEMENTATION_AUTHORIZED: NO",
        "NEXT_IMPLEMENTATION_STARTED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO",
        "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_10.EXAMPLE_JOB_TYPES_SECTION in text
    assert phase_2c_10.NON_DUPLICATION_PHASE_2C_03 in text
    assert phase_2c_10.NON_DUPLICATION_DAY1_DAY160 in text
    assert phase_2c_10.FINAL_VERDICT in text


def test_phase_2c_10_allows_next_planning_only_after_phase_2c_09_acceptance():
    report = phase_2c_10.build_phase_2c_10_next_slice_decision_gate_authorization_review_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["phase_2c_09_acceptance_confirmed"] is True
    assert report["phase_2c_09_decision"] == "ACCEPT"
    assert report["authorization_decision"] == "ALLOW_NEXT_PLANNING_ONLY"
    assert report["allow_next_planning"] is True
    assert report["next_allowed_phase"] == phase_2c_10.NEXT_ALLOWED_PHASE
    assert report["final_verdict"] == phase_2c_10.FINAL_VERDICT


def test_phase_2c_10_blocks_when_phase_2c_09_acceptance_is_missing(tmp_path):
    report = phase_2c_10.build_phase_2c_10_next_slice_decision_gate_authorization_review_report(tmp_path)

    assert report["status"] == "FAIL"
    assert report["validation"]["valid"] is False
    assert phase_2c_10.BLOCKED_VERDICT in report["validation"]["errors"]
    assert report["phase_2c_09_acceptance_confirmed"] is False
    assert report["phase_2c_09_decision"] == "NOT_FOUND"
    assert report["allow_next_planning"] is False
    assert report["next_allowed_phase"] == "NONE"


def test_phase_2c_10_does_not_list_select_or_authorize_candidates():
    report = phase_2c_10.build_phase_2c_10_next_slice_decision_gate_authorization_review_report(Path.cwd())

    assert report["candidate_inventory"] == []
    assert report["example_job_types_section"] == phase_2c_10.EXAMPLE_JOB_TYPES_SECTION
    assert report["candidate_inventory_deferred_to"] == phase_2c_10.NEXT_ALLOWED_PHASE
    assert report["next_slice_candidates_listed"] is False
    assert report["next_slice_selected"] is False
    assert report["next_implementation_authorized"] is False
    assert report["next_implementation_started"] is False


def test_phase_2c_10_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_10.build_phase_2c_10_next_slice_decision_gate_authorization_review_report(Path.cwd())

    for flag_name, expected in phase_2c_10.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "phase_2c_11_started",
        "next_slice_candidates_listed",
        "next_slice_selected",
        "next_implementation_authorized",
        "next_implementation_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_10_rejects_tampered_candidate_or_execution_flags():
    report = phase_2c_10.build_phase_2c_10_next_slice_decision_gate_authorization_review_report(Path.cwd())
    tampered = copy.deepcopy(report)
    tampered["candidate_inventory"] = [{"candidate_id": "candidate-01"}]
    tampered["next_slice_candidates_listed"] = True
    tampered["next_slice_selected"] = True
    tampered["next_implementation_authorized"] = True
    tampered["next_implementation_started"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["broker_added"] = True
    tampered["scheduler_added"] = True
    tampered["queue_added"] = True
    tampered["worker_added"] = True
    tampered["agent_loop_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["config_backup_or_change_behavior_added"] = True
    tampered["day1_day160_rewritten_or_replaced"] = True
    tampered["second_safety_matrix_created"] = True

    validation = phase_2c_10.validate_phase_2c_10_report(tampered)

    assert validation["valid"] is False
    assert "CANDIDATE_INVENTORY_NOT_EMPTY" in validation["errors"]
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_candidates_listed" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:agent_loop_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_10_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_phase_2c_09_acceptance(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-10 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-10 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_10.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-10 Next-Slice Decision Gate / Authorization Review - Planning Only" in output
    assert "phase_2c_09_acceptance_confirmed: true" in output
    assert "phase_2c_09_decision: ACCEPT" in output
    assert "allow_next_planning: YES" in output
    assert f"next_allowed_phase: {phase_2c_10.NEXT_ALLOWED_PHASE}" in output
    assert "duplicates_phase_2c_03: PATTERN_REUSE_ONLY" in output
    assert "duplicates_day1_day160: REFERENCE_ONLY" in output
    assert "next_slice_candidates_listed: false" in output
    assert "next_slice_selected: false" in output
    assert "next_implementation_authorized: false" in output
    assert "next_implementation_started: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "scheduler_queue_broker_worker_agent_loop_added: false" in output
    assert "live_device_ssh_netconf_restconf_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "config_backup_or_change_behavior_added: false" in output
    assert f"[PASS] {phase_2c_10.FINAL_VERDICT}" in output
    assert path_exists(tmp_path / phase_2c_10.REPORT_JSON)
    assert path_exists(tmp_path / phase_2c_10.REPORT_HTML)


def test_task_catalog_and_report_index_visibility_for_phase_2c_10(tmp_path):
    _materialize_phase_2c_09_acceptance(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_10.TASK_NAME)

    assert task["task_id"] == "phase_2c_10_next_slice_decision_gate_authorization_review"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_10.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_10.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_10.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2C_09_ACCEPTANCE_CONFIRMED_YES" in task["notes"]
    assert "ALLOW_NEXT_PLANNING_YES" in task["notes"]
    assert "NEXT_SLICE_CANDIDATES_LISTED_NO" in task["notes"]
    assert "NEXT_SLICE_SELECTED_NO" in task["notes"]
    assert "NEXT_IMPLEMENTATION_AUTHORIZED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_10.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Phase 2C-10 Next-Slice Decision Gate / Authorization Review - Planning Only" in html
    assert "phase_2c_10_next_slice_decision_gate_authorization_review.json" in html
