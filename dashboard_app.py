import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

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
from network_lab import discover_report_visibility, discover_vrrp_evidence, infer_report_result, mask_secret_values


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


@dataclass
class DashboardEvidenceEntry:
    title: str
    day: str
    device: str
    report_type: str
    status: str
    availability: str
    json_path: str
    html_path: str
    description: str
    notes: str
    json_view_path: Optional[str]
    html_view_path: Optional[str]


@dataclass
class AIIntentReviewerReference:
    day: str
    title: str
    summary: str
    doc_path: str
    roadmap_path: str
    report_paths: Sequence[str]


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


def normalize_dashboard_status(value: Any) -> str:
    status = normalize_status(value)
    if status == "WARNING":
        return "WARN"
    return status


def _project_root_for_reports_dir(reports_dir: Path) -> Path:
    reports_dir = Path(reports_dir).resolve()
    if reports_dir.name.lower() == "reports":
        return reports_dir.parent
    return PROJECT_ROOT


def safe_evidence_dirs(project_root: Path, reports_dir: Path) -> List[Path]:
    root = Path(project_root).resolve()
    configured_reports = Path(reports_dir).resolve()
    candidates = [configured_reports, root / "reports", root / "summary", root / "docs", root / "topology_profiles"]
    safe_dirs: List[Path] = []
    seen = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        safe_dirs.append(resolved)
    return safe_dirs


def _safe_relative_to_any(path: Path, safe_dirs: Sequence[Path]) -> Optional[Path]:
    resolved = Path(path).resolve()
    for safe_dir in safe_dirs:
        try:
            resolved.relative_to(Path(safe_dir).resolve())
            return resolved
        except ValueError:
            continue
    return None


def _safe_project_relative_path(
    project_root: Path,
    relative_path: str,
    safe_dirs: Sequence[Path],
) -> Optional[str]:
    if not relative_path or relative_path == "MISSING":
        return None
    requested = (Path(project_root).resolve() / relative_path).resolve()
    if not _safe_relative_to_any(requested, safe_dirs):
        return None
    try:
        return requested.relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return None


def safe_report_path(
    project_root: Path,
    report_path: str,
    safe_dirs: Sequence[Path],
    allowed_suffixes: Sequence[str],
) -> Optional[Path]:
    if not report_path:
        return None
    candidate_bases = [Path(project_root).resolve(), *[Path(item).resolve() for item in safe_dirs]]
    seen = set()
    for base in candidate_bases:
        requested = (base / report_path).resolve()
        if requested in seen:
            continue
        seen.add(requested)
        if requested.suffix.lower() not in allowed_suffixes:
            continue
        if not _safe_relative_to_any(requested, safe_dirs):
            continue
        if requested.is_file():
            return requested
    return None


def sanitize_json_preview(value: Any) -> Any:
    masked = mask_secret_values(value)
    if contains_unredacted_private_key(masked):
        return _redact_private_key_strings(masked)
    return masked


