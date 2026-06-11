"""Day101 parser evidence closure plan.

This module converts the Day100 parser phase-gate review into a deterministic
evidence closure roadmap. It is local-only, report-only, and does not advance
parser output into broker, executor, adapter, SSH, or live-device paths.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_parser_phase_gate_review import build_parser_phase_gate_review_report


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-evidence-closure-plan"
TITLE = "Parser Evidence Closure Plan"
PHASE = "PARSER_EVIDENCE_CLOSURE_PLANNING"
SCHEMA_VERSION = "day101.parser_evidence_closure_plan.v1"
SOURCE_KIND = "day101_static_day100_evidence_closure_plan"
REVIEW_MODE = "evidence_closure_plan_report_only"
REVIEWER_STATUS = "EVIDENCE_CLOSURE_PLAN_READY"
REPORT_JSON = Path("reports") / "ai" / "day101_parser_evidence_closure_plan.json"
REPORT_HTML = Path("reports") / "ai" / "day101_parser_evidence_closure_plan.html"

RUNTIME_DISABLED_FLAGS = (
    "parser_ready_for_broker",
    "broker_handoff_allowed",
    "execution_allowed",
    "adapter_invocation_allowed",
    "executor_invocation_allowed",
    "ssh_allowed",
    "live_device_access_allowed",
    "live_access_allowed",
    "live_read_allowed",
    "live_device_path_allowed",
    "routeros_execution_allowed",
    "command_execution_allowed",
    "dashboard_action_allowed",
    "approval_unlock_supported",
    "openai_api_allowed",
    "voice_runtime_allowed",
)

CLOSURE_PROFILES = {
    "supported_table_parse": {
        "priority": 1,
        "gap": "Table parsing is under-covered and needs more positive, malformed, and degraded fixture evidence.",
        "required_evidence": [
            "Add table-shaped positive fixtures with repeated headers and optional columns.",
            "Add malformed table fixtures with truncated rows and mixed delimiters.",
            "Add golden normalized-output expectations for each table fixture.",
        ],
        "target_follow_up_day": "Day102",
        "risk": "missing_positive_cases",
    },
    "malformed_input": {
        "priority": 2,
        "gap": "Malformed parser inputs remain reviewer evidence only and need expanded negative fixture coverage.",
        "required_evidence": [
            "Add malformed input fixtures for broken lines, invalid encodings, and empty fields.",
            "Assert deterministic rejection envelopes and non-executable classifications.",
        ],
        "target_follow_up_day": "Day102",
        "risk": "malformed_input_coverage_gaps",
    },
    "ambiguous_output": {
        "priority": 3,
        "gap": "Ambiguous output is review-only and needs reject-by-default regression coverage.",
        "required_evidence": [
            "Add ambiguous fixture families where command family or schema shape cannot be inferred safely.",
            "Assert reject-by-default classifications and reviewer-facing reasons.",
        ],
        "target_follow_up_day": "Day104",
        "risk": "reject_by_default_risks",
    },
    "unsupported_command_family": {
        "priority": 4,
        "gap": "Unsupported command families must stay review-only until negative cases prove they do not cross safety boundaries.",
        "required_evidence": [
            "Add unsupported command fixtures for non-read-only and unknown command families.",
            "Assert no broker handoff, no execution unlock, and stable rejection metadata.",
        ],
        "target_follow_up_day": "Day104",
        "risk": "missing_negative_cases",
    },
    "parser_error_guarded": {
        "priority": 5,
        "gap": "Parser error paths are review-only and need schema-stability regression before any re-gate.",
        "required_evidence": [
            "Freeze error envelope keys and reviewer reason fields.",
            "Add regression checks that parser errors cannot change authorization flags.",
        ],
        "target_follow_up_day": "Day103",
        "risk": "schema_stability_risks",
    },
    "unsupported_format": {
        "priority": 6,
        "gap": "Unsupported formats need negative fixtures so reviewer-only handling remains stable.",
        "required_evidence": [
            "Add fixtures for JSON-like, binary-like, and free-form unsupported outputs.",
            "Assert deterministic review-only rejection records.",
        ],
        "target_follow_up_day": "Day102",
        "risk": "missing_negative_cases",
    },
    "empty_output": {
        "priority": 7,
        "gap": "Empty output needs explicit fixtures proving no parser advance or broker handoff occurs.",
        "required_evidence": [
            "Add blank, whitespace-only, and header-only fixtures.",
            "Assert stable empty-output classification and review-only reason text.",
        ],
        "target_follow_up_day": "Day102",
        "risk": "malformed_input_coverage_gaps",
    },
    "partial_output": {
        "priority": 8,
        "gap": "Partial output needs fixture expansion before schema stability can be claimed.",
        "required_evidence": [
            "Add truncated key-value, line, and table fixtures.",
            "Assert stable partial-output normalization and review-only handling.",
        ],
        "target_follow_up_day": "Day103",
        "risk": "schema_stability_risks",
    },
}

DEFAULT_CLOSURE_PROFILE = {
    "priority": 9,
    "gap": "Day100 did not provide enough evidence to allow advancement.",
    "required_evidence": [
        "Add static fixtures that make the parser behavior reviewable.",
        "Add regression assertions before rerunning the phase gate.",
    ],
    "target_follow_up_day": "Day102",
    "risk": "weak_fixture_coverage",
}

RECOMMENDED_SEQUENCE = [
    {
        "day": "Day102",
        "name": "Parser Fixture Expansion",
        "purpose": "Add positive, negative, malformed, ambiguous, and unsafe parser fixtures.",
        "entry_condition": "Day101 closure plan identifies under-covered and review-only categories.",
        "exit_condition": "Fixture gaps are represented as deterministic static samples.",
        "broker_handoff_allowed": False,
    },
    {
        "day": "Day103",
        "name": "Parser Schema Stability Regression",
        "purpose": "Freeze normalized parser schema and detect accidental output drift.",
        "entry_condition": "Day102 fixture families exist.",
        "exit_condition": "Golden output schemas are stable across supported and guarded parser paths.",
        "broker_handoff_allowed": False,
    },
    {
        "day": "Day104",
        "name": "Parser Reject-by-default Regression",
        "purpose": "Strengthen unknown, ambiguous, and unsafe input rejection behavior.",
        "entry_condition": "Day103 schema checks are stable enough to validate rejection records.",
        "exit_condition": "Reject-by-default behavior is deterministic and reviewable.",
        "broker_handoff_allowed": False,
    },
    {
        "day": "Day105",
        "name": "Parser Re-Gate Review",
        "purpose": "Re-run the parser phase gate and decide which categories, if any, may advance.",
        "entry_condition": "Day102-Day104 closure work is complete and reviewed.",
        "exit_condition": "A new phase-gate decision is produced; broker integration remains blocked unless explicitly approved later.",
        "broker_handoff_allowed": False,
    },
]


@dataclass(frozen=True)
class ClosureItem:
    priority: int
    category: str
    day100_decision: str
    day100_coverage_status: str
    gap: str
    required_evidence: List[str]
    target_follow_up_day: str
    closure_status: str
    risk: str
    blocked_from_advancement: bool

    def to_record(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "source_kind": SOURCE_KIND,
            "review_mode": REVIEW_MODE,
            "parser_ready_for_broker": False,
            "broker_handoff_allowed": False,
            "execution_allowed": False,
            "live_device_access_allowed": False,
            "ssh_allowed": False,
            "openai_api_allowed": False,
        }


def build_parser_evidence_closure_plan_report(
    day100_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_report = deepcopy(day100_report) if day100_report is not None else build_parser_phase_gate_review_report()
    under_covered_categories = build_category_records(source_report, "UNDER_COVERED")
    review_only_categories = build_category_records(source_report, "REVIEW_ONLY")
    closure_items = build_closure_items(source_report)
    summary = build_summary(source_report, closure_items, under_covered_categories, review_only_categories)
    report = {
        "day": 101,
        "day_id": "Day101",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "schema_version": SCHEMA_VERSION,
        "source_kind": SOURCE_KIND,
        "review_mode": REVIEW_MODE,
        "scope": {
            "report_only": True,
            "planning_only": True,
            "source_day": "Day100",
            "purpose": "Convert Day100 under-covered and review-only parser findings into an evidence closure roadmap.",
            "parser_capability_added": False,
            "broker_boundary_opened": False,
            "parser_gate_released": False,
        },
        "source_reports": {
            "day100": {
                "task": source_report.get("task"),
                "status": source_report.get("overall_status"),
                "final_readiness_decision": source_report.get("summary", {}).get("final_readiness_decision"),
                "path": "reports/ai/day100_parser_phase_gate_review.json",
            },
        },
        "summary": summary,
        "parser_ready_for_broker": False,
        "broker_handoff_allowed": False,
        "execution_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "openai_api_allowed": False,
        "evidence_closure_required": True,
        "phase_gate_rerun_required": True,
        "under_covered_categories": under_covered_categories,
        "review_only_categories": review_only_categories,
        "closure_items": closure_items,
        "recommended_sequence": deepcopy(RECOMMENDED_SEQUENCE),
        "next_phase_gate": "Day105 Parser Re-Gate Review",
        "positioning_statement": (
            "Parser phase is not moving toward execution; it is converting reviewable evidence "
            "into proof of stable parser behavior."
        ),
        "safety_invariants": build_safety_invariants(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "no_broker_handoff": True,
        "no_broker_connection": True,
        "no_executor": True,
        "no_adapter_invocation": True,
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_access": True,
        "no_live_execution": True,
        "no_routeros_execution": True,
        "no_command_execution": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
    }
    validation_errors = validate_parser_evidence_closure_plan_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_category_records(day100_report: Dict[str, Any], decision: str) -> List[Dict[str, Any]]:
    rows = []
    for row in day100_report.get("decision_rows", []):
        if row.get("readiness_decision") != decision:
            continue
        rows.append(
            {
                "category": row.get("evidence_area", "unknown"),
                "day100_decision": decision,
                "coverage_status": row.get("coverage_status", "UNKNOWN"),
                "observed_count": int(row.get("observed_count", 0)),
                "minimum_expected": int(row.get("minimum_expected", 0)),
                "sample_refs": list(row.get("sample_refs", [])),
                "reason": row.get("decision_reason", ""),
                "blocked_from_advancement": True,
            }
        )
    return rows


def build_closure_items(day100_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = []
    for row in day100_report.get("decision_rows", []):
        decision = row.get("readiness_decision")
        if decision not in {"UNDER_COVERED", "REVIEW_ONLY"}:
            continue
        category = row.get("evidence_area", "unknown")
        profile = CLOSURE_PROFILES.get(category, DEFAULT_CLOSURE_PROFILE)
        items.append(
            ClosureItem(
                priority=int(profile["priority"]),
                category=category,
                day100_decision=decision,
                day100_coverage_status=row.get("coverage_status", "UNKNOWN"),
                gap=str(profile["gap"]),
                required_evidence=list(profile["required_evidence"]),
                target_follow_up_day=str(profile["target_follow_up_day"]),
                closure_status="OPEN",
                risk=str(profile["risk"]),
                blocked_from_advancement=True,
            ).to_record()
        )
    return sorted(items, key=lambda item: (item["priority"], item["category"]))


def build_summary(
    day100_report: Dict[str, Any],
    closure_items: List[Dict[str, Any]],
    under_covered_categories: List[Dict[str, Any]],
    review_only_categories: List[Dict[str, Any]],
) -> Dict[str, Any]:
    source_summary = day100_report.get("summary", {})
    source_validation_error_count = len(day100_report.get("validation_errors", []))
    source_status = day100_report.get("overall_status")
    disabled_violation_count = sum(
        1
        for item in closure_items
        if item.get("parser_ready_for_broker") is not False
        or item.get("broker_handoff_allowed") is not False
        or item.get("execution_allowed") is not False
        or item.get("live_device_access_allowed") is not False
        or item.get("ssh_allowed") is not False
        or item.get("openai_api_allowed") is not False
    )
    required_days = [item["day"] for item in RECOMMENDED_SEQUENCE]
    sequence_complete = required_days == ["Day102", "Day103", "Day104", "Day105"]
    overall_status = (
        "PASS"
        if closure_items
        and under_covered_categories
        and review_only_categories
        and source_status == "PASS"
        and source_validation_error_count == 0
        and source_summary.get("final_readiness_decision") == "UNDER_COVERED"
        and disabled_violation_count == 0
        and sequence_complete
        else "FAIL"
    )
    return {
        "closure_item_count": len(closure_items),
        "blocked_category_count": len(closure_items),
        "under_covered_category_count": len(under_covered_categories),
        "review_only_category_count": len(review_only_categories),
        "recommended_next_action_count": len(RECOMMENDED_SEQUENCE),
        "recommended_next_days": required_days,
        "day100_final_readiness_decision": source_summary.get("final_readiness_decision"),
        "day100_status": source_status,
        "source_validation_error_count": source_validation_error_count,
        "disabled_violation_count": disabled_violation_count,
        "parser_ready_for_broker": False,
        "broker_handoff_allowed": False,
        "execution_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "openai_api_allowed": False,
        "evidence_closure_required": True,
        "phase_gate_rerun_required": True,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "report_only": True,
        "planning_only": True,
        "parser_capability_added": False,
        "parser_gate_released": False,
        "broker_boundary_opened": False,
        "broker_connection_attempted": False,
        "phase_gate_rerun_required": True,
        "evidence_closure_required": True,
        **{flag: False for flag in RUNTIME_DISABLED_FLAGS},
    }


def validate_parser_evidence_closure_plan_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    closure_items = report.get("closure_items", [])

    if report.get("day") != 101:
        errors.append("day must be 101.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-evidence-closure-plan.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")

    for field in (
        "parser_ready_for_broker",
        "broker_handoff_allowed",
        "execution_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "openai_api_allowed",
        "dashboard_action_allowed",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
        if summary.get(field) is not False and field in summary:
            errors.append(f"summary.{field} must be false.")
    for field in ("evidence_closure_required", "phase_gate_rerun_required"):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
        if summary.get(field) is not True:
            errors.append(f"summary.{field} must be true.")

    if not report.get("under_covered_categories"):
        errors.append("UNDER_COVERED categories must be represented.")
    if not report.get("review_only_categories"):
        errors.append("REVIEW_ONLY categories must be represented.")
    if summary.get("recommended_next_days") != ["Day102", "Day103", "Day104", "Day105"]:
        errors.append("recommended sequence must be Day102, Day103, Day104, Day105.")
    if report.get("next_phase_gate") != "Day105 Parser Re-Gate Review":
        errors.append("next_phase_gate must be Day105 Parser Re-Gate Review.")

    required_item_fields = {
        "priority",
        "category",
        "gap",
        "required_evidence",
        "target_follow_up_day",
        "day100_decision",
        "day100_coverage_status",
        "closure_status",
        "risk",
        "blocked_from_advancement",
        "parser_ready_for_broker",
        "broker_handoff_allowed",
        "execution_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "openai_api_allowed",
    }
    for item in closure_items:
        missing = required_item_fields.difference(item)
        if missing:
            errors.append(f"{item.get('category', '<unknown>')} missing fields: {', '.join(sorted(missing))}.")
        if item.get("day100_decision") not in {"UNDER_COVERED", "REVIEW_ONLY"}:
            errors.append(f"{item.get('category', '<unknown>')} must come from UNDER_COVERED or REVIEW_ONLY.")
        if item.get("target_follow_up_day") not in {"Day102", "Day103", "Day104", "Day105"}:
            errors.append(f"{item.get('category', '<unknown>')} target follow-up day is outside Day102-Day105.")
        if not item.get("required_evidence"):
            errors.append(f"{item.get('category', '<unknown>')} requires evidence instructions.")
        if item.get("blocked_from_advancement") is not True:
            errors.append(f"{item.get('category', '<unknown>')} must remain blocked from advancement.")
        for flag in (
            "parser_ready_for_broker",
            "broker_handoff_allowed",
            "execution_allowed",
            "live_device_access_allowed",
            "ssh_allowed",
            "openai_api_allowed",
        ):
            if item.get(flag) is not False:
                errors.append(f"{item.get('category', '<unknown>')} {flag} must be false.")

    for field in (
        "no_broker_handoff",
        "no_broker_connection",
        "no_executor",
        "no_adapter_invocation",
        "no_real_device_access",
        "no_ssh",
        "no_live_access",
        "no_live_execution",
        "no_routeros_execution",
        "no_command_execution",
        "no_config_json_read",
        "no_openai_api",
        "no_ai_sdk_runtime",
        "no_voice",
        "dashboard_read_only",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")

    invariants = report.get("safety_invariants", {})
    for field in ("report_only", "planning_only", "phase_gate_rerun_required", "evidence_closure_required"):
        if invariants.get(field) is not True:
            errors.append(f"safety_invariants.{field} must be true.")
    for field in (
        "parser_capability_added",
        "parser_gate_released",
        "broker_boundary_opened",
        "broker_connection_attempted",
    ):
        if invariants.get(field) is not False:
            errors.append(f"safety_invariants.{field} must be false.")
    for flag in RUNTIME_DISABLED_FLAGS:
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    return errors


def write_parser_evidence_closure_plan_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_evidence_closure_plan_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_evidence_closure_plan_html(safe_report, html_path)
    return json_path, html_path


def write_parser_evidence_closure_plan_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    category_rows = "".join(
        "<tr>"
        f"<td>{html.escape(category['category'])}</td>"
        f"<td>{html.escape(category['day100_decision'])}</td>"
        f"<td>{html.escape(category['coverage_status'])}</td>"
        f"<td>{html.escape(str(category['observed_count']))}</td>"
        f"<td>{html.escape(str(category['minimum_expected']))}</td>"
        f"<td>{html.escape(category['reason'])}</td>"
        "</tr>"
        for category in report["under_covered_categories"] + report["review_only_categories"]
    )
    closure_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item['priority']))}</td>"
        f"<td>{html.escape(item['category'])}</td>"
        f"<td>{html.escape(item['day100_decision'])}</td>"
        f"<td>{html.escape(item['gap'])}</td>"
        f"<td>{html.escape('; '.join(item['required_evidence']))}</td>"
        f"<td>{html.escape(item['target_follow_up_day'])}</td>"
        "</tr>"
        for item in report["closure_items"]
    )
    sequence_rows = "".join(
        "<tr>"
        f"<td>{html.escape(step['day'])}</td>"
        f"<td>{html.escape(step['name'])}</td>"
        f"<td>{html.escape(step['purpose'])}</td>"
        f"<td>{html.escape(step['exit_condition'])}</td>"
        f"<td>{html.escape(json.dumps(step['broker_handoff_allowed']))}</td>"
        "</tr>"
        for step in report["recommended_sequence"]
    )
    invariant_rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for name, value in report["safety_invariants"].items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 22px; }}
    th, td {{ border: 1px solid #d6dee9; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    .pass {{ color: #116329; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>Day101 Parser Evidence Closure Plan</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Scope:</strong> Day101 converts Day100 parser findings into a closure roadmap. It does not approve broker handoff, release the parser gate, add parser execution capability, use SSH, or contact live devices.</p>
  <p><strong>Core locks:</strong> <code>parser_ready_for_broker=false</code>, <code>broker_handoff_allowed=false</code>, <code>phase_gate_rerun_required=true</code></p>
  <h2>Summary</h2>
  <p><strong>Closure items:</strong> {summary['closure_item_count']} | <strong>Blocked categories:</strong> {summary['blocked_category_count']} | <strong>UNDER_COVERED:</strong> {summary['under_covered_category_count']} | <strong>REVIEW_ONLY:</strong> {summary['review_only_category_count']} | <strong>Next actions:</strong> {summary['recommended_next_action_count']}</p>
  <h2>Day100 Findings</h2>
  <table>
    <thead><tr><th>Category</th><th>Decision</th><th>Coverage</th><th>Observed</th><th>Minimum</th><th>Reason</th></tr></thead>
    <tbody>{category_rows}</tbody>
  </table>
  <h2>Closure Items</h2>
  <table>
    <thead><tr><th>Priority</th><th>Category</th><th>Day100 Decision</th><th>Gap</th><th>Required Evidence</th><th>Target Day</th></tr></thead>
    <tbody>{closure_rows}</tbody>
  </table>
  <h2>Recommended Sequence</h2>
  <table>
    <thead><tr><th>Day</th><th>Name</th><th>Purpose</th><th>Exit Condition</th><th>Broker Handoff</th></tr></thead>
    <tbody>{sequence_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Value</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )
