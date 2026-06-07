# Portfolio Demo Script - v0.1

## Purpose

這份文件提供目前 Network Automation Lab v0.1 狀態的 5 到 10 分鐘 reviewer / portfolio demo script。

目標是協助 reviewer、demo reviewer 或 technical hiring manager 理解這個平台目前已經能展示的能力，同時不改變平台行為、不啟動 live VPN execution，也不碰觸真實設備設定。

## Audience

- reviewer
- demo reviewer
- technical hiring manager

## Demo Duration

5 到 10 分鐘。

## What This Demo Shows

- 一個以 Python 為基礎、用於 infrastructure validation 的 network automation lab platform。
- MikroTik hEX S router validation workflows。
- Cisco switch topology validation workflows。
- 既有 report output 中的 WireGuard VPN validation evidence。
- 既有 performance reports 中的 iperf3 throughput evidence。
- 用來整理 lab actions 的 unified runner 與 task catalog concept。
- 用於瀏覽本機 evidence 的 dashboard 與 report viewer concept。
- 給 automation 與 human review 使用的 JSON 與 HTML report outputs。
- README、docs 與本機 ignored report folders 之間的 portfolio evidence organization。
- safety-first automation boundary，清楚區分 report-only、read-only、guarded-live、dry-run 與 disabled behavior。

## What This Demo Does NOT Do

- 不新增 features。
- 不修改 runner behavior。
- 不修改 dashboard behavior。
- 不啟動 live VPN execution。
- 不對 routers、switches 或 VPN clients 套用 configuration。
- 不執行會改變 device state 的 commands。
- 不 commit generated reports、exports、real configs、secrets、passwords、private keys 或 WireGuard config files。

## Safety Boundaries

這個 demo 應聚焦在 repository structure、既有 report evidence、安全 metadata，以及本機 read-only views。

Demo 時請維持以下 boundaries：

- 優先使用 `--list-tasks`、`--report-index`、portfolio docs，以及既有 report viewer pages。
- 把 live-device scripts 視為 evidence sources，而不是 portfolio review 中要直接執行的 commands；除非 lab 已準備好，而且已取得明確同意。
- 不展示或開啟真實 secret files、exported WireGuard `.conf` files、private keys，或包含本機密碼的 configs。
- 不把 secrets 貼到 terminal、README、docs、chat、PRs、screenshots 或 reports。
- 讓 generated `reports/`、`exports/`、caches、local configs 與 WireGuard config files 保持在 Git 之外。

## Suggested Repository Walkthrough

從 `README.md` 開始，先用一句話說明專案：

> This is a Python-based network automation lab that validates MikroTik routers, a Cisco switch, WireGuard VPN evidence, throughput measurements, and report visibility in a safety-first portfolio format.

接著用高層次方式 walkthrough repository：

- `network_lab.py` 是 unified runner entry point，也是 task catalog。
- `mikrotik_*` scripts 包含 MikroTik validation 與 automation workflows。
- `cisco_topology_validation.py` 包含 Cisco switch topology validation。
- `performance_test.py` 與 `performance_regression.py` 涵蓋 iperf3 throughput evidence 與 regression-style checks。
- `dashboard_app.py` 與 `templates/` 提供本機 dashboard 與 report viewer concept。
- `docs/portfolio_evidence/` 存放已 commit 的 portfolio review notes。
- `reports/`、`exports/` 與 real configs 都是本機 working artifacts，不應 commit。

## Suggested Runner Demonstration

先展示 task catalog：

```powershell
python network_lab.py --list-tasks --verbose
```

說明 reviewer 可以看什麼：

- Task IDs 與 day labels 展示平台逐步成長的脈絡。
- Safety labels 讓 execution model 變得明確。
- Report-only tasks 可以 index 或 summarize local evidence。
- Read-only tasks 用來 inspect state。
- Guarded-live tasks 在碰觸 lab devices 前需要明確確認。
- Dry-run tasks 用來 preview planned actions。
- Disabled tasks 會刻意阻擋不支援或不安全的 execution。

如果本機已有 reports，可以展示 report index command：

```powershell
python network_lab.py --report-index
```

接著說明：

- runner 可以在不連線到 devices 的情況下 inventory expected evidence。
- Missing reports 會被清楚顯示為 missing evidence，而不是造成 crash。
- 既有 JSON 與 HTML reports 會被連結起來，方便 human review。

## Suggested Dashboard / Report-Viewer Demonstration

只有在 demo environment 適合時，才啟動本機 dashboard：

```powershell
python dashboard_app.py
```

開啟：

```text
http://127.0.0.1:5000/reports
```

說明 report-viewer concept：

- dashboard 是本機 evidence browser。
- `/reports` page 會依 day 與 task 分組 available evidence。
- JSON previews 需要容易閱讀，並且維持 redacted。
- HTML report links 會開啟既有 local reports。
- Missing reports 會被清楚呈現。
- report viewer 不會啟動 live validation、不會套用 device changes、不會 activate VPN clients，也不會 reveal secrets。

## Suggested Evidence / Report Walkthrough

如果本機 reports 存在，請選一小段 curated path，不要全部打開。

建議 evidence 順序：

