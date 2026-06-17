import json

import network_lab
import phase_2a_06_negative_regression_matrix as matrix


def test_negative_regression_matrix_rejects_redacts_and_never_executes():
    report = matrix.build_phase_2a_06_negative_regression_matrix_report()

    assert report["phase"] == "2A-06"
    assert report["status"] == "PASS"
    assert report["summary"]["matrix_cases"] == 12
    assert report["summary"]["unsafe_inputs_rejected"] == 12
    assert report["summary"]["unsafe_inputs_redacted"] == 12
    assert report["summary"]["unsafe_inputs_non_executing"] == 12
    assert report["summary"]["raw_unsafe_literals_present"] == 0
    assert report["summary"]["failed_cases"] == 0
    assert report["summary"]["next_phase_allowed_count"] == 0
    assert report["next_phase_allowed"] is False
    assert report["phase_2b_authorized"] is False
    assert report["phase_2a_07_authorized"] is False

    for case in report["negative_regression_matrix"]:
        assert case["passed"] is True
        assert case["actual"]["validator_status"] == "REJECTED"
        assert case["actual"]["plan_gate_status"] == "REJECTED"
        assert case["actual"]["evidence_status"] == "rejected"
        assert case["actual"]["values_redacted"] is True
        assert case["actual"]["runner_invoked"] is False
        assert case["actual"]["adapter_invoked"] is False
        assert case["actual"]["plan_generated"] is False
        assert case["actual"]["live_execution_opened"] is False
        assert case["actual"]["next_phase_allowed"] is False
        assert case["redacted_input_summary"]["raw_values_included"] is False
        assert case["redacted_input_summary"]["values_redacted"] is True
        assert case["non_execution_proof"]["execution_payload_present"] is False

    payload = json.dumps(report, sort_keys=True)
    for literal in matrix.RAW_UNSAFE_LITERALS:
        assert literal not in payload


def test_validator_fails_if_raw_unsafe_literal_is_leaked():
    report = matrix.build_phase_2a_06_negative_regression_matrix_report()
    report["negative_regression_matrix"][0]["redacted_input_summary"]["leaked_value"] = (
        matrix.RAW_UNSAFE_LITERALS[0]
    )

    validation = matrix.validate_phase_2a_06_report(report)

    assert validation["valid"] is False
    assert "RAW_UNSAFE_LITERAL_PRESENT" in validation["errors"]


def test_cli_writes_negative_regression_matrix_without_runner_adapter_or_profile(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-06 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-06 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", matrix.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-06 Negative Regression Matrix" in output
    assert "Task name: phase2a-06-negative-regression-matrix" in output
    assert "Matrix cases: 12" in output
    assert "Unsafe inputs rejected: 12" in output
    assert "Unsafe inputs redacted: 12" in output
    assert "Unsafe inputs non-executing: 12" in output
    assert "Raw unsafe literals present: 0" in output
    assert "runner_invoked: false" in output
    assert "adapter_invoked: false" in output
    assert "plan_generated_for_unsafe_input: false" in output
    assert "live_execution_opened: false" in output
    assert "phase_2b_authorized: false" in output
    assert "phase_2a_07_authorized: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] PHASE_2A_06_NEGATIVE_REGRESSION_MATRIX_READY" in output
    assert (tmp_path / matrix.REPORT_JSON).exists()
    assert (tmp_path / matrix.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == matrix.TASK_NAME)

    assert task["task_id"] == "phase_2a_06_negative_regression_matrix"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert matrix.REPORT_JSON.as_posix() in task["report_paths"]
    assert matrix.REPORT_HTML.as_posix() in task["report_paths"]
    assert matrix.DOC_PATH.as_posix() in task["report_paths"]
    assert "NEGATIVE_REGRESSION_MATRIX_ONLY" in task["notes"]
    assert "UNSAFE_INPUTS_REJECTED" in task["notes"]
    assert "UNSAFE_INPUT_VALUES_REDACTED" in task["notes"]
    assert "REJECTED_INPUTS_NON_EXECUTING" in task["notes"]
    assert "PHASE_2A_07_AUTHORIZED_FALSE" in task["notes"]

    assert network_lab.main(["--task", matrix.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-06 Negative Regression Matrix" in html
    assert "phase_2a_06_negative_regression_matrix.json" in html
