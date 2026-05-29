import argparse
import argparse
import getpass
import html
import ipaddress
import json
import shlex
import shutil
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import paramiko


DEFAULT_DIRECTION = "WAN_TO_LAN_DNAT"
DEFAULT_DURATION = 40
DEFAULT_OMIT = 10
DEFAULT_PARALLEL = 4
DEFAULT_THRESHOLD_MBPS = 800
DEFAULT_WARN_THRESHOLD_MBPS = 700
DEFAULT_LAN_SERVER_IP = "192.168.88.254"
DEFAULT_ROUTER_SSH_PORT = 22
SUPPORTED_DIRECTIONS = {"WAN_TO_LAN_DNAT", "LAN_TO_WAN_DNAT_REPLY"}
DIRECTION_ALIASES = {
    "WAN_TO_LAN": "WAN_TO_LAN_DNAT",
    "LAN_TO_WAN": "LAN_TO_WAN_DNAT_REPLY",
}
IPERF3_PORT = 5201
WAN_INTERFACE = "ether1"


@dataclass
class Day8Config:
    device_name: str
    router_wan_ip: str
    lan_server_ip: str
    direction: str
    duration: int
    omit: int
    parallel: int
    threshold_mbps: float
    warn_threshold_mbps: float
    output_dir: Path
    skip_router_wan_ip_confirm: bool
    non_interactive: bool
    router_host: Optional[str]
    router_username: Optional[str]
    router_password: Optional[str]
    router_ssh_port: int
    skip_router_precheck: bool
    iperf3_path: str = "iperf3"
    wan_client_ip: str = ""
    interactive_input_used: bool = False


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Day 8 iperf3 Router Performance Automation."
    )
    parser.add_argument("--device-name")
    parser.add_argument("--router-wan-ip")
    parser.add_argument("--lan-server-ip")
    parser.add_argument("--direction")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--omit", type=int, default=DEFAULT_OMIT)
    parser.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL)
    parser.add_argument("--threshold-mbps", type=float, default=DEFAULT_THRESHOLD_MBPS)
    parser.add_argument(
        "--warn-threshold-mbps",
        type=float,
        default=DEFAULT_WARN_THRESHOLD_MBPS,
        help="WARN floor. PASS is >= threshold, WARN is >= warn threshold, FAIL is below it.",
    )
    parser.add_argument(
        "--wan-client-ip",
        help="WAN-side automation PC IP to show in reports. If omitted, the script tries to infer it.",
    )
    parser.add_argument("--output-dir")
    parser.add_argument("--skip-router-wan-ip-confirm", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--router-host")
    parser.add_argument("--router-username")
    parser.add_argument("--router-password")
    parser.add_argument("--router-ssh-port", type=int, default=DEFAULT_ROUTER_SSH_PORT)
    parser.add_argument("--skip-router-precheck", action="store_true")
    parser.add_argument(
        "--iperf3-path",
        default="iperf3",
        help="iperf3 executable name or full path. Default: iperf3",
    )
    return parser.parse_args(argv)


def sanitize_path_name(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("-", "_", ".") else "_" for char in value)
    return safe.strip("._") or "unknown_device"


def validate_ipv4(value: str, field_name: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a valid IPv4 address.") from error
    if address.version != 4:
        raise ValueError(f"{field_name} must be a valid IPv4 address.")
    return str(address)


def validate_direction(value: str) -> str:
    direction = value.strip().upper()
    direction = DIRECTION_ALIASES.get(direction, direction)
    if direction not in SUPPORTED_DIRECTIONS:
        raise ValueError(
            "direction must be WAN_TO_LAN_DNAT or LAN_TO_WAN_DNAT_REPLY."
        )
    return direction


def infer_wan_client_ip(router_wan_ip: str) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect((router_wan_ip, IPERF3_PORT))
            return sock.getsockname()[0]
    except OSError:
        return ""


def prompt_until_valid(
    prompt: str,
    validator: Callable[[str], str],
    default: Optional[str] = None,
) -> str:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            raw = default
        try:
            return validator(raw)
        except ValueError as error:
            print(f"Error: {error}")


def require_non_empty(value: str) -> str:
    if not value.strip():
        raise ValueError("device_name cannot be empty.")
    return value.strip()


def require_cli_value(args: argparse.Namespace, attr: str, option_name: str) -> str:
    value = getattr(args, attr)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Error: {option_name} is required in non-interactive mode.")
    return str(value).strip()


def build_config_from_args(args: argparse.Namespace) -> Day8Config:
    interactive_used = False

    if args.non_interactive:
        device_name = require_non_empty(require_cli_value(args, "device_name", "--device-name"))
        router_wan_ip = validate_ipv4(
            require_cli_value(args, "router_wan_ip", "--router-wan-ip"),
            "--router-wan-ip",
        )
        direction = validate_direction(require_cli_value(args, "direction", "--direction"))
        lan_server_ip = validate_ipv4(
            require_cli_value(args, "lan_server_ip", "--lan-server-ip"),
            "--lan-server-ip",
        )
        if not args.skip_router_precheck:
            require_cli_value(args, "router_host", "--router-host")
            require_cli_value(args, "router_username", "--router-username")
            require_cli_value(args, "router_password", "--router-password")
    else:
        if args.device_name:
            device_name = require_non_empty(args.device_name)
        else:
            interactive_used = True
            device_name = prompt_until_valid("Please input device name: ", require_non_empty)

        if args.router_wan_ip:
            router_wan_ip = validate_ipv4(args.router_wan_ip, "--router-wan-ip")
        else:
            interactive_used = True
            router_wan_ip = prompt_until_valid(
                "Please input Router WAN IP: ",
                lambda value: validate_ipv4(value, "Router WAN IP"),
            )

        if args.direction:
            direction = validate_direction(args.direction)
        else:
            interactive_used = True
            direction = prompt_until_valid(
                "Please input test direction [WAN_TO_LAN_DNAT/LAN_TO_WAN_DNAT_REPLY] (default: WAN_TO_LAN_DNAT): ",
                validate_direction,
                DEFAULT_DIRECTION,
            )

        if args.lan_server_ip:
            lan_server_ip = validate_ipv4(args.lan_server_ip, "--lan-server-ip")
        else:
            interactive_used = True
            lan_server_ip = prompt_until_valid(
                "Please input LAN iperf3 server IP (default: 192.168.88.254): ",
                lambda value: validate_ipv4(value, "LAN iperf3 server IP"),
                DEFAULT_LAN_SERVER_IP,
            )

        if not args.skip_router_precheck:
            if not args.router_host:
                interactive_used = True
                args.router_host = prompt_until_valid(
                    "Please input RouterOS SSH host: ",
                    require_non_empty,
                )
            if not args.router_username:
                interactive_used = True
                args.router_username = prompt_until_valid(
                    "Please input RouterOS SSH username: ",
                    require_non_empty,
                )
            if not args.router_password:
                interactive_used = True
                args.router_password = getpass.getpass(
                    "Please input RouterOS SSH password: "
                ).strip()
                if not args.router_password:
                    raise ValueError("Error: RouterOS SSH password is required.")

    output_dir = Path(args.output_dir) if args.output_dir else Path("reports") / sanitize_path_name(device_name)
    return Day8Config(
        device_name=device_name,
        router_wan_ip=router_wan_ip,
        lan_server_ip=lan_server_ip,
        direction=direction,
        duration=args.duration,
        omit=args.omit,
        parallel=args.parallel,
        threshold_mbps=args.threshold_mbps,
        warn_threshold_mbps=getattr(args, "warn_threshold_mbps", DEFAULT_WARN_THRESHOLD_MBPS),
        output_dir=output_dir,
        skip_router_wan_ip_confirm=args.skip_router_wan_ip_confirm,
        non_interactive=args.non_interactive,
        router_host=args.router_host,
        router_username=args.router_username,
        router_password=args.router_password,
        router_ssh_port=args.router_ssh_port,
        skip_router_precheck=args.skip_router_precheck,
        iperf3_path=getattr(args, "iperf3_path", "iperf3"),
        wan_client_ip=(
            validate_ipv4(args.wan_client_ip, "--wan-client-ip")
            if getattr(args, "wan_client_ip", None)
            else infer_wan_client_ip(router_wan_ip)
        ),
        interactive_input_used=interactive_used,
    )


def confirm_router_wan_ip(config: Day8Config) -> bool:
    if config.skip_router_wan_ip_confirm:
        return True
    print()
    print("You are going to run iperf3 against Router WAN IP:")
    print(config.router_wan_ip)
    print()
    print("For WAN_TO_LAN_DNAT:")
    print("WAN PC -> Router WAN IP:5201 -> DNAT -> LAN server IP:5201")
    print()
    print("For LAN_TO_WAN_DNAT_REPLY:")
    print("WAN PC controls the same DNAT test, but -R makes LAN server send reply-direction traffic back to WAN PC.")
    print()
    answer = input("Please confirm Router WAN IP is correct. Type YES to continue: ").strip()
    return answer.upper() == "YES"


def build_iperf3_command(
    router_wan_ip: str,
    direction: str,
    duration: int,
    parallel: int,
    omit: int,
    iperf3_path: str = "iperf3",
) -> List[str]:
    normalized_direction = validate_direction(direction)
    command = [
        iperf3_path,
        "-c",
        router_wan_ip,
        "-t",
        str(duration),
        "-P",
        str(parallel),
    ]
    if normalized_direction == "LAN_TO_WAN_DNAT_REPLY":
        command.append("-R")
    command.extend(["-O", str(omit), "-J"])
    return command


def parse_iperf3_json(data: Dict[str, Any]) -> Dict[str, Any]:
    end = data.get("end")
    if not isinstance(end, dict):
        raise ValueError("iperf3 JSON is missing end object.")

    for section_name in ("sum_received", "sum_sent"):
        section = end.get(section_name)
        if not isinstance(section, dict):
            continue
        value = section.get("bits_per_second")
        if value is None:
            continue
        try:
            bps = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"iperf3 JSON field end.{section_name}.bits_per_second is not numeric."
            ) from error
        return {
            "throughput_mbps": bps / 1_000_000,
            "source_field": f"end.{section_name}.bits_per_second",
        }

    raise ValueError(
        "iperf3 JSON is missing end.sum_received.bits_per_second and "
        "end.sum_sent.bits_per_second."
    )


def countdown_progress(stop_event: threading.Event, seconds: int) -> None:
    if not sys.stdout.isatty():
        return
    for remaining in range(seconds, 0, -1):
        if stop_event.is_set():
            break
        print(f"\riperf3 running... {remaining:>3}s remaining", end="", flush=True)
        stop_event.wait(1)
    if not stop_event.is_set():
        print("\riperf3 finishing...                       ", end="", flush=True)


def run_iperf3(
    command: List[str],
    timeout: int,
    progress_seconds: Optional[int] = None,
) -> Tuple[str, Optional[Dict[str, Any]], Optional[str], str]:
    executable = command[0]
    if shutil.which(executable) is None:
        return (
            "FAIL",
            None,
            (
                f"iperf3 executable was not found: {executable}. "
                "Run 'where iperf3' in PowerShell/CMD, then either add that folder "
                "to PATH or pass the full path with --iperf3-path."
            ),
            "",
        )
    stop_event = threading.Event()
    progress_thread: Optional[threading.Thread] = None
    if progress_seconds:
        progress_thread = threading.Thread(
            target=countdown_progress,
            args=(stop_event, progress_seconds),
            daemon=True,
        )
        progress_thread.start()

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        stderr = error.stderr if isinstance(error.stderr, str) else ""
        return "FAIL", None, f"iperf3 timeout after {timeout} seconds.", stderr
    except OSError as error:
        return "FAIL", None, f"{type(error).__name__}: {error}", ""
    finally:
        stop_event.set()
        if progress_thread:
            progress_thread.join(timeout=1)
            if sys.stdout.isatty():
                print("\r" + " " * 48 + "\r", end="", flush=True)

    stderr = completed.stderr or ""
    if completed.returncode != 0:
        error = f"iperf3 failed with return code {completed.returncode}."
        if stderr.strip():
            error = f"{error} stderr: {stderr.strip()}"
        return "FAIL", None, error, stderr

    try:
        parsed_json = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        return "FAIL", None, f"iperf3 JSON parse error: {error}", stderr

    try:
        parsed = parse_iperf3_json(parsed_json)
    except ValueError as error:
        return "FAIL", None, str(error), stderr
    return "PASS", parsed, None, stderr


def parse_routeros_records(output: str) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    blocks: List[str] = []
    current_lines: List[str] = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("Flags:", "Columns:", "#", ";;;")):
            continue
        starts_record = bool(line.split() and line.split()[0].isdigit())
        if starts_record and current_lines:
            blocks.append(" ".join(current_lines))
            current_lines = [line]
        elif starts_record:
            current_lines = [line]
        elif current_lines:
            current_lines.append(line)
        else:
            blocks.append(line)

    if current_lines:
        blocks.append(" ".join(current_lines))

    for block in blocks:
        record: Dict[str, str] = {}
        for token in shlex.split(block, posix=False):
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            record[key] = value.strip('"')
        if record:
            records.append(record)
    return records


