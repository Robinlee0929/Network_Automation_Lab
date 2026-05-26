import argparse
import getpass
import json
import re
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko


CONFIG_PATH = Path("config.json")
REPORT_DIR = Path("reports") / "day2"
DISCOVERED_CONFIG_REPORT_PATH = REPORT_DIR / "discovered_day2_config.json"
GOLDEN_TEMPLATE_PATH = Path("golden_day2_config.example.json")

DEFAULT_HOST = "192.168.88.1"
DEFAULT_PORT = 22
DEFAULT_USERNAME = "admin"
DEFAULT_TARGET_ROUTEROS_VERSION = "7.22.3"
DEFAULT_TIMEZONE = "Asia/Taipei"

SSH_TIMEOUT_SECONDS = 15
COMMAND_TIMEOUT_SECONDS = 30
NTP_SYNC_TIMEOUT_SECONDS = 120
NTP_SYNC_RETRY_INTERVAL_SECONDS = 10

REPORT_FIELDS = [
    "device_name",
    "host",
    "board_name",
    "routeros_version",
    "target_routeros_version",
    "package_latest",
    "current_firmware",
    "upgrade_firmware",
    "factory_firmware",
    "routerboard_firmware_synced",
    "ntp_client",
    "version_gate_result",
    "ssh_connect_result",
    "precheck_result",
    "backup_result",
    "baseline_marker_result",
    "apply_config_result",
    "validation_result",
    "commands_executed",
    "warnings",
    "errors",
]

VALIDATION_COMMANDS = [
    "/system identity print",
    "/system clock print",
    "/system ntp client print",
    "/ip service print",
    "/system resource print",
    "/system package print",
    "/system routerboard print",
]

DISCOVERY_COMMANDS = [
    "/system identity print",
    "/system clock print",
    "/system ntp client print detail",
    "/system resource print",
    "/system package print",
    "/system routerboard print",
    "/ip service print",
    "/interface bridge port print",
    "/ip dhcp-client print detail",
]

COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_DIM = "\033[2m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"


@dataclass
class Day2Config:
    host: str
    port: int
    username: str
    password: str
    device_name: str
    target_routeros_version: str
    enable_apply_config: bool
    enable_backup: bool
    enable_report: bool
    timezone: str
    disable_services: List[str]
    expected_wan_interface: str = "ether1"
    expected_wan_dhcp_client_required: bool = True
    expected_lan_bridge: str = "bridge"
    expected_lan_ip_cidr: str = "192.168.88.1/24"
    required_disabled_services: List[str] = None


class CommandTimeoutError(RuntimeError):
    pass


def load_config(path: Path = CONFIG_PATH) -> Day2Config:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Create it from config.example.json and set RouterOS login values."
        )

    with path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)
    expected_config = raw_config.get("expected", {})
    if not isinstance(expected_config, dict):
        expected_config = {}

    return Day2Config(
        host=str(raw_config.get("host", raw_config.get("router_ip", DEFAULT_HOST))),
        port=int(raw_config.get("port", raw_config.get("ssh_port", DEFAULT_PORT))),
        username=str(raw_config.get("username", DEFAULT_USERNAME)),
        password=str(raw_config.get("password", "")),
        device_name=str(raw_config.get("device_name", "")).strip(),
        target_routeros_version=str(
            raw_config.get("target_routeros_version", DEFAULT_TARGET_ROUTEROS_VERSION)
        ).strip(),
        enable_apply_config=bool(raw_config.get("enable_apply_config", False)),
        enable_backup=bool(raw_config.get("enable_backup", True)),
        enable_report=bool(raw_config.get("enable_report", True)),
        timezone=str(raw_config.get("timezone", DEFAULT_TIMEZONE)).strip() or DEFAULT_TIMEZONE,
        disable_services=list(raw_config.get("disable_services", [])),
        expected_wan_interface=str(
            expected_config.get("wan_interface", "ether1")
        ).strip()
        or "ether1",
        expected_wan_dhcp_client_required=bool(
            expected_config.get("wan_dhcp_client_required", True)
        ),
        expected_lan_bridge=str(expected_config.get("lan_bridge", "bridge")).strip()
        or "bridge",
        expected_lan_ip_cidr=str(
            expected_config.get("lan_ip_cidr", "192.168.88.1/24")
        ).strip()
        or "192.168.88.1/24",
        required_disabled_services=list(
            expected_config.get(
                "required_disabled_services",
                raw_config.get("disable_services", ["ftp", "telnet"]),
            )
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MikroTik Day 2 auto setup.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force enable_apply_config=false for this run.",
    )
    parser.add_argument(
        "--discover-config",
        action="store_true",
        help="Read current RouterOS settings and write a suggested Day 2 config report without applying changes.",
    )
    parser.add_argument(
        "--export-template",
        action="store_true",
        help="Create golden_day2_config.example.json from reports/day2/discovered_day2_config.json.",
    )
    return parser.parse_args()


def get_password(default_password: str = "") -> str:
    if default_password:
        return default_password

    password = getpass.getpass("Please input SSH password: ").strip()
    if not password:
        raise ValueError("SSH password is required.")
    return password


def get_host(default_host: str) -> str:
    prompt = f"Please input router host/IP (press Enter to use config.json default: {default_host}): "
    host = input(prompt).strip()
    if host:
        return host
    if default_host:
        return default_host
    raise ValueError("Router host/IP is required.")


def make_keyboard_interactive_handler(password: str):
    def handler(
        _title: str,
        _instructions: str,
        prompts: List[Tuple[str, bool]],
    ) -> List[str]:
        return [password for _prompt, _echo in prompts]

    return handler


def connect_ssh_keyboard_interactive(config: Day2Config) -> paramiko.SSHClient:
    sock: Optional[socket.socket] = None
    transport: Optional[paramiko.Transport] = None

    try:
        sock = socket.create_connection((config.host, config.port), timeout=SSH_TIMEOUT_SECONDS)
        transport = paramiko.Transport(sock)
        transport.start_client(timeout=SSH_TIMEOUT_SECONDS)
        transport.auth_interactive(
            config.username,
            make_keyboard_interactive_handler(config.password),
        )

        if not transport.is_authenticated():
            raise paramiko.AuthenticationException(
                "Keyboard-interactive authentication failed."
            )

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client._transport = transport
        return client
    except Exception:
        if transport:
            transport.close()
        elif sock:
            sock.close()
        raise


def connect_ssh(config: Day2Config) -> paramiko.SSHClient:
    try:
        return connect_ssh_keyboard_interactive(config)
    except (paramiko.AuthenticationException, paramiko.SSHException):
        pass

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            timeout=SSH_TIMEOUT_SECONDS,
            banner_timeout=SSH_TIMEOUT_SECONDS,
            auth_timeout=SSH_TIMEOUT_SECONDS,
            look_for_keys=False,
            allow_agent=False,
        )
        return client
    except Exception:
        client.close()
        raise


