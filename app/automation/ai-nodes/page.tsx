import { AiNodeTabs } from "@/components/automation/ai-nodes/AiNodeTabs";
import { isLegacyAiProviderEnabled } from "@/lib/ai/providerPolicy";

export const dynamic = "force-dynamic";

export default function AutomationAiNodesPage() {
  const legacyAiProviderEnabled = isLegacyAiProviderEnabled();

  return (
    <main className="ai-page automation-page">
      <section className="ai-hero" aria-labelledby="automation-ai-title">
        <div>
          <p className="eyebrow">Automation AI Nodes</p>
          <h1 id="automation-ai-title">自動化平台 AI 節點 MVP</h1>
          <p>
            三個可嵌入 workflow 的 AI Action Nodes，輸出可供下一步流程使用的 JSON。
          </p>
        </div>
        <div className="hero-note" role="note">
          AI 草稿，需人工確認
        </div>
      </section>
      {legacyAiProviderEnabled ? (
        <>
          <div className="status-strip" role="note">
            Explicit local opt-in is active. Submitted text is sent to the configured external
            provider. Do not submit secrets, credentials, or private device or lab data. These
            nodes cannot execute device commands or configuration changes.
          </div>
          <AiNodeTabs />
        </>
      ) : (
        <section className="status-strip" aria-labelledby="legacy-ai-nodes-disabled-title">
          <h2 id="legacy-ai-nodes-disabled-title">Legacy provider workbench disabled</h2>
          <p>
            These legacy/general AI provider nodes are outside the canonical provider-free Stage-0
            reviewer path and are disabled by default. Intentional local use requires
            <code> LEGACY_AI_PROVIDER_ENABLED=1</code>. Enabling them does not authorize device or
            command execution.
          </p>
        </section>
      )}
    </main>
  );
}
