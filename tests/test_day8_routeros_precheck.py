import json

import performance_test as day8


GOOD_OUTPUTS = {
    "addresses": '0 address=192.168.0.199/24 interface=ether1 actual-interface=ether1',
    "dst_nat": (
        '0 chain=dstnat action=dst-nat protocol=tcp dst-port=5201 '
        'to-addresses=192.168.88.254 to-ports=5201 disabled=no'
    ),
    "forward_filter": (
        '0 chain=forward action=accept protocol=tcp dst-address=192.168.88.254 '
        'dst-port=5201 disabled=no'
    ),
    "fasttrack": '0 chain=forward action=fasttrack-connection disabled=no',
    "ether1": "status=link-ok rate=1Gbps full-duplex=yes",
}


def evaluate(overrides=None):
    outputs = dict(GOOD_OUTPUTS)
    if overrides:
        outputs.update(overrides)
    return day8.evaluate_routeros_outputs(
        outputs,
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
    )


def test_nat_output_detects_dst_nat_rule():
    result = evaluate()

    assert result["checks"]["dst_nat_found"] is True
    assert result["result"] == "PASS"


def test_filter_output_detects_allow_rule():
    result = evaluate()

    assert result["checks"]["firewall_filter_allow_found"] is True
    assert result["result"] == "PASS"


def test_wrapped_routeros_nat_output_detects_dst_nat_rule():
    output = """
Flags: X - DISABLED, I - INVALID; D - DYNAMIC
 3    ;;; day8 iperf3 WAN to LAN dst-nat
      chain=dstnat action=dst-nat to-addresses=192.168.88.254 to-ports=5201 protocol=tcp in-interface=ether1 dst-port=5201
"""

    assert day8.dst_nat_found(output, "192.168.88.254") is True


def test_wrapped_routeros_filter_output_detects_allow_rule():
    output = """
Flags: X - DISABLED, I - INVALID; D - DYNAMIC
13    ;;; day8 allow iperf3 WAN to LAN
      chain=forward action=accept protocol=tcp dst-address=192.168.88.254 in-interface=ether1 dst-port=5201
"""

    assert day8.firewall_filter_allow_found(output, "192.168.88.254") is True


def test_missing_dst_nat_fails_precheck():
    result = evaluate({"dst_nat": ""})

    assert result["result"] == "FAIL"
    assert result["checks"]["dst_nat_found"] is False
    assert "Missing dst-nat" in result["errors"][0]


def test_missing_filter_allow_fails_precheck():
    result = evaluate({"forward_filter": ""})

    assert result["result"] == "FAIL"
    assert result["checks"]["firewall_filter_allow_found"] is False
    assert "Missing firewall forward accept" in result["errors"][0]


def test_router_wan_ip_missing_fails_precheck():
    result = evaluate({"addresses": '0 address=192.168.0.200/24 interface=ether1'})

    assert result["result"] == "FAIL"
    assert result["checks"]["router_wan_ip_found"] is False
    assert "/ip address print" in result["suggested_manual_checks"]


def test_fasttrack_missing_warns_without_failure():
    result = evaluate({"fasttrack": ""})

    assert result["result"] == "PASS"
    assert result["checks"]["fasttrack_found"] is False
    assert result["warnings"] == ["FastTrack rule was not found."]


def test_ether1_not_gigabit_full_duplex_warns_without_failure():
    result = evaluate({"ether1": "status=link-ok rate=100Mbps full-duplex=no"})

    assert result["result"] == "PASS"
    assert result["checks"]["ether1_link_ok"] is False
    assert "ether1 is not reporting" in result["warnings"][0]


def test_missing_dst_nat_suggests_dnat_command():
    result = evaluate({"dst_nat": ""})

    assert result["suggested_mikrotik_commands"] == [
        '/ip firewall nat add chain=dstnat in-interface=ether1 protocol=tcp dst-port=5201 action=dst-nat to-addresses=192.168.88.254 to-ports=5201 comment="day8 iperf3 WAN to LAN dst-nat"'
    ]


def test_missing_filter_allow_suggests_filter_command():
    result = evaluate({"forward_filter": ""})

    assert result["suggested_mikrotik_commands"] == [
        '/ip firewall filter add chain=forward in-interface=ether1 protocol=tcp dst-address=192.168.88.254 dst-port=5201 action=accept comment="day8 allow iperf3 WAN to LAN"'
    ]


def test_precheck_fail_does_not_execute_iperf3_and_writes_reports(tmp_path, monkeypatch):
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
        skip_router_wan_ip_confirm=True,
        non_interactive=True,
        router_host="192.168.88.1",
        router_username="admin",
        router_password="password",
        router_ssh_port=22,
        skip_router_precheck=False,
    )
    monkeypatch.setattr(day8, "run_routeros_precheck", lambda _config: evaluate({"dst_nat": ""}))

    def fake_run_iperf3(*_args, **_kwargs):
        ran_iperf["value"] = True

    monkeypatch.setattr(day8, "run_iperf3", fake_run_iperf3)

    report, json_path, html_path = day8.run(config)
    saved = json.loads(json_path.read_text(encoding="utf-8"))

    assert report["result"] == "FAIL"
    assert report["router_precheck_result"] == "FAIL"
    assert report["error"] == "RouterOS precheck failed. iperf3 was not executed."
    assert ran_iperf["value"] is False
    assert saved["suggested_mikrotik_commands"]
    assert html_path.exists()


def test_ssh_timeout_precheck_includes_reachable_host_guidance(monkeypatch):
    config = day8.Day8Config(
        device_name="Hex-s-2025-lab01",
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
        direction="WAN_TO_LAN",
        duration=60,
        omit=10,
        parallel=4,
        threshold_mbps=800,
        output_dir=None,
        skip_router_wan_ip_confirm=True,
        non_interactive=True,
        router_host="192.168.88.1",
        router_username="admin",
        router_password="password",
        router_ssh_port=22,
        skip_router_precheck=False,
    )
    monkeypatch.setattr(
        day8,
        "connect_routeros",
        lambda **_kwargs: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    result = day8.run_routeros_precheck(config)

    assert result["result"] == "FAIL"
    assert "RouterOS SSH precheck failed: TimeoutError: timed out" in result["errors"]
    assert "Confirm --router-host is reachable from the WAN-side PC." in result[
        "suggested_manual_checks"
    ]
    assert "To run iperf3 without RouterOS SSH validation, add --skip-router-precheck." in result[
        "suggested_manual_checks"
    ]


def test_html_precheck_skip_uses_skip_badges_not_false_fail():
    config = day8.Day8Config(
        device_name="Hex-s-2025-lab01",
        router_wan_ip="192.168.0.199",
        lan_server_ip="192.168.88.254",
        direction="WAN_TO_LAN",
        duration=40,
        omit=10,
        parallel=4,
        threshold_mbps=800,
        output_dir=None,
        skip_router_wan_ip_confirm=True,
        non_interactive=True,
        router_host=None,
        router_username=None,
        router_password=None,
        router_ssh_port=22,
        skip_router_precheck=True,
    )
    report = day8.base_report(
        config,
        ["iperf3", "-c", "192.168.0.199", "-t", "40", "-P", "4", "-O", "10", "-J"],
        True,
    )
    report["result"] = "PASS"
    report["throughput_mbps"] = 946.611
    report["router_precheck_result"] = "SKIP"

    html = day8.build_html_report(report)

    assert "RouterOS precheck was skipped" in html
    assert "Firewall/NAT state was not verified" in html
    assert html.count('class="badge skip"') >= 4
    assert "Test Path" in html
    assert "No suggested commands" in html
