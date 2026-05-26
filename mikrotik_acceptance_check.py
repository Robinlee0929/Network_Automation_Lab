import argparse
import json
import re
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
    parse_identity,
    run_raw_command,
)


REPORT_ROOT = Path("reports")

CHECK_COMMANDS = {
    "identity": "/system identity print",
    "interfaces": "/interface print",
    "bridge_ports": "/interface bridge port print",
    "dhcp_client": "/ip dhcp-client print detail",
    "bridges": "/interface bridge print",
    "ip_address": "/ip address print",
    "services": "/ip service print",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MikroTik setup acceptance check.")
    parser.add_argument("--device-name", help="Device name expected on RouterOS.")
    return parser.parse_args()


def get_device_name(arg_value: Optional[str], default_value: str = "") -> str:
    if arg_value and arg_value.strip():
        return arg_value.strip()
    if default_value.strip():
        return default_value.strip()
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


def interface_exists(output: str, interface_name: str) -> bool:
    return interface_name.lower() in normalize_output(output)


def interface_in_bridge(output: str, interface_name: str) -> bool:
    normalized = normalize_output(output)
    return interface_name.lower() in normalized


def dhcp_client_for_interface(output: str, interface_name: str) -> Dict[str, Any]:
    normalized_interface = interface_name.lower()
    for block in split_routeros_records(output):
        normalized = normalize_output(block)
        if normalized_interface not in normalized:
            continue
        return {
            "exists": True,
            "enabled": "disabled: true" not in normalized
            and "disabled=true" not in normalized
            and " x " not in f" {normalized} ",
            "add_default_route": "add-default-route: yes" in normalized
            or "add-default-route=yes" in normalized,
            "raw": block,
        }
    return {"exists": False, "enabled": False, "add_default_route": False, "raw": ""}


def split_routeros_records(output: str) -> List[str]:
    records: List[str] = []
    current: List[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                records.append("\n".join(current))
                current = []
            continue
        if re.match(r"^\d+\s", stripped) and current:
            records.append("\n".join(current))
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        records.append("\n".join(current))
    return records


def bridge_exists(output: str, bridge_name: str) -> bool:
    return bridge_name.lower() in normalize_output(output)


def bridge_ip_matches(output: str, bridge_name: str, lan_ip_cidr: str) -> bool:
    normalized = normalize_output(output)
    return bridge_name.lower() in normalized and lan_ip_cidr.lower() in normalized


def service_states(output: str) -> Dict[str, bool]:
    states: Dict[str, bool] = {}
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
        elif len(parts) >= 2:
            flags = list(parts[0].upper())
            service_name = parts[1]
        else:
            continue
        if service_name in known_services:
            states[service_name] = "X" not in flags
    return states


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
    errors: List[Dict[str, Any]] = []
    for key, command in CHECK_COMMANDS.items():
        try:
            outputs[key] = run_raw_command(client, command)
        except Exception as error:
            outputs[key] = ""
            errors.append(
                make_result(
                    f"command {command}",
                    "FAIL",
                    f"{type(error).__name__}: {error}",
                    command,
                    "",
                )
            )
    return outputs, errors


def evaluate_setup_acceptance(
    outputs: Dict[str, str],
    device_name: str,
    config: Day2Config,
) -> List[Dict[str, Any]]:
    expected_disabled = config.required_disabled_services or ["ftp", "telnet"]
    results: List[Dict[str, Any]] = []

    identity = parse_identity(outputs.get("identity", ""))
    results.append(
        make_result(
            "identity matches device name",
            "PASS" if identity == device_name else "FAIL",
            f"identity={identity or 'unknown'}, expected={device_name}.",
            CHECK_COMMANDS["identity"],
            outputs.get("identity", ""),
        )
    )

    wan_interface = config.expected_wan_interface
    wan_exists = interface_exists(outputs.get("interfaces", ""), wan_interface)
    results.append(
        make_result(
            f"{wan_interface} interface exists",
            "PASS" if wan_exists else "FAIL",
            f"{wan_interface} {'exists' if wan_exists else 'was not found'}.",
            CHECK_COMMANDS["interfaces"],
            outputs.get("interfaces", ""),
        )
    )

    in_bridge = interface_in_bridge(outputs.get("bridge_ports", ""), wan_interface)
    results.append(
        make_result(
            f"{wan_interface} is not in LAN bridge",
            "FAIL" if in_bridge else "PASS",
            f"{wan_interface} {'is still in bridge ports' if in_bridge else 'is not in bridge ports'}.",
            CHECK_COMMANDS["bridge_ports"],
            outputs.get("bridge_ports", ""),
        )
    )

    dhcp = dhcp_client_for_interface(outputs.get("dhcp_client", ""), wan_interface)
    dhcp_required = config.expected_wan_dhcp_client_required
    results.append(
        make_result(
            f"{wan_interface} DHCP client exists",
            "PASS" if dhcp["exists"] else ("FAIL" if dhcp_required else "SKIP"),
            f"DHCP client {'exists' if dhcp['exists'] else 'not found'} on {wan_interface}.",
            CHECK_COMMANDS["dhcp_client"],
            outputs.get("dhcp_client", ""),
        )
    )
    results.append(
        make_result(
            f"{wan_interface} DHCP client enabled",
            "PASS" if dhcp["enabled"] else ("FAIL" if dhcp_required else "SKIP"),
            "DHCP client is enabled." if dhcp["enabled"] else "DHCP client is disabled or missing.",
            CHECK_COMMANDS["dhcp_client"],
            outputs.get("dhcp_client", ""),
        )
    )
    results.append(
        make_result(
            f"{wan_interface} DHCP add-default-route",
            "PASS" if dhcp["add_default_route"] else ("FAIL" if dhcp_required else "SKIP"),
            (
                "DHCP client add-default-route=yes."
                if dhcp["add_default_route"]
                else "DHCP client add-default-route is not yes or client is missing."
            ),
            CHECK_COMMANDS["dhcp_client"],
            outputs.get("dhcp_client", ""),
        )
    )

    lan_bridge = config.expected_lan_bridge
    lan_bridge_exists = bridge_exists(outputs.get("bridges", ""), lan_bridge)
    results.append(
        make_result(
            "LAN bridge exists",
            "PASS" if lan_bridge_exists else "FAIL",
            f"Bridge {lan_bridge} {'exists' if lan_bridge_exists else 'was not found'}.",
            CHECK_COMMANDS["bridges"],
            outputs.get("bridges", ""),
        )
    )

    lan_ip_ok = bridge_ip_matches(
        outputs.get("ip_address", ""),
        lan_bridge,
        config.expected_lan_ip_cidr,
    )
    results.append(
        make_result(
            "LAN bridge IP matches expected",
            "PASS" if lan_ip_ok else "FAIL",
            f"Expected {config.expected_lan_ip_cidr} on {lan_bridge}.",
            CHECK_COMMANDS["ip_address"],
            outputs.get("ip_address", ""),
        )
    )

    services = service_states(outputs.get("services", ""))
    ssh_enabled = services.get("ssh", False)
    results.append(
        make_result(
            "ssh service enabled",
            "PASS" if ssh_enabled else "FAIL",
            "ssh service is enabled." if ssh_enabled else "ssh service is disabled or missing.",
            CHECK_COMMANDS["services"],
            outputs.get("services", ""),
        )
    )

    unsafe_enabled = [
        service for service in expected_disabled if services.get(service, False)
    ]
    results.append(
        make_result(
            "unsafe services disabled",
            "PASS" if not unsafe_enabled else "WARNING",
            (
                f"{', '.join(expected_disabled)} are disabled."
                if not unsafe_enabled
                else f"Services still enabled: {', '.join(unsafe_enabled)}."
            ),
            CHECK_COMMANDS["services"],
            outputs.get("services", ""),
        )
    )

    return results


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
) -> Dict[str, Any]:
    return {
        "device_name": device_name,
        "host": config.host,
        "check_time": datetime.now().isoformat(timespec="seconds"),
        "expected_config": {
            "wan_interface": config.expected_wan_interface,
            "wan_dhcp_client_required": config.expected_wan_dhcp_client_required,
            "lan_bridge": config.expected_lan_bridge,
            "lan_ip_cidr": config.expected_lan_ip_cidr,
            "required_disabled_services": config.required_disabled_services
            or ["ftp", "telnet"],
        },
        "summary": build_summary(results),
        "check_results": results,
        "failed_items": [
            result["name"] for result in results if result.get("status") == "FAIL"
        ],
        "warning_items": [
            result["name"] for result in results if result.get("status") == "WARNING"
        ],
    }


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    short_divider = "-" * 72
    lines = [
        divider,
        "MikroTik Setup Acceptance Check",
        divider,
        f"{'Device Name':<22}: {report['device_name']}",
        f"{'Host':<22}: {report['host']}",
        f"{'Summary':<22}: {report['summary']}",
        short_divider,
    ]
    for result in report["check_results"]:
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
            f"{'JSON':<22}: {json_path}",
            f"{'TXT':<22}: {txt_path}",
            divider,
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    report_dir = REPORT_ROOT / sanitize_path_name(report["device_name"])
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "day2_setup_check_report.json"
    txt_path = report_dir / "day2_setup_check_report.txt"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report, json_path, txt_path))
    return json_path, txt_path


