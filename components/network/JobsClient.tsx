"use client";

import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import type { NetworkJob } from "@/lib/network-ai/schemas";

export function JobsClient({ initialJobs }: { initialJobs: NetworkJob[] }) {
  const [jobs, setJobs] = useState(initialJobs);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function refreshJobs(options: { quiet?: boolean } = {}) {
    setIsLoading(true);
    if (!options.quiet) {
      setError("");
    }
    try {
      const response = await fetch("/api/network/jobs");
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Refresh jobs failed.");
      }
      setJobs(payload.jobs);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Refresh jobs failed.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refreshJobs({ quiet: true });
  }, []);

  return (
    <section className="network-panel network-panel-wide">
      <div className="network-toolbar">
        <h2>Network Jobs</h2>
        <button className="icon-action-button" disabled={isLoading} onClick={() => refreshJobs()} type="button">
          <RefreshCcw aria-hidden="true" size={18} />
          <span>{isLoading ? "Refreshing" : "Refresh"}</span>
        </button>
      </div>
      {error && <div className="error-box">{error}</div>}
      <div className="job-table" role="table" aria-label="Network jobs">
        <div className="job-row job-row-head" role="row">
          <span>Job</span>
          <span>Status</span>
          <span>Action</span>
          <span>Target</span>
          <span>Vendor</span>
          <span>Risk</span>
          <span>Approval</span>
          <span>Created</span>
          <span>Source</span>
        </div>
        {jobs.map((job) => (
          <div className="job-row" key={job.id} role="row">
            <span>{job.id}</span>
            <span>{job.blockedReason ? `${job.status}: ${job.blockedReason}` : job.status}</span>
            <span>{job.actionId}</span>
            <span>{job.targetDevice ?? "N/A"}</span>
            <span>{job.vendor ?? "unknown"}</span>
            <span>{job.riskLevel}</span>
            <span>{job.requiresApproval ? "required" : "not required"}</span>
            <span>{job.createdAt}</span>
            <span>{job.parseResultId ?? job.source ?? "manual"}</span>
          </div>
        ))}
      </div>
      <div className="status-strip">Runner not enabled in Phase 1.</div>
      {!jobs.length && <p className="muted-copy">No jobs have been created in this server session.</p>}
    </section>
  );
}
