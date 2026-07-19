import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { DayResult } from "@/lib/network-ai/schemas";
import { ReportsClient } from "./ReportsClient";

const prohibitedSentinels = {
  id: "SENSITIVE_REPORT_IDENTIFIER",
  deviceName: "SENSITIVE_DEVICE_NAME",
  reportTitle: "SENSITIVE_REPORT_TITLE",
  vendor: "mikrotik" as const,
  checkType: "SENSITIVE_CHECK_TYPE",
  rawOutput: "SENSITIVE_RAW_OUTPUT",
  parsedResult: { secret: "SENSITIVE_PARSED_RESULT" },
  sourcePath: "C:/private/SENSITIVE_SOURCE_PATH.json"
};

function report(overrides: Partial<DayResult> = {}): DayResult {
  return {
    ...prohibitedSentinels,
    sourceDay: "Day-12",
    dayLabel: "SENSITIVE_DAY_LABEL",
    resultKind: "device_report",
    status: "pass",
    createdAt: "2026-07-13T09:10:11.000Z",
    ...overrides
  };
}

describe("ReportsClient", () => {
  it("renders the reviewer-facing empty state without a not-found or external operation", () => {
    const markup = renderToStaticMarkup(createElement(ReportsClient, { reports: [] }));

    expect(markup).toContain("0 reports");
    expect(markup).toContain("No report evidence is currently available");
    expect(markup).toContain("This page is working");
    expect(markup).toContain("no external service or device operation is required");
    expect(markup).not.toContain("notFound");
  });

  it("renders only normalized safe metadata for available reports", () => {
    const markup = renderToStaticMarkup(
      createElement(ReportsClient, {
        reports: [
          report(),
          report({
            id: "SECOND_SENSITIVE_ID",
            resultKind: "summary_report",
            sourceDay: "untrusted source label",
            status: "unexpected custom status",
            createdAt: "invalid date"
          })
        ]
      })
    );

    expect(markup).toContain("2 reports");
    expect(markup).toContain("Device Check Report");
    expect(markup).toContain("Project Summary");
    expect(markup).toContain("Day 12");
    expect(markup).toContain("Unspecified day");
    expect(markup).toContain("2026-07-13");
    expect(markup).toContain("Unknown date");
    expect(markup).toContain("PASS");
    expect(markup).toContain("UNKNOWN");

    for (const value of [
      prohibitedSentinels.id,
      prohibitedSentinels.deviceName,
      prohibitedSentinels.reportTitle,
      prohibitedSentinels.checkType,
      prohibitedSentinels.rawOutput,
      prohibitedSentinels.parsedResult.secret,
      prohibitedSentinels.sourcePath,
      "SENSITIVE_DAY_LABEL",
      "SECOND_SENSITIVE_ID",
      "untrusted source label",
      "unexpected custom status"
    ]) {
      expect(markup).not.toContain(value);
    }

    expect(markup).not.toContain("AI Summary");
    expect(markup).not.toContain("analyze-report");
    expect(markup).not.toContain("All Missing Reports");
  });

  it("keeps the Reports navigation matched to a page and preserves Evidence", () => {
    const workspace = process.cwd();
    const networkLayout = path.join(workspace, "app", "network", "layout.tsx");
    const reportsPage = path.join(workspace, "app", "network", "reports", "page.tsx");
    const dayResultsPage = path.join(workspace, "app", "network", "day-results", "page.tsx");
    const navigation = readFileSync(
      path.join(workspace, "components", "network", "NetworkNav.tsx"),
      "utf8"
    );
    const ignoreRules = readFileSync(path.join(workspace, ".gitignore"), "utf8");

    expect(existsSync(networkLayout)).toBe(true);
    expect(existsSync(reportsPage)).toBe(true);
    expect(existsSync(dayResultsPage)).toBe(true);
    expect(navigation).toContain('{ href: "/network/reports", label: "Reports" }');
    expect(navigation).not.toContain("All Missing Reports");
    expect(ignoreRules).toContain("reports/");
    expect(ignoreRules).toContain("!app/network/reports/**");

    const layoutSource = readFileSync(networkLayout, "utf8");
    const routeSource = readFileSync(reportsPage, "utf8");
    expect(layoutSource).toContain("<NetworkNav />");
    expect(routeSource).toContain("importDayResults()");
    expect(routeSource).not.toContain("<NetworkNav />");
    expect(routeSource).not.toContain("notFound(");
  });
});
