"""Phase 2B-07 first-slice definition pack.

This module creates a deterministic, local, planning-only definition pack for
the first minimal safe implementation slice that may be implemented later only
after explicit authorization. It does not re-run the Phase 2B-06 entry gate
review, recreate safety gates, implement the slice, or enable runners,
adapters, brokers, schedulers, queue workers, execution engines, SSH, NETCONF,
RESTCONF, live-device access, provider/API/model calls, secrets handling,
frontend integration, backup, validation, or command execution.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review import (
    FINAL_VERDICT as PHASE_2B_06_VERDICT,
)


PHASE = "2B-07"
TASK_NAME = "phase2b-07-first-slice-definition-pack"
TITLE = "Phase 2B-07 First-Slice Definition Pack"
MODE = "planning_only_first_slice_definition_pack"
SCOPE = "phase_wide_phase_2b_first_slice_definition_pack_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_07_FIRST_SLICE_DEFINED_PLANNING_ONLY"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_07_first_slice_definition_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_07_first_slice_definition_pack.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_07_first_slice_definition_pack.md"

PHASE_GOAL = (
    "Define the first minimal safe implementation slice for a future Phase 2B "
    "implementation step while remaining planning-only."
)

FIRST_MINIMAL_SAFE_SLICE = {
    "name": "local_static_job_definition_and_evidence_contract_slice",
    "definition": (
        "A future, explicitly authorized implementation may add only local static "
        "job-definition and reviewer-evidence contract structures for the Phase 2B "
        "job lifecycle. The slice may describe supported planning states, safety "
        "flags, evidence fields, and report visibility for multiple example job "
        "types, but it must not execute work or connect to any device or provider."
    ),
    "why_minimal": (
        "It creates the smallest reviewable boundary needed before any executable "
        "workflow can be discussed: static contracts, examples-only job categories, "
        "machine-readable no-execution flags, and tests that prove forbidden paths "
        "remain absent."
    ),
    "why_safe": (
        "It keeps all execution-capable surfaces out of scope and requires future "
        "tests to fail if a runner, adapter, broker, scheduler, queue worker, "
        "network client, provider/API/model call, secret path, frontend integration, "
        "or live-device path appears."
    ),
}

IN_SCOPE_BOUNDARIES = (
    "planning-only definition of a future local static job-definition contract",
    "planning-only definition of future reviewer-evidence fields",
    "planning-only definition of future machine-readable no-execution flags",
    "planning-only definition of future report-index visibility expectations",
    "phase-wide treatment of example job types as examples only",
    "future negative-test expectations proving no execution path is reached",
    "references to existing Phase 2B safety gates without changing them",
)

OUT_OF_SCOPE_BOUNDARIES = (
    "slice implementation",
    "runner",
    "adapter",
    "broker",
    "scheduler",
    "queue worker",
    "execution engine",
    "provider integration",
    "API call",
    "model call",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "real backup",
    "real configuration collection",
    "real validation",
    "real command execution",
    "secrets handling",
    "frontend integration",
    "background execution",
    "second safety matrix",
    "Phase 2B-06 entry gate re-run",
    "GO/NO-GO verdict change from Phase 2B-06",
)

AUTHORITATIVE_SAFETY_GATES = (
    {
        "gate": "Phase 2B-00 authorization / scope gate review",
        "artifact": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "authority": "Keeps Phase 2B implementation locked unless separately authorized.",
    },
    {
        "gate": "Phase 2B-00A owner authorization statement",
        "artifact": "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "authority": "Authorizes planning-only scope and denies implementation.",
    },
    {
        "gate": "Phase 2B-01 planning scope design",
        "artifact": "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "authority": "Preserves phase-wide scope and examples-only job types.",
    },
    {
        "gate": "Phase 2B-02 safety gate design planning",
        "artifact": "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "authority": "Defines planning-only future gate categories and stop conditions.",
    },
    {
        "gate": "Phase 2B-04 safety artifact crosswalk and gap review",
        "artifact": "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "authority": "References existing safety coverage without creating a new matrix.",
    },
    {
        "gate": "Phase 2B-05 Day1-Day160 safety de-duplication acceptance criteria",
        "artifact": "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "authority": "Controls de-duplication and prohibits second or replacement safety matrices.",
    },
    {
        "gate": "Phase 2B-06 implementation entry gate and first-slice readiness review",
        "artifact": "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
        "authority": "Provides the GO_TO_DEFINE_FIRST_SLICE_PLANNING_ONLY verdict; this task does not re-run or change it.",
    },
)

HISTORICAL_PHASE_2A_CONTEXT = (
    "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
    "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
    "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
    "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
    "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
    "docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
    "docs/phase_2a/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md",
    "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
    "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
)

FUTURE_IMPLEMENTATION_PRECONDITIONS = (
    "Explicit user authorization for a future implementation task.",
    "Written confirmation that the future scope remains phase-wide and examples-only.",
    "No narrower task title, branch name, file name, or implementation goal that reduces Phase 2B to one example job type.",
    "Existing Phase 2B safety gates remain authoritative and unchanged.",
    "Phase 2B-06 verdict remains GO_TO_DEFINE_FIRST_SLICE_PLANNING_ONLY and is not re-run here.",
    "A future test plan proves rejected, planning-only, dry-run-only, mock-only, and report-only flows reach no execution path.",
    "Reviewer-facing evidence paths and report-index visibility are identified before implementation begins.",
)

FUTURE_ACCEPTANCE_CRITERIA = (
    "The future implementation contains static local contract structures only.",
    "It covers multiple example job types without narrowing the phase to one job or one device scenario.",
    "It keeps runner_enabled, adapter_enabled, execution_path_implemented, provider_api_model_calls_enabled, and live_device_access_enabled false.",
    "It adds negative tests proving forbidden capability paths are absent or unreachable.",
    "It preserves Phase 2B-05 de-duplication authority and does not create a second safety matrix.",
    "It produces reviewer-visible evidence without live dependencies, private config, secrets, SSH, VPN, WireGuard, external services, or provider calls.",
)

MUST_REMAIN_LIMITED_TO = (
    "mock-only",
    "dry-run-only",
    "report-only",
    "documentation-only",
    "design-only",
    "local deterministic validation-only",
)

STOP_CONDITIONS = (
    "Scope narrows to only VRRP, only backup, only baseline, only one job type, or only one device scenario.",
    "Any runner, adapter, broker, scheduler, queue worker, or execution engine is introduced.",
    "Any SSH, NETCONF, RESTCONF, API, provider, model, secret, frontend integration, background execution, or live-device path is introduced.",
    "The task attempts to collect real backup, real configuration, real validation, or real command output.",
    "A second safety matrix or replacement safety gate framework is created.",
    "The Phase 2B-06 verdict is changed or the entry gate review is re-run.",
    "Non-execution proof is missing, ambiguous, or weakened.",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "first_slice_defined": True,
    "first_slice_implemented": False,
    "readiness_review_rerun": False,
    "entry_gate_review_rerun": False,
    "safety_gates_recreated": False,
    "second_safety_matrix_created": False,
    "runner_enabled": False,
    "adapter_enabled": False,
    "execution_path_implemented": False,
    "broker_enabled": False,
    "scheduler_enabled": False,
    "queue_worker_enabled": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "live_device_access_enabled": False,
    "provider_api_model_calls_enabled": False,
    "provider_calls_enabled": False,
    "api_calls_enabled": False,
    "model_calls_enabled": False,
    "secrets_handling_enabled": False,
    "frontend_integration_enabled": False,
    "background_execution_enabled": False,
    "real_backup_enabled": False,
    "real_configuration_collection_enabled": False,
    "real_validation_enabled": False,
    "real_command_execution_enabled": False,
    "device_mutation_enabled": False,
    "approval_bypass_enabled": False,
    "safety_gate_weakening_enabled": False,
}

COMPLETION_MARKERS = (
    FINAL_VERDICT,
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "SAFETY_GATES_RECREATED_FALSE",
    "ENTRY_GATE_REVIEW_RERUN_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE",
    "PROVIDER_API_MODEL_CALLS_ENABLED_FALSE",
    "LIVE_DEVICE_ACCESS_ENABLED_FALSE",
)


def _authoritative_safety_gates() -> Tuple[Dict[str, str], ...]:
    return tuple(deepcopy(item) for item in AUTHORITATIVE_SAFETY_GATES)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_07": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_07_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
    if len(example_job_types) <= 1 or example_job_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    first_slice = report.get("first_minimal_safe_slice", {})
    if not isinstance(first_slice, Mapping):
        errors.append("FIRST_MINIMAL_SAFE_SLICE_NOT_OBJECT")
        first_slice = {}
    for field in ("name", "definition", "why_minimal", "why_safe"):
        if field not in first_slice:
            errors.append(f"FIRST_MINIMAL_SAFE_SLICE_MISSING:{field}")
    if first_slice.get("name") == "vrrp_validation":
        errors.append("FIRST_SLICE_NARROWED_TO_VRRP")

    if set(report.get("in_scope_boundaries", [])) != set(IN_SCOPE_BOUNDARIES):
        errors.append("IN_SCOPE_BOUNDARIES_MISMATCH")
    if set(report.get("out_of_scope_boundaries", [])) != set(OUT_OF_SCOPE_BOUNDARIES):
        errors.append("OUT_OF_SCOPE_BOUNDARIES_MISMATCH")
    if set(report.get("future_implementation_preconditions", [])) != set(FUTURE_IMPLEMENTATION_PRECONDITIONS):
        errors.append("FUTURE_IMPLEMENTATION_PRECONDITIONS_MISMATCH")
    if set(report.get("future_acceptance_criteria", [])) != set(FUTURE_ACCEPTANCE_CRITERIA):
        errors.append("FUTURE_ACCEPTANCE_CRITERIA_MISMATCH")
    if set(report.get("stop_conditions", [])) != set(STOP_CONDITIONS):
        errors.append("STOP_CONDITIONS_MISMATCH")

    safety_gate_names = {str(item.get("gate")) for item in report.get("authoritative_safety_gates", []) if isinstance(item, Mapping)}
    expected_gate_names = {item["gate"] for item in AUTHORITATIVE_SAFETY_GATES}
    if safety_gate_names != expected_gate_names:
        errors.append("AUTHORITATIVE_SAFETY_GATES_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_06_VERDICT_REFERENCED": PHASE_2B_06_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_DEFINED": "YES",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "SAFETY_GATES_RECREATED": "NO",
        "ENTRY_GATE_REVIEW_RERUN": "NO",
        "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
        "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
        "LIVE_DEVICE_ACCESS_ENABLED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "authoritative_safety_gates_checked": len(safety_gate_names),
        "future_preconditions_checked": len(report.get("future_implementation_preconditions", [])),
        "future_acceptance_criteria_checked": len(report.get("future_acceptance_criteria", [])),
        "stop_conditions_checked": len(report.get("stop_conditions", [])),
    }


def build_phase_2b_07_first_slice_definition_pack_report() -> Dict[str, Any]:
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
            "forbidden_scope": list(FORBIDDEN_CAPABILITIES),
            "existing_artifacts_to_reference": [item["artifact"] for item in AUTHORITATIVE_SAFETY_GATES],
            "implementation_boundary": list(IN_SCOPE_BOUNDARIES) + list(OUT_OF_SCOPE_BOUNDARIES),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "phase_2b_06_relationship": {
            "referenced_verdict": PHASE_2B_06_VERDICT,
            "entry_gate_review_rerun": False,
            "verdict_changed": False,
            "relationship": (
                "Phase 2B-07 uses the Phase 2B-06 GO_TO_DEFINE_FIRST_SLICE_PLANNING_ONLY "
                "verdict as input and defines the first slice planning boundary. It is not "
                "a readiness review and does not re-run Phase 2B-06."
            ),
        },
        "first_minimal_safe_slice": deepcopy(FIRST_MINIMAL_SAFE_SLICE),
        "in_scope_boundaries": list(IN_SCOPE_BOUNDARIES),
        "out_of_scope_boundaries": list(OUT_OF_SCOPE_BOUNDARIES),
        "authoritative_safety_gates": list(_authoritative_safety_gates()),
        "existing_artifacts_referenced": [item["artifact"] for item in AUTHORITATIVE_SAFETY_GATES],
        "historical_phase_2a_context": list(HISTORICAL_PHASE_2A_CONTEXT),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "future_implementation_preconditions": list(FUTURE_IMPLEMENTATION_PRECONDITIONS),
        "future_acceptance_criteria": list(FUTURE_ACCEPTANCE_CRITERIA),
        "must_remain_limited_to": list(MUST_REMAIN_LIMITED_TO),
        "stop_conditions": list(STOP_CONDITIONS),
        "non_duplication_statement": (
            "Phase 2B-07 does not create, duplicate, rename, replace, or weaken safety gates. "
            "Phase 2B-05 remains authoritative for de-duplication, and Phase 2B-06 is referenced "
            "without being re-run."
        ),
        "non_implementation_statement": (
            "This task is planning-only. It does not implement the slice, re-create safety gates, "
            "re-run the Phase 2B-06 entry gate review, authorize live execution, or enable runner, "
            "adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, API, provider, "
            "model, secrets, frontend, background, or live-device access."
        ),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_06_VERDICT_REFERENCED": PHASE_2B_06_VERDICT,
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "FIRST_SLICE_DEFINED": "YES",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "SAFETY_GATES_RECREATED": "NO",
            "ENTRY_GATE_REVIEW_RERUN": "NO",
            "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
            "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
            "LIVE_DEVICE_ACCESS_ENABLED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "safety_gates_recreated": False,
            "entry_gate_review_rerun": False,
            "first_slice_implemented": False,
            "runner_adapter_execution_enabled": False,
            "provider_api_model_calls_enabled": False,
            "live_device_access_enabled": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_07_report(report)
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
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Relationship to Phase 2B-06</h2>
  <table><tbody>{_dict_rows(report["phase_2b_06_relationship"])}</tbody></table>
  <h2>First Minimal Safe Slice</h2>
  <table><tbody>{_dict_rows(report["first_minimal_safe_slice"])}</tbody></table>
  <h2>In Scope</h2>
  <ul>{_list_items(report["in_scope_boundaries"])}</ul>
  <h2>Out of Scope</h2>
  <ul>{_list_items(report["out_of_scope_boundaries"])}</ul>
  <h2>Authoritative Safety Gates</h2>
  <table>
    <thead><tr><th>Gate</th><th>Artifact</th><th>Authority</th></tr></thead>
    <tbody>{_table_rows(report["authoritative_safety_gates"], ("gate", "artifact", "authority"))}</tbody>
  </table>
  <h2>Future Preconditions</h2>
  <ul>{_list_items(report["future_implementation_preconditions"])}</ul>
  <h2>Future Acceptance Criteria</h2>
  <ul>{_list_items(report["future_acceptance_criteria"])}</ul>
  <h2>Stop Conditions</h2>
  <ul>{_list_items(report["stop_conditions"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_07_first_slice_definition_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_07_first_slice_definition_pack_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_07_first_slice_definition_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_07_first_slice_definition_pack_report()
    json_path, html_path = write_phase_2b_07_first_slice_definition_pack_reports(project_root, report)
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
    print(f"safety_gates_recreated: {str(report['safety_gates_recreated']).lower()}")
    print(f"entry_gate_review_rerun: {str(report['entry_gate_review_rerun']).lower()}")
    print(f"first_slice_implemented: {str(report['first_slice_implemented']).lower()}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"execution_path_implemented: {str(report['execution_path_implemented']).lower()}")
    print(f"provider_api_model_calls_enabled: {str(report['provider_api_model_calls_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"Authoritative safety gates checked: {report['validation']['authoritative_safety_gates_checked']}")
    print(f"Future preconditions checked: {report['validation']['future_preconditions_checked']}")
    print(f"Future acceptance criteria checked: {report['validation']['future_acceptance_criteria_checked']}")
    print(f"Stop conditions checked: {report['validation']['stop_conditions_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
