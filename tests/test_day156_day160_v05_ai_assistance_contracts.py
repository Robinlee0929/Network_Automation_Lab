import copy
import json
from pathlib import Path

import day156_v05_ai_assistance_input_boundary_contract as day156
import day157_v05_ai_assistance_output_template_contract as day157
import day158_v05_ai_assistance_reviewer_only_fixture_renderer as day158
import day159_v05_ai_assistance_safety_regression_matrix as day159
import day160_v05_ai_assistance_phase_gate_review as day160
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name
from v05_ai_assistance_contracts import REQUIRED_FALSE_FIELDS, REQUIRED_TRUE_FIELDS


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DAY_MODULES = [
    (
        day156,
        day156.build_day156_v05_ai_assistance_input_boundary_contract,
        "v05-ai-assistance-input-boundary-contract",
        "V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY",
        156,
        "input_boundary_contract",
    ),
    (
        day157,
        day157.build_day157_v05_ai_assistance_output_template_contract,
        "v05-ai-assistance-output-template-contract",
        "V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY",
        157,
        "output_template_contract",
    ),
    (
        day158,
        day158.build_day158_v05_ai_assistance_reviewer_only_fixture_renderer,
        "v05-ai-assistance-reviewer-only-fixture-renderer",
        "V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_REVIEW_READY",
        158,
        "reviewer_only_fixture_renderer",
    ),
    (
        day159,
        day159.build_day159_v05_ai_assistance_safety_regression_matrix,
        "v05-ai-assistance-safety-regression-matrix",
        "V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_REVIEW_READY",
        159,
        "safety_regression_matrix",
    ),
    (
        day160,
        day160.build_day160_v05_ai_assistance_phase_gate_review,
        "v05-ai-assistance-phase-gate-review",
        "V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_READY",
        160,
        "phase_gate_review",
    ),
]


def test_day156_day160_reports_are_review_only_non_executable_contracts():
    for module, builder, task_name, status_label, day, contract_type in DAY_MODULES:
        report = builder(PROJECT_ROOT)

        assert report["overall_status"] == "PASS"
        assert report["status"] == "REVIEW_READY"
        assert report["day"] == day
        assert report["task"] == task_name
        assert report["status_label"] == status_label
        assert report["contract_type"] == contract_type
        assert report["agents_md_pre_read"] == "YES"
        assert report["agents_md_result"] == "FOUND_AND_READ"
        assert report["agents_md_modified"] is False
        assert report["validation_errors"] == []
        assert report["contract_records"]
        assert report["acceptance_checks"]

        for field in REQUIRED_TRUE_FIELDS:
            assert report[field] is True
        for field in REQUIRED_FALSE_FIELDS:
            assert report[field] is False

        for record in report["contract_records"]:
            assert record["status"] == "PASS"
            assert record["review_only"] is True
            assert record["report_only"] is True
            assert record["execution_allowed"] is False
            assert record["next_phase_allowed"] is False

        for check in report["acceptance_checks"]:
            assert check["status"] == "PASS"
            assert check["blocks_execution_unlock"] is True

        assert report["forbidden_capability_scan"]["status"] == "PASS"
        assert report["forbidden_capability_scan"]["provider_api_live_device_activation_found"] is False
        assert report["forbidden_capability_scan"]["direct_command_generation_found"] is False
        assert report["forbidden_capability_scan"]["secrets_access_found"] is False
        assert report["forbidden_capability_scan"]["executor_unlock_found"] is False
        assert report["safety_boundary_regression"]["next_phase_allowed"] is False
        assert report["result_semantics"]["ai_execution_allowed"] is False
        assert report["result_semantics"]["provider_api_integration_allowed"] is False
        assert report["result_semantics"]["executor_can_act_on_ai_output"] is False
        assert report["result_semantics"]["next_phase_allowed"] is False
        assert module.collect_validation_errors(report) == []


