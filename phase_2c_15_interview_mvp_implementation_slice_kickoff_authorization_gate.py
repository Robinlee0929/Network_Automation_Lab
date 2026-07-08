"""Phase 2C-15 Interview MVP implementation slice kickoff authorization gate.

This module creates deterministic, local, planning-only authorization evidence
for whether candidate-03 / local_result_envelope_contract may begin
implementation in a later phase. It does not implement, scaffold, execute, or
prepare execution for that slice.
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_14_interview_mvp_implementation_slice_final_selection_gate import (
    FINAL_VERDICT as PHASE_2C_14_VERDICT,
    SELECTED_CANDIDATE_ID as PHASE_2C_14_SELECTED_CANDIDATE_ID,
    SELECTED_NEXT_SLICE as PHASE_2C_14_SELECTED_NEXT_SLICE,
    TASK_NAME as PHASE_2C_14_TASK_NAME,
    build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report,
    validate_phase_2c_14_report,
)


PHASE = "2C-15"
TASK_NAME = "phase2c-15-interview-mvp-implementation-slice-kickoff-authorization-gate"
TITLE = "Phase 2C-15 Interview MVP Implementation Slice Kickoff Authorization Gate - Planning Only"
MODE = "planning_only_interview_mvp_kickoff_authorization_gate"
SCOPE = "candidate_03_local_result_envelope_contract_future_implementation_authorization_only"
STATUS = "PASS"
AUTHORIZATION_RESULT = "AUTHORIZED"
DECISION_TARGET_ID = "candidate-03"
DECISION_TARGET_SLICE = "local_result_envelope_contract"
DECISION_TARGET_DISPLAY_NAME = "Local Result Envelope Contract"
FINAL_VERDICT = "PHASE_2C_15_INTERVIEW_MVP_KICKOFF_AUTHORIZATION_GATE_DONE_AUTHORIZED_FOR_LATER_PHASE"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_15_kickoff_authorization_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_15_kickoff_authorization_gate.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.md"

PHASE_GOAL = (
    "Produce a planning-only authorization gate that answers whether "
    "candidate-03 / local_result_envelope_contract is authorized to begin "
    "implementation in a later phase. Phase 2C-15 itself does not implement "
    "the slice and does not start the next phase."
)

AUTHORIZATION_QUESTION = (
    "Is candidate-03 / local_result_envelope_contract authorized to begin "
    "implementation in a later phase?"
)

EXAMPLE_JOB_TYPES = (
    "local_static_job",
    "artifact_validation_job",
    "local_result_envelope_contract",
    "future demo/read-only local validation jobs",
)

FORBIDDEN_SCOPE = (
    "local_result_envelope_contract implementation",
    "result envelope runtime implementation",
    "runner behavior",
    "adapter behavior",
    "execution path",
    "scheduler",
    "queue",
    "broker",
    "worker",
    "AI agent loop",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider integration",
    "API integration",
    "model integration",
    "secrets handling",
    "real command execution",
    "config backup behavior",
    "config change behavior",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "Phase 2C-16 start",
    "AGENTS.md modification",
    "unrelated file modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_11_interview_mvp_scope_architecture_gate.md",
    "docs/phase_2c/phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.md",
    "phase_2c_11_interview_mvp_scope_architecture_gate.py",
    "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.py",
    "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.py",
    "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

FUTURE_IMPLEMENTATION_BOUNDARY = (
    "Authorized for a later phase only: define a local, deterministic "
    "local_result_envelope_contract artifact for reviewer-visible result "
    "shape and validation evidence. The later phase must stay non-executing "
    "unless a separate explicit safety gate authorizes otherwise. Phase "
    "2C-15 does not implement the contract, add runtime behavior, add runner "
    "or adapter behavior, open execution paths, start Phase 2C-16, or touch "
    "live devices, SSH, NETCONF, RESTCONF, providers, APIs, models, secrets, "
    "config backup/change behavior, production execution, Day1-Day160 "
    "artifacts, or a second safety matrix."
)

DECISION_RATIONALE = (
    "AUTHORIZED because Phase 2C-14 selected candidate-03 / "
    "local_result_envelope_contract as the lowest-boundary Interview MVP "
    "implementation slice, with Phase 2C-13 safety review preserving no new "
    "safety delta for the selected candidate. The authorization is limited to "
    "starting implementation in a later phase and does not create any "
    "implementation, runtime, runner, adapter, execution, live-device, "
    "provider/API/model, secret, backup, config-change, production, "
    "Day1-Day160 rewrite, or second-safety-matrix behavior in Phase 2C-15."
)

SAFETY_FLAGS = {
    "phase_2c_15_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_2c_11_referenced": True,
    "phase_2c_12_referenced": True,
    "phase_2c_13_referenced": True,
    "phase_2c_14_read": True,
    "authorization_gate_only": True,
    "decision_target_candidate_03_only": True,
    "authorization_result_authorized": True,
    "future_phase_implementation_authorized": True,
    "phase_2c_15_implements_slice": False,
    "local_result_envelope_contract_implemented": False,
    "result_envelope_runtime_added": False,
    "implementation_started": False,
    "next_phase_started": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "ai_loop_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "extra_slice_selected_or_implemented": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_15_INTERVIEW_MVP_IMPLEMENTATION_SLICE_KICKOFF_AUTHORIZATION_GATE",
    "AUTHORIZATION_GATE_ONLY_YES",
    "DECISION_TARGET_CANDIDATE_03_LOCAL_RESULT_ENVELOPE_CONTRACT",
    "AUTHORIZATION_RESULT_AUTHORIZED",
    "FUTURE_PHASE_IMPLEMENTATION_AUTHORIZED_YES",
    "PHASE_2C_15_IMPLEMENTS_SLICE_NO",
    "LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED_NO",
    "RESULT_ENVELOPE_RUNTIME_ADDED_NO",
    "IMPLEMENTATION_STARTED_NO",
    "NEXT_PHASE_STARTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_15": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_14_source_review(project_root: Path) -> Dict[str, Any]:
    source_report = build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(project_root)
    source_validation = validate_phase_2c_14_report(source_report)
    return {
        "reviewed_task": PHASE_2C_14_TASK_NAME,
        "expected_verdict": PHASE_2C_14_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "selected_candidate_id": source_report.get("selected_candidate_id"),
        "selected_next_slice": source_report.get("selected_next_slice"),
        "source_implementation_authorized": source_report.get("implementation_authorized"),
        "source_implementation_started": source_report.get("implementation_started"),
        "source_phase_2c_15_started": source_report.get("phase_2c_15_started"),
        "selected_candidate_matches_decision_target": (
            source_report.get("selected_candidate_id") == DECISION_TARGET_ID
            and source_report.get("selected_next_slice") == DECISION_TARGET_SLICE
        ),
    }


def validate_phase_2c_15_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("authorization_decision") != "KICKOFF_AUTHORIZATION_GATE_ONLY":
        errors.append("AUTHORIZATION_DECISION_MISMATCH")
    if report.get("authorization_question") != AUTHORIZATION_QUESTION:
        errors.append("AUTHORIZATION_QUESTION_MISMATCH")
    if report.get("authorization_result") != AUTHORIZATION_RESULT:
        errors.append("AUTHORIZATION_RESULT_MISMATCH")
    if report.get("decision_target_id") != DECISION_TARGET_ID:
        errors.append("DECISION_TARGET_ID_MISMATCH")
    if report.get("decision_target_slice") != DECISION_TARGET_SLICE:
        errors.append("DECISION_TARGET_SLICE_MISMATCH")

    source_14 = report.get("phase_2c_14_source_review", {})
    if not isinstance(source_14, Mapping):
        errors.append("PHASE_2C_14_SOURCE_NOT_OBJECT")
        source_14 = {}
    if source_14.get("reviewed_task") != PHASE_2C_14_TASK_NAME:
        errors.append("PHASE_2C_14_TASK_MISMATCH")
    if source_14.get("observed_verdict") != PHASE_2C_14_VERDICT:
        errors.append("PHASE_2C_14_VERDICT_MISMATCH")
    if not isinstance(source_14.get("source_validation"), Mapping) or source_14["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_14_VALIDATION_NOT_PASS")
    if source_14.get("selected_candidate_id") != DECISION_TARGET_ID:
        errors.append("PHASE_2C_14_SELECTED_CANDIDATE_MISMATCH")
    if source_14.get("selected_next_slice") != DECISION_TARGET_SLICE:
        errors.append("PHASE_2C_14_SELECTED_SLICE_MISMATCH")
    if source_14.get("selected_candidate_matches_decision_target") is not True:
        errors.append("SOURCE_SELECTION_NOT_DECISION_TARGET")
    if source_14.get("source_implementation_authorized") is not False:
        errors.append("SOURCE_ALREADY_AUTHORIZED_IMPLEMENTATION")
    if source_14.get("source_implementation_started") is not False:
        errors.append("SOURCE_IMPLEMENTATION_STARTED")

    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if set(report.get("existing_artifacts_referenced", [])) != set(EXISTING_ARTIFACTS_REFERENCED):
        errors.append("EXISTING_ARTIFACTS_MISMATCH")
    if report.get("future_implementation_boundary") != FUTURE_IMPLEMENTATION_BOUNDARY:
        errors.append("FUTURE_IMPLEMENTATION_BOUNDARY_MISMATCH")
    if report.get("decision_rationale") != DECISION_RATIONALE:
        errors.append("DECISION_RATIONALE_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "AUTHORIZATION_GATE_ONLY": "YES",
        "DECISION_TARGET": f"{DECISION_TARGET_ID} / {DECISION_TARGET_SLICE}",
        "AUTHORIZATION_RESULT": AUTHORIZATION_RESULT,
        "FUTURE_PHASE_IMPLEMENTATION_AUTHORIZED": "YES",
        "PHASE_2C_15_IMPLEMENTS_SLICE": "NO",
        "LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED": "NO",
        "RESULT_ENVELOPE_RUNTIME_ADDED": "NO",
        "IMPLEMENTATION_STARTED": "NO",
        "NEXT_PHASE_STARTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "phase_2c_15_implements_slice",
        "local_result_envelope_contract_implemented",
        "result_envelope_runtime_added",
        "implementation_started",
        "next_phase_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
        "extra_slice_selected_or_implemented",
        "needs_scope_confirmation",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(report.get("existing_artifacts_referenced", [])),
    }


def build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
    project_root: Path,
) -> Dict[str, Any]:
    phase_2c_14_source_review = _phase_2c_14_source_review(project_root)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "authorization_decision": "KICKOFF_AUTHORIZATION_GATE_ONLY",
        "phase_goal": PHASE_GOAL,
        "authorization_question": AUTHORIZATION_QUESTION,
        "authorization_result": AUTHORIZATION_RESULT,
        "decision_target_id": DECISION_TARGET_ID,
        "decision_target_slice": DECISION_TARGET_SLICE,
        "decision_target_display_name": DECISION_TARGET_DISPLAY_NAME,
        "decision_rationale": DECISION_RATIONALE,
        "safety_baseline_compatibility": (
            "Compatible with the report-only / dry-run / mock-only baseline "
            "because this phase makes a future authorization decision only and "
            "does not implement or execute the selected slice."
        ),
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "future_implementation_boundary": FUTURE_IMPLEMENTATION_BOUNDARY,
        "phase_2c_14_source_review": phase_2c_14_source_review,
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "authorization_statement": (
            "Phase 2C-15 authorizes candidate-03 / "
            "local_result_envelope_contract to begin implementation in a later "
            "phase only. This is not implementation and does not start that "
            "later phase."
        ),
        "non_execution_statement": (
            "This task opens no local_result_envelope_contract implementation, "
            "runtime behavior, runner, adapter, scheduler, queue, broker, "
            "worker, AI loop, execution path, SSH, NETCONF, RESTCONF, "
            "live-device access, provider/API/model calls, secrets, backup "
            "behavior, config-change behavior, production execution, "
            "Day1-Day160 rewrite, second safety matrix, or next phase start."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AUTHORIZATION_GATE_ONLY": "YES",
            "DECISION_TARGET": f"{DECISION_TARGET_ID} / {DECISION_TARGET_SLICE}",
            "AUTHORIZATION_RESULT": AUTHORIZATION_RESULT,
            "FUTURE_PHASE_IMPLEMENTATION_AUTHORIZED": "YES",
            "PHASE_2C_15_IMPLEMENTS_SLICE": "NO",
            "LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED": "NO",
            "RESULT_ENVELOPE_RUNTIME_ADDED": "NO",
            "IMPLEMENTATION_STARTED": "NO",
            "NEXT_PHASE_STARTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "authorization_gate_only": True,
        "decision_target": f"{DECISION_TARGET_ID} / {DECISION_TARGET_SLICE}",
        "authorization_result": AUTHORIZATION_RESULT,
        "future_phase_implementation_authorized": True,
        "phase_2c_15_implements_slice": False,
        "local_result_envelope_contract_implemented": False,
        "result_envelope_runtime_added": False,
        "implementation_started": False,
        "next_phase_started": False,
        "runner_adapter_execution_path_added": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "extra_slice_selected_or_implemented": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_15_report(report)
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


def _windows_extended_path(path: Path) -> Path:
    if os.name != "nt":
        return path

    resolved = path.resolve()
    text = str(resolved)
    if text.startswith("\\\\?\\"):
        return resolved
    if text.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + text.lstrip("\\"))
    return Path("\\\\?\\" + text)


def _write_text(path: Path, text: str) -> None:
    io_path = _windows_extended_path(path)
    io_path.parent.mkdir(parents=True, exist_ok=True)
    io_path.write_text(text, encoding="utf-8")


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    _write_text(
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
  <p>Authorization result: <strong>{html.escape(str(report["authorization_result"]))}</strong></p>
  <p>Decision target: <strong>{html.escape(str(report["summary"]["decision_target"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["authorization_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Phase 2C-14 Source Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_14_source_review"])}</tbody></table>
  <h2>Future Implementation Boundary</h2>
  <p>{html.escape(str(report["future_implementation_boundary"]))}</p>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_referenced"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
    )


def write_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
        project_root
    )
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    _write_text(json_path, json.dumps(report_data, indent=2, sort_keys=True))
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(project_root)
    json_path, html_path = write_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Authorization decision: {report['authorization_decision']}")
    print(f"authorization_gate_only: {str(report['summary']['authorization_gate_only']).lower()}")
    print(f"decision_target: {report['summary']['decision_target']}")
    print(f"authorization_result: {report['summary']['authorization_result']}")
    print(
        "future_phase_implementation_authorized: "
        f"{str(report['summary']['future_phase_implementation_authorized']).lower()}"
    )
    print(f"phase_2c_15_implements_slice: {str(report['summary']['phase_2c_15_implements_slice']).lower()}")
    print(
        "local_result_envelope_contract_implemented: "
        f"{str(report['summary']['local_result_envelope_contract_implemented']).lower()}"
    )
    print(f"result_envelope_runtime_added: {str(report['summary']['result_envelope_runtime_added']).lower()}")
    print(f"implementation_started: {str(report['summary']['implementation_started']).lower()}")
    print(f"next_phase_started: {str(report['summary']['next_phase_started']).lower()}")
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
    print(
        "extra_slice_selected_or_implemented: "
        f"{str(report['summary']['extra_slice_selected_or_implemented']).lower()}"
    )
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
