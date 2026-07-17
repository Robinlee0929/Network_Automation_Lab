import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

import dashboard_app as dashboard


AUTHORIZED_FILTERS = (
    "ALL",
    "PASS",
    "WARN",
    "FAIL",
    "MISSING",
    "UNKNOWN",
    "MALFORMED",
    "UNAVAILABLE",
)


def _entry(
    status,
    *,
    availability="FOUND",
    slug=None,
    available=True,
    device="review-scope",
    description="Existing technical detail.",
    notes="",
):
    slug = slug or str(status).lower()
    json_path = f"reports/sample/{slug}.json"
    html_path = f"reports/sample/{slug}.html"
    return dashboard.DashboardEvidenceEntry(
        title=f"{slug.title()} evidence",
        day=f"Day {slug.title()}",
        device=device,
        report_type="Validation evidence",
        status=status,
        availability=availability,
        json_path=json_path,
        html_path=html_path,
        description=description,
        notes=notes,
        json_view_path=json_path if available else None,
        html_view_path=html_path if available else None,
    )


def _status_entries():
    return [
        _entry("PASS", slug="pass"),
        _entry("WARNING", slug="warn"),
        _entry("FAIL", slug="fail"),
        _entry("MISSING", availability="MISSING", slug="missing", available=False),
        _entry("UNKNOWN", slug="unknown"),
        _entry("MALFORMED", slug="malformed"),
        _entry(
            "UNAVAILABLE",
            availability="UNAVAILABLE",
            slug="unavailable",
            available=False,
        ),
        _entry("FOUND", slug="found-availability-only"),
    ]


def _home_reports():
    return [
        dashboard.ReportEntry(
            device="review-scope",
            filename="day4_baseline_validation.json",
            report_type="Day4 baseline",
            file_type="JSON",
            status="PASS",
            relative_path="review/day4_baseline_validation.json",
            html_relative_path="review/day4_baseline_validation.html",
            modified_at="2026-07-17 12:00:00",
        ),
        dashboard.ReportEntry(
            device="review-scope",
            filename="day9_performance_regression_report.json",
            report_type="Day9 performance regression",
            file_type="JSON",
            status="WARNING",
            relative_path="review/day9_performance_regression_report.json",
            html_relative_path="review/day9_performance_regression_report.html",
            modified_at="2026-07-17 12:00:00",
        ),
    ]


def _write_safe_drilldown_files(reports_dir, entries):
    for entry in entries:
        if not entry.json_view_path:
            continue
        relative_json = Path(entry.json_view_path).relative_to("reports")
        relative_html = Path(entry.html_view_path).relative_to("reports")
        json_path = reports_dir / relative_json
        html_path = reports_dir / relative_html
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps({"status": entry.status}), encoding="utf-8")
        html_path.write_text("<html><body>Safe evidence</body></html>", encoding="utf-8")


@pytest.fixture()
def phase_surface(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    entries = _status_entries()
    _write_safe_drilldown_files(reports_dir, entries)

    monkeypatch.setattr(dashboard, "discover_reports", lambda _path: _home_reports())
    monkeypatch.setattr(
        dashboard,
        "collect_dashboard_evidence",
        lambda _root, _reports: list(entries),
    )
    monkeypatch.setattr(dashboard, "discover_vrrp_evidence", lambda _root: [])
    monkeypatch.setattr(dashboard, "build_day12_dashboard_summaries", lambda _path: [])

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    app.config.update(TESTING=True)
    return app, app.test_client(), entries


def _html(response):
    assert response.status_code == 200
    return response.data.decode("utf-8")


def _plain_text(source):
    return " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", source)).split()
    )


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self._active = None

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._active = [int(tag[1]), []]

    def handle_data(self, data):
        if self._active:
            self._active[1].append(data)

    def handle_endtag(self, tag):
        if self._active and tag == f"h{self._active[0]}":
            self.headings.append(
                (self._active[0], "".join(self._active[1]).strip())
            )
            self._active = None


def test_phase_2o_02_preserves_exact_route_and_method_contract(phase_surface):
    app, _, _ = phase_surface
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