def run_acceptance_check(device_name: str, config: Day2Config) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    client: Optional[paramiko.SSHClient] = None
    try:
        client = connect_ssh_with_auth_retry(config)
        outputs, command_errors = collect_outputs(client)
        results.extend(command_errors)
        results.extend(evaluate_setup_acceptance(outputs, device_name, config))
    except Exception as error:
        results.append(
            make_result("ssh login", "FAIL", f"{type(error).__name__}: {error}", "ssh", "")
        )
    finally:
        if client:
            client.close()
    return build_report(device_name, config, results)


def print_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    print()
    print("=" * 72)
    print("MikroTik Setup Acceptance Check")
    print("=" * 72)
    print(f"{'Device Name':<18}: {report['device_name']}")
    print(f"{'Host':<18}: {report['host']}")
    print(f"{'Summary':<18}: {report['summary']}")
    print("-" * 72)
    for result in report["check_results"]:
        print(f"{result['status']:<8} {result['name']}: {result['reason']}")
    print("-" * 72)
    print(f"{'JSON report':<18}: {json_path}")
    print(f"{'TXT report':<18}: {txt_path}")
    print("=" * 72)


def main() -> int:
    try:
        args = parse_args()
        config = load_config(CONFIG_PATH)
        device_name = get_device_name(args.device_name, config.device_name)
        config.host = get_host(config.host)
        config.password = get_password(config.password)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    report = run_acceptance_check(device_name, config)
    json_path, txt_path = write_reports(report)
    print_summary(report, json_path, txt_path)
    return 1 if report["summary"]["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
