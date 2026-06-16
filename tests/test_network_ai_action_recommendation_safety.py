import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NODE_SAFETY_CHECK = r"""
const fs = require("fs");
const path = require("path");
const ts = require("typescript");
const vm = require("vm");

const cache = new Map();

function loadTs(relativePath) {
  const filename = path.resolve(relativePath);
  if (cache.has(filename)) {
    return cache.get(filename).exports;
  }

  const source = fs.readFileSync(filename, "utf8");
  const compiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
      esModuleInterop: true
    }
  }).outputText;

  const module = { exports: {} };
  cache.set(filename, module);
  const sandbox = {
    module,
    exports: module.exports,
    console,
    process,
    require: (request) => {
      if (request === "@/lib/ai/openaiClient") {
        return {
          getOpenAIClient: () => {
            throw new Error("OpenAI client should not be called by safety tests.");
          },
          getOpenAIModel: () => "gpt-5-mini"
        };
      }
      if (request.startsWith("./")) {
        return loadTs(path.resolve(path.dirname(filename), `${request}.ts`));
      }
      return require(request);
    }
  };

  vm.runInNewContext(compiled, sandbox, { filename });
  return module.exports;
}

const aiNode = loadTs("lib/network-ai/aiNode.ts");
const jobs = loadTs("lib/network-ai/jobs.ts");

function baseOutput(riskLevel = "low") {
  return {
    summary: "Report summary",
    findings: [],
    warnings: [],
    possibleCauses: [],
    recommendedActions: [],
    recommendedExistingActionIds: [
      "baseline_check",
      "environment_check",
      "not_real_action"
    ],
    riskLevel,
    requiresApproval: false,
    needsHumanReview: false
  };
}

const phase = aiNode.sanitizeAnalyzeReportOutput(baseOutput(), {
  resultKind: "phase_gate_report",
  targetDevice: "N/A"
});
const summary = aiNode.sanitizeAnalyzeReportOutput(baseOutput(), {
  resultKind: "summary_report",
  deviceName: null
});
const testReport = aiNode.sanitizeAnalyzeReportOutput(baseOutput(), {
  resultKind: "test_report",
  targetDevice: ""
});
const device = aiNode.sanitizeAnalyzeReportOutput(baseOutput(), {
  resultKind: "device_report",
  targetDevice: "core-switch"
});
const medium = aiNode.sanitizeAnalyzeReportOutput(baseOutput("medium"), {
  resultKind: "device_report",
  targetDevice: "core-switch"
});
const blockedJob = jobs.createNetworkJob({
  actionId: "baseline_check",
  params: { source: "test" }
}).job;

process.stdout.write(JSON.stringify({
  phase,
  summary,
  testReport,
  device,
  medium,
  blockedJob,
  warning: aiNode.NON_DEVICE_ACTION_WARNING
}));
"""


def run_safety_check(tmp_path: Path) -> dict:
    env = os.environ.copy()
    env["NETWORK_AI_JOB_STORE_PATH"] = str(tmp_path / "jobs.json")
    completed = subprocess.run(
        ["node", "-e", NODE_SAFETY_CHECK],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_phase_gate_report_analyze_recommendations_are_removed(tmp_path):
    result = run_safety_check(tmp_path)

    assert result["phase"]["recommendedExistingActionIds"] == []
    assert result["phase"]["needsHumanReview"] is True
    assert result["warning"] in result["phase"]["warnings"]


def test_summary_report_analyze_recommendations_are_removed(tmp_path):
    result = run_safety_check(tmp_path)

    assert result["summary"]["recommendedExistingActionIds"] == []
    assert result["summary"]["needsHumanReview"] is True
    assert result["warning"] in result["summary"]["warnings"]


def test_test_report_analyze_recommendations_are_removed(tmp_path):
    result = run_safety_check(tmp_path)

    assert result["testReport"]["recommendedExistingActionIds"] == []
    assert result["testReport"]["needsHumanReview"] is True
    assert result["warning"] in result["testReport"]["warnings"]


def test_device_report_with_target_keeps_only_allowlisted_action_ids(tmp_path):
    result = run_safety_check(tmp_path)

    assert result["device"]["recommendedExistingActionIds"] == [
        "baseline_check",
        "environment_check",
    ]
    assert result["warning"] not in result["device"]["warnings"]


def test_medium_risk_analyze_requires_approval_and_human_review(tmp_path):
    result = run_safety_check(tmp_path)

    assert result["medium"]["riskLevel"] == "medium"
    assert result["medium"]["needsHumanReview"] is True
    assert result["medium"]["requiresApproval"] is True


def test_job_create_with_action_id_but_missing_target_device_is_blocked(tmp_path):
    result = run_safety_check(tmp_path)
    job = result["blockedJob"]

    assert job["actionId"] == "baseline_check"
    assert job["targetDevice"] is None
    assert job["status"] == "blocked"
    assert job["blockedReason"] == "Missing targetDevice"
