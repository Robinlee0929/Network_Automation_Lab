"""Thin deterministic projection for the canonical Flask Stage-0 journey.

The projection reads committed Day95 fake-adapter evidence and reuses the
existing Day96 parser. It never invokes an adapter, runner, provider, or live
fallback, and rejected scenarios never receive a parsed or useful result.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from intent_readonly_output_parser_prototype import (
    parse_normalized_fake_adapter_result,
)


ALLOWED_SCENARIO_ID = "D95-S02-readonly-interfaces-multiline"
REJECTED_SCENARIO_ID = "D95-S03-reject-write-capable"
EVIDENCE_AVAILABLE = "AVAILABLE"
EVIDENCE_UNAVAILABLE = "UNAVAILABLE"
EVIDENCE_MALFORMED = "MALFORMED"


def load_stage0_useful_result_presentation(report_path: Path) -> Dict[str, Any]:
    """Load committed Day95 evidence and build the bounded Stage-0 view model."""
    try:
        report_text = Path(report_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return _build_unavailable_presentation(
            EVIDENCE_UNAVAILABLE,
            "EVIDENCE_MISSING",
        )
    except UnicodeDecodeError:
        return _build_unavailable_presentation(
            EVIDENCE_MALFORMED,
            "EVIDENCE_INVALID_ENCODING",
        )
    except OSError:
        return _build_unavailable_presentation(
            EVIDENCE_UNAVAILABLE,
            "EVIDENCE_UNREADABLE",
        )

    try:
        report = json.loads(report_text)
    except json.JSONDecodeError:
        return _build_unavailable_presentation(
            EVIDENCE_MALFORMED,
            "EVIDENCE_INVALID_JSON",
        )

    if not isinstance(report, dict):
        return _build_unavailable_presentation(
            EVIDENCE_MALFORMED,
            "EVIDENCE_INVALID_SHAPE",
        )

    return build_stage0_useful_result_presentation(report)


def build_stage0_useful_result_presentation(
    day95_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Project one allowed and one rejected Day95 scenario for presentation."""
    scenarios = {
        scenario.get("scenario_id"): scenario
        for scenario in day95_report.get("scenario_records", [])
        if isinstance(scenario, dict)
    }
    allowed = scenarios.get(ALLOWED_SCENARIO_ID, {})
    rejected = scenarios.get(REJECTED_SCENARIO_ID, {})

    adapter_result = allowed.get("adapter_result")
    parsed_result: Optional[Dict[str, Any]] = None
    useful_result: Optional[Dict[str, Any]] = None
    if _is_safe_allowed_fake_result(allowed, adapter_result):
        parsed_result = parse_normalized_fake_adapter_result(adapter_result)
        useful_result = _project_interface_result(adapter_result, parsed_result)

    return {
        "evidence_status": EVIDENCE_AVAILABLE,
        "reason_code": None,
        "allowed": {
            "request": allowed.get("intent"),
            "reason": allowed.get("reason"),
            "guard_decision": allowed.get("guard_decision"),
            "adapter_invoked": allowed.get("adapter_invoked") is True,
            "result_status": (
                adapter_result.get("result_status")
                if isinstance(adapter_result, dict)
                else None
            ),
            "parsed_result": parsed_result,
            "useful_result": useful_result,
        },
        "rejected": {
            "request": rejected.get("intent"),
            "reason": rejected.get("reason"),
            "guard_decision": rejected.get("guard_decision"),
            "adapter_invoked": rejected.get("adapter_invoked") is True,
            "adapter_result": rejected.get("adapter_result"),
            "parsed_result": None,
            "useful_result": None,
        },
    }


def _build_unavailable_presentation(
    evidence_status: str,
    reason_code: str,
) -> Dict[str, Any]:
    """Return a fixed fail-closed model without evidence-derived results."""
    return {
        "evidence_status": evidence_status,
        "reason_code": reason_code,
        "allowed": {
            "request": None,
            "reason": None,
            "guard_decision": None,
            "adapter_invoked": False,
            "result_status": None,
            "parsed_result": None,
            "useful_result": None,
        },
        "rejected": {
            "request": None,
            "reason": None,
            "guard_decision": None,
            "adapter_invoked": False,
            "adapter_result": None,
            "parsed_result": None,
            "useful_result": None,
        },
    }


def _is_safe_allowed_fake_result(
    scenario: Dict[str, Any],
    adapter_result: Any,
) -> bool:
    if not isinstance(adapter_result, dict):
        return False
    safety = adapter_result.get("safety")
    return (
        scenario.get("guard_decision") == "ALLOW"
        and scenario.get("adapter_invoked") is True
        and adapter_result.get("adapter_type") == "fake"
        and adapter_result.get("result_status") == "FAKE_RESULT_READY"
        and isinstance(safety, dict)
        and safety.get("real_adapter_result_present") is False
        and safety.get("live_execution_result_present") is False
        and safety.get("ssh_used") is False
        and safety.get("device_access_used") is False
        and safety.get("execution_unlocked") is False
    )


def _project_interface_result(
    adapter_result: Dict[str, Any],
    parsed_result: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if parsed_result.get("parser_status") != "PARSED":
        return None

    interface_records: List[Dict[str, str]] = []
    for record in parsed_result.get("parsed_records", []):
        if record.get("record_type") != "text_line":
            return None
        text = record.get("text")
        if not isinstance(text, str):
            return None
        parts = text.rsplit(maxsplit=1)
        if len(parts) != 2:
            return None
        interface_records.append({"name": parts[0], "status": parts[1].lower()})

    if not interface_records:
        return None

    status_counts: Dict[str, int] = {}
    for record in interface_records:
        status = record["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    findings = [
        record.copy()
        for record in interface_records
        if record["status"] != "running"
    ]
    safety = adapter_result["safety"]
    return {
        "label": "Simulated Stage-0 result",
        "record_count": len(interface_records),
        "status_counts": status_counts,
        "findings": findings,
        "source": "Deterministic fake adapter",
        "live_device_contacted": (
            safety["device_access_used"] or safety["live_execution_result_present"]
        ),
    }