def connect_ssh_with_auth_retry(
    config: Day2Config,
    max_attempts: int = 3,
) -> paramiko.SSHClient:
    last_error: Optional[paramiko.AuthenticationException] = None

    for attempt in range(1, max_attempts + 1):
        try:
            return connect_ssh(config)
        except paramiko.AuthenticationException as error:
            last_error = error
            if attempt >= max_attempts:
                break

            print("Authentication failed. Please try again.")
            config.password = getpass.getpass("Please input SSH password: ").strip()
            if not config.password:
                print("Empty password entered; retrying may fail.")

    if last_error:
        raise last_error

    raise paramiko.AuthenticationException("Authentication failed.")


def run_raw_command(
    client: paramiko.SSHClient,
    command: str,
    timeout_seconds: int = COMMAND_TIMEOUT_SECONDS,
) -> str:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout_seconds)
    stdin.close()

    channel = stdout.channel
    output_chunks: List[str] = []
    error_chunks: List[str] = []
    deadline = time.monotonic() + timeout_seconds

    while not channel.exit_status_ready():
        if time.monotonic() > deadline:
            channel.close()
            raise CommandTimeoutError(f"Command timed out after {timeout_seconds}s: {command}")

        if channel.recv_ready():
            output_chunks.append(channel.recv(4096).decode("utf-8", errors="replace"))
        if channel.recv_stderr_ready():
            error_chunks.append(channel.recv_stderr(4096).decode("utf-8", errors="replace"))
        time.sleep(0.1)

    while channel.recv_ready():
        output_chunks.append(channel.recv(4096).decode("utf-8", errors="replace"))
    while channel.recv_stderr_ready():
        error_chunks.append(channel.recv_stderr(4096).decode("utf-8", errors="replace"))

    exit_status = channel.recv_exit_status()
    output = "".join(output_chunks)
    error_output = "".join(error_chunks).strip()

    if exit_status != 0:
        raise RuntimeError(
            f"Command failed with exit status {exit_status}: {command}; stderr={error_output}"
        )

    return output


def quote_routeros_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def parse_key_value_output(output: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    pattern = re.compile(r"([\w-]+)\s*:\s*(.*?)(?=\s+[\w-]+\s*:|$)")

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for key, value in pattern.findall(stripped):
            values[key] = value.strip()

    return values


def parse_system_resource(output: str) -> Dict[str, str]:
    values = parse_key_value_output(output)
    return {
        "version": values.get("version", ""),
        "board-name": values.get("board-name", ""),
        "architecture-name": values.get("architecture-name", ""),
        "cpu": values.get("cpu", ""),
        "cpu-count": values.get("cpu-count", ""),
        "total-memory": values.get("total-memory", ""),
        "free-memory": values.get("free-memory", ""),
        "uptime": values.get("uptime", ""),
    }


def parse_package_version(output: str) -> str:
    for line in output.splitlines():
        if "routeros" not in line.lower():
            continue

        version_match = re.search(r"\b(\d+\.\d+(?:\.\d+)?(?:[A-Za-z0-9_.-]*)?)\b", line)
        if version_match:
            return version_match.group(1)

    values = parse_key_value_output(output)
    name = values.get("name", "").lower()
    if name == "routeros" and values.get("version"):
        return values["version"]

    return ""


def parse_routerboard_firmware(output: str) -> Dict[str, str]:
    values = parse_key_value_output(output)
    return {
        "current-firmware": values.get("current-firmware", ""),
        "upgrade-firmware": values.get("upgrade-firmware", ""),
        "factory-firmware": values.get("factory-firmware", ""),
    }


def parse_ntp_client(output: str) -> Dict[str, str]:
    values = parse_key_value_output(output)
    return {
        "enabled": values.get("enabled", ""),
        "mode": values.get("mode", ""),
        "servers": values.get("servers", ""),
        "status": values.get("status", ""),
        "synced-server": values.get("synced-server", ""),
        "synced-stratum": values.get("synced-stratum", ""),
        "system-offset": values.get("system-offset", ""),
    }


def parse_identity(output: str) -> str:
    values = parse_key_value_output(output)
    return values.get("name", "").strip()


def parse_disabled_services(output: str) -> List[str]:
    disabled_services: List[str] = []
    known_services = {"ftp", "ssh", "telnet", "www", "www-ssl", "winbox", "api", "api-ssl"}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("Flags:", "Columns:", "#", ";;;")):
            continue
        parts = stripped.split()
        if parts and parts[0].isdigit():
            flags = []
            service_name = ""
            for token in parts[1:]:
                if token in {"D", "X", "I", "c"}:
                    flags.append(token)
                    continue
                service_name = token
                break
            if "X" not in flags:
                continue
        elif len(parts) >= 2 and "X" in parts[0].upper():
            service_name = parts[1]
        else:
            continue
        if service_name in known_services and service_name not in {"ssh", "www", "www-ssl"}:
            disabled_services.append(service_name)
    return disabled_services


