import copy
import json
from pathlib import Path

import day146_v04_ai_assistance_non_advancement_gate as day146
import network_lab
import network_lab_cli_dispatch
from ai_assistance_evidence_test_fixtures import build_deterministic_ai_assistance_evidence_root
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _day145_paths(project_root):
    day145_record = next(item for item in day146.SOURCE_ARTIFACTS if item["day"] == "Day145")
    return [project_root / path for path in day145_record["paths"]]


def _sha256(path):
    return day146._sha256_file(path)


def test_day146_report_contains_non_advancement_scope_and_review_only_boundaries(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day146.build_day146_v04_ai_assistance_non_advancement_gate(evidence_root)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY"
    assert report["day"] == 146
    assert report["day_label"] == "Day146"
    assert report["task"] == "v0.4-ai-assistance-non-advancement-gate"
    assert report["title"] == "v0.4 AI Assistance Non-Advancement Gate"
    assert report["mode"] == "REVIEW_ONLY_NON_ADVANCEMENT_GATE"
    assert report["agents_md_read_before_day146_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["non_advancement_scope"] == "Day127-Day145"
    assert report["included_day_range"] == [f"Day{day}" for day in range(127, 146)]
    assert report["frozen_reference_commit_hash"] == "ddefb46e045df5310634ad307937f81c9f08e6cb"
    assert report["source_artifact_count"] == 19
    assert report["source_artifact_missing_count"] == 0
    assert report["final_recommendation"] == (
        "KEEP_DAY127_DAY145_V0_4_AI_ASSISTANCE_FROZEN_AND_NEXT_PHASE_FALSE"
    )
    assert report["validation_errors"] == []

    for field in day146.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day146.REQUIRED_FALSE_FIELDS:
        assert report[field] is False


def test_day146_source_artifacts_are_static_ordered_day127_to_day145_and_not_write_targets(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day146.build_day146_v04_ai_assistance_non_advancement_gate(evidence_root)

    assert [item["source_day"] for item in report["source_artifacts"]] == [
        f"Day{day}" for day in range(127, 146)
    ]
    for artifact in report["source_artifacts"]:
        assert artifact["all_paths_exist"] is True
        assert artifact["review_mode"] == "static_reference_only"
        assert artifact["gate_status"] == "LOCKED"
        assert artifact["write_target"] is False
        assert artifact["rerun_allowed"] is False
        assert artifact["rewrite_allowed"] is False
        assert artifact["repair_allowed"] is False
        assert artifact["execution_allowed"] is False
        assert artifact["provider_allowed"] is False
        assert artifact["api_allowed"] is False
        assert artifact["next_phase_allowed"] is False


def test_day146_day145_artifacts_are_frozen_input_only_and_not_modified_by_cli(
    tmp_path, monkeypatch, capsys
):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    before_hashes = {path.as_posix(): _sha256(path) for path in _day145_paths(evidence_root)}

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day146 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day146 must not load runner profile or config data")

    def fail_day145(*args, **kwargs):
        raise AssertionError("Day146 must not rerun Day145")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day145_v04_ai_assistance_evidence_freeze_package", fail_day145)

    exit_code = network_lab.main(
        ["--task", "v0.4-ai-assistance-non-advancement-gate"],
        project_root=evidence_root,
    )
    output = capsys.readouterr().out
    after_hashes = {path.as_posix(): _sha256(path) for path in _day145_paths(evidence_root)}

    assert exit_code == 0
    assert before_hashes == after_hashes
    assert "Day145 is frozen input only and was not rerun, rewritten, repaired, or modified." in output
    assert "Day146 is a non-advancement gate and does not implement Day147 or any next phase." in output
    assert "Day146 does not call providers, APIs, OpenAI API, or models." in output
    assert "Day146 does not invoke runners, brokers, adapters, execution paths, or mapped tasks." in output
    assert "Day146 does not use SSH, NETCONF, RESTCONF, RouterOS, live devices, or real network access." in output
    assert "Day146 performs no folder move, rename, relocation, cleanup, or git clean." in output
    assert "Day146 keeps next_phase_allowed=false and execution_provider_api_phase_advanced=false." in output
    assert "non_advancement_scope: \"Day127-Day145\"" in output
    assert "frozen_reference_commit_hash: \"ddefb46e045df5310634ad307937f81c9f08e6cb\"" in output
    assert "source_artifact_count: 19" in output
    for field in day146.REQUIRED_FALSE_FIELDS:
        assert f"{field}: false" in output
    assert "[PASS] V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY" in output


def test_day146_negative_validation_blocks_unsafe_flags_day145_mutation_and_next_phase(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    report = day146.build_day146_v04_ai_assistance_non_advancement_gate(evidence_root)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_read_before_day146_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["source_artifacts"][-1]["write_target"] = True
    unsafe["day145_frozen_artifacts"][0]["rerun_allowed"] = True
    unsafe["non_advancement_checks"][1]["day145_modified"] = True
    unsafe["non_advancement_checks"][4]["next_phase_allowed"] = True
    unsafe["non_advancement_checks"][4]["day147_implemented"] = True

    for field in day146.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day146.collect_validation_errors(unsafe)

    assert "agents_md_read_before_day146_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors
    assert "DAY146_NON_ADVANCEMENT_SOURCE_19 write_target must be false." in errors
    assert "Day145 frozen artifact rerun_allowed must be false." in errors
    assert "DAY146-NON-ADVANCE-002 day145_modified must be false." in errors
    assert "DAY146-NON-ADVANCE-005 next_phase_allowed must be false." in errors
    assert "DAY146-NON-ADVANCE-005 day147_implemented must be false." in errors
    for field in day146.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day146_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    evidence_root = build_deterministic_ai_assistance_evidence_root(tmp_path, PROJECT_ROOT)
    task = next(
        task for task in network_lab.list_tasks() if task["id"] == "v0.4-ai-assistance-non-advancement-gate"
    )
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "v0.4-ai-assistance-non-advancement-gate"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("v0.4-ai-assistance-non-advancement-gate", handlers)

    assert resolve_task_name("v0.4-ai-assistance-non-advancement-gate") == (
        "v0.4-ai-assistance-non-advancement-gate"
    )
    assert resolved.canonical_name == "v0.4-ai-assistance-non-advancement-gate"
    assert callable(resolved.handler)
    assert task["task_id"] == "day146_v04_ai_assistance_non_advancement_gate"
    assert task["day"] == "Day146"
    assert task["user_display_name"] == "v0.4 AI Assistance Non-Advancement Gate"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day146_v04_ai_assistance_non_advancement_gate.py"
    assert "Day127-Day145" in task["notes"]
    assert "Day145 frozen input only" in task["notes"]
    assert "day147_implemented=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]

    report = day146.build_day146_v04_ai_assistance_non_advancement_gate(evidence_root)
    json_path, html_path = day146.write_day146_v04_ai_assistance_non_advancement_gate_reports(
        evidence_root,
        report,
    )
    exit_code = network_lab.main(["--report-index"], project_root=evidence_root)
    index_html = (evidence_root / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY"
    assert written["next_phase_allowed"] is False
    assert written["day147_implemented"] is False
    assert "Day146" in index_html
    assert "v0.4 AI Assistance Non-Advancement Gate" in index_html
    assert "reports/lab-summary/day146_v04_ai_assistance_non_advancement_gate.json" in index_html


def test_day146_module_does_not_import_network_provider_api_execution_or_cleanup_surfaces():
    source = Path(day146.__file__).read_text(encoding="utf-8").lower()

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
        "remove-item",
        "rmtree",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day146_docs_preserve_required_non_advancement_boundary_statements_and_task_name():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day146_v04_ai_assistance_non_advancement_gate.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day146_v04_ai_assistance_non_advancement_gate.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "v0.4 AI Assistance Non-Advancement Gate" in doc
        assert "Day127-Day145" in doc
        assert "ddefb46e045df5310634ad307937f81c9f08e6cb" in doc
        assert "Day145 is frozen input only" in doc
        assert "day145_untouched: true" in doc
        assert "ai_assistance_non_advancement_gate: true" in doc
        assert "execution_allowed: false" in doc
        assert "provider_allowed: false" in doc
        assert "api_allowed: false" in doc
        assert "openai_api_called: false" in doc
        assert "ai_provider_called: false" in doc
        assert "model_invocation_allowed: false" in doc
        assert "mapped_task_execution_allowed: false" in doc
        assert "live_device_access_allowed: false" in doc
        assert "real_device_access_allowed: false" in doc
        assert "live_network_access_allowed: false" in doc
        assert "ssh_allowed: false" in doc
        assert "netconf_allowed: false" in doc
        assert "restconf_allowed: false" in doc
        assert "routeros_allowed: false" in doc
        assert "folder_move_performed: false" in doc
        assert "cleanup_performed: false" in doc
        assert "git_clean_run: false" in doc
        assert "day145_modified: false" in doc
        assert "day145_rerun: false" in doc
        assert "execution_provider_api_phase_advanced: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "day147_implemented: false" in doc
        assert "ai_assistance_advanced_beyond_v04: false" in doc
        assert "provider_runtime_unlocked: false" in doc
        assert "reviewer_approval_inferred: false" in doc
        assert "KEEP_DAY127_DAY145_V0_4_AI_ASSISTANCE_FROZEN_AND_NEXT_PHASE_FALSE" in doc
