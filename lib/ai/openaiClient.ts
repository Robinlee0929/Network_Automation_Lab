import OpenAI from "openai";

export const DEFAULT_OPENAI_MODEL = "gpt-5-mini";

export function getOpenAIModel() {
  return process.env.OPENAI_MODEL?.trim() || DEFAULT_OPENAI_MODEL;
}

export function getOpenAIClient() {
  const apiKey = process.env.OPENAI_API_KEY?.trim();

  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured. Add it to .env.local before using AI features.");
  }

  return new OpenAI({ apiKey });
}