def check_version_gate(routeros_version: str, target_routeros_version: str) -> Tuple[str, bool]:
    if not routeros_version:
        return "FAIL", False
    package_latest = routeros_version == target_routeros_version
    return ("PASS" if package_latest else "WARNING"), package_latest


def build_manual_update_steps(routeros_version: str, target_routeros_version: str) -> List[str]:
    return [
        f"Current RouterOS package version is {routeros_version or 'unknown'}; target version is {target_routeros_version}.",
        "Do not upgrade during this automation run. Schedule a maintenance window before changing RouterOS packages.",
        "Manual CLI check: /system package update check-for-updates",
        "Manual upgrade path: use WinBox/WebFig System > Packages > Check For Updates, choose the target channel/version, then Download&Install when ready.",
        "After the router comes back online, run mikrotik_day2_auto_setup.py again in dry-run mode to verify the package version and firmware status.",
    ]


def add_manual_update_steps(report: Dict[str, Any]) -> None:
    if report.get("manual_update_steps"):
        return
    report["manual_update_steps"] = build_manual_update_steps(
        str(report.get("routeros_version", "")),
        str(report.get("target_routeros_version", "")),
    )


def validate_identity_name(device_name: str) -> None:
    if not device_name:
        raise ValueError("device_name is required in config.json.")
    if len(device_name) > 64:
        raise ValueError("device_name must be 64 characters or fewer.")
    if "\n" in device_name or "\r" in device_name:
        raise ValueError("device_name must not contain newline characters.")


def validate_disable_services(services: List[str]) -> List[str]:
    protected_services = {"ssh", "www", "www-ssl"}
    safe_services = []
    for service in services:
        normalized = str(service).strip()
        if not normalized:
            continue
        if normalized.lower() in protected_services:
            raise ValueError("disable_services must not include ssh, www, or www-ssl.")
        if "\n" in normalized or "\r" in normalized or '"' in normalized:
            raise ValueError(f"Invalid service name in disable_services: {normalized!r}")
        safe_services.append(normalized)
    return safe_services


def build_apply_commands(config: Day2Config) -> List[str]:
    validate_identity_name(config.device_name)
    disable_services = validate_disable_services(
        sorted(set((config.disable_services or []) + (config.required_disabled_services or [])))
    )
    wan_interface = quote_routeros_value(config.expected_wan_interface)
    lan_bridge = quote_routeros_value(config.expected_lan_bridge)
    lan_ip_cidr = quote_routeros_value(config.expected_lan_ip_cidr)

    commands = [
        f"/system identity set name={quote_routeros_value(config.device_name)}",
        f"/system clock set time-zone-name={quote_routeros_value(config.timezone)}",
        f":if ([:len [/interface find name={wan_interface}]] = 0) do={{:error \"WAN interface not found\"}}",
        f":if ([:len [/interface bridge find name={lan_bridge}]] = 0) do={{/interface bridge add name={lan_bridge}}}",
        f"/interface bridge port remove [find interface={wan_interface}]",
        f":if ([:len [/ip dhcp-client find interface={wan_interface}]] = 0) do={{/ip dhcp-client add interface={wan_interface} disabled=no add-default-route=yes use-peer-dns=yes}} else={{/ip dhcp-client set [find interface={wan_interface}] disabled=no add-default-route=yes use-peer-dns=yes}}",
        f":if ([:len [/ip address find interface={lan_bridge} address={lan_ip_cidr}]] = 0) do={{/ip address add interface={lan_bridge} address={lan_ip_cidr}}}",
        "/system ntp client set enabled=no",
        "/system ntp client set enabled=yes mode=unicast servers=pool.ntp.org",
        "/ip service enable [find name=ssh]",
    ]
    for service in disable_services:
        commands.append(f"/ip service disable [find name={quote_routeros_value(service)}]")
    return commands


def make_empty_report(config: Day2Config) -> Dict[str, Any]:
    return {
        "device_name": config.device_name,
        "host": config.host,
        "board_name": "",
        "routeros_version": "",
        "target_routeros_version": config.target_routeros_version,
        "package_latest": False,
        "current_firmware": "",
        "upgrade_firmware": "",
        "factory_firmware": "",
        "routerboard_firmware_synced": False,
        "ntp_client": {
            "enabled": "",
            "mode": "",
            "servers": "",
            "status": "",
            "synced-server": "",
            "synced-stratum": "",
            "system-offset": "",
        },
        "version_gate_result": "FAIL",
        "ssh_connect_result": "FAIL",
        "precheck_result": "SKIPPED",
        "backup_result": "SKIPPED",
        "baseline_marker_result": "SKIPPED",
        "apply_config_result": "SKIPPED",
        "validation_result": "FAIL",
        "commands_executed": [],
        "warnings": [],
        "errors": [],
        "dry_run_commands": [],
        "manual_update_steps": [],
        "collected": {},
        "validation_outputs": {},
        "expected_config": {
            "wan_interface": config.expected_wan_interface,
            "wan_dhcp_client_required": config.expected_wan_dhcp_client_required,
            "lan_bridge": config.expected_lan_bridge,
            "lan_ip_cidr": config.expected_lan_ip_cidr,
            "required_disabled_services": config.required_disabled_services
            or ["ftp", "telnet"],
        },
    }


