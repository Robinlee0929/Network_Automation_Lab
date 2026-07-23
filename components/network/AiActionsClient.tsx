"use client";

import { useEffect, useMemo, useState } from "react";
import type { AvailableAction } from "@/lib/network-ai/schemas";
import { AiActionsStage0Presentation } from "./Phase2N04DemoPresentation";
import {
  projectActionCatalog,
  projectParseResult
} from "./Phase2O05SafePresentation";

function parseResultFromPayload(value: unknown) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  return "parseResult" in value ? value.parseResult : null;
}

export function AiActionsClient({ actions }: { actions: AvailableAction[] }) {
  const [parseResult, setParseResult] = useState<unknown>(null);
  const [readError, setReadError] = useState(false);
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);
  const catalog = useMemo(() => projectActionCatalog(actions), [actions]);
  const recorded = useMemo(() => projectParseResult(parseResult), [parseResult]);

  useEffect(() => {
    let ignore = false;

    async function loadLatestParseResult() {
      setIsLoadingLatest(true);
      setReadError(false);
      try {
        const response = await fetch("/api/network/ai/parse-request/latest");
        const payload: unknown = await response.json();
        if (!response.ok) {
          throw new Error("Recorded parse read failed.");
        }
        if (!ignore) {
          setParseResult(parseResultFromPayload(payload));
        }
      } catch {
        if (!ignore) {
          setParseResult(null);
          setReadError(true);
        }
      } finally {
        if (!ignore) {
          setIsLoadingLatest(false);
        }
      }
    }

    loadLatestParseResult();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="network-grid">
      <AiActionsStage0Presentation />

      <section
        className="network-panel"
        aria-labelledby="recorded-recommendation-heading"
      >
        <div className="network-toolbar">
          <h2 id="recorded-recommendation-heading">Recorded Recommendation</h2>
          <span>UNAVAILABLE — parsing and execution</span>
        </div>

        {isLoadingLatest ? (
          <p className="safe-state" data-state="loading" role="status">
            Loading the recorded parse result…
          </p>
        ) : null}
        {readError ? (
          <p className="safe-state" data-state="error" role="alert">
            Unable to read the recorded parse result.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && recorded.state === "EMPTY" ? (
          <p className="safe-state" data-state="empty" role="status">
            EMPTY — No recorded parse result is available. Provider parsing remains
            UNAVAILABLE in Stage 0.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && recorded.state === "REJECTED" ? (
          <p className="safe-state" data-state="rejected" role="status">
            REJECTED — recorded parse detail is unavailable.
          </p>
        ) : null}
        {!isLoadingLatest && !readError && recorded.state === "AVAILABLE" ? (
          <>
            <p className="safe-state" data-state="available" role="status">
              Recorded recommendation available · non-executing.
            </p>
            <dl className="detail-grid">
              <div>
                <dt>Intent</dt>
                <dd>{recorded.intent}</dd>
              </div>
              <div>
                <dt>Catalog recommendation</dt>
                <dd>{recorded.recommendation}</dd>
              </div>
              <div>
                <dt>Risk</dt>
                <dd>{recorded.risk}</dd>
              </div>
              <div>
                <dt>Approval</dt>
                <dd>{recorded.approvalFlag}</dd>
              </div>
              <div>
                <dt>Safety</dt>
                <dd>{recorded.safetyResult}</dd>
              </div>
              <div>
                <dt>Job eligibility</dt>
                <dd>{recorded.jobEligibility}</dd>
              </div>
              <div>
                <dt>Reason</dt>
                <dd>{recorded.reason}</dd>
              </div>
              <div>
                <dt>Date</dt>
                <dd>{recorded.recordedDate}</dd>
              </div>
            </dl>
            <div>
              <h3>Recorded missing-field flags</h3>
              <ul className="safe-flag-list">
                {recorded.missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
            </div>
            <p className="safe-state" data-state="unavailable">
              Recorded detail withheld; parsing, approval, and job creation are
              unavailable.
            </p>
          </>
        ) : null}
      </section>

      <section
        className="network-panel network-panel-wide"
        aria-labelledby="allowlist-reference-heading"
      >
        <div className="network-toolbar">
          <h2 id="allowlist-reference-heading">Allowlist Reference</h2>
          <span>
            {catalog.length} static catalog entr
            {catalog.length === 1 ? "y" : "ies"}
          </span>
        </div>

        <p className="safe-state" data-state="unavailable">
          UNAVAILABLE — no request, provider, approval, job creation, or execution
          control exists on this surface.
        </p>

        {catalog.length ? (
          <div className="action-grid">
            {catalog.map((action) => (
              <article className="action-card" key={action.id}>
                <h3>{action.label}</h3>
                <p className="safe-catalog-id">Static catalog ID: {action.id}</p>
                <p>{action.reviewerCopy}</p>
                <ul className="safe-flag-list">
                  <li>{action.readOnly}</li>
                  <li>{action.configurationCapability}</li>
                  <li>{action.risk}</li>
                </ul>
              </article>
            ))}
          </div>
        ) : (
          <p className="safe-state" data-state="empty" role="status">
            EMPTY — No static action references available.
          </p>
        )}
      </section>
    </div>
  );
}
