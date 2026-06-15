"""Day143 dry-run draft safety diff viewer.

This module compares two existing dry-run draft display payload dictionaries.
It is review-only and display-only: it does not create AI summaries, rebuild
draft contracts, call providers or APIs, persist drafts, apply drafts, run
commands, use SSH, or touch live device paths.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 143
DAY_LABEL = "Day143"
TASK_NAME = "dry-run-draft-safety-diff-viewer"
TITLE = "Dry-run Draft Safety Diff Viewer"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_DISPLAY_ONLY"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "SAFETY_DIFF_VIEW_READY"
BLOCKED_STATUS = "SAFETY_DIFF_VIEW_BLOCKED"
FINAL_RECOMMENDATION = "DISPLAY_ONLY_SAFETY_DIFF_KEEP_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day143_dry_run_draft_safety_diff_viewer.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day143_dry_run_draft_safety_diff_viewer.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day143_dry_run_draft_safety_diff_viewer.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day143_dry_run_draft_safety_diff_viewer.md"
BASELINE_FIXTURE = Path("fixtures") / "day143_baseline_dry_run_draft_display_payload.example.json"
CANDIDATE_FIXTURE = Path("fixtures") / "day143_candidate_dry_run_draft_display_payload.example.json"

UNSAFE_WHEN_TRUE_FIELDS: Tuple[str, ...] = (
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "openai_api_called",
    "live_device_enabled",
    "ssh_enabled",
    "draft_applied",
    "draft_saved",
    "side_effect_allowed",
    "secrets_present",
    "next_phase_allowed",
)
SAFE_WHEN_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "display_only",
    "dry_run_only",
)
SAFETY_SENSITIVE_FIELDS: Tuple[str, ...] = UNSAFE_WHEN_TRUE_FIELDS + SAFE_WHEN_TRUE_FIELDS
REQUIRED_FALSE_FIELDS: Tuple[str, ...] = UNSAFE_WHEN_TRUE_FIELDS
REQUIRED_TRUE_FIELDS: Tuple[str, ...] = SAFE_WHEN_TRUE_FIELDS + (
    "not_next_day_feature",
    "not_day144",
    "not_day142_redo",
)

MISSING = "<MISSING>"


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day143_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day143_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def load_display_payload_fixture(project_root: Path, fixture_path: Path) -> Dict[str, Any]:
    full_path = Path(project_root) / fixture_path
    return json.loads(full_path.read_text(encoding="utf-8"))


def compare_dry_run_draft_display_payloads(
    baseline_payload: Mapping[str, Any],
    candidate_payload: Mapping[str, Any],
) -> Dict[str, Any]:
    """Return a deterministic reviewer-facing diff of two display payloads."""
    baseline_copy = deepcopy(dict(baseline_payload))
    candidate_copy = deepcopy(dict(candidate_payload))
    baseline_flat = _flatten_mapping(baseline_copy)
    candidate_flat = _flatten_mapping(candidate_copy)
    diff_rows = []

    for path in sorted(set(baseline_flat) | set(candidate_flat)):
        baseline_present = path in baseline_flat
        candidate_present = path in candidate_flat
        baseline_value = baseline_flat.get(path, MISSING)
        candidate_value = candidate_flat.get(path, MISSING)
        leaf_name = path.rsplit(".", 1)[-1]
        safety_sensitive = leaf_name in SAFETY_SENSITIVE_FIELDS

        if not baseline_present:
            change_type = "added"
        elif not candidate_present:
            change_type = "removed"
        elif baseline_value == candidate_value:
            change_type = "unchanged"
        else:
            change_type = "changed"

        classification, blocker, review_required, reason = _classify_diff_row(
            leaf_name=leaf_name,
            change_type=change_type,
            baseline_present=baseline_present,
            candidate_present=candidate_present,
            baseline_value=baseline_value,
            candidate_value=candidate_value,
            safety_sensitive=safety_sensitive,
        )
        diff_rows.append(
            {
                "path": path,
                "change_type": change_type,
                "baseline_value": baseline_value,
                "candidate_value": candidate_value,
                "safety_sensitive": safety_sensitive,
                "classification": classification,
                "blocker": blocker,
                "review_required": review_required,
                "reason": reason,
            }
        )

    added_fields = [row["path"] for row in diff_rows if row["change_type"] == "added"]
    removed_fields = [row["path"] for row in diff_rows if row["change_type"] == "removed"]
    changed_fields = [row["path"] for row in diff_rows if row["change_type"] == "changed"]
    unchanged_safety_flags = [
        row["path"]
        for row in diff_rows
        if row["safety_sensitive"] and row["change_type"] == "unchanged"
    ]
    safety_relevant_regressions = [
        row
        for row in diff_rows
        if row["safety_sensitive"]
        and row["classification"] in {"SAFETY_REGRESSION", "SAFETY_FIELD_MISSING"}
    ]
    blocked_unsafe_transitions = [
        row
        for row in diff_rows
        if row["classification"] == "UNSAFE_TRANSITION_BLOCKED"
    ]
    blockers = [row for row in diff_rows if row["blocker"]]
    final_verdict = "DISPLAY_ONLY_DIFF_BLOCKED" if blockers else "DISPLAY_ONLY_DIFF_ACCEPTED"

    return {
        "added_fields": added_fields,
        "removed_fields": removed_fields,
        "changed_fields": changed_fields,
        "unchanged_safety_flags": unchanged_safety_flags,
        "safety_relevant_regressions": safety_relevant_regressions,
        "blocked_unsafe_transitions": blocked_unsafe_transitions,
        "final_display_only_verdict": final_verdict,
        "diff_rows_total": len(diff_rows),
        "safety_regressions_detected": len(safety_relevant_regressions),
        "unsafe_transitions_blocked": len(blocked_unsafe_transitions),
        "diff_rows": diff_rows,
    }


def build_dry_run_draft_safety_diff_viewer_report(
    project_root: Path,
    baseline_payload: Optional[Mapping[str, Any]] = None,
    candidate_payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    baseline_loaded = baseline_payload is None
    candidate_loaded = candidate_payload is None
    baseline = (
        load_display_payload_fixture(project_root, BASELINE_FIXTURE)
        if baseline_payload is None
        else deepcopy(dict(baseline_payload))
    )
    candidate = (
        load_display_payload_fixture(project_root, CANDIDATE_FIXTURE)
        if candidate_payload is None
        else deepcopy(dict(candidate_payload))
    )
    diff_result = compare_dry_run_draft_display_payloads(baseline, candidate)
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
        "baseline_payload_loaded": baseline_loaded,
        "candidate_payload_loaded": candidate_loaded,
        "baseline_payload_fixture": BASELINE_FIXTURE.as_posix(),
        "candidate_payload_fixture": CANDIDATE_FIXTURE.as_posix(),
        "baseline_payload_id": baseline.get("payload_id", "unknown"),
        "candidate_payload_id": candidate.get("payload_id", "unknown"),
        "not_next_day_feature": True,
        "not_day144": True,
        "not_day142_redo": True,
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "openai_api_called": False,
        "live_device_enabled": False,
        "ssh_enabled": False,
        "draft_applied": False,
        "draft_saved": False,
        "side_effect_allowed": False,
        "secrets_present": False,
        "review_only": True,
        "display_only": True,
        "dry_run_only": True,
        "next_phase_allowed": False,
        "provider_runtime_invoked": False,
        "api_runtime_invoked": False,
        "day142_summary_to_draft_builder_called": False,
        "day142_contract_semantics_changed": False,
        "draft_persisted": False,
        "next_phase_allowed_by_diff": False,
        "diff_result": diff_result,
        "diff_rows_total": diff_result["diff_rows_total"],
        "safety_regressions_detected": diff_result["safety_regressions_detected"],
        "unsafe_transitions_blocked": diff_result["unsafe_transitions_blocked"],
        "final_display_only_verdict": diff_result["final_display_only_verdict"],
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
    expected_values = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day143_work") is not True:
        errors.append("agents_md_read_before_day143_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    false_runtime_fields = (
        "provider_runtime_invoked",
        "api_runtime_invoked",
        "day142_summary_to_draft_builder_called",
        "day142_contract_semantics_changed",
        "draft_persisted",
        "next_phase_allowed_by_diff",
    )
    for field in false_runtime_fields:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    diff_result = report.get("diff_result")
    if not isinstance(diff_result, Mapping):
        errors.append("diff_result must be an object.")
    else:
        for field in (
            "added_fields",
            "removed_fields",
            "changed_fields",
            "unchanged_safety_flags",
            "safety_relevant_regressions",
            "blocked_unsafe_transitions",
            "final_display_only_verdict",
            "diff_rows",
        ):
            if field not in diff_result:
                errors.append(f"diff_result.{field} is missing.")
    return errors


def write_dry_run_draft_safety_diff_viewer_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_dry_run_draft_safety_diff_viewer_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_dry_run_draft_safety_diff_viewer_html(safe_report, html_path)
    return json_path, html_path


def write_dry_run_draft_safety_diff_viewer_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_fields = (
        "day_label",
        "task",
        "mode",
        "overall_status",
        "status",
        "baseline_payload_loaded",
        "candidate_payload_loaded",
        "diff_rows_total",
        "safety_regressions_detected",
        "unsafe_transitions_blocked",
        "final_display_only_verdict",
        "not_day142_redo",
        "not_next_day_feature",
        "not_day144",
    )
    safety_fields = REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS
    diff_rows = report.get("diff_result", {}).get("diff_rows", [])
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
  <p><strong>Review-only/display-only:</strong> Day143 compares two existing dry-run draft display payloads. It does not rebuild Day142, call providers/APIs, execute commands, use SSH, save/apply drafts, or unlock any next phase.</p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{_table_rows((field, report.get(field, "")) for field in summary_fields)}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{_table_rows((field, report.get(field, "")) for field in safety_fields)}</tbody></table>
  <h2>Diff Rows</h2>
  <table><thead><tr><th>Path</th><th>Change</th><th>Baseline</th><th>Candidate</th><th>Classification</th><th>Blocker</th></tr></thead><tbody>{_diff_table_rows(diff_rows)}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_dry_run_draft_safety_diff_viewer(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_dry_run_draft_safety_diff_viewer_report(project_root)
    json_path, html_path = write_dry_run_draft_safety_diff_viewer_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md read before Day143 work: {json.dumps(report['agents_md_read_before_day143_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day143 task: {TASK_NAME}")
    print(f"status: {report['overall_status']}")
    print(f"result: {report['status']}")
    print(f"mode: {report['mode']}")
    print(f"baseline_payload_loaded: {json.dumps(report['baseline_payload_loaded'])}")
    print(f"candidate_payload_loaded: {json.dumps(report['candidate_payload_loaded'])}")
    print(f"diff_rows_total: {report['diff_rows_total']}")
    print(f"safety_regressions_detected: {report['safety_regressions_detected']}")
    print(f"unsafe_transitions_blocked: {report['unsafe_transitions_blocked']}")
    for field in ("not_day142_redo", "not_next_day_feature", "not_day144"):
        print(f"{field}: {json.dumps(report[field])}")
        print(f"{field}={json.dumps(report[field])}")
    for field in REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"final_display_only_verdict: {json.dumps(report['final_display_only_verdict'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {READY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_STATUS}")
    return 1


def _flatten_mapping(value: Any, prefix: str = "") -> Dict[str, Any]:
    if isinstance(value, Mapping):
        flattened: Dict[str, Any] = {}
        for key, nested in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten_mapping(nested, child_path))
        return flattened
    return {prefix: deepcopy(value)}


def _classify_diff_row(
    leaf_name: str,
    change_type: str,
    baseline_present: bool,
    candidate_present: bool,
    baseline_value: Any,
    candidate_value: Any,
    safety_sensitive: bool,
) -> Tuple[str, bool, bool, str]:
    if not safety_sensitive:
        if change_type == "unchanged":
            return "UNCHANGED_INFORMATIONAL", False, False, "Non-safety field unchanged."
        return "INFORMATIONAL_DISPLAY_DIFF", False, False, "Display-only metadata/content diff."

    if not baseline_present or not candidate_present:
        return (
            "SAFETY_FIELD_MISSING",
            True,
            True,
            "Safety-sensitive field is missing on one side; missing values are not inferred safe.",
        )

    if leaf_name in UNSAFE_WHEN_TRUE_FIELDS:
        if baseline_value is False and candidate_value is True:
            return (
                "UNSAFE_TRANSITION_BLOCKED",
                True,
                True,
                "Unsafe false-to-true transition is blocked.",
            )
        if candidate_value is not False:
            return (
                "SAFETY_REGRESSION",
                True,
                True,
                "Unsafe safety field must remain false in the candidate payload.",
            )
        return "UNCHANGED_SAFE_FLAG", False, False, "Unsafe capability remains false."

    if leaf_name in SAFE_WHEN_TRUE_FIELDS:
        if baseline_value is True and candidate_value is False:
            return (
                "SAFETY_REGRESSION",
                True,
                True,
                "Review/display/dry-run safety assertion regressed from true to false.",
            )
        if candidate_value is not True:
            return (
                "SAFETY_REGRESSION",
                True,
                True,
                "Safety assertion must remain true in the candidate payload.",
            )
        return "UNCHANGED_SAFE_FLAG", False, False, "Required safety assertion remains true."

    return "UNCHANGED_INFORMATIONAL", False, False, "No safety classification required."


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


def _diff_table_rows(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('path', '')))}</td>"
        f"<td>{html.escape(str(row.get('change_type', '')))}</td>"
        f"<td>{html.escape(_cell_text(row.get('baseline_value', '')))}</td>"
        f"<td>{html.escape(_cell_text(row.get('candidate_value', '')))}</td>"
        f"<td>{html.escape(str(row.get('classification', '')))}</td>"
        f"<td>{html.escape(_cell_text(row.get('blocker', '')))}</td>"
        "</tr>"
        for row in rows
    )
