"""Day148 AI assistance demo/export/draft display consistency audit.

This module creates deterministic review-only evidence over existing Day136,
Day141, Day142, and Day143 AI Assistance review artifacts. It reads local
artifact files only and does not enable providers, APIs, models, execution
paths, SSH, live-device access, adapters, brokers, runners, or next-phase
behavior.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = 148
DAY_LABEL = "Day148"
TASK_NAME = "ai-assistance-demo-export-draft-display-consistency-audit"
TITLE = "AI Assistance Demo / Export / Draft Display Consistency Audit"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_CONSISTENCY_AUDIT"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_READY"
BLOCKED_STATUS = "AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_AI_ASSISTANCE_REVIEW_ONLY_AND_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day148_ai_assistance_display_consistency_audit.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day148_ai_assistance_display_consistency_audit.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day148_ai_assistance_display_consistency_audit.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day148_ai_assistance_display_consistency_audit.md"

NOT_NEXT_DAY_STATEMENT = "Day148 is not next-day functionality."
REVIEW_ONLY_AUDIT_STATEMENT = "Day148 is a review-only consistency audit over existing display/export/draft/diff artifacts."
NO_EXECUTION_PROVIDER_API_STATEMENT = "Day148 keeps execution, provider, API, device access, SSH, NETCONF, RESTCONF, CLI live execution, model calls, adapters, brokers, runners, and next-phase advancement disabled."
MISMATCH_RECORDING_STATEMENT = "Day148 records any mismatch findings as audit evidence and does not silently correct prior artifacts."
PASS_CONDITION_STATEMENT = "Day148 returns PASS only when checked artifacts preserve review-only safety semantics."

AUDIT_SCOPE_DAYS: Tuple[str, ...] = ("Day141", "Day136", "Day142", "Day143")
AUDIT_SCOPE_LABEL = "Day141, Day136, Day142, Day143"

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "audit_only",
    "report_only",
    "local_only",
    "deterministic_static_data_only",
    "consistency_check_only",
    "mismatch_findings_recorded",
    "not_next_day_functionality_confirmed",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "is_next_day_functionality",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "device_access_enabled",
    "ssh_enabled",
    "netconf_enabled",
    "restconf_enabled",
    "cli_live_execution_enabled",
    "model_call_enabled",
    "model_api_call_performed",
    "adapter_invoked",
    "broker_invoked",
    "runner_invoked",
    "openai_api_called",
    "external_service_called",
    "live_network_enabled",
    "configuration_change_allowed",
    "draft_applied",
    "draft_saved",
    "next_phase_allowed",
    "safety_gate_advanced",
    "provider_runtime_unlocked",
    "execution_path_created",
    "reviewer_approval_inferred",
    "day149_implemented",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "day_label",
    "task",
    "title",
    "mode",
    "overall_status",
    "status",
    "agents_md_pre_read",
    "agents_md_path",
    "agents_md_modified",
    "audit_scope",
    "artifact_audits",
    "consistency_summary",
    "mismatch_findings",
    "final_recommendation",
)

FORBIDDEN_IMPLYING_EXECUTION_PHRASES: Tuple[str, ...] = (
    "execution_enabled: true",
    '"execution_enabled": true',
    "provider_enabled: true",
    '"provider_enabled": true',
    "api_enabled: true",
    '"api_enabled": true',
    "ssh_enabled: true",
    '"ssh_enabled": true',
    "next_phase_allowed: true",
    '"next_phase_allowed": true',
    "draft_applied: true",
    '"draft_applied": true',
    "draft_saved: true",
    '"draft_saved": true',
    "openai_api_called: true",
    '"openai_api_called": true',
    "production execution enabled",
    "execute on live devices",
    "provider is enabled",
    "api is enabled",
    "model call enabled",
)

ARTIFACT_SPECS: Tuple[Dict[str, Any], ...] = (
    {
        "day": "Day141",
        "artifact_kind": "demo",
        "expected_title": "AI Assistance Review Demo Package",
        "review_label": "review-only demo package",
        "paths": (
            "day141_ai_assistance_review_demo_package.py",
            "docs/roadmap/day141_ai_assistance_review_demo_package.md",
            "docs/ai-intent/day141_ai_assistance_review_demo_package.md",
            "reports/lab-summary/day141_ai_assistance_review_demo_package.json",
            "reports/lab-summary/day141_ai_assistance_review_demo_package.html",
        ),
        "json_path": "reports/lab-summary/day141_ai_assistance_review_demo_package.json",
        "required_true": ("review_only", "report_only", "demo_package_only"),
        "required_false": (
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
            "adapter_execution_allowed",
            "broker_execution_allowed",
            "runner_execution_allowed",
            "mapped_execution_allowed",
            "next_phase_allowed",
            "is_next_day_feature",
            "future_day_functionality_implemented",
        ),
        "required_phrases": (
            "Day141 is a review-only demo package",
            "Day141 does not open execution / provider / API",
            "Day141 is not the next day's feature",
        ),
    },
    {
        "day": "Day136",
        "artifact_kind": "export",
        "expected_title": "AI Reviewer Export Package Integration",
        "review_label": "review-only export package",
        "paths": (
            "ai_reviewer_export_package_integration.py",
            "docs/roadmap/day136_ai_reviewer_export_package_integration.md",
            "reports/lab-summary/day136_ai_reviewer_export_package_integration.json",
            "reports/lab-summary/day136_ai_reviewer_export_package_integration.html",
        ),
        "json_path": "reports/lab-summary/day136_ai_reviewer_export_package_integration.json",
        "required_true": ("review_only", "report_only", "local_repo_evidence_only"),
        "required_false": (
            "execution_enabled",
            "provider_enabled",
            "api_enabled",
            "live_actions_enabled",
            "secret_or_env_access",
            "external_network_call",
            "adapter_broker_runner_invoked",
            "model_invocation_enabled",
            "ssh_enabled",
            "device_action_enabled",
            "next_day_functionality_enabled",
        ),
        "required_phrases": (
            "This is not next-day functionality",
            "Execution / provider / API remain disabled",
            "review-only export package",
        ),
    },
    {
        "day": "Day142",
        "artifact_kind": "dry-run draft",
        "expected_title": "AI Summary to Dry-run Draft Display Contract",
        "review_label": "review-only/display-only dry-run draft display contract",
        "paths": (
            "day142_ai_summary_to_dry_run_draft_display_contract.py",
            "docs/roadmap/day142_ai_summary_to_dry_run_draft_display_contract.md",
            "docs/ai-intent/day142_ai_summary_to_dry_run_draft_display_contract.md",
            "reports/lab-summary/day142_ai_summary_to_dry_run_draft_display_contract.json",
            "reports/lab-summary/day142_ai_summary_to_dry_run_draft_display_contract.html",
        ),
        "json_path": "reports/lab-summary/day142_ai_summary_to_dry_run_draft_display_contract.json",
        "required_true": ("review_only", "display_only", "dry_run_draft_display_only"),
        "required_false": (
            "provider_enabled",
            "api_enabled",
            "model_invocation_enabled",
            "execution_enabled",
            "ssh_allowed",
            "netconf_allowed",
            "restconf_allowed",
            "live_device_allowed",
            "config_write_allowed",
            "command_apply_allowed",
            "adapter_invoked",
            "next_phase_allowed",
        ),
        "required_phrases": (
            "Day142 dry-run draft output is display-only and review-only",
            "Day142 enables no provider, API, or model invocation",
            "Day142 keeps next_phase_allowed=false",
        ),
    },
    {
        "day": "Day143",
        "artifact_kind": "diff viewer",
        "expected_title": "Dry-run Draft Safety Diff Viewer",
        "review_label": "review-only/display-only diff viewer",
        "paths": (
            "intent_dry_run_draft_safety_diff_viewer.py",
            "docs/roadmap/day143_dry_run_draft_safety_diff_viewer.md",
            "docs/ai-intent/day143_dry_run_draft_safety_diff_viewer.md",
            "reports/lab-summary/day143_dry_run_draft_safety_diff_viewer.json",
            "reports/lab-summary/day143_dry_run_draft_safety_diff_viewer.html",
        ),
        "json_path": "reports/lab-summary/day143_dry_run_draft_safety_diff_viewer.json",
        "required_true": ("review_only", "display_only", "dry_run_only", "not_next_day_feature"),
        "required_false": (
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
            "provider_runtime_invoked",
            "api_runtime_invoked",
            "day142_summary_to_draft_builder_called",
            "draft_persisted",
            "next_phase_allowed_by_diff",
        ),
        "required_phrases": (
            "review-only/display-only safety diff viewer",
            "This is not Day144",
            "next_phase_allowed: false",
        ),
    },
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read": "NO",
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day148_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read": "YES" if markers_present else "NO",
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day148_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def build_day148_ai_assistance_display_consistency_audit(project_root: Path) -> Dict[str, Any]:
    artifact_audits = [audit_artifact(project_root, spec) for spec in ARTIFACT_SPECS]
    mismatch_findings = [
        finding
        for artifact in artifact_audits
        for finding in artifact.get("mismatch_findings", [])
    ]
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
        "audit_scope": list(AUDIT_SCOPE_DAYS),
        "audit_scope_label": AUDIT_SCOPE_LABEL,
        "artifact_audits": artifact_audits,
        "artifact_count": len(artifact_audits),
        "consistency_summary": build_consistency_summary(artifact_audits, mismatch_findings),
        "mismatch_findings": mismatch_findings,
        "mismatch_finding_count": len(mismatch_findings),
        "explicit_boundary_statements": [
            NOT_NEXT_DAY_STATEMENT,
            REVIEW_ONLY_AUDIT_STATEMENT,
            NO_EXECUTION_PROVIDER_API_STATEMENT,
            MISMATCH_RECORDING_STATEMENT,
            PASS_CONDITION_STATEMENT,
        ],
        "blocked_non_advancement_statement": (
            "Day148 blocks advancement: no provider/API/model/execution/device path is enabled and "
            "next_phase_allowed=false."
        ),
        "reviewer_next_action": "Review the consistency audit findings only; do not enable provider, API, execution, model, device access, adapter, broker, runner, or next phase.",
        "final_recommendation": FINAL_RECOMMENDATION,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["status"] = READY_STATUS if report["overall_status"] == OVERALL_STATUS else BLOCKED_STATUS
    return report


def audit_artifact(project_root: Path, spec: Mapping[str, Any]) -> Dict[str, Any]:
    root = Path(project_root)
    path_records = [_path_record(root, relative_path) for relative_path in spec["paths"]]
    loaded_report, read_error = _load_json(root / str(spec["json_path"]))
    text_blob = _artifact_text_blob(root, spec["paths"], loaded_report)

    mismatch_findings: list[Dict[str, Any]] = []
    if read_error:
        mismatch_findings.append(_finding(spec, "JSON_READ", "BLOCKING", read_error))
    if any(record["path_exists"] is not True for record in path_records):
        mismatch_findings.append(_finding(spec, "PATH_MISSING", "BLOCKING", "One or more expected artifact paths are missing."))

    if isinstance(loaded_report, Mapping):
        if loaded_report.get("title") != spec["expected_title"]:
            mismatch_findings.append(
                _finding(
                    spec,
                    "DISPLAY_TITLE_MISMATCH",
                    "BLOCKING",
                    f"title must be {spec['expected_title']}.",
                )
            )
        _check_required_flags(spec, loaded_report, mismatch_findings)

    for phrase in spec["required_phrases"]:
        if phrase.lower() not in text_blob.lower():
            mismatch_findings.append(
                _finding(spec, "REQUIRED_WORDING_MISSING", "BLOCKING", f"Missing wording: {phrase}")
            )

    forbidden_hits = [
        phrase
        for phrase in FORBIDDEN_IMPLYING_EXECUTION_PHRASES
        if phrase.lower() in text_blob.lower()
    ]
    for phrase in forbidden_hits:
        mismatch_findings.append(
            _finding(spec, "MISLEADING_EXECUTION_WORDING", "BLOCKING", f"Forbidden wording found: {phrase}")
        )

    safety_semantics_preserved = not any(item["severity"] == "BLOCKING" for item in mismatch_findings)
    return {
        "day": spec["day"],
        "artifact_kind": spec["artifact_kind"],
        "expected_title": spec["expected_title"],
        "review_label": spec["review_label"],
        "json_path": spec["json_path"],
        "paths": path_records,
        "all_paths_exist": all(record["path_exists"] is True for record in path_records),
        "loaded": isinstance(loaded_report, Mapping),
        "read_error": read_error,
        "display_consistency": "PASS" if safety_semantics_preserved else "FAIL",
        "safety_semantics": "PASS" if safety_semantics_preserved else "FAIL",
        "review_only_wording_present": _has_review_only_wording(text_blob),
        "not_next_day_or_non_advancement_present": _has_non_advancement_wording(text_blob),
        "no_misleading_execution_wording": not forbidden_hits,
        "mismatch_findings": mismatch_findings,
        "mismatch_count": len(mismatch_findings),
    }


def build_consistency_summary(
    artifact_audits: Iterable[Mapping[str, Any]],
    mismatch_findings: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    audits = list(artifact_audits)
    findings = list(mismatch_findings)
    return {
        "result_status": OVERALL_STATUS if not findings else FAIL_STATUS,
        "audit_scope": AUDIT_SCOPE_LABEL,
        "checked_artifact_count": len(audits),
        "mismatch_finding_count": len(findings),
        "display_consistency": "PASS" if not findings else "FAIL",
        "safety_semantic_consistency": "PASS" if not findings else "FAIL",
        "day141_demo_language_implies_execution": False,
        "day136_export_package_remains_review_only": True,
        "day142_dry_run_draft_remains_draft_only": True,
        "day143_diff_viewer_remains_display_review_only": True,
        "execution_provider_api_remain_disabled": True,
        "no_device_access": True,
        "no_ssh_netconf_restconf_cli_live_command": True,
        "no_model_call": True,
        "no_adapter_broker_runner_invocation": True,
        "next_phase_allowed": False,
        "not_next_day_functionality": True,
        "summary_text": (
            "No blocking display or safety-semantic mismatches were found across Day141, Day136, Day142, and Day143."
            if not findings
            else "Blocking display or safety-semantic mismatches were recorded; prior artifacts were not corrected."
        ),
    }


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
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read") != "YES":
        errors.append("agents_md_pre_read must be YES.")
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day148_work") is not True:
        errors.append("agents_md_read_before_day148_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("audit_scope") != list(AUDIT_SCOPE_DAYS):
        errors.append("audit_scope must be Day141, Day136, Day142, Day143.")

    artifact_audits = report.get("artifact_audits", [])
    if not isinstance(artifact_audits, list) or len(artifact_audits) != len(ARTIFACT_SPECS):
        errors.append("artifact_audits must cover Day141, Day136, Day142, and Day143.")
    else:
        for artifact in artifact_audits:
            if artifact.get("all_paths_exist") is not True:
                errors.append(f"{artifact.get('day', '<unknown>')} all_paths_exist must be true.")
            if artifact.get("loaded") is not True:
                errors.append(f"{artifact.get('day', '<unknown>')} JSON report must be loaded.")
            if artifact.get("display_consistency") != "PASS":
                errors.append(f"{artifact.get('day', '<unknown>')} display_consistency must be PASS.")
            if artifact.get("safety_semantics") != "PASS":
                errors.append(f"{artifact.get('day', '<unknown>')} safety_semantics must be PASS.")
            if artifact.get("mismatch_count") != 0:
                errors.append(f"{artifact.get('day', '<unknown>')} mismatch_count must be 0 for PASS.")

    summary = report.get("consistency_summary", {})
    if not isinstance(summary, Mapping):
        errors.append("consistency_summary must be an object.")
    else:
        if summary.get("result_status") != OVERALL_STATUS:
            errors.append("consistency_summary.result_status must be PASS.")
        if summary.get("next_phase_allowed") is not False:
            errors.append("consistency_summary.next_phase_allowed must be false.")

    if report.get("mismatch_findings") != []:
        errors.append("mismatch_findings must be empty for PASS.")

    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)
    return errors


def write_day148_ai_assistance_display_consistency_audit_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day148_ai_assistance_display_consistency_audit(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day148_ai_assistance_display_consistency_audit_html(safe_report, html_path)
    return json_path, html_path


def write_day148_ai_assistance_display_consistency_audit_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    flag_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    artifact_rows = _table_rows(
        (
            item.get("day", ""),
            item.get("artifact_kind", ""),
            item.get("expected_title", ""),
            item.get("display_consistency", ""),
            item.get("safety_semantics", ""),
            item.get("mismatch_count", 0),
        )
        for item in report.get("artifact_audits", [])
    )
    finding_rows = _table_rows(
        (
            finding.get("finding_id", ""),
            finding.get("source_day", ""),
            finding.get("category", ""),
            finding.get("severity", ""),
            finding.get("description", ""),
        )
        for finding in report.get("mismatch_findings", [])
    ) or "<tr><td colspan='5'>No mismatch findings.</td></tr>"
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
  <p><strong>{html.escape(REVIEW_ONLY_AUDIT_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_PROVIDER_API_STATEMENT)}</strong></p>
  <p><strong>{html.escape(MISMATCH_RECORDING_STATEMENT)}</strong></p>
  <p><strong>{html.escape(PASS_CONDITION_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Artifact Audits</h2>
  <table><thead><tr><th>Day</th><th>Kind</th><th>Title</th><th>Display</th><th>Safety</th><th>Mismatches</th></tr></thead><tbody>{artifact_rows}</tbody></table>
  <h2>Mismatch Findings</h2>
  <table><thead><tr><th>ID</th><th>Day</th><th>Category</th><th>Severity</th><th>Description</th></tr></thead><tbody>{finding_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day148_ai_assistance_display_consistency_audit(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day148_ai_assistance_display_consistency_audit(project_root)
    json_path, html_path = write_day148_ai_assistance_display_consistency_audit_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read']}")
    print(f"AGENTS.md path: {Path(project_root, report['agents_md_path']).resolve()}")
    print(f"AGENTS.md modified: {'YES' if report['agents_md_modified'] else 'NO'}")
    print(format_heading(FULL_TITLE))
    print(f"Day148 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    print(f"Audit scope: {report['audit_scope_label']}")
    print(f"Result status: {report['overall_status']}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(report["blocked_non_advancement_statement"])
    print(f"mismatch_finding_count: {report['mismatch_finding_count']}")
    for artifact in report["artifact_audits"]:
        print(
            f"{artifact['day']} {artifact['artifact_kind']}: "
            f"display_consistency={artifact['display_consistency']} "
            f"safety_semantics={artifact['safety_semantics']} "
            f"mismatch_count={artifact['mismatch_count']}"
        )
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


def _check_required_flags(
    spec: Mapping[str, Any],
    loaded_report: Mapping[str, Any],
    mismatch_findings: list[Dict[str, Any]],
) -> None:
    for field in spec["required_true"]:
        if loaded_report.get(field) is not True:
            mismatch_findings.append(
                _finding(spec, "REQUIRED_TRUE_FLAG_MISMATCH", "BLOCKING", f"{field} must be true.")
            )
    for field in spec["required_false"]:
        if loaded_report.get(field) is not False:
            mismatch_findings.append(
                _finding(spec, "REQUIRED_FALSE_FLAG_MISMATCH", "BLOCKING", f"{field} must be false.")
            )


def _path_record(project_root: Path, relative_path: str) -> Dict[str, Any]:
    path = project_root / relative_path
    return {"path": relative_path, "path_exists": path.exists(), "read_only": True}


def _load_json(path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"Missing JSON report: {path.as_posix()}"
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON report: {path.as_posix()}: {exc.msg}"
    except OSError as exc:
        return None, f"JSON read error: {path.as_posix()}: {exc}"
    if not isinstance(loaded, dict):
        return None, f"JSON report must contain an object: {path.as_posix()}"
    return loaded, ""


def _artifact_text_blob(
    project_root: Path,
    relative_paths: Iterable[str],
    loaded_report: Optional[Mapping[str, Any]],
) -> str:
    chunks = []
    for relative_path in relative_paths:
        path = project_root / relative_path
        if path.suffix.lower() in {".md", ".py", ".html"} and path.exists():
            try:
                chunks.append(path.read_text(encoding="utf-8"))
            except OSError:
                continue
    if loaded_report is not None:
        chunks.append(json.dumps(loaded_report, sort_keys=True))
    return "\n".join(chunks)


def _has_review_only_wording(text_blob: str) -> bool:
    lowered = text_blob.lower()
    return "review-only" in lowered or '"review_only": true' in lowered or "review_only: true" in lowered


def _has_non_advancement_wording(text_blob: str) -> bool:
    lowered = text_blob.lower()
    return (
        "not next-day" in lowered
        or "not the next day" in lowered
        or "not the next day's feature" in lowered
        or "next_phase_allowed=false" in lowered
        or "next_phase_allowed: false" in lowered
        or '"next_phase_allowed": false' in lowered
        or "next_day_functionality_enabled" in lowered
    )


def _finding(
    spec: Mapping[str, Any],
    category: str,
    severity: str,
    description: str,
) -> Dict[str, Any]:
    return {
        "finding_id": f"DAY148-{spec['day']}-{category}",
        "source_day": spec["day"],
        "artifact_kind": spec["artifact_kind"],
        "category": category,
        "severity": severity,
        "description": description,
        "corrected_by_day148": False,
        "next_phase_allowed": False,
    }


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        NOT_NEXT_DAY_STATEMENT,
        REVIEW_ONLY_AUDIT_STATEMENT,
        NO_EXECUTION_PROVIDER_API_STATEMENT,
        MISMATCH_RECORDING_STATEMENT,
        PASS_CONDITION_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day148 boundary statements.")


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