def test_day156_day160_reference_records_cover_docs_registry_dispatch_and_report_index():
    for _module, builder, _task_name, _status_label, _day, _contract_type in DAY_MODULES:
        report = builder(PROJECT_ROOT)

        for record in report["reference_records"]:
            assert record["path_exists"] is True
            assert record["all_required_fragments_present"] is True
            assert record["missing_fragments"] == []
            assert record["review_only"] is True
            assert record["report_only"] is True
            assert record["next_phase_allowed"] is False


def test_day156_day160_negative_validation_blocks_unsafe_values():
    for module, builder, _task_name, _status_label, _day, _contract_type in DAY_MODULES:
        unsafe = copy.deepcopy(builder(PROJECT_ROOT))
        unsafe["agents_md_pre_read"] = "NO"
        unsafe["agents_md_result"] = "MISSING"
        unsafe["agents_md_modified"] = True
        unsafe["contract_records"][0]["status"] = "FAIL"
        unsafe["contract_records"][0]["review_only"] = False
        unsafe["contract_records"][0]["report_only"] = False
        unsafe["contract_records"][0]["execution_allowed"] = True
        unsafe["contract_records"][0]["next_phase_allowed"] = True
        unsafe["acceptance_checks"][0]["status"] = "FAIL"
        unsafe["acceptance_checks"][0]["blocks_execution_unlock"] = False
        unsafe["forbidden_capability_scan"]["direct_command_generation_found"] = True
        unsafe["safety_boundary_regression"]["execution_allowed"] = True
        unsafe["safety_boundary_regression"]["next_phase_allowed"] = True
        unsafe["result_semantics"]["ai_execution_allowed"] = True
        unsafe["reference_records"][0]["path_exists"] = False
        unsafe["reference_records"][0]["missing_fragments"] = ["next_phase_allowed: false"]

        for field in REQUIRED_FALSE_FIELDS:
            unsafe[field] = True
        for field in REQUIRED_TRUE_FIELDS:
            unsafe[field] = False

        errors = module.collect_validation_errors(unsafe)

        assert "agents_md_pre_read must be YES." in errors
        assert "agents_md_result must be FOUND_AND_READ." in errors
        assert "agents_md_modified must be false." in errors
        assert "forbidden_capability_scan unsafe findings must all be false." in errors
        assert "safety_boundary_regression.execution_allowed must be false." in errors
        assert "safety_boundary_regression.next_phase_allowed must be false." in errors
        assert "result_semantics.ai_execution_allowed must be false." in errors
        for field in REQUIRED_FALSE_FIELDS:
            assert f"{field} must be false." in errors
        for field in REQUIRED_TRUE_FIELDS:
            assert f"{field} must be true." in errors


