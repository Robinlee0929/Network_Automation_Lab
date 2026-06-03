import argparse
import html
import ipaddress
import json
import math
import os
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


DEFAULT_DIRECTION = "WAN_TO_LAN_DNAT"
DEFAULT_DURATION = 40
DEFAULT_PARALLEL = 4
DEFAULT_OMIT = 10
DEFAULT_RUNS = 3
DEFAULT_REGRESSION_RATIO = 0.90
DEFAULT_LAN_SERVER_IP = "192.168.88.254"
SUPPORTED_DIRECTIONS = {
    "WAN_TO_LAN_DNAT",
    "LAN_TO_WAN_DNAT_REPLY",
    "LAN_TO_WAN_ROUTING",
}
REPORT_JSON = "day9_performance_regression_report.json"
REPORT_HTML = "day9_performance_regression_report.html"
REPORT_TXT = "day9_performance_regression_report.txt"
ARCHIVE_DIR_NAME = "performance_regression"


def filesystem_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    resolved = str(path.resolve())
    if resolved.startswith("\\\\?\\"):
        return path
    return Path("\\\\?\\" + resolved)


def path_exists(path: Path) -> bool:
    return filesystem_path(path).exists()


def copy_file(src: Path, dst: Path) -> None:
    target = filesystem_path(dst)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(filesystem_path(src), target)


@dataclass
class Day9Config:
    device_name: str
    direction: str
    router_wan_ip: str
    lan_server_ip: str
    client_ip: Optional[str]
    duration: int
    parallel: int
    omit: int
    runs: int
    threshold_mbps: float
    baseline_mbps: Optional[float]
    regression_ratio: float
    output_dir: Path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Router Performance Regression Framework.",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        "-help",
        action="help",
        help="Show this help message and exit.",
    )
    parser.add_argument("--device-name")
    parser.add_argument("--direction")
    parser.add_argument("--router-wan-ip")
    parser.add_argument("--lan-server-ip")
    parser.add_argument("--client-ip")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL)
    parser.add_argument("--omit", type=int, default=DEFAULT_OMIT)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--threshold-mbps", type=float)
    parser.add_argument("--baseline-mbps", type=float)
    parser.add_argument(
        "--regression-ratio",
        type=float,
        default=DEFAULT_REGRESSION_RATIO,
    )
    parser.add_argument("--output-dir")
    return parser.parse_args(argv)


def sanitize_path_name(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("-", "_", ".") else "_" for char in value)
    return safe.strip("._") or "unknown_device"


def require_non_empty(value: str) -> str:
    if not value.strip():
        raise ValueError("value cannot be empty.")
    return value.strip()


def validate_ipv4(value: str, field_name: str) -> str:
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError as error:
        raise ValueError(f"{field_name} must be a valid IPv4 address.") from error
    if address.version != 4:
        raise ValueError(f"{field_name} must be a valid IPv4 address.")
    return str(address)


def validate_direction(value: str) -> str:
    direction = value.strip().upper()
    if direction not in SUPPORTED_DIRECTIONS:
        supported = ", ".join(sorted(SUPPORTED_DIRECTIONS))
        raise ValueError(f"direction must be one of: {supported}.")
    return direction


