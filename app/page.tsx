import Link from "next/link";

export default function HomePage() {
  return (
    <main className="home-shell">
      <section className="home-panel">
        <p className="eyebrow">Internal Tool</p>
        <h1>Network Automation AI Node</h1>
        <p>
          Router / Switch 自動化平台的報告分析、意圖解析、action 推薦與 job 建立節點。
        </p>
        <Link className="primary-link" href="/network/day-results">
          開啟 Network AI Node
        </Link>
        <Link className="primary-link" href="/ai">
          開啟舊版 AI 工作台
        </Link>
        <Link className="secondary-link" href="/automation/ai-nodes">
          開啟 Automation AI Nodes
        </Link>
      </section>
    </main>
  );
}
