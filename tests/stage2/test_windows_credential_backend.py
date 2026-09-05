"""Offline tests for the bounded S2-RO-04 Windows credential backend."""

import ast
import ctypes
from ctypes import wintypes
from dataclasses import FrozenInstanceError, fields
import inspect
import json

import pytest

from validation_framework import stage2_windows_credential_backend as module
from validation_framework.stage2_mikrotik_credential_resolver import (
    STAGE2_CREDENTIAL_BACKEND_KIND,
    STAGE2_CREDENTIAL_LOCATOR_REF,
    STAGE2_FIXED_CREDENTIAL_REF,
    Stage2CredentialBinding,
    build_stage2_fixed_credential_resolver,
)
from validation_framework.stage2_windows_credential_backend import (
    MAX_CREDENTIAL_SECRET_BLOB_LENGTH,
    MAX_CREDENTIAL_USERNAME_LENGTH,
    Stage2CtypesWindowsCredentialApi,
    Stage2ResolvedCredential,
    Stage2TrustedWindowsCredentialConfiguration,
    Stage2WindowsCredentialApiRecord,
    Stage2WindowsCredentialError,
    Stage2WindowsCredentialFailure,
    build_stage2_windows_credential_backend,
)


_SYNTHETIC_TARGET = "synthetic.stage2.test.windows-credential-target"
_SYNTHETIC_USERNAME = "synthetic-readonly-user"
_SYNTHETIC_SECRET = b"synthetic-secret-bytes"


class FakeWindowsCredentialApi:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.read_calls = []

    def read_exact(self, credential_target):
        self.read_calls.append(credential_target)
        if self.error is not None:
            raise self.error
        return self.result


class _SyntheticCredentialW(ctypes.Structure):
    """Test-owned memory with the exact layout consumed by the adapter."""

    _fields_ = (
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    )


class _FakeNativeFunction:
    """Callable that accepts the ctypes signature assigned by production."""

    def __init__(self, implementation):
        self._implementation = implementation
        self.argtypes = None
        self.restype = None
        self.calls = []

    def __call__(self, *arguments):
        self.calls.append(arguments)
        return self._implementation(*arguments)


class _FakeAdvapi32:
    def __init__(self, credential_read, credential_free):
        self.CredReadW = _FakeNativeFunction(credential_read)
        self.CredFree = _FakeNativeFunction(credential_free)


def _native_boundary_harness(
    monkeypatch,
    *,
    username=_SYNTHETIC_USERNAME,
    secret_blob=_SYNTHETIC_SECRET,
    blob_size=None,
    null_blob=False,
    read_succeeds=True,
    string_at_error=None,
):
    """Install a structurally fake WinAPI before production can load a DLL."""

    state = {
        "events": [],
        "freed": False,
        "win_dll_calls": [],
    }
    username_buffer = (
        ctypes.create_unicode_buffer(username) if username is not None else None
    )
    blob_buffer = (ctypes.c_ubyte * max(1, len(secret_blob)))(
        *secret_blob,
        *([0] if not secret_blob else []),
    )
    credential = _SyntheticCredentialW()
    credential.UserName = (
        ctypes.cast(username_buffer, wintypes.LPWSTR)
        if username_buffer is not None
        else None
    )
    credential.CredentialBlobSize = (
        len(secret_blob) if blob_size is None else blob_size
    )
    credential.CredentialBlob = (
        ctypes.POINTER(ctypes.c_ubyte)()
        if null_blob
        else ctypes.cast(blob_buffer, ctypes.POINTER(ctypes.c_ubyte))
    )

    def fake_credential_read(target, credential_type, flags, output_pointer):
        state["events"].append("cred_read")
        assert target == _SYNTHETIC_TARGET
        assert credential_type == 1
        assert flags == 0
        if not read_succeeds:
            return 0
        output_slot = ctypes.cast(
            output_pointer,
            ctypes.POINTER(ctypes.c_void_p),
        )
        output_slot[0] = ctypes.addressof(credential)
        return 1

    def fake_credential_free(pointer):
        state["events"].append("cred_free")
        state["freed"] = True
        assert ctypes.cast(pointer, ctypes.c_void_p).value == ctypes.addressof(
            credential
        )
        credential.UserName = None
        credential.CredentialBlob = ctypes.POINTER(ctypes.c_ubyte)()
        if username_buffer is not None:
            for index in range(len(username_buffer)):
                username_buffer[index] = "\0"
        for index in range(len(blob_buffer)):
            blob_buffer[index] = 0

    fake_library = _FakeAdvapi32(fake_credential_read, fake_credential_free)

    def fake_win_dll(name, *, use_last_error):
        state["win_dll_calls"].append((name, use_last_error))
        return fake_library

    real_string_at = ctypes.string_at

    def guarded_string_at(pointer, size):
        assert not state["freed"], "native blob dereferenced after CredFree"
        state["events"].append("secret_read")
        if string_at_error is not None:
            raise string_at_error
        return real_string_at(pointer, size)

    monkeypatch.setattr(ctypes, "WinDLL", fake_win_dll, raising=False)
    monkeypatch.setattr(ctypes, "string_at", guarded_string_at)
    monkeypatch.setattr(module.sys, "platform", "win32")
    if not read_succeeds:
        monkeypatch.setattr(ctypes, "get_last_error", lambda: 1168)

    backend = build_stage2_windows_credential_backend(_configuration())
    return backend, fake_library, state


