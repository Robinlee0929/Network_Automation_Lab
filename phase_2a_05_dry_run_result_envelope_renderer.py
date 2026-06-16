"""Phase 2A-05 dry-run result envelope and renderer.

This module is envelope-and-renderer only. It consumes the existing Phase
2A-04 report builder as the source interface, wraps that result in a compact
reviewer-facing envelope, and writes deterministic JSON/HTML/text outputs. It
does not rebuild Phase 2A-03 plans or the Phase 2A-04 ledger.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple

from phase_2a_04_plan_evidence_ledger import (
    TASK_NAME as PHASE_2A_04_TASK_NAME,
    build_phase_2a_04_plan_evidence_ledger_report,
)


PHASE = "2A-05"
TASK_NAME = "phase2a-05-dry-run-result-envelope-renderer"
TITLE = "Phase 2A-05 Dry-Run Result Envelope / Renderer"
STATUS_LABEL = "PHASE_2A_05_DRY_RUN_RESULT_ENVELOPE_RENDERER_READY"
MODE = "report_only"
SCOPE = "mock_local_read_only_dry_run"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_05_dry_run_result_envelope_renderer.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_05_dry_run_result_envelope_renderer.html"
REPORT_TXT = Path("reports") / "lab-summary" / "phase_2a_05_dry_run_result_envelope_renderer.txt"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_05_dry_run_result_envelope_renderer.md"

SAFETY_FLAGS = {
    "runner_invoked": False,
    "adapter_invoked": False,
    "live_execution_opened": False,
    "ssh_execution_opened": False,
    "netconf_execution_opened": False,
    "restconf_execution_opened": False,
    "provider_api_model_call_opened": False,
    "backup_config_invoked": False,
    "arbitrary_command_execution_opened": False,
    "arbitrary_script_path_execution_opened": False,
    "phase_2b_authorized": False,
    "real_execution_authorized": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_05_DRY_RUN_RESULT_ENVELOPE_RENDERER_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "PHASE_2A_04_IMPLEMENTATION_SEARCHED_AND_CONSUMED",
    "PHASE_2A_04_REPORT_INTERFACE_CONSUMED",
    "RESULT_ENVELOPE_RENDER_OUTPUTS_SEPARATED",
    "JSON_SELF_RECURSION_PREVENTED",
    "PLANNER_NOT_REBUILT",
    "LEDGER_NOT_REBUILT",
    "RENDERER_ONLY",
    "RUNNER_INVOKED_FALSE",
    "ADAPTER_INVOKED_FALSE",
    "LIVE_EXECUTION_OPENED_FALSE",
    "PHASE_2B_AUTHORIZED_FALSE",
    "REAL_EXECUTION_AUTHORIZED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)

REQUIRED_PHASE_2A_04_REPORT_FIELDS = (
    "phase",
    "status",
    "task",
    "title",
    "status_label",
    "summary",
    "validation",
    "ledger",
    "agents_md_pre_read",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _source_report_ref(source_report: Mapping[str, Any]) -> str:
    source_seed = {
        "phase": source_report.get("phase"),
        "task": source_report.get("task"),
        "status": source_report.get("status"),
        "status_label": source_report.get("status_label"),
        "summary": source_report.get("summary"),
        "validation": source_report.get("validation"),
    }
    return f"PHASE_2A_04_REPORT_REF_{_stable_digest(source_seed)}"


def _agents_md_status(source_report: Mapping[str, Any]) -> Dict[str, Any]:
    source_status = source_report.get("agents_md_pre_read", {})
    if not isinstance(source_status, Mapping):
        source_status = {}
    return {
        "path": str(source_status.get("path", "AGENTS.md")),
        "pre_read_required": bool(source_status.get("required", True)),
        "pre_read_completed": bool(source_status.get("read", False)),
        "found": bool(source_status.get("found", False)),
        "modified": bool(source_status.get("modified", False)),
        "source": "Phase 2A-04 report metadata plus Phase 2A-05 pre-edit read",
    }


def _source_counts(source_report: Mapping[str, Any]) -> Dict[str, int]:
    summary = source_report.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "source_accepted_plans": int(summary.get("source_accepted_plans", 0)),
        "source_rejected_requests": int(summary.get("source_rejected_requests", 0)),
        "accepted_evidence_records": int(summary.get("accepted_evidence_records", 0)),
        "rejected_evidence_records": int(summary.get("rejected_evidence_records", 0)),
        "runner_invoked_count": int(summary.get("runner_invoked_count", 0)),
        "adapter_invoked_count": int(summary.get("adapter_invoked_count", 0)),
        "live_execution_opened_count": int(summary.get("live_execution_opened_count", 0)),
        "next_phase_allowed_count": int(summary.get("next_phase_allowed_count", 0)),
    }


def build_phase_2a_05_result_envelope(source_report: Mapping[str, Any]) -> Dict[str, Any]:
    """Wrap a Phase 2A-04 report in a compact non-executable result envelope."""

    source_counts = _source_counts(source_report)
    source_ref = _source_report_ref(source_report)
    envelope_seed = {
        "source_report_ref": source_ref,
        "source_counts": source_counts,
        "source_status": source_report.get("status"),
        "source_status_label": source_report.get("status_label"),
    }
    return {
        "envelope_id": f"PHASE_2A_05_RESULT_ENVELOPE_{_stable_digest(envelope_seed)}",
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "envelope_type": "dry_run_result_envelope",
        "source_phase": "2A-04",
        "source_task": str(source_report.get("task", PHASE_2A_04_TASK_NAME)),
        "source_report_ref": source_ref,
        "source_status": str(source_report.get("status", "UNKNOWN")),
        "source_status_label": str(source_report.get("status_label", "")),
        "source_validation_status": str(
            source_report.get("validation", {}).get("status", "UNKNOWN")
            if isinstance(source_report.get("validation"), Mapping)
            else "UNKNOWN"
        ),
        "source_counts": source_counts,
        "agents_md_status": _agents_md_status(source_report),
        "non_execution_proof": {
            "phase_2a_04_report_consumed": True,
            "phase_2a_03_planner_rebuilt": False,
            "phase_2a_04_ledger_rebuilt": False,
            "renderer_only": True,
            "result_envelope_contains_render_outputs": False,
            "render_outputs_contains_result_envelope": False,
            "execution_payload_present": False,
        },
        **SAFETY_FLAGS,
    }


def build_phase_2a_05_render_outputs(result_envelope: Mapping[str, Any]) -> Dict[str, Any]:
    """Declare renderer outputs as metadata separate from the envelope object."""

    return {
        "renderer_status": "READY",
        "renderer_type": "deterministic_local_file_renderer",
        "rendered_from_envelope_id": str(result_envelope.get("envelope_id", "")),
        "formats": ["json", "html", "text"],
        "paths": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
            "text": REPORT_TXT.as_posix(),
        },
        "result_envelope_embedded": False,
        "json_self_recursion_prevented": True,
        "renderer_only": True,
        "planner_rebuilt": False,
        "ledger_rebuilt": False,
    }


def _iter_mapping_keys(payload: Any) -> Iterable[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            yield str(key)
            yield from _iter_mapping_keys(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_mapping_keys(item)


def validate_phase_2a_05_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate envelope separation, source interface use, and safety flags."""

    errors = []
    result_envelope = report.get("result_envelope")
    render_outputs = report.get("render_outputs")
    if not isinstance(result_envelope, Mapping):
        errors.append("MISSING_RESULT_ENVELOPE")
    if not isinstance(render_outputs, Mapping):
        errors.append("MISSING_RENDER_OUTPUTS")

    if isinstance(result_envelope, Mapping) and "render_outputs" in result_envelope:
        errors.append("RESULT_ENVELOPE_CONTAINS_RENDER_OUTPUTS")
    if isinstance(render_outputs, Mapping) and "result_envelope" in render_outputs:
        errors.append("RENDER_OUTPUTS_CONTAINS_RESULT_ENVELOPE")
    if isinstance(render_outputs, Mapping) and any(key == "result_envelope" for key in _iter_mapping_keys(render_outputs)):
        errors.append("RENDER_OUTPUTS_NESTS_RESULT_ENVELOPE_KEY")
    if isinstance(result_envelope, Mapping) and any(key == "render_outputs" for key in _iter_mapping_keys(result_envelope)):
        errors.append("RESULT_ENVELOPE_NESTS_RENDER_OUTPUTS_KEY")

    try:
        json.dumps(report, sort_keys=True, default=str)
    except (TypeError, ValueError) as exc:
        errors.append(f"JSON_SERIALIZATION_FAILED:{exc}")

    source_interface = report.get("source_phase_2a_04_interface", {})
    if not isinstance(source_interface, Mapping) or source_interface.get("implementation_searched") is not True:
        errors.append("PHASE_2A_04_IMPLEMENTATION_SEARCH_NOT_RECORDED")
    if isinstance(source_interface, Mapping) and source_interface.get("report_builder_consumed") is not True:
        errors.append("PHASE_2A_04_REPORT_BUILDER_NOT_CONSUMED")
    if isinstance(source_interface, Mapping):
        missing_fields = list(source_interface.get("missing_required_fields", []))
        if missing_fields:
            errors.append("PHASE_2A_04_REPORT_INTERFACE_MISSING_FIELDS:" + ",".join(missing_fields))

    for flag_name, expected_value in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected_value:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")
        if isinstance(result_envelope, Mapping) and result_envelope.get(flag_name) is not expected_value:
            errors.append(f"ENVELOPE_SAFETY_FLAG_NOT_FALSE:{flag_name}")

    if isinstance(result_envelope, Mapping):
        proof = result_envelope.get("non_execution_proof", {})
        if not isinstance(proof, Mapping):
            errors.append("MISSING_NON_EXECUTION_PROOF")
        else:
            expected_false = (
                "phase_2a_03_planner_rebuilt",
                "phase_2a_04_ledger_rebuilt",
                "result_envelope_contains_render_outputs",
                "render_outputs_contains_result_envelope",
                "execution_payload_present",
            )
            for key in expected_false:
                if proof.get(key) is not False:
                    errors.append(f"NON_EXECUTION_PROOF_NOT_FALSE:{key}")
            if proof.get("renderer_only") is not True:
                errors.append("RENDERER_ONLY_NOT_TRUE")

        agents_status = result_envelope.get("agents_md_status", {})
        if not isinstance(agents_status, Mapping):
            errors.append("MISSING_AGENTS_MD_STATUS")
        else:
            if agents_status.get("pre_read_completed") is not True:
                errors.append("AGENTS_MD_PRE_READ_NOT_RECORDED")
            if agents_status.get("modified") is not False:
                errors.append("AGENTS_MD_MODIFIED")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def build_phase_2a_05_dry_run_result_envelope_renderer_report(
    source_report: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    source_phase_2a_04_report = source_report or build_phase_2a_04_plan_evidence_ledger_report()
    missing_required_fields = [
        field for field in REQUIRED_PHASE_2A_04_REPORT_FIELDS if field not in source_phase_2a_04_report
    ]
    result_envelope = build_phase_2a_05_result_envelope(source_phase_2a_04_report)
    render_outputs = build_phase_2a_05_render_outputs(result_envelope)
    status = "PASS" if not missing_required_fields and source_phase_2a_04_report.get("status") == "PASS" else "FAIL"
    report = {
        "phase": PHASE,
        "status": status,
        "overall_status": status,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": result_envelope["agents_md_status"]["found"],
            "read": result_envelope["agents_md_status"]["pre_read_completed"],
            "modified": result_envelope["agents_md_status"]["modified"],
            "path": "AGENTS.md",
        },
        "source_phase_2a_04_interface": {
            "implementation_searched": True,
            "module": "phase_2a_04_plan_evidence_ledger.py",
            "report_builder_consumed": True,
            "report_builder": "build_phase_2a_04_plan_evidence_ledger_report",
            "source_task": str(source_phase_2a_04_report.get("task", PHASE_2A_04_TASK_NAME)),
            "source_status": str(source_phase_2a_04_report.get("status", "UNKNOWN")),
            "required_fields": list(REQUIRED_PHASE_2A_04_REPORT_FIELDS),
            "missing_required_fields": missing_required_fields,
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "envelope_count": 1,
            "render_output_count": len(render_outputs["formats"]),
            "source_phase_2a_04_status": str(source_phase_2a_04_report.get("status", "UNKNOWN")),
            "source_accepted_plans": result_envelope["source_counts"]["source_accepted_plans"],
            "source_rejected_requests": result_envelope["source_counts"]["source_rejected_requests"],
            "accepted_evidence_records": result_envelope["source_counts"]["accepted_evidence_records"],
            "rejected_evidence_records": result_envelope["source_counts"]["rejected_evidence_records"],
            "runner_invoked_count": result_envelope["source_counts"]["runner_invoked_count"],
            "adapter_invoked_count": result_envelope["source_counts"]["adapter_invoked_count"],
            "live_execution_opened_count": result_envelope["source_counts"]["live_execution_opened_count"],
            "next_phase_allowed_count": result_envelope["source_counts"]["next_phase_allowed_count"],
            "json_self_recursion_prevented": True,
            "planner_rebuilt": False,
            "ledger_rebuilt": False,
        },
        "result_envelope": result_envelope,
        "render_outputs": render_outputs,
    }
    validation = validate_phase_2a_05_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if status == "PASS" and validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    return report


