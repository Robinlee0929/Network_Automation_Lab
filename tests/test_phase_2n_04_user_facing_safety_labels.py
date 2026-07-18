from pathlib import Path

import pytest

import dashboard_app as dashboard


ROOT = Path(__file__).resolve().parents[1]


def test_phase_2n_04_home_template_states_the_static_demo_boundaries():
    home = (ROOT / "templates" / "dashboard_home.html").read_text(encoding="utf-8")

    assert "Canonical reviewer entry point · Stage 0 Demo" in home
    assert "report-only / demo-only" in home
    assert "display-only during the Phase 2N Demo" in home


def test_phase_2n_04_flask_labels_render_through_get_without_command_execution(
    tmp_path, monkeypatch
):
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    command_execution_calls = 0

    def fail_if_executed(*args, **kwargs):
        nonlocal command_execution_calls
        command_execution_calls += 1
        raise AssertionError("GET-only presentation validation reached command execution")

    monkeypatch.setattr(dashboard, "execute_registered_command", fail_if_executed)
    app = dashboard.create_app(
        reports_dir=tmp_path / "reports",
        execution_logs_dir=tmp_path / "execution_logs",
    )
    client = app.test_client()

    home_response = client.get("/")
    commands_response = client.get("/commands")

    assert home_response.status_code == 200
    assert commands_response.status_code == 200
    assert b"Canonical reviewer entry point" in home_response.data
    assert b"report-only / demo-only" in home_response.data
    assert b"display-only during the Phase 2N Demo" in home_response.data
    assert b"Phase 2N Stage 0 Demo" in commands_response.data
    assert b"display-only" in commands_response.data
    assert b"demo-only" in commands_response.data

    commands_html = commands_response.get_data(as_text=True)
    assert "Command Allowlist Reference" in commands_html
    assert "No command can be submitted or executed from this page" in commands_html
    assert "Registered Command Examples" in commands_html
    assert "Historical Execution Records" in commands_html
    assert "Static Command Examples" in commands_html
    assert "Historical Demonstration Records" not in commands_html
    assert ">Execution Logs<" not in commands_html
    assert "Safe Command Execution" not in commands_html
    assert "Run a limited allowlist" not in commands_html
    assert "Recent Execution Logs" not in commands_html
    assert "before running commands" not in commands_html
    assert "<form" not in commands_html
    assert "<button" not in commands_html
    assert command_execution_calls == 0
