"""Day75 manual review approval envelope simulation.

This module wraps Day74 dry-run plans in deterministic reviewer sign-off
records. It is mock-only and dry-run-only: reviewer decisions are evidence
labels, not execution approvals.
"""

from copy import deepcopy
from typing import Any, Dict, List

from intent_dry_run_plan_builder import (
    BLOCKED,
    DRY_RUN_READY,
    INVALID_INPUT_BLOCKED_STATUS,
    REVIEW_REQUIRED_STATUS,
    build_dry_run_plans,
)


EXECUTION_MODE = "manual_review_approval_envelope_mock_dry_run_only"
CREATED_AT = "2026-06-08T00:00:00Z"

APPROVED_FOR_RECORD_ONLY = "approved_for_record_only"
REJECTED_FOR_REVIEW_GAP = "rejected_for_review_gap"
REQUIRES_MANUAL_FOLLOW_UP = "requires_manual_follow_up"
BLOCKED_LIVE_ACTION = "blocked_live_action"

REVIEWER_DECISIONS = {
    APPROVED_FOR_RECORD_ONLY,
    REJECTED_FOR_REVIEW_GAP,
    REQUIRES_MANUAL_FOLLOW_UP,
    BLOCKED_LIVE_ACTION,
}

REQUIRED_ENVELOPE_FIELDS = (
    "envelope_id",
    "scenario_id",
    "source_decision_id",
    "dry_run_plan_id",
    "reviewer_signoff_state",
    "reviewer_decision",
    "required_review_items",
    "safety_invariants",
    "execution_policy",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "created_at",
)

EVIDENCE_REFERENCES = [
    "docs/ai/intent_dry_run_plan_builder.md",
    "docs/roadmap/day74_dry_run_plan_builder.md",
    "docs/ai/intent_manual_review_approval_envelope.md",
    "docs/roadmap/day75_manual_review_approval_envelope.md",
]


def _reviewer_decision(plan: Dict[str, Any]) -> str:
    status = plan.get("plan_status")
    if status == DRY_RUN_READY:
        return APPROVED_FOR_RECORD_ONLY
    if status == REVIEW_REQUIRED_STATUS:
        return REQUIRES_MANUAL_FOLLOW_UP
    if status == BLOCKED:
        return BLOCKED_LIVE_ACTION
    return REJECTED_FOR_REVIEW_GAP


def _reviewer_signoff_state(decision: str) -> str:
    states = {
        APPROVED_FOR_RECORD_ONLY: "SIGNED_RECORD_ONLY",
        REJECTED_FOR_REVIEW_GAP: "REJECTED_REVIEW_GAP",
        REQUIRES_MANUAL_FOLLOW_UP: "PENDING_MANUAL_FOLLOW_UP",
        BLOCKED_LIVE_ACTION: "BLOCKED_NO_LIVE_ACTION",
    }
    return states[decision]


def _required_review_items(plan: Dict[str, Any], decision: str) -> List[str]:
    common_items = [
        "Confirm allowed_to_execute is false.",
        "Confirm dry_run_only is true.",
        "Confirm execution_unlock_supported is false.",
        "Confirm the envelope records reviewer evidence only.",
    ]
    if decision == APPROVED_FOR_RECORD_ONLY:
        return common_items + [
            "Confirm the Day74 plan is documentation/report preview only.",
            "Record sign-off for audit evidence without enabling any action.",
        ]
    if decision == REQUIRES_MANUAL_FOLLOW_UP:
        return common_items + [
            "Resolve reviewer questions outside the dashboard action surface.",
            "Keep ambiguous intent stopped before any command, API call, SSH, or device access.",
        ]
    if decision == BLOCKED_LIVE_ACTION:
        return common_items + [
            "Confirm live device or network action remains blocked.",
            "Confirm no approval envelope can override the live-action block.",
        ]
    return common_items + [
        "Correct the invalid or incomplete review input before any later mock-only resubmission.",
        "Confirm no rejected review gap can become an execution approval.",
    ]


