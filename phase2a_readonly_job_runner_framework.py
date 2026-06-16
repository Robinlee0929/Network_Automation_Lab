"""Phase 2A-02 job spec contract validator and negative input matrix.

This module is validator/evidence-only. It uses positive allowlisted schemas
as the primary safety boundary, records denylist/negative-matrix evidence, and
only invokes deterministic mock/local review-only handling after validation
passes.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple


PHASE = "Phase 2A"
TASK_NAME = "phase2a-readonly-job-runner-framework"
TITLE = "Phase 2A-02 Job Spec Contract Validator + Negative Input Matrix"
PHASE_STATUS = "PHASE_2A_STARTED"
STATUS_LABEL = "JOB_SPEC_CONTRACT_VALIDATOR_READY"
EXECUTION_MODE = "mock-local-review-only-validator"
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

FORBIDDEN_JOB_TYPES = frozenset(
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

REJECTED_JOB_TYPES = FORBIDDEN_JOB_TYPES

ALLOWED_TOP_LEVEL_FIELDS = frozenset({"job_type", "inputs"})

ALLOWED_INPUT_FIELDS_BY_JOB_TYPE = {
    "mock_parse_report": frozenset({"report_path", "evidence_ref"}),
    "mock_collect_local_evidence": frozenset({"artifact_path", "evidence_ref"}),
    "mock_validate_existing_artifact": frozenset({"artifact_path", "report_path", "evidence_ref"}),
}

ARTIFACT_PATH_FIELDS = frozenset({"artifact_path", "report_path"})
ARTIFACT_STYLE_FIELDS = frozenset({"artifact_path", "report_path", "evidence_ref"})
APPROVED_ARTIFACT_PATH_ROOTS = ("reports", "docs", "fixtures", "summary")
SAFE_ARTIFACT_EXTENSIONS = frozenset({".json", ".html", ".md", ".txt", ".csv", ".log"})
EXECUTABLE_OR_SCRIPT_EXTENSIONS = frozenset(
    {".bat", ".cmd", ".com", ".exe", ".jar", ".js", ".mjs", ".ps1", ".py", ".sh", ".ts", ".vbs"}
)
SECRET_PATH_MARKERS = frozenset(
    {
        ".env",
        "api_key",
        "apikey",
        "credential",
        "credentials",
        "id_ed25519",
        "id_rsa",
        "key",
        "keys",
        "password",
        "private_key",
        "secret",
        "secrets",
        "token",
    }
)
SECRET_OR_KEY_EXTENSIONS = frozenset({".cer", ".crt", ".der", ".key", ".p12", ".pem", ".pfx", ".pub"})

DANGEROUS_FIELD_REJECTION_GROUPS = {
    "ARBITRARY_COMMAND_FIELD_REJECTED": frozenset({"command", "cmd", "shell"}),
    "ARBITRARY_SCRIPT_PATH_FIELD_REJECTED": frozenset(
        {"scriptpath", "customscriptpath", "executablepath"}
    ),
    "LIVE_DEVICE_FIELD_REJECTED": frozenset({"host", "ip", "device", "routeros"}),
    "SSH_FIELD_REJECTED": frozenset({"ssh", "username", "password"}),
    "NETCONF_RESTCONF_FIELD_REJECTED": frozenset({"netconf", "restconf"}),
    "PROVIDER_API_MODEL_FIELD_REJECTED": frozenset({"apikey", "provider", "model"}),
}

DANGEROUS_FIELDS_COVERED = tuple(
    sorted(
        {
            "api_key",
            "cmd",
            "command",
            "custom_script_path",
            "device",
            "executable_path",
            "host",
            "ip",
            "model",
            "netconf",
            "password",
            "port:22",
            "provider",
            "restconf",
            "routeros",
            "scriptPath",
            "script_path",
            "shell",
            "ssh",
            "username",
        }
    )
)

COMPLETION_MARKERS = (
    PHASE_STATUS,
    STATUS_LABEL,
    "ALLOWLIST_SCHEMA_PRIMARY_TRUE",
    "DENYLIST_EVIDENCE_ONLY_TRUE",
    "NEGATIVE_INPUT_MATRIX_RECORDED_TRUE",
    "INVALID_JOB_SPECS_REJECTED_BEFORE_RUNNER_TRUE",
    "RUNNER_INVOKED_FALSE_FOR_REJECTIONS_TRUE",
    "SAFE_ARTIFACT_PATHS_ONLY_TRUE",
    "NEXT_PHASE_ALLOWED_FALSE",
    "MOCK_ONLY_TRUE",
    "LOCAL_ONLY_TRUE",
    "LIVE_DEVICE_ACCESS_FALSE",
    "SSH_ENABLED_FALSE",
    "NETCONF_ENABLED_FALSE",
    "RESTCONF_ENABLED_FALSE",
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
        "contract_validator": True,
        "allowlist_schema_primary": True,
        "denylist_evidence_only": True,
        "read_only": True,
        "local_only": True,
        "mock_only": True,
        "review_only": True,
        "next_phase_allowed": False,
        "live_device_access": False,
        "ssh_enabled": False,
        "netconf_enabled": False,
        "restconf_enabled": False,
        "routeros_enabled": False,
        "arbitrary_command_allowed": False,
        "arbitrary_shell_allowed": False,
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
        "command_runner_added": False,
        "shell_runner_added": False,
        "script_path_runner_added": False,
        "real_adapter_integration_added": False,
        "runner_invoked": False,
        "completion_markers": list(COMPLETION_MARKERS),
    }


def _rejected_result(
    job_type: str,
    rejection_reason: str,
    rejected_field: Optional[str] = None,
    rejected_value: Optional[Any] = None,
) -> Dict[str, Any]:
    result = _base_result(job_type, "REJECTED")
    result["valid"] = False
    result["rejection_reason"] = rejection_reason
    result["safe_rejection"] = True
    result["mock_result_recorded"] = False
    result["runner_invoked"] = False
    if rejected_field is not None:
        result["rejected_field"] = rejected_field
    if rejected_value is not None:
        result["rejected_value"] = str(rejected_value)
    return result


def _accepted_validation_result(job_type: str, inputs: Mapping[str, Any]) -> Dict[str, Any]:
    result = _base_result(job_type, "VALIDATED")
    result["valid"] = True
    result["rejection_reason"] = None
    result["safe_rejection"] = False
    result["mock_result_recorded"] = False
    result["runner_invoked"] = False
    result["validated_inputs"] = dict(inputs)
    return result


def _iter_fields(payload: Any, prefix: str = "") -> Iterable[Tuple[str, Any, str]]:
    if isinstance(payload, Mapping):
        for field_name, value in payload.items():
            display = f"{prefix}.{field_name}" if prefix else str(field_name)
            yield str(field_name), value, display
            yield from _iter_fields(value, display)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            yield from _iter_fields(value, f"{prefix}[{index}]")


def _dangerous_field_rejection(job: Mapping[str, Any]) -> Optional[Tuple[str, str, Any]]:
    for field_name, value, display_name in _iter_fields(job):
        normalized = _normalize_field_name(field_name)
        if normalized == "port" and str(value) == "22":
            return "SSH_FIELD_REJECTED", display_name, value
        for reason, fields in DANGEROUS_FIELD_REJECTION_GROUPS.items():
            if normalized in fields:
                return reason, display_name, value
    return None


def _is_absolute_artifact_path(path_value: str) -> bool:
    return (
        path_value.startswith("/")
        or path_value.startswith("\\")
        or re.match(r"^[A-Za-z]:[\\/]", path_value) is not None
        or "://" in path_value
    )


def _path_has_secret_marker(parts: Sequence[str], suffix: str) -> bool:
    if suffix in SECRET_OR_KEY_EXTENSIONS:
        return True
    for part in parts:
        lowered = part.lower()
        if lowered in SECRET_PATH_MARKERS:
            return True
        if lowered.endswith(".env"):
            return True
        for marker in SECRET_PATH_MARKERS:
            if marker != "key" and marker in lowered:
                return True
    return False


def validate_artifact_path(field_name: str, value: Any) -> Optional[Tuple[str, str, Any]]:
    if not isinstance(value, str) or not value.strip():
        return "ARTIFACT_PATH_INVALID_TYPE_REJECTED", field_name, value

    raw_path = value.strip()
    if _is_absolute_artifact_path(raw_path):
        return "ARTIFACT_PATH_ABSOLUTE_REJECTED", field_name, raw_path

    normalized_path = raw_path.replace("\\", "/")
    parts = tuple(part for part in normalized_path.split("/") if part)
    if not parts:
        return "ARTIFACT_PATH_INVALID_TYPE_REJECTED", field_name, raw_path
    if any(part == ".." for part in parts):
        return "ARTIFACT_PATH_TRAVERSAL_REJECTED", field_name, raw_path
    if parts[0] not in APPROVED_ARTIFACT_PATH_ROOTS:
        return "ARTIFACT_PATH_OUTSIDE_APPROVED_DIR_REJECTED", field_name, raw_path

    suffix = Path(parts[-1]).suffix.lower()
    if _path_has_secret_marker(parts, suffix):
        return "ARTIFACT_PATH_SECRET_LIKE_REJECTED", field_name, raw_path
    if suffix in EXECUTABLE_OR_SCRIPT_EXTENSIONS:
        return "ARTIFACT_PATH_EXECUTABLE_OR_SCRIPT_REJECTED", field_name, raw_path
    if suffix and suffix not in SAFE_ARTIFACT_EXTENSIONS:
        return "ARTIFACT_PATH_UNSUPPORTED_EXTENSION_REJECTED", field_name, raw_path

    return None


def validate_evidence_ref(field_name: str, value: Any) -> Optional[Tuple[str, str, Any]]:
    if not isinstance(value, str) or not value.strip():
        return "EVIDENCE_REF_INVALID_TYPE_REJECTED", field_name, value

    raw_ref = value.strip()
    if "/" in raw_ref or "\\" in raw_ref or _is_absolute_artifact_path(raw_ref):
        return validate_artifact_path(field_name, raw_ref)

    suffix = Path(raw_ref).suffix.lower()
    if ".." in raw_ref:
        return "EVIDENCE_REF_TRAVERSAL_REJECTED", field_name, raw_ref
    if _path_has_secret_marker((raw_ref,), suffix):
        return "EVIDENCE_REF_SECRET_LIKE_REJECTED", field_name, raw_ref
    if suffix in EXECUTABLE_OR_SCRIPT_EXTENSIONS:
        return "EVIDENCE_REF_EXECUTABLE_OR_SCRIPT_REJECTED", field_name, raw_ref
    return None


def validate_job_spec(job: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a Phase 2A job spec before any runner path can be invoked."""

    if not isinstance(job, Mapping):
        return _rejected_result("<invalid>", "JOB_SPEC_NOT_MAPPING")

    job_type_value = job.get("job_type")
    job_type = str(job_type_value) if job_type_value is not None else ""

    dangerous = _dangerous_field_rejection(job)
    if dangerous is not None:
        reason, field_name, value = dangerous
        return _rejected_result(job_type or "<missing>", reason, field_name, value)

    for field_name in job:
        if field_name not in ALLOWED_TOP_LEVEL_FIELDS:
            return _rejected_result(job_type or "<missing>", "UNKNOWN_TOP_LEVEL_FIELD_REJECTED", str(field_name))

    if not job_type:
        return _rejected_result("<missing>", "MISSING_JOB_TYPE")
    if job_type in FORBIDDEN_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_EXPLICITLY_FORBIDDEN")
    if job_type not in ALLOWED_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_NOT_ALLOWLISTED")

    inputs = job.get("inputs", {})
    if inputs is None:
        inputs = {}
    if not isinstance(inputs, Mapping):
        return _rejected_result(job_type, "INPUTS_NOT_MAPPING_REJECTED", "inputs", inputs)

    allowed_input_fields = ALLOWED_INPUT_FIELDS_BY_JOB_TYPE[job_type]
    for field_name, value in inputs.items():
        if field_name not in allowed_input_fields:
            return _rejected_result(job_type, "UNKNOWN_INPUT_FIELD_REJECTED", f"inputs.{field_name}", value)
        if field_name in ARTIFACT_PATH_FIELDS:
            path_rejection = validate_artifact_path(f"inputs.{field_name}", value)
            if path_rejection is not None:
                reason, rejected_field, rejected_value = path_rejection
                return _rejected_result(job_type, reason, rejected_field, rejected_value)
        if field_name == "evidence_ref":
            evidence_ref_rejection = validate_evidence_ref(f"inputs.{field_name}", value)
            if evidence_ref_rejection is not None:
                reason, rejected_field, rejected_value = evidence_ref_rejection
                return _rejected_result(job_type, reason, rejected_field, rejected_value)

    return _accepted_validation_result(job_type, inputs)


