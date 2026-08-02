# Task Specification and Work Package Boundary

**Contract ID：** `SPEC-WP-001`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存每次任務 SSOT、execution projection、readiness、versioning
與 revision boundary；不授權 runtime、schema、CLI 或 migration  

---

## 1. 第一原則

Task Specification 是每次任務的 SSOT。Work Package 是依 Task Specification、
current project state 與執行能力產生的 execution envelope／projection，不是第二
份 SSOT。

```text
Specification Package
├─ Task Specification       ← human-confirmed task SSOT
└─ Work Package Projection  ← mechanically generated execution envelope
```

兩者邏輯責任分離；小型任務可以存在同一實體文件，大型／高風險任務可以使用
兩份固定引用文件。檔案數量不改變 authority。

## 2. Task Specification

至少保存：

```text
user goal and source
selected scope and level
required observable behavior
business scenarios
acceptance conditions
constraints and prohibitions
non-goals
risk／external-side-effect boundary
fixed long-term specification／decision references
ambiguities requiring human decision
```

- 使用者寫明的 Agent 目標是來源。
- Agent 可以整理成結構化 draft，但不能改寫使用者意圖。
- System Map 只協助定位 actual scope／impact，不是規格來源。
- Live assets 證明 current implementation，不決定 expected behavior。

## 3. Work Package Projection

由 confirmed Task Specification＋current state 解析：

```text
task specification identity／digest
resolved actual nodes and resources
read／write boundaries
prohibited operations
risk execution profile
budget allocation
required test／stress profiles
candidate／baseline identity
partitions and ownership plan
Context Envelope references
runner／environment profile
automatic recovery routes
human escalation conditions
```

可以因以下原因自動建立新 generation：

- partition／Agent profile adjustment；
- Context expansion；
- runner／tool recovery；
- System Map query 改用 live-source fallback；
- candidate generation change；
- parallel-to-serial fallback；
- execution ordering／sharding change。

只要 Task Specification authority fields 未變，就不需人類重新確認。

## 4. Layered Readiness

Readiness 判斷「能否產生不需要猜 expected behavior 的 executable acceptance」，
不以文件長度、檔案數或欄位填滿比例判斷。

### L0／Documentation

使用者清楚寫下：

- 要修改什麼；
- 不要改什麼；
- 如何做 lightweight confirmation。

不建立完整 Work Package lifecycle。

### Module

至少：

- input／output；
- normal calculation／transformation；
- error／boundary behavior；
- side effects；
- executable acceptance examples。

### Subsystem

另外：

- Module responsibilities／contracts；
- state transitions；
- shared resources；
- cross-module business scenarios；
- failure recovery；
- stress applicability。

### Domain

另外：

- end-to-end workflows；
- business invariants；
- cross-Subsystem transactions；
- compensation／consistency／permission；
- capacity／concurrency／load／soak expectations。

### Global

另外：

- cross-Domain behavior；
- compatibility／security／operational invariants；
- global regressions；
- release-level constraints。

## 5. Agent Drafting Boundary

Agent 可以自動補充：

- current source／test paths；
- System Map node references；
- existing public contracts；
- admitted pytest／coverage gaps；
- 可由規格直接推導的正向、反向、邊界與錯誤測試；
- runner、Context、partition、budget projection；
- 不改 observable behavior 的技術細節。

Agent 不能自行補充：

- missing business expected outcome；
- operation authority；
- monetary／state／consistency business rules；
- compatibility-breaking permission；
- new schema／public contract；
- external-side-effect permission；
- acceptance threshold。

缺少上述內容時產生 structured `specification_not_ready`，不能猜測施工。

## 6. Confirmation Strictness

避免逐欄或逐測試人工 approval：

1. Agent 產生完整 Specification Package draft。
2. Readiness Checker 機械標示缺口與矛盾。
3. 人類一次確認整個 Task Specification version。
4. Work Package Projection 自動產生與調整。
5. 一般 implementation、test、repair、repartition、Context expansion 與 runner
   recovery 不再詢問人類。

只有 authority-bearing change 才需要重新確認。

Decision 0025固定authority roles與確認時點：

