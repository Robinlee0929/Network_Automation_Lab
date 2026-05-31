import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from flask import Flask, abort, render_template, send_from_directory, url_for
except ImportError:  # pragma: no cover - exercised by environments without Flask.
    Flask = None  # type: ignore[assignment]
    abort = None  # type: ignore[assignment]
    render_template = None  # type: ignore[assignment]
    send_from_directory = None  # type: ignore[assignment]
    url_for = None  # type: ignore[assignment]


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"

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


def create_app(reports_dir: Optional[Path] = None) -> Flask:
    if Flask is None:
        raise RuntimeError(
            "Flask is required for the Day10 dashboard. Install it with: pip install flask"
        )

    app = Flask(__name__)
    app.config["REPORTS_DIR"] = Path(reports_dir) if reports_dir else DEFAULT_REPORTS_DIR

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
            grouped.setdefault(entry.device, []).append(entry)
        return render_template(
            "dashboard_reports.html",
            grouped_reports=grouped,
            reports_exist=app.config["REPORTS_DIR"].exists(),
        )

    @app.route("/commands")
    def commands():
        return render_template(
            "dashboard_commands.html",
            commands=command_examples(),
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

    @app.template_filter("status_class")
    def status_class(value: str) -> str:
        normalized = str(value).lower()
        if normalized in {"pass", "fail", "warning", "malformed"}:
            return normalized
        return "unknown"

    @app.context_processor
    def inject_helpers():
        return {"report_url": lambda path: url_for("open_report", report_path=path)}

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
