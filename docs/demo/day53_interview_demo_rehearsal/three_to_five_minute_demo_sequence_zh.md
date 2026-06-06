# Day53 3-5 Minute Demo Sequence

## 0:00-0:30 Opening

打開專案資料夾，說明：

- 這是 Network Automation Lab。
- 目標是展示安全網路自動化、報告證據、dashboard evidence 和面試可操作流程。
- 今天 demo 是 offline/report-only，不碰 live device。

## 0:30-1:00 Repository Status

在 terminal 確認 branch/status，或引用已記錄的狀態：

```powershell
git status --short --branch
```

說明目前 demo 基準來自 latest `main`，Day52 已 merged，Day53 只做 rehearsal documentation。

## 1:00-1:45 Local Validation

執行或引用最新本機 validation：

```powershell
python -m pytest
python network_lab.py --task report-index
```

說明：

- `pytest` 保護 parser、runner metadata、dashboard route 和 report behavior。
- `report-index` 是 report-only task。
- 如果 `report-index` 是 `WARN`，只要 `fail=0` 且缺的是 optional local generated reports，就可以接受。

## 1:45-2:15 Dashboard Start

如果本機環境可用，啟動 dashboard：

```powershell
python dashboard_app.py
```

打開：

```text
http://127.0.0.1:5000/
```

如果 dashboard 不能開，直接切到 Day52 screenshot package：

```text
docs/demo/day52_offline_demo_package/
```

## 2:15-3:30 Dashboard Walkthrough

依序展示：

1. Home page: interview landing page、project purpose、demo status、proof points、safety boundary。
2. Reports page: report index、evidence navigation、optional missing local reports 的說明方式。
3. Commands page: allowlisted local commands、disabled live tasks、command log visibility。
4. AI Checklist page: AI 輔助時的 safety controls、code-level guard、不能直接改 router settings。

## 3:30-4:30 Evidence And Safety Explanation

說明核心設計：

- Evidence: JSON/HTML reports、dashboard、roadmap、release/demo docs。
- Safety guard: documentation-only、report-only、read-only、dry-run、guarded-live 分層。
- 面試 demo 只走 local/report-only 路徑。
- Live VRRP、WireGuard、router、firewall、interface 變更不在面試路徑內。

## 4:30-5:00 Close

收尾說明未來方向：

- `v0.3` 可以強化 dashboard/report workflow，但不能未定義安全邊界就加入 live behavior。
- `v3.0` 或 AI/Voice assistant 可以做成安全編排入口，但 AI 只能產生建議、報告、dry-run plan 或需要人工確認的 guarded workflow，不能直接任意修改設備。
- 這個專案已證明可以把網路自動化從一次性 CLI 操作，提升成有測試、有 evidence、有安全分層的 automation platform。
