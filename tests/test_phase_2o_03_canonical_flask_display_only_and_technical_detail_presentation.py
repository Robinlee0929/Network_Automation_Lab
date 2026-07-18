import json
import re
import socket
import subprocess
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import pytest

import dashboard_app as dashboard


TARGET_ROUTES = (
    "/commands",
    "/commands/logs",
    "/commands/logs/sample-log",
    "/reports/json/reports/sample/safe.json",
    "/ai-checklist",
    "/ai-intent-reviewer",
)

SUPERSEDED_ACTIVE_LABELS = (
    "Execution Logs",
    "Historical Demonstration Records",
    "Recent Execution Logs",
)


class PageProbe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.heading_levels = []
        self._heading_level = None
        self._heading_text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if re.fullmatch(r"h[1-6]", tag):
            self._heading_level = int(tag[1])
            self._heading_text = []

    def handle_data(self, data):
        if self._heading_level is not None:
            self._heading_text.append(data)

    def handle_endtag(self, tag):
        if self._heading_level is not None and tag == f"h{self._heading_level}":
            self.heading_levels.append(
                (self._heading_level, "".join(self._heading_text).strip())
            )
            self._heading_level = None
            self._heading_text = []

    def count(self, tag):
        return sum(1 for observed, _ in self.tags if observed == tag)


@pytest.fixture()
def phase_2o_03_surface(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    report_dir = reports_dir / "sample"
    report_dir.mkdir(parents=True)
    (report_dir / "safe.json").write_text(
        json.dumps(
            {
                "schema_version": "phase2o03.safe.v1",
                "title": "Bounded reviewer evidence",
                "status": "PASS",
                "mode": "report_only",
                "arbitrary_summary_sentinel": "SUMMARY-SENTINEL-NOT-ALLOWLISTED",
                "password": "JSON-SECRET-SENTINEL",
                "provider": "STRUCTURED-PROVIDER-SENTINEL",
                "Provider-Name": "MIXED-PROVIDER-SENTINEL",
                "model": "STRUCTURED-MODEL-SENTINEL",
                "model_name": "STRUCTURED-MODEL-NAME-SENTINEL",
                "MODEL_id": "MIXED-MODEL-SENTINEL",
                "private_path": (
                    r"C:\Users\Synthetic Reviewer\Private Folder\evidence file.json"
                ),
                "forward_private_path": (
                    "C:/Users/Synthetic Reviewer/Private Folder/forward evidence.json"
                ),
                "management_address": "192.168.44.10",
                "nested": {
                    "model-config": "NESTED-MODEL-SENTINEL",
                    "runtime_provider": "NESTED-PROVIDER-SENTINEL",
                    "safe_note": "sanitized subordinate detail",
                },
            }
        ),
        encoding="utf-8",
    )
    (report_dir / "malformed.json").write_text("{not valid json", encoding="utf-8")
    (report_dir / "unsupported.txt").write_text("not json", encoding="utf-8")

    logs_dir = tmp_path / "execution_logs"
    logs_dir.mkdir()
    long_output = (
        "first line\nsecond line\n"
        "token=OUTPUT-SECRET-SENTINEL\n"
        "provider=OUTPUT-PROVIDER-SENTINEL\n"
        "model: OUTPUT-MODEL-SENTINEL\n"
        "MODEL_NAME = OUTPUT-MODEL-NAME-SENTINEL\n"
        '{"Provider-Id":"OUTPUT-PROVIDER-ID-SENTINEL"}\n'
        'quoted private path "C:\\Users\\Synthetic Reviewer\\Private Folder\\result file.txt"\n'
        "forward private path C:/Users/Synthetic Reviewer/Private Folder/forward result.txt\n"
        "private address 10.10.10.10\n"
        + ("LONG-UNBROKEN-CONTENT-" * 420)
    )
    (logs_dir / "sample-log.json").write_text(
        json.dumps(
            {
                "log_id": "sample-log",
                "command_id": "pytest_all",
                "command_label": "Static pytest reference",
                "argv": ["ARGV-PRIVATE-SENTINEL"],
                "working_directory": r"C:\Users\private-reviewer\workspace",
                "started_at": "2026-07-18T09:00:00+08:00",
                "finished_at": "2026-07-18T09:00:01+08:00",
                "duration_seconds": 1.125,
                "status": "PASS",
                "exit_code": 0,
                "stdout": long_output,
                "stderr": "",
            }
        ),
        encoding="utf-8",
    )

    execution_calls = []

    def execution_must_not_run(*args, **kwargs):
        execution_calls.append((args, kwargs))
        raise AssertionError("GET presentation reached command execution")

    monkeypatch.setattr(dashboard, "execute_registered_command", execution_must_not_run)
    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=logs_dir,
    )
    app.config.update(TESTING=True)
    return app, app.test_client(), execution_calls, reports_dir


