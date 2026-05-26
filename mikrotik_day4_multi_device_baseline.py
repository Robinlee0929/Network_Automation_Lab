import getpass
import html
import json
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import paramiko

from mikrotik_day2_auto_setup import (
    CONFIG_PATH,
    COLOR_BOLD,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    Day2Config,
    apply_device_profile,
    color_text,
    connect_ssh_with_auth_retry,
    load_config,
    parse_identity,
    parse_package_version,
    parse_routerboard_firmware,
    run_raw_command,
)
from mikrotik_post_validation import (
    parse_ip_addresses,
    parse_wan_dhcp_client,
    sanitize_path_name,
)


REPORT_ROOT = Path("reports")

DAY4_COMMANDS = {
    "identity": "/system identity print",
    "package": "/system package print",
    "routerboard": "/system routerboard print",
    "dhcp_client": "/ip dhcp-client print detail",
    "ip_address": "/ip address print",
    "services": "/ip service print",
}

REQUIRED_CHECKS = {
    "SSH connection",
    "Device identity",
    "RouterOS version",
    "RouterBOARD current firmware",
    "RouterBOARD upgrade firmware",
    "WAN DHCP client status",
    "LAN bridge IP",
    "SSH service status",
    "Report generation",
}


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


def load_day4_device_configs(path: Path = CONFIG_PATH) -> List[Day2Config]:
    base_config = load_config(path)
    profiles = base_config.device_profiles or {}
    if not profiles:
        return [base_config]

    configs: List[Day2Config] = []
    for device_name in profiles:
        config = load_config(path)
        apply_device_profile(config, str(device_name))
        apply_day4_connection_profile(config, profiles.get(device_name, {}))
        apply_day4_precheck_host(config)
        configs.append(config)
    return configs


def apply_day4_connection_profile(config: Day2Config, profile: Any) -> Day2Config:
    if not isinstance(profile, dict):
        return config

    day4_profile = profile.get("day4", {})
    if not isinstance(day4_profile, dict):
        day4_profile = {}

    day4_host = (
        day4_profile.get("host")
        or day4_profile.get("wan_host")
        or profile.get("day4_host")
        or profile.get("wan_host")
    )
    if day4_host:
        config.host = str(day4_host).strip()
        setattr(config, "_day4_host_from_profile", True)

    day4_port = (
        day4_profile.get("ssh_port")
        or day4_profile.get("port")
        or profile.get("day4_ssh_port")
    )
    if day4_port:
        config.port = int(day4_port)

    return config


def strip_cidr(value: str) -> str:
    return str(value).split("/", 1)[0].strip()


def load_day4_precheck_wan_ip(device_name: str) -> str:
    report_path = (
        REPORT_ROOT
        / sanitize_path_name(device_name)
        / "day4_precheck_wan_ssh.json"
    )
    if not report_path.exists():
        return ""
    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError):
        return ""
    return strip_cidr(str(report.get("wan_dhcp_ip", "")))


def apply_day4_precheck_host(config: Day2Config) -> Day2Config:
    if getattr(config, "_day4_host_from_profile", False):
        return config
    wan_ip = load_day4_precheck_wan_ip(config.device_name)
    if wan_ip:
        config.host = wan_ip
    return config


def ensure_device_password(config: Day2Config) -> None:
    if config.password:
        return
    config.password = getpass.getpass(
        f"Please input SSH password for {config.device_name} ({config.host}): "
    ).strip()
    if not config.password:
        raise ValueError(f"SSH password is required for {config.device_name}.")


def prompt_device_host(config: Day2Config) -> None:
    prompt = (
        f"Please input Day 4 SSH host/IP for {config.device_name} "
        f"(press Enter to use config default: {config.host}): "
    )
    host = input(prompt).strip()
    if host:
        config.host = host


def collect_outputs(client: paramiko.SSHClient) -> Tuple[Dict[str, str], List[str]]:
    outputs: Dict[str, str] = {}
    errors: List[str] = []
    for key, command in DAY4_COMMANDS.items():
        try:
            outputs[key] = run_raw_command(client, command)
        except Exception as error:
            outputs[key] = ""
            errors.append(f"{command}: {type(error).__name__}: {error}")
    return outputs, errors


