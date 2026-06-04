import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mikrotik_day33_vrrp_topology_dry_run as day33
from mikrotik_day2_auto_setup import color_text


DAY = "Day34"
TITLE = "VRRP Staged Apply Plan and Safety Gate"
SAFETY_MODE = "blocked_guarded_live_plan"
REPORT_DIR = Path("reports") / "lab-summary"
REPORT_STEM = "day34_vrrp_staged_apply_plan"
REPORT_JSON = REPORT_DIR / f"{REPORT_STEM}.json"
REPORT_HTML = REPORT_DIR / f"{REPORT_STEM}.html"
REPORT_TXT = REPORT_DIR / f"{REPORT_STEM}.txt"
DEFAULT_PROFILE = Path("topology_profiles") / "day34_vrrp_staged_apply_plan.json"
EXECUTION_STATUS = "BLOCKED - PLAN ONLY - NOT EXECUTED"
REQUIRED_EVIDENCE = [
    Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.json",
    Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.json",
]

PLAN_ONLY_NOTE = (
    "BLOCKED PLAN ONLY and NOT EXECUTED: Day34 renders staged apply steps and safety gate evidence only."
)


def assert_rollback_preview_safe(command: str) -> None:
    normalized = day33.normalize_command(command)
    if not normalized.startswith("/"):
        raise ValueError(f"Rollback preview command must start with '/': {command}")
    if " remove " not in f" {normalized} ":
        raise ValueError(f"Rollback preview command must be an explicit remove preview: {command}")
    if "[find " not in normalized:
        raise ValueError(f"Rollback preview command must scope remove with [find ...]: {command}")
    for keyword in ("reboot", "reset-configuration", "shutdown", "disable", "enable"):
        if keyword in normalized:
            raise ValueError(f"Unsafe rollback preview command blocked: {command}")


def evidence_status(profile: Dict[str, Any], project_root: Path) -> List[Dict[str, str]]:
    configured = profile.get("required_evidence") or [path.as_posix() for path in REQUIRED_EVIDENCE]
    rows: List[Dict[str, str]] = []
    for raw_path in configured:
        relative_path = Path(str(raw_path))
        exists = (project_root / relative_path).exists()
        rows.append(
            {
                "path": relative_path.as_posix(),
                "status": "PASS" if exists else "BLOCKED",
                "message": "Evidence file found." if exists else "Required safety evidence is missing.",
            }
        )
    return rows


def build_router_plan(device: Dict[str, Any], topology: Dict[str, Any]) -> Dict[str, Any]:
    preview = day33.build_device_commands(device, topology)
    validation = [
        "/interface vrrp print detail",
        "/ip address print detail",
        f"/ping {topology['virtual_gateway_ip']} count=3",
    ]
    rollback = [
        f"/ip address remove [find address={topology['virtual_gateway_cidr']} interface={topology['vrrp_interface_name']}]",
        f"/interface vrrp remove [find name={topology['vrrp_interface_name']}]",
    ]
    for command in validation:
        day33.assert_preview_command_safe(command)
    for command in rollback:
        assert_rollback_preview_safe(command)
    return {
        "device_name": preview["device_name"],
        "role": preview["role"],
        "priority": preview["priority"],
        "precheck_commands": preview["precheck_commands"],
        "planned_apply_commands": preview["configuration_preview_commands"],
        "validation_commands": validation,
        "rollback_preview_commands": rollback,
        "execution_allowed": False,
        "execution_status": EXECUTION_STATUS,
    }


