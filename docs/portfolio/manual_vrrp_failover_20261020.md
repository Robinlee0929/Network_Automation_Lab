# Manual VRRP Failover / Recovery — 2026-10-20

**Result / 結果：MANUAL PASS_WITH_PACKET_LOSS。**
Owner 提供的人工觀察記載 Lab2 在 Lab1 LAN 隔離後接手 MASTER，
恢復連線後回到 Lab1 MASTER／Lab2 BACKUP。Windows VIP Ping 原始檔
包含 205 replies、2 timeouts，共 207 observations，封包遺失率 0.9662%。

Owner-supplied manual observations record Lab2 taking the MASTER role after
Lab1 LAN isolation, followed by Lab1 MASTER / Lab2 BACKUP after recovery.
The original Windows VIP Ping input contains 205 replies and 2 timeouts across
207 observations: 0.9662% packet loss. This is not a zero-loss result.

**Document status / 文件狀態：LOCAL_DOCS_DRAFT_READY_FOR_OWNER_REVIEW。**
本文件可離線閱讀，不需要執行設備命令。這是外部人工實驗摘要，
不是 NAL DL-06-02 official Live Proof，也不授予新的 Live 權限。
This external manual-test summary can be reviewed offline without device
commands. It is not NAL DL-06-02 official Live Proof and grants no live authority.

## Objective / 測試目的

整理一次人工中斷與恢復 Lab1 LAN 連線的既有證據，說明觀察到的
VRRP 角色變化及 VIP 可達性，並區分可直接計數的資料與人工提供的觀察。

Explain the observed VRRP role transitions and VIP reachability during one
manual Lab1 LAN isolation and recovery, separating directly countable evidence
from Owner-reported observations. The documentation review did not repeat the test.

## Topology / 測試拓樸

| Component / 元件 | Lab address / 位址 | LAN connection / 連線 | Reported priority / 優先權 |
| --- | --- | --- | --- |
| MikroTik Lab1 | `192.168.88.2` | `ether5` ↔ Cisco `Gi0/7` | 150 |
| MikroTik Lab2 | `192.168.88.3` | `ether5` ↔ Cisco `Gi0/8` | 100 |
| Shared VRRP VIP | `192.168.88.99` | Shared LAN / 共用 LAN | VRID 88 |

以上為 Owner 提供的實驗拓樸與觀察資料，不是本文件審查重新探測的結果。
原拓樸圖上的 `2024-05-20` 為歷史圖面日期，不是 `2026-10-20` 的測試時間。

These are Owner-supplied lab details, not a fresh discovery of deployed devices.
The original topology image's `2024-05-20` date belongs to the historical drawing;
it is not an event timestamp for the `2026-10-20` test.

## Test Procedure / 已完成的人工測試步驟

下列內容是 Owner 已完成操作的回顧，不是要求讀者重跑的操作指令。
The following describes the completed manual test, not instructions to rerun it.

1. Owner 提供 baseline：Lab1 MASTER／Lab2 BACKUP，並提供 Windows VIP Ping。
   The Owner supplied baseline role observations and Windows VIP Ping evidence.
2. Owner 手動斷開一次 Lab1 `ether5` ↔ Cisco `Gi0/7` LAN 網線，
   隨後提供 Lab2 的人工 CLI 角色觀察。
   The Owner disconnected that LAN cable once and supplied a subsequent Lab2 CLI observation.
3. Owner 恢復該連線，並提供 Lab1 與 Lab2 的後續人工 CLI 角色觀察。
   The Owner restored the connection and supplied subsequent CLI observations from both labs.
4. 離線整理者以既有 Ping 原始檔計數，將人工觀察整理為 JSON／HTML，
   再由離線審查核對包內一致性與敘述限制。
   The supplied Ping input and manual observations were summarized offline in JSON/HTML;
   offline review checked internal consistency and the limits of the claims.

## Observed Results / 觀察結果

角色欄位來自 Owner 提供的人工觀察。切換與恢復的 RouterOS 狀態來自
人工貼上的 CLI 輸出；baseline 在 JSON 中另註為先前提供的 WinBox 狀態
與 VIP Ping。ZIP 沒有獨立保存完整原始 RouterOS CLI transcript。

Role states are normalized Owner observations. Failover and recovery states
come from manually supplied RouterOS CLI output; the JSON separately identifies
the baseline as prior Owner-provided WinBox states and VIP Ping. The ZIP does
not independently preserve a complete raw RouterOS CLI transcript.

| Phase / 階段 | Lab1 observation / 觀察 | Lab2 observation / 觀察 |
| --- | --- | --- |
| Baseline / 起始 | MASTER, priority 150 | BACKUP, priority 100 |
| Lab1 LAN isolated / LAN 隔離後 | NOT_OBSERVED_WHILE_ISOLATED | RM / MASTER, priority 100 |
| LAN restored / 連線恢復後 | RM / MASTER, priority 150 | B / BACKUP, priority 100 |

此順序支持本次人工角色切換與恢復的觀察結論，但不是同時量測兩台設備，
也不是離線審查者獨立重新驗證設備狀態。
The sequence supports the reported manual failover and recovery result.
It is neither simultaneous cross-device measurement nor independent device-state
reverification by the offline reviewer.