def output_contains_ip(output: str, ip_address: str) -> bool:
    return ip_address in output


def dst_nat_found(output: str, lan_server_ip: str) -> bool:
    for record in parse_routeros_records(output):
        if (
            record.get("chain") == "dstnat"
            and record.get("protocol") == "tcp"
            and record.get("dst-port") == str(IPERF3_PORT)
            and record.get("to-addresses") == lan_server_ip
            and record.get("to-ports") == str(IPERF3_PORT)
            and record.get("disabled", "no").lower() not in {"yes", "true"}
        ):
            return True
    return False


def firewall_filter_allow_found(output: str, lan_server_ip: str) -> bool:
    for record in parse_routeros_records(output):
        if (
            record.get("chain") == "forward"
            and record.get("action") == "accept"
            and record.get("protocol") == "tcp"
            and record.get("dst-address") == lan_server_ip
            and record.get("dst-port") == str(IPERF3_PORT)
            and record.get("disabled", "no").lower() not in {"yes", "true"}
        ):
            return True
    return False


def fasttrack_found(output: str) -> bool:
    return "action=fasttrack-connection" in output


def parse_ether1_monitor(output: str) -> Dict[str, Any]:
    records = parse_routeros_records(output)
    values = records[0] if records else {}
    if not values:
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip()] = value.strip()
    rate = values.get("rate", "")
    full_duplex = values.get("full-duplex", "").lower() == "yes"
    status = values.get("status", "")
    return {
        "status": status,
        "rate": rate,
        "full_duplex": full_duplex,
        "link_ok": status == "link-ok" and rate == "1Gbps" and full_duplex,
    }


