import argparse
import html
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


DAY14_NAME = "Unified Lab Runner and Report Index"
DEFAULT_PROFILE = Path("topology_profiles") / "day14_lab_runner_profile.json"
DAY4_BASELINE_SCRIPT = "mikrotik_day4_multi_device_baseline.py"
DAY4_BASELINE_DISPLAY_COMMAND = f"python {DAY4_BASELINE_SCRIPT}"
DAY8_PERFORMANCE_SCRIPT = "performance_test.py"
DAY8_PERFORMANCE_PROFILE = Path("topology_profiles") / "day8_iperf3_router_performance.json"
DAY17_REPORT_INDEX_HTML = Path("reports") / "report_index.html"
RESULTS = {"PASS", "FAIL", "WARN", "MISSING", "INCOMPLETE", "UNKNOWN", "SKIP", "NOT_RUN"}
INTERACTIVE_ACTION_COMPLETE = (
    "Action complete. Returning to menu. Choose another option or enter 0 to exit."
)
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_COLORS = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "gray": "\033[90m",
}
STATUS_COLORS = {
    "PASS": "green",
    "FAIL": "red",
    "WARN": "yellow",
    "MISSING": "gray",
    "INCOMPLETE": "yellow",
    "UNKNOWN": "magenta",
    "SKIP": "blue",
    "NOT_RUN": "blue",
}
LIVE_WORKFLOW_RECOMMENDATIONS = {
    "day4": {
        "title": "Day4 multi-device baseline",
        "command": "python mikrotik_day4_multi_device_baseline.py",
        "reminder": "This is a live SSH validation workflow. Review config first and run it manually.",
    },
    "day8": {
        "title": "Day8 iperf3 performance workflow",
        "command": "python performance_test.py --profile topology_profiles/day8_iperf3_router_performance.json",
        "reminder": "This workflow depends on lab reachability and iperf3 readiness. Run it manually with the correct direction/profile.",
    },
    "day12": {
        "title": "Day12 WireGuard validation",
        "command": "python mikrotik_day12_wireguard_vpn_automation.py --config Set_WireguardVPN_config.json --run-iperf",
        "reminder": "This may validate live WireGuard and iperf3 state. Confirm the client, LAN host, and secrets stay local before running.",
    },
    "day13": {
        "title": "Day13 multi-router WireGuard summary",
        "command": "Run the Day13 multi-router WireGuard summary workflow, then run: python network_lab.py --task report-index",
        "reminder": "Day13 live or summary generation is not executed by Day14 Phase 2. Use the Day13 workflow manually first.",
    },
}

SAFETY_LEVELS = {
    "SAFE_READ_ONLY": "Local report viewing, summary generation, dry-run, or existing report indexing.",
    "LIVE_READ_ONLY": "Live device checks that read state without changing configuration.",
    "LIVE_PERFORMANCE": "Live throughput tests that generate traffic but do not modify router configuration.",
    "LIVE_CONFIG_CHANGE": "Tasks that may change network configuration and require explicit confirmation.",
    "FUTURE_RESERVED": "Placeholder for intentionally disabled future runner integration.",
}

REPORT_CATALOG = [
    {
        "day": "Day2",
        "title": "Day2 Auto Setup",
        "json_globs": ["reports/**/day2*.json", "reports/**/*day2*auto*setup*.json"],
        "html_globs": ["reports/**/day2*.html", "reports/**/*day2*auto*setup*.html"],
    },
    {
        "day": "Day4",
        "title": "Day4 Baseline Validation",
        "json_globs": ["reports/**/day4_baseline_validation.json", "reports/**/*day4*baseline*.json"],
        "html_globs": ["reports/**/day4_baseline_validation.html", "reports/**/*day4*baseline*.html"],
    },
    {
        "day": "Day5",
        "title": "Day5 Cisco Switch Topology",
        "json_globs": ["reports/**/*day5*cisco*.json", "reports/**/*cisco*topology*.json"],
        "html_globs": ["reports/**/*day5*cisco*.html", "reports/**/*cisco*topology*.html"],
    },
    {
        "day": "Day6",
        "title": "Day6 Lab Topology Summary",
        "json_globs": ["reports/**/*day6*topology*.json", "summary/**/*day6*topology*.json"],
        "html_globs": ["reports/**/*day6*topology*.html", "summary/**/*day6*topology*.html"],
    },
    {
        "day": "Day8",
        "title": "Day8 iperf3 Performance",
        "json_globs": ["reports/**/day8_iperf3_*_report.json", "reports/**/*iperf3*performance*.json"],
        "html_globs": ["reports/**/day8_iperf3_*_report.html", "reports/**/*iperf3*performance*.html"],
    },
    {
        "day": "Day13",
        "title": "Day13 WireGuard Summary",
        "json_globs": ["summary/**/*day13*wireguard*.json", "reports/**/*day13*wireguard*.json"],
        "html_globs": ["summary/**/*day13*wireguard*.html", "reports/**/*day13*wireguard*.html"],
    },
    {
        "day": "Day14-Day16",
        "title": "Runner Overview Reports",
        "json_globs": ["reports/lab-summary/latest_lab_overview.json"],
        "html_globs": ["reports/lab-summary/latest_lab_overview.html", "reports/report_index.html"],
    },
]