- Demand Owner確認goal、behavior、scope、prohibition、acceptance與task budget；
- Architecture Owner確認L3 architecture／schema／public contract；
- Profile Policy Owner只在project defaults建立或改版時確認；
- External Authority Owner只核准exact external operation；
- Main Agent可起草與編譯，但沒有self-confirm權；
- Mechanical components可執行enforcement／verification／completion，但不能創造
  authority。

L0的明確人類請求可直接構成最小確認；L1／L2一次確認exact Task
Specification version；L3先確認authority change，再確認引用它的Task
Specification。一般local work不要求cryptographic signature、Checkpoint或逐關
按鈕。

## 7. Freeze and Revision

Confirmed Task Specification version immutable。

需要新版本與 human-confirmed structured diff：

- goal change；
- required behavior／acceptance change；
- write scope expansion；
- prohibition change；
- risk／external permission change；
- architecture／schema／public contract change。

只需要新的 Work Package Projection generation：

- Agent／partition adjustment；
- Context change；
- runner placement；
- retry／recovery route；
- test ordering／sharding；
- System Map query fallback；
- non-authoritative resource resolution。

不建立 global freshness chain；只 invalidates 被改變內容實際影響的 projection、
candidate、subject 與 completion。

## 8. Structured Exception Report

需要修改 Task Specification 時，停止 affected work 並報告：

```text
trigger
current specification clause
observed evidence
attempted safe actions
why current scope／behavior is insufficient
affected nodes and contracts
requested change
available options and tradeoffs
verification impact
external-side-effect impact
```

Known tool failure、runner recovery、Context expansion 或合法 repartition 不產生
人類 exception report。

## 9. Completion Boundary

Work Package completion 依 `DDH-COMP-001` 核對：

- exact Task Specification version；
- current candidate；
- MVE verdict；
- actual diff／scope closure；
- exception closure。

Work Package Projection 自己不能宣告 completion，也不能修改 required
acceptance。

Completion Judge的PASS不需要額外完工核准。Subsystem integration、Domain
acceptance與release candidate依各自層級規格另行判定，不能由Work Package
completion向上推導。

## 10. 業務場景

使用者要求修改 Workspace Module：

> 路徑正規化接受 workspace root 與相對路徑，輸出 canonical repository path；逃逸 workspace 的路徑必須拒絕。

Agent整理正常計算、rounding、zero／negative boundaries、required pytest 與
禁止改 public API；人類一次確認 Task Specification。

Work Package 自動解析 actual Module／source、affected tests、product／test write
partitions、Context、runner 與 budget。Runner 故障只重建 projection／environment，
不修改 Task Specification。

後來發現 API 無法表達 junction／symlink resolution mode，涉及 public contract。系統產生
versioned exception proposal，不能自行補規格。

## 11. Stress Contract

- Large Domain Specification 有大量 scenarios，Agent Context 仍有界。
- Frequent repartition 不產生 Task Specification version storm。
- Missing expected outcome 正確阻擋 readiness。
- Tool／runner failure 不誤觸 specification revision。
- Specification revision 與 candidate freeze 競態會 invalidates 舊 projection。
- System Map drift 只觸發 live confirmation／maintenance，不改 Task Specification。
- Work Package Projection 無法擴大 authority scope。
- Human 只確認 Task Specification，不逐次批准 execution projection。
- Readiness、version diff 與 projection generation 不依賴 Agent／LLM runtime。

## 12. 對應機械測試

```text
test_task_specification_is_task_ssot_and_projection_is_not
test_small_package_can_physically_bundle_logically_separate_sections
test_readiness_depends_on_executable_expected_behavior_not_document_length
test_agent_can_resolve_current_paths_but_not_invent_business_outcome
test_missing_business_authority_emits_specification_not_ready
test_projection_rebuild_does_not_require_human_when_authority_is_unchanged
test_authority_change_requires_new_specification_version
test_tool_recovery_context_and_repartition_do_not_revision_specification
test_projection_cannot_expand_scope_or_weaken_acceptance
test_system_map_drift_does_not_rewrite_task_specification
test_large_layered_specification_projects_bounded_context
```

## 13. Self-Evolution Boundary

OLE 可以改善 draft／summary／Context templates、readiness explanation 與 projection
assembly efficiency，但不能修改 Task Specification authority、required fields by
layer、human confirmation boundary、revision classification、exception fields、
acceptance、scope、risk 或 external-side-effect permission。
