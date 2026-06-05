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
DAY12_WIREGUARD_SCRIPT = "mikrotik_day12_wireguard_vpn_automation.py"
DAY12_WIREGUARD_CONFIG = "Set_WireguardVPN_config.json"
DAY12_WIREGUARD_TIMEOUT_SECONDS = 900
DAY32_VRRP_PRECHECK_SCRIPT = "mikrotik_day32_vrrp_readonly_precheck.py"
DAY32_VRRP_PRECHECK_TASK_ID = "day32-vrrp-precheck"
DAY32_VRRP_PRECHECK_JSON = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.json"
DAY32_VRRP_PRECHECK_HTML = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.html"
DAY32_VRRP_PRECHECK_TXT = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.txt"
DAY33_VRRP_DRY_RUN_SCRIPT = "mikrotik_day33_vrrp_topology_dry_run.py"
DAY33_VRRP_DRY_RUN_TASK_ID = "day33-vrrp-dry-run"
DAY33_VRRP_DRY_RUN_JSON = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.json"
DAY33_VRRP_DRY_RUN_HTML = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.html"
DAY33_VRRP_DRY_RUN_TXT = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.txt"
DAY34_VRRP_STAGED_PLAN_SCRIPT = "mikrotik_day34_vrrp_staged_apply_plan.py"
DAY34_VRRP_STAGED_PLAN_TASK_ID = "day34-vrrp-staged-plan"
DAY34_VRRP_STAGED_PLAN_JSON = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.json"
DAY34_VRRP_STAGED_PLAN_HTML = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.html"
DAY34_VRRP_STAGED_PLAN_TXT = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.txt"
DAY35_VRRP_FAILOVER_SCRIPT = "mikrotik_day35_vrrp_failover_validation.py"
DAY35_VRRP_FAILOVER_TASK_ID = "day35-vrrp-failover-validation"
DAY35_VRRP_FAILOVER_JSON = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.json"
DAY35_VRRP_FAILOVER_HTML = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.html"
DAY35_VRRP_FAILOVER_TXT = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.txt"
WIREGUARD_RUNNER_TASK_ALIAS = "wireguard-runner"
WIREGUARD_RUNNER_TASK_ID = "wireguard_runner_safety_layer"
WIREGUARD_RUNNER_DISPLAY_NAME = "WireGuard Runner Safety Layer"
WIREGUARD_RUNNER_REPORT_JSON = Path("reports") / "lab-summary" / "wireguard_runner_safety_layer.json"
WIREGUARD_RUNNER_REPORT_HTML = Path("reports") / "lab-summary" / "wireguard_runner_safety_layer.html"
DAY12_WIREGUARD_REPORT_JSON_NAME = "day12_wireguard_vpn_automation_report.json"
DAY12_WIREGUARD_REPORT_HTML_NAME = "day12_wireguard_vpn_automation_report.html"
SECRET_FIELD_MARKERS = ("secret", "password", "private_key", "preshared_key", "token", "key")
DAY17_REPORT_INDEX_HTML = Path("reports") / "report_index.html"
DAY19_EVIDENCE_INDEX_JSON = Path("reports") / "portfolio" / "day19_runner_evidence_index.json"
DAY19_EVIDENCE_INDEX_HTML = Path("reports") / "portfolio" / "day19_runner_evidence_index.html"
DAY24_DEMO_FLOW_JSON = Path("reports") / "portfolio" / "day24_rc_demo_flow.json"
DAY24_DEMO_FLOW_HTML = Path("reports") / "portfolio" / "day24_rc_demo_flow.html"
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
    "wireguard_runner": {
        "title": WIREGUARD_RUNNER_DISPLAY_NAME,
        "command": "python network_lab.py --task wireguard-runner --dry-run",
        "reminder": "This may validate live WireGuard and iperf3 state. Confirm the client, LAN host, and secrets stay local before running.",
    },
    "day13": {
        "title": "Day13 multi-router WireGuard summary",
        "command": "Run the Day13 multi-router WireGuard summary workflow, then run: python network_lab.py --task report-index",
        "reminder": "Day13 live or summary generation is not executed by Day14 Phase 2. Use the Day13 workflow manually first.",
    },
}

SAFETY_LEVELS = {
    "report-only": "Local report viewing, summary generation, dry-run output, or existing report indexing.",
    "read-only": "Live device checks that read state without changing configuration.",
    "guarded-live": "Live validation delegated only after explicit runner action, confirmation, or guard flag.",
    "controlled_failover_observation": "Live read-only HA observation where the failure trigger is manual and external.",
    "dry-run": "Planned-action preview that does not connect to devices or start live checks.",
    "disabled": "Placeholder or blocked workflow that is intentionally not available from the runner.",
}

