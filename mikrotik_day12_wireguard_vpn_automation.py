import argparse
import getpass
import html
import ipaddress
import json
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any, Dict, Iterable, List, Optional, Tuple

import paramiko

from mikrotik_day2_auto_setup import (
    Day2Config,
    connect_ssh_with_auth_retry,
    quote_routeros_value,
    run_raw_command,
)
from mikrotik_post_validation import sanitize_path_name


REPORT_ROOT = Path("reports")
EXPORT_ROOT = Path("exports") / "wireguard"
FEATURE = "WireGuard Client Config Export + VPN Throughput Baseline Automation"
DEFAULT_WG_INTERFACE = "wg0"
DEFAULT_PEER_NAME = "pc-wg-day12"
DEFAULT_CLIENT_ADDRESS = "10.10.10.2/32"
DEFAULT_CLIENT_DNS = "192.168.88.1"
DEFAULT_CLIENT_ENDPOINT_HOST = "192.168.0.199"
DEFAULT_CLIENT_ALLOWED_IPS = "10.10.10.0/24,192.168.88.0/24"
DEFAULT_KEEPALIVE = 25
DEFAULT_CONF_FILENAME = "wireguard-client.conf"
DEFAULT_WG_ROUTER_IP = "10.10.10.1/24"
DEFAULT_LAN_SUBNET = "192.168.88.0/24"
DEFAULT_LAN_GATEWAY_IP = "192.168.88.1"
DEFAULT_LAN_HOST_IP = "192.168.88.254"
DEFAULT_IPERF_PORT = 5201
DEFAULT_IPERF_DURATION = 40
DEFAULT_IPERF_OMIT = 10
DEFAULT_IPERF_PARALLEL = 4
DEFAULT_IPERF_THRESHOLD_MBPS = 100.0
DEFAULT_DAY12_CONFIG_PATH = Path("Set_WireguardVPN_config.json")

READ_COMMANDS = {
    "/system/resource/print",
    "/system/routerboard/print",
    "/interface/wireguard/print detail",
    "/interface/wireguard/peers/print detail",
    "/ip/address/print detail",
    "/ip/firewall/filter/print detail",
    "/interface/list/member/print detail",
    "/ip/route/print detail",
}


@dataclass
class Day12Config:
    device_name: str
    router_host: str
    router_username: str
    router_password: str
    router_ssh_port: int
    wg_interface: str
    peer_name: str
    client_address: str
    client_dns: str
    client_endpoint_host: str
    client_allowed_ips: str
    client_keepalive: int
    conf_filename: str
    wg_router_ip: str
    lan_subnet: str
    lan_gateway_ip: str
    lan_host_ip: str
    iperf_server_ip: str
    iperf_port: int
    iperf_duration: int
    iperf_omit: int
    iperf_parallel: int
    run_iperf: bool
    recreate_peer: bool
    apply_firewall_fixes: bool
    expect_connected: bool
    non_interactive: bool


