"""Day144 v0.4 AI assistance compatibility review.

This module reviews existing Day127-Day143 AI assistance artifacts for a future
v0.4 review package. It is local-only, deterministic, report-only evidence and
does not call providers, APIs, OpenAI API, runners, adapters, SSH, NETCONF,
RESTCONF, RouterOS, or live device paths.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 144
DAY_LABEL = "Day144"
TASK_NAME = "v0.4-ai-assistance-compatibility-review"
TITLE = "v0.4 AI Assistance Compatibility Review"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_COMPATIBILITY_REVIEW"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "V0_4_AI_ASSISTANCE_COMPATIBILITY_REVIEW_READY"
BLOCKED_STATUS = "V0_4_AI_ASSISTANCE_COMPATIBILITY_REVIEW_BLOCKED"
FINAL_RECOMMENDATION = "V0_4_COMPATIBLE_REVIEW_ONLY_KEEP_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day144_v04_ai_assistance_compatibility_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day144_v04_ai_assistance_compatibility_review.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day144_v04_ai_assistance_compatibility_review.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day144_v04_ai_assistance_compatibility_review.md"

NOT_DAY145_STATEMENT = "Day144 is not Day145 and does not implement the next-day feature."
NO_EXECUTION_PROVIDER_API_STATEMENT = "Day144 keeps execution / provider / API closed."
NO_OPENAI_PROVIDER_STATEMENT = "Day144 does not call OpenAI API or any AI provider."
NO_LIVE_DEVICE_STATEMENT = "Day144 does not use SSH, NETCONF, RESTCONF, RouterOS, or live device access."
NO_FOLDER_MOVE_REDO_STATEMENT = "Day144 does not redo the folder move compatibility gate or perform any folder move."
V04_REVIEW_ONLY_STATEMENT = "Day144 is a v0.4 AI assistance compatibility review only."

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "compatibility_review_only",
    "deterministic_static_data_only",
    "local_repo_metadata_only",
    "future_v04_review_package_compatible",
    "existing_day127_day143_artifacts_remain_compatible",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "openai_api_called",
    "ai_provider_called",
    "model_invocation_allowed",
    "execution_runner_behavior_added",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "routeros_allowed",
    "configuration_change_allowed",
    "secrets_allowed",
    "credentials_allowed",
    "environment_provider_activation_allowed",
    "next_phase_allowed",
    "day145_implemented",
    "is_next_day_feature",
    "folder_move_compatibility_gate_redone",
    "folder_move_performed",
    "folder_organization_logic_modified",
    "actual_folder_move_performed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "overall_status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day144_work",
    "source_day_range",
    "source_artifact_count",
    "compatibility_checks",
    "compatibility_conclusion",
    "final_recommendation",
)

SOURCE_ARTIFACTS: Tuple[Dict[str, str], ...] = (
    {
        "day": "Day127",
        "name": "AI Reviewer Summary Schema Contract",
        "path": "docs/ai-intent/day127_ai_reviewer_summary_schema_contract.md",
        "role": "schema foundation for future v0.4 review packages",
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
        "role": "no-secret reviewer text policy",
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
        "role": "display-only dashboard evidence",
    },
    {
        "day": "Day133",
        "name": "Disabled AI Provider Interface Boundary",
        "path": "docs/ai-intent/day133_disabled_ai_provider_interface_boundary.md",
        "role": "provider boundary remains disabled",
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
        "role": "disabled-by-default regression evidence",
    },
    {
        "day": "Day136",
        "name": "AI Reviewer Export Package Integration",
        "path": "docs/roadmap/day136_ai_reviewer_export_package_integration.md",
        "role": "review-only export package context",
    },
    {
        "day": "Day137",
        "name": "Project Folder Organization Decision Gate",
        "path": "docs/roadmap/day137_project_folder_organization_decision_gate.md",
        "role": "folder organization decision context only",
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
        "role": "docs-only move plan context only",
    },
    {
        "day": "Day140",
        "name": "Folder Move Compatibility Gate",
        "path": "docs/ai-intent/day140_folder_move_compatibility_gate.md",
        "role": "folder move compatibility context only; not redone",
    },
    {
        "day": "Day141",
        "name": "AI Assistance Review Demo Package",
        "path": "docs/ai-intent/day141_ai_assistance_review_demo_package.md",
        "role": "review-only demo package",
    },
    {
        "day": "Day142",
        "name": "AI Summary to Dry-run Draft Display Contract",
        "path": "docs/ai-intent/day142_ai_summary_to_dry_run_draft_display_contract.md",
        "role": "display-only dry-run draft payload contract",
    },
    {
        "day": "Day143",
        "name": "Dry-run Draft Safety Diff Viewer",
        "path": "docs/ai-intent/day143_dry_run_draft_safety_diff_viewer.md",
        "role": "display-only safety diff evidence",
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day144_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day144_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_source_artifact_records(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    records: list[Dict[str, Any]] = []
    for index, artifact in enumerate(SOURCE_ARTIFACTS, start=1):
        path = artifact["path"]
        records.append(
            {
                "artifact_id": f"DAY144_SOURCE_ARTIFACT_{index:02d}",
                "source_day": artifact["day"],
                "name": artifact["name"],
                "path": path,
                "path_exists": (root / path).exists(),
                "role": artifact["role"],
                "review_mode": "static_reference_only",
                "compatibility_status": "PASS",
                "execution_allowed": False,
                "provider_allowed": False,
                "api_allowed": False,
                "next_phase_allowed": False,
            }
        )
    return records


def build_compatibility_checks(source_artifacts: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    artifact_list = list(source_artifacts)
    return [
        {
            "check_id": "DAY144-COMPAT-001",
            "name": "Day127-Day143 artifact chain present",
            "status": "PASS" if all(item.get("path_exists") is True for item in artifact_list) else "FAIL",
            "review_only": True,
            "next_phase_allowed": False,
        },
        {
            "check_id": "DAY144-COMPAT-002",
            "name": "Provider and API boundary remains disabled",
            "status": "PASS",
            "provider_allowed": False,
            "api_allowed": False,
            "openai_api_called": False,
            "environment_provider_activation_allowed": False,
        },
        {
            "check_id": "DAY144-COMPAT-003",
            "name": "Execution and live device boundary remains closed",
            "status": "PASS",
            "execution_allowed": False,
            "execution_runner_behavior_added": False,
            "live_device_access_allowed": False,
            "ssh_allowed": False,
            "netconf_allowed": False,
            "restconf_allowed": False,
            "routeros_allowed": False,
        },
        {
            "check_id": "DAY144-COMPAT-004",
            "name": "Folder move compatibility gate not redone",
            "status": "PASS",
            "folder_move_compatibility_gate_redone": False,
            "folder_move_performed": False,
            "folder_organization_logic_modified": False,
        },
        {
            "check_id": "DAY144-COMPAT-005",
            "name": "Day145 remains blocked",
            "status": "PASS",
            "day145_implemented": False,
            "is_next_day_feature": False,
            "next_phase_allowed": False,
        },
    ]


def build_day144_v04_ai_assistance_compatibility_review(project_root: Path) -> Dict[str, Any]:
    source_artifacts = build_source_artifact_records(project_root)
    compatibility_checks = build_compatibility_checks(source_artifacts)
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "overall_status": "PENDING",
        "status": "PENDING",
        **build_agents_md_evidence(project_root),
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        "source_day_range": "Day127-Day143",
        "source_artifacts": source_artifacts,
        "source_artifact_count": len(source_artifacts),
        "source_artifact_missing_count": sum(1 for item in source_artifacts if item["path_exists"] is not True),
        "compatibility_checks": compatibility_checks,
        "compatibility_conclusion": "COMPATIBLE_WITH_FUTURE_V0_4_REVIEW_PACKAGE_REVIEW_ONLY",
        "explicit_boundary_statements": [
            NOT_DAY145_STATEMENT,
            NO_EXECUTION_PROVIDER_API_STATEMENT,
            NO_OPENAI_PROVIDER_STATEMENT,
            NO_LIVE_DEVICE_STATEMENT,
            NO_FOLDER_MOVE_REDO_STATEMENT,
            V04_REVIEW_ONLY_STATEMENT,
        ],
        "reviewer_next_action": "Review the Day144 compatibility report; do not enable Day145, execution, providers, APIs, live access, SSH, NETCONF, RESTCONF, RouterOS, folder moves, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
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
        "source_day_range": "Day127-Day143",
        "compatibility_conclusion": "COMPATIBLE_WITH_FUTURE_V0_4_REVIEW_PACKAGE_REVIEW_ONLY",
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day144_work") is not True:
        errors.append("agents_md_read_before_day144_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_source_artifacts(report.get("source_artifacts", []), errors)
    _validate_compatibility_checks(report.get("compatibility_checks", []), errors)
    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)
    return errors


def _validate_source_artifacts(artifacts: Any, errors: list[str]) -> None:
    if not isinstance(artifacts, list) or len(artifacts) != len(SOURCE_ARTIFACTS):
        errors.append("source_artifacts must cover Day127-Day143.")
        return
    expected_days = [f"Day{day}" for day in range(127, 144)]
    days = [artifact.get("source_day") for artifact in artifacts if isinstance(artifact, Mapping)]
    if days != expected_days:
        errors.append("source_artifacts must be ordered Day127 through Day143.")
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            errors.append("Each source artifact must be an object.")
            continue
        if artifact.get("path_exists") is not True:
            errors.append(f"{artifact.get('path', '<unknown>')} must exist for Day144 compatibility review.")
        if artifact.get("review_mode") != "static_reference_only":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} review_mode must be static_reference_only.")
        if artifact.get("compatibility_status") != "PASS":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} compatibility_status must be PASS.")
        for field in ("execution_allowed", "provider_allowed", "api_allowed", "next_phase_allowed"):
            if artifact.get(field) is not False:
                errors.append(f"{artifact.get('artifact_id', '<unknown>')} {field} must be false.")


def _validate_compatibility_checks(checks: Any, errors: list[str]) -> None:
    if not isinstance(checks, list) or len(checks) != 5:
        errors.append("compatibility_checks must contain five Day144 checks.")
        return
    for check in checks:
        if not isinstance(check, Mapping):
            errors.append("Each compatibility check must be an object.")
            continue
        if check.get("status") != "PASS":
            errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")
        for field, value in check.items():
            if field in REQUIRED_FALSE_FIELDS and value is not False:
                errors.append(f"{check.get('check_id', '<unknown>')} {field} must be false.")


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        NOT_DAY145_STATEMENT,
        NO_EXECUTION_PROVIDER_API_STATEMENT,
        NO_OPENAI_PROVIDER_STATEMENT,
        NO_LIVE_DEVICE_STATEMENT,
        NO_FOLDER_MOVE_REDO_STATEMENT,
        V04_REVIEW_ONLY_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day144 boundary statements.")


def write_day144_v04_ai_assistance_compatibility_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day144_v04_ai_assistance_compatibility_review(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day144_v04_ai_assistance_compatibility_review_html(safe_report, html_path)
    return json_path, html_path


def write_day144_v04_ai_assistance_compatibility_review_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
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
            item.get("compatibility_status", ""),
        )
        for item in report.get("source_artifacts", [])
    )
    check_rows = _table_rows(
        (
            item.get("check_id", ""),
            item.get("name", ""),
            item.get("status", ""),
            item.get("next_phase_allowed", False),
        )
        for item in report.get("compatibility_checks", [])
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
  <p><strong>{html.escape(NOT_DAY145_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_PROVIDER_API_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_OPENAI_PROVIDER_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_LIVE_DEVICE_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_FOLDER_MOVE_REDO_STATEMENT)}</strong></p>
  <p><strong>{html.escape(V04_REVIEW_ONLY_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Compatibility Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Next Phase Allowed</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Safety Boundaries</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
  <h2>Source Artifacts</h2>
  <table><thead><tr><th>Day</th><th>Name</th><th>Role</th><th>Path</th><th>Exists</th><th>Compatibility</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day144_v04_ai_assistance_compatibility_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day144_v04_ai_assistance_compatibility_review(project_root)
    json_path, html_path = write_day144_v04_ai_assistance_compatibility_review_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md read before Day144 work: {json.dumps(report['agents_md_read_before_day144_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day144 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(f"source_day_range: {json.dumps(report['source_day_range'])}")
    print(f"source_artifact_count: {report['source_artifact_count']}")
    print(f"source_artifact_missing_count: {report['source_artifact_missing_count']}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"compatibility_conclusion: {json.dumps(report['compatibility_conclusion'])}")
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
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
