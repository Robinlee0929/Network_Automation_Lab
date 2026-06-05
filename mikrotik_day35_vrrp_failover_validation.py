import argparse
import html
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import paramiko

import mikrotik_day32_vrrp_readonly_precheck as day32
from mikrotik_day2_auto_setup import (
    CONFIG_PATH,
    Day2Config,
    color_text,
    connect_ssh_with_auth_retry,
    parse_identity,
    run_raw_command,
)
from mikrotik_day4_multi_device_baseline import (
    apply_day4_connection_profile,
    apply_day4_precheck_host,
    ensure_device_password,
    load_day4_device_configs,
)


DAY = "Day35"
TITLE = "VRRP Failover Validation"
SAFETY_MODE = "controlled_failover_observation"
REPORT_DIR = Path("reports") / "lab-summary"
REPORT_STEM = "day35_vrrp_failover_validation"
REPORT_JSON = REPORT_DIR / f"{REPORT_STEM}.json"
REPORT_HTML = REPORT_DIR / f"{REPORT_STEM}.html"
REPORT_TXT = REPORT_DIR / f"{REPORT_STEM}.txt"
DEFAULT_PROFILE = Path("topology_profiles") / "day35_vrrp_failover_validation.json"

MANUAL_FAILOVER_PROMPT = "Disconnect lab01 LAN cable from the LAN switch, then press Enter."
MANUAL_RECOVERY_PROMPT = "Reconnect lab01 LAN cable, then press Enter."
NO_CONFIG_CHANGE_NOTE = (
    "Day35 observes manual VRRP failover only. It does not modify RouterOS configuration, "
    "interfaces, NAT/firewall, IP addresses, VRID, virtual IP, priority, reboot, or reset devices."
)

READONLY_COMMANDS: Dict[str, str] = {
    "identity": "/system identity print",
    "ip_addresses": "/ip address print",
    "vrrp": "/interface vrrp print detail",
    "interfaces": "/interface print",
    "routes": "/ip route print",
    "firewall_nat": "/ip firewall nat print",
    "firewall_filter": "/ip firewall filter print",
}

FORBIDDEN_OPERATIONS = [
    "add",
    "set",
    "remove",
    "disable",
    "enable",
    "reboot",
    "reset",
    "reset-configuration",
    "shutdown",
]

SECRET_VALUE_PATTERNS = [
    re.compile(
        r"(?i)\b(password|secret|private-key|private_key|preshared-key|preshared_key|passphrase|token)\s*=\s*(\"[^\"]*\"|\S+)"
    ),
    re.compile(
        r"(?i)\b(password|secret|private-key|private_key|preshared-key|preshared_key|passphrase|token)\s*:\s*(.*)"
    ),
]


CommandRunner = Callable[[Any, str], str]
PingRunner = Callable[[List[str]], subprocess.CompletedProcess[str]]


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
    if "print" not in normalized:
        reasons.append("Day35 only permits read-only RouterOS print commands.")
    return reasons


def assert_readonly_observation_command(command: str) -> None:
    reasons = blocked_command_reasons(command)
    if reasons:
        raise ValueError(f"Unsafe Day35 RouterOS command blocked: {command}; " + "; ".join(reasons))


def assert_all_observation_commands_readonly(commands: Dict[str, str]) -> None:
    for command in commands.values():
        assert_readonly_observation_command(command)


def redact_sensitive_data(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: redact_sensitive_data(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_sensitive_data(item) for item in value]
    if not isinstance(value, str):
        return value

    redacted = value
    for pattern in SECRET_VALUE_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}=<REDACTED>", redacted)
    return redacted


