import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

import dashboard_app as dashboard


TARGET_TEMPLATES = (
    "dashboard_home.html",
    "dashboard_reports.html",
    "dashboard_commands.html",
    "dashboard_command_logs.html",
    "dashboard_command_log.html",
    "dashboard_ai_checklist.html",
    "dashboard_ai_intent_reviewer.html",
    "dashboard_json_preview.html",
)

NAVIGATION = (
    ("Home", "/"),
    ("Reports", "/reports"),
    ("Commands", "/commands"),
    ("Execution Logs", "/commands/logs"),
    ("AI Intent Reviewer", "/ai-intent-reviewer"),
    ("AI Checklist", "/ai-checklist"),
)


class ShellParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.nav_depth = 0
        self.nav_links = []
        self._anchor = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if tag == "nav":
            self.nav_depth += 1
        if tag == "a" and self.nav_depth:
            self._anchor = {"attrs": attributes, "text": []}

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._anchor is not None:
            self._anchor["text"] = "".join(self._anchor["text"]).strip()
            self.nav_links.append(self._anchor)
            self._anchor = None
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1


@pytest.fixture()
def shell_client(tmp_path):
    reports_dir = tmp_path / "reports"
    report_dir = reports_dir / "sample"
    report_dir.mkdir(parents=True)
    (report_dir / "summary.json").write_text(
        json.dumps({"status": "PASS", "summary": {"checks": 1}}),
        encoding="utf-8",
    )

    logs_dir = tmp_path / "execution_logs"
    logs_dir.mkdir()
    (logs_dir / "sample-log.json").write_text(
        json.dumps(
            {
                "log_id": "sample-log",
                "command_id": "sample",
                "command_label": "Safe sample",
                "argv": ["python", "network_lab.py", "--help"],
                "working_directory": str(tmp_path),
                "started_at": "2026-07-16T10:00:00+08:00",
                "finished_at": "2026-07-16T10:00:01+08:00",
                "duration_seconds": 1.0,
                "status": "PASS",
                "exit_code": 0,
                "stdout": "sample",
                "stderr": "",
            }
        ),
        encoding="utf-8",
    )

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=logs_dir,
    )
    app.config.update(TESTING=True)
    return app, app.test_client()


def _parse(response):
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    parser = ShellParser()
    parser.feed(html)
    return html, parser


def test_phase_2o_01_preserves_exact_flask_route_and_method_contract(shell_client):
    app, _ = shell_client
    observed = {
        (rule.rule, rule.endpoint): frozenset(rule.methods - {"HEAD", "OPTIONS"})
        for rule in app.url_map.iter_rules()
    }
    expected = {
        ("/static/<path:filename>", "static"): frozenset({"GET"}),
        ("/", "home"): frozenset({"GET"}),
        ("/reports", "reports"): frozenset({"GET"}),
        ("/commands", "commands"): frozenset({"GET"}),
        ("/commands/<command_id>/run", "run_command"): frozenset({"POST"}),
        ("/commands/logs", "command_logs"): frozenset({"GET"}),
        ("/commands/logs/<log_id>", "command_log_detail"): frozenset({"GET"}),
        ("/ai-checklist", "ai_checklist"): frozenset({"GET"}),
        ("/ai-intent-reviewer", "ai_intent_reviewer"): frozenset({"GET"}),
        ("/reports/open/<path:report_path>", "open_report"): frozenset({"GET"}),
        ("/reports/json/<path:report_path>", "preview_json_report"): frozenset({"GET"}),
        ("/reports/evidence/<path:report_path>", "open_evidence_artifact"): frozenset({"GET"}),
        ("/reports/wireguard-vpn/<path:device_name>", "open_wireguard_vpn_report"): frozenset({"GET"}),
    }
    assert observed == expected