def _binding():
    return build_stage2_fixed_credential_resolver().resolve(
        STAGE2_FIXED_CREDENTIAL_REF
    )


def _configuration(**changes):
    values = {
        "locator_ref": STAGE2_CREDENTIAL_LOCATOR_REF,
        "credential_target": _SYNTHETIC_TARGET,
    }
    values.update(changes)
    return Stage2TrustedWindowsCredentialConfiguration(**values)


def _record(**changes):
    values = {
        "username": _SYNTHETIC_USERNAME,
        "secret_blob": _SYNTHETIC_SECRET,
    }
    values.update(changes)
    return Stage2WindowsCredentialApiRecord(**values)


def _backend(*, result=None, error=None):
    fake = FakeWindowsCredentialApi(result=result, error=error)
    backend = build_stage2_windows_credential_backend(
        _configuration(), windows_api=fake
    )
    return backend, fake


def _assert_error(function, code):
    with pytest.raises(Stage2WindowsCredentialError) as captured:
        function()
    assert captured.value.code is code
    assert str(captured.value) == code.value
    assert repr(captured.value) == f"Stage2WindowsCredentialError('{code.value}')"
    return captured.value


def _tampered_binding(**changes):
    original = _binding()
    result = object.__new__(Stage2CredentialBinding)
    for item in fields(Stage2CredentialBinding):
        object.__setattr__(
            result,
            item.name,
            changes.get(item.name, getattr(original, item.name)),
        )
    return result


def test_public_surface_and_bounds_are_exact_and_narrow():
    assert set(module.__all__) == {
        "MAX_CREDENTIAL_SECRET_BLOB_LENGTH",
        "MAX_CREDENTIAL_USERNAME_LENGTH",
        "MAX_WINDOWS_CREDENTIAL_TARGET_LENGTH",
        "Stage2CtypesWindowsCredentialApi",
        "Stage2ResolvedCredential",
        "Stage2TrustedWindowsCredentialConfiguration",
        "Stage2WindowsCredentialApi",
        "Stage2WindowsCredentialApiRecord",
        "Stage2WindowsCredentialBackend",
        "Stage2WindowsCredentialError",
        "Stage2WindowsCredentialFailure",
        "build_stage2_windows_credential_backend",
    }
    assert MAX_CREDENTIAL_USERNAME_LENGTH == 256
    assert MAX_CREDENTIAL_SECRET_BLOB_LENGTH == 4096


def test_exact_accepted_binding_reads_once_and_returns_immutable_material():
    backend, fake = _backend(result=_record())
    binding = _binding()
    before = (binding.credential_ref, binding.backend_kind, binding.locator_ref)

    credential = backend.read(binding)

    assert type(credential) is Stage2ResolvedCredential
    assert credential.username == _SYNTHETIC_USERNAME
    assert credential.secret_blob == _SYNTHETIC_SECRET
    assert fake.read_calls == [_SYNTHETIC_TARGET]
    assert (binding.credential_ref, binding.backend_kind, binding.locator_ref) == before
    with pytest.raises(FrozenInstanceError):
        credential.username = "changed"
    assert not hasattr(credential, "__dict__")


