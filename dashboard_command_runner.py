import json
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class CommandSpec:
    command_id: str
    label: str
    description: str
    category: str
    effect: str
    argv: List[str]
    working_directory: str
    timeout_seconds: int
    enabled: bool
    available: bool
    unavailable_reason: Optional[str] = None


class CommandUnavailableError(ValueError):
    pass


def _repo_path_exists(project_root: Path, relative_path: str) -> bool:
    return (project_root / relative_path).exists()


def build_command_registry(
    project_root: Path,
    python_executable: Optional[str] = None,
) -> Dict[str, CommandSpec]:
    project_root = Path(project_root).resolve()
    python_bin = python_executable or sys.executable
    candidates = [
        {
            "command_id": "pytest_all",
            "label": "Run all pytest tests",
            "description": "Run the full repository pytest suite.",
            "category": "Test / validation",
            "effect": "Validates the Python test suite only. Does not generate live device reports.",
            "argv": [python_bin, "-m", "pytest"],
            "timeout_seconds": 300,
            "required_path": "tests",
            "enabled_when_available": True,
        },
        {
            "command_id": "pytest_tests_dir",
            "label": "Run tests directory",
            "description": "Run pytest against the tests/ folder.",
            "category": "Test / validation",
            "effect": "Validates repository tests only. Does not connect to routers or switches.",
            "argv": [python_bin, "-m", "pytest", "tests"],
            "timeout_seconds": 300,
            "required_path": "tests",
            "enabled_when_available": True,
        },
        {
            "command_id": "pytest_performance_regression",
            "label": "Run performance regression tests",
            "description": "Run only the Day9 pytest file. This validates code behavior; it is not a live router performance test.",
            "category": "Test / validation",
            "effect": "Runs unit tests for Day9 code. Does not update day9_performance_regression_report.*.",
            "argv": [python_bin, "-m", "pytest", "tests/test_performance_regression.py"],
            "timeout_seconds": 180,
            "required_path": "tests/test_performance_regression.py",
            "enabled_when_available": True,
        },
        {
            "command_id": "performance_regression",
            "label": "Day9 performance regression script",
            "description": "Requires lab IP parameters and iperf3 readiness. Run manually with explicit arguments.",
            "category": "Manual lab workflow",
            "effect": "Would update Day9 performance reports only when run manually with full lab arguments.",
            "argv": [python_bin, "performance_regression.py"],
            "timeout_seconds": 300,
            "required_path": "performance_regression.py",
            "enabled_when_available": False,
            "disabled_reason": "Disabled in the dashboard because the script needs lab parameters.",
        },
        {
            "command_id": "topology_summary",
            "label": "Rebuild Day6 topology summary",
            "description": "Read existing report JSON files and rebuild the Day6 lab topology summary.",
            "category": "Report / local workflow",
            "effect": "Updates reports/day6_lab_topology_summary.json and .html. Does not rerun Day8 or Day9 performance tests.",
            "argv": [python_bin, "topology_summary.py"],
            "timeout_seconds": 180,
            "required_path": "topology_summary.py",
            "enabled_when_available": True,
        },
    ]

    registry: Dict[str, CommandSpec] = {}
    for candidate in candidates:
        available = _repo_path_exists(project_root, candidate["required_path"])
        enabled = bool(available and candidate["enabled_when_available"])
        registry[candidate["command_id"]] = CommandSpec(
            command_id=candidate["command_id"],
            label=candidate["label"],
            description=candidate["description"],
            category=candidate["category"],
            effect=candidate["effect"],
            argv=candidate["argv"],
            working_directory=str(project_root),
            timeout_seconds=candidate["timeout_seconds"],
            enabled=enabled,
            available=available,
            unavailable_reason=None
            if enabled
            else candidate.get("disabled_reason")
            if available
            else f"Missing {candidate['required_path']}",
        )
    return registry


def get_command_or_raise(
    registry: Dict[str, CommandSpec],
    command_id: str,
) -> CommandSpec:
    if command_id not in registry:
        raise KeyError(f"Unknown command id: {command_id}")
    command = registry[command_id]
    if not command.enabled or not command.available:
        raise CommandUnavailableError(
            command.unavailable_reason or f"Command is unavailable: {command_id}"
        )
    return command


def _local_timestamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _write_log(logs_dir: Path, payload: Dict[str, Any]) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{payload['log_id']}.json"
    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return log_path


def execute_command(
    command: CommandSpec,
    logs_dir: Path,
) -> Dict[str, Any]:
    started_at = _local_timestamp()
    started = datetime.now()
    log_id = f"{started.strftime('%Y%m%d_%H%M%S')}_{command.command_id}_{uuid.uuid4().hex[:8]}"

    payload: Dict[str, Any] = {
        "log_id": log_id,
        "command_id": command.command_id,
        "command_label": command.label,
        "argv": command.argv,
        "started_at": started_at,
        "finished_at": None,
        "duration_seconds": None,
        "exit_code": None,
        "status": "ERROR",
        "stdout": "",
        "stderr": "",
        "working_directory": command.working_directory,
    }

    try:
        result = subprocess.run(
            command.argv,
            cwd=command.working_directory,
            capture_output=True,
            text=True,
            timeout=command.timeout_seconds,
            shell=False,
        )
        payload["exit_code"] = result.returncode
        payload["status"] = "PASS" if result.returncode == 0 else "FAIL"
        payload["stdout"] = result.stdout
        payload["stderr"] = result.stderr
    except subprocess.TimeoutExpired as exc:
        payload["status"] = "TIMEOUT"
        payload["stdout"] = exc.stdout or ""
        payload["stderr"] = exc.stderr or ""
    except OSError as exc:
        payload["status"] = "ERROR"
        payload["stderr"] = str(exc)
    finally:
        finished = datetime.now()
        payload["finished_at"] = finished.replace(microsecond=0).isoformat(sep=" ")
        payload["duration_seconds"] = round((finished - started).total_seconds(), 3)
        _write_log(Path(logs_dir), payload)

    return payload


def execute_registered_command(
    registry: Dict[str, CommandSpec],
    command_id: str,
    logs_dir: Path,
) -> Dict[str, Any]:
    command = get_command_or_raise(registry, command_id)
    return execute_command(command, logs_dir)


def _safe_log_id(log_id: str) -> bool:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    return bool(log_id) and all(character in allowed for character in log_id)


def load_execution_log(logs_dir: Path, log_id: str) -> Optional[Dict[str, Any]]:
    if not _safe_log_id(log_id):
        return None
    log_path = Path(logs_dir) / f"{log_id}.json"
    try:
        return json.loads(log_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def list_execution_logs(logs_dir: Path) -> List[Dict[str, Any]]:
    logs_root = Path(logs_dir)
    if not logs_root.exists() or not logs_root.is_dir():
        return []

    entries: List[Dict[str, Any]] = []
    for log_path in logs_root.glob("*.json"):
        try:
            payload = json.loads(log_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        payload.setdefault("log_id", log_path.stem)
        payload["log_path"] = str(log_path)
        entries.append(payload)

    return sorted(
        entries,
        key=lambda item: item.get("started_at") or "",
        reverse=True,
    )


def command_to_dict(command: CommandSpec) -> Dict[str, Any]:
    return asdict(command)
