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
Phase 1 `DDH-P1-SPEC-001@1.0.0` 已取得 exact human confirmation，Python
reference runtime 已完成本機施工與 Windows／Python 3.14 驗證。規格要求的
Windows／Ubuntu Python 3.13 與 latest-stable matrix 尚未執行，因此目前不宣告
`work_package_completed`。

Phase 1 建立的範圍包括：

- `src/ddh/` 模組化 Python reference runtime。
- strict Contract、Ports、disposable Candidate、Test Auditor、Verification
  Runner、Completion Judge與portable Candidate Bundle。
- thin local confirmation CLI。
- unit、contract、integration與portable workspace verification。

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

多代理分區與精準子代理 Context Envelope 屬後續 Phase，不在 Phase 1 runtime。

## Legacy 邊界

舊專案 `ADAD` 只作唯讀功能參考與 migration 來源。DDH 不得在正常啟動、
測試或開發流程 fallback 到 legacy `system_map.md`、`system_map.yaml`、Task、
Source Lock、Checkpoint 或 hooks。
