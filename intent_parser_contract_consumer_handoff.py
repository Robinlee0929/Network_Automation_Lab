"""Day108 parser contract consumer handoff.

This module consumes Day107-style reviewer evidence contract records and
produces deterministic reviewer decision handoff records. It is report-only:
it does not execute commands, call adapters or brokers, use SSH, contact live
devices, call OpenAI APIs, unlock approvals, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_reviewer_evidence_contract import (
    SCHEMA_VERSION as DAY107_SCHEMA_VERSION,
    TASK_NAME as DAY107_TASK_NAME,
    build_parser_reviewer_evidence_contract_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
TASK_NAME = "parser-contract-consumer-handoff"
TITLE = "Day108 Parser Contract Consumer / Reviewer Decision Handoff"
PHASE_NAME = "Parser Contract Consumer / Reviewer Decision Handoff"
CONSUMER_HANDOFF_SCHEMA_VERSION = "day108.parser_contract_consumer_handoff.v1"
SOURCE_CONTRACT = "day107.parser_reviewer_evidence_contract"
AUDIT_TYPE = "REPORT_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day108_parser_contract_consumer_handoff.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day108_parser_contract_consumer_handoff.html"

READY_FOR_REVIEW_HANDOFF = "READY_FOR_REVIEW_HANDOFF"
NEEDS_REVIEWER_CLARIFICATION = "NEEDS_REVIEWER_CLARIFICATION"
BLOCKED_UNSAFE_OR_UNSUPPORTED = "BLOCKED_UNSAFE_OR_UNSUPPORTED"
ALLOWED_REVIEWER_DECISIONS = (
    READY_FOR_REVIEW_HANDOFF,
    NEEDS_REVIEWER_CLARIFICATION,
    BLOCKED_UNSAFE_OR_UNSUPPORTED,
)
ACCEPTABLE_EVIDENCE_STATUSES = (
    "ACCEPTABLE_FOR_REVIEW_ONLY_HANDOFF",
    "PASS",
)

SAFETY_INVARIANTS: Dict[str, bool] = {
    "report_only": True,
    "dry_run_only": True,
    "live_execution_allowed": False,
    "ssh_allowed": False,
    "device_connection_allowed": False,
    "command_execution_allowed": False,
    "write_or_config_change_allowed": False,
    "approval_unlock_supported": False,
    "mapped_task_execution_allowed": False,
    "openai_api_used": False,
    "voice_input_used": False,
}

BLOCKING_SAFETY_FLAG_FIELDS = (
    "live_execution_requested",
    "ssh_requested",
    "device_connection_requested",
    "command_execution_requested",
    "write_or_config_change_requested",
    "approval_unlock_requested",
    "mapped_task_execution_requested",
    "openai_api_requested",
    "voice_input_requested",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "source_contract",
    "source_contract_version",
    "consumer_schema_version",
    "intent_id",
    "normalized_intent",
    "parser_supported",
    "reviewer_decision",
    "evidence_status",
    "handoff_ready",
    "handoff_blockers",
    "safety_flags",
    "next_stage_recommendation",
)


@dataclass(frozen=True)
class SourceContractMetadata:
    source_contract: str
    source_contract_version: str
    source_task: str
    source_report_status: str


@dataclass(frozen=True)
class ParserOutcomeSummary:
    intent_id: str
    normalized_intent: str
    parser_supported: bool
    parser_outcome: str


@dataclass(frozen=True)
class ReviewerEvidenceSummary:
    evidence_status: str
    evidence_reference: str
    evidence_summary: str


@dataclass(frozen=True)
class ConsumerValidationResult:
    valid: bool
    errors: List[str]
    blockers: List[str]


@dataclass(frozen=True)
class ReviewerDecisionHandoff:
    handoff_id: str
    source_contract: str
    source_contract_version: str
    consumer_schema_version: str
    intent_id: str
    normalized_intent: str
    parser_supported: bool
    reviewer_decision: str
    evidence_status: str
    handoff_ready: bool
    handoff_blockers: List[str]
    safety_flags: Dict[str, bool]
    next_stage_recommendation: str


def build_source_contract_metadata() -> SourceContractMetadata:
    day107_report = build_parser_reviewer_evidence_contract_report()
    return SourceContractMetadata(
        source_contract=SOURCE_CONTRACT,
        source_contract_version=day107_report["schema_version"],
        source_task=DAY107_TASK_NAME,
        source_report_status=day107_report["overall_status"],
    )


def build_default_safety_flags(**overrides: bool) -> Dict[str, bool]:
    flags = {field: False for field in BLOCKING_SAFETY_FLAG_FIELDS}
    flags.update({field: bool(value) for field, value in overrides.items()})
    return flags


def build_sample_day107_style_records() -> List[Dict[str, Any]]:
    source = build_source_contract_metadata()
    base = {
        "source_contract": source.source_contract,
        "source_contract_version": source.source_contract_version,
        "consumer_schema_version": CONSUMER_HANDOFF_SCHEMA_VERSION,
    }
    return [
        {
            **base,
            "intent_id": "D108-I001",
            "normalized_intent": "review parser evidence contract handoff",
            "parser_supported": True,
            "parser_outcome": "SUPPORTED_REVIEW_ONLY",
            "evidence_status": "ACCEPTABLE_FOR_REVIEW_ONLY_HANDOFF",
            "evidence_reference": "Day107 evidence_chain_complete=true",
            "evidence_summary": "Day107 source contract is complete and locked for review-only continuation.",
            "safety_flags": build_default_safety_flags(),
        },
        {
            **base,
            "intent_id": "D108-I002",
            "normalized_intent": "ambiguous parser evidence request",
            "parser_supported": True,
            "parser_outcome": "SUPPORTED_WITH_REVIEWER_CLARIFICATION",
            "evidence_status": "NEEDS_REVIEWER_CLARIFICATION",
            "evidence_reference": "Day107 contract requires reviewer interpretation before next-stage use",
            "evidence_summary": "Evidence exists but the consumer cannot decide the next reviewer action without clarification.",
            "safety_flags": build_default_safety_flags(),
        },
        {
            **base,
            "intent_id": "D108-I003",
            "normalized_intent": "run mapped task from parser handoff",
            "parser_supported": False,
            "parser_outcome": "UNSUPPORTED_EXECUTION_REQUEST",
            "evidence_status": "BLOCKED_UNSAFE_OR_UNSUPPORTED",
            "evidence_reference": "Day107 live-capable transitions remain blocked",
            "evidence_summary": "The requested consumer action attempts to turn review evidence into execution.",
            "safety_flags": build_default_safety_flags(mapped_task_execution_requested=True),
        },
    ]


def _derive_reviewer_decision(source_record: Dict[str, Any]) -> str:
    safety_flags = source_record.get("safety_flags", {})
    if any(safety_flags.get(field) is True for field in BLOCKING_SAFETY_FLAG_FIELDS):
        return BLOCKED_UNSAFE_OR_UNSUPPORTED
    if source_record.get("parser_supported") is not True:
        return BLOCKED_UNSAFE_OR_UNSUPPORTED
    if source_record.get("evidence_status") in ACCEPTABLE_EVIDENCE_STATUSES:
        return READY_FOR_REVIEW_HANDOFF
    return NEEDS_REVIEWER_CLARIFICATION


def _next_stage_recommendation(reviewer_decision: str) -> str:
    return {
        READY_FOR_REVIEW_HANDOFF: "Continue to reviewer decision handoff as report-only evidence.",
        NEEDS_REVIEWER_CLARIFICATION: "Ask the reviewer to clarify the consumer interpretation before handoff.",
        BLOCKED_UNSAFE_OR_UNSUPPORTED: "Block handoff and keep all execution-capable paths closed.",
    }[reviewer_decision]


def build_handoff_record_from_day107_style_record(
    source_record: Dict[str, Any],
    index: int = 1,
) -> Dict[str, Any]:
    decision = str(source_record.get("reviewer_decision") or _derive_reviewer_decision(source_record))
    handoff = ReviewerDecisionHandoff(
        handoff_id=f"D108-H{index:03d}",
        source_contract=str(source_record.get("source_contract", "")),
        source_contract_version=str(source_record.get("source_contract_version", "")),
        consumer_schema_version=str(source_record.get("consumer_schema_version", CONSUMER_HANDOFF_SCHEMA_VERSION)),
        intent_id=str(source_record.get("intent_id", "")),
        normalized_intent=str(source_record.get("normalized_intent", "")),
        parser_supported=source_record.get("parser_supported") is True,
        reviewer_decision=decision,
        evidence_status=str(source_record.get("evidence_status", "")),
        handoff_ready=False,
        handoff_blockers=[],
        safety_flags=deepcopy(source_record.get("safety_flags", {})),
        next_stage_recommendation=_next_stage_recommendation(decision)
        if decision in ALLOWED_REVIEWER_DECISIONS
        else "Block handoff until reviewer_decision is corrected to the allowed enum.",
    )
    record = asdict(handoff)
    validation = validate_handoff_record(record)
    record["handoff_blockers"] = validation.blockers
    record["handoff_ready"] = validation.valid and decision == READY_FOR_REVIEW_HANDOFF
    record["consumer_validation"] = asdict(
        ConsumerValidationResult(
            valid=record["handoff_ready"],
            errors=validation.errors,
            blockers=validation.blockers,
        )
    )
    return record


def build_handoff_records_from_day107_style_records(
    source_records: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [
        build_handoff_record_from_day107_style_record(record, index)
        for index, record in enumerate(source_records, start=1)
    ]


def validate_handoff_record(record: Dict[str, Any]) -> ConsumerValidationResult:
    errors: List[str] = []
    blockers: List[str] = []

    for field in REQUIRED_HANDOFF_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")
            blockers.append(f"MISSING_{field.upper()}")

    if record.get("source_contract") != SOURCE_CONTRACT:
        errors.append("source_contract is unknown.")
        blockers.append("UNKNOWN_SOURCE_CONTRACT")
    if not record.get("source_contract_version"):
        errors.append("source_contract_version must be non-empty.")
        blockers.append("MISSING_SOURCE_CONTRACT_VERSION")
    if not record.get("consumer_schema_version"):
        errors.append("consumer_schema_version must be non-empty.")
        blockers.append("MISSING_CONSUMER_SCHEMA_VERSION")
    if record.get("reviewer_decision") not in ALLOWED_REVIEWER_DECISIONS:
        errors.append("reviewer_decision is outside the allowed enum.")
        blockers.append("INVALID_REVIEWER_DECISION")
    if (
        record.get("reviewer_decision") == READY_FOR_REVIEW_HANDOFF
        and record.get("evidence_status") not in ACCEPTABLE_EVIDENCE_STATUSES
    ):
        errors.append("evidence_status is not acceptable for ready handoff.")
        blockers.append("UNACCEPTABLE_EVIDENCE_STATUS")

    safety_flags = record.get("safety_flags")
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags must be a dictionary.")
        blockers.append("INVALID_SAFETY_FLAGS")
    else:
        for field in BLOCKING_SAFETY_FLAG_FIELDS:
            if safety_flags.get(field) is True:
                errors.append(f"safety flag blocks handoff: {field}")
                blockers.append(f"SAFETY_FLAG_{field.upper()}")

    if record.get("parser_supported") is not True:
        blockers.append("PARSER_UNSUPPORTED")
    if record.get("reviewer_decision") != READY_FOR_REVIEW_HANDOFF:
        blockers.append("REVIEWER_DECISION_NOT_READY")

    unique_blockers = sorted(set(blockers))
    return ConsumerValidationResult(valid=not errors and not unique_blockers, errors=errors, blockers=unique_blockers)


def validate_day108_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 108:
        errors.append("day must be 108.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("consumer_schema_version") != CONSUMER_HANDOFF_SCHEMA_VERSION:
        errors.append("consumer_schema_version does not match Day108 schema.")
    if report.get("source_contract", {}).get("source_contract") != SOURCE_CONTRACT:
        errors.append("source contract reference must point to Day107.")
    if report.get("source_contract", {}).get("source_contract_version") != DAY107_SCHEMA_VERSION:
        errors.append("source contract version must reference the Day107 schema version.")
    for field, expected in SAFETY_INVARIANTS.items():
        if report.get("safety_invariants", {}).get(field) is not expected:
            errors.append(f"safety_invariants.{field} must be {json.dumps(expected)}.")
    if not report.get("handoff_records"):
        errors.append("handoff_records must be non-empty.")
    for index, record in enumerate(report.get("handoff_records", []), start=1):
        validation = validate_handoff_record(record)
        expected_ready = validation.valid and record.get("reviewer_decision") == READY_FOR_REVIEW_HANDOFF
        if record.get("handoff_ready") is not expected_ready:
            errors.append(f"handoff_records[{index}] handoff_ready does not match validation result.")
    return errors


def build_parser_contract_consumer_handoff_report(
    source_records: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    records = build_handoff_records_from_day107_style_records(
        deepcopy(list(source_records)) if source_records is not None else build_sample_day107_style_records()
    )
    ready_count = sum(1 for record in records if record["handoff_ready"])
    blocked_count = sum(1 for record in records if record["reviewer_decision"] == BLOCKED_UNSAFE_OR_UNSUPPORTED)
    clarification_count = sum(1 for record in records if record["reviewer_decision"] == NEEDS_REVIEWER_CLARIFICATION)
    source = build_source_contract_metadata()
    report = {
        "day": 108,
        "day_id": "Day108",
        "task": TASK_NAME,
        "title": TITLE,
        "phase_name": PHASE_NAME,
        "created_at": CREATED_AT,
        "audit_type": AUDIT_TYPE,
        "consumer_schema_version": CONSUMER_HANDOFF_SCHEMA_VERSION,
        "source_contract": asdict(source),
        "allowed_reviewer_decisions": list(ALLOWED_REVIEWER_DECISIONS),
        "acceptable_evidence_statuses": list(ACCEPTABLE_EVIDENCE_STATUSES),
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "handoff_records": records,
        "summary": {
            "handoff_record_count": len(records),
            "handoff_ready_count": ready_count,
            "clarification_required_count": clarification_count,
            "blocked_count": blocked_count,
            "all_ready_records_are_report_only": all(
                record["handoff_ready"] is False
                or record["reviewer_decision"] == READY_FOR_REVIEW_HANDOFF
                for record in records
            ),
            "unsafe_flags_block_handoff": all(
                record["handoff_ready"] is False
                for record in records
                if any(record["safety_flags"].get(field) is True for field in BLOCKING_SAFETY_FLAG_FIELDS)
            ),
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    report["validation_errors"] = validate_day108_report(report)
    report["overall_status"] = "PASS" if not report["validation_errors"] else "FAIL"
    report["reviewer_handoff_status"] = (
        "CONSUMER_HANDOFF_READY_REPORT_ONLY"
        if report["overall_status"] == "PASS" and ready_count > 0
        else "CONSUMER_HANDOFF_BLOCKED"
    )
    return report


def write_parser_contract_consumer_handoff_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_contract_consumer_handoff_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_contract_consumer_handoff_html(safe_report, html_path)
    return json_path, html_path


def write_parser_contract_consumer_handoff_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(record['handoff_id'])}</code></td>"
        f"<td>{html.escape(record['intent_id'])}</td>"
        f"<td>{html.escape(record['normalized_intent'])}</td>"
        f"<td>{html.escape(record['reviewer_decision'])}</td>"
        f"<td>{html.escape(record['evidence_status'])}</td>"
        f"<td>{html.escape(json.dumps(record['handoff_ready']))}</td>"
        f"<td>{html.escape(', '.join(record['handoff_blockers']) or 'none')}</td>"
        "</tr>"
        for record in report["handoff_records"]
    )
    invariant_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(field)}</code></td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for field, value in report["safety_invariants"].items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .status {{ font-weight: bold; }}
  </style>
</head>
<body>
  <h1>{html.escape(TITLE)}</h1>
  <p><strong>Phase:</strong> {html.escape(report['phase_name'])}</p>
  <p><strong>Status:</strong> <span class="status">{html.escape(report['overall_status'])}</span> / {html.escape(report['reviewer_handoff_status'])}</p>
  <p><strong>Audit type:</strong> <code>{html.escape(report['audit_type'])}</code></p>
  <p><strong>Consumer schema:</strong> <code>{html.escape(report['consumer_schema_version'])}</code></p>
  <p><strong>Source contract:</strong> <code>{html.escape(report['source_contract']['source_contract'])}</code> / <code>{html.escape(report['source_contract']['source_contract_version'])}</code></p>
  <p><strong>Reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <p><strong>Scope:</strong> Day108 consumes the Day107 reviewer evidence contract shape and emits reviewer decision handoff records only. It adds no live execution, SSH, device connection, command execution, approval unlock, mapped task execution, OpenAI API, voice input, or write/config change path.</p>
  <h2>Handoff Records</h2>
  <table>
    <thead><tr><th>Handoff</th><th>Intent</th><th>Normalized Intent</th><th>Reviewer Decision</th><th>Evidence Status</th><th>Ready</th><th>Blockers</th></tr></thead>
    <tbody>{handoff_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Field</th><th>Value</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    report = build_parser_contract_consumer_handoff_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
