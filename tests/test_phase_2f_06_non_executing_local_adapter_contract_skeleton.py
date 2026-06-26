from dataclasses import replace
from pathlib import Path

import phase_2f_06_non_executing_local_adapter_contract_skeleton as phase_2f_06


DOC_PATH = Path("docs/phase_2f/phase_2f_06_non_executing_local_adapter_contract_skeleton.md")


def test_agents_md_is_not_modified_for_phase_2f_06():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2F-06 Non-Executing Local Adapter Contract Skeleton" not in agents_text
    assert "phase_2f_06_non_executing_local_adapter_contract_skeleton" not in agents_text


def test_phase_2f_06_document_exists_with_required_markers():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Phase 2F-06 - Non-Executing Local Adapter Contract Skeleton" in text
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
        "AUTHORIZED_SCOPE: non_executing_local_adapter_contract_skeleton",
        "NON_EXECUTING: YES",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "CONTRACT_ONLY: YES",
        "RUNNER_INTEGRATION_TOUCHED: NO",
        "ADAPTER_EXECUTION_WIRING_TOUCHED: NO",
        "SSH_NETCONF_RESTCONF_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_TOUCHED: NO",
        "NEXT_PHASE_STARTED: NO",
        phase_2f_06.FINAL_VERDICT,
    ):
        assert marker in text


def test_local_adapter_contract_metadata_is_non_executing():
    contract = phase_2f_06.build_local_adapter_contract()

    assert contract.contract_name == phase_2f_06.AUTHORIZED_SCOPE
    assert contract.phase == "2F-06"
    assert contract.local_only is True
    assert contract.deterministic is True
    assert contract.non_executing is True
    assert contract.contract_only is True
    assert contract.report_only is True
    assert contract.dry_run_safe is True
    assert contract.mock_only is True
    assert contract.wired_to_runner is False
    assert contract.wired_to_execution_path is False
    assert contract.connected_to_live_device is False
    assert contract.connected_to_provider_api_model_secrets is False
    assert contract.capable_of_config_backup_change is False


def test_capability_declarations_do_not_support_forbidden_work():
    contract = phase_2f_06.build_local_adapter_contract()

    assert tuple(capability.name for capability in contract.capabilities) == (
        "contract_metadata_review",
        "contract_shape_validation",
    )
    for capability in contract.capabilities:
        assert capability.local_only is True
        assert capability.deterministic is True
        assert capability.contract_only is True
        assert capability.supports_execution is False
        assert capability.supports_live_device is False
        assert capability.supports_provider_api_model is False
        assert capability.supports_secrets is False
        assert capability.supports_config_backup is False
        assert capability.supports_config_change is False


def test_contract_validation_is_deterministic_and_local():
    contract = phase_2f_06.build_local_adapter_contract()

    first = phase_2f_06.validate_local_adapter_contract(contract)
    second = phase_2f_06.validate_local_adapter_contract(contract)

    assert first == second
    assert first.passed is True
    assert first.status == "PASS"
    assert first.non_executing is True
    assert first.local_only is True
    assert first.deterministic is True
    assert first.runner_reached is False
    assert first.execution_path_reached is False
    assert first.external_access_attempted is False
    assert first.secrets_accessed is False


def test_request_shape_validation_accepts_only_static_contract_fixture():
    request = phase_2f_06.build_sample_adapter_contract_request()

    result = phase_2f_06.validate_adapter_contract_request(request)

    assert result.passed is True
    assert result.status == "PASS"
    assert request["requested_capability"] == "contract_shape_validation"
    assert request["source_kind"] == "static_contract_fixture"
    assert request["safety_boundary"]["supports_execution"] is False
    assert result.runner_reached is False
    assert result.execution_path_reached is False
    assert result.external_access_attempted is False
    assert result.secrets_accessed is False


def test_request_validation_rejects_live_transport_runner_and_secret_keys():
    request = phase_2f_06.build_sample_adapter_contract_request()
    request["ssh_target"] = "router1"
    request["payload"]["command_allowlist"] = ["show version"]
    request["payload"]["runner"] = "network_lab"
    request["payload"]["secret_ref"] = "LAB_SECRET"

    result = phase_2f_06.validate_adapter_contract_request(request)

    assert result.passed is False
    assert "FORBIDDEN_REQUEST_KEY:$.ssh_target" in result.errors
    assert "FORBIDDEN_REQUEST_KEY:$.payload.command_allowlist" in result.errors
    assert "FORBIDDEN_REQUEST_KEY:$.payload.runner" in result.errors
    assert "FORBIDDEN_REQUEST_KEY:$.payload.secret_ref" in result.errors
    assert result.runner_reached is False
    assert result.execution_path_reached is False
    assert result.external_access_attempted is False
    assert result.secrets_accessed is False


def test_request_validation_rejects_execution_capability_and_boundary_tampering():
    request = phase_2f_06.build_sample_adapter_contract_request()
    request["requested_capability"] = "read_only_device_collection"
    request["safety_boundary"]["supports_execution"] = True
    request["safety_boundary"]["wired_to_runner"] = True

    result = phase_2f_06.validate_adapter_contract_request(request)

    assert result.passed is False
    assert "REQUESTED_CAPABILITY_NOT_CONTRACT_ONLY" in result.errors
    assert "SAFETY_BOUNDARY_VALUE_MISMATCH:supports_execution" in result.errors
    assert "SAFETY_BOUNDARY_VALUE_MISMATCH:wired_to_runner" in result.errors
    assert result.execution_path_reached is False


def test_contract_validation_rejects_tampered_execution_support():
    contract = phase_2f_06.build_local_adapter_contract()
    tampered_capability = replace(contract.capabilities[0], supports_execution=True)
    tampered = replace(
        contract,
        wired_to_execution_path=True,
        connected_to_live_device=True,
        capabilities=(tampered_capability,) + contract.capabilities[1:],
    )

    result = phase_2f_06.validate_local_adapter_contract(tampered)

    assert result.passed is False
    assert "CONTRACT_FLAG_MISMATCH:wired_to_execution_path" in result.errors
    assert "CONTRACT_FLAG_MISMATCH:connected_to_live_device" in result.errors
    assert (
        "CAPABILITY_FORBIDDEN_FLAG_ENABLED:contract_metadata_review:supports_execution"
        in result.errors
    )
    assert result.runner_reached is False
    assert result.execution_path_reached is False


def test_phase_2f_06_summary_is_deterministic_and_forbidden_scope_closed():
    first = phase_2f_06.build_phase_2f_06_contract_summary()
    second = phase_2f_06.build_phase_2f_06_contract_summary()

    assert first == second
    assert first["final_verdict"] == phase_2f_06.FINAL_VERDICT
    assert first["contract_validation"]["passed"] is True
    assert first["request_validation"]["passed"] is True
    assert all(value is False for value in first["forbidden_scope_status"].values())
