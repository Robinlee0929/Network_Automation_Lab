import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const providerMocks = vi.hoisted(() => {
  const create = vi.fn();
  return {
    create,
    getOpenAIClient: vi.fn(() => ({ responses: { create } }))
  };
});

const analyzerMocks = vi.hoisted(() => ({
  analyzeReportWithAi: vi.fn(),
  createAnalysisRecord: vi.fn(),
  hashAnalysisInput: vi.fn(() => "abcdef0123456789abcdef0123456789")
}));

vi.mock("./openaiClient", () => ({
  getOpenAIClient: providerMocks.getOpenAIClient,
  getOpenAIModel: () => "mock-model"
}));

vi.mock("@/lib/ai/providerPolicy", () => import("./providerPolicy"));
vi.mock("@/lib/ai/routeHandler", () => import("./routeHandler"));

vi.mock("@/lib/network-ai/aiNode", () => ({
  analyzeReportWithAi: analyzerMocks.analyzeReportWithAi
}));

vi.mock("@/lib/network-ai/analysisStore", () => ({
  createAnalysisRecord: analyzerMocks.createAnalysisRecord,
  hashAnalysisInput: analyzerMocks.hashAnalysisInput
}));

import { AI_DRAFT_NOTICE } from "./prompts";
import { LegacyAiProviderDisabledError } from "./providerPolicy";
import { aiError, generateAiDraft, generateAiNodeJson } from "./routeHandler";
import type { KnowledgeQaNodeOutput } from "./schemas";
import { validateAnalyzeReportOutput } from "../network-ai/schemas";
import { POST as analyzeReportPost } from "../../app/api/network/ai/analyze-report/route";

const originalLegacyProviderFlag = process.env.LEGACY_AI_PROVIDER_ENABLED;

beforeEach(() => {
  delete process.env.LEGACY_AI_PROVIDER_ENABLED;
  providerMocks.create.mockReset();
  providerMocks.getOpenAIClient.mockClear();
  analyzerMocks.analyzeReportWithAi.mockReset();
  analyzerMocks.createAnalysisRecord.mockReset();
  analyzerMocks.hashAnalysisInput.mockClear();
});

afterEach(() => {
  if (originalLegacyProviderFlag === undefined) {
    delete process.env.LEGACY_AI_PROVIDER_ENABLED;
  } else {
    process.env.LEGACY_AI_PROVIDER_ENABLED = originalLegacyProviderFlag;
  }
});

describe("legacy provider helper boundary", () => {
  it("blocks AI drafts before provider-client construction", async () => {
    await expect(
      generateAiDraft({ systemPrompt: "system", userInput: "input" })
    ).rejects.toThrow(LegacyAiProviderDisabledError);

    expect(providerMocks.getOpenAIClient).not.toHaveBeenCalled();
    expect(providerMocks.create).not.toHaveBeenCalled();
  });

  it("blocks structured AI nodes before provider-client construction", async () => {
    await expect(
      generateAiNodeJson<KnowledgeQaNodeOutput>({
        nodeType: "KnowledgeQaNode",
        systemPrompt: "system",
        userInput: "input"
      })
    ).rejects.toThrow(LegacyAiProviderDisabledError);

    expect(providerMocks.getOpenAIClient).not.toHaveBeenCalled();
    expect(providerMocks.create).not.toHaveBeenCalled();
  });

  it("preserves the enabled mocked draft path", async () => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = "1";
    providerMocks.create.mockResolvedValue({ output_text: "mock draft" });

    const result = await generateAiDraft({ systemPrompt: "system", userInput: "input" });

    expect(providerMocks.getOpenAIClient).toHaveBeenCalledTimes(1);
    expect(providerMocks.create).toHaveBeenCalledTimes(1);
    expect(result).toEqual({
      model: "mock-model",
      result: `${AI_DRAFT_NOTICE}\n\nmock draft`
    });
  });

  it("strictly validates enabled structured output and forces human review", async () => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = "1";
    providerMocks.create.mockResolvedValue({
      output_text: JSON.stringify({
        answer: "bounded answer",
        evidence: ["fixture evidence"],
        insufficientInfo: false,
        suggestedNextStep: "review",
        needsHumanReview: false
      })
    });

    const result = await generateAiNodeJson<KnowledgeQaNodeOutput>({
      nodeType: "KnowledgeQaNode",
      systemPrompt: "system",
      userInput: "input"
    });

    expect(result.output.needsHumanReview).toBe(true);
    expect(providerMocks.getOpenAIClient).toHaveBeenCalledTimes(1);
    expect(providerMocks.create).toHaveBeenCalledTimes(1);
  });

  it("rejects unsupported provider output fields", async () => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = "1";
    providerMocks.create.mockResolvedValue({
      output_text: JSON.stringify({
        answer: "bounded answer",
        evidence: [],
        insufficientInfo: false,
        suggestedNextStep: "review",
        needsHumanReview: true,
        unexpectedAuthority: "execute"
      })
    });

    await expect(
      generateAiNodeJson<KnowledgeQaNodeOutput>({
        nodeType: "KnowledgeQaNode",
        systemPrompt: "system",
        userInput: "input"
      })
    ).rejects.toThrow("strict schema validation");
  });
});

