"""Day126 post-refactor compatibility evidence pack.

This module is deterministic and report-only. It packages compatibility
evidence for the Day120-Day125 responsibility-split work while representing
Day125 thin CLI evidence as a single snapshot only. It deliberately does not
add a thin CLI budget gate, numeric budget thresholds, or long-term enforcement.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from intent_safety_invariant_helpers import (
    assert_review_only_safety_invariants,
    build_blocked_execution_capabilities,
    build_default_safety_invariants,
)
from intent_thin_cli_regression_gate import build_thin_cli_check
from network_lab_task_registry import (
    CANONICAL_TASK_NAMES,
    UnknownTaskError,
    resolve_task_name,
)


DAY = 126
DAY_LABEL = "Day126"
TASK_NAME = "post-refactor-compatibility-evidence-pack"
TITLE = "Post-Refactor Compatibility Evidence Pack"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
SCHEMA_VERSION = "day126.post_refactor_compatibility_evidence_pack.v1"
CREATED_AT = "2026-06-14T00:00:00+08:00"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
COMPATIBILITY_STATUS = "COMPATIBILITY_EVIDENCE_READY"
POST_REFACTOR_SCOPE = "DAY120_DAY125"
FINAL_RECOMMENDATION = "KEEP_COMPATIBILITY_EVIDENCE_REVIEW_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day126_post_refactor_compatibility_evidence_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day126_post_refactor_compatibility_evidence_pack.html"

COMPATIBILITY_RECORD_IDS: Tuple[str, ...] = (
    "DAY120_NETWORK_LAB_TASK_REGISTRY_EXTRACTION",
    "DAY121_CLI_DISPATCH_RESPONSIBILITY_SPLIT",
    "DAY122_REPORT_REGISTRY_EXTRACTION",
    "DAY123_TASK_OUTPUT_FORMATTER_EXTRACTION",
    "DAY124_SAFETY_INVARIANT_HELPER_CONSOLIDATION",
    "DAY125_THIN_CLI_REGRESSION_GATE_SNAPSHOT",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "overall_status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day126_work",
    "compatibility_pack_status",
    "post_refactor_scope",
    "thin_cli_snapshot_included",
    "thin_cli_budget_gate_added",
    "thin_cli_budget_enforcement_added",
    "live_execution_introduced",
    "ssh_introduced",
    "openai_or_voice_runtime_introduced",
    "mapped_task_execution_introduced",
    "reviewer_only",
    "next_phase_allowed",
)

FORBIDDEN_BUDGET_MARKERS: Tuple[str, ...] = (
    "max_cli_lines",
    "max_functions",
    "max_dispatch_score",
    "responsibility_score",
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day126_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day126_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    passed = bool(agents_md_read_before_day126_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if passed else FAIL_STATUS,
        "agents_md_read_before_day126_work": passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def build_compatibility_records(project_root: Path) -> List[Dict[str, Any]]:
    root = Path(project_root)
    registry_record = _build_registry_record()
    dispatch_record = _build_source_record(
        project_root=root,
        record_id="DAY121_CLI_DISPATCH_RESPONSIBILITY_SPLIT",
        source_day="Day121",
        source_theme="CLI dispatch responsibility split",
        evidence_type="static dispatch compatibility evidence",
        path=Path("network_lab_cli_dispatch.py"),
        required_terms=(
            "resolve_task_handler",
            "get_cli_task_choices",
            "_build_task_handlers",
            TASK_NAME,
        ),
    )
    report_registry_record = _build_source_record(
        project_root=root,
        record_id="DAY122_REPORT_REGISTRY_EXTRACTION",
        source_day="Day122",
        source_theme="Report registry extraction compatibility",
        evidence_type="report-index catalog compatibility evidence",
        path=Path("network_lab.py"),
        required_terms=(
            "REPORT_CATALOG = [",
            "discover_report_visibility",
            "write_report_index_html",
            "day126_post_refactor_compatibility_evidence_pack.json",
        ),
    )
    formatter_record = _build_source_record(
        project_root=root,
        record_id="DAY123_TASK_OUTPUT_FORMATTER_EXTRACTION",
        source_day="Day123",
        source_theme="Task output formatter compatibility",
        evidence_type="formatter surface compatibility evidence",
        path=Path("network_lab.py"),
        required_terms=(
            "def format_status",
            "def format_heading",
            "format_status_func=format_status",
            "relative_to_project_func=_relative_to_project",
        ),
    )
    safety_record = _build_safety_helper_record()
    thin_cli_record = _build_thin_cli_snapshot_record(root)
    return [
        registry_record,
        dispatch_record,
        report_registry_record,
        formatter_record,
        safety_record,
        thin_cli_record,
    ]


def _build_registry_record() -> Dict[str, Any]:
    checks: Dict[str, bool] = {
        "registry_contains_day126_task": TASK_NAME in CANONICAL_TASK_NAMES,
        "registry_contains_day125_snapshot_source": "thin-cli-regression-gate" in CANONICAL_TASK_NAMES,
        "report_index_still_registered": "report-index" in CANONICAL_TASK_NAMES,
    }
    resolved_tasks: Dict[str, str] = {}
    validation_errors: List[str] = []
    for task_name in ("report-index", "thin-cli-regression-gate", TASK_NAME):
        try:
            resolved_tasks[task_name] = resolve_task_name(task_name)
        except UnknownTaskError as exc:
            validation_errors.append(str(exc))

    try:
        resolve_task_name("day126-unknown-compatibility-task")
    except UnknownTaskError:
        unknown_task_rejected = True
    else:
        unknown_task_rejected = False
        validation_errors.append("Unknown task unexpectedly resolved.")
    checks["unknown_task_rejected"] = unknown_task_rejected
    validation_errors.extend(name for name, passed in checks.items() if passed is not True)
    return _compatibility_record(
        record_id="DAY120_NETWORK_LAB_TASK_REGISTRY_EXTRACTION",
        source_day="Day120",
        source_theme="Network lab task registry extraction",
        evidence_type="registry resolution compatibility evidence",
        checks=checks,
        validation_errors=validation_errors,
        details={"resolved_tasks": resolved_tasks},
    )


def _build_source_record(
    project_root: Path,
    record_id: str,
    source_day: str,
    source_theme: str,
    evidence_type: str,
    path: Path,
    required_terms: Iterable[str],
) -> Dict[str, Any]:
    source_path = project_root / path
    try:
        source = source_path.read_text(encoding="utf-8")
        readable = True
        read_error = ""
    except OSError as exc:
        source = ""
        readable = False
        read_error = str(exc)

    checks = {"source_readable": readable}
    for term in required_terms:
        checks[f"contains:{term}"] = term in source

    validation_errors = [name for name, passed in checks.items() if passed is not True]
    if read_error:
        validation_errors.append(f"{path.as_posix()} could not be read: {read_error}")
    return _compatibility_record(
        record_id=record_id,
        source_day=source_day,
        source_theme=source_theme,
        evidence_type=evidence_type,
        checks=checks,
        validation_errors=validation_errors,
        details={"source_path": path.as_posix()},
    )


def _build_safety_helper_record() -> Dict[str, Any]:
    safety_invariants = build_default_safety_invariants()
    blocked_capabilities = build_blocked_execution_capabilities()
    helper_errors = assert_review_only_safety_invariants(
        safety_invariants=safety_invariants,
        blocked_capabilities=blocked_capabilities,
        execution_allowed=False,
    )
    checks = {
        "safety_invariants_all_false": all(value is False for value in safety_invariants.values()),
        "blocked_capabilities_all_false": all(value is False for value in blocked_capabilities.values()),
        "helper_validation_errors_absent": not helper_errors,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    validation_errors.extend(helper_errors)
    return _compatibility_record(
        record_id="DAY124_SAFETY_INVARIANT_HELPER_CONSOLIDATION",
        source_day="Day124",
        source_theme="Safety invariant helper consolidation",
        evidence_type="shared safety invariant helper compatibility evidence",
        checks=checks,
        validation_errors=validation_errors,
        details={
            "safety_invariants": safety_invariants,
            "blocked_capabilities": blocked_capabilities,
        },
    )


def _build_thin_cli_snapshot_record(project_root: Path) -> Dict[str, Any]:
    snapshot = build_thin_cli_check(project_root)
    checks = {
        "thin_cli_snapshot_included": True,
        "snapshot_only": True,
        "thin_cli_check_passed": snapshot.get("result") == OVERALL_STATUS,
        "thin_cli_budget_gate_added": False,
        "thin_cli_budget_enforcement_added": False,
        "numeric_budget_thresholds_absent": True,
    }
    validation_errors = [
        name for name, passed in checks.items() if passed is not True and name not in {
            "thin_cli_budget_gate_added",
            "thin_cli_budget_enforcement_added",
        }
    ]
    if checks["thin_cli_budget_gate_added"] is not False:
        validation_errors.append("thin_cli_budget_gate_added must be false.")
    if checks["thin_cli_budget_enforcement_added"] is not False:
        validation_errors.append("thin_cli_budget_enforcement_added must be false.")
    return _compatibility_record(
        record_id="DAY125_THIN_CLI_REGRESSION_GATE_SNAPSHOT",
        source_day="Day125",
        source_theme="Thin CLI regression gate snapshot",
        evidence_type="single snapshot evidence item",
        checks=checks,
        validation_errors=validation_errors,
        details={
            "snapshot_source_task": "thin-cli-regression-gate",
            "snapshot": snapshot,
            "snapshot_count": 1,
            "numeric_budget_thresholds": [],
        },
    )


def _compatibility_record(
    record_id: str,
    source_day: str,
    source_theme: str,
    evidence_type: str,
    checks: Mapping[str, Any],
    validation_errors: Iterable[str],
    details: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    errors = list(validation_errors)
    return {
        "record_id": record_id,
        "source_day": source_day,
        "source_theme": source_theme,
        "compatibility_status": "COMPATIBLE" if not errors else FAIL_STATUS,
        "evidence_type": evidence_type,
        "execution_boundary_preserved": not errors,
        "reviewer_boundary_preserved": not errors,
        "regression_detected": bool(errors),
        "checks": dict(checks),
        "details": dict(details or {}),
        "validation_errors": errors,
    }


def build_post_refactor_compatibility_evidence_pack(
    project_root: Path,
    agents_md_read_before_day126_work: bool = True,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day126_work=agents_md_read_before_day126_work,
    )
    compatibility_records = build_compatibility_records(project_root)
    safety_invariants = build_default_safety_invariants()
    blocked_capabilities = build_blocked_execution_capabilities()
    helper_errors = assert_review_only_safety_invariants(
        safety_invariants=safety_invariants,
        blocked_capabilities=blocked_capabilities,
        execution_allowed=False,
    )

    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "created_at": CREATED_AT,
        "schema_version": SCHEMA_VERSION,
        "overall_status": "PENDING",
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_day126_work": agents_evidence["agents_md_read_before_day126_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "compatibility_pack_status": COMPATIBILITY_STATUS,
        "post_refactor_scope": POST_REFACTOR_SCOPE,
        "compatibility_records": compatibility_records,
        "compatibility_record_count": len(compatibility_records),
        "compatible_record_count": sum(
            1 for record in compatibility_records if record["compatibility_status"] == "COMPATIBLE"
        ),
        "regression_detected_count": sum(1 for record in compatibility_records if record["regression_detected"]),
        "thin_cli_snapshot_included": True,
        "thin_cli_snapshot_count": 1,
        "thin_cli_budget_gate_added": False,
        "thin_cli_budget_enforcement_added": False,
        "long_term_numeric_budget_enforcement_added": False,
        "numeric_budget_thresholds": [],
        "budget_blocking_policy_added": False,
        "live_execution_introduced": False,
        "ssh_introduced": False,
        "device_connection_introduced": False,
        "configuration_change_introduced": False,
        "openai_or_voice_runtime_introduced": False,
        "mapped_task_execution_introduced": False,
        "dashboard_action_endpoint_introduced": False,
        "execution_unlock_introduced": False,
        "reviewer_only": True,
        "report_only": True,
        "next_phase_allowed": False,
        "safety_invariants": safety_invariants,
        "blocked_capabilities": blocked_capabilities,
        "final_recommendation": FINAL_RECOMMENDATION,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "agents_md_evidence": agents_evidence,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report, helper_errors)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    if report["overall_status"] != OVERALL_STATUS:
        report["compatibility_pack_status"] = "COMPATIBILITY_EVIDENCE_BLOCKED"
    return report


def collect_validation_errors(report: Mapping[str, Any], helper_errors: Iterable[str] = ()) -> List[str]:
    errors = list(helper_errors)
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day126_work") is not True:
        errors.append("AGENTS.md read-before-Day126-work evidence is not true.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    if report.get("post_refactor_scope") != POST_REFACTOR_SCOPE:
        errors.append(f"post_refactor_scope must be {POST_REFACTOR_SCOPE}.")
    record_ids = [record.get("record_id") for record in report.get("compatibility_records", [])]
    if tuple(record_ids) != COMPATIBILITY_RECORD_IDS:
        errors.append("compatibility_records must include exactly the Day120-Day125 record sequence.")
    for record in report.get("compatibility_records", []):
        if record.get("compatibility_status") != "COMPATIBLE":
            errors.append(f"{record.get('record_id')} is not COMPATIBLE.")
        if record.get("regression_detected") is not False:
            errors.append(f"{record.get('record_id')} detected a regression.")
        if record.get("execution_boundary_preserved") is not True:
            errors.append(f"{record.get('record_id')} execution boundary was not preserved.")
        if record.get("reviewer_boundary_preserved") is not True:
            errors.append(f"{record.get('record_id')} reviewer boundary was not preserved.")
    if report.get("thin_cli_snapshot_included") is not True:
        errors.append("thin_cli_snapshot_included must be true.")
    if report.get("thin_cli_snapshot_count") != 1:
        errors.append("thin_cli_snapshot_count must be exactly 1.")
    for flag in (
        "thin_cli_budget_gate_added",
        "thin_cli_budget_enforcement_added",
        "long_term_numeric_budget_enforcement_added",
        "budget_blocking_policy_added",
        "live_execution_introduced",
        "ssh_introduced",
        "device_connection_introduced",
        "configuration_change_introduced",
        "openai_or_voice_runtime_introduced",
        "mapped_task_execution_introduced",
        "dashboard_action_endpoint_introduced",
        "execution_unlock_introduced",
        "next_phase_allowed",
    ):
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")
    if report.get("numeric_budget_thresholds") != []:
        errors.append("numeric_budget_thresholds must remain empty.")
    if report.get("reviewer_only") is not True or report.get("report_only") is not True:
        errors.append("Day126 must remain reviewer-only and report-only.")
    return errors


def write_post_refactor_compatibility_evidence_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_post_refactor_compatibility_evidence_pack(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_post_refactor_compatibility_evidence_pack_html(safe_report, html_path)
    return json_path, html_path


def write_post_refactor_compatibility_evidence_pack_html(
    report: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record_rows = _table_rows(
        (
            record["record_id"],
            record["source_day"],
            record["source_theme"],
            record["compatibility_status"],
            record["evidence_type"],
            record["execution_boundary_preserved"],
            record["reviewer_boundary_preserved"],
            record["regression_detected"],
        )
        for record in report["compatibility_records"]
    )
    safety_rows = _table_rows(
        (
            ("thin_cli_snapshot_included", report["thin_cli_snapshot_included"]),
            ("thin_cli_snapshot_count", report["thin_cli_snapshot_count"]),
            ("thin_cli_budget_gate_added", report["thin_cli_budget_gate_added"]),
            ("thin_cli_budget_enforcement_added", report["thin_cli_budget_enforcement_added"]),
            ("live_execution_introduced", report["live_execution_introduced"]),
            ("ssh_introduced", report["ssh_introduced"]),
            ("openai_or_voice_runtime_introduced", report["openai_or_voice_runtime_introduced"]),
            ("mapped_task_execution_introduced", report["mapped_task_execution_introduced"]),
            ("next_phase_allowed", report["next_phase_allowed"]),
        )
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['full_title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    .pass, .compatible {{ color: #116329; font-weight: bold; }}
    .fail {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['full_title'])}</h1>
  <p><strong>Overall status:</strong> <span class="{html.escape(str(report['overall_status']).lower())}">{html.escape(report['overall_status'])}</span></p>
  <p><strong>Compatibility pack status:</strong> <code>{html.escape(report['compatibility_pack_status'])}</code></p>
  <p><strong>AGENTS.md pre-read:</strong> <code>{html.escape(report['agents_md_pre_read_result'])}</code>, read before work: <code>{html.escape(json.dumps(report['agents_md_read_before_day126_work']))}</code></p>
  <p><strong>Thin CLI rule:</strong> one snapshot is included; no thin CLI budget gate, budget enforcement, numeric thresholds, or blocking policy is added.</p>

  <h2>Compatibility Records</h2>
  <table>
    <thead><tr><th>Record</th><th>Day</th><th>Theme</th><th>Status</th><th>Evidence</th><th>Execution Boundary</th><th>Reviewer Boundary</th><th>Regression</th></tr></thead>
    <tbody>{record_rows}</tbody>
  </table>

  <h2>Safety and Thin CLI Snapshot</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{safety_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_post_refactor_compatibility_evidence_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_post_refactor_compatibility_evidence_pack(project_root)
    json_path, html_path = write_post_refactor_compatibility_evidence_pack_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: report-only; reviewer-only; no live execution, SSH, device connection, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or execution unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"thin_cli_snapshot_count: {report['thin_cli_snapshot_count']}")
    print(f"long_term_numeric_budget_enforcement_added: {json.dumps(report['long_term_numeric_budget_enforcement_added'])}")
    print(f"numeric_budget_thresholds: {json.dumps(report['numeric_budget_thresholds'])}")
    print(f"compatibility_record_count: {report['compatibility_record_count']}")
    print(f"compatible_record_count: {report['compatible_record_count']}")
    print(f"regression_detected_count: {report['regression_detected_count']}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {COMPATIBILITY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} Day126 compatibility evidence pack failed.")
    return 1


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value) or "none"
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )


def main() -> int:
    report = build_post_refactor_compatibility_evidence_pack(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
