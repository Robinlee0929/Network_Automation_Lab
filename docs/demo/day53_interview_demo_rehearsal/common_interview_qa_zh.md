# Day53 Common Reviewer Q&A

## 為什麼 demo 要 offline？

因為一般作品集展示、專案審查或面試環境不是受控 change window。這個 demo 的目標是展示架構、測試、報告證據、dashboard 和安全邊界，不是現場修改真實設備。Offline/report-only demo 可以避免網路、設備、VPN、SSH、VRRP 或 WireGuard 狀態影響展示，也能避免不必要的 live configuration 風險。

## 為什麼不在 public demo 中做 live VRRP failover？

VRRP failover 會影響 gateway/availability behavior，應該在受控 lab、明確 rollback plan、可觀測性完整的條件下執行。Public demo 中會展示 VRRP topology plan、read-only precheck、dry-run preview、staged apply plan、failover evidence review 和 dashboard/report-index integration，但不把一般 demo 當成 live failover 測試。

## 這個專案的 safety model 是什麼？

核心是把 task 分層：documentation-only、report-only、read-only、dry-run、guarded-live、disabled。Portfolio/offline demo 只使用 documentation-only/report-only/local dashboard path。任何可能連線設備、使用 SSH、修改 NAT/IP/VRRP/WireGuard/firewall/interface/route 的工作，都必須明確標示安全等級並離開 public demo path。

## 這個 project prove 了什麼？

它證明網路自動化可以被做成 QA/SDET 風格的平台：有 repeatable tests、有 expected/actual/result、有 JSON/HTML evidence、有 report index、有 dashboard、有 runner metadata、有 safety controls，也有 portfolio-ready demo package。它不是只把 CLI 指令包成 script，而是把驗證、報告、風險控管和展示路徑一起工程化。

## 這和真實 network automation work 有什麼關係？

真實環境最需要的是可重複、可審查、可回溯、可控風險的流程。這個專案用 lab 規模展示同樣的工作方式：先把讀取、驗證、報告、dry-run 和 guarded-live 分開，再用測試與文件保護行為，最後用 dashboard/report 讓非實作人員也能理解結果。

## AI 在未來版本的角色是什麼？

AI 應該是 reviewer、explainer、planner 和 evidence summarizer，不應該是可以任意下 live router command 的代理。它可以協助解讀 reports、產生 checklist、比較 drift、建議 dry-run plan，或在有 guard 的 workflow 中提出下一步，但 live changes 必須經過 allowlist、safety metadata、human approval 和 audit log。

## `v0.3` 或 `v3.0` 會做什麼？

`v0.3` 可以聚焦在更好的 report workflow、dashboard evidence、task metadata 和 demo hardening。`v3.0` 可以是 Voice + AI Network Test Assistant，但只能在安全框架成熟後再做：先支援查詢、摘要、dry-run plan 和人工確認，再考慮 guarded-live orchestration。

## 如何防止 AI 直接修改 router settings？

第一，AI 不直接拿任意 shell 或 SSH 權限。第二，task catalog 要有 safety level、device scope、command boundary 和 disabled/live 標記。第三，live 變更必須走 allowlisted workflow、dry-run preview、human approval、audit log 和 rollback thinking。第四，portfolio/offline demo 完全不給 AI live device path。

## report-only、read-only、dry-run、guarded-live 有什麼差異？

Report-only 只讀本機已存在的報告或 metadata，不連設備。Read-only 可以連設備讀取狀態，但不進 config mode、不修改設定。Dry-run 產生預覽或 plan，不套用到設備。Guarded-live 是在明確 allowlist、人為確認、安全檢查與 rollback plan 下才允許執行的 live workflow。

## 目前限制是什麼？

目前 demo 依賴本機環境能跑 Python、pytest 和 dashboard；部分 generated reports 是 local/ignored evidence，所以 fresh checkout 可能有 optional missing reports。Live device workflows 需要受控 lab、正確 config 和設備連線，不屬於 portfolio/offline demo。AI/voice assistant 仍是 roadmap，不是假裝已經完成的功能。