describe("public AI error mapping", () => {
  it("does not reflect raw provider or internal error messages", async () => {
    const response = aiError(new Error("sensitive provider detail at C:\\private\\path"));
    const payload = (await response.json()) as { error: string };

    expect(response.status).toBe(500);
    expect(payload.error).toBe(
      "AI provider request failed."
    );
    expect(payload.error).not.toContain("sensitive provider detail");
    expect(payload.error).not.toContain("C:\\private\\path");
  });

  it("maps the intentional disabled state distinctly", async () => {
    const response = aiError(new LegacyAiProviderDisabledError());
    const payload = (await response.json()) as { error: string };

    expect(response.status).toBe(503);
    expect(payload.error).toContain("LEGACY_AI_PROVIDER_ENABLED=1");
  });
});

describe("legacy report analyzer boundary", () => {
  it("short-circuits disabled requests before body parsing, provider analysis, or persistence", async () => {
    const json = vi.fn();

    const response = await analyzeReportPost({ json } as unknown as Request);

    expect(response.status).toBe(503);
    expect(json).not.toHaveBeenCalled();
    expect(analyzerMocks.analyzeReportWithAi).not.toHaveBeenCalled();
    expect(analyzerMocks.createAnalysisRecord).not.toHaveBeenCalled();
  });

  it("rejects expanded and oversized analyzer requests without analysis or persistence", async () => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = "1";

    const expandedResponse = await analyzeReportPost(
      new Request("http://localhost/api/network/ai/analyze-report", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ reportText: "report", deviceContext: { targetDevice: "private" } })
      })
    );
    const oversizedResponse = await analyzeReportPost(
      new Request("http://localhost/api/network/ai/analyze-report", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ reportText: "x".repeat(20_001) })
      })
    );

    expect(expandedResponse.status).toBe(400);
    expect(oversizedResponse.status).toBe(400);
    expect(analyzerMocks.analyzeReportWithAi).not.toHaveBeenCalled();
    expect(analyzerMocks.createAnalysisRecord).not.toHaveBeenCalled();
  });

  it("persists only after successful explicitly enabled mocked analysis", async () => {
    process.env.LEGACY_AI_PROVIDER_ENABLED = "1";
    analyzerMocks.analyzeReportWithAi.mockResolvedValue({
      model: "mock-model",
      promptVersion: "mock-prompt",
      output: { needsHumanReview: true },
      safety: { jobCreationAllowed: false }
    });
    analyzerMocks.createAnalysisRecord.mockReturnValue({ id: "analysis_fixture" });

    const response = await analyzeReportPost(
      new Request("http://localhost/api/network/ai/analyze-report", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ reportText: " bounded report " })
      })
    );

    expect(response.status).toBe(200);
    expect(analyzerMocks.analyzeReportWithAi).toHaveBeenCalledWith({
      reportText: "bounded report"
    });
    expect(analyzerMocks.createAnalysisRecord).toHaveBeenCalledTimes(1);
    expect(analyzerMocks.analyzeReportWithAi.mock.invocationCallOrder[0]).toBeLessThan(
      analyzerMocks.createAnalysisRecord.mock.invocationCallOrder[0]
    );
  });
});

describe("network provider output schema", () => {
  it("rejects unsupported report-analysis fields", () => {
    const result = validateAnalyzeReportOutput({
      summary: "summary",
      findings: [],
      warnings: [],
      possibleCauses: [],
      recommendedActions: [],
      recommendedExistingActionIds: [],
      riskLevel: "low",
      requiresApproval: false,
      needsHumanReview: true,
      unexpectedAuthority: "execute"
    });

    expect(result).toEqual({
      ok: false,
      error: "AI report analyzer output contained an unsupported field."
    });
  });
});
