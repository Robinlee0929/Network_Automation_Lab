import { NextResponse } from "next/server";
import { getLatestAnalysisForReport } from "@/lib/network-ai/analysisStore";

export async function GET(
  _request: Request,
  context: { params: Promise<{ reportId: string }> }
) {
  const { reportId } = await context.params;

  return NextResponse.json({
    analysis: getLatestAnalysisForReport(reportId)
  });
}
