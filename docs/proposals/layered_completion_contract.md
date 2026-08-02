# DDH Layered Completion Contract

**Contract ID：** `DDH-COMP-001`  
**Canonical role name：** `Completion Judge`  
**歷史名稱：** Completion Evaluator  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存已確認的分層完成語義；不授權 runtime、schema 或 migration  

---

## 1. 第一原則

下層完成只是一項可供上層消費的輸入，不會自動向上提升：

```text
Work Package completed
        ≠
subsystem_integrated
        ≠
domain_accepted
        ≠
release_candidate
        ≠
deployment approved
```

每個狀態都必須綁定自己的：

- completion level；
- current candidate identity；
- task／layer specification identity and version；
- required child results；
- required mechanical verification verdict；
- scope／diff closure；
- exception closure；
- risk／external-side-effect boundary。

Agent claim、檔名、System Map node state、歷史 PASS 或下層完成比例都不能單獨
發布任何完成狀態。

## 2. Completion Evaluator 的權責

DDH 需要一個機械 Completion Evaluator 消費 canonical current state，依固定規格
發布 completion decision。實際 Subsystem 名稱與 runtime placement 尚未決定。

它可以：

- 核對 task／layer specification closure。
- 核對 current candidate、MVE verdict、actual diff、child completions 與 open
  exceptions。
- 依固定層級規則發布或拒絕 completion。
- 在 input invalidated 時自動撤回目前 transition，重建 current evaluation。

它不能：

- 改寫 task specification、acceptance 或 risk policy。
- 把 System Map 當成 completion authority。
- 擴大 write scope。
- 把 required child result 改成 optional。
- 核准 deployment、production DB、credential、network 或其他 external side
  effect。
- 因 Agent 宣稱完成而跳過 canonical reconciliation。

人類不需要逐次核准一般 completion；只有需要改變 specification、scope、
architecture、public／data contract、risk policy 或外部副作用授權時才提升。

## 3. Work Package `completed`

Work Package completed 只代表人類選定範圍的任務規格已完成，與 scope 位於
Module、Subsystem、Domain 或其他層級無關。

必要條件：

1. Agent 目標、required behavior 與 acceptance scenarios 已完成。
2. Current immutable candidate 已取得相符的
   `mechanical_verification_passed`。
3. Actual diff、created／deleted resources 與 side effects 都位於允許範圍。
4. 沒有 prohibited mutation 或未分類的 baseline contamination。
5. Required test assets 已 admitted，且沒有 required not-run／stale／suspect
   或 missing coverage。
6. 沒有未處理的 specification、scope、architecture、contract 或 external
   side-effect exception。
7. 實際 touched resources 與 failure closure 沒有留下未確認的 scope 外產品
   影響。
8. Candidate、specification、test assets、verification verdict 與 completion
   evaluation 仍是 current。

Work Package completed 不代表它已和其他 Work Packages 整合，也不代表上層
業務接受。

## 4. `subsystem_integrated`

`subsystem_integrated` 代表所需 Modules／Work Packages 已在同一個 current
integrated candidate 上共同運作。

除適用的 child completion 外，至少要求：

- 所有 required Modules 使用相同 integrated candidate。
- Module 間 contracts、state transitions、shared resources、data flow 與錯誤
  傳遞已驗證。
- 在 integrated candidate 上重跑 affected Module regressions。
- Required Subsystem business scenarios、boundary cases、failure recovery 與
  risk-adjusted stress tests 通過。
- 沒有只在 isolated Module candidate 通過、整合後未執行的 required result。
- Shared-contract ownership gap、unresolved integration conflict 與 outside-scope
  impact 已封閉。

即使 Work Package scope 本身就是整個 Subsystem，也不能因名稱或 scope 相同
自動發布 `subsystem_integrated`；仍需獨立的 integrated-candidate evaluation。

## 5. `domain_accepted`

`domain_accepted` 代表同一個 current Domain candidate 已完成完整 Domain 業務
能力驗收。

至少要求：

