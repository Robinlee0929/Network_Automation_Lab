import Link from "next/link";

export default function HomePage() {
  return (
    <main className="home-shell">
      <section className="home-panel">
        <p className="eyebrow">Secondary Stage 0 surface</p>
        <h1>Network Automation AI Node</h1>
        <p>
          Router / Switch 自動化平台的報告分析、意圖解析、action 推薦與 job 建立節點。
        </p>
        <p className="status-strip" role="note">
          Canonical reviewer entry point: Flask dashboard at http://127.0.0.1:5000/. This
          Next.js app is a secondary, demo-only surface; provider-backed actions are
          unavailable in the Stage 0 safe Demo.
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
