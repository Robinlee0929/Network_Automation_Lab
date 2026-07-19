import { AiActionsClient } from "@/components/network/AiActionsClient";
import { getAvailableActions } from "@/lib/network-ai/actions";

export default function NetworkAiActionsPage() {
  const actions = getAvailableActions();

  return (
    <main className="network-page" id="network-primary-content" tabIndex={-1}>
      <header className="network-route-header">
        <h1>AI Actions</h1>
      </header>
      <AiActionsClient actions={actions} />
    </main>
  );
}
