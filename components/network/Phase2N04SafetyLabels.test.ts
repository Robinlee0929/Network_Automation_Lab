import { readFileSync } from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  AiActionsStage0Presentation,
  EvidenceStage0Presentation
} from "./Phase2N04DemoPresentation";

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

  it("renders provider-unavailable surfaces without provider or job controls", () => {
    const evidenceMarkup = renderToStaticMarkup(
      createElement(EvidenceStage0Presentation)
    );
    const actionsMarkup = renderToStaticMarkup(
      createElement(AiActionsStage0Presentation)
    );

    expect(evidenceMarkup).toContain(
      "Stage 0 safe Demo · report-only · provider-unavailable"
    );
    expect(evidenceMarkup).toContain("Provider analysis controls are not rendered");
    expect(evidenceMarkup).toContain("device identity, source paths, and technical payload remain withheld");
    expect(evidenceMarkup).not.toContain("AI Analyze");
    expect(evidenceMarkup).not.toContain("icon-action-button");

    expect(actionsMarkup).toContain(
      "Stage 0 safe Demo · demo-only · provider-unavailable"
    );
    expect(actionsMarkup).toContain("Provider parsing and job-creation controls are not rendered");
    expect(actionsMarkup).toContain("safely projected recorded metadata");
    expect(actionsMarkup).toContain("Recorded Request Context");
    expect(actionsMarkup).toContain("No provider request can be submitted from this page");
    expect(actionsMarkup).toContain("Approval, job creation, and execution are also unavailable");
    expect(actionsMarkup).not.toContain("<button");
    expect(actionsMarkup).not.toContain("<textarea");
    expect(actionsMarkup).not.toContain(">Parse<");
    expect(actionsMarkup).not.toContain("Create Job");
  });

  it("removes the legacy provider and job action paths from the rendered Demo parents", () => {
    const evidence = source("components/network/DayResultsClient.tsx");
    const aiActions = source("components/network/AiActionsClient.tsx");
    const jobs = source("components/network/JobsClient.tsx");

    expect(evidence).toContain("<EvidenceStage0Presentation />");
    expect(evidence).toContain("Recorded evidence · non-executing");
    expect(evidence).toContain("Technical payload is not displayed");
    expect(evidence).not.toContain("analyzeSelected");
    expect(evidence).not.toContain("/api/network/ai/analyze-report");
    expect(evidence).not.toContain("icon-action-button");
    expect(evidence).not.toContain("deriveExecutionBoundary");
    expect(evidence).not.toContain("Raw Evidence JSON");
    expect(evidence).not.toContain("JSON.stringify");

    expect(aiActions).toContain("<AiActionsStage0Presentation />");
    expect(aiActions).toContain("Allowlist Reference");
    expect(aiActions).toContain("Provider parsing remains");
    expect(aiActions).not.toContain("parseRequest");
    expect(aiActions).not.toContain("createJob");
    expect(aiActions).not.toContain('fetch("/api/network/ai/parse-request"');
    expect(aiActions).not.toContain("/api/network/jobs/create");
    expect(aiActions).not.toContain("icon-action-button");
    expect(aiActions).not.toContain("<textarea");
    expect(aiActions).not.toContain("JSON.stringify");
    expect(aiActions).not.toContain("output?.targetDevice");

    expect(jobs).toContain('fetch("/api/network/jobs")');
    expect(jobs).toContain("Reload recorded jobs");
    expect(jobs).toContain("<table");
    expect(jobs).toContain("runner, queue, scheduler, worker");
    expect(jobs).not.toContain('fetch("/api/network/jobs/create"');
    expect(jobs).not.toContain("Run Job");
    expect(jobs).not.toContain("job.targetDevice");
    expect(jobs).not.toContain("job.params");
    expect(jobs).not.toContain("job.source");
  });
});
