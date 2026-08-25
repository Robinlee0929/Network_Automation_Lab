import hashlib
import json
import re
from pathlib import Path

import pytest

import dashboard_app as dashboard
import stage0_useful_result_presentation as stage0


ROOT = Path(__file__).resolve().parents[1]
DAY95_JSON = ROOT / "reports" / "lab-summary" / "day95_adapter_result_normalization.json"
HOME_TEMPLATE = ROOT / "templates" / "dashboard_home.html"
README = ROOT / "README.md"


@pytest.fixture()
def stage0_journey_surface(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    logs_dir = tmp_path / "execution_logs"
    logs_dir.mkdir()
    execution_calls = []

    def execution_must_not_run(*args, **kwargs):
        execution_calls.append((args, kwargs))
        raise AssertionError("GET-only interview journey reached command execution")

    monkeypatch.setattr(dashboard, "execute_registered_command", execution_must_not_run)
    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=logs_dir,
    )
    app.config.update(TESTING=True)
    return app.test_client(), execution_calls


@pytest.fixture()
def parser_calls(monkeypatch):
    calls = []

    def record_parser_call(adapter_result):
        calls.append(adapter_result)
        return {}

    monkeypatch.setattr(
        stage0,
        "parse_normalized_fake_adapter_result",
        record_parser_call,
    )
    return calls


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _journey_section(source: str) -> str:
    start = source.index('<section class="journey-section"')
    end = source.index("</section>", start) + len("</section>")
    return source[start:end]


def _scenario_section(source: str, scenario: str) -> str:
    marker = source.index(f'data-demo-scenario="{scenario}"')
    start = source.rfind("<article", 0, marker)
    end = source.index("</article>", marker) + len("</article>")
    return source[start:end]


def _assert_fail_closed_presentation(presentation, status, reason_code):
    assert presentation["evidence_status"] == status
    assert presentation["reason_code"] == reason_code

    allowed = presentation["allowed"]
    assert allowed["request"] is None
    assert allowed["reason"] is None
    assert allowed["guard_decision"] is None
    assert allowed["adapter_invoked"] is False
    assert allowed["result_status"] is None
    assert allowed["parsed_result"] is None
    assert allowed["useful_result"] is None

    rejected = presentation["rejected"]
    assert rejected["request"] is None
    assert rejected["reason"] is None
    assert rejected["guard_decision"] is None
    assert rejected["adapter_invoked"] is False
    assert rejected["adapter_result"] is None
    assert rejected["parsed_result"] is None
    assert rejected["useful_result"] is None


def _block_repository_writes(monkeypatch):
    forbidden_writes = []

    def fail_write(name):
        def fail(*args, **kwargs):
            forbidden_writes.append((name, args, kwargs))
            raise AssertionError(f"fail-closed journey attempted {name}")

        return fail

    monkeypatch.setattr(Path, "write_text", fail_write("Path.write_text"))
    monkeypatch.setattr(Path, "write_bytes", fail_write("Path.write_bytes"))
    monkeypatch.setattr(Path, "touch", fail_write("Path.touch"))
    return forbidden_writes


def test_stage0_loader_marks_valid_committed_evidence_available():
    presentation = stage0.load_stage0_useful_result_presentation(DAY95_JSON)

    assert presentation["evidence_status"] == stage0.EVIDENCE_AVAILABLE
    assert presentation["reason_code"] is None
    assert presentation["allowed"]["useful_result"]["record_count"] == 3
    assert presentation["rejected"]["adapter_result"] is None
    assert presentation["rejected"]["parsed_result"] is None
    assert presentation["rejected"]["useful_result"] is None


def test_stage0_loader_fails_closed_when_evidence_is_missing(tmp_path, parser_calls):
    report_path = tmp_path / "private-stage0-evidence.json"

    presentation = stage0.load_stage0_useful_result_presentation(report_path)

    _assert_fail_closed_presentation(
        presentation,
        stage0.EVIDENCE_UNAVAILABLE,
        "EVIDENCE_MISSING",
    )
    assert parser_calls == []
    assert str(report_path) not in json.dumps(presentation)


