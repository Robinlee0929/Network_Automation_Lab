import { NextResponse } from "next/server";
import { getOpenAIClient, getOpenAIModel } from "./openaiClient";
import { AI_DRAFT_NOTICE } from "./prompts";
import { ensureHumanReview, type AiNodeResponse } from "./schemas";

type GenerateAiDraftOptions = {
  systemPrompt: string;
  userInput: string;
};

function normalizeDraft(text: string) {
  const trimmed = text.trim();
  if (trimmed.startsWith(AI_DRAFT_NOTICE)) {
    return trimmed;
  }

  return `${AI_DRAFT_NOTICE}\n\n${trimmed}`;
}

export async function generateAiDraft({ systemPrompt, userInput }: GenerateAiDraftOptions) {
  const client = getOpenAIClient();
  const model = getOpenAIModel();

  const response = await client.responses.create({
    model,
    input: [
      {
        role: "system",
        content: systemPrompt
      },
      {
        role: "user",
        content: userInput
      }
    ]
  });

  const result = response.output_text?.trim();
  if (!result) {
    throw new Error("OpenAI response did not include text output.");
  }

  return {
    model,
    result: normalizeDraft(result)
  };
}

function extractJsonObject(text: string) {
  const trimmed = text.trim();
  const fencedMatch = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  if (fencedMatch) {
    return fencedMatch[1].trim();
  }

  const firstBrace = trimmed.indexOf("{");
  const lastBrace = trimmed.lastIndexOf("}");
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    return trimmed.slice(firstBrace, lastBrace + 1);
  }

  return trimmed;
}

export async function generateAiNodeJson<TOutput extends { needsHumanReview: boolean }>({
  nodeType,
  systemPrompt,
  userInput
}: GenerateAiDraftOptions & {
  nodeType: string;
}): Promise<AiNodeResponse<TOutput>> {
  const client = getOpenAIClient();
  const model = getOpenAIModel();

  const response = await client.responses.create({
    model,
    input: [
      {
        role: "system",
        content: systemPrompt
      },
      {
        role: "user",
        content: userInput
      }
    ]
  });

  const text = response.output_text?.trim();
  if (!text) {
    throw new Error("OpenAI response did not include JSON output.");
  }

  const rawJson = extractJsonObject(text);
  let parsed: TOutput;
  try {
    parsed = JSON.parse(rawJson) as TOutput;
  } catch {
    throw new Error("OpenAI response was not valid JSON.");
  }

  const output = ensureHumanReview(parsed);

  return {
    nodeType,
    draftNotice: AI_DRAFT_NOTICE,
    model,
    output,
    rawJson: JSON.stringify(output, null, 2)
  };
}

export function validationError(error: string) {
  return NextResponse.json({ error }, { status: 400 });
}

export function aiError(error: unknown) {
  const message = error instanceof Error ? error.message : "OpenAI API request failed.";
  return NextResponse.json({ error: message }, { status: 500 });
}
