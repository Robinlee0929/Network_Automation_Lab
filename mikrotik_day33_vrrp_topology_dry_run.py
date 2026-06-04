import argparse
import html
import ipaddress
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mikrotik_day2_auto_setup import color_text


DAY = "Day33"
TITLE = "VRRP Topology Design + Dry-run Command Preview"
SAFETY_MODE = "safe_dry_run"
REPORT_DIR = Path("reports") / "lab-summary"
REPORT_STEM = "day33_vrrp_topology_dry_run"
REPORT_JSON = REPORT_DIR / f"{REPORT_STEM}.json"
REPORT_HTML = REPORT_DIR / f"{REPORT_STEM}.html"
REPORT_TXT = REPORT_DIR / f"{REPORT_STEM}.txt"
DEFAULT_PROFILE = Path("topology_profiles") / "day33_vrrp_topology_dry_run.json"
REQUIRED_VRID = 88
REQUIRED_PARENT_INTERFACE = "bridge"
REQUIRED_VRRP_INTERFACE_NAME = "vrrp-lan"
REQUIRED_PRIMARY_DEVICE = "Hex-s-2025-lab01"
REQUIRED_BACKUP_DEVICE = "Hex-s-2025-lab02"
REQUIRED_PRIMARY_PRIORITY = 150
REQUIRED_BACKUP_PRIORITY = 100
REQUIRED_VIRTUAL_GATEWAY_CIDR = "192.168.88.1/32"
EXECUTION_STATUS = "DRY-RUN ONLY - NOT EXECUTED"

DESTRUCTIVE_KEYWORDS = [
    "remove",
    "disable",
    "enable",
    "reboot",
    "reset-configuration",
    "shutdown",
]

CONFIG_PREVIEW_ONLY_NOTE = (
    "DRY-RUN ONLY and NOT EXECUTED: commands are rendered for human review and are never sent to RouterOS by this runner."
)


def normalize_command(command: str) -> str:
    return " ".join(str(command).strip().split()).lower()


def blocked_preview_command_reasons(command: str) -> List[str]:
    normalized = normalize_command(command)
    reasons: List[str] = []
    if not normalized.startswith("/"):
        reasons.append("RouterOS preview command must start with '/'.")
    for keyword in DESTRUCTIVE_KEYWORDS:
        pattern = r"(^|[\s/])" + re.escape(keyword) + r"($|[\s=])"
        if re.search(pattern, normalized):
            reasons.append(f"Destructive operation is not allowed in Day33 preview: {keyword}")
    return reasons


def assert_preview_command_safe(command: str) -> None:
    reasons = blocked_preview_command_reasons(command)
    if reasons:
        raise ValueError(f"Unsafe Day33 preview command blocked: {command}; " + "; ".join(reasons))


