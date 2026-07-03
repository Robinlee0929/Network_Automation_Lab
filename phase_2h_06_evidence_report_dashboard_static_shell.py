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
PHASE_2H_08 = "2H-08"
PHASE_2H_12 = "2H-12"
TASK_NAME = "phase2h-06-evidence-report-dashboard-static-shell"
TITLE = "Phase 2H-06 Evidence / Report Dashboard Static Shell"
MODE = "implementation_static_local_deterministic_read_only_dashboard_shell"
SCOPE = "static_evidence_report_dashboard_shell"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
FINAL_VERDICT = "PHASE_2H_06_STATIC_DASHBOARD_SHELL_READY"
DOC_PATH = "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.md"
HTML_PATH = "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html"
PHASE_2H_08_DOC_PATH = (
    "docs/phase_2h/phase_2h_08_evidence_report_dashboard_static_artifact_reference.md"
)
PHASE_2H_12_DOC_PATH = (
    "docs/phase_2h/"
    "phase_2h_12_dashboard_empty_state_missing_artifact_messaging.md"
)
AI_INTRODUCTION_SAFE_WORKFLOW = (
    "User Request -> Static Review Context -> Policy Boundary Explanation -> "
    "Manual Reviewer Interpretation -> Committed Evidence -> Static Dashboard / Report"
)

BOUNDARY_NOTICE = (
    "Static/read-only/no execution boundary: this dashboard shell is local, "
    "deterministic, and non-executing. It connects to no live data source, "
    "runner, adapter, execution system, provider, API, model, secret store, "
    "SSH, NETCONF, or RESTCONF. AI may explain committed evidence and static "
    "review context only; AI must not act as a controller."
)

EXPECTED_SECTION_TITLES = (
    "Boundary notice",
    "AI introduction",
    "Empty state",
    "Static evidence summary",
    "Static report summary",
    "Static artifact summary",
    "Static artifact references",
    "Static empty-state messaging",
    "Static missing-artifact messaging",
)

EXPECTED_SECTION_GROUPS = (
    {
        "id": "reviewer-orientation",
        "title": "Reviewer orientation",
        "description": (
            "Start with the locked safety boundary, AI review-only role, and "
            "no-live-data state so reviewers know the dashboard is passive "
            "before reading evidence."
        ),
        "section_ids": ("boundary-notice", "ai-introduction", "empty-state"),
    },
    {
        "id": "static-evidence-and-reports",
        "title": "Static evidence, report, and artifact summaries",
        "description": (
            "Then show the committed static evidence, report, and artifact "
            "summaries before the hard-coded repository-local artifact references."
        ),
        "section_ids": (
            "evidence-summary",
            "report-summary",
            "artifact-status",
            "static-artifact-references",
        ),
    },
    {
        "id": "static-state-messaging",
        "title": "Static state messaging",
        "description": (
            "Close with committed empty-state and missing-artifact copy that "
            "explains optional local artifacts without probing the filesystem."
        ),
        "section_ids": (
            "static-empty-state-messaging",
            "static-missing-artifact-messaging",
        ),
    },
)

STATIC_SECTION_STATUS_EXPLANATIONS = {
    "LOCKED": (
        "the committed safety boundary is closed to live execution and remains "
        "static reviewer copy only."
    ),
    "NO_LIVE_DATA": (
        "no live data source is attached and no runtime collection is attempted."
    ),
    "EMPTY_STATE": (
        "the section is an intentional static summary state, not a failed lookup."
    ),
    "REVIEW_ONLY": (
        "the section is for reviewer orientation and does not trigger execution."
    ),
    "STATIC_EMPTY_STATE": (
        "the empty-state content is committed dashboard copy from the static model."
    ),
    "STATIC_MISSING_ARTIFACT": (
        "the missing-artifact content is a static notice and performs no filesystem "
        "probe."
    ),
}

STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS = {
    "STATIC_COMMITTED": (
        "the referenced artifact is committed static reviewer evidence."
    ),
    "REPORT_REFERENCE": (
        "the referenced path points to a committed static report or review artifact."
    ),
    "OPTIONAL_LOCAL_ARTIFACT_STATIC_REFERENCE_ONLY": (
        "the path is a static label for an optional local artifact and is not checked "
        "at runtime."
    ),
}

STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS = {
    "STATIC_REFERENCE_AVAILABLE": (
        "availability is a committed static declaration, not a live filesystem check."
    ),
    "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY": (
        "availability is message-only static copy; the optional artifact may be "
        "absent without probing, recovery, refresh, or execution."
    ),
}

