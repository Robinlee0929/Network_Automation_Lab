"""Day135 AI provider disabled-by-default safety regression.

This module reads Day134 disabled provider evidence as data only and verifies
that downstream registry, CLI, report, and consumer-style read paths preserve
disabled-by-default behavior. It does not import or instantiate providers.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple

from report_file_utils import write_text_with_parents


DAY = 135
DAY_LABEL = "Day135"
TASK_NAME = "ai-provider-disabled-by-default-safety-regression"
TITLE = "AI Provider Disabled-by-Default Safety Regression"
FULL_TITLE = f"{DAY_LABEL} {TITLE}"
MODE = "REVIEW_ONLY"
SCOPE = "DISABLED_BY_DEFAULT_SAFETY_REGRESSION"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
REGRESSION_VERDICT = "DISABLED_BY_DEFAULT_PRESERVED"
BLOCKED_VERDICT = "DISABLED_BY_DEFAULT_REGRESSION_BLOCKED"
SOURCE_CONTRACT_DAY = 134
SOURCE_CONTRACT_RESULT = "DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY"
SOURCE_CONTRACT_JSON = Path("reports") / "lab-summary" / "day134_disabled_ai_provider_adapter_contract.json"
REPORT_JSON = Path("reports") / "lab-summary" / "day135_ai_provider_disabled_by_default_safety_regression.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day135_ai_provider_disabled_by_default_safety_regression.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day135_ai_provider_disabled_by_default_safety_regression.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day135_ai_provider_disabled_by_default_safety_regression.md"

DISABLED_SOURCE_FIELDS: Tuple[str, ...] = (
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
)

DAY135_DISABLED_FIELDS: Tuple[str, ...] = (
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "provider_instantiated",
    "api_called",
    "execution_invoked",
    "registry_activation_allowed",
    "cli_activation_allowed",
    "report_activation_allowed",
    "next_phase_allowed",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "day",
    "task",
    "mode",
    "scope",
    "is_next_day_feature",
    "is_day136",
    "opens_execution_provider_or_api",
    "agents_md_pre_read",
    "agents_md_path",
    "agents_md_modified",
    "source_contract_day",
    "source_contract_read",
    "source_contract_read_only",
    "consumer_read_allowed",
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "provider_instantiated",
    "api_called",
    "execution_invoked",
    "registry_activation_allowed",
    "cli_activation_allowed",
    "report_activation_allowed",
    "next_phase_allowed",
    "regression_verdict",
    "overall_status",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_pre_read": "NO",
            "agents_md_path": "AGENTS.md",
            "agents_md_modified": False,
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_read_error": "AGENTS.md not found.",
        }
    except OSError as exc:
        return {
            "agents_md_pre_read": "NO",
            "agents_md_path": "AGENTS.md",
            "agents_md_modified": False,
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_read_error": str(exc),
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read": "YES" if required_phrase_present else "NO",
        "agents_md_path": "AGENTS.md",
        "agents_md_modified": False,
        "agents_md_status": "FOUND_AND_READ" if required_phrase_present else "MISSING_STOPPED",
        "agents_md_read_error": "",
    }


def load_day134_disabled_contract_evidence(
    project_root: Path,
    source_contract_path: Path = SOURCE_CONTRACT_JSON,
) -> Dict[str, Any]:
    path = Path(project_root) / source_contract_path
    evidence: Dict[str, Any] = {
        "source_contract_path": source_contract_path.as_posix(),
        "source_contract_read": False,
        "source_contract_read_only": True,
        "source_contract_read_error": "",
        "source_contract": {},
    }
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        evidence["source_contract_read_error"] = f"Day134 evidence not found: {source_contract_path.as_posix()}"
        return evidence
    except json.JSONDecodeError as exc:
        evidence["source_contract_read_error"] = f"Day134 evidence is not valid JSON: {exc.msg}"
        return evidence
    except OSError as exc:
        evidence["source_contract_read_error"] = str(exc)
        return evidence

    if not isinstance(loaded, dict):
        evidence["source_contract_read_error"] = "Day134 evidence must contain a JSON object."
        return evidence

    evidence["source_contract_read"] = True
    evidence["source_contract"] = loaded
    return evidence


def validate_disabled_by_default_source_contract(source_contract: Mapping[str, Any]) -> Tuple[bool, list[str]]:
    errors: list[str] = []
    if source_contract.get("day_number") != SOURCE_CONTRACT_DAY:
        errors.append("Day134 source contract day_number must be 134.")
    if source_contract.get("result") != SOURCE_CONTRACT_RESULT:
        errors.append(f"Day134 source contract result must be {SOURCE_CONTRACT_RESULT}.")
    if source_contract.get("overall_status") != "PASS":
        errors.append("Day134 source contract overall_status must be PASS.")

    for field in DISABLED_SOURCE_FIELDS:
        if source_contract.get(field) is not False:
            errors.append(f"Day134 source field {field} must be false.")

    if _source_bool(source_contract, "provider_instantiated", "provider_invoked") is not False:
        errors.append("provider_instantiated must be false; Day134 evidence must not show provider invocation.")
    if _source_bool(source_contract, "api_called", "api_called") is not False:
        errors.append("api_called must be false; Day134 evidence must not show API calls.")
    if _source_bool(source_contract, "execution_invoked", "execution_path_reached") is not False:
        errors.append("execution_invoked must be false; Day134 evidence must not show execution path reachability.")
    if source_contract.get("next_phase_allowed") is not False:
        errors.append("Day134 source contract next_phase_allowed must be false.")

    return not errors, errors


def build_regression_cases(source_contract: Mapping[str, Any], source_read: bool) -> list[Dict[str, Any]]:
    cases: list[Dict[str, Any]] = []
    baseline_ok, baseline_errors = validate_disabled_by_default_source_contract(source_contract) if source_read else (False, ["Day134 evidence was not readable."])
    cases.append(
        _case(
            "baseline_day134_disabled_provider_contract",
            "Baseline Day134 disabled provider contract is accepted as read-only evidence.",
            accepted=baseline_ok,
            errors=baseline_errors,
        )
    )
    cases.append(
        _case(
            "consumer_read_only_inspection",
            "Consumer-style read is allowed only as read-only inspection.",
            accepted=baseline_ok,
            errors=baseline_errors,
            read_only=True,
        )
    )

    for field in (
        "provider_enabled",
        "api_enabled",
        "execution_enabled",
        "model_invocation_enabled",
        "network_enabled",
        "provider_instantiated",
        "api_called",
        "execution_invoked",
    ):
        mutated = dict(source_contract)
        mutated[field] = True
        accepted, errors = validate_disabled_by_default_source_contract(mutated)
        cases.append(
            _case(
                f"{field}_true_rejected",
                f"{field}=true fails the disabled-by-default regression.",
                accepted=accepted,
                errors=errors,
                expected_rejected=True,
            )
        )

    cases.append(
        _case(
            "missing_or_unreadable_day134_evidence_rejected",
            "Missing or unreadable Day134 evidence must not advance.",
            accepted=False,
            errors=["Day134 evidence was not readable."],
            expected_rejected=True,
        )
    )
    cases.append(
        {
            "case": "cli_report_registry_paths_do_not_activate_provider_api_execution",
            "description": "CLI/report/registry paths must not activate provider/API/execution.",
            "registry_activation_allowed": False,
            "cli_activation_allowed": False,
            "report_activation_allowed": False,
            "provider_instantiated": False,
            "api_called": False,
            "execution_invoked": False,
            "accepted": True,
            "rejected": False,
            "next_phase_allowed": False,
            "status": "PASS",
            "errors": [],
        }
    )
    return cases


def build_ai_provider_disabled_by_default_safety_regression_report(
    project_root: Path,
    source_contract_path: Path = SOURCE_CONTRACT_JSON,
) -> Dict[str, Any]:
    agents = build_agents_md_evidence(project_root)
    source = load_day134_disabled_contract_evidence(project_root, source_contract_path)
    source_contract = source["source_contract"]
    source_ok, source_errors = (
        validate_disabled_by_default_source_contract(source_contract)
        if source["source_contract_read"]
        else (False, [source["source_contract_read_error"]])
    )
    regression_cases = build_regression_cases(source_contract, source["source_contract_read"])

    report: Dict[str, Any] = {
        "day": DAY,
        "day_label": DAY_LABEL,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "is_next_day_feature": False,
        "is_day136": False,
        "opens_execution_provider_or_api": False,
        **agents,
        "source_contract_day": SOURCE_CONTRACT_DAY,
        "source_contract_path": source["source_contract_path"],
        "source_contract_read": source["source_contract_read"],
        "source_contract_read_only": source["source_contract_read_only"],
        "source_contract_read_error": source["source_contract_read_error"],
        "source_contract_validation_errors": source_errors,
        "consumer_read_allowed": bool(source["source_contract_read"] and source_ok),
        "provider_enabled": False,
        "api_enabled": False,
        "execution_enabled": False,
        "model_invocation_enabled": False,
        "network_enabled": False,
        "provider_instantiated": False,
        "api_called": False,
        "execution_invoked": False,
        "registry_activation_allowed": False,
        "cli_activation_allowed": False,
        "report_activation_allowed": False,
        "next_phase_allowed": False,
        "regression_verdict": "PENDING",
        "overall_status": "PENDING",
        "regression_cases": regression_cases,
        "explicit_non_goals": [
            "This is not the next day's feature.",
            "This is not Day136.",
            "No provider, API, model, network, or execution path is opened.",
            "No provider object is instantiated.",
            "No API is called.",
            "No execution is invoked.",
            "No next phase is unlocked.",
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    report["regression_verdict"] = REGRESSION_VERDICT if report["overall_status"] == OVERALL_STATUS else BLOCKED_VERDICT
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")

    if report.get("agents_md_pre_read") != "YES":
        errors.append("AGENTS.md pre-read must be YES.")
    if report.get("agents_md_path") != "AGENTS.md":
        errors.append("AGENTS.md path must be AGENTS.md.")
    if report.get("agents_md_modified") is not False:
        errors.append("AGENTS.md modified must be false.")
    if report.get("source_contract_read") is not True:
        errors.append("Day134 source contract/evidence must be readable.")
    if report.get("source_contract_read_only") is not True:
        errors.append("Day134 source contract/evidence must be read-only.")
    if report.get("consumer_read_allowed") is not True:
        errors.append("Consumer read must be allowed only after valid read-only Day134 evidence.")
    if report.get("is_next_day_feature") is not False:
        errors.append("Day135 must not be the next day's feature.")
    if report.get("is_day136") is not False:
        errors.append("Day135 must not be Day136.")
    if report.get("opens_execution_provider_or_api") is not False:
        errors.append("Day135 must not open execution/provider/API.")

    for field in DAY135_DISABLED_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    for source_error in report.get("source_contract_validation_errors", []):
        errors.append(str(source_error))

    for case in report.get("regression_cases", []):
        if case.get("status") != "PASS":
            errors.append(f"Regression case {case.get('case')} did not pass.")

    return errors


def write_ai_provider_disabled_by_default_safety_regression_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_ai_provider_disabled_by_default_safety_regression_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(safe_report, indent=2), encoding="utf-8")
    write_ai_provider_disabled_by_default_safety_regression_html(safe_report, html_path)
    return json_path, html_path


def write_ai_provider_disabled_by_default_safety_regression_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    case_rows = _table_rows(
        (
            case.get("case"),
            case.get("status"),
            case.get("accepted"),
            case.get("rejected"),
            case.get("next_phase_allowed"),
            "; ".join(str(error) for error in case.get("errors", [])) or "none",
        )
        for case in report.get("regression_cases", [])
    )
    write_text_with_parents(
        output_path,
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
  <p><strong>Mode:</strong> {html.escape(str(report['mode']))}</p>
  <p><strong>Scope:</strong> {html.escape(str(report['scope']))}</p>
  <p><strong>Regression verdict:</strong> {html.escape(str(report['regression_verdict']))}</p>
  <h2>Disabled-by-Default Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Regression Cases</h2>
  <table><thead><tr><th>Case</th><th>Status</th><th>Accepted</th><th>Rejected</th><th>Next Phase Allowed</th><th>Errors</th></tr></thead><tbody>{case_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_ai_provider_disabled_by_default_safety_regression(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_ai_provider_disabled_by_default_safety_regression_report(project_root)
    json_path, html_path = write_ai_provider_disabled_by_default_safety_regression_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {REGRESSION_VERDICT}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BLOCKED_VERDICT}")
    return 1


def _source_bool(source_contract: Mapping[str, Any], top_level_name: str, nested_name: str) -> Any:
    if top_level_name in source_contract:
        return source_contract.get(top_level_name)
    disabled_response = source_contract.get("disabled_response", {})
    if isinstance(disabled_response, Mapping) and nested_name in disabled_response:
        return disabled_response.get(nested_name)
    no_execution = source_contract.get("no_execution_evidence", {})
    if isinstance(no_execution, Mapping) and nested_name in no_execution:
        return no_execution.get(nested_name)
    return False


def _case(
    case_name: str,
    description: str,
    accepted: bool,
    errors: Iterable[str],
    expected_rejected: bool = False,
    read_only: bool = False,
) -> Dict[str, Any]:
    rejected = not accepted
    expected = rejected if expected_rejected else accepted
    return {
        "case": case_name,
        "description": description,
        "read_only": read_only,
        "accepted": accepted,
        "rejected": rejected,
        "next_phase_allowed": False,
        "status": "PASS" if expected else "FAIL",
        "errors": list(errors),
    }


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
    report = build_ai_provider_disabled_by_default_safety_regression_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
