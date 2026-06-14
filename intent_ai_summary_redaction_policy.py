"""Day130 AI summary redaction and no-secret policy.

This module is deterministic, local-only, and review-only. It checks reviewer
summary text for obvious secret-like values and renders redacted evidence. It
does not call OpenAI, configure a provider, make AI decisions, bind audit
trails, infer reviewer approval, execute tools, or unlock any next phase.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Pattern, Tuple


DAY = "Day130"
DAY_NUMBER = 130
TASK_NAME = "ai-summary-redaction-and-no-secret-policy"
TITLE = "AI Summary Redaction and No-Secret Policy"
FULL_TITLE = f"{DAY} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
POLICY_STATUS = "NO_SECRET_POLICY_ENFORCED"
REDACTION_STATUS = "REDACTION_REVIEW_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day130_ai_summary_redaction_and_no_secret_policy.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day130_ai_summary_redaction_and_no_secret_policy.html"
FIXTURE_PATH = Path("fixtures") / "day130_ai_summary_redaction_policy.example.json"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day130_ai_summary_redaction_and_no_secret_policy.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day130_ai_summary_redaction_and_no_secret_policy.md"

REDACTION_MARKERS: Tuple[str, ...] = (
    "[REDACTED:API_KEY]",
    "[REDACTED:BEARER_TOKEN]",
    "[REDACTED:ENV_SECRET]",
    "[REDACTED:PASSWORD]",
    "[REDACTED:PRIVATE_KEY_BLOCK]",
    "[REDACTED:SSH_PUBLIC_KEY]",
    "[REDACTED:TOKEN]",
)


@dataclass(frozen=True)
class SecretPattern:
    label: str
    pattern: Pattern[str]
    replacement: str


SECRET_PATTERNS: Tuple[SecretPattern, ...] = (
    SecretPattern(
        "private_key_block",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        "[REDACTED:PRIVATE_KEY_BLOCK]",
    ),
    SecretPattern(
        "env_secret_assignment",
        re.compile(
            r"(\b[A-Z][A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[A-Z0-9_]*\s*=\s*)([^\s\"'<>]+)"
        ),
        r"\1[REDACTED:ENV_SECRET]",
    ),
    SecretPattern(
        "bearer_token",
        re.compile(r"\bBearer\s+([A-Za-z0-9._~+/=-]{16,})"),
        "Bearer [REDACTED:BEARER_TOKEN]",
    ),
    SecretPattern(
        "ssh_public_key",
        re.compile(r"\b(ssh-(?:rsa|ed25519))\s+([A-Za-z0-9+/=]{20,})(?:\s+\S+)?"),
        r"\1 [REDACTED:SSH_PUBLIC_KEY]",
    ),
    SecretPattern(
        "openai_api_key",
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "[REDACTED:API_KEY]",
    ),
    SecretPattern(
        "api_key_assignment",
        re.compile(r"(\b(?:api[_ -]?key|openai[_ -]?api[_ -]?key)\s*[:=]\s*)([^\s\"'<>]+)", re.IGNORECASE),
        r"\1[REDACTED:API_KEY]",
    ),
    SecretPattern(
        "password_assignment",
        re.compile(r"(\b(?:password|passwd|pwd)\s*[:=]\s*)([^\s\"'<>]+)", re.IGNORECASE),
        r"\1[REDACTED:PASSWORD]",
    ),
    SecretPattern(
        "token_assignment",
        re.compile(r"(\b(?:access[_ -]?token|refresh[_ -]?token|token|secret)\s*[:=]\s*)([^\s\"'<>]+)", re.IGNORECASE),
        r"\1[REDACTED:TOKEN]",
    ),
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "day",
    "task",
    "policy_status",
    "redaction_status",
    "review_only",
    "execution_enabled",
    "provider_enabled",
    "api_enabled",
    "openai_api_called",
    "ai_decision_made",
    "next_phase_allowed",
    "fixture_count",
    "redacted_count",
    "blocked_secret_like_count",
    "unsafe_flag_count",
)


def build_agents_md_pre_read_evidence(
    project_root: Path,
    agents_md_read_before_day130_work: bool = True,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_pre_read_result": "MISSING",
            "agents_md_read_before_day130_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": "AGENTS.md not found.",
            "agents_md_required_phrase_present": False,
        }
    except OSError as exc:
        return {
            "agents_md_pre_read_result": "READ_ERROR",
            "agents_md_read_before_day130_work": False,
            "agents_md_path": "AGENTS.md",
            "agents_md_read_error": str(exc),
            "agents_md_required_phrase_present": False,
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    passed = bool(agents_md_read_before_day130_work and required_phrase_present)
    return {
        "agents_md_pre_read_result": OVERALL_STATUS if passed else FAIL_STATUS,
        "agents_md_read_before_day130_work": passed,
        "agents_md_path": "AGENTS.md",
        "agents_md_read_error": "",
        "agents_md_required_phrase_present": required_phrase_present,
    }


def build_default_redaction_fixtures() -> List[Dict[str, Any]]:
    return [
        {
            "fixture_id": "day130-safe-reviewer-summary",
            "category": "safe_text",
            "input_text": "Reviewer summary: Day129 prompt contract remains report-only and has no live execution.",
            "expect_secret_like": False,
        },
        {
            "fixture_id": "day130-already-redacted-reviewer-summary",
            "category": "redacted_text",
            "input_text": "Reviewer summary: credential field is [REDACTED:TOKEN] and remains safe to display.",
            "expect_secret_like": False,
        },
        {
            "fixture_id": "day130-api-key-like-text",
            "category": "secret_like_text",
            "input_text": "Reviewer note includes api_key=day130_fake_api_key_value_000000000000.",
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-bearer-token-like-text",
            "category": "secret_like_text",
            "input_text": "Authorization header preview: Bearer day130.fake.bearer.token.value.000000",
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-password-like-text",
            "category": "secret_like_text",
            "input_text": "Operator note accidentally wrote password=day130_fake_password_value.",
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-private-key-block-like-text",
            "category": "secret_like_text",
            "input_text": (
                "Captured block:\n"
                "-----BEGIN PRIVATE KEY-----\n"
                "day130-fake-private-key-material-not-real\n"
                "-----END PRIVATE KEY-----"
            ),
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-ssh-key-like-text",
            "category": "secret_like_text",
            "input_text": "SSH public key sample: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDAY130FAKEKEY000000000 reviewer@example",
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-env-secret-like-text",
            "category": "secret_like_text",
            "input_text": "Environment preview: OPENAI_API_KEY=sk-day130-example-not-real-token-000000",
            "expect_secret_like": True,
        },
        {
            "fixture_id": "day130-token-like-text",
            "category": "secret_like_text",
            "input_text": "Summary metadata accidentally included access_token=day130_fake_access_token_000000.",
            "expect_secret_like": True,
        },
    ]


def load_redaction_fixtures(project_root: Path) -> List[Dict[str, Any]]:
    fixture_path = Path(project_root) / FIXTURE_PATH
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def redact_ai_summary_text(text: str) -> Dict[str, Any]:
    redacted_text = text
    findings: List[Dict[str, Any]] = []

    for secret_pattern in SECRET_PATTERNS:
        count = 0

        def replace_secret(_match: re.Match[str]) -> str:
            nonlocal count
            count += 1
            return secret_pattern.replacement

        redacted_text = secret_pattern.pattern.sub(replace_secret, redacted_text)
        if count:
            findings.append(
                {
                    "pattern": secret_pattern.label,
                    "count": count,
                    "redaction_applied": True,
                }
            )

    return {
        "secret_like_found": bool(findings),
        "redacted_text": redacted_text,
        "redacted_count": sum(int(item["count"]) for item in findings),
        "findings": findings,
    }


def evaluate_redaction_fixture(fixture: Mapping[str, Any]) -> Dict[str, Any]:
    result = redact_ai_summary_text(str(fixture.get("input_text", "")))
    post_redaction_scan = redact_ai_summary_text(str(result["redacted_text"]))
    return {
        "fixture_id": fixture.get("fixture_id", ""),
        "category": fixture.get("category", ""),
        "expect_secret_like": bool(fixture.get("expect_secret_like", False)),
        "secret_like_found": result["secret_like_found"],
        "redacted_count": result["redacted_count"],
        "finding_patterns": [item["pattern"] for item in result["findings"]],
        "redacted_text": result["redacted_text"],
        "post_redaction_secret_like_found": post_redaction_scan["secret_like_found"],
        "source_text_omitted_from_report": True,
    }


def build_ai_summary_redaction_policy_report(
    project_root: Path,
    agents_md_read_before_day130_work: bool = True,
    fixtures: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_read_before_day130_work=agents_md_read_before_day130_work,
    )
    fixture_rows = list(fixtures if fixtures is not None else load_redaction_fixtures(project_root))
    evaluations = [evaluate_redaction_fixture(fixture) for fixture in fixture_rows]
    unsafe_flags = {
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "openai_api_called": False,
        "ai_decision_made": False,
        "next_phase_allowed": False,
        "audit_trail_binding_enabled": False,
        "reviewer_approval_gate_enabled": False,
        "mock_provider_boundary_enabled": False,
        "ssh_enabled": False,
        "live_device_access_enabled": False,
        "network_calls_enabled": False,
    }

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "policy_status": POLICY_STATUS,
        "redaction_status": REDACTION_STATUS,
        "review_only": True,
        "local_only": True,
        "deterministic_only": True,
        "execution_enabled": False,
        "provider_enabled": False,
        "api_enabled": False,
        "openai_api_called": False,
        "ai_decision_made": False,
        "next_phase_allowed": False,
        "not_day131_audit_trail_binding": True,
        "not_day132_reviewer_approval_gate": True,
        "not_day133_mock_provider_boundary": True,
        "fixture_path": FIXTURE_PATH.as_posix(),
        "fixture_count": len(evaluations),
        "redacted_count": sum(int(item["redacted_count"]) for item in evaluations),
        "blocked_secret_like_count": sum(1 for item in evaluations if item["secret_like_found"]),
        "unsafe_flag_count": sum(1 for value in unsafe_flags.values() if value is not False),
        "redaction_markers": list(REDACTION_MARKERS),
        "pattern_count": len(SECRET_PATTERNS),
        "fixture_evaluations": evaluations,
        "unsafe_flags": unsafe_flags,
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_read_before_day130_work": agents_evidence["agents_md_read_before_day130_work"],
        "agents_md_path": agents_evidence["agents_md_path"],
        "agents_md_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    if report["overall_status"] != OVERALL_STATUS:
        report["policy_status"] = "NO_SECRET_POLICY_BLOCKED"
        report["redaction_status"] = "REDACTION_REVIEW_BLOCKED"
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("agents_md_pre_read_result") != OVERALL_STATUS:
        errors.append("AGENTS.md pre-read evidence did not pass.")
    if report.get("agents_md_read_before_day130_work") is not True:
        errors.append("AGENTS.md must be read before Day130 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    if report.get("day") != DAY:
        errors.append(f"day must be {DAY}.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("policy_status") != POLICY_STATUS:
        errors.append(f"policy_status must be {POLICY_STATUS}.")
    if report.get("redaction_status") != REDACTION_STATUS:
        errors.append(f"redaction_status must be {REDACTION_STATUS}.")
    for field in (
        "review_only",
        "local_only",
        "deterministic_only",
        "not_day131_audit_trail_binding",
        "not_day132_reviewer_approval_gate",
        "not_day133_mock_provider_boundary",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in (
        "execution_enabled",
        "provider_enabled",
        "api_enabled",
        "openai_api_called",
        "ai_decision_made",
        "next_phase_allowed",
    ):
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if report.get("unsafe_flag_count") != 0:
        errors.append("unsafe_flag_count must be 0.")
    if report.get("fixture_count", 0) < 3:
        errors.append("At least safe, redacted, and secret-like fixtures are required.")
    if report.get("blocked_secret_like_count", 0) < 1:
        errors.append("At least one secret-like fixture must be blocked/redacted.")

    categories = {item.get("category") for item in report.get("fixture_evaluations", [])}
    for category in ("safe_text", "redacted_text", "secret_like_text"):
        if category not in categories:
            errors.append(f"Missing fixture category: {category}.")

    for item in report.get("fixture_evaluations", []):
        if item.get("expect_secret_like") and item.get("secret_like_found") is not True:
            errors.append(f"{item.get('fixture_id')} expected secret-like content to be detected.")
        if not item.get("expect_secret_like") and item.get("secret_like_found") is not False:
            errors.append(f"{item.get('fixture_id')} should not be detected as secret-like.")
        if item.get("post_redaction_secret_like_found") is not False:
            errors.append(f"{item.get('fixture_id')} still has secret-like content after redaction.")

    return errors


def write_ai_summary_redaction_policy_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_summary_redaction_policy_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_summary_redaction_policy_html(safe_report, html_path)
    return json_path, html_path


def write_ai_summary_redaction_policy_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    boundary_rows = _table_rows(
        (
            ("not_day131_audit_trail_binding", report["not_day131_audit_trail_binding"]),
            ("not_day132_reviewer_approval_gate", report["not_day132_reviewer_approval_gate"]),
            ("not_day133_mock_provider_boundary", report["not_day133_mock_provider_boundary"]),
            ("local_only", report["local_only"]),
            ("deterministic_only", report["deterministic_only"]),
        )
    )
    fixture_rows = _table_rows(
        (
            (
                item["fixture_id"],
                item["category"],
                item["secret_like_found"],
                item["redacted_count"],
                ", ".join(item["finding_patterns"]) or "none",
                item["redacted_text"],
            )
            for item in report.get("fixture_evaluations", [])
        )
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
  <h2>Policy Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Future Scope Boundary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{boundary_rows}</tbody></table>
  <h2>Fixture Redaction Review</h2>
  <table><thead><tr><th>Fixture</th><th>Category</th><th>Secret-like Found</th><th>Redactions</th><th>Patterns</th><th>Redacted Text</th></tr></thead><tbody>{fixture_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_summary_redaction_policy(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_summary_redaction_policy_report(project_root)
    json_path, html_path = write_ai_summary_redaction_policy_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print("Safety: deterministic local redaction policy only; no execution, provider/API enablement, OpenAI API call, AI decision, reviewer approval gate, audit trail binding, mock provider boundary, SSH, network call, or next-phase unlock")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"not_day131_audit_trail_binding: {json.dumps(report['not_day131_audit_trail_binding'])}")
    print(f"not_day132_reviewer_approval_gate: {json.dumps(report['not_day132_reviewer_approval_gate'])}")
    print(f"not_day133_mock_provider_boundary: {json.dumps(report['not_day133_mock_provider_boundary'])}")
    print(f"local_only: {json.dumps(report['local_only'])}")
    print(f"deterministic_only: {json.dumps(report['deterministic_only'])}")
    print(f"fixture_path: {json.dumps(report['fixture_path'])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {POLICY_STATUS}; {REDACTION_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {report['policy_status']}; {report['redaction_status']}")
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
    report = build_ai_summary_redaction_policy_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
