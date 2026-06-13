import ast
import json
import subprocess
import sys
from pathlib import Path

import network_lab
import network_lab_cli_dispatch


def test_cli_dispatch_module_is_importable_and_builds_parser():
    parser = network_lab_cli_dispatch._build_parser(network_lab)
    args = parser.parse_args(["--task", "report-index", "--dry-run"])

    assert args.task == "report-index"
    assert args.dry_run is True


def test_network_lab_script_help_entrypoint_works():
    result = subprocess.run(
        [sys.executable, "network_lab.py", "--help"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--task" in result.stdout
    assert "--report-index" in result.stdout


def test_cli_dispatch_preserves_report_index_task(tmp_path):
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "lab_name": "Dispatch Test Lab",
                "overview_output": {
                    "json": "reports/lab-summary/latest_lab_overview.json",
                    "html": "reports/lab-summary/latest_lab_overview.html",
                },
                "devices": [
                    {
                        "name": "router1",
                        "type": "mikrotik",
                        "required": False,
                        "reports": [
                            {
                                "name": "Optional Report",
                                "json": "reports/router1/report.json",
                                "html": "reports/router1/report.html",
                                "required": False,
                            }
                        ],
                    }
                ],
                "lab_summary_reports": [
                    {
                        "name": "Lab Summary",
                        "json": "reports/lab-summary/summary.json",
                        "html": "reports/lab-summary/summary.html",
                        "required": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "reports/lab-summary").mkdir(parents=True)
    (tmp_path / "reports/lab-summary/summary.json").write_text(
        json.dumps({"summary": {"result": "PASS"}}),
        encoding="utf-8",
    )

    exit_code = network_lab.main(
        ["--task", "report-index", "--profile", str(profile_path)],
        project_root=tmp_path,
    )

    assert exit_code == 0
    assert (tmp_path / "reports/lab-summary/latest_lab_overview.html").exists()


def test_cli_dispatch_preserves_report_index_flag(tmp_path):
    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    assert (tmp_path / "reports/report_index.html").exists()


def test_cli_dispatch_preserves_lightweight_existing_task(tmp_path, capsys):
    exit_code = network_lab.main(
        ["--task", "intent-mapping-prototype", "--intent-text", "show me the latest reports"],
        project_root=tmp_path,
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Day57 AI-assisted Task Intent Mapping Prototype" in output
    assert "Dry-run mapping only. No mapped task was executed." in output


def test_cli_dispatch_module_adds_no_live_execution_dependency_imports():
    source = Path(network_lab_cli_dispatch.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".")[0])

    assert imported_modules.isdisjoint(
        {
            "netmiko",
            "openai",
            "paramiko",
            "requests",
            "socket",
            "subprocess",
            "webbrowser",
        }
    )