def suggested_dnat_command(lan_server_ip: str) -> str:
    return (
        "/ip firewall nat add chain=dstnat in-interface=ether1 protocol=tcp "
        "dst-port=5201 action=dst-nat "
        f"to-addresses={lan_server_ip} to-ports=5201 "
        'comment="day8 iperf3 WAN to LAN dst-nat"'
    )


def suggested_filter_command(lan_server_ip: str) -> str:
    return (
        "/ip firewall filter add chain=forward in-interface=ether1 protocol=tcp "
        f"dst-address={lan_server_ip} dst-port=5201 action=accept "
        'comment="day8 allow iperf3 WAN to LAN"'
    )


def empty_precheck_result(enabled: bool) -> Dict[str, Any]:
    return {
        "enabled": enabled,
        "result": "SKIP" if not enabled else "FAIL",
        "errors": [],
        "warnings": [],
        "checks": {
            "router_wan_ip_found": False,
            "dst_nat_found": False,
            "firewall_filter_allow_found": False,
            "fasttrack_found": False,
            "ether1_link_ok": False,
            "ether1_rate": "",
            "ether1_full_duplex": False,
        },
        "suggested_mikrotik_commands": [],
        "suggested_manual_checks": [],
    }


def run_routeros_command(client: paramiko.SSHClient, command: str) -> str:
    _stdin, stdout, stderr = client.exec_command(command)
    stdout_text = stdout.read().decode("utf-8", errors="replace")
    stderr_text = stderr.read().decode("utf-8", errors="replace")
    if stderr_text.strip():
        raise RuntimeError(f"RouterOS command failed: {command}: {stderr_text.strip()}")
    return stdout_text


def connect_routeros(host: str, username: str, password: str, port: int) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
        timeout=10,
    )
    return client


def evaluate_routeros_outputs(outputs: Dict[str, str], router_wan_ip: str, lan_server_ip: str) -> Dict[str, Any]:
    result = empty_precheck_result(enabled=True)
    errors = result["errors"]
    warnings = result["warnings"]
    checks = result["checks"]
    suggested_commands = result["suggested_mikrotik_commands"]
    manual_checks = result["suggested_manual_checks"]

    checks["router_wan_ip_found"] = output_contains_ip(outputs.get("addresses", ""), router_wan_ip)
    checks["dst_nat_found"] = dst_nat_found(outputs.get("dst_nat", ""), lan_server_ip)
    checks["firewall_filter_allow_found"] = firewall_filter_allow_found(
        outputs.get("forward_filter", ""),
        lan_server_ip,
    )
    checks["fasttrack_found"] = fasttrack_found(outputs.get("fasttrack", ""))
    ether1 = parse_ether1_monitor(outputs.get("ether1", ""))
    checks["ether1_link_ok"] = ether1["link_ok"]
    checks["ether1_rate"] = ether1["rate"]
    checks["ether1_full_duplex"] = ether1["full_duplex"]

    if not checks["router_wan_ip_found"]:
        errors.append(f"Router WAN IP {router_wan_ip} was not found in RouterOS address list.")
        manual_checks.append("/ip address print")
    if not checks["dst_nat_found"]:
        errors.append(f"Missing dst-nat TCP/5201 rule to {lan_server_ip}:5201.")
        suggested_commands.append(suggested_dnat_command(lan_server_ip))
    if not checks["firewall_filter_allow_found"]:
        errors.append(f"Missing firewall forward accept TCP/5201 rule to {lan_server_ip}.")
        suggested_commands.append(suggested_filter_command(lan_server_ip))
    if not checks["fasttrack_found"]:
        warnings.append("FastTrack rule was not found.")
        manual_checks.append("/ip firewall filter print detail where action=fasttrack-connection")
    if not checks["ether1_link_ok"]:
        warnings.append("ether1 is not reporting 1Gbps full-duplex link-ok.")
        manual_checks.append("/interface ethernet monitor ether1 once")

    result["result"] = "FAIL" if errors else "PASS"
    return result