def test_success_is_deterministic_and_performs_no_retry_or_fallback():
    backend, fake = _backend(result=_record())

    first = backend.read(_binding())
    second = backend.read(_binding())

    assert first == second
    assert fake.read_calls == [_SYNTHETIC_TARGET, _SYNTHETIC_TARGET]


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        (
            {"backend_kind": "OTHER_BACKEND"},
            Stage2WindowsCredentialFailure.UNSUPPORTED_BACKEND,
        ),
        (
            {"locator_ref": "locator.stage2.mikrotik.lab02.readonly"},
            Stage2WindowsCredentialFailure.UNSUPPORTED_LOCATOR,
        ),
        (
            {"credential_ref": "credential.mikrotik.lab02"},
            Stage2WindowsCredentialFailure.INVALID_BINDING,
        ),
    ],
)
def test_wrong_binding_identity_rejects_before_api_call(changes, code):
    backend, fake = _backend(result=_record())

    _assert_error(lambda: backend.read(_tampered_binding(**changes)), code)

    assert fake.read_calls == []


@pytest.mark.parametrize("binding", [None, {}, object(), "credential"])
def test_malformed_binding_rejects_before_api_call(binding):
    backend, fake = _backend(result=_record())

    _assert_error(
        lambda: backend.read(binding),
        Stage2WindowsCredentialFailure.INVALID_BINDING,
    )

    assert fake.read_calls == []


def test_read_call_has_no_target_backend_locator_or_windows_options():
    backend, fake = _backend(result=_record())
    assert list(inspect.signature(backend.read).parameters) == ["binding"]

    with pytest.raises(TypeError):
        backend.read(_binding(), credential_target="alternate")
    with pytest.raises(TypeError):
        backend.read(_binding(), backend_kind="OTHER_BACKEND")
    with pytest.raises(TypeError):
        backend.read(_binding(), locator_ref="alternate")
    with pytest.raises(TypeError):
        backend.read(_binding(), credential_type=2, read_flags=1)

    assert fake.read_calls == []


@pytest.mark.parametrize(
    "changes",
    [
        {"locator_ref": "locator.stage2.mikrotik.lab02.readonly"},
        {"locator_ref": None},
        {"credential_target": ""},
        {"credential_target": " target"},
        {"credential_target": "target\nvalue"},
        {"credential_target": None},
        {"credential_target": "x" * 513},
    ],
)
def test_trusted_configuration_rejects_alternate_locator_or_bad_target(changes):
    _assert_error(
        lambda: _configuration(**changes),
        Stage2WindowsCredentialFailure.INVALID_TRUSTED_CONFIGURATION,
    )


def test_configuration_backend_api_record_and_material_repr_are_redacted():
    configuration = _configuration()
    record = _record()
    backend, _ = _backend(result=record)
    credential = backend.read(_binding())

    rendered = " ".join(
        (
            repr(configuration),
            str(configuration),
            repr(record),
            str(record),
            repr(backend),
            str(backend),
            repr(credential),
            str(credential),
        )
    )
    assert _SYNTHETIC_TARGET not in rendered
    assert _SYNTHETIC_USERNAME not in rendered
    assert _SYNTHETIC_SECRET.decode() not in rendered
    assert rendered.count("redacted") >= 6


def test_resolved_credential_has_only_required_fields_and_no_serialization_api():
    backend, _ = _backend(result=_record())
    credential = backend.read(_binding())

    assert {item.name for item in fields(credential)} == {
        "username",
        "secret_blob",
    }
    assert not hasattr(credential, "to_dict")
    assert not hasattr(credential, "to_json")
    with pytest.raises(TypeError):
        json.dumps(credential)


def test_not_found_fails_closed_after_exactly_one_read():
    backend, fake = _backend(result=None)

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_NOT_FOUND,
    )

    assert fake.read_calls == [_SYNTHETIC_TARGET]


