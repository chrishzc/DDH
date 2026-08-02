# DDH Execution and Orchestration Domain Overview

**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存已確認的 Domain 拆分與跨 Subsystem 關係；尚未授權 runtime 實作  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

> Naming decision：Decision 0003 已採用角色導向名稱。後續優先使用
> `Work Coordinator`、`Change Guard`、`Context Curator`、`Test Auditor`、
> `Verification Runner`、`Completion Judge` 與 `Learning Steward`。本文既有
> PWC／CIM／TAQG／MVE／OLE 名稱與 ID 保留為歷史 Contract 引用。
>
> Runtime／verification amendment：Decision 0013 已採
> language-neutral Contracts＋單一模組化Python reference runtime，長期選擇性
> 演進高保證Rust／Go backends。正式治理對象是tool-neutral Verification Assets；
> pytest只是Python reference adapter，CI/CD pipeline名稱不授予deployment或其他
> external authority。
>
> External high-risk產品化依Decision 0024：MVP只需可執行Contract fixtures與
> deterministic simulator；真實provider Adapter在核心MVP通過後逐個核准，
> 且不得以generic shell／HTTP工具繞過Trusted Executor capability。
>
> Runtime baseline amendment：Decision 0014 已採Python 3.13作為DDH Reference
> Runtime最低版本，required CI驗證最低版本與最新穩定版；目標專案runtime保持
> 獨立，不因DDH自身版本而被迫升級。
>
> Native backend evolution amendment：Decision 0015 已採evidence-gated
> evolution；只有可重現、可量測且無法合理修正的backend能力缺口，經人類核准
> architecture change後，才能建立以新Task Specification為SSOT的Rust／Go施工。
> Default promotion與Python backend retirement另行決策。
>
> Cross-language Contract amendment：Decision 0016 已採UTF-8 JSON＋JSON
> Schema Draft 2020-12的versioned Contract Envelope；初始backend transport
> 使用isolated invocation directory與atomic result file。Wire message是短期
> runtime projection，不取代Task Specification、semantic specification或可信
> execution channel identity。
>
> Shared identity amendment：Decision 0017 已採四種minimal typed references：
> Versioned Authority、Lifecycle、Content與Invocation。每個atomic handoff只
> 攜帶防止stale／wrong-subject absorption所需欄位，不建立永久cross-version
> identity、freshness或provenance chain；System Map identity只作index reference。
>
> Mutation mediation amendment：Decision 0018 已採`Serial Reconciled`、
> `Guarded Shared`與`Isolated Candidate`三種local Change Guard modes。L1
> single-writer可用post-delta admission；L2 parallel／shared mutation使用
> verified containment或isolated Patch Admission。Git hook不是authority，
> 第一版不建立central Patch Service。
>
> System Map consumer amendment：Decision 0019 已採capability-based Consumer
> Port；DDH只固定node resolution、hierarchy、direct adjacency／reverse
> adjacency、resource binding、local currentness與exact branch／commit view
> binding，不固定System Map schema或backend。Candidate delta使用baseline
> Map＋bounded live overlay，query必須被下游artifact實際消費。
>
> Quality defaults amendment：Decision 0020 已採`Static／Module／Subsystem／
> Domain／Global` verification scope layer＋independent quality add-ons＋
> specification-sourced product thresholds。V0～V3只保留歷史alias，scope layer
> 不自動要求所有high-cost checks，且unchanged admitted assets重用admission。
>
> Budget amendment：Decision 0021 已將Agent、Context、wall time、Verification、
> Recovery與Stress budgets分離。Context使用relative bootstrap；Recovery依
> progress而非固定Agent attempt數；unknown-duration一般verification使用
> 10-minute bootstrap hard deadline，沒有stdout不等於no-progress。Budget不得
> 改變required acceptance。
>
> Platform amendment：Decision 0022 已採vendor-supported Windows 11 x86_64
> 與Ubuntu 24.04 LTS x86_64作MVP release-blocking matrix，並驗證Python 3.13
> 與latest stable。macOS、ARM64、WSL2與其他Linux先列preview；network-share
> writable candidate不列MVP正式支援。

---

## 1. Domain 目標

DDH Execution and Orchestration Domain 依任務規格安排單一或平行 Agent 施工，控制 Context 與 candidate 變更，使用無 Agent 機械測試證明需求，並從短期 Attempt Ledger 改善未來編排。

任務規格是本次完成判定 SSOT。System Map 只是真實架構 index，用於 discovery、dependency 與 scope 規劃，不提供授權。

### 1.1 已確認原則：Mechanical Safety 不得破壞 Automation Continuity

機械阻擋的目的，是防止無法安全吸收的 mutation 或錯誤完成判定，不是把日常工具問題轉成人工 Checkpoint。有效的 Harness 必須同時滿足：

- **Safety：** 不靜默越界、不修改規格、不降低驗收、不跨越未授權外部副作用。
- **Continuity：** 一般工具失敗、暫時性環境問題、stale generation、writer draining、candidate rematerialization 與可重試的機械錯誤，由編排流程自動診斷、選擇安全復原路徑並繼續。
- **Actionability：** 每個 mechanical block 都必須回傳穩定 reason code、目前 state／identity、retryability、已嘗試策略與允許的 machine actions；不得只給模糊錯誤文字，要求 Agent 或人類重新研究 Harness 如何操作。
- **Bounded recovery：** 相同 failure fingerprint 不得無限重試或反覆消耗 Agent token；常見復原策略應由無 Agent 的機械流程選擇與執行。
- **No routine human query：** Recovery 不改變架構、規格、scope、風險政策、公開契約或外部副作用時，不得要求人工逐步核准。

`recovery_required` 在本 Domain 中首先表示「進入自動復原狀態」，不是「立即詢問人類」。只有所有已規定的安全復原策略耗盡，且繼續需要改變上述人類決策邊界時，才形成結構化 exception report。

需要誠實保留的底線：若 Harness 自己存在無安全 fallback 的缺陷，系統不能用繞過機械邊界來假裝流程暢通。此時應輸出一次可重現的 platform-blocked report，而不是展開多輪人工互動式除錯。

#### 已確認 Contract：Automation Continuity Response

每個可阻擋流程的 Subsystem 回應至少包含：

```text
reason_code
＋ subject_identity
＋ current_state
＋ retryability
＋ safe_machine_actions
＋ attempted_action_fingerprints
＋ remaining_recovery_budget
＋ escalation_boundary_if_exhausted
```

預設自動策略依實際狀態選用：

1. 等待／drain 已核准 operation。
2. 以相同 identity 執行有界、冪等 retry。
3. 重建 Context、boundary、candidate 或 test runner 的可重建資產。
4. 撤回 stale generation，保存 delta 後建立新 generation。
5. 從 guarded shared mode 切換到 isolated candidate，或從平行改為序列施工。
6. 重跑 Harness self-check 與受影響的機械驗證。
7. 若沒有安全路徑，停止 mutation 並產生單一結構化 exception；不得自行放寬規格或安全條件。

產品業務 pytest 可以發現 candidate 的功能錯誤，但不能單獨證明 Harness 不會 deadlock、錯誤阻擋或產生不可操作訊息。因此 Harness 本身還需要 orchestration continuity、fault injection 與 recovery stress tests。

對應業務場景與機械測試至少包括：

```text
test_mechanical_block_returns_machine_actionable_recovery_response
test_recoverable_tool_failure_continues_without_human_checkpoint
test_same_failure_fingerprint_does_not_loop_or_consume_unbounded_tokens
test_orchestrator_switches_to_safe_isolated_or_serial_mode_when_supported
test_harness_failure_never_silently_disables_safety_boundary
test_exhausted_recovery_emits_one_reproducible_platform_blocked_report
test_product_business_tests_and_harness_continuity_tests_remain_separate
```

#### 已確認目標：Deterministic Recovery Routing

任何已知且可安全復原的 mechanical failure，都必須在 recovery policy 中對應下一個 machine action。Agent 可以閱讀結果做產品診斷，但日常 recovery path 的選擇與執行不依賴 Agent 推理，也不等待人類回答。

```text
mechanical outcome
→ stable reason classification
→ ordered safe recovery actions
→ execute next action
→ re-check invariant
→ continue original flow
```

`recovery_required` 是暫態 routing state，不是 terminal state。只有 `human_change_decision_required`、`external_high_risk_handoff` 與所有安全路徑耗盡後的 `platform_blocked` 可以停止一般自動流程。

建議 outcome family 與預設 routing：

| Outcome family | 預設機械下一步 |
|---|---|
| `transient_retryable` | 依 profile 執行 bounded idempotent retry |
| `stale_identity` | 撤回 stale generation，刷新 identity／Context 後重建 |
| `rebuildable_artifact_failure` | 重建 Context、manifest、boundary、candidate 或 runner artifact |
| `writer_not_quiescent` | Fence、drain、reconcile；必要時保存 delta 後建立新 generation |
| `shared_mode_conflict` | 切換 isolated candidate；若平行收益消失則改序列施工 |
| `runner_environment_failure` | 重建乾淨 runner environment，重跑 environment self-check |
| `component_unhealthy` | Circuit-break 故障元件並切換已驗證的等價 backend／安全模式 |
| `product_verification_failure` | 交回 Agent 在原規格 scope 內修正 candidate，再建立新 subject 重測 |
| `specification_or_scope_change_required` | `human_change_decision_required` |
| `unknown_external_side_effect` | `external_high_risk_handoff` |
| `safe_routes_exhausted` | 單次 `platform_blocked` report |

為避免「工具卡住但沒有回傳失敗」，每個 blocking operation 還必須有：

- progress／heartbeat 或可觀察的 lifecycle。
- 依 operation profile 設定的 bounded stall detection，不使用全域固定 timeout。
- idempotency／deduplication key，避免 retry 重複套用 mutation。
- circuit breaker，避免持續呼叫已知故障 component。
- 經測試的 fallback compatibility；不存在等價 fallback 時不能臨時假裝相容。

DDH 的可驗收目標不是宣稱所有軟體永遠不會有 bug，而是：

> 單一工具故障、暫時環境失敗或已知 recovery case 不會阻礙 Agent 繼續開發；只有需要改變人類決策邊界或所有安全冗餘路徑同時失效時才停止。

### 1.2 已確認原則：System Map Query 必須綁定流程觸發點

System Map 是長期維護的真實架構 index，用來快速定位 node、正反向依賴、跨層關係與候選 impact closure；它不是任務規格、scope authority、驗收 authority 或 mutation permission。

只在 prompt 中告訴 Agent「可以查 System Map」不足以保證使用。DDH 必須在需要架構理解的 lifecycle transition 機械觸發 query，並驗證 query result 實際進入 partitioning、Context、impact closure 或 suite selection 的輸入。

