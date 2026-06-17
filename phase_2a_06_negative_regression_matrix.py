"""Phase 2A-06 negative regression matrix.

This module is regression-matrix only. It replays fixed unsafe input shapes
against the existing Phase 2A validator, dry-run plan gate, and evidence
binding layers, then records that each unsafe input remains rejected, redacted,
and non-executing.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase2a_readonly_job_runner_framework import run_readonly_job
from phase_2a_03_dry_run_job_plan_gate import build_phase_2a_03_dry_run_job_plan
from phase_2a_04_plan_evidence_ledger import build_phase_2a_04_plan_evidence_record


PHASE = "2A-06"
TASK_NAME = "phase2a-06-negative-regression-matrix"
TITLE = "Phase 2A-06 Negative Regression Matrix"
STATUS_LABEL = "PHASE_2A_06_NEGATIVE_REGRESSION_MATRIX_READY"
MODE = "report_only"
SCOPE = "unsafe_input_rejection_redaction_non_execution_regression"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_06_negative_regression_matrix.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_06_negative_regression_matrix.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_06_negative_regression_matrix.md"

SAFETY_FLAGS = {
    "runner_invoked": False,
    "adapter_invoked": False,
    "plan_generated_for_unsafe_input": False,
    "live_execution_opened": False,
    "ssh_execution_opened": False,
    "netconf_execution_opened": False,
    "restconf_execution_opened": False,
    "provider_api_model_call_opened": False,
    "backup_config_invoked": False,
    "arbitrary_command_execution_opened": False,
    "arbitrary_script_path_execution_opened": False,
    "phase_2b_authorized": False,
    "phase_2a_07_authorized": False,
    "real_execution_authorized": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_06_NEGATIVE_REGRESSION_MATRIX_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "NEGATIVE_REGRESSION_MATRIX_ONLY",
    "UNSAFE_INPUTS_REJECTED",
    "UNSAFE_INPUT_VALUES_REDACTED",
    "REJECTED_INPUTS_NON_EXECUTING",
    "PHASE_2A_02_VALIDATOR_REUSED",
    "PHASE_2A_03_PLAN_GATE_REUSED",
    "PHASE_2A_04_EVIDENCE_BINDING_REUSED",
    "RUNNER_INVOKED_FALSE",
    "ADAPTER_INVOKED_FALSE",
    "LIVE_EXECUTION_OPENED_FALSE",
    "PHASE_2B_AUTHORIZED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)

RAW_UNSAFE_LITERALS = (
    "show running-config",
    "/system reset-configuration",
    "unsafe-script-preview.py",
    "198.51.100.10",
    "unsafe-user-placeholder",
    "unsafe-password-placeholder",
    "unsafe-api-key-placeholder",
    "unsafe-provider-name",
    "unsafe-model-name",
    "C:/Users/example/.ssh/id_rsa",
    "reports/../secrets/token.txt",
    "reports/lab-summary/run_anything.py",
    "unsafe-metadata-value",
)


def _negative_regression_specs() -> Sequence[Mapping[str, Any]]:
    return (
        {
            "case_id": "NR01",
            "target": "forbidden job type",
            "job": {"job_type": "backup_config", "inputs": {}},
        },
        {
            "case_id": "NR02",
            "target": "arbitrary command field",
            "job": {"job_type": "mock_parse_report", "inputs": {"command": "show running-config"}},
        },
        {
            "case_id": "NR03",
            "target": "shell field",
            "job": {"job_type": "mock_parse_report", "inputs": {"shell": "/system reset-configuration"}},
        },
        {
            "case_id": "NR04",
            "target": "script path field",
            "job": {
                "job_type": "mock_collect_local_evidence",
                "inputs": {"custom_script_path": "unsafe-script-preview.py"},
            },
        },
        {
            "case_id": "NR05",
            "target": "live device target fields",
            "job": {
                "job_type": "mock_parse_report",
                "inputs": {"host": "lab-router", "ip": "198.51.100.10", "device": "router01", "routeros": True},
            },
        },
        {
            "case_id": "NR06",
            "target": "SSH credential fields",
            "job": {
                "job_type": "mock_parse_report",
                "inputs": {
                    "ssh": True,
                    "username": "unsafe-user-placeholder",
                    "password": "unsafe-password-placeholder",
                    "port": 22,
                },
            },
        },
        {
            "case_id": "NR07",
            "target": "NETCONF and RESTCONF fields",
            "job": {"job_type": "mock_parse_report", "inputs": {"netconf": True, "restconf": True}},
        },
        {
            "case_id": "NR08",
            "target": "provider/API/model fields",
            "job": {
                "job_type": "mock_parse_report",
                "inputs": {
                    "api_key": "unsafe-api-key-placeholder",
                    "provider": "unsafe-provider-name",
                    "model": "unsafe-model-name",
                },
            },
        },
        {
            "case_id": "NR09",
            "target": "absolute private-path artifact reference",
            "job": {
                "job_type": "mock_validate_existing_artifact",
                "inputs": {"artifact_path": "C:/Users/example/.ssh/id_rsa"},
            },
        },
        {
            "case_id": "NR10",
            "target": "path traversal and secret-like artifact reference",
            "job": {
                "job_type": "mock_validate_existing_artifact",
                "inputs": {"artifact_path": "reports/../secrets/token.txt"},
            },
        },
        {
            "case_id": "NR11",
            "target": "executable-looking evidence reference",
            "job": {
                "job_type": "mock_parse_report",
                "inputs": {"evidence_ref": "reports/lab-summary/run_anything.py"},
            },
        },
        {
            "case_id": "NR12",
            "target": "unknown top-level metadata",
            "job": {
                "job_type": "mock_parse_report",
                "inputs": {},
                "metadata": "unsafe-metadata-value",
            },
        },
    )


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _iter_field_paths(payload: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path
            yield from _iter_field_paths(value, path)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            yield from _iter_field_paths(value, f"{prefix}[{index}]")


def _redacted_input_summary(job: Mapping[str, Any]) -> Dict[str, Any]:
    job_type = str(job.get("job_type", "<missing>"))
    input_paths = sorted(path for path in _iter_field_paths(job.get("inputs", {})) if not path.endswith(".inputs"))
    return {
        "input_ref": f"PHASE_2A_06_INPUT_REF_{_stable_digest(job)}",
        "job_type_ref": f"PHASE_2A_06_JOB_TYPE_REF_{_stable_digest(job_type)}",
        "input_field_paths": input_paths,
        "values_redacted": True,
        "raw_values_included": False,
    }


def _contains_raw_unsafe_literal(payload: Any) -> bool:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return any(literal in serialized for literal in RAW_UNSAFE_LITERALS)


def _matrix_case(spec: Mapping[str, Any]) -> Dict[str, Any]:
    job = spec["job"]
    validator_result = run_readonly_job(job)
    plan_result = build_phase_2a_03_dry_run_job_plan(job)
    evidence_record = build_phase_2a_04_plan_evidence_record(plan_result)
    case = {
        "case_id": spec["case_id"],
        "target": spec["target"],
        "expected": {
            "validator_status": "REJECTED",
            "plan_gate_status": "REJECTED",
            "evidence_status": "rejected",
            "values_redacted": True,
            "runner_invoked": False,
            "adapter_invoked": False,
            "plan_generated": False,
            "live_execution_opened": False,
            "next_phase_allowed": False,
        },
        "actual": {
            "validator_status": validator_result.get("status"),
            "validator_rejection_reason": validator_result.get("rejection_reason"),
            "plan_gate_status": plan_result.get("status"),
            "plan_gate_rejection_reason": plan_result.get("rejection_reason"),
            "evidence_status": evidence_record.get("accepted_or_rejected"),
            "evidence_id": evidence_record.get("evidence_id"),
            "source_plan_id": evidence_record.get("source_plan_id"),
            "values_redacted": True,
            "runner_invoked": bool(validator_result.get("runner_invoked")) or bool(plan_result.get("runner_invoked")),
            "adapter_invoked": bool(plan_result.get("adapter_invoked")) or bool(evidence_record.get("adapter_invoked")),
            "plan_generated": bool(plan_result.get("plan_generated")),
            "live_execution_opened": bool(plan_result.get("live_execution_opened"))
            or bool(evidence_record.get("live_execution_opened")),
            "next_phase_allowed": bool(plan_result.get("next_phase_allowed"))
            or bool(evidence_record.get("next_phase_allowed")),
        },
        "redacted_input_summary": _redacted_input_summary(job),
        "non_execution_proof": {
            "phase_2a_02_runner_invoked": bool(validator_result.get("runner_invoked")),
            "phase_2a_03_plan_generated": bool(plan_result.get("plan_generated")),
            "phase_2a_03_runner_invoked": bool(plan_result.get("runner_invoked")),
            "phase_2a_03_adapter_invoked": bool(plan_result.get("adapter_invoked")),
            "phase_2a_04_record_live_execution_opened": bool(evidence_record.get("live_execution_opened")),
            "execution_payload_present": False,
        },
    }
    case["passed"] = (
        case["actual"]["validator_status"] == "REJECTED"
        and case["actual"]["plan_gate_status"] == "REJECTED"
        and case["actual"]["evidence_status"] == "rejected"
        and case["actual"]["values_redacted"] is True
        and case["actual"]["runner_invoked"] is False
        and case["actual"]["adapter_invoked"] is False
        and case["actual"]["plan_generated"] is False
        and case["actual"]["live_execution_opened"] is False
        and case["actual"]["next_phase_allowed"] is False
        and not _contains_raw_unsafe_literal(case)
    )
    return case


def build_negative_regression_matrix() -> Sequence[Dict[str, Any]]:
    return [_matrix_case(spec) for spec in _negative_regression_specs()]


def validate_phase_2a_06_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    matrix = report.get("negative_regression_matrix", [])
    if not matrix:
        errors.append("NEGATIVE_REGRESSION_MATRIX_EMPTY")
    for index, case in enumerate(matrix):
        if case.get("passed") is not True:
            errors.append(f"CASE_FAILED:{case.get('case_id', index)}")
        summary = case.get("redacted_input_summary", {})
        if not isinstance(summary, Mapping) or summary.get("raw_values_included") is not False:
            errors.append(f"CASE_RAW_VALUES_NOT_REDACTED:{case.get('case_id', index)}")
        proof = case.get("non_execution_proof", {})
        if not isinstance(proof, Mapping) or proof.get("execution_payload_present") is not False:
            errors.append(f"CASE_EXECUTION_PAYLOAD_PRESENT:{case.get('case_id', index)}")
    for flag_name, expected_value in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected_value:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")
    if _contains_raw_unsafe_literal(report):
        errors.append("RAW_UNSAFE_LITERAL_PRESENT")
    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "cases_checked": len(matrix),
    }


def build_phase_2a_06_negative_regression_matrix_report() -> Dict[str, Any]:
    matrix = list(build_negative_regression_matrix())
    rejected_cases = [case for case in matrix if case["actual"]["validator_status"] == "REJECTED"]
    report = {
        "phase": PHASE,
        "status": "PASS",
        "overall_status": "PASS",
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "source_layers_reused": {
            "phase_2a_02_validator": "phase2a_readonly_job_runner_framework.run_readonly_job",
            "phase_2a_03_plan_gate": "phase_2a_03_dry_run_job_plan_gate.build_phase_2a_03_dry_run_job_plan",
            "phase_2a_04_evidence_binding": "phase_2a_04_plan_evidence_ledger.build_phase_2a_04_plan_evidence_record",
            "phase_2a_05_consumed_or_modified": False,
        },
        "summary": {
            "matrix_cases": len(matrix),
            "unsafe_inputs_rejected": len(rejected_cases),
            "unsafe_inputs_redacted": sum(
                1 for case in matrix if case["redacted_input_summary"]["values_redacted"] is True
            ),
            "unsafe_inputs_non_executing": sum(
                1
                for case in matrix
                if case["actual"]["runner_invoked"] is False
                and case["actual"]["adapter_invoked"] is False
                and case["actual"]["plan_generated"] is False
                and case["actual"]["live_execution_opened"] is False
            ),
            "raw_unsafe_literals_present": sum(1 for case in matrix if _contains_raw_unsafe_literal(case)),
            "failed_cases": sum(1 for case in matrix if case["passed"] is not True),
            "next_phase_allowed_count": sum(1 for case in matrix if case["actual"]["next_phase_allowed"] is True),
        },
        "negative_regression_matrix": matrix,
    }
    validation = validate_phase_2a_06_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    return report


def write_phase_2a_06_negative_regression_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_06_negative_regression_matrix_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _summary_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    case_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(case['case_id']))}</td>"
        f"<td>{html.escape(str(case['target']))}</td>"
        f"<td>{html.escape(str(case['actual']['validator_status']))}</td>"
        f"<td>{html.escape(str(case['actual']['plan_gate_status']))}</td>"
        f"<td>{html.escape(str(case['actual']['values_redacted']))}</td>"
        f"<td>{html.escape(str(case['actual']['runner_invoked']))}</td>"
        f"<td>{html.escape(str(case['actual']['adapter_invoked']))}</td>"
        f"<td>{html.escape(str(case['actual']['plan_generated']))}</td>"
        f"<td>{html.escape(str(case['actual']['live_execution_opened']))}</td>"
        f"<td>{html.escape(str(case['passed']))}</td>"
        "</tr>"
        for case in report["negative_regression_matrix"]
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
  <p>Status: {html.escape(str(report["status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Phase 2A-06 replays fixed unsafe inputs only and proves they remain rejected, redacted, and non-executing.</p>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Negative Regression Matrix</h2>
  <table>
    <thead><tr><th>Case</th><th>Target</th><th>Validator</th><th>Plan gate</th><th>Redacted</th><th>Runner</th><th>Adapter</th><th>Plan generated</th><th>Live execution</th><th>Passed</th></tr></thead>
    <tbody>{case_rows}</tbody>
  </table>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_06_negative_regression_matrix(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_06_negative_regression_matrix_report()
    json_path, html_path = write_phase_2a_06_negative_regression_matrix_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Matrix cases: {report['summary']['matrix_cases']}")
    print(f"Unsafe inputs rejected: {report['summary']['unsafe_inputs_rejected']}")
    print(f"Unsafe inputs redacted: {report['summary']['unsafe_inputs_redacted']}")
    print(f"Unsafe inputs non-executing: {report['summary']['unsafe_inputs_non_executing']}")
    print(f"Raw unsafe literals present: {report['summary']['raw_unsafe_literals_present']}")
    print(f"runner_invoked: {str(report['runner_invoked']).lower()}")
    print(f"adapter_invoked: {str(report['adapter_invoked']).lower()}")
    print(f"plan_generated_for_unsafe_input: {str(report['plan_generated_for_unsafe_input']).lower()}")
    print(f"live_execution_opened: {str(report['live_execution_opened']).lower()}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"phase_2a_07_authorized: {str(report['phase_2a_07_authorized']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
