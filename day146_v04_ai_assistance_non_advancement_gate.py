"""Day146 v0.4 AI assistance non-advancement gate.

This module verifies that the Day127-Day145 v0.4 AI assistance evidence chain
remains frozen and does not advance into provider, API, model, execution,
runner, broker, adapter, SSH, live-device, folder-move, cleanup, or next-phase
behavior. It is local-only deterministic reviewer evidence.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple

import day145_v04_ai_assistance_evidence_freeze_package as day145_freeze


DAY = 146
DAY_LABEL = "Day146"
TASK_NAME = "v0.4-ai-assistance-non-advancement-gate"
TITLE = "v0.4 AI Assistance Non-Advancement Gate"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_NON_ADVANCEMENT_GATE"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY"
BLOCKED_STATUS = "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_DAY127_DAY145_V0_4_AI_ASSISTANCE_FROZEN_AND_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day146_v04_ai_assistance_non_advancement_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day146_v04_ai_assistance_non_advancement_gate.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day146_v04_ai_assistance_non_advancement_gate.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day146_v04_ai_assistance_non_advancement_gate.md"

FROZEN_REFERENCE_COMMIT_HASH = day145_freeze.FREEZE_COMMIT_HASH
DAY145_FROZEN_STATEMENT = "Day145 is frozen input only and was not rerun, rewritten, repaired, or modified."
NON_ADVANCEMENT_STATEMENT = "Day146 is a non-advancement gate and does not implement Day147 or any next phase."
NO_PROVIDER_API_MODEL_STATEMENT = "Day146 does not call providers, APIs, OpenAI API, or models."
NO_EXECUTION_PATH_STATEMENT = "Day146 does not invoke runners, brokers, adapters, execution paths, or mapped tasks."
NO_SSH_REAL_DEVICE_STATEMENT = "Day146 does not use SSH, NETCONF, RESTCONF, RouterOS, live devices, or real network access."
NO_FOLDER_MOVE_CLEANUP_STATEMENT = "Day146 performs no folder move, rename, relocation, cleanup, or git clean."
NEXT_PHASE_LOCK_STATEMENT = "Day146 keeps next_phase_allowed=false and execution_provider_api_phase_advanced=false."

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "gate_only",
    "local_only",
    "deterministic_static_data_only",
    "day127_day145_frozen_scope_verified",
    "day145_frozen_input_only",
    "day145_untouched",
    "ai_assistance_non_advancement_gate",
    "phase_lock_reviewed",
    "no_new_runtime_surface",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "execution_allowed",
    "provider_allowed",
    "api_allowed",
    "openai_api_called",
    "ai_provider_called",
    "model_invocation_allowed",
    "external_ai_runtime_allowed",
    "execution_runner_behavior_added",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "mapped_task_execution_allowed",
    "live_device_access_allowed",
    "real_device_access_allowed",
    "live_network_access_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "routeros_allowed",
    "configuration_change_allowed",
    "configuration_changing_commands_allowed",
    "config_write_apply_allowed",
    "reset_reboot_remove_disable_enable_allowed",
    "secrets_allowed",
    "credentials_allowed",
    "environment_provider_activation_allowed",
    "folder_move_performed",
    "folders_moved",
    "folder_reorganization_performed",
    "cleanup_performed",
    "broad_cleanup_command_run",
    "git_clean_run",
    "day145_modified",
    "day145_reports_modified",
    "day145_docs_modified",
    "day145_roadmap_modified",
    "day145_evidence_modified",
    "day145_rerun",
    "day145_rewritten",
    "day145_repaired",
    "freeze_scope_expanded",
    "execution_provider_api_phase_advanced",
    "next_phase_allowed",
    "day147_implemented",
    "ai_assistance_advanced_beyond_v04",
    "provider_runtime_unlocked",
    "reviewer_approval_inferred",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "overall_status",
    "agents_md_pre_read_result",
    "agents_md_read_before_day146_work",
    "non_advancement_scope",
    "frozen_reference_commit_hash",
    "source_artifact_count",
    "day145_frozen_artifacts",
    "non_advancement_checks",
    "final_recommendation",
)

DAY145_ARTIFACT: Dict[str, Any] = {
    "day": "Day145",
    "name": "v0.4 AI Assistance Evidence Freeze Package",
    "paths": (
        "day145_v04_ai_assistance_evidence_freeze_package.py",
        "docs/ai-intent/day145_v04_ai_assistance_evidence_freeze_package.md",
        "docs/roadmap/day145_v04_ai_assistance_evidence_freeze_package.md",
        "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.json",
        "reports/lab-summary/day145_v04_ai_assistance_evidence_freeze_package.html",
    ),
    "frozen_input_only": True,
}

SOURCE_ARTIFACTS: Tuple[Dict[str, Any], ...] = tuple(
    {
        "day": artifact["day"],
        "name": artifact["name"],
        "paths": tuple(artifact["paths"]),
        "frozen_input_only": bool(artifact.get("frozen_input_only", False)),
    }
    for artifact in day145_freeze.SOURCE_ARTIFACTS
) + (DAY145_ARTIFACT,)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day146_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day146_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_source_artifact_records(project_root: Path) -> list[Dict[str, Any]]:
    root = Path(project_root)
    records: list[Dict[str, Any]] = []
    for index, artifact in enumerate(SOURCE_ARTIFACTS, start=1):
        path_records = [_build_path_record(root, path) for path in artifact["paths"]]
        records.append(
            {
                "artifact_id": f"DAY146_NON_ADVANCEMENT_SOURCE_{index:02d}",
                "source_day": artifact["day"],
                "name": artifact["name"],
                "paths": path_records,
                "all_paths_exist": all(item["path_exists"] is True for item in path_records),
                "frozen_input_only": bool(artifact.get("frozen_input_only", False)),
                "review_mode": "static_reference_only",
                "gate_status": "LOCKED",
                "write_target": False,
                "rerun_allowed": False,
                "rewrite_allowed": False,
                "repair_allowed": False,
                "execution_allowed": False,
                "provider_allowed": False,
                "api_allowed": False,
                "next_phase_allowed": False,
            }
        )
    return records


def _build_path_record(project_root: Path, relative_path: str) -> Dict[str, Any]:
    path = project_root / relative_path
    exists = path.exists()
    return {
        "path": relative_path,
        "path_exists": exists,
        "sha256": _sha256_file(path) if exists and path.is_file() else None,
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_non_advancement_checks(source_artifacts: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    artifacts = list(source_artifacts)
    day145_artifacts = [item for item in artifacts if item.get("source_day") == "Day145"]
    return [
        {
            "check_id": "DAY146-NON-ADVANCE-001",
            "name": "Day127-Day145 frozen scope remains present",
            "status": "PASS" if [item.get("source_day") for item in artifacts] == [f"Day{day}" for day in range(127, 146)] else "FAIL",
            "non_advancement_scope": "Day127-Day145",
            "freeze_scope_expanded": False,
            "next_phase_allowed": False,
        },
        {
            "check_id": "DAY146-NON-ADVANCE-002",
            "name": "Day145 frozen evidence remains untouched",
            "status": "PASS" if day145_artifacts and day145_artifacts[0].get("frozen_input_only") is True else "FAIL",
            "day145_modified": False,
            "day145_reports_modified": False,
            "day145_docs_modified": False,
            "day145_roadmap_modified": False,
            "day145_evidence_modified": False,
            "day145_rerun": False,
            "day145_rewritten": False,
            "day145_repaired": False,
        },
        {
            "check_id": "DAY146-NON-ADVANCE-003",
            "name": "Provider API model runtime remains locked",
            "status": "PASS",
            "provider_allowed": False,
            "api_allowed": False,
            "openai_api_called": False,
            "ai_provider_called": False,
            "model_invocation_allowed": False,
            "external_ai_runtime_allowed": False,
            "provider_runtime_unlocked": False,
        },
        {
            "check_id": "DAY146-NON-ADVANCE-004",
            "name": "Execution live device and command paths remain closed",
            "status": "PASS",
            "execution_allowed": False,
            "adapter_execution_allowed": False,
            "broker_execution_allowed": False,
            "runner_execution_allowed": False,
            "mapped_task_execution_allowed": False,
            "live_device_access_allowed": False,
            "real_device_access_allowed": False,
            "live_network_access_allowed": False,
            "ssh_allowed": False,
            "netconf_allowed": False,
            "restconf_allowed": False,
            "routeros_allowed": False,
        },
        {
            "check_id": "DAY146-NON-ADVANCE-005",
            "name": "Next phase and Day147 remain blocked",
            "status": "PASS",
            "execution_provider_api_phase_advanced": False,
            "next_phase_allowed": False,
            "day147_implemented": False,
            "ai_assistance_advanced_beyond_v04": False,
            "reviewer_approval_inferred": False,
        },
    ]


def build_day146_v04_ai_assistance_non_advancement_gate(project_root: Path) -> Dict[str, Any]:
    source_artifacts = build_source_artifact_records(project_root)
    non_advancement_checks = build_non_advancement_checks(source_artifacts)
    day145_frozen_artifacts = [item for item in source_artifacts if item["source_day"] == "Day145"]
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
        "non_advancement_scope": "Day127-Day145",
        "included_day_range": [f"Day{day}" for day in range(127, 146)],
        "frozen_reference_commit_hash": FROZEN_REFERENCE_COMMIT_HASH,
        "source_artifacts": source_artifacts,
        "source_artifact_count": len(source_artifacts),
        "source_artifact_missing_count": sum(1 for item in source_artifacts if item["all_paths_exist"] is not True),
        "day145_frozen_artifacts": day145_frozen_artifacts,
        "non_advancement_checks": non_advancement_checks,
        "explicit_boundary_statements": [
            DAY145_FROZEN_STATEMENT,
            NON_ADVANCEMENT_STATEMENT,
            NO_PROVIDER_API_MODEL_STATEMENT,
            NO_EXECUTION_PATH_STATEMENT,
            NO_SSH_REAL_DEVICE_STATEMENT,
            NO_FOLDER_MOVE_CLEANUP_STATEMENT,
            NEXT_PHASE_LOCK_STATEMENT,
        ],
        "reviewer_next_action": "Review the Day146 gate; do not rerun Day145, implement Day147, unlock providers/APIs/models, invoke execution paths, use live devices, move folders, clean files, or infer approval.",
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
        "non_advancement_scope": "Day127-Day145",
        "frozen_reference_commit_hash": FROZEN_REFERENCE_COMMIT_HASH,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day146_work") is not True:
        errors.append("agents_md_read_before_day146_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    _validate_source_artifacts(report.get("source_artifacts", []), errors)
    _validate_day145_frozen_artifacts(report.get("day145_frozen_artifacts", []), errors)
    _validate_non_advancement_checks(report.get("non_advancement_checks", []), errors)
    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)
    return errors


def _validate_source_artifacts(artifacts: Any, errors: list[str]) -> None:
    if not isinstance(artifacts, list) or len(artifacts) != len(SOURCE_ARTIFACTS):
        errors.append("source_artifacts must cover Day127-Day145.")
        return
    expected_days = [f"Day{day}" for day in range(127, 146)]
    days = [artifact.get("source_day") for artifact in artifacts if isinstance(artifact, Mapping)]
    if days != expected_days:
        errors.append("source_artifacts must be ordered Day127 through Day145.")
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            errors.append("Each source artifact must be an object.")
            continue
        if artifact.get("all_paths_exist") is not True:
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} must have all frozen paths present.")
        if artifact.get("review_mode") != "static_reference_only":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} review_mode must be static_reference_only.")
        if artifact.get("gate_status") != "LOCKED":
            errors.append(f"{artifact.get('artifact_id', '<unknown>')} gate_status must be LOCKED.")
        for field in (
            "write_target",
            "rerun_allowed",
            "rewrite_allowed",
            "repair_allowed",
            "execution_allowed",
            "provider_allowed",
            "api_allowed",
            "next_phase_allowed",
        ):
            if artifact.get(field) is not False:
                errors.append(f"{artifact.get('artifact_id', '<unknown>')} {field} must be false.")


def _validate_day145_frozen_artifacts(day145_artifacts: Any, errors: list[str]) -> None:
    if not isinstance(day145_artifacts, list) or len(day145_artifacts) != 1:
        errors.append("day145_frozen_artifacts must contain exactly one Day145 artifact record.")
        return
    artifact = day145_artifacts[0]
    if not isinstance(artifact, Mapping):
        errors.append("day145_frozen_artifacts entry must be an object.")
        return
    if artifact.get("source_day") != "Day145":
        errors.append("day145_frozen_artifacts must reference Day145.")
    if artifact.get("frozen_input_only") is not True:
        errors.append("Day145 frozen artifact must be frozen_input_only.")
    for field in ("write_target", "rerun_allowed", "rewrite_allowed", "repair_allowed", "next_phase_allowed"):
        if artifact.get(field) is not False:
            errors.append(f"Day145 frozen artifact {field} must be false.")


def _validate_non_advancement_checks(checks: Any, errors: list[str]) -> None:
    if not isinstance(checks, list) or len(checks) != 5:
        errors.append("non_advancement_checks must contain five Day146 checks.")
        return
    for check in checks:
        if not isinstance(check, Mapping):
            errors.append("Each non-advancement check must be an object.")
            continue
        if check.get("status") != "PASS":
            errors.append(f"{check.get('check_id', '<unknown>')} status must be PASS.")
        for field, value in check.items():
            if field in REQUIRED_FALSE_FIELDS and value is not False:
                errors.append(f"{check.get('check_id', '<unknown>')} {field} must be false.")


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        DAY145_FROZEN_STATEMENT,
        NON_ADVANCEMENT_STATEMENT,
        NO_PROVIDER_API_MODEL_STATEMENT,
        NO_EXECUTION_PATH_STATEMENT,
        NO_SSH_REAL_DEVICE_STATEMENT,
        NO_FOLDER_MOVE_CLEANUP_STATEMENT,
        NEXT_PHASE_LOCK_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day146 boundary statements.")


def write_day146_v04_ai_assistance_non_advancement_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day146_v04_ai_assistance_non_advancement_gate(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day146_v04_ai_assistance_non_advancement_gate_html(safe_report, html_path)
    return json_path, html_path


def write_day146_v04_ai_assistance_non_advancement_gate_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    flag_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    artifact_rows = _table_rows(
        (
            item.get("source_day", ""),
            item.get("name", ""),
            item.get("gate_status", ""),
            item.get("all_paths_exist", False),
            item.get("frozen_input_only", False),
            len(item.get("paths", [])),
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
        for item in report.get("non_advancement_checks", [])
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
  <p><strong>{html.escape(DAY145_FROZEN_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NON_ADVANCEMENT_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_PROVIDER_API_MODEL_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_PATH_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_SSH_REAL_DEVICE_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_FOLDER_MOVE_CLEANUP_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NEXT_PHASE_LOCK_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Non-Advancement Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Next Phase Allowed</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
  <h2>Frozen Source Artifacts</h2>
  <table><thead><tr><th>Day</th><th>Name</th><th>Status</th><th>All Paths Exist</th><th>Frozen Input Only</th><th>Path Count</th></tr></thead><tbody>{artifact_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day146_v04_ai_assistance_non_advancement_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day146_v04_ai_assistance_non_advancement_gate(project_root)
    json_path, html_path = write_day146_v04_ai_assistance_non_advancement_gate_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md read before Day146 work: {json.dumps(report['agents_md_read_before_day146_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day146 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(f"non_advancement_scope: {json.dumps(report['non_advancement_scope'])}")
    print(f"frozen_reference_commit_hash: {json.dumps(report['frozen_reference_commit_hash'])}")
    print(f"source_artifact_count: {report['source_artifact_count']}")
    print(f"source_artifact_missing_count: {report['source_artifact_missing_count']}")
    for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
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
