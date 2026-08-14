from pathlib import Path

import phase_2h_06_evidence_report_dashboard_static_shell as phase_2h_06


DOC_PATH = Path(
    "docs/phase_2h/"
    "phase_2h_25_static_status_availability_label_clarity_implementation_slice.md"
)
AUTHORIZATION_PATH = Path(
    "docs/phase_2h/"
    "phase_2h_24_static_status_availability_label_clarity_implementation_authorization_gate.md"
)
HTML_PATH = Path("docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html")


def test_agents_md_is_not_modified_for_phase_2h_25():
    agents_text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2H-25" not in agents_text
    assert "STATIC_LABEL_EXPLANATION_GROUPS" not in agents_text


def test_phase_2h_25_document_exists_with_required_boundary_markers():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert (
        "# Phase 2H-25 - Static Status and Availability Label Clarity "
        "Implementation Slice"
    ) in text
    for marker in (
        "TASK_MODE: IMPLEMENTATION_SLICE_ONLY",
        "SELECTED_SLICE: STATIC_STATUS_AND_AVAILABILITY_LABEL_CLARITY",
        "AUTHORIZATION_SOURCE: Phase 2H-24",
        "STATIC_ONLY: YES",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "READ_ONLY: YES",
        "REPORT_ONLY: YES",
        "DRY_RUN: YES",
        "MOCK_ONLY: YES",
        "NON_EXECUTING: YES",
        "RUNTIME_ARTIFACT_DISCOVERY_ADDED: NO",
        "FILESYSTEM_PROBING_ADDED: NO",
        "RUNNER_ADAPTER_SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_TOUCHED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED: NO",
        "PRODUCTION_EXECUTION_PATH_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
        "NEXT_PHASE_STARTED: NO",
        "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO",
        "FORBIDDEN_SCOPE_TOUCHED: NO",
    ):
        assert marker in text


def test_phase_2h_25_references_authorized_label_clarity_scope():
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    authorization_text = AUTHORIZATION_PATH.read_text(encoding="utf-8")

    assert "AUTHORIZED_NEXT_PHASE: Phase 2H-25" in authorization_text
    assert "AUTHORIZED_SLICE: Static Status and Availability Label Clarity" in authorization_text
    assert str(AUTHORIZATION_PATH).replace("\\", "/") in doc_text
    assert "STATIC_LABEL_EXPLANATION_GROUPS" in doc_text
    assert "availability is a committed static declaration" in doc_text
    assert "message-only static copy" in doc_text


def test_phase_2h_25_static_dashboard_html_contains_label_clarity_copy():
    html = HTML_PATH.read_text(encoding="utf-8")

    assert "Status label:" in html
    assert "Availability label:" in html
    assert "STATIC_REFERENCE_AVAILABLE" in html
    assert "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY" in html
    assert "availability is a committed static declaration" in html
    assert "message-only static copy" in html
    assert phase_2h_06.BOUNDARY_NOTICE in html
    assert "<script" not in html.lower()


def test_phase_2h_25_formal_record_preserves_static_label_clarity_boundary():
    doc_text = DOC_PATH.read_text(encoding="utf-8")

    assert "AUTHORIZED_SLICE: Static Status and Availability Label Clarity" in doc_text
    assert "adds static reviewer-facing explanations for existing dashboard status" in doc_text
    assert "not a live filesystem check" in doc_text
    assert "reviewer guidance only and do not change dashboard behavior" in doc_text
