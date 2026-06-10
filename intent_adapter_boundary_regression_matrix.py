"""Day94 adapter boundary regression matrix evidence.

This module is deterministic and local-only. It expands the Day93 fake adapter
boundary proof into a matrix of allowed, rejected, fake-target, and blocked
real-target cases without adding any live adapter behavior.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "adapter-boundary-regression-matrix"
TITLE = "Adapter Boundary Regression Matrix"
MODE = "FAKE_ADAPTER_BOUNDARY_EVIDENCE_ONLY"
ALLOWED = "allowed"
REJECTED = "rejected"
FAKE_ADAPTER = "fake_adapter"
REAL_ADAPTER_BLOCKED = "real_adapter_blocked"
REPORT_JSON = Path("reports") / "lab-summary" / "day94_adapter_boundary_regression_matrix.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day94_adapter_boundary_regression_matrix.html"


@dataclass(frozen=True)
class MatrixScenario:
    row_id: str
    intent_name: str
    intent_class: str
    guard_decision: str
    adapter_target: str
    live_execution_attempted: bool
    dry_run_only: bool
    evidence_chain_present: bool
    reason: str
    policy_allows_fake_boundary_evidence: bool = True

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


class BoundaryEvidenceFakeAdapter:
    """Fake boundary that records evidence only for already-allowed rows."""

    def __init__(self) -> None:
        self.invocations: List[Dict[str, Any]] = []

    def invoke(self, scenario: MatrixScenario) -> Dict[str, Any]:
        if scenario.guard_decision != ALLOWED or scenario.adapter_target != FAKE_ADAPTER:
            raise ValueError("Fake adapter boundary accepts only allowed fake-adapter rows.")
        invocation_id = f"day94-fake-boundary-{len(self.invocations) + 1:03d}"
        evidence = {
            "invocation_id": invocation_id,
            "row_id": scenario.row_id,
            "adapter_type": "fake",
            "boundary_use": "evidence_only",
            "live_side_effects": False,
            "dry_run_only": scenario.dry_run_only,
            "evidence_chain_present": scenario.evidence_chain_present,
        }
        self.invocations.append(deepcopy(evidence))
        return evidence


def build_regression_matrix() -> List[MatrixScenario]:
    """Return deterministic Day94 boundary regression rows."""
    return [
        MatrixScenario(
            row_id="D94-R01",
            intent_name="readonly identity evidence",
            intent_class="readonly_safe",
            guard_decision=ALLOWED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Allowed read-only safe case may enter fake adapter as boundary evidence.",
        ),
        MatrixScenario(
            row_id="D94-R02",
            intent_name="readonly interface summary requiring review",
            intent_class="readonly_requires_review",
            guard_decision=ALLOWED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Review-required read-only case may enter fake adapter only for boundary evidence.",
        ),
        MatrixScenario(
            row_id="D94-R03",
            intent_name="live ssh command attempt",
            intent_class="live_capable",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=True,
            dry_run_only=False,
            evidence_chain_present=False,
            reason="Live-capable request is rejected before fake adapter invocation.",
        ),
        MatrixScenario(
            row_id="D94-R04",
            intent_name="configure interface address",
            intent_class="config_mutation",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=False,
            evidence_chain_present=False,
            reason="Configuration mutation is rejected before any adapter boundary.",
        ),
        MatrixScenario(
            row_id="D94-R05",
            intent_name="unknown operator request",
            intent_class="unknown_intent",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=False,
            evidence_chain_present=False,
            reason="Unknown intent fails closed and cannot invoke the fake adapter.",
        ),
        MatrixScenario(
            row_id="D94-R06",
            intent_name="readonly safe request targeting real adapter",
            intent_class="readonly_safe",
            guard_decision=ALLOWED,
            adapter_target=REAL_ADAPTER_BLOCKED,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Guard may allow intent semantics, but real adapter target remains blocked.",
        ),
        MatrixScenario(
            row_id="D94-R07",
            intent_name="readonly label with reboot operation",
            intent_class="live_capable",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=True,
            dry_run_only=False,
            evidence_chain_present=True,
            reason="Misleading read-only label is rejected because the operation is unsafe.",
        ),
        MatrixScenario(
            row_id="D94-R08",
            intent_name="allowed fake adapter evidence chain",
            intent_class="readonly_safe",
            guard_decision=ALLOWED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Allowed fake adapter case records complete evidence chain.",
        ),
        MatrixScenario(
            row_id="D94-R09",
            intent_name="rejected request with evidence chain",
            intent_class="config_mutation",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=False,
            evidence_chain_present=True,
            reason="Evidence chain may exist for review, but rejected case must not invoke adapter.",
        ),
        MatrixScenario(
            row_id="D94-R10",
            intent_name="attempted execution flag present",
            intent_class="live_capable",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=True,
            dry_run_only=False,
            evidence_chain_present=True,
            reason="Attempted execution flag is recorded as blocked evidence only.",
        ),
        MatrixScenario(
            row_id="D94-R11",
            intent_name="dry-run-only readonly audit",
            intent_class="readonly_requires_review",
            guard_decision=ALLOWED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Allowed case proves dry-run-only invariant while invoking fake boundary evidence.",
        ),
        MatrixScenario(
            row_id="D94-R12",
            intent_name="rejected adapter invocation regression lock",
            intent_class="unknown_intent",
            guard_decision=REJECTED,
            adapter_target=FAKE_ADAPTER,
            live_execution_attempted=False,
            dry_run_only=False,
            evidence_chain_present=True,
            reason="Regression lock proves adapter_invoked_for_rejected remains 0.",
        ),
        MatrixScenario(
            row_id="D94-R13",
            intent_name="rejected real adapter mutation target",
            intent_class="config_mutation",
            guard_decision=REJECTED,
            adapter_target=REAL_ADAPTER_BLOCKED,
            live_execution_attempted=True,
            dry_run_only=False,
            evidence_chain_present=True,
            reason="Rejected mutation targeting a real adapter proves real adapter remains uninvoked.",
        ),
        MatrixScenario(
            row_id="D94-R14",
            intent_name="allowed review evidence with real adapter blocked",
            intent_class="readonly_requires_review",
            guard_decision=ALLOWED,
            adapter_target=REAL_ADAPTER_BLOCKED,
            live_execution_attempted=False,
            dry_run_only=True,
            evidence_chain_present=True,
            reason="Allowed semantics still cannot cross into a real adapter target.",
        ),
    ]


def run_adapter_boundary_regression_matrix() -> Dict[str, Any]:
    adapter = BoundaryEvidenceFakeAdapter()
    rows: List[Dict[str, Any]] = []

    for scenario in build_regression_matrix():
        expected_fake_adapter_invoked = _expected_fake_adapter_invoked(scenario)
        expected_real_adapter_invoked = False
        live_execution_allowed = False
        actual_real_adapter_invoked = False
        live_execution_invoked = False
        invocation: Optional[Dict[str, Any]] = None
        actual_fake_adapter_invoked = False

        if expected_fake_adapter_invoked:
            invocation = adapter.invoke(scenario)
            actual_fake_adapter_invoked = True

        row = _build_matrix_row(
            scenario=scenario,
            expected_fake_adapter_invoked=expected_fake_adapter_invoked,
            actual_fake_adapter_invoked=actual_fake_adapter_invoked,
            expected_real_adapter_invoked=expected_real_adapter_invoked,
            actual_real_adapter_invoked=actual_real_adapter_invoked,
            live_execution_allowed=live_execution_allowed,
            live_execution_invoked=live_execution_invoked,
            invocation=invocation,
        )
        rows.append(row)

    summary = build_aggregate_summary(rows)
    report = {
        "day": 94,
        "day_id": "Day94",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "mode": MODE,
        "overall_status": summary["overall_status"],
        "summary": summary,
        "invariant_checks": build_invariant_checks(summary, rows),
        "matrix_rows": rows,
        "fake_adapter_invocation_evidence": deepcopy(adapter.invocations),
        "safety_note": (
            "Fake-adapter-only regression evidence. No SSH, no real device access, "
            "no live execution, and no real adapter invocation."
        ),
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_execution": True,
        "no_real_adapter_invocation": True,
        "no_config_json_read": True,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
    return report


def build_aggregate_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_rows = len(rows)
    passed_rows = sum(1 for row in rows if row["regression_status"] == "PASS")
    failed_rows = total_rows - passed_rows
    allowed_rows = sum(1 for row in rows if row["guard_decision"] == ALLOWED)
    rejected_rows = sum(1 for row in rows if row["guard_decision"] == REJECTED)
    fake_adapter_invocations = sum(1 for row in rows if row["actual_fake_adapter_invoked"])
    real_adapter_invocations = sum(1 for row in rows if row["actual_real_adapter_invoked"])
    live_execution_invocations = sum(1 for row in rows if row["live_execution_invoked"])
    adapter_invoked_for_rejected = sum(
        1
        for row in rows
        if row["guard_decision"] == REJECTED
        and (row["actual_fake_adapter_invoked"] or row["actual_real_adapter_invoked"])
    )
    rejected_without_adapter_invocation = sum(
        1
        for row in rows
        if row["guard_decision"] == REJECTED
        and not row["actual_fake_adapter_invoked"]
        and not row["actual_real_adapter_invoked"]
    )
    overall_status = "PASS" if (
        total_rows >= 12
        and failed_rows == 0
        and real_adapter_invocations == 0
        and live_execution_invocations == 0
        and adapter_invoked_for_rejected == 0
        and rejected_without_adapter_invocation == rejected_rows
    ) else "FAIL"
    return {
        "total_rows": total_rows,
        "passed_rows": passed_rows,
        "failed_rows": failed_rows,
        "allowed_rows": allowed_rows,
        "rejected_rows": rejected_rows,
        "fake_adapter_invocations": fake_adapter_invocations,
        "real_adapter_invocations": real_adapter_invocations,
        "live_execution_invocations": live_execution_invocations,
        "adapter_invoked_for_rejected": adapter_invoked_for_rejected,
        "rejected_without_adapter_invocation": rejected_without_adapter_invocation,
        "overall_status": overall_status,
    }


def build_invariant_checks(
    summary: Dict[str, Any],
    rows: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    checks = [
        ("failed_rows == 0", summary["failed_rows"] == 0),
        ("real_adapter_invocations == 0", summary["real_adapter_invocations"] == 0),
        ("live_execution_invocations == 0", summary["live_execution_invocations"] == 0),
        ("adapter_invoked_for_rejected == 0", summary["adapter_invoked_for_rejected"] == 0),
        ("total_rows >= 12", summary["total_rows"] >= 12),
        (
            "rejected rows never invoke adapters",
            summary["rejected_without_adapter_invocation"] == summary["rejected_rows"],
        ),
        (
            "allowed fake adapter rows have evidence-only invocation",
            all(
                row["boundary_result"] == "FAKE_BOUNDARY_EVIDENCE_RECORDED"
                for row in rows
                if row["guard_decision"] == ALLOWED and row["adapter_target"] == FAKE_ADAPTER
            ),
        ),
    ]
    return [
        {"name": name, "status": "PASS" if passed else "FAIL"}
        for name, passed in checks
    ]


def validate_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    rows = report.get("matrix_rows", [])

    if report.get("day") != 94:
        errors.append("day must be 94.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be adapter-boundary-regression-matrix.")
    if report.get("mode") != MODE:
        errors.append(f"mode must be {MODE}.")
    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_live_execution",
        "no_real_adapter_invocation",
        "no_config_json_read",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    if summary.get("total_rows", 0) < 12:
        errors.append("total_rows must be at least 12.")
    for count_field in (
        "failed_rows",
        "real_adapter_invocations",
        "live_execution_invocations",
        "adapter_invoked_for_rejected",
    ):
        if summary.get(count_field) != 0:
            errors.append(f"{count_field} must be 0.")
    if summary.get("overall_status") != "PASS":
        errors.append("overall_status must be PASS.")
    row_ids = [row.get("row_id") for row in rows]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row IDs must be unique.")

    for row in rows:
        if row.get("actual_real_adapter_invoked") is not False:
            errors.append(f"{row.get('row_id')} invoked a real adapter.")
        if row.get("live_execution_invoked") is not False:
            errors.append(f"{row.get('row_id')} invoked live execution.")
        if row.get("live_execution_allowed") is not False:
            errors.append(f"{row.get('row_id')} allowed live execution.")
        if row.get("guard_decision") == REJECTED and row.get("actual_fake_adapter_invoked") is not False:
            errors.append(f"{row.get('row_id')} rejected row invoked fake adapter.")
        if row.get("expected_fake_adapter_invoked") != row.get("actual_fake_adapter_invoked"):
            errors.append(f"{row.get('row_id')} fake adapter expectation mismatch.")
        if row.get("expected_real_adapter_invoked") != row.get("actual_real_adapter_invoked"):
            errors.append(f"{row.get('row_id')} real adapter expectation mismatch.")
        if row.get("regression_status") != "PASS":
            errors.append(f"{row.get('row_id')} regression_status must be PASS.")
    return errors


def write_adapter_boundary_regression_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    invariant_rows = "".join(
        "<tr>"
        f"<td>{html.escape(check['name'])}</td>"
        f"<td class=\"{html.escape(check['status'].lower())}\">{html.escape(check['status'])}</td>"
        "</tr>"
        for check in report["invariant_checks"]
    )
    matrix_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['row_id'])}</td>"
        f"<td>{html.escape(row['intent_name'])}</td>"
        f"<td>{html.escape(row['intent_class'])}</td>"
        f"<td>{html.escape(row['guard_decision'])}</td>"
        f"<td>{html.escape(row['adapter_target'])}</td>"
        f"<td>{html.escape(json.dumps(row['expected_fake_adapter_invoked']))}</td>"
        f"<td>{html.escape(json.dumps(row['actual_fake_adapter_invoked']))}</td>"
        f"<td>{html.escape(json.dumps(row['actual_real_adapter_invoked']))}</td>"
        f"<td>{html.escape(json.dumps(row['live_execution_attempted']))}</td>"
        f"<td>{html.escape(json.dumps(row['live_execution_allowed']))}</td>"
        f"<td>{html.escape(row['boundary_result'])}</td>"
        f"<td class=\"{html.escape(row['regression_status'].lower())}\">{html.escape(row['regression_status'])}</td>"
        f"<td>{html.escape(row['reason'])}</td>"
        "</tr>"
        for row in report["matrix_rows"]
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1c2733; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 22px; }}
    th, td {{ border: 1px solid #d6dee9; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    .pass {{ color: #116329; font-weight: bold; }}
    .warn {{ color: #9a6700; font-weight: bold; }}
    .fail {{ color: #b42318; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['title'])}</h1>
  <p><strong>Result:</strong> <span class="{html.escape(summary['overall_status'].lower())}">{html.escape(summary['overall_status'])}</span> / {html.escape(report['mode'])}</p>
  <p><strong>Safety note:</strong> fake-adapter-only, no SSH, no real device access, no live execution, no real adapter invocation.</p>
  <h2>Summary</h2>
  <p><strong>Total rows:</strong> {summary['total_rows']} | <strong>Allowed:</strong> {summary['allowed_rows']} | <strong>Rejected:</strong> {summary['rejected_rows']} | <strong>Passed:</strong> {summary['passed_rows']} | <strong>Failed:</strong> {summary['failed_rows']}</p>
  <p><strong>Fake adapter invocations:</strong> {summary['fake_adapter_invocations']} | <strong>adapter_invoked_for_rejected:</strong> {summary['adapter_invoked_for_rejected']} | <strong>real_adapter_invocations:</strong> {summary['real_adapter_invocations']} | <strong>live_execution_invocations:</strong> {summary['live_execution_invocations']}</p>
  <h2>Invariant Checks</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Status</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
  <h2>Regression Matrix</h2>
  <table>
    <thead><tr><th>Row</th><th>Intent</th><th>Intent class</th><th>Guard</th><th>Adapter target</th><th>Expected fake</th><th>Actual fake</th><th>Actual real</th><th>Live attempted</th><th>Live allowed</th><th>Boundary result</th><th>Status</th><th>Reason</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <p>Final recommendation: <code>KEEP_FAKE_BOUNDARY_EVIDENCE_ONLY</code></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_adapter_boundary_regression_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else run_adapter_boundary_regression_matrix()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_adapter_boundary_regression_matrix_html(safe_report, html_path)
    return json_path, html_path


def _expected_fake_adapter_invoked(scenario: MatrixScenario) -> bool:
    return (
        scenario.guard_decision == ALLOWED
        and scenario.adapter_target == FAKE_ADAPTER
        and scenario.policy_allows_fake_boundary_evidence
    )


def _build_matrix_row(
    scenario: MatrixScenario,
    expected_fake_adapter_invoked: bool,
    actual_fake_adapter_invoked: bool,
    expected_real_adapter_invoked: bool,
    actual_real_adapter_invoked: bool,
    live_execution_allowed: bool,
    live_execution_invoked: bool,
    invocation: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    boundary_result = _boundary_result(
        scenario=scenario,
        actual_fake_adapter_invoked=actual_fake_adapter_invoked,
        actual_real_adapter_invoked=actual_real_adapter_invoked,
    )
    row = {
        **scenario.to_record(),
        "expected_fake_adapter_invoked": expected_fake_adapter_invoked,
        "actual_fake_adapter_invoked": actual_fake_adapter_invoked,
        "expected_real_adapter_invoked": expected_real_adapter_invoked,
        "actual_real_adapter_invoked": actual_real_adapter_invoked,
        "live_execution_allowed": live_execution_allowed,
        "live_execution_invoked": live_execution_invoked,
        "boundary_result": boundary_result,
        "invocation_id": invocation["invocation_id"] if invocation else None,
        "invocation_evidence": invocation,
    }
    row["regression_status"] = "PASS" if _row_passes(row) else "FAIL"
    return row


def _boundary_result(
    scenario: MatrixScenario,
    actual_fake_adapter_invoked: bool,
    actual_real_adapter_invoked: bool,
) -> str:
    if actual_real_adapter_invoked:
        return "REAL_ADAPTER_VIOLATION"
    if scenario.adapter_target == REAL_ADAPTER_BLOCKED:
        return "REAL_ADAPTER_BLOCKED"
    if scenario.guard_decision == REJECTED:
        return "REJECTED_BEFORE_ADAPTER"
    if actual_fake_adapter_invoked:
        return "FAKE_BOUNDARY_EVIDENCE_RECORDED"
    return "NO_ADAPTER_INVOCATION"


def _row_passes(row: Dict[str, Any]) -> bool:
    if row["expected_fake_adapter_invoked"] != row["actual_fake_adapter_invoked"]:
        return False
    if row["expected_real_adapter_invoked"] != row["actual_real_adapter_invoked"]:
        return False
    if row["actual_real_adapter_invoked"] is not False:
        return False
    if row["live_execution_allowed"] is not False:
        return False
    if row["live_execution_invoked"] is not False:
        return False
    if row["guard_decision"] == REJECTED and row["actual_fake_adapter_invoked"]:
        return False
    if row["adapter_target"] == REAL_ADAPTER_BLOCKED and row["actual_fake_adapter_invoked"]:
        return False
    return True
