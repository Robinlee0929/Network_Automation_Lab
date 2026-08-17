"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";
import type { AvailableAction } from "../../lib/network-ai/schemas";
import { AiActionsStage0Presentation } from "./Phase2N04DemoPresentation";
import {
  projectActionCatalog,
  projectParseResult,
  type SafeParseProjection
} from "./Phase2O05SafePresentation";

type AiActionsClientProps = {
  actions: AvailableAction[];
  maxRequestLength: number;
  providerDemoEnabled: boolean;
};

function parseResultFromPayload(value: unknown) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  return "parseResult" in value ? value.parseResult : null;
}

function RecommendationDetails({ result }: { result: SafeParseProjection }) {
  if (result.state === "EMPTY") {
    return null;
  }

  if (result.state === "REJECTED") {
    return (
      <p className="safe-state" data-state="rejected" role="status">
        REJECTED — recommendation detail is unavailable.
      </p>
    );
  }

  return (
    <>
      <p className="safe-state" data-state="available" role="status">
        Sanitized catalog recommendation available · non-executing.
      </p>
      <dl className="detail-grid">
        <div>
          <dt>Intent</dt>
          <dd>{result.intent}</dd>
        </div>
        <div>
          <dt>Recommended Action</dt>
          <dd>{result.recommendation}</dd>
        </div>
        <div>
          <dt>Risk</dt>
          <dd>{result.risk}</dd>
        </div>
        <div>
          <dt>Approval</dt>
          <dd>{result.approvalFlag}</dd>
        </div>
        <div>
          <dt>Safety Result</dt>
          <dd>{result.safetyResult}</dd>
        </div>
        <div>
          <dt>Job Eligibility</dt>
          <dd>{result.jobEligibility}</dd>
        </div>
        <div>
          <dt>Reason</dt>
          <dd>{result.reason}</dd>
        </div>
        <div>
          <dt>Date</dt>
          <dd>{result.recordedDate}</dd>
        </div>
      </dl>
      <div>
        <h3>Missing Fields</h3>
        <ul className="safe-flag-list">
          {result.missingFields.map((field) => (
            <li key={field}>{field}</li>
          ))}
        </ul>
      </div>
    </>
  );
}

export function AiActionsClient({
  actions,
  maxRequestLength,
  providerDemoEnabled
}: AiActionsClientProps) {
  const [parseResult, setParseResult] = useState<unknown>(null);
  const [previewResult, setPreviewResult] = useState<unknown>(null);
  const [userRequest, setUserRequest] = useState("");
  const [readError, setReadError] = useState(false);
  const [submitError, setSubmitError] = useState(false);
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const catalog = useMemo(() => projectActionCatalog(actions), [actions]);
  const recorded = useMemo(() => projectParseResult(parseResult), [parseResult]);
  const previewed = useMemo(() => projectParseResult(previewResult), [previewResult]);

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

  async function analyzeRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = userRequest.trim();
    if (!trimmed || trimmed.length > maxRequestLength) {
      setSubmitError(true);
      setPreviewResult(null);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(false);
    setPreviewResult(null);
    try {
      const response = await fetch("/api/network/ai/parse-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userRequest: trimmed })
      });
      const payload: unknown = await response.json();
      if (!response.ok) {
        throw new Error("Recommendation preview failed.");
      }
      setPreviewResult(parseResultFromPayload(payload));
      setParseResult(parseResultFromPayload(payload));
    } catch {
      setSubmitError(true);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="network-grid">
      {providerDemoEnabled ? (
        <section
          className="network-panel network-panel-wide"
          aria-labelledby="local-ai-preview-heading"
        >
          <div className="network-toolbar">
            <h2 id="local-ai-preview-heading">
              Optional Local AI Recommendation Preview
            </h2>
            <span>LOCAL OPT-IN · PROVIDER-BACKED · NO EXECUTION</span>
          </div>
          <p className="muted-copy">
            This preview may call the configured AI provider to classify a request.
            It does not create jobs, generate arbitrary CLI, contact devices, or
            execute network commands.
          </p>
          <p className="safe-state" data-state="unavailable">
            The server supplies a fixed synthetic LAB-DEMO-ROUTER inventory for
            local demonstration only. It is not production inventory or
            authorization.
          </p>
          <form onSubmit={analyzeRequest}>
            <div className="network-field">
              <label htmlFor="network-ai-user-request">
                Natural-language network request
              </label>
              <textarea
                className="compact-textarea"
                id="network-ai-user-request"
                maxLength={maxRequestLength}
                onChange={(event) => setUserRequest(event.target.value)}
                placeholder="Check WAN and LAN status for LAB-DEMO-ROUTER."
                required
                value={userRequest}
              />
            </div>
            <div className="form-footer">
              <p className="muted-copy">
                {userRequest.length}/{maxRequestLength} characters · request text is
                untrusted input
              </p>
              <button
                className="submit-button"
                disabled={isSubmitting || !userRequest.trim()}
                type="submit"
              >
                {isSubmitting ? "Analyzing…" : "Analyze request"}
              </button>
            </div>
          </form>
          {isSubmitting ? (
            <p className="safe-state" data-state="loading" role="status">
              Classifying the request and applying deterministic safety checks…
            </p>
          ) : null}
          {submitError ? (
            <p className="safe-state" data-state="error" role="alert">
              Unable to produce a safe recommendation. Check the request and local
              provider configuration.
            </p>
          ) : null}
          {!isSubmitting && !submitError ? (
            <RecommendationDetails result={previewed} />
          ) : null}
          {previewed.state === "AVAILABLE" ? (
            <p className="safe-state" data-state="unavailable">
              Recommendation review complete. This preview stops here: no job is
              created and no command or device operation is available.
            </p>
          ) : null}
        </section>
      ) : (
        <AiActionsStage0Presentation />
      )}

      <section
        className="network-panel"
        aria-labelledby="recorded-recommendation-heading"
      >
        <div className="network-toolbar">
          <h2 id="recorded-recommendation-heading">Recorded Recommendation</h2>
          <span>
            {providerDemoEnabled
              ? "Recorded metadata · non-executing"
              : "UNAVAILABLE — parsing and execution"}
          </span>
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
            {providerDemoEnabled
              ? "EMPTY — No recorded parse result is available."
              : "EMPTY — No recorded parse result is available. Provider parsing remains UNAVAILABLE in Stage 0."}
          </p>
        ) : null}
        {!isLoadingLatest && !readError ? (
          <RecommendationDetails result={recorded} />
        ) : null}
        {!isLoadingLatest && !readError && recorded.state === "AVAILABLE" ? (
          <p className="safe-state" data-state="unavailable">
            Recorded detail is safely projected; approval, job creation, and
            execution remain unavailable.
          </p>
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
          {providerDemoEnabled
            ? "The local preview can recommend only these server-owned catalog entries. Browser input cannot add or authorize an action."
            : "UNAVAILABLE — no request, provider, approval, job creation, or execution control exists on this surface."}
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