def test_api_error_is_sanitized_and_does_not_expose_material():
    unsafe_message = (
        f"{_SYNTHETIC_TARGET}:{_SYNTHETIC_USERNAME}:"
        f"{_SYNTHETIC_SECRET.decode()}"
    )
    backend, fake = _backend(error=OSError(unsafe_message))

    error = _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_READ_FAILED,
    )

    rendered = f"{error!r} {error!s}"
    assert _SYNTHETIC_TARGET not in rendered
    assert _SYNTHETIC_USERNAME not in rendered
    assert _SYNTHETIC_SECRET.decode() not in rendered
    assert error.__context__ is None
    assert error.__cause__ is None
    assert fake.read_calls == [_SYNTHETIC_TARGET]


@pytest.mark.parametrize(
    ("result", "code"),
    [
        (object(), Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD),
        (_record(username=None), Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING),
        (_record(username=""), Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING),
        (_record(username="   "), Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING),
        (_record(username=b"user"), Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD),
        (_record(username=" user"), Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD),
        (_record(username="user\nname"), Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD),
        (
            _record(username="u" * (MAX_CREDENTIAL_USERNAME_LENGTH + 1)),
            Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_TOO_LONG,
        ),
        (_record(secret_blob=None), Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID),
        (_record(secret_blob=b""), Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID),
        (_record(secret_blob="secret"), Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID),
        (_record(secret_blob=bytearray(b"secret")), Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID),
        (
            _record(secret_blob=b"x" * (MAX_CREDENTIAL_SECRET_BLOB_LENGTH + 1)),
            Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_TOO_LARGE,
        ),
    ],
)
def test_malformed_or_unbounded_api_result_fails_closed(result, code):
    backend, fake = _backend(result=result)

    _assert_error(lambda: backend.read(_binding()), code)

    assert fake.read_calls == [_SYNTHETIC_TARGET]


def test_non_windows_real_adapter_path_fails_without_loading_windows_api(monkeypatch):
    invoked = []

    def unexpected_call(_target):
        invoked.append(True)
        raise AssertionError("Windows API boundary must not be loaded")

    monkeypatch.setattr(module.sys, "platform", "linux")
    monkeypatch.setattr(module, "_read_windows_credential_exact", unexpected_call)
    backend = build_stage2_windows_credential_backend(_configuration())

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.UNSUPPORTED_PLATFORM,
    )

    assert invoked == []


def test_fake_api_is_used_without_calling_real_adapter(monkeypatch):
    real_calls = []

    def unexpected_call(_target):
        real_calls.append(True)
        raise AssertionError("real adapter called")

    monkeypatch.setattr(module, "_read_windows_credential_exact", unexpected_call)
    backend, fake = _backend(result=_record())

    assert backend.read(_binding()).secret_blob == _SYNTHETIC_SECRET
    assert fake.read_calls == [_SYNTHETIC_TARGET]
    assert real_calls == []


def test_real_adapter_exposes_only_one_fixed_read_operation():
    api = Stage2CtypesWindowsCredentialApi()
    public_callables = {
        name
        for name in dir(api)
        if not name.startswith("_") and callable(getattr(api, name))
    }
    assert public_callables == {"read_exact"}
    assert list(inspect.signature(api.read_exact).parameters) == [
        "credential_target"
    ]


def test_native_success_copies_before_free_without_pointer_escape(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(monkeypatch)

    resolved = backend.read(_binding())

    assert type(resolved.username) is str
    assert type(resolved.secret_blob) is bytes
    assert resolved.username == _SYNTHETIC_USERNAME
    assert resolved.secret_blob == _SYNTHETIC_SECRET
    assert state["events"] == ["cred_read", "secret_read", "cred_free"]
    assert state["freed"] is True
    assert state["win_dll_calls"] == [("Advapi32.dll", True)]
    assert len(fake_library.CredReadW.calls) == 1
    assert len(fake_library.CredFree.calls) == 1
    assert fake_library.CredReadW.argtypes[:3] == (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
    )
    assert len(fake_library.CredReadW.argtypes) == 4
    assert fake_library.CredReadW.restype is wintypes.BOOL
    assert fake_library.CredFree.argtypes == (ctypes.c_void_p,)
    assert fake_library.CredFree.restype is None
    assert not hasattr(resolved.username, "contents")
    assert not hasattr(resolved.secret_blob, "contents")


def test_native_allocated_null_username_rejects_and_frees_once(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        username=None,
    )

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING,
    )

    assert state["events"] == ["cred_read", "secret_read", "cred_free"]
    assert len(fake_library.CredFree.calls) == 1


