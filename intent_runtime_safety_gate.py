"""Day77 runtime safety gate / no-execution enforcement report.

This module links deterministic Day73-Day76 reviewer evidence into final
runtime gate records. It is mock-only and dry-run-only: the gate can report
review readiness, blocks, or evidence gaps, but it never unlocks execution.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional

from intent_dry_run_plan_builder import build_dry_run_plans
from intent_manual_review_approval_envelope import build_approval_envelopes
from intent_mock_ai_decision_pipeline import run_mock_ai_decision_pipeline
from intent_runtime_audit_trail import build_runtime_audit_records


EXECUTION_MODE = "runtime_safety_gate_mock_dry_run_no_execution"
CREATED_AT = "2026-06-08T00:00:00+08:00"
RUNTIME_GATE_STATE = "LOCKED"

REVIEW_READY = "REVIEW_READY"
LOCKED_BY_POLICY = "LOCKED_BY_POLICY"
BLOCKED_FOR_REVIEW = "BLOCKED_FOR_REVIEW"
EVIDENCE_GAP = "EVIDENCE_GAP"

GATE_RESULTS = {
    REVIEW_READY,
    LOCKED_BY_POLICY,
    BLOCKED_FOR_REVIEW,
    EVIDENCE_GAP,
}

REQUIRED_GATE_FIELDS = (
    "gate_id",
    "scenario_id",
    "decision_id",
    "dry_run_plan_id",
    "approval_envelope_id",
    "audit_id",
    "evidence_chain_complete",
    "runtime_gate_state",
    "execution_policy",
    "blocked_conditions",
    "safety_invariants",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "gate_result",
    "created_at",
)

EVIDENCE_REFERENCES = [
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
]


def _decision_id(decision_record: Optional[Dict[str, Any]], scenario_id: str) -> str:
    if not decision_record:
        return ""
    return str(decision_record.get("decision_id") or f"day73-decision-{scenario_id}")


def _evidence_chain_complete(
    decision_id: str,
    dry_run_plan_id: str,
    approval_envelope_id: str,
    audit_id: str,
) -> bool:
    return bool(decision_id and dry_run_plan_id and approval_envelope_id and audit_id)


def _gate_result(
    chain_complete: bool,
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
) -> str:
    if not chain_complete:
        return EVIDENCE_GAP
    if audit_record and str(audit_record.get("audit_result", "")) == REVIEW_READY:
        return REVIEW_READY
    if audit_record and str(audit_record.get("audit_result", "")) == BLOCKED_FOR_REVIEW:
        return BLOCKED_FOR_REVIEW
    if plan_record and str(plan_record.get("plan_status", "")) in {"BLOCKED", "INVALID_INPUT_BLOCKED"}:
        return BLOCKED_FOR_REVIEW
    if envelope_record and str(envelope_record.get("reviewer_decision", "")) in {
        "blocked_live_action",
        "rejected_for_review_gap",
        "requires_manual_follow_up",
    }:
        return BLOCKED_FOR_REVIEW
    return LOCKED_BY_POLICY


def _blocked_conditions(gate_result: str) -> List[str]:
    conditions = [
        "runtime gate state is LOCKED",
        "allowed_to_execute is false",
        "dry_run_only is true",
        "execution_unlock_supported is false",
        "execute mapped task is blocked",
        "OpenAI API, AI SDK, and real AI runtime are blocked",
        "SSH, device access, arbitrary command execution, and config.json dependency are blocked",
        "dashboard form submission, POST routes, approve buttons, execute buttons, and action endpoints are blocked",
        "router, switch, firewall, VPN, VRRP, or network configuration changes are blocked",
    ]
    if gate_result == EVIDENCE_GAP:
        return ["complete Day73-Day76 evidence chain is required before reviewer status can be trusted"] + conditions
    if gate_result == BLOCKED_FOR_REVIEW:
        return ["source decision, plan, envelope, or audit requires reviewer block/follow-up"] + conditions
    if gate_result == LOCKED_BY_POLICY:
        return ["execution remains locked by final Day77 runtime policy"] + conditions
    return conditions


def _safety_invariants(
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "decision_allowed_to_execute": decision_record.get("allowed_to_execute") if decision_record else None,
        "plan_allowed_to_execute": plan_record.get("allowed_to_execute") if plan_record else None,
        "plan_dry_run_only": plan_record.get("dry_run_only") if plan_record else None,
        "envelope_allowed_to_execute": envelope_record.get("allowed_to_execute") if envelope_record else None,
        "envelope_dry_run_only": envelope_record.get("dry_run_only") if envelope_record else None,
        "envelope_execution_unlock_supported": (
            envelope_record.get("execution_unlock_supported") if envelope_record else None
        ),
        "audit_allowed_to_execute": audit_record.get("allowed_to_execute") if audit_record else None,
        "audit_dry_run_only": audit_record.get("dry_run_only") if audit_record else None,
        "audit_execution_unlock_supported": (
            audit_record.get("execution_unlock_supported") if audit_record else None
        ),
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "runtime_gate_state": RUNTIME_GATE_STATE,
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


def _execution_policy(gate_result: str) -> Dict[str, Any]:
    return {
        "mode": EXECUTION_MODE,
        "gate_result": gate_result,
        "allowed_actions": ["record_no_execution_gate_evidence"],
        "blocked_actions": [
            "execute mapped task",
            "call OpenAI API or AI SDK",
            "start real AI runtime",
            "open SSH or access a device",
            "run arbitrary commands",
            "read config.json",
            "submit dashboard approval",
            "click approve button",
            "click execute button",
            "call dashboard action endpoint",
            "unlock execution",
            "change router, switch, firewall, VPN, VRRP, or network configuration",
        ],
        "gate_effect": "locked_no_execution_unlock",
    }


def build_runtime_safety_gate_record(
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    audit_record: Optional[Dict[str, Any]],
    scenario_id: str,
) -> Dict[str, Any]:
    """Build one deterministic Day77 no-execution safety gate record."""
    decision = deepcopy(decision_record) if decision_record else None
    plan = deepcopy(plan_record) if plan_record else None
    envelope = deepcopy(envelope_record) if envelope_record else None
    audit = deepcopy(audit_record) if audit_record else None

    decision_id = _decision_id(decision, scenario_id)
    dry_run_plan_id = str(plan.get("plan_id", "")) if plan else ""
    approval_envelope_id = str(envelope.get("envelope_id", "")) if envelope else ""
    audit_id = str(audit.get("audit_id", "")) if audit else ""
    chain_complete = _evidence_chain_complete(
        decision_id,
        dry_run_plan_id,
        approval_envelope_id,
        audit_id,
    )
    gate_result = _gate_result(chain_complete, plan, envelope, audit)

    return {
        "gate_id": f"day77-gate-{scenario_id}",
        "scenario_id": scenario_id,
        "decision_id": decision_id,
        "dry_run_plan_id": dry_run_plan_id,
        "approval_envelope_id": approval_envelope_id,
        "audit_id": audit_id,
        "evidence_chain_complete": chain_complete,
        "runtime_gate_state": RUNTIME_GATE_STATE,
        "execution_policy": _execution_policy(gate_result),
        "blocked_conditions": _blocked_conditions(gate_result),
        "safety_invariants": _safety_invariants(decision, plan, envelope, audit),
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "gate_result": gate_result,
        "created_at": CREATED_AT,
    }


def build_runtime_safety_gate_records(
    decision_records: Optional[List[Dict[str, Any]]] = None,
    dry_run_plans: Optional[List[Dict[str, Any]]] = None,
    approval_envelopes: Optional[List[Dict[str, Any]]] = None,
    audit_records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Link deterministic Day73-Day76 records into final Day77 locked gates."""
    decisions = deepcopy(decision_records) if decision_records is not None else run_mock_ai_decision_pipeline()
    plans = deepcopy(dry_run_plans) if dry_run_plans is not None else build_dry_run_plans()
    envelopes = deepcopy(approval_envelopes) if approval_envelopes is not None else build_approval_envelopes()
    audits = (
        deepcopy(audit_records)
        if audit_records is not None
        else build_runtime_audit_records(decisions, plans, envelopes)
    )

    decisions_by_scenario = {str(item.get("scenario_id", "")): item for item in decisions}
    plans_by_scenario = {str(item.get("source_scenario_id", "")): item for item in plans}
    envelopes_by_scenario = {str(item.get("scenario_id", "")): item for item in envelopes}
    audits_by_scenario = {str(item.get("scenario_id", "")): item for item in audits}
    scenario_ids = sorted(
        scenario_id
        for scenario_id in (
            set(decisions_by_scenario)
            | set(plans_by_scenario)
            | set(envelopes_by_scenario)
            | set(audits_by_scenario)
        )
        if scenario_id
    )
    return [
        build_runtime_safety_gate_record(
            decisions_by_scenario.get(scenario_id),
            plans_by_scenario.get(scenario_id),
            envelopes_by_scenario.get(scenario_id),
            audits_by_scenario.get(scenario_id),
            scenario_id,
        )
        for scenario_id in scenario_ids
    ]


