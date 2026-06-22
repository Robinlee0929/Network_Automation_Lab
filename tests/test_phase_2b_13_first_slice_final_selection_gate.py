import copy
from pathlib import Path

import network_lab
import phase_2b_13_first_slice_final_selection_gate as gate


DOC_PATH = Path("docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_13():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-13 First-Slice Final Selection Gate" not in agents_text
    assert "phase_2b_13_first_slice_final_selection_gate" not in agents_text


def test_phase_2b_13_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-13 First-Slice Final Selection Gate - Planning Only" in text
    for section in (
        "## Purpose",
        "## AGENTS.md Handling",
        "## Selected Future First Slice",
        "## Selection Criteria",
        "## Example Job Types Remain Examples Only",
        "## Phase 2B-14 Authorization Gate",
        "## Planning-Only Boundary",
        "## Existing Artifacts Referenced",
        "## Non-Implementation Statement",
        "## Decision",
    ):
        assert section in text
    assert gate.FINAL_VERDICT in text
    assert "No implementation is authorized by this artifact." in text


def test_phase_2b_13_selects_future_first_slice_but_does_not_implement_it():
    report = gate.build_phase_2b_13_first_slice_final_selection_gate_report()
    text = _doc_text()

    assert report["future_first_slice_selected"] is True
    assert report["selected_future_first_slice"]["name"] == "local_static_job_definition_and_evidence_contract_slice"
    assert report["selected_future_first_slice"]["implementation_status"] == "NOT_IMPLEMENTED"
    assert report["selected_future_first_slice_implemented"] is False
    assert report["implementation_authorized_by_phase_2b_13"] is False
    assert "Future first slice selected: YES." in text
    assert "`local_static_job_definition_and_evidence_contract_slice`" in text
    assert "Implementation remains forbidden: YES." in text


def test_phase_2b_13_preserves_2b_14_as_implementation_authorization_gate():
    report = gate.build_phase_2b_13_first_slice_final_selection_gate_report()
    text = _doc_text()

    auth_gate = report["implementation_authorization_gate_2b_14"]
    assert auth_gate["gate"] == "Phase 2B-14 Implementation Authorization Gate"
    assert auth_gate["required_before_any_implementation"] is True
    assert auth_gate["reserved_by_phase_2b_13"] is True
    assert auth_gate["phase_2b_13_grants_implementation_permission"] is False
    assert report["phase_2b_14_implementation_authorization_gate_reserved"] is True
    assert "Phase 2B-14 remains the required implementation authorization gate." in text
    assert "PHASE_2B_14_IMPLEMENTATION_AUTHORIZATION_GATE_RESERVED: YES" in text


def test_phase_2b_13_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = gate.build_phase_2b_13_first_slice_final_selection_gate_report()

    assert report["validation"]["valid"] is True
    for flag_name, expected in gate.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "selected_future_first_slice_implemented",
        "implementation_authorized_by_phase_2b_13",
        "phase_2c_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_worker_added",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "live_device_access_added",
        "real_device_inventory_access_added",
        "provider_calls_added",
        "api_calls_added",
        "model_calls_added",
        "secrets_handling_added",
        "frontend_api_integration_added",
        "production_workflow_added",
        "real_backup_execution_added",
        "real_validation_added",
        "real_command_execution_added",
        "real_configuration_change_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
    ):
        assert report[flag_name] is False


def test_phase_2b_13_rejects_tampered_implementation_or_phase_2c_flags():
    report = gate.build_phase_2b_13_first_slice_final_selection_gate_report()
    tampered = copy.deepcopy(report)
    tampered["selected_future_first_slice_implemented"] = True
    tampered["implementation_authorized_by_phase_2b_13"] = True
    tampered["phase_2c_touched"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_touched"] = True
    tampered["api_calls_added"] = True
    tampered["secrets_handling_added"] = True

    validation = gate.validate_phase_2b_13_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_2B_14_IMPLEMENTATION_AUTHORIZATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:selected_future_first_slice_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_authorized_by_phase_2b_13" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:api_calls_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_13_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-13 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-13 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-13 First-Slice Final Selection Gate - Planning Only" in output
    assert "agents_md_read_before_changes: true" in output
    assert "agents_md_modified: false" in output
    assert "future_first_slice_selected: true" in output
    assert "selected_future_first_slice_name: local_static_job_definition_and_evidence_contract_slice" in output
    assert "selected_future_first_slice_implemented: false" in output
    assert "phase_2b_13_planning_only: true" in output
    assert "implementation_authorized_by_phase_2b_13: false" in output
    assert "phase_2b_14_implementation_authorization_gate_reserved: true" in output
    assert "phase_2c_touched: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {gate.FINAL_VERDICT}" in output
    assert (tmp_path / gate.REPORT_JSON).exists()
    assert (tmp_path / gate.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2b_13(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == gate.TASK_NAME)

    assert task["task_id"] == "phase_2b_13_first_slice_final_selection_gate"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert gate.REPORT_JSON.as_posix() in task["report_paths"]
    assert gate.REPORT_HTML.as_posix() in task["report_paths"]
    assert gate.DOC_PATH.as_posix() in task["report_paths"]
    assert "FUTURE_FIRST_SLICE_SELECTED_TRUE" in task["notes"]
    assert "SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED_FALSE" in task["notes"]
    assert "IMPLEMENTATION_AUTHORIZED_BY_PHASE_2B_13_FALSE" in task["notes"]
    assert "PHASE_2B_14_IMPLEMENTATION_AUTHORIZATION_GATE_RESERVED_TRUE" in task["notes"]
    assert "PHASE_2C_TOUCHED_FALSE" in task["notes"]

    assert network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-13 First-Slice Final Selection Gate - Planning Only" in html
    assert "phase_2b_13_first_slice_final_selection_gate.json" in html