def run_routeros_precheck(config: Day8Config) -> Dict[str, Any]:
    if config.skip_router_precheck:
        return empty_precheck_result(enabled=False)

    client: Optional[paramiko.SSHClient] = None
    try:
        client = connect_routeros(
            host=str(config.router_host),
            username=str(config.router_username),
            password=str(config.router_password),
            port=config.router_ssh_port,
        )
        outputs = {
            "addresses": run_routeros_command(client, "/ip address print detail"),
            "dst_nat": run_routeros_command(
                client,
                "/ip firewall/nat print detail where chain=dstnat",
            ),
            "forward_filter": run_routeros_command(
                client,
                "/ip firewall/filter print detail where chain=forward",
            ),
            "fasttrack": run_routeros_command(
                client,
                "/ip firewall/filter print detail where action=fasttrack-connection",
            ),
            "ether1": run_routeros_command(client, "/interface ethernet monitor ether1 once"),
        }
        return evaluate_routeros_outputs(outputs, config.router_wan_ip, config.lan_server_ip)
    except (
        paramiko.AuthenticationException,
        paramiko.SSHException,
        socket.timeout,
        TimeoutError,
        OSError,
        RuntimeError,
    ) as error:
        result = empty_precheck_result(enabled=True)
        result["result"] = "FAIL"
        result["errors"].append(f"RouterOS SSH precheck failed: {type(error).__name__}: {error}")
        result["suggested_manual_checks"].extend(
            [
                "Confirm --router-host is reachable from the WAN-side PC.",
                "If running from the WAN-side PC, use a RouterOS SSH IP reachable from that PC, for example the Router WAN IP when WAN SSH is allowed.",
                "To run iperf3 without RouterOS SSH validation, add --skip-router-precheck.",
                "/ip service print detail where name=ssh",
                "/ip firewall filter print detail where chain=input",
            ]
        )
        return result
    finally:
        if client:
            client.close()


def direction_metadata(direction: str) -> Dict[str, Any]:
    normalized = validate_direction(direction)
    reverse = normalized == "LAN_TO_WAN_DNAT_REPLY"
    if reverse:
        return {
            "control_connection": "WAN_PC_TO_ROUTER_WAN_IP",
            "traffic_direction": "LAN server to WAN client over iperf3 reverse mode",
            "requires_dnat": True,
            "reverse_mode": True,
            "test_type": "DNAT reply-direction throughput",
            "description": (
                "This is iperf3 reverse mode over the same DNAT connection. "
                "The LAN iperf3 server sends reply-direction traffic back to the WAN-side client."
            ),
        }
    return {
        "control_connection": "WAN_PC_TO_ROUTER_WAN_IP",
        "traffic_direction": "WAN client to LAN server",
        "requires_dnat": True,
        "reverse_mode": False,
        "test_type": "DNAT forward throughput",
        "description": (
            "WAN-side client sends traffic to Router WAN IP, and Router DNAT forwards "
            "traffic to LAN iperf3 server."
        ),
    }


def traffic_path(config: Day8Config) -> str:
    if config.direction == "LAN_TO_WAN_DNAT_REPLY":
        return (
            f"LAN Server {config.lan_server_ip} -> Router -> "
            f"WAN PC {config.wan_client_ip or 'unknown'}"
        )
    return (
        f"WAN PC {config.wan_client_ip or 'unknown'} -> Router WAN "
        f"{config.router_wan_ip}:{IPERF3_PORT} -> DNAT -> LAN Server "
        f"{config.lan_server_ip}:{IPERF3_PORT}"
    )


def fasttrack_observation(direction: str) -> str:
    if direction == "LAN_TO_WAN_DNAT_REPLY":
        return (
            "Manual connection tracking observation: flags include F=FASTTRACK, "
            "d=DSTNAT, S=SEEN-REPLY, A=ASSURED, C=CONFIRMED. Reference rates: "
            "orig-rate around 3.9 Mbps, repl-rate around 791.5 Mbps."
        )
    return (
        "Manual connection tracking observation: flags include F=FASTTRACK, "
        "d=DSTNAT, S=SEEN-REPLY, A=ASSURED, C=CONFIRMED. Reference rates: "
        "orig-rate around 968.6 Mbps, repl-rate around 4.2 Mbps."
    )


def interpretation(direction: str) -> str:
    base = (
        "Both forward and reverse iperf3 flows are fasttracked. The lower "
        "reverse-direction throughput is not caused by missing FastTrack. Possible "
        "causes include host sender/receiver behavior, NIC flow-control, Ethernet "
        "path, RouterOS driver behavior, or DNAT reply-direction path behavior."
    )
    if direction == "LAN_TO_WAN_DNAT_REPLY":
        return (
            "This is the reverse direction of a DNAT iperf3 session. It should not "
            "be interpreted as standard outbound LAN-to-WAN SRCNAT performance. "
            + base
        )
    return (
        "This measures DNAT forward throughput from the WAN-side client to the LAN "
        "iperf3 server. "
        + base
    )


