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
from intent_controlled_ai_runtime_entry import get_day71_controlled_entry_design
from intent_offline_mock_runtime import build_mock_runtime_report
from intent_reviewer_report_quality import build_reviewer_quality_report
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


@dataclass
class Day69EvidenceChainItem:
    day: str
    title: str
    status: str
    evidence: str
    doc_path: str
    report_paths: Sequence[str]


@dataclass
class Day69ScenarioEvidence:
    scenario_name: str
    scenario_id: str
    expected_decision: str
    safety_category: str
    evidence_source: str
    contract_status: str
    review_quality_status: str
    safety_note: str
    doc_path: str
    report_paths: Sequence[str]


@dataclass
class Day70ReadinessGate:
    gate: str
    status: str
    evidence: str


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
        AIIntentReviewerReference(
            day="Day62",
            title="Scenario pack / sample cases",
            summary=(
                "Adds static reviewer sample cases for report-only, dry-run, blocked, "
                "and clarification-required intents without adding any execution path."
            ),
            doc_path="docs/ai/intent_reviewer_scenario_pack.md",
            roadmap_path="docs/roadmap/day62_ai_intent_reviewer_scenario_pack.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day66",
            title="Offline mock runtime skeleton",
            summary=(
                "Models the future runtime record shape with deterministic offline mock "
                "scenarios while keeping live execution permanently disallowed."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_skeleton.md",
            roadmap_path="docs/roadmap/day66_offline_mock_runtime_skeleton.md",
            report_paths=(
                "reports/portfolio/day66_offline_mock_runtime_skeleton.json",
                "reports/portfolio/day66_offline_mock_runtime_skeleton.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day67",
            title="Offline mock runtime contract",
            summary=(
                "Validates Day66 mock runtime output fields and safety invariants before "
                "any future AI, voice, SSH, or live execution integration."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_contract.md",
            roadmap_path="docs/roadmap/day67_offline_mock_runtime_contract_safety_invariants.md",
            report_paths=(
                "reports/portfolio/day67_offline_mock_runtime_contract.json",
                "reports/portfolio/day67_offline_mock_runtime_contract.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day68",
            title="Reviewer report quality and evidence trace",
            summary=(
                "Reviews Day66-Day67 report quality, evidence traceability, contract "
                "validation proof, and no-execution evidence for human reviewers."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_reviewer_report_quality.md",
            roadmap_path="docs/roadmap/day68_offline_mock_runtime_reviewer_report_quality.md",
            report_paths=(
                "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json",
                "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day69",
            title="Reviewer dashboard evidence drilldown",
            summary=(
                "Makes the Day66-Day68 offline mock runtime evidence chain visible "
                "scenario by scenario on the static reviewer dashboard."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md",
            roadmap_path="docs/roadmap/day69_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day70",
            title="AI runtime readiness gate",
            summary=(
                "Reviews the Day66-Day69 offline mock runtime evidence chain and "
                "records whether the project is ready to plan a controlled AI "
                "runtime prototype without starting that runtime."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_phase_exit_review.md",
            roadmap_path="docs/roadmap/day70_offline_mock_runtime_phase_exit_ai_readiness_gate.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day71",
            title="Controlled AI runtime prototype entry design",
            summary=(
                "Defines the controlled future AI runtime entry contract, input/output "
                "fields, safety gate sequence, and blocked surfaces while keeping "
                "execution disabled."
            ),
            doc_path="docs/ai/intent_controlled_ai_runtime_entry_design.md",
            roadmap_path="docs/roadmap/day71_controlled_ai_runtime_prototype_entry_design.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day72",
            title="Controlled AI runtime input contract validator",
            summary=(
                "Validates future controlled AI runtime intent payloads before any "
                "runtime decision path while keeping execution disabled."
            ),
            doc_path="docs/ai/intent_controlled_ai_runtime_input_validator.md",
            roadmap_path="docs/roadmap/day72_controlled_ai_runtime_input_contract_validator.md",
            report_paths=(),
        ),
        AIIntentReviewerReference(
            day="Day73",
            title="Mock AI decision pipeline",
            summary=(
                "Runs deterministic mock decisions after Day72 validation and "
                "records reviewer-ready labels while keeping execution disabled."
            ),
            doc_path="docs/ai/intent_mock_ai_decision_pipeline.md",
            roadmap_path="docs/roadmap/day73_mock_ai_decision_pipeline.md",
            report_paths=(
                "reports/lab-summary/day73_mock_ai_decision_pipeline.json",
                "reports/lab-summary/day73_mock_ai_decision_pipeline.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day74",
            title="Controlled dry-run plan builder",
            summary=(
                "Converts Day73 mock decision records into reviewer dry-run plan "
                "previews while keeping execution disabled."
            ),
            doc_path="docs/ai/intent_dry_run_plan_builder.md",
            roadmap_path="docs/roadmap/day74_dry_run_plan_builder.md",
            report_paths=(
                "reports/lab-summary/day74_dry_run_plan_builder.json",
                "reports/lab-summary/day74_dry_run_plan_builder.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day75",
            title="Manual review approval envelope",
            summary=(
                "Wraps Day74 dry-run plans in deterministic reviewer sign-off "
                "envelopes while preserving no execution unlock."
            ),
            doc_path="docs/ai/intent_manual_review_approval_envelope.md",
            roadmap_path="docs/roadmap/day75_manual_review_approval_envelope.md",
            report_paths=(
                "reports/lab-summary/day75_manual_review_approval_envelope.json",
                "reports/lab-summary/day75_manual_review_approval_envelope.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day76",
            title="Controlled runtime audit trail",
            summary=(
                "Links Day73 decisions, Day74 dry-run plans, and Day75 approval "
                "envelopes into deterministic reviewer evidence packages while "
                "preserving no execution unlock."
            ),
            doc_path="docs/ai/intent_runtime_audit_trail.md",
            roadmap_path="docs/roadmap/day76_runtime_audit_trail.md",
            report_paths=(
                "reports/lab-summary/day76_runtime_audit_trail.json",
                "reports/lab-summary/day76_runtime_audit_trail.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day77",
            title="Runtime safety gate",
            summary=(
                "Links Day73 decisions, Day74 dry-run plans, Day75 approval "
                "envelopes, and Day76 audit records into deterministic locked "
                "runtime gate records that prove execution remains unavailable."
            ),
            doc_path="docs/ai/intent_runtime_safety_gate.md",
            roadmap_path="docs/roadmap/day77_runtime_safety_gate.md",
            report_paths=(
                "reports/lab-summary/day77_runtime_safety_gate.json",
                "reports/lab-summary/day77_runtime_safety_gate.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day78",
            title="Controlled runtime safety case",
            summary=(
                "Links Day72 input validation, Day73 mock decisions, Day74 dry-run "
                "plans, Day75 approval envelopes, Day76 audit records, and Day77 "
                "locked gates into final REVIEW_ONLY safety case records."
            ),
            doc_path="docs/ai/intent_runtime_safety_case.md",
            roadmap_path="docs/roadmap/day78_runtime_safety_case.md",
            report_paths=(
                "reports/lab-summary/day78_runtime_safety_case.json",
                "reports/lab-summary/day78_runtime_safety_case.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day79",
            title="Controlled read-only task contract and allowlist",
            summary=(
                "Defines future read-only task candidates, blocked write actions, "
                "destructive actions, unknown tasks, and manual classification cases "
                "while keeping all execution disabled."
            ),
            doc_path="docs/ai/intent_readonly_task_contract.md",
            roadmap_path="docs/roadmap/day79_readonly_task_contract.md",
            report_paths=(
                "reports/lab-summary/day79_readonly_task_contract.json",
                "reports/lab-summary/day79_readonly_task_contract.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day80",
            title="Read-only execution broker skeleton",
            summary=(
                "Receives fixed mock read-only task requests, checks the Day79 "
                "contract, rejects unsafe requests, queues review-only requests, "
                "and prepares mock execution request data without executing anything."
            ),
            doc_path="docs/ai/intent_readonly_execution_broker.md",
            roadmap_path="docs/roadmap/day80_readonly_execution_broker_skeleton.md",
            report_paths=(
                "reports/lab-summary/day80_readonly_execution_broker.json",
                "reports/lab-summary/day80_readonly_execution_broker.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day81",
            title="Read-only broker review queue and decision state report",
            summary=(
                "Transforms Day80 broker records into reviewer-facing queue "
                "records with review states and decision states while keeping "
                "all execution, SSH, device access, live command, mapped task, "
                "and dashboard action surfaces disabled."
            ),
            doc_path="docs/ai/intent_broker_review_queue.md",
            roadmap_path="docs/roadmap/day81_broker_review_queue.md",
            report_paths=(
                "reports/lab-summary/day81_broker_review_queue.json",
                "reports/lab-summary/day81_broker_review_queue.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day82",
            title="Reviewer decision audit summary and queue evidence export",
            summary=(
                "Summarizes Day81 queue decisions and exports reviewer audit "
                "evidence while keeping all execution, SSH, device access, live "
                "command, AI runtime, mapped task, and dashboard action surfaces "
                "disabled."
            ),
            doc_path="docs/ai/intent_reviewer_decision_audit_summary.md",
            roadmap_path="docs/roadmap/day82_reviewer_decision_audit_summary.md",
            report_paths=(
                "reports/lab-summary/day82_reviewer_decision_audit_summary.json",
                "reports/lab-summary/day82_reviewer_decision_audit_summary.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day83",
            title="Read-only executor readiness gate",
            summary=(
                "Validates the Day79-Day82 evidence chain as future adapter design "
                "readiness only, while preserving no executor, SSH, device access, "
                "AI runtime, mapped task, dashboard action, or unlock path."
            ),
            doc_path="docs/ai/readonly_executor_readiness_gate.md",
            roadmap_path="docs/roadmap/day83_readonly_executor_readiness_gate.md",
            report_paths=(
                "reports/lab-summary/day83_readonly_executor_readiness_gate.json",
                "reports/lab-summary/day83_readonly_executor_readiness_gate.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day84",
            title="Read-only executor adapter interface contract",
            summary=(
                "Defines future adapter request, response, capability, evidence, "
                "safety flag, and validation shapes as a contract-only boundary."
            ),
            doc_path="docs/ai/intent_readonly_executor_adapter_contract.md",
            roadmap_path="docs/roadmap/day84_readonly_executor_adapter_interface_contract.md",
            report_paths=(
                "reports/lab-summary/day84_readonly_executor_adapter_contract.json",
                "reports/lab-summary/day84_readonly_executor_adapter_contract.html",
            ),
        ),
        AIIntentReviewerReference(
            day="Day85",
            title="Mock Adapter + Evidence Binding",
            summary=(
                "Builds deterministic mock adapter fixtures that conform to Day84 "
                "and bind every response to request, adapter, contract, evidence, "
                "and reviewer decision fields; Compatibility Matrix stays internal "
                "validation only."
            ),
            doc_path="docs/ai/intent_mock_adapter_evidence_binding.md",
            roadmap_path="docs/roadmap/day85_mock_adapter_evidence_binding.md",
            report_paths=(
                "reports/lab-summary/day85_mock_adapter_evidence_binding.json",
                "reports/lab-summary/day85_mock_adapter_evidence_binding.html",
            ),
        ),
    ]


def day69_evidence_chain() -> List[Day69EvidenceChainItem]:
    runtime_report = build_mock_runtime_report()
    quality_report = build_reviewer_quality_report(runtime_report)
    contract_evidence = quality_report["contract_validation_evidence"]
    quality_summary = quality_report["quality_gate_summary"]
    return [
        Day69EvidenceChainItem(
            day="Day66",
            title="Offline Mock Runtime",
            status=runtime_report["reviewer_status"],
            evidence=(
                f"{runtime_report['summary']['mock_scenarios']} deterministic offline "
                "mock scenarios expose intent, safety category, mock plan, and "
                "no-execution record fields."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_skeleton.md",
            report_paths=(
                "reports/portfolio/day66_offline_mock_runtime_skeleton.json",
                "reports/portfolio/day66_offline_mock_runtime_skeleton.html",
            ),
        ),
        Day69EvidenceChainItem(
            day="Day67",
            title="Contract Validation / Safety Invariants",
            status=contract_evidence["contract_status"],
            evidence=(
                f"{contract_evidence['validated_scenario_count']} scenarios validate "
                "against required output fields, blocked handling, and no-live "
                "safety invariants."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_contract.md",
            report_paths=(
                "reports/portfolio/day67_offline_mock_runtime_contract.json",
                "reports/portfolio/day67_offline_mock_runtime_contract.html",
            ),
        ),
        Day69EvidenceChainItem(
            day="Day68",
            title="Reviewer Report Quality",
            status=quality_report["review_status"],
            evidence=(
                f"{quality_summary['review_ready_count']} of "
                f"{quality_summary['total_scenarios']} scenario reviews are "
                "review-ready with visible decision, evidence, contract, and "
                "no-execution proof."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_reviewer_report_quality.md",
            report_paths=(
                "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json",
                "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.html",
            ),
        ),
        Day69EvidenceChainItem(
            day="Day69",
            title="Dashboard Evidence Drilldown",
            status="STATIC_REVIEW_READY",
            evidence=(
                "The reviewer dashboard presents the Day66-Day68 chain and each "
                "mock scenario as read-only evidence cards."
            ),
            doc_path="docs/ai/intent_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md",
            report_paths=(),
        ),
    ]


def day69_scenario_evidence_drilldown() -> List[Day69ScenarioEvidence]:
    runtime_report = build_mock_runtime_report()
    quality_report = build_reviewer_quality_report(runtime_report)
    reviews_by_id = {
        item["scenario_id"]: item
        for item in quality_report["scenario_reviews"]
        if isinstance(item, dict)
    }
    scenario_cards: List[Day69ScenarioEvidence] = []
    for scenario in runtime_report["mock_scenarios"]:
        review = reviews_by_id.get(scenario["scenario_id"], {})
        contract_status = review.get("contract_validation_status", "UNKNOWN")
        review_status = review.get("reviewer_verdict", "UNKNOWN")
        evidence_source = (
            "Day66 mock_scenarios -> Day67 contract validator -> "
            "Day68 scenario_reviews"
        )
        safety_note = (
            "Static reviewer evidence only: live_execution_allowed=False, "
            "mapped_task_executed=False, No API, no voice, no SSH, no device "
            "access, and no network change."
        )
        if scenario["safety_category"] == "blocked_live_action":
            safety_note = f"{scenario['reviewer_note']} {safety_note}"
        elif scenario["safety_category"] == "needs_manual_review":
            safety_note = f"{scenario['reviewer_note']} {safety_note}"
        scenario_cards.append(
            Day69ScenarioEvidence(
                scenario_name=scenario["scenario_name"],
                scenario_id=scenario["scenario_id"],
                expected_decision=scenario["decision"],
                safety_category=scenario["safety_category"],
                evidence_source=evidence_source,
                contract_status=contract_status,
                review_quality_status=review_status,
                safety_note=safety_note,
                doc_path="docs/ai/intent_offline_mock_runtime_reviewer_dashboard_evidence_drilldown.md",
                report_paths=(
                    "reports/portfolio/day66_offline_mock_runtime_skeleton.json",
                    "reports/portfolio/day67_offline_mock_runtime_contract.json",
                    "reports/lab-summary/day68_offline_mock_runtime_reviewer_report_quality.json",
                ),
            )
        )
    return scenario_cards


def day70_ai_runtime_readiness_gates() -> List[Day70ReadinessGate]:
    return [
        Day70ReadinessGate(
            gate="Offline mock runtime exists",
            status="PASS",
            evidence="Day66 deterministic offline mock runtime skeleton.",
        ),
        Day70ReadinessGate(
            gate="Contract validation exists",
            status="PASS",
            evidence="Day67 contract and safety invariant validation.",
        ),
        Day70ReadinessGate(
            gate="Reviewer quality review exists",
            status="PASS",
            evidence="Day68 reviewer report quality and evidence trace review.",
        ),
        Day70ReadinessGate(
            gate="Dashboard evidence drilldown exists",
            status="PASS",
            evidence="Day69 static reviewer dashboard evidence drilldown.",
        ),
        Day70ReadinessGate(
            gate="Live execution boundary documented",
            status="PASS",
            evidence="Day70 safety boundary keeps live execution outside scope.",
        ),
        Day70ReadinessGate(
            gate="Human review requirement documented",
            status="PASS",
            evidence="Day70 requires human review before any Day71+ prototype.",
        ),
        Day70ReadinessGate(
            gate="AI runtime implementation started",
            status="NOT STARTED",
            evidence="Day70 is a readiness gate only, not runtime implementation.",
        ),
        Day70ReadinessGate(
            gate="Voice integration started",
            status="NOT STARTED",
            evidence="No voice input, speech API, or voice control is added.",
        ),
        Day70ReadinessGate(
            gate="Device access enabled",
            status="NOT ENABLED",
            evidence="No SSH, router, switch, firewall, VPN, or lab device access.",
        ),
        Day70ReadinessGate(
            gate="OpenAI API enabled",
            status="NOT ENABLED",
            evidence="No OpenAI dependency, API key, environment variable, or API call.",
        ),
    ]


def day71_controlled_ai_runtime_entry_design() -> Dict[str, object]:
    return get_day71_controlled_entry_design()


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
        "No automatic execution of mapped tasks from scenario examples.",
        "Day66 mock runtime output is fixed offline evidence only.",
        "Day67 validates contract and safety invariants without enabling runtime behavior.",
        "Day68 reviews report quality and evidence traceability without enabling runtime behavior.",
        "Day69 presents reviewer evidence drilldown only; it is static, read-only, and report-only.",
        "Day70 is an AI runtime readiness gate only; it does not start AI runtime implementation.",
        "Day70 preserves no dashboard forms, no POST routes for AI intent review, and no action endpoints.",
        "Day71 defines a controlled AI runtime entry design only; execution_allowed remains false.",
        "Day71 keeps API integration, voice, device access, live execution, mapped task execution, and dashboard action surfaces disabled.",
        "Day72 validates controlled AI runtime input payloads only; execution_allowed remains false.",
        "Day72 adds no OpenAI API, voice, SSH, device access, live execution, mapped task execution, config changes, forms, POST routes, or action endpoints.",
        "Day73 runs deterministic mock decisions after Day72 validation only; allowed_to_execute remains false.",
        "Day73 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard POST/action endpoint, or network configuration change.",
        "Day74 converts Day73 mock decisions into dry-run plan previews only; allowed_to_execute remains false and dry_run_only remains true.",
        "Day74 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, or network configuration change.",
        "Day75 wraps Day74 dry-run plans in record-only reviewer sign-off envelopes; allowed_to_execute remains false, dry_run_only remains true, and execution_unlock_supported remains false.",
        "Day75 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approval surface, execution control, approval unlock, or network configuration change.",
        "Day76 links Day73 decisions, Day74 dry-run plans, and Day75 approval envelopes into reviewer audit evidence only; allowed_to_execute remains false, dry_run_only remains true, and execution_unlock_supported remains false.",
        "Day76 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, or network configuration change.",
        "Day77 links Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, and Day76 audit records into locked runtime safety gate evidence only; allowed_to_execute remains false, dry_run_only remains true, execution_unlock_supported remains false, and runtime_gate_state remains LOCKED.",
        "Day77 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day78 links Day72 input validation, Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, Day76 audit records, and Day77 locked gates into end-to-end reviewer safety case evidence only; final_recommendation remains REVIEW_ONLY.",
        "Day78 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day79 defines the read-only task allowlist and capability definition layer after the Day72-Day78 runtime safety chain; allowed_to_execute remains false, dry_run_only remains true, and execution_unlock_supported remains false.",
        "Day79 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day80 defines the read-only execution broker skeleton after the Day79 allowlist; allowed_to_execute remains false, dry_run_only remains true, execution_unlock_supported remains false, ssh_allowed remains false, and live_command_allowed remains false.",
        "Day80 adds no OpenAI API, AI SDK, real AI runtime, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, approve button, execute button, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day81 defines the read-only broker review queue and decision state report after Day80; it is review-only, dry-run-only, report-only, and has no execution unlock.",
        "Day81 keeps allowed_to_execute false, dry_run_only true, execution_unlock_supported false, ssh_allowed false, device_connection_allowed false, live_command_allowed false, mapped_task_execution_allowed false, and dashboard_action_allowed false.",
        "Day81 adds no OpenAI API, AI SDK, real AI runtime, voice, SSH, device access, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day82 summarizes Day81 queue decisions into reviewer audit evidence exports only; it is review-only, mock/deterministic, dry-run-only, report-only, and has no execution unlock.",
        "Day82 keeps allowed_to_execute false, dry_run_only true, execution_unlock_supported false, device_connection_allowed false, ssh_allowed false, live_command_allowed false, network_change_allowed false, ai_runtime_allowed false, and dashboard_action_allowed false.",
        "Day82 adds no OpenAI API, AI SDK runtime, real AI runtime, voice, SSH, device access, live execution, live command execution, mapped task execution, dashboard form, POST route, action endpoint, approval unlock, execution control, or network configuration change.",
        "Day83 marks future read-only executor adapter design readiness only; it adds no executor, AI runtime, SSH, device access, live execution, mapped task execution, dashboard action, approval unlock, or execution unlock.",
        "Day84 defines the read-only executor adapter interface contract only; it adds no adapter implementation, executor implementation, SSH, device access, live command execution, AI API, approval unlock, execution unlock, dashboard form, POST route, or action endpoint.",
        "Day85 remains Mock Adapter + Evidence Binding; Compatibility Matrix is internal validation evidence only and not a standalone topic.",
        "Day85 keeps every adapter record non-executing with allowed_to_execute false, ssh_allowed false, device_access_allowed false, live_command_allowed false, approval_unlock_supported false, execution_unlock_supported false, and ai_api_allowed false.",
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
            day69_evidence_chain=day69_evidence_chain(),
            day69_scenario_drilldown=day69_scenario_evidence_drilldown(),
            day70_readiness_gates=day70_ai_runtime_readiness_gates(),
            day71_entry_design=day71_controlled_ai_runtime_entry_design(),
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
