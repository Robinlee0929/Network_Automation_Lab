import { AiActionsClient } from "@/components/network/AiActionsClient";
import { NetworkNav } from "@/components/network/NetworkNav";
import { getAvailableActions } from "@/lib/network-ai/actions";

export default function NetworkAiActionsPage() {
  const actions = getAvailableActions();

  return (
    <main className="network-page">
      <header className="network-header">
        <div>
          <p className="eyebrow">Network Automation AI Node</p>
          <h1>AI Actions</h1>
        </div>
        <NetworkNav />
      </header>
      <AiActionsClient actions={actions} />
    </main>
  );
}
