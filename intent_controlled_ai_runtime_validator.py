"""Day72 controlled AI runtime input contract validation.

This module validates in-memory intent payload dictionaries only. It does not
invoke models, run commands, read configuration files, open connections, or
delegate work to any runtime path.
"""

from typing import Any, Dict, List


REQUIRED_FIELDS = (
    "user_intent_text",
    "requested_operation_type",
    "target_scope",
    "safety_level",
    "evidence_required",
    "reviewer_required",
    "execution_allowed",
)

FIELD_TYPES = {
    "user_intent_text": str,
    "requested_operation_type": str,
    "target_scope": str,
    "safety_level": str,
    "evidence_required": bool,
    "reviewer_required": bool,
    "execution_allowed": bool,
}

ALLOWED_OPERATION_TYPES = {
    "documentation_only",
    "report_only",
    "dry_run_review",
    "reviewer_summary",
}

ALLOWED_TARGET_SCOPES = {
    "lab_summary",
    "ai_intent_reviewer",
    "offline_mock_runtime",
    "documentation",
    "portfolio_evidence",
}

ALLOWED_SAFETY_LEVELS = {
    "documentation_only",
    "report_only",
    "review_required",
    "blocked",
}

UNSAFE_OPERATION_TYPES = {
    "apply",
    "configure",
    "execute",
    "live",
    "reboot",
    "run",
    "ssh",
}

UNSAFE_TARGET_SCOPES = {
    "device",
    "firewall",
    "router",
    "switch",
    "vpn",
    "vrrp",
}

UNSAFE_SAFETY_LEVELS = {
    "device_access",
    "execute",
    "live_execution",
    "production",
}

UNSAFE_TEXT_PATTERNS = (
    "run ssh command",
    "apply firewall rule",
    "change vrrp priority",
    "reboot device",
    "connect to openai api",
    "start voice command mode",
    "execute mapped task",
    "use config.json",
    "connect device",
    "run subprocess command",
    "push configuration",
    "push config",
    "configure router",
    "configure switch",
    "change firewall",
    "live execution",
    "device access",
    "api key",
    "secret",
    "subprocess",
    "requests",
    "paramiko",
    "netmiko",
    "openai",
    "socket",
    "ssh",
)

EXPECTED_OUTPUT_KEYS = (
    "valid",
    "risk_level",
    "blocked",
    "blocked_reason",
    "reviewer_required",
    "execution_allowed",
    "next_safe_step",
    "validation_errors",
)


def _base_result() -> Dict[str, Any]:
    return {
        "valid": False,
        "risk_level": "medium",
        "blocked": False,
        "blocked_reason": "",
        "reviewer_required": True,
        "execution_allowed": False,
        "next_safe_step": "correct_payload_and_resubmit_for_review",
        "validation_errors": [],
    }


def _contains_unsafe_marker(value: str, markers: set) -> bool:
    normalized = value.strip().lower()
    tokens = {
        normalized,
        *normalized.replace("-", "_").replace(" ", "_").split("_"),
    }
    return any(marker in normalized or marker in tokens for marker in markers)


def _unsafe_text_patterns(intent_text: str) -> List[str]:
    normalized = " ".join(intent_text.lower().split())
    return [pattern for pattern in UNSAFE_TEXT_PATTERNS if pattern in normalized]


def _finalize_blocked(
    result: Dict[str, Any],
    reason: str,
    errors: List[str],
    reviewer_required: bool = True,
) -> Dict[str, Any]:
    result["valid"] = False
    result["risk_level"] = "high"
    result["blocked"] = True
    result["blocked_reason"] = reason
    result["reviewer_required"] = reviewer_required
    result["execution_allowed"] = False
    result["next_safe_step"] = "block_and_request_reviewer_triage"
    result["validation_errors"] = errors
    return result


