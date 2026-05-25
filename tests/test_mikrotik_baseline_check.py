import json

import pytest

import mikrotik_baseline_check as checker


def test_get_device_name_uses_cli_value():
    assert checker.get_device_name(" hex-s-2025-lab01 ") == "hex-s-2025-lab01"


def test_get_password_uses_prompt_value(monkeypatch):
    monkeypatch.setattr(checker.getpass, "getpass", lambda _: "runtime-password")

    assert checker.get_password("config-password") == "runtime-password"


def test_get_password_falls_back_to_config_default(monkeypatch):
    monkeypatch.setattr(checker.getpass, "getpass", lambda _: "")

    assert checker.get_password("config-password") == "config-password"


def test_get_password_requires_some_password(monkeypatch):
    monkeypatch.setattr(checker.getpass, "getpass", lambda _: "")

    with pytest.raises(ValueError, match="SSH password is required"):
        checker.get_password("")


def test_connect_ssh_with_auth_retry_prompts_again_after_auth_failure(monkeypatch):
    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="wrong-password",
    )
    attempts = []

    def fake_connect_ssh(received_config):
        attempts.append(received_config.password)
        if len(attempts) == 1:
            raise checker.paramiko.AuthenticationException("Authentication failed.")
        return "connected"

    monkeypatch.setattr(checker, "connect_ssh", fake_connect_ssh)
    monkeypatch.setattr(checker.getpass, "getpass", lambda _: "correct-password")

    assert checker.connect_ssh_with_auth_retry(config) == "connected"
    assert attempts == ["wrong-password", "correct-password"]


def test_connect_ssh_with_auth_retry_raises_after_max_attempts(monkeypatch):
    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="wrong-password",
    )

    def fake_connect_ssh(_):
        raise checker.paramiko.AuthenticationException("Authentication failed.")

    monkeypatch.setattr(checker, "connect_ssh", fake_connect_ssh)
    monkeypatch.setattr(checker.getpass, "getpass", lambda _: "still-wrong")

    with pytest.raises(checker.paramiko.AuthenticationException):
        checker.connect_ssh_with_auth_retry(config, max_attempts=2)


def test_load_config_uses_defaults(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"password": "secret"}), encoding="utf-8")

    config = checker.load_config(config_path)

    assert config.router_ip == "192.168.88.1"
    assert config.ssh_port == 22
    assert config.username == "admin"
    assert config.password == "secret"


def test_validate_read_only_command_accepts_allowlisted_command():
    checker.validate_read_only_command("/system clock print")


def test_validate_read_only_command_rejects_forbidden_command():
    with pytest.raises(ValueError, match="read-only allowlist"):
        checker.validate_read_only_command("/system reboot")


def test_validate_read_only_command_still_rejects_identity_set():
    with pytest.raises(ValueError, match="read-only allowlist"):
        checker.validate_read_only_command('/system identity set name="hex-s-2025-lab01"')


def test_quote_routeros_value_escapes_special_characters():
    assert checker.quote_routeros_value('lab"01\\rack') == '"lab\\"01\\\\rack"'


def test_keyboard_interactive_handler_returns_password_for_each_prompt():
    handler = checker.make_keyboard_interactive_handler("secret")

    responses = handler(
        "title",
        "instructions",
        [("Password: ", False), ("Verification: ", False)],
    )

    assert responses == ["secret", "secret"]


def test_validate_identity_name_rejects_newline():
    with pytest.raises(ValueError, match="newline"):
        checker.validate_identity_name("lab01\nbad")


def test_set_routeros_identity_uses_explicit_identity_command(monkeypatch):
    calls = []

    def fake_run_raw_command(_client, command):
        calls.append(command)
        return ""

    monkeypatch.setattr(checker, "run_raw_command", fake_run_raw_command)

    check = checker.set_routeros_identity(object(), "hex-s-2025-lab01")

    assert check["result"] == "PASS"
    assert calls == ['/system identity set name="hex-s-2025-lab01"']


def test_output_has_field_matches_routeros_key_value_output():
    output = """
        time: 13:41:20
        time-zone-name: Asia/Taipei
        gmt-offset: +08:00
    """

    assert checker.output_has_field(output, "time-zone-name", "Asia/Taipei")
    assert checker.output_has_field(output, "gmt-offset", "+08:00")


