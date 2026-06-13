import ast
import json
from pathlib import Path

import intent_safety_boundary_regression_matrix as day123
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


def test_day123_matrix_is_deterministic_and_passes_catalog_boundaries():
    first = day123.build_safety_boundary_regression_matrix_report(network_lab.list_tasks())
    second = day123.build_safety_boundary_regression_matrix_report(network_lab.list_tasks())

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 123
    assert first["task"] == "safety-boundary-regression-matrix"
    assert first["overall_status"] == "PASS"
    assert first["mode"] == "REPORT_ONLY_SAFETY_BOUNDARY_REGRESSION"
    assert first["summary"]["total_rows"] >= 24
    assert first["summary"]["failed_rows"] == 0
    assert first["summary"]["missing_catalog_rows"] == 0
    assert first["final_recommendation"] == "KEEP_BOUNDARIES_LOCKED"
    assert day123.validate_safety_boundary_regression_matrix_report(first) == []


def test_day123_all_reviewed_boundaries_remain_non_executing():
    report = day123.build_safety_boundary_regression_matrix_report(network_lab.list_tasks())

    for row in report["matrix_rows"]:
        assert row["status"] == "PASS"
        assert row["execution_allowed"] is False
        assert row["ssh_allowed"] is False
        assert row["live_command_allowed"] is False
        assert row["mutation_allowed"] is False
        assert row["unlock_supported"] is False
        assert row["adapter_invocation_allowed"] is False
        assert row["broker_invocation_allowed"] is False
        assert row["runner_invocation_allowed"] is False
        assert row["openai_api_allowed"] is False
        assert row["voice_runtime_allowed"] is False
        assert row["dashboard_post_action_allowed"] is False

    for count_name, count in report["summary"].items():
        if count_name.endswith("_allowed_count") or count_name.endswith("_supported_count"):
            assert count == 0


def test_day123_blocks_missing_catalog_entry():
    report = day123.build_safety_boundary_regression_matrix_report([])

    assert report["overall_status"] == "BLOCKED"
    assert report["summary"]["failed_rows"] > 0
    assert report["summary"]["missing_catalog_rows"] > 0
    assert report["validation_errors"]


def test_day123_reports_are_written_without_action_controls(tmp_path):
    report = day123.build_safety_boundary_regression_matrix_report(network_lab.list_tasks())
    json_path, html_path = day123.write_safety_boundary_regression_matrix_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day123_safety_boundary_regression_matrix.json"
    assert html_path == tmp_path / "reports/lab-summary/day123_safety_boundary_regression_matrix.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Safety Boundary Regression Matrix" in html
    assert "No SSH, live command execution, mutation" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()
    assert "<script" not in html.lower()


def test_day123_module_has_no_forbidden_runtime_imports_or_live_io():
    source = Path(day123.__file__).read_text(encoding="utf-8")
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


def test_day123_runner_task_is_registered_and_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "safety-boundary-regression-matrix")

    assert task["task_id"] == "day123_safety_boundary_regression_matrix"
    assert task["day"] == "Day123"
    assert task["display_name"] == "Day123 Safety Boundary Regression Matrix"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day123_safety_boundary_regression_matrix.json" in task["report_paths"]
    assert "reports/lab-summary/day123_safety_boundary_regression_matrix.html" in task["report_paths"]
    assert "docs/ai-intent/day123_safety_boundary_regression_matrix.md" in task["report_paths"]
    assert "docs/roadmap/day123_safety_boundary_regression_matrix.md" in task["report_paths"]
    assert "execution_allowed=false" in task["notes"]
    assert "dashboard_post_action_allowed=false" in task["notes"]


def test_day123_runner_writes_reports_without_live_runner_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day123 safety boundary matrix must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day123 safety boundary matrix must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "safety-boundary-regression-matrix"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day123_safety_boundary_regression_matrix.json"
    html_path = tmp_path / "reports/lab-summary/day123_safety_boundary_regression_matrix.html"
    assert exit_code == 0
    assert "Day123 Safety Boundary Regression Matrix" in output
    assert "Task name: safety-boundary-regression-matrix" in output
    assert "overall_status: PASS" in output
    assert "failed_rows: 0" in output
    assert "missing_catalog_rows: 0" in output
    assert "execution_allowed_count: 0" in output
    assert "ssh_allowed_count: 0" in output
    assert "live_command_allowed_count: 0" in output
    assert "mutation_allowed_count: 0" in output
    assert "unlock_supported_count: 0" in output
    assert "openai_api_allowed_count: 0" in output
    assert "voice_runtime_allowed_count: 0" in output
    assert "dashboard_post_action_allowed_count: 0" in output
    assert "JSON report: reports/lab-summary/day123_safety_boundary_regression_matrix.json" in output
    assert "HTML report: reports/lab-summary/day123_safety_boundary_regression_matrix.html" in output
    assert "[PASS] SAFETY_BOUNDARY_REGRESSION_MATRIX_READY" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()


def test_day123_report_index_visibility_includes_safety_boundary_regression_matrix(tmp_path):
    assert network_lab.main(["--task", "safety-boundary-regression-matrix"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Safety Boundary Regression Matrix" in html
    assert "REPORT_ONLY_SAFETY_BOUNDARY_REGRESSION" in html
    assert "reports/lab-summary/day123_safety_boundary_regression_matrix.json" in html
    assert "reports/lab-summary/day123_safety_boundary_regression_matrix.html" in html