def load_profile(profile_path: Path) -> Dict[str, Any]:
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Day35 topology profile was not found: {profile_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Day35 topology profile is not valid JSON: {profile_path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Day35 topology profile must contain a JSON object.")
    return profile


def required_text(profile: Dict[str, Any], key: str) -> str:
    value = str(profile.get(key, "")).strip()
    if not value:
        raise ValueError(f"Day35 topology profile must define {key}.")
    return value


def required_int(profile: Dict[str, Any], key: str) -> int:
    value = profile.get(key)
    if isinstance(value, bool):
        raise ValueError(f"Day35 topology profile must define numeric {key}.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Day35 topology profile must define numeric {key}.") from exc


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
        raise ValueError("Day35 topology profile must include primary and backup MikroTik devices.")
    return roles


def _validate_ip(value: str, key: str) -> str:
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as exc:
        raise ValueError(f"Day35 topology profile has invalid {key}: {value}") from exc


def validate_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    shared_lan_subnet = required_text(profile, "shared_lan_subnet")
    lab01_lan_ip = _validate_ip(required_text(profile, "lab01_lan_ip"), "lab01_lan_ip")
    lab02_lan_ip = _validate_ip(required_text(profile, "lab02_lan_ip"), "lab02_lan_ip")
    vip = _validate_ip(required_text(profile, "vrrp_virtual_ip"), "vrrp_virtual_ip")
    automation_pc_lan_ip = _validate_ip(required_text(profile, "automation_pc_lan_ip"), "automation_pc_lan_ip")
    lan_server_ip = _validate_ip(required_text(profile, "lan_server_ip"), "lan_server_ip")
    default_route = _validate_ip(required_text(profile, "windows_default_route"), "windows_default_route")
    virtual_mac = required_text(profile, "virtual_mac").upper()
    vrid = required_int(profile, "vrid")
    lab01_priority = required_int(profile, "lab01_priority")
    lab02_priority = required_int(profile, "lab02_priority")
    roles = role_devices(profile)

    try:
        subnet = ipaddress.ip_network(shared_lan_subnet, strict=False)
    except ValueError as exc:
        raise ValueError(f"Day35 topology profile has invalid shared_lan_subnet: {shared_lan_subnet}") from exc

    for label, value in {
        "lab01_lan_ip": lab01_lan_ip,
        "lab02_lan_ip": lab02_lan_ip,
        "vrrp_virtual_ip": vip,
        "automation_pc_lan_ip": automation_pc_lan_ip,
        "lan_server_ip": lan_server_ip,
    }.items():
        if ipaddress.ip_address(value) not in subnet:
            raise ValueError(f"Day35 {label} must belong to shared_lan_subnet.")

    if vrid != 88:
        raise ValueError("Day35 vrid must be 88.")
    if lab01_priority != 150:
        raise ValueError("Day35 lab01_priority must be 150.")
    if lab02_priority != 100:
        raise ValueError("Day35 lab02_priority must be 100.")
    if lab01_priority <= lab02_priority:
        raise ValueError("Day35 lab01_priority must be higher than lab02_priority.")
    if virtual_mac != "00:00:5E:00:01:58":
        raise ValueError("Day35 virtual_mac must be 00:00:5E:00:01:58.")

    return {
        "shared_lan_subnet": str(subnet),
        "lab01_lan_ip": lab01_lan_ip,
        "lab02_lan_ip": lab02_lan_ip,
        "vrrp_virtual_ip": vip,
        "automation_pc_lan_ip": automation_pc_lan_ip,
        "lan_server_ip": lan_server_ip,
        "windows_default_route": default_route,
        "virtual_mac": virtual_mac,
        "vrid": vrid,
        "lab01_priority": lab01_priority,
        "lab02_priority": lab02_priority,
        "expected_baseline_states": {
            "primary": str(profile.get("lab01_state_before_failover", "MASTER")).upper(),
            "backup": str(profile.get("lab02_state_before_failover", "BACKUP")).upper(),
        },
        "roles": roles,
    }


def load_day35_device_configs(config_path: Path, profile_path: Path) -> List[Day2Config]:
    profile = load_profile(profile_path)
    roles = role_devices(profile)
    ordered_names = [str(roles[role].get("name", "")).strip() for role in ("primary", "backup")]
    configs = load_day4_device_configs(config_path)
    by_name = {config.device_name: config for config in configs}
    selected = [by_name[name] for name in ordered_names if name in by_name]
    if len(selected) != len([name for name in ordered_names if name]):
        missing = [name for name in ordered_names if name and name not in by_name]
        raise ValueError("No MikroTik Day35 device profiles were found for: " + ", ".join(missing))
    return selected


def build_ping_command(source_ip: str, target_ip: str, count: int = 3) -> List[str]:
    if os.name == "nt":
        return ["ping", "-S", source_ip, "-n", str(count), target_ip]
    return ["ping", "-I", source_ip, "-c", str(count), target_ip]


def run_pc_ping(
    source_ip: str,
    target_ip: str,
    label: str,
    ping_runner: Optional[PingRunner] = None,
) -> Dict[str, Any]:
    command = build_ping_command(source_ip, target_ip)
    runner = ping_runner or (lambda cmd: subprocess.run(cmd, text=True, capture_output=True, timeout=20))
    try:
        result = runner(command)
        output = "\n".join([str(getattr(result, "stdout", "")), str(getattr(result, "stderr", ""))]).strip()
        return {
            "label": label,
            "target": target_ip,
            "source": source_ip,
            "command": " ".join(command),
            "reachable": getattr(result, "returncode", 1) == 0,
            "status": "PASS" if getattr(result, "returncode", 1) == 0 else "FAIL",
            "output": redact_sensitive_data(output),
        }
    except Exception as error:
        return {
            "label": label,
            "target": target_ip,
            "source": source_ip,
            "command": " ".join(command),
            "reachable": False,
            "status": "FAIL",
            "output": redact_sensitive_data(f"{type(error).__name__}: {error}"),
        }


def run_ping_checks(topology: Dict[str, Any], ping_runner: Optional[PingRunner] = None) -> List[Dict[str, Any]]:
    source = topology["automation_pc_lan_ip"]
    targets = [
        ("lab01_lan_ip", topology["lab01_lan_ip"]),
        ("lab02_lan_ip", topology["lab02_lan_ip"]),
        ("vrrp_virtual_ip", topology["vrrp_virtual_ip"]),
        ("lan_server_ip", topology["lan_server_ip"]),
    ]
    return [run_pc_ping(source, target, label, ping_runner=ping_runner) for label, target in targets]


def collect_readonly_outputs(
    client: Any,
    command_runner: CommandRunner = run_raw_command,
) -> Tuple[Dict[str, str], List[str], List[str]]:
    outputs: Dict[str, str] = {}
    errors: List[str] = []
    commands_executed: List[str] = []
    assert_all_observation_commands_readonly(READONLY_COMMANDS)
    for key, command in READONLY_COMMANDS.items():
        assert_readonly_observation_command(command)
        commands_executed.append(command)
        try:
            outputs[key] = str(redact_sensitive_data(command_runner(client, command)))
        except Exception as error:
            outputs[key] = ""
            errors.append(f"{command}: {type(error).__name__}: {error}")
    return outputs, errors, commands_executed


def _state(value: Any) -> str:
    return str(value or "").strip().upper()


def _visible_virtual_mac(vrrp_summary: Dict[str, Any]) -> str:
    for entry in vrrp_summary.get("entries", []):
        for key in ("virtual-mac-address", "virtual-mac", "mac-address", "vr-mac-address"):
            value = str(entry.get(key, "")).strip()
            if value:
                return value.upper()
    return ""


def build_device_observation(
    config: Day2Config,
    role: str,
    reachable: bool,
    outputs: Optional[Dict[str, str]] = None,
    command_errors: Optional[List[str]] = None,
    commands_executed: Optional[List[str]] = None,
    connection_error: str = "",
) -> Dict[str, Any]:
    outputs = outputs or {}
    command_errors = command_errors or []
    commands_executed = commands_executed or []
    vrrp_summary = day32.parse_vrrp_summary(outputs.get("vrrp", ""), outputs.get("ip_addresses", ""))
    notes: List[str] = []
    if connection_error:
        notes.append(connection_error)
    notes.extend(command_errors)
    return {
        "device_name": config.device_name,
        "role": role,
        "host": config.host,
        "ssh_port": config.port,
        "reachable": reachable,
        "identity": parse_identity(outputs.get("identity", "")) or config.device_name,
        "vrrp_state": _state(vrrp_summary.get("state")),
        "vrrp_priority": str(vrrp_summary.get("priority", "")),
        "vrrp_vrid": str(vrrp_summary.get("vrid", "")),
        "vrrp_virtual_ip": str(vrrp_summary.get("virtual_ip", "")),
        "reported_virtual_mac": _visible_virtual_mac(vrrp_summary),
        "readonly_commands_executed": commands_executed,
        "blocked_commands_detected": [],
        "notes": notes,
        "raw_outputs": redact_sensitive_data(outputs),
    }


def collect_device_observation(
    config: Day2Config,
    role: str,
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
        return build_device_observation(config, role, True, outputs, errors, commands)
    except (paramiko.AuthenticationException, socket.timeout, TimeoutError, OSError, ValueError) as error:
        return build_device_observation(
            config,
            role,
            False,
            connection_error=f"{type(error).__name__}: {error}",
        )
    finally:
        if client:
            client.close()


def collect_router_observations(
    configs: List[Day2Config],
    profile: Dict[str, Any],
    command_runner: CommandRunner = run_raw_command,
    connect_func: Callable[[Day2Config], Any] = connect_ssh_with_auth_retry,
) -> List[Dict[str, Any]]:
    roles = role_devices(profile)
    role_by_name = {str(device.get("name", "")).strip(): role for role, device in roles.items()}
    return [
        collect_device_observation(
            config,
            role_by_name.get(config.device_name, "unknown"),
            command_runner=command_runner,
            connect_func=connect_func,
        )
        for config in configs
    ]


def build_phase(
    phase_id: str,
    title: str,
    topology: Dict[str, Any],
    devices: List[Dict[str, Any]],
    ping_checks: List[Dict[str, Any]],
    operator_action: str = "",
) -> Dict[str, Any]:
    return {
        "id": phase_id,
        "title": title,
        "operator_action": operator_action,
        "ping_checks": ping_checks,
        "devices": devices,
        "checks": evaluate_phase_checks(phase_id, topology, devices, ping_checks),
    }


def _device_by_role(devices: List[Dict[str, Any]], role: str) -> Dict[str, Any]:
    for device in devices:
        if device.get("role") == role:
            return device
    return {}


def _ping_status(pings: List[Dict[str, Any]], label: str) -> str:
    for ping in pings:
        if ping.get("label") == label:
            return "PASS" if ping.get("reachable") else "FAIL"
    return "FAIL"


def evaluate_phase_checks(
    phase_id: str,
    topology: Dict[str, Any],
    devices: List[Dict[str, Any]],
    ping_checks: List[Dict[str, Any]],
) -> Dict[str, str]:
    primary = _device_by_role(devices, "primary")
    backup = _device_by_role(devices, "backup")
    checks: Dict[str, str] = {
        "vip_reachable": _ping_status(ping_checks, "vrrp_virtual_ip"),
        "lan_server_reachable": _ping_status(ping_checks, "lan_server_ip"),
        "routeros_config_modification_attempted": "FAIL"
        if any(device.get("blocked_commands_detected") for device in devices)
        else "PASS",
    }

    if phase_id == "baseline":
        expected = topology["expected_baseline_states"]
        checks["lab01_master_before_failover"] = "PASS" if primary.get("vrrp_state") == expected["primary"] else "FAIL"
        checks["lab02_backup_before_failover"] = "PASS" if backup.get("vrrp_state") == expected["backup"] else "FAIL"
        reported_mac = primary.get("reported_virtual_mac") or backup.get("reported_virtual_mac")
        if reported_mac:
            checks["expected_virtual_mac_if_visible"] = "PASS" if reported_mac == topology["virtual_mac"] else "FAIL"
        else:
            checks["expected_virtual_mac_if_visible"] = "PASS_WITH_NOTES"
    elif phase_id == "failover":
        checks["lab02_master_after_failover"] = "PASS" if backup.get("vrrp_state") == "MASTER" else "FAIL"
    elif phase_id == "recovery":
        checks["lab01_preemption_back_to_master_observed"] = (
            "PASS" if primary.get("vrrp_state") == "MASTER" else "PASS_WITH_NOTES"
        )
    return checks


def phase_status(phase: Dict[str, Any]) -> str:
    values = set(phase.get("checks", {}).values())
    if "FAIL" in values:
        return "FAIL"
    if "PASS_WITH_NOTES" in values:
        return "PASS_WITH_NOTES"
    return "PASS"


def overall_status(phases: List[Dict[str, Any]]) -> str:
    baseline = next((phase for phase in phases if phase.get("id") == "baseline"), {})
    failover = next((phase for phase in phases if phase.get("id") == "failover"), {})
    recovery = next((phase for phase in phases if phase.get("id") == "recovery"), {})

    if phase_status(baseline) == "FAIL":
        return "FAIL"
    if phase_status(failover) == "FAIL":
        return "FAIL"
    if phase_status(recovery) == "FAIL":
        return "FAIL"
    if any(phase_status(phase) == "PASS_WITH_NOTES" for phase in phases):
        return "PASS_WITH_NOTES"
    return "PASS"


def build_report(profile: Dict[str, Any], profile_path: Path, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
    topology = validate_profile(profile)
    return redact_sensitive_data(
        {
            "day": DAY,
            "title": TITLE,
            "safety_mode": SAFETY_MODE,
            "profile_path": profile_path.as_posix(),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "overall_status": overall_status(phases),
            "topology": {key: value for key, value in topology.items() if key != "roles"},
            "allowed_operations": ["source-specific Windows ping", "read-only RouterOS print commands", "report generation"],
            "forbidden_operations": FORBIDDEN_OPERATIONS,
            "safety_guardrails": {
                "routeros_configuration_modification": "BLOCKED",
                "interface_enable_disable": "BLOCKED",
                "firewall_nat_modification": "BLOCKED",
                "ip_address_modification": "BLOCKED",
                "vrrp_priority_vrid_virtual_ip_change": "BLOCKED",
                "reboot_or_reset": "BLOCKED",
                "manual_external_failover_trigger_only": "PASS",
            },
            "manual_prompts": [MANUAL_FAILOVER_PROMPT, MANUAL_RECOVERY_PROMPT],
            "readonly_commands": list(READONLY_COMMANDS.values()),
            "phases": phases,
            "notes": [NO_CONFIG_CHANGE_NOTE] + list(profile.get("notes", [])),
        }
    )


def html_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    css = value.lower() if value in {"PASS", "PASS_WITH_NOTES", "FAIL", "BLOCKED"} else "warn"
    return f'<span class="badge {css}">{html.escape(value)}</span>'


def _render_checks(checks: Dict[str, str]) -> str:
    return "".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html_badge(value)}</td></tr>"
        for key, value in checks.items()
    )


def _render_pings(pings: List[Dict[str, Any]]) -> str:
    rows = []
    for ping in pings:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(ping.get('label', '')))}</td>"
            f"<td><code>{html.escape(str(ping.get('target', '')))}</code></td>"
            f"<td><code>{html.escape(str(ping.get('source', '')))}</code></td>"
            f"<td>{html_badge(ping.get('status'))}</td>"
            f"<td><code>{html.escape(str(ping.get('command', '')))}</code></td>"
            "</tr>"
        )
    return "".join(rows)


