import { NextResponse } from "next/server";
import { generateAiDraft, aiError, validationError } from "@/lib/ai/routeHandler";
import { buildRequirementAnalysisInput, requirementAnalysisPrompt } from "@/lib/ai/prompts";
import { validateRequirementPayload } from "@/lib/ai/validators";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateRequirementPayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const content = (body as { content: string }).content.trim();
    const draft = await generateAiDraft({
      systemPrompt: requirementAnalysisPrompt,
      userInput: buildRequirementAnalysisInput(content)
    });

    return NextResponse.json(draft);
  } catch (error) {
    return aiError(error);
  }
}
