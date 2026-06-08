"""Day74 controlled dry-run plan builder.

This module converts deterministic Day73 mock AI decision records into
reviewer-friendly dry-run plans. It does not call AI providers, run commands,
read configuration files, open connections, delegate tasks, or touch devices.
"""

from copy import deepcopy
from typing import Any, Dict, List

from intent_mock_ai_decision_pipeline import (
    BLOCKED_LIVE_ACTION,
    DOCUMENTATION_ONLY,
    INVALID_INPUT_BLOCKED,
    REPORT_ONLY,
    REVIEW_REQUIRED,
    run_mock_ai_decision_pipeline,
)


EXECUTION_MODE = "controlled_dry_run_plan_report_only"

DRY_RUN_READY = "DRY_RUN_READY"
REVIEW_REQUIRED_STATUS = "REVIEW_REQUIRED"
BLOCKED = "BLOCKED"
INVALID_INPUT_BLOCKED_STATUS = "INVALID_INPUT_BLOCKED"

PLAN_STATUSES = {
    DRY_RUN_READY,
    REVIEW_REQUIRED_STATUS,
    BLOCKED,
    INVALID_INPUT_BLOCKED_STATUS,
}

REQUIRED_PLAN_FIELDS = (
    "plan_id",
    "source_scenario_id",
    "decision_label",
    "plan_status",
    "allowed_to_execute",
    "dry_run_only",
    "planned_steps",
    "blocked_steps",
    "reviewer_checks",
    "safety_rationale",
    "evidence",
    "next_reviewer_action",
)

EVIDENCE_REFERENCES = [
    "docs/ai/intent_controlled_ai_runtime_input_validator.md",
    "docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md",
    "docs/ai/intent_mock_ai_decision_pipeline.md",
    "docs/roadmap/day73_mock_ai_decision_pipeline.md",
    "docs/ai/intent_dry_run_plan_builder.md",
    "docs/roadmap/day74_dry_run_plan_builder.md",
]


def _plan_status(decision_label: str) -> str:
    if decision_label in {DOCUMENTATION_ONLY, REPORT_ONLY}:
        return DRY_RUN_READY
    if decision_label == REVIEW_REQUIRED:
        return REVIEW_REQUIRED_STATUS
    if decision_label == BLOCKED_LIVE_ACTION:
        return BLOCKED
    return INVALID_INPUT_BLOCKED_STATUS


def _planned_steps(decision_record: Dict[str, Any], status: str) -> List[str]:
    label = decision_record.get("decision_label", "")
    if status == DRY_RUN_READY and label == DOCUMENTATION_ONLY:
        return [
            "Preview documentation references from the Day72-Day73 evidence chain.",
            "Prepare a reviewer-visible documentation summary.",
            "Record that no mapped task, command, API call, or device access is available.",
        ]
    if status == DRY_RUN_READY and label == REPORT_ONLY:
        return [
            "Preview report-only evidence from the Day73 decision record.",
            "Prepare a reviewer summary of the requested report context.",
            "Record that the plan is a structured preview only and stops before execution.",
        ]
    if status == REVIEW_REQUIRED_STATUS:
        return [
            "Hold the dry-run plan for manual reviewer triage.",
            "List the ambiguous or higher-risk decision context for reviewer inspection.",
            "Stop before any mapped task, live check, command, API call, or device access.",
        ]
    return [
        "Record the blocked decision as reviewer evidence.",
        "Preserve the Day72-Day73 block without proposing execution steps.",
    ]


def _blocked_steps(decision_record: Dict[str, Any], status: str) -> List[str]:
    label = decision_record.get("decision_label", "")
    common_blocks = [
        "Execute mapped runner task.",
        "Call OpenAI API or any AI SDK.",
        "Open SSH, access devices, or change network configuration.",
        "Run arbitrary commands or read config.json.",
    ]
    if status == DRY_RUN_READY:
        return common_blocks
    if status == REVIEW_REQUIRED_STATUS:
        return [
            "Continue without reviewer clarification.",
            "Convert ambiguous intent into an executable action.",
            *common_blocks,
        ]
    if label == BLOCKED_LIVE_ACTION:
        return [
            "Perform live device or network action.",
            "Unlock execution through approval from this plan.",
            *common_blocks,
        ]
    return [
        "Proceed with an invalid input contract.",
        "Repair and execute the request in the same plan.",
        *common_blocks,
    ]