@pytest.mark.parametrize(
    ("path", "current_href"),
    (
        ("/", "/"),
        ("/reports", "/reports"),
        ("/commands", "/commands"),
        ("/commands/logs", "/commands/logs"),
        ("/commands/logs/sample-log", "/commands/logs"),
        ("/ai-checklist", "/ai-checklist"),
        ("/ai-intent-reviewer", "/ai-intent-reviewer"),
        ("/reports/json/sample/summary.json", "/reports"),
    ),
)
def test_all_eight_flask_views_render_one_accessible_shared_shell(
    shell_client, path, current_href
):
    _, client = shell_client
    html, parser = _parse(client.get(path))

    assert len([tag for tag, _ in parser.tags if tag == "main"]) == 1
    assert len([tag for tag, _ in parser.tags if tag == "h1"]) == 1
    assert any(
        tag == "html" and attrs.get("lang") == "en"
        for tag, attrs in parser.tags
    )
    assert any(
        tag == "main"
        and attrs.get("id") == "main-content"
        and attrs.get("tabindex") == "-1"
        for tag, attrs in parser.tags
    )
    assert any(
        tag == "a"
        and attrs.get("class") == "skip-link"
        and attrs.get("href") == "#main-content"
        for tag, attrs in parser.tags
    )
    assert any(
        tag == "nav" and attrs.get("aria-label") == "Primary navigation"
        for tag, attrs in parser.tags
    )

    assert [(link["text"], link["attrs"].get("href")) for link in parser.nav_links] == list(NAVIGATION)
    current_links = [
        link for link in parser.nav_links if link["attrs"].get("aria-current") == "page"
    ]
    assert len(current_links) == 1
    assert current_links[0]["attrs"]["href"] == current_href

    assert "Stage 0 canonical Flask reviewer surface" in html
    assert "display-only and report-only" in html
    assert "No provider or model access" in html
    assert "command execution" in html
    assert "live-device access" in html
    assert len([tag for tag, _ in parser.tags if tag == "form"]) == 0
    assert len([tag for tag, _ in parser.tags if tag == "button"]) == 0


def test_commands_remains_display_only_and_has_no_action_control(shell_client):
    _, client = shell_client
    html, parser = _parse(client.get("/commands"))

    assert "No command can be submitted or executed from this page" in html
    assert len([tag for tag, _ in parser.tags if tag == "form"]) == 0
    assert len([tag for tag, _ in parser.tags if tag == "button"]) == 0
    assert not any(
        tag == "input" and attrs.get("type", "").lower() in {"button", "submit"}
        for tag, attrs in parser.tags
    )


def test_target_views_inherit_the_shared_base_and_base_owns_shell_contract():
    templates_dir = Path("templates")
    for template_name in TARGET_TEMPLATES:
        source = (templates_dir / template_name).read_text(encoding="utf-8")
        assert source.startswith('{% extends "dashboard_base.html" %}')
        assert "<!doctype html>" not in source.lower()
        assert "<main" not in source.lower()
        assert "<nav" not in source.lower()

    base = (templates_dir / "dashboard_base.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in base.lower()
    assert 'class="skip-link"' in base
    assert 'aria-label="Primary navigation"' in base
    assert 'aria-current="page"' in base
    assert ':focus-visible' in base
    assert '@media (max-width: 760px)' in base
    assert '@media (max-width: 420px)' in base
    assert '<link rel="stylesheet"' not in base.lower()
    assert "http://" not in base and "https://" not in base


def test_phase_2o_01_adds_no_dependency_or_static_stylesheet():
    assert Path("requirements.txt").read_text(encoding="utf-8").splitlines() == [
        "paramiko>=3.4.0,<4.0.0",
        "pytest>=8.0.0,<9.0.0",
        "flask>=3.0.0,<4.0.0",
    ]
    assert not Path("static").exists()


def test_phase_2o_01_markdown_is_utf8_structured_and_repository_local_links_resolve():
    repository_root = Path.cwd().resolve()
    markdown_paths = (
        Path("README.md"),
        Path(
            "docs/phase_2o/"
            "phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md"
        ),
        Path(
            "docs/phase_2o/"
            "phase_2o_01_canonical_flask_shell_and_information_architecture_"
            "foundation_implementation.md"
        ),
    )

    for markdown_path in markdown_paths:
        source = markdown_path.read_bytes().decode("utf-8", errors="strict")
        headings = [line for line in source.splitlines() if line.startswith("#")]
        assert headings and headings[0].startswith("# ")
        assert source.count("```") % 2 == 0
        assert not re.search(r"^(<<<<<<<|=======|>>>>>>>)", source, re.MULTILINE)

        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", source):
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            relative_target = target.split("#", 1)[0]
            resolved = (markdown_path.parent / relative_target).resolve()
            assert resolved.is_relative_to(repository_root)
            assert resolved.exists(), f"Broken repository link: {markdown_path} -> {target}"
