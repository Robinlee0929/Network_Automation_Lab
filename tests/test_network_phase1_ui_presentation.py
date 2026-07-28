import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_NARROW_CONTRACT = {
    ".result-list": {"min-width": "0"},
    ".evidence-group": {"min-width": "0"},
    ".result-row": {
        "min-width": "0",
        "grid-template-columns": "20px minmax(0, 1fr)",
    },
    ".result-row > span": {"grid-column": "2"},
    ".result-row > .kind-badge": {
        "grid-column": "2",
        "justify-self": "start",
    },
    ".result-row > .status-badge": {
        "grid-column": "2",
        "justify-self": "start",
    },
    ".result-row strong": {
        "overflow": "visible",
        "text-overflow": "clip",
        "white-space": "normal",
        "overflow-wrap": "anywhere",
    },
    ".result-row small": {
        "overflow": "visible",
        "text-overflow": "clip",
        "white-space": "normal",
        "overflow-wrap": "anywhere",
    },
}

AI_ACTIONS_NARROW_REFLOW_CONTRACT = {
    ".status-strip": {
        "align-items": "flex-start",
        "flex-direction": "column",
    },
    ".network-toolbar": {
        "align-items": "flex-start",
        "flex-direction": "column",
    },
}


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _matching_closing_brace(source: str, opening_brace: int) -> int:
    depth = 0
    for index in range(opening_brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise AssertionError("CSS block is missing a closing brace")


def _narrow_media_body(css: str) -> str:
    media_query = re.search(
        r"@media\s*\(\s*max-width\s*:\s*420px\s*\)\s*\{",
        css,
        flags=re.IGNORECASE,
    )
    assert media_query, "Missing max-width: 420px media query"
    opening_brace = css.find("{", media_query.start())
    closing_brace = _matching_closing_brace(css, opening_brace)
    return css[opening_brace + 1 : closing_brace]


def _normalize_selector(selector: str) -> str:
    normalized = re.sub(r"\s+", " ", selector.strip())
    return re.sub(r"\s*>\s*", " > ", normalized)


def _parse_declarations(body: str) -> dict[str, str]:
    declarations: dict[str, str] = {}
    for declaration in body.split(";"):
        if not declaration.strip():
            continue
        property_name, separator, value = declaration.partition(":")
        assert separator, f"Malformed CSS declaration: {declaration.strip()}"
        declarations[property_name.strip().lower()] = re.sub(
            r"\s+",
            " ",
            value.strip(),
        )
    return declarations


def _parse_rules(css_body: str) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    source = re.sub(r"/\*.*?\*/", "", css_body, flags=re.DOTALL)
    cursor = 0
    while True:
        opening_brace = source.find("{", cursor)
        if opening_brace == -1:
            break
        closing_brace = _matching_closing_brace(source, opening_brace)
        selectors = source[cursor:opening_brace]
        declarations = _parse_declarations(source[opening_brace + 1 : closing_brace])
        for selector in selectors.split(","):
            normalized_selector = _normalize_selector(selector)
            if normalized_selector:
                rules.setdefault(normalized_selector, {}).update(declarations)
        cursor = closing_brace + 1
    return rules


def _assert_evidence_narrow_contract(css: str) -> dict[str, dict[str, str]]:
    rules = _parse_rules(_narrow_media_body(css))
    assert EVIDENCE_NARROW_CONTRACT.keys() <= rules.keys()
    for selector, required_declarations in EVIDENCE_NARROW_CONTRACT.items():
        for property_name, expected_value in required_declarations.items():
            actual_value = rules[selector].get(property_name)
            assert actual_value == expected_value, (
                f"{selector} requires {property_name}: {expected_value}; "
                f"got {actual_value}"
            )
    return rules


def _reformatted_narrow_contract(css: str) -> str:
    rules = _assert_evidence_narrow_contract(css)
    rule_fragments = []
    for selector in reversed(tuple(EVIDENCE_NARROW_CONTRACT)):
        declarations = rules[selector]
        compact_declarations = ";".join(
            f"{property_name}:{value}"
            for property_name, value in reversed(tuple(declarations.items()))
        )
        rule_fragments.append(f"\n{selector}\n{{{compact_declarations};}}")
    return "@media  ( max-width : 420px ) {" + "".join(rule_fragments) + "\n}"


def _assert_ai_actions_narrow_reflow_contract(
    css: str,
) -> dict[str, dict[str, str]]:
    rules = _parse_rules(_narrow_media_body(css))
    assert AI_ACTIONS_NARROW_REFLOW_CONTRACT.keys() <= rules.keys()
    for selector, required_declarations in AI_ACTIONS_NARROW_REFLOW_CONTRACT.items():
        for property_name, expected_value in required_declarations.items():
            actual_value = rules[selector].get(property_name)
            assert actual_value == expected_value, (
                f"{selector} requires {property_name}: {expected_value}; "
                f"got {actual_value}"
            )
    return rules


def _reformatted_ai_actions_narrow_reflow_contract(css: str) -> str:
    rules = _assert_ai_actions_narrow_reflow_contract(css)
    rule_fragments = []
    for selector in reversed(tuple(AI_ACTIONS_NARROW_REFLOW_CONTRACT)):
        declarations = rules[selector]
        compact_declarations = ";".join(
            f"{property_name}:{value}"
            for property_name, value in reversed(tuple(declarations.items()))
        )
        rule_fragments.append(f"\n{selector}\n{{{compact_declarations};}}")
    return "@media  ( max-width : 420px ) {" + "".join(rule_fragments) + "\n}"


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
    _assert_evidence_narrow_contract(css)


def test_evidence_narrow_contract_ignores_insignificant_formatting():
    css = read("app/globals.css")
    reformatted_css = _reformatted_narrow_contract(css)

    assert reformatted_css != css
    _assert_evidence_narrow_contract(reformatted_css)


def test_evidence_narrow_contract_rejects_missing_required_declaration():
    css = read("app/globals.css")
    narrow_body = _narrow_media_body(css)
    mutated_body, mutation_count = re.subn(
        r"overflow-wrap\s*:\s*anywhere\s*;",
        "",
        narrow_body,
        count=1,
    )

    assert mutation_count == 1
    mutated_css = css.replace(narrow_body, mutated_body, 1)
    with pytest.raises(AssertionError, match="overflow-wrap"):
        _assert_evidence_narrow_contract(mutated_css)


def test_ai_actions_status_and_toolbar_reflow_at_narrow_width():
    css = read("app/globals.css")
    _assert_ai_actions_narrow_reflow_contract(css)


def test_ai_actions_narrow_reflow_contract_ignores_formatting_and_selector_order():
    css = read("app/globals.css")
    reformatted_css = _reformatted_ai_actions_narrow_reflow_contract(css)

    assert reformatted_css != css
    _assert_ai_actions_narrow_reflow_contract(reformatted_css)


def test_ai_actions_narrow_reflow_rejects_missing_align_items():
    css = read("app/globals.css")
    narrow_body = _narrow_media_body(css)
    mutated_body, mutation_count = re.subn(
        r"align-items\s*:\s*flex-start\s*;",
        "",
        narrow_body,
        count=1,
    )

    assert mutation_count == 1
    mutated_css = css.replace(narrow_body, mutated_body, 1)
    with pytest.raises(AssertionError, match="align-items"):
        _assert_ai_actions_narrow_reflow_contract(mutated_css)


def test_ai_actions_narrow_reflow_rejects_missing_flex_direction():
    css = read("app/globals.css")
    narrow_body = _narrow_media_body(css)
    mutated_body, mutation_count = re.subn(
        r"flex-direction\s*:\s*column\s*;",
        "",
        narrow_body,
        count=1,
    )

    assert mutation_count == 1
    mutated_css = css.replace(narrow_body, mutated_body, 1)
    with pytest.raises(AssertionError, match="flex-direction"):
        _assert_ai_actions_narrow_reflow_contract(mutated_css)


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
