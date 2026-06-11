"""Day106 Codex AGENTS.md instruction compliance audit.

The audit reads only the repository-level AGENTS.md file and writes reviewer
evidence. It does not execute adapters, brokers, SSH, APIs, live-device
commands, OpenAI runtime, voice runtime, push, merge, tag, or deployment flows.
"""

from __future__ import annotations

import html
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DAY = 106
TASK_NAME = "codex-agents-instruction-audit"
TITLE = "Day106 Codex AGENTS.md Instruction Compliance Audit"
PHASE_NAME = "Codex AGENTS.md Instruction Compliance Audit"
CREATED_AT = "2026-06-11T00:00:00+08:00"
AUDIT_TYPE = "REPORT_ONLY"
SCHEMA_VERSION = "day106.codex_agents_instruction_audit.v1"
REPORT_JSON = Path("reports") / "ai" / "day106_codex_agents_instruction_compliance_audit.json"
REPORT_HTML = Path("reports") / "ai" / "day106_codex_agents_instruction_compliance_audit.html"
AGENTS_FILE = Path("AGENTS.md")

PASS_RECOMMENDATION = "AGENTS_INSTRUCTION_CONTRACT_ACCEPTABLE_FOR_REVIEW_ONLY_CODEX_WORK"
MISSING_RECOMMENDATION = "AGENTS_INSTRUCTION_CONTRACT_MISSING"
RISK_RECOMMENDATION = "AGENTS_INSTRUCTION_CONTRACT_REJECTED_FOR_SAFETY_RISK"
HARDENING_RECOMMENDATION = "AGENTS_INSTRUCTION_CONTRACT_NEEDS_HARDENING_BEFORE_REUSE"

FORBIDDEN_RUNTIME_FLAGS = {
    "live_execution_allowed": False,
    "ssh_allowed": False,
    "device_connection_allowed": False,
    "config_mutation_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
    "push_allowed_without_user_approval": False,
    "merge_allowed_without_user_approval": False,
    "tag_allowed_without_user_approval": False,
}

GOVERNANCE_POLICY = {
    "codex_may_read_agents_md": True,
    "codex_may_audit_agents_md": True,
    "codex_may_report_findings_and_proposed_changes": True,
    "codex_must_not_modify_agents_md": True,
    "codex_must_not_stage_agents_md": True,
    "codex_must_not_commit_agents_md": True,
    "audit_modifies_agents_md": False,
    "audit_stages_agents_md": False,
    "audit_commits_agents_md": False,
}

PROPOSED_HARDENING_TEXT = {
    "D106-C01": "Document the repository purpose and review-only network automation lab scope.",
    "D106-C02": "Document the safe development workflow and keep changes focused.",
    "D106-C03": "Before considering work complete, run `python -m pytest` and `python network_lab.py --task report-index`.",
    "D106-C04": "If the task has a dedicated runner, also run `python network_lab.py --task <task-name>`.",
    "D106-C05": "Do not perform live device access unless a future task explicitly approves a separate safety gate.",
    "D106-C06": "Do not use SSH or real network-device commands unless explicitly approved by a future safety gate.",
    "D106-C07": "Do not execute configuration-changing commands.",
    "D106-C08": "Dry-run, mock-only, report-only, documentation-only, and design-only tasks must remain non-executing.",
    "D106-C09": "Do not add secrets, credentials, tokens, private local memory, private paths, or personal environment details.",
    "D106-C10": "Do not add OpenAI API calls, external AI runtime, voice input, speech-to-text, text-to-speech, microphone, or cloud execution unless a future task explicitly approves a separate safety gate.",
    "D106-C11": "Do not push, merge, tag, deploy, or publish changes without explicit user approval.",
    "D106-C12": "Work is done only when required source, test, docs, report evidence, and validation are complete without weakening safety gates.",
}

