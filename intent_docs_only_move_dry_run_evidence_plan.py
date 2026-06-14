"""Day139 docs-only move dry-run evidence plan.

This module produces reviewer-visible docs-only dry-run evidence. It does not
move, rename, delete, edit imports, enable execution/provider/API behavior,
call SSH, or invoke adapters, brokers, runners, mapped execution, or live
commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple


DAY = "Day139"
TASK_NAME = "docs-only-move-dry-run-evidence-plan"
TITLE = "Docs-Only Move Dry-Run Evidence Plan"
FULL_TITLE = f"{DAY} {TITLE}"
MODE = "REVIEW_ONLY"
BASED_ON_DAY = "Day138"
SOURCE_SCOPE = "docs-only"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_RECORDED"
BLOCKED_STATUS = "DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET"
REPORT_JSON = Path("reports") / "lab-summary" / "day139_docs_only_move_dry_run_evidence_plan.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day139_docs_only_move_dry_run_evidence_plan.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day139_docs_only_move_dry_run_evidence_plan.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day139_docs_only_move_dry_run_evidence_plan.md"

NOT_NEXT_DAY_FEATURE_STATEMENT = "This is not the next-day feature implementation."
NOT_DAY140_STATEMENT = "This is not Day140."
NO_EXECUTION_PROVIDER_API_STATEMENT = "No execution, provider, or API is enabled."

SAFETY_FALSE_FIELDS: Tuple[str, ...] = (
    "files_moved",
    "files_renamed",
    "imports_modified",
    "source_import_paths_modified",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "adapter_enabled",
    "ssh_enabled",
    "live_command_enabled",
    "next_phase_allowed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "title",
    "mode",
    "based_on_day",
    "source_scope",
    "agents_md_read_before_day139_work",
    "dry_run_only",
    "files_moved",
    "files_renamed",
    "imports_modified",
    "source_import_paths_modified",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "adapter_enabled",
    "ssh_enabled",
    "live_command_enabled",
    "next_phase_allowed",
    "hypothetical_docs_target_folders",
    "docs_only_dry_run_move_pairs",
    "proposal_diff_preview",
    "affected_doc_paths",
    "affected_doc_links",
    "affected_report_index_paths",
    "migration_risk_matrix",
    "safety_invariants",
    "final_recommendation",
)

DAY138_DOCS_BASELINE_GROUPS: Tuple[Dict[str, Any], ...] = (
    {
        "day138_group_name": "docs / roadmap",
        "current_location": "docs/roadmap/",
        "future_organization_candidate": True,
        "day138_risk_level": "LOW",
    },
    {
        "day138_group_name": "docs / ai-intent",
        "current_location": "docs/ai-intent/",
        "future_organization_candidate": True,
        "day138_risk_level": "LOW",
    },
)

DOCS_MOVE_CANDIDATES: Tuple[Tuple[str, str, str], ...] = (
    (
        "docs/roadmap/pre_day137_project_folder_safety_inventory_no_move_plan.md",
        "docs/roadmap/project-organization/pre_day137_project_folder_safety_inventory_no_move_plan.md",
        "Pre-Day137 no-move inventory belongs with project organization planning evidence.",
    ),
    (
        "docs/roadmap/pre_day137_2_project_folder_organization_policy_move_risk_matrix.md",
        "docs/roadmap/project-organization/pre_day137_2_project_folder_organization_policy_move_risk_matrix.md",
        "Pre-Day137-2 move-risk matrix belongs with project organization planning evidence.",
    ),
    (
        "docs/roadmap/day137_project_folder_organization_decision_gate.md",
        "docs/roadmap/project-organization/day137_project_folder_organization_decision_gate.md",
        "Day137 decision gate is part of the folder organization evidence line.",
    ),
    (
        "docs/roadmap/day138_project_folder_organization_dry_run_inventory_gate.md",
        "docs/roadmap/project-organization/day138_project_folder_organization_dry_run_inventory_gate.md",
        "Day138 docs organization candidates are the baseline for Day139 dry-run evidence.",
    ),
    (
        ROADMAP_DOC.as_posix(),
        "docs/roadmap/project-organization/day139_docs_only_move_dry_run_evidence_plan.md",
        "Day139 would remain grouped with project organization dry-run planning evidence.",
    ),
    (
        "docs/ai-intent/day138_project_folder_organization_dry_run_inventory_gate.md",
        "docs/ai-intent/project-organization/day138_project_folder_organization_dry_run_inventory_gate.md",
        "Day138 AI intent docs are docs-only evidence and remain dry-run candidates only.",
    ),
    (
        AI_INTENT_DOC.as_posix(),
        "docs/ai-intent/project-organization/day139_docs_only_move_dry_run_evidence_plan.md",
        "Day139 AI intent docs would remain grouped with docs-only move planning evidence.",
    ),
)

HYPOTHETICAL_TARGET_FOLDERS: Tuple[Dict[str, Any], ...] = (
    {
        "target_folder": "docs/roadmap/project-organization/",
        "source_day138_group": "docs / roadmap",
        "purpose": "Group folder organization roadmap and no-move planning docs.",
        "created_now": False,
    },
    {
        "target_folder": "docs/ai-intent/project-organization/",
        "source_day138_group": "docs / ai-intent",
        "purpose": "Group AI-intent notes for folder organization planning docs.",
        "created_now": False,
    },
)

RISK_CATEGORIES: Tuple[Tuple[str, str, str, str, str], ...] = (
    (
        "documentation_link_breakage",
        "Documentation links",
        "docs/**/*.md",
        "MEDIUM",
        "Generate a link-reference inventory and update links in a separate approved docs-only migration.",
    ),
    (
        "roadmap_link_breakage",
        "Roadmap links",
        "docs/roadmap/*.md",
        "MEDIUM",
        "Keep compatibility references or redirect notes until reviewers accept the new roadmap layout.",
    ),
    (
        "report_index_path_breakage",
        "Report-index paths",
        "network_lab.py report visibility metadata",
        "HIGH",
        "Update report-index metadata only in a future compatibility gate after dry-run approval.",
    ),
    (
        "readme_reference_breakage",
        "README references",
        "README.md and docs/README-style files",
        "MEDIUM",
        "Scan README references and include exact replacements before any docs move.",
    ),
    (
        "test_documentation_reference_breakage",
        "Test documentation references",
        "tests/test_*.py",
        "HIGH",
        "Update tests only in a future approved compatibility gate; do not modify imports in Day139.",
    ),
    (
        "fixture_documentation_reference_breakage",
        "Fixture documentation references",
        "fixtures/** and topology_profiles/** documentation references",
        "LOW",
        "Verify sample and fixture references before any docs move.",
    ),
    (
        "backward_compatibility_breakage",
        "Backward compatibility",
        "Existing reviewer links and historical evidence paths",
        "HIGH",
        "Keep old paths stable until a future compatibility and redirect plan is approved.",
    ),
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day139_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": "NOT_FOUND",
        }
    except OSError as exc:
        return {
            "agents_md_found": False,
            "agents_md_read_before_day139_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_found": True,
        "agents_md_read_before_day139_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_docs_only_move_dry_run_evidence_plan_report(project_root: Path) -> Dict[str, Any]:
    move_pairs = build_docs_only_dry_run_move_pairs(project_root)
    affected_paths = build_affected_doc_paths(move_pairs)
    affected_links = build_affected_doc_links(project_root, move_pairs)
    report: Dict[str, Any] = {
        "day": DAY,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "based_on_day": BASED_ON_DAY,
        "source_scope": SOURCE_SCOPE,
        "status": "PENDING",
        "overall_status": "PENDING",
        "review_only": True,
        "dry_run_only": True,
        "docs_only": True,
        "not_next_day_feature": True,
        "not_day140": True,
        "not_folder_move_compatibility_gate": True,
        "files_moved": False,
        "files_renamed": False,
        "imports_modified": False,
        "source_import_paths_modified": False,
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "adapter_enabled": False,
        "ssh_enabled": False,
        "live_command_enabled": False,
        "next_phase_allowed": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "not_next_day_feature_statement": NOT_NEXT_DAY_FEATURE_STATEMENT,
        "not_day140_statement": NOT_DAY140_STATEMENT,
        "no_execution_provider_api_statement": NO_EXECUTION_PROVIDER_API_STATEMENT,
        **build_agents_md_evidence(project_root),
        "day138_docs_organization_candidate_baseline": [dict(item) for item in DAY138_DOCS_BASELINE_GROUPS],
        "hypothetical_docs_target_folders": [dict(item) for item in HYPOTHETICAL_TARGET_FOLDERS],
        "docs_only_dry_run_move_pairs": move_pairs,
        "proposal_diff_preview": build_proposal_diff_preview(move_pairs),
        "affected_doc_paths": affected_paths,
        "affected_doc_links": affected_links,
        "affected_report_index_paths": build_affected_report_index_paths(),
        "migration_risk_matrix": build_migration_risk_matrix(move_pairs, affected_links),
        "safety_invariants": build_safety_invariants(),
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    return report


def build_docs_only_dry_run_move_pairs(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    pairs: list[Dict[str, Any]] = []
    for index, (current_path, target_path, reason) in enumerate(DOCS_MOVE_CANDIDATES, start=1):
        pairs.append(
            {
                "pair_id": f"DOCS_DRY_RUN_MOVE_{index:02d}",
                "current_path": current_path,
                "hypothetical_target_path": target_path,
                "source_scope": SOURCE_SCOPE,
                "current_path_exists": (root / current_path).exists(),
                "target_folder": str(Path(target_path).parent).replace("\\", "/") + "/",
                "reason": reason,
                "move_allowed_now": False,
                "dry_run_only": True,
            }
        )
    return pairs


def build_affected_doc_paths(move_pairs: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    affected: list[Dict[str, Any]] = []
    for pair in move_pairs:
        affected.append(
            {
                "current_path": pair["current_path"],
                "hypothetical_target_path": pair["hypothetical_target_path"],
                "path_type": "documentation",
                "action": "DRY_RUN_PREVIEW_ONLY",
                "move_allowed_now": False,
            }
        )
    return affected


def build_affected_doc_links(project_root: Path, move_pairs: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    doc_texts = _read_docs_text(project_root)
    affected: list[Dict[str, Any]] = []
    for pair in move_pairs:
        current_path = str(pair["current_path"])
        file_name = Path(current_path).name
        references = []
        for doc_path, text in doc_texts.items():
            if doc_path == current_path:
                continue
            if current_path in text or file_name in text:
                references.append(doc_path)
        affected.append(
            {
                "current_path": current_path,
                "hypothetical_target_path": pair["hypothetical_target_path"],
                "reference_count": len(references),
                "referencing_docs": references[:12],
                "links_modified_now": False,
            }
        )
    return affected


def build_affected_report_index_paths() -> list[Dict[str, Any]]:
    return [
        {
            "path": "network_lab.py",
            "reference_type": "report visibility metadata",
            "affected_by_docs_move": True,
            "modified_now": False,
            "reason": "Report-index metadata lists roadmap and AI-intent docs for Day137-Day139 evidence.",
        },
        {
            "path": REPORT_JSON.as_posix(),
            "reference_type": "Day139 generated JSON evidence",
            "affected_by_docs_move": False,
            "modified_now": False,
            "reason": "Report output path remains stable and is not part of docs-only move candidates.",
        },
        {
            "path": REPORT_HTML.as_posix(),
            "reference_type": "Day139 generated HTML evidence",
            "affected_by_docs_move": False,
            "modified_now": False,
            "reason": "Report output path remains stable and is not part of docs-only move candidates.",
        },
        {
            "path": ROADMAP_DOC.as_posix(),
            "reference_type": "Day139 roadmap evidence",
            "affected_by_docs_move": True,
            "modified_now": False,
            "reason": "Roadmap doc is included only as a hypothetical docs-only move pair.",
        },
        {
            "path": AI_INTENT_DOC.as_posix(),
            "reference_type": "Day139 AI-intent evidence",
            "affected_by_docs_move": True,
            "modified_now": False,
            "reason": "AI-intent doc is included only as a hypothetical docs-only move pair.",
        },
    ]


def build_migration_risk_matrix(
    move_pairs: Sequence[Mapping[str, Any]],
    affected_links: Sequence[Mapping[str, Any]],
) -> list[Dict[str, Any]]:
    link_counts = {item["current_path"]: item.get("reference_count", 0) for item in affected_links}
    primary_pair = move_pairs[0] if move_pairs else {"current_path": "docs/**/*.md", "target_folder": "docs/"}
    rows: list[Dict[str, Any]] = []
    for index, (risk_id, area, current_pattern, risk_level, mitigation) in enumerate(RISK_CATEGORIES, start=1):
        target_folder = primary_pair.get("target_folder", "docs/")
        affected_references = sum(link_counts.values()) if "link" in risk_id or "reference" in risk_id else 0
        rows.append(
            {
                "risk_id": risk_id,
                "area": area,
                "current_doc_path_or_pattern": current_pattern,
                "hypothetical_target_folder": target_folder,
                "affected_links_or_references": affected_references,
                "risk_level": risk_level,
                "mitigation": mitigation,
                "migration_allowed_now": False,
            }
        )
    return rows


def build_proposal_diff_preview(move_pairs: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    return [
        {
            "diff_id": f"DRY_RUN_DIFF_{index:02d}",
            "from": pair["current_path"],
            "to": pair["hypothetical_target_path"],
            "preview": f"DRY-RUN ONLY: would plan docs path {pair['current_path']} -> {pair['hypothetical_target_path']}",
            "applied": False,
        }
        for index, pair in enumerate(move_pairs, start=1)
    ]


def build_safety_invariants() -> Dict[str, Any]:
    invariants: Dict[str, Any] = {
        "dry_run_only": True,
        "review_only": True,
        "docs_only": True,
        "not_next_day_feature": True,
        "not_day140": True,
    }
    for field in SAFETY_FALSE_FIELDS:
        invariants[field] = False
    return invariants


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    expected_values = {
        "day": DAY,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "based_on_day": BASED_ON_DAY,
        "source_scope": SOURCE_SCOPE,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_read_before_day139_work") is not True:
        errors.append("agents_md_read_before_day139_work must be true.")
    if report.get("dry_run_only") is not True:
        errors.append("dry_run_only must be true.")
    if report.get("review_only") is not True:
        errors.append("review_only must be true.")
    if report.get("docs_only") is not True:
        errors.append("docs_only must be true.")
    if report.get("not_next_day_feature") is not True:
        errors.append("not_next_day_feature must be true.")
    if report.get("not_day140") is not True:
        errors.append("not_day140 must be true.")

    for field in SAFETY_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_move_pairs(report.get("docs_only_dry_run_move_pairs", []), errors)
    _validate_risk_matrix(report.get("migration_risk_matrix", []), errors)
    _validate_safety_invariants(report.get("safety_invariants", {}), errors)
    return errors


def _validate_move_pairs(move_pairs: Any, errors: list[str]) -> None:
    if not isinstance(move_pairs, list) or not move_pairs:
        errors.append("docs_only_dry_run_move_pairs must be a non-empty list.")
        return
    for pair in move_pairs:
        if not isinstance(pair, Mapping):
            errors.append("Each docs-only move pair must be an object.")
            continue
        current_path = str(pair.get("current_path", ""))
        target_path = str(pair.get("hypothetical_target_path", ""))
        if not current_path.startswith("docs/"):
            errors.append(f"current_path must stay docs-only: {current_path}")
        if not target_path.startswith("docs/"):
            errors.append(f"hypothetical_target_path must stay docs-only: {target_path}")
        if pair.get("move_allowed_now") is not False:
            errors.append(f"{current_path} move_allowed_now must be false.")
        if pair.get("dry_run_only") is not True:
            errors.append(f"{current_path} dry_run_only must be true.")


def _validate_risk_matrix(risk_matrix: Any, errors: list[str]) -> None:
    if not isinstance(risk_matrix, list) or not risk_matrix:
        errors.append("migration_risk_matrix must be a non-empty list.")
        return
    risk_ids = {row.get("risk_id") for row in risk_matrix if isinstance(row, Mapping)}
    for risk_id, *_rest in RISK_CATEGORIES:
        if risk_id not in risk_ids:
            errors.append(f"Missing migration risk: {risk_id}")
    for row in risk_matrix:
        if not isinstance(row, Mapping):
            errors.append("Each migration risk row must be an object.")
            continue
        for field in (
            "risk_id",
            "area",
            "current_doc_path_or_pattern",
            "hypothetical_target_folder",
            "affected_links_or_references",
            "risk_level",
            "mitigation",
            "migration_allowed_now",
        ):
            if field not in row:
                errors.append(f"Migration risk row is missing {field}.")
        if row.get("migration_allowed_now") is not False:
            errors.append(f"{row.get('risk_id', '<unknown>')} migration_allowed_now must be false.")


def _validate_safety_invariants(safety_invariants: Any, errors: list[str]) -> None:
    if not isinstance(safety_invariants, Mapping):
        errors.append("safety_invariants must be an object.")
        return
    for field in SAFETY_FALSE_FIELDS:
        if safety_invariants.get(field) is not False:
            errors.append(f"safety_invariants.{field} must be false.")
    for field in ("dry_run_only", "review_only", "docs_only", "not_next_day_feature", "not_day140"):
        if safety_invariants.get(field) is not True:
            errors.append(f"safety_invariants.{field} must be true.")


def write_docs_only_move_dry_run_evidence_plan_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_docs_only_move_dry_run_evidence_plan_report(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_docs_only_move_dry_run_evidence_plan_html(safe_report, html_path)
    return json_path, html_path


def write_docs_only_move_dry_run_evidence_plan_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    move_rows = _table_rows(
        (
            item.get("pair_id", ""),
            item.get("current_path", ""),
            item.get("hypothetical_target_path", ""),
            item.get("move_allowed_now", False),
            item.get("reason", ""),
        )
        for item in report.get("docs_only_dry_run_move_pairs", [])
    )
    risk_rows = _table_rows(
        (
            item.get("risk_id", ""),
            item.get("area", ""),
            item.get("risk_level", ""),
            item.get("migration_allowed_now", False),
            item.get("mitigation", ""),
        )
        for item in report.get("migration_risk_matrix", [])
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
  <p>{html.escape(str(report['not_day140_statement']))}</p>
  <p>{html.escape(str(report['no_execution_provider_api_statement']))}</p>
  <p>next_phase_allowed: <code>{html.escape(json.dumps(report['next_phase_allowed']))}</code></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Docs-Only Dry-Run Move Pairs</h2>
  <table><thead><tr><th>Pair</th><th>Current path</th><th>Hypothetical target path</th><th>Move allowed now</th><th>Reason</th></tr></thead><tbody>{move_rows}</tbody></table>
  <h2>Migration Risk Matrix</h2>
  <table><thead><tr><th>Risk</th><th>Area</th><th>Level</th><th>Migration allowed now</th><th>Mitigation</th></tr></thead><tbody>{risk_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_docs_only_move_dry_run_evidence_plan(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_docs_only_move_dry_run_evidence_plan_report(project_root)
    json_path, html_path = write_docs_only_move_dry_run_evidence_plan_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(report["not_next_day_feature_statement"])
    print(report["not_day140_statement"])
    print(report["no_execution_provider_api_statement"])
    print(f"based_on_day: {json.dumps(report['based_on_day'])}")
    print(f"source_scope: {json.dumps(report['source_scope'])}")
    print(f"agents_md_read_before_day139_work: {json.dumps(report['agents_md_read_before_day139_work'])}")
    print(f"final_recommendation: {json.dumps(report['final_recommendation'])}")
    for field in SAFETY_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"docs_only_dry_run_move_pair_count: {len(report['docs_only_dry_run_move_pairs'])}")
    print(f"migration_risk_count: {len(report['migration_risk_matrix'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _read_docs_text(project_root: Path) -> Dict[str, str]:
    docs_root = Path(project_root) / "docs"
    texts: Dict[str, str] = {}
    if not docs_root.exists():
        return texts
    for path in sorted(docs_root.rglob("*.md")):
        try:
            relative = path.relative_to(project_root).as_posix()
        except ValueError:
            continue
        try:
            texts[relative] = path.read_text(encoding="utf-8")
        except OSError:
            continue
    return texts


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
    report = build_docs_only_move_dry_run_evidence_plan_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