def build_stages(topology: Dict[str, Any], evidence_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    backup_plan = build_router_plan(topology["roles"]["backup"], topology)
    primary_plan = build_router_plan(topology["roles"]["primary"], topology)
    return [
        {
            "id": "stage_0_evidence_gate",
            "title": "Evidence and Operator Gate",
            "status": "PASS" if all(row["status"] == "PASS" for row in evidence_rows) else "BLOCKED",
            "checks": evidence_rows,
            "execution_allowed": False,
        },
        {
            "id": "stage_1_backup_router_preview",
            "title": "Backup Router VRRP Preview",
            "status": "PLAN_ONLY",
            "device": backup_plan,
            "execution_allowed": False,
        },
        {
            "id": "stage_2_primary_router_preview",
            "title": "Primary Router VRRP Preview",
            "status": "PLAN_ONLY",
            "device": primary_plan,
            "execution_allowed": False,
        },
        {
            "id": "stage_3_post_apply_validation_preview",
            "title": "Post-apply Validation Preview",
            "status": "PLAN_ONLY",
            "commands": [
                "/interface vrrp print detail",
                "/ip address print detail",
                f"/ping {topology['virtual_gateway_ip']} count=3",
            ],
            "expected_state": {
                "virtual_gateway_cidr": topology["virtual_gateway_cidr"],
                "primary_priority": topology["primary_priority"],
                "backup_priority": topology["backup_priority"],
                "vrid": topology["vrid"],
            },
            "execution_allowed": False,
        },
    ]


def build_report(profile: Dict[str, Any], profile_path: Path, project_root: Path = Path(".")) -> Dict[str, Any]:
    topology = day33.validate_profile(profile)
    evidence_rows = evidence_status(profile, project_root)
    gate_status = "PASS" if all(row["status"] == "PASS" for row in evidence_rows) else "BLOCKED"
    return {
        "day": DAY,
        "title": TITLE,
        "safety_mode": SAFETY_MODE,
        "execution_status": EXECUTION_STATUS,
        "profile_path": profile_path.as_posix(),
        "overall_status": gate_status,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "topology": {key: value for key, value in topology.items() if key != "roles"},
        "safety_gate": {
            "day32_readonly_precheck_evidence": evidence_rows[0]["status"] if evidence_rows else "BLOCKED",
            "day33_dry_run_evidence": evidence_rows[1]["status"] if len(evidence_rows) > 1 else "BLOCKED",
            "manual_operator_confirmation": "BLOCKED",
            "rollback_plan_visible": "PASS",
            "live_execution": "BLOCKED",
        },
        "blocked_actions": profile.get("blocked_actions", []),
        "stages": build_stages(topology, evidence_rows),
        "notes": [PLAN_ONLY_NOTE] + list(profile.get("notes", [])),
    }


def html_badge(status: Any) -> str:
    value = str(status or "UNKNOWN").upper()
    css = value.lower() if value in {"PASS", "FAIL", "BLOCKED"} else "warn"
    return f'<span class="badge {css}">{html.escape(value)}</span>'


def render_command_list(commands: List[str]) -> str:
    return "".join(f"<li><code>{html.escape(command)}</code></li>" for command in commands)


def build_html_report(report: Dict[str, Any]) -> str:
    gate_rows = "".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html_badge(value)}</td></tr>"
        for key, value in report.get("safety_gate", {}).items()
    )
    stage_sections = []
    for stage in report.get("stages", []):
        body = ""
        if "device" in stage:
            device = stage["device"]
            body = (
                f"<p><strong>{html.escape(str(device['device_name']))}</strong> "
                f"({html.escape(str(device['role']))}, priority {html.escape(str(device['priority']))})</p>"
                "<h3>Planned apply commands</h3>"
                f"<ol>{render_command_list(device.get('planned_apply_commands', []))}</ol>"
                "<h3>Rollback preview commands</h3>"
                f"<ol>{render_command_list(device.get('rollback_preview_commands', []))}</ol>"
            )
        elif "checks" in stage:
            body = "<table><tbody>" + "".join(
                f"<tr><td>{html.escape(row['path'])}</td><td>{html_badge(row['status'])}</td><td>{html.escape(row['message'])}</td></tr>"
                for row in stage.get("checks", [])
            ) + "</tbody></table>"
        else:
            body = f"<ol>{render_command_list(stage.get('commands', []))}</ol>"
        stage_sections.append(
            "<section class='panel'>"
            f"<h2>{html.escape(stage['title'])} {html_badge(stage['status'])}</h2>"
            f"{body}</section>"
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
    .panel {{ background: white; border: 1px solid #d8e0ec; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .badge {{ display: inline-block; min-width: 70px; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 800; text-align: center; }}
    .pass {{ background: #e7f7ee; color: #147a3d; }}
    .blocked, .fail {{ background: #fdecec; color: #b42318; }}
    .warn {{ background: #fff4d8; color: #8a6100; }}
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
      <h2>Safety Gate</h2>
      <table><tbody>{gate_rows}</tbody></table>
    </section>
    {''.join(stage_sections)}
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
        PLAN_ONLY_NOTE,
        "-" * 72,
        "Safety gate:",
    ]
    for key, value in report.get("safety_gate", {}).items():
        lines.append(f"  - {key}: {value}")
    lines.append("-" * 72)
    for stage in report.get("stages", []):
        lines.append(f"{stage['id']}: {stage['title']} [{stage['status']}]")
        device = stage.get("device")
        if device:
            lines.append(f"  Device: {device['device_name']} ({device['role']}, priority {device['priority']})")
            lines.extend(f"  PLAN: {command}" for command in device.get("planned_apply_commands", []))
            lines.extend(f"  ROLLBACK: {command}" for command in device.get("rollback_preview_commands", []))
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


def run(
    profile_path: Path = DEFAULT_PROFILE,
    report_dir: Path = REPORT_DIR,
    project_root: Path = Path("."),
) -> Tuple[Dict[str, Any], Tuple[Path, Path, Path]]:
    profile = day33.load_profile(profile_path)
    report = build_report(profile, profile_path, project_root)
    paths = write_reports(report, report_dir)
    return report, paths


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"{DAY} {TITLE}")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Day34 staged apply plan profile path.")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR, help="Directory for Day34 JSON/HTML/TXT reports.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report, paths = run(args.profile, args.report_dir, Path("."))
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
    for stage in report["stages"]:
        print(f"- {stage['id']}: {stage['status']}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print(f"TXT report: {txt_path}")
    print("Safety gate: PLAN ONLY, NOT EXECUTED, no SSH connection is opened, and no RouterOS command is executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
