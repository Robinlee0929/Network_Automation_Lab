"""Validate exact working-tree and cumulative Git file scope read-only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
from typing import Callable, Sequence


READ_ONLY_GIT_SUBCOMMANDS = {"diff", "ls-files", "rev-parse"}
HEX_OBJECT_LENGTHS = {40, 64}


def emit_json(payload: dict[str, object]) -> None:
    """Write deterministic JSON to stdout."""

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def normalize_repository_path(path: Path) -> str:
    """Return a resolved repository path with forward slashes."""

    return path.resolve(strict=False).as_posix()


def normalize_authorized_path(repo: Path, raw: str) -> str:
    """Normalize one authorized path and reject repository-boundary escapes."""

    if not isinstance(raw, str) or not raw:
        raise ValueError("path must be a non-empty string")
    if any(ord(character) < 32 or ord(character) == 127 for character in raw):
        raise ValueError(f"path contains a control character: {raw!r}")
    cleaned = raw.replace("\\", "/")
    pure = PurePosixPath(cleaned)
    windows = PureWindowsPath(raw)
    if cleaned.startswith("/") or windows.is_absolute() or windows.drive:
        raise ValueError(f"path escapes repository: {raw}")
    if not pure.parts or pure.parts[0].startswith("-") or ".." in pure.parts:
        raise ValueError(f"path escapes repository: {raw}")
    candidate = repo.joinpath(*pure.parts)
    resolved_repo = repo.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        relative = resolved_candidate.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {raw}") from exc
    normalized = PurePosixPath(relative.as_posix()).as_posix()
    if normalized in {"", "."}:
        raise ValueError(f"path must identify a file below the repository: {raw}")
    return normalized


def normalize_git_path(raw: str) -> str:
    """Normalize a repository-relative path reported by Git."""

    if not isinstance(raw, str) or not raw:
        raise ValueError("malformed Git path: empty path")
    if any(ord(character) < 32 or ord(character) == 127 for character in raw):
        raise ValueError(f"malformed Git path: {raw!r}")
    cleaned = raw.replace("\\", "/")
    path = PurePosixPath(cleaned)
    windows = PureWindowsPath(raw)
    if (
        path.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or ".." in path.parts
        or cleaned in {"", "."}
        or not path.parts
        or path.parts[0].startswith("-")
    ):
        raise ValueError(f"malformed Git path: {raw!r}")
    return path.as_posix()


def run_read_only_git(
    repo: Path,
    args: Sequence[str],
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> subprocess.CompletedProcess[bytes]:
    """Run one allowlisted read-only local Git command."""

    command = tuple(args)
    fixed_commands = {
        ("rev-parse", "--is-inside-work-tree"),
        ("diff", "--cached", "--name-status", "-z", "--find-renames"),
        ("diff", "--name-status", "-z", "--find-renames"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    }
    revision_resolution = (
        len(command) == 4
        and command[:3] == ("rev-parse", "--verify", "--end-of-options")
        and command[3].endswith("^{commit}")
    )
    cumulative_diff = (
        len(command) == 7
        and command[:4] == ("diff", "--name-status", "-z", "--find-renames")
        and all(
            len(object_id) in HEX_OBJECT_LENGTHS
            and all(character in "0123456789abcdefABCDEF" for character in object_id)
            for object_id in command[4:6]
        )
        and command[6] == "--"
    )
    if command not in fixed_commands and not revision_resolution and not cumulative_diff:
        raise ValueError("Git argv is not an exact read-only command shape")
    return runner(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
        shell=False,
    )


def _require_bytes(value: bytes | None, label: str) -> bytes:
    if value is None:
        raise ValueError(f"{label} produced missing output")
    if not isinstance(value, bytes):
        raise ValueError(f"{label} did not produce binary output")
    return value


def _decode_diagnostic(value: bytes | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, bytes):
        return "invalid non-binary Git diagnostic"
    return value.decode("utf-8", errors="replace").strip()


def require_success(result: subprocess.CompletedProcess[bytes], label: str) -> bytes:
    """Return stdout or raise an execution error."""

    if result.returncode != 0:
        detail = _decode_diagnostic(result.stderr) or _decode_diagnostic(result.stdout) or "unknown Git error"
        raise RuntimeError(f"{label} failed: {detail}")
    return _require_bytes(result.stdout, label)


def _decode_ascii(value: bytes, label: str) -> str:
    try:
        return value.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} was not ASCII") from exc


def _decode_git_path(value: bytes) -> str:
    try:
        return value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("Git path output was not valid UTF-8") from exc


def _nul_records(value: bytes | None, label: str) -> list[bytes]:
    raw = _require_bytes(value, label)
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        raise ValueError(f"malformed {label}: missing NUL terminator")
    records = raw[:-1].split(b"\0")
    if any(record == b"" for record in records):
        raise ValueError(f"malformed {label}: empty NUL record")
    return records


def validate_revision(value: str | None, label: str) -> str:
    """Validate one unresolved revision without permitting option/range syntax."""

    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} revision must be a non-empty string")
    if value.startswith("-"):
        raise ValueError(f"{label} revision must not begin with '-'")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{label} revision contains a control character")
    if ".." in value:
        raise ValueError(f"{label} revision must identify one revision, not a range")
    return value


def resolve_commit(
    repo: Path,
    revision: str | None,
    label: str,
    runner: Callable[..., subprocess.CompletedProcess[bytes]],
) -> str:
    """Resolve one validated revision to a hexadecimal commit object ID."""

    selected = validate_revision(revision, label)
    raw = require_success(
        run_read_only_git(
            repo,
            ["rev-parse", "--verify", "--end-of-options", f"{selected}^{{commit}}"],
            runner,
        ),
        f"{label} revision resolution",
    )
    object_id = _decode_ascii(raw, f"{label} commit object ID").strip()
    if len(object_id) not in HEX_OBJECT_LENGTHS or any(character not in "0123456789abcdefABCDEF" for character in object_id):
        raise ValueError(f"{label} revision did not resolve to a hexadecimal commit object ID")
    return object_id.lower()


def parse_name_status(value: bytes | None) -> tuple[set[str], set[str], set[str], list[dict[str, str]]]:
    """Parse ``git diff --name-status -z`` including both sides of renames."""

    tokens = _nul_records(value, "Git name-status output")
    paths: set[str] = set()
    added: set[str] = set()
    deleted: set[str] = set()
    renames: list[dict[str, str]] = []
    index = 0
    while index < len(tokens):
        status = _decode_ascii(tokens[index], "Git status record")
        index += 1
        if not status:
            raise ValueError("malformed Git name-status output: empty status")
        kind = status[0]
        if kind in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise ValueError("malformed Git rename output")
            old_path = normalize_git_path(_decode_git_path(tokens[index]))
            new_path = normalize_git_path(_decode_git_path(tokens[index + 1]))
            index += 2
            paths.update({old_path, new_path})
            renames.append({"new_path": new_path, "old_path": old_path})
            continue
        if index >= len(tokens):
            raise ValueError("malformed Git name-status output: missing path")
        path = normalize_git_path(_decode_git_path(tokens[index]))
        index += 1
        paths.add(path)
        if kind == "A":
            added.add(path)
        elif kind == "D":
            deleted.add(path)
    return paths, added, deleted, renames


def parse_nul_paths(value: bytes | None) -> set[str]:
    """Parse a NUL-delimited path list."""

    return {normalize_git_path(_decode_git_path(item)) for item in _nul_records(value, "Git path output")}


def _empty_report(repo: Path) -> dict[str, object]:
    return {
        "actual_files": [],
        "added_files": [],
        "allowed_files": [],
        "cumulative_files": [],
        "deleted_files": [],
        "errors": [],
        "missing_required_files": [],
        "renamed_files": [],
        "repository_path": normalize_repository_path(repo),
        "required_files": [],
        "result": "ERROR",
        "staged_files": [],
        "unexpected_files": [],
        "unstaged_files": [],
        "untracked_files": [],
    }


def validate_scope(
    repo_arg: str,
    allowed_args: Sequence[str],
    required_args: Sequence[str] = (),
    *,
    base: str | None = None,
    head: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> tuple[dict[str, object], int]:
    """Inspect and validate exact scope, returning JSON-ready evidence and status."""

    repo = Path(repo_arg).expanduser()
    report = _empty_report(repo)
    if not repo.exists() or not repo.is_dir():
        report["errors"] = ["repository path does not exist or is not a directory"]
        return report, 2
    try:
        allowed = sorted({normalize_authorized_path(repo, item) for item in allowed_args})
        required = sorted({normalize_authorized_path(repo, item) for item in required_args})
        if not allowed:
            raise ValueError("at least one --allowed-file is required")
        report["allowed_files"] = allowed
        report["required_files"] = required

        inside = _decode_ascii(require_success(
            run_read_only_git(repo, ["rev-parse", "--is-inside-work-tree"], runner),
            "repository inspection",
        ), "repository inspection").strip()
        if inside != "true":
            raise RuntimeError("supplied path is not a Git worktree")

        staged_raw = require_success(
            run_read_only_git(repo, ["diff", "--cached", "--name-status", "-z", "--find-renames"], runner),
            "staged scope inspection",
        )
        unstaged_raw = require_success(
            run_read_only_git(repo, ["diff", "--name-status", "-z", "--find-renames"], runner),
            "unstaged scope inspection",
        )
        untracked_raw = require_success(
            run_read_only_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"], runner),
            "untracked scope inspection",
        )
        staged, added_s, deleted_s, renamed_s = parse_name_status(staged_raw)
        unstaged, added_u, deleted_u, renamed_u = parse_name_status(unstaged_raw)
        untracked = parse_nul_paths(untracked_raw)

        cumulative: set[str] = set()
        added_c: set[str] = set()
        deleted_c: set[str] = set()
        renamed_c: list[dict[str, str]] = []
        if base is not None:
            selected_head = "HEAD" if head is None else head
            base_object = resolve_commit(repo, base, "base", runner)
            head_object = resolve_commit(repo, selected_head, "head", runner)
            cumulative_raw = require_success(
                run_read_only_git(
                    repo,
                    [
                        "diff",
                        "--name-status",
                        "-z",
                        "--find-renames",
                        base_object,
                        head_object,
                        "--",
                    ],
                    runner,
                ),
                "cumulative scope inspection",
            )
            cumulative, added_c, deleted_c, renamed_c = parse_name_status(cumulative_raw)
        elif head is not None:
            raise ValueError("--head requires --base")

        actual = staged | unstaged | untracked | cumulative
        added = added_s | added_u | added_c | untracked
        deleted = deleted_s | deleted_u | deleted_c
        rename_map = {
            (entry["old_path"], entry["new_path"]): entry
            for entry in [*renamed_s, *renamed_u, *renamed_c]
        }
        unexpected = sorted(actual - set(allowed))
        missing = sorted(set(required) - actual)
        report.update(
            {
                "actual_files": sorted(actual),
                "added_files": sorted(added),
                "cumulative_files": sorted(cumulative),
                "deleted_files": sorted(deleted),
                "missing_required_files": missing,
                "renamed_files": [rename_map[key] for key in sorted(rename_map)],
                "result": "PASS" if not unexpected and not missing else "FAIL",
                "staged_files": sorted(staged),
                "unexpected_files": unexpected,
                "unstaged_files": sorted(unstaged),
                "untracked_files": sorted(untracked),
            }
        )
        return report, 0 if report["result"] == "PASS" else 1
    except (OSError, RuntimeError, ValueError) as exc:
        report["errors"] = [str(exc)]
        return report, 2


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--allowed-file", action="append", default=[], required=True)
    parser.add_argument("--required-file", action="append", default=[])
    parser.add_argument("--base")
    parser.add_argument("--head")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run scope validation and return a documented exit status."""

    args = build_parser().parse_args(argv)
    report, status = validate_scope(
        args.repo,
        args.allowed_file,
        args.required_file,
        base=args.base,
        head=args.head,
    )
    emit_json(report)
    if status == 2:
        print("; ".join(report["errors"]), file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
