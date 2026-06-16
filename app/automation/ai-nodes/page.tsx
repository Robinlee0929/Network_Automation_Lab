import { AiNodeTabs } from "@/components/automation/ai-nodes/AiNodeTabs";

export default function AutomationAiNodesPage() {
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
      <AiNodeTabs />
    </main>
  );
}