def parse_ssh_service_enabled(output: str) -> bool:
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
            return "X" not in flags
    return False


def lan_bridge_ip(output: str) -> str:
    for address in parse_ip_addresses(output):
        if "bridge" in address.get("interface", "").lower():
            return address.get("address", "")
    return ""


def evaluate_device_outputs(
    config: Day2Config,
    outputs: Dict[str, str],
    command_errors: List[str],
) -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []

    identity = parse_identity(outputs.get("identity", ""))
    checks.append(
        make_check(
            "Device identity",
            config.device_name,
            identity or "unknown",
            "PASS" if identity == config.device_name else "FAIL",
            "Router identity matches expected device name."
            if identity == config.device_name
            else "Router identity does not match expected device name.",
        )
    )

    routeros_version = parse_package_version(outputs.get("package", ""))
    checks.append(
        make_check(
            "RouterOS version",
            "version is present",
            routeros_version or "unknown",
            "PASS" if routeros_version else "FAIL",
            "RouterOS package version was parsed."
            if routeros_version
            else "RouterOS package version could not be parsed.",
        )
    )

    firmware = parse_routerboard_firmware(outputs.get("routerboard", ""))
    current_firmware = firmware.get("current-firmware", "")
    checks.append(
        make_check(
            "RouterBOARD current firmware",
            "current-firmware is present",
            current_firmware or "unknown",
            "PASS" if current_firmware else "FAIL",
            "RouterBOARD current firmware was parsed."
            if current_firmware
            else "RouterBOARD current firmware could not be parsed.",
        )
    )

    upgrade_firmware = firmware.get("upgrade-firmware", "")
    checks.append(
        make_check(
            "RouterBOARD upgrade firmware",
            "upgrade-firmware is present",
            upgrade_firmware or "unknown",
            "PASS" if upgrade_firmware else "FAIL",
            "RouterBOARD upgrade firmware was parsed."
            if upgrade_firmware
            else "RouterBOARD upgrade firmware could not be parsed.",
        )
    )

    dhcp_client = parse_wan_dhcp_client(outputs.get("dhcp_client", ""))
    wan_interface = dhcp_client.get("interface", "")
    wan_status = dhcp_client.get("status", "").lower()
    expected_wan_mode = config.expected_wan_mode
    expected_wan_status = "bound" if expected_wan_mode == "dhcp" else expected_wan_mode
    wan_ok = wan_interface == config.expected_wan_interface and wan_status == "bound"
    checks.append(
        make_check(
            "WAN DHCP client status",
            f"{config.expected_wan_interface} {expected_wan_status}",
            f"{wan_interface or 'unknown'} {wan_status or 'unknown'}",
            "PASS" if wan_ok else "FAIL",
            "WAN DHCP client is bound on the expected interface."
            if wan_ok
            else "WAN DHCP client is not bound on the expected interface.",
        )
    )

    actual_lan_ip = lan_bridge_ip(outputs.get("ip_address", ""))
    checks.append(
        make_check(
            "LAN bridge IP",
            config.expected_lan_ip_cidr,
            actual_lan_ip or "not found",
            "PASS" if actual_lan_ip == config.expected_lan_ip_cidr else "FAIL",
            "LAN bridge IP matches expected profile."
            if actual_lan_ip == config.expected_lan_ip_cidr
            else "LAN bridge IP does not match expected profile.",
        )
    )

    ssh_enabled = parse_ssh_service_enabled(outputs.get("services", ""))
    checks.append(
        make_check(
            "SSH service status",
            "enabled",
            "enabled" if ssh_enabled else "disabled or missing",
            "PASS" if ssh_enabled else "FAIL",
            "SSH service is enabled."
            if ssh_enabled
            else "SSH service is disabled or missing.",
        )
    )

    for error in command_errors:
        checks.append(
            make_check(
                "Command execution",
                "all baseline commands execute",
                error,
                "FAIL",
                "A required RouterOS command failed.",
            )
        )

    return checks