def test_day156_day160_cli_does_not_execute_subprocess_profile_or_live_paths(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("v0.5 AI Assistance contract tasks must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("v0.5 AI Assistance contract tasks must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    for _module, _builder, task_name, status_label, day, _contract_type in DAY_MODULES:
        exit_code = network_lab.main(["--task", task_name], project_root=PROJECT_ROOT)
        output = capsys.readouterr().out

        assert exit_code == 0
        assert "AGENTS.md pre-read: YES" in output
        assert "AGENTS.md result: FOUND_AND_READ" in output
        assert "AGENTS.md modified: false" in output
        assert f"Task slug: {task_name}" in output
        assert f"day: {day}" in output
        assert f"status_label: {status_label}" in output
        assert "execution_allowed: false" in output
        assert "provider_allowed: false" in output
        assert "api_allowed: false" in output
        assert "openai_api_call_allowed: false" in output
        assert "external_api_call_allowed: false" in output
        assert "live_device_allowed: false" in output
        assert "command_execution_allowed: false" in output
        assert "executor_unlock_allowed: false" in output
        assert "secrets_allowed: false" in output
        assert "phase_gate_approval: false" in output
        assert "next_phase_allowed: false" in output
        assert "forbidden_capability_scan: PASS" in output
        assert "safety_boundary_regression: PASS" in output
        assert f"[PASS] {status_label}" in output


def test_day156_day160_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    parser = network_lab_cli_dispatch._build_parser(network_lab)

    writers = {
        "v05-ai-assistance-input-boundary-contract": day156.write_day156_v05_ai_assistance_input_boundary_contract_reports,
        "v05-ai-assistance-output-template-contract": day157.write_day157_v05_ai_assistance_output_template_contract_reports,
        "v05-ai-assistance-reviewer-only-fixture-renderer": day158.write_day158_v05_ai_assistance_reviewer_only_fixture_renderer_reports,
        "v05-ai-assistance-safety-regression-matrix": day159.write_day159_v05_ai_assistance_safety_regression_matrix_reports,
        "v05-ai-assistance-phase-gate-review": day160.write_day160_v05_ai_assistance_phase_gate_review_reports,
    }

    for _module, builder, task_name, status_label, day, _contract_type in DAY_MODULES:
        task = next(task for task in network_lab.list_tasks() if task["id"] == task_name)
        args = parser.parse_args(["--task", task_name])
        handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
        resolved = resolve_task_handler(task_name, handlers)

        assert resolve_task_name(task_name) == task_name
        assert resolved.canonical_name == task_name
        assert callable(resolved.handler)
        assert task["day"] == f"Day{day}"
        assert task["user_display_name"].startswith("v0.5 AI Assistance")
        assert task["safety_level"] == "report-only"
        assert task["execution_mode"] == "report-only"
        assert task["requires_live_device"] is False
        assert task["requires_password"] is False
        assert "NEXT_PHASE_ALLOWED_FALSE" in task["notes"]

        report = builder(PROJECT_ROOT)
        json_path, html_path = writers[task_name](tmp_path, report)
        written = json.loads(json_path.read_text(encoding="utf-8"))

        assert json_path.exists()
        assert html_path.exists()
        assert written["day"] == day
        assert written["status_label"] == status_label
        assert written["next_phase_allowed"] is False
        assert written["execution_allowed"] is False
        assert written["provider_allowed"] is False
        assert written["api_allowed"] is False

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")

    assert exit_code == 0
    for _module, _builder, _task_name, _status_label, day, _contract_type in DAY_MODULES:
        assert f"Day{day}" in index_html
    assert "v0.5 AI Assistance Input Boundary Contract" in index_html
    assert "v0.5 AI Assistance Output Template Contract" in index_html
    assert "v0.5 AI Assistance Reviewer-Only Fixture Renderer" in index_html
    assert "v0.5 AI Assistance Safety Regression Matrix" in index_html
    assert "v0.5 AI Assistance Phase Gate Review" in index_html


def test_day156_day160_docs_preserve_v05_boundaries():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    ai_readme = (PROJECT_ROOT / "docs/ai-intent/README.md").read_text(encoding="utf-8")

    assert "Current project status after Day160" in readme
    assert "V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_READY" in readme
    assert "NEXT_PHASE_ALLOWED_FALSE" in readme
    assert "## Day160" in ai_readme
    assert "next_phase_allowed=false" in ai_readme

    for _module, _builder, task_name, status_label, day, _contract_type in DAY_MODULES:
        roadmap = (PROJECT_ROOT / f"docs/roadmap/day{day}_{task_name.replace('-', '_')}.md").read_text(
            encoding="utf-8"
        )
        ai_doc = (PROJECT_ROOT / f"docs/ai/day{day}_{task_name.replace('-', '_')}.md").read_text(
            encoding="utf-8"
        )

        for doc in (roadmap, ai_doc):
            assert task_name in doc
            assert status_label in doc
            assert "execution_allowed: false" in doc
            assert "provider_allowed: false" in doc
            assert "api_allowed: false" in doc
            assert "live_device_allowed: false" in doc
            assert "secrets_allowed: false" in doc
            assert "phase_gate_approval: false" in doc
            assert "next_phase_allowed: false" in doc
