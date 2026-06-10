"""Day95 adapter result normalization evidence.

This module is deterministic and local-only. It normalizes only fake adapter
boundary results for guard-allowed scenarios, and rejected scenarios produce no
adapter result at all.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "adapter-result-normalization"
TITLE = "Adapter Result Normalization"
PHASE = "FAKE_ONLY_EVIDENCE_HARDENING"
SCHEMA_VERSION = "day95.adapter_result.v1"
RESULT_KIND = "normalized_fake_adapter_result"
SOURCE_BOUNDARY = "guarded_fake_adapter_boundary"
DETERMINISTIC_FAKE_STATUS = "FAKE_RESULT_READY"
ALLOW = "ALLOW"
REJECT = "REJECT"
REPORT_JSON = Path("reports") / "lab-summary" / "day95_adapter_result_normalization.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day95_adapter_result_normalization.html"


@dataclass(frozen=True)
class AdapterResultScenario:
    scenario_id: str
    intent: str
    command_family: str
    guard_decision: str
    readonly_intent: bool
    simulated_output: str
    reason: str
    unsafe_category: str = "none"

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


class DeterministicFakeAdapterBoundary:
    """Fake boundary that emits fixed status for already-allowed scenarios."""

    def __init__(self) -> None:
        self.invocations: List[Dict[str, Any]] = []

    def invoke(self, scenario: AdapterResultScenario) -> Dict[str, Any]:
        if scenario.guard_decision != ALLOW or not scenario.readonly_intent:
            raise ValueError("Fake adapter boundary accepts only guard-allowed read-only scenarios.")
        invocation_id = f"day95-fake-boundary-{len(self.invocations) + 1:03d}"
        result = {
            "invocation_id": invocation_id,
            "scenario_id": scenario.scenario_id,
            "adapter_type": "fake",
            "source_boundary": SOURCE_BOUNDARY,
            "deterministic_status": DETERMINISTIC_FAKE_STATUS,
            "command_family": scenario.command_family,
            "readonly_intent": True,
            "simulated_output": scenario.simulated_output,
            "parser_ready": True,
        }
        self.invocations.append(deepcopy(result))
        return result


def build_day95_scenarios() -> List[AdapterResultScenario]:
    """Return deterministic Day95 normalization scenarios."""
    return [
        AdapterResultScenario(
            scenario_id="D95-S01-readonly-identity",
            intent="Normalize fake identity evidence",
            command_family="readonly_identity",
            guard_decision=ALLOW,
            readonly_intent=True,
            simulated_output="name: lab-router-simulated",
            reason="Allowed read-only identity scenario reaches fake boundary.",
        ),
        AdapterResultScenario(
            scenario_id="D95-S02-readonly-interfaces-multiline",
            intent="Normalize fake multi-line interface evidence",
            command_family="readonly_interfaces",
            guard_decision=ALLOW,
            readonly_intent=True,
            simulated_output="ether1 running\nbridge-lan running\nwireguard-lab disabled",
            reason="Allowed read-only interface scenario proves multi-line parser-ready payload.",
        ),
        AdapterResultScenario(
            scenario_id="D95-S03-reject-write-capable",
            intent="Set interface address",
            command_family="write_interface_address",
            guard_decision=REJECT,
            readonly_intent=False,
            simulated_output="",
            reason="Write-capable request is rejected before adapter result creation.",
            unsafe_category="write_capable",
        ),
        AdapterResultScenario(
            scenario_id="D95-S04-reject-live-capable",
            intent="Run live command transport",
            command_family="live_transport_command",
            guard_decision=REJECT,
            readonly_intent=False,
            simulated_output="",
            reason="Live-capable request is rejected before fake adapter invocation.",
            unsafe_category="live_capable",
        ),
        AdapterResultScenario(
            scenario_id="D95-S05-reject-ambiguous-unsafe",
            intent="Inspect or repair unknown device state",
            command_family="ambiguous_unknown",
            guard_decision=REJECT,
            readonly_intent=False,
            simulated_output="",
            reason="Ambiguous request fails closed and produces no adapter result.",
            unsafe_category="ambiguous_unsafe",
        ),
    ]


def run_adapter_result_normalization() -> Dict[str, Any]:
    adapter = DeterministicFakeAdapterBoundary()
    scenario_records: List[Dict[str, Any]] = []
    normalized_results: List[Dict[str, Any]] = []
    rejection_records: List[Dict[str, Any]] = []

    for scenario in build_day95_scenarios():
        adapter_invoked = False
        fake_boundary_result: Optional[Dict[str, Any]] = None
        adapter_result: Optional[Dict[str, Any]] = None

        if scenario.guard_decision == ALLOW:
            fake_boundary_result = adapter.invoke(scenario)
            adapter_invoked = True
            adapter_result = normalize_fake_adapter_result(scenario, fake_boundary_result)
            normalized_results.append(deepcopy(adapter_result))

        record = build_scenario_record(
            scenario=scenario,
            adapter_invoked=adapter_invoked,
            fake_boundary_result=fake_boundary_result,
            adapter_result=adapter_result,
        )
        scenario_records.append(record)
        if scenario.guard_decision == REJECT:
            rejection_records.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "guard_decision": REJECT,
                    "adapter_invoked": False,
                    "adapter_result_present": False,
                    "result_payload_present": False,
                    "reason": scenario.reason,
                    "unsafe_category": scenario.unsafe_category,
                }
            )

    summary = build_summary(scenario_records, normalized_results, rejection_records)
    report = {
        "day": 95,
        "day_id": "Day95",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "overall_status": summary["overall_status"],
        "summary": summary,
        "normalized_schema": build_normalized_schema_summary(),
        "scenario_records": scenario_records,
        "normalized_result_records": normalized_results,
        "rejection_records": rejection_records,
        "fake_boundary_invocation_evidence": deepcopy(adapter.invocations),
        "safety_invariant_summary": build_safety_invariant_summary(summary),
        "evidence_chain_summary": build_evidence_chain_summary(),
        "references": {
            "day93": {
                "task": "guarded-fake-adapter-contract",
                "report": "reports/lab-summary/day93_guarded_fake_adapter_contract.json",
                "evidence": "Guard-first fake adapter boundary audit.",
            },
            "day94": {
                "task": "adapter-boundary-regression-matrix",
                "report": "reports/lab-summary/day94_adapter_boundary_regression_matrix.json",
                "evidence": "Adapter boundary regression matrix.",
            },
        },
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_execution": True,
        "no_real_adapter_invocation": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "no_config_json_read": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
    return report


def normalize_fake_adapter_result(
    scenario: AdapterResultScenario,
    fake_boundary_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Normalize a deterministic fake boundary result into the Day95 schema."""
    result_status = fake_boundary_result["deterministic_status"]
    return {
        "schema_version": SCHEMA_VERSION,
        "result_kind": RESULT_KIND,
        "adapter_type": "fake",
        "source_boundary": SOURCE_BOUNDARY,
        "scenario_id": scenario.scenario_id,
        "guard_decision": ALLOW,
        "adapter_invoked": True,
        "result_status": result_status,
        "result_payload": {
            "command_family": fake_boundary_result["command_family"],
            "readonly_intent": fake_boundary_result["readonly_intent"],
            "simulated_output": fake_boundary_result["simulated_output"],
            "parser_ready": fake_boundary_result["parser_ready"],
        },
        "safety": {
            "real_adapter_result_present": False,
            "live_execution_result_present": False,
            "ssh_used": False,
            "device_access_used": False,
            "execution_unlocked": False,
        },
        "evidence": {
            "day93_guarded_fake_adapter_boundary_audit": True,
            "day94_adapter_boundary_regression_matrix": True,
            "normalization_applied": True,
        },
    }


