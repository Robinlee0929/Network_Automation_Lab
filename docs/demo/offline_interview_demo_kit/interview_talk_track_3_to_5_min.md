# 3 到 5 分鐘面試 Demo Talk Track

這個專案叫 Network Automation Lab，目標是把網路設備驗證從一次性的手動 SSH 檢查，轉成可以重複執行、可以產生 evidence、也可以被測試保護的自動化流程。

我想解決的問題是：很多網路驗證平常會靠人工登入設備、貼指令、截圖，短期可以用，但很難重複、很難比較，也很容易在 demo 或維護時不小心碰到 live configuration。所以這個專案把 MikroTik、Cisco、WireGuard、VRRP、效能測試與報告整理成清楚的 workflow，讓每個結果都有 JSON 或 HTML evidence，也可以用 pytest 保護 parser、runner metadata、dashboard route 和 report behavior。

安全 guard 是這個專案很重要的設計。不是所有任務都應該直接執行在真實設備上，所以我把任務分成 documentation-only、report-only、safe dry-run、read-only、guarded live 等不同層級。面試 demo 只走本機與 report-only 路徑，不開 SSH、不連 router 或 switch、不改 NAT、IP、VRRP、WireGuard、防火牆、介面或路由設定。這樣面試時可以展示架構和工程品質，但不會因為環境不穩或設備不在現場而增加風險。

Unified Runner 是我用來整理任務入口的核心。面試時我會先用 `python network_lab.py --list-tasks --verbose` 展示 task catalog，讓面試官看到每個 task 的安全層級、device scope、report path 和 notes。這代表專案不是一堆單獨 script，而是有統一入口、有 safety metadata，也能把 live workflow 跟 offline demo workflow 分開。

Report Index 和 Dashboard 是 human review surface。`python network_lab.py --task report-index` 會掃描本機 evidence path，整理成 report index；dashboard 則可以在本機 `127.0.0.1:5000` 打開，從 `/reports` 看 evidence navigation。就算乾淨 checkout 沒有 ignored 的 generated reports，也可以用 WARN 說明哪些是 optional historical evidence，而不是假裝資料存在。

VRRP 是 v0.2 主要里程碑之一。這裡我會展示從 topology planning、safety model、read-only precheck、dry-run preview、staged apply plan、failover evidence review，到 dashboard/report-index integration 的 evidence chain。面試 demo 不會跑 live failover，因為 live failover 應該在受控 lab 條件下做；面試時展示的是設計、證據鏈、風險控管和離線可說明性。

WireGuard 則展示專案往 VPN validation 延伸的方向，包括 client-to-site evidence、secret redaction、PrivateKey 不外洩，以及 runner safety layer。未來我也把 AI/Voice Network Test Assistant 放在 roadmap 裡，但現階段把它當成未來方向，不在這次 demo 裡實作或假裝已完成。

這個 Day48 offline kit 的重點是：即使沒有 GitHub、沒有網路、沒有 router、switch、VPN 或 lab device，我仍然可以用本機程式碼、文件、測試、runner metadata、report index 和 dashboard route 說清楚整個平台。面試官應該注意到三件事：第一，這不是只會下指令的腳本，而是有測試和 evidence 的 automation platform；第二，安全邊界是刻意設計的，不會在 demo 時碰 live config；第三，這個專案可以從 day-by-day roadmap 看出持續迭代、修正、驗證和包裝的工程流程。
