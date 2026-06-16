"use client";

import { BrainCircuit, FileText } from "lucide-react";
import { useMemo, useState } from "react";
import type { AnalysisRecord, DayResult } from "@/lib/network-ai/schemas";

export function ReportsClient({ reports }: { reports: DayResult[] }) {
  const [selectedId, setSelectedId] = useState(reports[0]?.id ?? "");
  const [analysis, setAnalysis] = useState<AnalysisRecord | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const selected = useMemo(
    () => reports.find((report) => report.id === selectedId) ?? reports[0] ?? null,
    [reports, selectedId]
  );

  async function summarize() {
    if (!selected) {
      return;
    }

    setIsLoading(true);
    setError("");
    try {
      const response = await fetch("/api/network/ai/analyze-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reportId: selected.id,
          reportText: selected.rawOutput,
          deviceContext: selected
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "AI summary failed.");
      }
      setAnalysis(payload.analysis);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "AI summary failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="network-grid">
      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Report List</h2>
          <span>{reports.length}</span>
        </div>
        <div className="result-list">
          {reports.map((report) => (
            <button
              className="result-row"
              data-active={report.id === selected?.id}
              key={report.id}
              onClick={() => {
                setSelectedId(report.id);
                setAnalysis(null);
              }}
              type="button"
            >
              <FileText aria-hidden="true" size={18} />
              <span>
                <strong>{report.sourcePath}</strong>
                <small>{report.checkType}</small>
              </span>
              <em>{report.status}</em>
            </button>
          ))}
        </div>
      </section>

      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Raw Output</h2>
          <button className="icon-action-button" disabled={!selected || isLoading} onClick={summarize} type="button">
            <BrainCircuit aria-hidden="true" size={18} />
            <span>{isLoading ? "Summarizing" : "AI Summary"}</span>
          </button>
        </div>
        <pre className="network-pre">{selected?.rawOutput ?? "No report selected."}</pre>
        {error && <div className="error-box">{error}</div>}
      </section>

      <section className="network-panel network-panel-wide">
        <div className="network-toolbar">
          <h2>AI Summary</h2>
          <span>{analysis?.output.requiresApproval ? "approval" : "review"}</span>
        </div>
        {analysis ? (
          <div className="summary-output">
            <h3>{analysis.output.summary}</h3>
            <ul>
              {analysis.output.findings.map((finding) => (
                <li key={finding}>{finding}</li>
              ))}
            </ul>
            <pre className="network-pre">{JSON.stringify(analysis.output, null, 2)}</pre>
          </div>
        ) : (
          <pre className="network-pre">Run AI Summary to generate validated JSON.</pre>
        )}
      </section>
    </div>
  );
}
