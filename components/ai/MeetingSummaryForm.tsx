"use client";

import { useState } from "react";
import { AiFormShell } from "./AiFormShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";

export function MeetingSummaryForm() {
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setResult("");
    setIsLoading(true);
    try {
      const response = await fetch("/api/ai/meeting-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "會議摘要產生失敗。");
      }
      setResult(payload.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "會議摘要產生失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AiFormShell
      buttonLabel="產生摘要"
      description="貼上會議逐字稿或筆記，整理成可追蹤的專案摘要。"
      error={error}
      isLoading={isLoading}
      onSubmit={handleSubmit}
      result={result}
      title="會議摘要"
    >
      <div className="field-group">
        <label htmlFor="meeting-content">會議紀錄或逐字稿</label>
        <textarea
          id="meeting-content"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setContent(event.target.value)}
          placeholder="貼上會議內容..."
          value={content}
        />
        <div className="char-count">
          {content.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiFormShell>
  );
}
