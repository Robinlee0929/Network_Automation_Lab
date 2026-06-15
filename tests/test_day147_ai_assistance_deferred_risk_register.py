import copy
import json
from pathlib import Path

import day147_ai_assistance_deferred_risk_register as day147
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day147_report_contains_deferred_register_and_required_safety_flags():
    report = day147.build_day147_ai_assistance_deferred_risk_register(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["status"] == "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY"
    assert report["day"] == 147
    assert report["day_label"] == "Day147"
    assert report["task"] == "ai-assistance-deferred-risk-register"
    assert report["title"] == "AI Assistance Deferred Risk Register"
    assert report["mode"] == "REVIEW_ONLY_DEFERRED_RISK_REGISTER"
    assert report["agents_md_read_before_day147_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["day145_freeze_reference"] == "ddefb46e045df5310634ad307937f81c9f08e6cb"
    assert report["day145_conclusion_preserved"] is True
    assert report["day146_gate_status"] == "V0_4_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_READY"
    assert report["day146_non_advancement_preserved"] is True
    assert report["risk_count"] == 10
    assert report["final_recommendation"] == "KEEP_AI_ASSISTANCE_DEFERRED_AND_NEXT_PHASE_FALSE"
    assert report["validation_errors"] == []

    for field in day147.REQUIRED_TRUE_FIELDS:
        assert report[field] is True
    for field in day147.REQUIRED_FALSE_FIELDS:
        assert report[field] is False

    expected = report["expected_task_result"]
    assert expected["overall_status"] == "PASS"
    assert expected["status"] == "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY"
    assert expected["review_only"] is True
    assert expected["next_phase_allowed"] is False
    assert expected["provider_enabled"] is False
    assert expected["api_call_enabled"] is False
    assert expected["execution_enabled"] is False
    assert expected["model_decision_enabled"] is False
    assert expected["live_network_enabled"] is False
    assert expected["secrets_required"] is False


def test_day147_risk_register_covers_required_categories_with_no_unsafe_flags():
    report = day147.build_day147_ai_assistance_deferred_risk_register(PROJECT_ROOT)

    assert [risk["category"] for risk in report["risk_register"]] == list(day147.REQUIRED_CATEGORIES)
    assert [risk["risk_id"] for risk in report["risk_register"]] == [
        f"DAY147-RISK-{index:03d}" for index in range(1, 11)
    ]
    for risk in report["risk_register"]:
        assert set(day147.RISK_FIELD_NAMES).issubset(risk)
        assert risk["status"] in {"BLOCKED_DEFERRED", "DEFERRED_TO_DAY148", "DEFERRED_TO_DAY149", "LOCKED"}
        assert risk["next_phase_allowed"] is False
        assert set(risk["unsafe_flags"]) == set(day147.UNSAFE_FLAG_KEYS)
        for field in day147.UNSAFE_FLAG_KEYS:
            assert risk["unsafe_flags"][field] is False


def test_day147_cli_does_not_execute_provider_network_or_prior_day_paths(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day147 must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day147 must not load runner profile or config data")

    def fail_day145(*args, **kwargs):
        raise AssertionError("Day147 must not rerun Day145")

    def fail_day146(*args, **kwargs):
        raise AssertionError("Day147 must not rerun Day146")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)
    monkeypatch.setattr(network_lab, "_run_day145_v04_ai_assistance_evidence_freeze_package", fail_day145)
    monkeypatch.setattr(network_lab, "_run_day146_v04_ai_assistance_non_advancement_gate", fail_day146)

    exit_code = network_lab.main(
        ["--task", "ai-assistance-deferred-risk-register"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day147 documents deferred risks and blocked items only." in output
    assert "Day147 preserves the Day146 non-advancement gate as authoritative." in output
    assert "Day147 keeps next_phase_allowed=false." in output
    assert "risk_count: 10" in output
    assert "provider_enabled: false" in output
    assert "api_call_enabled: false" in output
    assert "execution_enabled: false" in output
    assert "model_decision_enabled: false" in output
    assert "live_network_enabled: false" in output
    assert "secrets_required: false" in output
    assert "[PASS] AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY" in output


def test_day147_negative_validation_blocks_unsafe_flags_and_gate_mutation():
    report = day147.build_day147_ai_assistance_deferred_risk_register(PROJECT_ROOT)
    unsafe = copy.deepcopy(report)
    unsafe["agents_md_read_before_day147_work"] = False
    unsafe["agents_md_pre_read_result"] = "FAIL"
    unsafe["day145_conclusion_preserved"] = False
    unsafe["day146_non_advancement_preserved"] = False
    unsafe["risk_register"][0]["next_phase_allowed"] = True
    unsafe["risk_register"][0]["unsafe_flags"]["provider_enabled"] = True
    unsafe["expected_task_result"]["next_phase_allowed"] = True

    for field in day147.REQUIRED_FALSE_FIELDS:
        unsafe[field] = True

    errors = day147.collect_validation_errors(unsafe)

    assert "agents_md_read_before_day147_work must be true." in errors
    assert "agents_md_pre_read_result must be PASS." in errors
    assert "day145_conclusion_preserved must be true." in errors
    assert "day146_non_advancement_preserved must be true." in errors
    assert "DAY147-RISK-001 next_phase_allowed must be false." in errors
    assert "DAY147-RISK-001 unsafe_flags.provider_enabled must be false." in errors
    assert "expected_task_result.next_phase_allowed must be false." in errors
    for field in day147.REQUIRED_FALSE_FIELDS:
        assert f"{field} must be false." in errors


def test_day147_task_catalog_dispatch_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == "ai-assistance-deferred-risk-register")
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-assistance-deferred-risk-register"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-assistance-deferred-risk-register", handlers)

    assert resolve_task_name("ai-assistance-deferred-risk-register") == "ai-assistance-deferred-risk-register"
    assert resolved.canonical_name == "ai-assistance-deferred-risk-register"
    assert callable(resolved.handler)
    assert task["task_id"] == "day147_ai_assistance_deferred_risk_register"
    assert task["day"] == "Day147"
    assert task["user_display_name"] == "AI Assistance Deferred Risk Register"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "day147_ai_assistance_deferred_risk_register.py"
    assert "Day145 freeze preserved" in task["notes"]
    assert "Day146 authoritative" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]

    report = day147.build_day147_ai_assistance_deferred_risk_register(PROJECT_ROOT)
    json_path, html_path = day147.write_day147_ai_assistance_deferred_risk_register_reports(tmp_path, report)
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["status"] == "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY"
    assert written["next_phase_allowed"] is False
    assert written["provider_enabled"] is False
    assert written["api_call_enabled"] is False
    assert written["execution_enabled"] is False
    assert "Day147" in index_html
    assert "AI Assistance Deferred Risk Register" in index_html
    assert "reports/lab-summary/day147_ai_assistance_deferred_risk_register.json" in index_html


def test_day147_module_does_not_import_provider_api_network_or_execution_surfaces():
    source = Path(day147.__file__).read_text(encoding="utf-8").lower()

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
        "authorization:",
        "bearer ",
        "remove-item",
        "rmtree",
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_day147_docs_preserve_required_deferred_risk_boundaries():
    roadmap = (PROJECT_ROOT / "docs/roadmap/day147_ai_assistance_deferred_risk_register.md").read_text(
        encoding="utf-8"
    )
    ai_intent = (PROJECT_ROOT / "docs/ai-intent/day147_ai_assistance_deferred_risk_register.md").read_text(
        encoding="utf-8"
    )

    for doc in (roadmap, ai_intent):
        assert "AI Assistance Deferred Risk Register" in doc
        assert "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY" in doc
        assert "ddefb46e045df5310634ad307937f81c9f08e6cb" in doc
        assert "Day145" in doc
        assert "Day146" in doc
        assert "review_only: true" in doc
        assert "provider_enabled: false" in doc
        assert "api_call_enabled: false" in doc
        assert "execution_enabled: false" in doc
        assert "model_decision_enabled: false" in doc
        assert "live_network_enabled: false" in doc
        assert "secrets_required: false" in doc
        assert "next_phase_allowed: false" in doc
        assert "day145_conclusion_changed: false" in doc
        assert "day145_evidence_mutated: false" in doc
        assert "day146_conclusion_changed: false" in doc
        assert "day146_gate_bypassed: false" in doc
        assert "day148_implemented: false" in doc
        assert "day149_implemented: false" in doc
        assert "KEEP_AI_ASSISTANCE_DEFERRED_AND_NEXT_PHASE_FALSE" in doc
        for category in day147.REQUIRED_CATEGORIES:
            assert category.rstrip(".") in doc
