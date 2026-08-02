# Decision 0005: Phase 1 Single-Agent Vertical Slice

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 1 是 DDH runtime 的第一條端到端 vertical slice。它必須證明：

> 一份 human-confirmed Task Specification 能由單一主 Agent 在既定 scope、
> authority 與 budget 內自主實作、建立或修正Verification Assets、重複驗證，最後由
> `Completion Judge` 機械判定 Work Package 是否完成。

Phase 1 不以逐關人工 Checkpoint 驅動。

## Required Roles and Flow

```text
confirmed Task Specification
→ readiness and risk/verification projection
→ Context Curator: System Map query + bounded live-source confirmation
→ Work Package projection
→ Change Guard: workspace baseline + mutation boundary
→ main Agent: implementation + verification assets + bounded repair
→ actual-diff impact reconciliation
→ Change Guard: immutable Candidate
→ Test Auditor: minimum credible independent test admission
→ Verification Runner: no-Agent execution and typed result
→ Completion Judge: Work Package completion only
```

## Required Capabilities

- 缺少 executable expected behavior 時，在任何產品寫入前回報
  `specification_not_ready`。
- System Map 必須被查詢與實際消費；不足時自動使用 bounded live-source
  fallback。
- 保護既有 user dirty diff，拒絕本次 scope 外 mutation。
- Actual diff 後重新估算 impact；verification closure 可擴張，write authority
  不可偷渡擴張。
- Main Agent 可在原規格與 scope 內自主修正產品與不改驗收語意的 test
  implementation defect。
- `Test Auditor` 至少阻擋 assertion deletion、expected-value widening、
  threshold lowering、fixture shrinking、case removal 與新增 skip／xfail。
- `Verification Runner` 使用 fixed Candidate、test assets 與 environment，
  支援 timeout、bounded output、process cleanup 與 typed result。
- `Completion Judge` 只能發布 Work Package completion；不得自動發布
  Subsystem、Domain、release 或 deployment 狀態。

## Required Business Scenarios

Phase 1 至少覆蓋：

1. 高業務重要性但局部的跨平台路徑 canonicalization 修正。
2. Expected behavior 不足，施工前拒絕。
3. Dirty worktree 中保護無關使用者差異。
4. Actual impact 超出原估算，擴張 verification 但不擴張 write authority。
5. Agent 嘗試放寬acceptance Verification Assets時被拒絕。
6. System Map unavailable／incomplete 時自動 live-source fallback。

## Reliability Coverage

- 大型 repository 的 bounded Context／impact discovery。
- 大量 unrelated dirty files。
- 重複 traceback 的 bounded result。
- timeout 後 process-tree cleanup。
- Candidate churn 時舊結果不得套用。
- repeated identical failure 的 no-progress detection。
- System Map backend failure 的 bounded fallback。
- Windows 與至少一個 POSIX runtime profile。

Exact thresholds 尚未固定；依 Task Specification、repository profile、risk 與
cost-benefit 決定。

## Explicit Exclusions

Phase 1 不包含：

- multi-Agent parallel work、partition 或 Join Barrier；
- Subsystem／Domain／release completion；
- full Verification Asset portfolio lifecycle；
- long-term memory／self-evolution；
- external database、deployment、credential、network 或 publication；
- System Map implementation design。

## Acceptance

Phase 1 只有在上述業務與可靠性 scenarios 可重跑、正常修復不需逐關詢問人類、
write／test／completion authority 沒有混淆，且沒有把 prompt／Git hook 誤稱為
mechanical isolation 時完成。
