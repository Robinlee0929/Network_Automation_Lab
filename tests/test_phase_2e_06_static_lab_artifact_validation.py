from copy import deepcopy
from pathlib import Path

import phase_2e_06_static_lab_artifact_validation as phase_2e_06


DOC_PATH = Path("docs/phase_2e/phase_2e_06_static_lab_artifact_validation_implementation.md")


def test_agents_md_is_not_modified_for_phase_2e_06():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2E-06 Static Lab Artifact Validation Implementation" not in agents_text
    assert "phase_2e_06_static_lab_artifact_validation" not in agents_text


def test_phase_2e_06_document_exists_with_required_sections():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Phase 2E-06 - Static Lab Artifact Validation Implementation" in text
    for section in (
        "## Scope",
        "## Implementation Summary",
        "## Files Changed",
        "## Safety Boundary Confirmation",
        "## Validation Commands Run",
        "## Test Results",
        "## Next Step",
    ):
        assert section in text
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO" in text
    assert "NEXT_STEP_REMAINS_UNAUTHORIZED: YES" in text


def test_valid_static_lab_artifact_returns_pass_result():
    artifact = phase_2e_06.build_valid_static_lab_artifact_fixture()

    result = phase_2e_06.validate_static_lab_artifact(artifact)

    assert result["passed"] is True
    assert result["status"] == "PASS"
    assert result["errors"] == []
    assert result["report_only"] is True
    assert result["dry_run_only"] is True
    assert result["mock_only"] is True


def test_missing_required_static_artifact_field_returns_fail_result():
    artifact = phase_2e_06.build_valid_static_lab_artifact_fixture()
    artifact.pop("reviewer_summary")

    result = phase_2e_06.validate_static_lab_artifact(artifact)

    assert result["passed"] is False
    assert result["status"] == "FAIL"
    assert "REQUIRED_FIELD_MISSING:reviewer_summary" in result["errors"]


def test_disallowed_live_network_or_execution_field_returns_fail_result():
    artifact = phase_2e_06.build_valid_static_lab_artifact_fixture()
    artifact["ssh_target"] = "router1"
    artifact["content"]["device_command"] = "show running-config"

    result = phase_2e_06.validate_static_lab_artifact(artifact)

    assert result["passed"] is False
    assert "UNSUPPORTED_FIELD:ssh_target" in result["errors"]
    assert "FORBIDDEN_FIELD_PRESENT:$.ssh_target" in result["errors"]
    assert "FORBIDDEN_FIELD_PRESENT:$.content.device_command" in result["errors"]
    assert result["runner_invoked"] is False
    assert result["adapter_invoked"] is False
    assert result["execution_path_reached"] is False


def test_static_artifact_validation_rejects_non_local_or_refresh_oriented_inputs():
    artifact = phase_2e_06.build_valid_static_lab_artifact_fixture()
    artifact["source_path"] = "ssh://router1/show/system"
    artifact["collected_state"] = "needs_refresh"

    result = phase_2e_06.validate_static_lab_artifact(artifact)

    assert result["passed"] is False
    assert "SOURCE_PATH_NOT_SAFE_LOCAL_RELATIVE_PATH" in result["errors"]
    assert "COLLECTED_STATE_NOT_ALREADY_COLLECTED" in result["errors"]


def test_validation_remains_local_deterministic_and_calls_no_external_systems():
    first = phase_2e_06.validate_static_lab_artifact(phase_2e_06.build_valid_static_lab_artifact_fixture())
    second = phase_2e_06.validate_static_lab_artifact(phase_2e_06.build_valid_static_lab_artifact_fixture())

    assert first == second
    assert first["external_access_attempted"] is False
    assert first["runner_invoked"] is False
    assert first["adapter_invoked"] is False
    assert first["execution_path_reached"] is False


def test_report_only_dry_run_mock_only_boundary_is_visible_in_report():
    report = phase_2e_06.build_phase_2e_06_static_lab_artifact_validation_report()

    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    assert report["summary"]["report_only_dry_run_mock_only_boundary_visible"] is True
    assert report["summary"]["external_system_calls_performed"] is False
    assert report["summary"]["runner_adapter_execution_path_reached"] is False
    assert report["machine_readable_verdict"]["REPORT_ONLY_DRY_RUN_MOCK_ONLY"] == "YES"
    assert report["machine_readable_verdict"]["RUNNER_ADAPTER_EXECUTION_PATH_ADDED"] == "NO"


def test_phase_2e_06_report_rejects_tampered_forbidden_scope_flags():
    report = phase_2e_06.build_phase_2e_06_static_lab_artifact_validation_report()
    tampered = deepcopy(report)
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["summary"]["external_system_calls_performed"] = True

    validation = phase_2e_06.validate_phase_2e_06_report(tampered)

    assert validation["valid"] is False
    assert "EXTERNAL_SYSTEM_CALLS_PERFORMED" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_netconf_restconf_live_device_touched" in validation["errors"]
    assert "FORBIDDEN_SCOPE_TOUCHED" in validation["errors"]
