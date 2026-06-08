"""Day73 deterministic mock AI decision pipeline.

This module runs fixed, in-memory reviewer scenarios through the Day72 input
contract validator and then produces mock decision records. It does not call AI
providers, execute tasks, read config files, open connections, or touch devices.
"""

from copy import deepcopy
from typing import Any, Dict, List

from intent_controlled_ai_runtime_validator import validate_controlled_ai_runtime_input


EXECUTION_MODE = "mock_decision_report_only"

DOCUMENTATION_ONLY = "DOCUMENTATION_ONLY"
REPORT_ONLY = "REPORT_ONLY"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
BLOCKED_LIVE_ACTION = "BLOCKED_LIVE_ACTION"
INVALID_INPUT_BLOCKED = "INVALID_INPUT_BLOCKED"

DECISION_LABELS = {
    DOCUMENTATION_ONLY,
    REPORT_ONLY,
    REVIEW_REQUIRED,
    BLOCKED_LIVE_ACTION,
    INVALID_INPUT_BLOCKED,
}

REQUIRED_DECISION_FIELDS = (
    "scenario_id",
    "input_summary",
    "validator_status",
    "mock_decision",
    "decision_label",
    "allowed_to_execute",
    "requires_manual_review",
    "blocked_reason",
    "safety_rationale",
    "evidence",
    "next_reviewer_action",
)

EVIDENCE_REFERENCES = [
    "docs/ai/intent_controlled_ai_runtime_input_validator.md",
    "docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md",
    "docs/ai/intent_mock_ai_decision_pipeline.md",
    "docs/roadmap/day73_mock_ai_decision_pipeline.md",
]

SAMPLE_INPUT_SCENARIOS = [
    {
        "scenario_id": "day73-documentation-only",
        "scenario_type": "documentation",
        "payload": {
            "user_intent_text": "Explain the AI intent reviewer safety boundary.",
            "requested_operation_type": "documentation_only",
            "target_scope": "documentation",
            "safety_level": "documentation_only",
            "evidence_required": False,
            "reviewer_required": False,
            "execution_allowed": False,
        },
    },
    {
        "scenario_id": "day73-report-only",
        "scenario_type": "report",
        "payload": {
            "user_intent_text": "Generate a reviewer summary for local AI intent reports.",
            "requested_operation_type": "report_only",
            "target_scope": "lab_summary",
            "safety_level": "report_only",
            "evidence_required": True,
            "reviewer_required": True,
            "execution_allowed": False,
        },
    },
    {
        "scenario_id": "day73-ambiguous-review",
        "scenario_type": "ambiguous",
        "payload": {
            "user_intent_text": "Review an ambiguous automation request and list reviewer questions.",
            "requested_operation_type": "reviewer_summary",
            "target_scope": "ai_intent_reviewer",
            "safety_level": "review_required",
            "evidence_required": True,
            "reviewer_required": True,
            "execution_allowed": False,
        },
    },
    {
        "scenario_id": "day73-live-action-blocked",
        "scenario_type": "live_action",
        "payload": {
            "user_intent_text": "Change firewall rule on device now.",
            "requested_operation_type": "report_only",
            "target_scope": "lab_summary",
            "safety_level": "report_only",
            "evidence_required": True,
            "reviewer_required": True,
            "execution_allowed": False,
        },
    },
    {
        "scenario_id": "day73-invalid-input",
        "scenario_type": "invalid",
        "payload": {
            "user_intent_text": "Summarize reviewer reports with an incomplete payload.",
            "requested_operation_type": "report_only",
            "safety_level": "report_only",
            "evidence_required": True,
            "reviewer_required": True,
            "execution_allowed": False,
        },
    },
]


def sample_day73_inputs() -> List[Dict[str, Any]]:
    """Return a copy of the fixed Day73 validator-compatible scenarios."""
    return deepcopy(SAMPLE_INPUT_SCENARIOS)


def _validator_status(validation: Dict[str, Any]) -> str:
    if validation.get("blocked") is True:
        return "BLOCKED"
    if validation.get("valid") is True:
        return "VALID"
    return "INVALID"


