"""Day133 disabled AI provider interface boundary.

This module creates reviewer-visible evidence for a disabled AI provider
interface boundary. It is not an adapter contract and it does not enable
execution, providers, APIs, SDKs, secrets, network calls, or model selection.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


DAY = "Day133"
DAY_NUMBER = 133
TASK_NAME = "disabled-ai-provider-interface-boundary"
TITLE = "Disabled AI Provider Interface Boundary"
FULL_TITLE = f"{DAY} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
BOUNDARY_STATUS = "AI_PROVIDER_INTERFACE_DISABLED"
REPORT_JSON = Path("reports") / "lab-summary" / "day133_disabled_ai_provider_interface_boundary.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day133_disabled_ai_provider_interface_boundary.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day133_disabled_ai_provider_interface_boundary.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day133_disabled_ai_provider_interface_boundary.md"

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "provider_enabled",
    "execution_enabled",
    "api_enabled",
    "network_call_enabled",
    "secrets_required",
    "external_sdk_required",
    "live_ai_call_enabled",
    "adapter_contract_enabled",
    "day134_feature_enabled",
    "next_day_feature_enabled",
    "provider_adapter_enabled",
    "vendor_sdk_integration_enabled",
    "prompt_submission_enabled",
    "model_selection_enabled",
    "retry_rate_limit_timeout_behavior_enabled",
    "async_job_enabled",
)

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "provider_interface_boundary_created",
    "review_only",
    "deterministic_only",
    "local_only",
    "report_only",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "boundary_status",
    "day",
    "task",
    "title",
    "provider_interface_boundary_created",
    "provider_enabled",
    "execution_enabled",
    "api_enabled",
    "network_call_enabled",
    "secrets_required",
    "external_sdk_required",
    "live_ai_call_enabled",
    "adapter_contract_enabled",
    "day134_feature_enabled",
    "next_day_feature_enabled",
    "review_only",
    "boundary_message",
    "no_execution_message",
    "agents_md_status",
)


@dataclass(frozen=True)
class DisabledAIProviderInterfaceBoundary:
    provider_interface_boundary_created: bool = True
    provider_enabled: bool = False
    execution_enabled: bool = False
    api_enabled: bool = False
    network_call_enabled: bool = False
    secrets_required: bool = False
    external_sdk_required: bool = False
    live_ai_call_enabled: bool = False
    adapter_contract_enabled: bool = False
    day134_feature_enabled: bool = False
    next_day_feature_enabled: bool = False
    provider_adapter_enabled: bool = False
    vendor_sdk_integration_enabled: bool = False
    prompt_submission_enabled: bool = False
    model_selection_enabled: bool = False
    retry_rate_limit_timeout_behavior_enabled: bool = False
    async_job_enabled: bool = False
    review_only: bool = True
    deterministic_only: bool = True
    local_only: bool = True
    report_only: bool = True


def build_agents_md_status(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day133_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": "AGENTS.md not found.",
        }
    except OSError as exc:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day133_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": str(exc),
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_status": "FOUND_AND_READ" if required_phrase_present else "MISSING_STOPPED",
        "agents_md_path": "AGENTS.md",
        "agents_md_read_before_day133_work": required_phrase_present,
        "agents_md_required_phrase_present": required_phrase_present,
        "agents_md_read_error": "",
    }


def build_disabled_ai_provider_interface_boundary() -> DisabledAIProviderInterfaceBoundary:
    return DisabledAIProviderInterfaceBoundary()


def build_disabled_ai_provider_interface_boundary_report(project_root: Path) -> Dict[str, Any]:
    agents_status = build_agents_md_status(project_root)
    boundary = build_disabled_ai_provider_interface_boundary()
    boundary_fields = asdict(boundary)
    boundary_text = [
        "Day133 is not the next-day feature.",
        "This is not Day134 adapter contract.",
        "No execution/provider/API is enabled.",
        "No provider adapter, vendor SDK, external API, API key, secret, network call, live AI call, prompt submission, model selection, async job, retry, rate limit, or timeout provider behavior is enabled.",
    ]

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "boundary_status": BOUNDARY_STATUS,
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        **boundary_fields,
        "boundary_message": "This is not Day134 adapter contract.",
        "no_execution_message": "No execution/provider/API is enabled.",
        "explicit_scope": "Disabled AI provider interface boundary only.",
        "explicit_non_goals": [
            "Not Day134 adapter contract.",
            "No provider adapter implementation.",
            "No OpenAI provider implementation.",
            "No Gemini provider implementation.",
            "No Claude provider implementation.",
            "No vendor SDK integration.",
            "No external API call.",
            "No API key read.",
            "No secrets added.",
            "No live provider execution.",
            "No async job or background execution.",
            "No retry, rate limit, or timeout provider behavior.",
            "No prompt submission.",
            "No model selection.",
            "No network call.",
            "No execution/provider/API switch.",
        ],
        "boundary_text": boundary_text,
        "no_execution_evidence": {
            "adapter_contract_path_opened": False,
            "provider_adapter_path_opened": False,
            "provider_api_path_opened": False,
            "external_sdk_path_opened": False,
            "secret_lookup_path_opened": False,
            "network_path_opened": False,
            "live_ai_call_path_opened": False,
            "prompt_submission_path_opened": False,
            "model_selection_path_opened": False,
            "background_execution_path_opened": False,
        },
        "agents_md_status": agents_status["agents_md_status"],
        "agents_md_read_before_day133_work": agents_status["agents_md_read_before_day133_work"],
        "agents_md_path": agents_status["agents_md_path"],
        "agents_md_evidence": agents_status,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "validation_errors": [],
    }
    report["validation_errors"] = collect_validation_errors(report)
    report["overall_status"] = OVERALL_STATUS if not report["validation_errors"] else FAIL_STATUS
    return report


def collect_validation_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("agents_md_status") != "FOUND_AND_READ":
        errors.append("AGENTS.md status must be FOUND_AND_READ.")
    if report.get("agents_md_read_before_day133_work") is not True:
        errors.append("AGENTS.md must be read before Day133 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if report.get("boundary_message") != "This is not Day134 adapter contract.":
        errors.append("boundary_message must state that this is not Day134 adapter contract.")
    if report.get("no_execution_message") != "No execution/provider/API is enabled.":
        errors.append("no_execution_message must state that no execution/provider/API is enabled.")
    if report.get("boundary_status") != BOUNDARY_STATUS:
        errors.append(f"boundary_status must be {BOUNDARY_STATUS}.")
    evidence = report.get("no_execution_evidence", {})
    for evidence_name, evidence_value in evidence.items():
        if evidence_value is not False:
            errors.append(f"no-execution evidence {evidence_name} must be false.")
    return errors


def write_disabled_ai_provider_interface_boundary_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_disabled_ai_provider_interface_boundary_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_disabled_ai_provider_interface_boundary_html(safe_report, html_path)
    return json_path, html_path


def write_disabled_ai_provider_interface_boundary_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows((field, report[field]) for field in REQUIRED_REPORT_FIELDS)
    evidence_rows = _table_rows(report.get("no_execution_evidence", {}).items())
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
  <p><strong>{html.escape(str(report['boundary_message']))}</strong></p>
  <p><strong>{html.escape(str(report['no_execution_message']))}</strong></p>
  <p><strong>AGENTS.md status:</strong> {html.escape(str(report['agents_md_status']))}</p>
  <h2>Disabled Boundary Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>No-Execution Evidence</h2>
  <table><thead><tr><th>Evidence</th><th>Value</th></tr></thead><tbody>{evidence_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_disabled_ai_provider_interface_boundary(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_disabled_ai_provider_interface_boundary_report(project_root)
    json_path, html_path = write_disabled_ai_provider_interface_boundary_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(report["boundary_message"])
    print(report["no_execution_message"])
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    for field in REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {BOUNDARY_STATUS}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {BOUNDARY_STATUS}")
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
    report = build_disabled_ai_provider_interface_boundary_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
