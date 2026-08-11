# DDH

**Demand-Driven Harness**

DDH（repository 歷史名稱 ADHD）是 ADAD 的全新世代，不是在 legacy ADAD
上持續堆疊相容層。

核心定位：

> 人類指定架構範圍；AI Orchestrator 在該範圍內自主規劃、施工、測試、診斷與修正，
> 直到高標準驗證證明結果符合語意規格。只有架構、語意規格或高風險不可逆決策改變時，
> 才返回人類決策。

## 目前階段

Phase 0 `Executable Contract Fixtures` 現行規格包
`DDH-P0-SPEC-001@1.1.0` 已於 2026-08-02 完成；`1.0.0` 僅保留於歷史封存。
Phase 1 `DDH-P1-SPEC-001@1.0.0` 已完成 reference runtime 與要求的 CI
平台驗證。

Phase 2 `DDH-P2-SPEC-001@1.0.0` 已取得 exact human confirmation，目前已完成
本機 reference implementation 與規格場景驗證；仍須通過 Windows 11、
Ubuntu 24.04／Python 3.13 及 latest-stable CI matrix，才宣告 Phase 2
`work_package_completed`。

Phase 3 `DDH-P3-SPEC-001@1.0.0` 已取得 exact human confirmation；本機 reference
implementation 現已提供 L2 的多 lane 協調、Change Guard activation、central Patch
Admission、Join Barrier 與三 Module Subsystem fork/join 驗證。Windows 11、Ubuntu
24.04／Python 3.13 及 latest-stable CI matrix 仍是 Phase 3 completion 的必要證據。

Phase 1 建立的範圍包括：

- `src/ddh/` 模組化 Python reference runtime。
- strict Contract、Ports、disposable Candidate、Test Auditor、Verification
  Runner、Completion Judge與portable Candidate Bundle。
- thin local confirmation CLI。
- unit、contract、integration與portable workspace verification。

Phase 2 新增：

- 12 類確定性 failure classification 與有界、去敏的 Failure Bundle。
- progress／budget-aware automatic recovery 與結構化例外報告。
- disposable runner rebuild 與僅限明確核准的 equivalent backend fallback。
- actual impact 驅動的驗證擴張，但不隱性擴大 write scope。
- 分離的 test repair proposal、機械 known-bad probe 與 independent admission。
- Invocation recovery checkpoint 與同一規格下的冪等重啟。

Phase 3 新增：

- 只在可證明淨收益與機械寫入分離存在時才啟用的平行分流。
- Module Work Group、product／acceptance Write Assignment、bounded Context 與
  scoped handoff 的 typed reference runtime。
- Change Guard 的 generation activation、fence、quiescence 與 late-writer
  rejection。
- Central Integrator 的 fixed-order Patch Admission 與 immutable integrated
  Candidate。
- 三 Module 加一條 Subsystem acceptance lane 的 asynchronous fork/join fixture；
  Work Package completion 與 Subsystem integration 分開判定。

仍不建立 System Map backend、legacy Task／Source Lock／Checkpoint、長期
provenance、真實 external provider、deployment或release操作。

## 權威與索引邊界

1. 本次人類確認的任務規格書，是 Agent 目標、scope、限制與完成判定的 SSOT。
2. `docs/architecture/` 與 `docs/semantic-specifications/` 保存可由任務規格固定
   引用的長期架構、行為、情境、不變量與驗收規範。
3. System Map 是長期維護、actual-only 的真實架構 index，用於 scope 規劃、
   impact 查詢、Context 選取、測試選取與視覺化；它不是 SSOT 或授權來源。

System Map 尚未完全落地；Bundle schema、狀態、API、currentness 與更新流程
仍可調整，但不得把 planned／declared-only 架構呈現為 Active actual view。

## 新版核心

- Actual architecture index 與任務規格 SSOT 的明確分工。
- 風險分級 Gate。
- 依架構範圍運作的自主施工與修正迴圈。
- 由語意規格與風險共同決定的分層驗證。
- 可選的 Dogfood、Adoption 與 Release 流程。

真實 remote Agent fleet、完整 Verification Asset portfolio lifecycle、System Map
backend、long-term orchestration learning 與 external high-risk execution 仍屬後續
Phase。

## Legacy 邊界

舊專案 `ADAD` 只作唯讀功能參考與 migration 來源。DDH 不得在正常啟動、
測試或開發流程 fallback 到 legacy `system_map.md`、`system_map.yaml`、Task、
Source Lock、Checkpoint 或 hooks。
