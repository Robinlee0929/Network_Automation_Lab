import ast
from pathlib import Path

import intent_offline_mock_runtime as runtime


UNSAFE_IMPORTS = {
    "netmiko",
    "openai",
    "paramiko",
    "requests",
    "socket",
    "speech",
    "subprocess",
}


def test_mock_runtime_output_is_deterministic():
    first = runtime.build_mock_runtime_report()
    second = runtime.build_mock_runtime_report()

    assert first == second
    assert first["overall_status"] == "PASS"
    assert first["reviewer_status"] == "REVIEW_READY"


def test_mock_runtime_never_allows_live_execution():
    report = runtime.build_mock_runtime_report()

    assert report["execution_mode"] in {"offline_mock", "dry_run_only"}
    assert report["live_execution_allowed"] is False
    assert report["no_live_execution_occurred"] is True
    assert report["openai_api_used"] is False
    assert report["voice_integration_used"] is False
    assert report["ssh_used"] is False
    assert report["config_json_read"] is False
    assert report["mapped_task_executed"] is False

    for scenario in report["mock_scenarios"]:
        assert scenario["execution_mode"] in {"offline_mock", "dry_run_only"}
        assert scenario["live_execution_allowed"] is False
        record = scenario["mock_execution_record"]
        assert record["real_command_executed"] is False
        assert record["mapped_task_executed"] is False
        assert record["ssh_used"] is False
        assert record["device_access_used"] is False
        assert record["network_change_made"] is False


def test_blocked_live_action_scenarios_remain_blocked():
    report = runtime.build_mock_runtime_report()
    blocked = [
        scenario
        for scenario in report["mock_scenarios"]
        if scenario["safety_category"] == "blocked_live_action"
    ]

    assert len(blocked) == report["summary"]["blocked_live_action_scenarios"]
    assert len(blocked) >= 2
    assert any("VRRP" in scenario["input_text"] for scenario in blocked)
    assert all(scenario["live_execution_allowed"] is False for scenario in blocked)


def test_mock_runtime_module_has_no_unsafe_imports_or_config_dependency():
    source_path = Path(runtime.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)
    assert "config.json" not in source
    assert "network_lab" not in source
