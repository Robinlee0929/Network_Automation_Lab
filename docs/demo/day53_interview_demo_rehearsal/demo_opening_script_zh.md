# Day53 Demo Opening Script

這個專案叫 Network Automation Lab。它是一個網路自動化測試平台，用 Python 把 MikroTik、Cisco、WireGuard、VRRP、效能測試和報告證據整理成可以重複執行、可以驗證、也可以展示的流程。

今天這個 demo 的重點不是現場修改設備，而是展示四件事：安全的網路自動化設計、結構化 report generation、本機 dashboard evidence，以及面試時可以穩定操作的 demo 流程。

這次 demo 會刻意走 offline/report-only 路徑。也就是說，我會用本機 repository、pytest、report index、dashboard 頁面、已整理好的文件與截圖來說明平台能力，不會在面試現場連線到 router、switch、firewall、VPN 或 WireGuard device。

這樣設計是有意識的安全選擇。真實網路設備的 VRRP failover、WireGuard peer、firewall、NAT、IP、interface 或 route 變更，都應該在受控 lab 條件下執行，不能把面試環境當成 live change window。

所以我今天會展示的是：這個平台如何把網路驗證變成有 evidence 的工程流程、如何用 dashboard 讓 reviewer 快速理解結果、如何用 safety metadata 區分 report-only、read-only、dry-run 和 guarded-live task，以及未來 AI 輔助版本應該如何被限制在安全邊界內。

簡短來說，這是一個 Network Automation Lab。它證明我不只會寫可以下指令的 script，也會把測試、證據、安全邊界、展示流程和未來擴充方向一起設計成一個可維護的平台。
