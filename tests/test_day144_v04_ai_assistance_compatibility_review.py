import copy
import json
from pathlib import Path

import day144_v04_ai_assistance_compatibility_review as day144
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day144_report_contains_required_task_name_and_review_only_boundaries():
    report = day144.build_day144_v04_ai_assistance_compatibility_review(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "V0_4_AI_ASSISTANCE_COMPATIBILITY_REVIEW_READY"
    assert report["day"] == 144
    assert report["day_label"] == "Day144"
    assert report["task"] == "v0.4-ai-assistance-compatibility-review"
    assert report["title"] == "v0.4 AI Assistance Compatibility Review"
    assert report["mode"] == "REVIEW_ONLY_COMPATIBILITY_REVIEW"
    assert report["agents_md_read_before_day144_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["source_day_range"] == "Day127-Day143"
    assert report["source_artifact_count"] == 17
    assert report["source_artifact_missing_count"] == 0
    assert report["compatibility_conclusion"] == (
        "COMPATIBLE_WITH_FUTURE_V0_4_REVIEW_PACKAGE_REVIEW_ONLY"
    )
    assert report["final_recommendation"] == "V0_4_COMPATIBLE_REVIEW_ONLY_KEEP_NEXT_PHASE_FALSE"
    assert report["validation_errors"] == []

    for field in day144.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day144.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day144_source_artifacts_are_static_and_ordered_day127_to_day143():
    report = day144.build_day144_v04_ai_assistance_compatibility_review(PROJECT_ROOT)

    assert [item["source_day"] for item in report["source_artifacts"]] == [
        f"Day{day}" for day in range(127, 144)
    ]
    for artifact in report["source_artifacts"]:
        assert artifact["path_exists"] is True
        assert artifact["review_mode"] == "static_reference_only"
        assert artifact["compatibility_status"] == "PASS"
        assert artifact["execution_allowed"] is False
        assert artifact["provider_allowed"] is False
        assert artifact["api_allowed"] is False
        assert artifact["next_phase_allowed"] is False


def test_day144_negative_validation_blocks_execution_provider_api_day145_and_folder_move_flags():
    report = day144.build_day144_v04_ai_assistance_compatibility_review(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_read_before_day144_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["source_artifacts"][0]["execution_allowed"] = True
    unsafe["source_artifacts"][0]["provider_allowed"] = True
    unsafe["compatibility_checks"][4]["day145_implemented"] = True

    for field in day144.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day144.collect_validation_errors(unsafe)

    assert "agents_md_read_before_day144_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors
    assert "DAY144_SOURCE_ARTIFACT_01 execution_allowed must be false." in errors
    assert "DAY144_SOURCE_ARTIFACT_01 provider_allowed must be false." in errors
    assert "DAY144-COMPAT-005 day145_implemented must be false." in errors
    for field in day144.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day144_cli_does_not_activate_execution_provider_api_folder_move_or_profile_load(
    monkeypatch,
    capsys,
):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day144 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day144 must not load runner profile or config data")

    def fail_day140(*args, **kwargs):
        raise AssertionError("Day144 must not redo Day140 folder move compatibility gate")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day140_folder_move_compatibility_gate", fail_day140)

    exit_code = network_lab.main(
        ["--task", "v0.4-ai-assistance-compatibility-review"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "AGENTS.md pre-read: PASS" in output
    assert "AGENTS.md read before Day144 work: true" in output
    assert "AGENTS.md modified: false" in output
    assert "Day144 task: v0.4 AI Assistance Compatibility Review" in output
    assert "Task slug: v0.4-ai-assistance-compatibility-review" in output
    assert "Day144 is not Day145 and does not implement the next-day feature." in output
    assert "Day144 keeps execution / provider / API closed." in output
    assert "Day144 does not call OpenAI API or any AI provider." in output
    assert "Day144 does not redo the folder move compatibility gate or perform any folder move." in output
    assert "source_day_range: \"Day127-Day143\"" in output
    assert "source_artifact_count: 17" in output
    assert "source_artifact_missing_count: 0" in output
    for field in day144.REQUIRED_TRUE_FIELDS:
        assert f"{field}: true" in output
    for field in day144.REQUIRED_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] V0_4_AI_ASSISTANCE_COMPATIBILITY_REVIEW_READY" in output


def test_day144_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "v0.4-ai-assistance-compatibility-review"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "v0.4-ai-assistance-compatibility-review"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("v0.4-ai-assistance-compatibility-review", handlers)

    assert resolve_task_name("v0.4-ai-assistance-compatibility-review") == (
        "v0.4-ai-assistance-compatibility-review"
    )
    assert resolved.canonical_name == "v0.4-ai-assistance-compatibility-review"
    assert callable(resolved.handler)
    assert task["task_id"] == "day144_v04_ai_assistance_compatibility_review"
    assert task["day"] == "Day144"
    assert task["user_display_name"] == "v0.4 AI Assistance Compatibility Review"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day144_v04_ai_assistance_compatibility_review.py"
    assert "not Day145" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]
    assert "folder_move_compatibility_gate_redone=false" in task["notes"]

    report = day144.build_day144_v04_ai_assistance_compatibility_review(PROJECT_ROOT)
    json_path, html_path = day144.write_day144_v04_ai_assistance_compatibility_review_reports(
        tmp_path,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "V0_4_AI_ASSISTANCE_COMPATIBILITY_REVIEW_READY"
    assert written["next_phase_allowed"] is False
    assert "Day144" in index_html
    assert "v0.4 AI Assistance Compatibility Review" in index_html
    assert "reports/lab-summary/day144_v04_ai_assistance_compatibility_review.json" in index_html


def test_day144_module_does_not_import_network_provider_api_execution_or_folder_move_surfaces():
    source = Path(day144.__file__).read_text(encoding="utf-8").lower()

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
        "import ncclient",
        "routeros_api",
        "intent_folder_move_compatibility_gate",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day144_docs_preserve_required_boundary_statements_and_exact_task_name():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day144_v04_ai_assistance_compatibility_review.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day144_v04_ai_assistance_compatibility_review.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "v0.4 AI Assistance Compatibility Review" in doc
        assert "This is not Day145." in doc or "Day144 is not Day145" in doc
        assert "execution_allowed: false" in doc
        assert "provider_allowed: false" in doc
        assert "api_allowed: false" in doc
        assert "openai_api_called: false" in doc
        assert "ai_provider_called: false" in doc
        assert "execution_runner_behavior_added: false" in doc
        assert "live_device_access_allowed: false" in doc
        assert "ssh_allowed: false" in doc
        assert "netconf_allowed: false" in doc
        assert "restconf_allowed: false" in doc
        assert "routeros_allowed: false" in doc
        assert "environment_provider_activation_allowed: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "day145_implemented: false" in doc
        assert "folder_move_compatibility_gate_redone: false" in doc
        assert "folder_move_performed: false" in doc
        assert "folder_organization_logic_modified: false" in doc
        assert "V0_4_COMPATIBLE_REVIEW_ONLY_KEEP_NEXT_PHASE_FALSE" in doc

    assert "| Task | v0.4 AI Assistance Compatibility Review |" in roadmap
    assert "AGENTS.md read before Day144 work | YES" in roadmap
    assert "AGENTS.md pre-read result | PASS" in roadmap