def build_scenario_record(
    scenario: AdapterResultScenario,
    adapter_invoked: bool,
    fake_boundary_result: Optional[Dict[str, Any]],
    adapter_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    record = {
        **scenario.to_record(),
        "adapter_invoked": adapter_invoked,
        "fake_adapter_invoked": adapter_invoked,
        "real_adapter_invoked": False,
        "live_execution_invoked": False,
        "ssh_used": False,
        "device_access_used": False,
        "dashboard_action_allowed": False,
        "adapter_result": adapter_result,
        "adapter_result_present": adapter_result is not None,
        "fake_boundary_result_status": (
            fake_boundary_result["deterministic_status"] if fake_boundary_result else None
        ),
    }
    record["scenario_status"] = "PASS" if scenario_record_passes(record) else "FAIL"
    return record


def scenario_record_passes(record: Dict[str, Any]) -> bool:
    if record["real_adapter_invoked"] or record["live_execution_invoked"]:
        return False
    if record["ssh_used"] or record["device_access_used"] or record["dashboard_action_allowed"]:
        return False
    if record["guard_decision"] == ALLOW:
        return (
            record["adapter_invoked"] is True
            and record["adapter_result_present"] is True
            and record["adapter_result"]["result_status"] == DETERMINISTIC_FAKE_STATUS
        )
    if record["guard_decision"] == REJECT:
        return (
            record["adapter_invoked"] is False
            and record["adapter_result"] is None
            and record["adapter_result_present"] is False
            and record["fake_boundary_result_status"] is None
        )
    return False


def build_summary(
    scenario_records: List[Dict[str, Any]],
    normalized_results: List[Dict[str, Any]],
    rejection_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    total_scenarios = len(scenario_records)
    allowed_count = sum(1 for record in scenario_records if record["guard_decision"] == ALLOW)
    rejected_count = sum(1 for record in scenario_records if record["guard_decision"] == REJECT)
    normalized_result_count = len(normalized_results)
    fake_adapter_result_count = normalized_result_count
    real_adapter_result_count = sum(
        1
        for result in normalized_results
        if result["safety"]["real_adapter_result_present"] is not False
    )
    live_execution_result_count = sum(
        1
        for result in normalized_results
        if result["safety"]["live_execution_result_present"] is not False
    )
    rejected_with_adapter_result = sum(
        1
        for record in scenario_records
        if record["guard_decision"] == REJECT and record["adapter_result_present"]
    )
    scenario_failures = sum(1 for record in scenario_records if record["scenario_status"] != "PASS")
    result_status_values = sorted({result["result_status"] for result in normalized_results})
    evidence_chain_complete = all(
        result["evidence"]["day93_guarded_fake_adapter_boundary_audit"]
        and result["evidence"]["day94_adapter_boundary_regression_matrix"]
        and result["evidence"]["normalization_applied"]
        for result in normalized_results
    )
    overall_status = "PASS" if (
        total_scenarios == 5
        and allowed_count == 2
        and rejected_count == 3
        and normalized_result_count == allowed_count
        and fake_adapter_result_count == allowed_count
        and len(rejection_records) == rejected_count
        and rejected_with_adapter_result == 0
        and real_adapter_result_count == 0
        and live_execution_result_count == 0
        and scenario_failures == 0
        and result_status_values == [DETERMINISTIC_FAKE_STATUS]
        and evidence_chain_complete
    ) else "FAIL"
    return {
        "total_scenarios": total_scenarios,
        "allowed_count": allowed_count,
        "rejected_count": rejected_count,
        "normalized_result_count": normalized_result_count,
        "fake_adapter_result_count": fake_adapter_result_count,
        "rejection_record_count": len(rejection_records),
        "rejected_with_adapter_result": rejected_with_adapter_result,
        "real_adapter_result_count": real_adapter_result_count,
        "live_execution_result_count": live_execution_result_count,
        "scenario_failures": scenario_failures,
        "result_status_values": result_status_values,
        "result_status_source": "deterministic_fake_boundary",
        "evidence_chain_complete": evidence_chain_complete,
        "overall_status": overall_status,
    }


def build_normalized_schema_summary() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "result_kind": RESULT_KIND,
        "required_top_level_fields": [
            "schema_version",
            "result_kind",
            "adapter_type",
            "source_boundary",
            "scenario_id",
            "guard_decision",
            "adapter_invoked",
            "result_status",
            "result_payload",
            "safety",
            "evidence",
        ],
        "payload_fields": [
            "command_family",
            "readonly_intent",
            "simulated_output",
            "parser_ready",
        ],
        "safety_fields": [
            "real_adapter_result_present",
            "live_execution_result_present",
            "ssh_used",
            "device_access_used",
            "execution_unlocked",
        ],
        "status_source": "deterministic_fake_boundary",
    }


def build_safety_invariant_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "fake_only": True,
        "deterministic_only": True,
        "report_only": True,
        "read_only_dashboard": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "no_ssh": True,
        "no_device_access": True,
        "no_live_execution": summary["live_execution_result_count"] == 0,
        "no_real_adapter_result": summary["real_adapter_result_count"] == 0,
        "no_mapped_task_execution": True,
        "no_dashboard_action": True,
        "no_post_route": True,
        "no_execution_approval_mechanism": True,
        "rejected_scenarios_have_no_adapter_result": summary["rejected_with_adapter_result"] == 0,
    }


