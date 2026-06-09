import ast
import json
from pathlib import Path

import intent_controlled_runner_harness as day86


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


def test_controlled_runner_harness_report_is_deterministic():
    first = day86.build_controlled_runner_harness_report()
    second = day86.build_controlled_runner_harness_report()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["phase"] == "Day86"
    assert first["overall_status"] == "PASS"
    assert first["runner_mode"] == "CONTROLLED_HARNESS"
    assert first["final_recommendation"] == "REVIEW_ONLY"


def test_all_scenarios_preserve_runner_safety_invariants():
    report = day86.build_controlled_runner_harness_report()

    assert report["summary"]["total_scenarios"] >= 6
    assert report["summary"]["failed_scenarios"] == 0
    assert report["summary"]["safety_lock_summary"]["all_safety_invariants_locked"] is True
    assert report["summary"]["safety_lock_summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["live_command_allowed_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["mapped_task_executed_values"] == [False]

    for scenario in report["scenarios"]:
        assert scenario["dry_run_only"] is True
        assert scenario["allowed_to_execute"] is False
        assert scenario["ssh_allowed"] is False
        assert scenario["live_command_allowed"] is False
        assert scenario["mapped_task_executed"] is False
        assert scenario["safety_regression_status"] == "PASS"
        assert scenario["evidence_refs"]


def test_compatible_adapter_does_not_imply_execution_permission():
    report = day86.build_controlled_runner_harness_report()
    compatible = [
        scenario
        for scenario in report["scenarios"]
        if scenario["compatibility_status"] == "compatible"
        and scenario["blocked_adapter"] is False
        and scenario["evidence_bound"] is True
    ]

    assert compatible
    for scenario in compatible:
        assert scenario["allowed_to_execute"] is False
        assert scenario["mapped_task_executed"] is False
        if scenario["requested_execution_flags"]:
            assert scenario["runner_decision"] == "UNSAFE_FLAG_REGRESSION_BLOCKED"
        else:
            assert scenario["runner_decision"] == "REPORT_REVIEW_ONLY"


def test_blocked_adapter_remains_blocked_at_runner_level():
    report = day86.build_controlled_runner_harness_report()
    blocked = next(
        scenario
        for scenario in report["scenarios"]
        if scenario["scenario_id"] == "day86-blocked-adapter-attempt"
    )

    assert blocked["requested_adapter"] == "ssh adapter"
    assert blocked["blocked_adapter"] is True
    assert blocked["runner_decision"] == "BLOCKED_ADAPTER_REVIEW_ONLY"
    assert blocked["allowed_to_execute"] is False
    assert blocked["ssh_allowed"] is False
    assert blocked["mapped_task_executed"] is False


def test_missing_evidence_cannot_become_executable():
    report = day86.build_controlled_runner_harness_report()
    missing = next(
        scenario
        for scenario in report["scenarios"]
        if scenario["scenario_id"] == "day86-incomplete-evidence-binding"
    )

    assert missing["evidence_bound"] is False
    assert missing["runner_decision"] == "MISSING_EVIDENCE_REVIEW_ONLY"
    assert missing["allowed_to_execute"] is False
    assert missing["mapped_task_executed"] is False
    assert missing["evidence_refs"]


def test_report_output_can_be_generated_without_enabling_execution(tmp_path):
    report = day86.build_controlled_runner_harness_report()
    json_path, html_path = day86.write_controlled_runner_harness_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day86_controlled_runner_harness.json"
    assert html_path == tmp_path / "reports/lab-summary/day86_controlled_runner_harness.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert data["final_recommendation"] == "REVIEW_ONLY"
    assert data["execution_unlock_supported"] is False
    assert data["summary"]["safety_lock_summary"]["report_output_without_execution"] is True
    assert "Day86 Controlled Runner Harness + Safety Regression" in html
    assert "Mapped task executed values" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_unsafe_execution_flag_regression_attempt_stays_locked():
    report = day86.build_controlled_runner_harness_report()
    regression = next(
        scenario
        for scenario in report["scenarios"]
        if scenario["scenario_id"] == "day86-unsafe-execution-flag-regression-attempt"
    )

    assert regression["requested_execution_flags"]["allowed_to_execute"] is True
    assert regression["requested_execution_flags"]["ssh_allowed"] is True
    assert regression["requested_execution_flags"]["live_command_allowed"] is True
    assert regression["requested_execution_flags"]["mapped_task_execution_allowed"] is True
    assert regression["runner_decision"] == "UNSAFE_FLAG_REGRESSION_BLOCKED"
    assert regression["allowed_to_execute"] is False
    assert regression["ssh_allowed"] is False
    assert regression["live_command_allowed"] is False
    assert regression["mapped_task_executed"] is False


def test_controlled_runner_harness_module_does_not_import_unsafe_runtime_surfaces():
    source_path = Path(day86.__file__)
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