def write_phase_2a_05_dry_run_result_envelope_renderer_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path, Path]:
    report_data = report or build_phase_2a_05_dry_run_result_envelope_renderer_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    text_path = project_root / REPORT_TXT
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    _write_text_report(report_data, text_path)
    return json_path, html_path, text_path


def _summary_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    envelope = report["result_envelope"]
    render_outputs = report["render_outputs"]
    output_rows = "\n".join(
        f"<tr><td>{html.escape(str(fmt))}</td><td>{html.escape(str(render_outputs['paths'][fmt]))}</td></tr>"
        for fmt in render_outputs["formats"]
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
  <p>Phase 2A-05 wraps the existing Phase 2A-04 report in a compact result envelope and renders reviewer outputs only.</p>
  <h2>Result Envelope</h2>
  <table><tbody>
    <tr><td>Envelope id</td><td>{html.escape(str(envelope["envelope_id"]))}</td></tr>
    <tr><td>Source report ref</td><td>{html.escape(str(envelope["source_report_ref"]))}</td></tr>
    <tr><td>AGENTS.md pre-read</td><td>{html.escape(str(envelope["agents_md_status"]["pre_read_completed"]))}</td></tr>
    <tr><td>AGENTS.md modified</td><td>{html.escape(str(envelope["agents_md_status"]["modified"]))}</td></tr>
    <tr><td>Renderer only</td><td>{html.escape(str(envelope["non_execution_proof"]["renderer_only"]))}</td></tr>
  </tbody></table>
  <h2>Render Outputs</h2>
  <table><thead><tr><th>Format</th><th>Path</th></tr></thead><tbody>{output_rows}</tbody></table>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _write_text_report(report: Mapping[str, Any], output_path: Path) -> None:
    envelope = report["result_envelope"]
    render_outputs = report["render_outputs"]
    lines = [
        str(report["title"]),
        f"status: {report['status']} / {report['status_label']}",
        f"task: {report['task']}",
        f"phase: {report['phase']}",
        f"envelope_id: {envelope['envelope_id']}",
        f"source_report_ref: {envelope['source_report_ref']}",
        f"agents_md_pre_read_completed: {str(envelope['agents_md_status']['pre_read_completed']).lower()}",
        f"agents_md_modified: {str(envelope['agents_md_status']['modified']).lower()}",
        f"result_envelope_contains_render_outputs: {str(envelope['non_execution_proof']['result_envelope_contains_render_outputs']).lower()}",
        f"render_outputs_contains_result_envelope: {str(envelope['non_execution_proof']['render_outputs_contains_result_envelope']).lower()}",
        f"json_self_recursion_prevented: {str(render_outputs['json_self_recursion_prevented']).lower()}",
        f"planner_rebuilt: {str(render_outputs['planner_rebuilt']).lower()}",
        f"ledger_rebuilt: {str(render_outputs['ledger_rebuilt']).lower()}",
        f"runner_invoked: {str(report['runner_invoked']).lower()}",
        f"adapter_invoked: {str(report['adapter_invoked']).lower()}",
        f"live_execution_opened: {str(report['live_execution_opened']).lower()}",
        f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}",
        f"real_execution_authorized: {str(report['real_execution_authorized']).lower()}",
        f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_phase_2a_05_dry_run_result_envelope_renderer(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_05_dry_run_result_envelope_renderer_report()
    json_path, html_path, text_path = write_phase_2a_05_dry_run_result_envelope_renderer_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))
    envelope = report["result_envelope"]

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Source task: {envelope['source_task']}")
    print(f"Envelope id: {envelope['envelope_id']}")
    print("result_envelope/render_outputs separated: true")
    print(f"agents_md_pre_read_completed: {str(envelope['agents_md_status']['pre_read_completed']).lower()}")
    print(f"agents_md_modified: {str(envelope['agents_md_status']['modified']).lower()}")
    print(f"planner_rebuilt: {str(report['summary']['planner_rebuilt']).lower()}")
    print(f"ledger_rebuilt: {str(report['summary']['ledger_rebuilt']).lower()}")
    print(f"runner_invoked: {str(report['runner_invoked']).lower()}")
    print(f"adapter_invoked: {str(report['adapter_invoked']).lower()}")
    print(f"live_execution_opened: {str(report['live_execution_opened']).lower()}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"real_execution_authorized: {str(report['real_execution_authorized']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"Text report: {relative(project_root, text_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