def _input_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_intent_text": payload.get("user_intent_text", ""),
        "requested_operation_type": payload.get("requested_operation_type", "<missing>"),
        "target_scope": payload.get("target_scope", "<missing>"),
        "safety_level": payload.get("safety_level", "<missing>"),
        "evidence_required": payload.get("evidence_required", "<missing>"),
        "reviewer_required": payload.get("reviewer_required", "<missing>"),
        "execution_allowed": payload.get("execution_allowed", "<missing>"),
    }


def _decision_label(scenario: Dict[str, Any], validation: Dict[str, Any]) -> str:
    scenario_type = scenario.get("scenario_type", "")
    payload = scenario.get("payload", {})
    if validation.get("blocked") is True and scenario_type == "live_action":
        return BLOCKED_LIVE_ACTION
    if validation.get("valid") is not True:
        return INVALID_INPUT_BLOCKED
    if scenario_type == "ambiguous" or payload.get("safety_level") == "review_required":
        return REVIEW_REQUIRED
    if payload.get("requested_operation_type") == "documentation_only":
        return DOCUMENTATION_ONLY
    return REPORT_ONLY


def _blocked_reason(label: str, validation: Dict[str, Any]) -> str:
    if label == BLOCKED_LIVE_ACTION:
        return (
            validation.get("blocked_reason")
            or "live device or network action is blocked before decision output."
        )
    if label == INVALID_INPUT_BLOCKED:
        return (
            validation.get("blocked_reason")
            or "input did not pass the Day72 controlled runtime contract."
        )
    return ""


def _mock_decision(label: str) -> str:
    decisions = {
        DOCUMENTATION_ONLY: "prepare_documentation_reference_for_reviewer",
        REPORT_ONLY: "prepare_report_only_reviewer_summary",
        REVIEW_REQUIRED: "stop_for_manual_reviewer_triage",
        BLOCKED_LIVE_ACTION: "block_live_action_and_record_evidence",
        INVALID_INPUT_BLOCKED: "block_invalid_input_and_request_contract_fix",
    }
    return decisions[label]


def _next_reviewer_action(label: str) -> str:
    actions = {
        DOCUMENTATION_ONLY: "Review documentation references; no execution is available.",
        REPORT_ONLY: "Review the generated report evidence; no mapped task is available.",
        REVIEW_REQUIRED: "Clarify intent and risk before any later mock decision stage.",
        BLOCKED_LIVE_ACTION: "Confirm the live-action block and keep device access disabled.",
        INVALID_INPUT_BLOCKED: "Correct the input contract before resubmitting for review.",
    }
    return actions[label]


def _safety_rationale(label: str, validation: Dict[str, Any]) -> str:
    base = "Day73 is a mock decision stage after Day72 validation; allowed_to_execute is always false."
    if label == DOCUMENTATION_ONLY:
        return base + " Documentation-only input can be reviewer-ready without delegating work."
    if label == REPORT_ONLY:
        return base + " Report-only input can be summarized for review without running a mapped task."
    if label == REVIEW_REQUIRED:
        return base + " Ambiguous or higher-risk input stops for manual reviewer triage."
    if label == BLOCKED_LIVE_ACTION:
        return base + " Live device or network action is blocked before any execution path."
    return base + f" Invalid input is blocked because Day72 returned {_validator_status(validation)}."


def _evidence(scenario: Dict[str, Any], validation: Dict[str, Any], label: str) -> List[str]:
    errors = validation.get("validation_errors", [])
    return [
        f"Day72 validator status: {_validator_status(validation)}.",
        f"Day72 execution_allowed output: {validation.get('execution_allowed')}.",
        f"Day73 decision label: {label}.",
        "Day73 allowed_to_execute output is fixed false.",
        "No OpenAI API, AI SDK, SSH, device access, mapped task execution, or config.json dependency is used.",
        "Evidence refs: " + ", ".join(EVIDENCE_REFERENCES),
        "Validation errors: " + ("; ".join(str(error) for error in errors) if errors else "none."),
        f"Scenario type: {scenario.get('scenario_type', '')}.",
    ]