- 所有 required Subsystems 已在同一個 Domain candidate 上完成整合。
- Domain 端到端 workflows、business invariants 與 failure semantics 通過。
- 跨 Subsystem transaction、資料一致性、補償、權限與錯誤恢復通過。
- 適用的 capacity、concurrency、load、soak 與 degradation requirements 通過。
- System Map impact query 與 bounded live-source confirmation 找出的 affected
  external nodes 已完成必要 regression closure。
- Scope 外需要 repair 的節點已有獨立核准，不能由 verification expansion
  偷渡 write permission。
- 沒有 unresolved Domain-level specification／contract／risk exception。

## 6. `release_candidate`

`release_candidate` 代表候選版本具備進入獨立發佈決策流程的資格，不代表允許
部署或執行外部副作用。

至少要求：

- 所有 required Domain／Global acceptance 已在同一個 release candidate identity
  上完成。
- Required cross-Domain workflows 與 regressions 通過。
- Release-specific security、compatibility、migration、packaging、configuration
  與 operational readiness checks 通過。
- Required platform matrix 與 release performance profile 完成。
- 已知限制、unresolved risks 與 external dependencies 符合固定 release policy。
- Candidate、artifacts、configuration 與驗證 inputs identities 一致。

Deployment、production database、real credentials、network mutation、data
migration、publication 與其他 external side effects 維持獨立高風險流程。

## 7. Completion 不自動向上冒泡

Higher-layer evaluator 只能消費 current child completion，不能將其直接相加：

```text
all_required_children_completed
＋ same_current_integrated_candidate
＋ higher_layer_specification_closure
＋ higher_layer_mechanical_verification_passed
＋ scope／exception／risk closure
＝ higher_layer completion
```

Higher-layer failure 不自動撤銷所有 lower-layer completion。系統先分類：

- 純 integration／higher-layer defect：lower completion 保持成立，建立上層 repair。
- 證明某 lower-layer implementation／specification／test coverage 原本有缺口：
  只 invalidates affected lower completion，建立 current candidate／subject 重驗。
- Impact unknown：不得猜測，使用 System Map index 與 bounded live-source
  discovery 封閉 affected closure。

## 8. System Map 參與和維護狀態

每個 higher-layer completion evaluation 使用 System Map：

- 定位實際包含 nodes。
- 查詢 dependencies、reverse dependents 與跨層關係。
- 產生 higher-layer regression candidates。
- 將 actual touched resources 對回 nodes，發現原本漏估的影響。

System Map 不決定 completion、scope、acceptance 或 mutation permission。
與 live source 衝突時，對受影響範圍使用 bounded live-source discovery。

因 System Map 尚未完全落地，本 Contract 只固定三種概念結果，不固定 enum、
field、API 或 reconciliation algorithm：

- Map 與本次已確認 actual architecture 一致。
- Map maintenance 尚待完成。
- Map query unavailable，但已使用 bounded live-source fallback。

Map maintenance pending 不自動等於功能驗收失敗。只有以下情況才阻止 completion：

- 任務規格明定 Map 更新本身是 required deliverable；或
- 缺少 Map 與 live-source fallback 後，仍無法安全封閉 impact scope。

## 9. 業務場景

### 9.1 三個 Module 完成，但 Subsystem 尚未整合

Workspace Subsystem 有 PathNormalizer、ManifestLoader、ManifestIndex 三個 Modules：

- 三個 Module Work Packages 都已 completed。
- Integrated scenario 發現路徑已 canonicalize、Manifest 已載入，但 ManifestIndex entry 未寫入。

結果：

| Completion level | Decision |
|---|---|
| 三個 Work Packages | 保持 completed；除非分析證明其中一個原完成條件有缺口 |
| `subsystem_integrated` | 不成立，建立 integration repair |
| `domain_accepted` | 不可發布 |
| `release_candidate` | 不可發布 |

修復後建立新的 integrated candidate，重跑 affected Module regressions、
Subsystem state machine、failure cases 與適用 stress tests，才可發布
`subsystem_integrated`。

### 9.2 Subsystem integrated，但 Domain 尚未 accepted

