import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NODE_WORKFLOW_PERSISTENCE = r"""
(async () => {
const fs = require("fs");
const path = require("path");
const ts = require("typescript");
const vm = require("vm");

const cache = new Map();

function matchedOutput(overrides = {}) {
  return {
    intent: "run_check",
    targetDevice: "HEX-S-2025-LAB01",
    vendor: "mikrotik",
    interfaceName: null,
    vlanId: null,
    recommendedActionId: "wan_lan_check",
    missingFields: [],
    riskLevel: "low",
    requiresApproval: false,
    blocked: false,
    jobCreationAllowed: true,
    blockedReason: null,
    notes: ["Phase 1 parse result"],
    ...overrides
  };
}

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
      if (request === "@/lib/ai/routeHandler") {
        return {
          aiError: (error) => Response.json({ error: error.message }, { status: 500 }),
          validationError: (error) => Response.json({ error }, { status: 400 })
        };
      }
      if (request === "@/lib/network-ai/aiNode") {
        return {
          parseNetworkRequestWithAi: async (input) => ({
            nodeType: "network_request_parser",
            draftNotice: "draft",
            model: "gpt-5-mini",
            output: matchedOutput(),
            rawJson: JSON.stringify(matchedOutput(), null, 2),
            input
          })
        };
      }
      if (request === "@/lib/network-ai/parseResultStore") {
        return loadTs("lib/network-ai/parseResultStore.ts");
      }
      if (request === "@/lib/network-ai/providerDemo") {
        return loadTs("lib/network-ai/providerDemo.ts");
      }
      if (request === "@/lib/network-ai/jobs") {
        return loadTs("lib/network-ai/jobs.ts");
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

const parseStore = loadTs("lib/network-ai/parseResultStore.ts");
const jobs = loadTs("lib/network-ai/jobs.ts");
const parseRoute = loadTs("app/api/network/ai/parse-request/route.ts");
const latestRoute = loadTs("app/api/network/ai/parse-request/latest/route.ts");
const createRoute = loadTs("app/api/network/jobs/create/route.ts");
const jobsRoute = loadTs("app/api/network/jobs/route.ts");

parseStore.clearParseResultStoreForTests();
jobs.clearNetworkJobStoreForTests();

const missingLatestResponse = await latestRoute.GET();
const missingLatestPayload = await missingLatestResponse.json();

const inventory = {
  devices: [
    {
      name: "HEX-S-2025-LAB01",
      vendor: "mikrotik",
      managementIp: "192.168.88.10"
    }
  ]
};

process.env.NETWORK_AI_PROVIDER_DEMO_ENABLED = "0";
const disabledResponse = await parseRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({ userRequest: "Check LAB-DEMO-ROUTER" })
  })
);
const disabledPayload = await disabledResponse.json();

process.env.NETWORK_AI_PROVIDER_DEMO_ENABLED = "1";
const emptyResponse = await parseRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({ userRequest: "   " })
  })
);
const emptyPayload = await emptyResponse.json();

const oversizedResponse = await parseRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({ userRequest: "x".repeat(501) })
  })
);
const oversizedPayload = await oversizedResponse.json();

const expandedBodyResponse = await parseRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({
      userRequest: "Check LAB-DEMO-ROUTER",
      availableActions: [{ id: "reboot_device" }],
      command: "/system reboot"
    })
  })
);
const expandedBodyPayload = await expandedBodyResponse.json();

const parseResponse = await parseRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({
      userRequest: "請幫我檢查 HEX-S-2025-LAB01 的 WAN/LAN 狀態"
    })
  })
);
const parsePayload = await parseResponse.json();
const storedParseResult = parseStore.getLatestParseResultRecord();

const latestResponse = await latestRoute.GET();
const latestPayload = await latestResponse.json();

const createResponse = await createRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({
      actionId: parsePayload.parseResult.output.recommendedActionId,
      targetDevice: storedParseResult.output.targetDevice,
      vendor: storedParseResult.output.vendor,
      deviceInventory: inventory,
      params: {
        source: "ai-actions",
        parseResultId: storedParseResult.id,
        intent: parsePayload.parseResult.output.intent
      }
    })
  })
);
const createPayload = await createResponse.json();

const jobsResponse = await jobsRoute.GET();
const jobsPayload = await jobsResponse.json();

const commandResponse = await createRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({
      actionId: "wan_lan_check",
      targetDevice: "HEX-S-2025-LAB01",
      vendor: "mikrotik",
      command: "/system reboot",
      deviceInventory: inventory
    })
  })
);
const commandPayload = await commandResponse.json();

const mismatch = jobs.createNetworkJob({
  actionId: "wan_lan_check",
  targetDevice: "HEX-S-2025-LAB01",
  vendor: "mikrotik",
  deviceInventory: { devices: [{ name: "core-switch", vendor: "cisco" }] },
  params: { source: "direct-test", parseResultId: storedParseResult.id }
}).job;

process.stdout.write(JSON.stringify({
  disabledStatus: disabledResponse.status,
  disabledPayload,
  emptyStatus: emptyResponse.status,
  emptyPayload,
  oversizedStatus: oversizedResponse.status,
  oversizedPayload,
  expandedBodyStatus: expandedBodyResponse.status,
  expandedBodyPayload,
  missingLatestPayload,
  parsePayload,
  storedParseResult,
  latestPayload,
  createPayload,
  jobsPayload,
  commandStatus: commandResponse.status,
  commandPayload,
  mismatch,
  parseStoreFile: JSON.parse(fs.readFileSync(process.env.NETWORK_AI_PARSE_RESULT_STORE_PATH, "utf8")),
  jobStoreFile: JSON.parse(fs.readFileSync(process.env.NETWORK_AI_JOB_STORE_PATH, "utf8"))
}));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""


def run_workflow_check(tmp_path: Path) -> dict:
    env = os.environ.copy()
    env["NETWORK_AI_PARSE_RESULT_STORE_PATH"] = str(tmp_path / "parse-results.json")
    env["NETWORK_AI_JOB_STORE_PATH"] = str(tmp_path / "jobs.json")
    env["NETWORK_AI_PROVIDER_DEMO_ENABLED"] = "1"
    completed = subprocess.run(
        ["node", "-e", NODE_WORKFLOW_PERSISTENCE],
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_parse_request_post_creates_persistent_record_and_latest_api_reads_it(tmp_path):
    result = run_workflow_check(tmp_path)

    parse_result = result["parsePayload"]["parseResult"]
    assert parse_result["output"]["jobCreationAllowed"] is True
    assert parse_result["output"]["blockedReason"] is None
    assert "id" not in parse_result
    assert "userRequest" not in parse_result
    assert "deviceInventorySnapshot" not in parse_result
    assert result["latestPayload"]["parseResult"] == parse_result
    assert result["storedParseResult"]["id"].startswith("parse_")
    assert result["storedParseResult"]["userRequest"] == (
        "請幫我檢查 HEX-S-2025-LAB01 的 WAN/LAN 狀態"
    )
    assert result["parseStoreFile"][0]["id"] == result["storedParseResult"]["id"]
    assert result["parseStoreFile"][0]["deviceInventorySnapshot"]["context"] == "synthetic-local-demo-only"


def test_parse_request_route_requires_opt_in_and_rejects_invalid_or_expanded_input(tmp_path):
    result = run_workflow_check(tmp_path)

    assert result["disabledStatus"] == 400
    assert "disabled" in result["disabledPayload"]["error"]
    assert result["emptyStatus"] == 400
    assert result["emptyPayload"]["error"] == "userRequest is required."
    assert result["oversizedStatus"] == 400
    assert "500 characters or fewer" in result["oversizedPayload"]["error"]
    assert result["expandedBodyStatus"] == 400
    assert result["expandedBodyPayload"]["error"] == (
        "Only userRequest is accepted by the local recommendation preview."
    )


def test_latest_parse_result_returns_null_when_store_is_empty(tmp_path):
    result = run_workflow_check(tmp_path)

    assert result["missingLatestPayload"]["parseResult"] is None


def test_create_job_from_allowed_parse_result_persists_and_jobs_api_lists_it(tmp_path):
    result = run_workflow_check(tmp_path)

    parse_result = result["parsePayload"]["parseResult"]
    job = result["createPayload"]["job"]
    jobs_payload = result["jobsPayload"]["jobs"]

    assert job["actionId"] == "wan_lan_check"
    assert job["targetDevice"] == "HEX-S-2025-LAB01"
    assert job["vendor"] == "mikrotik"
    assert job["status"] == "ready"
    assert job["riskLevel"] == "low"
    assert job["requiresApproval"] is False
    assert job["source"] == "ai-actions"
    assert job["parseResultId"] == result["storedParseResult"]["id"]
    assert jobs_payload[0]["id"] == job["id"]
    assert any(stored_job["id"] == job["id"] for stored_job in result["jobStoreFile"])


def test_create_job_rejects_command_and_direct_inventory_mismatch_is_blocked(tmp_path):
    result = run_workflow_check(tmp_path)

    assert result["commandStatus"] == 400
    assert "command and scriptPath are not accepted" in result["commandPayload"]["error"]
    assert result["mismatch"]["status"] == "blocked"
    assert result["mismatch"]["blockedReason"] == "Target device not found in inventory or missing connection details"
