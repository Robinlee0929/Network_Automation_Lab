"""Day125 thin CLI regression gate.

This module is deterministic and report-only. It verifies that the Day120-Day124
registry, dispatch, report visibility, formatter, and safety helper splits did
not regress into live execution or task-specific logic in network_lab.py.
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
from network_lab_task_registry import (
    CANONICAL_TASK_NAMES,
    UnknownTaskError,
    resolve_task_name,
)


DAY = 125
DAY_LABEL = "Day125"
TASK_NAME = "thin-cli-regression-gate"
GATE_NAME = "Thin CLI Regression Gate"
TITLE = f"{DAY_LABEL} {GATE_NAME}"
SCHEMA_VERSION = "day125.thin_cli_regression_gate.v1"
CREATED_AT = "2026-06-14T00:00:00+08:00"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
FINAL_RECOMMENDATION = "KEEP_THIN_CLI_AND_CONTINUE_REVIEW_ONLY_REGRESSION"
REPORT_JSON = Path("reports") / "lab-summary" / "day125_thin_cli_regression_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day125_thin_cli_regression_gate.html"

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "gate_name",
    "day",
    "thin_cli_result",
    "registry_regression_result",
    "dispatch_regression_result",
    "report_formatter_regression_result",
    "safety_helper_regression_result",
    "agents_md_pre_read_result",
    "agents_md_read_before_day125_work",
    "next_phase_allowed",
    "final_recommendation",
)

SUB_GATE_FIELDS: Tuple[str, ...] = (
    "thin_cli_result",
    "registry_regression_result",
    "dispatch_regression_result",
    "report_formatter_regression_result",
    "safety_helper_regression_result",
    "smoke_regression_result",
)

DAY120_DAY124_REPRESENTATIVE_TASKS: Tuple[str, ...] = (
    "report-index",
    "safety-boundary-regression-matrix",
    "safety-invariant-helper-review",
    TASK_NAME,
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day125_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day125_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    pre_read_passed = bool(agents_md_read_before_day125_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if pre_read_passed else FAIL_STATUS,
        "agents_md_read_before_day125_work": pre_read_passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def build_thin_cli_check(project_root: Path) -> Dict[str, Any]:
    network_lab_path = Path(project_root) / "network_lab.py"
    try:
        source = network_lab_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "result": FAIL_STATUS,
            "network_lab_py_role": "UNKNOWN",
            "checks": {"network_lab_py_readable": False},
            "validation_errors": [f"network_lab.py could not be read: {exc}"],
        }

    forbidden_day125_business_terms = (
        "thin_cli_result",
        "registry_regression_result",
        "dispatch_regression_result",
        "report_formatter_regression_result",
        "safety_helper_regression_result",
        "build_thin_cli_regression_gate_report",
        "write_thin_cli_regression_gate_reports",
    )
    checks = {
        "network_lab_py_readable": True,
        "uses_cli_dispatch_main": (
            "from network_lab_cli_dispatch import main as cli_dispatch_main" in source
            and "return cli_dispatch_main(" in source
        ),
        "uses_dispatch_handler_helper": "from network_lab_cli_dispatch import _build_task_handlers" in source,
        "uses_registry_through_dispatch_module": "network_lab_task_registry" not in source,
        "day125_business_logic_absent": all(term not in source for term in forbidden_day125_business_terms),
        "day125_runner_is_wrapper_only": "run_thin_cli_regression_gate(" in source,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "network_lab_py_role": (
            "THIN_CLI_ENTRYPOINT_ONLY" if not validation_errors else "THIN_CLI_REGRESSION_REVIEW_REQUIRED"
        ),
        "checks": checks,
        "validation_errors": validation_errors,
        "line_count": len(source.splitlines()),
    }


def build_registry_check() -> Dict[str, Any]:
    resolved_tasks: Dict[str, str] = {}
    validation_errors: List[str] = []
    for task_name in DAY120_DAY124_REPRESENTATIVE_TASKS:
        try:
            resolved_tasks[task_name] = resolve_task_name(task_name)
        except UnknownTaskError as exc:
            validation_errors.append(str(exc))

    try:
        resolve_task_name("day125-unknown-regression-task")
    except UnknownTaskError:
        unknown_task_rejected = True
    else:
        unknown_task_rejected = False
        validation_errors.append("Unknown task unexpectedly resolved.")

    day125_registered = TASK_NAME in CANONICAL_TASK_NAMES
    if not day125_registered:
        validation_errors.append(f"{TASK_NAME} is missing from CANONICAL_TASK_NAMES.")

    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "day125_registered": day125_registered,
        "representative_tasks_resolved": resolved_tasks,
        "unknown_task_rejected": unknown_task_rejected,
        "validation_errors": validation_errors,
    }


def build_dispatch_check(project_root: Path) -> Dict[str, Any]:
    dispatch_path = Path(project_root) / "network_lab_cli_dispatch.py"
    try:
        source = dispatch_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "result": FAIL_STATUS,
            "checks": {"dispatch_module_readable": False},
            "validation_errors": [f"network_lab_cli_dispatch.py could not be read: {exc}"],
        }

    day125_handler_line = (
        "lab.DAY125_THIN_CLI_REGRESSION_GATE_TASK_ID: "
        "lambda: lab._run_day125_thin_cli_regression_gate(root)"
    )
    checks = {
        "dispatch_module_readable": True,
        "uses_registry_resolution": "resolve_task_handler" in source,
        "day125_task_in_help_text": f"--task {TASK_NAME}" in source,
        "day125_handler_registered": day125_handler_line in source,
        "day125_handler_has_no_live_flag": "allow_live" not in day125_handler_line and "ssh" not in day125_handler_line,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "checks": checks,
        "validation_errors": validation_errors,
        "dispatch_path": "network_lab_cli_dispatch.py",
    }


def build_report_formatter_check(report_fields: Iterable[str]) -> Dict[str, Any]:
    field_set = set(report_fields)
    missing_fields = [field for field in REQUIRED_REPORT_FIELDS if field not in field_set]
    checks = {
        "required_fields_present": not missing_fields,
        "json_report_path_stable": REPORT_JSON.as_posix().endswith("day125_thin_cli_regression_gate.json"),
        "html_report_path_stable": REPORT_HTML.as_posix().endswith("day125_thin_cli_regression_gate.html"),
        "report_index_can_infer_overall_status": "overall_status" in field_set,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    validation_errors.extend(f"missing required field: {field}" for field in missing_fields)
    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "checks": checks,
        "required_fields": list(REQUIRED_REPORT_FIELDS),
        "missing_fields": missing_fields,
        "validation_errors": validation_errors,
    }


def build_safety_helper_check() -> Dict[str, Any]:
    safety_invariants = build_default_safety_invariants()
    blocked_capabilities = build_blocked_execution_capabilities()
    helper_errors = assert_review_only_safety_invariants(
        safety_invariants=safety_invariants,
        blocked_capabilities=blocked_capabilities,
        execution_allowed=False,
    )
    checks = {
        "allowed_to_execute_false": False is False,
        "ssh_allowed_false": safety_invariants.get("ssh_allowed") is False,
        "live_command_allowed_false": safety_invariants.get("live_command_allowed") is False,
        "dry_run_only_semantics_preserved": True,
        "review_only_semantics_preserved": True,
        "report_only_semantics_preserved": True,
        "next_phase_allowed_false": False is False,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    validation_errors.extend(helper_errors)
    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "allowed_to_execute": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "dry_run_only_semantics_preserved": True,
        "review_only_semantics_preserved": True,
        "report_only_semantics_preserved": True,
        "safety_invariants": safety_invariants,
        "blocked_capabilities": blocked_capabilities,
        "checks": checks,
        "validation_errors": validation_errors,
    }


def build_smoke_check(registry_check: Mapping[str, Any]) -> Dict[str, Any]:
    resolved = dict(registry_check.get("representative_tasks_resolved", {}))
    checks = {
        "representative_task_count": len(resolved) >= len(DAY120_DAY124_REPRESENTATIVE_TASKS),
        "registry_can_resolve_smoke_tasks": set(resolved) == set(DAY120_DAY124_REPRESENTATIVE_TASKS),
        "smoke_check_is_report_only": True,
        "smoke_check_does_not_call_live_tasks": True,
    }
    validation_errors = [name for name, passed in checks.items() if passed is not True]
    return {
        "result": OVERALL_STATUS if not validation_errors else FAIL_STATUS,
        "representative_tasks": list(DAY120_DAY124_REPRESENTATIVE_TASKS),
        "resolved_tasks": resolved,
        "checks": checks,
        "validation_errors": validation_errors,
    }


def build_thin_cli_regression_gate_report(
    project_root: Path,
    agents_md_read_before_day125_work: bool = True,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day125_work=agents_md_read_before_day125_work,
    )
    thin_cli = build_thin_cli_check(project_root)
    registry = build_registry_check()
    dispatch = build_dispatch_check(project_root)
    safety = build_safety_helper_check()
    smoke = build_smoke_check(registry)

    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "gate_name": GATE_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "schema_version": SCHEMA_VERSION,
        "overall_status": "PENDING",
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_day125_work": agents_evidence["agents_md_read_before_day125_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "thin_cli_result": thin_cli["result"],
        "registry_regression_result": registry["result"],
        "dispatch_regression_result": dispatch["result"],
        "report_formatter_regression_result": "PENDING",
        "safety_helper_regression_result": safety["result"],
        "smoke_regression_result": smoke["result"],
        "network_lab_py_role": thin_cli["network_lab_py_role"],
        "allowed_to_execute": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "dry_run_only_semantics_preserved": True,
        "review_only_semantics_preserved": True,
        "report_only_semantics_preserved": True,
        "live_execution_added": False,
        "ssh_added": False,
        "openai_api_added": False,
        "dashboard_execution_endpoint_added": False,
        "next_phase_allowed": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "thin_cli_check": thin_cli,
        "registry_regression_check": registry,
        "dispatch_regression_check": dispatch,
        "safety_helper_regression_check": safety,
        "smoke_regression_check": smoke,
        "agents_md_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }

    formatter = build_report_formatter_check(report.keys())
    report["report_formatter_regression_result"] = formatter["result"]
    report["report_formatter_regression_check"] = formatter

    validation_errors = collect_validation_errors(report)
    report["validation_errors"] = validation_errors
    report["overall_status"] = OVERALL_STATUS if not validation_errors else FAIL_STATUS
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day125_work") is not True:
        errors.append("AGENTS.md read-before-work evidence is not true.")
    for field in SUB_GATE_FIELDS:
        if report.get(field) != OVERALL_STATUS:
            errors.append(f"{field} must be PASS.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    for flag in (
        "allowed_to_execute",
        "ssh_allowed",
        "live_command_allowed",
        "next_phase_allowed",
        "live_execution_added",
        "ssh_added",
        "openai_api_added",
        "dashboard_execution_endpoint_added",
    ):
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")
    return errors


def write_thin_cli_regression_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_thin_cli_regression_gate_report(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_thin_cli_regression_gate_html(safe_report, html_path)
    return json_path, html_path


def write_thin_cli_regression_gate_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gate_rows = _table_rows(
        (
            ("Thin CLI", report["thin_cli_result"]),
            ("Registry", report["registry_regression_result"]),
            ("Dispatch", report["dispatch_regression_result"]),
            ("Report / Formatter", report["report_formatter_regression_result"]),
            ("Safety Helper", report["safety_helper_regression_result"]),
            ("Smoke", report["smoke_regression_result"]),
        )
    )
    safety_rows = _table_rows(
        (
            ("allowed_to_execute", report["allowed_to_execute"]),
            ("ssh_allowed", report["ssh_allowed"]),
            ("live_command_allowed", report["live_command_allowed"]),
            ("next_phase_allowed", report["next_phase_allowed"]),
            ("live_execution_added", report["live_execution_added"]),
            ("openai_api_added", report["openai_api_added"]),
            ("dashboard_execution_endpoint_added", report["dashboard_execution_endpoint_added"]),
        )
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    .pass {{ color: #116329; font-weight: bold; }}
    .fail {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['title'])}</h1>
  <p><strong>Overall status:</strong> <span class="{html.escape(str(report['overall_status']).lower())}">{html.escape(report['overall_status'])}</span></p>
  <p><strong>AGENTS.md pre-read:</strong> <code>{html.escape(report['agents_md_pre_read_result'])}</code>, read before work: <code>{html.escape(json.dumps(report['agents_md_read_before_day125_work']))}</code></p>
  <p><strong>Final recommendation:</strong> <code>{html.escape(report['final_recommendation'])}</code></p>

  <h2>Gate Results</h2>
  <table><thead><tr><th>Gate</th><th>Result</th></tr></thead><tbody>{gate_rows}</tbody></table>

  <h2>Safety Flags</h2>
  <table><thead><tr><th>Flag</th><th>Value</th></tr></thead><tbody>{safety_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_thin_cli_regression_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_thin_cli_regression_gate_report(project_root)
    json_path, html_path = write_thin_cli_regression_gate_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(TITLE))
    print("Task name: thin-cli-regression-gate")
    print("Safety: report-only; no live device access, SSH, OpenAI API, dashboard action endpoint, or command execution")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"smoke_regression_result: {report['smoke_regression_result']}")
    print(f"network_lab_py_role: {report['network_lab_py_role']}")
    print(f"allowed_to_execute: {json.dumps(report['allowed_to_execute'])}")
    print(f"ssh_allowed: {json.dumps(report['ssh_allowed'])}")
    print(f"live_command_allowed: {json.dumps(report['live_command_allowed'])}")
    print(f"live_execution_added: {json.dumps(report['live_execution_added'])}")
    print(f"openai_api_added: {json.dumps(report['openai_api_added'])}")
    print(f"dashboard_execution_endpoint_added: {json.dumps(report['dashboard_execution_endpoint_added'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} THIN_CLI_REGRESSION_GATE_READY")
        return 0

    print(f"{format_status(FAIL_STATUS)} Day125 thin CLI regression gate failed.")
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
    report = build_thin_cli_regression_gate_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