#### 已確認 Contract：SMQ-001 Architecture Impact Query

| Lifecycle transition | Query 目的 | 最小查詢 |
|---|---|---|
| Task specification → initial scope plan | 將人類選定範圍定位到 Global／Domain／Subsystem／Module | selected node、ancestors、direct dependencies、direct reverse dependents |
| Scope plan → parallel partitioning | 找出共享依賴、共同下游與可能寫入重疊 | partitions 的 dependency／reverse-dependency intersection |
| Context Envelope materialization／expansion | 只載入 Agent 當下需要的架構鄰域 | target node summary，預設 one-hop；按證據有界擴張 |
| Agent 實際 touched resources 超出 predicted closure | 判斷是 Map drift、實作間接影響或真正 scope expansion | resource → node bindings，再查 affected reverse dependents |
| Product verification failure → repair impact closure | 找出失敗功能可能影響的原本未納入節點 | failed scenario mapped nodes、dependencies、reverse dependents、上層 Subsystem／Domain boundary |
| Frozen candidate → Verification Subject | 產生受影響 suite 候選與 regression closure | changed nodes、affected dependents、node → test asset bindings |
| 架構關係已核准改變 → System Map maintenance | 讓 index 反映實際架構，不讓後續查詢持續漂移 | changed nodes／edges／source bindings 的 refresh candidate |

**Query 深度與 Context 成本**

```text
Q0：單一 node identity／summary
Q1：one-hop dependencies＋reverse dependents
Q2：bounded impact closure，預設不越過選定 Subsystem／Domain 邊界
Q3：有跨邊界證據時才擴張，並標示需要 scope decision 的節點
```

- Agent 不直接讀取整份 System Map；Context Broker 先回傳有界摘要與 node IDs。
- 主 Agent 可以依失敗、實際 touched resources 或契約關係請求 Q2／Q3；子代理仍透過 Context Request 取得最小增量。
- Query artifact 是可重建的短期 derived artifact，不成為永久 Evidence Retention。
- Query service／index 故障時依 `RC-DOM-003` 自動重建；仍不可用時以 bounded live-source discovery 作安全 fallback，不能讓 index 工具 bug 阻礙 Agent。
- Live source 與 System Map 不一致時，以實際 source／schema／configuration 為現況證據，產生 Map drift；不能以 Map 內容壓過真實程式。
- DDH 只消費 published actual view；planned／proposed／declared-only overlay
  不得進入 scope、impact closure、Context 或 suite selection。
- Agent 可以在未來 System Map 規格允許時補充已觀測 node 的 semantic details，
  但不能藉由宣告建立 actual node，也不能覆蓋 source-observed facts。
- Currentness 採局部、與 evidence binding 相關的判定；確切欄位、狀態名稱、
  演算法與 reconciliation 流程由尚未完成的 System Map 規格決定。

**防止「有呼叫但沒使用」**

每個 mandatory query transition 必須同時滿足：

1. 產生帶 `query_purpose`、map／index version、seed nodes、traversal bounds 與 omission metadata 的結果。
2. 下游 artifact 明確引用該 `architecture_query_result_id`。
3. 下游決策記錄哪些 nodes／edges 被納入、排除或因何需要 live-source fallback。
4. Contract test 必須在 query 未呼叫、結果未消費、使用 stale result 或拿 query 當授權時失敗。

對應機械測試候選：

```text
test_initial_scope_planning_queries_selected_node_architecture_neighborhood
test_parallel_partitioning_consumes_dependency_intersection_query
test_failure_impact_closure_queries_reverse_dependents
test_verification_suite_selection_consumes_changed_node_impact_query
test_query_called_but_not_consumed_cannot_satisfy_transition_contract
test_system_map_query_never_grants_scope_or_acceptance_authority
test_declared_only_overlay_is_excluded_from_ddh_architecture_queries
test_agent_semantics_cannot_create_or_override_observed_architecture_facts
test_index_failure_rebuilds_or_falls_back_without_blocking_agent
test_locally_unusable_map_result_falls_back_only_for_affected_scope
test_live_source_drift_overrides_map_assumption_and_schedules_map_refresh
test_query_context_is_bounded_instead_of_loading_entire_map
```

**本 Contract 的設計邊界**

- 本 Contract 只決定 DDH 何時提出 query、最小 query purpose／depth、哪些下游 artifact 必須消費結果，以及失敗時如何 fallback。
- 本 Contract 不設計 System Map schema、Bundle／index 格式、query language、graph traversal engine、freshness algorithm、更新工具、儲存技術或視覺化 UI。
- DDH 透過外部提供的 versioned System Map query interface 使用 index；可用欄位與能力以該 System Map 規格為準，不在此推測。
- 若另一份 System Map 規格尚未提供某項 query capability，DDH 必須將其標記為 unavailable，使用 bounded live-source fallback；不得自行擴張或修改 System Map 設計。

#### 下一個待確認項目：Recovery Transition Table

仍需逐一固定每個 Subsystem 的：

- stable reason codes。
- allowed next actions 與順序。
- invariant re-check。
- retry／rebuild／mode-switch budget。
- terminal classification。
- 對應業務場景、fault injection 與 stress tests。

#### 已確認 Recovery Chain RC-PWC-CIM-001：Registered Writer Not Quiescent

**功能**

當 CIM 仍能識別 writer、partition、generation 與 boundary，但 writer 沒有在一般 drain 過程中結束時，系統必須依工具 profile 自動完成等待、stall 判定、安全終止或隔離重派，不向人類詢問工具該如何處理。

**業務例子**

Test Agent 宣告完成後，背景 formatter 仍在執行。它起初仍有 progress，因此 CIM 繼續 draining；之後 heartbeat 停止並達到該 formatter profile 的 stall 條件。若 profile 已宣告此程序可以安全終止，CIM 自動終止並核對已產生的 pytest delta。若不能安全終止或 termination 失敗，PWC 封存可辨識 delta、撤回舊 generation，改在 isolated candidate 建立新 generation，讓 Agent 繼續完成原任務。

**Deterministic transition**

```text
registered_writer_not_quiescent
→ fence_generation
→ observe_progress
   ├─ progress_present → continue_bounded_drain
   └─ stall_confirmed
      ├─ safe_termination_allowed → terminate → reconcile
      └─ termination_not_allowed_or_failed
         → quarantine_old_boundary
         → preserve_attributable_delta
         → materialize_isolated_candidate
         → issue_new_generation
         → resume_original_work
```

**Transition table**

| Current reason／state | Guard | Machine action | 成功後 | 失敗後 |
|---|---|---|---|---|
| `writer_active_with_progress` | heartbeat／progress 符合 operation profile | `continue_bounded_drain` | 回到 quiescence check | `writer_stalled` |
| `writer_stalled` | profile 明確允許安全終止 | `terminate_registered_writer` | `reconcile_actual_delta` | `termination_failed` |
| `writer_stalled` | profile 不允許終止 | 不嘗試 kill | `isolation_fallback_required` | 不適用 |
| `termination_failed` | boundary 仍可 quarantine | `quarantine_old_boundary` | `preserve_attributable_delta` | `mutation_closure_unknown` |
| `isolation_fallback_required` | 可從 last safe candidate 與可辨識 delta 物化 | `materialize_isolated_candidate` | `issue_new_generation` | `safe_materialization_unavailable` |
| `new_generation_ready` | identity、scope 與 baseline 重驗通過 | `resume_original_work` | 回到原 Work Package 流程 | 依新 reason code 路由 |
| `safe_materialization_unavailable` | 所有已驗證 fallback 均不可用 | `emit_platform_blocked_once` | terminal | 不再自動重試 |

**必要不變量**

- 只允許終止已綁定 trusted writer identity、partition generation 與 boundary instance 的程序；不得廣泛掃描或終止不明程序。
- Stall threshold 由 operation profile 決定；有 progress 的長任務不得被固定全域 timeout 誤殺。
- Termination、quarantine、isolation fallback 都不得 reset、stash、刪除或覆寫使用者既有差異。
- 新 generation 必須從可證明的 candidate／delta 組合建立，不能接管仍可能寫入的舊環境。
- 所有自動路徑都維持原 task specification、scope 與 acceptance，不得為了恢復而降低要求。
- `platform_blocked` 只在安全終止、quarantine 與隔離物化均不可用時產生一次；不得變成反覆詢問人類的對話迴圈。

**對應業務測試**

```text
test_writer_with_progress_is_not_killed_by_global_timeout
test_stalled_writer_is_terminated_only_when_profile_allows
test_successful_termination_reconciles_delta_and_continues_freeze
test_termination_failure_switches_to_isolated_new_generation
test_isolation_fallback_preserves_user_baseline_and_agent_delta
test_recovered_generation_resumes_original_scope_without_human_checkpoint
test_exhausted_safe_routes_emit_one_platform_blocked_result
test_same_stalled_writer_fingerprint_does_not_loop_indefinitely
```

**後續 Stress Contract 候選**

- 大量 writers 同時 stall 時，recovery queue 不得造成 owner overlap 或重複 termination。
- 連續 termination failure／isolation fallback 下，不得遺失 delta、重複套用 mutation 或無界消耗 token。
- Heartbeat 高延遲或抖動時，不得把仍有實際 progress 的 writer 誤判為 stalled。

#### 已確認 Recovery Chain RC-PWC-CIM-002：Stale Generation Result

**功能**

舊 generation 在新 generation 已啟用後才回傳 patch、工具結果或 mutation request 時，系統必須先機械隔離 stale result，再讓目前 writer 繼續。Stale delta 可以作為暫時的重用候選，但不得自動覆蓋目前 candidate，也不需要詢問人類如何處理。

**業務例子**

Implementation Agent A 的 generation 1 失聯後，PWC 已建立 generation 2 交給 Agent B。A 隨後恢復並送回一份看似有效的 patch。CIM 依 partition identity 與 generation 判定它已 stale，拒絕直接 admission；若 patch 位於隔離區且內容可讀，系統把它封裝成 temporary `stale_delta_candidate` 提供給 B。B 可以在目前 scope 內參考或重新產生需要的修改，但舊 patch 不會自動寫入 generation 2。

**Deterministic transition**

```text
stale_identity_detected
→ classify_result_location
   ├─ mutation_blocked_before_write
   │  → record_bounded_attempt → continue_current_generation
   ├─ isolated_delta_available
   │  → quarantine_stale_delta
   │  → attach_as_reuse_candidate
   │  → continue_current_generation
   └─ mutation_already_landed
      → invalidate_candidate_and_subject
      → circuit_break_failed_boundary
      → reconcile_actual_snapshot
      → materialize_isolated_candidate
      → issue_fresh_generation
```

**Transition table**

