import argparse
import getpass
import html
import json
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko

from adapters.cisco_ios import CiscoIOS, CommandTimeoutError
from mikrotik_day2_auto_setup import (
    COLOR_BOLD,
    COLOR_CYAN,
    COLOR_DIM,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    color_text,
)
from parsers import cisco_parser


CISCO_CONFIG_PATH = Path("config.cisco.json")
CISCO_EXAMPLE_CONFIG_PATH = Path("config.cisco.example.json")
REPORT_DIR = Path("reports") / "cisco-switch"
REPORT_JSON = REPORT_DIR / "switch_topology_report.json"
REPORT_HTML = REPORT_DIR / "switch_topology_report.html"

DAY5_COMMANDS = {
    "show_version": "show version",
    "show_ip_interface_brief": "show ip interface brief",
    "show_interfaces_status": "show interfaces status",
    "show_vlan_brief": "show vlan brief",
    "show_mac_address_table": "show mac address-table",
    "show_spanning_tree_summary": "show spanning-tree summary",
}

REQUIRED_CHECKS = {
    "SSH login",
    "show version readable",
    "Switch model",
    "IOS version parsed",
    "show ip interface brief readable",
    "Vlan1 management IP",
    "show interfaces status readable",
    "Expected ports connected",
    "VLAN 1 active",
    "MAC address table readable",
    "Dynamic MAC learned",
    "spanning-tree summary readable",
    "VLAN0001 blocking ports",
    "Report generation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cisco Switch Topology Validation."
    )
    parser.add_argument("--config", default="", help="Path to Cisco config JSON.")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def is_cisco_config(config: Dict[str, Any]) -> bool:
    device = config.get("device", {})
    if not isinstance(device, dict):
        device = {}
    vendor = str(device.get("vendor", config.get("vendor", ""))).lower()
    platform = str(device.get("platform", config.get("platform", ""))).lower()
    device_type = str(config.get("device_type", "")).lower()
    return vendor == "cisco" or platform == "ios" or device_type == "cisco_ios"


def resolve_config_path(explicit_path: str = "") -> Path:
    if explicit_path:
        return Path(explicit_path)
    if CISCO_CONFIG_PATH.exists():
        return CISCO_CONFIG_PATH
    return CISCO_EXAMPLE_CONFIG_PATH


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Create config.cisco.json from config.cisco.example.json."
        )
    config = load_json(path)
    if not is_cisco_config(config):
        raise ValueError(
            f"{path} is not a Cisco IOS config. Use config.cisco.example.json as the template."
        )
    config.setdefault("device", {"vendor": "cisco", "platform": "ios"})
    config.setdefault("port", config.get("ssh_port", 22))
    config.setdefault("device_name", "cisco-switch")
    return config


def ensure_password(config: Dict[str, Any]) -> None:
    if config.get("password"):
        return
    password = getpass.getpass(
        f"Please input SSH password for {config.get('host')} "
        f"(press Enter to use blank password): "
    )
    config["password"] = password


def prompt_password(config: Dict[str, Any], prompt: str) -> None:
    config["password"] = getpass.getpass(prompt)


def connect_with_auth_retry(config: Dict[str, Any], attempts: int = 3) -> CiscoIOS:
    last_error: Optional[Exception] = None
    for attempt in range(1, attempts + 1):
        if attempt == 1:
            ensure_password(config)
        else:
            prompt_password(
                config,
                f"SSH authentication failed. Please input SSH password for "
                f"{config.get('host')} (attempt {attempt}/{attempts}): ",
            )

        device = CiscoIOS(config)
        try:
            device.connect()
            return device
        except paramiko.AuthenticationException as error:
            device.close()
            last_error = error

    if last_error:
        raise last_error
    raise paramiko.AuthenticationException("SSH authentication failed.")


def make_check(
    name: str,
    expected: str,
    actual: str,
    result: str,
    message: str,
) -> Dict[str, str]:
    return {
        "name": name,
        "expected": expected,
        "actual": actual,
        "result": result,
        "message": message,
    }