def build_evidence_chain_summary() -> Dict[str, Any]:
    return {
        "day93_guarded_fake_adapter_boundary_audit": True,
        "day94_adapter_boundary_regression_matrix": True,
        "day95_normalization_applied": True,
        "chain": [
            "Day93 proved guard-approved scenarios are the only ones reaching the fake adapter boundary.",
            "Day94 expanded that proof into regression matrix evidence.",
            "Day95 normalizes only deterministic fake adapter results and leaves rejected scenarios result-free.",
        ],
    }


def validate_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    scenario_records = report.get("scenario_records", [])
    normalized_results = report.get("normalized_result_records", [])

    if report.get("day") != 95:
        errors.append("day must be 95.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be adapter-result-normalization.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_live_execution",
        "no_real_adapter_invocation",
        "no_openai_api",
        "no_ai_sdk_runtime",
        "no_voice",
        "no_config_json_read",
        "dashboard_read_only",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    if report.get("dashboard_action_allowed") is not False:
        errors.append("dashboard_action_allowed must be false.")
    for count_field in (
        "real_adapter_result_count",
        "live_execution_result_count",
        "rejected_with_adapter_result",
        "scenario_failures",
    ):
        if summary.get(count_field) != 0:
            errors.append(f"{count_field} must be 0.")
    if summary.get("normalized_result_count") != summary.get("allowed_count"):
        errors.append("normalized_result_count must equal allowed_count.")
    if summary.get("fake_adapter_result_count") != summary.get("allowed_count"):
        errors.append("fake_adapter_result_count must equal allowed_count.")
    if summary.get("result_status_values") != [DETERMINISTIC_FAKE_STATUS]:
        errors.append("result_status_values must come only from deterministic fake boundary.")
    if summary.get("result_status_source") != "deterministic_fake_boundary":
        errors.append("result_status_source must be deterministic_fake_boundary.")
    if summary.get("evidence_chain_complete") is not True:
        errors.append("evidence_chain_complete must be true.")

    schema_fields = report.get("normalized_schema", {}).get("required_top_level_fields", [])
    for result in normalized_results:
        missing = [field for field in schema_fields if field not in result]
        if missing:
            errors.append(f"{result.get('scenario_id')} missing schema fields: {', '.join(missing)}.")
        if result.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{result.get('scenario_id')} has wrong schema_version.")
        if result.get("result_kind") != RESULT_KIND:
            errors.append(f"{result.get('scenario_id')} has wrong result_kind.")
        if result.get("adapter_type") != "fake":
            errors.append(f"{result.get('scenario_id')} adapter_type must be fake.")
        if result.get("result_status") != DETERMINISTIC_FAKE_STATUS:
            errors.append(f"{result.get('scenario_id')} result_status must be deterministic fake status.")
        if any(result.get("safety", {}).values()):
            errors.append(f"{result.get('scenario_id')} has a safety flag set true.")
        if not all(result.get("evidence", {}).values()):
            errors.append(f"{result.get('scenario_id')} evidence chain is incomplete.")

    for record in scenario_records:
        if not scenario_record_passes(record):
            errors.append(f"{record.get('scenario_id')} scenario record failed.")
        if record.get("guard_decision") == REJECT and record.get("adapter_result") is not None:
            errors.append(f"{record.get('scenario_id')} rejected scenario has adapter_result.")
    return errors


def write_adapter_result_normalization_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    scenario_rows = "".join(
        "<tr>"
        f"<td>{html.escape(record['scenario_id'])}</td>"
        f"<td>{html.escape(record['intent'])}</td>"
        f"<td>{html.escape(record['command_family'])}</td>"
        f"<td>{html.escape(record['guard_decision'])}</td>"
        f"<td>{html.escape(json.dumps(record['adapter_invoked']))}</td>"
        f"<td>{html.escape(json.dumps(record['adapter_result_present']))}</td>"
        f"<td>{html.escape(str(record['fake_boundary_result_status']))}</td>"
        f"<td>{html.escape(record['scenario_status'])}</td>"
        f"<td>{html.escape(record['reason'])}</td>"
        "</tr>"
        for record in report["scenario_records"]
    )
    schema_fields = ", ".join(report["normalized_schema"]["required_top_level_fields"])
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
  <h1>Day95 Adapter Result Normalization</h1>
  <p><strong>Overall status:</strong> <span class="{html.escape(report['overall_status'].lower())}">{html.escape(report['overall_status'])}</span> / {html.escape(report['phase'])}</p>
  <p><strong>Fake-only safety boundary:</strong> deterministic fake adapter result normalization only; no SSH, no device access, no RouterOS connection, no real adapter result, no live execution result, no dashboard action.</p>
  <h2>Normalized Schema Summary</h2>
  <p><strong>Schema version:</strong> <code>{html.escape(report['normalized_schema']['schema_version'])}</code></p>
  <p><strong>Result kind:</strong> <code>{html.escape(report['normalized_schema']['result_kind'])}</code></p>
  <p><strong>Required fields:</strong> {html.escape(schema_fields)}</p>
  <p><strong>Result status source:</strong> <code>{html.escape(summary['result_status_source'])}</code>; values: <code>{html.escape(', '.join(summary['result_status_values']))}</code></p>
  <h2>Scenario Evidence</h2>
  <p><strong>Total scenarios:</strong> {summary['total_scenarios']} | <strong>Allowed:</strong> {summary['allowed_count']} | <strong>Rejected:</strong> {summary['rejected_count']} | <strong>Normalized results:</strong> {summary['normalized_result_count']}</p>
  <table>
    <thead><tr><th>Scenario</th><th>Intent</th><th>Command family</th><th>Guard</th><th>Fake adapter invoked</th><th>Adapter result present</th><th>Fake status</th><th>Status</th><th>Reason</th></tr></thead>
    <tbody>{scenario_rows}</tbody>
  </table>
  <h2>Evidence Chain</h2>
  <p>Day93 guarded fake adapter boundary audit: true. Day94 adapter boundary regression matrix: true. Day95 normalization applied: true.</p>
  <p>Real adapter result count = {summary['real_adapter_result_count']}; live execution result count = {summary['live_execution_result_count']}; rejected scenarios with adapter result = {summary['rejected_with_adapter_result']}.</p>
  <p>Explicit absence statement: real adapter result and live execution result are absent.</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_adapter_result_normalization_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else run_adapter_result_normalization()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_adapter_result_normalization_html(safe_report, html_path)
    return json_path, html_path
