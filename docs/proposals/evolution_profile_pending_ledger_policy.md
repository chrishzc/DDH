# Evolution Profile Pending Ledger Policy

**Contract ID：** `OLE-PROFILE-001`  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 pending Ledger 的資源、優先級與 expiration 語義；
不固定實際數值、storage、queue、scheduler 或 model provider  

---

## 1. 第一原則

Attempt Ledger 是短期自進化原料，不得因 Analyzer 長期不可用而變成永久事件庫。
也不得為了控制 storage，在尚未進行任何機械判定時任意刪除所有 learning
candidate。

採用：

```text
immediate mechanical prefilter
→ priority and bounded pending
→ model analysis when justified
→ explicit terminal disposition
→ deletion
```

Completion、verification 與新 Work Package execution 不等待本流程。

## 2. Immediate Mechanical Prefilter

每份 sealed Ledger 先由零 Agent／LLM prefilter 分類：

| Prefilter result | Disposition |
|---|---|
| `routine_no_orchestration_signal` | `consumed`，不建立 memory candidate |
| `known_pattern_no_change` | 依既有記憶 policy 更新 bounded mechanical support observation 後 `consumed` |
| `one_off_product_or_test_failure` | 無編排訊號，不送模型，`consumed` |
| `candidate_new_pattern` | 建立 pending candidate |
| `candidate_repeated_pattern` | 與相似 candidates 聚合後 pending |
| `critical_orchestration_failure` | 高優先 pending Analyzer／Critic |
| `prefilter_unknown` | 有界等待 prefilter repair／retry |

`consumed` 只表示此 Ledger 已得到完整的 learning disposition，不表示產品 PASS、
長期記憶有更新或 Critic 已執行。

## 3. Priority Classes

概念優先級：

| Priority | 適用訊號 |
|---|---|
| P0 | mutation boundary 失效、unsafe recovery、權限／scope 危險、自進化候選導致退步 |
| P1 | 重複 no-progress、handoff／partition／Context 失敗、顯著 budget waste |
| P2 | 新 task split、Context、profile 或 orchestration 改善候選 |
| P3 | 單次低信心模式、非阻斷成本優化或待累積觀察 |

Priority 只影響分析順序、retry 與 retention budget，不能改變產品 completion、
acceptance、write scope 或人類升級條件。

## 4. Versioned Evolution Profile

每個 Evolution Profile 至少固定四種 budget：

```text
maximum_pending_age
＋ maximum_pending_bytes
＋ maximum_pending_items
＋ model_analysis_token_budget
```

可以另外定義：

- priority-specific retry／retention weights；
- candidate grouping keys；
- circuit-breaker／health-probe policy；
- storage pressure watermarks；
- maximum batch size；
- bounded artifact retention；
- final expiration disposition。

核心 Contract 不把數值變成不可演進的架構常數；DDH MVP bootstrap defaults
由 Decision 0023 固定，專案可再以明確核准、版本化的 Evolution Profile
覆寫。Main Agent、Analyzer、Critic 或單次 Work Package 不得因 queue 壓力自行
延長保留、提高模型預算或改變 priority semantics。

Evolution budget 與 current development Work Package budget 分離，不能消耗
目前施工所需 token／compute 來清理歷史 backlog。

### 4.1 DDH MVP Bootstrap Defaults

自進化輸入分為：

```text
Individual Attempt Ledger
→ mechanically aggregated Learning Candidate
→ validated Long-term Orchestration Memory
```

- Individual Ledger serialized hard cap 為 64 KiB。
- Routine／known-no-change／one-off product failure 在 prefilter disposition 後
  立即刪除。
- 成功 atomic fold into Learning Candidate 後立即可刪除 source Ledger，最遲
  24 小時。
- 尚未完成 fold／prefilter 的 outage upper bound 為 P3 24 小時、P2 72 小時、
  P1 7 天、P0 14 天。
- Learning Candidate maximum age 為 P3 7 天、P2 14 天、P1 30 天、P0 90 天。
- P0 單次即在安全終止目前 mutation transaction 後排程；P1 兩次或一小時；
  P2 跨至少兩個 Work Packages 且三次或每日 idle batch；P3 五次才取得專用
  model analysis。
- Restart 可非阻塞 catch-up；model analysis 不得逐 Ledger 呼叫。

Learning Candidate 保存 normalized aggregate facts，不得保存 raw Ledger 的
壓縮副本。完整語義、刪除邊界與驗收見 Decision 0023。

## 5. Backlog Pressure Order

資源接近門檻時依序：

1. 刪除已經 prefilter consumed 的 routine Ledgers。
2. 刪除 raw logs、duplicate tracebacks、per-sample metrics 與可重建 artifacts。
3. 依 scope／risk／profile／fingerprint／outcome 將相似 pending Ledgers 聚合成
   短期 candidate batch。
4. 優先分析 P0、P1。
5. 延後 P2、P3。
6. 達到 maximum age／storage／item／token policy 時產生明確 expiration
   disposition。

Candidate batch 仍是短期資料，不是 accepted long-term memory，也不是永久
compact Ledger shadow。

聚合不得合併：

- 不同 scope／risk boundary；
- 不同 Agent／Context／template applicability；
- safe 與 unsafe recovery；
- success 與 failure pattern；
- current 與 superseded candidate；
- 不同 failure classification 但文字相似的 Ledgers。

## 6. Analyzer Outage

Analyzer／Critic 長期不可用時：

