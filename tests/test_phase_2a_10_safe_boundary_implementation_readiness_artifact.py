import json
from pathlib import Path

import network_lab
import phase_2a_10_safe_boundary_implementation_readiness_artifact as pack


def test_agents_md_status_is_recorded_and_file_was_not_modified_by_pack():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    agents_path = Path("AGENTS.md")

    assert agents_path.exists()
    assert "Phase 2A-10 Safe-Boundary Implementation Readiness Artifact" not in agents_path.read_text(
        encoding="utf-8"
    )
    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }


def test_phase_2a_10_remains_phase_wide_and_not_one_example_job_type():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()

    assert report["phase"] == "2A-10"
    assert report["status"] == "PASS"
    assert report["scope_confirmation"]["phase_wide"] is True
    assert report["scope_confirmation"]["narrowed_to_one_example"] is False
    assert report["scope_confirmation"]["example_job_types_treated_as_examples_only"] is True
    assert set(report["example_job_types"]) == set(pack.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    assert report["example_job_type_role"] == "examples_only_not_full_scope"


def test_forbidden_scope_is_complete_and_all_safety_flags_remain_false():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()

    assert set(pack.FORBIDDEN_SCOPE).issubset(report["forbidden_scope"])
    for flag_name in pack.SAFETY_FLAGS:
        assert report[flag_name] is False
    assert report["implementation_boundary"]["real_execution_allowed"] is False
    assert report["implementation_boundary"]["phase_2b_allowed"] is False
    assert report["implementation_boundary"]["provider_api_model_allowed"] is False
    assert report["implementation_boundary"]["secrets_handling_allowed"] is False
    assert report["implementation_boundary"]["safety_gate_weakening_allowed"] is False


def test_implementation_boundary_allows_only_safe_local_readiness_work():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    boundary = report["implementation_boundary"]

    assert set(boundary["allowed_work"]) == set(pack.IMPLEMENTATION_BOUNDARY)
    for item in report["readiness_checklist"]:
        assert item["allowed_inside_phase_2a_10"] is True
        assert item["readiness_status"] == "READY"
        assert item["executable_capability"] is False


def test_prior_phase_2a_artifacts_are_referenced_and_phase_2a_09_is_safe():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    references = " ".join(report["existing_artifacts_referenced"])

    for fragment in pack.REQUIRED_REFERENCE_FRAGMENTS:
        assert fragment in references

    prior = report["prior_phase_2a_status"]
    assert prior["phase_2a_09_status"] == "PASS"
    assert prior["phase_2a_09_validation_status"] == "PASS"
    assert prior["phase_2a_09_source_job_count"] == 6
    assert set(prior["phase_2a_09_source_job_types"]) == set(pack.REQUIRED_JOB_TYPES)
    assert prior["phase_2a_09_next_phase_allowed"] is False
    assert prior["phase_2a_09_phase_2b_introduced"] is False
    assert prior["phase_2a_09_runner_introduced"] is False
    assert prior["phase_2a_09_adapter_introduced"] is False
    assert prior["phase_2a_09_live_device_introduced"] is False


def test_readiness_decision_is_ready_and_validation_rejects_unsafe_tampering():
    report = pack.build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()

    assert report["validation"]["valid"] is True
    assert report["readiness_decision"]["decision"] == "PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READY"
    assert report["readiness_decision"]["blocked"] is False

    tampered = json.loads(json.dumps(report))
    tampered["scope_confirmation"]["narrowed_to_one_example"] = True
    tampered["example_job_types"] = ["vrrp_validation"]
    validation = pack.validate_phase_2a_10_report(tampered)
    assert validation["valid"] is False
    assert "SCOPE_NARROWED_TO_ONE_EXAMPLE" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]

    tampered = json.loads(json.dumps(report))
    tampered["phase_2b_enabled"] = True
    tampered["real_runner_enabled"] = True
    tampered["safety_gates_weakened"] = True
    validation = pack.validate_phase_2a_10_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_NOT_FALSE:phase_2b_enabled" in validation["errors"]
    assert "SAFETY_FLAG_NOT_FALSE:real_runner_enabled" in validation["errors"]
    assert "SAFETY_FLAG_NOT_FALSE:safety_gates_weakened" in validation["errors"]


def test_cli_writes_phase_2a_10_readiness_artifact_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-10 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-10 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-10 Safe-Boundary Implementation Readiness Artifact" in output
    assert "Task name: phase2a-10-safe-boundary-implementation-readiness-artifact" in output
    assert "Phase-wide: true" in output
    assert "Narrowed to one example: false" in output
    assert "Example job types: 6" in output
    assert "phase_2b_enabled: false" in output
    assert "real_runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_calls_enabled: false" in output
    assert "model_calls_enabled: false" in output
    assert "safety_gates_weakened: false" in output
    assert "Readiness decision: PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READY" in output
    assert "[PASS] PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READY" in output
    assert (tmp_path / pack.REPORT_JSON).exists()
    assert (tmp_path / pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == pack.TASK_NAME)

    assert task["task_id"] == "phase_2a_10_safe_boundary_implementation_readiness_artifact"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["produces_report"] is True
    assert pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert pack.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_WIDE_SCOPE_CONFIRMED" in task["notes"]
    assert "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY" in task["notes"]
    assert "PHASE_2B_ENABLED_FALSE" in task["notes"]
    assert "REAL_RUNNER_ENABLED_FALSE" in task["notes"]
    assert "SAFETY_GATES_WEAKENED_FALSE" in task["notes"]

    assert network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-10 Safe-Boundary Implementation Readiness Artifact" in html
    assert "phase_2a_10_safe_boundary_implementation_readiness_artifact.json" in html
