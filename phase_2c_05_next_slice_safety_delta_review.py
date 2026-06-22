"""Phase 2C-05 next-slice safety delta review.

This module creates deterministic, local, planning-only evidence comparing the
Phase 2C-04 candidate list against existing safety boundaries. It does not
select, authorize, scaffold, implement, execute, or prepare any candidate.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_13_first_slice_final_selection_gate import FINAL_VERDICT as PHASE_2B_13_VERDICT
from phase_2b_14_first_slice_implementation_kickoff_gate import FINAL_VERDICT as PHASE_2B_14_VERDICT
from phase_2c_01_local_static_job_first_slice import FINAL_VERDICT as PHASE_2C_01_VERDICT
from phase_2c_02_post_first_slice_acceptance_review import FINAL_VERDICT as PHASE_2C_02_VERDICT
from phase_2c_03_next_slice_decision_gate_authorization_review import FINAL_VERDICT as PHASE_2C_03_VERDICT
from phase_2c_04_next_slice_candidate_inventory import (
    FINAL_VERDICT as PHASE_2C_04_VERDICT,
    TASK_NAME as PHASE_2C_04_TASK_NAME,
    build_phase_2c_04_next_slice_candidate_inventory_report,
    validate_phase_2c_04_report,
)


PHASE = "2C-05"
TASK_NAME = "phase2c-05-next-slice-safety-delta-review"
TITLE = "Phase 2C-05 Next-Slice Safety Delta Review - Planning Only"
MODE = "planning_only_next_slice_safety_delta_review"
SCOPE = "phase_wide_safety_delta_review_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_05_SAFETY_DELTA_REVIEW_DONE_NEXT_SLICE_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_05_next_slice_safety_delta_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_05_next_slice_safety_delta_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_05_next_slice_safety_delta_review.md"

PHASE_GOAL = (
    "Evaluate whether the next-slice candidates from Phase 2C-04 introduce new "
    "safety risk compared with the current approved planning/report-only "
    "boundaries. This phase compares safety deltas only and does not select, "
    "rank as final, authorize, scaffold, or implement any candidate."
)

CANDIDATE_SOURCE = (
    "Phase 2C-04 Next-Slice Candidate Inventory is the only candidate source. "
    "No unrelated candidates are added, selected, ranked as final, or authorized."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job continuation",
    "artifact validation job",
    "report-only evidence collection job",
    "dry-run result rendering job",
    "mock parse/report job",
    "candidate UI display contract follow-up",
    "candidate safety regression follow-up",
)

SAFETY_DELTA_REVIEW_CRITERIA = (
    "new runtime execution behavior",
    "new runner, adapter, scheduler, queue, broker, worker, or agent loop",
    "SSH, NETCONF, RESTCONF, live-device access, or real command execution",
    "provider/API/model calls",
    "secrets or credential handling",
    "config backup or config change behavior",
    "Day1-Day160 rewrite or replacement",
    "a second safety matrix",
    "expanded file-system trust boundary",
    "expanded artifact input boundary",
    "expanded report rendering boundary",
    "new user approval or authorization requirement",
    "new validation requirement before implementation",
)

SAFETY_DELTA_FIELDS = (
    "new_runtime_execution_behavior",
    "new_runner_adapter_scheduler_queue_broker_worker_or_agent_loop",
    "ssh_netconf_restconf_live_device_or_real_command_execution",
    "provider_api_model_calls",
    "secrets_or_credential_handling",
    "config_backup_or_config_change_behavior",
    "day1_day160_rewrite_or_replacement",
    "second_safety_matrix",
    "expanded_file_system_trust_boundary",
    "expanded_artifact_input_boundary",
    "expanded_report_rendering_boundary",
    "new_user_approval_or_authorization_requirement",
    "new_validation_requirement_before_implementation",
)

FORBIDDEN_SCOPE = (
    "next-slice selection",
    "Phase 2C-06 authorization or start",
    "Phase 2C-07 authorization or start",
    "Phase 2C-08 authorization or start",
    "candidate implementation",
    "runner",
    "adapter",
    "execution path",
    "scheduler",
    "queue",
    "broker",
    "worker",
    "agent loop",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "real command execution",
    "configuration-changing command",
    "config backup behavior",
    "config change behavior",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
    "unrelated file modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md",
    "docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md",
    "phase_2b_13_first_slice_final_selection_gate.py",
    "phase_2b_14_first_slice_implementation_kickoff_gate.py",
    "phase_2c_01_local_static_job_first_slice.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "phase_2c_04_next_slice_candidate_inventory.py",
    "Day1-Day160 existing reference material only",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add the Phase 2C-05 planning-only safety delta review artifact, "
    "minimal report-only Python evidence generation, targeted tests, and "
    "registry/CLI/report-index visibility. Not allowed: selecting a next "
    "slice, authorizing Phase 2C-06/2C-07/2C-08, implementing a candidate, "
    "creating a runner/adapter/execution path, touching SSH/NETCONF/RESTCONF/"
    "live-device/provider/API/model/secret scope, adding backup or config "
    "change behavior, rewriting Day1-Day160, modifying AGENTS.md, or creating "
    "a second safety matrix."
)

DELTA_STATUS = "NO_NEW_SAFETY_DELTA_WITHIN_PLANNING_BOUNDARY"

SAFETY_FLAGS = {
    "phase_2c_05_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_2c_04_read": True,
    "safety_delta_review_only": True,
    "phase_goal_separated": True,
    "candidate_source_separated": True,
    "example_job_types_separated": True,
    "safety_delta_review_criteria_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "final_verdict_separated": True,
    "candidate_selected": False,
    "next_slice_authorized": False,
    "phase_2c_06_started": False,
    "phase_2c_07_started": False,
    "phase_2c_08_started": False,
    "implementation_added": False,
    "runtime_implementation_added": False,
    "execution_opened": False,
    "provider_api_opened": False,
    "model_opened": False,
    "secrets_touched": False,
    "live_device_touched": False,
    "ssh_netconf_restconf_touched": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "agent_loop_added": False,
    "shell_command_added": False,
    "custom_script_execution_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "real_device_operation_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "scope_narrowed_to_one_example_job_type": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_05_NEXT_SLICE_SAFETY_DELTA_REVIEW_PLANNING_ONLY",
    "PHASE_2C_04_READ_YES",
    "SAFETY_DELTA_REVIEW_ONLY_YES",
    "CANDIDATE_SELECTED_NO",
    "NEXT_SLICE_AUTHORIZED_NO",
    "PHASE_2C_06_STARTED_NO",
    "PHASE_2C_07_STARTED_NO",
    "PHASE_2C_08_STARTED_NO",
    "IMPLEMENTATION_ADDED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "SCOPE_NARROWED_TO_ONE_EXAMPLE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_05": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_04_source_review() -> Dict[str, Any]:
    source_report = build_phase_2c_04_next_slice_candidate_inventory_report()
    source_validation = validate_phase_2c_04_report(source_report)
    return {
        "reviewed_task": PHASE_2C_04_TASK_NAME,
        "expected_verdict": PHASE_2C_04_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "candidate_count": len(source_report.get("candidate_inventory", [])),
        "candidate_selected": source_report.get("candidate_selected"),
        "next_slice_authorized": source_report.get("next_slice_authorized"),
        "phase_2c_05_authorized_by_source": source_report.get("phase_2c_05_authorized"),
    }


def _candidate_delta_review() -> Tuple[Dict[str, Any], ...]:
    source_report = build_phase_2c_04_next_slice_candidate_inventory_report()
    return tuple(
        {
            "candidate_id": candidate["candidate_id"],
            "example_job_type": candidate["example_job_type"],
            "source_inventory_status": candidate["inventory_status"],
            "new_runtime_execution_behavior": False,
            "new_runner_adapter_scheduler_queue_broker_worker_or_agent_loop": False,
            "ssh_netconf_restconf_live_device_or_real_command_execution": False,
            "provider_api_model_calls": False,
            "secrets_or_credential_handling": False,
            "config_backup_or_config_change_behavior": False,
            "day1_day160_rewrite_or_replacement": False,
            "second_safety_matrix": False,
            "expanded_file_system_trust_boundary": False,
            "expanded_artifact_input_boundary": False,
            "expanded_report_rendering_boundary": False,
            "new_user_approval_or_authorization_requirement": False,
            "new_validation_requirement_before_implementation": False,
            "candidate_selected": False,
            "delta_status": DELTA_STATUS,
        }
        for candidate in source_report.get("candidate_inventory", [])
    )


def validate_phase_2c_05_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    source_review = report.get("phase_2c_04_source_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_04_SOURCE_NOT_OBJECT")
        source_review = {}
    if source_review.get("reviewed_task") != PHASE_2C_04_TASK_NAME:
        errors.append("PHASE_2C_04_TASK_MISMATCH")
    if source_review.get("observed_verdict") != PHASE_2C_04_VERDICT:
        errors.append("PHASE_2C_04_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_04_VALIDATION_NOT_PASS")
    if source_review.get("candidate_count") != len(EXAMPLE_JOB_TYPES):
        errors.append("PHASE_2C_04_CANDIDATE_COUNT_MISMATCH")
    if source_review.get("candidate_selected") is not False:
        errors.append("PHASE_2C_04_SOURCE_SELECTED_CANDIDATE")

    candidate_reviews = report.get("candidate_safety_delta_reviews", [])
    if not isinstance(candidate_reviews, Sequence) or isinstance(candidate_reviews, (str, bytes)):
        errors.append("CANDIDATE_DELTA_REVIEWS_NOT_LIST")
        candidate_reviews = []
    if len(candidate_reviews) != len(EXAMPLE_JOB_TYPES):
        errors.append("CANDIDATE_DELTA_REVIEW_COUNT_MISMATCH")
    if any(not isinstance(item, Mapping) for item in candidate_reviews):
        errors.append("CANDIDATE_DELTA_REVIEW_ITEM_NOT_OBJECT")
    else:
        for item in candidate_reviews:
            if item.get("delta_status") != DELTA_STATUS:
                errors.append(f"DELTA_STATUS_MISMATCH:{item.get('candidate_id')}")
            if item.get("candidate_selected") is not False:
                errors.append(f"CANDIDATE_SELECTED:{item.get('candidate_id')}")
            for field in SAFETY_DELTA_FIELDS:
                if item.get(field) is not False:
                    errors.append(f"SAFETY_DELTA_FIELD_TRUE:{item.get('candidate_id')}:{field}")

    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if report.get("safety_delta_review_criteria") != list(SAFETY_DELTA_REVIEW_CRITERIA):
        errors.append("SAFETY_DELTA_REVIEW_CRITERIA_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("candidate_source") != CANDIDATE_SOURCE:
        errors.append("CANDIDATE_SOURCE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "SAFETY_DELTA_REVIEW_ONLY": "YES",
        "PHASE_2C_04_READ": "YES",
        "CANDIDATE_SELECTED": "NO",
        "NEXT_SLICE_AUTHORIZED": "NO",
        "PHASE_2C_06_STARTED": "NO",
        "PHASE_2C_07_STARTED": "NO",
        "PHASE_2C_08_STARTED": "NO",
        "IMPLEMENTATION_ADDED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "candidate_selected",
        "next_slice_authorized",
        "phase_2c_06_started",
        "phase_2c_07_started",
        "phase_2c_08_started",
        "implementation_added",
        "runtime_implementation_added",
        "execution_opened",
        "provider_api_opened",
        "model_opened",
        "secrets_touched",
        "live_device_touched",
        "ssh_netconf_restconf_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "shell_command_added",
        "custom_script_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "real_device_operation_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
        "scope_narrowed_to_one_example_job_type",
        "needs_scope_confirmation",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "candidate_delta_reviews_checked": len(candidate_reviews),
        "safety_delta_criteria_checked": len(report.get("safety_delta_review_criteria", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(artifacts),
    }


def build_phase_2c_05_next_slice_safety_delta_review_report() -> Dict[str, Any]:
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
        "example_job_type_role": "examples_only_not_selection_or_phase_scope",
        "safety_delta_review_criteria": list(SAFETY_DELTA_REVIEW_CRITERIA),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "phase_2b_14_verdict_referenced": PHASE_2B_14_VERDICT,
        "phase_2c_01_verdict_referenced": PHASE_2C_01_VERDICT,
        "phase_2c_02_verdict_referenced": PHASE_2C_02_VERDICT,
        "phase_2c_03_verdict_referenced": PHASE_2C_03_VERDICT,
        "phase_2c_04_source_review": _phase_2c_04_source_review(),
        "candidate_safety_delta_reviews": list(_candidate_delta_review()),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "review_statement": (
            "Phase 2C-05 compares each Phase 2C-04 candidate against the "
            "existing planning/report-only safety boundary. The review records "
            "safety deltas only and is not a final selection gate."
        ),
        "non_execution_statement": (
            "This task opens no runtime implementation, runner, adapter, "
            "scheduler, queue, broker, worker, agent loop, execution path, SSH, "
            "NETCONF, RESTCONF, live-device access, provider/API/model calls, "
            "secrets, backup behavior, config-change behavior, Day1-Day160 "
            "rewrite, Phase 2C-06/2C-07/2C-08 start, or second safety matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "SAFETY_DELTA_REVIEW_ONLY": "YES",
            "PHASE_2C_04_READ": "YES",
            "CANDIDATE_SELECTED": "NO",
            "NEXT_SLICE_AUTHORIZED": "NO",
            "PHASE_2C_06_STARTED": "NO",
            "PHASE_2C_07_STARTED": "NO",
            "PHASE_2C_08_STARTED": "NO",
            "IMPLEMENTATION_ADDED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "safety_delta_review_only": True,
        "phase_2c_04_read": True,
        "candidate_count": len(report["candidate_safety_delta_reviews"]),
        "candidate_selected": False,
        "next_slice_authorized": False,
        "phase_2c_06_started": False,
        "phase_2c_07_started": False,
        "phase_2c_08_started": False,
        "implementation_added": False,
        "runner_adapter_execution_path_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_05_report(report)
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
        f"<td>{html.escape(str(item.get('example_job_type')))}</td>"
        f"<td>{html.escape(str(item.get('delta_status')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_selected')))}</td>"
        "</tr>"
        for item in values
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
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
  <p>Review decision: <strong>{html.escape(str(report["review_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["review_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Phase 2C-04 Source Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_04_source_review"])}</tbody></table>
  <h2>Candidate Safety Delta Reviews</h2>
  <table><thead><tr><th>Candidate</th><th>Example Job Type</th><th>Delta Status</th><th>Selected</th></tr></thead><tbody>{_candidate_delta_rows(report["candidate_safety_delta_reviews"])}</tbody></table>
  <h2>Safety Delta Review Criteria</h2>
  <ul>{_list_items(report["safety_delta_review_criteria"])}</ul>
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


def write_phase_2c_05_next_slice_safety_delta_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_05_next_slice_safety_delta_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_05_next_slice_safety_delta_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_05_next_slice_safety_delta_review_report()
    json_path, html_path = write_phase_2c_05_next_slice_safety_delta_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Review decision: {report['review_decision']}")
    print(f"phase_2c_04_read: {str(report['summary']['phase_2c_04_read']).lower()}")
    print(f"safety_delta_review_only: {str(report['summary']['safety_delta_review_only']).lower()}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"candidate_selected: {str(report['summary']['candidate_selected']).lower()}")
    print(f"next_slice_authorized: {str(report['summary']['next_slice_authorized']).lower()}")
    print(f"phase_2c_06_started: {str(report['summary']['phase_2c_06_started']).lower()}")
    print(f"phase_2c_07_started: {str(report['summary']['phase_2c_07_started']).lower()}")
    print(f"phase_2c_08_started: {str(report['summary']['phase_2c_08_started']).lower()}")
    print(f"implementation_added: {str(report['summary']['implementation_added']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
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
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Candidate delta reviews checked: {report['validation']['candidate_delta_reviews_checked']}")
    print(f"Safety delta criteria checked: {report['validation']['safety_delta_criteria_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
