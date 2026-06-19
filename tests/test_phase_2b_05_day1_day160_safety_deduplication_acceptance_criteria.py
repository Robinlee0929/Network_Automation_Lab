from pathlib import Path

import network_lab
from network_lab_task_registry import CANONICAL_TASK_NAMES


DOC_PATH = Path("docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md")
TASK_ID = "phase2b-05-day1-day160-safety-deduplication-acceptance-criteria"


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_phase_2b_05_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-05 Day1-Day160 Safety De-duplication Acceptance Criteria" in text
    for section in (
        "## 1. Scope Confirmation",
        "## 2. Day1-Day160 Existing Safety Designs",
        "## 3. Phase 2B Safety Gate Duplication Review",
        "## 4. Reusable Existing Controls",
        "## 5. True Gaps",
        "## 6. Non-Duplication Acceptance Criteria",
        "## 7. Forbidden Implementation Proof",
        "## 8. Final Verdict",
    ):
        assert section in text
    assert "PHASE_2B_05_PLANNING_ONLY_DEDUP_ACCEPTANCE_CRITERIA_READY" in text


def test_phase_2b_05_scope_is_phase_wide_and_examples_only():
    text = _doc_text()

    for job_type in (
        "baseline_check",
        "interface_status_check",
        "wan_lan_check",
        "vrrp_validation",
        "backup_config_plan",
        "blocked_config_change_request",
    ):
        assert f"`{job_type}`" in text
    assert "These job types are examples only. They do not narrow Phase 2B-05" in text
    assert "this task remains phase-wide" in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text


def test_phase_2b_05_references_existing_artifacts_without_inventing_phase_2b_03():
    text = _doc_text()

    for artifact in (
        "AGENTS.md",
        "docs/roadmap/day35_vrrp_failover_validation_safety.md",
        "docs/ai-intent/day153_post_closure_forbidden_capability_reference_scan.md",
        "docs/ai/day159_v05_ai_assistance_safety_regression_matrix.md",
        "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
        "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
        "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    ):
        assert artifact in text
    assert "Phase 2B-03 source, documentation, and tests were not found" in text
    assert "does not invent a Phase 2B-03 path" in text


def test_phase_2b_05_forbidden_implementation_proof_stays_locked():
    text = _doc_text()

    for proof in (
        "implementation started: `NO`",
        "runner created/enabled: `NO`",
        "adapter created/enabled: `NO`",
        "execution created/enabled: `NO`",
        "provider calls enabled: `NO`",
        "API calls enabled: `NO`",
        "model calls enabled: `NO`",
        "live-device access enabled: `NO`",
        "SSH / NETCONF / RESTCONF enabled: `NO`",
        "second safety matrix created: `NO`",
        "renamed safety matrix created: `NO`",
        "replacement safety framework created: `NO`",
    ):
        assert proof in text
    assert "It must not create a second safety matrix." in text
    assert "It must not rename a duplicated matrix as an acceptance list, gate map, or control framework." in text


def test_phase_2b_05_catalog_visibility_without_cli_handler_or_runner(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == TASK_ID)

    assert TASK_ID not in CANONICAL_TASK_NAMES
    assert task["task_id"] == "phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["report_paths"] == [DOC_PATH.as_posix()]
    assert task["related_script"] == "none_planning_only_markdown_artifact"
    assert "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE" in task["notes"]
    assert "PROVIDER_API_MODEL_CALLS_ENABLED_FALSE" in task["notes"]
    assert "SECOND_PARALLEL_SAFETY_MATRIX_CREATED_FALSE" in task["notes"]

    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-05 Day1-Day160 Safety De-duplication Acceptance Criteria" in html
