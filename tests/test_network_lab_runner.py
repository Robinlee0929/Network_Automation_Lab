import json
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

import network_lab


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def profile(required=True, output_json="reports/lab-summary/latest_lab_overview.json"):
    return {
        "lab_name": "Test Lab",
        "overview_output": {
            "json": output_json,
            "html": "reports/lab-summary/latest_lab_overview.html",
        },
        "devices": [
            {
                "name": "router1",
                "type": "mikrotik",
                "required": True,
                "reports": [
                    {
                        "name": "Required Report" if required else "Optional Report",
                        "json": "reports/router1/report.json",
                        "html": "reports/router1/report.html",
                        "required": required,
                    }
                ],
            }
        ],
        "lab_summary_reports": [
            {
                "name": "Lab Summary",
                "json": "reports/lab-summary/summary.json",
                "html": "reports/lab-summary/summary.html",
                "required": False,
            }
        ],
    }


def write_default_profile(tmp_path: Path, data=None) -> Path:
    profile_path = tmp_path / "topology_profiles" / "day14_lab_runner_profile.json"
    write_json(profile_path, data or profile(required=False))
    return profile_path


def test_load_lab_runner_profile_loads_valid_profile():
    loaded = network_lab.load_lab_runner_profile(
        Path("topology_profiles/day14_lab_runner_profile.json")
    )

    assert loaded["lab_name"] == "Network Automation Lab"
    assert loaded["overview_output"]["json"] == "reports/lab-summary/latest_lab_overview.json"


def test_iter_report_items_returns_device_reports_and_lab_summary_reports():
    items = list(network_lab.iter_report_items(profile()))

    assert [item[0] for item in items] == ["device", "lab_summary"]
    assert items[0][1]["name"] == "router1"
    assert items[1][2]["name"] == "Lab Summary"


def test_missing_required_report_makes_overall_incomplete(tmp_path):
    overview = network_lab.build_latest_lab_overview(profile(required=True), tmp_path)

    assert overview["overall_result"] == "INCOMPLETE"
    assert overview["devices"][0]["reports"][0]["status"] == "MISSING"


def test_missing_optional_report_makes_overall_warn(tmp_path):
    write_json(tmp_path / "reports/lab-summary/summary.json", {"overall_result": "PASS"})

    overview = network_lab.build_latest_lab_overview(profile(required=False), tmp_path)

    assert overview["overall_result"] == "WARN"


def test_existing_pass_json_becomes_pass(tmp_path):
    item = {"name": "Report", "json": "reports/report.json", "html": "reports/report.html"}
    write_json(tmp_path / "reports/report.json", {"overall_result": "PASS"})

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "PASS"


def test_existing_fail_json_becomes_fail(tmp_path):
    item = {"name": "Report", "json": "reports/report.json", "html": "reports/report.html"}
    write_json(tmp_path / "reports/report.json", {"passed": False})

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "FAIL"


def test_day2_validation_result_becomes_pass(tmp_path):
    item = {"name": "Day2 Auto Setup", "json": "reports/day2.json", "html": "reports/day2.html"}
    write_json(tmp_path / "reports/day2.json", {"validation_result": "PASS"})

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "PASS"


def test_day2_validation_warning_becomes_warn(tmp_path):
    item = {"name": "Day2 Auto Setup", "json": "reports/day2.json", "html": "reports/day2.html"}
    write_json(tmp_path / "reports/day2.json", {"validation_result": "WARNING"})

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "WARN"


def test_unknown_schema_becomes_unknown(tmp_path):
    item = {"name": "Report", "json": "reports/report.json", "html": "reports/report.html"}
    write_json(tmp_path / "reports/report.json", {"device": "router1"})

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "UNKNOWN"
    assert "Could not infer" in record["message"]


def test_invalid_json_becomes_unknown_with_message(tmp_path):
    item = {"name": "Report", "json": "reports/report.json", "html": "reports/report.html"}
    path = tmp_path / "reports/report.json"
    path.parent.mkdir(parents=True)
    path.write_text("{bad", encoding="utf-8")

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == "UNKNOWN"
    assert "Invalid JSON" in record["message"]


def test_latest_overview_json_is_generated(tmp_path):
    data = network_lab.build_latest_lab_overview(profile(), tmp_path)
    output = tmp_path / "reports/lab-summary/latest_lab_overview.json"

    network_lab.write_json_report(data, output)

    assert json.loads(output.read_text(encoding="utf-8"))["day"] == "Day14"


def test_latest_overview_html_is_generated(tmp_path):
    data = network_lab.build_latest_lab_overview(profile(), tmp_path)
    output = tmp_path / "reports/lab-summary/latest_lab_overview.html"

    network_lab.write_html_overview(data, output, tmp_path)

    assert "Latest Lab Overview" in output.read_text(encoding="utf-8")


