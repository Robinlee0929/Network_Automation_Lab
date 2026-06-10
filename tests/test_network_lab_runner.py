import json
import os
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

import network_lab


def windows_long_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    resolved = str(path.resolve())
    if resolved.startswith("\\\\?\\"):
        return path
    return Path("\\\\?\\" + resolved)


def write_json(path: Path, data):
    path = windows_long_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def write_text(path: Path, text: str):
    path = windows_long_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


@pytest.mark.parametrize(
    ("payload", "expected_status", "expected_message"),
    [
        ({"overall_status": "PASS"}, "PASS", ""),
        ({"status": "WARN"}, "WARN", ""),
        ({"device": "router1"}, "UNKNOWN", "Could not infer result from supported report fields."),
        ({"status": "DEFERRED_REVIEW"}, "UNKNOWN", "Could not infer result from supported report fields."),
    ],
)
def test_report_index_status_field_detection_handles_supported_and_unknown_shapes(
    tmp_path,
    payload,
    expected_status,
    expected_message,
):
    item = {"name": "Report", "json": "reports/report.json", "html": "reports/report.html"}
    write_json(tmp_path / "reports/report.json", payload)

    record = network_lab.check_report_file(item, tmp_path)

    assert record["status"] == expected_status
    assert record["message"] == expected_message


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
    assert "portfolio-finalize" in output
    assert "day4-baseline" in output
    assert "iperf3-performance" in output
    assert "wireguard-runner" in output
    assert "day13-wireguard-summary" in output
    assert "Portfolio Evidence Index" in output
    assert "Multi-device Baseline Validation" in output
    assert "iperf3 Performance Test" in output
    assert "WireGuard VPN Validation" in output
    assert "WireGuard Summary Only" in output
    assert "day19_runner_evidence_index" not in output
    assert "Day19 Runner Evidence Index" not in output
    assert "Day14-Day19" not in output
    assert "Related script" not in output
    assert "Reports:" not in output


