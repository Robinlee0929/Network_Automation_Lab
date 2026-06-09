import ast
import json
from pathlib import Path

import intent_real_adapter_safety_scaffold as day91


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


def test_day91_scaffold_output_is_deterministic_and_scaffold_only():
    first = day91.build_day91_real_adapter_safety_scaffold()
    second = day91.build_day91_real_adapter_safety_scaffold()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 91
    assert first["day_id"] == "Day91"
    assert first["title"] == "Real Adapter Safety Scaffold"
    assert first["status"] == "SCAFFOLD_ONLY"
    assert first["overall_decision"] == "PASS"
    assert first["day90_gate"]["decision"] == "CONDITIONAL_GO"
    assert day91.validate_day91_real_adapter_safety_scaffold(first) == []


def test_day91_dangerous_actions_are_denied_by_default():
    report = day91.build_day91_real_adapter_safety_scaffold()

    assert report["dangerous_actions"]
    categories = {item["category"] for item in report["dangerous_actions"]}
    for expected in (
        "configuration write",
        "firewall change",
        "route change",
        "interface disable/enable",
        "VRRP modification",
        "WireGuard peer modification",
        "reboot",
        "reset configuration",
        "raw command execution",
        "file upload/download to device",
        "credential export",
        "arbitrary command passthrough",
    ):
        assert expected in categories

    for action in report["dangerous_actions"]:
        assert action["decision"] == "DENY"
        assert action["allowed"] is False
        assert action["denied_by_default"] is True
        assert action["proof_state"] == "STRUCTURALLY_BLOCKED"


def test_day91_read_only_candidates_are_future_only_pending_guards():
    report = day91.build_day91_real_adapter_safety_scaffold()

    assert report["read_only_candidates"]
    for candidate in report["read_only_candidates"]:
        assert candidate["execution_state"] == "NOT_EXECUTABLE"
        assert candidate["guard_state"] == "PENDING_GUARD"
        assert candidate["scope_state"] == "FUTURE_ONLY"
        assert candidate["allowed_to_execute"] is False
        assert candidate["live_read_allowed"] is False


def test_day91_invariants_block_transport_credentials_and_live_device_contact():
    report = day91.build_day91_real_adapter_safety_scaffold()
    invariants = report["invariants"]

    assert invariants["fail_closed_default"] is True
    assert invariants["live_read_allowed"] is False
    assert invariants["write_allowed"] is False
    assert invariants["raw_command_allowed"] is False
    assert invariants["credential_required"] is False
    assert invariants["transport_required"] is False
    assert invariants["real_device_contact_allowed"] is False

    blocked = report["blocked_imports_or_capabilities"]
    assert blocked
    assert all(item["present"] is False for item in blocked)
    assert all(item["allowed"] is False for item in blocked)


def test_day91_evidence_chain_and_next_required_days_are_locked():
    report = day91.build_day91_real_adapter_safety_scaffold()
    chain_text = json.dumps(report["evidence_chain"], sort_keys=True)

    assert "Day90" in chain_text
    assert "CONDITIONAL_GO" in chain_text
    assert "Day91" in chain_text
    assert "scaffold" in chain_text.lower()
    assert [item["day"] for item in report["next_required_days"]] == [
        "Day92",
        "Day93",
        "Day94",
        "Day95",
        "Day96",
    ]


def test_day91_reports_are_written_without_action_controls(tmp_path):
    report = day91.build_day91_real_adapter_safety_scaffold()
    json_path, html_path = day91.write_day91_real_adapter_safety_scaffold_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day91_real_adapter_safety_scaffold.json"
    assert html_path == tmp_path / "reports/lab-summary/day91_real_adapter_safety_scaffold.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Real Adapter Safety Scaffold" in html
    assert "live-read not allowed" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day91_module_has_no_forbidden_runtime_imports_or_network_io():
    source_path = Path(day91.__file__)
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