def test_stage0_loader_fails_closed_without_exposing_unreadable_error(
    tmp_path,
    monkeypatch,
    parser_calls,
):
    report_path = tmp_path / "sensitive-stage0-evidence.json"
    sensitive_error = (
        r"Access denied: C:\Users\example-private-user\private-stage0-evidence.json"
    )
    original_read_text = Path.read_text

    def raise_for_controlled_path(path, *args, **kwargs):
        if path == report_path:
            raise PermissionError(sensitive_error)
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", raise_for_controlled_path)
    presentation = stage0.load_stage0_useful_result_presentation(report_path)

    _assert_fail_closed_presentation(
        presentation,
        stage0.EVIDENCE_UNAVAILABLE,
        "EVIDENCE_UNREADABLE",
    )
    serialized = json.dumps(presentation)
    assert parser_calls == []
    assert str(report_path) not in serialized
    assert sensitive_error not in serialized
    assert "Access denied" not in serialized


def test_stage0_loader_fails_closed_on_invalid_utf8(tmp_path, parser_calls):
    report_path = tmp_path / "invalid-utf8-stage0-evidence.json"
    report_path.write_bytes(b"\xff\xfe\x80")

    presentation = stage0.load_stage0_useful_result_presentation(report_path)

    _assert_fail_closed_presentation(
        presentation,
        stage0.EVIDENCE_MALFORMED,
        "EVIDENCE_INVALID_ENCODING",
    )
    assert parser_calls == []


def test_stage0_loader_fails_closed_on_malformed_json(tmp_path, parser_calls):
    report_path = tmp_path / "malformed-stage0-evidence.json"
    malformed_content = '{"private_stage0_value": '
    report_path.write_text(malformed_content, encoding="utf-8")

    presentation = stage0.load_stage0_useful_result_presentation(report_path)

    _assert_fail_closed_presentation(
        presentation,
        stage0.EVIDENCE_MALFORMED,
        "EVIDENCE_INVALID_JSON",
    )
    serialized = json.dumps(presentation)
    assert parser_calls == []
    assert malformed_content not in serialized
    assert "JSONDecodeError" not in serialized
    assert "line 1 column" not in serialized


@pytest.mark.parametrize("payload", [[], "not-an-object", None])
def test_stage0_loader_fails_closed_on_non_object_json(
    tmp_path,
    parser_calls,
    payload,
):
    report_path = tmp_path / "wrong-shape-stage0-evidence.json"
    report_path.write_text(json.dumps(payload), encoding="utf-8")

    presentation = stage0.load_stage0_useful_result_presentation(report_path)

    _assert_fail_closed_presentation(
        presentation,
        stage0.EVIDENCE_MALFORMED,
        "EVIDENCE_INVALID_SHAPE",
    )
    assert parser_calls == []


def test_canonical_home_get_renders_missing_evidence_without_fallback_or_leak(
    stage0_journey_surface,
    tmp_path,
    monkeypatch,
    parser_calls,
):
    client, execution_calls = stage0_journey_surface
    report_path = tmp_path / "private-missing-stage0-evidence.json"
    monkeypatch.setattr(
        dashboard,
        "load_stage0_useful_result_presentation",
        lambda _configured_path: stage0.load_stage0_useful_result_presentation(
            report_path
        ),
    )
    forbidden_writes = _block_repository_writes(monkeypatch)

    response = client.get("/")

    assert response.status_code == 200
    source = response.get_data(as_text=True)
    journey = _journey_section(source)
    assert 'data-stage0-evidence-state="UNAVAILABLE"' in journey
    assert "Stage-0 journey evidence is unavailable" in journey
    assert "No valid Stage-0 result is inferred" in journey
    assert "No live fallback was attempted" in journey
    assert "No adapter, runner, command, provider, or device execution occurred" in journey
    assert "No allowed or rejected useful result was fabricated" in journey
    assert 'data-demo-scenario="allowed"' not in journey
    assert 'data-demo-scenario="rejected"' not in journey
    assert str(report_path) not in source
    assert r"C:\Users" not in source
    assert "Traceback" not in source
    assert parser_calls == []
    assert forbidden_writes == []
    assert execution_calls == []


