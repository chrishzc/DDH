# Long-term Orchestration Memory Model

**Contract ID：** `OLE-MEM-001`  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存長期編排記憶的物件、查詢、消費與維護責任；
不授權 runtime、schema、vector store、model provider 或 prompt implementation  

---

## 1. 第一原則

Long-term Orchestration Memory 只能改善主 Agent 如何編排工作，不能影響工作必須
完成什麼。

主 Agent 是 Memory consumer，不是 maintainer。它不能直接新增、修改、升級、
刪除 Memory 或自行調整 confidence。

## 2. Memory Type 白名單

允許：

- `partitioning_strategy`
- `parallelization_decision`
- `agent_profile_selection`
- `context_envelope_template`
- `context_expansion_strategy`
- `integration_sequence`
- `handoff_summary_template`
- `orchestration_recovery_order`

禁止：

- product expected behavior；
- Task Specification／acceptance；
- Architecture／schema／public contract；
- scope／write permission／risk class；
- pytest oracle／threshold／measurement logic；
- human escalation／external-side-effect boundary；
- credentials、full conversation、source、diff 或 raw logs。

新增 Memory Type 必須先修改白名單與 policy，不能由 Analyzer／Critic 自行擴張。

## 3. 概念資料模型

```text
memory identity and version
memory type and lifecycle status

applicability conditions
recommended orchestration adjustment
expected effect
prohibited uses

support evidence summary
counterexample summary
independent support count
confidence and confidence reason

profile compatibility
invalidation conditions
expiration conditions
conflict group
supersedes reference
```

這是語義模型，不固定 exact schema、field names 或 storage。

## 4. Applicability

Applicability 必須可機械比對，不能只保存模糊建議。

不合格：

> 多使用子代理通常比較快。

合格：

```text
when:
  scope_level: Subsystem
  module_count: at_least_three
  write_zones: disjoint
  shared_contract_owner: centralized
  integration_cost: bounded
  product_test_lanes: separable

recommend:
  parallelize_module_lanes
  require_subsystem_join_barrier
```

Applicability 無法確認時，Memory 不適用。

## 5. Evidence and Confidence

Confidence 不能只是 Analyzer 自行填入的分數。至少考慮：

- independent Work Package／execution run count；
- success、failure 與 counterexamples；
- evidence 是否跨時間與不同 runs；
- Agent／Context／tool／System Map query profile compatibility；
- Critic replay／trial results；
- 最近支持與反證時間。

至少分開保存：

```text
support evidence summary
counterevidence summary
confidence class
confidence reason
```

不能用單一總分掩蓋重要反例。Operational Telemetry 只能提供 aggregate signals；
不得直接寫成 Memory，仍須經 Ledger、Analyzer 與 Critic。

## 6. Version and Lifecycle

```text
candidate
→ active
→ suspended／superseded／retired
```

更新建立新 immutable version，不覆寫舊內容。

重新評估條件：

- Agent／Context／tool profile 改變；
- System Map query／isolation capability 改變；
- 新 counterexample；
- applicability 不再成立；
- Critic 發現效果退步；
- 長期沒有新支持；
- template／strategy 被新版本取代。

Memory version 只管理編排經驗，不建立 legacy stable cross-version architecture
identity。

## 7. Conflict Resolution

Resolver 順序：

1. Task Specification、scope、risk 與 safety 永遠優先。
2. 排除 invalid／expired／profile-incompatible Memory。
3. Applicability 更具體者優先。
4. Independent evidence 更強、profile 更相容、版本更 current 者優先。
5. 仍有 material conflict 時回到固定 baseline。

Baseline：

```text
single main Agent
＋ bounded initial Context
＋ no optional parallelism
```

Memory conflict 不阻擋施工或詢問人類，只形成新的 evolution candidate。Memory
不能因 confidence 高而越過 Task Specification 或 safety boundary。

## 8. Maintenance Responsibilities

| Component／role | Responsibility |
|---|---|
| Ledger Collector | 記錄 actual execution attempts |
| Mechanical Prefilter | 判定 orchestration signal、聚合 candidates |
| Evolution Analyzer | 提出 Memory Candidate |
| Independent Critic | replay／trial，接受、拒絕或要求更多證據 |
| Memory Registry | 發布 immutable active version |
| Memory Reconciler | counterexample、失效、衝突、suspend、supersede |
| Main Agent | 消費 Cards，回報 applied／declined 與 actual effect |

主 Agent 不能直接寫 Registry。它可以拒絕本次建議並提供 bounded structured
reason；該理由與執行結果進入 Ledger，由 Analyzer／Critic 決定是否影響
Memory。

## 9. Query Triggers

Memory 不在每個 tool call 查詢，只在可能改變 orchestration 的 transition 觸發：

| Trigger | Requested Memory types |
|---|---|
| T1 Task Specification ready → planning | partitioning、parallelization、Agent profile |
| T2 Context Envelope materialization | Context template／initial depth |
| T3 Context expansion／repartition evidence | Context expansion、partition／profile adjustment |
| T4 Integration／handoff | integration sequence、handoff summary |
| T5 多個 confirmed recovery routes 都合法 | approved recovery order |

同一 Task Feature Envelope 未改變時，不反覆查詢。Product coding、pytest oracle、
acceptance 或 permission 決策不觸發 Memory Query。

## 10. Task Feature Envelope

由機械流程建立：

```text
task specification identity
scope level
risk class
selected System Map nodes
dependency／reverse-dependency shape
module count
predicted write overlap
shared contracts／resources
product／test lane separability
Context budget
available Agent profiles
current DDH capability health
current execution phase
```

來源：

- Task Specification：goal、scope、risk、constraints；
- System Map：actual architecture index／candidate relations；
- live source：current implementation confirmation；
- Operational Telemetry：current capability health；
- current execution：Context requests、conflicts、retries。

