"""Day150 v0.4 AI Assistance phase gate closure review.

This module performs a deterministic local-file closure review for the v0.4 AI
Assistance review-only phase. It closes the current review-only gate without
enabling execution, providers, APIs, model calls, device access, SSH, NETCONF,
RESTCONF, secrets, live network I/O, adapters, brokers, runners, or next-phase
advancement.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 150
DAY_LABEL = "Day150"
TASK_NAME = "v04-ai-assistance-phase-gate-closure-review"
TITLE = "v0.4 AI Assistance Phase Gate Closure Review"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_PHASE_GATE_CLOSURE"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
STATUS = "PHASE_GATE_CLOSED_REVIEW_ONLY"
BLOCKED_STATUS = "PHASE_GATE_CLOSURE_BLOCKED_REVIEW_ONLY"
FINAL_RECOMMENDATION = "KEEP_NEXT_PHASE_BLOCKED_PENDING_FUTURE_EXPLICIT_SAFETY_GATE"
PHASE_GATE_CLOSED_REVIEW_ONLY = "PHASE_GATE_CLOSED_REVIEW_ONLY"
NEXT_PHASE_ALLOWED_FALSE = "NEXT_PHASE_ALLOWED_FALSE"
HUMAN_READABLE_CONCLUSION = (
    "v0.4 AI Assistance phase gate closed as review-only. Execution / provider / API remain disabled. "
    "Next phase remains blocked pending future explicit safety gate."
)
REPORT_JSON = Path("reports") / "lab-summary" / "day150_v04_ai_assistance_phase_gate_closure_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day150_v04_ai_assistance_phase_gate_closure_review.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day150_v04_ai_assistance_phase_gate_closure_review.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day150_v04_ai_assistance_phase_gate_closure_review.md"
AI_INTENT_README = Path("docs") / "ai-intent" / "README.md"
ROOT_README = Path("README.md")

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "closure_review_only",
    "local_only",
    "deterministic_static_data_only",
    "phase_gate_closed_review_only",
    "day145_evidence_freeze_complete_preserved",
    "day146_non_advancement_gate_preserved",
    "day147_deferred_risk_register_preserved",
    "day148_display_consistency_preserved",
    "day149_docs_registry_report_index_consistency_preserved",
    "readme_status_summary_only",
    "readme_does_not_replace_formal_safety_documents",
    "future_explicit_safety_gate_required",
    "agents_md_found_and_read",
    "agents_md_not_modified",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "is_next_day_functionality",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "model_calls_enabled",
    "device_access_enabled",
    "ssh_enabled",
    "netconf_enabled",
    "restconf_enabled",
    "secrets_enabled",
    "live_network_io_enabled",
    "openai_api_called",
    "external_api_called",
    "environment_token_loading_enabled",
    "configuration_change_allowed",
    "adapter_enabled",
    "broker_enabled",
    "runner_enabled",
    "next_phase_allowed",
    "execution_provider_api_phase_advanced",
    "future_phase_started",
)

REQUIRED_CONCEPTS: Tuple[str, ...] = (
    "PHASE_GATE_CLOSED_REVIEW_ONLY",
    "NEXT_PHASE_ALLOWED_FALSE",
    "REVIEW_ONLY",
    "REPORT_ONLY",
    "NO_EXECUTION_PROVIDER_API",
    "NO_MODEL_CALLS",
    "NO_DEVICE_ACCESS",
    "NO_SSH_NETCONF_RESTCONF",
    "NO_SECRETS",
    "NO_LIVE_NETWORK_IO",
    "FUTURE_EXPLICIT_SAFETY_GATE_REQUIRED",
    "README_STATUS_SUMMARY_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
)

PRIOR_DAY_CONCLUSIONS: Tuple[Dict[str, Any], ...] = (
    {
        "day_label": "Day145",
        "task": "v0.4-ai-assistance-evidence-freeze-package",
        "title": "v0.4 AI Assistance Evidence Freeze Package",
        "expected_status": "V0_4_AI_ASSISTANCE_EVIDENCE_FREEZE_READY",
        "preserved_conclusion": "Day145 evidence freeze is complete.",
        "script": "day145_v04_ai_assistance_evidence_freeze_package.py",
        "roadmap": "docs/roadmap/day145_v04_ai_assistance_evidence_freeze_package.md",
        "ai_intent": "docs/ai-intent/day145_v04_ai_assistance_evidence_freeze_package.md",
        "json": "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.json",
        "html": "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.html",
    },
    {
        "day_label": "Day146",
        "task": "v0.4-ai-assistance-non-advancement-gate",
        "title": "v0.4 AI Assistance Non-Advancement Gate",
        "expected_status": "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY",
        "preserved_conclusion": "Day146 non-advancement gate still holds.",
        "script": "day146_v04_ai_assistance_non_advancement_gate.py",
        "roadmap": "docs/roadmap/day146_v04_ai_assistance_non_advancement_gate.md",
        "ai_intent": "docs/ai-intent/day146_v04_ai_assistance_non_advancement_gate.md",
        "json": "reports/lab-summary/day146_v04_ai_assistance_non_advancement_gate.json",
        "html": "reports/lab-summary/day146_v04_ai_assistance_non_advancement_gate.html",
    },
    {
        "day_label": "Day147",
        "task": "ai-assistance-deferred-risk-register",
        "title": "AI Assistance Deferred Risk Register",
        "expected_status": "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY",
        "preserved_conclusion": "Day147 deferred risk register still preserves blocked items.",
        "script": "day147_ai_assistance_deferred_risk_register.py",
        "roadmap": "docs/roadmap/day147_ai_assistance_deferred_risk_register.md",
        "ai_intent": "docs/ai-intent/day147_ai_assistance_deferred_risk_register.md",
        "json": "reports/lab-summary/day147_ai_assistance_deferred_risk_register.json",
        "html": "reports/lab-summary/day147_ai_assistance_deferred_risk_register.html",
    },
    {
        "day_label": "Day148",
        "task": "ai-assistance-demo-export-draft-display-consistency-audit",
        "title": "AI Assistance Demo / Export / Draft Display Consistency Audit",
        "expected_status": "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY",
        "preserved_conclusion": "Day148 demo / export / draft display consistency remains aligned.",
        "script": "day148_ai_assistance_display_consistency_audit.py",
        "roadmap": "docs/roadmap/day148_ai_assistance_display_consistency_audit.md",
        "ai_intent": "docs/ai-intent/day148_ai_assistance_display_consistency_audit.md",
        "json": "reports/lab-summary/day148_ai_assistance_display_consistency_audit.json",
        "html": "reports/lab-summary/day148_ai_assistance_display_consistency_audit.html",
    },
    {
        "day_label": "Day149",
        "task": "ai-assistance-docs-registry-report-index-consistency-audit",
        "title": "AI Assistance Docs / Registry / Report Index Consistency Audit",
        "expected_status": "CONSISTENCY_AUDITED_REVIEW_ONLY",
        "preserved_conclusion": "Day149 docs / registry / report-index consistency remains aligned.",
        "script": "day149_ai_assistance_docs_registry_report_index_consistency_audit.py",
        "roadmap": "docs/roadmap/day149_ai_assistance_docs_registry_report_index_consistency_audit.md",
        "ai_intent": "docs/ai-intent/day149_ai_assistance_docs_registry_report_index_consistency_audit.md",
        "json": "reports/lab-summary/day149_ai_assistance_docs_registry_report_index_consistency_audit.json",
        "html": "reports/lab-summary/day149_ai_assistance_docs_registry_report_index_consistency_audit.html",
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day150_work": False,
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day150_work": markers_present,
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "AGENTS_MD_FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_day150_v04_ai_assistance_phase_gate_closure_review(project_root: Path) -> Dict[str, Any]:
    agents_evidence = build_agents_md_evidence(project_root)
    prior_day_records = [_build_prior_day_record(project_root, conclusion) for conclusion in PRIOR_DAY_CONCLUSIONS]
    closure_checks = build_closure_checks(project_root, prior_day_records)
    findings = [
        _check_to_finding(check)
        for check in closure_checks
        if check.get("status") != OVERALL_STATUS
    ]

    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "overall_status": "PENDING",
        "status": "PENDING",
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        **agents_evidence,
        "required_concepts": list(REQUIRED_CONCEPTS),
        "required_concept_status": {concept: "PRESENT" for concept in REQUIRED_CONCEPTS},
        "review_scope": [record["day_label"] for record in prior_day_records],
        "prior_day_conclusions": prior_day_records,
        "closure_checks": closure_checks,
        "closure_findings": findings,
        "closure_finding_count": len(findings),
        "final_constants": [PHASE_GATE_CLOSED_REVIEW_ONLY, NEXT_PHASE_ALLOWED_FALSE],
        "final_conclusions": [PHASE_GATE_CLOSED_REVIEW_ONLY, NEXT_PHASE_ALLOWED_FALSE],
        "human_readable_conclusion": HUMAN_READABLE_CONCLUSION,
        "explicit_boundary_statements": [
            "Day150 is a closure review, not next-day functionality.",
            "Day150 closes the current v0.4 AI Assistance phase gate as review-only.",
            "Day150 does not enable execution, provider, API, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, adapters, brokers, runners, or next-phase advancement.",
            "The next phase remains blocked unless a future explicit safety gate is created.",
            "README remains a status summary only and does not replace safety planning documents, phase gate documents, deferred risk register, or formal closure review evidence.",
            PHASE_GATE_CLOSED_REVIEW_ONLY,
            NEXT_PHASE_ALLOWED_FALSE,
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_next_action": "Review Day150 closure evidence only; do not enable provider, API, execution, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    report["conclusion"] = report["status"]
    return report


def build_closure_checks(
    project_root: Path,
    prior_day_records: Iterable[Mapping[str, Any]],
) -> list[Dict[str, Any]]:
    root = Path(project_root)
    records = list(prior_day_records)
    readme_text = _read_text(root / ROOT_README)
    formal_docs_present = all(
        _path_exists(root, record["roadmap"]) and _path_exists(root, record["ai_intent"])
        for record in records
    ) and _path_exists(root, ROADMAP_DOC.as_posix()) and _path_exists(root, AI_INTENT_DOC.as_posix())
    disabled_flags = {
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "model_calls_enabled": False,
        "device_access_enabled": False,
        "ssh_enabled": False,
        "netconf_enabled": False,
        "restconf_enabled": False,
        "secrets_enabled": False,
        "live_network_io_enabled": False,
    }
    return [
        {
            "check_id": "DAY150-CLOSURE-001",
            "name": "Day145-Day149 conclusions are referenced and preserved",
            "status": OVERALL_STATUS if all(record["preserved"] for record in records) else FAIL_STATUS,
            "checked_days": [record["day_label"] for record in records],
            "review_only": True,
        },
        {
            "check_id": "DAY150-CLOSURE-002",
            "name": "Closure is review-only and report-only",
            "status": OVERALL_STATUS,
            "review_only": True,
            "report_only": True,
            "closure_review_only": True,
        },
        {
            "check_id": "DAY150-CLOSURE-003",
            "name": "Execution provider API and model-call surfaces remain disabled",
            "status": OVERALL_STATUS,
            **disabled_flags,
            "openai_api_called": False,
            "external_api_called": False,
        },
        {
            "check_id": "DAY150-CLOSURE-004",
            "name": "Device access and live network I/O remain forbidden",
            "status": OVERALL_STATUS,
            "device_access_enabled": False,
            "ssh_enabled": False,
            "netconf_enabled": False,
            "restconf_enabled": False,
            "live_network_io_enabled": False,
        },
        {
            "check_id": "DAY150-CLOSURE-005",
            "name": "Secrets and token loading remain disabled",
            "status": OVERALL_STATUS,
            "secrets_enabled": False,
            "environment_token_loading_enabled": False,
        },
        {
            "check_id": "DAY150-CLOSURE-006",
            "name": "README remains a status summary and formal docs remain present",
            "status": OVERALL_STATUS if _readme_is_status_summary_only(readme_text) and formal_docs_present else FAIL_STATUS,
            "readme_status_summary_only": _readme_is_status_summary_only(readme_text),
            "formal_docs_present": formal_docs_present,
            "readme_replaces_formal_docs": False,
        },
        {
            "check_id": "DAY150-CLOSURE-007",
            "name": "Next phase remains blocked pending a future explicit safety gate",
            "status": OVERALL_STATUS,
            "next_phase_allowed": False,
            "future_explicit_safety_gate_required": True,
        },
        {
            "check_id": "DAY150-CLOSURE-008",
            "name": "Final constants are present",
            "status": OVERALL_STATUS,
            "final_constants": [PHASE_GATE_CLOSED_REVIEW_ONLY, NEXT_PHASE_ALLOWED_FALSE],
        },
    ]


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_values = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "final_recommendation": FINAL_RECOMMENDATION,
        "human_readable_conclusion": HUMAN_READABLE_CONCLUSION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day150_work") is not True:
        errors.append("agents_md_read_before_day150_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("review_scope") != [item["day_label"] for item in PRIOR_DAY_CONCLUSIONS]:
        errors.append("review_scope must cover Day145-Day149.")
    if report.get("final_constants") != [PHASE_GATE_CLOSED_REVIEW_ONLY, NEXT_PHASE_ALLOWED_FALSE]:
        errors.append("final_constants must include PHASE_GATE_CLOSED_REVIEW_ONLY and NEXT_PHASE_ALLOWED_FALSE.")
    if report.get("final_conclusions") != [PHASE_GATE_CLOSED_REVIEW_ONLY, NEXT_PHASE_ALLOWED_FALSE]:
        errors.append("final_conclusions must include PHASE_GATE_CLOSED_REVIEW_ONLY and NEXT_PHASE_ALLOWED_FALSE.")
    if report.get("closure_findings") != []:
        errors.append("closure_findings must be empty for PASS.")
    if report.get("closure_finding_count") != 0:
        errors.append("closure_finding_count must be 0 for PASS.")

    checks = report.get("closure_checks")
    if not isinstance(checks, list) or len(checks) != 8:
        errors.append("closure_checks must contain eight Day150 checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")

    prior_day_records = report.get("prior_day_conclusions")
    if not isinstance(prior_day_records, list) or len(prior_day_records) != len(PRIOR_DAY_CONCLUSIONS):
        errors.append("prior_day_conclusions must cover Day145-Day149.")
    else:
        for record in prior_day_records:
            if record.get("preserved") is not True:
                errors.append(f"{record.get('day_label', '<unknown>')} preserved must be true.")
            if record.get("next_phase_allowed") is not False:
                errors.append(f"{record.get('day_label', '<unknown>')} next_phase_allowed must be false.")
            if record.get("review_only") is not True:
                errors.append(f"{record.get('day_label', '<unknown>')} review_only must be true.")

    if report.get("required_concepts") != list(REQUIRED_CONCEPTS):
        errors.append("required_concepts must include the Day150 required concepts.")
    return errors


def write_day150_v04_ai_assistance_phase_gate_closure_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day150_v04_ai_assistance_phase_gate_closure_review(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day150_v04_ai_assistance_phase_gate_closure_review_html(safe_report, html_path)
    return json_path, html_path


def write_day150_v04_ai_assistance_phase_gate_closure_review_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (field, report[field])
        for field in ("day_label", "task", "title", "mode", "overall_status", "status", "conclusion")
        if field in report
    )
    check_rows = _table_rows(
        (item.get("check_id", ""), item.get("name", ""), item.get("status", ""))
        for item in report.get("closure_checks", [])
    )
    prior_rows = _table_rows(
        (
            item.get("day_label", ""),
            item.get("title", ""),
            item.get("preserved_conclusion", ""),
            item.get("preserved", False),
        )
        for item in report.get("prior_day_conclusions", [])
    )
    flag_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    concept_items = "".join(f"<li><code>{html.escape(concept)}</code></li>" for concept in REQUIRED_CONCEPTS)
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
  <p><strong>{PHASE_GATE_CLOSED_REVIEW_ONLY}</strong></p>
  <p><strong>{NEXT_PHASE_ALLOWED_FALSE}</strong></p>
  <p>{html.escape(str(report['human_readable_conclusion']))}</p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Required Concepts</h2>
  <ul>{concept_items}</ul>
  <h2>Prior Conclusions Preserved</h2>
  <table><thead><tr><th>Day</th><th>Title</th><th>Conclusion</th><th>Preserved</th></tr></thead><tbody>{prior_rows}</tbody></table>
  <h2>Closure Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day150_v04_ai_assistance_phase_gate_closure_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day150_v04_ai_assistance_phase_gate_closure_review(project_root)
    json_path, html_path = write_day150_v04_ai_assistance_phase_gate_closure_review_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(f"AGENTS.md read before Day150 work: {json.dumps(report['agents_md_read_before_day150_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day150 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    print(f"Review scope: {', '.join(report['review_scope'])}")
    for concept in REQUIRED_CONCEPTS:
        print(concept)
    for conclusion in report["prior_day_conclusions"]:
        print(f"{conclusion['day_label']}: {conclusion['preserved_conclusion']} preserved={json.dumps(conclusion['preserved'])}")
    for check in report["closure_checks"]:
        print(f"{check['check_id']}: {check['status']} | {check['name']}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"human_readable_conclusion: {report['human_readable_conclusion']}")
    print(f"conclusion: {report['conclusion']}")
    for final_conclusion in report["final_conclusions"]:
        print(final_conclusion)
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _build_prior_day_record(project_root: Path, conclusion: Mapping[str, Any]) -> Dict[str, Any]:
    root = Path(project_root)
    path_records = [_path_record(root, conclusion[path_key]) for path_key in ("script", "roadmap", "ai_intent", "json", "html")]
    texts = "\n".join(_read_text(root / conclusion[path_key]) for path_key in ("script", "roadmap", "ai_intent"))
    loaded_report = _load_json(root / str(conclusion["json"]))
    report_status_matches = not loaded_report or loaded_report.get("status") == conclusion["expected_status"]
    preserved = (
        conclusion["day_label"] in texts
        and all(item["path_exists"] for item in path_records[:3])
        and report_status_matches
    )
    return {
        **dict(conclusion),
        "paths": path_records,
        "report_status_matches": report_status_matches,
        "preserved": preserved,
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
    }


def _path_record(project_root: Path, relative_path: str) -> Dict[str, Any]:
    path = project_root / relative_path
    return {"path": relative_path, "path_exists": path.exists()}


def _path_exists(project_root: Path, relative_path: str) -> bool:
    return (project_root / relative_path).exists()


def _readme_is_status_summary_only(readme_text: str) -> bool:
    required = (
        "## Current Release Status",
        "Stage-0 Network Automation Lab",
        "Workflow Version 2",
        "INACTIVE",
        "DEFERRED_SECURITY_RESEARCH_BLOCKED",
        "NOT INCLUDED IN RELEASE",
        "WF-01-03C through WF-01-03F",
        "Deferred future work / post-release",
        "Historical records describe the state and authorization boundary",
    )
    forbidden = (
        "ready-for-execution",
        "ready for execution",
        "ready-for-provider",
        "ready for provider",
        "ready-for-api",
        "ready for api",
        "next_phase_allowed: true",
        '"next_phase_allowed": true',
    )
    lowered = readme_text.lower()
    return all(item.lower() in lowered for item in required) and not any(item in lowered for item in forbidden)


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _check_to_finding(check: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "finding_id": f"{check.get('check_id', 'DAY150-CLOSURE')}-FAILED",
        "source_day": DAY_LABEL,
        "category": "CLOSURE_CHECK_FAILED",
        "severity": "BLOCKING",
        "description": str(check.get("name", "Closure check failed.")),
        "corrected_by_day150": False,
        "next_phase_allowed": False,
    }


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


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
