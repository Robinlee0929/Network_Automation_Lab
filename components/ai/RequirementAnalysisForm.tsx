"use client";

import { useState } from "react";
import { AiFormShell } from "./AiFormShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";

export function RequirementAnalysisForm() {
  const [content, setContent] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setResult("");
    setIsLoading(true);
    try {
      const response = await fetch("/api/ai/requirement-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "需求整理失敗。");
      }
      setResult(payload.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "需求整理失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AiFormShell
      buttonLabel="整理需求"
      description="把原始需求轉成設計與開發可以審閱的規格草稿。"
      error={error}
      isLoading={isLoading}
      onSubmit={handleSubmit}
      result={result}
      title="需求整理"
    >
      <div className="field-group">
        <label htmlFor="requirement-content">原始需求</label>
        <textarea
          id="requirement-content"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setContent(event.target.value)}
          placeholder="貼上使用者需求、訪談紀錄或 issue 描述..."
          value={content}
        />
        <div className="char-count">
          {content.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiFormShell>
  );
}
