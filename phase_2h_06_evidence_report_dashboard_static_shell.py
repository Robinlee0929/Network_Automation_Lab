"""Phase 2H-06 static Evidence / Report Dashboard shell.

This module builds a deterministic, local-only dashboard shell model and
renders static HTML. It does not read live data, connect to runners or
adapters, invoke execution paths, call providers/APIs/models, load secrets,
or use SSH, NETCONF, RESTCONF, queues, schedulers, workers, or agent loops.
"""

from __future__ import annotations

from html import escape
from typing import Any, Dict, Mapping, Sequence, Tuple


PHASE = "2H-06"
TASK_NAME = "phase2h-06-evidence-report-dashboard-static-shell"
TITLE = "Phase 2H-06 Evidence / Report Dashboard Static Shell"
MODE = "implementation_static_local_deterministic_read_only_dashboard_shell"
SCOPE = "static_evidence_report_dashboard_shell"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
FINAL_VERDICT = "PHASE_2H_06_STATIC_DASHBOARD_SHELL_READY"
DOC_PATH = "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.md"
HTML_PATH = "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html"

BOUNDARY_NOTICE = (
    "Static/read-only/no execution boundary: this dashboard shell is local, "
    "deterministic, and non-executing. It connects to no live data source, "
    "runner, adapter, execution system, provider, API, model, secret store, "
    "SSH, NETCONF, or RESTCONF."
)

EXPECTED_SECTION_TITLES = (
    "Evidence summary placeholder",
    "Report summary placeholder",
    "Artifact status placeholder",
    "Empty state",
    "Boundary notice",
)

FORBIDDEN_SCOPE_STATUS = {
    "live_data_connected": False,
    "runner_connected": False,
    "adapter_connected": False,
    "execution_path_added": False,
    "ssh_netconf_restconf_added": False,
    "provider_api_model_secrets_added": False,
    "config_backup_change_added": False,
    "queue_scheduler_worker_agent_loop_added": False,
    "day1_day160_rewritten": False,
    "second_safety_matrix_added": False,
    "production_execution_path_added": False,
    "next_phase_started": False,
    "extra_slice_selected_or_implemented": False,
}


def build_dashboard_shell_model() -> Dict[str, Any]:
    """Return the deterministic static dashboard shell model."""

    sections = (
        {
            "id": "evidence-summary",
            "title": "Evidence summary placeholder",
            "status": "EMPTY_STATE",
            "body": "No live evidence is connected. Static evidence links may be added only as committed local references in a later authorized slice.",
        },
        {
            "id": "report-summary",
            "title": "Report summary placeholder",
            "status": "EMPTY_STATE",
            "body": "No report refresh is performed. This shell is a passive reviewer navigation surface only.",
        },
        {
            "id": "artifact-status",
            "title": "Artifact status placeholder",
            "status": "REVIEW_ONLY",
            "body": "Artifact status is reserved for local deterministic committed evidence references, not runtime collection.",
        },
        {
            "id": "empty-state",
            "title": "Empty state",
            "status": "NO_LIVE_DATA",
            "body": "No live data source is attached. The dashboard shell is ready for static review only.",
        },
        {
            "id": "boundary-notice",
            "title": "Boundary notice",
            "status": "LOCKED",
            "body": BOUNDARY_NOTICE,
        },
    )
    model: Dict[str, Any] = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS_PASS,
        "final_verdict": FINAL_VERDICT,
        "local_only": True,
        "deterministic": True,
        "static_only": True,
        "read_only": True,
        "non_executing": True,
        "requires_external_dependencies": False,
        "external_dependency_names": (),
        "sections": sections,
        "boundary_notice": BOUNDARY_NOTICE,
        "forbidden_scope_status": dict(FORBIDDEN_SCOPE_STATUS),
    }
    model["validation"] = validate_dashboard_shell_model(model)
    return model


