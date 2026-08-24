import { NextResponse } from "next/server";
import { assertLegacyAiProviderEnabled } from "@/lib/ai/providerPolicy";
import { aiError, validationError } from "@/lib/ai/routeHandler";
import { analyzeReportWithAi } from "@/lib/network-ai/aiNode";
import { createAnalysisRecord, hashAnalysisInput } from "@/lib/network-ai/analysisStore";

const MAX_ANALYZE_REPORT_CHARS = 20_000;

function isExactAnalyzeReportBody(value: unknown): value is { reportText: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    Object.keys(value).length === 1 &&
    Object.prototype.hasOwnProperty.call(value, "reportText")
  );
}

export async function POST(request: Request) {
  try {
    assertLegacyAiProviderEnabled();
    const body = (await request.json()) as unknown;

    if (!isExactAnalyzeReportBody(body) || typeof body.reportText !== "string") {
      return validationError("Request body must contain only the reportText string field.");
    }

    const reportText = body.reportText.trim();
    if (!reportText) {
      return validationError("reportText is required.");
    }
    if (reportText.length > MAX_ANALYZE_REPORT_CHARS) {
      return validationError(
        `reportText must be ${MAX_ANALYZE_REPORT_CHARS.toLocaleString("en-US")} characters or fewer.`
      );
    }

    const reportId = `ad_hoc_${hashAnalysisInput(reportText, undefined).slice(0, 16)}`;

    const result = await analyzeReportWithAi({
      reportText
    });

    const analysis = createAnalysisRecord({
      reportId,
      reportText,
      model: result.model,
      promptVersion: result.promptVersion,
      output: result.output,
      safety: result.safety
    });

    return NextResponse.json({ analysis });
  } catch (error) {
    return aiError(error);
  }
}