```text
repeated failures
→ circuit breaker
→ stop per-Ledger model retries
→ retain bounded prioritized backlog
→ periodic mechanical health probe
→ service restored
→ drain P0／P1 first
```

- Circuit breaker 與 probes 不需要 Agent。
- Duplicate failure 不得為每份 Ledger 重複呼叫模型。
- Backlog 不注入新施工 Agent Context。
- Analyzer unavailable 不撤銷 completion，也不建立人工 Checkpoint。
- Ingestion、prefilter 與 cleanup 必須可以在沒有 LLM service 時運作。

## 7. Expiration

當 profile 的最長等待或資源政策耗盡，允許終局：

```text
analysis_expired_without_memory_change
```

適用條件包括：

- Analyzer／Critic 在允許期間始終不可用。
- Model analysis token budget 長期不足。
- Candidate 一直未達最低重複／證據門檻。
- Candidate 被新版本記憶、profile 或更完整 candidate supersede。
- Ledger／candidate 損毀且無法安全重建。

此 disposition 表示：

- 未建立或修改長期記憶。
- 不宣稱 Analyzer／Critic 已接受或拒絕。
- 原始 Ledger、candidate batch 與短期 artifacts 可以刪除。
- 原 execution completion 不受影響。
- 不建立永久 failure receipt。

P0／P1 可以取得較長 retention 與更多 approved retry routes，但仍不得永久保存。
最終 TTL 到達後同樣刪除，只能留下不含 Ledger 內容的 bounded operational
health metric。

## 8. Safe Discard Order

最先可丟棄：

- routine success without orchestration signal；
- one-off product／test implementation failure；
- 已被有效 long-term memory 完整涵蓋且無新衝突的 known pattern；
- duplicate raw outputs／artifacts；
- superseded low-confidence candidate；
- 超過 profile 期限且未達 evidence threshold 的 P3／P2 candidate。

最後處理但仍有最終期限：

- boundary／unsafe recovery signal；
- repeated no-progress／resource waste；
- promoted memory 可能造成 regression 的證據；
- 高信心且跨多個 Work Packages 重複的 orchestration defect。

刪除順序不能由 Agent 即席決定，也不能以資料量為由優先刪除最嚴重訊號。

## 9. 業務場景

Analyzer 因外部服務故障離線三天，期間產生 10,000 份 Ledgers：

- 8,000 份首次成功或一般產品 bug 經 prefilter consumed／deleted。
- 1,500 份符合既有模式，只形成 bounded mechanical support observation。
- 400 份聚合為 20 組 P2 candidate batches。
- 90 份反覆 Context／handoff 浪費列為 P1。
- 10 份涉及 boundary／unsafe recovery 列為 P0。

Analyzer 恢復後先處理 P0／P1，再依剩餘 Evolution token budget 處理 P2。
所有 Work Packages 在此期間正常完成。

若部分 P2 candidates 超過 profile 最大等待，標記
`analysis_expired_without_memory_change` 後刪除；不留下永久 Ledger。

## 10. Stress Contract

- Analyzer／Critic 長時間完全離線。
- 每分鐘大量 Ledgers terminal。
- 大量相同 fingerprints 不重複保存或重複呼叫模型。
- P3 flood 不餓死 P0／P1。
- Queue、storage、item 與 model token budgets 同時達上限。
- Circuit breaker 不形成 retry storm。
- Restart／clock drift 不使 TTL 無限延長或提早錯刪。
- Candidate aggregation 保留 scope、risk、profile、outcome 與 unsafe distinctions。
- Superseded candidate 可提早完成 disposition。
- Corrupt／secret-bearing Ledger 不進入一般 Analyzer。
- Expiration 不影響 completion、candidate、source 或 pytest Evidence Retention。
- Prefilter、priority、expiration 與 cleanup 的 Agent token cost 為零。

## 11. 對應機械測試

```text
test_every_sealed_ledger_runs_zero_agent_prefilter
test_routine_and_one_off_product_failures_do_not_start_model_analysis
test_priority_changes_analysis_order_not_product_authority
test_evolution_budget_is_separate_from_current_work_package_budget
test_backlog_pressure_deletes_raw_and_duplicate_data_first
test_candidate_batching_preserves_scope_risk_profile_and_outcome_distinctions
test_analyzer_outage_trips_circuit_breaker_without_completion_backpressure
test_p3_flood_cannot_starve_p0_or_p1
test_expiration_reports_no_memory_change_without_fake_critic_decision
test_p0_and_p1_receive_priority_but_never_become_permanent_ledgers
test_restart_and_clock_drift_preserve_bounded_ttl
test_expired_ledger_deletion_never_removes_tests_source_or_user_diff
test_large_pending_backlog_is_bounded_deterministic_and_zero_agent
test_individual_ledger_hard_cap_preserves_required_aggregate_facts
test_atomic_candidate_fold_allows_source_ledger_deletion_within_24_hours
test_bootstrap_priority_triggers_do_not_call_model_per_ledger
test_candidate_and_source_ledger_have_independent_retention_clocks
test_restart_catch_up_is_non_blocking_and_idempotent
```

## 12. Self-Evolution Boundary

OLE 可以改善 prefilter implementation、batching、compression、queue placement、
retry scheduling 與 health probes，但不能自行修改：

- priority semantics；
- profile authority；
- maximum-resource categories；
- current Work Package budget isolation；
- expiration meaning；
- no-permanent-Ledger requirement；
- completion independence；
- specification、scope、acceptance 或 external high-risk boundaries。