| Current reason／state | Guard | Machine action | 成功後 | 失敗後 |
|---|---|---|---|---|
| `stale_mutation_blocked` | Boundary 已證明 mutation 未落地 | `continue_current_generation` | 原流程繼續 | 不適用 |
| `stale_isolated_delta_received` | Delta 可讀且未影響 current candidate | `quarantine_as_reuse_candidate` | 提供最小摘要給 current writer | `discard_unreadable_temporary_delta` |
| `stale_delta_reuse_requested` | Current writer 仍在相同授權 scope | 在 current generation 重新產生／明確採納 | 建立 current-generation delta | 依一般施工失敗路由 |
| `stale_mutation_landed` | 受保護 snapshot 已被改變 | `invalidate_candidate_and_subject` | `boundary_integrity_breach` | 不適用 |
| `boundary_integrity_breach` | 可從 last safe candidate 與 accepted deltas 重建 | `switch_to_isolated_candidate` | `issue_fresh_generation` | `safe_materialization_unavailable` |
| `safe_materialization_unavailable` | 所有安全重建路徑耗盡 | `emit_platform_blocked_once` | terminal | 不再自動重試 |

**必要不變量**

- Generation 比對必須在 mutation／patch admission 前機械執行，不能依 Agent 自報「這份 patch 還能用」。
- Stale delta 不得自動套用到 current candidate；是否重用由 current writer 在原授權 scope 內重新產生或明確採納。
- 被機械阻擋且未落地的 stale request 不應中斷 current generation。
- Stale mutation 若真的落地，代表 boundary integrity breach；既有 candidate 與 verification subject 必須失效。
- Quarantined stale delta 是短期 recovery artifact，完成重用判斷或 Work Package terminal 後依 retention policy 刪除，不成為永久 Evidence Retention。
- 整個 routing 不需要人工 Checkpoint；只有無法安全重建 candidate 時才形成單次 `platform_blocked`。

**對應業務測試**

```text
test_blocked_stale_mutation_does_not_interrupt_current_generation
test_isolated_stale_delta_is_quarantined_without_auto_admission
test_current_writer_can_reuse_stale_delta_only_under_current_generation
test_unreadable_stale_delta_does_not_block_current_work
test_landed_stale_mutation_invalidates_candidate_and_subject
test_boundary_breach_switches_to_isolated_fresh_generation
test_stale_delta_is_deleted_after_reuse_decision_or_terminal_state
test_repeated_stale_results_do_not_create_human_checkpoints_or_retry_loops
```

**後續 Stress Contract 候選**

- 大量 stale results 亂序到達時，current generation 必須保持唯一且單調。
- Stale result flood 不得讓 Context、temporary storage 或 Agent token 無界成長。
- Boundary breach 與新 generation 建立競態時，不得讓失效 candidate 被驗證或完成。

#### 已確認 Recovery Chain RC-DOM-003：Rebuildable Artifact Failure

**功能**

DDH 執行期間產生的衍生資產若遺失、損壞、格式版本過期或無法讀取，系統必須從仍有效的 authority／canonical state 自動重建並重驗 identity。Agent 不需要理解內部檔案格式，也不需要詢問人類如何修理 Harness artifact。

**可重建與不可捏造的邊界**

| 類型 | 例子 | 處理 |
|---|---|---|
| Rebuildable derived artifact | Context Envelope、candidate manifest、verification intake、suite selection、runner plan、temporary index | 從固定規格與實際 canonical state 重建 |
| Active safety component | mutation boundary／write guard instance | 不可只重寫 metadata 假裝恢復；先停止暴露 writes，再重新 provision 或切換隔離模式 |
| Authority／canonical source | task specification、實際 source snapshot、必要 test asset、已核准外部副作用決策 | 不得從 cache、System Map 或 Agent 猜測補造 |

**業務例子**

Candidate 已凍結，但 temporary candidate manifest 因程序 crash 只寫入一半。Frozen snapshot 本身仍完整且 immutable。CIM 從實際 snapshot 與固定 identity inputs 重建 manifest，得到相同 candidate identity 後自動繼續。若重建結果顯示 snapshot 已改變，則不是單純 manifest 故障，舊 candidate 與 verification subject 必須失效並重新 freeze。

**Deterministic transition**

```text
artifact_failure_detected
→ classify_artifact_role
   ├─ rebuildable_derived
   │  → load_canonical_inputs
   │  → rebuild_with_versioned_serializer
   │  → verify_identity_and_invariants
   │     ├─ equivalent → resume_original_flow
   │     └─ mismatch → invalidate_dependents → route_by_new_state
   ├─ active_safety_component
   │  → suspend_write_exposure
   │  → reprovision_or_switch_isolation
   │  → rerun_boundary_activation_contract
   └─ authority_or_canonical_input_missing
      → do_not_fabricate
      → safe_fallback_if_available
      → platform_blocked_or_human_change_decision
```

**Transition table**

| Current reason／state | Guard | Machine action | 成功後 | 失敗後 |
|---|---|---|---|---|
| `derived_artifact_missing_or_corrupt` | Canonical inputs 完整且 identity 有效 | `rebuild_derived_artifact` | 重驗後回原流程 | `artifact_rebuild_failed` |
| `derived_artifact_version_stale` | 有已測試的 deterministic upgrader／recompiler | `recompile_current_version` | 重驗後回原流程 | `artifact_rebuild_failed` |
| `artifact_identity_mismatch` | 重建結果與原 identity 不同 | `invalidate_dependent_artifacts` | 依目前 canonical state 建立新 identity | 依新 reason 路由 |
| `active_boundary_unhealthy` | 可停止 write exposure | `reprovision_boundary_or_switch_isolation` | 重跑 `PWC-CIM-001` | `safe_boundary_unavailable` |
| `canonical_input_missing` | 無法從 task specification／source／test assets 取得必要內容 | `do_not_fabricate_authority` | 走已定義 safe fallback | `platform_blocked` 或 `human_change_decision_required` |
| `artifact_rebuild_failed` | 仍有另一個已驗證 builder／backend | `circuit_break_and_use_fallback_builder` | 重驗後回原流程 | `safe_routes_exhausted` |

**必要不變量**

- 重建衍生資產不能改變 task specification、scope、acceptance、candidate content 或外部副作用決策。
- System Map 只能協助定位 canonical inputs，不能代替遺失的規格或授權。
- Rebuild 必須 deterministic、versioned，且完成後重新驗證 identity／digest／schema／必要不變量。
- Identity mismatch 不能被覆寫成原 identity；必須使所有依賴舊 identity 的 artifacts 與 PASS 失效。
- Active safety component 故障期間不得繼續暴露可寫工具。
- 常見 rebuild 由無 Agent 流程處理，只把有界結果摘要交給 Agent；不得把完整內部 log 注入 Context。

**對應業務測試**

```text
test_corrupt_candidate_manifest_is_rebuilt_from_immutable_snapshot
test_equivalent_rebuild_resumes_original_flow_without_human_checkpoint
test_rebuild_identity_mismatch_invalidates_dependent_subjects
test_context_or_runner_plan_rebuild_does_not_change_specification
test_system_map_cannot_replace_missing_task_specification_authority
test_unhealthy_boundary_suspends_write_tools_before_reprovision
test_failed_primary_builder_uses_verified_fallback_without_agent_debugging
test_rebuild_failure_fingerprint_does_not_create_unbounded_retry_or_logs
```

**後續 Stress Contract 候選**

- 大量 artifacts 同時損壞時，依賴順序重建不得產生循環、identity split-brain 或重複工作。
- 反覆 crash during rebuild 時，atomic publication 必須保證只看見舊完整版本或新完整版本。
- 大型 snapshot／suite manifest 重建不得讓 Agent token 消耗隨 artifact 大小線性成長。

#### 已確認 Recovery Chain RC-MVE-004：Runner Environment Failure

**功能**

Verification runner、虛擬環境、temporary workspace、port、dependency cache 或測試程序本身故障時，MVE 必須把它分類為 infrastructure failure，自動重建或切換已驗證 runner，再對完全相同的 Verification Subject 重跑。不得把環境故障回報成產品 pytest failure，也不得要求產品 Agent 修改 source 來迎合壞掉的 runner。

**業務例子**

固定 Verification Subject 準備執行 workspace acceptance tests，但 disposable runner 的 temporary directory 權限錯誤，pytest 尚未載入任何測試。MVE 機械判定 `runner_workspace_unusable`，銷毀該 disposable runner、建立新的受控 workspace、執行 environment self-check，然後對相同 subject 自動重跑。Implementation Agent 不會收到「請修改產品程式」或「請人工修理 temp directory」。

**Deterministic transition**

```text
runner_failure_detected
→ classify_failure_origin
   ├─ before_test_execution
   │  → rebuild_disposable_runner
   │  → environment_self_check
   │  → rerun_same_subject
   ├─ infrastructure_failure_during_execution
   │  → discard_non_authoritative_result
   │  → switch_verified_runner_backend
   │  → rerun_same_subject
   ├─ deterministic_test_failure
   │  → publish_product_verification_failure
   └─ origin_unknown
      → reproduce_in_clean_runner
      ├─ follows_subject → test_or_product_diagnosis
      └─ follows_runner → infrastructure_recovery
```

**Transition table**

| Reason code | Machine action | 必須保持不變 | Fallback |
|---|---|---|---|
| `runner_workspace_unusable` | 重建 disposable workspace | Verification Subject | 切換已驗證 workspace backend |
| `runner_environment_drift` | 依 environment profile 重建環境 | Candidate、spec、suite、threshold | 使用相容的預建環境 |
| `dependency_cache_corrupt` | 驗證並重建允許來源的 cache | Dependency lock／allowlist | 使用已驗證唯讀 cache |
| `resource_collision` | 重新分配受控 port／temp／worker slot | 測試語意與 subject | 序列 runner |
| `runner_process_crashed` | 保存有界 crash fingerprint，重建 runner 後重跑 | Verification Subject | 等價 runner backend |
| `infrastructure_failure_during_test` | 丟棄非權威結果並重跑 | 不產生產品 FAIL | clean runner reproduction |
| `failure_origin_unknown` | 在 clean runner 執行一次分類重播 | Subject 不變 | 依重播結果路由 |
| `runner_safe_routes_exhausted` | `emit_platform_blocked_once` | 不修改產品 source／tests | terminal |

**必要不變量**

- Environment recovery 必須重用完全相同的 `verification_subject_id`；若 candidate、spec、suite、threshold 或 profile 改變，必須建立新 subject，不能稱為 recovery retry。
- Runner failure 不能觸發產品 Agent 修改 source、pytest expectation、skip／xfail 或 threshold。
- Dependency download、network、credential 或其他外部副作用只能使用任務規格／environment profile 已明確允許的來源；未允許時不得為了修復環境自行連網。
- 每次 runner 必須先通過 environment self-check；self-check 只證明 runner 可執行，不代表產品 PASS。
- Infrastructure retry 的結果只有在 clean execution 完整跑完 required suites 後才有驗收效力。
- 常見重建、port replacement、temp replacement 與 backend fallback 由無 Agent 機械執行。
- 相同 infrastructure fingerprint 超過 recovery budget 後只產生一次 `platform_blocked`，不反覆呼叫 Agent。

