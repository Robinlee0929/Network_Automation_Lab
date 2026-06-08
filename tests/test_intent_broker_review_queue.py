import ast
import json
from pathlib import Path

import intent_broker_review_queue as queue


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


def test_broker_review_queue_report_is_deterministic():
    first = queue.build_broker_review_queue_report()
    second = queue.build_broker_review_queue_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == queue.CREATED_AT
    assert {item["created_at"] for item in first["queue_records"]} == {
        "2026-06-08T00:00:00Z"
    }


def test_broker_review_queue_records_have_required_fields_and_invariants():
    report = queue.build_broker_review_queue_report()
    records = report["queue_records"]

    assert len(records) == 5
    assert [record["queue_id"] for record in records] == [
        "day81-queue-001",
        "day81-queue-002",
        "day81-queue-003",
        "day81-queue-004",
        "day81-queue-005",
    ]
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["review_states"] == [
        "REJECTED_BY_BROKER",
        "QUEUED_FOR_HUMAN_REVIEW",
        "MOCK_EXECUTION_REQUEST_PREPARED",
        "REVIEW_BLOCKED_BY_POLICY",
        "REVIEW_READY_NO_EXECUTION",
    ]
    assert report["summary"]["decision_states"] == [
        "REJECT",
        "HOLD_FOR_REVIEW",
        "MOCK_ONLY",
        "POLICY_BLOCKED",
        "REVIEW_ONLY",
    ]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["summary"]["device_connection_allowed_values"] == [False]
    assert report["summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["live_command_allowed_values"] == [False]
    assert report["summary"]["mapped_task_execution_allowed_values"] == [False]
    assert report["summary"]["dashboard_action_allowed_values"] == [False]
    assert report["summary"]["report_only_values"] == [True]

    for record in records:
        assert set(queue.REQUIRED_QUEUE_FIELDS).issubset(record)
        assert record["allowed_to_execute"] is False
        assert record["dry_run_only"] is True
        assert record["execution_unlock_supported"] is False
        assert record["device_connection_allowed"] is False
        assert record["ssh_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["mapped_task_execution_allowed"] is False
        assert record["dashboard_action_allowed"] is False
        assert record["report_only"] is True
        assert record["safety_boundary"]["allowed_to_execute"] is False
        assert record["safety_boundary"]["dry_run_only"] is True
        assert record["safety_boundary"]["execution_unlock_supported"] is False
        assert record["safety_boundary"]["device_connection_allowed"] is False
        assert record["safety_boundary"]["ssh_allowed"] is False
        assert record["safety_boundary"]["live_command_allowed"] is False
        assert record["safety_boundary"]["mapped_task_execution_allowed"] is False
        assert record["safety_boundary"]["dashboard_action_allowed"] is False
        evidence_text = " ".join(record["evidence_chain"])
        assert "Day79" in evidence_text
        assert "Day80" in evidence_text
        assert "approve execution" not in record["final_recommendation"].lower()


def test_broker_review_queue_maps_day80_states_to_review_and_decision_states():
    records = {
        record["source_request_id"]: record
        for record in queue.build_broker_review_queue_records()
    }

    assert records["day80-request-001"]["review_state"] == "MOCK_EXECUTION_REQUEST_PREPARED"
    assert records["day80-request-001"]["decision_state"] == "MOCK_ONLY"
    assert records["day80-request-002"]["review_state"] == "QUEUED_FOR_HUMAN_REVIEW"
    assert records["day80-request-002"]["decision_state"] == "HOLD_FOR_REVIEW"
    assert records["day80-request-003"]["review_state"] == "REJECTED_BY_BROKER"
    assert records["day80-request-003"]["decision_state"] == "REJECT"
    assert records["day80-request-004"]["review_state"] == "REVIEW_BLOCKED_BY_POLICY"
    assert records["day80-request-004"]["decision_state"] == "POLICY_BLOCKED"
    assert records["day80-request-005"]["review_state"] == "REVIEW_READY_NO_EXECUTION"
    assert records["day80-request-005"]["decision_state"] == "REVIEW_ONLY"


def test_broker_review_queue_validation_flags_unlock_attempts():
    records = queue.build_broker_review_queue_records()
    records[0]["allowed_to_execute"] = True
    records[0]["dry_run_only"] = False
    records[0]["execution_unlock_supported"] = True
    records[0]["ssh_allowed"] = True
    records[0]["live_command_allowed"] = True
    records[0]["mapped_task_execution_allowed"] = True
    records[0]["dashboard_action_allowed"] = True
    records[0]["report_only"] = False

    errors = queue.validate_broker_review_queue_records(records)

    assert any("allowed_to_execute must be false" in error for error in errors)
    assert any("dry_run_only must be true" in error for error in errors)
    assert any("execution_unlock_supported must be false" in error for error in errors)
    assert any("ssh_allowed must be false" in error for error in errors)
    assert any("live_command_allowed must be false" in error for error in errors)
    assert any("mapped_task_execution_allowed must be false" in error for error in errors)
    assert any("dashboard_action_allowed must be false" in error for error in errors)
    assert any("report_only must be true" in error for error in errors)


def test_broker_review_queue_reports_are_written(tmp_path):
    report = queue.build_broker_review_queue_report()
    json_path, html_path = queue.write_broker_review_queue_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day81_broker_review_queue.json"
    assert html_path == tmp_path / "reports/lab-summary/day81_broker_review_queue.html"
    assert json_path.exists()
    assert html_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day81 Read-only Broker Review Queue" in html
    assert "No request is allowed to execute" in html or "no request is allowed to execute" in html
    assert "REVIEW_BLOCKED_BY_POLICY" in html
    assert "Dashboard action allowed values" in html


def test_broker_review_queue_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(queue.__file__)
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
