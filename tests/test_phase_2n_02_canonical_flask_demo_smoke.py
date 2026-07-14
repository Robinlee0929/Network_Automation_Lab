"""Phase 2N-02 canonical local Flask demo smoke-test baseline."""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pytest

import dashboard_app as dashboard


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 5000
BASE_URL = f"http://{HOST}:{PORT}"
STARTUP_TIMEOUT_SECONDS = 20.0
GET_ROUTES = (
    "/",
    "/reports",
    "/ai-checklist",
    "/ai-intent-reviewer",
    "/commands",
)


def _port_is_listening() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.25)
        return probe.connect_ex((HOST, PORT)) == 0


def _assert_port_can_be_bound() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        probe.bind((HOST, PORT))


def _wait_for_port_closed(timeout_seconds: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not _port_is_listening():
            try:
                _assert_port_can_be_bound()
            except OSError:
                time.sleep(0.05)
                continue
            return True
        time.sleep(0.05)
    return False


def _windows_child_process_ids(parent_pid: int) -> list[int]:
    from ctypes import wintypes

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * 260),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    invalid_handle = ctypes.c_void_p(-1).value
    if snapshot == invalid_handle:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")

    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    child_ids: list[int] = []
    try:
        found = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while found:
            if entry.th32ParentProcessID == parent_pid:
                child_ids.append(int(entry.th32ProcessID))
            found = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return sorted(child_ids)