def validate_conf_filename(filename: str) -> str:
    value = filename.strip()
    if not value.endswith(".conf"):
        raise ValueError("WireGuard config filename must end with .conf.")
    if "/" in value or "\\" in value:
        raise ValueError("WireGuard config filename must not contain path separators.")
    if ".." in value:
        raise ValueError("WireGuard config filename must not contain '..'.")
    if Path(value).is_absolute() or re.match(r"^[A-Za-z]:", value):
        raise ValueError("WireGuard config filename must not be an absolute path.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise ValueError("WireGuard config filename may only use letters, numbers, dash, underscore, and dot.")
    return value


def build_export_path(filename: str) -> Path:
    safe_name = validate_conf_filename(filename)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    return EXPORT_ROOT / safe_name


def sanitize_client_config_for_report(config_text: str) -> str:
    return re.sub(
        r"(?im)^(\s*PrivateKey\s*=\s*).+$",
        r"\1REDACTED",
        config_text,
    )


def redact_private_keys(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_client_config_for_report(value)
    if isinstance(value, dict):
        return {key: redact_private_keys(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_private_keys(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_private_keys(item) for item in value)
    return value


def private_key_leaked(value: Any) -> bool:
    if isinstance(value, str):
        for line in value.splitlines():
            match = re.match(r"(?i)^\s*PrivateKey\s*=\s*(.*?)\s*$", line)
            if match and match.group(1).strip().upper() != "REDACTED":
                return True
        return False
    if isinstance(value, dict):
        return any(private_key_leaked(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(private_key_leaked(item) for item in value)
    return False


def parse_wireguard_client_config(config_text: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {"interface": {}, "peer": {}, "valid": False, "missing": []}
    section = ""
    for line in config_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped == "[Interface]":
            section = "interface"
            continue
        if stripped == "[Peer]":
            section = "peer"
            continue
        if "=" in stripped and section in {"interface", "peer"}:
            key, value = stripped.split("=", 1)
            parsed[section][key.strip()] = value.strip()

    required = [
        ("interface", "PrivateKey"),
        ("interface", "Address"),
        ("peer", "PublicKey"),
        ("peer", "AllowedIPs"),
        ("peer", "Endpoint"),
        ("peer", "PersistentKeepalive"),
    ]
    parsed["missing"] = [f"{section}.{key}" for section, key in required if key not in parsed[section]]
    parsed["valid"] = not parsed["missing"]
    return parsed


def endpoint_host_only(endpoint: str) -> str:
    value = endpoint.strip()
    if re.fullmatch(r"\d+\.\d+\.\d+\.\d+:\d+", value):
        return value.rsplit(":", 1)[0]
    return value


def validate_endpoint_host(endpoint: str) -> str:
    host = endpoint_host_only(endpoint)
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        raise ValueError("Client endpoint host must be a host or IP only, for example 192.168.0.199.")
    return host


def build_peer_add_command(
    wg_interface: str,
    peer_name: str,
    client_address: str,
    client_dns: str,
    client_endpoint_host: str,
    client_allowed_ips: str,
    keepalive: int,
) -> str:
    endpoint = endpoint_host_only(client_endpoint_host)
    parts = [
        "/interface/wireguard/peers/add",
        f"interface={quote_routeros_value(wg_interface)}",
        f"name={quote_routeros_value(peer_name)}",
        "private-key=auto",
        f"allowed-address={quote_routeros_value(client_address)}",
        f"client-address={quote_routeros_value(client_address)}",
        f"client-dns={quote_routeros_value(client_dns)}",
        f"client-endpoint={quote_routeros_value(endpoint)}",
        f"client-allowed-address={quote_routeros_value(client_allowed_ips)}",
        f"client-keepalive={int(keepalive)}",
        'comment="day12 wireguard client config export"',
    ]
    return " ".join(parts)


def build_peer_remove_command(peer_name: str) -> str:
    return f"/interface/wireguard/peers/remove [find name={quote_routeros_value(peer_name)}]"


def split_routeros_records(output: str) -> List[str]:
    records: List[List[str]] = []
    current: List[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("Flags:", "Columns:", "#")):
            continue
        if re.match(r"^\d+\s", stripped) and current:
            records.append(current)
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        records.append(current)
    return [" ".join(record) for record in records]


def parse_key_values(text: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for key, value in re.findall(r"([\w-]+)=((?:\"[^\"]*\")|\S+)", text):
        values[key] = value.strip('"')
    for key, value in re.findall(r"([\w-]+)\s*:\s*(.*?)(?=\s+[\w-]+\s*:|$)", text):
        values[key] = value.strip().strip('"')
    return values


def parse_wireguard_peer_detail(output: str, peer_name: Optional[str] = None) -> Dict[str, Any]:
    records = split_routeros_records(output)
    selected: Dict[str, str] = {}
    for record in records or [output]:
        values = parse_key_values(record)
        if peer_name is None or values.get("name") == peer_name:
            selected = values
            break
    rx = parse_routeros_bytes(selected.get("rx", selected.get("rx-byte", "0")))
    tx = parse_routeros_bytes(selected.get("tx", selected.get("tx-byte", "0")))
    handshake = selected.get("latest-handshake") or selected.get("last-handshake") or ""
    return {
        "exists": bool(selected),
        "name": selected.get("name", ""),
        "allowed_address": selected.get("allowed-address", ""),
        "client_allowed_address": selected.get("client-allowed-address", ""),
        "latest_handshake": handshake,
        "handshake_seen": bool(handshake and handshake.lower() not in {"never", "0s"}),
        "rx_bytes": rx,
        "tx_bytes": tx,
        "rx_tx_nonzero": rx > 0 and tx > 0,
        "raw": " ".join(selected.values()) if selected else "",
    }


def parse_routeros_bytes(value: str) -> int:
    text = str(value).strip().replace(" ", "")
    match = re.match(r"^([\d.]+)([KMGT]?i?B)?$", text, re.IGNORECASE)
    if not match:
        return 0
    amount = float(match.group(1))
    unit = (match.group(2) or "B").lower()
    multipliers = {
        "b": 1,
        "kb": 1000,
        "mb": 1000 ** 2,
        "gb": 1000 ** 3,
        "tb": 1000 ** 4,
        "kib": 1024,
        "mib": 1024 ** 2,
        "gib": 1024 ** 3,
        "tib": 1024 ** 4,
    }
    return int(amount * multipliers.get(unit, 1))


def parse_wireguard_interfaces(output: str) -> List[Dict[str, str]]:
    return [parse_key_values(record) for record in split_routeros_records(output)]


def detect_firewall_udp_allow_before_drop(output: str, listen_port: int) -> Dict[str, Any]:
    accept_index: Optional[int] = None
    drop_index: Optional[int] = None
    for index, record in enumerate(split_routeros_records(output)):
        values = parse_key_values(record)
        if values.get("chain") != "input" or values.get("disabled", "no").lower() in {"yes", "true"}:
            continue
        action = values.get("action", "")
        if (
            accept_index is None
            and action == "accept"
            and values.get("protocol") == "udp"
            and values.get("dst-port") == str(listen_port)
            and values.get("in-interface-list") == "WAN"
        ):
            accept_index = index
        is_final_input_drop = (
            action == "drop"
            and (
                values.get("in-interface-list") == "!LAN"
                or "drop all not coming from LAN" in record
            )
        )
        if drop_index is None and is_final_input_drop:
            drop_index = index
    found = accept_index is not None and (drop_index is None or accept_index < drop_index)
    return {"found": found, "accept_index": accept_index, "drop_index": drop_index}


def detect_forward_vpn_to_lan_rule(output: str, vpn_subnet: str, lan_subnet: str) -> Dict[str, Any]:
    for index, record in enumerate(split_routeros_records(output)):
        values = parse_key_values(record)
        if values.get("chain") != "forward" or values.get("disabled", "no").lower() in {"yes", "true"}:
            continue
        if (
            values.get("action") == "accept"
            and address_or_network_matches(values.get("src-address", ""), vpn_subnet)
            and address_or_network_matches(values.get("dst-address", ""), lan_subnet)
        ):
            return {"found": True, "index": index}
    return {"found": False, "index": None}


def address_or_network_matches(actual: str, expected: str) -> bool:
    if actual == expected:
        return True
    try:
        return ipaddress.ip_network(actual, strict=False) == ipaddress.ip_network(expected, strict=False)
    except ValueError:
        return False


def parse_iperf3_summary_mbps(output: str) -> Optional[float]:
    candidates: List[Tuple[float, str]] = []
    for line in output.splitlines():
        if "[SUM]" not in line:
            continue
        match = re.search(r"([\d.]+)\s+([KMG])bits/sec\s+(?:sender|receiver)", line)
        if not match:
            continue
        value = float(match.group(1))
        unit = match.group(2)
        mbps = value / 1000 if unit == "K" else value * 1000 if unit == "G" else value
        candidates.append((mbps, line))
    if not candidates:
        return None
    receivers = [mbps for mbps, line in candidates if "receiver" in line]
    return receivers[-1] if receivers else candidates[-1][0]


def build_ping_command(target_ip: str) -> List[str]:
    return ["ping", "-n", "2", target_ip]


def build_tcp_test_command(target_ip: str, port: int) -> List[str]:
    return [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Test-NetConnection -ComputerName {target_ip} -Port {int(port)} -InformationLevel Quiet",
    ]


def build_iperf_command(server_ip: str, duration: int, omit: int, parallel: int, reverse: bool = False) -> List[str]:
    command = ["iperf3", "-c", server_ip, "-t", str(duration), "-O", str(omit), "-P", str(parallel)]
    if reverse:
        command.append("-R")
    return command


def run_subprocess(command: List[str], timeout: int) -> Tuple[bool, str, str]:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, shell=False)
    return completed.returncode == 0, completed.stdout, completed.stderr


def countdown_progress(label: str, seconds: int, stop_event: threading.Event) -> None:
    if seconds <= 0:
        return
    start = monotonic()
    while not stop_event.is_set():
        elapsed = int(monotonic() - start)
        remaining = max(seconds - elapsed, 0)
        print(f"\r{label} running... {remaining:>3}s remaining", end="", flush=True)
        if remaining <= 0:
            break
        stop_event.wait(1)
    print("\r" + " " * 70 + "\r", end="", flush=True)


def run_subprocess_with_countdown(
    command: List[str],
    timeout: int,
    progress_label: str,
    progress_seconds: int,
) -> Tuple[bool, str, str]:
    stop_event = threading.Event()
    progress_thread = threading.Thread(
        target=countdown_progress,
        args=(progress_label, progress_seconds, stop_event),
        daemon=True,
    )
    progress_thread.start()
    try:
        return run_subprocess(command, timeout=timeout)
    finally:
        stop_event.set()
        progress_thread.join(timeout=2)


def evaluate_day12_result(
    checks: Dict[str, str],
    run_iperf: bool = False,
    expect_connected: bool = False,
    report_data: Optional[Dict[str, Any]] = None,
) -> Tuple[str, List[str], List[str]]:
    warnings: List[str] = []
    errors: List[str] = []

    if report_data is not None and private_key_leaked(report_data):
        errors.append("PrivateKey leaked into report data.")

    fail_always = {
        "wg_interface_exists": "WireGuard interface is missing.",
        "peer_exists": "WireGuard peer is missing.",
        "peer_allowed_address": "WireGuard peer allowed-address does not match the expected client address.",
        "client_config_generated": "WireGuard client config export failed.",
        "config_file_written": "WireGuard config file was not written.",
        "private_key_redacted_in_report": "PrivateKey was not redacted in report.",
    }
    for key, message in fail_always.items():
        if checks.get(key) == "FAIL":
            errors.append(message)

    warn_default = {
        "firewall_udp_input_allow": "Firewall UDP input allow rule is missing.",
        "firewall_forward_vpn_to_lan": "Firewall VPN-to-LAN forward rule is missing.",
        "handshake_seen": "WireGuard handshake has not been seen yet.",
        "peer_rx_tx_nonzero": "WireGuard peer rx/tx counters are zero.",
        "ping_lan_gateway": "LAN gateway ping failed.",
        "ping_lan_host": "LAN host ping failed.",
        "tcp_5201_reachable": "TCP 5201 is not reachable.",
        "iperf_forward": "iperf forward test was not run or did not pass.",
        "iperf_reverse": "iperf reverse test was not run or did not pass.",
        "initial_handshake_seen": "Initial WireGuard handshake has not been seen yet.",
        "post_connectivity_handshake_seen": "Post-connectivity WireGuard handshake has not been seen yet.",
        "final_vpn_connectivity": "No VPN connectivity proof passed.",
    }
    for key, message in warn_default.items():
        if key in {"initial_handshake_seen", "post_connectivity_handshake_seen"} and checks.get("handshake_seen") == "PASS":
            continue
        if checks.get(key) == "FAIL":
            warnings.append(message)
        elif checks.get(key) == "WARN":
            warnings.append(message)

    connectivity_is_proven = vpn_connectivity_proven(checks)
    if expect_connected:
        strict_keys = ["peer_rx_tx_nonzero", "ping_lan_gateway", "ping_lan_host"]
        if not connectivity_is_proven:
            strict_keys.append("handshake_seen")
        for key in strict_keys:
            if checks.get(key) in {"FAIL", "WARN"}:
                errors.append(warn_default[key])
                warnings = [warning for warning in warnings if warning != warn_default[key]]
        if checks.get("final_vpn_connectivity") == "FAIL":
            errors.append(warn_default["final_vpn_connectivity"])
            warnings = [warning for warning in warnings if warning != warn_default["final_vpn_connectivity"]]

    if run_iperf:
        for key in ("tcp_5201_reachable", "iperf_forward", "iperf_reverse"):
            if checks.get(key) == "FAIL":
                errors.append(warn_default[key])
                warnings = [warning for warning in warnings if warning != warn_default[key]]
        if checks.get("iperf_forward") == "WARN":
            warnings.append("iperf forward throughput is below threshold.")
        if checks.get("iperf_reverse") == "WARN":
            warnings.append("iperf reverse throughput is below threshold.")
    else:
        pass

    if errors:
        return "FAIL", sorted(set(warnings)), sorted(set(errors))
    if warnings:
        return "WARN", sorted(set(warnings)), []
    return "PASS", [], []


def check_status(passed: bool, strict: bool = False) -> str:
    if passed:
        return "PASS"
    return "FAIL" if strict else "WARN"


CONNECTIVITY_PROOF_CHECKS = (
    "ping_lan_gateway",
    "ping_lan_host",
    "tcp_5201_reachable",
    "iperf_forward",
    "iperf_reverse",
)


def vpn_connectivity_proven(checks: Dict[str, str]) -> bool:
    return any(checks.get(key) == "PASS" for key in CONNECTIVITY_PROOF_CHECKS)


def peer_handshake_check_status(peer: Dict[str, Any], strict: bool, connectivity_proven: bool = False) -> str:
    if peer.get("handshake_seen"):
        return "PASS"
    if peer.get("exists") and peer.get("rx_tx_nonzero"):
        return "WARN"
    if connectivity_proven:
        return "WARN"
    return check_status(False, strict)


def peer_state_summary(peer: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "exists": bool(peer.get("exists")),
        "name": peer.get("name", ""),
        "allowed_address": peer.get("allowed_address", ""),
        "latest_handshake": peer.get("latest_handshake", ""),
        "handshake_seen": bool(peer.get("handshake_seen")),
        "rx_bytes": peer.get("rx_bytes", 0),
        "tx_bytes": peer.get("tx_bytes", 0),
        "rx_tx_nonzero": bool(peer.get("rx_tx_nonzero")),
    }


def console_color(text: Any, color_code: str) -> str:
    value = str(text)
    if not sys.stdout.isatty():
        return value
    return f"\033[{color_code}m{value}\033[0m"


def color_status(status: str) -> str:
    normalized = str(status).upper()
    if normalized == "PASS":
        return console_color("PASS", "32;1")
    if normalized == "WARN":
        return console_color("WARN", "33;1")
    if normalized == "FAIL":
        return console_color("FAIL", "31;1")
    if normalized in {"SKIP", "SKIPPED"}:
        return console_color("SKIP", "90;1")
    return str(status)


def console_stage(step: int, total: int, message: str) -> None:
    print(f"{console_color(f'Step {step}/{total}', '36;1')} {message}")


def console_check(label: str, status: str, detail: str = "") -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"  [{color_status(status)}] {label}{suffix}")


def console_summary(report: Dict[str, Any]) -> None:
    checks = report.get("checks", {})
    pass_count = sum(1 for status in checks.values() if status == "PASS")
    warn_count = sum(1 for status in checks.values() if status == "WARN")
    fail_count = sum(1 for status in checks.values() if status == "FAIL")
    skip_count = sum(1 for status in checks.values() if status == "SKIP")
    print()
    print(f"{console_color('Day12 summary', '36;1')}: {color_status(report.get('overall_result', 'UNKNOWN'))}")
    print(
        f"  Checks: {color_status('PASS')}={pass_count} "
        f"{color_status('WARN')}={warn_count} {color_status('FAIL')}={fail_count} "
        f"{color_status('SKIP')}={skip_count}"
    )
    if report.get("wireguard_summary", {}).get("exported_config_path"):
        print(f"  Config path: {report['wireguard_summary']['exported_config_path']}")
    if report.get("errors"):
        print(f"  {color_status('FAIL')} errors:")
        for error in report["errors"]:
            print(f"    - {error}")
    if report.get("warnings"):
        print(f"  {color_status('WARN')} warnings:")
        for warning in report["warnings"][:8]:
            print(f"    - {warning}")
        if len(report["warnings"]) > 8:
            print(f"    - ... {len(report['warnings']) - 8} more warnings in report")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Day 12 {FEATURE}.")
    parser.add_argument("--device-name")
    parser.add_argument("--router-host")
    parser.add_argument("--router-username")
    parser.add_argument("--router-password")
    parser.add_argument("--router-ssh-port", type=int)
    parser.add_argument("--wg-interface")
    parser.add_argument("--peer-name")
    parser.add_argument("--client-address")
    parser.add_argument("--client-dns")
    parser.add_argument("--client-endpoint-host")
    parser.add_argument("--client-allowed-ips")
    parser.add_argument("--client-keepalive", type=int)
    parser.add_argument("--conf-filename")
    parser.add_argument("--wg-router-ip")
    parser.add_argument("--lan-subnet")
    parser.add_argument("--lan-gateway-ip")
    parser.add_argument("--lan-host-ip")
    parser.add_argument("--iperf-server-ip")
    parser.add_argument("--iperf-port", type=int)
    parser.add_argument("--iperf-duration", type=int)
    parser.add_argument("--iperf-omit", type=int)
    parser.add_argument("--iperf-parallel", type=int)
    parser.add_argument("--run-iperf", action="store_true")
    parser.add_argument("--recreate-peer", action="store_true")
    parser.add_argument("--apply-firewall-fixes", action="store_true")
    parser.add_argument("--expect-connected", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument(
        "--config",
        help="Load Day12 values from a JSON config file, for example Set_WireguardVPN_config.json.",
    )
    parser.add_argument(
        "--save-config",
        nargs="?",
        const=str(DEFAULT_DAY12_CONFIG_PATH),
        help="Save the current Day12 values to a JSON config file without secrets.",
    )
    return parser.parse_args(argv)


def load_default_router_config() -> Dict[str, Any]:
    path = Path("config.json")
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_day12_config(path_value: Optional[str]) -> Dict[str, Any]:
    if not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        raise ValueError(f"Day12 config file was not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Day12 config file is not valid JSON: {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"Day12 config file must contain a JSON object: {path}")
    return data


def prompt_value(prompt: str, default: str, validator: Optional[Any] = None) -> str:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip() or default
        try:
            return validator(raw) if validator else raw
        except ValueError as error:
            print(f"Error: {error}")


def build_config_from_args(args: argparse.Namespace) -> Day12Config:
    defaults = load_default_router_config()
    day12_values = load_day12_config(args.config)

    def saved_value(name: str, default: Any = None) -> Any:
        return day12_values.get(name, default)

    def cli_or_saved(name: str, default: Any = None) -> Any:
        value = getattr(args, name)
        return value if value not in (None, "") else saved_value(name, default)

    def resolve_text(name: str, prompt: str, default: str, validator: Optional[Any] = None) -> str:
        value = cli_or_saved(name)
        if value not in (None, ""):
            return validator(str(value)) if validator else str(value)
        if args.non_interactive:
            return validator(default) if validator else default
        return prompt_value(prompt, default, validator)

    def resolve_int(name: str, prompt: str, default: int) -> int:
        value = cli_or_saved(name)
        if value not in (None, ""):
            return int(value)
        if args.non_interactive:
            return default
        return int(prompt_value(prompt, str(default)))

    device_name = args.device_name or saved_value("device_name") or defaults.get("device_name") or "Hex-s-2025-lab01"
    host = args.router_host or saved_value("router_host") or defaults.get("host") or ""
    username = args.router_username or saved_value("router_username") or defaults.get("username") or ""
    password = args.router_password
    if password is None:
        password = defaults.get("password", "")

    if not args.non_interactive:
        if not args.device_name:
            device_name = prompt_value("Device name", device_name)
        if not host:
            host = prompt_value("RouterOS SSH host", DEFAULT_LAN_GATEWAY_IP)
        if not username:
            username = prompt_value("RouterOS SSH username", "admin")
        if password == "":
            password = getpass.getpass("RouterOS SSH password: ")

    missing = [
        name
        for name, value in (
            ("--device-name", device_name),
            ("--router-host", host),
            ("--router-username", username),
        )
        if not value
    ]
    if args.non_interactive and missing:
        raise ValueError(f"Missing required non-interactive values: {', '.join(missing)}")

    if args.non_interactive:
        conf_filename = validate_conf_filename(cli_or_saved("conf_filename", DEFAULT_CONF_FILENAME))
        run_iperf = args.run_iperf
    else:
        conf_filename = resolve_text("conf_filename", "Client config filename", DEFAULT_CONF_FILENAME, validate_conf_filename)
        if args.run_iperf:
            run_iperf = True
        else:
            run_iperf = (input("Run iperf3 throughput test? [y/N]: ").strip().lower() == "y")

    return Day12Config(
        device_name=device_name,
        router_host=host,
        router_username=username,
        router_password=password,
        router_ssh_port=int(cli_or_saved("router_ssh_port", 22)),
        wg_interface=resolve_text("wg_interface", "WireGuard interface name", DEFAULT_WG_INTERFACE),
        peer_name=resolve_text("peer_name", "Peer name", DEFAULT_PEER_NAME),
        client_address=resolve_text("client_address", "Client address", DEFAULT_CLIENT_ADDRESS),
        client_dns=resolve_text("client_dns", "Client DNS", DEFAULT_CLIENT_DNS),
        client_endpoint_host=resolve_text(
            "client_endpoint_host",
            "Client endpoint host",
            DEFAULT_CLIENT_ENDPOINT_HOST,
            validate_endpoint_host,
        ),
        client_allowed_ips=resolve_text("client_allowed_ips", "Client allowed IPs", DEFAULT_CLIENT_ALLOWED_IPS),
        client_keepalive=resolve_int("client_keepalive", "Client keepalive", DEFAULT_KEEPALIVE),
        conf_filename=conf_filename,
        wg_router_ip=resolve_text("wg_router_ip", "WireGuard router IP", DEFAULT_WG_ROUTER_IP),
        lan_subnet=resolve_text("lan_subnet", "LAN subnet", DEFAULT_LAN_SUBNET),
        lan_gateway_ip=resolve_text("lan_gateway_ip", "LAN gateway IP", DEFAULT_LAN_GATEWAY_IP),
        lan_host_ip=resolve_text("lan_host_ip", "LAN host IP", DEFAULT_LAN_HOST_IP),
        iperf_server_ip=str(args.iperf_server_ip or saved_value("iperf_server_ip") or args.lan_host_ip or saved_value("lan_host_ip") or DEFAULT_LAN_HOST_IP),
        iperf_port=int(cli_or_saved("iperf_port", DEFAULT_IPERF_PORT)),
        iperf_duration=int(cli_or_saved("iperf_duration", DEFAULT_IPERF_DURATION)),
        iperf_omit=int(cli_or_saved("iperf_omit", DEFAULT_IPERF_OMIT)),
        iperf_parallel=int(cli_or_saved("iperf_parallel", DEFAULT_IPERF_PARALLEL)),
        run_iperf=run_iperf,
        recreate_peer=args.recreate_peer,
        apply_firewall_fixes=args.apply_firewall_fixes,
        expect_connected=args.expect_connected,
        non_interactive=args.non_interactive,
    )


def day12_config_to_saved_dict(config: Day12Config) -> Dict[str, Any]:
    return {
        "device_name": config.device_name,
        "router_host": config.router_host,
        "router_username": config.router_username,
        "router_ssh_port": config.router_ssh_port,
        "wg_interface": config.wg_interface,
        "peer_name": config.peer_name,
        "client_address": config.client_address,
        "client_dns": config.client_dns,
        "client_endpoint_host": config.client_endpoint_host,
        "client_allowed_ips": config.client_allowed_ips,
        "client_keepalive": config.client_keepalive,
        "conf_filename": config.conf_filename,
        "wg_router_ip": config.wg_router_ip,
        "lan_subnet": config.lan_subnet,
        "lan_gateway_ip": config.lan_gateway_ip,
        "lan_host_ip": config.lan_host_ip,
        "iperf_server_ip": config.iperf_server_ip,
        "iperf_port": config.iperf_port,
        "iperf_duration": config.iperf_duration,
        "iperf_omit": config.iperf_omit,
        "iperf_parallel": config.iperf_parallel,
    }


def write_day12_config(config: Day12Config, path_value: str) -> Path:
    path = Path(path_value)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(day12_config_to_saved_dict(config), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def run_allowlisted_read(client: paramiko.SSHClient, command: str) -> str:
    if command not in READ_COMMANDS:
        raise ValueError(f"RouterOS read command is not allowlisted: {command}")
    return run_raw_command(client, command)


def run_allowlisted_write(client: paramiko.SSHClient, command: str) -> str:
    allowed = (
        command.startswith("/interface/wireguard/peers/add ")
        or command.startswith("/interface/wireguard/peers/remove [find name=")
        or command.startswith("/ip/firewall/filter/add chain=input action=accept protocol=udp ")
        or command.startswith("/ip/firewall/filter/add chain=forward action=accept ")
    )
    if not allowed:
        raise ValueError(f"RouterOS write command is not allowlisted: {command}")
    return run_raw_command(client, command)


def show_client_config(client: paramiko.SSHClient, peer_name: str) -> str:
    command = f"/interface/wireguard/peers/show-client-config [find name={quote_routeros_value(peer_name)}]"
    return run_raw_command(client, command)


def find_interface(outputs: Dict[str, str], config: Day12Config) -> Dict[str, Any]:
    for item in parse_wireguard_interfaces(outputs.get("wireguard", "")):
        if item.get("name") == config.wg_interface:
            return item
    return {}


def output_contains_interface_ip(address_output: str, interface_name: str, expected_ip: str) -> bool:
    for record in split_routeros_records(address_output):
        values = parse_key_values(record)
        if values.get("interface") == interface_name and values.get("address") == expected_ip:
            return True
    return False


def allowed_ips_include(actual: str, expected_csv: str) -> bool:
    actual_set = {part.strip() for part in actual.split(",") if part.strip()}
    expected_set = {part.strip() for part in expected_csv.split(",") if part.strip()}
    return expected_set.issubset(actual_set)


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    report_dir = REPORT_ROOT / sanitize_path_name(str(report["device_name"]))
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "day12_wireguard_vpn_automation_report.json"
    html_path = report_dir / "day12_wireguard_vpn_automation_report.html"
    if private_key_leaked(report):
        report = redact_private_keys(report)
        report["overall_result"] = "FAIL"
        report.setdefault("errors", []).append("PrivateKey leaked into report before write.")
        report.setdefault("checks", {})["private_key_redacted_in_report"] = "FAIL"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(build_html_report(report), encoding="utf-8")
    return json_path, html_path


def build_html_report(report: Dict[str, Any]) -> str:
    wireguard_summary = report.get("wireguard_summary", {})
    exported_config_path = ""
    if isinstance(wireguard_summary, dict):
        exported_config_path = str(wireguard_summary.get("exported_config_path", ""))
    rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td class='{html.escape(str(status).lower())}'>{html.escape(str(status))}</td></tr>"
        for name, status in report.get("checks", {}).items()
    )
    warnings = "".join(f"<li>{html.escape(item)}</li>" for item in report.get("warnings", [])) or "<li>None</li>"
    errors = "".join(f"<li>{html.escape(item)}</li>" for item in report.get("errors", [])) or "<li>None</li>"
    suggestions = "".join(f"<pre>{html.escape(item)}</pre>" for item in report.get("suggestions", [])) or "<p>None</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>WireGuard VPN Automation</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2937; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: 700; }}
    .pass {{ color: #047857; }} .warn {{ color: #b45309; }} .fail {{ color: #b91c1c; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    td, th {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
    pre {{ background: #f3f4f6; padding: 10px; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>WireGuard VPN Automation</h1>
  <p><strong>Device:</strong> {html.escape(str(report.get("device_name", "")))}</p>
  <p><strong>Result:</strong> <span class="badge {html.escape(str(report.get("overall_result", "")).lower())}">{html.escape(str(report.get("overall_result", "")))}</span></p>
  <h2>Exported Config</h2>
  <p><strong>Path:</strong> {html.escape(exported_config_path)}</p>
  <h2>Checks</h2>
  <table><tbody>{rows}</tbody></table>
  <h2>Warnings</h2><ul>{warnings}</ul>
  <h2>Errors</h2><ul>{errors}</ul>
  <h2>Suggestions</h2>{suggestions}
</body>
</html>
"""


def make_initial_report(config: Day12Config) -> Dict[str, Any]:
    return {
        "device_name": config.device_name,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "day": 12,
        "feature": FEATURE,
        "overall_result": "FAIL",
        "wireguard_summary": {
            "interface_name": config.wg_interface,
            "listen_port": "",
            "interface_ip": config.wg_router_ip,
            "peer_name": config.peer_name,
            "client_address": config.client_address,
            "client_dns": config.client_dns,
            "client_endpoint_host": endpoint_host_only(config.client_endpoint_host),
            "client_allowed_ips": config.client_allowed_ips,
            "exported_config_path": str(EXPORT_ROOT / config.conf_filename),
        },
        "checks": {
            name: "WARN"
            for name in (
                "wg_interface_exists",
                "wg_interface_running",
                "wg_interface_ip_exists",
                "peer_exists",
                "peer_allowed_address",
                "client_config_generated",
                "config_file_written",
                "private_key_redacted_in_report",
                "firewall_udp_input_allow",
                "firewall_forward_vpn_to_lan",
                "initial_handshake_seen",
                "handshake_seen",
                "post_connectivity_handshake_seen",
                "peer_rx_tx_nonzero",
                "ping_lan_gateway",
                "ping_lan_host",
                "tcp_5201_reachable",
                "iperf_forward",
                "iperf_reverse",
                "final_vpn_connectivity",
            )
        },
        "iperf_summary": {},
        "warnings": [],
        "errors": [],
        "suggestions": [],
        "sanitized_client_config_summary": "",
    }


def run(config: Day12Config) -> Tuple[Dict[str, Any], Path, Path]:
    report = make_initial_report(config)
    client: Optional[paramiko.SSHClient] = None
    strict_connected = config.expect_connected or config.run_iperf
    total_steps = 7
    try:
        console_stage(1, total_steps, f"Connecting to MikroTik SSH host {config.router_host}:{config.router_ssh_port}")
        day2_config = Day2Config(
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
        client = connect_ssh_with_auth_retry(day2_config)
        console_check("SSH connection", "PASS", config.router_host)

        console_stage(2, total_steps, "Collecting RouterOS WireGuard, address, and firewall state")
        outputs = {
            "wireguard": run_allowlisted_read(client, "/interface/wireguard/print detail"),
            "peers": run_allowlisted_read(client, "/interface/wireguard/peers/print detail"),
            "addresses": run_allowlisted_read(client, "/ip/address/print detail"),
            "firewall": run_allowlisted_read(client, "/ip/firewall/filter/print detail"),
        }
        console_check("RouterOS read commands", "PASS", "allowlisted commands only")

        console_stage(3, total_steps, "Validating WireGuard interface and peer")
        interface = find_interface(outputs, config)
        listen_port = int(interface.get("listen-port", 13231)) if interface else 13231
        report["wireguard_summary"]["listen_port"] = listen_port
        report["checks"]["wg_interface_exists"] = "PASS" if interface else "FAIL"
        report["checks"]["wg_interface_running"] = "PASS" if interface and interface.get("disabled", "no") != "yes" and interface.get("running", "yes") != "no" else "FAIL"
        report["checks"]["wg_interface_ip_exists"] = "PASS" if output_contains_interface_ip(outputs["addresses"], config.wg_interface, config.wg_router_ip) else "FAIL"
        console_check(f"WireGuard interface {config.wg_interface} exists", report["checks"]["wg_interface_exists"])
        console_check(f"WireGuard interface {config.wg_interface} running", report["checks"]["wg_interface_running"])
        console_check(f"WireGuard interface IP {config.wg_router_ip}", report["checks"]["wg_interface_ip_exists"])

        peer = parse_wireguard_peer_detail(outputs["peers"], config.peer_name)
        if peer["exists"] and config.recreate_peer:
            if config.non_interactive or input(f"Remove and recreate peer {config.peer_name}? Type YES: ").strip() == "YES":
                run_allowlisted_write(client, build_peer_remove_command(config.peer_name))
                run_allowlisted_write(
                    client,
                    build_peer_add_command(
                        config.wg_interface,
                        config.peer_name,
                        config.client_address,
                        config.client_dns,
                        config.client_endpoint_host,
                        config.client_allowed_ips,
                        config.client_keepalive,
                    ),
                )
                outputs["peers"] = run_allowlisted_read(client, "/interface/wireguard/peers/print detail")
                peer = parse_wireguard_peer_detail(outputs["peers"], config.peer_name)
        elif not peer["exists"]:
            report["suggestions"].append(
                build_peer_add_command(
                    config.wg_interface,
                    config.peer_name,
                    config.client_address,
                    config.client_dns,
                    config.client_endpoint_host,
                    config.client_allowed_ips,
                    config.client_keepalive,
                )
            )

        report["checks"]["peer_exists"] = "PASS" if peer["exists"] else "FAIL"
        report["checks"]["peer_allowed_address"] = "PASS" if address_or_network_matches(peer.get("allowed_address", ""), config.client_address) else "FAIL"
        report["wireguard_summary"]["initial_peer_state"] = peer_state_summary(peer)
        report["checks"]["initial_handshake_seen"] = peer_handshake_check_status(peer, strict_connected)
        report["checks"]["handshake_seen"] = report["checks"]["initial_handshake_seen"]
        report["checks"]["peer_rx_tx_nonzero"] = check_status(peer["rx_tx_nonzero"], strict_connected)
        console_check(f"WireGuard peer {config.peer_name} exists", report["checks"]["peer_exists"])
        console_check("Peer allowed address", report["checks"]["peer_allowed_address"], config.client_address)
        console_check("Initial peer handshake seen", report["checks"]["initial_handshake_seen"])
        console_check("Peer rx/tx nonzero", report["checks"]["peer_rx_tx_nonzero"])

        console_stage(4, total_steps, "Checking firewall rules")
        udp = detect_firewall_udp_allow_before_drop(outputs["firewall"], listen_port)
        vpn_subnet = config.client_allowed_ips.split(",", 1)[0]
        lan_subnet = config.lan_subnet
        forward = detect_forward_vpn_to_lan_rule(outputs["firewall"], vpn_subnet.strip(), lan_subnet.strip())
        report["checks"]["firewall_udp_input_allow"] = "PASS" if udp["found"] else "WARN"
        report["checks"]["firewall_forward_vpn_to_lan"] = "PASS" if forward["found"] else "WARN"
        console_check(f"Firewall input UDP {listen_port} allow before drop", report["checks"]["firewall_udp_input_allow"])
        console_check("Firewall forward VPN to LAN allow", report["checks"]["firewall_forward_vpn_to_lan"])
        if not udp["found"]:
            report["suggestions"].append(
                f'/ip/firewall/filter/add chain=input action=accept protocol=udp in-interface-list=WAN dst-port={listen_port} comment="day12 allow wireguard udp"'
            )
        if not forward["found"]:
            report["suggestions"].append(
                f'/ip/firewall/filter/add chain=forward action=accept src-address={vpn_subnet.strip()} dst-address={lan_subnet.strip()} comment="day12 allow wireguard to LAN"'
            )

        console_stage(5, total_steps, f"Exporting WireGuard client config to {EXPORT_ROOT / config.conf_filename}")
        if peer["exists"]:
            client_config = show_client_config(client, config.peer_name)
            parsed_config = parse_wireguard_client_config(client_config)
            report["checks"]["client_config_generated"] = "PASS" if parsed_config["valid"] else "FAIL"
            export_path = build_export_path(config.conf_filename)
            export_path.write_text(client_config, encoding="utf-8")
            report["checks"]["config_file_written"] = "PASS"
            report["wireguard_summary"]["exported_config_path"] = str(export_path)
            report["sanitized_client_config_summary"] = sanitize_client_config_for_report(client_config)
            report["checks"]["private_key_redacted_in_report"] = "PASS" if not private_key_leaked(report) else "FAIL"
            print(f"Exported WireGuard config to {export_path}")
            print("PrivateKey: REDACTED")
            console_check("Client config generated", report["checks"]["client_config_generated"])
            console_check("Config file written", report["checks"]["config_file_written"], str(export_path))
            console_check("PrivateKey redacted in reports", report["checks"]["private_key_redacted_in_report"])
            if not strict_connected and not config.non_interactive:
                print()
                answer = input(
                    "Do you want to import/activate this WireGuard config now and run connectivity checks? [y/N]: "
                ).strip().lower()
                if answer == "y":
                    print(f"Config file: {export_path}")
                    input("Import it into WireGuard, click Activate, then press Enter here to continue...")
                    strict_connected = True
                    outputs["peers"] = run_allowlisted_read(client, "/interface/wireguard/peers/print detail")
                    peer = parse_wireguard_peer_detail(outputs["peers"], config.peer_name)
                    report["wireguard_summary"]["initial_peer_state"] = peer_state_summary(peer)
                    report["checks"]["initial_handshake_seen"] = peer_handshake_check_status(peer, strict_connected)
                    report["checks"]["handshake_seen"] = report["checks"]["initial_handshake_seen"]
                    report["checks"]["peer_rx_tx_nonzero"] = check_status(peer["rx_tx_nonzero"], strict_connected)
                    console_check("Initial peer handshake seen after activation", report["checks"]["initial_handshake_seen"])
                    console_check("Peer rx/tx nonzero after activation", report["checks"]["peer_rx_tx_nonzero"])
        else:
            console_check("Client config generated", "FAIL", "peer does not exist")

        if strict_connected:
            console_stage(6, total_steps, "Running local connectivity checks")
            report["checks"]["ping_lan_gateway"] = run_connectivity_check(build_ping_command(config.lan_gateway_ip), strict_connected)
            console_check(f"Ping LAN gateway {config.lan_gateway_ip}", report["checks"]["ping_lan_gateway"])
            report["checks"]["ping_lan_host"] = run_connectivity_check(build_ping_command(config.lan_host_ip), strict_connected)
            console_check(f"Ping LAN host {config.lan_host_ip}", report["checks"]["ping_lan_host"])
            report["checks"]["tcp_5201_reachable"] = run_tcp_5201_check(
                build_tcp_test_command(config.iperf_server_ip, config.iperf_port),
                config.run_iperf,
                timeout=45,
            )
            console_check(f"TCP {config.iperf_port} to iperf server {config.iperf_server_ip}", report["checks"]["tcp_5201_reachable"])
        else:
            console_stage(6, total_steps, "Skipping local connectivity checks until config is imported")
            report["checks"]["ping_lan_gateway"] = "SKIP"
            report["checks"]["ping_lan_host"] = "SKIP"
            report["checks"]["tcp_5201_reachable"] = "SKIP"
            console_check("Ping LAN gateway", "SKIP", "run again with --expect-connected after importing the config")
            console_check("Ping LAN host", "SKIP", "run again with --expect-connected after importing the config")
            console_check("TCP 5201", "SKIP", "run again with --run-iperf after importing the config")

        console_stage(7, total_steps, "Handling iperf3 throughput test and reports")
        if config.run_iperf and report["checks"]["tcp_5201_reachable"] == "PASS":
            run_iperf_tests(config, report)
        elif config.run_iperf:
            report["checks"]["iperf_forward"] = "SKIP"
            report["checks"]["iperf_reverse"] = "SKIP"
            console_check("iperf3 forward", "SKIP", "TCP 5201 precheck did not pass")
            console_check("iperf3 reverse", "SKIP", "TCP 5201 precheck did not pass")
        elif not config.run_iperf:
            report["checks"]["iperf_forward"] = "SKIP"
            report["checks"]["iperf_reverse"] = "SKIP"
            console_check("iperf3 forward", "SKIP", "not requested")
            console_check("iperf3 reverse", "SKIP", "not requested")

        if strict_connected:
            connectivity_proven = vpn_connectivity_proven(report["checks"])
            report["checks"]["final_vpn_connectivity"] = "PASS" if connectivity_proven else "FAIL"
            console_check("Final VPN connectivity", report["checks"]["final_vpn_connectivity"])
            if peer["exists"]:
                try:
                    outputs["peers"] = run_allowlisted_read(client, "/interface/wireguard/peers/print detail")
                    peer = parse_wireguard_peer_detail(outputs["peers"], config.peer_name)
                    report["wireguard_summary"]["post_connectivity_peer_state"] = peer_state_summary(peer)
                    report["checks"]["post_connectivity_handshake_seen"] = peer_handshake_check_status(
                        peer,
                        strict_connected,
                        connectivity_proven=connectivity_proven,
                    )
                    if report["checks"]["post_connectivity_handshake_seen"] == "PASS":
                        report["checks"]["handshake_seen"] = "PASS"
                    elif connectivity_proven:
                        report["checks"]["handshake_seen"] = "WARN"
                    else:
                        report["checks"]["handshake_seen"] = report["checks"]["post_connectivity_handshake_seen"]
                    report["checks"]["peer_rx_tx_nonzero"] = check_status(peer["rx_tx_nonzero"], strict_connected)
                    console_check("Post-connectivity peer handshake seen", report["checks"]["post_connectivity_handshake_seen"])
                    console_check("Post-connectivity peer rx/tx nonzero", report["checks"]["peer_rx_tx_nonzero"])
                except Exception as error:
                    report["checks"]["post_connectivity_handshake_seen"] = "WARN"
                    report["warnings"].append(f"Could not refresh WireGuard peer state after connectivity checks: {error}")
                    console_check("Post-connectivity peer refresh", "WARN", str(error))
        else:
            report["checks"]["final_vpn_connectivity"] = "SKIP"
            report["checks"]["post_connectivity_handshake_seen"] = "SKIP"

    except Exception as error:
        print(f"{color_status('FAIL')} stopped before config export: {type(error).__name__}: {error}")
        report["errors"].append(f"{type(error).__name__}: {error}")
        report["checks"]["wg_interface_exists"] = "FAIL"
        report["checks"]["peer_exists"] = "FAIL"
        report["checks"]["client_config_generated"] = "FAIL"
        report["checks"]["config_file_written"] = "FAIL"
        report["suggestions"].append(
            "SSH connection to MikroTik failed before config export. Confirm --router-host is reachable and SSH is allowed."
        )
    finally:
        if client:
            client.close()

    result, warnings, errors = evaluate_day12_result(
        report["checks"],
        run_iperf=config.run_iperf,
        expect_connected=strict_connected,
        report_data=report,
    )
    report["overall_result"] = result
    report["warnings"] = sorted(set(report["warnings"] + warnings))
    report["errors"] = sorted(set(report["errors"] + errors))
    json_path, html_path = write_reports(report)
    console_summary(report)
    return report, json_path, html_path


def run_connectivity_check(
    command: List[str],
    strict: bool,
    positive_text: Optional[str] = None,
    timeout: int = 20,
) -> str:
    try:
        ok, stdout, _stderr = run_subprocess(command, timeout=timeout)
        if positive_text:
            ok = ok and positive_text in stdout
        return check_status(ok, strict)
    except (OSError, subprocess.TimeoutExpired):
        return "FAIL" if strict else "WARN"


def run_tcp_5201_check(command: List[str], strict: bool, timeout: int = 45) -> str:
    try:
        _ok, stdout, _stderr = run_subprocess(command, timeout=timeout)
        return check_status(stdout.strip().lower().endswith("true"), strict)
    except (OSError, subprocess.TimeoutExpired):
        return "FAIL" if strict else "WARN"


def run_iperf_tests(config: Day12Config, report: Dict[str, Any]) -> None:
    for label, reverse in (("forward", False), ("reverse", True)):
        command = build_iperf_command(
            config.iperf_server_ip,
            config.iperf_duration,
            config.iperf_omit,
            config.iperf_parallel,
            reverse,
        )
        key = f"iperf_{label}"
        summary_key = f"{label}_mbps"
        report["iperf_summary"][f"{label}_command"] = command
        report["iperf_summary"][f"{label}_threshold_mbps"] = DEFAULT_IPERF_THRESHOLD_MBPS
        if shutil.which(command[0]) is None:
            report["checks"][key] = "FAIL"
            report["iperf_summary"][f"{label}_result"] = "FAIL"
            console_check(f"iperf3 {label}", "FAIL", "iperf3 executable not found")
            continue
        try:
            ok, stdout, _stderr = run_subprocess_with_countdown(
                command,
                timeout=config.iperf_duration + config.iperf_omit + 30,
                progress_label=f"iperf3 {label}",
                progress_seconds=config.iperf_duration + config.iperf_omit,
            )
        except (OSError, subprocess.TimeoutExpired):
            ok, stdout = False, ""
        mbps = parse_iperf3_summary_mbps(stdout)
        report["iperf_summary"][summary_key] = mbps
        if not ok or mbps is None:
            report["checks"][key] = "FAIL"
        elif mbps >= DEFAULT_IPERF_THRESHOLD_MBPS:
            report["checks"][key] = "PASS"
        else:
            report["checks"][key] = "WARN"
        report["iperf_summary"][f"{label}_result"] = report["checks"][key]
        detail = f"{mbps} Mbps" if mbps is not None else "no [SUM] Mbps parsed"
        console_check(f"iperf3 {label}", report["checks"][key], detail)


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
        config = build_config_from_args(args)
        if args.save_config:
            saved_path = write_day12_config(config, args.save_config)
            print(f"Saved Day12 WireGuard VPN config to {saved_path}")
            print("Saved config does not include SSH password, PrivateKey, or exported .conf content.")
        report, json_path, html_path = run(config)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    return {"PASS": 0, "WARN": 1, "FAIL": 2}.get(report["overall_result"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