def ensure_report_fields(report: Dict[str, Any]) -> Dict[str, Any]:
    for field in REPORT_FIELDS:
        report.setdefault(field, [] if field in {"commands_executed", "warnings", "errors"} else "")
    return report


def record_command(report: Dict[str, Any], command: str) -> None:
    report["commands_executed"].append(command)


def run_and_record(client: paramiko.SSHClient, command: str, report: Dict[str, Any]) -> str:
    record_command(report, command)
    return run_raw_command(client, command)


def run_backup_set(client: paramiko.SSHClient, prefix: str, report: Dict[str, Any]) -> None:
    for command in [
        f"/export file={prefix}",
        f"/system backup save name={prefix}",
    ]:
        run_and_record(client, command, report)


def run_setup_precheck(
    client: paramiko.SSHClient,
    config: Day2Config,
    report: Dict[str, Any],
) -> None:
    checks: List[str] = []
    try:
        identity_output = run_and_record(client, "/system identity print", report)
        if identity_output.strip():
            checks.append("RouterOS command execution PASS")
        interface_output = run_and_record(
            client,
            f"/interface print where name={quote_routeros_value(config.expected_wan_interface)}",
            report,
        )
        if config.expected_wan_interface not in interface_output:
            raise RuntimeError(f"{config.expected_wan_interface} interface was not found.")
        checks.append(f"{config.expected_wan_interface} interface exists")
        report["precheck_result"] = "PASS"
        report["collected"]["precheck"] = checks
    except Exception as error:
        report["precheck_result"] = "FAIL"
        report["errors"].append(f"Setup pre-check failed: {type(error).__name__}: {error}")


def create_baseline_marker_backup(client: paramiko.SSHClient, report: Dict[str, Any]) -> None:
    if report.get("validation_result") == "FAIL":
        report["baseline_marker_result"] = "SKIPPED"
        report["warnings"].append(
            "baseline-wan-ntp-ok backup was skipped because validation_result=FAIL."
        )
        return

    if report.get("ntp_client", {}).get("status") != "synchronized":
        report["baseline_marker_result"] = "SKIPPED"
        report["warnings"].append(
            "baseline-wan-ntp-ok backup was skipped because NTP is not synchronized."
        )
        return

    try:
        run_backup_set(client, "baseline-wan-ntp-ok", report)
        report["baseline_marker_result"] = "PASS"
    except Exception as error:
        report["baseline_marker_result"] = "FAIL"
        report["errors"].append(
            f"baseline-wan-ntp-ok backup failed: {type(error).__name__}: {error}"
        )


def collect_preflight(client: paramiko.SSHClient, report: Dict[str, Any]) -> None:
    resource_output = run_and_record(client, "/system resource print", report)
    package_output = run_and_record(client, "/system package print", report)
    routerboard_output = run_and_record(client, "/system routerboard print", report)

    resource = parse_system_resource(resource_output)
    firmware = parse_routerboard_firmware(routerboard_output)
    routeros_version = parse_package_version(package_output) or resource.get("version", "")
    version_gate_result, package_latest = check_version_gate(
        routeros_version,
        str(report["target_routeros_version"]),
    )

    report["routeros_version"] = routeros_version
    report["board_name"] = resource.get("board-name", "")
    report["package_latest"] = package_latest
    report["version_gate_result"] = version_gate_result
    report["current_firmware"] = firmware.get("current-firmware", "")
    report["upgrade_firmware"] = firmware.get("upgrade-firmware", "")
    report["factory_firmware"] = firmware.get("factory-firmware", "")
    report["routerboard_firmware_synced"] = (
        bool(report["current_firmware"])
        and report["current_firmware"] == report["upgrade_firmware"]
    )
    report["collected"]["resource"] = resource
    report["collected"]["routerboard"] = firmware

    if version_gate_result == "WARNING":
        report["warnings"].append(
            "RouterOS package version differs from target_routeros_version; no upgrade was attempted."
        )
        add_manual_update_steps(report)
    elif version_gate_result == "FAIL":
        report["errors"].append("Unable to parse RouterOS routeros package version.")

    if not report["routerboard_firmware_synced"]:
        report["warnings"].append(
            "RouterBOARD current-firmware differs from upgrade-firmware; no firmware upgrade or reboot was attempted."
        )


def apply_or_dry_run(client: paramiko.SSHClient, config: Day2Config, report: Dict[str, Any]) -> None:
    apply_commands = build_apply_commands(config)
    if not config.enable_apply_config:
        report["apply_config_result"] = "SKIPPED"
        report["dry_run_commands"] = apply_commands
        report["warnings"].append("enable_apply_config=false; configuration commands were dry-run only.")
        return

    for command in apply_commands:
        run_and_record(client, command, report)
    report["apply_config_result"] = "PASS"


