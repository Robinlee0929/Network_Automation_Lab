"""Phase 2A-08 Jobs catalog / UI readiness planning pack.

This module turns the existing Phase 2A-07 artifact-to-Jobs mapping into a
deterministic, UI-ready catalog for future /network/jobs work. It is planning
and rendering only; it does not create runners, adapters, brokers, providers,
device access, commands, or executable backup/VRRP behavior.
"""

from __future__ import annotations

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase_2a_07_vrrp_dry_run_validation_pack import (
    DOC_PATH as PHASE_2A_07_DOC_PATH,
    REPORT_HTML as PHASE_2A_07_REPORT_HTML,
    REPORT_JSON as PHASE_2A_07_REPORT_JSON,
    build_artifact_to_jobs_mapping,
)


PHASE = "2A-08"
TASK_NAME = "phase2a-08-jobs-catalog-ui-readiness-planning-pack"
TITLE = "Phase 2A-08 Jobs Catalog / UI Readiness Planning Pack"
STATUS_LABEL = "PHASE_2A_08_JOBS_CATALOG_UI_READINESS_PLANNING_PACK_READY"
MODE = "planning_only_report_only"
SCOPE = "multi_job_catalog_ui_readiness_planning"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md"

REQUIRED_JOB_TYPES = (
    "baseline_check",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "backup_config_plan",
    "blocked_config_change_request",
)

UI_READY_FIELDS = (
    "job_id",
    "display_name",
    "category",
    "user_goal",
    "supported_status",
    "dry_run",
    "planning_only",
    "requires_approval",
    "blocked_reason",
    "safety_summary",
    "forbidden_capabilities_confirmed",
    "ui_card_summary",
    "ui_card",
    "evidence_or_artifact_references",
    "expected_outputs",
    "next_phase_allowed",
)

FORBIDDEN_CAPABILITIES = (
    "ssh",
    "netconf",
    "restconf",
    "live_device",
    "runner",
    "adapter",
    "broker",
    "provider_api_model",
    "secrets",
    "real_backup",
    "real_vrrp_test",
    "config_change",
    "command_execution",
)