def next_validation_steps() -> List[str]:
    return [
        "Run the same direction 3 times and compare median throughput.",
        "Check RouterOS /tool profile during the iperf3 run.",
        "Check RouterOS connection tracking flags and rates.",
        "Run PC-to-PC direct iperf3 baseline without router.",
        "If standard outbound LAN-to-WAN performance is required, add a separate SRCNAT test topology.",
    ]


def base_report(config: Day8Config, command: List[str], confirmed: bool) -> Dict[str, Any]:
    metadata = direction_metadata(config.direction)
    return {
        "day": "Day 8",
        "test_name": f"iperf3_{config.direction}",
        "test_type": metadata["test_type"],
        "device_name": config.device_name,
        "direction": config.direction,
        "description": metadata["description"],
        "router_wan_ip": config.router_wan_ip,
        "lan_server_ip": config.lan_server_ip,
        "wan_client_ip": config.wan_client_ip,
        "iperf3_target_ip": config.router_wan_ip,
        "actual_server_ip": config.lan_server_ip,
        "control_connection": metadata["control_connection"],
        "traffic_direction": metadata["traffic_direction"],
        "traffic_path": traffic_path(config),
        "requires_dnat": metadata["requires_dnat"],
        "reverse_mode": metadata["reverse_mode"],
        "duration_sec": config.duration,
        "omit_sec": config.omit,
        "parallel_streams": config.parallel,
        "threshold_mbps": config.threshold_mbps,
        "warn_threshold_mbps": config.warn_threshold_mbps,
        "throughput_mbps": None,
        "throughput_source_field": None,
        "measured_field": None,
        "result": "FAIL",
        "command": " ".join(command),
        "iperf3_command": " ".join(command),
        "router_wan_ip_confirmed": confirmed,
        "interactive_input_used": config.interactive_input_used,
        "router_precheck_enabled": not config.skip_router_precheck,
        "router_precheck_result": "SKIP" if config.skip_router_precheck else "FAIL",
        "router_precheck_errors": [],
        "router_precheck_warnings": [],
        "routeros_checks": empty_precheck_result(enabled=True)["checks"],
        "suggested_mikrotik_commands": [],
        "suggested_manual_checks": [],
        "routeros_precheck_result": "SKIP" if config.skip_router_precheck else "FAIL",
        "fasttrack_observation": fasttrack_observation(config.direction),
        "interpretation": interpretation(config.direction),
        "next_action": next_validation_steps(),
        "iperf3_stderr": "",
        "error": None,
    }


def apply_precheck_to_report(report: Dict[str, Any], precheck: Dict[str, Any]) -> None:
    report["router_precheck_enabled"] = bool(precheck["enabled"])
    report["router_precheck_result"] = precheck["result"]
    report["routeros_precheck_result"] = precheck["result"]
    report["router_precheck_errors"] = precheck["errors"]
    report["router_precheck_warnings"] = precheck["warnings"]
    report["routeros_checks"] = precheck["checks"]
    report["suggested_mikrotik_commands"] = precheck["suggested_mikrotik_commands"]
    report["suggested_manual_checks"] = precheck["suggested_manual_checks"]


def evaluate_throughput_result(
    throughput_mbps: float,
    threshold_mbps: float,
    warn_threshold_mbps: float,
) -> Tuple[str, Optional[str]]:
    if throughput_mbps >= threshold_mbps:
        return "PASS", None
    if throughput_mbps >= warn_threshold_mbps:
        return (
            "WARN",
            "Throughput is below the target threshold but above the warning threshold. "
            "RouterOS connection tracking should be checked before treating this as DUT failure.",
        )
    return (
        "FAIL",
        (
            f"Throughput {throughput_mbps:.3f} Mbps is below warning threshold "
            f"{warn_threshold_mbps} Mbps."
        ),
    )


