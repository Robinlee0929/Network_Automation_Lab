import json
import re
from pathlib import Path

import pytest

import performance_regression as day9


def make_config(tmp_path: Path, **overrides):
    values = {
        "device_name": "Hex-s-2025-lab01",
        "direction": "WAN_TO_LAN_DNAT",
        "router_wan_ip": "192.168.0.199",
        "lan_server_ip": "192.168.88.254",
        "client_ip": None,
        "duration": 40,
        "parallel": 4,
        "omit": 10,
        "runs": 3,
        "threshold_mbps": 800.0,
        "baseline_mbps": 948.0,
        "regression_ratio": 0.90,
        "output_dir": tmp_path / "reports" / "Hex-s-2025-lab01",
    }
    values.update(overrides)
    return day9.Day9Config(**values)


def test_pass_logic_with_baseline():
    result = day9.classify_run_result(946.35, 800, 948, 0.90)

    assert result == "PASS"


def test_warning_logic_with_baseline():
    result = day9.classify_run_result(840, 800, 948, 0.90)

    assert result == "WARNING"


def test_fail_logic_with_baseline():
    result = day9.classify_run_result(799.99, 800, 948, 0.90)

    assert result == "FAIL"


def test_pass_fail_logic_without_baseline():
    assert day9.classify_run_result(801, 800, None, 0.90) == "PASS"
    assert day9.classify_run_result(799, 800, None, 0.90) == "FAIL"


def test_aggregate_calculation():
    runs = [
        {"throughput_mbps": 900.0, "result": "PASS"},
        {"throughput_mbps": 800.0, "result": "WARNING"},
        {"throughput_mbps": 700.0, "result": "FAIL"},
    ]

    aggregate = day9.aggregate_results(runs)

    assert aggregate["average_mbps"] == 800.0
    assert aggregate["min_mbps"] == 700.0
    assert aggregate["max_mbps"] == 900.0
    assert aggregate["standard_deviation_mbps"] == pytest.approx(81.65, abs=0.001)
    assert aggregate["pass_count"] == 1
    assert aggregate["warning_count"] == 1
    assert aggregate["fail_count"] == 1
    assert aggregate["total_runs"] == 3
    assert aggregate["overall_result"] == "FAIL"


def test_overall_result_calculation():
    assert day9.calculate_overall_result([{"result": "PASS"}]) == "PASS"
    assert (
        day9.calculate_overall_result([{"result": "PASS"}, {"result": "WARNING"}])
        == "WARNING"
    )
    assert (
        day9.calculate_overall_result([{"result": "WARNING"}, {"result": "FAIL"}])
        == "FAIL"
    )


def test_report_path_generation(tmp_path):
    output_dir = tmp_path / "reports" / "Hex-s-2025-lab01"

    paths = day9.report_paths(output_dir)

    assert paths["json"] == output_dir / "day9_performance_regression_report.json"
    assert paths["html"] == output_dir / "day9_performance_regression_report.html"
    assert paths["txt"] == output_dir / "day9_performance_regression_report.txt"


def test_archived_report_path_generation(tmp_path):
    output_dir = tmp_path / "reports" / "Hex-s-2025-lab01"

    paths = day9.archived_report_paths(
        output_dir,
        "LAN_TO_WAN_DNAT_REPLY",
        "PASS",
        "20260530_013400",
    )

    archive_dir = output_dir / "performance_regression"
    assert paths["json_archive"].parent == archive_dir
    assert paths["html_archive"].parent == archive_dir
    assert paths["txt_archive"].parent == archive_dir
    assert paths["json_archive"].name == "LAN_TO_WAN_DNAT_REPLY_PASS_20260530_013400.json"
    assert paths["html_archive"].name == "LAN_TO_WAN_DNAT_REPLY_PASS_20260530_013400.html"
    assert paths["txt_archive"].name == "LAN_TO_WAN_DNAT_REPLY_PASS_20260530_013400.txt"
    assert paths["json_archive"].parent.name == "performance_regression"
    assert paths["json_archive"].parent.parent == output_dir