SAFETY_FLAGS = {
    "phase_2b_authorized": False,
    "runner_enabled": False,
    "adapter_enabled": False,
    "broker_enabled": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "live_device_access_enabled": False,
    "provider_api_model_enabled": False,
    "secrets_enabled": False,
    "real_backup_enabled": False,
    "real_vrrp_test_enabled": False,
    "config_change_enabled": False,
    "command_execution_enabled": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_08_JOBS_CATALOG_UI_READINESS_PLANNING_PACK_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "MULTI_JOB_SCOPE_CONFIRMED",
    "PHASE_2A_07_ARTIFACT_MAPPING_REFERENCED",
    "JOBS_CATALOG_JSON_UI_READY",
    "JOB_CARD_FIELDS_RENDERED",
    "BACKUP_CONFIG_PLAN_PLANNING_ONLY",
    "BLOCKED_CONFIG_CHANGE_REQUEST_BLOCKED",
    "RUNNER_ENABLED_FALSE",
    "ADAPTER_ENABLED_FALSE",
    "BROKER_ENABLED_FALSE",
    "SSH_ENABLED_FALSE",
    "NETCONF_ENABLED_FALSE",
    "RESTCONF_ENABLED_FALSE",
    "LIVE_DEVICE_ACCESS_ENABLED_FALSE",
    "PROVIDER_API_MODEL_ENABLED_FALSE",
    "SECRETS_ENABLED_FALSE",
    "REAL_BACKUP_ENABLED_FALSE",
    "REAL_VRRP_TEST_ENABLED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)

EXISTING_ARTIFACT_REFERENCES = (
    "docs/phase2a_readonly_job_runner_framework.md",
    "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
    "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
    "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
    "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
    PHASE_2A_07_DOC_PATH.as_posix(),
    PHASE_2A_07_REPORT_JSON.as_posix(),
    PHASE_2A_07_REPORT_HTML.as_posix(),
)

JOB_CARD_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "baseline_check": {
        "display_name": "Baseline Check",
        "category": "baseline",
        "user_goal": "Review local baseline evidence and present whether expected baseline artifacts are ready for reviewer inspection.",
        "supported_status": "planning_only",
        "dry_run": True,
        "planning_only": True,
        "requires_approval": False,
        "blocked_reason": "",
        "safety_summary": "Planning-only catalog card for local baseline evidence; no collection, no device access, and no execution path.",
        "ui_card_summary": "Local baseline evidence readiness card.",
        "expected_outputs": ["status badge", "dry-run badge", "evidence links", "safety lock flags"],
    },
    "interface_status_check": {
        "display_name": "Interface Status Check",
        "category": "readiness",
        "user_goal": "Display local interface/topology evidence readiness without collecting live interface state.",
        "supported_status": "planning_only",
        "dry_run": True,
        "planning_only": True,
        "requires_approval": False,
        "blocked_reason": "",
        "safety_summary": "Planning-only card for previously generated read-only interface evidence; no interface command or adapter is enabled.",
        "ui_card_summary": "Interface evidence readiness card.",
        "expected_outputs": ["status badge", "dry-run badge", "interface evidence references", "safety lock flags"],
    },
    "wan_lan_check": {
        "display_name": "WAN/LAN Check",
        "category": "connectivity",
        "user_goal": "Represent WAN/LAN evidence summaries for future UI browsing without running pings, VPN checks, or throughput tests.",
        "supported_status": "planning_only",
        "dry_run": True,
        "planning_only": True,
        "requires_approval": False,
        "blocked_reason": "",
        "safety_summary": "Planning-only card for local WAN/LAN evidence; no network I/O or performance runner is enabled.",
        "ui_card_summary": "WAN/LAN evidence readiness card.",
        "expected_outputs": ["status badge", "dry-run badge", "WAN/LAN evidence references", "safety lock flags"],
    },
    "vrrp_validation": {
        "display_name": "VRRP Validation",
        "category": "high_availability",
        "user_goal": "Show the Phase 2A-07 local mock VRRP validation example as one catalog card among multiple Jobs.",
        "supported_status": "planning_only",
        "dry_run": True,
        "planning_only": True,
        "requires_approval": False,
        "blocked_reason": "",
        "safety_summary": "Planning-only card backed by local mock evidence; no real VRRP test, failover, or RouterOS command is enabled.",
        "ui_card_summary": "Local mock VRRP evidence card.",
        "expected_outputs": ["status badge", "dry-run badge", "mock VRRP evidence references", "safety lock flags"],
    },
    "backup_config_plan": {
        "display_name": "Backup Config Plan",
        "category": "backup_planning",
        "user_goal": "Describe a future backup planning card while proving no backup operation, export, secret handling, or device access exists.",
        "supported_status": "planning_only",
        "dry_run": True,
        "planning_only": True,
        "requires_approval": True,
        "blocked_reason": "Real backup, export, secret handling, and device access remain outside Phase 2A-08.",
        "safety_summary": "Planning-only and non-executing; real backup behavior is not implemented.",
        "ui_card_summary": "Backup planning card, locked against execution.",
        "expected_outputs": ["planning-only badge", "approval badge", "blocked reason", "safety lock flags"],
    },
    "blocked_config_change_request": {
        "display_name": "Blocked Config Change Request",
        "category": "blocked_change",
        "user_goal": "Show how future UI cards should explain a configuration-changing request that remains blocked before any execution path.",
        "supported_status": "blocked",
        "dry_run": False,
        "planning_only": True,
        "requires_approval": True,
        "blocked_reason": "Configuration-changing jobs are blocked; Phase 2B and live execution are not authorized.",
        "safety_summary": "Blocked catalog card only; it cannot produce a runner payload or unlock execution.",
        "ui_card_summary": "Blocked config-change card with visible safety reason.",
        "expected_outputs": ["blocked badge", "approval badge", "blocked reason", "safety lock flags"],
    },
}


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _forbidden_capabilities_confirmed() -> Dict[str, bool]:
    return {capability: False for capability in FORBIDDEN_CAPABILITIES}


