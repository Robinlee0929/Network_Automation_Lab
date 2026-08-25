"use client";

import { RefreshCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { NetworkJob } from "@/lib/network-ai/schemas";
import { projectJobsCollection } from "./Phase2O05SafePresentation";

function jobsFromPayload(value: unknown) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }
  return "jobs" in value ? value.jobs : null;
}

async function readJobs() {
  const response = await fetch("/api/network/jobs");
  const payload: unknown = await response.json();
  if (!response.ok) {
    throw new Error("Recorded jobs read failed.");
  }
  return jobsFromPayload(payload);
}

export function JobsClient({ initialJobs }: { initialJobs: NetworkJob[] }) {
  const [jobs, setJobs] = useState<unknown>(initialJobs);
  const [readError, setReadError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const collection = useMemo(() => projectJobsCollection(jobs), [jobs]);

  async function refreshJobs() {
    setIsLoading(true);
    setReadError(false);
    try {
      setJobs(await readJobs());
    } catch {
      setReadError(true);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let ignore = false;

    async function loadInitialJobs() {
      try {
        const initialRefresh = await readJobs();
        if (!ignore) {
          setJobs(initialRefresh);
        }
      } catch {
        if (!ignore) {
          setReadError(true);
        }
      } finally {
        if (!ignore) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialJobs();

    return () => {
      ignore = true;
    };
  }, []);

  return (
    <section
      className="network-panel network-panel-wide"
      aria-labelledby="recorded-jobs-heading"
    >
      <div className="network-toolbar">
        <h2 id="recorded-jobs-heading">Recorded Jobs</h2>
        <button
          className="icon-action-button"
          disabled={isLoading}
          onClick={() => refreshJobs()}
          type="button"
        >
          <RefreshCcw aria-hidden="true" size={18} />
          <span>{isLoading ? "Reloading recorded jobs" : "Reload recorded jobs"}</span>
        </button>
      </div>

      <p className="safe-state" data-state="unavailable" id="jobs-stage-0-boundary">
        UNAVAILABLE — runner, queue, scheduler, worker, approval, and execution
        capability are not present in Stage 0.
      </p>

      {isLoading ? (
        <p className="safe-state" data-state="loading" role="status">
          Reloading recorded local job metadata…
        </p>
      ) : null}
      {readError ? (
        <p className="safe-state" data-state="error" role="alert">
          Unable to read recorded jobs. Previously projected rows, if any, are stale
          local records.
        </p>
      ) : null}
      {collection.rejectedCount > 0 ? (
        <p className="safe-state" data-state="rejected" role="status">
          REJECTED — {collection.rejectedCount} recorded row
          {collection.rejectedCount === 1 ? "" : "s"} withheld as malformed.
        </p>
      ) : null}

      {collection.state === "AVAILABLE" ? (
        <div
          aria-describedby="jobs-stage-0-boundary"
          aria-label="Safely projected recorded jobs; scroll horizontally when needed"
          className="safe-table-scroll"
          role="region"
          tabIndex={0}
        >
          <table className="safe-job-table">
            <caption>Recorded local job metadata · non-executing</caption>
            <thead>
              <tr>
                <th scope="col">Recorded job ID</th>
                <th scope="col">Recorded status</th>
                <th scope="col">Catalog action</th>
                <th scope="col">Platform</th>
                <th scope="col">Risk</th>
                <th scope="col">Approval</th>
                <th scope="col">Read-only property</th>
                <th scope="col">Recorded date</th>
                <th scope="col">Recorded reason</th>
              </tr>
            </thead>
            <tbody>
              {collection.items.map((job) => (
                <tr key={job.internalKey}>
                  <td>{job.visibleId}</td>
                  <td>{job.status}</td>
                  <td>{job.action}</td>
                  <td>{job.platform}</td>
                  <td>{job.risk}</td>
                  <td>{job.approvalFlag}</td>
                  <td>{job.readOnly}</td>
                  <td>{job.recordedDate}</td>
                  <td>{job.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {collection.state === "EMPTY" ? (
        <p className="safe-state" data-state="empty" role="status">
          EMPTY — no recorded jobs in this local store.
        </p>
      ) : null}
      {collection.state === "ERROR" ? (
        <p className="safe-state" data-state="error" role="alert">
          ERROR — no safely displayable recorded jobs.
        </p>
      ) : null}
    </section>
  );
}