def test_parse_iperf3_json_uses_sample_data():
    parsed = day9.parse_iperf3_json(
        {"end": {"sum_received": {"bits_per_second": 946_350_000}}}
    )

    assert parsed["throughput_mbps"] == 946.35
    assert parsed["measured_field"] == "end.sum_received.bits_per_second"


def test_parse_iperf3_json_falls_back_to_sum_sent():
    parsed = day9.parse_iperf3_json(
        {"end": {"sum_sent": {"bits_per_second": 812_500_000}}}
    )

    assert parsed["throughput_mbps"] == 812.5
    assert parsed["measured_field"] == "end.sum_sent.bits_per_second"


def test_command_construction_for_wan_to_lan_dnat(tmp_path):
    config = make_config(tmp_path, direction="WAN_TO_LAN_DNAT")

    command = day9.build_iperf3_command(config)

    assert command == [
        "iperf3",
        "-c",
        "192.168.0.199",
        "-t",
        "40",
        "-P",
        "4",
        "-O",
        "10",
        "-J",
    ]
    assert "-R" not in command


def test_command_construction_for_lan_to_wan_dnat_reply(tmp_path):
    config = make_config(tmp_path, direction="LAN_TO_WAN_DNAT_REPLY")

    command = day9.build_iperf3_command(config)

    assert command == [
        "iperf3",
        "-c",
        "192.168.0.199",
        "-t",
        "40",
        "-P",
        "4",
        "-R",
        "-O",
        "10",
        "-J",
    ]


def test_command_construction_for_lan_to_wan_routing_uses_client_ip(tmp_path):
    config = make_config(
        tmp_path,
        direction="LAN_TO_WAN_ROUTING",
        client_ip="192.168.0.114",
    )

    command = day9.build_iperf3_command(config)

    assert command[2] == "192.168.0.114"
    assert "-R" not in command


def test_json_report_generation_validation(tmp_path):
    config = make_config(tmp_path)
    runs = [
        day9.make_run_result(
            config,
            1,
            day9.build_iperf3_command(config),
            946.35,
            "end.sum_received.bits_per_second",
            "PASS",
        )
    ]
    report = day9.build_report(config, day9.aggregate_results(runs), runs)

    path = day9.write_json_report(report, config.output_dir)
    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert loaded["metadata"]["day"] == "Performance Regression"
    assert loaded["metadata"]["title"] == "Router Performance Regression Framework"
    assert loaded["config"]["direction"] == "WAN_TO_LAN_DNAT"
    assert loaded["aggregate"]["overall_result"] == "PASS"
    assert loaded["runs"][0]["command"].startswith("iperf3 -c")


def test_html_report_generation_validation(tmp_path):
    config = make_config(tmp_path)
    runs = [
        day9.make_run_result(
            config,
            1,
            day9.build_iperf3_command(config),
            946.35,
            "end.sum_received.bits_per_second",
            "PASS",
        )
    ]
    report = day9.build_report(config, day9.aggregate_results(runs), runs)

    path = day9.write_html_report(report, config.output_dir)
    content = path.read_text(encoding="utf-8")

    assert "Router Performance Regression" in content
    assert "Hex-s-2025-lab01" in content
    assert "WAN_TO_LAN_DNAT" in content
    assert "iperf3 -c 192.168.0.199" in content


def test_txt_report_generation_validation(tmp_path):
    config = make_config(tmp_path)
    runs = [
        day9.make_run_result(
            config,
            1,
            day9.build_iperf3_command(config),
            946.35,
            "end.sum_received.bits_per_second",
            "PASS",
        )
    ]
    report = day9.build_report(config, day9.aggregate_results(runs), runs)
    json_path = day9.write_json_report(report, config.output_dir)
    html_path = day9.write_html_report(report, config.output_dir)

    path = day9.write_txt_report(report, config.output_dir, json_path, html_path)
    content = path.read_text(encoding="utf-8")

    assert "Router Performance Regression" in content
    assert "Overall Result: PASS" in content
    assert "Run 1: 946.35 Mbps PASS" in content
    assert "JSON report path:" in content