@pytest.mark.parametrize(
    "output",
    [
        "sent=3 received=3 packet-loss=0%",
        "sent: 3 received: 1 packet-loss: 66%",
        "sent=3 received=0 packet-loss=50%",
    ],
)
def test_validate_ping_output_passes_when_packets_received_or_loss_not_100(output):
    assert checker.validate_ping_output(output)


def test_validate_ping_output_fails_when_loss_is_100():
    assert not checker.validate_ping_output("sent=3 received=0 packet-loss=100%")


def test_validate_ping_output_rejects_unexpected_format():
    with pytest.raises(checker.UnexpectedOutputError):
        checker.validate_ping_output("routeros ping output without summary")


def test_build_reports_sets_overall_pass():
    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="secret",
    )
    checks = [
        checker.make_check("ssh login", True, "SSH login succeeds.", "ok"),
        checker.make_check("ntp client is enabled", True, "enabled: yes", "ok"),
    ]

    report = checker.build_reports("hex-s-2025-lab01", config, checks)

    assert report["device_name"] == "hex-s-2025-lab01"
    assert report["router_ip"] == "192.168.88.1"
    assert report["ssh_port"] == 22
    assert report["overall_result"] == "PASS"


def test_build_reports_sets_overall_fail_when_any_check_fails():
    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="secret",
    )
    checks = [
        checker.make_check("ssh login", True, "SSH login succeeds.", "ok"),
        checker.make_check("ntp client is enabled", False, "enabled: yes", "missing"),
    ]

    report = checker.build_reports("hex-s-2025-lab01", config, checks)

    assert report["overall_result"] == "FAIL"


def test_write_reports_creates_timestamped_and_latest_files(tmp_path, monkeypatch):
    monkeypatch.setattr(checker, "REPORT_DIR", tmp_path / "reports")

    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="secret",
    )
    checks = [
        checker.make_check("ssh login", True, "SSH login succeeds.", "ok"),
    ]
    report = checker.build_reports("hex-s-2025-lab01", config, checks)

    json_path, txt_path = checker.write_reports(report)

    assert json_path.name.endswith("_PASS.json")
    assert txt_path.name.endswith("_PASS.txt")
    assert json_path.exists()
    assert txt_path.exists()
    assert (checker.REPORT_DIR / "report.json").exists()
    assert (checker.REPORT_DIR / "report.txt").exists()


def test_write_reports_text_file_uses_plain_table_format(tmp_path, monkeypatch):
    monkeypatch.setattr(checker, "REPORT_DIR", tmp_path / "reports")

    config = checker.RouterConfig(
        router_ip="192.168.88.1",
        ssh_port=22,
        username="admin",
        password="secret",
    )
    checks = [
        checker.make_check(
            "ssh login",
            True,
            "SSH login succeeds.",
            "Authenticated successfully.",
        ),
    ]
    report = checker.build_reports("hex-s-2025-lab01", config, checks)

    _, txt_path = checker.write_reports(report)
    text_report = txt_path.read_text(encoding="utf-8")

    assert "MikroTik Baseline Acceptance" in text_report
    assert "No.  Result" in text_report
    assert "1    PASS" in text_report
    assert "ssh login" in text_report
    assert "\033[" not in text_report


def test_print_console_summary_lists_each_check(capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(checker, "REPORT_DIR", tmp_path / "reports")
    report = {
        "device_name": "hex-s-2025-lab01",
        "router_ip": "192.168.88.1",
        "ssh_port": 22,
        "overall_result": "PASS",
        "checks": [
            {
                "name": "ssh login",
                "result": "PASS",
                "expected": "SSH login succeeds.",
                "details": "Authenticated successfully.",
            }
        ],
    }

    checker.print_console_summary(
        report,
        checker.REPORT_DIR / "report_20260525_133500_PASS.json",
        checker.REPORT_DIR / "report_20260525_133500_PASS.txt",
    )

    output = capsys.readouterr().out
    assert "MikroTik Baseline Acceptance" in output
    assert "Checks" in output
    assert "PASS" in output
    assert "ssh login" in output
    assert "Authenticated successfully." in output
    assert "report_20260525_133500_PASS.json" in output