def _mock_local_review_only_job_handler(validation: Mapping[str, Any]) -> Dict[str, Any]:
    job_type = str(validation["job_type"])
    inputs = validation.get("validated_inputs", {})
    result = _base_result(job_type, "PASS")
    result.update(
        {
            "valid": True,
            "rejection_reason": None,
            "safe_rejection": False,
            "runner_invoked": True,
            "mock_result_recorded": True,
            "result_record": {
                "record_type": "deterministic_mock_local_review_only_evidence",
                "artifact_path": inputs.get("artifact_path"),
                "report_path": inputs.get("report_path"),
                "evidence_ref": inputs.get("evidence_ref", f"phase2a::{job_type}"),
                "summary": f"{job_type} accepted after allowlist schema validation for mock/local review only.",
            },
        }
    )
    return result


def run_readonly_job(job: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one Phase 2A job spec, then invoke only mock/local handling if valid."""

    validation = validate_job_spec(job)
    if validation["status"] == "REJECTED":
        return validation
    return _mock_local_review_only_job_handler(validation)


def _matrix_case(case_id: str, description: str, job: Mapping[str, Any], expected_status: str) -> Dict[str, Any]:
    result = run_readonly_job(job)
    passed = result["status"] == expected_status
    if expected_status == "REJECTED":
        passed = passed and result["runner_invoked"] is False
    return {
        "case_id": case_id,
        "description": description,
        "expected_status": expected_status,
        "actual_status": result["status"],
        "passed": passed,
        "runner_invoked": result["runner_invoked"],
        "rejection_reason": result.get("rejection_reason"),
        "rejected_field": result.get("rejected_field"),
        "job_type": result["job_type"],
    }


def build_negative_input_matrix() -> Sequence[Dict[str, Any]]:
    cases = [
        (
            "M01",
            "safe allowed job type passes",
            {
                "job_type": "mock_validate_existing_artifact",
                "inputs": {"artifact_path": "reports/lab-summary/sample.json", "evidence_ref": "phase2a-safe"},
            },
            "PASS",
        ),
        ("M02", "unknown job type fails", {"job_type": "unknown_job", "inputs": {}}, "REJECTED"),
        ("M03", "forbidden job type fails", {"job_type": "backup_config", "inputs": {}}, "REJECTED"),
        (
            "M04",
            "allowed job type with command fails",
            {"job_type": "mock_parse_report", "inputs": {"command": "/system print"}},
            "REJECTED",
        ),
        (
            "M05",
            "allowed job type with cmd fails",
            {"job_type": "mock_parse_report", "inputs": {"cmd": "show run"}},
            "REJECTED",
        ),
        (
            "M06",
            "allowed job type with shell fails",
            {"job_type": "mock_parse_report", "inputs": {"shell": "powershell"}},
            "REJECTED",
        ),
        (
            "M07",
            "allowed job type with scriptPath fails",
            {"job_type": "mock_collect_local_evidence", "inputs": {"scriptPath": "scripts/run.py"}},
            "REJECTED",
        ),
        (
            "M08",
            "allowed job type with script_path fails",
            {"job_type": "mock_collect_local_evidence", "inputs": {"script_path": "scripts/run.py"}},
            "REJECTED",
        ),
        (
            "M09",
            "allowed job type with custom_script_path fails",
            {"job_type": "mock_collect_local_evidence", "inputs": {"custom_script_path": "scripts/run.py"}},
            "REJECTED",
        ),
        (
            "M10",
            "allowed job type with host/ip/device/routeros fails",
            {
                "job_type": "mock_parse_report",
                "inputs": {"host": "router01", "ip": "192.0.2.1", "device": "r1", "routeros": True},
            },
            "REJECTED",
        ),
        (
            "M11",
            "allowed job type with ssh/username/password/port 22 fails",
            {
                "job_type": "mock_parse_report",
                "inputs": {"ssh": True, "username": "admin", "password": "redacted", "port": 22},
            },
            "REJECTED",
        ),
        (
            "M12",
            "allowed job type with netconf/restconf fails",
            {"job_type": "mock_parse_report", "inputs": {"netconf": True, "restconf": True}},
            "REJECTED",
        ),
        (
            "M13",
            "allowed job type with api_key/provider/model fails",
            {"job_type": "mock_parse_report", "inputs": {"api_key": "redacted", "provider": "none", "model": "none"}},
            "REJECTED",
        ),
        (
            "M14",
            "allowed job type with unknown extra field fails",
            {"job_type": "mock_parse_report", "inputs": {"report_path": "reports/lab-summary/sample.json", "extra": True}},
            "REJECTED",
        ),
        (
            "M15",
            "absolute artifact path fails",
            {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "C:/Users/example/report.json"}},
            "REJECTED",
        ),
        (
            "M16",
            "path traversal artifact path fails",
            {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/../config.json"}},
            "REJECTED",
        ),
        (
            "M17",
            "secret-like artifact path fails",
            {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/secrets/api_key.json"}},
            "REJECTED",
        ),
        (
            "M18",
            "rejected specs do not invoke the runner",
            {"job_type": "mock_parse_report", "inputs": {"shell": "cmd.exe"}},
            "REJECTED",
        ),
    ]
    return [_matrix_case(case_id, description, job, expected_status) for case_id, description, job, expected_status in cases]


def _default_jobs() -> Iterable[Mapping[str, Any]]:
    yield {
        "job_type": "mock_parse_report",
        "inputs": {"report_path": "reports/lab-summary/phase2a_readonly_job_runner_framework.json"},
    }
    yield {
        "job_type": "mock_collect_local_evidence",
        "inputs": {"artifact_path": "docs/phase2a_readonly_job_runner_framework.md"},
    }
    yield {
        "job_type": "mock_validate_existing_artifact",
        "inputs": {"artifact_path": "fixtures/day127_ai_reviewer_summary.example.json"},
    }
    for forbidden_job_type in sorted(FORBIDDEN_JOB_TYPES):
        yield {"job_type": forbidden_job_type, "inputs": {}}


def _count(results: Iterable[Mapping[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)


def build_phase2a_readonly_job_runner_framework_report() -> Dict[str, Any]:
    results = [run_readonly_job(job) for job in _default_jobs()]
    matrix = list(build_negative_input_matrix())
    rejected_results = [result for result in results if result["status"] == "REJECTED"]
    rejected_matrix = [case for case in matrix if case["expected_status"] == "REJECTED"]
    all_rejections_skip_runner = all(result["runner_invoked"] is False for result in rejected_results) and all(
        case["runner_invoked"] is False for case in rejected_matrix
    )
    opened_provider_api_model = any(
        result["provider_allowed"] or result["api_call_allowed"] or result["model_call_allowed"]
        for result in results
    )
    summary = {
        "total_jobs": len(results),
        "allowed_jobs": sum(1 for result in results if result["status"] == "PASS"),
        "rejected_jobs": len(rejected_results),
        "negative_matrix_cases": len(matrix),
        "negative_matrix_passed": sum(1 for case in matrix if case["passed"] is True),
        "negative_matrix_failed": sum(1 for case in matrix if case["passed"] is False),
        "rejected_specs_runner_invoked_count": sum(1 for result in rejected_results if result["runner_invoked"] is True),
        "negative_matrix_rejected_runner_invoked_count": sum(
            1 for case in rejected_matrix if case["runner_invoked"] is True
        ),
        "all_rejections_runner_invoked_false": all_rejections_skip_runner,
        "live_device_access_count": _count(results, "live_device_access"),
        "ssh_enabled_count": _count(results, "ssh_enabled"),
        "netconf_enabled_count": _count(results, "netconf_enabled"),
        "restconf_enabled_count": _count(results, "restconf_enabled"),
        "arbitrary_command_allowed_count": _count(results, "arbitrary_command_allowed"),
        "arbitrary_shell_allowed_count": _count(results, "arbitrary_shell_allowed"),
        "arbitrary_script_path_allowed_count": _count(results, "arbitrary_script_path_allowed"),
        "backup_config_run_allowed_count": _count(results, "backup_config_run_allowed"),
        "config_change_allowed_count": _count(results, "config_change_allowed"),
        "provider_api_model_open_count": 1 if opened_provider_api_model else 0,
        "adapter_invocation_allowed_count": _count(results, "adapter_invocation_allowed"),
        "broker_invocation_allowed_count": _count(results, "broker_invocation_allowed"),
        "live_execution_allowed_count": _count(results, "live_execution_allowed"),
    }
    overall_status = "PASS" if summary["negative_matrix_failed"] == 0 and all_rejections_skip_runner else "FAIL"
    return {
        "overall_status": overall_status,
        "status": overall_status,
        "phase": PHASE,
        "phase_status": PHASE_STATUS,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "execution_mode": EXECUTION_MODE,
        "framework_only": True,
        "validator_contract_only": True,
        "negative_input_matrix_evidence": True,
        "allowlist_schema_primary": True,
        "denylist_evidence_only": True,
        "read_only": True,
        "local_only": True,
        "mock_only": True,
        "review_only": True,
        "next_phase_allowed": False,
        "live_device_access": False,
        "ssh_enabled": False,
        "netconf_enabled": False,
        "restconf_enabled": False,
        "routeros_enabled": False,
        "arbitrary_command_allowed": False,
        "arbitrary_shell_allowed": False,
        "arbitrary_script_path_allowed": False,
        "backup_config_run_allowed": False,
        "config_change_allowed": False,
        "provider_allowed": False,
        "api_call_allowed": False,
        "external_api_call_allowed": False,
        "model_call_allowed": False,
        "allowed_job_types": sorted(ALLOWED_JOB_TYPES),
        "forbidden_job_types": sorted(FORBIDDEN_JOB_TYPES),
        "rejected_job_types": sorted(FORBIDDEN_JOB_TYPES),
        "allowed_top_level_fields": sorted(ALLOWED_TOP_LEVEL_FIELDS),
        "allowed_input_fields_by_job_type": {
            job_type: sorted(fields) for job_type, fields in ALLOWED_INPUT_FIELDS_BY_JOB_TYPE.items()
        },
        "dangerous_fields_covered": list(DANGEROUS_FIELDS_COVERED),
        "path_safety_rules": {
            "artifact_style_fields": sorted(ARTIFACT_STYLE_FIELDS),
            "path_validated_fields": sorted(ARTIFACT_PATH_FIELDS),
            "evidence_ref_rejects_path_traversal_secrets_and_scripts": True,
            "approved_repo_local_roots": list(APPROVED_ARTIFACT_PATH_ROOTS),
            "reject_absolute_paths": True,
            "reject_path_traversal": True,
            "reject_paths_outside_approved_roots": True,
            "reject_secret_env_credential_key_paths": True,
            "reject_executable_or_script_paths": True,
            "safe_extensions": sorted(SAFE_ARTIFACT_EXTENSIONS),
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "forbidden_capability_markers_absent": True,
        "summary": summary,
        "job_results": results,
        "negative_input_matrix": matrix,
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
        f"<td>{html.escape(str(result['runner_invoked']))}</td>"
        f"<td>{html.escape(str(result['read_only']))}</td>"
        f"<td>{html.escape(str(result['local_only']))}</td>"
        f"<td>{html.escape(str(result['mock_only']))}</td>"
        f"<td>{html.escape(str(result['live_device_access']))}</td>"
        f"<td>{html.escape(str(result['ssh_enabled']))}</td>"
        "</tr>"
        for result in report["job_results"]
    )
    matrix_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(case['case_id']))}</td>"
        f"<td>{html.escape(str(case['description']))}</td>"
        f"<td>{html.escape(str(case['expected_status']))}</td>"
        f"<td>{html.escape(str(case['actual_status']))}</td>"
        f"<td>{html.escape(str(case['runner_invoked']))}</td>"
        f"<td>{html.escape(str(case.get('rejection_reason')))}</td>"
        f"<td>{html.escape(str(case['passed']))}</td>"
        "</tr>"
        for case in report["negative_input_matrix"]
    )
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    allowed_jobs = "".join(f"<li>{html.escape(job_type)}</li>" for job_type in report["allowed_job_types"])
    forbidden_jobs = "".join(f"<li>{html.escape(job_type)}</li>" for job_type in report["forbidden_job_types"])
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
    code {{ background: #f3f6fa; padding: 1px 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["overall_status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Allowlist schema is the primary safety boundary. Denylist checks and negative cases are evidence.</p>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
  <h2>Allowed Job Types</h2>
  <ul>{allowed_jobs}</ul>
  <h2>Forbidden Job Types</h2>
  <ul>{forbidden_jobs}</ul>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Job Results</h2>
  <table>
    <thead>
      <tr><th>Job type</th><th>Status</th><th>Rejection reason</th><th>Runner invoked</th><th>Read only</th><th>Local only</th><th>Mock only</th><th>Live access</th><th>SSH</th></tr>
    </thead>
    <tbody>{result_rows}</tbody>
  </table>
  <h2>Negative Input Matrix</h2>
  <table>
    <thead>
      <tr><th>Case</th><th>Description</th><th>Expected</th><th>Actual</th><th>Runner invoked</th><th>Rejection reason</th><th>Passed</th></tr>
    </thead>
    <tbody>{matrix_rows}</tbody>
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
    print(f"Forbidden job types: {', '.join(report['forbidden_job_types'])}")
    print(f"Allowlist schema primary: {str(report['allowlist_schema_primary']).lower()}")
    print(f"Denylist evidence only: {str(report['denylist_evidence_only']).lower()}")
    print(f"Negative matrix cases: {report['summary']['negative_matrix_cases']}")
    print(f"Rejected specs runner_invoked=false: {str(report['summary']['all_rejections_runner_invoked_false']).lower()}")
    print(f"read_only: {str(report['read_only']).lower()}")
    print(f"local_only: {str(report['local_only']).lower()}")
    print(f"mock_only: {str(report['mock_only']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"live_device_access: {str(report['live_device_access']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"netconf_enabled: {str(report['netconf_enabled']).lower()}")
    print(f"restconf_enabled: {str(report['restconf_enabled']).lower()}")
    print(f"arbitrary_command_allowed: {str(report['arbitrary_command_allowed']).lower()}")
    print(f"arbitrary_shell_allowed: {str(report['arbitrary_shell_allowed']).lower()}")
    print(f"arbitrary_script_path_allowed: {str(report['arbitrary_script_path_allowed']).lower()}")
    print(f"backup_config_run_allowed: {str(report['backup_config_run_allowed']).lower()}")
    print(f"config_change_allowed: {str(report['config_change_allowed']).lower()}")
    print(f"provider_allowed: {str(report['provider_allowed']).lower()}")
    print(f"api_call_allowed: {str(report['api_call_allowed']).lower()}")
    print(f"model_call_allowed: {str(report['model_call_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['overall_status'])} {report['status_label']}")
    return 0 if report["overall_status"] == "PASS" else 1
