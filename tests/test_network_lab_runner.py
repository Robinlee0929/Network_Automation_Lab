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


def write_day8_performance_profile(tmp_path: Path) -> Path:
    profile_path = tmp_path / "topology_profiles" / "day8_iperf3_router_performance.json"
    write_json(
        profile_path,
        {
            "default_lan_server_ip": "192.168.88.254",
            "default_duration_sec": 40,
            "default_omit_sec": 10,
            "default_parallel_streams": 4,
            "default_threshold_mbps": 800,
            "default_warn_threshold_mbps": 700,
        },
    )
    return profile_path


def write_wireguard_runner_config(tmp_path: Path, data=None, filename: str = "Set_WireguardVPN_config.json") -> Path:
    config_path = tmp_path / filename
    write_json(
        config_path,
        data
        or {
            "device_name": "Hex-s-2025-lab01",
            "router_host": "192.168.0.199",
            "router_username": "admin",
            "wg_interface": "wg0",
            "peer_name": "pc-wg",
            "lan_gateway_ip": "192.168.88.1",
            "lan_host_ip": "192.168.88.254",
            "iperf_server_ip": "192.168.88.254",
            "client_address": "10.10.10.2/32",
        },
    )
    return config_path


def write_delegated_day12_report(tmp_path: Path, device_name: str = "Hex-s-2025-lab02", data=None) -> Path:
    report_path = tmp_path / "reports" / device_name / "day12_wireguard_vpn_automation_report.json"
    write_json(
        report_path,
        data
        or {
            "overall_result": "PASS",
            "checks": {
                "wg_interface_exists": "PASS",
                "peer_exists": "PASS",
                "initial_handshake_seen": "PASS",
                "post_connectivity_handshake_seen": "PASS",
                "final_vpn_connectivity": "PASS",
                "ping_lan_gateway": "PASS",
                "ping_lan_host": "PASS",
                "tcp_5201_reachable": "PASS",
                "iperf_forward": "PASS",
                "iperf_reverse": "PASS",
            },
            "iperf_summary": {
                "forward_mbps": 166.0,
                "reverse_mbps": 225.0,
            },
        },
    )
    html_path = report_path.with_suffix(".html")
    html_path.write_text("<html><body>Day12 report</body></html>", encoding="utf-8")
    return report_path


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


def test_task_catalog_contains_day17_required_fields():
    required_fields = {
        "task_id",
        "display_name",
        "day",
        "category",
        "description",
        "safety_level",
        "execution_mode",
        "enabled",
        "requires_live_device",
        "requires_password",
        "produces_report",
        "report_paths",
        "related_script",
        "notes",
    }

    tasks = network_lab.list_tasks()

    assert tasks
    for task in tasks:
        assert required_fields.issubset(task)
    assert {task["task_id"] for task in tasks} >= {
        "report_index",
        "day4_baseline_validation",
        "day8_iperf3_performance",
        "wireguard_runner_safety_layer",
        "day13_wireguard_summary_only",
    }


