"""Day158 v0.5 AI Assistance reviewer-only fixture renderer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from v05_ai_assistance_contracts import (
    build_v05_ai_assistance_report,
    collect_v05_validation_errors,
    run_v05_ai_assistance_report,
    write_v05_ai_assistance_reports,
)


DAY = 158
TASK_NAME = "v05-ai-assistance-reviewer-only-fixture-renderer"
TITLE = "v0.5 AI Assistance Reviewer-Only Fixture Renderer"
STATUS_LABEL = "V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day158_v05_ai_assistance_reviewer_only_fixture_renderer.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day158_v05_ai_assistance_reviewer_only_fixture_renderer.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day158_v05_ai_assistance_reviewer_only_fixture_renderer.md"
AI_DOC = Path("docs") / "ai" / "day158_v05_ai_assistance_reviewer_only_fixture_renderer.md"

SPEC: Dict[str, Any] = {
    "day": DAY,
    "task_name": TASK_NAME,
    "title": TITLE,
    "status_label": STATUS_LABEL,
    "contract_type": "reviewer_only_fixture_renderer",
    "purpose": "Render deterministic mock reviewer fixtures that exercise Day156 input and Day157 output contracts without provider/API/model/runtime behavior.",
    "pass_means": "fixtures render deterministically and remain reviewer-only",
    "final_recommendation": "ACCEPT_FIXTURE_RENDERER_KEEP_EXECUTION_LOCKED",
    "report_json": REPORT_JSON,
    "report_html": REPORT_HTML,
    "contract_records": [
        {
            "id": "DAY158-FIX-001",
            "name": "Safe report summary fixture",
            "status": "PASS",
            "summary": "Uses committed report metadata and emits fixed-template review notes only.",
            "fixture_input_class": "repo_reports",
            "fixture_output_class": "reviewer_template_only",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY158-FIX-002",
            "name": "Missing optional evidence fixture",
            "status": "PASS",
            "summary": "Represents optional report-index WARN handling without treating missing optional evidence as an execution trigger.",
            "fixture_input_class": "report_index_optional_missing",
            "fixture_output_class": "risk_flag_only",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY158-FIX-003",
            "name": "Blocked live-action request fixture",
            "status": "PASS",
            "summary": "Represents a live-device or command request as blocked reviewer evidence, never as an executable plan.",
            "fixture_input_class": "blocked_live_action",
            "fixture_output_class": "blocked_review_note",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
    ],
    "acceptance_checks": [
        {"id": "DAY158-AC-001", "name": "Fixtures use Day156 allowed/static inputs only", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY158-AC-002", "name": "Fixtures emit Day157 fixed template outputs only", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY158-AC-003", "name": "Blocked live-action fixture does not become a plan", "status": "PASS", "blocks_execution_unlock": True},
    ],
    "reference_targets": [
        {"surface": "Day158 roadmap doc", "path": ROADMAP_DOC.as_posix(), "required_fragments": (TASK_NAME, STATUS_LABEL, "provider_allowed: false", "next_phase_allowed: false")},
        {"surface": "Day158 AI doc", "path": AI_DOC.as_posix(), "required_fragments": (TITLE, "Safe report summary fixture", "Missing optional evidence fixture", "Blocked live-action request fixture")},
        {"surface": "task registry", "path": "network_lab_task_registry.py", "required_fragments": (TASK_NAME,)},
        {"surface": "CLI dispatch", "path": "network_lab_cli_dispatch.py", "required_fragments": (TASK_NAME, "_run_day158_v05_ai_assistance_reviewer_only_fixture_renderer")},
        {"surface": "network_lab task catalog and report-index", "path": "network_lab.py", "required_fragments": ("DAY158_V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_TASK_ID", "day158_v05_ai_assistance_reviewer_only_fixture_renderer")},
    ],
}


def build_day158_v05_ai_assistance_reviewer_only_fixture_renderer(project_root: Path) -> Dict[str, Any]:
    return build_v05_ai_assistance_report(project_root, SPEC)


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    return collect_v05_validation_errors(report, SPEC)


def write_day158_v05_ai_assistance_reviewer_only_fixture_renderer_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    return write_v05_ai_assistance_reports(project_root, SPEC, report)


def run_day158_v05_ai_assistance_reviewer_only_fixture_renderer(
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