def _reviewer_checks(decision_record: Dict[str, Any], status: str) -> List[str]:
    checks = [
        "Confirm allowed_to_execute is false.",
        "Confirm dry_run_only is true.",
        "Confirm no mapped task execution is present.",
    ]
    if status == DRY_RUN_READY:
        return checks + [
            "Confirm planned steps are preview/report steps only.",
            "Confirm evidence links point to Day72, Day73, and Day74 artifacts.",
        ]
    if status == REVIEW_REQUIRED_STATUS:
        return checks + [
            "Clarify reviewer questions before any later design stage.",
            "Confirm no approval mechanism can unlock execution from this plan.",
        ]
    if status == BLOCKED:
        return checks + [
            "Confirm the live-action block is preserved.",
            "Confirm no device, SSH, VPN, VRRP, firewall, router, or switch change is proposed.",
        ]
    return checks + [
        "Confirm invalid input remains blocked.",
        "Correct the Day72 input contract before any later reviewer-only resubmission.",
    ]


def _safety_rationale(decision_record: Dict[str, Any], status: str) -> str:
    base = (
        "Day74 converts Day73 mock decision records into dry-run plan previews only; "
        "allowed_to_execute is always false and dry_run_only is always true."
    )
    if status == DRY_RUN_READY:
        return base + " Safe documentation/report decisions may be previewed for reviewers without delegating work."
    if status == REVIEW_REQUIRED_STATUS:
        return base + " Reviewer-required decisions stop for human checks before any later design stage."
    if status == BLOCKED:
        return base + " Live device or network action decisions remain blocked and cannot be unlocked by a plan."
    return base + " Invalid input decisions remain blocked until the Day72 contract is corrected."


def _next_reviewer_action(status: str) -> str:
    actions = {
        DRY_RUN_READY: "Review the preview plan and evidence; no execution action is available.",
        REVIEW_REQUIRED_STATUS: "Complete reviewer checks and clarify intent before any later mock-only step.",
        BLOCKED: "Confirm the block and keep live/device access disabled.",
        INVALID_INPUT_BLOCKED_STATUS: "Correct the input contract before any later reviewer-only dry-run plan.",
    }
    return actions[status]


def _evidence(decision_record: Dict[str, Any], status: str) -> List[str]:
    return [
        f"Source Day73 scenario: {decision_record.get('scenario_id', '')}.",
        f"Source Day73 decision label: {decision_record.get('decision_label', '')}.",
        f"Source Day73 allowed_to_execute: {decision_record.get('allowed_to_execute')}.",
        f"Day74 plan status: {status}.",
        "Day74 allowed_to_execute output is fixed false.",
        "Day74 dry_run_only output is fixed true.",
        "No OpenAI API, AI SDK, SSH, device access, mapped task execution, arbitrary command execution, config.json dependency, or network configuration change is used.",
        "Evidence refs: " + ", ".join(EVIDENCE_REFERENCES),
    ]


def build_dry_run_plan_record(decision_record: Dict[str, Any]) -> Dict[str, Any]:
    """Build one reviewer-facing dry-run plan from one Day73 decision record."""
    source = deepcopy(decision_record)
    decision_label = str(source.get("decision_label", ""))
    status = _plan_status(decision_label)
    source_scenario_id = str(source.get("scenario_id", ""))
    return {
        "plan_id": f"day74-plan-{source_scenario_id}",
        "source_scenario_id": source_scenario_id,
        "decision_label": decision_label,
        "plan_status": status,
        "allowed_to_execute": False,
        "dry_run_only": True,
        "planned_steps": _planned_steps(source, status),
        "blocked_steps": _blocked_steps(source, status),
        "reviewer_checks": _reviewer_checks(source, status),
        "safety_rationale": _safety_rationale(source, status),
        "evidence": _evidence(source, status),
        "next_reviewer_action": _next_reviewer_action(status),
    }


