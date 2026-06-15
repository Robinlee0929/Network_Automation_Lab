"""Day159 v0.5 AI Assistance safety regression matrix."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from v05_ai_assistance_contracts import (
    build_v05_ai_assistance_report,
    collect_v05_validation_errors,
    run_v05_ai_assistance_report,
    write_v05_ai_assistance_reports,
)


DAY = 159
TASK_NAME = "v05-ai-assistance-safety-regression-matrix"
TITLE = "v0.5 AI Assistance Safety Regression Matrix"
STATUS_LABEL = "V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day159_v05_ai_assistance_safety_regression_matrix.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day159_v05_ai_assistance_safety_regression_matrix.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day159_v05_ai_assistance_safety_regression_matrix.md"
AI_DOC = Path("docs") / "ai" / "day159_v05_ai_assistance_safety_regression_matrix.md"

SPEC: Dict[str, Any] = {
    "day": DAY,
    "task_name": TASK_NAME,
    "title": TITLE,
    "status_label": STATUS_LABEL,
    "contract_type": "safety_regression_matrix",
    "purpose": "Map v0.5 AI Assistance safety invariants to deterministic PASS records before phase gate review.",
    "pass_means": "safety invariants are represented and still block execution/provider/API/live-device paths",
    "final_recommendation": "ACCEPT_SAFETY_MATRIX_KEEP_EXECUTION_LOCKED",
    "report_json": REPORT_JSON,
    "report_html": REPORT_HTML,
    "contract_records": [
        {
            "id": "DAY159-MAT-001",
            "name": "Provider/API/model disabled invariant",
            "status": "PASS",
            "summary": "Provider, API, OpenAI API, external API, and model-call flags remain false.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY159-MAT-002",
            "name": "Live-device and command disabled invariant",
            "status": "PASS",
            "summary": "Live device, SSH, NETCONF, RESTCONF, RouterOS, command execution, and live command template flags remain false.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY159-MAT-003",
            "name": "Secret and private input disabled invariant",
            "status": "PASS",
            "summary": "Secrets, credentials, config.json, private keys, and environment-derived inputs remain forbidden.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY159-MAT-004",
            "name": "Reviewer authority invariant",
            "status": "PASS",
            "summary": "Human reviewer final authority remains true while phase_gate_approval and next_phase_allowed remain false.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
    ],
    "acceptance_checks": [
        {"id": "DAY159-AC-001", "name": "All unsafe capability flags are false", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY159-AC-002", "name": "All matrix rows are review-only/report-only", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY159-AC-003", "name": "No row advances phase gate or next phase", "status": "PASS", "blocks_execution_unlock": True},
    ],
    "reference_targets": [
        {"surface": "Day159 roadmap doc", "path": ROADMAP_DOC.as_posix(), "required_fragments": (TASK_NAME, STATUS_LABEL, "live_device_allowed: false", "next_phase_allowed: false")},
        {"surface": "Day159 AI doc", "path": AI_DOC.as_posix(), "required_fragments": (TITLE, "Provider/API/model disabled invariant", "Live-device and command disabled invariant", "Reviewer authority invariant")},
        {"surface": "task registry", "path": "network_lab_task_registry.py", "required_fragments": (TASK_NAME,)},
        {"surface": "CLI dispatch", "path": "network_lab_cli_dispatch.py", "required_fragments": (TASK_NAME, "_run_day159_v05_ai_assistance_safety_regression_matrix")},
        {"surface": "network_lab task catalog and report-index", "path": "network_lab.py", "required_fragments": ("DAY159_V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_TASK_ID", "day159_v05_ai_assistance_safety_regression_matrix")},
    ],
}


def build_day159_v05_ai_assistance_safety_regression_matrix(project_root: Path) -> Dict[str, Any]:
    return build_v05_ai_assistance_report(project_root, SPEC)


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    return collect_v05_validation_errors(report, SPEC)


def write_day159_v05_ai_assistance_safety_regression_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    return write_v05_ai_assistance_reports(project_root, SPEC, report)


def run_day159_v05_ai_assistance_safety_regression_matrix(
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
