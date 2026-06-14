import json
from pathlib import Path

import intent_ai_summary_redaction_policy as day130
import network_lab
import network_lab_cli_dispatch
from network_lab_task_registry import resolve_task_handler, resolve_task_name


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_day130_safe_and_already_redacted_text_are_not_flagged():
    safe = day130.redact_ai_summary_text("Reviewer summary has no credentials or tokens.")
    already_redacted = day130.redact_ai_summary_text("Value is [REDACTED:TOKEN].")

    assert safe["secret_like_found"] is False
    assert safe["redacted_count"] == 0
    assert already_redacted["secret_like_found"] is False
    assert already_redacted["redacted_count"] == 0


def test_day130_detects_and_redacts_required_secret_like_patterns():
    samples = {
        "api_key_assignment": ("api_key=day130_fake_api_key_value_000000000000", "[REDACTED:API_KEY]"),
        "bearer_token": ("Authorization: Bearer day130.fake.bearer.token.value.000000", "[REDACTED:BEARER_TOKEN]"),
        "password_assignment": ("password=day130_fake_password_value", "[REDACTED:PASSWORD]"),
        "private_key_block": (
            "-----BEGIN PRIVATE KEY-----\nfake-key-material\n-----END PRIVATE KEY-----",
            "[REDACTED:PRIVATE_KEY_BLOCK]",
        ),
        "ssh_public_key": (
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDAY130FAKEKEY000000000 reviewer@example",
            "[REDACTED:SSH_PUBLIC_KEY]",
        ),
        "env_secret_assignment": ("OPENAI_API_KEY=sk-day130-example-not-real-token-000000", "[REDACTED:ENV_SECRET]"),
        "token_assignment": ("access_token=day130_fake_access_token_000000", "[REDACTED:TOKEN]"),
    }

    for pattern, (text, marker) in samples.items():
        result = day130.redact_ai_summary_text(text)

        assert result["secret_like_found"] is True
        assert result["redacted_count"] >= 1
        assert marker in result["redacted_text"]
        assert any(finding["pattern"] == pattern for finding in result["findings"])
        assert day130.redact_ai_summary_text(result["redacted_text"])["secret_like_found"] is False


def test_day130_fixture_file_covers_safe_redacted_and_secret_like_cases():
    fixtures = day130.load_redaction_fixtures(PROJECT_ROOT)
    categories = {fixture["category"] for fixture in fixtures}

    assert {"safe_text", "redacted_text", "secret_like_text"}.issubset(categories)
    assert any(fixture["expect_secret_like"] is True for fixture in fixtures)
    assert any(fixture["expect_secret_like"] is False for fixture in fixtures)


def test_day130_report_shape_counts_and_locked_boundaries():
    report = day130.build_ai_summary_redaction_policy_report(PROJECT_ROOT)

    assert report["overall_status"] == "PASS"
    assert report["day"] == "Day130"
    assert report["day_number"] == 130
    assert report["task"] == "ai-summary-redaction-and-no-secret-policy"
    assert report["policy_status"] == "NO_SECRET_POLICY_ENFORCED"
    assert report["redaction_status"] == "REDACTION_REVIEW_READY"
    assert report["review_only"] is True
    assert report["fixture_count"] >= 3
    assert report["redacted_count"] >= 7
    assert report["blocked_secret_like_count"] >= 7
    assert report["unsafe_flag_count"] == 0
    assert report["validation_errors"] == []
    for field in (
        "execution_enabled",
        "provider_enabled",
        "api_enabled",
        "openai_api_called",
        "ai_decision_made",
        "next_phase_allowed",
    ):
        assert report[field] is False
    assert report["not_day131_audit_trail_binding"] is True
    assert report["not_day132_reviewer_approval_gate"] is True
    assert report["not_day133_mock_provider_boundary"] is True


