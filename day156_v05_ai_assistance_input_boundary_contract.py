"""Day156 v0.5 AI Assistance input boundary contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from v05_ai_assistance_contracts import (
    build_v05_ai_assistance_report,
    collect_v05_validation_errors,
    run_v05_ai_assistance_report,
    write_v05_ai_assistance_reports,
)


DAY = 156
TASK_NAME = "v05-ai-assistance-input-boundary-contract"
TITLE = "v0.5 AI Assistance Input Boundary Contract"
STATUS_LABEL = "V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day156_v05_ai_assistance_input_boundary_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day156_v05_ai_assistance_input_boundary_contract.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day156_v05_ai_assistance_input_boundary_contract.md"
AI_DOC = Path("docs") / "ai" / "day156_v05_ai_assistance_input_boundary_contract.md"

SPEC: Dict[str, Any] = {
    "day": DAY,
    "task_name": TASK_NAME,
    "title": TITLE,
    "status_label": STATUS_LABEL,
    "contract_type": "input_boundary_contract",
    "purpose": "Define the only data classes v0.5 AI Assistance may review before any provider, model, live-device, or executor work is considered.",
    "pass_means": "input boundary is documented and blocks unsafe data sources",
    "final_recommendation": "ACCEPT_INPUT_BOUNDARY_KEEP_EXECUTION_LOCKED",
    "report_json": REPORT_JSON,
    "report_html": REPORT_HTML,
    "contract_records": [
        {
            "id": "DAY156-IN-001",
            "name": "Allowed reviewer evidence inputs",
            "status": "PASS",
            "summary": "Allows repo reports, evidence files, pytest output, report-index output, task registry metadata, docs, dry-run outputs, and mock-only fixtures.",
            "allowed_inputs": [
                "repo reports",
                "evidence files",
                "pytest results",
                "report-index results",
                "task registry metadata",
                "roadmap/docs",
                "dry-run outputs",
                "mock-only fixtures",
            ],
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY156-IN-002",
            "name": "Forbidden data sources",
            "status": "PASS",
            "summary": "Forbids secrets, credentials, private keys, live device configs, config.json, environment values, microphone/voice input, and unauthorized API responses.",
            "forbidden_inputs": [
                "secrets",
                "tokens",
                "passwords",
                "private keys",
                ".env files",
                "config.json",
                "live device configs",
                "microphone or voice input",
                "unauthorized external API responses",
            ],
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY156-IN-003",
            "name": "No live collection path",
            "status": "PASS",
            "summary": "Inputs must already exist as static repo-local reviewer evidence; Day156 does not collect from devices, providers, APIs, shells, or microphones.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
    ],
    "acceptance_checks": [
        {"id": "DAY156-AC-001", "name": "Allowed input classes are explicit", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY156-AC-002", "name": "Forbidden private/live sources are explicit", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY156-AC-003", "name": "No provider, API, shell, voice, or device collection is enabled", "status": "PASS", "blocks_execution_unlock": True},
    ],
    "reference_targets": [
        {"surface": "Day156 roadmap doc", "path": ROADMAP_DOC.as_posix(), "required_fragments": (TASK_NAME, STATUS_LABEL, "config_json_read_allowed: false", "next_phase_allowed: false")},
        {"surface": "Day156 AI doc", "path": AI_DOC.as_posix(), "required_fragments": (TITLE, "Allowed reviewer evidence inputs", "Forbidden data sources", "No live collection path")},
        {"surface": "task registry", "path": "network_lab_task_registry.py", "required_fragments": (TASK_NAME,)},
        {"surface": "CLI dispatch", "path": "network_lab_cli_dispatch.py", "required_fragments": (TASK_NAME, "_run_day156_v05_ai_assistance_input_boundary_contract")},
        {"surface": "network_lab task catalog and report-index", "path": "network_lab.py", "required_fragments": ("DAY156_V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_TASK_ID", "day156_v05_ai_assistance_input_boundary_contract")},
    ],
}


def build_day156_v05_ai_assistance_input_boundary_contract(project_root: Path) -> Dict[str, Any]:
    return build_v05_ai_assistance_report(project_root, SPEC)


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    return collect_v05_validation_errors(report, SPEC)


def write_day156_v05_ai_assistance_input_boundary_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    return write_v05_ai_assistance_reports(project_root, SPEC, report)


def run_day156_v05_ai_assistance_input_boundary_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    return run_v05_ai_assistance_report(
        project_root,
        SPEC,
        format_heading_func=format_heading_func,
        format_status_func=format_status_func,
        relative_to_project_func=relative_to_project_func,
    )
