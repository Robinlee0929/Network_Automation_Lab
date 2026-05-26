import re
from typing import Any, Dict


def normalize_output(output: str) -> str:
    return re.sub(r"\s+", " ", output.strip()).lower()


def parse_key_value_output(output: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    pattern = re.compile(r"([\w-]+)\s*:\s*(.*?)(?=\s+[\w-]+\s*:|$)")

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for key, value in pattern.findall(stripped):
            values[key] = value.strip()

    return values


def parse_ping(output: str) -> Dict[str, Any]:
    normalized = normalize_output(output)
    received_match = re.search(r"\breceived\s*[=:]\s*(\d+)\b", normalized)
    loss_match = re.search(r"\bpacket-loss\s*[=:]\s*(\d+)%", normalized)

    received = int(received_match.group(1)) if received_match else None
    packet_loss = int(loss_match.group(1)) if loss_match else None
    passed = bool(received and received > 0) or (
        packet_loss is not None and packet_loss != 100
    )

    return {
        "result": "PASS" if passed else "FAIL",
        "received": received,
        "packet_loss_percent": packet_loss,
        "details": "received > 0 or packet-loss is not 100%",
    }


def parse_ntp(output: str) -> Dict[str, Any]:
    values = parse_key_value_output(output)
    enabled = values.get("enabled", "").lower()
    status = values.get("status", "").lower()
    passed = enabled == "yes" and status == "synchronized"

    return {
        "result": "PASS" if passed else "FAIL",
        "enabled": values.get("enabled", ""),
        "status": values.get("status", ""),
        "synced_server": values.get("synced-server", ""),
        "details": "MikroTik NTP is enabled and synchronized.",
    }


def parse_clock(output: str) -> Dict[str, Any]:
    values = parse_key_value_output(output)
    timezone = values.get("time-zone-name", "")
    gmt_offset = values.get("gmt-offset", "")

    return {
        "result": "PASS" if timezone and gmt_offset else "WARNING",
        "time_zone_name": timezone,
        "gmt_offset": gmt_offset,
        "details": "Clock output contains timezone and GMT offset.",
    }
