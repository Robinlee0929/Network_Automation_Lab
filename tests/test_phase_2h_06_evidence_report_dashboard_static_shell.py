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
    assert first["section_groups"] == phase_2h_06.EXPECTED_SECTION_GROUPS
    assert first["validation"]["valid"] is True


def test_dashboard_shell_contains_expected_static_section_order_groups_and_boundary_notice():
    model = phase_2h_06.build_dashboard_shell_model()
    section_titles = tuple(section["title"] for section in model["sections"])

    assert section_titles == phase_2h_06.EXPECTED_SECTION_TITLES
    assert tuple(group["title"] for group in model["section_groups"]) == (
        "Reviewer orientation",
        "Static evidence, report, and artifact summaries",
        "Static state messaging",
    )
    assert tuple(
        section_id
        for group in model["section_groups"]
        for section_id in group["section_ids"]
    ) == tuple(section["id"] for section in model["sections"])
    assert phase_2h_06.BOUNDARY_NOTICE in model["boundary_notice"]

    html = phase_2h_06.render_dashboard_shell_html(model)
    assert "<h1>Phase 2H-06 Evidence / Report Dashboard Static Shell</h1>" in html
    assert html.index("Reviewer orientation") < html.index(
        "Static evidence, report, and artifact summaries"
    )
    assert html.index("Static evidence, report, and artifact summaries") < html.index(
        "Static state messaging"
    )
    assert html.index("Boundary notice") < html.index("Static evidence summary")
    assert "Static evidence summary" in html
    assert "Static report summary" in html
    assert "Static artifact summary" in html
    assert "Static artifact references" in html
    assert "Static empty-state messaging" in html
    assert "Static missing-artifact messaging" in html
    assert "No live data source is attached" in html
    assert phase_2h_06.BOUNDARY_NOTICE in html
    assert "<script" not in html.lower()


def test_phase_2h_29_static_summary_wording_refinement_is_visible():
    model = phase_2h_06.build_dashboard_shell_model()
    sections = {section["id"]: section for section in model["sections"]}
    rendered = phase_2h_06.render_dashboard_shell_html(model)

    assert sections["evidence-summary"]["title"] == "Static evidence summary"
    assert "committed local evidence references only" in sections["evidence-summary"]["body"]
    assert "No live evidence source is connected, collected, refreshed, or inferred." in rendered

    assert sections["report-summary"]["title"] == "Static report summary"
    assert "committed report references only" in sections["report-summary"]["body"]
    assert "No report refresh, regeneration, fetch, or runtime lookup is performed." in rendered

    assert sections["artifact-status"]["title"] == "Static artifact summary"
    assert "optional static labels, not runtime collection" in sections["artifact-status"]["body"]
    assert "Evidence summary placeholder" not in rendered
    assert "Report summary placeholder" not in rendered
    assert "Artifact status placeholder" not in rendered


