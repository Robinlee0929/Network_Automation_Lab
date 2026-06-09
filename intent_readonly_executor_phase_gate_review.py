"""Day87 read-only executor phase gate review.

This module reviews the Day83-Day86 read-only executor safety evidence chain
and decides whether Day88 may start a design draft. It is report-only: it does
not design or implement a real adapter, connect to devices, or execute commands.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_controlled_runner_harness import build_controlled_runner_harness_report
from intent_mock_adapter_evidence_binding import build_mock_adapter_evidence_binding_report
from intent_readonly_executor_adapter_contract import build_readonly_executor_adapter_contract_report
from intent_readonly_executor_readiness_gate import build_readonly_executor_readiness_gate_report


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "readonly-executor-phase-gate-review"
PHASE_NAME = "Day87 Read-only Executor Phase Gate Review"
TITLE = "Day87 Read-only Executor Phase Gate Review"
ALLOWED_NEXT_STEP = "Real Read-only Executor Adapter Design Draft"
PHASE_GATE_RECOMMENDATION = "DESIGN_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day87_readonly_executor_phase_gate_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day87_readonly_executor_phase_gate_review.html"

REQUIRED_FALSE_FLAGS = (
    "execution_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "write_command_allowed",
    "device_connection_allowed",
    "real_adapter_implementation_allowed",
)
REQUIRED_TRUE_FLAGS = ("real_adapter_design_allowed",)
REQUIRED_GATE_CHECKS = (
    "day83-readiness-gate-review-only",
    "day84-adapter-contract-read-only",
    "day85-mock-evidence-binding-deterministic",
    "day86-controlled-runner-execution-blocked",
    "no-ssh-path-enabled",
    "no-live-command-path-enabled",
    "no-write-command-path-enabled",
    "no-execution-unlock-exists",
    "dashboard-surface-static-read-only",
    "runner-task-only-emits-reports",
)


def _review_safety_flags() -> Dict[str, bool]:
    return {
        "execution_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "write_command_allowed": False,
        "device_connection_allowed": False,
        "real_adapter_implementation_allowed": False,
        "real_adapter_design_allowed": True,
    }


def _check(
    check_id: str,
    title: str,
    passed: bool,
    evidence_refs: List[str],
    failure_message: str,
    severity: str = "REVIEW_REQUIRED",
) -> Dict[str, Any]:
    result = {
        "check_id": check_id,
        "title": title,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "evidence_refs": evidence_refs,
        "severity_if_failed": severity,
    }
    if not passed:
        result["message"] = failure_message
    return result


def _all_values(records: List[Dict[str, Any]], field: str, expected: Any) -> bool:
    return bool(records) and all(record.get(field) is expected for record in records)


def _flag(report: Dict[str, Any], field: str) -> Any:
    if field in report:
        return report.get(field)
    return report.get("safety_invariants", {}).get(field)


def _source_reports(
    day83_report: Optional[Dict[str, Any]],
    day84_report: Optional[Dict[str, Any]],
    day85_report: Optional[Dict[str, Any]],
    day86_report: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    return (
        deepcopy(day83_report) if day83_report is not None else build_readonly_executor_readiness_gate_report(),
        deepcopy(day84_report) if day84_report is not None else build_readonly_executor_adapter_contract_report(),
        deepcopy(day85_report) if day85_report is not None else build_mock_adapter_evidence_binding_report(),
        deepcopy(day86_report) if day86_report is not None else build_controlled_runner_harness_report(),
    )


def build_phase_gate_checks(
    day83_report: Dict[str, Any],
    day84_report: Dict[str, Any],
    day85_report: Dict[str, Any],
    day86_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Build the required deterministic Day87 phase gate checks."""
    day84_flags = day84_report.get("adapter_safety_flags", {})
    day85_records = day85_report.get("adapter_records", [])
    day86_flags = day86_report.get("safety_invariants", {})
    day86_locks = day86_report.get("summary", {}).get("safety_lock_summary", {})

    return [
        _check(
            "day83-readiness-gate-review-only",
            "Day83 readiness gate exists conceptually and remains review-only.",
            (
                day83_report.get("overall_status") == "PASS"
                and day83_report.get("readiness_state") == "READINESS_REVIEW_READY"
                and day83_report.get("readonly_executor_candidate") is True
                and day83_report.get("executor_allowed") is False
                and day83_report.get("live_execution_allowed") is False
                and day83_report.get("ssh_allowed") is False
                and day83_report.get("candidate_scope", {}).get("future_adapter_design_review_only") is True
            ),
            ["Day83", "intent_readonly_executor_readiness_gate"],
            "Day83 is missing, failed, or no longer review-only.",
        ),
        _check(
            "day84-adapter-contract-read-only",
            "Day84 adapter interface contract remains read-only.",
            (
                day84_report.get("overall_status") == "PASS"
                and day84_report.get("adapter_boundary", {}).get("implements_executor") is False
                and day84_report.get("adapter_boundary", {}).get("implements_adapter") is False
                and day84_flags.get("read_only_only") is True
                and day84_flags.get("dry_run_only") is True
                and day84_flags.get("allowed_to_execute") is False
                and day84_flags.get("live_command_allowed") is False
                and day84_flags.get("adapter_implementation_present") is False
                and day84_report.get("adapter_capability_declaration_shape", {}).get("supported_transports")
                == ["none_contract_only"]
            ),
            ["Day84", "intent_readonly_executor_adapter_contract"],
            "Day84 contract evidence is missing, failed, or exposes adapter/runtime capability.",
        ),
        _check(
            "day85-mock-evidence-binding-deterministic",
            "Day85 mock adapter evidence binding remains deterministic.",
            (
                day85_report.get("overall_status") == "PASS"
                and day85_report.get("final_recommendation") == "REVIEW_ONLY"
                and day85_report.get("traceability_summary", {}).get("all_responses_bound_to_request") is True
                and day85_report.get("traceability_summary", {}).get("all_responses_bound_to_day84_contract") is True
                and day85_report.get("traceability_summary", {}).get("all_responses_bound_to_evidence") is True
                and _all_values(day85_records, "allowed_to_execute", False)
                and _all_values(day85_records, "ssh_allowed", False)
                and _all_values(day85_records, "live_command_allowed", False)
            ),
            ["Day85", "intent_mock_adapter_evidence_binding"],
            "Day85 mock adapter evidence is missing, failed, nondeterministic, or executable.",
        ),
        _check(
            "day86-controlled-runner-execution-blocked",
            "Day86 controlled runner harness keeps execution blocked.",
            (
                day86_report.get("overall_status") == "PASS"
                and day86_report.get("review_status") == "REVIEW_ONLY"
                and day86_report.get("final_recommendation") == "REVIEW_ONLY"
                and day86_locks.get("all_safety_invariants_locked") is True
                and day86_locks.get("report_output_without_execution") is True
                and day86_locks.get("allowed_to_execute_values") == [False]
                and day86_locks.get("ssh_allowed_values") == [False]
                and day86_locks.get("live_command_allowed_values") == [False]
                and day86_locks.get("mapped_task_executed_values") == [False]
            ),
            ["Day86", "intent_controlled_runner_harness"],
            "Day86 runner harness is missing, failed, or no longer blocks execution.",
            "BLOCKED",
        ),
        _check(
            "no-ssh-path-enabled",
            "No SSH path is enabled.",
            (
                day83_report.get("ssh_allowed") is False
                and day84_flags.get("ssh_allowed") is False
                and day85_report.get("safety_invariants", {}).get("ssh_allowed") is False
                and day86_flags.get("ssh_allowed") is False
            ),
            ["Day83-Day86 safety flags"],
            "An SSH path is enabled in the reviewed evidence.",
            "BLOCKED",
        ),
        _check(
            "no-live-command-path-enabled",
            "No live command path is enabled.",
            (
                day83_report.get("live_execution_allowed") is False
                and day84_flags.get("live_command_allowed") is False
                and day85_report.get("safety_invariants", {}).get("live_command_allowed") is False
                and day86_flags.get("live_command_allowed") is False
            ),
            ["Day83-Day86 safety flags"],
            "A live command path is enabled in the reviewed evidence.",
            "BLOCKED",
        ),
        _check(
            "no-write-command-path-enabled",
            "No write command path is enabled.",
            (
                day83_report.get("safety_invariants", {}).get("network_configuration_changed") is False
                and day84_flags.get("network_change_allowed") is False
                and day85_report.get("safety_invariants", {}).get("network_change_allowed") is False
                and day86_flags.get("network_change_allowed") is False
            ),
            ["Day83-Day86 network/write safety flags"],
            "A write or network-change path is enabled in the reviewed evidence.",
            "BLOCKED",
        ),
        _check(
            "no-execution-unlock-exists",
            "No execution unlock exists.",
            (
                day83_report.get("execution_unlock_supported") is False
                and day84_flags.get("execution_unlock_supported") is False
                and day85_report.get("safety_invariants", {}).get("execution_unlock_supported") is False
                and day86_report.get("execution_unlock_supported") is False
            ),
            ["Day83-Day86 unlock flags"],
            "An execution unlock exists in the reviewed evidence.",
            "BLOCKED",
        ),
        _check(
            "dashboard-surface-static-read-only",
            "Dashboard surface remains static/read-only.",
            (
                day83_report.get("safety_invariants", {}).get("html_contains_execution_controls") is False
                and day83_report.get("safety_invariants", {}).get("dashboard_post_route_added") is False
                and day84_report.get("safety_invariants", {}).get("html_contains_execution_controls") is False
                and day84_report.get("safety_invariants", {}).get("dashboard_post_route_added") is False
                and day85_report.get("safety_invariants", {}).get("html_contains_execution_controls") is False
                and day85_report.get("safety_invariants", {}).get("post_endpoint_added") is False
                and day86_flags.get("html_contains_execution_controls") is False
                and day86_flags.get("post_endpoint_added") is False
            ),
            ["Day83-Day86 report/dashboard safety flags"],
            "A dashboard action, POST route, or execution control is enabled.",
            "BLOCKED",
        ),
        _check(
            "runner-task-only-emits-reports",
            "Runner task only emits reports.",
            (
                day86_locks.get("report_output_without_execution") is True
                and day86_flags.get("report_only") is True
                and day86_flags.get("mapped_task_executed") is False
                and day86_flags.get("subprocess_allowed") is False
                and day86_flags.get("config_json_required") is False
            ),
            ["Day86 runner safety lock summary"],
            "Runner evidence implies subprocess, mapped task execution, config loading, or non-report output.",
            "BLOCKED",
        ),
    ]