def build_device_report(
    config: Day2Config,
    checks: List[Dict[str, str]],
    started_at: str,
) -> Dict[str, Any]:
    required_failures = [
        check for check in checks if check["name"] in REQUIRED_CHECKS and check["result"] == "FAIL"
    ]
    skipped = [check for check in checks if check["result"] == "SKIP"]
    overall = "FAIL" if required_failures else ("SKIP" if skipped and len(skipped) == len(checks) else "PASS")
    return {
        "device_name": config.device_name,
        "host": config.host,
        "ssh_port": config.port,
        "username": config.username,
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "overall_result": overall,
        "checks": checks,
    }


def build_text_report(report: Dict[str, Any]) -> str:
    divider = "=" * 72
    lines = [
        divider,
        "MikroTik Day 4 Multi-Device Baseline Validation",
        divider,
        f"Device: {report['device_name']}",
        f"Host: {report['host']}:{report['ssh_port']}",
        f"Overall Result: {report['overall_result']}",
        "-" * 72,
    ]
    for check in report["checks"]:
        lines.extend(
            [
                f"Check: {check['name']}",
                f"Expected: {check['expected']}",
                f"Actual: {check['actual']}",
                f"Result: {check['result']}",
                f"Message: {check['message']}",
                "-" * 72,
            ]
        )
    return "\n".join(lines) + "\n"


def status_badge(status: str) -> str:
    normalized = str(status).lower()
    if normalized not in {"pass", "fail", "skip"}:
        normalized = "skip"
    return f'<span class="badge {normalized}">{html.escape(str(status))}</span>'


def html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f9fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #637083;
      --line: #d8e0ea;
      --pass: #147a3d;
      --pass-bg: #e8f6ee;
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
      font-weight: 700;
    }}
    h2 {{
      margin: 28px 0 12px;
      font-size: 18px;
    }}
    .meta {{
      color: var(--muted);
      margin-bottom: 24px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
      font-size: 24px;
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
{body}
</main>
</body>
</html>
"""


def build_device_html_report(report: Dict[str, Any]) -> str:
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
    body = f"""
<h1>MikroTik Day 4 Device Baseline</h1>
<div class="meta">
  Device: <strong>{html.escape(report['device_name'])}</strong><br>
  Host: <code>{html.escape(str(report['host']))}:{html.escape(str(report['ssh_port']))}</code><br>
  Started: {html.escape(report['started_at'])}<br>
  Finished: {html.escape(report['finished_at'])}
</div>
<div class="summary">
  <div class="metric"><div class="label">Overall</div><div class="value">{status_badge(report['overall_result'])}</div></div>
  <div class="metric"><div class="label">Checks</div><div class="value">{len(report['checks'])}</div></div>
</div>
<h2>Check Results</h2>
<table>
  <thead>
    <tr><th>Check</th><th>Expected</th><th>Actual</th><th>Result</th><th>Message</th></tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""
    return html_page("MikroTik Day 4 Device Baseline", body)


def write_device_report(report: Dict[str, Any]) -> Tuple[Path, Path, Path]:
    report_dir = REPORT_ROOT / sanitize_path_name(report["device_name"])
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "day4_baseline_validation.json"
    txt_path = report_dir / "day4_baseline_validation.txt"
    html_path = report_dir / "day4_baseline_validation.html"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report))
    with html_path.open("w", encoding="utf-8") as file:
        file.write(build_device_html_report(report))
    return json_path, txt_path, html_path


