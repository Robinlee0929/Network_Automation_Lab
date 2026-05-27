import time
from typing import Any, Dict, List, Optional, Tuple

import paramiko

from core.device_base import NetworkDevice
from parsers import cisco_parser


SSH_TIMEOUT_SECONDS = 15
COMMAND_TIMEOUT_SECONDS = 30


class CommandTimeoutError(RuntimeError):
    pass


class CiscoIOS(NetworkDevice):
    def __init__(self, config: Dict[str, Any]):
        self.host = str(config.get("host", config.get("router_ip", "")))
        self.port = int(config.get("port", config.get("ssh_port", 22)))
        self.username = str(config.get("username", "admin"))
        self.password = str(config.get("password", ""))
        self.legacy_ssh = bool(config.get("legacy_ssh", False))
        self.client: Optional[paramiko.SSHClient] = None
        self.command_log: List[Dict[str, str]] = []

    def connect(self) -> None:
        if self.legacy_ssh:
            self.client = self._connect_legacy_ssh()
            return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=SSH_TIMEOUT_SECONDS,
            banner_timeout=SSH_TIMEOUT_SECONDS,
            auth_timeout=SSH_TIMEOUT_SECONDS,
            look_for_keys=False,
            allow_agent=False,
        )
        self.client = client

    def _connect_legacy_ssh(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        transport = self._create_legacy_transport()
        try:
            transport.auth_password(self.username, self.password)
        except paramiko.AuthenticationException:
            transport.close()
            transport = self._create_legacy_transport()
            transport.auth_interactive(self.username, self._keyboard_interactive_handler)
        client._transport = transport
        return client

    def _create_legacy_transport(self) -> paramiko.Transport:
        transport = paramiko.Transport((self.host, self.port))

        security_options = transport.get_security_options()
        security_options.kex = self._prefer_supported_algorithms(
            security_options.kex,
            [
                "diffie-hellman-group14-sha1",
                "diffie-hellman-group1-sha1",
                "diffie-hellman-group-exchange-sha1",
            ],
        )
        security_options.ciphers = self._prefer_supported_algorithms(
            security_options.ciphers,
            ["aes128-cbc", "3des-cbc", "aes192-cbc", "aes256-cbc"],
        )
        if hasattr(security_options, "digests"):
            security_options.digests = self._prefer_supported_algorithms(
                security_options.digests,
                ["hmac-sha1"],
            )
        security_options.key_types = self._prefer_supported_algorithms(
            security_options.key_types,
            ["ssh-rsa", "ssh-dss"],
        )

        transport.banner_timeout = SSH_TIMEOUT_SECONDS
        transport.auth_timeout = SSH_TIMEOUT_SECONDS
        transport.start_client(timeout=SSH_TIMEOUT_SECONDS)
        return transport

    def _prefer_supported_algorithms(
        self,
        current: Tuple[str, ...],
        preferred: List[str],
    ) -> Tuple[str, ...]:
        supported = set(current)
        ordered: List[str] = []
        for algorithm in preferred:
            if algorithm in supported and algorithm not in ordered:
                ordered.append(algorithm)
        for algorithm in current:
            if algorithm not in ordered:
                ordered.append(algorithm)
        return tuple(ordered)

    def _keyboard_interactive_handler(
        self,
        _title: str,
        _instructions: str,
        prompts: List[Tuple[str, bool]],
    ) -> List[str]:
        return [self.password for _prompt, _echo in prompts]

    def get_identity(self) -> str:
        return self._run_command("show running-config | include hostname")

    def get_version(self) -> str:
        return self._run_command("show version")

    def get_interfaces(self) -> str:
        return self._run_command("show ip interface brief")

    def get_clock(self) -> str:
        return self._run_command("show clock")

    def ping(self, target: str) -> str:
        return self._run_command(f"ping {target}", timeout_seconds=45)

    def backup_config(self) -> str:
        return self._run_command("show running-config", timeout_seconds=60)

    def check_ntp(self) -> Dict[str, Any]:
        output = self._run_command("show ntp status")
        parsed = cisco_parser.parse_ntp(output)
        parsed["raw_output"] = output
        return parsed

    def close(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    def _run_command(
        self,
        command: str,
        timeout_seconds: int = COMMAND_TIMEOUT_SECONDS,
    ) -> str:
        if not self.client:
            raise RuntimeError("CiscoIOS is not connected.")

        self.command_log.append({"command": command})
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout_seconds)
        stdin.close()

        channel = stdout.channel
        output_chunks: List[str] = []
        error_chunks: List[str] = []
        deadline = time.monotonic() + timeout_seconds

        while not channel.exit_status_ready():
            if time.monotonic() > deadline:
                channel.close()
                raise CommandTimeoutError(
                    f"Command timed out after {timeout_seconds}s: {command}"
                )
            if channel.recv_ready():
                output_chunks.append(channel.recv(4096).decode("utf-8", errors="replace"))
            if channel.recv_stderr_ready():
                error_chunks.append(
                    channel.recv_stderr(4096).decode("utf-8", errors="replace")
                )
            time.sleep(0.1)

        while channel.recv_ready():
            output_chunks.append(channel.recv(4096).decode("utf-8", errors="replace"))
        while channel.recv_stderr_ready():
            error_chunks.append(channel.recv_stderr(4096).decode("utf-8", errors="replace"))

        exit_status = channel.recv_exit_status()
        output = "".join(output_chunks)
        error_output = "".join(error_chunks).strip()

        if exit_status != 0:
            raise RuntimeError(
                f"Command failed with exit status {exit_status}: {command}; stderr={error_output}"
            )

        return output
