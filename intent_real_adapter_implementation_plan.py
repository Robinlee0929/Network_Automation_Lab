"""Day90 real adapter implementation plan.

This module decides whether the project may enter a later real read-only
adapter prototype phase. It is deterministic planning evidence only: no SSH,
RouterOS transport, device connection, command execution, subprocess, or live
adapter implementation is provided here.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "real-adapter-implementation-plan"
TITLE = "Real Adapter Implementation Plan"
SCOPE = "planning_only"
REPORT_JSON = Path("reports") / "lab-summary" / "day90_real_adapter_implementation_plan.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day90_real_adapter_implementation_plan.html"
DECISIONS = ("GO", "CONDITIONAL_GO", "NO_GO")

REQUIRED_FALSE_FLAGS = (
    "adapter_implementation_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "routeros_command_execution_allowed",
)

FORBIDDEN_SCOPE = (
    "true SSH client implementation",
    "RouterOS command runner",
    "real device host username or password",
    "adapter implementation class connection logic",
    "automatic configuration apply",
    "configuration mutation",
    "write operations",
    "firewall or interface changes",
    "reboot reset or destructive operations",
    "subprocess or network command execution",
)

MINIMUM_SAFE_REAL_ADAPTER_SCOPE = (
    "minimal read-only prototype only after a later explicit Day91 gate",
    "explicit allow flag required before any future live-read path",
    "bounded positive command allowlist",
    "short timeout with fail-closed handling",
    "reviewer-visible evidence logging",
    "redaction or digest-only output handling",
    "no configuration mutation",
)

REQUIRED_NEXT_PHASE_CONTROLS = (
    "Keep the first future implementation phase to a minimal read-only prototype.",
    "Require an explicit allow flag before any future live-read request can cross the boundary.",
    "Validate every future command against a bounded positive allowlist before adapter entry.",
    "Apply a bounded timeout and fail closed on timeout or adapter error.",
    "Log reviewer-visible evidence for every future live-read attempt.",
    "Reject or redact secret-bearing output before storage.",
    "Keep configuration mutation and automatic apply paths blocked.",
)

IMPLEMENTATION_ENTRY_CRITERIA = (
    "Day83-Day89 required design, safety, runner, documentation, and report evidence exists.",
    "Day90 report keeps adapter_implementation_allowed=false.",
    "Day90 report keeps live_device_access_allowed=false.",
    "Day90 report keeps ssh_allowed=false.",
    "Day90 report keeps routeros_command_execution_allowed=false.",
    "Day91 scope is limited to a minimal read-only prototype with hard safety guards.",
)


def _artifact(path: str, required: bool = True) -> Dict[str, Any]:
    return {"path": path, "required": required}


def required_evidence_spec() -> List[Dict[str, Any]]:
    """Return deterministic Day90 evidence checks."""
    return [
        {
            "id": "day83_readiness_artifact",
            "day": "Day83",
            "title": "Read-only Executor Readiness Gate",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day83_readonly_executor_readiness_gate.json"),
                _artifact("reports/lab-summary/day83_readonly_executor_readiness_gate.html"),
                _artifact("docs/ai/readonly_executor_readiness_gate.md"),
                _artifact("docs/roadmap/day83_readonly_executor_readiness_gate.md"),
            ],
        },
        {
            "id": "day84_adapter_contract_artifact",
            "day": "Day84",
            "title": "Read-only Executor Adapter Interface Contract",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day84_readonly_executor_adapter_contract.json"),
                _artifact("reports/lab-summary/day84_readonly_executor_adapter_contract.html"),
                _artifact("docs/ai/intent_readonly_executor_adapter_contract.md"),
                _artifact("docs/roadmap/day84_readonly_executor_adapter_interface_contract.md"),
            ],
        },
        {
            "id": "day85_mock_adapter_evidence_binding_artifact",
            "day": "Day85",
            "title": "Mock Adapter + Evidence Binding",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day85_mock_adapter_evidence_binding.json"),
                _artifact("reports/lab-summary/day85_mock_adapter_evidence_binding.html"),
                _artifact("docs/ai/intent_mock_adapter_evidence_binding.md"),
                _artifact("docs/roadmap/day85_mock_adapter_evidence_binding.md"),
            ],
        },
        {
            "id": "day86_controlled_runner_harness_artifact",
            "day": "Day86",
            "title": "Controlled Runner Harness + Safety Regression",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day86_controlled_runner_harness.json"),
                _artifact("reports/lab-summary/day86_controlled_runner_harness.html"),
                _artifact("docs/ai/intent_controlled_runner_harness.md"),
                _artifact("docs/roadmap/day86_controlled_runner_harness_safety_regression.md"),
            ],
        },
        {
            "id": "day87_phase_gate_review_artifact",
            "day": "Day87",
            "title": "Read-only Executor Phase Gate Review",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day87_readonly_executor_phase_gate_review.json"),
                _artifact("reports/lab-summary/day87_readonly_executor_phase_gate_review.html"),
                _artifact("docs/ai/intent_readonly_executor_phase_gate_review.md"),
                _artifact("docs/roadmap/day87_readonly_executor_phase_gate_review.md"),
            ],
        },
        {
            "id": "day88_real_adapter_design_draft_artifact",
            "day": "Day88",
            "title": "Real Read-only Executor Adapter Design Draft",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day88_real_readonly_executor_adapter_design.json"),
                _artifact("reports/lab-summary/day88_real_readonly_executor_adapter_design.html"),
                _artifact("docs/ai/intent_real_readonly_executor_adapter_design.md"),
                _artifact("docs/roadmap/day88_real_readonly_executor_adapter_design.md"),
            ],
        },
        {
            "id": "day89_real_adapter_safety_boundary_artifact",
            "day": "Day89",
            "title": "Real Adapter Safety Boundary Spec",
            "critical": True,
            "artifacts": [
                _artifact("reports/lab-summary/day89_real_adapter_safety_boundary_spec.json"),
                _artifact("reports/lab-summary/day89_real_adapter_safety_boundary_spec.html"),
                _artifact("docs/ai/real_adapter_safety_boundary_spec.md"),
                _artifact("docs/roadmap/day89_real_adapter_safety_boundary_spec.md"),
            ],
        },
        {
            "id": "day90_runner_registration",
            "day": "Day90",
            "title": "Runner task registration",
            "critical": True,
            "artifacts": [
                _artifact("network_lab.py"),
            ],
            "required_text": TASK_NAME,
        },
        {
            "id": "day90_dashboard_visibility",
            "day": "Day90",
            "title": "Static dashboard/report visibility",
            "critical": True,
            "artifacts": [
                _artifact("network_lab.py"),
                _artifact("dashboard_app.py"),
            ],
            "required_text": "day90_real_adapter_implementation_plan",
        },
        {
            "id": "day90_safety_docs",
            "day": "Day90",
            "title": "AI reviewer and roadmap documentation",
            "critical": True,
            "artifacts": [
                _artifact("docs/ai/intent_real_adapter_implementation_plan.md"),
                _artifact("docs/roadmap/day90_real_adapter_implementation_plan.md"),
            ],
        },
    ]


def _path_exists(project_root: Path, path: str) -> bool:
    return (Path(project_root) / path).is_file()


def _file_contains(project_root: Path, path: str, required_text: str) -> bool:
    file_path = Path(project_root) / path
    try:
        return required_text in file_path.read_text(encoding="utf-8")
    except OSError:
        return False


def build_prerequisite_checks(project_root: Path) -> List[Dict[str, Any]]:
    """Evaluate Day90 prerequisite checks from repository evidence only."""
    checks: List[Dict[str, Any]] = []
    root = Path(project_root)
    for spec in required_evidence_spec():
        artifacts = []
        required_text = spec.get("required_text")
        for artifact in spec["artifacts"]:
            exists = _path_exists(root, artifact["path"])
            text_present = True
            if exists and required_text:
                text_present = _file_contains(root, artifact["path"], str(required_text))
            artifacts.append(
                {
                    "path": artifact["path"],
                    "required": artifact["required"],
                    "exists": exists,
                    "required_text_present": text_present,
                }
            )

        missing_required = [
            item["path"]
            for item in artifacts
            if item["required"] and (not item["exists"] or not item["required_text_present"])
        ]
        checks.append(
            {
                "id": spec["id"],
                "day": spec["day"],
                "title": spec["title"],
                "critical": spec["critical"],
                "status": "PASS" if not missing_required else "MISSING",
                "artifacts": artifacts,
                "missing_required": missing_required,
            }
        )
    return checks


def build_evidence_chain(prerequisite_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "day": check["day"],
            "title": check["title"],
            "evidence_status": check["status"],
            "critical": check["critical"],
            "artifacts": [artifact["path"] for artifact in check["artifacts"]],
            "missing_required": list(check["missing_required"]),
        }
        for check in prerequisite_checks
    ]


def build_non_go_blockers(prerequisite_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    blockers = []
    for check in prerequisite_checks:
        if check["critical"] and check["missing_required"]:
            blockers.append(
                {
                    "check_id": check["id"],
                    "day": check["day"],
                    "reason": "Required critical evidence is missing or incomplete.",
                    "missing_required": list(check["missing_required"]),
                }
            )
    return blockers


def decide_day90(non_go_blockers: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    if non_go_blockers:
        return (
            "NO_GO",
            "BLOCKED",
            "Critical Day83-Day90 evidence is missing, so implementation entry cannot be approved.",
        )
    return (
        "CONDITIONAL_GO",
        "READY_WITH_CONDITIONS",
        (
            "Required design and safety evidence exists, but Day90 remains planning-only; "
            "Day91 may enter only a minimal read-only prototype path with explicit hard guards."
        ),
    )


def build_conditional_go_requirements(non_go_blockers: List[Dict[str, Any]]) -> List[str]:
    if non_go_blockers:
        return [
            "Resolve every non_go_blocker before requesting Day91 prototype entry.",
            "Regenerate Day90 after missing critical evidence is restored.",
        ]
    return list(REQUIRED_NEXT_PHASE_CONTROLS)


def validate_real_adapter_implementation_plan(report: Dict[str, Any]) -> List[str]:
    """Return validation errors for the Day90 planning report."""
    errors: List[str] = []
    if report.get("day") != 90:
        errors.append("day must be 90.")
    if report.get("title") != TITLE:
        errors.append("title must match Day90.")
    if report.get("scope") != SCOPE:
        errors.append("scope must be planning_only.")
    if report.get("decision") not in DECISIONS:
        errors.append("decision must be GO, CONDITIONAL_GO, or NO_GO.")
    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if not report.get("evidence_chain"):
        errors.append("evidence_chain must be present.")
    forbidden_text = " ".join(report.get("explicitly_forbidden_scope", [])).lower()
    for token in ("mutation", "configuration", "write"):
        if token not in forbidden_text:
            errors.append(f"explicitly_forbidden_scope must include {token}.")
    if report.get("decision") == "GO" and report.get("non_go_blockers"):
        errors.append("GO cannot be produced when non_go_blockers are present.")
    return errors


def build_real_adapter_implementation_plan_report(project_root: Path = Path(".")) -> Dict[str, Any]:
    """Build the deterministic Day90 implementation-entry decision report."""
    prerequisite_checks = build_prerequisite_checks(Path(project_root))
    non_go_blockers = build_non_go_blockers(prerequisite_checks)
    decision, readiness_level, decision_reason = decide_day90(non_go_blockers)
    report: Dict[str, Any] = {
        "day": 90,
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "scope": SCOPE,
        "status": "PASS",
        "adapter_implementation_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "routeros_command_execution_allowed": False,
        "decision": decision,
        "readiness_level": readiness_level,
        "decision_reason": decision_reason,
        "prerequisite_checks": prerequisite_checks,
        "implementation_entry_criteria": list(IMPLEMENTATION_ENTRY_CRITERIA),
        "non_go_blockers": non_go_blockers,
        "conditional_go_requirements": build_conditional_go_requirements(non_go_blockers),
        "required_next_phase_controls": list(REQUIRED_NEXT_PHASE_CONTROLS),
        "minimum_safe_real_adapter_scope": list(MINIMUM_SAFE_REAL_ADAPTER_SCOPE),
        "explicitly_forbidden_scope": list(FORBIDDEN_SCOPE),
        "evidence_chain": build_evidence_chain(prerequisite_checks),
        "recommended_day91_positioning": (
            "Do not enter Day91 implementation; restore missing critical evidence first."
            if decision == "NO_GO"
            else (
                "Day91 may be positioned as a minimal read-only prototype only, with explicit "
                "allow flag, bounded allowlist, timeout, evidence logging, redaction, and no mutation."
            )
        ),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day90 is not implementation. It does not add a true SSH client, RouterOS "
            "command runner, real host credentials, adapter connection logic, or automatic "
            "configuration apply behavior."
        ),
    }
    validation_errors = validate_real_adapter_implementation_plan(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _check_rows(checks: List[Dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(check['day'])}</td>"
        f"<td>{html.escape(check['title'])}</td>"
        f"<td>{html.escape(check['status'])}</td>"
        f"<td>{html.escape(', '.join(check['missing_required']) or 'none')}</td>"
        "</tr>"
        for check in checks
    )


def write_real_adapter_implementation_plan_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write the static Day90 reviewer HTML report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['title'])}</h1>
  <p><strong>Decision:</strong> {html.escape(report['decision'])}</p>
  <p><strong>Readiness level:</strong> {html.escape(report['readiness_level'])}</p>
  <p><strong>Scope:</strong> {html.escape(report['scope'])}</p>
  <p><strong>Decision reason:</strong> {html.escape(report['decision_reason'])}</p>
  <p><strong>Safety:</strong> planning-only; no SSH, RouterOS command runner, live device access, adapter connection logic, or automatic apply.</p>
  <h2>Locked Flags</h2>
  <table>
    <tbody>
      <tr><th>Adapter implementation allowed</th><td>{html.escape(json.dumps(report['adapter_implementation_allowed']))}</td></tr>
      <tr><th>Live device access allowed</th><td>{html.escape(json.dumps(report['live_device_access_allowed']))}</td></tr>
      <tr><th>SSH allowed</th><td>{html.escape(json.dumps(report['ssh_allowed']))}</td></tr>
      <tr><th>RouterOS command execution allowed</th><td>{html.escape(json.dumps(report['routeros_command_execution_allowed']))}</td></tr>
    </tbody>
  </table>
  <h2>Prerequisite Checks</h2>
  <table><thead><tr><th>Day</th><th>Evidence</th><th>Status</th><th>Missing required</th></tr></thead><tbody>{_check_rows(report['prerequisite_checks'])}</tbody></table>
  <h2>Blockers</h2>
  <ul>{_html_list([blocker['reason'] + ' ' + ', '.join(blocker['missing_required']) for blocker in report['non_go_blockers']] or ['none'])}</ul>
  <h2>Required Controls Before Implementation</h2>
  <ul>{_html_list(report['required_next_phase_controls'])}</ul>
  <h2>Minimum Safe Real Adapter Scope</h2>
  <ul>{_html_list(report['minimum_safe_real_adapter_scope'])}</ul>
  <h2>Forbidden Actions</h2>
  <ul>{_html_list(report['explicitly_forbidden_scope'])}</ul>
  <h2>Evidence Chain</h2>
  <table><thead><tr><th>Day</th><th>Evidence</th><th>Status</th><th>Artifacts</th></tr></thead><tbody>{''.join('<tr><td>' + html.escape(item['day']) + '</td><td>' + html.escape(item['title']) + '</td><td>' + html.escape(item['evidence_status']) + '</td><td>' + html.escape(', '.join(item['artifacts'])) + '</td></tr>' for item in report['evidence_chain'])}</tbody></table>
  <h2>Day91 Positioning</h2>
  <p>{html.escape(report['recommended_day91_positioning'])}</p>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_real_adapter_implementation_plan_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day90 JSON and HTML reports and return their paths."""
    root = Path(project_root)
    safe_report = deepcopy(report) if report is not None else build_real_adapter_implementation_plan_report(root)
    json_path = root / REPORT_JSON
    html_path = root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_real_adapter_implementation_plan_html(safe_report, html_path)
    return json_path, html_path
