"""Day131 AI summary audit trail binding.

This module binds Day127-Day130 AI summary artifacts into deterministic
reviewer-facing audit records. It is review-only and non-advancing: it does not
call providers, APIs, models, network paths, SSH, brokers, runners, adapters,
or any execution path.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from intent_ai_reviewer_summary_fixture_renderer import (
    RENDERER_STATUS as DAY128_RENDERER_STATUS,
    TASK_NAME as DAY128_TASK_NAME,
    render_day127_summary_fixture,
)
from intent_ai_reviewer_summary_schema_contract import (
    FIXTURE_PATH as DAY127_FIXTURE_PATH,
    SCHEMA_VERSION as DAY127_SCHEMA_VERSION,
    TASK_NAME as DAY127_TASK_NAME,
    load_summary_fixture,
    validate_ai_reviewer_summary_contract,
)
from intent_ai_summary_prompt_contract import (
    ALLOWED_PROMPT as DAY129_ALLOWED_PROMPT,
    CONTRACT_SCOPE as DAY129_CONTRACT_SCOPE,
    CONTRACT_STATUS as DAY129_CONTRACT_STATUS,
    TASK_NAME as DAY129_TASK_NAME,
    validate_prompt_contract,
)
from intent_ai_summary_redaction_policy import (
    FIXTURE_PATH as DAY130_FIXTURE_PATH,
    POLICY_STATUS as DAY130_POLICY_STATUS,
    REDACTION_STATUS as DAY130_REDACTION_STATUS,
    TASK_NAME as DAY130_TASK_NAME,
    build_ai_summary_redaction_policy_report,
)


DAY = "Day131"
DAY_NUMBER = 131
TASK_NAME = "ai-summary-audit-trail-binding"
TITLE = "AI Summary Audit Trail Binding"
FULL_TITLE = f"{DAY} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
AUDIT_STATUS = "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day131_ai_summary_audit_trail_binding.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day131_ai_summary_audit_trail_binding.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day131_ai_summary_audit_trail_binding.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day131_ai_summary_audit_trail_binding.md"

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "day",
    "task",
    "audit_status",
    "review_only",
    "non_advancing",
    "deterministic_only",
    "provider_api_enabled",
    "ai_execution_enabled",
    "ai_decision_enabled",
    "next_phase_allowed",
    "reviewer_approval_enabled",
    "mock_provider_enabled",
    "live_execution_enabled",
    "ssh_invocation_enabled",
    "device_invocation_enabled",
    "broker_invocation_enabled",
    "runner_invocation_enabled",
    "adapter_invocation_enabled",
    "schema_reference",
    "prompt_contract_reference",
    "redaction_no_secret_policy_reference",
    "audit_record_count",
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day131_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_pre_read_result": "MISSING",
            "agents_md_read_before_day131_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": "AGENTS.md not found.",
            "agents_md_required_phrase_present": False,
        }
    except OSError as exc:
        return {
            "agents_md_pre_read_result": "READ_ERROR",
            "agents_md_read_before_day131_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    passed = bool(agents_md_read_before_day131_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if passed else FAIL_STATUS,
        "agents_md_read_before_day131_work": passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
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
        "next_phase_allowed": False,
        "reviewer_approval_enabled": False,
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


def build_audit_record(
    summary_fixture: Mapping[str, Any],
    rendered_fixture_text: str,
    redaction_report: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "audit_record_id": "day131-ai-summary-audit-binding-record-001",
        "summary_artifact_identity": {
            "summary_id": summary_fixture.get("summary_id", ""),
            "summary_kind": summary_fixture.get("summary_kind", ""),
            "contract_revision": summary_fixture.get("contract_revision", ""),
            "schema_version": summary_fixture.get("schema_version", ""),
        },
        "schema_reference": {
            "task": DAY127_TASK_NAME,
            "schema_version": DAY127_SCHEMA_VERSION,
            "fixture_path": DAY127_FIXTURE_PATH.as_posix(),
        },
        "fixture_renderer_reference": {
            "task": DAY128_TASK_NAME,
            "renderer_status": DAY128_RENDERER_STATUS,
            "rendered_fixture_line_count": len(rendered_fixture_text.splitlines()),
        },
        "prompt_contract_reference": {
            "task": DAY129_TASK_NAME,
            "contract_scope": DAY129_CONTRACT_SCOPE,
            "contract_status": DAY129_CONTRACT_STATUS,
        },
        "redaction_no_secret_policy_reference": {
            "task": DAY130_TASK_NAME,
            "policy_status": DAY130_POLICY_STATUS,
            "redaction_status": DAY130_REDACTION_STATUS,
            "fixture_path": DAY130_FIXTURE_PATH.as_posix(),
            "source_text_omitted_from_audit": True,
            "redacted_fixture_count": redaction_report.get("redacted_count", 0),
            "blocked_secret_like_count": redaction_report.get("blocked_secret_like_count", 0),
        },
        "fixture_or_source_record_reference": {
            "primary_fixture_ref": DAY127_FIXTURE_PATH.as_posix(),
            "source_report_refs": list(summary_fixture.get("source_report_refs", [])),
            "evidence_refs": list(summary_fixture.get("evidence_refs", [])),
        },
        "reviewer_visible_audit_status": AUDIT_STATUS,
        "non_execution_safety_flags": build_non_execution_safety_flags(),
        "no_execution_evidence": {
            "provider_api_path_opened": False,
            "ai_decision_path_opened": False,
            "ai_execution_path_opened": False,
            "live_execution_path_opened": False,
            "ssh_device_path_opened": False,
            "broker_runner_adapter_path_opened": False,
            "next_phase_unlock_opened": False,
        },
    }


def build_ai_summary_audit_trail_binding_report(
    project_root: Path,
    agents_md_read_before_day131_work: bool = True,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day131_work=agents_md_read_before_day131_work,
    )
    summary_fixture = load_summary_fixture(project_root)
    schema_validation = validate_ai_reviewer_summary_contract(summary_fixture)
    rendered_fixture_text = render_day127_summary_fixture(summary_fixture)
    prompt_validation = validate_prompt_contract(DAY129_ALLOWED_PROMPT)
    redaction_report = build_ai_summary_redaction_policy_report(project_root)
    safety_flags = build_non_execution_safety_flags()
    audit_record = build_audit_record(summary_fixture, rendered_fixture_text, redaction_report)

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "audit_status": AUDIT_STATUS,
        "review_only": True,
        "non_advancing": True,
        "deterministic_only": True,
        "report_only": True,
        "local_only": True,
        "not_day132_reviewer_approval_gate": True,
        "not_day133_mock_provider_boundary": True,
        "not_provider_api_integration": True,
        "not_ai_execution": True,
        "not_ai_decision_making": True,
        "not_next_phase_unlock": True,
        "provider_api_enabled": safety_flags["provider_api_enabled"],
        "ai_execution_enabled": safety_flags["ai_execution_enabled"],
        "ai_decision_enabled": safety_flags["ai_decision_enabled"],
        "next_phase_allowed": safety_flags["next_phase_allowed"],
        "reviewer_approval_enabled": safety_flags["reviewer_approval_enabled"],
        "mock_provider_enabled": safety_flags["mock_provider_enabled"],
        "live_execution_enabled": safety_flags["live_execution_enabled"],
        "ssh_invocation_enabled": safety_flags["ssh_invocation_enabled"],
        "device_invocation_enabled": safety_flags["device_invocation_enabled"],
        "broker_invocation_enabled": safety_flags["broker_invocation_enabled"],
        "runner_invocation_enabled": safety_flags["runner_invocation_enabled"],
        "adapter_invocation_enabled": safety_flags["adapter_invocation_enabled"],
        "openai_api_called": safety_flags["openai_api_called"],
        "network_access_enabled": safety_flags["network_access_enabled"],
        "schema_reference": audit_record["schema_reference"],
        "prompt_contract_reference": audit_record["prompt_contract_reference"],
        "redaction_no_secret_policy_reference": audit_record["redaction_no_secret_policy_reference"],
        "fixture_renderer_reference": audit_record["fixture_renderer_reference"],
        "fixture_or_source_record_reference": audit_record["fixture_or_source_record_reference"],
        "input_artifacts": [
            {"day": "Day127", "task": DAY127_TASK_NAME, "status": schema_validation["status"]},
            {"day": "Day128", "task": DAY128_TASK_NAME, "status": DAY128_RENDERER_STATUS},
            {"day": "Day129", "task": DAY129_TASK_NAME, "status": prompt_validation["status"]},
            {"day": "Day130", "task": DAY130_TASK_NAME, "status": redaction_report["overall_status"]},
        ],
        "audit_record_count": 1,
        "audit_records": [audit_record],
        "safety_flags": safety_flags,
        "schema_validation_status": schema_validation["status"],
        "prompt_validation_status": prompt_validation["status"],
        "redaction_policy_status": redaction_report["policy_status"],
        "redaction_report_status": redaction_report["overall_status"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_day131_work": agents_evidence["agents_md_read_before_day131_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "agents_md_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    if report["overall_status"] != OVERALL_STATUS:
        report["audit_status"] = "AI_SUMMARY_AUDIT_TRAIL_BINDING_BLOCKED"
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day131_work") is not True:
        errors.append("AGENTS.md must be read before Day131 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    for field in (
        "review_only",
        "non_advancing",
        "deterministic_only",
        "report_only",
        "local_only",
        "not_day132_reviewer_approval_gate",
        "not_day133_mock_provider_boundary",
        "not_provider_api_integration",
        "not_ai_execution",
        "not_ai_decision_making",
        "not_next_phase_unlock",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in (
        "provider_api_enabled",
        "ai_execution_enabled",
        "ai_decision_enabled",
        "next_phase_allowed",
        "reviewer_approval_enabled",
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
    if report.get("audit_status") != AUDIT_STATUS:
        errors.append(f"audit_status must be {AUDIT_STATUS}.")
    if report.get("audit_record_count") != 1:
        errors.append("audit_record_count must be 1.")
    if not report.get("schema_reference"):
        errors.append("schema_reference is required.")
    if not report.get("prompt_contract_reference"):
        errors.append("prompt_contract_reference is required.")
    if not report.get("redaction_no_secret_policy_reference"):
        errors.append("redaction_no_secret_policy_reference is required.")
    if report.get("schema_validation_status") != OVERALL_STATUS:
        errors.append("Day127 schema validation must pass.")
    if report.get("prompt_validation_status") != OVERALL_STATUS:
        errors.append("Day129 prompt validation must pass.")
    if report.get("redaction_report_status") != OVERALL_STATUS:
        errors.append("Day130 redaction report must pass.")

    for record in report.get("audit_records", []):
        flags = record.get("non_execution_safety_flags", {})
        for flag_name, flag_value in flags.items():
            if flag_value is not False:
                errors.append(f"audit record safety flag {flag_name} must be false.")
        evidence = record.get("no_execution_evidence", {})
        for evidence_name, evidence_value in evidence.items():
            if evidence_value is not False:
                errors.append(f"audit record evidence {evidence_name} must be false.")

    return errors


def write_ai_summary_audit_trail_binding_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_summary_audit_trail_binding_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_summary_audit_trail_binding_html(safe_report, html_path)
    return json_path, html_path


def write_ai_summary_audit_trail_binding_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    input_rows = _table_rows(
        (
            item.get("day", ""),
            item.get("task", ""),
            item.get("status", ""),
        )
        for item in report.get("input_artifacts", [])
    )
    flag_rows = _table_rows((key, value) for key, value in report.get("safety_flags", {}).items())
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
  <h2>Audit Binding Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Input Artifacts</h2>
  <table><thead><tr><th>Day</th><th>Task</th><th>Status</th></tr></thead><tbody>{input_rows}</tbody></table>
  <h2>Non-Execution Safety Flags</h2>
  <table><thead><tr><th>Flag</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_summary_audit_trail_binding(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_summary_audit_trail_binding_report(project_root)
    json_path, html_path = write_ai_summary_audit_trail_binding_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: review-only audit binding; no provider/API, AI execution, AI decision, reviewer approval gate, mock provider boundary, live execution, SSH/device/broker/runner/adapter invocation, or next-phase unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"not_day132_reviewer_approval_gate: {json.dumps(report['not_day132_reviewer_approval_gate'])}")
    print(f"not_day133_mock_provider_boundary: {json.dumps(report['not_day133_mock_provider_boundary'])}")
    print(f"not_provider_api_integration: {json.dumps(report['not_provider_api_integration'])}")
    print(f"not_ai_execution: {json.dumps(report['not_ai_execution'])}")
    print(f"not_ai_decision_making: {json.dumps(report['not_ai_decision_making'])}")
    print(f"not_next_phase_unlock: {json.dumps(report['not_next_phase_unlock'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {AUDIT_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {report['audit_status']}")
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
    report = build_ai_summary_audit_trail_binding_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
