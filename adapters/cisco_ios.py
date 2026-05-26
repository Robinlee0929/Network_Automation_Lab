import time
from typing import Any, Dict, List, Optional

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
        self.client: Optional[paramiko.SSHClient] = None
        self.command_log: List[Dict[str, str]] = []

    def connect(self) -> None:
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