def validate_controlled_ai_runtime_input(payload: dict) -> dict:
    """Validate a future controlled AI runtime intent payload.

    The validator is deterministic, standard-library-only, and report-only. It
    never permits execution and only returns reviewer-facing validation state.
    """
    result = _base_result()

    if not isinstance(payload, dict):
        result["validation_errors"] = ["payload must be a dictionary."]
        result["blocked_reason"] = "payload is not a valid input contract dictionary."
        return result

    errors: List[str] = []
    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    for field in missing_fields:
        errors.append(f"missing required field: {field}.")

    for field in REQUIRED_FIELDS:
        if field not in payload:
            continue
        expected_type = FIELD_TYPES[field]
        value = payload[field]
        if type(value) is not expected_type:
            errors.append(f"{field} must be {expected_type.__name__}.")

    reviewer_required = payload.get("reviewer_required")
    if isinstance(reviewer_required, bool):
        result["reviewer_required"] = reviewer_required

    if payload.get("execution_allowed") is True:
        errors.append("execution_allowed must always be False.")
        return _finalize_blocked(
            result,
            "execution_allowed true is outside the Day72 safety boundary.",
            errors,
        )

    if errors:
        result["validation_errors"] = errors
        result["blocked_reason"] = "payload failed input contract validation."
        result["reviewer_required"] = True
        return result

    user_intent_text = payload["user_intent_text"]
    requested_operation_type = payload["requested_operation_type"]
    target_scope = payload["target_scope"]
    safety_level = payload["safety_level"]

    if not user_intent_text.strip():
        result["validation_errors"] = ["user_intent_text must not be empty."]
        result["blocked_reason"] = "payload failed input contract validation."
        result["reviewer_required"] = True
        return result

    if requested_operation_type not in ALLOWED_OPERATION_TYPES:
        errors.append(
            "requested_operation_type must be one of: "
            + ", ".join(sorted(ALLOWED_OPERATION_TYPES))
            + "."
        )
    if target_scope not in ALLOWED_TARGET_SCOPES:
        errors.append(
            "target_scope must be one of: "
            + ", ".join(sorted(ALLOWED_TARGET_SCOPES))
            + "."
        )
    if safety_level not in ALLOWED_SAFETY_LEVELS:
        errors.append(
            "safety_level must be one of: "
            + ", ".join(sorted(ALLOWED_SAFETY_LEVELS))
            + "."
        )

    unsafe_patterns = _unsafe_text_patterns(user_intent_text)
    unsafe_contract_fields: List[str] = []
    if _contains_unsafe_marker(requested_operation_type, UNSAFE_OPERATION_TYPES):
        unsafe_contract_fields.append("requested_operation_type")
    if _contains_unsafe_marker(target_scope, UNSAFE_TARGET_SCOPES):
        unsafe_contract_fields.append("target_scope")
    if _contains_unsafe_marker(safety_level, UNSAFE_SAFETY_LEVELS):
        unsafe_contract_fields.append("safety_level")

    if unsafe_patterns or unsafe_contract_fields or safety_level == "blocked":
        if unsafe_patterns:
            errors.append(
                "user_intent_text contains blocked pattern(s): "
                + ", ".join(sorted(unsafe_patterns))
                + "."
            )
        if unsafe_contract_fields:
            errors.append(
                "unsafe contract field value(s): "
                + ", ".join(sorted(unsafe_contract_fields))
                + "."
            )
        if safety_level == "blocked":
            errors.append("safety_level blocked requires reviewer triage.")
        return _finalize_blocked(
            result,
            "unsafe intent contract content is blocked before runtime decision paths.",
            errors,
        )

    if errors:
        result["validation_errors"] = errors
        result["blocked_reason"] = "payload failed input contract validation."
        result["reviewer_required"] = True
        return result

    reviewer_required = payload["reviewer_required"] or safety_level == "review_required"
    result["valid"] = True
    result["risk_level"] = "medium" if reviewer_required or payload["evidence_required"] else "low"
    result["blocked"] = False
    result["blocked_reason"] = ""
    result["reviewer_required"] = reviewer_required
    result["execution_allowed"] = False
    result["next_safe_step"] = "generate_report_only_review_summary"
    result["validation_errors"] = []
    return result