def validate_positive_int(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return value


def validate_non_negative_int(value: int, field_name: str) -> int:
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return value


def validate_positive_float(value: float, field_name: str) -> float:
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return value


def prompt_until_valid(
    prompt: str,
    validator: Callable[[str], Any],
    default: Optional[str] = None,
) -> Any:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            raw = default
        try:
            return validator(raw)
        except ValueError as error:
            print(f"Error: {error}")


def prompt_missing_args(args: argparse.Namespace) -> Day9Config:
    if args.device_name:
        device_name = require_non_empty(args.device_name)
    else:
        device_name = prompt_until_valid("Please input device name: ", require_non_empty)

    if args.direction:
        direction = validate_direction(args.direction)
    else:
        direction = prompt_until_valid(
            "Please input direction [WAN_TO_LAN_DNAT/LAN_TO_WAN_DNAT_REPLY/LAN_TO_WAN_ROUTING] "
            "(default: WAN_TO_LAN_DNAT): ",
            validate_direction,
            DEFAULT_DIRECTION,
        )

    if args.router_wan_ip:
        router_wan_ip = validate_ipv4(args.router_wan_ip, "--router-wan-ip")
    else:
        router_wan_ip = prompt_until_valid(
            "Please input Router WAN IP: ",
            lambda value: validate_ipv4(value, "Router WAN IP"),
        )

    if args.lan_server_ip:
        lan_server_ip = validate_ipv4(args.lan_server_ip, "--lan-server-ip")
    else:
        lan_server_ip = prompt_until_valid(
            "Please input LAN iperf3 server IP (default: 192.168.88.254): ",
            lambda value: validate_ipv4(value, "LAN iperf3 server IP"),
            DEFAULT_LAN_SERVER_IP,
        )

    client_ip = None
    if args.client_ip:
        client_ip = validate_ipv4(args.client_ip, "--client-ip")
    elif direction == "LAN_TO_WAN_ROUTING":
        client_ip = prompt_until_valid(
            "Please input WAN-side iperf3 server IP for LAN_TO_WAN_ROUTING: ",
            lambda value: validate_ipv4(value, "client IP"),
        )

    if args.threshold_mbps is None:
        threshold_mbps = prompt_until_valid(
            "Please input threshold Mbps: ",
            lambda value: validate_positive_float(float(value), "threshold Mbps"),
        )
    else:
        threshold_mbps = validate_positive_float(args.threshold_mbps, "--threshold-mbps")

    duration = validate_positive_int(args.duration, "--duration")
    parallel = validate_positive_int(args.parallel, "--parallel")
    omit = validate_non_negative_int(args.omit, "--omit")
    runs = validate_positive_int(args.runs, "--runs")
    regression_ratio = validate_positive_float(args.regression_ratio, "--regression-ratio")
    baseline_mbps = (
        validate_positive_float(args.baseline_mbps, "--baseline-mbps")
        if args.baseline_mbps is not None
        else None
    )
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path("reports") / sanitize_path_name(device_name)
    )

    return Day9Config(
        device_name=device_name,
        direction=direction,
        router_wan_ip=router_wan_ip,
        lan_server_ip=lan_server_ip,
        client_ip=client_ip,
        duration=duration,
        parallel=parallel,
        omit=omit,
        runs=runs,
        threshold_mbps=threshold_mbps,
        baseline_mbps=baseline_mbps,
        regression_ratio=regression_ratio,
        output_dir=output_dir,
    )


def build_config_from_args(args: argparse.Namespace) -> Day9Config:
    return prompt_missing_args(args)


def build_iperf3_command(config: Day9Config) -> List[str]:
    direction = validate_direction(config.direction)
    target_ip = config.router_wan_ip
    if direction == "LAN_TO_WAN_ROUTING":
        if not config.client_ip:
            raise ValueError("--client-ip is required for LAN_TO_WAN_ROUTING.")
        target_ip = config.client_ip

    command = [
        "iperf3",
        "-c",
        target_ip,
        "-t",
        str(config.duration),
        "-P",
        str(config.parallel),
    ]
    if direction == "LAN_TO_WAN_DNAT_REPLY":
        command.append("-R")
    command.extend(["-O", str(config.omit), "-J"])
    return command


def command_to_string(command: List[str]) -> str:
    return " ".join(command)


def console_color(text: Any, color_code: str) -> str:
    value = str(text)
    if not sys.stdout.isatty():
        return value
    return f"\033[{color_code}m{value}\033[0m"


def color_for_result(result: str) -> str:
    normalized = result.upper()
    if normalized == "PASS":
        return "32;1"
    if normalized == "WARNING":
        return "33;1"
    if normalized == "FAIL":
        return "31;1"
    return "37"