| Ping metric / 指標 | Verified from supplied raw input / 原始輸入計數 |
| --- | --- |
| VIP | `192.168.88.99` |
| Replies / 成功回覆 | 205 |
| Timeouts / 逾時 | 2 |
| Observations / 探測結果總數 | 207 |
| Packet loss / 封包遺失率 | `2 / 207 × 100 = 0.9662%` (rounded / 四捨五入) |
| Timeout source lines / 原始檔逾時行號 | 32, 130 |
| Successful reply RTT / 成功回覆延遲 | `<1 ms`: 125; `1 ms`: 79; `3 ms`: 1 |
| Overall manual result / 整體人工測試結果 | MANUAL PASS_WITH_PACKET_LOSS |

## Evidence and Provenance / 證據與來源

Reviewed external archive / 已審查外部壓縮檔：
`NAL_manual_vrrp_failover_evidence_20261020.zip`

Archive SHA-256 / 壓縮檔雜湊：

```text
4eb211fe0fe406d62cf5164e1144079cd779bcfb4f078d3c3355b26ca28d1004
```

Prior offline review / 前次離線審查：
`PASS_WITH_NON_BLOCKING_DOCUMENTATION_NOTE`。
The ZIP hash was verified before drafting this document.

下表路徑相對於 ZIP 內的 `NAL_manual_vrrp_failover_evidence_20261020/`；
它們是外部證據索引，不是 repository 中已發布的檔案連結。
Paths below are relative to the archive's package directory. They identify
external evidence, not files published in this repository. The archive and
raw inputs are not copied into this documentation change.

| Package path / 包內路徑 | Evidence class / 證據類別 | Interpretation / 解讀 |
| --- | --- | --- |
| `inputs/ping_vip_raw.txt` | Owner-provided original input / Owner 原始輸入 | Directly countable replies and timeouts / 可直接計數 |
| `inputs/topology.png` | Owner-provided original input / Owner 原始輸入 | Diagram context, not current device verification / 拓樸背景 |
| `report/manual_observations.json` | Offline derived report / 離線衍生報告 | Normalized observations and calculated metrics / 人工觀察與統計整理 |
| `report/manual_report.html` | Offline derived report / 離線衍生報告 | Readable presentation of the same evidence / 閱讀介面 |
| `README.md` | Package explanation / 包裝說明 | Scope, provenance and limitations / 範圍與限制 |
| `manifest.json` | Unsigned integrity manifest / 未簽署雜湊清單 | Lists the other five files / 涵蓋其餘五個檔案 |

SHA-256、大小與 ZIP CRC 檢查通過，只證明包內檔案與清單一致。
Manifest 未簽署，不能獨立證明採集來源、封裝前未修改、設備狀態或執行授權。
Owner 指定 Ping 與拓樸圖為原始輸入；本次未改寫這些輸入。

The SHA-256, byte-size and ZIP CRC checks passed. The unsigned manifest establishes
internal package consistency only. It does not independently authenticate collection
provenance, prove that inputs were unchanged before packaging, verify device state,
or authorize execution. The Owner identifies the Ping and topology files as original
inputs; this documentation work did not alter them.

### Erratum / 勘誤

原 ZIP `README.md` 的「four files above」是非阻擋性敘述錯誤：
實際 manifest 涵蓋 **5 個檔案**，ZIP 總共 **6 個檔案**（包含 manifest）。
本文件只記錄勘誤，原 ZIP、原始證據與上述 SHA-256 均保持不變。

The archive README's “four files above” wording is a non-blocking documentation
error: the manifest covers **five files**, and the ZIP contains **six files**
including the manifest. This erratum does not modify the original ZIP, its
source evidence, or its reviewed SHA-256.

## Limitations and Safety Boundary / 限制與安全邊界

| Measurement / 量測項目 | Status / 狀態 |
| --- | --- |
| Event timestamps / 事件時間戳 | NOT_AVAILABLE |
| Exact failover convergence / 精確切換收斂時間 | NOT_MEASURED |
| Exact recovery convergence / 精確恢復收斂時間 | NOT_MEASURED |
| Individual timeout-to-event attribution / 個別逾時與事件關聯 | NOT_ESTABLISHED |

Ping 檔沒有逐封包時間戳，人工斷線／恢復也沒有精確事件時間戳。
不能把兩次逾時各自歸因為一次切換與一次恢復，不能從 RTT 或逾時數推算
收斂時間，也不能宣稱零遺失或全程無中斷。

There are no per-packet timestamps or exact disconnect/reconnect timestamps.
Neither timeout can be independently assigned to failover or recovery. Reply RTTs
and timeout counts do not measure convergence, zero loss, or uninterrupted availability.

這是 **2026-10-20 新的人工 Failover／Recovery 測試**，不是歷史 Day35
測試的重跑證明，也不等同 NAL DL-06-02 Live Proof。此摘要不改變既有
Stage-2 closure、DL-06-01、DL-06-02 或 Day35 的正式判定，不證明
credential authorization、trusted startup 或 replay readiness。

This is a **new manual failover/recovery test dated 2026-10-20**, distinct from
historical Day35 evidence and NAL DL-06-02 Live Proof. It does not change the
formal Stage-2 closure, DL-06-01, DL-06-02 or Day35 decisions, or establish credential
authorization, trusted startup or replay readiness. The documentation work ran
no Day35 runner, live adapter, device command or new network test.

Formal status and safety gates are recorded in the
[actual automation integration plan](../automation_readiness/actual_automation_integration_plan.md)
and [canonical Dual-Lab record](../automation_readiness/dual_lab_vrrp_ai_query_mvp.md).
本文件只供離線審閱；任何新的 Live 操作或文件發布均需另行授權。
Any new live operation or publication requires separate authorization.

Return to the [Public Reviewer Walkthrough](public_reviewer_walkthrough.md).
