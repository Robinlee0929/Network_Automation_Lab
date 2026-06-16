"use client";

import { useState } from "react";
import { AiNodeShell } from "./AiNodeShell";
import { MAX_INPUT_CHARS } from "@/lib/ai/validators";
import type { AiNodeResponse, MeetingSummaryNodeOutput } from "@/lib/ai/schemas";

export function MeetingSummaryNode() {
  const [meetingText, setMeetingText] = useState("");
  const [result, setResult] = useState<AiNodeResponse<MeetingSummaryNodeOutput> | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function runNode() {
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      const response = await fetch("/api/automation/ai/meeting-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meetingText })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Meeting Summary Node 執行失敗。");
      }
      setResult(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Meeting Summary Node 執行失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  const output = result?.output;

  return (
    <AiNodeShell
      buttonLabel="Run Node"
      description="輸入 meetingText，輸出摘要、決議、任務、風險與追問問題。"
      error={error}
      isLoading={isLoading}
      nodeName="POST /api/automation/ai/meeting-summary"
      onRun={runNode}
      rawJson={result?.rawJson || ""}
      readableOutput={
        output ? (
          <div>
            <p><strong>Summary:</strong> {output.summary}</p>
            <h4>Decisions</h4>
            <ul>{output.decisions.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Tasks</h4>
            <ul>
              {output.tasks.map((task) => (
                <li key={`${task.title}-${task.owner}`}>
                  {task.title} | {task.owner} | {task.dueDate} | {task.status}
                </li>
              ))}
            </ul>
            <h4>Risks</h4>
            <ul>{output.risks.map((item) => <li key={item}>{item}</li>)}</ul>
            <h4>Follow-up Questions</h4>
            <ul>{output.followUpQuestions.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        ) : (
          <p className="empty-output">執行後會顯示人類可讀摘要。</p>
        )
      }
      title="Meeting Summary Node"
    >
      <div className="field-group">
        <label htmlFor="meeting-node-input">meetingText</label>
        <textarea
          id="meeting-node-input"
          maxLength={MAX_INPUT_CHARS}
          onChange={(event) => setMeetingText(event.target.value)}
          placeholder="貼上會議紀錄或逐字稿..."
          value={meetingText}
        />
        <div className="char-count">
          {meetingText.length.toLocaleString()} / {MAX_INPUT_CHARS.toLocaleString()} characters
        </div>
      </div>
    </AiNodeShell>
  );
}