def test_canonical_home_get_renders_malformed_evidence_without_fallback_or_leak(
    stage0_journey_surface,
    tmp_path,
    monkeypatch,
    parser_calls,
):
    client, execution_calls = stage0_journey_surface
    report_path = tmp_path / "private-malformed-stage0-evidence.json"
    malformed_content = '{"private_stage0_value": '
    report_path.write_text(malformed_content, encoding="utf-8")
    monkeypatch.setattr(
        dashboard,
        "load_stage0_useful_result_presentation",
        lambda _configured_path: stage0.load_stage0_useful_result_presentation(
            report_path
        ),
    )
    forbidden_writes = _block_repository_writes(monkeypatch)

    response = client.get("/")

    assert response.status_code == 200
    source = response.get_data(as_text=True)
    journey = _journey_section(source)
    assert 'data-stage0-evidence-state="MALFORMED"' in journey
    assert "Stage-0 journey evidence is malformed" in journey
    assert "cannot be used as valid Stage-0 evidence" in journey
    assert "No live fallback was attempted" in journey
    assert "No adapter, runner, command, provider, or device execution occurred" in journey
    assert "No allowed or rejected useful result was fabricated" in journey
    assert malformed_content not in source
    assert str(report_path) not in source
    assert "JSONDecodeError" not in source
    assert "line 1 column" not in source
    assert "Traceback" not in source
    assert parser_calls == []
    assert forbidden_writes == []
    assert execution_calls == []


def test_committed_day95_evidence_supports_the_projected_allowed_and_rejected_examples():
    payload = json.loads(DAY95_JSON.read_text(encoding="utf-8"))
    scenarios = {
        scenario["scenario_id"]: scenario for scenario in payload["scenario_records"]
    }

    allowed = scenarios["D95-S02-readonly-interfaces-multiline"]
    assert allowed["intent"] == "Normalize fake multi-line interface evidence"
    assert allowed["guard_decision"] == "ALLOW"
    assert allowed["fake_adapter_invoked"] is True
    assert allowed["real_adapter_invoked"] is False
    assert allowed["live_execution_invoked"] is False
    assert allowed["adapter_result"]["result_status"] == "FAKE_RESULT_READY"
    assert (
        allowed["adapter_result"]["result_payload"]["simulated_output"]
        == "ether1 running\nbridge-lan running\nwireguard-lab disabled"
    )

    rejected = scenarios["D95-S03-reject-write-capable"]
    assert rejected["intent"] == "Set interface address"
    assert rejected["guard_decision"] == "REJECT"
    assert rejected["unsafe_category"] == "write_capable"
    assert rejected["adapter_invoked"] is False
    assert rejected["fake_adapter_invoked"] is False
    assert rejected["real_adapter_invoked"] is False
    assert rejected["live_execution_invoked"] is False
    assert rejected["adapter_result"] is None


def test_stage0_projection_reuses_day96_for_allowed_only_and_never_fabricates_rejected(
    monkeypatch,
):
    payload = json.loads(DAY95_JSON.read_text(encoding="utf-8"))
    parser_calls = []
    existing_parser = stage0.parse_normalized_fake_adapter_result

    def record_parser_call(adapter_result):
        parser_calls.append(adapter_result["scenario_id"])
        return existing_parser(adapter_result)

    monkeypatch.setattr(
        stage0,
        "parse_normalized_fake_adapter_result",
        record_parser_call,
    )
    presentation = stage0.build_stage0_useful_result_presentation(payload)

    allowed = presentation["allowed"]
    assert parser_calls == ["D95-S02-readonly-interfaces-multiline"]
    assert allowed["parsed_result"]["parser_status"] == "PARSED"
    assert allowed["useful_result"] == {
        "label": "Simulated Stage-0 result",
        "record_count": 3,
        "status_counts": {"running": 2, "disabled": 1},
        "findings": [{"name": "wireguard-lab", "status": "disabled"}],
        "source": "Deterministic fake adapter",
        "live_device_contacted": False,
    }

    rejected = presentation["rejected"]
    assert rejected["adapter_invoked"] is False
    assert rejected["adapter_result"] is None
    assert rejected["parsed_result"] is None
    assert rejected["useful_result"] is None