REQUIRED_CHECKS = [
    {
        "id": "D106-C01",
        "name": "Repository purpose",
        "status_field": "repo_guidance_status",
        "required": ["repository", "network automation lab"],
    },
    {
        "id": "D106-C02",
        "name": "Practical development guidance",
        "status_field": "repo_guidance_status",
        "required": ["git workflow", "keep changes focused"],
    },
    {
        "id": "D106-C03",
        "name": "Validation commands",
        "status_field": "validation_guidance_status",
        "required": ["python -m pytest", "python network_lab.py --task report-index"],
    },
    {
        "id": "D106-C04",
        "name": "Dedicated runner guidance",
        "status_field": "validation_guidance_status",
        "required": ["python network_lab.py --task <task-name>"],
    },
    {
        "id": "D106-C05",
        "name": "No live device access",
        "status_field": "safety_boundary_status",
        "required": ["do not perform live device access"],
    },
    {
        "id": "D106-C06",
        "name": "No SSH or real network-device commands",
        "status_field": "safety_boundary_status",
        "required": ["do not use ssh", "real network-device commands"],
    },
    {
        "id": "D106-C07",
        "name": "No configuration mutation",
        "status_field": "safety_boundary_status",
        "required": ["do not execute configuration-changing commands"],
    },
    {
        "id": "D106-C08",
        "name": "Review-only default and safety gates",
        "status_field": "instruction_contract_status",
        "required": ["report-only", "safety gates", "no-execution proof"],
    },
    {
        "id": "D106-C09",
        "name": "No secrets or private memory",
        "status_field": "secrets_exposure_status",
        "required": ["do not add secrets", "private local memory"],
    },
    {
        "id": "D106-C10",
        "name": "No OpenAI API or voice runtime by default",
        "status_field": "safety_boundary_status",
        "required": ["do not add openai api", "voice input"],
    },
    {
        "id": "D106-C11",
        "name": "No push, merge, or tag without explicit approval",
        "status_field": "instruction_contract_status",
        "required": ["do not push", "merge", "tag", "explicit user approval"],
    },
    {
        "id": "D106-C12",
        "name": "Done criteria",
        "status_field": "done_criteria_status",
        "required": ["done criteria", "validation commands", "no safety gate"],
    },
]

RISK_PATTERNS = [
    ("live_execution", re.compile(r"\b(connect|execute|run|perform)\b.*\b(live|device|router|switch)\b")),
    ("ssh", re.compile(r"\b(use|run|open|connect)\b.*\bssh\b")),
    ("config_mutation", re.compile(r"\b(apply|change|modify|write|reset|reboot|disable|enable|remove)\b.*\b(config|router|switch|interface|firewall|nat|vrrp)\b")),
    ("openai_api", re.compile(r"\b(openai api|external ai runtime|cloud execution)\b")),
    ("voice_runtime", re.compile(r"\b(voice runtime|microphone|speech-to-text|text-to-speech)\b")),
    (
        "git_publication",
        re.compile(
            r"\b(always|automatically|auto|may|can|should|allow|allowed)\b.*\b(push|merge|tag|deploy|publish)\b"
            r"|\b(push|merge|tag|deploy|publish)\b.*\b(without approval|without user approval)\b"
        ),
    ),
]