def skip_check(name: str, expected: str, message: str) -> Dict[str, str]:
    return make_check(name, expected, "", "SKIP", message)


def collect_outputs(device: CiscoIOS) -> Tuple[Dict[str, str], List[str]]:
    if device.client:
        try:
            return collect_outputs_interactive_shell(device)
        except Exception:
            pass

    outputs: Dict[str, str] = {}
    errors: List[str] = []
    for key, command in DAY5_COMMANDS.items():
        try:
            outputs[key] = device._run_command(command, timeout_seconds=60)
        except Exception as error:
            outputs[key] = ""
            errors.append(f"{command}: {type(error).__name__}: {error}")
    return outputs, errors


def collect_outputs_interactive_shell(device: CiscoIOS) -> Tuple[Dict[str, str], List[str]]:
    if not device.client:
        raise RuntimeError("CiscoIOS is not connected.")

    channel = device.client.invoke_shell(width=200, height=1000)
    channel.settimeout(2.0)
    _read_shell_until_prompt(channel, timeout_seconds=10)
    _send_shell_command(channel, "terminal length 0", timeout_seconds=10)
    _send_shell_command(channel, "terminal width 512", timeout_seconds=10)

    outputs: Dict[str, str] = {}
    errors: List[str] = []
    for key, command in DAY5_COMMANDS.items():
        try:
            outputs[key] = _send_shell_command(channel, command, timeout_seconds=90)
        except Exception as error:
            outputs[key] = ""
            errors.append(f"{command}: {type(error).__name__}: {error}")

    channel.close()
    return outputs, errors


def _send_shell_command(channel: Any, command: str, timeout_seconds: int = 30) -> str:
    channel.send(command + "\n")
    output = _read_shell_until_prompt(channel, timeout_seconds)
    return _clean_shell_output(output, command)


def _read_shell_until_prompt(channel: Any, timeout_seconds: int = 30) -> str:
    chunks: List[str] = []
    deadline = time.monotonic() + timeout_seconds
    last_data_at = time.monotonic()

    while time.monotonic() < deadline:
        if channel.recv_ready():
            data = channel.recv(65535).decode("utf-8", errors="replace")
            chunks.append(data)
            last_data_at = time.monotonic()
            if _looks_like_cisco_prompt("".join(chunks)):
                return "".join(chunks)
        elif chunks and time.monotonic() - last_data_at > 1.0:
            text = "".join(chunks)
            if _looks_like_cisco_prompt(text):
                return text
        time.sleep(0.1)

    raise TimeoutError(f"Cisco shell command timed out after {timeout_seconds}s.")


def _looks_like_cisco_prompt(output: str) -> bool:
    tail_lines = [line.strip() for line in output.replace("\r", "").splitlines() if line.strip()]
    if not tail_lines:
        return False
    return bool(re_match_prompt(tail_lines[-1]))


def re_match_prompt(line: str) -> bool:
    import re

    return bool(re.search(r"[A-Za-z0-9_.:/()-]+[>#]\s*$", line))


def _clean_shell_output(output: str, command: str) -> str:
    text = output.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    cleaned: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append(line)
            continue
        if stripped == command:
            continue
        if re_match_prompt(stripped):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() + ("\n" if cleaned else "")


def expected_connected_ports(config: Dict[str, Any]) -> List[str]:
    ports = config.get("expected_connected_ports", [])
    if isinstance(ports, str):
        return [item.strip() for item in ports.split(",") if item.strip()]
    return [str(port).strip() for port in ports if str(port).strip()]


def expected_vlan(config: Dict[str, Any]) -> str:
    return str(config.get("expected_vlan", 1))


