"""Day76 controlled runtime audit trail.

This module links the deterministic Day73 mock AI decisions, Day74 dry-run
plans, and Day75 manual review approval envelopes into reviewer evidence
packages. It is mock-only and dry-run-only: audit results are evidence labels
and never execution permissions.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional

from intent_dry_run_plan_builder import build_dry_run_plans
from intent_manual_review_approval_envelope import build_approval_envelopes
from intent_mock_ai_decision_pipeline import run_mock_ai_decision_pipeline


EXECUTION_MODE = "controlled_runtime_audit_trail_mock_dry_run_only"
CREATED_AT = "2026-06-08T00:00:00Z"

REVIEW_READY = "REVIEW_READY"
BLOCKED_FOR_REVIEW = "BLOCKED_FOR_REVIEW"
EVIDENCE_GAP = "EVIDENCE_GAP"

AUDIT_RESULTS = {REVIEW_READY, BLOCKED_FOR_REVIEW, EVIDENCE_GAP}

REQUIRED_AUDIT_FIELDS = (
    "audit_id",
    "scenario_id",
    "decision_id",
    "dry_run_plan_id",
    "approval_envelope_id",
    "evidence_chain",
    "reviewer_trace",
    "safety_invariants",
    "final_runtime_policy",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "evidence_chain_complete",
    "audit_result",
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
]


def _decision_id(decision_record: Optional[Dict[str, Any]], scenario_id: str) -> str:
    if not decision_record:
        return ""
    return str(decision_record.get("decision_id") or f"day73-decision-{scenario_id}")


def _evidence_chain(
    scenario_id: str,
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_id = _decision_id(decision_record, scenario_id)
    dry_run_plan_id = str(plan_record.get("plan_id", "")) if plan_record else ""
    approval_envelope_id = str(envelope_record.get("envelope_id", "")) if envelope_record else ""
    return {
        "day73_mock_ai_decision": {
            "present": bool(decision_record),
            "decision_id": decision_id,
            "scenario_id": scenario_id if decision_record else "",
            "decision_label": str(decision_record.get("decision_label", "")) if decision_record else "",
            "allowed_to_execute": decision_record.get("allowed_to_execute") if decision_record else None,
        },
        "day74_dry_run_plan": {
            "present": bool(plan_record),
            "dry_run_plan_id": dry_run_plan_id,
            "source_scenario_id": str(plan_record.get("source_scenario_id", "")) if plan_record else "",
            "plan_status": str(plan_record.get("plan_status", "")) if plan_record else "",
            "allowed_to_execute": plan_record.get("allowed_to_execute") if plan_record else None,
            "dry_run_only": plan_record.get("dry_run_only") if plan_record else None,
        },
        "day75_approval_envelope": {
            "present": bool(envelope_record),
            "approval_envelope_id": approval_envelope_id,
            "scenario_id": str(envelope_record.get("scenario_id", "")) if envelope_record else "",
            "reviewer_decision": str(envelope_record.get("reviewer_decision", "")) if envelope_record else "",
            "allowed_to_execute": envelope_record.get("allowed_to_execute") if envelope_record else None,
            "dry_run_only": envelope_record.get("dry_run_only") if envelope_record else None,
            "execution_unlock_supported": (
                envelope_record.get("execution_unlock_supported") if envelope_record else None
            ),
        },
        "complete": bool(decision_id and dry_run_plan_id and approval_envelope_id),
    }


def _reviewer_trace(
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
) -> List[str]:
    trace = []
    if decision_record:
        trace.append(
            "Day73 decision "
            f"{decision_record.get('decision_label', '')}: "
            f"{decision_record.get('next_reviewer_action', '')}"
        )
    else:
        trace.append("Day73 decision evidence is missing.")
    if plan_record:
        trace.append(
            "Day74 dry-run plan "
            f"{plan_record.get('plan_status', '')}: "
            f"{plan_record.get('next_reviewer_action', '')}"
        )
    else:
        trace.append("Day74 dry-run plan evidence is missing.")
    if envelope_record:
        trace.append(
            "Day75 approval envelope "
            f"{envelope_record.get('reviewer_decision', '')}: "
            f"{envelope_record.get('reviewer_signoff_state', '')}"
        )
    else:
        trace.append("Day75 approval envelope evidence is missing.")
    trace.append("Day76 audit result is evidence-only and cannot unlock execution.")
    return trace


def _safety_invariants(
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
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
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "mock_only": True,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "real_ai_runtime_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "mapped_task_executed": False,
        "arbitrary_command_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }


def _final_runtime_policy(audit_result: str) -> Dict[str, Any]:
    return {
        "mode": EXECUTION_MODE,
        "audit_result": audit_result,
        "allowed_actions": ["record_reviewer_evidence_package"],
        "blocked_actions": [
            "execute mapped task",
            "call OpenAI API or AI SDK",
            "start real AI runtime",
            "open SSH or access a device",
            "run arbitrary commands",
            "read config.json",
            "submit dashboard approval",
            "unlock execution",
            "change router, switch, firewall, VPN, VRRP, or network configuration",
        ],
        "review_effect": "evidence_only_no_execution_unlock",
    }


def _audit_result(
    chain_complete: bool,
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
) -> str:
    if not chain_complete:
        return EVIDENCE_GAP
    if str(plan_record.get("plan_status", "")) in {"BLOCKED", "INVALID_INPUT_BLOCKED"}:
        return BLOCKED_FOR_REVIEW
    if str(envelope_record.get("reviewer_decision", "")) in {
        "requires_manual_follow_up",
        "rejected_for_review_gap",
        "blocked_live_action",
    }:
        return BLOCKED_FOR_REVIEW
    return REVIEW_READY


def build_runtime_audit_record(
    decision_record: Optional[Dict[str, Any]],
    plan_record: Optional[Dict[str, Any]],
    envelope_record: Optional[Dict[str, Any]],
    scenario_id: str,
) -> Dict[str, Any]:
    """Build one deterministic Day76 reviewer audit record."""
    decision = deepcopy(decision_record) if decision_record else None
    plan = deepcopy(plan_record) if plan_record else None
    envelope = deepcopy(envelope_record) if envelope_record else None
    chain = _evidence_chain(scenario_id, decision, plan, envelope)
    chain_complete = chain["complete"]
    audit_result = _audit_result(chain_complete, plan, envelope)
    decision_id = _decision_id(decision, scenario_id)
    dry_run_plan_id = str(plan.get("plan_id", "")) if plan else ""
    approval_envelope_id = str(envelope.get("envelope_id", "")) if envelope else ""
    return {
        "audit_id": f"day76-audit-{scenario_id}",
        "scenario_id": scenario_id,
        "decision_id": decision_id,
        "dry_run_plan_id": dry_run_plan_id,
        "approval_envelope_id": approval_envelope_id,
        "evidence_chain": chain,
        "reviewer_trace": _reviewer_trace(decision, plan, envelope),
        "safety_invariants": _safety_invariants(decision, plan, envelope),
        "final_runtime_policy": _final_runtime_policy(audit_result),
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "evidence_chain_complete": chain_complete,
        "audit_result": audit_result,
        "created_at": CREATED_AT,
    }


def build_runtime_audit_records(
    decision_records: Optional[List[Dict[str, Any]]] = None,
    dry_run_plans: Optional[List[Dict[str, Any]]] = None,
    approval_envelopes: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Link all deterministic Day73-Day75 records into Day76 audit records."""
    decisions = deepcopy(decision_records) if decision_records is not None else run_mock_ai_decision_pipeline()
    plans = deepcopy(dry_run_plans) if dry_run_plans is not None else build_dry_run_plans()
    envelopes = deepcopy(approval_envelopes) if approval_envelopes is not None else build_approval_envelopes()

    decisions_by_scenario = {str(item.get("scenario_id", "")): item for item in decisions}
    plans_by_scenario = {str(item.get("source_scenario_id", "")): item for item in plans}
    envelopes_by_scenario = {str(item.get("scenario_id", "")): item for item in envelopes}
    scenario_ids = sorted(
        scenario_id
        for scenario_id in set(decisions_by_scenario) | set(plans_by_scenario) | set(envelopes_by_scenario)
        if scenario_id
    )
    return [
        build_runtime_audit_record(
            decisions_by_scenario.get(scenario_id),
            plans_by_scenario.get(scenario_id),
            envelopes_by_scenario.get(scenario_id),
            scenario_id,
        )
        for scenario_id in scenario_ids
    ]