def test_list_tasks_does_not_execute_live_device_commands(monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("list-tasks must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--list-tasks"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Task Catalog" in output
    assert "LIVE_READ_ONLY" in output
    assert "LIVE_PERFORMANCE" in output
    assert "guarded-live" in output


def test_report_visibility_index_works_when_reports_directory_is_missing(tmp_path, capsys):
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Report Index" in output
    assert "Summary: found=" in output
    assert "missing=" in output
    assert "disabled=" in output
    assert "Output: reports/report_index.html" in output
    assert "MISSING" in output
    assert "Day18 WireGuard runner integration uses dry-run and explicit confirmation guardrails" in output
    assert (tmp_path / "reports/report_index.html").exists()


def test_report_visibility_index_finds_partial_reports_and_marks_missing(tmp_path, capsys):
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"result": "PASS"},
    )
    (tmp_path / "reports" / "Hex-s-2025-lab01" / "day8_iperf3_WAN_TO_LAN_DNAT_report.html").parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    (tmp_path / "reports" / "Hex-s-2025-lab01" / "day8_iperf3_WAN_TO_LAN_DNAT_report.html").write_text(
        "<html>day8</html>",
        encoding="utf-8",
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day4 Baseline Validation" in output
    assert "[FOUND]" in output
    assert "Hex-s-2025-lab01" in output
    assert "JSON: reports/Hex-s-2025-lab01/day4_baseline_validation.json" in output
    assert "Day8 iperf3 Performance" in output
    assert "HTML: reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.html" in output
    assert "Day13 WireGuard Live Execution" in output
    assert "DISABLED FOR DAY18" in output
    assert "Expected Cisco switch report was not found in local reports folder." in output


def test_report_visibility_console_compacts_historical_day13_reports(tmp_path, capsys):
    for index in range(1, 7):
        write_json(
            tmp_path
            / "reports"
            / "lab-summary"
            / f"day13_multi_router_wireguard_client_to_site_summary_20260602_000{index}.json",
            {"result": "PASS"},
        )
        (
            tmp_path
            / "reports"
            / "lab-summary"
            / f"day13_multi_router_wireguard_client_to_site_summary_20260602_000{index}.html"
        ).write_text("<html>day13</html>", encoding="utf-8")

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "more reports hidden in console" in output
    assert "open reports/report_index.html for full list" in output
    assert "day13_multi_router_wireguard_client_to_site_summary_20260602_0001.json" in output
    assert "day13_multi_router_wireguard_client_to_site_summary_20260602_0004.json" not in output
    assert "Expected Cisco switch report was not found in local reports folder." in output
    assert "DISABLED FOR DAY18" in output
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "day13_multi_router_wireguard_client_to_site_summary_20260602_0006.json" in html


def test_wireguard_runner_catalog_entry_uses_feature_identity():
    wireguard_tasks = [task for task in network_lab.list_tasks() if task["category"] == "vpn"]

    assert wireguard_tasks
    runner = next(task for task in wireguard_tasks if task["id"] == "wireguard-runner")
    assert runner["task_id"] == "wireguard_runner_safety_layer"
    assert runner["display_name"] == "WireGuard Runner Safety Layer"
    assert runner["day"] == "Day18"
    assert runner["enabled"] is True
    assert runner["safety_level"] == "guarded-live"
    assert runner["execution_mode"] == "dry-run by default"
    assert runner["report_output_path"] == "reports/lab-summary/wireguard_runner_safety_layer.json"


def test_day13_wireguard_summary_remains_disabled_until_own_safety_layer():
    day13 = next(task for task in network_lab.list_tasks() if task["id"] == "day13-wireguard-summary")

    assert day13["enabled"] is False
    assert day13["safety_level"] == "FUTURE_RESERVED"
    assert "Day13 summary remains report-only in Day18" in day13["notes"]


def test_wireguard_placeholder_does_not_call_live_scripts(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("WireGuard placeholder/report index must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day18 WireGuard runner integration uses dry-run and explicit confirmation guardrails" in output
    assert "WireGuard Runner Safety Layer" in output
    assert "reports/lab-summary/wireguard_runner_safety_layer.json" in output
    assert "day12-wireguard-live-validation" not in output
    assert "day18-wireguard-runner" not in output


def test_html_report_index_generation_contains_catalog_reports_and_legend(tmp_path):
    rows = network_lab.discover_report_visibility(tmp_path)
    output = tmp_path / "reports" / "report_index.html"

    network_lab.write_report_index_html(network_lab.list_tasks(), rows, output, tmp_path)

    html = output.read_text(encoding="utf-8")
    assert "Network Automation Lab Report Index" in html
    assert "Task Catalog Summary" in html
    assert "Report Visibility" in html
    assert "Safety Level Legend" in html
    assert "Day18 WireGuard runner integration uses a safety layer" in html
    assert "WireGuard Runner Safety Layer" in html
    assert "day12-wireguard-live-validation" not in html
    assert "day18-wireguard-runner" not in html


def test_report_index_does_not_print_config_json_secret_content(tmp_path, capsys):
    write_json(tmp_path / "config.json", {"password": "super-secret-password"})
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"result": "PASS"},
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert exit_code == 0
    assert "super-secret-password" not in output
    assert "super-secret-password" not in html
    assert "config.json" not in output


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
    write_day8_performance_profile(tmp_path)

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
    assert "python performance_test.py --lan-server-ip 192.168.88.254" in output
    assert "--duration 40" in output
    assert "--omit 10" in output
    assert "--parallel 4" in output
    assert "--threshold-mbps 800" in output
    assert "--warn-threshold-mbps 700" in output
    assert "--profile" not in output
    assert "Safety notes" in output
    assert "No live workflow was executed" in output
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.json").exists()
    assert not (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_cli_day8_performance_command_does_not_include_unsupported_profile_argument(tmp_path):
    write_day8_performance_profile(tmp_path)

    command = network_lab._build_day8_performance_command(tmp_path)

    assert "--profile" not in command
    assert command[1:] == [
        "performance_test.py",
        "--lan-server-ip",
        "192.168.88.254",
        "--duration",
        "40",
        "--omit",
        "10",
        "--parallel",
        "4",
        "--threshold-mbps",
        "800",
        "--warn-threshold-mbps",
        "700",
    ]


def test_cli_day8_performance_calls_existing_script_through_subprocess(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)
    write_day8_performance_profile(tmp_path)
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
                "--lan-server-ip",
                "192.168.88.254",
                "--duration",
                "40",
                "--omit",
                "10",
                "--parallel",
                "4",
                "--threshold-mbps",
                "800",
                "--warn-threshold-mbps",
                "700",
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
    write_day8_performance_profile(tmp_path)

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


def test_wireguard_runner_command_builder_uses_guarded_args_only():
    command = network_lab._build_wireguard_runner_command(
        config_path="Set_WireguardVPN_lab02_config.json",
        run_iperf=True,
    )

    assert command == [
        sys.executable,
        "mikrotik_day12_wireguard_vpn_automation.py",
        "--config",
        "Set_WireguardVPN_lab02_config.json",
        "--run-iperf",
        "--expect-connected",
        "--non-interactive",
    ]
    assert "--recreate-peer" not in command
    assert "--apply-firewall-fixes" not in command
    network_lab._validate_wireguard_runner_command(command, config_path="Set_WireguardVPN_lab02_config.json")


def test_wireguard_runner_command_builder_keeps_default_config_compatible():
    command = network_lab._build_wireguard_runner_command()

    assert command == [
        sys.executable,
        "mikrotik_day12_wireguard_vpn_automation.py",
        "--config",
        "Set_WireguardVPN_config.json",
        "--non-interactive",
    ]
    network_lab._validate_wireguard_runner_command(command)


def test_wireguard_runner_guard_rejects_write_flags():
    command = network_lab._build_wireguard_runner_command()
    command.append("--apply-firewall-fixes")

    with pytest.raises(ValueError, match="forbidden live write flags"):
        network_lab._validate_wireguard_runner_command(command)


def test_cli_wireguard_runner_dry_run_does_not_call_subprocess_and_writes_report(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called during WireGuard runner dry-run")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--dry-run",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "WireGuard Runner Safety Layer" in output
    assert "Mode: Dry run" in output
    assert "python network_lab.py --task wireguard-runner --dry-run" in output
    assert "Selected WireGuard config: Set_WireguardVPN_lab02_config.json" in output
    assert "does not include --recreate-peer or --apply-firewall-fixes" in output
    assert (
        "Live execution requires explicit --allow-live-wireguard. "
        "Interactive menu execution also requires explicit confirmation."
    ) in output
    assert "from CLI or an interactive y confirmation" not in output
    assert "No live workflow was executed" in output
    report = json.loads((tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text())
    assert report["task_id"] == "wireguard_runner_safety_layer"
    assert report["display_name"] == "WireGuard Runner Safety Layer"
    assert report["day"] == "Day18"
    assert report["category"] == "vpn"
    assert report["mode"] == "dry-run"
    assert report["result"] == "DRY-RUN"
    assert report["selected_config_path"] == "Set_WireguardVPN_lab02_config.json"
    assert report["delegated_command_summary"] == (
        "python mikrotik_day12_wireguard_vpn_automation.py "
        "--config Set_WireguardVPN_lab02_config.json --non-interactive"
    )


def test_cli_wireguard_runner_without_allow_live_blocks_safely(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess.run should not be called without --allow-live-wireguard")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Selected WireGuard config: Set_WireguardVPN_lab02_config.json" in output
    assert "WireGuard live execution requires explicit --allow-live-wireguard" in output
    report = json.loads((tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text())
    assert report["mode"] == "blocked"
    assert report["result"] == "BLOCKED"
    assert report["selected_config_path"] == "Set_WireguardVPN_lab02_config.json"
    assert report["message"] == "WireGuard live execution requires explicit --allow-live-wireguard"


def test_cli_wireguard_runner_default_config_path_remains_compatible(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)

    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run should not be called")),
    )

    exit_code = network_lab.main(
        ["--task", "wireguard-runner", "--profile", str(profile_path), "--dry-run"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    report = json.loads((tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text())
    assert exit_code == 0
    assert "Selected WireGuard config: Set_WireguardVPN_config.json" in output
    assert report["selected_config_path"] == "Set_WireguardVPN_config.json"


def test_cli_wireguard_runner_allow_live_uses_shell_false_and_timeout(
    tmp_path,
    monkeypatch,
    capsys,
):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    calls = []

    def fake_run(command, cwd, shell, timeout):
        calls.append((command, cwd, shell, timeout))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--allow-live-wireguard",
            "--wireguard-run-iperf",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [
        (
            [
                sys.executable,
                "mikrotik_day12_wireguard_vpn_automation.py",
                "--config",
                "Set_WireguardVPN_lab02_config.json",
                "--run-iperf",
                "--expect-connected",
                "--non-interactive",
            ],
            tmp_path.resolve(),
            False,
            network_lab.DAY12_WIREGUARD_TIMEOUT_SECONDS,
        )
    ]
    assert "--recreate-peer" not in calls[0][0]
    assert "--apply-firewall-fixes" not in calls[0][0]
    assert "Selected WireGuard config: Set_WireguardVPN_lab02_config.json" in output
    assert "WireGuard runner completed successfully" in output


def test_cli_wireguard_runner_allow_live_without_iperf_does_not_delegate_iperf(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    calls = []

    def fake_run(command, cwd, shell, timeout):
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--allow-live-wireguard",
        ],
        project_root=tmp_path,
    )

    assert exit_code == 0
    assert calls == [
        [
            sys.executable,
            "mikrotik_day12_wireguard_vpn_automation.py",
            "--config",
            "Set_WireguardVPN_lab02_config.json",
            "--non-interactive",
        ]
    ]
    assert "--run-iperf" not in calls[0]
    assert "--expect-connected" not in calls[0]


def test_cli_wireguard_runner_report_includes_delegated_day12_summary(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(
        tmp_path,
        data={
            "device_name": "Hex-s-2025-lab02",
            "router_host": "192.168.0.113",
            "router_username": "admin",
            "wg_interface": "wg0",
            "peer_name": "pc-wg-lab02",
            "lan_gateway_ip": "192.168.89.1",
            "lan_host_ip": "192.168.89.200",
            "iperf_server_ip": "192.168.89.200",
            "client_address": "10.10.20.2/32",
        },
        filename="Set_WireguardVPN_lab02_config.json",
    )

    def fake_run(command, cwd, shell, timeout):
        write_delegated_day12_report(tmp_path)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--allow-live-wireguard",
            "--wireguard-run-iperf",
        ],
        project_root=tmp_path,
    )

    capsys.readouterr()
    report = json.loads((tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text())
    html = (tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.html").read_text()
    assert exit_code == 0
    assert report["result"] == "PASS"
    assert report["delegated_report"] == {
        "json": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json",
        "html": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.html",
    }
    assert report["delegated_result_summary"]["result"] == "PASS"
    assert report["delegated_result_summary"]["final_vpn_connectivity"] == "PASS"
    assert report["delegated_result_summary"]["initial_handshake_seen"] == "PASS"
    assert report["delegated_result_summary"]["post_connectivity_handshake_seen"] == "PASS"
    assert report["delegated_result_summary"]["iperf_forward_mbps"] == 166.0
    assert report["delegated_result_summary"]["iperf_reverse_mbps"] == 225.0
    assert report["delegated_result_summary"]["pass_count"] == 10
    assert "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json" in html
    assert "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.html" in html
    assert "final_vpn_connectivity" in html
    assert "iperf_forward_mbps" in html
    assert "166.0" in html
    assert "iperf_reverse_mbps" in html
    assert "225.0" in html


def test_cli_wireguard_runner_passes_when_delegated_report_parse_fails(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(
        tmp_path,
        data={
            "device_name": "Hex-s-2025-lab02",
            "router_host": "192.168.0.113",
            "router_username": "admin",
            "wg_interface": "wg0",
            "peer_name": "pc-wg-lab02",
        },
        filename="Set_WireguardVPN_lab02_config.json",
    )

    def fake_run(command, cwd, shell, timeout):
        report_path = tmp_path / "reports" / "Hex-s-2025-lab02" / "day12_wireguard_vpn_automation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("{not-json", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--allow-live-wireguard",
        ],
        project_root=tmp_path,
    )

    capsys.readouterr()
    report = json.loads((tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text())
    assert exit_code == 0
    assert report["result"] == "PASS"
    assert "delegated_report_parse_warning" in report
    assert "Could not parse delegated Day12 report JSON" in report["delegated_report_parse_warning"]
    assert any("Could not parse delegated Day12 report JSON" in warning for warning in report["warnings"])


def test_cli_wireguard_runner_delegated_summary_does_not_copy_day12_secrets(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(
        tmp_path,
        data={
            "device_name": "Hex-s-2025-lab02",
            "router_host": "192.168.0.113",
            "router_username": "admin",
            "router_password": "router-secret-password",
            "wg_interface": "wg0",
            "peer_name": "pc-wg-lab02",
            "private_key": "CONFIG_PRIVATE",
            "preshared_key": "CONFIG_PRESHARED",
            "api_token": "CONFIG_TOKEN",
        },
        filename="Set_WireguardVPN_lab02_config.json",
    )

    def fake_run(command, cwd, shell, timeout):
        write_delegated_day12_report(
            tmp_path,
            data={
                "overall_result": "PASS",
                "checks": {
                    "final_vpn_connectivity": "PASS",
                    "initial_handshake_seen": "PASS",
                    "post_connectivity_handshake_seen": "PASS",
                },
                "iperf_summary": {"forward_mbps": 166.0, "reverse_mbps": 225.0},
                "sanitized_client_config_summary": "PrivateKey = super-secret-private-key",
                "router_password": "day12-router-secret",
                "nested": {"preshared_key": "day12-preshared", "api_token": "day12-token"},
            },
        )
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--allow-live-wireguard",
            "--wireguard-run-iperf",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    report_text = (tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text()
    html = (tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.html").read_text()
    assert exit_code == 0
    for secret in (
        "router-secret-password",
        "CONFIG_PRIVATE",
        "CONFIG_PRESHARED",
        "CONFIG_TOKEN",
        "super-secret-private-key",
        "day12-router-secret",
        "day12-preshared",
        "day12-token",
    ):
        assert secret not in output
        assert secret not in report_text
        assert secret not in html
    assert "sanitized_client_config_summary" not in report_text


def test_cli_wireguard_runner_timeout_returns_124(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path)

    def timeout_run(command, cwd, shell, timeout):
        raise network_lab.subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr(network_lab.subprocess, "run", timeout_run)

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--allow-live-wireguard",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 124
    assert "timed out after" in output
    assert str(network_lab.DAY12_WIREGUARD_TIMEOUT_SECONDS) in output


def test_wireguard_runner_reports_mask_secret_like_fields(tmp_path, monkeypatch, capsys):
    profile_path = write_default_profile(tmp_path)
    write_wireguard_runner_config(
        tmp_path,
        {
            "device_name": "Hex-s-2025-lab01",
            "router_host": "192.168.0.199",
            "router_username": "admin",
            "router_password": "super-secret-password",
            "wg_interface": "wg0",
            "peer_name": "pc-wg",
            "nested": {
                "private_key": "PRIVATE",
                "preshared_key": "PRESHARED",
                "api_token": "TOKEN",
            },
        },
        filename="Set_WireguardVPN_lab02_config.json",
    )
    monkeypatch.setattr(network_lab.subprocess, "run", lambda *_args, **_kwargs: SimpleNamespace(returncode=0))

    exit_code = network_lab.main(
        [
            "--task",
            "wireguard-runner",
            "--profile",
            str(profile_path),
            "--wireguard-config",
            "Set_WireguardVPN_lab02_config.json",
            "--dry-run",
        ],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    report_text = (tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.json").read_text()
    html = (tmp_path / "reports/lab-summary/wireguard_runner_safety_layer.html").read_text()
    assert exit_code == 0
    assert "Selected WireGuard config: Set_WireguardVPN_lab02_config.json" in output
    assert "Set_WireguardVPN_lab02_config.json" in report_text
    for secret in ("super-secret-password", "PRIVATE", "PRESHARED", "TOKEN"):
        assert secret not in output
        assert secret not in report_text
        assert secret not in html


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
    assert output.count("  7. WireGuard Runner Safety Layer") == 2
    assert output.count("  8. Show recommended command for Day13 multi-router WireGuard summary") == 2
    assert "day12-wireguard-live-validation" not in output
    assert "day18-wireguard-runner" not in output


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
    write_day8_performance_profile(tmp_path)
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
    assert "python performance_test.py --lan-server-ip 192.168.88.254" in output
    assert "Confirm live Day8 iperf3 performance run" in prompts[1]
    assert "Day8 iperf3 performance cancelled" in output


def test_interactive_day8_option_with_y_delegates_to_day8_script(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_day8_performance_profile(tmp_path)
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
                "--lan-server-ip",
                "192.168.88.254",
                "--duration",
                "40",
                "--omit",
                "10",
                "--parallel",
                "4",
                "--threshold-mbps",
                "800",
                "--warn-threshold-mbps",
                "700",
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
    write_day8_performance_profile(tmp_path)
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


def test_interactive_wireguard_runner_option_asks_for_confirmation(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    choices = iter(["7", "n", "0"])
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
    assert "live WireGuard validation workflow" in output
    assert "python mikrotik_day12_wireguard_vpn_automation.py --config Set_WireguardVPN_config.json --non-interactive" in output
    assert "Confirm live WireGuard runner execution" in prompts[1]
    assert "WireGuard runner cancelled" in output
    assert "Day12 WireGuard" not in output


def test_interactive_wireguard_runner_option_with_y_delegates_to_existing_script(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path)
    choices = iter(["7", "y", "0"])
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fake_run(command, cwd, shell, timeout):
        calls.append((command, cwd, shell, timeout))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [
        (
            [
                sys.executable,
                "mikrotik_day12_wireguard_vpn_automation.py",
                "--config",
                "Set_WireguardVPN_config.json",
                "--non-interactive",
            ],
            tmp_path.resolve(),
            False,
            network_lab.DAY12_WIREGUARD_TIMEOUT_SECONDS,
        )
    ]
    assert "WireGuard runner completed successfully" in output
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output


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