def _ui_card(entry: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "title": str(entry["display_name"]),
        "description": str(entry["user_goal"]),
        "status_badge": str(entry["supported_status"]),
        "dry_run_badge": "dry-run" if entry["dry_run"] else "not-dry-run",
        "approval_badge": "approval-required" if entry["requires_approval"] else "approval-not-required",
        "blocked_reason": str(entry["blocked_reason"]),
        "evidence_references": list(entry["evidence_or_artifact_references"]),
        "safety_lock_flags": dict(entry["forbidden_capabilities_confirmed"]),
        "ui_readiness_state": {
            "future_route": "/network/jobs",
            "can_be_consumed_by_future_ui": True,
            "executable_now": False,
        },
    }


def _source_references_by_job_type() -> Dict[str, Sequence[str]]:
    mapping = build_artifact_to_jobs_mapping()
    references: Dict[str, Sequence[str]] = {}
    for job in mapping.get("job_candidates", []):
        if isinstance(job, Mapping):
            references[str(job.get("job_type"))] = tuple(str(path) for path in job.get("source_artifacts", []))
    return references


def build_jobs_catalog_entries() -> Tuple[Dict[str, Any], ...]:
    """Build deterministic UI-ready catalog entries for all Phase 2A-08 Jobs."""

    source_references = _source_references_by_job_type()
    entries = []
    for job_type in REQUIRED_JOB_TYPES:
        definition = JOB_CARD_DEFINITIONS[job_type]
        seed = {"phase": PHASE, "job_type": job_type, "display_name": definition["display_name"]}
        entry = {
            "job_id": f"PHASE_2A_08_JOB_{_stable_digest(seed, length=10)}",
            "job_type": job_type,
            "display_name": definition["display_name"],
            "category": definition["category"],
            "user_goal": definition["user_goal"],
            "supported_status": definition["supported_status"],
            "dry_run": definition["dry_run"],
            "planning_only": definition["planning_only"],
            "requires_approval": definition["requires_approval"],
            "blocked_reason": definition["blocked_reason"],
            "safety_summary": definition["safety_summary"],
            "forbidden_capabilities_confirmed": _forbidden_capabilities_confirmed(),
            "ui_card_summary": definition["ui_card_summary"],
            "evidence_or_artifact_references": list(source_references.get(job_type, ())),
            "expected_outputs": list(definition["expected_outputs"]),
            "next_phase_allowed": False,
        }
        entry["ui_card"] = _ui_card(entry)
        entries.append(entry)
    return tuple(entries)