def test_day130_report_omits_original_fixture_input_text():
    report = day130.build_ai_summary_redaction_policy_report(PROJECT_ROOT)
    serialized = json.dumps(report)

    assert "input_text" not in serialized
    assert "day130_fake_password_value" not in serialized
    assert "sk-day130-example-not-real-token-000000" not in serialized
    assert "[REDACTED:PASSWORD]" in serialized
    assert "[REDACTED:ENV_SECRET]" in serialized


def test_day130_cli_task_reports_required_safety_fields(monkeypatch, capsys):
    def fail_subprocess(*args, **kwargs):
        raise AssertionError("Day130 redaction policy must not execute subprocess")

    def fail_profile_load(*args, **kwargs):
        raise AssertionError("Day130 redaction policy must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_subprocess)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_profile_load)

    exit_code = network_lab.main(
        ["--task", "ai-summary-redaction-and-no-secret-policy"],
        project_root=PROJECT_ROOT,
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Task name: ai-summary-redaction-and-no-secret-policy" in output
    assert "overall_status: \"PASS\"" in output
    assert "day: \"Day130\"" in output
    assert "policy_status: \"NO_SECRET_POLICY_ENFORCED\"" in output
    assert "redaction_status: \"REDACTION_REVIEW_READY\"" in output
    assert "review_only: true" in output
    assert "execution_enabled: false" in output
    assert "provider_enabled: false" in output
    assert "api_enabled: false" in output
    assert "openai_api_called: false" in output
    assert "ai_decision_made: false" in output
    assert "next_phase_allowed: false" in output
    assert "unsafe_flag_count: 0" in output


def test_day130_task_catalog_and_registry_wiring():
    task = next(
        task
        for task in network_lab.list_tasks()
        if task["id"] == "ai-summary-redaction-and-no-secret-policy"
    )

    assert resolve_task_name("ai-summary-redaction-and-no-secret-policy") == (
        "ai-summary-redaction-and-no-secret-policy"
    )
    assert task["task_id"] == "day130_ai_summary_redaction_and_no_secret_policy"
    assert task["day"] == "Day130"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert task["related_script"] == "intent_ai_summary_redaction_policy.py"
    assert "Day131 audit trail binding" in task["notes"]
    assert "Day132 reviewer approval gate" in task["notes"]
    assert "Day133 mock provider boundary" in task["notes"]
    assert "OpenAI API calls" in task["notes"]
    assert "execution unlock" in task["notes"]


def test_day130_dispatch_handler_is_registered_without_profile_load():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "ai-summary-redaction-and-no-secret-policy"])
    handlers = network_lab._build_task_handlers(args, PROJECT_ROOT)
    resolved = resolve_task_handler("ai-summary-redaction-and-no-secret-policy", handlers)

    assert resolved.canonical_name == "ai-summary-redaction-and-no-secret-policy"
    assert callable(resolved.handler)


def test_day130_write_reports_and_report_index_visibility(tmp_path):
    report = day130.build_ai_summary_redaction_policy_report(PROJECT_ROOT)
    json_path, html_path = day130.write_ai_summary_redaction_policy_reports(tmp_path, report)

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)
    index_html = (tmp_path / "reports" / "report_index.html").read_text(encoding="utf-8")
    written = json.loads(json_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert json_path.exists()
    assert html_path.exists()
    assert written["overall_status"] == "PASS"
    assert "Day130" in index_html
    assert "AI Summary Redaction and No-Secret Policy" in index_html


def test_day130_docs_exist_and_preserve_boundaries():
    docs = [
        PROJECT_ROOT / "docs/ai-intent/day130_ai_summary_redaction_and_no_secret_policy.md",
        PROJECT_ROOT / "docs/roadmap/day130_ai_summary_redaction_and_no_secret_policy.md",
    ]

    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        assert "deterministic" in text.lower()
        assert "local-only" in text.lower()
        assert "not day131 audit trail binding" in text.lower()
        assert "not day132 reviewer approval gate" in text.lower()
        assert "not day133 mock provider boundary" in text.lower()
        assert "does not enable execution / provider / api" in text.lower()
        assert "does not call openai api" in text.lower()
        assert "does not make ai decisions" in text.lower()
        assert "does not unlock" in text.lower()