def build_dry_run_plans() -> List[Dict[str, Any]]:
    """Convert all deterministic Day73 decisions into Day74 dry-run plans."""
    return [build_dry_run_plan_record(record) for record in run_mock_ai_decision_pipeline()]


def validate_dry_run_plans(plans: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day74 dry-run plans."""
    errors: List[str] = []
    if not plans:
        errors.append("no dry-run plans were produced.")
        return errors

    statuses = {plan.get("plan_status") for plan in plans}
    for expected in PLAN_STATUSES:
        if expected not in statuses:
            errors.append(f"missing plan status: {expected}.")

    for plan in plans:
        plan_id = plan.get("plan_id", "<missing>")
        for field in REQUIRED_PLAN_FIELDS:
            if field not in plan:
                errors.append(f"{plan_id} missing required field: {field}.")
        if plan.get("allowed_to_execute") is not False:
            errors.append(f"{plan_id} allowed_to_execute must be false.")
        if plan.get("dry_run_only") is not True:
            errors.append(f"{plan_id} dry_run_only must be true.")
        if plan.get("plan_status") not in PLAN_STATUSES:
            errors.append(f"{plan_id} has unknown plan_status.")
        if not plan.get("planned_steps"):
            errors.append(f"{plan_id} must include planned steps.")
        if not plan.get("blocked_steps"):
            errors.append(f"{plan_id} must include blocked steps.")
        if plan.get("plan_status") in {REVIEW_REQUIRED_STATUS, BLOCKED, INVALID_INPUT_BLOCKED_STATUS}:
            if not plan.get("reviewer_checks"):
                errors.append(f"{plan_id} must include reviewer checks.")

    return errors


def build_dry_run_plan_builder_report() -> Dict[str, Any]:
    """Build the Day74 reviewer report payload."""
    plans = build_dry_run_plans()
    validation_errors = validate_dry_run_plans(plans)
    status_counts = {
        status: sum(1 for plan in plans if plan.get("plan_status") == status)
        for status in sorted(PLAN_STATUSES)
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            plan.get("allowed_to_execute") is False for plan in plans
        ),
        "dry_run_only_always_true": all(plan.get("dry_run_only") is True for plan in plans),
        "blocked_live_actions_remain_blocked": any(
            plan.get("decision_label") == BLOCKED_LIVE_ACTION
            and plan.get("plan_status") == BLOCKED
            for plan in plans
        ),
        "invalid_inputs_remain_blocked": any(
            plan.get("decision_label") == INVALID_INPUT_BLOCKED
            and plan.get("plan_status") == INVALID_INPUT_BLOCKED_STATUS
            for plan in plans
        ),
        "review_required_has_reviewer_checks": any(
            plan.get("plan_status") == REVIEW_REQUIRED_STATUS
            and bool(plan.get("reviewer_checks"))
            for plan in plans
        ),
        "mapped_task_executed": False,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "config_json_read": False,
    }
    disabled_keys = {
        "mapped_task_executed",
        "openai_api_used",
        "ai_sdk_dependency_used",
        "ssh_used",
        "device_access_used",
        "config_json_read",
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in disabled_keys else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day74",
        "title": "Controlled Dry-run Plan Builder",
        "task_name": "dry-run-plan-builder",
        "execution_mode": EXECUTION_MODE,
        "source_pipeline": "intent_mock_ai_decision_pipeline.run_mock_ai_decision_pipeline",
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "summary": {
            "plan_count": len(plans),
            "plan_status_counts": status_counts,
            "allowed_to_execute_values": sorted(
                {plan.get("allowed_to_execute") for plan in plans}
            ),
            "dry_run_only_values": sorted({plan.get("dry_run_only") for plan in plans}),
        },
        "dry_run_plans": plans,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No real AI runtime.",
            "No SSH or device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No dashboard form, POST route, action endpoint, or approval mechanism.",
            "No router, switch, firewall, VPN, VRRP, or network configuration changes.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day74 converts deterministic Day73 mock decision records into dry-run "
            "plan previews only. Every plan has allowed_to_execute=false and "
            "dry_run_only=true; no AI API, AI SDK, SSH, device access, live "
            "execution, mapped task execution, config.json dependency, dashboard "
            "action surface, approval unlock, or network change is introduced."
        ),
    }