def validate_runtime_safety_gate_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day77 gate records."""
    errors: List[str] = []
    if not records:
        errors.append("no runtime safety gate records were produced.")
        return errors

    for record in records:
        gate_id = record.get("gate_id", "<missing>")
        for field in REQUIRED_GATE_FIELDS:
            if field not in record:
                errors.append(f"{gate_id} missing required field: {field}.")
        if record.get("allowed_to_execute") is not False:
            errors.append(f"{gate_id} allowed_to_execute must be false.")
        if record.get("dry_run_only") is not True:
            errors.append(f"{gate_id} dry_run_only must be true.")
        if record.get("execution_unlock_supported") is not False:
            errors.append(f"{gate_id} execution_unlock_supported must be false.")
        if record.get("runtime_gate_state") != RUNTIME_GATE_STATE:
            errors.append(f"{gate_id} runtime_gate_state must be LOCKED.")
        if record.get("gate_result") not in GATE_RESULTS:
            errors.append(f"{gate_id} has unknown gate_result.")

        expected_complete = bool(
            record.get("decision_id")
            and record.get("dry_run_plan_id")
            and record.get("approval_envelope_id")
            and record.get("audit_id")
        )
        if record.get("evidence_chain_complete") is not expected_complete:
            errors.append(f"{gate_id} evidence_chain_complete is not calculated from all references.")
        if record.get("gate_result") == EVIDENCE_GAP and expected_complete:
            errors.append(f"{gate_id} complete evidence chain must not be marked EVIDENCE_GAP.")

        policy = record.get("execution_policy", {})
        if policy.get("gate_effect") != "locked_no_execution_unlock":
            errors.append(f"{gate_id} execution policy must keep the gate locked.")
        if "unlock execution" not in policy.get("blocked_actions", []):
            errors.append(f"{gate_id} execution policy must block execution unlock.")
        if policy.get("allowed_actions") != ["record_no_execution_gate_evidence"]:
            errors.append(f"{gate_id} allowed actions must be record-only evidence.")

        invariants = record.get("safety_invariants", {})
        if invariants.get("allowed_to_execute") is not False:
            errors.append(f"{gate_id} invariant allowed_to_execute must be false.")
        if invariants.get("dry_run_only") is not True:
            errors.append(f"{gate_id} invariant dry_run_only must be true.")
        if invariants.get("execution_unlock_supported") is not False:
            errors.append(f"{gate_id} invariant execution_unlock_supported must be false.")
        if invariants.get("runtime_gate_state") != RUNTIME_GATE_STATE:
            errors.append(f"{gate_id} invariant runtime_gate_state must be LOCKED.")

    return errors


def build_runtime_safety_gate_report() -> Dict[str, Any]:
    """Build the Day77 reviewer no-execution enforcement report payload."""
    records = build_runtime_safety_gate_records()
    validation_errors = validate_runtime_safety_gate_records(records)
    result_counts = {
        result: sum(1 for record in records if record.get("gate_result") == result)
        for result in sorted(GATE_RESULTS)
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
        "evidence_chain_complete_all_records": all(
            record.get("evidence_chain_complete") is True for record in records
        ),
        "gate_results_do_not_unlock_execution": all(
            record.get("execution_policy", {}).get("gate_effect") == "locked_no_execution_unlock"
            and "unlock execution" in record.get("execution_policy", {}).get("blocked_actions", [])
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
        "day": "Day77",
        "title": "Runtime Safety Gate / No-Execution Enforcement Report",
        "task_name": "runtime-safety-gate",
        "execution_mode": EXECUTION_MODE,
        "source_pipeline": (
            "intent_mock_ai_decision_pipeline.run_mock_ai_decision_pipeline -> "
            "intent_dry_run_plan_builder.build_dry_run_plans -> "
            "intent_manual_review_approval_envelope.build_approval_envelopes -> "
            "intent_runtime_audit_trail.build_runtime_audit_records"
        ),
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "summary": {
            "gate_record_count": len(records),
            "gate_result_counts": result_counts,
            "runtime_gate_state_values": sorted({record.get("runtime_gate_state") for record in records}),
            "evidence_chain_complete_values": sorted(
                {record.get("evidence_chain_complete") for record in records}
            ),
            "allowed_to_execute_values": sorted(
                {record.get("allowed_to_execute") for record in records}
            ),
            "dry_run_only_values": sorted({record.get("dry_run_only") for record in records}),
            "execution_unlock_supported_values": sorted(
                {record.get("execution_unlock_supported") for record in records}
            ),
        },
        "safety_gate_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Mock-only runtime safety gate evidence.",
            "Dry-run-only no-execution enforcement report.",
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No real AI runtime.",
            "No SSH or device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No dashboard form, POST route, approve button, execute button, or action endpoint.",
            "No gate result can unlock execution.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day77 links Day73 mock decisions, Day74 dry-run plans, Day75 approval "
            "envelopes, and Day76 audit records into deterministic runtime safety "
            "gate records. Every gate remains LOCKED with allowed_to_execute=false, "
            "dry_run_only=true, and execution_unlock_supported=false; no gate result, "
            "reviewer decision, audit result, dashboard surface, API, SSH, device "
            "access, mapped task, config dependency, or network change can unlock execution."
        ),
    }