def _status_from_checks(checks: List[Dict[str, Any]]) -> str:
    if checks and all(check.get("status") == "PASS" for check in checks):
        return "PASS"
    if any(check.get("status") == "FAIL" and check.get("severity_if_failed") == "BLOCKED" for check in checks):
        return "BLOCKED"
    return "REVIEW_REQUIRED"


def validate_readonly_executor_phase_gate_review(report: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for the Day87 review."""
    errors: List[str] = []
    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
        if report.get("safety_invariants", {}).get(field) is not False:
            errors.append(f"safety_invariants {field} must be false.")
    for field in REQUIRED_TRUE_FLAGS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
        if report.get("safety_invariants", {}).get(field) is not True:
            errors.append(f"safety_invariants {field} must be true.")

    checks = report.get("gate_checks", [])
    check_ids = {check.get("check_id") for check in checks}
    for check_id in REQUIRED_GATE_CHECKS:
        if check_id not in check_ids:
            errors.append(f"missing required gate check: {check_id}.")
    if report.get("phase_gate_status") == "PASS" and not all(
        check.get("status") == "PASS" for check in checks
    ):
        errors.append("phase_gate_status cannot be PASS when a required gate check failed.")
    if report.get("phase_gate_status") == "PASS":
        if report.get("phase_gate_recommendation") != PHASE_GATE_RECOMMENDATION:
            errors.append("PASS report must recommend DESIGN_ONLY.")
        if report.get("allowed_next_step") != ALLOWED_NEXT_STEP:
            errors.append("PASS report must allow only the Day88 design draft next step.")

    chain_text = json.dumps(report.get("evidence_chain", []), sort_keys=True)
    for day in ("Day83", "Day84", "Day85", "Day86"):
        if day not in chain_text:
            errors.append(f"evidence_chain must include {day}.")
    return errors


def build_readonly_executor_phase_gate_review(
    day83_report: Optional[Dict[str, Any]] = None,
    day84_report: Optional[Dict[str, Any]] = None,
    day85_report: Optional[Dict[str, Any]] = None,
    day86_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the deterministic Day87 phase gate review report."""
    day83, day84, day85, day86 = _source_reports(day83_report, day84_report, day85_report, day86_report)
    gate_checks = build_phase_gate_checks(day83, day84, day85, day86)
    phase_gate_status = _status_from_checks(gate_checks)
    flags = _review_safety_flags()
    report: Dict[str, Any] = {
        "day": "Day87",
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "phase_name": PHASE_NAME,
        "reviewed_days": ["Day83", "Day84", "Day85", "Day86"],
        "phase_gate_status": phase_gate_status,
        "phase_gate_recommendation": PHASE_GATE_RECOMMENDATION
        if phase_gate_status == "PASS"
        else "DO_NOT_PROCEED",
        "allowed_next_step": ALLOWED_NEXT_STEP if phase_gate_status == "PASS" else None,
        **flags,
        "gate_checks": gate_checks,
        "evidence_chain": [
            {
                "day": "Day83",
                "artifact": "Read-only Executor Readiness Gate",
                "evidence": "Future adapter candidate readiness only; executor_allowed remains false.",
            },
            {
                "day": "Day84",
                "artifact": "Read-only Executor Adapter Interface Contract",
                "evidence": "Contract-only adapter boundary; no adapter implementation or transport.",
            },
            {
                "day": "Day85",
                "artifact": "Mock Adapter + Evidence Binding",
                "evidence": "Deterministic mock/replay/evidence fixtures bind responses to contract and evidence.",
            },
            {
                "day": "Day86",
                "artifact": "Controlled Runner Harness + Safety Regression",
                "evidence": "Runner scenarios emit reports while execution, SSH, and live commands stay blocked.",
            },
        ],
        "safety_invariants": {
            **flags,
            "phase_gate_review_only": True,
            "design_only_next_step": phase_gate_status == "PASS",
            "day88_design_only": True,
            "day87_real_adapter_design_allowed": False,
            "day87_real_adapter_implementation_allowed": False,
            "day88_real_adapter_implementation_allowed": False,
            "deterministic": True,
            "offline_only": True,
            "report_only": True,
            "review_only": True,
            "openai_api_allowed": False,
            "voice_allowed": False,
            "routeros_allowed": False,
            "mapped_task_execution_allowed": False,
            "dashboard_post_route_added": False,
            "html_contains_execution_controls": False,
        },
        "blocked_capabilities": [
            {"capability": "execution", "allowed": False},
            {"capability": "SSH", "allowed": False},
            {"capability": "live command", "allowed": False},
            {"capability": "write command", "allowed": False},
            {"capability": "device connection", "allowed": False},
            {"capability": "OpenAI API", "allowed": False},
            {"capability": "voice", "allowed": False},
            {"capability": "real adapter implementation", "allowed": False},
        ],
        "source_evidence_summary": {
            "day83": {
                "overall_status": day83.get("overall_status"),
                "readiness_state": day83.get("readiness_state"),
                "executor_allowed": day83.get("executor_allowed"),
            },
            "day84": {
                "overall_status": day84.get("overall_status"),
                "contract_state": day84.get("contract_state"),
                "adapter_implementation_present": day84.get("adapter_safety_flags", {}).get(
                    "adapter_implementation_present"
                ),
            },
            "day85": {
                "overall_status": day85.get("overall_status"),
                "final_recommendation": day85.get("final_recommendation"),
                "adapter_record_count": day85.get("traceability_summary", {}).get("adapter_record_count"),
            },
            "day86": {
                "overall_status": day86.get("overall_status"),
                "review_status": day86.get("review_status"),
                "final_recommendation": day86.get("final_recommendation"),
            },
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day87 is a phase gate review only. It permits Day88 to draft the "
            "real read-only executor adapter design, but it does not permit real "
            "adapter implementation, SSH, device connections, live commands, write "
            "commands, OpenAI, voice, or any execution unlock."
        ),
    }
    validation_errors = validate_readonly_executor_phase_gate_review(report)
    report["validation_errors"] = validation_errors
    if validation_errors and report["phase_gate_status"] == "PASS":
        report["phase_gate_status"] = "REVIEW_REQUIRED"
        report["phase_gate_recommendation"] = "DO_NOT_PROCEED"
        report["allowed_next_step"] = None
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _check_rows(checks: List[Dict[str, Any]]) -> str:
    rows = []
    for check in checks:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(check['check_id']))}</td>"
            f"<td>{html.escape(str(check['title']))}</td>"
            f"<td>{html.escape(str(check['status']))}</td>"
            f"<td>{html.escape(', '.join(str(item) for item in check.get('evidence_refs', [])))}</td>"
            "</tr>"
        )
    return "".join(rows)