def test_home_is_conclusion_first_and_retains_canonical_stage_0_copy(phase_surface):
    _, client, _ = phase_surface
    source = _html(client.get("/"))

    assert source.index("Reviewer conclusion:") < source.index("Evidence Health")
    assert source.index("Evidence Health") < source.index("Key Proof Points")
    assert "Stage 0 canonical Flask reviewer surface" in source
    assert "report-only Stage 0 boundaries" in source
    assert "never triggers live collection" in source


def test_home_evidence_health_uses_only_normalized_safe_card_fields():
    cards = dashboard.build_home_evidence_health_cards(_home_reports())

    assert all(
        set(card)
        == {
            "home_card_title",
            "home_card_normalized_status",
            "home_card_missing_flag",
        }
        for card in cards
    )
    by_title = {card["home_card_title"]: card for card in cards}
    assert by_title["MikroTik baseline"] == {
        "home_card_title": "MikroTik baseline",
        "home_card_normalized_status": "PASS",
        "home_card_missing_flag": False,
    }
    assert by_title["Performance regression"]["home_card_normalized_status"] == "WARN"
    assert by_title["WireGuard VPN"]["home_card_normalized_status"] == "MISSING"
    assert by_title["WireGuard VPN"]["home_card_missing_flag"] is True


def test_reports_summary_has_deterministic_exact_counts_and_separates_availability():
    summary = dashboard.build_reports_summary(
        _status_entries(),
        reports_directory_present=True,
    )

    assert summary == {
        "reports_directory_present": True,
        "available_evidence_present": True,
        "total_count": 8,
        "available_count": 6,
        "pass_count": 1,
        "warn_count": 1,
        "fail_count": 1,
        "missing_count": 1,
        "unknown_count": 2,
        "malformed_count": 1,
        "unavailable_count": 1,
        "filtered_count": 8,
        "active_status_filter": "ALL",
        "collection_state": "MALFORMED",
    }


def test_found_is_availability_only_and_is_never_counted_as_pass():
    entry = _entry("FOUND", availability="FOUND", slug="found")
    summary = dashboard.build_reports_summary(
        [entry],
        reports_directory_present=True,
    )

    assert entry.evidence_availability_state == "FOUND"
    assert entry.evidence_normalized_result_status == "UNKNOWN"
    assert summary["available_count"] == 1
    assert summary["pass_count"] == 0
    assert summary["unknown_count"] == 1


@pytest.mark.parametrize(
    ("status_filter", "expected_count"),
    (
        ("ALL", 8),
        ("PASS", 1),
        ("WARN", 1),
        ("FAIL", 1),
        ("MISSING", 1),
        ("UNKNOWN", 2),
        ("MALFORMED", 1),
        ("UNAVAILABLE", 1),
    ),
)
def test_every_allowlisted_get_filter_has_server_derived_count(
    phase_surface, status_filter, expected_count
):
    _, client, _ = phase_surface
    source = _html(client.get("/reports", query_string={"status": status_filter}))
    text = _plain_text(source)

    assert f"{expected_count} of 8 evidence items match {status_filter}" in text
    assert f'href="/reports?status={status_filter}" aria-current="page"' in source
    assert f"{status_filter} (current)" in text


@pytest.mark.parametrize(
    "invalid_filter",
    (
        "FOUND",
        "../../private/path",
        '<script>alert("unsafe")</script>',
        "PASS%00token",
    ),
)
def test_invalid_filters_fall_back_to_all_without_echo(phase_surface, invalid_filter):
    _, client, _ = phase_surface
    source = _html(client.get("/reports", query_string={"status": invalid_filter}))
    text = _plain_text(source)

    assert "8 of 8 evidence items match ALL" in text
    assert "ALL (current)" in text
    if invalid_filter != "FOUND":
        assert invalid_filter not in source


def test_filter_links_are_get_only_with_no_form_input_button_or_javascript(phase_surface):
    _, client, _ = phase_surface
    source = _html(client.get("/reports"))
    template = Path("templates/dashboard_reports.html").read_text(encoding="utf-8")

    for status_filter in AUTHORIZED_FILTERS:
        assert f'href="/reports?status={status_filter}"' in source
    assert "<form" not in source.lower()
    assert "<input" not in source.lower()
    assert "<button" not in source.lower()
    assert "<script" not in template.lower()
    assert 'method="post"' not in source.lower()