PathNormalizer／ManifestLoader／ManifestIndex 整合通過，但 Domain plugin-discovery workflow 的跨 Subsystem
補償失敗。Subsystem integration 結果不自動變成 Domain acceptance；Domain
candidate 必須修復路徑別名、失效資產移除、索引重建與資料一致性場景後重新驗證。

### 9.3 Release candidate 不授權部署

所有 required Domains 與 release checks 通過並形成 release candidate，但部署
需要 production credential 與 database migration。Completion Evaluator 只能
發布 `release_candidate`，不能開始部署；後續交給獨立高風險流程。

## 10. Invalidation and State

每個 completion level 有自己的 current evaluation：

```text
inputs_collecting
→ canonical_reconciliation
→ closure_evaluating
→ completed／not_ready／nonpass／escalation_required
                                  └→ invalidated
```

- Child completion、candidate、specification、MVE verdict、scope closure 或
  exception state 變更時，只 invalidates affected completion level and dependents。
- 舊 completion 不能套用到新的 candidate identity。
- At-least-once events 只作通知；protected transition 前重讀 canonical current
  identities。
- Event loss／restart 後可從 current candidate、specification、tests、verdicts、
  diff 與 exception state 重建，不依賴永久 receipt chain。

## 11. Stress Contract

- 數百 Work Packages 亂序完成時，不會自動誤升級 Subsystem。
- 多個 child completions 來自不同 candidate 時，不能拼成 higher-layer completion。
- Higher-layer aggregation 期間 child candidate／specification invalidation 可阻止
  stale publication。
- 所有 Modules PASS 但 shared-state／cross-contract scenario FAIL 時，
  `subsystem_integrated` 不成立。
- System Map 漏估 scope 外節點時，actual diff mapping、reverse dependency 與
  live-source fallback 觸發重新評估。
- 多個 Subsystems 同時完成時，只能對單一 current Domain candidate 判定。
- Release candidate 建立期間 required Domain 被撤回時，stale release result
  不得發布。
- Duplicate／late／out-of-order completion events idempotent。
- Completion Evaluator restart 後可由 current canonical facts 重建。
- Routine reconciliation、aggregation、invalidation 與 completion publication
  的 Agent token cost 為零。

## 12. 對應機械測試

```text
test_work_package_completion_binds_exact_task_candidate_verdict_and_diff
test_agent_claim_or_system_map_state_cannot_publish_completion
test_completed_modules_do_not_automatically_integrate_subsystem
test_subsystem_integration_requires_same_current_integrated_candidate
test_higher_layer_failure_invalidates_only_proven_affected_lower_completion
test_domain_acceptance_requires_end_to_end_business_and_invariant_closure
test_scope_external_impact_requires_verification_and_separate_write_authority
test_release_candidate_does_not_authorize_deployment_or_external_side_effect
test_map_maintenance_pending_does_not_override_task_acceptance
test_missing_map_and_live_fallback_blocks_only_when_impact_cannot_close
test_old_candidate_completion_cannot_pollute_current_higher_layer
test_invalidation_racing_completion_prevents_stale_publication
test_large_out_of_order_completion_graph_is_deterministic_and_zero_agent
```

## 13. Retention

Completion result 只保留到目前上層 transition、repair 或 terminal reporting 已可靠
消費，之後依 retention policy 刪除。DDH 不建立永久 PASS receipt、completion
history chain 或 System Map lifecycle state。

長期 Evidence Retention 仍是可重播 pytest、fixtures、configuration、profiles、
seeds 與 workload models。需要版本／release 稽核的外部流程應另行定義其必要
artifact，不反向讓一般 Work Package 保存全部歷史 logs。

## 14. Self-Evolution Boundary

OLE 可以改善 completion evaluation order、incremental dependency reduction、
event coalescing、cache、summary 與 retry scheduling，但不能修改：

- 各 completion level 的必要語義；
- task／layer specification authority；
- required child／verification closure；
- scope／diff／exception closure；
- required／optional acceptance；
- System Map 非 authority 邊界；
- external high-risk boundary；
- invalidation precedence 或 retention semantics。
