"use client";

import { Sparkles } from "lucide-react";
import type { ReactNode } from "react";

type AiFormShellProps = {
  title: string;
  description: string;
  children: ReactNode;
  result: string;
  error: string;
  isLoading: boolean;
  buttonLabel: string;
  onSubmit: () => void;
};

export function AiFormShell({
  title,
  description,
  children,
  result,
  error,
  isLoading,
  buttonLabel,
  onSubmit
}: AiFormShellProps) {
  return (
    <div className="form-shell">
      <section className="form-panel" aria-label={title}>
        <div className="form-header">
          <div>
            <h2>{title}</h2>
            <p>{description}</p>
          </div>
        </div>
        {children}
        <div className="form-footer">
          <button className="submit-button" disabled={isLoading} onClick={onSubmit} type="button">
            <Sparkles aria-hidden="true" size={18} />
            <span>{isLoading ? "產生中..." : buttonLabel}</span>
          </button>
        </div>
        {error && (
          <div className="error-box" role="alert">
            {error}
          </div>
        )}
      </section>

      <section className="output-panel" aria-label={`${title}輸出`}>
        <div className="output-toolbar">
          <h3>輸出結果</h3>
          <span className="draft-badge">AI 草稿，需人工確認</span>
        </div>
        <pre className={`output-content ${result ? "" : "empty-output"}`}>
          {result || "產生後的草稿會顯示在這裡。"}
        </pre>
      </section>
    </div>
  );
}
