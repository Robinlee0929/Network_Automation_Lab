"use client";

import { BrainCircuit, FileJson } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { AnalysisRecord, DayResult, DayResultKind } from "@/lib/network-ai/schemas";

type ExecutionBoundary = "report_only" | "read_only_action_candidate" | "approval_required" | "blocked";

const evidenceTypeLabels: Record<DayResultKind, string> = {
  device_report: "Device Check Report",
  phase_gate_report: "Readiness Gate Review",
  summary_report: "Project Summary",
  test_report: "Test Evidence",
  unknown: "Uncategorized Evidence"
};

const evidenceGroupLabels: Record<DayResultKind, string> = {
  device_report: "Device Check Reports",
  phase_gate_report: "Readiness Gate Reviews",
  test_report: "Test Evidence",
  summary_report: "Project Summaries",
  unknown: "Uncategorized Evidence"
};

const evidenceTypeRanks: Record<DayResultKind, number> = {
  device_report: 1,
  phase_gate_report: 2,
  test_report: 3,
  summary_report: 4,
  unknown: 5
};

const executionBoundaryLabels: Record<ExecutionBoundary, string> = {
  report_only: "Report-only",
  read_only_action_candidate: "Read-only candidate",
  approval_required: "Approval required",
  blocked: "Blocked"
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function getEvidenceTypeLabel(resultKind: DayResultKind) {
  return evidenceTypeLabels[resultKind] ?? evidenceTypeLabels.unknown;
}

export function getEvidenceTypeRank(resultKind: DayResultKind) {
  return evidenceTypeRanks[resultKind] ?? evidenceTypeRanks.unknown;
}

export function getSourceDayNumber(dayLabel: string | null | undefined, sourceDay?: string | null) {
  const source = sourceDay ?? dayLabel ?? "";
  const match = source.match(/day\s*[-_]?(\d{1,3})/i);
  return match ? Number(match[1]) : -1;
}

function evidenceTitle(result: DayResult) {
  const fallbackFile = result.sourcePath.split(/[\\/]/).pop();
  return result.reportTitle ?? result.checkType ?? fallbackFile ?? "Untitled Evidence";
}

function resultSource(result: DayResult) {
  return result.sourceDay ?? result.dayLabel ?? "Unknown Source";
}

function resultStatus(result: DayResult) {
  return result.status || "UNKNOWN";
}

function statusTone(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes("pass") || normalized.includes("success") || normalized === "ok") {
    return "success";
  }
  if (normalized.includes("warn") || normalized.includes("warning")) {
    return "warning";
  }
  if (normalized.includes("fail") || normalized.includes("block")) {
    return "danger";
  }
  return "neutral";
}

function boundaryTone(boundary: ExecutionBoundary) {
  if (boundary === "read_only_action_candidate") {
    return "info";
  }
  if (boundary === "approval_required") {
    return "warning";
  }
  if (boundary === "blocked") {
    return "danger";
  }
  return "neutral";
}

export function deriveExecutionBoundary(result: DayResult): ExecutionBoundary {
  if (
    result.resultKind === "phase_gate_report" ||
    result.resultKind === "summary_report" ||
    result.resultKind === "test_report"
  ) {
    return "report_only";
  }

  if (result.resultKind !== "device_report") {
    return "blocked";
  }

  if (!result.deviceName) {
    return "blocked";
  }

  if (isRecord(result.parsedResult)) {
    const risk = result.parsedResult.riskLevel ?? result.parsedResult.risk;
    const requiresApproval = result.parsedResult.requiresApproval;
    if (
      requiresApproval === true ||
      risk === "medium" ||
      risk === "high" ||
      resultStatus(result).toLowerCase().includes("fail")
    ) {
      return "approval_required";
    }
  }

  return "read_only_action_candidate";
}

export function sortEvidenceItems(items: DayResult[]) {
  return [...items].sort((left, right) => {
    const rankDelta = getEvidenceTypeRank(left.resultKind) - getEvidenceTypeRank(right.resultKind);
    if (rankDelta !== 0) {
      return rankDelta;
    }

    const dayDelta =
      getSourceDayNumber(right.dayLabel, right.sourceDay) -
      getSourceDayNumber(left.dayLabel, left.sourceDay);
    if (dayDelta !== 0) {
      return dayDelta;
    }

    const createdDelta = Date.parse(right.createdAt) - Date.parse(left.createdAt);
    if (Number.isFinite(createdDelta) && createdDelta !== 0) {
      return createdDelta;
    }

    return evidenceTitle(left).localeCompare(evidenceTitle(right));
  });
}

