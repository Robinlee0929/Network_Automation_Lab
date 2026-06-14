"""Day134 disabled AI provider adapter contract.

This module defines the future adapter contract shape for AI summary providers,
but keeps every provider, API, model invocation, network, and execution path
disabled. It produces deterministic reviewer-visible evidence only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Protocol, Tuple


DAY = "Day134"
DAY_NUMBER = 134
TASK_NAME = "disabled-ai-provider-adapter-contract"
TITLE = "Disabled AI Provider Adapter Contract"
FULL_TITLE = f"{DAY} {TITLE}"
OVERALL_STATUS = "PASS"
FAIL_STATUS = "FAIL"
RESULT = "DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day134_disabled_ai_provider_adapter_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day134_disabled_ai_provider_adapter_contract.html"
AI_INTENT_DOC = Path("docs") / "ai-intent" / "day134_disabled_ai_provider_adapter_contract.md"
ROADMAP_DOC = Path("docs") / "roadmap" / "day134_disabled_ai_provider_adapter_contract.md"

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "api_key_required",
    "live_backend_enabled",
    "next_phase_allowed",
    "provider_sdk_required",
    "provider_sdk_imported",
    "environment_config_required",
    "prompt_submission_enabled",
    "model_selection_enabled",
    "async_client_enabled",
    "subprocess_provider_enabled",
    "broker_runner_adapter_execution_enabled",
    "day135_feature_enabled",
)

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "adapter_contract_defined",
    "adapter_is_disabled",
    "deterministic_response",
    "report_only",
    "review_only",
    "local_only",
    "not_next_day_feature",
)

REQUIRED_REPORT_FIELDS: Tuple[str, ...] = (
    "overall_status",
    "result",
    "day",
    "task",
    "title",
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "api_key_required",
    "live_backend_enabled",
    "adapter_is_disabled",
    "next_phase_allowed",
    "not_next_day_feature",
    "contract_message",
    "disabled_response_message",
    "agents_md_status",
)


class DisabledAIProviderAdapter(Protocol):
    """Future adapter shape only; implementations must remain disabled here."""

    name: str
    contract_version: str
    safety: "DisabledAIProviderAdapterSafety"

    def summarize(self, request: "DisabledAIProviderRequest") -> "DisabledAIProviderResponse":
        """Return deterministic disabled evidence without provider invocation."""


@dataclass(frozen=True)
class DisabledAIProviderAdapterSafety:
    provider_enabled: bool = False
    api_enabled: bool = False
    execution_enabled: bool = False
    model_invocation_enabled: bool = False
    network_enabled: bool = False
    api_key_required: bool = False
    live_backend_enabled: bool = False
    adapter_is_disabled: bool = True
    next_phase_allowed: bool = False
    provider_sdk_required: bool = False
    provider_sdk_imported: bool = False
    environment_config_required: bool = False
    prompt_submission_enabled: bool = False
    model_selection_enabled: bool = False
    async_client_enabled: bool = False
    subprocess_provider_enabled: bool = False
    broker_runner_adapter_execution_enabled: bool = False
    day135_feature_enabled: bool = False


@dataclass(frozen=True)
class DisabledAIProviderRequest:
    request_id: str = "day134-disabled-ai-provider-adapter-contract"
    source_summary_schema: str = "Day127 reviewer summary schema"
    source_prompt_contract: str = "Day129 reviewer summary prompt contract"
    redaction_policy_reference: str = "Day130 no-secret policy"
    provider_payload_allowed: bool = False
    provider_payload: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DisabledAIProviderResponse:
    status: str = OVERALL_STATUS
    result: str = RESULT
    provider_name: str = "disabled-ai-provider"
    output_text: str = "Provider adapter contract is defined, disabled, and not invoked."
    provider_invoked: bool = False
    api_called: bool = False
    model_invoked: bool = False
    network_called: bool = False
    execution_path_reached: bool = False
    next_phase_allowed: bool = False


@dataclass(frozen=True)
class DisabledAIProviderAdapterContract:
    name: str = "disabled-ai-provider-adapter"
    contract_version: str = "day134.disabled.v1"
    adapter_contract_defined: bool = True
    deterministic_response: bool = True
    report_only: bool = True
    review_only: bool = True
    local_only: bool = True
    not_next_day_feature: bool = True
    safety: DisabledAIProviderAdapterSafety = DisabledAIProviderAdapterSafety()

    def summarize(self, request: DisabledAIProviderRequest) -> DisabledAIProviderResponse:
        if request.provider_payload_allowed:
            raise RuntimeError("Provider payloads are disabled for Day134.")
        return DisabledAIProviderResponse()


def build_agents_md_status(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day134_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": "AGENTS.md not found.",
        }
    except OSError as exc:
        return {
            "agents_md_status": "MISSING_STOPPED",
            "agents_md_path": "AGENTS.md",
            "agents_md_read_before_day134_work": False,
            "agents_md_required_phrase_present": False,
            "agents_md_read_error": str(exc),
        }

    required_phrase_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_status": "FOUND_AND_READ" if required_phrase_present else "MISSING_STOPPED",
        "agents_md_path": "AGENTS.md",
        "agents_md_read_before_day134_work": required_phrase_present,
        "agents_md_required_phrase_present": required_phrase_present,
        "agents_md_read_error": "",
    }


def build_disabled_ai_provider_adapter_contract() -> DisabledAIProviderAdapterContract:
    return DisabledAIProviderAdapterContract()


def build_disabled_ai_provider_adapter_contract_report(project_root: Path) -> Dict[str, Any]:
    agents_status = build_agents_md_status(project_root)
    contract = build_disabled_ai_provider_adapter_contract()
    request = DisabledAIProviderRequest()
    response = contract.summarize(request)
    safety_fields = asdict(contract.safety)
    response_fields = asdict(response)
    contract_text = [
        "Day134 is not the next day's feature.",
        "This defines only the disabled AI provider adapter contract shape.",
        "No provider/API/model/network/execution path is enabled.",
        "No provider SDK import, API key, environment configuration, subprocess provider, broker, runner, adapter execution, live backend, prompt submission, or model selection is enabled.",
    ]

    report: Dict[str, Any] = {
        "overall_status": "PENDING",
        "result": RESULT,
        "day": DAY,
        "day_number": DAY_NUMBER,
        "task": TASK_NAME,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "adapter_contract_defined": contract.adapter_contract_defined,
        "contract_version": contract.contract_version,
        "adapter_name": contract.name,
        **safety_fields,
        "deterministic_response": contract.deterministic_response,
        "report_only": contract.report_only,
        "review_only": contract.review_only,
        "local_only": contract.local_only,
        "not_next_day_feature": contract.not_next_day_feature,
        "contract_message": "Disabled AI provider adapter contract shape only.",
        "disabled_response_message": response.output_text,
        "contract_request_shape": asdict(request),
        "disabled_response": response_fields,
        "explicit_scope": "Disabled AI provider adapter contract only.",
        "explicit_non_goals": [
            "Not the next day's feature.",
            "No provider implementation.",
            "No OpenAI, Anthropic, Gemini, local LLM, network service, or subprocess provider.",
            "No provider SDK import.",
            "No API key handling.",
            "No environment variable provider configuration.",
            "No HTTP request.",
            "No async provider client.",
            "No model invocation.",
            "No shell command execution.",
            "No broker, runner, or adapter execution path.",
            "No live backend.",
            "No next-phase unlock.",
        ],
        "contract_text": contract_text,
        "no_execution_evidence": {
            "provider_invoked": response.provider_invoked,
            "api_called": response.api_called,
            "model_invoked": response.model_invoked,
            "network_called": response.network_called,
            "execution_path_reached": response.execution_path_reached,
            "provider_payload_allowed": request.provider_payload_allowed,
        },
        "agents_md_status": agents_status["agents_md_status"],
        "agents_md_read_before_day134_work": agents_status["agents_md_read_before_day134_work"],
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
    if report.get("agents_md_read_before_day134_work") is not True:
        errors.append("AGENTS.md must be read before Day134 work.")
    for field in REQUIRED_REPORT_FIELDS:
        if field not in report:
            errors.append(f"{field} is missing.")
    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    if report.get("result") != RESULT:
        errors.append(f"result must be {RESULT}.")
    if report.get("contract_message") != "Disabled AI provider adapter contract shape only.":
        errors.append("contract_message must describe disabled contract shape only.")
    if report.get("disabled_response_message") != "Provider adapter contract is defined, disabled, and not invoked.":
        errors.append("disabled_response_message must be deterministic disabled output.")
    evidence = report.get("no_execution_evidence", {})
    for evidence_name, evidence_value in evidence.items():
        if evidence_value is not False:
            errors.append(f"no-execution evidence {evidence_name} must be false.")
    response = report.get("disabled_response", {})
    if response.get("result") != RESULT:
        errors.append("disabled_response result mismatch.")
    if response.get("next_phase_allowed") is not False:
        errors.append("disabled_response next_phase_allowed must be false.")
    return errors


def write_disabled_ai_provider_adapter_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_disabled_ai_provider_adapter_contract_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_disabled_ai_provider_adapter_contract_html(safe_report, html_path)
    return json_path, html_path


def write_disabled_ai_provider_adapter_contract_html(report: Mapping[str, Any], output_path: Path) -> None:
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
  <p><strong>{html.escape(str(report['contract_message']))}</strong></p>
  <p><strong>{html.escape(str(report['disabled_response_message']))}</strong></p>
  <p><strong>AGENTS.md status:</strong> {html.escape(str(report['agents_md_status']))}</p>
  <h2>Disabled Adapter Contract Summary</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>No-Execution Evidence</h2>
  <table><thead><tr><th>Evidence</th><th>Value</th></tr></thead><tbody>{evidence_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_disabled_ai_provider_adapter_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_disabled_ai_provider_adapter_contract_report(project_root)
    json_path, html_path = write_disabled_ai_provider_adapter_contract_reports(project_root, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(format_heading(FULL_TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"AGENTS.md status: {report['agents_md_status']}")
    print(report["contract_message"])
    print(report["disabled_response_message"])
    for field in REQUIRED_REPORT_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    for field in REQUIRED_FALSE_FIELDS:
        print(f"{field}: {json.dumps(report[field])}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {RESULT}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {RESULT}")
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
    report = build_disabled_ai_provider_adapter_contract_report(Path.cwd())
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
