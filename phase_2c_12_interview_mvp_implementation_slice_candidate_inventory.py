"""Phase 2C-12 Interview MVP implementation slice candidate inventory.

This module creates deterministic, local, planning-only candidate inventory
evidence for possible future Interview MVP implementation slices. It does not
select, authorize, scaffold, implement, or prepare execution for any candidate
and does not add runners, adapters, result envelopes, report renderers, demo
jobs, schedulers, queues, workers, agent loops, SSH, NETCONF, RESTCONF, live
devices, providers, APIs, models, secrets, backups, config changes, or
production execution paths.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_11_interview_mvp_scope_architecture_gate import (
    FINAL_VERDICT as PHASE_2C_11_VERDICT,
    REFERENCE_DOC,
    build_phase_2c_11_interview_mvp_scope_architecture_gate_report,
)


PHASE = "2C-12"
TASK_NAME = "phase2c-12-interview-mvp-implementation-slice-candidate-inventory"
TITLE = "Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory"
MODE = "planning_only_candidate_inventory"
SCOPE = "interview_mvp_implementation_slice_candidate_inventory_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_12_INTERVIEW_MVP_CANDIDATE_INVENTORY_DONE_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md"

PHASE_GOAL = (
    "Create a planning-only artifact that inventories possible future "
    "Interview MVP implementation slices. The inventory does not select one "
    "slice, authorize implementation, or start implementation."
)

PLANNING_ONLY_BOUNDARY = (
    "Phase 2C-12 is candidate inventory only. It may describe possible future "
    "artifact types and their safety risks, but every candidate remains "
    "unselected and unauthorized until a separate future user-approved phase."
)

FORBIDDEN_SCOPE = (
    "implementation logic",
    "runner code",
    "adapter code",
    "result envelope code",
    "report renderer code",
    "demo jobs",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "queue",
    "scheduler",
    "worker",
    "AI loop",
    "provider integration",
    "API integration",
    "model integration",
    "secrets handling",
    "config backup",
    "config change",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "Phase 2C-13 start",
    "AGENTS.md modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    REFERENCE_DOC.as_posix(),
    "docs/phase_2c/phase_2c_11_interview_mvp_scope_architecture_gate.md",
    "phase_2c_11_interview_mvp_scope_architecture_gate.py",
    "tests/test_phase_2c_11_interview_mvp_scope_architecture_gate.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add Phase 2C-12 planning-only candidate inventory evidence, "
    "minimal deterministic report-only generation, targeted tests, and "
    "existing-pattern registry/CLI/report-index visibility. Not allowed: "
    "selecting a slice, authorizing implementation, starting Phase 2C-13, or "
    "adding implementation logic, runner, adapter, result envelope, report "
    "renderer, demo job, execution, provider/API/model, secret, SSH, NETCONF, "
    "RESTCONF, live-device, queue, scheduler, worker, AI loop, backup, config "
    "change, production, Day1-Day160 replacement, AGENTS.md modification, or "
    "second safety-matrix behavior."
)

CANDIDATE_STATUS = "CANDIDATE_ONLY_NOT_SELECTED_NOT_AUTHORIZED"

CANDIDATE_INVENTORY = (
    {
        "candidate_id": "candidate-01",
        "candidate_name": "safe_runner_interface_contract",
        "candidate_purpose": "Define a future runner interface as documentation and static contract evidence only.",
        "why_it_may_belong_in_interview_mvp": "Could explain how tasks would be bounded before any executable runner exists.",
        "required_prerequisites": "Separate authorization gate, no-execution negative tests, and continued Stage 0 scope.",
        "safety_scope_notes": "Opens runner/execution design risk if broadened beyond documentation.",
        "explicitly_allowed_future_artifact_type": "planning document or static contract fixture",
        "explicitly_forbidden_future_artifact_type": "runner implementation or dispatcher execution path",
        "opens_runner_adapter_execution_risk": True,
        "touches_live_device_provider_secrets_risk": False,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
    {
        "candidate_id": "candidate-02",
        "candidate_name": "mock_adapter_contract",
        "candidate_purpose": "Describe a local deterministic mock adapter contract without device communication.",
        "why_it_may_belong_in_interview_mvp": "Could show adapter boundary judgment while keeping all device access forbidden.",
        "required_prerequisites": "Separate authorization gate, fixture-only inputs, and no live credential references.",
        "safety_scope_notes": "Adapter wording must not imply SSH, NETCONF, RESTCONF, provider, or live device access.",
        "explicitly_allowed_future_artifact_type": "mock-only adapter contract document or static fixture",
        "explicitly_forbidden_future_artifact_type": "real adapter, SSH adapter, provider client, or credential path",
        "opens_runner_adapter_execution_risk": True,
        "touches_live_device_provider_secrets_risk": True,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
    {
        "candidate_id": "candidate-03",
        "candidate_name": "local_result_envelope_contract",
        "candidate_purpose": "Inventory a possible local result envelope shape for mock-only evidence.",
        "why_it_may_belong_in_interview_mvp": "Could make pass, warn, fail, blocked, and safety flags reviewer-visible.",
        "required_prerequisites": "Separate contract authorization and proof that no renderer/runtime behavior is modified.",
        "safety_scope_notes": "Must not become runtime serialization or result processing infrastructure in this phase.",
        "explicitly_allowed_future_artifact_type": "static schema planning document or fixture example",
        "explicitly_forbidden_future_artifact_type": "runtime envelope code or shared result infrastructure",
        "opens_runner_adapter_execution_risk": False,
        "touches_live_device_provider_secrets_risk": False,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
    {
        "candidate_id": "candidate-04",
        "candidate_name": "report_visibility_contract",
        "candidate_purpose": "Plan how future Interview MVP evidence would appear in local reports.",
        "why_it_may_belong_in_interview_mvp": "Could improve reviewer navigation without creating execution or rendering infrastructure.",
        "required_prerequisites": "Separate report-only authorization and reuse of existing report-index conventions.",
        "safety_scope_notes": "Must not modify report renderer infrastructure or add action controls.",
        "explicitly_allowed_future_artifact_type": "planning document or static report-index visibility checklist",
        "explicitly_forbidden_future_artifact_type": "new report renderer, dashboard action, or POST workflow",
        "opens_runner_adapter_execution_risk": False,
        "touches_live_device_provider_secrets_risk": False,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
    {
        "candidate_id": "candidate-05",
        "candidate_name": "offline_demo_job_fixture_catalog",
        "candidate_purpose": "List possible future demo job fixtures as offline examples only.",
        "why_it_may_belong_in_interview_mvp": "Could help interview reviewers understand representative job stories without live execution.",
        "required_prerequisites": "Separate fixture-selection authorization and explicit no-demo-job implementation proof.",
        "safety_scope_notes": "Job examples must not become executable tasks, command allowlists, or live device checks.",
        "explicitly_allowed_future_artifact_type": "static fixture catalog or documentation-only example list",
        "explicitly_forbidden_future_artifact_type": "demo job implementation, command runner, or device validation task",
        "opens_runner_adapter_execution_risk": True,
        "touches_live_device_provider_secrets_risk": True,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
    {
        "candidate_id": "candidate-06",
        "candidate_name": "forbidden_intent_no_execution_proof",
        "candidate_purpose": "Plan evidence for rejected Interview MVP scenarios proving no execution path is reached.",
        "why_it_may_belong_in_interview_mvp": "Could make safety gates visible to reviewers through negative examples.",
        "required_prerequisites": "Separate authorization and reuse of existing safety evidence without creating a second matrix.",
        "safety_scope_notes": "Must reference existing safety boundaries and avoid new execution-capable test harnesses.",
        "explicitly_allowed_future_artifact_type": "planning document or static negative-evidence checklist",
        "explicitly_forbidden_future_artifact_type": "new safety matrix, runner harness, adapter invocation, or live rejection path",
        "opens_runner_adapter_execution_risk": True,
        "touches_live_device_provider_secrets_risk": True,
        "current_decision_status": CANDIDATE_STATUS,
        "selected": False,
        "authorized": False,
        "implementation_started": False,
    },
)

REVIEW_CHECKS = (
    {
        "check": "Phase 2C-11 remains the prior Interview MVP boundary input",
        "expected": PHASE_2C_11_VERDICT,
        "status": "PASS",
    },
    {
        "check": "Candidate inventory remains broader than one slice",
        "expected": "candidate_count > 1",
        "status": "PASS",
    },
    {
        "check": "No single implementation slice is selected",
        "expected": "NO_SINGLE_SLICE_SELECTED",
        "status": "PASS",
    },
    {
        "check": "No implementation is authorized",
        "expected": "NO_IMPLEMENTATION_AUTHORIZED",
        "status": "PASS",
    },
    {
        "check": "No implementation is started",
        "expected": "NO_IMPLEMENTATION_STARTED",
        "status": "PASS",
    },
)

SAFETY_FLAGS = {
    "phase_2c_12_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "required_reference_document_read": True,
    "candidate_inventory_only": True,
    "single_slice_selected": False,
    "implementation_authorized": False,
    "implementation_started": False,
    "phase_2c_13_started": False,
    "runner_code_added": False,
    "adapter_code_added": False,
    "result_envelope_code_added": False,
    "report_renderer_code_added": False,
    "demo_jobs_added": False,
    "execution_path_added": False,
    "queue_added": False,
    "scheduler_added": False,
    "worker_added": False,
    "ai_loop_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_added": False,
    "config_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_12_INTERVIEW_MVP_IMPLEMENTATION_SLICE_CANDIDATE_INVENTORY",
    "CANDIDATE_INVENTORY_ONLY_YES",
    "NO_SINGLE_SLICE_SELECTED",
    "NO_IMPLEMENTATION_AUTHORIZED",
    "NO_IMPLEMENTATION_STARTED",
    "PHASE_2C_13_STARTED_NO",
    "RUNNER_CODE_ADDED_NO",
    "ADAPTER_CODE_ADDED_NO",
    "RESULT_ENVELOPE_CODE_ADDED_NO",
    "REPORT_RENDERER_CODE_ADDED_NO",
    "DEMO_JOBS_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_12": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_11_input_review(project_root: Path) -> Dict[str, Any]:
    report = build_phase_2c_11_interview_mvp_scope_architecture_gate_report(project_root)
    return {
        "reviewed_task": "phase2c-11-interview-mvp-scope-architecture-gate",
        "expected_verdict": PHASE_2C_11_VERDICT,
        "observed_verdict": report.get("final_verdict"),
        "source_validation": report.get("validation", {}),
        "implementation_authorized": report.get("implementation_authorized"),
        "implementation_started": report.get("implementation_started"),
        "phase_2c_12_started_by_phase_2c_11": report.get("phase_2c_12_started"),
    }


def validate_phase_2c_12_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("planning_only_boundary") != PLANNING_ONLY_BOUNDARY:
        errors.append("PLANNING_ONLY_BOUNDARY_MISMATCH")

    source_review = report.get("phase_2c_11_input_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_11_INPUT_NOT_OBJECT")
        source_review = {}
    if source_review.get("observed_verdict") != PHASE_2C_11_VERDICT:
        errors.append("PHASE_2C_11_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_11_VALIDATION_NOT_PASS")

    candidates = report.get("candidate_inventory", [])
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        errors.append("CANDIDATE_INVENTORY_NOT_LIST")
        candidates = []
    if len(candidates) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_CANDIDATE")
    expected_ids = {candidate["candidate_id"] for candidate in CANDIDATE_INVENTORY}
    observed_ids = {candidate.get("candidate_id") for candidate in candidates if isinstance(candidate, Mapping)}
    if observed_ids != expected_ids:
        errors.append("CANDIDATE_ID_SET_MISMATCH")
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            errors.append("CANDIDATE_NOT_OBJECT")
            continue
        if candidate.get("current_decision_status") != CANDIDATE_STATUS:
            errors.append(f"CANDIDATE_STATUS_MISMATCH:{candidate.get('candidate_id')}")
        if candidate.get("selected") is not False:
            errors.append("CANDIDATE_SELECTED")
        if candidate.get("authorized") is not False:
            errors.append("CANDIDATE_AUTHORIZED")
        if candidate.get("implementation_started") is not False:
            errors.append("CANDIDATE_IMPLEMENTATION_STARTED")

    if tuple(report.get("review_checks", ())) != REVIEW_CHECKS:
        errors.append("REVIEW_CHECKS_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("review_checks", ())):
        errors.append("REVIEW_CHECK_NOT_PASS")
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
        "NO_SINGLE_SLICE_SELECTED": "YES",
        "NO_IMPLEMENTATION_AUTHORIZED": "YES",
        "NO_IMPLEMENTATION_STARTED": "YES",
        "PHASE_2C_13_STARTED": "NO",
        "RUNNER_CODE_ADDED": "NO",
        "ADAPTER_CODE_ADDED": "NO",
        "RESULT_ENVELOPE_CODE_ADDED": "NO",
        "REPORT_RENDERER_CODE_ADDED": "NO",
        "DEMO_JOBS_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "single_slice_selected",
        "implementation_authorized",
        "implementation_started",
        "phase_2c_13_started",
        "runner_code_added",
        "adapter_code_added",
        "result_envelope_code_added",
        "report_renderer_code_added",
        "demo_jobs_added",
        "execution_path_added",
        "queue_added",
        "scheduler_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_added",
        "config_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "candidate_count": len(candidates),
        "review_checks_checked": len(report.get("review_checks", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }


def build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
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
        "phase_goal": PHASE_GOAL,
        "planning_only_boundary": PLANNING_ONLY_BOUNDARY,
        "candidate_inventory": deepcopy(CANDIDATE_INVENTORY),
        "candidate_status_required": CANDIDATE_STATUS,
        "phase_2c_11_input_review": _phase_2c_11_input_review(project_root),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "review_checks": deepcopy(REVIEW_CHECKS),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "explicit_non_selection_statement": "NO_SINGLE_SLICE_SELECTED",
        "explicit_non_authorization_statement": "NO_IMPLEMENTATION_AUTHORIZED",
        "implementation_not_started_confirmation": "NO_IMPLEMENTATION_STARTED",
        "next_phase_boundary": "Phase 2C-13 is not started and would require separate user authorization.",
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "NO_SINGLE_SLICE_SELECTED": "YES",
            "NO_IMPLEMENTATION_AUTHORIZED": "YES",
            "NO_IMPLEMENTATION_STARTED": "YES",
            "PHASE_2C_13_STARTED": "NO",
            "RUNNER_CODE_ADDED": "NO",
            "ADAPTER_CODE_ADDED": "NO",
            "RESULT_ENVELOPE_CODE_ADDED": "NO",
            "REPORT_RENDERER_CODE_ADDED": "NO",
            "DEMO_JOBS_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "candidate_count": len(CANDIDATE_INVENTORY),
        "candidate_inventory_only": True,
        "single_slice_selected": False,
        "implementation_authorized": False,
        "implementation_started": False,
        "phase_2c_13_started": False,
        "runner_code_added": False,
        "adapter_code_added": False,
        "result_envelope_code_added": False,
        "report_renderer_code_added": False,
        "demo_jobs_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_12_report(report)
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


def _check_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('check')))}</td>"
        f"<td>{html.escape(str(item.get('expected')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
        "</tr>"
        for item in values
    )


def _candidate_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('candidate_id')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_name')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_purpose')))}</td>"
        f"<td>{html.escape(str(item.get('explicitly_allowed_future_artifact_type')))}</td>"
        f"<td>{html.escape(str(item.get('explicitly_forbidden_future_artifact_type')))}</td>"
        f"<td>{html.escape(str(item.get('current_decision_status')))}</td>"
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
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["planning_only_boundary"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Candidate Inventory</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Purpose</th><th>Allowed Future Artifact</th><th>Forbidden Future Artifact</th><th>Status</th></tr></thead><tbody>{_candidate_rows(report["candidate_inventory"])}</tbody></table>
  <h2>Review Checks</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_check_rows(report["review_checks"])}</tbody></table>
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


def write_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        project_root
    )
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(project_root)
    json_path, html_path = write_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"candidate_inventory_only: {str(report['summary']['candidate_inventory_only']).lower()}")
    print(f"single_slice_selected: {str(report['summary']['single_slice_selected']).lower()}")
    print(f"implementation_authorized: {str(report['summary']['implementation_authorized']).lower()}")
    print(f"implementation_started: {str(report['summary']['implementation_started']).lower()}")
    print(f"phase_2c_13_started: {str(report['summary']['phase_2c_13_started']).lower()}")
    print(f"runner_code_added: {str(report['summary']['runner_code_added']).lower()}")
    print(f"adapter_code_added: {str(report['summary']['adapter_code_added']).lower()}")
    print(f"result_envelope_code_added: {str(report['summary']['result_envelope_code_added']).lower()}")
    print(f"report_renderer_code_added: {str(report['summary']['report_renderer_code_added']).lower()}")
    print(f"demo_jobs_added: {str(report['summary']['demo_jobs_added']).lower()}")
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
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