SECRET_VALUE_PATTERNS = [
    re.compile(r"\b[a-z0-9_-]*(api[_-]?key|token|password|secret|private[_-]?key)[a-z0-9_-]*\b\s*[:=]\s*['\"]?[a-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
]

SAFE_NEGATIONS = (
    "do not",
    "does not",
    "must not",
    "should not",
    "not allowed",
    "without explicit",
    "unless explicitly",
    "unless a future task explicitly approves",
    "before any",
    "no ",
)


def build_codex_agents_instruction_audit_report(project_root: Path = Path(".")) -> Dict[str, Any]:
    agents_path = Path(project_root) / AGENTS_FILE
    agents_file_found = agents_path.is_file()
    text = agents_path.read_text(encoding="utf-8") if agents_file_found else ""
    normalized = normalize_text(text)

    check_results = build_check_results(normalized, agents_file_found)
    risk_findings = build_risk_findings(text)
    secret_findings = build_secret_findings(text)
    status_fields = build_status_fields(check_results, risk_findings, secret_findings)
    overall_status, final_recommendation = decide_overall_status(
        agents_file_found,
        check_results,
        risk_findings,
        secret_findings,
    )

    report: Dict[str, Any] = {
        "day": DAY,
        "day_id": "Day106",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "overall_status": overall_status,
        "status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "agends_file_expected": True,
        "agents_file_expected": True,
        "agents_file_found": agents_file_found,
        "agents_file_path": AGENTS_FILE.as_posix(),
        **status_fields,
        **FORBIDDEN_RUNTIME_FLAGS,
        **GOVERNANCE_POLICY,
        "agents_governance_policy": deepcopy(GOVERNANCE_POLICY),
        "execution_proof": {
            "adapters_invoked": False,
            "brokers_invoked": False,
            "runners_invoked": False,
            "ssh_attempted": False,
            "network_calls_attempted": False,
            "openai_runtime_attempted": False,
            "voice_runtime_attempted": False,
            "git_push_merge_tag_attempted": False,
        },
        "audit_checks": check_results,
        "risk_findings": risk_findings,
        "secret_findings": secret_findings,
        "proposed_agents_md_changes": build_proposed_agents_md_changes(check_results),
        "missing_required_checks": [
            check["id"] for check in check_results if check["status"] != "PASS"
        ],
        "summary": build_summary(check_results, risk_findings, secret_findings),
        "final_recommendation": final_recommendation,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_codex_agents_instruction_audit_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors and report["overall_status"] == "PASS":
        report["overall_status"] = "FAIL"
        report["status"] = "FAIL"
        report["reviewer_status"] = "REVIEW_REQUIRED"
        report["final_recommendation"] = RISK_RECOMMENDATION
    return report


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def build_check_results(normalized: str, agents_file_found: bool) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for check in REQUIRED_CHECKS:
        missing = [phrase for phrase in check["required"] if phrase.lower() not in normalized]
        status = "PASS" if agents_file_found and not missing else "WARN"
        if not agents_file_found:
            status = "FAIL"
        results.append(
            {
                "id": check["id"],
                "name": check["name"],
                "status": status,
                "status_field": check["status_field"],
                "required_phrases": list(check["required"]),
                "missing_phrases": missing,
            }
        )
    return results


def build_risk_findings(text: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        lowered = line.lower()
        if not line or is_negated_safety_line(lowered):
            continue
        for risk_id, pattern in RISK_PATTERNS:
            if pattern.search(lowered):
                findings.append(
                    {
                        "risk_id": risk_id,
                        "line": str(line_number),
                        "evidence": line[:180],
                    }
                )
    return findings


def build_secret_findings(text: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if is_negated_safety_line(line.lower()):
            continue
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(line):
                findings.append(
                    {
                        "risk_id": "secret_literal",
                        "line": str(line_number),
                        "evidence": "<redacted-secret-like-value>",
                    }
                )
    return findings


def is_negated_safety_line(lowered_line: str) -> bool:
    return any(marker in lowered_line for marker in SAFE_NEGATIONS)


def build_status_fields(
    check_results: List[Dict[str, Any]],
    risk_findings: List[Dict[str, str]],
    secret_findings: List[Dict[str, str]],
) -> Dict[str, str]:
    grouped = {
        "instruction_contract_status": "PASS",
        "safety_boundary_status": "PASS",
        "secrets_exposure_status": "PASS",
        "repo_guidance_status": "PASS",
        "validation_guidance_status": "PASS",
        "done_criteria_status": "PASS",
    }
    for status_field in grouped:
        relevant = [check["status"] for check in check_results if check["status_field"] == status_field]
        if any(status == "FAIL" for status in relevant):
            grouped[status_field] = "FAIL"
        elif any(status == "WARN" for status in relevant):
            grouped[status_field] = "WARN"
    if risk_findings:
        grouped["instruction_contract_status"] = "FAIL"
        grouped["safety_boundary_status"] = "FAIL"
    if secret_findings:
        grouped["secrets_exposure_status"] = "FAIL"
    return grouped


def decide_overall_status(
    agents_file_found: bool,
    check_results: List[Dict[str, Any]],
    risk_findings: List[Dict[str, str]],
    secret_findings: List[Dict[str, str]],
) -> Tuple[str, str]:
    if not agents_file_found:
        return "FAIL", MISSING_RECOMMENDATION
    if risk_findings or secret_findings:
        return "FAIL", RISK_RECOMMENDATION
    if all(check["status"] == "PASS" for check in check_results):
        return "PASS", PASS_RECOMMENDATION
    return "WARN", HARDENING_RECOMMENDATION


def build_summary(
    check_results: List[Dict[str, Any]],
    risk_findings: List[Dict[str, str]],
    secret_findings: List[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "total_checks": len(check_results),
        "passed_checks": sum(1 for check in check_results if check["status"] == "PASS"),
        "warn_checks": sum(1 for check in check_results if check["status"] == "WARN"),
        "failed_checks": sum(1 for check in check_results if check["status"] == "FAIL"),
        "risk_findings": len(risk_findings),
        "secret_findings": len(secret_findings),
        "report_only": True,
    }


def validate_codex_agents_instruction_audit_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected_values = {
        "day": DAY,
        "task": TASK_NAME,
        "phase_name": PHASE_NAME,
        "created_at": CREATED_AT,
        "audit_type": AUDIT_TYPE,
        "agends_file_expected": True,
        "agents_file_expected": True,
    }
    for key, expected in expected_values.items():
        if report.get(key) != expected:
            errors.append(f"{key} must be {json.dumps(expected)}.")
    for key, expected in FORBIDDEN_RUNTIME_FLAGS.items():
        if report.get(key) is not expected:
            errors.append(f"{key} must be {json.dumps(expected)}.")
    for key, expected in GOVERNANCE_POLICY.items():
        if report.get(key) is not expected:
            errors.append(f"{key} must be {json.dumps(expected)}.")
        if report.get("agents_governance_policy", {}).get(key) is not expected:
            errors.append(f"agents_governance_policy.{key} must be {json.dumps(expected)}.")
    execution_proof = report.get("execution_proof", {})
    for key, value in execution_proof.items():
        if value is not False:
            errors.append(f"execution_proof.{key} must be false.")
    if not report.get("audit_checks"):
        errors.append("audit_checks must be non-empty.")
    if report.get("overall_status") == "PASS" and report.get("final_recommendation") != PASS_RECOMMENDATION:
        errors.append("PASS reports must use the accepted final recommendation.")
    return errors


def build_proposed_agents_md_changes(check_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    proposals: List[Dict[str, str]] = []
    for check in check_results:
        if check["status"] == "PASS":
            continue
        proposals.append(
            {
                "check_id": str(check["id"]),
                "reason": "AGENTS.md hardening proposal only; Day106 must not modify, stage, or commit AGENTS.md.",
                "proposed_wording": PROPOSED_HARDENING_TEXT[str(check["id"])],
            }
        )
    return proposals


def write_codex_agents_instruction_audit_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_codex_agents_instruction_audit_report(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_codex_agents_instruction_audit_html(safe_report, html_path)
    return json_path, html_path


def write_codex_agents_instruction_audit_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    check_rows = build_table_rows(
        (
            (
                check["id"],
                check["name"],
                check["status"],
                ", ".join(check["missing_phrases"]) or "none",
            )
            for check in report["audit_checks"]
        )
    )
    risk_rows = build_table_rows(
        (
            (finding["risk_id"], finding["line"], finding["evidence"])
            for finding in report["risk_findings"]
        ),
        empty_columns=3,
    )
    proposal_rows = build_table_rows(
        (
            (proposal["check_id"], proposal["reason"], proposal["proposed_wording"])
            for proposal in report["proposed_agents_md_changes"]
        ),
        empty_columns=3,
    )
    flag_rows = build_table_rows(
        (
            (name, json.dumps(report[name]))
            for name in FORBIDDEN_RUNTIME_FLAGS
        )
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .status {{ font-weight: bold; }}
  </style>
</head>
<body>
  <h1>{html.escape(TITLE)}</h1>
  <p><strong>Phase:</strong> {html.escape(report['phase_name'])}</p>
  <p><strong>Status:</strong> <span class="status">{html.escape(report['overall_status'])}</span></p>
  <p><strong>Audit type:</strong> <code>{html.escape(report['audit_type'])}</code></p>
  <p><strong>AGENTS.md found:</strong> {html.escape(json.dumps(report['agents_file_found']))}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <p><strong>Scope:</strong> Day106 reads repository instructions and writes reviewer evidence only. It does not connect to devices, use SSH, mutate configuration, call OpenAI APIs, use voice runtime, push, merge, tag, deploy, or publish.</p>
  <p><strong>AGENTS.md governance:</strong> Codex may read AGENTS.md, audit AGENTS.md, and report findings with proposed wording. During an AGENTS.md governance audit, Codex must not modify, stage, or commit AGENTS.md.</p>
  <h2>Instruction Checks</h2>
  <table>
    <thead><tr><th>ID</th><th>Check</th><th>Status</th><th>Missing Phrases</th></tr></thead>
    <tbody>{check_rows}</tbody>
  </table>
  <h2>Risk Findings</h2>
  <table>
    <thead><tr><th>Risk</th><th>Line</th><th>Evidence</th></tr></thead>
    <tbody>{risk_rows}</tbody>
  </table>
  <h2>Proposed AGENTS.md Wording</h2>
  <table>
    <thead><tr><th>Check</th><th>Reason</th><th>Proposed Wording</th></tr></thead>
    <tbody>{proposal_rows}</tbody>
  </table>
  <h2>Locked Runtime Flags</h2>
  <table>
    <thead><tr><th>Flag</th><th>Value</th></tr></thead>
    <tbody>{flag_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_table_rows(rows: Iterable[Iterable[Any]], empty_columns: int = 0) -> str:
    escaped_rows = [
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    ]
    if escaped_rows:
        return "".join(escaped_rows)
    if empty_columns:
        return "<tr>" + "".join("<td>none</td>" for _ in range(empty_columns)) + "</tr>"
    return ""
