"""Phase 2A read-only job runner framework scaffold.

This module is framework-only evidence. It performs deterministic local/mock
classification of fixed job types and never dispatches commands, scripts,
adapters, brokers, device connections, providers, APIs, or model calls.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


PHASE = "Phase 2A"
TASK_NAME = "phase2a-readonly-job-runner-framework"
TITLE = "Phase 2A Read-only Job Runner Framework"
PHASE_STATUS = "PHASE_2A_STARTED"
STATUS_LABEL = "READ_ONLY_JOB_RUNNER_FRAMEWORK_SCAFFOLD_READY"
EXECUTION_MODE = "mock-local-read-only-framework"
REPORT_JSON = Path("reports") / "lab-summary" / "phase2a_readonly_job_runner_framework.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase2a_readonly_job_runner_framework.html"
DOC_PATH = Path("docs") / "phase2a_readonly_job_runner_framework.md"

ALLOWED_JOB_TYPES = frozenset(
    {
        "mock_parse_report",
        "mock_collect_local_evidence",
        "mock_validate_existing_artifact",
    }
)

REJECTED_JOB_TYPES = frozenset(
    {
        "backup_config",
        "config_change",
        "ssh_command",
        "netconf_get",
        "restconf_get",
        "custom_command",
        "custom_script_path",
    }
)

ALLOWED_INPUT_FIELDS = frozenset({"job_type", "artifact_id", "evidence_label"})

FIELD_REJECTION_GROUPS = {
    "ARBITRARY_COMMAND_FIELD_REJECTED": frozenset(
        {"command", "commands", "cmd", "shell", "exec", "argv", "args", "commandtext", "commandline"}
    ),
    "ARBITRARY_SCRIPT_PATH_FIELD_REJECTED": frozenset(
        {"scriptpath", "script_path", "script", "runnerpath", "scriptfile", "artifactpath", "path"}
    ),
    "LIVE_DEVICE_FIELD_REJECTED": frozenset(
        {
            "device",
            "devices",
            "host",
            "hostname",
            "ip",
            "address",
            "target",
            "routerhost",
            "router_host",
            "username",
            "password",
            "secret",
            "token",
            "config",
        }
    ),
    "SSH_FIELD_REJECTED": frozenset(
        {"ssh", "sshenabled", "ssh_enabled", "sshhost", "ssh_host", "sshport", "ssh_port", "privatekey"}
    ),
    "NETCONF_RESTCONF_FIELD_REJECTED": frozenset(
        {
            "netconf",
            "netconfenabled",
            "netconf_enabled",
            "netconfhost",
            "netconf_host",
            "restconf",
            "restconfenabled",
            "restconf_enabled",
            "restconfurl",
            "restconf_url",
            "url",
            "endpoint",
        }
    ),
    "PROVIDER_API_MODEL_FIELD_REJECTED": frozenset(
        {
            "provider",
            "api",
            "apikey",
            "api_key",
            "model",
            "modelname",
            "model_name",
            "prompt",
            "messages",
            "openaiapikey",
            "openai_api_key",
        }
    ),
}

COMPLETION_MARKERS = (
    PHASE_STATUS,
    STATUS_LABEL,
    "MOCK_ONLY_TRUE",
    "LOCAL_ONLY_TRUE",
    "LIVE_DEVICE_ACCESS_FALSE",
    "SSH_ENABLED_FALSE",
    "ARBITRARY_COMMAND_ALLOWED_FALSE",
    "ARBITRARY_SCRIPT_PATH_ALLOWED_FALSE",
    "BACKUP_CONFIG_RUN_ALLOWED_FALSE",
    "CONFIG_CHANGE_ALLOWED_FALSE",
)

def _normalize_field_name(field_name: Any) -> str:
    return str(field_name).replace("-", "").replace("_", "").replace(".", "").lower()


def _base_result(job_type: str, status: str) -> Dict[str, Any]:
    return {
        "status": status,
        "job_type": job_type,
        "phase": PHASE,
        "phase_status": PHASE_STATUS,
        "status_label": STATUS_LABEL,
        "execution_mode": EXECUTION_MODE,
        "read_only": True,
        "local_only": True,
        "mock_only": True,
        "live_device_access": False,
        "ssh_enabled": False,
        "netconf_enabled": False,
        "restconf_enabled": False,
        "arbitrary_command_allowed": False,
        "arbitrary_script_path_allowed": False,
        "config_change_allowed": False,
        "backup_config_run_allowed": False,
        "provider_allowed": False,
        "api_call_allowed": False,
        "external_api_call_allowed": False,
        "model_call_allowed": False,
        "adapter_invocation_allowed": False,
        "broker_invocation_allowed": False,
        "live_execution_allowed": False,
        "completion_markers": list(COMPLETION_MARKERS),
    }


def _rejected_result(job_type: str, rejection_reason: str, rejected_field: Optional[str] = None) -> Dict[str, Any]:
    result = _base_result(job_type, "REJECTED")
    result["rejection_reason"] = rejection_reason
    result["safe_rejection"] = True
    result["mock_result_recorded"] = False
    if rejected_field is not None:
        result["rejected_field"] = rejected_field
    return result


def _field_rejection(job: Mapping[str, Any]) -> Optional[Tuple[str, str]]:
    for field_name in job:
        normalized = _normalize_field_name(field_name)
        for reason, fields in FIELD_REJECTION_GROUPS.items():
            if normalized in fields:
                return reason, str(field_name)
        if field_name not in ALLOWED_INPUT_FIELDS:
            return "UNSUPPORTED_FIELD_REJECTED", str(field_name)
    return None


def run_readonly_job(job: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify one Phase 2A job record without executing anything."""

    job_type_value = job.get("job_type")
    job_type = str(job_type_value) if job_type_value is not None else ""

    field_rejection = _field_rejection(job)
    if field_rejection is not None:
        reason, field_name = field_rejection
        return _rejected_result(job_type or "<missing>", reason, field_name)

    if not job_type:
        return _rejected_result("<missing>", "MISSING_JOB_TYPE")
    if job_type in REJECTED_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_EXPLICITLY_REJECTED")
    if job_type not in ALLOWED_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_NOT_ALLOWLISTED")

    result = _base_result(job_type, "PASS")
    result.update(
        {
            "rejection_reason": None,
            "safe_rejection": False,
            "mock_result_recorded": True,
            "result_record": {
                "record_type": "deterministic_mock_local_evidence",
                "artifact_id": str(job.get("artifact_id", f"phase2a::{job_type}")),
                "evidence_label": str(job.get("evidence_label", "phase2a framework scaffold evidence")),
                "summary": f"{job_type} accepted as fixed mock/local/read-only framework job only.",
            },
        }
    )
    return result


