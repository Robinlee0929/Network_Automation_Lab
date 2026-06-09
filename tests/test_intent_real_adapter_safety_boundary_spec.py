import ast
import json
from pathlib import Path

import intent_real_adapter_safety_boundary_spec as day89


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


def test_day89_report_is_deterministic_and_design_only():
    first = day89.build_real_adapter_safety_boundary_spec_report()
    second = day89.build_real_adapter_safety_boundary_spec_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 89
    assert first["title"] == "Real Adapter Safety Boundary Spec"
    assert first["phase"] == "DESIGN_ONLY"
    assert first["status"] == "PASS"
    assert first["safety_boundary_locked"] is True


def test_day89_required_safety_flags_remain_locked():
    report = day89.build_real_adapter_safety_boundary_spec_report()

    assert day89.validate_real_adapter_safety_boundary_spec(report) == []
    assert report["implementation_allowed"] is False
    assert report["live_device_access_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["config_change_allowed"] is False
    assert report["command_execution_allowed"] is False
    assert report["reviewer_decision_required"] is True
    assert report["adapter_scope"] == "read-only evidence collection only"


def test_day89_blocks_destructive_write_and_fallback_capabilities():
    report = day89.build_real_adapter_safety_boundary_spec_report()
    blocked = {item["capability"]: item for item in report["blocked_capabilities"]}

    for capability in day89.BLOCKED_CAPABILITIES:
        assert capability in blocked
        assert blocked[capability]["allowed"] is False

    assert "configuration changes" in blocked
    assert "firewall changes" in blocked
    assert "interface disable/enable" in blocked
    assert "reboot/reset" in blocked
    assert "arbitrary command execution" in blocked
    assert "write-mode SSH sessions" in blocked
    assert "destructive RouterOS commands" in blocked
    assert "fallback to non-allowlisted commands" in blocked


def test_day89_allowed_capabilities_are_spec_level_only():
    report = day89.build_real_adapter_safety_boundary_spec_report()
    allowed = {item["capability"]: item for item in report["allowed_capabilities"]}

    for capability in day89.ALLOWED_CAPABILITIES:
        assert capability in allowed
        assert allowed[capability]["allowed"] is True
        assert allowed[capability]["scope"] == "SPEC_ONLY"

    allowed_text = " ".join(allowed).lower()
    assert "ssh" not in allowed_text
    assert "routeros connection" not in allowed_text
    assert "live implementation" not in allowed_text
    assert "execute" not in allowed_text


def test_day89_invariants_cover_default_deny_review_evidence_and_fail_closed():
    report = day89.build_real_adapter_safety_boundary_spec_report()
    invariants = set(report["required_invariants"])

    assert "default deny" in invariants
    assert "no command may run unless allowlisted" in invariants
    assert "no command may mutate device state" in invariants
    assert "no secret-bearing output may be stored unredacted" in invariants
    assert "every future live read-only run must produce evidence" in invariants
    assert "every future live read-only run must be reviewer-gated" in invariants
    assert "adapter errors must fail closed" in invariants
    assert "design-only reports must not imply live readiness" in invariants


def test_day89_reports_are_written_without_action_controls(tmp_path):
    report = day89.build_real_adapter_safety_boundary_spec_report()
    json_path, html_path = day89.write_real_adapter_safety_boundary_spec_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day89_real_adapter_safety_boundary_spec.json"
    assert html_path == tmp_path / "reports/lab-summary/day89_real_adapter_safety_boundary_spec.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Real Adapter Safety Boundary Spec" in html
    assert "PASS / DESIGN_ONLY" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day89_module_has_no_forbidden_runtime_imports_or_network_io():
    source_path = Path(day89.__file__)
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
