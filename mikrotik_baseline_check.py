import argparse
import getpass
import json
import os
import re
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko


DEFAULT_ROUTER_IP = "192.168.88.1"
DEFAULT_SSH_PORT = 22
DEFAULT_USERNAME = "admin"
CONFIG_PATH = Path("config.json")
REPORT_DIR = Path("reports") / "day1"

COMMAND_TIMEOUT_SECONDS = 20
SSH_TIMEOUT_SECONDS = 15

READ_ONLY_COMMANDS = (
    "/system clock print",
    "/system ntp client print",
    "/ping 8.8.8.8 count=3",
    "/file print",
)

FORBIDDEN_COMMAND_PATTERNS = (
    r"^/system\s+reset-configuration\b",
    r"^/system\s+reboot\b",
    r"^/system\s+backup\s+load\b",
    r"^/import\b",
    r"^/system\s+identity\s+set\s+name\s*=",
    r"\b(add|set|remove|enable|disable)\b.*\b(ip|firewall|bridge|dhcp)\b",
)

COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_DIM = "\033[2m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"


@dataclass
class RouterConfig:
    router_ip: str
    ssh_port: int
    username: str
    password: str


class CommandTimeoutError(RuntimeError):
    pass


class UnexpectedOutputError(RuntimeError):
    pass


def load_config(path: Path) -> RouterConfig:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Create it from config.example.json and set the password."
        )

    with path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)

    return RouterConfig(
        router_ip=raw_config.get("router_ip", DEFAULT_ROUTER_IP),
        ssh_port=int(raw_config.get("ssh_port", DEFAULT_SSH_PORT)),
        username=raw_config.get("username", DEFAULT_USERNAME),
        password=str(raw_config.get("password", "")),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MikroTik reset baseline acceptance automation."
    )
    parser.add_argument(
        "--device-name",
        help="Device name used for report identification, and optionally RouterOS identity with --set-identity.",
    )
    parser.add_argument(
        "--set-identity",
        action="store_true",
        help="Set RouterOS /system identity name to --device-name before running baseline checks.",
    )
    return parser.parse_args()


def get_device_name(arg_value: Optional[str]) -> str:
    if arg_value and arg_value.strip():
        return arg_value.strip()

    device_name = input("Please input device name:").strip()
    if not device_name:
        raise ValueError("Device name is required.")
    return device_name


def get_password(default_password: str) -> str:
    password = getpass.getpass(
        "Please input SSH password (press Enter to use config.json default): "
    )
    if password:
        return password

    if default_password:
        return default_password

    raise ValueError("SSH password is required when config.json has no default password.")


def normalize_output(output: str) -> str:
    return re.sub(r"\s+", " ", output.strip()).lower()


def validate_read_only_command(command: str) -> None:
    if command not in READ_ONLY_COMMANDS:
        raise ValueError(f"Command is not in the read-only allowlist: {command}")

    normalized = command.strip().lower()
    for pattern in FORBIDDEN_COMMAND_PATTERNS:
        if re.search(pattern, normalized):
            raise ValueError(f"Forbidden command blocked: {command}")


def validate_identity_name(device_name: str) -> None:
    if not device_name:
        raise ValueError("Device name is required before setting RouterOS identity.")
    if len(device_name) > 64:
        raise ValueError("Device name must be 64 characters or fewer for RouterOS identity.")
    if "\n" in device_name or "\r" in device_name:
        raise ValueError("Device name must not contain newline characters.")


def quote_routeros_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def make_keyboard_interactive_handler(password: str):
    def handler(
        _title: str,
        _instructions: str,
        prompts: List[Tuple[str, bool]],
    ) -> List[str]:
        return [password for _prompt, _echo in prompts]

    return handler


def connect_ssh_keyboard_interactive(config: RouterConfig) -> paramiko.SSHClient:
    sock: Optional[socket.socket] = None
    transport: Optional[paramiko.Transport] = None

    try:
        sock = socket.create_connection(
            (config.router_ip, config.ssh_port),
            timeout=SSH_TIMEOUT_SECONDS,
        )
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


