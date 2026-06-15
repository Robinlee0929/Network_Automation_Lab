"""Day142 AI summary to dry-run draft display contract.

This module maps an already-produced AI reviewer summary into deterministic
display-only dry-run draft data. It does not call providers, APIs, models,
adapters, brokers, runners, SSH, NETCONF, RESTCONF, or live device paths.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 142
DAY_LABEL = "Day142"
TASK_NAME = "ai-summary-to-dry-run-draft-display-contract"
TITLE = "AI Summary to Dry-run Draft Display Contract"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_DISPLAY_CONTRACT"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_READY"
BLOCKED_STATUS = "AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_BLOCKED"
FINAL_RECOMMENDATION = "REVIEW_ONLY_DISPLAY_CONTRACT_KEEP_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day142_ai_summary_to_dry_run_draft_display_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day142_ai_summary_to_dry_run_draft_display_contract.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day142_ai_summary_to_dry_run_draft_display_contract.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day142_ai_summary_to_dry_run_draft_display_contract.md"
SOURCE_SUMMARY_FIXTURE = Path("fixtures") / "day127_ai_reviewer_summary.example.json"

ALREADY_PRODUCED_SUMMARY_STATEMENT = (
    "Day142 treats AI summary input as already-produced reviewer text/metadata."
)
DISPLAY_ONLY_STATEMENT = "Day142 dry-run draft output is display-only and review-only."
NO_PROVIDER_API_MODEL_STATEMENT = "Day142 enables no provider, API, or model invocation."
NO_EXECUTION_DEVICE_STATEMENT = (
    "Day142 opens no command execution, SSH, NETCONF, RESTCONF, live-device, or config write/apply path."
)
NEXT_PHASE_FALSE_STATEMENT = "Day142 keeps next_phase_allowed=false."
NOT_DAY141_REDO_STATEMENT = "Day142 does not redo, extend, rename, or re-validate Day141."

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "display_only",
    "dry_run_draft_display_only",
    "already_produced_summary_input",
    "deterministic_payload",
    "human_review_required",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "provider_enabled",
    "api_enabled",
    "model_invocation_enabled",
    "execution_enabled",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "live_device_allowed",
    "config_write_allowed",
    "command_apply_allowed",
    "adapter_invoked",
    "next_phase_allowed",
)

FORBIDDEN_DISPLAY_PAYLOAD_KEYS: Tuple[str, ...] = (
    "executable_commands",
    "commands",
    "command",
    "device_connection_parameters",
    "connection_parameters",
    "host",
    "hostname",
    "ip_address",
    "username",
    "password",
    "secret",
    "token",
    "api_key",
    "provider_credentials",
    "api_request_payload",
    "request_payload",
    "apply_actions",
    "commit_actions",
    "deploy_actions",
)

REQUIRED_DISPLAY_PAYLOAD_FIELDS: Tuple[str, ...] = (
    "source_summary_id",
    "source_summary_status",
    "draft_display_title",
    "draft_display_sections",
    "safety_banner",
    "review_required",
    "blocked_actions",
    "non_execution_guards",
    "next_phase_allowed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "overall_status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day142_work",
    "source_summary_input_mode",
    "display_payload_contract_status",
    "display_payload",
    "final_recommendation",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day142_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day142_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def load_source_summary(project_root: Path) -> Dict[str, Any]:
    fixture_path = Path(project_root) / SOURCE_SUMMARY_FIXTURE
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def build_example_source_summary() -> Dict[str, Any]:
    return {
        "summary_id": "day142-example-already-produced-summary",
        "status_rollup": {"overall_status": "REVIEW_ONLY"},
        "reviewer_findings": [
            {
                "finding_id": "DAY142-DISPLAY-001",
                "severity": "INFO",
                "status": "REVIEW_ONLY",
                "title": "Already-produced reviewer summary is ready for display draft mapping.",
                "requires_human_review": True,
            }
        ],
        "evidence_refs": [
            {
                "ref_id": "day142-display-contract",
                "kind": "display_contract",
                "path": AI_INTENT_DOC.as_posix(),
                "description": "Day142 display-only contract evidence.",
            }
        ],
    }


def build_dry_run_draft_display_payload(summary: Mapping[str, Any]) -> Dict[str, Any]:
    summary_id = str(summary.get("summary_id", "unknown-summary"))
    status_rollup = summary.get("status_rollup", {})
    source_summary_status = (
        str(status_rollup.get("overall_status", "UNKNOWN"))
        if isinstance(status_rollup, Mapping)
        else "UNKNOWN"
    )
    findings = summary.get("reviewer_findings", [])
    evidence_refs = summary.get("evidence_refs", [])

    finding_count = len(findings) if isinstance(findings, list) else 0
    evidence_count = len(evidence_refs) if isinstance(evidence_refs, list) else 0
    first_finding_title = ""
    if isinstance(findings, list) and findings and isinstance(findings[0], Mapping):
        first_finding_title = str(findings[0].get("title", "Reviewer summary available."))

    return {
        "source_summary_id": summary_id,
        "source_summary_status": source_summary_status,
        "draft_display_title": f"Dry-run Draft Review: {summary_id}",
        "draft_display_sections": [
            {
                "section_id": "summary_status",
                "heading": "Source Summary",
                "body": f"Already-produced reviewer summary status: {source_summary_status}.",
                "display_only": True,
            },
            {
                "section_id": "review_findings",
                "heading": "Reviewer Findings",
                "body": first_finding_title or "No reviewer finding title supplied.",
                "finding_count": finding_count,
                "display_only": True,
            },
            {
                "section_id": "evidence_refs",
                "heading": "Evidence References",
                "body": f"{evidence_count} evidence reference(s) are available for reviewer display.",
                "evidence_ref_count": evidence_count,
                "display_only": True,
            },
            {
                "section_id": "safety_guards",
                "heading": "Safety Guards",
                "body": "Display contract only; all execution, provider, API, model, live-device, and apply paths remain closed.",
                "display_only": True,
            },
        ],
        "safety_banner": (
            "REVIEW_ONLY_DISPLAY: dry-run draft display only; no provider/API/model invocation, "
            "no command execution, no live-device access, no config write/apply."
        ),
        "review_required": True,
        "blocked_actions": [
            "provider_enable",
            "api_enable",
            "model_invocation",
            "command_execution",
            "ssh_access",
            "netconf_access",
            "restconf_access",
            "live_device_access",
            "config_write",
            "apply_commit_deploy",
        ],
        "non_execution_guards": {field: False for field in REQUIRED_FALSE_FIELDS},
        "next_phase_allowed": False,
    }


def build_day142_ai_summary_to_dry_run_draft_display_contract(
    project_root: Path,
    source_summary: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    summary = dict(source_summary or load_source_summary(project_root))
    display_payload = build_dry_run_draft_display_payload(summary)
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "overall_status": "PENDING",
        "status": "PENDING",
        **build_agents_md_evidence(project_root),
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        "source_summary_input_mode": "already_produced_reviewer_text_metadata",
        "source_summary_fixture": SOURCE_SUMMARY_FIXTURE.as_posix(),
        "source_summary_id": display_payload["source_summary_id"],
        "source_summary_status": display_payload["source_summary_status"],
        "display_payload_contract_status": "PENDING",
        "display_payload": display_payload,
        "forbidden_display_payload_keys": list(FORBIDDEN_DISPLAY_PAYLOAD_KEYS),
        "explicit_boundary_statements": [
            ALREADY_PRODUCED_SUMMARY_STATEMENT,
            DISPLAY_ONLY_STATEMENT,
            NO_PROVIDER_API_MODEL_STATEMENT,
            NO_EXECUTION_DEVICE_STATEMENT,
            NEXT_PHASE_FALSE_STATEMENT,
            NOT_DAY141_REDO_STATEMENT,
        ],
        "day141_validation_fix_redone": False,
        "day141_files_modified": False,
        "day143_safety_diff_viewer_implemented": False,
        "day144_v04_compatibility_review_implemented": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    report["display_payload_contract_status"] = (
        "DISPLAY_PAYLOAD_CONTRACT_READY"
        if report["overall_status"] == OVERALL_STATUS
        else "DISPLAY_PAYLOAD_CONTRACT_BLOCKED"
    )
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    expected_values = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "source_summary_input_mode": "already_produced_reviewer_text_metadata",
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day142_work") is not True:
        errors.append("agents_md_read_before_day142_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    display_payload = report.get("display_payload", {})
    _validate_display_payload(display_payload, errors)
    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)

    if report.get("day141_validation_fix_redone") is not False:
        errors.append("day141_validation_fix_redone must be false.")
    if report.get("day141_files_modified") is not False:
        errors.append("day141_files_modified must be false.")
    if report.get("day143_safety_diff_viewer_implemented") is not False:
        errors.append("day143_safety_diff_viewer_implemented must be false.")
    if report.get("day144_v04_compatibility_review_implemented") is not False:
        errors.append("day144_v04_compatibility_review_implemented must be false.")
    return errors


def _validate_display_payload(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("display_payload must be an object.")
        return

    for field in REQUIRED_DISPLAY_PAYLOAD_FIELDS:
        if field not in payload:
            errors.append(f"display_payload.{field} is missing.")

    if payload.get("review_required") is not True:
        errors.append("display_payload.review_required must be true.")
    if payload.get("next_phase_allowed") is not False:
        errors.append("display_payload.next_phase_allowed must be false.")

    sections = payload.get("draft_display_sections")
    if not isinstance(sections, list) or not sections:
        errors.append("display_payload.draft_display_sections must be a non-empty list.")
    else:
        for section in sections:
            if not isinstance(section, Mapping):
                errors.append("Each draft display section must be an object.")
                continue
            if section.get("display_only") is not True:
                errors.append(f"{section.get('section_id', '<unknown>')} display_only must be true.")

    guards = payload.get("non_execution_guards")
    if not isinstance(guards, Mapping):
        errors.append("display_payload.non_execution_guards must be an object.")
    else:
        for field in REQUIRED_FALSE_FIELDS:
            if guards.get(field) is not False:
                errors.append(f"display_payload.non_execution_guards.{field} must be false.")

    forbidden_keys = _find_forbidden_display_payload_keys(payload)
    if forbidden_keys:
        errors.append("display_payload contains forbidden keys: " + ", ".join(forbidden_keys))


def _find_forbidden_display_payload_keys(value: Any) -> list[str]:
    found: set[str] = set()

    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, nested in item.items():
                if str(key).lower() in FORBIDDEN_DISPLAY_PAYLOAD_KEYS:
                    found.add(str(key))
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)

    walk(value)
    return sorted(found)


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        ALREADY_PRODUCED_SUMMARY_STATEMENT,
        DISPLAY_ONLY_STATEMENT,
        NO_PROVIDER_API_MODEL_STATEMENT,
        NO_EXECUTION_DEVICE_STATEMENT,
        NEXT_PHASE_FALSE_STATEMENT,
        NOT_DAY141_REDO_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day142 boundary statements.")


def write_day142_ai_summary_to_dry_run_draft_display_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day142_ai_summary_to_dry_run_draft_display_contract(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day142_ai_summary_to_dry_run_draft_display_contract_html(safe_report, html_path)
    return json_path, html_path


def write_day142_ai_summary_to_dry_run_draft_display_contract_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    boundary_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    payload = report.get("display_payload", {})
    payload_rows = _table_rows((field, payload.get(field, "")) for field in REQUIRED_DISPLAY_PAYLOAD_FIELDS)
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
  <p><strong>{html.escape(ALREADY_PRODUCED_SUMMARY_STATEMENT)}</strong></p>
  <p><strong>{html.escape(DISPLAY_ONLY_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_PROVIDER_API_MODEL_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_DEVICE_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NEXT_PHASE_FALSE_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NOT_DAY141_REDO_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Display Payload</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{payload_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day142_ai_summary_to_dry_run_draft_display_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day142_ai_summary_to_dry_run_draft_display_contract(project_root)
    json_path, html_path = write_day142_ai_summary_to_dry_run_draft_display_contract_reports(
        project_root,
        report,
    )
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(f"agents_md_read_before_day142_work: {json.dumps(report['agents_md_read_before_day142_work'])}")
    print(f"agents_md_pre_read_result: {json.dumps(report['agents_md_pre_read_result'])}")
    print(f"source_summary_id: {json.dumps(report['source_summary_id'])}")
    print(f"source_summary_status: {json.dumps(report['source_summary_status'])}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    payload = report["display_payload"]
    print(f"display_payload.source_summary_id: {json.dumps(payload['source_summary_id'])}")
    print(f"display_payload.source_summary_status: {json.dumps(payload['source_summary_status'])}")
    print(f"display_payload.review_required: {json.dumps(payload['review_required'])}")
    print(f"display_payload.next_phase_allowed: {json.dumps(payload['next_phase_allowed'])}")
    print(f"display_payload_contract_status: {json.dumps(report['display_payload_contract_status'])}")
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
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

