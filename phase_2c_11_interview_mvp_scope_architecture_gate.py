"""Phase 2C-11 Interview MVP scope + architecture authorization gate.

This module creates deterministic, local, planning-only authorization evidence
for the Interview MVP scope and architecture boundary. It does not implement a
runner, adapter, result envelope, report renderer, demo job, scheduler, queue,
worker, agent loop, SSH, NETCONF, RESTCONF, live-device access, provider/API
or model integration, secrets handling, config backup, config change, or
production execution path.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES


PHASE = "2C-11"
TASK_NAME = "phase2c-11-interview-mvp-scope-architecture-gate"
TITLE = "Phase 2C-11 Interview MVP Scope + Architecture Authorization Gate - Planning Only"
MODE = "planning_only_authorization_gate"
SCOPE = "phase_2c_11_interview_mvp_scope_architecture_boundary"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_11_INTERVIEW_MVP_SCOPE_ARCHITECTURE_GATE_IMPLEMENTATION_LOCKED"
NEEDS_SCOPE_CONFIRMATION_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REFERENCE_MISSING_VERDICT = "BLOCKED_REFERENCE_DOCUMENT_MISSING"

REFERENCE_DOC = Path("docs") / "automation_readiness" / "actual_automation_integration_plan.md"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_11_interview_mvp_scope_architecture_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_11_interview_mvp_scope_architecture_gate.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_11_interview_mvp_scope_architecture_gate.md"

PHASE_GOAL = (
    "Create a planning-only authorization artifact that defines the accelerated "
    "Interview MVP scope and architecture boundary for the Network Automation "
    "Lab. This phase decides what is safe to plan next, but it does not start "
    "implementation."
)

INTERVIEW_MVP_DEFINITION = (
    "The Interview MVP is a reviewer-visible, offline-safe demonstration of "
    "network automation judgment: it may show scoped planning, static evidence, "
    "mock-only boundaries, dry-run expectations, and report visibility, while "
    "proving that no live automation, runtime worker, or production execution "
    "path has been introduced."
)

SAFE_DRY_RUN_PLATFORM_SCOPE = (
    "Allowed planning scope is Stage 0 mock-only / dry-run / report-only: "
    "local static artifacts, deterministic fixtures, reviewer-facing report "
    "evidence, no-execution proof, and negative-test expectations for rejected "
    "or forbidden scenarios."
)

SAFE_RUNNER_ARCHITECTURE_BOUNDARY = (
    "A future safe runner may be planned only as an interface boundary and "
    "reviewer contract. Phase 2C-11 does not create runner code, dispatch "
    "behavior, subprocess execution, command transport, brokers, queues, "
    "schedulers, workers, or agent loops."
)

MOCK_ADAPTER_BOUNDARY = (
    "A future mock adapter may be planned only as a local deterministic adapter "
    "contract. It must not communicate with devices, shells, SSH, NETCONF, "
    "RESTCONF, provider APIs, model APIs, secrets stores, or production systems."
)

RESULT_ENVELOPE_BOUNDARY = (
    "A future result envelope may be planned only as a reportable data contract "
    "for local mock results, status, evidence paths, safety flags, and rejection "
    "reasons. Phase 2C-11 does not implement result envelope classes, schemas, "
    "renderers, or runtime serialization."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job",
    "artifact_validation_job",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "blocked_ssh_command",
)

DEMO_JOB_CANDIDATE_BOUNDARY = (
    "Demo job candidates are planning examples only. Phase 2C-11 lists them as "
    "candidate categories for later authorization planning, without selecting, "
    "implementing, executing, scheduling, queuing, or broadening any candidate "
    "into platform behavior."
)

NEXT_IMPLEMENTATION_CANDIDATES = (
    "separate Phase 2C-12 planning or kickoff gate for safe runner interface design",
    "separate Phase 2C-12 planning or kickoff gate for mock adapter contract design",
    "separate Phase 2C-12 planning or kickoff gate for result envelope contract design",
    "separate Phase 2C-12 planning or kickoff gate for demo job fixture selection",
)

AUTHORIZATION_STATUS = {
    "later_implementation_planning_authorized": True,
    "implementation_authorized": False,
    "implementation_started": False,
    "phase_2c_12_started": False,
    "next_allowed_activity": "separate future planning or kickoff gate only",
}

FORBIDDEN_SCOPE = (
    "runner implementation",
    "adapter implementation",
    "result envelope implementation",
    "report renderer implementation",
    "demo job implementation",
    "SSH execution",
    "NETCONF execution",
    "RESTCONF execution",
    "live device access",
    "provider integration",
    "API integration",
    "model integration",
    "secrets handling",
    "queue",
    "scheduler",
    "worker",
    "AI agent loop",
    "config backup execution",
    "config change execution",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
    "Phase 2C-10 artifact modification",
    "Phase 2C-12 start",
)

EXISTING_ARTIFACTS_REVIEWED = (
    "AGENTS.md",
    REFERENCE_DOC.as_posix(),
    "docs/phase_2c/phase_2c_10_next_slice_decision_gate_authorization_review.md",
    "phase_2c_10_next_slice_decision_gate_authorization_review.py",
    "tests/test_phase_2c_10_next_slice_decision_gate_authorization_review.py",
    "reports/lab-summary/phase_2c_10_next_slice_decision_gate_authorization_review.json",
    "reports/lab-summary/phase_2c_10_next_slice_decision_gate_authorization_review.html",
    "docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_08_next_slice_implementation.md",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: create Phase 2C-11 planning-only authorization evidence, register "
    "the report-only task through existing local catalog and CLI visibility "
    "patterns, and add tests for the planning artifact and report visibility. "
    "Not allowed: runtime behavior changes, runner/adapter/result-envelope/"
    "renderer/demo-job implementation, live automation integration, production "
    "automation integration, Phase 2C-10 modification, Phase 2C-12 start, or "
    "any forbidden capability."
)

DECISION_CRITERIA = (
    {
        "check": "Required automation readiness reference is found and read",
        "expected": "REFERENCE_DOCUMENT_FOUND_AND_READ: YES",
        "status": "PASS",
    },
    {
        "check": "Interview MVP remains Stage 0 safe",
        "expected": "MOCK_ONLY_DRY_RUN_REPORT_ONLY: YES",
        "status": "PASS",
    },
    {
        "check": "Architecture boundaries are authorized for planning only",
        "expected": "RUNNER_ADAPTER_RESULT_ENVELOPE_PLANNING_ONLY: YES",
        "status": "PASS",
    },
    {
        "check": "Demo job candidates remain examples only",
        "expected": "DEMO_JOB_CANDIDATES_SELECTED_OR_IMPLEMENTED: NO",
        "status": "PASS",
    },
    {
        "check": "Later implementation planning may be prepared by a separate gate",
        "expected": "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED: YES",
        "status": "PASS",
    },
    {
        "check": "Implementation remains locked in Phase 2C-11",
        "expected": "IMPLEMENTATION_AUTHORIZED: NO and IMPLEMENTATION_STARTED: NO",
        "status": "PASS",
    },
)

SAFETY_FLAGS = {
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "required_reference_document_found": True,
    "required_reference_document_read_before_scope_confirmation": True,
    "scope_confirmation_written": True,
    "needs_scope_confirmation": False,
    "interview_mvp_defined": True,
    "safe_dry_run_platform_scope_defined": True,
    "runner_architecture_boundary_defined": True,
    "mock_adapter_boundary_defined": True,
    "result_envelope_boundary_defined": True,
    "demo_job_candidates_listed_as_examples_only": True,
    "later_implementation_planning_authorized": True,
    "implementation_authorized": False,
    "implementation_started": False,
    "phase_2c_12_started": False,
    "runner_added": False,
    "adapter_added": False,
    "result_envelope_added": False,
    "report_renderer_added": False,
    "demo_jobs_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "agent_loop_added": False,
    "real_command_execution_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "phase_2c_10_modified": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_11_INTERVIEW_MVP_SCOPE_ARCHITECTURE_GATE_PLANNING_ONLY",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "REQUIRED_REFERENCE_DOCUMENT_FOUND_YES",
    "REQUIRED_REFERENCE_DOCUMENT_READ_BEFORE_SCOPE_CONFIRMATION_YES",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "INTERVIEW_MVP_DEFINITION_PRESENT_YES",
    "SAFE_DRY_RUN_PLATFORM_SCOPE_DEFINED_YES",
    "RUNNER_ARCHITECTURE_BOUNDARY_DEFINED_YES",
    "MOCK_ADAPTER_BOUNDARY_DEFINED_YES",
    "RESULT_ENVELOPE_BOUNDARY_DEFINED_YES",
    "DEMO_JOB_CANDIDATES_EXAMPLES_ONLY_YES",
    "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED_YES",
    "IMPLEMENTATION_AUTHORIZED_NO",
    "IMPLEMENTATION_STARTED_NO",
    "PHASE_2C_12_STARTED_NO",
    "RUNNER_ADAPTER_RESULT_ENVELOPE_REPORT_RENDERER_DEMO_JOBS_ADDED_NO",
    "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO",
    "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED_NO",
    "PRODUCTION_EXECUTION_PATH_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "PHASE_2C_10_MODIFIED_NO",
    FINAL_VERDICT,
)


def _artifact_record(project_root: Path, path_text: str) -> Dict[str, Any]:
    path = Path(path_text)
    return {
        "path": path.as_posix(),
        "exists": (project_root / path).exists(),
        "local_repository_artifact": True,
        "external_access_required": False,
    }


def _reference_document_review(project_root: Path) -> Dict[str, Any]:
    path = project_root / REFERENCE_DOC
    exists = path.exists()
    text = path.read_text(encoding="utf-8") if exists else ""
    required_markers = (
        "Default decision: NO-GO for real automation",
        "Stage 0: Mock-only / Dry-run Platform",
        "It does not authorize live device access",
    )
    return {
        "path": REFERENCE_DOC.as_posix(),
        "exists": exists,
        "read_before_scope_confirmation": exists,
        "required_markers_present": all(marker in text for marker in required_markers),
        "external_access_required": False,
    }


def _demo_job_candidate_records() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "job_type": job_type,
            "candidate_only": True,
            "selected": False,
            "implemented": False,
            "execution_capable": False,
            "requires_live_device": False,
        }
        for job_type in EXAMPLE_JOB_TYPES
    )


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_11": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_11_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
    if report.get("interview_mvp_definition") != INTERVIEW_MVP_DEFINITION:
        errors.append("INTERVIEW_MVP_DEFINITION_MISMATCH")
    if report.get("safe_dry_run_platform_scope") != SAFE_DRY_RUN_PLATFORM_SCOPE:
        errors.append("SAFE_DRY_RUN_PLATFORM_SCOPE_MISMATCH")
    if report.get("safe_runner_architecture_boundary") != SAFE_RUNNER_ARCHITECTURE_BOUNDARY:
        errors.append("SAFE_RUNNER_ARCHITECTURE_BOUNDARY_MISMATCH")
    if report.get("mock_adapter_boundary") != MOCK_ADAPTER_BOUNDARY:
        errors.append("MOCK_ADAPTER_BOUNDARY_MISMATCH")
    if report.get("result_envelope_boundary") != RESULT_ENVELOPE_BOUNDARY:
        errors.append("RESULT_ENVELOPE_BOUNDARY_MISMATCH")
    if tuple(report.get("example_job_types", ())) != EXAMPLE_JOB_TYPES:
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if report.get("demo_job_candidate_boundary") != DEMO_JOB_CANDIDATE_BOUNDARY:
        errors.append("DEMO_JOB_CANDIDATE_BOUNDARY_MISMATCH")
    if tuple(report.get("next_implementation_candidates", ())) != NEXT_IMPLEMENTATION_CANDIDATES:
        errors.append("NEXT_IMPLEMENTATION_CANDIDATES_MISMATCH")
    if report.get("authorization_status") != AUTHORIZATION_STATUS:
        errors.append("AUTHORIZATION_STATUS_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    reference_review = report.get("required_reference_document_review", {})
    if not isinstance(reference_review, Mapping):
        errors.append("REFERENCE_REVIEW_NOT_OBJECT")
        reference_review = {}
    if reference_review.get("exists") is not True:
        errors.append(REFERENCE_MISSING_VERDICT)
    if reference_review.get("read_before_scope_confirmation") is not True:
        errors.append("REFERENCE_DOCUMENT_NOT_READ_BEFORE_SCOPE_CONFIRMATION")
    if reference_review.get("required_markers_present") is not True:
        errors.append("REFERENCE_DOCUMENT_REQUIRED_MARKERS_MISSING")

    artifacts = set(report.get("existing_artifacts_reviewed", []))
    for artifact in EXISTING_ARTIFACTS_REVIEWED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    if tuple(report.get("decision_criteria", ())) != DECISION_CRITERIA:
        errors.append("DECISION_CRITERIA_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("decision_criteria", ())):
        errors.append("DECISION_CRITERIA_NOT_PASS")

    for candidate in report.get("demo_job_candidates", ()):
        if candidate.get("selected") or candidate.get("implemented") or candidate.get("execution_capable"):
            errors.append("DEMO_JOB_CANDIDATE_IMPLEMENTED_OR_SELECTED")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "REQUIRED_REFERENCE_DOCUMENT_FOUND": "YES",
        "REQUIRED_REFERENCE_DOCUMENT_READ": "YES",
        "INTERVIEW_MVP_DEFINITION_PRESENT": "YES",
        "SAFE_DRY_RUN_PLATFORM_SCOPE_DEFINED": "YES",
        "RUNNER_ARCHITECTURE_BOUNDARY_DEFINED": "YES",
        "MOCK_ADAPTER_BOUNDARY_DEFINED": "YES",
        "RESULT_ENVELOPE_BOUNDARY_DEFINED": "YES",
        "DEMO_JOB_CANDIDATES_EXAMPLES_ONLY": "YES",
        "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED": "YES",
        "IMPLEMENTATION_AUTHORIZED": "NO",
        "IMPLEMENTATION_STARTED": "NO",
        "PHASE_2C_12_STARTED": "NO",
        "RUNNER_ADAPTER_RESULT_ENVELOPE_REPORT_RENDERER_DEMO_JOBS_ADDED": "NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
        "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
        "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "PHASE_2C_10_MODIFIED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "needs_scope_confirmation",
        "agents_md_modified",
        "implementation_authorized",
        "implementation_started",
        "phase_2c_12_started",
        "runner_added",
        "adapter_added",
        "result_envelope_added",
        "report_renderer_added",
        "demo_jobs_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "phase_2c_10_modified",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(NEEDS_SCOPE_CONFIRMATION_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "decision_criteria_checked": len(report.get("decision_criteria", [])),
        "existing_artifacts_reviewed": len(artifacts),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "demo_job_candidates_checked": len(report.get("demo_job_candidates", [])),
    }


def build_phase_2c_11_interview_mvp_scope_architecture_gate_report(project_root: Path) -> Dict[str, Any]:
    reference_review = _reference_document_review(project_root)
    reference_ready = (
        reference_review["exists"] is True
        and reference_review["read_before_scope_confirmation"] is True
        and reference_review["required_markers_present"] is True
    )
    final_verdict = FINAL_VERDICT if reference_ready else REFERENCE_MISSING_VERDICT
    status = STATUS if reference_ready else "FAIL"

    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": status,
        "overall_status": status,
        "final_verdict": final_verdict,
        "phase_goal": PHASE_GOAL,
        "interview_mvp_definition": INTERVIEW_MVP_DEFINITION,
        "safe_dry_run_platform_scope": SAFE_DRY_RUN_PLATFORM_SCOPE,
        "safe_runner_architecture_boundary": SAFE_RUNNER_ARCHITECTURE_BOUNDARY,
        "mock_adapter_boundary": MOCK_ADAPTER_BOUNDARY,
        "result_envelope_boundary": RESULT_ENVELOPE_BOUNDARY,
        "demo_job_candidate_boundary": DEMO_JOB_CANDIDATE_BOUNDARY,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "demo_job_candidates": list(_demo_job_candidate_records()),
        "next_implementation_candidates": list(NEXT_IMPLEMENTATION_CANDIDATES),
        "authorization_status": dict(AUTHORIZATION_STATUS),
        "required_reference_document_review": reference_review,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_action": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "status": "PASS" if reference_ready else "FAIL",
            "scope_confirmation_written": True,
            "task_mode": "planning-only / authorization-gate",
            "phase_goal": PHASE_GOAL,
            "example_job_types": list(EXAMPLE_JOB_TYPES),
            "forbidden_scope": list(FORBIDDEN_SCOPE),
            "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REVIEWED),
            "implementation_boundary": IMPLEMENTATION_BOUNDARY,
            "validation_plan": (
                "Run the Phase 2C-11 targeted pytest, run the Phase 2C-11 "
                "report-only task, and run report-index validation. Run full "
                "pytest only because catalog, CLI, and report-index visibility "
                "metadata are updated."
            ),
            "needs_scope_confirmation": False,
        },
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_reviewed": list(EXISTING_ARTIFACTS_REVIEWED),
        "artifact_records": [_artifact_record(project_root, path) for path in EXISTING_ARTIFACTS_REVIEWED],
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "decision_criteria": deepcopy(DECISION_CRITERIA),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_execution_statement": (
            "Phase 2C-11 is planning-only authorization evidence. It defines "
            "Interview MVP scope and architecture boundaries but does not "
            "implement or start a runner, adapter, result envelope, report "
            "renderer, demo job, scheduler, queue, worker, AI agent loop, SSH, "
            "NETCONF, RESTCONF, live device access, provider/API/model "
            "integration, secrets handling, config backup, config change, "
            "production execution, Phase 2C-12, Day1-Day160 rewrite, Phase "
            "2C-10 modification, or a second safety matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "REQUIRED_REFERENCE_DOCUMENT_FOUND": "YES",
            "REQUIRED_REFERENCE_DOCUMENT_READ": "YES",
            "INTERVIEW_MVP_DEFINITION_PRESENT": "YES",
            "SAFE_DRY_RUN_PLATFORM_SCOPE_DEFINED": "YES",
            "RUNNER_ARCHITECTURE_BOUNDARY_DEFINED": "YES",
            "MOCK_ADAPTER_BOUNDARY_DEFINED": "YES",
            "RESULT_ENVELOPE_BOUNDARY_DEFINED": "YES",
            "DEMO_JOB_CANDIDATES_EXAMPLES_ONLY": "YES",
            "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED": "YES",
            "IMPLEMENTATION_AUTHORIZED": "NO",
            "IMPLEMENTATION_STARTED": "NO",
            "PHASE_2C_12_STARTED": "NO",
            "RUNNER_ADAPTER_RESULT_ENVELOPE_REPORT_RENDERER_DEMO_JOBS_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
            "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "PHASE_2C_10_MODIFIED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    if not reference_ready:
        report["required_reference_document_found"] = bool(reference_review["exists"])
        report["required_reference_document_read_before_scope_confirmation"] = False
        report["machine_readable_verdict"] = {
            **report["machine_readable_verdict"],
            "FINAL_VERDICT": REFERENCE_MISSING_VERDICT,
            "REQUIRED_REFERENCE_DOCUMENT_FOUND": "YES" if reference_review["exists"] else "NO",
            "REQUIRED_REFERENCE_DOCUMENT_READ": "NO",
        }

    report["summary"] = {
        "required_reference_document_found": reference_review["exists"],
        "required_reference_document_read_before_scope_confirmation": reference_review[
            "read_before_scope_confirmation"
        ],
        "interview_mvp_defined": True,
        "safe_dry_run_platform_scope_defined": True,
        "runner_architecture_boundary_defined": True,
        "mock_adapter_boundary_defined": True,
        "result_envelope_boundary_defined": True,
        "demo_job_candidates": list(EXAMPLE_JOB_TYPES),
        "later_implementation_planning_authorized": True,
        "implementation_authorized": False,
        "implementation_started": False,
        "phase_2c_12_started": False,
        "runner_adapter_result_envelope_report_renderer_demo_jobs_added": False,
        "scheduler_queue_broker_worker_agent_loop_added": False,
        "live_device_ssh_netconf_restconf_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "production_execution_path_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "phase_2c_10_modified": False,
        "final_verdict": final_verdict,
    }
    validation = validate_phase_2c_11_report(report) if reference_ready else {
        "valid": False,
        "status": "FAIL",
        "errors": [REFERENCE_MISSING_VERDICT],
        "decision_criteria_checked": len(report.get("decision_criteria", [])),
        "existing_artifacts_reviewed": len(report.get("existing_artifacts_reviewed", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "demo_job_candidates_checked": len(report.get("demo_job_candidates", [])),
    }
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        if reference_ready:
            report["final_verdict"] = NEEDS_SCOPE_CONFIRMATION_VERDICT
            report["summary"]["final_verdict"] = NEEDS_SCOPE_CONFIRMATION_VERDICT
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
        f"<td>{html.escape(str(item.get('job_type')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_only')))}</td>"
        f"<td>{html.escape(str(item.get('selected')))}</td>"
        f"<td>{html.escape(str(item.get('implemented')))}</td>"
        f"<td>{html.escape(str(item.get('execution_capable')))}</td>"
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
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Interview MVP Definition</h2>
  <p>{html.escape(str(report["interview_mvp_definition"]))}</p>
  <h2>Architecture Boundaries</h2>
  <table><tbody>{_dict_rows({
            "safe_dry_run_platform_scope": report["safe_dry_run_platform_scope"],
            "safe_runner_architecture_boundary": report["safe_runner_architecture_boundary"],
            "mock_adapter_boundary": report["mock_adapter_boundary"],
            "result_envelope_boundary": report["result_envelope_boundary"],
        })}</tbody></table>
  <h2>Demo Job Candidates</h2>
  <table><thead><tr><th>Job type</th><th>Candidate only</th><th>Selected</th><th>Implemented</th><th>Execution capable</th></tr></thead><tbody>{_candidate_rows(report["demo_job_candidates"])}</tbody></table>
  <h2>Decision Criteria</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_check_rows(report["decision_criteria"])}</tbody></table>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Reviewed</h2>
  <ul>{_list_items(report["existing_artifacts_reviewed"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_11_interview_mvp_scope_architecture_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_11_interview_mvp_scope_architecture_gate_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_11_interview_mvp_scope_architecture_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_11_interview_mvp_scope_architecture_gate_report(project_root)
    json_path, html_path = write_phase_2c_11_interview_mvp_scope_architecture_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"required_reference_document_found: {str(report['summary']['required_reference_document_found']).lower()}")
    print(
        "required_reference_document_read_before_scope_confirmation: "
        f"{str(report['summary']['required_reference_document_read_before_scope_confirmation']).lower()}"
    )
    print(f"interview_mvp_defined: {str(report['summary']['interview_mvp_defined']).lower()}")
    print(
        "safe_dry_run_platform_scope_defined: "
        f"{str(report['summary']['safe_dry_run_platform_scope_defined']).lower()}"
    )
    print(
        "runner_architecture_boundary_defined: "
        f"{str(report['summary']['runner_architecture_boundary_defined']).lower()}"
    )
    print(f"mock_adapter_boundary_defined: {str(report['summary']['mock_adapter_boundary_defined']).lower()}")
    print(f"result_envelope_boundary_defined: {str(report['summary']['result_envelope_boundary_defined']).lower()}")
    print(
        "later_implementation_planning_authorized: "
        f"{str(report['summary']['later_implementation_planning_authorized']).lower()}"
    )
    print(f"implementation_authorized: {str(report['summary']['implementation_authorized']).lower()}")
    print(f"implementation_started: {str(report['summary']['implementation_started']).lower()}")
    print(f"phase_2c_12_started: {str(report['summary']['phase_2c_12_started']).lower()}")
    print(
        "runner_adapter_result_envelope_report_renderer_demo_jobs_added: "
        f"{str(report['summary']['runner_adapter_result_envelope_report_renderer_demo_jobs_added']).lower()}"
    )
    print(
        "scheduler_queue_broker_worker_agent_loop_added: "
        f"{str(report['summary']['scheduler_queue_broker_worker_agent_loop_added']).lower()}"
    )
    print(
        "live_device_ssh_netconf_restconf_touched: "
        f"{str(report['summary']['live_device_ssh_netconf_restconf_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(
        "config_backup_or_change_behavior_added: "
        f"{str(report['summary']['config_backup_or_change_behavior_added']).lower()}"
    )
    print(
        "production_execution_path_added: "
        f"{str(report['summary']['production_execution_path_added']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"phase_2c_10_modified: {str(report['summary']['phase_2c_10_modified']).lower()}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