**對應業務測試**

```text
test_unusable_runner_workspace_is_rebuilt_without_human_checkpoint
test_environment_failure_never_becomes_product_test_failure
test_rebuilt_runner_executes_the_exact_same_verification_subject
test_resource_collision_falls_back_to_safe_port_or_serial_runner
test_corrupt_dependency_cache_uses_only_allowed_rebuild_sources
test_unknown_failure_origin_is_classified_by_one_clean_reproduction
test_runner_recovery_never_changes_tests_thresholds_or_product_source
test_repeated_runner_failure_emits_one_platform_blocked_result
```

**後續 Stress Contract 候選**

- 多個 Verification Subjects 同時遇到 runner crash 時，重建不得造成 port、temp path 或 cache writer collision。
- 大量 infrastructure failures 不得污染產品 failure metrics，也不得讓 Agent Context 接收重複完整 logs。
- 長時間 soak 中反覆建立／銷毀 runner，不得殘留可修改 frozen candidate 的 process 或資源。

#### 已確認 Recovery Chain RC-DOM-MVE-005：Product Verification Failure

**功能**

固定 Verification Subject 完整執行後，若 required business pytest／stress tests 確認產品行為不符合任務規格，系統必須把有界失敗證據送回主 Agent，在原核准 scope、架構與驗收下自動修正 candidate；修正後建立新 candidate 與新 Verification Subject，重跑相同規格要求，不需要人工 Checkpoint。

**業務例子**

Workspace Subsystem 的狀態機通過 Module-level 路徑測試，但在 Subsystem 業務場景中無法正確處理「junction 解析後再次 canonicalize」。MVE 確認 runner 正常、pytest expectation 仍符合任務規格，因此將失敗分類為 `product_verification_failure`。主 Agent 依 Subsystem impact closure 修正狀態轉移與相關模組，重新 freeze candidate，再以相同規格條目與 acceptance assets 建立新 subject 重測。

**已確認場景 RC-DOM-MVE-005A：System Map 找到原 Scope 外的受影響節點**

**Given**

- 任務 write scope 是 Workspace Subsystem。
- Agent 修改 `PathCanonicalizationStateMachine` 產生的 normalized-path event。
- 初始 scope 沒有包含 Reporting Subsystem。
- System Map reverse-dependency query 顯示 `RevenueRecognitionProjection` 消費該 event。

**When**

- Workspace 業務場景驗證失敗，MVE 觸發 `SMQ-001` Q2 impact query。
- Context Broker 回傳 PathNormalizer 與 ManifestLoader 的 dependency edge。
- 主 Agent 以 live source 確認 Reporting 確實消費被修改的 event contract。

**Then**

- `RevenueRecognitionProjection` 加入 verification impact closure，但不因此取得 write permission。
- MVE 自動加入 Reporting 對應 regression suites，不需要人類核准「多跑測試」。
- 若 ManifestLoader regression PASS，Agent 只在原 Workspace scope 修正並重驗完整 closure。
- 若失敗可由 Workspace Subsystem 在既有 contract 內修正，仍不擴大 write scope。
- 只有修復必須修改 Reporting source、event schema 或跨 Subsystem contract 時，才產生 `human_change_decision_required`。
- 修改 Reporting source 時，至少需要新版 Work Package／Task Specification scope；只有 expected behavior 本身改變時才修改 behavioral specification，不能把 scope 估錯誤稱為業務規格錯誤。
- Failure Bundle 必須引用 `architecture_query_result_id`，並列出 Map edge 與 live-source confirmation；只呼叫 query 但未擴張 verification closure 視為 Contract failure。

**對應機械測試**

```text
test_reverse_dependent_outside_write_scope_is_added_to_verification_closure
test_adding_regression_suite_does_not_grant_write_permission
test_live_source_confirms_system_map_dependency_before_impact_use
test_workspace_fix_continues_without_human_when_manifest_loader_source_need_not_change
test_reporting_source_or_event_contract_change_requires_scope_decision
test_scope_expansion_updates_task_scope_without_rewriting_unchanged_expected_behavior
test_query_result_must_be_consumed_by_failure_bundle_and_suite_selection
```

**Deterministic transition**

```text
verification_failed
→ classify_failure_origin
   ├─ infrastructure_failure → RC-MVE-004
   ├─ test_implementation_defect → supervised_test_repair_flow
   ├─ specification_ambiguity_or_change → human_change_decision_required
   └─ product_verification_failure
      → query_system_map_impact_index
      → verify_map_assumptions_against_live_source
      → compute_failure_impact_closure
      → create_bounded_failure_bundle
      → resume_agent_in_authorized_scope
      → implement_and_self_test
      → freeze_new_candidate
      → create_new_verification_subject
      → rerun_required_verification
```

**完成與循環規則**

- Candidate 未修改前可以重播同一 subject；任何 source／test／configuration 修改後都必須建立新 candidate identity 與新 verification subject。
- 新 subject 必須沿用相同 task specification 與未經核准不得改變的 acceptance requirements。
- Repair scope 由失敗場景所在層級、System Map 正反向依賴查詢與 live-source verification 共同形成 impact closure：Module failure 可停留 Module；Subsystem／Domain 場景失敗時，必須以該層級整體重新分析與驗證，不能只修到單一檔案測試變綠。
- System Map 發現原 scope 外的 affected node 時，先加入 impact candidate；若只需在既有核准 scope 內擴大驗證可自動進行，若需要擴大 write scope、修改架構或契約才轉為人類決策。
- Agent 可在已核准 scope 內修改實作並增加自己的 diagnostic／unit tests，但不得修改受保護 acceptance expectation、降低 threshold、縮小 fixture、增加 skip／xfail 或移除 required suite。
- 一般產品缺陷修復、自測、freeze 與重驗自動循環；不在每輪詢問人類。
- 需要改變架構、schema、公開契約、任務規格、scope 或外部副作用時，才轉為 `human_change_decision_required`。
- 相同 failure fingerprint 反覆出現時，必須使用 bounded attempt budget；每輪沒有新 source delta 或新診斷證據時不得重複消耗 Agent token。

**Failure Bundle 最小內容**

```text
verification_subject_id
＋ failed_specification_and_scenario_ids
＋ failure_layer
＋ failure_classification
＋ impact_scope_assessment
＋ impact_closure
＋ architecture_query_result_id
＋ mapped_and_live_discovered_affected_nodes
＋ outside_verification_scope_nodes
＋ outside_write_scope_nodes
＋ required_specification_update_kind
＋ minimal_reproduction_command
＋ bounded_assertion_diff
＋ failure_fingerprint
＋ relevant_source_and_contract_locations
＋ attempted_fix_summaries
＋ remaining_attempt_budget
```

完整 pytest output、重複 traceback 與所有 PASS logs 保留在有界短期 buffer，不直接注入 Agent Context。

**對應業務測試**

```text
test_product_failure_returns_bounded_actionable_bundle_to_agent
test_module_failure_repairs_and_retests_module_impact_closure
test_subsystem_failure_revalidates_the_whole_subsystem_business_scenario
test_product_failure_queries_and_consumes_system_map_reverse_dependencies
test_out_of_scope_affected_node_expands_verification_without_granting_write_scope
test_candidate_change_always_creates_new_verification_subject
test_repair_loop_preserves_specification_and_acceptance_thresholds
test_product_agent_cannot_weaken_protected_acceptance_to_obtain_pass
test_successful_fix_freezes_and_retests_without_human_checkpoint
test_repeated_identical_failure_without_new_evidence_stops_token_loop
test_scope_or_spec_change_routes_to_human_change_decision
```

**後續 Stress Contract 候選**

- 大量 pytest failures 必須依 scenario／root-cause fingerprint 聚類，不能為每個 assertion 啟動獨立 Agent 修復。
- 多層 failures 同時存在時，修復排序與 impact closure 不得漏掉較高層業務場景。
- 長時間 repair／retest 循環不得讓 temporary logs、Attempt Ledger 或 Agent Context 無界成長。

#### 已確認 Recovery Chain RC-MVE-TAQG-006：Test Implementation Defect

**功能**

當 verification failure 的根因是 pytest／fixture／test helper 實作錯誤，而不是產品不符合規格時，DDH 必須允許自動修復 test asset；但修復 proposal、驗收語意判定與最終 admission 必須分離，防止同一 Agent 透過放寬 assertion、threshold、fixture 或 suite selection 製造 PASS。

**業務例子**

Workspace acceptance test 依核准規格驗證 `canonical_path == "src/module.py"`，但 test helper 因欄位改名仍讀取不存在的 `normalized_file`，導致 setup error。Test Repair Agent 提議只把 helper 改讀 `canonical_path`，不改 expected value、fixture data 或 scenario mapping。獨立 Test Critic 依固定規格與 protected acceptance manifest 審查，機械 guard 確認沒有 assertion weakening，再用原場景及 mutation probe 重跑；全部通過後自動接受 test repair 並建立新 test asset manifest／Verification Subject。

**分級處理**

| Test change 類型 | 自動流程 |
|---|---|
| Syntax、import、path、API rename、fixture construction 等實作修正，驗收語意不變 | Test Repair proposal → mechanical guard → independent Critic → replay／mutation probe → 自動 admission |
| Assertion 結構改寫但可機械證明與固定規格語意等價或更強 | 加強 Critic 與 mutation／property replay；證明成立才自動 admission |
| Expected value、threshold、fixture population、scenario boundary、required suite、skip／xfail 改變 | 視為 acceptance semantics change；不得由一般 repair flow 自動接受 |
| 規格本身矛盾或無法判斷語意等價 | `human_change_decision_required` |

**Deterministic transition**

```text
suspected_test_defect
→ reproduce_against_fixed_subject
→ create_test_repair_proposal
→ mechanical_acceptance_guard
   ├─ weakening_detected → reject_proposal
   └─ no_mechanical_weakening
      → independent_test_critic
      → scenario_replay_and_mutation_probe
         ├─ semantics_preserved → admit_new_test_asset_version
         │  → create_new_verification_subject
         │  → rerun_required_verification
         └─ ambiguous_or_weaker → reject_or_human_change_decision
```

**角色與機械邊界**

