"""Day140 folder move compatibility gate.

This module produces reviewer-visible compatibility evidence for deciding
whether a future first-batch docs-only move review may begin. It does not move
or rename files, edit imports, enable execution/provider/API behavior, call
SSH/NETCONF/RESTCONF, or invoke adapters, brokers, runners, or live commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple


DAY = 140
DAY_LABEL = "Day140"
TASK_NAME = "folder-move-compatibility-gate"
TITLE = "Folder Move Compatibility Gate"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY"
SOURCE_SCOPE = "docs-only compatibility review"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "FOLDER_MOVE_COMPATIBILITY_GATE_READY_FOR_FUTURE_DOCS_ONLY_REVIEW"
BLOCKED_STATUS = "FOLDER_MOVE_COMPATIBILITY_GATE_BLOCKED"
READY_RECOMMENDATION = "READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW"
NOT_READY_RECOMMENDATION = "NOT_READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW"
REVIEW_REQUIRED_RECOMMENDATION = "REVIEW_REQUIRED_BEFORE_DOCS_ONLY_MOVE"
REPORT_JSON = Path("reports") / "lab-summary" / "day140_folder_move_compatibility_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day140_folder_move_compatibility_gate.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day140_folder_move_compatibility_gate.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day140_folder_move_compatibility_gate.md"

NOT_NEXT_DAY_FEATURE_STATEMENT = "This is not the next-day feature implementation."
NO_MOVE_STATEMENT = "No files or folders are moved by Day140."
NO_EXECUTION_PROVIDER_API_STATEMENT = "No execution, provider, or API is enabled."
REVIEW_ONLY_DECISION_STATEMENT = (
    "Readiness only means a future docs-only move review may begin; it never authorizes moving files now."
)

SAFETY_FALSE_FIELDS: Tuple[str, ...] = (
    "execution_allowed",
    "provider_enabled",
    "api_enabled",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "live_command_allowed",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "next_day_feature_implemented",
    "move_allowed_now",
)

COUNT_ZERO_FIELDS: Tuple[str, ...] = (
    "files_moved_count",
    "folders_moved_count",
    "imports_modified_count",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "title",
    "mode",
    "source_scope",
    "agents_md_read_before_day140_work",
    "agents_md_pre_read_result",
    "files_moved_count",
    "folders_moved_count",
    "imports_modified_count",
    "execution_allowed",
    "provider_enabled",
    "api_enabled",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "live_command_allowed",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "next_day_feature_implemented",
    "docs_only_move_candidates_identifiable",
    "candidate_docs_isolated_enough_for_review",
    "import_sensitive_files_excluded_from_first_batch",
    "cli_task_test_report_index_references_identified",
    "first_batch_docs_only_move_review_allowed",
    "final_recommendation",
)

DOCS_ONLY_CANDIDATE_PATHS: Tuple[Tuple[str, str], ...] = (
    (
        "docs/roadmap/pre_day137_project_folder_safety_inventory_no_move_plan.md",
        "Pre-Day137 project-folder no-move inventory evidence.",
    ),
    (
        "docs/roadmap/pre_day137_2_project_folder_organization_policy_move_risk_matrix.md",
        "Pre-Day137-2 project-folder policy and move-risk evidence.",
    ),
    (
        "docs/roadmap/day137_project_folder_organization_decision_gate.md",
        "Day137 project-folder organization decision gate evidence.",
    ),
    (
        "docs/roadmap/day138_project_folder_organization_dry_run_inventory_gate.md",
        "Day138 dry-run inventory evidence.",
    ),
    (
        "docs/roadmap/day139_docs_only_move_dry_run_evidence_plan.md",
        "Day139 docs-only dry-run evidence plan.",
    ),
    (
        ROADMAP_DOC.as_posix(),
        "Day140 compatibility gate roadmap documentation.",
    ),
    (
        "docs/ai-intent/day138_project_folder_organization_dry_run_inventory_gate.md",
        "Day138 AI-intent project-folder dry-run evidence.",
    ),
    (
        "docs/ai-intent/day139_docs_only_move_dry_run_evidence_plan.md",
        "Day139 AI-intent docs-only dry-run evidence.",
    ),
    (
        AI_INTENT_DOC.as_posix(),
        "Day140 AI-intent compatibility gate documentation.",
    ),
)

IMPORT_SENSITIVE_EXCLUSIONS: Tuple[Tuple[str, str], ...] = (
    ("*.py", "Python source files may contain import paths and are excluded from first-batch docs-only review."),
    ("tests/**/*.py", "Tests may assert documentation/report-index paths and are excluded from first-batch docs-only review."),
    ("network_lab.py", "CLI and report-index metadata may reference docs and must not be moved."),
    ("network_lab_cli_dispatch.py", "CLI task dispatch must remain stable and must not be moved."),
    ("network_lab_task_registry.py", "Task registry identifiers must remain stable and must not be moved."),
)

REFERENCE_SURFACES: Tuple[Tuple[str, str], ...] = (
    ("network_lab.py", "CLI task catalog and report-index metadata"),
    ("network_lab_cli_dispatch.py", "CLI parser examples and task handler registration"),
    ("network_lab_task_registry.py", "Canonical task name registration"),
    ("tests/test_intent_docs_only_move_dry_run_evidence_plan.py", "Day139 path visibility tests"),
    ("tests/test_intent_folder_move_compatibility_gate.py", "Day140 compatibility gate tests"),
    ("docs/roadmap/day139_docs_only_move_dry_run_evidence_plan.md", "Prior-day roadmap references"),
    ("docs/ai-intent/day139_docs_only_move_dry_run_evidence_plan.md", "Prior-day AI-intent references"),
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day140_work": False,
            "agents_md_pre_read_result": "FAIL",
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day140_work": False,
            "agents_md_pre_read_result": "FAIL",
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_read_before_day140_work": markers_present,
        "agents_md_pre_read_result": "PASS" if markers_present else "FAIL",
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_folder_move_compatibility_gate_report(project_root: Path) -> Dict[str, Any]:
    docs_candidates = build_docs_only_candidate_inventory(project_root)
    import_sensitive_exclusions = build_import_sensitive_exclusions()
    reference_surfaces = build_reference_surface_audit(project_root)
    candidates_identifiable = bool(docs_candidates)
    candidates_isolated = all(item["docs_only"] and item["extension"] == ".md" for item in docs_candidates)
    import_sensitive_excluded = all(item["excluded_from_first_batch"] for item in import_sensitive_exclusions)
    references_identified = bool(reference_surfaces)

    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "source_scope": SOURCE_SCOPE,
        "status": "PENDING",
        "overall_status": "PENDING",
        "review_only": True,
        "report_only": True,
        "dry_run_only": True,
        "docs_only": True,
        "files_moved_count": 0,
        "folders_moved_count": 0,
        "imports_modified_count": 0,
        "docs_only_move_candidates_identifiable": candidates_identifiable,
        "candidate_docs_isolated_enough_for_review": candidates_isolated,
        "import_sensitive_files_excluded_from_first_batch": import_sensitive_excluded,
        "cli_task_test_report_index_references_identified": references_identified,
        "first_batch_docs_only_move_review_allowed": False,
        "final_recommendation": REVIEW_REQUIRED_RECOMMENDATION,
        "not_next_day_feature_statement": NOT_NEXT_DAY_FEATURE_STATEMENT,
        "no_move_statement": NO_MOVE_STATEMENT,
        "no_execution_provider_api_statement": NO_EXECUTION_PROVIDER_API_STATEMENT,
        "review_only_decision_statement": REVIEW_ONLY_DECISION_STATEMENT,
        "docs_only_move_candidates": docs_candidates,
        "import_sensitive_exclusions": import_sensitive_exclusions,
        "cli_task_test_report_index_reference_audit": reference_surfaces,
        "compatibility_decision_inputs": {
            "docs_only_candidates_identified": candidates_identifiable,
            "candidate_docs_isolated": candidates_isolated,
            "import_sensitive_files_excluded": import_sensitive_excluded,
            "reference_surfaces_identified": references_identified,
            "review_allowed_scope": "FUTURE_REVIEW_ONLY_NOT_MOVE",
        },
        "safety_invariants": build_safety_invariants(),
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
        **build_agents_md_evidence(project_root),
    }
    for field in SAFETY_FALSE_FIELDS:
        report[field] = False

    preliminary_errors = collect_validation_errors(report, check_decision_consistency=False)
    review_allowed = not preliminary_errors
    report["first_batch_docs_only_move_review_allowed"] = review_allowed
    report["final_recommendation"] = (
        READY_RECOMMENDATION if review_allowed else NOT_READY_RECOMMENDATION
    )
    report["validation_errors"] = collect_validation_errors(report, check_decision_consistency=True)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    return report


def build_docs_only_candidate_inventory(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    candidates: list[Dict[str, Any]] = []
    for index, (path, reason) in enumerate(DOCS_ONLY_CANDIDATE_PATHS, start=1):
        candidate_path = Path(path)
        candidates.append(
            {
                "candidate_id": f"DOCS_ONLY_REVIEW_CANDIDATE_{index:02d}",
                "current_path": path,
                "current_path_exists": (root / candidate_path).exists(),
                "docs_only": path.startswith("docs/"),
                "extension": candidate_path.suffix,
                "candidate_type": "documentation",
                "isolated_enough_for_future_review": path.startswith("docs/") and candidate_path.suffix == ".md",
                "move_allowed_now": False,
                "review_allowed_now": True,
                "reason": reason,
            }
        )
    return candidates


def build_import_sensitive_exclusions() -> list[Dict[str, Any]]:
    return [
        {
            "pattern": pattern,
            "excluded_from_first_batch": True,
            "import_sensitive": True,
            "reason": reason,
        }
        for pattern, reason in IMPORT_SENSITIVE_EXCLUSIONS
    ]


def build_reference_surface_audit(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    rows: list[Dict[str, Any]] = []
    for path, reason in REFERENCE_SURFACES:
        rows.append(
            {
                "path": path,
                "exists": (root / path).exists(),
                "reference_type": reason,
                "could_be_affected_by_future_docs_move": True,
                "modified_now": False,
                "execution_surface": False,
            }
        )
    return rows


def build_safety_invariants() -> Dict[str, Any]:
    invariants: Dict[str, Any] = {
        "review_only": True,
        "report_only": True,
        "dry_run_only": True,
        "docs_only": True,
    }
    for field in COUNT_ZERO_FIELDS:
        invariants[field] = 0
    for field in SAFETY_FALSE_FIELDS:
        invariants[field] = False
    return invariants


def collect_validation_errors(
    report: Mapping[str, Any],
    *,
    check_decision_consistency: bool = True,
) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    expected_values = {
        "day": DAY,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "source_scope": SOURCE_SCOPE,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_read_before_day140_work") is not True:
        errors.append("agents_md_read_before_day140_work must be true.")
    if report.get("agents_md_pre_read_result") != "PASS":
        errors.append("agents_md_pre_read_result must be PASS.")
    for field in ("review_only", "report_only", "dry_run_only", "docs_only"):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in COUNT_ZERO_FIELDS:
        if report.get(field) != 0:
            errors.append(f"{field} must be 0.")
    for field in SAFETY_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_docs_candidates(report.get("docs_only_move_candidates", []), errors)
    _validate_import_sensitive_exclusions(report.get("import_sensitive_exclusions", []), errors)
    _validate_reference_surface_audit(report.get("cli_task_test_report_index_reference_audit", []), errors)
    _validate_safety_invariants(report.get("safety_invariants", {}), errors)

    if report.get("docs_only_move_candidates_identifiable") is not True:
        errors.append("docs_only_move_candidates_identifiable must be true.")
    if report.get("candidate_docs_isolated_enough_for_review") is not True:
        errors.append("candidate_docs_isolated_enough_for_review must be true.")
    if report.get("import_sensitive_files_excluded_from_first_batch") is not True:
        errors.append("import_sensitive_files_excluded_from_first_batch must be true.")
    if report.get("cli_task_test_report_index_references_identified") is not True:
        errors.append("cli_task_test_report_index_references_identified must be true.")

    if check_decision_consistency:
        final_recommendation = report.get("final_recommendation")
        allowed = report.get("first_batch_docs_only_move_review_allowed")
        if allowed is True and final_recommendation != READY_RECOMMENDATION:
            errors.append("ready review decisions must use READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW.")
        if allowed is False and final_recommendation not in {
            NOT_READY_RECOMMENDATION,
            REVIEW_REQUIRED_RECOMMENDATION,
        }:
            errors.append("blocked review decisions must use a not-ready or review-required recommendation.")

    return errors


def _validate_docs_candidates(candidates: Any, errors: list[str]) -> None:
    if not isinstance(candidates, list) or not candidates:
        errors.append("docs_only_move_candidates must be a non-empty list.")
        return
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            errors.append("Each docs-only move candidate must be an object.")
            continue
        current_path = str(candidate.get("current_path", ""))
        if not current_path.startswith("docs/"):
            errors.append(f"current_path must stay docs-only: {current_path}")
        if candidate.get("extension") != ".md":
            errors.append(f"{current_path} must be a Markdown documentation file.")
        if candidate.get("move_allowed_now") is not False:
            errors.append(f"{current_path} move_allowed_now must be false.")
        if candidate.get("review_allowed_now") is not True:
            errors.append(f"{current_path} review_allowed_now must be true.")


def _validate_import_sensitive_exclusions(exclusions: Any, errors: list[str]) -> None:
    if not isinstance(exclusions, list) or not exclusions:
        errors.append("import_sensitive_exclusions must be a non-empty list.")
        return
    for item in exclusions:
        if not isinstance(item, Mapping):
            errors.append("Each import-sensitive exclusion must be an object.")
            continue
        if item.get("excluded_from_first_batch") is not True:
            errors.append(f"{item.get('pattern', '<unknown>')} must be excluded from first batch.")
        if item.get("import_sensitive") is not True:
            errors.append(f"{item.get('pattern', '<unknown>')} must be marked import-sensitive.")


def _validate_reference_surface_audit(reference_surfaces: Any, errors: list[str]) -> None:
    if not isinstance(reference_surfaces, list) or not reference_surfaces:
        errors.append("cli_task_test_report_index_reference_audit must be a non-empty list.")
        return
    for row in reference_surfaces:
        if not isinstance(row, Mapping):
            errors.append("Each reference surface row must be an object.")
            continue
        if row.get("modified_now") is not False:
            errors.append(f"{row.get('path', '<unknown>')} modified_now must be false.")
        if row.get("execution_surface") is not False:
            errors.append(f"{row.get('path', '<unknown>')} execution_surface must be false.")


def _validate_safety_invariants(safety_invariants: Any, errors: list[str]) -> None:
    if not isinstance(safety_invariants, Mapping):
        errors.append("safety_invariants must be an object.")
        return
    for field in ("review_only", "report_only", "dry_run_only", "docs_only"):
        if safety_invariants.get(field) is not True:
            errors.append(f"safety_invariants.{field} must be true.")
    for field in COUNT_ZERO_FIELDS:
        if safety_invariants.get(field) != 0:
            errors.append(f"safety_invariants.{field} must be 0.")
    for field in SAFETY_FALSE_FIELDS:
        if safety_invariants.get(field) is not False:
            errors.append(f"safety_invariants.{field} must be false.")


def write_folder_move_compatibility_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_folder_move_compatibility_gate_report(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_folder_move_compatibility_gate_html(safe_report, html_path)
    return json_path, html_path


def write_folder_move_compatibility_gate_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    candidate_rows = _table_rows(
        (
            item.get("candidate_id", ""),
            item.get("current_path", ""),
            item.get("current_path_exists", False),
            item.get("isolated_enough_for_future_review", False),
            item.get("move_allowed_now", False),
            item.get("reason", ""),
        )
        for item in report.get("docs_only_move_candidates", [])
    )
    exclusion_rows = _table_rows(
        (
            item.get("pattern", ""),
            item.get("excluded_from_first_batch", False),
            item.get("import_sensitive", False),
            item.get("reason", ""),
        )
        for item in report.get("import_sensitive_exclusions", [])
    )
    reference_rows = _table_rows(
        (
            item.get("path", ""),
            item.get("reference_type", ""),
            item.get("could_be_affected_by_future_docs_move", False),
            item.get("modified_now", False),
        )
        for item in report.get("cli_task_test_report_index_reference_audit", [])
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
  <p>{html.escape(str(report['not_next_day_feature_statement']))}</p>
  <p>{html.escape(str(report['no_move_statement']))}</p>
  <p>{html.escape(str(report['no_execution_provider_api_statement']))}</p>
  <p>{html.escape(str(report['review_only_decision_statement']))}</p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Docs-Only Review Candidates</h2>
  <table><thead><tr><th>Candidate</th><th>Current path</th><th>Exists</th><th>Isolated</th><th>Move allowed now</th><th>Reason</th></tr></thead><tbody>{candidate_rows}</tbody></table>
  <h2>Import-Sensitive Exclusions</h2>
  <table><thead><tr><th>Pattern</th><th>Excluded</th><th>Import-sensitive</th><th>Reason</th></tr></thead><tbody>{exclusion_rows}</tbody></table>
  <h2>CLI, Task, Test, Report-Index References</h2>
  <table><thead><tr><th>Path</th><th>Reference type</th><th>Could be affected later</th><th>Modified now</th></tr></thead><tbody>{reference_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_folder_move_compatibility_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_folder_move_compatibility_gate_report(project_root)
    json_path, html_path = write_folder_move_compatibility_gate_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(report["not_next_day_feature_statement"])
    print(report["no_move_statement"])
    print(report["no_execution_provider_api_statement"])
    print(report["review_only_decision_statement"])
    print(f"agents_md_read_before_day140_work: {json.dumps(report['agents_md_read_before_day140_work'])}")
    print(f"agents_md_pre_read_result: {json.dumps(report['agents_md_pre_read_result'])}")
    for field in COUNT_ZERO_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    for field in SAFETY_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(
        "docs_only_move_candidates_identifiable: "
        f"{json.dumps(report['docs_only_move_candidates_identifiable'])}"
    )
    print(
        "candidate_docs_isolated_enough_for_review: "
        f"{json.dumps(report['candidate_docs_isolated_enough_for_review'])}"
    )
    print(
        "import_sensitive_files_excluded_from_first_batch: "
        f"{json.dumps(report['import_sensitive_files_excluded_from_first_batch'])}"
    )
    print(
        "cli_task_test_report_index_references_identified: "
        f"{json.dumps(report['cli_task_test_report_index_references_identified'])}"
    )
    print(
        "first_batch_docs_only_move_review_allowed: "
        f"{json.dumps(report['first_batch_docs_only_move_review_allowed'])}"
    )
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    print(f"docs_only_candidate_count: {len(report['docs_only_move_candidates'])}")
    print(f"import_sensitive_exclusion_count: {len(report['import_sensitive_exclusions'])}")
    print(f"reference_surface_count: {len(report['cli_task_test_report_index_reference_audit'])}")
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
    report = build_folder_move_compatibility_gate_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
