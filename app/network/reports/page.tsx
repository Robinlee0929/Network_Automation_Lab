import { ReportsClient } from "@/components/network/ReportsClient";
import { importDayResults } from "@/lib/network-ai/dayResults";

export default function NetworkReportsPage() {
  const reports = importDayResults();

  return (
    <main className="network-page" id="network-primary-content" tabIndex={-1}>
      <header className="network-route-header">
        <h1>Reports</h1>
      </header>
      <ReportsClient reports={reports} />
    </main>
  );
}
