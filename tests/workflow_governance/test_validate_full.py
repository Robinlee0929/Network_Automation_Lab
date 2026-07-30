"""Tests for complete local validation planning and controlled execution."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[2] / "scripts" / "validate_full.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_full", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configured_repo(tmp_path: Path, *, omit_script: str | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    scripts = {
        "build": "next build",
        "lint": "eslint app components lib --no-cache --max-warnings=0",
        "test:unit": "vitest run",
        "typecheck": "tsc --noEmit --incremental false",
    }
    if omit_script:
        scripts.pop(omit_script)
    (repo / "package.json").write_text(json.dumps({"scripts": scripts}), encoding="utf-8")
    (repo / "network_lab.py").write_text("print('report')\n", encoding="utf-8")
    return repo


def test_deterministic_full_plan_contains_all_required_ids(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    first = module.resolve_full_plan(repo)
    second = module.resolve_full_plan(repo)
    assert first == second
    assert first["required_validation_ids"] == [
        "lint",
        "nextjs_build",
        "python_full",
        "report_index",
        "typecheck",
        "typescript_unit_full",
    ]
    assert first["unresolved_commands"] == []


def test_plan_mode_is_default_and_executes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    monkeypatch.setattr(module, "execute_full_plan", lambda *args, **kwargs: pytest.fail("executed"))
    report, status = module.build_validation(str(repo), execute=False)
    assert status == 0
    assert report["execution_requested"] is False
    assert report["command_results"] == []


def test_missing_required_package_script_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path, omit_script="lint")
    plan = module.resolve_full_plan(repo)
    report, status = module.execute_full_plan(repo, plan)
    assert status == 2
    assert report["result"] == "ERROR"
    assert "lint" in report["unresolved_commands"]
    assert report["command_results"] == []


def test_missing_report_runner_is_unresolved(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    (repo / "network_lab.py").unlink()
    plan = module.resolve_full_plan(repo)
    assert "report_index" in plan["unresolved_commands"]
    assert all(item["validation_id"] != "report_index" for item in plan["resolved_commands"])


def test_resolved_commands_execute_sequentially(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    calls: list[list[str]] = []
    monkeypatch.setattr(module.shutil, "which", lambda executable: f"/bin/{executable}")

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    report, status = module.execute_full_plan(repo, plan, runner=runner)
    assert status == 0
    assert [item["validation_id"] for item in report["command_results"]] == [
        item["validation_id"] for item in plan["resolved_commands"]
    ]
    assert len(calls) == 6


def test_first_failure_stops_later_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    calls: list[list[str]] = []
    monkeypatch.setattr(module.shutil, "which", lambda executable: f"/bin/{executable}")

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        code = 1 if len(calls) == 2 else 0
        return subprocess.CompletedProcess(argv, code, stdout="", stderr="")

    report, status = module.execute_full_plan(repo, plan, runner=runner)
    assert status == 1
    assert len(calls) == 2
    assert report["command_results"][-1]["exit_code"] == 1


def test_command_results_include_duration_and_isolated_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    monkeypatch.setattr(module.shutil, "which", lambda executable: f"/bin/{executable}")

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    report, status = module.execute_full_plan(repo, plan, runner=runner)
    assert status == 0
    assert all("duration_seconds" in item for item in report["command_results"])
    assert "<system-temp>" not in report["isolated_paths"]["temporary_root"]
    assert "--basetemp" in report["command_results"][0]["argv"]


@pytest.mark.parametrize(
    "argv",
    [
        ["npm", "install"],
        ["git", "fetch"],
        ["git", "push"],
        ["python", "-m", "pip", "install", "x"],
        ["npm", "run", "unknown"],
    ],
)
def test_command_allowlist_rejects_install_remote_and_unknown(argv: list[str]) -> None:
    module = load_module()
    assert module.command_is_safe({"argv": argv, "validation_id": "bad"}) is False


def test_all_resolved_commands_are_fixed_and_local(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    assert all(module.command_is_safe(command) for command in plan["resolved_commands"])
    assert all(command["argv"][0] in {"python", "npm"} for command in plan["resolved_commands"])


def test_package_file_is_not_modified(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    package = repo / "package.json"
    before = package.read_bytes()
    module.resolve_full_plan(repo)
    assert package.read_bytes() == before


def test_missing_script_is_not_invented(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path, omit_script="typecheck")
    plan = module.resolve_full_plan(repo)
    assert "typecheck" in plan["unresolved_commands"]
    assert all(command["argv"] != ["npm", "run", "typecheck"] for command in plan["resolved_commands"])


def test_missing_executable_fails_before_any_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    calls: list[list[str]] = []
    monkeypatch.setattr(module.shutil, "which", lambda executable: None if executable == "npm" else executable)
    report, status = module.execute_full_plan(
        repo,
        plan,
        runner=lambda argv, **kwargs: calls.append(argv),
    )
    assert status == 2
    assert calls == []
    assert "executable:npm" in report["unresolved_commands"]


@pytest.mark.parametrize(
    "body",
    [
        "npm install",
        "npm ci",
        "pnpm install",
        "yarn install",
        "pip install danger",
        "git push origin main",
        "npx vitest run",
        "vitest run && npm install",
        "vitest run || npm install",
        "vitest run | tee output.txt",
        "vitest run > output.txt",
        "vitest run $(danger)",
        "vitest run unsupported-helper",
    ],
)
def test_unsafe_package_body_is_unresolved_and_prevents_all_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    package = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    package["scripts"]["test:unit"] = body
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    plan = module.resolve_full_plan(repo)
    assert "typescript_unit_full" in plan["unresolved_commands"]
    assert all(
        command["validation_id"] != "typescript_unit_full"
        for command in plan["resolved_commands"]
    )
    calls: list[list[str]] = []
    monkeypatch.setattr(module.shutil, "which", lambda executable: executable)
    report, status = module.execute_full_plan(
        repo, plan, runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert calls == []
    assert report["command_results"] == []


def test_exact_normalized_safe_package_bodies_are_accepted(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    package = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    package["scripts"]["test:unit"] = "  vitest   run  "
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    plan = module.resolve_full_plan(repo)
    command = next(
        item for item in plan["resolved_commands"] if item["validation_id"] == "typescript_unit_full"
    )
    assert command["script_body"] == "vitest run"
    assert module.command_is_safe(command)


def test_package_body_changed_after_planning_prevents_every_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_full_plan(repo)
    package = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    package["scripts"]["lint"] = "git push origin main"
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(module.shutil, "which", lambda executable: executable)
    report, status = module.execute_full_plan(
        repo, plan, runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert report["command_results"] == []
    assert calls == []