- Test Repair Agent 只提出 patch，不擁有 admission。
- Independent Test Critic 必須使用獨立 execution identity，且不得接收 Repair Agent 的結論作為 authority；模型／profile 是否必須不同留待成本與效果實驗固定，但同一執行實例不得自審自批。
- Mechanical Acceptance Guard 至少阻擋 assertion deletion、expected-value widening、threshold lowering、fixture shrinking、case removal、required marker removal、skip／xfail 增加與 suite exclusion。
- Critic 的 prompt 是審查輔助，不是機械強制；真正 admission 必須由 guard、固定規格映射與可重播 tests／mutation probes 支持。
- Test asset 一旦修改，舊 verification subject 必須失效；不能用新 pytest 回填舊 subject 的 PASS。
- 修復不改變驗收語意時，全流程自動繼續，不建立人工 Checkpoint。

**Failure／Review Bundle 最小內容**

```text
task_specification_id_and_version
＋ protected_acceptance_manifest_id
＋ affected_scenario_and_test_asset_ids
＋ original_and_proposed_test_diff
＋ claimed_test_implementation_defect
＋ mechanical_guard_result
＋ critic_result
＋ replay_and_mutation_results
＋ remaining_test_repair_budget
```

**對應業務測試**

```text
test_fixture_api_rename_can_be_repaired_without_changing_expectation
test_test_repair_agent_cannot_admit_its_own_patch
test_assertion_deletion_or_threshold_lowering_is_mechanically_rejected
test_fixture_shrinking_or_skip_addition_is_mechanically_rejected
test_independent_critic_receives_fixed_spec_not_repair_agent_authority
test_semantics_preserving_test_repair_creates_new_asset_and_subject_ids
test_mutation_probe_detects_a_test_patch_that_no_longer_catches_violation
test_ambiguous_acceptance_change_routes_to_human_decision
test_accepted_test_repair_reruns_full_required_verification_without_checkpoint
```

**後續 Stress Contract 候選**

- 大量 test repair proposals 同時提交時，不得讓同一 execution identity 同時成為 proposer 與 approver。
- 對抗性 assertion weakening／fixture shrinking 變形應由 guard 與 mutation probes 維持高偵測率。
- Critic unavailable 時可以排隊或切換已驗證 Critic profile，不能降級成 Repair Agent 自批。

**討論狀態**

Test Asset Quality Governance 的四軸品質模型、Admission Pipeline、TAQG／MVE Subsystem 拆分、`TAQG-MVE-001` handoff 與本 Recovery Chain 均已確認。

## 2. Subsystems

| Subsystem | 責任 |
|---|---|
| Parallel Work Coordination | 平行判斷、施工分區、共享資源、跨區請求、移交、中央整合與隔離模式 |
| Candidate Integrity and Mutation | 寫入邊界、快照、復原、stale result、Mutation Mediation 與 candidate identity |
| Context Broker | System Map discovery、最小 Context Envelope、content grant 與 token budget |
| Test Asset Quality Governance | Test Quality Contract、test asset admission、Critic、mutation、生命週期與防放寬 |
| Mechanical Verification Execution | Immutable Verification Subject、runner recovery、無 Agent pytest／stress 執行與結果分類 |
| Orchestration Learning and Evolution | 短期觀測、Attempt Ledger、log buffer、自進化消化與刪除 |

## 3. 端到端流程

```text
使用者目標＋固定引用規範
→ 凍結任務規格
→ Parallel Work Coordination 決定單一／平行施工
→ Context Broker 提供最小 Context
→ Candidate Integrity 保護寫入與候選版本
→ Test Asset Quality Governance admission pytest 資產
→ 主 Agent 中央整合
→ Mechanical Verification Execution 無 Agent 重跑 pytest／stress
→ 完成後保留 pytest 資產
→ Attempt Ledger 進入 Evolution 分析並刪除
```

## 4. Domain 級業務場景

### OW-S01：實作與 pytest 正常平行完成

**Given**

- 任務規格已固定。
- Implementation Agent 與 Test Agent 有不重疊的寫入區。

**When**

- 兩者平行完成候選變更。
- 主 Agent凍結寫入並建立整合快照。

**Then**

- 兩份候選 diff 都保留。
- 沒有越界寫入。
- 最終 pytest 對固定 snapshot 執行。
- PASS 可追溯至規格版本與 source candidate。

### OW-S02：Implementation Agent 嘗試修改驗收測試

**Then**

- 寫入被阻擋。
- 原檔案不變。
- 事件被記錄。
- Agent 可提出測試錯誤報告，但不能自行修改 expected behavior。

### OW-S03：Test Agent 嘗試修改產品程式

**Then**

- 寫入被阻擋。
- Test Agent 回報需要實作修正的證據。
- 主 Agent將缺陷交還 Implementation Agent。

### OW-S04：發現公開契約不足

**Given**

- Test Agent 發現現有 API 無法表達規格要求。

**Then**

- 子代理不得修改公開契約。
- 主 Agent判斷是實作缺陷還是契約變更。
- 若需要改變公開介面，產生人類例外報告。

### OW-S05：測試需要共享 fixture

**Then**

- Test Agent 提出跨區請求。
- 主 Agent確認 fixture 是否只屬測試資產。
- 若可安全重分區，先完成原區凍結與 diff 檢查，再移交。

### OW-S06：Agent 在持有分區時失聯

**Then**

- 分區進入 `recovery_required`，而不是自動釋放給下一個 Agent。
- 保存殘留 diff。
- 檢查是否存在未完成寫入。
- 完成復原判定後才能重新分配。

### OW-S07：平行期間 pytest 通過

**Then**

- 結果只能標記為 provisional。
- 不得宣告 Work Package 完成。
- 所有 writer 停止後仍須建立固定 snapshot 並重跑必要驗證。

### OW-S08：兩項工作無法切分共享檔案

**Then**

- 主 Agent不得建立兩個重疊 writer。
- 工作改為序列執行，或重新切分成不重疊的邏輯資源。

### OW-S09：既有 dirty worktree

**Given**

- 任務開始前，使用者已在目標路徑留下未提交差異。

**Then**

- baseline 必須保存既有差異。
- Agent 產生的 delta 必須可以與既有差異區分。
- ownership 不得把既有差異錯誤歸屬給任何 Agent。
- 不得為了建立乾淨環境而擅自 reset、stash 或覆寫。

### OW-S10：舊 Agent 遲交成果

**Given**

- Agent A 從 candidate `C1` 開始施工後失聯。
- 主 Agent已把資源重新分配給 Agent B，並產生 candidate `C2`。

**When**

- Agent A 遲交基於 `C1` 與舊 generation 的 patch。

**Then**

- patch 不得靜默套用。
- 系統必須標示 baseline／generation 已過期。
- 主 Agent可以檢查其中是否有可保留資訊，但必須重新整合及重驗。

### OW-S11：個別成果都通過，但整合失敗

**Given**

- Implementation Agent 與 Test Agent各自在自己的 candidate 上回報 PASS。

**When**

- 主 Agent整合兩份成果後，Subsystem interaction test 失敗。

**Then**

- Work Package 不得完成。
- 回到 Subsystem 層級重新分析。
- 個別 PASS 只作診斷證據，不能取代整合 candidate 的結果。

## 5. 跨 Subsystem 完成邊界

- 子代理 submitted 不代表 Work Package completed。
- Subsystem implementation verified 不代表 DDH integrated。
- DDH integrated 不代表 Domain accepted、release candidate 或 production deployed。
- 一般節點完成後只保留可重跑 pytest 資產；不永久保存歷史 PASS、Ledger 或一般 logs。

## 6. 舊功能 ID 遷移矩陣

| 舊 ID | 新責任歸屬 | 已確認功能 |
|---|---|---|
| OW-F01 | 平行施工協調 Subsystem | 判斷是否需要平行寫入分區 |
| OW-F02 | 平行施工協調 Subsystem | 建立寫入分區 |
| OW-F05 | 平行施工協調 Subsystem | 管理共享資源 |
| OW-F06 | 平行施工協調 Subsystem | 處理跨區變更請求 |
| OW-F07 | 平行施工協調 Subsystem | 安全移交 |
| OW-F12 | 平行施工協調 Subsystem | 保留中央整合權 |
| OW-F13 | 平行施工協調 Subsystem | 選擇施工隔離模式 |
| OW-F03 | Candidate 完整性與 Mutation Subsystem | 讀取與寫入分離 |
| OW-F08 | Candidate 完整性與 Mutation Subsystem | 固定整合快照 |
| OW-F10 | Candidate 完整性與 Mutation Subsystem | 故障復原 |
| OW-F11 | Candidate 完整性與 Mutation Subsystem | 防止接受過期成果 |
| OW-F14 | Candidate 完整性與 Mutation Subsystem | 建立 Mutation Mediation Boundary |
| OW-F15 | Candidate 完整性與 Mutation Subsystem | Candidate Identity 與 Snapshot Manifest |
| OW-F16 | Context Broker Subsystem | Context Broker 與 Context Budget |
| OW-F04 | Test Asset Quality Governance Subsystem | 保護規格、測試品質與獨立 admission |
| OW-F17 | Mechanical Verification Execution Subsystem | 可重用的無 Agent 機械驗證 |
| OW-F09 | 編排學習與自進化 Subsystem | 執行期間的機械觀測 |
| OW-F18 | 編排學習與自進化 Subsystem | Attempt Ledger 暫存與自進化消化 |
| OW-F18.1 | 編排學習與自進化 Subsystem | Attempt Ledger 最小資料模型 |
| OW-F18.2 | 編排學習與自進化 Subsystem | 短期 Log Buffer 與輸出邊界 |
| OW-F18.3 | 編排學習與自進化 Subsystem | Ledger 消化觸發與刪除時機 |

## 7. 文件

- `parallel_work_coordination_subsystem_specification.md`
- `candidate_integrity_and_mutation_subsystem_specification.md`
- `context_broker_subsystem_specification.md`
- `test_asset_quality_governance_subsystem_specification.md`
- `mechanical_verification_execution_subsystem_specification.md`
- `mechanical_verification_and_test_governance_subsystem_specification.md`（split archive）
- `orchestration_learning_and_evolution_subsystem_specification.md`
- `layered_completion_contract.md`（`DDH-COMP-001`）
- `terminal_completion_attempt_ledger_handoff_contract.md`（`DOM-OLE-001`）
- `evolution_profile_pending_ledger_policy.md`（`OLE-PROFILE-001`）
- `operational_telemetry_and_health_model.md`（`DDH-OBS-001`）
- `long_term_orchestration_memory_model.md`（`OLE-MEM-001`）
- `memory_evolution_critic_trial_rollback_contract.md`（`OLE-EVOL-001`）
- `task_specification_work_package_boundary.md`（`SPEC-WP-001`）
- `risk_gate_and_exception_escalation_contract.md`（`DDH-RISK-001`）
- `coding_harness_and_agent_self_check_profile.md`（`DDH-CODE-001`）
- `managed_assets_and_external_high_risk_operations_contract.md`（`DDH-OPS-001`）

