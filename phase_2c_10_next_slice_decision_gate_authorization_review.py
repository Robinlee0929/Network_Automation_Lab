"""Phase 2C-10 next-slice decision gate / authorization review.

This module creates deterministic, local, planning-only authorization review
evidence for deciding whether another planning-only candidate inventory phase
may begin after Phase 2C-09 accepted the Phase 2C-08
`artifact_validation_job`. It does not list candidates, select a next slice,
authorize implementation, or open runners, adapters, brokers, schedulers,
queues, workers, agent loops, SSH, NETCONF, RESTCONF, live devices, providers,
APIs, models, secrets, backup behavior, or configuration-change behavior.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_03_next_slice_decision_gate_authorization_review import (
    FINAL_VERDICT as PHASE_2C_03_VERDICT,
    REPORT_JSON as PHASE_2C_03_REPORT_JSON,
    TASK_NAME as PHASE_2C_03_TASK_NAME,
)
from phase_2c_04_next_slice_candidate_inventory import (
    FINAL_VERDICT as PHASE_2C_04_VERDICT,
    TASK_NAME as PHASE_2C_04_TASK_NAME,
)
from phase_2c_05_next_slice_safety_delta_review import (
    FINAL_VERDICT as PHASE_2C_05_VERDICT,
    TASK_NAME as PHASE_2C_05_TASK_NAME,
)
from phase_2c_06_next_slice_final_selection_gate import (
    FINAL_VERDICT as PHASE_2C_06_VERDICT,
    TASK_NAME as PHASE_2C_06_TASK_NAME,
)
from phase_2c_07_next_slice_implementation_kickoff_gate import (
    FINAL_VERDICT as PHASE_2C_07_VERDICT,
    TASK_NAME as PHASE_2C_07_TASK_NAME,
)
from phase_2c_08_next_slice_implementation import (
    FINAL_VERDICT as PHASE_2C_08_VERDICT,
    REPORT_JSON as PHASE_2C_08_REPORT_JSON,
    TASK_NAME as PHASE_2C_08_TASK_NAME,
)
from phase_2c_09_post_next_slice_acceptance_review import (
    DOC_PATH as PHASE_2C_09_DOC_PATH,
    FINAL_VERDICT as PHASE_2C_09_VERDICT,
    REPORT_JSON as PHASE_2C_09_REPORT_JSON,
    TASK_NAME as PHASE_2C_09_TASK_NAME,
    build_phase_2c_09_post_next_slice_acceptance_review_report,
    validate_phase_2c_09_report,
)


PHASE = "2C-10"
TASK_NAME = "phase2c-10-next-slice-decision-gate-authorization-review"
TITLE = "Phase 2C-10 Next-Slice Decision Gate / Authorization Review - Planning Only"
MODE = "planning_only_next_slice_decision_gate_authorization_review"
SCOPE = "phase_wide_next_planning_authorization_review_after_phase_2c_09_acceptance"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_10_NEXT_PLANNING_ALLOWED_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "PHASE_2C_09_ACCEPTANCE_NOT_CONFIRMED"
NEEDS_SCOPE_CONFIRMATION_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_10_next_slice_decision_gate_authorization_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_10_next_slice_decision_gate_authorization_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_10_next_slice_decision_gate_authorization_review.md"
PHASE_2C_09_SOURCE_PATH = Path("phase_2c_09_post_next_slice_acceptance_review.py")

NEXT_ALLOWED_PHASE = "Phase 2C-11 Next-Slice Candidate Inventory - Planning Only"

PHASE_GOAL = (
    "After Phase 2C-09 acceptance review is complete and accepted, decide only "
    "whether the project may enter the next planning-only candidate inventory "
    "phase. This phase must not select the next slice, list the next-slice "
    "candidate inventory, or start implementation."
)

EXAMPLE_JOB_TYPES_SECTION = (
    "Example job types are out of scope for selection in Phase 2C-10. "
    "Any concrete next-slice candidate inventory is deferred to Phase 2C-11. "
    "Historical examples from previous artifacts may be referenced only as "
    "context and must not be ranked, selected, expanded, or authorized here."
)

NON_DUPLICATION_PHASE_2C_03 = (
    "Phase 2C-03 was the first next-slice decision gate after Phase 2C-02 / "
    "local_static_job acceptance. Phase 2C-10 is the second next-slice decision "
    "gate after Phase 2C-09 / artifact_validation_job acceptance. The gate "
    "pattern is reused, but the input acceptance point and planning cycle are "
    "different."
)

NON_DUPLICATION_DAY1_DAY160 = (
    "Day1-Day160 may be referenced only as historical project context. "
    "Phase 2C-10 does not rewrite, replace, regenerate, or extend Day1-Day160."
)

FORBIDDEN_SCOPE = (
    "Phase 2C-11 start",
    "next-slice candidate inventory",
    "next-slice selection",
    "implementation authorization",
    "Phase 2C-15 start",
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
    "config backup behavior",
    "config change behavior",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
)

EXISTING_ARTIFACTS_REVIEWED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_08_next_slice_implementation.md",
    "phase_2c_08_next_slice_implementation.py",
    "tests/test_phase_2c_08_next_slice_implementation.py",
    PHASE_2C_08_REPORT_JSON.as_posix(),
    "docs/phase_2c/phase_2c_09_post_next_slice_acceptance_review.md",
    "phase_2c_09_post_next_slice_acceptance_review.py",
    "tests/test_phase_2c_09_post_next_slice_acceptance_review.py",
    PHASE_2C_09_REPORT_JSON.as_posix(),
    "docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "tests/test_phase_2c_03_next_slice_decision_gate_authorization_review.py",
    PHASE_2C_03_REPORT_JSON.as_posix(),
    "docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md",
    "docs/phase_2c/phase_2c_07_next_slice_implementation_kickoff_gate.md",
    "phase_2c_04_next_slice_candidate_inventory.py",
    "phase_2c_05_next_slice_safety_delta_review.py",
    "phase_2c_06_next_slice_final_selection_gate.py",
    "phase_2c_07_next_slice_implementation_kickoff_gate.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: create Phase 2C-10 planning-only authorization review evidence, "
    "register a report-only task through existing registry and CLI patterns, "
    "and add tests proving the decision allows only Phase 2C-11 planning. Not "
    "allowed: starting Phase 2C-11, listing or selecting candidates, "
    "authorizing implementation, adding runner/adapter/execution paths, adding "
    "scheduler/queue/broker/worker/agent-loop behavior, touching live devices, "
    "SSH, NETCONF, RESTCONF, provider/API/model/secrets, config backup/change "
    "behavior, rewriting Day1-Day160, or creating a second safety matrix."
)

DECISION_CRITERIA = (
    {
        "check": "Phase 2C-09 acceptance review is found and accepted",
        "expected": "ACCEPT",
        "status": "PASS",
    },
    {
        "check": "Only the next planning-only candidate inventory phase may begin",
        "expected": "ALLOW_NEXT_PLANNING: YES",
        "status": "PASS",
    },
    {
        "check": "Candidate inventory remains deferred",
        "expected": "NEXT_SLICE_CANDIDATES_LISTED: NO",
        "status": "PASS",
    },
    {
        "check": "No next slice is selected",
        "expected": "NEXT_SLICE_SELECTED: NO",
        "status": "PASS",
    },
    {
        "check": "No implementation is authorized or started",
        "expected": "NEXT_IMPLEMENTATION_AUTHORIZED: NO and NEXT_IMPLEMENTATION_STARTED: NO",
        "status": "PASS",
    },
    {
        "check": "Gate pattern reuse is distinct from Phase 2C-03",
        "expected": "DUPLICATES_PHASE_2C_03: PATTERN_REUSE_ONLY",
        "status": "PASS",
    },
    {
        "check": "Day1-Day160 remains historical reference only",
        "expected": "DUPLICATES_DAY1_DAY160: REFERENCE_ONLY",
        "status": "PASS",
    },
)

SAFETY_FLAGS = {
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "needs_scope_confirmation": False,
    "phase_2c_09_acceptance_confirmed": True,
    "allow_next_planning": True,
    "phase_2c_11_started": False,
    "next_slice_candidates_listed": False,
    "next_slice_selected": False,
    "next_implementation_authorized": False,
    "next_implementation_started": False,
    "runner_added": False,
    "adapter_added": False,
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
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_10_NEXT_SLICE_DECISION_GATE_AUTHORIZATION_REVIEW_PLANNING_ONLY",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "PHASE_2C_09_ACCEPTANCE_CONFIRMED_YES",
    "PHASE_2C_09_DECISION_ACCEPT",
    "ALLOW_NEXT_PLANNING_YES",
    "NEXT_ALLOWED_PHASE_PHASE_2C_11_NEXT_SLICE_CANDIDATE_INVENTORY_PLANNING_ONLY",
    "DUPLICATES_PHASE_2C_03_PATTERN_REUSE_ONLY",
    "DUPLICATES_DAY1_DAY160_REFERENCE_ONLY",
    "NEXT_SLICE_CANDIDATES_LISTED_NO",
    "NEXT_SLICE_SELECTED_NO",
    "NEXT_IMPLEMENTATION_AUTHORIZED_NO",
    "NEXT_IMPLEMENTATION_STARTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO",
    "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def _load_json_artifact(project_root: Path, path: Path) -> Dict[str, Any]:
    absolute_path = project_root / path
    if not absolute_path.exists():
        return {"path": path.as_posix(), "exists": False, "loaded": False, "data": {}}
    try:
        data = json.loads(absolute_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": path.as_posix(),
            "exists": True,
            "loaded": False,
            "error": f"JSON_DECODE_ERROR:{exc.msg}",
            "data": {},
        }
    if not isinstance(data, Mapping):
        return {"path": path.as_posix(), "exists": True, "loaded": False, "error": "JSON_NOT_OBJECT", "data": {}}
    return {"path": path.as_posix(), "exists": True, "loaded": True, "data": dict(data)}


def _source_artifacts_available(project_root: Path, artifacts: Sequence[Path]) -> bool:
    return all((project_root / artifact).exists() for artifact in artifacts)


def _generated_json_artifact(path: Path, data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": True,
        "loaded": True,
        "persisted_file_exists": False,
        "materialized_from_source": True,
        "data": dict(data),
    }


def _artifact_record(project_root: Path, path_text: str) -> Dict[str, Any]:
    path = Path(path_text)
    return {
        "path": path.as_posix(),
        "exists": (project_root / path).exists(),
        "local_repository_artifact": True,
        "external_access_required": False,
    }


def _phase_2c_09_acceptance_review(project_root: Path) -> Dict[str, Any]:
    artifact = _load_json_artifact(project_root, PHASE_2C_09_REPORT_JSON)
    if artifact.get("loaded") is not True and _source_artifacts_available(
        project_root,
        (PHASE_2C_09_SOURCE_PATH, PHASE_2C_09_DOC_PATH),
    ):
        artifact = _generated_json_artifact(
            PHASE_2C_09_REPORT_JSON,
            build_phase_2c_09_post_next_slice_acceptance_review_report(project_root),
        )
    data = artifact.get("data", {})
    validation = validate_phase_2c_09_report(data) if artifact.get("loaded") is True else {}
    return {
        "path": artifact["path"],
        "exists": artifact["exists"],
        "loaded": artifact["loaded"],
        "reviewed_task": PHASE_2C_09_TASK_NAME,
        "expected_verdict": PHASE_2C_09_VERDICT,
        "observed_verdict": data.get("final_verdict") if isinstance(data, Mapping) else None,
        "acceptance_decision": data.get("acceptance_decision") if isinstance(data, Mapping) else None,
        "artifact_validation_job_accepted": data.get("artifact_validation_job_accepted") if isinstance(data, Mapping) else None,
        "source_validation": validation,
    }


def _phase_2c_09_acceptance_confirmed(acceptance_review: Mapping[str, Any]) -> bool:
    source_validation = acceptance_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping):
        source_validation = {}
    return (
        acceptance_review.get("exists") is True
        and acceptance_review.get("loaded") is True
        and acceptance_review.get("observed_verdict") == PHASE_2C_09_VERDICT
        and acceptance_review.get("acceptance_decision") == "ACCEPT"
        and acceptance_review.get("artifact_validation_job_accepted") == "YES"
        and source_validation.get("valid") is True
    )


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_10": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_10_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
    if report.get("example_job_types_section") != EXAMPLE_JOB_TYPES_SECTION:
        errors.append("EXAMPLE_JOB_TYPES_SECTION_MISMATCH")
    if report.get("candidate_inventory") != []:
        errors.append("CANDIDATE_INVENTORY_NOT_EMPTY")
    if report.get("next_allowed_phase") != NEXT_ALLOWED_PHASE:
        errors.append("NEXT_ALLOWED_PHASE_MISMATCH")
    if report.get("duplicates_phase_2c_03") != "PATTERN_REUSE_ONLY":
        errors.append("DUPLICATES_PHASE_2C_03_MISMATCH")
    if report.get("duplicates_day1_day160") != "REFERENCE_ONLY":
        errors.append("DUPLICATES_DAY1_DAY160_MISMATCH")
    if report.get("non_duplication_phase_2c_03") != NON_DUPLICATION_PHASE_2C_03:
        errors.append("NON_DUPLICATION_PHASE_2C_03_MISMATCH")
    if report.get("non_duplication_day1_day160") != NON_DUPLICATION_DAY1_DAY160:
        errors.append("NON_DUPLICATION_DAY1_DAY160_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    artifacts = set(report.get("existing_artifacts_reviewed", []))
    for artifact in EXISTING_ARTIFACTS_REVIEWED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    source_review = report.get("phase_2c_09_acceptance_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("PHASE_2C_09_ACCEPTANCE_REVIEW_NOT_OBJECT")
        source_review = {}
    if report.get("phase_2c_09_acceptance_confirmed") is not True:
        errors.append(BLOCKED_VERDICT)
    if source_review.get("acceptance_decision") != "ACCEPT":
        errors.append("PHASE_2C_09_DECISION_NOT_ACCEPT")
    if source_review.get("observed_verdict") != PHASE_2C_09_VERDICT:
        errors.append("PHASE_2C_09_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("PHASE_2C_09_VALIDATION_NOT_PASS")

    if tuple(report.get("decision_criteria", ())) != DECISION_CRITERIA:
        errors.append("DECISION_CRITERIA_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("decision_criteria", ())):
        errors.append("DECISION_CRITERIA_NOT_PASS")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2C_09_ACCEPTANCE_CONFIRMED": "YES",
        "PHASE_2C_09_DECISION": "ACCEPT",
        "ALLOW_NEXT_PLANNING": "YES",
        "NEXT_ALLOWED_PHASE": NEXT_ALLOWED_PHASE,
        "DUPLICATES_PHASE_2C_03": "PATTERN_REUSE_ONLY",
        "DUPLICATES_DAY1_DAY160": "REFERENCE_ONLY",
        "NEXT_SLICE_CANDIDATES_LISTED": "NO",
        "NEXT_SLICE_SELECTED": "NO",
        "NEXT_IMPLEMENTATION_AUTHORIZED": "NO",
        "NEXT_IMPLEMENTATION_STARTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
        "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "needs_scope_confirmation",
        "agents_md_modified",
        "phase_2c_11_started",
        "next_slice_candidates_listed",
        "next_slice_selected",
        "next_implementation_authorized",
        "next_implementation_started",
        "runner_added",
        "adapter_added",
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
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
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
    }


def build_phase_2c_10_next_slice_decision_gate_authorization_review_report(project_root: Path) -> Dict[str, Any]:
    acceptance_review = _phase_2c_09_acceptance_review(project_root)
    acceptance_confirmed = _phase_2c_09_acceptance_confirmed(acceptance_review)
    allow_next_planning = acceptance_confirmed
    final_verdict = FINAL_VERDICT if acceptance_confirmed else BLOCKED_VERDICT
    status = STATUS if acceptance_confirmed else "FAIL"

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
        "authorization_decision": "ALLOW_NEXT_PLANNING_ONLY" if allow_next_planning else "BLOCKED",
        "allow_next_planning": allow_next_planning,
        "next_allowed_phase": NEXT_ALLOWED_PHASE if allow_next_planning else "NONE",
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_action": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "status": "PASS",
            "scope_confirmation_written": True,
            "phase_goal": PHASE_GOAL,
            "example_job_types": EXAMPLE_JOB_TYPES_SECTION,
            "forbidden_scope": list(FORBIDDEN_SCOPE),
            "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REVIEWED),
            "implementation_boundary": IMPLEMENTATION_BOUNDARY,
            "needs_scope_confirmation": False,
        },
        "example_job_types_section": EXAMPLE_JOB_TYPES_SECTION,
        "candidate_inventory": [],
        "candidate_inventory_deferred_to": NEXT_ALLOWED_PHASE,
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_reviewed": list(EXISTING_ARTIFACTS_REVIEWED),
        "artifact_records": [_artifact_record(project_root, path) for path in EXISTING_ARTIFACTS_REVIEWED],
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "phase_2c_09_acceptance_review": acceptance_review,
        "phase_2c_09_acceptance_confirmed": acceptance_confirmed,
        "phase_2c_09_decision": acceptance_review.get("acceptance_decision") or "NOT_FOUND",
        "phase_2c_08_verdict_referenced": PHASE_2C_08_VERDICT,
        "phase_2c_09_verdict_referenced": PHASE_2C_09_VERDICT,
        "phase_2c_03_pattern_referenced": {
            "task": PHASE_2C_03_TASK_NAME,
            "verdict": PHASE_2C_03_VERDICT,
        },
        "phase_2c_04_to_2c_07_flow_referenced": {
            PHASE_2C_04_TASK_NAME: PHASE_2C_04_VERDICT,
            PHASE_2C_05_TASK_NAME: PHASE_2C_05_VERDICT,
            PHASE_2C_06_TASK_NAME: PHASE_2C_06_VERDICT,
            PHASE_2C_07_TASK_NAME: PHASE_2C_07_VERDICT,
        },
        "phase_2c_08_task_referenced": PHASE_2C_08_TASK_NAME,
        "duplicates_phase_2c_03": "PATTERN_REUSE_ONLY",
        "non_duplication_phase_2c_03": NON_DUPLICATION_PHASE_2C_03,
        "duplicates_day1_day160": "REFERENCE_ONLY",
        "non_duplication_day1_day160": NON_DUPLICATION_DAY1_DAY160,
        "decision_criteria": deepcopy(DECISION_CRITERIA),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "deferred_work": (
            "Phase 2C-11 may create the next-slice candidate inventory only if "
            "this gate remains accepted. Phase 2C-10 itself does not create "
            "that inventory."
        ),
        "non_execution_statement": (
            "Phase 2C-10 is planning-only authorization review evidence. It "
            "allows only entry into Phase 2C-11 planning and does not list "
            "candidates, select a slice, authorize implementation, start "
            "implementation, or open execution, live-device, provider/API/model, "
            "secret, backup, configuration-change, Day1-Day160 replacement, or "
            "second-safety-matrix scope."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2C_09_ACCEPTANCE_CONFIRMED": "YES",
            "PHASE_2C_09_DECISION": "ACCEPT",
            "ALLOW_NEXT_PLANNING": "YES",
            "NEXT_ALLOWED_PHASE": NEXT_ALLOWED_PHASE,
            "DUPLICATES_PHASE_2C_03": "PATTERN_REUSE_ONLY",
            "DUPLICATES_DAY1_DAY160": "REFERENCE_ONLY",
            "NEXT_SLICE_CANDIDATES_LISTED": "NO",
            "NEXT_SLICE_SELECTED": "NO",
            "NEXT_IMPLEMENTATION_AUTHORIZED": "NO",
            "NEXT_IMPLEMENTATION_STARTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    if not acceptance_confirmed:
        report["phase_2c_09_acceptance_confirmed"] = False
        report["allow_next_planning"] = False
        report["next_allowed_phase"] = "NONE"
        report["machine_readable_verdict"] = {
            **report["machine_readable_verdict"],
            "FINAL_VERDICT": BLOCKED_VERDICT,
            "PHASE_2C_09_ACCEPTANCE_CONFIRMED": "NO",
            "PHASE_2C_09_DECISION": str(report["phase_2c_09_decision"]),
            "ALLOW_NEXT_PLANNING": "NO",
            "NEXT_ALLOWED_PHASE": "NONE",
        }

    report["summary"] = {
        "phase_2c_09_acceptance_confirmed": acceptance_confirmed,
        "phase_2c_09_decision": report["phase_2c_09_decision"],
        "allow_next_planning": allow_next_planning,
        "next_allowed_phase": report["next_allowed_phase"],
        "duplicates_phase_2c_03": "PATTERN_REUSE_ONLY",
        "duplicates_day1_day160": "REFERENCE_ONLY",
        "next_slice_candidates_listed": False,
        "next_slice_selected": False,
        "next_implementation_authorized": False,
        "next_implementation_started": False,
        "runner_adapter_execution_path_added": False,
        "scheduler_queue_broker_worker_agent_loop_added": False,
        "live_device_ssh_netconf_restconf_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": final_verdict,
    }
    validation = validate_phase_2c_10_report(report) if acceptance_confirmed else {
        "valid": False,
        "status": "FAIL",
        "errors": [BLOCKED_VERDICT],
        "decision_criteria_checked": len(report.get("decision_criteria", [])),
        "existing_artifacts_reviewed": len(report.get("existing_artifacts_reviewed", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        if acceptance_confirmed:
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
  <p>ALLOW_NEXT_PLANNING: <strong>{html.escape("YES" if report["allow_next_planning"] else "NO")}</strong></p>
  <p>Next allowed phase: <strong>{html.escape(str(report["next_allowed_phase"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Phase 2C-09 Acceptance Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_09_acceptance_review"])}</tbody></table>
  <h2>Decision Criteria</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_check_rows(report["decision_criteria"])}</tbody></table>
  <h2>Example Job Types</h2>
  <p>{html.escape(str(report["example_job_types_section"]))}</p>
  <h2>Non-Duplication Checks</h2>
  <p>{html.escape(str(report["non_duplication_phase_2c_03"]))}</p>
  <p>{html.escape(str(report["non_duplication_day1_day160"]))}</p>
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


def write_phase_2c_10_next_slice_decision_gate_authorization_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_10_next_slice_decision_gate_authorization_review_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_10_next_slice_decision_gate_authorization_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_10_next_slice_decision_gate_authorization_review_report(project_root)
    json_path, html_path = write_phase_2c_10_next_slice_decision_gate_authorization_review_reports(
        project_root, report
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"phase_2c_09_acceptance_confirmed: {str(report['summary']['phase_2c_09_acceptance_confirmed']).lower()}")
    print(f"phase_2c_09_decision: {report['summary']['phase_2c_09_decision']}")
    print(f"allow_next_planning: {'YES' if report['summary']['allow_next_planning'] else 'NO'}")
    print(f"next_allowed_phase: {report['summary']['next_allowed_phase']}")
    print(f"duplicates_phase_2c_03: {report['summary']['duplicates_phase_2c_03']}")
    print(f"duplicates_day1_day160: {report['summary']['duplicates_day1_day160']}")
    print(f"next_slice_candidates_listed: {str(report['summary']['next_slice_candidates_listed']).lower()}")
    print(f"next_slice_selected: {str(report['summary']['next_slice_selected']).lower()}")
    print(
        "next_implementation_authorized: "
        f"{str(report['summary']['next_implementation_authorized']).lower()}"
    )
    print(f"next_implementation_started: {str(report['summary']['next_implementation_started']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
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
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
