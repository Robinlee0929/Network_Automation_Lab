import ast
import json
from pathlib import Path

import intent_real_adapter_implementation_plan as day90


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "routeros_api",
    "librouteros",
    "socket",
    "subprocess",
    "requests",
    "telnetlib",
    "asyncssh",
}


def write_required_day90_evidence(root: Path) -> None:
    for spec in day90.required_evidence_spec():
        for artifact in spec["artifacts"]:
            path = root / artifact["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            text = spec.get("required_text") or artifact["path"]
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            path.write_text(f"{existing}\n{text}", encoding="utf-8")


def test_day90_report_generation_is_deterministic_and_planning_only(tmp_path):
    write_required_day90_evidence(tmp_path)

    first = day90.build_real_adapter_implementation_plan_report(tmp_path)
    second = day90.build_real_adapter_implementation_plan_report(tmp_path)

    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["day"] == 90
    assert first["title"] == "Real Adapter Implementation Plan"
    assert first["scope"] == "planning_only"
    assert first["status"] == "PASS"
    assert first["decision"] in {"GO", "CONDITIONAL_GO", "NO_GO"}


def test_day90_required_safety_flags_remain_locked(tmp_path):
    write_required_day90_evidence(tmp_path)
    report = day90.build_real_adapter_implementation_plan_report(tmp_path)

    assert day90.validate_real_adapter_implementation_plan(report) == []
    assert report["adapter_implementation_allowed"] is False
    assert report["live_device_access_allowed"] is False
    assert report["ssh_allowed"] is False
    assert report["routeros_command_execution_allowed"] is False
    assert report["decision"] == "CONDITIONAL_GO"


def test_day90_missing_critical_evidence_cannot_produce_go(tmp_path):
    report = day90.build_real_adapter_implementation_plan_report(tmp_path)

    assert report["decision"] == "NO_GO"
    assert report["readiness_level"] == "BLOCKED"
    assert report["non_go_blockers"]
    assert day90.validate_real_adapter_implementation_plan(report) == []


def test_day90_evidence_chain_forbidden_scope_and_report_paths(tmp_path):
    write_required_day90_evidence(tmp_path)
    report = day90.build_real_adapter_implementation_plan_report(tmp_path)

    assert report["evidence_chain"]
    chain_text = json.dumps(report["evidence_chain"], sort_keys=True)
    for day in ("Day83", "Day84", "Day85", "Day86", "Day87", "Day88", "Day89", "Day90"):
        assert day in chain_text

    forbidden = " ".join(report["explicitly_forbidden_scope"]).lower()
    assert "mutation" in forbidden
    assert "configuration" in forbidden
    assert "write" in forbidden
    assert report["reports"]["json"] == "reports/lab-summary/day90_real_adapter_implementation_plan.json"
    assert report["reports"]["html"] == "reports/lab-summary/day90_real_adapter_implementation_plan.html"


def test_day90_reports_are_written_without_action_controls(tmp_path):
    write_required_day90_evidence(tmp_path)
    report = day90.build_real_adapter_implementation_plan_report(tmp_path)
    json_path, html_path = day90.write_real_adapter_implementation_plan_reports(tmp_path, report)

    assert json_path == tmp_path / "reports/lab-summary/day90_real_adapter_implementation_plan.json"
    assert html_path == tmp_path / "reports/lab-summary/day90_real_adapter_implementation_plan.html"
    assert json_path.exists()
    assert html_path.exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert data == report
    assert "Real Adapter Implementation Plan" in html
    assert "Readiness level" in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert "<button" not in html.lower()
    assert "<script" not in html.lower()


def test_day90_module_has_no_forbidden_runtime_imports_or_network_io():
    source_path = Path(day90.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(FORBIDDEN_IMPORTS)
    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source
        assert f"from {forbidden}" not in source
    assert ".connect(" not in source
    assert ".send(" not in source
    assert ".recv(" not in source
    assert "subprocess." not in source
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "random" not in source
    assert "uuid" not in source.lower()
    assert "exec(" not in source
    assert "eval(" not in source
