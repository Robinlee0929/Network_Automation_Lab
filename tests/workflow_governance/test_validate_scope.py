"""Tests for exact read-only Git scope validation."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[2] / "scripts" / "validate_scope.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_scope", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        shell=False,
    )
    return result.stdout.strip()


def initialized_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Workflow Tests")
    tracked = repo / "tracked.txt"
    tracked.write_text("initial content\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "initial")
    return repo


def test_exact_allowed_untracked_set_passes(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "new.py").write_text("print('ok')\n", encoding="utf-8")
    report, status = module.validate_scope(str(repo), ["new.py"])
    assert status == 0
    assert report["result"] == "PASS"
    assert report["actual_files"] == ["new.py"]


def test_unexpected_staged_file_fails(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "unexpected.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "unexpected.py")
    report, status = module.validate_scope(str(repo), ["tracked.txt"])
    assert status == 1
    assert report["unexpected_files"] == ["unexpected.py"]


def test_unexpected_unstaged_file_fails(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
    report, status = module.validate_scope(str(repo), ["other.txt"])
    assert status == 1
    assert report["unstaged_files"] == ["tracked.txt"]


def test_unexpected_untracked_file_fails(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "surprise.txt").write_text("new\n", encoding="utf-8")
    report, status = module.validate_scope(str(repo), ["tracked.txt"])
    assert status == 1
    assert report["untracked_files"] == ["surprise.txt"]


def test_added_and_deleted_files_are_reported(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "added.txt").write_text("added\n", encoding="utf-8")
    (repo / "tracked.txt").unlink()
    git(repo, "add", "-A")
    report, status = module.validate_scope(str(repo), ["added.txt", "tracked.txt"])
    assert status == 0
    assert report["added_files"] == ["added.txt"]
    assert report["deleted_files"] == ["tracked.txt"]


def test_rename_exposes_old_and_new_paths(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    git(repo, "mv", "tracked.txt", "renamed.txt")
    report, status = module.validate_scope(str(repo), ["tracked.txt", "renamed.txt"])
    assert status == 0
    assert report["actual_files"] == ["renamed.txt", "tracked.txt"]
    assert report["renamed_files"] == [{"new_path": "renamed.txt", "old_path": "tracked.txt"}]


def test_unicode_cross_directory_rename_exposes_both_paths(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    source = repo / "舊目錄"
    target = repo / "新目錄"
    source.mkdir()
    target.mkdir()
    unicode_file = source / "網路 測試.txt"
    unicode_file.write_text("內容\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "unicode source")
    git(repo, "mv", "舊目錄/網路 測試.txt", "新目錄/網路 測試.txt")
    report, status = module.validate_scope(
        str(repo), ["舊目錄/網路 測試.txt", "新目錄/網路 測試.txt"]
    )
    assert status == 0
    assert report["renamed_files"] == [
        {"new_path": "新目錄/網路 測試.txt", "old_path": "舊目錄/網路 測試.txt"}
    ]


def test_cumulative_base_to_head_scope(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    (repo / "cumulative.txt").write_text("new\n", encoding="utf-8")
    git(repo, "add", "cumulative.txt")
    git(repo, "commit", "-m", "cumulative")
    head = git(repo, "rev-parse", "HEAD")
    report, status = module.validate_scope(
        str(repo), ["cumulative.txt"], base=base, head=head
    )
    assert status == 0
    assert report["cumulative_files"] == ["cumulative.txt"]


def test_path_separator_normalization_and_deterministic_order(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    (repo / "dir").mkdir()
    (repo / "dir" / "b.py").write_text("b=1\n", encoding="utf-8")
    (repo / "a.py").write_text("a=1\n", encoding="utf-8")
    first = module.validate_scope(str(repo), ["dir\\b.py", "a.py"])
    second = module.validate_scope(str(repo), ["a.py", "dir/b.py"])
    assert first == second
    assert first[0]["actual_files"] == ["a.py", "dir/b.py"]


def test_missing_required_file_fails(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    report, status = module.validate_scope(
        str(repo), ["required.py"], ["required.py"]
    )
    assert status == 1
    assert report["missing_required_files"] == ["required.py"]


def test_absolute_external_path_is_rejected(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    external = tmp_path / "outside.py"
    report, status = module.validate_scope(str(repo), [str(external)])
    assert status == 2
    assert "escapes repository" in report["errors"][0]


def test_parent_escape_is_rejected(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    report, status = module.validate_scope(str(repo), ["../outside.py"])
    assert status == 2
    assert report["result"] == "ERROR"


def test_symlink_escape_is_rejected_when_supported(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = repo / "link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    report, status = module.validate_scope(str(repo), ["link.txt"])
    assert status == 2
    assert "escapes repository" in report["errors"][0]


def test_head_without_base_is_execution_error(tmp_path: Path) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    report, status = module.validate_scope(str(repo), ["tracked.txt"], head="HEAD")
    assert status == 2
    assert "requires --base" in report["errors"][0]


@pytest.mark.parametrize("revision_name", ["base", "head"])
def test_option_like_revision_cannot_create_external_file(
    tmp_path: Path, revision_name: str
) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    commit = git(repo, "rev-parse", "HEAD")
    external = tmp_path / f"{revision_name}-escaped.txt"
    kwargs = {"base": commit, "head": commit}
    kwargs[revision_name] = f"--output={external}"
    before = git(repo, "status", "--porcelain=v1")
    report, status = module.validate_scope(str(repo), ["tracked.txt"], **kwargs)
    assert status == 2
    assert report["result"] == "ERROR"
    assert not external.exists()
    assert git(repo, "status", "--porcelain=v1") == before
    json.dumps(report, ensure_ascii=False)


@pytest.mark.parametrize("revision_name", ["base", "head"])
def test_option_like_revision_cli_emits_json_and_exit_two(
    tmp_path: Path, revision_name: str
) -> None:
    repo = initialized_repo(tmp_path)
    commit = git(repo, "rev-parse", "HEAD")
    external = tmp_path / f"cli-{revision_name}-escaped.txt"
    argv = [
        sys.executable,
        "-B",
        str(SCRIPT),
        "--repo",
        str(repo),
        "--allowed-file",
        "tracked.txt",
        f"--base={commit}",
        f"--head={commit}",
    ]
    option = f"--{revision_name}=--output={external}"
    argv[argv.index(next(item for item in argv if item.startswith(f"--{revision_name}=")))] = option
    result = subprocess.run(argv, capture_output=True, text=True, check=False, shell=False)
    assert result.returncode == 2
    assert json.loads(result.stdout)["result"] == "ERROR"
    assert not external.exists()


@pytest.mark.parametrize("revision", ["", "missing-revision", "HEAD..HEAD", "HEAD\nHEAD"])
def test_invalid_or_missing_revision_is_structured_error(tmp_path: Path, revision: str) -> None:
    module = load_module()
    repo = initialized_repo(tmp_path)
    report, status = module.validate_scope(
        str(repo), ["tracked.txt"], base=revision, head="HEAD"
    )
    assert status == 2
    assert report["result"] == "ERROR"
    assert report["errors"]
    json.dumps(report, ensure_ascii=False)


def test_malformed_nul_records_and_invalid_utf8_are_rejected() -> None:
    module = load_module()
    with pytest.raises(ValueError, match="missing NUL terminator"):
        module.parse_name_status(b"A\0path.txt")
    with pytest.raises(ValueError, match="valid UTF-8"):
        module.parse_name_status(b"A\0bad-\xff.txt\0")
    with pytest.raises(ValueError, match="rename"):
        module.parse_name_status(b"R100\0old.txt\0")


def test_cumulative_diff_uses_resolved_object_ids_and_path_boundary(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []
    object_id = b"a" * 40 + b"\n"

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        if argv[3:] == ["rev-parse", "--is-inside-work-tree"]:
            stdout = b"true\n"
        elif argv[3] == "rev-parse":
            stdout = object_id
        else:
            stdout = b""
        return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr=b"")

    report, status = module.validate_scope(
        str(tmp_path), ["allowed.py"], base="HEAD^", head="HEAD", runner=runner
    )
    assert status == 0
    cumulative = next(argv for argv in calls if argv[3:5] == ["diff", "--name-status"] and argv[-1] == "--")
    assert cumulative[-3:] == ["a" * 40, "a" * 40, "--"]
    assert "HEAD^..HEAD" not in cumulative


def test_helper_constructs_no_modifying_git_command(tmp_path: Path) -> None:
    module = load_module()
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        stdout = b"true\n" if argv[3] == "rev-parse" else b""
        return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr=b"")

    report, status = module.validate_scope(str(tmp_path), ["allowed.py"], runner=runner)
    assert status == 0
    assert report["result"] == "PASS"
    assert {argv[3] for argv in calls} <= module.READ_ONLY_GIT_SUBCOMMANDS
    forbidden = {"add", "commit", "reset", "clean", "checkout", "switch", "merge", "rebase"}
    assert all(not (set(argv[3:]) & forbidden) for argv in calls)