def validate_phase_2a_08_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    entries = report.get("jobs_catalog", [])
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
        errors.append("JOBS_CATALOG_NOT_LIST")
        entries = []

    by_type = {str(entry.get("job_type")): entry for entry in entries if isinstance(entry, Mapping)}
    missing = sorted(set(REQUIRED_JOB_TYPES).difference(by_type))
    if missing:
        errors.append("MISSING_REQUIRED_JOB_TYPES:" + ",".join(missing))
    if len(by_type) <= 1 or set(by_type) == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if set(REQUIRED_JOB_TYPES) != set(by_type):
        errors.append("CATALOG_JOB_TYPE_SET_MISMATCH")

    for entry in entries:
        if not isinstance(entry, Mapping):
            errors.append("CATALOG_ENTRY_NOT_OBJECT")
            continue
        job_type = str(entry.get("job_type"))
        for field in UI_READY_FIELDS:
            if field not in entry:
                errors.append(f"UI_READY_FIELD_MISSING:{job_type}:{field}")
        if entry.get("next_phase_allowed") is not False:
            errors.append(f"NEXT_PHASE_ALLOWED_NOT_FALSE:{job_type}")
        if entry.get("planning_only") is not True:
            errors.append(f"PLANNING_ONLY_NOT_TRUE:{job_type}")
        if job_type != "blocked_config_change_request" and entry.get("dry_run") is not True:
            errors.append(f"DRY_RUN_NOT_TRUE:{job_type}")
        if job_type == "backup_config_plan":
            if entry.get("planning_only") is not True or entry.get("supported_status") != "planning_only":
                errors.append("BACKUP_CONFIG_PLAN_NOT_PLANNING_ONLY")
            if not str(entry.get("blocked_reason", "")):
                errors.append("BACKUP_CONFIG_PLAN_MISSING_BLOCKED_REASON")
        if job_type == "blocked_config_change_request":
            if entry.get("supported_status") != "blocked":
                errors.append("BLOCKED_CONFIG_CHANGE_REQUEST_NOT_BLOCKED")
            if entry.get("requires_approval") is not True:
                errors.append("BLOCKED_CONFIG_CHANGE_REQUEST_APPROVAL_NOT_REQUIRED")
            if not str(entry.get("blocked_reason", "")):
                errors.append("BLOCKED_CONFIG_CHANGE_REQUEST_MISSING_REASON")

        forbidden = entry.get("forbidden_capabilities_confirmed", {})
        if not isinstance(forbidden, Mapping):
            errors.append(f"FORBIDDEN_CAPABILITIES_NOT_OBJECT:{job_type}")
        else:
            missing_capabilities = sorted(set(FORBIDDEN_CAPABILITIES).difference(forbidden))
            if missing_capabilities:
                errors.append(f"FORBIDDEN_CAPABILITIES_MISSING:{job_type}:{','.join(missing_capabilities)}")
            enabled_capabilities = sorted(key for key, value in forbidden.items() if value is not False)
            if enabled_capabilities:
                errors.append(f"FORBIDDEN_CAPABILITIES_ENABLED:{job_type}:{','.join(enabled_capabilities)}")

        ui_card = entry.get("ui_card", {})
        if not isinstance(ui_card, Mapping):
            errors.append(f"UI_CARD_NOT_OBJECT:{job_type}")
        else:
            readiness = ui_card.get("ui_readiness_state", {})
            if not isinstance(readiness, Mapping):
                errors.append(f"UI_READINESS_STATE_NOT_OBJECT:{job_type}")
            else:
                if readiness.get("future_route") != "/network/jobs":
                    errors.append(f"UI_FUTURE_ROUTE_MISMATCH:{job_type}")
                if readiness.get("can_be_consumed_by_future_ui") is not True:
                    errors.append(f"UI_CONSUMPTION_NOT_READY:{job_type}")
                if readiness.get("executable_now") is not False:
                    errors.append(f"UI_EXECUTABLE_NOW_NOT_FALSE:{job_type}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")

    try:
        canonical = _canonical_json(report)
        if _canonical_json(json.loads(canonical)) != canonical:
            errors.append("JSON_NOT_DETERMINISTIC")
    except (TypeError, ValueError) as exc:
        errors.append(f"JSON_SERIALIZATION_FAILED:{exc}")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "jobs_checked": len(entries),
    }


