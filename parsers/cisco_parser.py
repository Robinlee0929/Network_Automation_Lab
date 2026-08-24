import re
from typing import Any, Dict, List


def _normalize_interface_name(name: str) -> str:
    text = name.strip()
    replacements = {
        "GigabitEthernet": "Gi",
        "FastEthernet": "Fa",
        "TenGigabitEthernet": "Te",
        "Vlan": "Vlan",
    }
    for long_name, short_name in replacements.items():
        if text.startswith(long_name):
            return short_name + text[len(long_name) :]
    return text


def parse_ping(output: str) -> Dict[str, Any]:
    success_match = re.search(r"Success rate is\s+(\d+)\s+percent", output, re.IGNORECASE)
    success_rate = int(success_match.group(1)) if success_match else None
    has_success_bang = "!" in output
    passed = bool((success_rate is not None and success_rate > 0) or has_success_bang)

    return {
        "result": "PASS" if passed else "FAIL",
        "success_rate": success_rate,
        "details": "Cisco ping contains Success rate > 0 or ! response markers.",
    }


def parse_ntp(output: str) -> Dict[str, Any]:
    synchronized = "clock is synchronized" in output.lower()
    return {
        "result": "PASS" if synchronized else "WARNING",
        "synchronized": synchronized,
        "details": (
            "Cisco NTP reports Clock is synchronized."
            if synchronized
            else "Cisco NTP is not synchronized; read-only baseline marks this WARNING."
        ),
    }


def parse_show_version(output: str) -> Dict[str, Any]:
    version_match = re.search(
        r"Cisco IOS Software.*?Version\s+([^,\s]+)",
        output,
        re.IGNORECASE | re.DOTALL,
    )
    if not version_match:
        version_match = re.search(r"\bVersion\s+([^,\s]+)", output, re.IGNORECASE)

    model = ""
    model_patterns = [
        r"Model\s+[Nn]umber\s*:\s*(\S+)",
        r"cisco\s+([A-Z0-9-]+)\s+\(",
        r"^([A-Z0-9-]+)\s+uptime is",
    ]
    for pattern in model_patterns:
        match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
        if match:
            model = match.group(1).strip()
            break

    serial_match = re.search(
        r"(?:System serial number|Processor board ID)\s*[: ]\s*(\S+)",
        output,
        re.IGNORECASE,
    )
    hostname_match = re.search(r"^(\S+)\s+uptime is", output, re.MULTILINE)

    return {
        "ios_version": version_match.group(1).strip() if version_match else "",
        "model": model,
        "serial_number": serial_match.group(1).strip() if serial_match else "",
        "hostname": hostname_match.group(1).strip() if hostname_match else "",
    }


def parse_show_ip_interface_brief(output: str) -> Dict[str, Dict[str, str]]:
    interfaces: Dict[str, Dict[str, str]] = {}
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith("interface"):
            continue
        parts = stripped.split()
        if len(parts) < 6:
            continue
        name = _normalize_interface_name(parts[0])
        interfaces[name] = {
            "interface": name,
            "ip_address": parts[1],
            "ok": parts[2],
            "method": parts[3],
            "status": " ".join(parts[4:-1]).lower(),
            "protocol": parts[-1].lower(),
        }
    return interfaces


def parse_show_interfaces_status(output: str) -> Dict[str, Dict[str, str]]:
    interfaces: Dict[str, Dict[str, str]] = {}
    for line in output.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.lower().startswith("port"):
            continue
        parts = stripped.split()
        if len(parts) < 4:
            continue
        port = _normalize_interface_name(parts[0])
        status_index = None
        for index, token in enumerate(parts[1:], start=1):
            if token.lower() in {
                "connected",
                "notconnect",
                "disabled",
                "err-disabled",
                "inactive",
                "monitoring",
                "sfpabsent",
            }:
                status_index = index
                break
        if status_index is None:
            continue
        interfaces[port] = {
            "port": port,
            "name": " ".join(parts[1:status_index]),
            "status": parts[status_index].lower(),
            "vlan": parts[status_index + 1] if len(parts) > status_index + 1 else "",
            "duplex": parts[status_index + 2] if len(parts) > status_index + 2 else "",
            "speed": parts[status_index + 3] if len(parts) > status_index + 3 else "",
            "type": " ".join(parts[status_index + 4 :]),
        }
    return interfaces


def parse_show_vlan_brief(output: str) -> Dict[str, Dict[str, Any]]:
    vlans: Dict[str, Dict[str, Any]] = {}
    current_vlan_id = ""

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower().startswith(("vlan", "----")):
            current_vlan_id = ""
            continue

        match = re.match(r"^(\d+)\s+(\S+)\s+(\S+)\s*(.*)$", stripped)
        if not match:
            continuation_ports = [
                port.strip().rstrip(",") for port in stripped.split()
            ]
            valid_continuation = bool(
                current_vlan_id
                and line[:1].isspace()
                and continuation_ports
                and all(
                    re.fullmatch(
                        r"[A-Za-z][A-Za-z-]*\d+(?:/\d+)*(?:\.\d+)?",
                        port,
                    )
                    for port in continuation_ports
                )
            )
            if valid_continuation:
                vlans[current_vlan_id]["ports"].extend(
                    _normalize_interface_name(port) for port in continuation_ports
                )
            else:
                current_vlan_id = ""
            continue

        vlan_id, name, status, ports_text = match.groups()
        ports = [
            _normalize_interface_name(port.strip().rstrip(","))
            for port in ports_text.split()
            if port.strip().rstrip(",")
        ]
        vlans[vlan_id] = {
            "vlan_id": vlan_id,
            "name": name,
            "status": status.lower(),
            "ports": ports,
        }
        current_vlan_id = vlan_id
    return vlans


def parse_show_mac_address_table(output: str) -> Dict[str, Any]:
    entries: List[Dict[str, str]] = []
    for line in output.splitlines():
        stripped = line.strip().lstrip("*").strip()
        if not stripped or stripped.startswith("-"):
            continue
        parts = stripped.split()
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        entry_type = parts[2].lower()
        entries.append(
            {
                "vlan": parts[0],
                "mac_address": parts[1],
                "type": entry_type,
                "ports": _normalize_interface_name(parts[-1]),
            }
        )
    return {
        "entries": entries,
        "dynamic_count": sum(1 for entry in entries if entry["type"] == "dynamic"),
    }


def parse_show_spanning_tree_summary(output: str) -> Dict[str, Any]:
    mode_match = re.search(
        r"Switch is in\s+(\S+)\s+mode",
        output,
        re.IGNORECASE,
    )
    if not mode_match:
        mode_match = re.search(r"spanning tree enabled protocol\s+(\S+)", output, re.IGNORECASE)

    vlan_blocking: Dict[str, int] = {}
    for line in output.splitlines():
        stripped = line.strip()
        match = re.match(
            r"^(VLAN\d+)\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+",
            stripped,
            re.IGNORECASE,
        )
        if match:
            vlan_blocking[match.group(1).upper()] = int(match.group(2))

    return {
        "mode": mode_match.group(1).lower() if mode_match else "",
        "vlan_blocking_ports": vlan_blocking,
    }