STATIC_MESSAGE_STATUS_EXPLANATIONS = {
    "STATIC_EMPTY_STATE_MESSAGE_ONLY": (
        "the message explains a static empty state only and does not inspect files."
    ),
    "STATIC_REPORT_ONLY": (
        "the message keeps the dashboard local, deterministic, read-only, and "
        "report-only."
    ),
    "STATIC_MISSING_ARTIFACT_MESSAGE_ONLY": (
        "the message describes an optional missing artifact without checking for it."
    ),
}

STATIC_LABEL_EXPLANATION_GROUPS = {
    "section_status_labels": STATIC_SECTION_STATUS_EXPLANATIONS,
    "artifact_reference_status_labels": STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS,
    "artifact_availability_labels": STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS,
    "message_status_labels": STATIC_MESSAGE_STATUS_EXPLANATIONS,
}

STATIC_ARTIFACT_REFERENCES = (
    {
        "kind": "static artifact reference",
        "label": "Committed dashboard static shell HTML",
        "path": HTML_PATH,
        "status": "STATIC_COMMITTED",
        "status_explanation": STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS[
            "STATIC_COMMITTED"
        ],
        "availability": "STATIC_REFERENCE_AVAILABLE",
        "availability_explanation": STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS[
            "STATIC_REFERENCE_AVAILABLE"
        ],
        "note": "Hard-coded repository-local dashboard artifact reference.",
    },
    {
        "kind": "report reference",
        "label": "Phase 2H-06 implementation report",
        "path": DOC_PATH,
        "status": "REPORT_REFERENCE",
        "status_explanation": STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS[
            "REPORT_REFERENCE"
        ],
        "availability": "STATIC_REFERENCE_AVAILABLE",
        "availability_explanation": STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS[
            "STATIC_REFERENCE_AVAILABLE"
        ],
        "note": "Hard-coded repository-local implementation report reference.",
    },
    {
        "kind": "report reference",
        "label": "Phase 2H-07 acceptance review",
        "path": (
            "docs/phase_2h/"
            "phase_2h_07_evidence_report_dashboard_static_shell_acceptance_review_planning_only.md"
        ),
        "status": "REPORT_REFERENCE",
        "status_explanation": STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS[
            "REPORT_REFERENCE"
        ],
        "availability": "STATIC_REFERENCE_AVAILABLE",
        "availability_explanation": STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS[
            "STATIC_REFERENCE_AVAILABLE"
        ],
        "note": "Hard-coded repository-local acceptance review reference.",
    },
    {
        "kind": "optional local artifact reference",
        "label": "Optional local report-index output",
        "path": "reports/report_index.html",
        "status": "OPTIONAL_LOCAL_ARTIFACT_STATIC_REFERENCE_ONLY",
        "status_explanation": STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS[
            "OPTIONAL_LOCAL_ARTIFACT_STATIC_REFERENCE_ONLY"
        ],
        "availability": "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY",
        "availability_explanation": STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS[
            "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY"
        ],
        "note": (
            "Static path label only; the dashboard performs no runtime existence "
            "check and does not generate or refresh this artifact."
        ),
    },
)

STATIC_EMPTY_STATE_MESSAGES = (
    {
        "id": "no-usable-artifact-reference",
        "status": "STATIC_EMPTY_STATE_MESSAGE_ONLY",
        "status_explanation": STATIC_MESSAGE_STATUS_EXPLANATIONS[
            "STATIC_EMPTY_STATE_MESSAGE_ONLY"
        ],
        "title": "No usable artifact reference in static context",
        "body": (
            "If static dashboard content has no usable artifact reference, the "
            "dashboard reports that state as committed copy only. No live scan, "
            "runtime artifact discovery, fetch, generation, recovery, or execution "
            "is attempted."
        ),
    },
    {
        "id": "static-report-only-dashboard-state",
        "status": "STATIC_REPORT_ONLY",
        "status_explanation": STATIC_MESSAGE_STATUS_EXPLANATIONS["STATIC_REPORT_ONLY"],
        "title": "Static report-only dashboard state",
        "body": (
            "The empty state remains local, deterministic, read-only, report-only, "
            "and non-executing; it does not inspect local files or infer runtime "
            "artifact availability."
        ),
    },
)

