"""Day138 project folder organization dry-run inventory gate.

This module inventories current repository file groups for reviewer-visible
folder organization planning. It is dry-run only and does not move, delete,
rename, rewrite imports, enable execution/provider/API behavior, call SSH, or
reach adapters, brokers, runners, mapped execution, or live commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents


DAY = 138
DAY_LABEL = "Day138"
TASK_NAME = "project-folder-organization-dry-run-inventory-gate"
TITLE = "Project Folder Organization Dry-Run Inventory Gate"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "DRY_RUN_INVENTORY_ONLY"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_RECORDED"
BLOCKED_STATUS = "PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_DRY_RUN_INVENTORY_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day138_project_folder_organization_dry_run_inventory_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day138_project_folder_organization_dry_run_inventory_gate.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day138_project_folder_organization_dry_run_inventory_gate.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day138_project_folder_organization_dry_run_inventory_gate.md"

NOT_NEXT_FEATURE_STATEMENT = "This is not the next day's feature."
NO_EXECUTION_PROVIDER_API_STATEMENT = "No execution, provider, or API is enabled."

FORBIDDEN_ACTIONS: Dict[str, bool] = {
    "move": False,
    "delete": False,
    "rename": False,
    "import_path_change": False,
    "execution_enabled": False,
    "provider_enabled": False,
    "api_enabled": False,
    "ssh_allowed": False,
    "live_command_allowed": False,
}

REQUIRED_GROUPS: Tuple[str, ...] = (
    "root CLI / entrypoint files",
    "task registry / dispatch files",
    "intent / task modules",
    "tests",
    "docs / roadmap",
    "docs / ai-intent",
    "reports / lab-summary",
    "fixtures / samples",
    "safety / review-only related files",
    "other / uncategorized",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "mode",
    "overall_status",
    "agents_md_pre_read",
    "forbidden_actions",
    "inventory_groups",
    "risk_marking_rules",
    "final_recommendation",
    "next_phase_allowed",
    "not_next_day_feature_statement",
    "no_execution_provider_api_statement",
)

EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_PART_PREFIXES = (".pytest-", ".pytest_")
ROOT_CLI_NAMES = {
    "network_lab.py",
    "dashboard_app.py",
    "dashboard_command_runner.py",
    "performance_test.py",
    "performance_regression.py",
    "topology_summary.py",
}
TASK_REGISTRY_DISPATCH_NAMES = {
    "network_lab_task_registry.py",
    "network_lab_cli_dispatch.py",
}
SAFETY_REVIEW_MARKERS = (
    "safety",
    "guard",
    "reviewer",
    "readonly",
    "read_only",
    "runtime",
    "broker",
    "adapter",
    "invariant",
    "approval",
    "disabled",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_pre_read": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_pre_read": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_pre_read": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_project_folder_organization_dry_run_inventory_gate_report(project_root: Path) -> Dict[str, Any]:
    files = _repo_files(project_root)
    test_reference_counts = _build_test_reference_counts(project_root, files)
    inventory_groups = _build_inventory_groups(files, test_reference_counts)
    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "overall_status": "PENDING",
        "status": "PENDING",
        "report_only": True,
        "dry_run_only": True,
        "mock_safe": True,
        "local_repo_inventory_only": True,
        "no_files_moved": True,
        "no_files_deleted": True,
        "no_files_renamed": True,
        "no_import_paths_changed": True,
        "forbidden_actions": dict(FORBIDDEN_ACTIONS),
        "next_phase_allowed": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "not_next_day_feature_statement": NOT_NEXT_FEATURE_STATEMENT,
        "no_execution_provider_api_statement": NO_EXECUTION_PROVIDER_API_STATEMENT,
        "explicit_scope_statements": [
            NOT_NEXT_FEATURE_STATEMENT,
            NO_EXECUTION_PROVIDER_API_STATEMENT,
            "Dry-run inventory report only; no folder organization is performed.",
            "No adapter, broker, runner, or mapped execution path is invoked.",
        ],
        **build_agents_md_evidence(project_root),
        "inventory_summary": {
            "total_repo_files_seen": len(files),
            "inventory_group_count": len(inventory_groups),
            "grouping_note": "Thematic inventory groups may overlap for safety review visibility.",
        },
        "inventory_groups": inventory_groups,
        "risk_marking_rules": build_risk_marking_rules(),
        "explicit_no_change_proof": {
            "move": False,
            "delete": False,
            "rename": False,
            "import_path_change": False,
            "execution_enabled": False,
            "provider_enabled": False,
            "api_enabled": False,
            "ssh_allowed": False,
            "live_command_allowed": False,
        },
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    return report


def build_risk_marking_rules() -> list[Dict[str, Any]]:
    return [
        {
            "rule": "Files whose movement would affect import paths are HIGH.",
            "risk_level": "HIGH",
            "applies_to": ["root Python modules", "intent/task modules", "registry/dispatch modules"],
        },
        {
            "rule": "CLI entrypoint, dispatch, and registry files are HIGH.",
            "risk_level": "HIGH",
            "applies_to": ["network_lab.py", "network_lab_cli_dispatch.py", "network_lab_task_registry.py"],
        },
        {
            "rule": "Files heavily referenced by tests are HIGH.",
            "risk_level": "HIGH",
            "applies_to": ["tests", "source modules referenced by tests"],
        },
        {
            "rule": "Safety, guard, invariant, review-only, disabled-provider, adapter, broker, and runner related files are HIGH.",
            "risk_level": "HIGH",
            "applies_to": ["safety / review-only related files"],
        },
        {
            "rule": "Docs-only groups are LOW.",
            "risk_level": "LOW",
            "applies_to": ["docs / roadmap", "docs / ai-intent"],
        },
        {
            "rule": "Generated reports are LOW for this inventory because they are not moved and remain reviewer evidence.",
            "risk_level": "LOW",
            "applies_to": ["reports / lab-summary"],
        },
        {
            "rule": "Fixtures and samples are LOW when unreferenced and MEDIUM when referenced by tests or task code.",
            "risk_level": "LOW / MEDIUM",
            "applies_to": ["fixtures / samples"],
        },
    ]


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    if report.get("day") != DAY:
        errors.append("day must be 138.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("mode") != MODE:
        errors.append(f"mode must be {MODE}.")
    if report.get("final_recommendation") != FINAL_RECOMMENDATION:
        errors.append(f"final_recommendation must be {FINAL_RECOMMENDATION}.")
    if report.get("next_phase_allowed") is not False:
        errors.append("next_phase_allowed must be false.")
    if report.get("not_next_day_feature_statement") != NOT_NEXT_FEATURE_STATEMENT:
        errors.append("not_next_day_feature_statement must match required wording.")
    if report.get("no_execution_provider_api_statement") != NO_EXECUTION_PROVIDER_API_STATEMENT:
        errors.append("no_execution_provider_api_statement must match required wording.")
    if report.get("agents_md_pre_read") is not True:
        errors.append("AGENTS.md pre-read evidence must be true.")

    forbidden_actions = report.get("forbidden_actions", {})
    if not isinstance(forbidden_actions, Mapping):
        errors.append("forbidden_actions must be an object.")
    else:
        for key, expected in FORBIDDEN_ACTIONS.items():
            if forbidden_actions.get(key) is not expected:
                errors.append(f"forbidden_actions.{key} must be false.")

    explicit_no_change = report.get("explicit_no_change_proof", {})
    if not isinstance(explicit_no_change, Mapping):
        errors.append("explicit_no_change_proof must be an object.")
    else:
        for key in FORBIDDEN_ACTIONS:
            if explicit_no_change.get(key) is not False:
                errors.append(f"explicit_no_change_proof.{key} must be false.")

    groups = report.get("inventory_groups", [])
    if not isinstance(groups, list) or not groups:
        errors.append("inventory_groups must be a non-empty list.")
    else:
        group_names = {group.get("group_name") for group in groups if isinstance(group, Mapping)}
        for required_group in REQUIRED_GROUPS:
            if required_group not in group_names:
                errors.append(f"Missing inventory group: {required_group}")
        risks = {group.get("risk_level") for group in groups if isinstance(group, Mapping)}
        if "HIGH" not in risks:
            errors.append("At least one HIGH risk group is required.")
        if "LOW" not in risks:
            errors.append("At least one LOW risk group is required.")
        for group in groups:
            if not isinstance(group, Mapping):
                errors.append("Each inventory group must be an object.")
                continue
            for field in (
                "group_name",
                "file_count",
                "sample_files",
                "current_location",
                "future_organization_candidate",
                "risk_level",
                "reason",
            ):
                if field not in group:
                    errors.append(f"inventory group is missing {field}.")

    return errors


def write_project_folder_organization_dry_run_inventory_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_project_folder_organization_dry_run_inventory_gate_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(safe_report, indent=2), encoding="utf-8")
    write_project_folder_organization_dry_run_inventory_gate_html(safe_report, html_path)
    return json_path, html_path


def write_project_folder_organization_dry_run_inventory_gate_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    forbidden_rows = _table_rows((key, value) for key, value in report["forbidden_actions"].items())
    inventory_rows = _table_rows(
        (
            group.get("group_name", ""),
            group.get("risk_level", ""),
            group.get("file_count", 0),
            group.get("current_location", ""),
            group.get("future_organization_candidate", False),
            group.get("sample_files", []),
            group.get("reason", ""),
        )
        for group in report.get("inventory_groups", [])
    )
    rules_rows = _table_rows(
        (rule.get("risk_level", ""), rule.get("rule", ""), rule.get("applies_to", []))
        for rule in report.get("risk_marking_rules", [])
    )
    write_text_with_parents(
        output_path,
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
  <p>{html.escape(str(report['not_next_day_feature_statement']))}</p>
  <p>{html.escape(str(report['no_execution_provider_api_statement']))}</p>
  <p>next_phase_allowed: <code>{html.escape(json.dumps(report['next_phase_allowed']))}</code></p>
  <h2>Forbidden Actions</h2>
  <table><thead><tr><th>Action</th><th>Allowed / enabled</th></tr></thead><tbody>{forbidden_rows}</tbody></table>
  <h2>Inventory Groups</h2>
  <table><thead><tr><th>Group</th><th>Risk</th><th>File count</th><th>Current location</th><th>Future candidate</th><th>Sample files</th><th>Reason</th></tr></thead><tbody>{inventory_rows}</tbody></table>
  <h2>Risk Marking Rules</h2>
  <table><thead><tr><th>Risk</th><th>Rule</th><th>Applies to</th></tr></thead><tbody>{rules_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_project_folder_organization_dry_run_inventory_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_project_folder_organization_dry_run_inventory_gate_report(project_root)
    json_path, html_path = write_project_folder_organization_dry_run_inventory_gate_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(report["not_next_day_feature_statement"])
    print(report["no_execution_provider_api_statement"])
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"agents_md_pre_read: {json.dumps(report['agents_md_pre_read'])}")
    for key, value in report["forbidden_actions"].items():
        print(f"forbidden_actions.{key}: {json.dumps(value)}")
    print(f"inventory_group_count: {len(report['inventory_groups'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _repo_files(project_root: Path) -> list[Path]:
    root = Path(project_root)
    files: list[Path] = []
    for path in root.rglob("*"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if any(part.startswith(EXCLUDED_PART_PREFIXES) for part in relative.parts):
            continue
        if path.is_file():
            files.append(relative)
    return sorted(files, key=lambda item: item.as_posix())


def _build_inventory_groups(files: Sequence[Path], test_reference_counts: Mapping[str, int]) -> list[Dict[str, Any]]:
    primary_classified: set[Path] = set()

    root_cli = [path for path in files if len(path.parts) == 1 and path.name in ROOT_CLI_NAMES]
    primary_classified.update(root_cli)
    registry_dispatch = [path for path in files if len(path.parts) == 1 and path.name in TASK_REGISTRY_DISPATCH_NAMES]
    primary_classified.update(registry_dispatch)
    intent_task = [
        path
        for path in files
        if len(path.parts) == 1
        and path.suffix == ".py"
        and (
            path.name.startswith("intent_")
            or path.name.startswith("mikrotik_")
            or path.name.startswith("cisco_")
            or path.name.startswith("disabled_ai_")
            or path.name.startswith("ai_")
            or path.name == "project_folder_organization_decision_gate.py"
        )
    ]
    primary_classified.update(intent_task)
    tests = [path for path in files if path.parts[:1] == ("tests",)]
    primary_classified.update(tests)
    roadmap_docs = [path for path in files if path.parts[:2] == ("docs", "roadmap")]
    primary_classified.update(roadmap_docs)
    ai_intent_docs = [path for path in files if path.parts[:2] == ("docs", "ai-intent")]
    primary_classified.update(ai_intent_docs)
    lab_summary_reports = [path for path in files if path.parts[:2] == ("reports", "lab-summary")]
    primary_classified.update(lab_summary_reports)
    fixtures_samples = [
        path
        for path in files
        if path.parts[:1] in {("fixtures",), ("topology_profiles",)}
        or path.name.endswith(".example.json")
        or path.parts[:1] == ("config",)
    ]
    primary_classified.update(fixtures_samples)
    safety_review = [
        path
        for path in files
        if any(marker in path.as_posix().lower() for marker in SAFETY_REVIEW_MARKERS)
    ]
    other = [path for path in files if path not in primary_classified and path not in safety_review]

    fixtures_reference_count = sum(test_reference_counts.get(path.as_posix(), 0) for path in fixtures_samples)
    fixtures_risk = "MEDIUM" if fixtures_reference_count else "LOW"
    fixtures_reason = (
        "Fixture/sample files are referenced by tests or task code; future organization needs consumer mapping."
        if fixtures_reference_count
        else "Fixture/sample files look low risk in this dry-run inventory, but no move is allowed here."
    )

    return [
        _group(
            "root CLI / entrypoint files",
            root_cli,
            "repo root",
            True,
            "HIGH",
            "Moving root entrypoints can change invocation behavior and import paths.",
        ),
        _group(
            "task registry / dispatch files",
            registry_dispatch,
            "repo root",
            True,
            "HIGH",
            "CLI choices, dispatch, and task handler resolution must remain stable.",
        ),
        _group(
            "intent / task modules",
            intent_task,
            "repo root intent_*.py and task modules",
            True,
            "HIGH",
            "Root task modules are imported directly by tests and CLI wiring; movement would affect import paths.",
        ),
        _group(
            "tests",
            tests,
            "tests/",
            True,
            "HIGH",
            "Tests are broad import consumers and pytest discovery can change if paths move.",
        ),
        _group(
            "docs / roadmap",
            roadmap_docs,
            "docs/roadmap/",
            True,
            "LOW",
            "Docs-only files are low risk for inventory purposes, but still not moved by this gate.",
        ),
        _group(
            "docs / ai-intent",
            ai_intent_docs,
            "docs/ai-intent/",
            True,
            "LOW",
            "AI intent docs are documentation-only inventory items and remain in place.",
        ),
        _group(
            "reports / lab-summary",
            lab_summary_reports,
            "reports/lab-summary/",
            True,
            "LOW",
            "Generated lab-summary reports are reviewer evidence; this task only records their current location.",
        ),
        _group(
            "fixtures / samples",
            fixtures_samples,
            "fixtures/, topology_profiles/, config/, root *.example.json",
            True,
            fixtures_risk,
            fixtures_reason,
        ),
        _group(
            "safety / review-only related files",
            safety_review,
            "repo-wide safety, guard, review-only, disabled, adapter, broker, and runtime markers",
            True,
            "HIGH",
            "Safety and review-only evidence must preserve no-execution proofs and should not be moved first.",
        ),
        _group(
            "other / uncategorized",
            other,
            "repo files outside the named inventory groups",
            False,
            "MEDIUM",
            "Uncategorized files need manual review before any future organization proposal.",
        ),
    ]


def _group(
    group_name: str,
    files: Sequence[Path],
    current_location: str,
    future_organization_candidate: bool,
    risk_level: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "group_name": group_name,
        "file_count": len(files),
        "sample_files": [path.as_posix() for path in files[:8]],
        "current_location": current_location,
        "future_organization_candidate": future_organization_candidate,
        "risk_level": risk_level,
        "reason": reason,
    }


def _build_test_reference_counts(project_root: Path, files: Sequence[Path]) -> Dict[str, int]:
    tests_dir = Path(project_root) / "tests"
    texts: list[str] = []
    if tests_dir.exists():
        for test_path in sorted(tests_dir.glob("test_*.py")):
            try:
                texts.append(test_path.read_text(encoding="utf-8"))
            except OSError:
                continue
    joined_tests = "\n".join(texts)
    counts: Dict[str, int] = {}
    for path in files:
        path_text = path.as_posix()
        stem = path.stem
        counts[path_text] = joined_tests.count(path.name) + joined_tests.count(stem)
    return counts


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
    report = build_project_folder_organization_dry_run_inventory_gate_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
