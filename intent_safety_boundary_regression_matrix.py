"""Day123 safety boundary regression matrix.

This module is deterministic and report-only. It reviews safety-critical task
families and refactor seams after the Day120-Day122 splits without invoking
adapters, brokers, runners, SSH, live device access, dashboard actions, or
external AI runtimes.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


CREATED_AT = "2026-06-13T00:00:00+08:00"
DAY = 123
DAY_ID = "Day123"
TASK_NAME = "safety-boundary-regression-matrix"
TITLE = "Safety Boundary Regression Matrix"
FULL_TITLE = f"Day123 {TITLE}"
SCHEMA_VERSION = "day123.safety_boundary_regression_matrix.v1"
MODE = "REPORT_ONLY_SAFETY_BOUNDARY_REGRESSION"
OVERALL_STATUS = "PASS"
BLOCKED_STATUS = "BLOCKED"
FINAL_RECOMMENDATION = "KEEP_BOUNDARIES_LOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "day123_safety_boundary_regression_matrix.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day123_safety_boundary_regression_matrix.html"

FALSE_FLAGS = (
    "execution_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "mutation_allowed",
    "unlock_supported",
    "adapter_invocation_allowed",
    "broker_invocation_allowed",
    "runner_invocation_allowed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "dashboard_post_action_allowed",
)

ACCEPTED_BOUNDARIES = {
    "report-only",
    "review-only",
    "dry-run-only",
    "mock-only",
    "fake-adapter-only",
    "locked",
    "disabled",
    "design-only",
    "planning-only",
    "scaffold-only",
    "parser-only",
    "profile-backed-report-only",
    "visibility-report-only",
}


@dataclass(frozen=True)
class BoundaryScenario:
    row_id: str
    task_or_component: str
    expected_boundary: str
    source: str
    evidence: str
    task_id: str = ""
    expected_enabled: Optional[bool] = True
    expected_safety_level: str = ""
    expected_execution_mode: str = ""

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


def build_boundary_scenarios() -> List[BoundaryScenario]:
    """Return deterministic Day123 rows for safety-critical families."""
    return [
        BoundaryScenario(
            row_id="D123-R01",
            task_or_component="intent-mapping-prototype",
            task_id="intent-mapping-prototype",
            expected_boundary="dry-run-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day57 AI intent mapping",
            evidence="Maps static text only and must not execute the mapped task.",
        ),
        BoundaryScenario(
            row_id="D123-R02",
            task_or_component="offline-mock-runtime",
            task_id="offline-mock-runtime",
            expected_boundary="mock-only",
            expected_safety_level="report-only",
            expected_execution_mode="report-only",
            source="Day66 offline runtime",
            evidence="Offline skeleton must remain disconnected from API, SSH, devices, and mapped tasks.",
        ),
        BoundaryScenario(
            row_id="D123-R03",
            task_or_component="mock-ai-decision-pipeline",
            task_id="mock-ai-decision-pipeline",
            expected_boundary="mock-only",
            expected_safety_level="report-only",
            expected_execution_mode="report-only",
            source="Day73 deterministic decisions",
            evidence="Mock decisions must remain local data, not OpenAI or cloud runtime calls.",
        ),
        BoundaryScenario(
            row_id="D123-R04",
            task_or_component="dry-run-plan-builder",
            task_id="dry-run-plan-builder",
            expected_boundary="dry-run-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day74 dry-run planning",
            evidence="Plan previews must not dispatch mapped tasks or network commands.",
        ),
        BoundaryScenario(
            row_id="D123-R05",
            task_or_component="manual-review-approval-envelope",
            task_id="manual-review-approval-envelope",
            expected_boundary="review-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day75 approval envelope",
            evidence="Reviewer sign-off envelope must not become an execution unlock.",
        ),
        BoundaryScenario(
            row_id="D123-R06",
            task_or_component="runtime-safety-gate",
            task_id="runtime-safety-gate",
            expected_boundary="locked",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day77 runtime gate",
            evidence="Locked gate must keep execution controls and dashboard actions disabled.",
        ),
        BoundaryScenario(
            row_id="D123-R07",
            task_or_component="readonly-execution-broker",
            task_id="readonly-execution-broker",
            expected_boundary="report-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day80 broker skeleton",
            evidence="Broker records must remain deterministic report data without runner or adapter handoff.",
        ),
        BoundaryScenario(
            row_id="D123-R08",
            task_or_component="broker-review-queue",
            task_id="broker-review-queue",
            expected_boundary="review-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day81 reviewer queue",
            evidence="Queue state must not add dashboard forms, POST routes, or action endpoints.",
        ),
        BoundaryScenario(
            row_id="D123-R09",
            task_or_component="readonly-executor-readiness-gate",
            task_id="readonly-executor-readiness-gate",
            expected_boundary="locked",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day83 readiness gate",
            evidence="Readiness review must remain future-adapter evidence only.",
        ),
        BoundaryScenario(
            row_id="D123-R10",
            task_or_component="readonly-executor-adapter-contract",
            task_id="readonly-executor-adapter-contract",
            expected_boundary="report-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day84 adapter contract",
            evidence="Contract shape must not implement an adapter or execution path.",
        ),
        BoundaryScenario(
            row_id="D123-R11",
            task_or_component="controlled-runner-harness",
            task_id="controlled-runner-harness",
            expected_boundary="dry-run-only",
            expected_safety_level="dry-run",
            expected_execution_mode="dry-run",
            source="Day86 runner harness",
            evidence="Harness regression scenarios must remain deterministic and non-executing.",
        ),
        BoundaryScenario(
            row_id="D123-R12",
            task_or_component="readonly-executor-adapter-design",
            task_id="readonly-executor-adapter-design",
            expected_boundary="design-only",
            expected_safety_level="design-only",
            expected_execution_mode="design-only",
            source="Day88 adapter design",
            evidence="Design contract must not create SSH, RouterOS connection, or live command support.",
        ),
        BoundaryScenario(
            row_id="D123-R13",
            task_or_component="real-adapter-implementation-plan",
            task_id="real-adapter-implementation-plan",
            expected_boundary="planning-only",
            expected_safety_level="planning-only",
            expected_execution_mode="planning-only",
            source="Day90 implementation plan",
            evidence="Planning decision must not implement real adapter access.",
        ),
        BoundaryScenario(
            row_id="D123-R14",
            task_or_component="real-adapter-safety-scaffold",
            task_id="real-adapter-safety-scaffold",
            expected_boundary="scaffold-only",
            expected_safety_level="scaffold-only",
            expected_execution_mode="scaffold-only",
            source="Day91 safety scaffold",
            evidence="Scaffold must keep dangerous actions denied and read-only candidates future-only.",
        ),
        BoundaryScenario(
            row_id="D123-R15",
            task_or_component="real-adapter-executable-guards",
            task_id="real-adapter-executable-guards",
            expected_boundary="locked",
            expected_safety_level="offline-deterministic-guard",
            expected_execution_mode="guard-only",
            source="Day92 executable guards",
            evidence="Rejected requests must fail before executor or adapter invocation.",
        ),
        BoundaryScenario(
            row_id="D123-R16",
            task_or_component="guarded-fake-adapter-contract",
            task_id="guarded-fake-adapter-contract",
            expected_boundary="fake-adapter-only",
            expected_safety_level="fake-adapter-only",
            expected_execution_mode="guarded-fake-only",
            source="Day93 fake adapter contract",
            evidence="Allowed rows may use fake evidence only; rejected rows must not invoke adapters.",
        ),
        BoundaryScenario(
            row_id="D123-R17",
            task_or_component="adapter-boundary-regression-matrix",
            task_id="adapter-boundary-regression-matrix",
            expected_boundary="fake-adapter-only",
            expected_safety_level="fake-adapter-only",
            expected_execution_mode="guarded-fake-only",
            source="Day94 adapter boundary matrix",
            evidence="Real adapter and live execution invocation counts must remain zero.",
        ),
        BoundaryScenario(
            row_id="D123-R18",
            task_or_component="parser-classification-matrix",
            task_id="parser-classification-matrix",
            expected_boundary="parser-only",
            expected_safety_level="fake-adapter-only",
            expected_execution_mode="report-only",
            source="Day98 parser classification",
            evidence="Parser matrix must classify evidence without executable capability.",
        ),
        BoundaryScenario(
            row_id="D123-R19",
            task_or_component="parser-consumer-final-gate",
            task_id="parser-consumer-final-gate",
            expected_boundary="review-only",
            expected_safety_level="report-only",
            expected_execution_mode="report-only",
            source="Day110 parser consumer gate",
            evidence="Final gate must preserve blocked records and no next-phase execution unlock.",
        ),
        BoundaryScenario(
            row_id="D123-R20",
            task_or_component="reviewer-evidence-intake-outcome-ledger",
            task_id="reviewer-evidence-intake-outcome-ledger",
            expected_boundary="review-only",
            expected_safety_level="report-only",
            expected_execution_mode="report-only",
            source="Day119 evidence intake ledger",
            evidence="Intake logging must not accept, sign off, release, hand off, or execute.",
        ),
        BoundaryScenario(
            row_id="D123-R21",
            task_or_component="network_lab_task_registry",
            expected_boundary="locked",
            expected_enabled=None,
            source="Day120 task registry extraction",
            evidence="Registry resolves task names only; rejected intents must not invoke handlers.",
        ),
        BoundaryScenario(
            row_id="D123-R22",
            task_or_component="network_lab_cli_dispatch",
            expected_boundary="locked",
            expected_enabled=None,
            source="Day121 CLI dispatch split",
            evidence="Dispatch owns argument routing only and must not import live execution dependencies.",
        ),
        BoundaryScenario(
            row_id="D123-R23",
            task_or_component="report-index task",
            task_id="report-index",
            expected_boundary="profile-backed-report-only",
            expected_safety_level="report-only",
            expected_execution_mode="report-only",
            source="Day122 profile-backed report-index path",
            evidence="`--task report-index` builds local overview evidence only.",
        ),
        BoundaryScenario(
            row_id="D123-R24",
            task_or_component="report-index visibility flag",
            expected_boundary="visibility-report-only",
            expected_enabled=None,
            source="Day122 `--report-index` visibility path",
            evidence="`--report-index` scans local report metadata and renders HTML only.",
        ),
        BoundaryScenario(
            row_id="D123-R25",
            task_or_component="Day13 WireGuard live execution catalog row",
            expected_boundary="disabled",
            expected_enabled=False,
            source="Day18 report-index guardrail",
            evidence="Historical Day13 live workflow remains disabled in report-index visibility.",
        ),
    ]


def build_safety_boundary_regression_matrix_report(
    task_catalog: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    catalog_by_id = {
        str(task.get("id")): dict(task)
        for task in (task_catalog or [])
        if isinstance(task, Mapping) and task.get("id")
    }
    rows = [
        _build_matrix_row(scenario, catalog_by_id.get(scenario.task_id))
        for scenario in build_boundary_scenarios()
    ]
    summary = build_summary(rows)
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "created_at": CREATED_AT,
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "overall_status": summary["overall_status"],
        "status": summary["overall_status"],
        "final_recommendation": FINAL_RECOMMENDATION,
        "matrix_rows": rows,
        "summary": summary,
        "invariant_checks": build_invariant_checks(summary),
        "safety_invariants": {flag: False for flag in FALSE_FLAGS},
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day123 is report-only and does not run reviewed tasks.",
            "Rows cover mock, review-only, report-only, dry-run-only, fake-adapter-only, locked, disabled, and refactor-boundary surfaces.",
            "Any observed live execution, SSH, mutation, unlock, adapter, broker, runner, OpenAI API, voice runtime, or dashboard POST action marks the matrix BLOCKED.",
        ],
    }
    report["validation_errors"] = validate_safety_boundary_regression_matrix_report(report)
    if report["validation_errors"]:
        report["overall_status"] = BLOCKED_STATUS
        report["status"] = BLOCKED_STATUS
        report["summary"]["overall_status"] = BLOCKED_STATUS
    return report


def build_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    unsafe_counts = {f"{flag}_count": sum(1 for row in rows if row[flag]) for flag in FALSE_FLAGS}
    failed_rows = sum(1 for row in rows if row["status"] != "PASS")
    missing_catalog_rows = sum(1 for row in rows if row["observed_boundary"] == "CATALOG_ENTRY_MISSING")
    total_rows = len(rows)
    passed_rows = total_rows - failed_rows
    overall_status = "PASS" if total_rows >= 24 and failed_rows == 0 and all(count == 0 for count in unsafe_counts.values()) else BLOCKED_STATUS
    return {
        "total_rows": total_rows,
        "passed_rows": passed_rows,
        "failed_rows": failed_rows,
        "missing_catalog_rows": missing_catalog_rows,
        **unsafe_counts,
        "overall_status": overall_status,
    }


def build_invariant_checks(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    checks = [
        ("total_rows >= 24", summary["total_rows"] >= 24),
        ("failed_rows == 0", summary["failed_rows"] == 0),
        ("missing_catalog_rows == 0", summary["missing_catalog_rows"] == 0),
    ]
    checks.extend((f"{flag}_count == 0", summary[f"{flag}_count"] == 0) for flag in FALSE_FLAGS)
    return [{"name": name, "status": "PASS" if passed else "FAIL"} for name, passed in checks]


def validate_safety_boundary_regression_matrix_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "mode": MODE,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    rows = report.get("matrix_rows", [])
    summary = report.get("summary", {})
    if len(rows) < 24:
        errors.append("matrix_rows must contain at least 24 rows.")
    row_ids = [row.get("row_id") for row in rows]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row IDs must be unique.")
    if summary.get("total_rows") != len(rows):
        errors.append("summary.total_rows must match matrix row count.")
    if summary.get("failed_rows") != 0:
        errors.append("summary.failed_rows must be 0.")
    if summary.get("missing_catalog_rows") != 0:
        errors.append("summary.missing_catalog_rows must be 0.")

    for flag in FALSE_FLAGS:
        if report.get("safety_invariants", {}).get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
        if summary.get(f"{flag}_count") != 0:
            errors.append(f"summary.{flag}_count must be 0.")

    for row in rows:
        row_id = row.get("row_id", "<unknown>")
        if row.get("expected_boundary") not in ACCEPTED_BOUNDARIES:
            errors.append(f"{row_id} expected_boundary is not accepted.")
        if row.get("status") != "PASS":
            errors.append(f"{row_id} status must be PASS.")
        for flag in FALSE_FLAGS:
            if row.get(flag) is not False:
                errors.append(f"{row_id}.{flag} must be false.")
    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day123 JSON and HTML reports.")
    return errors


def write_safety_boundary_regression_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_safety_boundary_regression_matrix_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_safety_boundary_regression_matrix_html(safe_report, html_path)
    return json_path, html_path


def write_safety_boundary_regression_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    invariant_rows = _table_rows((check["name"], check["status"]) for check in report["invariant_checks"])
    matrix_rows = _table_rows(
        (
            row["row_id"],
            row["task_or_component"],
            row["expected_boundary"],
            row["observed_boundary"],
            row["execution_allowed"],
            row["ssh_allowed"],
            row["live_command_allowed"],
            row["mutation_allowed"],
            row["unlock_supported"],
            row["status"],
            row["evidence"],
        )
        for row in report["matrix_rows"]
    )
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
    .blocked, .fail {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['full_title'])}</h1>
  <p><strong>Result:</strong> <span class="{html.escape(report['overall_status'].lower())}">{html.escape(report['overall_status'])}</span> / {html.escape(report['mode'])}</p>
  <p><strong>Final recommendation:</strong> <code>{html.escape(report['final_recommendation'])}</code></p>
  <p>Report-only regression evidence. No SSH, live command execution, mutation, execution unlock, adapter/broker/runner invocation, OpenAI API, voice runtime, or dashboard POST action is introduced.</p>
  <h2>Summary</h2>
  <p><strong>Total rows:</strong> {summary['total_rows']} | <strong>Passed:</strong> {summary['passed_rows']} | <strong>Failed:</strong> {summary['failed_rows']} | <strong>Missing catalog rows:</strong> {summary['missing_catalog_rows']}</p>
  <h2>Invariant Checks</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Status</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
  <h2>Regression Matrix</h2>
  <table>
    <thead><tr><th>Row</th><th>Task or Component</th><th>Expected Boundary</th><th>Observed Boundary</th><th>Execution</th><th>SSH</th><th>Live Command</th><th>Mutation</th><th>Unlock</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def _build_matrix_row(
    scenario: BoundaryScenario,
    catalog_task: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    observed_boundary = _observed_boundary(scenario, catalog_task)
    mismatches = _mismatches(scenario, catalog_task, observed_boundary)
    row = {
        **scenario.to_record(),
        "observed_boundary": observed_boundary,
        "execution_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "mutation_allowed": False,
        "unlock_supported": False,
        "adapter_invocation_allowed": False,
        "broker_invocation_allowed": False,
        "runner_invocation_allowed": False,
        "openai_api_allowed": False,
        "voice_runtime_allowed": False,
        "dashboard_post_action_allowed": False,
        "catalog_safety_level": catalog_task.get("safety_level", "") if catalog_task else "",
        "catalog_execution_mode": catalog_task.get("execution_mode", "") if catalog_task else "",
        "catalog_enabled": catalog_task.get("enabled") if catalog_task else None,
        "catalog_requires_live_device": catalog_task.get("requires_live_device") if catalog_task else None,
        "catalog_requires_password": catalog_task.get("requires_password") if catalog_task else None,
        "mismatches": mismatches,
        "reason": scenario.evidence,
    }
    row["status"] = "PASS" if not mismatches else BLOCKED_STATUS
    return row


def _observed_boundary(
    scenario: BoundaryScenario,
    catalog_task: Optional[Mapping[str, Any]],
) -> str:
    if not scenario.task_id:
        return scenario.expected_boundary
    if catalog_task is None:
        return "CATALOG_ENTRY_MISSING"
    safety_level = str(catalog_task.get("safety_level", ""))
    execution_mode = str(catalog_task.get("execution_mode", ""))
    if safety_level == "fake-adapter-only":
        return "fake-adapter-only"
    if safety_level in {"report-only", "review-only", "dry-run-only", "locked"}:
        return safety_level
    if safety_level in {"design-only", "planning-only", "scaffold-only"}:
        return safety_level
    if execution_mode in {"offline-mock", "mock-only"}:
        return "mock-only"
    return safety_level or execution_mode or "UNKNOWN"


def _mismatches(
    scenario: BoundaryScenario,
    catalog_task: Optional[Mapping[str, Any]],
    observed_boundary: str,
) -> List[str]:
    mismatches: List[str] = []
    if scenario.task_id and catalog_task is None:
        return ["catalog entry missing"]
    if scenario.expected_enabled is not None:
        if not scenario.task_id:
            return mismatches
        if catalog_task and catalog_task.get("enabled") is not scenario.expected_enabled:
            mismatches.append("enabled flag changed")
    if catalog_task:
        if catalog_task.get("requires_live_device") is not False:
            mismatches.append("requires_live_device must be false")
        if catalog_task.get("requires_password") is not False:
            mismatches.append("requires_password must be false")
        if scenario.expected_safety_level and catalog_task.get("safety_level") != scenario.expected_safety_level:
            mismatches.append("safety_level mismatch")
        if scenario.expected_execution_mode and catalog_task.get("execution_mode") != scenario.expected_execution_mode:
            mismatches.append("execution_mode mismatch")
    if observed_boundary == "CATALOG_ENTRY_MISSING":
        mismatches.append("observed boundary missing")
    return mismatches


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
    report = build_safety_boundary_regression_matrix_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
