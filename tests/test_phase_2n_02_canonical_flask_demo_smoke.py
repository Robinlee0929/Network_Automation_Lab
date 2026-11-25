"""Phase 2N-02 canonical local Flask demo smoke-test baseline."""

from __future__ import annotations

import ctypes
import hashlib
from dataclasses import asdict, dataclass
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


@dataclass
class LifecycleProgress:
    sampling_started: bool = False
    sampling_completed: bool = False
    classification_completed: bool = False
    cleanup_completed: bool = False
    post_cleanup_check_completed: bool = False
    port_check_completed: bool = False


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
    http_requests: list[dict[str, object]],
    lifecycle: LifecycleProgress,
    child_identities: list[ChildProcessIdentity],
    classification: ChildProcessClassification,
    post_cleanup_live_child_ids: list[int],
    unexpected_live_child_ids: list[int],
    bridge_exited_automatically: bool,
    port_closed: bool,
    report_files_unchanged: bool | None = None,
) -> dict[str, object]:
    methods = sorted({request["method"] for request in http_requests})
    command_posts = [
        request for request in http_requests
        if request["method"] == "POST"
        and str(request["path"]).startswith("/commands/")
        and str(request["path"]).endswith("/run")
    ]
    classification_verified = lifecycle.sampling_completed and lifecycle.classification_completed
    exit_verified = lifecycle.sampling_completed and lifecycle.post_cleanup_check_completed
    classification_failed = classification_verified and classification.unexpected_children != ()
    exit_failed = exit_verified and post_cleanup_live_child_ids != []
    if classification_failed or exit_failed:
        identity_status = "FAIL"
    elif not (classification_verified and exit_verified and lifecycle.cleanup_completed):
        identity_status = "NOT_VERIFIED"
    else:
        identity_status = "PASS" if bridge_exited_automatically else "FAIL"
    exit_status = ("FAIL" if exit_failed else "PASS") if exit_verified else "NOT_VERIFIED"
    runtime_bridge_detected = classification_verified and classification.runtime_bridge is not None
    return {
        "interpreter_classification": (
            "NOT_VERIFIED" if not classification_verified else
            "unexpected_or_unclassified" if classification_failed else
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
        # Retain the legacy summary keys, but describe actual HTTP attempts.
        "request_method": methods[0] if len(methods) == 1 else ("MIXED" if methods else "NOT_ATTEMPTED"),
        "request_methods": methods,
        "http_requests": http_requests,
        "command_run_post_performed": bool(command_posts),
        "command_run_post_attempts": command_posts,
        "command_execution": {
            "status": "NOT_INDEPENDENTLY_MEASURED",
            "scope": "Child-process runner/subprocess calls are not instrumented; HTTP rejection alone does not measure execution side effects.",
        },
        "report_files_unchanged": report_files_unchanged,
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
        ] if exit_verified else [],
        "unexpected_live_children": unexpected_live_child_ids,
        "lifecycle_progress": asdict(lifecycle),
        "cleanup_scope": "Exact spawned parent and stdout; captured-child exit is verified separately.",
        "lifecycle_result_semantics": "False with NOT_VERIFIED means unverified, not an observed failure.",
        "identity_aware_contract_result": identity_status == "PASS",
        "identity_aware_contract_status": identity_status,
        "process_exit_code": process_exit_code,
        "process_exited": process_exited,
        "child_processes_exited": exit_status == "PASS",
        "child_processes_exit_status": exit_status,
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


def _observed_urlopen(
    request: Request,
    http_requests: list[dict[str, object]],
    *,
    timeout: float,
):
    # Record dispatch attempts, not pre-planned requests or inferred execution.
    # None means no HTTP response was observed, including transport failures.
    observation = {
        "method": request.get_method(),
        "path": urlparse(request.full_url).path,
        "response_status": None,
    }
    http_requests.append(observation)
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as exc:
        observation["response_status"] = exc.code
        raise
    observation["response_status"] = response.status
    return response


def _wait_for_get(
    path: str,
    process: subprocess.Popen[str],
    http_requests: list[dict[str, object]],
) -> tuple[int, str]:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    last_error = "no response"
    url = f"{BASE_URL}{path}"
    assert urlparse(url).hostname == HOST
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail(f"Flask exited during startup with code {process.returncode}")
        try:
            request = Request(url, method="GET")
            with _observed_urlopen(request, http_requests, timeout=1.0) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = str(exc)
            time.sleep(0.1)
    pytest.fail(
        f"Flask did not answer {url} within {STARTUP_TIMEOUT_SECONDS:.1f}s: {last_error}"
    )


def _report_file_hashes() -> dict[str, str]:
    return {
        path.relative_to(PROJECT_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (PROJECT_ROOT / "reports").rglob("*")
        if path.is_file()
    }


def _assert_canonical_reviewer_http_boundary(http_requests: list[dict[str, object]]) -> None:
    command_paths = [f"/commands/{key}/run" for key in ("pytest_all", "topology_summary", "not_allowed")]
    # Fail before sending any POST if the real entry point accidentally uses Legacy.
    for path in command_paths:
        with pytest.raises(HTTPError) as rejected:
            _observed_urlopen(Request(f"{BASE_URL}{path}", method="OPTIONS"), http_requests, timeout=2)
        assert rejected.value.code == 404
        rejected.value.close()
    for method, path in [("POST", path) for path in command_paths] + [
        (method, command_paths[1]) for method in ("PUT", "PATCH", "DELETE")
    ]:
        with pytest.raises(HTTPError) as rejected:
            _observed_urlopen(Request(f"{BASE_URL}{path}", data=b"mode=legacy", method=method), http_requests, timeout=2)
        assert rejected.value.code == 404
        rejected.value.close()
    with _observed_urlopen(Request(f"{BASE_URL}/", method="HEAD"), http_requests, timeout=2) as response:
        assert response.status == 200
        assert response.read() == b""
    with _observed_urlopen(Request(f"{BASE_URL}/", method="OPTIONS"), http_requests, timeout=2) as response:
        assert response.status == 200
        assert {item.strip() for item in response.headers["Allow"].split(",")} == {"GET", "HEAD", "OPTIONS"}


def test_canonical_flask_process_lifecycle_and_get_only_routes() -> None:
    assert not _port_is_listening(), (
        "Canonical port 127.0.0.1:5000 is already occupied; the smoke test will "
        "not terminate an unrelated process or substitute another port."
    )
    _assert_port_can_be_bound()
    reports_before = _report_file_hashes()

    process = subprocess.Popen(
        [sys.executable, "dashboard_app.py"],
        cwd=PROJECT_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    statuses: dict[str, int] = {}
    http_requests: list[dict[str, object]] = []
    report_files_unchanged = None
    child_identities: list[ChildProcessIdentity] = []
    classification = ChildProcessClassification(None, ())
    post_cleanup_live_child_ids: list[int] = []
    unexpected_live_child_ids: list[int] = []
    bridge_exited_automatically = False
    lifecycle = LifecycleProgress()
    process_exited = False
    port_closed = False
    server_output = ""
    try:
        landing_status, landing_html = _wait_for_get("/", process, http_requests)
        statuses["/"] = landing_status
        assert landing_status == 200
        assert "Network Automation Lab - Portfolio Demo" in landing_html

        for route in GET_ROUTES[1:]:
            status, _ = _wait_for_get(route, process, http_requests)
            statuses[route] = status
        assert statuses == {route: 200 for route in GET_ROUTES}
        _assert_canonical_reviewer_http_boundary(http_requests)
        report_files_unchanged = _report_file_hashes() == reports_before
        assert report_files_unchanged

        lifecycle.sampling_started = True
        child_identities = _child_process_identities(process.pid)
        lifecycle.sampling_completed = True
        classification = _classify_child_processes(
            child_identities,
            parent_pid=process.pid,
            platform_name=os.name,
            executable=sys.executable,
            base_executable=getattr(sys, "_base_executable", None),
        )
        lifecycle.classification_completed = True
        assert classification.unexpected_children == (), (
            "The canonical debug=False Flask entry point unexpectedly spawned "
            "unclassified child processes: "
            f"{[child.pid for child in classification.unexpected_children]}"
        )
    finally:
        original_failure = sys.exc_info()[1]
        cleanup_errors: list[Exception] = []
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            process_exited = process.poll() is not None
        except Exception as exc:
            cleanup_errors.append(exc)
        # An empty captured set is meaningful only after a completed sample.
        try:
            if lifecycle.sampling_completed:
                captured_child_ids = [child.pid for child in child_identities]
                post_cleanup_live_child_ids = _wait_for_captured_processes_exit(captured_child_ids)
                lifecycle.post_cleanup_check_completed = True
                unexpected_live_child_ids = _unexpected_live_child_ids(
                    captured_child_ids, post_cleanup_live_child_ids,
                )
                if lifecycle.classification_completed:
                    bridge_exited_automatically = (
                        classification.runtime_bridge is None
                        or classification.runtime_bridge.pid not in post_cleanup_live_child_ids
                    )
        except Exception as exc:
            cleanup_errors.append(exc)
        try:
            if process.stdout is not None:
                try:
                    if process_exited:
                        server_output = process.stdout.read()
                finally:
                    process.stdout.close()
            lifecycle.cleanup_completed = process_exited
        except Exception as exc:
            cleanup_errors.append(exc)

        try:
            port_closed = _wait_for_port_closed()
            lifecycle.port_check_completed = True
        except Exception as exc:
            cleanup_errors.append(exc)
        evidence = _build_runtime_evidence(
            process_pid=process.pid,
            process_exit_code=process.returncode,
            process_exited=process_exited,
            statuses=statuses,
            http_requests=http_requests,
            lifecycle=lifecycle,
            report_files_unchanged=report_files_unchanged,
            child_identities=child_identities,
            classification=classification,
            post_cleanup_live_child_ids=post_cleanup_live_child_ids,
            unexpected_live_child_ids=unexpected_live_child_ids,
            bridge_exited_automatically=bridge_exited_automatically,
            port_closed=port_closed,
        )
        evidence["cleanup_error_types"] = [type(exc).__name__ for exc in cleanup_errors]
        print("PHASE_2N_02_RUNTIME_EVIDENCE=" + json.dumps(evidence, sort_keys=True))
        if cleanup_errors:
            if original_failure is None:
                raise cleanup_errors[0]
            original_failure.add_note(
                "Lifecycle cleanup/observation also failed: "
                + ", ".join(evidence["cleanup_error_types"])
            )

    # Do not replace an earlier failure with a cleanup assertion.
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
    assert evidence["identity_aware_contract_result"] is True
    assert evidence["identity_aware_contract_status"] == "PASS"
    assert evidence["child_processes_exited"] is True
    assert evidence["child_processes_exit_status"] == "PASS"
    assert evidence["command_run_post_performed"] is True
    assert evidence["command_run_post_attempts"] == [
        {"method": "POST", "path": f"/commands/{key}/run", "response_status": 404}
        for key in ("pytest_all", "topology_summary", "not_allowed")
    ]
    assert evidence["request_method"] == "MIXED"
    assert evidence["request_methods"] == ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    assert evidence["report_files_unchanged"] is True
    assert evidence["command_execution"]["status"] == "NOT_INDEPENDENTLY_MEASURED"


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
    http_requests: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    classification = _synthetic_classification([child])
    return _build_runtime_evidence(
        process_pid=SYNTHETIC_PARENT_PID,
        process_exit_code=0,
        process_exited=True,
        statuses={route: 200 for route in GET_ROUTES},
        http_requests=http_requests if http_requests is not None else [],
        lifecycle=LifecycleProgress(
            sampling_started=True, sampling_completed=True, classification_completed=True,
            cleanup_completed=True, post_cleanup_check_completed=True, port_check_completed=True,
        ),
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
        http_requests=[],
        lifecycle=LifecycleProgress(
            sampling_started=True, sampling_completed=True, classification_completed=True,
            cleanup_completed=True, post_cleanup_check_completed=True, port_check_completed=True,
        ),
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


def test_runtime_evidence_before_http_does_not_claim_post_or_execution() -> None:
    evidence = _synthetic_runtime_evidence(_synthetic_child())
    assert evidence["command_run_post_performed"] is False
    assert evidence["command_run_post_attempts"] == []
    assert evidence["request_method"] == "NOT_ATTEMPTED"
    assert evidence["request_methods"] == []
    assert evidence["report_files_unchanged"] is None
    assert evidence["command_execution"]["status"] == "NOT_INDEPENDENTLY_MEASURED"


@pytest.mark.parametrize(
    "failure_method,failure_status,post_count",
    [("OPTIONS", 405, 0), ("POST", 503, 2), ("POST", None, 2)],
)
def test_runtime_evidence_preserves_partial_http_attempts(
    monkeypatch, failure_method, failure_status, post_count,
) -> None:
    calls = []
    observations = []

    def fake_urlopen(request, *, timeout):
        method = request.get_method()
        calls.append(method)
        failing = method == failure_method and (
            method == "OPTIONS" or calls.count("POST") == 2
        )
        if failing and failure_status is None:
            raise URLError("synthetic transport failure")
        raise HTTPError(
            request.full_url, failure_status if failing else 404,
            "synthetic rejection", {}, None,
        )

    monkeypatch.setattr(sys.modules[__name__], "urlopen", fake_urlopen)
    expected_error = URLError if failure_status is None else AssertionError
    with pytest.raises(expected_error):
        _assert_canonical_reviewer_http_boundary(observations)

    evidence = _synthetic_runtime_evidence(_synthetic_child(), observations)
    assert calls.count("POST") == post_count
    assert evidence["command_run_post_performed"] is (post_count > 0)
    assert evidence["command_run_post_attempts"] == [
        {"method": "POST", "path": f"/commands/{key}/run", "response_status": status}
        for key, status in zip(("pytest_all", "topology_summary"), (404, failure_status))
    ][:post_count]
    assert evidence["http_requests"][-1]["response_status"] == failure_status
    assert evidence["request_methods"] == sorted(set(calls))
    assert evidence["request_method"] == ("MIXED" if post_count else "OPTIONS")
    assert evidence["report_files_unchanged"] is None
    assert evidence["command_execution"]["status"] == "NOT_INDEPENDENTLY_MEASURED"


def test_runtime_evidence_exposes_generic_bridge_classification() -> None:
    evidence = _synthetic_runtime_evidence(_synthetic_child())

    assert evidence["interpreter_classification"] == "environment_runtime_bridge"
    assert evidence["environment_runtime_bridge_detected"] is True
    assert evidence["exact_identity_match"] is True
    assert evidence["executable_paths_redacted"] is True


@pytest.fixture
def mocked_canonical_lifecycle(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import MagicMock, Mock

    module = sys.modules[__name__]
    process = Mock(pid=SYNTHETIC_PARENT_PID, returncode=None)
    process.poll.side_effect = lambda: process.returncode
    process.terminate.side_effect = lambda: setattr(process, "returncode", 1)
    process.stdout.read.return_value = "Running on http://127.0.0.1:5000"
    state = SimpleNamespace(
        html=b"Network Automation Lab - Portfolio Demo", options_status=404,
        process=process, popen=Mock(return_value=process),
        hashes=Mock(side_effect=[{"fixture": "same"}, {"fixture": "same"}]),
        sample=Mock(return_value=[]), classify=Mock(wraps=_classify_child_processes),
        exit_check=Mock(return_value=[]), port_check=Mock(return_value=True),
    )

    def fake_urlopen(request, *, timeout):
        method = request.get_method()
        if urlparse(request.full_url).path.startswith("/commands/"):
            raise HTTPError(
                request.full_url, state.options_status if method == "OPTIONS" else 404,
                "synthetic rejection", {}, None,
            )
        response = MagicMock(status=200, headers={"Allow": "GET, HEAD, OPTIONS"})
        response.__enter__.return_value = response
        response.read.return_value = b"" if method == "HEAD" else state.html
        return response

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    monkeypatch.setattr(subprocess, "Popen", state.popen)
    monkeypatch.setattr(socket, "socket", Mock(side_effect=AssertionError("Unexpected real socket")))
    monkeypatch.setattr(module, "_port_is_listening", Mock(return_value=False))
    monkeypatch.setattr(module, "_assert_port_can_be_bound", Mock())
    monkeypatch.setattr(module, "_report_file_hashes", state.hashes)
    monkeypatch.setattr(module, "_child_process_identities", state.sample)
    monkeypatch.setattr(module, "_classify_child_processes", state.classify)
    monkeypatch.setattr(module, "_wait_for_captured_processes_exit", state.exit_check)
    monkeypatch.setattr(module, "_wait_for_port_closed", state.port_check)
    return state


def _captured_runtime_receipt(capsys) -> dict[str, object]:
    prefix = "PHASE_2N_02_RUNTIME_EVIDENCE="
    receipts = [line[len(prefix):] for line in capsys.readouterr().out.splitlines() if line.startswith(prefix)]
    assert len(receipts) == 1
    return json.loads(receipts[0])


@pytest.mark.parametrize("failure_stage", ["GET", "OPTIONS", "HASH"])
def test_lifecycle_early_failure_receipt_is_unverified(
    mocked_canonical_lifecycle, capsys, failure_stage,
) -> None:
    runtime = mocked_canonical_lifecycle
    if failure_stage == "GET":
        runtime.html = b"Unexpected landing page"
    elif failure_stage == "OPTIONS":
        runtime.options_status = 405
    else:
        runtime.hashes.side_effect = [{"fixture": "before"}, {"fixture": "after"}]

    with pytest.raises(AssertionError) as failure:
        test_canonical_flask_process_lifecycle_and_get_only_routes()
    expected_origin = (
        "_assert_canonical_reviewer_http_boundary" if failure_stage == "OPTIONS"
        else "test_canonical_flask_process_lifecycle_and_get_only_routes"
    )
    assert failure.traceback[-1].name == expected_origin
    evidence = _captured_runtime_receipt(capsys)
    assert evidence["lifecycle_progress"] == {
        "sampling_started": False, "sampling_completed": False,
        "classification_completed": False, "cleanup_completed": True,
        "post_cleanup_check_completed": False, "port_check_completed": True,
    }
    assert evidence["identity_aware_contract_result"] is False
    assert evidence["identity_aware_contract_status"] == "NOT_VERIFIED"
    assert evidence["child_processes_exited"] is False
    assert evidence["child_processes_exit_status"] == "NOT_VERIFIED"
    assert evidence["interpreter_classification"] == "NOT_VERIFIED"
    assert evidence["process_exited"] is True
    assert evidence["port_closed"] is True
    assert evidence["cleanup_error_types"] == []
    assert evidence["command_run_post_performed"] is (failure_stage == "HASH")
    assert len(evidence["command_run_post_attempts"]) == (3 if failure_stage == "HASH" else 0)
    assert all(item["response_status"] == 404 for item in evidence["command_run_post_attempts"])
    assert evidence["report_files_unchanged"] is (False if failure_stage == "HASH" else None)
    runtime.sample.assert_not_called()
    runtime.classify.assert_not_called()
    runtime.exit_check.assert_not_called()
    runtime.process.terminate.assert_called_once()
    runtime.process.stdout.close.assert_called_once()


@pytest.mark.parametrize("unexpected,still_alive", [(False, False), (True, False), (True, True)])
def test_lifecycle_completed_observations_keep_independent_results(
    mocked_canonical_lifecycle, capsys, unexpected, still_alive,
) -> None:
    runtime = mocked_canonical_lifecycle
    if unexpected:
        runtime.sample.return_value = [_synthetic_child(filename="unknown.exe", full_image_path=None)]
    if still_alive:
        runtime.exit_check.return_value = [SYNTHETIC_CHILD_PID]
    if unexpected:
        with pytest.raises(AssertionError, match="unexpectedly spawned unclassified child processes"):
            test_canonical_flask_process_lifecycle_and_get_only_routes()
    else:
        test_canonical_flask_process_lifecycle_and_get_only_routes()
    evidence = _captured_runtime_receipt(capsys)
    assert all(evidence["lifecycle_progress"].values())
    assert evidence["identity_aware_contract_result"] is (not unexpected)
    assert evidence["identity_aware_contract_status"] == ("FAIL" if unexpected else "PASS")
    assert evidence["child_processes_exited"] is (not still_alive)
    assert evidence["child_processes_exit_status"] == ("FAIL" if still_alive else "PASS")
    assert evidence["command_run_post_performed"] is True
    assert len(evidence["command_run_post_attempts"]) == 3
    assert evidence["process_exited"] is True
    runtime.sample.assert_called_once_with(SYNTHETIC_PARENT_PID)
    runtime.exit_check.assert_called_once_with([SYNTHETIC_CHILD_PID] if unexpected else [])


@pytest.mark.parametrize("failure_stage", ["sampling", "classification"])
def test_lifecycle_incomplete_observation_preserves_original_error(
    mocked_canonical_lifecycle, capsys, failure_stage,
) -> None:
    runtime = mocked_canonical_lifecycle
    original = OSError("Synthetic observation failure")
    (runtime.sample if failure_stage == "sampling" else runtime.classify).side_effect = original
    with pytest.raises(OSError) as failure:
        test_canonical_flask_process_lifecycle_and_get_only_routes()
    assert failure.value is original
    evidence = _captured_runtime_receipt(capsys)
    sampled = failure_stage == "classification"
    assert evidence["lifecycle_progress"]["sampling_started"] is True
    assert evidence["lifecycle_progress"]["sampling_completed"] is sampled
    assert evidence["lifecycle_progress"]["classification_completed"] is False
    assert evidence["lifecycle_progress"]["post_cleanup_check_completed"] is sampled
    assert evidence["identity_aware_contract_status"] == "NOT_VERIFIED"
    assert evidence["identity_aware_contract_result"] is False
    assert evidence["child_processes_exited"] is sampled
    assert evidence["child_processes_exit_status"] == ("PASS" if sampled else "NOT_VERIFIED")
    assert evidence["interpreter_classification"] == "NOT_VERIFIED"
    assert evidence["process_exited"] is True


@pytest.mark.parametrize("failed_cleanup", ["stdout", "port"])
def test_lifecycle_cleanup_error_does_not_mask_get_failure(
    mocked_canonical_lifecycle, capsys, failed_cleanup,
) -> None:
    runtime = mocked_canonical_lifecycle
    runtime.html = b"Unexpected landing page"
    operation = runtime.process.stdout.close if failed_cleanup == "stdout" else runtime.port_check
    operation.side_effect = OSError("Synthetic cleanup failure")
    with pytest.raises(AssertionError, match="Network Automation Lab - Portfolio Demo") as failure:
        test_canonical_flask_process_lifecycle_and_get_only_routes()
    assert failure.traceback[-1].name == "test_canonical_flask_process_lifecycle_and_get_only_routes"
    evidence = _captured_runtime_receipt(capsys)
    assert evidence["cleanup_error_types"] == ["OSError"]
    assert evidence["lifecycle_progress"]["cleanup_completed"] is (failed_cleanup != "stdout")
    assert evidence["lifecycle_progress"]["port_check_completed"] is (failed_cleanup != "port")
    assert evidence["identity_aware_contract_status"] == "NOT_VERIFIED"
    assert evidence["child_processes_exit_status"] == "NOT_VERIFIED"
    assert evidence["process_exited"] is True
    runtime.process.terminate.assert_called_once()
    runtime.process.stdout.close.assert_called_once()


@pytest.mark.parametrize("unexpected", [False, True])
def test_lifecycle_failed_exit_inspection_cannot_claim_children_exited(
    mocked_canonical_lifecycle, capsys, unexpected,
) -> None:
    runtime = mocked_canonical_lifecycle
    original = OSError("Synthetic exit inspection failure")
    runtime.exit_check.side_effect = original
    if unexpected:
        runtime.sample.return_value = [_synthetic_child(filename="unknown.exe", full_image_path=None)]
        with pytest.raises(AssertionError, match="unexpectedly spawned unclassified child processes"):
            test_canonical_flask_process_lifecycle_and_get_only_routes()
    else:
        with pytest.raises(OSError) as failure:
            test_canonical_flask_process_lifecycle_and_get_only_routes()
        assert failure.value is original
    evidence = _captured_runtime_receipt(capsys)
    assert evidence["lifecycle_progress"]["sampling_completed"] is True
    assert evidence["lifecycle_progress"]["classification_completed"] is True
    assert evidence["lifecycle_progress"]["post_cleanup_check_completed"] is False
    assert evidence["identity_aware_contract_status"] == ("FAIL" if unexpected else "NOT_VERIFIED")
    assert evidence["identity_aware_contract_result"] is False
    assert evidence["child_processes_exit_status"] == "NOT_VERIFIED"
    assert evidence["child_processes_exited"] is False
    assert evidence["post_cleanup_child_state"] == []
    assert evidence["cleanup_error_types"] == ["OSError"]


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
