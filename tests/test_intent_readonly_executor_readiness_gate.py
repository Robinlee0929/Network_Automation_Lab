import ast
from copy import deepcopy
import json
from pathlib import Path

import intent_readonly_executor_readiness_gate as gate


UNSAFE_IMPORTS = {
    "paramiko",
    "netmiko",
    "asyncssh",
    "socket",
    "telnetlib",
    "requests",
    "httpx",
    "openai",
    "subprocess",
    "os",
    "fabric",
    "scrapli",
}


def test_readonly_executor_readiness_gate_report_is_deterministic():
    first = gate.build_readonly_executor_readiness_gate_report()
    second = gate.build_readonly_executor_readiness_gate_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == gate.CREATED_AT
    assert first["overall_status"] == "PASS"
    assert first["readiness_state"] == gate.READINESS_REVIEW_READY


def test_readonly_executor_readiness_gate_preserves_safety_invariants():
    report = gate.build_readonly_executor_readiness_gate_report()

    assert gate.validate_readonly_executor_readiness_gate_report(report) == []
    assert report["executor_allowed"] is False
    assert report["readonly_executor_candidate"] is True
    assert report["live_execution_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["device_access_allowed"] is False
    assert report["ai_runtime_allowed"] is False
    assert report["dashboard_action_allowed"] is False
    assert report["mapped_task_execution_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_unlock_supported"] is False

    for field in gate.REQUIRED_FALSE_FLAGS:
        assert report[field] is False
        assert report["safety_invariants"][field] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ai_sdk_dependency_used"] is False
    assert report["safety_invariants"]["routeros_command_path_added"] is False
    assert report["safety_invariants"]["external_command_execution_added"] is False


def test_candidate_does_not_imply_executor_allowed():
    report = gate.build_readonly_executor_readiness_gate_report()

    assert report["readonly_executor_candidate"] is True
    assert report["executor_allowed"] is False
    assert report["candidate_scope"]["candidate_means_execution_allowed"] is False

    tampered = deepcopy(report)
    tampered["executor_allowed"] = True
    tampered["safety_invariants"]["executor_allowed"] = True

    errors = gate.validate_readonly_executor_readiness_gate_report(tampered)

    assert any("executor_allowed must be false" in error for error in errors)
    assert any("readonly_executor_candidate must never imply executor_allowed" in error for error in errors)


def test_no_ssh_live_device_ai_dashboard_action_flags_are_enabled():
    report = gate.build_readonly_executor_readiness_gate_report()

    forbidden_flags = {
        "live_execution_allowed",
        "ssh_allowed",
        "device_access_allowed",
        "ai_runtime_allowed",
        "dashboard_action_allowed",
        "mapped_task_execution_allowed",
        "approval_unlock_allowed",
        "execution_unlock_supported",
    }
    for field in forbidden_flags:
        assert report[field] is False
        assert report["safety_invariants"][field] is False


def test_day79_to_day82_evidence_chain_completeness():
    report = gate.build_readonly_executor_readiness_gate_report()

    assert report["summary"]["source_days"] == ["Day79", "Day80", "Day81", "Day82"]
    assert report["summary"]["day79_contract_records"] == 5
    assert report["summary"]["day80_broker_records"] == 5
    assert report["summary"]["day81_queue_records"] == 5
    assert report["summary"]["day82_evidence_exports"] == 5
    assert {check["status"] for check in report["readiness_checks"]} == {"PASS"}

    chain_text = json.dumps(report["evidence_chain"], sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82", "Day83"):
        assert day in chain_text


def test_readonly_executor_readiness_gate_reports_are_written(tmp_path):
    report = gate.build_readonly_executor_readiness_gate_report()
    json_path, html_path = gate.write_readonly_executor_readiness_gate_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day83_readonly_executor_readiness_gate.json"
    assert html_path == tmp_path / "reports/lab-summary/day83_readonly_executor_readiness_gate.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day83 Read-only Executor Readiness Gate" in html
    assert "Executor allowed" in html
    assert "Read-only executor candidate" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_readonly_executor_readiness_gate_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(gate.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "subprocess.run" not in source
    assert "os.system" not in source
    assert "exec(" not in source
    assert "eval(" not in source
