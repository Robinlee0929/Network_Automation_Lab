import { AiTabs } from "@/components/ai/AiTabs";

export default function AiPage() {
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
      <AiTabs />
    </main>
  );
}
