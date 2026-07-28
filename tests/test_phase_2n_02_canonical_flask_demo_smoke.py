"""Phase 2N-02 canonical local Flask demo smoke-test baseline."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import json
import ntpath
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


@dataclass(frozen=True)
class ChildProcessIdentity:
    pid: int
    parent_pid: int
    executable_filename: str
    full_image_path: str | None


@dataclass(frozen=True)
class ChildProcessClassification:
    runtime_bridge: ChildProcessIdentity | None
    unexpected_children: tuple[ChildProcessIdentity, ...]


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


def _windows_process_snapshot() -> list[ChildProcessIdentity]:
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
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Process32FirstW.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(PROCESSENTRY32W),
    ]
    kernel32.Process32FirstW.restype = wintypes.BOOL
    kernel32.Process32NextW.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(PROCESSENTRY32W),
    ]
    kernel32.Process32NextW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    invalid_handle = wintypes.HANDLE(-1).value
    if snapshot == invalid_handle:
        raise OSError(ctypes.get_last_error(), "CreateToolhelp32Snapshot failed")

    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    identities: list[ChildProcessIdentity] = []
    try:
        found = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while found:
            identities.append(
                ChildProcessIdentity(
                    pid=int(entry.th32ProcessID),
                    parent_pid=int(entry.th32ParentProcessID),
                    executable_filename=entry.szExeFile,
                    full_image_path=None,
                )
            )
            found = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return sorted(identities, key=lambda identity: identity.pid)


def _windows_full_process_image_path(process_id: int) -> str | None:
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    process_handle = kernel32.OpenProcess(
        0x1000,  # PROCESS_QUERY_LIMITED_INFORMATION
        False,
        process_id,
    )
    if not process_handle:
        return None
    try:
        image_path_size = wintypes.DWORD(32768)
        image_path_buffer = ctypes.create_unicode_buffer(image_path_size.value)
        if not kernel32.QueryFullProcessImageNameW(
            process_handle,
            0,
            image_path_buffer,
            ctypes.byref(image_path_size),
        ):
            return None
        return image_path_buffer.value
    finally:
        kernel32.CloseHandle(process_handle)


def _windows_child_process_identities(
    parent_pid: int,
) -> list[ChildProcessIdentity]:
    return [
        ChildProcessIdentity(
            pid=identity.pid,
            parent_pid=identity.parent_pid,
            executable_filename=identity.executable_filename,
            full_image_path=_windows_full_process_image_path(identity.pid),
        )
        for identity in _windows_process_snapshot()
        if identity.parent_pid == parent_pid
    ]


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


def _child_process_identities(parent_pid: int) -> list[ChildProcessIdentity]:
    if os.name == "nt":
        return _windows_child_process_identities(parent_pid)
    return [
        ChildProcessIdentity(
            pid=pid,
            parent_pid=parent_pid,
            executable_filename="",
            full_image_path=None,
        )
        for pid in _posix_child_process_ids(parent_pid)
    ]


def _normalize_windows_path(path: str | None) -> str | None:
    if not path:
        return None
    return ntpath.normcase(ntpath.normpath(path))


def _classify_child_processes(
    children: list[ChildProcessIdentity],
    *,
    parent_pid: int,
    platform_name: str,
    executable: str | None,
    base_executable: str | None,
) -> ChildProcessClassification:
    if not children:
        return ChildProcessClassification(None, ())

    normalized_executable = _normalize_windows_path(executable)
    normalized_base_executable = _normalize_windows_path(base_executable)
    runtime_bridge: ChildProcessIdentity | None = None
    if (
        platform_name == "nt"
        and len(children) == 1
        and normalized_executable is not None
        and normalized_base_executable is not None
        and normalized_executable != normalized_base_executable
        and children[0].parent_pid == parent_pid
        and _normalize_windows_path(children[0].full_image_path)
        == normalized_base_executable
    ):
        runtime_bridge = children[0]

    if runtime_bridge is not None:
        return ChildProcessClassification(runtime_bridge, ())
    return ChildProcessClassification(None, tuple(children))


def _live_captured_process_ids(process_ids: list[int]) -> list[int]:
    if not process_ids:
        return []
    if os.name == "nt":
        live_process_ids = {
            identity.pid for identity in _windows_process_snapshot()
        }
        return sorted(set(process_ids) & live_process_ids)

    live_process_ids = []
    for process_id in process_ids:
        try:
            os.kill(process_id, 0)
        except ProcessLookupError:
            continue
        except PermissionError:
            live_process_ids.append(process_id)
        else:
            live_process_ids.append(process_id)
    return sorted(live_process_ids)


def _wait_for_captured_processes_exit(
    process_ids: list[int],
    timeout_seconds: float = 5.0,
) -> list[int]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        live_process_ids = _live_captured_process_ids(process_ids)
        if not live_process_ids or time.monotonic() >= deadline:
            return live_process_ids
        time.sleep(0.05)


def _unexpected_live_child_ids(
    captured_process_ids: list[int],
    live_process_ids: list[int],
) -> list[int]:
    return sorted(set(captured_process_ids) & set(live_process_ids))


def _generic_child_identity_evidence(
    children: list[ChildProcessIdentity],
    runtime_bridge: ChildProcessIdentity | None,
) -> list[dict[str, object]]:
    return [
        {
            "pid": child.pid,
            "parent_pid": child.parent_pid,
            "executable_filename": child.executable_filename,
            "full_image_path_accessible": child.full_image_path is not None,
            "classification": (
                "windows_environment_runtime_bridge"
                if runtime_bridge is not None and child.pid == runtime_bridge.pid
                else "unexpected_or_unclassified"
            ),
        }
        for child in children
    ]


def _build_runtime_evidence(
    *,
    process_pid: int,
    process_exit_code: int | None,
    process_exited: bool,
    statuses: dict[str, int],
    child_identities: list[ChildProcessIdentity],
    classification: ChildProcessClassification,
    post_cleanup_live_child_ids: list[int],
    unexpected_live_child_ids: list[int],
    bridge_exited_automatically: bool,
    port_closed: bool,
) -> dict[str, object]:
    runtime_bridge_detected = classification.runtime_bridge is not None
    return {
        "interpreter_classification": (
            "environment_runtime_bridge"
            if runtime_bridge_detected
            else "direct_runtime"
        ),
        "environment_runtime_bridge_detected": runtime_bridge_detected,
        "exact_identity_match": runtime_bridge_detected,
        "executable_paths_redacted": True,
        "pid": process_pid,
        "address": HOST,
        "port": PORT,
        "startup_timeout_seconds": STARTUP_TIMEOUT_SECONDS,
        "http_statuses": statuses,
        "request_method": "GET",
        "command_run_post_performed": False,
        "non_local_network_contact_performed": False,
        "child_process_ids": [child.pid for child in child_identities],
        "pre_cleanup_child_identities": _generic_child_identity_evidence(
            child_identities,
            classification.runtime_bridge,
        ),
        "classified_runtime_bridge_pid": (
            classification.runtime_bridge.pid
            if classification.runtime_bridge is not None
            else None
        ),
        "post_cleanup_child_state": [
            {
                "pid": child.pid,
                "alive": child.pid in post_cleanup_live_child_ids,
            }
            for child in child_identities
        ],
        "unexpected_live_children": unexpected_live_child_ids,
        "identity_aware_contract_result": (
            classification.unexpected_children == ()
            and bridge_exited_automatically
            and unexpected_live_child_ids == []
        ),
        "process_exit_code": process_exit_code,
        "process_exited": process_exited,
        "child_processes_exited": post_cleanup_live_child_ids == [],
        "port_closed": port_closed,
    }


def _json_string_values(
    value: object,
    selector: str = "$",
) -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(selector, value)]
    if isinstance(value, dict):
        values: list[tuple[str, str]] = []
        for key, item in value.items():
            values.extend(_json_string_values(item, f"{selector}.{key}"))
        return values
    if isinstance(value, list):
        values = []
        for index, item in enumerate(value):
            values.extend(_json_string_values(item, f"{selector}[{index}]"))
        return values
    return []


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
    child_identities: list[ChildProcessIdentity] = []
    classification = ChildProcessClassification(None, ())
    post_cleanup_live_child_ids: list[int] = []
    unexpected_live_child_ids: list[int] = []
    bridge_exited_automatically = True
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

        child_identities = _child_process_identities(process.pid)
        classification = _classify_child_processes(
            child_identities,
            parent_pid=process.pid,
            platform_name=os.name,
            executable=sys.executable,
            base_executable=getattr(sys, "_base_executable", None),
        )
        assert classification.unexpected_children == (), (
            "The canonical debug=False Flask entry point unexpectedly spawned "
            "unclassified child processes: "
            f"{[child.pid for child in classification.unexpected_children]}"
        )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        captured_child_ids = [child.pid for child in child_identities]
        post_cleanup_live_child_ids = _wait_for_captured_processes_exit(
            captured_child_ids
        )
        unexpected_live_child_ids = _unexpected_live_child_ids(
            captured_child_ids,
            post_cleanup_live_child_ids,
        )
        bridge_exited_automatically = (
            classification.runtime_bridge is None
            or classification.runtime_bridge.pid not in post_cleanup_live_child_ids
        )
        if process.stdout is not None:
            server_output = process.stdout.read()
            process.stdout.close()

        port_closed = _wait_for_port_closed()
        evidence = _build_runtime_evidence(
            process_pid=process.pid,
            process_exit_code=process.returncode,
            process_exited=process.poll() is not None,
            statuses=statuses,
            child_identities=child_identities,
            classification=classification,
            post_cleanup_live_child_ids=post_cleanup_live_child_ids,
            unexpected_live_child_ids=unexpected_live_child_ids,
            bridge_exited_automatically=bridge_exited_automatically,
            port_closed=port_closed,
        )
        print("PHASE_2N_02_RUNTIME_EVIDENCE=" + json.dumps(evidence, sort_keys=True))
        assert process.poll() is not None, "The exact spawned Flask process did not exit"
        assert classification.unexpected_children == (), (
            "Unexpected Flask child processes remained unclassified"
        )
        assert bridge_exited_automatically, (
            "The accepted Windows environment runtime bridge did not exit automatically"
        )
        assert unexpected_live_child_ids == [], (
            "Captured child processes remained alive after exact parent cleanup: "
            f"{unexpected_live_child_ids}"
        )
        assert port_closed, "Canonical port 127.0.0.1:5000 remained open after shutdown"

    assert process.returncode is not None
    assert "Running on http://127.0.0.1:5000" in server_output


SYNTHETIC_PARENT_PID = 100
SYNTHETIC_CHILD_PID = 200
SYNTHETIC_EXECUTABLE = r"C:\runtime\venv\Scripts\python.exe"
SYNTHETIC_BASE_EXECUTABLE = r"C:\runtime\base\python.exe"


def _synthetic_child(
    *,
    pid: int = SYNTHETIC_CHILD_PID,
    parent_pid: int = SYNTHETIC_PARENT_PID,
    filename: str = "python.exe",
    full_image_path: str | None = SYNTHETIC_BASE_EXECUTABLE,
) -> ChildProcessIdentity:
    return ChildProcessIdentity(pid, parent_pid, filename, full_image_path)


def _synthetic_classification(
    children: list[ChildProcessIdentity],
    *,
    platform_name: str = "nt",
    executable: str = SYNTHETIC_EXECUTABLE,
    base_executable: str = SYNTHETIC_BASE_EXECUTABLE,
) -> ChildProcessClassification:
    return _classify_child_processes(
        children,
        parent_pid=SYNTHETIC_PARENT_PID,
        platform_name=platform_name,
        executable=executable,
        base_executable=base_executable,
    )


def _synthetic_runtime_evidence(
    child: ChildProcessIdentity,
) -> dict[str, object]:
    classification = _synthetic_classification([child])
    return _build_runtime_evidence(
        process_pid=SYNTHETIC_PARENT_PID,
        process_exit_code=0,
        process_exited=True,
        statuses={route: 200 for route in GET_ROUTES},
        child_identities=[child],
        classification=classification,
        post_cleanup_live_child_ids=[],
        unexpected_live_child_ids=[],
        bridge_exited_automatically=True,
        port_closed=True,
    )


def test_runtime_evidence_redacts_supplied_private_path_values() -> None:
    synthetic_private_root = ntpath.join("C:\\", "synthetic-profile", "private")
    synthetic_executable = ntpath.join(
        synthetic_private_root,
        "venv",
        "Scripts",
        "python.exe",
    )
    synthetic_base_executable = ntpath.join(
        synthetic_private_root,
        "runtime",
        "python.exe",
    )
    child = _synthetic_child(full_image_path=synthetic_base_executable)
    classification = _classify_child_processes(
        [child],
        parent_pid=SYNTHETIC_PARENT_PID,
        platform_name="nt",
        executable=synthetic_executable,
        base_executable=synthetic_base_executable,
    )
    evidence = _build_runtime_evidence(
        process_pid=SYNTHETIC_PARENT_PID,
        process_exit_code=0,
        process_exited=True,
        statuses={route: 200 for route in GET_ROUTES},
        child_identities=[child],
        classification=classification,
        post_cleanup_live_child_ids=[],
        unexpected_live_child_ids=[],
        bridge_exited_automatically=True,
        port_closed=True,
    )

    assert "interpreter" not in evidence
    for selector, value in _json_string_values(evidence):
        for sensitive_value in (
            synthetic_private_root,
            synthetic_executable,
            synthetic_base_executable,
        ):
            assert sensitive_value not in value, (
                f"private runtime value exposed at {selector}"
            )


def test_runtime_evidence_exposes_generic_bridge_classification() -> None:
    evidence = _synthetic_runtime_evidence(_synthetic_child())

    assert evidence["interpreter_classification"] == "environment_runtime_bridge"
    assert evidence["environment_runtime_bridge_detected"] is True
    assert evidence["exact_identity_match"] is True
    assert evidence["executable_paths_redacted"] is True


def test_runtime_bridge_classifier_accepts_exact_single_base_executable() -> None:
    classification = _synthetic_classification([_synthetic_child()])
    assert classification.runtime_bridge == _synthetic_child()
    assert classification.unexpected_children == ()


def test_runtime_bridge_classifier_rejects_filename_only_match() -> None:
    classification = _synthetic_classification(
        [_synthetic_child(full_image_path=r"C:\other\python.exe")]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_runtime_bridge_classifier_rejects_wrong_full_path() -> None:
    classification = _synthetic_classification(
        [
            _synthetic_child(
                filename="base-runtime.exe",
                full_image_path=r"C:\wrong\base-runtime.exe",
            )
        ]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_runtime_bridge_classifier_rejects_inaccessible_image_identity() -> None:
    classification = _synthetic_classification(
        [_synthetic_child(full_image_path=None)]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_runtime_bridge_classifier_rejects_multiple_children() -> None:
    classification = _synthetic_classification(
        [_synthetic_child(), _synthetic_child(pid=201)]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 2


def test_runtime_bridge_classifier_rejects_additional_unexplained_child() -> None:
    classification = _synthetic_classification(
        [
            _synthetic_child(),
            _synthetic_child(
                pid=202,
                filename="helper.exe",
                full_image_path=r"C:\runtime\helper.exe",
            ),
        ]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 2


def test_runtime_bridge_classifier_rejects_equal_executable_paths() -> None:
    classification = _synthetic_classification(
        [_synthetic_child(full_image_path=SYNTHETIC_EXECUTABLE)],
        base_executable=SYNTHETIC_EXECUTABLE,
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_runtime_bridge_classifier_rejects_non_windows_platform() -> None:
    classification = _synthetic_classification(
        [_synthetic_child()], platform_name="posix"
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_runtime_bridge_classifier_rejects_incorrect_parent_pid() -> None:
    classification = _synthetic_classification(
        [_synthetic_child(parent_pid=SYNTHETIC_PARENT_PID + 1)]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


def test_post_cleanup_contract_rejects_unexpected_live_child() -> None:
    assert _unexpected_live_child_ids([SYNTHETIC_CHILD_PID], [SYNTHETIC_CHILD_PID]) == [
        SYNTHETIC_CHILD_PID
    ]


def test_runtime_bridge_classifier_accepts_no_child_normal_case() -> None:
    classification = _synthetic_classification([])
    assert classification.runtime_bridge is None
    assert classification.unexpected_children == ()


def test_runtime_bridge_classifier_rejects_werkzeug_reloader_like_child() -> None:
    classification = _synthetic_classification(
        [
            _synthetic_child(
                filename="python.exe",
                full_image_path=SYNTHETIC_EXECUTABLE,
            )
        ]
    )
    assert classification.runtime_bridge is None
    assert len(classification.unexpected_children) == 1


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
