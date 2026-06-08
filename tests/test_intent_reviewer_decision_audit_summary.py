import ast
import json
from pathlib import Path

import intent_reviewer_decision_audit_summary as audit


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


REQUIRED_TOP_LEVEL_FIELDS = {
    "day",
    "title",
    "status",
    "review_scope",
    "source_chain",
    "decision_summary",
    "evidence_exports",
    "safety_invariants",
    "traceability_map",
    "reviewer_notes",
    "reports",
}


def test_reviewer_decision_audit_summary_report_is_deterministic():
    first = audit.build_reviewer_decision_audit_summary_report()
    second = audit.build_reviewer_decision_audit_summary_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == audit.CREATED_AT
    assert {item["created_at"] for item in first["evidence_exports"]} == {
        "2026-06-08T00:00:00Z"
    }


def test_reviewer_decision_audit_summary_has_required_fields_and_status():
    report = audit.build_reviewer_decision_audit_summary_report()

    assert REQUIRED_TOP_LEVEL_FIELDS.issubset(report)
    assert audit.validate_reviewer_decision_audit_summary_report(report) == []
    assert report["day"] == "Day82"
    assert report["title"] == "Reviewer Decision Audit Summary / Queue Evidence Export"
    assert report["status"] == "REVIEW_READY"
    assert report["overall_status"] == "PASS"
    assert report["decision_summary"]["queue_record_count"] == 5
    assert report["decision_summary"]["evidence_export_count"] == 5


def test_reviewer_decision_audit_summary_preserves_required_invariants():
    report = audit.build_reviewer_decision_audit_summary_report()
    invariants = report["safety_invariants"]

    assert invariants["allowed_to_execute"] is False
    assert invariants["dry_run_only"] is True
    assert invariants["execution_unlock_supported"] is False
    assert invariants["device_connection_allowed"] is False
    assert invariants["ssh_allowed"] is False
    assert invariants["live_command_allowed"] is False
    assert invariants["network_change_allowed"] is False
    assert invariants["ai_runtime_allowed"] is False
    assert invariants["dashboard_action_allowed"] is False
    assert invariants["all_day82_records_preserve_required_flags"] is True
    assert invariants["mapped_task_executed"] is False
    assert invariants["live_execution_used"] is False

    for record in report["evidence_exports"]:
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["device_connection_allowed"] is False
        assert record["ssh_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["network_change_allowed"] is False
        assert record["ai_runtime_allowed"] is False
        assert record["dashboard_action_allowed"] is False
        for field, expected in audit.REQUIRED_EXECUTION_FLAGS:
            assert record["safety_invariants"][field] is expected


def test_reviewer_decision_audit_summary_traceability_map_includes_day79_to_day82():
    report = audit.build_reviewer_decision_audit_summary_report()
    traceability_text = json.dumps(report["traceability_map"], sort_keys=True)

    for day in ("Day79", "Day80", "Day81", "Day82"):
        assert day in traceability_text
        assert day in report["source_chain"][int(day[-2:]) - 79]


def test_reviewer_decision_audit_summary_validation_flags_unlock_attempts():
    exports = audit.build_queue_evidence_exports()
    exports[0]["allowed_to_execute"] = True
    exports[0]["dry_run_only"] = False
    exports[0]["execution_unlock_supported"] = True
    exports[0]["device_connection_allowed"] = True
    exports[0]["ssh_allowed"] = True
    exports[0]["live_command_allowed"] = True
    exports[0]["network_change_allowed"] = True
    exports[0]["ai_runtime_allowed"] = True
    exports[0]["dashboard_action_allowed"] = True

    errors = audit.validate_reviewer_decision_audit_summary_exports(exports)

    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("dry_run_only must be true" in error for error in errors)
    assert any("execution_unlock_supported must be false" in error for error in errors)
    assert any("device_connection_allowed must be false" in error for error in errors)
    assert any("ssh_allowed must be false" in error for error in errors)
    assert any("live_command_allowed must be false" in error for error in errors)
    assert any("network_change_allowed must be false" in error for error in errors)
    assert any("ai_runtime_allowed must be false" in error for error in errors)
    assert any("dashboard_action_allowed must be false" in error for error in errors)


def test_reviewer_decision_audit_summary_reports_are_written(tmp_path):
    report = audit.build_reviewer_decision_audit_summary_report()
    json_path, html_path = audit.write_reviewer_decision_audit_summary_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day82_reviewer_decision_audit_summary.json"
    assert html_path == tmp_path / "reports/lab-summary/day82_reviewer_decision_audit_summary.html"
    assert json_path.exists()
    assert html_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Reviewer Decision Audit Summary / Queue Evidence Export" in html
    assert "AI runtime allowed values" in html
    assert "Day82 Reviewer Decision Audit Summary" in html


def test_reviewer_decision_audit_summary_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(audit.__file__)
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