def validate_runtime_audit_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day76 audit records."""
    errors: List[str] = []
    if not records:
        errors.append("no runtime audit records were produced.")
        return errors

    for record in records:
        audit_id = record.get("audit_id", "<missing>")
        for field in REQUIRED_AUDIT_FIELDS:
            if field not in record:
                errors.append(f"{audit_id} missing required field: {field}.")
        if record.get("allowed_to_execute") is not False:
            errors.append(f"{audit_id} allowed_to_execute must be false.")
        if record.get("dry_run_only") is not True:
            errors.append(f"{audit_id} dry_run_only must be true.")
        if record.get("execution_unlock_supported") is not False:
            errors.append(f"{audit_id} execution_unlock_supported must be false.")
        if record.get("audit_result") not in AUDIT_RESULTS:
            errors.append(f"{audit_id} has unknown audit_result.")
        chain = record.get("evidence_chain", {})
        expected_complete = bool(
            record.get("decision_id")
            and record.get("dry_run_plan_id")
            and record.get("approval_envelope_id")
        )
        if record.get("evidence_chain_complete") is not expected_complete:
            errors.append(f"{audit_id} evidence_chain_complete is not calculated from all references.")
        if chain.get("complete") is not expected_complete:
            errors.append(f"{audit_id} evidence_chain.complete is not calculated from all references.")
        if record.get("audit_result") == EVIDENCE_GAP and expected_complete:
            errors.append(f"{audit_id} complete evidence chain must not be marked EVIDENCE_GAP.")
        policy = record.get("final_runtime_policy", {})
        if policy.get("review_effect") != "evidence_only_no_execution_unlock":
            errors.append(f"{audit_id} final runtime policy must remain evidence-only.")
        if "unlock execution" not in policy.get("blocked_actions", []):
            errors.append(f"{audit_id} final runtime policy must block execution unlock.")
        invariants = record.get("safety_invariants", {})
        if invariants.get("allowed_to_execute") is not False:
            errors.append(f"{audit_id} invariant allowed_to_execute must be false.")
        if invariants.get("dry_run_only") is not True:
            errors.append(f"{audit_id} invariant dry_run_only must be true.")
        if invariants.get("execution_unlock_supported") is not False:
            errors.append(f"{audit_id} invariant execution_unlock_supported must be false.")

    return errors


def build_runtime_audit_trail_report() -> Dict[str, Any]:
    """Build the Day76 reviewer evidence package."""
    records = build_runtime_audit_records()
    validation_errors = validate_runtime_audit_records(records)
    result_counts = {
        result: sum(1 for record in records if record.get("audit_result") == result)
        for result in sorted(AUDIT_RESULTS)
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            record.get("allowed_to_execute") is False for record in records
        ),
        "dry_run_only_always_true": all(record.get("dry_run_only") is True for record in records),
        "execution_unlock_supported_always_false": all(
            record.get("execution_unlock_supported") is False for record in records
        ),
        "evidence_chain_complete_all_records": all(
            record.get("evidence_chain_complete") is True for record in records
        ),
        "audit_results_do_not_unlock_execution": all(
            record.get("final_runtime_policy", {}).get("review_effect")
            == "evidence_only_no_execution_unlock"
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
        "dashboard_action_endpoint_added",
        "network_configuration_changed",
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in disabled_keys else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day76",
        "title": "Controlled Runtime Audit Trail",
        "task_name": "runtime-audit-trail",
        "execution_mode": EXECUTION_MODE,
        "source_pipeline": (
            "intent_mock_ai_decision_pipeline.run_mock_ai_decision_pipeline -> "
            "intent_dry_run_plan_builder.build_dry_run_plans -> "
            "intent_manual_review_approval_envelope.build_approval_envelopes"
        ),
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "summary": {
            "audit_record_count": len(records),
            "audit_result_counts": result_counts,
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
        "audit_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Mock-only reviewer audit evidence.",
            "Dry-run-only runtime policy evidence.",
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No real AI runtime.",
            "No SSH or device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No dashboard form, POST route, action endpoint, approve button, or execute button.",
            "No reviewer decision or audit result can unlock execution.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day76 links Day73 mock decisions, Day74 dry-run plans, and Day75 "
            "approval envelopes into deterministic reviewer audit evidence. Every "
            "audit record keeps allowed_to_execute=false, dry_run_only=true, and "
            "execution_unlock_supported=false; no audit result, reviewer decision, "
            "dashboard surface, API, SSH, device access, mapped task, config "
            "dependency, or network change can unlock execution."
        ),
    }
