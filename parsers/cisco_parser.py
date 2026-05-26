import re
from typing import Any, Dict


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
