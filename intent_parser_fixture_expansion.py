"""Day102 parser fixture expansion.

This module adds deterministic parser fixture evidence only. It does not add
parser capability, invoke adapters, contact devices, open SSH, or hand parser
output to a broker or executor.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-fixture-expansion"
TITLE = "Parser Fixture Expansion"
PHASE = "PARSER_FIXTURE_EXPANSION"
SCHEMA_VERSION = "day102.parser_fixture_expansion.v1"
SOURCE_KIND = "day102_static_parser_fixture"
PARSER_MODE = "fixture_expansion_report_only"
REVIEWER_STATUS = "FIXTURE_EXPANSION_READY"
REPORT_JSON = Path("reports") / "ai" / "day102_parser_fixture_expansion.json"
REPORT_HTML = Path("reports") / "ai" / "day102_parser_fixture_expansion.html"

FIXTURE_CATEGORIES = {"positive", "negative", "malformed", "ambiguous", "unsafe"}
PARSER_STATUSES = {
    "PARSED",
    "UNSUPPORTED_OUTPUT",
    "MALFORMED_INPUT",
    "AMBIGUOUS_OUTPUT",
    "UNSAFE_INTENT_BLOCKED",
}
FIXTURE_CLASSIFICATIONS = {
    "accepted_readonly_report_only",
    "rejected_unsupported",
    "rejected_malformed",
    "rejected_ambiguous",
    "rejected_unsafe",
}
REVIEWER_ACTIONS = {
    "positive": "accept_as_static_parser_evidence_only",
    "negative": "reject_with_unsupported_reason",
    "malformed": "reject_without_crash_and_attach_reason",
    "ambiguous": "reject_until_meaning_is_disambiguated",
    "unsafe": "block_before_parser_or_runtime_use",
}
RUNTIME_DISABLED_FLAGS = (
    "parser_capability_added",
    "parser_ready_for_broker",
    "broker_handoff_allowed",
    "execution_allowed",
    "adapter_invocation_allowed",
    "executor_invocation_allowed",
    "ssh_allowed",
    "live_device_access_allowed",
    "live_access_allowed",
    "routeros_execution_allowed",
    "command_execution_allowed",
    "raw_command_allowed",
    "config_change_allowed",
    "auth_material_required",
    "device_contact_allowed",
    "dashboard_action_allowed",
    "approval_unlock_supported",
    "openai_api_allowed",
    "voice_runtime_allowed",
)


@dataclass(frozen=True)
class ParserFixtureCase:
    case_id: str
    category: str
    case_name: str
    input_source: str
    command_family: str
    raw_input: Optional[str]
    expected_parser_status: str
    fixture_classification: str
    accepted_by_fixture_contract: bool
    reason: Optional[str]
    evidence_goal: str
    unsafe_intent_markers: List[str]

    def to_record(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "fixture_origin": SOURCE_KIND,
            "parser_mode": PARSER_MODE,
            "is_static_fixture": True,
            "raw_input_present": isinstance(self.raw_input, str) and bool(self.raw_input),
            "raw_input_preview": _preview_raw_input(self.raw_input),
            "reviewer_action": REVIEWER_ACTIONS[self.category],
            "reason_required": self.category != "positive",
            "reason_present": bool(self.reason),
            "malformed_handled_without_exception": self.category != "malformed" or bool(self.reason),
            "ambiguous_not_silently_accepted": self.category != "ambiguous"
            or self.accepted_by_fixture_contract is False,
            "unsafe_intent_blocked": self.category != "unsafe"
            or (
                self.accepted_by_fixture_contract is False
                and self.expected_parser_status == "UNSAFE_INTENT_BLOCKED"
            ),
            "parser_output_is_review_data_only": True,
            "executable_allowed": False,
            "broker_handoff_allowed": False,
            "live_device_access_allowed": False,
            "ssh_allowed": False,
            "config_change_allowed": False,
            "adapter_invocation_allowed": False,
            "not_verified_device_truth": True,
        }


def build_day102_parser_fixture_cases() -> List[Dict[str, Any]]:
    """Return static parser fixtures for Day102 evidence expansion."""
    cases = [
        ParserFixtureCase(
            case_id="D102-P01-readonly-identity-key-value",
            category="positive",
            case_name="Read-only identity key-value output",
            input_source="day102_static_readonly_report_fixture",
            command_family="readonly_identity",
            raw_input="name: lab-router-simulated\nuptime: 1d2h",
            expected_parser_status="PARSED",
            fixture_classification="accepted_readonly_report_only",
            accepted_by_fixture_contract=True,
            reason=None,
            evidence_goal="Legal read-only key-value parser input is not rejected.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-P02-readonly-interface-table",
            category="positive",
            case_name="Read-only interface table output",
            input_source="day102_static_readonly_report_fixture",
            command_family="readonly_interfaces",
            raw_input="NAME  STATE  COMMENT\nether1  running  wan\nether2  disabled  spare",
            expected_parser_status="PARSED",
            fixture_classification="accepted_readonly_report_only",
            accepted_by_fixture_contract=True,
            reason=None,
            evidence_goal="Legal read-only table parser input is not rejected.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-P03-report-only-summary-lines",
            category="positive",
            case_name="Report-only summary text",
            input_source="day102_static_readonly_report_fixture",
            command_family="report_only_summary",
            raw_input="report: latest parser evidence\nstatus: review-only\nexecution: disabled",
            expected_parser_status="PARSED",
            fixture_classification="accepted_readonly_report_only",
            accepted_by_fixture_contract=True,
            reason=None,
            evidence_goal="Report-only parser evidence text is not mistaken for unsafe input.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-N01-unsupported-bgp-normal-format",
            category="negative",
            case_name="Unsupported BGP output with normal table format",
            input_source="day102_static_unsupported_fixture",
            command_family="readonly_bgp_neighbors",
            raw_input="PEER  STATE\n198.51.100.1  established",
            expected_parser_status="UNSUPPORTED_OUTPUT",
            fixture_classification="rejected_unsupported",
            accepted_by_fixture_contract=False,
            reason="Command family readonly_bgp_neighbors is outside the reviewed parser surface.",
            evidence_goal="Unsupported but well-formed input is clearly rejected.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-N02-unsupported-json-like-format",
            category="negative",
            case_name="Unsupported JSON-like evidence shape",
            input_source="day102_static_unsupported_fixture",
            command_family="readonly_inventory_json_like",
            raw_input='{"name":"lab-router","interfaces":["ether1","ether2"]}',
            expected_parser_status="UNSUPPORTED_OUTPUT",
            fixture_classification="rejected_unsupported",
            accepted_by_fixture_contract=False,
            reason="Structured JSON-like parser fixtures are not supported by the Day96 text parser contract.",
            evidence_goal="Unsupported format is rejected with a specific reason.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-N03-unsupported-firewall-normal-table",
            category="negative",
            case_name="Unsupported firewall rule table",
            input_source="day102_static_unsupported_fixture",
            command_family="readonly_firewall_rules",
            raw_input="ID  CHAIN  ACTION\n0  input  accept",
            expected_parser_status="UNSUPPORTED_OUTPUT",
            fixture_classification="rejected_unsupported",
            accepted_by_fixture_contract=False,
            reason="Firewall rule output is outside Day102 supported parser fixture evidence.",
            evidence_goal="Normal-looking unsupported input does not pass silently.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-M01-missing-raw-input",
            category="malformed",
            case_name="Missing raw input",
            input_source="day102_static_malformed_fixture",
            command_family="readonly_identity",
            raw_input=None,
            expected_parser_status="MALFORMED_INPUT",
            fixture_classification="rejected_malformed",
            accepted_by_fixture_contract=False,
            reason="raw_input is absent; parser evidence cannot be reviewed.",
            evidence_goal="Missing input is rejected without crashing and with a reason.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-M02-empty-command-family",
            category="malformed",
            case_name="Missing command family",
            input_source="day102_static_malformed_fixture",
            command_family="",
            raw_input="name: lab-router-simulated",
            expected_parser_status="MALFORMED_INPUT",
            fixture_classification="rejected_malformed",
            accepted_by_fixture_contract=False,
            reason="command_family is missing, so the fixture cannot be mapped to a reviewed parser context.",
            evidence_goal="Bad fixture shape does not crash and reports what is missing.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-M03-truncated-table-row",
            category="malformed",
            case_name="Truncated table row",
            input_source="day102_static_malformed_fixture",
            command_family="readonly_interfaces",
            raw_input="NAME  STATE  COMMENT\nether1  running\nether2",
            expected_parser_status="MALFORMED_INPUT",
            fixture_classification="rejected_malformed",
            accepted_by_fixture_contract=False,
            reason="Table rows are truncated and cannot be normalized deterministically.",
            evidence_goal="Malformed table input is held with an explicit reason.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-A01-mixed-identity-and-routing",
            category="ambiguous",
            case_name="Mixed supported identity and routing sections",
            input_source="day102_static_ambiguous_fixture",
            command_family="readonly_identity+readonly_routes",
            raw_input="name: lab-router-simulated\n/routing/route print\n0 dst-address=0.0.0.0/0",
            expected_parser_status="AMBIGUOUS_OUTPUT",
            fixture_classification="rejected_ambiguous",
            accepted_by_fixture_contract=False,
            reason="Supported identity data is mixed with a second command family.",
            evidence_goal="Ambiguous mixed sections are not silently accepted.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-A02-conflicting-parser-hints",
            category="ambiguous",
            case_name="Conflicting parser hints",
            input_source="day102_static_ambiguous_fixture",
            command_family="readonly_identity",
            raw_input="# parser_hint: readonly_identity\n# parser_hint: readonly_interfaces\nname: lab-router",
            expected_parser_status="AMBIGUOUS_OUTPUT",
            fixture_classification="rejected_ambiguous",
            accepted_by_fixture_contract=False,
            reason="Fixture contains conflicting parser hints.",
            evidence_goal="Conflicting semantic hints force review instead of acceptance.",
            unsafe_intent_markers=[],
        ),
        ParserFixtureCase(
            case_id="D102-A03-read-report-or-run",
            category="ambiguous",
            case_name="Ambiguous report versus run request",
            input_source="day102_static_ambiguous_fixture",
            command_family="ambiguous_report_or_runtime",
            raw_input="show the latest report and run it if stale",
            expected_parser_status="AMBIGUOUS_OUTPUT",
            fixture_classification="rejected_ambiguous",
            accepted_by_fixture_contract=False,
            reason="The input mixes report viewing with a possible runtime action.",
            evidence_goal="Ambiguous intent cannot become implicit execution permission.",
            unsafe_intent_markers=["run it"],
        ),
        ParserFixtureCase(
            case_id="D102-U01-live-ssh-request",
            category="unsafe",
            case_name="Live SSH request",
            input_source="day102_static_unsafe_fixture",
            command_family="unsafe_live_ssh",
            raw_input="ssh into the router and show interfaces",
            expected_parser_status="UNSAFE_INTENT_BLOCKED",
            fixture_classification="rejected_unsafe",
            accepted_by_fixture_contract=False,
            reason="Live SSH intent is blocked before parser or runtime use.",
            evidence_goal="SSH-related intent is blocked.",
            unsafe_intent_markers=["ssh", "router"],
        ),
        ParserFixtureCase(
            case_id="D102-U02-config-change-request",
            category="unsafe",
            case_name="Configuration change request",
            input_source="day102_static_unsafe_fixture",
            command_family="unsafe_config_change",
            raw_input="/interface set ether2 disabled=no",
            expected_parser_status="UNSAFE_INTENT_BLOCKED",
            fixture_classification="rejected_unsafe",
            accepted_by_fixture_contract=False,
            reason="Mutating RouterOS configuration intent is blocked.",
            evidence_goal="Config-changing intent is blocked.",
            unsafe_intent_markers=["/interface set", "disabled=no"],
        ),
        ParserFixtureCase(
            case_id="D102-U03-live-apply-request",
            category="unsafe",
            case_name="Live apply request",
            input_source="day102_static_unsafe_fixture",
            command_family="unsafe_live_apply",
            raw_input="apply the recommended config to the live device",
            expected_parser_status="UNSAFE_INTENT_BLOCKED",
            fixture_classification="rejected_unsafe",
            accepted_by_fixture_contract=False,
            reason="Live device mutation request is outside parser evidence scope.",
            evidence_goal="Live or mutating intent is blocked.",
            unsafe_intent_markers=["apply", "live device", "config"],
        ),
    ]
    return [case.to_record() for case in cases]


def build_parser_fixture_expansion_report() -> Dict[str, Any]:
    fixtures = build_day102_parser_fixture_cases()
    summary = build_summary(fixtures)
    report = {
        "day": 102,
        "day_id": "Day102",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "schema_version": SCHEMA_VERSION,
        "source_kind": SOURCE_KIND,
        "parser_mode": PARSER_MODE,
        "scope": {
            "report_only": True,
            "static_fixture_only": True,
            "parser_capability_added": False,
            "adapter_connected": False,
            "device_connected": False,
            "purpose": "Expand parser fixtures across positive, negative, malformed, ambiguous, and unsafe evidence categories.",
        },
        "day101_context": {
            "task": "parser-evidence-closure-plan",
            "report_json": "reports/ai/day101_parser_evidence_closure_plan.json",
            "relationship": "Day102 implements the first closure step from the Day101 sequence.",
        },
        "summary": summary,
        "success_criteria": build_success_criteria(fixtures),
        "fixture_cases": fixtures,
        "safety_invariants": build_safety_invariants(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "parser_capability_added": False,
        "parser_ready_for_broker": False,
        "broker_handoff_allowed": False,
        "execution_allowed": False,
        "adapter_invocation_allowed": False,
        "executor_invocation_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "command_execution_allowed": False,
        "config_change_allowed": False,
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_execution": True,
        "no_routeros_execution": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
    }
    validation_errors = validate_parser_fixture_expansion_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_summary(fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts = {
        category: sum(1 for fixture in fixtures if fixture["category"] == category)
        for category in sorted(FIXTURE_CATEGORIES)
    }
    accepted_count = sum(1 for fixture in fixtures if fixture["accepted_by_fixture_contract"] is True)
    rejected_count = len(fixtures) - accepted_count
    reason_missing_count = sum(
        1 for fixture in fixtures if fixture["reason_required"] is True and not fixture["reason_present"]
    )
    unsupported_clear_rejection_count = sum(
        1
        for fixture in fixtures
        if fixture["category"] == "negative"
        and fixture["accepted_by_fixture_contract"] is False
        and fixture["expected_parser_status"] == "UNSUPPORTED_OUTPUT"
        and fixture["reason_present"] is True
    )
    malformed_no_crash_count = sum(
        1
        for fixture in fixtures
        if fixture["category"] == "malformed"
        and fixture["malformed_handled_without_exception"] is True
        and fixture["reason_present"] is True
    )
    ambiguous_rejected_count = sum(
        1
        for fixture in fixtures
        if fixture["category"] == "ambiguous"
        and fixture["ambiguous_not_silently_accepted"] is True
        and fixture["accepted_by_fixture_contract"] is False
    )
    unsafe_blocked_count = sum(
        1
        for fixture in fixtures
        if fixture["category"] == "unsafe" and fixture["unsafe_intent_blocked"] is True
    )
    runtime_violation_count = sum(
        1
        for fixture in fixtures
        if fixture["executable_allowed"] is not False
        or fixture["broker_handoff_allowed"] is not False
        or fixture["live_device_access_allowed"] is not False
        or fixture["ssh_allowed"] is not False
        or fixture["config_change_allowed"] is not False
        or fixture["adapter_invocation_allowed"] is not False
    )
    required_categories_present = all(count >= 3 for count in category_counts.values())
    positive_not_rejected_count = category_counts["positive"]
    success_criteria_met = (
        required_categories_present
        and accepted_count == category_counts["positive"]
        and positive_not_rejected_count >= 3
        and unsupported_clear_rejection_count == category_counts["negative"]
        and malformed_no_crash_count == category_counts["malformed"]
        and ambiguous_rejected_count == category_counts["ambiguous"]
        and unsafe_blocked_count == category_counts["unsafe"]
        and reason_missing_count == 0
        and runtime_violation_count == 0
    )
    overall_status = "PASS" if success_criteria_met else "FAIL"
    return {
        "total_fixtures": len(fixtures),
        "category_counts": category_counts,
        "required_categories_present": required_categories_present,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "positive_not_rejected_count": positive_not_rejected_count,
        "unsupported_clear_rejection_count": unsupported_clear_rejection_count,
        "malformed_no_crash_count": malformed_no_crash_count,
        "ambiguous_rejected_count": ambiguous_rejected_count,
        "unsafe_blocked_count": unsafe_blocked_count,
        "reason_missing_count": reason_missing_count,
        "runtime_violation_count": runtime_violation_count,
        "parser_capability_added": False,
        "parser_ready_for_broker": False,
        "broker_handoff_allowed": False,
        "execution_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "config_change_allowed": False,
        "success_criteria_met": success_criteria_met,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def build_success_criteria(fixtures: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    category_counts = {
        category: sum(1 for fixture in fixtures if fixture["category"] == category)
        for category in sorted(FIXTURE_CATEGORIES)
    }
    return {
        "positive": {
            "goal": "Legal read-only / report-only parser input is not incorrectly rejected.",
            "met": category_counts["positive"] >= 3
            and all(
                fixture["accepted_by_fixture_contract"] is True
                and fixture["expected_parser_status"] == "PARSED"
                for fixture in fixtures
                if fixture["category"] == "positive"
            ),
        },
        "negative": {
            "goal": "Unsupported but normally formatted input is clearly rejected.",
            "met": category_counts["negative"] >= 3
            and all(
                fixture["expected_parser_status"] == "UNSUPPORTED_OUTPUT"
                and fixture["accepted_by_fixture_contract"] is False
                and fixture["reason_present"] is True
                for fixture in fixtures
                if fixture["category"] == "negative"
            ),
        },
        "malformed": {
            "goal": "Bad format does not crash and has a clear reason.",
            "met": category_counts["malformed"] >= 3
            and all(
                fixture["expected_parser_status"] == "MALFORMED_INPUT"
                and fixture["malformed_handled_without_exception"] is True
                and fixture["reason_present"] is True
                for fixture in fixtures
                if fixture["category"] == "malformed"
            ),
        },
        "ambiguous": {
            "goal": "Ambiguous semantics are not silently accepted.",
            "met": category_counts["ambiguous"] >= 3
            and all(
                fixture["expected_parser_status"] == "AMBIGUOUS_OUTPUT"
                and fixture["ambiguous_not_silently_accepted"] is True
                and fixture["reason_present"] is True
                for fixture in fixtures
                if fixture["category"] == "ambiguous"
            ),
        },
        "unsafe": {
            "goal": "Live, mutating, SSH, and config-change intents are blocked.",
            "met": category_counts["unsafe"] >= 3
            and all(
                fixture["expected_parser_status"] == "UNSAFE_INTENT_BLOCKED"
                and fixture["unsafe_intent_blocked"] is True
                and fixture["reason_present"] is True
                for fixture in fixtures
                if fixture["category"] == "unsafe"
            ),
        },
    }


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "report_only": True,
        "static_fixture_only": True,
        "fixture_expansion_only": True,
        "parser_output_is_review_data_only": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice_runtime": True,
        "no_dashboard_post_route": True,
        **{flag: False for flag in RUNTIME_DISABLED_FLAGS},
    }


def validate_parser_fixture_expansion_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    fixtures = report.get("fixture_cases", [])

    if report.get("day") != 102:
        errors.append("day must be 102.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-fixture-expansion.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    if summary.get("total_fixtures", 0) < 15:
        errors.append("At least 15 Day102 fixtures are required.")
    if summary.get("required_categories_present") is not True:
        errors.append("All five Day102 fixture categories must have at least three cases.")
    if summary.get("success_criteria_met") is not True:
        errors.append("Day102 success criteria must be met.")
    if summary.get("reason_missing_count") != 0:
        errors.append("Rejected fixtures must include clear reasons.")
    if summary.get("runtime_violation_count") != 0:
        errors.append("Fixture rows must not enable runtime, broker, adapter, SSH, or config changes.")

    for field in (
        "parser_capability_added",
        "parser_ready_for_broker",
        "broker_handoff_allowed",
        "execution_allowed",
        "adapter_invocation_allowed",
        "executor_invocation_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "command_execution_allowed",
        "config_change_allowed",
        "dashboard_action_allowed",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
        if field in summary and summary.get(field) is not False:
            errors.append(f"summary.{field} must be false.")
    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_live_execution",
        "no_routeros_execution",
        "no_config_json_read",
        "no_openai_api",
        "no_ai_sdk_runtime",
        "no_voice",
        "dashboard_read_only",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")

    criteria = report.get("success_criteria", {})
    for category in FIXTURE_CATEGORIES:
        if criteria.get(category, {}).get("met") is not True:
            errors.append(f"success_criteria.{category}.met must be true.")

    required_fields = {
        "case_id",
        "category",
        "case_name",
        "input_source",
        "command_family",
        "raw_input_preview",
        "expected_parser_status",
        "fixture_classification",
        "accepted_by_fixture_contract",
        "reason_required",
        "reason_present",
        "reviewer_action",
        "evidence_goal",
        "parser_output_is_review_data_only",
        "executable_allowed",
        "broker_handoff_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "config_change_allowed",
        "adapter_invocation_allowed",
    }
    for fixture in fixtures:
        missing = required_fields.difference(fixture)
        case_id = fixture.get("case_id", "<unknown>")
        if missing:
            errors.append(f"{case_id} missing fields: {', '.join(sorted(missing))}.")
        category = fixture.get("category")
        if category not in FIXTURE_CATEGORIES:
            errors.append(f"{case_id} has invalid category.")
        if fixture.get("fixture_origin") != SOURCE_KIND:
            errors.append(f"{case_id} must be a Day102 static fixture.")
        if fixture.get("parser_mode") != PARSER_MODE:
            errors.append(f"{case_id} has invalid parser_mode.")
        if fixture.get("is_static_fixture") is not True:
            errors.append(f"{case_id} must be static.")
        if fixture.get("expected_parser_status") not in PARSER_STATUSES:
            errors.append(f"{case_id} has unsupported expected_parser_status.")
        if fixture.get("fixture_classification") not in FIXTURE_CLASSIFICATIONS:
            errors.append(f"{case_id} has unsupported fixture_classification.")
        if category == "positive" and fixture.get("accepted_by_fixture_contract") is not True:
            errors.append(f"{case_id} positive fixture must be accepted.")
        if category != "positive" and fixture.get("accepted_by_fixture_contract") is not False:
            errors.append(f"{case_id} rejected fixture must not be accepted.")
        if fixture.get("reason_required") and not fixture.get("reason_present"):
            errors.append(f"{case_id} rejected fixture must include a reason.")
        for field in (
            "executable_allowed",
            "broker_handoff_allowed",
            "live_device_access_allowed",
            "ssh_allowed",
            "config_change_allowed",
            "adapter_invocation_allowed",
        ):
            if fixture.get(field) is not False:
                errors.append(f"{case_id} {field} must be false.")
        if fixture.get("parser_output_is_review_data_only") is not True:
            errors.append(f"{case_id} parser output must remain review data only.")

    invariants = report.get("safety_invariants", {})
    for field in (
        "report_only",
        "static_fixture_only",
        "fixture_expansion_only",
        "parser_output_is_review_data_only",
        "no_config_json_read",
        "no_openai_api",
        "no_ai_sdk_runtime",
        "no_voice_runtime",
        "no_dashboard_post_route",
    ):
        if invariants.get(field) is not True:
            errors.append(f"safety_invariants.{field} must be true.")
    for flag in RUNTIME_DISABLED_FLAGS:
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    return errors


def write_parser_fixture_expansion_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_fixture_expansion_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_fixture_expansion_html(safe_report, html_path)
    return json_path, html_path


def write_parser_fixture_expansion_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    criteria_rows = "".join(
        "<tr>"
        f"<td>{html.escape(category)}</td>"
        f"<td>{html.escape(criteria['goal'])}</td>"
        f"<td>{html.escape(json.dumps(criteria['met']))}</td>"
        "</tr>"
        for category, criteria in report["success_criteria"].items()
    )
    fixture_rows = "".join(
        "<tr>"
        f"<td>{html.escape(fixture['case_id'])}</td>"
        f"<td>{html.escape(fixture['category'])}</td>"
        f"<td>{html.escape(fixture['case_name'])}</td>"
        f"<td>{html.escape(fixture['command_family'] or 'MISSING')}</td>"
        f"<td><code>{html.escape(fixture['raw_input_preview'])}</code></td>"
        f"<td>{html.escape(fixture['expected_parser_status'])}</td>"
        f"<td>{html.escape(json.dumps(fixture['accepted_by_fixture_contract']))}</td>"
        f"<td>{html.escape(fixture['reason'] or '')}</td>"
        f"<td>{html.escape(fixture['reviewer_action'])}</td>"
        "</tr>"
        for fixture in report["fixture_cases"]
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
  <h1>Day102 Parser Fixture Expansion</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Scope:</strong> static fixture expansion only. Day102 adds no parser capability, broker handoff, adapter connection, SSH, live device access, RouterOS execution, config change, dashboard action, OpenAI API, or voice runtime.</p>
  <h2>Summary</h2>
  <p><strong>Total fixtures:</strong> {summary['total_fixtures']} | <strong>Accepted:</strong> {summary['accepted_count']} | <strong>Rejected:</strong> {summary['rejected_count']} | <strong>Runtime violations:</strong> {summary['runtime_violation_count']} | <strong>Missing reasons:</strong> {summary['reason_missing_count']}</p>
  <p><strong>Category counts:</strong> <code>{html.escape(json.dumps(summary['category_counts'], sort_keys=True))}</code></p>
  <h2>Success Criteria</h2>
  <table>
    <thead><tr><th>Category</th><th>Goal</th><th>Met</th></tr></thead>
    <tbody>{criteria_rows}</tbody>
  </table>
  <h2>Fixture Cases</h2>
  <table>
    <thead><tr><th>Case</th><th>Category</th><th>Name</th><th>Command family</th><th>Input preview</th><th>Status</th><th>Accepted</th><th>Reason</th><th>Reviewer action</th></tr></thead>
    <tbody>{fixture_rows}</tbody>
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


def _preview_raw_input(raw_input: Optional[str]) -> str:
    if raw_input is None:
        return "<missing>"
    compact = " ".join(raw_input.split())
    if not compact:
        return "<empty>"
    return compact[:140]