def evaluate_topology(
    config: Dict[str, Any],
    outputs: Dict[str, str],
    command_errors: Optional[List[str]] = None,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    command_errors = command_errors or []
    version = cisco_parser.parse_show_version(outputs.get("show_version", ""))
    ip_interfaces = cisco_parser.parse_show_ip_interface_brief(
        outputs.get("show_ip_interface_brief", "")
    )
    interface_status = cisco_parser.parse_show_interfaces_status(
        outputs.get("show_interfaces_status", "")
    )
    vlans = cisco_parser.parse_show_vlan_brief(outputs.get("show_vlan_brief", ""))
    mac_table = cisco_parser.parse_show_mac_address_table(
        outputs.get("show_mac_address_table", "")
    )
    stp = cisco_parser.parse_show_spanning_tree_summary(
        outputs.get("show_spanning_tree_summary", "")
    )

    parsed = {
        "show_version": version,
        "ip_interfaces": ip_interfaces,
        "interface_status": interface_status,
        "vlans": vlans,
        "mac_address_table": mac_table,
        "spanning_tree": stp,
    }

    checks: List[Dict[str, str]] = []
    checks.append(
        make_check(
            "show version readable",
            "command output is present",
            "present" if outputs.get("show_version") else "missing",
            "PASS" if outputs.get("show_version") else "FAIL",
            "show version output was collected."
            if outputs.get("show_version")
            else "show version output is missing.",
        )
    )

    expected_model = str(config.get("expected_model", "WS-C2960CG-8TC-L"))
    actual_model = str(version.get("model", ""))
    checks.append(
        make_check(
            "Switch model",
            expected_model,
            actual_model or "unknown",
            "PASS" if actual_model == expected_model else "FAIL",
            "Cisco switch model matches expected profile."
            if actual_model == expected_model
            else "Cisco switch model does not match expected profile.",
        )
    )

    ios_version = str(version.get("ios_version", ""))
    checks.append(
        make_check(
            "IOS version parsed",
            "IOS version is present",
            ios_version or "unknown",
            "PASS" if ios_version else "FAIL",
            "IOS version was parsed from show version."
            if ios_version
            else "IOS version could not be parsed from show version.",
        )
    )

    checks.append(
        make_check(
            "show ip interface brief readable",
            "command output is present",
            "present" if outputs.get("show_ip_interface_brief") else "missing",
            "PASS" if outputs.get("show_ip_interface_brief") else "FAIL",
            "show ip interface brief output was collected."
            if outputs.get("show_ip_interface_brief")
            else "show ip interface brief output is missing.",
        )
    )

    expected_management_ip = str(config.get("expected_management_ip", "192.168.0.111"))
    vlan1 = ip_interfaces.get("Vlan1", {})
    vlan1_actual = (
        f"{vlan1.get('ip_address', 'unknown')} "
        f"{vlan1.get('status', 'unknown')}/{vlan1.get('protocol', 'unknown')}"
    )
    vlan1_ok = (
        vlan1.get("ip_address") == expected_management_ip
        and vlan1.get("status") == "up"
        and vlan1.get("protocol") == "up"
    )
    checks.append(
        make_check(
            "Vlan1 management IP",
            f"{expected_management_ip} up/up",
            vlan1_actual,
            "PASS" if vlan1_ok else "FAIL",
            "Vlan1 management IP and state match expected topology."
            if vlan1_ok
            else "Vlan1 management IP or state does not match expected topology.",
        )
    )

    checks.append(
        make_check(
            "show interfaces status readable",
            "command output is present",
            "present" if outputs.get("show_interfaces_status") else "missing",
            "PASS" if outputs.get("show_interfaces_status") else "FAIL",
            "show interfaces status output was collected."
            if outputs.get("show_interfaces_status")
            else "show interfaces status output is missing.",
        )
    )

    ports = expected_connected_ports(config)
    port_results = {
        port: interface_status.get(port, {}).get("status", "missing")
        for port in ports
    }
    connected_ok = bool(ports) and all(status == "connected" for status in port_results.values())
    checks.append(
        make_check(
            "Expected ports connected",
            ", ".join(f"{port}=connected" for port in ports),
            ", ".join(f"{port}={status}" for port, status in port_results.items())
            or "no expected ports configured",
            "PASS" if connected_ok else "FAIL",
            "All expected access/uplink ports are connected."
            if connected_ok
            else "One or more expected ports are not connected.",
        )
    )

    vlan_id = expected_vlan(config)
    vlan = vlans.get(vlan_id, {})
    vlan_active = vlan.get("status") == "active"
    checks.append(
        make_check(
            "VLAN 1 active",
            f"VLAN {vlan_id} active",
            f"VLAN {vlan_id} {vlan.get('status', 'missing')}",
            "PASS" if vlan_active else "FAIL",
            "Expected VLAN is active."
            if vlan_active
            else "Expected VLAN is missing or not active.",
        )
    )

    mac_entries = mac_table.get("entries", [])
    checks.append(
        make_check(
            "MAC address table readable",
            "at least one MAC table entry",
            f"{len(mac_entries)} entries",
            "PASS" if mac_entries else "FAIL",
            "MAC address table output contained entries."
            if mac_entries
            else "MAC address table output did not contain entries.",
        )
    )

    dynamic_count = int(mac_table.get("dynamic_count", 0))
    checks.append(
        make_check(
            "Dynamic MAC learned",
            "dynamic MAC count > 0",
            str(dynamic_count),
            "PASS" if dynamic_count > 0 else "FAIL",
            "At least one dynamic MAC address was learned."
            if dynamic_count > 0
            else "No dynamic MAC addresses were found.",
        )
    )

    checks.append(
        make_check(
            "spanning-tree summary readable",
            "command output is present",
            "present" if outputs.get("show_spanning_tree_summary") else "missing",
            "PASS" if outputs.get("show_spanning_tree_summary") else "FAIL",
            "show spanning-tree summary output was collected."
            if outputs.get("show_spanning_tree_summary")
            else "show spanning-tree summary output is missing.",
        )
    )

    expected_stp_mode = str(config.get("expected_stp_mode", "pvst")).lower()
    actual_stp_mode = str(stp.get("mode", ""))
    checks.append(
        make_check(
            "STP mode",
            expected_stp_mode,
            actual_stp_mode or "unknown",
            "PASS" if actual_stp_mode == expected_stp_mode else "FAIL",
            "STP mode matches expected profile."
            if actual_stp_mode == expected_stp_mode
            else "STP mode does not match expected profile.",
        )
    )

    blocking_ports = stp.get("vlan_blocking_ports", {}).get("VLAN0001")
    checks.append(
        make_check(
            "VLAN0001 blocking ports",
            "0",
            "unknown" if blocking_ports is None else str(blocking_ports),
            "PASS" if blocking_ports == 0 else "FAIL",
            "VLAN0001 has no blocking ports."
            if blocking_ports == 0
            else "VLAN0001 has blocking ports or could not be parsed.",
        )
    )

    for error in command_errors:
        checks.append(
            make_check(
                "Command execution",
                "all Cisco show commands execute",
                error,
                "FAIL",
                "A required Cisco show command failed.",
            )
        )

    return checks, parsed


def overall_result(checks: List[Dict[str, str]]) -> str:
    required = [check for check in checks if check["name"] in REQUIRED_CHECKS]
    if any(check["result"] == "FAIL" for check in required):
        return "FAIL"
    if any(check["result"] == "SKIP" for check in required):
        return "FAIL"
    return "PASS"


def build_report(
    config: Dict[str, Any],
    checks: List[Dict[str, str]],
    parsed: Dict[str, Any],
    outputs: Dict[str, str],
    started_at: str,
) -> Dict[str, Any]:
    return {
        "device_name": str(config.get("device_name", "cisco-switch")),
        "host": str(config.get("host", "")),
        "ssh_port": int(config.get("port", config.get("ssh_port", 22))),
        "username": str(config.get("username", "")),
        "device_type": str(config.get("device_type", "cisco_ios")),
        "legacy_ssh": bool(config.get("legacy_ssh", False)),
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "overall_result": overall_result(checks),
        "checks": checks,
        "parsed": parsed,
        "raw_outputs": outputs,
    }


def status_badge(status: str) -> str:
    normalized = str(status).lower()
    if normalized not in {"pass", "fail", "skip"}:
        normalized = "skip"
    return f'<span class="badge {normalized}">{html.escape(str(status))}</span>'


def build_html_report(report: Dict[str, Any]) -> str:
    rows = []
    for check in report["checks"]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(check['name'])}</td>"
            f"<td><code>{html.escape(check['expected'])}</code></td>"
            f"<td><code>{html.escape(check['actual'])}</code></td>"
            f"<td>{status_badge(check['result'])}</td>"
            f"<td>{html.escape(check['message'])}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cisco Switch Topology Validation</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --line: #d7dee8;
      --pass: #147a3d;
      --pass-bg: #e7f5ed;
      --fail: #b42318;
      --fail-bg: #fdecec;
      --skip: #8a5a00;
      --skip-bg: #fff4d8;
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
      padding: 32px 20px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 18px;
    }}
    .meta {{
      color: var(--muted);
      margin-bottom: 20px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin: 20px 0 24px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .metric .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }}
    .metric .value {{
      font-size: 22px;
      font-weight: 700;
      margin-top: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #edf2f7;
      font-weight: 600;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .badge {{
      display: inline-block;
      min-width: 52px;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
    }}
    .badge.pass {{
      background: var(--pass-bg);
      color: var(--pass);
    }}
    .badge.fail {{
      background: var(--fail-bg);
      color: var(--fail);
    }}
    .badge.skip {{
      background: var(--skip-bg);
      color: var(--skip);
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
    }}
  </style>
</head>
<body>
<main>
  <h1>Cisco Switch Topology Validation</h1>
  <div class="meta">
    Device: <strong>{html.escape(report['device_name'])}</strong><br>
    Host: <code>{html.escape(str(report['host']))}:{html.escape(str(report['ssh_port']))}</code><br>
    Started: {html.escape(report['started_at'])}<br>
    Finished: {html.escape(report['finished_at'])}
  </div>
  <div class="summary">
    <div class="metric"><div class="label">Overall</div><div class="value">{status_badge(report['overall_result'])}</div></div>
    <div class="metric"><div class="label">Checks</div><div class="value">{len(report['checks'])}</div></div>
    <div class="metric"><div class="label">Legacy SSH</div><div class="value">{html.escape(str(report['legacy_ssh']))}</div></div>
  </div>
  <h2>Check Results</h2>
  <table>
    <thead>
      <tr><th>Check</th><th>Expected</th><th>Actual</th><th>Result</th><th>Message</th></tr>
    </thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</main>
</body>
</html>
"""


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_JSON.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with REPORT_HTML.open("w", encoding="utf-8") as file:
        file.write(build_html_report(report))
    return REPORT_JSON, REPORT_HTML


def result_text(value: Any) -> str:
    text = str(value)
    status = text.strip()
    if status == "PASS":
        return color_text(text, COLOR_GREEN)
    if status == "FAIL":
        return color_text(text, COLOR_RED)
    if status == "SKIP":
        return color_text(text, COLOR_YELLOW)
    return text


def padded_result_text(value: Any, width: int = 8) -> str:
    text = str(value)
    return result_text(f"{text:<{width}}")


def legacy_ssh_hint(config: Dict[str, Any], error: Exception) -> str:
    if config.get("legacy_ssh"):
        return (
            f"{type(error).__name__}: {error}. legacy_ssh is enabled; if this still fails, "
            "verify the switch SSH server supports an algorithm Paramiko can negotiate."
        )
    return (
        f"{type(error).__name__}: {error}. Older Cisco IOS switches may require legacy "
        "SSH algorithms. Set legacy_ssh=true in config.cisco.example.json or config.cisco.json."
    )


def run_validation(config: Dict[str, Any]) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    checks: List[Dict[str, str]] = []
    outputs: Dict[str, str] = {}
    parsed: Dict[str, Any] = {}
    device: Optional[CiscoIOS] = None

    try:
        device = connect_with_auth_retry(config)
        checks.append(
            make_check(
                "SSH login",
                "authenticated",
                "authenticated",
                "PASS",
                "SSH login succeeded.",
            )
        )
        outputs, command_errors = collect_outputs(device)
        topology_checks, parsed = evaluate_topology(config, outputs, command_errors)
        checks.extend(topology_checks)
    except (
        paramiko.AuthenticationException,
        paramiko.SSHException,
        socket.timeout,
        TimeoutError,
        OSError,
        CommandTimeoutError,
        ValueError,
    ) as error:
        checks.append(
            make_check(
                "SSH login",
                "authenticated",
                legacy_ssh_hint(config, error),
                "FAIL",
                "SSH login failed; Cisco show command checks were skipped.",
            )
        )
        for name, expected in [
            ("show version readable", "command output is present"),
            ("Switch model", str(config.get("expected_model", "WS-C2960CG-8TC-L"))),
            ("IOS version parsed", "IOS version is present"),
            ("show ip interface brief readable", "command output is present"),
            ("Vlan1 management IP", f"{config.get('expected_management_ip', '192.168.0.111')} up/up"),
            ("show interfaces status readable", "command output is present"),
            ("Expected ports connected", ", ".join(expected_connected_ports(config))),
            ("VLAN 1 active", f"VLAN {expected_vlan(config)} active"),
            ("MAC address table readable", "at least one MAC table entry"),
            ("Dynamic MAC learned", "dynamic MAC count > 0"),
            ("spanning-tree summary readable", "command output is present"),
            ("VLAN0001 blocking ports", "0"),
        ]:
            checks.append(skip_check(name, expected, "Skipped because SSH login failed."))
    finally:
        if device:
            device.close()

    report = build_report(config, checks, parsed, outputs, started_at)
    try:
        json_path, html_path = write_reports(report)
        report["report_paths"] = {"json": str(json_path), "html": str(html_path)}
        report["checks"].append(
            make_check(
                "Report generation",
                "JSON and HTML report files",
                f"{json_path}; {html_path}",
                "PASS",
                "Cisco topology reports were generated.",
            )
        )
        report["overall_result"] = overall_result(report["checks"])
        write_reports(report)
    except Exception as error:
        report["checks"].append(
            make_check(
                "Report generation",
                "JSON and HTML report files",
                f"{type(error).__name__}: {error}",
                "FAIL",
                "Cisco topology report generation failed.",
            )
        )
        report["overall_result"] = "FAIL"
    return report


def print_summary(report: Dict[str, Any]) -> None:
    print()
    print(color_text("=" * 72, COLOR_CYAN))
    print(color_text("Cisco Switch Topology Validation", COLOR_BOLD))
    print(color_text("=" * 72, COLOR_CYAN))
    print(f"Device: {report['device_name']}")
    print(f"Host: {report['host']}:{report['ssh_port']}")
    print(f"Overall Result: {result_text(report['overall_result'])}")
    print(color_text("-" * 72, COLOR_CYAN))
    for check in report["checks"]:
        print(f"{padded_result_text(check['result'])} {check['name']}: {check['message']}")
    print(color_text("-" * 72, COLOR_CYAN))
    paths = report.get("report_paths", {})
    if paths:
        print(f"{'JSON report':<12}: {color_text(str(paths.get('json')), COLOR_DIM)}")
        print(f"{'HTML report':<12}: {color_text(str(paths.get('html')), COLOR_DIM)}")
    print(color_text("=" * 72, COLOR_CYAN))


def main() -> int:
    try:
        args = parse_args()
        config_path = resolve_config_path(args.config)
        config = load_config(config_path)
        report = run_validation(config)
        print_summary(report)
        return 0 if report["overall_result"] == "PASS" else 1
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
