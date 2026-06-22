import copy
import json
from pathlib import Path

import network_lab
import phase_2c_08_next_slice_implementation as phase_2c_08


DOC_PATH = Path("docs/phase_2c/phase_2c_08_next_slice_implementation.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _materialize_required_artifacts(project_root: Path) -> None:
    for path_text in phase_2c_08.EXISTING_ARTIFACTS_REFERENCED:
        path = project_root / path_text
        path.parent.mkdir(parents=True, exist_ok=True)
        if path_text == phase_2c_08.PHASE_2C_06_REPORT_JSON.as_posix():
            path.write_text(
                json.dumps(
                    {
                        "selected_next_slice": "artifact_validation_job",
                        "next_slice_authorized": False,
                        "phase_2c_08_started": False,
                        "implementation_added": False,
                        "final_verdict": "PHASE_2C_06_FINAL_SELECTION_GATE_DONE_IMPLEMENTATION_LOCKED",
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        elif path_text == phase_2c_08.PHASE_2C_07_REPORT_JSON.as_posix():
            path.write_text(
                json.dumps(
                    {
                        "selected_next_slice": "artifact_validation_job",
                        "selected_next_slice_authorized_for_phase_2c_08": True,
                        "phase_2c_08_started": False,
                        "implementation_added": False,
                        "artifact_validation_job_implemented": False,
                        "final_verdict": "PHASE_2C_07_AUTHORIZATION_GATE_DONE_PHASE_2C_08_AUTHORIZED_NOT_STARTED",
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        else:
            path.write_text(f"fixture for {path_text}\n", encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_08():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-08 Next-Slice Implementation" not in agents_text
    assert "phase_2c_08_next_slice_implementation" not in agents_text


def test_phase_2c_08_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-08 Next-Slice Implementation" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Selected Next Slice",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Validation Method",
        "## Report-Only / Dry-Run / Mock-Only Behavior",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "SCOPE_CONFIRMATION_WRITTEN: YES",
        "PHASE_NAME_USED: Phase 2C-08 Next-Slice Implementation",
        "SELECTED_NEXT_SLICE: artifact_validation_job",
        "PHASE_GOAL_CONFIRMED: YES",
        "PHASE_2C_06_SELECTION_CONFIRMED: YES",
        "PHASE_2C_07_AUTHORIZATION_CONFIRMED: YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE: NO",
        "NEEDS_SCOPE_CONFIRMATION: NO",
        "ARTIFACT_VALIDATION_JOB_IMPLEMENTED: YES",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "REPORT_ONLY_DRY_RUN_MOCK_ONLY: YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_OR_CHANGE_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_08.FINAL_VERDICT in text


def test_artifact_validation_job_definition_is_local_deterministic_report_only():
    first = phase_2c_08.build_artifact_validation_job_definition()
    second = phase_2c_08.build_artifact_validation_job_definition()

    assert first == second
    assert first["job_kind"] == "artifact_validation_job"
    assert first["local_only"] is True
    assert first["deterministic"] is True
    assert first["report_only"] is True
    assert first["dry_run_only"] is True
    assert first["mock_only"] is True
    assert first["validates_existing_local_artifacts_only"] is True
    assert first["requires_live_device"] is False
    assert first["requires_network"] is False
    assert first["requires_provider"] is False
    assert first["requires_api"] is False
    assert first["requires_model"] is False
    assert first["requires_secrets"] is False
    assert phase_2c_08.validate_artifact_validation_job_definition(first)["valid"] is True


def test_artifact_validation_job_does_not_populate_execution_or_external_fields():
    job = phase_2c_08.build_artifact_validation_job_definition()

    for field_name in phase_2c_08.NON_EXECUTABLE_FIELDS:
        assert job[field_name] is None
    assert all(value is False for value in job["non_execution_proof"].values())


def test_phase_2c_08_report_validates_local_repository_artifacts_only():
    report = phase_2c_08.build_phase_2c_08_next_slice_implementation_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["selected_next_slice"] == "artifact_validation_job"
    assert report["phase_2c_06_selection_confirmed"] is True
    assert report["phase_2c_07_authorization_confirmed"] is True
    assert report["artifact_validation_job_implemented"] is True
    assert report["local_only"] is True
    assert report["deterministic"] is True
    assert report["report_only"] is True
    assert report["dry_run_only"] is True
    assert report["mock_only"] is True
    assert report["validates_existing_local_artifacts_only"] is True
    assert all(item["exists"] is True for item in report["artifact_records"])
    assert all(item["external_access_required"] is False for item in report["artifact_records"])
    assert all(item["status"] == "PASS" for item in report["artifact_validation_checks"])


def test_phase_2c_08_report_output_is_deterministic():
    first = phase_2c_08.build_phase_2c_08_next_slice_implementation_report(Path.cwd())
    second = phase_2c_08.build_phase_2c_08_next_slice_implementation_report(Path.cwd())

    assert first == second


def test_phase_2c_08_no_forbidden_scope_flags_are_added():
    report = phase_2c_08.build_phase_2c_08_next_slice_implementation_report(Path.cwd())

    for flag_name, expected in phase_2c_08.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
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
        "config_backup_or_change_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "external_network_access_added",
        "non_deterministic_behavior_added",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_08_rejects_tampered_execution_and_scope_flags():
    report = phase_2c_08.build_phase_2c_08_next_slice_implementation_report(Path.cwd())
    tampered = copy.deepcopy(report)
    tampered["scope_narrowed_to_one_example"] = True
    tampered["needs_scope_confirmation"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["worker_added"] = True
    tampered["agent_loop_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["real_command_execution_added"] = True
    tampered["config_backup_or_change_added"] = True
    tampered["day1_day160_rewritten_or_replaced"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["artifact_validation_job"]["shell_command"] = "echo unsafe"
    tampered["artifact_validation_checks"][0]["status"] = "FAIL"

    validation = phase_2c_08.validate_phase_2c_08_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "ARTIFACT_VALIDATION_CHECK_FAILED" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:worker_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:agent_loop_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]
    assert "ARTIFACT_VALIDATION_JOB:NON_EXECUTABLE_FIELD_POPULATED:shell_command" in validation["errors"]


def test_cli_writes_phase_2c_08_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_required_artifacts(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-08 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-08 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_08.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-08 Next-Slice Implementation" in output
    assert "selected_next_slice: artifact_validation_job" in output
    assert "phase_goal_confirmed: true" in output
    assert "phase_2c_06_selection_confirmed: true" in output
    assert "phase_2c_07_authorization_confirmed: true" in output
    assert "scope_narrowed_to_one_example: false" in output
    assert "needs_scope_confirmation: false" in output
    assert "artifact_validation_job_implemented: true" in output
    assert "local_only: true" in output
    assert "deterministic: true" in output
    assert "report_only_dry_run_mock_only: true" in output
    assert "validates_existing_local_artifacts_only: true" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "scheduler_queue_broker_worker_agent_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "config_backup_or_change_added: false" in output
    assert f"[PASS] {phase_2c_08.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_08.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_08.REPORT_HTML).exists()


def test_task_alias_catalog_and_report_index_visibility_for_phase_2c_08(tmp_path):
    _materialize_required_artifacts(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_08.TASK_NAME)

    assert task["task_id"] == "phase_2c_08_next_slice_implementation"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_08.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_08.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_08.DOC_PATH.as_posix() in task["report_paths"]
    assert "SELECTED_NEXT_SLICE_ARTIFACT_VALIDATION_JOB" in task["notes"]
    assert "ARTIFACT_VALIDATION_JOB_IMPLEMENTED_YES" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]
    assert "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_08.TASK_ALIAS], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-08 Next-Slice Implementation" in html
    assert "phase_2c_08_next_slice_implementation.json" in html
