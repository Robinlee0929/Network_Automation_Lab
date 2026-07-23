import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

import {
  normalizeRecordedDate,
  normalizeRecordedStatus,
  normalizeSourceDay,
  projectActionCatalog,
  projectAnalysisRecord,
  projectEvidenceCollection,
  projectJobsCollection,
  projectParseResult,
  projectReportsCollection
} from "./Phase2O05SafePresentation";

const sensitiveSentinels = {
  device: "SENSITIVE_DEVICE_HOST_10.10.10.10",
  path: "C:/Users/private/SENSITIVE_REPORT.json",
  provider: "SENSITIVE_PROVIDER_MODEL",
  command: "SENSITIVE_COMMAND_ARGUMENT",
  secret: "SENSITIVE_TOKEN_CREDENTIAL",
  traceback: "SENSITIVE_TRACEBACK",
  userText: "SENSITIVE_USER_REQUEST"
};

function recordedEvidence(overrides: Record<string, unknown> = {}) {
  return {
    id: "0123456789abcdef",
    sourceDay: "day-12",
    dayLabel: sensitiveSentinels.userText,
    resultKind: "device_report",
    deviceName: sensitiveSentinels.device,
    reportTitle: sensitiveSentinels.userText,
    vendor: "mikrotik",
    checkType: sensitiveSentinels.command,
    status: "pass",
    rawOutput: `${sensitiveSentinels.secret} ${sensitiveSentinels.path}`,
    parsedResult: {
      provider: sensitiveSentinels.provider,
      traceback: sensitiveSentinels.traceback
    },
    createdAt: "2026-07-23T01:02:03.000Z",
    sourcePath: sensitiveSentinels.path,
    ...overrides
  };
}

function assertNoSensitiveOutput(value: unknown) {
  const serialized = JSON.stringify(value);
  for (const sentinel of Object.values(sensitiveSentinels)) {
    expect(serialized).not.toContain(sentinel);
  }
}