def test_list_tasks_verbose_prints_internal_metadata(capsys):
    exit_code = network_lab.main(["--list-tasks", "--verbose"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "day19_runner_evidence_index" in output
    assert "Day19 Runner Evidence Index" in output
    assert "Day14-Day19" in output
    assert "Related script" in output
    assert "Reports:" in output
    assert "Notes:" in output
    assert "User-facing name: Portfolio Evidence Index" in output


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
        "report_outputs",
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
    assert "read-only" in output
    assert "guarded-live" in output
    assert "report-only" in output
    assert "guarded-live" in output
    assert "day19_runner_evidence_index" not in output


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
    assert "local report index" in output
    assert "guarded-live / dry-run" in output
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
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "guarded-live performance evidence" in html


def test_lab_overview_infers_day35_overall_status_as_pass(tmp_path, capsys):
    prof = profile(required=False)
    prof["devices"] = []
    prof["lab_summary_reports"] = [
        {
            "name": "Day35 VRRP Failover Validation",
            "json": "reports/lab-summary/day35_vrrp_failover_validation.json",
            "html": "reports/lab-summary/day35_vrrp_failover_validation.html",
            "required": False,
        }
    ]
    profile_path = tmp_path / "profile.json"
    write_json(profile_path, prof)
    write_json(
        tmp_path / "reports" / "lab-summary" / "day35_vrrp_failover_validation.json",
        {
            "day": "Day35",
            "title": "VRRP Failover Validation",
            "overall_status": "PASS",
        },
    )

    exit_code = network_lab.main(["--task", "report-index", "--profile", str(profile_path)], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "[PASS] Day35 VRRP Failover Validation" in output


def test_report_visibility_console_compacts_historical_day13_reports(tmp_path, capsys):
    for index in range(1, 7):
        write_json(
            tmp_path
            / "reports"
            / "lab-summary"
            / f"day13_wireguard_000{index}.json",
            {"result": "PASS"},
        )
        write_text(
            tmp_path
            / "reports"
            / "lab-summary"
            / f"day13_wireguard_000{index}.html",
            "<html>day13</html>",
        )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "more reports hidden in console" in output
    assert "open reports/report_index.html for full list" in output
    assert "day13_wireguard_0001.json" in output
    assert "day13_wireguard_0004.json" not in output
    assert "Expected Cisco switch report was not found in local reports folder." in output
    assert "DISABLED FOR DAY18" in output
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "day13_wireguard_0006.json" in html


def test_wireguard_runner_catalog_entry_uses_feature_identity():
    wireguard_tasks = [task for task in network_lab.list_tasks() if task["category"] == "vpn"]

    assert wireguard_tasks
    runner = next(task for task in wireguard_tasks if task["id"] == "wireguard-runner")
    assert runner["task_id"] == "wireguard_runner_safety_layer"
    assert runner["display_name"] == "WireGuard Runner Safety Layer"
    assert runner["day"] == "Day18"
    assert runner["enabled"] is True
    assert runner["safety_level"] == "guarded-live"
    assert runner["execution_mode"] == "dry-run"
    assert runner["report_output_path"] == "reports/lab-summary/wireguard_runner_safety_layer.json"


def test_day13_wireguard_summary_remains_disabled_until_own_safety_layer():
    day13 = next(task for task in network_lab.list_tasks() if task["id"] == "day13-wireguard-summary")

    assert day13["enabled"] is False
    assert day13["safety_level"] == "disabled"
    assert "Disabled live runner task" in day13["notes"]


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


def test_report_index_console_shows_day18_runner_evidence(tmp_path, capsys):
    write_json(
        tmp_path / "reports" / "lab-summary" / "wireguard_runner_safety_layer.json",
        {
            "selected_config_path": "Set_WireguardVPN_lab02_config.json",
            "safety_guardrail_status": {
                "dry_run_default": "PASS",
                "requires_allow_live_wireguard": "PASS",
                "subprocess_shell_false": "PASS",
            },
            "delegated_report": {
                "json": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json",
                "html": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.html",
            },
            "delegated_result_summary": {
                "final_vpn_connectivity": "PASS",
                "iperf_forward_mbps": 181.0,
                "iperf_reverse_mbps": 231.0,
            },
        },
    )
    (tmp_path / "reports" / "lab-summary" / "wireguard_runner_safety_layer.html").write_text(
        "<html>runner</html>",
        encoding="utf-8",
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "WireGuard Runner Safety Layer" in output
    assert "reports/lab-summary/wireguard_runner_safety_layer.json" in output
    assert "Set_WireguardVPN_lab02_config.json" in output
    assert "vpn=PASS" in output
    assert "iperf=181.0/231.0 Mbps" in output
    assert "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json" in output
    assert "dry_run_default=PASS" in output


def test_report_index_html_shows_day18_runner_evidence_details(tmp_path):
    write_json(
        tmp_path / "reports" / "lab-summary" / "wireguard_runner_safety_layer.json",
        {
            "selected_config_path": "Set_WireguardVPN_lab02_config.json",
            "safety_guardrail_status": {
                "dry_run_default": "PASS",
                "requires_allow_live_wireguard": "PASS",
                "subprocess_shell_false": "PASS",
                "forbidden_write_flags_blocked": "PASS",
            },
            "delegated_report": {
                "json": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json",
                "html": "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.html",
            },
            "delegated_result_summary": {
                "final_vpn_connectivity": "PASS",
                "iperf_forward_mbps": 181.0,
                "iperf_reverse_mbps": 231.0,
            },
        },
    )
    (tmp_path / "reports" / "lab-summary" / "wireguard_runner_safety_layer.html").write_text(
        "<html>runner</html>",
        encoding="utf-8",
    )
    rows = network_lab.discover_report_visibility(tmp_path)
    output = tmp_path / "reports" / "report_index.html"

    network_lab.write_report_index_html(network_lab.list_tasks(), rows, output, tmp_path)

    html = output.read_text(encoding="utf-8")
    assert "Day18 WireGuard Runner Evidence" in html
    assert "Day12 remains the detailed source of truth" in html
    assert "reports/lab-summary/wireguard_runner_safety_layer.json" in html
    assert "reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json" in html
    assert "Set_WireguardVPN_lab02_config.json" in html
    assert "Final VPN connectivity" in html
    assert "181.0" in html
    assert "231.0" in html
    assert "forbidden_write_flags_blocked" in html


def test_html_report_index_generation_contains_catalog_reports_and_legend(tmp_path):
    rows = network_lab.discover_report_visibility(tmp_path)
    output = tmp_path / "reports" / "report_index.html"

    network_lab.write_report_index_html(network_lab.list_tasks(), rows, output, tmp_path)

    html = output.read_text(encoding="utf-8")
    assert "Network Automation Lab Report Index" in html
    assert "Task Catalog Summary" in html
    assert "Report Visibility" in html
    assert "Safety Level Legend" in html
    assert "Task Name" in html
    assert "Report Type" in html
    assert "Description" in html
    assert "Multi-device baseline report" in html
    assert "live read-only evidence" in html
    assert "Day8 performance report" in html
    assert "guarded-live performance evidence" in html
    assert "Day21 report viewer / evidence viewer relationship" in html
    assert "local report index" in html
    assert "Day18 WireGuard runner integration uses a safety layer" in html
    assert "WireGuard Runner Safety Layer" in html
    assert "day12-wireguard-live-validation" not in html
    assert "day18-wireguard-runner" not in html
    lower_html = html.lower()
    assert "password" not in lower_html
    assert "private_key" not in lower_html
    assert "privatekey" not in lower_html
    assert "[interface]" not in lower_html
    assert "wireguard private key" not in lower_html


def test_portfolio_finalization_writes_day19_evidence_index(tmp_path, capsys):
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"result": "PASS"},
    )
    (tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.html").write_text(
        "<html>day4</html>",
        encoding="utf-8",
    )

    exit_code = network_lab.main(["--portfolio-finalize"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports" / "portfolio" / "day19_runner_evidence_index.json"
    html_path = tmp_path / "reports" / "portfolio" / "day19_runner_evidence_index.html"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Day19 Runner Evidence Index" in output
    assert "without live execution" in output
    assert data["day"] == "Day19"
    assert data["portfolio_readiness"] == "READY_WITH_GAPS"
    assert data["summary"]["reports_found"] >= 1
    assert any(item["quality"] == "READY" for item in data["evidence_items"])
    assert any(item["report_type"] == "Multi-device baseline report" for item in data["evidence_items"])
    assert any(item["safety"] == "live read-only evidence" for item in data["evidence_items"])
    assert any("report index only reads" in item["description"].lower() for item in data["evidence_items"])
    assert "Portfolio Highlights" in html
    assert "Report Type" in html
    assert "Safety" in html
    assert "Description" in html
    assert "day4_baseline_validation.html" in html
    lower_html = html.lower()
    assert "password" not in lower_html
    assert "private_key" not in lower_html
    assert "privatekey" not in lower_html
    assert "[interface]" not in lower_html


def test_cli_task_portfolio_finalize_writes_evidence_index(tmp_path, capsys):
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"result": "PASS"},
    )

    exit_code = network_lab.main(["--task", "portfolio-finalize"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day19 Runner Evidence Index" in output
    assert (tmp_path / "reports/portfolio/day19_runner_evidence_index.json").exists()
    assert (tmp_path / "reports/portfolio/day19_runner_evidence_index.html").exists()


def test_cli_task_demo_flow_writes_day24_walkthrough(tmp_path, capsys):
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {"result": "PASS"},
    )
    (tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.html").write_text(
        "<html>day4</html>",
        encoding="utf-8",
    )

    exit_code = network_lab.main(["--task", "demo-flow"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports" / "portfolio" / "day24_rc_demo_flow.json"
    html_path = tmp_path / "reports" / "portfolio" / "day24_rc_demo_flow.html"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "Day24 RC Demo Flow" in output
    assert "without live execution" in output
    assert data["day"] == "Day24"
    assert data["mode"] == "report-only"
    assert data["result"] == "READY"
    assert any(step["section"] == "Runner Safety" for step in data["walkthrough_steps"])
    assert any("python network_lab.py --list-tasks --verbose" in step["command_or_location"] for step in data["walkthrough_steps"])
    assert "http://127.0.0.1:5000/reports" in data["recommended_open_order"]
    assert "Walkthrough Steps" in html
    assert "RC Checklist" in html
    assert "WireGuard validation is intentionally dry-run by default" in html


def test_demo_flow_does_not_execute_subprocess_or_read_config_secret(tmp_path, monkeypatch, capsys):
    write_json(tmp_path / "config.json", {"password": "super-secret-password"})

    def fail_run(*_args, **_kwargs):
        raise AssertionError("demo flow must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--task", "demo-flow"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_text = (tmp_path / "reports/portfolio/day24_rc_demo_flow.json").read_text(encoding="utf-8")
    html = (tmp_path / "reports/portfolio/day24_rc_demo_flow.html").read_text(encoding="utf-8")
    assert exit_code == 0
    assert "super-secret-password" not in output
    assert "super-secret-password" not in json_text
    assert "super-secret-password" not in html
    assert "config.json" not in output


def test_task_catalog_contains_day24_demo_flow_entry():
    task = next(item for item in network_lab.list_tasks() if item["id"] == "demo-flow")

    assert task["task_id"] == "day24_rc_demo_flow"
    assert task["day"] == "Day24"
    assert task["safety_level"] == "report-only"
    assert task["requires_live_device"] is False
    assert "reports/portfolio/day24_rc_demo_flow.html" in task["report_paths"]


def test_portfolio_finalization_does_not_execute_subprocess_or_read_config_secret(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_json(tmp_path / "config.json", {"password": "super-secret-password"})

    def fail_run(*_args, **_kwargs):
        raise AssertionError("portfolio finalization must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--portfolio-finalize"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_text = (tmp_path / "reports/portfolio/day19_runner_evidence_index.json").read_text()
    html = (tmp_path / "reports/portfolio/day19_runner_evidence_index.html").read_text()
    assert exit_code == 0
    assert "super-secret-password" not in output
    assert "super-secret-password" not in json_text
    assert "super-secret-password" not in html
    assert "config.json" not in output


def test_task_catalog_contains_day19_portfolio_entry():
    task = next(item for item in network_lab.list_tasks() if item["id"] == "portfolio-finalize")

    assert task["task_id"] == "day19_runner_evidence_index"
    assert task["day"] == "Day19"
    assert task["safety_level"] == "report-only"
    assert task["requires_live_device"] is False
    assert "reports/portfolio/day19_runner_evidence_index.html" in task["report_paths"]


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
    assert "Network Lab Runner" in output
    assert "Select an option by number" in output
    assert "Exiting Network Lab Runner." in output
    assert "Exiting Day14 interactive menu" not in output


def test_interactive_exit_does_not_print_completion_message(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt: "0")

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert network_lab.INTERACTIVE_ACTION_COMPLETE not in output
    assert output.count("Select an option by number") == 1
    assert "Exiting Network Lab Runner." in output
    assert "Day14 interactive menu" not in output


def test_interactive_menu_uses_user_facing_labels(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    monkeypatch.setattr("builtins.input", lambda _prompt: "0")

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Network Lab Runner" in output
    assert "  2. Generate report index" in output
    assert "  5. Run multi-device baseline validation" in output
    assert "  6. Run iperf3 performance test" in output
    assert "  7. Run WireGuard VPN validation" in output
    assert "  8. Show WireGuard summary command" in output
    assert "Day14 Unified Lab Runner and Report Index" not in output
    assert "Run Day4 multi-device baseline" not in output
    assert "Run Day8 iperf3 performance workflow" not in output
    assert "WireGuard Runner Safety Layer" not in output
    assert "Show recommended command for Day13 multi-router WireGuard summary" not in output


def test_interactive_action_prints_completion_and_reprints_full_menu(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    choices = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert network_lab.INTERACTIVE_ACTION_COMPLETE in output
    assert output.count("Select an option by number") == 2
    assert output.count("  7. Run WireGuard VPN validation") == 2
    assert output.count("  8. Show WireGuard summary command") == 2
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
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    choices = iter(["7", "Set_WireguardVPN_lab02_config.json", "n", "0"])
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
    assert "Select a WireGuard config file for this run" in output
    assert "Set_WireguardVPN_lab02_config.json" in output
    assert "live WireGuard validation workflow" in output
    assert "python mikrotik_day12_wireguard_vpn_automation.py --config Set_WireguardVPN_lab02_config.json --non-interactive" in output
    assert "WireGuard config path or number" in prompts[1]
    assert "Confirm live WireGuard runner execution" in prompts[2]
    assert "WireGuard runner cancelled" in output
    assert "Day12 WireGuard" not in output


def test_interactive_wireguard_runner_blank_config_cancels_without_default(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path)
    choices = iter(["7", "", "0"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))
    monkeypatch.setattr(
        network_lab.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("subprocess.run should not be called")),
    )

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Set_WireguardVPN_config.json" in output
    assert "WireGuard runner cancelled. No config was selected." in output
    assert "Selected WireGuard config: Set_WireguardVPN_config.json" not in output
    assert "Confirm live WireGuard runner execution" not in output


def test_interactive_wireguard_runner_accepts_user_provided_config_path(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    choices = iter(["7", "Set_WireguardVPN_lab02_config.json", "y", "0"])
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fake_run(command, cwd, shell, timeout):
        calls.append((command, cwd, shell, timeout))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Selected WireGuard config: Set_WireguardVPN_lab02_config.json" in output
    assert calls == [
        (
            [
                sys.executable,
                "mikrotik_day12_wireguard_vpn_automation.py",
                "--config",
                "Set_WireguardVPN_lab02_config.json",
                "--non-interactive",
            ],
            tmp_path.resolve(),
            False,
            network_lab.DAY12_WIREGUARD_TIMEOUT_SECONDS,
        )
    ]
    assert "--recreate-peer" not in calls[0][0]
    assert "--apply-firewall-fixes" not in calls[0][0]


def test_interactive_wireguard_runner_accepts_numbered_config_selection(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    write_wireguard_runner_config(tmp_path)
    choices = iter(["7", "1", "y", "0"])
    calls = []
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    def fake_run(command, cwd, shell, timeout):
        calls.append((command, cwd, shell, timeout))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--interactive"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "1. Set_WireguardVPN_lab02_config.json" in output
    assert "2. Set_WireguardVPN_config.json" in output
    assert calls[0][0] == [
        sys.executable,
        "mikrotik_day12_wireguard_vpn_automation.py",
        "--config",
        "Set_WireguardVPN_lab02_config.json",
        "--non-interactive",
    ]


def test_interactive_wireguard_runner_option_with_y_delegates_to_existing_script(
    tmp_path,
    monkeypatch,
    capsys,
):
    write_default_profile(tmp_path)
    write_wireguard_runner_config(tmp_path, filename="Set_WireguardVPN_lab02_config.json")
    choices = iter(["7", "Set_WireguardVPN_lab02_config.json", "y", "0"])
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
                "Set_WireguardVPN_lab02_config.json",
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


def test_day33_vrrp_dry_run_delegates_to_preview_script(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--task", "day33-vrrp-dry-run"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [([sys.executable, "mikrotik_day33_vrrp_topology_dry_run.py"], tmp_path.resolve())]
    assert "no SSH connection or RouterOS execution" in output
    assert "DRY-RUN ONLY and NOT EXECUTED" in output
    assert "--allow-live" not in " ".join(calls[0][0])


def test_day34_vrrp_staged_plan_delegates_to_plan_script(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--task", "day34-vrrp-staged-plan"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert calls == [([sys.executable, "mikrotik_day34_vrrp_staged_apply_plan.py"], tmp_path.resolve())]
    assert "no SSH connection or RouterOS execution" in output
    assert "BLOCKED PLAN ONLY and NOT EXECUTED" in output
    assert "--allow-live" not in " ".join(calls[0][0])


def test_day35_vrrp_failover_delegates_to_validation_script_without_destructive_args(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--task", "day35-vrrp-failover-validation"], project_root=tmp_path)

    output = capsys.readouterr().out
    command_text = " ".join(calls[0][0])
    assert exit_code == 0
    assert calls == [([sys.executable, "mikrotik_day35_vrrp_failover_validation.py"], tmp_path.resolve())]
    assert "Controlled live observation workflow" in output
    assert "disconnect/reconnect lab01 LAN cable" in output
    for blocked in ("disable", "enable", "firewall", "reboot", "reset", "set", "remove"):
        assert blocked not in command_text


def test_day35_vrrp_failover_dry_run_does_not_execute_script(tmp_path, monkeypatch, capsys):
    write_default_profile(tmp_path)

    def fake_run(_command, _cwd):
        raise AssertionError("Day35 dry-run must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fake_run)

    exit_code = network_lab.main(["--task", "day35-vrrp-failover-validation", "--dry-run"], project_root=tmp_path)

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "No live workflow was executed" in output
    assert "ping -S 192.168.88.100 <target>" in output
    assert "Dry-run does not prompt for cable actions, wait, connect to devices, run pings, or write reports." in output


def test_day35_report_paths_are_visible_in_report_catalog():
    day35 = next(item for item in network_lab.REPORT_CATALOG if item["day"] == "Day35")

    assert day35["json_globs"] == ["reports/lab-summary/day35_vrrp_failover_validation.json"]
    assert day35["html_globs"] == ["reports/lab-summary/day35_vrrp_failover_validation.html"]
    assert "day35-vrrp-failover-validation" in day35["missing_note"]
    assert day35["safety_label"] == "controlled_failover_observation"


def test_day39_vrrp_evidence_report_generates_without_live_access(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day39 must not execute live scripts or subprocesses")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "day39-vrrp-evidence-dashboard-integration"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day39 VRRP Evidence Dashboard Integration" in output
    assert "Safety: report-only" in output
    json_path = tmp_path / "reports/lab-summary/day39_vrrp_evidence_dashboard_integration.json"
    html_path = tmp_path / "reports/lab-summary/day39_vrrp_evidence_dashboard_integration.html"
    assert json_path.exists()
    assert html_path.exists()
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["safety_scope"]["live_tests_executed"] is False
    assert report["safety_scope"]["ssh_connections_opened"] is False
    assert report["safety_scope"]["router_configuration_changed"] is False
    assert report["missing_optional_artifacts"]
    assert {entry["status"] for entry in report["evidence"]} >= {"MISSING", "NOT_GENERATED"}


def test_day40_demo_readiness_report_generates_without_live_access(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day40 must not execute live scripts or subprocesses")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "day40-v0.2-demo-readiness-review"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day40_v0.2_demo_readiness_review.json"
    html_path = tmp_path / "reports/portfolio/day40_v0.2_demo_readiness_review.html"
    assert exit_code == 0
    assert "Day40 v0.2 Demo Readiness Review and Scope Lock" in output
    assert "Safety: report-only" in output
    assert json_path.exists()
    assert html_path.exists()
    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == 40
    assert report["task_name"] == "day40-v0.2-demo-readiness-review"
    assert report["task_type"] == "report-only"
    assert report["safety_level"] == "report_only"
    assert report["live_test"] is False
    assert report["ssh_used"] is False
    assert report["device_config_changed"] is False
    assert report["scope_included"]
    assert report["scope_excluded"]
    assert report["day31_to_day39_summary"]
    assert report["demo_checklist"]
    assert report["evidence_traceability"]
    assert report["dashboard_walkthrough"]
    assert report["known_limitations"]
    assert report["next_steps"]
    assert "Day40 v0.2 Demo Readiness Review and Scope Lock" in html
    assert "does not run live tests" in html

    rows = network_lab.discover_report_visibility(tmp_path)
    day40 = next(row for row in rows if row["day"] == "Day40")
    assert day40["status"] == "FOUND"
    assert day40["json"].endswith("day40_v0.2_demo_readiness_review.json")
    assert day40["html"].endswith("day40_v0.2_demo_readiness_review.html")


def test_day41_release_packaging_report_generates_without_live_access(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day41 must not execute live scripts or subprocesses")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    write_text(tmp_path / "docs/releases/v0.2_release_package.md", "# package")
    write_text(tmp_path / "docs/releases/v0.2_artifact_checklist.md", "# checklist")
    write_text(tmp_path / "docs/portfolio/v0.2_demo_handoff_guide.md", "# handoff")

    exit_code = network_lab.main(
        ["--task", "day41-v0.2-release-packaging"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day41_v0.2_release_packaging.json"
    html_path = tmp_path / "reports/portfolio/day41_v0.2_release_packaging.html"
    assert exit_code == 0
    assert "Day41 v0.2 Release Packaging" in output
    assert "Safety: report-only" in output
    assert json_path.exists()
    assert html_path.exists()
    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == 41
    assert report["task_name"] == "day41-v0.2-release-packaging"
    assert report["task_type"] == "report-only"
    assert report["safety_level"] == "report_only"
    assert report["live_test"] is False
    assert report["ssh_used"] is False
    assert report["device_config_changed"] is False
    assert report["v0_2_tag_created"] is False
    assert report["voice_ai_implemented"] is False
    assert report["safety_status"]["live_execution"] is False
    assert report["safety_status"]["ssh_required"] is False
    assert report["safety_status"]["device_config_change"] is False
    assert report["created_or_updated_docs"]
    assert all(item["status"] == "FOUND" for item in report["created_or_updated_docs"])
    assert "Day42" in report["day42_next_action"]
    assert "roadmap-only" in report["v3_0_roadmap_note"]
    assert "Day41 v0.2 Release Packaging" in html
    assert "did not run live tests" in html
    assert "create a v0.2 tag" in html

    rows = network_lab.discover_report_visibility(tmp_path)
    day41 = next(row for row in rows if row["day"] == "Day41")
    assert day41["status"] == "FOUND"
    assert day41["json"].endswith("day41_v0.2_release_packaging.json")
    assert day41["html"].endswith("day41_v0.2_release_packaging.html")


def test_day39_vrrp_evidence_entries_include_status_fields(tmp_path):
    write_text(tmp_path / "docs/roadmap/ha_vrrp_topology_plan.md", "# plan")
    write_json(
        tmp_path / "reports/lab-summary/day32_vrrp_readonly_precheck.json",
        {"overall_status": "PASS"},
    )

    entries = network_lab.discover_vrrp_evidence(tmp_path)

    topology = next(entry for entry in entries if entry["title"] == "HA / VRRP topology plan")
    day32 = next(entry for entry in entries if entry["title"] == "VRRP read-only precheck JSON")
    day35 = next(entry for entry in entries if entry["title"] == "VRRP failover validation JSON")
    assert topology["status"] == "FOUND"
    assert day32["status"] == "FOUND"
    assert day35["status"] == "NOT_GENERATED"
    for entry in entries:
        assert "status" in entry
        assert "safety_level" in entry
        assert "demo_relevance" in entry


def test_report_index_html_exposes_vrrp_evidence_group(tmp_path):
    write_text(tmp_path / "docs/roadmap/ha_vrrp_topology_plan.md", "# plan")

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "HA / VRRP Evidence" in html
    assert "Topology and planning" in html
    assert "docs/roadmap/ha_vrrp_topology_plan.md" in html
    assert "NOT_GENERATED" in html


def test_latest_lab_overview_html_exposes_vrrp_evidence_group(tmp_path):
    prof = profile(required=False)
    write_text(tmp_path / "docs/roadmap/ha_vrrp_topology_plan.md", "# plan")
    overview = network_lab.build_latest_lab_overview(prof, tmp_path)
    output = tmp_path / "reports/lab-summary/latest_lab_overview.html"

    network_lab.write_html_overview(overview, output, tmp_path)

    html = output.read_text(encoding="utf-8")
    assert "HA / VRRP Evidence" in html
    assert "HA / VRRP topology plan" in html
    assert "FOUND" in html


def test_console_status_format_respects_no_color(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    colored = network_lab.format_status("PASS")
    monkeypatch.setenv("NO_COLOR", "1")

    plain = network_lab.format_status("PASS")

    assert "\033[" in colored
    assert plain == "[PASS]"


def test_day57_report_request_maps_to_report_index_without_execution():
    mapping = network_lab.build_day57_intent_mapping("Show me the latest reports")

    assert mapping["detected_intent"] == "view_reports"
    assert mapping["mapped_allowlisted_task"] == "report-index"
    assert mapping["safety_level"] == "report_only"
    assert mapping["execution_mode"] == "dry_run_only"
    assert mapping["mapped_task_executed"] is False
    assert mapping["openai_api_used"] is False
    assert mapping["voice_control_used"] is False
    assert mapping["ssh_used"] is False
    assert mapping["device_connection_used"] is False
    assert mapping["config_json_read"] is False


def test_day57_vrrp_failover_request_is_blocked_dry_run_and_requires_confirmation():
    mapping = network_lab.build_day57_intent_mapping("Do VRRP failover test")

    assert mapping["detected_intent"] == "vrrp_failover_test_request"
    assert "day35-vrrp-failover-validation" in mapping["mapped_allowlisted_task"]
    assert mapping["safety_level"] == "guarded_live_candidate"
    assert mapping["confirmation_requirement"] == "mandatory_before_any_future_live_capable_path"
    assert mapping["day57_result"] == "blocked_in_day57_dry_run_mapping_only"
    assert mapping["human_review_required"] is True
    assert mapping["mapped_task_executed"] is False


def test_day57_unknown_intent_maps_to_manual_review_with_no_task():
    mapping = network_lab.build_day57_intent_mapping("make everything better")

    assert mapping["detected_intent"] == "unknown_or_ambiguous"
    assert mapping["mapped_allowlisted_task"] is None
    assert mapping["safety_level"] == "needs_manual_review"
    assert mapping["confirmation_requirement"] == "manual_review_required"
    assert mapping["human_review_required"] is True
    assert mapping["mapped_task_executed"] is False


def test_day57_intent_mapping_cli_never_executes_mapped_tasks(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day57 intent mapping prototype must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "intent-mapping-prototype", "--intent-text", "Run the WireGuard check"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Day57 AI-assisted Task Intent Mapping Prototype" in output
    assert '"detected_intent": "wireguard_status_or_validation_request"' in output
    assert '"mapped_allowlisted_task": "wireguard-runner"' in output
    assert '"execution_mode": "dry_run_only"' in output
    assert '"mapped_task_executed": false' in output
    assert "No mapped task was executed" in output


def test_day58_intent_safety_review_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "intent-safety-review")

    assert task["task_id"] == "day58_intent_mapping_safety_review_confirmation_gate"
    assert task["day"] == "Day58"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["produces_report"] is True


def test_day58_report_only_intent_is_allowed():
    report = network_lab.build_day58_intent_safety_review("show latest reports")

    assert report["safety_classification"] == "report_only"
    assert report["mapped_task"] == "report-index"
    assert report["confirmation_gate_required"] is False
    assert report["blocked"] is False
    assert report["mapped_task_executed"] is False
    assert report["no_live_execution_occurred"] is True


def test_day58_vrrp_failover_intent_is_live_capable_and_blocked():
    report = network_lab.build_day58_intent_safety_review("do VRRP failover test")

    assert report["action_capability"] == "live_capable"
    assert report["safety_classification"] == "blocked_live_capable"
    assert report["blocked"] is True
    assert report["confirmation_gate_required"] is True
    assert report["blocked_policy_match"] == "VRRP failover execution"
    assert report["mapped_task_executed"] is False


@pytest.mark.parametrize(
    ("intent_text", "blocked_policy"),
    [
        ("change firewall rule", "firewall rule add/remove/change"),
        ("set IP address on router", "IP address change"),
        ("remove route from router", "route change"),
        ("apply device configuration", "direct device configuration apply"),
    ],
)
def test_day58_config_change_intents_are_blocked(intent_text, blocked_policy):
    report = network_lab.build_day58_intent_safety_review(intent_text)

    assert report["safety_classification"] == "blocked_live_capable"
    assert report["blocked"] is True
    assert report["confirmation_gate_required"] is True
    assert report["blocked_policy_match"] == blocked_policy
    assert report["device_configuration_changed"] is False


def test_day58_unknown_intent_is_blocked():
    report = network_lab.build_day58_intent_safety_review("make everything better")

    assert report["safety_classification"] == "unknown_blocked"
    assert report["mapped_task"] is None
    assert report["blocked"] is True
    assert report["confirmation_gate_required"] is True


def test_day58_cli_generates_redacted_report_without_config_or_network_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day58 intent safety review must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(
        ["--task", "intent-safety-review", "--intent-text", "show latest reports password hunter2"],
        project_root=tmp_path,
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day58_intent_mapping_safety_review.json"
    html_path = tmp_path / "reports/portfolio/day58_intent_mapping_safety_review.html"
    assert exit_code == 0
    assert "No live execution occurred" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()
    json_text = json_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    assert "hunter2" not in json_text
    assert "hunter2" not in html_text
    report = json.loads(json_text)
    assert report["final_status"] == "PASS"
    assert report["openai_api_used"] is False
    assert report["ssh_used"] is False
    assert report["device_connection_used"] is False
    assert report["config_json_read"] is False
    assert report["mapped_task_executed"] is False


def test_day59_intent_policy_matrix_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "intent-policy-matrix")

    assert task["task_id"] == "day59_intent_policy_matrix_reviewer_safety_explanation"
    assert task["day"] == "Day59"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["produces_report"] is True
    assert "reports/portfolio/day59_intent_policy_matrix.json" in task["report_paths"]
    assert "reports/portfolio/day59_intent_policy_matrix.html" in task["report_paths"]


def test_day59_policy_matrix_includes_allowed_and_blocked_examples():
    report = network_lab.build_day59_intent_policy_matrix()
    rows = {row["intent_category"]: row for row in report["policy_matrix"]}

    assert report["task_name"] == "intent-policy-matrix"
    assert report["task_type"] == "report-only"
    assert report["safety_level"] == "report_only"
    assert report["mapped_task_executed"] is False
    assert report["openai_api_used"] is False
    assert report["voice_control_used"] is False
    assert report["ssh_used"] is False
    assert report["device_connection_used"] is False
    assert report["config_json_read"] is False

    for category in [
        "Open dashboard / latest reports",
        "Show task catalog",
        "Generate report index",
        "Dry-run intent mapping",
        "Read-only safety review",
    ]:
        assert rows[category]["allowed_to_execute_automatically"] is True
        assert rows[category]["default_decision"].startswith("allowed")

    assert rows["Dry-run intent mapping"]["mapped_task_execution_allowed"] is False

    for category in [
        "VRRP failover request",
        "WireGuard live validation request",
        "SSH command request",
        "Router / switch configuration change request",
        "Unknown or ambiguous request",
    ]:
        assert rows[category]["allowed_to_execute_automatically"] is False
        assert rows[category]["mapped_task_execution_allowed"] is False
        assert rows[category]["requires_confirmation"] is True

    assert rows["VRRP failover request"]["safety_classification"] == "blocked_live_capable"
    assert rows["SSH command request"]["safety_classification"] == "blocked_live_capable"
    assert rows["Router / switch configuration change request"]["safety_classification"] == "blocked_live_capable"
    assert rows["Unknown or ambiguous request"]["safety_classification"] == "unknown_blocked"


def test_day59_cli_generates_report_only_matrix_without_subprocess(tmp_path, monkeypatch, capsys):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day59 intent policy matrix must not execute subprocess")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)

    exit_code = network_lab.main(["--task", "intent-policy-matrix"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day59_intent_policy_matrix.json"
    html_path = tmp_path / "reports/portfolio/day59_intent_policy_matrix.html"
    assert exit_code == 0
    assert "Day59 Intent Policy Matrix" in output
    assert "Safety: report-only" in output
    assert "No mapped task was executed" in output
    assert json_path.exists()
    assert html_path.exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["final_status"] == "PASS"
    assert report["safety_scope"]["mapped_tasks_executed"] is False
    assert report["safety_scope"]["openai_api_used"] is False
    assert report["safety_scope"]["voice_control_used"] is False
    assert report["safety_scope"]["ssh_connections_opened"] is False
    assert report["safety_scope"]["device_connections_opened"] is False
    assert report["safety_scope"]["config_json_read"] is False
    assert "VRRP failover request" in html
    assert "SSH command request" in html
    assert "Router / switch configuration change request" in html
    assert "Dry-run intent mapping" in html


def test_day60_intent_workflow_demo_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "intent-workflow-demo")

    assert task["task_id"] == "day60_ai_intent_workflow_demo_reviewer_walkthrough"
    assert task["day"] == "Day60"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/portfolio/day60_intent_workflow_demo.json" in task["report_paths"]
    assert "reports/portfolio/day60_intent_workflow_demo.html" in task["report_paths"]


def test_day60_workflow_demo_includes_allowed_and_blocked_examples():
    report = network_lab.build_day60_intent_workflow_demo()
    rows = {row["input_intent_text"]: row for row in report["example_intents"]}

    assert report["task_name"] == "intent-workflow-demo"
    assert report["task_type"] == "report-only"
    assert report["safety_level"] == "report_only"
    assert report["final_safety_statement"] == (
        "No mapped task was executed. This is a dry-run reviewer walkthrough only."
    )
    assert report["mapped_task_executed"] is False
    assert report["openai_api_used"] is False
    assert report["voice_control_used"] is False
    assert report["ssh_used"] is False
    assert report["device_connection_used"] is False
    assert report["config_json_read"] is False
    assert report["config_json_required"] is False
    assert report["summary"]["mapped_tasks_executed"] is False

    assert rows["show latest reports"]["expected_classification"] == "report-only"
    assert rows["show latest reports"]["reviewer_decision"] == "allowed"
    assert rows["explain available runner tasks"]["expected_classification"] == "documentation/report-only"
    assert rows["explain available runner tasks"]["reviewer_decision"] == "allowed"

    for intent_text in [
        "do VRRP failover test",
        "change router firewall rule",
        "run WireGuard throughput test",
    ]:
        assert rows[intent_text]["blocked"] is True
        assert rows[intent_text]["mapped_task_executed"] is False

    assert rows["do VRRP failover test"]["expected_classification"] == "live-capable"
    assert rows["change router firewall rule"]["expected_classification"] == "configuration-changing"
    assert rows["run WireGuard throughput test"]["reviewer_decision"] == (
        "blocked unless future guarded-live flow exists"
    )


def test_day60_cli_generates_json_and_html_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day60 intent workflow demo must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day60 intent workflow demo must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "intent-workflow-demo"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day60_intent_workflow_demo.json"
    html_path = tmp_path / "reports/portfolio/day60_intent_workflow_demo.html"
    assert exit_code == 0
    assert "Day60 AI Intent Workflow Demo" in output
    assert "No mapped task was executed. This is a dry-run reviewer walkthrough only." in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["final_status"] == "PASS"
    assert report["safety_scope"]["mapped_tasks_executed"] is False
    assert report["safety_scope"]["openai_api_used"] is False
    assert report["safety_scope"]["voice_control_used"] is False
    assert report["safety_scope"]["ssh_connections_opened"] is False
    assert report["safety_scope"]["device_connections_opened"] is False
    assert report["safety_scope"]["config_json_read"] is False
    assert report["safety_scope"]["config_json_required"] is False
    assert "show latest reports" in html
    assert "do VRRP failover test" in html
    assert "change router firewall rule" in html
    assert "run WireGuard throughput test" in html
    assert "No mapped task was executed. This is a dry-run reviewer walkthrough only." in html


def test_day66_offline_mock_runtime_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "offline-mock-runtime")

    assert task["task_id"] == "day66_offline_mock_runtime_skeleton"
    assert task["day"] == "Day66"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/portfolio/day66_offline_mock_runtime_skeleton.json" in task["report_paths"]
    assert "reports/portfolio/day66_offline_mock_runtime_skeleton.html" in task["report_paths"]
    assert "docs/ai/intent_offline_mock_runtime_skeleton.md" in task["report_paths"]


def test_day66_cli_generates_fixed_mock_report_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day66 offline mock runtime must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day66 offline mock runtime must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "offline-mock-runtime"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day66_offline_mock_runtime_skeleton.json"
    html_path = tmp_path / "reports/portfolio/day66_offline_mock_runtime_skeleton.html"
    assert exit_code == 0
    assert "Day66 Offline Mock Runtime Skeleton" in output
    assert "No live execution, API, voice, SSH, device access, or network change occurred" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["execution_mode"] == "offline_mock"
    assert report["live_execution_allowed"] is False
    assert report["summary"]["mock_scenarios"] >= 4
    assert report["summary"]["blocked_live_action_scenarios"] >= 1
    assert report["no_live_execution_occurred"] is True
    assert report["openai_api_used"] is False
    assert report["voice_integration_used"] is False
    assert report["ssh_used"] is False
    assert report["config_json_read"] is False
    assert report["mapped_task_executed"] is False
    assert "request_vrrp_failover_live_action" in html
    assert "live_execution_allowed" not in html
    assert "Live execution allowed" in html


def test_day67_offline_mock_runtime_contract_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "offline-mock-runtime-contract")

    assert task["task_id"] == "day67_offline_mock_runtime_contract"
    assert task["day"] == "Day67"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/portfolio/day67_offline_mock_runtime_contract.json" in task["report_paths"]
    assert "reports/portfolio/day67_offline_mock_runtime_contract.html" in task["report_paths"]
    assert "docs/ai/intent_offline_mock_runtime_contract.md" in task["report_paths"]


def test_day67_cli_validates_contract_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day67 contract validation must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day67 contract validation must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "offline-mock-runtime-contract"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/portfolio/day67_offline_mock_runtime_contract.json"
    html_path = tmp_path / "reports/portfolio/day67_offline_mock_runtime_contract.html"
    assert exit_code == 0
    assert "Day67 Offline Mock Runtime Contract" in output
    assert "REVIEW_READY" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["validated_scenarios"] >= 4
    assert report["validation_errors"] == []
    assert report["safety_invariants"]["live_execution_allowed_always_false"] is True
    assert report["safety_invariants"]["mapped_task_executed_always_false"] is True
    assert "Day67 Offline Mock Runtime Contract" in html
    assert "No live execution" in html


def test_day68_offline_mock_runtime_review_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "offline-mock-runtime-review")

    assert task["task_id"] == "day68_offline_mock_runtime_reviewer_report_quality"
    assert task["day"] == "Day68"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json" in task["report_paths"]
    assert "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html" in task["report_paths"]
    assert "docs/ai/intent_offline_mock_runtime_reviewer_report_quality.md" in task["report_paths"]


def test_day68_cli_reviews_report_quality_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day68 reviewer quality review must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day68 reviewer quality review must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "offline-mock-runtime-review"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json"
    html_path = tmp_path / "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html"
    assert exit_code == 0
    assert "Day68 Offline Mock Runtime Reviewer Report Quality" in output
    assert "REVIEW_READY" in output
    assert "No live action, mapped task execution" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day68"
    assert report["review_status"] == "REVIEW_READY"
    assert report["scenario_count"] >= 4
    assert report["quality_gate_summary"]["all_scenarios_review_ready"] is True
    assert report["non_execution_evidence"]["no_live_action_executed"] is True
    assert report["non_execution_evidence"]["no_mapped_task_executed"] is True
    assert report["non_execution_evidence"]["no_device_network_configuration_changed"] is True
    assert report["contract_validation_evidence"]["contract_status"] == "PASS"
    assert "No live action" in html
    assert "No mapped task" in html
    assert "Contract Validation Confirmation" in html


def test_day73_mock_ai_decision_pipeline_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "mock-ai-decision-pipeline")

    assert task["task_id"] == "day73_mock_ai_decision_pipeline"
    assert task["day"] == "Day73"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day73_mock_ai_decision_pipeline.json" in task["report_paths"]
    assert "reports/lab-summary/day73_mock_ai_decision_pipeline.html" in task["report_paths"]
    assert "docs/ai/intent_mock_ai_decision_pipeline.md" in task["report_paths"]
    assert "docs/roadmap/day73_mock_ai_decision_pipeline.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "execute mapped tasks" in task["notes"]


def test_day73_cli_generates_mock_decision_report_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day73 mock decision pipeline must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day73 mock decision pipeline must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "mock-ai-decision-pipeline"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day73_mock_ai_decision_pipeline.json"
    html_path = tmp_path / "reports/lab-summary/day73_mock_ai_decision_pipeline.html"
    assert exit_code == 0
    assert "Day73 Mock AI Decision Pipeline" in output
    assert "No AI API, SSH, device access, live execution, mapped task execution" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day73"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["scenario_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(record["allowed_to_execute"] is False for record in report["decision_records"])
    assert "BLOCKED_LIVE_ACTION" in html
    assert "INVALID_INPUT_BLOCKED" in html
    assert "Allowed to execute?" in html


def test_day74_dry_run_plan_builder_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "dry-run-plan-builder")

    assert task["task_id"] == "day74_dry_run_plan_builder"
    assert task["day"] == "Day74"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day74_dry_run_plan_builder.json" in task["report_paths"]
    assert "reports/lab-summary/day74_dry_run_plan_builder.html" in task["report_paths"]
    assert "docs/ai/intent_dry_run_plan_builder.md" in task["report_paths"]
    assert "docs/roadmap/day74_dry_run_plan_builder.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "execute mapped tasks" in task["notes"]


def test_day74_cli_generates_dry_run_plan_report_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day74 dry-run plan builder must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day74 dry-run plan builder must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "dry-run-plan-builder"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day74_dry_run_plan_builder.json"
    html_path = tmp_path / "reports/lab-summary/day74_dry_run_plan_builder.html"
    assert exit_code == 0
    assert "Day74 Controlled Dry-run Plan Builder" in output
    assert "No AI API, SSH, device access, live execution, mapped task execution" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day74"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["plan_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(plan["allowed_to_execute"] is False for plan in report["dry_run_plans"])
    assert all(plan["dry_run_only"] is True for plan in report["dry_run_plans"])
    assert "DRY_RUN_READY" in html
    assert "INVALID_INPUT_BLOCKED" in html
    assert "Dry-run only?" in html


def test_day75_manual_review_approval_envelope_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "manual-review-approval-envelope"
    )

    assert task["task_id"] == "day75_manual_review_approval_envelope"
    assert task["day"] == "Day75"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day75_manual_review_approval_envelope.json" in task["report_paths"]
    assert "reports/lab-summary/day75_manual_review_approval_envelope.html" in task["report_paths"]
    assert "docs/ai/intent_manual_review_approval_envelope.md" in task["report_paths"]
    assert "docs/roadmap/day75_manual_review_approval_envelope.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "approval unlocks" in task["notes"]


def test_day75_cli_generates_approval_envelope_report_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day75 approval envelope must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day75 approval envelope must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "manual-review-approval-envelope"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day75_manual_review_approval_envelope.json"
    html_path = tmp_path / "reports/lab-summary/day75_manual_review_approval_envelope.html"
    assert exit_code == 0
    assert "Day75 Manual Review Approval Envelope" in output
    assert "PASS" in output
    assert "REVIEW_READY" in output
    assert "Approval envelopes: 5" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day75"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["approval_envelope_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["approval_states_do_not_unlock_execution"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(item["allowed_to_execute"] is False for item in report["approval_envelopes"])
    assert all(item["dry_run_only"] is True for item in report["approval_envelopes"])
    assert all(
        item["execution_unlock_supported"] is False for item in report["approval_envelopes"]
    )
    assert "approved_for_record_only" in html
    assert "blocked_live_action" in html
    assert "Execution unlock supported?" in html


def test_day76_runtime_audit_trail_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "runtime-audit-trail")

    assert task["task_id"] == "day76_runtime_audit_trail"
    assert task["day"] == "Day76"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day76_runtime_audit_trail.json" in task["report_paths"]
    assert "reports/lab-summary/day76_runtime_audit_trail.html" in task["report_paths"]
    assert "docs/ai/intent_runtime_audit_trail.md" in task["report_paths"]
    assert "docs/roadmap/day76_runtime_audit_trail.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "execution unlocks" in task["notes"]


def test_day76_cli_generates_runtime_audit_trail_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day76 runtime audit trail must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day76 runtime audit trail must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "runtime-audit-trail"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day76_runtime_audit_trail.json"
    html_path = tmp_path / "reports/lab-summary/day76_runtime_audit_trail.html"
    assert exit_code == 0
    assert "Day76 Controlled Runtime Audit Trail" in output
    assert "PASS" in output
    assert "REVIEW_READY" in output
    assert "Audit records: 5" in output
    assert "Evidence chain complete values: [True]" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day76"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["audit_record_count"] == 5
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["audit_results_do_not_unlock_execution"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(item["evidence_chain_complete"] is True for item in report["audit_records"])
    assert all(item["allowed_to_execute"] is False for item in report["audit_records"])
    assert all(item["dry_run_only"] is True for item in report["audit_records"])
    assert all(
        item["execution_unlock_supported"] is False for item in report["audit_records"]
    )
    assert "Day76 Controlled Runtime Audit Trail" in html
    assert "Evidence chain complete?" in html
    assert "Execution unlock supported?" in html


def test_day77_runtime_safety_gate_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "runtime-safety-gate")

    assert task["task_id"] == "day77_runtime_safety_gate"
    assert task["day"] == "Day77"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day77_runtime_safety_gate.json" in task["report_paths"]
    assert "reports/lab-summary/day77_runtime_safety_gate.html" in task["report_paths"]
    assert "docs/ai/intent_runtime_safety_gate.md" in task["report_paths"]
    assert "docs/roadmap/day77_runtime_safety_gate.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "execution unlocks" in task["notes"]


def test_day77_cli_generates_runtime_safety_gate_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day77 runtime safety gate must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day77 runtime safety gate must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "runtime-safety-gate"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day77_runtime_safety_gate.json"
    html_path = tmp_path / "reports/lab-summary/day77_runtime_safety_gate.html"
    assert exit_code == 0
    assert "Day77 Runtime Safety Gate" in output
    assert "Safety: deterministic mock-only / no-execution enforcement report" in output
    assert "PASS" in output
    assert "REVIEW_READY" in output
    assert "Gate records: 5" in output
    assert "Runtime gate state values: ['LOCKED']" in output
    assert "Evidence chain complete values: [True]" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day77"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["gate_record_count"] == 5
    assert report["summary"]["runtime_gate_state_values"] == ["LOCKED"]
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["runtime_gate_state_locked_all_records"] is True
    assert report["safety_invariants"]["gate_results_do_not_unlock_execution"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(item["evidence_chain_complete"] is True for item in report["safety_gate_records"])
    assert all(item["runtime_gate_state"] == "LOCKED" for item in report["safety_gate_records"])
    assert all(item["allowed_to_execute"] is False for item in report["safety_gate_records"])
    assert all(item["dry_run_only"] is True for item in report["safety_gate_records"])
    assert all(
        item["execution_unlock_supported"] is False for item in report["safety_gate_records"]
    )
    assert "Day77 Runtime Safety Gate" in html
    assert "Runtime gate state" in html
    assert "Execution unlock supported?" in html


def test_day78_runtime_safety_case_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "runtime-safety-case")

    assert task["task_id"] == "day78_runtime_safety_case"
    assert task["day"] == "Day78"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day78_runtime_safety_case.json" in task["report_paths"]
    assert "reports/lab-summary/day78_runtime_safety_case.html" in task["report_paths"]
    assert "docs/ai/intent_runtime_safety_case.md" in task["report_paths"]
    assert "docs/roadmap/day78_runtime_safety_case.md" in task["report_paths"]
    assert "does not call APIs" in task["notes"]
    assert "execution unlocks" in task["notes"]


def test_day78_cli_generates_runtime_safety_case_without_config_or_device_access(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day78 runtime safety case must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day78 runtime safety case must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "runtime-safety-case"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day78_runtime_safety_case.json"
    html_path = tmp_path / "reports/lab-summary/day78_runtime_safety_case.html"
    assert exit_code == 0
    assert "Day78 Controlled Runtime Safety Case" in output
    assert "Safety: deterministic mock-only / end-to-end reviewer package" in output
    assert "PASS" in output
    assert "REVIEW_READY" in output
    assert "Safety case records: 5" in output
    assert "Runtime gate state values: ['LOCKED']" in output
    assert "Evidence chain complete values: [True]" in output
    assert "Final recommendation values: ['REVIEW_ONLY']" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day78"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["safety_case_record_count"] == 5
    assert report["summary"]["runtime_gate_state_values"] == ["LOCKED"]
    assert report["summary"]["evidence_chain_complete_values"] == [True]
    assert report["summary"]["final_recommendation_values"] == ["REVIEW_ONLY"]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["runtime_gate_state_locked_all_records"] is True
    assert report["safety_invariants"]["final_recommendation_review_only_all_records"] is True
    assert report["safety_invariants"]["safety_case_results_do_not_unlock_execution"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(item["evidence_chain_complete"] is True for item in report["safety_case_records"])
    assert all(item["runtime_gate_state"] == "LOCKED" for item in report["safety_case_records"])
    assert all(
        item["final_recommendation"] == "REVIEW_ONLY"
        for item in report["safety_case_records"]
    )
    assert all(item["allowed_to_execute"] is False for item in report["safety_case_records"])
    assert all(item["dry_run_only"] is True for item in report["safety_case_records"])
    assert all(
        item["execution_unlock_supported"] is False
        for item in report["safety_case_records"]
    )
    assert "Day78 Controlled Runtime Safety Case" in html
    assert "Final recommendation" in html
    assert "Execution unlock supported?" in html


def test_day79_readonly_task_contract_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "readonly-task-contract")

    assert task["task_id"] == "day79_readonly_task_contract"
    assert task["day"] == "Day79"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day79_readonly_task_contract.json" in task["report_paths"]
    assert "reports/lab-summary/day79_readonly_task_contract.html" in task["report_paths"]
    assert "docs/ai/intent_readonly_task_contract.md" in task["report_paths"]
    assert "docs/roadmap/day79_readonly_task_contract.md" in task["report_paths"]
    assert "read-only candidates" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day79_readonly_task_contract_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day79 read-only task contract must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day79 read-only task contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "readonly-task-contract"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day79_readonly_task_contract.json"
    html_path = tmp_path / "reports/lab-summary/day79_readonly_task_contract.html"
    assert exit_code == 0
    assert "Day79 Controlled Read-only Task Contract & Allowlist" in output
    assert "Safety: deterministic mock-only / dry-run-only task eligibility contract" in output
    assert "Overall status: PASS / REVIEW_READY" in output
    assert "Contract records: 5" in output
    assert "Read-only eligible values: [False, True]" in output
    assert "Execution candidate values: [False, True]" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert "JSON report: reports/lab-summary/day79_readonly_task_contract.json" in output
    assert "HTML report: reports/lab-summary/day79_readonly_task_contract.html" in output
    assert "[PASS] REVIEW_READY. Read-only task contract is defined" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day79"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["contract_record_count"] == 5
    assert report["summary"]["readonly_eligible_values"] == [False, True]
    assert report["summary"]["execution_candidate_values"] == [False, True]
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["openai_api_used"] is False
    assert report["safety_invariants"]["ssh_used"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert report["safety_invariants"]["config_json_read"] is False
    assert all(item["allowed_to_execute"] is False for item in report["contract_records"])
    assert all(item["dry_run_only"] is True for item in report["contract_records"])
    assert all(
        item["execution_unlock_supported"] is False
        for item in report["contract_records"]
    )
    assert any(
        item["readonly_eligible"] is True and item["execution_candidate"] is True
        for item in report["contract_records"]
    )
    assert "Day79 Controlled Read-only Task Contract" in html
    assert "READONLY_CONTRACT_READY" in html
    assert "Execution unlock supported values" in html


def test_day80_readonly_execution_broker_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "readonly-execution-broker")

    assert task["task_id"] == "day80_readonly_execution_broker"
    assert task["day"] == "Day80"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day80_readonly_execution_broker.json" in task["report_paths"]
    assert "reports/lab-summary/day80_readonly_execution_broker.html" in task["report_paths"]
    assert "docs/ai/intent_readonly_execution_broker.md" in task["report_paths"]
    assert "docs/roadmap/day80_readonly_execution_broker_skeleton.md" in task["report_paths"]
    assert "Day79 read-only task contract" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day80_readonly_execution_broker_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day80 read-only execution broker must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day80 read-only execution broker must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "readonly-execution-broker"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day80_readonly_execution_broker.json"
    html_path = tmp_path / "reports/lab-summary/day80_readonly_execution_broker.html"
    assert exit_code == 0
    assert "Day80 Read-only Execution Broker Skeleton" in output
    assert "Safety: deterministic mock-only / dry-run-only broker skeleton" in output
    assert "Overall status: PASS / REVIEW_READY" in output
    assert "Broker records: 5" in output
    assert "Broker statuses:" in output
    assert "MOCK_EXECUTION_REQUEST_PREPARED" in output
    assert "QUEUED_FOR_REVIEW" in output
    assert "REJECTED" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert "Device connection allowed values: [False]" in output
    assert "SSH allowed values: [False]" in output
    assert "Live command allowed values: [False]" in output
    assert "JSON report: reports/lab-summary/day80_readonly_execution_broker.json" in output
    assert "HTML report: reports/lab-summary/day80_readonly_execution_broker.html" in output
    assert "[PASS] REVIEW_READY. Read-only broker skeleton is defined" in output
    assert "no live command was executed" in output
    assert "no mapped task was executed" in output
    assert "no device was accessed" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day80"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["broker_record_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["summary"]["device_connection_allowed_values"] == [False]
    assert report["summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["live_command_allowed_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["device_connection_allowed_always_false"] is True
    assert report["safety_invariants"]["ssh_allowed_always_false"] is True
    assert report["safety_invariants"]["live_command_allowed_always_false"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert all(item["allowed_to_execute"] is False for item in report["broker_records"])
    assert all(item["dry_run_only"] is True for item in report["broker_records"])
    assert all(
        item["execution_unlock_supported"] is False
        for item in report["broker_records"]
    )
    assert all(item["ssh_allowed"] is False for item in report["broker_records"])
    assert all(item["live_command_allowed"] is False for item in report["broker_records"])
    assert any(
        item["broker_status"] == "MOCK_EXECUTION_REQUEST_PREPARED"
        and isinstance(item["mock_execution_request"], dict)
        for item in report["broker_records"]
    )
    assert "Day80 Read-only Execution Broker Skeleton" in html
    assert "MOCK_EXECUTION_REQUEST_PREPARED" in html
    assert "Live command allowed values" in html


def test_day81_broker_review_queue_task_exists_in_catalog():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "broker-review-queue")

    assert task["task_id"] == "day81_broker_review_queue"
    assert task["day"] == "Day81"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day81_broker_review_queue.json" in task["report_paths"]
    assert "reports/lab-summary/day81_broker_review_queue.html" in task["report_paths"]
    assert "docs/ai/intent_broker_review_queue.md" in task["report_paths"]
    assert "docs/roadmap/day81_broker_review_queue.md" in task["report_paths"]
    assert "Day80 broker records" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day81_broker_review_queue_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day81 broker review queue must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day81 broker review queue must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(["--task", "broker-review-queue"], project_root=tmp_path)

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day81_broker_review_queue.json"
    html_path = tmp_path / "reports/lab-summary/day81_broker_review_queue.html"
    assert exit_code == 0
    assert "Day81 Read-only Broker Review Queue & Decision State Report" in output
    assert "Task name: broker-review-queue" in output
    assert "Result: PASS / REVIEW_READY" in output
    assert "Queue records count: 5" in output
    assert "Review states list:" in output
    assert "REJECTED_BY_BROKER" in output
    assert "QUEUED_FOR_HUMAN_REVIEW" in output
    assert "MOCK_EXECUTION_REQUEST_PREPARED" in output
    assert "REVIEW_BLOCKED_BY_POLICY" in output
    assert "REVIEW_READY_NO_EXECUTION" in output
    assert "Decision states list:" in output
    assert "HOLD_FOR_REVIEW" in output
    assert "MOCK_ONLY" in output
    assert "POLICY_BLOCKED" in output
    assert "REVIEW_ONLY" in output
    assert "Allowed to execute values: [False]" in output
    assert "Dry-run-only values: [True]" in output
    assert "Execution unlock supported values: [False]" in output
    assert "Device connection allowed values: [False]" in output
    assert "SSH allowed values: [False]" in output
    assert "Live command allowed values: [False]" in output
    assert "Mapped task execution allowed values: [False]" in output
    assert "Dashboard action allowed values: [False]" in output
    assert "JSON report: reports/lab-summary/day81_broker_review_queue.json" in output
    assert "HTML report: reports/lab-summary/day81_broker_review_queue.html" in output
    assert "[PASS] REVIEW_READY. Broker review queue is report-only" in output
    assert "no request is allowed to execute" in output
    assert "no mapped task was executed" in output
    assert "no dashboard action endpoint was added" in output
    assert "approve execution" not in output.lower()
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day81"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["summary"]["queue_record_count"] == 5
    assert report["summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["dry_run_only_values"] == [True]
    assert report["summary"]["execution_unlock_supported_values"] == [False]
    assert report["summary"]["device_connection_allowed_values"] == [False]
    assert report["summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["live_command_allowed_values"] == [False]
    assert report["summary"]["mapped_task_execution_allowed_values"] == [False]
    assert report["summary"]["dashboard_action_allowed_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute_always_false"] is True
    assert report["safety_invariants"]["dry_run_only_always_true"] is True
    assert report["safety_invariants"]["execution_unlock_supported_always_false"] is True
    assert report["safety_invariants"]["device_connection_allowed_always_false"] is True
    assert report["safety_invariants"]["ssh_allowed_always_false"] is True
    assert report["safety_invariants"]["live_command_allowed_always_false"] is True
    assert report["safety_invariants"]["mapped_task_execution_allowed_always_false"] is True
    assert report["safety_invariants"]["dashboard_action_allowed_always_false"] is True
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["safety_invariants"]["device_access_used"] is False
    assert all(item["allowed_to_execute"] is False for item in report["queue_records"])
    assert all(item["dry_run_only"] is True for item in report["queue_records"])
    assert all(item["execution_unlock_supported"] is False for item in report["queue_records"])
    assert all(item["ssh_allowed"] is False for item in report["queue_records"])
    assert all(item["live_command_allowed"] is False for item in report["queue_records"])
    assert all(item["mapped_task_execution_allowed"] is False for item in report["queue_records"])
    assert all(item["dashboard_action_allowed"] is False for item in report["queue_records"])
    assert "Day81 Read-only Broker Review Queue" in html
    assert "REVIEW_BLOCKED_BY_POLICY" in html
    assert "Dashboard action allowed values" in html


def test_day81_broker_review_queue_decision_state_alias_works(tmp_path):
    exit_code = network_lab.main(["--task", "broker-review-queue-decision-state"], project_root=tmp_path)

    assert exit_code == 0
    assert (tmp_path / "reports/lab-summary/day81_broker_review_queue.json").exists()
    assert (tmp_path / "reports/lab-summary/day81_broker_review_queue.html").exists()


def test_day82_reviewer_decision_audit_summary_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "reviewer-decision-audit-summary"
    )

    assert task["task_id"] == "day82_reviewer_decision_audit_summary"
    assert task["day"] == "Day82"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day82_reviewer_decision_audit_summary.json" in task["report_paths"]
    assert "reports/lab-summary/day82_reviewer_decision_audit_summary.html" in task["report_paths"]
    assert "docs/ai/intent_reviewer_decision_audit_summary.md" in task["report_paths"]
    assert "docs/roadmap/day82_reviewer_decision_audit_summary.md" in task["report_paths"]
    assert "Day81 queue evidence" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day82_reviewer_decision_audit_summary_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day82 reviewer decision audit summary must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day82 reviewer decision audit summary must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "reviewer-decision-audit-summary"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day82_reviewer_decision_audit_summary.json"
    html_path = tmp_path / "reports/lab-summary/day82_reviewer_decision_audit_summary.html"
    assert exit_code == 0
    assert "Day82 Reviewer Decision Audit Summary / Queue Evidence Export" in output
    assert "Task name: reviewer-decision-audit-summary" in output
    assert "Result: PASS / REVIEW_READY" in output
    assert "Queue records summarized: 5" in output
    assert "Evidence exports count: 5" in output
    assert "allowed_to_execute: [False]" in output
    assert "dry_run_only: [True]" in output
    assert "execution_unlock_supported: [False]" in output
    assert "device_connection_allowed: [False]" in output
    assert "ssh_allowed: [False]" in output
    assert "live_command_allowed: [False]" in output
    assert "network_change_allowed: [False]" in output
    assert "ai_runtime_allowed: [False]" in output
    assert "dashboard_action_allowed: [False]" in output
    assert "JSON report: reports/lab-summary/day82_reviewer_decision_audit_summary.json" in output
    assert "HTML report: reports/lab-summary/day82_reviewer_decision_audit_summary.html" in output
    assert "[PASS] REVIEW_READY. Reviewer decision audit summary is review-only" in output
    assert "no live execution" in output
    assert "no dashboard action endpoint was added" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day82"
    assert report["status"] == "REVIEW_READY"
    assert report["overall_status"] == "PASS"
    assert report["decision_summary"]["queue_record_count"] == 5
    assert report["decision_summary"]["evidence_export_count"] == 5
    assert report["decision_summary"]["allowed_to_execute_values"] == [False]
    assert report["decision_summary"]["dry_run_only_values"] == [True]
    assert report["decision_summary"]["execution_unlock_supported_values"] == [False]
    assert report["decision_summary"]["device_connection_allowed_values"] == [False]
    assert report["decision_summary"]["ssh_allowed_values"] == [False]
    assert report["decision_summary"]["live_command_allowed_values"] == [False]
    assert report["decision_summary"]["network_change_allowed_values"] == [False]
    assert report["decision_summary"]["ai_runtime_allowed_values"] == [False]
    assert report["decision_summary"]["dashboard_action_allowed_values"] == [False]
    assert report["safety_invariants"]["allowed_to_execute"] is False
    assert report["safety_invariants"]["dry_run_only"] is True
    assert report["safety_invariants"]["execution_unlock_supported"] is False
    assert report["safety_invariants"]["device_connection_allowed"] is False
    assert report["safety_invariants"]["ssh_allowed"] is False
    assert report["safety_invariants"]["live_command_allowed"] is False
    assert report["safety_invariants"]["network_change_allowed"] is False
    assert report["safety_invariants"]["ai_runtime_allowed"] is False
    assert report["safety_invariants"]["dashboard_action_allowed"] is False
    assert all(item["allowed_to_execute"] is False for item in report["evidence_exports"])
    assert all(item["dry_run_only"] is True for item in report["evidence_exports"])
    assert all(item["execution_unlock_supported"] is False for item in report["evidence_exports"])
    traceability_text = json.dumps(report["traceability_map"], sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82"):
        assert day in traceability_text
    assert "Reviewer Decision Audit Summary / Queue Evidence Export" in html
    assert "AI runtime allowed values" in html


def test_day83_readonly_executor_readiness_gate_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "readonly-executor-readiness-gate"
    )

    assert task["task_id"] == "day83_readonly_executor_readiness_gate"
    assert task["day"] == "Day83"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day83_readonly_executor_readiness_gate.json" in task["report_paths"]
    assert "reports/lab-summary/day83_readonly_executor_readiness_gate.html" in task["report_paths"]
    assert "docs/ai/readonly_executor_readiness_gate.md" in task["report_paths"]
    assert "docs/roadmap/day83_readonly_executor_readiness_gate.md" in task["report_paths"]
    assert "future adapter design candidacy only" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day83_readonly_executor_readiness_gate_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day83 read-only executor readiness gate must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day83 read-only executor readiness gate must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "readonly-executor-readiness-gate"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day83_readonly_executor_readiness_gate.json"
    html_path = tmp_path / "reports/lab-summary/day83_readonly_executor_readiness_gate.html"
    assert exit_code == 0
    assert "Day83 Read-only Executor Readiness Gate / Controlled Runner Preflight" in output
    assert "Task name: readonly-executor-readiness-gate" in output
    assert "Result: PASS / READINESS_REVIEW_READY" in output
    assert "Readiness checks: 7 / 7" in output
    assert "Day79 contract records: 5" in output
    assert "Day80 broker records: 5" in output
    assert "Day81 queue records: 5" in output
    assert "Day82 evidence exports: 5" in output
    assert "Executor allowed: false" in output
    assert "Read-only executor candidate: true" in output
    assert "Live execution allowed: false" in output
    assert "SSH allowed: false" in output
    assert "Device access allowed: false" in output
    assert "AI runtime allowed: false" in output
    assert "Dashboard action allowed: false" in output
    assert "Mapped task execution allowed: false" in output
    assert "Approval unlock allowed: false" in output
    assert "Execution unlock supported: false" in output
    assert "JSON report: reports/lab-summary/day83_readonly_executor_readiness_gate.json" in output
    assert "HTML report: reports/lab-summary/day83_readonly_executor_readiness_gate.html" in output
    assert "[PASS] READINESS_REVIEW_READY. Read-only executor candidate status is review-only" in output
    assert "no executor" in output
    assert "approval unlock" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day83"
    assert report["overall_status"] == "PASS"
    assert report["readiness_state"] == "READINESS_REVIEW_READY"
    assert report["executor_allowed"] is False
    assert report["readonly_executor_candidate"] is True
    assert report["live_execution_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["device_access_allowed"] is False
    assert report["ai_runtime_allowed"] is False
    assert report["dashboard_action_allowed"] is False
    assert report["mapped_task_execution_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_unlock_supported"] is False
    assert report["candidate_scope"]["candidate_means_execution_allowed"] is False
    assert report["summary"]["source_days"] == ["Day79", "Day80", "Day81", "Day82"]
    assert {check["status"] for check in report["readiness_checks"]} == {"PASS"}
    assert "Day83 Read-only Executor Readiness Gate" in html
    assert "Executor allowed" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()


def test_day84_readonly_executor_adapter_contract_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "readonly-executor-adapter-contract"
    )

    assert task["task_id"] == "day84_readonly_executor_adapter_contract"
    assert task["day"] == "Day84"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day84_readonly_executor_adapter_contract.json" in task["report_paths"]
    assert "reports/lab-summary/day84_readonly_executor_adapter_contract.html" in task["report_paths"]
    assert "docs/ai/intent_readonly_executor_adapter_contract.md" in task["report_paths"]
    assert "docs/roadmap/day84_readonly_executor_adapter_interface_contract.md" in task["report_paths"]
    assert "contract-only adapter boundary" in task["notes"]
    assert "not an executor or adapter implementation" in task["notes"]
    assert "does not call APIs" in task["notes"]


def test_day84_readonly_executor_adapter_contract_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day84 read-only executor adapter contract must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day84 read-only executor adapter contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "readonly-executor-adapter-contract"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day84_readonly_executor_adapter_contract.json"
    html_path = tmp_path / "reports/lab-summary/day84_readonly_executor_adapter_contract.html"
    assert exit_code == 0
    assert "Day84 Read-only Executor Adapter Interface Contract" in output
    assert "Task name: readonly-executor-adapter-contract" in output
    assert "Result: PASS / REVIEW_READY" in output
    assert "Contract state: LOCKED_REVIEW_ONLY_CONTRACT" in output
    assert "Request shapes: 1" in output
    assert "Response shapes: 1" in output
    assert "Capability declarations: 1" in output
    assert "Evidence references: 1" in output
    assert "Read-only only: true" in output
    assert "Dry-run only: true" in output
    assert "Allowed to execute: false" in output
    assert "SSH allowed: false" in output
    assert "Device access allowed: false" in output
    assert "Live command allowed: false" in output
    assert "Approval unlock supported: false" in output
    assert "Execution unlock supported: false" in output
    assert "AI API allowed: false" in output
    assert "Adapter implementation present: false" in output
    assert "JSON report: reports/lab-summary/day84_readonly_executor_adapter_contract.json" in output
    assert "HTML report: reports/lab-summary/day84_readonly_executor_adapter_contract.html" in output
    assert "[PASS] REVIEW_READY. Read-only executor adapter contract is locked as review-only" in output
    assert "no executor implementation" in output
    assert "approval unlock" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day84"
    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "REVIEW_READY"
    assert report["contract_state"] == "LOCKED_REVIEW_ONLY_CONTRACT"
    assert report["adapter_boundary"]["boundary_type"] == "contract_only_boundary"
    assert report["adapter_boundary"]["implements_executor"] is False
    assert report["adapter_boundary"]["implements_adapter"] is False
    assert report["adapter_safety_flags"]["read_only_only"] is True
    assert report["adapter_safety_flags"]["dry_run_only"] is True
    assert report["adapter_safety_flags"]["allowed_to_execute"] is False
    assert report["adapter_safety_flags"]["ssh_allowed"] is False
    assert report["adapter_safety_flags"]["device_access_allowed"] is False
    assert report["adapter_safety_flags"]["live_command_allowed"] is False
    assert report["adapter_safety_flags"]["approval_unlock_supported"] is False
    assert report["adapter_safety_flags"]["execution_unlock_supported"] is False
    assert report["adapter_safety_flags"]["ai_api_allowed"] is False
    assert report["adapter_safety_flags"]["adapter_implementation_present"] is False
    assert report["adapter_capability_declaration_shape"]["supported_transports"] == ["none_contract_only"]
    assert report["adapter_capability_declaration_shape"]["runnable_entrypoint"] is None
    assert report["adapter_capability_declaration_shape"]["implementation_module"] is None
    assert report["adapter_response_shape"]["execution_result"] is None
    assert report["adapter_response_shape"]["commands_executed"] == []
    assert "Day84 Read-only Executor Adapter Interface Contract" in html
    assert "Adapter implementation present values" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day85_mock_adapter_evidence_binding_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "mock-adapter-evidence-binding"
    )

    assert task["task_id"] == "day85_mock_adapter_evidence_binding"
    assert task["day"] == "Day85"
    assert task["display_name"] == "Day85 Mock Adapter + Evidence Binding"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day85_mock_adapter_evidence_binding.json" in task["report_paths"]
    assert "reports/lab-summary/day85_mock_adapter_evidence_binding.html" in task["report_paths"]
    assert "docs/ai/intent_mock_adapter_evidence_binding.md" in task["report_paths"]
    assert "docs/roadmap/day85_mock_adapter_evidence_binding.md" in task["report_paths"]
    assert "Mock Adapter + Evidence Binding" in task["display_name"]
    assert "Compatibility Matrix as internal validation only" in task["notes"]
    assert "not a standalone topic" in task["notes"]


def test_day85_mock_adapter_evidence_binding_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day85 mock adapter evidence binding must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day85 mock adapter evidence binding must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "mock-adapter-evidence-binding"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day85_mock_adapter_evidence_binding.json"
    html_path = tmp_path / "reports/lab-summary/day85_mock_adapter_evidence_binding.html"
    assert exit_code == 0
    assert "Day85 Mock Adapter + Evidence Binding" in output
    assert "Task name: mock-adapter-evidence-binding" in output
    assert "Result: PASS / REVIEW_READY" in output
    assert "Final recommendation: REVIEW_ONLY" in output
    assert "Adapter records: 7" in output
    assert "Evidence bindings: 7" in output
    assert "Compatible adapters: 3" in output
    assert "Blocked adapters: 4" in output
    assert "Compatibility Matrix: internal Day85/Day86 validation only" in output
    assert "Allowed to execute: false" in output
    assert "SSH allowed: false" in output
    assert "Device access allowed: false" in output
    assert "Live command allowed: false" in output
    assert "Approval unlock supported: false" in output
    assert "Execution unlock supported: false" in output
    assert "AI API allowed: false" in output
    assert "JSON report: reports/lab-summary/day85_mock_adapter_evidence_binding.json" in output
    assert "HTML report: reports/lab-summary/day85_mock_adapter_evidence_binding.html" in output
    assert "[PASS] REVIEW_READY. Mock adapter evidence binding is review-only" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day85"
    assert report["title"] == "Day85 Mock Adapter + Evidence Binding"
    assert report["overall_status"] == "PASS"
    assert report["review_status"] == "REVIEW_READY"
    assert report["final_recommendation"] == "REVIEW_ONLY"
    assert report["traceability_summary"]["adapter_record_count"] == 7
    assert report["traceability_summary"]["compatible_adapter_count"] == 3
    assert report["traceability_summary"]["blocked_adapter_count"] == 4
    assert report["safety_invariants"]["compatibility_matrix_is_internal_validation"] is True
    assert report["safety_invariants"]["compatibility_matrix_is_standalone_topic"] is False
    assert report["safety_invariants"]["allowed_to_execute"] is False
    assert report["safety_invariants"]["ssh_allowed"] is False
    assert report["safety_invariants"]["device_access_allowed"] is False
    assert report["safety_invariants"]["live_command_allowed"] is False
    assert report["safety_invariants"]["approval_unlock_supported"] is False
    assert report["safety_invariants"]["execution_unlock_supported"] is False
    assert report["safety_invariants"]["ai_api_allowed"] is False
    assert "Day85 Mock Adapter + Evidence Binding" in html
    assert "Compatibility Matrix Internal Validation" in html
    assert "not a standalone Day85 topic" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day86_controlled_runner_harness_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "controlled-runner-harness"
    )

    assert task["task_id"] == "day86_controlled_runner_harness"
    assert task["day"] == "Day86"
    assert task["display_name"] == "Day86 Controlled Runner Harness + Safety Regression"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day86_controlled_runner_harness.json" in task["report_paths"]
    assert "reports/lab-summary/day86_controlled_runner_harness.html" in task["report_paths"]
    assert "docs/ai/intent_controlled_runner_harness.md" in task["report_paths"]
    assert "docs/roadmap/day86_controlled_runner_harness_safety_regression.md" in task["report_paths"]
    assert "runner-level safety regression" in task["notes"]
    assert "mapped_task_executed remains false" in task["notes"]
    assert "does not add adapter functionality" in task["notes"]


def test_day86_controlled_runner_harness_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day86 controlled runner harness must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day86 controlled runner harness must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "controlled-runner-harness"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day86_controlled_runner_harness.json"
    html_path = tmp_path / "reports/lab-summary/day86_controlled_runner_harness.html"
    assert exit_code == 0
    assert "Day86 Controlled Runner Harness + Safety Regression" in output
    assert "Task name: controlled-runner-harness" in output
    assert "Result: PASS / REVIEW_ONLY" in output
    assert "Runner mode: CONTROLLED_HARNESS" in output
    assert "Final recommendation: REVIEW_ONLY" in output
    assert "Total scenarios: 6" in output
    assert "Failed scenarios: 0" in output
    assert "allowed_to_execute=false" in output
    assert "ssh_allowed=false" in output
    assert "live_command_allowed=false" in output
    assert "mapped_task_executed=false" in output
    assert "Execution unlock supported: false" in output
    assert "JSON report: reports/lab-summary/day86_controlled_runner_harness.json" in output
    assert "HTML report: reports/lab-summary/day86_controlled_runner_harness.html" in output
    assert "[PASS] REVIEW_ONLY. Controlled runner harness is dry-run-only" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == "Day86"
    assert report["phase"] == "Day86"
    assert report["overall_status"] == "PASS"
    assert report["runner_mode"] == "CONTROLLED_HARNESS"
    assert report["final_recommendation"] == "REVIEW_ONLY"
    assert report["execution_unlock_supported"] is False
    assert report["summary"]["total_scenarios"] == 6
    assert report["summary"]["failed_scenarios"] == 0
    assert report["safety_invariants"]["allowed_to_execute"] is False
    assert report["safety_invariants"]["ssh_allowed"] is False
    assert report["safety_invariants"]["live_command_allowed"] is False
    assert report["safety_invariants"]["mapped_task_executed"] is False
    assert report["summary"]["safety_lock_summary"]["allowed_to_execute_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["ssh_allowed_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["live_command_allowed_values"] == [False]
    assert report["summary"]["safety_lock_summary"]["mapped_task_executed_values"] == [False]
    assert all(scenario["mapped_task_executed"] is False for scenario in report["scenarios"])
    assert "Day86 Controlled Runner Harness" in html
    assert "Mapped task executed values" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day87_readonly_executor_phase_gate_review_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "readonly-executor-phase-gate-review"
    )

    assert task["task_id"] == "day87_readonly_executor_phase_gate_review"
    assert task["day"] == "Day87"
    assert task["display_name"] == "Day87 Read-only Executor Phase Gate Review"
    assert task["safety_level"] == "dry-run"
    assert task["execution_mode"] == "dry-run"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day87_readonly_executor_phase_gate_review.json" in task["report_paths"]
    assert "reports/lab-summary/day87_readonly_executor_phase_gate_review.html" in task["report_paths"]
    assert "docs/ai/intent_readonly_executor_phase_gate_review.md" in task["report_paths"]
    assert "docs/roadmap/day87_readonly_executor_phase_gate_review.md" in task["report_paths"]
    assert "DESIGN_ONLY" in task["notes"]
    assert "real_adapter_implementation_allowed remains false" in task["notes"]


def test_day87_readonly_executor_phase_gate_review_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day87 phase gate review must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day87 phase gate review must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "readonly-executor-phase-gate-review"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day87_readonly_executor_phase_gate_review.json"
    html_path = tmp_path / "reports/lab-summary/day87_readonly_executor_phase_gate_review.html"
    assert exit_code == 0
    assert "Day87 Read-only Executor Phase Gate Review" in output
    assert "Task name: readonly-executor-phase-gate-review" in output
    assert "Result: PASS / DESIGN_ONLY" in output
    assert "Reviewed days: Day83, Day84, Day85, Day86" in output
    assert "Execution allowed: false" in output
    assert "SSH allowed: false" in output
    assert "Live command allowed: false" in output
    assert "Write command allowed: false" in output
    assert "Device connection allowed: false" in output
    assert "Real adapter design allowed: true" in output
    assert "Real adapter implementation allowed: false" in output
    assert "Next phase: Day88 Real Read-only Executor Adapter Design Draft" in output
    assert "JSON report: reports/lab-summary/day87_readonly_executor_phase_gate_review.json" in output
    assert "HTML report: reports/lab-summary/day87_readonly_executor_phase_gate_review.html" in output
    assert "[PASS] DESIGN_ONLY. Reviewed Day83, Day84, Day85, and Day86" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["phase_gate_status"] == "PASS"
    assert report["phase_gate_recommendation"] == "DESIGN_ONLY"
    assert report["execution_allowed"] is False
    assert report["real_adapter_design_allowed"] is True
    assert report["real_adapter_implementation_allowed"] is False
    chain_text = json.dumps(report["evidence_chain"], sort_keys=True)
    for day in ("Day83", "Day84", "Day85", "Day86"):
        assert day in chain_text
        assert day in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day88_real_readonly_executor_adapter_design_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "readonly-executor-adapter-design"
    )

    assert task["task_id"] == "day88_real_readonly_executor_adapter_design"
    assert task["day"] == "Day88"
    assert task["display_name"] == "Day88 Real Read-only Executor Adapter Design Draft"
    assert task["safety_level"] == "design-only"
    assert task["execution_mode"] == "design-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day88_real_readonly_executor_adapter_design.json" in task["report_paths"]
    assert "reports/lab-summary/day88_real_readonly_executor_adapter_design.html" in task["report_paths"]
    assert "docs/ai/intent_real_readonly_executor_adapter_design.md" in task["report_paths"]
    assert "docs/roadmap/day88_real_readonly_executor_adapter_design.md" in task["report_paths"]
    assert "execution_supported remains false" in task["notes"]
    assert "Day87 is not redone" in task["notes"]
    assert "no SSH" in task["notes"]


def test_day88_real_readonly_executor_adapter_design_runner_outputs_reports_without_live_access(
    tmp_path, monkeypatch, capsys
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day88 design draft must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day88 design draft must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "readonly-executor-adapter-design"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day88_real_readonly_executor_adapter_design.json"
    html_path = tmp_path / "reports/lab-summary/day88_real_readonly_executor_adapter_design.html"
    assert exit_code == 0
    assert "Day88 Real Read-only Executor Adapter Design Draft" in output
    assert "Task name: readonly-executor-adapter-design" in output
    assert "Result: PASS / DESIGN_ONLY" in output
    assert "Allowlist policy: positive_allowlist" in output
    assert "Execution supported: false" in output
    assert "SSH supported: false" in output
    assert "RouterOS connection supported: false" in output
    assert "Live command supported: false" in output
    assert "Execution unlock supported: false" in output
    assert "Dashboard action button supported: false" in output
    assert "Current adapter state: ADAPTER_NOT_IMPLEMENTED" in output
    assert "Timeout retry supported: false" in output
    assert "Day89 handoff: Real Adapter Safety Boundary Spec" in output
    assert "JSON report: reports/lab-summary/day88_real_readonly_executor_adapter_design.json" in output
    assert "HTML report: reports/lab-summary/day88_real_readonly_executor_adapter_design.html" in output
    assert "[PASS] DESIGN_ONLY. Day88 defines the future adapter contract" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["phase_state"] == "DESIGN_ONLY"
    assert report["execution_supported"] is False
    assert report["ssh_supported"] is False
    assert report["routeros_connection_supported"] is False
    assert report["live_command_supported"] is False
    assert report["execution_unlock_supported"] is False
    assert report["dashboard_execute_button_supported"] is False
    assert report["day87_transition"]["day87_redone"] is False
    assert report["command_allowlist_design"]["policy_type"] == "positive_allowlist"
    assert "export" not in report["command_allowlist_design"]["normalized_commands"]
    assert "export" in report["forbidden_command_policy"]["tokens"]
    assert report["error_contract"]["day88_current_error_code"] == "ADAPTER_NOT_IMPLEMENTED"
    assert report["timeout_contract"]["retry_supported"] is False
    assert report["evidence_contract"]["stdout_collection_state"] == "NOT_COLLECTED_DESIGN_ONLY"
    assert "Day88 does not unlock real read-only execution" in report["final_safety_statement"]
    assert "Real Read-only Executor Adapter Design Draft" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day89_real_adapter_safety_boundary_spec_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "real-adapter-safety-boundary-spec"
    )

    assert task["task_id"] == "day89_real_adapter_safety_boundary_spec"
    assert task["day"] == "Day89"
    assert task["display_name"] == "Day89 Real Adapter Safety Boundary Spec"
    assert task["safety_level"] == "design-only"
    assert task["execution_mode"] == "design-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day89_real_adapter_safety_boundary_spec.json" in task["report_paths"]
    assert "reports/lab-summary/day89_real_adapter_safety_boundary_spec.html" in task["report_paths"]
    assert "docs/ai/real_adapter_safety_boundary_spec.md" in task["report_paths"]
    assert "docs/roadmap/day89_real_adapter_safety_boundary_spec.md" in task["report_paths"]
    assert "implementation_allowed remains false" in task["notes"]
    assert "live_device_access_allowed remains false" in task["notes"]
    assert "ssh_allowed remains false" in task["notes"]


def test_day89_real_adapter_safety_boundary_spec_runner_writes_reports(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day89 boundary spec must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day89 boundary spec must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "real-adapter-safety-boundary-spec"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day89_real_adapter_safety_boundary_spec.json"
    html_path = tmp_path / "reports/lab-summary/day89_real_adapter_safety_boundary_spec.html"
    assert exit_code == 0
    assert "Day89 Real Adapter Safety Boundary Spec" in output
    assert "Task name: real-adapter-safety-boundary-spec" in output
    assert "Result: PASS / DESIGN_ONLY" in output
    assert "safety_boundary_locked=True" in output
    assert "implementation_allowed=False" in output
    assert "live_device_access_allowed=False" in output
    assert "SSH allowed: false" in output
    assert "Config change allowed: false" in output
    assert "Command execution allowed: false" in output
    assert "Reviewer decision required: true" in output
    assert "JSON report: reports/lab-summary/day89_real_adapter_safety_boundary_spec.json" in output
    assert "HTML report: reports/lab-summary/day89_real_adapter_safety_boundary_spec.html" in output
    assert "[PASS] DESIGN_ONLY. Day89 locks the safety boundary" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == 89
    assert report["phase"] == "DESIGN_ONLY"
    assert report["status"] == "PASS"
    assert report["implementation_allowed"] is False
    assert report["live_device_access_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["safety_boundary_locked"] is True
    assert "configuration changes" in {item["capability"] for item in report["blocked_capabilities"]}
    assert "Real Adapter Safety Boundary Spec" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day89_report_index_visibility_includes_boundary_spec(tmp_path, capsys):
    assert network_lab.main(["--task", "real-adapter-safety-boundary-spec"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Real Adapter Safety Boundary Spec" in html
    assert "reports/lab-summary/day89_real_adapter_safety_boundary_spec.json" in html
    assert "reports/lab-summary/day89_real_adapter_safety_boundary_spec.html" in html


def test_day90_real_adapter_implementation_plan_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "real-adapter-implementation-plan"
    )

    assert task["task_id"] == "day90_real_adapter_implementation_plan"
    assert task["day"] == "Day90"
    assert task["display_name"] == "Day90 Real Adapter Implementation Plan"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day90_real_adapter_implementation_plan.json" in task["report_paths"]
    assert "reports/lab-summary/day90_real_adapter_implementation_plan.html" in task["report_paths"]
    assert "docs/ai/intent_real_adapter_implementation_plan.md" in task["report_paths"]
    assert "docs/roadmap/day90_real_adapter_implementation_plan.md" in task["report_paths"]
    assert "adapter_implementation_allowed remains false" in task["notes"]
    assert "live_device_access_allowed remains false" in task["notes"]
    assert "routeros_command_execution_allowed remains false" in task["notes"]


def test_day90_real_adapter_implementation_plan_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day90 implementation plan must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day90 implementation plan must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "real-adapter-implementation-plan"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day90_real_adapter_implementation_plan.json"
    html_path = tmp_path / "reports/lab-summary/day90_real_adapter_implementation_plan.html"
    assert exit_code == 0
    assert "Day90 Real Adapter Implementation Plan" in output
    assert "Task name: real-adapter-implementation-plan" in output
    assert "Scope: PLANNING_ONLY" in output
    assert "Decision: NO_GO" in output
    assert "Adapter implementation allowed: false" in output
    assert "Live device access allowed: false" in output
    assert "SSH allowed: false" in output
    assert "RouterOS command execution allowed: false" in output
    assert "JSON report: reports/lab-summary/day90_real_adapter_implementation_plan.json" in output
    assert "HTML report: reports/lab-summary/day90_real_adapter_implementation_plan.html" in output
    assert "[PASS] PLANNING_ONLY. Day90 produced an implementation-entry decision" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["day"] == 90
    assert report["scope"] == "planning_only"
    assert report["decision"] in {"GO", "CONDITIONAL_GO", "NO_GO"}
    assert report["decision"] != "GO"
    assert report["adapter_implementation_allowed"] is False
    assert report["live_device_access_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["routeros_command_execution_allowed"] is False
    assert report["evidence_chain"]
    assert "configuration mutation" in report["explicitly_forbidden_scope"]
    assert "Real Adapter Implementation Plan" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day90_report_index_visibility_includes_implementation_plan(tmp_path, capsys):
    assert network_lab.main(["--task", "real-adapter-implementation-plan"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Real Adapter Implementation Plan" in html
    assert "reports/lab-summary/day90_real_adapter_implementation_plan.json" in html
    assert "reports/lab-summary/day90_real_adapter_implementation_plan.html" in html


def test_day91_real_adapter_safety_scaffold_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "real-adapter-safety-scaffold"
    )

    assert task["task_id"] == "day91_real_adapter_safety_scaffold"
    assert task["day"] == "Day91"
    assert task["display_name"] == "Day91 Real Adapter Safety Scaffold"
    assert task["safety_level"] == "scaffold-only"
    assert task["execution_mode"] == "scaffold-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day91_real_adapter_safety_scaffold.json" in task["report_paths"]
    assert "reports/lab-summary/day91_real_adapter_safety_scaffold.html" in task["report_paths"]
    assert "docs/ai/intent_real_adapter_safety_scaffold.md" in task["report_paths"]
    assert "docs/roadmap/day91_real_adapter_safety_scaffold.md" in task["report_paths"]
    assert "CONDITIONAL_GO only" in task["notes"]
    assert "live_read_allowed false" in task["notes"]
    assert "real_device_contact_allowed false" in task["notes"]


def test_day91_real_adapter_safety_scaffold_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day91 safety scaffold must not execute subprocess")

    def fail_profile_load(*_args, **_kwargs):
        raise AssertionError("Day91 safety scaffold must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "real-adapter-safety-scaffold"], project_root=tmp_path
    )

    output = capsys.readouterr().out
    json_path = tmp_path / "reports/lab-summary/day91_real_adapter_safety_scaffold.json"
    html_path = tmp_path / "reports/lab-summary/day91_real_adapter_safety_scaffold.html"
    assert exit_code == 0
    assert "Day91 Real Adapter Safety Scaffold" in output
    assert "Task name: real-adapter-safety-scaffold" in output
    assert "Result: PASS / SCAFFOLD_ONLY" in output
    assert "Day90 gate: CONDITIONAL_GO only" in output
    assert "Dangerous actions denied:" in output
    assert "Read-only candidates future-only:" in output
    assert "live_read_allowed: false" in output
    assert "write_allowed: false" in output
    assert "raw_command_allowed: false" in output
    assert "credential_required: false" in output
    assert "transport_required: false" in output
    assert "real_device_contact_allowed: false" in output
    assert "Next required days: Day92, Day93, Day94, Day95, Day96" in output
    assert "JSON report: reports/lab-summary/day91_real_adapter_safety_scaffold.json" in output
    assert "HTML report: reports/lab-summary/day91_real_adapter_safety_scaffold.html" in output
    assert "[PASS] SCAFFOLD_ONLY. Day91 denied dangerous actions" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_decision"] == "PASS"
    assert report["status"] == "SCAFFOLD_ONLY"
    assert report["day90_gate"]["decision"] == "CONDITIONAL_GO"
    assert all(item["decision"] == "DENY" for item in report["dangerous_actions"])
    assert all(item["scope_state"] == "FUTURE_ONLY" for item in report["read_only_candidates"])
    assert report["invariants"]["live_read_allowed"] is False
    assert report["invariants"]["credential_required"] is False
    assert "Real Adapter Safety Scaffold" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day91_report_index_visibility_includes_safety_scaffold(tmp_path, capsys):
    assert network_lab.main(["--task", "real-adapter-safety-scaffold"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Real Adapter Safety Scaffold" in html
    assert "scaffold-only" in html
    assert "reports/lab-summary/day91_real_adapter_safety_scaffold.json" in html
    assert "reports/lab-summary/day91_real_adapter_safety_scaffold.html" in html


def test_day92_real_adapter_executable_guards_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "real-adapter-executable-guards"
    )

    assert task["task_id"] == "day92_real_adapter_executable_guards"
    assert task["day"] == "Day92"
    assert task["display_name"] == "Day92 Real Adapter Executable Guards"
    assert task["safety_level"] == "offline-deterministic-guard"
    assert task["execution_mode"] == "guard-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day92_real_adapter_executable_guards_report.json" in task["report_paths"]
    assert "reports/lab-summary/day92_real_adapter_executable_guards_report.html" in task["report_paths"]
    assert "docs/ai/intent_executable_guards.md" in task["report_paths"]
    assert "docs/roadmap/day92_real_adapter_executable_guards.md" in task["report_paths"]
    assert "rejected_adapter_invocations remains 0" in task["notes"]
    assert "adapter_implementation_added remains false" in task["notes"]
    assert "adds no real adapter" in task["notes"]


def test_day92_real_adapter_executable_guards_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day92 executable guards must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day92 executable guards must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "real-adapter-executable-guards"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day92_real_adapter_executable_guards_report.json"
    html_path = tmp_path / "reports/lab-summary/day92_real_adapter_executable_guards_report.html"
    assert exit_code == 0
    assert "Day92 Real Adapter Executable Guards" in output
    assert "Task name: real-adapter-executable-guards" in output
    assert "Result: PASS / GUARD_ENFORCED" in output
    assert "Total scenarios: 20" in output
    assert "Allowed count: 5" in output
    assert "Rejected count: 15" in output
    assert "adapter_invoked_for_rejected = 0" in output
    assert "Evidence report JSON: reports/lab-summary/day92_real_adapter_executable_guards_report.json" in output
    assert "Evidence report HTML: reports/lab-summary/day92_real_adapter_executable_guards_report.html" in output
    assert "[PASS] GUARD_ENFORCED. Day92 rejected unsafe requests" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["status"] == "PASS"
    assert report["phase"] == "GUARD_ENFORCED"
    assert report["safety_level"] == "offline_deterministic_guard"
    assert report["no_real_device_access"] is True
    assert report["no_ssh"] is True
    assert report["no_subprocess"] is True
    assert report["no_socket"] is True
    assert report["no_real_adapter"] is True
    assert report["adapter_implementation_added"] is False
    assert report["rejected_adapter_invocations"] == 0
    assert all(
        item["executor_invoked"] is False
        for item in report["scenario_results"]
        if item["guard_decision"]["decision"] == "REJECT"
    )
    assert "Real Adapter Executable Guards" in html
    assert "GUARD_ENFORCED" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day92_report_index_visibility_includes_executable_guards(tmp_path, capsys):
    assert network_lab.main(["--task", "real-adapter-executable-guards"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Real Adapter Executable Guards" in html
    assert "offline deterministic guard" in html
    assert "reports/lab-summary/day92_real_adapter_executable_guards_report.json" in html
    assert "reports/lab-summary/day92_real_adapter_executable_guards_report.html" in html


def test_day93_guarded_fake_adapter_contract_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "guarded-fake-adapter-contract"
    )

    assert task["task_id"] == "day93_guarded_fake_adapter_contract"
    assert task["day"] == "Day93"
    assert task["display_name"] == "Day93 Guarded Fake Adapter Contract"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "guarded-fake-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day93_guarded_fake_adapter_contract.json" in task["report_paths"]
    assert "reports/lab-summary/day93_guarded_fake_adapter_contract.html" in task["report_paths"]
    assert "docs/ai/intent_guarded_fake_adapter_contract.md" in task["report_paths"]
    assert "docs/roadmap/day93_guarded_fake_adapter_contract.md" in task["report_paths"]
    assert "real_adapter_invocations remains 0" in task["notes"]
    assert "ssh_allowed remains false" in task["notes"]
    assert "no config.json is read" in task["notes"]


def test_day93_guarded_fake_adapter_contract_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day93 guarded fake adapter contract must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day93 guarded fake adapter contract must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "guarded-fake-adapter-contract"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day93_guarded_fake_adapter_contract.json"
    html_path = tmp_path / "reports/lab-summary/day93_guarded_fake_adapter_contract.html"
    assert exit_code == 0
    assert "Day93 Guarded Fake Adapter Contract" in output
    assert "Task name: guarded-fake-adapter-contract" in output
    assert "PASS" in output
    assert "FAKE_ADAPTER_ONLY" in output
    assert "Total scenarios: 9" in output
    assert "Allowed count: 3" in output
    assert "Rejected count: 6" in output
    assert "Fake adapter invocations: 3" in output
    assert "Rejected adapter invocations = 0" in output
    assert "Real adapter invocations = 0" in output
    assert "JSON report: reports/lab-summary/day93_guarded_fake_adapter_contract.json" in output
    assert "HTML report: reports/lab-summary/day93_guarded_fake_adapter_contract.html" in output
    assert "[PASS] FAKE_ADAPTER_ONLY" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["mode"] == "FAKE_ADAPTER_ONLY"
    assert report["fake_adapter_invocations"] == report["allowed_count"]
    assert report["rejected_adapter_invocations"] == 0
    assert report["real_adapter_invocations"] == 0
    assert report["guard_ordering_violations"] == 0
    assert report["safety_violations"] == 0
    assert report["audit_chain_complete"] is True
    assert report["adapter_boundary_verified"] is True
    assert report["no_config_json_read"] is True
    assert "Guarded Fake Adapter Contract" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()


def test_day93_report_index_visibility_includes_guarded_fake_adapter_contract(tmp_path, capsys):
    assert network_lab.main(["--task", "guarded-fake-adapter-contract"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Guarded Fake Adapter Contract" in html
    assert "fake adapter only" in html
    assert "reports/lab-summary/day93_guarded_fake_adapter_contract.json" in html
    assert "reports/lab-summary/day93_guarded_fake_adapter_contract.html" in html


def test_day94_adapter_boundary_regression_matrix_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "adapter-boundary-regression-matrix"
    )

    assert task["task_id"] == "day94_adapter_boundary_regression_matrix"
    assert task["day"] == "Day94"
    assert task["display_name"] == "Day94 Adapter Boundary Regression Matrix"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "guarded-fake-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day94_adapter_boundary_regression_matrix.json" in task["report_paths"]
    assert "reports/lab-summary/day94_adapter_boundary_regression_matrix.html" in task["report_paths"]
    assert "docs/ai/intent_adapter_boundary_regression_matrix.md" in task["report_paths"]
    assert "docs/roadmap/day94_adapter_boundary_regression_matrix.md" in task["report_paths"]
    assert "adapter_invoked_for_rejected remains 0" in task["notes"]
    assert "real_adapter_invocations remains 0" in task["notes"]
    assert "live_execution_invocations remains 0" in task["notes"]


def test_day94_adapter_boundary_regression_matrix_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day94 adapter boundary matrix must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day94 adapter boundary matrix must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "adapter-boundary-regression-matrix"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day94_adapter_boundary_regression_matrix.json"
    html_path = tmp_path / "reports/lab-summary/day94_adapter_boundary_regression_matrix.html"
    assert exit_code == 0
    assert "Day94 Adapter Boundary Regression Matrix" in output
    assert "Task name: adapter-boundary-regression-matrix" in output
    assert "PASS" in output
    assert "Total rows: 14" in output
    assert "Allowed rows: 6" in output
    assert "Rejected rows: 8" in output
    assert "Fake adapter invocations: 4" in output
    assert "adapter_invoked_for_rejected = 0" in output
    assert "real_adapter_invocations = 0" in output
    assert "live_execution_invocations = 0" in output
    assert "JSON report: reports/lab-summary/day94_adapter_boundary_regression_matrix.json" in output
    assert "HTML report: reports/lab-summary/day94_adapter_boundary_regression_matrix.html" in output
    assert "[PASS] FAKE_ADAPTER_BOUNDARY_EVIDENCE_ONLY" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["summary"]["total_rows"] >= 12
    assert report["summary"]["failed_rows"] == 0
    assert report["summary"]["adapter_invoked_for_rejected"] == 0
    assert report["summary"]["real_adapter_invocations"] == 0
    assert report["summary"]["live_execution_invocations"] == 0
    assert all(
        row["actual_fake_adapter_invoked"] is False
        for row in report["matrix_rows"]
        if row["guard_decision"] == "rejected"
    )
    assert "Adapter Boundary Regression Matrix" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()


def test_day94_report_index_visibility_includes_adapter_boundary_regression_matrix(tmp_path, capsys):
    assert network_lab.main(["--task", "adapter-boundary-regression-matrix"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Adapter Boundary Regression Matrix" in html
    assert "fake-adapter-only matrix" in html
    assert "reports/lab-summary/day94_adapter_boundary_regression_matrix.json" in html
    assert "reports/lab-summary/day94_adapter_boundary_regression_matrix.html" in html


def test_day95_adapter_result_normalization_task_exists_in_catalog():
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "adapter-result-normalization"
    )

    assert task["task_id"] == "day95_adapter_result_normalization"
    assert task["day"] == "Day95"
    assert task["display_name"] == "Day95 Adapter Result Normalization"
    assert task["safety_level"] == "fake-adapter-only"
    assert task["execution_mode"] == "guarded-fake-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert "reports/lab-summary/day95_adapter_result_normalization.json" in task["report_paths"]
    assert "reports/lab-summary/day95_adapter_result_normalization.html" in task["report_paths"]
    assert "docs/ai/intent_adapter_result_normalization.md" in task["report_paths"]
    assert "docs/roadmap/day95_adapter_result_normalization.md" in task["report_paths"]
    assert "rejected scenarios keep adapter_result None" in task["notes"]
    assert "real_adapter_result_count remains 0" in task["notes"]
    assert "live_execution_result_count remains 0" in task["notes"]


def test_day95_adapter_result_normalization_runner_writes_reports_without_live_access(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day95 adapter result normalization must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day95 adapter result normalization must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "adapter-result-normalization"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/day95_adapter_result_normalization.json"
    html_path = tmp_path / "reports/lab-summary/day95_adapter_result_normalization.html"
    assert exit_code == 0
    assert "Day95 Adapter Result Normalization" in output
    assert "Task name: adapter-result-normalization" in output
    assert "PASS" in output
    assert "Total scenarios: 5" in output
    assert "Allowed count: 2" in output
    assert "Rejected count: 3" in output
    assert "Normalized result count: 2" in output
    assert "Fake adapter result count: 2" in output
    assert "real_adapter_result_count = 0" in output
    assert "live_execution_result_count = 0" in output
    assert "result_status_source = deterministic_fake_boundary" in output
    assert "evidence_chain_complete = true" in output
    assert "JSON report: reports/lab-summary/day95_adapter_result_normalization.json" in output
    assert "HTML report: reports/lab-summary/day95_adapter_result_normalization.html" in output
    assert "[PASS] FAKE_ONLY_EVIDENCE_HARDENING" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()

    report = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_status"] == "PASS"
    assert report["summary"]["normalized_result_count"] == report["summary"]["allowed_count"]
    assert report["summary"]["rejected_with_adapter_result"] == 0
    assert report["summary"]["real_adapter_result_count"] == 0
    assert report["summary"]["live_execution_result_count"] == 0
    assert report["summary"]["result_status_source"] == "deterministic_fake_boundary"
    assert all(
        record["adapter_result"] is None
        for record in report["scenario_records"]
        if record["guard_decision"] == "REJECT"
    )
    assert "Adapter Result Normalization" in html
    assert "<form" not in html.lower()
    assert "<button" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "action=" not in html.lower()


def test_day95_report_index_visibility_includes_adapter_result_normalization(tmp_path, capsys):
    assert network_lab.main(["--task", "adapter-result-normalization"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    index_html = tmp_path / "reports/report_index.html"
    assert exit_code == 0
    assert index_html.exists()
    html = index_html.read_text(encoding="utf-8")
    assert "Adapter Result Normalization" in html
    assert "fake-only result normalization" in html
    assert "reports/lab-summary/day95_adapter_result_normalization.json" in html
    assert "reports/lab-summary/day95_adapter_result_normalization.html" in html
