"""Day127 AI reviewer summary schema contract integration.

This module is deterministic and report-only. It defines the data shape that a
future AI reviewer summary may consume, validates an example fixture, and keeps
renderer, prompt text, and redaction policy work explicitly out of scope.
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


DAY = 127
DAY_LABEL = "Day127"
TASK_NAME = "ai-reviewer-summary-schema-contract"
TITLE = "AI Reviewer Summary Schema Contract Integration"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
SCHEMA_VERSION = "day127.ai_reviewer_summary_schema_contract.v1"
CREATED_AT = "2026-06-14T00:00:00+08:00"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
CONTRACT_STATUS = "SCHEMA_CONTRACT_READY"
FINAL_RECOMMENDATION = "KEEP_SCHEMA_CONTRACT_REVIEW_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day127_ai_reviewer_summary_schema_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day127_ai_reviewer_summary_schema_contract.html"
FIXTURE_PATH = Path("fixtures") / "day127_ai_reviewer_summary.example.json"

SUMMARY_STATUSES: Tuple[str, ...] = ("PASS", "WARN", "FAIL", "BLOCKED", "REVIEW_ONLY", "LOCKED")
FINDING_SEVERITIES: Tuple[str, ...] = ("INFO", "LOW", "MEDIUM", "HIGH", "BLOCKING")
REQUIRED_SUMMARY_FIELDS: Tuple[str, ...] = (
    "schema_version",
    "summary_id",
    "summary_kind",
    "contract_revision",
    "source_report_refs",
    "status_rollup",
    "reviewer_findings",
    "evidence_refs",
    "safety_boundary",
    "non_goals",
)
REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "overall_status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day127_work",
    "schema_contract_status",
    "fixture_validation_status",
    "renderer_implemented",
    "prompt_text_contract_implemented",
    "redaction_policy_implemented",
    "execution_unlock_added",
    "reviewer_only",
)
FORBIDDEN_FUTURE_SCOPE_FIELDS: Tuple[str, ...] = (
    "renderer_template",
    "rendered_html",
    "prompt_text",
    "system_prompt",
    "user_prompt",
    "redaction_rules",
    "redaction_policy",
    "secret_patterns",
    "execution_unlock",
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day127_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day127_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    passed = bool(agents_md_read_before_day127_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if passed else FAIL_STATUS,
        "agents_md_read_before_day127_work": passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def build_example_ai_reviewer_summary_fixture() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "summary_id": "day127-example-ai-reviewer-summary",
        "summary_kind": "AI_REVIEWER_SUMMARY_CONTRACT_FIXTURE",
        "contract_revision": 1,
        "source_report_refs": [
            {
                "ref_id": "day126-compatibility-pack",
                "day": "Day126",
                "title": "Post-Refactor Compatibility Evidence Pack",
                "path": "reports/lab-summary/day126_post_refactor_compatibility_evidence_pack.json",
                "required": True,
            }
        ],
        "status_rollup": {
            "overall_status": "REVIEW_ONLY",
            "pass_count": 1,
            "warn_count": 0,
            "fail_count": 0,
            "blocked_count": 0,
            "locked_count": 1,
        },
        "reviewer_findings": [
            {
                "finding_id": "DAY127-SCHEMA-001",
                "severity": "INFO",
                "status": "REVIEW_ONLY",
                "title": "AI reviewer summary data contract is available for review.",
                "evidence_ref_ids": ["day127-schema-contract"],
                "requires_human_review": True,
            }
        ],
        "evidence_refs": [
            {
                "ref_id": "day127-schema-contract",
                "kind": "schema_contract",
                "path": "docs/ai-intent/day127_ai_reviewer_summary_schema_contract.md",
                "description": "Reviewer-facing schema contract evidence.",
            }
        ],
        "safety_boundary": {
            "renderer_implemented": False,
            "prompt_text_contract_implemented": False,
            "redaction_policy_implemented": False,
            "openai_api_allowed": False,
            "voice_runtime_allowed": False,
            "ssh_allowed": False,
            "live_device_allowed": False,
            "live_command_allowed": False,
            "mapped_task_execution_allowed": False,
            "dashboard_action_endpoint_allowed": False,
            "execution_unlock_added": False,
            "next_phase_allowed": False,
        },
        "non_goals": [
            "Day128 renderer is not implemented.",
            "Day129 prompt text contract is not implemented.",
            "Day130 redaction policy is not implemented.",
            "No execution unlock is added.",
        ],
    }


def load_summary_fixture(project_root: Path) -> Dict[str, Any]:
    fixture_path = Path(project_root) / FIXTURE_PATH
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def validate_ai_reviewer_summary_contract(summary: Mapping[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    for field in REQUIRED_SUMMARY_FIELDS:
        if field not in summary:
            errors.append(f"{field} is missing.")

    if summary.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if summary.get("summary_kind") != "AI_REVIEWER_SUMMARY_CONTRACT_FIXTURE":
        errors.append("summary_kind must be AI_REVIEWER_SUMMARY_CONTRACT_FIXTURE.")
    if summary.get("contract_revision") != 1:
        errors.append("contract_revision must be 1.")

    source_report_refs = summary.get("source_report_refs")
    if not isinstance(source_report_refs, list) or not source_report_refs:
        errors.append("source_report_refs must be a non-empty list.")
    else:
        for index, ref in enumerate(source_report_refs, start=1):
            if not isinstance(ref, Mapping):
                errors.append(f"source_report_refs[{index}] must be an object.")
                continue
            for field in ("ref_id", "day", "title", "path", "required"):
                if field not in ref:
                    errors.append(f"source_report_refs[{index}].{field} is missing.")
            if ref.get("required") is not True:
                errors.append(f"source_report_refs[{index}].required must be true.")

    status_rollup = summary.get("status_rollup")
    if not isinstance(status_rollup, Mapping):
        errors.append("status_rollup must be an object.")
    else:
        if status_rollup.get("overall_status") not in SUMMARY_STATUSES:
            errors.append("status_rollup.overall_status is not an allowed reviewer status.")
        for field in ("pass_count", "warn_count", "fail_count", "blocked_count", "locked_count"):
            if not isinstance(status_rollup.get(field), int) or status_rollup.get(field, -1) < 0:
                errors.append(f"status_rollup.{field} must be a non-negative integer.")

    findings = summary.get("reviewer_findings")
    if not isinstance(findings, list) or not findings:
        errors.append("reviewer_findings must be a non-empty list.")
    else:
        evidence_ids = {
            ref.get("ref_id")
            for ref in summary.get("evidence_refs", [])
            if isinstance(ref, Mapping)
        }
        for index, finding in enumerate(findings, start=1):
            if not isinstance(finding, Mapping):
                errors.append(f"reviewer_findings[{index}] must be an object.")
                continue
            for field in ("finding_id", "severity", "status", "title", "evidence_ref_ids", "requires_human_review"):
                if field not in finding:
                    errors.append(f"reviewer_findings[{index}].{field} is missing.")
            if finding.get("severity") not in FINDING_SEVERITIES:
                errors.append(f"reviewer_findings[{index}].severity is not allowed.")
            if finding.get("status") not in SUMMARY_STATUSES:
                errors.append(f"reviewer_findings[{index}].status is not allowed.")
            if finding.get("requires_human_review") is not True:
                errors.append(f"reviewer_findings[{index}].requires_human_review must be true.")
            for evidence_id in finding.get("evidence_ref_ids", []):
                if evidence_id not in evidence_ids:
                    errors.append(f"reviewer_findings[{index}] references unknown evidence ref {evidence_id}.")

    evidence_refs = summary.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        errors.append("evidence_refs must be a non-empty list.")
    else:
        for index, ref in enumerate(evidence_refs, start=1):
            if not isinstance(ref, Mapping):
                errors.append(f"evidence_refs[{index}] must be an object.")
                continue
            for field in ("ref_id", "kind", "path", "description"):
                if field not in ref:
                    errors.append(f"evidence_refs[{index}].{field} is missing.")

    boundary = summary.get("safety_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("safety_boundary must be an object.")
    else:
        for field in (
            "renderer_implemented",
            "prompt_text_contract_implemented",
            "redaction_policy_implemented",
            "openai_api_allowed",
            "voice_runtime_allowed",
            "ssh_allowed",
            "live_device_allowed",
            "live_command_allowed",
            "mapped_task_execution_allowed",
            "dashboard_action_endpoint_allowed",
            "execution_unlock_added",
            "next_phase_allowed",
        ):
            if boundary.get(field) is not False:
                errors.append(f"safety_boundary.{field} must be false.")

    forbidden_present = sorted(field for field in FORBIDDEN_FUTURE_SCOPE_FIELDS if field in summary)
    if forbidden_present:
        errors.append("Forbidden future-scope fields are present: " + ", ".join(forbidden_present))

    return {
        "status": OVERALL_STATUS if not errors else FAIL_STATUS,
        "schema_version": summary.get("schema_version"),
        "required_field_count": len(REQUIRED_SUMMARY_FIELDS),
        "forbidden_future_scope_fields": forbidden_present,
        "errors": errors,
        "warnings": warnings,
    }


def build_ai_reviewer_summary_schema_contract_report(
    project_root: Path,
    agents_md_read_before_day127_work: bool = True,
    fixture: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day127_work=agents_md_read_before_day127_work,
    )
    summary_fixture = dict(fixture or build_example_ai_reviewer_summary_fixture())
    fixture_validation = validate_ai_reviewer_summary_contract(summary_fixture)
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
        "agents_md_read_before_day127_work": agents_evidence["agents_md_read_before_day127_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "schema_contract_status": CONTRACT_STATUS,
        "summary_contract_required_fields": list(REQUIRED_SUMMARY_FIELDS),
        "summary_contract_allowed_statuses": list(SUMMARY_STATUSES),
        "summary_contract_allowed_severities": list(FINDING_SEVERITIES),
        "example_fixture_path": FIXTURE_PATH.as_posix(),
        "example_fixture": summary_fixture,
        "fixture_validation_status": fixture_validation["status"],
        "fixture_validation": fixture_validation,
        "renderer_implemented": False,
        "day128_renderer_implemented": False,
        "prompt_text_contract_implemented": False,
        "day129_prompt_contract_implemented": False,
        "redaction_policy_implemented": False,
        "day130_redaction_policy_implemented": False,
        "live_execution_introduced": False,
        "ssh_introduced": False,
        "device_connection_introduced": False,
        "configuration_change_introduced": False,
        "openai_or_voice_runtime_introduced": False,
        "mapped_task_execution_introduced": False,
        "dashboard_action_endpoint_introduced": False,
        "execution_unlock_added": False,
        "next_phase_allowed": False,
        "reviewer_only": True,
        "report_only": True,
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
        report["schema_contract_status"] = "SCHEMA_CONTRACT_BLOCKED"
    return report


def collect_validation_errors(report: Mapping[str, Any], helper_errors: Iterable[str] = ()) -> List[str]:
    errors = list(helper_errors)
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day127_work") is not True:
        errors.append("AGENTS.md read-before-Day127-work evidence is not true.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    if report.get("fixture_validation_status") != OVERALL_STATUS:
        errors.extend(report.get("fixture_validation", {}).get("errors", []))
    for flag in (
        "renderer_implemented",
        "day128_renderer_implemented",
        "prompt_text_contract_implemented",
        "day129_prompt_contract_implemented",
        "redaction_policy_implemented",
        "day130_redaction_policy_implemented",
        "live_execution_introduced",
        "ssh_introduced",
        "device_connection_introduced",
        "configuration_change_introduced",
        "openai_or_voice_runtime_introduced",
        "mapped_task_execution_introduced",
        "dashboard_action_endpoint_introduced",
        "execution_unlock_added",
        "next_phase_allowed",
    ):
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")
    if report.get("reviewer_only") is not True or report.get("report_only") is not True:
        errors.append("Day127 must remain reviewer-only and report-only.")
    return errors


def write_ai_reviewer_summary_schema_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_reviewer_summary_schema_contract_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_reviewer_summary_schema_contract_html(safe_report, html_path)
    return json_path, html_path


def write_ai_reviewer_summary_schema_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    contract_rows = _table_rows(
        (
            ("schema_version", report["schema_version"]),
            ("schema_contract_status", report["schema_contract_status"]),
            ("fixture_validation_status", report["fixture_validation_status"]),
            ("example_fixture_path", report["example_fixture_path"]),
            ("required_field_count", len(report["summary_contract_required_fields"])),
        )
    )
    boundary_rows = _table_rows(
        (
            ("renderer_implemented", report["renderer_implemented"]),
            ("prompt_text_contract_implemented", report["prompt_text_contract_implemented"]),
            ("redaction_policy_implemented", report["redaction_policy_implemented"]),
            ("openai_or_voice_runtime_introduced", report["openai_or_voice_runtime_introduced"]),
            ("mapped_task_execution_introduced", report["mapped_task_execution_introduced"]),
            ("execution_unlock_added", report["execution_unlock_added"]),
            ("next_phase_allowed", report["next_phase_allowed"]),
        )
    )
    field_rows = _table_rows((field,) for field in report["summary_contract_required_fields"])
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
    .pass {{ color: #116329; font-weight: bold; }}
    .fail {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['full_title'])}</h1>
  <p><strong>Overall status:</strong> <span class="{html.escape(str(report['overall_status']).lower())}">{html.escape(report['overall_status'])}</span></p>
  <p><strong>AGENTS.md pre-read:</strong> <code>{html.escape(report['agents_md_pre_read_result'])}</code>, read before work: <code>{html.escape(json.dumps(report['agents_md_read_before_day127_work']))}</code></p>
  <p><strong>Scope:</strong> schema, validation, example fixture, CLI task, tests, and documentation evidence only.</p>

  <h2>Contract Evidence</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{contract_rows}</tbody></table>

  <h2>Required Summary Fields</h2>
  <table><thead><tr><th>Field</th></tr></thead><tbody>{field_rows}</tbody></table>

  <h2>Out-of-Scope Guardrails</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_reviewer_summary_schema_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_reviewer_summary_schema_contract_report(project_root)
    json_path, html_path = write_ai_reviewer_summary_schema_contract_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: schema/report-only; no renderer, prompt text contract, redaction policy, live execution, SSH, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or execution unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"schema_version: {json.dumps(report['schema_version'])}")
    print(f"example_fixture_path: {json.dumps(report['example_fixture_path'])}")
    print(f"required_summary_field_count: {len(report['summary_contract_required_fields'])}")
    print(f"day128_renderer_implemented: {json.dumps(report['day128_renderer_implemented'])}")
    print(f"day129_prompt_contract_implemented: {json.dumps(report['day129_prompt_contract_implemented'])}")
    print(f"day130_redaction_policy_implemented: {json.dumps(report['day130_redaction_policy_implemented'])}")
    print(f"live_execution_introduced: {json.dumps(report['live_execution_introduced'])}")
    print(f"ssh_introduced: {json.dumps(report['ssh_introduced'])}")
    print(f"openai_or_voice_runtime_introduced: {json.dumps(report['openai_or_voice_runtime_introduced'])}")
    print(f"mapped_task_execution_introduced: {json.dumps(report['mapped_task_execution_introduced'])}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {CONTRACT_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} Day127 schema contract failed.")
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
    report = build_ai_reviewer_summary_schema_contract_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
