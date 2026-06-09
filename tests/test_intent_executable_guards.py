import ast
import json
from pathlib import Path

import intent_executable_guards as day92


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "routeros_api",
    "librouteros",
    "socket",
    "subprocess",
    "requests",
    "telnetlib",
    "asyncssh",
}


class FakeReadOnlyExecutor:
    def __init__(self):
        self.invocations = []

    def __call__(self, request):
        self.invocations.append(request.request_id)
        return day92.deterministic_read_only_executor(request)


def test_day92_report_is_deterministic_and_guard_enforced():
    first = day92.build_day92_real_adapter_executable_guards_report()
    second = day92.build_day92_real_adapter_executable_guards_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 92
    assert first["day_id"] == "Day92"
    assert first["title"] == "Real Adapter Executable Guards"
    assert first["status"] == "PASS"
    assert first["phase"] == "GUARD_ENFORCED"
    assert first["safety_level"] == "offline_deterministic_guard"
    assert first["no_real_device_access"] is True
    assert first["no_ssh"] is True
    assert first["no_subprocess"] is True
    assert first["no_socket"] is True
    assert first["no_real_adapter"] is True
    assert first["adapter_implementation_added"] is False
    assert first["rejected_adapter_invocations"] == 0
    assert day92.validate_day92_real_adapter_executable_guards_report(first) == []


def test_day92_all_required_dangerous_requests_are_rejected_before_executor():
    guard = day92.ExecutableGuard()
    executor = FakeReadOnlyExecutor()
    dangerous_actions = [
        "reboot_device",
        "reset_configuration",
        "disable_interface",
        "enable_interface",
        "add_firewall_rule",
        "remove_firewall_rule",
        "change_ip_address",
        "modify_route",
        "modify_wireguard_peer",
        "modify_vrrp",
        "run_arbitrary_command",
        "export_secret",
    ]

    for index, action in enumerate(dangerous_actions, start=1):
        request = day92.GuardRequest(f"deny-{index:03d}", action, action.replace("_", " "), {})
        result = day92.execute_guarded_request(request, executor, guard)
        decision = result["guard_decision"]
        assert decision["decision"] == "REJECT"
        assert decision["allowed"] is False
        assert decision["reason_code"] in {"DANGEROUS_ACTION_REJECTED", "SECRET_MATERIAL_DETECTED"}
        assert decision["matched_rule_name"]
        assert decision["evidence"]
        assert decision["adapter_invocation_allowed"] is False
        assert result["executor_invoked"] is False

    assert executor.invocations == []


def test_day92_unknown_and_sensitive_requests_reject_by_default():
    guard = day92.ExecutableGuard()
    executor = FakeReadOnlyExecutor()
    requests = [
        day92.GuardRequest("unknown", "inventory_lookup", "Maybe inspect something", {}),
        day92.GuardRequest("password", "collect_interface_status", "Collect status", {"password": "REDACTED"}),
        day92.GuardRequest("token", "read_route_summary", "Read route summary token", {}),
        day92.GuardRequest("private-key", "read_system_resource_summary", "private key requested", {}),
        day92.GuardRequest("mutation", "read_route_summary", "Please apply read route summary", {}),
    ]

    results = [day92.execute_guarded_request(request, executor, guard) for request in requests]

    assert [item["guard_decision"]["decision"] for item in results] == ["REJECT"] * len(requests)
    assert [item["executor_invoked"] for item in results] == [False] * len(requests)
    assert {item["guard_decision"]["reason_code"] for item in results} == {
        "UNKNOWN_ACTION_REJECTED",
        "SECRET_MATERIAL_DETECTED",
        "MUTATION_VERB_REJECTED",
    }
    assert executor.invocations == []


def test_day92_allowlisted_read_only_requests_invoke_fake_executor_once_each():
    guard = day92.ExecutableGuard()
    executor = FakeReadOnlyExecutor()
    requests = [
        day92.GuardRequest(f"allow-{index:03d}", action, action.replace("_", " "), {})
        for index, action in enumerate(day92.SAFE_READ_ONLY_ACTIONS, start=1)
    ]

    results = [day92.execute_guarded_request(request, executor, guard) for request in requests]

    assert [item["guard_decision"]["decision"] for item in results] == ["ALLOW"] * len(requests)
    assert [item["executor_invoked"] for item in results] == [True] * len(requests)
    assert executor.invocations == [request.request_id for request in requests]
    assert "PRIVATEKEY" not in json.dumps(results).upper()
    assert "PrivateKey" not in json.dumps(results)
    assert "private key" not in json.dumps(results).lower()
    assert "REDACTED" in json.dumps(results)


def test_day92_reports_are_written_without_action_controls(tmp_path):
    report = day92.build_day92_real_adapter_executable_guards_report()
    json_path, html_path = day92.write_day92_real_adapter_executable_guards_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day92_real_adapter_executable_guards_report.json"
    assert html_path == tmp_path / "reports/lab-summary/day92_real_adapter_executable_guards_report.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert data["phase"] == "GUARD_ENFORCED"
    assert data["rejected_adapter_invocations"] == 0
    assert "Real Adapter Executable Guards" in html
    assert "GUARD_ENFORCED" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day92_module_has_no_forbidden_runtime_imports_or_network_io():
    source_path = Path(day92.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    assert ".connect(" not in source
    assert ".send(" not in source
    assert ".recv(" not in source
    assert "subprocess." not in source
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
