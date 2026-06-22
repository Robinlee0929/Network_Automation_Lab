import copy
from pathlib import Path

import network_lab
import phase_2c_04_next_slice_candidate_inventory as phase_2c_04


DOC_PATH = Path("docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_04():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-04 Next-Slice Candidate Inventory" not in agents_text
    assert "phase_2c_04_next_slice_candidate_inventory" not in agents_text


def test_phase_2c_04_markdown_artifact_exists_and_has_required_separation():
    text = _doc_text()

    assert "# Phase 2C-04 Next-Slice Candidate Inventory - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Candidate Inventory",
        "## Neutral Review Fields",
        "## Review Checks",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "CANDIDATE_INVENTORY_ONLY: YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE: NO",
        "CANDIDATE_SELECTED: NO",
        "NEXT_SLICE_AUTHORIZED: NO",
        "PHASE_2C_05_AUTHORIZED: NO",
        "IMPLEMENTATION_ADDED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
    ):
        assert label in text
    assert phase_2c_04.FINAL_VERDICT in text


def test_phase_2c_04_builds_candidate_inventory_only_report():
    report = phase_2c_04.build_phase_2c_04_next_slice_candidate_inventory_report()

    assert report["validation"]["valid"] is True
    assert report["inventory_decision"] == "CANDIDATE_INVENTORY_ONLY"
    assert report["phase_2c_03_input_review"]["observed_verdict"] == (
        "PHASE_2C_03_NEXT_SLICE_PLANNING_ALLOWED_IMPLEMENTATION_LOCKED"
    )
    assert report["phase_2c_03_input_review"]["source_validation"]["valid"] is True
    assert report["candidate_inventory_only"] is True
    assert report["candidate_selected"] is False
    assert report["next_slice_authorized"] is False
    assert report["phase_2c_05_authorized"] is False
    assert report["later_implementation_authorized"] is False
    assert report["implementation_added"] is False


def test_phase_2c_04_candidates_are_broad_neutral_and_unselected():
    report = phase_2c_04.build_phase_2c_04_next_slice_candidate_inventory_report()

    assert report["example_job_types"] == list(phase_2c_04.EXAMPLE_JOB_TYPES)
    assert len(report["candidate_inventory"]) > 1
    assert {candidate["example_job_type"] for candidate in report["candidate_inventory"]} == set(
        phase_2c_04.EXAMPLE_JOB_TYPES
    )
    assert all(candidate["inventory_status"] == "CANDIDATE_ONLY" for candidate in report["candidate_inventory"])
    assert all(candidate["selected"] is False for candidate in report["candidate_inventory"])
    assert "rank" not in report
    assert "selected_candidate" not in report
    assert "next_slice" not in {
        candidate.get("inventory_status", "") for candidate in report["candidate_inventory"]
    }


def test_phase_2c_04_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_04.build_phase_2c_04_next_slice_candidate_inventory_report()

    for flag_name, expected in phase_2c_04.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "candidate_selected",
        "next_slice_authorized",
        "phase_2c_05_authorized",
        "later_implementation_authorized",
        "implementation_added",
        "runtime_implementation_added",
        "execution_opened",
        "provider_api_opened",
        "model_opened",
        "secrets_touched",
        "live_device_touched",
        "ssh_netconf_restconf_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "shell_command_added",
        "custom_script_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "real_device_operation_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_04_rejects_tampered_selection_or_execution_flags():
    report = phase_2c_04.build_phase_2c_04_next_slice_candidate_inventory_report()
    tampered = copy.deepcopy(report)
    tampered["inventory_decision"] = "SELECT_NEXT_SLICE"
    tampered["candidate_selected"] = True
    tampered["next_slice_authorized"] = True
    tampered["phase_2c_05_authorized"] = True
    tampered["implementation_added"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["candidate_inventory"][0]["selected"] = True

    validation = phase_2c_04.validate_phase_2c_04_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "INVENTORY_DECISION_MISMATCH" in validation["errors"]
    assert "CANDIDATE_SELECTED" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:candidate_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_05_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]


def test_cli_writes_phase_2c_04_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-04 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-04 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_04.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-04 Next-Slice Candidate Inventory - Planning Only" in output
    assert "Inventory decision: CANDIDATE_INVENTORY_ONLY" in output
    assert "candidate_count: 7" in output
    assert "candidate_inventory_only: true" in output
    assert "candidate_selected: false" in output
    assert "next_slice_authorized: false" in output
    assert "phase_2c_05_authorized: false" in output
    assert "implementation_added: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_04.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_04.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_04.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_04(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_04.TASK_NAME)

    assert task["task_id"] == "phase_2c_04_next_slice_candidate_inventory"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_04.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_04.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_04.DOC_PATH.as_posix() in task["report_paths"]
    assert "CANDIDATE_INVENTORY_ONLY" in task["notes"]
    assert "CANDIDATE_SELECTED_NO" in task["notes"]
    assert "NEXT_SLICE_AUTHORIZED_NO" in task["notes"]
    assert "PHASE_2C_05_AUTHORIZED_NO" in task["notes"]
    assert "IMPLEMENTATION_ADDED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_04.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-04 Next-Slice Candidate Inventory - Planning Only" in html
    assert "phase_2c_04_next_slice_candidate_inventory.json" in html
