"""Day68 reviewer quality checks for offline mock runtime reports.

This module inspects deterministic Day66 mock runtime dictionaries and uses the
Day67 contract validator in memory. It does not execute commands, read config
files, call APIs, open SSH, connect to devices, or change network state.
"""

from typing import Any, Dict, List

from intent_offline_mock_runtime import build_mock_runtime_report
from intent_runtime_contract import validate_runtime_results


RUNTIME_MODE = "offline_mock_report_only"
REVIEW_READY = "REVIEW_READY"
NEEDS_REVIEW = "NEEDS_REVIEW"

SAFETY_BOUNDARY = [
    "Offline mock reviewer quality check only.",
    "No OpenAI API usage.",
    "No voice integration.",
    "No SSH.",
    "No device or network access.",
    "No live action execution.",
    "No mapped task execution.",
    "No arbitrary command execution.",
    "No config.json dependency.",
    "No router, switch, firewall, VPN, VRRP, interface, route, or device configuration changes.",
    "No release tag.",
]


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_references(value: Any) -> bool:
    return isinstance(value, list) and any(_has_text(item) for item in value)


def _flag_is_false(mapping: Dict[str, Any], field: str) -> bool:
    return mapping.get(field) is False


def _mock_record_flag_is_false(scenario: Dict[str, Any], field: str) -> bool:
    record = scenario.get("mock_execution_record")
    return isinstance(record, dict) and record.get(field) is False


def _append_missing(missing: List[str], condition: bool, label: str) -> None:
    if not condition:
        missing.append(label)


