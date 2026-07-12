"""Deterministic AI-assistance evidence roots for hermetic positive-path tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Mapping

import ai_provider_disabled_by_default_safety_regression as day135
import ai_reviewer_export_package_integration as day136
import day145_v04_ai_assistance_evidence_freeze_package as day145
import day146_v04_ai_assistance_non_advancement_gate as day146
import day148_ai_assistance_display_consistency_audit as day148
import day149_ai_assistance_docs_registry_report_index_consistency_audit as day149
import day150_v04_ai_assistance_phase_gate_closure_review as day150
import day151_v04_ai_assistance_closure_evidence_index as day151
import project_folder_organization_decision_gate as day137


_CORE_STATIC_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/ai-intent/README.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
)


def build_deterministic_ai_assistance_evidence_root(
    test_root: Path,
    repository_root: Path,
) -> Path:
    """Materialize the bounded Day127-Day150 evidence chain under ``test_root``."""

    root = Path(test_root)
    source_root = Path(repository_root)
    _copy_tracked_static_inputs(source_root, root)
    _write_day127_to_day144_reports(root)

    report135 = day135.build_ai_provider_disabled_by_default_safety_regression_report(root)
    _require_pass("Day135", report135)
    day135.write_ai_provider_disabled_by_default_safety_regression_reports(root, report135)

    report136 = day136.build_ai_reviewer_export_package_integration_report(root)
    _require_pass("Day136", report136)
    day136.write_ai_reviewer_export_package_integration_reports(root, report136)

    report137 = day137.build_project_folder_organization_decision_gate_report(root)
    _require_pass("Day137", report137)
    day137.write_project_folder_organization_decision_gate_reports(root, report137)

    report145 = day145.build_day145_v04_ai_assistance_evidence_freeze_package(root)
    _require_pass("Day145", report145)
    day145.write_day145_v04_ai_assistance_evidence_freeze_package_reports(root, report145)

    report146 = day146.build_day146_v04_ai_assistance_non_advancement_gate(root)
    _require_pass("Day146", report146)
    day146.write_day146_v04_ai_assistance_non_advancement_gate_reports(root, report146)

    _write_json(
        root / "reports/lab-summary/day147_ai_assistance_deferred_risk_register.json",
        {
            "day": 147,
            "day_label": "Day147",
            "task": "ai-assistance-deferred-risk-register",
            "title": "AI Assistance Deferred Risk Register",
            "overall_status": "PASS",
            "status": "AI_ASSISTANCE_DEFERRED_RISK_REGISTER_READY",
            "review_only": True,
            "report_only": True,
            "next_phase_allowed": False,
        },
    )
    _write_text(
        root / "reports/lab-summary/day147_ai_assistance_deferred_risk_register.html",
        "<p>Day147 review-only deferred risk evidence.</p>",
    )

    report148 = day148.build_day148_ai_assistance_display_consistency_audit(root)
    _require_pass("Day148", report148)
    day148.write_day148_ai_assistance_display_consistency_audit_reports(root, report148)

    report149 = day149.build_day149_ai_assistance_docs_registry_report_index_consistency_audit(root)
    _require_pass("Day149", report149)
    day149.write_day149_ai_assistance_docs_registry_report_index_consistency_audit_reports(root, report149)

    report150 = day150.build_day150_v04_ai_assistance_phase_gate_closure_review(root)
    _require_pass("Day150", report150)
    day150.write_day150_v04_ai_assistance_phase_gate_closure_review_reports(root, report150)
    return root


def day134_disabled_provider_contract() -> dict[str, Any]:
    """Return the minimal valid Day134 disabled-provider contract."""

    return {
        "day_number": 134,
        "day_label": "Day134",
        "task": "disabled-ai-provider-adapter-contract",
        "result": day135.SOURCE_CONTRACT_RESULT,
        "overall_status": "PASS",
        "provider_enabled": False,
        "api_enabled": False,
        "execution_enabled": False,
        "model_invocation_enabled": False,
        "network_enabled": False,
        "provider_instantiated": False,
        "api_called": False,
        "execution_invoked": False,
        "next_phase_allowed": False,
    }


def _copy_tracked_static_inputs(source_root: Path, target_root: Path) -> None:
    relative_paths = set(_CORE_STATIC_PATHS)
    for artifact in day145.SOURCE_ARTIFACTS:
        relative_paths.update(str(path) for path in artifact["paths"])
    for spec in day148.ARTIFACT_SPECS:
        relative_paths.update(str(path) for path in spec["paths"])
    for spec in day149.DAY_SPECS:
        relative_paths.update(str(spec[key]) for key in ("script", "roadmap", "ai_intent"))
    for source in (*day150.PRIOR_DAY_CONCLUSIONS, *day151.SOURCE_EVIDENCE):
        relative_paths.update(str(source[key]) for key in ("script", "roadmap", "ai_intent"))

    for relative_path in sorted(relative_paths):
        normalized = Path(relative_path)
        if normalized.parts and normalized.parts[0] == "reports":
            continue
        source = source_root / normalized
        if not source.is_file():
            raise AssertionError(f"Tracked test input is missing: {relative_path}")
        destination = target_root / normalized
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _write_day127_to_day144_reports(root: Path) -> None:
    reports_by_day: dict[int, set[str]] = {}
    for artifact in day145.SOURCE_ARTIFACTS:
        day_number = int(str(artifact["day"]).removeprefix("Day"))
        reports_by_day[day_number] = {
            str(path) for path in artifact["paths"] if Path(str(path)).parts[0] == "reports"
        }

    display_specs = {int(str(spec["day"]).removeprefix("Day")): spec for spec in day148.ARTIFACT_SPECS}
    for day_number, report_paths in reports_by_day.items():
        payload = _base_report(day_number)
        if day_number == 130:
            payload["redaction_status"] = "REDACTION_REVIEW_READY"
        if day_number == 131:
            payload.update(
                {
                    "audit_status": "AI_SUMMARY_AUDIT_TRAIL_BOUND_REVIEW_ONLY",
                    "audit_record_count": 1,
                }
            )
        if day_number == 134:
            payload = day134_disabled_provider_contract()
        if day_number in display_specs:
            payload = _display_report(display_specs[day_number])

        for relative_path in sorted(report_paths):
            output = root / relative_path
            if output.suffix == ".json":
                _write_json(output, payload)
            else:
                _write_text(output, f"Day{day_number} deterministic review-only test evidence.\n")


def _base_report(day_number: int) -> dict[str, Any]:
    return {
        "day": day_number,
        "day_label": f"Day{day_number}",
        "task": f"deterministic-day{day_number}-test-evidence",
        "overall_status": "PASS",
        "status": "PASS",
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
    }


def _display_report(spec: Mapping[str, Any]) -> dict[str, Any]:
    payload = _base_report(int(str(spec["day"]).removeprefix("Day")))
    payload.update(
        {
            "title": spec["expected_title"],
            "required_phrases": list(spec["required_phrases"]),
            **{field: True for field in spec["required_true"]},
            **{field: False for field in spec["required_false"]},
        }
    )
    return payload


def _require_pass(label: str, report: Mapping[str, Any]) -> None:
    if report.get("overall_status") != "PASS":
        errors = report.get("validation_errors", [])
        raise AssertionError(f"{label} deterministic evidence did not pass: {errors}")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _write_text(path, json.dumps(dict(payload), indent=2, sort_keys=True))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
