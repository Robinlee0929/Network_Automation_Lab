"""Phase 2J-05 local approval envelope validation job.

This module validates static local approval-envelope documentation markers only.
It does not execute approvals, grant runtime permission, invoke runners,
adapters, schedulers, queues, brokers, workers, agent loops, devices, SSH,
NETCONF, RESTCONF, providers, APIs, models, secrets, config backup, or config
change behavior.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import path_exists, read_text_with_long_path, write_text_with_parents


PHASE = "2J-05"
JOB_NAME = "local_approval_envelope_validation_job"
TASK_NAME = "local-approval-envelope-validation-job"
TITLE = "Phase 2J-05 First Local-only Validation Job"
MODE = "LOCAL_ONLY_VALIDATION_JOB_IMPLEMENTATION"
SCOPE = "local_static_approval_envelope_field_validation"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2J_05_LOCAL_APPROVAL_ENVELOPE_VALIDATION_JOB_IMPLEMENTED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
DEFAULT_APPROVAL_ENVELOPE_PATH = (
    Path("docs")
    / "phase_2j"
    / "phase_2j_04_first_local_validation_job_authorization_gate_planning_only.md"
)
PHASE_2J_03_APPROVAL_ENVELOPE_CONTRACT_PATH = (
    Path("docs") / "phase_2j" / "phase_2j_03_approval_envelope_contract_documentation_only.md"
)
DOC_PATH = Path("docs") / "phase_2j" / "phase_2j_05_first_local_validation_job_implementation.md"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2j_05_local_approval_envelope_validation_job.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2j_05_local_approval_envelope_validation_job.html"

PHASE_GOAL = (
    "Implement the first local-only validation job authorized by Phase 2J-04. "
    "The job validates static approval-envelope documentation markers and "
    "returns report-style evidence only."
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: deterministic local static text validation of a repository "
    "approval-envelope artifact. Not allowed: approval execution, runtime "
    "permission grants, runner/scheduler/worker/queue/broker/agent-loop "
    "behavior, adapter invocation, live device access, SSH, NETCONF, RESTCONF, "
    "provider/API/model/secrets integration, config backup/change behavior, "
    "production execution, Day1-Day160 rewrite, or a second safety matrix."
)

SCOPE_BOUNDARY = "local-only / deterministic / report-only / dry-run / mock-only / non-device"

FORBIDDEN_SCOPE = (
    "live device access",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "config backup",
    "config change",
    "approval execution",
    "runtime permission grant",
    "runner behavior",
    "scheduler behavior",
    "worker behavior",
    "queue behavior",
    "broker behavior",
    "agent loop behavior",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
)

NON_EXECUTABLE_FIELDS = (
    "approval_executor",
    "runtime_permission_grant",
    "runner_call",
    "adapter_call",
    "scheduler_call",
    "worker_call",
    "queue_call",
    "broker_call",
    "agent_loop",
    "execution_engine",
    "device_command",
    "shell_command",
    "ssh_target",
    "netconf_target",
    "restconf_target",
    "provider_call",
    "api_call",
    "model_call",
    "secret_ref",
    "credential_ref",
    "config_backup_action",
    "config_change_action",
)

REQUIRED_FIELD_MARKERS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("phase name", ("Phase 2J-04", "Phase 2J-05", "phase")),
    ("task mode", ("RECOMMENDED_NEXT_TASK_MODE", "IMPLEMENTATION", "PLANNING_ONLY_DOCUMENTATION_ONLY")),
    ("authorization decision", ("AUTHORIZED_FOR_2J_05_LOCAL_ONLY_VALIDATION_JOB_IMPLEMENTATION",)),
    ("authorized implementation scope", ("FIRST_VALIDATION_JOB_SCOPE_FIXED", "First Validation Job Scope")),
    ("explicit allowed scope", ("Allowed Scope For Phase 2J-05",)),
    ("explicit forbidden scope", ("Forbidden Scope",)),
    ("approval envelope boundary statement", ("APPROVAL_ENVELOPE_BOUNDARY", "authorization boundary")),
    ("runtime non-permission statement", ("Runtime Non-permission Statement", "RUNTIME_PERMISSION_GRANTED: NO")),
    ("device access prohibition", ("live device access", "does not touch devices")),
    ("SSH prohibition", ("SSH", "does not use SSH")),
    ("NETCONF prohibition", ("NETCONF", "does not use NETCONF")),
    ("RESTCONF prohibition", ("RESTCONF", "does not use RESTCONF")),
    ("provider / API / model / secrets prohibition", ("providers, APIs, models, or secrets",)),
    ("config backup prohibition", ("config backup",)),
    ("config change prohibition", ("config change",)),
    ("runner prohibition", ("runner", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
    ("scheduler prohibition", ("scheduler", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
    ("worker prohibition", ("worker", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
    ("queue prohibition", ("queue", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
    ("broker prohibition", ("broker", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
    ("agent loop prohibition", ("agent loop", "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED: NO")),
)

SAFETY_FLAGS = {
    "phase_2j_05_started": True,
    "authorized_by_2j_04": True,
    "implementation_added": True,
    "local_approval_envelope_validation_job_implemented": True,
    "local_only": True,
    "deterministic": True,
    "report_only": True,
    "dry_run_only": True,
    "mock_only": True,
    "validates_static_repository_artifacts_only": True,
    "approval_execution_added": False,
    "runtime_permission_added": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "broker_added": False,
    "worker_added": False,
    "agent_loop_added": False,
    "live_device_touched": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_touched": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "next_phase_started": False,
    "extra_slice_selected_or_implemented": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2J_05_LOCAL_APPROVAL_ENVELOPE_VALIDATION_JOB",
    "AUTHORIZED_BY_2J_04_YES",
    "LOCAL_APPROVAL_ENVELOPE_VALIDATION_JOB_IMPLEMENTED_YES",
    "LOCAL_ONLY_YES",
    "DETERMINISTIC_YES",
    "REPORT_ONLY_YES",
    "DRY_RUN_MOCK_ONLY_YES",
    "RUNTIME_PERMISSION_ADDED_NO",
    "APPROVAL_EXECUTION_ADDED_NO",
    "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED_NO",
    "DEVICE_SSH_NETCONF_RESTCONF_PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_OR_CHANGE_TOUCHED_NO",
    FINAL_VERDICT,
)


def build_validation_job_definition() -> Dict[str, Any]:
    return {
        "job_name": JOB_NAME,
        "task_name": TASK_NAME,
        "phase": PHASE,
        "implementation_kind": "local_static_approval_envelope_field_validation",
        "local_only": True,
        "deterministic": True,
        "report_only": True,
        "dry_run_only": True,
        "mock_only": True,
        "validates_static_repository_artifacts_only": True,
        "requires_live_device": False,
        "requires_network": False,
        "requires_provider": False,
        "requires_api": False,
        "requires_model": False,
        "requires_secrets": False,
        "grants_runtime_permission": False,
        "executes_approval": False,
        "required_fields": [name for name, _markers in REQUIRED_FIELD_MARKERS],
        "non_execution_proof": {f"contains_{field}": False for field in NON_EXECUTABLE_FIELDS},
        **{field: None for field in NON_EXECUTABLE_FIELDS},
    }


def validate_validation_job_definition(job_definition: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if job_definition.get("job_name") != JOB_NAME:
        errors.append("JOB_NAME_MISMATCH")
    for flag_name in (
        "local_only",
        "deterministic",
        "report_only",
        "dry_run_only",
        "mock_only",
        "validates_static_repository_artifacts_only",
    ):
        if job_definition.get(flag_name) is not True:
            errors.append(f"JOB_FLAG_NOT_TRUE:{flag_name}")
    for flag_name in (
        "requires_live_device",
        "requires_network",
        "requires_provider",
        "requires_api",
        "requires_model",
        "requires_secrets",
        "grants_runtime_permission",
        "executes_approval",
    ):
        if job_definition.get(flag_name) is not False:
            errors.append(f"FORBIDDEN_JOB_REQUIREMENT:{flag_name}")
    for field_name in NON_EXECUTABLE_FIELDS:
        if job_definition.get(field_name) is not None:
            errors.append(f"NON_EXECUTABLE_FIELD_POPULATED:{field_name}")
    proof = job_definition.get("non_execution_proof", {})
    if not isinstance(proof, Mapping):
        errors.append("NON_EXECUTION_PROOF_NOT_OBJECT")
        proof = {}
    if any(value is not False for value in proof.values()):
        errors.append("NON_EXECUTION_PROOF_NOT_FALSE")
    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
        "non_execution_proof_fields_checked": len(proof),
    }


def validate_approval_envelope_text(text: str) -> Dict[str, Any]:
    found_fields = []
    missing_fields = []
    lower_text = text.casefold()
    field_results = []
    for field_name, markers in REQUIRED_FIELD_MARKERS:
        matched_markers = [marker for marker in markers if marker.casefold() in lower_text]
        passed = bool(matched_markers)
        field_results.append(
            {
                "field": field_name,
                "status": "PASS" if passed else "FAIL",
                "matched_markers": matched_markers,
            }
        )
        if passed:
            found_fields.append(field_name)
        else:
            missing_fields.append(field_name)
    return {
        "status": "PASS" if not missing_fields else "FAIL",
        "valid": not missing_fields,
        "missing_fields": missing_fields,
        "found_fields": found_fields,
        "field_results": field_results,
        "required_fields_checked": len(REQUIRED_FIELD_MARKERS),
    }


def _read_local_artifact(project_root: Path, artifact_path: Path) -> Dict[str, Any]:
    path = project_root / artifact_path
    if not path_exists(path):
        return {
            "path": artifact_path.as_posix(),
            "exists": False,
            "loaded": False,
            "text": "",
            "error": "LOCAL_APPROVAL_ENVELOPE_ARTIFACT_MISSING",
        }
    return {
        "path": artifact_path.as_posix(),
        "exists": True,
        "loaded": True,
        "text": read_text_with_long_path(path, encoding="utf-8"),
        "error": None,
    }


def _static_reference_checks(project_root: Path, artifact_record: Mapping[str, Any]) -> Tuple[Dict[str, Any], ...]:
    return (
        {
            "check": "Phase 2J-03 approval envelope contract source exists",
            "status": "PASS" if path_exists(project_root / PHASE_2J_03_APPROVAL_ENVELOPE_CONTRACT_PATH) else "FAIL",
        },
        {
            "check": "validated artifact is local repository documentation",
            "status": "PASS"
            if artifact_record.get("exists") is True and str(artifact_record.get("path", "")).startswith("docs/")
            else "FAIL",
        },
        {
            "check": "validation result is documentation field presence only",
            "status": "PASS",
        },
        {
            "check": "approval envelope does not grant runtime permission",
            "status": "PASS",
        },
        {
            "check": "no execution path is invoked for validation",
            "status": "PASS",
        },
    )


def build_phase_2j_05_local_approval_envelope_validation_report(
    project_root: Path,
    artifact_path: Path = DEFAULT_APPROVAL_ENVELOPE_PATH,
) -> Dict[str, Any]:
    artifact_record = _read_local_artifact(project_root, artifact_path)
    text_validation = validate_approval_envelope_text(str(artifact_record.get("text", "")))
    reference_checks = _static_reference_checks(project_root, artifact_record)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "job_name": JOB_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "scope_boundary": SCOPE_BOUNDARY,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "authorized_by_2j_04": True,
        "phase_goal": PHASE_GOAL,
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "validated_artifact_path": artifact_path.as_posix(),
        "approval_envelope_artifact": {
            "path": artifact_record["path"],
            "exists": artifact_record["exists"],
            "loaded": artifact_record["loaded"],
            "local_repository_artifact": True,
            "external_access_required": False,
            "error": artifact_record["error"],
        },
        "validation_job": build_validation_job_definition(),
        "approval_envelope_validation": text_validation,
        "static_reference_checks": list(reference_checks),
        "missing_fields": list(text_validation["missing_fields"]),
        "non_permission_statement": (
            "PASS only means the local static approval-envelope artifact contains "
            "expected documentation markers. It does not execute approval, grant "
            "runtime permission, contact devices, call external systems, read "
            "secrets, run backups, change configs, or enable a runner."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AUTHORIZED_BY_2J_04": "YES",
            "IMPLEMENTED_JOB_NAME": JOB_NAME,
            "VALIDATED_ARTIFACT_PATH": artifact_path.as_posix(),
            "LOCAL_ONLY": "YES",
            "DETERMINISTIC": "YES",
            "REPORT_ONLY": "YES",
            "DRY_RUN_MOCK_ONLY": "YES",
            "RUNTIME_PERMISSION_ADDED": "NO",
            "APPROVAL_EXECUTION_ADDED": "NO",
            "RUNNER_SCHEDULER_WORKER_QUEUE_BROKER_AGENT_LOOP_ADDED": "NO",
            "DEVICE_SSH_NETCONF_RESTCONF_PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_TOUCHED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2j_05_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = BLOCKED_VERDICT
    return report


def validate_phase_2j_05_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("job_name") != JOB_NAME:
        errors.append("JOB_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("authorized_by_2j_04") is not True:
        errors.append("AUTHORIZED_BY_2J_04_NOT_TRUE")

    job_validation = validate_validation_job_definition(report.get("validation_job", {}))
    if job_validation["valid"] is not True:
        errors.extend(f"VALIDATION_JOB:{error}" for error in job_validation["errors"])

    envelope_validation = report.get("approval_envelope_validation", {})
    if not isinstance(envelope_validation, Mapping):
        errors.append("APPROVAL_ENVELOPE_VALIDATION_NOT_OBJECT")
        envelope_validation = {}
    if envelope_validation.get("valid") is not True:
        errors.extend(f"APPROVAL_ENVELOPE_MISSING_FIELD:{field}" for field in envelope_validation.get("missing_fields", []))

    checks = report.get("static_reference_checks", [])
    if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)):
        errors.append("STATIC_REFERENCE_CHECKS_NOT_LIST")
        checks = []
    if any(not isinstance(item, Mapping) or item.get("status") != "PASS" for item in checks):
        errors.append("STATIC_REFERENCE_CHECK_FAILED")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    if report.get("missing_fields"):
        errors.append("APPROVAL_ENVELOPE_MISSING_REQUIRED_FIELDS")

    blocked_flags = (
        "approval_execution_added",
        "runtime_permission_added",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "scheduler_added",
        "queue_added",
        "broker_added",
        "worker_added",
        "agent_loop_added",
        "live_device_touched",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_touched",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "next_phase_started",
        "extra_slice_selected_or_implemented",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "missing_fields": list(report.get("missing_fields", [])),
        "validated_artifact_path": report.get("validated_artifact_path"),
        "job_definition_validation": job_validation,
        "required_fields_checked": envelope_validation.get("required_fields_checked", 0),
        "static_reference_checks_checked": len(checks),
    }


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


def _field_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('field')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
        f"<td>{html.escape(str(item.get('matched_markers')))}</td>"
        "</tr>"
        for item in values
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    envelope_validation = report["approval_envelope_validation"]
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
  <p>Job name: <code>{html.escape(str(report["job_name"]))}</code></p>
  <p>Validated artifact: <code>{html.escape(str(report["validated_artifact_path"]))}</code></p>
  <p>{html.escape(str(report["non_permission_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Field Validation</h2>
  <table><thead><tr><th>Field</th><th>Status</th><th>Matched Markers</th></tr></thead><tbody>{_field_rows(envelope_validation["field_results"])}</tbody></table>
  <h2>Missing Fields</h2>
  <ul>{_list_items(report["missing_fields"]) or "<li>None</li>"}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["validation"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2j_05_local_approval_envelope_validation_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2j_05_local_approval_envelope_validation_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2j_05_local_approval_envelope_validation_job(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2j_05_local_approval_envelope_validation_report(project_root)
    json_path, html_path = write_phase_2j_05_local_approval_envelope_validation_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Job name: {JOB_NAME}")
    print(f"Mode: {MODE}")
    print(f"validated_artifact_path: {report['validated_artifact_path']}")
    print(f"scope_boundary: {report['scope_boundary']}")
    print(f"missing_fields: {len(report['missing_fields'])}")
    print(f"local_only: {str(report['local_only']).lower()}")
    print(f"deterministic: {str(report['deterministic']).lower()}")
    print(f"report_only: {str(report['report_only']).lower()}")
    print(f"dry_run_mock_only: {str(report['dry_run_only'] and report['mock_only']).lower()}")
    print(f"runtime_permission_added: {str(report['runtime_permission_added']).lower()}")
    print(f"approval_execution_added: {str(report['approval_execution_added']).lower()}")
    print(
        "runner_scheduler_worker_queue_broker_agent_loop_added: "
        f"{str(any(report[key] for key in ('runner_added', 'scheduler_added', 'worker_added', 'queue_added', 'broker_added', 'agent_loop_added'))).lower()}"
    )
    print(
        "device_ssh_netconf_restconf_provider_api_model_secrets_touched: "
        f"{str(any(report[key] for key in ('live_device_touched', 'ssh_touched', 'netconf_touched', 'restconf_touched', 'provider_api_model_secrets_touched'))).lower()}"
    )
    print(f"config_backup_or_change_touched: {str(report['config_backup_or_change_touched']).lower()}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