def test_native_disclosures_use_safe_summary_fields_and_safe_get_drilldowns(phase_surface):
    _, client, entries = phase_surface
    source = _html(client.get("/reports?status=PASS"))

    assert source.count('<details class="evidence-disclosure">') == 1
    assert source.count("<summary>") == 1
    assert "Pass evidence" in source
    assert "Validation evidence" in source
    assert "Result: PASS" in source
    assert "Availability: FOUND" in source
    assert 'href="/reports/json/reports/sample/pass.json"' in source
    assert 'href="/reports/open/reports/sample/pass.html"' in source
    assert entries[0].evidence_normalized_result_status == "PASS"


def test_disclosure_headings_do_not_promote_prohibited_technical_fields(tmp_path, monkeypatch):
    sentinel = "PRIVATE-SUMMARY-SENTINEL"
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    entry = _entry(
        "PASS",
        slug="safe-title",
        device=f"device-{sentinel}",
        description=f"description-{sentinel}",
        notes=f"notes-{sentinel}",
    )
    monkeypatch.setattr(dashboard, "collect_dashboard_evidence", lambda *_args: [entry])
    monkeypatch.setattr(dashboard, "discover_vrrp_evidence", lambda *_args: [])
    monkeypatch.setattr(dashboard, "build_day12_dashboard_summaries", lambda *_args: [])
    app = dashboard.create_app(reports_dir=reports_dir, execution_logs_dir=tmp_path / "logs")

    source = _html(app.test_client().get("/reports"))
    summary_markup = " ".join(re.findall(r"<summary>(.*?)</summary>", source, re.DOTALL))
    overview_markup = re.search(
        r'<section class="reports-overview".*?</section>', source, re.DOTALL
    ).group(0)

    assert sentinel not in summary_markup
    assert sentinel not in overview_markup
    assert "report.device" not in re.search(
        r"<summary>(.*?)</summary>",
        Path("templates/dashboard_reports.html").read_text(encoding="utf-8"),
        re.DOTALL,
    ).group(1)


@pytest.mark.parametrize(
    ("entries", "directory_present", "collection_error", "expected"),
    (
        ([_entry("PASS")], True, False, "READY"),
        ([], True, False, "EMPTY"),
        ([], False, False, "MISSING"),
        ([_entry("MALFORMED")], True, False, "MALFORMED"),
        (
            [
                _entry("PASS", slug="available"),
                _entry(
                    "UNAVAILABLE",
                    availability="UNAVAILABLE",
                    available=False,
                ),
            ],
            True,
            False,
            "UNAVAILABLE",
        ),
        ([], True, True, "ERROR"),
    ),
)
def test_collection_state_precedence_is_deterministic(
    entries, directory_present, collection_error, expected
):
    summary = dashboard.build_reports_summary(
        entries,
        reports_directory_present=directory_present,
        collection_error=collection_error,
    )
    assert summary["collection_state"] == expected


