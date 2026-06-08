"""Day78 controlled runtime safety case package.

This module links the deterministic Day72-Day77 controlled runtime evidence
chain into final reviewer safety case records. It is mock-only, dry-run-only,
and report-only. It never unlocks execution.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional

from intent_controlled_ai_runtime_validator import validate_controlled_ai_runtime_input
from intent_dry_run_plan_builder import build_dry_run_plans
from intent_manual_review_approval_envelope import build_approval_envelopes
from intent_mock_ai_decision_pipeline import (
    run_mock_ai_decision_pipeline,
    sample_day73_inputs,
)
from intent_runtime_audit_trail import build_runtime_audit_records
from intent_runtime_safety_gate import (
    BLOCKED_FOR_REVIEW,
    EVIDENCE_GAP,
    LOCKED_BY_POLICY,
    REVIEW_READY,
    RUNTIME_GATE_STATE,
    build_runtime_safety_gate_records,
)


EXECUTION_MODE = "runtime_safety_case_mock_dry_run_end_to_end_reviewer_package"
CREATED_AT = "2026-06-08T00:00:00Z"
FINAL_RECOMMENDATION = "REVIEW_ONLY"

SAFETY_CASE_RESULTS = {
    REVIEW_READY,
    LOCKED_BY_POLICY,
    BLOCKED_FOR_REVIEW,
    EVIDENCE_GAP,
}

REQUIRED_SAFETY_CASE_FIELDS = (
    "case_id",
    "scenario_id",
    "input_validation_id",
    "decision_id",
    "dry_run_plan_id",
    "approval_envelope_id",
    "audit_id",
    "gate_id",
    "evidence_chain_complete",
    "runtime_gate_state",
    "compliance_checks",
    "reviewer_findings",
    "safety_invariants",
    "final_recommendation",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "safety_case_result",
    "created_at",
)

EVIDENCE_REFERENCES = [
    "docs/ai/intent_controlled_ai_runtime_input_validator.md",
    "docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md",
    "docs/ai/intent_mock_ai_decision_pipeline.md",
    "docs/roadmap/day73_mock_ai_decision_pipeline.md",
    "docs/ai/intent_dry_run_plan_builder.md",
    "docs/roadmap/day74_dry_run_plan_builder.md",
    "docs/ai/intent_manual_review_approval_envelope.md",
    "docs/roadmap/day75_manual_review_approval_envelope.md",
    "docs/ai/intent_runtime_audit_trail.md",
    "docs/roadmap/day76_runtime_audit_trail.md",
    "docs/ai/intent_runtime_safety_gate.md",
    "docs/roadmap/day77_runtime_safety_gate.md",
    "docs/ai/intent_runtime_safety_case.md",
    "docs/roadmap/day78_runtime_safety_case.md",
]


def _input_validation_records() -> List[Dict[str, Any]]:
    records = []
    for scenario in sample_day73_inputs():
        scenario_copy = deepcopy(scenario)
        scenario_id = str(scenario_copy.get("scenario_id", ""))
        payload = deepcopy(scenario_copy.get("payload", {}))
        validation = validate_controlled_ai_runtime_input(payload)
        records.append(
            {
                "input_validation_id": f"day72-validation-{scenario_id}",
                "scenario_id": scenario_id,
                "validator_result": validation,
                "validator_status": (
                    "BLOCKED"
                    if validation.get("blocked") is True
                    else "VALID"
                    if validation.get("valid") is True
                    else "INVALID"
                ),
                "allowed_to_execute": False,
                "created_at": CREATED_AT,
            }
        )
    return records


def _safety_case_result(chain_complete: bool, gate_record: Optional[Dict[str, Any]]) -> str:
    if not chain_complete:
        return EVIDENCE_GAP
    gate_result = str(gate_record.get("gate_result", "")) if gate_record else ""
    if gate_result in SAFETY_CASE_RESULTS:
        return gate_result
    return LOCKED_BY_POLICY


def _evidence_chain_complete(
    input_validation_id: str,
    decision_id: str,
    dry_run_plan_id: str,
    approval_envelope_id: str,
    audit_id: str,
    gate_id: str,
) -> bool:
    return bool(
        input_validation_id
        and decision_id
        and dry_run_plan_id
        and approval_envelope_id
        and audit_id
        and gate_id
    )


def _compliance_checks(
    validation_record: Optional[Dict[str, Any]],
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
    gate_record: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "day72_input_validation_present": bool(validation_record),
        "day73_mock_decision_present": bool(decision_record),
        "day74_dry_run_plan_present": bool(plan_record),
        "day75_approval_envelope_present": bool(envelope_record),
        "day76_audit_trail_present": bool(audit_record),
        "day77_runtime_safety_gate_present": bool(gate_record),
        "day72_execution_allowed_false": (
            validation_record.get("validator_result", {}).get("execution_allowed") is False
            if validation_record
            else False
        ),
        "day73_allowed_to_execute_false": (
            decision_record.get("allowed_to_execute") is False if decision_record else False
        ),
        "day74_allowed_to_execute_false": (
            plan_record.get("allowed_to_execute") is False if plan_record else False
        ),
        "day74_dry_run_only_true": (
            plan_record.get("dry_run_only") is True if plan_record else False
        ),
        "day75_execution_unlock_supported_false": (
            envelope_record.get("execution_unlock_supported") is False
            if envelope_record
            else False
        ),
        "day76_execution_unlock_supported_false": (
            audit_record.get("execution_unlock_supported") is False if audit_record else False
        ),
        "day77_runtime_gate_locked": (
            gate_record.get("runtime_gate_state") == RUNTIME_GATE_STATE
            if gate_record
            else False
        ),
    }


def _reviewer_findings(
    result: str,
    chain_complete: bool,
    gate_record: Optional[Dict[str, Any]],
) -> List[str]:
    findings = [
        "Day78 links Day72-Day77 evidence into one reviewer safety case record.",
        "The safety case is deterministic, mock-only, dry-run-only, and report-only.",
        "Final recommendation is REVIEW_ONLY; no safety case result is an execution permission.",
    ]
    if chain_complete:
        findings.append("All Day72-Day77 references are present for this scenario.")
    else:
        findings.append("One or more Day72-Day77 references are missing; reviewer evidence has a gap.")
    if gate_record:
        findings.append(
            "Day77 gate result "
            f"{gate_record.get('gate_result', '')} is preserved with runtime_gate_state LOCKED."
        )
    findings.append(f"Day78 safety case result is {result}.")
    return findings


def _safety_invariants(
    validation_record: Optional[Dict[str, Any]],
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
    gate_record: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "input_validation_execution_allowed": (
            validation_record.get("validator_result", {}).get("execution_allowed")
            if validation_record
            else None
        ),
        "decision_allowed_to_execute": (
            decision_record.get("allowed_to_execute") if decision_record else None
        ),
        "plan_allowed_to_execute": plan_record.get("allowed_to_execute") if plan_record else None,
        "plan_dry_run_only": plan_record.get("dry_run_only") if plan_record else None,
        "envelope_allowed_to_execute": (
            envelope_record.get("allowed_to_execute") if envelope_record else None
        ),
        "envelope_dry_run_only": envelope_record.get("dry_run_only") if envelope_record else None,
        "envelope_execution_unlock_supported": (
            envelope_record.get("execution_unlock_supported") if envelope_record else None
        ),
        "audit_allowed_to_execute": audit_record.get("allowed_to_execute") if audit_record else None,
        "audit_dry_run_only": audit_record.get("dry_run_only") if audit_record else None,
        "audit_execution_unlock_supported": (
            audit_record.get("execution_unlock_supported") if audit_record else None
        ),
        "gate_allowed_to_execute": gate_record.get("allowed_to_execute") if gate_record else None,
        "gate_dry_run_only": gate_record.get("dry_run_only") if gate_record else None,
        "gate_execution_unlock_supported": (
            gate_record.get("execution_unlock_supported") if gate_record else None
        ),
        "runtime_gate_state": RUNTIME_GATE_STATE,
        "final_recommendation": FINAL_RECOMMENDATION,
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "execution_unlock_supported_by_safety_case_result": False,
        "mock_only": True,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "real_ai_runtime_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "mapped_task_executed": False,
        "arbitrary_command_executed": False,
        "config_json_read": False,
        "dashboard_form_added": False,
        "dashboard_post_route_added": False,
        "dashboard_approve_button_added": False,
        "dashboard_execute_button_added": False,
        "dashboard_action_endpoint_added": False,
        "network_configuration_changed": False,
    }


def build_runtime_safety_case_record(
    validation_record: Optional[Dict[str, Any]],
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
    gate_record: Optional[Dict[str, Any]],
    scenario_id: str,
) -> Dict[str, Any]:
    """Build one deterministic Day78 end-to-end reviewer safety case."""
    validation = deepcopy(validation_record) if validation_record else None
    decision = deepcopy(decision_record) if decision_record else None
    plan = deepcopy(plan_record) if plan_record else None
    envelope = deepcopy(envelope_record) if envelope_record else None
    audit = deepcopy(audit_record) if audit_record else None
    gate = deepcopy(gate_record) if gate_record else None

    input_validation_id = (
        str(validation.get("input_validation_id", "")) if validation else ""
    )
    decision_id = (
        str(decision.get("decision_id") or f"day73-decision-{scenario_id}")
        if decision
        else ""
    )
    dry_run_plan_id = str(plan.get("plan_id", "")) if plan else ""
    approval_envelope_id = str(envelope.get("envelope_id", "")) if envelope else ""
    audit_id = str(audit.get("audit_id", "")) if audit else ""
    gate_id = str(gate.get("gate_id", "")) if gate else ""
    chain_complete = _evidence_chain_complete(
        input_validation_id,
        decision_id,
        dry_run_plan_id,
        approval_envelope_id,
        audit_id,
        gate_id,
    )
    safety_case_result = _safety_case_result(chain_complete, gate)

    return {
        "case_id": f"day78-case-{scenario_id}",
        "scenario_id": scenario_id,
        "input_validation_id": input_validation_id,
        "decision_id": decision_id,
        "dry_run_plan_id": dry_run_plan_id,
        "approval_envelope_id": approval_envelope_id,
        "audit_id": audit_id,
        "gate_id": gate_id,
        "evidence_chain_complete": chain_complete,
        "runtime_gate_state": RUNTIME_GATE_STATE,
        "compliance_checks": _compliance_checks(
            validation,
            decision,
            plan,
            envelope,
            audit,
            gate,
        ),
        "reviewer_findings": _reviewer_findings(safety_case_result, chain_complete, gate),
        "safety_invariants": _safety_invariants(
            validation,
            decision,
            plan,
            envelope,
            audit,
            gate,
        ),
        "final_recommendation": FINAL_RECOMMENDATION,
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "safety_case_result": safety_case_result,
        "created_at": CREATED_AT,
    }


def build_runtime_safety_case_records(
    validation_records: Optional[List[Dict[str, Any]]] = None,
    decision_records: Optional[List[Dict[str, Any]]] = None,
    dry_run_plans: Optional[List[Dict[str, Any]]] = None,
    approval_envelopes: Optional[List[Dict[str, Any]]] = None,
    audit_records: Optional[List[Dict[str, Any]]] = None,
    gate_records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Link deterministic Day72-Day77 records into Day78 safety cases."""
    validations = (
        deepcopy(validation_records)
        if validation_records is not None
        else _input_validation_records()
    )
    decisions = (
        deepcopy(decision_records)
        if decision_records is not None
        else run_mock_ai_decision_pipeline()
    )
    plans = deepcopy(dry_run_plans) if dry_run_plans is not None else build_dry_run_plans()
    envelopes = (
        deepcopy(approval_envelopes)
        if approval_envelopes is not None
        else build_approval_envelopes()
    )
    audits = (
        deepcopy(audit_records)
        if audit_records is not None
        else build_runtime_audit_records(decisions, plans, envelopes)
    )
    gates = (
        deepcopy(gate_records)
        if gate_records is not None
        else build_runtime_safety_gate_records(decisions, plans, envelopes, audits)
    )

    validations_by_scenario = {str(item.get("scenario_id", "")): item for item in validations}
    decisions_by_scenario = {str(item.get("scenario_id", "")): item for item in decisions}
    plans_by_scenario = {str(item.get("source_scenario_id", "")): item for item in plans}
    envelopes_by_scenario = {str(item.get("scenario_id", "")): item for item in envelopes}
    audits_by_scenario = {str(item.get("scenario_id", "")): item for item in audits}
    gates_by_scenario = {str(item.get("scenario_id", "")): item for item in gates}
    scenario_ids = sorted(
        scenario_id
        for scenario_id in (
            set(validations_by_scenario)
            | set(decisions_by_scenario)
            | set(plans_by_scenario)
            | set(envelopes_by_scenario)
            | set(audits_by_scenario)
            | set(gates_by_scenario)
        )
        if scenario_id
    )

    return [
        build_runtime_safety_case_record(
            validations_by_scenario.get(scenario_id),
            decisions_by_scenario.get(scenario_id),
            plans_by_scenario.get(scenario_id),
            envelopes_by_scenario.get(scenario_id),
            audits_by_scenario.get(scenario_id),
            gates_by_scenario.get(scenario_id),
            scenario_id,
        )
        for scenario_id in scenario_ids
    ]


