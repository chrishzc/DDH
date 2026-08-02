# Decision 0024: Staged External High-risk Adapter Productization

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

External high-risk capability 分為兩個產品階段：

1. `Phase 7A — Contract and Simulator`：DDH MVP 必備。
2. `Phase 7B — Real Provider Adapter`：核心 MVP 通過後，依實際需求逐個核准。

Phase 7A 使 external authority、uncertain result 與 reconciliation 成為可執行
驗證的產品邊界，但不讓 production provider、credential 或外部整合阻塞核心
DDH MVP。

## Phase 7A: MVP Contract and Simulator

MVP 必須提供 technology-neutral contracts／fixtures 與 deterministic simulator，
驗證：

- exact External Operation Plan 與 plan digest；
- Candidate／commit／artifact／configuration／target binding；
- approval currentness 與 drift invalidation；
- Trusted Executor Port 與 capability-scoped invocation；
- credential reference boundary；
- success、failure、rejection、timeout、uncertain、reconciliation 與 rollback；
- external postcondition 不以 exit code 或 Agent claim 取代；
- uncertain operation 禁止盲目 retry。

Phase 7A 不包含：

- 真實 production credential；
- 真實 deployment、release publication、production database mutation、outbound
  message 或其他 external write；
- 任意 shell command、任意 URL 或任意 network request 的 generic Trusted
  Executor；
- 因 simulator PASS 自動取得任何 external authority。

Simulator 必須能注入 provider timeout、late response、partial effect、target
drift、duplicate request、rollback failure 與 reconciliation unavailable。

## Phase 7B: Real Provider Adapters

真實 Adapter 不作核心 MVP release blocker。第一個及其後每個 Adapter 都是
獨立、可選、capability-scoped 的產品擴充，必須有自己的 Task Specification、
architecture scope、risk、acceptance、retention／compliance 與 human
implementation authorization。

進入 Phase 7B 的最低條件：

1. 核心 MVP 的 L1 serial、L2 parallel、verification quality、mutation
   boundary、recovery 與 Phase 7A simulator acceptance 已通過。
2. Human 選定 exact provider、environment、operation class 與 blast radius。
3. 有隔離的 test account、staging target 或 disposable target。
4. 規格固定 idempotency、retry eligibility、reconciliation、rollback／
   compensation、credential、postcondition 與 retention。
5. Trusted Executor 具有可機械驗證的 least privilege 與 capability boundary。
6. 有 separate approval 可進行實作、有限試用及任何真實 side effect。

Provider Adapter 的 API／SDK／credential model 不進入 core contract。Core 只
依 Trusted Executor Port 與 typed result 工作；未安裝 Adapter 時，系統應明確
停在 `adapter_unavailable`／`approval_required`，不影響一般 Work Package。

## Initial Adapter Selection

不預先指定第一個 provider。選擇順序依實際需求及：

- 可回復性；
- target 隔離程度；
- postcondition 可觀察性；
- idempotency；
- credential blast radius；
- uncertain-result reconciliation 能力。

預設優先考慮 staging artifact publication 或其他可隔離、可查驗、可回復操作。
Production database migration、external transaction、正式訊息發送與不可逆操作必須各自建立
更嚴格規格，不得因已有另一個 Adapter 而繼承 authority。

## Business Scenarios

### MVP Requests Deployment

一般 Work Package 完成並產生 deployment plan。Phase 7A simulator 可驗證 plan
與 state transitions；因沒有 real Adapter／approval，流程停在
`adapter_unavailable` 或 `approval_required`，不進行真實部署。

### Staging Adapter Timeout

經核准的 staging Adapter 送出 operation 後 response timeout。Trusted Executor
停止 retry，查詢 exact target current state並分類為 `succeeded`、
`not_executed` 或 `uncertain`；只有能證明安全時才依原 Plan retry。

### Generic Escape Attempt

Agent 嘗試把未建模的 external action 包裝為 generic shell／HTTP operation。
Trusted Executor 因沒有明確 operation class、capability 與 approved plan 而
拒絕，不能以工具可用性推導 authority。

## Acceptance

- Phase 7A 可在沒有 network、provider SDK 或 credentials 時重播全部場景。
- Simulator 與 fixtures 不能執行真實 external writes。
- Generic shell／URL／network escape 不存在。
- Phase 7B Adapter 缺少、故障或未核准時，不阻塞 core DDH execution。
- 每個 real Adapter 的 authority、credential、retention 與 rollout 隔離。
- 一個 Adapter 的核准不能授權其他 provider、target 或 operation class。
- Phase 7A PASS 不等於 release、deployment 或 external operation approval。
