import ast
from pathlib import Path

import intent_controlled_ai_runtime_validator as validator


EXPECTED_KEYS = {
    "valid",
    "risk_level",
    "blocked",
    "blocked_reason",
    "reviewer_required",
    "execution_allowed",
    "next_safe_step",
    "validation_errors",
}

UNSAFE_IMPORTS = {
    "openai",
    "paramiko",
    "netmiko",
    "subprocess",
    "socket",
    "requests",
}


def safe_payload():
    return {
        "user_intent_text": "Generate a dry-run report for interface status review.",
        "requested_operation_type": "report_only",
        "target_scope": "lab_summary",
        "safety_level": "review_required",
        "evidence_required": True,
        "reviewer_required": True,
        "execution_allowed": False,
    }


def test_safe_report_only_payload_is_valid():
    result = validator.validate_controlled_ai_runtime_input(safe_payload())

    assert result["valid"] is True
    assert result["blocked"] is False
    assert result["risk_level"] in {"low", "medium"}
    assert result["reviewer_required"] is True
    assert result["next_safe_step"] == "generate_report_only_review_summary"
    assert result["validation_errors"] == []


def test_safe_payload_still_has_execution_allowed_false():
    result = validator.validate_controlled_ai_runtime_input(safe_payload())

    assert result["execution_allowed"] is False


def test_missing_required_field_is_invalid():
    payload = safe_payload()
    payload.pop("target_scope")

    result = validator.validate_controlled_ai_runtime_input(payload)

    assert result["valid"] is False
    assert result["blocked"] is False
    assert "missing required field: target_scope." in result["validation_errors"]
    assert result["execution_allowed"] is False


def test_wrong_field_type_is_invalid():
    payload = safe_payload()
    payload["evidence_required"] = "true"

    result = validator.validate_controlled_ai_runtime_input(payload)

    assert result["valid"] is False
    assert result["blocked"] is False
    assert "evidence_required must be bool." in result["validation_errors"]
    assert result["execution_allowed"] is False


def test_execution_allowed_true_is_blocked():
    payload = safe_payload()
    payload["execution_allowed"] = True

    result = validator.validate_controlled_ai_runtime_input(payload)

    assert result["valid"] is False
    assert result["blocked"] is True
    assert result["risk_level"] == "high"
    assert result["execution_allowed"] is False


def test_unsafe_intent_texts_are_blocked():
    unsafe_texts = [
        "Run SSH command on router",
        "Apply firewall rule",
        "Change VRRP priority",
        "Reboot device",
        "Connect to OpenAI API",
        "Start voice command mode",
        "Execute mapped task",
        "Use config.json to connect device",
        "Run subprocess command",
        "Push configuration to switch",
    ]

    for intent_text in unsafe_texts:
        payload = safe_payload()
        payload["user_intent_text"] = intent_text
        result = validator.validate_controlled_ai_runtime_input(payload)

        assert result["valid"] is False, intent_text
        assert result["blocked"] is True, intent_text
        assert result["risk_level"] == "high", intent_text
        assert result["execution_allowed"] is False, intent_text
        assert result["blocked_reason"], intent_text


def test_unsafe_imports_are_absent_from_validator_source():
    source_path = Path(validator.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)


def test_blocked_cases_always_return_execution_allowed_false():
    payloads = []
    execution_payload = safe_payload()
    execution_payload["execution_allowed"] = True
    payloads.append(execution_payload)

    unsafe_payload = safe_payload()
    unsafe_payload["user_intent_text"] = "Configure router"
    payloads.append(unsafe_payload)

    blocked_safety_payload = safe_payload()
    blocked_safety_payload["safety_level"] = "blocked"
    payloads.append(blocked_safety_payload)

    for payload in payloads:
        result = validator.validate_controlled_ai_runtime_input(payload)

        assert result["blocked"] is True
        assert result["execution_allowed"] is False


def test_output_always_contains_expected_keys():
    payloads = [
        safe_payload(),
        {},
        "not-a-dict",
    ]

    for payload in payloads:
        result = validator.validate_controlled_ai_runtime_input(payload)
        assert set(result) == EXPECTED_KEYS


def test_validator_is_deterministic_for_same_input():
    payload = safe_payload()

    first = validator.validate_controlled_ai_runtime_input(payload)
    second = validator.validate_controlled_ai_runtime_input(payload)

    assert first == second


def test_unknown_allowed_field_values_are_invalid():
    payload = safe_payload()
    payload["requested_operation_type"] = "mystery"

    result = validator.validate_controlled_ai_runtime_input(payload)

    assert result["valid"] is False
    assert result["blocked"] is False
    assert result["execution_allowed"] is False
    assert any("requested_operation_type must be one of" in error for error in result["validation_errors"])


def test_empty_intent_text_is_invalid():
    payload = safe_payload()
    payload["user_intent_text"] = "   "

    result = validator.validate_controlled_ai_runtime_input(payload)

    assert result["valid"] is False
    assert result["blocked"] is False
    assert result["execution_allowed"] is False
    assert result["validation_errors"] == ["user_intent_text must not be empty."]
