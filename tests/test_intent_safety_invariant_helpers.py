import ast
import json
from pathlib import Path

import intent_safety_invariant_helpers as day124
import network_lab


FORBIDDEN_IMPORTS = {
    "asyncssh",
    "netmiko",
    "openai",
    "paramiko",
    "requests",
    "routeros_api",
    "socket",
    "subprocess",
    "telnetlib",
}


def test_day124_default_safety_invariants_are_deterministic_and_false():
    first = day124.build_default_safety_invariants()
    second = day124.build_default_safety_invariants()

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    for flag in day124.DANGEROUS_CAPABILITY_FLAGS:
        assert flag in first
        assert first[flag] is False


def test_day124_helper_review_has_required_acceptance_fields():
    report = day124.build_safety_invariant_helper_review()

    assert report["day"] == "Day124"
    assert report["task"] == "safety-invariant-helper-review"
    assert report["overall_status"] == "PASS"
    assert report["mode"] == "REVIEW_ONLY"
    assert report["reviewer_status"] == "SAFETY_INVARIANT_HELPER_CONSOLIDATED"
    assert report["execution_allowed"] is False
    assert report["final_recommendation"] == "KEEP_REVIEW_ONLY_SAFETY_INVARIANTS"
    assert report["dangerous_flag_summary"]["unsafe_true_flags"] == 0
    assert report["dangerous_flag_summary"]["unblocked_capabilities"] == 0
    assert report["validation_errors"] == []
    for value in report["safety_invariants"].values():
        assert value is False


def test_day124_blocked_capabilities_remain_blocked():
    blocked = day124.build_blocked_execution_capabilities()
    report = day124.build_safety_invariant_helper_review()

    assert blocked == report["blocked_capabilities"]
    assert blocked
    for value in blocked.values():
        assert value is False
    assert day124.assert_review_only_safety_invariants(
        safety_invariants=report["safety_invariants"],
        blocked_capabilities=blocked,
        execution_allowed=report["execution_allowed"],
        final_recommendation=report["final_recommendation"],
    ) == []


def test_day124_validator_blocks_any_unsafe_flag():
    invariants = day124.build_default_safety_invariants()
    invariants["ssh_allowed"] = True

    errors = day124.assert_review_only_safety_invariants(safety_invariants=invariants)

    assert "safety_invariants.ssh_allowed must be false." in errors


def test_day124_reports_are_written_without_action_controls(tmp_path):
    report = day124.build_safety_invariant_helper_review()
    json_path, html_path = day124.write_safety_invariant_helper_review_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day124_safety_invariant_helper_review.json"
    assert html_path == tmp_path / "reports/lab-summary/day124_safety_invariant_helper_review.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Safety Invariant Helper Consolidation" in html
    assert "Helper consolidation completed" in html
    assert "All execution-related flags remain false" in html
    assert "no runtime or provider capability was enabled" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<script" not in html.lower()


def test_day124_module_has_no_forbidden_runtime_imports_or_live_io():
    source = Path(day124.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
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


def test_day124_runner_task_is_registered_and_review_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "safety-invariant-helper-review")

    assert task["task_id"] == "day124_safety_invariant_helper_review"
    assert task["day"] == "Day124"
    assert task["display_name"] == "Day124 Safety Invariant Helper Consolidation"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day124_safety_invariant_helper_review.json" in task["report_paths"]
    assert "reports/lab-summary/day124_safety_invariant_helper_review.html" in task["report_paths"]
    assert "docs/ai-intent/day124_safety_invariant_helper_consolidation.md" in task["report_paths"]
    assert "docs/roadmap/day124_safety_invariant_helper_consolidation.md" in task["report_paths"]
    assert "execution_allowed=false" in task["notes"]
    assert "openai_api_allowed=false" in task["notes"]
    assert "configuration_change_allowed=false" in task["notes"]


def test_day124_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day124 safety invariant helper review must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day124 safety invariant helper review must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "safety-invariant-helper-review"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day124_safety_invariant_helper_review.json"
    html_path = tmp_path / "reports/lab-summary/day124_safety_invariant_helper_review.html"
    assert exit_code == 0
    assert "Day124 Safety Invariant Helper Consolidation" in output
    assert "Task name: safety-invariant-helper-review" in output
    assert "overall_status: PASS" in output
    assert "mode: REVIEW_ONLY" in output
    assert "execution_allowed: false" in output
    assert "final_recommendation: KEEP_REVIEW_ONLY_SAFETY_INVARIANTS" in output
    assert "unsafe_true_flags: 0" in output
    assert "unblocked_capabilities: 0" in output
    assert "openai_api_allowed: false" in output
    assert "voice_input_allowed: false" in output
    assert "ssh_allowed: false" in output
    assert "live_device_allowed: false" in output
    assert "live_command_allowed: false" in output
    assert "runtime_unlock_supported: false" in output
    assert "dashboard_post_allowed: false" in output
    assert "broker_execution_allowed: false" in output
    assert "mapped_task_execution_allowed: false" in output
    assert "write_operation_allowed: false" in output
    assert "configuration_change_allowed: false" in output
    assert "JSON report: reports/lab-summary/day124_safety_invariant_helper_review.json" in output
    assert "HTML report: reports/lab-summary/day124_safety_invariant_helper_review.html" in output
    assert "[PASS] SAFETY_INVARIANT_HELPER_CONSOLIDATED" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()


def test_day124_report_index_visibility_includes_helper_review(tmp_path):
    assert network_lab.main(["--task", "safety-invariant-helper-review"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Safety Invariant Helper Consolidation" in html
    assert "REVIEW_ONLY" in html
    assert "reports/lab-summary/day124_safety_invariant_helper_review.json" in html
    assert "reports/lab-summary/day124_safety_invariant_helper_review.html" in html
