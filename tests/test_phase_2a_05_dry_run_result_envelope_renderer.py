import inspect
import json

import network_lab
import phase_2a_05_dry_run_result_envelope_renderer as renderer


def _minimal_phase_2a_04_report():
    return {
        "phase": "2A-04",
        "status": "PASS",
        "task": "phase2a-04-plan-evidence-ledger",
        "title": "Phase 2A-04 Dry-Run Job Plan Evidence Binding / Traceability Ledger",
        "status_label": "PHASE_2A_04_PLAN_EVIDENCE_LEDGER_READY",
        "summary": {
            "source_accepted_plans": 3,
            "source_rejected_requests": 4,
            "accepted_evidence_records": 3,
            "rejected_evidence_records": 4,
            "runner_invoked_count": 0,
            "adapter_invoked_count": 0,
            "live_execution_opened_count": 0,
            "next_phase_allowed_count": 0,
        },
        "validation": {"status": "PASS", "valid": True, "errors": []},
        "ledger": {"ledger_id": "PHASE_2A_04_LEDGER_TEST"},
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
    }


def test_result_envelope_and_render_outputs_are_separate_siblings():
    report = renderer.build_phase_2a_05_dry_run_result_envelope_renderer_report(_minimal_phase_2a_04_report())

    assert report["phase"] == "2A-05"
    assert report["status"] == "PASS"
    assert set(("result_envelope", "render_outputs")).issubset(report)
    assert "render_outputs" not in report["result_envelope"]
    assert "result_envelope" not in report["render_outputs"]
    assert report["result_envelope"]["non_execution_proof"]["result_envelope_contains_render_outputs"] is False
    assert report["result_envelope"]["non_execution_proof"]["render_outputs_contains_result_envelope"] is False
    assert report["render_outputs"]["rendered_from_envelope_id"] == report["result_envelope"]["envelope_id"]
    assert report["render_outputs"]["json_self_recursion_prevented"] is True
    json.dumps(report)


def test_agents_md_status_is_carried_into_final_result_envelope():
    report = renderer.build_phase_2a_05_dry_run_result_envelope_renderer_report(_minimal_phase_2a_04_report())

    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }
    assert report["result_envelope"]["agents_md_status"]["pre_read_completed"] is True
    assert report["result_envelope"]["agents_md_status"]["modified"] is False
    assert "AGENTS_MD_FOUND_AND_READ" in report["completion_markers"]
    assert "AGENTS_MD_NOT_MODIFIED" in report["completion_markers"]


def test_phase_2a_05_consumes_phase_2a_04_report_builder_without_rebuilding_planner_or_ledger(monkeypatch):
    calls = []

    def fake_phase_2a_04_builder():
        calls.append("phase2a04")
        return _minimal_phase_2a_04_report()

    monkeypatch.setattr(renderer, "build_phase_2a_04_plan_evidence_ledger_report", fake_phase_2a_04_builder)

    report = renderer.build_phase_2a_05_dry_run_result_envelope_renderer_report()

    assert calls == ["phase2a04"]
    assert report["source_phase_2a_04_interface"]["implementation_searched"] is True
    assert report["source_phase_2a_04_interface"]["report_builder_consumed"] is True
    assert report["summary"]["planner_rebuilt"] is False
    assert report["summary"]["ledger_rebuilt"] is False
    assert report["result_envelope"]["non_execution_proof"]["phase_2a_03_planner_rebuilt"] is False
    assert report["result_envelope"]["non_execution_proof"]["phase_2a_04_ledger_rebuilt"] is False

    source = inspect.getsource(renderer)
    assert "from phase_2a_03" not in source
    assert "import phase_2a_03" not in source
    assert "build_phase_2a_04_plan_evidence_ledger(" not in source


def test_validator_rejects_recursive_render_output_embedding():
    report = renderer.build_phase_2a_05_dry_run_result_envelope_renderer_report(_minimal_phase_2a_04_report())
    report["render_outputs"]["result_envelope"] = report["result_envelope"]

    validation = renderer.validate_phase_2a_05_report(report)

    assert validation["valid"] is False
    assert "RENDER_OUTPUTS_CONTAINS_RESULT_ENVELOPE" in validation["errors"]


def test_cli_writes_report_only_envelope_renderer_without_runner_adapter_or_profile(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-05 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-05 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", renderer.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-05 Dry-Run Result Envelope / Renderer" in output
    assert "Task name: phase2a-05-dry-run-result-envelope-renderer" in output
    assert "result_envelope/render_outputs separated: true" in output
    assert "agents_md_pre_read_completed: true" in output
    assert "agents_md_modified: false" in output
    assert "planner_rebuilt: false" in output
    assert "ledger_rebuilt: false" in output
    assert "runner_invoked: false" in output
    assert "adapter_invoked: false" in output
    assert "live_execution_opened: false" in output
    assert "phase_2b_authorized: false" in output
    assert "real_execution_authorized: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] PHASE_2A_05_DRY_RUN_RESULT_ENVELOPE_RENDERER_READY" in output
    assert (tmp_path / renderer.REPORT_JSON).exists()
    assert (tmp_path / renderer.REPORT_HTML).exists()
    assert (tmp_path / renderer.REPORT_TXT).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == renderer.TASK_NAME)

    assert task["task_id"] == "phase_2a_05_dry_run_result_envelope_renderer"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert renderer.REPORT_JSON.as_posix() in task["report_paths"]
    assert renderer.REPORT_HTML.as_posix() in task["report_paths"]
    assert renderer.REPORT_TXT.as_posix() in task["report_paths"]
    assert renderer.DOC_PATH.as_posix() in task["report_paths"]
    assert "RESULT_ENVELOPE_RENDER_OUTPUTS_SEPARATED" in task["notes"]
    assert "JSON_SELF_RECURSION_PREVENTED" in task["notes"]
    assert "PLANNER_NOT_REBUILT" in task["notes"]
    assert "LEDGER_NOT_REBUILT" in task["notes"]

    assert network_lab.main(["--task", renderer.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-05 Dry-Run Result Envelope / Renderer" in html
    assert "phase_2a_05_dry_run_result_envelope_renderer.json" in html
