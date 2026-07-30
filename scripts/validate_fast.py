"""Plan or execute bounded fast/phase repository validation safely."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
import tempfile
import time
from typing import Callable, Sequence


CATEGORIES = {
    "css_ui",
    "documentation_config",
    "python_production",
    "python_tests",
    "shared_runtime",
    "typescript_react",
}
SAFE_NPM_SCRIPT_BODIES = {
    "lint": "eslint app components lib --no-cache --max-warnings=0",
    "test:unit": "vitest run",
    "typecheck": "tsc --noEmit --incremental false",
}
SHARED_RUNTIME_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "requirements.txt",
    "tsconfig.json",
    "vitest.config.js",
    "vitest.config.mjs",
    "vitest.config.ts",
}
DOC_CONFIG_SUFFIXES = {".json", ".md", ".rst", ".txt", ".yaml", ".yml"}
CSS_SUFFIXES = {".css", ".less", ".sass", ".scss"}
TS_SUFFIXES = {".js", ".jsx", ".ts", ".tsx"}


def emit_json(payload: dict[str, object]) -> None:
    """Write deterministic JSON to stdout."""

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def _reject_response_file_path(path: PurePosixPath, raw: str) -> None:
    """Reject paths that a downstream tool could expand as response files."""

    if path.as_posix().startswith("@"):
        raise ValueError(f"changed path uses response-file syntax: {raw}")


def _lexical_changed_path(raw: str) -> PurePosixPath:
    if not isinstance(raw, str) or not raw:
        raise ValueError("changed path must be a non-empty string")
    if any(ord(character) < 32 or ord(character) == 127 for character in raw):
        raise ValueError(f"changed path contains a control character: {raw!r}")
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
        raise ValueError(f"changed path is not repository-relative: {raw}")
    _reject_response_file_path(path, raw)
    return path


def normalize_changed_path(repo: Path, raw: str) -> str:
    """Validate and normalize one changed path within the supplied repository."""

    path = _lexical_changed_path(raw)
    resolved_repo = repo.resolve(strict=False)
    candidate = repo.joinpath(*path.parts)
    resolved_candidate = candidate.resolve(strict=False)
    try:
        relative = resolved_candidate.relative_to(resolved_repo)
    except ValueError as exc:
        raise ValueError(f"changed path escapes repository: {raw}") from exc
    normalized_path = PurePosixPath(relative.as_posix())
    _reject_response_file_path(normalized_path, raw)
    normalized = normalized_path.as_posix()
    if normalized in {"", "."}:
        raise ValueError(f"changed path must identify a file: {raw}")
    return normalized


def classify_path(path: str) -> str:
    """Classify a changed path, failing closed to shared runtime."""

    pure = _lexical_changed_path(path)
    suffix = pure.suffix.lower()
    name = pure.name.lower()
    parts = tuple(part.lower() for part in pure.parts)
    if name in SHARED_RUNTIME_NAMES or name.endswith("lock.json") or name.endswith("lock.yaml"):
        return "shared_runtime"
    if suffix in CSS_SUFFIXES:
        return "css_ui"
    if suffix == ".py":
        if "tests" in parts or name.startswith("test_") or name.endswith("_test.py"):
            return "python_tests"
        return "python_production"
    if suffix in TS_SUFFIXES:
        return "typescript_react"
    if suffix in DOC_CONFIG_SUFFIXES or "docs" in parts:
        return "documentation_config"
    return "shared_runtime"


def _decode_diagnostic(value: bytes | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, bytes):
        return "invalid non-binary Git diagnostic"
    return value.decode("utf-8", errors="replace").strip()


def _git_paths(repo: Path, args: Sequence[str]) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        detail = _decode_diagnostic(result.stderr) or "unknown Git error"
        raise RuntimeError(f"read-only scope discovery failed: {detail}")
    if result.stdout is None or not isinstance(result.stdout, bytes):
        raise ValueError("read-only scope discovery produced missing binary output")
    if not result.stdout:
        return set()
    if not result.stdout.endswith(b"\0"):
        raise ValueError("malformed Git path output: missing NUL terminator")
    records = result.stdout[:-1].split(b"\0")
    if any(record == b"" for record in records):
        raise ValueError("malformed Git path output: empty NUL record")
    paths: set[str] = set()
    for record in records:
        try:
            decoded = record.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("Git path output was not valid UTF-8") from exc
        paths.add(normalize_changed_path(repo, decoded))
    return paths


def discover_changed_files(repo: Path) -> list[str]:
    """Discover staged, unstaged, and untracked paths through read-only Git."""

    staged = _git_paths(repo, ["diff", "--cached", "--name-only", "-z"])
    unstaged = _git_paths(repo, ["diff", "--name-only", "-z"])
    untracked = _git_paths(repo, ["ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(staged | unstaged | untracked)


def read_package_scripts(repo: Path) -> dict[str, str]:
    """Read existing package scripts without changing package files."""

    package_path = repo / "package.json"
    if not package_path.is_file():
        return {}
    try:
        payload = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read package.json: {exc}") from exc
    scripts = payload.get("scripts", {})
    if not isinstance(scripts, dict):
        raise ValueError("package.json scripts must be an object")
    return {str(key): str(value) for key, value in scripts.items()}


def _normalized_script_body(value: str) -> str:
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError("package script body contains a control character")
    return " ".join(value.split())


def supported_script_body(scripts: dict[str, str], name: str) -> str | None:
    body = scripts.get(name)
    if not isinstance(body, str):
        return None
    try:
        normalized = _normalized_script_body(body)
    except ValueError:
        return None
    return normalized if normalized == SAFE_NPM_SCRIPT_BODIES.get(name) else None


def _python_test_targets(repo: Path, changed: Sequence[str]) -> list[str]:
    targets: set[str] = set()
    for path in changed:
        if classify_path(path) == "python_tests":
            targets.add(path)
        elif classify_path(path) == "python_production":
            source = PurePosixPath(path)
            candidates = [
                PurePosixPath("tests") / f"test_{source.stem}.py",
                PurePosixPath("tests/workflow_governance") / f"test_{source.stem}.py",
            ]
            for candidate in candidates:
                if (repo / Path(candidate.as_posix())).is_file():
                    targets.add(candidate.as_posix())
    return sorted(targets)


def _command(
    identifier: str,
    argv: Sequence[str],
    *,
    script_body: str | None = None,
) -> dict[str, object]:
    command: dict[str, object] = {"argv": list(argv), "validation_id": identifier}
    if script_body is not None:
        command["script_body"] = script_body
    return command


def command_is_safe(command: dict[str, object], repo: Path | None = None) -> bool:
    """Validate command structure, not arbitrary path substrings."""

    argv = command.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        return False
    executable = Path(argv[0]).name.lower()
    if executable in {"python", "python.exe", "py", "py.exe"}:
        if len(argv) < 5 or argv[1:4] != ["-m", "pytest", "--"]:
            return False
        try:
            for item in argv[4:]:
                if repo is None:
                    _lexical_changed_path(item)
                else:
                    normalize_changed_path(repo, item)
        except ValueError:
            return False
        return True
    if executable in {"npm", "npm.cmd", "npm.exe"}:
        if len(argv) < 3 or argv[1] != "run" or argv[2] not in SAFE_NPM_SCRIPT_BODIES:
            return False
        if command.get("script_body") != SAFE_NPM_SCRIPT_BODIES[argv[2]]:
            return False
        if repo is not None:
            try:
                if supported_script_body(read_package_scripts(repo), argv[2]) != command["script_body"]:
                    return False
            except (OSError, ValueError):
                return False
        if argv[2] != "test:unit":
            return len(argv) == 3
        if len(argv) < 6 or argv[3:5] != ["--", "--related"]:
            return False
        try:
            for item in argv[5:]:
                if repo is None:
                    _lexical_changed_path(item)
                else:
                    normalize_changed_path(repo, item)
        except ValueError:
            return False
        return True
    return False


def resolve_plan(repo: Path, changed_files: Sequence[str], profile: str) -> dict[str, object]:
    """Resolve a deterministic bounded validation plan from repository config."""

    changed = sorted({normalize_changed_path(repo, item) for item in changed_files})
    categories = sorted({classify_path(item) for item in changed})
    package_scripts = read_package_scripts(repo)
    commands: list[dict[str, object]] = []
    unresolved: set[str] = set()
    validation_ids: set[str] = set()

    if "documentation_config" in categories:
        validation_ids.add("documentation_scope_review")
    if {"python_tests", "python_production"} & set(categories):
        validation_ids.add("targeted_pytest")
        targets = _python_test_targets(repo, changed)
        if targets:
            commands.append(_command("targeted_pytest", ["python", "-m", "pytest", "--", *targets]))
        else:
            unresolved.add("targeted_pytest")
    if "css_ui" in categories:
        validation_ids.add("bounded_ui_pytest")
        ui_test = "tests/test_network_phase1_ui_presentation.py"
        if (repo / ui_test).is_file():
            commands.append(_command("bounded_ui_pytest", ["python", "-m", "pytest", "--", ui_test]))
        else:
            unresolved.add("bounded_ui_pytest")
    if "typescript_react" in categories:
        validation_ids.update({"relevant_vitest", "typecheck"})
        ts_files = [item for item in changed if PurePosixPath(item).suffix.lower() in TS_SUFFIXES]
        unit_body = supported_script_body(package_scripts, "test:unit")
        if unit_body:
            commands.append(
                _command(
                    "relevant_vitest",
                    ["npm", "run", "test:unit", "--", "--related", *ts_files],
                    script_body=unit_body,
                )
            )
        else:
            unresolved.add("relevant_vitest")
        typecheck_body = supported_script_body(package_scripts, "typecheck")
        if typecheck_body:
            commands.append(
                _command("typecheck", ["npm", "run", "typecheck"], script_body=typecheck_body)
            )
        else:
            unresolved.add("typecheck")
    if "shared_runtime" in categories:
        validation_ids.update({"lint", "typecheck"})
        for identifier in ("typecheck", "lint"):
            script_body = supported_script_body(package_scripts, identifier)
            if script_body:
                commands.append(
                    _command(identifier, ["npm", "run", identifier], script_body=script_body)
                )
            else:
                unresolved.add(identifier)
    if profile == "phase" and {"css_ui", "typescript_react"} & set(categories):
        validation_ids.add("lint")
        lint_body = supported_script_body(package_scripts, "lint")
        if lint_body:
            commands.append(_command("lint", ["npm", "run", "lint"], script_body=lint_body))
        else:
            unresolved.add("lint")

    deduplicated: list[dict[str, object]] = []
    seen: set[tuple[str, ...]] = set()
    for item in commands:
        key = tuple(item["argv"])
        if key not in seen:
            seen.add(key)
            deduplicated.append(item)
    if any(not command_is_safe(item, repo) for item in deduplicated):
        raise ValueError("resolved command failed the fixed safety allowlist")
    return {
        "categories": categories,
        "changed_files": changed,
        "commands": deduplicated,
        "errors": [],
        "execution_requested": False,
        "isolated_paths": {
            "pytest_basetemp": "<system-temp>/codex-workflow-pytest",
            "temporary_root": "<system-temp>/codex-workflow-fast",
        },
        "profile": profile,
        "result": "PASS" if not unresolved else "WARN",
        "unresolved_commands": sorted(unresolved),
        "validation_ids": sorted(validation_ids),
    }


def execute_plan(
    repo: Path,
    plan: dict[str, object],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[dict[str, object], int]:
    """Execute allowlisted commands sequentially and stop at first failure."""

    plan["execution_requested"] = True
    if plan["unresolved_commands"]:
        plan["result"] = "ERROR"
        plan["errors"] = ["execution refused because required commands are unresolved"]
        plan["command_results"] = []
        return plan, 2
    if any(not command_is_safe(command, repo) for command in plan["commands"]):
        plan["result"] = "ERROR"
        plan["errors"] = ["execution command failed the fixed safety allowlist"]
        plan["command_results"] = []
        return plan, 2

    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="codex-workflow-fast-") as temp_root:
        pytest_base = Path(temp_root) / "pytest"
        plan["isolated_paths"] = {
            "pytest_basetemp": pytest_base.as_posix(),
            "temporary_root": Path(temp_root).as_posix(),
        }
        environment = os.environ.copy()
        environment.update({"TEMP": temp_root, "TMP": temp_root, "TMPDIR": temp_root})
        for command in plan["commands"]:
            argv = list(command["argv"])
            if argv[1:3] == ["-m", "pytest"]:
                separator = argv.index("--")
                argv[separator:separator] = ["--basetemp", str(pytest_base)]
            started = time.monotonic()
            try:
                completed = runner(
                    argv,
                    cwd=repo,
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=False,
                    env=environment,
                )
            except OSError as exc:
                plan["result"] = "ERROR"
                plan["errors"] = [f"command execution failed: {exc}"]
                plan["command_results"] = results
                return plan, 2
            result = {
                "argv": argv,
                "duration_seconds": round(time.monotonic() - started, 6),
                "exit_code": completed.returncode,
                "validation_id": command["validation_id"],
            }
            results.append(result)
            if completed.returncode != 0:
                plan["result"] = "FAIL"
                plan["command_results"] = results
                return plan, 1
    plan["result"] = "PASS"
    plan["command_results"] = results
    return plan, 0


def build_validation(
    repo_arg: str,
    changed_args: Sequence[str],
    *,
    profile: str,
    execute: bool,
) -> tuple[dict[str, object], int]:
    """Build and optionally execute a fast/phase validation plan."""

    repo = Path(repo_arg).expanduser().resolve(strict=False)
    if not repo.exists() or not repo.is_dir():
        return {
            "categories": [],
            "changed_files": [],
            "commands": [],
            "errors": ["repository path does not exist or is not a directory"],
            "execution_requested": execute,
            "isolated_paths": {},
            "profile": profile,
            "result": "ERROR",
            "unresolved_commands": [],
            "validation_ids": [],
        }, 2
    try:
        changed = sorted({normalize_changed_path(repo, item) for item in changed_args})
        if not changed:
            changed = discover_changed_files(repo)
        plan = resolve_plan(repo, changed, profile)
        if execute:
            return execute_plan(repo, plan)
        return plan, 0
    except (OSError, RuntimeError, ValueError) as exc:
        return {
            "categories": [],
            "changed_files": [],
            "commands": [],
            "errors": [str(exc)],
            "execution_requested": execute,
            "isolated_paths": {},
            "profile": profile,
            "result": "ERROR",
            "unresolved_commands": [],
            "validation_ids": [],
        }, 2


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--profile", choices=("fast", "phase"), default="fast")
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run validation planning or explicitly requested execution."""

    args = build_parser().parse_args(argv)
    report, status = build_validation(
        args.repo,
        args.changed_file,
        profile=args.profile,
        execute=args.execute,
    )
    emit_json(report)
    if status == 2:
        print("; ".join(report["errors"]), file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
