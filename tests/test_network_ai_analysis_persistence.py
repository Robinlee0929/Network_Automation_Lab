import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NODE_ANALYSIS_PERSISTENCE = r"""
(async () => {
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
    Request,
    Response,
    require: (request) => {
      if (request === "next/server") {
        return {
          NextResponse: {
            json: (body, init) => Response.json(body, init)
          }
        };
      }
      if (request === "@/lib/ai/openaiClient") {
        return {
          getOpenAIClient: () => {
            throw new Error("OpenAI client should not be called by persistence tests.");
          },
          getOpenAIModel: () => "gpt-5-mini"
        };
      }
      if (request === "@/lib/network-ai/analysisStore") {
        return loadTs("lib/network-ai/analysisStore.ts");
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
const store = loadTs("lib/network-ai/analysisStore.ts");
const latestRoute = loadTs("app/api/network/reports/[reportId]/analysis/latest/route.ts");

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

store.clearAnalysisStoreForTests();

const phase = aiNode.sanitizeAnalyzeReportResult(baseOutput(), {
  sourceDay: "Day160",
  resultKind: "phase_gate_report",
  targetDevice: "N/A",
  checkType: "phase-gate-review"
});
const summary = aiNode.sanitizeAnalyzeReportResult(baseOutput(), {
  sourceDay: "Day13",
  resultKind: "summary_report",
  targetDevice: null,
  checkType: "lab-summary"
});
const testReport = aiNode.sanitizeAnalyzeReportResult(baseOutput(), {
  resultKind: "test_report",
  targetDevice: ""
});
const device = aiNode.sanitizeAnalyzeReportResult(baseOutput(), {
  sourceDay: "Day5",
  resultKind: "device_report",
  targetDevice: "core-switch",
  checkType: "interface_status"
});
const medium = aiNode.sanitizeAnalyzeReportResult(baseOutput("medium"), {
  resultKind: "device_report",
  targetDevice: "core-switch"
});

const phaseRecord = store.createAnalysisRecord({
  reportId: "phase-report-1",
  reportText: "phase gate review",
  deviceContext: {
    sourceDay: "Day160",
    resultKind: "phase_gate_report",
    targetDevice: "N/A",
    checkType: "phase-gate-review"
  },
  model: "gpt-5-mini",
  promptVersion: aiNode.NETWORK_ANALYZE_PROMPT_VERSION,
  output: phase.output,
  safety: phase.safety
});

const deviceRecord = store.createAnalysisRecord({
  reportId: "device-report-1",
  reportText: "Cisco IOS interface status",
  deviceContext: {
    sourceDay: "Day5",
    resultKind: "device_report",
    targetDevice: "core-switch",
    checkType: "interface_status"
  },
  model: "gpt-5-mini",
  promptVersion: aiNode.NETWORK_ANALYZE_PROMPT_VERSION,
  output: device.output,
  safety: device.safety
});

const latestResponse = await latestRoute.GET(new Request("http://local"), {
  params: Promise.resolve({ reportId: "phase-report-1" })
});
const latestPayload = await latestResponse.json();
const missingResponse = await latestRoute.GET(new Request("http://local"), {
  params: Promise.resolve({ reportId: "missing-report" })
});
const missingPayload = await missingResponse.json();

process.stdout.write(JSON.stringify({
  phase,
  summary,
  testReport,
  device,
  medium,
  phaseRecord,
  deviceRecord,
  latestPayload,
  missingPayload,
  latestDirect: store.getLatestAnalysisForReport("phase-report-1")
}));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""


def run_persistence_check(tmp_path: Path) -> dict:
    env = os.environ.copy()
    env["NETWORK_AI_ANALYSIS_STORE_PATH"] = str(tmp_path / "analyses.json")
    completed = subprocess.run(
        ["node", "-e", NODE_ANALYSIS_PERSISTENCE],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_ai_analyze_creates_analysis_record_and_latest_api_reads_it(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["phaseRecord"]["reportId"] == "phase-report-1"
    assert result["phaseRecord"]["promptVersion"] == "network-analyze-report-v2"
    assert result["latestPayload"]["analysis"]["id"] == result["phaseRecord"]["id"]


def test_latest_analysis_survives_client_state_loss_model(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["latestDirect"]["id"] == result["phaseRecord"]["id"]
    assert result["latestDirect"]["output"]["summary"] == "Report summary"


def test_nonexistent_report_latest_analysis_returns_null(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["missingPayload"]["analysis"] is None


def test_non_device_reports_clear_recommended_existing_action_ids(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["phase"]["output"]["recommendedExistingActionIds"] == []
    assert result["summary"]["output"]["recommendedExistingActionIds"] == []
    assert result["testReport"]["output"]["recommendedExistingActionIds"] == []
    assert result["phase"]["safety"]["jobCreationAllowed"] is False
    assert result["summary"]["safety"]["jobCreationAllowed"] is False
    assert result["testReport"]["safety"]["jobCreationAllowed"] is False


def test_device_report_with_target_allows_only_allowlisted_action_ids(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["device"]["output"]["recommendedExistingActionIds"] == [
        "baseline_check",
        "environment_check",
    ]
    assert result["device"]["safety"]["jobCreationAllowed"] is True
    assert result["device"]["safety"]["recommendedActionIdsSanitized"] is True


def test_medium_high_risk_with_human_review_requires_approval(tmp_path):
    result = run_persistence_check(tmp_path)

    assert result["medium"]["output"]["riskLevel"] == "medium"
    assert result["medium"]["output"]["needsHumanReview"] is True
    assert result["medium"]["output"]["requiresApproval"] is True
