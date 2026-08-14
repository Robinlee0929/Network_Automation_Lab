"""Day154 post-closure evidence baseline lock review.

This module records the post-closure evidence baseline after Day145-Day153 and
drafts the current SDD operating contract. It is review-only/report-only
evidence and does not unlock execution, providers, APIs, model calls, live
device access, adapters, brokers, runners, or the next phase.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 154
DAY_LABEL = "Day154"
TASK_NAME = "post-closure-evidence-baseline-lock-review"
TITLE = "Post-Closure Evidence Baseline Lock Review + SDD Operating Contract Draft"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "review-only / report-only"
OVERALL_STATUS = "PASS"
STATUS = "REVIEW_READY"
FAIL_STATUS = "FAIL"
BLOCKED_STATUS = "BLOCKED"
FINAL_RECOMMENDATION = "KEEP_POST_CLOSURE_BASELINE_LOCKED_AND_NEXT_PHASE_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "day154_post_closure_evidence_baseline_lock_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day154_post_closure_evidence_baseline_lock_review.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day154_post_closure_evidence_baseline_lock_review.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day154_post_closure_evidence_baseline_lock_review.md"
AI_INTENT_README = Path("docs") / "ai-intent" / "README.md"

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "continues_day153",
    "evidence_first_required",
    "phase_gate_required",
    "agents_md_found_and_read",
    "agents_md_not_modified",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "new_feature",
    "touches_execution",
    "touches_provider",
    "touches_api",
    "touches_model_call",
    "touches_live_device",
    "day153_supplement",
    "next_day_feature",
    "next_phase_allowed",
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "model_call_allowed",
    "live_device_allowed",
    "adapter_allowed",
    "broker_allowed",
    "runner_allowed",
    "ssh_allowed",
    "secrets_allowed",
)

SDD_CONTRACT_REQUIRED_VALUES: Dict[str, Any] = {
    "contract_type": "draft",
    "purpose": "operating contract for SDD-style review/report-only governance",
    "execution_allowed": False,
    "provider_allowed": False,
    "api_allowed": False,
    "model_call_allowed": False,
    "live_device_allowed": False,
    "evidence_first_required": True,
    "phase_gate_required": True,
    "agents_md_pre_read_required": True,
}

REFERENCE_TARGETS: Tuple[Dict[str, Any], ...] = (
    {
        "surface": "README",
        "path": "README.md",
        "required_fragments": (
            "## Current Release Status",
            "Stage-0 Network Automation Lab",
            "Workflow Version 2",
            "DEFERRED_SECURITY_RESEARCH_BLOCKED",
            "WF-01-03C through WF-01-03F",
        ),
    },
    {
        "surface": "AI intent README",
        "path": AI_INTENT_README.as_posix(),
        "required_fragments": (
            "## Day154",
            "Day154 Post-Closure Evidence Baseline Lock Review",
            "SDD Operating Contract Draft",
        ),
    },
    {
        "surface": "Day154 roadmap doc",
        "path": ROADMAP_DOC.as_posix(),
        "required_fragments": (
            TASK_NAME,
            "POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY",
            "next_phase_allowed: false",
            "day153_supplement: false",
            "next_day_feature: false",
        ),
    },
    {
        "surface": "Day154 AI-intent doc",
        "path": AI_INTENT_DOC.as_posix(),
        "required_fragments": (
            TITLE,
            "contract_type: draft",
            "execution_allowed: false",
            "provider_allowed: false",
            "model_call_allowed: false",
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
        "required_fragments": (TASK_NAME, "_run_day154_post_closure_evidence_baseline_lock_review"),
    },
    {
        "surface": "network_lab task catalog and report-index",
        "path": "network_lab.py",
        "required_fragments": (
            "DAY154_POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_TASK_ID",
            "DAY154_POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_JSON",
            "DAY154_POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_HTML",
            "day154_post_closure_evidence_baseline_lock_review",
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


def build_day154_post_closure_evidence_baseline_lock_review(project_root: Path) -> Dict[str, Any]:
    reference_records = [_build_reference_record(Path(project_root), target) for target in REFERENCE_TARGETS]
    lock_checks = build_lock_checks(reference_records)
    sdd_contract = build_sdd_operating_contract_draft()
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
        "frozen_evidence": [
            "Day145 v0.4 AI Assistance evidence freeze package remains frozen.",
            "Day146 non-advancement gate remains authoritative for blocked advancement.",
            "Day147 deferred risk register remains deferred and locked.",
            "Day148 display consistency audit remains review-only evidence.",
            "Day149 docs/registry/report-index consistency audit remains preserved.",
            "Day150 phase gate closure review remains closed as review-only/report-only.",
            "Day151 closure evidence index remains the closure navigation authority.",
            "Day152 post-closure reference integrity audit remains preserved.",
            "Day153 forbidden capability reference scan remains the latest preserved scan evidence.",
        ],
        "preserved_references": [
            "README post-closure status summary.",
            "docs/ai-intent reviewer index through Day154.",
            "Day145-Day153 AI-intent and roadmap evidence references.",
            "network_lab task catalog and report-index metadata for Day154 registration.",
        ],
        "forbidden_capabilities": [
            "execution",
            "provider",
            "API",
            "model call",
            "live device access",
            "SSH",
            "RouterOS or network device interaction",
            "external service calls",
            "credentials or secrets",
            "adapters, brokers, runners, or runtime execution capability",
        ],
        "blocked_or_deferred_future_work": [
            "Day155 and all future-day functionality remain blocked.",
            "Execution/provider/API enablement remains blocked pending a future explicit safety gate.",
            "Model calls and live AI/provider behavior remain blocked.",
            "Live device access, SSH, RouterOS, adapter, broker, and runner work remain blocked.",
            "Deferred Day147 risks remain deferred and are not resolved by Day154.",
        ],
        "next_phase_allowed_rationale": (
            "Day154 only records the already-closed post-closure baseline and drafts operating rules; "
            "it provides no approval, implementation, or safety gate that could set next_phase_allowed=true."
        ),
        "no_unlock_rationale": (
            "The Day154 work adds reviewer evidence, documentation, metadata, and tests only. It does not "
            "create provider configuration, API clients, model invocation paths, execution handlers, live "
            "adapters, SSH access, external calls, credentials, or runtime behavior."
        ),
        "scope_boundary_rationale": (
            "Day154 continues the post-Day153 review chain by recording the baseline lock. It is not a "
            "Day153 supplement because it does not repair, amend, or rerun Day153 evidence, and it is not "
            "a next-day feature because it introduces no future functionality."
        ),
        "sdd_operating_contract_draft": sdd_contract,
        "reference_records": reference_records,
        "lock_checks": lock_checks,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "final_recommendation": FINAL_RECOMMENDATION,
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    if report["validation_errors"]:
        report["overall_status"] = FAIL_STATUS
        report["status"] = BLOCKED_STATUS
    return report


def build_sdd_operating_contract_draft() -> Dict[str, Any]:
    return {
        **SDD_CONTRACT_REQUIRED_VALUES,
        "review_only_report_only_first": True,
        "no_execution_provider_api_enablement": True,
        "no_model_call": True,
        "no_live_device_access": True,
        "blocked_future_work_must_remain_blocked": True,
        "next_phase_allowed": False,
        "codex_task_rules": [
            "Every Codex task must state whether AGENTS.md was read before work.",
            "Every applicable Codex task must explicitly state that it is not the next-day feature.",
            "Every Codex task must explicitly state that it does not open execution / provider / API.",
        ],
    }


def build_lock_checks(reference_records: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    records = list(reference_records)
    return [
        {
            "check_id": "DAY154-LOCK-001",
            "name": "Day145-Day153 evidence baseline is summarized as frozen or preserved",
            "status": OVERALL_STATUS,
            "next_phase_allowed": False,
        },
        {
            "check_id": "DAY154-LOCK-002",
            "name": "Forbidden capabilities remain explicitly denied",
            "status": OVERALL_STATUS,
            "touches_execution": False,
            "touches_provider": False,
            "touches_api": False,
            "touches_model_call": False,
            "touches_live_device": False,
        },
        {
            "check_id": "DAY154-LOCK-003",
            "name": "Future work remains blocked or deferred",
            "status": OVERALL_STATUS,
            "next_day_feature": False,
            "next_phase_allowed": False,
        },
        {
            "check_id": "DAY154-LOCK-004",
            "name": "SDD operating contract draft keeps review/report-only governance",
            "status": OVERALL_STATUS,
            "contract_type": "draft",
            "execution_allowed": False,
            "provider_allowed": False,
            "api_allowed": False,
        },
        {
            "check_id": "DAY154-LOCK-005",
            "name": "Day154 registration references are visible",
            "status": _combined_status(
                records,
                (
                    "README",
                    "AI intent README",
                    "Day154 roadmap doc",
                    "Day154 AI-intent doc",
                    "task registry",
                    "CLI dispatch",
                    "network_lab task catalog and report-index",
                ),
            ),
            "report_only": True,
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

    contract = report.get("sdd_operating_contract_draft")
    if not isinstance(contract, dict):
        errors.append("sdd_operating_contract_draft must be present.")
    else:
        for field, expected in SDD_CONTRACT_REQUIRED_VALUES.items():
            if contract.get(field) != expected:
                errors.append(f"sdd_operating_contract_draft.{field} must be {expected}.")
        if contract.get("next_phase_allowed") is not False:
            errors.append("sdd_operating_contract_draft.next_phase_allowed must be false.")

    records = report.get("reference_records")
    if not isinstance(records, list) or len(records) != len(REFERENCE_TARGETS):
        errors.append("reference_records must cover all Day154 reference targets.")
    else:
        for record in records:
            if record.get("path_exists") is not True:
                errors.append(f"{record.get('surface', '<unknown>')} path must exist.")
            if record.get("missing_fragments") != []:
                errors.append(f"{record.get('surface', '<unknown>')} must contain all required fragments.")
            if record.get("next_phase_allowed") is not False:
                errors.append(f"{record.get('surface', '<unknown>')} next_phase_allowed must be false.")

    checks = report.get("lock_checks")
    if not isinstance(checks, list) or len(checks) != 5:
        errors.append("lock_checks must contain five Day154 checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")
            if check.get("next_phase_allowed", False) is not False:
                errors.append(f"{check.get('check_id', '<unknown>')} next_phase_allowed must be false.")

    for field in ("frozen_evidence", "preserved_references", "forbidden_capabilities", "blocked_or_deferred_future_work"):
        if not isinstance(report.get(field), list) or not report.get(field):
            errors.append(f"{field} must be a non-empty list.")
    return errors


def write_day154_post_closure_evidence_baseline_lock_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day154_post_closure_evidence_baseline_lock_review(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day154_post_closure_evidence_baseline_lock_review_html(safe_report, html_path)
    return json_path, html_path


def write_day154_post_closure_evidence_baseline_lock_review_html(
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
            "new_feature",
            "touches_execution",
            "touches_provider",
            "touches_api",
            "touches_model_call",
            "touches_live_device",
            "continues_day153",
            "day153_supplement",
            "next_day_feature",
            "next_phase_allowed",
        )
    )
    contract_rows = _table_rows(report["sdd_operating_contract_draft"].items())
    check_rows = _table_rows(
        (item.get("check_id", ""), item.get("name", ""), item.get("status", ""))
        for item in report.get("lock_checks", [])
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
  <p><strong>POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY</strong></p>
  <p><strong>SDD Operating Contract Draft</strong></p>
  <p><strong>next_phase_allowed=false</strong></p>
  <p>{html.escape(str(report['next_phase_allowed_rationale']))}</p>
  <h2>Day154 Status Ideas</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>SDD Operating Contract Draft</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{contract_rows}</tbody></table>
  <h2>Lock Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Reference Records</h2>
  <table><thead><tr><th>Surface</th><th>Path</th><th>Path Exists</th><th>Fragments Present</th><th>Missing Fragments</th></tr></thead><tbody>{reference_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day154_post_closure_evidence_baseline_lock_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day154_post_closure_evidence_baseline_lock_review(project_root)
    json_path, html_path = write_day154_post_closure_evidence_baseline_lock_review_reports(project_root, report)
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
        "new_feature",
        "touches_execution",
        "touches_provider",
        "touches_api",
        "touches_model_call",
        "touches_live_device",
        "continues_day153",
        "day153_supplement",
        "next_day_feature",
        "next_phase_allowed",
    ):
        print(f"{field}: {_json_value(report[field])}")
    print("SDD Operating Contract Draft:")
    for field in SDD_CONTRACT_REQUIRED_VALUES:
        print(f"{field}: {_json_value(report['sdd_operating_contract_draft'][field])}")
    for check in report["lock_checks"]:
        print(f"{check['check_id']}: {check['status']} | {check['name']}")
    print(f"next_phase_allowed_rationale: {report['next_phase_allowed_rationale']}")
    print(f"no_unlock_rationale: {report['no_unlock_rationale']}")
    print(f"scope_boundary_rationale: {report['scope_boundary_rationale']}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_READY")
        return 0

    print(f"{format_status(FAIL_STATUS)} POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_BLOCKED")
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


def _combined_status(records: Iterable[Mapping[str, Any]], surfaces: Iterable[str]) -> str:
    records_by_surface = {record.get("surface"): record for record in records}
    return (
        OVERALL_STATUS
        if all(records_by_surface.get(surface, {}).get("all_required_fragments_present") is True for surface in surfaces)
        else FAIL_STATUS
    )


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
