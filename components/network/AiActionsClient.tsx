"use client";

import { useEffect, useState } from "react";
import type { AvailableAction, ParseResultRecord } from "@/lib/network-ai/schemas";
import { AiActionsStage0Presentation } from "./Phase2N04DemoPresentation";

type ParseResponse = {
  parseResult: ParseResultRecord | null;
};

export function AiActionsClient({ actions }: { actions: AvailableAction[] }) {
  const [parseResult, setParseResult] = useState<ParseResultRecord | null>(null);
  const [error, setError] = useState("");
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);

  const output = parseResult?.output ?? null;
  const recommendedAction = actions.find((action) => action.id === output?.recommendedActionId) ?? null;

  useEffect(() => {
    let ignore = false;

    async function loadLatestParseResult() {
      setIsLoadingLatest(true);
      setError("");
      try {
        const response = await fetch("/api/network/ai/parse-request/latest");
        const payload = (await response.json()) as ParseResponse;
        if (!response.ok) {
          throw new Error("Load latest parse result failed.");
        }
        if (!ignore && payload.parseResult) {
          setParseResult(payload.parseResult);
        }
      } catch (caught) {
        if (!ignore) {
          setError(caught instanceof Error ? caught.message : "Load latest parse result failed.");
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
      <section className="network-panel">
        {error && <div className="error-box">{error}</div>}
        {isLoadingLatest && <div className="status-strip">Loading latest parse result...</div>}
      </section>

      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Recorded Recommendation</h2>
          <span>Read-only</span>
        </div>
        <dl className="detail-grid">
          <div>
            <dt>Intent</dt>
            <dd>{output?.intent ?? "unknown"}</dd>
          </div>
          <div>
            <dt>Action</dt>
            <dd>{recommendedAction?.id ?? "unknown"}</dd>
          </div>
          <div>
            <dt>Device</dt>
            <dd>{output?.targetDevice ?? "missing"}</dd>
          </div>
          <div>
            <dt>Approval</dt>
            <dd>{output?.requiresApproval ? "required" : "not required"}</dd>
          </div>
          <div>
            <dt>Vendor</dt>
            <dd>{output?.vendor ?? "unknown"}</dd>
          </div>
          <div>
            <dt>Recorded Job Eligibility</dt>
            <dd>{output?.jobCreationAllowed ? "yes" : "no"}</dd>
          </div>
          <div>
            <dt>Blocked Reason</dt>
            <dd>{output?.blockedReason ?? "none"}</dd>
          </div>
          <div>
            <dt>Missing Fields</dt>
            <dd>{output?.missingFields.length ? output.missingFields.join(", ") : "none"}</dd>
          </div>
          <div>
            <dt>Parse Result</dt>
            <dd>{parseResult?.id ?? "none"}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{parseResult?.createdAt ?? "none"}</dd>
          </div>
        </dl>
        {output?.missingFields.length ? (
          <div className="status-strip">Missing: {output.missingFields.join(", ")}</div>
        ) : null}
        <pre className="network-pre">
          {parseResult
            ? JSON.stringify(parseResult.output, null, 2)
            : "No recorded parse result is available."}
        </pre>
      </section>

      <section className="network-panel network-panel-wide">
        <div className="network-toolbar">
          <h2>Allowlist Reference</h2>
          <span>{actions.length} static entries</span>
        </div>
        <div className="action-grid">
          {actions.map((action) => (
            <article className="action-card" key={action.id}>
              <h3>{action.id}</h3>
              <p>{action.description}</p>
              <span>{action.readOnly ? "read-only" : "config-change"}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
