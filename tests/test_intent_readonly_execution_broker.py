import ast
import json
from pathlib import Path

import intent_readonly_execution_broker as broker


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


def test_readonly_execution_broker_report_is_deterministic():
    first = broker.build_readonly_execution_broker_report()
    second = broker.build_readonly_execution_broker_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == broker.CREATED_AT
    assert {item["created_at"] for item in first["broker_records"]} == {
        "2026-06-08T00:00:00Z"
    }


def test_readonly_execution_broker_records_have_required_fields_and_invariants():
    report = broker.build_readonly_execution_broker_report()
    records = report["broker_records"]

    assert len(records) >= 5
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["summary"]["device_connection_allowed_values"] == [False]
    assert report["summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["live_command_allowed_values"] == [False]

    for record in records:
        assert set(broker.REQUIRED_BROKER_FIELDS).issubset(record)
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["device_connection_allowed"] is False
        assert record["ssh_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["safety_invariants"]["allowed_to_execute"] is False
        assert record["safety_invariants"]["dry_run_only"] is True
        assert record["safety_invariants"]["execution_unlock_supported"] is False
        assert record["safety_invariants"]["device_connection_allowed"] is False
        assert record["safety_invariants"]["ssh_allowed"] is False
        assert record["safety_invariants"]["live_command_allowed"] is False


def test_valid_readonly_task_can_prepare_mock_execution_request_data_only():
    records = broker.build_readonly_execution_broker_records()
    prepared = next(
        record
        for record in records
        if record["broker_status"] == broker.MOCK_EXECUTION_REQUEST_PREPARED
    )

    assert prepared["requested_task"] == "show_interface_status"
    assert prepared["contract_check_result"] == "READONLY_CONTRACT_READY"
    mock_request = prepared["mock_execution_request"]
    assert isinstance(mock_request, dict)
    assert mock_request["execution_mode"] == "MOCK_ONLY"
    assert mock_request["live_execution"] is False
    assert mock_request["data_object_only"] is True
    assert mock_request["runnable_entrypoint"] is None
    assert "command" not in " ".join(mock_request.keys()).lower()


def test_review_unsafe_write_and_ambiguous_requests_are_not_executable():
    rows = {
        record["requested_task"]: record
        for record in broker.build_readonly_execution_broker_records()
    }

    assert rows["show_log_summary"]["broker_status"] == broker.QUEUED_FOR_REVIEW
    assert rows["show_log_summary"]["mock_execution_request"] is None
    assert rows["show_bgp_neighbors"]["broker_status"] == broker.REJECTED
    assert rows["add_firewall_rule"]["broker_status"] == broker.REJECTED
    assert rows["add_firewall_rule"]["contract_check_result"] == "BLOCKED_WRITE_ACTION"
    assert rows["needs_manual_classification"]["broker_status"] == broker.QUEUED_FOR_REVIEW
    assert rows["needs_manual_classification"]["mock_execution_request"] is None
    assert all(record["allowed_to_execute"] is False for record in rows.values())


def test_readonly_execution_broker_validation_flags_unlock_attempts():
    records = broker.build_readonly_execution_broker_records()
    records[0]["allowed_to_execute"] = True
    records[0]["dry_run_only"] = False
    records[0]["execution_unlock_supported"] = True
    records[0]["ssh_allowed"] = True
    records[0]["live_command_allowed"] = True

    errors = broker.validate_readonly_execution_broker_records(records)

    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("dry_run_only must be true" in error for error in errors)
    assert any("execution_unlock_supported must be false" in error for error in errors)
    assert any("ssh_allowed must be false" in error for error in errors)
    assert any("live_command_allowed must be false" in error for error in errors)


def test_readonly_execution_broker_reports_are_written(tmp_path):
    report = broker.build_readonly_execution_broker_report()
    json_path, html_path = broker.write_readonly_execution_broker_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day80_readonly_execution_broker.json"
    assert html_path == tmp_path / "reports/lab-summary/day80_readonly_execution_broker.html"
    assert json_path.exists()
    assert html_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day80 Read-only Execution Broker Skeleton" in html
    assert "MOCK_EXECUTION_REQUEST_PREPARED" in html
    assert "QUEUED_FOR_REVIEW" in html
    assert "REJECTED" in html


def test_readonly_execution_broker_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(broker.__file__)
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
