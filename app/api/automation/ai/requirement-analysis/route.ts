import { NextResponse } from "next/server";
import { generateAiNodeJson, aiError, validationError } from "@/lib/ai/routeHandler";
import {
  automationRequirementAnalysisPrompt,
  buildAutomationRequirementInput
} from "@/lib/ai/prompts";
import { validateAutomationRequirementPayload } from "@/lib/ai/validators";
import type { RequirementAnalysisNodeOutput } from "@/lib/ai/schemas";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateAutomationRequirementPayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const requirementText = (body as { requirementText: string }).requirementText.trim();
    const nodeResult = await generateAiNodeJson<RequirementAnalysisNodeOutput>({
      nodeType: "RequirementAnalysisNode",
      systemPrompt: automationRequirementAnalysisPrompt,
      userInput: buildAutomationRequirementInput(requirementText)
    });

    return NextResponse.json(nodeResult);
  } catch (error) {
    return aiError(error);
  }
}
