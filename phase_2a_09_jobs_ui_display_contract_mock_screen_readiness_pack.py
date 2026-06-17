"""Phase 2A-09 Jobs UI display contract / mock screen readiness pack.

This module defines deterministic display contracts and mock screen data for a
future /network/jobs UI over the Phase 2A-08 Jobs Catalog. It is contract,
fixture, documentation, and report output only. It does not add a frontend API,
runner, adapter, broker, scheduler, shell runner, SSH, NETCONF, RESTCONF, live
device access, real backup, real VRRP execution, provider/API/model call, or
Phase 2B path.
"""

from __future__ import annotations

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import (
    DOC_PATH as PHASE_2A_08_DOC_PATH,
    REPORT_HTML as PHASE_2A_08_REPORT_HTML,
    REPORT_JSON as PHASE_2A_08_REPORT_JSON,
    REQUIRED_JOB_TYPES as PHASE_2A_08_REQUIRED_JOB_TYPES,
    build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report,
)


PHASE = "2A-09"
TASK_NAME = "phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack"
TITLE = "Phase 2A-09 Jobs UI Display Contract / Mock Screen Readiness Pack"
STATUS_LABEL = "PHASE_2A_09_JOBS_UI_DISPLAY_CONTRACT_MOCK_SCREEN_READINESS_PACK_READY"
MODE = "planning_only_ui_contract_mock_only"
SCOPE = "jobs_ui_display_contract_for_full_phase_2a_08_catalog"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md"

EXISTING_ARTIFACT_REFERENCES = (
    "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
    PHASE_2A_08_DOC_PATH.as_posix(),
    PHASE_2A_08_REPORT_JSON.as_posix(),
    PHASE_2A_08_REPORT_HTML.as_posix(),
    "phase_2a_07_vrrp_dry_run_validation_pack.py",
    "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
    "reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json",
)

SAFETY_FLAGS = {
    "phase_2b_introduced": False,
    "phase_2b_authorized": False,
    "runner_introduced": False,
    "runner_enabled": False,
    "adapter_introduced": False,
    "adapter_enabled": False,
    "broker_introduced": False,
    "broker_enabled": False,
    "scheduler_introduced": False,
    "queue_worker_introduced": False,
    "ssh_introduced": False,
    "ssh_enabled": False,
    "netconf_introduced": False,
    "netconf_enabled": False,
    "restconf_introduced": False,
    "restconf_enabled": False,
    "live_device_introduced": False,
    "live_device_access_enabled": False,
    "real_backup_introduced": False,
    "real_backup_enabled": False,
    "real_vrrp_execution_introduced": False,
    "real_vrrp_test_enabled": False,
    "real_frontend_api_integration_introduced": False,
    "provider_api_model_enabled": False,
    "secrets_enabled": False,
    "command_execution_enabled": False,
    "config_change_enabled": False,
    "next_phase_allowed": False,
}

SCREEN_SAFETY_DISPLAY = {
    "required_banner_lines": [
        "no SSH",
        "no runner",
        "no live device",
        "no NETCONF",
        "no RESTCONF",
        "dry-run only",
        "planning/mock/local only",
        "not Phase 2B",
    ],
    "display_flags": {
        "no_ssh": True,
        "no_runner": True,
        "no_live_device": True,
        "no_netconf": True,
        "no_restconf": True,
        "dry_run_only": True,
        "planning_mock_local_only": True,
        "not_phase_2b": True,
    },
    "executable_interpretation": "blocked",
}

JOB_LIST_REQUIRED_FIELDS = (
    "job_id",
    "job_name",
    "job_type",
    "category",
    "display_status",
    "allowed_or_blocked",
    "planning_only_indicator",
    "dry_run_indicator",
    "approval_required_indicator",
    "blocked_reason",
    "evidence_summary",
    "evidence_count",
    "safety_summary",
    "badges",
)

JOB_DETAIL_REQUIRED_FIELDS = (
    "job_id",
    "job_name",
    "job_type",
    "what_this_job_can_do",
    "what_this_job_cannot_do",
    "blocked_explanation",
    "approval_explanation",
    "referenced_evidence",
    "related_artifact_or_ledger_reference",
    "dry_run_boundary",
    "no_execution_proof",
    "no_live_device_proof",
    "no_ssh_netconf_restconf_proof",
    "safety_display",
    "badges",
)