def console_result(result: str) -> str:
    return console_color(result, color_for_result(result))


def progress_countdown(
    stop_event: threading.Event,
    run_index: int,
    total_runs: int,
    seconds: int,
) -> None:
    remaining = max(seconds, 0)
    while remaining > 0 and not stop_event.is_set():
        message = (
            f"Run {run_index}/{total_runs} running... "
            f"{remaining:>3}s remaining"
        )
        if sys.stdout.isatty():
            print(f"\r{message}", end="", flush=True)
        else:
            print(message, flush=True)
        stop_event.wait(1)
        remaining -= 1
    if sys.stdout.isatty() and not stop_event.is_set():
        print("\riperf3 finishing...                       ", end="", flush=True)


def run_iperf3_command(
    command: List[str],
    timeout: int,
    run_index: int = 1,
    total_runs: int = 1,
    progress_seconds: int = 0,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if shutil.which(command[0]) is None:
        return None, (
            f"iperf3 executable was not found: {command[0]}. "
            "Install iperf3 or add it to PATH."
        )
    stop_event = threading.Event()
    progress_thread: Optional[threading.Thread] = None
    if progress_seconds > 0:
        progress_thread = threading.Thread(
            target=progress_countdown,
            args=(stop_event, run_index, total_runs, progress_seconds),
            daemon=True,
        )
        progress_thread.start()

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"iperf3 timeout after {timeout} seconds."
    except OSError as error:
        return None, f"{type(error).__name__}: {error}"
    finally:
        stop_event.set()
        if progress_thread:
            progress_thread.join(timeout=1)
            if sys.stdout.isatty():
                print("\r" + " " * 72 + "\r", end="", flush=True)

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        message = f"iperf3 failed with return code {completed.returncode}."
        return None, f"{message} stderr: {stderr}" if stderr else message

    try:
        return json.loads(completed.stdout), None
    except json.JSONDecodeError as error:
        return None, f"iperf3 JSON parse error: {error}"


def parse_iperf3_json(data: Dict[str, Any]) -> Dict[str, Any]:
    end = data.get("end")
    if not isinstance(end, dict):
        raise ValueError("iperf3 JSON is missing end object.")

    for section_name in ("sum_received", "sum_sent"):
        section = end.get(section_name)
        if not isinstance(section, dict):
            continue
        value = section.get("bits_per_second")
        if value is None:
            continue
        try:
            bps = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"iperf3 JSON field end.{section_name}.bits_per_second is not numeric."
            ) from error
        return {
            "throughput_mbps": bps / 1_000_000,
            "measured_field": f"end.{section_name}.bits_per_second",
        }

    raise ValueError(
        "iperf3 JSON is missing end.sum_received.bits_per_second and "
        "end.sum_sent.bits_per_second."
    )


def classify_run_result(
    throughput_mbps: float,
    threshold_mbps: float,
    baseline_mbps: Optional[float] = None,
    regression_ratio: float = DEFAULT_REGRESSION_RATIO,
) -> str:
    if throughput_mbps < threshold_mbps:
        return "FAIL"
    if baseline_mbps is not None and throughput_mbps < baseline_mbps * regression_ratio:
        return "WARNING"
    return "PASS"


def calculate_overall_result(runs: List[Dict[str, Any]]) -> str:
    results = [run.get("result") for run in runs]
    if "FAIL" in results:
        return "FAIL"
    if "WARNING" in results:
        return "WARNING"
    return "PASS"


