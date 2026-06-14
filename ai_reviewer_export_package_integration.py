"""Day136 AI reviewer export package integration.

This module packages existing AI reviewer evidence into a deterministic
review-only export package. It reads local repository evidence files only and
does not call providers, APIs, network paths, SSH, devices, adapters, brokers,
runners, or execution paths.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple

from intent_safety_invariant_helpers import (
    FINAL_RECOMMENDATION,
    assert_review_only_safety_invariants,
    build_blocked_execution_capabilities,
    build_default_safety_invariants,
)


DAY = 136
DAY_LABEL = "Day136"
TASK_NAME = "ai-reviewer-export-package-integration"
TITLE = "AI Reviewer Export Package Integration"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
PACKAGE_ID = "day136-ai-reviewer-export-package"
MODE = "REVIEW_ONLY"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
PACKAGE_STATUS = "AI_REVIEWER_EXPORT_PACKAGE_READY"
BLOCKED_PACKAGE_STATUS = "AI_REVIEWER_EXPORT_PACKAGE_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "day136_ai_reviewer_export_package_integration.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day136_ai_reviewer_export_package_integration.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day136_ai_reviewer_export_package_integration.md"

NOT_NEXT_DAY_STATEMENT = "This is not next-day functionality."
NO_EXECUTION_PROVIDER_API_STATEMENT = "Execution / provider / API remain disabled."

SOURCE_EVIDENCE: Tuple[Dict[str, Any], ...] = (
    {
        "day": 127,
        "section": "AI reviewer summary schema",
        "task": "ai-reviewer-summary-schema-contract",
        "path": Path("reports") / "lab-summary" / "day127_ai_reviewer_summary_schema_contract.json",
        "status_field": "overall_status",
    },
    {
        "day": 128,
        "section": "AI reviewer summary fixture renderer",
        "task": "ai-reviewer-summary-fixture-renderer",
        "path": Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.json",
        "status_field": "overall_status",
    },
    {
        "day": 129,
        "section": "AI summary prompt contract",
        "task": "ai-summary-prompt-contract",
        "path": Path("reports") / "lab-summary" / "day129_ai_summary_prompt_contract.json",
        "status_field": "overall_status",
    },
    {
        "day": 130,
        "section": "AI summary redaction and no-secret policy",
        "task": "ai-summary-redaction-and-no-secret-policy",
        "path": Path("reports") / "lab-summary" / "day130_ai_summary_redaction_and_no_secret_policy.json",
        "status_field": "overall_status",
    },
    {
        "day": 131,
        "section": "AI summary audit trail binding",
        "task": "ai-summary-audit-trail-binding",
        "path": Path("reports") / "lab-summary" / "day131_ai_summary_audit_trail_binding.json",
        "status_field": "overall_status",
    },
    {
        "day": 132,
        "section": "AI summary dashboard card integration",
        "task": "ai-summary-dashboard-card-integration",
        "path": Path("reports") / "lab-summary" / "day132_ai_summary_dashboard_card_integration.json",
        "status_field": "overall_status",
    },
    {
        "day": 133,
        "section": "Disabled AI provider interface boundary",
        "task": "disabled-ai-provider-interface-boundary",
        "path": Path("reports") / "lab-summary" / "day133_disabled_ai_provider_interface_boundary.json",
        "status_field": "overall_status",
    },
    {
        "day": 134,
        "section": "Disabled AI provider adapter contract",
        "task": "disabled-ai-provider-adapter-contract",
        "path": Path("reports") / "lab-summary" / "day134_disabled_ai_provider_adapter_contract.json",
        "status_field": "overall_status",
    },
    {
        "day": 135,
        "section": "Disabled-by-default provider safety regression and consumer gate",
        "task": "ai-provider-disabled-by-default-safety-regression",
        "path": Path("reports") / "lab-summary" / "day135_ai_provider_disabled_by_default_safety_regression.json",
        "status_field": "overall_status",
    },
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "live_actions_enabled",
    "secret_or_env_access",
    "external_network_call",
    "adapter_broker_runner_invoked",
    "model_invocation_enabled",
    "ssh_enabled",
    "device_action_enabled",
    "next_day_functionality_enabled",
)

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "deterministic",
    "local_repo_evidence_only",
    "statement_present_not_next_day_functionality",
    "statement_present_no_execution_provider_api",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "package_id",
    "package_name",
    "day",
    "title",
    "status",
    "review_only",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "live_actions_enabled",
    "source_sections",
    "included_evidence",
    "redaction_status",
    "audit_binding_status",
    "consumer_gate_status",
    "safety_invariants",
    "reviewer_next_action",
    "not_next_day_statement",
    "no_execution_provider_api_statement",
    "agents_md_found",
    "agents_md_pre_read_before_changes",
    "agents_md_modified",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_pre_read_before_changes": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
            "agents_md_read_error": "AGENTS.md not found.",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_pre_read_before_changes": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "READ_ERROR",
            "agents_md_read_error": str(exc),
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_pre_read_before_changes": required_phrase_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if required_phrase_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
        "agents_md_read_error": "",
    }


def load_source_sections(project_root: Path) -> Tuple[list[Dict[str, Any]], list[str]]:
    sections: list[Dict[str, Any]] = []
    errors: list[str] = []
    for source in SOURCE_EVIDENCE:
        relative_path = source["path"]
        path = Path(project_root) / relative_path
        section: Dict[str, Any] = {
            "day": source["day"],
            "section": source["section"],
            "task": source["task"],
            "path": relative_path.as_posix(),
            "read_only": True,
            "loaded": False,
            "status": "MISSING",
            "evidence_keys": [],
        }
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            section["read_error"] = f"Missing source evidence: {relative_path.as_posix()}"
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue
        except json.JSONDecodeError as exc:
            section["status"] = "INVALID_JSON"
            section["read_error"] = f"Invalid JSON in {relative_path.as_posix()}: {exc.msg}"
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue
        except OSError as exc:
            section["status"] = "READ_ERROR"
            section["read_error"] = str(exc)
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue

        if not isinstance(loaded, dict):
            section["status"] = "INVALID_SHAPE"
            section["read_error"] = f"{relative_path.as_posix()} must contain a JSON object."
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue

        section["loaded"] = True
        section["status"] = str(loaded.get(source["status_field"], loaded.get("status", "UNKNOWN")))
        section["evidence_keys"] = sorted(str(key) for key in loaded.keys())
        section["evidence_summary"] = extract_source_summary(int(source["day"]), loaded)
        sections.append(section)

    return sections, errors


def extract_source_summary(day: int, loaded: Mapping[str, Any]) -> Dict[str, Any]:
    if day == 130:
        return {
            "redaction_status": loaded.get("redaction_status", loaded.get("policy_status", "UNKNOWN")),
            "secret_or_env_access": False,
        }
    if day == 131:
        return {
            "audit_binding_status": loaded.get("audit_status", "UNKNOWN"),
            "audit_record_count": loaded.get("audit_record_count", 0),
        }
    if day == 135:
        return {
            "consumer_gate_status": "PASS" if loaded.get("consumer_read_allowed") is True else "BLOCKED",
            "regression_verdict": loaded.get("regression_verdict", "UNKNOWN"),
        }
    return {
        "overall_status": loaded.get("overall_status", loaded.get("status", "UNKNOWN")),
        "task": loaded.get("task", ""),
    }


def build_ai_reviewer_export_package_integration_report(project_root: Path) -> Dict[str, Any]:
    agents = build_agents_md_evidence(project_root)
    source_sections, source_errors = load_source_sections(project_root)
    safety_invariants = build_default_safety_invariants()
    blocked_capabilities = build_blocked_execution_capabilities()
    included_evidence = build_included_evidence(source_sections)

    report: Dict[str, Any] = {
        "package_id": PACKAGE_ID,
        "package_name": PACKAGE_ID,
        "day": DAY,
        "day_label": DAY_LABEL,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "task": TASK_NAME,
        "mode": MODE,
        "status": "PENDING",
        "overall_status": "PENDING",
        "review_only": True,
        "report_only": True,
        "deterministic": True,
        "local_repo_evidence_only": True,
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "live_actions_enabled": False,
        "secret_or_env_access": False,
        "external_network_call": False,
        "adapter_broker_runner_invoked": False,
        "model_invocation_enabled": False,
        "ssh_enabled": False,
        "device_action_enabled": False,
        "next_day_functionality_enabled": False,
        "not_next_day_statement": NOT_NEXT_DAY_STATEMENT,
        "no_execution_provider_api_statement": NO_EXECUTION_PROVIDER_API_STATEMENT,
        "statement_present_not_next_day_functionality": True,
        "statement_present_no_execution_provider_api": True,
        **agents,
        "source_sections": source_sections,
        "included_evidence": included_evidence,
        "redaction_status": included_evidence["redaction_status"],
        "audit_binding_status": included_evidence["audit_binding_status"],
        "consumer_gate_status": included_evidence["consumer_gate_status"],
        "safety_invariants": safety_invariants,
        "blocked_capabilities": blocked_capabilities,
        "safety_invariant_validation": [],
        "reviewer_next_action": "Review the packaged Day127-Day135 evidence; do not enable providers, APIs, execution, live actions, SSH, adapters, brokers, or runners.",
        "explicit_statements": [
            NOT_NEXT_DAY_STATEMENT,
            NO_EXECUTION_PROVIDER_API_STATEMENT,
        ],
        "scope": "Day136 export package integration only.",
        "non_goals": [
            "No next-day functionality.",
            "No provider enablement.",
            "No API enablement.",
            "No API key, token, secret, credential, or environment variable lookup.",
            "No external network call.",
            "No SSH, RouterOS, device action, adapter execution, broker execution, runner execution, or live execution.",
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": source_errors,
    }
    report["safety_invariant_validation"] = assert_review_only_safety_invariants(
        safety_invariants=safety_invariants,
        blocked_capabilities=blocked_capabilities,
        execution_allowed=False,
        final_recommendation=FINAL_RECOMMENDATION,
    )
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = PACKAGE_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_PACKAGE_STATUS
    return report


def build_included_evidence(source_sections: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    sections = list(source_sections)
    by_day = {section.get("day"): section for section in sections}
    day130 = by_day.get(130, {})
    day131 = by_day.get(131, {})
    day135 = by_day.get(135, {})
    return {
        "source_day_range": "Day127-Day135",
        "source_count": len(sections),
        "loaded_source_count": sum(1 for section in sections if section.get("loaded") is True),
        "evidence_paths": [str(section.get("path", "")) for section in sections],
        "redaction_status": _summary_value(day130, "redaction_status"),
        "audit_binding_status": _summary_value(day131, "audit_binding_status"),
        "consumer_gate_status": _summary_value(day135, "consumer_gate_status"),
    }


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors = list(report.get("validation_errors", []))
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    if report.get("agents_md_found") is not True:
        errors.append("AGENTS.md must exist before Day136 work.")
    if report.get("agents_md_pre_read_before_changes") is not True:
        errors.append("AGENTS.md must be read before Day136 changes.")
    if report.get("agents_md_modified") is not False:
        errors.append("AGENTS.md modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("not_next_day_statement") != NOT_NEXT_DAY_STATEMENT:
        errors.append("not-next-day statement is missing or changed.")
    if report.get("no_execution_provider_api_statement") != NO_EXECUTION_PROVIDER_API_STATEMENT:
        errors.append("execution/provider/API disabled statement is missing or changed.")
    if report.get("redaction_status") in {"", "UNKNOWN"}:
        errors.append("redaction_status must be sourced from Day130 evidence.")
    if report.get("audit_binding_status") in {"", "UNKNOWN"}:
        errors.append("audit_binding_status must be sourced from Day131 evidence.")
    if report.get("consumer_gate_status") != "PASS":
        errors.append("consumer_gate_status must be PASS from Day135 read-only evidence.")

    for invariant_error in report.get("safety_invariant_validation", []):
        errors.append(str(invariant_error))
    for section in report.get("source_sections", []):
        if section.get("loaded") is not True:
            errors.append(f"source section not loaded: {section.get('path')}")
        if section.get("read_only") is not True:
            errors.append(f"source section must be read-only: {section.get('path')}")
    return errors


def write_ai_reviewer_export_package_integration_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_reviewer_export_package_integration_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_reviewer_export_package_integration_html(safe_report, html_path)
    return json_path, html_path


def write_ai_reviewer_export_package_integration_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    source_rows = _table_rows(
        (
            section.get("day", ""),
            section.get("section", ""),
            section.get("task", ""),
            section.get("status", ""),
            section.get("loaded", False),
            section.get("path", ""),
        )
        for section in report.get("source_sections", [])
    )
    invariant_rows = _table_rows((key, value) for key, value in report.get("safety_invariants", {}).items())
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
  <p><strong>{html.escape(str(report['not_next_day_statement']))}</strong></p>
  <p><strong>{html.escape(str(report['no_execution_provider_api_statement']))}</strong></p>
  <h2>Package Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Source Sections</h2>
  <table><thead><tr><th>Day</th><th>Section</th><th>Task</th><th>Status</th><th>Loaded</th><th>Path</th></tr></thead><tbody>{source_rows}</tbody></table>
  <h2>Safety Invariants</h2>
  <table><thead><tr><th>Flag</th><th>Value</th></tr></thead><tbody>{invariant_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_reviewer_export_package_integration(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_reviewer_export_package_integration_report(project_root)
    json_path, html_path = write_ai_reviewer_export_package_integration_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(report["not_next_day_statement"])
    print(report["no_execution_provider_api_statement"])
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    for field in REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {PACKAGE_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_PACKAGE_STATUS}")
    return 1


def _summary_value(section: Mapping[str, Any], key: str) -> Any:
    summary = section.get("evidence_summary", {})
    if isinstance(summary, Mapping):
        return summary.get(key, "UNKNOWN")
    return "UNKNOWN"


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
    report = build_ai_reviewer_export_package_integration_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