- `ddh_execution_domain_discussion_archive.md`：只保存拆分前討論歷史。

## 8. 拆分後待補

### 8.1 共享 Identity Vocabulary

六個 Subsystems 必須共同使用並區分：

- task specification id／version。
- Work Package／execution run id。
- partition id。
- trusted writer／execution identity。
- partition generation。
- source candidate／snapshot manifest identity。
- verification subject／verification manifest identity。
- attempt／Ledger identity。

### 8.2 尚未固定的原子交接

1. **已確認：** PWC 核發 partition 與 CIM 啟用 mutation boundary。
2. **已確認：** Writer freeze／stop、candidate patch admission 與 candidate frozen。
3. **已確認：** TAQG admitted test assets 與 MVE manifest usable。
4. **已確認：** Candidate frozen 與 verification subject 建立。
5. **已確認：** Verification PASS 與分層 completion decision（`DDH-COMP-001`）。
6. **已確認：** Terminal execution 與 OLE Ledger seal／enqueue
   （`DOM-OLE-001`）。

#### 已確認：Partition Activation Contract

PWC 只能在 CIM 對完全相同的 identity tuple 回報 `boundary_active` 後，將 partition 公開為 `active`：

```text
work_package_id
＋ partition_id
＋ partition_generation
＋ trusted_writer_execution_identity
＋ base_candidate_id
＋ write_resource_set_digest
＋ boundary_mode
```

狀態流程：

```text
PWC: planned → activating → active
                   └→ activation_failed

CIM: requested → provisioning → boundary_active
                     └→ boundary_failed
```

必要不變量：

- `activating` 期間不得把可寫施工工具交給子代理。
- `boundary_active` 必須來自 CIM 的機械狀態，不能來自 Agent claim 或 prompt。
- PWC 收到的 identity tuple 任一欄不符、generation 過期或 boundary mode 不符時，Activation 失敗。
- CIM 啟用失敗時，PWC 改用隔離模式、序列施工或 recovery；不得降級為 prompt-only 平行寫入。
- Boundary 啟用後若在 Agent 開始前失效，partition 不得維持 `active`。

### DDH-EO-E2E-001：Boundary 生效後才能啟動 Partition

**Given**

- PWC 已建立 partition generation。
- 子代理尚未取得可寫工具。

**When**

- CIM 為相同 identity tuple 啟用 mutation boundary 並回報 `boundary_active`。

**Then**

- PWC 才能將 partition 改為 `active`。
- 子代理才取得該分區的可寫施工環境。
- 若 CIM 回報失敗、過期或不相符 tuple，partition 進入 `activation_failed`。

對應機械測試：

```text
test_partition_becomes_active_only_after_matching_mutation_boundary_is_active
test_partition_activation_rejects_stale_or_mismatched_boundary_identity
test_writer_tools_are_not_exposed_while_partition_is_activating
```

#### 已確認：PWC-CIM-002 Writer Quiescence and Candidate Freeze

Agent 或 PWC 宣告「施工完成」只能觸發 freeze request，不能證明 writer 已停止，也不能直接凍結 candidate。CIM 必須先建立 generation fence、排空已核准的寫入，並以機械狀態證明沒有修改仍可能落入該 candidate。

Freeze request 至少綁定：

```text
work_package_id
＋ integration_group_id
＋ freeze_request_id
＋ expected_base_candidate_id
＋ target_partition_ids_and_generations
＋ trusted_writer_execution_identities
＋ mutation_boundary_instance_ids
＋ submitted_delta_ids
```

建議狀態流程：

```text
PWC: active → freeze_requested → waiting_for_quiescence → writers_stopped
                           └→ freeze_failed／recovery_required

CIM: boundary_active → freeze_fenced → draining → quiescent → candidate_frozen
                                      └→ recovery_required
```

必要不變量：

- `freeze_fenced` 後，目標 generations 不得開始新的寫入；遲到寫入必須被拒絕。
- `draining` 必須涵蓋已核准但尚未結束的工具操作、formatter、generator 與其他間接 writer。
- Agent claim、程序正常退出或 PWC 狀態都不能取代 CIM 的 mechanical quiescence。
- 所有目標 partitions、shared resources 與 submitted deltas 都通過 admission，才能建立整合 candidate。
- 任一 writer 的 mutation closure 未知、外部副作用狀態未知、generation 不符或 delta 身分不符時，不得部分凍結成最終 candidate，必須進入 recovery。單純遺失 exit code 但已證明 mutation closure，不構成阻塞。
- Frozen candidate 必須綁定 immutable candidate identity 與 manifest；後續合法修改必須產生新 candidate generation。
- Candidate frozen 只代表驗證輸入已固定，不代表驗證通過或 Work Package 完成。
- 使用者在任務前已存在的差異必須保留在 baseline／manifest 中，不得誤算為某個 Agent delta。

### DDH-EO-E2E-002：所有 Writer 靜止後才能凍結 Candidate

**Given**

- Implementation Agent 與 Test Agent 已提交各自的 candidate delta。
- PWC 已對完整 integration group 發出 freeze request。

**When**

- CIM 封鎖所有目標 generations 的新寫入。
- CIM 等待已核准操作完成，核對 touched resources、shared resources 與 admitted deltas。
- CIM 對完全相同的 freeze identity 回報 `quiescent` 並建立 frozen candidate manifest。

**Then**

- PWC 才能把該 integration group 標記為 `writers_stopped`。
- Candidate 才能進入 `candidate_frozen`，供下一階段建立 verification subject。
- 若仍有 active／unknown writer、stale generation、未核准 delta 或 fence 後寫入，結果為 `freeze_failed` 或 `recovery_required`。

對應機械測試：

```text
test_candidate_freezes_only_after_all_target_generations_are_quiescent
test_agent_done_claim_does_not_prove_writer_quiescence
test_freeze_rejects_unknown_or_inflight_mutation
test_post_fence_mutation_cannot_change_frozen_candidate
test_partial_writer_quiescence_cannot_create_final_candidate
test_freeze_manifest_preserves_user_baseline_and_partition_deltas
```

### 已確認場景 DDH-EO-E2E-002A：Agent 宣告完成但背景 Writer 尚未停止

**業務例子**

Implementation Agent 完成主要程式修改後宣告完成，但先前啟動的 code generator、formatter、test watcher 或其 descendant process 仍可能修改受管理資源。PWC 收到完成訊息時，不得假設 candidate 已穩定。

**Given**

- Partition 仍綁定有效的 writer identity 與 generation。
- Agent 已向 PWC 回報工作完成。
- CIM 仍觀察到至少一個已核准但尚未結束的 write-capable operation，或其 mutation closure 無法確認。

**When**

- PWC 對該 integration group 發出 freeze request。
- CIM 建立 generation fence，阻擋新的 writes，並開始 draining 已存在的 writer。

**Then**

- PWC 保持 `waiting_for_quiescence`；不得因 Agent claim 進入 `writers_stopped`。
- Writer 在允許的 bounded drain budget 內正常結束時，CIM 核對其實際 touched resources 與 delta，再自動繼續 candidate freeze，不需要人工 Checkpoint。
- Writer 超過 drain budget、失聯或 mutation closure 仍未知時，結果必須是 `recovery_required`，不得建立 frozen candidate。
- Fence 後由該 writer 或 descendant process 發起的新 mutation 必須被拒絕，且不能改變最終 manifest。
- 已產生的合法 candidate delta 與使用者原有差異都必須保留，不得為了停止 writer 而 reset、stash 或刪除。

**對應機械測試**

```text
test_agent_completion_claim_does_not_prove_writer_quiescence
test_candidate_freeze_waits_for_registered_descendant_writer
test_freeze_continues_automatically_after_background_writer_drains
test_unresolved_writer_after_drain_budget_requires_recovery
test_post_fence_descendant_mutation_cannot_change_candidate_manifest
test_writer_recovery_preserves_agent_delta_and_user_baseline
```

**尚未固定的參數**

- Drain budget 由風險與工具 profile 決定，不在此憑空固定秒數。
- Writer 可否安全終止、允許何種 termination action，必須由工具／隔離模式的既定政策決定；不能由 Agent 臨時選擇。

### 已確認場景 DDH-EO-E2E-002B：只有部分 Writers 已靜止

**業務例子**

Implementation Agent 與 Test Agent 屬於同一 integration group，兩者都已向 PWC 宣告完成。CIM 確認 Implementation Agent 已停止寫入，但發現 Test Agent 的背景 test generator 仍在 draining 或 outcome unknown。系統需要保留已完成的 implementation delta，但不能把只有一半達到 mechanical quiescence 的 candidate 當成最終驗證對象。

**Given**

- Freeze request 指定兩個以上 target partitions／generations。
- 所有目標 Agent 都已回報完成。
- 至少一個 partition 已達 mechanical quiescence，且其 delta 已通過 admission。
- 至少一個其他 partition 仍在 draining、active 或 outcome unknown。

**When**

- CIM 彙整整個 freeze request 的 quiescence 狀態。

**Then**

- 已靜止 partition 的 delta 可以被個別 seal 並保留，舊 generation 不得恢復寫入。
- PWC 對完整 integration group 維持 `waiting_for_quiescence`。
- CIM 不得建立代表完整 integration group 的 `candidate_frozen` manifest。
- 不得以已靜止 partition 的局部 candidate 執行最終 Work Package 驗收或宣告完成。
- 其餘 writers 隨後正常靜止時，自動重新彙整並建立完整 frozen candidate。
- 其餘 writers 失敗或需要重派時，保留已 sealed delta；新 writer 必須取得新 generation，完成後再建立新的完整 freeze request。

**對應機械測試**

```text
test_partial_writer_quiescence_cannot_freeze_integration_candidate
test_quiescent_partition_delta_is_sealed_and_preserved_while_group_waits
test_sealed_partition_generation_cannot_resume_writing
test_group_freezes_automatically_after_remaining_writers_become_quiescent
test_failed_remaining_writer_requires_new_generation_before_refreeze
test_partial_candidate_cannot_be_used_for_final_work_package_acceptance
```

### 已確認場景 DDH-EO-E2E-002C：工具結果未知但 Mutation 狀態可或不可封閉

**需要釐清的兩種「未知」**

| 狀態 | 意義 | Freeze 結果 |
|---|---|---|
| `operation_result_unknown_but_mutation_closed` | Exit code／工具回應遺失，但已機械證明 writer 終止、沒有後續 write 能力，且完整 candidate snapshot 可枚舉 | 可依實際 snapshot 繼續 freeze；後續由規格驗證判斷內容是否正確 |
| `mutation_state_unknown` | 無法證明 writer 已停止、可能仍有 descendant writer、實際 touched resources 無法完整取得，或存在未知外部副作用 | 必須 `recovery_required`，不得 freeze |

