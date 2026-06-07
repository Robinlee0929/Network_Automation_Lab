"""Day67 offline mock runtime contract validation.

This module validates in-memory runtime result dictionaries only. It does not
read configuration files, execute commands, call APIs, open SSH, or access
devices.
"""

from typing import Any, Dict, List


REQUIRED_FIELDS = (
    "scenario_id",
    "scenario_name",
    "intent_category",
    "execution_mode",
    "safety_category",
    "decision",
    "live_execution_allowed",
    "mapped_task_executed",
    "blocked",
    "reviewer_warning",
    "evidence_references",
)

ALLOWED_EXECUTION_MODES = {"offline_mock", "dry_run_only"}
ALLOWED_SAFETY_CATEGORIES = {
    "documentation_only",
    "report_only",
    "blocked_live_action",
    "needs_manual_review",
}

FORBIDDEN_TRUE_FIELDS = (
    "api_access_used",
    "device_access_used",
    "device_configuration_changed",
    "device_connection_used",
    "external_api_used",
    "live_execution_used",
    "network_change_made",
    "openai_api_used",
    "real_command_executed",
    "ssh_used",
    "voice_control_used",
    "voice_integration_used",
)

FORBIDDEN_TEXT_MARKERS = (
    "api called",
    "api connected",
    "device access used",
    "device configuration changed",
    "live execution allowed",
    "live execution occurred",
    "mapped task executed",
    "network change made",
    "ssh used",
    "voice integration used",
)


def _is_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_evidence_references(result: Dict[str, Any], prefix: str) -> List[str]:
    errors: List[str] = []
    references = result.get("evidence_references")
    if not isinstance(references, list):
        return [f"{prefix}evidence_references must be a list of non-empty strings."]
    if not references:
        errors.append(f"{prefix}evidence_references must contain at least one reference.")
    for index, reference in enumerate(references):
        if not _is_non_empty_text(reference):
            errors.append(
                f"{prefix}evidence_references[{index}] must be a non-empty string."
            )
    return errors


def _validate_forbidden_surface(result: Dict[str, Any], prefix: str) -> List[str]:
    errors: List[str] = []
    for field in FORBIDDEN_TRUE_FIELDS:
        if result.get(field) is True:
            errors.append(f"{prefix}{field} must not be True.")

    record = result.get("mock_execution_record")
    if isinstance(record, dict):
        for field in FORBIDDEN_TRUE_FIELDS:
            if record.get(field) is True:
                errors.append(f"{prefix}mock_execution_record.{field} must not be True.")

    for field in ("decision", "reviewer_warning", "reviewer_note"):
        value = result.get(field)
        if not isinstance(value, str):
            continue
        normalized = value.lower()
        for marker in FORBIDDEN_TEXT_MARKERS:
            if marker in normalized:
                errors.append(f"{prefix}{field} implies forbidden runtime behavior: {marker}.")
    return errors


def validate_runtime_result(result: dict) -> List[str]:
    """Return contract validation errors for one offline mock runtime result."""
    if not isinstance(result, dict):
        return ["result must be a dictionary."]

    errors: List[str] = []
    prefix = ""
    for field in REQUIRED_FIELDS:
        if field not in result:
            errors.append(f"{prefix}missing required field: {field}.")

    execution_mode = result.get("execution_mode")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        errors.append(
            "execution_mode must be one of: "
            + ", ".join(sorted(ALLOWED_EXECUTION_MODES))
            + "."
        )

    safety_category = result.get("safety_category")
    if safety_category not in ALLOWED_SAFETY_CATEGORIES:
        errors.append(
            "safety_category must be one of: "
            + ", ".join(sorted(ALLOWED_SAFETY_CATEGORIES))
            + "."
        )

    if result.get("live_execution_allowed") is not False:
        errors.append("live_execution_allowed must always be False.")
    if result.get("mapped_task_executed") is not False:
        errors.append("mapped_task_executed must always be False.")

    blocked = result.get("blocked")
    if not isinstance(blocked, bool):
        errors.append("blocked must be a boolean.")

    reviewer_warning = result.get("reviewer_warning")
    if not isinstance(reviewer_warning, str):
        errors.append("reviewer_warning must be a string.")

    errors.extend(_validate_evidence_references(result, prefix))

    if safety_category == "blocked_live_action":
        if result.get("blocked") is not True:
            errors.append("blocked_live_action scenarios must have blocked == True.")
        if not _is_non_empty_text(reviewer_warning):
            errors.append(
                "blocked_live_action scenarios must have a non-empty reviewer_warning."
            )
        references = result.get("evidence_references")
        if not isinstance(references, list) or not any(
            _is_non_empty_text(reference) for reference in references
        ):
            errors.append(
                "blocked_live_action scenarios must have at least one evidence reference."
            )

    errors.extend(_validate_forbidden_surface(result, prefix))
    return errors


def validate_runtime_results(results: list) -> List[str]:
    """Return contract validation errors for a list of runtime results."""
    if not isinstance(results, list):
        return ["results must be a list of dictionaries."]

    errors: List[str] = []
    for index, result in enumerate(results):
        result_errors = validate_runtime_result(result)
        errors.extend(f"result[{index}]: {error}" for error in result_errors)
    return errors


def is_contract_valid(result: dict) -> bool:
    """Return True when one result satisfies the Day67 contract."""
    return not validate_runtime_result(result)
