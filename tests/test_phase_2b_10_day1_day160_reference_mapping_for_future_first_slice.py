import copy
from pathlib import Path

import network_lab
import phase_2b_10_day1_day160_reference_mapping_for_future_first_slice as reference_mapping


DOC_PATH = Path("docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_10():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-10 Day1-Day160 Reference Mapping" not in agents_text
    assert "phase_2b_10_day1_day160_reference_mapping" not in agents_text


def test_phase_2b_10_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-10 Day1-Day160 Reference Mapping for Future First Slice - Planning Only" in text
    for section in (
        "## Purpose",
        "## Input Context",
        "## Scope Confirmation",
        "### Phase Goal",
        "### Example Job Types",
        "### Forbidden Scope",
        "### Existing Artifacts to Reference",
        "### Implementation Boundary",
        "## Phase Goal",
        "## Reference Mapping Table",
        "## De-duplication Proof",
        "## Allowed Reference Behavior",
        "## Future First-Slice Reviewer Checklist",
        "## Out-of-Scope List",
        "## Acceptance Criteria",
        "## Boundary Proof Checklist",
        "## Machine-Readable Boundary Proof",
        "## Final Verdict",
    ):
        assert section in text
    assert reference_mapping.FINAL_VERDICT in text
    assert "No implementation is authorized by this artifact." in text


def test_phase_2b_10_references_day1_day160_and_required_phase_2b_inputs():
    report = reference_mapping.build_phase_2b_10_day1_day160_reference_mapping_report()
    text = _doc_text()

    assert report["summary"]["day1_day160_referenced"] is True
    assert report["day1_day160_rewritten_or_replaced"] is False
    for artifact in reference_mapping.REQUIRED_PHASE_2B_REFERENCES:
        assert artifact in report["existing_artifacts_referenced"]
        assert artifact in text
    assert "Phase 2B-05 = Day1-Day160 safety de-duplication acceptance criteria." in text
    assert "Phase 2B-06 = implementation entry gate and first-slice readiness review." in text
    assert "Phase 2B-08 = first-slice implementation authorization gate." in text
    assert "Phase 2B-09 = first-slice implementation plan pack." in text
    assert "Phase 2B-10 = reference mapping only." in text


def test_phase_2b_10_scope_is_phase_wide_and_examples_only():
    report = reference_mapping.build_phase_2b_10_day1_day160_reference_mapping_report()
    text = _doc_text()

    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(reference_mapping.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    for job_type in reference_mapping.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "These job types are examples only." in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = reference_mapping.validate_phase_2b_10_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_phase_2b_10_includes_reference_mapping_table_and_reference_rules():
    report = reference_mapping.build_phase_2b_10_day1_day160_reference_mapping_report()
    text = _doc_text()

    assert report["validation"]["reference_mapping_rows_checked"] == len(reference_mapping.REFERENCE_MAPPING_TABLE)
    assert "| Future first-slice concern | Existing control or artifact to reference | Allowed use | Forbidden use | Reviewer evidence expected |" in text
    assert tuple(report["allowed_reference_behavior"]) == reference_mapping.ALLOWED_REFERENCE_BEHAVIOR
    assert tuple(report["forbidden_reference_behavior"]) == reference_mapping.FORBIDDEN_REFERENCE_BEHAVIOR
    for phrase in (
        "cite",
        "link",
        "summarize narrowly",
        "inherit",
        "verify consistency",
        "copy wholesale",
        "create parallel safety gate",
        "create new matrix",
    ):
        assert phrase in text

    tampered = copy.deepcopy(report)
    tampered["reference_mapping_table"] = []
    validation = reference_mapping.validate_phase_2b_10_report(tampered)
    assert validation["valid"] is False
    assert "REFERENCE_MAPPING_TABLE_MISSING" in validation["errors"]


def test_phase_2b_10_does_not_duplicate_prior_phase_roles_or_safety_matrix():
    report = reference_mapping.build_phase_2b_10_day1_day160_reference_mapping_report()
    text = _doc_text()

    assert report["de_duplication_proof"]["creates_second_safety_matrix"] is False
    assert report["de_duplication_proof"]["day1_day160_controls_remain_authoritative"] is True
    assert report["phase_2b_05_duplicated"] is False
    assert report["phase_2b_06_duplicated"] is False
    assert report["phase_2b_08_duplicated"] is False
    assert report["phase_2b_09_duplicated"] is False
    assert "This artifact does not create a second safety matrix." in text
    assert "Day1-Day160 controls remain authoritative." in text
    assert "Phase 2B-10 does not duplicate their roles" in text

    tampered = copy.deepcopy(report)
    tampered["second_safety_matrix_created"] = True
    tampered["phase_2b_09_duplicated"] = True
    validation = reference_mapping.validate_phase_2b_10_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2b_09_duplicated" in validation["errors"]


def test_phase_2b_10_forbidden_capabilities_stay_disabled():
    report = reference_mapping.build_phase_2b_10_day1_day160_reference_mapping_report()
    text = _doc_text()

    assert report["validation"]["valid"] is True
    for flag_name, expected in reference_mapping.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": reference_mapping.FINAL_VERDICT,
        "PLANNING_ONLY": "YES",
        "DAY1_DAY160_REFERENCED": "YES",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "PHASE_2B_05_DUPLICATED": "NO",
        "PHASE_2B_06_DUPLICATED": "NO",
        "PHASE_2B_08_DUPLICATED": "NO",
        "PHASE_2B_09_DUPLICATED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
    }
    for phrase in (
        "No runner, adapter, execution path",
        "provider/API/model call",
        "secrets handling",
        "SSH / NETCONF / RESTCONF / live device touched: `NO`",
    ):
        assert phrase in text

    tampered = copy.deepcopy(report)
    tampered["runner_added"] = True
    tampered["execution_path_added"] = True
    tampered["secrets_handling_added"] = True
    validation = reference_mapping.validate_phase_2b_10_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_10_reference_mapping_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-10 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-10 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", reference_mapping.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-10 Day1-Day160 Reference Mapping for Future First Slice - Planning Only" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "day1_day160_referenced: true" in output
    assert "day1_day160_rewritten_or_replaced: false" in output
    assert "second_safety_matrix_created: false" in output
    assert "phase_2b_05_duplicated: false" in output
    assert "phase_2b_06_duplicated: false" in output
    assert "phase_2b_08_duplicated: false" in output
    assert "phase_2b_09_duplicated: false" in output
    assert "first_slice_implemented: false" in output
    assert "runner_added: false" in output
    assert "adapter_added: false" in output
    assert "execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {reference_mapping.FINAL_VERDICT}" in output
    assert (tmp_path / reference_mapping.REPORT_JSON).exists()
    assert (tmp_path / reference_mapping.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == reference_mapping.TASK_NAME)

    assert task["task_id"] == "phase_2b_10_day1_day160_reference_mapping_for_future_first_slice"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert reference_mapping.REPORT_JSON.as_posix() in task["report_paths"]
    assert reference_mapping.REPORT_HTML.as_posix() in task["report_paths"]
    assert reference_mapping.DOC_PATH.as_posix() in task["report_paths"]
    assert reference_mapping.FINAL_VERDICT in task["notes"]
    assert "DAY1_DAY160_REFERENCED" in task["notes"]
    assert "DAY1_DAY160_REWRITTEN_OR_REPLACED_FALSE" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_FALSE" in task["notes"]
    assert "PHASE_2B_05_DUPLICATED_FALSE" in task["notes"]
    assert "PHASE_2B_06_DUPLICATED_FALSE" in task["notes"]
    assert "PHASE_2B_08_DUPLICATED_FALSE" in task["notes"]
    assert "PHASE_2B_09_DUPLICATED_FALSE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_FALSE" in task["notes"]

    assert network_lab.main(["--task", reference_mapping.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-10 Day1-Day160 Reference Mapping for Future First Slice - Planning Only" in html
    assert "phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.json" in html
