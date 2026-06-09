import ast
import json
from pathlib import Path

import intent_mock_adapter_evidence_binding as day85
from intent_readonly_executor_adapter_contract import (
    validate_adapter_request_shape,
    validate_adapter_response_shape,
)


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


def test_mock_adapter_evidence_binding_report_is_deterministic():
    first = day85.build_mock_adapter_evidence_binding_report()
    second = day85.build_mock_adapter_evidence_binding_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == "Day85"
    assert first["title"] == "Day85 Mock Adapter + Evidence Binding"
    assert first["overall_status"] == "PASS"
    assert first["review_status"] == "REVIEW_READY"
    assert first["final_recommendation"] == "REVIEW_ONLY"


def test_mock_adapter_request_and_responses_conform_to_day84_contract():
    report = day85.build_mock_adapter_evidence_binding_report()

    for record in report["adapter_records"]:
        request = day85.build_mock_adapter_request(record["request_id"])
        response = record["mock_response"]

        assert validate_adapter_request_shape(request) == []
        assert validate_adapter_response_shape(response) == []
        assert response["request_id"] == record["request_id"]
        assert response["contract_version"] == record["contract_id"]
        assert response["execution_result"] is None
        assert response["commands_executed"] == []
        assert response["device_session"] is None


def test_every_mock_response_is_bound_to_request_contract_adapter_and_evidence():
    report = day85.build_mock_adapter_evidence_binding_report()

    assert report["traceability_summary"]["all_responses_bound_to_request"] is True
    assert report["traceability_summary"]["all_responses_bound_to_day84_contract"] is True
    assert report["traceability_summary"]["all_responses_bound_to_evidence"] is True
    assert report["validation_errors"] == []

    for record in report["adapter_records"]:
        traceability = record["traceability"]
        assert traceability["original_request"] == record["request_id"]
        assert traceability["day84_contract"] == record["contract_id"]
        assert traceability["adapter_fixture"] == day85.ADAPTER_FIXTURE_ID
        assert traceability["adapter_id"] == record["adapter_id"]
        assert traceability["evidence_reference"] == record["evidence_reference"]
        assert record["evidence_reference"] in record["mock_response"]["evidence_refs"]
        assert record["contract_reference"] in record["mock_response"]["evidence_refs"]


def test_compatibility_matrix_is_internal_validation_not_standalone_topic():
    report = day85.build_mock_adapter_evidence_binding_report()
    matrix = {row["adapter_type"]: row for row in report["compatibility_matrix"]}

    assert report["safety_invariants"]["compatibility_matrix_is_internal_validation"] is True
    assert report["safety_invariants"]["compatibility_matrix_is_standalone_topic"] is False
    for row in matrix.values():
        assert row["validation_scope"] == "internal_day85_day86_validation"
        assert row["standalone_topic"] is False

    assert matrix["mock adapter"]["expected_result"] == "compatible"
    assert matrix["replay adapter"]["expected_result"] == "compatible"
    assert matrix["evidence-only adapter"]["expected_result"] == "compatible"
    assert matrix["ssh adapter"]["expected_result"] == "blocked"
    assert matrix["live command adapter"]["expected_result"] == "blocked"
    assert matrix["AI executor adapter"]["expected_result"] == "blocked"
    assert matrix["approval unlock adapter"]["expected_result"] == "blocked"


def test_compatible_adapters_are_non_executing():
    records = {
        record["adapter_type"]: record
        for record in day85.build_mock_adapter_evidence_binding_report()["adapter_records"]
    }

    for adapter_type in ("mock adapter", "replay adapter", "evidence-only adapter"):
        record = records[adapter_type]
        assert record["compatible_with_day84_contract"] is True
        assert record["decision"] == "COMPATIBLE_REVIEW_ONLY"
        assert record["allowed_to_execute"] is False
        assert record["ssh_allowed"] is False
        assert record["device_access_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["approval_unlock_supported"] is False
        assert record["execution_unlock_supported"] is False


def test_unsafe_adapters_are_blocked_with_evidence_trails():
    report = day85.build_mock_adapter_evidence_binding_report()
    blocked = {
        check["adapter_type"]: check
        for check in report["blocked_adapter_checks"]
    }

    for adapter_type in (
        "ssh adapter",
        "live command adapter",
        "AI executor adapter",
        "approval unlock adapter",
    ):
        check = blocked[adapter_type]
        assert check["allowed_to_execute"] is False
        assert check["ssh_allowed"] is False
        assert check["live_command_allowed"] is False
        assert check["approval_unlock_supported"] is False
        assert check["execution_unlock_supported"] is False
        assert check["reviewer_decision"] in {"BLOCKED", "REJECTED"}
        assert check["evidence_trail_generated"] is True


def test_no_adapter_enables_execution_ssh_device_or_live_command():
    report = day85.build_mock_adapter_evidence_binding_report()

    for record in report["adapter_records"]:
        assert record["allowed_to_execute"] is False
        assert record["ssh_allowed"] is False
        assert record["device_access_allowed"] is False
        assert record["live_command_allowed"] is False
        assert record["approval_unlock_supported"] is False
        assert record["execution_unlock_supported"] is False
        flags = record["mock_response"]["safety_flags"]
        assert flags["allowed_to_execute"] is False
        assert flags["ssh_allowed"] is False
        assert flags["device_access_allowed"] is False
        assert flags["live_command_allowed"] is False
        assert flags["approval_unlock_supported"] is False
        assert flags["execution_unlock_supported"] is False
        assert flags["ai_api_allowed"] is False


def test_mock_adapter_evidence_binding_reports_are_written(tmp_path):
    report = day85.build_mock_adapter_evidence_binding_report()
    json_path, html_path = day85.write_mock_adapter_evidence_binding_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day85_mock_adapter_evidence_binding.json"
    assert html_path == tmp_path / "reports/lab-summary/day85_mock_adapter_evidence_binding.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day85 Mock Adapter + Evidence Binding" in html
    assert "Compatibility Matrix Internal Validation" in html
    assert "not a standalone Day85 topic" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_mock_adapter_evidence_binding_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(day85.__file__)
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
