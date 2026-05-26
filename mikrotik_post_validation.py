import argparse
import getpass
import json
import re
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko

from mikrotik_day2_auto_setup import (
    CONFIG_PATH,
    Day2Config,
    connect_ssh_with_auth_retry,
    get_host,
    get_password,
    load_config,
    parse_key_value_output,
    parse_package_version,
    parse_routerboard_firmware,
    parse_system_resource,
    run_raw_command,
)


REPORT_ROOT = Path("reports")
PING_TARGET_IP = "8.8.8.8"
PING_TARGET_DNS = "google.com"

DAY3_COMMANDS = {
    "resource": "/system resource print",
    "package": "/system package print",
    "routerboard": "/system routerboard print",
    "dhcp_client": "/ip dhcp-client print detail",
    "ip_address": "/ip address print",
    "route": "/ip route print",
    "ping_ip": f"/ping {PING_TARGET_IP} count=3",
    "ping_dns": f"/ping {PING_TARGET_DNS} count=3",
    "service": "/ip service print",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MikroTik post-setup validation automation."
    )
    parser.add_argument("--device-name", help="Device name used for report folder.")
    return parser.parse_args()


def get_device_name(arg_value: Optional[str]) -> str:
    if arg_value and arg_value.strip():
        return arg_value.strip()

    device_name = input("Please input device name: ").strip()
    if not device_name:
        raise ValueError("Device name is required.")
    return device_name


def sanitize_path_name(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    sanitized = sanitized.strip(".-")
    if not sanitized:
        raise ValueError("Device name cannot be converted to a report folder name.")
    return sanitized


def normalize_output(output: str) -> str:
    return re.sub(r"\s+", " ", output.strip()).lower()


def parse_ping_output(output: str) -> bool:
    normalized = normalize_output(output)
    received_match = re.search(r"\breceived\s*[=:]\s*(\d+)\b", normalized)
    loss_match = re.search(r"\bpacket-loss\s*[=:]\s*(\d+)%", normalized)

    if received_match and int(received_match.group(1)) > 0:
        return True
    if loss_match and int(loss_match.group(1)) != 100:
        return True
    return False


def parse_ip_addresses(output: str) -> List[Dict[str, str]]:
    addresses: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    pattern = re.compile(r"([\w-]+)\s*=\s*(\S+)|([\w-]+)\s*:\s*(\S+)")

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("Flags:", "Columns:", "#")):
            continue

        values: Dict[str, str] = {}
        for key_eq, value_eq, key_colon, value_colon in pattern.findall(stripped):
            key = key_eq or key_colon
            value = value_eq or value_colon
            values[key] = value

        if values:
            current.update(values)

        table_match = re.search(
            r"(?P<address>\d+\.\d+\.\d+\.\d+/\d+).*?(?P<interface>[\w.-]*bridge[\w.-]*|ether\d+|sfp\S*)",
            stripped,
            re.IGNORECASE,
        )
        if table_match:
            addresses.append(table_match.groupdict())
            continue

        if current.get("address") and current.get("interface"):
            addresses.append(
                {
                    "address": current["address"],
                    "interface": current["interface"],
                }
            )
            current = {}

    return addresses


def parse_wan_dhcp_client(output: str) -> Dict[str, str]:
    values = parse_key_value_output(output)
    normalized = normalize_output(output)
    interface = values.get("interface", "")
    status = values.get("status", "")
    address = values.get("address", values.get("dhcp-server", ""))

    if not interface:
        interface_match = re.search(r"\binterface\s*[=:]\s*([^\s]+)", normalized)
        if interface_match:
            interface = interface_match.group(1)

    if not status:
        status_match = re.search(r"\bstatus\s*[=:]\s*([^\s]+)", normalized)
        if status_match:
            status = status_match.group(1)

    if not address:
        address_match = re.search(r"\baddress\s*[=:]\s*([0-9.]+)", normalized)
        if address_match:
            address = address_match.group(1)

    return {
        "interface": interface,
        "status": status,
        "address": address,
    }


def has_default_route(output: str) -> bool:
    normalized = normalize_output(output)
    return "0.0.0.0/0" in normalized or "dst-address=0.0.0.0/0" in normalized


def parse_disabled_services(output: str) -> Dict[str, bool]:
    protected = {"ftp": False, "telnet": False, "www": False}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("Flags:", "Columns:", "#", ";;;")):
            continue

        parts = stripped.split()
        if len(parts) >= 3 and parts[0].isdigit():
            flags = parts[1].upper()
            service = parts[2]
        elif len(parts) >= 2:
            flags = parts[0].upper()
            service = parts[1]
        else:
            continue

        if service in protected:
            protected[service] = "X" in flags
    return protected


def make_result(
    name: str,
    status: str,
    reason: str,
    command: str,
    raw_output: str,
) -> Dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "reason": reason,
        "command": command,
        "raw_output": raw_output,
    }


