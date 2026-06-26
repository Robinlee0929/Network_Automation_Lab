from pathlib import Path

import pytest

import phase_2f_10_non_executing_local_adapter_evidence_binding as phase_2f_10


DOC_PATH = Path("docs/phase_2f/phase_2f_10_non_executing_local_adapter_evidence_binding.md")


def test_agents_md_is_not_modified_for_phase_2f_10():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2F-10 Non-Executing Local Adapter Evidence Binding" not in agents_text
    assert "phase_2f_10_non_executing_local_adapter_evidence_binding" not in agents_text


def test_phase_2f_10_document_exists_with_required_markers():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Phase 2F-10 - Non-Executing Local Adapter Evidence Binding" in text
    for section in (
        "## Scope",
        "## Implementation Summary",
        "## Files Changed",
        "## Safety Boundary Confirmation",
        "## Validation Method",
        "## Final Verdict",
    ):
        assert section in text
    for marker in (
        "AUTHORIZED_SCOPE: non_executing_local_adapter_evidence_binding",
        "NON_EXECUTING: YES",
        "LOCAL_ONLY: YES",
        "EVIDENCE_BINDING_ONLY: YES",
        "NO_LIVE_NETWORK: YES",
        "NO_COMMAND_EXECUTION: YES",
        "NO_SSH_NETCONF_RESTCONF: YES",
        "RUNNER_CONNECTED: NO",
        "READ_ONLY_LAB_ADAPTER_CREATED: NO",
        "EXECUTABLE_JOB_REGISTERED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_TOUCHED: NO",
        "NEXT_PHASE_STARTED: NO",
        phase_2f_10.FINAL_VERDICT,
    ):
        assert marker in text


def test_local_adapter_evidence_binding_is_deterministic_and_non_executing():
    metadata = phase_2f_10.build_sample_local_adapter_evidence_metadata()

    first = phase_2f_10.bind_local_adapter_evidence(metadata)
    second = phase_2f_10.bind_local_adapter_evidence(metadata)

    assert first == second
    assert first.binding_name == phase_2f_10.AUTHORIZED_SCOPE
    assert first.phase == "2F-10"
    assert first.adapter_contract_reference == phase_2f_10.PHASE_2F_06_CONTRACT_REFERENCE
    assert first.local_only is True
    assert first.deterministic is True
    assert first.non_executing is True
    assert first.evidence_binding_only is True
    assert first.report_only is True
    assert first.dry_run_safe is True
    assert first.mock_only is True
    assert first.no_live_network is True
    assert first.no_command_execution is True
    assert first.no_ssh_netconf_restconf is True
    assert first.runner_attached is False
    assert first.execution_path_attached is False
    assert first.adapter_instantiated is False
    assert first.live_device_touched is False
    assert first.provider_api_model_used is False
    assert first.secrets_used is False
    assert first.config_backup_change_added is False
    assert len(first.evidence_digest) == 64


def test_metadata_validation_accepts_local_fixture_only():
    metadata = phase_2f_10.build_sample_local_adapter_evidence_metadata()

    result = phase_2f_10.validate_local_adapter_evidence_metadata(metadata)

    assert result.passed is True
    assert result.status == "PASS"
    assert result.non_executing is True
    assert result.local_only is True
    assert result.deterministic is True
    assert result.evidence_binding_only is True
    assert result.runner_reached is False
    assert result.execution_path_reached is False
    assert result.adapter_instantiated is False
    assert result.external_access_attempted is False
    assert result.secrets_accessed is False
    assert result.live_device_touched is False


def test_metadata_validation_rejects_live_transport_runner_command_and_secret_keys():
    metadata = phase_2f_10.build_sample_local_adapter_evidence_metadata()
    metadata["ssh_target"] = "router1"
    metadata["metadata"]["command"] = "show version"
    metadata["metadata"]["runner"] = "network_lab"
    metadata["metadata"]["secret_ref"] = "LAB_SECRET"

    result = phase_2f_10.validate_local_adapter_evidence_metadata(metadata)

    assert result.passed is False
    assert "FORBIDDEN_METADATA_KEY:$.ssh_target" in result.errors
    assert "FORBIDDEN_METADATA_KEY:$.metadata.command" in result.errors
    assert "FORBIDDEN_METADATA_KEY:$.metadata.runner" in result.errors
    assert "FORBIDDEN_METADATA_KEY:$.metadata.secret_ref" in result.errors
    assert result.runner_reached is False
    assert result.execution_path_reached is False
    assert result.external_access_attempted is False
    assert result.secrets_accessed is False


def test_binding_rejects_unsafe_metadata_without_creating_binding():
    metadata = phase_2f_10.build_sample_local_adapter_evidence_metadata()
    metadata["source_kind"] = "live_device_collection"
    metadata["safety_boundary"]["no_live_network"] = False
    metadata["safety_boundary"]["runner_attached"] = True
    metadata["evidence_reference"]["evidence_status"] = "LIVE_COLLECTED"

    result = phase_2f_10.validate_local_adapter_evidence_metadata(metadata)

    assert result.passed is False
    assert "METADATA_SOURCE_KIND_NOT_LOCAL_EVIDENCE" in result.errors
    assert "SAFETY_BOUNDARY_VALUE_MISMATCH:no_live_network" in result.errors
    assert "SAFETY_BOUNDARY_VALUE_MISMATCH:runner_attached" in result.errors
    assert "EVIDENCE_STATUS_NOT_REVIEW_ONLY" in result.errors
    with pytest.raises(ValueError):
        phase_2f_10.bind_local_adapter_evidence(metadata)
    assert result.runner_reached is False
    assert result.execution_path_reached is False


def test_metadata_validation_rejects_wrong_contract_reference_and_bad_evidence_shape():
    metadata = phase_2f_10.build_sample_local_adapter_evidence_metadata()
    metadata["adapter_contract_reference"] = "read_only_lab_adapter"
    metadata["evidence_reference"] = {"evidence_id": "missing-local-kind-and-status"}

    result = phase_2f_10.validate_local_adapter_evidence_metadata(metadata)

    assert result.passed is False
    assert "ADAPTER_CONTRACT_REFERENCE_MISMATCH" in result.errors
    assert "EVIDENCE_REFERENCE_FIELD_MISSING:evidence_kind" in result.errors
    assert "EVIDENCE_REFERENCE_FIELD_MISSING:evidence_status" in result.errors
    assert "EVIDENCE_STATUS_NOT_REVIEW_ONLY" in result.errors
    assert "EVIDENCE_KIND_NOT_LOCAL_METADATA" in result.errors


def test_phase_2f_10_summary_is_deterministic_and_forbidden_scope_closed():
    first = phase_2f_10.build_phase_2f_10_evidence_binding_summary()
    second = phase_2f_10.build_phase_2f_10_evidence_binding_summary()

    assert first == second
    assert first["final_verdict"] == phase_2f_10.FINAL_VERDICT
    assert first["metadata_validation"]["passed"] is True
    assert first["binding"]["evidence_binding_only"] is True
    assert first["binding"]["runner_attached"] is False
    assert first["binding"]["execution_path_attached"] is False
    assert all(value is False for value in first["forbidden_scope_status"].values())
