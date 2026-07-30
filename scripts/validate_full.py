"""Plan or explicitly execute the complete local integration-validation set."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Callable, Sequence


REQUIRED_VALIDATION_IDS = [
    "lint",
    "nextjs_build",
    "python_full",
    "report_index",
    "typecheck",
    "typescript_unit_full",
]
NPM_SCRIPT_BY_ID = {
    "lint": "lint",
    "nextjs_build": "build",
    "typecheck": "typecheck",
    "typescript_unit_full": "test:unit",
}
SAFE_NPM_SCRIPT_BODIES = {
    "build": "next build",
    "lint": "eslint app components lib --no-cache --max-warnings=0",
    "test:unit": "vitest run",
    "typecheck": "tsc --noEmit --incremental false",
}


def emit_json(payload: dict[str, object]) -> None:
    """Write deterministic JSON to stdout."""

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def read_package_scripts(repo: Path) -> dict[str, str]:
    """Read package scripts without modifying package.json."""

    path = repo / "package.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
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
    """Accept only the fixed local validation command structures."""

    argv = command.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        return False
    executable = Path(argv[0]).name.lower()
    if executable in {"python", "python.exe", "py", "py.exe"}:
        if argv[1:3] == ["-m", "pytest"]:
            return len(argv) == 3
        return argv[1:] == ["network_lab.py", "--task", "report-index"]
    if executable in {"npm", "npm.cmd", "npm.exe"}:
        structurally_safe = (
            len(argv) == 3
            and argv[1] == "run"
            and argv[2] in SAFE_NPM_SCRIPT_BODIES
            and command.get("script_body") == SAFE_NPM_SCRIPT_BODIES[argv[2]]
        )
        if not structurally_safe:
            return False
        if repo is not None:
            try:
                return supported_script_body(read_package_scripts(repo), argv[2]) == command["script_body"]
            except (OSError, ValueError):
                return False
        return True
    return False


def resolve_full_plan(repo: Path) -> dict[str, object]:
    """Resolve the deterministic full validation plan from existing config."""

    scripts = read_package_scripts(repo)
    commands: list[dict[str, object]] = []
    unresolved: list[str] = []
    commands.append(_command("python_full", ["python", "-m", "pytest"]))
    for identifier in ("typescript_unit_full", "typecheck", "lint", "nextjs_build"):
        script = NPM_SCRIPT_BY_ID[identifier]
        script_body = supported_script_body(scripts, script)
        if script_body:
            commands.append(
                _command(identifier, ["npm", "run", script], script_body=script_body)
            )
        else:
            unresolved.append(identifier)
    if (repo / "network_lab.py").is_file():
        commands.append(_command("report_index", ["python", "network_lab.py", "--task", "report-index"]))
    else:
        unresolved.append("report_index")
    if any(not command_is_safe(command, repo) for command in commands):
        raise ValueError("resolved command failed the fixed safety allowlist")
    return {
        "command_results": [],
        "errors": [],
        "execution_requested": False,
        "isolated_paths": {
            "pytest_basetemp": "<system-temp>/codex-workflow-full-pytest",
            "temporary_root": "<system-temp>/codex-workflow-full",
        },
        "required_validation_ids": REQUIRED_VALIDATION_IDS,
        "resolved_commands": commands,
        "result": "PASS" if not unresolved else "WARN",
        "unresolved_commands": sorted(unresolved),
    }


def _unavailable_executables(commands: Sequence[dict[str, object]]) -> list[str]:
    unavailable: set[str] = set()
    for command in commands:
        executable = command["argv"][0]
        if shutil.which(executable) is None:
            unavailable.add(f"executable:{executable}")
    return sorted(unavailable)


def execute_full_plan(
    repo: Path,
    plan: dict[str, object],
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> tuple[dict[str, object], int]:
    """Execute the complete resolved plan sequentially, stopping on failure."""

    plan["execution_requested"] = True
    if any(not command_is_safe(command, repo) for command in plan["resolved_commands"]):
        plan["result"] = "ERROR"
        plan["errors"] = ["execution command failed the fixed safety allowlist"]
        plan["command_results"] = []
        return plan, 2
    unresolved = sorted({*plan["unresolved_commands"], *_unavailable_executables(plan["resolved_commands"])})
    plan["unresolved_commands"] = unresolved
    if unresolved:
        plan["result"] = "ERROR"
        plan["errors"] = ["execution refused because required commands are unresolved"]
        return plan, 2

    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="codex-workflow-full-") as temp_root:
        pytest_base = Path(temp_root) / "pytest"
        plan["isolated_paths"] = {
            "pytest_basetemp": pytest_base.as_posix(),
            "temporary_root": Path(temp_root).as_posix(),
        }
        environment = os.environ.copy()
        environment.update({"TEMP": temp_root, "TMP": temp_root, "TMPDIR": temp_root})
        for command in plan["resolved_commands"]:
            argv = list(command["argv"])
            if argv[1:3] == ["-m", "pytest"]:
                argv.extend(["--basetemp", str(pytest_base)])
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
            results.append(
                {
                    "argv": argv,
                    "duration_seconds": round(time.monotonic() - started, 6),
                    "exit_code": completed.returncode,
                    "validation_id": command["validation_id"],
                }
            )
            if completed.returncode != 0:
                plan["result"] = "FAIL"
                plan["command_results"] = results
                return plan, 1
    plan["result"] = "PASS"
    plan["command_results"] = results
    return plan, 0


def build_validation(repo_arg: str, *, execute: bool) -> tuple[dict[str, object], int]:
    """Build and optionally execute the full validation plan."""

    repo = Path(repo_arg).expanduser().resolve(strict=False)
    if not repo.exists() or not repo.is_dir():
        return {
            "command_results": [],
            "errors": ["repository path does not exist or is not a directory"],
            "execution_requested": execute,
            "isolated_paths": {},
            "required_validation_ids": REQUIRED_VALIDATION_IDS,
            "resolved_commands": [],
            "result": "ERROR",
            "unresolved_commands": REQUIRED_VALIDATION_IDS,
        }, 2
    try:
        plan = resolve_full_plan(repo)
        if execute:
            return execute_full_plan(repo, plan)
        return plan, 0
    except (OSError, ValueError) as exc:
        return {
            "command_results": [],
            "errors": [str(exc)],
            "execution_requested": execute,
            "isolated_paths": {},
            "required_validation_ids": REQUIRED_VALIDATION_IDS,
            "resolved_commands": [],
            "result": "ERROR",
            "unresolved_commands": REQUIRED_VALIDATION_IDS,
        }, 2


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run full validation planning or explicit execution."""

    args = build_parser().parse_args(argv)
    report, status = build_validation(args.repo, execute=args.execute)
    emit_json(report)
    if status == 2:
        print("; ".join(report["errors"]), file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
