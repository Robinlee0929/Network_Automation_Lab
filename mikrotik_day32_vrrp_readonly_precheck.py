import argparse
import html
import json
import re
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import paramiko

from mikrotik_day2_auto_setup import (
    CONFIG_PATH,
    Day2Config,
    color_text,
    connect_ssh_with_auth_retry,
    parse_identity,
    parse_system_resource,
    run_raw_command,
)
from mikrotik_day4_multi_device_baseline import (
    apply_day4_connection_profile,
    apply_day4_precheck_host,
    ensure_device_password,
    load_day4_device_configs,
)


DAY = "Day32"
TITLE = "VRRP Read-only Precheck Runner"
SAFETY_MODE = "read-only"
REPORT_DIR = Path("reports") / "lab-summary"
REPORT_STEM = "day32_vrrp_readonly_precheck"
REPORT_JSON = REPORT_DIR / f"{REPORT_STEM}.json"
REPORT_HTML = REPORT_DIR / f"{REPORT_STEM}.html"
REPORT_TXT = REPORT_DIR / f"{REPORT_STEM}.txt"
DEFAULT_PROFILE = Path("topology_profiles") / "day32_vrrp_readonly_precheck.json"

ALLOWED_OPERATIONS = ["print", "export terse", "report generation"]
FORBIDDEN_OPERATIONS = [
    "add",
    "set",
    "remove",
    "disable",
    "enable",
    "reboot",
    "reset-configuration",
]

READONLY_COMMANDS: Dict[str, str] = {
    "identity": "/system identity print",
    "resource": "/system resource print",
    "vrrp": "/interface vrrp print detail",
    "interfaces": "/interface print terse",
    "ip_addresses": "/ip address print detail",
    "routes": "/ip route print detail",
    "bridges": "/interface bridge print detail",
    "bridge_ports": "/interface bridge port print detail",
    "export": "/export terse",
}

VRRP_NOT_CONFIGURED_NOTE = "VRRP not configured or command returned no entries"


def normalize_command(command: str) -> str:
    return " ".join(str(command).strip().split()).lower()


def blocked_command_reasons(command: str) -> List[str]:
    normalized = normalize_command(command)
    reasons: List[str] = []
    if not normalized.startswith("/"):
        reasons.append("RouterOS command must start with '/'.")

    for keyword in FORBIDDEN_OPERATIONS:
        pattern = r"(^|[\s/])" + re.escape(keyword) + r"($|[\s=])"
        if re.search(pattern, normalized):
            reasons.append(f"Forbidden operation detected: {keyword}")

    if "print" not in normalized and normalized != "/export terse":
        reasons.append("Command is not an allowed read-only print/export terse operation.")

    return reasons


def assert_readonly_command(command: str) -> None:
    reasons = blocked_command_reasons(command)
    if reasons:
        raise ValueError(f"Unsafe MikroTik command blocked: {command}; " + "; ".join(reasons))


def assert_all_commands_readonly(commands: Dict[str, str]) -> None:
    for command in commands.values():
        assert_readonly_command(command)