REPORT_CATALOG = [
    {
        "day": "Day2",
        "title": "Day2 Auto Setup",
        "report_type": "Automation validation report",
        "safety_label": "live config evidence",
        "description": "Evidence from MikroTik setup automation; report index only reads generated JSON/HTML.",
        "json_globs": ["reports/**/day2*.json", "reports/**/*day2*auto*setup*.json"],
        "html_globs": ["reports/**/day2*.html", "reports/**/*day2*auto*setup*.html"],
    },
    {
        "day": "Day4",
        "title": "Day4 Baseline Validation",
        "report_type": "Multi-device baseline report",
        "safety_label": "live read-only evidence",
        "description": "RouterOS baseline checks gathered from existing reports; report index does not connect to devices.",
        "json_globs": ["reports/**/day4_baseline_validation.json", "reports/**/*day4*baseline*.json"],
        "html_globs": ["reports/**/day4_baseline_validation.html", "reports/**/*day4*baseline*.html"],
    },
    {
        "day": "Day5",
        "title": "Day5 Cisco Switch Topology",
        "report_type": "Topology validation report",
        "safety_label": "read-only evidence",
        "description": "Cisco switch topology validation evidence when local reports are available.",
        "json_globs": ["reports/**/*day5*cisco*.json", "reports/**/*cisco*topology*.json"],
        "html_globs": ["reports/**/*day5*cisco*.html", "reports/**/*cisco*topology*.html"],
        "missing_note": "Expected Cisco switch report was not found in local reports folder.",
    },
    {
        "day": "Day6",
        "title": "Day6 Lab Topology Summary",
        "report_type": "Lab topology summary",
        "safety_label": "report-only evidence",
        "description": "Local topology summary evidence for portfolio review.",
        "json_globs": ["reports/**/*day6*topology*.json", "summary/**/*day6*topology*.json"],
        "html_globs": ["reports/**/*day6*topology*.html", "summary/**/*day6*topology*.html"],
    },
    {
        "day": "Day8",
        "title": "Day8 iperf3 Performance",
        "report_type": "Day8 performance report",
        "safety_label": "guarded-live performance evidence",
        "description": "Day8 iperf3 throughput evidence; report visibility reads existing files and does not generate traffic.",
        "json_globs": ["reports/**/day8_iperf3_*_report.json", "reports/**/*iperf3*performance*.json"],
        "html_globs": ["reports/**/day8_iperf3_*_report.html", "reports/**/*iperf3*performance*.html"],
    },
    {
        "day": "Day12",
        "title": "Day12 WireGuard Validation",
        "report_type": "Day12 WireGuard report / documentation relationship",
        "safety_label": "guarded-live evidence",
        "description": "Detailed WireGuard client-to-site validation evidence; Day18 links to these reports when guarded delegation runs.",
        "json_globs": ["reports/**/day12_wireguard_vpn_automation_report.json"],
        "html_globs": ["reports/**/day12_wireguard_vpn_automation_report.html"],
    },
    {
        "day": "Day13",
        "title": "Day13 WireGuard Summary",
        "report_type": "Day13 multi-router WireGuard validation report",
        "safety_label": "report-only evidence",
        "description": "Multi-router WireGuard validation summary evidence; Day12 remains the detailed source of truth for per-router live validation.",
        "json_globs": ["summary/**/*day13*wireguard*.json", "reports/**/*day13*wireguard*.json"],
        "html_globs": ["summary/**/*day13*wireguard*.html", "reports/**/*day13*wireguard*.html"],
    },
    {
        "day": "Day18",
        "title": WIREGUARD_RUNNER_DISPLAY_NAME,
        "report_type": "Day18 WireGuard runner result",
        "safety_label": "guarded-live / dry-run default",
        "description": "Safety-layer result for delegated Day12 WireGuard validation; unsafe Day12 write flags are not delegated.",
        "json_globs": [WIREGUARD_RUNNER_REPORT_JSON.as_posix()],
        "html_globs": [WIREGUARD_RUNNER_REPORT_HTML.as_posix()],
        "missing_note": f"Expected report path: {WIREGUARD_RUNNER_REPORT_JSON.as_posix()}",
    },
    {
        "day": "Day14-Day16",
        "title": "Runner Overview Reports",
        "report_type": "Day21 report viewer / evidence viewer relationship",
        "safety_label": "local report index",
        "description": "Unified runner overview and report index generated from local files for the dashboard /reports evidence viewer.",
        "json_globs": ["reports/lab-summary/latest_lab_overview.json"],
        "html_globs": ["reports/lab-summary/latest_lab_overview.html", "reports/report_index.html"],
    },
    {
        "day": "Day24",
        "title": "Day24 RC Demo Flow",
        "report_type": "RC demo walkthrough",
        "safety_label": "report-only demo guidance",
        "description": "Local reviewer walkthrough for RC demo and portfolio presentation; generated without live execution.",
        "json_globs": [DAY24_DEMO_FLOW_JSON.as_posix()],
        "html_globs": [DAY24_DEMO_FLOW_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task demo-flow",
    },
    {
        "day": "Day32",
        "title": "VRRP Read-only Precheck Runner",
        "report_type": "HA / VRRP read-only precheck report",
        "safety_label": "read-only evidence",
        "description": "MikroTik HA/VRRP readiness evidence gathered with read-only print/export terse commands only.",
        "json_globs": [DAY32_VRRP_PRECHECK_JSON.as_posix()],
        "html_globs": [DAY32_VRRP_PRECHECK_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY32_VRRP_PRECHECK_TASK_ID}",
    },
    {
        "day": "Day33",
        "title": "VRRP Topology Design + Dry-run Command Preview",
        "report_type": "HA / VRRP dry-run topology design report",
        "safety_label": "dry-run preview",
        "description": "MikroTik HA/VRRP v0.2 topology design and command preview generated from local dry-run profile data only.",
        "json_globs": [DAY33_VRRP_DRY_RUN_JSON.as_posix()],
        "html_globs": [DAY33_VRRP_DRY_RUN_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY33_VRRP_DRY_RUN_TASK_ID}",
    },
    {
        "day": "Day34",
        "title": "VRRP Staged Apply Plan and Safety Gate",
        "report_type": "HA / VRRP staged apply plan report",
        "safety_label": "blocked plan-only safety gate",
        "description": "MikroTik HA/VRRP staged apply plan that checks Day32/Day33 evidence and blocks live execution.",
        "json_globs": [DAY34_VRRP_STAGED_PLAN_JSON.as_posix()],
        "html_globs": [DAY34_VRRP_STAGED_PLAN_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY34_VRRP_STAGED_PLAN_TASK_ID}",
    },
    {
        "day": "Day35",
        "title": "VRRP Failover Validation",
        "report_type": "HA / VRRP controlled failover validation report",
        "safety_label": "controlled_failover_observation",
        "description": "MikroTik HA/VRRP failover evidence gathered after a manual external lab01 LAN disconnect/reconnect; automation only observes and reports.",
        "json_globs": [DAY35_VRRP_FAILOVER_JSON.as_posix()],
        "html_globs": [DAY35_VRRP_FAILOVER_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY35_VRRP_FAILOVER_TASK_ID}",
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

    for key in ("overall_result", "overall_status", "result", "status", "passed", "validation_result"):
        if key in json_data:
            return normalize_result(json_data.get(key))

    for container_key in ("summary", "aggregate", "day13", "Day13 summary"):
        nested = json_data.get(container_key)
        if isinstance(nested, dict):
            for key in ("overall_result", "overall_status", "result", "status", "passed", "validation_result"):
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
    path.write_text(json.dumps(mask_secret_values(data), indent=2), encoding="utf-8")


def mask_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        masked = {}
        for key, item in value.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in SECRET_FIELD_MARKERS):
                masked[key] = "[REDACTED]"
            else:
                masked[key] = mask_secret_values(item)
        return masked
    if isinstance(value, list):
        return [mask_secret_values(item) for item in value]
    return value


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
            "user_display_name": "Report Index",
            "day": "Day14-Day19",
            "category": "reports",
            "description": "Read local reports and build lab overview or visibility indexes.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/lab-summary/latest_lab_overview.json",
                "reports/lab-summary/latest_lab_overview.html",
                "reports/report_index.html",
                DAY19_EVIDENCE_INDEX_JSON.as_posix(),
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day14 latest lab overview JSON/HTML",
                "Day17-Day21 report viewer visibility index",
                "Day19 portfolio evidence index JSON/HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Reads local report paths only and does not connect to devices or read config.json.",
        },
        {
            "id": "portfolio-finalize",
            "task_id": "day19_runner_evidence_index",
            "display_name": "Day19 Runner Evidence Index",
            "user_display_name": "Portfolio Evidence Index",
            "day": "Day19",
            "category": "portfolio",
            "description": "Build a portfolio-ready evidence index from the task catalog and local report visibility.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY19_EVIDENCE_INDEX_JSON.as_posix(),
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day19 runner evidence index JSON",
                "Day19 runner evidence index HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Day19 finalization reads local report metadata only; generated output is safe for screenshots and portfolio review.",
        },
        {
            "id": "demo-flow",
            "task_id": "day24_rc_demo_flow",
            "display_name": "Day24 RC Demo Flow",
            "user_display_name": "RC Demo Flow",
            "day": "Day24",
            "category": "portfolio",
            "description": "Build a reviewer-friendly RC demo flow and portfolio walkthrough from local task/report metadata.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY24_DEMO_FLOW_JSON.as_posix(),
                DAY24_DEMO_FLOW_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day24 RC demo flow JSON",
                "Day24 RC demo flow HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Day24 demo flow reads task/report metadata only and gives reviewers a safe click-through order for RC walkthroughs.",
        },
        {
            "id": "day4-baseline",
            "task_id": "day4_baseline_validation",
            "display_name": "Day4 Multi-device Baseline Validation",
            "user_display_name": "Multi-device Baseline Validation",
            "day": "Day4",
            "category": "baseline",
            "description": "Existing Day4 multi-device RouterOS baseline validation.",
            "safety_level": "read-only",
            "execution_mode": "guarded-live",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day4_baseline_validation.json",
                "reports/<device>/day4_baseline_validation.html",
            ],
            "report_outputs": [
                "Day4 per-device baseline validation JSON/HTML",
            ],
            "related_script": DAY4_BASELINE_SCRIPT,
            "notes": "Read-only live SSH validation. Uses the existing Day4 script; interactive runner asks before delegation.",
        },
        {
            "id": "iperf3-performance",
            "task_id": "day8_iperf3_performance",
            "display_name": "Day8 iperf3 Performance",
            "user_display_name": "iperf3 Performance Test",
            "day": "Day8",
            "category": "performance",
            "description": "Existing Day8 iperf3 performance workflow.",
            "safety_level": "guarded-live",
            "execution_mode": "guarded-live",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day8_iperf3_performance_report.json",
                "reports/<device>/day8_iperf3_performance_report.html",
            ],
            "report_outputs": [
                "Day8 iperf3 performance report JSON/HTML",
            ],
            "related_script": DAY8_PERFORMANCE_SCRIPT,
            "notes": "Guarded-live performance task. Generates iperf3 traffic only after confirmation and does not modify router configuration.",
        },
        {
            "id": DAY32_VRRP_PRECHECK_TASK_ID,
            "task_id": "day32_vrrp_readonly_precheck",
            "display_name": "Day32 VRRP Read-only Precheck",
            "user_display_name": "VRRP Read-only Precheck",
            "day": "Day32",
            "category": "ha_vrrp",
            "description": "Collect HA/VRRP readiness state from MikroTik routers using read-only RouterOS commands only.",
            "safety_level": "read-only",
            "execution_mode": "read-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                DAY32_VRRP_PRECHECK_JSON.as_posix(),
                DAY32_VRRP_PRECHECK_HTML.as_posix(),
                DAY32_VRRP_PRECHECK_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day32 VRRP read-only precheck JSON",
                "Day32 VRRP read-only precheck HTML",
                "Day32 VRRP read-only precheck TXT",
            ],
            "related_script": DAY32_VRRP_PRECHECK_SCRIPT,
            "notes": "Live SSH read-only precheck. The Day32 script blocks add, set, remove, disable, enable, reboot, and reset-configuration before any MikroTik command is sent.",
        },
        {
            "id": DAY33_VRRP_DRY_RUN_TASK_ID,
            "task_id": "day33_vrrp_topology_dry_run",
            "display_name": "Day33 VRRP Topology Dry-run",
            "user_display_name": "VRRP Topology Dry-run",
            "day": "Day33",
            "category": "ha_vrrp",
            "description": "Render HA/VRRP v0.2 topology design and RouterOS command previews without connecting to devices.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY33_VRRP_DRY_RUN_JSON.as_posix(),
                DAY33_VRRP_DRY_RUN_HTML.as_posix(),
                DAY33_VRRP_DRY_RUN_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day33 VRRP topology dry-run JSON",
                "Day33 VRRP topology dry-run HTML",
                "Day33 VRRP topology dry-run TXT",
            ],
            "related_script": DAY33_VRRP_DRY_RUN_SCRIPT,
            "notes": "Safe dry-run only. The Day33 script validates the v0.2 VRRP contract, renders RouterOS command previews, and never opens SSH or executes commands.",
        },
        {
            "id": DAY34_VRRP_STAGED_PLAN_TASK_ID,
            "task_id": "day34_vrrp_staged_apply_plan",
            "display_name": "Day34 VRRP Staged Apply Plan",
            "user_display_name": "VRRP Staged Apply Plan",
            "day": "Day34",
            "category": "ha_vrrp",
            "description": "Render a staged VRRP apply plan and safety gate; live execution remains blocked.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY34_VRRP_STAGED_PLAN_JSON.as_posix(),
                DAY34_VRRP_STAGED_PLAN_HTML.as_posix(),
                DAY34_VRRP_STAGED_PLAN_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day34 VRRP staged apply plan JSON",
                "Day34 VRRP staged apply plan HTML",
                "Day34 VRRP staged apply plan TXT",
            ],
            "related_script": DAY34_VRRP_STAGED_PLAN_SCRIPT,
            "notes": "Plan-only safety gate. Day34 requires Day32/Day33 evidence for review readiness, keeps manual confirmation blocked, and never opens SSH or executes RouterOS commands.",
        },
        {
            "id": DAY35_VRRP_FAILOVER_TASK_ID,
            "task_id": "day35_vrrp_failover_validation",
            "display_name": "Day35 VRRP Failover Validation",
            "user_display_name": "VRRP Failover Validation",
            "day": "Day35",
            "category": "ha_vrrp",
            "description": "Validate that lab02 takes over the VRRP VIP after a manual external lab01 LAN failure.",
            "safety_level": "controlled_failover_observation",
            "execution_mode": "controlled_failover_observation",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                DAY35_VRRP_FAILOVER_JSON.as_posix(),
                DAY35_VRRP_FAILOVER_HTML.as_posix(),
                DAY35_VRRP_FAILOVER_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day35 VRRP failover validation JSON",
                "Day35 VRRP failover validation HTML",
                "Day35 VRRP failover validation TXT",
            ],
            "related_script": DAY35_VRRP_FAILOVER_SCRIPT,
            "notes": "Controlled live observation. Day35 prompts the operator to disconnect/reconnect lab01 LAN externally, uses source-specific ping, sends only read-only RouterOS print commands, and blocks interface, firewall/NAT, IP, VRRP, reboot, and reset changes.",
        },
        {
            "id": WIREGUARD_RUNNER_TASK_ALIAS,
            "task_id": WIREGUARD_RUNNER_TASK_ID,
            "display_name": WIREGUARD_RUNNER_DISPLAY_NAME,
            "user_display_name": "WireGuard VPN Validation",
            "day": "Day18",
            "category": "vpn",
            "description": "Feature-named WireGuard runner integration for dry-run safety reporting and manually guarded live validation.",
            "safety_level": "guarded-live",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_output_path": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
            "report_paths": [
                WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
                WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day18 WireGuard runner safety-layer result JSON/HTML",
                "Related Day12 WireGuard validation report paths when delegated evidence exists",
                "Day22 WireGuard documentation relationship for safety review",
            ],
            "related_script": DAY12_WIREGUARD_SCRIPT,
            "notes": "Dry-run is the default runner posture. Guarded live validation requires manual --allow-live-wireguard authorization and omits firewall apply, peer recreation, reset, reboot, and VPN activation logic.",
        },
        {
            "id": "day13-wireguard-summary",
            "task_id": "day13_wireguard_summary_only",
            "display_name": "Day13 WireGuard Summary Only",
            "user_display_name": "WireGuard Summary Only",
            "day": "Day13",
            "category": "vpn",
            "description": "Report-only or placeholder visibility for Day13 WireGuard summaries.",
            "safety_level": "disabled",
            "execution_mode": "report-only",
            "enabled": False,
            "status": "planned",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.json",
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.html",
            ],
            "report_outputs": [
                "Day13 multi-router WireGuard validation summary JSON/HTML when generated outside the runner",
            ],
            "related_script": "mikrotik_day13_multi_router_wireguard_validation.py",
            "notes": "Disabled live runner task. Day13 summary remains report-only until its own live safety layer is implemented.",
        },
    ]