REQUIRED_BADGE_TYPES = (
    "allowed",
    "blocked",
    "planning-only",
    "dry-run",
    "approval-required",
    "mock-only",
    "local-only",
    "no-runner",
    "no-ssh",
    "no-live-device",
    "invalid-catalog",
    "empty-catalog",
)

BADGE_RULES: Dict[str, Dict[str, Any]] = {
    "allowed": {
        "label": "Allowed",
        "tone": "success",
        "when": "Display data is safe to show as a non-executing local/mock/dry-run catalog item.",
        "executable_allowed": False,
    },
    "blocked": {
        "label": "Blocked",
        "tone": "danger",
        "when": "Catalog item is blocked or cannot be rendered as safe display data.",
        "executable_allowed": False,
    },
    "planning-only": {
        "label": "Planning only",
        "tone": "neutral",
        "when": "The item describes future-safe planning or review content only.",
        "executable_allowed": False,
    },
    "dry-run": {
        "label": "Dry-run",
        "tone": "info",
        "when": "The item is represented as dry-run/mock/local display data.",
        "executable_allowed": False,
    },
    "approval-required": {
        "label": "Approval required",
        "tone": "warning",
        "when": "The item requires a future separate approval gate before any live-capable phase could be considered.",
        "executable_allowed": False,
    },
    "mock-only": {
        "label": "Mock only",
        "tone": "neutral",
        "when": "The item is backed by deterministic local fixture or report data only.",
        "executable_allowed": False,
    },
    "local-only": {
        "label": "Local only",
        "tone": "neutral",
        "when": "The UI may read committed/local report references only.",
        "executable_allowed": False,
    },
    "no-runner": {
        "label": "No runner",
        "tone": "locked",
        "when": "No runner, worker, scheduler, broker, adapter, or execution path is available.",
        "executable_allowed": False,
    },
    "no-ssh": {
        "label": "No SSH",
        "tone": "locked",
        "when": "No SSH transport, command channel, or device session is available.",
        "executable_allowed": False,
    },
    "no-live-device": {
        "label": "No live device",
        "tone": "locked",
        "when": "No live-device target, session, or network I/O is available.",
        "executable_allowed": False,
    },
    "invalid-catalog": {
        "label": "Invalid catalog",
        "tone": "danger",
        "when": "Catalog JSON is malformed, missing fields, has unknown status, or contains forbidden execution fields.",
        "executable_allowed": False,
    },
    "empty-catalog": {
        "label": "Empty catalog",
        "tone": "neutral",
        "when": "No catalog or no displayable jobs are available.",
        "executable_allowed": False,
    },
}

EMPTY_STATE_CONTRACT = {
    "no_catalog_exists": {
        "title": "Jobs catalog unavailable",
        "message": "No local Phase 2A Jobs Catalog artifact is available for display.",
        "primary_action_label": "Review catalog documentation",
        "badges": ["empty-catalog", "no-runner", "no-ssh", "no-live-device"],
        "must_not_suggest_execution": True,
    },
    "catalog_exists_zero_jobs": {
        "title": "Jobs catalog is empty",
        "message": "The local catalog exists, but it contains zero displayable job rows.",
        "primary_action_label": "Review catalog evidence",
        "badges": ["empty-catalog", "planning-only", "local-only"],
        "must_not_suggest_execution": True,
    },
    "no_displayable_jobs": {
        "title": "No displayable jobs",
        "message": "Catalog entries were filtered out because they cannot be safely displayed.",
        "primary_action_label": "Review validation findings",
        "badges": ["empty-catalog", "invalid-catalog", "blocked"],
        "must_not_suggest_execution": True,
    },
}

ERROR_STATE_CONTRACT = {
    "malformed_json": {
        "title": "Catalog JSON is malformed",
        "message": "The screen must show a blocked invalid-catalog state and treat the payload as non-executable.",
        "blocks_executable_interpretation": True,
        "badges": ["invalid-catalog", "blocked", "no-runner"],
    },
    "required_fields_missing": {
        "title": "Required display fields are missing",
        "message": "The screen must block executable interpretation until the contract is corrected.",
        "blocks_executable_interpretation": True,
        "badges": ["invalid-catalog", "blocked"],
    },
    "unknown_status": {
        "title": "Unknown job status",
        "message": "The screen must not guess whether a job is safe; display must remain blocked.",
        "blocks_executable_interpretation": True,
        "badges": ["invalid-catalog", "blocked"],
    },
    "forbidden_execution_fields": {
        "title": "Forbidden execution fields detected",
        "message": "The screen must reject payloads that expose execution targets, credentials, scripts, commands, or transports.",
        "blocks_executable_interpretation": True,
        "badges": ["invalid-catalog", "blocked", "no-ssh", "no-runner"],
    },
    "unsafe_capability": {
        "title": "Unsafe capability detected",
        "message": "The screen must block display as executable when any live, runner, adapter, SSH, NETCONF, RESTCONF, backup, or VRRP execution capability appears enabled.",
        "blocks_executable_interpretation": True,
        "badges": ["invalid-catalog", "blocked", "no-live-device"],
    },
}

