import copy
from pathlib import Path

import network_lab
import phase_2j_05_local_approval_envelope_validation_job as phase_2j_05
from report_file_utils import path_exists, read_text_with_long_path, write_text_with_parents


DOC_PATH = Path("docs/phase_2j/phase_2j_05_first_local_validation_job_implementation.md")


APPROVAL_ENVELOPE_TEXT = """
# Phase 2J-04 - First Local-only Validation Job Authorization Gate / Planning Only

Status: PLANNING_ONLY_DOCUMENTATION_ONLY

AUTHORIZED_FOR_2J_05_LOCAL_ONLY_VALIDATION_JOB_IMPLEMENTATION: YES
FIRST_VALIDATION_JOB_SCOPE_FIXED: YES

## First Validation Job Scope

The first validation job is local_approval_envelope_validation_job.

## Allowed Scope For Phase 2J-05

Local files only.

## Forbidden Scope

No live device access. The job does not use SSH. The job does not use NETCONF.
The job does not use RESTCONF. It does not use providers, APIs, models, or secrets.
It does not perform config backup or config change behavior.
It does not add runner, scheduler, worker, queue, broker, or agent loop behavior.

## Runtime Non-permission Statement

APPROVAL_ENVELOPE_BOUNDARY: DOCUMENTATION_AUTHORIZATION_ONLY
RUNTIME_PERMISSION_GRANTED: NO
RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO

RECOMMENDED_NEXT_TASK_MODE: IMPLEMENTATION
"""


def _materialize_required_artifacts(project_root: Path) -> None:
    contract_path = project_root / phase_2j_05.PHASE_2J_03_APPROVAL_ENVELOPE_CONTRACT_PATH
    envelope_path = project_root / phase_2j_05.DEFAULT_APPROVAL_ENVELOPE_PATH
    write_text_with_parents(contract_path, "Phase 2J-03 approval envelope contract fixture\n", encoding="utf-8")
    write_text_with_parents(envelope_path, APPROVAL_ENVELOPE_TEXT, encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2j_05():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2J-05 First Local-only Validation Job" not in agents_text
    assert "phase_2j_05_local_approval_envelope_validation_job" not in agents_text


def test_phase_2j_05_markdown_artifact_exists_and_has_required_sections():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Phase 2J-05 First Local-only Validation Job / Implementation" in text
    for section in (
        "## Decision Summary",
        "## Implementation Scope",
        "## Relationship To Phase 2J-04 Authorization",
        "## Job Name",
        "## What The Job Validates",
        "## What The Job Does Not Do",
        "## Explicit Forbidden Runtime Boundaries",
        "## Test / Verification Summary",
        "## Documentation Readability Review",
        "## Final Implementation Result",
    ):
        assert section in text
    for label in (
        "AUTHORIZED_BY_2J_04: YES",
        "IMPLEMENTED_JOB_NAME: local_approval_envelope_validation_job",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "REPORT_ONLY: YES",
        "DRY_RUN_MOCK_ONLY: YES",
        "RUNTIME_PERMISSION_ADDED: NO",
        "APPROVAL_EXECUTION_ADDED: NO",
        "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO",
        "DEVICE_SSH_NETCONF_RESTCONF_PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_OR_CHANGE_TOUCHED: NO",
        "FINAL_READABILITY_RESULT: PASS",
    ):
        assert label in text
    assert phase_2j_05.FINAL_VERDICT in text


def test_validation_job_definition_is_local_deterministic_report_only():
    first = phase_2j_05.build_validation_job_definition()
    second = phase_2j_05.build_validation_job_definition()

    assert first == second
    assert first["job_name"] == "local_approval_envelope_validation_job"
    assert first["local_only"] is True
    assert first["deterministic"] is True
    assert first["report_only"] is True
    assert first["dry_run_only"] is True
    assert first["mock_only"] is True
    assert first["validates_static_repository_artifacts_only"] is True
    assert first["requires_live_device"] is False
    assert first["requires_network"] is False
    assert first["requires_provider"] is False
    assert first["requires_api"] is False
    assert first["requires_model"] is False
    assert first["requires_secrets"] is False
    assert first["grants_runtime_permission"] is False
    assert first["executes_approval"] is False
    assert phase_2j_05.validate_validation_job_definition(first)["valid"] is True


def test_validation_job_does_not_populate_execution_or_external_fields():
    job = phase_2j_05.build_validation_job_definition()

    for field_name in phase_2j_05.NON_EXECUTABLE_FIELDS:
        assert job[field_name] is None
    assert all(value is False for value in job["non_execution_proof"].values())


def test_approval_envelope_text_validation_reports_missing_fields():
    valid = phase_2j_05.validate_approval_envelope_text(APPROVAL_ENVELOPE_TEXT)
    invalid = phase_2j_05.validate_approval_envelope_text("Phase 2J-04 only\n")

    assert valid["valid"] is True
    assert valid["status"] == "PASS"
    assert valid["missing_fields"] == []
    assert invalid["valid"] is False
    assert invalid["status"] == "FAIL"
    assert "authorization decision" in invalid["missing_fields"]
    assert "explicit forbidden scope" in invalid["missing_fields"]


def test_phase_2j_05_report_validates_default_local_artifact():
    report = phase_2j_05.build_phase_2j_05_local_approval_envelope_validation_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["job_name"] == "local_approval_envelope_validation_job"
    assert report["validated_artifact_path"] == phase_2j_05.DEFAULT_APPROVAL_ENVELOPE_PATH.as_posix()
    assert report["missing_fields"] == []
    assert report["local_only"] is True
    assert report["deterministic"] is True
    assert report["report_only"] is True
    assert report["dry_run_only"] is True
    assert report["mock_only"] is True
    assert all(item["status"] == "PASS" for item in report["static_reference_checks"])


def test_phase_2j_05_report_output_is_deterministic():
    first = phase_2j_05.build_phase_2j_05_local_approval_envelope_validation_report(Path.cwd())
    second = phase_2j_05.build_phase_2j_05_local_approval_envelope_validation_report(Path.cwd())

    assert first == second


def test_phase_2j_05_no_forbidden_scope_flags_are_added():
    report = phase_2j_05.build_phase_2j_05_local_approval_envelope_validation_report(Path.cwd())

    for flag_name, expected in phase_2j_05.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "approval_execution_added",
        "runtime_permission_added",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "scheduler_added",
        "queue_added",
        "broker_added",
        "worker_added",
        "agent_loop_added",
        "live_device_touched",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_touched",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
    ):
        assert report[flag_name] is False


