import hashlib
import json
import re
from pathlib import Path

import pytest

import dashboard_app as dashboard


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _journey_section(source: str) -> str:
    start = source.index('<section class="journey-section"')
    end = source.index("</section>", start) + len("</section>")
    return source[start:end]


def test_committed_day95_evidence_supports_the_projected_allowed_and_rejected_examples():
    payload = json.loads(DAY95_JSON.read_text(encoding="utf-8"))
    scenarios = {
        scenario["scenario_id"]: scenario for scenario in payload["scenario_records"]
    }

    allowed = scenarios["D95-S01-readonly-identity"]
    assert allowed["intent"] == "Normalize fake identity evidence"
    assert allowed["guard_decision"] == "ALLOW"
    assert allowed["fake_adapter_invoked"] is True
    assert allowed["real_adapter_invoked"] is False
    assert allowed["live_execution_invoked"] is False
    assert allowed["adapter_result"]["result_status"] == "FAKE_RESULT_READY"
    assert (
        allowed["adapter_result"]["result_payload"]["simulated_output"]
        == "name: lab-router-simulated"
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
    assert "Reviewer conclusion" in journey
    assert "Normalize fake identity evidence" in journey
    assert "FAKE_RESULT_READY" in journey
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