describe("Phase2O05SafePresentation", () => {
  it("preserves the singular 109-row controlling matrix structure", () => {
    const plan = readFileSync(
      path.join(
        process.cwd(),
        "docs",
        "phase_2o",
        "phase_2o_05_secondary_nextjs_evidence_reports_ai_actions_and_jobs_visualization_planning_only.md"
      ),
      "utf8"
    );
    const rows = plan
      .split(/\r?\n/)
      .filter((line) => /^\| [ERAJ][0-9]{2} \|/.test(line));
    const ids = rows.map((line) => line.match(/^\| ([ERAJ][0-9]{2}) \|/)?.[1]);

    expect(rows).toHaveLength(109);
    expect(new Set(ids).size).toBe(109);
    expect(rows.every((line) => line.split("|").length - 2 === 13)).toBe(true);
    expect(ids.filter((id) => id?.startsWith("E"))).toHaveLength(41);
    expect(ids.filter((id) => id?.startsWith("R"))).toHaveLength(16);
    expect(ids.filter((id) => id?.startsWith("A"))).toHaveLength(31);
    expect(ids.filter((id) => id?.startsWith("J"))).toHaveLength(21);
  });

  it("normalizes only closed status, source-day, and UTC-date values", () => {
    expect(normalizeRecordedStatus("PASS")).toBe("PASS");
    expect(normalizeRecordedStatus("warning")).toBe("WARN");
    expect(normalizeRecordedStatus("failure with secret")).toBe("UNKNOWN");
    expect(normalizeSourceDay("day_007")).toEqual({ label: "Day 7", number: 7 });
    expect(normalizeSourceDay("prefix day 7 secret")).toEqual({
      label: "Unspecified day",
      number: -1
    });
    expect(normalizeRecordedDate("2026-07-23T01:02:03.000Z").label).toBe(
      "2026-07-23"
    );
    expect(normalizeRecordedDate("private local timestamp").label).toBe("Unknown date");
  });

  it("projects Evidence and Reports without raw fields, unknown keys, or mutation", () => {
    const input = [
      recordedEvidence(),
      recordedEvidence({
        id: "fedcba9876543210",
        sourceDay: "untrusted day",
        resultKind: "unexpected-kind",
        status: "unexpected custom status",
        createdAt: "invalid",
        parsedResult: { parseWarning: "JSON report could not be parsed." },
        unknownField: sensitiveSentinels.secret
      }),
      recordedEvidence({ id: sensitiveSentinels.path })
    ];
    const before = structuredClone(input);
    const evidence = projectEvidenceCollection(input);
    const reports = projectReportsCollection(input);

    expect(evidence.state).toBe("AVAILABLE");
    expect(evidence.items).toHaveLength(2);
    expect(evidence.rejectedCount).toBe(1);
    expect(evidence.items[0]).toMatchObject({
      category: "Device Check Report",
      dayLabel: "Day 12",
      status: "PASS",
      recordedDate: "2026-07-23"
    });
    expect(evidence.items[1]).toMatchObject({
      category: "Uncategorized Evidence",
      dayLabel: "Unspecified day",
      status: "UNKNOWN",
      recordedDate: "Unknown date",
      malformed: true
    });
    expect(reports).toEqual(evidence);
    expect(input).toEqual(before);
    assertNoSensitiveOutput(evidence);
  });

  it("fails closed for unavailable, malformed, and unknown analysis fields", () => {
    expect(projectAnalysisRecord(null)).toEqual({ state: "EMPTY" });
    expect(projectAnalysisRecord({ output: "unsafe" })).toEqual({
      state: "REJECTED"
    });

    const projected = projectAnalysisRecord({
      id: sensitiveSentinels.secret,
      model: sensitiveSentinels.provider,
      output: {
        summary: sensitiveSentinels.userText,
        riskLevel: "high",
        requiresApproval: true,
        needsHumanReview: false,
        recommendedActions: [sensitiveSentinels.command]
      },
      safety: {
        jobCreationAllowed: false,
        reason: sensitiveSentinels.path
      },
      createdAt: "2026-07-23T01:02:03.000Z",
      unknown: sensitiveSentinels.traceback
    });

    expect(projected).toEqual({
      state: "AVAILABLE",
      risk: "Recorded risk: HIGH",
      approvalFlag: "Recorded approval flag: yes",
      humanReviewFlag: "Recorded human-review flag: no",
      jobEligibility:
        "Recorded job eligibility: no · job creation unavailable in Stage 0",
      recordedDate: "Recorded analysis date: 2026-07-23"
    });
    assertNoSensitiveOutput(projected);
  });

  it("allows only fixed catalog IDs and never reflects catalog descriptions", () => {
    const projected = projectActionCatalog([
      {
        id: "baseline_check",
        label: sensitiveSentinels.userText,
        description: sensitiveSentinels.command,
        readOnly: true,
        configChange: false,
        riskLevel: "low",
        allowedVendors: [sensitiveSentinels.provider]
      },
      {
        id: sensitiveSentinels.secret,
        label: sensitiveSentinels.userText
      }
    ]);

    expect(projected).toHaveLength(1);
    expect(projected[0]).toMatchObject({
      id: "baseline_check",
      label: "Baseline Check",
      configurationCapability: "Configuration-changing capability: unavailable",
      risk: "Catalog risk: LOW"
    });
    assertNoSensitiveOutput(projected);
  });

  it("projects parse records through closed enums and fixed reason mappings", () => {
    expect(projectParseResult(null)).toEqual({ state: "EMPTY" });
    expect(projectParseResult({ output: "unsafe" })).toEqual({
      state: "REJECTED"
    });

    const projected = projectParseResult({
      id: sensitiveSentinels.secret,
      userRequest: sensitiveSentinels.userText,
      deviceInventoryHash: sensitiveSentinels.secret,
      deviceInventorySnapshot: { host: sensitiveSentinels.device },
      output: {
        intent: "backup_config",
        targetDevice: sensitiveSentinels.device,
        vendor: "cisco",
        interfaceName: sensitiveSentinels.command,
        vlanId: 999,
        recommendedActionId: "backup_config",
        missingFields: [
          "targetDevice",
          sensitiveSentinels.userText,
          sensitiveSentinels.userText
        ],
        riskLevel: "medium",
        requiresApproval: true,
        blocked: true,
        jobCreationAllowed: false,
        blockedReason:
          "backup_config requires approval because it may expose sensitive configuration",
        notes: [sensitiveSentinels.provider]
      },
      createdAt: "2026-07-23T01:02:03.000Z",
      unknown: sensitiveSentinels.traceback
    });

    expect(projected).toMatchObject({
      state: "AVAILABLE",
      intent: "Recorded intent category: configuration backup reference · unavailable",
      recommendation: "Recorded recommendation: Backup Config",
      missingFields: [
        "Target reference required",
        "Other required information withheld"
      ],
      risk: "Recorded risk: MEDIUM",
      approvalFlag: "Recorded approval flag: yes",
      safetyResult: "Recorded safety result: BLOCKED · non-executing",
      jobEligibility:
        "Recorded eligibility: no · job creation unavailable in Stage 0",
      reason: "Recorded reason: configuration backup requires review",
      recordedDate: "Recorded parse date: 2026-07-23"
    });
    assertNoSensitiveOutput(projected);
  });

  it("validates Jobs top-level shape and withholds prohibited nested data", () => {
    const validJob = {
      id: "job_123e4567-e89b-42d3-a456-426614174000",
      actionId: "baseline_check",
      targetDevice: sensitiveSentinels.device,
      vendor: "cisco",
      params: {
        command: sensitiveSentinels.command,
        token: sensitiveSentinels.secret,
        path: sensitiveSentinels.path
      },
      status: "ready",
      blockedReason: null,
      riskLevel: "low",
      requiresApproval: false,
      readOnly: true,
      source: sensitiveSentinels.userText,
      parseResultId: sensitiveSentinels.secret,
      createdAt: "2026-07-23T01:02:03.000Z"
    };
    const invalidId = {
      ...validJob,
      id: sensitiveSentinels.path,
      actionId: "unknown-action",
      status: "unexpected",
      blockedReason: sensitiveSentinels.secret
    };
    const extraShape = {
      ...validJob,
      id: "job_123e4567-e89b-42d3-a456-426614174001",
      extra: sensitiveSentinels.traceback
    };
    const before = structuredClone([validJob, invalidId, extraShape]);
    const projected = projectJobsCollection([validJob, invalidId, extraShape]);

    expect(projected.state).toBe("AVAILABLE");
    expect(projected.items).toHaveLength(2);
    expect(projected.rejectedCount).toBe(1);
    expect(projected.items[0]).toMatchObject({
      visibleId: validJob.id,
      action: "Baseline Check",
      platform: "Recorded device platform: Cisco",
      status: "RECORDED / NEVER EXECUTED",
      risk: "Recorded risk: LOW",
      approvalFlag: "Recorded approval flag: no",
      recordedDate: "Recorded: 2026-07-23"
    });
    expect(projected.items[1]).toMatchObject({
      visibleId: "Identifier withheld",
      action: "Unknown catalog reference",
      status: "REJECTED",
      reason: "Recorded reason withheld"
    });
    expect([validJob, invalidId, extraShape]).toEqual(before);
    assertNoSensitiveOutput(projected);
  });

  it("uses explicit empty and error states for invalid collections", () => {
    expect(projectEvidenceCollection([])).toEqual({
      state: "EMPTY",
      items: [],
      rejectedCount: 0
    });
    expect(projectEvidenceCollection({ raw: sensitiveSentinels.secret })).toEqual({
      state: "ERROR",
      items: [],
      rejectedCount: 0
    });
    expect(projectJobsCollection([{ id: null, extra: sensitiveSentinels.secret }])).toEqual(
      {
        state: "ERROR",
        items: [],
        rejectedCount: 1
      }
    );
  });
});
