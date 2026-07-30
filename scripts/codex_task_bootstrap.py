"""Prepare governance prerequisites and inspect local Git state safely.

The ``prereq`` command uses filesystem operations only. The ``inspect``
command is deliberately separate and requires a caller assertion before it
may invoke a small allowlist of read-only Git commands.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Callable, Sequence


NEXT_GIT_COMMAND = "git status --short --branch"
IGNORED_AGENT_DIRS = {".git", ".pytest_cache", "node_modules", "__pycache__"}
READ_ONLY_GIT_COMMANDS = {
    ("branch", "--show-current"),
    ("diff", "--cached", "--name-only", "-z"),
    ("diff", "--name-only", "-z"),
    ("for-each-ref", "--format=%(refname:short)", "refs/remotes"),
    ("ls-files", "--others", "--exclude-standard", "-z"),
    ("rev-parse", "--is-inside-work-tree"),
    ("rev-parse", "--verify", "HEAD"),
    ("worktree", "list", "--porcelain", "-z"),
}
READ_ONLY_GIT_SUBCOMMANDS = {command[0] for command in READ_ONLY_GIT_COMMANDS}
HEX_OBJECT_LENGTHS = {40, 64}


def emit_json(payload: dict[str, object]) -> None:
    """Write deterministic JSON to stdout."""

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def normalize_path(path: Path) -> str:
    """Return a resolved path using forward slashes."""

    return path.resolve(strict=False).as_posix()


def default_skill_path(home: Path | None = None) -> Path:
    """Construct the default external Skill path without invoking Git."""

    selected_home = home or Path(os.environ.get("USERPROFILE") or Path.home())
    return selected_home / ".codex" / "skills" / "manage-network-lab-codex-tasks" / "SKILL.md"


def discover_agents_files(repo: Path) -> list[str]:
    """Discover applicable AGENTS.md files with filesystem traversal only."""

    found: set[str] = set()
    current = repo.resolve(strict=False)
    for directory in (current, *current.parents):
        candidate = directory / "AGENTS.md"
        if candidate.is_file():
            found.add(normalize_path(candidate))

    if repo.is_dir():
        for root, directories, files in os.walk(repo):
            directories[:] = sorted(d for d in directories if d not in IGNORED_AGENT_DIRS)
            if "AGENTS.md" in files:
                found.add(normalize_path(Path(root) / "AGENTS.md"))
    return sorted(found)


def build_prereq_report(repo_arg: str, skill_arg: str | None = None) -> tuple[dict[str, object], int]:
    """Build the non-Git prerequisite report and its documented exit status."""

    repo = Path(repo_arg).expanduser()
    skill = Path(skill_arg).expanduser() if skill_arg else default_skill_path()
    errors: list[str] = []
    if not repo.exists() or not repo.is_dir():
        errors.append("repository path does not exist or is not a directory")
    if not skill.exists() or not skill.is_file():
        errors.append("Skill path does not exist or is not a file")

    agents = discover_agents_files(repo) if repo.is_dir() else []
    report: dict[str, object] = {
        "agents_discovery_completed": repo.is_dir(),
        "agents_files": agents,
        "errors": sorted(errors),
        "existence_proves_semantic_reading": False,
        "first_git_history_proven": False,
        "next_required_command": NEXT_GIT_COMMAND,
        "repository_path": normalize_path(repo),
        "result": "PASS" if not errors else "ERROR",
        "semantic_reading_proven": False,
        "skill_path": normalize_path(skill),
        "skill_path_exists": skill.is_file(),
    }
    return report, 0 if not errors else 2


def _require_bytes(value: bytes | None, label: str) -> bytes:
    if value is None:
        raise ValueError(f"{label} produced missing output")
    if not isinstance(value, bytes):
        raise ValueError(f"{label} did not produce binary output")
    return value


def _decode_utf8(value: bytes, label: str) -> str:
    try:
        return value.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} was not valid UTF-8") from exc


def _decode_ascii(value: bytes, label: str) -> str:
    try:
        return value.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} was not ASCII") from exc


def _decode_diagnostic(value: bytes | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, bytes):
        return "invalid non-binary Git diagnostic"
    return value.decode("utf-8", errors="replace").strip()


def _parse_nul_paths(value: bytes | None) -> list[str]:
    raw = _require_bytes(value, "Git path output")
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        raise ValueError("malformed Git path output: missing NUL terminator")
    records = raw[:-1].split(b"\0")
    if any(record == b"" for record in records):
        raise ValueError("malformed Git path output: empty NUL record")
    return sorted(_decode_utf8(item, "Git path output").replace("\\", "/") for item in records)


def _parse_worktree_paths(value: bytes | None) -> list[str]:
    raw = _require_bytes(value, "Git worktree output")
    if not raw:
        return []
    if not raw.endswith(b"\0"):
        raise ValueError("malformed Git worktree output: missing NUL terminator")
    paths: list[str] = []
    for record in raw[:-1].split(b"\0"):
        if not record:
            continue
        decoded = _decode_utf8(record, "Git worktree output")
        if decoded.startswith("worktree "):
            paths.append(decoded.removeprefix("worktree ").replace("\\", "/"))
    return sorted(paths)


def _validate_git_args(args: Sequence[str]) -> tuple[str, ...]:
    command = tuple(args)
    if command not in READ_ONLY_GIT_COMMANDS:
        raise ValueError("Git argv is not an exact read-only command shape")
    return command


def run_read_only_git(
    repo: Path,
    args: Sequence[str],
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> subprocess.CompletedProcess[bytes]:
    """Run one allowlisted read-only local Git command."""

    command = _validate_git_args(args)
    argv = ["git", "-C", str(repo), *command]
    return runner(argv, capture_output=True, check=False, shell=False)


def _require_git_success(result: subprocess.CompletedProcess[bytes], label: str) -> bytes:
    if result.returncode != 0:
        detail = _decode_diagnostic(result.stderr) or _decode_diagnostic(result.stdout) or "unknown Git error"
        raise RuntimeError(f"{label} failed: {detail}")
    return _require_bytes(result.stdout, label)


def _require_hex_object_id(value: bytes, label: str) -> str:
    object_id = _decode_ascii(value, label).strip()
    if len(object_id) not in HEX_OBJECT_LENGTHS or any(
        character not in "0123456789abcdefABCDEF" for character in object_id
    ):
        raise ValueError(f"{label} was not a hexadecimal object ID")
    return object_id.lower()


def build_inspect_report(
    repo_arg: str,
    *,
    caller_confirms_gate: bool,
    include_worktrees: bool = False,
    include_local_tracking: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> tuple[dict[str, object], int]:
    """Inspect current local Git state after an explicit caller gate assertion."""

    repo = Path(repo_arg).expanduser()
    base: dict[str, object] = {
        "caller_confirms_first_git_gate": caller_confirms_gate is True,
        "errors": [],
        "first_git_history_independently_verified": False,
        "repository_path": normalize_path(repo),
        "result": "ERROR",
    }
    if caller_confirms_gate is not True:
        base["errors"] = ["caller confirmation of the first-Git gate is required"]
        return base, 2
    if not repo.exists() or not repo.is_dir():
        base["errors"] = ["repository path does not exist or is not a directory"]
        return base, 2

    try:
        inside = _decode_ascii(_require_git_success(
            run_read_only_git(repo, ["rev-parse", "--is-inside-work-tree"], runner),
            "repository inspection",
        ), "repository inspection").strip()
        if inside != "true":
            raise RuntimeError("supplied path is not a Git worktree")
        head = _require_hex_object_id(
            _require_git_success(
                run_read_only_git(repo, ["rev-parse", "--verify", "HEAD"], runner),
                "HEAD inspection",
            ),
            "HEAD inspection",
        )
        branch = _decode_utf8(
            _require_git_success(
                run_read_only_git(repo, ["branch", "--show-current"], runner),
                "branch inspection",
            ),
            "branch inspection",
        ).strip() or None
        staged = _parse_nul_paths(
            _require_git_success(
                run_read_only_git(repo, ["diff", "--cached", "--name-only", "-z"], runner),
                "staged-path inspection",
            )
        )
        unstaged = _parse_nul_paths(
            _require_git_success(
                run_read_only_git(repo, ["diff", "--name-only", "-z"], runner),
                "unstaged-path inspection",
            )
        )
        untracked = _parse_nul_paths(
            _require_git_success(
                run_read_only_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"], runner),
                "untracked-path inspection",
            )
        )
        base.update(
            {
                "branch": branch,
                "head": head,
                "independently_observed_current_git_state": True,
                "result": "PASS",
                "staged_paths": staged,
                "unstaged_paths": unstaged,
                "untracked_paths": untracked,
            }
        )
        if include_worktrees:
            output = _require_git_success(
                run_read_only_git(repo, ["worktree", "list", "--porcelain", "-z"], runner),
                "worktree inspection",
            )
            base["worktrees"] = _parse_worktree_paths(output)
        if include_local_tracking:
            output = _require_git_success(
                run_read_only_git(
                    repo,
                    ["for-each-ref", "--format=%(refname:short)", "refs/remotes"],
                    runner,
                ),
                "local tracking-ref inspection",
            )
            decoded = _decode_utf8(output, "local tracking-ref inspection")
            base["local_tracking_refs"] = sorted(line for line in decoded.splitlines() if line)
        return base, 0
    except (OSError, RuntimeError, ValueError) as exc:
        base["errors"] = [str(exc)]
        return base, 2


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prereq = subparsers.add_parser("prereq", help="prepare non-Git prerequisite evidence")
    prereq.add_argument("--repo", required=True)
    prereq.add_argument("--skill-path")
    inspect = subparsers.add_parser("inspect", help="inspect current read-only local Git state")
    inspect.add_argument("--repo", required=True)
    inspect.add_argument("--caller-confirms-first-git-gate", action="store_true")
    inspect.add_argument("--include-worktrees", action="store_true")
    inspect.add_argument("--include-local-tracking", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected command and return a documented exit status."""

    args = build_parser().parse_args(argv)
    if args.command == "prereq":
        report, status = build_prereq_report(args.repo, args.skill_path)
    else:
        report, status = build_inspect_report(
            args.repo,
            caller_confirms_gate=args.caller_confirms_first_git_gate,
            include_worktrees=args.include_worktrees,
            include_local_tracking=args.include_local_tracking,
        )
    emit_json(report)
    if status == 2:
        print("; ".join(report.get("errors", [])), file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