def test_phase_2j_05_rejects_tampered_execution_and_missing_field_flags():
    report = phase_2j_05.build_phase_2j_05_local_approval_envelope_validation_report(Path.cwd())
    tampered = copy.deepcopy(report)
    tampered["runtime_permission_added"] = True
    tampered["approval_execution_added"] = True
    tampered["runner_added"] = True
    tampered["queue_added"] = True
    tampered["broker_added"] = True
    tampered["agent_loop_added"] = True
    tampered["live_device_touched"] = True
    tampered["ssh_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["config_backup_or_change_touched"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["missing_fields"] = ["authorization decision"]
    tampered["validation_job"]["shell_command"] = "echo unsafe"

    validation = phase_2j_05.validate_phase_2j_05_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "APPROVAL_ENVELOPE_MISSING_REQUIRED_FIELDS" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runtime_permission_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:approval_execution_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]
    assert "VALIDATION_JOB:NON_EXECUTABLE_FIELD_POPULATED:shell_command" in validation["errors"]


def test_cli_writes_phase_2j_05_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_required_artifacts(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2J-05 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2J-05 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2j_05.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2J-05 First Local-only Validation Job" in output
    assert "Job name: local_approval_envelope_validation_job" in output
    assert "validated_artifact_path: docs/phase_2j/phase_2j_04_first_local_validation_job_authorization_gate_planning_only.md" in output
    assert "missing_fields: 0" in output
    assert "local_only: true" in output
    assert "deterministic: true" in output
    assert "report_only: true" in output
    assert "dry_run_mock_only: true" in output
    assert "runtime_permission_added: false" in output
    assert "approval_execution_added: false" in output
    assert "runner_scheduler_worker_queue_broker_agent_loop_added: false" in output
    assert "device_ssh_netconf_restconf_provider_api_model_secrets_touched: false" in output
    assert "config_backup_or_change_touched: false" in output
    assert f"[PASS] {phase_2j_05.FINAL_VERDICT}" in output
    assert path_exists(tmp_path / phase_2j_05.REPORT_JSON)
    assert path_exists(tmp_path / phase_2j_05.REPORT_HTML)


def test_task_catalog_and_report_index_visibility_for_phase_2j_05(tmp_path):
    _materialize_required_artifacts(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2j_05.TASK_NAME)

    assert task["task_id"] == "phase_2j_05_local_approval_envelope_validation_job"
    assert task["day"] == "Phase 2J"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2j_05.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2j_05.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2j_05.DOC_PATH.as_posix() in task["report_paths"]
    assert "LOCAL_APPROVAL_ENVELOPE_VALIDATION_JOB_IMPLEMENTED_YES" in task["notes"]
    assert "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED_NO" in task["notes"]
    assert "CONFIG_BACKUP_OR_CHANGE_TOUCHED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2j_05.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Phase 2J-05 First Local-only Validation Job" in html
    assert "phase_2j_05_local_approval_envelope_validation_job.json" in html
