import pytest

import performance_test as day8


def test_wan_to_lan_command_does_not_include_reverse_mode():
    command = day8.build_iperf3_command("192.168.0.199", "WAN_TO_LAN_DNAT", 60, 4, 10)

    assert command == [
        "iperf3",
        "-c",
        "192.168.0.199",
        "-t",
        "60",
        "-P",
        "4",
        "-O",
        "10",
        "-J",
    ]
    assert "-R" not in command


def test_lan_to_wan_command_includes_reverse_mode():
    command = day8.build_iperf3_command(
        "192.168.0.199",
        "LAN_TO_WAN_DNAT_REPLY",
        60,
        4,
        10,
    )

    assert command == [
        "iperf3",
        "-c",
        "192.168.0.199",
        "-t",
        "60",
        "-P",
        "4",
        "-R",
        "-O",
        "10",
        "-J",
    ]


def test_command_target_uses_router_wan_ip():
    command = day8.build_iperf3_command("192.168.0.199", "WAN_TO_LAN_DNAT", 30, 2, 5)

    assert command[2] == "192.168.0.199"
    assert "192.168.88.254" not in command


def test_invalid_direction_has_clear_error():
    with pytest.raises(ValueError, match="WAN_TO_LAN_DNAT or LAN_TO_WAN_DNAT_REPLY"):
        day8.build_iperf3_command("192.168.0.199", "SIDEWAYS", 60, 4, 10)


def test_command_can_use_custom_iperf3_path():
    command = day8.build_iperf3_command(
        "192.168.0.199",
        "WAN_TO_LAN_DNAT",
        20,
        4,
        10,
        "C:\\Tools\\iperf3.exe",
    )

    assert command == [
        "C:\\Tools\\iperf3.exe",
        "-c",
        "192.168.0.199",
        "-t",
        "20",
        "-P",
        "4",
        "-O",
        "10",
        "-J",
    ]


def test_missing_iperf3_executable_returns_clear_error(monkeypatch):
    monkeypatch.setattr(day8.shutil, "which", lambda _executable: None)

    result, parsed, error, stderr = day8.run_iperf3(
        ["iperf3", "-c", "192.168.0.199", "-t", "20", "-P", "4", "-O", "10", "-J"],
        timeout=60,
    )

    assert result == "FAIL"
    assert parsed is None
    assert stderr == ""
    assert "iperf3 executable was not found" in error
    assert "--iperf3-path" in error


def test_default_args_use_40_second_duration_and_10_second_omit():
    args = day8.parse_args(
        [
            "--device-name",
            "Hex-s-2025-lab01",
            "--router-wan-ip",
            "192.168.0.199",
            "--lan-server-ip",
            "192.168.88.254",
            "--direction",
            "WAN_TO_LAN_DNAT",
            "--skip-router-precheck",
            "--non-interactive",
        ]
    )
    config = day8.build_config_from_args(args)
    command = day8.build_iperf3_command(
        config.router_wan_ip,
        config.direction,
        config.duration,
        config.parallel,
        config.omit,
    )

    assert config.duration == 40
    assert config.omit == 10
    assert config.warn_threshold_mbps == 700
    assert config.direction == "WAN_TO_LAN_DNAT"
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


def test_legacy_direction_aliases_are_normalized():
    assert day8.validate_direction("WAN_TO_LAN") == "WAN_TO_LAN_DNAT"
    assert day8.validate_direction("LAN_TO_WAN") == "LAN_TO_WAN_DNAT_REPLY"


def test_warn_result_between_warn_floor_and_target_threshold():
    result, message = day8.evaluate_throughput_result(769.354, 800, 700)

    assert result == "WARN"
    assert "below the target threshold" in message
