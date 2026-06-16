import { NextResponse } from "next/server";
import { generateAiNodeJson, aiError, validationError } from "@/lib/ai/routeHandler";
import {
  automationMeetingSummaryPrompt,
  buildAutomationMeetingInput
} from "@/lib/ai/prompts";
import { validateAutomationMeetingPayload } from "@/lib/ai/validators";
import type { MeetingSummaryNodeOutput } from "@/lib/ai/schemas";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const validation = validateAutomationMeetingPayload(body);
    if (!validation.ok) {
      return validationError(validation.error);
    }

    const meetingText = (body as { meetingText: string }).meetingText.trim();
    const nodeResult = await generateAiNodeJson<MeetingSummaryNodeOutput>({
      nodeType: "MeetingSummaryNode",
      systemPrompt: automationMeetingSummaryPrompt,
      userInput: buildAutomationMeetingInput(meetingText)
    });

    return NextResponse.json(nodeResult);
  } catch (error) {
    return aiError(error);
  }
}