def test_dry_run_does_not_create_output_files(tmp_path, capsys):
    profile_path = tmp_path / "profile.json"
    write_json(profile_path, profile())

    exit_code = network_lab.main(
        ["--task", "report-index", "--profile", str(profile_path), "--dry-run"],
        project_root=tmp_path,
    )

    assert exit_code == 0
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()
    assert "No reports were written" in capsys.readouterr().out


def test_html_includes_links_to_existing_html_reports(tmp_path):
    prof = profile(required=False)
    write_json(tmp_path / "reports/router1/report.json", {"overall_result": "PASS"})
    (tmp_path / "reports/router1/report.html").write_text("<html></html>", encoding="utf-8")
    data = network_lab.build_latest_lab_overview(prof, tmp_path)
    output = tmp_path / "reports/lab-summary/latest_lab_overview.html"

    network_lab.write_html_overview(data, output, tmp_path)

    html = output.read_text(encoding="utf-8")
    assert '<a href="../router1/report.html">reports/router1/report.html</a>' in html


def test_report_index_uses_lab_summary_latest_overview_output_paths():
    prof = network_lab.load_lab_runner_profile(Path("topology_profiles/day14_lab_runner_profile.json"))

    assert prof["overview_output"]["json"] == "reports/lab-summary/latest_lab_overview.json"
    assert prof["overview_output"]["html"] == "reports/lab-summary/latest_lab_overview.html"


