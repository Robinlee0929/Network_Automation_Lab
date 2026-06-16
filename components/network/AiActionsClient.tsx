"use client";

import { BrainCircuit, ClipboardCheck, Play } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { AvailableAction, NetworkJob, ParseResultRecord } from "@/lib/network-ai/schemas";

type ParseResponse = {
  parseResult: ParseResultRecord | null;
};

export function AiActionsClient({ actions }: { actions: AvailableAction[] }) {
  const [userRequest, setUserRequest] = useState("");
  const [inventoryText, setInventoryText] = useState("");
  const [parseResult, setParseResult] = useState<ParseResultRecord | null>(null);
  const [createdJob, setCreatedJob] = useState<NetworkJob | null>(null);
  const [error, setError] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingLatest, setIsLoadingLatest] = useState(false);

  const output = parseResult?.output ?? null;
  const recommendedAction = actions.find((action) => action.id === output?.recommendedActionId) ?? null;
  const canCreateJob = Boolean(output?.jobCreationAllowed && output.recommendedActionId);
  const disabledReason =
    output && !output.jobCreationAllowed
      ? output.blockedReason ??
        (output.missingFields.length
          ? `Missing: ${output.missingFields.join(", ")}`
          : "Job creation is not allowed for this parsed request.")
      : "";

  function parseOptionalJson(text: string) {
    if (!text.trim()) {
      return undefined;
    }
    return JSON.parse(text);
  }

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
          setUserRequest(payload.parseResult.userRequest);
          setInventoryText(
            payload.parseResult.deviceInventorySnapshot
              ? JSON.stringify(payload.parseResult.deviceInventorySnapshot, null, 2)
              : ""
          );
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

  async function parseRequest() {
    setIsParsing(true);
    setError("");
    setCreatedJob(null);
    try {
      const response = await fetch("/api/network/ai/parse-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userRequest,
          deviceInventory: parseOptionalJson(inventoryText),
          availableActions: actions
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Parse request failed.");
      }
      setParseResult(payload.parseResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Parse request failed.");
    } finally {
      setIsParsing(false);
    }
  }

  async function createJob() {
    if (!output?.recommendedActionId || !output.targetDevice) {
      return;
    }

    setIsCreating(true);
    setError("");
    try {
      const response = await fetch("/api/network/jobs/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          actionId: output.recommendedActionId,
          targetDevice: output.targetDevice,
          vendor: output.vendor,
          deviceInventory: parseOptionalJson(inventoryText),
          params: {
            source: "ai-actions",
            parseResultId: parseResult?.id,
            intent: output.intent,
            interfaceName: output.interfaceName,
            vlanId: output.vlanId
          }
        })
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Create job failed.");
      }
      setCreatedJob(payload.job);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Create job failed.");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="network-grid">
      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Network Request Parser</h2>
          <button className="icon-action-button" disabled={isParsing || !userRequest.trim()} onClick={parseRequest} type="button">
            <BrainCircuit aria-hidden="true" size={18} />
            <span>{isParsing ? "Parsing" : "Parse"}</span>
          </button>
        </div>
        <label className="network-field">
          <span>User request</span>
          <textarea
            onChange={(event) => setUserRequest(event.target.value)}
            placeholder="例如：幫我檢查 core-switch Gi0/1 的介面狀態"
            value={userRequest}
          />
        </label>
        <label className="network-field">
          <span>Device inventory JSON</span>
          <textarea
            className="compact-textarea"
            onChange={(event) => setInventoryText(event.target.value)}
            placeholder='{"devices":[{"name":"core-switch","vendor":"cisco"}]}'
            value={inventoryText}
          />
        </label>
        {error && <div className="error-box">{error}</div>}
        {isLoadingLatest && <div className="status-strip">Loading latest parse result...</div>}
      </section>

      <section className="network-panel">
        <div className="network-toolbar">
          <h2>Recommendation</h2>
          <button className="icon-action-button" disabled={!canCreateJob || isCreating} onClick={createJob} type="button">
            <Play aria-hidden="true" size={18} />
            <span>{isCreating ? "Creating" : "Create Job"}</span>
          </button>
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
            <dt>Job Allowed</dt>
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
        {disabledReason && <div className="status-strip">{disabledReason}</div>}
        {output?.missingFields.length ? (
          <div className="status-strip">Missing: {output.missingFields.join(", ")}</div>
        ) : null}
        {createdJob && (
          <div className="status-strip">
            <ClipboardCheck aria-hidden="true" size={18} />
            Job {createdJob.id} is {createdJob.status}.{" "}
            <Link href="/network/jobs">View Jobs</Link>
          </div>
        )}
        <pre className="network-pre">
          {parseResult
            ? JSON.stringify(parseResult.output, null, 2)
            : "Parse output JSON will appear here."}
        </pre>
      </section>

      <section className="network-panel network-panel-wide">
        <div className="network-toolbar">
          <h2>Available Actions</h2>
          <span>{actions.length} allowlisted</span>
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
