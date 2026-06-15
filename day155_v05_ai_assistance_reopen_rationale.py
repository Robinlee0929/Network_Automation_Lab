"""Day155 v0.5 AI Assistance reopen rationale.

This module records a deterministic, data-only rationale package for whether
v0.5 AI Assistance may be reopened after the Day154 closure baseline lock. It
is review-only/report-only evidence and does not unlock providers, APIs, model
calls, live devices, command execution, adapters, brokers, runners, secrets, or
the next phase.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 155
DAY_LABEL = "Day155"
TASK_NAME = "v05-ai-assistance-reopen-rationale"
TITLE = "v0.5 AI Assistance Reopen Rationale"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "docs-only / rationale-only / review-only / non-executable"
OVERALL_STATUS = "PASS"
STATUS = "REVIEW_READY"
FAIL_STATUS = "FAIL"
BLOCKED_STATUS = "BLOCKED"
FINAL_RECOMMENDATION = "ALLOW_REOPEN_RATIONALE_ONLY_KEEP_EXECUTION_LOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "day155_v05_ai_assistance_reopen_rationale.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day155_v05_ai_assistance_reopen_rationale.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day155_v05_ai_assistance_reopen_rationale.md"
AI_DOC = Path("docs") / "ai" / "day155_v05_ai_assistance_reopen_rationale.md"

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "agents_md_found_and_read",
    "agents_md_not_modified",
    "day154_closure_baseline_lock_respected",
    "reviewer_assistance_only",
    "executor_recommendation_only",
    "fixed_output_template_required",
    "human_reviewer_final_authority",
    "pytest_required",
    "report_index_no_new_blocking_issue_required",
    "forbidden_capability_scan_required",
    "safety_boundary_regression_required",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "docs_only_package_allows_ai_execution",
    "phase_gate_approval",
    "next_phase_allowed",
    "execution_allowed",
    "executor_unlock_allowed",
    "provider_allowed",
    "api_allowed",
    "external_api_call_allowed",
    "openai_api_call_allowed",
    "model_call_allowed",
    "live_device_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "routeros_allowed",
    "command_execution_allowed",
    "live_command_template_allowed",
    "secrets_allowed",
    "direct_command_generation_allowed",
)

RATIONALE_QUESTIONS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "Q1",
        "question": "Why is AI needed?",
        "answer": [
            "AI is needed to simplify and automate reviewer-side testing review steps.",
            "It may summarize reports, compare evidence, flag risk, and reduce repetitive review work.",
            "It must not replace human review.",
        ],
    },
    {
        "id": "Q2",
        "question": "Who does AI help?",
        "answer": [
            "Primary user: reviewer.",
            "Executor support is limited to recommendation-only guidance.",
            "Executor must not receive direct live commands or executable infrastructure actions from AI.",
        ],
    },
    {
        "id": "Q3",
        "question": "What data may AI read?",
        "answer": [
            {
                "allowed": [
                    "repo reports",
                    "evidence files",
                    "pytest results",
                    "report-index results",
                    "task registry metadata",
                    "roadmap/docs",
                    "dry-run outputs",
                    "mock-only fixtures",
                ],
                "forbidden": [
                    "secrets",
                    "tokens",
                    "passwords",
                    "private keys",
                    ".env files",
                    "production credentials",
                    "live device configs",
                    "unauthorized external API responses",
                ],
            }
        ],
    },
    {
        "id": "Q4",
        "question": "What must AI never do?",
        "answer": [
            "It must never directly issue commands.",
            "It must never activate providers.",
            "It must never call live APIs.",
            "It must never access live devices.",
            "It must never generate executable live infrastructure commands.",
            "It must only provide templated review output.",
        ],
    },
    {
        "id": "Q5",
        "question": "Under what conditions is AI Assistance allowed into the repo?",
        "answer": [
            "reviewer-assistance only",
            "executor recommendation-only",
            "fixed output template",
            "no direct command generation",
            "no secrets access",
            "no provider/API/live device activation",
            "pytest passes",
            "report-index has no new blocking issue",
            "forbidden capability scan passes",
            "safety boundary regression passes",
            "human reviewer keeps final decision authority",
            "next_phase_allowed remains false for this Day155 rationale package",
        ],
    },
)

PASS_SEMANTICS: Tuple[str, ...] = (
    "PASS only means the reopen rationale is documented and safety-bounded.",
    "PASS does not mean AI execution is allowed.",
    "PASS does not mean provider/API integration is allowed.",
    "PASS does not mean executor can act on AI output.",
    "next_phase_allowed must remain false.",
)

REFERENCE_TARGETS: Tuple[Dict[str, Any], ...] = (
    {
        "surface": "Day155 roadmap doc",
        "path": ROADMAP_DOC.as_posix(),
        "required_fragments": (
            TASK_NAME,
            TITLE,
            "next_phase_allowed: false",
            "provider_allowed: false",
            "api_allowed: false",
            "executor_unlock_allowed: false",
        ),
    },
    {
        "surface": "Day155 AI doc",
        "path": AI_DOC.as_posix(),
        "required_fragments": (
            TITLE,
            "Why is AI needed?",
            "Who does AI help?",
            "What data may AI read?",
            "What must AI never do?",
            "Under what conditions is AI Assistance allowed into the repo?",
            "next_phase_allowed: false",
        ),
    },
    {
        "surface": "task registry",
        "path": "network_lab_task_registry.py",
        "required_fragments": (TASK_NAME,),
    },
    {
        "surface": "CLI dispatch",
        "path": "network_lab_cli_dispatch.py",
        "required_fragments": (TASK_NAME, "_run_day155_v05_ai_assistance_reopen_rationale"),
    },
    {
        "surface": "network_lab task catalog and report-index",
        "path": "network_lab.py",
        "required_fragments": (
            "DAY155_V05_AI_ASSISTANCE_REOPEN_RATIONALE_TASK_ID",
            "DAY155_V05_AI_ASSISTANCE_REOPEN_RATIONALE_JSON",
            "DAY155_V05_AI_ASSISTANCE_REOPEN_RATIONALE_HTML",
            "day155_v05_ai_assistance_reopen_rationale",
        ),
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read": "NO",
            "agents_md_result": f"READ_ERROR: {exc}",
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": True,
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read": "YES" if markers_present else "NO",
        "agents_md_result": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
    }


def build_day155_v05_ai_assistance_reopen_rationale(project_root: Path) -> Dict[str, Any]:
    reference_records = [_build_reference_record(Path(project_root), target) for target in REFERENCE_TARGETS]
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "overall_status": OVERALL_STATUS,
        "status": STATUS,
        "mode": MODE,
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        **build_agents_md_evidence(project_root),
        "rationale_questions": deepcopy(list(RATIONALE_QUESTIONS)),
        "pass_semantics": list(PASS_SEMANTICS),
        "fixed_review_output_template": {
            "template_id": "day155_v05_reviewer_assistance_summary",
            "output_type": "templated_review_output_only",
            "fields": [
                "review_subject",
                "evidence_references",
                "summary",
                "risk_flags",
                "comparison_notes",
                "open_questions",
                "human_reviewer_decision",
            ],
            "live_command_field_present": False,
            "executor_action_field_present": False,
            "provider_activation_field_present": False,
            "secrets_field_present": False,
        },
        "forbidden_capability_scan": {
            "status": OVERALL_STATUS,
            "provider_api_live_device_activation_found": False,
            "direct_command_generation_found": False,
            "secrets_access_found": False,
            "executor_unlock_found": False,
        },
        "safety_boundary_regression": {
            "status": OVERALL_STATUS,
            "day154_closure_baseline_lock_respected": True,
            "next_phase_allowed": False,
            "phase_gate_approval": False,
        },
        "result_semantics": {
            "pass_means": "reopen rationale documented and safety-bounded",
            "ai_execution_allowed": False,
            "provider_api_integration_allowed": False,
            "executor_can_act_on_ai_output": False,
            "next_phase_allowed": False,
        },
        "reference_records": reference_records,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    if report["validation_errors"]:
        report["overall_status"] = FAIL_STATUS
        report["status"] = BLOCKED_STATUS
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_values = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "overall_status": OVERALL_STATUS,
        "status": STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read") != "YES":
        errors.append("agents_md_pre_read must be YES.")
    if report.get("agents_md_result") != "FOUND_AND_READ":
        errors.append("agents_md_result must be FOUND_AND_READ.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    questions = report.get("rationale_questions")
    if not isinstance(questions, list) or len(questions) != 5:
        errors.append("rationale_questions must contain exactly five questions.")
    else:
        expected_questions = [item["question"] for item in RATIONALE_QUESTIONS]
        actual_questions = [item.get("question") for item in questions]
        if actual_questions != expected_questions:
            errors.append("rationale_questions must preserve the required five questions in order.")

    if report.get("pass_semantics") != list(PASS_SEMANTICS):
        errors.append("pass_semantics must preserve the Day155 PASS boundaries.")

    template = report.get("fixed_review_output_template")
    if not isinstance(template, dict):
        errors.append("fixed_review_output_template must be present.")
    else:
        for field in (
            "live_command_field_present",
            "executor_action_field_present",
            "provider_activation_field_present",
            "secrets_field_present",
        ):
            if template.get(field) is not False:
                errors.append(f"fixed_review_output_template.{field} must be false.")

    forbidden_scan = report.get("forbidden_capability_scan")
    if not isinstance(forbidden_scan, dict) or forbidden_scan.get("status") != OVERALL_STATUS:
        errors.append("forbidden_capability_scan.status must be PASS.")
    elif any(value is not False for key, value in forbidden_scan.items() if key != "status"):
        errors.append("forbidden_capability_scan unsafe findings must all be false.")

    safety_boundary = report.get("safety_boundary_regression")
    if not isinstance(safety_boundary, dict) or safety_boundary.get("status") != OVERALL_STATUS:
        errors.append("safety_boundary_regression.status must be PASS.")
    else:
        if safety_boundary.get("day154_closure_baseline_lock_respected") is not True:
            errors.append("safety_boundary_regression.day154_closure_baseline_lock_respected must be true.")
        if safety_boundary.get("next_phase_allowed") is not False:
            errors.append("safety_boundary_regression.next_phase_allowed must be false.")
        if safety_boundary.get("phase_gate_approval") is not False:
            errors.append("safety_boundary_regression.phase_gate_approval must be false.")

    semantics = report.get("result_semantics")
    if not isinstance(semantics, dict):
        errors.append("result_semantics must be present.")
    else:
        for field in ("ai_execution_allowed", "provider_api_integration_allowed", "executor_can_act_on_ai_output", "next_phase_allowed"):
            if semantics.get(field) is not False:
                errors.append(f"result_semantics.{field} must be false.")

    records = report.get("reference_records")
    if not isinstance(records, list) or len(records) != len(REFERENCE_TARGETS):
        errors.append("reference_records must cover all Day155 reference targets.")
    else:
        for record in records:
            if record.get("path_exists") is not True:
                errors.append(f"{record.get('surface', '<unknown>')} path must exist.")
            if record.get("missing_fragments") != []:
                errors.append(f"{record.get('surface', '<unknown>')} must contain all required fragments.")
            if record.get("next_phase_allowed") is not False:
                errors.append(f"{record.get('surface', '<unknown>')} next_phase_allowed must be false.")
    return errors


def write_day155_v05_ai_assistance_reopen_rationale_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day155_v05_ai_assistance_reopen_rationale(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day155_v05_ai_assistance_reopen_rationale_html(safe_report, html_path)
    return json_path, html_path


def write_day155_v05_ai_assistance_reopen_rationale_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (field, report[field])
        for field in (
            "day",
            "status",
            "mode",
            "reviewer_assistance_only",
            "executor_recommendation_only",
            "fixed_output_template_required",
            "execution_allowed",
            "provider_allowed",
            "api_allowed",
            "openai_api_call_allowed",
            "external_api_call_allowed",
            "live_device_allowed",
            "command_execution_allowed",
            "executor_unlock_allowed",
            "phase_gate_approval",
            "next_phase_allowed",
        )
    )
    question_rows = _table_rows(
        (item.get("id", ""), item.get("question", ""), item.get("answer", ""))
        for item in report.get("rationale_questions", [])
    )
    reference_rows = _table_rows(
        (
            item.get("surface", ""),
            item.get("path", ""),
            item.get("path_exists", False),
            item.get("all_required_fragments_present", False),
            item.get("missing_fragments", []),
        )
        for item in report.get("reference_records", [])
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
  <p><strong>V05_AI_ASSISTANCE_REOPEN_RATIONALE_REVIEW_READY</strong></p>
  <p><strong>next_phase_allowed=false</strong></p>
  <p><strong>PASS does not allow AI execution, provider/API integration, or executor action.</strong></p>
  <h2>Status</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Five Required Questions</h2>
  <table><thead><tr><th>ID</th><th>Question</th><th>Answer</th></tr></thead><tbody>{question_rows}</tbody></table>
  <h2>Reference Records</h2>
  <table><thead><tr><th>Surface</th><th>Path</th><th>Path Exists</th><th>Fragments Present</th><th>Missing Fragments</th></tr></thead><tbody>{reference_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day155_v05_ai_assistance_reopen_rationale(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day155_v05_ai_assistance_reopen_rationale(project_root)
    json_path, html_path = write_day155_v05_ai_assistance_reopen_rationale_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read']}")
    print(f"AGENTS.md result: {report['agents_md_result']}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Task slug: {TASK_NAME}")
    for field in (
        "day",
        "status",
        "mode",
        "reviewer_assistance_only",
        "executor_recommendation_only",
        "fixed_output_template_required",
        "execution_allowed",
        "provider_allowed",
        "api_allowed",
        "openai_api_call_allowed",
        "external_api_call_allowed",
        "live_device_allowed",
        "command_execution_allowed",
        "executor_unlock_allowed",
        "phase_gate_approval",
        "next_phase_allowed",
    ):
        print(f"{field}: {_json_value(report[field])}")
    print(f"rationale_question_count: {len(report['rationale_questions'])}")
    for item in report["rationale_questions"]:
        print(f"{item['id']}: {item['question']}")
    print(f"forbidden_capability_scan: {report['forbidden_capability_scan']['status']}")
    print(f"safety_boundary_regression: {report['safety_boundary_regression']['status']}")
    for line in report["pass_semantics"]:
        print(f"pass_semantics: {line}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} V05_AI_ASSISTANCE_REOPEN_RATIONALE_REVIEW_READY")
        return 0

    print(f"{format_status(FAIL_STATUS)} V05_AI_ASSISTANCE_REOPEN_RATIONALE_BLOCKED")
    return 1


def _build_reference_record(project_root: Path, target: Mapping[str, Any]) -> Dict[str, Any]:
    path = project_root / str(target["path"])
    text = _read_text(path)
    required_fragments = list(target["required_fragments"])
    missing_fragments = [fragment for fragment in required_fragments if fragment not in text]
    return {
        "surface": target["surface"],
        "path": target["path"],
        "path_exists": path.exists(),
        "required_fragments": required_fragments,
        "missing_fragments": missing_fragments,
        "all_required_fragments_present": path.exists() and not missing_fragments,
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _json_value(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    return str(value)


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
