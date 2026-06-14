"""Day128 AI reviewer summary fixture renderer.

This module renders the existing Day127 AI reviewer summary fixture into stable
reviewer-facing evidence. It consumes Day127's loader and validator, and does
not redefine the schema, make AI decisions, define prompt text, define
redaction policy, call APIs, or enable execution.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from intent_ai_reviewer_summary_schema_contract import (
    FIXTURE_PATH as DAY127_FIXTURE_PATH,
    SCHEMA_VERSION as DAY127_SCHEMA_VERSION,
    load_summary_fixture,
    validate_ai_reviewer_summary_contract,
)


DAY = 128
DAY_LABEL = "Day128"
TASK_NAME = "ai-reviewer-summary-fixture-renderer"
TITLE = "AI Reviewer Summary Fixture Renderer"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
OVERALL_STATUS = "PASS"
BLOCKED_STATUS = "BLOCKED"
FAIL_STATUS = "FAIL"
RENDERER_STATUS = "FIXTURE_RENDERED"
MISSING_FIXTURE_STATUS = "DAY127_SCHEMA_FIXTURE_NOT_FOUND"
REPORT_JSON = Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.html"
REPORT_TXT = Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.txt"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day128_ai_reviewer_summary_fixture_renderer.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day128_ai_reviewer_summary_fixture_renderer.md"


def build_agents_md_pre_read_evidence(
    project_root: Path,
    read_before_code_changes: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_pre_read_result": "MISSING",
            "agents_md_read_before_code_changes": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": "AGENTS.md not found.",
            "agents_md_required_phrase_present": False,
        }
    except OSError as exc:
        return {
            "agents_md_pre_read_result": "READ_ERROR",
            "agents_md_read_before_code_changes": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": (
            "FOUND_AND_READ"
            if read_before_code_changes and required_phrase_present
            else "FOUND_BUT_PRE_READ_NOT_CONFIRMED"
        ),
        "agents_md_read_before_code_changes": bool(read_before_code_changes and required_phrase_present),
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def render_day127_summary_fixture(fixture: Mapping[str, Any]) -> str:
    """Render the Day127 fixture in a stable human-readable text form."""
    lines = [
        "Day128 AI Reviewer Summary Fixture Renderer",
        f"schema_version: {_string_value(fixture.get('schema_version'))}",
        f"summary_id: {_string_value(fixture.get('summary_id'))}",
        f"summary_kind: {_string_value(fixture.get('summary_kind'))}",
        f"contract_revision: {_string_value(fixture.get('contract_revision'))}",
        "",
        "source_report_refs:",
    ]
    for ref in fixture.get("source_report_refs", []):
        lines.append(
            "  - "
            + _join_fields(
                ref,
                ("ref_id", "day", "title", "path", "required"),
            )
        )

    status_rollup = fixture.get("status_rollup", {})
    lines.extend(
        [
            "",
            "status_rollup:",
            f"  overall_status: {_string_value(status_rollup.get('overall_status'))}",
            f"  pass_count: {_string_value(status_rollup.get('pass_count'))}",
            f"  warn_count: {_string_value(status_rollup.get('warn_count'))}",
            f"  fail_count: {_string_value(status_rollup.get('fail_count'))}",
            f"  blocked_count: {_string_value(status_rollup.get('blocked_count'))}",
            f"  locked_count: {_string_value(status_rollup.get('locked_count'))}",
            "",
            "reviewer_findings:",
        ]
    )
    for finding in fixture.get("reviewer_findings", []):
        lines.append(
            "  - "
            + _join_fields(
                finding,
                (
                    "finding_id",
                    "severity",
                    "status",
                    "title",
                    "evidence_ref_ids",
                    "requires_human_review",
                ),
            )
        )

    lines.append("")
    lines.append("evidence_refs:")
    for ref in fixture.get("evidence_refs", []):
        lines.append(
            "  - "
            + _join_fields(
                ref,
                ("ref_id", "kind", "path", "description"),
            )
        )

    lines.append("")
    lines.append("safety_boundary:")
    boundary = fixture.get("safety_boundary", {})
    for key in sorted(boundary):
        lines.append(f"  {key}: {_string_value(boundary[key])}")

    lines.append("")
    lines.append("non_goals:")
    for item in fixture.get("non_goals", []):
        lines.append(f"  - {_string_value(item)}")

    return "\n".join(lines) + "\n"


def build_ai_reviewer_summary_fixture_renderer_report(
    project_root: Path,
    agents_md_read_before_code_changes: bool = True,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        read_before_code_changes=agents_md_read_before_code_changes,
    )
    base_report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "scope": "Day128 fixture renderer only; consumes Day127 schema fixture without redefining schema.",
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_code_changes": agents_evidence["agents_md_read_before_code_changes"],
        "schema_source": (
            "intent_ai_reviewer_summary_schema_contract.SCHEMA_VERSION="
            f"{DAY127_SCHEMA_VERSION}"
        ),
        "fixture_source": DAY127_FIXTURE_PATH.as_posix(),
        "renderer_status": "PENDING",
        "ai_decision_performed": False,
        "prompt_contract_defined": False,
        "redaction_policy_defined": False,
        "openai_api_called": False,
        "execution_unlock_added": False,
        "provider_enabled": False,
        "api_enabled": False,
        "next_day_feature_included": False,
        "next_phase_allowed": False,
        "day128_only": True,
        "not_next_day_feature": True,
        "fixture_renderer_only": True,
        "report_only": True,
        "fixture_only": True,
        "non_executable": True,
        "reused_day127_schema_fixture": False,
        "redefined_schema": False,
        "schema_validation_status": "NOT_RUN",
        "fixture_summary": {},
        "rendered_text": "",
        "report_paths": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
            "text": REPORT_TXT.as_posix(),
        },
        "agents_md_evidence": agents_evidence,
        "validation_errors": [],
    }

    try:
        fixture = load_summary_fixture(project_root)
    except FileNotFoundError:
        blocked_report = dict(base_report)
        blocked_report["overall_status"] = BLOCKED_STATUS
        blocked_report["renderer_status"] = MISSING_FIXTURE_STATUS
        blocked_report["validation_errors"] = [MISSING_FIXTURE_STATUS]
        return blocked_report

    validation = validate_ai_reviewer_summary_contract(fixture)
    rendered_text = render_day127_summary_fixture(fixture)
    report = dict(base_report)
    report.update(
        {
            "renderer_status": RENDERER_STATUS,
            "reused_day127_schema_fixture": True,
            "schema_validation_status": validation["status"],
            "fixture_summary": {
                "schema_version": fixture.get("schema_version"),
                "summary_id": fixture.get("summary_id"),
                "summary_kind": fixture.get("summary_kind"),
                "source_report_ref_count": len(fixture.get("source_report_refs", [])),
                "reviewer_finding_count": len(fixture.get("reviewer_findings", [])),
                "evidence_ref_count": len(fixture.get("evidence_refs", [])),
            },
            "rendered_text": rendered_text,
        }
    )
    report["validation_errors"] = collect_validation_errors(report, validation)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    return report


def collect_validation_errors(
    report: Mapping[str, Any],
    fixture_validation: Mapping[str, Any],
) -> List[str]:
    errors = list(fixture_validation.get("errors", []))
    if report.get("agents_md_pre_read_result") != "FOUND_AND_READ":
        errors.append("AGENTS.md pre-read result must be FOUND_AND_READ.")
    if report.get("agents_md_read_before_code_changes") is not True:
        errors.append("AGENTS.md must be read before code changes.")
    if fixture_validation.get("schema_version") != DAY127_SCHEMA_VERSION:
        errors.append("Day128 renderer must consume the Day127 schema fixture.")
    if report.get("renderer_status") != RENDERER_STATUS:
        errors.append("Day128 fixture renderer did not render the Day127 fixture.")
    for field in (
        "ai_decision_performed",
        "prompt_contract_defined",
        "redaction_policy_defined",
        "openai_api_called",
        "execution_unlock_added",
        "provider_enabled",
        "api_enabled",
        "next_day_feature_included",
        "next_phase_allowed",
        "redefined_schema",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    for field in ("day128_only", "not_next_day_feature", "fixture_renderer_only", "report_only", "fixture_only", "non_executable", "reused_day127_schema_fixture"):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    return errors


def write_ai_reviewer_summary_fixture_renderer_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_reviewer_summary_fixture_renderer_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    text_path = Path(project_root) / REPORT_TXT
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    text_path.write_text(str(safe_report.get("rendered_text", "")), encoding="utf-8")
    write_ai_reviewer_summary_fixture_renderer_html(safe_report, html_path)
    return json_path, html_path, text_path


def write_ai_reviewer_summary_fixture_renderer_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (
            ("overall_status", report["overall_status"]),
            ("day", report["day"]),
            ("scope", report["scope"]),
            ("agents_md_pre_read_result", report["agents_md_pre_read_result"]),
            ("schema_source", report["schema_source"]),
            ("fixture_source", report["fixture_source"]),
            ("renderer_status", report["renderer_status"]),
        )
    )
    boundary_rows = _table_rows(
        (
            ("ai_decision_performed", report["ai_decision_performed"]),
            ("prompt_contract_defined", report["prompt_contract_defined"]),
            ("redaction_policy_defined", report["redaction_policy_defined"]),
            ("openai_api_called", report["openai_api_called"]),
            ("execution_unlock_added", report["execution_unlock_added"]),
            ("provider_enabled", report["provider_enabled"]),
            ("api_enabled", report["api_enabled"]),
            ("next_day_feature_included", report["next_day_feature_included"]),
            ("next_phase_allowed", report["next_phase_allowed"]),
        )
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
    pre {{ background: #f7f9fb; border: 1px solid #d5d8dc; padding: 1rem; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report['full_title']))}</h1>
  <h2>Renderer Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Locked Boundary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
  <h2>Rendered Fixture</h2>
  <pre>{html.escape(str(report.get('rendered_text', '')))}</pre>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_reviewer_summary_fixture_renderer(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_reviewer_summary_fixture_renderer_report(project_root)
    json_path, html_path, text_path = write_ai_reviewer_summary_fixture_renderer_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: fixture renderer only; no AI decision, prompt contract, redaction policy, OpenAI API, provider, API enablement, execution unlock, SSH, live device access, mapped execution, or next phase")
    for field in (
        "overall_status",
        "day",
        "scope",
        "agents_md_pre_read_result",
        "agents_md_read_before_code_changes",
        "schema_source",
        "fixture_source",
        "renderer_status",
        "ai_decision_performed",
        "prompt_contract_defined",
        "redaction_policy_defined",
        "openai_api_called",
        "execution_unlock_added",
        "provider_enabled",
        "api_enabled",
        "next_day_feature_included",
        "next_phase_allowed",
    ):
        print(f"{field}: {json.dumps(report[field])}")
    print(f"reused_day127_schema_fixture: {json.dumps(report['reused_day127_schema_fixture'])}")
    print(f"redefined_schema: {json.dumps(report['redefined_schema'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")
    print(f"Text report: {relative_to_project(project_root, text_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {RENDERER_STATUS}")
        return 0

    print(f"{format_status(report['overall_status'])} {report['renderer_status']}")
    return 1


def _join_fields(row: Any, fields: Iterable[str]) -> str:
    if not isinstance(row, Mapping):
        return _string_value(row)
    return "; ".join(f"{field}={_string_value(row.get(field))}" for field in fields)


def _string_value(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return json.dumps(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_string_value(item) for item in value) + "]"
    return str(value)


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def main() -> int:
    report = build_ai_reviewer_summary_fixture_renderer_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
