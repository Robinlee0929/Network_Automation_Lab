import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from flask import Flask, abort, redirect, render_template, send_from_directory, url_for
except ImportError:  # pragma: no cover - exercised by environments without Flask.
    Flask = None  # type: ignore[assignment]
    abort = None  # type: ignore[assignment]
    redirect = None  # type: ignore[assignment]
    render_template = None  # type: ignore[assignment]
    send_from_directory = None  # type: ignore[assignment]
    url_for = None  # type: ignore[assignment]

from dashboard_command_runner import (
    CommandUnavailableError,
    build_command_registry,
    execute_registered_command,
    list_execution_logs,
    load_execution_log,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_EXECUTION_LOGS_DIR = DEFAULT_REPORTS_DIR / "execution_logs"

STATUS_FIELDS = (
    "overall_result",
    "overall_status",
    "result",
    "status",
    "passed",
    "pass",
    "success",
)
PASS_VALUES = {"PASS", "PASSED", "OK", "TRUE"}
FAIL_VALUES = {"FAIL", "FAILED", "ERROR", "FALSE"}
WARNING_VALUES = {"WARN", "WARNING"}


@dataclass
class ReportEntry:
    device: str
    filename: str
    report_type: str
    file_type: str
    status: str
    relative_path: str
    html_relative_path: Optional[str]
    modified_at: str


DAY12_REPORT_JSON = "day12_wireguard_vpn_automation_report.json"
DAY12_REPORT_HTML = "day12_wireguard_vpn_automation_report.html"


def contains_unredacted_private_key(value: Any) -> bool:
    if isinstance(value, str):
        for line in value.splitlines():
            if "PrivateKey" not in line:
                continue
            if "PrivateKey = REDACTED" not in line and "PrivateKey=REDACTED" not in line:
                return True
        return False
    if isinstance(value, dict):
        return any(contains_unredacted_private_key(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_unredacted_private_key(item) for item in value)
    return False


def safe_day12_value(value: Any, fallback: str = "Not found") -> str:
    if value in (None, ""):
        return fallback
    text = str(value)
    if contains_unredacted_private_key(text):
        return "PrivateKey: REDACTED"
    return text


def dashboard_wireguard_label(value: Any, fallback: str = "Not found") -> str:
    text = safe_day12_value(value, fallback)
    return re.sub("day12", "vpn", text, flags=re.IGNORECASE)


def normalize_status(value: Any) -> str:
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if value is None:
        return "UNKNOWN"
    normalized = str(value).strip().upper()
    if normalized in PASS_VALUES:
        return "PASS"
    if normalized in FAIL_VALUES:
        return "FAIL"
    if normalized in WARNING_VALUES:
        return "WARNING"
    return "UNKNOWN"


def _iter_status_candidates(data: Any) -> Iterable[Any]:
    if isinstance(data, dict):
        for field in STATUS_FIELDS:
            if field in data:
                yield data[field]
        for value in data.values():
            yield from _iter_status_candidates(value)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_status_candidates(item)


def parse_report_status(json_path: Path) -> str:
    try:
        with json_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        return "MALFORMED"
    except OSError:
        return "UNKNOWN"

    for candidate in _iter_status_candidates(data):
        status = normalize_status(candidate)
        if status != "UNKNOWN":
            return status
    return "UNKNOWN"


def classify_report_type(filename_or_path: Any) -> str:
    name = Path(filename_or_path).name.lower()
    path_text = str(filename_or_path).lower()
    if "day2" in name or "auto_setup" in name:
        return "Day2 auto setup"
    if "day3" in name or "post" in name:
        return "Day3 validation"
    if "day4" in name or "baseline" in name:
        return "Day4 baseline"
    if "day5" in name or "switch_topology" in name or "cisco" in path_text:
        return "Day5 Cisco topology"
    if "day6" in name or "lab_topology_summary" in name:
        return "Day6 lab topology summary"
    if "day8" in name or "iperf3" in name:
        return "Day8 iperf3 performance"
    if "day9" in name or "performance_regression" in path_text:
        return "Day9 performance regression"
    if "day12" in name or "wireguard_vpn_automation" in name:
        return "WireGuard VPN automation"
    return "Unknown report"


def _relative_report_path(path: Path, reports_dir: Path) -> str:
    return path.relative_to(reports_dir).as_posix()


def _device_name(path: Path, reports_dir: Path) -> str:
    relative_parts = path.relative_to(reports_dir).parts
    return relative_parts[0] if len(relative_parts) > 1 else "reports"


def _is_excluded_report_path(path: Path, reports_dir: Path) -> bool:
    relative_parts = path.relative_to(reports_dir).parts
    return bool(relative_parts) and relative_parts[0].lower() == "backup"


def discover_reports(reports_dir: Path) -> List[ReportEntry]:
    reports_dir = Path(reports_dir)
    if not reports_dir.exists() or not reports_dir.is_dir():
        return []

    files = sorted(
        [
            path
            for path in reports_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".json", ".html"}
            and not _is_excluded_report_path(path, reports_dir)
        ],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    html_by_stem = {
        _relative_report_path(path, reports_dir): path
        for path in files
        if path.suffix.lower() == ".html"
    }
    html_by_stem = {
        str(Path(relative).with_suffix("")): path
        for relative, path in html_by_stem.items()
    }
    json_status_by_stem = {
        str(Path(_relative_report_path(path, reports_dir)).with_suffix("")): parse_report_status(path)
        for path in files
        if path.suffix.lower() == ".json"
    }

    entries: List[ReportEntry] = []
    for path in files:
        relative_path = _relative_report_path(path, reports_dir)
        stem_key = str(Path(relative_path).with_suffix(""))
        matching_html = html_by_stem.get(stem_key)
        html_relative_path = (
            _relative_report_path(matching_html, reports_dir)
            if matching_html is not None
            else None
        )
        if path.suffix.lower() == ".html":
            html_relative_path = relative_path

        modified_at = datetime.fromtimestamp(path.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        entries.append(
            ReportEntry(
                device=_device_name(path, reports_dir),
                filename=path.name,
                report_type=classify_report_type(path),
                file_type=path.suffix.lower().lstrip(".").upper(),
                status=parse_report_status(path)
                if path.suffix.lower() == ".json"
                else json_status_by_stem.get(stem_key, "UNKNOWN"),
                relative_path=relative_path,
                html_relative_path=html_relative_path,
                modified_at=modified_at,
            )
        )
    return entries


def build_summary_cards(entries: List[ReportEntry]) -> List[Dict[str, Any]]:
    categories = [
        ("MikroTik baseline", ("Day4 baseline", "Day3 validation", "Day2 auto setup")),
        ("Cisco topology", ("Day5 Cisco topology",)),
        ("Lab topology summary", ("Day6 lab topology summary",)),
        ("iperf3 performance", ("Day8 iperf3 performance",)),
        ("Performance regression", ("Day9 performance regression",)),
        ("WireGuard VPN", ("WireGuard VPN automation",)),
    ]
    cards = []
    for title, report_types in categories:
        matches = [entry for entry in entries if entry.report_type in report_types]
        html_entry = next((entry for entry in matches if entry.html_relative_path), None)
        status_entry = next(
            (entry for entry in matches if entry.status != "UNKNOWN"), None
        )
        cards.append(
            {
                "title": title,
                "status": status_entry.status if status_entry else "UNKNOWN",
                "report": html_entry,
                "missing": not matches,
            }
        )
    return cards


def build_day12_dashboard_summaries(reports_dir: Path) -> List[Dict[str, Any]]:
    reports_dir = Path(reports_dir)
    if not reports_dir.exists():
        return []

    summaries: List[Dict[str, Any]] = []
    for json_path in sorted(reports_dir.rglob(DAY12_REPORT_JSON)):
        if _is_excluded_report_path(json_path, reports_dir):
            continue
        try:
            report = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if contains_unredacted_private_key(report):
            report = dict(report)
            report["sanitized_client_config_summary"] = "PrivateKey: REDACTED"

        relative_json = _relative_report_path(json_path, reports_dir)
        html_path = json_path.with_name(DAY12_REPORT_HTML)
        html_relative_path = (
            _relative_report_path(html_path, reports_dir) if html_path.exists() else None
        )
        checks = report.get("checks", {}) if isinstance(report.get("checks"), dict) else {}
        wireguard = (
            report.get("wireguard_summary", {})
            if isinstance(report.get("wireguard_summary"), dict)
            else {}
        )
        iperf = (
            report.get("iperf_summary", {})
            if isinstance(report.get("iperf_summary"), dict)
            else {}
        )
        sanitized_summary = safe_day12_value(
            report.get("sanitized_client_config_summary", ""), ""
        )
        summaries.append(
            {
                "device_name": safe_day12_value(report.get("device_name"), _device_name(json_path, reports_dir)),
                "device_folder": _device_name(json_path, reports_dir),
                "overall_result": normalize_status(report.get("overall_result")),
                "interface_name": dashboard_wireguard_label(wireguard.get("interface_name")),
                "peer_name": dashboard_wireguard_label(wireguard.get("peer_name")),
                "client_address": dashboard_wireguard_label(wireguard.get("client_address")),
                "exported_config_path": dashboard_wireguard_label(wireguard.get("exported_config_path")),
                "handshake_status": dashboard_wireguard_label(checks.get("handshake_seen")),
                "ping_lan_gateway": dashboard_wireguard_label(checks.get("ping_lan_gateway")),
                "ping_lan_host": dashboard_wireguard_label(checks.get("ping_lan_host")),
                "tcp_5201": dashboard_wireguard_label(checks.get("tcp_5201_reachable")),
                "iperf_forward_mbps": dashboard_wireguard_label(iperf.get("forward_mbps"), "Not run"),
                "iperf_reverse_mbps": dashboard_wireguard_label(iperf.get("reverse_mbps"), "Not run"),
                "json_relative_path": relative_json,
                "html_relative_path": html_relative_path,
                "sanitized_client_config_summary": sanitized_summary,
            }
        )
    return summaries


def command_examples() -> List[Dict[str, str]]:
    return [
        {"title": "Run all tests", "command": "python -m pytest"},
        {
            "title": "Day4 multi-device baseline",
            "command": "python mikrotik_day4_multi_device_baseline.py",
        },
        {
            "title": "Day5 Cisco validation",
            "command": "python cisco_topology_validation.py",
        },
        {"title": "Day6 topology summary", "command": "python topology_summary.py"},
        {
            "title": "Day8 iperf3 WAN to LAN performance",
            "command": (
                "python performance_test.py --direction WAN_TO_LAN "
                "--router-wan-ip <ROUTER_WAN_IP> --lan-server-ip <LAN_SERVER_IP>"
            ),
        },
        {
            "title": "Day8 iperf3 LAN to WAN performance",
            "command": (
                "python performance_test.py --direction LAN_TO_WAN "
                "--router-wan-ip <ROUTER_WAN_IP> --lan-server-ip <LAN_SERVER_IP>"
            ),
        },
        {
            "title": "Day9 performance regression",
            "command": (
                "python performance_regression.py --device-name <DEVICE_NAME> "
                "--direction LAN_TO_WAN_DNAT_REPLY "
                "--router-wan-ip <ROUTER_WAN_IP> --lan-server-ip <LAN_SERVER_IP> "
                "--threshold-mbps 800"
            ),
        },
    ]


def ai_review_checklist() -> List[Dict[str, str]]:
    return [
        {
            "category": "Command safety",
            "item": "Allowlist-only execution",
            "expected": "Dashboard can run only registered command IDs; it must not accept arbitrary shell text.",
            "evidence": "dashboard_command_runner.py build_command_registry(); /commands/<command_id>/run rejects unknown IDs.",
        },
        {
            "category": "Command safety",
            "item": "No direct device operations",
            "expected": "Dashboard must not collect passwords, open SSH sessions, apply router/switch config, reboot, reset, or modify firewall/NAT.",
            "evidence": "Allowed commands are local pytest/report workflows only; Day9 lab workflow is listed but disabled.",
        },
        {
            "category": "Command safety",
            "item": "No shell injection surface",
            "expected": "Commands should run with argument lists and shell=False.",
            "evidence": "dashboard_command_runner.py execute_command() uses subprocess.run(command.argv, shell=False).",
        },
        {
            "category": "Command safety",
            "item": "Timeout handling",
            "expected": "Long-running commands should finish, fail, or be logged as TIMEOUT without crashing Flask.",
            "evidence": "CommandSpec.timeout_seconds and subprocess.TimeoutExpired handling write TIMEOUT logs.",
        },
        {
            "category": "Dashboard behavior",
            "item": "Commands page separates command types",
            "expected": "Test commands, report/local workflows, and disabled manual lab workflows should be visibly distinct.",
            "evidence": "/commands shows category badges and effect notes for each registered command.",
        },
        {
            "category": "Dashboard behavior",
            "item": "Day9 real lab regression is not one-click",
            "expected": "Day9 performance_regression.py should not run from the dashboard without explicit lab parameters.",
            "evidence": "performance_regression command is available when script exists but disabled with a lab-parameter reason.",
        },
        {
            "category": "Report behavior",
            "item": "Topology summary scope is clear",
            "expected": "Rebuild Day6 topology summary should update Day6 summary reports only and not rerun Day8 or Day9 tests.",
            "evidence": "topology_summary effect text names reports/day6_lab_topology_summary.json/.html and says it does not rerun Day8 or Day9.",
        },
        {
            "category": "Execution logs",
            "item": "Structured JSON log is saved",
            "expected": "Every execution should write a JSON log with status, argv, timestamps, duration, stdout, stderr, exit code, and working directory.",
            "evidence": "reports/execution_logs/<log_id>.json; /commands/logs/<log_id> detail page.",
        },
        {
            "category": "Execution logs",
            "item": "Local system time is used",
            "expected": "New execution logs should use local system time instead of UTC Z timestamps.",
            "evidence": "dashboard_command_runner.py _local_timestamp(); log detail Started/Finished fields.",
        },
        {
            "category": "Testing",
            "item": "Automated checks cover Day11",
            "expected": "Tests should verify registry behavior, unknown command rejection, log writing, failures, timeouts, and Flask routes.",
            "evidence": "tests/test_dashboard_command_runner.py and tests/test_dashboard_app.py.",
        },
        {
            "category": "WireGuard VPN safety",
            "item": "Exported config stays local",
            "expected": "Exported .conf files should stay under ignored exports/ and must not be committed.",
            "evidence": ".gitignore includes exports/ and *.conf; the dashboard shows only the exported path.",
        },
        {
            "category": "WireGuard VPN safety",
            "item": "Reports and dashboard redact PrivateKey",
            "expected": "Reports and dashboard must never render a real WireGuard PrivateKey or full .conf content.",
            "evidence": "WireGuard VPN reports use PrivateKey = REDACTED; dashboard_app.py contains an unredacted PrivateKey guard.",
        },
        {
            "category": "WireGuard VPN safety",
            "item": "Dashboard does not read exports/wireguard",
            "expected": "Dashboard should read WireGuard VPN JSON reports only and should not open exported .conf files.",
            "evidence": "The WireGuard VPN summary builder reads report JSON files only.",
        },
        {
            "category": "WireGuard VPN safety",
            "item": "Filename and RouterOS command safety",
            "expected": "Filename is sanitized, RouterOS commands are allowlisted, peer recreation and firewall fixes require explicit confirmation or flags.",
            "evidence": "WireGuard VPN automation validates filenames, allowlists RouterOS commands, and gates peer/firewall changes.",
        },
        {
            "category": "WireGuard VPN subprocess safety",
            "item": "Local commands are allowlisted and timed",
            "expected": "ping, Test-NetConnection, and iperf3 should run with shell=False and timeouts.",
            "evidence": "Local subprocess builders return argument lists; run_subprocess() uses subprocess.run(..., shell=False, timeout=...).",
        },
        {
            "category": "WireGuard VPN testing",
            "item": "Secret and lab validation coverage exists",
            "expected": "Tests should cover PrivateKey leak handling and real lab evidence should validate tunnel, LAN reachability, TCP 5201, and iperf3 throughput.",
            "evidence": "Automated tests cover PrivateKey safety; lab report evidence shows overall_result PASS.",
        },
    ]


def create_app(
    reports_dir: Optional[Path] = None,
    execution_logs_dir: Optional[Path] = None,
) -> Flask:
    if Flask is None:
        raise RuntimeError(
            "Flask is required for the Day10 dashboard. Install it with: pip install flask"
        )

    app = Flask(__name__)
    app.config["REPORTS_DIR"] = Path(reports_dir) if reports_dir else DEFAULT_REPORTS_DIR
    app.config["EXECUTION_LOGS_DIR"] = (
        Path(execution_logs_dir)
        if execution_logs_dir
        else DEFAULT_EXECUTION_LOGS_DIR
    )

    @app.route("/")
    def home():
        entries = discover_reports(app.config["REPORTS_DIR"])
        return render_template(
            "dashboard_home.html",
            summary_cards=build_summary_cards(entries),
            description=(
                "A Python-based network automation and validation lab for "
                "MikroTik RouterOS, Cisco switch topology checks, iperf3 "
                "performance testing, regression checks, and local report "
                "visualization."
            ),
        )

    @app.route("/reports")
    def reports():
        entries = discover_reports(app.config["REPORTS_DIR"])
        grouped: Dict[str, List[ReportEntry]] = {}
        for entry in entries:
            if entry.report_type == "WireGuard VPN automation":
                continue
            grouped.setdefault(entry.device, []).append(entry)
        return render_template(
            "dashboard_reports.html",
            grouped_reports=grouped,
            day12_summaries=build_day12_dashboard_summaries(app.config["REPORTS_DIR"]),
            reports_exist=app.config["REPORTS_DIR"].exists(),
        )

    @app.route("/commands")
    def commands():
        registry = build_command_registry(PROJECT_ROOT)
        logs = list_execution_logs(app.config["EXECUTION_LOGS_DIR"])
        return render_template(
            "dashboard_commands.html",
            commands=list(registry.values()),
            manual_commands=command_examples(),
            recent_logs=logs[:5],
        )

    @app.post("/commands/<command_id>/run")
    def run_command(command_id: str):
        registry = build_command_registry(PROJECT_ROOT)
        try:
            log = execute_registered_command(
                registry,
                command_id,
                app.config["EXECUTION_LOGS_DIR"],
            )
        except (KeyError, CommandUnavailableError):
            abort(404)
        return redirect(url_for("command_log_detail", log_id=log["log_id"]))

    @app.route("/commands/logs")
    def command_logs():
        return render_template(
            "dashboard_command_logs.html",
            logs=list_execution_logs(app.config["EXECUTION_LOGS_DIR"]),
        )

    @app.route("/commands/logs/<log_id>")
    def command_log_detail(log_id: str):
        log = load_execution_log(app.config["EXECUTION_LOGS_DIR"], log_id)
        if log is None:
            abort(404)
        return render_template("dashboard_command_log.html", log=log)

    @app.route("/ai-checklist")
    def ai_checklist():
        return render_template(
            "dashboard_ai_checklist.html",
            checklist=ai_review_checklist(),
        )

    @app.route("/reports/open/<path:report_path>")
    def open_report(report_path: str):
        reports_root = app.config["REPORTS_DIR"].resolve()
        requested = (reports_root / report_path).resolve()
        try:
            requested.relative_to(reports_root)
        except ValueError:
            abort(404)
        if requested.suffix.lower() != ".html" or not requested.is_file():
            abort(404)
        safe_relative_path = requested.relative_to(reports_root).as_posix()
        return send_from_directory(str(reports_root), safe_relative_path)

    @app.route("/reports/wireguard-vpn/<path:device_name>")
    def open_wireguard_vpn_report(device_name: str):
        reports_root = app.config["REPORTS_DIR"].resolve()
        requested = (reports_root / device_name / DAY12_REPORT_HTML).resolve()
        try:
            requested.relative_to(reports_root)
        except ValueError:
            abort(404)
        if not requested.is_file():
            abort(404)
        return send_from_directory(str(requested.parent), requested.name)

    @app.template_filter("status_class")
    def status_class(value: str) -> str:
        normalized = str(value).lower()
        if normalized in {"pass", "fail", "warning", "malformed", "timeout", "error"}:
            return normalized
        return "unknown"

    @app.context_processor
    def inject_helpers():
        return {"report_url": lambda path: url_for("open_report", report_path=path)}

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
