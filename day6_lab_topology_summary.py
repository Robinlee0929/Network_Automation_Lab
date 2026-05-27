import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_PROFILE = Path("topology_profiles") / "day6_lab_topology.json"
REPORT_JSON = Path("reports") / "day6_lab_topology_summary.json"
REPORT_HTML = Path("reports") / "day6_lab_topology_summary.html"
RESULT_FIELDS = ("overall_result", "overall_status", "result", "status")
CHECK_ITEM_FIELDS = (
    "checks",
    "check_results",
    "validation_results",
    "test_results",
    "results",
    "validations",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile-based multi-device lab topology summary report."
    )
    parser.add_argument(
        "--profile",
        default=str(DEFAULT_PROFILE),
        help="Path to topology profile JSON.",
    )
    return parser.parse_args()


def resolve_project_path(path: Path, project_root: Path = PROJECT_ROOT) -> Path:
    if path.is_absolute():
        return path
    return project_root / path


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def load_profile(profile_path: Path, project_root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    resolved = resolve_project_path(profile_path, project_root)
    profile = load_json(resolved)
    devices = profile.get("devices")
    if not isinstance(devices, list):
        raise ValueError(f"{resolved} must contain a devices list.")
    return profile


def normalize_result(report: Dict[str, Any]) -> str:
    for field in RESULT_FIELDS:
        value = report.get(field)
        if value is None:
            continue
        normalized = str(value).strip().upper()
        if normalized == "PASS":
            return "PASS"
        if normalized == "FAIL":
            return "FAIL"
    return "UNKNOWN"


def normalize_check_result(value: Any) -> str:
    normalized = str(value).strip().upper()
    if normalized in {"PASS", "FAIL", "WARNING", "SKIP"}:
        return normalized
    return "UNKNOWN"


def first_text_value(item: Dict[str, Any], fields: Tuple[str, ...], default: str = "") -> str:
    for field in fields:
        value = item.get(field)
        if value is not None and str(value).strip():
            return str(value)
    return default


def check_item_sources(report: Dict[str, Any]) -> List[Any]:
    sources: List[Any] = []
    for field in CHECK_ITEM_FIELDS:
        value = report.get(field)
        if isinstance(value, list):
            sources.append(value)

    summary = report.get("summary")
    if isinstance(summary, dict):
        summary_checks = summary.get("checks")
        if isinstance(summary_checks, list):
            sources.append(summary_checks)

    return sources


def normalize_check_items(report: Dict[str, Any]) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for source in check_item_sources(report):
        for index, item in enumerate(source, start=1):
            if isinstance(item, dict):
                name = first_text_value(
                    item,
                    ("name", "check", "check_name", "test_name", "item", "title"),
                    f"check_{index}",
                )
                result = normalize_check_result(
                    first_text_value(item, ("result", "status", "outcome"), "UNKNOWN")
                )
                message = first_text_value(
                    item,
                    ("message", "detail", "description", "reason", "actual"),
                    "",
                )
                category = first_text_value(
                    item,
                    ("category", "group", "section", "type"),
                    "general",
                )
            else:
                name = str(item).strip() or f"check_{index}"
                result = "UNKNOWN"
                message = ""
                category = "general"

            items.append(
                {
                    "name": name,
                    "result": result,
                    "message": message,
                    "category": category,
                }
            )
    return items


def failed_checks(report: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    for check in normalize_check_items(report):
        if check["result"] == "FAIL":
            failures.append(check["name"])
    return failures


def source_report_type(report: Dict[str, Any], report_path: Path) -> str:
    for field in ("source_report_type", "report_type", "validation_type"):
        value = report.get(field)
        if value:
            return str(value)

    path_text = str(report_path).replace("\\", "/").lower()
    if "switch_topology_report" in path_text or "day5_switch_topology_report" in path_text:
        return "cisco_switch_topology"
    if "day4_baseline_validation" in path_text:
        return "mikrotik_day4_baseline"
    return "json_report"


def summarize_device(
    device: Dict[str, Any],
    project_root: Path = PROJECT_ROOT,
) -> Dict[str, Any]:
    report_path_text = str(device.get("report_path", "")).strip()
    report_path = resolve_project_path(Path(report_path_text), project_root)
    report_found = report_path.exists()
    normalized = "UNKNOWN"
    failures: List[str] = []
    check_items: List[Dict[str, str]] = []
    source_type = "missing_report"
    read_error: Optional[str] = None

    if report_found:
        try:
            report = load_json(report_path)
            normalized = normalize_result(report)
            failures = failed_checks(report)
            check_items = normalize_check_items(report)
            source_type = source_report_type(report, Path(report_path_text))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            read_error = f"{type(error).__name__}: {error}"
            source_type = "unreadable_json_report"

    summary = {
        "device_name": str(device.get("device_name", "")),
        "device_type": str(device.get("device_type", "")),
        "role": str(device.get("role", "")),
        "management_ip": str(device.get("management_ip", "")),
        "report_path": report_path_text,
        "required": bool(device.get("required", False)),
        "report_found": report_found,
        "normalized_result": normalized,
        "failed_checks": failures,
        "check_items": check_items,
        "source_report_type": source_type,
    }
    if read_error:
        summary["read_error"] = read_error
    return summary


def evaluate_overall(devices: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    result = "PASS"

    for device in devices:
        name = device["device_name"] or "unnamed_device"
        required = bool(device["required"])
        found = bool(device["report_found"])
        normalized = device["normalized_result"]

        if required and not found:
            reasons.append(f"Required device report missing: {name}")
            result = "FAIL"
            continue
        if required and normalized == "FAIL":
            reasons.append(f"Required device failed: {name}")
            result = "FAIL"
            continue
        if not required and not found:
            reasons.append(f"Optional device report missing: {name}")
            if result != "FAIL":
                result = "WARNING"
            continue
        if normalized == "UNKNOWN":
            reasons.append(f"Device result unknown: {name}")
            if result != "FAIL":
                result = "WARNING"
            continue
        if not required and normalized == "FAIL":
            reasons.append(f"Optional device failed: {name}")
            if result != "FAIL":
                result = "WARNING"

    return result, reasons


def build_summary_report(
    profile: Dict[str, Any],
    profile_path: Path,
    project_root: Path = PROJECT_ROOT,
) -> Dict[str, Any]:
    devices = [
        summarize_device(device, project_root)
        for device in profile.get("devices", [])
        if isinstance(device, dict)
    ]
    overall, reasons = evaluate_overall(devices)
    return {
        "topology_name": str(profile.get("topology_name", "")),
        "profile_path": str(profile_path),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall_result": overall,
        "reasons": reasons,
        "total_devices": len(devices),
        "required_devices": sum(1 for device in devices if device["required"]),
        "optional_devices": sum(1 for device in devices if not device["required"]),
        "pass_count": sum(1 for device in devices if device["normalized_result"] == "PASS"),
        "fail_count": sum(1 for device in devices if device["normalized_result"] == "FAIL"),
        "unknown_count": sum(1 for device in devices if device["normalized_result"] == "UNKNOWN"),
        "missing_report_count": sum(1 for device in devices if not device["report_found"]),
        "devices": devices,
    }


def status_badge(status: str) -> str:
    normalized = str(status).lower()
    if normalized not in {"pass", "fail", "warning", "skip", "unknown"}:
        normalized = "unknown"
    return f'<span class="badge {normalized}">{html.escape(str(status))}</span>'


def build_html_report(report: Dict[str, Any]) -> str:
    device_rows = []
    topology_nodes = []
    detail_sections = []
    for device in report["devices"]:
        failed = ", ".join(device["failed_checks"]) or "None"
        found = "Found" if device["report_found"] else "Missing"
        required = "Required" if device["required"] else "Optional"
        node_class = str(device["normalized_result"]).lower()
        device_rows.append(
            "<tr>"
            f"<td>{html.escape(device['device_name'])}</td>"
            f"<td>{html.escape(device['device_type'])}</td>"
            f"<td>{html.escape(device['role'])}</td>"
            f"<td><code>{html.escape(device['management_ip'])}</code></td>"
            f"<td><code>{html.escape(device['report_path'])}</code></td>"
            f"<td>{html.escape(found)}</td>"
            f"<td>{status_badge(device['normalized_result'])}</td>"
            f"<td>{html.escape(failed)}</td>"
            f"<td>{html.escape(device['source_report_type'])}</td>"
            "</tr>"
        )
        topology_nodes.append(
            f"""
    <article class="node {html.escape(node_class)}">
      <div class="node-head">
        <div>
          <div class="node-role">{html.escape(device['role'])}</div>
          <h3>{html.escape(device['device_name'])}</h3>
        </div>
        {status_badge(device['normalized_result'])}
      </div>
      <dl>
        <div><dt>Type</dt><dd>{html.escape(device['device_type'])}</dd></div>
        <div><dt>Management</dt><dd><code>{html.escape(device['management_ip'])}</code></dd></div>
        <div><dt>Report</dt><dd>{html.escape(found)} / {html.escape(required)}</dd></div>
        <div><dt>Source</dt><dd>{html.escape(device['source_report_type'])}</dd></div>
      </dl>
    </article>
"""
        )
        check_rows = []
        for item in device.get("check_items", []):
            check_rows.append(
                "<tr>"
                f"<td>{html.escape(item['name'])}</td>"
                f"<td>{status_badge(item['result'])}</td>"
                f"<td>{html.escape(item['message'])}</td>"
                f"<td>{html.escape(item['category'])}</td>"
                "</tr>"
            )
        if not check_rows:
            check_rows.append(
                '<tr><td colspan="4" class="empty-detail">'
                "No detailed check items found in source report."
                "</td></tr>"
            )
        detail_sections.append(
            f"""
    <section class="device-detail">
      <div class="detail-head">
        <h3>{html.escape(device['device_name'])}</h3>
        {status_badge(device['normalized_result'])}
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Check Item</th><th>Result</th><th>Message</th><th>Category</th></tr>
          </thead>
          <tbody>{''.join(check_rows)}</tbody>
        </table>
      </div>
    </section>
"""
        )

    reasons = "".join(f"<li>{html.escape(reason)}</li>" for reason in report["reasons"])
    if not reasons:
        reasons = "<li>No warnings or failures.</li>"

    if report["overall_result"] == "PASS":
        result_copy = "All required device reports are present and passing."
    elif report["overall_result"] == "WARNING":
        result_copy = "The lab is usable, with items that need review."
    else:
        result_copy = "One or more required lab checks need attention."

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 6 Lab Topology Summary</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --panel: #ffffff;
      --text: #172033;
      --muted: #637083;
      --line: #d8e0ea;
      --ink: #111827;
      --accent: #2563eb;
      --accent-soft: #dbeafe;
      --pass: #147a3d;
      --pass-bg: #e8f6ee;
      --fail: #b42318;
      --fail-bg: #fdecec;
      --warning: #8a5a00;
      --warning-bg: #fff4d8;
      --unknown: #475467;
      --unknown-bg: #eef2f6;
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
      max-width: 1200px;
      margin: 0 auto;
      padding: 28px 20px 52px;
    }}
    .hero {{
      background: var(--ink);
      color: #ffffff;
      border-radius: 8px;
      padding: 28px;
      margin-bottom: 20px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.6fr) minmax(260px, 0.8fr);
      gap: 24px;
      align-items: end;
    }}
    .eyebrow {{
      color: #bfdbfe;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 34px;
      line-height: 1.15;
    }}
    h2 {{
      margin: 30px 0 12px;
      font-size: 18px;
    }}
    h3 {{
      margin: 4px 0 0;
      font-size: 18px;
    }}
    .meta {{
      color: #d1d5db;
      margin-top: 14px;
    }}
    .hero-panel {{
      background: rgba(255, 255, 255, .08);
      border: 1px solid rgba(255, 255, 255, .18);
      border-radius: 8px;
      padding: 18px;
    }}
    .hero-panel .label {{
      color: #bfdbfe;
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 700;
    }}
    .hero-panel .result {{
      margin: 8px 0 10px;
      font-size: 30px;
      font-weight: 800;
    }}
    .hero-panel p {{
      margin: 0;
      color: #e5e7eb;
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
      font-size: 22px;
      font-weight: 700;
      margin-top: 4px;
    }}
    .topology {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-top: 12px;
    }}
    .node {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--unknown);
      border-radius: 8px;
      padding: 16px;
    }}
    .node.pass {{
      border-left-color: var(--pass);
    }}
    .node.fail {{
      border-left-color: var(--fail);
    }}
    .node.warning, .node.unknown {{
      border-left-color: var(--warning);
    }}
    .node-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
      margin-bottom: 14px;
    }}
    .node-role {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    dl {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 0;
    }}
    dt {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 2px;
    }}
    dd {{
      margin: 0;
      font-weight: 600;
      overflow-wrap: anywhere;
    }}
    .reasons {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 18px;
    }}
    .reasons ul {{
      margin: 0;
      padding-left: 20px;
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
      min-width: 64px;
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
    .badge.warning {{
      background: var(--warning-bg);
      color: var(--warning);
    }}
    .badge.skip {{
      background: var(--warning-bg);
      color: var(--warning);
    }}
    .badge.unknown {{
      background: var(--unknown-bg);
      color: var(--unknown);
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
      font-size: 13px;
    }}
    .table-wrap {{
      overflow-x: auto;
      border-radius: 8px;
    }}
    .device-detail {{
      margin-bottom: 18px;
    }}
    .detail-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 12px 0 8px;
    }}
    .empty-detail {{
      color: var(--muted);
      font-style: italic;
    }}
    @media (max-width: 760px) {{
      .hero-grid {{
        grid-template-columns: 1fr;
      }}
      h1 {{
        font-size: 28px;
      }}
      dl {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <div class="hero-grid">
      <div>
        <div class="eyebrow">Network Automation Test Platform</div>
        <h1>Profile-Based Multi-Device Lab Topology</h1>
        <div class="meta">
          Topology: <strong>{html.escape(report['topology_name'])}</strong><br>
          Profile: <code>{html.escape(report['profile_path'])}</code><br>
          Generated: {html.escape(report['generated_at'])}
        </div>
      </div>
      <div class="hero-panel">
        <div class="label">Lab Health</div>
        <div class="result">{status_badge(report['overall_result'])}</div>
        <p>{html.escape(result_copy)}</p>
      </div>
    </div>
  </section>
  <div class="summary">
    <div class="metric"><div class="label">Overall</div><div class="value">{status_badge(report['overall_result'])}</div></div>
    <div class="metric"><div class="label">Devices</div><div class="value">{report['total_devices']}</div></div>
    <div class="metric"><div class="label">Required</div><div class="value">{report['required_devices']}</div></div>
    <div class="metric"><div class="label">Optional</div><div class="value">{report['optional_devices']}</div></div>
    <div class="metric"><div class="label">PASS</div><div class="value">{report['pass_count']}</div></div>
    <div class="metric"><div class="label">FAIL</div><div class="value">{report['fail_count']}</div></div>
    <div class="metric"><div class="label">UNKNOWN</div><div class="value">{report['unknown_count']}</div></div>
    <div class="metric"><div class="label">Missing</div><div class="value">{report['missing_report_count']}</div></div>
  </div>
  <h2>Topology Nodes</h2>
  <section class="topology">{''.join(topology_nodes)}</section>
  <h2>Review Notes</h2>
  <section class="reasons"><ul>{reasons}</ul></section>
  <h2>Evidence Matrix</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>Device</th><th>Type</th><th>Role</th><th>Management IP</th><th>Report Path</th><th>Found</th><th>Result</th><th>Failed Checks</th><th>Source Type</th></tr>
      </thead>
      <tbody>{''.join(device_rows)}</tbody>
    </table>
  </div>
  <h2>Detailed Test Evidence</h2>
  {''.join(detail_sections)}
</main>
</body>
</html>
"""


def write_reports(
    report: Dict[str, Any],
    project_root: Path = PROJECT_ROOT,
) -> Tuple[Path, Path]:
    json_path = resolve_project_path(REPORT_JSON, project_root)
    html_path = resolve_project_path(REPORT_HTML, project_root)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with html_path.open("w", encoding="utf-8") as file:
        file.write(build_html_report(report))
    return json_path, html_path


def run(profile_path: Path, project_root: Path = PROJECT_ROOT) -> Tuple[Dict[str, Any], Path, Path]:
    resolved_profile_path = resolve_project_path(profile_path, project_root)
    profile = load_profile(profile_path, project_root)
    report = build_summary_report(profile, profile_path, project_root)
    report["profile_path"] = str(resolved_profile_path)
    json_path, html_path = write_reports(report, project_root)
    report["report_paths"] = {"json": str(json_path), "html": str(html_path)}
    return report, json_path, html_path


def print_summary(report: Dict[str, Any], json_path: Path, html_path: Path) -> None:
    print()
    print("=" * 72)
    print("Day 6 Lab Topology Summary")
    print("=" * 72)
    print(f"Topology: {report['topology_name']}")
    print(f"Overall Result: {report['overall_result']}")
    print("-" * 72)
    for device in report["devices"]:
        found = "found" if device["report_found"] else "missing"
        print(
            f"{device['device_name']:<24} "
            f"{device['normalized_result']:<8} "
            f"{found:<7} "
            f"{device['report_path']}"
        )
    if report["reasons"]:
        print("-" * 72)
        for reason in report["reasons"]:
            print(f"- {reason}")
    print("-" * 72)
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
    print("=" * 72)


def main() -> int:
    try:
        args = parse_args()
        report, json_path, html_path = run(Path(args.profile), PROJECT_ROOT)
        print_summary(report, json_path, html_path)
        return 1 if report["overall_result"] == "FAIL" else 0
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(f"ERROR: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
