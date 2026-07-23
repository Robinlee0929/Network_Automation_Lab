"use client";

import { FileJson } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { AnalysisRecord, DayResult } from "@/lib/network-ai/schemas";
import { EvidenceStage0Presentation } from "./Phase2N04DemoPresentation";
import {
  projectAnalysisRecord,
  projectEvidenceCollection,
  type SafeEvidenceItem,
  type SafeRecordedStatus
} from "./Phase2O05SafePresentation";

type StatusFilter = "ALL" | SafeRecordedStatus;

const statusOptions: StatusFilter[] = [
  "ALL",
  "PASS",
  "WARN",
  "FAIL",
  "BLOCKED",
  "REVIEW",
  "UNKNOWN"
];

function analysisFromPayload(value: unknown) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  return "analysis" in value ? (value.analysis as unknown) : null;
}

function groupedEvidence(items: SafeEvidenceItem[]) {
  return items.reduce<Array<{ category: string; items: SafeEvidenceItem[] }>>(
    (groups, item) => {
      const existing = groups.find((group) => group.category === item.category);
      if (existing) {
        existing.items.push(item);
      } else {
        groups.push({ category: item.category, items: [item] });
      }
      return groups;
    },
    []
  );
}

export function DayResultsClient({ results }: { results: DayResult[] }) {
  const collection = useMemo(() => projectEvidenceCollection(results), [results]);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const [selectedId, setSelectedId] = useState(collection.items[0]?.internalId ?? "");
  const [analysis, setAnalysis] = useState<AnalysisRecord | unknown | null>(null);
  const [readError, setReadError] = useState(false);
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);

  const visibleItems = useMemo(
    () =>
      statusFilter === "ALL"
        ? collection.items
        : collection.items.filter((item) => item.status === statusFilter),
    [collection.items, statusFilter]
  );
  const selected =
    visibleItems.find((item) => item.internalId === selectedId) ??
    visibleItems[0] ??
    null;
  const groups = useMemo(() => groupedEvidence(visibleItems), [visibleItems]);
  const safeAnalysis = useMemo(() => projectAnalysisRecord(analysis), [analysis]);

  useEffect(() => {
    let ignore = false;

    async function loadLatestAnalysis(reportId: string) {
      setIsLoadingLatest(true);
      setAnalysis(null);
      setReadError(false);
      try {
        const response = await fetch(
          `/api/network/reports/${encodeURIComponent(reportId)}/analysis/latest`
        );
        const payload: unknown = await response.json();
        if (!response.ok) {
          throw new Error("Recorded analysis read failed.");
        }
        if (!ignore) {
          setAnalysis(analysisFromPayload(payload));
        }
      } catch {
        if (!ignore) {
          setAnalysis(null);
          setReadError(true);
        }
      } finally {
        if (!ignore) {
          setIsLoadingLatest(false);
        }
      }
    }

    if (selected?.internalId) {
      loadLatestAnalysis(selected.internalId);
    } else {
      setAnalysis(null);
      setReadError(false);
    }

    return () => {
      ignore = true;
    };
  }, [selected?.internalId]);

  return (
    <div className="network-grid">
      <EvidenceStage0Presentation />

      <section className="network-panel" aria-labelledby="evidence-collection-heading">
        <div className="network-toolbar">
          <h2 id="evidence-collection-heading">Imported Evidence</h2>
          <span role="status" aria-live="polite">
            {visibleItems.length} safely displayable item
            {visibleItems.length === 1 ? "" : "s"}
          </span>
        </div>

        <div className="safe-filter-bar">
          <label htmlFor="evidence-status-filter">
            Recorded status
            <select
              id="evidence-status-filter"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status === "ALL" ? "All recorded statuses" : status}
                </option>
              ))}
            </select>
          </label>
          <button
            className="safe-secondary-button"
            type="button"
            onClick={() => {
              setStatusFilter("ALL");
              setSelectedId(collection.items[0]?.internalId ?? "");
            }}
          >
            Reset evidence view
          </button>
        </div>

        {collection.rejectedCount > 0 ? (
          <p className="safe-state" data-state="rejected" role="status">
            REJECTED — {collection.rejectedCount} recorded item
            {collection.rejectedCount === 1 ? "" : "s"} withheld as malformed.
          </p>
        ) : null}

        <div className="result-list">
          {groups.map((group) => (
            <div className="evidence-group" key={group.category}>
              <h3>{group.category}</h3>
              {group.items.map((item) => (
                <button
                  aria-pressed={item.internalId === selected?.internalId}
                  className="result-row evidence-row"
                  data-active={item.internalId === selected?.internalId}
                  key={item.internalId}
                  onClick={() => setSelectedId(item.internalId)}
                  type="button"
                >
                  <FileJson aria-hidden="true" size={18} />
                  <span>
                    <strong>{item.category}</strong>
                    <small>
                      {item.dayLabel} · Recorded result: {item.status}
                    </small>
                    <small>Recorded: {item.recordedDate}</small>
                  </span>
                  <b className="kind-badge">Recorded evidence</b>
                  <em className="status-badge" data-tone={item.statusTone}>
                    {item.status}
                  </em>
                </button>
              ))}
            </div>
          ))}
        </div>

        {collection.state === "EMPTY" ? (
          <p className="safe-state" data-state="empty" role="status">
            EMPTY — no recorded evidence is available in the local collection.
          </p>
        ) : null}
        {collection.state === "ERROR" ? (
          <p className="safe-state" data-state="error" role="alert">
            ERROR — no safely displayable recorded evidence.
          </p>
        ) : null}
        {collection.state === "AVAILABLE" && visibleItems.length === 0 ? (
          <p className="safe-state" data-state="empty" role="status">
            EMPTY — no matching recorded evidence.
          </p>
        ) : null}
      </section>

      <section className="network-panel" aria-labelledby="selected-evidence-heading">
        <div className="network-toolbar">
          <h2 id="selected-evidence-heading">Selected Evidence</h2>
          <span>Recorded evidence · non-executing</span>
        </div>
        {selected ? (
          <>
            <dl className="detail-grid">
              <div>
                <dt>Artifact category</dt>
                <dd>{selected.category}</dd>
              </div>
              <div>
                <dt>Recorded grouping</dt>
                <dd>{selected.dayLabel}</dd>
              </div>
              <div>
                <dt>Recorded result</dt>
                <dd>
                  <span className="status-badge" data-tone={selected.statusTone}>
                    {selected.status}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Recorded date</dt>
                <dd>{selected.recordedDate}</dd>
              </div>
              <div>
                <dt>Source identity</dt>
                <dd>Source path and device identity withheld</dd>
              </div>
              <div>
                <dt>Technical detail</dt>
                <dd>Technical payload is not displayed on this surface</dd>
              </div>
            </dl>
            {selected.malformed ? (
              <p className="safe-state" data-state="rejected" role="status">
                REJECTED — malformed local evidence.
              </p>
            ) : null}
          </>
        ) : (
          <p className="safe-state" data-state="empty">
            EMPTY — no evidence selected.
          </p>
        )}
      </section>

      <section
        className="network-panel network-panel-wide"
        aria-labelledby="recorded-analysis-heading"
      >
        <div className="network-toolbar">
          <h2 id="recorded-analysis-heading">Historical Analysis Record</h2>
          <span>UNAVAILABLE — provider analysis</span>
        </div>

        {isLoadingLatest ? (
          <p className="safe-state" data-state="loading" role="status">
            Loading the recorded analysis…
          </p>
        ) : null}
        {readError ? (
          <p className="safe-state" data-state="error" role="alert">
            Unable to read the recorded analysis.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && safeAnalysis.state === "EMPTY" ? (
          <p className="safe-state" data-state="empty" role="status">
            No recorded analysis. Provider analysis remains UNAVAILABLE in Stage 0.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && safeAnalysis.state === "REJECTED" ? (
          <p className="safe-state" data-state="rejected" role="status">
            REJECTED — recorded analysis detail is unavailable.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && safeAnalysis.state === "AVAILABLE" ? (
          <>
            <p className="safe-state" data-state="available" role="status">
              Recorded analysis available. Recorded detail is limited to approved
              presentation fields.
            </p>
            <dl className="detail-grid">
              <div>
                <dt>Risk</dt>
                <dd>{safeAnalysis.risk}</dd>
              </div>
              <div>
                <dt>Approval</dt>
                <dd>{safeAnalysis.approvalFlag}</dd>
              </div>
              <div>
                <dt>Human review</dt>
                <dd>{safeAnalysis.humanReviewFlag}</dd>
              </div>
              <div>
                <dt>Job eligibility</dt>
                <dd>{safeAnalysis.jobEligibility}</dd>
              </div>
              <div>
                <dt>Date</dt>
                <dd>{safeAnalysis.recordedDate}</dd>
              </div>
              <div>
                <dt>Current capability</dt>
                <dd>Provider analysis and job creation unavailable in Stage 0</dd>
              </div>
            </dl>
          </>
        ) : null}
      </section>
    </div>
  );
}
