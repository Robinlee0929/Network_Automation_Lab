"""Tests for bounded fast/phase validation planning and execution."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


SCRIPT = Path(__file__).parents[2] / "scripts" / "validate_fast.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_fast", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configured_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    package = {
        "scripts": {
            "lint": "eslint app components lib --no-cache --max-warnings=0",
            "test:unit": "vitest run",
            "typecheck": "tsc --noEmit --incremental false",
        }
    }
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_network_phase1_ui_presentation.py").write_text("def test_ui(): pass\n", encoding="utf-8")
    workflow_tests = tests / "workflow_governance"
    workflow_tests.mkdir()
    (workflow_tests / "test_example.py").write_text("def test_example(): pass\n", encoding="utf-8")
    return repo


@pytest.mark.parametrize(
    ("path", "category"),
    [
        ("docs/readme.md", "documentation_config"),
        ("config/inert.yaml", "documentation_config"),
        ("app/globals.css", "css_ui"),
        ("tests/test_logic.py", "python_tests"),
        ("tests/widget.test.ts", "typescript_react"),
        ("scripts/tool.py", "python_production"),
        ("components/view.tsx", "typescript_react"),
        ("package.json", "shared_runtime"),
        ("unknown.binary", "shared_runtime"),
    ],
)
def test_classification_is_safe(path: str, category: str) -> None:
    module = load_module()
    assert module.classify_path(path) == category


def test_css_plan_uses_bounded_ui_validation_not_full(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["app/globals.css"], "fast")
    assert plan["categories"] == ["css_ui"]
    assert plan["validation_ids"] == ["bounded_ui_pytest"]
    assert all("python_full" != item["validation_id"] for item in plan["commands"])


def test_python_test_and_typescript_test_never_map_to_documentation() -> None:
    module = load_module()
    assert module.classify_path("tests/test_exec.py") == "python_tests"
    assert module.classify_path("tests/exec.test.ts") == "typescript_react"


def test_python_production_resolves_matching_targeted_test(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    script = repo / "scripts"
    script.mkdir()
    (script / "example.py").write_text("x = 1\n", encoding="utf-8")
    plan = module.resolve_plan(repo, ["scripts/example.py"], "fast")
    assert plan["unresolved_commands"] == []
    assert plan["commands"][0]["argv"][-1] == "tests/workflow_governance/test_example.py"


def test_typescript_plan_uses_existing_scripts_only(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["components/view.tsx"], "fast")
    assert plan["unresolved_commands"] == []
    assert [item["validation_id"] for item in plan["commands"]] == ["relevant_vitest", "typecheck"]
    assert plan["commands"][0]["argv"] == [
        "npm",
        "run",
        "test:unit",
        "--",
        "--related",
        "components/view.tsx",
    ]


def test_shared_runtime_plan_broadens_safely(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["package.json"], "fast")
    assert plan["categories"] == ["shared_runtime"]
    assert plan["validation_ids"] == ["lint", "typecheck"]


def test_dry_run_is_default_and_does_not_execute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    monkeypatch.setattr(module, "execute_plan", lambda *args, **kwargs: pytest.fail("executed"))
    report, status = module.build_validation(
        str(repo), ["docs/readme.md"], profile="fast", execute=False
    )
    assert status == 0
    assert report["execution_requested"] is False
    assert "command_results" not in report


def test_unresolved_command_fails_closed_on_execution(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["scripts/missing_match.py"], "fast")
    report, status = module.execute_plan(repo, plan)
    assert status == 2
    assert report["result"] == "ERROR"
    assert report["command_results"] == []


def test_fixed_command_allowlist_rejects_install_and_arbitrary_commands() -> None:
    module = load_module()
    assert module.command_is_safe({"argv": ["npm", "install"], "validation_id": "bad"}) is False
    assert module.command_is_safe({"argv": ["git", "fetch"], "validation_id": "bad"}) is False
    assert module.command_is_safe({"argv": ["python", "tool.py"], "validation_id": "bad"}) is False


def test_execution_is_sequential_and_stops_after_first_failure(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        code = 1 if len(calls) == 2 else 0
        return subprocess.CompletedProcess(argv, code, stdout="", stderr="")

    plan = {
        "categories": ["shared_runtime"],
        "changed_files": ["package.json"],
        "commands": [
            {
                "argv": ["npm", "run", "typecheck"],
                "script_body": "tsc --noEmit --incremental false",
                "validation_id": "typecheck",
            },
            {
                "argv": ["npm", "run", "lint"],
                "script_body": "eslint app components lib --no-cache --max-warnings=0",
                "validation_id": "lint",
            },
            {
                "argv": ["npm", "run", "typecheck"],
                "script_body": "tsc --noEmit --incremental false",
                "validation_id": "later",
            },
        ],
        "errors": [],
        "execution_requested": False,
        "isolated_paths": {},
        "profile": "phase",
        "result": "PASS",
        "unresolved_commands": [],
        "validation_ids": ["lint", "typecheck"],
    }
    report, status = module.execute_plan(repo, plan, runner=runner)
    assert status == 1
    assert len(calls) == 2
    assert len(report["command_results"]) == 2
    assert "duration_seconds" in report["command_results"][0]


def test_execution_constructs_isolated_temporary_paths(tmp_path: Path) -> None:
    module = load_module()
    observed: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        observed.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    plan = {
        "categories": ["python_tests"],
        "changed_files": ["tests/test_x.py"],
        "commands": [
            {
                "argv": ["python", "-m", "pytest", "--", "tests/test_x.py"],
                "validation_id": "targeted_pytest",
            }
        ],
        "errors": [],
        "execution_requested": False,
        "isolated_paths": {},
        "profile": "fast",
        "result": "PASS",
        "unresolved_commands": [],
        "validation_ids": ["targeted_pytest"],
    }
    report, status = module.execute_plan(tmp_path, plan, runner=runner)
    assert status == 0
    assert "--basetemp" in observed[0]
    assert "<system-temp>" not in report["isolated_paths"]["temporary_root"]


def test_discovery_constructs_only_read_only_git_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_module()
    calls: list[list[str]] = []

    def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout=b"docs/a.md\0", stderr=b"")

    monkeypatch.setattr(module.subprocess, "run", runner)
    assert module.discover_changed_files(tmp_path) == ["docs/a.md"]
    assert {argv[3] for argv in calls} == {"diff", "ls-files"}
    assert all("fetch" not in argv and "push" not in argv for argv in calls)


def test_resolved_commands_contain_no_install_or_remote_operation(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["components/view.tsx", "package.json"], "phase")
    for command in plan["commands"]:
        argv = command["argv"]
        assert module.command_is_safe(command)
        assert argv[:2] not in (["npm", "install"], ["git", "fetch"], ["git", "push"])


@pytest.mark.parametrize(
    "body",
    [
        "npm install",
        "pip install danger",
        "git push origin main",
        "npx vitest run",
        "vitest run && npm install",
        "vitest run || npm install",
        "vitest run | tee result.txt",
        "vitest run > result.txt",
        "vitest run $(danger)",
        "vitest run arbitrary-helper",
    ],
)
def test_unsafe_package_script_body_is_unresolved_and_executes_nothing(
    tmp_path: Path, body: str
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    package = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    package["scripts"]["test:unit"] = body
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    plan = module.resolve_plan(repo, ["components/view.tsx"], "fast")
    assert "relevant_vitest" in plan["unresolved_commands"]
    assert all(command["validation_id"] != "relevant_vitest" for command in plan["commands"])
    calls: list[list[str]] = []
    report, status = module.execute_plan(
        repo, plan, runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert report["command_results"] == []
    assert calls == []


@pytest.mark.parametrize(
    "path",
    [
        "-danger.tsx",
        "--config=C:/outside/evil.tsx",
        "C:/outside/evil.tsx",
        "\\\\server\\share\\evil.tsx",
        "../outside.tsx",
        "dir\\..\\..\\outside.tsx",
    ],
)
def test_option_external_and_traversal_changed_paths_are_rejected(
    tmp_path: Path, path: str
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    report, status = module.build_validation(
        str(repo), [path], profile="fast", execute=False
    )
    assert status == 2
    assert report["result"] == "ERROR"
    assert report["commands"] == []


@pytest.mark.parametrize(
    "path",
    [
        "@payload_test.py",
        "@arguments.txt",
        ".\\@payload_test.py",
        "./@payload_test.py",
        ".\\.\\@payload_test.py",
    ],
)
def test_response_file_paths_are_rejected_before_planning(tmp_path: Path, path: str) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)

    with pytest.raises(ValueError, match="response-file syntax"):
        module.normalize_changed_path(repo, path)
    with pytest.raises(ValueError, match="response-file syntax"):
        module.resolve_plan(repo, [path], "fast")

    report, status = module.build_validation(str(repo), [path], profile="fast", execute=False)
    assert status == 2
    assert report["result"] == "ERROR"
    assert report["commands"] == []
    assert "command_results" not in report
    assert path in report["errors"][0]


def test_response_file_rejection_prevents_execute_and_runner_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    marker = tmp_path / "external-marker"
    calls: list[str] = []

    def unexpected_call(*_: object, **__: object) -> None:
        calls.append("called")
        pytest.fail("response-file path reached an execution boundary")

    monkeypatch.setattr(module, "execute_plan", unexpected_call)
    monkeypatch.setattr(module.subprocess, "run", unexpected_call)
    report, status = module.build_validation(
        str(repo), ["@payload_test.py", "tests/test_safe.py"], profile="fast", execute=True
    )

    assert status == 2
    assert report["result"] == "ERROR"
    assert report["commands"] == []
    assert "command_results" not in report
    assert report["execution_requested"] is True
    assert calls == []
    assert not marker.exists()


def test_cli_plan_rejects_response_file_path_with_deterministic_json(tmp_path: Path) -> None:
    repo = configured_repo(tmp_path)
    command = [
        sys.executable,
        "-B",
        str(SCRIPT),
        "--repo",
        str(repo),
        "--changed-file",
        "@arguments.txt",
    ]

    first = subprocess.run(command, capture_output=True, text=True, check=False, shell=False)
    second = subprocess.run(command, capture_output=True, text=True, check=False, shell=False)
    report = json.loads(first.stdout)

    assert first.returncode == 2
    assert second.returncode == 2
    assert first.stdout == second.stdout
    assert report["result"] == "ERROR"
    assert report["commands"] == []
    assert report["execution_requested"] is False
    assert "response-file syntax" in report["errors"][0]


def test_cli_execute_rejects_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    marker = tmp_path / "external-marker"
    calls: list[str] = []

    def unexpected_execute(*_: object, **__: object) -> None:
        calls.append("called")
        pytest.fail("CLI execute reached the command runner")

    monkeypatch.setattr(module, "execute_plan", unexpected_execute)
    status = module.main(
        [
            "--repo",
            str(repo),
            "--changed-file",
            "@payload_test.py",
            "--execute",
        ]
    )
    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert status == 2
    assert report["result"] == "ERROR"
    assert report["commands"] == []
    assert report["execution_requested"] is True
    assert calls == []
    assert not marker.exists()


def test_valid_spaces_unicode_and_deleted_paths_have_exact_safe_argv(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    paths = [
        "components/space name.tsx",
        "components/café.tsx",
        "components/網路元件.tsx",
        "components/deleted.tsx",
    ]
    plan = module.resolve_plan(repo, paths, "fast")
    command = next(item for item in plan["commands"] if item["validation_id"] == "relevant_vitest")
    assert command["argv"] == ["npm", "run", "test:unit", "--", "--related", *sorted(paths)]
    assert module.command_is_safe(command, repo)


def test_python_target_uses_option_terminator_and_safe_relative_path(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    target = repo / "tests" / "test space 網路.py"
    target.write_text("def test_ok(): pass\n", encoding="utf-8")
    plan = module.resolve_plan(repo, ["tests/test space 網路.py"], "fast")
    assert plan["commands"][0]["argv"] == [
        "python",
        "-m",
        "pytest",
        "--",
        "tests/test space 網路.py",
    ]


def test_symlink_escape_changed_path_is_rejected_when_supported(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = repo / "components"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink or junction creation is unavailable")
    report, status = module.build_validation(
        str(repo), ["components/escape.tsx"], profile="fast", execute=False
    )
    assert status == 2
    assert "escapes repository" in report["errors"][0]


def test_malformed_git_byte_output_is_structured_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda argv, **kwargs: subprocess.CompletedProcess(
            argv, 0, stdout=b"bad-\xff.tsx\0", stderr=b""
        ),
    )
    report, status = module.build_validation(str(repo), [], profile="fast", execute=False)
    assert status == 2
    assert report["result"] == "ERROR"
    json.dumps(report, ensure_ascii=False)


def test_package_body_changed_after_planning_prevents_every_command(tmp_path: Path) -> None:
    module = load_module()
    repo = configured_repo(tmp_path)
    plan = module.resolve_plan(repo, ["components/view.tsx"], "fast")
    package = json.loads((repo / "package.json").read_text(encoding="utf-8"))
    package["scripts"]["test:unit"] = "git push origin main"
    (repo / "package.json").write_text(json.dumps(package), encoding="utf-8")
    calls: list[list[str]] = []
    report, status = module.execute_plan(
        repo, plan, runner=lambda argv, **kwargs: calls.append(argv)
    )
    assert status == 2
    assert report["command_results"] == []
    assert calls == []