def review_runtime_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Return reviewer-visible quality gates for one mock scenario."""
    contract_errors = validate_runtime_results([scenario])
    blocked = scenario.get("safety_category") == "blocked_live_action"

    input_intent_present = _has_text(scenario.get("input_text"))
    decision_result_present = _has_text(scenario.get("decision"))
    safety_classification_present = _has_text(scenario.get("safety_category"))
    blocked_reason_present_when_applicable = (
        _has_text(scenario.get("reviewer_warning")) if blocked else True
    )
    evidence_reference_present = _has_references(scenario.get("evidence_references"))
    contract_validation_result_present = isinstance(contract_errors, list)
    no_live_execution_evidence_present = (
        scenario.get("live_execution_allowed") is False
        and _mock_record_flag_is_false(scenario, "real_command_executed")
    )
    no_mapped_task_execution_evidence_present = (
        _flag_is_false(scenario, "mapped_task_executed")
        and _mock_record_flag_is_false(scenario, "mapped_task_executed")
    )
    no_device_network_change_evidence_present = (
        _mock_record_flag_is_false(scenario, "device_access_used")
        and _mock_record_flag_is_false(scenario, "device_connection_used")
        and _mock_record_flag_is_false(scenario, "network_change_made")
        and _mock_record_flag_is_false(scenario, "device_configuration_changed")
    )

    missing_evidence: List[str] = []
    _append_missing(missing_evidence, input_intent_present, "input intent")
    _append_missing(missing_evidence, decision_result_present, "decision result")
    _append_missing(missing_evidence, safety_classification_present, "safety classification")
    _append_missing(
        missing_evidence,
        blocked_reason_present_when_applicable,
        "blocked reason for live-action scenario",
    )
    _append_missing(missing_evidence, evidence_reference_present, "evidence reference")
    _append_missing(
        missing_evidence,
        contract_validation_result_present,
        "contract validation result",
    )
    _append_missing(
        missing_evidence,
        no_live_execution_evidence_present,
        "no live execution evidence",
    )
    _append_missing(
        missing_evidence,
        no_mapped_task_execution_evidence_present,
        "no mapped task execution evidence",
    )
    _append_missing(
        missing_evidence,
        no_device_network_change_evidence_present,
        "no device or network configuration change evidence",
    )
    if contract_errors:
        missing_evidence.append("passing Day67 contract validation")

    reviewer_verdict = REVIEW_READY if not missing_evidence else NEEDS_REVIEW
    return {
        "scenario_id": scenario.get("scenario_id", ""),
        "scenario_name": scenario.get("scenario_name", ""),
        "input_intent": scenario.get("input_text", ""),
        "decision": scenario.get("decision", ""),
        "safety_classification": scenario.get("safety_category", ""),
        "blocked_reason": scenario.get("reviewer_warning", ""),
        "evidence_references": list(scenario.get("evidence_references", []))
        if isinstance(scenario.get("evidence_references"), list)
        else [],
        "input_intent_present": input_intent_present,
        "decision_result_present": decision_result_present,
        "safety_classification_present": safety_classification_present,
        "blocked_reason_present_when_applicable": blocked_reason_present_when_applicable,
        "evidence_reference_present": evidence_reference_present,
        "contract_validation_result_present": contract_validation_result_present,
        "contract_validation_status": "PASS" if not contract_errors else "FAIL",
        "contract_validation_errors": contract_errors,
        "no_live_execution_evidence_present": no_live_execution_evidence_present,
        "no_mapped_task_execution_evidence_present": no_mapped_task_execution_evidence_present,
        "no_device_network_change_evidence_present": no_device_network_change_evidence_present,
        "missing_evidence": missing_evidence,
        "reviewer_verdict": reviewer_verdict,
    }


def _quality_gate_summary(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    gate_fields = [
        "input_intent_present",
        "decision_result_present",
        "safety_classification_present",
        "blocked_reason_present_when_applicable",
        "evidence_reference_present",
        "contract_validation_result_present",
        "no_live_execution_evidence_present",
        "no_mapped_task_execution_evidence_present",
        "no_device_network_change_evidence_present",
    ]
    return {
        "total_scenarios": len(entries),
        "review_ready_count": sum(1 for item in entries if item["reviewer_verdict"] == REVIEW_READY),
        "needs_review_count": sum(1 for item in entries if item["reviewer_verdict"] != REVIEW_READY),
        "all_scenarios_review_ready": all(item["reviewer_verdict"] == REVIEW_READY for item in entries),
        "gates": {
            field: {
                "pass_count": sum(1 for item in entries if item.get(field) is True),
                "fail_count": sum(1 for item in entries if item.get(field) is not True),
            }
            for field in gate_fields
        },
    }


def build_reviewer_quality_report(
    runtime_report: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build the fixed Day68 reviewer quality and evidence trace report."""
    source_report = runtime_report if runtime_report is not None else build_mock_runtime_report()
    scenarios = source_report.get("mock_scenarios", [])
    entries = [review_runtime_scenario(scenario) for scenario in scenarios if isinstance(scenario, dict)]
    validation_errors = validate_runtime_results(scenarios)
    quality_summary = _quality_gate_summary(entries)
    review_ready = (
        bool(entries)
        and not validation_errors
        and quality_summary["all_scenarios_review_ready"]
        and source_report.get("live_execution_allowed") is False
        and source_report.get("mapped_task_executed") is False
        and source_report.get("no_live_execution_occurred") is True
        and source_report.get("no_network_change_occurred") is True
    )

    return {
        "day": "Day68",
        "title": "Offline Mock Runtime Reviewer Report Quality & Evidence Trace Review",
        "runtime_mode": RUNTIME_MODE,
        "review_status": REVIEW_READY if review_ready else NEEDS_REVIEW,
        "overall_status": "PASS" if review_ready else "WARN",
        "source_days": ["Day66", "Day67"],
        "source_runtime_title": source_report.get("title", ""),
        "scenario_count": len(entries),
        "quality_gate_summary": quality_summary,
        "scenario_reviews": entries,
        "safety_boundary": list(SAFETY_BOUNDARY),
        "non_execution_evidence": {
            "no_live_action_executed": source_report.get("no_live_execution_occurred") is True,
            "live_execution_allowed_false": source_report.get("live_execution_allowed") is False,
            "no_mapped_task_executed": source_report.get("mapped_task_executed") is False
            and all(item.get("no_mapped_task_execution_evidence_present") is True for item in entries),
            "no_device_access_occurred": source_report.get("no_device_access_occurred") is True,
            "no_device_network_configuration_changed": source_report.get("no_network_change_occurred") is True
            and all(item.get("no_device_network_change_evidence_present") is True for item in entries),
            "no_openai_api_used": source_report.get("openai_api_used") is False,
            "no_voice_integration_used": source_report.get("voice_integration_used") is False,
            "no_ssh_used": source_report.get("ssh_used") is False,
            "no_config_json_dependency": source_report.get("config_json_read") is False,
        },
        "contract_validation_evidence": {
            "validator": "intent_runtime_contract.validate_runtime_results",
            "validation_performed": True,
            "contract_status": "PASS" if not validation_errors else "FAIL",
            "validation_errors": validation_errors,
            "validated_scenario_count": len(scenarios) if isinstance(scenarios, list) else 0,
        },
        "validation_notes": [
            "Day68 reviews Day66 mock runtime output and reuses the Day67 in-memory contract validator.",
            "Reviewer-ready scenarios must expose input intent, decision, safety classification, evidence references, and no-execution proof.",
            "Blocked live-action scenarios must include a reviewer-visible blocked reason.",
            "This report is generated from deterministic local mock data only.",
        ],
    }
