"use client";

import { Braces, Play } from "lucide-react";
import type { ReactNode } from "react";

type AiNodeShellProps = {
  title: string;
  nodeName: string;
  description: string;
  children: ReactNode;
  readableOutput: ReactNode;
  rawJson: string;
  error: string;
  isLoading: boolean;
  buttonLabel: string;
  onRun: () => void;
};

export function AiNodeShell({
  title,
  nodeName,
  description,
  children,
  readableOutput,
  rawJson,
  error,
  isLoading,
  buttonLabel,
  onRun
}: AiNodeShellProps) {
  return (
    <div className="form-shell node-shell">
      <section className="form-panel" aria-label={title}>
        <div className="form-header">
          <div>
            <p className="node-name">{nodeName}</p>
            <h2>{title}</h2>
            <p>{description}</p>
          </div>
        </div>
        {children}
        <div className="form-footer">
          <button className="submit-button" disabled={isLoading} onClick={onRun} type="button">
            <Play aria-hidden="true" size={18} />
            <span>{isLoading ? "執行中..." : buttonLabel}</span>
          </button>
        </div>
        {error && (
          <div className="error-box" role="alert">
            {error}
          </div>
        )}
      </section>

      <section className="node-output-grid" aria-label={`${title}輸出`}>
        <div className="output-panel">
          <div className="output-toolbar">
            <h3>Human-readable Output</h3>
            <span className="draft-badge">AI 草稿，需人工確認</span>
          </div>
          <div className="readable-output">{readableOutput}</div>
        </div>

        <div className="output-panel">
          <div className="output-toolbar">
            <h3>Raw JSON Output</h3>
            <Braces aria-hidden="true" size={18} />
          </div>
          <pre className={`output-content json-output ${rawJson ? "" : "empty-output"}`}>
            {rawJson || "AI Node 執行後，workflow-ready JSON 會顯示在這裡。"}
          </pre>
        </div>
      </section>
    </div>
  );
}