def wait_for_ntp_synchronized(
    client: paramiko.SSHClient,
    report: Dict[str, Any],
    timeout_seconds: int = NTP_SYNC_TIMEOUT_SECONDS,
    interval_seconds: int = NTP_SYNC_RETRY_INTERVAL_SECONDS,
) -> Dict[str, str]:
    print(
        f"NTP is not synchronized yet; waiting up to {timeout_seconds} seconds "
        f"(retry every {interval_seconds} seconds)."
    )
    deadline = time.monotonic() + timeout_seconds
    last_ntp_client: Dict[str, str] = {}

    while True:
        output = run_and_record(client, "/system ntp client print", report)
        report["validation_outputs"]["/system ntp client print"] = output
        last_ntp_client = parse_ntp_client(output)
        report["ntp_client"] = last_ntp_client

        if last_ntp_client.get("status") == "synchronized":
            print("NTP status is synchronized.")
            return last_ntp_client

        if time.monotonic() >= deadline:
            print(
                "NTP did not reach synchronized before timeout; "
                f"last status={last_ntp_client.get('status', 'unknown')}."
            )
            return last_ntp_client

        remaining_seconds = max(0, int(deadline - time.monotonic()))
        print(
            "NTP status="
            f"{last_ntp_client.get('status', 'unknown')}; retrying in "
            f"{interval_seconds} seconds ({remaining_seconds} seconds remaining)."
        )
        time.sleep(interval_seconds)


def validate_after_apply(client: paramiko.SSHClient, report: Dict[str, Any]) -> None:
    validation_outputs: Dict[str, str] = {}
    validation_errors: List[str] = []

    for command in VALIDATION_COMMANDS:
        try:
            validation_outputs[command] = run_and_record(client, command, report)
        except Exception as error:
            validation_errors.append(f"{command}: {type(error).__name__}: {error}")

    report["validation_outputs"] = validation_outputs

    resource_output = validation_outputs.get("/system resource print", "")
    package_output = validation_outputs.get("/system package print", "")
    routerboard_output = validation_outputs.get("/system routerboard print", "")
    ntp_output = validation_outputs.get("/system ntp client print", "")

    if resource_output:
        resource = parse_system_resource(resource_output)
        report["board_name"] = resource.get("board-name", report["board_name"])
        report["collected"]["resource_after"] = resource
    if package_output:
        routeros_version = parse_package_version(package_output)
        if routeros_version:
            report["routeros_version"] = routeros_version
            version_gate_result, package_latest = check_version_gate(
                routeros_version,
                str(report["target_routeros_version"]),
            )
            report["version_gate_result"] = version_gate_result
            report["package_latest"] = package_latest
            if version_gate_result == "WARNING":
                add_manual_update_steps(report)
    if routerboard_output:
        firmware = parse_routerboard_firmware(routerboard_output)
        report["current_firmware"] = firmware.get("current-firmware", report["current_firmware"])
        report["upgrade_firmware"] = firmware.get("upgrade-firmware", report["upgrade_firmware"])
        report["factory_firmware"] = firmware.get("factory-firmware", report["factory_firmware"])
        report["routerboard_firmware_synced"] = (
            bool(report["current_firmware"])
            and report["current_firmware"] == report["upgrade_firmware"]
        )
    if ntp_output:
        report["ntp_client"] = parse_ntp_client(ntp_output)

    ntp_client = report["ntp_client"]
    is_dry_run = report.get("apply_config_result") == "SKIPPED" and bool(
        report.get("dry_run_commands")
    )
    if ntp_client.get("status") != "synchronized" and is_dry_run:
        report["warnings"].append(
            "NTP client is not synchronized during dry-run; retry wait was skipped."
        )
    elif ntp_client.get("status") != "synchronized":
        try:
            ntp_client = wait_for_ntp_synchronized(client, report)
        except Exception as error:
            validation_errors.append(
                f"/system ntp client print retry: {type(error).__name__}: {error}"
            )

    ntp_synchronized = ntp_client.get("status") == "synchronized"
    if not ntp_synchronized:
        report["warnings"].append(
            "NTP client did not reach status=synchronized within 120 seconds; validation marked WARNING."
        )

    if validation_errors:
        report["errors"].extend(validation_errors)
        report["validation_result"] = "FAIL"
    elif (
        report["version_gate_result"] == "WARNING"
        or not report["routerboard_firmware_synced"]
        or not ntp_synchronized
    ):
        report["validation_result"] = "WARNING"
    elif report["version_gate_result"] == "PASS":
        report["validation_result"] = "PASS"
    else:
        report["validation_result"] = "FAIL"


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    short_divider = "-" * 72
    lines = [
        divider,
        "MikroTik Day 2 Auto Setup",
        divider,
        f"{'Device Name':<28}: {report['device_name']}",
        f"{'Host':<28}: {report['host']}",
        f"{'Board Name':<28}: {report['board_name']}",
        f"{'RouterOS Version':<28}: {report['routeros_version']}",
        f"{'Target RouterOS Version':<28}: {report['target_routeros_version']}",
        f"{'Package Latest':<28}: {report['package_latest']}",
        f"{'Current Firmware':<28}: {report['current_firmware']}",
        f"{'Upgrade Firmware':<28}: {report['upgrade_firmware']}",
        f"{'Factory Firmware':<28}: {report['factory_firmware']}",
        f"{'RouterBOARD Firmware Synced':<28}: {report['routerboard_firmware_synced']}",
        f"{'NTP Status':<28}: {report.get('ntp_client', {}).get('status', '')}",
        short_divider,
        "Results",
        f"{'SSH Connect':<28}: {report['ssh_connect_result']}",
        f"{'Setup Pre-check':<28}: {report['precheck_result']}",
        f"{'Version Gate':<28}: {report['version_gate_result']}",
        f"{'Backup':<28}: {report['backup_result']}",
        f"{'Baseline Marker Backup':<28}: {report['baseline_marker_result']}",
        f"{'Apply Config':<28}: {report['apply_config_result']}",
        f"{'Validation':<28}: {report['validation_result']}",
        short_divider,
        "Commands Executed",
    ]

    if report["commands_executed"]:
        lines.extend(f"- {command}" for command in report["commands_executed"])
    else:
        lines.append("- None")

    if report.get("dry_run_commands"):
        lines.extend([short_divider, "Dry-Run Commands"])
        lines.extend(f"- {command}" for command in report["dry_run_commands"])

    if report.get("manual_update_steps"):
        lines.extend([short_divider, "Manual RouterOS Update Guidance"])
        lines.extend(f"- {step}" for step in report["manual_update_steps"])

    ntp_client = report.get("ntp_client", {})
    lines.extend(
        [
            short_divider,
            "NTP Client Status",
            f"{'enabled':<28}: {ntp_client.get('enabled', '')}",
            f"{'mode':<28}: {ntp_client.get('mode', '')}",
            f"{'servers':<28}: {ntp_client.get('servers', '')}",
            f"{'status':<28}: {ntp_client.get('status', '')}",
            f"{'synced-server':<28}: {ntp_client.get('synced-server', '')}",
            f"{'synced-stratum':<28}: {ntp_client.get('synced-stratum', '')}",
            f"{'system-offset':<28}: {ntp_client.get('system-offset', '')}",
        ]
    )

    lines.extend([short_divider, "Warnings"])
    if report["warnings"]:
        lines.extend(f"- {warning}" for warning in report["warnings"])
    else:
        lines.append("- None")

    lines.extend([short_divider, "Errors"])
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None")

    lines.extend(
        [
            short_divider,
            "Reports",
            f"{'JSON':<28}: {json_path}",
            f"{'TXT':<28}: {txt_path}",
            divider,
        ]
    )

    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "day2_auto_setup_report.json"
    txt_path = REPORT_DIR / "day2_auto_setup_report.txt"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(ensure_report_fields(report), file, indent=2, ensure_ascii=False)
        file.write("\n")

    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report, json_path, txt_path))

    return json_path, txt_path