def _render_devices(devices: List[Dict[str, Any]]) -> str:
    rows = []
    for device in devices:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(device.get('device_name', '')))}</td>"
            f"<td>{html.escape(str(device.get('role', '')))}</td>"
            f"<td>{'Yes' if device.get('reachable') else 'No'}</td>"
            f"<td>{html.escape(str(device.get('vrrp_state', '')))}</td>"
            f"<td>{html.escape(str(device.get('vrrp_priority', '')))}</td>"
            f"<td>{html.escape(str(device.get('vrrp_vrid', '')))}</td>"
            f"<td>{html.escape(str(device.get('reported_virtual_mac', '')))}</td>"
            f"<td>{html.escape('; '.join(str(note) for note in device.get('notes', [])))}</td>"
            "</tr>"
        )
    return "".join(rows)


def build_html_report(report: Dict[str, Any]) -> str:
    phase_sections = []
    for phase in report.get("phases", []):
        phase_sections.append(
            "<section class='panel'>"
            f"<h2>{html.escape(str(phase.get('title', '')))} {html_badge(phase_status(phase))}</h2>"
            f"<p>{html.escape(str(phase.get('operator_action', '')))}</p>"
            "<h3>Checks</h3>"
            f"<table><tbody>{_render_checks(phase.get('checks', {}))}</tbody></table>"
            "<h3>Source-specific LAN pings</h3>"
            "<table><thead><tr><th>Label</th><th>Target</th><th>Source</th><th>Status</th><th>Command</th></tr></thead>"
            f"<tbody>{_render_pings(phase.get('ping_checks', []))}</tbody></table>"
            "<h3>RouterOS observations</h3>"
            "<table><thead><tr><th>Device</th><th>Role</th><th>SSH reachable</th><th>VRRP state</th><th>Priority</th><th>VRID</th><th>Virtual MAC</th><th>Notes</th></tr></thead>"
            f"<tbody>{_render_devices(phase.get('devices', []))}</tbody></table>"
            "</section>"
        )
    guardrails = "".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html_badge(value)}</td></tr>"
        for key, value in report.get("safety_guardrails", {}).items()
    )
    commands = "".join(f"<li><code>{html.escape(command)}</code></li>" for command in READONLY_COMMANDS.values())
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ margin: 0; background: #f6f8fb; color: #182230; font-family: Arial, sans-serif; }}
    header {{ background: #26364a; color: white; padding: 28px 36px; }}
    main {{ padding: 24px 36px 44px; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin-bottom: 16px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .panel {{ background: white; border: 1px solid #d8e0ec; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .badge {{ display: inline-block; min-width: 72px; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 800; text-align: center; }}
    .pass {{ background: #e7f7ee; color: #147a3d; }}
    .pass_with_notes, .warn {{ background: #fff4d8; color: #8a6100; }}
    .blocked, .fail {{ background: #fdecec; color: #b42318; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(TITLE)}</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))} · Overall {html_badge(report.get("overall_status"))}</div>
    <p>{html.escape(NO_CONFIG_CHANGE_NOTE)}</p>
  </header>
  <main>
    <section class="panel">
      <h2>Safety Guardrails</h2>
      <table><tbody>{guardrails}</tbody></table>
      <h3>Allowed RouterOS evidence commands</h3>
      <ul>{commands}</ul>
    </section>
    {''.join(phase_sections)}
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
        f"Overall status: {report.get('overall_status', '')}",
        NO_CONFIG_CHANGE_NOTE,
        "-" * 72,
    ]
    for phase in report.get("phases", []):
        lines.append(f"{phase.get('id', '')}: {phase.get('title', '')} [{phase_status(phase)}]")
        if phase.get("operator_action"):
            lines.append(f"Operator action: {phase.get('operator_action')}")
        lines.append("Checks:")
        lines.extend(f"  - {key}: {value}" for key, value in phase.get("checks", {}).items())
        lines.append("Pings:")
        lines.extend(
            f"  - {ping.get('command', '')}: {ping.get('status', '')}"
            for ping in phase.get("ping_checks", [])
        )
        lines.append("RouterOS observations:")
        for device in phase.get("devices", []):
            lines.append(
                f"  - {device.get('device_name', '')} ({device.get('role', '')}): "
                f"reachable={device.get('reachable')} state={device.get('vrrp_state', '')} "
                f"priority={device.get('vrrp_priority', '')} vrid={device.get('vrrp_vrid', '')}"
            )
        lines.append("-" * 72)
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any], report_dir: Path = REPORT_DIR) -> Tuple[Path, Path, Path]:
    safe_report = redact_sensitive_data(report)
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / f"{REPORT_STEM}.json"
    html_path = report_dir / f"{REPORT_STEM}.html"
    txt_path = report_dir / f"{REPORT_STEM}.txt"
    json_path.write_text(json.dumps(safe_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(build_html_report(safe_report), encoding="utf-8")
    txt_path.write_text(build_text_report(safe_report), encoding="utf-8")
    return json_path, html_path, txt_path


def run(
    config_path: Path = CONFIG_PATH,
    profile_path: Path = DEFAULT_PROFILE,
    report_dir: Path = REPORT_DIR,
    input_func: Callable[[str], str] = input,
    ping_runner: Optional[PingRunner] = None,
) -> Tuple[Dict[str, Any], Tuple[Path, Path, Path]]:
    assert_all_observation_commands_readonly(READONLY_COMMANDS)
    profile = load_profile(profile_path)
    topology = validate_profile(profile)
    configs = load_day35_device_configs(config_path, profile_path)

    baseline = build_phase(
        "baseline",
        "Baseline before manual failure",
        topology,
        collect_router_observations(configs, profile),
        run_ping_checks(topology, ping_runner=ping_runner),
    )

    input_func(MANUAL_FAILOVER_PROMPT)
    failover = build_phase(
        "failover",
        "Failover observation after lab01 LAN disconnect",
        topology,
        collect_router_observations(configs, profile),
        run_ping_checks(topology, ping_runner=ping_runner),
        operator_action=MANUAL_FAILOVER_PROMPT,
    )

    input_func(MANUAL_RECOVERY_PROMPT)
    recovery = build_phase(
        "recovery",
        "Recovery observation after lab01 LAN reconnect",
        topology,
        collect_router_observations(configs, profile),
        run_ping_checks(topology, ping_runner=ping_runner),
        operator_action=MANUAL_RECOVERY_PROMPT,
    )

    phases = [baseline, failover, recovery]
    report = build_report(profile, profile_path, phases)
    paths = write_reports(report, report_dir)
    return report, paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{DAY} {TITLE}")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Local MikroTik inventory/config path.")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Day35 topology profile path.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR, help="Directory for Day35 JSON/HTML/TXT reports.")
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
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print(f"TXT report: {txt_path}")
    print("Safety guard: controlled observation only; RouterOS modification commands are blocked before execution.")
    return 2 if report["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
