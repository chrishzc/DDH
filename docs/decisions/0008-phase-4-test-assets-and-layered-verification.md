# Decision 0008: Phase 4 Verification Assets and Layered Verification

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 4 建立 Verification Asset 品質、currentness、分層驗證與成本效益式 stress
governance。Task／Layer Specification 保持 expected behavior authority；
admitted Verification Assets 是可重跑 executable evidence；Verification Asset Catalog 只作可重建
discovery／state／suite-selection index。

## Logical Organization

正式 Verification Assets 必須可按下列層級查詢：

```text
Module
Subsystem
Domain
Global
```

物理路徑可遵循既有project conventions，但不得按Agent或一次性Work Package
永久分類。每個正式asset至少能追溯specification/version、scenario IDs、
architecture layer/nodes、fixture/helper dependencies、quality dimensions、
stress profile與supersession relation。

pytest是Python reference adapter，不是必要tool。所有正式assets使用相同的
三軸治理、Subject binding、timeout與result protocol。

## Three Independent State Axes

```text
admission:
  draft | under_review | admitted | rejected | quarantined

semantic validity:
  current | suspect | stale | retired

candidate execution:
  not_run | passed | failed | error | invalidated
```

`superseded_by`是版本關係，不是PASS或archive狀態。

## Quality Contract Authority

Test Quality Contract由confirmed specifications、layer、risk、System Map impact
candidates、live facts與approved defaults編譯。Agent可提出候選，不能自行將
required改optional或創造expected behavior。規格與approved defaults均無法決定
且選擇會實質改變品質／成本／風險時，產生`quality_policy_gap`。

正式admission前，每個quality dimension必須解析成`required`或
`not_applicable`；`conditional`只可作等待fact的暫態狀態。

## Admission and Anti-weakening

```text
test draft
→ traceability/static checks
→ Mechanical Acceptance Guard
→ independent Test Auditor
→ replay
→ mutation/negative probe
→ admitted
```

至少阻擋assertion deletion／weakening、expected-value widening、threshold
lowering、fixture shrinking、case removal、new skip／xfail、required marker
removal與suite exclusion。

## Currentness Timing

- Work Package開始：建立existing test validity projection。
- 施工期間：product change只標記`rerun_required`；spec／test／fixture／helper／
  contract／schema／toolchain change觸發對應validity evaluation。
- Candidate freeze後：Test Auditor對fixed Candidate與current spec作正式判斷，
  發布atomic Verification Asset Manifest。
- Verification期間：Candidate、spec、asset、fixture、helper或environment identity
  改變，使舊subject失效。

Product source hash改變不直接代表test semantics stale。

## Retention

Work Package完成後長期保留confirmed specification、admitted rerunnable Verification Assets、
required fixtures/helpers與environment declaration。不永久保存每次stdout、
traceback、PASS receipt、shard result、完整Attempt Ledger或Agent conversation。

## Layered Verification

Module、Subsystem、Domain與Global各有自己的business scenarios、invariants、
integration與適用stress。Lower-level PASS只作higher-level input，不自動發布上層
completion。

Stress profile依frequency、data size、concurrency、failure cost、recovery、
consistency、critical path與budget選擇`not_applicable`、`light`、`standard`或
`high_assurance`。低頻不自動等於低風險。

## Acceptance

Phase 4必須證明：

- Verification Asset Catalog可從repo重建且不是authority；
- admission／validity／execution三軸獨立；
- required behavior有admitted executable coverage；
- independent Test Auditor與mechanical guards阻止驗收放寬；
- false stale、fixture/helper impact、supersession與retirement正確；
- suspect／stale assets不參與completion；
- Verification Assets提供長期rerunnable evidence，不依賴永久PASS receipts；
- suite scale與stress cost-benefit可受控。
