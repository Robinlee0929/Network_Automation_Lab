import { DayResultsClient } from "@/components/network/DayResultsClient";
import { importDayResults } from "@/lib/network-ai/dayResults";

export default function NetworkDayResultsPage() {
  const results = importDayResults();

  return (
    <main className="network-page" id="network-primary-content" tabIndex={-1}>
      <header className="network-route-header">
        <h1>Automation Evidence</h1>
      </header>
      <DayResultsClient results={results} />
    </main>
  );
}
