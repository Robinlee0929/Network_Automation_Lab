"""Day86 controlled runner harness and safety regression report.

This module raises the Day85 adapter evidence into runner-level regression
checks. It is deterministic and report-only: compatible adapters may produce
reviewer evidence, but the runner never grants SSH, live command execution, or
mapped task execution.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_mock_adapter_evidence_binding import (
    ADAPTER_FIXTURE_ID,
    BLOCKED_ADAPTER_TYPES,
    COMPATIBLE_ADAPTER_TYPES,
    build_adapter_records,
    build_compatibility_matrix,
)


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "controlled-runner-harness"
TITLE = "Day86 Controlled Runner Harness + Safety Regression"
RUNNER_MODE = "CONTROLLED_HARNESS"
REPORT_JSON = Path("reports") / "lab-summary" / "day86_controlled_runner_harness.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day86_controlled_runner_harness.html"

LOCKED_FALSE_FIELDS = (
    "allowed_to_execute",
    "ssh_allowed",
    "live_command_allowed",
    "mapped_task_executed",
)
REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "requested_adapter",
    "compatibility_status",
    "blocked_adapter",
    "evidence_bound",
    "report_output_expected",
    "dry_run_only",
    "allowed_to_execute",
    "ssh_allowed",
    "live_command_allowed",
    "mapped_task_executed",
    "runner_decision",
    "safety_regression_status",
    "evidence_refs",
)


def runner_safety_flags() -> Dict[str, bool]:
    """Return the locked Day86 runner-level safety invariants."""
    return {
        "dry_run_only": True,
        "allowed_to_execute": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "mapped_task_executed": False,
        "execution_unlock_supported": False,
        "approval_unlock_supported": False,
        "device_access_allowed": False,
        "device_connection_allowed": False,
        "live_execution_allowed": False,
        "mapped_task_execution_allowed": False,
        "dashboard_action_allowed": False,
        "post_endpoint_added": False,
        "html_contains_execution_controls": False,
        "ai_api_allowed": False,
        "subprocess_allowed": False,
        "config_json_required": False,
        "network_change_allowed": False,
        "report_only": True,
        "review_only": True,
        "mock_only": True,
        "deterministic": True,
    }


def _adapter_records_by_type() -> Dict[str, Dict[str, Any]]:
    return {record["adapter_type"]: record for record in build_adapter_records()}


def _matrix_by_adapter_type() -> Dict[str, Dict[str, Any]]:
    return {row["adapter_type"]: row for row in build_compatibility_matrix()}


def _scenario_evidence_refs(
    scenario_id: str,
    adapter_record: Optional[Dict[str, Any]],
    evidence_bound: bool,
) -> List[str]:
    refs = [
        "Day85 Mock Adapter + Evidence Binding",
        "docs/ai/intent_mock_adapter_evidence_binding.md",
        "docs/roadmap/day85_mock_adapter_evidence_binding.md",
        "docs/ai/intent_controlled_runner_harness.md",
        "docs/roadmap/day86_controlled_runner_harness_safety_regression.md",
        f"Day86 runner scenario: {scenario_id}",
    ]
    if adapter_record and evidence_bound:
        refs.append(str(adapter_record["evidence_reference"]))
        refs.append(str(adapter_record["mock_response"]["response_id"]))
    if adapter_record and not evidence_bound:
        refs.append("Day86 intentionally incomplete evidence binding regression fixture")
    return refs


def _runner_decision(
    compatible: bool,
    blocked_adapter: bool,
    evidence_bound: bool,
    unsafe_flag_requested: bool,
) -> str:
    if blocked_adapter:
        return "BLOCKED_ADAPTER_REVIEW_ONLY"
    if unsafe_flag_requested:
        return "UNSAFE_FLAG_REGRESSION_BLOCKED"
    if not compatible:
        return "COMPATIBILITY_MISMATCH_REVIEW_ONLY"
    if not evidence_bound:
        return "MISSING_EVIDENCE_REVIEW_ONLY"
    return "REPORT_REVIEW_ONLY"


def build_runner_harness_scenario(
    scenario_id: str,
    requested_adapter: str,
    report_output_expected: bool,
    evidence_bound: bool = True,
    force_compatibility_status: Optional[str] = None,
    requested_execution_flags: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    """Build one deterministic runner-level safety regression scenario."""
    records = _adapter_records_by_type()
    matrix = _matrix_by_adapter_type()
    adapter_record = records.get(requested_adapter)
    matrix_row = matrix.get(requested_adapter, {})
    adapter_is_compatible = requested_adapter in COMPATIBLE_ADAPTER_TYPES
    blocked_adapter = requested_adapter in BLOCKED_ADAPTER_TYPES
    compatibility_status = force_compatibility_status or str(
        matrix_row.get("expected_result", "mismatch")
    )
    requested_flags = dict(requested_execution_flags or {})
    unsafe_flag_requested = any(
        requested_flags.get(field) is True
        for field in (
            "allowed_to_execute",
            "ssh_allowed",
            "live_command_allowed",
            "mapped_task_execution_allowed",
        )
    )
    flags = runner_safety_flags()
    decision = _runner_decision(
        compatible=adapter_is_compatible and compatibility_status == "compatible",
        blocked_adapter=blocked_adapter,
        evidence_bound=evidence_bound,
        unsafe_flag_requested=unsafe_flag_requested,
    )

    return {
        "scenario_id": scenario_id,
        "requested_adapter": requested_adapter,
        "compatibility_status": compatibility_status,
        "blocked_adapter": blocked_adapter,
        "evidence_bound": evidence_bound,
        "report_output_expected": report_output_expected,
        "dry_run_only": flags["dry_run_only"],
        "allowed_to_execute": flags["allowed_to_execute"],
        "ssh_allowed": flags["ssh_allowed"],
        "live_command_allowed": flags["live_command_allowed"],
        "mapped_task_executed": flags["mapped_task_executed"],
        "runner_decision": decision,
        "safety_regression_status": "PASS",
        "requested_execution_flags": requested_flags,
        "adapter_fixture_id": ADAPTER_FIXTURE_ID,
        "source_adapter_record_id": adapter_record.get("adapter_id") if adapter_record else None,
        "source_adapter_decision": adapter_record.get("decision") if adapter_record else None,
        "evidence_refs": _scenario_evidence_refs(scenario_id, adapter_record, evidence_bound),
    }


def build_runner_harness_scenarios() -> List[Dict[str, Any]]:
    """Build the Day86 controlled runner safety regression scenarios."""
    return [
        build_runner_harness_scenario(
            "day86-compatible-mock-evidence-bound",
            "mock adapter",
            report_output_expected=True,
        ),
        build_runner_harness_scenario(
            "day86-compatible-report-output-requested",
            "replay adapter",
            report_output_expected=True,
        ),
        build_runner_harness_scenario(
            "day86-blocked-adapter-attempt",
            "ssh adapter",
            report_output_expected=True,
        ),
        build_runner_harness_scenario(
            "day86-adapter-compatibility-mismatch",
            "mock adapter",
            report_output_expected=True,
            force_compatibility_status="mismatch",
        ),
        build_runner_harness_scenario(
            "day86-incomplete-evidence-binding",
            "evidence-only adapter",
            report_output_expected=True,
            evidence_bound=False,
        ),
        build_runner_harness_scenario(
            "day86-unsafe-execution-flag-regression-attempt",
            "mock adapter",
            report_output_expected=True,
            requested_execution_flags={
                "allowed_to_execute": True,
                "ssh_allowed": True,
                "live_command_allowed": True,
                "mapped_task_execution_allowed": True,
            },
        ),
    ]


def validate_runner_harness_scenario(scenario: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for one Day86 scenario."""
    errors: List[str] = []
    scenario_id = str(scenario.get("scenario_id", "<unknown>"))
    for field in REQUIRED_SCENARIO_FIELDS:
        if field not in scenario:
            errors.append(f"{scenario_id} missing required field: {field}.")

    if scenario.get("dry_run_only") is not True:
        errors.append(f"{scenario_id} dry_run_only must be true.")
    for field in LOCKED_FALSE_FIELDS:
        if scenario.get(field) is not False:
            errors.append(f"{scenario_id} {field} must be false.")
    if not scenario.get("evidence_refs"):
        errors.append(f"{scenario_id} must include evidence references.")
    if scenario.get("blocked_adapter") is True and scenario.get("runner_decision") == "REPORT_REVIEW_ONLY":
        errors.append(f"{scenario_id} blocked adapter cannot pass runner report decision.")
    if scenario.get("evidence_bound") is False and scenario.get("allowed_to_execute") is not False:
        errors.append(f"{scenario_id} missing evidence cannot become executable.")
    if scenario.get("compatibility_status") == "compatible" and scenario.get("allowed_to_execute") is not False:
        errors.append(f"{scenario_id} compatible adapter cannot become executable.")
    return errors