**業務例子**

Code generator 執行期間控制通道逾時，PWC 沒有收到 exit code。若 CIM 能證明程序及 descendants 均已結束、隔離邊界仍完整，並能擷取全部生成結果，則「工具是否自認成功」不是 candidate integrity 問題；生成內容是否符合需求交由後續 pytest 驗證。反之，若仍可能繼續寫入或有無法觀察的外部副作用，就不能凍結。

**Given**

- Agent 執行一個可能修改多個受管理資源的工具。
- 工具的 exit code、response 或 Agent-side result 遺失。
- CIM 已建立 freeze fence。

**When**

- CIM 檢查 writer／descendant lifecycle、mutation boundary、實際 candidate snapshot、touched resources 與外部副作用分類。

**Then**

- 若 mutation closure 可被機械證明，CIM 記為 `operation_result_unknown_but_mutation_closed`，依實際 snapshot 建立 manifest 並允許流程自動進入 verification。
- 此結果不得被描述為工具成功；功能正確性仍必須由固定 Verification Subject 的 pytest／stress tests 判定。
- 若 mutation closure 無法證明，結果為 `mutation_state_unknown`／`recovery_required`，不得建立 frozen candidate。
- 涉及資料庫、網路、部署、憑證或其他外部副作用且結果未知時，移交獨立高風險流程，不得套用單純 filesystem snapshot 的寬鬆判定。
- Agent claim、推測性 log 解讀或「大概已結束」都不能證明 mutation closure。

**對應機械測試**

```text
test_unknown_exit_code_allows_freeze_when_mutation_closure_is_proven
test_unknown_exit_code_is_not_reported_as_operation_success
test_unclosed_writer_state_requires_recovery_instead_of_freeze
test_frozen_manifest_captures_all_outputs_of_result_unknown_operation
test_verification_runs_against_result_unknown_but_closed_snapshot
test_unknown_external_side_effect_is_routed_to_high_risk_recovery
```

**對既有 Contract 文字的已確認修正**

`PWC-CIM-002` 中原本籠統的「operation outcome 未知時不得 freeze」，應縮窄為「mutation closure 或外部副作用狀態未知時不得 freeze」，避免把遺失 exit code 這類可由實際 snapshot 與後續驗證吸收的問題變成人工阻塞。

### 已確認場景 DDH-EO-E2E-002D：Freeze Fence 與遲到寫入競態

**需要區分的寫入**

| 寫入類型 | Fence 後處理 |
|---|---|
| Fence 前已被 boundary 核准、仍在追蹤中的 in-flight operation | 允許在 `draining` 期間完成；所有結果納入 touched resources 與 delta，結束前不得宣告 quiescent |
| Fence 後才要求開始的新 operation，或來自 stale generation 的 operation | 必須拒絕，不得進入 candidate |
| 已宣告 `quiescent`／`candidate_frozen` 後仍實際落入的 mutation | 視為 integrity breach；舊 candidate／verification subject 立即失效並進入 recovery |

**業務例子**

Test Agent 在 freeze request 前已啟動 formatter。CIM 建立 fence 後，formatter 仍需要完成最後一批已核准寫入；同時 test watcher 又嘗試啟動第二次 formatter。前者屬於 draining，後者是 fence 後的新 operation，必須被拒絕。只有第一個 formatter 完成並完成 reconciliation 後才能 freeze。

**Given**

- Partition generation 正在 `active`，且存在至少一個 fence 前已核准的 in-flight operation。
- PWC 發出 freeze request，CIM 建立帶有 freeze epoch 的 fence。

**When**

- 已核准 operation 在 draining 期間完成其剩餘寫入。
- 同一 writer、descendant 或 stale generation 在 fence 後嘗試開始另一個 mutation operation。

**Then**

- Fence 前已核准的 operation 可以完成，其全部實際變更必須被 reconciliation 與 manifest 收錄。
- Fence 後的新 operation 必須得到 `blocked_frozen_generation`／`blocked_stale_generation`，不得污染 candidate。
- CIM 必須等所有 fence 前 operations 結束後才能回報 `quiescent`。
- Frozen candidate 在任何隔離模式下都必須保持 immutable；共享工作區阻擋原地寫入，隔離模式則確保舊 writer 無法改變已物化的 frozen snapshot。
- 若 mutation 在 `quiescent` 或 `candidate_frozen` 後仍成功落入受驗證 snapshot，必須使 candidate 與既有 verification subject 失效，不能只補記 warning 或沿用 PASS。

**對應機械測試**

```text
test_pre_fence_admitted_operation_can_drain_before_quiescence
test_drained_operation_outputs_are_included_in_candidate_manifest
test_post_fence_new_operation_is_blocked
test_stale_generation_cannot_start_mutation_after_fence
test_candidate_is_not_quiescent_until_all_pre_fence_operations_finish
test_post_freeze_landed_mutation_invalidates_candidate_and_subject
test_freeze_write_race_assigns_each_operation_to_exactly_one_side_of_fence
```

### 已確認 Contract PWC-INTEG-003：Asynchronous Module Fork-Join and Subsystem Verification

一個 Subsystem 內的多個 Modules 在寫入範圍、必要 Context 與 shared contracts 可分離時，可以由 PWC 建立非同步施工 lanes。產品 source 與 Test Asset 都是施工產物；Implementation／Test writers 分區擁有，draft test execution 只提供 provisional feedback。

```text
fixed Subsystem specification
→ System Map dependency intersection query
→ fork Module construction lanes
→ each lane reaches product-quiescent＋test-admitted＋module-verified
→ mechanical Join Barrier
→ integrate current generations in deterministic order
→ actual diff／System Map impact reconciliation
→ freeze Subsystem candidate
→ rerun required Module tests
→ run Subsystem scenarios／stress／affected regressions
```

必要不變量：

- Module lane readiness 是 composite mechanical state，不能由 Agent 完成宣告取代。
- Module lane 可以封存 immutable provisional snapshot 做 Module feedback，但只有 Join 後的 integrated snapshot 是 Subsystem candidate。
- Subsystem Test Agent 可以在 Module product construction 期間依固定規格提前施工 tests，但正式執行等待 integrated candidate。
- 先完成 lanes 進入 waiting state，停止 writer 與 Agent token 消耗；shared dependency change 只喚醒受影響 lanes。
- Module-level PASS 不等於 Work Package completion，也不能把不同 Module candidates 的 PASS 拼成 Subsystem PASS。
- Join 只接受 current generations、pinned shared contracts、admitted Test Assets 與已證明 quiescent 的 writers。
- Subsystem failure 提升整體分析／重驗範圍，但寫入權只重新授予實際責任 Modules。
- Scope 外 affected nodes 依 `MVE-RESULT-001` 擴大 verification；需要越界 repair 時建立 versioned scope／contract／specification proposal。

System Map 必須在 fork 前、各 lane actual diff 後、join 前與 Subsystem failure 後被查詢並由 partition plan／integration plan／suite selection 實際消費。本 Contract 的完整 responsibility projection、業務場景、Stress Contract 與測試位於 `parallel_work_coordination_subsystem_specification.md`。

### 待確認場景 DDH-EO-E2E-002E：使用者既有差異與 Agent Delta 共存

**業務例子**

使用者在 Work Package 開始前已修改 `workspace/path_service.py`，但尚未 commit。Agent 的任務也需要修改同一檔案中的另一段功能。DDH 不要求先清理、stash 或提交工作區；它必須以任務開始時的實際內容作為 baseline，保留使用者差異，並只把 baseline 之後由受信 writer 產生的變更視為 Agent delta。

**Given**

- 工作區在任務開始前存在 tracked 或 untracked 的使用者差異。
- CIM 已在 writer 啟用前擷取 task-start baseline identity 與必要內容邊界。
- Agent 在授權 partition 內修改部分相同或不同資源。

**When**

- PWC 發出 freeze request。
- CIM 對 task-start baseline、目前 candidate snapshot、writer identity、partition generation 與實際 touched resources 進行 reconciliation。

**Then**

- Frozen candidate 必須保留 task-start baseline 中的所有使用者差異。
- Agent delta 只能表示「candidate 相對 task-start baseline」且可歸屬於本次受信 writer 的變更；不得把 baseline 中既有內容算成 Agent 成果。
- 同一檔案同時包含使用者既有內容與 Agent 新修改時，必須保留完整最終內容，不能用整檔 restore／replace 消除任一方。
- 與任務無關的使用者差異不得因 freeze、recovery、reassignment 或 candidate materialization 被 reset、stash、刪除或覆寫。
- 若 task-start baseline 未成功建立，或執行期間出現無法歸屬的外部 mutation，使 baseline／Agent delta 無法可靠區分，結果為 `baseline_ambiguous`／`recovery_required`；不得捏造 attribution。此狀態先進入自動 baseline 重建、隔離 candidate 或新 generation 流程，不直接詢問人類。
- Baseline／delta manifest 是執行期間的 integrity state，不升格為永久 Evidence Retention；Work Package 完成後仍依既定 retention policy，只長期保留可重跑的 pytest 資產。

**對應機械測試**

```text
test_preexisting_user_changes_are_preserved_in_frozen_candidate
test_agent_delta_is_computed_relative_to_task_start_baseline
test_preexisting_changes_are_not_attributed_to_agent_writer
test_same_file_user_baseline_and_agent_delta_survive_freeze
test_freeze_and_recovery_never_reset_stash_or_delete_unrelated_user_changes
test_unattributable_external_mutation_requires_recovery
test_baseline_manifest_remains_temporary_execution_state
```

#### 已確認：TAQG-MVE-001 Admitted Test Asset Handoff

TAQG admission 的目的，是把固定規格、業務場景與 test quality requirements 編譯成 MVE 可機械執行的 immutable asset set。MVE 不重新審查測試語意，也不能自行挑選「看起來可用」的 draft tests。

Handoff 至少綁定：

```text
task_specification_id_and_version
＋ test_quality_contract_id_and_version
＋ test_asset_manifest_id_and_digest
＋ admitted_asset_ids_versions_and_content_digests
＋ required_scenario_mapping
＋ required_suite_and_fixture_mapping
＋ execution_profile_ids_and_versions
＋ runner_compatibility_profile
＋ invalidation_epoch
```

狀態流程：

```text
TAQG: draft → candidate → admission_validating → admitted → active
                                      ├→ rejected
                                      └→ quarantined
             active → stale／superseded

MVE: manifest_received → manifest_validating → manifest_usable
                                      ├→ verification_not_ready
                                      └→ manifest_rejected
```

**Machine routing**

