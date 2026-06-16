"use client";

import { useState } from "react";
import { AiNodeShell } from "./AiNodeShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";
import type { AiNodeResponse, KnowledgeQaNodeOutput } from "@/lib/ai/schemas";

export function KnowledgeQaNode() {
  const [documentText, setDocumentText] = useState("");
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AiNodeResponse<KnowledgeQaNodeOutput> | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runNode() {
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      const response = await fetch("/api/automation/ai/kb-qa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentText, question })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Knowledge QA Node 執行失敗。");
      }
      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Knowledge QA Node 執行失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  const output = result?.output;

  return (
    <AiNodeShell
      buttonLabel="Run Node"
      description="輸入 documentText 與 question，輸出答案、依據、不足判斷與下一步建議。"
      error={error}
      isLoading={isLoading}
      nodeName="POST /api/automation/ai/kb-qa"
      onRun={runNode}
      rawJson={result?.rawJson || ""}
      readableOutput={
        output ? (
          <div>
            <p><strong>Answer:</strong> {output.answer}</p>
            <p><strong>Insufficient Info:</strong> {String(output.insufficientInfo)}</p>
            <h4>Evidence</h4>
            <ul>{output.evidence.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Suggested Next Step</h4>
            <p>{output.suggestedNextStep}</p>
          </div>
        ) : (
          <p className="empty-output">執行後會顯示人類可讀問答結果。</p>
        )
      }
      title="Knowledge QA Node"
    >
      <div className="field-group">
        <label htmlFor="knowledge-node-document">documentText</label>
        <textarea
          id="knowledge-node-document"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setDocumentText(event.target.value)}
          placeholder="貼上 SOP、政策或文件內容..."
          value={documentText}
        />
        <div className="char-count">
          {documentText.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
      <div className="field-group">
        <label htmlFor="knowledge-node-question">question</label>
        <textarea
          className="knowledge-question"
          id="knowledge-node-question"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="輸入要根據文件回答的問題..."
          value={question}
        />
        <div className="char-count">
          {question.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiNodeShell>
  );
}
