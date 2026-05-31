import json
import sys
from pathlib import Path

import pytest

from dashboard_command_runner import (
    CommandSpec,
    CommandUnavailableError,
    build_command_registry,
    execute_command,
    execute_registered_command,
    get_command_or_raise,
    list_execution_logs,
    load_execution_log,
)


def test_command_registry_contains_only_allowlisted_commands(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_performance_regression.py").write_text(
        "def test_placeholder(): pass",
        encoding="utf-8",
    )
    (tmp_path / "performance_regression.py").write_text("", encoding="utf-8")
    (tmp_path / "topology_summary.py").write_text("", encoding="utf-8")

    registry = build_command_registry(tmp_path, python_executable="python")

    assert set(registry) == {
        "pytest_all",
        "pytest_tests_dir",
        "pytest_performance_regression",
        "performance_regression",
        "topology_summary",
    }
    assert all(command.argv[0] == "python" for command in registry.values())


def test_command_registry_marks_missing_commands_unavailable(tmp_path):
    registry = build_command_registry(tmp_path, python_executable="python")

    assert registry["performance_regression"].available is False
    assert registry["performance_regression"].enabled is False
    assert "Missing performance_regression.py" == registry["performance_regression"].unavailable_reason


def test_day9_lab_regression_script_is_listed_but_disabled(tmp_path):
    (tmp_path / "performance_regression.py").write_text("", encoding="utf-8")

    registry = build_command_registry(tmp_path, python_executable="python")

    assert registry["performance_regression"].available is True
    assert registry["performance_regression"].enabled is False
    assert registry["performance_regression"].category == "Manual lab workflow"
    assert "Day9 performance reports" in registry["performance_regression"].effect
    assert "needs lab parameters" in registry["performance_regression"].unavailable_reason


def test_topology_summary_command_describes_report_effect(tmp_path):
    (tmp_path / "topology_summary.py").write_text("", encoding="utf-8")

    registry = build_command_registry(tmp_path, python_executable="python")

    assert registry["topology_summary"].label == "Rebuild Day6 topology summary"
    assert "reports/day6_lab_topology_summary.json" in registry["topology_summary"].effect
    assert "Does not rerun Day8 or Day9" in registry["topology_summary"].effect


def test_unknown_command_id_is_rejected(tmp_path):
    registry = build_command_registry(tmp_path, python_executable="python")

    with pytest.raises(KeyError):
        get_command_or_raise(registry, "not_allowed")


def test_unavailable_command_id_is_rejected(tmp_path):
    registry = build_command_registry(tmp_path, python_executable="python")

    with pytest.raises(CommandUnavailableError):
        get_command_or_raise(registry, "topology_summary")


def test_command_execution_creates_json_log(tmp_path):
    command = CommandSpec(
        command_id="unit_success",
        label="Unit success",
        description="A lightweight success command.",
        category="Test / validation",
        effect="Test effect.",
        argv=[sys.executable, "-c", "print('hello')"],
        working_directory=str(tmp_path),
        timeout_seconds=30,
        enabled=True,
        available=True,
    )

    log = execute_command(command, tmp_path / "logs")

    log_path = tmp_path / "logs" / f"{log['log_id']}.json"
    saved = json.loads(log_path.read_text(encoding="utf-8"))
    assert saved["status"] == "PASS"
    assert saved["exit_code"] == 0
    assert "hello" in saved["stdout"]
    assert "Z" not in saved["started_at"]
    assert "T" not in saved["started_at"]


def test_failed_command_is_logged_as_fail(tmp_path):
    command = CommandSpec(
        command_id="unit_fail",
        label="Unit fail",
        description="A lightweight failing command.",
        category="Test / validation",
        effect="Test effect.",
        argv=[sys.executable, "-c", "import sys; sys.exit(2)"],
        working_directory=str(tmp_path),
        timeout_seconds=30,
        enabled=True,
        available=True,
    )

    log = execute_command(command, tmp_path / "logs")

    assert log["status"] == "FAIL"
    assert log["exit_code"] == 2


def test_timeout_command_is_logged_as_timeout(tmp_path):
    command = CommandSpec(
        command_id="unit_timeout",
        label="Unit timeout",
        description="A lightweight timeout command.",
        category="Test / validation",
        effect="Test effect.",
        argv=[sys.executable, "-c", "import time; time.sleep(1)"],
        working_directory=str(tmp_path),
        timeout_seconds=0.01,
        enabled=True,
        available=True,
    )

    log = execute_command(command, tmp_path / "logs")

    assert log["status"] == "TIMEOUT"


def test_execute_registered_command_writes_log_for_allowed_command(tmp_path):
    command = CommandSpec(
        command_id="unit_success",
        label="Unit success",
        description="A lightweight success command.",
        category="Test / validation",
        effect="Test effect.",
        argv=[sys.executable, "-c", "print('ok')"],
        working_directory=str(tmp_path),
        timeout_seconds=30,
        enabled=True,
        available=True,
    )

    log = execute_registered_command(
        {"unit_success": command},
        "unit_success",
        tmp_path / "logs",
    )

    assert load_execution_log(tmp_path / "logs", log["log_id"])["status"] == "PASS"
    assert list_execution_logs(tmp_path / "logs")[0]["log_id"] == log["log_id"]


def test_load_execution_log_rejects_unsafe_id(tmp_path):
    assert load_execution_log(tmp_path, "../secret") is None