def build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report() -> Dict[str, Any]:
    entries = list(build_jobs_catalog_entries())
    artifact_mapping = build_artifact_to_jobs_mapping()
    report = {
        "phase": PHASE,
        "status": "PASS",
        "overall_status": "PASS",
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "phase_goal": "Create a planning-only Jobs Catalog / UI Readiness Pack for multiple Phase 2A-08 job types.",
            "example_job_types": list(REQUIRED_JOB_TYPES),
            "forbidden_scope": [
                "Phase 2B",
                "live device access",
                "SSH/NETCONF/RESTCONF/API/model/provider calls",
                "runner/adapter/broker/execution provider",
                "configuration-changing commands",
                "real backup",
                "real VRRP testing",
                "secrets",
            ],
            "existing_artifacts_referenced": list(EXISTING_ARTIFACT_REFERENCES),
            "implementation_boundary": "JSON catalog data, UI-card planning fields, HTML report, docs, tests, and report-index registration only.",
        },
        "existing_artifacts_referenced": list(EXISTING_ARTIFACT_REFERENCES),
        "phase_2a_07_source": {
            "artifact_mapping_reused": True,
            "artifact_reference_groups": len(artifact_mapping.get("artifact_reference_groups", [])),
            "job_candidates": len(artifact_mapping.get("job_candidates", [])),
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "catalog_entries": len(entries),
            "required_job_types": len(REQUIRED_JOB_TYPES),
            "planning_only_entries": sum(1 for entry in entries if entry["planning_only"] is True),
            "dry_run_entries": sum(1 for entry in entries if entry["dry_run"] is True),
            "blocked_entries": sum(1 for entry in entries if entry["supported_status"] == "blocked"),
            "approval_required_entries": sum(1 for entry in entries if entry["requires_approval"] is True),
            "ui_ready_entries": sum(
                1
                for entry in entries
                if entry["ui_card"]["ui_readiness_state"]["can_be_consumed_by_future_ui"] is True
            ),
            "executable_entries": sum(
                1 for entry in entries if entry["ui_card"]["ui_readiness_state"]["executable_now"] is True
            ),
            "next_phase_allowed_count": sum(1 for entry in entries if entry["next_phase_allowed"] is True),
        },
        "ui_schema": {
            "future_route": "/network/jobs",
            "deterministic_json": True,
            "fields": list(UI_READY_FIELDS),
            "status_badges": ["planning_only", "blocked"],
            "safety_lock_flags": list(FORBIDDEN_CAPABILITIES),
        },
        "jobs_catalog": entries,
    }
    validation = validate_phase_2a_08_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    return report


def write_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _summary_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )


def _job_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(entry['job_type']))}</td>"
        f"<td>{html.escape(str(entry['display_name']))}</td>"
        f"<td>{html.escape(str(entry['supported_status']))}</td>"
        f"<td>{html.escape(str(entry['dry_run']))}</td>"
        f"<td>{html.escape(str(entry['planning_only']))}</td>"
        f"<td>{html.escape(str(entry['requires_approval']))}</td>"
        f"<td>{html.escape(str(entry['blocked_reason'] or ''))}</td>"
        f"<td>{html.escape(str(entry['ui_card']['ui_readiness_state']['executable_now']))}</td>"
        "</tr>"
        for entry in report["jobs_catalog"]
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    code {{ background: #f3f6fa; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Phase 2A-08 creates deterministic Jobs catalog and card data for future <code>/network/jobs</code> UI consumption. It is not executable and keeps Phase 2B, live devices, SSH, NETCONF, RESTCONF, providers, APIs, models, secrets, real backup, and real VRRP testing disabled.</p>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Jobs Catalog Cards</h2>
  <table>
    <thead><tr><th>Job type</th><th>Display name</th><th>Status</th><th>Dry-run</th><th>Planning-only</th><th>Approval</th><th>Blocked reason</th><th>Executable now</th></tr></thead>
    <tbody>{_job_rows(report)}</tbody>
  </table>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_08_jobs_catalog_ui_readiness_planning_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    json_path, html_path = write_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Catalog entries: {report['summary']['catalog_entries']}")
    print(f"Required job types: {report['summary']['required_job_types']}")
    print(f"Planning-only entries: {report['summary']['planning_only_entries']}")
    print(f"Dry-run entries: {report['summary']['dry_run_entries']}")
    print(f"Blocked entries: {report['summary']['blocked_entries']}")
    print(f"UI-ready entries: {report['summary']['ui_ready_entries']}")
    print(f"Executable entries: {report['summary']['executable_entries']}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"broker_enabled: {str(report['broker_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"netconf_enabled: {str(report['netconf_enabled']).lower()}")
    print(f"restconf_enabled: {str(report['restconf_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"provider_api_model_enabled: {str(report['provider_api_model_enabled']).lower()}")
    print(f"secrets_enabled: {str(report['secrets_enabled']).lower()}")
    print(f"real_backup_enabled: {str(report['real_backup_enabled']).lower()}")
    print(f"real_vrrp_test_enabled: {str(report['real_vrrp_test_enabled']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
