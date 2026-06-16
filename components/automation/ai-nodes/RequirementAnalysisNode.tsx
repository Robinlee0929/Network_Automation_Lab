"use client";

import { useState } from "react";
import { AiNodeShell } from "./AiNodeShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";
import type { AiNodeResponse, RequirementAnalysisNodeOutput } from "@/lib/ai/schemas";

export function RequirementAnalysisNode() {
  const [requirementText, setRequirementText] = useState("");
  const [result, setResult] = useState<AiNodeResponse<RequirementAnalysisNodeOutput> | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runNode() {
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      const response = await fetch("/api/automation/ai/requirement-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requirementText })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Requirement Analysis Node 執行失敗。");
      }
      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Requirement Analysis Node 執行失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  const output = result?.output;

  return (
    <AiNodeShell
      buttonLabel="Run Node"
      description="輸入 requirementText，輸出可接任務建立、審核與排程的需求 JSON。"
      error={error}
      isLoading={isLoading}
      nodeName="POST /api/automation/ai/requirement-analysis"
      onRun={runNode}
      rawJson={result?.rawJson || ""}
      readableOutput={
        output ? (
          <div>
            <p><strong>Summary:</strong> {output.summary}</p>
            <p><strong>Priority:</strong> {output.priority}</p>
            <h4>Modules</h4>
            <ul>{output.modules.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>User Stories</h4>
            <ul>{output.userStories.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Acceptance Criteria</h4>
            <ul>{output.acceptanceCriteria.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Missing Info</h4>
            <ul>{output.missingInfo.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Risks</h4>
            <ul>{output.risks.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        ) : (
          <p className="empty-output">執行後會顯示人類可讀需求整理。</p>
        )
      }
      title="Requirement Analysis Node"
    >
      <div className="field-group">
        <label htmlFor="requirement-node-input">requirementText</label>
        <textarea
          id="requirement-node-input"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setRequirementText(event.target.value)}
          placeholder="貼上原始需求、訪談紀錄或 issue 描述..."
          value={requirementText}
        />
        <div className="char-count">
          {requirementText.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiNodeShell>
  );
}
