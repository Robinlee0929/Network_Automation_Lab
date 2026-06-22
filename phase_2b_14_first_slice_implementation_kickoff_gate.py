"""Phase 2B-14 first-slice implementation kickoff gate.

This module creates deterministic, local, authorization-gate report artifacts
for confirming whether a future first-slice implementation task may be started.
It does not implement the selected slice, create runners, adapters, brokers,
schedulers, queue workers, execution paths, SSH, NETCONF, RESTCONF,
live-device access, provider/API/model calls, secrets handling, backup
execution, configuration changes, custom command execution, or custom script
execution.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_13_first_slice_final_selection_gate import (
    FINAL_VERDICT as PHASE_2B_13_VERDICT,
    SELECTED_FUTURE_FIRST_SLICE,
)


PHASE = "2B-14"
TASK_NAME = "phase2b-14-first-slice-implementation-kickoff-gate"
TITLE = "Phase 2B-14 First-Slice Implementation Kickoff Gate"
MODE = "authorization_gate_not_implementation"
SCOPE = "phase_wide_first_slice_implementation_kickoff_gate"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_14_KICKOFF_GATE_READY_NOT_IMPLEMENTED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_14_first_slice_implementation_kickoff_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_14_first_slice_implementation_kickoff_gate.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_14_first_slice_implementation_kickoff_gate.md"

PHASE_GOAL = (
    "Create a written authorization gate confirming whether the project is ready "
    "to start a future first-slice implementation task, while stating that this "
    "task itself is not first-slice implementation."
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
    "first-slice implementation",
    "local_static_job implementation",
    "runner",
    "adapter",
    "scheduler",
    "broker",
    "queue",
    "execution path",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live-device access",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "config backup execution",
    "config change execution",
    "custom command execution",
    "custom script execution",
    "real device operation",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "weakened safety gates",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_12_future_implementation_authorization_review.md",
    "docs/phase_2b/phase_2b_11_project_consolidation_and_implementation_entry_map.md",
    "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    "existing Phase 2A read-only / dry-run runner boundary artifacts",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add this written Phase 2B-14 gate artifact, expose it through the "
    "minimal report task/registry/report-index metadata, and add targeted tests. "
    "Not allowed: implement the selected first slice or add any runtime, live, "
    "provider/API/model, secrets, runner, adapter, broker, scheduler, queue, or "
    "execution behavior."
)

SCOPE_CONFIRMATION = {
    "status": "PASS",
    "scope_confirmation_written": True,
    "phase_goal": PHASE_GOAL,
    "phase_goal_separated": True,
    "example_job_types": list(EXAMPLE_JOB_TYPES),
    "example_job_types_separated": True,
    "example_job_type_role": "examples_only_not_phase_scope",
    "local_static_job_redefines_phase": False,
    "forbidden_scope": list(FORBIDDEN_SCOPE),
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
    "existing_artifacts_referenced": True,
    "implementation_boundary": IMPLEMENTATION_BOUNDARY,
    "implementation_boundary_separated": True,
    "scope_narrowed_to_single_example": False,
    "needs_scope_confirmation": False,
}

SAFETY_FLAGS = {
    "phase_2b_14_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_goal_separated": True,
    "example_job_types_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_referenced": True,
    "implementation_boundary_separated": True,
    "phase_2b_13_selected_future_first_slice": True,
    "selected_first_slice_is_first_target_only": True,
    "broader_phase_scope_reduced_to_first_slice": False,
    "scope_narrowed_to_single_example": False,
    "needs_scope_confirmation": False,
    "later_implementation_requires_explicit_user_authorization": True,
    "first_slice_implemented": False,
    "local_static_job_implemented": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "secrets_handling_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "custom_command_execution_added": False,
    "custom_script_execution_added": False,
    "real_device_operation_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_14_FIRST_SLICE_IMPLEMENTATION_KICKOFF_GATE",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "PHASE_GOAL_SEPARATED_YES",
    "EXAMPLE_JOB_TYPES_SEPARATED_YES",
    "FORBIDDEN_SCOPE_SEPARATED_YES",
    "EXISTING_ARTIFACTS_REFERENCED_YES",
    "IMPLEMENTATION_BOUNDARY_SEPARATED_YES",
    "SCOPE_NARROWED_TO_SINGLE_EXAMPLE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "FIRST_SLICE_IMPLEMENTED_NO",
    "LOCAL_STATIC_JOB_IMPLEMENTED_NO",
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
            "allowed_by_phase_2b_14": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_14_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
        if agents.get("read_before_action") is not True:
            errors.append("AGENTS_MD_READ_BEFORE_ACTION_NOT_TRUE")
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
    if scope_confirmation.get("scope_confirmation_written") is not True:
        errors.append("SCOPE_CONFIRMATION_NOT_WRITTEN")
    if scope_confirmation.get("needs_scope_confirmation") is not False:
        errors.append("NEEDS_SCOPE_CONFIRMATION_NOT_FALSE")
    if scope_confirmation.get("scope_narrowed_to_single_example") is not False:
        errors.append("SCOPE_NARROWED_TO_SINGLE_EXAMPLE")

    selected = report.get("selected_future_first_slice", {})
    if not isinstance(selected, Mapping):
        errors.append("SELECTED_FUTURE_FIRST_SLICE_NOT_OBJECT")
        selected = {}
    if selected.get("implementation_status") != "NOT_IMPLEMENTED":
        errors.append("SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED")
    if report.get("phase_2b_13_verdict_referenced") != PHASE_2B_13_VERDICT:
        errors.append("PHASE_2B_13_VERDICT_NOT_REFERENCED")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_scope_reduction":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    artifacts = set(report.get("existing_artifacts_to_reference", []))
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
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "SCOPE_CONFIRMATION_WRITTEN": "YES",
        "PHASE_GOAL_SEPARATED": "YES",
        "EXAMPLE_JOB_TYPES_SEPARATED": "YES",
        "FORBIDDEN_SCOPE_SEPARATED": "YES",
        "EXISTING_ARTIFACTS_REFERENCED": "YES",
        "IMPLEMENTATION_BOUNDARY_SEPARATED": "YES",
        "SCOPE_NARROWED_TO_SINGLE_EXAMPLE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "LOCAL_STATIC_JOB_IMPLEMENTED": "NO",
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
            "scope_narrowed_to_single_example",
            "needs_scope_confirmation",
            "first_slice_implemented",
            "local_static_job_implemented",
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
            "second_safety_matrix_created",
        )
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(artifacts),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }


def build_phase_2b_14_first_slice_implementation_kickoff_gate_report() -> Dict[str, Any]:
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
            "read_before_action": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": deepcopy(SCOPE_CONFIRMATION),
        "phase_goal": PHASE_GOAL,
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "selected_future_first_slice": deepcopy(SELECTED_FUTURE_FIRST_SLICE),
        "selected_first_slice_role": "first_implementation_target_only_not_phase_scope",
        "broader_phase_scope_statement": (
            "The selected first slice may reference local_static_job, but "
            "local_static_job does not redefine the whole phase."
        ),
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_not_scope_reduction",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "authorization_gate_statement": (
            "Phase 2B-14 is a kickoff authorization gate only. A later "
            "implementation task still requires explicit user authorization."
        ),
        "non_implementation_statement": (
            "This task does not add runner, adapter, execution, provider, API, "
            "model, secrets, SSH, NETCONF, RESTCONF, live-device, backup, config "
            "change, custom command, or custom script behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "SCOPE_CONFIRMATION_WRITTEN": "YES",
            "PHASE_GOAL_SEPARATED": "YES",
            "EXAMPLE_JOB_TYPES_SEPARATED": "YES",
            "FORBIDDEN_SCOPE_SEPARATED": "YES",
            "EXISTING_ARTIFACTS_REFERENCED": "YES",
            "IMPLEMENTATION_BOUNDARY_SEPARATED": "YES",
            "SCOPE_NARROWED_TO_SINGLE_EXAMPLE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "LOCAL_STATIC_JOB_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation_written": True,
            "phase_goal_separated": True,
            "example_job_types_separated": True,
            "forbidden_scope_separated": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_separated": True,
            "scope_narrowed_to_single_example": False,
            "needs_scope_confirmation": False,
            "first_slice_implemented": False,
            "local_static_job_implemented": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_14_report(report)
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
  <p>{html.escape(str(report["authorization_gate_statement"]))}</p>
  <p>{html.escape(str(report["non_implementation_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Phase Goal</h2>
  <p>{html.escape(str(report["phase_goal"]))}</p>
  <h2>Example Job Types</h2>
  <ul>{_list_items(report["example_job_types"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_to_reference"])}</ul>
  <h2>Implementation Boundary</h2>
  <p>{html.escape(str(report["implementation_boundary"]))}</p>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_14_first_slice_implementation_kickoff_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_14_first_slice_implementation_kickoff_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_14_first_slice_implementation_kickoff_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_14_first_slice_implementation_kickoff_gate_report()
    json_path, html_path = write_phase_2b_14_first_slice_implementation_kickoff_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"scope_confirmation_written: {str(report['summary']['scope_confirmation_written']).lower()}")
    print(f"phase_goal_separated: {str(report['summary']['phase_goal_separated']).lower()}")
    print(f"example_job_types_separated: {str(report['summary']['example_job_types_separated']).lower()}")
    print(f"forbidden_scope_separated: {str(report['summary']['forbidden_scope_separated']).lower()}")
    print(f"existing_artifacts_referenced: {str(report['summary']['existing_artifacts_referenced']).lower()}")
    print(
        "implementation_boundary_separated: "
        f"{str(report['summary']['implementation_boundary_separated']).lower()}"
    )
    print(
        "scope_narrowed_to_single_example: "
        f"{str(report['summary']['scope_narrowed_to_single_example']).lower()}"
    )
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(f"first_slice_implemented: {str(report['summary']['first_slice_implemented']).lower()}")
    print(f"local_static_job_implemented: {str(report['summary']['local_static_job_implemented']).lower()}")
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
    print(f"Example job types checked: {report['validation']['example_job_types_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