def _page(response):
    assert response.status_code == 200
    source = response.get_data(as_text=True)
    probe = PageProbe()
    probe.feed(source)
    return source, probe


def test_exact_six_target_routes_remain_get_only_and_existing_post_is_unchanged(
    phase_2o_03_surface,
):
    app, _, _, _ = phase_2o_03_surface
    target_rules = {
        rule.rule: frozenset(rule.methods - {"HEAD", "OPTIONS"})
        for rule in app.url_map.iter_rules()
        if rule.rule
        in {
            "/commands",
            "/commands/logs",
            "/commands/logs/<log_id>",
            "/reports/json/<path:report_path>",
            "/ai-checklist",
            "/ai-intent-reviewer",
        }
    }

    assert target_rules == {
        "/commands": frozenset({"GET"}),
        "/commands/logs": frozenset({"GET"}),
        "/commands/logs/<log_id>": frozenset({"GET"}),
        "/reports/json/<path:report_path>": frozenset({"GET"}),
        "/ai-checklist": frozenset({"GET"}),
        "/ai-intent-reviewer": frozenset({"GET"}),
    }
    post_rule = next(
        rule for rule in app.url_map.iter_rules() if rule.rule == "/commands/<command_id>/run"
    )
    assert frozenset(post_rule.methods - {"HEAD", "OPTIONS"}) == frozenset({"POST"})


def test_all_six_get_surfaces_have_no_action_markup_and_reach_no_execution_path(
    phase_2o_03_surface,
):
    _, client, execution_calls, _ = phase_2o_03_surface

    for path in TARGET_ROUTES:
        source, probe = _page(client.get(path))
        assert probe.count("form") == 0
        assert probe.count("button") == 0
        assert probe.count("input") == 0
        assert probe.count("script") == 0
        assert 'method="post"' not in source.lower()
        assert "javascript:" not in source.lower()

    assert execution_calls == []


def test_all_six_get_surfaces_reach_no_forbidden_indirect_side_effect_primitive(
    phase_2o_03_surface, monkeypatch
):
    app, client, execution_calls, _ = phase_2o_03_surface
    forbidden_attempts = []

    def fail_forbidden(name):
        def fail(*args, **kwargs):
            forbidden_attempts.append((name, args, kwargs))
            raise AssertionError(f"GET presentation reached forbidden primitive: {name}")

        return fail

    monkeypatch.setattr(subprocess, "run", fail_forbidden("subprocess.run"))
    monkeypatch.setattr(subprocess, "Popen", fail_forbidden("subprocess.Popen"))
    monkeypatch.setattr(socket, "create_connection", fail_forbidden("socket.connect"))
    monkeypatch.setattr(urllib.request, "urlopen", fail_forbidden("provider-http"))
    for attribute in ("write_text", "write_bytes", "mkdir", "touch"):
        monkeypatch.setattr(Path, attribute, fail_forbidden(f"Path.{attribute}"))

    forbidden_route_names = {
        "execute_registered_command",
        "create_job",
        "import_report",
        "provider_model_runtime_call",
        "write_text",
        "write_bytes",
        "urlopen",
        "create_connection",
        "Popen",
    }
    for endpoint in (
        "commands",
        "command_logs",
        "command_log_detail",
        "preview_json_report",
        "ai_checklist",
        "ai_intent_reviewer",
    ):
        assert forbidden_route_names.isdisjoint(
            app.view_functions[endpoint].__code__.co_names
        )

    for path in TARGET_ROUTES:
        assert client.get(path).status_code == 200

    assert execution_calls == []
    assert forbidden_attempts == []


