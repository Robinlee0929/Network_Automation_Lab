from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_ai_project_assistant_env_files_do_not_commit_real_key() -> None:
    env_example = read(".env.example")
    gitignore = read(".gitignore")

    assert "OPENAI_API_KEY=" in env_example
    assert "OPENAI_MODEL=gpt-5-mini" in env_example
    assert "sk-" not in env_example
    assert ".env.*" in gitignore
    assert "!.env.example" in gitignore


def test_ai_project_assistant_server_routes_are_present() -> None:
    expected_routes = [
        "app/api/ai/meeting-summary/route.ts",
        "app/api/ai/requirement-analysis/route.ts",
        "app/api/ai/kb-qa/route.ts",
    ]

    for route in expected_routes:
        text = read(route)
        assert "export async function POST" in text
        assert "generateAiDraft" in text
        assert "validationError" in text


def test_automation_ai_node_routes_are_present() -> None:
    expected_routes = [
        "app/api/automation/ai/meeting-summary/route.ts",
        "app/api/automation/ai/requirement-analysis/route.ts",
        "app/api/automation/ai/kb-qa/route.ts",
    ]

    for route in expected_routes:
        text = read(route)
        assert "export async function POST" in text
        assert "generateAiNodeJson" in text
        assert "validationError" in text


def test_ai_project_assistant_keeps_openai_key_server_side() -> None:
    component_files = [
        *list((ROOT / "components" / "ai").glob("*.tsx")),
        *list((ROOT / "components" / "automation" / "ai-nodes").glob("*.tsx")),
    ]
    assert component_files

    for component in component_files:
        text = component.read_text(encoding="utf-8")
        assert "OPENAI_API_KEY" not in text
        assert "process.env" not in text
        assert "openai" not in text.lower()

    server_text = read("lib/ai/openaiClient.ts")
    assert "process.env.OPENAI_API_KEY" in server_text
    assert "new OpenAI({ apiKey })" in server_text


def test_ai_project_assistant_validators_and_prompts_preserve_safety_copy() -> None:
    validators = read("lib/ai/validators.ts")
    prompts = read("lib/ai/prompts.ts")

    assert "MAX_INPUT_CHARS = 20000" in validators
    assert "不可為空" in validators
    assert "AI 草稿，需人工確認" in prompts
    assert "不要編造" in prompts
    assert "目前提供的文件內容不足以回答" in prompts


def test_automation_ai_node_schemas_and_prompts_are_workflow_ready() -> None:
    schemas = read("lib/ai/schemas.ts")
    prompts = read("lib/ai/prompts.ts")
    route_handler = read("lib/ai/routeHandler.ts")
    page = read("app/automation/ai-nodes/page.tsx")
    readme = read("README.md")

    for field in [
        "rawJson",
        "nodeType",
        "MeetingSummaryNodeOutput",
        "RequirementAnalysisNodeOutput",
        "KnowledgeQaNodeOutput",
        "needsHumanReview",
    ]:
        assert field in schemas

    assert "只輸出 JSON object" in prompts
    assert "insufficientInfo 必須是 true" in prompts
    assert "JSON.parse" in route_handler
    assert "ensureHumanReview" in route_handler
    assert "自動化平台 AI 節點 MVP" in page
    assert "intended human-guided flow" in readme
    assert "execution capabilities remain gated" in readme
