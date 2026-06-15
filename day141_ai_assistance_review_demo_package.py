"""Day141 AI assistance review demo package.

This module builds a deterministic reviewer-facing package over existing AI
assistance review artifacts. It is review-only metadata packaging and does not
execute source tasks, call providers or APIs, reach devices, invoke SSH, or
open any next-phase capability.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 141
DAY_LABEL = "Day141"
TASK_NAME = "ai-assistance-review-demo-package"
TITLE = "AI Assistance Review Demo Package"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_READY"
BLOCKED_STATUS = "AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "day141_ai_assistance_review_demo_package.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day141_ai_assistance_review_demo_package.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day141_ai_assistance_review_demo_package.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day141_ai_assistance_review_demo_package.md"

NOT_NEXT_DAY_STATEMENT = "Day141 is not the next day's feature."
NO_EXECUTION_PROVIDER_API_STATEMENT = "Day141 does not open execution / provider / API."
NOT_FOLDER_MOVE_CONTINUATION_STATEMENT = "Day141 is not a folder-move continuation."
NOT_TMP_CLEANUP_CONTINUATION_STATEMENT = "Day141 is not a tmp cleanup continuation."
REVIEW_ONLY_DEMO_STATEMENT = "Day141 is a review-only demo package."

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "demo_package_only",
    "deterministic_static_data_only",
    "local_repo_metadata_only",
    "human_reviewer_presentation_only",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "execution_allowed",
    "source_execution_allowed",
    "provider_allowed",
    "api_allowed",
    "openai_api_called",
    "ai_provider_called",
    "ai_decision_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "router_switch_command_execution_allowed",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "mapped_execution_allowed",
    "configuration_change_allowed",
    "secrets_allowed",
    "credential_handling_allowed",
    "next_phase_allowed",
    "is_next_day_feature",
    "is_day142",
    "future_day_functionality_implemented",
    "execution_provider_api_opened",
    "folder_move_continuation",
    "tmp_cleanup_continuation",
    "project_folder_move_allowed",
    "tmp_cleanup_allowed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "status",
    "overall_status",
    "agents_md_read_before_day141_work",
    "agents_md_pre_read_result",
    "review_only",
    "execution_allowed",
    "source_execution_allowed",
    "provider_allowed",
    "api_allowed",
    "openai_api_called",
    "ai_decision_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "next_phase_allowed",
    "is_next_day_feature",
    "folder_move_continuation",
    "tmp_cleanup_continuation",
    "source_execution_commands_run",
    "demo_records",
    "source_artifacts",
    "safety_boundaries",
    "final_recommendation",
)

SOURCE_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {
        "day": "Day127",
        "name": "AI Reviewer Summary Schema Contract",
        "path": "docs/ai-intent/day127_ai_reviewer_summary_schema_contract.md",
        "role": "schema contract",
    },
    {
        "day": "Day128",
        "name": "AI Reviewer Summary Fixture Renderer",
        "path": "docs/ai-intent/day128_ai_reviewer_summary_fixture_renderer.md",
        "role": "deterministic fixture rendering",
    },
    {
        "day": "Day129",
        "name": "AI Summary Prompt Contract",
        "path": "docs/ai-intent/day129_ai_summary_prompt_contract.md",
        "role": "reviewer text contract",
    },
    {
        "day": "Day130",
        "name": "AI Summary Redaction and No-Secret Policy",
        "path": "docs/ai-intent/day130_ai_summary_redaction_and_no_secret_policy.md",
        "role": "redaction and no-secret policy",
    },
    {
        "day": "Day131",
        "name": "AI Summary Audit Trail Binding",
        "path": "docs/ai-intent/day131_ai_summary_audit_trail_binding.md",
        "role": "audit traceability",
    },
    {
        "day": "Day132",
        "name": "AI Summary Dashboard Card Integration",
        "path": "docs/ai-intent/day132_ai_summary_dashboard_card_integration.md",
        "role": "display-only dashboard card",
    },
    {
        "day": "Day133",
        "name": "Disabled AI Provider Interface Boundary",
        "path": "docs/ai-intent/day133_disabled_ai_provider_interface_boundary.md",
        "role": "disabled provider boundary",
    },
    {
        "day": "Day134",
        "name": "Disabled AI Provider Adapter Contract",
        "path": "docs/ai-intent/day134_disabled_ai_provider_adapter_contract.md",
        "role": "disabled adapter contract shape",
    },
    {
        "day": "Day135",
        "name": "AI Provider Disabled-by-Default Safety Regression",
        "path": "docs/ai-intent/day135_ai_provider_disabled_by_default_safety_regression.md",
        "role": "disabled-by-default regression",
    },
    {
        "day": "Day136",
        "name": "AI Reviewer Export Package Integration",
        "path": "docs/roadmap/day136_ai_reviewer_export_package_integration.md",
        "role": "review-only export package",
    },
    {
        "day": "Day137",
        "name": "Project Folder Organization Decision Gate",
        "path": "docs/roadmap/day137_project_folder_organization_decision_gate.md",
        "role": "demo deferral and folder decision boundary context only",
    },
    {
        "day": "Day138",
        "name": "Project Folder Organization Dry-Run Inventory Gate",
        "path": "docs/ai-intent/day138_project_folder_organization_dry_run_inventory_gate.md",
        "role": "folder inventory boundary context only",
    },
    {
        "day": "Day139",
        "name": "Docs-Only Move Dry-Run Evidence Plan",
        "path": "docs/ai-intent/day139_docs_only_move_dry_run_evidence_plan.md",
        "role": "docs-only no-move boundary context only",
    },
    {
        "day": "Day140",
        "name": "Folder Move Compatibility Gate",
        "path": "docs/ai-intent/day140_folder_move_compatibility_gate.md",
        "role": "compatibility boundary context only",
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day141_work": False,
            "agents_md_pre_read_result": "FAIL",
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day141_work": False,
            "agents_md_pre_read_result": "FAIL",
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_read_before_day141_work": markers_present,
        "agents_md_pre_read_result": "PASS" if markers_present else "FAIL",
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_source_artifact_records(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    records: list[Dict[str, Any]] = []
    for index, artifact in enumerate(SOURCE_ARTIFACTS, start=1):
        path = str(artifact["path"])
        records.append(
            {
                "artifact_id": f"DAY141_SOURCE_ARTIFACT_{index:02d}",
                "source_day": artifact["day"],
                "name": artifact["name"],
                "path": path,
                "path_exists": (root / path).exists(),
                "role": artifact["role"],
                "presentation_mode": "metadata_only",
                "read_mode": "static_reference_only",
                "execution_allowed": False,
                "source_execution_allowed": False,
                "provider_allowed": False,
                "api_allowed": False,
                "ai_decision_allowed": False,
                "next_phase_allowed": False,
            }
        )
    return records


def build_demo_records() -> list[Dict[str, Any]]:
    return [
        {
            "section_id": "reviewer_entry",
            "title": "Reviewer Entry",
            "purpose": "Orient a human reviewer to the AI assistance evidence chain.",
            "review_only": True,
            "execution_allowed": False,
        },
        {
            "section_id": "artifact_catalog",
            "title": "Artifact Catalog",
            "purpose": "Show Day127-Day140 artifact references as static review records.",
            "review_only": True,
            "execution_allowed": False,
        },
        {
            "section_id": "safety_boundary_table",
            "title": "Safety Boundary Table",
            "purpose": "Display explicit false gates for execution, source execution, providers, APIs, AI decisions, live access, SSH, next phase, folder moves, and tmp cleanup.",
            "review_only": True,
            "execution_allowed": False,
        },
        {
            "section_id": "reviewer_close",
            "title": "Reviewer Close",
            "purpose": "Confirm Day141 is a demo package only and next_phase_allowed remains false.",
            "review_only": True,
            "execution_allowed": False,
        },
    ]


def build_safety_boundaries() -> Dict[str, Any]:
    boundaries: Dict[str, Any] = {field: True for field in REQUIRED_TRUE_FIELDS}
    for field in REQUIRED_FALSE_FIELDS:
        boundaries[field] = False
    boundaries["source_execution_commands_run"] = []
    boundaries["reviewer_decision_effect"] = "presentation_only_no_unlock"
    boundaries["final_recommendation"] = "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE"
    return boundaries


def build_day141_ai_assistance_review_demo_package(project_root: Path) -> Dict[str, Any]:
    source_artifacts = build_source_artifact_records(project_root)
    safety_boundaries = build_safety_boundaries()
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "status": "PENDING",
        "overall_status": "PENDING",
        **build_agents_md_evidence(project_root),
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        "source_execution_commands_run": [],
        "demo_records": build_demo_records(),
        "source_artifacts": source_artifacts,
        "source_day_range": "Day127-Day140",
        "source_artifact_count": len(source_artifacts),
        "source_artifact_missing_count": sum(1 for item in source_artifacts if item["path_exists"] is not True),
        "safety_boundaries": safety_boundaries,
        "explicit_boundary_statements": [
            NOT_NEXT_DAY_STATEMENT,
            NO_EXECUTION_PROVIDER_API_STATEMENT,
            NOT_FOLDER_MOVE_CONTINUATION_STATEMENT,
            NOT_TMP_CLEANUP_CONTINUATION_STATEMENT,
            REVIEW_ONLY_DEMO_STATEMENT,
        ],
        "reviewer_next_action": "Review the static Day141 demo package; do not enable execution, source execution, providers, APIs, AI decisions, live access, SSH, next phase, folder moves, or tmp cleanup.",
        "final_recommendation": "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE",
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    expected_values = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "source_day_range": "Day127-Day140",
        "final_recommendation": "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE",
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_read_before_day141_work") is not True:
        errors.append("agents_md_read_before_day141_work must be true.")
    if report.get("agents_md_pre_read_result") != "PASS":
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")
    if report.get("source_execution_commands_run") != []:
        errors.append("source_execution_commands_run must be empty.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_demo_records(report.get("demo_records", []), errors)
    _validate_source_artifacts(report.get("source_artifacts", []), errors)
    _validate_safety_boundaries(report.get("safety_boundaries", {}), errors)
    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)
    return errors


def _validate_demo_records(records: Any, errors: list[str]) -> None:
    if not isinstance(records, list) or not records:
        errors.append("demo_records must be a non-empty list.")
        return
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("Each demo record must be an object.")
            continue
        if record.get("review_only") is not True:
            errors.append(f"{record.get('section_id', '<unknown>')} review_only must be true.")
        if record.get("execution_allowed") is not False:
            errors.append(f"{record.get('section_id', '<unknown>')} execution_allowed must be false.")


def _validate_source_artifacts(artifacts: Any, errors: list[str]) -> None:
    if not isinstance(artifacts, list) or len(artifacts) != len(SOURCE_ARTIFACTS):
        errors.append("source_artifacts must cover Day127-Day140.")
        return
    days = [artifact.get("source_day") for artifact in artifacts if isinstance(artifact, Mapping)]
    if days != [f"Day{day}" for day in range(127, 141)]:
        errors.append("source_artifacts must be ordered Day127 through Day140.")
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            errors.append("Each source artifact must be an object.")
            continue
        if artifact.get("path_exists") is not True:
            errors.append(f"{artifact.get('path', '<unknown>')} must exist for the static demo package.")
        if artifact.get("presentation_mode") != "metadata_only":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} presentation_mode must be metadata_only.")
        if artifact.get("read_mode") != "static_reference_only":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} read_mode must be static_reference_only.")
        for field in (
            "execution_allowed",
            "source_execution_allowed",
            "provider_allowed",
            "api_allowed",
            "ai_decision_allowed",
            "next_phase_allowed",
        ):
            if artifact.get(field) is not False:
                errors.append(f"{artifact.get('artifact_id', '<unknown>')} {field} must be false.")


def _validate_safety_boundaries(boundaries: Any, errors: list[str]) -> None:
    if not isinstance(boundaries, Mapping):
        errors.append("safety_boundaries must be an object.")
        return
    for field in REQUIRED_TRUE_FIELDS:
        if boundaries.get(field) is not True:
            errors.append(f"safety_boundaries.{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if boundaries.get(field) is not False:
            errors.append(f"safety_boundaries.{field} must be false.")
    if boundaries.get("source_execution_commands_run") != []:
        errors.append("safety_boundaries.source_execution_commands_run must be empty.")
    if boundaries.get("final_recommendation") != "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE":
        errors.append("safety_boundaries.final_recommendation must keep next phase false.")


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        NOT_NEXT_DAY_STATEMENT,
        NO_EXECUTION_PROVIDER_API_STATEMENT,
        NOT_FOLDER_MOVE_CONTINUATION_STATEMENT,
        NOT_TMP_CLEANUP_CONTINUATION_STATEMENT,
        REVIEW_ONLY_DEMO_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day141 boundary statements.")


def write_day141_ai_assistance_review_demo_package_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day141_ai_assistance_review_demo_package(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day141_ai_assistance_review_demo_package_html(safe_report, html_path)
    return json_path, html_path


def write_day141_ai_assistance_review_demo_package_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    boundary_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    artifact_rows = _table_rows(
        (
            item.get("source_day", ""),
            item.get("name", ""),
            item.get("role", ""),
            item.get("path", ""),
            item.get("path_exists", False),
            item.get("execution_allowed", False),
        )
        for item in report.get("source_artifacts", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report['full_title']))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report['full_title']))}</h1>
  <p><strong>{html.escape(NOT_NEXT_DAY_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_PROVIDER_API_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NOT_FOLDER_MOVE_CONTINUATION_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NOT_TMP_CLEANUP_CONTINUATION_STATEMENT)}</strong></p>
  <p><strong>{html.escape(REVIEW_ONLY_DEMO_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Safety Boundaries</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
  <h2>Source Artifact Catalog</h2>
  <table><thead><tr><th>Day</th><th>Name</th><th>Role</th><th>Path</th><th>Exists</th><th>Execution Allowed</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day141_ai_assistance_review_demo_package(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day141_ai_assistance_review_demo_package(project_root)
    json_path, html_path = write_day141_ai_assistance_review_demo_package_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(f"agents_md_read_before_day141_work: {json.dumps(report['agents_md_read_before_day141_work'])}")
    print(f"agents_md_pre_read_result: {json.dumps(report['agents_md_pre_read_result'])}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"source_execution_commands_run: {json.dumps(report['source_execution_commands_run'])}")
    print(f"source_artifact_count: {json.dumps(report['source_artifact_count'])}")
    print(f"source_artifact_missing_count: {json.dumps(report['source_artifact_missing_count'])}")
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return "; ".join(str(item) for item in value) or "none"
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
