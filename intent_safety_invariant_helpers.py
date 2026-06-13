"""Day124 shared safety invariant helpers.

This module is deterministic and review-only. It centralizes the common
dangerous capability flags used by AI intent, reviewer, provider, and dry-run
tasks without adding runtime, provider, broker, dashboard action, SSH, or live
device execution behavior.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


CREATED_AT = "2026-06-14T00:00:00+08:00"
DAY = "Day124"
DAY_NUMBER = 124
TASK_NAME = "safety-invariant-helper-review"
TITLE = "Safety Invariant Helper Consolidation"
FULL_TITLE = f"{DAY} {TITLE}"
SCHEMA_VERSION = "day124.safety_invariant_helper_consolidation.v1"
MODE = "REVIEW_ONLY"
OVERALL_STATUS = "PASS"
BLOCKED_STATUS = "BLOCKED"
REVIEWER_STATUS = "SAFETY_INVARIANT_HELPER_CONSOLIDATED"
FINAL_RECOMMENDATION = "KEEP_REVIEW_ONLY_SAFETY_INVARIANTS"
REPORT_JSON = Path("reports") / "lab-summary" / "day124_safety_invariant_helper_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day124_safety_invariant_helper_review.html"

DANGEROUS_CAPABILITY_FLAGS: Tuple[str, ...] = (
    "execution_allowed",
    "openai_api_allowed",
    "voice_input_allowed",
    "ssh_allowed",
    "live_device_allowed",
    "live_command_allowed",
    "runtime_unlock_supported",
    "dashboard_post_allowed",
    "broker_execution_allowed",
    "mapped_task_execution_allowed",
    "write_operation_allowed",
    "configuration_change_allowed",
)


def build_default_safety_invariants() -> Dict[str, bool]:
    """Return the shared review-only dangerous capability contract."""
    return {flag: False for flag in DANGEROUS_CAPABILITY_FLAGS}


def build_blocked_execution_capabilities() -> Dict[str, bool]:
    """Return blocked capability switches derived from the shared contract."""
    return {
        "openai_api": False,
        "voice_input": False,
        "ssh": False,
        "live_device_connection": False,
        "live_command_execution": False,
        "runtime_unlock": False,
        "dashboard_post_or_action_endpoint": False,
        "broker_execution": False,
        "mapped_task_execution": False,
        "write_operation": False,
        "configuration_change": False,
    }


def assert_review_only_safety_invariants(
    safety_invariants: Optional[Mapping[str, Any]] = None,
    blocked_capabilities: Optional[Mapping[str, Any]] = None,
    execution_allowed: Any = False,
    final_recommendation: str = FINAL_RECOMMENDATION,
) -> List[str]:
    """Validate the Day124 review-only invariant contract.

    The function returns deterministic validation errors instead of raising so
    report-only callers can preserve reviewer evidence in the generated report.
    """
    invariants = dict(safety_invariants or build_default_safety_invariants())
    blocked = dict(blocked_capabilities or build_blocked_execution_capabilities())
    errors: List[str] = []

    for flag in DANGEROUS_CAPABILITY_FLAGS:
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")

    for capability, allowed in blocked.items():
        if allowed is not False:
            errors.append(f"blocked_capabilities.{capability} must be false.")

    if execution_allowed is not False:
        errors.append("execution_allowed must be false.")
    if final_recommendation != FINAL_RECOMMENDATION:
        errors.append(f"final_recommendation must be {json.dumps(FINAL_RECOMMENDATION)}.")
    return errors


def build_safety_invariant_helper_review() -> Dict[str, Any]:
    """Build the Day124 deterministic helper consolidation review report."""
    safety_invariants = build_default_safety_invariants()
    blocked_capabilities = build_blocked_execution_capabilities()
    validation_errors = assert_review_only_safety_invariants(
        safety_invariants=safety_invariants,
        blocked_capabilities=blocked_capabilities,
        execution_allowed=False,
        final_recommendation=FINAL_RECOMMENDATION,
    )
    false_flag_count = sum(1 for value in safety_invariants.values() if value is False)
    blocked_capability_count = sum(1 for value in blocked_capabilities.values() if value is False)
    overall_status = OVERALL_STATUS if not validation_errors else BLOCKED_STATUS

    return {
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "created_at": CREATED_AT,
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "overall_status": overall_status,
        "status": overall_status,
        "reviewer_status": REVIEWER_STATUS if not validation_errors else "SAFETY_INVARIANT_HELPER_BLOCKED",
        "execution_allowed": False,
        "final_recommendation": FINAL_RECOMMENDATION,
        "safety_invariants": safety_invariants,
        "blocked_capabilities": blocked_capabilities,
        "helper_contract": {
            "module": "intent_safety_invariant_helpers.py",
            "default_builder": "build_default_safety_invariants",
            "blocked_capability_builder": "build_blocked_execution_capabilities",
            "validator": "assert_review_only_safety_invariants",
            "review_builder": "build_safety_invariant_helper_review",
            "contract_scope": "AI intent, reviewer, provider, dry-run, and report-only tasks",
            "deterministic": True,
            "review_only": True,
            "report_only": True,
            "runtime_provider_enabled": False,
            "execution_unlock_supported": False,
            "dangerous_flag_count": len(DANGEROUS_CAPABILITY_FLAGS),
            "dangerous_false_count": false_flag_count,
            "blocked_capability_count": blocked_capability_count,
        },
        "source_evidence": [
            {
                "source": "AGENTS.md",
                "evidence": "Project safety rules require dry-run, mock-only, report-only, documentation-only, and design-only tasks to remain non-executing.",
            },
            {
                "source": "Day120 task registry extraction",
                "evidence": "Task registration remains metadata and dispatch naming only.",
            },
            {
                "source": "Day121 CLI dispatch responsibility split",
                "evidence": "CLI routing remains thin and does not introduce execution capability.",
            },
            {
                "source": "Day122 report-index responsibility split",
                "evidence": "Report index scans and renders local files only.",
            },
            {
                "source": "Day123 safety boundary regression matrix",
                "evidence": "Safety-critical mock, review-only, report-only, dry-run-only, fake-adapter-only, locked, and disabled surfaces remain non-executing.",
            },
        ],
        "reviewer_notes": [
            "Day124 consolidates common dangerous capability flags into one reusable helper contract.",
            "The helper is deterministic and does not read secrets, local private configuration, network devices, or external services.",
            "All OpenAI API, voice input, SSH, live device, live command, runtime unlock, dashboard POST/action, broker, mapped task, write, and configuration change flags remain false.",
            "The final recommendation keeps the project in review-only safety invariant mode.",
        ],
        "dangerous_flag_summary": {
            "total_flags": len(DANGEROUS_CAPABILITY_FLAGS),
            "false_flags": false_flag_count,
            "unsafe_true_flags": len(DANGEROUS_CAPABILITY_FLAGS) - false_flag_count,
            "blocked_capabilities": len(blocked_capabilities),
            "unblocked_capabilities": len(blocked_capabilities) - blocked_capability_count,
        },
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": validation_errors,
    }


def write_safety_invariant_helper_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_safety_invariant_helper_review()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_safety_invariant_helper_review_html(safe_report, html_path)
    return json_path, html_path


def write_safety_invariant_helper_review_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    invariant_rows = _table_rows(report["safety_invariants"].items())
    blocked_rows = _table_rows(report["blocked_capabilities"].items())
    source_rows = _table_rows((item["source"], item["evidence"]) for item in report["source_evidence"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['full_title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    .pass {{ color: #116329; font-weight: bold; }}
    .blocked {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['full_title'])}</h1>
  <p><strong>Result:</strong> <span class="{html.escape(report['overall_status'].lower())}">{html.escape(report['overall_status'])}</span> / {html.escape(report['mode'])}</p>
  <p><strong>Reviewer status:</strong> <code>{html.escape(report['reviewer_status'])}</code></p>
  <p><strong>Final recommendation:</strong> <code>{html.escape(report['final_recommendation'])}</code></p>
  <p>Helper consolidation completed. All execution-related flags remain false, the final recommendation remains review-only, and no runtime or provider capability was enabled.</p>

  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Flag</th><th>Allowed</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>

  <h2>Blocked Capabilities</h2>
  <table>
    <thead><tr><th>Capability</th><th>Allowed</th></tr></thead>
    <tbody>{blocked_rows}</tbody>
  </table>

  <h2>Source Evidence</h2>
  <table>
    <thead><tr><th>Source</th><th>Evidence</th></tr></thead>
    <tbody>{source_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, list):
        return "; ".join(str(item) for item in value) or "none"
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )


def main() -> int:
    report = build_safety_invariant_helper_review()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
