"""Phase 2C-13 Interview MVP implementation slice safety delta review.

This module creates deterministic, local, planning-only safety delta evidence
for the Phase 2C-12 Interview MVP implementation slice candidates. It does not
select, authorize, scaffold, implement, execute, or prepare any candidate and
does not add runners, adapters, execution paths, queues, schedulers, workers,
AI loops, SSH, NETCONF, RESTCONF, live devices, providers, APIs, models,
secrets, backups, config changes, production execution paths, Day1-Day160
replacement, or a second safety matrix.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_12_interview_mvp_implementation_slice_candidate_inventory import (
    CANDIDATE_INVENTORY as PHASE_2C_12_CANDIDATE_INVENTORY,
    FINAL_VERDICT as PHASE_2C_12_VERDICT,
    TASK_NAME as PHASE_2C_12_TASK_NAME,
    build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report,
    validate_phase_2c_12_report,
)


PHASE = "2C-13"
TASK_NAME = "phase2c-13-interview-mvp-implementation-slice-safety-delta-review"
TITLE = "Phase 2C-13 Interview MVP Implementation Slice Safety Delta Review - Planning Only"
MODE = "planning_only_safety_delta_review"
SCOPE = "interview_mvp_implementation_slice_safety_delta_review_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_13_INTERVIEW_MVP_SAFETY_DELTA_REVIEW_DONE_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.md"

PHASE_GOAL = (
    "Create a planning-only safety delta review for the Phase 2C-12 Interview "
    "MVP implementation slice candidates. The review is candidate-level and "
    "risk-level only; it does not select a final slice, authorize "
    "implementation, or start implementation."
)

CANDIDATE_SOURCE = (
    "Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory is the "
    "only candidate source. Phase 2C-13 derives candidate IDs and names from "
    "that artifact and does not invent, select, rank as final, authorize, or "
    "implement any candidate."
)

EXAMPLE_JOB_TYPES = (
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "artifact_validation_job",
    "Phase 2C-12 candidate inventory entries only",
)

SAFETY_MATRIX_RULE = (
    "The existing safety matrix remains the single source of truth. Phase "
    "2C-13 only records safety deltas and must not create a second safety "
    "matrix."
)

SAFETY_DELTA_FIELDS = (
    "would_require_new_input_types",
    "would_require_live_device_access",
    "would_require_ssh_netconf_restconf",
    "would_require_provider_api_model_integration",
    "would_require_secrets",
    "would_require_queue_scheduler_worker_ai_loop",
    "would_require_runner_adapter_execution_path_changes",
    "would_create_config_backup_or_config_change_behavior",
    "would_affect_day1_day160_artifacts",
    "would_require_new_safety_matrix",
    "opens_new_risk_category_within_phase_2c_13",
)

FORBIDDEN_SCOPE = (
    "unique slice selection",
    "implementation authorization",
    "implementation start",
    "candidate implementation logic",
    "runner logic",
    "adapter logic",
    "execution path",
    "scheduler logic",
    "queue logic",
    "worker logic",
    "AI agent loop",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider integration",
    "API integration",
    "model integration",
    "secrets handling",
    "config backup execution",
    "config change execution",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "Phase 2C-14 start",
    "AGENTS.md modification",
    "unrelated file modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/automation_readiness/actual_automation_integration_plan.md",
    "docs/phase_2c/phase_2c_10_next_slice_decision_gate_authorization_review.md",
    "docs/phase_2c/phase_2c_11_interview_mvp_scope_architecture_gate.md",
    "docs/phase_2c/phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md",
    "phase_2c_10_next_slice_decision_gate_authorization_review.py",
    "phase_2c_11_interview_mvp_scope_architecture_gate.py",
    "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.py",
    "tests/test_phase_2c_10_next_slice_decision_gate_authorization_review.py",
    "tests/test_phase_2c_11_interview_mvp_scope_architecture_gate.py",
    "tests/test_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add Phase 2C-13 planning-only safety delta review evidence, "
    "minimal deterministic report-only generation, targeted tests, and "
    "existing-pattern registry/CLI/report-index visibility. Not allowed: "
    "selecting a unique slice, authorizing implementation, starting "
    "implementation, adding implementation logic, runner, adapter, execution "
    "path, scheduler, queue, worker, AI loop, SSH, NETCONF, RESTCONF, live "
    "device access, provider/API/model integration, secrets, config backup, "
    "config change, production execution, Day1-Day160 replacement, Phase "
    "2C-14 start, AGENTS.md modification, or a second safety matrix."
)

DELTA_STATUS = "NO_NEW_SAFETY_DELTA_WITHIN_PHASE_2C_13_PLANNING_BOUNDARY"

SAFETY_FLAGS = {
    "phase_2c_13_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmed_before_implementation": True,
    "required_reference_document_read": True,
    "phase_2c_12_candidate_inventory_found": True,
    "phase_2c_12_candidate_inventory_read": True,
    "candidate_source_phase_2c_12_only": True,
    "no_new_candidates_invented": True,
    "safety_delta_review_only": True,
    "unique_slice_selected": False,
    "implementation_authorized": False,
    "implementation_started": False,
    "phase_2c_14_started": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "queue_added": False,
    "scheduler_added": False,
    "worker_added": False,
    "ai_loop_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_13_INTERVIEW_MVP_IMPLEMENTATION_SLICE_SAFETY_DELTA_REVIEW",
    "CANDIDATE_SOURCE_PHASE_2C_12_ONLY_YES",
    "NO_NEW_CANDIDATES_INVENTED_YES",
    "SAFETY_DELTA_REVIEW_ONLY_YES",
    "UNIQUE_SLICE_SELECTED_NO",
    "IMPLEMENTATION_AUTHORIZED_NO",
    "IMPLEMENTATION_STARTED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "NEXT_PHASE_STARTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_13": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_12_source_review(project_root: Path) -> Dict[str, Any]:
    source_report = build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(project_root)
    source_validation = validate_phase_2c_12_report(source_report)
    candidates = source_report.get("candidate_inventory", [])
    return {
        "reviewed_task": PHASE_2C_12_TASK_NAME,
        "expected_verdict": PHASE_2C_12_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "candidate_count": len(candidates),
        "candidate_ids": [candidate.get("candidate_id") for candidate in candidates if isinstance(candidate, Mapping)],
        "candidate_source_confirmed": True,
        "new_candidates_invented": False,
        "unique_slice_selected_by_source": source_report.get("single_slice_selected"),
        "implementation_authorized_by_source": source_report.get("implementation_authorized"),
        "implementation_started_by_source": source_report.get("implementation_started"),
    }


def _source_risk_categories(candidate: Mapping[str, Any]) -> Tuple[str, ...]:
    categories = []
    if candidate.get("opens_runner_adapter_execution_risk") is True:
        categories.append("runner_adapter_execution_scope_if_broadened")
    if candidate.get("touches_live_device_provider_secrets_risk") is True:
        categories.append("live_device_provider_secrets_scope_if_broadened")
    return tuple(categories)


def _candidate_delta_review() -> Tuple[Dict[str, Any], ...]:
    reviews = []
    for candidate in PHASE_2C_12_CANDIDATE_INVENTORY:
        source_risk_categories = _source_risk_categories(candidate)
        reviews.append(
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "source_candidate_status": candidate["current_decision_status"],
                "candidate_source": "Phase 2C-12",
                "candidate_selected": False,
                "candidate_authorized": False,
                "implementation_started": False,
                "would_require_new_input_types": False,
                "would_require_live_device_access": False,
                "would_require_ssh_netconf_restconf": False,
                "would_require_provider_api_model_integration": False,
                "would_require_secrets": False,
                "would_require_queue_scheduler_worker_ai_loop": False,
                "would_require_runner_adapter_execution_path_changes": False,
                "would_create_config_backup_or_config_change_behavior": False,
                "would_affect_day1_day160_artifacts": False,
                "would_require_new_safety_matrix": False,
                "opens_new_risk_category_within_phase_2c_13": False,
                "source_risk_categories_not_opened_by_this_phase": list(source_risk_categories),
                "delta_status": DELTA_STATUS,
            }
        )
    return tuple(reviews)


def validate_phase_2c_13_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("review_decision") != "SAFETY_DELTA_REVIEW_ONLY":
        errors.append("REVIEW_DECISION_MISMATCH")
    if report.get("candidate_source") != CANDIDATE_SOURCE:
        errors.append("CANDIDATE_SOURCE_MISMATCH")
    if report.get("safety_matrix_rule") != SAFETY_MATRIX_RULE:
        errors.append("SAFETY_MATRIX_RULE_MISMATCH")

    source_review = report.get("phase_2c_12_source_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_12_SOURCE_NOT_OBJECT")
        source_review = {}
    if source_review.get("reviewed_task") != PHASE_2C_12_TASK_NAME:
        errors.append("PHASE_2C_12_TASK_MISMATCH")
    if source_review.get("observed_verdict") != PHASE_2C_12_VERDICT:
        errors.append("PHASE_2C_12_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_12_VALIDATION_NOT_PASS")

    candidate_reviews = report.get("candidate_safety_delta_reviews", [])
    if not isinstance(candidate_reviews, Sequence) or isinstance(candidate_reviews, (str, bytes)):
        errors.append("CANDIDATE_DELTA_REVIEWS_NOT_LIST")
        candidate_reviews = []
    expected_ids = {candidate["candidate_id"] for candidate in PHASE_2C_12_CANDIDATE_INVENTORY}
    observed_ids = {item.get("candidate_id") for item in candidate_reviews if isinstance(item, Mapping)}
    if observed_ids != expected_ids:
        errors.append("CANDIDATE_ID_SET_MISMATCH")
    if len(candidate_reviews) != len(PHASE_2C_12_CANDIDATE_INVENTORY):
        errors.append("CANDIDATE_DELTA_REVIEW_COUNT_MISMATCH")
    for item in candidate_reviews:
        if not isinstance(item, Mapping):
            errors.append("CANDIDATE_DELTA_REVIEW_ITEM_NOT_OBJECT")
            continue
        if item.get("candidate_source") != "Phase 2C-12":
            errors.append(f"CANDIDATE_SOURCE_NOT_PHASE_2C_12:{item.get('candidate_id')}")
        if item.get("delta_status") != DELTA_STATUS:
            errors.append(f"DELTA_STATUS_MISMATCH:{item.get('candidate_id')}")
        if item.get("candidate_selected") is not False:
            errors.append(f"CANDIDATE_SELECTED:{item.get('candidate_id')}")
        if item.get("candidate_authorized") is not False:
            errors.append(f"CANDIDATE_AUTHORIZED:{item.get('candidate_id')}")
        if item.get("implementation_started") is not False:
            errors.append(f"CANDIDATE_IMPLEMENTATION_STARTED:{item.get('candidate_id')}")
        for field in SAFETY_DELTA_FIELDS:
            if item.get(field) is not False:
                errors.append(f"SAFETY_DELTA_FIELD_TRUE:{item.get('candidate_id')}:{field}")

    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if report.get("safety_delta_fields") != list(SAFETY_DELTA_FIELDS):
        errors.append("SAFETY_DELTA_FIELDS_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if set(report.get("existing_artifacts_referenced", [])) != set(EXISTING_ARTIFACTS_REFERENCED):
        errors.append("EXISTING_ARTIFACTS_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "CANDIDATE_SOURCE_PHASE_2C_12_ONLY": "YES",
        "NO_NEW_CANDIDATES_INVENTED": "YES",
        "SAFETY_DELTA_REVIEW_ONLY": "YES",
        "UNIQUE_SLICE_SELECTED": "NO",
        "IMPLEMENTATION_AUTHORIZED": "NO",
        "IMPLEMENTATION_STARTED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEXT_PHASE_STARTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "unique_slice_selected",
        "implementation_authorized",
        "implementation_started",
        "phase_2c_14_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "queue_added",
        "scheduler_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
        "needs_scope_confirmation",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "candidate_delta_reviews_checked": len(candidate_reviews),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(report.get("existing_artifacts_referenced", [])),
    }


def build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
    project_root: Path,
) -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "review_decision": "SAFETY_DELTA_REVIEW_ONLY",
        "phase_goal": PHASE_GOAL,
        "candidate_source": CANDIDATE_SOURCE,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "safety_delta_fields": list(SAFETY_DELTA_FIELDS),
        "safety_matrix_rule": SAFETY_MATRIX_RULE,
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "phase_2c_12_source_review": _phase_2c_12_source_review(project_root),
        "candidate_safety_delta_reviews": list(_candidate_delta_review()),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "review_statement": (
            "Phase 2C-13 compares each Phase 2C-12 candidate with the current "
            "project safety baseline. It records candidate-level safety deltas "
            "only and is not a selection, authorization, kickoff, or "
            "implementation phase."
        ),
        "non_execution_statement": (
            "This task opens no runner, adapter, execution path, queue, "
            "scheduler, worker, AI loop, SSH, NETCONF, RESTCONF, live-device "
            "access, provider/API/model calls, secrets, backup behavior, "
            "config-change behavior, Day1-Day160 rewrite, Phase 2C-14 start, "
            "or second safety matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "CANDIDATE_SOURCE_PHASE_2C_12_ONLY": "YES",
            "NO_NEW_CANDIDATES_INVENTED": "YES",
            "SAFETY_DELTA_REVIEW_ONLY": "YES",
            "UNIQUE_SLICE_SELECTED": "NO",
            "IMPLEMENTATION_AUTHORIZED": "NO",
            "IMPLEMENTATION_STARTED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEXT_PHASE_STARTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "candidate_count": len(report["candidate_safety_delta_reviews"]),
        "candidate_source_phase_2c_12_only": True,
        "no_new_candidates_invented": True,
        "safety_delta_review_only": True,
        "unique_slice_selected": False,
        "implementation_authorized": False,
        "implementation_started": False,
        "runner_adapter_execution_path_added": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "next_phase_started": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_13_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = BLOCKED_VERDICT
        report["summary"]["final_verdict"] = BLOCKED_VERDICT
    return report


def _list_items(values: Sequence[Any]) -> str:
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values)


def _dict_rows(values: Mapping[str, Any]) -> str:
    return "".join(
        "<tr>"
        f"<th>{html.escape(str(key))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for key, value in values.items()
    )


def _candidate_delta_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('candidate_id')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_name')))}</td>"
        f"<td>{html.escape(str(item.get('delta_status')))}</td>"
        f"<td>{html.escape(str(item.get('opens_new_risk_category_within_phase_2c_13')))}</td>"
        f"<td>{html.escape(str(item.get('source_risk_categories_not_opened_by_this_phase')))}</td>"
        "</tr>"
        for item in values
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    write_text_with_parents(
        output_path,
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2933; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #f4f6f8; padding: 0.1rem 0.25rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: <strong>{html.escape(str(report["status"]))}</strong></p>
  <p>Review decision: <strong>{html.escape(str(report["review_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["review_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Safety Matrix Rule</h2>
  <p>{html.escape(str(report["safety_matrix_rule"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Phase 2C-12 Source Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_12_source_review"])}</tbody></table>
  <h2>Candidate Safety Delta Reviews</h2>
  <table><thead><tr><th>Candidate ID</th><th>Name</th><th>Delta Status</th><th>New Risk Opened</th><th>Source Risk Categories</th></tr></thead><tbody>{_candidate_delta_rows(report["candidate_safety_delta_reviews"])}</tbody></table>
  <h2>Safety Delta Fields</h2>
  <ul>{_list_items(report["safety_delta_fields"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_referenced"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        project_root
    )
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(project_root)
    json_path, html_path = write_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Review decision: {report['review_decision']}")
    print(f"candidate_source_phase_2c_12_only: {str(report['summary']['candidate_source_phase_2c_12_only']).lower()}")
    print(f"no_new_candidates_invented: {str(report['summary']['no_new_candidates_invented']).lower()}")
    print(f"safety_delta_review_only: {str(report['summary']['safety_delta_review_only']).lower()}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"unique_slice_selected: {str(report['summary']['unique_slice_selected']).lower()}")
    print(f"implementation_authorized: {str(report['summary']['implementation_authorized']).lower()}")
    print(f"implementation_started: {str(report['summary']['implementation_started']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
    )
    print(
        "queue_scheduler_worker_ai_loop_added: "
        f"{str(report['summary']['queue_scheduler_worker_ai_loop_added']).lower()}"
    )
    print(
        "ssh_netconf_restconf_live_device_touched: "
        f"{str(report['summary']['ssh_netconf_restconf_live_device_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(
        "config_backup_or_change_behavior_added: "
        f"{str(report['summary']['config_backup_or_change_behavior_added']).lower()}"
    )
    print(f"day1_day160_rewritten_or_replaced: {str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}")
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"next_phase_started: {str(report['summary']['next_phase_started']).lower()}")
    print(f"Candidate delta reviews checked: {report['validation']['candidate_delta_reviews_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