STATIC_MISSING_ARTIFACT_MESSAGES = (
    {
        "id": "optional-report-index-static-missing",
        "reference_label": "Optional local report-index output",
        "reference_path": "reports/report_index.html",
        "status": "STATIC_MISSING_ARTIFACT_MESSAGE_ONLY",
        "status_explanation": STATIC_MESSAGE_STATUS_EXPLANATIONS[
            "STATIC_MISSING_ARTIFACT_MESSAGE_ONLY"
        ],
        "title": "Optional local artifact may be absent",
        "body": (
            "The optional report-index reference is marked by static dashboard "
            "context only. The dashboard does not check the filesystem, discover "
            "artifacts, recover, fetch, generate, refresh, or execute anything."
        ),
    },
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
            "id": "boundary-notice",
            "title": "Boundary notice",
            "status": "LOCKED",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["LOCKED"],
            "body": BOUNDARY_NOTICE,
        },
        {
            "id": "ai-introduction",
            "title": "AI introduction",
            "status": "REVIEW_ONLY",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["REVIEW_ONLY"],
            "body": (
                "AI is allowed only as a static explanation, review, and "
                "documentation aid for committed evidence, report summaries, "
                "safe boundaries, and mock-only demo narrative. AI must not act "
                "as a controller and must not execute tools, jobs, commands, "
                "model calls, provider calls, device operations, SSH, NETCONF, "
                "RESTCONF, config backup, config change, scheduler, queue, "
                "worker, agent loop, MCP bridge, live discovery, secrets, or "
                "external automation. The safe control object is evidence, "
                "report, and dashboard copy, not a router, switch, session, or "
                "device command. Safe workflow: "
                f"{AI_INTRODUCTION_SAFE_WORKFLOW}. Phase 2J non-device "
                "automation control remains future work and is not implemented "
                "by this dashboard refresh."
            ),
        },
        {
            "id": "empty-state",
            "title": "Empty state",
            "status": "NO_LIVE_DATA",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["NO_LIVE_DATA"],
            "body": "No live data source is attached. The dashboard shell is ready for static review only.",
        },
        {
            "id": "evidence-summary",
            "title": "Static evidence summary",
            "status": "EMPTY_STATE",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["EMPTY_STATE"],
            "body": (
                "The evidence summary describes committed local evidence references "
                "only. No live evidence source is connected, collected, refreshed, "
                "or inferred."
            ),
        },
        {
            "id": "report-summary",
            "title": "Static report summary",
            "status": "EMPTY_STATE",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["EMPTY_STATE"],
            "body": (
                "The report summary describes committed report references only. No "
                "report refresh, regeneration, fetch, or runtime lookup is performed."
            ),
        },
        {
            "id": "artifact-status",
            "title": "Static artifact summary",
            "status": "REVIEW_ONLY",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["REVIEW_ONLY"],
            "body": (
                "Artifact summary status is limited to local deterministic committed "
                "references and optional static labels, not runtime collection."
            ),
        },
        {
            "id": "static-artifact-references",
            "title": "Static artifact references",
            "status": "REVIEW_ONLY",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS["REVIEW_ONLY"],
            "body": (
                "Hard-coded repository-local references only. These entries are static "
                "dashboard content and perform no scan, fetch, discovery, or runtime "
                "existence check."
            ),
            "references": STATIC_ARTIFACT_REFERENCES,
        },
        {
            "id": "static-empty-state-messaging",
            "title": "Static empty-state messaging",
            "status": "STATIC_EMPTY_STATE",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS[
                "STATIC_EMPTY_STATE"
            ],
            "body": (
                "Empty-state messages are deterministic dashboard copy derived "
                "only from the static dashboard model."
            ),
            "messages": STATIC_EMPTY_STATE_MESSAGES,
        },
        {
            "id": "static-missing-artifact-messaging",
            "title": "Static missing-artifact messaging",
            "status": "STATIC_MISSING_ARTIFACT",
            "status_explanation": STATIC_SECTION_STATUS_EXPLANATIONS[
                "STATIC_MISSING_ARTIFACT"
            ],
            "body": (
                "Missing-artifact messages are static report-only notices. They "
                "do not perform live scans, runtime discovery, fetching, recovery, "
                "generation, or execution."
            ),
            "messages": STATIC_MISSING_ARTIFACT_MESSAGES,
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
        "artifact_references": STATIC_ARTIFACT_REFERENCES,
        "static_empty_state_messages": STATIC_EMPTY_STATE_MESSAGES,
        "static_missing_artifact_messages": STATIC_MISSING_ARTIFACT_MESSAGES,
        "static_label_explanation_groups": STATIC_LABEL_EXPLANATION_GROUPS,
        "sections": sections,
        "section_groups": EXPECTED_SECTION_GROUPS,
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

    artifact_references = model.get("artifact_references", ())
    if tuple(artifact_references) != STATIC_ARTIFACT_REFERENCES:
        errors.append("STATIC_ARTIFACT_REFERENCES_MISMATCH")

    if tuple(model.get("static_empty_state_messages", ())) != STATIC_EMPTY_STATE_MESSAGES:
        errors.append("STATIC_EMPTY_STATE_MESSAGES_MISMATCH")
    if (
        tuple(model.get("static_missing_artifact_messages", ()))
        != STATIC_MISSING_ARTIFACT_MESSAGES
    ):
        errors.append("STATIC_MISSING_ARTIFACT_MESSAGES_MISMATCH")
    if model.get("static_label_explanation_groups") != STATIC_LABEL_EXPLANATION_GROUPS:
        errors.append("STATIC_LABEL_EXPLANATION_GROUPS_MISMATCH")

    sections = model.get("sections", ())
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes, bytearray)):
        errors.append("SECTIONS_NOT_SEQUENCE")
        sections = ()
    section_titles = tuple(section.get("title") for section in sections if isinstance(section, Mapping))
    if section_titles != EXPECTED_SECTION_TITLES:
        errors.append("SECTION_ORDER_MISMATCH")
    for expected in EXPECTED_SECTION_TITLES:
        if expected not in section_titles:
            errors.append(f"EXPECTED_SECTION_MISSING:{expected}")
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        label = section.get("status")
        expected_explanation = STATIC_SECTION_STATUS_EXPLANATIONS.get(str(label))
        if section.get("status_explanation") != expected_explanation:
            errors.append(f"SECTION_STATUS_EXPLANATION_MISMATCH:{label}")

    for reference in artifact_references:
        if not isinstance(reference, Mapping):
            continue
        label = reference.get("status")
        expected_explanation = STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS.get(str(label))
        if reference.get("status_explanation") != expected_explanation:
            errors.append(f"ARTIFACT_STATUS_EXPLANATION_MISMATCH:{label}")
        availability_label = reference.get("availability")
        expected_availability = STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS.get(
            str(availability_label)
        )
        if reference.get("availability_explanation") != expected_availability:
            errors.append(f"ARTIFACT_AVAILABILITY_EXPLANATION_MISMATCH:{availability_label}")

    for message_group_name in (
        "static_empty_state_messages",
        "static_missing_artifact_messages",
    ):
        for message in model.get(message_group_name, ()):
            if not isinstance(message, Mapping):
                continue
            label = message.get("status")
            expected_explanation = STATIC_MESSAGE_STATUS_EXPLANATIONS.get(str(label))
            if message.get("status_explanation") != expected_explanation:
                errors.append(f"MESSAGE_STATUS_EXPLANATION_MISMATCH:{label}")

    section_groups = model.get("section_groups", ())
    if tuple(section_groups) != EXPECTED_SECTION_GROUPS:
        errors.append("SECTION_GROUPS_MISMATCH")
        section_groups = ()
    section_ids = tuple(section.get("id") for section in sections if isinstance(section, Mapping))
    grouped_section_ids = tuple(
        section_id
        for group in section_groups
        if isinstance(group, Mapping)
        for section_id in group.get("section_ids", ())
    )
    if grouped_section_ids != section_ids:
        errors.append("SECTION_GROUP_ORDER_MISMATCH")

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

    groups = "\n".join(
        _render_section_group(group, shell_model["sections"])
        for group in shell_model["section_groups"]
    )
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
        "    .section-group { margin: 0 0 18px; }\n"
        "    .section-group > h2 { font-size: 20px; margin: 0 0 6px; }\n"
        "    .section-group-intro { margin: 0 0 12px; color: #52616f; }\n"
        "    .group-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }\n"
        "    section { background: #ffffff; border: 1px solid #d6dee8; padding: 16px; }\n"
        "    h3 { font-size: 18px; margin: 0 0 8px; }\n"
        "    .status { font-size: 12px; font-weight: bold; letter-spacing: .04em; color: #375a7f; }\n"
        "    .label-explanation { font-size: 13px; margin: 6px 0 10px; color: #465562; }\n"
        "    .label-explanation strong { color: #17202a; }\n"
        "    .reference-labels { display: block; margin-top: 4px; color: #465562; }\n"
        "    p { line-height: 1.45; }\n"
        "    ul { padding-left: 20px; margin: 12px 0 0; }\n"
        "    li { margin: 0 0 10px; line-height: 1.4; }\n"
        "    code { background: #eef3f8; padding: 1px 4px; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <main>\n"
        "    <header>\n"
        f"      <h1>{escape(str(shell_model['title']))}</h1>\n"
        "      <p>Static local dashboard shell for reviewer-visible evidence summaries, report summaries, and AI boundary explanation.</p>\n"
        f"      <div class=\"notice\">{escape(str(shell_model['boundary_notice']))}</div>\n"
        "    </header>\n"
        f"{groups}\n"
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
        "phase_2h_08_doc_path": PHASE_2H_08_DOC_PATH,
        "phase_2h_12_doc_path": PHASE_2H_12_DOC_PATH,
        "artifact_references": STATIC_ARTIFACT_REFERENCES,
        "static_empty_state_messages": STATIC_EMPTY_STATE_MESSAGES,
        "static_missing_artifact_messages": STATIC_MISSING_ARTIFACT_MESSAGES,
        "static_label_explanation_groups": STATIC_LABEL_EXPLANATION_GROUPS,
        "section_titles": tuple(section["title"] for section in model["sections"]),
        "section_groups": EXPECTED_SECTION_GROUPS,
        "ai_introduction_safe_workflow": AI_INTRODUCTION_SAFE_WORKFLOW,
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
    references = section.get("references", ())
    messages = section.get("messages", ())
    status_explanation = _render_label_explanation(
        "Status label",
        section.get("status_explanation"),
    )
    reference_html = ""
    if references:
        items = "\n".join(_render_reference(reference) for reference in references)
        reference_html = f"\n        <ul>\n{items}\n        </ul>"
    message_html = ""
    if messages:
        items = "\n".join(_render_message(message) for message in messages)
        message_html = f"\n        <ul>\n{items}\n        </ul>"
    return (
        "      <section>\n"
        f"        <div class=\"status\">{escape(str(section['status']))}</div>\n"
        f"{status_explanation}"
        f"        <h3>{escape(str(section['title']))}</h3>\n"
        f"        <p>{escape(str(section['body']))}</p>\n"
        f"{reference_html}\n"
        f"{message_html}\n"
        "      </section>"
    )


