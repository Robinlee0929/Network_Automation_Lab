"""Phase 2B-11 project consolidation and implementation entry map.

This module creates deterministic, local, planning-only report artifacts for a
project consolidation and future implementation entry map. It does not create
future phases, authorize implementation, select a first slice, or enable
runners, adapters, execution paths, SSH, NETCONF, RESTCONF, live-device access,
provider/API/model calls, secrets handling, backups, validation, command
execution, or real network operations.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_10_day1_day160_reference_mapping_for_future_first_slice import (
    FINAL_VERDICT as PHASE_2B_10_VERDICT,
)


PHASE = "2B-11"
TASK_NAME = "phase2b-11-project-consolidation-and-implementation-entry-map-planning-only"
TITLE = "Phase 2B-11 Project Consolidation and Implementation Entry Map — Planning Only"
MODE = "planning_only_project_consolidation_and_implementation_entry_map"
SCOPE = "phase_wide_project_consolidation_and_future_entry_map_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_11_PROJECT_CONSOLIDATION_ENTRY_MAP_PLANNING_ONLY_DONE"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_11_project_consolidation_and_implementation_entry_map.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_11_project_consolidation_and_implementation_entry_map.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_11_project_consolidation_and_implementation_entry_map.md"

PHASE_GOAL = (
    "Consolidate Phase 2B planning artifacts into a reviewer-visible entry map "
    "for possible future owner review while preserving planning-only status and "
    "not authorizing or starting implementation."
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "existing Phase 2B planning artifact tests",
)

FORBIDDEN_SCOPE = (
    "implementation",
    "first-slice implementation",
    "final first-slice selection",
    "new phase creation",
    "runner design",
    "runner creation",
    "adapter design",
    "adapter creation",
    "broker creation",
    "scheduler creation",
    "queue worker creation",
    "execution path design",
    "execution path creation",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "real network execution",
    "real backup",
    "real validation",
    "real command execution",
    "real config change",
    "provider call",
    "API call",
    "model call",
    "secrets handling",
    "second safety matrix",
    "Day1-Day160 rewrite or replacement",
    "Phase 2B-10 replacement",
)

FUTURE_PLAN_STEPS = (
    {
        "step": "1",
        "suggested_phase_task": "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
        "purpose": "Owner review of whether future implementation authorization should even be considered.",
        "allowed_now": "Review listing only; do not create this phase yet.",
        "implementation_involved": "NO",
        "risk_of_scope_drift": "Medium if treated as authorization instead of planning review.",
        "required_gate_before_proceeding": "Explicit owner request to create Phase 2B-12 as planning-only.",
    },
    {
        "step": "2",
        "suggested_phase_task": "Phase 2B-13 First-Slice Final Selection Gate — Planning Only",
        "purpose": "Future planning gate to choose a first-slice candidate only after authorization review.",
        "allowed_now": "Review listing only; do not create this phase yet.",
        "implementation_involved": "NO",
        "risk_of_scope_drift": "High if this artifact selects a final first slice.",
        "required_gate_before_proceeding": "Completed Phase 2B-12 planning-only authorization review.",
    },
    {
        "step": "3",
        "suggested_phase_task": "Phase 2B-14 First-Slice Implementation Kickoff Gate — Authorization Required",
        "purpose": "Future explicit kickoff gate after a candidate is selected and tests are defined.",
        "allowed_now": "NO",
        "implementation_involved": "Authorization gate only; no implementation in this artifact.",
        "risk_of_scope_drift": "High if treated as permission to code the slice.",
        "required_gate_before_proceeding": "Owner authorization plus written scope, boundary, tests, and rollback/refusal behavior.",
    },
    {
        "step": "4",
        "suggested_phase_task": "Future Phase 2C First-Slice Implementation — Not Allowed Yet",
        "purpose": "Possible future implementation only after all entry conditions are satisfied.",
        "allowed_now": "NO",
        "implementation_involved": "YES, but forbidden now.",
        "risk_of_scope_drift": "Critical.",
        "required_gate_before_proceeding": "Separate explicit implementation authorization after Phase 2B gates complete.",
    },
    {
        "step": "5",
        "suggested_phase_task": "Future runner / adapter / execution path design — Not Allowed Yet",
        "purpose": "Possible future design topic only after implementation entry is separately authorized.",
        "allowed_now": "NO",
        "implementation_involved": "Not allowed now.",
        "risk_of_scope_drift": "Critical.",
        "required_gate_before_proceeding": "Separate safety gate explicitly allowing runner/adapter/execution-path design.",
    },
    {
        "step": "6",
        "suggested_phase_task": "Future live-device integration — Not Allowed Yet",
        "purpose": "Possible future live-device scope only after a later live-operation safety gate.",
        "allowed_now": "NO",
        "implementation_involved": "Not allowed now.",
        "risk_of_scope_drift": "Critical.",
        "required_gate_before_proceeding": "Separate owner approval for the specific live operation and safety gate.",
    },
    {
        "step": "7",
        "suggested_phase_task": "Future provider / API / model integration — Not Allowed Yet",
        "purpose": "Possible future provider integration only after a later provider/API/model safety gate.",
        "allowed_now": "NO",
        "implementation_involved": "Not allowed now.",
        "risk_of_scope_drift": "Critical.",
        "required_gate_before_proceeding": "Separate owner approval for provider/API/model/secrets boundary.",
    },
)

FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS = (
    "Explicit owner authorization",
    "Written scope confirmation",
    "No narrowing to only one example job type unless explicitly approved",
    "Canonical safety boundary reference",
    "No duplicate safety matrix",
    "No Day1-Day160 rewrite or replacement",
    "Clear first-slice candidate selection",
    "Clear implementation boundary",
    "Targeted tests defined before implementation",
    "Rollback / refusal behavior defined before implementation",
    "No SSH / NETCONF / RESTCONF / live device access unless separately authorized later",
    "No provider / API / model / secrets handling unless separately authorized later",
    "Clean git status before starting",
)

FIRST_SLICE_CANDIDATES = (
    {
        "candidate": "baseline_check",
        "classification": "Potential future candidate",
        "review_note": "Example only; no final first-slice selection is made here.",
    },
    {
        "candidate": "interface_status_check",
        "classification": "Potential future candidate",
        "review_note": "Example only; would still require final selection gate and tests.",
    },
    {
        "candidate": "wan_lan_check",
        "classification": "Needs more planning",
        "review_note": "Example only; scope and refusal behavior need more detail.",
    },
    {
        "candidate": "vrrp_validation",
        "classification": "Needs more planning",
        "review_note": "Example only; must not become the whole phase without explicit approval.",
    },
    {
        "candidate": "backup_config_plan",
        "classification": "Needs more planning",
        "review_note": "Example only; real backup behavior remains forbidden.",
    },
    {
        "candidate": "blocked_config_change_request",
        "classification": "Blocked / forbidden for now",
        "review_note": "Rejected-request behavior may be reviewed, but config-change behavior is forbidden.",
    },
)

SCOPE_DRIFT_CHECKLIST = (
    "The task starts implementing a first slice.",
    "The task chooses one job type as the whole phase without explicit confirmation.",
    "The task rewrites or replaces Day1-Day160.",
    "The task replaces Phase 2B-10.",
    "The task creates a second safety matrix.",
    "The task adds runner, adapter, broker, scheduler, queue worker, or execution path.",
    "The task adds SSH, NETCONF, RESTCONF, live device access, or real network execution.",
    "The task adds provider, API, model, token, credential, or secrets handling.",
    "The task changes planning-only status into implementation status.",
    "The task creates real backup, real validation, real command execution, or real config change behavior.",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_11_artifact_created": True,
    "future_plan_created": True,
    "future_plan_is_review_only": True,
    "future_implementation_authorized": False,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "direct_implementation_authorized": False,
    "first_slice_selected": False,
    "first_slice_implemented": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_worker_added": False,
    "background_worker_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "real_device_access_added": False,
    "real_network_execution_added": False,
    "real_backup_added": False,
    "real_validation_added": False,
    "real_command_execution_added": False,
    "real_config_change_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "token_handling_added": False,
    "credential_handling_added": False,
    "secrets_handling_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "phase_2b_10_replaced": False,
    "second_safety_matrix_created": False,
    "future_scope_drift_items_listed": True,
    "current_scope_drift_detected": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_11_PROJECT_CONSOLIDATION_ENTRY_MAP_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "FUTURE_PLAN_CREATED",
    "FUTURE_PLAN_IS_REVIEW_ONLY",
    "FUTURE_IMPLEMENTATION_AUTHORIZED_FALSE",
    "FIRST_SLICE_SELECTED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "CURRENT_SCOPE_DRIFT_DETECTED_FALSE",
    "FUTURE_SCOPE_DRIFT_ITEMS_LISTED",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_FALSE",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_FALSE",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_FALSE",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_11": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_11_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")

    agents = report.get("agents_md_pre_read", {})
    if not isinstance(agents, Mapping):
        errors.append("AGENTS_MD_PRE_READ_NOT_OBJECT")
    else:
        if agents.get("found") is not True:
            errors.append("AGENTS_MD_FOUND_NOT_TRUE")
        if agents.get("read_before_changes") is not True:
            errors.append("AGENTS_MD_READ_BEFORE_CHANGES_NOT_TRUE")
        if agents.get("modified") is not False:
            errors.append("AGENTS_MD_MODIFIED_NOT_FALSE")

    if report.get("phase_2b_10_verdict_referenced") != PHASE_2B_10_VERDICT:
        errors.append("PHASE_2B_10_VERDICT_NOT_REFERENCED")
    if set(report.get("example_job_types", [])) != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    future_plan = report.get("future_plan", {})
    if not isinstance(future_plan, Mapping):
        errors.append("FUTURE_PLAN_NOT_OBJECT")
        future_plan = {}
    required_future_sections = (
        "recommended_next_planning_steps",
        "future_implementation_entry_conditions",
        "first_slice_candidate_path",
        "scope_drift_checklist",
        "current_drift_verdict",
    )
    for section in required_future_sections:
        if section not in future_plan:
            errors.append(f"FUTURE_PLAN_SECTION_MISSING:{section}")

    steps = future_plan.get("recommended_next_planning_steps", [])
    required_step_fields = {
        "step",
        "suggested_phase_task",
        "purpose",
        "allowed_now",
        "implementation_involved",
        "risk_of_scope_drift",
        "required_gate_before_proceeding",
    }
    if len(steps) != len(FUTURE_PLAN_STEPS):
        errors.append("FUTURE_PLAN_STEP_COUNT_MISMATCH")
    for index, row in enumerate(steps):
        if not isinstance(row, Mapping):
            errors.append(f"FUTURE_PLAN_STEP_NOT_OBJECT:{index}")
            continue
        for field in sorted(required_step_fields.difference(row)):
            errors.append(f"FUTURE_PLAN_STEP_FIELD_MISSING:{index}:{field}")

    if set(future_plan.get("future_implementation_entry_conditions", [])) != set(
        FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS
    ):
        errors.append("FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS_MISMATCH")
    if len(future_plan.get("first_slice_candidate_path", [])) != len(FIRST_SLICE_CANDIDATES):
        errors.append("FIRST_SLICE_CANDIDATE_COUNT_MISMATCH")
    if set(item.get("candidate") for item in future_plan.get("first_slice_candidate_path", [])) != set(
        REQUIRED_JOB_TYPES
    ):
        errors.append("FIRST_SLICE_CANDIDATE_SET_MISMATCH")
    if set(future_plan.get("scope_drift_checklist", [])) != set(SCOPE_DRIFT_CHECKLIST):
        errors.append("SCOPE_DRIFT_CHECKLIST_MISMATCH")

    verdict = future_plan.get("current_drift_verdict", {})
    expected_drift_verdict = {
        "CURRENT_SCOPE_DRIFT_DETECTED": "NO",
        "FUTURE_PLAN_IS_REVIEW_ONLY": "YES",
        "FUTURE_IMPLEMENTATION_AUTHORIZED": "NO",
        "FIRST_SLICE_SELECTED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
    }
    if verdict != expected_drift_verdict:
        errors.append("CURRENT_DRIFT_VERDICT_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_machine_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "FUTURE_PLAN_CREATED": "YES",
        "FUTURE_PLAN_IS_REVIEW_ONLY": "YES",
        "FUTURE_IMPLEMENTATION_AUTHORIZED": "NO",
        "FIRST_SLICE_SELECTED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "CURRENT_SCOPE_DRIFT_DETECTED": "NO",
        "FUTURE_SCOPE_DRIFT_ITEMS_LISTED": "YES",
        "NEXT_RECOMMENDED_STEP": "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
    }
    if report.get("machine_readable_verdict") != expected_machine_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(report.get(flag) for flag in (
        "current_scope_drift_detected",
        "future_implementation_authorized",
        "first_slice_selected",
        "first_slice_implemented",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "live_device_access_added",
        "provider_calls_added",
        "api_calls_added",
        "model_calls_added",
        "secrets_handling_added",
        "day1_day160_rewritten_or_replaced",
        "phase_2b_10_replaced",
        "second_safety_matrix_created",
    )):
        errors.append("NEEDS_SCOPE_CONFIRMATION")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "future_plan_steps_checked": len(steps),
        "entry_conditions_checked": len(future_plan.get("future_implementation_entry_conditions", [])),
        "first_slice_candidates_checked": len(future_plan.get("first_slice_candidate_path", [])),
        "scope_drift_items_checked": len(future_plan.get("scope_drift_checklist", [])),
    }


def build_phase_2b_11_project_consolidation_entry_map_report() -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_changes": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "phase_goal": PHASE_GOAL,
        "phase_2b_10_verdict_referenced": PHASE_2B_10_VERDICT,
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "future_plan": {
            "recommended_next_planning_steps": list(deepcopy(FUTURE_PLAN_STEPS)),
            "future_implementation_entry_conditions": list(FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS),
            "first_slice_candidate_path": list(deepcopy(FIRST_SLICE_CANDIDATES)),
            "scope_drift_checklist": list(SCOPE_DRIFT_CHECKLIST),
            "current_drift_verdict": {
                "CURRENT_SCOPE_DRIFT_DETECTED": "NO",
                "FUTURE_PLAN_IS_REVIEW_ONLY": "YES",
                "FUTURE_IMPLEMENTATION_AUTHORIZED": "NO",
                "FIRST_SLICE_SELECTED": "NO",
                "FIRST_SLICE_IMPLEMENTED": "NO",
            },
        },
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_implementation_statement": (
            "This artifact is review-only planning. It does not authorize implementation, "
            "start implementation, select a final first slice, create future phases, or add "
            "runner, adapter, execution, SSH, NETCONF, RESTCONF, live-device, provider, API, "
            "model, or secrets-handling paths."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "FUTURE_PLAN_CREATED": "YES",
            "FUTURE_PLAN_IS_REVIEW_ONLY": "YES",
            "FUTURE_IMPLEMENTATION_AUTHORIZED": "NO",
            "FIRST_SLICE_SELECTED": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "CURRENT_SCOPE_DRIFT_DETECTED": "NO",
            "FUTURE_SCOPE_DRIFT_ITEMS_LISTED": "YES",
            "NEXT_RECOMMENDED_STEP": "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "future_plan_created": True,
            "future_plan_is_review_only": True,
            "future_implementation_authorized": False,
            "first_slice_selected": False,
            "first_slice_implemented": False,
            "current_scope_drift_detected": False,
            "future_scope_drift_items_listed": True,
            "next_recommended_step": "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_11_report(report)
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


def _table_rows(values: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> str:
    return "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in fields) + "</tr>"
        for item in values
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    future_plan = report["future_plan"]
    output_path.write_text(
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
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_implementation_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>11. Future Plan and Drift Check</h2>
  <h3>A. Recommended next planning steps</h3>
  <table>
    <thead><tr><th>Step</th><th>Suggested phase/task</th><th>Purpose</th><th>Allowed now?</th><th>Implementation involved?</th><th>Risk of scope drift</th><th>Required gate before proceeding</th></tr></thead>
    <tbody>{_table_rows(future_plan["recommended_next_planning_steps"], ("step", "suggested_phase_task", "purpose", "allowed_now", "implementation_involved", "risk_of_scope_drift", "required_gate_before_proceeding"))}</tbody>
  </table>
  <h3>B. Future implementation entry conditions</h3>
  <ul>{_list_items(future_plan["future_implementation_entry_conditions"])}</ul>
  <h3>C. First-slice candidate path</h3>
  <table>
    <thead><tr><th>Candidate</th><th>Classification</th><th>Review note</th></tr></thead>
    <tbody>{_table_rows(future_plan["first_slice_candidate_path"], ("candidate", "classification", "review_note"))}</tbody>
  </table>
  <h3>D. Items that would indicate scope drift</h3>
  <ul>{_list_items(future_plan["scope_drift_checklist"])}</ul>
  <h3>E. Current drift verdict</h3>
  <table><tbody>{_dict_rows(future_plan["current_drift_verdict"])}</tbody></table>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_11_project_consolidation_entry_map_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_11_project_consolidation_entry_map_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_11_project_consolidation_entry_map(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_11_project_consolidation_entry_map_report()
    json_path, html_path = write_phase_2b_11_project_consolidation_entry_map_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"future_plan_created: {str(report['summary']['future_plan_created']).lower()}")
    print(f"future_plan_is_review_only: {str(report['summary']['future_plan_is_review_only']).lower()}")
    print(f"future_implementation_authorized: {str(report['summary']['future_implementation_authorized']).lower()}")
    print(f"first_slice_selected: {str(report['summary']['first_slice_selected']).lower()}")
    print(f"first_slice_implemented: {str(report['summary']['first_slice_implemented']).lower()}")
    print(f"current_scope_drift_detected: {str(report['summary']['current_scope_drift_detected']).lower()}")
    print(f"future_scope_drift_items_listed: {str(report['summary']['future_scope_drift_items_listed']).lower()}")
    print(f"next_recommended_step: {report['summary']['next_recommended_step']}")
    print(f"runner_added: {str(report['runner_added']).lower()}")
    print(f"adapter_added: {str(report['adapter_added']).lower()}")
    print(f"execution_path_added: {str(report['execution_path_added']).lower()}")
    print(f"ssh_touched: {str(report['ssh_touched']).lower()}")
    print(f"netconf_touched: {str(report['netconf_touched']).lower()}")
    print(f"restconf_touched: {str(report['restconf_touched']).lower()}")
    print(f"live_device_access_added: {str(report['live_device_access_added']).lower()}")
    print(f"provider_api_model_secrets_touched: false")
    print(f"Future plan steps checked: {report['validation']['future_plan_steps_checked']}")
    print(f"Entry conditions checked: {report['validation']['entry_conditions_checked']}")
    print(f"First-slice candidates checked: {report['validation']['first_slice_candidates_checked']}")
    print(f"Scope drift items checked: {report['validation']['scope_drift_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
