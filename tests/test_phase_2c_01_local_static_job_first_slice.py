import copy
from pathlib import Path

import network_lab
import phase_2c_01_local_static_job_first_slice as phase_2c_01


DOC_PATH = Path("docs/phase_2c/phase_2c_01_local_static_job_first_slice.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_01():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-01 Local Static Job First Slice" not in agents_text
    assert "phase_2c_01_local_static_job_first_slice" not in agents_text


def test_scope_confirmation_artifact_exists_with_required_sections():
    text = _doc_text()

    assert "# Phase 2C-01 Local Static Job First Slice" in text
    for section in (
        "## PHASE_GOAL:",
        "## EXAMPLE_JOB_TYPES:",
        "## FORBIDDEN_SCOPE:",
        "## EXISTING_ARTIFACTS_TO_REFERENCE:",
        "## IMPLEMENTATION_BOUNDARY:",
    ):
        assert section in text
    assert "SCOPE_CONFIRMATION_WRITTEN: YES" in text
    assert "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE: NO" in text
    assert "PHASE_2C_01_LOCAL_STATIC_JOB_FIRST_SLICE_SCOPE_CONFIRMED" in text


def test_local_static_job_exists_and_is_local_static_deterministic():
    first = phase_2c_01.build_local_static_job_definition()
    second = phase_2c_01.build_local_static_job_definition()

    assert first == second
    assert first["job_kind"] == "local_static_job"
    assert first["local_only"] is True
    assert first["static_only"] is True
    assert first["deterministic"] is True
    assert first["offline"] is True
    assert first["testable"] is True
    assert first["non_device"] is True
    assert first["non_provider"] is True
    assert first["non_api"] is True
    assert first["non_model"] is True
    assert first["non_secret"] is True
    assert phase_2c_01.validate_local_static_job_definition(first)["valid"] is True


def test_local_static_job_does_not_populate_execution_or_external_fields():
    job = phase_2c_01.build_local_static_job_definition()

    for field_name in phase_2c_01.NON_EXECUTABLE_FIELDS:
        assert job[field_name] is None
    assert all(value is False for value in job["non_execution_proof"].values())


def test_phase_2c_01_report_preserves_forbidden_scope_and_implements_only_local_static_job():
    report = phase_2c_01.build_phase_2c_01_local_static_job_first_slice_report()

    assert report["validation"]["valid"] is True
    assert report["authorized_first_slice"] == "local_static_job"
    assert report["local_static_job_implemented"] is True
    assert report["not_next_day_feature"] is True
    for flag_name in (
        "execution_opened",
        "provider_api_opened",
        "model_opened",
        "secrets_touched",
        "live_device_touched",
        "ssh_netconf_restconf_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "provider_calls_added",
        "api_calls_added",
        "model_calls_added",
        "secrets_handling_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "custom_command_execution_added",
        "custom_script_execution_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
    ):
        assert report[flag_name] is False


def test_example_job_types_remain_examples_and_phase_is_not_narrowed():
    report = phase_2c_01.build_phase_2c_01_local_static_job_first_slice_report()

    assert set(report["example_job_types"]) == set(phase_2c_01.EXAMPLE_JOB_TYPES)
    assert "local_static_job" not in report["example_job_types"]
    assert len(report["example_job_types"]) > 1
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert report["scope_narrowed_to_one_example_job_type"] is False
    assert report["needs_scope_confirmation"] is False


def test_phase_2c_01_rejects_tampered_execution_and_scope_flags():
    report = phase_2c_01.build_phase_2c_01_local_static_job_first_slice_report()
    tampered = copy.deepcopy(report)
    tampered["execution_opened"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["live_device_touched"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["scope_narrowed_to_one_example_job_type"] = True
    tampered["needs_scope_confirmation"] = True
    tampered["local_static_job_definition"]["shell_command"] = "echo unsafe"

    validation = phase_2c_01.validate_phase_2c_01_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:provider_api_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:model_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:live_device_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_netconf_restconf_touched" in validation["errors"]
    assert "LOCAL_STATIC_JOB:NON_EXECUTABLE_FIELD_POPULATED:shell_command" in validation["errors"]


def test_cli_writes_phase_2c_01_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-01 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-01 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_01.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-01 Local Static Job First Slice" in output
    assert "Authorized first slice: local_static_job" in output
    assert "local_static_job_implemented: true" in output
    assert "execution_opened: false" in output
    assert "provider_api_opened: false" in output
    assert "model_opened: false" in output
    assert "secrets_touched: false" in output
    assert "live_device_touched: false" in output
    assert "ssh_netconf_restconf_touched: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert f"[PASS] {phase_2c_01.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_01.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_01.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_01(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_01.TASK_NAME)

    assert task["task_id"] == "phase_2c_01_local_static_job_first_slice"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_01.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_01.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_01.DOC_PATH.as_posix() in task["report_paths"]
    assert "LOCAL_STATIC_JOB_IMPLEMENTED_YES" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]
    assert "SSH_NETCONF_RESTCONF_TOUCHED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_01.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-01 Local Static Job First Slice" in html
    assert "phase_2c_01_local_static_job_first_slice.json" in html
