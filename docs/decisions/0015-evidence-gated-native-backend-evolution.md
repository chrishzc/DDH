# Decision 0015: Evidence-gated Native Backend Evolution

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Rust／Go不是DDH的預定重寫路線。只有特定Python backend出現可重現、
可量測，且無法在合理成本內修正的能力缺口，才可建立Backend Evolution
Proposal。

可接受的trigger classes為：

- safety／correctness invariant缺口；
- repeated reliability缺口；
- 已核准latency／throughput／memory／concurrency SLO持續未達；
- 可重現的distribution／operability問題；
- 必要cross-platform system capability缺口。

各Subsystem的需求規格定義代表性workload、SLO、風險與成本收益；DDH不設定
一個適用所有能力的全域效能數字。

語言偏好、單次benchmark、偶發故障、程式碼外觀、未經profiling的推測或
Learning Steward的未驗證建議，均不能單獨觸發抽換。

## Required Path

```text
observe
→ reproduce and classify
→ bounded Python remediation
→ remeasure
→ Backend Evolution Proposal
→ human architecture approval
→ new Task Specification as execution SSOT
→ optional backend implementation
→ conformance／differential／stress verification
→ shadow or limited trial
→ separate default-promotion decision
```

Backend Evolution Proposal只提供architecture change evidence，不授權施工。

## Eligibility

抽換前必須具備：

1. 能力已由明確Port隔離。
2. Language-neutral input、result與failure semantics已定義。
3. 可重複的Contract Verification Assets已admit。
4. Python缺口可在固定workload重現。
5. 已記錄有界Python修正與量測結果。
6. 預期收益大於跨語言build、maintenance與debugging成本。
7. Rollout、fallback與rollback已定義。
8. Contract變更另走L3架構決策，不得混入implementation replacement。

Python implementation是reference implementation，不是behavioral SSOT。Backend
結果不一致時，依Task Specification、semantic specification及admitted
Verification Assets判定，不能預設Python一定正確。

## Authority

- Work Coordinator彙整證據與proposal。
- Learning Steward只可提出候選。
- 人類核准architecture change。
- Test Auditor審核conformance、differential與anti-weakening assets。
- Verification Runner執行相同Contract Verification Assets。
- Completion Judge判定該Task Specification是否完成，不決定default promotion。

將native backend設為default或退役Python backend，必須另行核准。

## Required Scenarios

- 單次timeout不觸發抽換。
- 重複的process-tree cleanup失敗可觸發native process-control提案。
- 代表性高平行workload持續違反固定SLO可觸發候選提案。
- Python／native結果不一致時阻擋promotion。
- Native backend crash只可在預先證明equivalence時自動fallback。
- Concurrency、fault injection、crash、resource ceiling、soak與platform測試
  依該Subsystem的風險與成本收益選用。