def _build_parser() -> argparse.ArgumentParser:
    examples = """examples:
  python network_lab.py
  python network_lab.py --interactive
  python network_lab.py --list-tasks
  python network_lab.py --list-tasks --verbose
  python network_lab.py --report-index
  python network_lab.py --portfolio-finalize
  python network_lab.py --task demo-flow
  python network_lab.py --task report-index --dry-run
  python network_lab.py --task report-index
  python network_lab.py --task day4-baseline --dry-run
  python network_lab.py --task day4-baseline
  python network_lab.py --task iperf3-performance --dry-run
  python network_lab.py --task iperf3-performance
  python network_lab.py --task day32-vrrp-precheck
  python network_lab.py --task day33-vrrp-dry-run
  python network_lab.py --task day34-vrrp-staged-plan
  python network_lab.py --task day35-vrrp-failover-validation
  python network_lab.py --task wireguard-runner --dry-run
  python network_lab.py --task wireguard-runner --wireguard-config Set_WireguardVPN_lab02_config.json --dry-run
  python network_lab.py --task wireguard-runner
  python network_lab.py --task wireguard-runner --wireguard-config Set_WireguardVPN_lab02_config.json --allow-live-wireguard
  python network_lab.py --task report-index --profile topology_profiles/day14_lab_runner_profile.json

report-index and portfolio-finalize read existing report metadata and do not connect to devices.
day4-baseline delegates to the existing live SSH validation script.
iperf3-performance delegates to the existing live iperf3 performance script.
day32-vrrp-precheck runs read-only MikroTik print/export terse commands with a blocking safety guard.
day33-vrrp-dry-run generates local VRRP topology and command previews without SSH or RouterOS execution.
day34-vrrp-staged-plan generates a blocked staged apply plan and safety gate without SSH or RouterOS execution.
day35-vrrp-failover-validation observes manual external VRRP failover with read-only RouterOS commands and source-specific LAN pings.
wireguard-runner is dry-run by default and delegates to the existing WireGuard script only after explicit --allow-live-wireguard."""
    parser = argparse.ArgumentParser(
        description=f"Day14 {DAY14_NAME}.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list-tasks", action="store_true", help="List available and planned lab tasks.")
    parser.add_argument("--verbose", action="store_true", help="Show detailed task catalog metadata with --list-tasks.")
    parser.add_argument("--report-index", action="store_true", help="Scan local reports and write reports/report_index.html.")
    parser.add_argument(
        "--portfolio-finalize",
        action="store_true",
        help="Write the Day19 portfolio evidence index JSON and HTML without running live workflows.",
    )
    parser.add_argument(
        "--task",
        choices=[
            "report-index",
            "portfolio-finalize",
            "demo-flow",
            "day4-baseline",
            "iperf3-performance",
            DAY32_VRRP_PRECHECK_TASK_ID,
            DAY33_VRRP_DRY_RUN_TASK_ID,
            DAY34_VRRP_STAGED_PLAN_TASK_ID,
            DAY35_VRRP_FAILOVER_TASK_ID,
            WIREGUARD_RUNNER_TASK_ALIAS,
        ],
        help="Task to run.",
    )
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Path to the Day14 lab runner profile JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Show report-index inputs and outputs without writing reports.")
    parser.add_argument("--interactive", action="store_true", help="Show the safe interactive Day14 menu.")
    parser.add_argument("--allow-live-wireguard", action="store_true", help="Allow guarded live WireGuard execution.")
    parser.add_argument(
        "--wireguard-config",
        default=DAY12_WIREGUARD_CONFIG,
        help=f"Config path for the delegated Day12 WireGuard validation script. Default: {DAY12_WIREGUARD_CONFIG}.",
    )
    parser.add_argument(
        "--wireguard-run-iperf",
        "--run-iperf",
        action="store_true",
        dest="run_iperf",
        help="For WireGuard runner live mode, also request iperf3 checks with --expect-connected.",
    )
    return parser


def _resolve_project_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _task_enabled_label(task: Dict[str, Any]) -> str:
    return "enabled" if task.get("enabled") else "planned"


def _print_compact_task_list() -> None:
    print(format_heading("Task Catalog"))
    print("Use: python network_lab.py --task <task-name>")
    print("For full metadata, run: python network_lab.py --list-tasks --verbose")
    print()
    print(f"{'Task':<24} {'Name':<38} {'Safety':<18} Status")
    print(f"{'-' * 24} {'-' * 38} {'-' * 18} {'-' * 10}")
    for task in list_tasks():
        print(
            f"{task['id']:<24} "
            f"{str(task.get('user_display_name', task['display_name']))[:38]:<38} "
            f"{task['safety_level']:<18} "
            f"{_task_enabled_label(task)}"
        )


def _print_verbose_task_list() -> None:
    print(format_heading("Task Catalog"))
    for task in list_tasks():
        print()
        print(f"[{task['task_id']}]")
        print(f"CLI task: {task['id']}")
        print(f"Day: {task['day']}")
        print(f"Display name: {task['display_name']}")
        print(f"User-facing name: {task.get('user_display_name', task['display_name'])}")
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


def _print_task_list(verbose: bool = False) -> None:
    if verbose:
        _print_verbose_task_list()
        return
    _print_compact_task_list()


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
                    "report_type": report_type.get("report_type", "Report evidence"),
                    "device": _report_device_label(None, report_type["title"]),
                    "status": "MISSING",
                    "safety": report_type.get("safety_label", "report-only evidence"),
                    "description": report_type.get("description", ""),
                    "json": "",
                    "html": "",
                    "notes": report_type.get("missing_note", "Expected report was not found."),
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
                    "report_type": report_type.get("report_type", "Report evidence"),
                    "device": _report_device_label(label_path, report_type["title"]),
                    "status": "FOUND" if json_path or html_path else "MISSING",
                    "safety": report_type.get("safety_label", "report-only evidence"),
                    "description": report_type.get("description", ""),
                    "json": _relative_to_project(project_root, json_path) if json_path else "MISSING",
                    "html": _relative_to_project(project_root, html_path) if html_path else "MISSING",
                    "notes": "",
                }
            )

    day18_evidence = build_day18_runner_evidence(project_root)
    for row in rows:
        if row.get("day") == "Day18" and row.get("title") == WIREGUARD_RUNNER_DISPLAY_NAME:
            row["day18_evidence"] = day18_evidence
            row["notes"] = _format_day18_console_note(day18_evidence)

    rows.append(
        {
            "day": "Day13",
            "title": "Day13 WireGuard Live Execution",
            "report_type": "Disabled live workflow",
            "device": "Runner guardrail",
            "status": "DISABLED FOR DAY18",
            "safety": "disabled guardrail",
            "description": "Day13 live execution is intentionally not exposed through the Day18 runner safety layer.",
            "json": "",
            "html": "",
            "notes": "Day13 live WireGuard execution remains disabled until its own runner safety layer is implemented.",
        }
    )
    return rows


