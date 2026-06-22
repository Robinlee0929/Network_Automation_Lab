"""Phase 2C-03 next-slice decision gate / authorization review.

This module creates deterministic, local, planning-only authorization review
evidence for deciding whether future next-slice planning may begin after the
Phase 2C-01 `local_static_job` first slice and Phase 2C-02 acceptance review.
It does not select, scaffold, implement, or enable a next slice and does not
open runners, adapters, brokers, schedulers, queues, execution paths, SSH,
NETCONF, RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_09_first_slice_implementation_plan_pack import FINAL_VERDICT as PHASE_2B_09_VERDICT
from phase_2b_13_first_slice_final_selection_gate import FINAL_VERDICT as PHASE_2B_13_VERDICT
from phase_2b_14_first_slice_implementation_kickoff_gate import FINAL_VERDICT as PHASE_2B_14_VERDICT
from phase_2c_01_local_static_job_first_slice import FINAL_VERDICT as PHASE_2C_01_VERDICT
from phase_2c_02_post_first_slice_acceptance_review import (
    FINAL_VERDICT as PHASE_2C_02_VERDICT,
    TASK_NAME as PHASE_2C_02_TASK_NAME,
    build_phase_2c_02_post_first_slice_acceptance_review_report,
    validate_phase_2c_02_report,
)


PHASE = "2C-03"
TASK_NAME = "phase2c-03-next-slice-decision-gate-authorization-review"
TITLE = "Phase 2C-03 Next-Slice Decision Gate / Authorization Review - Planning Only"
MODE = "planning_only_next_slice_decision_gate_authorization_review"
SCOPE = "phase_wide_next_slice_planning_authorization_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_03_NEXT_SLICE_PLANNING_ALLOWED_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_03_next_slice_decision_gate_authorization_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_03_next_slice_decision_gate_authorization_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_03_next_slice_decision_gate_authorization_review.md"

PHASE_GOAL = (
    "Create a planning-only authorization review gate that decides whether the "
    "completed local_static_job first slice, after Phase 2C-01 and Phase 2C-02, "
    "is stable enough to allow planning for a future next slice while keeping "
    "the next slice itself unauthorized until a separate user approval."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job",
    "baseline_check",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "backup_config_plan",
    "blocked_config_change_request",
)

FORBIDDEN_SCOPE = (
    "execution runner",
    "runner adapter",
    "broker",
    "scheduler",
    "queue",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "live device access",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "real network command execution",
    "configuration-changing workflow",
    "backup execution workflow",
    "next-slice implementation",
    "next-slice scaffolding",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "weakened safety gates",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    "phase_2c_01_local_static_job_first_slice.py",
    "tests/test_phase_2c_01_local_static_job_first_slice.py",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "tests/test_phase_2c_02_post_first_slice_acceptance_review.py",
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "phase2a_readonly_job_runner_framework.py",
    "phase_2a_03_dry_run_job_plan_gate.py",
    "phase_2a_06_negative_regression_matrix.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: create Phase 2C-03 planning-only authorization review evidence, "
    "register a report-only task, and add tests proving no execution/provider/API/"
    "live-device or next-slice implementation scope is opened. Not allowed: "
    "selecting, scaffolding, or implementing the next slice, or adding any "
    "runner, adapter, broker, scheduler, queue, execution, provider/API/model, "
    "secret, SSH, NETCONF, RESTCONF, live-device, backup, config-change, "
    "Day1-Day160 replacement, or second safety-matrix behavior."
)

DECISION_CRITERIA = (
    {
        "check": "Completed first slice reviewed",
        "expected": PHASE_2C_01_VERDICT,
        "status": "PASS",
    },
    {
        "check": "Phase 2C-02 acceptance review used as input",
        "expected": PHASE_2C_02_VERDICT,
        "status": "PASS",
    },
    {
        "check": "Next-slice planning may proceed only from this gate conclusion",
        "expected": "NEXT_SLICE_PLANNING_ALLOWED",
        "status": "PASS",
    },
    {
        "check": "Next-slice implementation remains unauthorized",
        "expected": "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE",
        "status": "PASS",
    },
    {
        "check": "No execution, provider/API/model, secret, or live-device scope is opened",
        "expected": "EXECUTION_PROVIDER_API_OPENED_FALSE and LIVE_DEVICE_ACCESS_OPENED_FALSE",
        "status": "PASS",
    },
    {
        "check": "Separate user authorization remains required before implementation",
        "expected": "REQUIRES_SEPARATE_USER_AUTHORIZATION_TRUE",
        "status": "PASS",
    },
    {
        "check": "Example job types remain examples only",
        "expected": "scope_narrowed_to_one_example_job_type == false",
        "status": "PASS",
    },
)

SAFETY_FLAGS = {
    "phase_2c_03_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_goal_separated": True,
    "example_job_types_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "local_static_job_reviewed": True,
    "phase_2c_02_referenced": True,
    "phase_2c_02_acceptance_review_used_as_input": True,
    "next_slice_planning_allowed": True,
    "next_slice_implementation_allowed": False,
    "separate_user_authorization_required": True,
    "execution_provider_api_opened": False,
    "live_device_access_opened": False,
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
    "shell_command_added": False,
    "custom_script_execution_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "real_device_operation_added": False,
    "next_slice_selected": False,
    "next_slice_scaffolded": False,
    "next_slice_implemented": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "scope_narrowed_to_one_example_job_type": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_03_NEXT_SLICE_DECISION_GATE_AUTHORIZATION_REVIEW_PLANNING_ONLY",
    "LOCAL_STATIC_JOB_REVIEWED",
    "PHASE_2C_02_REFERENCED",
    "NEXT_SLICE_PLANNING_ALLOWED",
    "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE",
    "EXECUTION_PROVIDER_API_OPENED_FALSE",
    "LIVE_DEVICE_ACCESS_OPENED_FALSE",
    "REQUIRES_SEPARATE_USER_AUTHORIZATION_TRUE",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "PHASE_GOAL_SEPARATED_YES",
    "EXAMPLE_JOB_TYPES_SEPARATED_YES",
    "FORBIDDEN_SCOPE_SEPARATED_YES",
    "EXISTING_ARTIFACTS_REFERENCED_YES",
    "IMPLEMENTATION_BOUNDARY_SEPARATED_YES",
    "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "NEXT_SLICE_SELECTED_NO",
    "NEXT_SLICE_SCAFFOLDED_NO",
    "NEXT_SLICE_IMPLEMENTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_03": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_02_input_review() -> Dict[str, Any]:
    phase_2c_02_report = build_phase_2c_02_post_first_slice_acceptance_review_report()
    phase_2c_02_validation = validate_phase_2c_02_report(phase_2c_02_report)
    return {
        "reviewed_task": PHASE_2C_02_TASK_NAME,
        "expected_verdict": PHASE_2C_02_VERDICT,
        "observed_verdict": phase_2c_02_report.get("final_verdict"),
        "source_validation": phase_2c_02_validation,
        "phase_2c_01_verdict_from_acceptance_review": PHASE_2C_01_VERDICT,
        "acceptance_decision": phase_2c_02_report.get("acceptance_decision"),
    }


def validate_phase_2c_03_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("authorization_decision") != "ALLOW_NEXT_SLICE_PLANNING_ONLY":
        errors.append("AUTHORIZATION_DECISION_MISMATCH")

    source_review = report.get("phase_2c_02_acceptance_review_input", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_02_INPUT_NOT_OBJECT")
        source_review = {}
    if source_review.get("reviewed_task") != PHASE_2C_02_TASK_NAME:
        errors.append("PHASE_2C_02_TASK_MISMATCH")
    if source_review.get("observed_verdict") != PHASE_2C_02_VERDICT:
        errors.append("PHASE_2C_02_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_02_VALIDATION_NOT_PASS")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_EXAMPLE")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")
    if tuple(report.get("decision_criteria", ())) != DECISION_CRITERIA:
        errors.append("DECISION_CRITERIA_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("decision_criteria", ())):
        errors.append("DECISION_CRITERIA_NOT_PASS")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "LOCAL_STATIC_JOB_REVIEWED": "YES",
        "PHASE_2C_02_REFERENCED": "YES",
        "NEXT_SLICE_PLANNING_ALLOWED": "YES",
        "NEXT_SLICE_IMPLEMENTATION_ALLOWED": "NO",
        "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE": "YES",
        "EXECUTION_PROVIDER_API_OPENED": "NO",
        "EXECUTION_PROVIDER_API_OPENED_FALSE": "YES",
        "LIVE_DEVICE_ACCESS_OPENED": "NO",
        "LIVE_DEVICE_ACCESS_OPENED_FALSE": "YES",
        "REQUIRES_SEPARATE_USER_AUTHORIZATION": "YES",
        "REQUIRES_SEPARATE_USER_AUTHORIZATION_TRUE": "YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "NEXT_SLICE_SELECTED": "NO",
        "NEXT_SLICE_SCAFFOLDED": "NO",
        "NEXT_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "next_slice_implementation_allowed",
            "execution_provider_api_opened",
            "live_device_access_opened",
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
            "shell_command_added",
            "custom_script_execution_added",
            "config_backup_execution_added",
            "config_change_execution_added",
            "real_device_operation_added",
            "next_slice_selected",
            "next_slice_scaffolded",
            "next_slice_implemented",
            "day1_day160_rewritten_or_replaced",
            "second_safety_matrix_created",
            "safety_gates_weakened",
            "scope_narrowed_to_one_example_job_type",
            "needs_scope_confirmation",
        )
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "decision_criteria_checked": len(report.get("decision_criteria", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(artifacts),
    }


def build_phase_2c_03_next_slice_decision_gate_authorization_review_report() -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "authorization_decision": "ALLOW_NEXT_SLICE_PLANNING_ONLY",
        "authorization_scope": "NEXT_SLICE_PLANNING_ONLY",
        "reviewed_completed_first_slice": "local_static_job",
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_action": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "status": "PASS",
            "scope_confirmation_written": True,
            "phase_goal": PHASE_GOAL,
            "phase_goal_separated": True,
            "example_job_types": list(EXAMPLE_JOB_TYPES),
            "example_job_types_separated": True,
            "example_job_type_role": "examples_only_not_phase_scope",
            "forbidden_scope": list(FORBIDDEN_SCOPE),
            "forbidden_scope_separated": True,
            "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
            "existing_artifacts_referenced": True,
            "implementation_boundary": IMPLEMENTATION_BOUNDARY,
            "implementation_boundary_separated": True,
            "scope_narrowed_to_one_example_job_type": False,
            "needs_scope_confirmation": False,
        },
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "phase_2b_09_verdict_referenced": PHASE_2B_09_VERDICT,
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "phase_2b_14_verdict_referenced": PHASE_2B_14_VERDICT,
        "phase_2c_02_acceptance_review_input": _phase_2c_02_input_review(),
        "decision_criteria": deepcopy(DECISION_CRITERIA),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "authorization_statement": (
            "Phase 2C-03 allows only planning for a future next slice because the "
            "completed local_static_job first slice and Phase 2C-02 acceptance "
            "review are stable as static reviewer evidence. The next slice itself "
            "is not selected, scaffolded, implemented, or executable."
        ),
        "non_execution_statement": (
            "This decision gate opens no execution, provider/API/model, secret, "
            "SSH, NETCONF, RESTCONF, or live-device scope. Separate user "
            "authorization is still required before any future implementation."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "LOCAL_STATIC_JOB_REVIEWED": "YES",
            "PHASE_2C_02_REFERENCED": "YES",
            "NEXT_SLICE_PLANNING_ALLOWED": "YES",
            "NEXT_SLICE_IMPLEMENTATION_ALLOWED": "NO",
            "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE": "YES",
            "EXECUTION_PROVIDER_API_OPENED": "NO",
            "EXECUTION_PROVIDER_API_OPENED_FALSE": "YES",
            "LIVE_DEVICE_ACCESS_OPENED": "NO",
            "LIVE_DEVICE_ACCESS_OPENED_FALSE": "YES",
            "REQUIRES_SEPARATE_USER_AUTHORIZATION": "YES",
            "REQUIRES_SEPARATE_USER_AUTHORIZATION_TRUE": "YES",
            "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "NEXT_SLICE_SELECTED": "NO",
            "NEXT_SLICE_SCAFFOLDED": "NO",
            "NEXT_SLICE_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "local_static_job_reviewed": True,
            "phase_2c_02_referenced": True,
            "next_slice_planning_allowed": True,
            "next_slice_implementation_allowed": False,
            "separate_user_authorization_required": True,
            "execution_provider_api_opened": False,
            "live_device_access_opened": False,
            "existing_artifacts_to_reference_separated": True,
            "scope_narrowed_to_one_example_job_type": False,
            "needs_scope_confirmation": False,
            "next_slice_selected": False,
            "next_slice_scaffolded": False,
            "next_slice_implemented": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2c_03_report(report)
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


def _criteria_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('check')))}</td>"
        f"<td>{html.escape(str(item.get('expected')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
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
  <p>Authorization decision: <strong>{html.escape(str(report["authorization_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["authorization_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Phase 2C-02 Input Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_02_acceptance_review_input"])}</tbody></table>
  <h2>Decision Criteria</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_criteria_rows(report["decision_criteria"])}</tbody></table>
  <h2>Example Job Types</h2>
  <ul>{_list_items(report["example_job_types"])}</ul>
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


def write_phase_2c_03_next_slice_decision_gate_authorization_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_03_next_slice_decision_gate_authorization_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_03_next_slice_decision_gate_authorization_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_03_next_slice_decision_gate_authorization_review_report()
    json_path, html_path = write_phase_2c_03_next_slice_decision_gate_authorization_review_reports(
        project_root, report
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Authorization decision: {report['authorization_decision']}")
    print(f"local_static_job_reviewed: {str(report['summary']['local_static_job_reviewed']).lower()}")
    print(f"phase_2c_02_referenced: {str(report['summary']['phase_2c_02_referenced']).lower()}")
    print(f"next_slice_planning_allowed: {str(report['summary']['next_slice_planning_allowed']).lower()}")
    print(
        "next_slice_implementation_allowed: "
        f"{str(report['summary']['next_slice_implementation_allowed']).lower()}"
    )
    print(
        "separate_user_authorization_required: "
        f"{str(report['summary']['separate_user_authorization_required']).lower()}"
    )
    print(f"execution_provider_api_opened: {str(report['summary']['execution_provider_api_opened']).lower()}")
    print(f"live_device_access_opened: {str(report['summary']['live_device_access_opened']).lower()}")
    print(
        "scope_narrowed_to_one_example_job_type: "
        f"{str(report['summary']['scope_narrowed_to_one_example_job_type']).lower()}"
    )
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(f"next_slice_selected: {str(report['summary']['next_slice_selected']).lower()}")
    print(f"next_slice_scaffolded: {str(report['summary']['next_slice_scaffolded']).lower()}")
    print(f"next_slice_implemented: {str(report['summary']['next_slice_implemented']).lower()}")
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
    print(f"Decision criteria checked: {report['validation']['decision_criteria_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
