import html
import re
import socket
import subprocess
from pathlib import Path
from unittest.mock import Mock
from urllib.parse import urlsplit

import pytest

import dashboard_app as dashboard
import dashboard_command_runner as runner
import network_lab


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "4b3f139af072d88cb6fc564b5cb37319faefe3f0"
SOURCE_PREFIX = f"/Robinlee0929/Network_Automation_Lab/blob/{SOURCE_COMMIT}/"
PLAN = "docs/automation_readiness/actual_automation_integration_plan.md"
MANUAL = "docs/portfolio/manual_vrrp_failover_20261020.md"
CLOSURE = "docs/automation_readiness/stage2_formal_closure.md"


def _page(client, path):
    response = client.get(path)
    assert response.status_code == 200
    return response.get_data(as_text=True)


def _history(source):
    match = re.search(r'<section class="historical-vrrp".*?</section>', source, re.S)
    assert match is not None
    return match.group(0)


def _facts(source):
    return dict(re.findall(r"<dt>([^<]+)</dt><dd>([^<]+)</dd>", source))


@pytest.fixture
def reviewer(tmp_path):
    app = dashboard.create_reviewer_app(tmp_path / "reports", tmp_path / "logs")
    app.testing = True
    return app, app.test_client()


@pytest.mark.parametrize(
    ("lab", "role", "priority", "baseline"),
    [
        ("lab1", "MASTER", "150", "39da163d80e5d8b2dde215eb6c0979448d0739fd"),
        ("lab2", "BACKUP", "100", "ea73196281e38a01af7bf959cc5e1bc60b0b2499"),
    ],
)
def test_each_lab_is_an_independent_historical_record(reviewer, lab, role, priority, baseline):
    _, client = reviewer
    history = _history(_page(client, "/reports"))
    card = re.search(fr'<article class="history-lab" data-history-lab="{lab}">.*?</article>', history, re.S).group(0)
    assert "HISTORICAL_LIVE_PROOF" in card
    assert f'data-history-role="{role}"' in card
    assert _facts(card) == {"VRID": "88", "Priority": priority}
    assert baseline in card
    assert "1 次" in card and "重試 0 次" in card
    assert "不同時間、不同授權" in history
    assert "不是目前設備狀態" in history and "不能代表雙機同步健康" in history
    assert "CURRENT_STATUS" not in history and "CURRENT_PAIR_HEALTH" not in history
    assert "STAGE2_FORMAL_STATUS = CLOSED" in history and "LIVE_AUTHORIZED = NO" in history
    assert baseline in (ROOT / PLAN).read_text(encoding="utf-8")


def test_manual_observation_preserves_loss_and_unmeasured_timing(reviewer):
    _, client = reviewer
    history = _history(_page(client, "/reports"))
    manual = re.search(r'<article class="history-manual".*?</article>', history, re.S).group(0)
    assert 'data-evidence-kind="MANUAL_FAILOVER_OBSERVATION"' in manual
    assert '<time datetime="2026-10-20">' in manual
    assert _facts(manual) == {
        "Ping Replies": "205", "Timeouts": "2", "Total": "207", "Packet Loss": "0.9662%",
        "Failover Time": "NOT_MEASURED", "Recovery Time": "NOT_MEASURED",
    }
    assert "不能宣稱零中斷" in manual
    assert "不能把兩次逾時分別歸因" in manual
    assert "625 ms 僅是單次命令耗時，不是 VRRP Failover Time" in manual
    document = (ROOT / MANUAL).read_text(encoding="utf-8")
    assert "205 replies and 2 timeouts" in document
    assert "207 observations: 0.9662%" in document
    assert "NOT_MEASURED" in document
    assert "LOCAL_DOCS_DRAFT_READY_FOR_OWNER_REVIEW" in document and "LOCAL_DOCS_DRAFT_READY_FOR_OWNER_REVIEW" in history