def build_discovery_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    short_divider = "-" * 72
    suggested = report.get("suggested_config", {})
    current = report.get("current_state", {})
    lines = [
        divider,
        "MikroTik Day 2 Config Discovery",
        divider,
        f"{'Host':<28}: {suggested.get('host', '')}",
        f"{'Device Name':<28}: {suggested.get('device_name', '')}",
        f"{'RouterOS Version':<28}: {suggested.get('target_routeros_version', '')}",
        f"{'Timezone':<28}: {suggested.get('timezone', '')}",
        f"{'NTP Status':<28}: {current.get('ntp_client', {}).get('status', '')}",
        f"{'NTP Servers':<28}: {current.get('ntp_client', {}).get('servers', '')}",
        short_divider,
        "Suggested config values",
        json.dumps(suggested, indent=2, ensure_ascii=False),
        short_divider,
        "Current WAN / bridge / DHCP raw state",
        "[/interface bridge port print]",
        current.get("raw_outputs", {}).get("/interface bridge port print", "").strip() or "(empty)",
        "[/ip dhcp-client print detail]",
        current.get("raw_outputs", {}).get("/ip dhcp-client print detail", "").strip() or "(empty)",
        short_divider,
        f"{'JSON':<28}: {json_path}",
        f"{'TXT':<28}: {txt_path}",
        divider,
    ]
    return "\n".join(lines) + "\n"


def write_discovery_report(report: Dict[str, Any]) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DISCOVERED_CONFIG_REPORT_PATH
    txt_path = REPORT_DIR / "discovered_day2_config.txt"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")

    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_discovery_text_report(report, json_path, txt_path))

    return json_path, txt_path


def build_golden_template_from_discovery(discovery_report: Dict[str, Any]) -> Dict[str, Any]:
    suggested = discovery_report.get("suggested_config", {})
    if not isinstance(suggested, dict) or not suggested:
        raise ValueError("discovered_day2_config.json does not contain suggested_config.")

    device = suggested.get("device", {})
    if not isinstance(device, dict):
        device = {}

    return {
        "device": {
            "vendor": device.get("vendor", "mikrotik"),
            "platform": device.get("platform", "routeros"),
        },
        "host": suggested.get("host", "192.168.88.1"),
        "port": int(suggested.get("port", 22)),
        "username": suggested.get("username", "admin"),
        "password": "",
        "device_name": suggested.get("device_name", ""),
        "target_routeros_version": suggested.get(
            "target_routeros_version",
            DEFAULT_TARGET_ROUTEROS_VERSION,
        ),
        "enable_apply_config": False,
        "enable_backup": bool(suggested.get("enable_backup", True)),
        "enable_report": bool(suggested.get("enable_report", True)),
        "timezone": suggested.get("timezone", DEFAULT_TIMEZONE),
        "disable_services": list(suggested.get("disable_services", [])),
        "expected": {
            "wan_interface": suggested.get("expected", {}).get("wan_interface", "ether1")
            if isinstance(suggested.get("expected", {}), dict)
            else "ether1",
            "wan_dhcp_client_required": suggested.get("expected", {}).get(
                "wan_dhcp_client_required",
                True,
            )
            if isinstance(suggested.get("expected", {}), dict)
            else True,
            "lan_bridge": suggested.get("expected", {}).get("lan_bridge", "bridge")
            if isinstance(suggested.get("expected", {}), dict)
            else "bridge",
            "lan_ip_cidr": suggested.get("expected", {}).get(
                "lan_ip_cidr",
                "192.168.88.1/24",
            )
            if isinstance(suggested.get("expected", {}), dict)
            else "192.168.88.1/24",
            "required_disabled_services": suggested.get("expected", {}).get(
                "required_disabled_services",
                ["ftp", "telnet"],
            )
            if isinstance(suggested.get("expected", {}), dict)
            else ["ftp", "telnet"],
        },
    }