def _render_section_group(group: Mapping[str, Any], sections: Sequence[Mapping[str, Any]]) -> str:
    section_by_id = {section["id"]: section for section in sections}
    grouped_sections = "\n".join(
        _render_section(section_by_id[section_id]) for section_id in group["section_ids"]
    )
    return (
        "    <div class=\"section-group\">\n"
        f"      <h2>{escape(str(group['title']))}</h2>\n"
        f"      <p class=\"section-group-intro\">{escape(str(group['description']))}</p>\n"
        "      <div class=\"group-grid\">\n"
        f"{grouped_sections}\n"
        "      </div>\n"
        "    </div>"
    )


def _render_reference(reference: Mapping[str, Any]) -> str:
    return (
        "          <li>"
        f"<strong>{escape(str(reference['kind']))}</strong>: "
        f"{escape(str(reference['label']))} - "
        f"<code>{escape(str(reference['path']))}</code> "
        f"({escape(str(reference['status']))}). "
        "<span class=\"reference-labels\">"
        "<strong>Status label:</strong> "
        f"{escape(str(reference['status_explanation']))} "
        "<strong>Availability label:</strong> "
        f"{escape(str(reference['availability']))}: "
        f"{escape(str(reference['availability_explanation']))}"
        "</span> "
        f"{escape(str(reference['note']))}"
        "</li>"
    )


def _render_message(message: Mapping[str, Any]) -> str:
    reference = ""
    if "reference_path" in message:
        reference = (
            f" <code>{escape(str(message['reference_path']))}</code>"
            f" ({escape(str(message.get('reference_label', 'static reference')))})."
        )
    return (
        "          <li>"
        f"<strong>{escape(str(message['status']))}</strong>: "
        "<span class=\"reference-labels\"><strong>Status label:</strong> "
        f"{escape(str(message['status_explanation']))}</span> "
        f"{escape(str(message['title']))}.{reference} "
        f"{escape(str(message['body']))}"
        "</li>"
    )


def _render_label_explanation(label_type: str, explanation: Any) -> str:
    if not explanation:
        return ""
    return (
        "        <p class=\"label-explanation\">"
        f"<strong>{escape(label_type)}:</strong> {escape(str(explanation))}"
        "</p>\n"
    )
