import network_lab


RESTRICTED_LIVE_LABELS = {
    "live",
    "unrestricted-live",
    "live-unrestricted",
    "LIVE_CONFIG_CHANGE",
    "LIVE_PERFORMANCE",
}


def test_runner_task_catalog_has_day23_metadata_contract():
    tasks = network_lab.list_tasks()

    assert tasks
    for task in tasks:
        assert task.get("id")
        assert task.get("user_display_name")
        assert task.get("description")
        assert task.get("safety_level")
        assert task.get("execution_mode")
        assert isinstance(task.get("report_outputs", []), list)


def test_runner_task_catalog_uses_consistent_day23_safety_labels():
    allowed_safety_levels = {
        "dry-run",
        "guarded-live",
        "read-only",
        "report-only",
        "disabled",
        "controlled_failover_observation",
    }
    allowed_execution_modes = {
        "dry-run",
        "guarded-live",
        "read-only",
        "report-only",
        "disabled",
        "controlled_failover_observation",
    }

    for task in network_lab.list_tasks():
        assert task["safety_level"] in allowed_safety_levels
        assert task["execution_mode"] in allowed_execution_modes


def test_wireguard_tasks_are_not_unrestricted_live_execution():
    wireguard_tasks = [
        task
        for task in network_lab.list_tasks()
        if "wireguard" in " ".join(
            [
                str(task.get("id", "")),
                str(task.get("task_id", "")),
                str(task.get("display_name", "")),
                str(task.get("user_display_name", "")),
                str(task.get("description", "")),
            ]
        ).lower()
    ]

    assert wireguard_tasks
    for task in wireguard_tasks:
        assert task["safety_level"] not in RESTRICTED_LIVE_LABELS
        assert task["execution_mode"] not in RESTRICTED_LIVE_LABELS
        safety_text = " ".join(
            [
                task["safety_level"],
                task["execution_mode"],
                task.get("notes", ""),
                task.get("description", ""),
            ]
        ).lower()
        assert "guarded" in safety_text or "dry-run" in safety_text or "disabled" in safety_text


def test_report_only_and_disabled_tasks_are_explained():
    for task in network_lab.list_tasks():
        if task["execution_mode"] == "report-only":
            assert task["safety_level"] != "guarded-live"
        if task["safety_level"] == "disabled" or task.get("enabled") is False:
            explanation = " ".join([task.get("notes", ""), task.get("description", "")]).lower()
            assert any(word in explanation for word in ("disabled", "blocked", "placeholder", "report-only"))


def test_day33_vrrp_dry_run_catalog_entry_is_non_live():
    day33 = next(task for task in network_lab.list_tasks() if task["id"] == "day33-vrrp-dry-run")

    assert day33["task_id"] == "day33_vrrp_topology_dry_run"
    assert day33["safety_level"] == "dry-run"
    assert day33["execution_mode"] == "dry-run"
    assert day33["requires_live_device"] is False
    assert day33["requires_password"] is False
    assert "day33_vrrp_topology_dry_run.json" in day33["report_paths"][0]
    assert "v0.2 VRRP contract" in day33["notes"]


def test_day34_vrrp_staged_plan_catalog_entry_is_non_live():
    day34 = next(task for task in network_lab.list_tasks() if task["id"] == "day34-vrrp-staged-plan")

    assert day34["task_id"] == "day34_vrrp_staged_apply_plan"
    assert day34["safety_level"] == "dry-run"
    assert day34["execution_mode"] == "dry-run"
    assert day34["requires_live_device"] is False
    assert day34["requires_password"] is False
    assert "day34_vrrp_staged_apply_plan.json" in day34["report_paths"][0]
    assert "safety gate" in day34["notes"].lower()
    assert "never opens SSH" in day34["notes"]


def test_day35_vrrp_failover_catalog_entry_is_controlled_observation():
    day35 = next(task for task in network_lab.list_tasks() if task["id"] == "day35-vrrp-failover-validation")

    assert day35["task_id"] == "day35_vrrp_failover_validation"
    assert day35["safety_level"] == "controlled_failover_observation"
    assert day35["execution_mode"] == "controlled_failover_observation"
    assert day35["requires_live_device"] is True
    assert day35["requires_password"] is True
    assert "day35_vrrp_failover_validation.json" in day35["report_paths"][0]
    assert "disconnect/reconnect lab01 LAN externally" in day35["notes"]
    assert "blocks interface, firewall/NAT, IP, VRRP, reboot, and reset changes" in day35["notes"]


def test_day39_vrrp_evidence_dashboard_integration_catalog_entry_is_report_only():
    day39 = next(task for task in network_lab.list_tasks() if task["id"] == "day39-vrrp-evidence-dashboard-integration")

    assert day39["task_id"] == "day39_vrrp_evidence_dashboard_integration"
    assert day39["safety_level"] == "report-only"
    assert day39["execution_mode"] == "report-only"
    assert day39["requires_live_device"] is False
    assert day39["requires_password"] is False
    assert "day39_vrrp_evidence_dashboard_integration.json" in day39["report_paths"][0]
    assert "does not run SSH" in day39["notes"]
    assert "configuration changes" in day39["notes"]


def test_day40_demo_readiness_catalog_entry_is_report_only():
    day40 = next(task for task in network_lab.list_tasks() if task["id"] == "day40-v0.2-demo-readiness-review")

    assert day40["task_id"] == "day40_v0.2_demo_readiness_review"
    assert day40["safety_level"] == "report-only"
    assert day40["execution_mode"] == "report-only"
    assert day40["requires_live_device"] is False
    assert day40["requires_password"] is False
    assert "reports/portfolio/day40_v0.2_demo_readiness_review.json" in day40["report_paths"]
    assert "does not run SSH" in day40["notes"]
    assert "configuration changes" in day40["notes"]