def run_device_validation(config: Day2Config) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    checks: List[Dict[str, str]] = []
    client: Optional[paramiko.SSHClient] = None

    try:
        prompt_device_host(config)
        ensure_device_password(config)
        client = connect_ssh_with_auth_retry(config)
        checks.append(
            make_check(
                "SSH connection",
                "authenticated",
                "authenticated",
                "PASS",
                "SSH login succeeded.",
            )
        )
        outputs, command_errors = collect_outputs(client)
        checks.extend(evaluate_device_outputs(config, outputs, command_errors))
    except (paramiko.AuthenticationException, socket.timeout, TimeoutError, OSError, ValueError) as error:
        checks.append(
            make_check(
                "SSH connection",
                "authenticated",
                f"{type(error).__name__}: {error}",
                "FAIL",
                "SSH login failed; dependent checks were skipped.",
            )
        )
        for name, expected in [
            ("Device identity", config.device_name),
            ("RouterOS version", "version is present"),
            ("RouterBOARD current firmware", "current-firmware is present"),
            ("RouterBOARD upgrade firmware", "upgrade-firmware is present"),
            ("WAN DHCP client status", f"{config.expected_wan_interface} bound"),
            ("LAN bridge IP", config.expected_lan_ip_cidr),
            ("SSH service status", "enabled"),
        ]:
            checks.append(skip_check(name, expected, "Skipped because SSH connection failed."))
    finally:
        if client:
            client.close()

    report = build_device_report(config, checks, started_at)
    try:
        json_path, txt_path, html_path = write_device_report(report)
        report["report_paths"] = {
            "json": str(json_path),
            "txt": str(txt_path),
            "html": str(html_path),
        }
        report["checks"].append(
            make_check(
                "Report generation",
                "JSON, TXT, and HTML report files",
                f"{json_path}; {txt_path}; {html_path}",
                "PASS",
                "Per-device reports were generated.",
            )
        )
        report["overall_result"] = build_device_report(
            config,
            report["checks"],
            started_at,
        )["overall_result"]
        write_device_report(report)
    except Exception as error:
        report["checks"].append(
            make_check(
                "Report generation",
                "JSON and TXT report files",
                f"{type(error).__name__}: {error}",
                "FAIL",
                "Per-device report generation failed.",
            )
        )
        report["overall_result"] = "FAIL"
    return report


def troubleshooting_message(report: Dict[str, Any]) -> str:
    failed = [check["name"] for check in report["checks"] if check["result"] == "FAIL"]
    if not failed:
        return "No action required."
    if "SSH connection" in failed:
        return "Check management IP, SSH reachability, username, password, and RouterOS SSH service."
    if "LAN bridge IP" in failed:
        return "Check the device profile expected_lan_bridge_ip and RouterOS bridge address."
    if "WAN DHCP client status" in failed:
        return "Check ether1 cabling, DHCP server, and RouterOS DHCP client state."
    return "Review the failed checks in the per-device report."


def build_summary_report(device_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    pass_count = sum(1 for report in device_reports if report["overall_result"] == "PASS")
    fail_count = sum(1 for report in device_reports if report["overall_result"] == "FAIL")
    skip_count = sum(1 for report in device_reports if report["overall_result"] == "SKIP")
    devices = []
    for report in device_reports:
        failed_checks = [
            check["name"] for check in report["checks"] if check["result"] == "FAIL"
        ]
        devices.append(
            {
                "device_name": report["device_name"],
                "host": report["host"],
                "overall_result": report["overall_result"],
                "failed_check_names": failed_checks,
                "checks": [
                    {
                        "name": check["name"],
                        "result": check["result"],
                    }
                    for check in report["checks"]
                ],
                "troubleshooting": troubleshooting_message(report),
            }
        )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_devices": len(device_reports),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "devices": devices,
    }


def build_summary_text(summary: Dict[str, Any]) -> str:
    divider = "=" * 72
    lines = [
        divider,
        "MikroTik Day 4 Summary Report",
        divider,
        f"Total devices: {summary['total_devices']}",
        f"PASS count: {summary['pass_count']}",
        f"FAIL count: {summary['fail_count']}",
        f"SKIP count: {summary['skip_count']}",
        "-" * 72,
    ]
    for device in summary["devices"]:
        lines.extend(
            [
                f"Device: {device['device_name']}",
                f"Host: {device['host']}",
                f"Overall Result: {device['overall_result']}",
                "Failed Checks: "
                + (", ".join(device["failed_check_names"]) or "None"),
                f"Troubleshooting: {device['troubleshooting']}",
                "-" * 72,
            ]
        )
    return "\n".join(lines) + "\n"


