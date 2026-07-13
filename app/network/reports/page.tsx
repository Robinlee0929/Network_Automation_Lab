import { NetworkNav } from "@/components/network/NetworkNav";
import { ReportsClient } from "@/components/network/ReportsClient";
import { importDayResults } from "@/lib/network-ai/dayResults";

export default function NetworkReportsPage() {
  const reports = importDayResults();

  return (
    <main className="network-page">
      <header className="network-header">
        <div>
          <p className="eyebrow">Network Automation AI Node</p>
          <h1>Reports</h1>
        </div>
        <NetworkNav />
      </header>
      <ReportsClient reports={reports} />
    </main>
  );
}