1. MikroTik hEX S validation evidence。
2. Cisco switch topology validation evidence。
3. Lab-level topology summary。
4. iperf3 throughput evidence。
5. WireGuard VPN validation evidence。
6. Runner report index 或 portfolio evidence index。
7. Day24 demo flow、Day25 RC validation evidence、Day26 release documentation，以及 Day28 final review notes。

Useful committed documentation：

```text
docs/portfolio_evidence.md
docs/portfolio_evidence/day25_v0.1_rc_validation.md
docs/portfolio_evidence/v0.1_release_notes.md
docs/portfolio_evidence/v0.1_portfolio_checklist.md
```

Useful local report examples when generated：

```text
reports/report_index.html
reports/portfolio/day19_runner_evidence_index.html
reports/portfolio/day24_rc_demo_flow.html
reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.html
reports/Hex-s-2025-lab01/day9_performance_regression_report.html
reports/cisco-switch/switch_topology_report.html
```

說明時聚焦在 evidence design：

- JSON reports 支援 automation、regression comparison 與 future integration。
- HTML reports 適合 reviewer-friendly reading、screenshots 與 portfolio demos。
- Report organization 可以呈現 expected scope、actual output、pass/fail/warning state，以及 missing evidence。

## Suggested Speaking Script

Opening：

> Network Automation Lab is my Python-based infrastructure validation platform. It started with MikroTik router checks and grew into a small multi-vendor lab story with Cisco topology validation, iperf3 throughput evidence, WireGuard VPN validation evidence, a unified runner, and a local report viewer.

Safety positioning：

> The important design choice is that the platform separates evidence browsing from live execution. For a portfolio or portfolio demo, I can show the task catalog, report index, dashboard viewer, and generated evidence without applying device-changing commands or exposing secrets.

Runner walkthrough：

> The unified runner makes the lab easier to review because tasks are cataloged with names, days, safety levels, execution modes, related scripts, and report paths. That turns a folder of scripts into a platform-style interface.

MikroTik and Cisco validation：

> On the MikroTik side, the project validates router identity, baseline state, WAN/LAN expectations, SSH availability, and later VPN-related evidence. On the Cisco side, it validates topology-oriented switch facts such as model, interface state, VLAN behavior, MAC learning, and spanning-tree evidence.

Performance and VPN evidence：

> The iperf3 workflows capture throughput evidence as structured JSON and readable HTML. The WireGuard work records validation evidence while keeping real client configs, private keys, and exported `.conf` files outside Git and outside the reports.

Dashboard/report viewer：

> The dashboard is intentionally local and evidence-oriented. It gives a reviewer a faster way to inspect generated JSON and HTML reports, including missing evidence, without implying that the browser page is changing the network.

Close：

> v0.1 is not trying to be a production NMS. It is a safety-first automation portfolio that shows how I structure network validation, evidence, report visibility, and guardrails as an engineering system.

## Demo Checklist

Before the demo：

- 確認 working tree 沒有包含 generated reports、exports、real configs、secrets、passwords、private keys 或 WireGuard config files。
- 確認你打算展示的 screenshots 或 reports 都適合分享。
- 如果要使用 dashboard，確認它只指向 local evidence。
- 準備 repository review 前先執行 test suite。

During the demo：

- 從 README scope 與 v0.1 positioning 開始。
- 展示 unified runner task catalog。
- 展示 safety labels 與 execution modes。
- 展示 report index 或 dashboard report viewer。
- Walk through 一個 router、一個 switch、一個 performance，以及一個 VPN evidence example。
- 以 release notes、portfolio checklist 與 next steps 收尾。

After the demo：

- 不 commit generated report output。
- 不 commit local configs、exports 或 WireGuard `.conf` files。
- 讓任何 follow-up changes 都維持 scoped 且 documented。

## Troubleshooting / Fallback

如果 dashboard 無法使用：

- 使用 `README.md`、`docs/portfolio_evidence.md` 與 committed release docs。
- 如果既有 local HTML reports 是安全且可用的，可以直接從 `reports/` 開啟。
- 使用 `python network_lab.py --list-tasks --verbose` 在沒有 dashboard 的情況下展示 runner metadata。

如果 generated reports 缺少：

- 說明 generated reports 是刻意被 Git ignore。
- 展示 README 中的 expected report paths。
- 使用 committed portfolio evidence docs 說明 validation story。
- 除非 lab 已準備好且已取得明確同意，否則避免執行 live-device workflows。

如果 live lab 無法使用：

- 將 demo 保持為 repository-only。
- 強調 unit tests、parser coverage、safety metadata 與 report schema design。
- 展示 missing evidence 如何被表示，而不是被當成 unhandled error。

如果準備過程中 tests fail：

- 不隱藏 failure。
- 記錄 failing test names。
- 在修改任何內容前，先說明 failure 是 documentation-related、environment-related，還是 behavior-related。

## Next-Step Roadmap

Potential post-v0.1 directions：

- 增加更清楚、可安全 commit 的 versioned demo fixtures。
- 改善 dashboard filtering 與 evidence comparison，同時保留 read-only behavior。
- 增加更豐富的 report summaries，幫助 reviewer navigation。
- 擴充更多 lab devices 的 read-only validation coverage。
- 只有在 evidence model 與 secret-handling rules 仍然明確時，才加入 AI-assisted report summarization。
- 讓所有 future live execution 都維持在清楚的 safety labels、confirmations 與 documentation 之後。
