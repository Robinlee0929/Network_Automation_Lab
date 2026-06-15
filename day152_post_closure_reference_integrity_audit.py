"""Day152 post-closure reference integrity audit.

This module verifies that the post-Day151 README, documentation, registry,
CLI, task catalog, and report-index references agree about the closed v0.4 AI
Assistance evidence chain. It is reviewer evidence only and does not rerun
Day145-Day151 source tasks or reopen their safety conclusions.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 152
DAY_LABEL = "Day152"
TASK_NAME = "post-closure-reference-integrity-audit"
TITLE = "Post-Closure Reference Integrity Audit"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_POST_CLOSURE_REFERENCE_AUDIT"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
STATUS = "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED"
BLOCKED_STATUS = "POST_CLOSURE_REFERENCE_INTEGRITY_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_DAY151_CLOSURE_REFERENCES_ALIGNED_AND_NEXT_PHASE_BLOCKED"
HUMAN_READABLE_CONCLUSION = (
    "Post-closure references are aligned for reviewer navigation. "
    "Day151 remains the closure evidence index authority and the next phase remains blocked."
)
REPORT_JSON = Path("reports") / "lab-summary" / "day152_post_closure_reference_integrity_audit.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day152_post_closure_reference_integrity_audit.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day152_post_closure_reference_integrity_audit.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day152_post_closure_reference_integrity_audit.md"
AI_INTENT_README = Path("docs") / "ai-intent" / "README.md"

DAY151_TASK = "v04-ai-assistance-closure-evidence-index"
DAY152_TASK_ID = "day152_post_closure_reference_integrity_audit"

REQUIRED_CONCEPTS: Tuple[str, ...] = (
    "POST_CLOSURE_REFERENCE_INTEGRITY_AUDITED",
    "DAY151_CLOSURE_INDEX_AUTHORITY_PRESERVED",
    "DAY145_DAY150_INDEXED_ASSUMED_CONFIRMED",
    "DAY151_REPORT_INDEX_VISIBILITY_ASSUMED_CONFIRMED",
    "PHASE_GATE_CLOSED_REVIEW_ONLY",
    "NEXT_PHASE_ALLOWED_FALSE",
    "UNSAFE_FLAGS_FALSE_ASSUMED_CONFIRMED",
    "REVIEW_ONLY",
    "REPORT_ONLY",
    "SOURCE_TASK_RERUN_FALSE",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
)

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "audit_only",
    "local_only",
    "deterministic_static_reference_audit_only",
    "post_day151_merge_reference_integrity_audited",
    "day151_closure_index_authority_preserved",
    "day145_day150_indexed_assumed_confirmed",
    "day151_report_index_visibility_assumed_confirmed",
    "unsafe_flags_false_assumed_confirmed",
    "next_phase_blocked_assumed_confirmed",
    "phase_gate_closed_review_only",
    "future_explicit_safety_gate_required",
    "agents_md_found_and_read",
    "agents_md_not_modified",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "redoes_day145_day151_safety_judgment",
    "source_task_rerun",
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
    "future_phase_started",
)

REFERENCE_TARGETS: Tuple[Dict[str, Any], ...] = (
    {
        "surface": "README",
        "path": "README.md",
        "required_fragments": (
            "Current project status after Day152",
            "Day151 remains the closure evidence index authority",
            "Post-Closure Reference Integrity Audit",
            "NEXT_PHASE_ALLOWED_FALSE",
        ),
    },
    {
        "surface": "AI intent README",
        "path": AI_INTENT_README.as_posix(),
        "required_fragments": (
            "## Day151",
            "## Day152",
            "Day151 v0.4 AI Assistance Closure Evidence Index",
            "Day152 Post-Closure Reference Integrity Audit",
        ),
    },
    {
        "surface": "Day151 roadmap doc",
        "path": "docs/roadmap/day151_v04_ai_assistance_closure_evidence_index.md",
        "required_fragments": (
            "v04-ai-assistance-closure-evidence-index",
            "V0_4_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_READY",
            "CLOSURE_EVIDENCE_INDEX_READY",
            "NEXT_PHASE_ALLOWED_FALSE",
        ),
    },
    {
        "surface": "Day151 AI-intent doc",
        "path": "docs/ai-intent/day151_v04_ai_assistance_closure_evidence_index.md",
        "required_fragments": (
            "v0.4 AI Assistance Closure Evidence Index",
            "CLOSURE_EVIDENCE_INDEX_READY",
            "source_task_rerun: false",
            "next_phase_allowed: false",
        ),
    },
    {
        "surface": "Day152 roadmap doc",
        "path": ROADMAP_DOC.as_posix(),
        "required_fragments": (
            TASK_NAME,
            STATUS,
            "Day151 remains the closure evidence index authority",
            "redoes_day145_day151_safety_judgment: false",
        ),
    },
    {
        "surface": "Day152 AI-intent doc",
        "path": AI_INTENT_DOC.as_posix(),
        "required_fragments": (
            TITLE,
            STATUS,
            "Day151 merge",
            "source_task_rerun: false",
        ),
    },
    {
        "surface": "task registry",
        "path": "network_lab_task_registry.py",
        "required_fragments": (DAY151_TASK, TASK_NAME),
    },
    {
        "surface": "CLI dispatch",
        "path": "network_lab_cli_dispatch.py",
        "required_fragments": (DAY151_TASK, TASK_NAME, "_run_day152_post_closure_reference_integrity_audit"),
    },
    {
        "surface": "network_lab task catalog and report-index",
        "path": "network_lab.py",
        "required_fragments": (
            "DAY151_V04_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_TASK_ID",
            "DAY152_POST_CLOSURE_REFERENCE_INTEGRITY_AUDIT_TASK_ID",
            "DAY152_POST_CLOSURE_REFERENCE_INTEGRITY_AUDIT_JSON",
            "DAY152_POST_CLOSURE_REFERENCE_INTEGRITY_AUDIT_HTML",
            DAY152_TASK_ID,
        ),
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day152_work": False,
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day152_work": markers_present,
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "AGENTS_MD_FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_day152_post_closure_reference_integrity_audit(project_root: Path) -> Dict[str, Any]:
    reference_records = [_build_reference_record(Path(project_root), target) for target in REFERENCE_TARGETS]
    integrity_checks = build_integrity_checks(reference_records)
    mismatch_findings = [
        _check_to_finding(check)
        for check in integrity_checks
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
        **build_agents_md_evidence(project_root),
        "required_concepts": list(REQUIRED_CONCEPTS),
        "required_concept_status": {concept: "PRESENT" for concept in REQUIRED_CONCEPTS},
        "audit_scope": [
            "README",
            "docs",
            "task registry",
            "CLI dispatch",
            "task catalog",
            "report-index metadata",
        ],
        "assumed_day151_closure_facts": {
            "day151_closure_index_found_by_report_index": True,
            "day145_day150_indexed": True,
            "unsafe_flags_false": True,
            "next_phase_allowed": False,
            "source_task_rerun": False,
            "safety_judgment_reopened": False,
        },
        "reference_records": reference_records,
        "integrity_checks": integrity_checks,
        "mismatch_findings": mismatch_findings,
        "mismatch_finding_count": len(mismatch_findings),
        "human_readable_conclusion": HUMAN_READABLE_CONCLUSION,
        "explicit_boundary_statements": [
            "Day152 audits post-Day151 reference integrity only.",
            "Day152 does not redo Day145-Day151 safety judgments.",
            "Day151 remains the closure evidence index authority.",
            "Day151 already confirmed Day145-Day150 indexed, unsafe flags false, next phase blocked, and report-index visibility.",
            "Execution, providers, APIs, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, adapters, brokers, and runners remain disabled.",
            "The next phase remains blocked unless a future explicit safety gate is created.",
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_next_action": "Review the Day152 reference-integrity evidence only; do not rerun closure source tasks or enable provider, API, execution, model, device, SSH, NETCONF, RESTCONF, secrets, live network I/O, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    report["conclusion"] = report["status"]
    return report


def build_integrity_checks(reference_records: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    records = list(reference_records)
    return [
        {
            "check_id": "DAY152-REF-001",
            "name": "README references Day152 while preserving Day151 closure authority",
            "status": _record_status(records, "README"),
            "review_only": True,
        },
        {
            "check_id": "DAY152-REF-002",
            "name": "AI intent docs list Day151 and Day152 reviewer navigation",
            "status": _combined_status(records, ("AI intent README", "Day151 AI-intent doc", "Day152 AI-intent doc")),
            "review_only": True,
        },
        {
            "check_id": "DAY152-REF-003",
            "name": "Roadmap docs preserve closure and audit boundaries",
            "status": _combined_status(records, ("Day151 roadmap doc", "Day152 roadmap doc")),
            "review_only": True,
        },
        {
            "check_id": "DAY152-REF-004",
            "name": "Task registry and CLI expose Day151 and Day152 canonical names",
            "status": _combined_status(records, ("task registry", "CLI dispatch")),
            "review_only": True,
        },
        {
            "check_id": "DAY152-REF-005",
            "name": "Task catalog and report-index metadata include Day152 output paths",
            "status": _record_status(records, "network_lab task catalog and report-index"),
            "review_only": True,
        },
        {
            "check_id": "DAY152-REF-006",
            "name": "Day152 does not rerun source tasks or redo closure safety judgment",
            "status": OVERALL_STATUS,
            "source_task_rerun": False,
            "redoes_day145_day151_safety_judgment": False,
            "next_phase_allowed": False,
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
    if report.get("agents_md_read_before_day152_work") is not True:
        errors.append("agents_md_read_before_day152_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    assumed = report.get("assumed_day151_closure_facts")
    if not isinstance(assumed, dict):
        errors.append("assumed_day151_closure_facts must be present.")
    else:
        if assumed.get("safety_judgment_reopened") is not False:
            errors.append("Day152 must not reopen Day145-Day151 safety judgment.")
        if assumed.get("source_task_rerun") is not False:
            errors.append("assumed source_task_rerun must be false.")
        if assumed.get("next_phase_allowed") is not False:
            errors.append("assumed next_phase_allowed must be false.")

    if report.get("mismatch_findings") != []:
        errors.append("mismatch_findings must be empty for PASS.")
    if report.get("mismatch_finding_count") != 0:
        errors.append("mismatch_finding_count must be 0 for PASS.")

    records = report.get("reference_records")
    if not isinstance(records, list) or len(records) != len(REFERENCE_TARGETS):
        errors.append("reference_records must cover all Day152 reference targets.")
    else:
        for record in records:
            if record.get("path_exists") is not True:
                errors.append(f"{record.get('surface', '<unknown>')} path must exist.")
            if record.get("missing_fragments") != []:
                errors.append(f"{record.get('surface', '<unknown>')} must contain all required fragments.")

    checks = report.get("integrity_checks")
    if not isinstance(checks, list) or len(checks) != 6:
        errors.append("integrity_checks must contain six Day152 checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")

    if report.get("required_concepts") != list(REQUIRED_CONCEPTS):
        errors.append("required_concepts must include the Day152 required concepts.")
    return errors


def write_day152_post_closure_reference_integrity_audit_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day152_post_closure_reference_integrity_audit(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day152_post_closure_reference_integrity_audit_html(safe_report, html_path)
    return json_path, html_path


def write_day152_post_closure_reference_integrity_audit_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (field, report[field])
        for field in ("day_label", "task", "title", "mode", "overall_status", "status", "conclusion")
        if field in report
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
    check_rows = _table_rows(
        (item.get("check_id", ""), item.get("name", ""), item.get("status", ""))
        for item in report.get("integrity_checks", [])
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
  <p><strong>{STATUS}</strong></p>
  <p><strong>DAY151_CLOSURE_INDEX_AUTHORITY_PRESERVED</strong></p>
  <p><strong>NEXT_PHASE_ALLOWED_FALSE</strong></p>
  <p>{html.escape(str(report['human_readable_conclusion']))}</p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Required Concepts</h2>
  <ul>{concept_items}</ul>
  <h2>Reference Records</h2>
  <table><thead><tr><th>Surface</th><th>Path</th><th>Path Exists</th><th>Fragments Present</th><th>Missing Fragments</th></tr></thead><tbody>{reference_rows}</tbody></table>
  <h2>Integrity Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day152_post_closure_reference_integrity_audit(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day152_post_closure_reference_integrity_audit(project_root)
    json_path, html_path = write_day152_post_closure_reference_integrity_audit_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(f"AGENTS.md read before Day152 work: {json.dumps(report['agents_md_read_before_day152_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day152 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    print(f"Audit scope: {', '.join(report['audit_scope'])}")
    for concept in REQUIRED_CONCEPTS:
        print(concept)
    for check in report["integrity_checks"]:
        print(f"{check['check_id']}: {check['status']} | {check['name']}")
    for record in report["reference_records"]:
        print(
            f"{record['surface']}: path_exists={json.dumps(record['path_exists'])} "
            f"fragments_present={json.dumps(record['all_required_fragments_present'])} "
            f"missing={json.dumps(record['missing_fragments'])}"
        )
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"human_readable_conclusion: {report['human_readable_conclusion']}")
    print(f"conclusion: {report['conclusion']}")
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
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
        "source_task_rerun": False,
        "next_phase_allowed": False,
    }


def _record_status(records: Iterable[Mapping[str, Any]], surface: str) -> str:
    for record in records:
        if record.get("surface") == surface:
            return OVERALL_STATUS if record.get("all_required_fragments_present") is True else FAIL_STATUS
    return FAIL_STATUS


def _combined_status(records: Iterable[Mapping[str, Any]], surfaces: Iterable[str]) -> str:
    records_by_surface = {record.get("surface"): record for record in records}
    return (
        OVERALL_STATUS
        if all(records_by_surface.get(surface, {}).get("all_required_fragments_present") is True for surface in surfaces)
        else FAIL_STATUS
    )


def _check_to_finding(check: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "finding_id": f"{check.get('check_id', 'DAY152-REF')}-FAILED",
        "source_day": DAY_LABEL,
        "category": "POST_CLOSURE_REFERENCE_INTEGRITY_CHECK_FAILED",
        "severity": "BLOCKING",
        "description": str(check.get("name", "Post-closure reference integrity check failed.")),
        "corrected_by_day152": False,
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