def build_html_report(report: Dict[str, Any]) -> str:
    precheck_result = str(report["router_precheck_result"]).upper()
    precheck_skipped = precheck_result in {"SKIP", "SKIPPED"}
    checks = report["routeros_checks"]
    report_direction = validate_direction(str(report.get("direction", DEFAULT_DIRECTION)))
    fallback_metadata = direction_metadata(report_direction)
    fallback_wan_client_ip = str(report.get("wan_client_ip") or "unknown")
    fallback_traffic_path = report.get("traffic_path") or (
        f"LAN Server {report.get('lan_server_ip', 'unknown')} -> Router -> WAN PC {fallback_wan_client_ip}"
        if report_direction == "LAN_TO_WAN_DNAT_REPLY"
        else (
            f"WAN PC {fallback_wan_client_ip} -> Router WAN "
            f"{report.get('router_wan_ip', 'unknown')}:{IPERF3_PORT} -> DNAT -> LAN Server "
            f"{report.get('lan_server_ip', 'unknown')}:{IPERF3_PORT}"
        )
    )

    def status_css_class(value: Any) -> str:
        normalized = str(value).strip().upper()
        if normalized in {"PASS", "TRUE", "YES"}:
            return "pass"
        if normalized in {"FAIL", "FALSE", "NO"}:
            return "fail"
        if normalized in {"SKIP", "SKIPPED", "NOT_RUN", "NONE"}:
            return "skip"
        if normalized in {"WARNING", "WARN"}:
            return "warning"
        return "info"

    def badge(value: Any, force_class: Optional[str] = None) -> str:
        text = "None" if value is None else str(value)
        css_class = force_class or status_css_class(text)
        return f'<span class="badge {css_class}">{html.escape(text)}</span>'

    def value_html(label: str, value: Any) -> str:
        if value is None or value == "":
            return '<span class="muted">None</span>'
        text = str(value)
        lower_label = label.lower()
        if "ip" in lower_label:
            return f'<span class="ip-badge">{html.escape(text)}</span>'
        if "command" in lower_label:
            return f'<pre class="code-block"><code>{html.escape(text)}</code></pre>'
        if label in {"Result", "RouterOS precheck result"}:
            return badge(text)
        if label == "Interactive input used" and isinstance(value, bool):
            return f'<span class="neutral-pill">{"TRUE" if value else "FALSE"}</span>'
        if isinstance(value, bool):
            if precheck_skipped and label in {
                "Router WAN IP found",
                "DNAT rule found",
                "Firewall filter allow rule found",
                "FastTrack found",
                "ether1 link status",
                "ether1 full duplex",
            }:
                return badge("SKIP", "skip")
            return badge("TRUE" if value else "FALSE")
        return html.escape(text)

    def row(label: str, value: Any) -> str:
        return (
            "<tr>"
            f"<th>{html.escape(label)}</th>"
            f"<td>{value_html(label, value)}</td>"
            "</tr>"
        )

    def notice_items(values: List[str], kind: str, empty_text: str) -> str:
        if not values:
            return f'<div class="notice neutral">{html.escape(empty_text)}</div>'
        items = "".join(f"<li>{html.escape(value)}</li>" for value in values)
        return f'<div class="notice {kind}"><ul>{items}</ul></div>'

    def code_blocks(values: List[str], empty_text: str) -> str:
        if not values:
            return f'<div class="notice neutral">{html.escape(empty_text)}</div>'
        return "".join(
            f'<pre class="code-block command-block"><code>{html.escape(value)}</code></pre>'
            for value in values
        )

    def check_row(label: str, value: Any, required: bool = False) -> str:
        if precheck_skipped:
            rendered = badge("SKIP", "skip")
        elif isinstance(value, bool):
            rendered = badge("PASS" if value else "FAIL" if required else "FALSE")
        elif value:
            rendered = html.escape(str(value))
        else:
            rendered = badge("SKIP", "skip")
        return f"<tr><th>{html.escape(label)}</th><td>{rendered}</td></tr>"

    if report_direction == "LAN_TO_WAN_DNAT_REPLY":
        path_steps = [
            "WAN PC controls test",
            "Router WAN IP:5201",
            "DNAT to LAN iperf3 Server",
            "Reply-direction traffic LAN -> WAN",
        ]
    else:
        path_steps = [
            "WAN PC",
            "Router WAN IP:5201",
            "DNAT",
            "LAN iperf3 Server",
        ]
    path_html = "".join(
        f'<div class="path-step">{html.escape(step)}</div>'
        + (('<div class="path-arrow">&rarr;</div>') if index < len(path_steps) - 1 else "")
        for index, step in enumerate(path_steps)
    )
    next_steps_html = "".join(
        f"<li>{html.escape(str(step))}</li>"
        for step in report.get("next_action", next_validation_steps())
    )

    precheck_note = ""
    if precheck_skipped:
        precheck_note = (
            '<div class="notice neutral">'
            "RouterOS precheck was skipped. Firewall/NAT state was not verified by this run."
            "</div>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>iperf3 Performance Report</title>
  <style>
    :root {{
      --bg: #eef2f7;
      --card: #ffffff;
      --text: #172033;
      --muted: #667085;
      --border: #d9e2ef;
      --success: #147a3d;
      --success-bg: #e8f6ee;
      --danger: #b42318;
      --danger-bg: #fdecec;
      --warning: #9a6700;
      --warning-bg: #fff4d8;
      --info: #2563eb;
      --info-bg: #dbeafe;
      --skip: #475467;
      --skip-bg: #eef2f6;
      --ink: #111827;
      --shadow: 0 14px 34px rgba(16, 24, 40, .08);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 28px 20px 52px;
    }}
    .hero {{
      background: linear-gradient(135deg, #111827 0%, #1e3a5f 58%, #0f766e 100%);
      color: #fff;
      border-radius: 14px;
      padding: 30px;
      box-shadow: var(--shadow);
      margin-bottom: 18px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(220px, .75fr);
      gap: 24px;
      align-items: end;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 32px;
      line-height: 1.15;
    }}
    h2 {{
      margin: 26px 0 12px;
      font-size: 18px;
    }}
    .eyebrow {{
      color: #bfdbfe;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .hero-meta {{
      color: #e5e7eb;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    .throughput {{
      font-size: 42px;
      font-weight: 850;
      line-height: 1;
      margin-bottom: 8px;
    }}
    .throughput-label {{
      color: #dbeafe;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 18px 0 22px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: var(--shadow);
      padding: 16px;
      min-width: 0;
    }}
    .card-label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .card-value {{
      font-size: 22px;
      font-weight: 800;
      overflow-wrap: anywhere;
    }}
    .panel {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: var(--shadow);
      padding: 18px;
      margin-bottom: 18px;
      overflow: hidden;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 12px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      width: 280px;
      color: var(--muted);
      font-weight: 700;
    }}
    tr:last-child th, tr:last-child td {{
      border-bottom: 0;
    }}
    .badge {{
      display: inline-block;
      min-width: 62px;
      padding: 4px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      text-align: center;
      white-space: nowrap;
    }}
    .pass {{
      background: var(--success-bg);
      color: var(--success);
    }}
    .fail {{
      background: var(--danger-bg);
      color: var(--danger);
    }}
    .skip {{
      background: var(--skip-bg);
      color: var(--skip);
    }}
    .warning {{
      background: var(--warning-bg);
      color: var(--warning);
    }}
    .info {{
      background: var(--info-bg);
      color: var(--info);
    }}
    .ip-badge {{
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      background: var(--info-bg);
      color: #1849a9;
      font-family: Consolas, "Courier New", monospace;
      font-weight: 700;
    }}
    .neutral-pill {{
      display: inline-block;
      padding: 4px 9px;
      border-radius: 999px;
      background: #f8fafc;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }}
    .muted {{
      color: var(--muted);
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      overflow-wrap: anywhere;
    }}
    .code-block {{
      background: var(--ink);
      color: #e5e7eb;
      border-radius: 10px;
      padding: 12px;
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      word-break: break-word;
    }}
    .command-block {{
      margin-bottom: 10px;
    }}
    .notice {{
      border-radius: 10px;
      padding: 12px 14px;
      border: 1px solid var(--border);
    }}
    .notice ul {{
      margin: 0;
      padding-left: 18px;
    }}
    .notice.danger {{
      background: var(--danger-bg);
      border-color: #f6b5b5;
      color: var(--danger);
    }}
    .notice.warning {{
      background: var(--warning-bg);
      border-color: #f3cf7a;
      color: var(--warning);
    }}
    .notice.neutral {{
      background: #f8fafc;
      color: var(--muted);
    }}
    .path {{
      display: grid;
      grid-template-columns: repeat(7, auto);
      gap: 10px;
      align-items: center;
      overflow-x: auto;
      padding-bottom: 2px;
    }}
    .path-step {{
      min-width: 130px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      font-weight: 800;
      text-align: center;
    }}
    .path-arrow {{
      color: var(--muted);
      font-size: 22px;
      font-weight: 800;
    }}
    @media (max-width: 760px) {{
      main {{
        padding: 18px 12px 36px;
      }}
      .hero {{
        padding: 22px;
      }}
      .hero-grid, .cards {{
        grid-template-columns: 1fr;
      }}
      h1 {{
        font-size: 26px;
      }}
      .throughput {{
        font-size: 34px;
      }}
      th, td {{
        display: block;
        width: 100%;
      }}
      th {{
        padding-bottom: 2px;
      }}
      td {{
        padding-top: 4px;
      }}
    }}
  </style>
</head>
<body>
<main>
  <header class="hero">
    <div class="hero-grid">
      <div>
        <div class="eyebrow">Network Automation Testing Platform</div>
        <h1>iperf3 Performance Report</h1>
        <div>{badge(report["result"])}</div>
        <div class="hero-meta">
          <span>{html.escape(str(report["device_name"]))}</span>
          <span>{html.escape(str(report_direction))}</span>
        </div>
      </div>
      <div>
        <div class="throughput-label">Throughput Mbps</div>
        <div class="throughput">{html.escape(str(report["throughput_mbps"]))}</div>
        <div>Target: {html.escape(str(report["threshold_mbps"]))} Mbps / Warn floor: {html.escape(str(report.get("warn_threshold_mbps", DEFAULT_WARN_THRESHOLD_MBPS)))} Mbps</div>
      </div>
    </div>
  </header>
  <section class="cards">
    <article class="card"><div class="card-label">Result</div><div class="card-value">{badge(report["result"])}</div></article>
    <article class="card"><div class="card-label">Throughput Mbps</div><div class="card-value">{html.escape(str(report["throughput_mbps"]))}</div></article>
    <article class="card"><div class="card-label">Direction</div><div class="card-value">{html.escape(str(report_direction))}</div></article>
    <article class="card"><div class="card-label">RouterOS Precheck</div><div class="card-value">{badge(report["router_precheck_result"])}</div></article>
  </section>
  <section class="panel">
    <h2>Test Path</h2>
    <div class="path">{path_html}</div>
  </section>
  <section class="panel">
    <h2>Test Summary</h2>
    <div class="table-wrap">
      <table>
        {row("Device name", report["device_name"])}
        {row("Test name", report["test_name"])}
        {row("Test type", report.get("test_type", fallback_metadata["test_type"]))}
        {row("Direction", report_direction)}
        {row("Traffic direction", report.get("traffic_direction", fallback_metadata["traffic_direction"]))}
        {row("Traffic path", fallback_traffic_path)}
        {row("Router WAN IP", report["router_wan_ip"])}
        {row("LAN server IP", report["lan_server_ip"])}
        {row("WAN client IP", fallback_wan_client_ip)}
        {row("iperf3 target IP", report["iperf3_target_ip"])}
        {row("Actual server IP", report["actual_server_ip"])}
        {row("Duration", report["duration_sec"])}
        {row("Omit seconds", report["omit_sec"])}
        {row("Parallel streams", report["parallel_streams"])}
        {row("Threshold Mbps", report["threshold_mbps"])}
        {row("Warn threshold Mbps", report.get("warn_threshold_mbps", DEFAULT_WARN_THRESHOLD_MBPS))}
        {row("Throughput Mbps", report["throughput_mbps"])}
        {row("Result", report["result"])}
        {row("Command", report["command"])}
        {row("iperf3 command", report["iperf3_command"])}
        {row("Measured field", report.get("measured_field", report.get("throughput_source_field")))}
        {row("routeros_precheck_result", report.get("routeros_precheck_result", report["router_precheck_result"]))}
        {row("Router WAN IP confirmed", report["router_wan_ip_confirmed"])}
        {row("Interactive input used", report["interactive_input_used"])}
        {row("FastTrack observation", report.get("fasttrack_observation", fasttrack_observation(report_direction)))}
        {row("Interpretation", report.get("interpretation", interpretation(report_direction)))}
      </table>
    </div>
  </section>
  <section class="panel">
    <h2>RouterOS Precheck</h2>
    {precheck_note}
    <div class="table-wrap">
      <table>
        {check_row("RouterOS precheck result", report["router_precheck_result"])}
        {check_row("Router WAN IP found", checks["router_wan_ip_found"], required=True)}
        {check_row("DNAT rule found", checks["dst_nat_found"], required=True)}
        {check_row("Firewall filter allow rule found", checks["firewall_filter_allow_found"], required=True)}
        {check_row("FastTrack found", checks["fasttrack_found"])}
        {check_row("ether1 link status", checks["ether1_link_ok"])}
        {row("ether1 rate", checks["ether1_rate"])}
        {check_row("ether1 full duplex", checks["ether1_full_duplex"])}
      </table>
    </div>
  </section>
  <section class="panel">
    <h2>Precheck Errors</h2>
    {notice_items(report["router_precheck_errors"], "danger", "None")}
  </section>
  <section class="panel">
    <h2>Precheck Warnings</h2>
    {notice_items(report["router_precheck_warnings"], "warning", "None")}
  </section>
  <section class="panel">
    <h2>Suggested MikroTik Commands</h2>
    {code_blocks(report["suggested_mikrotik_commands"], "No suggested commands")}
  </section>
  <section class="panel">
    <h2>Suggested Manual Checks</h2>
    {code_blocks(report["suggested_manual_checks"], "No suggested manual checks")}
  </section>
  <section class="panel">
    <h2>Error Message</h2>
    {notice_items([report["error"]] if report["error"] else [], "danger", "None")}
  </section>
  <section class="panel">
    <h2>Next Validation Steps</h2>
    <div class="notice neutral"><ol>{next_steps_html}</ol></div>
  </section>
</main>
</body>
</html>
"""


def write_reports(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    direction_name = sanitize_path_name(str(report.get("direction", "unknown")))
    json_path = output_dir / f"day8_iperf3_{direction_name}_report.json"
    html_path = output_dir / f"day8_iperf3_{direction_name}_report.html"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with html_path.open("w", encoding="utf-8") as file:
        file.write(build_html_report(report))
    return json_path, html_path


def console_color(text: Any, color_code: str) -> str:
    value = str(text)
    if not sys.stdout.isatty():
        return value
    return f"\033[{color_code}m{value}\033[0m"


def console_status(value: Any) -> str:
    normalized = str(value).strip().upper()
    if normalized == "PASS":
        return console_color(value, "32;1")
    if normalized == "FAIL":
        return console_color(value, "31;1")
    if normalized in {"SKIP", "SKIPPED", "NOT_RUN"}:
        return console_color(value, "90;1")
    if normalized in {"WARNING", "WARN"}:
        return console_color(value, "33;1")
    return str(value)


def run(config: Day8Config) -> Tuple[Dict[str, Any], Path, Path]:
    command = build_iperf3_command(
        config.router_wan_ip,
        config.direction,
        config.duration,
        config.parallel,
        config.omit,
        config.iperf3_path,
    )
    confirmed = confirm_router_wan_ip(config)
    report = base_report(config, command, confirmed)

    if not confirmed:
        report["router_precheck_result"] = "NOT_RUN"
        report["routeros_precheck_result"] = "NOT_RUN"
        report["error"] = "Aborted: Router WAN IP was not confirmed."
        json_path, html_path = write_reports(report, config.output_dir)
        return report, json_path, html_path

    precheck = run_routeros_precheck(config)
    apply_precheck_to_report(report, precheck)
    if precheck["result"] == "FAIL":
        report["error"] = "RouterOS precheck failed. iperf3 was not executed."
        json_path, html_path = write_reports(report, config.output_dir)
        return report, json_path, html_path

    iperf_result, parsed, error, stderr = run_iperf3(
        command,
        timeout=config.duration + config.omit + 30,
        progress_seconds=config.duration + config.omit,
    )
    report["iperf3_stderr"] = stderr
    if iperf_result == "FAIL":
        report["error"] = error
        json_path, html_path = write_reports(report, config.output_dir)
        return report, json_path, html_path

    assert parsed is not None
    report["throughput_mbps"] = round(parsed["throughput_mbps"], 3)
    report["throughput_source_field"] = parsed["source_field"]
    report["measured_field"] = parsed["source_field"]
    result, message = evaluate_throughput_result(
        parsed["throughput_mbps"],
        config.threshold_mbps,
        config.warn_threshold_mbps,
    )
    report["result"] = result
    report["error"] = message

    json_path, html_path = write_reports(report, config.output_dir)
    return report, json_path, html_path


def print_summary(report: Dict[str, Any], json_path: Path, html_path: Path) -> None:
    print()
    print(console_color("=" * 72, "36"))
    print(console_color("iperf3 Router Performance Automation", "1"))
    print(console_color("=" * 72, "36"))
    print(f"Device Name: {report['device_name']}")
    print(f"Test Type: {report['test_type']}")
    print(f"Direction: {report['direction']}")
    print(f"Traffic Path: {report['traffic_path']}")
    print(f"Router WAN IP: {report['router_wan_ip']}")
    print(f"LAN Server IP: {report['lan_server_ip']}")
    print(f"Command: {report['command']}")
    print(f"Result: {console_status(report['result'])}")
    print(f"Throughput Mbps: {console_color(report['throughput_mbps'], '32;1')}")
    print(f"Threshold Mbps: {report['threshold_mbps']}")
    print(f"Warn Threshold Mbps: {report['warn_threshold_mbps']}")
    print(f"Measured Field: {report['measured_field']}")
    print(f"RouterOS Precheck: {console_status(report['router_precheck_result'])}")
    if report["error"]:
        print(f"Error: {console_color(report['error'], '31;1')}")
    if report["router_precheck_errors"]:
        print(console_color("-" * 72, "36"))
        print(console_color("Precheck Errors", "31;1"))
        for error in report["router_precheck_errors"]:
            print(f"- {error}")
    if report["router_precheck_warnings"]:
        print(console_color("-" * 72, "36"))
        print(console_color("Precheck Warnings", "33;1"))
        for warning in report["router_precheck_warnings"]:
            print(f"- {warning}")
    if report["suggested_mikrotik_commands"]:
        print(console_color("-" * 72, "36"))
        print(console_color("Suggested MikroTik Commands", "33;1"))
        for command in report["suggested_mikrotik_commands"]:
            print(command)
    if report["suggested_manual_checks"]:
        print(console_color("-" * 72, "36"))
        print(console_color("Suggested Manual Checks", "33;1"))
        for command in report["suggested_manual_checks"]:
            print(command)
    print(console_color("-" * 72, "36"))
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print(console_color("=" * 72, "36"))


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
        config = build_config_from_args(args)
        report, json_path, html_path = run(config)
        print_summary(report, json_path, html_path)
        return 0 if report["result"] in {"PASS", "WARN"} else 1
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(str(error))
        return 2


if __name__ == "__main__":
    sys.exit(main())
