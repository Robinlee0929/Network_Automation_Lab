"""Day147 AI assistance deferred risk register.

This module creates deterministic review-only evidence for deferred AI
Assistance risks after the Day145 evidence freeze and Day146 non-advancement
gate. It does not enable providers, APIs, models, execution paths, SSH,
live-device access, or network operations.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple

import day146_v04_ai_assistance_non_advancement_gate as day146_gate


DAY = 147
DAY_LABEL = "Day147"
TASK_NAME = "ai-assistance-deferred-risk-register"
TITLE = "AI Assistance Deferred Risk Register"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY_DEFERRED_RISK_REGISTER"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
READY_STATUS = "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY"
BLOCKED_STATUS = "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_BLOCKED"
FINAL_RECOMMENDATION = "KEEP_AI_ASSISTANCE_DEFERRED_AND_NEXT_PHASE_FALSE"
REPORT_JSON = Path("reports") / "lab-summary" / "day147_ai_assistance_deferred_risk_register.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day147_ai_assistance_deferred_risk_register.html"
ROADMAP_DOC = Path("docs") / "roadmap" / "day147_ai_assistance_deferred_risk_register.md"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day147_ai_assistance_deferred_risk_register.md"

DAY145_FREEZE_REFERENCE = day146_gate.FROZEN_REFERENCE_COMMIT_HASH
DAY145_PRESERVATION_STATEMENT = "Day147 does not change Day145 conclusions or mutate frozen evidence."
DAY146_AUTHORITY_STATEMENT = "Day147 preserves the Day146 non-advancement gate as authoritative."
REVIEW_ONLY_STATEMENT = "Day147 documents deferred risks and blocked items only."
NO_PROVIDER_API_MODEL_STATEMENT = "Day147 does not enable, instantiate, call, or prepare providers, APIs, OpenAI API, external AI runtimes, or models."
NO_EXECUTION_PATH_STATEMENT = "Day147 does not create execution paths, runners, brokers, adapters, mapped execution, SSH, NETCONF, RESTCONF, CLI runners, or live network/device operations."
NEXT_PHASE_LOCK_STATEMENT = "Day147 keeps next_phase_allowed=false."

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "review_only",
    "report_only",
    "local_only",
    "deterministic_static_data_only",
    "deferred_risk_register_only",
    "blocked_items_only",
    "day145_freeze_preserved",
    "day146_non_advancement_authoritative",
    "no_new_runtime_surface",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "next_phase_allowed",
    "provider_enabled",
    "api_call_enabled",
    "execution_enabled",
    "model_decision_enabled",
    "live_network_enabled",
    "secrets_required",
    "provider_config_added",
    "api_key_required",
    "openai_api_called",
    "ai_provider_called",
    "external_ai_runtime_allowed",
    "model_invocation_allowed",
    "prompt_submission_enabled",
    "model_selection_enabled",
    "execution_path_created",
    "runner_execution_allowed",
    "broker_execution_allowed",
    "adapter_execution_allowed",
    "mapped_execution_allowed",
    "cli_runner_enabled",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "routeros_allowed",
    "http_client_enabled",
    "live_device_access_allowed",
    "real_device_access_allowed",
    "configuration_change_allowed",
    "config_write_apply_allowed",
    "reset_reboot_remove_disable_enable_allowed",
    "day145_conclusion_changed",
    "day145_evidence_mutated",
    "day146_conclusion_changed",
    "day146_gate_bypassed",
    "day148_implemented",
    "day149_implemented",
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
    "agents_md_read_before_day147_work",
    "day145_freeze_reference",
    "day146_gate_status",
    "risk_register",
    "risk_count",
    "final_recommendation",
)

RISK_FIELD_NAMES: Tuple[str, ...] = (
    "risk_id",
    "title",
    "source_day_or_evidence",
    "category",
    "status",
    "severity",
    "blocking_reason",
    "deferral_reason",
    "required_condition_to_reopen",
    "forbidden_until_reopened",
    "evidence_reference",
    "owner_or_review_role",
    "follow_up_type",
    "next_phase_allowed",
    "unsafe_flags",
)

REQUIRED_CATEGORIES: Tuple[str, ...] = (
    "AI provider/API invocation remains blocked",
    "AI execution path remains blocked",
    "Model decision-making remains blocked",
    "Prompt/summary/display output must remain review-only",
    "Redaction/no-secret policy must remain enforced",
    "Demo/export/draft/diff display consistency remains deferred to Day148",
    "Docs/registry/report-index consistency remains deferred to Day149",
    "Evidence freeze mutation risk from Day145 must remain controlled",
    "Non-advancement gate from Day146 must remain authoritative",
    "Future live/device/network/API integration requires a separate safety gate",
)

UNSAFE_FLAG_KEYS: Tuple[str, ...] = (
    "provider_enabled",
    "api_call_enabled",
    "execution_enabled",
    "model_decision_enabled",
    "live_network_enabled",
    "secrets_required",
    "next_phase_allowed",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read_result": FAIL_STATUS,
            "agents_md_read_before_day147_work": False,
            "agents_md_modified": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_status": f"READ_ERROR: {exc}",
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if markers_present else FAIL_STATUS,
        "agents_md_read_before_day147_work": markers_present,
        "agents_md_modified": False,
        "agents_md_path": "AGENTS.md",
        "agents_md_status": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
    }


def _unsafe_flags() -> Dict[str, bool]:
    return {field: False for field in UNSAFE_FLAG_KEYS}


def build_risk_register() -> list[Dict[str, Any]]:
    risks = [
        (
            "DAY147-RISK-001",
            "Provider and API invocation remains blocked",
            "Day133-Day146 provider disabled evidence",
            REQUIRED_CATEGORIES[0],
            "BLOCKED_DEFERRED",
            "CRITICAL",
            "No provider/API safety gate exists and no provider runtime may be activated.",
            "Only deferred risk documentation is in scope for Day147.",
            "A separately approved provider/API safety gate with negative tests and reviewer approval.",
            "Provider SDK imports, API key handling, provider config, HTTP calls, OpenAI API calls, and external AI runtime activation.",
            "Day133 disabled provider boundary; Day134 adapter contract; Day135 regression; Day146 non-advancement gate",
            "Safety reviewer",
            "separate_safety_gate_required",
        ),
        (
            "DAY147-RISK-002",
            "AI execution path remains blocked",
            "Day141-Day146 review-only AI Assistance track",
            REQUIRED_CATEGORIES[1],
            "BLOCKED_DEFERRED",
            "CRITICAL",
            "Execution paths would bypass the non-advancement gate.",
            "Day147 records the blocked state only.",
            "A future approved execution safety gate proving rejected intents never reach runners, brokers, adapters, or mapped tasks.",
            "Runner, broker, adapter, CLI runner, mapped execution, subprocess execution, and automatic apply paths.",
            "Day141 demo package; Day142 display contract; Day143 diff viewer; Day146 gate",
            "Safety reviewer",
            "blocked_item_review",
        ),
        (
            "DAY147-RISK-003",
            "Model decision-making remains blocked",
            "Day127-Day146 reviewer summary and non-advancement evidence",
            REQUIRED_CATEGORIES[2],
            "BLOCKED_DEFERRED",
            "HIGH",
            "The project has no approval for model decisions, approval inference, or autonomous routing.",
            "Decision capability is outside Day147 scope.",
            "A future safety gate defining model decision limits, reviewer controls, and no-execution proof.",
            "Model invocation, model-selected actions, approval inference, task routing, or execution recommendations treated as approval.",
            "Day127 schema; Day129 prompt contract; Day131 audit binding; Day146 gate",
            "Reviewer workflow owner",
            "future_design_review",
        ),
        (
            "DAY147-RISK-004",
            "Prompt summary and display output stay review-only",
            "Day127-Day143 summary, display, and diff evidence",
            REQUIRED_CATEGORIES[3],
            "BLOCKED_DEFERRED",
            "HIGH",
            "Reviewer-visible text and displays must not become execution inputs.",
            "Day148 will review display consistency separately.",
            "A separate display-to-action gate proving display output cannot trigger execution or approval.",
            "Treating prompt text, summaries, exports, drafts, or diffs as runnable intent or device commands.",
            "Day127 summary schema; Day142 display contract; Day143 safety diff viewer",
            "Reviewer workflow owner",
            "day148_follow_up",
        ),
        (
            "DAY147-RISK-005",
            "Redaction and no-secret policy remains enforced",
            "Day130 redaction policy and AGENTS.md safety rules",
            REQUIRED_CATEGORIES[4],
            "BLOCKED_DEFERRED",
            "CRITICAL",
            "Provider/API work remains blocked and secrets must not be required or stored.",
            "Day147 does not introduce secret-bearing config or live endpoints.",
            "A future no-secret review that keeps public documentation safe and proves secrets are not needed.",
            "Secrets, tokens, credentials, API keys, private local paths, provider configs, and live endpoint examples.",
            "Day130 redaction/no-secret policy; AGENTS.md Core Safety Rules",
            "Security reviewer",
            "policy_enforcement",
        ),
        (
            "DAY147-RISK-006",
            "Demo export draft diff display consistency deferred to Day148",
            "Day141-Day143 and Day136 display/export evidence",
            REQUIRED_CATEGORIES[5],
            "DEFERRED_TO_DAY148",
            "MEDIUM",
            "Display consistency review needs its own bounded task and must not unlock execution.",
            "Day147 only records the deferred item.",
            "Day148 review-only task completes consistency checks while keeping all execution/provider flags false.",
            "Implementing Day148 behavior, generating runnable drafts, applying diffs, or saving device-ready commands.",
            "Day136 export package; Day141 demo package; Day142 display contract; Day143 diff viewer",
            "AI Assistance reviewer",
            "day148_follow_up",
        ),
        (
            "DAY147-RISK-007",
            "Docs registry and report-index consistency deferred to Day149",
            "Task catalog and report-index evidence",
            REQUIRED_CATEGORIES[6],
            "DEFERRED_TO_DAY149",
            "MEDIUM",
            "A wider docs/registry/report-index sweep must stay separate from Day147 risk registration.",
            "Day147 adds only its own required local registry and report-index visibility.",
            "Day149 review-only consistency task completes the broader sweep without changing gates.",
            "Broad registry rewrites, unrelated report-index reshaping, task renames, or phase advancement.",
            "network_lab task catalog; report-index local visibility",
            "Documentation reviewer",
            "day149_follow_up",
        ),
        (
            "DAY147-RISK-008",
            "Day145 evidence freeze mutation risk remains controlled",
            "Day145 evidence freeze package",
            REQUIRED_CATEGORIES[7],
            "LOCKED",
            "CRITICAL",
            "Frozen evidence must remain a static reference and must not be rerun, rewritten, repaired, or mutated.",
            "Day147 references Day145 but does not modify it.",
            "A separately approved evidence maintenance gate with explicit mutation authorization.",
            "Changing Day145 source, docs, roadmap, JSON/HTML reports, conclusions, or frozen reference state.",
            f"Day145 freeze reference commit {DAY145_FREEZE_REFERENCE}",
            "Evidence reviewer",
            "freeze_control",
        ),
        (
            "DAY147-RISK-009",
            "Day146 non-advancement gate remains authoritative",
            "Day146 non-advancement gate",
            REQUIRED_CATEGORIES[8],
            "LOCKED",
            "CRITICAL",
            "Day146 explicitly blocks Day147 from advancing the next phase.",
            "Day147 must preserve the gate and only document deferred risks.",
            "A future explicit safety gate that supersedes Day146 with reviewer approval and equivalent negative tests.",
            "Bypassing Day146, inferring approval, setting next_phase_allowed=true, or advancing provider/API/execution phase.",
            "Day146 non-advancement gate JSON/HTML and docs",
            "Safety reviewer",
            "gate_authority_review",
        ),
        (
            "DAY147-RISK-010",
            "Future live device network API integration requires separate safety gate",
            "AGENTS.md and Day89-Day146 safety-boundary evidence",
            REQUIRED_CATEGORIES[9],
            "BLOCKED_DEFERRED",
            "CRITICAL",
            "Live/device/network/API integration is prohibited without a separate approved gate and operation-specific approval.",
            "Day147 has no live-capable scope.",
            "A future live-capable safety gate plus separate user approval for each specific live operation.",
            "SSH, NETCONF, RESTCONF, RouterOS, HTTP API calls, real network commands, live devices, config writes, reset/reboot/remove/disable/enable actions.",
            "AGENTS.md Core Safety Rules; Day89 safety boundary; Day146 gate",
            "Safety reviewer",
            "separate_live_gate_required",
        ),
    ]
    return [
        {
            "risk_id": risk_id,
            "title": title,
            "source_day_or_evidence": source,
            "category": category,
            "status": status,
            "severity": severity,
            "blocking_reason": blocking_reason,
            "deferral_reason": deferral_reason,
            "required_condition_to_reopen": required_condition,
            "forbidden_until_reopened": forbidden,
            "evidence_reference": evidence,
            "owner_or_review_role": owner,
            "follow_up_type": follow_up,
            "next_phase_allowed": False,
            "unsafe_flags": _unsafe_flags(),
        }
        for (
            risk_id,
            title,
            source,
            category,
            status,
            severity,
            blocking_reason,
            deferral_reason,
            required_condition,
            forbidden,
            evidence,
            owner,
            follow_up,
        ) in risks
    ]


def build_day147_ai_assistance_deferred_risk_register(project_root: Path) -> Dict[str, Any]:
    risk_register = build_risk_register()
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
        "day145_freeze_reference": DAY145_FREEZE_REFERENCE,
        "day145_conclusion_preserved": True,
        "day146_gate_status": day146_gate.READY_STATUS,
        "day146_non_advancement_preserved": True,
        "risk_register": risk_register,
        "risk_count": len(risk_register),
        "required_categories": list(REQUIRED_CATEGORIES),
        "explicit_boundary_statements": [
            DAY145_PRESERVATION_STATEMENT,
            DAY146_AUTHORITY_STATEMENT,
            REVIEW_ONLY_STATEMENT,
            NO_PROVIDER_API_MODEL_STATEMENT,
            NO_EXECUTION_PATH_STATEMENT,
            NEXT_PHASE_LOCK_STATEMENT,
        ],
        "expected_task_result": {
            "overall_status": OVERALL_STATUS,
            "status": READY_STATUS,
            "review_only": True,
            "next_phase_allowed": False,
            "provider_enabled": False,
            "api_call_enabled": False,
            "execution_enabled": False,
            "model_decision_enabled": False,
            "live_network_enabled": False,
            "secrets_required": False,
        },
        "reviewer_next_action": "Review the Day147 deferred risk register; do not enable providers, APIs, models, execution, live devices, SSH, network calls, secrets, Day148, Day149, or next phase.",
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
        "day145_freeze_reference": DAY145_FREEZE_REFERENCE,
        "day146_gate_status": day146_gate.READY_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("agents_md_pre_read_result must be PASS.")
    if report.get("agents_md_read_before_day147_work") is not True:
        errors.append("agents_md_read_before_day147_work must be true.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    if report.get("day145_conclusion_preserved") is not True:
        errors.append("day145_conclusion_preserved must be true.")
    if report.get("day146_non_advancement_preserved") is not True:
        errors.append("day146_non_advancement_preserved must be true.")

    _validate_risk_register(report.get("risk_register", []), errors)
    _validate_expected_task_result(report.get("expected_task_result", {}), errors)
    _validate_boundary_statements(report.get("explicit_boundary_statements", []), errors)
    return errors


def _validate_risk_register(risks: Any, errors: list[str]) -> None:
    if not isinstance(risks, list) or len(risks) != len(REQUIRED_CATEGORIES):
        errors.append("risk_register must contain ten Day147 risk records.")
        return
    categories = []
    for risk in risks:
        if not isinstance(risk, Mapping):
            errors.append("Each risk register entry must be an object.")
            continue
        for field in RISK_FIELD_NAMES:
            if field not in risk:
                errors.append(f"{risk.get('risk_id', '<unknown>')} {field} is missing.")
        categories.append(risk.get("category"))
        if risk.get("status") not in {"BLOCKED_DEFERRED", "DEFERRED_TO_DAY148", "DEFERRED_TO_DAY149", "LOCKED"}:
            errors.append(f"{risk.get('risk_id', '<unknown>')} status must be deferred or locked.")
        if risk.get("next_phase_allowed") is not False:
            errors.append(f"{risk.get('risk_id', '<unknown>')} next_phase_allowed must be false.")
        unsafe_flags = risk.get("unsafe_flags")
        if not isinstance(unsafe_flags, Mapping):
            errors.append(f"{risk.get('risk_id', '<unknown>')} unsafe_flags must be an object.")
            continue
        for field in UNSAFE_FLAG_KEYS:
            if unsafe_flags.get(field) is not False:
                errors.append(f"{risk.get('risk_id', '<unknown>')} unsafe_flags.{field} must be false.")
    if categories != list(REQUIRED_CATEGORIES):
        errors.append("risk_register categories must match the required Day147 categories in order.")


def _validate_expected_task_result(result: Any, errors: list[str]) -> None:
    if not isinstance(result, Mapping):
        errors.append("expected_task_result must be an object.")
        return
    expected = {
        "overall_status": OVERALL_STATUS,
        "status": READY_STATUS,
        "review_only": True,
        "next_phase_allowed": False,
        "provider_enabled": False,
        "api_call_enabled": False,
        "execution_enabled": False,
        "model_decision_enabled": False,
        "live_network_enabled": False,
        "secrets_required": False,
    }
    for field, value in expected.items():
        if result.get(field) != value:
            errors.append(f"expected_task_result.{field} must be {json.dumps(value)}.")


def _validate_boundary_statements(statements: Any, errors: list[str]) -> None:
    required = {
        DAY145_PRESERVATION_STATEMENT,
        DAY146_AUTHORITY_STATEMENT,
        REVIEW_ONLY_STATEMENT,
        NO_PROVIDER_API_MODEL_STATEMENT,
        NO_EXECUTION_PATH_STATEMENT,
        NEXT_PHASE_LOCK_STATEMENT,
    }
    if not isinstance(statements, list) or not required.issubset(set(statements)):
        errors.append("explicit_boundary_statements must include all Day147 boundary statements.")


def write_day147_ai_assistance_deferred_risk_register_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_day147_ai_assistance_deferred_risk_register(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day147_ai_assistance_deferred_risk_register_html(safe_report, html_path)
    return json_path, html_path


def write_day147_ai_assistance_deferred_risk_register_html(
    report: Mapping[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS if field in report)
    flag_rows = _table_rows((field, report[field]) for field in REQUIRED_TRUE_FIELDS + REQUIRED_FALSE_FIELDS)
    risk_rows = _table_rows(
        (
            item.get("risk_id", ""),
            item.get("category", ""),
            item.get("status", ""),
            item.get("severity", ""),
            item.get("follow_up_type", ""),
            item.get("next_phase_allowed", False),
        )
        for item in report.get("risk_register", [])
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
  <p><strong>{html.escape(DAY145_PRESERVATION_STATEMENT)}</strong></p>
  <p><strong>{html.escape(DAY146_AUTHORITY_STATEMENT)}</strong></p>
  <p><strong>{html.escape(REVIEW_ONLY_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_PROVIDER_API_MODEL_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NO_EXECUTION_PATH_STATEMENT)}</strong></p>
  <p><strong>{html.escape(NEXT_PHASE_LOCK_STATEMENT)}</strong></p>
  <h2>Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Deferred Risk Register</h2>
  <table><thead><tr><th>ID</th><th>Category</th><th>Status</th><th>Severity</th><th>Follow-up</th><th>Next Phase Allowed</th></tr></thead><tbody>{risk_rows}</tbody></table>
  <h2>Safety Flags</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{flag_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_day147_ai_assistance_deferred_risk_register(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_day147_ai_assistance_deferred_risk_register(project_root)
    json_path, html_path = write_day147_ai_assistance_deferred_risk_register_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read_result']}")
    print(f"AGENTS.md read before Day147 work: {json.dumps(report['agents_md_read_before_day147_work'])}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(FULL_TITLE))
    print(f"Day147 task: {TITLE}")
    print(f"Task slug: {TASK_NAME}")
    for statement in report["explicit_boundary_statements"]:
        print(statement)
    print(f"day145_freeze_reference: {json.dumps(report['day145_freeze_reference'])}")
    print(f"day146_gate_status: {json.dumps(report['day146_gate_status'])}")
    print(f"risk_count: {report['risk_count']}")
    for risk in report["risk_register"]:
        print(f"{risk['risk_id']}: {risk['category']} | {risk['status']} | next_phase_allowed=false")
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
