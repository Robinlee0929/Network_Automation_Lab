import copy
from pathlib import Path

import network_lab
import phase_2c_02_post_first_slice_acceptance_review as phase_2c_02


DOC_PATH = Path("docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_02():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-02 Post-First-Slice Acceptance Review" not in agents_text
    assert "phase_2c_02_post_first_slice_acceptance_review" not in agents_text


def test_phase_2c_02_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-02 Post-First-Slice Acceptance Review" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Acceptance Scope",
        "## Acceptance Criteria",
        "## Existing Artifacts Reviewed",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    assert phase_2c_02.FINAL_VERDICT in text
    assert "NEXT_SLICE_AUTHORIZED: NO" in text


def test_phase_2c_02_accepts_phase_2c_01_without_rerun_or_regeneration():
    report = phase_2c_02.build_phase_2c_02_post_first_slice_acceptance_review_report()

    assert report["validation"]["valid"] is True
    assert report["acceptance_decision"] == "ACCEPT"
    assert report["phase_2c_01_accepted"] is True
    assert report["phase_2c_01_verdict_referenced"] is True
    assert report["phase_2c_01_validation_passed"] is True
    assert report["source_task_rerun"] is False
    assert report["source_report_regenerated"] is False
    assert report["first_slice_implementation_modified"] is False
    assert report["source_first_slice_review"]["observed_verdict"] == "PHASE_2C_01_LOCAL_STATIC_JOB_FIRST_SLICE_DONE"
    assert report["source_first_slice_review"]["source_validation"]["valid"] is True


def test_phase_2c_02_acceptance_checks_are_pass_only_and_next_slice_locked():
    report = phase_2c_02.build_phase_2c_02_post_first_slice_acceptance_review_report()

    assert tuple(report["acceptance_checks"]) == phase_2c_02.ACCEPTANCE_CHECKS
    assert all(check["status"] == "PASS" for check in report["acceptance_checks"])
    assert report["next_slice_authorized"] is False
    assert report["next_day_feature_added"] is False
    assert "NEXT_SLICE_AUTHORIZED_NO" in report["completion_markers"]


def test_phase_2c_02_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_02.build_phase_2c_02_post_first_slice_acceptance_review_report()

    for flag_name, expected in phase_2c_02.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "source_task_rerun",
        "source_report_regenerated",
        "first_slice_implementation_modified",
        "next_slice_authorized",
        "next_day_feature_added",
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


def test_phase_2c_02_rejects_tampered_acceptance_or_execution_flags():
    report = phase_2c_02.build_phase_2c_02_post_first_slice_acceptance_review_report()
    tampered = copy.deepcopy(report)
    tampered["acceptance_decision"] = "BLOCKED"
    tampered["source_task_rerun"] = True
    tampered["source_report_regenerated"] = True
    tampered["first_slice_implementation_modified"] = True
    tampered["next_slice_authorized"] = True
    tampered["execution_opened"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["live_device_touched"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["source_first_slice_review"]["observed_verdict"] = "TAMPERED"

    validation = phase_2c_02.validate_phase_2c_02_report(tampered)

    assert validation["valid"] is False
    assert "PHASE_2C_02_ACCEPTANCE_BLOCKED" in validation["errors"]
    assert "ACCEPTANCE_DECISION_NOT_ACCEPT" in validation["errors"]
    assert "SOURCE_VERDICT_MISMATCH" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:source_task_rerun" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:provider_api_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:model_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:live_device_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_netconf_restconf_touched" in validation["errors"]


def test_cli_writes_phase_2c_02_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-02 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-02 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_02.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-02 Post-First-Slice Acceptance Review" in output
    assert "Acceptance decision: ACCEPT" in output
    assert "phase_2c_01_accepted: true" in output
    assert "phase_2c_01_validation_passed: true" in output
    assert "source_task_rerun: false" in output
    assert "source_report_regenerated: false" in output
    assert "first_slice_implementation_modified: false" in output
    assert "next_slice_authorized: false" in output
    assert "execution_opened: false" in output
    assert "provider_api_opened: false" in output
    assert "model_opened: false" in output
    assert "secrets_touched: false" in output
    assert "live_device_touched: false" in output
    assert "ssh_netconf_restconf_touched: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert f"[PASS] {phase_2c_02.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_02.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_02.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_02(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_02.TASK_NAME)

    assert task["task_id"] == "phase_2c_02_post_first_slice_acceptance_review"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_02.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_02.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_02.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2C_01_ACCEPTED_YES" in task["notes"]
    assert "SOURCE_TASK_RERUN_NO" in task["notes"]
    assert "NEXT_SLICE_AUTHORIZED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_02.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-02 Post-First-Slice Acceptance Review" in html
    assert "phase_2c_02_post_first_slice_acceptance_review.json" in html