def test_canonical_home_get_exposes_a_complete_three_minute_stage0_journey(
    stage0_journey_surface,
):
    client, execution_calls = stage0_journey_surface
    response = client.get("/")

    assert response.status_code == 200
    source = response.get_data(as_text=True)
    journey = _journey_section(source)

    assert 'href="#stage0-interview-journey"' in source
    assert 'id="stage0-interview-journey"' in journey
    assert "Network Automation Lab" in source
    assert "Primary user: Network Engineer / Automation Reviewer" in journey
    assert "difficult to repeat, compare, review, audit, and automate safely" in journey
    assert "Bounded request" in journey
    assert "Safety decision" in journey
    assert "Fake boundary" in journey
    assert "Structured evidence" in journey
    assert "Useful result" in journey
    assert "Reviewer conclusion" in journey
    assert "Normalize fake multi-line interface evidence" in journey
    assert "FAKE_RESULT_READY" in journey
    assert "Simulated Stage-0 result" in journey
    assert "3 interface records parsed" in journey
    assert "2 running" in journey
    assert "1 disabled" in journey
    assert "wireguard-lab — disabled" in journey
    assert "Deterministic fake adapter" in journey
    assert "Live device contacted" in journey
    assert "Set interface address" in journey
    assert "Rejected before adapter invocation" in journey
    assert "Implemented in this Stage-0 journey" in journey
    assert "Intentionally outside this accepted demo path" in journey
    assert "This is more than a one-off script" in journey
    assert execution_calls == []


def test_stage0_journey_is_get_only_safe_linked_and_does_not_mutate_evidence(
    stage0_journey_surface, monkeypatch
):
    client, execution_calls = stage0_journey_surface
    evidence_hash_before = _sha256(DAY95_JSON)
    evidence_mtime_before = DAY95_JSON.stat().st_mtime_ns
    forbidden_writes = []

    def fail_write(name):
        def fail(*args, **kwargs):
            forbidden_writes.append((name, args, kwargs))
            raise AssertionError(f"GET-only interview journey attempted {name}")

        return fail

    monkeypatch.setattr(Path, "write_text", fail_write("Path.write_text"))
    monkeypatch.setattr(Path, "write_bytes", fail_write("Path.write_bytes"))
    monkeypatch.setattr(Path, "touch", fail_write("Path.touch"))

    response = client.get("/")
    assert response.status_code == 200
    journey = _journey_section(response.get_data(as_text=True))
    lower = journey.lower()
    rejected = _scenario_section(journey, "rejected")

    assert "<form" not in lower
    assert "<button" not in lower
    assert "<input" not in lower
    assert 'method="post"' not in lower
    assert "javascript:" not in lower
    assert "/api/" not in lower
    assert "/commands/" not in lower
    assert "/jobs" not in lower

    links = re.findall(r'href="([^"]+)"', journey)
    assert links == [
        "/reports/json/reports/lab-summary/day95_adapter_result_normalization.json",
        "/reports/open/reports/lab-summary/day95_adapter_result_normalization.html",
    ]
    assert all(
        link.startswith(("/reports/json/", "/reports/open/")) for link in links
    )
    assert "no live-device action" in lower
    assert "does not invoke provider-backed operations" not in lower
    assert "provider-backed operations or model invocation" in lower
    assert 'data-stage0-useful-result="absent"' in rejected
    assert "no adapter result, parsed result, or useful result is created" in rejected.lower()
    assert evidence_hash_before == _sha256(DAY95_JSON)
    assert evidence_mtime_before == DAY95_JSON.stat().st_mtime_ns
    assert forbidden_writes == []
    assert execution_calls == []


def test_readme_routes_interviewers_to_the_canonical_journey_and_drops_stale_sequence():
    text = README.read_text(encoding="utf-8")

    assert "## Interview / Demo Quick Path" in text
    assert "python dashboard_app.py" in text
    assert "Open the 3-minute Stage-0 journey" in text
    assert "committed Day95 evidence" in text
    assert "This accepted Stage-0 demo path is GET-only" in text
    assert "Other internal or legacy surfaces" in text
    assert "### Current release baseline" in text
    assert "v0.3 release and its bounded post-release maintenance cycle are complete" in text
    assert "### August release critical path" not in text
    assert "diagnose and fix the known GitHub main CI red-X" not in text
    assert "ai-project-assistant-mvp" not in HOME_TEMPLATE.read_text(encoding="utf-8")
