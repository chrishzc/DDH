# DDH Invalidation and Reconciliation Domain Contract

**Contract ID：** DDH-INV-001  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存已確認的跨 Subsystem invalidation 與 reconciliation；不授權 runtime 實作  

---

## 1. 目的

執行期間規格、產品 source、pytest、fixture、helper、configuration、contract、schema、Quality Profile、runner 或 toolchain 改變時，DDH 必須讓 PWC、Context Broker、CIM、TAQG 與 MVE 自動知道哪些 local state 需要重算、失效或建立新 generation。

Invalidation event 只提供快速增量通知，不是 authority。Protected lifecycle transition 前的 reconciliation 必須重新比對目前 canonical inputs，確保事件重複、遺失、亂序或 Bus 故障都不能讓錯誤 identity 通過。

## 2. 定位

- 本 Contract 是 Execution and Orchestration Domain 的共用機械服務，不先建立第七個 Subsystem。
- 不建立全專案、跨版本的中央 freshness authority。
- 不建立永久 Invalidation Ledger、event sourcing history 或人工 Checkpoint。
- 各 Subsystem 只改變自己擁有的 derived state。
- 規格、source、test assets、candidate 與 profile 的既有 authority 不因事件而改變。

## 3. 執行模型：局部狀態機與 Reconciliation Barrier

DDH-INV-001 使用狀態機，但不是一部中央大狀態機：

```text
canonical change
→ invalidation event
→ each consumer advances its local state machine
→ protected transition reconciliation
→ continue／automatic rebuild／new generation
```

共用 reconciliation state 可以表示為：

```text
clean(generation N)
→ invalidated(generation N+1)
→ reconciling
→ reconciled

reconciling
→ rebuild_required
→ rebuilding
→ reconciling
```

各 consumer 仍保有自己的狀態機，例如：

```text
Context: fresh → stale → rematerialized
CIM: mutable_generation → invalidated → new_generation → frozen
TAQG: active → rerun_required／suspect／stale → readmitted／active
MVE: subject_ready／running → invalidated → new_subject_required
```

Event transport 不負責決定業務 transition；versioned consumer rules 與 reconciliation 才負責。

## 4. Event Producers

| Change | Producer |
|---|---|
| Product／test／fixture／configuration write | PWC／CIM mutation observer |
| Test dependency closure change | TAQG Discovery Adapter |
| Task Specification version change | Task Specification lifecycle owner |
| Quality Profile change | TAQG profile lifecycle |
| Runner／toolchain change | MVE environment manager |
| System Map 發現新影響關係 | Query consumer 發出 `impact_reassessment_required` |

System Map event 只表示需要重新檢查 impact closure，不能自行宣告 test stale、授予 write scope 或改變 acceptance。

## 5. 最小事件模型

```text
event_id
＋ work_package_id
＋ generation
＋ change_kind
＋ changed_resource_reference
＋ before_identity
＋ after_identity
＋ scope_hint
＋ producer
＋ required_consumers
```

- Event 不包含完整 source、diff、log、prompt 或對話。
- Caller-supplied Agent identity 不能偽造 producer、generation 或 acknowledgement。
- 同一 resource 的高頻 change 可以 coalesce 至最新 identity，但不同 change kinds 不能互相覆蓋。

## 6. Consumer Routing

| Consumer | Required reaction |
|---|---|
| PWC | 標記 partition dirty、檢查 write conflict 或撤銷 stale generation |
| Context Broker | 將已 materialize 的相關 Context 標成 stale，按需重新載入 |
| CIM | 拒絕舊 generation patch／result，必要時建立新 candidate generation |
| TAQG | 依 `TAQG-QUAL-003` 判定 rerun／suspect／stale／re-admit |
| MVE | 使 identity 不再匹配的 Verification Subject 失效並等待新 subject |

一般已核准 partition 施工不因 queue 暫時故障而全面停止；只有會發布共享或完成狀態的 protected transition 必須等待 reconciliation。

## 7. Delivery and Ordering

- Delivery 採 at-least-once；consumer 必須 idempotent。
- 只要求同一 Work Package／resource generation 的局部順序，不建立全域 total ordering。
- Duplicate event 不得重複建立 candidate、manifest 或 Verification Subject。
- Old generation event 不得覆寫 new generation state。
- Raw event delivery 可以批次與 coalesce，但不能漏掉 spec、test、fixture、contract、schema、profile 或 toolchain change kind。

## 8. Protected Reconciliation Transitions

下列 transition 前必須重新比對 current canonical state：

```text
Partition activation
Candidate Freeze
Test Asset Manifest publication
Verification Subject creation
```

