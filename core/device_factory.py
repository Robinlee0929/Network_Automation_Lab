from typing import Any, Dict

from adapters.cisco_ios import CiscoIOS
from adapters.mikrotik_routeros import MikroTikRouterOS
from core.device_base import NetworkDevice


def create_device(config: Dict[str, Any]) -> NetworkDevice:
    device_config = dict(config)
    device_section = config.get("device", {})
    if isinstance(device_section, dict):
        device_config.update(device_section)

    vendor = str(device_config.get("vendor", "mikrotik")).strip().lower()
    platform = str(device_config.get("platform", "routeros")).strip().lower()

    if vendor == "mikrotik" and platform == "routeros":
        return MikroTikRouterOS(device_config)
    if vendor == "cisco" and platform == "ios":
        return CiscoIOS(device_config)

    raise ValueError(f"Unsupported device platform: vendor={vendor}, platform={platform}")