def export_golden_template(
    discovery_path: Path = DISCOVERED_CONFIG_REPORT_PATH,
    template_path: Path = GOLDEN_TEMPLATE_PATH,
) -> Dict[str, Any]:
    if not discovery_path.exists():
        raise FileNotFoundError(
            f"Missing {discovery_path}. Run mikrotik_day2_auto_setup.py --discover-config first."
        )

    with discovery_path.open("r", encoding="utf-8") as file:
        discovery_report = json.load(file)

    template = build_golden_template_from_discovery(discovery_report)
    with template_path.open("w", encoding="utf-8") as file:
        json.dump(template, file, indent=2, ensure_ascii=False)
        file.write("\n")

    return template


def discover_day2_config(config: Day2Config) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "host": config.host,
        "port": config.port,
        "username": config.username,
        "suggested_config": {},
        "current_state": {
            "raw_outputs": {},
            "ntp_client": {},
            "resource": {},
            "routerboard": {},
        },
        "warnings": [],
        "errors": [],
    }
    client: Optional[paramiko.SSHClient] = None

    try:
        client = connect_ssh_with_auth_retry(config)
        for command in DISCOVERY_COMMANDS:
            try:
                report["current_state"]["raw_outputs"][command] = run_raw_command(client, command)
            except Exception as error:
                report["warnings"].append(
                    f"{command}: {type(error).__name__}: {error}"
                )

        raw_outputs = report["current_state"]["raw_outputs"]
        identity = parse_identity(raw_outputs.get("/system identity print", ""))
        clock = parse_key_value_output(raw_outputs.get("/system clock print", ""))
        ntp_client = parse_ntp_client(raw_outputs.get("/system ntp client print detail", ""))
        resource = parse_system_resource(raw_outputs.get("/system resource print", ""))
        package_version = parse_package_version(raw_outputs.get("/system package print", ""))
        firmware = parse_routerboard_firmware(
            raw_outputs.get("/system routerboard print", "")
        )
        disabled_services = parse_disabled_services(raw_outputs.get("/ip service print", ""))

        report["current_state"]["ntp_client"] = ntp_client
        report["current_state"]["resource"] = resource
        report["current_state"]["routerboard"] = firmware
        report["current_state"]["disabled_services"] = disabled_services

        report["suggested_config"] = {
            "device": {
                "vendor": "mikrotik",
                "platform": "routeros",
            },
            "host": config.host,
            "port": config.port,
            "username": config.username,
            "password": "",
            "device_name": identity or config.device_name,
            "target_routeros_version": package_version
            or resource.get("version", config.target_routeros_version),
            "enable_apply_config": False,
            "enable_backup": config.enable_backup,
            "enable_report": config.enable_report,
            "timezone": clock.get("time-zone-name", config.timezone),
            "disable_services": disabled_services or config.disable_services,
            "expected": {
                "wan_interface": config.expected_wan_interface,
                "wan_dhcp_client_required": config.expected_wan_dhcp_client_required,
                "lan_bridge": config.expected_lan_bridge,
                "lan_ip_cidr": config.expected_lan_ip_cidr,
                "required_disabled_services": config.required_disabled_services
                or ["ftp", "telnet"],
            },
        }
    except Exception as error:
        report["errors"].append(f"{type(error).__name__}: {error}")
    finally:
        if client:
            client.close()

    return report


def print_discovery_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    suggested = report.get("suggested_config", {})
    current = report.get("current_state", {})
    print()
    print("=" * 72)
    print("MikroTik Day 2 Config Discovery")
    print("=" * 72)
    print(f"{'Host':<18}: {report.get('host', '')}")
    print(f"{'Device Name':<18}: {suggested.get('device_name', '')}")
    print(f"{'RouterOS Version':<18}: {suggested.get('target_routeros_version', '')}")
    print(f"{'Timezone':<18}: {suggested.get('timezone', '')}")
    print(f"{'NTP Status':<18}: {current.get('ntp_client', {}).get('status', '')}")
    print(f"{'Disabled Services':<18}: {', '.join(suggested.get('disable_services', []))}")
    if report.get("warnings"):
        print("-" * 72)
        print("Warnings")
        for warning in report["warnings"]:
            print(f"- {warning}")
    if report.get("errors"):
        print("-" * 72)
        print("Errors")
        for error in report["errors"]:
            print(f"- {error}")
    print("-" * 72)
    print(f"{'JSON report':<18}: {json_path}")
    print(f"{'TXT report':<18}: {txt_path}")
    print("=" * 72)


def print_export_template_summary(template: Dict[str, Any], template_path: Path) -> None:
    print()
    print("=" * 72)
    print("MikroTik Day 2 Golden Config Template")
    print("=" * 72)
    print(f"{'Template':<18}: {template_path}")
    print(f"{'Vendor':<18}: {template.get('device', {}).get('vendor', '')}")
    print(f"{'Platform':<18}: {template.get('device', {}).get('platform', '')}")
    print(f"{'RouterOS Target':<18}: {template.get('target_routeros_version', '')}")
    print(f"{'Timezone':<18}: {template.get('timezone', '')}")
    print(f"{'Apply Enabled':<18}: {template.get('enable_apply_config')}")
    print("=" * 72)


def supports_color() -> bool:
    return sys.stdout.isatty()


def color_text(text: str, color: str) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def result_text(result: Any) -> str:
    text = str(result)
    if text in {"PASS", "True", "synchronized"}:
        return color_text(text, COLOR_GREEN)
    if text in {"FAIL", "False"}:
        return color_text(text, COLOR_RED)
    if text in {"WARNING", "SKIPPED", "waiting"}:
        return color_text(text, COLOR_YELLOW)
    return text


