import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NODE_NORMALIZER = r"""
const fs = require("fs");
const ts = require("typescript");
const vm = require("vm");

const source = fs.readFileSync("lib/network-ai/dayResults.ts", "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
    esModuleInterop: true
  }
}).outputText;

const sandbox = {
  exports: {},
  require,
  process,
  console
};
sandbox.module = { exports: sandbox.exports };
vm.runInNewContext(compiled, sandbox);

const cases = JSON.parse(fs.readFileSync(process.env.CASES_FILE, "utf8"));
const results = cases.map((item) => {
  const rawOutput = item.rawOutput || JSON.stringify(item.raw);
  return sandbox.exports.normalizeDayResult({
    filePath: item.filePath,
    rawOutput,
    parsedResult: item.raw,
    createdAt: "2026-06-16T00:00:00.000Z",
    mtimeMs: 1
  });
});
process.stdout.write(JSON.stringify(results));
"""


def normalize_cases(tmp_path: Path, cases: list[dict]) -> list[dict]:
    case_payload = []
    for index, case in enumerate(cases):
        report_path = tmp_path / case["path"]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        raw_output = case.get("rawOutput") or json.dumps(case["raw"])
        report_path.write_text(raw_output, encoding="utf-8")
        case_payload.append(
            {
                "filePath": str(report_path),
                "raw": case["raw"],
                "rawOutput": raw_output,
            }
        )

    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(case_payload), encoding="utf-8")

    env = os.environ.copy()
    env["CASES_FILE"] = str(cases_file)
    completed = subprocess.run(
        ["node", "-e", NODE_NORMALIZER],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_day_id_and_day_number_fallbacks(tmp_path):
    day_id_result, day_number_result = normalize_cases(
        tmp_path,
        [
            {
                "path": "reports/no-day-in-path.json",
                "raw": {
                    "day_id": "Day100",
                    "task": "parser-phase-gate-review",
                    "status": "PASS",
                },
            },
            {
                "path": "reports/plain-report.json",
                "raw": {"day": 42, "task": "baseline_check", "status": "PASS"},
            },
        ],
    )

    assert day_id_result["sourceDay"] == "Day100"
    assert day_id_result["dayLabel"] == "Day100"
    assert day_number_result["sourceDay"] == "Day42"
    assert day_number_result["dayLabel"] == "Day42"


def test_phase_gate_and_summary_reports_are_not_device_reports(tmp_path):
    phase_result, summary_result = normalize_cases(
        tmp_path,
        [
            {
                "path": "reports/day160_ai_phase_gate.json",
                "raw": {
                    "day": 160,
                    "task": "v05-ai-assistance-phase-gate-review",
                    "vendor": "mikrotik",
                    "status": "REVIEW_READY",
                },
            },
            {
                "path": "summary/day13_lab_summary.json",
                "raw": {
                    "day_id": "Day13",
                    "title": "Multi-router WireGuard summary",
                    "vendor": "cisco",
                    "overall_status": "PASS",
                },
            },
        ],
    )

    assert phase_result["resultKind"] == "phase_gate_report"
    assert phase_result["deviceName"] is None
    assert summary_result["resultKind"] == "summary_report"
    assert summary_result["deviceName"] is None


def test_vendor_inference_for_cisco_and_mikrotik(tmp_path):
    mikrotik_result, cisco_result = normalize_cases(
        tmp_path,
        [
            {
                "path": "reports/day4_routeros.txt",
                "raw": {"deviceName": "hex-s-lab01", "status": "PASS"},
                "rawOutput": "RouterOS interface status PASS",
            },
            {
                "path": "reports/day5_cisco.txt",
                "raw": {"hostname": "core-switch", "status": "PASS"},
                "rawOutput": "Cisco IOS show interfaces status PASS",
            },
        ],
    )

    assert mikrotik_result["vendor"] == "mikrotik"
    assert cisco_result["vendor"] == "cisco"


def test_unknown_day_fallback(tmp_path):
    [result] = normalize_cases(
        tmp_path,
        [
            {
                "path": "reports/no-day-here.json",
                "raw": {"task": "misc-report", "status": "UNKNOWN"},
            }
        ],
    )

    assert result["sourceDay"] is None
    assert result["dayLabel"] == "Unknown Day"