def test_stable_top_level_json_schema_validation(tmp_path):
    config = make_config(tmp_path)
    report = day9.build_report(config, day9.aggregate_results([]), [])

    assert list(report.keys()) == ["metadata", "config", "aggregate", "runs"]


def test_write_reports_generates_fixed_latest_and_archives(tmp_path):
    config = make_config(tmp_path, direction="LAN_TO_WAN_DNAT_REPLY")
    runs = [
        day9.make_run_result(
            config,
            1,
            day9.build_iperf3_command(config),
            946.35,
            "end.sum_received.bits_per_second",
            "PASS",
        )
    ]
    report = day9.build_report(config, day9.aggregate_results(runs), runs)
    report["metadata"]["generated_at"] = "2026-05-30T01:34:00"

    paths = day9.write_reports(report, config.output_dir)

    assert paths["json"] == config.output_dir / "day9_performance_regression_report.json"
    assert paths["html"] == config.output_dir / "day9_performance_regression_report.html"
    assert paths["txt"] == config.output_dir / "day9_performance_regression_report.txt"
    assert paths["json"].exists()
    assert paths["html"].exists()
    assert paths["txt"].exists()
    assert day9.path_exists(paths["json_archive"])
    assert day9.path_exists(paths["html_archive"])
    assert day9.path_exists(paths["txt_archive"])
    assert paths["json_archive"].parent == config.output_dir / "performance_regression"
    assert paths["json_archive"].parent.parent == config.output_dir
    assert paths["json_archive"].name == "LAN_TO_WAN_DNAT_REPLY_PASS_20260530_013400.json"
    assert re.search(r"\d{8}_\d{6}", paths["json_archive"].name)
    assert "LAN_TO_WAN_DNAT_REPLY" in paths["json_archive"].name
    assert "PASS" in paths["json_archive"].name
    assert "946" not in paths["json_archive"].name
    assert "946.35" not in paths["json_archive"].name
    assert not (config.output_dir / "performance_regression" / "LAN_TO_WAN_DNAT_REPLY").exists()
    assert day9.filesystem_path(paths["json"]).read_text(encoding="utf-8") == day9.filesystem_path(
        paths["json_archive"]
    ).read_text(encoding="utf-8")
    assert day9.filesystem_path(paths["html"]).read_text(encoding="utf-8") == day9.filesystem_path(
        paths["html_archive"]
    ).read_text(encoding="utf-8")
    assert day9.filesystem_path(paths["txt"]).read_text(encoding="utf-8") == day9.filesystem_path(
        paths["txt_archive"]
    ).read_text(encoding="utf-8")


def test_help_flags_are_available(capsys):
    for flag in ("-h", "-help"):
        with pytest.raises(SystemExit) as error:
            day9.parse_args([flag])
        captured = capsys.readouterr()

        assert error.value.code == 0
        assert "Router Performance Regression Framework" in captured.out
        assert "--device-name" in captured.out


def test_no_real_iperf3_execution_in_unit_tests(monkeypatch, tmp_path):
    config = make_config(tmp_path, runs=2)
    sample = {"end": {"sum_received": {"bits_per_second": 946_000_000}}}
    calls = []

    def fake_run(command, timeout, **_kwargs):
        calls.append((command, timeout))
        return sample, None

    monkeypatch.setattr(day9, "run_iperf3_command", fake_run)

    report, paths = day9.run_regression(config)

    assert len(calls) == 2
    assert report["aggregate"]["overall_result"] == "PASS"
    assert paths["json"].exists()
    assert paths["html"].exists()
    assert paths["txt"].exists()
    assert day9.path_exists(paths["json_archive"])
    assert day9.path_exists(paths["html_archive"])
    assert day9.path_exists(paths["txt_archive"])
