# Terminal Completion to Attempt Ledger Handoff Contract

**Contract ID：** `DOM-OLE-001`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 terminal execution 與短期編排學習資料的交接語義；
不授權 runtime、queue、schema 或 storage implementation  

---

## 1. 第一原則

Work Package／integration／Domain execution run 進入 terminal 後，terminal
result 必須立即供目前流程消費。Attempt Ledger 的 seal、enqueue、Analyzer、
Critic 或長期記憶更新不得阻擋、撤銷或延遲該 terminal result。

```text
execution terminal
    ├─ publish terminal result → current caller／higher-layer flow continues
    └─ seal Ledger → asynchronous OLE handoff
```

OLE 是非權威的編排改善流程。遺失一次 learning input 可以降低未來改善效果，
但不能改變已由 task specification、candidate、verification 與 completion closure
證明的結果。

## 2. Ledger 單位

一份 Attempt Ledger 對應一個實際產生 attempts 的 execution run：

- 一般 Work Package execution run 有自己的 Ledger。
- Subsystem integration、Domain acceptance 或其他 higher-layer evaluation
  若包含獨立施工、診斷、repair 或 retry，也有自己的 Ledger。
- 只消費 child completion、沒有新 attempt 的純狀態轉移不重複建立 Ledger。
- 新 candidate／repair 若仍屬同一 active execution run，繼續使用目前 Ledger。
- Terminal 後再次施工必須建立新 execution run／generation／Ledger，不重開舊
  Ledger。

實際 runtime 是否共用 storage、table 或 queue 尚未決定；不得因實作共用而混合
不同 execution identities。

## 3. Seal Trigger

當 current execution run 不再接受新的合法 attempt 時，立即 seal Ledger。
Terminal 語義至少涵蓋：

- `completed`
- `blocked`
- `budget_exhausted`
- `escalation_required`
- `cancelled`
- `superseded`

確切 enum 名稱可由後續 schema 調整，但不得漏掉非成功 terminal outcomes。
同一 run 內的 automatic retry、repair、repartition、runner recovery 或 candidate
重建尚未 terminal 時，Ledger 保持 active。

Seal 必須：

1. Fence 該 Ledger generation，不再接受 Attempt Row。
2. 固定 bounded Work Package／run summary、partition summaries 與 attempt rows。
3. 固定 terminal outcome、remaining budget 與 unresolved orchestration signals。
4. 產生 immutable handoff identity／digest 或等價 integrity binding。
5. 建立 transient pending learning handoff。

## 4. Ledger Content Boundary

Sealed Ledger 只包含有界、結構化編排特徵：

- execution run、task specification、scope level 與 risk identity。
- Agent／profile／template、partition、phase 與 generation。
- attempt sequence 與 token／tool／verification／time cost。
- failure classification、normalized fingerprint 與 no-progress signals。
- selected recovery／repartition／serialization／fallback routes。
- 新增證據的 bounded summary／digest。
- terminal outcome。
- Context Envelope／prompt template version references。
- 必要的 bounded diagnostic artifact references。

不得包含：

- 完整 prompt、對話或原始 Agent chain of thought。
- 無界 stdout／stderr、重複 traceback 或完整 metrics stream。
- 完整 source diff 或使用者工作區副本。
- credentials、personal data 或未遮罩 secrets。
- 沒有 observed facts 支持的 Agent 心得。
- 可由 canonical current state 便宜重建的大型副本。

Ledger 不是 acceptance evidence、completion authority、System Map authoring input
或永久 audit record。

## 5. Terminal Publication and Pending Handoff

正常路徑必須在同一 terminal generation 建立：

```text
terminal decision
＋ ledger write fence
＋ pending learning handoff
```

這是語義上的一致性邊界，不預先指定 database transaction、outbox、journal、
queue 或 message bus。

- Completion consumer 只等待 terminal decision 的 canonical publication。
- OLE enqueue 在此之後非同步執行。
- Pending handoff 是可刪除的短期 recovery material，不是永久 receipt。
- Enqueue 成功並被 ingestion boundary 接受後，可以刪除 pending handoff。

若 Ledger seal／pending handoff storage 本身不可用：

```text
terminal result remains valid
＋ learning_input_unavailable
```

系統依 profile 執行有界 mechanical retry／fallback；耗盡後可以放棄這次 learning
input，不能要求人類修復 OLE 才完成產品工作。

## 6. Enqueue, Idempotency and Recovery

- Enqueue 以 handoff／Ledger identity 冪等。
- Duplicate delivery 不建立重複 analysis candidate 或支持計數。
- Out-of-order delivery 依 execution／generation identity reconciliation。
- Terminal publication 後 crash 時，重啟由 transient pending handoff 重播。
- Analyzer／Critic unavailable 不影響 ingestion acceptance 或 terminal flow。
- Queue／backlog 滿載時依 Evolution Profile 的 bounded policy 延後、壓縮或
  最終放棄 learning input；不能反壓完成流程。
