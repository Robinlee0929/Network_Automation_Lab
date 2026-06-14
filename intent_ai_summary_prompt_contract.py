"""Day129 AI summary prompt contract for reviewer text only.

This module is deterministic and report-only. It defines and validates the
limited wording a future AI reviewer-summary prompt may use. It does not call
OpenAI, configure a provider, execute tools, make approval decisions, redact
secrets, bind audit trails, or unlock any next phase.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from intent_ai_reviewer_summary_fixture_renderer import (
    RENDERER_STATUS as DAY128_RENDERER_STATUS,
    TASK_NAME as DAY128_TASK_NAME,
)
from intent_ai_reviewer_summary_schema_contract import (
    SCHEMA_VERSION as DAY127_SCHEMA_VERSION,
    TASK_NAME as DAY127_TASK_NAME,
)


DAY = 129
DAY_LABEL = "Day129"
TASK_NAME = "ai-summary-prompt-contract"
TITLE = "AI Summary Prompt Contract for Reviewer Text Only"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
CONTRACT_STATUS = "PROMPT_CONTRACT_READY"
CONTRACT_SCOPE = "REVIEWER_TEXT_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day129_ai_summary_prompt_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day129_ai_summary_prompt_contract.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day129_ai_summary_prompt_contract.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day129_ai_summary_prompt_contract.md"

ALLOWED_PROMPT = "\n".join(
    (
        "Produce a concise reviewer summary from the provided structured summary evidence.",
        "Use only the provided evidence.",
        "Do not make approval decisions.",
        "Do not infer pass/fail.",
        "Do not request execution.",
        "Do not request tools.",
        "Do not request API/provider access.",
        "Do not unlock any next phase.",
        "Return reviewer text only.",
    )
)

REQUIRED_ALLOWED_PHRASES: Tuple[str, ...] = (
    "produce a concise reviewer summary",
    "provided structured summary evidence",
    "use only the provided evidence",
    "do not make approval decisions",
    "do not infer pass/fail",
    "do not request execution",
    "do not request tools",
    "do not request api/provider access",
    "do not unlock any next phase",
    "return reviewer text only",
)

FORBIDDEN_PROMPT_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("execution", r"\b(execute|execution|run\s+commands?|shell|subprocess)\b"),
    ("commands", r"\b(commands?|cli command|terminal command|powershell|bash)\b"),
    ("tool calls", r"\b(tool[- ]?calls?|call tools?|use tools?)\b"),
    ("provider/API setup", r"\b(provider setup|configure provider|api setup|sdk setup)\b"),
    ("OpenAI API call", r"\b(openai api|api call|call the api|model provider)\b"),
    ("live integration", r"\b(live integration|live device|ssh|routeros|network calls?)\b"),
    ("approval decision", r"\b(approve|approval decision|approved|reject|rejected)\b"),
    ("pass/fail decision", r"\b(pass/fail decision|decide pass|decide fail|mark pass|mark fail)\b"),
    ("next phase unlock", r"\b(next phase unlock|unlock next phase|allow next phase|advance phase)\b"),
    ("redaction or secrets masking", r"\b(redact|redaction|mask secrets?|secrets? masking|secret policy)\b"),
    ("audit trail binding", r"\b(audit trail|bind audit|binding audit|audit binding)\b"),
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "reviewer_status",
    "day",
    "task",
    "agents_md_pre_read_result",
    "agents_md_read_before_day129_work",
    "contract_scope",
    "reviewer_text_only",
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "tool_calling_enabled",
    "ai_decision_enabled",
    "next_phase_allowed",
    "redaction_policy_enabled",
    "audit_trail_binding_enabled",
    "contract_fixture_count",
    "violations",
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day129_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_pre_read_result": "MISSING",
            "agents_md_read_before_day129_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": "AGENTS.md not found.",
            "agents_md_required_phrase_present": False,
        }
    except OSError as exc:
        return {
            "agents_md_pre_read_result": "READ_ERROR",
            "agents_md_read_before_day129_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    passed = bool(agents_md_read_before_day129_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if passed else FAIL_STATUS,
        "agents_md_read_before_day129_work": passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def build_prompt_contract_fixture() -> Dict[str, Any]:
    return {
        "fixture_id": "day129-reviewer-text-only-prompt-contract",
        "contract_scope": CONTRACT_SCOPE,
        "prompt_text": ALLOWED_PROMPT,
        "source_context": {
            "day127_schema_task": DAY127_TASK_NAME,
            "day127_schema_version": DAY127_SCHEMA_VERSION,
            "day128_renderer_task": DAY128_TASK_NAME,
            "day128_renderer_status": DAY128_RENDERER_STATUS,
        },
        "allowed_output": "reviewer summary text only",
        "must_not_request": [
            "execution",
            "provider/API access",
            "tool calls",
            "secrets",
            "redaction",
            "audit trail binding",
            "AI approval",
            "pass/fail decision",
            "next phase unlock",
        ],
    }


def validate_prompt_contract(prompt_text: str) -> Dict[str, Any]:
    normalized = _normalize_prompt(prompt_text)
    forbidden_scan_text = normalized
    violations: List[str] = []

    for phrase in REQUIRED_ALLOWED_PHRASES:
        if phrase not in normalized:
            violations.append(f"Missing required prompt boundary: {phrase}")
        forbidden_scan_text = forbidden_scan_text.replace(phrase, "")

    for label, pattern in FORBIDDEN_PROMPT_PATTERNS:
        if re.search(pattern, forbidden_scan_text):
            violations.append(f"Forbidden prompt request detected: {label}")

    if "reviewer text only" not in normalized:
        violations.append("Prompt must return reviewer text only.")

    return {
        "status": OVERALL_STATUS if not violations else FAIL_STATUS,
        "contract_scope": CONTRACT_SCOPE,
        "reviewer_text_only": "reviewer text only" in normalized,
        "violations": violations,
    }


def build_ai_summary_prompt_contract_report(
    project_root: Path,
    agents_md_read_before_day129_work: bool = True,
    contract_fixture: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day129_work=agents_md_read_before_day129_work,
    )
    fixture = dict(contract_fixture or build_prompt_contract_fixture())
    validation = validate_prompt_contract(str(fixture.get("prompt_text", "")))

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "reviewer_status": CONTRACT_STATUS,
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_day129_work": agents_evidence["agents_md_read_before_day129_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "contract_scope": CONTRACT_SCOPE,
        "reviewer_text_only": True,
        "provider_enabled": False,
        "api_enabled": False,
        "execution_enabled": False,
        "tool_calling_enabled": False,
        "ai_decision_enabled": False,
        "next_phase_allowed": False,
        "redaction_policy_enabled": False,
        "audit_trail_binding_enabled": False,
        "openai_api_called": False,
        "provider_configuration_added": False,
        "tool_calling_behavior_added": False,
        "live_integration_added": False,
        "secrets_requested": False,
        "pass_fail_decision_enabled": False,
        "approval_decision_enabled": False,
        "day129_only": True,
        "not_day130_redaction_policy": True,
        "not_day131_audit_trail_binding": True,
        "not_day132_reviewer_approval_gate": True,
        "not_day133_mock_provider_boundary": True,
        "day127_schema_reference": DAY127_SCHEMA_VERSION,
        "day128_renderer_reference": DAY128_RENDERER_STATUS,
        "contract_fixture_count": 1,
        "contract_fixture": fixture,
        "contract_validation": validation,
        "violations": list(validation["violations"]),
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "agents_md_evidence": agents_evidence,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    if report["overall_status"] != OVERALL_STATUS:
        report["reviewer_status"] = "PROMPT_CONTRACT_BLOCKED"
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day129_work") is not True:
        errors.append("AGENTS.md must be read before Day129 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    if report.get("contract_scope") != CONTRACT_SCOPE:
        errors.append(f"contract_scope must be {CONTRACT_SCOPE}.")
    for field in (
        "reviewer_text_only",
        "day129_only",
        "not_day130_redaction_policy",
        "not_day131_audit_trail_binding",
        "not_day132_reviewer_approval_gate",
        "not_day133_mock_provider_boundary",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in (
        "provider_enabled",
        "api_enabled",
        "execution_enabled",
        "tool_calling_enabled",
        "ai_decision_enabled",
        "next_phase_allowed",
        "redaction_policy_enabled",
        "audit_trail_binding_enabled",
        "openai_api_called",
        "provider_configuration_added",
        "tool_calling_behavior_added",
        "live_integration_added",
        "secrets_requested",
        "pass_fail_decision_enabled",
        "approval_decision_enabled",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if report.get("contract_fixture_count") != 1:
        errors.append("contract_fixture_count must be 1.")
    if report.get("violations") != []:
        errors.append("The default Day129 prompt contract must have no violations.")
    if report.get("contract_validation", {}).get("status") != OVERALL_STATUS:
        errors.extend(report.get("contract_validation", {}).get("violations", []))
    return errors


def write_ai_summary_prompt_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_summary_prompt_contract_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_summary_prompt_contract_html(safe_report, html_path)
    return json_path, html_path


def write_ai_summary_prompt_contract_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    boundary_rows = _table_rows(
        (
            ("openai_api_called", report["openai_api_called"]),
            ("provider_configuration_added", report["provider_configuration_added"]),
            ("tool_calling_behavior_added", report["tool_calling_behavior_added"]),
            ("live_integration_added", report["live_integration_added"]),
            ("not_day130_redaction_policy", report["not_day130_redaction_policy"]),
            ("not_day131_audit_trail_binding", report["not_day131_audit_trail_binding"]),
            ("not_day132_reviewer_approval_gate", report["not_day132_reviewer_approval_gate"]),
            ("not_day133_mock_provider_boundary", report["not_day133_mock_provider_boundary"]),
        )
    )
    prompt_text = str(report.get("contract_fixture", {}).get("prompt_text", ""))
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
  <h2>Prompt Contract Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Future Scope Boundary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
  <h2>Allowed Prompt</h2>
  <pre>{html.escape(prompt_text)}</pre>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_summary_prompt_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_summary_prompt_contract_report(project_root)
    json_path, html_path = write_ai_summary_prompt_contract_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: prompt contract for reviewer text only; no OpenAI API, provider, tool calls, execution, AI decision, redaction policy, audit trail binding, approval gate, mock provider boundary, or next-phase unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"openai_api_called: {json.dumps(report['openai_api_called'])}")
    print(f"provider_configuration_added: {json.dumps(report['provider_configuration_added'])}")
    print(f"tool_calling_behavior_added: {json.dumps(report['tool_calling_behavior_added'])}")
    print(f"live_integration_added: {json.dumps(report['live_integration_added'])}")
    print(f"day127_schema_reference: {json.dumps(report['day127_schema_reference'])}")
    print(f"day128_renderer_reference: {json.dumps(report['day128_renderer_reference'])}")
    print(f"not_day130_redaction_policy: {json.dumps(report['not_day130_redaction_policy'])}")
    print(f"not_day131_audit_trail_binding: {json.dumps(report['not_day131_audit_trail_binding'])}")
    print(f"not_day132_reviewer_approval_gate: {json.dumps(report['not_day132_reviewer_approval_gate'])}")
    print(f"not_day133_mock_provider_boundary: {json.dumps(report['not_day133_mock_provider_boundary'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {CONTRACT_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {report['reviewer_status']}")
    return 1


def _normalize_prompt(prompt_text: str) -> str:
    return re.sub(r"\s+", " ", prompt_text.lower()).strip()


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
    report = build_ai_summary_prompt_contract_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
