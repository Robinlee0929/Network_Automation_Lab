"""Day157 v0.5 AI Assistance output template contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from v05_ai_assistance_contracts import (
    build_v05_ai_assistance_report,
    collect_v05_validation_errors,
    run_v05_ai_assistance_report,
    write_v05_ai_assistance_reports,
)


DAY = 157
TASK_NAME = "v05-ai-assistance-output-template-contract"
TITLE = "v0.5 AI Assistance Output Template Contract"
STATUS_LABEL = "V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day157_v05_ai_assistance_output_template_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day157_v05_ai_assistance_output_template_contract.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day157_v05_ai_assistance_output_template_contract.md"
AI_DOC = Path("docs") / "ai" / "day157_v05_ai_assistance_output_template_contract.md"

SPEC: Dict[str, Any] = {
    "day": DAY,
    "task_name": TASK_NAME,
    "title": TITLE,
    "status_label": STATUS_LABEL,
    "contract_type": "output_template_contract",
    "purpose": "Define fixed reviewer-only output fields and explicitly exclude command, executor, provider, secret, and live-action fields.",
    "pass_means": "output template is fixed and cannot carry executable instructions",
    "final_recommendation": "ACCEPT_OUTPUT_TEMPLATE_KEEP_EXECUTION_LOCKED",
    "report_json": REPORT_JSON,
    "report_html": REPORT_HTML,
    "contract_records": [
        {
            "id": "DAY157-OUT-001",
            "name": "Allowed output fields",
            "status": "PASS",
            "summary": "Allows only review_subject, evidence_references, summary, risk_flags, comparison_notes, open_questions, and human_reviewer_decision.",
            "allowed_fields": [
                "review_subject",
                "evidence_references",
                "summary",
                "risk_flags",
                "comparison_notes",
                "open_questions",
                "human_reviewer_decision",
            ],
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY157-OUT-002",
            "name": "Forbidden output fields",
            "status": "PASS",
            "summary": "Forbids live commands, command templates, executor actions, provider activation, secrets, credentials, and approval-unlock fields.",
            "forbidden_fields": [
                "live_command",
                "command_template",
                "executor_action",
                "provider_activation",
                "secret",
                "credential",
                "approval_unlock",
            ],
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
        {
            "id": "DAY157-OUT-003",
            "name": "Human decision remains external",
            "status": "PASS",
            "summary": "The template can capture human_reviewer_decision as a review note, but it cannot approve a phase gate or unlock execution.",
            "review_only": True,
            "report_only": True,
            "execution_allowed": False,
            "next_phase_allowed": False,
        },
    ],
    "acceptance_checks": [
        {"id": "DAY157-AC-001", "name": "Template fields are fixed", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY157-AC-002", "name": "Executable fields are absent", "status": "PASS", "blocks_execution_unlock": True},
        {"id": "DAY157-AC-003", "name": "PASS cannot approve provider/API/executor paths", "status": "PASS", "blocks_execution_unlock": True},
    ],
    "reference_targets": [
        {"surface": "Day157 roadmap doc", "path": ROADMAP_DOC.as_posix(), "required_fragments": (TASK_NAME, STATUS_LABEL, "command_execution_allowed: false", "next_phase_allowed: false")},
        {"surface": "Day157 AI doc", "path": AI_DOC.as_posix(), "required_fragments": (TITLE, "Allowed output fields", "Forbidden output fields", "Human decision remains external")},
        {"surface": "task registry", "path": "network_lab_task_registry.py", "required_fragments": (TASK_NAME,)},
        {"surface": "CLI dispatch", "path": "network_lab_cli_dispatch.py", "required_fragments": (TASK_NAME, "_run_day157_v05_ai_assistance_output_template_contract")},
        {"surface": "network_lab task catalog and report-index", "path": "network_lab.py", "required_fragments": ("DAY157_V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_TASK_ID", "day157_v05_ai_assistance_output_template_contract")},
    ],
}


def build_day157_v05_ai_assistance_output_template_contract(project_root: Path) -> Dict[str, Any]:
    return build_v05_ai_assistance_report(project_root, SPEC)


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    return collect_v05_validation_errors(report, SPEC)


def write_day157_v05_ai_assistance_output_template_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    return write_v05_ai_assistance_reports(project_root, SPEC, report)


def run_day157_v05_ai_assistance_output_template_contract(
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
