# Decision 0020: Layered Quality Profiles and Independent Add-ons

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Test Quality Defaults不採單一V0～V3強度階梯。正式模型由三部分組成：

```text
verification scope layer
＋ independent quality add-ons
＋ specification-sourced product thresholds
```

Scope layers使用`Static`、`Module`、`Subsystem`、`Domain`與`Global`。它只
決定驗證到哪個architecture layer，不自動要求所有high-cost checks。既有
V0～V3保留為歷史alias，不再作canonical single severity scale。

## Independent Add-ons

每個add-on獨立標記`required`或
`not_applicable_with_business_reason`：

- Boundary and Negative
- State Transition
- Data Integrity and Invariants
- Idempotency
- Concurrency
- Failure and Recovery
- Compatibility and Migration
- Security
- Performance and Load
- Long-running and Soak
- External-effect Isolation

System Map fanout只可觸發dependency regression候選，不能單獨創造load／soak
需求。

## Bootstrap Floors

所有project共用的最低要求：

- 每個required business scenario至少映射一項Verification Asset。
- 所有required scenarios必須PASS。
- Required asset不得unexpected skip、not-run或incomplete。
- Oracle必須能判斷規格結果，不能只檢查沒有exception。
- Runtime behavior change預設需要negative／boundary場景。
- New／changed formal acceptance assets必須獨立admit；unchanged assets重用
  admission。
- Tool unavailable、timeout與runner error不能作PASS。

Bootstrap Defaults不設定全域code coverage percentage、mutation score、
property case count、concurrency workers、request rate、soak duration或所有
tests的固定repeat count。

## Applicability Triggers

High-cost add-ons只有在approved facts支持時啟用：

- Concurrency：parallel expectation、shared mutable state、async worker或
  parallel writer。
- Performance／Load：規格提供volume、rate、latency或throughput requirement。
- Soak：daemon、scheduler、pool、cache或long-lived state。
- Recovery：IO、transaction、retry、partial write或external dependency。
- Compatibility：schema、public API、persistent data或serialized format。
- External isolation：DB、network、credential、external transaction、deployment或publish。

## Authority and Timing

```text
user Task Specification
→ approved project／Domain quality profile
→ versioned DDH Bootstrap Defaults
→ Test Auditor deterministic compilation
→ Independent Critic review
```

Main Agent、Implementation／Test Agent、System Map、Telemetry與Learning Steward
都不能創造或降低product threshold。

Task Specification確認後先產生provisional profile；System Map、live source與
actual delta補足facts後，Test Auditor在formal test admission前解析所有
conditional並pin profile。新facts可以自動strengthen verification；看到失敗
後不能downgrade。

若required quality超出預算，先嘗試不改語意的cache、sharding、parallelism與
equivalent runner。仍不足時回報`quality_budget_conflict`，不得移除required
scenarios或降低threshold。

## Required Scenarios

- Same specification／facts產生相同profile。
- High-criticality small change只加入相關add-ons。
- Large low-risk refactor不依file count升到所有high-cost checks。
- Agent不能在failure後移除add-on或threshold。
- Unchanged admitted assets不重新消耗model Critic。
- Policy gap decision形成reusable rule，避免逐Task詢問。
- Map stale不降低quality。
- Budget不足不縮減required scenarios。
- Load／soak沒有business basis時可以正式標N/A。
