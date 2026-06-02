import argparse
import getpass
import html
import ipaddress
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import mikrotik_day12_wireguard_vpn_automation as day12


DAY13_TITLE = "Multi-router WireGuard Client-to-Site Validation"
VPN_TYPE = "client_to_site"
DEFAULT_PROFILE_PATH = Path("topology_profiles") / "day13_wireguard_client_to_site_profiles.json"
REPORT_JSON_PATH = Path("reports") / "day13_multi_router_wireguard_client_to_site_summary.json"
REPORT_HTML_PATH = Path("reports") / "day13_multi_router_wireguard_client_to_site_summary.html"
SUMMARY_REPORT_DIR = Path("summary")
SUMMARY_REPORT_STEM = "day13_multi_router_wireguard_client_to_site_summary"
REQUIRED_DEVICE_FIELDS = {
    "device_name",
    "lan_subnet",
    "lan_gateway",
    "wireguard_subnet",
    "wireguard_router_ip",
    "wireguard_client_ip",
    "peer_name",
    "export_conf_name",
}
SECRET_FIELD_NAMES = {"password", "privatekey", "private_key"}
CONF_CONTENT_TOKENS = (
    "[Interface]",
    "[Peer]",
    "PrivateKey",
    "PublicKey",
    "AllowedIPs",
    "Endpoint",
    "PersistentKeepalive",
    "DNS",
    "ListenPort",
)


@dataclass
class DeviceValidation:
    device_name: str
    router_host: str
    client_endpoint_host: str
    lan_subnet: str
    wireguard_subnet: str
    wireguard_router_ip: str
    wireguard_client_ip: str
    lan_gateway: str
    lan_host_ip: str
    iperf_server_ip: str
    peer_name: str
    exported_config_path: str
    result: str
    warnings: List[str]
    errors: List[str]
    lan_host_validation: Dict[str, Any]
    wireguard_tunnel_status: str = "NOT_RUN"
    router_gateway_reachability: str = "NOT_RUN"
    router_to_lan_host_reachability: str = "SKIP"
    router_to_lan_host_ping: str = "SKIP"
    lan_host_diagnosis: str = "LAN host validation disabled"
    remediation_commands: List[str] = None
    day12_report_json: str = ""
    day12_report_html: str = ""


