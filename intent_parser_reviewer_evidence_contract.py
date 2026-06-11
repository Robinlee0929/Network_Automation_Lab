"""Day107 parser reviewer evidence contract consolidation.

This module consolidates Day96-Day105 parser evidence into one deterministic,
report-only reviewer contract. It does not execute adapters, brokers, SSH,
network commands, external APIs, voice runtimes, or configuration changes.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


CREATED_AT = "2026-06-11T00:00:00+08:00"
TASK_NAME = "parser-reviewer-evidence-contract"
TITLE = "Day107 Parser Reviewer Evidence Contract Consolidation"
PHASE_NAME = "Parser Reviewer Evidence Contract Consolidation"
SCHEMA_VERSION = "day107.parser_reviewer_evidence_contract.v1"
AUDIT_TYPE = "REPORT_ONLY"
EVIDENCE_SCOPE = "Day96-Day105"
REPORT_JSON = Path("reports") / "lab-summary" / "day107_parser_reviewer_evidence_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day107_parser_reviewer_evidence_contract.html"

REQUIRED_DAYS = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105]
REQUIRED_ITEM_FIELDS = (
    "day",
    "name",
    "stage_status",
    "scope",
    "execution_allowed",
    "safety_boundary_locked",
    "reviewer_acceptance_relevance",
)
LOCKED_PERMISSION_FLAGS = (
    "live_execution_allowed",
    "ssh_allowed",
    "device_connection_allowed",
    "config_mutation_allowed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "adapter_invocation_allowed",
    "rejected_intent_execution_allowed",
)
LIVE_ACCEPTANCE_FLAG = "accepted_for_live_execution"
ALL_NO_EXECUTION_FLAGS = LOCKED_PERMISSION_FLAGS + (LIVE_ACCEPTANCE_FLAG,)

PASS_RECOMMENDATION = "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION"
WARN_RECOMMENDATION = "PARSER_REVIEWER_EVIDENCE_CONTRACT_NEEDS_GAP_REVIEW"
FAIL_RECOMMENDATION = "PARSER_REVIEWER_EVIDENCE_CONTRACT_REJECTED_FOR_SAFETY_RISK"


def build_default_evidence_items() -> List[Dict[str, Any]]:
    """Return the fixed Day96-Day105 evidence contract items."""
    specs = [
        (
            96,
            "Read-only Output Parser Prototype",
            "COMPLETE",
            "PARSER_ONLY",
            "Established parser-only handling for normalized fake adapter output without live fallback.",
        ),
        (
            97,
            "Parser Evidence Quality",
            "COMPLETE",
            "PARSER_ONLY",
            "Hardened unsupported, malformed, ambiguous, and unsafe output as fail-closed reviewer evidence.",
        ),
        (
            98,
            "Parser Classification Matrix",
            "COMPLETE",
            "REVIEW_ONLY",
            "Mapped parser classifications to reviewer actions and non-executable safety invariants.",
        ),
        (
            99,
            "Parser Evidence Coverage / Sample Gap Audit",
            "COMPLETE",
            "REPORT_ONLY",
            "Made sample gaps visible so reviewers can distinguish coverage gaps from execution readiness.",
        ),
        (
            100,
            "Parser Phase Gate Review",
            "COMPLETE",
            "REVIEW_ONLY",
            "Separated parser evidence readiness from broker, adapter, SSH, and execution readiness.",
        ),
        (
            101,
            "Parser Evidence Closure Plan",
            "COMPLETE",
            "STATIC_ONLY",
            "Defined the closure sequence while keeping parser_ready_for_broker and execution paths blocked.",
        ),
        (
            102,
            "Parser Fixture Expansion",
            "COMPLETE",
            "STATIC_ONLY",
            "Expanded deterministic fixtures without adding parser capability or live-device behavior.",
        ),
        (
            103,
            "Parser Evidence Matrix / Gap Traceability",
            "COMPLETE",
            "REVIEW_ONLY",
            "Linked Day96-Day102 evidence, gaps, expected decisions, actual results, and safety boundaries.",
        ),
        (
            104,
            "Parser Reviewer Acceptance Gate",
            "COMPLETE",
            "REVIEW_ONLY",
            "Converted matrix trace states into reviewer acceptance criteria with safety blocks preserved.",
        ),
        (
            105,
            "Parser Acceptance Closure / Safety-Blocked Exit Summary",
            "COMPLETE",
            "BLOCKED_REVIEW_ONLY",
            "Closed the parser evidence package for review-only continuation while live execution remains blocked.",
        ),
    ]
    return [
        {
            "day": day,
            "name": name,
            "stage_status": stage_status,
            "scope": scope,
            "execution_allowed": False,
            "safety_boundary_locked": True,
            "reviewer_acceptance_relevance": relevance,
        }
        for day, name, stage_status, scope, relevance in specs
    ]


def build_parser_reviewer_evidence_contract_report(
    evidence_items: Optional[Iterable[Dict[str, Any]]] = None,
    safety_overrides: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    """Build the deterministic Day107 parser reviewer evidence contract."""
    items = [deepcopy(item) for item in (evidence_items or build_default_evidence_items())]
    requested_overrides = deepcopy(safety_overrides or {})
    represented_days = sorted(
        item.get("day") for item in items if isinstance(item.get("day"), int)
    )
    missing_days = [day for day in REQUIRED_DAYS if day not in represented_days]
    duplicate_days = sorted(
        {day for day in represented_days if represented_days.count(day) > 1}
    )
    item_contract_errors = validate_evidence_items(items)
    safety_violation_fields = find_safety_violation_fields(items, requested_overrides)

    evidence_chain_complete = not missing_days and not duplicate_days and not item_contract_errors
    safety_ok = not safety_violation_fields

    if not safety_ok:
        overall_status = "FAIL"
        final_recommendation = FAIL_RECOMMENDATION
        accepted_for_review_only_continuation = False
        reviewer_contract_status = "REJECTED_FOR_SAFETY_RISK"
        safety_boundary_status = "SAFETY_VIOLATION_DETECTED"
        no_execution_proof_status = "FAIL"
    elif evidence_chain_complete:
        overall_status = "PASS"
        final_recommendation = PASS_RECOMMENDATION
        accepted_for_review_only_continuation = True
        reviewer_contract_status = "ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION"
        safety_boundary_status = "LOCKED"
        no_execution_proof_status = "PASS"
    else:
        overall_status = "WARN"
        final_recommendation = WARN_RECOMMENDATION
        accepted_for_review_only_continuation = False
        reviewer_contract_status = "NEEDS_GAP_REVIEW"
        safety_boundary_status = "LOCKED"
        no_execution_proof_status = "PASS"

    report = {
        "day": 107,
        "day_id": "Day107",
        "task": TASK_NAME,
        "title": TITLE,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "created_at": CREATED_AT,
        "audit_type": AUDIT_TYPE,
        "evidence_scope": EVIDENCE_SCOPE,
        "evidence_chain_complete": evidence_chain_complete,
        "parser_boundary_status": "LOCKED_PARSER_ONLY_REVIEW_ONLY",
        "reviewer_contract_status": reviewer_contract_status,
        "safety_boundary_status": safety_boundary_status,
        "no_execution_proof_status": no_execution_proof_status,
        "blocked_transition_status": "LIVE_CAPABLE_WORKFLOWS_BLOCKED",
        "accepted_for_review_only_continuation": accepted_for_review_only_continuation,
        "accepted_for_live_execution": False,
        "live_execution_allowed": False,
        "ssh_allowed": False,
        "device_connection_allowed": False,
        "config_mutation_allowed": False,
        "openai_api_allowed": False,
        "voice_runtime_allowed": False,
        "adapter_invocation_allowed": False,
        "rejected_intent_execution_allowed": False,
        "final_recommendation": final_recommendation,
        "evidence_items": items,
        "overall_status": overall_status,
        "required_days": REQUIRED_DAYS,
        "represented_days": represented_days,
        "missing_evidence_days": missing_days,
        "duplicate_evidence_days": duplicate_days,
        "item_contract_errors": item_contract_errors,
        "safety_violation_fields": safety_violation_fields,
        "requested_safety_overrides": requested_overrides,
        "reviewer_acceptance_criteria": build_reviewer_acceptance_criteria(),
        "locked_safety_boundaries": build_locked_safety_boundaries(),
        "blocked_transition_reasons": build_blocked_transition_reasons(),
        "no_execution_proof": {
            flag: False for flag in ALL_NO_EXECUTION_FLAGS
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    report["validation_errors"] = validate_parser_reviewer_evidence_contract_report(report)
    if report["validation_errors"] and report["overall_status"] == "PASS":
        report["overall_status"] = "FAIL"
        report["reviewer_contract_status"] = "REJECTED_FOR_CONTRACT_ERROR"
        report["accepted_for_review_only_continuation"] = False
        report["final_recommendation"] = FAIL_RECOMMENDATION
    return report


def validate_evidence_items(items: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    for index, item in enumerate(items, start=1):
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                errors.append(f"evidence_items[{index}] missing {field}.")
        if item.get("execution_allowed") is not False:
            errors.append(f"Day{item.get('day')} execution_allowed must be false.")
        if item.get("safety_boundary_locked") is not True:
            errors.append(f"Day{item.get('day')} safety_boundary_locked must be true.")
    return errors


def find_safety_violation_fields(
    items: List[Dict[str, Any]],
    requested_overrides: Dict[str, bool],
) -> List[str]:
    violations: List[str] = []
    for field in ALL_NO_EXECUTION_FLAGS:
        if requested_overrides.get(field) is True:
            violations.append(field)
    for item in items:
        day = item.get("day", "unknown")
        if item.get("execution_allowed") is True:
            violations.append(f"Day{day}.execution_allowed")
        if item.get("safety_boundary_locked") is not True:
            violations.append(f"Day{day}.safety_boundary_locked")
    return sorted(set(violations))


def build_reviewer_acceptance_criteria() -> List[Dict[str, str]]:
    criteria = [
        "Day96-Day105 evidence stages are all represented.",
        "Every evidence item contains the required reviewer contract fields.",
        "Every evidence item keeps execution_allowed=false.",
        "Every evidence item keeps safety_boundary_locked=true.",
        "Coverage gaps remain visible and do not become execution permission.",
        "Reviewer acceptance is limited to review-only continuation.",
        "No live, SSH, device, adapter, OpenAI API, voice, or config mutation flag is unlocked.",
    ]
    return [
        {"criterion_id": f"D107-C{index:02d}", "criterion": criterion}
        for index, criterion in enumerate(criteria, start=1)
    ]


def build_locked_safety_boundaries() -> List[Dict[str, Any]]:
    boundaries = [
        ("live_execution_allowed", "No live execution is permitted by Day107."),
        ("ssh_allowed", "No SSH transport is permitted by Day107."),
        ("device_connection_allowed", "No device connection is permitted by Day107."),
        ("config_mutation_allowed", "No router, switch, firewall, NAT, VRRP, WireGuard, or interface mutation is permitted."),
        ("openai_api_allowed", "No OpenAI API or external AI runtime is permitted by Day107."),
        ("voice_runtime_allowed", "No voice input, speech-to-text, text-to-speech, or microphone runtime is permitted."),
        ("adapter_invocation_allowed", "No adapter, broker, runner, or execution path may be invoked by rejected or report-only intent."),
        ("accepted_for_live_execution", "Parser evidence acceptance cannot become live execution acceptance."),
    ]
    return [
        {
            "boundary_id": f"D107-B{index:02d}",
            "field": field,
            "locked_value": False,
            "reason": reason,
        }
        for index, (field, reason) in enumerate(boundaries, start=1)
    ]


def build_blocked_transition_reasons() -> List[Dict[str, str]]:
    reasons = [
        "Parser evidence quality does not prove live-device safety.",
        "Reviewer acceptance does not grant adapter, broker, runner, SSH, or command execution authority.",
        "No separate live-capable safety gate has been approved.",
        "No explicit user approval has been granted for a specific live operation.",
        "No rollback, recovery, or mutation safety case is part of Day107.",
    ]
    return [
        {"reason_id": f"D107-T{index:02d}", "reason": reason}
        for index, reason in enumerate(reasons, start=1)
    ]


def validate_parser_reviewer_evidence_contract_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 107:
        errors.append("day must be 107.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("phase_name") != PHASE_NAME:
        errors.append(f"phase_name must be {PHASE_NAME}.")
    if report.get("created_at") != CREATED_AT:
        errors.append(f"created_at must be {CREATED_AT}.")
    if report.get("audit_type") != AUDIT_TYPE:
        errors.append(f"audit_type must be {AUDIT_TYPE}.")
    if report.get("evidence_scope") != EVIDENCE_SCOPE:
        errors.append(f"evidence_scope must be {EVIDENCE_SCOPE}.")
    for flag in ALL_NO_EXECUTION_FLAGS:
        if report.get(flag) is not False:
            errors.append(f"{flag} must remain false.")
        if report.get("no_execution_proof", {}).get(flag) is not False:
            errors.append(f"no_execution_proof.{flag} must remain false.")
    if report.get("accepted_for_review_only_continuation") is True and report.get("overall_status") != "PASS":
        errors.append("accepted_for_review_only_continuation can be true only on PASS.")
    if report.get("accepted_for_live_execution") is not False:
        errors.append("accepted_for_live_execution cannot become true.")
    if not report.get("evidence_items"):
        errors.append("evidence_items must be non-empty.")
    errors.extend(report.get("item_contract_errors", []))
    return errors


def write_parser_reviewer_evidence_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_reviewer_evidence_contract_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_reviewer_evidence_contract_html(safe_report, html_path)
    return json_path, html_path


def write_parser_reviewer_evidence_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_rows = "".join(
        "<tr>"
        f"<td>Day{html.escape(str(item['day']))}</td>"
        f"<td>{html.escape(item['name'])}</td>"
        f"<td>{html.escape(item['stage_status'])}</td>"
        f"<td><code>{html.escape(item['scope'])}</code></td>"
        f"<td>{html.escape(json.dumps(item['execution_allowed']))}</td>"
        f"<td>{html.escape(json.dumps(item['safety_boundary_locked']))}</td>"
        f"<td>{html.escape(item['reviewer_acceptance_relevance'])}</td>"
        "</tr>"
        for item in report["evidence_items"]
    )
    criteria_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['criterion_id'])}</code></td>"
        f"<td>{html.escape(item['criterion'])}</td>"
        "</tr>"
        for item in report["reviewer_acceptance_criteria"]
    )
    boundary_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['field'])}</code></td>"
        f"<td>{html.escape(json.dumps(item['locked_value']))}</td>"
        f"<td>{html.escape(item['reason'])}</td>"
        "</tr>"
        for item in report["locked_safety_boundaries"]
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
  <p><strong>Status:</strong> <span class="status">{html.escape(report['overall_status'])}</span> / {html.escape(report['reviewer_contract_status'])}</p>
  <p><strong>Audit type:</strong> <code>{html.escape(report['audit_type'])}</code></p>
  <p><strong>Evidence scope:</strong> {html.escape(report['evidence_scope'])}</p>
  <p><strong>Final recommendation:</strong> <code>{html.escape(report['final_recommendation'])}</code></p>
  <p><strong>Review-only continuation accepted:</strong> {html.escape(json.dumps(report['accepted_for_review_only_continuation']))}</p>
  <p><strong>Live execution accepted:</strong> {html.escape(json.dumps(report['accepted_for_live_execution']))}</p>
  <p><strong>Reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <p><strong>Scope:</strong> Day107 consolidates Day96-Day105 parser reviewer evidence only. It opens no live execution, SSH, device connection, adapter invocation, OpenAI API, voice runtime, rejected-intent execution, or configuration mutation path.</p>
  <h2>Evidence Items</h2>
  <table>
    <thead><tr><th>Day</th><th>Name</th><th>Stage</th><th>Scope</th><th>Execution Allowed</th><th>Safety Boundary Locked</th><th>Reviewer Relevance</th></tr></thead>
    <tbody>{evidence_rows}</tbody>
  </table>
  <h2>Reviewer Acceptance Criteria</h2>
  <table>
    <thead><tr><th>ID</th><th>Criterion</th></tr></thead>
    <tbody>{criteria_rows}</tbody>
  </table>
  <h2>Locked Safety Boundaries</h2>
  <table>
    <thead><tr><th>Field</th><th>Locked Value</th><th>Reason</th></tr></thead>
    <tbody>{boundary_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )
