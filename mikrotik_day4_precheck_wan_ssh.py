import getpass
import ipaddress
import json
import re
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko

from mikrotik_day2_auto_setup import (
    COLOR_BOLD,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    Day2Config,
    color_text,
    connect_ssh_with_auth_retry,
    parse_key_value_output,
    quote_routeros_value,
    run_raw_command,
)
from mikrotik_post_validation import sanitize_path_name


REPORT_ROOT = Path("reports")
SSH_RULE_COMMENT = "Day4 allow SSH from automation source"
DEFAULT_WAN_DROP_COMMENT = "defconf: drop all not coming from LAN"
WAN_INTERFACE = "ether1"


def get_required_input(prompt: str) -> str:
    value = input(prompt).strip()
    if not value:
        raise ValueError(f"{prompt.strip()} is required.")
    return value


def get_allowed_source() -> Tuple[str, str]:
    source = get_required_input(
        "Please input allowed SSH source, for example 192.168.0.159/32 or 192.168.0.0/24: "
    )
    network = ipaddress.ip_network(source, strict=False)
    if network.prefixlen == 0:
        raise ValueError("0.0.0.0/0 is not allowed for WAN SSH access.")
    if network.version != 4:
        raise ValueError("Only IPv4 allowed SSH sources are supported.")
    mode = "single Automation PC IP" if network.prefixlen == 32 else "Home LAN subnet"
    return str(network), mode


def build_config(lan_management_ip: str, username: str, password: str, device_name: str) -> Day2Config:
    return Day2Config(
        host=lan_management_ip,
        port=22,
        username=username,
        password=password,
        device_name=device_name,
        target_routeros_version="",
        enable_apply_config=False,
        enable_backup=False,
        enable_report=True,
        timezone="",
        disable_services=[],
    )


def parse_detail_values(output: str) -> Dict[str, str]:
    values = parse_key_value_output(output)
    for key, value in re_findall_key_values(output):
        values[key] = value.strip('"')
    return values


def re_findall_key_values(output: str) -> List[Tuple[str, str]]:
    return re.findall(r"([\w-]+)=((?:\"[^\"]*\")|\S+)", output)


def parse_ssh_service(output: str) -> Dict[str, Any]:
    values = parse_detail_values(output)
    if values.get("name") == "ssh":
        disabled = values.get("disabled", "no").lower() in {"yes", "true"}
        return {
            "exists": True,
            "enabled": not disabled,
            "raw": output.strip(),
        }

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("Flags:", "Columns:", "#", ";;;")):
            continue
        parts = stripped.split()
        if parts and parts[0].isdigit():
            flags: List[str] = []
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

        if service_name == "ssh":
            return {
                "exists": True,
                "enabled": "X" not in flags,
                "raw": stripped,
            }
    return {"exists": False, "enabled": False, "raw": ""}


def parse_wan_dhcp_ip(output: str) -> str:
    values = parse_detail_values(output)
    if values.get("address"):
        return values["address"]
    for line in output.splitlines():
        stripped = line.strip()
        if "interface=ether1" not in stripped and "interface: ether1" not in stripped:
            continue
        parts = stripped.replace("=", " ").replace(":", " ").split()
        for index, token in enumerate(parts):
            if token == "address" and index + 1 < len(parts):
                return parts[index + 1]
    return ""


def parse_firewall_rule(output: str) -> Dict[str, Any]:
    values = parse_detail_values(output)
    normalized = " ".join(output.split())
    exists = any(
        values.get(key)
        for key in (
            "chain",
            "action",
            "protocol",
            "dst-port",
            "src-address",
            "in-interface-list",
        )
    )
    return {
        "exists": exists,
        "chain": values.get("chain", ""),
        "action": values.get("action", ""),
        "protocol": values.get("protocol", ""),
        "dst-port": values.get("dst-port", ""),
        "src-address": values.get("src-address", ""),
        "in-interface-list": values.get("in-interface-list", ""),
        "disabled": values.get("disabled", ""),
        "raw": output.strip(),
        "normalized": normalized,
    }


def address_matches(actual: str, expected: str) -> bool:
    if not actual or not expected:
        return False
    try:
        actual_network = ipaddress.ip_network(
            actual if "/" in actual else f"{actual}/32",
            strict=False,
        )
        expected_network = ipaddress.ip_network(expected, strict=False)
    except ValueError:
        return actual == expected
    return actual_network == expected_network


def rule_matches(rule: Dict[str, Any], allowed_source: str) -> bool:
    if not rule.get("exists"):
        return False
    return (
        rule.get("chain") == "input"
        and rule.get("action") == "accept"
        and rule.get("protocol") == "tcp"
        and rule.get("dst-port") == "22"
        and address_matches(rule.get("src-address", ""), allowed_source)
        and rule.get("in-interface-list") == "WAN"
        and str(rule.get("disabled", "")).lower() not in {"yes", "true"}
    )


def ensure_ssh_service(client: paramiko.SSHClient) -> Dict[str, Any]:
    before_output = run_raw_command(client, "/ip service print detail where name=ssh")
    before = parse_ssh_service(before_output)
    if not before["exists"]:
        return {
            "exists": False,
            "enabled": False,
            "action": "missing",
            "raw": before_output,
        }
    if not before["enabled"]:
        run_raw_command(client, "/ip service enable [find name=ssh]")
        after_output = run_raw_command(client, "/ip service print detail where name=ssh")
        after = parse_ssh_service(after_output)
        return {
            "exists": True,
            "enabled": after["enabled"],
            "action": "enabled",
            "raw": after_output,
        }
    return {
        "exists": True,
        "enabled": True,
        "action": "already enabled",
        "raw": before_output,
    }


def firewall_rule_print_command() -> str:
    return (
        "/ip firewall filter print detail where comment="
        + quote_routeros_value(SSH_RULE_COMMENT)
    )


def default_drop_print_command() -> str:
    return (
        "/ip firewall filter print detail where comment="
        + quote_routeros_value(DEFAULT_WAN_DROP_COMMENT)
    )


def add_or_update_firewall_rule(
    client: paramiko.SSHClient,
    allowed_source: str,
) -> Dict[str, Any]:
    before_output = run_raw_command(client, firewall_rule_print_command())
    before_rule = parse_firewall_rule(before_output)
    drop_rule_exists = bool(run_raw_command(client, default_drop_print_command()).strip())

    if not before_rule["exists"]:
        rule_status = "added"
        command = (
            "/ip firewall filter add chain=input action=accept protocol=tcp "
            f"dst-port=22 src-address={quote_routeros_value(allowed_source)} "
            f"in-interface-list=WAN comment={quote_routeros_value(SSH_RULE_COMMENT)}"
        )
        run_raw_command(client, command)
    elif rule_matches(before_rule, allowed_source):
        rule_status = "already existed"
    else:
        rule_status = "updated"
        command = (
            "/ip firewall filter set [find comment="
            f"{quote_routeros_value(SSH_RULE_COMMENT)}] chain=input action=accept "
            f"protocol=tcp dst-port=22 src-address={quote_routeros_value(allowed_source)} "
            "in-interface-list=WAN disabled=no"
        )
        run_raw_command(client, command)

    move_command = (
        f":local allow [/ip firewall filter find comment={quote_routeros_value(SSH_RULE_COMMENT)}]; "
        f":local drop [/ip firewall filter find comment={quote_routeros_value(DEFAULT_WAN_DROP_COMMENT)}]; "
        ':if (([:len $allow] > 0) and ([:len $drop] > 0)) do={/ip firewall filter move $allow destination=$drop}'
    )
    if drop_rule_exists:
        run_raw_command(client, move_command)

    after_output = run_raw_command(client, firewall_rule_print_command())
    after_rule = parse_firewall_rule(after_output)
    return {
        "status": rule_status,
        "moved_before_default_drop": drop_rule_exists,
        "matches_expected": rule_matches(after_rule, allowed_source),
        "actual": {
            "chain": after_rule.get("chain", ""),
            "action": after_rule.get("action", ""),
            "protocol": after_rule.get("protocol", ""),
            "dst-port": after_rule.get("dst-port", ""),
            "src-address": after_rule.get("src-address", ""),
            "in-interface-list": after_rule.get("in-interface-list", ""),
            "disabled": after_rule.get("disabled", ""),
        },
        "raw": after_output,
    }


def read_wan_dhcp_ip(client: paramiko.SSHClient) -> str:
    output = run_raw_command(
        client,
        f"/ip dhcp-client print detail where interface={WAN_INTERFACE}",
    )
    return parse_wan_dhcp_ip(output)


def build_report(
    device_name: str,
    lan_management_ip: str,
    wan_dhcp_ip: str,
    allowed_source: str,
    allowed_source_mode: str,
    ssh_service: Dict[str, Any],
    firewall_rule: Dict[str, Any],
    errors: List[str],
) -> Dict[str, Any]:
    warnings: List[str] = []
    if allowed_source_mode == "Home LAN subnet":
        warnings.append(
            "Subnet mode was used. This is convenient for a lab, but a /32 Automation PC source is tighter."
        )

    status = "PASS"
    if errors or not ssh_service.get("enabled") or not firewall_rule.get("matches_expected"):
        status = "FAIL"

    return {
        "device_name": device_name,
        "lan_management_ip": lan_management_ip,
        "wan_dhcp_ip": wan_dhcp_ip,
        "allowed_ssh_source": allowed_source,
        "allowed_source_mode": allowed_source_mode,
        "ssh_service_status": {
            "exists": bool(ssh_service.get("exists")),
            "enabled": bool(ssh_service.get("enabled")),
            "action": ssh_service.get("action", ""),
        },
        "firewall_rule_status": {
            "status": firewall_rule.get("status", ""),
            "matches_expected": bool(firewall_rule.get("matches_expected")),
            "moved_before_default_drop": bool(
                firewall_rule.get("moved_before_default_drop")
            ),
            "comment": SSH_RULE_COMMENT,
            "actual": firewall_rule.get("actual", {}),
        },
        "warnings": warnings,
        "errors": errors,
        "overall_result": status,
        "report_time": datetime.now().isoformat(timespec="seconds"),
    }


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    short_divider = "-" * 72
    ssh = report["ssh_service_status"]
    firewall = report["firewall_rule_status"]
    lines = [
        divider,
        "MikroTik Day 4 Pre-check - WAN SSH Management Access",
        divider,
        f"{'Device Name':<28}: {report['device_name']}",
        f"{'LAN Management IP':<28}: {report['lan_management_ip']}",
        f"{'WAN DHCP IP':<28}: {report['wan_dhcp_ip'] or 'not found'}",
        f"{'Allowed SSH Source':<28}: {report['allowed_ssh_source']}",
        f"{'Allowed Source Mode':<28}: {report['allowed_source_mode']}",
        f"{'Overall Result':<28}: {report['overall_result']}",
        short_divider,
        f"{'SSH Service Exists':<28}: {ssh['exists']}",
        f"{'SSH Service Enabled':<28}: {ssh['enabled']}",
        f"{'SSH Service Action':<28}: {ssh['action']}",
        f"{'Firewall Rule Status':<28}: {firewall['status']}",
        f"{'Firewall Rule Matches':<28}: {firewall['matches_expected']}",
        f"{'Moved Before WAN Drop':<28}: {firewall['moved_before_default_drop']}",
    ]
    if report["warnings"]:
        lines.extend([short_divider, "Warnings"])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    if report["errors"]:
        lines.extend([short_divider, "Errors"])
        lines.extend(f"- {error}" for error in report["errors"])
    lines.extend(
        [
            short_divider,
            f"{'JSON report':<28}: {json_path}",
            f"{'TXT report':<28}: {txt_path}",
            divider,
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    report_dir = REPORT_ROOT / sanitize_path_name(report["device_name"])
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "day4_precheck_wan_ssh.json"
    txt_path = report_dir / "day4_precheck_wan_ssh.txt"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report, json_path, txt_path))
    return json_path, txt_path


def result_text(value: Any) -> str:
    text = str(value)
    if text in {"PASS", "True", "already enabled", "already existed", "added", "updated"}:
        return color_text(text, COLOR_GREEN)
    if text in {"FAIL", "False", "missing"}:
        return color_text(text, COLOR_RED)
    if text in {"Home LAN subnet"}:
        return color_text(text, COLOR_YELLOW)
    return text


def run_precheck(
    lan_management_ip: str,
    device_name: str,
    username: str,
    password: str,
    allowed_source: str,
    allowed_source_mode: str,
) -> Dict[str, Any]:
    errors: List[str] = []
    ssh_service: Dict[str, Any] = {"exists": False, "enabled": False, "action": ""}
    firewall_rule: Dict[str, Any] = {
        "status": "",
        "matches_expected": False,
        "moved_before_default_drop": False,
    }
    wan_dhcp_ip = ""
    client: Optional[paramiko.SSHClient] = None

    try:
        config = build_config(lan_management_ip, username, password, device_name)
        client = connect_ssh_with_auth_retry(config)
        ssh_service = ensure_ssh_service(client)
        firewall_rule = add_or_update_firewall_rule(client, allowed_source)
        wan_dhcp_ip = read_wan_dhcp_ip(client)
    except (paramiko.AuthenticationException, socket.timeout, TimeoutError, OSError, ValueError) as error:
        errors.append(f"{type(error).__name__}: {error}")
    finally:
        if client:
            client.close()

    return build_report(
        device_name,
        lan_management_ip,
        wan_dhcp_ip,
        allowed_source,
        allowed_source_mode,
        ssh_service,
        firewall_rule,
        errors,
    )


def print_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    print()
    print(color_text("=" * 72, COLOR_CYAN))
    print(color_text("MikroTik Day 4 Pre-check - WAN SSH Management Access", COLOR_BOLD))
    print(color_text("=" * 72, COLOR_CYAN))
    print(f"{'Device Name':<24}: {report['device_name']}")
    print(f"{'LAN Management IP':<24}: {report['lan_management_ip']}")
    print(f"{'WAN DHCP IP':<24}: {report['wan_dhcp_ip'] or 'not found'}")
    print(f"{'Allowed SSH Source':<24}: {report['allowed_ssh_source']}")
    print(f"{'Allowed Source Mode':<24}: {result_text(report['allowed_source_mode'])}")
    print(f"{'Overall Result':<24}: {result_text(report['overall_result'])}")
    print(color_text("-" * 72, COLOR_CYAN))
    print(f"{'SSH Service':<24}: {result_text(report['ssh_service_status']['action'])}")
    print(f"{'Firewall Rule':<24}: {result_text(report['firewall_rule_status']['status'])}")
    print(
        f"{'Rule Matches Expected':<24}: "
        f"{result_text(report['firewall_rule_status']['matches_expected'])}"
    )
    if report["warnings"]:
        print(color_text("-" * 72, COLOR_CYAN))
        print(color_text("Warnings", COLOR_YELLOW))
        for warning in report["warnings"]:
            print(f"- {warning}")
    if report["errors"]:
        print(color_text("-" * 72, COLOR_CYAN))
        print(color_text("Errors", COLOR_RED))
        for error in report["errors"]:
            print(f"- {error}")
    print(color_text("-" * 72, COLOR_CYAN))
    print(f"{'JSON report':<24}: {json_path}")
    print(f"{'TXT report':<24}: {txt_path}")
    print(color_text("=" * 72, COLOR_CYAN))


def main() -> int:
    try:
        lan_management_ip = get_required_input("Please input LAN management IP: ")
        device_name = get_required_input("Please input device name: ")
        username = get_required_input("Please input username: ")
        password = getpass.getpass("Please input password: ").strip()
        if not password:
            raise ValueError("password is required.")
        allowed_source, allowed_source_mode = get_allowed_source()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    report = run_precheck(
        lan_management_ip,
        device_name,
        username,
        password,
        allowed_source,
        allowed_source_mode,
    )
    json_path, txt_path = write_reports(report)
    print_summary(report, json_path, txt_path)
    return 0 if report["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