def _redact_private_key_strings(value: Any) -> Any:
    if isinstance(value, str):
        if contains_unredacted_private_key(value):
            return "PrivateKey: REDACTED"
        return value
    if isinstance(value, dict):
        return {key: _redact_private_key_strings(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_private_key_strings(item) for item in value]
    return value


def load_json_preview(json_path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "MALFORMED",
            "summary": {"error": f"Invalid JSON: {exc.msg}"},
            "pretty": "",
        }
    except OSError as exc:
        return {
            "status": "UNKNOWN",
            "summary": {"error": f"Could not read JSON report: {exc}"},
            "pretty": "",
        }

    safe_data = sanitize_json_preview(data)
    summary = safe_data if isinstance(safe_data, dict) else {"value": safe_data}
    if isinstance(summary, dict) and len(summary) > 12:
        summary = dict(list(summary.items())[:12])
        summary["_preview_note"] = "Showing first 12 top-level fields."
    return {
        "status": normalize_dashboard_status(infer_report_result(data)),
        "summary": summary,
        "pretty": json.dumps(safe_data, indent=2, sort_keys=True),
    }


def collect_dashboard_evidence(
    project_root: Path,
    reports_dir: Optional[Path] = None,
) -> List[DashboardEvidenceEntry]:
    root = Path(project_root).resolve()
    reports_root = Path(reports_dir).resolve() if reports_dir else root / "reports"
    safe_dirs = safe_evidence_dirs(root, reports_root)
    entries: List[DashboardEvidenceEntry] = []

    for row in discover_report_visibility(root):
        json_path = _safe_project_relative_path(root, str(row.get("json", "")), safe_dirs)
        html_path = _safe_project_relative_path(root, str(row.get("html", "")), safe_dirs)
        json_file = safe_report_path(root, json_path or "", safe_dirs, (".json",))
        status = "UNKNOWN"
        if json_file:
            status = load_json_preview(json_file)["status"]
        elif str(row.get("status", "")).upper() == "MISSING":
            status = "MISSING"
        elif str(row.get("status", "")).upper() == "FOUND":
            status = "FOUND"

        entries.append(
            DashboardEvidenceEntry(
                title=str(row.get("title", "Untitled report")),
                day=str(row.get("day", "Unknown")),
                device=str(row.get("device", "Unknown scope")),
                report_type=str(row.get("report_type", "Report evidence")),
                status=status,
                availability=str(row.get("status", "UNKNOWN")),
                json_path=json_path or str(row.get("json", "")),
                html_path=html_path or str(row.get("html", "")),
                description=str(row.get("description", "")),
                notes=str(row.get("notes", "")),
                json_view_path=json_path,
                html_view_path=html_path,
            )
        )
    return entries


def classify_report_type(filename_or_path: Any) -> str:
    name = Path(filename_or_path).name.lower()
    path_text = str(filename_or_path).lower()
    if "vrrp" in name or any(day in name for day in ("day32", "day33", "day34", "day35", "day39")):
        return "HA / VRRP evidence"
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
        ("HA / VRRP evidence", ("HA / VRRP evidence",)),
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


def ai_intent_reviewer_references() -> List[AIIntentReviewerReference]:
    return [
        AIIntentReviewerReference(
            day="Day57",
            title="AI intent mapping prototype",
            summary=(
                "Maps static reviewer text to a proposed allowlisted task and safety label, "
                "but keeps the mapped task unexecuted."
            ),
            doc_path="docs/ai/day57_intent_mapping_prototype.md",
            roadmap_path="docs/roadmap/day57_ai_assisted_task_intent_mapping_prototype_plan.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day58",
            title="Safety review gate",
            summary=(
                "Classifies mapped proposals before any future execution path, with "
                "live-capable or unknown intents blocked by default."
            ),
            doc_path="docs/ai/day58_intent_mapping_safety_review_confirmation_gate.md",
            roadmap_path="docs/roadmap/day58_intent_mapping_safety_review_confirmation_gate.md",
            report_paths=(
                "reports/portfolio/day58_intent_mapping_safety_review.json",
                "reports/portfolio/day58_intent_mapping_safety_review.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day59",
            title="Intent policy matrix",
            summary=(
                "Explains allowed report-only intents, dry-run-only proposals, and "
                "blocked live or configuration-changing requests."
            ),
            doc_path="docs/ai/day59_intent_policy_matrix_reviewer_safety_explanation.md",
            roadmap_path="docs/roadmap/day59_intent_policy_matrix_reviewer_safety_explanation.md",
            report_paths=(
                "reports/portfolio/day59_intent_policy_matrix.json",
                "reports/portfolio/day59_intent_policy_matrix.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day60",
            title="Reviewer walkthrough",
            summary=(
                "Connects Day57 mapping, Day58 safety review, and Day59 policy explanation "
                "into one local report-only demo."
            ),
            doc_path="docs/ai/day60_ai_intent_workflow_demo_reviewer_walkthrough.md",
            roadmap_path="docs/roadmap/day60_ai_intent_workflow_demo_reviewer_walkthrough.md",
            report_paths=(
                "reports/portfolio/day60_intent_workflow_demo.json",
                "reports/portfolio/day60_intent_workflow_demo.html",
            ),
        ),
    ]


def ai_intent_safety_boundaries() -> List[str]:
    return [
        "Report-only reviewer entry point; this page does not execute anything.",
        "No OpenAI API calls.",
        "No voice input or speech API.",
        "No mapped runner task execution.",
        "No live network tests.",
        "No SSH sessions.",
        "No MikroTik, Cisco, router, switch, firewall, VPN, or real device access.",
        "No config.json requirement.",
        "No NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration changes.",
        "No release tag creation.",
        "No real v0.3 runtime execution.",
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
    app.config["PROJECT_ROOT"] = _project_root_for_reports_dir(app.config["REPORTS_DIR"])
    app.config["SAFE_EVIDENCE_DIRS"] = safe_evidence_dirs(
        app.config["PROJECT_ROOT"],
        app.config["REPORTS_DIR"],
    )
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
        evidence_entries = collect_dashboard_evidence(
            app.config["PROJECT_ROOT"],
            app.config["REPORTS_DIR"],
        )
        grouped: Dict[str, List[DashboardEvidenceEntry]] = {}
        for entry in evidence_entries:
            grouped.setdefault(entry.day, []).append(entry)
        return render_template(
            "dashboard_reports.html",
            grouped_evidence=grouped,
            vrrp_evidence=discover_vrrp_evidence(app.config["PROJECT_ROOT"]),
            day12_summaries=build_day12_dashboard_summaries(app.config["REPORTS_DIR"]),
            reports_exist=app.config["REPORTS_DIR"].exists(),
            has_evidence=bool(evidence_entries),
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

    @app.route("/ai-intent-reviewer")
    def ai_intent_reviewer():
        return render_template(
            "dashboard_ai_intent_reviewer.html",
            references=ai_intent_reviewer_references(),
            safety_boundaries=ai_intent_safety_boundaries(),
        )

    @app.route("/reports/open/<path:report_path>")
    def open_report(report_path: str):
        requested = safe_report_path(
            app.config["PROJECT_ROOT"],
            report_path,
            app.config["SAFE_EVIDENCE_DIRS"],
            (".html",),
        )
        if requested is None:
            abort(404)
        return send_from_directory(str(requested.parent), requested.name)

    @app.route("/reports/json/<path:report_path>")
    def preview_json_report(report_path: str):
        requested = safe_report_path(
            app.config["PROJECT_ROOT"],
            report_path,
            app.config["SAFE_EVIDENCE_DIRS"],
            (".json",),
        )
        if requested is None:
            abort(404)
        try:
            display_path = requested.relative_to(app.config["PROJECT_ROOT"].resolve()).as_posix()
        except ValueError:
            display_path = requested.name
        preview = load_json_preview(requested)
        return render_template(
            "dashboard_json_preview.html",
            report_path=display_path,
            preview=preview,
        )

    @app.route("/reports/evidence/<path:report_path>")
    def open_evidence_artifact(report_path: str):
        requested = safe_report_path(
            app.config["PROJECT_ROOT"],
            report_path,
            app.config["SAFE_EVIDENCE_DIRS"],
            (".html", ".txt", ".md", ".png", ".jpg", ".jpeg", ".svg"),
        )
        if requested is None:
            abort(404)
        return send_from_directory(str(requested.parent), requested.name)

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
        normalized = str(value).lower().replace(" ", "-")
        aliases = {"warn": "warning", "missing": "unknown", "found": "pass", "not_generated": "warning"}
        normalized = aliases.get(normalized, normalized)
        if "disabled" in normalized:
            return "unknown"
        if normalized in {"pass", "fail", "warning", "malformed", "timeout", "error"}:
            return normalized
        return "unknown"

    @app.context_processor
    def inject_helpers():
        return {
            "report_url": lambda path: url_for("open_report", report_path=path),
            "json_report_url": lambda path: url_for("preview_json_report", report_path=path),
            "evidence_url": lambda path: url_for("open_evidence_artifact", report_path=path),
        }

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