def test_provenance_links_pin_public_documents_and_preserve_closure_baseline(reviewer):
    _, client = reviewer
    history = _history(_page(client, "/reports"))
    links = [urlsplit(html.unescape(url)) for url in re.findall(r'href="([^"]+)"', history)]
    expected = {
        (PLAN, "historical-lab1-proven-scope-and-result"),
        (PLAN, "later-lab2-proof-and-persistent-startup-closure-evidence"),
        (MANUAL, ""), (CLOSURE, "decision-summary"),
    }
    assert len(links) == len(expected)
    assert all(link.scheme == "https" and link.netloc == "github.com" and not link.query for link in links)
    assert all(link.path.startswith(SOURCE_PREFIX) for link in links)
    assert {(link.path.removeprefix(SOURCE_PREFIX), link.fragment) for link in links} == expected
    for document, anchor in expected:
        contents = (ROOT / document).read_text(encoding="utf-8")
        if anchor:
            headings = re.findall(r"^#+ (.+)$", contents, re.M)
            assert anchor in [heading.lower().strip().replace(" ", "-") for heading in headings]
    closure = (ROOT / CLOSURE).read_text(encoding="utf-8")
    for marker in ("DOCUMENTATION_ONLY_FIXED_HEAD", "0f774c47b2529a5f93c0b0abd7c245b85e2d61d2"):
        assert marker in history and marker in closure
    assert "不是新的設備測試基準" in history
    assert "不讀取外部 ZIP" in history and "不自動檢查外部連結" in history


def test_home_entry_keeps_stage0_fake_journey_separate(reviewer):
    _, client = reviewer
    source = _page(client, "/")
    journey = re.search(r'<section class="journey-section".*?</section>', source, re.S).group(0)
    assert "Fake Adapter" in journey
    assert "HISTORICAL_LIVE_PROOF" not in journey
    assert source.index('id="stage2-history-entry"') > source.index(journey) + len(journey)
    assert 'href="/reports#stage2-historical-vrrp"' in source
    assert "不表示目前設備狀態" in source


@pytest.mark.parametrize("evidence_state", ["MISSING", "MALFORMED"])
def test_history_never_upgrades_missing_or_malformed_local_reports(tmp_path, evidence_state):
    reports_dir = tmp_path / "reports"
    if evidence_state == "MALFORMED":
        artifact = reports_dir / "fixture-router" / "day4_baseline_validation.json"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("{broken-json", encoding="utf-8")
    app = dashboard.create_reviewer_app(reports_dir, tmp_path / "logs")
    app.testing = True
    client = app.test_client()
    source = _page(client, "/reports")
    assert f'data-collection-state="{evidence_state}"' in source
    assert re.search(r'data-count-field="pass_count"><dt>PASS results</dt><dd>0</dd>', source)
    if evidence_state == "MALFORMED":
        assert "Result: MALFORMED" in source
    history = _history(source)
    assert 'data-evidence-source="PINNED_PUBLIC_DOCUMENTATION"' in history
    assert "不納入下方本機報告計數" in history
    assert "不以歷史紀錄補成 PASS" in history
    assert 'class="badge pass"' not in history
    assert _history(_page(client, "/reports?status=PASS&mode=live")) == history


@pytest.mark.parametrize("path", ["/", "/reports"])
def test_historical_pages_do_not_execute_write_or_fetch_sources(reviewer, tmp_path, monkeypatch, path):
    app, client = reviewer
    guards = {name: Mock(side_effect=AssertionError(name)) for name in (
        "runner", "subprocess", "execution_log", "report_writer", "file_write", "network",
    )}
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    with monkeypatch.context() as patch:
        patch.setattr(dashboard, "execute_registered_command", guards["runner"])
        patch.setattr(runner, "execute_command", guards["runner"])
        patch.setattr(runner, "_write_log", guards["execution_log"])
        patch.setattr(network_lab, "write_report_index_html", guards["report_writer"])
        patch.setattr(subprocess, "run", guards["subprocess"])
        patch.setattr(subprocess, "Popen", guards["subprocess"])
        patch.setattr(socket, "socket", guards["network"])
        for method in ("write_text", "write_bytes", "mkdir", "touch"):
            patch.setattr(Path, method, guards["file_write"])
        source = _page(client, path)
        assert client.head(path).status_code == 200
        assert set(client.options(path).allow) == {"GET", "HEAD", "OPTIONS"}
    for guard in guards.values():
        guard.assert_not_called()
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    assert "run_command" not in app.view_functions
    assert all(rule.methods <= {"GET", "HEAD", "OPTIONS"} for rule in app.url_map.iter_rules())
    for control in ("<form", "<button", "<script", 'method="post"'):
        assert control not in source.lower()