def parse_key_value_tokens(output: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for key, value in re.findall(r"([\w-]+)=(\"[^\"]*\"|\S+)", output):
        values[key] = value.strip('"')
    for key, value in re.findall(r"([\w-]+)\s*:\s*(.*?)(?=\s+[\w-]+\s*:|$)", output):
        values[key] = value.strip()
    return values


def parse_print_entries(output: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    current: List[str] = []
    for raw_line in str(output).splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("Flags:", "Columns:", "#", ";;;")):
            continue
        if re.match(r"^\d+\s", line) and current:
            entries.append(parse_key_value_tokens(" ".join(current)))
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append(parse_key_value_tokens(" ".join(current)))
    return [entry for entry in entries if entry]


def parse_vrrp_summary(vrrp_output: str, ip_address_output: str) -> Dict[str, Any]:
    entries = parse_print_entries(vrrp_output)
    if not entries:
        return {
            "configured": False,
            "interfaces": [],
            "state": "",
            "priority": "",
            "vrid": "",
            "virtual_ip": "",
            "entries": [],
        }

    first = entries[0]
    interface_name = first.get("interface") or first.get("name", "")
    virtual_ips = []
    if interface_name:
        for address in parse_print_entries(ip_address_output):
            if address.get("interface") == interface_name and address.get("address"):
                virtual_ips.append(address["address"])

    explicit_vip = first.get("virtual-address") or first.get("address", "")
    return {
        "configured": True,
        "interfaces": sorted({entry.get("interface") or entry.get("name", "") for entry in entries if entry}),
        "interface": interface_name,
        "state": first.get("state", ""),
        "priority": first.get("priority", ""),
        "vrid": first.get("vrid", ""),
        "virtual_ip": ", ".join(virtual_ips) or explicit_vip,
        "entries": entries,
    }


def summarize_bridge_info(bridge_output: str, bridge_port_output: str) -> Dict[str, Any]:
    bridges = parse_print_entries(bridge_output)
    ports = parse_print_entries(bridge_port_output)
    return {
        "bridges": [
            {
                "name": item.get("name", ""),
                "disabled": item.get("disabled", ""),
                "protocol-mode": item.get("protocol-mode", ""),
            }
            for item in bridges
        ],
        "ports": [
            {
                "interface": item.get("interface", ""),
                "bridge": item.get("bridge", ""),
                "disabled": item.get("disabled", ""),
                "hw": item.get("hw", ""),
            }
            for item in ports
        ],
    }


def summarize_routes(route_output: str) -> Dict[str, Any]:
    entries = parse_print_entries(route_output)
    active = [entry for entry in entries if entry.get("active") == "yes" or "A" in entry.get("flags", "")]
    default_routes = [
        entry
        for entry in entries
        if entry.get("dst-address", "").startswith("0.0.0.0/0") or entry.get("dst-address") == "0.0.0.0"
    ]
    return {
        "route_count": len(entries),
        "active_route_count": len(active),
        "default_routes": default_routes[:5],
    }


def load_profile_device_names(profile_path: Path) -> List[str]:
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    if not isinstance(profile, dict):
        return []
    names = []
    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        role = str(device.get("role", "")).lower()
        name = str(device.get("name", "")).strip()
        if name and "switch" not in role and "cisco" not in name.lower():
            names.append(name)
    return names


def load_day32_device_configs(config_path: Path, profile_path: Path) -> List[Day2Config]:
    configs = load_day4_device_configs(config_path)
    selected_names = set(load_profile_device_names(profile_path))
    if selected_names:
        configs = [config for config in configs if config.device_name in selected_names]
    return configs


CommandRunner = Callable[[Any, str], str]


def collect_readonly_outputs(client: Any, command_runner: CommandRunner = run_raw_command) -> Tuple[Dict[str, str], List[str], List[str]]:
    outputs: Dict[str, str] = {}
    errors: List[str] = []
    commands_executed: List[str] = []
    assert_all_commands_readonly(READONLY_COMMANDS)
    for key, command in READONLY_COMMANDS.items():
        assert_readonly_command(command)
        commands_executed.append(command)
        try:
            outputs[key] = command_runner(client, command)
        except Exception as error:
            outputs[key] = ""
            errors.append(f"{command}: {type(error).__name__}: {error}")
    return outputs, errors, commands_executed


def build_device_entry(
    config: Day2Config,
    reachable: bool,
    outputs: Optional[Dict[str, str]] = None,
    command_errors: Optional[List[str]] = None,
    commands_executed: Optional[List[str]] = None,
    connection_error: str = "",
) -> Dict[str, Any]:
    outputs = outputs or {}
    command_errors = command_errors or []
    commands_executed = commands_executed or []
    notes: List[str] = []

    if connection_error:
        notes.append(connection_error)
    if command_errors:
        notes.extend(command_errors)

    identity = parse_identity(outputs.get("identity", "")) or config.device_name
    resource = parse_system_resource(outputs.get("resource", ""))
    vrrp_summary = parse_vrrp_summary(outputs.get("vrrp", ""), outputs.get("ip_addresses", ""))
    if not vrrp_summary["configured"]:
        notes.append(VRRP_NOT_CONFIGURED_NOTE)

    status = "FAIL"
    if reachable:
        status = "PASS" if vrrp_summary["configured"] and not command_errors else "WARN"

    return {
        "device_name": config.device_name,
        "host": config.host,
        "ssh_port": config.port,
        "reachable": reachable,
        "status": status,
        "identity": identity,
        "routeros_version": resource.get("version", ""),
        "vrrp_configured": bool(vrrp_summary["configured"]),
        "vrrp_summary": vrrp_summary,
        "bridge_lan_summary": summarize_bridge_info(outputs.get("bridges", ""), outputs.get("bridge_ports", "")),
        "route_summary": summarize_routes(outputs.get("routes", "")),
        "readonly_commands_executed": commands_executed,
        "blocked_commands_detected": [],
        "notes": notes,
        "raw_outputs": outputs,
    }


def overall_status(devices: List[Dict[str, Any]]) -> str:
    if not devices or not any(device.get("reachable") for device in devices):
        return "FAIL"
    if any(device.get("status") == "FAIL" for device in devices):
        return "FAIL"
    if any(device.get("status") == "WARN" for device in devices):
        return "WARN"
    return "PASS"


def build_report(devices: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "day": DAY,
        "title": TITLE,
        "safety_mode": SAFETY_MODE,
        "allowed_operations": ALLOWED_OPERATIONS,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "overall_status": overall_status(devices),
        "devices": devices,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def html_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    css = value.lower() if value in {"PASS", "WARN", "FAIL"} else "warn"
    return f'<span class="badge {css}">{html.escape(value)}</span>'


def build_html_report(report: Dict[str, Any]) -> str:
    device_rows = []
    for device in report.get("devices", []):
        summary = device.get("vrrp_summary", {})
        device_rows.append(
            "<tr>"
            f"<td>{html.escape(str(device.get('device_name', '')))}</td>"
            f"<td><code>{html.escape(str(device.get('host', '')))}</code></td>"
            f"<td>{'Yes' if device.get('reachable') else 'No'}</td>"
            f"<td>{html_badge(device.get('status'))}</td>"
            f"<td>{'Yes' if device.get('vrrp_configured') else 'No'}</td>"
            f"<td>{html.escape(str(summary.get('interface', '') or ', '.join(summary.get('interfaces', []))))}</td>"
            f"<td>{html.escape(str(summary.get('state', '')))}</td>"
            f"<td>{html.escape(str(summary.get('priority', '')))}</td>"
            f"<td>{html.escape(str(summary.get('virtual_ip', '')))}</td>"
            f"<td>{html.escape('; '.join(str(note) for note in device.get('notes', [])))}</td>"
            "</tr>"
        )
    commands = "".join(f"<li><code>{html.escape(command)}</code></li>" for command in READONLY_COMMANDS.values())
    forbidden = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in FORBIDDEN_OPERATIONS)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ margin: 0; background: #f6f8fb; color: #182230; font-family: Arial, sans-serif; }}
    header {{ background: #243447; color: white; padding: 28px 36px; }}
    main {{ padding: 26px 36px 44px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d8e0ec; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #d8e0ec; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
    .badge {{ display: inline-block; min-width: 58px; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 800; text-align: center; }}
    .pass {{ background: #e7f7ee; color: #147a3d; }}
    .warn {{ background: #fff4d8; color: #8a6100; }}
    .fail {{ background: #fdecec; color: #b42318; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 18px 0 24px; }}
    .panel {{ background: white; border: 1px solid #d8e0ec; border-radius: 8px; padding: 14px 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(TITLE)}</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))} · Overall {html_badge(report.get("overall_status"))}</div>
  </header>
  <main>
    <section class="grid">
      <div class="panel"><strong>Safety mode</strong><br>{html.escape(SAFETY_MODE)}</div>
      <div class="panel"><strong>Allowed read-only commands</strong><ul>{commands}</ul></div>
      <div class="panel"><strong>Blocked keywords</strong><ul>{forbidden}</ul></div>
    </section>
    <table>
      <thead><tr><th>Device</th><th>Host</th><th>Reachable</th><th>Status</th><th>VRRP</th><th>Interface</th><th>State</th><th>Priority</th><th>Virtual IP</th><th>Notes</th></tr></thead>
      <tbody>{''.join(device_rows) or '<tr><td colspan="10">No devices were checked.</td></tr>'}</tbody>
    </table>
  </main>
</body>
</html>
"""


def build_text_report(report: Dict[str, Any]) -> str:
    divider = "=" * 72
    lines = [
        divider,
        f"{DAY} - {TITLE}",
        divider,
        f"Generated: {report.get('generated_at', '')}",
        f"Safety mode: {SAFETY_MODE}",
        f"Overall status: {report.get('overall_status', '')}",
        f"Allowed operations: {', '.join(ALLOWED_OPERATIONS)}",
        f"Forbidden operations: {', '.join(FORBIDDEN_OPERATIONS)}",
        "-" * 72,
    ]
    for device in report.get("devices", []):
        summary = device.get("vrrp_summary", {})
        lines.extend(
            [
                f"Device: {device.get('device_name', '')}",
                f"Host: {device.get('host', '')}:{device.get('ssh_port', '')}",
                f"Reachable: {device.get('reachable')}",
                f"Status: {device.get('status', '')}",
                f"Identity: {device.get('identity', '')}",
                f"RouterOS: {device.get('routeros_version', '')}",
                f"VRRP configured: {device.get('vrrp_configured')}",
                f"VRRP interface: {summary.get('interface', '') or ', '.join(summary.get('interfaces', []))}",
                f"VRRP state: {summary.get('state', '')}",
                f"VRRP priority: {summary.get('priority', '')}",
                f"VRRP virtual IP: {summary.get('virtual_ip', '')}",
                "Commands executed:",
            ]
        )
        lines.extend(f"  - {command}" for command in device.get("readonly_commands_executed", []))
        lines.append("Notes:")
        notes = device.get("notes", [])
        lines.extend(f"  - {note}" for note in notes) if notes else lines.append("  - None")
        lines.append("-" * 72)
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any], report_dir: Path = REPORT_DIR) -> Tuple[Path, Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{REPORT_STEM}.json"
    html_path = report_dir / f"{REPORT_STEM}.html"
    txt_path = report_dir / f"{REPORT_STEM}.txt"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(build_html_report(report), encoding="utf-8")
    txt_path.write_text(build_text_report(report), encoding="utf-8")
    return json_path, html_path, txt_path


def run_device_precheck(
    config: Day2Config,
    command_runner: CommandRunner = run_raw_command,
    connect_func: Callable[[Day2Config], Any] = connect_ssh_with_auth_retry,
) -> Dict[str, Any]:
    client: Any = None
    try:
        apply_day4_connection_profile(config, (config.device_profiles or {}).get(config.device_name, {}))
        apply_day4_precheck_host(config)
        ensure_device_password(config)
        client = connect_func(config)
        outputs, errors, commands = collect_readonly_outputs(client, command_runner=command_runner)
        return build_device_entry(config, True, outputs, errors, commands)
    except (paramiko.AuthenticationException, socket.timeout, TimeoutError, OSError, ValueError) as error:
        return build_device_entry(
            config,
            False,
            connection_error=f"{type(error).__name__}: {error}",
        )
    finally:
        if client:
            client.close()


def run(
    config_path: Path = CONFIG_PATH,
    profile_path: Path = DEFAULT_PROFILE,
    report_dir: Path = REPORT_DIR,
) -> Tuple[Dict[str, Any], Tuple[Path, Path, Path]]:
    assert_all_commands_readonly(READONLY_COMMANDS)
    configs = load_day32_device_configs(config_path, profile_path)
    if not configs:
        raise ValueError("No MikroTik Day32 device profiles were found.")
    devices = [run_device_precheck(config) for config in configs]
    report = build_report(devices)
    paths = write_reports(report, report_dir)
    return report, paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{DAY} {TITLE}")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Local MikroTik inventory/config path.")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Day32 topology profile path.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR, help="Directory for Day32 JSON/HTML/TXT reports.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report, paths = run(args.config, args.profile, args.report_dir)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    json_path, html_path, txt_path = paths
    print()
    print(color_text("=" * 72, "\033[36m"))
    print(f"{DAY} - {TITLE}")
    print(color_text("=" * 72, "\033[36m"))
    print(f"Overall status: {report['overall_status']}")
    print(f"Devices checked: {len(report['devices'])}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print(f"TXT report: {txt_path}")
    print("Safety guard: blocks add/set/remove/disable/enable/reboot/reset-configuration before command execution.")
    return 2 if report["overall_status"] == "FAIL" and not any(d.get("reachable") for d in report["devices"]) else 0


if __name__ == "__main__":
    sys.exit(main())