def _blocked_rows(capabilities: List[Dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item['capability']))}</td>"
        f"<td>{html.escape(json.dumps(item['allowed']))}</td>"
        "</tr>"
        for item in capabilities
    )


def write_readonly_executor_phase_gate_review_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static reviewer-facing Day87 HTML report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
  <p><strong>Result:</strong> {html.escape(report['phase_gate_status'])} / {html.escape(report['phase_gate_recommendation'])}</p>
  <p><strong>Reviewed days:</strong> {html.escape(', '.join(report['reviewed_days']))}</p>
  <p><strong>Next phase:</strong> {html.escape(str(report['allowed_next_step']))}</p>
  <p><strong>Safety:</strong> phase gate review only; this report does not design or implement a real adapter.</p>
  <h2>Gate Decision</h2>
  <table>
    <tbody>
      <tr><th>Execution allowed</th><td>{html.escape(json.dumps(report['execution_allowed']))}</td></tr>
      <tr><th>Real adapter design allowed</th><td>{html.escape(json.dumps(report['real_adapter_design_allowed']))}</td></tr>
      <tr><th>Real adapter implementation allowed</th><td>{html.escape(json.dumps(report['real_adapter_implementation_allowed']))}</td></tr>
      <tr><th>SSH allowed</th><td>{html.escape(json.dumps(report['ssh_allowed']))}</td></tr>
      <tr><th>Live command allowed</th><td>{html.escape(json.dumps(report['live_command_allowed']))}</td></tr>
      <tr><th>Write command allowed</th><td>{html.escape(json.dumps(report['write_command_allowed']))}</td></tr>
      <tr><th>Device connection allowed</th><td>{html.escape(json.dumps(report['device_connection_allowed']))}</td></tr>
    </tbody>
  </table>
  <h2>Gate Checks</h2>
  <table>
    <thead><tr><th>Check ID</th><th>Title</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_check_rows(report['gate_checks'])}</tbody>
  </table>
  <h2>Blocked Capabilities</h2>
  <table>
    <thead><tr><th>Capability</th><th>Allowed</th></tr></thead>
    <tbody>{_blocked_rows(report['blocked_capabilities'])}</tbody>
  </table>
  <h2>Evidence Chain</h2>
  <ul>{_html_list([f"{item['day']}: {item['artifact']} - {item['evidence']}" for item in report['evidence_chain']])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_readonly_executor_phase_gate_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day87 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_readonly_executor_phase_gate_review()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_readonly_executor_phase_gate_review_html(safe_report, html_path)
    return json_path, html_path