| MVE intake result | 下一步 |
|---|---|
| `manifest_not_yet_admitted` | 等待 TAQG admission event；不詢問人類、不漏跑 acceptance |
| `manifest_rejected_or_quarantined` | TAQG 自動送回 Test Agent repair flow；MVE 保持 `verification_not_ready` |
| `manifest_stale_or_superseded` | 取得最新 admitted manifest，重新驗證 identity／epoch |
| `asset_missing_or_digest_mismatch` | 依 `RC-DOM-003` 重建；內容改變時回 TAQG 重新 admission |
| `required_scenario_unmapped` | 視為 TAQG admission defect，撤回 manifest 並修復 mapping |
| `runner_incompatible` | 依 `RC-MVE-004` 重建／切換 runner，不修改 test assets |
| `invalidation_during_validation` | 原子拒絕舊 manifest，取得新 epoch 後重試 |

必要不變量：

- Formal Verification Subject 只能引用 `admitted／active` test assets。
- Draft／candidate tests 可以由 Test Agent 在自己的施工區自測，但結果永遠不能完成 Work Package。
- `admitted` 狀態必須來自 TAQG canonical lifecycle state；discovery index、檔名、marker 或 Agent claim 不能單獨證明 admission。
- Manifest publication 必須 atomic；MVE 只能看到舊完整版本或新完整版本。
- Manifest usable 不代表產品 PASS，只代表 test assets 可被正式綁入 Verification Subject。
- TAQG 新版本不覆寫任何既有 subject；MVE 必須用新 manifest 建立新 subject identity。
- Admission 尚未完成、manifest stale 或 runner 不相容都是機械等待／復原狀態，不產生人工 Checkpoint。
- Test Asset Manifest 是由 pytest／fixture／configuration／profile 產生的 derived artifact；長期 Evidence Retention 仍是這些可重播資產，不另外保存歷史 admission receipt。

### DDH-EO-E2E-TAQG-MVE-001：Candidate 先完成但 Test Admission 尚未完成

**Given**

- Implementation candidate 已完成並 frozen。
- Test Agent 已提交 draft pytest，但 TAQG 仍在執行 mutation／determinism admission。

**When**

- MVE 收到 candidate intake，但尚未取得 admitted Test Asset Manifest。

**Then**

- MVE 回報 `verification_not_ready／manifest_not_yet_admitted`，並等待 TAQG lifecycle event。
- MVE 不使用 draft tests 建立正式 Verification Subject，也不要求人類批准等待。
- TAQG admission 成功後，自動發布 immutable manifest；MVE 驗證完整 identity 後繼續建立 subject。
- TAQG rejection 時，自動送回 Test Agent 修復；產品 candidate 可以保持 frozen，不需要重做未受影響實作。

對應機械測試：

```text
test_mve_accepts_only_taqg_admitted_active_assets
test_draft_tests_can_run_diagnostically_but_cannot_complete_work_package
test_candidate_waits_for_test_admission_without_human_checkpoint
test_admission_event_automatically_resumes_subject_creation
test_rejected_test_asset_routes_to_repair_without_refreezing_product_candidate
test_stale_or_invalidated_manifest_is_atomically_rejected
test_manifest_digest_mismatch_rebuilds_or_readmits_instead_of_silent_use
test_admission_metadata_from_discovery_index_cannot_authorize_manifest
```

Stress Contract 候選：

- 大量 test assets admission／invalidation 同時發生時，MVE 不得看到 partial manifest 或混合 epoch。
- Admission event storm 必須 coalesce，不得重複建立相同 Verification Subject。
- 大型 manifest validation 不得把完整 asset list 注入 Agent Context，且 token 成本不隨 suite 大小線性成長。

#### 已確認：CIM-MVE-001 Frozen Candidate to Verification Subject

Frozen candidate 只能觸發 verification intake，不能直接開始任意測試。MVE 必須把「哪一份規格、哪一個不可變 candidate、哪一份 TAQG admitted Test Asset Manifest」組合成固定的 verification subject，之後 runner 只能依該 subject 機械執行。

Verification intake 至少綁定：

```text
work_package_id
＋ task_specification_id_and_version
＋ task_specification_digest
＋ frozen_candidate_id
＋ frozen_candidate_manifest_digest
＋ verification_contract_id_and_version
＋ test_asset_manifest_id_and_digest
＋ execution_environment_profile_id_and_version
＋ invalidation_epoch
```

建議狀態流程：

```text
CIM: candidate_frozen → verification_intake_published

MVE: intake_received → subject_validating → verification_subject_ready
                                      └→ subject_rejected／verification_not_ready
```

必要不變量：

- MVE 只能讀取 CIM 發布的 immutable candidate 與 TAQG admitted test assets；不得在建立 subject 時修改 source 或 tests。
- Candidate manifest、任務規格、Verification Contract、test asset manifest 與 environment profile 任一 identity／digest 不符，都不能建立 subject。
- 任務規格中的必要驗收若沒有對應的可執行測試資產，結果是 `verification_not_ready`，不能視為通過或自行刪除該驗收。
- Verification Contract 必須在執行前固定 required suites、stress applicability、threshold、skip／xfail policy 與必要 fixtures；看到測試結果後不得由同一執行者靜默縮減。
- `verification_subject_ready` 只代表可重複的驗證輸入已建立，不代表 pytest 已執行或驗收通過。
- Candidate、規格、Contract、test assets 或 environment profile 之後若改變，舊 subject 必須失效並建立新 identity；不得覆寫舊 subject 冒充同一次驗證。
- System Map 只可協助定位受影響節點與候選 suites，不能決定驗收 authority 或替代任務規格。

### DDH-EO-E2E-003：固定驗證對象後才能執行驗收

**Given**

- CIM 已建立 immutable frozen candidate manifest。
- 任務規格已列出功能驗收與適用的壓力測試要求。
- 對應 pytest、fixtures、configuration 與 profiles 可由無 Agent runner 執行。

**When**

- CIM 發布綁定完整 identity 的 verification intake。
- MVE 核對規格、candidate、Verification Contract、TAQG admitted test assets 與 environment profile。

**Then**

- 全部一致且必要驗收均有可執行覆蓋時，建立 `verification_subject_ready`。
- 缺少必要測試、identity mismatch、stale asset 或規格漂移時，結果為 `verification_not_ready`／`subject_rejected`。
- Runner 後續只能對該固定 subject 執行，不得臨時換 candidate、漏跑 required suites 或降低 threshold。

對應機械測試：

```text
test_verification_subject_binds_exact_frozen_candidate_and_specification
test_verification_subject_rejects_missing_required_acceptance_assets
test_verification_subject_rejects_identity_or_digest_mismatch
test_required_suites_and_thresholds_cannot_change_after_subject_creation
test_subject_is_invalidated_when_candidate_spec_or_test_assets_change
test_system_map_discovery_cannot_replace_specification_authority
```

#### 業務場景覆蓋審視

`PWC-CIM-002` 與 `CIM-MVE-001` 都已有一條完整 Given／When／Then 主流程，以及對應的機械測試名稱；但目前還不能稱為完整的業務場景集。

尚未各自展開成獨立 Given／When／Then 的必要分支：

| Contract | 已有主場景 | 待展開的業務分支 |
|---|---|---|
| PWC-CIM-002 | 主流程與 002A／002B／002C／002D 已確認 | 使用者 baseline 與 Agent delta 混合 |
| CIM-MVE-001 | Frozen candidate、規格與 admitted test assets 一致後建立 verification subject | 必要 pytest 缺失、identity／digest mismatch、subject 建立後 candidate／規格／tests 漂移、System Map 建議與任務規格衝突 |

尚未形成獨立 Stress Contract 的必要壓力場景：

- Freeze request 與大量並行／間接 writes 的競態。
- 多 partitions 同時 draining 時只建立一份穩定 candidate manifest。
- 大量 required suites／test assets 的 subject 組裝與一致性檢查。
- Candidate、specification 與 test assets 高頻 invalidation 時，不得誤用 stale subject。

因此，現況是「功能契約與主業務場景已確認」，但上述失敗分支與壓力場景仍須逐條規格化，才能符合 DDH 先定義功能、業務場景與壓力測試，再反推實作的原則。

### 8.3 Invalidation Bus

完整 Domain Contract 已確認於：

- `invalidation_and_reconciliation_domain_contract.md`
- Contract ID：`DDH-INV-001`

`TAQG-QUAL-003` 已確認 test asset lifecycle 的局部 invalidation slice：

- 施工期間由 mutation inventory 對 product source change 標記 `rerun_required`；不直接使 test semantics stale。
- Spec／test／fixture／helper／contract／schema／toolchain change 觸發 TAQG validity evaluation。
- Product writers quiescent後由 CIM 凍結 product candidate；TAQG 對該 immutable identity 執行正式 validity／disposition，MVE intake 前再核對 identity／digest／epoch。
- TAQG 發布新的 atomic Test Asset Manifest／invalidation epoch；MVE 拒絕 suspect／stale／quarantined／retired assets。
- Invalidation 是自動路由，不增加人工 Checkpoint；只有規格或 quality policy 缺口提升人類。

`DDH-INV-001` 已確認 Domain-wide rules：

- Event 是快速通知，不是 authority；protected transition 前以 current canonical state reconciliation。
- PWC、Context Broker、CIM、TAQG 與 MVE 各自推進 owned local state machine，不建立中央大狀態機。
- At-least-once delivery、consumer idempotency、Work Package／resource generation 局部順序與 bounded coalescing。
- Queue／event 遺失時自動從 current identities 重建，不詢問人類如何修 Harness。
- Raw events 在 required consumers reconciliation 後刪除，不形成永久 freshness／receipt chain。

### 8.4 權責邊界

- PWC 擁有派工與整合排序，不擁有 patch admission 或完成判定。
- CIM 擁有 mutation／candidate integrity，不擁有業務 expected behavior。
- Context Broker 擁有 Context materialization，不擁有讀取安全授權或寫入權。
- TAQG 擁有 test asset quality／admission，不發布產品驗證結果或改變規格。
- MVE 擁有機械驗證執行與結果分類，不修改或 admission test assets。
- Completion Evaluator 依 `DDH-COMP-001` 擁有分層 closure 判定，不修改規格、
  scope、risk policy 或 external-side-effect authority。
- OLE 擁有短期編排學習，不得阻塞一般完成或修改規格／權限／驗收。
- Scope expansion、規格歧義、架構／schema／公開契約與外部副作用提升至 Domain 或獨立高風險流程。

### 8.5 建議下一個討論點

六個原子交接／完成 Contract、pending Ledger profile 與 Operational Telemetry
已確認。下一項確認：

1. Legacy ADAD migration matrix、MVP end-to-end flow 與 phased implementation：
   `legacy_adad_capability_migration_matrix_and_ddh_mvp_plan.md`（Proposed）。
2. Operational lifecycle 已由 `DDH-OPS-001` 確認。