def build_summary_html_report(summary: Dict[str, Any]) -> str:
    device_rows = []
    for device in summary["devices"]:
        failed = ", ".join(device["failed_check_names"]) or "None"
        device_rows.append(
            "<tr>"
            f"<td>{html.escape(device['device_name'])}</td>"
            f"<td><code>{html.escape(str(device['host']))}</code></td>"
            f"<td>{status_badge(device['overall_result'])}</td>"
            f"<td>{html.escape(failed)}</td>"
            f"<td>{html.escape(device['troubleshooting'])}</td>"
            "</tr>"
        )

    check_sections = []
    for device in summary["devices"]:
        check_rows = []
        for check in device.get("checks", []):
            check_rows.append(
                "<tr>"
                f"<td>{html.escape(check['name'])}</td>"
                f"<td>{status_badge(check['result'])}</td>"
                "</tr>"
            )
        check_sections.append(
            f"""
<h2>{html.escape(device['device_name'])} Checks</h2>
<table>
  <thead><tr><th>Check</th><th>Result</th></tr></thead>
  <tbody>{''.join(check_rows)}</tbody>
</table>
"""
        )

    body = f"""
<h1>MikroTik Day 4 Multi-Device Baseline</h1>
<div class="meta">Generated: {html.escape(summary['generated_at'])}</div>
<div class="summary">
  <div class="metric"><div class="label">Total Devices</div><div class="value">{summary['total_devices']}</div></div>
  <div class="metric"><div class="label">PASS</div><div class="value">{summary['pass_count']}</div></div>
  <div class="metric"><div class="label">FAIL</div><div class="value">{summary['fail_count']}</div></div>
  <div class="metric"><div class="label">SKIP</div><div class="value">{summary['skip_count']}</div></div>
</div>
<h2>Device Summary</h2>
<table>
  <thead>
    <tr><th>Device</th><th>Host</th><th>Overall</th><th>Failed Checks</th><th>Troubleshooting</th></tr>
  </thead>
  <tbody>
    {''.join(device_rows)}
  </tbody>
</table>
{''.join(check_sections)}
"""
    return html_page("MikroTik Day 4 Multi-Device Baseline", body)


def write_summary_report(summary: Dict[str, Any]) -> Tuple[Path, Path, Path]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_ROOT / "day4_summary_report.json"
    txt_path = REPORT_ROOT / "day4_summary_report.txt"
    html_path = REPORT_ROOT / "day4_summary_report.html"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_summary_text(summary))
    with html_path.open("w", encoding="utf-8") as file:
        file.write(build_summary_html_report(summary))
    return json_path, txt_path, html_path


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


def print_summary(summary: Dict[str, Any], json_path: Path, txt_path: Path, html_path: Path) -> None:
    print()
    print(color_text("=" * 72, COLOR_CYAN))
    print(color_text("MikroTik Day 4 Multi-Device Baseline Validation", COLOR_BOLD))
    print(color_text("=" * 72, COLOR_CYAN))
    print(f"{'Total devices':<14}: {summary['total_devices']}")
    print(f"{'PASS':<14}: {color_text(str(summary['pass_count']), COLOR_GREEN)}")
    print(f"{'FAIL':<14}: {color_text(str(summary['fail_count']), COLOR_RED)}")
    print(f"{'SKIP':<14}: {color_text(str(summary['skip_count']), COLOR_YELLOW)}")
    print(color_text("-" * 72, COLOR_CYAN))
    for device in summary["devices"]:
        print(f"{device['device_name']:<24} {result_text(device['overall_result'])}")
        for check in device.get("checks", []):
            print(f"  {padded_result_text(check['result'])} {check['name']}")
        if device["failed_check_names"]:
            print(f"  {color_text('Failed', COLOR_RED)}: {', '.join(device['failed_check_names'])}")
            print(f"  Hint  : {device['troubleshooting']}")
    print(color_text("-" * 72, COLOR_CYAN))
    print(f"{'JSON summary':<14}: {json_path}")
    print(f"{'TXT summary':<14}: {txt_path}")
    print(f"{'HTML summary':<14}: {html_path}")
    print(color_text("=" * 72, COLOR_CYAN))


def main() -> int:
    try:
        configs = load_day4_device_configs(CONFIG_PATH)
        reports = [run_device_validation(config) for config in configs]
        summary = build_summary_report(reports)
        json_path, txt_path, html_path = write_summary_report(summary)
        print_summary(summary, json_path, txt_path, html_path)
        return 1 if summary["fail_count"] else 0
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