def _safe_nested_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_day18_runner_evidence(project_root: Path) -> Dict[str, Any]:
    json_path = project_root / WIREGUARD_RUNNER_REPORT_JSON
    html_path = project_root / WIREGUARD_RUNNER_REPORT_HTML
    evidence: Dict[str, Any] = {
        "runner_json": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
        "runner_html": WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
        "runner_json_exists": json_path.exists(),
        "runner_html_exists": html_path.exists(),
        "selected_config_path": "Not available",
        "delegated_day12_json": "Not available",
        "delegated_day12_html": "Not available",
        "final_vpn_connectivity": "Not available",
        "iperf_forward_mbps": "Not available",
        "iperf_reverse_mbps": "Not available",
        "runner_safety_guardrail_status": {},
        "parse_warning": "",
    }
    if not json_path.exists():
        return evidence

    try:
        report = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        evidence["parse_warning"] = f"Could not parse Day18 runner report: {exc}"
        return evidence

    delegated_report = _safe_nested_dict(report.get("delegated_report"))
    delegated_summary = _safe_nested_dict(report.get("delegated_result_summary"))
    guardrails = _safe_nested_dict(report.get("safety_guardrail_status"))
    evidence.update(
        mask_secret_values(
            {
                "selected_config_path": report.get("selected_config_path") or "Not available",
                "delegated_day12_json": delegated_report.get("json") or "Not available",
                "delegated_day12_html": delegated_report.get("html") or "Not available",
                "final_vpn_connectivity": delegated_summary.get("final_vpn_connectivity") or "Not available",
                "iperf_forward_mbps": delegated_summary.get("iperf_forward_mbps", "Not available"),
                "iperf_reverse_mbps": delegated_summary.get("iperf_reverse_mbps", "Not available"),
                "runner_safety_guardrail_status": guardrails,
            }
        )
    )
    return evidence


def _format_day18_console_note(evidence: Dict[str, Any]) -> str:
    if not evidence.get("runner_json_exists"):
        return f"Expected Day18 runner report: {evidence['runner_json']}"
    return (
        f"config={evidence.get('selected_config_path')}; "
        f"vpn={evidence.get('final_vpn_connectivity')}; "
        f"iperf={evidence.get('iperf_forward_mbps')}/{evidence.get('iperf_reverse_mbps')} Mbps"
    )


def _compact_guardrail_status(guardrails: Dict[str, Any]) -> str:
    if not guardrails:
        return "Not available"
    return ", ".join(f"{key}={value}" for key, value in guardrails.items())


def _print_report_visibility(rows: List[Dict[str, Any]], output_path: str = "reports/report_index.html") -> None:
    print(format_heading("Report Index"))
    counts = _count_report_statuses(rows)
    status_width = max(22, max(len(str(row.get("status", ""))) + 2 for row in rows))
    print(
        "Summary: "
        f"found={color_text(str(counts['found']), 'green', bold=True)} "
        f"missing={color_text(str(counts['missing']), 'yellow', bold=True)} "
        f"disabled={color_text(str(counts['disabled']), 'blue', bold=True)}"
    )
    print(f"Output: {output_path}")

    current_key: Optional[Tuple[str, str]] = None
    group_rows: List[Dict[str, Any]] = []

    def flush_group() -> None:
        if not group_rows:
            return
        first = group_rows[0]
        print()
        print(format_heading(f"{first['title']} ({first['day']})"))
        print(f"  {'Status':<{status_width}} {'Device':<24} {'Safety':<28} Report paths")
        print(f"  {'-' * status_width} {'-' * 24} {'-' * 28} {'-' * 42}")
        visible_rows, hidden_count = _compact_console_report_rows(group_rows)
        for visible_row in visible_rows:
            _print_report_visibility_row(visible_row, status_width)
        if hidden_count:
            print(
                f"  ... {hidden_count} more reports hidden in console; "
                f"open {output_path} for full list"
            )

    for row in rows:
        key = (str(row["day"]), str(row["title"]))
        if current_key is None:
            current_key = key
        if key != current_key:
            flush_group()
            group_rows = []
            current_key = key
        group_rows.append(row)
    flush_group()


def _compact_console_report_rows(
    rows: List[Dict[str, Any]],
    max_default_rows: int = 3,
) -> Tuple[List[Dict[str, Any]], int]:
    special_rows = [
        row
        for row in rows
        if str(row.get("status", "")).upper() == "MISSING"
        or "DISABLED" in str(row.get("status", "")).upper()
    ]
    visible_ids = {id(row) for row in special_rows}
    remaining_slots = max(0, max_default_rows - len(special_rows))
    for row in rows:
        if id(row) in visible_ids:
            continue
        if remaining_slots <= 0:
            break
        special_rows.append(row)
        visible_ids.add(id(row))
        remaining_slots -= 1
    hidden_count = len(rows) - len(visible_ids)
    return special_rows, hidden_count


def _print_report_visibility_row(row: Dict[str, Any], status_width: int) -> None:
    status = _format_report_visibility_status(str(row["status"]))
    safety = str(row.get("safety", ""))[:28]
    print(f"  {status:<{status_width}} {str(row['device'])[:24]:<24} {safety:<28} JSON: {row.get('json') or '-'}")
    if row.get("html"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} HTML: {row['html']}")
    if row.get("notes"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} Notes: {row['notes']}")
    evidence = row.get("day18_evidence")
    if isinstance(evidence, dict) and evidence.get("runner_json_exists"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} Day12 JSON: {evidence.get('delegated_day12_json')}")
        print(
            f"  {'':<{status_width}} {'':<24} {'':<28} Guardrails: "
            f"{_compact_guardrail_status(_safe_nested_dict(evidence.get('runner_safety_guardrail_status')))}"
        )


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


def _day18_evidence_for_html(report_rows: List[Dict[str, Any]], project_root: Path) -> Dict[str, Any]:
    for row in report_rows:
        evidence = row.get("day18_evidence")
        if isinstance(evidence, dict):
            return evidence
    return build_day18_runner_evidence(project_root)


