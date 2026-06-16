import { NetworkNav } from "@/components/network/NetworkNav";
import { DayResultsClient } from "@/components/network/DayResultsClient";
import { importDayResults } from "@/lib/network-ai/dayResults";

export default function NetworkDayResultsPage() {
  const results = importDayResults();

  return (
    <main className="network-page">
      <header className="network-header">
        <div>
          <p className="eyebrow">Network Automation AI Node</p>
          <h1>Automation Evidence</h1>
        </div>
        <NetworkNav />
      </header>
      <DayResultsClient results={results} />
    </main>
  );
}
