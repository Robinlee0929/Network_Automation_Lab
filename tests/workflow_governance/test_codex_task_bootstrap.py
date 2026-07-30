"""Tests for the two-stage workflow bootstrap helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[2] / "scripts" / "codex_task_bootstrap.py"


def load_module() -> ModuleType:
    """Load the authorized script without requiring a package file."""

    spec = importlib.util.spec_from_file_location("codex_task_bootstrap", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def completed(
    argv: list[str], stdout: bytes = b"", returncode: int = 0
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr=b"")


def test_prereq_performs_no_git_invocation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = tmp_path / "repo"
    repo.mkdir()
    skill = tmp_path / "SKILL.md"
    skill.write_text("skill", encoding="utf-8")
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: pytest.fail("Git invoked"))
    report, status = module.build_prereq_report(str(repo), str(skill))
    assert status == 0
    assert report["result"] == "PASS"


def test_prereq_rejects_missing_repository(tmp_path: Path) -> None:
    module = load_module()
    skill = tmp_path / "SKILL.md"
    skill.write_text("skill", encoding="utf-8")
    report, status = module.build_prereq_report(str(tmp_path / "missing"), str(skill))
    assert status == 2
    assert report["result"] == "ERROR"


def test_prereq_rejects_missing_skill(tmp_path: Path) -> None:
    module = load_module()
    report, status = module.build_prereq_report(str(tmp_path), str(tmp_path / "missing.md"))
    assert status == 2
    assert report["skill_path_exists"] is False


def test_prereq_output_is_deterministic_and_has_exact_next_command(tmp_path: Path) -> None:
    module = load_module()
    skill = tmp_path / "SKILL.md"
    skill.write_text("skill", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    first = module.build_prereq_report(str(tmp_path), str(skill))
    second = module.build_prereq_report(str(tmp_path), str(skill))
    assert first == second
    assert first[0]["next_required_command"] == "git status --short --branch"


def test_prereq_makes_no_semantic_or_history_claim(tmp_path: Path) -> None:
    module = load_module()
    skill = tmp_path / "SKILL.md"
    skill.write_text("skill", encoding="utf-8")
    report, _ = module.build_prereq_report(str(tmp_path), str(skill))
    assert report["semantic_reading_proven"] is False
    assert report["existence_proves_semantic_reading"] is False
    assert report["first_git_history_proven"] is False
    assert "SKILL_READ_COMPLETELY" not in report
    assert "PRE_GIT_GATE_PASSED" not in report


def test_inspect_refuses_without_caller_confirmation(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        return completed(argv)

    report, status = module.build_inspect_report(
        str(tmp_path), caller_confirms_gate=False, runner=runner
    )
    assert status == 2
    assert calls == []
    assert report["first_git_history_independently_verified"] is False


def test_inspect_rejects_invalid_repository_before_git(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []
    report, status = module.build_inspect_report(
        str(tmp_path / "missing"),
        caller_confirms_gate=True,
        runner=lambda argv, **kwargs: calls.append(argv),
    )
    assert status == 2
    assert calls == []
    assert report["result"] == "ERROR"


@pytest.mark.parametrize("confirmation", ["false", "true", 1, 2, [], [True]])
def test_inspect_requires_literal_true(tmp_path: Path, confirmation: object) -> None:
    module = load_module()
    calls: list[list[str]] = []
    report, status = module.build_inspect_report(
        str(tmp_path), caller_confirms_gate=confirmation, runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert calls == []
    assert report["caller_confirms_first_git_gate"] is False


def test_custom_truthy_confirmation_is_rejected(tmp_path: Path) -> None:
    module = load_module()

    class Truthy:
        def __bool__(self) -> bool:
            return True

    calls: list[list[str]] = []
    _, status = module.build_inspect_report(
        str(tmp_path), caller_confirms_gate=Truthy(), runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert calls == []


def test_inspect_uses_only_read_only_git_commands(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        subcommand = argv[3]
        if subcommand == "rev-parse":
            output = b"true\n" if argv[-1] == "--is-inside-work-tree" else b"a" * 40 + b"\n"
        elif subcommand == "branch":
            output = b"codex/test\n"
        else:
            output = b""
        return completed(argv, output)

    report, status = module.build_inspect_report(
        str(tmp_path), caller_confirms_gate=True, runner=runner
    )
    assert status == 0
    assert report["branch"] == "codex/test"
    assert {argv[3] for argv in calls} <= module.READ_ONLY_GIT_SUBCOMMANDS
    assert all("remote" not in argv and "fetch" not in argv for argv in calls)


def test_optional_inspection_remains_local_and_read_only(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        subcommand = argv[3]
        if subcommand == "rev-parse":
            output = b"true\n" if argv[-1] == "--is-inside-work-tree" else b"a" * 40 + b"\n"
        elif subcommand == "branch":
            output = b"codex/test\n"
        elif subcommand == "worktree":
            output = f"worktree {tmp_path}".encode("utf-8") + b"\0"
        elif subcommand == "for-each-ref":
            output = b"origin/main\n"
        else:
            output = b""
        return completed(argv, output)

    report, status = module.build_inspect_report(
        str(tmp_path),
        caller_confirms_gate=True,
        include_worktrees=True,
        include_local_tracking=True,
        runner=runner,
    )
    assert status == 0
    assert report["local_tracking_refs"] == ["origin/main"]
    assert all(argv[3] != "remote" for argv in calls)


@pytest.mark.parametrize(
    "args",
    [
        ["fetch"],
        ["push"],
        ["reset"],
        ["commit"],
        ["worktree", "add"],
        ["symbolic-ref", "HEAD", "refs/heads/unsafe"],
        ["branch", "--show-current", "extra"],
        ["rev-parse", "--verify", "HEAD", "extra"],
    ],
)
def test_modifying_remote_or_extra_git_argv_are_rejected(tmp_path: Path, args: list[str]) -> None:
    module = load_module()
    with pytest.raises(ValueError):
        module.run_read_only_git(tmp_path, args)


@pytest.mark.parametrize("args", sorted(module_args for module_args in [
    ["branch", "--show-current"],
    ["diff", "--cached", "--name-only", "-z"],
    ["diff", "--name-only", "-z"],
    ["ls-files", "--others", "--exclude-standard", "-z"],
    ["rev-parse", "--is-inside-work-tree"],
    ["rev-parse", "--verify", "HEAD"],
]))
def test_permitted_exact_git_argv_is_accepted(tmp_path: Path, args: list[str]) -> None:
    module = load_module()
    calls: list[list[str]] = []
    module.run_read_only_git(
        tmp_path,
        args,
        runner=lambda argv, **kwargs: calls.append(argv) or completed(argv),
    )
    assert calls[0][3:] == args


def test_malformed_git_bytes_return_structured_error(tmp_path: Path) -> None:
    module = load_module()

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        if argv[3:] == ["rev-parse", "--is-inside-work-tree"]:
            return completed(argv, b"true\n")
        if argv[3:] == ["rev-parse", "--verify", "HEAD"]:
            return completed(argv, b"a" * 40 + b"\n")
        if argv[3:] == ["branch", "--show-current"]:
            return completed(argv, b"codex/test\n")
        return completed(argv, b"bad-\xff\0")

    report, status = module.build_inspect_report(
        str(tmp_path), caller_confirms_gate=True, runner=runner
    )
    assert status == 2
    assert report["result"] == "ERROR"
    assert "valid UTF-8" in report["errors"][0]