def test_static_artifact_references_are_hard_coded_and_local_only():
    model = phase_2h_06.build_dashboard_shell_model()
    references = model["artifact_references"]

    assert references == phase_2h_06.STATIC_ARTIFACT_REFERENCES
    assert tuple(reference["kind"] for reference in references) == (
        "static artifact reference",
        "report reference",
        "report reference",
        "optional local artifact reference",
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
    assert references[-1]["availability"] == "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY"
    for reference in references:
        assert reference["status_explanation"]
        assert reference["availability_explanation"]


def test_static_empty_state_and_missing_artifact_messages_are_deterministic_copy_only():
    model = phase_2h_06.build_dashboard_shell_model()

    assert model["static_empty_state_messages"] == phase_2h_06.STATIC_EMPTY_STATE_MESSAGES
    assert (
        model["static_missing_artifact_messages"]
        == phase_2h_06.STATIC_MISSING_ARTIFACT_MESSAGES
    )
    assert tuple(message["id"] for message in model["static_empty_state_messages"]) == (
        "no-usable-artifact-reference",
        "static-report-only-dashboard-state",
    )
    assert tuple(message["id"] for message in model["static_missing_artifact_messages"]) == (
        "optional-report-index-static-missing",
    )

    rendered = phase_2h_06.render_dashboard_shell_html(model)
    for expected in (
        "No usable artifact reference in static context",
        "No live scan, runtime artifact discovery, fetch, generation, recovery, or execution is attempted.",
        "Optional local artifact may be absent",
        "The dashboard does not check the filesystem, discover artifacts, recover, fetch, generate, refresh, or execute anything.",
        "local, deterministic, read-only, report-only, and non-executing",
    ):
        assert expected in rendered


def test_static_status_and_availability_labels_have_reviewer_explanations():
    model = phase_2h_06.build_dashboard_shell_model()
    rendered = phase_2h_06.render_dashboard_shell_html(model)

    assert model["static_label_explanation_groups"] == (
        phase_2h_06.STATIC_LABEL_EXPLANATION_GROUPS
    )
    for section in model["sections"]:
        assert section["status"] in phase_2h_06.STATIC_SECTION_STATUS_EXPLANATIONS
        assert (
            section["status_explanation"]
            == phase_2h_06.STATIC_SECTION_STATUS_EXPLANATIONS[section["status"]]
        )
    for reference in model["artifact_references"]:
        assert (
            reference["status_explanation"]
            == phase_2h_06.STATIC_ARTIFACT_REFERENCE_STATUS_EXPLANATIONS[
                reference["status"]
            ]
        )
        assert (
            reference["availability_explanation"]
            == phase_2h_06.STATIC_ARTIFACT_AVAILABILITY_EXPLANATIONS[
                reference["availability"]
            ]
        )
    for message in (
        *model["static_empty_state_messages"],
        *model["static_missing_artifact_messages"],
    ):
        assert (
            message["status_explanation"]
            == phase_2h_06.STATIC_MESSAGE_STATUS_EXPLANATIONS[message["status"]]
        )

    assert "Status label:" in rendered
    assert "Availability label:" in rendered
    assert "STATIC_REFERENCE_AVAILABLE" in rendered
    assert "STATIC_OPTIONAL_OR_MISSING_MESSAGE_ONLY" in rendered
    assert "availability is a committed static declaration" in rendered
    assert "message-only static copy" in rendered


def test_static_artifact_reference_section_uses_no_runtime_discovery_terms():
    source = Path("phase_2h_06_evidence_report_dashboard_static_shell.py").read_text(
        encoding="utf-8"
    )

    forbidden_terms = (
        "glob(",
        ".glob",
        "rglob",
        "os.walk",
        "os.path.exists",
        "scandir",
        "Path.exists",
        ".exists(",
        "iterdir",
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
    assert "Static evidence summary" in html
    assert "Static report summary" in html
    assert "Static artifact summary" in html
    assert "Static artifact references" in html
    assert "Static empty-state messaging" in html
    assert "Static missing-artifact messaging" in html
    assert "static artifact reference" in html
    assert "report reference" in html
    assert "optional local artifact reference" in html
    assert "reports/report_index.html" in html
    assert "No usable artifact reference in static context" in html
    assert "Optional local artifact may be absent" in html
    assert "<script" not in html.lower()


def test_no_live_connector_runner_adapter_or_execution_integration_is_required():
    summary = phase_2h_06.build_phase_2h_06_dashboard_shell_summary()
    validation = summary["validation"]

    assert summary["section_titles"] == phase_2h_06.EXPECTED_SECTION_TITLES
    assert summary["section_groups"] == phase_2h_06.EXPECTED_SECTION_GROUPS
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


def test_dashboard_shell_validation_rejects_tampered_section_grouping():
    model = phase_2h_06.build_dashboard_shell_model()
    tampered = deepcopy(model)
    tampered["section_groups"] = (
        {
            "id": "static-state-messaging",
            "title": "Static state messaging",
            "description": "Tampered group order.",
            "section_ids": (
                "static-empty-state-messaging",
                "static-missing-artifact-messaging",
            ),
        },
    )

    validation = phase_2h_06.validate_dashboard_shell_model(tampered)

    assert validation["valid"] is False
    assert "SECTION_GROUPS_MISMATCH" in validation["errors"]
    assert "SECTION_GROUP_ORDER_MISMATCH" in validation["errors"]
