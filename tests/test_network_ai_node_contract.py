from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_network_ai_action_allowlist_is_fixed_and_no_unknown_action_fabrication():
    actions = read("lib/network-ai/actions.ts")
    parser = read("lib/network-ai/aiNode.ts")

    for action_id in [
        "baseline_check",
        "wan_lan_check",
        "interface_status_check",
        "backup_config",
        "environment_check",
    ]:
        assert action_id in actions

    assert "recommendedActionId must be exactly one ID from availableActions or null" in parser
    assert "isAvailableActionId" in parser
    assert "recommendedActionId" in parser
    assert "blocked" in parser


def test_network_ai_routes_are_server_side_and_do_not_return_api_keys_to_frontend():
    openai_client = read("lib/ai/openaiClient.ts")
    analyze_route = read("app/api/network/ai/analyze-report/route.ts")
    parse_route = read("app/api/network/ai/parse-request/route.ts")
    frontend_sources = [
        read("components/network/DayResultsClient.tsx"),
        read("components/network/AiActionsClient.tsx"),
        read("components/network/ReportsClient.tsx"),
        read("components/network/JobsClient.tsx"),
    ]

    assert "process.env.OPENAI_API_KEY" in openai_client
    assert "gpt-5-mini" in openai_client
    assert "analyzeReportWithAi" in analyze_route
    assert "parseNetworkRequestWithAi" in parse_route
    assert all("OPENAI_API_KEY" not in source for source in frontend_sources)
    assert all('from "openai"' not in source for source in frontend_sources)


def test_network_ai_job_adapter_creates_jobs_without_execution_paths():
    jobs = read("lib/network-ai/jobs.ts")
    create_route = read("app/api/network/jobs/create/route.ts")
    combined = f"{jobs}\n{create_route}".lower()

    assert "pending_approval" in jobs
    assert "ready" in jobs
    assert "createnetworkjob" in create_route.lower()
    forbidden_terms = ["ssh", "paramiko", "netmiko", "subprocess", "exec(", "spawn("]
    for term in forbidden_terms:
        assert term not in combined


def test_network_ai_readme_documents_safe_flow_and_env_contract():
    readme = read("README.md")
    gitignore = read(".gitignore")
    env_example = read(".env.example")

    assert "Network Automation AI Node" in readme
    assert "parse -> recommend -> validate -> create job -> approve -> execute" in readme
    assert "AI Node cannot" in readme
    assert "OPENAI_API_KEY=" in env_example
    assert "OPENAI_MODEL=gpt-5-mini" in env_example
    assert ".env.local" in gitignore