def print_summary(report: Dict[str, Any], json_path: Optional[Path], txt_path: Optional[Path]) -> None:
    divider = "=" * 72
    short_divider = "-" * 72
    print()
    print(color_text(divider, COLOR_CYAN))
    print(color_text("MikroTik Day 2 Auto Setup", COLOR_BOLD))
    print(color_text(divider, COLOR_CYAN))
    print(f"{'Device Name':<16}: {report['device_name']}")
    print(f"{'Host':<16}: {report['host']}")
    print(f"{'RouterOS':<16}: {report['routeros_version']} target={report['target_routeros_version']}")
    print(f"{'Firmware Sync':<16}: {result_text(report['routerboard_firmware_synced'])}")
    print(f"{'NTP Status':<16}: {result_text(report.get('ntp_client', {}).get('status', ''))}")
    print(color_text(short_divider, COLOR_CYAN))
    print(f"{'SSH':<16}: {result_text(report['ssh_connect_result'])}")
    print(f"{'Pre-check':<16}: {result_text(report['precheck_result'])}")
    print(f"{'Version Gate':<16}: {result_text(report['version_gate_result'])}")
    print(f"{'Backup':<16}: {result_text(report['backup_result'])}")
    print(f"{'Baseline Mark':<16}: {result_text(report['baseline_marker_result'])}")
    print(f"{'Apply Config':<16}: {result_text(report['apply_config_result'])}")
    print(f"{'Validation':<16}: {result_text(report['validation_result'])}")
    if report.get("dry_run_commands"):
        print(color_text(short_divider, COLOR_CYAN))
        print(color_text("Dry-run commands", COLOR_BOLD))
        for command in report["dry_run_commands"]:
            print(color_text(f"- {command}", COLOR_DIM))
    if report.get("manual_update_steps"):
        print(color_text(short_divider, COLOR_CYAN))
        print(color_text("Manual RouterOS update guidance", COLOR_BOLD))
        for step in report["manual_update_steps"]:
            print(f"- {step}")
    if report["warnings"]:
        print(color_text(short_divider, COLOR_CYAN))
        print(color_text("Warnings", COLOR_YELLOW))
        for warning in report["warnings"]:
            print(f"- {warning}")
    if report["errors"]:
        print(color_text(short_divider, COLOR_CYAN))
        print(color_text("Errors", COLOR_RED))
        for error in report["errors"]:
            print(f"- {error}")
    if json_path and txt_path:
        print(color_text(short_divider, COLOR_CYAN))
        print(f"{'JSON report':<16}: {color_text(str(json_path), COLOR_DIM)}")
        print(f"{'TXT report':<16}: {color_text(str(txt_path), COLOR_DIM)}")
    print(color_text(divider, COLOR_CYAN))


def run_day2_auto_setup(config: Day2Config) -> Dict[str, Any]:
    report = make_empty_report(config)
    client: Optional[paramiko.SSHClient] = None

    try:
        client = connect_ssh_with_auth_retry(config)
        report["ssh_connect_result"] = "PASS"

        run_setup_precheck(client, config, report)
        if report["precheck_result"] == "FAIL":
            report["validation_result"] = "FAIL"
            return ensure_report_fields(report)

        collect_preflight(client, report)

        if config.enable_backup:
            try:
                run_backup_set(client, "day2-before-auto-setup", report)
                report["backup_result"] = "PASS"
            except Exception as error:
                report["backup_result"] = "FAIL"
                report["errors"].append(f"Before backup failed: {type(error).__name__}: {error}")
        else:
            report["backup_result"] = "SKIPPED"
            report["warnings"].append("enable_backup=false; before/after backups were skipped.")

        apply_or_dry_run(client, config, report)

        if config.enable_backup and report["backup_result"] == "PASS":
            try:
                run_backup_set(client, "day2-after-auto-setup", report)
            except Exception as error:
                report["backup_result"] = "FAIL"
                report["errors"].append(f"After backup failed: {type(error).__name__}: {error}")

        validate_after_apply(client, report)

        if config.enable_apply_config:
            create_baseline_marker_backup(client, report)
    except Exception as error:
        if report["ssh_connect_result"] != "PASS":
            report["ssh_connect_result"] = "FAIL"
        report["errors"].append(f"{type(error).__name__}: {error}")
        if report["apply_config_result"] == "SKIPPED":
            report["validation_result"] = "FAIL"
    finally:
        if client:
            client.close()

    return ensure_report_fields(report)


def main() -> int:
    try:
        args = parse_args()
        if args.export_template:
            template = export_golden_template()
            print_export_template_summary(template, GOLDEN_TEMPLATE_PATH)
            return 0

        config = load_config(CONFIG_PATH)
        if args.dry_run:
            config.enable_apply_config = False
        config.host = get_host(config.host)
        config.password = get_password(config.password)
        if args.discover_config:
            report = discover_day2_config(config)
            json_path, txt_path = write_discovery_report(report)
            print_discovery_summary(report, json_path, txt_path)
            return 0 if not report.get("errors") else 1
        validate_identity_name(config.device_name)
        validate_disable_services(config.disable_services)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    try:
        report = run_day2_auto_setup(config)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130

    json_path: Optional[Path] = None
    txt_path: Optional[Path] = None
    if config.enable_report:
        json_path, txt_path = write_reports(report)
    else:
        report["warnings"].append("enable_report=false; report files were not written.")

    print_summary(report, json_path, txt_path)

    if report["ssh_connect_result"] == "FAIL" or report["validation_result"] == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
