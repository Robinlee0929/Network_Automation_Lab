import { NextResponse } from "next/server";
import { generateAiNodeJson, aiError, validationError } from "@/lib/ai/routeHandler";
import {
  automationKnowledgeQaPrompt,
  buildAutomationKnowledgeInput
} from "@/lib/ai/prompts";
import { validateAutomationKnowledgePayload } from "@/lib/ai/validators";
import type { KnowledgeQaNodeOutput } from "@/lib/ai/schemas";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateAutomationKnowledgePayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const payload = body as { documentText: string; question: string };
    const nodeResult = await generateAiNodeJson<KnowledgeQaNodeOutput>({
      nodeType: "KnowledgeQaNode",
      systemPrompt: automationKnowledgeQaPrompt,
      userInput: buildAutomationKnowledgeInput(payload.documentText.trim(), payload.question.trim())
    });

    return NextResponse.json(nodeResult);
  } catch (error) {
    return aiError(error);
  }
}
