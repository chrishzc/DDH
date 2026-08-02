# Decision 0011: Phase 7 External High-Risk Operations

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 7將release publication、deployment、production database、credential／secret、
external network mutation、outbound messaging與irreversible filesystem operation
置於一般Work Package外的獨立高風險流程。

Decision 0024將產品化分為兩段：Phase 7A的Contract、fixtures與deterministic
simulator是MVP必備；Phase 7B真實provider Adapters在核心MVP通過後，依實際
需求及獨立人類核准逐個加入。Phase 7A不持有credential或執行真實external
write，Phase 7B也不得提供generic shell／HTTP escape。

```text
work_package_completed
≠ domain_accepted
≠ release_candidate
≠ external_operation_approved
≠ external_operation_succeeded
```

一般Work Package可自主建立artifact、migration rehearsal、deployment manifest、
release notes draft、dry-run、preflight與External Operation Plan，但不得因此取得
真實外部操作權限。

## Exact Operation Plan and Approval

External Operation Plan至少固定operation class、exact Candidate／commit／artifact／
configuration／target、ordered operations、allowed／prohibited actions、
credential references、pre／postconditions、timeout／budget、idempotency、retry、
rollback／compensation、uncertain-result procedure與approval expiry。

Human approval綁exact plan digest與上述identities。Candidate、commit、artifact、
config、target、operation sequence、rollback或expiry任一改變，approval失效。

這是一次核准完整高風險計畫，不是恢復每一步人工Checkpoint。

## Trusted Executor

只有capability-scoped Trusted Executor可執行approved external operations。它必須
least privilege、validate exact identities、拒絕臨時新增operation、redact
secrets、回傳structured step results並驗證external postconditions。

Main Agent可準備計畫與解讀結果，不能繞過Executor直接操作production。
Learning Steward與System Map均不能授予external authority。

## Local High-risk State

```text
plan_draft
→ preflight_ready
→ approval_required
→ approved
→ executing
→ succeeded | failed | uncertain
→ reconciled | rollback_required | human_decision_required
```

這是單一外部操作的局部狀態，不建立全域Task lifecycle。

## Retry and Uncertainty

只有能機械證明操作未發生，或具有效idempotency key、target precondition仍一致、
重複執行無額外副作用且approval仍current時，才能依Plan自動retry。

Request已送出但外部結果不確定時：

```text
stop retry
→ inspect current external state
→ reconcile
→ classify succeeded／not executed／uncertain
```

無法確定時需人類決策，不能盲目重送外部交易、migration、publication或deployment。

## Database, Credentials and Messaging

- Production DB要求approved contract、backup-first、restore route、disposable
  rehearsal、pre／post reconciliation、rollback或forward repair與exact target。
- 「保留資料」預設採backup→new/additive target→migrate→reconcile→reversible
  config switch，不以destructive rebuild為預設。
- Credential只以reference出現在Plan，執行時由Executor以最小權限取得；不得進
  spec、Agent Context、Ledger、Memory或test output。
- Outbound message固定recipient／channel、content或approved template variables、
  send count與postcondition；draft可自主，send需approval。

## Release Candidate and Postconditions

Completion Judge發布release candidate需same identity上的Domain／Global acceptance、
security、compatibility、packaging、asset parity、platform matrix、performance、
migration rehearsal與configuration readiness。

Command exit code 0不等於外部成功。Executor必須從current external state驗證
artifact可取得、deployed version、health、database consistency、configuration或
message delivery。

## Acceptance

Phase 7必須證明：

- MVP可在沒有provider、network與credential時以simulator重播高風險流程；
- release candidate、approval、execution與postcondition分離；
- drift使approval失效；
- Trusted Executor無法越過Plan；
- uncertain side effect不盲目retry；
- database backup／rehearsal／reconciliation／repair完整；
- credentials與sensitive output不進一般DDH資料；
- destructive target在執行前機械解析；
- external failure不阻塞一般DDH施工；
- rollback failure保存current facts並要求新的高風險決策；
- real Adapter缺少或未核准時明確停在`adapter_unavailable`／
  `approval_required`，不推導外部權限。
