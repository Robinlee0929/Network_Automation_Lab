"""Day137 project folder organization decision gate.

This module produces decision-only evidence for future folder organization.
It does not move, delete, rename, rewrite imports, enable execution, enable
provider behavior, call APIs, use SSH, or implement the deferred AI Assistance
Review Demo Package.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 137
DAY_LABEL = "Day137"
TASK_NAME = "project-folder-organization-decision-gate"
TITLE = "Project Folder Organization Decision Gate"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "DECISION_ONLY"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "PROJECT_FOLDER_ORGANIZATION_DECISION_RECORDED"
BLOCKED_STATUS = "PROJECT_FOLDER_ORGANIZATION_DECISION_BLOCKED"
FINAL_RECOMMENDATION = "DO_NOT_REORGANIZE_YET_DECISION_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day137_project_folder_organization_decision_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day137_project_folder_organization_decision_gate.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day137_project_folder_organization_decision_gate.md"

NOT_NEXT_FEATURE_STATEMENT = "This is not the next day's feature."
DEFERRED_AI_ASSISTANCE_STATEMENT = "Original Day137 AI Assistance Review Demo Package is deferred."
NO_EXECUTION_PROVIDER_API_STATEMENT = "Execution / provider / API remain disabled."
NO_DIRECT_MOVE_STATEMENT = (
    "Day137 does not directly move folders because CLI, registry, dispatch, "
    "report-index, AI reviewer summary, tests, and generated report paths are coupled."
)

SAFETY_FALSE_FIELDS: Tuple[str, ...] = (
    "moves_allowed",
    "deletes_allowed",
    "renames_allowed",
    "import_path_changes_allowed",
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "next_feature_allowed",
    "original_day137_ai_assistance_demo_allowed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "mode",
    "moves_allowed",
    "deletes_allowed",
    "renames_allowed",
    "import_path_changes_allowed",
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "next_feature_allowed",
    "original_day137_ai_assistance_demo_allowed",
    "final_recommendation",
    "folder_groups_candidate_for_future_organization",
    "folder_groups_high_risk_do_not_move_first",
    "coupled_paths",
    "proof_required_before_future_move",
    "why_day137_does_not_move_folders",
    "why_not_next_feature",
    "why_execution_provider_api_remain_disabled",
    "day134_day136_stability_evidence",
)

DAY134_DAY136_EVIDENCE: Tuple[Dict[str, Any], ...] = (
    {
        "day": 134,
        "task": "disabled-ai-provider-adapter-contract",
        "path": Path("reports") / "lab-summary" / "day134_disabled_ai_provider_adapter_contract.json",
    },
    {
        "day": 135,
        "task": "ai-provider-disabled-by-default-safety-regression",
        "path": Path("reports") / "lab-summary" / "day135_ai_provider_disabled_by_default_safety_regression.json",
    },
    {
        "day": 136,
        "task": "ai-reviewer-export-package-integration",
        "path": Path("reports") / "lab-summary" / "day136_ai_reviewer_export_package_integration.json",
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_pre_read_before_changes": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_pre_read_before_changes": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_pre_read_before_changes": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_future_candidate_groups() -> list[Dict[str, Any]]:
    return [
        {
            "group": "documentation classification",
            "paths": ["docs/roadmap/**", "docs/ai/**", "docs/ai-intent/**"],
            "future_candidate": True,
            "allowed_now": False,
            "reason": "Documentation may be lower risk, but traceability links still require a separate dry-run gate.",
        },
        {
            "group": "generated report policy",
            "paths": ["reports/**", "summary/**"],
            "future_candidate": True,
            "allowed_now": False,
            "reason": "Report-index may depend on current locations; classify before moving any output.",
        },
        {
            "group": "test classification",
            "paths": ["tests/**"],
            "future_candidate": True,
            "allowed_now": False,
            "reason": "Pytest discovery and direct imports must be mapped before changing test layout.",
        },
        {
            "group": "future source package planning",
            "paths": ["network_lab/**", "network_lab/tasks/**", "network_lab/safety/**", "network_lab/ai_reviewer/**"],
            "future_candidate": True,
            "allowed_now": False,
            "reason": "Package paths do not become active until compatibility shims and import maps are approved.",
        },
    ]


def build_high_risk_groups() -> list[Dict[str, Any]]:
    return [
        {
            "group": "CLI entry point",
            "paths": ["network_lab.py"],
            "move_allowed_now": False,
            "risk": "BLOCKED",
            "reason": "Main workflow, task runners, report-index helpers, and tests depend on this entry point.",
        },
        {
            "group": "registry and dispatch modules",
            "paths": ["network_lab_task_registry.py", "network_lab_cli_dispatch.py"],
            "move_allowed_now": False,
            "risk": "HIGH",
            "reason": "Task choices, aliases, handler resolution, and CLI help depend on stable imports.",
        },
        {
            "group": "report-index modules and templates",
            "paths": ["network_lab.py", "dashboard_app.py", "dashboard_command_runner.py", "templates/**"],
            "move_allowed_now": False,
            "risk": "HIGH",
            "reason": "Report discovery and reviewer-visible paths may depend on fixed locations.",
        },
        {
            "group": "AI reviewer and provider-disabled evidence",
            "paths": [
                "disabled_ai_provider_adapter_contract.py",
                "ai_provider_disabled_by_default_safety_regression.py",
                "ai_reviewer_export_package_integration.py",
                "intent_ai_reviewer_summary_schema_contract.py",
                "intent_ai_reviewer_summary_fixture_renderer.py",
                "intent_ai_summary_prompt_contract.py",
                "intent_ai_summary_redaction_policy.py",
                "intent_ai_summary_audit_trail_binding.py",
                "intent_ai_summary_dashboard_card_integration.py",
            ],
            "move_allowed_now": False,
            "risk": "HIGH",
            "reason": "Day134-Day136 and related AI reviewer evidence must stay stable and provider/API disabled.",
        },
        {
            "group": "tests",
            "paths": ["tests/**"],
            "move_allowed_now": False,
            "risk": "MEDIUM",
            "reason": "Moving tests can affect pytest discovery, direct imports, fixtures, and report-index visibility checks.",
        },
        {
            "group": "generated reports and historical evidence",
            "paths": ["reports/**", "summary/**", "docs/demo/**", "docs/assets/**", "fixtures/**", "topology_profiles/**"],
            "move_allowed_now": False,
            "risk": "UNKNOWN",
            "reason": "Historical evidence, links, generated report paths, and reviewer workflows must stay traceable.",
        },
    ]


def build_coupled_paths() -> list[Dict[str, Any]]:
    return [
        {"path": "network_lab.py", "coupled_to": ["CLI", "dispatch", "report-index", "task catalog"]},
        {"path": "network_lab_task_registry.py", "coupled_to": ["registry", "CLI choices", "task handler resolution"]},
        {"path": "network_lab_cli_dispatch.py", "coupled_to": ["CLI parser", "dispatch", "registry"]},
        {"path": "dashboard_app.py", "coupled_to": ["report-index", "dashboard templates", "local report discovery"]},
        {"path": "dashboard_command_runner.py", "coupled_to": ["dashboard commands", "safety wording", "report views"]},
        {"path": "templates/**", "coupled_to": ["dashboard rendering", "report-index rendering"]},
        {"path": "tests/**", "coupled_to": ["pytest discovery", "direct imports", "CLI/registry/report-index regression"]},
        {"path": "reports/**", "coupled_to": ["report-index", "generated reviewer evidence"]},
        {"path": "summary/**", "coupled_to": ["historical generated evidence", "report-index discovery"]},
        {
            "path": "ai_reviewer_export_package_integration.py",
            "coupled_to": ["AI reviewer export package", "Day136 stability", "report-index"],
        },
        {
            "path": "ai_provider_disabled_by_default_safety_regression.py",
            "coupled_to": ["Day135 provider-disabled regression", "Day134 evidence"],
        },
        {
            "path": "disabled_ai_provider_adapter_contract.py",
            "coupled_to": ["Day134 provider-disabled contract", "no provider/API proof"],
        },
    ]


def build_future_move_proof_requirements() -> list[str]:
    return [
        "Separate user approval for the exact future move list.",
        "Separate dry-run-only day task before any physical move.",
        "Complete import consumer map for every source and test path.",
        "Compatibility shim plan for any module path that changes.",
        "Report-index path impact review for reports, summary files, templates, and docs links.",
        "Negative tests proving rejected scenarios do not reach adapters, brokers, runners, execution, providers, APIs, SSH, or live commands.",
        "Full pytest pass before and after any future dry-run or move proposal.",
        "report-index pass or documented acceptable WARN that is unrelated to safety or regression.",
        "Day134-Day136 AI reviewer/export/package evidence remains stable and provider/API disabled.",
    ]


def load_day134_day136_stability_evidence(project_root: Path) -> Dict[str, Any]:
    sections: list[Dict[str, Any]] = []
    errors: list[str] = []
    dangerous_true_fields = {
        "execution_enabled",
        "provider_enabled",
        "api_enabled",
        "provider_instantiated",
        "api_called",
        "execution_invoked",
        "execution_path_reached",
        "opens_execution_provider_or_api",
        "broker_runner_adapter_execution_enabled",
        "subprocess_provider_enabled",
        "provider_sdk_imported",
    }

    for source in DAY134_DAY136_EVIDENCE:
        relative_path = source["path"]
        path = Path(project_root) / relative_path
        section: Dict[str, Any] = {
            "day": source["day"],
            "task": source["task"],
            "path": relative_path.as_posix(),
            "read_only": True,
            "loaded": False,
            "status": "MISSING",
            "overall_status": "UNKNOWN",
            "dangerous_true_fields": [],
        }
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            section["read_error"] = f"Missing evidence: {relative_path.as_posix()}"
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue
        except json.JSONDecodeError as exc:
            section["status"] = "INVALID_JSON"
            section["read_error"] = f"Invalid JSON in {relative_path.as_posix()}: {exc.msg}"
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue
        except OSError as exc:
            section["status"] = "READ_ERROR"
            section["read_error"] = str(exc)
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue

        if not isinstance(loaded, dict):
            section["status"] = "INVALID_SHAPE"
            section["read_error"] = f"{relative_path.as_posix()} must contain a JSON object."
            errors.append(str(section["read_error"]))
            sections.append(section)
            continue

        dangerous = sorted(key for key in dangerous_true_fields if loaded.get(key) is True)
        section.update(
            {
                "loaded": True,
                "status": str(loaded.get("status", loaded.get("overall_status", "UNKNOWN"))),
                "overall_status": str(loaded.get("overall_status", loaded.get("status", "UNKNOWN"))),
                "dangerous_true_fields": dangerous,
                "provider_enabled": loaded.get("provider_enabled", False),
                "api_enabled": loaded.get("api_enabled", loaded.get("api_called", False)),
                "execution_enabled": loaded.get("execution_enabled", False),
            }
        )
        if dangerous:
            errors.append(f"Dangerous true fields in {relative_path.as_posix()}: {', '.join(dangerous)}")
        if section["overall_status"] != "PASS":
            errors.append(f"{relative_path.as_posix()} overall_status must be PASS.")
        sections.append(section)

    return {
        "source_day_range": "Day134-Day136",
        "source_count": len(sections),
        "loaded_source_count": sum(1 for section in sections if section.get("loaded") is True),
        "preserved": not errors,
        "sections": sections,
        "errors": errors,
    }


def build_project_folder_organization_decision_gate_report(project_root: Path) -> Dict[str, Any]:
    agents = build_agents_md_evidence(project_root)
    stability = load_day134_day136_stability_evidence(project_root)
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "status": "PENDING",
        "overall_status": "PENDING",
        "decision_only": True,
        "report_only": True,
        "deterministic": True,
        "local_repo_evidence_only": True,
        "moves_allowed": False,
        "deletes_allowed": False,
        "renames_allowed": False,
        "import_path_changes_allowed": False,
        "execution_allowed": False,
        "provider_allowed": False,
        "api_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "next_feature_allowed": False,
        "original_day137_ai_assistance_demo_allowed": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "not_next_feature_statement": NOT_NEXT_FEATURE_STATEMENT,
        "deferred_ai_assistance_statement": DEFERRED_AI_ASSISTANCE_STATEMENT,
        "no_execution_provider_api_statement": NO_EXECUTION_PROVIDER_API_STATEMENT,
        "no_direct_move_statement": NO_DIRECT_MOVE_STATEMENT,
        **agents,
        "folder_groups_candidate_for_future_organization": build_future_candidate_groups(),
        "folder_groups_high_risk_do_not_move_first": build_high_risk_groups(),
        "coupled_paths": build_coupled_paths(),
        "proof_required_before_future_move": build_future_move_proof_requirements(),
        "why_day137_does_not_move_folders": NO_DIRECT_MOVE_STATEMENT,
        "why_not_next_feature": (
            "Day137 is a project folder organization decision gate; the original AI Assistance "
            "Review Demo Package is explicitly deferred."
        ),
        "why_execution_provider_api_remain_disabled": (
            "The gate reads local evidence and emits reports only; it does not call providers, "
            "APIs, SSH, devices, adapters, brokers, runners, or live commands."
        ),
        "day134_day136_stability_evidence": stability,
        "future_day_sequence": {
            "day137_day140": "Folder organization decision and dry-run gates only.",
            "day141_day144": "Original AI Assistance line may resume only after organization risk is controlled.",
        },
        "explicit_no_change_proof": {
            "files_moved": False,
            "files_deleted": False,
            "files_renamed": False,
            "import_paths_changed": False,
            "generated_report_locations_changed": False,
        },
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

    if report.get("day") != DAY:
        errors.append("day must be 137.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("mode") != MODE:
        errors.append(f"mode must be {MODE}.")
    if report.get("final_recommendation") != FINAL_RECOMMENDATION:
        errors.append(f"final_recommendation must be {FINAL_RECOMMENDATION}.")

    for field in SAFETY_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("decision_only") is not True:
        errors.append("decision_only must be true.")
    if report.get("report_only") is not True:
        errors.append("report_only must be true.")
    if report.get("agents_md_found") is not True:
        errors.append("AGENTS.md must exist before Day137 work.")
    if report.get("agents_md_pre_read_before_changes") is not True:
        errors.append("AGENTS.md must be read before Day137 changes.")
    if report.get("agents_md_modified") is not False:
        errors.append("AGENTS.md modified must be false.")

    no_change = report.get("explicit_no_change_proof", {})
    if not isinstance(no_change, Mapping):
        errors.append("explicit_no_change_proof must be an object.")
    else:
        for key in (
            "files_moved",
            "files_deleted",
            "files_renamed",
            "import_paths_changed",
            "generated_report_locations_changed",
        ):
            if no_change.get(key) is not False:
                errors.append(f"explicit_no_change_proof.{key} must be false.")

    stability = report.get("day134_day136_stability_evidence", {})
    if not isinstance(stability, Mapping):
        errors.append("day134_day136_stability_evidence must be an object.")
    else:
        if stability.get("preserved") is not True:
            errors.append("Day134-Day136 stability evidence must be preserved.")
        if stability.get("loaded_source_count") != 3:
            errors.append("Day134-Day136 stability evidence must load three sources.")
        for stability_error in stability.get("errors", []):
            errors.append(str(stability_error))

    high_risk_groups = report.get("folder_groups_high_risk_do_not_move_first", [])
    high_risk_names = {item.get("group") for item in high_risk_groups if isinstance(item, Mapping)}
    required_high_risk = {
        "CLI entry point",
        "registry and dispatch modules",
        "report-index modules and templates",
        "AI reviewer and provider-disabled evidence",
        "tests",
        "generated reports and historical evidence",
    }
    missing_groups = sorted(required_high_risk - high_risk_names)
    if missing_groups:
        errors.append(f"Missing high-risk groups: {', '.join(missing_groups)}")

    return errors


def write_project_folder_organization_decision_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_project_folder_organization_decision_gate_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_project_folder_organization_decision_gate_html(safe_report, html_path)
    return json_path, html_path


def write_project_folder_organization_decision_gate_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    high_risk_rows = _table_rows(
        (
            item.get("group", ""),
            item.get("risk", ""),
            item.get("move_allowed_now", False),
            item.get("paths", []),
            item.get("reason", ""),
        )
        for item in report.get("folder_groups_high_risk_do_not_move_first", [])
    )
    coupled_rows = _table_rows(
        (item.get("path", ""), item.get("coupled_to", []))
        for item in report.get("coupled_paths", [])
    )
    stability_rows = _table_rows(
        (
            item.get("day", ""),
            item.get("task", ""),
            item.get("overall_status", ""),
            item.get("loaded", False),
            item.get("dangerous_true_fields", []),
            item.get("path", ""),
        )
        for item in report.get("day134_day136_stability_evidence", {}).get("sections", [])
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
  <p><strong>{html.escape(str(report['final_recommendation']))}</strong></p>
  <p>{html.escape(str(report['not_next_feature_statement']))}</p>
  <p>{html.escape(str(report['deferred_ai_assistance_statement']))}</p>
  <p>{html.escape(str(report['no_execution_provider_api_statement']))}</p>
  <h2>Decision Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Do Not Move First</h2>
  <table><thead><tr><th>Group</th><th>Risk</th><th>Move allowed now</th><th>Paths</th><th>Reason</th></tr></thead><tbody>{high_risk_rows}</tbody></table>
  <h2>Coupled Paths</h2>
  <table><thead><tr><th>Path</th><th>Coupled to</th></tr></thead><tbody>{coupled_rows}</tbody></table>
  <h2>Day134-Day136 Stability Evidence</h2>
  <table><thead><tr><th>Day</th><th>Task</th><th>Overall status</th><th>Loaded</th><th>Dangerous true fields</th><th>Path</th></tr></thead><tbody>{stability_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_project_folder_organization_decision_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_project_folder_organization_decision_gate_report(project_root)
    json_path, html_path = write_project_folder_organization_decision_gate_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(report["not_next_feature_statement"])
    print(report["deferred_ai_assistance_statement"])
    print(report["no_execution_provider_api_statement"])
    print(report["why_day137_does_not_move_folders"])
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    for field in SAFETY_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
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


def main() -> int:
    report = build_project_folder_organization_decision_gate_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
