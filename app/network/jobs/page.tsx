import { JobsClient } from "@/components/network/JobsClient";
import { listNetworkJobs } from "@/lib/network-ai/jobs";

export default function NetworkJobsPage() {
  const jobs = listNetworkJobs();

  return (
    <main className="network-page" id="network-primary-content" tabIndex={-1}>
      <header className="network-route-header">
        <h1>Jobs</h1>
      </header>
      <div className="network-grid">
        <JobsClient initialJobs={jobs} />
      </div>
    </main>
  );
}
