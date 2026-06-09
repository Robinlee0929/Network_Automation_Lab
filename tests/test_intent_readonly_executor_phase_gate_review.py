import ast
from copy import deepcopy
import json
from pathlib import Path

import intent_readonly_executor_phase_gate_review as day87


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


def test_phase_gate_review_report_is_deterministic():
    first = day87.build_readonly_executor_phase_gate_review()
    second = day87.build_readonly_executor_phase_gate_review()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["created_at"] == day87.CREATED_AT
    assert first["phase_name"] == day87.PHASE_NAME
    assert first["phase_gate_status"] == "PASS"
    assert first["phase_gate_recommendation"] == "DESIGN_ONLY"
    assert first["allowed_next_step"] == "Real Read-only Executor Adapter Design Draft"


def test_phase_gate_review_preserves_required_safety_invariants():
    report = day87.build_readonly_executor_phase_gate_review()

    assert day87.validate_readonly_executor_phase_gate_review(report) == []
    for field in day87.REQUIRED_FALSE_FLAGS:
        assert report[field] is False
        assert report["safety_invariants"][field] is False

    assert report["real_adapter_design_allowed"] is True
    assert report["safety_invariants"]["real_adapter_design_allowed"] is True
    assert report["real_adapter_implementation_allowed"] is False
    assert report["execution_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["live_command_allowed"] is False
    assert report["write_command_allowed"] is False
    assert report["device_connection_allowed"] is False
    assert report["safety_invariants"]["openai_api_allowed"] is False
    assert report["safety_invariants"]["voice_allowed"] is False


def test_phase_gate_review_contains_all_required_gate_checks():
    report = day87.build_readonly_executor_phase_gate_review()

    assert report["reviewed_days"] == ["Day83", "Day84", "Day85", "Day86"]
    assert {check["check_id"] for check in report["gate_checks"]} == set(day87.REQUIRED_GATE_CHECKS)
    assert {check["status"] for check in report["gate_checks"]} == {"PASS"}
    assert all(check["required"] is True for check in report["gate_checks"])

    chain_text = json.dumps(report["evidence_chain"], sort_keys=True)
    for day in ("Day83", "Day84", "Day85", "Day86"):
        assert day in chain_text


def test_failed_required_gate_check_blocks_or_requires_review():
    day83 = day87.build_readonly_executor_readiness_gate_report()
    day83["overall_status"] = "FAIL"

    report = day87.build_readonly_executor_phase_gate_review(day83_report=day83)

    assert report["phase_gate_status"] in {"BLOCKED", "REVIEW_REQUIRED"}
    assert report["phase_gate_status"] != "PASS"
    assert report["phase_gate_recommendation"] == "DO_NOT_PROCEED"
    assert report["allowed_next_step"] is None
    failing = [
        check for check in report["gate_checks"] if check["check_id"] == "day83-readiness-gate-review-only"
    ]
    assert failing[0]["status"] == "FAIL"


def test_execution_unlock_or_ssh_regression_blocks_phase_gate():
    day86 = day87.build_controlled_runner_harness_report()
    day86["safety_invariants"]["ssh_allowed"] = True

    report = day87.build_readonly_executor_phase_gate_review(day86_report=day86)

    assert report["phase_gate_status"] == "BLOCKED"
    assert report["phase_gate_recommendation"] == "DO_NOT_PROCEED"
    assert any(
        check["check_id"] == "no-ssh-path-enabled" and check["status"] == "FAIL"
        for check in report["gate_checks"]
    )


def test_phase_gate_status_cannot_be_pass_when_required_check_failed():
    report = day87.build_readonly_executor_phase_gate_review()
    tampered = deepcopy(report)
    tampered["gate_checks"][0]["status"] = "FAIL"

    errors = day87.validate_readonly_executor_phase_gate_review(tampered)

    assert any("phase_gate_status cannot be PASS" in error for error in errors)


def test_phase_gate_review_reports_are_written_without_action_controls(tmp_path):
    report = day87.build_readonly_executor_phase_gate_review()
    json_path, html_path = day87.write_readonly_executor_phase_gate_review_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day87_readonly_executor_phase_gate_review.json"
    assert html_path == tmp_path / "reports/lab-summary/day87_readonly_executor_phase_gate_review.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Day87 Read-only Executor Phase Gate Review" in html
    assert "PASS / DESIGN_ONLY" in html
    assert "Day83" in html
    assert "Day84" in html
    assert "Day85" in html
    assert "Day86" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_phase_gate_review_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(day87.__file__)
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
