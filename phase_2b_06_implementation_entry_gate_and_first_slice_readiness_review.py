"""Phase 2B-06 implementation entry gate and first-slice readiness review.

This module creates a deterministic, local, planning-only readiness review for
Phase 2B. It decides only whether the project is ready to define a future first
safe implementation slice planning artifact. It does not implement or authorize
the slice, create a second safety matrix, or enable runners, adapters,
execution, SSH, NETCONF, RESTCONF, live-device access, provider/API/model
calls, secrets handling, frontend API integration, backup, VRRP execution,
device mutation, approval bypass, or safety-gate behavior changes.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES


PHASE = "2B-06"
TASK_NAME = "phase2b-06-implementation-entry-gate-and-first-slice-readiness-review"
TITLE = "Phase 2B-06 Implementation Entry Gate and First-Slice Readiness Review"
MODE = "planning_only_implementation_entry_gate"
SCOPE = "phase_wide_phase_2b_implementation_entry_gate_and_first_slice_readiness_review"
STATUS = "PASS"
FINAL_VERDICT = "GO_TO_DEFINE_FIRST_SLICE_PLANNING_ONLY"
BLOCKED_VERDICT = "NO_GO_NEEDS_MORE_PLANNING"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md"

PHASE_GOAL = (
    "Create an implementation entry gate that consolidates Phase 2B-00 through "
    "Phase 2B-05 and determines whether the project is ready to enter the first "
    "safe implementation slice definition step."
)

IMPLEMENTATION_BOUNDARY = (
    "planning-only implementation entry gate",
    "readiness review only",
    "future first-slice definition may be planned next",
    "no first-slice implementation",
    "no runner, adapter, broker, scheduler, queue worker, or execution engine",
    "no SSH, NETCONF, RESTCONF, live-device access, or real-device access",
    "no provider, API, model, cloud, or external AI runtime calls",
    "no secrets handling",
    "no frontend API integration",
    "no real backup, real configuration change, or real VRRP execution",
    "no second safety matrix",
)

PRIOR_PHASE_2B_ARTIFACTS = (
    {
        "phase": "Phase 2B-00",
        "artifact": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "contribution": "Establishes the authorization and scope gate baseline and keeps Phase 2B implementation locked.",
    },
    {
        "phase": "Phase 2B-00A",
        "artifact": "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "contribution": "Records owner authorization for Phase 2B planning-only scope work and denies implementation.",
    },
    {
        "phase": "Phase 2B-01",
        "artifact": "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "contribution": "Defines phase-wide planning scope, examples-only job types, forbidden scope, and stop conditions.",
    },
    {
        "phase": "Phase 2B-02",
        "artifact": "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "contribution": "Defines planning-only safety gate categories, evidence requirements, failure conditions, and stop conditions.",
    },
    {
        "phase": "Phase 2B-03",
        "artifact": "Phase 2B-03 scope confirmation before implementation",
        "contribution": "Required scope-confirmation concept; current repository evidence does not include a concrete Phase 2B-03 source/doc/test path, so Phase 2B-06 records the reference without inventing a missing artifact.",
    },
    {
        "phase": "Phase 2B-04",
        "artifact": "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "contribution": "Provides the existing safety artifact crosswalk and gap review that Phase 2B-06 references instead of recreating.",
    },
    {
        "phase": "Phase 2B-05",
        "artifact": "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "contribution": "Controls safety de-duplication and prohibits second, parallel, renamed, or replacement safety matrices.",
    },
)

ENTRY_CONDITIONS = (
    {
        "category": "scope remains phase-wide",
        "condition": "The future first-slice planning artifact must keep Phase 2B phase-wide and treat job types as examples only.",
        "status": "PASS",
    },
    {
        "category": "safety gates are reused, not duplicated",
        "condition": "Phase 2B-05 controls de-duplication; future work must cite existing gates before adding anything new.",
        "status": "PASS",
    },
    {
        "category": "implementation slice is minimal and reversible",
        "condition": "A future slice definition may describe only a smallest reversible planning target with explicit stop and rollback criteria.",
        "status": "PASS",
    },
    {
        "category": "no runner / adapter / execution is enabled during this task",
        "condition": "Phase 2B-06 does not add or enable execution surfaces.",
        "status": "PASS",
    },
    {
        "category": "no provider / API / model calls are enabled",
        "condition": "Phase 2B-06 remains local and deterministic with provider/API/model paths disabled.",
        "status": "PASS",
    },
    {
        "category": "no live-device access is introduced",
        "condition": "No SSH, NETCONF, RESTCONF, live-device, or real-device path is introduced.",
        "status": "PASS",
    },
    {
        "category": "first slice has clear non-execution boundaries",
        "condition": "The future slice definition must prove rejected and planning-only flows do not reach adapters, brokers, runners, queues, workers, subprocesses, network clients, or execution paths.",
        "status": "PASS",
    },
    {
        "category": "first slice has evidence and report expectations",
        "condition": "The future slice definition must name expected reviewer evidence, report-index visibility, and validation commands before code exists.",
        "status": "PASS",
    },
    {
        "category": "first slice has rollback / stop conditions",
        "condition": "The future slice definition must include stop conditions for scope narrowing, duplicated safety design, forbidden capability enablement, or missing non-execution proof.",
        "status": "PASS",
    },
    {
        "category": "first slice has explicit Go / No-Go criteria",
        "condition": "The future slice definition must end with Go / No-Go planning criteria and must not authorize implementation directly.",
        "status": "PASS",
    },
)

FIRST_SLICE_READINESS_DEFINITION = {
    "purpose": "Define a future first implementation slice planning artifact only; do not implement the slice.",
    "minimum_inputs": (
        "Phase 2B-00 through Phase 2B-05 artifacts",
        "AGENTS.md safety rules",
        "phase-wide scope confirmation",
        "example job types treated as examples only",
        "forbidden capability inventory",
    ),
    "minimum_outputs": (
        "future first-slice planning artifact",
        "non-execution proof expectations",
        "reviewer evidence expectations",
        "validation expectations",
        "rollback and stop conditions",
        "Go / No-Go planning verdict",
    ),
    "safety_preconditions": (
        "reuse existing safety gates",
        "do not duplicate Phase 2B-05 de-duplication controls",
        "keep provider/API/model/live-device/execution paths disabled",
        "keep scope phase-wide",
    ),
    "non_execution_proof": (
        "runner_enabled remains false",
        "adapter_enabled remains false",
        "execution_path_implemented remains false",
        "provider_api_model_calls_enabled remains false",
        "live_device_access_enabled remains false",
    ),
    "expected_report_evidence": (
        "planning artifact path",
        "task catalog/report-index visibility",
        "machine-readable safety flags",
        "tests proving no execution path is reached",
    ),
    "stop_conditions": (
        "scope narrows to one job type",
        "a second safety matrix is created",
        "implementation begins under a planning label",
        "any forbidden capability is enabled",
        "non-execution proof is missing",
    ),
    "validation_expectations": (
        "dedicated Phase 2B-06 tests",
        "future first-slice planning tests before implementation",
        "python -m pytest when practical",
        "python network_lab.py --report-index or report-index equivalent",
    ),
}

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "first_slice_definition_allowed_next_planning_only": True,
    "first_slice_implemented": False,
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
    "frontend_api_integration_enabled": False,
    "real_backup_enabled": False,
    "real_configuration_change_enabled": False,
    "real_vrrp_execution_enabled": False,
    "device_mutation_enabled": False,
    "approval_bypass_enabled": False,
    "safety_gate_weakening_enabled": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_06_IMPLEMENTATION_ENTRY_GATE_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "PHASE_2B_05_CONTROLS_SAFETY_DEDUPLICATION",
    "SECOND_SAFETY_MATRIX_CREATED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE",
    "PROVIDER_API_MODEL_CALLS_ENABLED_FALSE",
    "LIVE_DEVICE_ACCESS_ENABLED_FALSE",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_06": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _prior_artifacts() -> Tuple[Dict[str, str], ...]:
    return tuple(deepcopy(item) for item in PRIOR_PHASE_2B_ARTIFACTS)


def validate_phase_2b_06_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    prior = report.get("phase_2b_00_through_05_consolidation", [])
    prior_phases = {str(item.get("phase")) for item in prior if isinstance(item, Mapping)}
    if prior_phases != {
        "Phase 2B-00",
        "Phase 2B-00A",
        "Phase 2B-01",
        "Phase 2B-02",
        "Phase 2B-03",
        "Phase 2B-04",
        "Phase 2B-05",
    }:
        errors.append("PHASE_2B_00_THROUGH_05_CONSOLIDATION_MISMATCH")
    if report.get("phase_2b_05_controls_safety_deduplication") is not True:
        errors.append("PHASE_2B_05_DEDUP_CONTROL_NOT_TRUE")
    if report.get("safety_matrix_policy") != "do_not_create_second_safety_matrix":
        errors.append("SAFETY_MATRIX_POLICY_MISMATCH")

    conditions = report.get("implementation_entry_conditions", [])
    condition_categories = {str(item.get("category")) for item in conditions if isinstance(item, Mapping)}
    expected_categories = {item["category"] for item in ENTRY_CONDITIONS}
    if condition_categories != expected_categories:
        errors.append("ENTRY_CONDITION_CATEGORY_MISMATCH")
    if any(item.get("status") != "PASS" for item in conditions if isinstance(item, Mapping)):
        errors.append("ENTRY_CONDITION_NOT_PASS")

    readiness = report.get("first_slice_readiness_definition", {})
    if not isinstance(readiness, Mapping):
        errors.append("FIRST_SLICE_READINESS_DEFINITION_NOT_OBJECT")
        readiness = {}
    for key in FIRST_SLICE_READINESS_DEFINITION:
        if key not in readiness:
            errors.append(f"FIRST_SLICE_READINESS_DEFINITION_MISSING:{key}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "FIRST_SLICE_DEFINITION_ALLOWED_NEXT_PLANNING_ONLY": "YES",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
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
        "prior_phase_2b_artifacts_checked": len(prior_phases),
        "entry_conditions_checked": len(condition_categories),
        "readiness_fields_checked": len(readiness),
    }


def build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report() -> Dict[str, Any]:
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
            "existing_artifacts_to_reference": [
                item["artifact"] for item in PRIOR_PHASE_2B_ARTIFACTS
            ],
            "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_CAPABILITIES),
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "phase_2b_00_through_05_consolidation": list(_prior_artifacts()),
        "phase_2b_05_controls_safety_deduplication": True,
        "safety_matrix_policy": "do_not_create_second_safety_matrix",
        "implementation_entry_conditions": list(deepcopy(ENTRY_CONDITIONS)),
        "first_slice_readiness_definition": deepcopy(FIRST_SLICE_READINESS_DEFINITION),
        "go_no_go_verdict": FINAL_VERDICT,
        "verdict_explanation": (
            "Phase 2B-06 is ready to define the next planning artifact for a future first safe "
            "implementation slice because Phase 2B-00 through Phase 2B-05 provide authorization, "
            "scope, safety gate, crosswalk, and de-duplication controls. This verdict does not "
            "authorize implementation directly."
        ),
        "explicit_non_implementation_statement": (
            "No runner implemented. No adapter implemented. No execution path implemented. "
            "No provider/API/model calls enabled. No live-device access enabled. "
            "No second safety matrix created. No Phase 2B implementation slice implemented."
        ),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "FIRST_SLICE_DEFINITION_ALLOWED_NEXT_PLANNING_ONLY": "YES",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
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
            "second_safety_matrix_created": False,
            "first_slice_implemented": False,
            "runner_adapter_execution_enabled": False,
            "provider_api_model_calls_enabled": False,
            "live_device_access_enabled": False,
            "go_no_go_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_06_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = BLOCKED_VERDICT
        report["go_no_go_verdict"] = BLOCKED_VERDICT
        report["summary"]["go_no_go_verdict"] = BLOCKED_VERDICT
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
    readiness = report["first_slice_readiness_definition"]
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
  <p>Go / No-Go verdict: <strong>{html.escape(str(report["go_no_go_verdict"]))}</strong></p>
  <p>{html.escape(str(report["verdict_explanation"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Phase 2B-00 Through Phase 2B-05 Consolidation</h2>
  <table>
    <thead><tr><th>Phase</th><th>Artifact</th><th>Contribution</th></tr></thead>
    <tbody>{_table_rows(report["phase_2b_00_through_05_consolidation"], ("phase", "artifact", "contribution"))}</tbody>
  </table>
  <h2>Implementation Entry Conditions</h2>
  <table>
    <thead><tr><th>Category</th><th>Condition</th><th>Status</th></tr></thead>
    <tbody>{_table_rows(report["implementation_entry_conditions"], ("category", "condition", "status"))}</tbody>
  </table>
  <h2>First-Slice Readiness Definition</h2>
  <table><tbody>{_dict_rows(readiness)}</tbody></table>
  <h2>Explicit Non-Implementation Statement</h2>
  <p>{html.escape(str(report["explicit_non_implementation_statement"]))}</p>
  <h2>Forbidden Capability Review</h2>
  <table>
    <thead><tr><th>Capability</th><th>Enabled</th><th>Allowed by Phase 2B-06</th><th>Status</th></tr></thead>
    <tbody>{_table_rows(report["forbidden_capability_review"], ("capability", "enabled", "allowed_by_phase_2b_06", "status"))}</tbody>
  </table>
  <h2>Completion Markers</h2>
  <ul>{_list_items(report["completion_markers"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    json_path, html_path = write_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_reports(
        project_root,
        report,
    )
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
    print(f"phase_2b_05_controls_safety_deduplication: {str(report['phase_2b_05_controls_safety_deduplication']).lower()}")
    print(f"second_safety_matrix_created: {str(report['second_safety_matrix_created']).lower()}")
    print(f"first_slice_implemented: {str(report['first_slice_implemented']).lower()}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"execution_path_implemented: {str(report['execution_path_implemented']).lower()}")
    print(f"provider_api_model_calls_enabled: {str(report['provider_api_model_calls_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"Entry conditions checked: {report['validation']['entry_conditions_checked']}")
    print(f"Readiness fields checked: {report['validation']['readiness_fields_checked']}")
    print(f"Go / No-Go verdict: {report['go_no_go_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['go_no_go_verdict']}")
    return 0 if report["status"] == "PASS" else 1
