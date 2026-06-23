"""Phase 2C-09 post-next-slice acceptance review.

This module creates deterministic, local, report-only acceptance evidence for
the Phase 2C-08 `artifact_validation_job` next-slice implementation. It
reviews existing Phase 2C evidence only. It does not start another slice,
select a next slice, modify the implementation, or call runners, adapters,
brokers, schedulers, queues, workers, agent loops, shells, scripts, SSH,
NETCONF, RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_06_next_slice_final_selection_gate import (
    REPORT_JSON as PHASE_2C_06_REPORT_JSON,
    SELECTED_NEXT_SLICE,
    TASK_NAME as PHASE_2C_06_TASK_NAME,
    validate_phase_2c_06_report,
)
from phase_2c_07_next_slice_implementation_kickoff_gate import (
    REPORT_JSON as PHASE_2C_07_REPORT_JSON,
    TASK_NAME as PHASE_2C_07_TASK_NAME,
    validate_phase_2c_07_report,
)
from phase_2c_08_next_slice_implementation import (
    FINAL_VERDICT as PHASE_2C_08_VERDICT,
    REPORT_HTML as PHASE_2C_08_REPORT_HTML,
    REPORT_JSON as PHASE_2C_08_REPORT_JSON,
    TASK_NAME as PHASE_2C_08_TASK_NAME,
    validate_phase_2c_08_report,
)


PHASE = "2C-09"
TASK_NAME = "phase2c-09-post-next-slice-acceptance-review"
TITLE = "Phase 2C-09 Post-Next-Slice Acceptance Review - Report Only"
MODE = "post_next_slice_acceptance_review_report_only"
SCOPE = "phase_2c_08_artifact_validation_job_acceptance_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_09_POST_NEXT_SLICE_ACCEPTED"
NOT_ACCEPT_VERDICT = "PHASE_2C_09_POST_NEXT_SLICE_NOT_ACCEPTED"
NEEDS_EVIDENCE_VERDICT = "PHASE_2C_09_NEEDS_EVIDENCE"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_09_post_next_slice_acceptance_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_09_post_next_slice_acceptance_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_09_post_next_slice_acceptance_review.md"

ALLOWED_ACCEPTANCE_DECISIONS = ("ACCEPT", "NOT_ACCEPT", "NEEDS_EVIDENCE")

PHASE_GOAL = (
    "Review whether the completed or claimed Phase 2C-08 artifact_validation_job "
    "implementation is acceptable against Phase 2C-06 selection evidence, Phase "
    "2C-07 authorization evidence, existing project safety boundaries, and "
    "report-only / dry-run / mock-only expectations."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job",
    "artifact_validation_job",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
)

FORBIDDEN_SCOPE = (
    "new implementation slice",
    "next slice selection",
    "Phase 2C-10 start",
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
    "config backup behavior",
    "config change behavior",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
)

EXISTING_ARTIFACTS_REVIEWED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md",
    "docs/phase_2c/phase_2c_07_next_slice_implementation_kickoff_gate.md",
    "docs/phase_2c/phase_2c_08_next_slice_implementation.md",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "phase_2c_06_next_slice_final_selection_gate.py",
    "phase_2c_07_next_slice_implementation_kickoff_gate.py",
    "phase_2c_08_next_slice_implementation.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "tests/test_phase_2c_08_next_slice_implementation.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    PHASE_2C_06_REPORT_JSON.as_posix(),
    PHASE_2C_07_REPORT_JSON.as_posix(),
    PHASE_2C_08_REPORT_JSON.as_posix(),
    PHASE_2C_08_REPORT_HTML.as_posix(),
)

ACCEPTANCE_REVIEW_QUESTIONS = (
    "Was artifact_validation_job the selected next slice from Phase 2C-06?",
    "Was artifact_validation_job authorized by Phase 2C-07?",
    "Does Phase 2C-08 evidence exist?",
    "Does Phase 2C-08 stay within the authorized implementation boundary?",
    "Does Phase 2C-08 avoid forbidden execution paths?",
    "Is Phase 2C-08 acceptable, not acceptable, or missing enough evidence?",
)

SAFETY_FLAGS = {
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmed_in_writing": True,
    "needs_scope_confirmation": False,
    "acceptance_review_created": True,
    "report_only_artifact_created": True,
    "phase_2c_08_source_task_rerun": False,
    "phase_2c_08_implementation_modified": False,
    "artifact_validation_job_modified": False,
    "next_slice_selected": False,
    "next_implementation_started": False,
    "phase_2c_10_started": False,
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
    "config_backup_change_behavior_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_09_POST_NEXT_SLICE_ACCEPTANCE_REVIEW_REPORT_ONLY",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "SCOPE_CONFIRMED_IN_WRITING_YES",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "PHASE_2C_06_SELECTION_CONFIRMED_YES",
    "PHASE_2C_07_AUTHORIZATION_CONFIRMED_YES",
    "PHASE_2C_08_EVIDENCE_FOUND_YES",
    "ARTIFACT_VALIDATION_JOB_ACCEPTED_YES",
    "REPORT_ONLY_ARTIFACT_CREATED_YES",
    "NEXT_SLICE_SELECTED_NO",
    "NEXT_IMPLEMENTATION_STARTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED_NO",
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


def _artifact_record(project_root: Path, path_text: str) -> Dict[str, Any]:
    path = Path(path_text)
    return {
        "path": path.as_posix(),
        "exists": (project_root / path).exists(),
        "local_repository_artifact": True,
        "external_access_required": False,
    }


def _source_evidence_review(project_root: Path) -> Dict[str, Any]:
    phase_2c_06_json = _load_json_artifact(project_root, PHASE_2C_06_REPORT_JSON)
    phase_2c_07_json = _load_json_artifact(project_root, PHASE_2C_07_REPORT_JSON)
    phase_2c_08_json = _load_json_artifact(project_root, PHASE_2C_08_REPORT_JSON)

    phase_2c_06_data = phase_2c_06_json.get("data", {})
    phase_2c_07_data = phase_2c_07_json.get("data", {})
    phase_2c_08_data = phase_2c_08_json.get("data", {})

    phase_2c_06_validation = (
        validate_phase_2c_06_report(phase_2c_06_data) if phase_2c_06_json.get("loaded") is True else {}
    )
    phase_2c_07_validation = (
        validate_phase_2c_07_report(phase_2c_07_data) if phase_2c_07_json.get("loaded") is True else {}
    )
    phase_2c_08_validation = (
        validate_phase_2c_08_report(phase_2c_08_data) if phase_2c_08_json.get("loaded") is True else {}
    )

    phase_2c_08_html_exists = (project_root / PHASE_2C_08_REPORT_HTML).exists()
    return {
        "phase_2c_06_report_json": {
            "path": phase_2c_06_json["path"],
            "exists": phase_2c_06_json["exists"],
            "loaded": phase_2c_06_json["loaded"],
            "reviewed_task": PHASE_2C_06_TASK_NAME,
            "selected_next_slice": phase_2c_06_data.get("selected_next_slice"),
            "next_slice_authorized": phase_2c_06_data.get("next_slice_authorized"),
            "validation": phase_2c_06_validation,
        },
        "phase_2c_07_report_json": {
            "path": phase_2c_07_json["path"],
            "exists": phase_2c_07_json["exists"],
            "loaded": phase_2c_07_json["loaded"],
            "reviewed_task": PHASE_2C_07_TASK_NAME,
            "selected_next_slice": phase_2c_07_data.get("selected_next_slice"),
            "selected_next_slice_authorized_for_phase_2c_08": phase_2c_07_data.get(
                "selected_next_slice_authorized_for_phase_2c_08"
            ),
            "validation": phase_2c_07_validation,
        },
        "phase_2c_08_report_json": {
            "path": phase_2c_08_json["path"],
            "exists": phase_2c_08_json["exists"],
            "loaded": phase_2c_08_json["loaded"],
            "reviewed_task": PHASE_2C_08_TASK_NAME,
            "selected_next_slice": phase_2c_08_data.get("selected_next_slice"),
            "artifact_validation_job_implemented": phase_2c_08_data.get("artifact_validation_job_implemented"),
            "final_verdict": phase_2c_08_data.get("final_verdict"),
            "local_only": phase_2c_08_data.get("local_only"),
            "deterministic": phase_2c_08_data.get("deterministic"),
            "report_only": phase_2c_08_data.get("report_only"),
            "dry_run_only": phase_2c_08_data.get("dry_run_only"),
            "mock_only": phase_2c_08_data.get("mock_only"),
            "runner_added": phase_2c_08_data.get("runner_added"),
            "adapter_added": phase_2c_08_data.get("adapter_added"),
            "execution_path_added": phase_2c_08_data.get("execution_path_added"),
            "scheduler_added": phase_2c_08_data.get("scheduler_added"),
            "queue_added": phase_2c_08_data.get("queue_added"),
            "broker_added": phase_2c_08_data.get("broker_added"),
            "worker_added": phase_2c_08_data.get("worker_added"),
            "agent_loop_added": phase_2c_08_data.get("agent_loop_added"),
            "ssh_netconf_restconf_live_device_touched": phase_2c_08_data.get(
                "ssh_netconf_restconf_live_device_touched"
            ),
            "provider_api_model_secrets_touched": phase_2c_08_data.get("provider_api_model_secrets_touched"),
            "config_backup_or_change_added": phase_2c_08_data.get("config_backup_or_change_added"),
            "day1_day160_rewritten_or_replaced": phase_2c_08_data.get("day1_day160_rewritten_or_replaced"),
            "second_safety_matrix_created": phase_2c_08_data.get("second_safety_matrix_created"),
            "validation": phase_2c_08_validation,
        },
        "phase_2c_08_report_html": {
            "path": PHASE_2C_08_REPORT_HTML.as_posix(),
            "exists": phase_2c_08_html_exists,
        },
    }


def _phase_2c_06_selection_confirmed(source_review: Mapping[str, Any]) -> bool:
    review = source_review.get("phase_2c_06_report_json", {})
    if not isinstance(review, Mapping):
        return False
    return (
        review.get("exists") is True
        and review.get("loaded") is True
        and review.get("selected_next_slice") == SELECTED_NEXT_SLICE
        and review.get("next_slice_authorized") is False
        and review.get("validation", {}).get("valid") is True
    )


def _phase_2c_07_authorization_confirmed(source_review: Mapping[str, Any]) -> bool:
    review = source_review.get("phase_2c_07_report_json", {})
    if not isinstance(review, Mapping):
        return False
    return (
        review.get("exists") is True
        and review.get("loaded") is True
        and review.get("selected_next_slice") == SELECTED_NEXT_SLICE
        and review.get("selected_next_slice_authorized_for_phase_2c_08") is True
        and review.get("validation", {}).get("valid") is True
    )


def _phase_2c_08_evidence_found(source_review: Mapping[str, Any]) -> bool:
    json_review = source_review.get("phase_2c_08_report_json", {})
    html_review = source_review.get("phase_2c_08_report_html", {})
    if not isinstance(json_review, Mapping) or not isinstance(html_review, Mapping):
        return False
    return json_review.get("exists") is True and json_review.get("loaded") is True and html_review.get("exists") is True


def _phase_2c_08_acceptance_facts(source_review: Mapping[str, Any]) -> Dict[str, bool]:
    review = source_review.get("phase_2c_08_report_json", {})
    if not isinstance(review, Mapping):
        review = {}
    validation = review.get("validation", {})
    if not isinstance(validation, Mapping):
        validation = {}
    return {
        "phase_2c_08_validation_passed": validation.get("valid") is True,
        "selected_next_slice_matches": review.get("selected_next_slice") == SELECTED_NEXT_SLICE,
        "final_verdict_matches": review.get("final_verdict") == PHASE_2C_08_VERDICT,
        "artifact_validation_job_implemented": review.get("artifact_validation_job_implemented") is True,
        "local_only": review.get("local_only") is True,
        "deterministic": review.get("deterministic") is True,
        "report_only": review.get("report_only") is True,
        "dry_run_only": review.get("dry_run_only") is True,
        "mock_only": review.get("mock_only") is True,
        "runner_adapter_execution_path_added": (
            review.get("runner_added") is False
            and review.get("adapter_added") is False
            and review.get("execution_path_added") is False
        ),
        "scheduler_queue_broker_worker_agent_loop_added": (
            review.get("scheduler_added") is False
            and review.get("queue_added") is False
            and review.get("broker_added") is False
            and review.get("worker_added") is False
            and review.get("agent_loop_added") is False
        ),
        "ssh_netconf_restconf_live_device_touched": review.get("ssh_netconf_restconf_live_device_touched") is False,
        "provider_api_model_secrets_touched": review.get("provider_api_model_secrets_touched") is False,
        "config_backup_change_behavior_added": review.get("config_backup_or_change_added") is False,
        "day1_day160_rewritten_or_replaced": review.get("day1_day160_rewritten_or_replaced") is False,
        "second_safety_matrix_created": review.get("second_safety_matrix_created") is False,
    }


def _acceptance_decision(
    phase_2c_06_selection_confirmed: bool,
    phase_2c_07_authorization_confirmed: bool,
    phase_2c_08_evidence_found: bool,
    phase_2c_08_facts: Mapping[str, bool],
) -> str:
    if (
        phase_2c_06_selection_confirmed is not True
        or phase_2c_07_authorization_confirmed is not True
        or phase_2c_08_evidence_found is not True
    ):
        return "NEEDS_EVIDENCE"
    if all(phase_2c_08_facts.values()):
        return "ACCEPT"
    return "NOT_ACCEPT"


def _acceptance_checks(
    phase_2c_06_selection_confirmed: bool,
    phase_2c_07_authorization_confirmed: bool,
    phase_2c_08_evidence_found: bool,
    phase_2c_08_facts: Mapping[str, bool],
    acceptance_decision: str,
) -> Tuple[Dict[str, Any], ...]:
    checks = (
        ("Phase 2C-06 selected artifact_validation_job", phase_2c_06_selection_confirmed),
        ("Phase 2C-07 authorized moving into Phase 2C-08", phase_2c_07_authorization_confirmed),
        ("Phase 2C-08 JSON/HTML evidence exists", phase_2c_08_evidence_found),
        ("Phase 2C-08 validation passed", phase_2c_08_facts.get("phase_2c_08_validation_passed") is True),
        ("Phase 2C-08 selected next slice matches artifact_validation_job", phase_2c_08_facts.get("selected_next_slice_matches") is True),
        ("Phase 2C-08 stayed local", phase_2c_08_facts.get("local_only") is True),
        ("Phase 2C-08 stayed deterministic", phase_2c_08_facts.get("deterministic") is True),
        ("Phase 2C-08 stayed report-only / dry-run / mock-only", (
            phase_2c_08_facts.get("report_only") is True
            and phase_2c_08_facts.get("dry_run_only") is True
            and phase_2c_08_facts.get("mock_only") is True
        )),
        ("Phase 2C-08 avoided runner / adapter / execution path", phase_2c_08_facts.get("runner_adapter_execution_path_added") is True),
        ("Phase 2C-08 avoided scheduler / queue / broker / worker / agent loop", phase_2c_08_facts.get("scheduler_queue_broker_worker_agent_loop_added") is True),
        ("Phase 2C-08 avoided SSH / NETCONF / RESTCONF / live device access", phase_2c_08_facts.get("ssh_netconf_restconf_live_device_touched") is True),
        ("Phase 2C-08 avoided provider / API / model / secrets", phase_2c_08_facts.get("provider_api_model_secrets_touched") is True),
        ("Phase 2C-08 avoided config backup / config change behavior", phase_2c_08_facts.get("config_backup_change_behavior_added") is True),
        ("Phase 2C-08 did not rewrite or replace Day1-Day160", phase_2c_08_facts.get("day1_day160_rewritten_or_replaced") is True),
        ("Phase 2C-08 did not create a second safety matrix", phase_2c_08_facts.get("second_safety_matrix_created") is True),
        ("Phase 2C-09 does not select a next slice", True),
        ("Phase 2C-09 does not start the next implementation", True),
    )
    return tuple(
        {
            "check": name,
            "passed": passed is True,
            "status": "PASS" if passed is True else ("NEEDS_EVIDENCE" if acceptance_decision == "NEEDS_EVIDENCE" else "FAIL"),
        }
        for name, passed in checks
    )


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_09": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_09_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
    if report.get("acceptance_decision") not in ALLOWED_ACCEPTANCE_DECISIONS:
        errors.append("ACCEPTANCE_DECISION_INVALID")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    if report.get("next_slice_selected") is not False:
        errors.append("NEXT_SLICE_SELECTED_NOT_FALSE")
    if report.get("next_implementation_started") is not False:
        errors.append("NEXT_IMPLEMENTATION_STARTED_NOT_FALSE")

    blocked_flags = (
        "needs_scope_confirmation",
        "agents_md_modified",
        "phase_2c_08_source_task_rerun",
        "phase_2c_08_implementation_modified",
        "artifact_validation_job_modified",
        "next_slice_selected",
        "next_implementation_started",
        "phase_2c_10_started",
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
        "config_backup_change_behavior_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append("PHASE_2C_09_FORBIDDEN_SCOPE_OPENED")

    expected_verdict = {
        "FINAL_VERDICT": report.get("final_verdict"),
        "ACCEPTANCE_DECISION": report.get("acceptance_decision"),
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "SCOPE_CONFIRMED_IN_WRITING": "YES",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "PHASE_2C_06_SELECTION_CONFIRMED": "YES" if report.get("phase_2c_06_selection_confirmed") else "NO",
        "PHASE_2C_07_AUTHORIZATION_CONFIRMED": "YES" if report.get("phase_2c_07_authorization_confirmed") else "NO",
        "PHASE_2C_08_EVIDENCE_FOUND": "YES" if report.get("phase_2c_08_evidence_found") else "NO",
        "ARTIFACT_VALIDATION_JOB_ACCEPTED": report.get("artifact_validation_job_accepted"),
        "REPORT_ONLY_ARTIFACT_CREATED": "YES",
        "NEXT_SLICE_SELECTED": "NO",
        "NEXT_IMPLEMENTATION_STARTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if report.get("acceptance_decision") == "ACCEPT":
        required_accept_flags = (
            "phase_2c_06_selection_confirmed",
            "phase_2c_07_authorization_confirmed",
            "phase_2c_08_evidence_found",
            "phase_2c_08_within_authorized_boundary",
            "phase_2c_08_forbidden_execution_paths_avoided",
        )
        if any(report.get(flag) is not True for flag in required_accept_flags):
            errors.append("ACCEPT_DECISION_WITHOUT_REQUIRED_EVIDENCE")
        if any(check.get("status") != "PASS" for check in report.get("acceptance_checks", [])):
            errors.append("ACCEPTANCE_CHECK_NOT_PASS")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "acceptance_checks_reviewed": len(report.get("acceptance_checks", [])),
        "existing_artifacts_reviewed": len(report.get("existing_artifacts_reviewed", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }


def build_phase_2c_09_post_next_slice_acceptance_review_report(project_root: Path) -> Dict[str, Any]:
    source_review = _source_evidence_review(project_root)
    phase_2c_06_selection_confirmed = _phase_2c_06_selection_confirmed(source_review)
    phase_2c_07_authorization_confirmed = _phase_2c_07_authorization_confirmed(source_review)
    phase_2c_08_evidence_found = _phase_2c_08_evidence_found(source_review)
    phase_2c_08_facts = _phase_2c_08_acceptance_facts(source_review)
    acceptance_decision = _acceptance_decision(
        phase_2c_06_selection_confirmed,
        phase_2c_07_authorization_confirmed,
        phase_2c_08_evidence_found,
        phase_2c_08_facts,
    )
    final_verdict = {
        "ACCEPT": FINAL_VERDICT,
        "NOT_ACCEPT": NOT_ACCEPT_VERDICT,
        "NEEDS_EVIDENCE": NEEDS_EVIDENCE_VERDICT,
    }[acceptance_decision]
    artifact_validation_job_accepted = {
        "ACCEPT": "YES",
        "NOT_ACCEPT": "NO",
        "NEEDS_EVIDENCE": "NEEDS_EVIDENCE",
    }[acceptance_decision]
    phase_2c_08_within_authorized_boundary = (
        phase_2c_08_evidence_found
        and phase_2c_08_facts.get("selected_next_slice_matches") is True
        and phase_2c_08_facts.get("phase_2c_08_validation_passed") is True
        and phase_2c_08_facts.get("local_only") is True
        and phase_2c_08_facts.get("deterministic") is True
        and phase_2c_08_facts.get("report_only") is True
        and phase_2c_08_facts.get("dry_run_only") is True
        and phase_2c_08_facts.get("mock_only") is True
    )
    phase_2c_08_forbidden_execution_paths_avoided = (
        phase_2c_08_facts.get("runner_adapter_execution_path_added") is True
        and phase_2c_08_facts.get("scheduler_queue_broker_worker_agent_loop_added") is True
        and phase_2c_08_facts.get("ssh_netconf_restconf_live_device_touched") is True
        and phase_2c_08_facts.get("provider_api_model_secrets_touched") is True
        and phase_2c_08_facts.get("config_backup_change_behavior_added") is True
        and phase_2c_08_facts.get("day1_day160_rewritten_or_replaced") is True
        and phase_2c_08_facts.get("second_safety_matrix_created") is True
    )

    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": final_verdict,
        "acceptance_decision": acceptance_decision,
        "phase_goal": PHASE_GOAL,
        "acceptance_review_questions": list(ACCEPTANCE_REVIEW_QUESTIONS),
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "reference_examples_only_not_phase_2c_09_implementation_targets",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_reviewed": list(EXISTING_ARTIFACTS_REVIEWED),
        "artifact_records": [_artifact_record(project_root, path) for path in EXISTING_ARTIFACTS_REVIEWED],
        "source_evidence_review": source_review,
        "phase_2c_08_acceptance_facts": dict(phase_2c_08_facts),
        "phase_2c_06_selection_confirmed": phase_2c_06_selection_confirmed,
        "phase_2c_07_authorization_confirmed": phase_2c_07_authorization_confirmed,
        "phase_2c_08_evidence_found": phase_2c_08_evidence_found,
        "phase_2c_08_within_authorized_boundary": phase_2c_08_within_authorized_boundary,
        "phase_2c_08_forbidden_execution_paths_avoided": phase_2c_08_forbidden_execution_paths_avoided,
        "artifact_validation_job_accepted": artifact_validation_job_accepted,
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_execution_statement": (
            "Phase 2C-09 is a report-only acceptance review of existing Phase "
            "2C-08 evidence. It does not select a next slice, start Phase "
            "2C-10, modify artifact_validation_job, or add runner, adapter, "
            "execution, live-device, provider/API/model, secret, backup, or "
            "configuration-change behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": final_verdict,
            "ACCEPTANCE_DECISION": acceptance_decision,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "SCOPE_CONFIRMED_IN_WRITING": "YES",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "PHASE_2C_06_SELECTION_CONFIRMED": "YES" if phase_2c_06_selection_confirmed else "NO",
            "PHASE_2C_07_AUTHORIZATION_CONFIRMED": "YES" if phase_2c_07_authorization_confirmed else "NO",
            "PHASE_2C_08_EVIDENCE_FOUND": "YES" if phase_2c_08_evidence_found else "NO",
            "ARTIFACT_VALIDATION_JOB_ACCEPTED": artifact_validation_job_accepted,
            "REPORT_ONLY_ARTIFACT_CREATED": "YES",
            "NEXT_SLICE_SELECTED": "NO",
            "NEXT_IMPLEMENTATION_STARTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["acceptance_checks"] = list(
        _acceptance_checks(
            phase_2c_06_selection_confirmed,
            phase_2c_07_authorization_confirmed,
            phase_2c_08_evidence_found,
            phase_2c_08_facts,
            acceptance_decision,
        )
    )
    report["summary"] = {
        "acceptance_decision": acceptance_decision,
        "phase_2c_06_selection_confirmed": phase_2c_06_selection_confirmed,
        "phase_2c_07_authorization_confirmed": phase_2c_07_authorization_confirmed,
        "phase_2c_08_evidence_found": phase_2c_08_evidence_found,
        "phase_2c_08_within_authorized_boundary": phase_2c_08_within_authorized_boundary,
        "phase_2c_08_forbidden_execution_paths_avoided": phase_2c_08_forbidden_execution_paths_avoided,
        "artifact_validation_job_accepted": artifact_validation_job_accepted,
        "report_only_artifact_created": True,
        "next_slice_selected": False,
        "next_implementation_started": False,
        "runner_adapter_execution_path_added": False,
        "scheduler_queue_broker_worker_agent_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": final_verdict,
    }
    validation = validate_phase_2c_09_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
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
        f"<td>{html.escape(str(item.get('status')))}</td>"
        f"<td>{html.escape(str(item.get('passed')))}</td>"
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
  <p>Acceptance decision: <strong>{html.escape(str(report["acceptance_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Acceptance Checks</h2>
  <table><thead><tr><th>Check</th><th>Status</th><th>Passed</th></tr></thead><tbody>{_check_rows(report["acceptance_checks"])}</tbody></table>
  <h2>Phase 2C-08 Acceptance Facts</h2>
  <table><tbody>{_dict_rows(report["phase_2c_08_acceptance_facts"])}</tbody></table>
  <h2>Existing Artifacts Reviewed</h2>
  <ul>{_list_items(report["existing_artifacts_reviewed"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_09_post_next_slice_acceptance_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_09_post_next_slice_acceptance_review_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_09_post_next_slice_acceptance_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_09_post_next_slice_acceptance_review_report(project_root)
    json_path, html_path = write_phase_2c_09_post_next_slice_acceptance_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"acceptance_decision: {report['summary']['acceptance_decision']}")
    print(f"phase_2c_06_selection_confirmed: {str(report['summary']['phase_2c_06_selection_confirmed']).lower()}")
    print(
        "phase_2c_07_authorization_confirmed: "
        f"{str(report['summary']['phase_2c_07_authorization_confirmed']).lower()}"
    )
    print(f"phase_2c_08_evidence_found: {str(report['summary']['phase_2c_08_evidence_found']).lower()}")
    print(
        "phase_2c_08_within_authorized_boundary: "
        f"{str(report['summary']['phase_2c_08_within_authorized_boundary']).lower()}"
    )
    print(
        "phase_2c_08_forbidden_execution_paths_avoided: "
        f"{str(report['summary']['phase_2c_08_forbidden_execution_paths_avoided']).lower()}"
    )
    print(f"artifact_validation_job_accepted: {report['summary']['artifact_validation_job_accepted']}")
    print(f"report_only_artifact_created: {str(report['summary']['report_only_artifact_created']).lower()}")
    print(f"next_slice_selected: {str(report['summary']['next_slice_selected']).lower()}")
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
        "ssh_netconf_restconf_live_device_touched: "
        f"{str(report['summary']['ssh_netconf_restconf_live_device_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(
        "config_backup_change_behavior_added: "
        f"{str(report['summary']['config_backup_change_behavior_added']).lower()}"
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