def test_list_tasks_prints_report_index_and_planned_tasks(capsys):
    exit_code = network_lab.main(["--list-tasks"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "report-index" in output
    assert "day4-baseline" in output
    assert "iperf3-performance" in output
    assert "day13-wireguard-summary" in output


def test_cli_task_report_index_dry_run_exits_zero(tmp_path):
    profile_path = tmp_path / "profile.json"
    write_json(profile_path, profile())

    assert (
        network_lab.main(
            ["--task", "report-index", "--profile", str(profile_path), "--dry-run"],
            project_root=tmp_path,
        )
        == 0
    )


def test_cli_task_report_index_creates_json_and_html_using_fake_reports(tmp_path):
    prof = profile(required=False)
    profile_path = tmp_path / "profile.json"
    write_json(profile_path, prof)
    write_json(tmp_path / "reports/router1/report.json", {"status": "PASS"})
    write_json(tmp_path / "reports/lab-summary/summary.json", {"summary": {"result": "PASS"}})

    exit_code = network_lab.main(
        ["--task", "report-index", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    assert exit_code == 0
    assert (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_cli_day4_baseline_dry_run_prints_command_and_does_not_call_subprocess(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called during dry-run")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "day4-baseline", "--profile", str(profile_path), "--dry-run"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "python mikrotik_day4_multi_device_baseline.py" in output
    assert "Dry-run does not connect to devices" in output
    assert "No live workflow was executed" in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()


def test_cli_day4_baseline_calls_existing_script_through_subprocess(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        ["--task", "day4-baseline", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [([sys.executable, "mikrotik_day4_multi_device_baseline.py"], tmp_path.resolve())]
    assert "Day4 baseline finished" in output
    assert "PASS" in output


def test_cli_day4_baseline_nonzero_subprocess_return_code_is_returned(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)

    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda _command, cwd: SimpleNamespace(returncode=7),
    )

    exit_code = network_lab.main(
        ["--task", "day4-baseline", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 7
    assert "FAIL" in output
    assert "exit code 7" in output
    assert "python network_lab.py --task report-index" in output


def test_cli_day8_performance_dry_run_prints_command_and_safety_notes(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called during Day8 dry-run")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "iperf3-performance", "--profile", str(profile_path), "--dry-run"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day8 iperf3 performance" in output
    assert "Mode: Dry run" in output
    assert "python performance_test.py --profile topology_profiles/day8_iperf3_router_performance.json" in output
    assert "Safety notes" in output
    assert "No live workflow was executed" in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_cli_day8_performance_calls_existing_script_through_subprocess(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        ["--task", "iperf3-performance", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [
        (
            [
                sys.executable,
                "performance_test.py",
                "--profile",
                "topology_profiles/day8_iperf3_router_performance.json",
            ],
            tmp_path.resolve(),
        )
    ]
    assert "Day8 iperf3 performance completed successfully" in output
    assert "PASS" in output


def test_cli_day8_performance_nonzero_subprocess_return_code_is_returned(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)

    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda _command, cwd: SimpleNamespace(returncode=9),
    )

    exit_code = network_lab.main(
        ["--task", "iperf3-performance", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 9
    assert "FAIL" in output
    assert "exit code 9" in output


def test_cli_report_index_output_lists_report_items(tmp_path, capsys):
    prof = profile(required=False)
    profile_path = tmp_path / "profile.json"
    write_json(profile_path, prof)
    write_json(tmp_path / "reports/router1/report.json", {"status": "PASS"})
    write_json(tmp_path / "reports/lab-summary/summary.json", {"summary": {"result": "PASS"}})

    exit_code = network_lab.main(
        ["--task", "report-index", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Device report results" in output
    assert "router1 / Optional Report" in output
    assert "Lab summary report results" in output
    assert "Lab Summary" in output


def test_no_argument_main_opens_interactive_menu_with_mocked_input(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt: "0")

    exit_code = network_lab.main([], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Select an option by number" in output
    assert "Exiting Day14 interactive menu" in output


def test_interactive_exit_does_not_print_completion_message(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt: "0")

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert network_lab.INTERACTIVE_ACTION_COMPLETE not in output
    assert output.count("Select an option by number") == 1


def test_interactive_action_prints_completion_and_reprints_full_menu(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert output.count("Select an option by number") == 2
    assert output.count("  8. Show recommended command for Day13 multi-router WireGuard summary") == 2


def test_interactive_dry_run_does_not_create_output_files(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["3", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Mode: Dry run" in output
    assert "No reports were written" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_interactive_report_index_writes_overview_files(tmp_path, monkeypatch):
    write_default_profile(tmp_path)
    write_json(tmp_path / "reports/router1/report.json", {"status": "PASS"})
    write_json(tmp_path / "reports/lab-summary/summary.json", {"summary": {"result": "PASS"}})
    choices = iter(["2", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    assert exit_code == 0
    assert (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_interactive_day4_option_asks_for_confirmation(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["5", "n", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run should not be called")),
    )

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "live SSH validation workflow" in output
    assert "python mikrotik_day4_multi_device_baseline.py" in output
    assert "Day4 baseline cancelled" in output


@pytest.mark.parametrize("confirmation", ["n", ""])
def test_interactive_day4_option_without_confirmation_cancels_safely(
    tmp_path,
    monkeypatch,
    capsys,
    confirmation,
):
    write_default_profile(tmp_path)
    choices = iter(["5", confirmation, "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called without confirmation")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day4 baseline cancelled" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()


def test_interactive_day4_option_with_y_delegates_to_day4_script(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    choices = iter(["5", "y", "0"])
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [([sys.executable, "mikrotik_day4_multi_device_baseline.py"], tmp_path.resolve())]
    assert "Day4 baseline finished" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output


def test_interactive_day8_option_asks_for_confirmation(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["6", "n", "0"])
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return next(choices)

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run should not be called")),
    )

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "live iperf3 performance workflow" in output
    assert "python performance_test.py --profile topology_profiles/day8_iperf3_router_performance.json" in output
    assert "Confirm live Day8 iperf3 performance run" in prompts[1]
    assert "Day8 iperf3 performance cancelled" in output


def test_interactive_day8_option_with_y_delegates_to_day8_script(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    choices = iter(["6", "y", "0"])
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [
        (
            [
                sys.executable,
                "performance_test.py",
                "--profile",
                "topology_profiles/day8_iperf3_router_performance.json",
            ],
            tmp_path.resolve(),
        )
    ]
    assert "Day8 iperf3 performance completed successfully" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output


@pytest.mark.parametrize("confirmation", ["n", "", "yes"])
def test_interactive_day8_option_without_y_cancels_safely(
    tmp_path,
    monkeypatch,
    capsys,
    confirmation,
):
    write_default_profile(tmp_path)
    choices = iter(["6", confirmation, "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called without Day8 confirmation")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day8 iperf3 performance cancelled" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()


@pytest.mark.parametrize(
    ("choice", "expected"),
    [
        ("7", "mikrotik_day12_wireguard_vpn_automation.py"),
        ("8", "Day13 multi-router WireGuard summary workflow"),
    ],
)
def test_interactive_live_workflow_choices_only_print_recommended_commands(
    tmp_path,
    monkeypatch,
    capsys,
    choice,
    expected,
):
    write_default_profile(tmp_path)
    choices = iter([choice, "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run should not be called")),
    )

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert expected in output
    assert "no live workflow was executed" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()


def test_interactive_invalid_menu_input_is_handled_safely(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["bad", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Invalid menu choice" in output
    assert "Please enter a number from 0 to 8" in output


def test_no_live_tooling_is_required():
    tasks = network_lab.list_tasks()

    assert tasks[0]["id"] == "report-index"
    assert tasks[0]["status"] == "implemented"


def test_console_status_format_respects_no_color(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    colored = network_lab.format_status("PASS")
    monkeypatch.setenv("NO_COLOR", "1")

    plain = network_lab.format_status("PASS")

    assert "\033[" in colored
    assert plain == "[PASS]"
