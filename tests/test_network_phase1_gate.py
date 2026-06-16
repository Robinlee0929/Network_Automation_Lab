import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


NODE_PHASE1_CHECK = r"""
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
      if (request === "@/lib/ai/routeHandler") {
        return {
          validationError: (error) => Response.json({ error }, { status: 400 })
        };
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

const readiness = loadTs("lib/network-ai/readiness.ts");
const jobs = loadTs("lib/network-ai/jobs.ts");
const schemas = loadTs("lib/network-ai/schemas.ts");
const createRoute = loadTs("app/api/network/jobs/create/route.ts");

function parseOutput(overrides) {
  return {
    intent: "run_check",
    targetDevice: "HEX-S-2025-LAB01",
    vendor: "unknown",
    interfaceName: null,
    vlanId: null,
    recommendedActionId: "wan_lan_check",
    missingFields: ["interfaceName", "vlanId", "evidence"],
    riskLevel: "low",
    requiresApproval: false,
    blocked: false,
    jobCreationAllowed: false,
    blockedReason: null,
    notes: [],
    ...overrides
  };
}

const missingInventoryWanLan = readiness.sanitizeParseRequestResult({
  output: parseOutput({}),
  userRequest: "請幫我檢查 HEX-S-2025-LAB01 的 WAN/LAN 狀態",
  deviceInventory: { devices: [{ name: "core-switch", vendor: "cisco" }] }
});

const matchedWanLan = readiness.sanitizeParseRequestResult({
  output: parseOutput({}),
  userRequest: "請幫我檢查 HEX-S-2025-LAB01 的 WAN/LAN 狀態",
  deviceInventory: {
    devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik", managementIp: "192.168.88.10" }]
  }
});

const baseline = readiness.sanitizeParseRequestResult({
  output: parseOutput({ recommendedActionId: "baseline_check" }),
  userRequest: "baseline check HEX-S-2025-LAB01",
  deviceInventory: {
    devices: [{ deviceName: "HEX-S-2025-LAB01", vendor: "mikrotik" }]
  }
});

const environment = readiness.sanitizeParseRequestResult({
  output: parseOutput({ recommendedActionId: "environment_check" }),
  userRequest: "environment check HEX-S-2025-LAB01",
  deviceInventory: {
    devices: [{ hostname: "HEX-S-2025-LAB01", vendor: "mikrotik" }]
  }
});

const vlanMissing = readiness.sanitizeParseRequestResult({
  output: parseOutput({
    intent: "change_access_vlan",
    recommendedActionId: null,
    interfaceName: null,
    vlanId: null,
    requiresApproval: false
  }),
  userRequest: "change access vlan on HEX-S-2025-LAB01",
  deviceInventory: {
    devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }]
  }
});

const backup = readiness.sanitizeParseRequestResult({
  output: parseOutput({
    intent: "backup_config",
    recommendedActionId: "backup_config"
  }),
  userRequest: "backup config HEX-S-2025-LAB01",
  deviceInventory: {
    devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }]
  }
});

const unknownActionJob = jobs.createNetworkJob({
  actionId: "not_real_action",
  targetDevice: "HEX-S-2025-LAB01",
  deviceInventory: { devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }] }
}).job;
const missingTargetJob = jobs.createNetworkJob({
  actionId: "wan_lan_check",
  deviceInventory: { devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }] }
}).job;
const inventoryMismatchJob = jobs.createNetworkJob({
  actionId: "wan_lan_check",
  targetDevice: "HEX-S-2025-LAB01",
  deviceInventory: { devices: [{ name: "core-switch", vendor: "cisco" }] }
}).job;
const readyJob = jobs.createNetworkJob({
  actionId: "wan_lan_check",
  targetDevice: "HEX-S-2025-LAB01",
  deviceInventory: { devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }] }
}).job;
const backupJob = jobs.createNetworkJob({
  actionId: "backup_config",
  targetDevice: "HEX-S-2025-LAB01",
  deviceInventory: { devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }] }
}).job;
const configIntentJob = jobs.createNetworkJob({
  actionId: "wan_lan_check",
  targetDevice: "HEX-S-2025-LAB01",
  deviceInventory: { devices: [{ name: "HEX-S-2025-LAB01", vendor: "mikrotik" }] },
  params: { intent: "change_access_vlan" }
}).job;

const schemaValidation = schemas.validateParseRequestOutput(matchedWanLan);

const commandResponse = await createRoute.POST(
  new Request("http://local", {
    method: "POST",
    body: JSON.stringify({
      actionId: "wan_lan_check",
      targetDevice: "HEX-S-2025-LAB01",
      command: "/system reboot"
    })
  })
);
const commandPayload = await commandResponse.json();

process.stdout.write(JSON.stringify({
  missingInventoryWanLan,
  matchedWanLan,
  baseline,
  environment,
  vlanMissing,
  backup,
  unknownActionJob,
  missingTargetJob,
  inventoryMismatchJob,
  readyJob,
  backupJob,
  configIntentJob,
  schemaValidation,
  commandStatus: commandResponse.status,
  commandPayload
}));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""


def run_phase1_check(tmp_path: Path) -> dict:
    env = os.environ.copy()
    env["NETWORK_AI_JOB_STORE_PATH"] = str(tmp_path / "jobs.json")
    completed = subprocess.run(
        ["node", "-e", NODE_PHASE1_CHECK],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_wan_lan_check_missing_inventory_does_not_require_interface_vlan_or_evidence(tmp_path):
    result = run_phase1_check(tmp_path)["missingInventoryWanLan"]

    assert result["recommendedActionId"] == "wan_lan_check"
    assert "interfaceName" not in result["missingFields"]
    assert "vlanId" not in result["missingFields"]
    assert "evidence" not in result["missingFields"]
    assert "deviceInventoryMatch" in result["missingFields"]
    assert result["blocked"] is True
    assert result["jobCreationAllowed"] is False
    assert result["blockedReason"] == "Target device not found in inventory or missing connection details"


def test_wan_lan_check_inventory_match_allows_job_creation_and_infers_vendor(tmp_path):
    result = run_phase1_check(tmp_path)["matchedWanLan"]

    assert result["recommendedActionId"] == "wan_lan_check"
    assert result["vendor"] == "mikrotik"
    assert result["missingFields"] == []
    assert result["blocked"] is False
    assert result["jobCreationAllowed"] is True
    assert result["blockedReason"] is None


def test_baseline_and_environment_do_not_require_interface_vlan_or_evidence(tmp_path):
    result = run_phase1_check(tmp_path)

    for key in ["baseline", "environment"]:
      output = result[key]
      assert "interfaceName" not in output["missingFields"]
      assert "vlanId" not in output["missingFields"]
      assert "evidence" not in output["missingFields"]
      assert output["jobCreationAllowed"] is True


def test_change_access_vlan_requires_interface_vlan_and_blocks_phase1_job_creation(tmp_path):
    result = run_phase1_check(tmp_path)["vlanMissing"]

    assert "interfaceName" in result["missingFields"]
    assert "vlanId" in result["missingFields"]
    assert result["requiresApproval"] is True
    assert result["jobCreationAllowed"] is False
    assert result["blockedReason"] == "Config change requires approval and is not executable in Phase 1"


def test_backup_config_requires_approval_and_cannot_be_ready_from_parse(tmp_path):
    result = run_phase1_check(tmp_path)["backup"]

    assert result["requiresApproval"] is True
    assert result["riskLevel"] == "medium"
    assert result["jobCreationAllowed"] is False
    assert result["blockedReason"] == "backup_config requires approval because it may expose sensitive configuration"


def test_job_create_phase1_gates(tmp_path):
    result = run_phase1_check(tmp_path)

    assert result["unknownActionJob"]["status"] == "blocked"
    assert result["missingTargetJob"]["status"] == "blocked"
    assert result["missingTargetJob"]["blockedReason"] == "Missing targetDevice"
    assert result["inventoryMismatchJob"]["status"] == "blocked"
    assert result["inventoryMismatchJob"]["blockedReason"] == "Target device not found in inventory or missing connection details"
    assert result["readyJob"]["status"] == "ready"
    assert result["backupJob"]["status"] == "pending_approval"
    assert result["configIntentJob"]["status"] == "pending_approval"


def test_job_create_rejects_command_or_script_path(tmp_path):
    result = run_phase1_check(tmp_path)

    assert result["commandStatus"] == 400
    assert "command and scriptPath are not accepted" in result["commandPayload"]["error"]


def test_parse_result_schema_supports_job_readiness_fields(tmp_path):
    result = run_phase1_check(tmp_path)["schemaValidation"]

    assert result["ok"] is True