def _posix_child_process_ids(parent_pid: int) -> list[int]:
    proc_root = Path("/proc")
    if proc_root.is_dir():
        child_ids = []
        for stat_path in proc_root.glob("[0-9]*/stat"):
            try:
                stat = stat_path.read_text(encoding="utf-8")
                fields = stat[stat.rfind(")") + 2 :].split()
                if int(fields[1]) == parent_pid:
                    child_ids.append(int(stat_path.parent.name))
            except (OSError, ValueError, IndexError):
                continue
        return sorted(child_ids)

    completed = subprocess.run(
        ["ps", "-axo", "pid=,ppid="],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return sorted(
        int(pid)
        for line in completed.stdout.splitlines()
        if len(parts := line.split()) == 2
        for pid, ppid in [parts]
        if int(ppid) == parent_pid
    )


def _child_process_ids(parent_pid: int) -> list[int]:
    if os.name == "nt":
        return _windows_child_process_ids(parent_pid)
    return _posix_child_process_ids(parent_pid)


def _wait_for_get(path: str, process: subprocess.Popen[str]) -> tuple[int, str]:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    last_error = "no response"
    url = f"{BASE_URL}{path}"
    assert urlparse(url).hostname == HOST
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail(f"Flask exited during startup with code {process.returncode}")
        try:
            request = Request(url, method="GET")
            with urlopen(request, timeout=1.0) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = str(exc)
            time.sleep(0.1)
    pytest.fail(
        f"Flask did not answer {url} within {STARTUP_TIMEOUT_SECONDS:.1f}s: {last_error}"
    )


def test_canonical_flask_process_lifecycle_and_get_only_routes() -> None:
    assert not _port_is_listening(), (
        "Canonical port 127.0.0.1:5000 is already occupied; the smoke test will "
        "not terminate an unrelated process or substitute another port."
    )
    _assert_port_can_be_bound()

    process = subprocess.Popen(
        [sys.executable, "dashboard_app.py"],
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    statuses: dict[str, int] = {}
    child_ids: list[int] = []
    server_output = ""
    try:
        landing_status, landing_html = _wait_for_get("/", process)
        statuses["/"] = landing_status
        assert landing_status == 200
        assert "Network Automation Lab - Portfolio Demo" in landing_html

        for route in GET_ROUTES[1:]:
            status, _ = _wait_for_get(route, process)
            statuses[route] = status
        assert statuses == {route: 200 for route in GET_ROUTES}

        child_ids = _child_process_ids(process.pid)
        assert child_ids == [], (
            "The canonical debug=False Flask entry point unexpectedly spawned "
            f"child processes: {child_ids}"
        )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if process.stdout is not None:
            server_output = process.stdout.read()
            process.stdout.close()

        port_closed = _wait_for_port_closed()
        evidence = {
            "interpreter": sys.executable,
            "pid": process.pid,
            "address": HOST,
            "port": PORT,
            "startup_timeout_seconds": STARTUP_TIMEOUT_SECONDS,
            "http_statuses": statuses,
            "request_method": "GET",
            "command_run_post_performed": False,
            "non_local_network_contact_performed": False,
            "child_process_ids": child_ids,
            "process_exit_code": process.returncode,
            "process_exited": process.poll() is not None,
            "child_processes_exited": child_ids == [],
            "port_closed": port_closed,
        }
        print("PHASE_2N_02_RUNTIME_EVIDENCE=" + json.dumps(evidence, sort_keys=True))
        assert process.poll() is not None, "The exact spawned Flask process did not exit"
        assert child_ids == [], "Unexpected Flask child processes remained unaccounted for"
        assert port_closed, "Canonical port 127.0.0.1:5000 remained open after shutdown"

    assert process.returncode is not None
    assert "Running on http://127.0.0.1:5000" in server_output


def test_synthetic_report_detail_empty_missing_and_traversal_states(tmp_path: Path) -> None:
    if dashboard.Flask is None:
        pytest.skip("Flask is not installed in this test environment.")

    reports_dir = tmp_path / "reports"
    report_dir = reports_dir / "router1"
    report_dir.mkdir(parents=True)
    (report_dir / "day9_performance_regression_report.html").write_text(
        "<html><body>Phase 2N-02 synthetic safe evidence</body></html>",
        encoding="utf-8",
    )
    (report_dir / "day9_performance_regression_report.json").write_text(
        json.dumps(
            {
                "aggregate": {"overall_result": "PASS"},
                "fixture": "synthetic-safe",
            }
        ),
        encoding="utf-8",
    )
    outside = tmp_path / "outside.html"
    outside.write_text("not safe evidence", encoding="utf-8")

    app = dashboard.create_app(
        reports_dir=reports_dir,
        execution_logs_dir=tmp_path / "execution_logs",
    )
    client = app.test_client()

    reports_response = client.get("/reports")
    assert reports_response.status_code == 200
    discovered = dashboard.discover_reports(reports_dir)
    assert {entry.status for entry in discovered} == {"PASS"}
    assert {
        entry.relative_path.replace("\\", "/") for entry in discovered
    } == {
        "router1/day9_performance_regression_report.html",
        "router1/day9_performance_regression_report.json",
    }

    html_detail = client.get(
        "/reports/open/router1/day9_performance_regression_report.html"
    )
    assert html_detail.status_code == 200
    assert b"Phase 2N-02 synthetic safe evidence" in html_detail.data
    json_detail = client.get(
        "/reports/json/router1/day9_performance_regression_report.json"
    )
    assert json_detail.status_code == 200
    assert b"synthetic-safe" in json_detail.data

    assert client.get("/reports/open/router1/missing.html").status_code == 404
    assert client.get("/reports/open/../outside.html").status_code == 404
    assert client.get("/reports/open/%2e%2e/outside.html").status_code == 404

    empty_reports_dir = tmp_path / "empty-reports"
    empty_reports_dir.mkdir()
    empty_app = dashboard.create_app(
        reports_dir=empty_reports_dir,
        execution_logs_dir=tmp_path / "empty-execution-logs",
    )
    empty_response = empty_app.test_client().get("/reports")
    assert empty_response.status_code == 200
    assert dashboard.discover_reports(empty_reports_dir) == []
    assert b"MISSING" in empty_response.data

    print(
        "PHASE_2N_02_REPORT_EVIDENCE="
        + json.dumps(
            {
                "reports_status": reports_response.status_code,
                "safe_html_detail_status": html_detail.status_code,
                "safe_json_detail_status": json_detail.status_code,
                "missing_status": 404,
                "empty_status": empty_response.status_code,
                "unsafe_path_status": 404,
                "real_report_fixture_committed": False,
                "command_run_post_performed": False,
            },
            sort_keys=True,
        )
    )
