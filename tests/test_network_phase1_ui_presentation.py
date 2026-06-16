from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_day_results_ui_is_presented_as_automation_evidence():
    day_results = read("components/network/DayResultsClient.tsx")
    nav = read("components/network/NetworkNav.tsx")
    page = read("app/network/day-results/page.tsx")
    combined = f"{day_results}\n{nav}\n{page}"

    for old_copy in [
        "Day1-160 Results",
        "Imported Day Results",
        "Selected Report",
        'label: "Day Results"',
    ]:
        assert old_copy not in combined

    for new_copy in [
        "Automation Evidence",
        "Imported Evidence",
        "Selected Evidence",
        'label: "Evidence"',
        "evidence items",
    ]:
        assert new_copy in combined


def test_evidence_cards_are_evidence_first_with_day_as_metadata():
    source = read("components/network/DayResultsClient.tsx")

    for label in [
        "Device Check Report",
        "Readiness Gate Review",
        "Project Summary",
        "Test Evidence",
        "Uncategorized Evidence",
    ]:
        assert label in source

    assert "<strong>{getEvidenceTypeLabel(result.resultKind)}</strong>" in source
    assert "{resultSource(result)} · {status} · {executionBoundaryLabels[boundary]}" in source
    assert "<strong>{result.dayLabel}</strong>" not in source


def test_evidence_sorting_prefers_type_then_source_day_then_created_at():
    source = read("components/network/DayResultsClient.tsx")

    assert "getEvidenceTypeLabel" in source
    assert "getEvidenceTypeRank" in source
    assert "getSourceDayNumber" in source
    assert "sortEvidenceItems" in source
    assert "getEvidenceTypeRank(left.resultKind) - getEvidenceTypeRank(right.resultKind)" in source
    assert "getSourceDayNumber(right.dayLabel, right.sourceDay)" in source
    assert "Date.parse(right.createdAt) - Date.parse(left.createdAt)" in source


def test_selected_evidence_uses_user_facing_fields_and_boundary_labels():
    source = read("components/network/DayResultsClient.tsx")

    for field in ["Source", "Type", "Target", "Check", "Status", "Boundary"]:
        assert f"<dt>{field}</dt>" in source

    for label in [
        "Report-only",
        "Read-only candidate",
        "Approval required",
        "Blocked",
        "AI Analysis Record",
        "Raw Evidence JSON",
    ]:
        assert label in source


def test_primary_button_contrast_and_icon_current_color_are_locked():
    css = read("app/globals.css")
    components = "\n".join(
        [
            read("components/network/DayResultsClient.tsx"),
            read("components/network/AiActionsClient.tsx"),
            read("components/network/ReportsClient.tsx"),
            read("components/network/JobsClient.tsx"),
        ]
    )

    assert ".network-toolbar > span" in css
    assert ".network-toolbar span," not in css
    assert "background: #0f766e;" in css
    assert "color: #fff;" in css
    assert ".icon-action-button span" in css
    assert "color: currentColor;" in css
    assert ".icon-action-button:disabled" in css
    assert "background: #e2e8f0;" in css
    assert "color: #64748b;" in css
    assert "cursor: not-allowed;" in css

    assert "text-slate-500" not in components
    assert "text-gray-500" not in components


def test_ai_actions_reloads_latest_parse_result_and_displays_record_metadata():
    source = read("components/network/AiActionsClient.tsx")

    assert 'fetch("/api/network/ai/parse-request/latest")' in source
    assert "setUserRequest(payload.parseResult.userRequest)" in source
    assert "setInventoryText(" in source
    assert "<dt>Parse Result</dt>" in source
    assert "<dt>Created</dt>" in source
    assert "parseResult?.id" in source
    assert "parseResult?.createdAt" in source
    assert 'source: "ai-actions"' in source
    assert "parseResultId: parseResult?.id" in source
    assert "vendor: output.vendor" in source


def test_jobs_client_reloads_jobs_and_does_not_offer_phase1_run_behavior():
    source = read("components/network/JobsClient.tsx")

    assert 'fetch("/api/network/jobs")' in source
    assert "<span>Vendor</span>" in source
    assert "<span>Created</span>" in source
    assert "<span>Source</span>" in source
    assert "job.parseResultId ?? job.source" in source
    assert "Runner not enabled in Phase 1" in source
    assert "Run Job" not in source
    assert "onClick={run" not in source