- Ingestion 只能接收 sealed Ledger；active／partial／identity-mismatched Ledger
  必須拒絕或保持 pending。

## 7. Late Attempt and Post-terminal Invalidation

Ledger seal 後收到 late attempt：

- 不得重新開啟舊 Ledger。
- 不得追加 Attempt Row 或修改已 sealed content。
- 依 partition／generation 判定為 stale。
- 未落地 mutation 直接拒絕或短期 quarantine。
- 已落地 mutation 依 CIM invalidates candidate／subject／completion，建立新的
  execution run 處理。

若 terminal completion 在 Ledger 尚 pending 時被後續 canonical invalidation
取代，可以在 Ledger lifecycle metadata 標記 `superseded／invalidated`
projection；不能改寫原 attempt facts。後續 repair 使用新 Ledger。確切 metadata
表示法尚未固定。

## 8. 業務場景

### 8.1 OLE 離線但 Work Package 正常完成

Workspace Work Package 經歷：

1. pytest 因 runner workspace 權限失敗。
2. MVE 自動重建 runner。
3. 第二次驗證發現產品計算錯誤。
4. Agent 修復後第三次驗證完整通過。
5. `DDH-COMP-001` 發布 Work Package completed。

OLE 此時離線：

- Caller 立即取得 completed result。
- Ledger 被 write-fenced、sealed 並形成 pending handoff。
- OLE 恢復後自動 ingestion，無重複分析。
- Analyzer 可以比較 runner recovery 與初始 environment selection 成本。
- 沒有人類 Checkpoint，也不撤銷 completed。

### 8.2 Terminal 後 Agent 遲到

舊 Test Agent 在 Ledger seal 後送回另一筆結果。結果 identity 屬於 stale
generation，不能寫入 Ledger 或 candidate。若只是 late message，安全丟棄；
若 mutation 已落地，CIM invalidates current artifacts 並建立新 run。

### 8.3 Learning storage 故障

Work Package completion 已成立，但 Ledger storage 無法建立 sealed artifact。
系統執行有界 fallback 後發布 `learning_input_unavailable`，清理可安全刪除的
短期資料並繼續。產品結果不被降級，且不虛構 Ledger 已成功分析。

## 9. Stress Contract

- 數千 execution runs 同時 terminal 時，completion latency 不依賴 Analyzer
  throughput。
- Analyzer／Critic 長時間離線時，terminal flow 持續運作且 pending backlog 有界。
- Terminal publication 後立即 crash，重啟只重送一次語義上的 handoff。
- Duplicate、late、out-of-order enqueue 不產生重複分析或支持計數。
- Ledger seal 後大量 stale attempts 無法重開或污染 sealed generation。
- Completion 隨後 invalidated 時，舊 learning material 不被誤解為 current
  success pattern。
- 單一 Ledger attempts 過多時，以 bounded summaries／segments 保持可 seal；
  exact segmentation policy 由 Evolution Profile 決定。
- Sensitive output storm 不進入一般 Ledger 或 Analyzer。
- Queue full、storage pressure 或 ingestion crash 不阻擋 terminal result。
- Seal、integrity validation、enqueue、replay 與 deduplication 的 Agent token
  cost 為零。

## 10. 對應機械測試

```text
test_terminal_completion_does_not_wait_for_analyzer_or_critic
test_each_attempting_execution_run_has_one_separate_ledger
test_retry_and_repair_stay_in_active_ledger_until_terminal
test_all_terminal_outcome_families_seal_ledger
test_sealed_ledger_rejects_late_attempt_rows
test_terminal_and_pending_handoff_share_same_generation_identity
test_crash_after_terminal_replays_pending_handoff_idempotently
test_duplicate_enqueue_does_not_duplicate_analysis_or_support_count
test_analyzer_outage_does_not_block_completion
test_queue_pressure_is_bounded_without_completion_backpressure
test_learning_storage_failure_reports_unavailable_without_invalidating_product
test_landed_post_terminal_mutation_invalidates_artifacts_and_uses_new_ledger
test_ledger_never_contains_full_prompt_log_diff_or_secret
test_mass_terminal_handoff_is_bounded_deterministic_and_zero_agent
```

## 11. Retention and Evolution Boundary

本 Contract 只固定 terminal、seal 與 ingestion handoff。Ledger 何時 prefilter、
進入 model analysis、等待多久、如何處理長期 pending、何時 consumed／deleted，
由`OW-F18.3`、`OLE-PROFILE-001`與Decision 0023負責。

OLE 可以改善 enqueue batching、compression、queue selection、retry scheduling、
backlog priority 與 transient storage，但不能修改：

- terminal completion independence；
- Ledger write fence；
- identity／integrity binding；
- idempotent ingestion；
- non-authoritative learning boundary；
- no-secret／bounded content；
- external high-risk or specification authority。
