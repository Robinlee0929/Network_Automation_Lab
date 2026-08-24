import { AiTabs } from "@/components/ai/AiTabs";
import { isLegacyAiProviderEnabled } from "@/lib/ai/providerPolicy";

export const dynamic = "force-dynamic";

export default function AiPage() {
  const legacyAiProviderEnabled = isLegacyAiProviderEnabled();

  return (
    <main className="ai-page">
      <section className="ai-hero" aria-labelledby="ai-title">
        <div>
          <p className="eyebrow">AI Project Assistant</p>
          <h1 id="ai-title">專案草稿工作台</h1>
          <p>
            將會議紀錄、原始需求與 SOP 文件整理成可審核的繁體中文草稿。
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
            provider. Do not submit secrets, credentials, or private device or lab data. This
            workbench cannot execute device commands or configuration changes.
          </div>
          <AiTabs />
        </>
      ) : (
        <section className="status-strip" aria-labelledby="legacy-ai-disabled-title">
          <h2 id="legacy-ai-disabled-title">Legacy provider workbench disabled</h2>
          <p>
            This legacy/general AI provider workbench is outside the canonical provider-free
            Stage-0 reviewer path and is disabled by default. Intentional local use requires
            <code> LEGACY_AI_PROVIDER_ENABLED=1</code>. Enabling it does not authorize device or
            command execution.
          </p>
        </section>
      )}
    </main>
  );
}
