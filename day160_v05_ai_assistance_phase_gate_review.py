"""Day160 v0.5 AI Assistance phase gate review."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from v05_ai_assistance_contracts import (
    build_v05_ai_assistance_report,
    collect_v05_validation_errors,
    run_v05_ai_assistance_report,
    write_v05_ai_assistance_reports,
)


DAY = 160
TASK_NAME = "v05-ai-assistance-phase-gate-review"
TITLE = "v0.5 AI Assistance Phase Gate Review"
STATUS_LABEL = "V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day160_v05_ai_assistance_phase_gate_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day160_v05_ai_assistance_phase_gate_review.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day160_v05_ai_assistance_phase_gate_review.md"
AI_DOC = Path("docs") / "ai" / "day160_v05_ai_assistance_phase_gate_review.md"

SPEC: Dict[str, Any] = {
    "day": DAY,
    "task_name": TASK_NAME,
    "title": TITLE,
    "status_label": STATUS_LABEL,
    "contract_type": "phase_gate_review",
    "purpose": "Review Day155-Day159 v0.5 evidence and decide whether the package is reviewer-ready without approving execution or next phase.",
    "pass_means": "phase gate evidence is ready for reviewer inspection, not approved for execution",
    "final_recommendation": "PHASE_GATE_REVIEW_READY_KEEP_NEXT_PHASE_BLOCKED",
    "report_json": REPORT_JSON,
    "report_html": REPORT_HTML,
    "contract_records": [
        {
            "id": "DAY160-GATE-001",
            "name": "Day155 reopen rationale present",
            "status": "PASS",
            "summary": "Rationale remains reviewer-assistance only and does not unlock execution.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY160-GATE-002",
            "name": "Day156 input boundary present",
            "status": "PASS",
            "summary": "Input boundary allows static reviewer evidence and forbids secrets/live/private sources.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY160-GATE-003",
            "name": "Day157 output template present",
            "status": "PASS",
            "summary": "Output template is fixed and has no executable command/provider/executor fields.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY160-GATE-004",
            "name": "Day158 fixture renderer present",
            "status": "PASS",
            "summary": "Fixtures remain deterministic, reviewer-only, and mock/static.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY160-GATE-005",
            "name": "Day159 safety regression matrix present",
            "status": "PASS",
            "summary": "Safety matrix keeps provider/API/model/live-device/command/secret paths blocked.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
    ],
    "acceptance_checks": [
        {"id": "DAY160-AC-001", "name": "Day155-Day159 evidence chain is represented", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY160-AC-002", "name": "Phase gate review does not approve phase gate", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY160-AC-003", "name": "next_phase_allowed remains false", "status": "PASS", "blocks_execution_unlock": True},
    ],
    "reference_targets": [
        {"surface": "Day160 roadmap doc", "path": ROADMAP_DOC.as_posix(), "required_fragments": (TASK_NAME, STATUS_LABEL, "phase_gate_approval: false", "next_phase_allowed: false")},
        {"surface": "Day160 AI doc", "path": AI_DOC.as_posix(), "required_fragments": (TITLE, "Day155 reopen rationale present", "Day159 safety regression matrix present", "next_phase_allowed remains false")},
        {"surface": "AI intent README", "path": "docs/ai-intent/README.md", "required_fragments": ("## Day160", "v0.5 AI Assistance Phase Gate Review", "next_phase_allowed=false")},
        {"surface": "README", "path": "README.md", "required_fragments": ("## Current Release Status", "Stage-0 Network Automation Lab", "Workflow Version 2", "DEFERRED_SECURITY_RESEARCH_BLOCKED", "WF-01-03C through WF-01-03F")},
        {"surface": "task registry", "path": "network_lab_task_registry.py", "required_fragments": (TASK_NAME,)},
        {"surface": "CLI dispatch", "path": "network_lab_cli_dispatch.py", "required_fragments": (TASK_NAME, "_run_day160_v05_ai_assistance_phase_gate_review")},
        {"surface": "network_lab task catalog and report-index", "path": "network_lab.py", "required_fragments": ("DAY160_V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_TASK_ID", "day160_v05_ai_assistance_phase_gate_review")},
    ],
}


def build_day160_v05_ai_assistance_phase_gate_review(project_root: Path) -> Dict[str, Any]:
    return build_v05_ai_assistance_report(project_root, SPEC)


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    return collect_v05_validation_errors(report, SPEC)


def write_day160_v05_ai_assistance_phase_gate_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    return write_v05_ai_assistance_reports(project_root, SPEC, report)


def run_day160_v05_ai_assistance_phase_gate_review(
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
