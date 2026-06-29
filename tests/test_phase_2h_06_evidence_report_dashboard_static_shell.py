from copy import deepcopy
from pathlib import Path

import pytest

import phase_2h_06_evidence_report_dashboard_static_shell as phase_2h_06


DOC_PATH = Path("docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.md")
HTML_PATH = Path("docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html")


def test_agents_md_is_not_modified_for_phase_2h_06():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2H-06 Evidence / Report Dashboard Static Shell" not in agents_text
    assert "phase_2h_06_evidence_report_dashboard_static_shell" not in agents_text


def test_phase_2h_06_document_exists_with_required_boundary_markers():
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Phase 2H-06 - Evidence / Report Dashboard Static Shell Implementation Slice" in text
    for marker in (
        "STATIC_DASHBOARD_SHELL: YES",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "READ_ONLY: YES",
        "NON_EXECUTING: YES",
        "LIVE_DATA_CONNECTED: NO",
        "RUNNER_CONNECTED: NO",
        "ADAPTER_CONNECTED: NO",
        "EXECUTION_PATH_ADDED: NO",
        "SSH_NETCONF_RESTCONF_ADDED: NO",
        "PROVIDER_API_MODEL_SECRETS_ADDED: NO",
        "CONFIG_BACKUP_CHANGE_ADDED: NO",
        "DAY1_DAY160_REWRITTEN: NO",
        "SECOND_SAFETY_MATRIX_ADDED: NO",
        phase_2h_06.FINAL_VERDICT,
    ):
        assert marker in text


def test_dashboard_shell_model_is_static_local_and_deterministic():
    first = phase_2h_06.build_dashboard_shell_model()
    second = phase_2h_06.build_dashboard_shell_model()

    assert first == second
    assert first["phase"] == "2H-06"
    assert first["status"] == "PASS"
    assert first["local_only"] is True
    assert first["deterministic"] is True
    assert first["static_only"] is True
    assert first["read_only"] is True
    assert first["non_executing"] is True
    assert first["requires_external_dependencies"] is False
    assert first["external_dependency_names"] == ()
    assert first["validation"]["valid"] is True


def test_dashboard_shell_contains_expected_static_sections_and_boundary_notice():
    model = phase_2h_06.build_dashboard_shell_model()
    section_titles = tuple(section["title"] for section in model["sections"])

    for expected in phase_2h_06.EXPECTED_SECTION_TITLES:
        assert expected in section_titles
    assert phase_2h_06.BOUNDARY_NOTICE in model["boundary_notice"]

    html = phase_2h_06.render_dashboard_shell_html(model)
    assert "<h1>Phase 2H-06 Evidence / Report Dashboard Static Shell</h1>" in html
    assert "Evidence summary placeholder" in html
    assert "Report summary placeholder" in html
    assert "Artifact status placeholder" in html
    assert "Static artifact references" in html
    assert "No live data source is attached" in html
    assert phase_2h_06.BOUNDARY_NOTICE in html
    assert "<script" not in html.lower()


def test_static_artifact_references_are_hard_coded_and_local_only():
    model = phase_2h_06.build_dashboard_shell_model()
    references = model["artifact_references"]

    assert references == phase_2h_06.STATIC_ARTIFACT_REFERENCES
    assert tuple(reference["kind"] for reference in references) == (
        "static artifact reference",
        "report reference",
        "report reference",
        "optional or missing local artifact reference",
    )
    assert tuple(reference["path"] for reference in references) == (
        "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html",
        "docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.md",
        "docs/phase_2h/phase_2h_07_evidence_report_dashboard_static_shell_acceptance_review_planning_only.md",
        "reports/report_index.html",
    )
    for reference in references:
        path = reference["path"]
        assert not path.startswith(("/", "\\"))
        assert "://" not in path
        assert "*" not in path
        assert "?" not in path


def test_static_artifact_reference_section_uses_no_runtime_discovery_terms():
    source = Path("phase_2h_06_evidence_report_dashboard_static_shell.py").read_text(
        encoding="utf-8"
    )

    forbidden_terms = (
        "glob(",
        ".glob",
        "os.walk",
        "scandir",
        "Path.exists",
        ".exists(",
        "requests",
        "urlopen",
        "fetch(",
        "importlib",
        "subprocess",
    )
    for term in forbidden_terms:
        assert term not in source


def test_committed_static_html_shell_can_be_read_locally():
    html = HTML_PATH.read_text(encoding="utf-8")

    assert "Phase 2H-06 Evidence / Report Dashboard Static Shell" in html
    assert phase_2h_06.BOUNDARY_NOTICE in html
    assert "Evidence summary placeholder" in html
    assert "Report summary placeholder" in html
    assert "Artifact status placeholder" in html
    assert "Static artifact references" in html
    assert "static artifact reference" in html
    assert "report reference" in html
    assert "optional or missing local artifact reference" in html
    assert "reports/report_index.html" in html
    assert "<script" not in html.lower()


def test_no_live_connector_runner_adapter_or_execution_integration_is_required():
    summary = phase_2h_06.build_phase_2h_06_dashboard_shell_summary()
    validation = summary["validation"]

    assert validation["valid"] is True
    assert validation["live_connector_required"] is False
    assert validation["runner_required"] is False
    assert validation["adapter_required"] is False
    assert validation["execution_path_required"] is False
    assert validation["external_access_attempted"] is False
    assert all(value is False for value in summary["forbidden_scope_status"].values())


def test_dashboard_shell_validation_rejects_tampered_forbidden_scope_flags():
    model = phase_2h_06.build_dashboard_shell_model()
    tampered = deepcopy(model)
    tampered["forbidden_scope_status"]["live_data_connected"] = True
    tampered["forbidden_scope_status"]["runner_connected"] = True
    tampered["forbidden_scope_status"]["adapter_connected"] = True
    tampered["forbidden_scope_status"]["execution_path_added"] = True
    tampered["requires_external_dependencies"] = True
    tampered["artifact_references"] = ()

    validation = phase_2h_06.validate_dashboard_shell_model(tampered)

    assert validation["valid"] is False
    assert "EXTERNAL_DEPENDENCIES_REQUIRED" in validation["errors"]
    assert "STATIC_ARTIFACT_REFERENCES_MISMATCH" in validation["errors"]
    assert "FORBIDDEN_SCOPE_STATUS_MISMATCH:live_data_connected" in validation["errors"]
    assert "FORBIDDEN_SCOPE_STATUS_MISMATCH:runner_connected" in validation["errors"]
    assert "FORBIDDEN_SCOPE_STATUS_MISMATCH:adapter_connected" in validation["errors"]
    assert "FORBIDDEN_SCOPE_STATUS_MISMATCH:execution_path_added" in validation["errors"]
    assert "FORBIDDEN_SCOPE_TOUCHED" in validation["errors"]


def test_render_rejects_invalid_model_without_reaching_execution_path():
    model = phase_2h_06.build_dashboard_shell_model()
    model["sections"] = ()

    with pytest.raises(ValueError):
        phase_2h_06.render_dashboard_shell_html(model)
