import argparse

import pytest

import performance_test as day8


def args(**overrides):
    values = {
        "device_name": "Hex-s-2025-lab01",
        "router_wan_ip": "192.168.0.199",
        "lan_server_ip": "192.168.88.254",
        "direction": "WAN_TO_LAN",
        "duration": 60,
        "omit": 10,
        "parallel": 4,
        "threshold_mbps": 800,
        "output_dir": None,
        "skip_router_wan_ip_confirm": True,
        "non_interactive": False,
        "router_host": None,
        "router_username": None,
        "router_password": None,
        "router_ssh_port": 22,
        "skip_router_precheck": True,
        "iperf3_path": "iperf3",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_missing_device_name_prompts(monkeypatch):
    prompts = []
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts.append(prompt) or "Hex-s-2025-lab01",
    )

    config = day8.build_config_from_args(args(device_name=None))

    assert config.device_name == "Hex-s-2025-lab01"
    assert prompts == ["Please input device name: "]
    assert config.interactive_input_used is True


def test_missing_router_wan_ip_prompts(monkeypatch):
    prompts = []
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: prompts.append(prompt) or "192.168.0.199",
    )

    config = day8.build_config_from_args(args(router_wan_ip=None))

    assert config.router_wan_ip == "192.168.0.199"
    assert prompts == ["Please input Router WAN IP: "]


def test_missing_direction_can_use_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    config = day8.build_config_from_args(args(direction=None))

    assert config.direction == "WAN_TO_LAN"


def test_missing_lan_server_ip_can_use_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    config = day8.build_config_from_args(args(lan_server_ip=None))

    assert config.lan_server_ip == "192.168.88.254"


def test_non_interactive_missing_required_parameter_errors():
    with pytest.raises(ValueError, match="--router-wan-ip is required"):
        day8.build_config_from_args(
            args(non_interactive=True, router_wan_ip=None, skip_router_precheck=True)
        )


def test_router_wan_ip_not_confirmed_does_not_execute_iperf3(tmp_path, monkeypatch):
    ran_iperf = {"value": False}
    config = day8.Day8Config(
        device_name="Hex-s-2025-lab01",
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
        direction="WAN_TO_LAN",
        duration=60,
        omit=10,
        parallel=4,
        threshold_mbps=800,
        output_dir=tmp_path,
        skip_router_wan_ip_confirm=False,
        non_interactive=False,
        router_host=None,
        router_username=None,
        router_password=None,
        router_ssh_port=22,
        skip_router_precheck=True,
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: "NO")

    def fake_run_iperf3(*_args, **_kwargs):
        ran_iperf["value"] = True

    monkeypatch.setattr(day8, "run_iperf3", fake_run_iperf3)

    report, json_path, html_path = day8.run(config)

    assert report["result"] == "FAIL"
    assert report["router_wan_ip_confirmed"] is False
    assert report["error"] == "Aborted: Router WAN IP was not confirmed."
    assert ran_iperf["value"] is False
    assert json_path.exists()
    assert html_path.exists()


def test_skip_router_wan_ip_confirm_does_not_prompt(monkeypatch, tmp_path):
    config = day8.Day8Config(
        device_name="Hex-s-2025-lab01",
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
        direction="WAN_TO_LAN",
        duration=60,
        omit=10,
        parallel=4,
        threshold_mbps=800,
        output_dir=tmp_path,
        skip_router_wan_ip_confirm=True,
        non_interactive=True,
        router_host=None,
        router_username=None,
        router_password=None,
        router_ssh_port=22,
        skip_router_precheck=True,
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: pytest.fail("unexpected prompt"))
    monkeypatch.setattr(
        day8,
        "run_iperf3",
        lambda *_args, **_kwargs: (
            "PASS",
            {
                "throughput_mbps": 946.0,
                "source_field": "end.sum_received.bits_per_second",
            },
            None,
            "",
        ),
    )

    report, _json_path, _html_path = day8.run(config)

    assert report["router_wan_ip_confirmed"] is True
    assert report["result"] == "PASS"


def test_router_wan_ip_confirm_accepts_lowercase_yes(monkeypatch, tmp_path):
    config = day8.Day8Config(
        device_name="Hex-s-2025-lab01",
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
        direction="WAN_TO_LAN",
        duration=60,
        omit=10,
        parallel=4,
        threshold_mbps=800,
        output_dir=tmp_path,
        skip_router_wan_ip_confirm=False,
        non_interactive=False,
        router_host=None,
        router_username=None,
        router_password=None,
        router_ssh_port=22,
        skip_router_precheck=True,
    )
    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")
    monkeypatch.setattr(
        day8,
        "run_iperf3",
        lambda *_args, **_kwargs: (
            "PASS",
            {
                "throughput_mbps": 946.851,
                "source_field": "end.sum_received.bits_per_second",
            },
            None,
            "",
        ),
    )

    report, _json_path, _html_path = day8.run(config)

    assert report["router_wan_ip_confirmed"] is True
    assert report["result"] == "PASS"