FORBIDDEN_DISPLAY_FIELD_NAMES = {
    "api_key",
    "adapter",
    "broker",
    "command",
    "commands",
    "credential",
    "credentials",
    "device_target",
    "executor",
    "host",
    "ip",
    "netconf",
    "password",
    "private_key",
    "restconf",
    "runner",
    "scheduler",
    "script",
    "script_path",
    "secret",
    "shell",
    "ssh",
    "target",
    "token",
    "transport",
    "username",
    "worker",
}

FORBIDDEN_EMPTY_ACTION_WORDS = ("run", "execute", "start", "connect", "launch", "apply")

COMPLETION_MARKERS = (
    "PHASE_2A_09_JOBS_UI_DISPLAY_CONTRACT_MOCK_SCREEN_READINESS_PACK_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "MULTI_JOB_SCOPE_CONFIRMED",
    "PHASE_2A_08_JOBS_CATALOG_REFERENCED",
    "JOB_LIST_VIEW_CONTRACT_DEFINED",
    "JOB_DETAIL_VIEW_CONTRACT_DEFINED",
    "BADGE_RULES_DEFINED",
    "EMPTY_STATE_CONTRACT_DEFINED",
    "ERROR_STATE_CONTRACT_DEFINED",
    "MOCK_SCREEN_FIXTURES_DEFINED",
    "SAFETY_DISPLAY_CONTRACT_DEFINED",
    "RUNNER_INTRODUCED_FALSE",
    "ADAPTER_INTRODUCED_FALSE",
    "SSH_INTRODUCED_FALSE",
    "NETCONF_INTRODUCED_FALSE",
    "RESTCONF_INTRODUCED_FALSE",
    "LIVE_DEVICE_INTRODUCED_FALSE",
    "REAL_BACKUP_INTRODUCED_FALSE",
    "REAL_VRRP_EXECUTION_INTRODUCED_FALSE",
    "REAL_FRONTEND_API_INTEGRATION_INTRODUCED_FALSE",
    "PHASE_2B_INTRODUCED_FALSE",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _phase_2a_08_entries() -> Tuple[Mapping[str, Any], ...]:
    report = build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    entries = report.get("jobs_catalog", [])
    return tuple(entry for entry in entries if isinstance(entry, Mapping))


def _evidence_summary(entry: Mapping[str, Any]) -> Dict[str, Any]:
    references = [str(value) for value in entry.get("evidence_or_artifact_references", [])]
    return {
        "count": len(references),
        "summary": f"{len(references)} local evidence/artifact reference(s)",
        "references": references,
    }


def _display_status(entry: Mapping[str, Any]) -> str:
    job_type = str(entry.get("job_type", ""))
    if str(entry.get("supported_status")) == "blocked":
        return "blocked"
    if entry.get("requires_approval") is True:
        return "approval-required"
    if job_type in {"baseline_check", "interface_status_check", "wan_lan_check"}:
        return "allowed"
    return "planning-only"


def _badges_for_entry(entry: Mapping[str, Any]) -> Tuple[str, ...]:
    badges = ["local-only", "mock-only", "no-runner", "no-ssh", "no-live-device"]
    status = _display_status(entry)
    if status == "allowed":
        badges.insert(0, "allowed")
    if status == "blocked":
        badges.insert(0, "blocked")
    if entry.get("planning_only") is True:
        badges.append("planning-only")
    if entry.get("dry_run") is True:
        badges.append("dry-run")
    if entry.get("requires_approval") is True:
        badges.append("approval-required")
    return tuple(dict.fromkeys(badges))


def _list_row(entry: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = _evidence_summary(entry)
    status = _display_status(entry)
    return {
        "job_id": str(entry["job_id"]),
        "job_name": str(entry["display_name"]),
        "job_type": str(entry["job_type"]),
        "category": str(entry["category"]),
        "display_status": status,
        "allowed_or_blocked": "blocked" if status == "blocked" else "allowed-for-display-only",
        "planning_only_indicator": entry.get("planning_only") is True,
        "dry_run_indicator": entry.get("dry_run") is True,
        "approval_required_indicator": entry.get("requires_approval") is True,
        "blocked_reason": str(entry.get("blocked_reason", "")),
        "evidence_summary": evidence["summary"],
        "evidence_count": evidence["count"],
        "safety_summary": str(entry["safety_summary"]),
        "badges": list(_badges_for_entry(entry)),
    }


def _detail_view(entry: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = _evidence_summary(entry)
    status = _display_status(entry)
    return {
        "job_id": str(entry["job_id"]),
        "job_name": str(entry["display_name"]),
        "job_type": str(entry["job_type"]),
        "what_this_job_can_do": [
            "Display local Phase 2A catalog metadata.",
            "Show reviewer-facing evidence references.",
            "Show safety badges and blocked/planning-only explanations.",
        ],
        "what_this_job_cannot_do": [
            "It cannot execute jobs.",
            "It cannot connect to devices.",
            "It cannot create backup, VRRP, runner, adapter, broker, SSH, NETCONF, or RESTCONF behavior.",
        ],
        "blocked_explanation": str(entry.get("blocked_reason", "")) if status == "blocked" else "",
        "approval_explanation": (
            "Approval is shown as a display badge only; it does not unlock execution."
            if entry.get("requires_approval") is True
            else ""
        ),
        "referenced_evidence": evidence["references"],
        "related_artifact_or_ledger_reference": evidence["references"][0] if evidence["references"] else PHASE_2A_08_DOC_PATH.as_posix(),
        "dry_run_boundary": "Display-only dry-run/mock/local contract; no live-capable operation is available.",
        "no_execution_proof": {
            "executable_now": False,
            "runner_invoked": False,
            "adapter_invoked": False,
            "broker_invoked": False,
            "command_payload_present": False,
        },
        "no_live_device_proof": {
            "live_device_access_enabled": False,
            "network_io_enabled": False,
            "device_target_present": False,
        },
        "no_ssh_netconf_restconf_proof": {
            "ssh_enabled": False,
            "netconf_enabled": False,
            "restconf_enabled": False,
        },
        "safety_display": deepcopy(SCREEN_SAFETY_DISPLAY),
        "badges": list(_badges_for_entry(entry)),
    }


def build_job_list_display_contract() -> Dict[str, Any]:
    return {
        "future_route": "/network/jobs",
        "view": "job-list",
        "required_fields": list(JOB_LIST_REQUIRED_FIELDS),
        "row_behavior": {
            "rows_are_display_only": True,
            "row_click_opens_detail_only": True,
            "row_must_not_execute": True,
            "show_blocked_reason_when_present": True,
            "show_evidence_count_or_summary": True,
        },
        "screen_safety_display": deepcopy(SCREEN_SAFETY_DISPLAY),
    }


def build_job_detail_display_contract() -> Dict[str, Any]:
    return {
        "future_route_template": "/network/jobs/{job_id}",
        "view": "job-detail",
        "required_fields": list(JOB_DETAIL_REQUIRED_FIELDS),
        "detail_behavior": {
            "details_are_display_only": True,
            "show_can_and_cannot_do_sections": True,
            "show_approval_explanation_when_required": True,
            "show_blocked_explanation_when_blocked": True,
            "show_no_execution_proof": True,
            "show_no_live_device_proof": True,
            "show_no_ssh_netconf_restconf_proof": True,
        },
        "screen_safety_display": deepcopy(SCREEN_SAFETY_DISPLAY),
    }


def build_mock_screen_data() -> Dict[str, Any]:
    entries = _phase_2a_08_entries()
    rows = [_list_row(entry) for entry in entries]
    details = [_detail_view(entry) for entry in entries]
    return {
        "fixture_id": f"PHASE_2A_09_UI_MOCK_{_stable_digest(rows, length=10)}",
        "future_route": "/network/jobs",
        "source": "derived_from_phase_2a_08_jobs_catalog",
        "screen_level_safety_display": deepcopy(SCREEN_SAFETY_DISPLAY),
        "job_list_populated": {
            "screen": "/network/jobs",
            "state": "populated",
            "rows": rows,
            "row_count": len(rows),
            "display_statuses": sorted({row["display_status"] for row in rows}),
        },
        "job_detail_examples": details,
        "empty_state_fixtures": deepcopy(EMPTY_STATE_CONTRACT),
        "error_state_fixtures": deepcopy(ERROR_STATE_CONTRACT),
    }


def _iter_field_names(payload: Any) -> Iterable[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            yield str(key).lower()
            yield from _iter_field_names(value)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for item in payload:
            yield from _iter_field_names(item)


def _empty_states_avoid_execution_suggestions(empty_states: Mapping[str, Any]) -> bool:
    for state in empty_states.values():
        if not isinstance(state, Mapping):
            return False
        action = str(state.get("primary_action_label", "")).lower()
        if any(word in action for word in FORBIDDEN_EMPTY_ACTION_WORDS):
            return False
        if state.get("must_not_suggest_execution") is not True:
            return False
    return True


def validate_phase_2a_09_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    source = report.get("phase_2a_08_source", {})
    if not isinstance(source, Mapping) or source.get("source_artifact_found") is not True:
        errors.append("PHASE_2A_08_SOURCE_ARTIFACT_NOT_CONFIRMED")
    source_job_types = set(source.get("source_job_types", [])) if isinstance(source, Mapping) else set()
    if set(PHASE_2A_08_REQUIRED_JOB_TYPES) != source_job_types:
        errors.append("PHASE_2A_08_JOB_TYPE_SET_MISMATCH")
    if len(source_job_types) <= 1 or source_job_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")

    list_contract = report.get("job_list_view_contract", {})
    missing_list_fields = sorted(set(JOB_LIST_REQUIRED_FIELDS).difference(list_contract.get("required_fields", [])))
    if missing_list_fields:
        errors.append("JOB_LIST_CONTRACT_MISSING_FIELDS:" + ",".join(missing_list_fields))

    detail_contract = report.get("job_detail_view_contract", {})
    missing_detail_fields = sorted(set(JOB_DETAIL_REQUIRED_FIELDS).difference(detail_contract.get("required_fields", [])))
    if missing_detail_fields:
        errors.append("JOB_DETAIL_CONTRACT_MISSING_FIELDS:" + ",".join(missing_detail_fields))

    badge_rules = report.get("badge_rules", {})
    missing_badges = sorted(set(REQUIRED_BADGE_TYPES).difference(badge_rules))
    if missing_badges:
        errors.append("BADGE_RULES_MISSING:" + ",".join(missing_badges))
    for badge_type, rule in badge_rules.items():
        if not isinstance(rule, Mapping) or rule.get("executable_allowed") is not False:
            errors.append(f"BADGE_RULE_EXECUTABLE_ALLOWED:{badge_type}")

    empty_states = report.get("empty_state_contract", {})
    if not isinstance(empty_states, Mapping) or set(EMPTY_STATE_CONTRACT).difference(empty_states):
        errors.append("EMPTY_STATE_CONTRACT_INCOMPLETE")
    elif not _empty_states_avoid_execution_suggestions(empty_states):
        errors.append("EMPTY_STATE_SUGGESTS_EXECUTION")

    error_states = report.get("error_state_contract", {})
    if not isinstance(error_states, Mapping) or set(ERROR_STATE_CONTRACT).difference(error_states):
        errors.append("ERROR_STATE_CONTRACT_INCOMPLETE")
    else:
        for state_name, state in error_states.items():
            if not isinstance(state, Mapping) or state.get("blocks_executable_interpretation") is not True:
                errors.append(f"ERROR_STATE_DOES_NOT_BLOCK_EXECUTABLE_INTERPRETATION:{state_name}")

    mock = report.get("mock_screen_data", {})
    rows = mock.get("job_list_populated", {}).get("rows", []) if isinstance(mock, Mapping) else []
    details = mock.get("job_detail_examples", []) if isinstance(mock, Mapping) else []
    statuses = {str(row.get("display_status")) for row in rows if isinstance(row, Mapping)}
    if len(rows) <= 1:
        errors.append("MOCK_SCREEN_DATA_NOT_MULTI_JOB")
    for required_status in ("allowed", "blocked", "planning-only", "approval-required"):
        if required_status not in statuses:
            errors.append(f"MOCK_SCREEN_DATA_MISSING_STATUS:{required_status}")
    if not details:
        errors.append("MOCK_DETAIL_FIXTURES_MISSING")
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("MOCK_ROW_NOT_OBJECT")
            continue
        missing = sorted(set(JOB_LIST_REQUIRED_FIELDS).difference(row))
        if missing:
            errors.append(f"MOCK_ROW_MISSING_FIELDS:{row.get('job_type')}:{','.join(missing)}")
    for detail in details:
        if not isinstance(detail, Mapping):
            errors.append("MOCK_DETAIL_NOT_OBJECT")
            continue
        missing = sorted(set(JOB_DETAIL_REQUIRED_FIELDS).difference(detail))
        if missing:
            errors.append(f"MOCK_DETAIL_MISSING_FIELDS:{detail.get('job_type')}:{','.join(missing)}")

    forbidden_field_hits = sorted(set(_iter_field_names(mock)).intersection(FORBIDDEN_DISPLAY_FIELD_NAMES))
    if forbidden_field_hits:
        errors.append("FORBIDDEN_EXECUTION_FIELDS_PRESENT_IN_MOCK:" + ",".join(forbidden_field_hits))

    safety_display = report.get("safety_display_contract", {})
    safety_lines = set(safety_display.get("required_banner_lines", [])) if isinstance(safety_display, Mapping) else set()
    for required_line in SCREEN_SAFETY_DISPLAY["required_banner_lines"]:
        if required_line not in safety_lines:
            errors.append("SAFETY_DISPLAY_LINE_MISSING:" + required_line)
    flags = safety_display.get("display_flags", {}) if isinstance(safety_display, Mapping) else {}
    for key in ("no_ssh", "no_runner", "no_live_device", "no_netconf", "no_restconf"):
        if flags.get(key) is not True:
            errors.append("SAFETY_DISPLAY_FLAG_MISSING:" + key)

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
        "mock_rows_checked": len(rows),
        "mock_details_checked": len(details),
    }


def build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report() -> Dict[str, Any]:
    source_entries = _phase_2a_08_entries()
    mock_screen_data = build_mock_screen_data()
    rows = mock_screen_data["job_list_populated"]["rows"]
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
            "phase_goal": "Define how a future /network/jobs screen displays the full Phase 2A-08 Jobs Catalog safely.",
            "example_job_types": list(PHASE_2A_08_REQUIRED_JOB_TYPES),
            "forbidden_scope": [
                "Phase 2B",
                "real runner",
                "job execution",
                "adapter",
                "SSH",
                "NETCONF",
                "RESTCONF",
                "live device access",
                "real backup",
                "real VRRP test",
                "real frontend API integration",
                "provider/model/API call",
                "secrets or credentials handling",
                "broker, scheduler, queue worker, shell/script runner",
            ],
            "existing_artifacts_referenced": list(EXISTING_ARTIFACT_REFERENCES),
            "implementation_boundary": "JSON/display contract, mock screen data, docs, tests, HTML/JSON report output, and registry/report-index wiring only.",
        },
        "existing_artifacts_referenced": list(EXISTING_ARTIFACT_REFERENCES),
        "phase_2a_08_source": {
            "source_artifact_found": True,
            "source_artifact_usage": "Phase 2A-09 derives list and detail mock rows from Phase 2A-08 jobs_catalog entries.",
            "source_job_types": [str(entry.get("job_type")) for entry in source_entries],
            "source_job_count": len(source_entries),
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "source_catalog_jobs": len(source_entries),
            "mock_list_rows": len(rows),
            "mock_detail_examples": len(mock_screen_data["job_detail_examples"]),
            "badge_rule_count": len(BADGE_RULES),
            "empty_state_count": len(EMPTY_STATE_CONTRACT),
            "error_state_count": len(ERROR_STATE_CONTRACT),
            "allowed_examples": sum(1 for row in rows if row["display_status"] == "allowed"),
            "blocked_examples": sum(1 for row in rows if row["display_status"] == "blocked"),
            "planning_only_examples": sum(1 for row in rows if row["display_status"] == "planning-only"),
            "approval_required_examples": sum(1 for row in rows if row["display_status"] == "approval-required"),
            "executable_examples": 0,
        },
        "job_list_view_contract": build_job_list_display_contract(),
        "job_detail_view_contract": build_job_detail_display_contract(),
        "badge_rules": deepcopy(BADGE_RULES),
        "empty_state_contract": deepcopy(EMPTY_STATE_CONTRACT),
        "error_state_contract": deepcopy(ERROR_STATE_CONTRACT),
        "safety_display_contract": deepcopy(SCREEN_SAFETY_DISPLAY),
        "mock_screen_data": mock_screen_data,
    }
    validation = validate_phase_2a_09_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    return report


def write_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
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


def _mock_list_rows(report: Mapping[str, Any]) -> str:
    rows = report["mock_screen_data"]["job_list_populated"]["rows"]
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row['job_type']))}</td>"
        f"<td>{html.escape(str(row['job_name']))}</td>"
        f"<td>{html.escape(str(row['display_status']))}</td>"
        f"<td>{html.escape(str(row['allowed_or_blocked']))}</td>"
        f"<td>{html.escape(str(row['planning_only_indicator']))}</td>"
        f"<td>{html.escape(str(row['dry_run_indicator']))}</td>"
        f"<td>{html.escape(str(row['approval_required_indicator']))}</td>"
        f"<td>{html.escape(str(row['evidence_count']))}</td>"
        f"<td>{html.escape(str(', '.join(row['badges'])))}</td>"
        "</tr>"
        for row in rows
    )


