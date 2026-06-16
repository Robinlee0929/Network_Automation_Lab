import { NextResponse } from "next/server";
import { aiError, validationError } from "@/lib/ai/routeHandler";
import { analyzeReportWithAi } from "@/lib/network-ai/aiNode";
import { createAnalysisRecord, hashAnalysisInput } from "@/lib/network-ai/analysisStore";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      reportId?: unknown;
      reportText?: unknown;
      deviceContext?: unknown;
    };

    if (typeof body.reportText !== "string" || !body.reportText.trim()) {
      return validationError("reportText is required.");
    }

    const reportText = body.reportText.trim();
    const reportId =
      typeof body.reportId === "string" && body.reportId.trim()
        ? body.reportId.trim()
        : `ad_hoc_${hashAnalysisInput(reportText, body.deviceContext).slice(0, 16)}`;

    const result = await analyzeReportWithAi({
      reportText,
      deviceContext: body.deviceContext
    });

    const analysis = createAnalysisRecord({
      reportId,
      reportText,
      deviceContext: body.deviceContext,
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
