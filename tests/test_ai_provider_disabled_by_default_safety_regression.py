import json
from copy import deepcopy
from pathlib import Path

import ai_provider_disabled_by_default_safety_regression as day135
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name
from report_file_utils import path_exists, read_text_with_long_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


DISABLED_FIELDS = (
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


NEGATIVE_FIELDS = (
    "provider_enabled",
    "api_enabled",
    "execution_enabled",
    "model_invocation_enabled",
    "network_enabled",
    "provider_instantiated",
    "api_called",
    "execution_invoked",
)


def _write_agents_md(root: Path) -> None:
    (root / "AGENTS.md").write_text(
        "# AGENTS.md\n\n## Core Safety Rules\n\n## Standard Validation\n",
        encoding="utf-8",
    )


def _day134_evidence() -> dict:
    return json.loads((PROJECT_ROOT / day135.SOURCE_CONTRACT_JSON).read_text(encoding="utf-8"))


def _write_day134_evidence(root: Path, evidence: dict) -> Path:
    path = root / day135.SOURCE_CONTRACT_JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return path


def test_day135_accepts_day134_disabled_contract_as_read_only_evidence():
    report = day135.build_ai_provider_disabled_by_default_safety_regression_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["regression_verdict"] == "DISABLED_BY_DEFAULT_PRESERVED"
    assert report["day"] == 135
    assert report["task"] == "ai-provider-disabled-by-default-safety-regression"
    assert report["mode"] == "REVIEW_ONLY"
    assert report["scope"] == "DISABLED_BY_DEFAULT_SAFETY_REGRESSION"
    assert report["source_contract_day"] == 134
    assert report["source_contract_read"] is True
    assert report["source_contract_read_only"] is True
    assert report["consumer_read_allowed"] is True
    assert report["is_next_day_feature"] is False
    assert report["is_day136"] is False
    assert report["opens_execution_provider_or_api"] is False
    assert report["agents_md_pre_read"] == "YES"
    assert report["agents_md_path"] == "AGENTS.md"
    assert report["agents_md_modified"] is False
    assert report["validation_errors"] == []

    for field in DISABLED_FIELDS:
        assert report[field] is False


def test_day135_regression_cases_cover_required_accept_and_reject_paths():
    report = day135.build_ai_provider_disabled_by_default_safety_regression_report(PROJECT_ROOT)
    cases = {case["case"]: case for case in report["regression_cases"]}

    assert cases["baseline_day134_disabled_provider_contract"]["accepted"] is True
    assert cases["consumer_read_only_inspection"]["accepted"] is True
    assert cases["consumer_read_only_inspection"]["read_only"] is True
    assert cases["missing_or_unreadable_day134_evidence_rejected"]["rejected"] is True
    assert cases["missing_or_unreadable_day134_evidence_rejected"]["next_phase_allowed"] is False

    for field in NEGATIVE_FIELDS:
        case = cases[f"{field}_true_rejected"]
        assert case["status"] == "PASS"
        assert case["accepted"] is False
        assert case["rejected"] is True
        assert case["next_phase_allowed"] is False


def test_day135_rejects_each_enabled_or_invoked_flag(tmp_path):
    _write_agents_md(tmp_path)
    evidence = _day134_evidence()

    for field in NEGATIVE_FIELDS:
        mutated = deepcopy(evidence)
        mutated[field] = True
        _write_day134_evidence(tmp_path, mutated)

        report = day135.build_ai_provider_disabled_by_default_safety_regression_report(tmp_path)

        assert report["overall_status"] == "FAIL"
        assert report["regression_verdict"] == "DISABLED_BY_DEFAULT_REGRESSION_BLOCKED"
        assert report["consumer_read_allowed"] is False
        assert report["next_phase_allowed"] is False
        assert report["provider_instantiated"] is False
        assert report["api_called"] is False
        assert report["execution_invoked"] is False
        assert any(field in error for error in report["validation_errors"])


def test_day135_missing_or_unreadable_day134_evidence_does_not_advance(tmp_path):
    _write_agents_md(tmp_path)

    report = day135.build_ai_provider_disabled_by_default_safety_regression_report(tmp_path)

    assert report["overall_status"] == "FAIL"
    assert report["source_contract_read"] is False
    assert report["consumer_read_allowed"] is False
    assert report["next_phase_allowed"] is False
    assert report["regression_verdict"] == "DISABLED_BY_DEFAULT_REGRESSION_BLOCKED"


def test_day135_cli_report_and_registry_paths_do_not_activate_provider_api_or_execution(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day135 regression must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day135 regression must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-provider-disabled-by-default-safety-regression"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-provider-disabled-by-default-safety-regression" in output
    assert "mode: \"REVIEW_ONLY\"" in output
    assert "scope: \"DISABLED_BY_DEFAULT_SAFETY_REGRESSION\"" in output
    assert "regression_verdict: \"DISABLED_BY_DEFAULT_PRESERVED\"" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "execution_enabled: false" in output
    assert "model_invocation_enabled: false" in output
    assert "network_enabled: false" in output
    assert "provider_instantiated: false" in output
    assert "api_called: false" in output
    assert "execution_invoked: false" in output
    assert "registry_activation_allowed: false" in output
    assert "cli_activation_allowed: false" in output
    assert "report_activation_allowed: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] DISABLED_BY_DEFAULT_PRESERVED" in output


def test_day135_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-provider-disabled-by-default-safety-regression"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-provider-disabled-by-default-safety-regression"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-provider-disabled-by-default-safety-regression", handlers)

    assert resolve_task_name("ai-provider-disabled-by-default-safety-regression") == (
        "ai-provider-disabled-by-default-safety-regression"
    )
    assert resolved.canonical_name == "ai-provider-disabled-by-default-safety-regression"
    assert callable(resolved.handler)
    assert task["task_id"] == "day135_ai_provider_disabled_by_default_safety_regression"
    assert task["day"] == "Day135"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "ai_provider_disabled_by_default_safety_regression.py"
    assert "not Day136" in task["notes"]
    assert "read-only regression case" in task["notes"]
    assert "does not instantiate providers" in task["notes"]


def test_day135_write_reports_and_report_index_visibility(tmp_path):
    _write_agents_md(tmp_path)
    _write_day134_evidence(tmp_path, _day134_evidence())
    report = day135.build_ai_provider_disabled_by_default_safety_regression_report(tmp_path)
    json_path, html_path = day135.write_ai_provider_disabled_by_default_safety_regression_reports(
        tmp_path,
        report,
    )

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = read_text_with_long_path(tmp_path / "reports" / "report_index.html", encoding="utf-8")
    written = json.loads(read_text_with_long_path(json_path, encoding="utf-8"))

    assert exit_code == 0
    assert path_exists(json_path)
    assert path_exists(html_path)
    assert written["overall_status"] == "PASS"
    assert written["regression_verdict"] == "DISABLED_BY_DEFAULT_PRESERVED"
    assert "Day135" in index_html
    assert "AI Provider Disabled-by-Default Safety Regression" in index_html


def test_day135_docs_exist_and_preserve_corrected_scope():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day135_ai_provider_disabled_by_default_safety_regression.md",
        PROJECT_ROOT / "docs/roadmap/day135_ai_provider_disabled_by_default_safety_regression.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8").lower()
        assert "ai provider disabled-by-default safety regression" in text
        assert "not day136" in text
        assert "not the next day's feature" in text
        assert "consumer" in text
        assert "read-only regression case" in text
        assert "provider_enabled: false" in text
        assert "api_enabled: false" in text
        assert "execution_enabled: false" in text
        assert "model_invocation_enabled: false" in text
        assert "network_enabled: false" in text
        assert "provider_instantiated: false" in text
        assert "api_called: false" in text
        assert "execution_invoked: false" in text
        assert "registry_activation_allowed: false" in text
        assert "cli_activation_allowed: false" in text
        assert "report_activation_allowed: false" in text
        assert "next_phase_allowed: false" in text