def load_profile(path: Path = DEFAULT_PROFILE_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        profile = json.load(handle)
    if not isinstance(profile, dict):
        raise ValueError("Day13 profile must be a JSON object.")
    return profile


def find_forbidden_profile_fields(value: Any, path: str = "profile") -> List[str]:
    hits: List[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).replace("-", "_").replace(" ", "_").lower()
            next_path = f"{path}.{key}"
            if normalized in SECRET_FIELD_NAMES:
                hits.append(next_path)
            hits.extend(find_forbidden_profile_fields(item, next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(find_forbidden_profile_fields(item, f"{path}[{index}]"))
    return hits


def network(value: str, label: str) -> Any:
    try:
        return ipaddress.ip_network(str(value), strict=False)
    except ValueError as error:
        raise ValueError(f"{label} must be a valid IP network: {value}") from error


def interface(value: str, label: str) -> Any:
    try:
        return ipaddress.ip_interface(str(value))
    except ValueError as error:
        raise ValueError(f"{label} must be a valid IP interface: {value}") from error


def find_overlaps(items: Iterable[Tuple[str, Any]]) -> List[str]:
    values = list(items)
    overlaps: List[str] = []
    for left_index, (left_name, left_net) in enumerate(values):
        for right_name, right_net in values[left_index + 1 :]:
            if left_net.overlaps(right_net):
                overlaps.append(f"{left_name} overlaps {right_name}: {left_net} and {right_net}")
    return overlaps


def find_duplicates(items: Iterable[Tuple[str, str]], label: str) -> List[str]:
    seen: Dict[str, str] = {}
    duplicates: List[str] = []
    for device_name, value in items:
        normalized = str(value).strip()
        if normalized in seen:
            duplicates.append(f"Duplicate {label}: {seen[normalized]} and {device_name} both use {normalized}")
        else:
            seen[normalized] = device_name
    return duplicates


def build_lan_host_validation_config(device: Dict[str, Any]) -> Dict[str, Any]:
    raw = device.get("lan_host_validation", {})
    if not isinstance(raw, dict):
        raw = {}
    enabled = bool(raw.get("enabled", False))
    lan_host_ip = str(raw.get("lan_host_ip") or device.get("lan_host_ip", "")).strip()
    expected_gateway = str(raw.get("expected_gateway") or device.get("lan_gateway", "")).strip()
    wireguard_client_subnet = str(
        raw.get("wireguard_client_subnet") or device.get("wireguard_subnet", "")
    ).strip()
    return {
        "enabled": enabled,
        "lan_host_ip": lan_host_ip,
        "expected_gateway": expected_gateway,
        "wireguard_client_subnet": wireguard_client_subnet,
    }


def parse_router_ping_success(output: str) -> bool:
    received_match = re.search(r"received=(\d+)", output)
    if received_match:
        return int(received_match.group(1)) > 0
    return bool(re.search(r"\s\d+(?:ms|us)\b", output)) and "timeout" not in output.lower()


def build_lan_host_remediation(validation: Dict[str, Any], device_name: str) -> List[str]:
    lan_host_ip = validation.get("lan_host_ip", "")
    gateway = validation.get("expected_gateway", "")
    wg_subnet = validation.get("wireguard_client_subnet", "")
    return [
        f"On the LAN host for {device_name}, run: ipconfig",
        f"Expected IPv4 Address: {lan_host_ip}",
        f"Expected Default Gateway: {gateway}",
        "If Windows Firewall blocks ICMP, run PowerShell as Administrator:",
        (
            'New-NetFirewallRule -DisplayName "Allow ICMPv4 from lab router and WireGuard" '
            f"-Protocol ICMPv4 -IcmpType 8 -RemoteAddress {gateway},{wg_subnet} -Action Allow"
        ),
    ]


def build_lan_host_failure_causes(validation: Dict[str, Any]) -> List[str]:
    return [
        "LAN host Windows Firewall blocking ICMP.",
        f"LAN host IP is not {validation.get('lan_host_ip', '')}.",
        f"LAN host default gateway is not {validation.get('expected_gateway', '')}.",
        "LAN host is not connected to this lab LAN.",
        "MikroTik bridge/port configuration does not include the host port.",
    ]


def build_default_lan_host_result(validation: Dict[str, Any]) -> Dict[str, Any]:
    if not validation.get("enabled"):
        return {
            "router_to_lan_host_ping": "SKIP",
            "router_to_lan_host_reachability": "SKIP",
            "lan_host_diagnosis": "LAN host validation disabled",
            "likely_causes": [],
            "remediation_commands": [],
            "router_ping_output": "",
        }
    return {
        "router_to_lan_host_ping": "SKIP",
        "router_to_lan_host_reachability": "NOT_RUN",
        "lan_host_diagnosis": "LAN host validation not run",
        "likely_causes": [],
        "remediation_commands": [],
        "router_ping_output": "",
    }


def evaluate_lan_host_ping(
    validation: Dict[str, Any],
    router_ping_output: str,
    router_gateway_reachability: str,
    device_name: str,
) -> Dict[str, Any]:
    if not validation.get("enabled"):
        return build_default_lan_host_result(validation)
    passed = parse_router_ping_success(router_ping_output)
    if passed:
        return {
            "router_to_lan_host_ping": "PASS",
            "router_to_lan_host_reachability": "PASS",
            "lan_host_diagnosis": "Router can reach LAN host",
            "likely_causes": [],
            "remediation_commands": [],
            "router_ping_output": router_ping_output,
        }
    diagnosis = (
        "Tunnel OK, LAN host unreachable"
        if router_gateway_reachability == "PASS"
        else "LAN host unreachable; gateway reachability is not confirmed"
    )
    return {
        "router_to_lan_host_ping": "FAIL",
        "router_to_lan_host_reachability": "FAIL",
        "lan_host_diagnosis": diagnosis,
        "likely_causes": build_lan_host_failure_causes(validation),
        "remediation_commands": build_lan_host_remediation(validation, device_name),
        "router_ping_output": router_ping_output,
    }


def apply_lan_host_result(device_summary: Dict[str, Any], result: Dict[str, Any]) -> None:
    device_summary["router_to_lan_host_ping"] = result["router_to_lan_host_ping"]
    device_summary["router_to_lan_host_reachability"] = result["router_to_lan_host_reachability"]
    device_summary["lan_host_diagnosis"] = result["lan_host_diagnosis"]
    device_summary["likely_causes"] = result["likely_causes"]
    device_summary["remediation_commands"] = result["remediation_commands"]
    device_summary["router_ping_output"] = result["router_ping_output"]
    if result["router_to_lan_host_ping"] == "FAIL":
        warning = f"Router cannot ping LAN host: {result['lan_host_diagnosis']}"
        if warning not in device_summary["warnings"]:
            device_summary["warnings"].append(warning)


def validate_device(device: Dict[str, Any]) -> Tuple[DeviceValidation, Dict[str, Any]]:
    device_name = str(device.get("device_name", "<unnamed>"))
    missing = sorted(field for field in REQUIRED_DEVICE_FIELDS if not device.get(field))
    errors = [f"Missing required field: {field}" for field in missing]
    warnings: List[str] = []

    lan_subnet = str(device.get("lan_subnet", ""))
    wireguard_subnet = str(device.get("wireguard_subnet", ""))
    router_ip = str(device.get("wireguard_router_ip", ""))
    client_ip = str(device.get("wireguard_client_ip", ""))
    export_conf_name = str(device.get("export_conf_name", ""))
    lan_host_validation = build_lan_host_validation_config(device)
    lan_host_result = build_default_lan_host_result(lan_host_validation)

    parsed: Dict[str, Any] = {}
    if not missing:
        try:
            parsed["lan_subnet"] = network(lan_subnet, f"{device_name} lan_subnet")
            parsed["wireguard_subnet"] = network(wireguard_subnet, f"{device_name} wireguard_subnet")
            parsed["wireguard_router_ip"] = interface(router_ip, f"{device_name} wireguard_router_ip")
            parsed["wireguard_client_ip"] = interface(client_ip, f"{device_name} wireguard_client_ip")
            if parsed["wireguard_router_ip"].ip not in parsed["wireguard_subnet"]:
                errors.append("Router WireGuard IP is outside the device WireGuard subnet.")
            if parsed["wireguard_client_ip"].ip not in parsed["wireguard_subnet"]:
                errors.append("Client WireGuard IP is outside the device WireGuard subnet.")
            day12.validate_conf_filename(export_conf_name)
        except ValueError as error:
            errors.append(str(error))

    exported_config_path = str(day12.EXPORT_ROOT / export_conf_name) if export_conf_name else ""
    result = "FAIL" if errors else "PASS"
    return (
        DeviceValidation(
            device_name=device_name,
            router_host=str(device.get("router_host", "")),
            client_endpoint_host=str(device.get("client_endpoint_host", "")),
            lan_subnet=lan_subnet,
            wireguard_subnet=wireguard_subnet,
            wireguard_router_ip=router_ip,
            wireguard_client_ip=client_ip,
            lan_gateway=str(device.get("lan_gateway", "")),
            lan_host_ip=str(device.get("lan_host_ip", "")),
            iperf_server_ip=str(device.get("iperf_server_ip", "")),
            peer_name=str(device.get("peer_name", "")),
            exported_config_path=exported_config_path,
            result=result,
            warnings=warnings,
            errors=errors,
            lan_host_validation=lan_host_validation,
            router_to_lan_host_reachability=lan_host_result["router_to_lan_host_reachability"],
            router_to_lan_host_ping=lan_host_result["router_to_lan_host_ping"],
            lan_host_diagnosis=lan_host_result["lan_host_diagnosis"],
            remediation_commands=lan_host_result["remediation_commands"],
        ),
        parsed,
    )


def validate_profile(profile: Dict[str, Any], device_name: str = "") -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    forbidden_fields = find_forbidden_profile_fields(profile)
    if forbidden_fields:
        errors.append("Profile must not contain password or PrivateKey fields: " + ", ".join(forbidden_fields))

    if profile.get("vpn_type") != VPN_TYPE:
        errors.append("vpn_type must be client_to_site.")

    devices = profile.get("devices")
    if not isinstance(devices, list) or not devices:
        errors.append("Profile must contain a non-empty devices array.")
        devices = []

    enabled_devices = [device for device in devices if isinstance(device, dict) and device.get("enabled", True)]
    if device_name:
        enabled_devices = [device for device in enabled_devices if device.get("device_name") == device_name]
        if not enabled_devices:
            errors.append(f"Enabled device profile was not found: {device_name}")
    disabled_count = len(
        [
            device
            for device in devices
            if isinstance(device, dict)
            and not device.get("enabled", True)
            and not device.get("template", False)
        ]
    )
    if disabled_count:
        warnings.append(f"{disabled_count} device profile(s) disabled and skipped.")

    device_results: List[DeviceValidation] = []
    parsed_by_device: Dict[str, Dict[str, Any]] = {}
    for device in enabled_devices:
        result, parsed = validate_device(device)
        device_results.append(result)
        parsed_by_device[result.device_name] = parsed

    lan_networks = [
        (device.device_name, parsed["lan_subnet"])
        for device in device_results
        for parsed in [parsed_by_device.get(device.device_name, {})]
        if "lan_subnet" in parsed
    ]
    wg_networks = [
        (device.device_name, parsed["wireguard_subnet"])
        for device in device_results
        for parsed in [parsed_by_device.get(device.device_name, {})]
        if "wireguard_subnet" in parsed
    ]
    errors.extend(f"LAN subnet overlap: {item}" for item in find_overlaps(lan_networks))
    errors.extend(f"WireGuard subnet overlap: {item}" for item in find_overlaps(wg_networks))
    errors.extend(
        find_duplicates(
            ((device.device_name, device.wireguard_client_ip) for device in device_results),
            "client WireGuard IP",
        )
    )
    errors.extend(
        find_duplicates(
            ((device.device_name, device.wireguard_router_ip) for device in device_results),
            "router WireGuard IP",
        )
    )
    errors.extend(
        find_duplicates(
            ((device.device_name, device.exported_config_path) for device in device_results),
            "exported config path",
        )
    )

    for device in device_results:
        if errors:
            cross_device_errors = [
                error
                for error in errors
                if device.device_name in error and error not in device.errors
            ]
            device.errors.extend(cross_device_errors)
        if device.errors:
            device.result = "FAIL"

    if any(device.result == "FAIL" for device in device_results) or errors:
        overall = "FAIL"
    elif warnings or any(device.warnings for device in device_results):
        overall = "WARN"
    else:
        overall = "PASS"

    return {
        "title": DAY13_TITLE,
        "vpn_type": VPN_TYPE,
        "topology_name": profile.get("topology_name", DAY13_TITLE),
        "overall_result": overall,
        "warnings": sorted(set(warnings)),
        "errors": sorted(set(errors)),
        "devices": [device.__dict__ for device in device_results],
        "suggestions": build_suggestions(device_results),
    }


def build_suggestions(devices: List[DeviceValidation]) -> List[str]:
    suggestions: List[str] = []
    for device in devices:
        if device.result == "PASS":
            continue
        suggestions.append(
            f"Review Day13 profile values for {device.device_name}; keep this as Client-to-Site and use separate LAN/WireGuard subnets."
        )
    return suggestions


def aggregate_result(device_results: Iterable[Dict[str, Any]]) -> str:
    statuses = [str(device.get("result", "")).upper() for device in device_results]
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if any(status in {"WARN", "SKIP", "SKIPPED"} for status in statuses):
        return "WARN"
    return "PASS"


def status_badge(status: str) -> str:
    normalized = str(status).upper()
    if normalized in {"PASS", "WARN", "FAIL", "SKIP"}:
        return color_text(f"[{normalized}]", status_color(normalized))
    return color_text(f"[{normalized or 'UNKNOWN'}]", "37")


def color_enabled() -> bool:
    return os.environ.get("NO_COLOR", "").strip() == ""


def color_text(text: str, color_code: str) -> str:
    if not color_enabled():
        return text
    return f"\033[{color_code}m{text}\033[0m"


def status_color(status: str) -> str:
    normalized = str(status).upper()
    if normalized == "PASS":
        return "32;1"
    if normalized == "WARN":
        return "33;1"
    if normalized == "FAIL":
        return "31;1"
    if normalized == "SKIP":
        return "90;1"
    return "37"


def mode_label(mode: str) -> str:
    if mode == "day12_per_device_validation":
        return "Day12 per-device validation"
    return "Static profile validation"


def check_status_from_errors(errors: Iterable[str], markers: Iterable[str]) -> str:
    marker_values = tuple(markers)
    return "FAIL" if any(any(marker in error for marker in marker_values) for error in errors) else "PASS"


def build_static_check_rows(report: Dict[str, Any]) -> List[Tuple[str, str]]:
    errors = report.get("errors", [])
    return [
        ("vpn_type is client_to_site", check_status_from_errors(errors, ("vpn_type must be client_to_site",))),
        (
            "required profile fields exist",
            "FAIL"
            if any("Missing required field" in error for device in report.get("devices", []) for error in device.get("errors", []))
            or any("devices array" in error for error in errors)
            else "PASS",
        ),
        (
            "no password or private key fields in profile",
            check_status_from_errors(errors, ("password or PrivateKey fields",)),
        ),
        ("WireGuard subnets do not overlap", check_status_from_errors(errors, ("WireGuard subnet overlap",))),
        ("LAN subnets do not overlap", check_status_from_errors(errors, ("LAN subnet overlap",))),
        ("client WireGuard IPs are unique", check_status_from_errors(errors, ("Duplicate client WireGuard IP",))),
        ("router WireGuard IPs are unique", check_status_from_errors(errors, ("Duplicate router WireGuard IP",))),
        ("exported config filenames are unique", check_status_from_errors(errors, ("Duplicate exported config path",))),
    ]


def build_console_output(
    report: Dict[str, Any],
    json_path: Path,
    html_path: Path,
    summary_json_path: Optional[Path] = None,
    summary_html_path: Optional[Path] = None,
) -> str:
    export_label = (
        "Exported config path"
        if report.get("mode") == "day12_per_device_validation"
        else "Expected export path"
    )
    lines = [
        color_text(f"Day13 {DAY13_TITLE}", "36;1"),
        color_text("VPN type: Client-to-Site", "36;1"),
        f"Mode: {mode_label(str(report.get('mode', 'static_profile_validation')))}",
        "",
        color_text("Static validation checks:", "36;1"),
    ]
    for label, status in build_static_check_rows(report):
        lines.append(f"  {status_badge(status)} {label}")

    lines.extend(["", color_text("Device profile summary:", "36;1")])
    for device in report.get("devices", []):
        lines.extend(
            [
                f"  {device.get('device_name', '<unnamed>')}",
                f"    Router SSH host: {device.get('router_host', '') or 'Not set'}",
                f"    Client endpoint host: {device.get('client_endpoint_host', '') or 'Not set'}",
                f"    LAN subnet: {device.get('lan_subnet', '')}",
                f"    LAN gateway: {device.get('lan_gateway', '')}",
                f"    LAN host: {device.get('lan_host_ip', '') or 'Not set'}",
                f"    iperf server: {device.get('iperf_server_ip', '') or 'Not set'}",
                f"    WireGuard subnet: {device.get('wireguard_subnet', '')}",
                f"    Router WireGuard IP: {device.get('wireguard_router_ip', '')}",
                f"    Client WireGuard IP: {device.get('wireguard_client_ip', '')}",
                f"    Peer name: {device.get('peer_name', '')}",
                f"    {export_label}: {device.get('exported_config_path', '')}",
                f"    WireGuard tunnel status: {status_badge(str(device.get('wireguard_tunnel_status', 'NOT_RUN')))}",
                f"    Router gateway reachability: {status_badge(str(device.get('router_gateway_reachability', 'NOT_RUN')))}",
                f"    Router to LAN host reachability: {status_badge(str(device.get('router_to_lan_host_reachability', 'SKIP')))}",
                f"    LAN host diagnosis: {device.get('lan_host_diagnosis', '')}",
                f"    Result: {status_badge(str(device.get('result', 'UNKNOWN')))}",
            ]
        )
        for remediation in device.get("remediation_commands", []):
            lines.append(f"    Remediation: {remediation}")
        for warning in device.get("warnings", []):
            lines.append(f"    {status_badge('WARN')} {warning}")
        for error in device.get("errors", []):
            lines.append(f"    {status_badge('FAIL')} {error}")

    lines.extend(
        [
            "",
            f"{color_text('Overall result:', '36;1')} {status_badge(str(report.get('overall_result', 'UNKNOWN')))}",
            f"JSON report: {json_path}",
            f"HTML report: {html_path}",
        ]
    )
    if summary_json_path and summary_html_path:
        lines.extend(
            [
                f"Summary JSON report: {summary_json_path}",
                f"Summary HTML report: {summary_html_path}",
            ]
        )
    return "\n".join(lines)


def find_profile_device(profile: Dict[str, Any], device_name: str) -> Dict[str, Any]:
    for device in profile.get("devices", []):
        if isinstance(device, dict) and device.get("device_name") == device_name:
            return device
    raise ValueError(f"Device profile was not found: {device_name}")


def build_lab_setup_guidance(
    device: Dict[str, Any],
    endpoint_host: str = "",
    router_host: str = "",
    router_username: str = "admin",
) -> str:
    wg_interface = str(device.get("wg_interface", day12.DEFAULT_WG_INTERFACE))
    listen_port = int(device.get("listen_port", 13231))
    endpoint = endpoint_host or str(device.get("client_endpoint_host", "")) or f"{device['device_name']}-public-endpoint"
    ssh_host = router_host or str(device.get("router_host", "")) or f"{device['device_name']}-ssh-host"
    username = router_username or str(device.get("router_username", "")) or "admin"
    client_dns = str(device.get("client_dns", device["lan_gateway"]))
    client_allowed_ips = f"{device['wireguard_subnet']},{device['lan_subnet']}"
    keepalive = int(device.get("client_keepalive", day12.DEFAULT_KEEPALIVE))
    export_path = day12.EXPORT_ROOT / str(device["export_conf_name"])
    lan_host_ip = str(device.get("lan_host_ip", "")) or str(device["lan_gateway"])
    iperf_server_ip = str(device.get("iperf_server_ip", "")) or lan_host_ip

    routeros_commands = [
        (
            f"/interface/wireguard/add name={day12.quote_routeros_value(wg_interface)} "
            f"listen-port={listen_port} comment=\"day13 client-to-site {device['device_name']}\""
        ),
        (
            f"/ip/address/add address={day12.quote_routeros_value(device['wireguard_router_ip'])} "
            f"interface={day12.quote_routeros_value(wg_interface)} comment=\"day13 wireguard gateway\""
        ),
        day12.build_peer_add_command(
            wg_interface,
            str(device["peer_name"]),
            str(device["wireguard_client_ip"]),
            client_dns,
            endpoint,
            client_allowed_ips,
            keepalive,
        ),
        (
            f"/ip/firewall/filter/add chain=input action=accept protocol=udp "
            f"in-interface-list=WAN dst-port={listen_port} comment=\"day13 allow wireguard udp\""
        ),
        '/ip/firewall/filter/move [find comment="day13 allow wireguard udp"] destination=6',
        (
            f"/ip/firewall/filter/add chain=forward action=accept "
            f"src-address={day12.quote_routeros_value(device['wireguard_subnet'])} "
            f"dst-address={day12.quote_routeros_value(device['lan_subnet'])} "
            f"comment=\"day13 allow wireguard to LAN\""
        ),
    ]
    export_command = " ".join(
        [
            "python mikrotik_day12_wireguard_vpn_automation.py",
            f"--device-name {device['device_name']}",
            f"--router-host {ssh_host}",
            f"--router-username {username}",
            f"--wg-interface {wg_interface}",
            f"--peer-name {device['peer_name']}",
            f"--client-address {device['wireguard_client_ip']}",
            f"--client-dns {client_dns}",
            f"--client-endpoint-host {endpoint}",
            f"--client-allowed-ips {client_allowed_ips}",
            f"--wg-router-ip {device['wireguard_router_ip']}",
            f"--lan-subnet {device['lan_subnet']}",
            f"--lan-gateway-ip {device['lan_gateway']}",
            f"--lan-host-ip {lan_host_ip}",
            f"--iperf-server-ip {iperf_server_ip}",
            f"--conf-filename {device['export_conf_name']}",
        ]
    )

    lines = [
        color_text(f"Day13 semi-automatic setup guidance: {device['device_name']}", "36;1"),
        "Mode: Show setup guidance only",
        f"{status_badge('SKIP')} No router changes were applied by this script.",
        f"{status_badge('PASS')} Client config private key will be generated by private-key=auto on the peer add command.",
        "",
        color_text(
            "Review these RouterOS commands, then paste them into the MikroTik terminal if they match your lab:",
            "36;1",
        ),
    ]
    lines.extend(f"  {command}" for command in routeros_commands)
    lines.extend(
        [
            "",
            color_text("After RouterOS setup is complete, run Day12 export/validation:", "36;1"),
            f"  {export_command}",
            "",
            f"Expected export path after Day12 succeeds: {export_path}",
            "",
            color_text("Verify these RouterOS states before running Day12 export:", "36;1"),
            f"  /ip/firewall/filter/print",
            f"    Expect: day13 allow wireguard udp is before defconf drop all not coming from LAN.",
            f"    Expect: day13 allow wireguard to LAN allows {device['wireguard_subnet']} -> {device['lan_subnet']}.",
            f"  /ip/address/print where interface={wg_interface}",
            f"    Expect: {device['wireguard_router_ip']} on {wg_interface}.",
            f"  ping {device['lan_gateway']}",
            f"    Expect: lab client can reach the {device['device_name']} LAN gateway.",
            f"  ping {lan_host_ip}",
            f"    Expect: lab client can reach the selected LAN host if it is online and allows ICMP.",
            "",
            color_text("Verify the LAN host side if LAN gateway works but LAN host ping fails:", "36;1"),
            f"  LAN host IP should be {lan_host_ip}.",
            f"  LAN host default gateway should be {device['lan_gateway']}.",
            f"  Windows Firewall on the LAN host should allow ICMP Echo Request.",
            f"  If the LAN host uses another default gateway, add a route back to {device['wireguard_subnet']} via {device['lan_gateway']}.",
            f"  /interface/wireguard/peers/print detail",
            f"    Expect: peer name {device['peer_name']}.",
            f"    Expect: allowed-address={device['wireguard_client_ip']}.",
            f"    Expect: client-address={device['wireguard_client_ip']}.",
            f"    Expect: client-dns={client_dns}.",
            f"    Expect: client-endpoint={endpoint}.",
            f"    Expect: client-allowed-address={client_allowed_ips}.",
            "Notes:",
            "  - Replace the endpoint host with this device's public WAN/DDNS value if needed.",
            "  - The commands are additive; review existing interfaces, peers, and firewall rules before pasting.",
            "  - The firewall move command keeps UDP 13231 above the default input drop rule.",
            "  - This guidance does not read exports/wireguard and does not print WireGuard client config content.",
        ]
    )
    return "\n".join(lines)


def build_day12_config(device: Dict[str, Any], args: argparse.Namespace) -> day12.Day12Config:
    router_password = os.environ.get("MIKROTIK_PASSWORD", "")
    if not router_password and not args.non_interactive:
        router_password = getpass.getpass(f"SSH password for {device['device_name']}: ")
    return day12.Day12Config(
        device_name=device["device_name"],
        router_host=device.get("router_host", args.router_host or ""),
        router_username=device.get("router_username", args.router_username or "admin"),
        router_password=router_password,
        router_ssh_port=int(device.get("router_ssh_port", args.router_ssh_port)),
        wg_interface=device.get("wg_interface", day12.DEFAULT_WG_INTERFACE),
        peer_name=device["peer_name"],
        client_address=device["wireguard_client_ip"],
        client_dns=device.get("client_dns", device["lan_gateway"]),
        client_endpoint_host=device.get("client_endpoint_host", device.get("router_host", args.router_host or "")),
        client_allowed_ips=f"{device['wireguard_subnet']},{device['lan_subnet']}",
        client_keepalive=int(device.get("client_keepalive", day12.DEFAULT_KEEPALIVE)),
        conf_filename=device["export_conf_name"],
        wg_router_ip=device["wireguard_router_ip"],
        lan_subnet=device["lan_subnet"],
        lan_gateway_ip=device["lan_gateway"],
        lan_host_ip=device.get("lan_host_ip", args.lan_host_ip or device["lan_gateway"]),
        iperf_server_ip=device.get("iperf_server_ip", args.iperf_server_ip or device.get("lan_host_ip", device["lan_gateway"])),
        iperf_port=int(device.get("iperf_port", day12.DEFAULT_IPERF_PORT)),
        iperf_duration=int(device.get("iperf_duration", day12.DEFAULT_IPERF_DURATION)),
        iperf_omit=int(device.get("iperf_omit", day12.DEFAULT_IPERF_OMIT)),
        iperf_parallel=int(device.get("iperf_parallel", day12.DEFAULT_IPERF_PARALLEL)),
        run_iperf=args.run_iperf,
        recreate_peer=False,
        apply_firewall_fixes=False,
        expect_connected=args.expect_connected,
        non_interactive=args.non_interactive,
    )


def classify_day12_tunnel(device_summary: Dict[str, Any], day12_report: Dict[str, Any]) -> None:
    checks = day12_report.get("checks", {})
    gateway_status = str(checks.get("ping_lan_gateway", "SKIP"))
    device_summary["router_gateway_reachability"] = gateway_status
    if gateway_status == "PASS" or checks.get("handshake_seen") == "PASS" or checks.get("peer_rx_tx_nonzero") == "PASS":
        device_summary["wireguard_tunnel_status"] = "PASS"
    elif gateway_status in {"FAIL", "WARN"}:
        device_summary["wireguard_tunnel_status"] = gateway_status
    else:
        device_summary["wireguard_tunnel_status"] = "NOT_RUN"


def run_router_lan_host_ping(config: day12.Day12Config, validation: Dict[str, Any]) -> str:
    lan_host_ip = str(validation.get("lan_host_ip", "")).strip()
    ipaddress.ip_address(lan_host_ip)
    day2_config = day12.Day2Config(
        host=config.router_host,
        port=config.router_ssh_port,
        username=config.router_username,
        password=config.router_password,
        device_name=config.device_name,
        target_routeros_version="",
        enable_apply_config=False,
        enable_backup=False,
        enable_report=True,
        timezone="",
        disable_services=[],
    )
    client = day12.connect_ssh_with_auth_retry(day2_config)
    try:
        return day12.run_raw_command(client, f"/ping {lan_host_ip} count=4")
    finally:
        client.close()


def run_day12_for_devices(profile: Dict[str, Any], report: Dict[str, Any], args: argparse.Namespace) -> None:
    devices_by_name = {
        device["device_name"]: device
        for device in profile.get("devices", [])
        if isinstance(device, dict) and device.get("enabled", True) and device.get("device_name")
    }
    for device_summary in report["devices"]:
        if device_summary["result"] == "FAIL":
            continue
        profile_device = devices_by_name.get(device_summary["device_name"], {})
        if not profile_device.get("router_host") and not args.router_host:
            device_summary["result"] = "WARN"
            device_summary["warnings"].append("Day12 device validation skipped because router_host was not provided.")
            continue
        day12_config = build_day12_config(profile_device, args)
        day12_report, json_path, html_path = day12.run(day12_config)
        device_summary["result"] = day12_report.get("overall_result", "FAIL")
        device_summary["warnings"].extend(day12_report.get("warnings", []))
        device_summary["errors"].extend(day12_report.get("errors", []))
        device_summary["day12_report_json"] = str(json_path)
        device_summary["day12_report_html"] = str(html_path)
        classify_day12_tunnel(device_summary, day12_report)
        if day12_report.get("wireguard_summary", {}).get("exported_config_path"):
            device_summary["exported_config_path"] = day12_report["wireguard_summary"]["exported_config_path"]
        validation = device_summary.get("lan_host_validation", {})
        if validation.get("enabled"):
            try:
                ping_output = run_router_lan_host_ping(day12_config, validation)
                lan_result = evaluate_lan_host_ping(
                    validation,
                    ping_output,
                    device_summary.get("router_gateway_reachability", "SKIP"),
                    device_summary["device_name"],
                )
            except Exception as error:
                lan_result = evaluate_lan_host_ping(
                    validation,
                    f"{type(error).__name__}: {error}",
                    device_summary.get("router_gateway_reachability", "SKIP"),
                    device_summary["device_name"],
                )
            apply_lan_host_result(device_summary, lan_result)
    report["overall_result"] = aggregate_result(report["devices"])


def assert_no_conf_content(value: Any) -> None:
    text = json.dumps(value, sort_keys=True)
    for token in CONF_CONTENT_TOKENS:
        if token in text:
            raise ValueError(f"Day13 report must not contain WireGuard .conf content token: {token}")


def report_timestamp_for_filename(report: Dict[str, Any]) -> str:
    raw_timestamp = str(report.get("timestamp", "")).strip()
    try:
        timestamp = datetime.fromisoformat(raw_timestamp)
    except ValueError:
        timestamp = datetime.now()
    return timestamp.strftime("%Y%m%d_%H%M%S")


def write_aggregate_reports(report: Dict[str, Any]) -> Tuple[Path, Path, Path, Path]:
    assert_no_conf_content(report)
    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    REPORT_JSON_PATH.write_text(json_text, encoding="utf-8")
    html_report = build_html_report(report)
    for token in CONF_CONTENT_TOKENS:
        if token in html_report:
            raise ValueError(f"Day13 HTML report must not contain WireGuard .conf content token: {token}")
    REPORT_HTML_PATH.write_text(html_report, encoding="utf-8")
    timestamp = report_timestamp_for_filename(report)
    summary_json_path = SUMMARY_REPORT_DIR / f"{SUMMARY_REPORT_STEM}_{timestamp}.json"
    summary_html_path = SUMMARY_REPORT_DIR / f"{SUMMARY_REPORT_STEM}_{timestamp}.html"
    summary_json_path.write_text(json_text, encoding="utf-8")
    summary_html_path.write_text(html_report, encoding="utf-8")
    return REPORT_JSON_PATH, REPORT_HTML_PATH, summary_json_path, summary_html_path


def html_status_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    css = value.lower() if value in {"PASS", "WARN", "FAIL", "SKIP"} else "unknown"
    return f"<span class=\"badge {html.escape(css)}\">{html.escape(value)}</span>"


def html_list(items: Iterable[Any]) -> str:
    values = [str(item) for item in items if str(item)]
    if not values:
        return "<p class=\"muted\">None</p>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in values) + "</ul>"


def html_code_blocks(items: Iterable[Any]) -> str:
    values = [str(item) for item in items if str(item)]
    if not values:
        return "<p class=\"muted\">None</p>"
    return "".join(f"<pre><code>{html.escape(item)}</code></pre>" for item in values)


def html_detail_grid(items: Iterable[Tuple[str, Any]]) -> str:
    return "<dl class=\"detail-grid\">" + "".join(
        f"<div><dt>{html.escape(label)}</dt><dd>{html.escape(str(value or 'None'))}</dd></div>"
        for label, value in items
    ) + "</dl>"


def build_device_overview_rows(devices: Iterable[Dict[str, Any]]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(device.get('device_name', '')))}</td>"
        f"<td>{html.escape(str(device.get('router_host', '')))}</td>"
        f"<td>{html.escape(str(device.get('lan_subnet', '')))}</td>"
        f"<td>{html.escape(str(device.get('lan_host_ip', '')))}</td>"
        f"<td>{html.escape(str(device.get('wireguard_subnet', '')))}</td>"
        f"<td>{html_status_badge(device.get('result', ''))}</td>"
        "</tr>"
        for device in devices
    )


def build_device_diagnosis_sections(report: Dict[str, Any]) -> str:
    export_label = (
        "Exported config path"
        if report.get("mode") == "day12_per_device_validation"
        else "Expected export path"
    )
    sections: List[str] = []
    for device in report.get("devices", []):
        details = html_detail_grid(
            [
                ("Router SSH host", device.get("router_host", "")),
                ("Client endpoint host", device.get("client_endpoint_host", "")),
                ("LAN subnet", device.get("lan_subnet", "")),
                ("LAN gateway", device.get("lan_gateway", "")),
                ("LAN host", device.get("lan_host_ip", "")),
                ("iperf server", device.get("iperf_server_ip", "")),
                ("WireGuard subnet", device.get("wireguard_subnet", "")),
                ("Router WireGuard IP", device.get("wireguard_router_ip", "")),
                ("Client WireGuard IP", device.get("wireguard_client_ip", "")),
                ("Peer name", device.get("peer_name", "")),
                (export_label, device.get("exported_config_path", "")),
            ]
        )
        checklist = "\n".join(
            [
                f"<li><span>WireGuard tunnel status</span>{html_status_badge(device.get('wireguard_tunnel_status', 'NOT_RUN'))}</li>",
                f"<li><span>Router gateway reachability</span>{html_status_badge(device.get('router_gateway_reachability', 'NOT_RUN'))}</li>",
                f"<li><span>Router to LAN host reachability</span>{html_status_badge(device.get('router_to_lan_host_reachability', 'SKIP'))}</li>",
                f"<li><span>LAN host diagnosis</span><strong>{html.escape(str(device.get('lan_host_diagnosis', 'None')))}</strong></li>",
            ]
        )
        sections.append(
            f"""
  <section class="card">
    <div class="card-header">
      <h3>{html.escape(str(device.get("device_name", "")))}</h3>
      {html_status_badge(device.get("result", ""))}
    </div>
    {details}
    <h4>Connectivity Checklist</h4>
    <ul class="checklist">{checklist}</ul>
    <h4>Likely Causes</h4>
    {html_list(device.get("likely_causes", []))}
    <h4>Remediation Commands</h4>
    {html_code_blocks(device.get("remediation_commands", []))}
    <h4>Warnings</h4>
    {html_list(device.get("warnings", []))}
    <h4>Errors</h4>
    {html_list(device.get("errors", []))}
  </section>
"""
        )
    return "\n".join(sections)


def build_html_report(report: Dict[str, Any]) -> str:
    devices = report.get("devices", [])
    rows = build_device_overview_rows(devices)
    device_sections = build_device_diagnosis_sections(report)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(DAY13_TITLE)}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2937; background: #f8fafc; }}
    h1, h2, h3, h4 {{ margin: 0 0 10px; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 20px; margin-top: 28px; }}
    h3 {{ font-size: 18px; }}
    h4 {{ font-size: 14px; margin-top: 18px; color: #374151; }}
    .summary, .card {{ background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 12px; }}
    .summary-grid div, .detail-grid div {{ border: 1px solid #e5e7eb; border-radius: 6px; padding: 10px; background: #f9fafb; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 12px; }}
    .pass {{ color: #047857; background: #d1fae5; }}
    .warn {{ color: #92400e; background: #fef3c7; }}
    .fail {{ color: #991b1b; background: #fee2e2; }}
    .skip, .unknown {{ color: #374151; background: #e5e7eb; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    td, th {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .card-header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; margin-bottom: 14px; }}
    .detail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin: 0; }}
    dt {{ font-size: 12px; color: #6b7280; font-weight: 700; text-transform: uppercase; }}
    dd {{ margin: 4px 0 0; overflow-wrap: anywhere; }}
    .checklist {{ list-style: none; padding: 0; margin: 0; }}
    .checklist li {{ display: flex; justify-content: space-between; gap: 12px; border: 1px solid #e5e7eb; border-radius: 6px; padding: 10px; margin-bottom: 8px; background: #f9fafb; }}
    ul {{ margin-top: 8px; }}
    pre {{ background: #111827; color: #f9fafb; border-radius: 6px; padding: 12px; overflow-x: auto; white-space: pre-wrap; }}
    code {{ font-family: Consolas, monospace; }}
    .muted {{ color: #6b7280; margin: 8px 0; }}
  </style>
</head>
<body>
  <section class="summary">
    <h1>{html.escape(DAY13_TITLE)}</h1>
    <div class="summary-grid">
      <div><dt>VPN type</dt><dd>Client-to-Site</dd></div>
      <div><dt>Mode</dt><dd>{html.escape(mode_label(str(report.get("mode", "static_profile_validation"))))}</dd></div>
      <div><dt>Overall result</dt><dd>{html_status_badge(report.get("overall_result", ""))}</dd></div>
      <div><dt>Device count</dt><dd>{len(devices)}</dd></div>
    </div>
  </section>
  <h2>Device Overview</h2>
  <table>
    <thead>
      <tr>
        <th>Device</th>
        <th>Router SSH host</th>
        <th>LAN subnet</th>
        <th>LAN host</th>
        <th>WireGuard subnet</th>
        <th>Result</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Per-Device Diagnosis</h2>
  {device_sections}
</body>
</html>
"""


def build_report(profile: Dict[str, Any], device_name: str = "") -> Dict[str, Any]:
    report = validate_profile(profile, device_name=device_name)
    report["timestamp"] = datetime.now().isoformat(timespec="seconds")
    report["day"] = 13
    report["mode"] = "static_profile_validation"
    return report


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DAY13_TITLE)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--device-name", default="", help="Run validation for one enabled device profile.")
    parser.add_argument("--show-setup", help="Print semi-automatic RouterOS setup guidance for one device profile.")
    parser.add_argument("--setup-endpoint-host", default="", help="Client endpoint host to show in --show-setup guidance.")
    parser.add_argument("--setup-router-host", default="", help="Router SSH host to show in the Day12 export command.")
    parser.add_argument("--run-day12", action="store_true", help="Run Day12 validation for each valid enabled device.")
    parser.add_argument("--router-host", default="", help="Fallback MikroTik SSH host for --run-day12.")
    parser.add_argument("--router-username", default="admin", help="Fallback MikroTik SSH username for --run-day12.")
    parser.add_argument("--router-ssh-port", type=int, default=22)
    parser.add_argument("--lan-host-ip", default="", help="Fallback LAN host ping target for --run-day12.")
    parser.add_argument("--iperf-server-ip", default="", help="Fallback iperf3 server target for --run-day12.")
    parser.add_argument("--expect-connected", action="store_true")
    parser.add_argument("--run-iperf", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
        profile = load_profile(args.profile)
        if args.show_setup:
            report = build_report(profile)
            if report["overall_result"] == "FAIL":
                print(build_console_output(report, REPORT_JSON_PATH, REPORT_HTML_PATH))
                return 2
            device = find_profile_device(profile, args.show_setup)
            print(
                build_lab_setup_guidance(
                    device,
                    endpoint_host=args.setup_endpoint_host,
                    router_host=args.setup_router_host or args.router_host,
                    router_username=args.router_username,
                )
            )
            return 0
        report = build_report(profile, device_name=args.device_name)
        if args.run_day12 and report["overall_result"] != "FAIL":
            report["mode"] = "day12_per_device_validation"
            run_day12_for_devices(profile, report, args)
        json_path, html_path, summary_json_path, summary_html_path = write_aggregate_reports(report)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}")
        return 2

    print(build_console_output(report, json_path, html_path, summary_json_path, summary_html_path))
    return {"PASS": 0, "WARN": 1, "FAIL": 2}.get(report["overall_result"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