def aggregate_results(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    throughputs = [
        float(run["throughput_mbps"])
        for run in runs
        if run.get("throughput_mbps") is not None
    ]
    average = sum(throughputs) / len(throughputs) if throughputs else 0
    variance = (
        sum((value - average) ** 2 for value in throughputs) / len(throughputs)
        if throughputs
        else 0
    )
    return {
        "average_mbps": round(average, 3),
        "min_mbps": round(min(throughputs), 3) if throughputs else 0,
        "max_mbps": round(max(throughputs), 3) if throughputs else 0,
        "standard_deviation_mbps": round(math.sqrt(variance), 3),
        "pass_count": sum(1 for run in runs if run.get("result") == "PASS"),
        "warning_count": sum(1 for run in runs if run.get("result") == "WARNING"),
        "fail_count": sum(1 for run in runs if run.get("result") == "FAIL"),
        "total_runs": len(runs),
        "overall_result": calculate_overall_result(runs),
    }


def build_report(config: Day9Config, aggregate: Dict[str, Any], runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    return {
        "metadata": {
            "day": "Performance Regression",
            "title": "Router Performance Regression Framework",
            "generated_at": generated_at,
            "device_name": config.device_name,
            "script": "performance_regression.py",
        },
        "config": {
            "direction": config.direction,
            "router_wan_ip": config.router_wan_ip,
            "lan_server_ip": config.lan_server_ip,
            "client_ip": config.client_ip,
            "duration": config.duration,
            "parallel": config.parallel,
            "omit": config.omit,
            "runs": config.runs,
            "threshold_mbps": config.threshold_mbps,
            "baseline_mbps": config.baseline_mbps,
            "regression_ratio": config.regression_ratio,
        },
        "aggregate": aggregate,
        "runs": runs,
    }


def report_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        "json": output_dir / REPORT_JSON,
        "html": output_dir / REPORT_HTML,
        "txt": output_dir / REPORT_TXT,
    }


def archive_timestamp(report: Dict[str, Any]) -> str:
    generated_at = str(report.get("metadata", {}).get("generated_at", ""))
    try:
        value = datetime.fromisoformat(generated_at)
    except ValueError:
        value = datetime.now()
    return value.strftime("%Y%m%d_%H%M%S")


def archived_report_paths(
    output_dir: Path,
    direction: str,
    overall_result: str,
    timestamp: str,
) -> Dict[str, Path]:
    archive_dir = output_dir / ARCHIVE_DIR_NAME
    stem = (
        f"{sanitize_path_name(direction.upper())}_"
        f"{sanitize_path_name(overall_result.upper())}_"
        f"{timestamp}"
    )
    return {
        "json_archive": archive_dir / f"{stem}.json",
        "html_archive": archive_dir / f"{stem}.html",
        "txt_archive": archive_dir / f"{stem}.txt",
    }


def write_json_report(report: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = report_paths(output_dir)["json"]
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return path


def result_class(value: str) -> str:
    normalized = value.lower()
    return "warning" if normalized == "warning" else normalized


def write_html_report(report: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = report_paths(output_dir)["html"]
    metadata = report["metadata"]
    config = report["config"]
    aggregate = report["aggregate"]
    overall_class = result_class(aggregate["overall_result"])
    baseline_text = "" if config.get("baseline_mbps") is None else str(config["baseline_mbps"])
    regression_floor = ""
    if config.get("baseline_mbps") is not None:
        regression_floor = str(round(config["baseline_mbps"] * config["regression_ratio"], 3))
    rows = []
    for run in report["runs"]:
        throughput = "" if run["throughput_mbps"] is None else str(run["throughput_mbps"])
        rows.append(
            "<tr>"
            f"<td class=\"run-index\">#{run['run_index']}</td>"
            f"<td>{html.escape(str(run['timestamp']))}</td>"
            f"<td class=\"number\">{html.escape(throughput)}</td>"
            f"<td><span class=\"badge {result_class(run['result'])}\">{html.escape(run['result'])}</span></td>"
            f"<td>{html.escape(str(run.get('measured_field') or ''))}</td>"
            f"<td>{html.escape(str(run.get('error_message') or ''))}</td>"
            f"<td><code>{html.escape(run['command'])}</code></td>"
            "</tr>"
        )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Router Performance Regression</title>
  <style>
    :root {{
      --bg: #f3f6fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #667085;
      --border: #d8e0ec;
      --ink: #111827;
      --pass: #147a3d;
      --pass-bg: #e8f6ee;
      --warning: #9a6700;
      --warning-bg: #fff4d8;
      --fail: #b42318;
      --fail-bg: #fdecec;
      --blue: #1d4ed8;
      --blue-bg: #dbeafe;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 48px; }}
    .hero {{
      background: linear-gradient(135deg, #102033 0%, #194f5d 52%, #256d5a 100%);
      color: #fff;
      border-radius: 8px;
      padding: 28px;
      box-shadow: 0 16px 34px rgba(16, 24, 40, .14);
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 22px;
      align-items: end;
    }}
    .eyebrow {{
      color: #bfdbfe;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    h1 {{ margin: 8px 0 10px; font-size: 32px; line-height: 1.12; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; color: #dbeafe; }}
    .hero-score {{ text-align: right; }}
    .score-value {{ font-size: 42px; font-weight: 850; line-height: 1; }}
    .score-label {{ margin-top: 7px; color: #dbeafe; font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 18px 0; }}
    .card, section {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 12px 28px rgba(16, 24, 40, .08);
    }}
    .card {{ padding: 16px; }}
    section {{ padding: 18px; margin-top: 16px; overflow: hidden; }}
    .card-label {{ color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .card-value {{ margin-top: 8px; font-size: 24px; font-weight: 850; overflow-wrap: anywhere; }}
    .card-sub {{ margin-top: 4px; color: var(--muted); font-size: 12px; }}
    .grid-two {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 10px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 750; }}
    tr:last-child th, tr:last-child td {{ border-bottom: 0; }}
    .kv th {{ width: 210px; }}
    .number {{ font-variant-numeric: tabular-nums; text-align: right; font-weight: 800; }}
    .run-index {{ font-weight: 850; }}
    code {{
      display: inline-block;
      max-width: 480px;
      padding: 3px 6px;
      border-radius: 6px;
      background: #f8fafc;
      color: #111827;
      font-family: Consolas, "Courier New", monospace;
      overflow-wrap: anywhere;
    }}
    .badge {{
      display: inline-block;
      min-width: 78px;
      padding: 4px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 850;
      text-align: center;
      white-space: nowrap;
    }}
    .pass {{ background: var(--pass-bg); color: var(--pass); }}
    .warning {{ background: var(--warning-bg); color: var(--warning); }}
    .fail {{ background: var(--fail-bg); color: var(--fail); }}
    .pill {{ display: inline-block; padding: 4px 9px; border-radius: 999px; background: var(--blue-bg); color: var(--blue); font-weight: 800; }}
    .criteria {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .criteria div {{ border: 1px solid var(--border); border-radius: 8px; padding: 12px; background: #fbfdff; }}
    @media (max-width: 820px) {{
      main {{ padding: 18px 12px 34px; }}
      .hero-grid, .cards, .grid-two, .criteria {{ grid-template-columns: 1fr; }}
      .hero-score {{ text-align: left; }}
      h1 {{ font-size: 26px; }}
      .score-value {{ font-size: 34px; }}
      code {{ max-width: 100%; }}
    }}
  </style>
</head>
<body>
<main>
  <header class="hero">
    <div class="hero-grid">
      <div>
        <div class="eyebrow">Network Automation Testing Platform</div>
        <h1>Router Performance Regression</h1>
        <div class="meta">
          <span>{html.escape(metadata['device_name'])}</span>
          <span>{html.escape(config['direction'])}</span>
          <span>Generated {html.escape(metadata['generated_at'])}</span>
        </div>
      </div>
      <div class="hero-score">
        <div><span class="badge {overall_class}">{html.escape(aggregate['overall_result'])}</span></div>
        <div class="score-value">{aggregate['average_mbps']}</div>
        <div class="score-label">Average Mbps</div>
      </div>
    </div>
  </header>

  <div class="cards">
    <article class="card"><div class="card-label">Minimum</div><div class="card-value">{aggregate['min_mbps']} Mbps</div><div class="card-sub">Lowest run</div></article>
    <article class="card"><div class="card-label">Maximum</div><div class="card-value">{aggregate['max_mbps']} Mbps</div><div class="card-sub">Highest run</div></article>
    <article class="card"><div class="card-label">Std Dev</div><div class="card-value">{aggregate['standard_deviation_mbps']}</div><div class="card-sub">Mbps spread</div></article>
    <article class="card"><div class="card-label">Runs</div><div class="card-value">{aggregate['total_runs']}</div><div class="card-sub">Pass {aggregate['pass_count']} / Warning {aggregate['warning_count']} / Fail {aggregate['fail_count']}</div></article>
  </div>

  <div class="grid-two">
  <section>
    <h2>Configuration</h2>
    <table class="kv">
      <tr><th>Device name</th><td>{html.escape(config['device_name'] if 'device_name' in config else metadata['device_name'])}</td></tr>
      <tr><th>Direction</th><td>{html.escape(config['direction'])}</td></tr>
      <tr><th>Router WAN IP</th><td>{html.escape(config['router_wan_ip'])}</td></tr>
      <tr><th>LAN server IP</th><td>{html.escape(config['lan_server_ip'])}</td></tr>
      <tr><th>Client IP</th><td>{html.escape(str(config.get('client_ip') or ''))}</td></tr>
      <tr><th>Duration</th><td>{config['duration']}</td></tr>
      <tr><th>Parallel streams</th><td>{config['parallel']}</td></tr>
      <tr><th>Omit seconds</th><td>{config['omit']}</td></tr>
      <tr><th>Runs</th><td>{config['runs']}</td></tr>
      <tr><th>Threshold Mbps</th><td>{config['threshold_mbps']}</td></tr>
      <tr><th>Baseline Mbps</th><td>{html.escape(baseline_text)}</td></tr>
      <tr><th>Regression ratio</th><td>{config['regression_ratio']}</td></tr>
      <tr><th>Regression floor</th><td>{html.escape(regression_floor)}</td></tr>
    </table>
  </section>
  <section>
    <h2>Aggregate</h2>
    <table class="kv">
      <tr><th>Average Mbps</th><td>{aggregate['average_mbps']}</td></tr>
      <tr><th>Min Mbps</th><td>{aggregate['min_mbps']}</td></tr>
      <tr><th>Max Mbps</th><td>{aggregate['max_mbps']}</td></tr>
      <tr><th>Standard deviation</th><td>{aggregate['standard_deviation_mbps']}</td></tr>
      <tr><th>Pass count</th><td>{aggregate['pass_count']}</td></tr>
      <tr><th>Warning count</th><td>{aggregate['warning_count']}</td></tr>
      <tr><th>Fail count</th><td>{aggregate['fail_count']}</td></tr>
      <tr><th>Overall result</th><td><span class="badge {result_class(aggregate['overall_result'])}">{aggregate['overall_result']}</span></td></tr>
    </table>
  </section>
  </div>

  <section>
    <h2>Regression Criteria</h2>
    <div class="criteria">
      <div><span class="badge pass">PASS</span><p>Throughput is at or above threshold and, when a baseline exists, at or above the regression floor.</p></div>
      <div><span class="badge warning">WARNING</span><p>Throughput is at or above threshold but below baseline multiplied by regression ratio.</p></div>
      <div><span class="badge fail">FAIL</span><p>Throughput is below threshold, or iperf3 execution/parsing failed.</p></div>
    </div>
  </section>

  <section>
    <h2>Runs</h2>
    <div class="table-wrap">
    <table>
      <tr><th>Run</th><th>Timestamp</th><th>Mbps</th><th>Result</th><th>Measured field</th><th>Error message</th><th>Command</th></tr>
      {''.join(rows)}
    </table>
    </div>
  </section>
</main>
</body>
</html>
"""
    with path.open("w", encoding="utf-8") as file:
        file.write(html_text)
    return path


def write_txt_report(
    report: Dict[str, Any],
    output_dir: Path,
    json_path: Path,
    html_path: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = report_paths(output_dir)["txt"]
    metadata = report["metadata"]
    config = report["config"]
    aggregate = report["aggregate"]
    lines = [
        "Router Performance Regression",
        f"Generated: {metadata['generated_at']}",
        f"Device Name: {metadata['device_name']}",
        f"Direction: {config['direction']}",
        f"Router WAN IP: {config['router_wan_ip']}",
        f"LAN Server IP: {config['lan_server_ip']}",
        f"Client IP: {config.get('client_ip') or ''}",
        f"Duration: {config['duration']}",
        f"Parallel Streams: {config['parallel']}",
        f"Omit Seconds: {config['omit']}",
        f"Runs: {config['runs']}",
        f"Threshold Mbps: {config['threshold_mbps']}",
        f"Baseline Mbps: {config.get('baseline_mbps') or ''}",
        f"Regression Ratio: {config['regression_ratio']}",
        f"Average Mbps: {aggregate['average_mbps']}",
        f"Min Mbps: {aggregate['min_mbps']}",
        f"Max Mbps: {aggregate['max_mbps']}",
        f"Standard Deviation Mbps: {aggregate['standard_deviation_mbps']}",
        f"Pass Count: {aggregate['pass_count']}",
        f"Warning Count: {aggregate['warning_count']}",
        f"Fail Count: {aggregate['fail_count']}",
        f"Total Runs: {aggregate['total_runs']}",
        f"Overall Result: {aggregate['overall_result']}",
        "",
        "Per-run Summary:",
    ]
    for run in report["runs"]:
        error = f" Error: {run['error_message']}" if run.get("error_message") else ""
        lines.append(
            f"Run {run['run_index']}: {run['throughput_mbps']} Mbps {run['result']}{error}"
        )
    lines.extend(
        [
            "",
            f"JSON report path: {json_path}",
            f"HTML report path: {html_path}",
            f"TXT report path: {path}",
        ]
    )
    with path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")
    return path


def write_reports(report: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    json_path = write_json_report(report, output_dir)
    html_path = write_html_report(report, output_dir)
    txt_path = write_txt_report(report, output_dir, json_path, html_path)
    archive_paths = archived_report_paths(
        output_dir,
        str(report["config"]["direction"]),
        str(report["aggregate"]["overall_result"]),
        archive_timestamp(report),
    )
    copy_file(json_path, archive_paths["json_archive"])
    copy_file(html_path, archive_paths["html_archive"])
    copy_file(txt_path, archive_paths["txt_archive"])
    return {
        "json": json_path,
        "html": html_path,
        "txt": txt_path,
        **archive_paths,
    }


def make_run_result(
    config: Day9Config,
    run_index: int,
    command: List[str],
    throughput_mbps: Optional[float],
    measured_field: str,
    result: str,
    error_message: str = "",
) -> Dict[str, Any]:
    return {
        "run_index": run_index,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "device_name": config.device_name,
        "direction": config.direction,
        "command": command_to_string(command),
        "measured_field": measured_field,
        "throughput_mbps": round(throughput_mbps, 3) if throughput_mbps is not None else None,
        "threshold_mbps": config.threshold_mbps,
        "baseline_mbps": config.baseline_mbps,
        "regression_ratio": config.regression_ratio,
        "result": result,
        "error_message": error_message,
    }


def print_run_start(index: int, total_runs: int, command: List[str]) -> None:
    print()
    print(console_color("-" * 72, "36"))
    print(console_color(f"Run {index}/{total_runs}", "36;1"))
    print(f"Command: {command_to_string(command)}")


def print_run_result(run: Dict[str, Any]) -> None:
    value = run["throughput_mbps"] if run["throughput_mbps"] is not None else "N/A"
    result = console_result(str(run["result"]))
    print(
        f"Run {run['run_index']} summary: "
        f"{console_color(value, '32;1' if run['result'] == 'PASS' else '37')} Mbps "
        f"{result}"
    )
    if run.get("measured_field"):
        print(f"Measured field: {run['measured_field']}")
    if run.get("error_message"):
        print(f"Error: {console_color(run['error_message'], '31;1')}")


def run_regression(config: Day9Config) -> Tuple[Dict[str, Any], Dict[str, Path]]:
    command = build_iperf3_command(config)
    runs = []
    timeout = config.duration + config.omit + 30
    print(console_color("iperf3 command:", "36;1"), command_to_string(command))

    for index in range(1, config.runs + 1):
        print_run_start(index, config.runs, command)
        raw_json, error = run_iperf3_command(
            command,
            timeout=timeout,
            run_index=index,
            total_runs=config.runs,
            progress_seconds=config.duration + config.omit,
        )
        if error:
            run = make_run_result(
                config,
                index,
                command,
                None,
                "",
                "FAIL",
                error,
            )
            runs.append(run)
            print_run_result(run)
            continue
        try:
            assert raw_json is not None
            parsed = parse_iperf3_json(raw_json)
            throughput = float(parsed["throughput_mbps"])
            result = classify_run_result(
                throughput,
                config.threshold_mbps,
                config.baseline_mbps,
                config.regression_ratio,
            )
            run = make_run_result(
                config,
                index,
                command,
                throughput,
                parsed["measured_field"],
                result,
            )
            runs.append(run)
            print_run_result(run)
        except (AssertionError, ValueError) as parse_error:
            run = make_run_result(
                config,
                index,
                command,
                None,
                "",
                "FAIL",
                str(parse_error),
            )
            runs.append(run)
            print_run_result(run)

    aggregate = aggregate_results(runs)
    report = build_report(config, aggregate, runs)
    paths = write_reports(report, config.output_dir)
    return report, paths


def print_console_summary(report: Dict[str, Any], paths: Dict[str, Path]) -> None:
    config = report["config"]
    aggregate = report["aggregate"]
    print(console_color("=" * 72, "36"))
    print(console_color("Router Performance Regression", "1"))
    print(console_color("=" * 72, "36"))
    print()
    print(f"Device Name: {report['metadata']['device_name']}")
    print(f"Direction: {config['direction']}")
    print(f"Runs: {config['runs']}")
    print(f"Threshold Mbps: {config['threshold_mbps']}")
    print(f"Baseline Mbps: {config['baseline_mbps'] if config['baseline_mbps'] is not None else ''}")
    print(f"Regression Ratio: {config['regression_ratio']:.2f}")
    print("-" * 22)
    print()
    for run in report["runs"]:
        value = run["throughput_mbps"] if run["throughput_mbps"] is not None else "N/A"
        print(f"Run {run['run_index']}: {value} Mbps {console_result(str(run['result']))}")
        if run.get("error_message"):
            print(f"  Error: {console_color(run['error_message'], '31;1')}")
    print(console_color("-" * 22, "36"))
    print()
    print(f"Average: {aggregate['average_mbps']} Mbps")
    print(f"Min: {aggregate['min_mbps']} Mbps")
    print(f"Max: {aggregate['max_mbps']} Mbps")
    print(f"Overall Result: {console_result(str(aggregate['overall_result']))}")
    print(console_color("-" * 20, "36"))
    print()
    print("Latest reports:")
    print(f"JSON report: {paths['json']}")
    print(f"HTML report: {paths['html']}")
    print(f"TXT report: {paths['txt']}")
    print()
    print("Archived reports:")
    print(f"JSON archive: {paths['json_archive']}")
    print(f"HTML archive: {paths['html_archive']}")
    print(f"TXT archive: {paths['txt_archive']}")
    print(console_color("=" * 72, "36"))


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(argv)
        config = build_config_from_args(args)
        report, paths = run_regression(config)
        print_console_summary(report, paths)
        return 0 if report["aggregate"]["overall_result"] == "PASS" else 1
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as error:
        print(str(error))
        return 1


if __name__ == "__main__":
    sys.exit(main())
