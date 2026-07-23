from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_day_results_ui_remains_recorded_automation_evidence():
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
        "Recorded evidence · non-executing",
    ]:
        assert new_copy in combined


def test_evidence_uses_only_safe_projection_fields_and_fixed_states():
    source = read("components/network/DayResultsClient.tsx")

    assert "projectEvidenceCollection" in source
    assert "projectAnalysisRecord" in source
    assert "Recorded result:" in source
    assert "Recorded:" in source
    assert "Source path and device identity withheld" in source
    assert "Technical payload is not displayed on this surface" in source
    assert "EMPTY — no matching recorded evidence" in source
    assert "Unable to read the recorded analysis" in source

    for unsafe_expression in [
        "result.deviceName",
        "result.reportTitle",
        "result.checkType",
        "selected.rawOutput",
        "analysis.model",
        "analysis.id",
        "analysis.safety.reason",
        "JSON.stringify",
        "Raw Evidence JSON",
        "deriveExecutionBoundary",
        "Read-only candidate",
        "Approval required",
    ]:
        assert unsafe_expression not in source


def test_evidence_sorting_and_filtering_use_closed_safe_fields():
    client = read("components/network/DayResultsClient.tsx")
    helper = read("components/network/Phase2O05SafePresentation.ts")

    assert 'type StatusFilter = "ALL" | SafeRecordedStatus' in client
    assert 'id="evidence-status-filter"' in client
    assert "Reset evidence view" in client
    assert "item.status === statusFilter" in client

    assert "left.categoryRank - right.categoryRank" in helper
    assert "right.dayNumber - left.dayNumber" in helper
    assert "right.recordedTimestamp - left.recordedTimestamp" in helper
    assert "normalizeRecordedStatus" in helper
    assert "normalizeSourceDay" in helper
    assert "normalizeRecordedDate" in helper


def test_safe_presentation_boundary_is_pure_and_fail_closed():
    source = read("components/network/Phase2O05SafePresentation.ts")

    for projection in [
        "projectEvidenceCollection",
        "projectReportsCollection",
        "projectAnalysisRecord",
        "projectActionCatalog",
        "projectParseResult",
        "projectJobsCollection",
    ]:
        assert f"function {projection}" in source

    for prohibited in [
        "JSON.stringify",
        "dangerouslySetInnerHTML",
        "fetch(",
        "writeFile",
        "readFile",
        "createNetworkJob",
        "listNetworkJobs",
        "importDayResults",
        "getLatestAnalysis",
        "getLatestParse",
        "openai",
    ]:
        assert prohibited not in source

    assert "Object.keys(value).every" in source
    assert '"Identifier withheld"' in source
    assert '"Recorded reason withheld"' in source
    assert '"Unknown catalog reference"' in source


def test_responsive_focus_and_native_table_contracts_are_present():
    css = read("app/globals.css")
    jobs = read("components/network/JobsClient.tsx")

    assert '.network-shell :where(a, button, select, summary, [tabindex="0"]):focus-visible' in css
    assert "outline: 3px solid #0f172a;" in css
    assert ".safe-table-scroll" in css
    assert "overflow-x: auto;" in css
    assert ".safe-job-table" in css
    assert "@media (max-width: 860px)" in css
    assert "@media (max-width: 420px)" in css

    assert "<table" in jobs
    assert "<caption>" in jobs
    assert '<th scope="col">' in jobs
    assert 'role="region"' in jobs
    assert "tabIndex={0}" in jobs
    assert 'aria-describedby="jobs-stage-0-boundary"' in jobs
    assert 'role="table"' not in jobs


def test_evidence_rows_reflow_without_narrow_internal_overflow():
    css = read("app/globals.css")
    narrow_css = css.partition("@media (max-width: 420px)")[2]

    assert narrow_css
    assert (
        ".result-list,\n"
        "  .evidence-group,\n"
        "  .result-row {\n"
        "    min-width: 0;\n"
        "  }"
    ) in narrow_css
    assert (
        ".result-row {\n"
        "    grid-template-columns: 20px minmax(0, 1fr);\n"
        "  }"
    ) in narrow_css
    assert (
        ".result-row > span,\n"
        "  .result-row > .kind-badge,\n"
        "  .result-row > .status-badge {\n"
        "    grid-column: 2;\n"
        "  }"
    ) in narrow_css
    assert (
        ".result-row strong,\n"
        "  .result-row small {\n"
        "    overflow: visible;\n"
        "    text-overflow: clip;\n"
        "    white-space: normal;\n"
        "    overflow-wrap: anywhere;\n"
        "  }"
    ) in narrow_css


def test_ai_actions_reads_only_recorded_data_without_submission_controls():
    source = read("components/network/AiActionsClient.tsx")

    assert 'fetch("/api/network/ai/parse-request/latest")' in source
    assert "projectActionCatalog" in source
    assert "projectParseResult" in source
    assert "Recorded Recommendation" in source
    assert "Allowlist Reference" in source
    assert "UNAVAILABLE — no request, provider, approval, job creation, or execution" in source
    assert "<AiActionsStage0Presentation />" in source

    for prohibited in [
        "setUserRequest(",
        "setInventoryText(",
        'fetch("/api/network/ai/parse-request"',
        "/api/network/jobs/create",
        "parseRequest",
        "createJob",
        "JSON.stringify",
        "<textarea",
        "output?.targetDevice",
        "output?.vendor",
        "parseResult?.id",
        "parseResult?.userRequest",
    ]:
        assert prohibited not in source


def test_jobs_client_uses_get_only_recorded_projection_without_execution_state():
    source = read("components/network/JobsClient.tsx")

    assert 'fetch("/api/network/jobs")' in source
    assert "projectJobsCollection" in source
    assert "Reload recorded jobs" in source
    assert "Recorded local job metadata · non-executing" in source
    assert "EMPTY — no recorded jobs in this local store" in source
    assert "ERROR — no safely displayable recorded jobs" in source
    assert "runner, queue, scheduler, worker" in source

    for prohibited in [
        "Run Job",
        "onClick={run",
        "/api/network/jobs/create",
        "job.targetDevice",
        "job.params",
        "job.source",
        "job.parseResultId",
        "setInterval",
        "setTimeout",
        "WebSocket",
        "EventSource",
    ]:
        assert prohibited not in source