def build_decision_record(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Validate one fixed input and produce one mock decision record."""
    payload = deepcopy(scenario.get("payload", {}))
    validation = validate_controlled_ai_runtime_input(payload)
    label = _decision_label(scenario, validation)
    requires_manual_review = label in {
        REVIEW_REQUIRED,
        BLOCKED_LIVE_ACTION,
        INVALID_INPUT_BLOCKED,
    } or validation.get("reviewer_required") is True
    return {
        "scenario_id": scenario.get("scenario_id", ""),
        "input_summary": _input_summary(payload),
        "validator_status": _validator_status(validation),
        "validator_result": validation,
        "mock_decision": _mock_decision(label),
        "decision_label": label,
        "allowed_to_execute": False,
        "requires_manual_review": requires_manual_review,
        "blocked_reason": _blocked_reason(label, validation),
        "safety_rationale": _safety_rationale(label, validation),
        "evidence": _evidence(scenario, validation, label),
        "next_reviewer_action": _next_reviewer_action(label),
    }


def run_mock_ai_decision_pipeline() -> List[Dict[str, Any]]:
    """Run all fixed Day73 mock decisions."""
    return [build_decision_record(scenario) for scenario in sample_day73_inputs()]


def validate_decision_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day73 decision records."""
    errors: List[str] = []
    if not records:
        errors.append("no decision records were produced.")
        return errors

    labels = {record.get("decision_label") for record in records}
    for expected in DECISION_LABELS:
        if expected not in labels:
            errors.append(f"missing decision label: {expected}.")

    for record in records:
        scenario_id = record.get("scenario_id", "<missing>")
        for field in REQUIRED_DECISION_FIELDS:
            if field not in record:
                errors.append(f"{scenario_id} missing required field: {field}.")
        if record.get("allowed_to_execute") is not False:
            errors.append(f"{scenario_id} allowed_to_execute must be false.")
        if record.get("decision_label") not in DECISION_LABELS:
            errors.append(f"{scenario_id} has unknown decision_label.")
        if record.get("decision_label") in {BLOCKED_LIVE_ACTION, INVALID_INPUT_BLOCKED}:
            if not str(record.get("blocked_reason", "")).strip():
                errors.append(f"{scenario_id} must include a blocked reason.")
        if record.get("decision_label") == REVIEW_REQUIRED:
            if record.get("requires_manual_review") is not True:
                errors.append(f"{scenario_id} must require manual review.")

    return errors


def build_mock_ai_decision_pipeline_report() -> Dict[str, Any]:
    """Build the Day73 reviewer report payload."""
    records = run_mock_ai_decision_pipeline()
    validation_errors = validate_decision_records(records)
    label_counts = {
        label: sum(1 for record in records if record.get("decision_label") == label)
        for label in sorted(DECISION_LABELS)
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            record.get("allowed_to_execute") is False for record in records
        ),
        "live_action_requests_blocked": any(
            record.get("decision_label") == BLOCKED_LIVE_ACTION for record in records
        ),
        "invalid_inputs_blocked": any(
            record.get("decision_label") == INVALID_INPUT_BLOCKED for record in records
        ),
        "manual_review_required_for_ambiguous": any(
            record.get("decision_label") == REVIEW_REQUIRED
            and record.get("requires_manual_review") is True
            for record in records
        ),
        "mapped_task_executed": False,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "config_json_read": False,
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in {
            "mapped_task_executed",
            "openai_api_used",
            "ai_sdk_dependency_used",
            "ssh_used",
            "device_access_used",
            "config_json_read",
        } else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day73",
        "title": "Mock AI Decision Pipeline",
        "task_name": "mock-ai-decision-pipeline",
        "execution_mode": EXECUTION_MODE,
        "source_validator": "intent_controlled_ai_runtime_validator.validate_controlled_ai_runtime_input",
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "summary": {
            "scenario_count": len(records),
            "decision_label_counts": label_counts,
            "allowed_to_execute_values": sorted(
                {record.get("allowed_to_execute") for record in records}
            ),
        },
        "decision_records": records,
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
            "No dashboard POST/action endpoint.",
            "No router, switch, firewall, VPN, VRRP, or network configuration changes.",
        ],
        "evidence_links_or_doc_refs": list(EVIDENCE_REFERENCES),
        "final_safety_statement": (
            "Day73 runs deterministic mock decisions after Day72 validation only. "
            "Every decision record has allowed_to_execute=false; no AI API, SSH, "
            "device access, live execution, mapped task execution, config.json "
            "dependency, dashboard action surface, or network change is introduced."
        ),
    }
