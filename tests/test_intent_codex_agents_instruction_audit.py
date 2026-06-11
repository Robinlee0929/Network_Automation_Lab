import ast
import json
from pathlib import Path

import intent_codex_agents_instruction_audit as day106
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "routeros_api",
    "openai",
    "requests",
    "httpx",
    "socket",
    "subprocess",
}


SAFE_AGENTS_TEXT = """# AGENTS.md

## Project

This repository is a Network Automation Lab for safe reviewer-visible validation.

## Core Safety Rules

- Do not perform live device access unless a future task explicitly approves a safety gate.
- Do not use SSH or real network-device commands.
- Do not execute configuration-changing commands.
- Preserve safety gates and no-execution proof.
- Report-only work remains report-only.
- Do not add secrets, credentials, tokens, private local memory, private paths, or personal details.
- Do not add OpenAI API calls, voice input, voice runtime, microphone, or cloud execution.
- Do not push, merge, or tag without explicit user approval.

## Git Workflow

- Keep changes focused.

## Standard Validation

```bash
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task <task-name>
```

## Done Criteria

Work is done when validation commands are run and no safety gate is weakened.
"""


def write_agents(project_root: Path, text: str = SAFE_AGENTS_TEXT) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_day106_safe_agents_contract_passes(tmp_path):
    write_agents(tmp_path)
    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    assert report["day"] == 106
    assert report["phase_name"] == "Codex AGENTS.md Instruction Compliance Audit"
    assert report["audit_type"] == "REPORT_ONLY"
    assert report["agents_file_found"] is True
    assert report["overall_status"] == "PASS", json.dumps(
        {
            "checks": report["audit_checks"],
            "risk_findings": report["risk_findings"],
            "secret_findings": report["secret_findings"],
        },
        indent=2,
    )
    assert report["final_recommendation"] == day106.PASS_RECOMMENDATION
    assert report["validation_errors"] == []
    assert report["codex_may_read_agents_md"] is True
    assert report["codex_may_audit_agents_md"] is True
    assert report["codex_may_report_findings_and_proposed_changes"] is True
    assert report["codex_must_not_modify_agents_md"] is True
    assert report["codex_must_not_stage_agents_md"] is True
    assert report["codex_must_not_commit_agents_md"] is True
    assert report["audit_modifies_agents_md"] is False
    assert report["audit_stages_agents_md"] is False
    assert report["audit_commits_agents_md"] is False


def test_day106_all_execution_and_publication_flags_remain_false(tmp_path):
    write_agents(tmp_path)
    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    for flag in day106.FORBIDDEN_RUNTIME_FLAGS:
        assert report[flag] is False
    assert all(value is False for value in report["execution_proof"].values())


def test_day106_missing_agents_file_fails(tmp_path):
    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    assert report["agents_file_found"] is False
    assert report["overall_status"] == "FAIL"
    assert report["final_recommendation"] == day106.MISSING_RECOMMENDATION


def test_day106_incomplete_agents_file_warns(tmp_path):
    write_agents(tmp_path, "# AGENTS.md\n\nThis repository has some guidance.\n")

    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    assert report["agents_file_found"] is True
    assert report["overall_status"] == "WARN"
    assert report["final_recommendation"] == day106.HARDENING_RECOMMENDATION
    assert report["missing_required_checks"]
    assert report["proposed_agents_md_changes"]
    assert "Day106 must not modify, stage, or commit AGENTS.md" in report["proposed_agents_md_changes"][0]["reason"]


def test_day106_risky_live_execution_language_fails(tmp_path):
    write_agents(
        tmp_path,
        SAFE_AGENTS_TEXT
        + "\n\n## Dangerous\n\nCodex may automatically connect to live routers and push changes without approval.\n",
    )

    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    assert report["overall_status"] == "FAIL"
    assert report["final_recommendation"] == day106.RISK_RECOMMENDATION
    assert report["risk_findings"]


