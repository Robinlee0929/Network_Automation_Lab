import copy
from pathlib import Path

import network_lab
import phase_2b_11_project_consolidation_and_implementation_entry_map as entry_map


DOC_PATH = Path("docs/phase_2b/phase_2b_11_project_consolidation_and_implementation_entry_map.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_11():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-11 Project Consolidation" not in agents_text
    assert "phase_2b_11_project_consolidation" not in agents_text


def test_phase_2b_11_markdown_artifact_exists_and_has_future_plan_sections():
    text = _doc_text()

    assert "# Phase 2B-11 Project Consolidation and Implementation Entry Map — Planning Only" in text
    for section in (
        "## 1. Purpose",
        "## 2. Input Context",
        "## 3. Existing Artifacts Referenced",
        "## 4. Scope Boundary",
        "## 5. Example Job Types",
        "## 6. Consolidation Map",
        "## 7. No-Execution Proof",
        "## 8. Non-Duplication Proof",
        "## 9. Reviewer Evidence",
        "## 10. Completion Boundary",
        "## 11. Future Plan and Drift Check",
        "### A. Recommended next planning steps",
        "### B. Future implementation entry conditions",
        "### C. First-slice candidate path",
        "### D. Items that would indicate scope drift",
        "### E. Current drift verdict",
        "## 12. Machine-Readable Boundary Proof",
        "## 13. Final Verdict",
    ):
        assert section in text
    assert entry_map.FINAL_VERDICT in text
    assert "No implementation is authorized by this artifact." in text


def test_phase_2b_11_future_plan_is_review_only_and_lists_required_steps():
    report = entry_map.build_phase_2b_11_project_consolidation_entry_map_report()
    text = _doc_text()

    assert report["future_plan_created"] is True
    assert report["future_plan_is_review_only"] is True
    assert report["future_implementation_authorized"] is False
    assert report["first_slice_selected"] is False
    assert report["first_slice_implemented"] is False
    assert report["current_scope_drift_detected"] is False
    assert report["future_scope_drift_items_listed"] is True
    for phrase in (
        "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
        "Phase 2B-13 First-Slice Final Selection Gate — Planning Only",
        "Phase 2B-14 First-Slice Implementation Kickoff Gate — Authorization Required",
        "Future Phase 2C First-Slice Implementation — Not Allowed Yet",
        "Future runner / adapter / execution path design — Not Allowed Yet",
        "Future live-device integration — Not Allowed Yet",
        "Future provider / API / model integration — Not Allowed Yet",
        "Do not create these phases yet.",
        "Do not implement these phases.",
        "Only list them as possible future direction for owner review.",
    ):
        assert phrase in text
    assert report["validation"]["future_plan_steps_checked"] == len(entry_map.FUTURE_PLAN_STEPS)


def test_phase_2b_11_entry_conditions_and_candidate_path_are_review_items_only():
    report = entry_map.build_phase_2b_11_project_consolidation_entry_map_report()
    text = _doc_text()

    assert set(report["future_plan"]["future_implementation_entry_conditions"]) == set(
        entry_map.FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS
    )
    for condition in entry_map.FUTURE_IMPLEMENTATION_ENTRY_CONDITIONS:
        assert condition in text
    assert set(item["candidate"] for item in report["future_plan"]["first_slice_candidate_path"]) == set(
        entry_map.REQUIRED_JOB_TYPES
    )
    for candidate in entry_map.REQUIRED_JOB_TYPES:
        assert f"`{candidate}`" in text
    for classification in (
        "Potential future candidate",
        "Needs more planning",
        "Blocked / forbidden for now",
    ):
        assert classification in text
    assert "No final first slice is selected." in text
    assert "No candidate is implemented." in text


def test_phase_2b_11_scope_drift_checklist_and_verdict_are_present():
    report = entry_map.build_phase_2b_11_project_consolidation_entry_map_report()
    text = _doc_text()

    assert set(report["future_plan"]["scope_drift_checklist"]) == set(entry_map.SCOPE_DRIFT_CHECKLIST)
    for drift_item in entry_map.SCOPE_DRIFT_CHECKLIST:
        assert drift_item in text
    for verdict_line in (
        "CURRENT_SCOPE_DRIFT_DETECTED: NO",
        "FUTURE_PLAN_IS_REVIEW_ONLY: YES",
        "FUTURE_IMPLEMENTATION_AUTHORIZED: NO",
        "FIRST_SLICE_SELECTED: NO",
        "FIRST_SLICE_IMPLEMENTED: NO",
    ):
        assert verdict_line in text
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": entry_map.FINAL_VERDICT,
        "FUTURE_PLAN_CREATED": "YES",
        "FUTURE_PLAN_IS_REVIEW_ONLY": "YES",
        "FUTURE_IMPLEMENTATION_AUTHORIZED": "NO",
        "FIRST_SLICE_SELECTED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "CURRENT_SCOPE_DRIFT_DETECTED": "NO",
        "FUTURE_SCOPE_DRIFT_ITEMS_LISTED": "YES",
        "NEXT_RECOMMENDED_STEP": "Phase 2B-12 Future Implementation Authorization Review — Planning Only",
    }


def test_phase_2b_11_forbidden_capabilities_stay_disabled_and_drift_blocks():
    report = entry_map.build_phase_2b_11_project_consolidation_entry_map_report()

    assert report["validation"]["valid"] is True
    for flag_name, expected in entry_map.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["current_scope_drift_detected"] = True
    tampered["future_implementation_authorized"] = True
    tampered["first_slice_selected"] = True
    tampered["runner_added"] = True
    tampered["ssh_touched"] = True
    tampered["secrets_handling_added"] = True
    validation = entry_map.validate_phase_2b_11_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:current_scope_drift_detected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:future_implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:first_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_11_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-11 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-11 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", entry_map.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-11 Project Consolidation and Implementation Entry Map — Planning Only" in output
    assert "future_plan_created: true" in output
    assert "future_plan_is_review_only: true" in output
    assert "future_implementation_authorized: false" in output
    assert "first_slice_selected: false" in output
    assert "first_slice_implemented: false" in output
    assert "current_scope_drift_detected: false" in output
    assert "future_scope_drift_items_listed: true" in output
    assert "runner_added: false" in output
    assert "adapter_added: false" in output
    assert "execution_path_added: false" in output
    assert "ssh_touched: false" in output
    assert "netconf_touched: false" in output
    assert "restconf_touched: false" in output
    assert "live_device_access_added: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {entry_map.FINAL_VERDICT}" in output
    assert (tmp_path / entry_map.REPORT_JSON).exists()
    assert (tmp_path / entry_map.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == entry_map.TASK_NAME)

    assert task["task_id"] == "phase_2b_11_project_consolidation_and_implementation_entry_map"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert entry_map.REPORT_JSON.as_posix() in task["report_paths"]
    assert entry_map.REPORT_HTML.as_posix() in task["report_paths"]
    assert entry_map.DOC_PATH.as_posix() in task["report_paths"]
    assert "FUTURE_PLAN_CREATED" in task["notes"]
    assert "FUTURE_PLAN_IS_REVIEW_ONLY" in task["notes"]
    assert "FUTURE_IMPLEMENTATION_AUTHORIZED_FALSE" in task["notes"]
    assert "FIRST_SLICE_SELECTED_FALSE" in task["notes"]
    assert "CURRENT_SCOPE_DRIFT_DETECTED_FALSE" in task["notes"]

    assert network_lab.main(["--task", entry_map.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-11 Project Consolidation and Implementation Entry Map - Planning Only" in html
    assert "phase_2b_11_project_consolidation_and_implementation_entry_map.json" in html
