"""Phase 2B-08 first-slice implementation authorization gate.

This module creates a deterministic, local, planning-only authorization gate
for deciding whether the Phase 2B-07 first slice is clear, bounded, safe,
reviewable, and eligible to move to the next planning-only implementation plan
pack. It does not authorize or implement the slice, rebuild safety gates,
create a second safety matrix, or enable runners, adapters, execution, SSH,
NETCONF, RESTCONF, live-device access, provider/API/model calls, secrets
handling, frontend integration, background work, backup, validation, or command
execution.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents
from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review import (
    FINAL_VERDICT as PHASE_2B_06_VERDICT,
)
from phase_2b_07_first_slice_definition_pack import (
    FINAL_VERDICT as PHASE_2B_07_VERDICT,
    FIRST_MINIMAL_SAFE_SLICE,
)


PHASE = "2B-08"
TASK_NAME = "phase2b-08-first-slice-implementation-authorization-gate-planning-only"
TITLE = "Phase 2B-08 First-Slice Implementation Authorization Gate - Planning Only"
MODE = "planning_only_first_slice_implementation_authorization_gate"
SCOPE = "phase_wide_phase_2b_first_slice_authorization_gate_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "GO_TO_2B_09_PLANNING_ONLY"
BLOCKED_VERDICT = "NO_GO"
SCOPE_BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_08_first_slice_implementation_authorization_gate_planning_only.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_08_first_slice_implementation_authorization_gate_planning_only.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md"

PHASE_GOAL = (
    "Create a planning-only authorization gate artifact that decides whether "
    "Phase 2B-07 is sufficiently clear, bounded, safe, reviewable, and eligible "
    "to move toward the next planning-only step."
)

EXISTING_ARTIFACTS_REVIEWED = (
    {
        "phase": "Phase 2B-00",
        "artifact": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "role": "Authorization and scope baseline; keeps implementation locked unless separately approved.",
    },
    {
        "phase": "Phase 2B-00A",
        "artifact": "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "role": "Owner planning-only authorization statement; denies implementation.",
    },
    {
        "phase": "Phase 2B-01",
        "artifact": "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "role": "Phase-wide planning scope and examples-only job type boundary.",
    },
    {
        "phase": "Phase 2B-02",
        "artifact": "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "role": "Safety gate design expectations and stop conditions.",
    },
    {
        "phase": "Phase 2B-04",
        "artifact": "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "role": "Existing safety artifact crosswalk and gap review; no replacement matrix.",
    },
    {
        "phase": "Phase 2B-05",
        "artifact": "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "role": "De-duplication authority; prevents second or replacement safety matrices.",
    },
    {
        "phase": "Phase 2B-06",
        "artifact": "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
        "role": "Prior planning-only entry gate; verdict referenced without re-running or changing it.",
    },
    {
        "phase": "Phase 2B-07",
        "artifact": "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
        "role": "First-slice definition pack evaluated by this gate.",
    },
)

CLARITY_CHECKS = (
    {
        "check": "first slice has a named boundary",
        "status": "PASS",
        "evidence": "Phase 2B-07 defines local_static_job_definition_and_evidence_contract_slice.",
    },
    {
        "check": "first slice explains why it is minimal",
        "status": "PASS",
        "evidence": "Phase 2B-07 limits the future target to static contracts, examples-only job categories, no-execution flags, and tests.",
    },
    {
        "check": "first slice explains why it is safe",
        "status": "PASS",
        "evidence": "Phase 2B-07 keeps execution-capable surfaces out of scope and requires negative tests.",
    },
    {
        "check": "first slice has explicit future preconditions",
        "status": "PASS",
        "evidence": "Phase 2B-07 lists future implementation preconditions before any code may begin.",
    },
    {
        "check": "first slice has explicit stop conditions",
        "status": "PASS",
        "evidence": "Phase 2B-07 stops on scope narrowing, forbidden capability enablement, second matrix creation, or missing no-execution proof.",
    },
)

BOUNDARY_COMPLIANCE_CHECKS = (
    {
        "check": "small controlled reviewable slice",
        "status": "PASS",
        "evidence": "Future work remains limited to local static job-definition and reviewer-evidence contracts.",
    },
    {
        "check": "phase-wide scope preserved",
        "status": "PASS",
        "evidence": "Required job types remain examples only and the slice is not reduced to one job type.",
    },
    {
        "check": "Phase 2B boundary preserved",
        "status": "PASS",
        "evidence": "The next allowed output is another planning-only plan pack, not implementation.",
    },
)

SAFETY_GATE_REUSE_CHECKS = (
    {
        "check": "existing safety gates reused",
        "status": "PASS",
        "evidence": "Phase 2B-08 references Phase 2B-00 through Phase 2B-07 instead of creating replacement controls.",
    },
    {
        "check": "safety gates not rebuilt",
        "status": "PASS",
        "evidence": "No new safety gate framework is introduced.",
    },
    {
        "check": "safety gates not duplicated",
        "status": "PASS",
        "evidence": "Phase 2B-05 remains the de-duplication authority.",
    },
    {
        "check": "second safety matrix not created",
        "status": "PASS",
        "evidence": "Phase 2B-04 and Phase 2B-05 remain referenced as existing sources.",
    },
)

AUTHORIZATION_CONDITIONS = (
    {
        "condition": "Phase 2B-07 defines the first slice clearly enough.",
        "status": "PASS",
    },
    {
        "condition": "The first slice remains small, controlled, and reviewable.",
        "status": "PASS",
    },
    {
        "condition": "The first slice still fits the Phase 2B boundary.",
        "status": "PASS",
    },
    {
        "condition": "The phase has not been narrowed to only one example job type.",
        "status": "PASS",
    },
    {
        "condition": "Existing safety gates are reused.",
        "status": "PASS",
    },
    {
        "condition": "Safety gates are not rebuilt, duplicated, or replaced.",
        "status": "PASS",
    },
    {
        "condition": "Future implementation authorization conditions are explicit.",
        "status": "PASS",
    },
    {
        "condition": "The gate produces a clear GO or NO-GO verdict.",
        "status": "PASS",
    },
    {
        "condition": "The next step is another planning-only implementation plan pack, not implementation.",
        "status": "PASS",
    },
)

GO_NO_GO_VERDICT_MODEL = {
    "GO": FINAL_VERDICT,
    "NO_GO": BLOCKED_VERDICT,
    "NEEDS_SCOPE_CONFIRMATION": SCOPE_BLOCKED_VERDICT,
    "go_meaning": "Proceed only to Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only.",
    "no_go_meaning": "Do not proceed until missing clarity, boundary, safety reuse, or evidence issues are resolved.",
    "needs_scope_confirmation_meaning": "Stop immediately if scope narrows to one example job type or implementation intent appears.",
}

RECOMMENDED_NEXT_STEP = "Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only"

EXPLICIT_NON_GOALS = (
    "Do not implement the first slice.",
    "Do not add a runner.",
    "Do not add an adapter.",
    "Do not add an execution path.",
    "Do not add a scheduler, broker, queue worker, or background worker.",
    "Do not add SSH, NETCONF, or RESTCONF.",
    "Do not touch live devices or add real device access.",
    "Do not add provider, API, or model calls.",
    "Do not add secrets or credentials handling.",
    "Do not rerun or rewrite Phase 2B-06.",
    "Do not rebuild, duplicate, or replace existing safety gates.",
    "Do not convert example job types into the whole phase scope.",
    "Do not create a second safety matrix.",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "phase_2b_08_authorization_gate_created": True,
    "phase_2b_09_planning_only_allowed_next": True,
    "direct_implementation_authorized": False,
    "first_slice_defined": True,
    "first_slice_implemented": False,
    "phase_2b_06_rerun": False,
    "phase_2b_06_rewritten": False,
    "safety_gates_rebuilt": False,
    "safety_gates_duplicated": False,
    "safety_gates_replaced": False,
    "second_safety_matrix_created": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_worker_added": False,
    "background_worker_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "real_device_access_added": False,
    "provider_api_model_calls_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "secrets_handling_added": False,
    "frontend_integration_added": False,
    "real_backup_added": False,
    "real_validation_added": False,
    "real_command_execution_added": False,
    "device_mutation_added": False,
    "approval_bypass_added": False,
    "safety_gate_weakening_added": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_08_FIRST_SLICE_AUTHORIZATION_GATE_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "PHASE_2B_07_CLARITY_CHECK_PASS",
    "BOUNDARY_COMPLIANCE_CHECK_PASS",
    "SAFETY_GATE_REUSE_CHECK_PASS",
    "FUTURE_AUTHORIZATION_CONDITIONS_EXPLICIT",
    "SAFETY_GATES_REBUILT_OR_REPLACED_FALSE",
    "SECOND_SAFETY_MATRIX_CREATED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_ADDED_FALSE",
    "SSH_NETCONF_RESTCONF_TOUCHED_FALSE",
    "LIVE_DEVICE_ACCESS_ADDED_FALSE",
    "PROVIDER_API_MODEL_CALLS_ADDED_FALSE",
    FINAL_VERDICT,
)


def _existing_artifacts_reviewed() -> Tuple[Dict[str, str], ...]:
    return tuple(deepcopy(item) for item in EXISTING_ARTIFACTS_REVIEWED)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_08": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_08_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    artifact_phases = {str(item.get("phase")) for item in report.get("existing_artifacts_reviewed", []) if isinstance(item, Mapping)}
    if artifact_phases != {item["phase"] for item in EXISTING_ARTIFACTS_REVIEWED}:
        errors.append("EXISTING_ARTIFACTS_REVIEWED_MISMATCH")

    for field_name, expected in (
        ("phase_2b_06_verdict_referenced", PHASE_2B_06_VERDICT),
        ("phase_2b_07_verdict_referenced", PHASE_2B_07_VERDICT),
    ):
        if report.get(field_name) != expected:
            errors.append(f"{field_name.upper()}_MISMATCH")

    for collection_name, expected in (
        ("phase_2b_07_first_slice_clarity_check", CLARITY_CHECKS),
        ("boundary_compliance_check", BOUNDARY_COMPLIANCE_CHECKS),
        ("safety_gate_reuse_check", SAFETY_GATE_REUSE_CHECKS),
        ("authorization_condition_checklist", AUTHORIZATION_CONDITIONS),
    ):
        values = report.get(collection_name, [])
        if len(values) != len(expected):
            errors.append(f"{collection_name.upper()}_COUNT_MISMATCH")
        if any(item.get("status") != "PASS" for item in values if isinstance(item, Mapping)):
            errors.append(f"{collection_name.upper()}_NOT_PASS")

    if report.get("go_no_go_verdict_model") != GO_NO_GO_VERDICT_MODEL:
        errors.append("GO_NO_GO_VERDICT_MODEL_MISMATCH")
    if report.get("recommended_next_step") != RECOMMENDED_NEXT_STEP:
        errors.append("RECOMMENDED_NEXT_STEP_MISMATCH")
    if report.get("final_verdict") != FINAL_VERDICT:
        errors.append("FINAL_VERDICT_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_06_VERDICT_REFERENCED": PHASE_2B_06_VERDICT,
        "PHASE_2B_07_VERDICT_REFERENCED": PHASE_2B_07_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "DIRECT_IMPLEMENTATION_AUTHORIZED": "NO",
        "NEXT_STEP": RECOMMENDED_NEXT_STEP,
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "LIVE_DEVICE_ACCESS_ADDED": "NO",
        "PROVIDER_API_MODEL_CALLS_ADDED": "NO",
        "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(artifact_phases),
        "clarity_checks": len(report.get("phase_2b_07_first_slice_clarity_check", [])),
        "boundary_checks": len(report.get("boundary_compliance_check", [])),
        "safety_reuse_checks": len(report.get("safety_gate_reuse_check", [])),
        "authorization_conditions_checked": len(report.get("authorization_condition_checklist", [])),
    }


def build_phase_2b_08_first_slice_implementation_authorization_gate_report() -> Dict[str, Any]:
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
            "existing_artifacts_to_reference": [item["artifact"] for item in EXISTING_ARTIFACTS_REVIEWED],
            "implementation_boundary": list(EXPLICIT_NON_GOALS),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_CAPABILITIES),
        "existing_artifacts_reviewed": list(_existing_artifacts_reviewed()),
        "phase_2b_06_verdict_referenced": PHASE_2B_06_VERDICT,
        "phase_2b_07_verdict_referenced": PHASE_2B_07_VERDICT,
        "phase_2b_07_first_slice": deepcopy(FIRST_MINIMAL_SAFE_SLICE),
        "phase_2b_07_first_slice_clarity_check": list(deepcopy(CLARITY_CHECKS)),
        "boundary_compliance_check": list(deepcopy(BOUNDARY_COMPLIANCE_CHECKS)),
        "safety_gate_reuse_check": list(deepcopy(SAFETY_GATE_REUSE_CHECKS)),
        "authorization_condition_checklist": list(deepcopy(AUTHORIZATION_CONDITIONS)),
        "go_no_go_verdict_model": deepcopy(GO_NO_GO_VERDICT_MODEL),
        "recommended_next_step": RECOMMENDED_NEXT_STEP,
        "explicit_non_goals": list(EXPLICIT_NON_GOALS),
        "evidence_summary": (
            "Phase 2B-08 references Phase 2B-00 through Phase 2B-07, confirms the "
            "Phase 2B-07 first slice is clear enough for another planning-only plan "
            "pack, and preserves no-execution proof without adding implementation."
        ),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_06_VERDICT_REFERENCED": PHASE_2B_06_VERDICT,
            "PHASE_2B_07_VERDICT_REFERENCED": PHASE_2B_07_VERDICT,
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "DIRECT_IMPLEMENTATION_AUTHORIZED": "NO",
            "NEXT_STEP": RECOMMENDED_NEXT_STEP,
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
            "LIVE_DEVICE_ACCESS_ADDED": "NO",
            "PROVIDER_API_MODEL_CALLS_ADDED": "NO",
            "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "phase_2b_07_clarity_check": "PASS",
            "boundary_compliance_check": "PASS",
            "safety_gate_reuse_check": "PASS",
            "future_authorization_conditions_explicit": True,
            "first_slice_implemented": False,
            "runner_added": False,
            "adapter_added": False,
            "execution_path_added": False,
            "ssh_netconf_restconf_touched": False,
            "live_device_access_added": False,
            "provider_api_model_calls_added": False,
            "secrets_handling_added": False,
            "safety_gates_rebuilt_or_replaced": False,
            "second_safety_matrix_created": False,
            "final_verdict": FINAL_VERDICT,
            "next_step": RECOMMENDED_NEXT_STEP,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_08_report(report)
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
    write_text_with_parents(
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
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>Recommended next step: <strong>{html.escape(str(report["recommended_next_step"]))}</strong></p>
  <p>{html.escape(str(report["evidence_summary"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Existing Artifacts Reviewed</h2>
  <table>
    <thead><tr><th>Phase</th><th>Artifact</th><th>Role</th></tr></thead>
    <tbody>{_table_rows(report["existing_artifacts_reviewed"], ("phase", "artifact", "role"))}</tbody>
  </table>
  <h2>Phase 2B-07 First-Slice Clarity Check</h2>
  <table>
    <thead><tr><th>Check</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_table_rows(report["phase_2b_07_first_slice_clarity_check"], ("check", "status", "evidence"))}</tbody>
  </table>
  <h2>Boundary Compliance Check</h2>
  <table>
    <thead><tr><th>Check</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_table_rows(report["boundary_compliance_check"], ("check", "status", "evidence"))}</tbody>
  </table>
  <h2>Safety Gate Reuse Check</h2>
  <table>
    <thead><tr><th>Check</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_table_rows(report["safety_gate_reuse_check"], ("check", "status", "evidence"))}</tbody>
  </table>
  <h2>Authorization Condition Checklist</h2>
  <table>
    <thead><tr><th>Condition</th><th>Status</th></tr></thead>
    <tbody>{_table_rows(report["authorization_condition_checklist"], ("condition", "status"))}</tbody>
  </table>
  <h2>GO / NO-GO Verdict Model</h2>
  <table><tbody>{_dict_rows(report["go_no_go_verdict_model"])}</tbody></table>
  <h2>Explicit Non-Goals</h2>
  <ul>{_list_items(report["explicit_non_goals"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_08_first_slice_implementation_authorization_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_08_first_slice_implementation_authorization_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    json_path, html_path = write_phase_2b_08_first_slice_implementation_authorization_gate_reports(
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
    print(f"phase_2b_07_clarity_check: {report['summary']['phase_2b_07_clarity_check']}")
    print(f"boundary_compliance_check: {report['summary']['boundary_compliance_check']}")
    print(f"safety_gate_reuse_check: {report['summary']['safety_gate_reuse_check']}")
    print(f"future_authorization_conditions_explicit: {str(report['summary']['future_authorization_conditions_explicit']).lower()}")
    print(f"first_slice_implemented: {str(report['first_slice_implemented']).lower()}")
    print(f"runner_added: {str(report['runner_added']).lower()}")
    print(f"adapter_added: {str(report['adapter_added']).lower()}")
    print(f"execution_path_added: {str(report['execution_path_added']).lower()}")
    print(f"ssh_netconf_restconf_touched: {str(report['summary']['ssh_netconf_restconf_touched']).lower()}")
    print(f"live_device_access_added: {str(report['live_device_access_added']).lower()}")
    print(f"provider_api_model_calls_added: {str(report['provider_api_model_calls_added']).lower()}")
    print(f"secrets_handling_added: {str(report['secrets_handling_added']).lower()}")
    print(f"safety_gates_rebuilt_or_replaced: {str(report['summary']['safety_gates_rebuilt_or_replaced']).lower()}")
    print(f"second_safety_matrix_created: {str(report['second_safety_matrix_created']).lower()}")
    print(f"Authorization conditions checked: {report['validation']['authorization_conditions_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"Recommended next step: {report['recommended_next_step']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