def test_day106_secret_like_literal_fails(tmp_path):
    write_agents(tmp_path, SAFE_AGENTS_TEXT + "\n\nrouter_password = supersecret123\n")

    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    assert report["overall_status"] == "FAIL"
    assert report["secrets_exposure_status"] == "FAIL"
    assert report["secret_findings"]


def test_day106_report_writer_outputs_json_and_html(tmp_path):
    write_agents(tmp_path)
    report = day106.build_codex_agents_instruction_audit_report(tmp_path)

    json_path, html_path = day106.write_codex_agents_instruction_audit_reports(tmp_path, report)

    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day106 Codex AGENTS.md Instruction Compliance Audit" in html
    assert "REPORT_ONLY" in html
    assert day106.PASS_RECOMMENDATION in html
    assert "reports/ai/day106_codex_agents_instruction_compliance_audit.json" in html
    assert "Codex may read AGENTS.md, audit AGENTS.md, and report findings" in html


def test_day106_module_has_no_live_or_external_tool_imports():
    tree = ast.parse(Path(day106.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day106_runner_task_returns_pass_without_execution(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day106 AGENTS audit must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day106 AGENTS audit must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "codex-agents-instruction-audit"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day106 Codex AGENTS.md Instruction Compliance Audit" in output
    assert "Task name: codex-agents-instruction-audit" in output
    assert "Audit type: REPORT_ONLY" in output
    assert "AGENTS.md found: true" in output
    assert f"Final recommendation: {day106.PASS_RECOMMENDATION}" in output
    for flag in day106.FORBIDDEN_RUNTIME_FLAGS:
        assert f"{flag} = false" in output
    assert "codex_may_read_agents_md = true" in output
    assert "codex_may_audit_agents_md = true" in output
    assert "codex_may_report_findings_and_proposed_changes = true" in output
    assert "codex_must_not_modify_agents_md = true" in output
    assert "codex_must_not_stage_agents_md = true" in output
    assert "codex_must_not_commit_agents_md = true" in output
    assert "audit_modifies_agents_md = false" in output
    assert "audit_stages_agents_md = false" in output
    assert "audit_commits_agents_md = false" in output
    assert (tmp_path / day106.REPORT_JSON).exists()
    assert (tmp_path / day106.REPORT_HTML).exists()
    assert not (tmp_path / "config.json").exists()


def test_day106_report_index_visibility_includes_agents_audit(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "codex-agents-instruction-audit"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Codex AGENTS.md Instruction Compliance Audit" in html
    assert "AGENTS.md governance audit only" in html
    assert "reports/ai/day106_codex_agents_instruction_compliance_audit.json" in html
    assert "reports/ai/day106_codex_agents_instruction_compliance_audit.html" in html


def test_day106_task_catalog_metadata_is_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "codex-agents-instruction-audit")

    assert task["task_id"] == "day106_codex_agents_instruction_compliance_audit"
    assert task["day"] == "Day106"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/ai/day106_codex_agents_instruction_compliance_audit.json" in task["report_paths"]
    assert "docs/ai-intent/day106_codex_agents_instruction_compliance_audit.md" in task["report_paths"]
    assert "openai_api_allowed" in task["notes"]
    assert "push_allowed_without_user_approval" in task["notes"]
    assert "codex_must_not_modify_agents_md" in task["notes"]
    assert "codex_must_not_stage_agents_md" in task["notes"]
    assert "codex_must_not_commit_agents_md" in task["notes"]


def test_day106_docs_and_html_do_not_introduce_action_surfaces(tmp_path):
    write_agents(tmp_path)
    report = day106.build_codex_agents_instruction_audit_report(tmp_path)
    _json_path, html_path = day106.write_codex_agents_instruction_audit_reports(tmp_path, report)
    checked_paths = [
        html_path,
        Path("docs/ai-intent/day106_codex_agents_instruction_compliance_audit.md"),
        Path("docs/roadmap/day106_codex_agents_instruction_compliance_audit.md"),
        Path("docs/ai-intent/README.md"),
    ]

    for path in checked_paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "<form" not in text
        assert "<button" not in text
        assert "method=\"post\"" not in text
        assert "action=" not in text
        assert "http://" not in text
        assert "https://" not in text