def connect_ssh(config: RouterConfig) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=config.router_ip,
            port=config.ssh_port,
            username=config.username,
            password=config.password,
            timeout=SSH_TIMEOUT_SECONDS,
            banner_timeout=SSH_TIMEOUT_SECONDS,
            auth_timeout=SSH_TIMEOUT_SECONDS,
            look_for_keys=False,
            allow_agent=False,
        )
        return client
    except paramiko.AuthenticationException:
        client.close()
        return connect_ssh_keyboard_interactive(config)


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


def connect_ssh_with_auth_retry(
    config: RouterConfig,
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
            config.password = getpass.getpass("Please input SSH password: ")
            if not config.password:
                print("Empty password entered; retrying may fail.")

    if last_error:
        raise last_error

    raise paramiko.AuthenticationException("Authentication failed.")


def run_command(
    client: paramiko.SSHClient,
    command: str,
    timeout_seconds: int = COMMAND_TIMEOUT_SECONDS,
) -> str:
    validate_read_only_command(command)
    return run_raw_command(client, command, timeout_seconds)


def set_routeros_identity(client: paramiko.SSHClient, device_name: str) -> Dict[str, Any]:
    validate_identity_name(device_name)
    command = f"/system identity set name={quote_routeros_value(device_name)}"

    try:
        run_raw_command(client, command)
        return make_check(
            "set RouterOS identity",
            True,
            f"/system identity name is set to {device_name}",
            "RouterOS identity was updated because --set-identity was provided.",
            command,
        )
    except Exception as error:
        return make_check(
            "set RouterOS identity",
            False,
            f"/system identity name is set to {device_name}",
            f"{type(error).__name__}: {error}",
            command,
        )


def make_check(
    name: str,
    result: bool,
    expected: str,
    details: str,
    command: Optional[str] = None,
) -> Dict[str, Any]:
    check: Dict[str, Any] = {
        "name": name,
        "result": "PASS" if result else "FAIL",
        "expected": expected,
        "details": details,
    }
    if command:
        check["command"] = command
    return check


def supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color_text(text: str, color: str) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def result_text(result: str) -> str:
    if result == "PASS":
        return color_text(result, COLOR_GREEN)
    if result == "FAIL":
        return color_text(result, COLOR_RED)
    return color_text(result, COLOR_YELLOW)


def output_has_field(output: str, field: str, value: str) -> bool:
    normalized = normalize_output(output)
    expected = f"{field.lower()}: {value.lower()}"
    return expected in normalized


def validate_ping_output(output: str) -> bool:
    normalized = normalize_output(output)

    received_match = re.search(r"\breceived\s*[=:]\s*(\d+)\b", normalized)
    loss_match = re.search(r"\bpacket-loss\s*[=:]\s*(\d+)%", normalized)

    if not received_match and not loss_match:
        raise UnexpectedOutputError(
            "Unable to find received or packet-loss in ping output."
        )

    if received_match and int(received_match.group(1)) > 0:
        return True

    if loss_match and int(loss_match.group(1)) != 100:
        return True

    return False


def validate_file_exists(output: str, filename: str) -> bool:
    return filename.lower() in output.lower()


def build_reports(
    device_name: str,
    config: RouterConfig,
    checks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    overall_result = "PASS" if all(check["result"] == "PASS" for check in checks) else "FAIL"
    return {
        "device_name": device_name,
        "router_ip": config.router_ip,
        "ssh_port": config.ssh_port,
        "overall_result": overall_result,
        "checks": checks,
    }


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    title = "MikroTik Baseline Acceptance"
    divider = "=" * 72
    short_divider = "-" * 72
    lines = [
        divider,
        title,
        divider,
        f"{'Device Name':<16}: {report['device_name']}",
        f"{'Router IP':<16}: {report['router_ip']}",
        f"{'SSH Port':<16}: {report['ssh_port']}",
        f"{'Overall Result':<16}: {report['overall_result']}",
        short_divider,
        "Checks",
        f"{'No.':<4} {'Result':<8} {'Check Item':<34} Details",
        short_divider,
    ]

    for index, check in enumerate(report["checks"], start=1):
        lines.append(
            f"{index:<4} {check['result']:<8} "
            f"{check['name']:<34} {check['details']}"
        )

    failed_checks = [check for check in report["checks"] if check["result"] == "FAIL"]
    if failed_checks:
        lines.extend([short_divider, "Failed Checks"])
        for check in failed_checks:
            lines.append(f"- {check['name']}: {check['details']}")

    lines.extend(
        [
            short_divider,
            "Reports",
            f"{'JSON':<16}: {json_path}",
            f"{'TXT':<16}: {txt_path}",
            f"{'Latest JSON':<16}: {REPORT_DIR / 'report.json'}",
            f"{'Latest TXT':<16}: {REPORT_DIR / 'report.txt'}",
            divider,
        ]
    )

    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = report["overall_result"]
    json_path = REPORT_DIR / f"report_{timestamp}_{result}.json"
    txt_path = REPORT_DIR / f"report_{timestamp}_{result}.txt"
    latest_json_path = REPORT_DIR / "report.json"
    latest_txt_path = REPORT_DIR / "report.txt"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with latest_json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")

    text_report = build_text_report(report, json_path, txt_path)
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(text_report)
    with latest_txt_path.open("w", encoding="utf-8") as file:
        file.write(text_report)

    return json_path, txt_path


def print_console_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    title = "MikroTik Baseline Acceptance"
    divider = "=" * 72
    short_divider = "-" * 72

    print()
    print(color_text(divider, COLOR_CYAN))
    print(color_text(title, COLOR_BOLD))
    print(color_text(divider, COLOR_CYAN))
    print(f"{'Device Name':<16}: {report['device_name']}")
    print(f"{'Router IP':<16}: {report['router_ip']}")
    print(f"{'SSH Port':<16}: {report['ssh_port']}")
    print(f"{'Overall Result':<16}: {result_text(report['overall_result'])}")
    print(color_text(short_divider, COLOR_CYAN))
    print(color_text("Checks", COLOR_BOLD))
    print(f"{'No.':<4} {'Result':<8} {'Check Item':<34} Details")
    print(color_text(short_divider, COLOR_CYAN))

    plain_result_width = 8
    for index, check in enumerate(report["checks"], start=1):
        colored_result = result_text(check["result"])
        result_padding = " " * max(0, plain_result_width - len(check["result"]))
        print(
            f"{index:<4} {colored_result}{result_padding} "
            f"{check['name']:<34} {check['details']}"
        )

    failed_checks = [check for check in report["checks"] if check["result"] == "FAIL"]
    if failed_checks:
        print(color_text(short_divider, COLOR_CYAN))
        print(color_text("Failed Checks", COLOR_RED))
        for check in failed_checks:
            print(f"- {check['name']}: {check['details']}")

    print(color_text(short_divider, COLOR_CYAN))
    print(color_text("Reports", COLOR_BOLD))
    print(f"{'JSON':<16}: {color_text(str(json_path), COLOR_DIM)}")
    print(f"{'TXT':<16}: {color_text(str(txt_path), COLOR_DIM)}")
    print(f"{'Latest JSON':<16}: {color_text(str(REPORT_DIR / 'report.json'), COLOR_DIM)}")
    print(f"{'Latest TXT':<16}: {color_text(str(REPORT_DIR / 'report.txt'), COLOR_DIM)}")
    print(color_text(divider, COLOR_CYAN))


def add_command_failure_checks(
    checks: List[Dict[str, Any]],
    command: str,
    error: Exception,
    names: List[str],
) -> None:
    for name in names:
        checks.append(
            make_check(
                name=name,
                result=False,
                expected="Command completes and output matches expected RouterOS fields.",
                details=f"{type(error).__name__}: {error}",
                command=command,
            )
        )


def run_acceptance_checks(client: paramiko.SSHClient) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    commands: Dict[str, str] = {}
    for command in READ_ONLY_COMMANDS:
        try:
            commands[command] = run_command(client, command)
        except Exception as error:
            if command == "/system clock print":
                add_command_failure_checks(
                    checks,
                    command,
                    error,
                    [
                        "clock timezone is Asia/Taipei",
                        "clock gmt-offset is +08:00",
                    ],
                )
            elif command == "/system ntp client print":
                add_command_failure_checks(
                    checks,
                    command,
                    error,
                    [
                        "ntp client is enabled",
                        "ntp client is synchronized",
                    ],
                )
            elif command == "/ping 8.8.8.8 count=3":
                add_command_failure_checks(
                    checks,
                    command,
                    error,
                    ["ping 8.8.8.8 receives packets"],
                )
            elif command == "/file print":
                add_command_failure_checks(
                    checks,
                    command,
                    error,
                    [
                        "backup file exists",
                        "rsc export file exists",
                    ],
                )

    clock_output = commands.get("/system clock print")
    if clock_output is not None:
        checks.append(
            make_check(
                "clock timezone is Asia/Taipei",
                output_has_field(clock_output, "time-zone-name", "Asia/Taipei"),
                "time-zone-name: Asia/Taipei",
                "Field was checked in /system clock print output.",
                "/system clock print",
            )
        )
        checks.append(
            make_check(
                "clock gmt-offset is +08:00",
                output_has_field(clock_output, "gmt-offset", "+08:00"),
                "gmt-offset: +08:00",
                "Field was checked in /system clock print output.",
                "/system clock print",
            )
        )

    ntp_output = commands.get("/system ntp client print")
    if ntp_output is not None:
        checks.append(
            make_check(
                "ntp client is enabled",
                output_has_field(ntp_output, "enabled", "yes"),
                "enabled: yes",
                "Field was checked in /system ntp client print output.",
                "/system ntp client print",
            )
        )
        checks.append(
            make_check(
                "ntp client is synchronized",
                output_has_field(ntp_output, "status", "synchronized"),
                "status: synchronized",
                "Field was checked in /system ntp client print output.",
                "/system ntp client print",
            )
        )

    ping_output = commands.get("/ping 8.8.8.8 count=3")
    if ping_output is not None:
        try:
            ping_passed = validate_ping_output(ping_output)
            ping_details = "received > 0 or packet-loss is not 100%."
        except UnexpectedOutputError as error:
            ping_passed = False
            ping_details = f"Unexpected RouterOS output format: {error}"
        checks.append(
            make_check(
                "ping 8.8.8.8 receives packets",
                ping_passed,
                "received > 0 or packet-loss is not 100%",
                ping_details,
                "/ping 8.8.8.8 count=3",
            )
        )

    file_output = commands.get("/file print")
    if file_output is not None:
        checks.append(
            make_check(
                "backup file exists",
                validate_file_exists(file_output, "baseline-wan-ntp-ok.backup"),
                "baseline-wan-ntp-ok.backup exists",
                "Filename was searched in /file print output.",
                "/file print",
            )
        )
        checks.append(
            make_check(
                "rsc export file exists",
                validate_file_exists(file_output, "baseline-wan-ntp-ok.rsc"),
                "baseline-wan-ntp-ok.rsc exists",
                "Filename was searched in /file print output.",
                "/file print",
            )
        )

    return checks


def main() -> int:
    try:
        args = parse_args()
        device_name = get_device_name(args.device_name)
        config = load_config(CONFIG_PATH)
        config.password = get_password(config.password)
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    checks: List[Dict[str, Any]] = []
    client: Optional[paramiko.SSHClient] = None

    try:
        client = connect_ssh_with_auth_retry(config)
        checks.append(
            make_check(
                "ssh login",
                True,
                "SSH login succeeds.",
                "Authenticated successfully.",
            )
        )
        if args.set_identity:
            checks.append(set_routeros_identity(client, device_name))
        checks.extend(run_acceptance_checks(client))
    except paramiko.AuthenticationException as error:
        checks.append(
            make_check(
                "ssh login",
                False,
                "SSH login succeeds.",
                f"Authentication failed: {error}",
            )
        )
    except (socket.timeout, TimeoutError) as error:
        checks.append(
            make_check(
                "ssh login",
                False,
                "SSH login succeeds.",
                f"SSH timeout: {error}",
            )
        )
    except paramiko.ssh_exception.NoValidConnectionsError as error:
        checks.append(
            make_check(
                "ssh login",
                False,
                "SSH login succeeds.",
                f"Unable to connect to RouterOS SSH: {error}",
            )
        )
    except paramiko.SSHException as error:
        checks.append(
            make_check(
                "ssh login",
                False,
                "SSH login succeeds.",
                f"SSH error: {error}",
            )
        )
    finally:
        if client:
            client.close()

    report = build_reports(device_name, config, checks)
    json_path, txt_path = write_reports(report)

    print_console_summary(report, json_path, txt_path)

    return 0 if report["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
