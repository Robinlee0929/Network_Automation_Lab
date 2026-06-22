"""Phase 2C-04 next-slice candidate inventory.

This module creates deterministic, local, planning-only inventory evidence for
possible next-slice candidates after Phase 2C-03. It does not select,
authorize, scaffold, implement, or prepare execution for any candidate and does
not open runners, adapters, brokers, schedulers, queues, execution paths, SSH,
NETCONF, RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_13_first_slice_final_selection_gate import FINAL_VERDICT as PHASE_2B_13_VERDICT
from phase_2b_14_first_slice_implementation_kickoff_gate import FINAL_VERDICT as PHASE_2B_14_VERDICT
from phase_2c_01_local_static_job_first_slice import FINAL_VERDICT as PHASE_2C_01_VERDICT
from phase_2c_02_post_first_slice_acceptance_review import FINAL_VERDICT as PHASE_2C_02_VERDICT
from phase_2c_03_next_slice_decision_gate_authorization_review import (
    FINAL_VERDICT as PHASE_2C_03_VERDICT,
    TASK_NAME as PHASE_2C_03_TASK_NAME,
    build_phase_2c_03_next_slice_decision_gate_authorization_review_report,
    validate_phase_2c_03_report,
)


PHASE = "2C-04"
TASK_NAME = "phase2c-04-next-slice-candidate-inventory"
TITLE = "Phase 2C-04 Next-Slice Candidate Inventory - Planning Only"
MODE = "planning_only_candidate_inventory"
SCOPE = "phase_wide_candidate_inventory_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_04_CANDIDATE_INVENTORY_DONE_NEXT_SLICE_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_04_next_slice_candidate_inventory.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_04_next_slice_candidate_inventory.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_04_next_slice_candidate_inventory.md"

PHASE_GOAL = (
    "Inventory possible next-slice candidates after Phase 2C-03 as a "
    "planning-only candidate list and review. No single candidate is selected "
    "as the next slice, and Phase 2C-05 or any later implementation is not "
    "authorized by this task."
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

FORBIDDEN_SCOPE = (
    "candidate implementation",
    "next-slice selection",
    "Phase 2C-05 authorization",
    "later implementation authorization",
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
    "AGENTS.md",
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md",
    "phase_2b_13_first_slice_final_selection_gate.py",
    "phase_2b_14_first_slice_implementation_kickoff_gate.py",
    "phase_2c_01_local_static_job_first_slice.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "Day1-Day160 existing reference material only",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add the Phase 2C-04 planning-only candidate inventory artifact, "
    "minimal report-only Python evidence generation, targeted tests, and "
    "registry/CLI/report-index visibility. Not allowed: selecting a next "
    "slice, authorizing Phase 2C-05, implementing or scaffolding any candidate, "
    "or adding runner, adapter, scheduler, queue, broker, worker, agent loop, "
    "execution, provider/API/model, secret, SSH, NETCONF, RESTCONF, live-device, "
    "backup, config-change, Day1-Day160 replacement, AGENTS.md modification, "
    "or second safety-matrix behavior."
)

NEUTRAL_REVIEW_FIELDS = (
    "candidate_id",
    "example_job_type",
    "readiness_note",
    "dependency_note",
    "safety_note",
    "existing_reference",
    "inventory_status",
    "selected",
)

CANDIDATE_INVENTORY = (
    {
        "candidate_id": "candidate-01",
        "example_job_type": "local_static_job continuation",
        "readiness_note": "Could continue static contract evidence review without opening runtime behavior.",
        "dependency_note": "Depends on Phase 2C-01 acceptance and Phase 2C-03 planning gate evidence.",
        "safety_note": "Must remain local, deterministic, report-only, and non-executing.",
        "existing_reference": "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-02",
        "example_job_type": "artifact validation job",
        "readiness_note": "Could validate existing artifact shape and reviewer visibility only.",
        "dependency_note": "Depends on existing Phase 2B/2C artifact naming and report-index conventions.",
        "safety_note": "Must not validate by executing devices, commands, providers, or adapters.",
        "existing_reference": "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-03",
        "example_job_type": "report-only evidence collection job",
        "readiness_note": "Could collect deterministic local report metadata for reviewer evidence.",
        "dependency_note": "Depends on existing report-index metadata and local report paths.",
        "safety_note": "Must not collect live, private, credential, provider, or device data.",
        "existing_reference": "reports/report_index.html",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-04",
        "example_job_type": "dry-run result rendering job",
        "readiness_note": "Could render already-approved dry-run result envelopes as display evidence.",
        "dependency_note": "Depends on existing dry-run renderer and Phase 2A display contracts.",
        "safety_note": "Must not create a runner, scheduler, queue, or real execution path.",
        "existing_reference": "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-05",
        "example_job_type": "mock parse/report job",
        "readiness_note": "Could summarize existing mock parser/report evidence without live inputs.",
        "dependency_note": "Depends on existing parser evidence and mock-only fixtures.",
        "safety_note": "Must not parse live command output or reach SSH/API/provider paths.",
        "existing_reference": "docs/ai/readonly_output_parser_prototype.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-06",
        "example_job_type": "candidate UI display contract follow-up",
        "readiness_note": "Could review display-contract expectations for existing report-only evidence.",
        "dependency_note": "Depends on existing dashboard/report display contracts.",
        "safety_note": "Must not add POST actions, execution controls, or workflow unlocks.",
        "existing_reference": "docs/phase_2a/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
    {
        "candidate_id": "candidate-07",
        "example_job_type": "candidate safety regression follow-up",
        "readiness_note": "Could review existing safety flags for regression coverage gaps.",
        "dependency_note": "Depends on existing safety regression evidence without creating a second matrix.",
        "safety_note": "Must reference existing safety evidence and avoid replacing Day1-Day160 material.",
        "existing_reference": "docs/roadmap/day123_safety_boundary_regression_matrix.md",
        "inventory_status": "CANDIDATE_ONLY",
        "selected": False,
    },
)

REVIEW_CHECKS = (
    {
        "check": "Phase 2C-03 evidence is referenced as prior planning gate input",
        "expected": PHASE_2C_03_VERDICT,
        "status": "PASS",
    },
    {
        "check": "Candidate list remains broader than one example job type",
        "expected": "candidate_count > 1",
        "status": "PASS",
    },
    {
        "check": "No candidate is selected as the next slice",
        "expected": "selected == false for every candidate",
        "status": "PASS",
    },
    {
        "check": "Phase 2C-05 and later implementation remain unauthorized",
        "expected": "phase_2c_05_authorized == false",
        "status": "PASS",
    },
    {
        "check": "No runner, adapter, broker, scheduler, queue, worker, or execution path is added",
        "expected": "runner_adapter_execution_path_added == false",
        "status": "PASS",
    },
    {
        "check": "No SSH, NETCONF, RESTCONF, live device, provider/API/model, or secret path is touched",
        "expected": "live_and_provider_paths_touched == false",
        "status": "PASS",
    },
)

SAFETY_FLAGS = {
    "phase_2c_04_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_goal_separated": True,
    "example_job_types_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "candidate_inventory_only": True,
    "candidate_selected": False,
    "next_slice_authorized": False,
    "phase_2c_05_authorized": False,
    "later_implementation_authorized": False,
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
    "PHASE_2C_04_NEXT_SLICE_CANDIDATE_INVENTORY_PLANNING_ONLY",
    "CANDIDATE_INVENTORY_ONLY_YES",
    "CANDIDATE_SELECTED_NO",
    "NEXT_SLICE_AUTHORIZED_NO",
    "PHASE_2C_05_AUTHORIZED_NO",
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
            "allowed_by_phase_2c_04": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _phase_2c_03_input_review() -> Dict[str, Any]:
    phase_2c_03_report = build_phase_2c_03_next_slice_decision_gate_authorization_review_report()
    phase_2c_03_validation = validate_phase_2c_03_report(phase_2c_03_report)
    return {
        "reviewed_task": PHASE_2C_03_TASK_NAME,
        "expected_verdict": PHASE_2C_03_VERDICT,
        "observed_verdict": phase_2c_03_report.get("final_verdict"),
        "source_validation": phase_2c_03_validation,
        "phase_2c_03_authorization_scope": phase_2c_03_report.get("authorization_scope"),
        "phase_2c_03_next_slice_selected": phase_2c_03_report.get("next_slice_selected"),
        "phase_2c_03_next_slice_implemented": phase_2c_03_report.get("next_slice_implemented"),
    }


def validate_phase_2c_04_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("inventory_decision") != "CANDIDATE_INVENTORY_ONLY":
        errors.append("INVENTORY_DECISION_MISMATCH")

    source_review = report.get("phase_2c_03_input_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_03_INPUT_NOT_OBJECT")
        source_review = {}
    if source_review.get("reviewed_task") != PHASE_2C_03_TASK_NAME:
        errors.append("PHASE_2C_03_TASK_MISMATCH")
    if source_review.get("observed_verdict") != PHASE_2C_03_VERDICT:
        errors.append("PHASE_2C_03_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_03_VALIDATION_NOT_PASS")

    candidate_inventory = report.get("candidate_inventory", [])
    if not isinstance(candidate_inventory, Sequence) or isinstance(candidate_inventory, (str, bytes)):
        errors.append("CANDIDATE_INVENTORY_NOT_LIST")
        candidate_inventory = []
    expected_ids = {candidate["candidate_id"] for candidate in CANDIDATE_INVENTORY}
    observed_ids = {
        candidate.get("candidate_id")
        for candidate in candidate_inventory
        if isinstance(candidate, Mapping)
    }
    if observed_ids != expected_ids:
        errors.append("CANDIDATE_ID_SET_MISMATCH")
    if len(candidate_inventory) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_EXAMPLE")
    if any(isinstance(candidate, Mapping) and candidate.get("selected") is not False for candidate in candidate_inventory):
        errors.append("CANDIDATE_SELECTED")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if set(report.get("neutral_review_fields", [])) != set(NEUTRAL_REVIEW_FIELDS):
        errors.append("NEUTRAL_REVIEW_FIELDS_MISMATCH")
    if tuple(report.get("review_checks", ())) != REVIEW_CHECKS:
        errors.append("REVIEW_CHECKS_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("review_checks", ())):
        errors.append("REVIEW_CHECK_NOT_PASS")
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
        "CANDIDATE_INVENTORY_ONLY": "YES",
        "CANDIDATE_SELECTED": "NO",
        "NEXT_SLICE_AUTHORIZED": "NO",
        "PHASE_2C_05_AUTHORIZED": "NO",
        "IMPLEMENTATION_ADDED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "candidate_selected",
            "next_slice_authorized",
            "phase_2c_05_authorized",
            "later_implementation_authorized",
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
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "candidate_count": len(candidate_inventory),
        "review_checks_checked": len(report.get("review_checks", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(artifacts),
    }


def build_phase_2c_04_next_slice_candidate_inventory_report() -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "inventory_decision": "CANDIDATE_INVENTORY_ONLY",
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_not_selection_or_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "neutral_review_fields": list(NEUTRAL_REVIEW_FIELDS),
        "candidate_inventory": deepcopy(CANDIDATE_INVENTORY),
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "phase_2b_14_verdict_referenced": PHASE_2B_14_VERDICT,
        "phase_2c_01_verdict_referenced": PHASE_2C_01_VERDICT,
        "phase_2c_02_verdict_referenced": PHASE_2C_02_VERDICT,
        "phase_2c_03_input_review": _phase_2c_03_input_review(),
        "review_checks": deepcopy(REVIEW_CHECKS),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "inventory_statement": (
            "Phase 2C-04 records possible next-slice candidates only. The "
            "candidate inventory is neutral planning evidence, not a ranking, "
            "final selection, authorization, scaffold, or implementation plan."
        ),
        "non_execution_statement": (
            "This task does not authorize Phase 2C-05 or any later "
            "implementation. It opens no runner, adapter, broker, scheduler, "
            "queue, worker, agent loop, execution, provider/API/model, secret, "
            "SSH, NETCONF, RESTCONF, live-device, backup, or config-change scope."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "CANDIDATE_INVENTORY_ONLY": "YES",
            "CANDIDATE_SELECTED": "NO",
            "NEXT_SLICE_AUTHORIZED": "NO",
            "PHASE_2C_05_AUTHORIZED": "NO",
            "IMPLEMENTATION_ADDED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "candidate_count": len(CANDIDATE_INVENTORY),
        "candidate_inventory_only": True,
        "candidate_selected": False,
        "next_slice_authorized": False,
        "phase_2c_05_authorized": False,
        "implementation_added": False,
        "runner_adapter_execution_path_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "scope_narrowed_to_one_example_job_type": False,
        "needs_scope_confirmation": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_04_report(report)
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


def _review_rows(values: Sequence[Mapping[str, Any]]) -> str:
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
        f"<td>{html.escape(str(item.get('example_job_type')))}</td>"
        f"<td>{html.escape(str(item.get('readiness_note')))}</td>"
        f"<td>{html.escape(str(item.get('dependency_note')))}</td>"
        f"<td>{html.escape(str(item.get('safety_note')))}</td>"
        f"<td>{html.escape(str(item.get('selected')))}</td>"
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
  <p>Inventory decision: <strong>{html.escape(str(report["inventory_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["inventory_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Candidate Inventory</h2>
  <table><thead><tr><th>Candidate</th><th>Example Job Type</th><th>Readiness Note</th><th>Dependency Note</th><th>Safety Note</th><th>Selected</th></tr></thead><tbody>{_candidate_rows(report["candidate_inventory"])}</tbody></table>
  <h2>Review Checks</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_review_rows(report["review_checks"])}</tbody></table>
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


def write_phase_2c_04_next_slice_candidate_inventory_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_04_next_slice_candidate_inventory_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_04_next_slice_candidate_inventory(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_04_next_slice_candidate_inventory_report()
    json_path, html_path = write_phase_2c_04_next_slice_candidate_inventory_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Inventory decision: {report['inventory_decision']}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"candidate_inventory_only: {str(report['summary']['candidate_inventory_only']).lower()}")
    print(f"candidate_selected: {str(report['summary']['candidate_selected']).lower()}")
    print(f"next_slice_authorized: {str(report['summary']['next_slice_authorized']).lower()}")
    print(f"phase_2c_05_authorized: {str(report['summary']['phase_2c_05_authorized']).lower()}")
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
    print(
        "scope_narrowed_to_one_example_job_type: "
        f"{str(report['summary']['scope_narrowed_to_one_example_job_type']).lower()}"
    )
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(f"Review checks checked: {report['validation']['review_checks_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