def load_lab_runner_profile(profile_path: Path) -> Dict[str, Any]:
    path = Path(profile_path)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Profile was not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Profile is not valid JSON: {path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Profile must contain a JSON object.")
    if not isinstance(profile.get("overview_output"), dict):
        raise ValueError("Profile must define overview_output.")
    return profile


def iter_report_items(profile: Dict[str, Any]) -> Iterator[Tuple[str, Optional[Dict[str, Any]], Dict[str, Any]]]:
    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        for report in device.get("reports", []):
            if isinstance(report, dict):
                yield "device", device, report

    for report in profile.get("lab_summary_reports", []):
        if isinstance(report, dict):
            yield "lab_summary", None, report


def normalize_result(value: Any) -> str:
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if value is None:
        return "UNKNOWN"

    normalized = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "OK": "PASS",
        "SUCCESS": "PASS",
        "SUCCEEDED": "PASS",
        "PASSED": "PASS",
        "TRUE": "PASS",
        "ERROR": "FAIL",
        "FAILED": "FAIL",
        "FALSE": "FAIL",
        "WARNING": "WARN",
        "WARNINGS": "WARN",
        "PARTIAL": "WARN",
        "MISSING": "MISSING",
        "INCOMPLETE": "INCOMPLETE",
        "UNKNOWN": "UNKNOWN",
        "SKIPPED": "SKIP",
        "SKIP": "SKIP",
        "N_A": "SKIP",
        "NA": "SKIP",
        "NOT_RUN": "NOT_RUN",
        "NOTRUN": "NOT_RUN",
    }
    return aliases.get(normalized, normalized if normalized in RESULTS else "UNKNOWN")


def infer_report_result(json_data: Any) -> str:
    if not isinstance(json_data, dict):
        return "UNKNOWN"

    for key in ("overall_result", "result", "status", "passed", "validation_result"):
        if key in json_data:
            return normalize_result(json_data.get(key))

    for container_key in ("summary", "aggregate", "day13", "Day13 summary"):
        nested = json_data.get(container_key)
        if isinstance(nested, dict):
            for key in ("overall_result", "result", "status", "passed", "validation_result"):
                if key in nested:
                    return normalize_result(nested.get(key))

    return "UNKNOWN"