def test_canonical_historical_terminology_and_conclusion_first_safety_copy(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface
    commands, _ = _page(client.get("/commands"))
    collection, collection_probe = _page(client.get("/commands/logs"))
    detail, detail_probe = _page(client.get("/commands/logs/sample-log"))

    for source in (commands, collection, detail):
        assert "Historical Execution Records" in source
        for superseded in SUPERSEDED_ACTIVE_LABELS:
            assert superseded not in source

    assert commands.index("Conclusion: static allowlist reference only") < commands.index(
        "Registered Command Examples"
    )
    assert collection.index("Conclusion: historical evidence only") < collection.index(
        "Recorded status, timestamp, bounded identity"
    )
    assert detail.index("Conclusion: recorded historical evidence") < detail.index(
        "Recorded summary"
    )
    assert collection_probe.count("table") == 1
    assert collection_probe.count("caption") == 1
    assert detail_probe.count("dl") == 1
    assert detail_probe.count("details") == 2
    assert detail_probe.count("summary") == 2


def test_command_entries_and_examples_are_static_bounded_references(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface
    source, _ = _page(client.get("/commands"))

    assert "static allowlist reference only" in source
    assert "Registered Command Examples" in source
    assert "Static Command Examples" in source
    assert "No command can be submitted or executed from this page" in source
    assert "Reference key:" in source
    assert "working_directory" not in source
    assert "sys.executable" not in source


def test_historical_detail_bounds_output_preserves_whitespace_and_hides_prohibited_data(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface
    source, _ = _page(client.get("/commands/logs/sample-log"))
    projected = dashboard.project_execution_log(
        {
            "log_id": "sample-log",
            "stdout": "line one\nline two\n" + ("x" * 9000),
            "stderr": "",
        }
    )

    assert "first line\nsecond line" in source
    assert "Preview truncated:" in source
    assert "OUTPUT-SECRET-SENTINEL" not in source
    assert "OUTPUT-PROVIDER-SENTINEL" not in source
    assert "OUTPUT-MODEL-SENTINEL" not in source
    assert "OUTPUT-MODEL-NAME-SENTINEL" not in source
    assert "OUTPUT-PROVIDER-ID-SENTINEL" not in source
    assert "Synthetic Reviewer" not in source
    assert "Private Folder" not in source
    assert "result file.txt" not in source
    assert "forward result.txt" not in source
    assert dashboard.PROVIDER_MODEL_REDACTION in source
    assert dashboard.PRIVATE_PATH_REDACTION in source
    assert "10.10.10.10" not in source
    assert "ARGV-PRIVATE-SENTINEL" not in source
    assert "working directory" not in source.lower()
    assert len(projected["stdout_preview"]["text"]) <= dashboard.OUTPUT_PREVIEW_MAX_CHARS
    assert projected["stdout_preview"]["truncated"] is True


def test_historical_output_provider_model_forms_and_private_paths_are_fully_redacted():
    provider_model_text = (
        "provider=PROVIDER-EQUALS-SENTINEL\n"
        "model: MODEL-COLON-SENTINEL\n"
        "Model-Name = MODEL-NAME-SENTINEL\n"
        '{"Provider_Id":"PROVIDER-JSON-SENTINEL"}'
    )
    redacted_provider_model = dashboard._redact_prohibited_text(provider_model_text)
    for sentinel in (
        "PROVIDER-EQUALS-SENTINEL",
        "MODEL-COLON-SENTINEL",
        "MODEL-NAME-SENTINEL",
        "PROVIDER-JSON-SENTINEL",
    ):
        assert sentinel not in redacted_provider_model
    assert dashboard.PROVIDER_MODEL_REDACTION in redacted_provider_model
    ordinary_prose = "This explanatory model remains ordinary reviewer prose."
    assert dashboard._redact_prohibited_text(ordinary_prose) == ordinary_prose

    path_cases = (
        r"C:\Users\Synthetic Reviewer\Private Folder\evidence file.json",
        r'"C:\Users\Synthetic Reviewer\Private Folder\quoted evidence.json"',
        "path=C:/Users/Synthetic Reviewer/Private Folder/forward evidence.json,",
        (
            "[C:\\Users\\Synthetic Reviewer\\Private Folder\\bracketed evidence.json]"
            "\nSAFE-NEXT-LINE"
        ),
    )
    for source_path in path_cases:
        redacted_path = dashboard._redact_prohibited_text(source_path)
        assert "Synthetic Reviewer" not in redacted_path
        assert "Reviewer" not in redacted_path
        assert "Private Folder" not in redacted_path
        assert "evidence" not in redacted_path
        assert dashboard.PRIVATE_PATH_REDACTION in redacted_path


def test_output_and_json_preview_limits_hold_exactly_at_and_one_over_boundaries():
    exact_lines = "\n".join(
        f"bounded-line-{index}" for index in range(dashboard.OUTPUT_PREVIEW_MAX_LINES)
    )
    at_line_limit = dashboard._bounded_output_preview(exact_lines)
    over_line_limit = dashboard._bounded_output_preview(
        f"{exact_lines}\nmodel=DISCARDED-LINE-SENTINEL"
    )
    assert at_line_limit["truncated"] is False
    assert len(at_line_limit["text"].splitlines()) == dashboard.OUTPUT_PREVIEW_MAX_LINES
    assert over_line_limit["truncated"] is True
    assert len(over_line_limit["text"].splitlines()) == dashboard.OUTPUT_PREVIEW_MAX_LINES
    assert "DISCARDED-LINE-SENTINEL" not in over_line_limit["text"]

    exact_chars = "x" * dashboard.OUTPUT_PREVIEW_MAX_CHARS
    at_char_limit = dashboard._bounded_output_preview(exact_chars)
    over_char_limit = dashboard._bounded_output_preview(
        exact_chars + "DISCARDED-CHAR-SENTINEL"
    )
    assert at_char_limit == {"text": exact_chars, "truncated": False}
    assert over_char_limit == {"text": exact_chars, "truncated": True}
    assert "DISCARDED-CHAR-SENTINEL" not in over_char_limit["text"]

    empty_detail_size = len(json.dumps({"allowed": ""}, indent=2, sort_keys=True))
    exact_json = {
        "allowed": "j" * (dashboard.JSON_PREVIEW_MAX_CHARS - empty_detail_size)
    }
    at_json_limit = dashboard._bounded_json_detail(exact_json)
    over_json_limit = dashboard._bounded_json_detail(
        {"allowed": exact_json["allowed"] + "k"}
    )
    assert len(at_json_limit["text"]) == dashboard.JSON_PREVIEW_MAX_CHARS
    assert at_json_limit["truncated"] is False
    assert len(over_json_limit["text"]) == dashboard.JSON_PREVIEW_MAX_CHARS
    assert over_json_limit["truncated"] is True


def test_json_preview_uses_normalized_allowlist_and_bounded_sanitized_detail(
    phase_2o_03_surface,
):
    _, client, _, reports_root = phase_2o_03_surface
    source, probe = _page(
        client.get("/reports/json/reports/sample/safe.json")
    )
    summary = re.search(
        r'<section aria-labelledby="json-summary-heading">(.*?)</section>',
        source,
        re.DOTALL,
    )

    assert summary is not None
    assert "Normalized status" in summary.group(1)
    assert "PASS" in summary.group(1)
    assert "schema_version" in summary.group(1)
    assert "title" in summary.group(1)
    assert "mode" in summary.group(1)
    assert "arbitrary_summary_sentinel" not in summary.group(1)
    assert "SUMMARY-SENTINEL-NOT-ALLOWLISTED" not in summary.group(1)
    assert "JSON-SECRET-SENTINEL" not in source
    assert "STRUCTURED-PROVIDER-SENTINEL" not in source
    assert "MIXED-PROVIDER-SENTINEL" not in source
    assert "STRUCTURED-MODEL-SENTINEL" not in source
    assert "STRUCTURED-MODEL-NAME-SENTINEL" not in source
    assert "MIXED-MODEL-SENTINEL" not in source
    assert "NESTED-MODEL-SENTINEL" not in source
    assert "NESTED-PROVIDER-SENTINEL" not in source
    assert "Provider-Name" not in source
    assert "MODEL_id" not in source
    assert "model_name" not in source
    assert "model-config" not in source
    assert "runtime_provider" not in source
    assert "Synthetic Reviewer" not in source
    assert "Private Folder" not in source
    assert "evidence file.json" not in source
    assert "forward evidence.json" not in source
    assert "sanitized subordinate detail" in source
    assert "192.168.44.10" not in source
    assert "[REDACTED]" in source
    assert dashboard.PRIVATE_PATH_REDACTION in source
    assert dashboard.sanitize_json_preview({"note": "192.168.44.10"}) == {
        "note": "[REDACTED PRIVATE ADDRESS]"
    }
    assert probe.count("table") == 1
    assert probe.count("caption") == 1
    assert probe.count("details") == 1
    assert probe.count("summary") == 1

    preview_path = reports_root / "sample" / "safe.json"
    preview = dashboard.load_json_preview(preview_path)
    assert preview_path.is_file()
    assert '"model"' not in preview["pretty"]
    assert "model_name" not in preview["pretty"]
    assert "Provider-Name" not in preview["pretty"]
    assert "MODEL_id" not in preview["pretty"]
    assert "model-config" not in preview["pretty"]
    assert "runtime_provider" not in preview["pretty"]
    assert "sanitized subordinate detail" in preview["pretty"]
    assert set(preview["summary"]).isdisjoint(
        {"provider", "Provider-Name", "model", "model_name", "MODEL_id"}
    )
    ordered = dashboard.sanitize_json_preview(
        {
            "allowed_before": "before",
            "model-name": "ORDER-MODEL-SENTINEL",
            "allowed_after": "after",
        }
    )
    assert list(ordered) == ["allowed_before", "allowed_after"]
    assert ordered == {"allowed_before": "before", "allowed_after": "after"}


def test_json_malformed_unreadable_missing_traversal_and_extension_states_are_safe(
    phase_2o_03_surface, tmp_path, monkeypatch
):
    _, client, _, _ = phase_2o_03_surface
    malformed, _ = _page(
        client.get("/reports/json/reports/sample/malformed.json")
    )

    assert "MALFORMED" in malformed
    assert "malformed and cannot be previewed safely" in malformed
    assert "JSONDecodeError" not in malformed
    assert "Traceback" not in malformed
    assert client.get("/reports/json/reports/sample/missing.json").status_code == 404
    assert client.get("/reports/json/../outside.json").status_code == 404
    assert client.get("/reports/json/reports/sample/unsupported.txt").status_code == 404

    unreadable = tmp_path / "unreadable.json"
    unreadable.write_text("{}", encoding="utf-8")
    original_read_text = Path.read_text

    def fail_selected_read(path, *args, **kwargs):
        if path == unreadable:
            raise OSError(r"C:\Users\private-reviewer\raw-error.txt")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_selected_read)
    preview = dashboard.load_json_preview(unreadable)
    assert preview == {
        "status": "UNKNOWN",
        "summary": {},
        "pretty": "",
        "pretty_truncated": False,
        "state_copy": "This JSON evidence is unavailable and cannot be previewed safely.",
    }


def test_ai_surfaces_are_static_historical_or_design_time_reviewer_evidence(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface
    checklist, checklist_probe = _page(client.get("/ai-checklist"))
    reviewer, reviewer_probe = _page(client.get("/ai-intent-reviewer"))

    assert "static reviewer evidence only" in checklist
    assert "grants no runtime, provider, model, command, or live-device authority" in checklist
    assert "STATIC EVIDENCE" in checklist
    assert checklist_probe.count("table") == 1
    assert checklist_probe.count("caption") == 1

    assert "historical and design-time reviewer evidence only" in reviewer
    assert "REVIEW EVIDENCE ONLY" in reviewer
    assert "Runtime status" in reviewer
    assert "NOT ENABLED" in reviewer
    assert "STAGE 0 · DISPLAY-ONLY · NO EXECUTION AUTHORITY" in reviewer
    assert reviewer_probe.count("dl") >= 1


def test_all_target_pages_preserve_heading_semantics_stage_zero_and_non_color_text(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface

    for path in TARGET_ROUTES:
        source, probe = _page(client.get(path))
        assert probe.count("h1") == 1
        assert probe.heading_levels[0][0] == 1
        for previous, current in zip(probe.heading_levels, probe.heading_levels[1:]):
            assert current[0] <= previous[0] + 1
        assert "Stage 0 canonical Flask reviewer surface" in source
        assert any(probe.count(tag) for tag in ("table", "ul", "ol", "dl"))

    collection, _ = _page(client.get("/commands/logs"))
    detail, _ = _page(client.get("/commands/logs/sample-log"))
    json_page, _ = _page(client.get("/reports/json/reports/sample/safe.json"))
    assert "PASS" in collection
    assert "PASS" in detail
    assert "PASS" in json_page


def test_rendered_detail_pages_expose_closed_keyboard_focusable_bounded_disclosures(
    phase_2o_03_surface,
):
    _, client, _, _ = phase_2o_03_surface
    log_source, log_probe = _page(client.get("/commands/logs/sample-log"))
    json_source, json_probe = _page(
        client.get("/reports/json/reports/sample/safe.json")
    )

    assert log_probe.count("details") == 2
    assert log_probe.count("summary") == 2
    assert json_probe.count("details") == 1
    assert json_probe.count("summary") == 1
    for probe in (log_probe, json_probe):
        detail_attributes = [attrs for tag, attrs in probe.tags if tag == "details"]
        assert detail_attributes
        assert all("open" not in attrs for attrs in detail_attributes)

    for source in (log_source, json_source):
        assert "summary:focus-visible" in source
        assert "outline: 3px solid" in source
        assert 'class="bounded-code"' in source
        assert "overflow-wrap: anywhere" in source
        assert "max-height: 28rem" in source
        assert "@media (max-width: 420px)" in source

    assert '<div class="table-wrap">' in json_source
    assert ".table-wrap { max-width: 100%; overflow-x: auto; }" in json_source
    assert "@media (max-width: 620px)" in json_source


def test_shared_css_exposes_focus_reflow_and_bounded_overflow_contracts():
    base = Path("templates/dashboard_base.html").read_text(encoding="utf-8")
    combined = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "templates/dashboard_base.html",
            "templates/dashboard_commands.html",
            "templates/dashboard_command_logs.html",
            "templates/dashboard_command_log.html",
            "templates/dashboard_json_preview.html",
            "templates/dashboard_ai_checklist.html",
            "templates/dashboard_ai_intent_reviewer.html",
        )
    )

    assert ":focus-visible" in base
    assert "summary:focus-visible" in base
    assert "outline: 3px solid" in base
    assert "@media (max-width: 420px)" in base
    assert "@media (max-width: 620px)" in combined
    assert "@media (max-width: 720px)" in combined
    assert ".table-wrap { max-width: 100%; overflow-x: auto; }" in base
    assert ".bounded-code" in base
    assert "max-height: 28rem" in base
    assert "overflow-wrap: anywhere" in base
    assert "main > *, section, article, details, dl, dd { min-width: 0; }" in base


def test_phase_2o_03_adds_no_dependency_or_external_stylesheet():
    assert Path("requirements.txt").read_text(encoding="utf-8").splitlines() == [
        "paramiko>=3.4.0,<4.0.0",
        "pytest>=8.0.0,<9.0.0",
        "flask>=3.0.0,<4.0.0",
    ]
    base = Path("templates/dashboard_base.html").read_text(encoding="utf-8")
    assert '<link rel="stylesheet"' not in base.lower()
    assert "http://" not in base and "https://" not in base
