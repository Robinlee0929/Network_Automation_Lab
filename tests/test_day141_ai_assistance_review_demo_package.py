import copy
import json
from pathlib import Path

import day141_ai_assistance_review_demo_package as day141
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_TRUE_FIELDS = (
    "review_only",
    "report_only",
    "demo_package_only",
    "deterministic_static_data_only",
    "local_repo_metadata_only",
    "human_reviewer_presentation_only",
)


REQUIRED_FALSE_FIELDS = (
    "execution_allowed",
    "source_execution_allowed",
    "provider_allowed",
    "api_allowed",
    "openai_api_called",
    "ai_provider_called",
    "ai_decision_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "router_switch_command_execution_allowed",
    "adapter_execution_allowed",
    "broker_execution_allowed",
    "runner_execution_allowed",
    "mapped_execution_allowed",
    "configuration_change_allowed",
    "secrets_allowed",
    "credential_handling_allowed",
    "next_phase_allowed",
    "is_next_day_feature",
    "is_day142",
    "future_day_functionality_implemented",
    "execution_provider_api_opened",
    "folder_move_continuation",
    "tmp_cleanup_continuation",
    "project_folder_move_allowed",
    "tmp_cleanup_allowed",
)


def test_day141_report_contains_required_review_only_demo_boundaries():
    report = day141.build_day141_ai_assistance_review_demo_package(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_READY"
    assert report["day"] == 141
    assert report["day_label"] == "Day141"
    assert report["task"] == "ai-assistance-review-demo-package"
    assert report["title"] == "AI Assistance Review Demo Package"
    assert report["mode"] == "REVIEW_ONLY"
    assert report["agents_md_read_before_day141_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["source_execution_commands_run"] == []
    assert report["source_day_range"] == "Day127-Day140"
    assert report["source_artifact_count"] == 14
    assert report["source_artifact_missing_count"] == 0
    assert report["final_recommendation"] == "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE"
    assert report["validation_errors"] == []

    for field in REQUIRED_TRUE_FIELDS:
        assert report[field] is True
        assert report["safety_boundaries"][field] is True
    for field in REQUIRED_FALSE_FIELDS:
        assert report[field] is False
        assert report["safety_boundaries"][field] is False


def test_day141_source_artifacts_are_static_metadata_only_and_ordered_day127_to_day140():
    report = day141.build_day141_ai_assistance_review_demo_package(PROJECT_ROOT)

    assert [item["source_day"] for item in report["source_artifacts"]] == [
        f"Day{day}" for day in range(127, 141)
    ]
    for artifact in report["source_artifacts"]:
        assert artifact["path_exists"] is True
        assert artifact["presentation_mode"] == "metadata_only"
        assert artifact["read_mode"] == "static_reference_only"
        assert artifact["execution_allowed"] is False
        assert artifact["source_execution_allowed"] is False
        assert artifact["provider_allowed"] is False
        assert artifact["api_allowed"] is False
        assert artifact["ai_decision_allowed"] is False
        assert artifact["next_phase_allowed"] is False


def test_day141_negative_validation_blocks_execution_provider_api_future_day_and_cleanup_flags():
    report = day141.build_day141_ai_assistance_review_demo_package(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_read_before_day141_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["source_execution_commands_run"] = ["python network_lab.py --task report-index"]
    unsafe["demo_records"][0]["execution_allowed"] = True
    unsafe["source_artifacts"][0]["source_execution_allowed"] = True
    unsafe["source_artifacts"][0]["provider_allowed"] = True
    unsafe["safety_boundaries"]["next_phase_allowed"] = True

    for field in REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day141.collect_validation_errors(unsafe)

    assert "agents_md_read_before_day141_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors
    assert "source_execution_commands_run must be empty." in errors
    assert "reviewer_entry execution_allowed must be false." in errors
    assert "DAY141_SOURCE_ARTIFACT_01 source_execution_allowed must be false." in errors
    assert "DAY141_SOURCE_ARTIFACT_01 provider_allowed must be false." in errors
    assert "safety_boundaries.next_phase_allowed must be false." in errors
    for field in REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day141_cli_report_and_registry_paths_do_not_activate_execution_provider_api_or_runners(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day141 demo package must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day141 demo package must not load runner profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-assistance-review-demo-package"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-assistance-review-demo-package" in output
    assert "Day141 is not the next day's feature." in output
    assert "Day141 does not open execution / provider / API." in output
    assert "Day141 is not a folder-move continuation." in output
    assert "Day141 is not a tmp cleanup continuation." in output
    assert "Day141 is a review-only demo package." in output
    assert "source_execution_commands_run: []" in output
    assert "final_recommendation: \"REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE\"" in output
    for field in REQUIRED_TRUE_FIELDS:
        assert f"{field}: true" in output
    for field in REQUIRED_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_READY" in output


def test_day141_task_catalog_and_dispatch_are_registered_without_activation():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "ai-assistance-review-demo-package")
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-assistance-review-demo-package"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-assistance-review-demo-package", handlers)

    assert resolve_task_name("ai-assistance-review-demo-package") == "ai-assistance-review-demo-package"
    assert resolved.canonical_name == "ai-assistance-review-demo-package"
    assert callable(resolved.handler)
    assert task["task_id"] == "day141_ai_assistance_review_demo_package"
    assert task["day"] == "Day141"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day141_ai_assistance_review_demo_package.py"
    assert "not Day142" in task["notes"]
    assert "source_execution_allowed=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day141_write_reports_and_report_index_visibility(tmp_path):
    report = day141.build_day141_ai_assistance_review_demo_package(PROJECT_ROOT)
    json_path, html_path = day141.write_day141_ai_assistance_review_demo_package_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert written["status"] == "AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_READY"
    assert written["next_phase_allowed"] is False
    assert "Day141" in index_html
    assert "AI Assistance Review Demo Package" in index_html
    assert "reports/lab-summary/day141_ai_assistance_review_demo_package.json" in index_html


def test_day141_module_does_not_import_network_provider_api_or_execution_surfaces():
    source = Path(day141.__file__).read_text(encoding="utf-8").lower()

    forbidden_fragments = (
        "import os",
        "os.environ",
        "getenv(",
        "import requests",
        "import urllib",
        "import http.client",
        "import socket",
        "import paramiko",
        "import netmiko",
        "import openai",
        "import subprocess",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day141_docs_preserve_required_boundary_statements():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day141_ai_assistance_review_demo_package.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day141_ai_assistance_review_demo_package.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "Day141 is not the next day's feature." in doc
        assert "Day141 does not open execution / provider / API." in doc
        assert "Day141 is not a folder-move continuation." in doc
        assert "Day141 is not a tmp cleanup continuation." in doc
        assert "Day141 is a review-only demo package." in doc
        assert "review_only: true" in doc
        assert "execution_allowed: false" in doc
        assert "source_execution_allowed: false" in doc
        assert "provider_allowed: false" in doc
        assert "api_allowed: false" in doc
        assert "openai_api_called: false" in doc
        assert "ai_decision_allowed: false" in doc
        assert "live_device_access_allowed: false" in doc
        assert "ssh_allowed: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "is_next_day_feature: false" in doc
        assert "folder_move_continuation: false" in doc
        assert "tmp_cleanup_continuation: false" in doc
        assert "REVIEW_ONLY_COMPLETE_KEEP_NEXT_PHASE_FALSE" in doc

    assert "AGENTS.md read before Day141 work | YES" in roadmap
    assert "AGENTS.md pre-read result | PASS" in roadmap