def _default_jobs() -> Iterable[Mapping[str, Any]]:
    yield {"job_type": "mock_parse_report", "artifact_id": "phase2a-mock-report"}
    yield {"job_type": "mock_collect_local_evidence", "artifact_id": "phase2a-local-evidence"}
    yield {"job_type": "mock_validate_existing_artifact", "artifact_id": "phase2a-existing-artifact"}
    for rejected_job_type in sorted(REJECTED_JOB_TYPES):
        yield {"job_type": rejected_job_type}


def _count(results: Iterable[Mapping[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)


def build_phase2a_readonly_job_runner_framework_report() -> Dict[str, Any]:
    results = [run_readonly_job(job) for job in _default_jobs()]
    opened_provider_api_model = any(
        result["provider_allowed"] or result["api_call_allowed"] or result["model_call_allowed"]
        for result in results
    )
    summary = {
        "total_jobs": len(results),
        "allowed_jobs": sum(1 for result in results if result["status"] == "PASS"),
        "rejected_jobs": sum(1 for result in results if result["status"] == "REJECTED"),
        "live_device_access_count": _count(results, "live_device_access"),
        "ssh_enabled_count": _count(results, "ssh_enabled"),
        "netconf_enabled_count": _count(results, "netconf_enabled"),
        "restconf_enabled_count": _count(results, "restconf_enabled"),
        "arbitrary_command_allowed_count": _count(results, "arbitrary_command_allowed"),
        "arbitrary_script_path_allowed_count": _count(results, "arbitrary_script_path_allowed"),
        "backup_config_run_allowed_count": _count(results, "backup_config_run_allowed"),
        "config_change_allowed_count": _count(results, "config_change_allowed"),
        "provider_api_model_open_count": 1 if opened_provider_api_model else 0,
        "adapter_invocation_allowed_count": _count(results, "adapter_invocation_allowed"),
        "broker_invocation_allowed_count": _count(results, "broker_invocation_allowed"),
        "live_execution_allowed_count": _count(results, "live_execution_allowed"),
    }
    return {
        "overall_status": "PASS",
        "status": "PASS",
        "phase": PHASE,
        "phase_status": PHASE_STATUS,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "execution_mode": EXECUTION_MODE,
        "framework_only": True,
        "read_only": True,
        "local_only": True,
        "mock_only": True,
        "live_device_access": False,
        "ssh_enabled": False,
        "netconf_enabled": False,
        "restconf_enabled": False,
        "arbitrary_command_allowed": False,
        "arbitrary_script_path_allowed": False,
        "backup_config_run_allowed": False,
        "config_change_allowed": False,
        "provider_allowed": False,
        "api_call_allowed": False,
        "external_api_call_allowed": False,
        "model_call_allowed": False,
        "allowed_job_types": sorted(ALLOWED_JOB_TYPES),
        "rejected_job_types": sorted(REJECTED_JOB_TYPES),
        "completion_markers": list(COMPLETION_MARKERS),
        "forbidden_capability_markers_absent": True,
        "summary": summary,
        "job_results": results,
    }


def write_phase2a_readonly_job_runner_framework_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase2a_readonly_job_runner_framework_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    summary_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )
    result_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(result['job_type']))}</td>"
        f"<td>{html.escape(str(result['status']))}</td>"
        f"<td>{html.escape(str(result.get('rejection_reason')))}</td>"
        f"<td>{html.escape(str(result['read_only']))}</td>"
        f"<td>{html.escape(str(result['local_only']))}</td>"
        f"<td>{html.escape(str(result['mock_only']))}</td>"
        f"<td>{html.escape(str(result['live_device_access']))}</td>"
        f"<td>{html.escape(str(result['ssh_enabled']))}</td>"
        "</tr>"
        for result in report["job_results"]
    )
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["overall_status"]))} / {html.escape(str(report["status_label"]))}</p>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Job Results</h2>
  <table>
    <thead>
      <tr><th>Job type</th><th>Status</th><th>Rejection reason</th><th>Read only</th><th>Local only</th><th>Mock only</th><th>Live access</th><th>SSH</th></tr>
    </thead>
    <tbody>{result_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase2a_readonly_job_runner_framework(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase2a_readonly_job_runner_framework_report()
    json_path, html_path = write_phase2a_readonly_job_runner_framework_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")

    if relative_to_project_func is None:
        relative = lambda _root, path: str(path)
    else:
        relative = relative_to_project_func

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Execution mode: {EXECUTION_MODE}")
    print(f"Allowed job types: {', '.join(report['allowed_job_types'])}")
    print(f"Rejected job types: {', '.join(report['rejected_job_types'])}")
    print(f"read_only: {str(report['read_only']).lower()}")
    print(f"local_only: {str(report['local_only']).lower()}")
    print(f"mock_only: {str(report['mock_only']).lower()}")
    print(f"live_device_access: {str(report['live_device_access']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"arbitrary_command_allowed: {str(report['arbitrary_command_allowed']).lower()}")
    print(f"arbitrary_script_path_allowed: {str(report['arbitrary_script_path_allowed']).lower()}")
    print(f"backup_config_run_allowed: {str(report['backup_config_run_allowed']).lower()}")
    print(f"config_change_allowed: {str(report['config_change_allowed']).lower()}")
    print(f"provider_allowed: {str(report['provider_allowed']).lower()}")
    print(f"api_call_allowed: {str(report['api_call_allowed']).lower()}")
    print(f"model_call_allowed: {str(report['model_call_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['overall_status'])} {report['status_label']}")
    return 0
