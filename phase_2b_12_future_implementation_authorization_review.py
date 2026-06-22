"""Phase 2B-12 future implementation authorization review.

This module creates deterministic, local, planning-only report artifacts for a
phase-wide future implementation authorization review. It does not authorize or
start implementation, select a single job type, create runners, adapters,
brokers, schedulers, queue workers, execution paths, SSH, NETCONF, RESTCONF,
live-device access, provider/API/model calls, secrets handling, backups,
validation, command execution, or real network operations.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_11_project_consolidation_and_implementation_entry_map import (
    FINAL_VERDICT as PHASE_2B_11_VERDICT,
)


PHASE = "2B-12"
TASK_NAME = "phase2b-12-future-implementation-authorization-review-planning-only"
TITLE = "Phase 2B-12 Future Implementation Authorization Review - Planning Only"
MODE = "planning_only_future_implementation_authorization_review"
SCOPE = "phase_wide_future_implementation_authorization_review_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_12_PLANNING_ONLY_COMMITTED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_12_future_implementation_authorization_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_12_future_implementation_authorization_review.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_12_future_implementation_authorization_review.md"

PHASE_GOAL = (
    "Review, phase-wide and planning-only, whether future implementation is currently allowed, "
    "whether Phase 2B must remain planning-only, which conditions are missing before future "
    "implementation can be authorized, whether scope drift risk exists, whether prior Phase 2B "
    "artifacts are sufficient for a later authorization decision, and whether any wording narrows "
    "the phase to only one example job."
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
    "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
    "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
    "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
    "Phase 2B-03 scope confirmation before implementation: no concrete source/doc/test path found; existing Phase 2B-04/05/06 record it as missing/deferred",
    "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
    "docs/phase_2b/phase_2b_11_project_consolidation_and_implementation_entry_map.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "existing Phase 2B planning artifact tests",
)

FORBIDDEN_SCOPE = (
    "real implementation",
    "first-slice implementation",
    "runner",
    "adapter",
    "broker",
    "scheduler",
    "queue worker",
    "execution path",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "real device inventory access",
    "provider call",
    "API call",
    "model call",
    "secrets handling",
    "real backup execution",
    "real configuration change",
    "real VRRP execution",
    "frontend API integration",
    "production workflow",
    "second safety matrix",
    "Day1-Day160 safety design replacement",
    "Day1-Day160 artifact rewrite",
    "single-job implementation plan",
)

MISSING_CONDITIONS_BEFORE_IMPLEMENTATION = (
    "Explicit written owner authorization for implementation",
    "Written scope confirmation that remains phase-wide or explicitly approves any narrower job-specific scope",
    "Final first-slice selection gate after this review",
    "Implementation kickoff gate after final selection",
    "Targeted implementation tests and refusal behavior defined before code changes",
    "Canonical safety boundary reuse without creating a second safety matrix",
    "No Day1-Day160 rewrite, replacement, or superseding artifact",
    "Confirmed no-live, no-SSH, no-NETCONF, no-RESTCONF boundary unless a later live gate separately approves a specific operation",
    "Confirmed no provider/API/model/secrets boundary unless a later provider gate separately approves it",
    "Reviewer-visible rollback and stop behavior for narrowed or unsafe future requests",
)

SCOPE_DRIFT_RISKS = (
    "Treating this review as implementation authorization",
    "Treating one example job type as the whole Phase 2B scope",
    "Creating a first implementation slice during an authorization review",
    "Adding runner, adapter, broker, scheduler, queue worker, or execution path behavior",
    "Adding SSH, NETCONF, RESTCONF, live-device, provider/API/model, or secrets behavior",
    "Creating a second safety matrix instead of referencing Day1-Day160 and Phase 2B artifacts",
    "Replacing or rewriting Day1-Day160 artifacts",
    "Using task title, branch name, filename, implementation goal, or artifact wording to narrow the phase without written scope confirmation",
)

AUTHORIZATION_REVIEW = {
    "future_implementation_currently_allowed": "NO",
    "phase_2b_must_remain_planning_only": "YES",
    "previous_phase_2b_artifacts_sufficient_for_later_decision": "PARTIAL",
    "previous_artifact_sufficiency_note": (
        "The Phase 2B chain is sufficient as evidence for a later authorization review, "
        "but it is not itself sufficient to authorize implementation."
    ),
    "scope_drift_risk_present": "YES",
    "task_wording_narrows_phase_to_one_example": "NO",
    "needs_scope_confirmation_behavior": BLOCKED_VERDICT,
}

SAFETY_FLAGS = {
    "phase_2b_12_artifact_created": True,
    "phase_2b_planning_only_authorized": True,
    "future_implementation_authorized": False,
    "phase_2b_remains_planning_only": True,
    "missing_conditions_listed": True,
    "scope_drift_risk_reviewed": True,
    "needs_scope_confirmation_behavior_included": True,
    "previous_phase_2b_artifacts_sufficient_for_later_decision": False,
    "example_job_types_treated_as_examples_only": True,
    "task_wording_narrows_phase_to_one_example": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "first_slice_implemented": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_worker_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "real_device_inventory_access_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "secrets_handling_added": False,
    "frontend_api_integration_added": False,
    "production_workflow_added": False,
    "real_backup_execution_added": False,
    "real_configuration_change_added": False,
    "real_vrrp_execution_added": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_12_FUTURE_IMPLEMENTATION_AUTHORIZATION_REVIEW_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "FUTURE_IMPLEMENTATION_AUTHORIZED_FALSE",
    "PHASE_2B_REMAINS_PLANNING_ONLY",
    "MISSING_CONDITIONS_LISTED",
    "SCOPE_DRIFT_RISK_REVIEWED",
    "NEEDS_SCOPE_CONFIRMATION_BEHAVIOR_INCLUDED",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_FALSE",
    "SECOND_SAFETY_MATRIX_CREATED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
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
            "allowed_by_phase_2b_12": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_12_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    scope_confirmation = report.get("scope_confirmation", {})
    if not isinstance(scope_confirmation, Mapping):
        errors.append("SCOPE_CONFIRMATION_NOT_OBJECT")
        scope_confirmation = {}
    for field in (
        "phase_goal",
        "example_job_types",
        "forbidden_scope",
        "existing_artifacts_to_reference",
        "implementation_boundary",
    ):
        if field not in scope_confirmation:
            errors.append(f"SCOPE_CONFIRMATION_FIELD_MISSING:{field}")
    if scope_confirmation.get("status") != "PASS":
        errors.append("SCOPE_CONFIRMATION_NOT_PASS")
    if scope_confirmation.get("needs_scope_confirmation") is not False:
        errors.append("NEEDS_SCOPE_CONFIRMATION_NOT_FALSE")
    if scope_confirmation.get("scope_narrowed_to_one_example") is not False:
        errors.append("SCOPE_NARROWED_TO_ONE_EXAMPLE")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")
    if report.get("phase_2b_11_verdict_referenced") != PHASE_2B_11_VERDICT:
        errors.append("PHASE_2B_11_VERDICT_NOT_REFERENCED")

    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if set(report.get("missing_conditions_before_implementation", [])) != set(
        MISSING_CONDITIONS_BEFORE_IMPLEMENTATION
    ):
        errors.append("MISSING_CONDITIONS_MISMATCH")
    if set(report.get("scope_drift_risks", [])) != set(SCOPE_DRIFT_RISKS):
        errors.append("SCOPE_DRIFT_RISKS_MISMATCH")
    if report.get("authorization_review") != AUTHORIZATION_REVIEW:
        errors.append("AUTHORIZATION_REVIEW_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "FUTURE_IMPLEMENTATION_AUTHORIZED_BY_THIS_TASK": "NO",
        "PHASE_2B_REMAINS_PLANNING_ONLY": "YES",
        "MISSING_CONDITIONS_LISTED": "YES",
        "SCOPE_DRIFT_RISK_REVIEWED": "YES",
        "NEEDS_SCOPE_CONFIRMATION_BEHAVIOR_INCLUDED": "YES",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "future_implementation_authorized",
            "task_wording_narrows_phase_to_one_example",
            "day1_day160_rewritten_or_replaced",
            "second_safety_matrix_created",
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
        )
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(artifacts),
        "missing_conditions_checked": len(report.get("missing_conditions_before_implementation", [])),
        "scope_drift_risks_checked": len(report.get("scope_drift_risks", [])),
    }


def build_phase_2b_12_future_implementation_authorization_review_report() -> Dict[str, Any]:
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
        "scope_confirmation": {
            "status": "PASS",
            "phase_goal": PHASE_GOAL,
            "example_job_types": list(REQUIRED_JOB_TYPES),
            "example_job_type_role": "examples_only_not_phase_scope",
            "forbidden_scope": list(FORBIDDEN_SCOPE),
            "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
            "implementation_boundary": (
                "planning artifact and validation only; no implementation slice, runner, adapter, broker, "
                "scheduler, queue worker, execution path, SSH, NETCONF, RESTCONF, live-device, provider/API/model, "
                "secrets, backup, VRRP execution, frontend API, production workflow, second safety matrix, "
                "or Day1-Day160 rewrite/replacement"
            ),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "phase_2b_11_verdict_referenced": PHASE_2B_11_VERDICT,
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "authorization_review": dict(AUTHORIZATION_REVIEW),
        "missing_conditions_before_implementation": list(MISSING_CONDITIONS_BEFORE_IMPLEMENTATION),
        "scope_drift_risks": list(SCOPE_DRIFT_RISKS),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "planning_only_boundary": (
            "Phase 2B-12 is a planning-only authorization review. It does not authorize implementation, "
            "does not choose a single implementation target, and must stop with NEEDS_SCOPE_CONFIRMATION "
            "if future scope is narrowed without written confirmation."
        ),
        "decision": (
            "Future implementation is not yet authorized. Phase 2B-12 does not authorize implementation. "
            "Phase 2B remains planning-only. Any future implementation requires explicit written authorization."
        ),
        "non_authorization_statement": (
            "This artifact is not an implementation approval, kickoff, runner, adapter, execution path, "
            "provider/API/model/secrets approval, live-device approval, second safety matrix, or Day1-Day160 replacement."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "FUTURE_IMPLEMENTATION_AUTHORIZED_BY_THIS_TASK": "NO",
            "PHASE_2B_REMAINS_PLANNING_ONLY": "YES",
            "MISSING_CONDITIONS_LISTED": "YES",
            "SCOPE_DRIFT_RISK_REVIEWED": "YES",
            "NEEDS_SCOPE_CONFIRMATION_BEHAVIOR_INCLUDED": "YES",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "future_implementation_authorized_by_this_task": False,
            "phase_2b_remains_planning_only": True,
            "missing_conditions_listed": True,
            "scope_drift_risk_reviewed": True,
            "needs_scope_confirmation_behavior_included": True,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "first_slice_implemented": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_12_report(report)
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
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["decision"]))}</p>
  <p>{html.escape(str(report["non_authorization_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Authorization Review</h2>
  <table><tbody>{_dict_rows(report["authorization_review"])}</tbody></table>
  <h2>Missing Conditions Before Implementation</h2>
  <ul>{_list_items(report["missing_conditions_before_implementation"])}</ul>
  <h2>Scope Drift Risks</h2>
  <ul>{_list_items(report["scope_drift_risks"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_referenced"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_12_future_implementation_authorization_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_12_future_implementation_authorization_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_12_future_implementation_authorization_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_12_future_implementation_authorization_review_report()
    json_path, html_path = write_phase_2b_12_future_implementation_authorization_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"scope_confirmation: {report['summary']['scope_confirmation']}")
    print(f"phase_goal_confirmed: {str(report['summary']['phase_goal_confirmed']).lower()}")
    print(
        "example_job_types_treated_as_examples_only: "
        f"{str(report['summary']['example_job_types_treated_as_examples_only']).lower()}"
    )
    print(f"forbidden_scope_preserved: {str(report['summary']['forbidden_scope_preserved']).lower()}")
    print(f"existing_artifacts_referenced: {str(report['summary']['existing_artifacts_referenced']).lower()}")
    print(
        "implementation_boundary_preserved: "
        f"{str(report['summary']['implementation_boundary_preserved']).lower()}"
    )
    print(
        "future_implementation_authorized_by_this_task: "
        f"{str(report['summary']['future_implementation_authorized_by_this_task']).lower()}"
    )
    print(f"phase_2b_remains_planning_only: {str(report['summary']['phase_2b_remains_planning_only']).lower()}")
    print(f"missing_conditions_listed: {str(report['summary']['missing_conditions_listed']).lower()}")
    print(f"scope_drift_risk_reviewed: {str(report['summary']['scope_drift_risk_reviewed']).lower()}")
    print(
        "needs_scope_confirmation_behavior_included: "
        f"{str(report['summary']['needs_scope_confirmation_behavior_included']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"first_slice_implemented: {str(report['summary']['first_slice_implemented']).lower()}")
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
    print(f"Missing conditions checked: {report['validation']['missing_conditions_checked']}")
    print(f"Scope drift risks checked: {report['validation']['scope_drift_risks_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
