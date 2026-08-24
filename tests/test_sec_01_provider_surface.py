from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


LEGACY_DRAFT_ROUTES = {
    "app/api/ai/meeting-summary/route.ts",
    "app/api/ai/requirement-analysis/route.ts",
    "app/api/ai/kb-qa/route.ts",
}

LEGACY_NODE_ROUTES = {
    "app/api/automation/ai/meeting-summary/route.ts",
    "app/api/automation/ai/requirement-analysis/route.ts",
    "app/api/automation/ai/kb-qa/route.ts",
}

PROVIDER_ROUTE_INVENTORY = LEGACY_DRAFT_ROUTES | LEGACY_NODE_ROUTES | {
    "app/api/network/ai/analyze-report/route.ts",
    "app/api/network/ai/parse-request/route.ts",
}


def test_provider_route_inventory_and_shared_legacy_gate_are_accounted_for() -> None:
    discovered = set()
    provider_markers = (
        "generateAiDraft",
        "generateAiNodeJson",
        "analyzeReportWithAi",
        "parseNetworkRequestWithAi",
    )
    for route in (ROOT / "app" / "api").rglob("route.ts"):
        text = route.read_text(encoding="utf-8")
        if any(marker in text for marker in provider_markers):
            discovered.add(route.relative_to(ROOT).as_posix())

    assert discovered == PROVIDER_ROUTE_INVENTORY

    for route in LEGACY_DRAFT_ROUTES:
        assert "generateAiDraft" in read(route)
    for route in LEGACY_NODE_ROUTES:
        assert "generateAiNodeJson" in read(route)

    route_handler = read("lib/ai/routeHandler.ts")
    assert route_handler.count("assertLegacyAiProviderEnabled();") == 2
    first_guard = route_handler.index("assertLegacyAiProviderEnabled();")
    first_client = route_handler.index("getOpenAIClient();", first_guard)
    second_guard = route_handler.index("assertLegacyAiProviderEnabled();", first_guard + 1)
    second_client = route_handler.index("getOpenAIClient();", second_guard)
    assert first_guard < first_client < second_guard < second_client


def test_network_routes_keep_separate_provider_policies() -> None:
    analyze_route = read("app/api/network/ai/analyze-report/route.ts")
    analyze_helper = read("lib/network-ai/aiNode.ts").split(
        "export async function analyzeReportWithAi", maxsplit=1
    )[1]
    parse_route = read("app/api/network/ai/parse-request/route.ts")

    assert "assertLegacyAiProviderEnabled" in analyze_route
    assert analyze_route.index("assertLegacyAiProviderEnabled();") < analyze_route.index(
        "request.json()"
    )
    assert "MAX_ANALYZE_REPORT_CHARS = 20_000" in analyze_route
    assert "Object.keys(value).length === 1" in analyze_route
    assert "deviceContext" not in analyze_route
    assert "reportId?:" not in analyze_route
    assert analyze_helper.index("assertLegacyAiProviderEnabled();") < analyze_helper.index(
        "getAvailableActions()"
    )

    assert "isNetworkAiProviderDemoEnabled" in parse_route
    assert "NETWORK_AI_PROVIDER_DEMO_ENABLED" not in analyze_route
    assert "LEGACY_AI_PROVIDER_ENABLED" not in parse_route


def test_provider_outputs_are_strict_and_keep_human_review() -> None:
    ai_schemas = read("lib/ai/schemas.ts")
    network_schemas = read("lib/network-ai/schemas.ts")
    route_handler = read("lib/ai/routeHandler.ts")

    assert "hasExactKeys" in ai_schemas
    assert "validateAiNodeOutput" in ai_schemas
    assert "ensureHumanReview" in ai_schemas
    assert "validateAiNodeOutput<TOutput>(nodeType, parsed)" in route_handler
    assert "AI report analyzer output contained an unsupported field." in network_schemas
    assert "AI request parser output contained an unsupported field." in network_schemas


def test_parse_results_is_retired_without_reading_the_store() -> None:
    route = read("app/api/network/ai/parse-results/route.ts")

    assert "status: 410" in route
    assert "retired" in route
    assert "parseResultStore" not in route
    assert "listParseResultRecords" not in route
    assert "parseResults:" not in route


def test_legacy_pages_hide_submission_controls_by_default() -> None:
    for path, tabs in [
        ("app/ai/page.tsx", "<AiTabs />"),
        ("app/automation/ai-nodes/page.tsx", "<AiNodeTabs />"),
    ]:
        page = read(path)
        assert 'export const dynamic = "force-dynamic"' in page
        assert "isLegacyAiProviderEnabled" in page
        assert "legacyAiProviderEnabled ?" in page
        assert page.index("legacyAiProviderEnabled ?") < page.index(tabs)
        assert "disabled by default" in page
        assert "LEGACY_AI_PROVIDER_ENABLED=1" in page
        assert "configured external" in page
        assert "device" in page and "command" in page


def test_public_configuration_and_docs_distinguish_both_policies() -> None:
    env_example = read(".env.example")
    readme = read("README.md")
    security = read("SECURITY.md")

    assert "LEGACY_AI_PROVIDER_ENABLED=0" in env_example
    assert "NETWORK_AI_PROVIDER_DEMO_ENABLED=0" in env_example
    assert "OPENAI_API_KEY=" in env_example
    assert "sk-" not in env_example

    for document in (readme, security):
        assert "canonical" in document.lower()
        assert "provider-free" in document
        assert "NETWORK_AI_PROVIDER_DEMO_ENABLED" in document
        assert "LEGACY_AI_PROVIDER_ENABLED" in document
        assert "OPENAI_API_KEY" in document
        assert "feature authorization" in document
