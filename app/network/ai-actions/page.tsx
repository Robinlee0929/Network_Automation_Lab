import { AiActionsClient } from "@/components/network/AiActionsClient";
import { getAvailableActions } from "@/lib/network-ai/actions";
import {
  NETWORK_AI_PROVIDER_DEMO_MAX_REQUEST_LENGTH,
  isNetworkAiProviderDemoEnabled
} from "@/lib/network-ai/providerDemo";

export const dynamic = "force-dynamic";

export default function NetworkAiActionsPage() {
  const actions = getAvailableActions();
  const providerDemoEnabled = isNetworkAiProviderDemoEnabled();

  return (
    <main className="network-page" id="network-primary-content" tabIndex={-1}>
      <header className="network-route-header">
        <h1>AI Actions</h1>
      </header>
      <AiActionsClient
        actions={actions}
        maxRequestLength={NETWORK_AI_PROVIDER_DEMO_MAX_REQUEST_LENGTH}
        providerDemoEnabled={providerDemoEnabled}
      />
    </main>
  );
}
