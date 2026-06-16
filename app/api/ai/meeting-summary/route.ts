import { NextResponse } from "next/server";
import { generateAiDraft, aiError, validationError } from "@/lib/ai/routeHandler";
import { buildMeetingSummaryInput, meetingSummaryPrompt } from "@/lib/ai/prompts";
import { validateMeetingPayload } from "@/lib/ai/validators";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateMeetingPayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const content = (body as { content: string }).content.trim();
    const draft = await generateAiDraft({
      systemPrompt: meetingSummaryPrompt,
      userInput: buildMeetingSummaryInput(content)
    });

    return NextResponse.json(draft);
  } catch (error) {
    return aiError(error);
  }
}