@pytest.mark.parametrize(
    ("blob_size", "code"),
    [
        (1, Stage2WindowsCredentialFailure.CREDENTIAL_READ_FAILED),
        (0, Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID),
    ],
)
def test_native_allocated_null_blob_rejects_and_frees_once(
    monkeypatch,
    blob_size,
    code,
):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        blob_size=blob_size,
        null_blob=True,
    )

    _assert_error(lambda: backend.read(_binding()), code)

    assert state["events"][-1] == "cred_free"
    assert len(fake_library.CredFree.calls) == 1


def test_native_allocated_oversized_username_rejects_and_frees_once(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        username="u" * (MAX_CREDENTIAL_USERNAME_LENGTH + 1),
    )

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_TOO_LONG,
    )

    assert state["events"] == ["cred_read", "secret_read", "cred_free"]
    assert len(fake_library.CredFree.calls) == 1


def test_native_allocated_oversized_blob_rejects_and_frees_once(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        blob_size=MAX_CREDENTIAL_SECRET_BLOB_LENGTH + 1,
    )

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_TOO_LARGE,
    )

    assert state["events"] == ["cred_read", "cred_free"]
    assert len(fake_library.CredFree.calls) == 1


def test_native_post_allocation_copy_exception_still_frees_once(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        string_at_error=RuntimeError("synthetic post-allocation failure"),
    )

    error = _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_READ_FAILED,
    )

    assert "synthetic" not in str(error)
    assert state["events"] == ["cred_read", "secret_read", "cred_free"]
    assert len(fake_library.CredFree.calls) == 1


def test_native_credread_failure_without_allocation_does_not_free(monkeypatch):
    backend, fake_library, state = _native_boundary_harness(
        monkeypatch,
        read_succeeds=False,
    )

    _assert_error(
        lambda: backend.read(_binding()),
        Stage2WindowsCredentialFailure.CREDENTIAL_NOT_FOUND,
    )

    assert state["events"] == ["cred_read"]
    assert len(fake_library.CredReadW.calls) == 1
    assert fake_library.CredFree.calls == []


def test_source_has_no_mutating_discovery_subprocess_or_network_capability():
    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert imported_roots.isdisjoint(
        {
            "keyring",
            "os",
            "paramiko",
            "pathlib",
            "requests",
            "socket",
            "subprocess",
            "win32cred",
            "winreg",
        }
    )
    for forbidden_symbol in (
        "CredEnumerateW",
        "CredWriteW",
        "CredDeleteW",
        "CryptUnprotectData",
        "PowerShell",
        "cmd.exe",
        "cmdkey",
    ):
        assert forbidden_symbol not in source
    assert not any(
        isinstance(node, ast.Name) and node.id in {"open", "exec", "eval"}
        for node in ast.walk(tree)
    )


def test_backend_contains_no_cache_evidence_or_transport_surface():
    backend, _ = _backend(result=_record())
    forbidden_names = {
        "connect",
        "delete",
        "enumerate",
        "execute",
        "get",
        "list",
        "load",
        "persist",
        "remove",
        "save",
        "serialize",
        "set",
        "to_dict",
        "to_json",
        "update",
        "write",
    }
    assert forbidden_names.isdisjoint(set(dir(backend)))
    assert not hasattr(module, "_credential_cache")
    assert not hasattr(module, "credential_cache")


def test_fixed_policy_matches_accepted_s2_ro_03_binding():
    binding = _binding()
    assert binding.credential_ref == STAGE2_FIXED_CREDENTIAL_REF
    assert binding.backend_kind == STAGE2_CREDENTIAL_BACKEND_KIND
    assert binding.locator_ref == STAGE2_CREDENTIAL_LOCATOR_REF
