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
    allowed_safety_levels = {"dry-run", "guarded-live", "read-only", "report-only", "disabled"}
    allowed_execution_modes = {"dry-run", "guarded-live", "read-only", "report-only", "disabled"}

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
