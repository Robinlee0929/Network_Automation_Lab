import json
import subprocess
import sys
from pathlib import Path

import day6_lab_topology_summary as day6


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def make_profile(tmp_path: Path, devices):
    profile_path = tmp_path / "topology_profiles" / "lab.json"
    write_json(
        profile_path,
        {
            "topology_name": "test_lab",
            "devices": devices,
        },
    )
    return profile_path


def device(name, report_path, required=True):
    return {
        "device_name": name,
        "device_type": "test_device",
        "role": "lab_node",
        "management_ip": "192.0.2.10",
        "report_path": report_path,
        "required": required,
    }


def build_report(tmp_path: Path, profile_path: Path):
    profile = day6.load_profile(profile_path, tmp_path)
    return day6.build_summary_report(profile, profile_path, tmp_path)


def test_all_required_pass_overall_pass(tmp_path):
    write_json(tmp_path / "reports" / "r1.json", {"overall_result": "PASS"})
    write_json(tmp_path / "reports" / "r2.json", {"overall_status": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [
            device("router-a", "reports/r1.json"),
            device("switch-a", "reports/r2.json"),
        ],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "PASS"
    assert report["pass_count"] == 2


def test_required_report_missing_overall_fail(tmp_path):
    profile_path = make_profile(
        tmp_path,
        [device("router-a", "reports/missing.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "FAIL"
    assert report["devices"][0]["report_found"] is False


def test_required_report_fail_overall_fail(tmp_path):
    write_json(
        tmp_path / "reports" / "router.json",
        {
            "overall_result": "FAIL",
            "checks": [{"name": "LAN bridge IP", "result": "FAIL"}],
        },
    )
    profile_path = make_profile(
        tmp_path,
        [device("router-a", "reports/router.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "FAIL"
    assert report["devices"][0]["failed_checks"] == ["LAN bridge IP"]


def test_optional_report_missing_overall_warning(tmp_path):
    write_json(tmp_path / "reports" / "required.json", {"overall_result": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [
            device("required-a", "reports/required.json", required=True),
            device("optional-a", "reports/optional.json", required=False),
        ],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "WARNING"


def test_required_unknown_format_overall_warning(tmp_path):
    write_json(tmp_path / "reports" / "router.json", {"summary": "looks good"})
    profile_path = make_profile(
        tmp_path,
        [device("router-a", "reports/router.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "WARNING"
    assert report["devices"][0]["normalized_result"] == "UNKNOWN"


def test_replaced_device_name_still_generates_report(tmp_path):
    write_json(tmp_path / "reports" / "custom-router.json", {"result": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [device("new-router-name", "reports/custom-router.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "PASS"
    assert report["devices"][0]["device_name"] == "new-router-name"


def test_replaced_report_path_still_reads_report(tmp_path):
    write_json(tmp_path / "custom" / "replacement.json", {"status": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [device("router-a", "custom/replacement.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["overall_result"] == "PASS"
    assert report["devices"][0]["report_path"] == "custom/replacement.json"


def test_cli_with_different_profile_runs_successfully(tmp_path):
    report_path = tmp_path / "reports" / "required.json"
    write_json(report_path, {"overall_result": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [device("required-a", str(report_path))],
    )
    script = Path(day6.__file__).resolve()

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--profile",
            str(profile_path),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert (script.parent / "reports" / "day6_lab_topology_summary.json").exists()


def test_source_report_checks_list_expands_check_items(tmp_path):
    write_json(
        tmp_path / "reports" / "device.json",
        {
            "overall_result": "PASS",
            "checks": [
                {
                    "name": "SSH login",
                    "result": "PASS",
                    "message": "SSH login succeeded.",
                    "category": "connectivity",
                },
                {
                    "name": "Report generation",
                    "result": "PASS",
                    "message": "Report generated.",
                    "category": "reporting",
                },
            ],
        },
    )
    profile_path = make_profile(
        tmp_path,
        [device("device-a", "reports/device.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["devices"][0]["check_items"] == [
        {
            "name": "SSH login",
            "result": "PASS",
            "message": "SSH login succeeded.",
            "category": "connectivity",
        },
        {
            "name": "Report generation",
            "result": "PASS",
            "message": "Report generated.",
            "category": "reporting",
        },
    ]


def test_source_report_validation_results_expands_check_items(tmp_path):
    write_json(
        tmp_path / "reports" / "device.json",
        {
            "overall_status": "PASS",
            "validation_results": [
                {
                    "check_name": "VLAN active",
                    "status": "PASS",
                    "detail": "VLAN 1 is active.",
                    "group": "switching",
                },
                {
                    "test_name": "Dynamic MAC learned",
                    "outcome": "PASS",
                    "description": "MAC table contains dynamic entries.",
                    "section": "l2",
                },
            ],
        },
    )
    profile_path = make_profile(
        tmp_path,
        [device("switch-a", "reports/device.json")],
    )

    report = build_report(tmp_path, profile_path)

    assert report["devices"][0]["check_items"][0] == {
        "name": "VLAN active",
        "result": "PASS",
        "message": "VLAN 1 is active.",
        "category": "switching",
    }
    assert report["devices"][0]["check_items"][1] == {
        "name": "Dynamic MAC learned",
        "result": "PASS",
        "message": "MAC table contains dynamic entries.",
        "category": "l2",
    }


def test_source_report_without_details_does_not_crash_and_html_shows_message(tmp_path):
    write_json(tmp_path / "reports" / "device.json", {"overall_result": "PASS"})
    profile_path = make_profile(
        tmp_path,
        [device("device-a", "reports/device.json")],
    )

    report = build_report(tmp_path, profile_path)
    html = day6.build_html_report(report)

    assert report["devices"][0]["check_items"] == []
    assert "No detailed check items found in source report." in html


def test_cisco_report_check_items_can_be_expanded(tmp_path):
    write_json(
        tmp_path / "reports" / "cisco-switch" / "switch_topology_report.json",
        {
            "device_name": "cisco-switch",
            "overall_result": "PASS",
            "checks": [
                {
                    "name": "SSH login",
                    "result": "PASS",
                    "message": "SSH login succeeded.",
                },
                {
                    "name": "Vlan1 management IP",
                    "result": "PASS",
                    "message": "Vlan1 management IP and state match expected topology.",
                },
            ],
        },
    )
    profile_path = make_profile(
        tmp_path,
        [
            {
                **device(
                    "cisco-switch",
                    "reports/cisco-switch/switch_topology_report.json",
                ),
                "device_type": "cisco_ios",
                "role": "core_switch",
            }
        ],
    )

    report = build_report(tmp_path, profile_path)
    names = [item["name"] for item in report["devices"][0]["check_items"]]

    assert names == ["SSH login", "Vlan1 management IP"]
    assert report["devices"][0]["check_items"][0]["category"] == "general"


def test_mikrotik_report_check_items_can_be_expanded(tmp_path):
    write_json(
        tmp_path / "reports" / "Hex-s-2025-lab01" / "day4_baseline_validation.json",
        {
            "device_name": "Hex-s-2025-lab01",
            "overall_result": "PASS",
            "checks": [
                {
                    "name": "SSH connection",
                    "result": "PASS",
                    "message": "SSH login succeeded.",
                },
                {
                    "name": "LAN bridge IP",
                    "result": "PASS",
                    "message": "LAN bridge IP matches expected profile.",
                },
            ],
        },
    )
    profile_path = make_profile(
        tmp_path,
        [
            {
                **device(
                    "Hex-s-2025-lab01",
                    "reports/Hex-s-2025-lab01/day4_baseline_validation.json",
                ),
                "device_type": "mikrotik_routeros",
                "role": "router_under_test",
            }
        ],
    )

    report = build_report(tmp_path, profile_path)
    names = [item["name"] for item in report["devices"][0]["check_items"]]

    assert names == ["SSH connection", "LAN bridge IP"]