def check_report_file(report_item: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    root = Path(project_root)
    json_path = root / str(report_item.get("json", ""))
    html_path = root / str(report_item.get("html", ""))
    record = {
        "name": report_item.get("name", "Unnamed Report"),
        "json": str(report_item.get("json", "")),
        "html": str(report_item.get("html", "")),
        "required": bool(report_item.get("required", False)),
        "status": "MISSING",
        "exists": json_path.exists(),
        "html_exists": html_path.exists(),
        "message": "",
    }

    if not record["exists"]:
        record["message"] = "JSON report is missing."
        return record

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        record["status"] = "UNKNOWN"
        record["message"] = f"Invalid JSON: {exc.msg}"
        return record
    except OSError as exc:
        record["status"] = "UNKNOWN"
        record["message"] = f"Could not read JSON report: {exc}"
        return record

    record["status"] = infer_report_result(data)
    if record["status"] == "UNKNOWN":
        record["message"] = "Could not infer result from supported report fields."
    return record


def compute_overall_result(report_records: List[Dict[str, Any]]) -> str:
    if not report_records or not any(record.get("exists") for record in report_records):
        return "INCOMPLETE"

    statuses = [record.get("status", "UNKNOWN") for record in report_records]
    if "FAIL" in statuses:
        return "FAIL"
    if any(record.get("required") and record.get("status") == "MISSING" for record in report_records):
        return "INCOMPLETE"
    if any(status in {"MISSING", "UNKNOWN", "WARN", "SKIP", "NOT_RUN", "INCOMPLETE"} for status in statuses):
        return "WARN"
    return "PASS"


def _empty_counts() -> Dict[str, int]:
    return {
        "total": 0,
        "pass": 0,
        "fail": 0,
        "warn": 0,
        "missing": 0,
        "unknown": 0,
        "skip": 0,
        "not_run": 0,
    }


def _update_counts(counts: Dict[str, int], status: str) -> None:
    counts["total"] += 1
    key = status.lower()
    if key in counts:
        counts[key] += 1


def build_latest_lab_overview(profile: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    counts = _empty_counts()
    all_records: List[Dict[str, Any]] = []
    devices = []

    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        device_reports = []
        for report in device.get("reports", []):
            if not isinstance(report, dict):
                continue
            record = check_report_file(report, project_root)
            device_reports.append(record)
            all_records.append(record)
            _update_counts(counts, record["status"])
        devices.append(
            {
                "name": device.get("name", "Unnamed Device"),
                "type": device.get("type", "unknown"),
                "required": bool(device.get("required", False)),
                "reports": device_reports,
            }
        )

    lab_summary_reports = []
    for report in profile.get("lab_summary_reports", []):
        if not isinstance(report, dict):
            continue
        record = check_report_file(report, project_root)
        lab_summary_reports.append(record)
        all_records.append(record)
        _update_counts(counts, record["status"])

    return {
        "day": "Day14",
        "name": DAY14_NAME,
        "lab_name": profile.get("lab_name", "Network Automation Lab"),
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "overall_result": compute_overall_result(all_records),
        "counts": counts,
        "devices": devices,
        "lab_summary_reports": lab_summary_reports,
    }


def write_json_report(data: Dict[str, Any], output_path: Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def supports_color(stream: Any = sys.stdout) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return bool(getattr(stream, "isatty", lambda: False)())


def color_text(text: str, color: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
    if not supports_color():
        return text

    parts = []
    if bold:
        parts.append(ANSI_BOLD)
    if dim:
        parts.append(ANSI_DIM)
    if color:
        parts.append(ANSI_COLORS.get(color, ""))
    parts.append(text)
    parts.append(ANSI_RESET)
    return "".join(parts)


def format_status(status: str) -> str:
    normalized = normalize_result(status)
    return color_text(f"[{normalized}]", STATUS_COLORS.get(normalized), bold=True)


def format_heading(text: str) -> str:
    return color_text(text, "cyan", bold=True)


def build_relative_link(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(Path(to_path).resolve(), Path(from_path).resolve().parent)).as_posix()


def _status_badge(status: str) -> str:
    return f'<span class="badge badge-{html.escape(status.lower())}">{html.escape(status)}</span>'


def _html_report_link(output_path: Path, report: Dict[str, Any], project_root: Path) -> str:
    if not report.get("html_exists"):
        return "MISSING"
    href = build_relative_link(output_path, project_root / report.get("html", ""))
    return f'<a href="{html.escape(href)}">{html.escape(report.get("html", ""))}</a>'


def _render_device_rows(data: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    rows = []
    for device in data.get("devices", []):
        for report in device.get("reports", []):
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(device.get('name', '')))}</td>"
                f"<td>{html.escape(str(device.get('type', '')))}</td>"
                f"<td>{html.escape(str(report.get('name', '')))}</td>"
                f"<td>{'Yes' if report.get('required') else 'No'}</td>"
                f"<td>{_status_badge(str(report.get('status', 'UNKNOWN')))}</td>"
                f"<td>{html.escape(str(report.get('json', '')) if report.get('exists') else 'MISSING')}</td>"
                f"<td>{_html_report_link(output_path, report, project_root)}</td>"
                "</tr>"
            )
    return "\n".join(rows) or '<tr><td colspan="7">No device reports configured.</td></tr>'


def _render_summary_rows(data: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    rows = []
    for report in data.get("lab_summary_reports", []):
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(report.get('name', '')))}</td>"
            f"<td>{'Yes' if report.get('required') else 'No'}</td>"
            f"<td>{_status_badge(str(report.get('status', 'UNKNOWN')))}</td>"
            f"<td>{html.escape(str(report.get('json', '')) if report.get('exists') else 'MISSING')}</td>"
            f"<td>{_html_report_link(output_path, report, project_root)}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="5">No lab summary reports configured.</td></tr>'


def write_html_overview(data: Dict[str, Any], output_path: Path, project_root: Optional[Path] = None) -> None:
    path = Path(output_path)
    root = Path(project_root or Path.cwd())
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = data.get("counts", {})
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Latest Lab Overview</title>
  <style>
    :root {{ --bg: #f5f7fb; --ink: #172033; --muted: #617089; --line: #d8e0ec; --panel: #ffffff; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 34px 38px 24px; background: #233044; color: white; }}
    main {{ padding: 28px 38px 46px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .meta {{ color: #dbe5f3; }}
    .summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; }}
    .metric {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; min-width: 112px; }}
    .metric .label {{ color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric .value {{ margin-top: 5px; font-size: 22px; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    a {{ color: #155bb5; font-weight: 700; text-decoration: none; }}
    .badge {{ display: inline-block; min-width: 74px; padding: 4px 8px; border-radius: 999px; font-weight: 800; font-size: 12px; text-align: center; }}
    .badge-pass {{ background: #dff7e8; color: #136b35; }}
    .badge-fail {{ background: #ffe1e1; color: #9c1d1d; }}
    .badge-warn, .badge-skip, .badge-not_run {{ background: #fff3cc; color: #856100; }}
    .badge-missing, .badge-incomplete {{ background: #eceff5; color: #4d596b; }}
    .badge-unknown {{ background: #e5e7ff; color: #393a8a; }}
  </style>
</head>
<body>
  <header>
    <h1>Latest Lab Overview</h1>
    <div class="meta">{html.escape(str(data.get("lab_name", "")))} · Generated {html.escape(str(data.get("generated_at", "")))}</div>
    <p>Overall {_status_badge(str(data.get("overall_result", "UNKNOWN")))}</p>
  </header>
  <main>
    <section class="summary">
      <div class="metric"><div class="label">Total</div><div class="value">{counts.get("total", 0)}</div></div>
      <div class="metric"><div class="label">PASS</div><div class="value">{counts.get("pass", 0)}</div></div>
      <div class="metric"><div class="label">FAIL</div><div class="value">{counts.get("fail", 0)}</div></div>
      <div class="metric"><div class="label">WARN</div><div class="value">{counts.get("warn", 0)}</div></div>
      <div class="metric"><div class="label">MISSING</div><div class="value">{counts.get("missing", 0)}</div></div>
      <div class="metric"><div class="label">UNKNOWN</div><div class="value">{counts.get("unknown", 0)}</div></div>
    </section>

    <h2>Device Reports</h2>
    <table>
      <thead><tr><th>Device</th><th>Type</th><th>Report</th><th>Required</th><th>Status</th><th>JSON</th><th>HTML</th></tr></thead>
      <tbody>{_render_device_rows(data, path, root)}</tbody>
    </table>

    <h2>Lab Summary Reports</h2>
    <table>
      <thead><tr><th>Report</th><th>Required</th><th>Status</th><th>JSON</th><th>HTML</th></tr></thead>
      <tbody>{_render_summary_rows(data, path, root)}</tbody>
    </table>
  </main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def list_tasks() -> List[Dict[str, Any]]:
    return [
        {
            "id": "report-index",
            "task_id": "report_index",
            "display_name": "Report Index",
            "day": "Day14-Day17",
            "category": "reports",
            "description": "Read local reports and build lab overview or visibility indexes.",
            "safety_level": "SAFE_READ_ONLY",
            "execution_mode": "local_only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/lab-summary/latest_lab_overview.json",
                "reports/lab-summary/latest_lab_overview.html",
                "reports/report_index.html",
            ],
            "related_script": "network_lab.py",
            "notes": "Report indexing reads local report paths only and does not connect to devices or read config.json.",
        },
        {
            "id": "day4-baseline",
            "task_id": "day4_baseline_validation",
            "display_name": "Day4 Multi-device Baseline Validation",
            "day": "Day4",
            "category": "baseline",
            "description": "Existing Day4 multi-device RouterOS baseline validation.",
            "safety_level": "LIVE_READ_ONLY",
            "execution_mode": "subprocess_with_confirmation",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day4_baseline_validation.json",
                "reports/<device>/day4_baseline_validation.html",
            ],
            "related_script": DAY4_BASELINE_SCRIPT,
            "notes": "Uses the existing Day4 script. Interactive runner asks before live SSH validation.",
        },
        {
            "id": "iperf3-performance",
            "task_id": "day8_iperf3_performance",
            "display_name": "Day8 iperf3 Performance",
            "day": "Day8",
            "category": "performance",
            "description": "Existing Day8 iperf3 performance workflow.",
            "safety_level": "LIVE_PERFORMANCE",
            "execution_mode": "subprocess_with_confirmation",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day8_iperf3_performance_report.json",
                "reports/<device>/day8_iperf3_performance_report.html",
            ],
            "related_script": DAY8_PERFORMANCE_SCRIPT,
            "notes": "Generates iperf3 traffic but does not modify router configuration.",
        },
        {
            "id": "day12-wireguard-live-validation",
            "task_id": "day12_wireguard_live_validation",
            "display_name": "Day12 WireGuard Live Validation",
            "day": "Day12",
            "category": "vpn",
            "description": "WireGuard live validation placeholder.",
            "safety_level": "FUTURE_RESERVED",
            "execution_mode": "disabled_placeholder",
            "enabled": False,
            "status": "planned",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": ["reports/<device>/day12_wireguard_validation.json"],
            "related_script": "mikrotik_day12_wireguard_vpn_automation.py",
            "notes": "WireGuard live runner integration is intentionally disabled in Day17 and reserved for Day18.",
        },
        {
            "id": "day13-wireguard-summary",
            "task_id": "day13_wireguard_summary_only",
            "display_name": "Day13 WireGuard Summary Only",
            "day": "Day13",
            "category": "vpn",
            "description": "Report-only or placeholder visibility for Day13 WireGuard summaries.",
            "safety_level": "FUTURE_RESERVED",
            "execution_mode": "report_only_disabled_live",
            "enabled": False,
            "status": "planned",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.json",
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.html",
            ],
            "related_script": "mikrotik_day13_multi_router_wireguard_validation.py",
            "notes": "WireGuard live execution is intentionally excluded from Day17. Planned for Day18.",
        },
    ]


def _build_parser() -> argparse.ArgumentParser:
    examples = """examples:
  python network_lab.py
  python network_lab.py --interactive
  python network_lab.py --list-tasks
  python network_lab.py --report-index
  python network_lab.py --task report-index --dry-run
  python network_lab.py --task report-index
  python network_lab.py --task day4-baseline --dry-run
  python network_lab.py --task day4-baseline
  python network_lab.py --task iperf3-performance --dry-run
  python network_lab.py --task iperf3-performance
  python network_lab.py --task report-index --profile topology_profiles/day14_lab_runner_profile.json

report-index reads existing JSON reports and does not connect to devices.
day4-baseline delegates to the existing live SSH validation script.
iperf3-performance delegates to the existing live iperf3 performance script.
Day17 report-index visibility scans local report paths only and does not run WireGuard live execution."""
    parser = argparse.ArgumentParser(
        description=f"Day14 {DAY14_NAME}.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list-tasks", action="store_true", help="List available and planned lab tasks.")
    parser.add_argument("--report-index", action="store_true", help="Scan local reports and write reports/report_index.html.")
    parser.add_argument("--task", choices=["report-index", "day4-baseline", "iperf3-performance"], help="Task to run.")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Path to the Day14 lab runner profile JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Show report-index inputs and outputs without writing reports.")
    parser.add_argument("--interactive", action="store_true", help="Show the safe interactive Day14 menu.")
    return parser


def _resolve_project_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _print_task_list() -> None:
    print(format_heading("Task Catalog"))
    for task in list_tasks():
        print()
        print(f"[{task['task_id']}]")
        print(f"CLI task: {task['id']}")
        print(f"Day: {task['day']}")
        print(f"Display name: {task['display_name']}")
        print(f"Category: {task['category']}")
        print(f"Safety: {task['safety_level']}")
        print(f"Enabled: {'yes' if task['enabled'] else 'no'}")
        print(f"Execution mode: {task['execution_mode']}")
        print(f"Live device required: {'yes' if task['requires_live_device'] else 'no'}")
        print(f"Password required: {'yes' if task['requires_password'] else 'no'}")
        print(f"Related script: {task['related_script']}")
        print("Reports:")
        for report_path in task.get("report_paths", []):
            print(f"  - {report_path}")
        print(f"Notes: {task['notes']}")


def _relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _collect_report_paths(project_root: Path, patterns: List[str]) -> List[Path]:
    paths: List[Path] = []
    seen = set()
    for pattern in patterns:
        for path in sorted(project_root.glob(pattern)):
            if path.is_file() and path.name.lower() != "config.json":
                resolved = path.resolve()
                if resolved not in seen:
                    paths.append(path)
                    seen.add(resolved)
    return paths


def _report_device_label(path: Optional[Path], report_title: str) -> str:
    if path is None:
        return "Summary report" if "summary" in report_title.lower() else "Expected report"
    parent = path.parent.name
    if parent in {"reports", "summary", "lab-summary"}:
        return "Summary report"
    return parent


def discover_report_visibility(project_root: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for report_type in REPORT_CATALOG:
        json_paths = _collect_report_paths(project_root, report_type["json_globs"])
        html_paths = _collect_report_paths(project_root, report_type["html_globs"])
        if not json_paths and not html_paths:
            rows.append(
                {
                    "day": report_type["day"],
                    "title": report_type["title"],
                    "device": _report_device_label(None, report_type["title"]),
                    "status": "MISSING",
                    "json": "",
                    "html": "",
                    "notes": "Expected report was not found.",
                }
            )
            continue

        max_count = max(len(json_paths), len(html_paths))
        for index in range(max_count):
            json_path = json_paths[index] if index < len(json_paths) else None
            html_path = html_paths[index] if index < len(html_paths) else None
            label_path = json_path or html_path
            rows.append(
                {
                    "day": report_type["day"],
                    "title": report_type["title"],
                    "device": _report_device_label(label_path, report_type["title"]),
                    "status": "FOUND" if json_path or html_path else "MISSING",
                    "json": _relative_to_project(project_root, json_path) if json_path else "MISSING",
                    "html": _relative_to_project(project_root, html_path) if html_path else "MISSING",
                    "notes": "",
                }
            )

    rows.append(
        {
            "day": "Day13",
            "title": "Day13 WireGuard Live Execution",
            "device": "Runner guardrail",
            "status": "DISABLED FOR DAY17",
            "json": "",
            "html": "",
            "notes": "WireGuard live runner integration is intentionally disabled in Day17 and reserved for Day18.",
        }
    )
    return rows


def _print_report_visibility(rows: List[Dict[str, Any]]) -> None:
    print(format_heading("Report Index"))
    counts = _count_report_statuses(rows)
    status_width = max(22, max(len(str(row.get("status", ""))) + 2 for row in rows))
    print(
        "Summary: "
        f"found={color_text(str(counts['found']), 'green', bold=True)} "
        f"missing={color_text(str(counts['missing']), 'yellow', bold=True)} "
        f"disabled={color_text(str(counts['disabled']), 'blue', bold=True)}"
    )
    current_title = ""
    for row in rows:
        title = str(row["title"])
        if title != current_title:
            current_title = title
            print()
            print(format_heading(f"{title} ({row['day']})"))
            print(f"  {'Status':<{status_width}} {'Device':<24} Report paths")
            print(f"  {'-' * status_width} {'-' * 24} {'-' * 42}")
        status = _format_report_visibility_status(str(row["status"]))
        print(f"  {status:<{status_width}} {str(row['device'])[:24]:<24} JSON: {row.get('json') or '-'}")
        if row.get("html"):
            print(f"  {'':<{status_width}} {'':<24} HTML: {row['html']}")
        if row.get("notes"):
            print(f"  {'':<{status_width}} {'':<24} Notes: {row['notes']}")


def _count_report_statuses(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"found": 0, "missing": 0, "disabled": 0}
    for row in rows:
        status = str(row.get("status", "")).upper()
        if status == "FOUND":
            counts["found"] += 1
        elif status == "MISSING":
            counts["missing"] += 1
        elif "DISABLED" in status:
            counts["disabled"] += 1
    return counts


def _format_report_visibility_status(status: str) -> str:
    normalized = status.upper()
    if normalized == "FOUND":
        return color_text("[FOUND]", "green", bold=True)
    if normalized == "MISSING":
        return color_text("[MISSING]", "yellow", bold=True)
    if "DISABLED" in normalized:
        return color_text(f"[{normalized}]", "blue", bold=True)
    return color_text(f"[{normalized}]", "gray", bold=True)


def _html_link_or_text(output_path: Path, project_root: Path, value: str) -> str:
    if not value or value == "MISSING":
        return html.escape(value or "")
    target = project_root / value
    if target.suffix.lower() == ".html" and target.exists():
        href = build_relative_link(output_path, target)
        return f'<a href="{html.escape(href)}">{html.escape(value)}</a>'
    return html.escape(value)


def _css_token(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def write_report_index_html(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
    output_path: Path,
    project_root: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().replace(microsecond=0).isoformat(sep=" ")
    counts = _count_report_statuses(report_rows)
    task_rows = "\n".join(
        "<tr>"
        f"<td><code>{html.escape(str(task['task_id']))}</code></td>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(task['day']))}</span></td>"
        f"<td>{html.escape(str(task['display_name']))}</td>"
        f"<td>{html.escape(str(task['category']))}</td>"
        f"<td><span class=\"pill safety-{_css_token(str(task['safety_level']))}\">{html.escape(str(task['safety_level']))}</span></td>"
        f"<td><span class=\"pill {'enabled' if task['enabled'] else 'disabled'}\">{'yes' if task['enabled'] else 'no'}</span></td>"
        f"<td>{html.escape(str(task['execution_mode']))}</td>"
        f"<td>{'yes' if task['requires_live_device'] else 'no'}</td>"
        "</tr>"
        for task in task_catalog
    )
    report_table_rows = "\n".join(
        "<tr>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(row['day']))}</span></td>"
        f"<td>{html.escape(str(row['title']))}</td>"
        f"<td>{html.escape(str(row['device']))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(row['status']))}\">{html.escape(str(row['status']))}</span></td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('json', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('html', '')))}</td>"
        f"<td>{html.escape(str(row.get('notes', '')))}</td>"
        "</tr>"
        for row in report_rows
    )
    safety_rows = "\n".join(
        f"<tr><td><span class=\"pill safety-{_css_token(level)}\">{html.escape(level)}</span></td><td>{html.escape(description)}</td></tr>"
        for level, description in SAFETY_LEVELS.items()
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Network Automation Lab Report Index</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #27364a;
      --blue: #155bb5;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
      --red-bg: #fdecec;
      --red: #b42318;
      --blue-bg: #e6f0ff;
      --blue-ink: #1849a9;
      --gray-bg: #eef2f6;
      --gray: #475467;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); box-shadow: 0 10px 24px rgba(16, 24, 40, .06); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    tr:nth-child(even) td {{ background: #fafcff; }}
    code {{ font-family: Consolas, "Courier New", monospace; overflow-wrap: anywhere; }}
    a {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .meta {{ color: #dbe5f3; }}
    .warning {{ background: var(--yellow-bg); border: 1px solid #f0c66a; border-radius: 8px; padding: 12px 14px; margin: 18px 0 20px; color: var(--yellow); }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .pill-day {{ background: var(--gray-bg); color: var(--gray); }}
    .enabled, .status-found {{ background: var(--green-bg); color: var(--green); }}
    .disabled, .status-disabled-for-day17, .safety-future-reserved {{ background: var(--blue-bg); color: var(--blue-ink); }}
    .status-missing {{ background: var(--yellow-bg); color: var(--yellow); }}
    .safety-safe-read-only {{ background: var(--green-bg); color: var(--green); }}
    .safety-live-read-only {{ background: #e7f0fb; color: #175cd3; }}
    .safety-live-performance {{ background: #f3e8ff; color: #6941c6; }}
    .safety-live-config-change {{ background: var(--red-bg); color: var(--red); }}
    @media (max-width: 820px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Network Automation Lab Report Index</h1>
    <div class="meta">Generated {html.escape(generated_at)}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Tasks</div><div class="metric-value">{len(task_catalog)}</div></div>
      <div class="metric"><div class="metric-label">Reports Found</div><div class="metric-value">{counts['found']}</div></div>
      <div class="metric"><div class="metric-label">Missing</div><div class="metric-value">{counts['missing']}</div></div>
      <div class="metric"><div class="metric-label">Disabled</div><div class="metric-value">{counts['disabled']}</div></div>
    </section>
  </header>
  <main>
    <div class="warning">WireGuard live execution is not enabled in Day17. WireGuard live runner integration is intentionally disabled and reserved for Day18.</div>
    <h2>Task Catalog Summary</h2>
    <table>
      <thead><tr><th>Task ID</th><th>Day</th><th>Name</th><th>Category</th><th>Safety</th><th>Enabled</th><th>Mode</th><th>Live Device</th></tr></thead>
      <tbody>{task_rows}</tbody>
    </table>
    <h2>Report Visibility</h2>
    <table>
      <thead><tr><th>Day</th><th>Report</th><th>Device</th><th>Status</th><th>JSON</th><th>HTML</th><th>Notes</th></tr></thead>
      <tbody>{report_table_rows}</tbody>
    </table>
    <h2>Safety Level Legend</h2>
    <table>
      <thead><tr><th>Safety Level</th><th>Description</th></tr></thead>
      <tbody>{safety_rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def _run_report_visibility_index(project_root: Path) -> int:
    rows = discover_report_visibility(project_root)
    _print_report_visibility(rows)
    output_path = project_root / DAY17_REPORT_INDEX_HTML
    write_report_index_html(list_tasks(), rows, output_path, project_root)
    print()
    print(f"{format_status('PASS')} HTML report index: {_relative_to_project(project_root, output_path)}")
    print("WireGuard live runner integration is intentionally disabled in Day17 and reserved for Day18.")
    return 0


def _print_dry_run(profile: Dict[str, Any], profile_path: Path) -> None:
    output = profile["overview_output"]
    print(format_heading(f"Day14 {DAY14_NAME}"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Profile path: {color_text(str(profile_path), 'gray')}")
    print()
    print(format_heading("Overview output paths"))
    print(f"  JSON overview : {output.get('json')}")
    print(f"  HTML overview : {output.get('html')}")
    print()
    print(format_heading("Report files that would be checked"))
    for _section, device, report in iter_report_items(profile):
        label = f"{device.get('name')} / {report.get('name')}" if device else str(report.get("name"))
        required = "required" if report.get("required") else "optional"
        print(
            f"  {format_status('NOT_RUN')} "
            f"{color_text(label, 'cyan')} "
            f"{color_text('[' + required + ']', 'yellow' if report.get('required') else 'gray')} "
            f"-> {report.get('json')}"
        )
    print()
    print(f"{format_status('PASS')} No reports were written")


def _format_required_label(required: bool) -> str:
    label = "required" if required else "optional"
    return color_text(f"[{label}]", "yellow" if required else "gray")


def _print_report_record(label: str, record: Dict[str, Any]) -> None:
    message = f" - {record.get('message')}" if record.get("message") else ""
    print(
        f"  {format_status(str(record.get('status', 'UNKNOWN')))} "
        f"{color_text(label, 'cyan')} "
        f"{_format_required_label(bool(record.get('required')))} "
        f"-> {record.get('json')}{message}"
    )


def _print_report_records(overview: Dict[str, Any]) -> None:
    print()
    print(format_heading("Device report results"))
    for device in overview.get("devices", []):
        device_label = f"{device.get('name')} / {device.get('type')}"
        print(f"  {color_text(str(device_label), 'gray', bold=True)}")
        reports = device.get("reports", [])
        if not reports:
            print(f"    {format_status('UNKNOWN')} No reports configured")
            continue
        for report in reports:
            _print_report_record(f"{device.get('name')} / {report.get('name')}", report)

    print()
    print(format_heading("Lab summary report results"))
    lab_summary_reports = overview.get("lab_summary_reports", [])
    if not lab_summary_reports:
        print(f"  {format_status('UNKNOWN')} No lab summary reports configured")
        return
    for report in lab_summary_reports:
        _print_report_record(str(report.get("name")), report)


def _print_run_summary(overview: Dict[str, Any], profile: Dict[str, Any]) -> None:
    counts = overview.get("counts", {})
    print(format_heading(f"Day14 {DAY14_NAME}"))
    print(f"Overall result: {format_status(str(overview.get('overall_result', 'UNKNOWN')))}")
    print(
        "Counts: "
        f"total={counts.get('total', 0)} "
        f"pass={color_text(str(counts.get('pass', 0)), 'green')} "
        f"fail={color_text(str(counts.get('fail', 0)), 'red')} "
        f"warn={color_text(str(counts.get('warn', 0)), 'yellow')} "
        f"missing={color_text(str(counts.get('missing', 0)), 'gray')} "
        f"unknown={color_text(str(counts.get('unknown', 0)), 'magenta')}"
    )
    _print_report_records(overview)
    print()
    print(f"JSON overview: {profile['overview_output']['json']}")
    print(f"HTML overview: {profile['overview_output']['html']}")


def _run_report_index(
    profile: Dict[str, Any],
    project_root: Path,
    profile_path: Path,
    dry_run: bool = False,
) -> int:
    if dry_run:
        _print_dry_run(profile, profile_path)
        return 0

    overview = build_latest_lab_overview(profile, project_root)
    json_output = _resolve_project_path(project_root, profile["overview_output"]["json"])
    html_output = _resolve_project_path(project_root, profile["overview_output"]["html"])
    write_json_report(overview, json_output)
    write_html_overview(overview, html_output, project_root)
    _print_run_summary(overview, profile)
    return 0 if overview["overall_result"] in {"PASS", "WARN"} else 1


def _build_day4_baseline_command() -> List[str]:
    return [sys.executable, DAY4_BASELINE_SCRIPT]


def _print_day4_baseline_dry_run() -> None:
    print(format_heading("Day4 multi-device baseline"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Command that would be executed: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    print()
    print(format_heading("Safety notes"))
    print("  This is a live SSH validation workflow.")
    print("  Dry-run does not connect to devices.")
    print(f"  Dry-run does not execute {DAY4_BASELINE_SCRIPT}.")
    print("  Dry-run does not write reports.")
    print()
    print(f"{format_status('PASS')} No live workflow was executed.")


def _print_day4_baseline_follow_up() -> None:
    print()
    print("Day4 baseline finished. To refresh the lab overview, run:")
    print("python network_lab.py --task report-index")


def _run_day4_baseline(project_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        _print_day4_baseline_dry_run()
        return 0

    print(format_heading("Day4 multi-device baseline"))
    print("Live SSH validation workflow.")
    print(f"Executing command: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    result = subprocess.run(_build_day4_baseline_command(), cwd=project_root)
    _print_day4_baseline_follow_up()
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day4 baseline completed successfully.")
        return 0

    print(f"{format_status('FAIL')} Day4 baseline failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_day4_baseline(project_root: Path, input_func: Any) -> int:
    print(format_heading("Day4 multi-device baseline"))
    print("This is a live SSH validation workflow.")
    print(f"Command to execute: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    try:
        confirmation = input_func("Confirm live Day4 baseline run? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation not in {"y", "yes"}:
        print(f"{format_status('NOT_RUN')} Day4 baseline cancelled. No live workflow was executed.")
        return 0

    return _run_day4_baseline(project_root, dry_run=False)


def _load_day8_performance_profile(project_root: Path) -> Dict[str, Any]:
    profile_path = project_root / DAY8_PERFORMANCE_PROFILE
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Day8 performance profile was not found: {profile_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Day8 performance profile is not valid JSON: {profile_path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Day8 performance profile must contain a JSON object.")
    return profile


def _required_day8_profile_value(profile: Dict[str, Any], key: str) -> str:
    value = profile.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Day8 performance profile must define {key}.")
    return str(value)


def _build_day8_performance_command(project_root: Path, executable: str = sys.executable) -> List[str]:
    profile = _load_day8_performance_profile(project_root)
    return [
        executable,
        DAY8_PERFORMANCE_SCRIPT,
        "--lan-server-ip",
        _required_day8_profile_value(profile, "default_lan_server_ip"),
        "--duration",
        _required_day8_profile_value(profile, "default_duration_sec"),
        "--omit",
        _required_day8_profile_value(profile, "default_omit_sec"),
        "--parallel",
        _required_day8_profile_value(profile, "default_parallel_streams"),
        "--threshold-mbps",
        _required_day8_profile_value(profile, "default_threshold_mbps"),
        "--warn-threshold-mbps",
        _required_day8_profile_value(profile, "default_warn_threshold_mbps"),
    ]


def _format_display_command(command: List[str]) -> str:
    display_parts = ["python" if index == 0 and part == sys.executable else part for index, part in enumerate(command)]
    return " ".join(display_parts)


def _print_day8_performance_dry_run(project_root: Path) -> int:
    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Command that would be executed: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    print()
    print(format_heading("Safety notes"))
    print("  This is a live iperf3 performance workflow.")
    print("  Dry-run does not connect to devices.")
    print("  Dry-run does not require real iperf3.")
    print(f"  Dry-run does not execute {DAY8_PERFORMANCE_SCRIPT}.")
    print("  Dry-run does not write reports.")
    print()
    print(f"{format_status('PASS')} No live workflow was executed.")
    return 0


def _run_day8_performance(project_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        return _print_day8_performance_dry_run(project_root)

    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print("Live iperf3 performance workflow.")
    print(f"Executing command: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day8 iperf3 performance completed successfully.")
        return 0

    print(f"{format_status('FAIL')} Day8 iperf3 performance failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_day8_performance(project_root: Path, input_func: Any) -> int:
    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print("This is a live iperf3 performance workflow.")
    print(f"Command to execute: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    try:
        confirmation = input_func("Confirm live Day8 iperf3 performance run? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation != "y":
        print(f"{format_status('NOT_RUN')} Day8 iperf3 performance cancelled. No live workflow was executed.")
        return 0

    return _run_day8_performance(project_root, dry_run=False)


def _print_recommended_live_command(workflow_id: str) -> None:
    recommendation = LIVE_WORKFLOW_RECOMMENDATIONS[workflow_id]
    print(format_heading(recommendation["title"]))
    print(f"Recommended command: {color_text(recommendation['command'], 'cyan', bold=True)}")
    print(f"Safety reminder: {color_text(recommendation['reminder'], 'yellow')}")
    print(f"{format_status('NOT_RUN')} Day14 Phase 2 printed guidance only; no live workflow was executed.")


def _open_latest_overview_html(profile: Dict[str, Any], project_root: Path) -> bool:
    html_output = _resolve_project_path(project_root, profile["overview_output"]["html"])
    if not html_output.exists():
        print(f"{format_status('MISSING')} Latest overview HTML was not found: {html_output}")
        print("Run report-index first to generate it.")
        return False

    print(f"{format_status('PASS')} Opening latest overview HTML: {html_output}")
    try:
        if hasattr(os, "startfile"):
            os.startfile(str(html_output))  # type: ignore[attr-defined]
        else:
            webbrowser.open(html_output.resolve().as_uri())
    except OSError as exc:
        print(f"{format_status('UNKNOWN')} Could not open HTML file: {exc}")
        return False
    return True


def _print_interactive_menu() -> None:
    print()
    print(format_heading(f"Day14 {DAY14_NAME}"))
    print("Select an option by number:")
    print("  1. List available tasks")
    print("  2. Generate latest report index")
    print("  3. Dry-run report index")
    print("  4. Open latest overview HTML if it exists")
    print("  5. Run Day4 multi-device baseline")
    print("  6. Run Day8 iperf3 performance workflow")
    print("  7. Show recommended command for Day12 WireGuard validation")
    print("  8. Show recommended command for Day13 multi-router WireGuard summary")
    print("  0. Exit")


def _print_interactive_action_complete() -> None:
    print()
    print(color_text(INTERACTIVE_ACTION_COMPLETE, "green", bold=True))


def run_interactive_menu(
    profile: Dict[str, Any],
    project_root: Path,
    profile_path: Path,
    input_func: Optional[Any] = None,
) -> int:
    read_input = input_func or input
    while True:
        _print_interactive_menu()
        try:
            choice = read_input("Choice: ").strip().lower()
        except EOFError:
            print()
            print("Input closed. Exiting.")
            return 0

        if choice in {"0", "q", "quit", "exit"}:
            print("Exiting Day14 interactive menu.")
            return 0
        if choice == "1":
            _print_task_list()
            _print_interactive_action_complete()
        elif choice == "2":
            _run_report_index(profile, project_root, profile_path, dry_run=False)
            _print_interactive_action_complete()
        elif choice == "3":
            _run_report_index(profile, project_root, profile_path, dry_run=True)
            _print_interactive_action_complete()
        elif choice == "4":
            _open_latest_overview_html(profile, project_root)
            _print_interactive_action_complete()
        elif choice == "5":
            day4_exit_code = _confirm_and_run_day4_baseline(project_root, read_input)
            _print_interactive_action_complete()
            if day4_exit_code != 0:
                return day4_exit_code
        elif choice == "6":
            day8_exit_code = _confirm_and_run_day8_performance(project_root, read_input)
            _print_interactive_action_complete()
            if day8_exit_code != 0:
                return day8_exit_code
        elif choice == "7":
            _print_recommended_live_command("day12")
            _print_interactive_action_complete()
        elif choice == "8":
            _print_recommended_live_command("day13")
            _print_interactive_action_complete()
        else:
            print(f"{format_status('UNKNOWN')} Invalid menu choice: {choice or '<empty>'}")
            print("Please enter a number from 0 to 8.")


def main(argv: Optional[List[str]] = None, project_root: Optional[Path] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(project_root or Path.cwd()).resolve()

    if args.list_tasks:
        _print_task_list()
        return 0
    if args.report_index:
        return _run_report_visibility_index(root)

    profile_path = _resolve_project_path(root, args.profile)
    try:
        profile = load_lab_runner_profile(profile_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.interactive or not args.task:
        return run_interactive_menu(profile, root, profile_path)

    if args.task == "report-index":
        return _run_report_index(profile, root, profile_path, dry_run=args.dry_run)
    if args.task == "day4-baseline":
        return _run_day4_baseline(root, dry_run=args.dry_run)
    if args.task == "iperf3-performance":
        return _run_day8_performance(root, dry_run=args.dry_run)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