def validate_runner_harness_scenarios(scenarios: List[Dict[str, Any]]) -> List[str]:
    """Return validation errors for all Day86 runner harness scenarios."""
    errors: List[str] = []
    if len(scenarios) < 6:
        errors.append("Day86 must include at least six runner harness scenarios.")
    for scenario in scenarios:
        errors.extend(validate_runner_harness_scenario(scenario))
    return errors


def build_controlled_runner_harness_report() -> Dict[str, Any]:
    """Build the Day86 controlled runner harness safety regression report."""
    scenarios = build_runner_harness_scenarios()
    validation_errors = validate_runner_harness_scenarios(scenarios)
    failed_scenarios = [
        scenario
        for scenario in scenarios
        if scenario["safety_regression_status"] != "PASS"
        or validate_runner_harness_scenario(scenario)
    ]
    flags = runner_safety_flags()
    safety_lock_summary = {
        "dry_run_only_values": sorted({scenario["dry_run_only"] for scenario in scenarios}),
        "allowed_to_execute_values": sorted({scenario["allowed_to_execute"] for scenario in scenarios}),
        "ssh_allowed_values": sorted({scenario["ssh_allowed"] for scenario in scenarios}),
        "live_command_allowed_values": sorted({scenario["live_command_allowed"] for scenario in scenarios}),
        "mapped_task_executed_values": sorted({scenario["mapped_task_executed"] for scenario in scenarios}),
        "all_safety_invariants_locked": not validation_errors and all(
            scenario["dry_run_only"] is True
            and scenario["allowed_to_execute"] is False
            and scenario["ssh_allowed"] is False
            and scenario["live_command_allowed"] is False
            and scenario["mapped_task_executed"] is False
            for scenario in scenarios
        ),
        "compatible_scenarios_executed": any(
            scenario["compatibility_status"] == "compatible"
            and scenario["mapped_task_executed"] is True
            for scenario in scenarios
        ),
        "blocked_adapter_execution_passed": any(
            scenario["blocked_adapter"] is True
            and scenario["runner_decision"] == "REPORT_REVIEW_ONLY"
            for scenario in scenarios
        ),
        "report_output_without_execution": all(
            scenario["mapped_task_executed"] is False
            for scenario in scenarios
            if scenario["report_output_expected"] is True
        ),
    }
    overall_status = "PASS" if not validation_errors and not failed_scenarios else "FAIL"
    return {
        "day": "Day86",
        "phase": "Day86",
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "overall_status": overall_status,
        "review_status": "REVIEW_ONLY",
        "runner_mode": RUNNER_MODE,
        "final_recommendation": "REVIEW_ONLY",
        "execution_unlock_supported": flags["execution_unlock_supported"],
        "scope": [
            "runner-level safety regression",
            "Day85 adapter compatibility evidence consumed as input",
            "reviewer-facing JSON and HTML reports",
            "dry-run-only and review-only execution boundary",
        ],
        "non_goals": [
            "new adapter functionality",
            "SSH",
            "device access",
            "live command execution",
            "mapped task execution",
            "AI API or OpenAI SDK usage",
            "dashboard POST route, form, button, or execution control",
            "approval or execution unlock",
        ],
        "day85_inputs": {
            "adapter_record_count": len(build_adapter_records()),
            "compatible_adapter_types": sorted(COMPATIBLE_ADAPTER_TYPES),
            "blocked_adapter_types": sorted(BLOCKED_ADAPTER_TYPES),
            "compatibility_matrix_scope": "internal Day85/Day86 validation evidence only",
        },
        "scenarios": scenarios,
        "safety_invariants": flags,
        "summary": {
            "total_scenarios": len(scenarios),
            "failed_scenarios": len(failed_scenarios),
            "runner_mode": RUNNER_MODE,
            "final_recommendation": "REVIEW_ONLY",
            "safety_lock_summary": safety_lock_summary,
            "validation_errors": validation_errors,
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "validation_errors": validation_errors,
        "final_safety_statement": (
            "Day86 is a runner-level safety regression. Adapter compatibility, "
            "evidence binding, and report generation never imply live execution, "
            "SSH permission, command permission, or mapped task execution."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _scenario_rows(scenarios: List[Dict[str, Any]]) -> str:
    rows = []
    for scenario in scenarios:
        rows.append(
            "<tr>"
            f"<td>{html.escape(scenario['scenario_id'])}</td>"
            f"<td>{html.escape(scenario['requested_adapter'])}</td>"
            f"<td>{html.escape(scenario['compatibility_status'])}</td>"
            f"<td>{html.escape(str(scenario['allowed_to_execute']))}</td>"
            f"<td>{html.escape(str(scenario['ssh_allowed']))}</td>"
            f"<td>{html.escape(str(scenario['live_command_allowed']))}</td>"
            f"<td>{html.escape(str(scenario['mapped_task_executed']))}</td>"
            f"<td>{html.escape(scenario['runner_decision'])}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_controlled_runner_harness_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static reviewer-facing Day86 HTML report."""
    summary = report["summary"]
    locks = summary["safety_lock_summary"]
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
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['review_status'])}</p>
  <p><strong>Runner mode:</strong> {html.escape(report['runner_mode'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Safety:</strong> runner-level regression, dry-run-only, review-only, report-only, and non-executing.</p>
  <h2>Safety Lock Summary</h2>
  <table>
    <tbody>
      <tr><th>Total scenarios</th><td>{summary['total_scenarios']}</td></tr>
      <tr><th>Failed scenarios</th><td>{summary['failed_scenarios']}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(locks['allowed_to_execute_values']))}</td></tr>
      <tr><th>SSH allowed values</th><td>{html.escape(str(locks['ssh_allowed_values']))}</td></tr>
      <tr><th>Live command allowed values</th><td>{html.escape(str(locks['live_command_allowed_values']))}</td></tr>
      <tr><th>Mapped task executed values</th><td>{html.escape(str(locks['mapped_task_executed_values']))}</td></tr>
      <tr><th>All safety invariants locked</th><td>{html.escape(str(locks['all_safety_invariants_locked']))}</td></tr>
    </tbody>
  </table>
  <h2>Runner Harness Scenarios</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Adapter</th><th>Compatibility</th><th>Allowed to execute</th><th>SSH allowed</th><th>Live command allowed</th><th>Mapped task executed</th><th>Runner decision</th></tr></thead>
    <tbody>{_scenario_rows(report['scenarios'])}</tbody>
  </table>
  <h2>Non Goals</h2>
  <ul>{_html_list(report['non_goals'])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_controlled_runner_harness_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day86 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_controlled_runner_harness_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_controlled_runner_harness_html(safe_report, html_path)
    return json_path, html_path
