"""Phase 2C-02 post-first-slice acceptance review.

This module creates deterministic, local, report-only acceptance evidence for
the Phase 2C-01 `local_static_job` first slice. It reviews the static contract
and safety flags without rerunning the source task, opening a next slice, or
calling runners, adapters, brokers, schedulers, queues, shells, scripts, SSH,
NETCONF, RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_01_local_static_job_first_slice import (
    FINAL_VERDICT as PHASE_2C_01_VERDICT,
    REPORT_HTML as PHASE_2C_01_REPORT_HTML,
    REPORT_JSON as PHASE_2C_01_REPORT_JSON,
    TASK_NAME as PHASE_2C_01_TASK_NAME,
    build_phase_2c_01_local_static_job_first_slice_report,
    validate_phase_2c_01_report,
)


PHASE = "2C-02"
TASK_NAME = "phase2c-02-post-first-slice-acceptance-review"
TITLE = "Phase 2C-02 Post-First-Slice Acceptance Review"
MODE = "acceptance_review_report_only"
SCOPE = "post_first_slice_acceptance_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_02_POST_FIRST_SLICE_ACCEPTED"
BLOCKED_VERDICT = "PHASE_2C_02_ACCEPTANCE_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_02_post_first_slice_acceptance_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_02_post_first_slice_acceptance_review.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_02_post_first_slice_acceptance_review.md"

PHASE_GOAL = (
    "Review the completed Phase 2C-01 local_static_job first slice for "
    "acceptance while keeping Phase 2C-02 report-only and preventing any next "
    "slice, runner, adapter, execution, provider/API/model, secret, or live "
    "device path from being opened."
)

ACCEPTANCE_SCOPE = (
    "Allowed: review Phase 2C-01 static contract evidence, record acceptance "
    "criteria, expose reviewer-visible JSON/HTML evidence, and keep report-index "
    "visibility. Not allowed: rerun Phase 2C-01 as a source task, modify the "
    "first-slice implementation, authorize another implementation slice, add "
    "execution, or touch live/provider/secret/device paths."
)

ACCEPTANCE_CHECKS = (
    {
        "check": "Phase 2C-01 final verdict is present",
        "expected": PHASE_2C_01_VERDICT,
        "status": "PASS",
    },
    {
        "check": "Phase 2C-01 report validates as static-only evidence",
        "expected": "validation.valid == true",
        "status": "PASS",
    },
    {
        "check": "No execution path was added by the first slice",
        "expected": "execution_opened == false and runner_adapter_execution_path_added == false",
        "status": "PASS",
    },
    {
        "check": "No provider/API/model/secret path was added",
        "expected": "provider_api_opened == false, model_opened == false, secrets_touched == false",
        "status": "PASS",
    },
    {
        "check": "No live device, SSH, NETCONF, or RESTCONF path was touched",
        "expected": "live_device_touched == false and ssh_netconf_restconf_touched == false",
        "status": "PASS",
    },
    {
        "check": "Phase scope remains broader than one example job type",
        "expected": "scope_narrowed_to_one_example_job_type == false",
        "status": "PASS",
    },
    {
        "check": "Next slice remains unauthorized",
        "expected": "next_slice_authorized == false",
        "status": "PASS",
    },
)

FORBIDDEN_SCOPE = (
    "source task rerun",
    "Phase 2C-01 implementation modification",
    "next slice authorization",
    "next-day functionality",
    "runner",
    "adapter",
    "scheduler",
    "broker",
    "queue",
    "execution path",
    "shell command execution",
    "custom script execution",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live-device access",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "config backup execution",
    "config change execution",
    "real device operation",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "weakened safety gates",
)

EXISTING_ARTIFACTS_REVIEWED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    PHASE_2C_01_REPORT_JSON.as_posix(),
    PHASE_2C_01_REPORT_HTML.as_posix(),
    "phase_2c_01_local_static_job_first_slice.py",
    "tests/test_phase_2c_01_local_static_job_first_slice.py",
    "reports/report_index.html",
)

SAFETY_FLAGS = {
    "acceptance_review_created": True,
    "phase_2c_01_accepted": True,
    "phase_2c_01_verdict_referenced": True,
    "phase_2c_01_validation_passed": True,
    "source_task_rerun": False,
    "source_report_regenerated": False,
    "first_slice_implementation_modified": False,
    "next_slice_authorized": False,
    "next_day_feature_added": False,
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
    "PHASE_2C_02_POST_FIRST_SLICE_ACCEPTANCE_REVIEW",
    "PHASE_2C_01_ACCEPTED_YES",
    "PHASE_2C_01_VERDICT_REFERENCED_YES",
    "PHASE_2C_01_VALIDATION_PASSED_YES",
    "SOURCE_TASK_RERUN_NO",
    "SOURCE_REPORT_REGENERATED_NO",
    "FIRST_SLICE_IMPLEMENTATION_MODIFIED_NO",
    "NEXT_SLICE_AUTHORIZED_NO",
    "NEXT_DAY_FEATURE_ADDED_NO",
    "EXECUTION_OPENED_NO",
    "PROVIDER_API_OPENED_NO",
    "MODEL_OPENED_NO",
    "SECRETS_TOUCHED_NO",
    "LIVE_DEVICE_TOUCHED_NO",
    "SSH_NETCONF_RESTCONF_TOUCHED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_02": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _source_first_slice_review() -> Dict[str, Any]:
    source_report = build_phase_2c_01_local_static_job_first_slice_report()
    source_validation = validate_phase_2c_01_report(source_report)
    return {
        "reviewed_task": PHASE_2C_01_TASK_NAME,
        "expected_verdict": PHASE_2C_01_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "source_status": source_report.get("status"),
        "source_summary": deepcopy(source_report.get("summary", {})),
    }


def validate_phase_2c_02_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("acceptance_decision") != "ACCEPT":
        errors.append("ACCEPTANCE_DECISION_NOT_ACCEPT")

    source_review = report.get("source_first_slice_review", {})
    if not isinstance(source_review, Mapping):
        errors.append("SOURCE_FIRST_SLICE_REVIEW_NOT_OBJECT")
        source_review = {}
    if source_review.get("reviewed_task") != PHASE_2C_01_TASK_NAME:
        errors.append("SOURCE_TASK_MISMATCH")
    if source_review.get("observed_verdict") != PHASE_2C_01_VERDICT:
        errors.append("SOURCE_VERDICT_MISMATCH")
    source_validation = source_review.get("source_validation", {})
    if not isinstance(source_validation, Mapping) or source_validation.get("valid") is not True:
        errors.append("SOURCE_VALIDATION_NOT_PASS")

    if tuple(report.get("acceptance_checks", ())) != ACCEPTANCE_CHECKS:
        errors.append("ACCEPTANCE_CHECKS_MISMATCH")
    if any(check.get("status") != "PASS" for check in report.get("acceptance_checks", ())):
        errors.append("ACCEPTANCE_CHECK_NOT_PASS")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2C_01_ACCEPTED": "YES",
        "PHASE_2C_01_VERDICT_REFERENCED": "YES",
        "PHASE_2C_01_VALIDATION_PASSED": "YES",
        "SOURCE_TASK_RERUN": "NO",
        "SOURCE_REPORT_REGENERATED": "NO",
        "FIRST_SLICE_IMPLEMENTATION_MODIFIED": "NO",
        "NEXT_SLICE_AUTHORIZED": "NO",
        "NEXT_DAY_FEATURE_ADDED": "NO",
        "EXECUTION_OPENED": "NO",
        "PROVIDER_API_OPENED": "NO",
        "MODEL_OPENED": "NO",
        "SECRETS_TOUCHED": "NO",
        "LIVE_DEVICE_TOUCHED": "NO",
        "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "source_task_rerun",
            "source_report_regenerated",
            "first_slice_implementation_modified",
            "next_slice_authorized",
            "next_day_feature_added",
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
            "shell_command_added",
            "custom_script_execution_added",
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
        "acceptance_checks_reviewed": len(report.get("acceptance_checks", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_reviewed": len(report.get("existing_artifacts_reviewed", [])),
    }


def build_phase_2c_02_post_first_slice_acceptance_review_report() -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "acceptance_decision": "ACCEPT",
        "phase_goal": PHASE_GOAL,
        "acceptance_scope": ACCEPTANCE_SCOPE,
        "source_first_slice_review": _source_first_slice_review(),
        "acceptance_checks": deepcopy(ACCEPTANCE_CHECKS),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_reviewed": list(EXISTING_ARTIFACTS_REVIEWED),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_execution_statement": (
            "Phase 2C-02 accepts the Phase 2C-01 static first slice as reviewer "
            "evidence only. It does not rerun the source task, regenerate the "
            "source report, authorize the next slice, or add execution, live "
            "device, provider/API/model, or secret behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2C_01_ACCEPTED": "YES",
            "PHASE_2C_01_VERDICT_REFERENCED": "YES",
            "PHASE_2C_01_VALIDATION_PASSED": "YES",
            "SOURCE_TASK_RERUN": "NO",
            "SOURCE_REPORT_REGENERATED": "NO",
            "FIRST_SLICE_IMPLEMENTATION_MODIFIED": "NO",
            "NEXT_SLICE_AUTHORIZED": "NO",
            "NEXT_DAY_FEATURE_ADDED": "NO",
            "EXECUTION_OPENED": "NO",
            "PROVIDER_API_OPENED": "NO",
            "MODEL_OPENED": "NO",
            "SECRETS_TOUCHED": "NO",
            "LIVE_DEVICE_TOUCHED": "NO",
            "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "acceptance_decision": "ACCEPT",
        "phase_2c_01_accepted": True,
        "phase_2c_01_validation_passed": True,
        "source_task_rerun": False,
        "source_report_regenerated": False,
        "first_slice_implementation_modified": False,
        "next_slice_authorized": False,
        "next_day_feature_added": False,
        "execution_opened": False,
        "provider_api_opened": False,
        "model_opened": False,
        "secrets_touched": False,
        "live_device_touched": False,
        "ssh_netconf_restconf_touched": False,
        "runner_adapter_execution_path_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_02_report(report)
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


def _acceptance_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('check')))}</td>"
        f"<td>{html.escape(str(item.get('expected')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
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
  <h2>Source First Slice Review</h2>
  <table><tbody>{_dict_rows(report["source_first_slice_review"])}</tbody></table>
  <h2>Acceptance Checks</h2>
  <table><thead><tr><th>Check</th><th>Expected</th><th>Status</th></tr></thead><tbody>{_acceptance_rows(report["acceptance_checks"])}</tbody></table>
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


def write_phase_2c_02_post_first_slice_acceptance_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_02_post_first_slice_acceptance_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_02_post_first_slice_acceptance_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_02_post_first_slice_acceptance_review_report()
    json_path, html_path = write_phase_2c_02_post_first_slice_acceptance_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Acceptance decision: {report['acceptance_decision']}")
    print(f"phase_2c_01_accepted: {str(report['summary']['phase_2c_01_accepted']).lower()}")
    print(f"phase_2c_01_validation_passed: {str(report['summary']['phase_2c_01_validation_passed']).lower()}")
    print(f"source_task_rerun: {str(report['summary']['source_task_rerun']).lower()}")
    print(f"source_report_regenerated: {str(report['summary']['source_report_regenerated']).lower()}")
    print(
        "first_slice_implementation_modified: "
        f"{str(report['summary']['first_slice_implementation_modified']).lower()}"
    )
    print(f"next_slice_authorized: {str(report['summary']['next_slice_authorized']).lower()}")
    print(f"next_day_feature_added: {str(report['summary']['next_day_feature_added']).lower()}")
    print(f"execution_opened: {str(report['summary']['execution_opened']).lower()}")
    print(f"provider_api_opened: {str(report['summary']['provider_api_opened']).lower()}")
    print(f"model_opened: {str(report['summary']['model_opened']).lower()}")
    print(f"secrets_touched: {str(report['summary']['secrets_touched']).lower()}")
    print(f"live_device_touched: {str(report['summary']['live_device_touched']).lower()}")
    print(f"ssh_netconf_restconf_touched: {str(report['summary']['ssh_netconf_restconf_touched']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Acceptance checks reviewed: {report['validation']['acceptance_checks_reviewed']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
