import { JobsClient } from "@/components/network/JobsClient";
import { NetworkNav } from "@/components/network/NetworkNav";
import { listNetworkJobs } from "@/lib/network-ai/jobs";

export default function NetworkJobsPage() {
  const jobs = listNetworkJobs();

  return (
    <main className="network-page">
      <header className="network-header">
        <div>
          <p className="eyebrow">Network Automation AI Node</p>
          <h1>Jobs</h1>
        </div>
        <NetworkNav />
      </header>
      <div className="network-grid">
        <JobsClient initialJobs={jobs} />
      </div>
    </main>
  );
}
