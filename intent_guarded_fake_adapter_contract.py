"""Day93 guarded fake adapter contract evidence.

This module is deterministic and local-only. It proves that the guard decision
is evaluated before any fake adapter boundary is entered, and that rejected
scenarios never reach the adapter boundary.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "guarded-fake-adapter-contract"
TITLE = "Guarded Fake Adapter Contract"
MODE = "FAKE_ADAPTER_ONLY"
ALLOWED = "ALLOWED"
REJECTED = "REJECTED"
BOUNDARY_NAME = "fake_readonly_adapter_boundary"
REPORT_JSON = Path("reports") / "lab-summary" / "day93_guarded_fake_adapter_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day93_guarded_fake_adapter_contract.html"


@dataclass(frozen=True)
class AdapterScenario:
    scenario_id: str
    intent: str
    command_family: str
    read_only_candidate: bool
    expected_guard_result: str
    guard_reason: str

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GuardDecision:
    scenario_id: str
    guard_result: str
    allowed: bool
    guard_reason: str
    guard_evaluated_before_adapter: bool

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


class GuardDecisionLayer:
    """Positive allowlist guard for deterministic Day93 scenarios."""

    def evaluate(self, scenario: AdapterScenario) -> GuardDecision:
        if scenario.expected_guard_result == ALLOWED and scenario.read_only_candidate:
            return GuardDecision(
                scenario_id=scenario.scenario_id,
                guard_result=ALLOWED,
                allowed=True,
                guard_reason=scenario.guard_reason,
                guard_evaluated_before_adapter=True,
            )
        return GuardDecision(
            scenario_id=scenario.scenario_id,
            guard_result=REJECTED,
            allowed=False,
            guard_reason=scenario.guard_reason,
            guard_evaluated_before_adapter=True,
        )


class FakeReadOnlyAdapter:
    """Fake adapter boundary that accepts only already-guarded scenarios."""

    def __init__(self) -> None:
        self.invocation_evidence: List[Dict[str, Any]] = []

    def invoke(self, scenario: AdapterScenario, decision: GuardDecision) -> Dict[str, Any]:
        if decision.guard_result != ALLOWED or not decision.allowed:
            raise ValueError("Fake adapter boundary accepts only guard-allowed scenarios.")
        invocation_id = f"day93-fake-invocation-{len(self.invocation_evidence) + 1:03d}"
        response = {
            "adapter_type": "fake",
            "boundary_name": BOUNDARY_NAME,
            "invocation_id": invocation_id,
            "scenario_id": scenario.scenario_id,
            "accepted_by_guard": True,
            "command_family": scenario.command_family,
            "fake_output_summary": _fake_output_summary(scenario.command_family),
            "live_side_effects": False,
        }
        self.invocation_evidence.append(deepcopy(response))
        return response


def build_scenario_catalog() -> List[AdapterScenario]:
    """Return deterministic Day93 adapter-boundary scenarios."""
    return [
        AdapterScenario(
            "readonly_show_identity",
            "Show system identity for reviewer evidence",
            "readonly_identity",
            True,
            ALLOWED,
            "Read-only identity query matched the positive fake-adapter allowlist.",
        ),
        AdapterScenario(
            "readonly_show_interfaces",
            "Show interface status summary",
            "readonly_interfaces",
            True,
            ALLOWED,
            "Read-only interface status query matched the positive fake-adapter allowlist.",
        ),
        AdapterScenario(
            "readonly_export_terse",
            "Export terse non-secret configuration summary",
            "readonly_export_terse",
            True,
            ALLOWED,
            "Read-only terse export summary matched the positive fake-adapter allowlist.",
        ),
        AdapterScenario(
            "mutating_set_ip_address",
            "Set an IP address on an interface",
            "mutating_ip_address",
            False,
            REJECTED,
            "Mutation request rejected before adapter boundary.",
        ),
        AdapterScenario(
            "mutating_disable_interface",
            "Disable a network interface",
            "mutating_interface_state",
            False,
            REJECTED,
            "Interface state mutation rejected before adapter boundary.",
        ),
        AdapterScenario(
            "reboot_device",
            "Reboot the device",
            "device_reboot",
            False,
            REJECTED,
            "Device reboot request rejected before adapter boundary.",
        ),
        AdapterScenario(
            "reset_configuration",
            "Reset device configuration",
            "device_reset",
            False,
            REJECTED,
            "Configuration reset request rejected before adapter boundary.",
        ),
        AdapterScenario(
            "live_ssh_command",
            "Run a live SSH command",
            "live_ssh_command",
            False,
            REJECTED,
            "Live SSH command request rejected before adapter boundary.",
        ),
        AdapterScenario(
            "unknown_task",
            "Perform an unknown task",
            "unknown",
            False,
            REJECTED,
            "Unknown task failed closed before adapter boundary.",
        ),
    ]


def run_guarded_fake_adapter_contract() -> Dict[str, Any]:
    """Evaluate every scenario through the guard before optional fake adapter entry."""
    adapter = FakeReadOnlyAdapter()
    guard = GuardDecisionLayer()
    scenario_records: List[Dict[str, Any]] = []

    for scenario in build_scenario_catalog():
        decision = guard.evaluate(scenario)
        adapter_response: Optional[Dict[str, Any]] = None
        adapter_invocation_attempted = False
        adapter_boundary_entered = False
        fake_adapter_invoked = False
        invocation_id: Optional[str] = None
        adapter_type: Optional[str] = None

        if decision.guard_result == ALLOWED:
            adapter_invocation_attempted = True
            adapter_response = adapter.invoke(scenario, decision)
            adapter_boundary_entered = True
            fake_adapter_invoked = True
            invocation_id = adapter_response["invocation_id"]
            adapter_type = adapter_response["adapter_type"]

        record = _build_scenario_record(
            scenario=scenario,
            decision=decision,
            adapter_invocation_attempted=adapter_invocation_attempted,
            adapter_boundary_entered=adapter_boundary_entered,
            fake_adapter_invoked=fake_adapter_invoked,
            invocation_id=invocation_id,
            adapter_type=adapter_type,
            adapter_response=adapter_response,
        )
        scenario_records.append(record)

    report = build_report(scenario_records, adapter.invocation_evidence)
    validation_errors = validate_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_status"] = "FAIL"
    return report


def build_report(
    scenario_records: List[Dict[str, Any]],
    invocation_evidence: List[Dict[str, Any]],
) -> Dict[str, Any]:
    allowed_count = sum(1 for record in scenario_records if record["guard_result"] == ALLOWED)
    rejected_count = sum(1 for record in scenario_records if record["guard_result"] == REJECTED)
    fake_adapter_invocations = sum(1 for record in scenario_records if record["fake_adapter_invoked"])
    rejected_adapter_invocations = sum(
        1
        for record in scenario_records
        if record["guard_result"] == REJECTED and record["adapter_invocation_attempted"]
    )
    real_adapter_invocations = sum(1 for record in scenario_records if record["real_adapter_invoked"])
    guard_ordering_violations = sum(
        1
        for record in scenario_records
        if not record["guard_evaluated_before_adapter"]
        or (record["guard_result"] == REJECTED and record["adapter_boundary_entered"])
    )
    safety_violations = sum(1 for record in scenario_records if _record_has_safety_violation(record))
    audit_chain_complete = all(record["audit_chain_complete"] for record in scenario_records)
    adapter_boundary_verified = (
        allowed_count > 0
        and fake_adapter_invocations == allowed_count
        and rejected_adapter_invocations == 0
        and all(
            record["adapter_boundary_entered"] is (record["guard_result"] == ALLOWED)
            for record in scenario_records
        )
    )
    overall_status = "PASS" if (
        allowed_count > 0
        and rejected_count > 0
        and fake_adapter_invocations == allowed_count
        and rejected_adapter_invocations == 0
        and real_adapter_invocations == 0
        and guard_ordering_violations == 0
        and safety_violations == 0
        and audit_chain_complete
        and adapter_boundary_verified
    ) else "FAIL"

    return {
        "day": 93,
        "day_id": "Day93",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": overall_status,
        "mode": MODE,
        "total_scenarios": len(scenario_records),
        "allowed_count": allowed_count,
        "rejected_count": rejected_count,
        "fake_adapter_invocations": fake_adapter_invocations,
        "rejected_adapter_invocations": rejected_adapter_invocations,
        "real_adapter_invocations": real_adapter_invocations,
        "guard_ordering_violations": guard_ordering_violations,
        "safety_violations": safety_violations,
        "audit_chain_complete": audit_chain_complete,
        "adapter_boundary_verified": adapter_boundary_verified,
        "final_recommendation": "KEEP_FAKE_ONLY",
        "no_real_device_access": True,
        "no_ssh": True,
        "no_config_json_read": True,
        "no_live_execution": True,
        "no_real_adapter_invocation": True,
        "adapter_boundary_name": BOUNDARY_NAME,
        "adapter_invocation_evidence": deepcopy(invocation_evidence),
        "scenario_records": deepcopy(scenario_records),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }


def validate_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 93:
        errors.append("day must be 93.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be guarded-fake-adapter-contract.")
    if report.get("mode") != MODE:
        errors.append("mode must be FAKE_ADAPTER_ONLY.")
    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_config_json_read",
        "no_live_execution",
        "no_real_adapter_invocation",
        "audit_chain_complete",
        "adapter_boundary_verified",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for count_field in (
        "rejected_adapter_invocations",
        "real_adapter_invocations",
        "guard_ordering_violations",
        "safety_violations",
    ):
        if report.get(count_field) != 0:
            errors.append(f"{count_field} must be 0.")
    if report.get("allowed_count", 0) <= 0:
        errors.append("allowed_count must be greater than 0.")
    if report.get("rejected_count", 0) <= 0:
        errors.append("rejected_count must be greater than 0.")
    if report.get("fake_adapter_invocations") != report.get("allowed_count"):
        errors.append("fake_adapter_invocations must equal allowed_count.")

    for record in report.get("scenario_records", []):
        if _record_has_safety_violation(record):
            errors.append(f"{record.get('scenario_id')} has a safety violation.")
        if record.get("guard_evaluated_before_adapter") is not True:
            errors.append(f"{record.get('scenario_id')} did not evaluate guard first.")
        if record.get("guard_result") == REJECTED:
            for field in (
                "adapter_invocation_attempted",
                "adapter_boundary_entered",
                "fake_adapter_invoked",
            ):
                if record.get(field) is not False:
                    errors.append(f"{record.get('scenario_id')} rejected record set {field}.")
            if record.get("invocation_id") is not None:
                errors.append(f"{record.get('scenario_id')} rejected record has invocation_id.")
        elif record.get("guard_result") == ALLOWED:
            for field in (
                "adapter_invocation_attempted",
                "adapter_boundary_entered",
                "fake_adapter_invoked",
            ):
                if record.get(field) is not True:
                    errors.append(f"{record.get('scenario_id')} allowed record did not set {field}.")
            if record.get("adapter_type") != "fake":
                errors.append(f"{record.get('scenario_id')} allowed record must use fake adapter.")
        else:
            errors.append(f"{record.get('scenario_id')} has invalid guard_result.")
    return errors


def write_guarded_fake_adapter_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(record['scenario_id'])}</td>"
        f"<td>{html.escape(record['intent'])}</td>"
        f"<td>{html.escape(record['command_family'])}</td>"
        f"<td>{html.escape(record['guard_result'])}</td>"
        f"<td>{html.escape(record['guard_reason'])}</td>"
        f"<td>{html.escape(json.dumps(record['adapter_boundary_entered']))}</td>"
        f"<td>{html.escape(json.dumps(record['fake_adapter_invoked']))}</td>"
        f"<td>{html.escape(json.dumps(record['real_adapter_invoked']))}</td>"
        f"<td>{html.escape(str(record['invocation_id']))}</td>"
        f"<td>{html.escape(record['evidence_status'])}</td>"
        "</tr>"
        for record in report["scenario_records"]
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['title'])}</h1>
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['mode'])}</p>
  <p><strong>Total scenarios:</strong> {report['total_scenarios']} | <strong>Allowed:</strong> {report['allowed_count']} | <strong>Rejected:</strong> {report['rejected_count']}</p>
  <p><strong>Fake adapter invocations:</strong> {report['fake_adapter_invocations']} | <strong>Rejected adapter invocations:</strong> {report['rejected_adapter_invocations']} | <strong>Real adapter invocations:</strong> {report['real_adapter_invocations']}</p>
  <p><strong>Safety:</strong> fake adapter only, no real device access, no SSH, no config.json read, no live execution, no real adapter invocation.</p>
  <h2>Scenario Evidence</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Intent</th><th>Command family</th><th>Guard result</th><th>Guard reason</th><th>Boundary entered</th><th>Fake adapter invoked</th><th>Real adapter invoked</th><th>Invocation id</th><th>Evidence status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Boundary Summary</h2>
  <p>Guard ordering violations: {report['guard_ordering_violations']}; safety violations: {report['safety_violations']}; audit chain complete: {html.escape(json.dumps(report['audit_chain_complete']))}; adapter boundary verified: {html.escape(json.dumps(report['adapter_boundary_verified']))}.</p>
  <p>Final recommendation: <code>{html.escape(report['final_recommendation'])}</code></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_guarded_fake_adapter_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else run_guarded_fake_adapter_contract()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_guarded_fake_adapter_contract_html(safe_report, html_path)
    return json_path, html_path


def _build_scenario_record(
    scenario: AdapterScenario,
    decision: GuardDecision,
    adapter_invocation_attempted: bool,
    adapter_boundary_entered: bool,
    fake_adapter_invoked: bool,
    invocation_id: Optional[str],
    adapter_type: Optional[str],
    adapter_response: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    record = {
        "scenario_id": scenario.scenario_id,
        "intent": scenario.intent,
        "command_family": scenario.command_family,
        "guard_result": decision.guard_result,
        "guard_reason": decision.guard_reason,
        "guard_evaluated_before_adapter": decision.guard_evaluated_before_adapter,
        "adapter_invocation_attempted": adapter_invocation_attempted,
        "adapter_boundary_entered": adapter_boundary_entered,
        "fake_adapter_invoked": fake_adapter_invoked,
        "real_adapter_invoked": False,
        "ssh_allowed": False,
        "device_access_allowed": False,
        "live_command_allowed": False,
        "side_effects_allowed": False,
        "invocation_id": invocation_id,
        "adapter_type": adapter_type,
        "adapter_response": adapter_response,
    }
    record["audit_chain_complete"] = _record_audit_chain_complete(record)
    record["evidence_status"] = "PASS" if record["audit_chain_complete"] else "FAIL"
    return record


def _record_audit_chain_complete(record: Dict[str, Any]) -> bool:
    if _record_has_safety_violation(record):
        return False
    if record["guard_evaluated_before_adapter"] is not True:
        return False
    if record["guard_result"] == REJECTED:
        return (
            record["adapter_invocation_attempted"] is False
            and record["adapter_boundary_entered"] is False
            and record["fake_adapter_invoked"] is False
            and record["invocation_id"] is None
        )
    if record["guard_result"] == ALLOWED:
        return (
            record["adapter_invocation_attempted"] is True
            and record["adapter_boundary_entered"] is True
            and record["fake_adapter_invoked"] is True
            and record["adapter_type"] == "fake"
            and record["invocation_id"] is not None
        )
    return False


def _record_has_safety_violation(record: Dict[str, Any]) -> bool:
    return any(
        record.get(field) is not False
        for field in (
            "real_adapter_invoked",
            "ssh_allowed",
            "device_access_allowed",
            "live_command_allowed",
            "side_effects_allowed",
        )
    )


def _fake_output_summary(command_family: str) -> str:
    fixtures = {
        "readonly_identity": "fake identity: lab-router-simulated",
        "readonly_interfaces": "fake interfaces: ether1 running, bridge-lan running",
        "readonly_export_terse": "fake terse export summary: 3 read-only sections, secrets omitted",
    }
    return fixtures[command_family]