流程：

```text
incremental event routing
→ consumer local update
→ protected transition reads current identities
→ compare generation／digest／version／epoch
→ exact match: continue
→ mismatch: automatic rebuild or new generation
```

Event acknowledgement、index 或 cache 不能替代 reconciliation。

## 9. Failure and Automatic Recovery

```text
delivery failure
→ bounded retry
→ rebuild consumer state from current identities
→ rerun reconciliation
→ continue
```

- Queue 遺失、損壞或版本不相容時，從 mutation inventory、spec version、candidate digest、Test Asset Inventory 與 environment profile 重建。
- Agent 不需要理解 queue／cache 格式，也不詢問人類如何修復 Harness。
- Safe recovery routes 耗盡時，輸出結構化 `platform_blocked`；不能把 infrastructure failure 當成產品 failure。
- 只有 canonical specification 矛盾、expected behavior 改變或 quality policy 缺口才需要人類決策。

## 10. Retention

只暫時保存：

```text
current_work_package_generation
＋ consumer_watermarks
＋ unacknowledged_events
＋ reconciliation_status
```

- 全部 required consumers 處理完成後，raw events 可以刪除。
- Work Package 結束後不保留完整 Invalidation event history。
- Watermark 與 status 是可重建的執行狀態，不是 Evidence Retention、SSOT 或永久 receipt。

## 11. 業務場景

### DDH-INV-S01：產品 source 修改

- Implementation Agent 修改跨平台路徑 canonicalization。
- PWC 發出 `product_source_changed`；CIM 增加 candidate generation。
- Context Broker 只使相關 excerpts stale。
- TAQG 將相關 active tests 標成 `rerun_required`，不把 pytest semantics 誤標為 stale。
- 舊 MVE subject 失效；Agent 在既有 scope 內繼續施工，不詢問人類。

### DDH-INV-S02：施工期間規格改變

- Task Specification expected behavior 改變。
- 現有 Work Package 仍綁定舊版本，不被 event 靜默改寫。
- 系統建立結構化規格更新提案。
- 因 acceptance semantics 改變，等待人類核准新版本；一般工具 recovery 不能越過這條邊界。

### DDH-INV-S03：Fixture change event 遺失

- Test Agent 修改共享 fixture，但 TAQG 沒收到 event。
- Manifest publication 前 reconciliation 發現 fixture digest closure 不一致。
- 自動重建 Test Asset Inventory，重新執行 disposition／admission。
- 舊 manifest 無法進入 MVE。

### DDH-INV-S04：Candidate Freeze 後遲到 Writer

- Freeze fence 阻擋舊 generation 的遲到 product write。
- CIM 建立新 candidate generation。
- 舊 TAQG／MVE result 不能套用到新 generation。
- 流程自動回到 quiescence／freeze，不建立人工 Checkpoint。

## 12. Stress Contract

- 數萬個短時間 change events 必須有界 coalesce，memory／disk 不無界成長。
- 多 partitions 亂序完成時，舊 generation 不得覆蓋新 generation。
- Consumer crash／restart 後可以由目前 canonical state reconciliation。
- Duplicate delivery 不重複建立同 identity artifacts。
- Event payload 與完整 inventory 不進入 Agent Context。
- Routine delivery、reconciliation、rebuild 與 known recovery 的 Agent token cost 為零。

## 13. 對應機械測試

```text
test_invalidation_event_is_not_acceptance_or_authorization
test_consumers_only_mutate_their_owned_local_state
test_duplicate_delivery_is_idempotent
test_old_generation_event_cannot_override_new_generation
test_different_change_kinds_are_not_lost_during_coalescing
test_candidate_freeze_reconciles_current_mutation_identity
test_manifest_publication_detects_missed_fixture_event
test_subject_creation_rejects_missed_or_stale_identity
test_bus_failure_rebuilds_from_canonical_state_without_human_checkpoint
test_product_source_change_requires_rerun_without_staling_test_semantics
test_specification_change_creates_update_proposal_without_rewriting_pinned_work
test_raw_events_are_deleted_after_required_consumers_reconcile
test_large_event_storm_has_bounded_storage_and_zero_agent_token_cost
```

## 14. Self-Evolution Boundary

OLE 可以改善 event batching、coalescing implementation、retry scheduling、cache、reconciliation ordering 與 failure summaries，但不能修改：

- Change kind semantics。
- Required consumers。
- Protected transition list。
- Identity comparison／invalidation rules。
- Fail-closed conditions。
- Specification、quality policy 或 human decision boundary。
