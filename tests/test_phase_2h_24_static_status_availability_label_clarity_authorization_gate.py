from pathlib import Path


DOC_PATH = Path(
    "docs/phase_2h/"
    "phase_2h_24_static_status_availability_label_clarity_implementation_authorization_gate.md"
)
SOURCE_PATH = Path("phase_2h_06_evidence_report_dashboard_static_shell.py")


def test_agents_md_is_not_modified_for_phase_2h_24():
    agents_text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2H-24" not in agents_text
    assert "static status and availability label clarity" not in agents_text.lower()


def test_phase_2h_24_document_exists_with_required_boundary_markers():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert (
        "# Phase 2H-24 - Static Status and Availability Label Clarity "
        "Implementation Authorization Gate / Planning Only"
    ) in text
    for marker in (
        "TASK_MODE: PLANNING_ONLY_IMPLEMENTATION_AUTHORIZATION_GATE_ONLY",
        "IMPLEMENTATION_AUTHORIZED_IN_THIS_PHASE: NO",
        "IMPLEMENTATION_PERFORMED_IN_THIS_PHASE: NO",
        "DASHBOARD_BEHAVIOR_CHANGED_IN_THIS_PHASE: NO",
        "DEFAULT_SAFETY_BASELINE: REPORT_ONLY_DRY_RUN_MOCK_ONLY",
        "PHASE_2H_23_SELECTED_SLICE_REVIEWED: YES",
        "SELECTED_SLICE_CHANGED: NO",
        "IMPLEMENTATION_AUTHORIZED_FOR_FUTURE_PHASE: YES",
        "AUTHORIZED_PHASE_2H_24_IMPLEMENTATION: NO",
        "RUNTIME_ARTIFACT_DISCOVERY_ADDED: NO",
        "FILESYSTEM_SCANNING_ADDED: NO",
        "NEW_FILESYSTEM_EXISTENCE_CHECKS_ADDED: NO",
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


def test_phase_2h_24_authorizes_only_one_future_static_label_clarity_slice():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "IMPLEMENTATION_AUTHORIZATION_DECISION: YES" in text
    assert "IMPLEMENTATION_AUTHORIZED_BY_THIS_PHASE: YES" in text
    assert "AUTHORIZED_FUTURE_PHASE_ONLY: YES" in text
    assert "AUTHORIZED_NEXT_PHASE: Phase 2H-25" in text
    assert "AUTHORIZED_SLICE: Static Status and Availability Label Clarity" in text
    assert (
        "AUTHORIZED_SCOPE: "
        "ONE_FUTURE_STATIC_STATUS_AND_AVAILABILITY_LABEL_CLARITY_IMPLEMENTATION_SLICE"
    ) in text
    assert (
        "Phase 2H-25 - Static Status and Availability Label Clarity Implementation Slice"
        in text
    )
    assert "Phase 2H-25 should not start until separately requested." in text


def test_phase_2h_24_keeps_current_static_labels_as_future_subject_only():
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    source_text = SOURCE_PATH.read_text(encoding="utf-8")

    existing_labels = (
        "LOCKED",
        "NO_LIVE_DATA",
        "EMPTY_STATE",
        "REVIEW_ONLY",
        "STATIC_EMPTY_STATE",
        "STATIC_MISSING_ARTIFACT",
        "STATIC_COMMITTED",
        "REPORT_REFERENCE",
        "OPTIONAL_LOCAL_ARTIFACT_STATIC_REFERENCE_ONLY",
        "STATIC_REFERENCE_AVAILABLE",
        "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY",
        "STATIC_EMPTY_STATE_MESSAGE_ONLY",
        "STATIC_REPORT_ONLY",
        "STATIC_MISSING_ARTIFACT_MESSAGE_ONLY",
    )
    for label in existing_labels:
        assert label in doc_text
        assert label in source_text

    assert "Phase 2H-24 remains planning-only and performs no implementation." in doc_text
    assert "modify dashboard implementation files" in doc_text
    assert "modify committed static dashboard HTML" in doc_text


def test_phase_2h_24_formal_record_preserves_authorization_without_implementation():
    doc_text = DOC_PATH.read_text(encoding="utf-8")

    assert "AUTHORIZED_SLICE: Static Status and Availability Label Clarity" in doc_text
    assert "Phase 2H-24 remains planning-only and performs no implementation." in doc_text
    assert "does not require real automation, live lab access, runtime command execution" in doc_text
    assert "no runtime discovery" in doc_text