def validate_dashboard_shell_model(model: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate that the shell model remains static and non-executing."""

    errors = []
    if model.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if model.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if model.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if model.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")

    for flag in ("local_only", "deterministic", "static_only", "read_only", "non_executing"):
        if model.get(flag) is not True:
            errors.append(f"STATIC_BOUNDARY_FLAG_MISMATCH:{flag}")

    if model.get("requires_external_dependencies") is not False:
        errors.append("EXTERNAL_DEPENDENCIES_REQUIRED")
    if tuple(model.get("external_dependency_names", ())) != ():
        errors.append("EXTERNAL_DEPENDENCY_NAMES_PRESENT")

    sections = model.get("sections", ())
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes, bytearray)):
        errors.append("SECTIONS_NOT_SEQUENCE")
        sections = ()
    section_titles = tuple(section.get("title") for section in sections if isinstance(section, Mapping))
    for expected in EXPECTED_SECTION_TITLES:
        if expected not in section_titles:
            errors.append(f"EXPECTED_SECTION_MISSING:{expected}")

    if model.get("boundary_notice") != BOUNDARY_NOTICE:
        errors.append("BOUNDARY_NOTICE_MISMATCH")

    forbidden_scope_status = model.get("forbidden_scope_status")
    if not isinstance(forbidden_scope_status, Mapping):
        errors.append("FORBIDDEN_SCOPE_STATUS_NOT_OBJECT")
        forbidden_scope_status = {}
    for key, expected in FORBIDDEN_SCOPE_STATUS.items():
        if forbidden_scope_status.get(key) is not expected:
            errors.append(f"FORBIDDEN_SCOPE_STATUS_MISMATCH:{key}")
    if any(value is True for value in forbidden_scope_status.values()):
        errors.append("FORBIDDEN_SCOPE_TOUCHED")

    return {
        "valid": not errors,
        "status": STATUS_PASS if not errors else STATUS_FAIL,
        "errors": errors,
        "section_count": len(sections),
        "live_connector_required": False,
        "runner_required": False,
        "adapter_required": False,
        "execution_path_required": False,
        "external_access_attempted": False,
    }


def render_dashboard_shell_html(model: Mapping[str, Any] | None = None) -> str:
    """Render deterministic static HTML for local reviewer reading."""

    shell_model = build_dashboard_shell_model() if model is None else model
    validation = validate_dashboard_shell_model(shell_model)
    if not validation["valid"]:
        raise ValueError(";".join(validation["errors"]))

    sections = "\n".join(_render_section(section) for section in shell_model["sections"])
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <title>Phase 2H-06 Evidence / Report Dashboard Static Shell</title>\n"
        "  <style>\n"
        "    body { font-family: Arial, sans-serif; margin: 0; color: #17202a; background: #f6f8fb; }\n"
        "    main { max-width: 1080px; margin: 0 auto; padding: 32px 20px 48px; }\n"
        "    header { border-bottom: 2px solid #d6dee8; margin-bottom: 24px; padding-bottom: 18px; }\n"
        "    h1 { font-size: 30px; margin: 0 0 10px; }\n"
        "    .notice { background: #fff7d6; border: 1px solid #d9ba45; padding: 14px; margin: 18px 0; }\n"
        "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }\n"
        "    section { background: #ffffff; border: 1px solid #d6dee8; padding: 16px; }\n"
        "    h2 { font-size: 18px; margin: 0 0 8px; }\n"
        "    .status { font-size: 12px; font-weight: bold; letter-spacing: .04em; color: #375a7f; }\n"
        "    p { line-height: 1.45; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <main>\n"
        "    <header>\n"
        f"      <h1>{escape(str(shell_model['title']))}</h1>\n"
        "      <p>Static local dashboard shell for reviewer-visible evidence and report orientation.</p>\n"
        f"      <div class=\"notice\">{escape(str(shell_model['boundary_notice']))}</div>\n"
        "    </header>\n"
        "    <div class=\"grid\">\n"
        f"{sections}\n"
        "    </div>\n"
        "  </main>\n"
        "</body>\n"
        "</html>\n"
    )


def build_phase_2h_06_dashboard_shell_summary() -> Dict[str, Any]:
    """Build a deterministic summary for tests and reviewer evidence."""

    model = build_dashboard_shell_model()
    html = render_dashboard_shell_html(model)
    return {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS_PASS,
        "final_verdict": FINAL_VERDICT,
        "doc_path": DOC_PATH,
        "html_path": HTML_PATH,
        "section_titles": tuple(section["title"] for section in model["sections"]),
        "boundary_notice": BOUNDARY_NOTICE,
        "html_length": len(html),
        "validation": validate_dashboard_shell_model(model),
        "forbidden_scope_status": dict(FORBIDDEN_SCOPE_STATUS),
        "non_execution_statement": (
            "Phase 2H-06 provides a committed static dashboard shell only. "
            "It requires no live connector, runner, adapter, execution path, "
            "provider, API, model, secret store, SSH, NETCONF, RESTCONF, queue, "
            "scheduler, worker, or agent loop."
        ),
    }


def _render_section(section: Mapping[str, Any]) -> str:
    return (
        "      <section>\n"
        f"        <div class=\"status\">{escape(str(section['status']))}</div>\n"
        f"        <h2>{escape(str(section['title']))}</h2>\n"
        f"        <p>{escape(str(section['body']))}</p>\n"
        "      </section>"
    )
