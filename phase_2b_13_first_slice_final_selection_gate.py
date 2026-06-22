"""Phase 2B-13 first-slice final selection gate.

This module creates deterministic, local, planning-only report artifacts for
selecting the future first-slice candidate. It does not implement the selected
slice, create runners, adapters, brokers, schedulers, queue workers, execution
paths, SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls,
secrets handling, Phase 2C work, or any configuration-changing behavior.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_07_first_slice_definition_pack import FIRST_MINIMAL_SAFE_SLICE
from phase_2b_12_future_implementation_authorization_review import (
    FINAL_VERDICT as PHASE_2B_12_VERDICT,
)


PHASE = "2B-13"
TASK_NAME = "phase2b-13-first-slice-final-selection-gate-planning-only"
TITLE = "Phase 2B-13 First-Slice Final Selection Gate - Planning Only"
MODE = "planning_only_first_slice_final_selection_gate"
SCOPE = "phase_wide_first_slice_final_selection_gate_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_13_FIRST_SLICE_SELECTED_PLANNING_ONLY"
BLOCKED_VERDICT = "NEEDS_2B_14_IMPLEMENTATION_AUTHORIZATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_13_first_slice_final_selection_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_13_first_slice_final_selection_gate.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_13_first_slice_final_selection_gate.md"

PHASE_GOAL = (
    "Select the future first-slice candidate for a later, separately authorized "
    "implementation gate while keeping Phase 2B-13 planning-only."
)

SELECTED_FUTURE_FIRST_SLICE = {
    "name": FIRST_MINIMAL_SAFE_SLICE["name"],
    "source": "Phase 2B-07 first minimal safe slice definition",
    "selection_status": "SELECTED_FOR_FUTURE_2B_14_AUTHORIZATION_REVIEW",
    "selection_reason": (
        "It is the smallest reviewer-visible candidate already defined by the "
        "Phase 2B planning chain: local static job-definition and reviewer-evidence "
        "contract structures only, with machine-readable no-execution flags."
    ),
    "implementation_status": "NOT_IMPLEMENTED",
    "implementation_gate": "Phase 2B-14 Implementation Authorization Gate",
}

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
    "docs/phase_2b/phase_2b_11_project_consolidation_and_implementation_entry_map.md",
    "docs/phase_2b/phase_2b_12_future_implementation_authorization_review.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "existing Phase 2B planning artifact tests",
)

FORBIDDEN_SCOPE = (
    "implementation",
    "first-slice implementation",
    "Phase 2C",
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
    "real validation",
    "real command execution",
    "real configuration change",
    "frontend API integration",
    "production workflow",
    "second safety matrix",
    "Day1-Day160 rewrite or replacement",
)

SELECTION_CRITERIA = (
    "candidate was already defined by an earlier Phase 2B planning artifact",
    "candidate remains local, static, and reviewer-visible",
    "candidate is not tied to one job type, one device, VRRP only, backup only, or baseline only",
    "candidate requires no runner, adapter, broker, scheduler, queue worker, or execution path",
    "candidate requires no SSH, NETCONF, RESTCONF, live device, provider/API/model, or secrets access",
    "candidate can be reviewed through documentation, deterministic report artifacts, and negative tests",
    "candidate preserves Day1-Day160 and Phase 2B safety boundaries without creating a second safety matrix",
)

IMPLEMENTATION_AUTHORIZATION_GATE_2B_14 = {
    "gate": "Phase 2B-14 Implementation Authorization Gate",
    "required_before_any_implementation": True,
    "reserved_by_phase_2b_13": True,
    "phase_2b_13_grants_implementation_permission": False,
    "minimum_future_decision_needed": (
        "A separate explicit owner authorization must approve whether the selected "
        "future first slice may be implemented at all."
    ),
}

SAFETY_FLAGS = {
    "agents_md_read_before_changes": True,
    "agents_md_modified": False,
    "future_first_slice_selected": True,
    "selected_future_first_slice_implemented": False,
    "phase_2b_13_planning_only": True,
    "implementation_authorized_by_phase_2b_13": False,
    "phase_2b_14_implementation_authorization_gate_reserved": True,
    "phase_2c_touched": False,
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
    "real_validation_added": False,
    "real_command_execution_added": False,
    "real_configuration_change_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_13_FIRST_SLICE_FINAL_SELECTION_GATE_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "FUTURE_FIRST_SLICE_SELECTED_TRUE",
    "SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED_FALSE",
    "IMPLEMENTATION_AUTHORIZED_BY_PHASE_2B_13_FALSE",
    "PHASE_2B_14_IMPLEMENTATION_AUTHORIZATION_GATE_RESERVED_TRUE",
    "PHASE_2C_TOUCHED_FALSE",
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
            "allowed_by_phase_2b_13": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_13_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    selected = report.get("selected_future_first_slice", {})
    if not isinstance(selected, Mapping):
        errors.append("SELECTED_FUTURE_FIRST_SLICE_NOT_OBJECT")
        selected = {}
    if selected.get("name") != FIRST_MINIMAL_SAFE_SLICE["name"]:
        errors.append("SELECTED_FUTURE_FIRST_SLICE_NAME_MISMATCH")
    if selected.get("implementation_status") != "NOT_IMPLEMENTED":
        errors.append("SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED")
    if selected.get("implementation_gate") != IMPLEMENTATION_AUTHORIZATION_GATE_2B_14["gate"]:
        errors.append("IMPLEMENTATION_GATE_2B_14_NOT_RESERVED")

    if set(report.get("example_job_types", [])) != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")
    if set(report.get("selection_criteria", [])) != set(SELECTION_CRITERIA):
        errors.append("SELECTION_CRITERIA_MISMATCH")
    if report.get("phase_2b_12_verdict_referenced") != PHASE_2B_12_VERDICT:
        errors.append("PHASE_2B_12_VERDICT_NOT_REFERENCED")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    gate = report.get("implementation_authorization_gate_2b_14", {})
    if gate != IMPLEMENTATION_AUTHORIZATION_GATE_2B_14:
        errors.append("IMPLEMENTATION_AUTHORIZATION_GATE_2B_14_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "AGENTS_MD_READ_BEFORE_CHANGES": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "FUTURE_FIRST_SLICE_SELECTED": "YES",
        "SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED": "NO",
        "IMPLEMENTATION_AUTHORIZED_BY_PHASE_2B_13": "NO",
        "PHASE_2B_14_IMPLEMENTATION_AUTHORIZATION_GATE_RESERVED": "YES",
        "PHASE_2C_TOUCHED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "selected_future_first_slice_implemented",
            "implementation_authorized_by_phase_2b_13",
            "phase_2c_touched",
            "runner_added",
            "adapter_added",
            "execution_path_added",
            "ssh_touched",
            "api_calls_added",
            "secrets_handling_added",
        )
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "selection_criteria_checked": len(report.get("selection_criteria", [])),
        "existing_artifacts_checked": len(artifacts),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }


def build_phase_2b_13_first_slice_final_selection_gate_report() -> Dict[str, Any]:
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
        "phase_2b_12_verdict_referenced": PHASE_2B_12_VERDICT,
        "selected_future_first_slice": deepcopy(SELECTED_FUTURE_FIRST_SLICE),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "selection_criteria": list(SELECTION_CRITERIA),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_authorization_gate_2b_14": dict(IMPLEMENTATION_AUTHORIZATION_GATE_2B_14),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "planning_only_boundary": (
            "Phase 2B-13 selects a future first-slice candidate only. It does not "
            "grant implementation permission, does not implement the slice, and "
            "preserves Phase 2B-14 as the required implementation authorization gate."
        ),
        "non_implementation_statement": (
            "This artifact does not touch runner, adapter, broker, scheduler, queue "
            "worker, execution path, SSH, NETCONF, RESTCONF, live-device access, "
            "provider/API/model calls, secrets handling, Phase 2C, or real operations."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AGENTS_MD_READ_BEFORE_CHANGES": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "FUTURE_FIRST_SLICE_SELECTED": "YES",
            "SELECTED_FUTURE_FIRST_SLICE_IMPLEMENTED": "NO",
            "IMPLEMENTATION_AUTHORIZED_BY_PHASE_2B_13": "NO",
            "PHASE_2B_14_IMPLEMENTATION_AUTHORIZATION_GATE_RESERVED": "YES",
            "PHASE_2C_TOUCHED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "agents_md_read_before_changes": True,
            "agents_md_modified": False,
            "future_first_slice_selected": True,
            "selected_future_first_slice_name": SELECTED_FUTURE_FIRST_SLICE["name"],
            "selected_future_first_slice_implemented": False,
            "phase_2b_13_planning_only": True,
            "implementation_authorized_by_phase_2b_13": False,
            "phase_2b_14_implementation_authorization_gate_reserved": True,
            "phase_2c_touched": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_13_report(report)
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
  <p>{html.escape(str(report["planning_only_boundary"]))}</p>
  <p>{html.escape(str(report["non_implementation_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Selected Future First Slice</h2>
  <table><tbody>{_dict_rows(report["selected_future_first_slice"])}</tbody></table>
  <h2>Phase 2B-14 Gate</h2>
  <table><tbody>{_dict_rows(report["implementation_authorization_gate_2b_14"])}</tbody></table>
  <h2>Selection Criteria</h2>
  <ul>{_list_items(report["selection_criteria"])}</ul>
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


def write_phase_2b_13_first_slice_final_selection_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_13_first_slice_final_selection_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_13_first_slice_final_selection_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_13_first_slice_final_selection_gate_report()
    json_path, html_path = write_phase_2b_13_first_slice_final_selection_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"agents_md_read_before_changes: {str(report['summary']['agents_md_read_before_changes']).lower()}")
    print(f"agents_md_modified: {str(report['summary']['agents_md_modified']).lower()}")
    print(f"future_first_slice_selected: {str(report['summary']['future_first_slice_selected']).lower()}")
    print(f"selected_future_first_slice_name: {report['summary']['selected_future_first_slice_name']}")
    print(
        "selected_future_first_slice_implemented: "
        f"{str(report['summary']['selected_future_first_slice_implemented']).lower()}"
    )
    print(f"phase_2b_13_planning_only: {str(report['summary']['phase_2b_13_planning_only']).lower()}")
    print(
        "implementation_authorized_by_phase_2b_13: "
        f"{str(report['summary']['implementation_authorized_by_phase_2b_13']).lower()}"
    )
    print(
        "phase_2b_14_implementation_authorization_gate_reserved: "
        f"{str(report['summary']['phase_2b_14_implementation_authorization_gate_reserved']).lower()}"
    )
    print(f"phase_2c_touched: {str(report['summary']['phase_2c_touched']).lower()}")
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
    print(f"Selection criteria checked: {report['validation']['selection_criteria_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
