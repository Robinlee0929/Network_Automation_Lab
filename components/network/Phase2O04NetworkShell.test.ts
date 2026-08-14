import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

function source(relativePath: string) {
  return readFileSync(path.join(process.cwd(), relativePath), "utf8");
}

function occurrences(value: string, pattern: RegExp) {
  return value.match(pattern)?.length ?? 0;
}

const pageContracts = [
  {
    path: "app/network/day-results/page.tsx",
    heading: "Automation Evidence",
    imports: [
      'import { DayResultsClient } from "@/components/network/DayResultsClient";',
      'import { importDayResults } from "@/lib/network-ai/dayResults";'
    ],
    dataCall: "const results = importDayResults();",
    client: "<DayResultsClient results={results} />"
  },
  {
    path: "app/network/ai-actions/page.tsx",
    heading: "AI Actions",
    imports: [
      'import { AiActionsClient } from "@/components/network/AiActionsClient";',
      'import { getAvailableActions } from "@/lib/network-ai/actions";'
    ],
    dataCall: "const actions = getAvailableActions();",
    client: "<AiActionsClient actions={actions} />"
  },
  {
    path: "app/network/reports/page.tsx",
    heading: "Reports",
    imports: [
      'import { ReportsClient } from "@/components/network/ReportsClient";',
      'import { importDayResults } from "@/lib/network-ai/dayResults";'
    ],
    dataCall: "const reports = importDayResults();",
    client: "<ReportsClient reports={reports} />"
  },
  {
    path: "app/network/jobs/page.tsx",
    heading: "Jobs",
    imports: [
      'import { JobsClient } from "@/components/network/JobsClient";',
      'import { listNetworkJobs } from "@/lib/network-ai/jobs";'
    ],
    dataCall: "const jobs = listNetworkJobs();",
    client: "<JobsClient initialJobs={jobs} />"
  }
] as const;

describe("Phase 2O-04 secondary Next.js network shell", () => {
  it("provides one shared presentation-only shell with canonical and secondary identities", () => {
    const layout = source("app/network/layout.tsx");

    expect(layout).toContain("export default function NetworkLayout");
    expect(layout).toContain('<div className="network-shell">');
    expect(layout).toContain("<NetworkNav />");
    expect(layout).toContain("Secondary Next.js · Stage 0");
    expect(layout).toContain("The Flask dashboard is the canonical reviewer surface");
    expect(layout).toContain('const canonicalFlaskUrl = "http://127.0.0.1:5000/";');
    expect(layout).toContain('href={canonicalFlaskUrl}');
    expect(layout).not.toMatch(/<main\b/);
  });

  it("targets route-owned primary content with the shared skip link", () => {
    const layout = source("app/network/layout.tsx");

    expect(layout).toContain('className="network-skip-link"');
    expect(layout).toContain('href="#network-primary-content"');

    for (const contract of pageContracts) {
      const page = source(contract.path);
      expect(page).toContain('id="network-primary-content"');
      expect(page).toContain("tabIndex={-1}");
    }
  });

  it("defines all five state terms without collapsing their meanings", () => {
    const layout = source("app/network/layout.tsx");
    const definitions = [
      '["EMPTY", "A valid collection contains zero items."]',
      '["MISSING", "An expected local artifact is absent."]',
      '["UNAVAILABLE", "A capability is intentionally not offered in Stage 0."]',
      '["ERROR", "An existing allowed read failed."]',
      '["BLOCKED", "A recorded safety result prevented an operation."]'
    ];

    for (const definition of definitions) {
      expect(layout).toContain(definition);
    }
  });

  it("retains exactly the four approved destinations and current-route semantics", () => {
    const navigation = source("components/network/NetworkNav.tsx");
    const destinations = [...navigation.matchAll(/href: "([^"]+)"/g)].map((match) => match[1]);

    expect(destinations).toEqual([
      "/network/day-results",
      "/network/ai-actions",
      "/network/reports",
      "/network/jobs"
    ]);
    expect(navigation).toContain('aria-current={isCurrent ? "page" : undefined}');
    expect(navigation).toContain("Current section");
    expect(navigation).toContain("Secondary Stage 0 surface · report-only / demo-only");
    expect(navigation).toContain("<ul");
    expect(navigation).toContain("<li");
  });

  it("keeps one route h1, one route main, and every existing data/client responsibility", () => {
    for (const contract of pageContracts) {
      const page = source(contract.path);

      expect(occurrences(page, /<main\b/g)).toBe(1);
      expect(occurrences(page, /<h1\b/g)).toBe(1);
      expect(page).toContain(`<h1>${contract.heading}</h1>`);
      expect(page).not.toContain("NetworkNav");
      for (const importLine of contract.imports) {
        expect(page).toContain(importLine);
      }
      expect(page).toContain(contract.dataCall);
      expect(page).toContain(contract.client);
    }
  });

  it("does not add provider, API, submission, or execution behavior to changed production sources", () => {
    const productionSources = [
      "app/network/layout.tsx",
      "components/network/NetworkNav.tsx",
      ...pageContracts.map((contract) => contract.path)
    ].map(source);
    const forbidden = [
      /["']\/ai["']/,
      /\/automation\/ai-nodes/,
      /\bopenai\b/i,
      /\bprovider\s*\(/i,
      /\bfetch\s*\(/,
      /\bPOST\b/,
      /AI Analyze/,
      />\s*Parse\s*</,
      /Create Job/,
      /Run Job/,
      /command execution/i,
      /<form\b/i,
      /<textarea\b/i,
      /<button\b/i,
      /type=["']submit["']/i
    ];

    for (const productionSource of productionSources) {
      for (const pattern of forbidden) {
        expect(productionSource).not.toMatch(pattern);
      }
    }
  });

  it("preserves the network redirect and package lock boundary", () => {
    const redirectPage = source("app/network/page.tsx");
    const packageHashes = {
      "package.json": "e1a170ec5f4665070c931d794bc85e0436039ba0a1346239bbf737e4212b9a51",
      "package-lock.json": "2c113d40fb5aa0968c214ac58f67fd336d843938d868198931c499a5a2146627"
    } as const;

    expect(redirectPage).toContain('redirect("/network/day-results")');
    for (const [file, expectedHash] of Object.entries(packageHashes)) {
      const canonicalSource = source(file).replace(/\r\n/g, "\n");
      const hash = createHash("sha256").update(canonicalSource).digest("hex");
      expect(hash).toBe(expectedHash);
    }
  });

  it("keeps skip, focus, wrapping, and narrow-screen CSS contracts", () => {
    const css = source("app/globals.css");

    expect(css).toContain(".network-skip-link");
    expect(css).toContain(".network-skip-link:focus");
    expect(css).toContain(":focus-visible");
    expect(css).toContain("flex-wrap: wrap");
    expect(css).toContain("overflow-wrap: anywhere");
    expect(css).toContain("@media (max-width: 860px)");
    expect(css).toContain("grid-template-columns: 1fr");
  });
});