def validate_runtime_safety_case_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day78 safety cases."""
    errors: List[str] = []
    if not records:
        errors.append("no runtime safety case records were produced.")
        return errors

    for record in records:
        case_id = record.get("case_id", "<missing>")
        for field in REQUIRED_SAFETY_CASE_FIELDS:
            if field not in record:
                errors.append(f"{case_id} missing required field: {field}.")
        if record.get("runtime_gate_state") != RUNTIME_GATE_STATE:
            errors.append(f"{case_id} runtime_gate_state must be LOCKED.")
        if record.get("final_recommendation") != FINAL_RECOMMENDATION:
            errors.append(f"{case_id} final_recommendation must be REVIEW_ONLY.")
        if record.get("allowed_to_execute") is not False:
            errors.append(f"{case_id} allowed_to_execute must be false.")
        if record.get("dry_run_only") is not True:
            errors.append(f"{case_id} dry_run_only must be true.")
        if record.get("execution_unlock_supported") is not False:
            errors.append(f"{case_id} execution_unlock_supported must be false.")
        if record.get("safety_case_result") not in SAFETY_CASE_RESULTS:
            errors.append(f"{case_id} has unknown safety_case_result.")

        expected_complete = bool(
            record.get("input_validation_id")
            and record.get("decision_id")
            and record.get("dry_run_plan_id")
            and record.get("approval_envelope_id")
            and record.get("audit_id")
            and record.get("gate_id")
        )
        if record.get("evidence_chain_complete") is not expected_complete:
            errors.append(
                f"{case_id} evidence_chain_complete is not calculated from all references."
            )
        if record.get("safety_case_result") == EVIDENCE_GAP and expected_complete:
            errors.append(f"{case_id} complete evidence chain must not be marked EVIDENCE_GAP.")

        invariants = record.get("safety_invariants", {})
        if invariants.get("allowed_to_execute") is not False:
            errors.append(f"{case_id} invariant allowed_to_execute must be false.")
        if invariants.get("dry_run_only") is not True:
            errors.append(f"{case_id} invariant dry_run_only must be true.")
        if invariants.get("execution_unlock_supported") is not False:
            errors.append(f"{case_id} invariant execution_unlock_supported must be false.")
        if invariants.get("runtime_gate_state") != RUNTIME_GATE_STATE:
            errors.append(f"{case_id} invariant runtime_gate_state must be LOCKED.")
        if invariants.get("final_recommendation") != FINAL_RECOMMENDATION:
            errors.append(f"{case_id} invariant final_recommendation must be REVIEW_ONLY.")
        if invariants.get("execution_unlock_supported_by_safety_case_result") is not False:
            errors.append(f"{case_id} safety case result must not support execution unlock.")

    return errors


def build_runtime_safety_case_report() -> Dict[str, Any]:
    """Build the Day78 end-to-end reviewer safety case package."""
    records = build_runtime_safety_case_records()
    validation_errors = validate_runtime_safety_case_records(records)
    result_counts = {
        result: sum(1 for record in records if record.get("safety_case_result") == result)
        for result in sorted(SAFETY_CASE_RESULTS)
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            record.get("allowed_to_execute") is False for record in records
        ),
        "dry_run_only_always_true": all(record.get("dry_run_only") is True for record in records),
        "execution_unlock_supported_always_false": all(
            record.get("execution_unlock_supported") is False for record in records
        ),
        "runtime_gate_state_locked_all_records": all(
            record.get("runtime_gate_state") == RUNTIME_GATE_STATE for record in records
        ),
        "final_recommendation_review_only_all_records": all(
            record.get("final_recommendation") == FINAL_RECOMMENDATION for record in records
        ),
        "evidence_chain_complete_all_records": all(
            record.get("evidence_chain_complete") is True for record in records
        ),
        "safety_case_results_do_not_unlock_execution": all(
            record.get("execution_unlock_supported") is False
            and record.get("allowed_to_execute") is False
            and record.get("final_recommendation") == FINAL_RECOMMENDATION
            for record in records
        ),
        "mapped_task_executed": False,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "real_ai_runtime_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "arbitrary_command_executed": False,
        "config_json_read": False,
        "dashboard_form_added": False,
        "dashboard_post_route_added": False,
        "dashboard_approve_button_added": False,
        "dashboard_execute_button_added": False,
        "dashboard_action_endpoint_added": False,
        "network_configuration_changed": False,
    }
    disabled_keys = {
        "mapped_task_executed",
        "openai_api_used",
        "ai_sdk_dependency_used",
        "real_ai_runtime_used",
        "ssh_used",
        "device_access_used",
        "arbitrary_command_executed",
        "config_json_read",
        "dashboard_form_added",
        "dashboard_post_route_added",
        "dashboard_approve_button_added",
        "dashboard_execute_button_added",
        "dashboard_action_endpoint_added",
        "network_configuration_changed",
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in disabled_keys else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day78",
        "title": "Controlled Runtime Safety Case / End-to-End Reviewer Package",
        "task_name": "runtime-safety-case",
        "execution_mode": EXECUTION_MODE,
        "source_pipeline": (
            "intent_controlled_ai_runtime_validator.validate_controlled_ai_runtime_input -> "
            "intent_mock_ai_decision_pipeline.run_mock_ai_decision_pipeline -> "
            "intent_dry_run_plan_builder.build_dry_run_plans -> "
            "intent_manual_review_approval_envelope.build_approval_envelopes -> "
            "intent_runtime_audit_trail.build_runtime_audit_records -> "
            "intent_runtime_safety_gate.build_runtime_safety_gate_records"
        ),
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "summary": {
            "safety_case_record_count": len(records),
            "safety_case_result_counts": result_counts,
            "runtime_gate_state_values": sorted(
                {record.get("runtime_gate_state") for record in records}
            ),
            "evidence_chain_complete_values": sorted(
                {record.get("evidence_chain_complete") for record in records}
            ),
            "final_recommendation_values": sorted(
                {record.get("final_recommendation") for record in records}
            ),
            "allowed_to_execute_values": sorted(
                {record.get("allowed_to_execute") for record in records}
            ),
            "dry_run_only_values": sorted({record.get("dry_run_only") for record in records}),
            "execution_unlock_supported_values": sorted(
                {record.get("execution_unlock_supported") for record in records}
            ),
        },
        "safety_case_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Mock-only end-to-end reviewer safety case.",
            "Dry-run-only final safety case package.",
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No real AI runtime.",
            "No SSH or device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No dashboard form, POST route, approve button, execute button, or action endpoint.",
            "No safety case result can unlock execution.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day78 links Day72 input validation, Day73 mock AI decisions, Day74 "
            "dry-run plans, Day75 approval envelopes, Day76 audit records, and "
            "Day77 locked runtime gates into deterministic reviewer safety case "
            "records. Every safety case keeps runtime_gate_state=LOCKED, "
            "final_recommendation=REVIEW_ONLY, allowed_to_execute=false, "
            "dry_run_only=true, and execution_unlock_supported=false; no safety "
            "case result, gate result, audit result, reviewer decision, dashboard "
            "surface, API, SSH, device access, mapped task, config dependency, "
            "or network change can unlock execution."
        ),
    }
