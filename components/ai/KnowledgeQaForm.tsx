"use client";

import { useState } from "react";
import { AiFormShell } from "./AiFormShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";

export function KnowledgeQaForm() {
  const [document, setDocument] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setResult("");
    setIsLoading(true);
    try {
      const response = await fetch("/api/ai/kb-qa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document, question })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "知識庫問答失敗。");
      }
      setResult(payload.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "知識庫問答失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <AiFormShell
      buttonLabel="回答問題"
      description="根據貼上的 SOP 或文件內容回答，不足時明確標示不足。"
      error={error}
      isLoading={isLoading}
      onSubmit={handleSubmit}
      result={result}
      title="知識庫問答"
    >
      <div className="field-group">
        <label htmlFor="knowledge-document">SOP / 文件內容</label>
        <textarea
          id="knowledge-document"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setDocument(event.target.value)}
          placeholder="貼上 SOP、政策、流程或內部文件..."
          value={document}
        />
        <div className="char-count">
          {document.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
      <div className="field-group">
        <label htmlFor="knowledge-question">使用者問題</label>
        <textarea
          className="knowledge-question"
          id="knowledge-question"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="輸入想詢問的問題..."
          value={question}
        />
        <div className="char-count">
          {question.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiFormShell>
  );
}