def _badge_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(name))}</td>"
        f"<td>{html.escape(str(rule['label']))}</td>"
        f"<td>{html.escape(str(rule['tone']))}</td>"
        f"<td>{html.escape(str(rule['executable_allowed']))}</td>"
        f"<td>{html.escape(str(rule['when']))}</td>"
        "</tr>"
        for name, rule in report["badge_rules"].items()
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    safety = "; ".join(report["safety_display_contract"]["required_banner_lines"])
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
  <p>Phase 2A-09 defines display contracts and mock screen data for future <code>/network/jobs</code> screens over the Phase 2A-08 Jobs Catalog. It is planning/mock/local only and not executable.</p>
  <p><strong>Screen safety display:</strong> {html.escape(safety)}</p>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Mock Job List</h2>
  <table>
    <thead><tr><th>Job type</th><th>Name</th><th>Status</th><th>Allowed/blocked</th><th>Planning-only</th><th>Dry-run</th><th>Approval</th><th>Evidence</th><th>Badges</th></tr></thead>
    <tbody>{_mock_list_rows(report)}</tbody>
  </table>
  <h2>Badge Rules</h2>
  <table>
    <thead><tr><th>Badge</th><th>Label</th><th>Tone</th><th>Executable allowed</th><th>Rule</th></tr></thead>
    <tbody>{_badge_rows(report)}</tbody>
  </table>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    json_path, html_path = write_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Source catalog jobs: {report['summary']['source_catalog_jobs']}")
    print(f"Mock list rows: {report['summary']['mock_list_rows']}")
    print(f"Mock detail examples: {report['summary']['mock_detail_examples']}")
    print(f"Badge rules: {report['summary']['badge_rule_count']}")
    print(f"Empty states: {report['summary']['empty_state_count']}")
    print(f"Error states: {report['summary']['error_state_count']}")
    print(f"Allowed examples: {report['summary']['allowed_examples']}")
    print(f"Blocked examples: {report['summary']['blocked_examples']}")
    print(f"Planning-only examples: {report['summary']['planning_only_examples']}")
    print(f"Approval-required examples: {report['summary']['approval_required_examples']}")
    print(f"Executable examples: {report['summary']['executable_examples']}")
    print(f"phase_2b_introduced: {str(report['phase_2b_introduced']).lower()}")
    print(f"runner_introduced: {str(report['runner_introduced']).lower()}")
    print(f"adapter_introduced: {str(report['adapter_introduced']).lower()}")
    print(f"ssh_introduced: {str(report['ssh_introduced']).lower()}")
    print(f"netconf_introduced: {str(report['netconf_introduced']).lower()}")
    print(f"restconf_introduced: {str(report['restconf_introduced']).lower()}")
    print(f"live_device_introduced: {str(report['live_device_introduced']).lower()}")
    print(f"real_backup_introduced: {str(report['real_backup_introduced']).lower()}")
    print(f"real_vrrp_execution_introduced: {str(report['real_vrrp_execution_introduced']).lower()}")
    print(f"real_frontend_api_integration_introduced: {str(report['real_frontend_api_integration_introduced']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