System Map 與 Memory 都不因作為 feature input 而取得 authority。

## 11. Resolver and Guidance Envelope

Memory Resolver 先機械執行：

1. applicability filter；
2. profile／version compatibility；
3. invalidation filter；
4. conflict resolution；
5. Context budget selection。

主 Agent只收到 bounded `Orchestration Guidance Envelope`：

```yaml
memory_query_result_id: derived-query-id
task_feature_digest: derived-feature-digest

baseline_policy:
  execution: single_main_agent
  context: bounded_initial_context

applicable_cards:
  - memory_id: example-memory
    version: example-version
    type: parallelization_decision
    why_matched:
      - disjoint_module_write_zones
      - centralized_shared_contract_owner
    recommendation: parallelize_module_lanes
    prohibited_uses:
      - do_not_expand_write_scope
      - do_not_skip_subsystem_join
    confidence: high
    counterexample_summary: shared_database_migration_requires_serialization

conflicts: []
```

Exact schema 尚未固定。主 Agent不得讀取 entire Memory Store、raw Ledgers、full
historical prompts 或 logs。

## 12. Consumption Contract

Orchestration Plan 必須引用：

```text
orchestration_memory_query_result_id
＋ applied_memory_ids
＋ declined_memory_ids_and_reason
＋ baseline_fallback_if_any
```

Contract 必須阻止：

- required transition 未查詢 Memory；
- query 產生但 plan 未消費；
- 使用 expired／invalid Memory；
- Card 被拿來擴大 scope、降低 acceptance 或改 risk；
- Main Agent載入 entire store；
- 使用後沒有把 actual effect 提供給 Ledger。

Memory unavailable 時：

```text
memory unavailable
→ fixed baseline policy
→ continue
```

Memory 工具故障不阻擋產品施工。

## 13. Main Agent Decline

主 Agent可以因 current facts 拒絕建議，例如：

- Task Feature Envelope 漏掉 shared resource；
- live source 證明 write zones 重疊；
- required Agent profile unavailable；
- integration cost 明顯高於 prediction；
- applicability 與本次任務不完全相符。

Main Agent只能拒絕本次使用，不能修改 Memory。Reason 與 actual outcome 成為
counterexample candidate；是否 shrink applicability、降低 confidence、suspend
或 version update 由 Analyzer／Critic／Reconciler 決定。

## 14. Child Agent Boundary

Child Agent 不讀 Memory Cards 或 Store。主 Agent只把已決定的 orchestration
結果轉成最小 Context Envelope：

```text
subgoal
read／write whitelist
required contracts
acceptance
handoff format
budget
escalation conditions
```

避免 Child Agent把 Memory 誤當 scope authority、自行擴大 Context 或承擔不必要
歷史成本。

## 15. Reconciliation Triggers

Memory Reconciler 在以下時點執行：

- new Memory accepted；
- valid counterexample；
- Agent／Context／tool／System Map query profile version change；
- expiration／review condition；
- active memories 進入相同 conflict group；
- applied Memory 導致顯著 regression；
- Memory Store／index rebuild。

Routine filter／conflict／lifecycle reconciliation 不使用模型；只有 semantic
candidate、反例與無法機械處理的衝突使用 Analyzer／Critic。

## 16. 業務場景

多次 Workspace Subsystem 任務中，Test Agent 都因缺少跨 Module data-contract 摘要而
反覆要求 Context expansion。

Memory Candidate：

> 對具有跨 Module state machine、但 test write zone 獨立的 Subsystem 任務，
> Test Agent 初始 Context 應包含相關公開 data-contract 摘要與一層 reverse
> dependencies。

它不保存 Workspace 規格正文、不擴大 Test Agent scope、不改變 pytest，只調整 Context
template。後續 Context requests 從五次降為一次；若其他任務因此載入大量無關
資料，該結果形成 counterexample，用於縮小 applicability。

## 17. Stress Contract

- 大量 Memories 中只投影 bounded applicable Cards。
- 多條相互衝突 Memories deterministic fallback。
- Old profile Memory 不套用新 capability。
- Broad Memory 不壓過 specific counterexample。
- Counterexample 可觸發 suspend／applicability shrink candidate。
- Store unavailable 時使用 baseline，不阻擋施工。
- Erroneous Ledger／Telemetry 不能直接成為 active Memory。
- Cards 不含 specification、permission、secret 或 full history。
- Applicability filtering、conflict resolution 與 routine reconciliation
  不使用 Agent／LLM。
- Memory 數量增長時 Main Agent Context 成本有界。

## 18. 對應機械測試

```text
test_only_whitelisted_orchestration_memory_types_can_be_published
test_memory_never_overrides_spec_scope_risk_acceptance_or_permission
test_applicability_must_be_mechanically_matchable
test_confidence_preserves_support_counterevidence_and_reason
test_specific_compatible_memory_precedes_broad_memory
test_material_conflict_falls_back_without_blocking_or_human_checkpoint
test_main_agent_cannot_write_promote_delete_or_reconfidence_memory
test_memory_queries_run_only_at_orchestration_transitions
test_plan_must_reference_and_disposition_queried_memory_cards
test_memory_store_unavailable_uses_fixed_baseline
test_child_agent_receives_context_result_not_memory_store
test_counterexample_routes_to_analyzer_critic_not_direct_mutation
test_large_memory_store_projects_bounded_zero_agent_guidance
```

## 19. Self-Evolution Boundary

Analyzer／Critic／OLE 可以提出與驗證白名單內的 Memory changes，但不能自行
修改 Memory Type whitelist、Task Feature authority、baseline safety、required
query transitions、specification／scope／risk／acceptance／measurement 或 human
escalation boundaries。