def load_profile(profile_path: Path) -> Dict[str, Any]:
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Day33 topology profile was not found: {profile_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Day33 topology profile is not valid JSON: {profile_path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Day33 topology profile must contain a JSON object.")
    return profile


def required_text(profile: Dict[str, Any], key: str) -> str:
    value = str(profile.get(key, "")).strip()
    if not value:
        raise ValueError(f"Day33 topology profile must define {key}.")
    return value


def required_int(profile: Dict[str, Any], key: str) -> int:
    value = profile.get(key)
    if isinstance(value, bool):
        raise ValueError(f"Day33 topology profile must define numeric {key}.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Day33 topology profile must define numeric {key}.") from exc


def role_devices(profile: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    roles: Dict[str, Dict[str, Any]] = {}
    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        role = str(device.get("role", "")).strip().lower()
        if role in {"primary", "backup"}:
            roles[role] = device
    missing = [role for role in ("primary", "backup") if role not in roles]
    if missing:
        raise ValueError("Day33 topology profile must include primary and backup MikroTik devices.")
    return roles


def parse_lan_bridge_ip(device: Dict[str, Any]) -> ipaddress.IPv4Interface | ipaddress.IPv6Interface:
    name = str(device.get("name", "")).strip() or "unnamed device"
    value = str(device.get("lan_bridge_ip", "")).strip()
    if not value:
        raise ValueError(f"Day33 device {name} must define lan_bridge_ip.")
    try:
        return ipaddress.ip_interface(value)
    except ValueError as exc:
        raise ValueError(f"Day33 device {name} has invalid lan_bridge_ip: {value}") from exc


def validate_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    shared_lan_subnet = required_text(profile, "shared_lan_subnet")
    virtual_gateway_ip = required_text(profile, "virtual_gateway_ip")
    parent_interface = required_text(profile, "parent_interface")
    vrrp_interface_name = required_text(profile, "vrrp_interface_name")
    vrid = required_int(profile, "vrid")
    primary_priority = required_int(profile, "primary_priority")
    backup_priority = required_int(profile, "backup_priority")
    roles = role_devices(profile)

    try:
        subnet = ipaddress.ip_network(shared_lan_subnet, strict=False)
        vip_interface = ipaddress.ip_interface(virtual_gateway_ip)
    except ValueError as exc:
        raise ValueError(f"Day33 topology profile has invalid IP data: {exc}") from exc

    vip = vip_interface.ip
    if vip not in subnet:
        raise ValueError("Day33 virtual_gateway_ip must belong to shared_lan_subnet.")
    if str(vip_interface) != REQUIRED_VIRTUAL_GATEWAY_CIDR:
        raise ValueError(f"Day33 virtual_gateway_ip must be {REQUIRED_VIRTUAL_GATEWAY_CIDR}.")
    if parent_interface != REQUIRED_PARENT_INTERFACE:
        raise ValueError(f"Day33 parent_interface must be {REQUIRED_PARENT_INTERFACE}.")
    if vrrp_interface_name != REQUIRED_VRRP_INTERFACE_NAME:
        raise ValueError(f"Day33 vrrp_interface_name must be {REQUIRED_VRRP_INTERFACE_NAME}.")
    if vrid != REQUIRED_VRID:
        raise ValueError(f"Day33 vrid must be {REQUIRED_VRID}.")
    for key, value in {"primary_priority": primary_priority, "backup_priority": backup_priority}.items():
        if not 1 <= value <= 254:
            raise ValueError(f"Day33 {key} must be between 1 and 254.")
    if primary_priority != REQUIRED_PRIMARY_PRIORITY:
        raise ValueError(f"Day33 primary_priority must be {REQUIRED_PRIMARY_PRIORITY}.")
    if backup_priority != REQUIRED_BACKUP_PRIORITY:
        raise ValueError(f"Day33 backup_priority must be {REQUIRED_BACKUP_PRIORITY}.")
    if primary_priority <= backup_priority:
        raise ValueError("Day33 primary_priority must be higher than backup_priority.")

    primary = roles["primary"]
    backup = roles["backup"]
    if str(primary.get("name", "")).strip() != REQUIRED_PRIMARY_DEVICE:
        raise ValueError(f"Day33 primary device must be {REQUIRED_PRIMARY_DEVICE}.")
    if str(backup.get("name", "")).strip() != REQUIRED_BACKUP_DEVICE:
        raise ValueError(f"Day33 backup device must be {REQUIRED_BACKUP_DEVICE}.")

    primary_lan = parse_lan_bridge_ip(primary)
    backup_lan = parse_lan_bridge_ip(backup)
    for label, lan_ip in {"lab01": primary_lan, "lab02": backup_lan}.items():
        if lan_ip.ip == vip:
            raise ValueError(f"Day33 virtual_gateway_ip must not equal {label} physical LAN bridge IP.")
        if lan_ip.ip not in subnet:
            raise ValueError(f"Day33 {label} physical LAN bridge IP must belong to shared_lan_subnet.")

    return {
        "shared_lan_subnet": str(subnet),
        "virtual_gateway_ip": str(vip),
        "virtual_gateway_cidr": str(vip_interface),
        "parent_interface": parent_interface,
        "vrrp_interface_name": vrrp_interface_name,
        "vrid": vrid,
        "primary_priority": primary_priority,
        "backup_priority": backup_priority,
        "primary_lan_bridge_ip": str(primary_lan),
        "backup_lan_bridge_ip": str(backup_lan),
        "roles": roles,
    }


def build_device_commands(device: Dict[str, Any], topology: Dict[str, Any]) -> Dict[str, Any]:
    role = str(device.get("role", "")).lower()
    priority = topology["primary_priority"] if role == "primary" else topology["backup_priority"]
    prechecks = [
        "/system identity print",
        "/interface print terse",
        "/ip address print detail",
        "/interface vrrp print detail",
    ]
    config_preview = [
        (
            f"/interface vrrp add name={topology['vrrp_interface_name']} "
            f"interface={topology['parent_interface']} vrid={topology['vrid']} "
            f"priority={priority} preemption-mode=yes"
        ),
        f"/ip address add address={topology['virtual_gateway_cidr']} interface={topology['vrrp_interface_name']}",
    ]
    postchecks = [
        "/interface vrrp print detail",
        "/ip address print detail",
        f"/ping {topology['virtual_gateway_ip']} count=3",
    ]
    for command in prechecks + config_preview + postchecks:
        assert_preview_command_safe(command)
    return {
        "device_name": device.get("name", ""),
        "role": role,
        "priority": priority,
        "precheck_commands": prechecks,
        "configuration_preview_commands": config_preview,
        "postcheck_commands": postchecks,
        "execution_allowed": False,
        "execution_status": EXECUTION_STATUS,
        "notes": [CONFIG_PREVIEW_ONLY_NOTE],
    }


def build_report(profile: Dict[str, Any], profile_path: Path) -> Dict[str, Any]:
    topology = validate_profile(profile)
    devices = [
        build_device_commands(topology["roles"]["primary"], topology),
        build_device_commands(topology["roles"]["backup"], topology),
    ]
    return {
        "day": DAY,
        "title": TITLE,
        "safety_mode": SAFETY_MODE,
        "execution_status": EXECUTION_STATUS,
        "profile_path": profile_path.as_posix(),
        "overall_status": "PASS",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "topology": {
            key: value
            for key, value in topology.items()
            if key != "roles"
        },
        "planned_links": profile.get("planned_links", []),
        "safety_guardrails": {
            "no_ssh_connection": "PASS",
            "no_routeros_execution": "PASS",
            "configuration_preview_only": "PASS",
            "destructive_keywords_blocked": "PASS",
            "not_executed": "PASS",
        },
        "blocked_keywords": DESTRUCTIVE_KEYWORDS,
        "devices": devices,
    }


def html_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    css = value.lower() if value in {"PASS", "WARN", "FAIL"} else "warn"
    return f'<span class="badge {css}">{html.escape(value)}</span>'


def render_command_list(commands: List[str]) -> str:
    return "".join(f"<li><code>{html.escape(command)}</code></li>" for command in commands)


def build_html_report(report: Dict[str, Any]) -> str:
    topology = report.get("topology", {})
    device_sections = []
    for device in report.get("devices", []):
        device_sections.append(
            "<section class='panel'>"
            f"<h2>{html.escape(str(device.get('device_name', '')))} ({html.escape(str(device.get('role', '')))} priority {html.escape(str(device.get('priority', '')))})</h2>"
            "<h3>Read-only prechecks</h3>"
            f"<ol>{render_command_list(device.get('precheck_commands', []))}</ol>"
            "<h3>Configuration preview</h3>"
            f"<ol>{render_command_list(device.get('configuration_preview_commands', []))}</ol>"
            "<h3>Postcheck preview</h3>"
            f"<ol>{render_command_list(device.get('postcheck_commands', []))}</ol>"
            "</section>"
        )
    guardrails = "".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html_badge(value)}</td></tr>"
        for key, value in report.get("safety_guardrails", {}).items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ margin: 0; background: #f7f9fb; color: #182230; font-family: Arial, sans-serif; }}
    header {{ background: #26364a; color: white; padding: 28px 36px; }}
    main {{ padding: 24px 36px 44px; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .panel {{ background: white; border: 1px solid #d8e0ec; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .badge {{ display: inline-block; min-width: 58px; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 800; text-align: center; }}
    .pass {{ background: #e7f7ee; color: #147a3d; }}
    .warn {{ background: #fff4d8; color: #8a6100; }}
    .fail {{ background: #fdecec; color: #b42318; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(TITLE)}</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))} · Overall {html_badge(report.get("overall_status"))}</div>
    <div><strong>{html.escape(str(report.get("execution_status", EXECUTION_STATUS)))}</strong></div>
  </header>
  <main>
    <section class="panel">
      <h2>Topology</h2>
      <table><tbody>
        <tr><th>Shared LAN subnet</th><td>{html.escape(str(topology.get("shared_lan_subnet", "")))}</td></tr>
        <tr><th>Virtual gateway IP</th><td>{html.escape(str(topology.get("virtual_gateway_cidr", "")))}</td></tr>
        <tr><th>lab01 LAN bridge IP</th><td>{html.escape(str(topology.get("primary_lan_bridge_ip", "")))}</td></tr>
        <tr><th>lab02 LAN bridge IP</th><td>{html.escape(str(topology.get("backup_lan_bridge_ip", "")))}</td></tr>
        <tr><th>Parent interface</th><td>{html.escape(str(topology.get("parent_interface", "")))}</td></tr>
        <tr><th>VRRP interface</th><td>{html.escape(str(topology.get("vrrp_interface_name", "")))}</td></tr>
        <tr><th>VRID</th><td>{html.escape(str(topology.get("vrid", "")))}</td></tr>
      </tbody></table>
    </section>
    <section class="panel">
      <h2>Safety Guardrails</h2>
      <table><tbody>{guardrails}</tbody></table>
    </section>
    {''.join(device_sections)}
  </main>
</body>
</html>
"""


def build_text_report(report: Dict[str, Any]) -> str:
    lines = [
        "=" * 72,
        f"{DAY} - {TITLE}",
        "=" * 72,
        f"Generated: {report.get('generated_at', '')}",
        f"Safety mode: {SAFETY_MODE}",
        f"Execution status: {report.get('execution_status', EXECUTION_STATUS)}",
        f"Overall status: {report.get('overall_status', '')}",
        CONFIG_PREVIEW_ONLY_NOTE,
        "-" * 72,
    ]
    topology = report.get("topology", {})
    for key in (
        "shared_lan_subnet",
        "virtual_gateway_cidr",
        "primary_lan_bridge_ip",
        "backup_lan_bridge_ip",
        "parent_interface",
        "vrrp_interface_name",
        "vrid",
    ):
        lines.append(f"{key}: {topology.get(key, '')}")
    lines.append("-" * 72)
    for device in report.get("devices", []):
        lines.append(f"Device: {device.get('device_name', '')} ({device.get('role', '')}, priority {device.get('priority', '')})")
        for label, key in [
            ("Read-only prechecks", "precheck_commands"),
            ("Configuration preview", "configuration_preview_commands"),
            ("Postcheck preview", "postcheck_commands"),
        ]:
            lines.append(label + ":")
            lines.extend(f"  - {command}" for command in device.get(key, []))
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


def run(profile_path: Path = DEFAULT_PROFILE, report_dir: Path = REPORT_DIR) -> Tuple[Dict[str, Any], Tuple[Path, Path, Path]]:
    profile = load_profile(profile_path)
    report = build_report(profile, profile_path)
    paths = write_reports(report, report_dir)
    return report, paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{DAY} {TITLE}")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Day33 VRRP topology dry-run profile path.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR, help="Directory for Day33 JSON/HTML/TXT reports.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report, paths = run(args.profile, args.report_dir)
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
    print(f"Execution status: {report['execution_status']}")
    print(f"Devices previewed: {len(report['devices'])}")
    for device in report["devices"]:
        print(f"- {device['device_name']} ({device['role']} priority {device['priority']})")
        for command in device["configuration_preview_commands"]:
            print(f"  DRY-RUN: {command}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print(f"TXT report: {txt_path}")
    print("Safety guard: DRY-RUN ONLY, NOT EXECUTED, no SSH connection is opened, and no RouterOS command is executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
