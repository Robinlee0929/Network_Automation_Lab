import { NextResponse } from "next/server";
import { generateAiDraft, aiError, validationError } from "@/lib/ai/routeHandler";
import { buildKnowledgeQaInput, knowledgeQaPrompt } from "@/lib/ai/prompts";
import { validateKnowledgePayload } from "@/lib/ai/validators";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateKnowledgePayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const payload = body as { document: string; question: string };
    const draft = await generateAiDraft({
      systemPrompt: knowledgeQaPrompt,
      userInput: buildKnowledgeQaInput(payload.document.trim(), payload.question.trim())
    });

    return NextResponse.json(draft);
  } catch (error) {
    return aiError(error);
  }
}