def collect_outputs(client: paramiko.SSHClient) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    outputs: Dict[str, str] = {}
    command_errors: List[Dict[str, Any]] = []

    for key, command in DAY3_COMMANDS.items():
        try:
            outputs[key] = run_raw_command(client, command)
        except Exception as error:
            outputs[key] = ""
            command_errors.append(
                make_result(
                    f"command {command}",
                    "FAIL",
                    f"{type(error).__name__}: {error}",
                    command,
                    "",
                )
            )

    return outputs, command_errors


def evaluate_results(
    outputs: Dict[str, str],
    target_routeros_version: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    resource = parse_system_resource(outputs.get("resource", ""))
    package_version = parse_package_version(outputs.get("package", ""))
    firmware = parse_routerboard_firmware(outputs.get("routerboard", ""))
    dhcp_client = parse_wan_dhcp_client(outputs.get("dhcp_client", ""))
    ip_addresses = parse_ip_addresses(outputs.get("ip_address", ""))

    routeros_version = package_version or resource.get("version", "")
    routeros_status = "PASS" if routeros_version else "FAIL"
    routeros_reason = f"RouterOS version recorded: {routeros_version or 'unknown'}."
    if target_routeros_version and routeros_version and routeros_version != target_routeros_version:
        routeros_status = "WARNING"
        routeros_reason = (
            f"RouterOS version {routeros_version} differs from target "
            f"{target_routeros_version}."
        )
    results.append(
        make_result(
            "RouterOS version",
            routeros_status,
            routeros_reason,
            DAY3_COMMANDS["resource"],
            outputs.get("resource", ""),
        )
    )

    results.append(
        make_result(
            "Package version",
            "PASS" if package_version else "FAIL",
            f"routeros package version: {package_version or 'unknown'}.",
            DAY3_COMMANDS["package"],
            outputs.get("package", ""),
        )
    )

    firmware_synced = (
        bool(firmware.get("current-firmware"))
        and firmware.get("current-firmware") == firmware.get("upgrade-firmware")
    )
    results.append(
        make_result(
            "RouterBOARD firmware",
            "PASS" if firmware_synced else "WARNING",
            (
                "current-firmware equals upgrade-firmware."
                if firmware_synced
                else "current-firmware differs from upgrade-firmware or could not be parsed."
            ),
            DAY3_COMMANDS["routerboard"],
            outputs.get("routerboard", ""),
        )
    )

    wan_status = dhcp_client.get("status", "").lower()
    wan_interface = dhcp_client.get("interface", "")
    results.append(
        make_result(
            "WAN DHCP client",
            "PASS" if wan_status == "bound" else "FAIL",
            (
                f"DHCP client on {wan_interface or 'unknown'} is bound."
                if wan_status == "bound"
                else f"DHCP client status is {wan_status or 'unknown'}."
            ),
            DAY3_COMMANDS["dhcp_client"],
            outputs.get("dhcp_client", ""),
        )
    )

    wan_ip = dhcp_client.get("address", "")
    if not wan_ip:
        for address in ip_addresses:
            interface = address.get("interface", "").lower()
            if interface and "bridge" not in interface:
                wan_ip = address.get("address", "")
                break
    results.append(
        make_result(
            "WAN IP address",
            "PASS" if wan_ip else "FAIL",
            f"WAN IP: {wan_ip or 'not found'}.",
            DAY3_COMMANDS["ip_address"],
            outputs.get("ip_address", ""),
        )
    )

    route_ok = has_default_route(outputs.get("route", ""))
    results.append(
        make_result(
            "Default route",
            "PASS" if route_ok else "FAIL",
            "Default route 0.0.0.0/0 exists." if route_ok else "Default route not found.",
            DAY3_COMMANDS["route"],
            outputs.get("route", ""),
        )
    )

    ip_ping_ok = parse_ping_output(outputs.get("ping_ip", ""))
    results.append(
        make_result(
            "Internet ping",
            "PASS" if ip_ping_ok else "FAIL",
            f"Ping {PING_TARGET_IP} received packets." if ip_ping_ok else f"Ping {PING_TARGET_IP} failed.",
            DAY3_COMMANDS["ping_ip"],
            outputs.get("ping_ip", ""),
        )
    )

    dns_ping_ok = parse_ping_output(outputs.get("ping_dns", ""))
    results.append(
        make_result(
            "DNS ping",
            "PASS" if dns_ping_ok else "FAIL",
            f"Ping {PING_TARGET_DNS} succeeded." if dns_ping_ok else f"Ping {PING_TARGET_DNS} failed.",
            DAY3_COMMANDS["ping_dns"],
            outputs.get("ping_dns", ""),
        )
    )

    lan_ip = ""
    for address in ip_addresses:
        interface = address.get("interface", "").lower()
        if "bridge" in interface:
            lan_ip = address.get("address", "")
            break
    results.append(
        make_result(
            "LAN bridge IP",
            "PASS" if lan_ip else "FAIL",
            f"LAN bridge IP: {lan_ip or 'not found'}.",
            DAY3_COMMANDS["ip_address"],
            outputs.get("ip_address", ""),
        )
    )

    disabled_services = parse_disabled_services(outputs.get("service", ""))
    unsafe_open = [service for service, disabled in disabled_services.items() if not disabled]
    results.append(
        make_result(
            "Service hardening",
            "PASS" if not unsafe_open else "WARNING",
            (
                "ftp, telnet, and www are disabled."
                if not unsafe_open
                else f"Services not disabled: {', '.join(unsafe_open)}."
            ),
            DAY3_COMMANDS["service"],
            outputs.get("service", ""),
        )
    )

    metadata = {
        "routeros_version": routeros_version,
        "package_version": package_version,
        "routerboard_firmware": firmware,
        "wan_ip": wan_ip,
        "lan_ip": lan_ip,
    }
    return results, metadata


def build_summary(results: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {"pass": 0, "fail": 0, "warning": 0, "skip": 0}
    for result in results:
        key = str(result.get("status", "")).lower()
        if key in summary:
            summary[key] += 1
    return summary


def build_report(
    device_name: str,
    config: Day2Config,
    results: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    failed_items = [
        result["name"] for result in results if result.get("status") == "FAIL"
    ]
    warning_items = [
        result["name"] for result in results if result.get("status") == "WARNING"
    ]
    return {
        "device_name": device_name,
        "host": config.host,
        "test_time": datetime.now().isoformat(timespec="seconds"),
        "routeros_version": metadata.get("routeros_version", ""),
        "package_version": metadata.get("package_version", ""),
        "routerboard_firmware": metadata.get("routerboard_firmware", {}),
        "wan_ip": metadata.get("wan_ip", ""),
        "lan_ip": metadata.get("lan_ip", ""),
        "summary": build_summary(results),
        "test_results": results,
        "failed_items": failed_items,
        "warning_items": warning_items,
        "raw_commands": DAY3_COMMANDS,
    }


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    short_divider = "-" * 72
    lines = [
        divider,
        "MikroTik Post-Setup Validation",
        divider,
        f"{'Device Name':<20}: {report['device_name']}",
        f"{'Host':<20}: {report['host']}",
        f"{'RouterOS Version':<20}: {report['routeros_version']}",
        f"{'WAN IP':<20}: {report['wan_ip']}",
        f"{'LAN IP':<20}: {report['lan_ip']}",
        f"{'Summary':<20}: {report['summary']}",
        short_divider,
    ]
    for result in report["test_results"]:
        lines.append(f"{result['status']:<8} {result['name']}: {result['reason']}")

    if report["failed_items"]:
        lines.extend([short_divider, "Failed Items"])
        lines.extend(f"- {item}" for item in report["failed_items"])

    if report["warning_items"]:
        lines.extend([short_divider, "Warning Items"])
        lines.extend(f"- {item}" for item in report["warning_items"])

    lines.extend(
        [
            short_divider,
            f"{'JSON':<20}: {json_path}",
            f"{'TXT':<20}: {txt_path}",
            divider,
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    report_dir = REPORT_ROOT / sanitize_path_name(report["device_name"])
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "day3_test_report.json"
    txt_path = report_dir / "day3_test_report.txt"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report, json_path, txt_path))

    return json_path, txt_path


def print_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    print()
    print("=" * 72)
    print("MikroTik Post-Setup Validation")
    print("=" * 72)
    print(f"{'Device Name':<18}: {report['device_name']}")
    print(f"{'Host':<18}: {report['host']}")
    print(f"{'WAN IP':<18}: {report['wan_ip']}")
    print(f"{'LAN IP':<18}: {report['lan_ip']}")
    print(f"{'Summary':<18}: {report['summary']}")
    print("-" * 72)
    for result in report["test_results"]:
        print(f"{result['status']:<8} {result['name']}: {result['reason']}")
    print("-" * 72)
    print(f"{'JSON report':<18}: {json_path}")
    print(f"{'TXT report':<18}: {txt_path}")
    print("=" * 72)


def run_post_validation(device_name: str, config: Day2Config) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    client: Optional[paramiko.SSHClient] = None

    try:
        client = connect_ssh_with_auth_retry(config)
        outputs, command_errors = collect_outputs(client)
        results.extend(command_errors)
        evaluated_results, metadata = evaluate_results(
            outputs,
            config.target_routeros_version,
        )
        results.extend(evaluated_results)
    except (paramiko.AuthenticationException, socket.timeout, TimeoutError) as error:
        results.append(
            make_result(
                "SSH login",
                "FAIL",
                f"{type(error).__name__}: {error}",
                "ssh",
                "",
            )
        )
    finally:
        if client:
            client.close()

    return build_report(device_name, config, results, metadata)


def main() -> int:
    try:
        args = parse_args()
        device_name = get_device_name(args.device_name)
        config = load_config(CONFIG_PATH)
        config.host = get_host(config.host)
        config.password = get_password(config.password)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    try:
        report = run_post_validation(device_name, config)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130

    json_path, txt_path = write_reports(report)
    print_summary(report, json_path, txt_path)

    return 1 if report["summary"]["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
