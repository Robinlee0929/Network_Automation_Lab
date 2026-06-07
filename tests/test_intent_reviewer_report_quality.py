import ast
from copy import deepcopy
from pathlib import Path

import intent_reviewer_report_quality as quality


UNSAFE_IMPORTS = {
    "netmiko",
    "openai",
    "paramiko",
    "requests",
    "socket",
    "speech",
    "subprocess",
}


def test_day68_reviewer_quality_report_is_deterministic_and_review_ready():
    first = quality.build_reviewer_quality_report()
    second = quality.build_reviewer_quality_report()

    assert first == second
    assert first["day"] == "Day68"
    assert first["runtime_mode"] == "offline_mock_report_only"
    assert first["review_status"] == "REVIEW_READY"
    assert first["overall_status"] == "PASS"
    assert first["scenario_count"] >= 4
    assert first["quality_gate_summary"]["all_scenarios_review_ready"] is True


def test_day68_reviews_reviewer_visible_fields_for_all_scenarios():
    report = quality.build_reviewer_quality_report()

    for scenario in report["scenario_reviews"]:
        assert scenario["input_intent_present"] is True
        assert scenario["decision_result_present"] is True
        assert scenario["safety_classification_present"] is True
        assert scenario["blocked_reason_present_when_applicable"] is True
        assert scenario["evidence_reference_present"] is True
        assert scenario["contract_validation_result_present"] is True
        assert scenario["contract_validation_status"] == "PASS"
        assert scenario["missing_evidence"] == []
        assert scenario["reviewer_verdict"] == "REVIEW_READY"


def test_day68_report_includes_no_execution_and_contract_evidence():
    report = quality.build_reviewer_quality_report()
    evidence = report["non_execution_evidence"]
    contract = report["contract_validation_evidence"]

    assert evidence["no_live_action_executed"] is True
    assert evidence["live_execution_allowed_false"] is True
    assert evidence["no_mapped_task_executed"] is True
    assert evidence["no_device_access_occurred"] is True
    assert evidence["no_device_network_configuration_changed"] is True
    assert evidence["no_openai_api_used"] is True
    assert evidence["no_voice_integration_used"] is True
    assert evidence["no_ssh_used"] is True
    assert evidence["no_config_json_dependency"] is True
    assert contract["validation_performed"] is True
    assert contract["contract_status"] == "PASS"
    assert contract["validation_errors"] == []


def test_day68_marks_missing_evidence_as_needs_review():
    source = quality.build_reviewer_quality_report()
    runtime_report = {
        "title": "Broken mock report",
        "live_execution_allowed": False,
        "mapped_task_executed": False,
        "no_live_execution_occurred": True,
        "no_device_access_occurred": True,
        "no_network_change_occurred": True,
        "openai_api_used": False,
        "voice_integration_used": False,
        "ssh_used": False,
        "config_json_read": False,
        "mock_scenarios": [
            {
                "scenario_id": source["scenario_reviews"][0]["scenario_id"],
                "scenario_name": "Incomplete scenario",
                "input_text": "",
                "decision": "",
                "safety_category": "blocked_live_action",
                "reviewer_warning": "",
                "evidence_references": [],
                "execution_mode": "offline_mock",
                "live_execution_allowed": False,
                "mapped_task_executed": False,
                "blocked": True,
                "intent_category": "broken",
                "mock_execution_record": {
                    "real_command_executed": False,
                    "mapped_task_executed": False,
                    "device_access_used": False,
                    "device_connection_used": False,
                    "network_change_made": False,
                    "device_configuration_changed": False,
                },
            }
        ],
    }

    report = quality.build_reviewer_quality_report(deepcopy(runtime_report))

    assert report["review_status"] == "NEEDS_REVIEW"
    assert report["scenario_reviews"][0]["reviewer_verdict"] == "NEEDS_REVIEW"
    assert "input intent" in report["scenario_reviews"][0]["missing_evidence"]
    assert "evidence reference" in report["scenario_reviews"][0]["missing_evidence"]


def test_day68_quality_module_has_no_unsafe_imports_or_runtime_dependency():
    source_path = Path(quality.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(UNSAFE_IMPORTS)
    assert ".read_text(" not in source
    assert "open(" not in source
    assert "network_lab" not in source
