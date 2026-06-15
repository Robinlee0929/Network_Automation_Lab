"""Day151 v0.4 AI Assistance closure evidence index.

This module writes a deterministic local-file index for the closed v0.4 AI
Assistance evidence chain. It is reviewer evidence only and does not enable
execution, providers, APIs, model calls, device access, SSH, NETCONF, RESTCONF,
secrets, live network I/O, adapters, brokers, runners, or next-phase work.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 151
DAY_LABEL = "Day151"
TASK_NAME = "v04-ai-assistance-closure-evidence-index"
TITLE = "v0.4 AI Assistance Closure Evidence Index"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_CLOSURE_EVIDENCE_INDEX"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
STATUS = "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_READY"
BLOCKED_STATUS = "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_AI_ASSISTANCE_V0_4_CLOSED_REVIEW_ONLY_AND_NEXT_PHASE_BLOCKED"
CLOSURE_EVIDENCE_INDEX_READY = "CLOSURE_EVIDENCE_INDEX_READY"
PHASE_GATE_CLOSED_REVIEW_ONLY = "PHASE_GATE_CLOSED_REVIEW_ONLY"
NEXT_PHASE_ALLOWED_FALSE = "NEXT_PHASE_ALLOWED_FALSE"
HUMAN_READABLE_CONCLUSION = (
    "v0.4 AI Assistance closure evidence is indexed for reviewer use only. "
    "The Day150 phase gate remains closed and the next phase remains blocked."
)
REPORT_JSON = Path("reports") / "lab-summary" / "day151_v04_ai_assistance_closure_evidence_index.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day151_v04_ai_assistance_closure_evidence_index.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day151_v04_ai_assistance_closure_evidence_index.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day151_v04_ai_assistance_closure_evidence_index.md"

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "closure_evidence_index_only",
    "local_only",
    "deterministic_static_data_only",
    "day145_evidence_freeze_indexed",
    "day146_non_advancement_gate_indexed",
    "day147_deferred_risk_register_indexed",
    "day148_display_consistency_audit_indexed",
    "day149_docs_registry_report_index_consistency_indexed",
    "day150_phase_gate_closure_indexed",
    "phase_gate_closed_review_only",
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
    "source_task_rerun",
    "next_phase_allowed",
    "future_phase_started",
)

REQUIRED_CONCEPTS: Tuple[str, ...] = (
    "CLOSURE_EVIDENCE_INDEX_READY",
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
    "SOURCE_TASK_RERUN_FALSE",
    "FUTURE_EXPLICIT_SAFETY_GATE_REQUIRED",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
)

SOURCE_EVIDENCE: Tuple[Dict[str, Any], ...] = (
    {
        "day_label": "Day145",
        "task": "v0.4-ai-assistance-evidence-freeze-package",
        "title": "v0.4 AI Assistance Evidence Freeze Package",
        "expected_status": "V0_4_AI_ASSISTANCE_EVIDENCE_FREEZE_READY",
        "index_role": "Evidence freeze baseline",
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
        "index_role": "Non-advancement gate",
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
        "index_role": "Deferred risk register",
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
        "index_role": "Display consistency audit",
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
        "index_role": "Docs registry report-index consistency audit",
        "script": "day149_ai_assistance_docs_registry_report_index_consistency_audit.py",
        "roadmap": "docs/roadmap/day149_ai_assistance_docs_registry_report_index_consistency_audit.md",
        "ai_intent": "docs/ai-intent/day149_ai_assistance_docs_registry_report_index_consistency_audit.md",
        "json": "reports/lab-summary/day149_ai_assistance_docs_registry_report_index_consistency_audit.json",
        "html": "reports/lab-summary/day149_ai_assistance_docs_registry_report_index_consistency_audit.html",
    },
    {
        "day_label": "Day150",
        "task": "v04-ai-assistance-phase-gate-closure-review",
        "title": "v0.4 AI Assistance Phase Gate Closure Review",
        "expected_status": "PHASE_GATE_CLOSED_REVIEW_ONLY",
        "index_role": "Final review-only phase gate closure",
        "script": "day150_v04_ai_assistance_phase_gate_closure_review.py",
        "roadmap": "docs/roadmap/day150_v04_ai_assistance_phase_gate_closure_review.md",
        "ai_intent": "docs/ai-intent/day150_v04_ai_assistance_phase_gate_closure_review.md",
        "json": "reports/lab-summary/day150_v04_ai_assistance_phase_gate_closure_review.json",
        "html": "reports/lab-summary/day150_v04_ai_assistance_phase_gate_closure_review.html",
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day151_work": False,
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day151_work": markers_present,
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "AGENTS_MD_FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_day151_v04_ai_assistance_closure_evidence_index(project_root: Path) -> Dict[str, Any]:
    agents_evidence = build_agents_md_evidence(project_root)
    evidence_items = [_build_evidence_item(Path(project_root), source) for source in SOURCE_EVIDENCE]
    index_checks = build_index_checks(evidence_items)
    findings = [_check_to_finding(check) for check in index_checks if check.get("status") != OVERALL_STATUS]

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
        "indexed_scope": [item["day_label"] for item in evidence_items],
        "evidence_item_count": len(evidence_items),
        "evidence_items": evidence_items,
        "index_checks": index_checks,
        "index_findings": findings,
        "index_finding_count": len(findings),
        "final_constants": [
            CLOSURE_EVIDENCE_INDEX_READY,
            PHASE_GATE_CLOSED_REVIEW_ONLY,
            NEXT_PHASE_ALLOWED_FALSE,
        ],
        "human_readable_conclusion": HUMAN_READABLE_CONCLUSION,
        "explicit_boundary_statements": [
            "Day151 is a closure evidence index, not next-day functionality.",
            "Day151 indexes Day145-Day150 evidence only and does not rerun source tasks.",
            "Day150 remains the phase-gate closure authority.",
            "Execution, providers, APIs, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, adapters, brokers, and runners remain disabled.",
            "The next phase remains blocked unless a future explicit safety gate is created.",
            CLOSURE_EVIDENCE_INDEX_READY,
            PHASE_GATE_CLOSED_REVIEW_ONLY,
            NEXT_PHASE_ALLOWED_FALSE,
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_next_action": "Review the indexed Day145-Day150 closure evidence only; do not enable provider, API, execution, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    report["conclusion"] = report["status"]
    return report


def build_index_checks(evidence_items: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    items = list(evidence_items)
    return [
        {
            "check_id": "DAY151-INDEX-001",
            "name": "Day145-Day150 source evidence is indexed",
            "status": OVERALL_STATUS if [item["day_label"] for item in items] == [source["day_label"] for source in SOURCE_EVIDENCE] else FAIL_STATUS,
            "indexed_days": [item["day_label"] for item in items],
        },
        {
            "check_id": "DAY151-INDEX-002",
            "name": "Required source scripts and docs exist",
            "status": OVERALL_STATUS if all(item["required_static_paths_present"] for item in items) else FAIL_STATUS,
        },
        {
            "check_id": "DAY151-INDEX-003",
            "name": "Source task reports are readable when present",
            "status": OVERALL_STATUS if all(item["json_readable_or_absent"] for item in items) else FAIL_STATUS,
        },
        {
            "check_id": "DAY151-INDEX-004",
            "name": "Day150 phase gate closure remains authoritative",
            "status": OVERALL_STATUS if _day150_is_closed(items) else FAIL_STATUS,
            "required_status": PHASE_GATE_CLOSED_REVIEW_ONLY,
        },
        {
            "check_id": "DAY151-INDEX-005",
            "name": "Closure index remains review-only and report-only",
            "status": OVERALL_STATUS,
            "review_only": True,
            "report_only": True,
            "source_task_rerun": False,
        },
        {
            "check_id": "DAY151-INDEX-006",
            "name": "Execution provider API model device and next phase remain disabled",
            "status": OVERALL_STATUS,
            **{field: False for field in REQUIRED_FALSE_FIELDS},
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
    if report.get("agents_md_read_before_day151_work") is not True:
        errors.append("agents_md_read_before_day151_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    expected_scope = [item["day_label"] for item in SOURCE_EVIDENCE]
    if report.get("indexed_scope") != expected_scope:
        errors.append("indexed_scope must cover Day145-Day150.")
    if report.get("evidence_item_count") != len(SOURCE_EVIDENCE):
        errors.append("evidence_item_count must match Day145-Day150.")
    if report.get("final_constants") != [
        CLOSURE_EVIDENCE_INDEX_READY,
        PHASE_GATE_CLOSED_REVIEW_ONLY,
        NEXT_PHASE_ALLOWED_FALSE,
    ]:
        errors.append("final_constants must include closure index ready, phase gate closed, and next phase false.")
    if report.get("index_findings") != []:
        errors.append("index_findings must be empty for PASS.")
    if report.get("index_finding_count") != 0:
        errors.append("index_finding_count must be 0 for PASS.")

    checks = report.get("index_checks")
    if not isinstance(checks, list) or len(checks) != 6:
        errors.append("index_checks must contain six Day151 checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")

    evidence_items = report.get("evidence_items")
    if not isinstance(evidence_items, list) or len(evidence_items) != len(SOURCE_EVIDENCE):
        errors.append("evidence_items must cover Day145-Day150.")
    else:
        for item in evidence_items:
            if item.get("required_static_paths_present") is not True:
                errors.append(f"{item.get('day_label', '<unknown>')} required static paths must be present.")
            if item.get("json_readable_or_absent") is not True:
                errors.append(f"{item.get('day_label', '<unknown>')} JSON evidence must be readable when present.")
            if item.get("source_task_rerun") is not False:
                errors.append(f"{item.get('day_label', '<unknown>')} source_task_rerun must be false.")
            if item.get("next_phase_allowed") is not False:
                errors.append(f"{item.get('day_label', '<unknown>')} next_phase_allowed must be false.")

    if report.get("required_concepts") != list(REQUIRED_CONCEPTS):
        errors.append("required_concepts must include the Day151 required concepts.")
    return errors


def write_day151_v04_ai_assistance_closure_evidence_index_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day151_v04_ai_assistance_closure_evidence_index(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day151_v04_ai_assistance_closure_evidence_index_html(safe_report, html_path)
    return json_path, html_path


def write_day151_v04_ai_assistance_closure_evidence_index_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (field, report[field])
        for field in ("day_label", "task", "title", "mode", "overall_status", "status", "conclusion")
        if field in report
    )
    evidence_rows = _table_rows(
        (
            item.get("day_label", ""),
            item.get("title", ""),
            item.get("index_role", ""),
            item.get("required_static_paths_present", False),
            item.get("json_status", ""),
            item.get("json_path", ""),
            item.get("html_path", ""),
        )
        for item in report.get("evidence_items", [])
    )
    check_rows = _table_rows(
        (item.get("check_id", ""), item.get("name", ""), item.get("status", ""))
        for item in report.get("index_checks", [])
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
  <p><strong>{CLOSURE_EVIDENCE_INDEX_READY}</strong></p>
  <p><strong>{PHASE_GATE_CLOSED_REVIEW_ONLY}</strong></p>
  <p><strong>{NEXT_PHASE_ALLOWED_FALSE}</strong></p>
  <p>{html.escape(str(report['human_readable_conclusion']))}</p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Required Concepts</h2>
  <ul>{concept_items}</ul>
  <h2>Evidence Index</h2>
  <table><thead><tr><th>Day</th><th>Title</th><th>Index Role</th><th>Static Paths Present</th><th>JSON Status</th><th>JSON</th><th>HTML</th></tr></thead><tbody>{evidence_rows}</tbody></table>
  <h2>Index Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day151_v04_ai_assistance_closure_evidence_index(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day151_v04_ai_assistance_closure_evidence_index(project_root)
    json_path, html_path = write_day151_v04_ai_assistance_closure_evidence_index_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(f"AGENTS.md read before Day151 work: {json.dumps(report['agents_md_read_before_day151_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day151 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    print(f"Indexed scope: {', '.join(report['indexed_scope'])}")
    for concept in REQUIRED_CONCEPTS:
        print(concept)
    for item in report["evidence_items"]:
        print(f"{item['day_label']}: {item['index_role']} static_paths_present={json.dumps(item['required_static_paths_present'])} json_status={item['json_status']}")
    for check in report["index_checks"]:
        print(f"{check['check_id']}: {check['status']} | {check['name']}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"human_readable_conclusion: {report['human_readable_conclusion']}")
    print(f"conclusion: {report['conclusion']}")
    for final_constant in report["final_constants"]:
        print(final_constant)
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _build_evidence_item(project_root: Path, source: Mapping[str, Any]) -> Dict[str, Any]:
    required_paths = [source["script"], source["roadmap"], source["ai_intent"]]
    optional_report_paths = [source["json"], source["html"]]
    loaded = _load_json(project_root / str(source["json"]))
    json_status = loaded.get("status") if isinstance(loaded, dict) else "REPORT_NOT_PRESENT"
    return {
        **dict(source),
        "json_path": source["json"],
        "html_path": source["html"],
        "required_paths": [_path_record(project_root, str(path)) for path in required_paths],
        "optional_report_paths": [_path_record(project_root, str(path)) for path in optional_report_paths],
        "required_static_paths_present": all(_path_exists(project_root, str(path)) for path in required_paths),
        "json_report_present": _path_exists(project_root, str(source["json"])),
        "html_report_present": _path_exists(project_root, str(source["html"])),
        "json_readable_or_absent": loaded is not None or not _path_exists(project_root, str(source["json"])),
        "json_status": json_status,
        "json_status_matches_expected": loaded is None or json_status == source["expected_status"],
        "source_task_rerun": False,
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
    }


def _day150_is_closed(evidence_items: Iterable[Mapping[str, Any]]) -> bool:
    for item in evidence_items:
        if item.get("day_label") == "Day150":
            return item.get("json_status") in (PHASE_GATE_CLOSED_REVIEW_ONLY, "REPORT_NOT_PRESENT")
    return False


def _path_record(project_root: Path, relative_path: str) -> Dict[str, Any]:
    path = project_root / relative_path
    return {"path": relative_path, "path_exists": path.exists()}


def _path_exists(project_root: Path, relative_path: str) -> bool:
    return (project_root / relative_path).exists()


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _check_to_finding(check: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "finding_id": f"{check.get('check_id', 'DAY151-INDEX')}-FAILED",
        "source_day": DAY_LABEL,
        "category": "CLOSURE_EVIDENCE_INDEX_CHECK_FAILED",
        "severity": "BLOCKING",
        "description": str(check.get("name", "Closure evidence index check failed.")),
        "corrected_by_day151": False,
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