def _safety_invariants(plan: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_allowed_to_execute": plan.get("allowed_to_execute"),
        "source_dry_run_only": plan.get("dry_run_only"),
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "mock_only": True,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "mapped_task_executed": False,
        "arbitrary_command_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }


def _execution_policy(decision: str) -> Dict[str, Any]:
    return {
        "mode": EXECUTION_MODE,
        "reviewer_decision": decision,
        "allowed_actions": ["record_review_evidence"],
        "blocked_actions": [
            "execute mapped task",
            "call OpenAI API or AI SDK",
            "open SSH or access a device",
            "run arbitrary commands",
            "read config.json",
            "submit dashboard approval",
            "unlock execution",
            "change router, switch, firewall, VPN, VRRP, or network configuration",
        ],
        "approval_effect": "record_only_no_execution_unlock",
    }


def build_approval_envelope_record(plan_record: Dict[str, Any]) -> Dict[str, Any]:
    """Build one deterministic reviewer sign-off envelope for a Day74 plan."""
    plan = deepcopy(plan_record)
    scenario_id = str(plan.get("source_scenario_id", ""))
    decision = _reviewer_decision(plan)
    return {
        "envelope_id": f"day75-envelope-{scenario_id}",
        "scenario_id": scenario_id,
        "source_decision_id": f"day73-decision-{scenario_id}",
        "dry_run_plan_id": str(plan.get("plan_id", "")),
        "reviewer_signoff_state": _reviewer_signoff_state(decision),
        "reviewer_decision": decision,
        "required_review_items": _required_review_items(plan, decision),
        "safety_invariants": _safety_invariants(plan),
        "execution_policy": _execution_policy(decision),
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "created_at": CREATED_AT,
    }


def build_approval_envelopes() -> List[Dict[str, Any]]:
    """Wrap all deterministic Day74 dry-run plans in Day75 approval envelopes."""
    return [build_approval_envelope_record(plan) for plan in build_dry_run_plans()]


def validate_approval_envelopes(envelopes: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day75 envelopes."""
    errors: List[str] = []
    if not envelopes:
        errors.append("no approval envelopes were produced.")
        return errors

    decisions = {envelope.get("reviewer_decision") for envelope in envelopes}
    for expected in REVIEWER_DECISIONS:
        if expected not in decisions:
            errors.append(f"missing reviewer decision: {expected}.")

    for envelope in envelopes:
        envelope_id = envelope.get("envelope_id", "<missing>")
        for field in REQUIRED_ENVELOPE_FIELDS:
            if field not in envelope:
                errors.append(f"{envelope_id} missing required field: {field}.")
        if envelope.get("allowed_to_execute") is not False:
            errors.append(f"{envelope_id} allowed_to_execute must be false.")
        if envelope.get("dry_run_only") is not True:
            errors.append(f"{envelope_id} dry_run_only must be true.")
        if envelope.get("execution_unlock_supported") is not False:
            errors.append(f"{envelope_id} execution_unlock_supported must be false.")
        if envelope.get("reviewer_decision") not in REVIEWER_DECISIONS:
            errors.append(f"{envelope_id} has unknown reviewer_decision.")
        if not envelope.get("required_review_items"):
            errors.append(f"{envelope_id} must include required review items.")
        invariants = envelope.get("safety_invariants", {})
        if invariants.get("allowed_to_execute") is not False:
            errors.append(f"{envelope_id} invariant allowed_to_execute must be false.")
        if invariants.get("dry_run_only") is not True:
            errors.append(f"{envelope_id} invariant dry_run_only must be true.")
        if invariants.get("execution_unlock_supported") is not False:
            errors.append(
                f"{envelope_id} invariant execution_unlock_supported must be false."
            )
        policy = envelope.get("execution_policy", {})
        if policy.get("approval_effect") != "record_only_no_execution_unlock":
            errors.append(f"{envelope_id} approval effect must remain record-only.")

    return errors


def build_manual_review_approval_envelope_report() -> Dict[str, Any]:
    """Build the Day75 reviewer sign-off envelope report payload."""
    envelopes = build_approval_envelopes()
    validation_errors = validate_approval_envelopes(envelopes)
    decision_counts = {
        decision: sum(1 for envelope in envelopes if envelope.get("reviewer_decision") == decision)
        for decision in sorted(REVIEWER_DECISIONS)
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            envelope.get("allowed_to_execute") is False for envelope in envelopes
        ),
        "dry_run_only_always_true": all(
            envelope.get("dry_run_only") is True for envelope in envelopes
        ),
        "execution_unlock_supported_always_false": all(
            envelope.get("execution_unlock_supported") is False for envelope in envelopes
        ),
        "approval_states_do_not_unlock_execution": all(
            envelope.get("execution_policy", {}).get("approval_effect")
            == "record_only_no_execution_unlock"
            for envelope in envelopes
        ),
        "mapped_task_executed": False,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
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
        "day": "Day75",
        "title": "Manual Review Approval Envelope",
        "task_name": "manual-review-approval-envelope",
        "execution_mode": EXECUTION_MODE,
        "source_pipeline": "intent_dry_run_plan_builder.build_dry_run_plans",
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "summary": {
            "approval_envelope_count": len(envelopes),
            "reviewer_decision_counts": decision_counts,
            "allowed_to_execute_values": sorted(
                {envelope.get("allowed_to_execute") for envelope in envelopes}
            ),
            "dry_run_only_values": sorted(
                {envelope.get("dry_run_only") for envelope in envelopes}
            ),
            "execution_unlock_supported_values": sorted(
                {envelope.get("execution_unlock_supported") for envelope in envelopes}
            ),
        },
        "approval_envelopes": envelopes,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Mock-only reviewer sign-off simulation.",
            "Dry-run-only record generation.",
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No real AI runtime.",
            "No SSH or device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No dashboard form, POST route, action endpoint, approve button, or execute button.",
            "No approval or reviewer decision can unlock execution.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day75 wraps deterministic Day74 dry-run plans in mock reviewer sign-off "
            "envelopes for record-only approval evidence. Every envelope keeps "
            "allowed_to_execute=false, dry_run_only=true, and "
            "execution_unlock_supported=false; no approval state, reviewer decision, "
            "dashboard surface, API, SSH, device access, mapped task, config dependency, "
            "or network change can unlock execution."
        ),
    }