export function DayResultsClient({ results }: { results: DayResult[] }) {
  const sortedResults = useMemo(() => sortEvidenceItems(results), [results]);
  const [selectedId, setSelectedId] = useState(sortedResults[0]?.id ?? "");
  const [analysis, setAnalysis] = useState<AnalysisRecord | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);

  const selected = useMemo(
    () => sortedResults.find((result) => result.id === selectedId) ?? sortedResults[0] ?? null,
    [sortedResults, selectedId]
  );

  const groupedResults = useMemo(
    () =>
      sortedResults.reduce<Array<{ kind: DayResultKind; items: DayResult[] }>>((groups, result) => {
        const existing = groups.find((group) => group.kind === result.resultKind);
        if (existing) {
          existing.items.push(result);
        } else {
          groups.push({ kind: result.resultKind, items: [result] });
        }
        return groups;
      }, []),
    [sortedResults]
  );

  useEffect(() => {
    let ignore = false;

    async function loadLatestAnalysis(reportId: string) {
      setIsLoadingLatest(true);
      setAnalysis(null);
      setError("");
      try {
        const response = await fetch(
          `/api/network/reports/${encodeURIComponent(reportId)}/analysis/latest`
        );
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.error ?? "Load latest analysis failed.");
        }
        if (!ignore) {
          setAnalysis(payload.analysis ?? null);
        }
      } catch (caught) {
        if (!ignore) {
          setAnalysis(null);
          setError(caught instanceof Error ? caught.message : "Load latest analysis failed.");
        }
      } finally {
        if (!ignore) {
          setIsLoadingLatest(false);
        }
      }
    }

    if (selected?.id) {
      loadLatestAnalysis(selected.id);
    } else {
      setAnalysis(null);
    }

    return () => {
      ignore = true;
    };
  }, [selected?.id]);

  async function analyzeSelected() {
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
          deviceContext: {
            sourceDay: selected.sourceDay,
            dayLabel: selected.dayLabel,
            resultKind: selected.resultKind,
            deviceName: selected.deviceName,
            vendor: selected.vendor,
            checkType: selected.checkType,
            status: selected.status
          }
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Analyze report failed.");
      }
      setAnalysis(payload.analysis);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Analyze report failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="network-grid">
      <section className="network-panel network-panel-wide">
        <div className="status-strip" role="note">
          <strong>Stage 0 safe Demo · report-only · provider-unavailable.</strong>
          AI Analyze is excluded from this Demo; review evidence only and do not submit
          analysis.
        </div>
      </section>
      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Imported Evidence</h2>
          <span>{results.length} evidence items</span>
        </div>
        <div className="result-list">
          {groupedResults.map((group) => (
            <div className="evidence-group" key={group.kind}>
              <h3>{evidenceGroupLabels[group.kind]}</h3>
              {group.items.map((result) => {
                const boundary = deriveExecutionBoundary(result);
                const status = resultStatus(result);
                return (
                  <button
                    className="result-row evidence-row"
                    data-active={result.id === selected?.id}
                    key={result.id}
                    onClick={() => {
                      setSelectedId(result.id);
                    }}
                    type="button"
                  >
                    <FileJson aria-hidden="true" size={18} />
                    <span>
                      <strong>{getEvidenceTypeLabel(result.resultKind)}</strong>
                      <small>
                        {resultSource(result)} · {status} · {executionBoundaryLabels[boundary]}
                      </small>
                      <small>{evidenceTitle(result)}</small>
                    </span>
                    <b className="kind-badge">{result.resultKind}</b>
                    <em className="status-badge" data-tone={statusTone(status)}>
                      {status}
                    </em>
                  </button>
                );
              })}
            </div>
          ))}
          {!sortedResults.length && <p className="muted-copy">No JSON or TXT evidence found.</p>}
        </div>
      </section>

      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Selected Evidence</h2>
          <button className="icon-action-button" disabled={!selected || isLoading} onClick={analyzeSelected} type="button">
            <BrainCircuit aria-hidden="true" size={18} />
            <span>{isLoading ? "Analyzing" : analysis ? "Re-analyze" : "AI Analyze"}</span>
          </button>
        </div>
        {selected ? (
          <>
            <dl className="detail-grid">
              <div>
                <dt>Source</dt>
                <dd>{resultSource(selected)}</dd>
              </div>
              <div>
                <dt>Type</dt>
                <dd>
                  {getEvidenceTypeLabel(selected.resultKind)}
                  <small className="raw-kind">{selected.resultKind}</small>
                </dd>
              </div>
              <div>
                <dt>Target</dt>
                <dd>{selected.deviceName ?? "N/A"}</dd>
              </div>
              <div>
                <dt>Check</dt>
                <dd>{selected.checkType}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>
                  <span className="status-badge" data-tone={statusTone(resultStatus(selected))}>
                    {resultStatus(selected)}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Boundary</dt>
                <dd>
                  <span
                    className="boundary-badge"
                    data-tone={boundaryTone(deriveExecutionBoundary(selected))}
                  >
                    {executionBoundaryLabels[deriveExecutionBoundary(selected)]}
                  </span>
                </dd>
              </div>
            </dl>
            <h3 className="pre-heading">Raw Evidence JSON</h3>
            <pre className="network-pre">{selected.rawOutput}</pre>
          </>
        ) : (
          <p className="muted-copy">No evidence selected.</p>
        )}
        {error && <div className="error-box">{error}</div>}
      </section>

      <section className="network-panel network-panel-wide">
        <div className="network-toolbar">
          <h2>AI Analysis Record</h2>
          <span>{analysis?.output.riskLevel ?? (isLoadingLatest ? "loading" : "waiting")}</span>
        </div>
        {analysis ? (
          <>
            <dl className="detail-grid">
              <div>
                <dt>Analysis</dt>
                <dd>{analysis.id}</dd>
              </div>
              <div>
                <dt>Created</dt>
                <dd>{analysis.createdAt}</dd>
              </div>
              <div>
                <dt>Model</dt>
                <dd>{analysis.model}</dd>
              </div>
              <div>
                <dt>Job Allowed</dt>
                <dd>{analysis.safety.jobCreationAllowed ? "yes" : "no"}</dd>
              </div>
            </dl>
            {analysis.safety.reason && <div className="status-strip">{analysis.safety.reason}</div>}
            <pre className="network-pre">{JSON.stringify(analysis.output, null, 2)}</pre>
          </>
        ) : (
          <pre className="network-pre">
            {isLoadingLatest ? "Loading latest analysis..." : "尚未分析"}
          </pre>
        )}
      </section>
    </div>
  );
}
