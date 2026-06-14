"""Day132 AI summary dashboard card integration.

This module exposes deterministic dashboard card data for reviewer-facing
visibility over the Day127-Day131 AI summary chain. It is display-only,
review-only, and non-advancing: it does not call providers, APIs, models,
network paths, SSH, brokers, runners, adapters, or any execution path.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from intent_ai_summary_audit_trail_binding import (
    AUDIT_STATUS as DAY131_AUDIT_STATUS,
    TASK_NAME as DAY131_TASK_NAME,
    build_ai_summary_audit_trail_binding_report,
)


DAY = "Day132"
DAY_NUMBER = 132
TASK_NAME = "ai-summary-dashboard-card-integration"
TITLE = "AI Summary Dashboard Card Integration"
FULL_TITLE = f"{DAY} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
CARD_STATUS = "AI_SUMMARY_DASHBOARD_CARD_INTEGRATED_DISPLAY_ONLY"
CARD_ID = "day132-ai-summary-dashboard-card"
REPORT_JSON = Path("reports") / "lab-summary" / "day132_ai_summary_dashboard_card_integration.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day132_ai_summary_dashboard_card_integration.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day132_ai_summary_dashboard_card_integration.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day132_ai_summary_dashboard_card_integration.md"

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "day",
    "task",
    "dashboard_card_id",
    "display_title",
    "display_status",
    "summary_chain_status",
    "redaction_no_secret_status",
    "audit_trail_binding_status",
    "display_only",
    "review_only",
    "non_advancing",
    "provider_api_enabled",
    "ai_execution_enabled",
    "ai_decision_enabled",
    "reviewer_approval_enabled",
    "next_phase_allowed",
    "mock_provider_enabled",
    "live_execution_enabled",
    "ssh_invocation_enabled",
    "device_invocation_enabled",
    "broker_invocation_enabled",
    "runner_invocation_enabled",
    "adapter_invocation_enabled",
    "agents_md_status",
)


def build_agents_md_status(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day132_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": "AGENTS.md not found.",
        }
    except OSError as exc:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day132_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": str(exc),
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_status": "FOUND_AND_READ" if required_phrase_present else "MISSING_STOPPED",
        "agents_md_path": "AGENTS.md",
        "agents_md_read_before_day132_work": required_phrase_present,
        "agents_md_required_phrase_present": required_phrase_present,
        "agents_md_read_error": "",
    }


def build_non_execution_safety_flags() -> Dict[str, bool]:
    return {
        "provider_api_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "openai_api_called": False,
        "ai_execution_enabled": False,
        "ai_decision_enabled": False,
        "execution_path_opened": False,
        "mapped_execution_enabled": False,
        "reviewer_approval_enabled": False,
        "next_phase_allowed": False,
        "mock_provider_enabled": False,
        "live_execution_enabled": False,
        "ssh_invocation_enabled": False,
        "device_invocation_enabled": False,
        "broker_invocation_enabled": False,
        "runner_invocation_enabled": False,
        "adapter_invocation_enabled": False,
        "network_access_enabled": False,
        "secrets_handling_enabled": False,
    }


def build_input_artifact_references(day131_report: Mapping[str, Any]) -> List[Dict[str, Any]]:
    references = []
    for item in day131_report.get("input_artifacts", []):
        references.append(
            {
                "day": item.get("day", ""),
                "task": item.get("task", ""),
                "status": item.get("status", ""),
                "reference_only": True,
            }
        )
    references.append(
        {
            "day": "Day131",
            "task": DAY131_TASK_NAME,
            "status": day131_report.get("audit_status", DAY131_AUDIT_STATUS),
            "reference_only": True,
        }
    )
    return references


def build_dashboard_card(day131_report: Mapping[str, Any]) -> Dict[str, Any]:
    safety_flags = build_non_execution_safety_flags()
    input_artifacts = build_input_artifact_references(day131_report)
    return {
        "dashboard_card_id": CARD_ID,
        "display_title": FULL_TITLE,
        "display_status": CARD_STATUS,
        "input_artifact_references": input_artifacts,
        "summary_chain_status": "DAY127_DAY131_REFERENCES_VISIBLE",
        "redaction_no_secret_status": day131_report.get("redaction_report_status", ""),
        "audit_trail_binding_status": day131_report.get("audit_status", ""),
        "reviewer_visible_warning": (
            "Display-only dashboard card. Not Day133 or Day134. No provider/API, "
            "AI execution, AI decision, reviewer approval, live execution, SSH, "
            "broker, runner, adapter, or next-phase unlock is enabled."
        ),
        "boundary_text": [
            "This is not Day133 Disabled AI Provider Interface Boundary.",
            "This is not Day134 Offline AI Provider Adapter Contract.",
            "This is not provider/API integration.",
            "This is not AI execution.",
            "This is not AI decision-making.",
            "This is not reviewer approval.",
            "This is not a next-phase unlock.",
        ],
        "display_only": True,
        "review_only": True,
        "non_advancing": True,
        "deterministic_only": True,
        "report_only": True,
        "local_only": True,
        "not_day133_disabled_ai_provider_interface_boundary": True,
        "not_day134_offline_ai_provider_adapter_contract": True,
        "not_provider_api_integration": True,
        "not_ai_execution": True,
        "not_ai_decision_making": True,
        "not_reviewer_approval": True,
        "not_next_phase_unlock": True,
        "non_execution_safety_flags": safety_flags,
        "no_execution_evidence": {
            "provider_api_path_opened": False,
            "ai_execution_path_opened": False,
            "ai_decision_path_opened": False,
            "reviewer_approval_path_opened": False,
            "next_phase_unlock_opened": False,
            "mock_provider_path_opened": False,
            "live_execution_path_opened": False,
            "ssh_device_path_opened": False,
            "broker_runner_adapter_path_opened": False,
        },
    }


def build_ai_summary_dashboard_card_integration_report(project_root: Path) -> Dict[str, Any]:
    agents_status = build_agents_md_status(project_root)
    day131_report = build_ai_summary_audit_trail_binding_report(project_root)
    card = build_dashboard_card(day131_report)
    safety_flags = card["non_execution_safety_flags"]

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "dashboard_card_id": card["dashboard_card_id"],
        "display_title": card["display_title"],
        "display_status": card["display_status"],
        "summary_chain_status": card["summary_chain_status"],
        "redaction_no_secret_status": card["redaction_no_secret_status"],
        "audit_trail_binding_status": card["audit_trail_binding_status"],
        "display_only": card["display_only"],
        "review_only": card["review_only"],
        "non_advancing": card["non_advancing"],
        "deterministic_only": card["deterministic_only"],
        "report_only": card["report_only"],
        "local_only": card["local_only"],
        "not_day133_disabled_ai_provider_interface_boundary": card[
            "not_day133_disabled_ai_provider_interface_boundary"
        ],
        "not_day134_offline_ai_provider_adapter_contract": card[
            "not_day134_offline_ai_provider_adapter_contract"
        ],
        "not_provider_api_integration": card["not_provider_api_integration"],
        "not_ai_execution": card["not_ai_execution"],
        "not_ai_decision_making": card["not_ai_decision_making"],
        "not_reviewer_approval": card["not_reviewer_approval"],
        "not_next_phase_unlock": card["not_next_phase_unlock"],
        "provider_api_enabled": safety_flags["provider_api_enabled"],
        "ai_execution_enabled": safety_flags["ai_execution_enabled"],
        "ai_decision_enabled": safety_flags["ai_decision_enabled"],
        "reviewer_approval_enabled": safety_flags["reviewer_approval_enabled"],
        "next_phase_allowed": safety_flags["next_phase_allowed"],
        "mock_provider_enabled": safety_flags["mock_provider_enabled"],
        "live_execution_enabled": safety_flags["live_execution_enabled"],
        "ssh_invocation_enabled": safety_flags["ssh_invocation_enabled"],
        "device_invocation_enabled": safety_flags["device_invocation_enabled"],
        "broker_invocation_enabled": safety_flags["broker_invocation_enabled"],
        "runner_invocation_enabled": safety_flags["runner_invocation_enabled"],
        "adapter_invocation_enabled": safety_flags["adapter_invocation_enabled"],
        "openai_api_called": safety_flags["openai_api_called"],
        "network_access_enabled": safety_flags["network_access_enabled"],
        "input_artifact_references": card["input_artifact_references"],
        "redaction_no_secret_reference": day131_report.get("redaction_no_secret_policy_reference", {}),
        "audit_trail_binding_reference": {
            "day": "Day131",
            "task": DAY131_TASK_NAME,
            "audit_status": day131_report.get("audit_status", ""),
            "report_status": day131_report.get("overall_status", ""),
        },
        "dashboard_card": card,
        "agents_md_status": agents_status["agents_md_status"],
        "agents_md_read_before_day132_work": agents_status["agents_md_read_before_day132_work"],
        "agents_md_path": agents_status["agents_md_path"],
        "agents_md_evidence": agents_status,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    if report["overall_status"] != OVERALL_STATUS:
        report["display_status"] = "AI_SUMMARY_DASHBOARD_CARD_INTEGRATION_BLOCKED"
        report["dashboard_card"]["display_status"] = report["display_status"]
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("agents_md_status") != "FOUND_AND_READ":
        errors.append("AGENTS.md status must be FOUND_AND_READ.")
    if report.get("agents_md_read_before_day132_work") is not True:
        errors.append("AGENTS.md must be read before Day132 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    for field in (
        "display_only",
        "review_only",
        "non_advancing",
        "deterministic_only",
        "report_only",
        "local_only",
        "not_day133_disabled_ai_provider_interface_boundary",
        "not_day134_offline_ai_provider_adapter_contract",
        "not_provider_api_integration",
        "not_ai_execution",
        "not_ai_decision_making",
        "not_reviewer_approval",
        "not_next_phase_unlock",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in (
        "provider_api_enabled",
        "ai_execution_enabled",
        "ai_decision_enabled",
        "reviewer_approval_enabled",
        "next_phase_allowed",
        "mock_provider_enabled",
        "live_execution_enabled",
        "ssh_invocation_enabled",
        "device_invocation_enabled",
        "broker_invocation_enabled",
        "runner_invocation_enabled",
        "adapter_invocation_enabled",
        "openai_api_called",
        "network_access_enabled",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if report.get("display_status") != CARD_STATUS:
        errors.append(f"display_status must be {CARD_STATUS}.")
    input_days = {item.get("day") for item in report.get("input_artifact_references", [])}
    for day in ("Day127", "Day128", "Day129", "Day130", "Day131"):
        if day not in input_days:
            errors.append(f"{day} input reference is required.")
    if not report.get("redaction_no_secret_reference"):
        errors.append("redaction_no_secret_reference is required.")
    if not report.get("audit_trail_binding_reference"):
        errors.append("audit_trail_binding_reference is required.")

    card = report.get("dashboard_card", {})
    flags = card.get("non_execution_safety_flags", {})
    for flag_name, flag_value in flags.items():
        if flag_value is not False:
            errors.append(f"dashboard card safety flag {flag_name} must be false.")
    evidence = card.get("no_execution_evidence", {})
    for evidence_name, evidence_value in evidence.items():
        if evidence_value is not False:
            errors.append(f"dashboard card evidence {evidence_name} must be false.")
    return errors


def write_ai_summary_dashboard_card_integration_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_summary_dashboard_card_integration_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_summary_dashboard_card_integration_html(safe_report, html_path)
    return json_path, html_path


def write_ai_summary_dashboard_card_integration_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    input_rows = _table_rows(
        (
            item.get("day", ""),
            item.get("task", ""),
            item.get("status", ""),
            item.get("reference_only", ""),
        )
        for item in report.get("input_artifact_references", [])
    )
    flag_rows = _table_rows(
        (key, value)
        for key, value in report.get("dashboard_card", {})
        .get("non_execution_safety_flags", {})
        .items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report['full_title']))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report['full_title']))}</h1>
  <p><strong>AGENTS.md status:</strong> {html.escape(str(report['agents_md_status']))}</p>
  <h2>Dashboard Card Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Input Artifact References</h2>
  <table><thead><tr><th>Day</th><th>Task</th><th>Status</th><th>Reference Only</th></tr></thead><tbody>{input_rows}</tbody></table>
  <h2>Non-Execution Safety Flags</h2>
  <table><thead><tr><th>Flag</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_summary_dashboard_card_integration(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_summary_dashboard_card_integration_report(project_root)
    json_path, html_path = write_ai_summary_dashboard_card_integration_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print("Safety: display-only dashboard card; no provider/API, AI execution, AI decision, reviewer approval, mock provider, live execution, SSH/device/broker/runner/adapter invocation, or next-phase unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(
        "not_day133_disabled_ai_provider_interface_boundary: "
        f"{json.dumps(report['not_day133_disabled_ai_provider_interface_boundary'])}"
    )
    print(
        "not_day134_offline_ai_provider_adapter_contract: "
        f"{json.dumps(report['not_day134_offline_ai_provider_adapter_contract'])}"
    )
    print(f"not_provider_api_integration: {json.dumps(report['not_provider_api_integration'])}")
    print(f"not_ai_execution: {json.dumps(report['not_ai_execution'])}")
    print(f"not_ai_decision_making: {json.dumps(report['not_ai_decision_making'])}")
    print(f"not_reviewer_approval: {json.dumps(report['not_reviewer_approval'])}")
    print(f"not_next_phase_unlock: {json.dumps(report['not_next_phase_unlock'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {CARD_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {report['display_status']}")
    return 1


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return "; ".join(str(item) for item in value) or "none"
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )


def main() -> int:
    report = build_ai_summary_dashboard_card_integration_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
