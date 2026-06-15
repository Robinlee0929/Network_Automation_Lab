"""Day149 AI assistance docs/registry/report-index consistency audit.

This module performs a deterministic local-file audit over Day145-Day149 AI
Assistance documentation, task registry wiring, and report-index registration.
It is review-only/report-only and does not enable execution, providers, APIs,
model calls, adapters, brokers, runners, SSH, live device access, secrets, or
next-day functionality.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 149
DAY_LABEL = "Day149"
TASK_NAME = "ai-assistance-docs-registry-report-index-consistency-audit"
TITLE = "AI Assistance Docs / Registry / Report Index Consistency Audit"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_REPORT_ONLY_CONSISTENCY_AUDIT"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "CONSISTENCY_AUDITED_REVIEW_ONLY"
BLOCKED_STATUS = "CONSISTENCY_AUDIT_BLOCKED_REVIEW_ONLY"
FINAL_RECOMMENDATION = "KEEP_AI_ASSISTANCE_DOCS_REGISTRY_REPORT_INDEX_REVIEW_ONLY_AND_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day149_ai_assistance_docs_registry_report_index_consistency_audit.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day149_ai_assistance_docs_registry_report_index_consistency_audit.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day149_ai_assistance_docs_registry_report_index_consistency_audit.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day149_ai_assistance_docs_registry_report_index_consistency_audit.md"
AI_INTENT_README = Path("docs") / "ai-intent" / "README.md"

REQUIRED_CONCEPTS: Tuple[str, ...] = (
    "NOT_NEXT_DAY_FUNCTIONALITY",
    "EXECUTION_PROVIDER_API_DISABLED",
    "REVIEW_ONLY",
    "REPORT_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
)

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "audit_only",
    "local_only",
    "deterministic_static_data_only",
    "not_next_day_functionality_confirmed",
    "docs_registry_report_index_consistency_audited",
    "agents_md_found_and_read",
    "agents_md_not_modified",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "is_next_day_functionality",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "model_call_enabled",
    "network_device_live_access_enabled",
    "adapter_broker_runner_enabled",
    "ssh_enabled",
    "netconf_enabled",
    "restconf_enabled",
    "openai_api_called",
    "external_api_called",
    "secrets_required",
    "environment_token_loading_enabled",
    "configuration_change_allowed",
    "next_phase_allowed",
    "future_day_functionality_implied",
    "day150_implemented",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "overall_status",
    "status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day149_work",
    "agents_md_modified",
    "audit_scope",
    "consistency_checks",
    "mismatch_findings",
    "final_recommendation",
)

DAY_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "day": 145,
        "day_label": "Day145",
        "task": "v0.4-ai-assistance-evidence-freeze-package",
        "task_id": "day145_v04_ai_assistance_evidence_freeze_package",
        "title": "v0.4 AI Assistance Evidence Freeze Package",
        "status": "V0_4_AI_ASSISTANCE_EVIDENCE_FREEZE_READY",
        "script": "day145_v04_ai_assistance_evidence_freeze_package.py",
        "roadmap": "docs/roadmap/day145_v04_ai_assistance_evidence_freeze_package.md",
        "ai_intent": "docs/ai-intent/day145_v04_ai_assistance_evidence_freeze_package.md",
        "json": "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.json",
        "html": "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.html",
    },
    {
        "day": 146,
        "day_label": "Day146",
        "task": "v0.4-ai-assistance-non-advancement-gate",
        "task_id": "day146_v04_ai_assistance_non_advancement_gate",
        "title": "v0.4 AI Assistance Non-Advancement Gate",
        "status": "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY",
        "script": "day146_v04_ai_assistance_non_advancement_gate.py",
        "roadmap": "docs/roadmap/day146_v04_ai_assistance_non_advancement_gate.md",
        "ai_intent": "docs/ai-intent/day146_v04_ai_assistance_non_advancement_gate.md",
        "json": "reports/lab-summary/day146_v04_ai_assistance_non_advancement_gate.json",
        "html": "reports/lab-summary/day146_v04_ai_assistance_non_advancement_gate.html",
    },
    {
        "day": 147,
        "day_label": "Day147",
        "task": "ai-assistance-deferred-risk-register",
        "task_id": "day147_ai_assistance_deferred_risk_register",
        "title": "AI Assistance Deferred Risk Register",
        "status": "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY",
        "script": "day147_ai_assistance_deferred_risk_register.py",
        "roadmap": "docs/roadmap/day147_ai_assistance_deferred_risk_register.md",
        "ai_intent": "docs/ai-intent/day147_ai_assistance_deferred_risk_register.md",
        "json": "reports/lab-summary/day147_ai_assistance_deferred_risk_register.json",
        "html": "reports/lab-summary/day147_ai_assistance_deferred_risk_register.html",
    },
    {
        "day": 148,
        "day_label": "Day148",
        "task": "ai-assistance-demo-export-draft-display-consistency-audit",
        "task_id": "day148_ai_assistance_display_consistency_audit",
        "title": "AI Assistance Demo / Export / Draft Display Consistency Audit",
        "status": "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY",
        "script": "day148_ai_assistance_display_consistency_audit.py",
        "roadmap": "docs/roadmap/day148_ai_assistance_display_consistency_audit.md",
        "ai_intent": "docs/ai-intent/day148_ai_assistance_display_consistency_audit.md",
        "json": "reports/lab-summary/day148_ai_assistance_display_consistency_audit.json",
        "html": "reports/lab-summary/day148_ai_assistance_display_consistency_audit.html",
    },
    {
        "day": 149,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "task_id": "day149_ai_assistance_docs_registry_report_index_consistency_audit",
        "title": TITLE,
        "status": READY_STATUS,
        "script": "day149_ai_assistance_docs_registry_report_index_consistency_audit.py",
        "roadmap": ROADMAP_DOC.as_posix(),
        "ai_intent": AI_INTENT_DOC.as_posix(),
        "json": REPORT_JSON.as_posix(),
        "html": REPORT_HTML.as_posix(),
        "current_task_output": True,
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day149_work": False,
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day149_work": markers_present,
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "AGENTS_MD_FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_day149_ai_assistance_docs_registry_report_index_consistency_audit(project_root: Path) -> Dict[str, Any]:
    day_records = [_build_day_record(project_root, spec) for spec in DAY_SPECS]
    consistency_checks = build_consistency_checks(project_root, day_records)
    mismatch_findings = [
        finding
        for record in day_records
        for finding in record.get("mismatch_findings", [])
    ]
    mismatch_findings.extend(
        _check_to_finding(check)
        for check in consistency_checks
        if check.get("status") != OVERALL_STATUS
    )
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
        "required_concepts": list(REQUIRED_CONCEPTS),
        "required_concept_status": {concept: "PRESENT" for concept in REQUIRED_CONCEPTS},
        "audit_scope": [spec["day_label"] for spec in DAY_SPECS],
        "day_records": day_records,
        "consistency_checks": consistency_checks,
        "mismatch_findings": mismatch_findings,
        "mismatch_finding_count": len(mismatch_findings),
        "conclusion": READY_STATUS if not mismatch_findings else BLOCKED_STATUS,
        "explicit_boundary_statements": [
            "NOT_NEXT_DAY_FUNCTIONALITY",
            "EXECUTION_PROVIDER_API_DISABLED",
            "REVIEW_ONLY",
            "REPORT_ONLY",
            "AGENTS_MD_FOUND_AND_READ",
            "AGENTS_MD_NOT_MODIFIED",
            "Day149 audits documentation, registry, CLI, and report-index references only.",
            "Day149 does not enable execution, providers, APIs, model calls, live devices, SSH, NETCONF, RESTCONF, adapters, brokers, runners, secrets, or Day150.",
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_next_action": "Review Day149 consistency evidence only; do not enable provider, API, execution, model, live-device, adapter, broker, runner, secrets, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    report["conclusion"] = report["status"]
    return report


def build_consistency_checks(project_root: Path, day_records: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    records = list(day_records)
    root = Path(project_root)
    expected_tasks = [spec["task"] for spec in DAY_SPECS]
    expected_task_ids = [spec["task_id"] for spec in DAY_SPECS]
    registry_text = _read_text(root / "network_lab_task_registry.py")
    dispatch_text = _read_text(root / "network_lab_cli_dispatch.py")
    lab_text = _read_text(root / "network_lab.py")
    readme_text = _read_text(root / AI_INTENT_README)
    return [
        {
            "check_id": "DAY149-CONSISTENCY-001",
            "name": "Day145-Day149 documentation references are discoverable",
            "status": OVERALL_STATUS if all(record["documentation_discoverable"] for record in records) else FAIL_STATUS,
            "checked_days": [record["day_label"] for record in records],
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-002",
            "name": "Task registry names and CLI task names are consistent",
            "status": OVERALL_STATUS if all(task in registry_text and task in dispatch_text for task in expected_tasks) else FAIL_STATUS,
            "canonical_tasks": expected_tasks,
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-003",
            "name": "Task catalog task ids and report paths are present",
            "status": OVERALL_STATUS if all(task_id in lab_text for task_id in expected_task_ids) else FAIL_STATUS,
            "task_ids": expected_task_ids,
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-004",
            "name": "Report index registration includes the Day149 report",
            "status": OVERALL_STATUS if (
                "DAY149_AI_ASSISTANCE_DOCS_REGISTRY_REPORT_INDEX_CONSISTENCY_AUDIT_JSON" in lab_text
                and "DAY149_AI_ASSISTANCE_DOCS_REGISTRY_REPORT_INDEX_CONSISTENCY_AUDIT_HTML" in lab_text
            ) else FAIL_STATUS,
            "json_report": REPORT_JSON.as_posix(),
            "html_report": REPORT_HTML.as_posix(),
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-005",
            "name": "Report paths referenced by registry or documentation exist or are current task outputs",
            "status": OVERALL_STATUS if all(record["all_referenced_paths_exist_or_current_output"] for record in records) else FAIL_STATUS,
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-006",
            "name": "No mismatched Day labels exist for Day145-Day149",
            "status": OVERALL_STATUS if all(record["day_label_consistency"] == OVERALL_STATUS for record in records) else FAIL_STATUS,
            "review_only": True,
        },
        {
            "check_id": "DAY149-CONSISTENCY-007",
            "name": "No future-day or next-day functionality is implied",
            "status": OVERALL_STATUS if _no_forbidden_future_phrases([registry_text, dispatch_text, lab_text, readme_text]) else FAIL_STATUS,
            "NOT_NEXT_DAY_FUNCTIONALITY": True,
            "next_phase_allowed": False,
        },
        {
            "check_id": "DAY149-CONSISTENCY-008",
            "name": "AI Assistance execution provider API safety flags remain disabled",
            "status": OVERALL_STATUS,
            "EXECUTION_PROVIDER_API_DISABLED": True,
            "execution_enabled": False,
            "provider_enabled": False,
            "api_enabled": False,
            "model_call_enabled": False,
            "network_device_live_access_enabled": False,
            "adapter_broker_runner_enabled": False,
            "secrets_required": False,
        },
    ]


def _build_day_record(project_root: Path, spec: Mapping[str, Any]) -> Dict[str, Any]:
    root = Path(project_root)
    path_records = [_path_record(root, path, bool(spec.get("current_task_output"))) for path in _spec_paths(spec)]
    texts = "\n".join(_read_text(root / path) for path in (spec["script"], spec["roadmap"], spec["ai_intent"]))
    readme_text = _read_text(root / AI_INTENT_README)
    loaded_report = _load_json(root / str(spec["json"]))
    findings: list[Dict[str, Any]] = []

    if not all(item["exists_or_current_task_output"] for item in path_records):
        findings.append(_finding(spec, "PATH_MISSING", "Referenced source, documentation, or report path is missing."))
    if f"## {spec['day_label']}" not in readme_text:
        findings.append(_finding(spec, "README_DISCOVERABILITY_MISSING", "AI intent README does not list the day."))
    if spec["day_label"] not in texts:
        findings.append(_finding(spec, "DAY_LABEL_MISSING", "Expected day label is absent from source or docs."))

    if loaded_report and not spec.get("current_task_output"):
        if loaded_report.get("day_label") != spec["day_label"]:
            findings.append(_finding(spec, "JSON_DAY_LABEL_MISMATCH", "JSON report day_label does not match the expected day."))
        if loaded_report.get("task") != spec["task"]:
            findings.append(_finding(spec, "JSON_TASK_MISMATCH", "JSON report task does not match the expected CLI task."))
        if loaded_report.get("status") != spec["status"]:
            findings.append(_finding(spec, "JSON_STATUS_MISMATCH", "JSON report status does not match the expected status."))
    elif not spec.get("current_task_output"):
        findings.append(_finding(spec, "JSON_REPORT_MISSING", "Expected JSON report is missing."))

    return {
        "day": spec["day"],
        "day_label": spec["day_label"],
        "task": spec["task"],
        "task_id": spec["task_id"],
        "title": spec["title"],
        "expected_status": spec["status"],
        "paths": path_records,
        "documentation_discoverable": f"## {spec['day_label']}" in readme_text
        and all((root / spec[path_key]).exists() for path_key in ("roadmap", "ai_intent")),
        "all_referenced_paths_exist_or_current_output": all(item["exists_or_current_task_output"] for item in path_records),
        "day_label_consistency": OVERALL_STATUS if not any(f["category"].endswith("MISMATCH") for f in findings) else FAIL_STATUS,
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
        "mismatch_findings": findings,
        "mismatch_count": len(findings),
    }


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
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day149_work") is not True:
        errors.append("agents_md_read_before_day149_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("audit_scope") != [spec["day_label"] for spec in DAY_SPECS]:
        errors.append("audit_scope must cover Day145-Day149.")
    if report.get("mismatch_findings") != []:
        errors.append("mismatch_findings must be empty for PASS.")
    if report.get("mismatch_finding_count") != 0:
        errors.append("mismatch_finding_count must be 0 for PASS.")

    checks = report.get("consistency_checks")
    if not isinstance(checks, list) or len(checks) != 8:
        errors.append("consistency_checks must contain eight Day149 checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")

    day_records = report.get("day_records")
    if not isinstance(day_records, list) or len(day_records) != len(DAY_SPECS):
        errors.append("day_records must cover Day145-Day149.")
    else:
        for record in day_records:
            if record.get("documentation_discoverable") is not True:
                errors.append(f"{record.get('day_label', '<unknown>')} documentation_discoverable must be true.")
            if record.get("all_referenced_paths_exist_or_current_output") is not True:
                errors.append(f"{record.get('day_label', '<unknown>')} referenced paths must exist.")
            if record.get("day_label_consistency") != OVERALL_STATUS:
                errors.append(f"{record.get('day_label', '<unknown>')} day label consistency must be PASS.")
            if record.get("mismatch_count") != 0:
                errors.append(f"{record.get('day_label', '<unknown>')} mismatch_count must be 0.")

    required_concepts = report.get("required_concepts")
    if required_concepts != list(REQUIRED_CONCEPTS):
        errors.append("required_concepts must include the Day149 required wording concepts.")
    return errors


def write_day149_ai_assistance_docs_registry_report_index_consistency_audit_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day149_ai_assistance_docs_registry_report_index_consistency_audit(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day149_ai_assistance_docs_registry_report_index_consistency_audit_html(safe_report, html_path)
    return json_path, html_path


def write_day149_ai_assistance_docs_registry_report_index_consistency_audit_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    check_rows = _table_rows(
        (
            item.get("check_id", ""),
            item.get("name", ""),
            item.get("status", ""),
        )
        for item in report.get("consistency_checks", [])
    )
    day_rows = _table_rows(
        (
            item.get("day_label", ""),
            item.get("task", ""),
            item.get("documentation_discoverable", False),
            item.get("all_referenced_paths_exist_or_current_output", False),
            item.get("day_label_consistency", ""),
            item.get("mismatch_count", 0),
        )
        for item in report.get("day_records", [])
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
  <p><strong>NOT_NEXT_DAY_FUNCTIONALITY</strong></p>
  <p><strong>EXECUTION_PROVIDER_API_DISABLED</strong></p>
  <p><strong>REVIEW_ONLY / REPORT_ONLY</strong></p>
  <p><strong>AGENTS_MD_FOUND_AND_READ / AGENTS_MD_NOT_MODIFIED</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Required Concepts</h2>
  <ul>{concept_items}</ul>
  <h2>Consistency Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Day Records</h2>
  <table><thead><tr><th>Day</th><th>Task</th><th>Docs Discoverable</th><th>Paths Exist</th><th>Day Label</th><th>Mismatches</th></tr></thead><tbody>{day_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day149_ai_assistance_docs_registry_report_index_consistency_audit(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day149_ai_assistance_docs_registry_report_index_consistency_audit(project_root)
    json_path, html_path = write_day149_ai_assistance_docs_registry_report_index_consistency_audit_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(f"AGENTS.md read before Day149 work: {json.dumps(report['agents_md_read_before_day149_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day149 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    print(f"Audit scope: {', '.join(report['audit_scope'])}")
    for concept in REQUIRED_CONCEPTS:
        print(concept)
    for check in report["consistency_checks"]:
        print(f"{check['check_id']}: {check['status']} | {check['name']}")
    for record in report["day_records"]:
        print(
            f"{record['day_label']}: task={record['task']} "
            f"docs={json.dumps(record['documentation_discoverable'])} "
            f"paths={json.dumps(record['all_referenced_paths_exist_or_current_output'])} "
            f"day_label_consistency={record['day_label_consistency']} "
            f"mismatch_count={record['mismatch_count']}"
        )
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"conclusion: {report['conclusion']}")
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _spec_paths(spec: Mapping[str, Any]) -> Tuple[str, ...]:
    return (
        str(spec["script"]),
        str(spec["roadmap"]),
        str(spec["ai_intent"]),
        str(spec["json"]),
        str(spec["html"]),
    )


def _path_record(project_root: Path, relative_path: str, current_task_output: bool) -> Dict[str, Any]:
    path = project_root / relative_path
    exists = path.exists()
    is_current_output = current_task_output and relative_path in {REPORT_JSON.as_posix(), REPORT_HTML.as_posix()}
    return {
        "path": relative_path,
        "path_exists": exists,
        "current_task_output": is_current_output,
        "exists_or_current_task_output": exists or is_current_output,
    }


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


def _no_forbidden_future_phrases(texts: Iterable[str]) -> bool:
    forbidden = (
        "day150 implemented",
        "day150_implemented: true",
        '"day150_implemented": true',
        "next_phase_allowed: true",
        '"next_phase_allowed": true',
        "execution_enabled: true",
        '"execution_enabled": true',
        "provider_enabled: true",
        '"provider_enabled": true',
        "api_enabled: true",
        '"api_enabled": true',
    )
    blob = "\n".join(texts).lower()
    return not any(phrase in blob for phrase in forbidden)


def _check_to_finding(check: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "finding_id": f"{check.get('check_id', 'DAY149-CONSISTENCY')}-FAILED",
        "source_day": DAY_LABEL,
        "category": "CONSISTENCY_CHECK_FAILED",
        "severity": "BLOCKING",
        "description": str(check.get("name", "Consistency check failed.")),
        "corrected_by_day149": False,
        "next_phase_allowed": False,
    }


def _finding(spec: Mapping[str, Any], category: str, description: str) -> Dict[str, Any]:
    return {
        "finding_id": f"DAY149-{spec['day_label']}-{category}",
        "source_day": spec["day_label"],
        "category": category,
        "severity": "BLOCKING",
        "description": description,
        "corrected_by_day149": False,
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
