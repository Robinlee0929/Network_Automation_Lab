import argparse
import getpass
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from core.device_factory import create_device
from parsers import cisco_parser, mikrotik_parser


CONFIG_PATH = Path("config.json")
REPORT_DIR = Path("reports") / "experimental"


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Create it from config.example.json.")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Experimental adapter-based MikroTik/Cisco baseline."
    )
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to config JSON.")
    parser.add_argument("--target", default="8.8.8.8", help="Ping target.")
    return parser.parse_args()


def get_device_meta(config: Dict[str, Any]) -> Tuple[str, str]:
    device = config.get("device", {})
    if not isinstance(device, dict):
        device = {}
    vendor = str(device.get("vendor", config.get("vendor", "mikrotik"))).lower()
    platform = str(device.get("platform", config.get("platform", "routeros"))).lower()
    return vendor, platform


def get_password(config: Dict[str, Any]) -> str:
    if config.get("password"):
        return str(config["password"])
    password = getpass.getpass("Please input SSH password: ")
    if not password:
        raise ValueError("SSH password is required.")
    return password


def make_check(name: str, result: str, details: str, output: str = "") -> Dict[str, Any]:
    return {
        "name": name,
        "result": result,
        "details": details,
        "output": output,
    }


def run_step(name: str, func: Callable[[], Any]) -> Dict[str, Any]:
    try:
        value = func()
        if isinstance(value, dict) and "result" in value:
            return make_check(
                name,
                str(value["result"]),
                str(value.get("details", "")),
                str(value.get("raw_output", "")),
            )
        return make_check(name, "PASS", "Command completed.", str(value))
    except Exception as error:
        return make_check(name, "FAIL", f"{type(error).__name__}: {error}")


def parse_ping_for_vendor(vendor: str, output: str) -> Dict[str, Any]:
    if vendor == "cisco":
        return cisco_parser.parse_ping(output)
    return mikrotik_parser.parse_ping(output)


def build_text_report(report: Dict[str, Any], json_path: Path, txt_path: Path) -> str:
    divider = "=" * 72
    lines = [
        divider,
        "Experimental Cross-Platform Baseline",
        divider,
        f"Vendor: {report['vendor']}",
        f"Platform: {report['platform']}",
        f"Host: {report['host']}",
        f"Overall Result: {report['overall_result']}",
        "-" * 72,
    ]
    for check in report["checks"]:
        lines.append(f"{check['result']:<8} {check['name']}: {check['details']}")
    lines.extend(
        [
            "-" * 72,
            f"JSON: {json_path}",
            f"TXT: {txt_path}",
            divider,
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(report: Dict[str, Any]) -> Tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORT_DIR / f"cross_platform_{timestamp}_{report['overall_result']}.json"
    txt_path = REPORT_DIR / f"cross_platform_{timestamp}_{report['overall_result']}.txt"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    with txt_path.open("w", encoding="utf-8") as file:
        file.write(build_text_report(report, json_path, txt_path))

    return json_path, txt_path


def summarize_result(checks: List[Dict[str, Any]]) -> str:
    if any(check["result"] == "FAIL" for check in checks):
        return "FAIL"
    if any(check["result"] == "WARNING" for check in checks):
        return "WARNING"
    return "PASS"


def print_summary(report: Dict[str, Any], json_path: Path, txt_path: Path) -> None:
    print()
    print("=" * 72)
    print("Experimental Cross-Platform Baseline")
    print("=" * 72)
    print(f"Vendor: {report['vendor']}")
    print(f"Platform: {report['platform']}")
    print(f"Host: {report['host']}")
    print(f"Overall Result: {report['overall_result']}")
    print("-" * 72)
    for check in report["checks"]:
        print(f"{check['result']:<8} {check['name']}: {check['details']}")
    print("-" * 72)
    print(f"JSON report: {json_path}")
    print(f"TXT report: {txt_path}")
    print("=" * 72)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    try:
        config = load_config(config_path)
        config["password"] = get_password(config)
        vendor, platform = get_device_meta(config)
        device = create_device(config)
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    checks: List[Dict[str, Any]] = []
    try:
        device.connect()
        checks.append(make_check("ssh login", "PASS", "Authenticated successfully."))
        checks.append(run_step("get_identity", device.get_identity))
        checks.append(run_step("get_version", device.get_version))
        checks.append(run_step("get_interfaces", device.get_interfaces))
        checks.append(run_step("get_clock", device.get_clock))
        checks.append(run_step("check_ntp", device.check_ntp))

        ping_output = device.ping(args.target)
        ping_result = parse_ping_for_vendor(vendor, ping_output)
        checks.append(
            make_check(
                f"ping {args.target}",
                str(ping_result["result"]),
                str(ping_result.get("details", "")),
                ping_output,
            )
        )
    except Exception as error:
        checks.append(make_check("baseline run", "FAIL", f"{type(error).__name__}: {error}"))
    finally:
        device.close()

    report = {
        "vendor": vendor,
        "platform": platform,
        "host": str(config.get("host", config.get("router_ip", ""))),
        "overall_result": summarize_result(checks),
        "checks": checks,
    }
    json_path, txt_path = write_reports(report)
    print_summary(report, json_path, txt_path)

    return 0 if report["overall_result"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