def _render_day18_evidence_html(evidence: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    guardrails = _safe_nested_dict(evidence.get("runner_safety_guardrail_status"))
    guardrail_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in guardrails.items()
    ) or "<tr><td colspan=\"2\">Not available</td></tr>"
    detail_rows = [
        ("Day18 runner JSON", _html_link_or_text(output_path, project_root, str(evidence.get("runner_json", "")))),
        ("Day18 runner HTML", _html_link_or_text(output_path, project_root, str(evidence.get("runner_html", "")))),
        ("Delegated Day12 JSON", _html_link_or_text(output_path, project_root, str(evidence.get("delegated_day12_json", "")))),
        ("Delegated Day12 HTML", _html_link_or_text(output_path, project_root, str(evidence.get("delegated_day12_html", "")))),
        ("Selected WireGuard config", html.escape(str(evidence.get("selected_config_path", "Not available")))),
        ("Final VPN connectivity", html.escape(str(evidence.get("final_vpn_connectivity", "Not available")))),
        ("iperf forward Mbps", html.escape(str(evidence.get("iperf_forward_mbps", "Not available")))),
        ("iperf reverse Mbps", html.escape(str(evidence.get("iperf_reverse_mbps", "Not available")))),
    ]
    if evidence.get("parse_warning"):
        detail_rows.append(("Parse warning", html.escape(str(evidence["parse_warning"]))))
    rows = "\n".join(f"<tr><td>{html.escape(label)}</td><td>{value}</td></tr>" for label, value in detail_rows)
    return f"""
    <h2>Day18 WireGuard Runner Evidence</h2>
    <div class="warning">Day18 runner evidence is summarized from the runner report. Day12 remains the detailed source of truth for WireGuard validation.</div>
    <table>
      <thead><tr><th>Field</th><th>Value</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <h2>Day18 Runner Guardrails</h2>
    <table>
      <thead><tr><th>Guardrail</th><th>Status</th></tr></thead>
      <tbody>{guardrail_rows}</tbody>
    </table>
"""


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
        f"<td>{html.escape(str(row.get('report_type', 'Report evidence')))}</td>"
        f"<td>{html.escape(str(row['device']))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(row['status']))}\">{html.escape(str(row['status']))}</span></td>"
        f"<td><span class=\"pill safety-{_css_token(str(row.get('safety', 'report-only')))}\">{html.escape(str(row.get('safety', 'report-only')))}</span></td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('json', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('html', '')))}</td>"
        f"<td>{html.escape(str(row.get('description', '')))}</td>"
        f"<td>{html.escape(str(row.get('notes', '')))}</td>"
        "</tr>"
        for row in report_rows
    )
    safety_rows = "\n".join(
        f"<tr><td><span class=\"pill safety-{_css_token(level)}\">{html.escape(level)}</span></td><td>{html.escape(description)}</td></tr>"
        for level, description in SAFETY_LEVELS.items()
    )
    day18_evidence_html = _render_day18_evidence_html(
        _day18_evidence_for_html(report_rows, project_root),
        output_path,
        project_root,
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
    .disabled, .status-disabled-for-day18, .safety-future-reserved {{ background: var(--blue-bg); color: var(--blue-ink); }}
    .status-missing {{ background: var(--yellow-bg); color: var(--yellow); }}
    .safety-safe-read-only {{ background: var(--green-bg); color: var(--green); }}
    .safety-live-read-only {{ background: #e7f0fb; color: #175cd3; }}
    .safety-live-performance {{ background: #f3e8ff; color: #6941c6; }}
    .safety-live-config-change {{ background: var(--red-bg); color: var(--red); }}
    .safety-guarded-live {{ background: #ecfdf3; color: #067647; }}
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
    <div class="warning">Day18 WireGuard runner integration uses a safety layer: dry-run by default, explicit live confirmation, fixed argv execution, and no peer/firewall write flags.</div>
    {day18_evidence_html}
    <h2>Task Catalog Summary</h2>
    <table>
      <thead><tr><th>Task ID</th><th>Day</th><th>Name</th><th>Category</th><th>Safety</th><th>Enabled</th><th>Mode</th><th>Live Device</th></tr></thead>
      <tbody>{task_rows}</tbody>
    </table>
    <h2>Report Visibility</h2>
    <table>
      <thead><tr><th>Day</th><th>Task Name</th><th>Report Type</th><th>Device</th><th>Status</th><th>Safety</th><th>JSON</th><th>HTML</th><th>Description</th><th>Notes</th></tr></thead>
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


def _portfolio_evidence_area(row: Dict[str, Any]) -> str:
    title = str(row.get("title", "")).lower()
    day = str(row.get("day", ""))
    if "wireguard" in title:
        return "VPN validation"
    if "iperf" in title or "performance" in title:
        return "Performance"
    if "topology" in title:
        return "Topology"
    if "baseline" in title or "auto setup" in title:
        return "Baseline"
    if "runner" in title or "overview" in title:
        return "Runner"
    return day or "Evidence"


def _portfolio_evidence_quality(row: Dict[str, Any]) -> str:
    status = str(row.get("status", "")).upper()
    json_path = str(row.get("json", ""))
    html_path = str(row.get("html", ""))
    if status == "FOUND" and json_path != "MISSING" and html_path != "MISSING":
        return "READY"
    if status == "FOUND":
        return "PARTIAL"
    if "DISABLED" in status:
        return "GUARDED"
    return "MISSING"


def build_portfolio_evidence_index(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    counts = _count_report_statuses(report_rows)
    evidence_items = [
        {
            "day": row.get("day", ""),
            "area": _portfolio_evidence_area(row),
            "title": row.get("title", ""),
            "report_type": row.get("report_type", ""),
            "device": row.get("device", ""),
            "quality": _portfolio_evidence_quality(row),
            "source_status": row.get("status", ""),
            "safety": row.get("safety", ""),
            "json": row.get("json", ""),
            "html": row.get("html", ""),
            "description": row.get("description", ""),
            "notes": row.get("notes", ""),
        }
        for row in report_rows
    ]
    local_only_tasks = [
        task
        for task in task_catalog
        if not task.get("requires_live_device") and task.get("safety_level") == "report-only"
    ]
    live_guarded_tasks = [
        task
        for task in task_catalog
        if task.get("requires_live_device") or "live" in str(task.get("safety_level", "")).lower()
    ]
    readiness = "READY_WITH_GAPS" if counts["found"] else "NEEDS_LOCAL_REPORTS"
    if counts["found"] and not counts["missing"]:
        readiness = "READY"

    return mask_secret_values(
        {
            "day": "Day19",
            "name": "Runner Evidence Index and Portfolio Finalization",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "portfolio_readiness": readiness,
            "summary": {
                "tasks": len(task_catalog),
                "local_only_tasks": len(local_only_tasks),
                "live_or_guarded_tasks": len(live_guarded_tasks),
                "reports_found": counts["found"],
                "reports_missing": counts["missing"],
                "disabled_guardrails": counts["disabled"],
            },
            "portfolio_highlights": [
                "Unified runner lists safe local tasks separately from guarded live workflows.",
                "Evidence index links JSON and HTML reports without reading config.json or exported WireGuard configs.",
                "WireGuard runner remains dry-run by default and requires explicit live authorization.",
                "Generated Day19 output is suitable for portfolio screenshots and final review.",
            ],
            "evidence_items": evidence_items,
        }
    )


def write_portfolio_evidence_html(
    evidence: Dict[str, Any],
    output_path: Path,
    project_root: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = evidence.get("summary", {})
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(item.get('day', '')))}</span></td>"
        f"<td>{html.escape(str(item.get('area', '')))}</td>"
        f"<td>{html.escape(str(item.get('title', '')))}</td>"
        f"<td>{html.escape(str(item.get('report_type', '')))}</td>"
        f"<td>{html.escape(str(item.get('device', '')))}</td>"
        f"<td><span class=\"pill quality-{_css_token(str(item.get('quality', '')))}\">{html.escape(str(item.get('quality', '')))}</span></td>"
        f"<td>{html.escape(str(item.get('safety', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(item.get('json', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(item.get('html', '')))}</td>"
        f"<td>{html.escape(str(item.get('description', '')))}</td>"
        f"<td>{html.escape(str(item.get('notes', '')))}</td>"
        "</tr>"
        for item in evidence.get("evidence_items", [])
    )
    highlights = "".join(
        f"<li>{html.escape(str(item))}</li>"
        for item in evidence.get("portfolio_highlights", [])
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day19 Runner Evidence Index</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #243447;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
      --blue-bg: #e6f0ff;
      --blue: #1849a9;
      --gray-bg: #eef2f6;
      --gray: #475467;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    a {{ color: #155bb5; font-weight: 700; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .meta {{ color: #dbe5f3; }}
    .summary {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .pill-day, .quality-missing {{ background: var(--gray-bg); color: var(--gray); }}
    .quality-ready {{ background: var(--green-bg); color: var(--green); }}
    .quality-partial {{ background: var(--yellow-bg); color: var(--yellow); }}
    .quality-guarded {{ background: var(--blue-bg); color: var(--blue); }}
    .highlights {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Day19 Runner Evidence Index</h1>
    <div class="meta">{html.escape(str(evidence.get("name", "")))} · Generated {html.escape(str(evidence.get("generated_at", "")))}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Readiness</div><div class="metric-value">{html.escape(str(evidence.get("portfolio_readiness", "")))}</div></div>
      <div class="metric"><div class="metric-label">Tasks</div><div class="metric-value">{summary.get("tasks", 0)}</div></div>
      <div class="metric"><div class="metric-label">Found</div><div class="metric-value">{summary.get("reports_found", 0)}</div></div>
      <div class="metric"><div class="metric-label">Missing</div><div class="metric-value">{summary.get("reports_missing", 0)}</div></div>
      <div class="metric"><div class="metric-label">Guardrails</div><div class="metric-value">{summary.get("disabled_guardrails", 0)}</div></div>
    </section>
  </header>
  <main>
    <h2>Portfolio Highlights</h2>
    <ul class="highlights">{highlights}</ul>
    <h2>Evidence Items</h2>
    <table>
      <thead><tr><th>Day</th><th>Area</th><th>Evidence</th><th>Report Type</th><th>Device</th><th>Quality</th><th>Safety</th><th>JSON</th><th>HTML</th><th>Description</th><th>Notes</th></tr></thead>
      <tbody>{evidence_rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def build_day24_demo_flow(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    task_ids = {str(task.get("id", "")) for task in task_catalog}
    available_titles = {
        str(row.get("title", ""))
        for row in report_rows
        if str(row.get("status", "")).upper() != "MISSING"
    }
    walkthrough_steps = [
        {
            "order": 1,
            "section": "Scope",
            "demo_action": "Open the README and explain the lab goal, supported devices, and current Day1-Day24 scope.",
            "command_or_location": "README.md",
            "talk_track": "This is a QA/SDET network automation lab focused on repeatable validation and readable evidence, not one-off screenshots.",
            "evidence": "Project overview, progress table, and safety sections.",
        },
        {
            "order": 2,
            "section": "Runner Safety",
            "demo_action": "Show the task catalog with verbose metadata.",
            "command_or_location": "python network_lab.py --list-tasks --verbose",
            "talk_track": "The runner separates report-only, read-only, dry-run, guarded-live, and disabled workflows before anyone can trigger live lab behavior.",
            "evidence": "Task IDs, safety levels, execution modes, report paths, and notes.",
        },
        {
            "order": 3,
            "section": "Evidence Index",
            "demo_action": "Generate or open the local report visibility index.",
            "command_or_location": "python network_lab.py --report-index",
            "talk_track": "Report visibility reads existing JSON/HTML files, marks missing evidence clearly, and does not connect to routers, switches, VPN clients, or iperf3 endpoints.",
            "evidence": DAY17_REPORT_INDEX_HTML.as_posix(),
        },
        {
            "order": 4,
            "section": "Dashboard Walkthrough",
            "demo_action": "Start the dashboard and open the read-only report viewer.",
            "command_or_location": "python dashboard_app.py -> http://127.0.0.1:5000/reports",
            "talk_track": "The dashboard is the human review surface: grouped evidence cards, redacted JSON preview, and safe links to already-generated HTML reports.",
            "evidence": "Day21 dashboard /reports viewer.",
        },
        {
            "order": 5,
            "section": "WireGuard Safety Boundary",
            "demo_action": "Run or show the WireGuard runner dry-run.",
            "command_or_location": "python network_lab.py --task wireguard-runner --dry-run",
            "talk_track": "WireGuard validation is intentionally dry-run by default, with guarded live delegation only after explicit authorization and without unsafe write flags.",
            "evidence": WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
        },
        {
            "order": 6,
            "section": "Portfolio Close",
            "demo_action": "Open the Day19 portfolio index, then this Day24 walkthrough artifact.",
            "command_or_location": "python network_lab.py --portfolio-finalize; python network_lab.py --task demo-flow",
            "talk_track": "The portfolio view ties together evidence quality, missing gaps, guardrails, and the recommended reviewer path for the RC.",
            "evidence": f"{DAY19_EVIDENCE_INDEX_HTML.as_posix()} and {DAY24_DEMO_FLOW_HTML.as_posix()}",
        },
    ]
    checklist = [
        {
            "item": "Task catalog includes report-only demo flow",
            "status": "PASS" if "demo-flow" in task_ids else "MISSING",
        },
        {
            "item": "Report visibility has at least one local evidence row",
            "status": "PASS" if available_titles else "MISSING",
        },
        {
            "item": "WireGuard runner remains guarded or dry-run",
            "status": "PASS"
            if any(task.get("id") == WIREGUARD_RUNNER_TASK_ALIAS and task.get("execution_mode") == "dry-run" for task in task_catalog)
            else "MISSING",
        },
        {
            "item": "Day13 live runner path remains disabled",
            "status": "PASS"
            if any(task.get("id") == "day13-wireguard-summary" and not task.get("enabled") for task in task_catalog)
            else "MISSING",
        },
        {
            "item": "Portfolio index task remains local-only",
            "status": "PASS"
            if any(task.get("id") == "portfolio-finalize" and not task.get("requires_live_device") for task in task_catalog)
            else "MISSING",
        },
    ]
    return mask_secret_values(
        {
            "day": "Day24",
            "name": "RC Demo Flow and Portfolio Walkthrough",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "mode": "report-only",
            "result": "READY" if all(item["status"] == "PASS" for item in checklist) else "READY_WITH_GAPS",
            "safety_summary": [
                "No live workflows are executed by this demo-flow task.",
                "No config.json, WireGuard .conf files, SSH passwords, or private keys are read.",
                "Live validation remains behind existing guarded runner paths.",
            ],
            "walkthrough_steps": walkthrough_steps,
            "rc_checklist": checklist,
            "recommended_open_order": [
                "README.md",
                "docs/portfolio_evidence.md",
                DAY17_REPORT_INDEX_HTML.as_posix(),
                "http://127.0.0.1:5000/reports",
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
                DAY24_DEMO_FLOW_HTML.as_posix(),
            ],
        }
    )


def write_day24_demo_flow_html(
    demo_flow: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    steps = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(step.get('order', '')))}</td>"
        f"<td>{html.escape(str(step.get('section', '')))}</td>"
        f"<td>{html.escape(str(step.get('demo_action', '')))}</td>"
        f"<td><code>{html.escape(str(step.get('command_or_location', '')))}</code></td>"
        f"<td>{html.escape(str(step.get('talk_track', '')))}</td>"
        f"<td>{html.escape(str(step.get('evidence', '')))}</td>"
        "</tr>"
        for step in demo_flow.get("walkthrough_steps", [])
    )
    checklist = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('item', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(item.get('status', '')))}\">{html.escape(str(item.get('status', '')))}</span></td>"
        "</tr>"
        for item in demo_flow.get("rc_checklist", [])
    )
    safety = "".join(f"<li>{html.escape(str(item))}</li>" for item in demo_flow.get("safety_summary", []))
    open_order = "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in demo_flow.get("recommended_open_order", []))
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day24 RC Demo Flow</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #243447;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
    .meta {{ color: #dbe5f3; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .status-pass, .status-ready {{ background: var(--green-bg); color: var(--green); }}
    .status-missing, .status-ready-with-gaps {{ background: var(--yellow-bg); color: var(--yellow); }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Day24 RC Demo Flow</h1>
    <div class="meta">{html.escape(str(demo_flow.get("name", "")))} · Generated {html.escape(str(demo_flow.get("generated_at", "")))} · Result {html.escape(str(demo_flow.get("result", "")))}</div>
  </header>
  <main>
    <h2>Walkthrough Steps</h2>
    <table>
      <thead><tr><th>#</th><th>Section</th><th>Demo Action</th><th>Command / Location</th><th>Talk Track</th><th>Evidence</th></tr></thead>
      <tbody>{steps}</tbody>
    </table>
    <h2>RC Checklist</h2>
    <table>
      <thead><tr><th>Item</th><th>Status</th></tr></thead>
      <tbody>{checklist}</tbody>
    </table>
    <h2>Safety Summary</h2>
    <ul class="panel">{safety}</ul>
    <h2>Recommended Open Order</h2>
    <ol class="panel">{open_order}</ol>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day24_demo_flow(project_root: Path) -> int:
    task_catalog = list_tasks()
    report_rows = discover_report_visibility(project_root)
    demo_flow = build_day24_demo_flow(task_catalog, report_rows)
    json_path = project_root / DAY24_DEMO_FLOW_JSON
    html_path = project_root / DAY24_DEMO_FLOW_HTML
    write_json_report(demo_flow, json_path)
    write_day24_demo_flow_html(demo_flow, html_path)
    print(format_heading("Day24 RC Demo Flow"))
    print(f"Result: {demo_flow['result']}")
    print(f"Walkthrough steps: {len(demo_flow['walkthrough_steps'])}")
    print(f"JSON demo flow: {_relative_to_project(project_root, json_path)}")
    print(f"HTML demo flow: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day24 demo flow completed without live execution.")
    return 0


def _run_portfolio_finalization(project_root: Path) -> int:
    task_catalog = list_tasks()
    report_rows = discover_report_visibility(project_root)
    evidence = build_portfolio_evidence_index(task_catalog, report_rows)
    json_path = project_root / DAY19_EVIDENCE_INDEX_JSON
    html_path = project_root / DAY19_EVIDENCE_INDEX_HTML
    write_json_report(evidence, json_path)
    write_portfolio_evidence_html(evidence, html_path, project_root)
    print(format_heading("Day19 Runner Evidence Index"))
    print(f"Portfolio readiness: {evidence['portfolio_readiness']}")
    print(
        "Summary: "
        f"tasks={evidence['summary']['tasks']} "
        f"found={evidence['summary']['reports_found']} "
        f"missing={evidence['summary']['reports_missing']} "
        f"guardrails={evidence['summary']['disabled_guardrails']}"
    )
    print(f"JSON evidence index: {_relative_to_project(project_root, json_path)}")
    print(f"HTML evidence index: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day19 portfolio finalization completed without live execution.")
    return 0


def _run_report_visibility_index(project_root: Path) -> int:
    rows = discover_report_visibility(project_root)
    output_path = project_root / DAY17_REPORT_INDEX_HTML
    output_path_text = _relative_to_project(project_root, output_path)
    _print_report_visibility(rows, output_path_text)
    write_report_index_html(list_tasks(), rows, output_path, project_root)
    print()
    print(f"{format_status('PASS')} HTML report index: {output_path_text}")
    print("Day18 WireGuard runner integration uses dry-run and explicit confirmation guardrails.")
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


def _run_day32_vrrp_precheck(project_root: Path, dry_run: bool = False) -> int:
    command = [sys.executable, DAY32_VRRP_PRECHECK_SCRIPT]
    display_command = _format_display_command(command)
    if dry_run:
        print(format_heading("Day32 VRRP Read-only Precheck"))
        print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
        print(f"Command that would be executed: {color_text(display_command, 'cyan', bold=True)}")
        print()
        print(format_heading("Safety notes"))
        print("  This is a live SSH read-only precheck workflow.")
        print("  The Day32 script validates every MikroTik command before sending it.")
        print("  Allowed operations are print, /export terse, and local report generation.")
        print("  Blocked keywords are add, set, remove, disable, enable, reboot, and reset-configuration.")
        print("  Dry-run does not connect to devices and does not write reports.")
        print()
        print(f"{format_status('PASS')} No live workflow was executed.")
        return 0

    print(format_heading("Day32 VRRP Read-only Precheck"))
    print("Live SSH read-only precheck workflow.")
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day32 VRRP read-only precheck completed.")
        return 0

    print(f"{format_status('FAIL')} Day32 VRRP read-only precheck failed with exit code {result.returncode}.")
    return result.returncode


def _run_day33_vrrp_dry_run(project_root: Path) -> int:
    command = [sys.executable, DAY33_VRRP_DRY_RUN_SCRIPT]
    display_command = _format_display_command(command)
    print(format_heading("Day33 VRRP Topology Dry-run"))
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    print("Safety guard: DRY-RUN ONLY and NOT EXECUTED; no SSH connection or RouterOS execution is performed.")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day33 VRRP topology dry-run completed.")
        print(f"JSON report: {DAY33_VRRP_DRY_RUN_JSON.as_posix()}")
        print(f"HTML report: {DAY33_VRRP_DRY_RUN_HTML.as_posix()}")
        print(f"TXT report: {DAY33_VRRP_DRY_RUN_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day33 VRRP topology dry-run failed with exit code {result.returncode}.")
    return result.returncode


def _run_day34_vrrp_staged_plan(project_root: Path) -> int:
    command = [sys.executable, DAY34_VRRP_STAGED_PLAN_SCRIPT]
    display_command = _format_display_command(command)
    print(format_heading("Day34 VRRP Staged Apply Plan"))
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    print("Safety gate: BLOCKED PLAN ONLY and NOT EXECUTED; no SSH connection or RouterOS execution is performed.")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day34 VRRP staged apply plan completed.")
        print(f"JSON report: {DAY34_VRRP_STAGED_PLAN_JSON.as_posix()}")
        print(f"HTML report: {DAY34_VRRP_STAGED_PLAN_HTML.as_posix()}")
        print(f"TXT report: {DAY34_VRRP_STAGED_PLAN_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day34 VRRP staged apply plan failed with exit code {result.returncode}.")
    return result.returncode


def _run_day35_vrrp_failover_validation(project_root: Path, dry_run: bool = False) -> int:
    command = [sys.executable, DAY35_VRRP_FAILOVER_SCRIPT]
    display_command = _format_display_command(command)
    if dry_run:
        print(format_heading("Day35 VRRP Failover Validation"))
        print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
        print(f"Command that would be executed: {color_text(display_command, 'cyan', bold=True)}")
        print()
        print(format_heading("Safety notes"))
        print("  This is a controlled live observation workflow.")
        print("  The operator manually disconnects/reconnects lab01 LAN from the switch.")
        print("  Automation uses ping -S 192.168.88.100 <target> and read-only RouterOS print commands.")
        print("  Blocked actions include interface enable/disable, firewall/NAT changes, IP changes, VRRP changes, reboot, and reset.")
        print("  Dry-run does not prompt for cable actions, wait, connect to devices, run pings, or write reports.")
        print()
        print(f"{format_status('PASS')} No live workflow was executed.")
        return 0

    print(format_heading("Day35 VRRP Failover Validation"))
    print("Controlled live observation workflow.")
    print("Manual trigger: disconnect/reconnect lab01 LAN cable only when prompted.")
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day35 VRRP failover validation completed.")
        print(f"JSON report: {DAY35_VRRP_FAILOVER_JSON.as_posix()}")
        print(f"HTML report: {DAY35_VRRP_FAILOVER_HTML.as_posix()}")
        print(f"TXT report: {DAY35_VRRP_FAILOVER_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day35 VRRP failover validation failed with exit code {result.returncode}.")
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


def _wireguard_runner_report_path(project_root: Path, html_report: bool = False) -> Path:
    return project_root / (WIREGUARD_RUNNER_REPORT_HTML if html_report else WIREGUARD_RUNNER_REPORT_JSON)


def _wireguard_runner_planned_steps(run_iperf: bool = False) -> List[str]:
    steps = [
        "Validate WireGuard runner config file path.",
        "Validate required non-secret config fields before guarded execution.",
        "Delegate to the existing WireGuard validation script only when live guard is explicit.",
        "Keep peer recreation and firewall fix flags disabled in the runner.",
        "Write local runner safety report with secrets masked.",
    ]
    if run_iperf:
        steps.append("Request iperf3 checks only in guarded live mode.")
    return steps


def _wireguard_config_path(project_root: Path, config_path: str) -> Path:
    path = Path(config_path)
    return path if path.is_absolute() else project_root / path


def _wireguard_config_display_path(project_root: Path, config_path: str) -> str:
    return _relative_to_project(project_root, _wireguard_config_path(project_root, config_path))


def _wireguard_runner_config_validation(project_root: Path, config_path: str = DAY12_WIREGUARD_CONFIG) -> Dict[str, Any]:
    selected_path = _wireguard_config_path(project_root, config_path)
    selected_display_path = _wireguard_config_display_path(project_root, config_path)
    required_fields = ["device_name", "router_host", "router_username", "wg_interface", "peer_name"]
    optional_fields = ["lan_gateway_ip", "lan_host_ip", "iperf_server_ip", "client_address"]
    validation: Dict[str, Any] = {
        "config_path": selected_display_path,
        "status": "PASS",
        "missing_required_fields": [],
        "missing_optional_fields": [],
        "warnings": [],
    }
    try:
        data = json.loads(selected_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation["status"] = "WARN"
        validation["missing_required_fields"] = ["config_file"]
        validation["warnings"] = [f"Config file was not found: {selected_display_path}"]
        return validation
    except json.JSONDecodeError as exc:
        validation["status"] = "FAIL"
        validation["missing_required_fields"] = ["valid_json_config"]
        validation["warnings"] = [f"Config file is not valid JSON: {exc.msg}"]
        return validation

    if not isinstance(data, dict):
        validation["status"] = "FAIL"
        validation["missing_required_fields"] = ["json_object_config"]
        validation["warnings"] = ["Config file must contain a JSON object."]
        return validation

    missing_required = [field for field in required_fields if str(data.get(field, "")).strip() == ""]
    missing_optional = [field for field in optional_fields if str(data.get(field, "")).strip() == ""]
    validation["missing_required_fields"] = missing_required
    validation["missing_optional_fields"] = missing_optional
    validation["status"] = "PASS" if not missing_required else "FAIL"
    if missing_optional:
        validation["warnings"] = [f"Optional fields missing: {', '.join(missing_optional)}"]
    return validation


def _is_safe_report_device_segment(value: str) -> bool:
    text = str(value).strip()
    return bool(text) and Path(text).name == text and "/" not in text and "\\" not in text


def _count_check_statuses(checks: Dict[str, Any]) -> Dict[str, int]:
    return {
        "pass_count": sum(1 for status in checks.values() if status == "PASS"),
        "warn_count": sum(1 for status in checks.values() if status == "WARN"),
        "fail_count": sum(1 for status in checks.values() if status == "FAIL"),
        "skip_count": sum(1 for status in checks.values() if status == "SKIP"),
    }


def _build_delegated_day12_summary(project_root: Path, config_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "delegated_report": {},
        "delegated_result_summary": {},
    }
    try:
        config_data = json.loads(_wireguard_config_path(project_root, config_path).read_text(encoding="utf-8"))
        device_name = str(config_data.get("device_name", "")).strip() if isinstance(config_data, dict) else ""
    except (OSError, json.JSONDecodeError) as exc:
        result["delegated_report_parse_warning"] = f"Could not read selected WireGuard config for delegated report discovery: {exc}"
        return result

    if not _is_safe_report_device_segment(device_name):
        result["delegated_report_parse_warning"] = "Selected WireGuard config does not contain a safe device_name for report discovery."
        return result

    json_path = project_root / "reports" / device_name / DAY12_WIREGUARD_REPORT_JSON_NAME
    html_path = project_root / "reports" / device_name / DAY12_WIREGUARD_REPORT_HTML_NAME
    result["delegated_report"] = {
        "json": _relative_to_project(project_root, json_path),
        "html": _relative_to_project(project_root, html_path),
    }

    try:
        report_data = json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result["delegated_report_parse_warning"] = (
            "Delegated Day12 report JSON was not found after runner completion: "
            + _relative_to_project(project_root, json_path)
        )
        return result
    except (OSError, json.JSONDecodeError) as exc:
        result["delegated_report_parse_warning"] = f"Could not parse delegated Day12 report JSON: {exc}"
        return result

    if not isinstance(report_data, dict):
        result["delegated_report_parse_warning"] = "Delegated Day12 report JSON did not contain an object."
        return result

    checks = report_data.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    iperf_summary = report_data.get("iperf_summary", {})
    if not isinstance(iperf_summary, dict):
        iperf_summary = {}

    summary: Dict[str, Any] = {
        "result": report_data.get("overall_result", report_data.get("result", "UNKNOWN")),
        **_count_check_statuses(checks),
    }
    for source_key, output_key in (
        ("final_vpn_connectivity", "final_vpn_connectivity"),
        ("initial_handshake_seen", "initial_handshake_seen"),
        ("post_connectivity_handshake_seen", "post_connectivity_handshake_seen"),
    ):
        if source_key in checks:
            summary[output_key] = checks[source_key]
    for source_key, output_key in (
        ("forward_mbps", "iperf_forward_mbps"),
        ("reverse_mbps", "iperf_reverse_mbps"),
    ):
        if source_key in iperf_summary:
            summary[output_key] = iperf_summary[source_key]

    result["delegated_result_summary"] = summary
    return result


def _build_wireguard_runner_report(
    mode: str,
    result: str,
    project_root: Path,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
    message: str = "",
    delegated_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    validation = _wireguard_runner_config_validation(project_root, config_path)
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    delegated_summary = delegated_summary or {}
    warnings = list(validation["warnings"])
    if delegated_summary.get("delegated_report_parse_warning"):
        warnings.append(str(delegated_summary["delegated_report_parse_warning"]))
    live_guard_status = {
        "dry-run": "DRY-RUN: no live execution",
        "blocked": "BLOCKED: missing explicit --allow-live-wireguard",
        "guarded-live": "PASS: explicit --allow-live-wireguard provided",
    }.get(mode, "UNKNOWN")
    guardrails = {
        "dry_run_default": "PASS",
        "requires_allow_live_wireguard": "PASS",
        "subprocess_shell_false": "PASS",
        "forbidden_write_flags_blocked": "PASS",
        "secrets_masked": "PASS",
        "live_device_execution": "ENABLED" if mode == "guarded-live" else "BLOCKED",
    }
    return mask_secret_values(
        {
            "task_id": WIREGUARD_RUNNER_TASK_ID,
            "display_name": WIREGUARD_RUNNER_DISPLAY_NAME,
            "day": "Day18",
            "category": "vpn",
            "mode": mode,
            "result": result,
            "selected_config_path": selected_config_path,
            "live_guard_status": live_guard_status,
            "delegated_command_summary": _format_display_command(command),
            "validation_status": validation["status"],
            "safety_guardrail_status": guardrails,
            "missing_required_fields": validation["missing_required_fields"],
            "missing_optional_fields": validation["missing_optional_fields"],
            "warnings": warnings,
            "planned_steps": _wireguard_runner_planned_steps(run_iperf=run_iperf),
            "report_output_path": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
            "message": message,
            "timestamp": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            **delegated_summary,
        }
    )


def _write_wireguard_runner_html(report: Dict[str, Any], output_path: Path) -> None:
    safe_report = mask_secret_values(report)
    rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in safe_report.items()
        if key not in {
            "safety_guardrail_status",
            "planned_steps",
            "warnings",
            "delegated_report",
            "delegated_result_summary",
        }
    )
    guardrail_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in safe_report.get("safety_guardrail_status", {}).items()
    )
    planned_steps = "".join(f"<li>{html.escape(str(step))}</li>" for step in safe_report.get("planned_steps", []))
    warnings = "".join(f"<li>{html.escape(str(item))}</li>" for item in safe_report.get("warnings", [])) or "<li>None</li>"
    delegated_report = safe_report.get("delegated_report", {})
    if not isinstance(delegated_report, dict):
        delegated_report = {}
    delegated_summary = safe_report.get("delegated_result_summary", {})
    if not isinstance(delegated_summary, dict):
        delegated_summary = {}
    delegated_report_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in delegated_report.items()
    ) or "<tr><td colspan='2'>Not available</td></tr>"
    delegated_summary_keys = [
        "result",
        "final_vpn_connectivity",
        "initial_handshake_seen",
        "post_connectivity_handshake_seen",
        "iperf_forward_mbps",
        "iperf_reverse_mbps",
    ]
    delegated_summary_rows = "\n".join(
        f"<tr><td>{html.escape(key)}</td><td>{html.escape(str(delegated_summary[key]))}</td></tr>"
        for key in delegated_summary_keys
        if key in delegated_summary
    ) or "<tr><td colspan='2'>Not available</td></tr>"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(WIREGUARD_RUNNER_DISPLAY_NAME)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(WIREGUARD_RUNNER_DISPLAY_NAME)}</h1>
  <table><tbody>{rows}</tbody></table>
  <h2>Delegated Day12 Reports</h2>
  <table><tbody>{delegated_report_rows}</tbody></table>
  <h2>Delegated Day12 Summary</h2>
  <table><tbody>{delegated_summary_rows}</tbody></table>
  <h2>Safety Guardrails</h2>
  <table><tbody>{guardrail_rows}</tbody></table>
  <h2>Planned Steps</h2>
  <ol>{planned_steps}</ol>
  <h2>Warnings</h2>
  <ul>{warnings}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _write_wireguard_runner_report(project_root: Path, report: Dict[str, Any]) -> Tuple[Path, Path]:
    json_path = _wireguard_runner_report_path(project_root)
    html_path = _wireguard_runner_report_path(project_root, html_report=True)
    write_json_report(report, json_path)
    _write_wireguard_runner_html(report, html_path)
    return json_path, html_path


def _build_wireguard_runner_command(
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
    executable: str = sys.executable,
) -> List[str]:
    command = [
        executable,
        DAY12_WIREGUARD_SCRIPT,
        "--config",
        str(config_path),
    ]
    if run_iperf:
        command.extend(["--run-iperf", "--expect-connected"])
    command.append("--non-interactive")
    return command


def _validate_wireguard_runner_command(command: List[str], config_path: str = DAY12_WIREGUARD_CONFIG) -> None:
    forbidden_flags = {"--recreate-peer", "--apply-firewall-fixes"}
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        raise ValueError("WireGuard runner command must be a list of string arguments.")
    present_forbidden_flags = sorted(forbidden_flags.intersection(command))
    if present_forbidden_flags:
        raise ValueError(
            "WireGuard runner command contains forbidden live write flags: "
            + ", ".join(present_forbidden_flags)
        )
    required_parts = {DAY12_WIREGUARD_SCRIPT, "--config", str(config_path), "--non-interactive"}
    missing_parts = sorted(part for part in required_parts if part not in command)
    if missing_parts:
        raise ValueError("WireGuard runner command is missing required safety args: " + ", ".join(missing_parts))


def _print_wireguard_runner_dry_run(
    project_root: Path,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
) -> int:
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    _validate_wireguard_runner_command(command, config_path=config_path)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    report = _build_wireguard_runner_report("dry-run", "DRY-RUN", project_root, config_path=config_path, run_iperf=run_iperf)
    json_path, html_path = _write_wireguard_runner_report(project_root, report)
    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Primary command: {color_text('python network_lab.py --task wireguard-runner --dry-run', 'cyan', bold=True)}")
    print(f"Selected WireGuard config: {selected_config_path}")
    print()
    print(format_heading("Planned validation steps"))
    for step in report["planned_steps"]:
        print(f"  - {step}")
    print()
    print(format_heading("Safety guardrails"))
    print("  This is a live WireGuard validation workflow.")
    print("  Dry-run does not connect to devices.")
    print("  Dry-run does not start WireGuard, ping, iperf, or device config changes.")
    print("  Runner command is non-interactive and does not include --recreate-peer or --apply-firewall-fixes.")
    print("  Live execution requires explicit --allow-live-wireguard. Interactive menu execution also requires explicit confirmation.")
    print()
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} No live workflow was executed.")
    return 0


def _run_wireguard_runner(
    project_root: Path,
    dry_run: bool = False,
    allow_live_wireguard: bool = False,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
) -> int:
    if dry_run:
        return _print_wireguard_runner_dry_run(project_root, config_path=config_path, run_iperf=run_iperf)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    if not allow_live_wireguard:
        message = "WireGuard live execution requires explicit --allow-live-wireguard"
        report = _build_wireguard_runner_report(
            "blocked",
            "BLOCKED",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            message=message,
        )
        _write_wireguard_runner_report(project_root, report)
        print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
        print(f"Selected WireGuard config: {selected_config_path}")
        print(message)
        return 0

    validation = _wireguard_runner_config_validation(project_root, config_path)
    if validation["status"] == "FAIL":
        message = "WireGuard runner config validation failed before live execution."
        report = _build_wireguard_runner_report(
            "blocked",
            "BLOCKED",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            message=message,
        )
        _write_wireguard_runner_report(project_root, report)
        print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
        print(f"Selected WireGuard config: {selected_config_path}")
        print(message)
        return 2

    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    try:
        _validate_wireguard_runner_command(command, config_path=config_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print("Live WireGuard validation workflow.")
    print(f"Selected WireGuard config: {selected_config_path}")
    print(f"Executing command: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            shell=False,
            timeout=DAY12_WIREGUARD_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            f"{format_status('FAIL')} WireGuard runner timed out after "
            f"{DAY12_WIREGUARD_TIMEOUT_SECONDS} seconds."
        )
        return 124
    delegated_summary = _build_delegated_day12_summary(project_root, config_path)
    if result.returncode == 0:
        report = _build_wireguard_runner_report(
            "guarded-live",
            "PASS",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            delegated_summary=delegated_summary,
        )
        _write_wireguard_runner_report(project_root, report)
        print(f"{format_status('PASS')} WireGuard runner completed successfully.")
        return 0

    report = _build_wireguard_runner_report(
        "guarded-live",
        "FAIL",
        project_root,
        config_path=config_path,
        run_iperf=run_iperf,
        delegated_summary=delegated_summary,
    )
    _write_wireguard_runner_report(project_root, report)
    print(f"{format_status('FAIL')} WireGuard runner failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_wireguard_runner(
    project_root: Path,
    input_func: Any,
    config_path: str = DAY12_WIREGUARD_CONFIG,
) -> int:
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=False)
    try:
        _validate_wireguard_runner_command(command, config_path=config_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print("This is a live WireGuard validation workflow.")
    print(f"Selected WireGuard config: {selected_config_path}")
    print(f"Command to execute: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    print("Runner safety layer omits --recreate-peer and --apply-firewall-fixes.")
    try:
        confirmation = input_func("Confirm live WireGuard runner execution? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation != "y":
        print(f"{format_status('NOT_RUN')} WireGuard runner cancelled. No live workflow was executed.")
        return 0

    return _run_wireguard_runner(project_root, allow_live_wireguard=True, config_path=config_path, run_iperf=False)


def _wireguard_config_suggestions(project_root: Path) -> List[str]:
    suggestions = []
    seen = set()
    for path in sorted(project_root.glob("Set_WireguardVPN*_config.json")):
        if not path.is_file():
            continue
        name = path.name
        if name in seen:
            continue
        suggestions.append(name)
        seen.add(name)
    return sorted(suggestions, key=lambda name: (name == DAY12_WIREGUARD_CONFIG, name.lower()))


def _prompt_for_wireguard_config(
    project_root: Path,
    input_func: Any,
) -> Optional[str]:
    suggestions = _wireguard_config_suggestions(project_root)
    print(format_heading("WireGuard VPN validation"))
    print("Select a WireGuard config file for this run.")
    if suggestions:
        print("Suggestions:")
        for index, suggestion in enumerate(suggestions, start=1):
            print(f"  {index}. {suggestion}")
    else:
        print("No Set_WireguardVPN*_config.json files were found. Type a config path to continue.")

    try:
        selection = input_func("WireGuard config path or number [blank to cancel]: ").strip()
    except EOFError:
        selection = ""

    if not selection:
        print(f"{format_status('NOT_RUN')} WireGuard runner cancelled. No config was selected.")
        return None

    if selection.isdigit() and suggestions:
        selected_index = int(selection)
        if 1 <= selected_index <= len(suggestions):
            return suggestions[selected_index - 1]
        print(f"{format_status('UNKNOWN')} Invalid WireGuard config selection: {selection}")
        return None

    return selection


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
    print(format_heading("Network Lab Runner"))
    print("Select an option by number:")
    print("  1. List available tasks")
    print("  2. Generate report index")
    print("  3. Dry-run report index")
    print("  4. Open latest overview HTML if it exists")
    print("  5. Run multi-device baseline validation")
    print("  6. Run iperf3 performance test")
    print("  7. Run WireGuard VPN validation")
    print("  8. Show WireGuard summary command")
    print("  0. Exit")


def _print_interactive_action_complete() -> None:
    print()
    print(color_text(INTERACTIVE_ACTION_COMPLETE, "green", bold=True))


def run_interactive_menu(
    profile: Dict[str, Any],
    project_root: Path,
    profile_path: Path,
    wireguard_config: str = DAY12_WIREGUARD_CONFIG,
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
            print("Exiting Network Lab Runner.")
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
            selected_wireguard_config = _prompt_for_wireguard_config(project_root, read_input)
            if selected_wireguard_config is None:
                _print_interactive_action_complete()
                continue
            wireguard_exit_code = _confirm_and_run_wireguard_runner(
                project_root,
                read_input,
                config_path=selected_wireguard_config,
            )
            _print_interactive_action_complete()
            if wireguard_exit_code != 0:
                return wireguard_exit_code
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
        _print_task_list(verbose=args.verbose)
        return 0
    if args.report_index:
        return _run_report_visibility_index(root)
    if args.portfolio_finalize:
        return _run_portfolio_finalization(root)
    if args.task == "portfolio-finalize":
        return _run_portfolio_finalization(root)
    if args.task == "demo-flow":
        return _run_day24_demo_flow(root)

    profile_path = _resolve_project_path(root, args.profile)
    try:
        profile = load_lab_runner_profile(profile_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.interactive or not args.task:
        return run_interactive_menu(profile, root, profile_path, wireguard_config=args.wireguard_config)

    if args.task == "report-index":
        return _run_report_index(profile, root, profile_path, dry_run=args.dry_run)
    if args.task == "day4-baseline":
        return _run_day4_baseline(root, dry_run=args.dry_run)
    if args.task == "iperf3-performance":
        return _run_day8_performance(root, dry_run=args.dry_run)
    if args.task == DAY32_VRRP_PRECHECK_TASK_ID:
        return _run_day32_vrrp_precheck(root, dry_run=args.dry_run)
    if args.task == DAY33_VRRP_DRY_RUN_TASK_ID:
        return _run_day33_vrrp_dry_run(root)
    if args.task == DAY34_VRRP_STAGED_PLAN_TASK_ID:
        return _run_day34_vrrp_staged_plan(root)
    if args.task == DAY35_VRRP_FAILOVER_TASK_ID:
        return _run_day35_vrrp_failover_validation(root, dry_run=args.dry_run)
    if args.task == WIREGUARD_RUNNER_TASK_ALIAS:
        return _run_wireguard_runner(
            root,
            dry_run=args.dry_run,
            allow_live_wireguard=args.allow_live_wireguard,
            config_path=args.wireguard_config,
            run_iperf=args.run_iperf,
        )

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