def test_error_state_uses_fixed_safe_copy_without_raw_exception(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    raw_error = r"C:\Users\private\secret-token.json"

    def fail_safely(*_args):
        raise RuntimeError(raw_error)

    monkeypatch.setattr(dashboard, "collect_dashboard_evidence", fail_safely)
    app = dashboard.create_app(reports_dir=reports_dir, execution_logs_dir=tmp_path / "logs")
    source = _html(app.test_client().get("/reports"))

    assert 'data-collection-state="ERROR"' in source
    assert "Evidence collection could not be summarized safely" in source
    assert raw_error not in source
    assert "secret-token" not in source
    assert "Traceback" not in source


def test_filter_no_match_uses_fixed_safe_state_copy(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    monkeypatch.setattr(
        dashboard,
        "collect_dashboard_evidence",
        lambda *_args: [_entry("PASS")],
    )
    monkeypatch.setattr(dashboard, "discover_vrrp_evidence", lambda *_args: [])
    monkeypatch.setattr(dashboard, "build_day12_dashboard_summaries", lambda *_args: [])
    app = dashboard.create_app(reports_dir=reports_dir, execution_logs_dir=tmp_path / "logs")
    source = _html(app.test_client().get("/reports?status=FAIL"))

    assert 'data-collection-state="FILTER_NO_MATCH"' in source
    assert "Filter result: no match" in source
    assert "No evidence items match the selected allowlisted status" in source


def test_home_and_reports_get_never_reach_execution_function(phase_surface, monkeypatch):
    _, client, _ = phase_surface

    def execution_must_not_run(*_args, **_kwargs):
        raise AssertionError("execution function reached")

    monkeypatch.setattr(dashboard, "execute_registered_command", execution_must_not_run)

    assert client.get("/").status_code == 200
    assert client.get("/reports").status_code == 200


def test_home_and_reports_render_no_action_or_execution_control(phase_surface):
    _, client, _ = phase_surface
    for path in ("/", "/reports"):
        source = _html(client.get(path)).lower()
        assert "<form" not in source
        assert "<button" not in source
        assert 'method="post"' not in source
        assert "/commands/sample/run" not in source
        assert ">run<" not in source
        assert ">execute<" not in source


def test_statuses_remain_understandable_without_color(phase_surface):
    _, client, _ = phase_surface
    source = _html(client.get("/reports"))
    text = _plain_text(source)

    for status in dashboard.EVIDENCE_RESULT_STATUSES:
        assert f"{status} results" in text
    assert "Result: PASS" in text
    assert "Availability: FOUND" in text
    assert "Collection state: MALFORMED" in text


def test_home_and_reports_have_one_h1_and_logical_heading_order(phase_surface):
    _, client, _ = phase_surface
    for path in ("/", "/reports"):
        parser = HeadingParser()
        parser.feed(_html(client.get(path)))
        levels = [level for level, _text in parser.headings]
        assert levels.count(1) == 1
        assert levels[0] == 1
        assert all(current <= previous + 1 for previous, current in zip(levels, levels[1:]))


def test_filter_and_disclosure_focus_and_responsive_source_contracts():
    source = Path("templates/dashboard_reports.html").read_text(encoding="utf-8")

    assert ".filters" in source and "flex-wrap: wrap" in source
    assert ".table-wrap { max-width: 100%; overflow-x: auto; }" in source
    assert ".filter-link:focus-visible, summary:focus-visible" in source
    assert "outline: 3px solid" in source
    assert "@media (max-width: 520px)" in source
    assert '<details class="evidence-disclosure">' in source
    assert "<summary>" in source


def test_canonical_report_index_copy_replaces_stale_copy():
    source = Path("templates/dashboard_reports.html").read_text(encoding="utf-8")

    assert "python network_lab.py --task report-index" in source
    assert "python network_lab.py --report-index" not in source


def test_existing_safe_report_routes_and_path_controls_remain_intact(phase_surface):
    _, client, _ = phase_surface

    assert client.get("/reports/json/reports/sample/pass.json").status_code == 200
    assert client.get("/reports/open/reports/sample/pass.html").status_code == 200
    assert client.get("/reports/json/../secret.json").status_code == 404
    assert client.get("/reports/open/../secret.html").status_code == 404
    assert client.get("/reports/evidence/../secret.txt").status_code == 404


def test_summary_templates_bind_only_the_approved_new_safe_fields():
    home_source = Path("templates/dashboard_home.html").read_text(encoding="utf-8")
    reports_source = Path("templates/dashboard_reports.html").read_text(encoding="utf-8")
    disclosure_summary = re.search(
        r"<summary>(.*?)</summary>", reports_source, re.DOTALL
    ).group(1)

    for field in (
        "home_card_title",
        "home_card_normalized_status",
        "home_card_missing_flag",
    ):
        assert field in home_source
    for field in (
        "evidence_title",
        "evidence_report_type",
        "evidence_normalized_result_status",
        "evidence_availability_state",
    ):
        assert field in disclosure_summary
    for prohibited in (
        "report.device",
        "report.json_path",
        "report.html_path",
        "report.description",
        "report.notes",
    ):
        assert prohibited not in disclosure_summary


def test_no_fabricated_score_rate_trend_or_health_grade_is_added():
    combined = "\n".join(
        Path(path).read_text(encoding="utf-8").lower()
        for path in (
            "templates/dashboard_home.html",
            "templates/dashboard_reports.html",
        )
    )

    assert "health grade" not in combined
    assert "health score" not in combined
    assert "success rate" not in combined
    assert "pass rate" not in combined
    assert "trend" not in combined
