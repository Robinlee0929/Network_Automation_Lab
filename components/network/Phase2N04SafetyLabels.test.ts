import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

function source(relativePath: string) {
  return readFileSync(path.join(process.cwd(), relativePath), "utf8");
}

describe("Phase 2N-04 user-facing safety labels", () => {
  it("identifies the canonical Flask entry point and secondary Next.js surface", () => {
    const landing = source("app/page.tsx");
    const navigation = source("components/network/NetworkNav.tsx");

    expect(landing).toContain("Canonical reviewer entry point: Flask dashboard");
    expect(landing).toContain("Next.js app is a secondary, demo-only surface");
    expect(landing).toContain("unavailable in the Stage 0 safe Demo");
    expect(navigation).toContain("Secondary Stage 0 surface · report-only / demo-only");

    for (const route of [
      "/network/day-results",
      "/network/ai-actions",
      "/network/reports",
      "/network/jobs"
    ]) {
      expect(navigation).toContain(`href: "${route}"`);
    }
  });

  it("labels provider-backed controls without importing or invoking their components", () => {
    const evidence = source("components/network/DayResultsClient.tsx");
    const aiActions = source("components/network/AiActionsClient.tsx");

    expect(evidence).toContain("Stage 0 safe Demo · report-only · provider-unavailable");
    expect(evidence).toContain("AI Analyze is excluded from this Demo");
    expect(aiActions).toContain("Stage 0 safe Demo · demo-only · provider-unavailable");
    expect(aiActions).toContain("Parse and Create Job are excluded from this Demo");
  });
});
