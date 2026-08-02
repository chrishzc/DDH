# Verification Runner Role Specification

**Canonical role name：** `Verification Runner`  
**歷史名稱／ID：** Mechanical Verification Execution／MVE  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存已確認的無 Agent 驗證執行責任；不授權 runtime 實作  
**拆分來源：** `mechanical_verification_and_test_governance_subsystem_specification.md`

---

## 1. 責任

Verification Runner對immutable Verification Subject執行admitted tool-neutral Verification Assets，包括pytest、language-specific test commands、build／lint／type／schema／security／integration／stress checks，建立可重現runner並機械分類infrastructure、product、suspected asset defect與specification ambiguity。

負責：

- 驗證 Verification Subject identity。
- 確認只引用 TAQG admitted Test Asset Manifest。
- 建立、self-check、修復與切換 runner environment。
- 無 Agent 執行 required pytest／stress suites。
- 發布綁定 `verification_subject_id` 的結構化結果。
- 將 product failure 交給 Domain repair loop。
- 將 suspected test defect 交給 TAQG。

## 2. 不負責

- 不修改或 admission pytest、fixture、threshold、suite selection 或 Test Quality Contract。
- 不生成 pytest／fixture／helper／configuration；寫入 Test Assets 屬於 PWC 管理的施工，draft diagnostic execution 不是正式 MVE acceptance。
- 不修改產品 source。
- 不重新解釋任務規格。
- 不把 System Map 當成驗收 authority。
- 不保存永久 PASS logs；長期 evidence 仍是可重播 pytest 資產。

## 3. 已確認 Contract：TAQG-MVE-001

- 只接受 TAQG 發布的 immutable admitted Test Asset Manifest。
- Draft／candidate／suspect／stale／quarantined／retired assets 不得進入正式 Verification Subject。
- Test asset version 或 invalidation epoch 改變時，舊 subject 必須失效。
- Manifest unavailable 或不一致時結果為 `verification_not_ready`，不能自行漏跑。
- Candidate 已 frozen 但 admission 尚未完成時，MVE 等待 TAQG lifecycle event 並自動續作，不詢問人類。
- Draft tests 不能進入正式 Verification Subject；Test Agent 的 diagnostic run 不具有完成效力。
- Manifest publication 必須 atomic；validation 期間 invalidation 時拒絕舊 epoch 並取得新 manifest。
- Runner incompatible 走 `RC-MVE-004`，不得修改 tests 來配合 runner。

完整 authority 在 TAQG specification。

## 4. 已確認 Contract：CIM-MVE-001 Frozen Candidate to Verification Subject

Verification intake 至少綁定：

```text
work_package_id
＋ task_specification_id_and_version
＋ task_specification_digest
＋ frozen_candidate_id
＋ frozen_candidate_manifest_digest
＋ verification_contract_id_and_version
＋ admitted_test_asset_manifest_id_and_digest
＋ execution_environment_profile_id_and_version
＋ invalidation_epoch
```

狀態：

```text
CIM: candidate_frozen → verification_intake_published

MVE: intake_received → subject_validating → verification_subject_ready
                                     └→ subject_rejected／verification_not_ready
```

必要不變量：

- MVE 只能讀取 immutable candidate，不得在建立 subject 時修改 source 或 tests。
- 任一 identity／digest 不符、required asset 缺失或 stale 時不得建立 subject。
- Subject ready 不代表 pytest 已執行或 PASS。
- Candidate、spec、test asset 或 environment profile 改變時，建立新 subject identity。
- Product candidate 改變只使 admitted／active tests 對新 subject 成為 `not_run`；不能因此把測試語意誤標為 stale。
- Test validity 與 disposition 完整 authority 在 `TAQG-QUAL-003`；MVE 只核對發布的 status、identity、digest 與 invalidation epoch。

## 5. 已確認 Recovery Chain：RC-MVE-004 Runner Environment Failure

- Infrastructure failure 與 product／test failure 必須分離。
- Workspace、environment、cache、resource collision 或 runner crash 由無 Agent recovery 重建。
- Recovery 對完全相同的 Verification Subject 重跑。
- Environment failure 不得要求 Agent 修改產品 source／tests。
- 所有安全 runner routes 耗盡時只輸出一次 `platform_blocked`。

## 6. 已確認 Recovery Chain：RC-DOM-MVE-005 Product Verification Failure

- MVE 先排除 infrastructure 與 suspected test defect，再發布 product Failure Bundle。
- Impact closure 消費 System Map query 並經 live source 確認。
- Verification closure 可以自動擴大，但不授予額外 write scope。
- Candidate 修改後建立新 subject，沿用相同 task specification 與 admitted acceptance。
- Repair／freeze／retest 自動循環，直到 PASS 或需要人類決策邊界改變。

## 7. 已確認 Recovery Chain：RC-MVE-TAQG-006 Test Implementation Defect

- MVE 只能發布 suspected defect bundle，不能修改測試或忽略 failure。
- TAQG admission 新版本前，MVE 繼續把原 admitted version 視為正式資產。
- 新 version admitted 後建立新 Test Asset Manifest 與新 Verification Subject。
- Semantics-preserving repair 自動續作；語意改變或不明時才提升。

## 8. System Map 使用

- Product failure impact closure 消費 failed-node reverse dependencies。
- Suite selection 消費 changed-node／affected-dependent query，但 required acceptance 仍由任務規格與 admitted manifest 決定。
- Query unavailable 時使用 bounded live-source fallback。
- 本 Subsystem 不設計 System Map。

## 9. 無 Agent 與可重播要求

- pytest／fixture／configuration／profile 與 runner interface 在沒有 Agent／LLM service 時可執行。
- Agent 只在 product diagnosis 或 test proposal 階段介入。
- PASS 必須綁定完整 subject identity；不保存歷史 PASS 作為長期 evidence。
- Output 先由機械流程聚類與有界化，避免 Agent token 隨完整 log 線性成長。

## 10. 已確認驗收方向

```text
test_mve_accepts_only_admitted_test_asset_manifest
test_frozen_candidate_and_manifest_identity_are_exactly_bound
test_runner_environment_failure_never_becomes_product_failure
test_product_failure_publishes_bounded_actionable_bundle
test_suspected_test_defect_routes_to_taqg_without_test_mutation
test_candidate_or_test_asset_change_creates_new_subject_identity
test_new_candidate_marks_active_tests_not_run_without_staling_them
test_mve_rejects_suspect_stale_quarantined_and_retired_assets
test_required_verification_runs_without_agent_or_llm_service
test_system_map_query_expands_verification_without_granting_write_scope
```

## 11. 尚未決定

- `MVE-PROTO-001` 已固定 Verification Invocation、Result Envelope 與 Runner
  interface 的最小語義。
- `MVE-VERDICT-001` 已固定 Subject result aggregation、mixed outcome 保存與
  `mechanical_verification_passed` 的必要條件。
- 正式 schema、wire format、transport、serialization、adapter API 與 protocol
  version negotiation 仍未決定。

## 12. 已確認 Contract：MVE-RESULT-001 Observed Result Classification, Impact Assessment and Routing

### 12.1 兩條獨立判定軸

每個 observed result 必須分開產生：

```text
failure_classification
＋ impact_scope_assessment
```

`failure_classification` 回答「發生哪一類失敗」；`impact_scope_assessment` 回答「原本 verification／write scope 是否足以診斷與修復」。知道是 product failure 不代表原 scope 足夠。

### 12.2 Failure Classification

| Classification | Routing |
|---|---|
| `pass` | 繼續完成判定 |
| `product_failure` | `RC-DOM-MVE-005` |
| `test_implementation_defect` | `RC-MVE-TAQG-006` |
| `runner_environment_failure` | `RC-MVE-004` |
| `specification_ambiguity` | 結構化規格決策報告 |
| `mixed_failure` | 保留多個 bundles 與尚未驗證項目，分別路由 |
| `unknown` | Bounded diagnostic plan；不能猜成 PASS／產品 FAIL |

`not_run／blocked` 是 execution state，不得作為 PASS 或產品失敗。

### 12.3 Impact Scope Assessment

| Assessment | 語意／動作 |
|---|---|
| `within_planned_closure` | 在既有 verification／write scope 自動修復 |
| `verification_closure_expanded` | 自動增加原 scope 外 regression；不授予 write permission |
| `write_scope_expansion_required` | 停止越界修改，提出 versioned Work Package scope update |
| `contract_or_architecture_change_required` | 提出 L3／架構或 contract change proposal |
| `behavior_specification_change_required` | Expected behavior 必須改變，提出規格版本更新 |
| `map_live_source_conflict` | 以 live source 作現況證據，納入 closure 並觸發 System Map maintenance |
| `impact_unknown` | 重建 query index／bounded live-source discovery；未封閉前不能完成 |

Task Specification 必須區分兩種修訂：

- 原 expected behavior 已正確，只是允許 write scope 估小：只更新 Work Package／Task Specification 的施工範圍與版本。
- 修復需要改變 expected behavior、schema、公開契約或架構：更新對應 behavioral／architecture specification，並依人類決策邊界核准。

不能因 out-of-scope failure 就自動改寫業務 expected behavior。

### 12.4 System Map Mandatory Query and Consumption

| 時機 | Query／用途 |
|---|---|
| Initial scope planning | selected nodes、dependencies、direct reverse dependents |
| Actual touched resources／diff closure | resource-to-node bindings、changed nodes、affected dependents |
| Product failure | failed scenario nodes、Q2 reverse dependencies、上層 Subsystem／Domain |
| Scope boundary evidence | Q3 cross-boundary affected nodes 與 scope-decision candidates |
| Verification Subject selection | changed／affected nodes 到 admitted test asset bindings |
| Completion | 確認 required impact closure 均已驗證或有規格化 N/A |

只呼叫 System Map query 不算完成。Result Envelope、Failure Bundle、suite selection 與 scope assessment 必須引用並實際消費 `architecture_query_result_id`。

- System Map 是 index，不是 impact／scope／acceptance authority。
- Map query 必須用 actual diff／failed scenario 作輸入，不能只沿用 initial predicted scope。
- Live source／schema／configuration 發現 Map 遺漏或錯誤 relation 時，以現況證據修正 closure，產生 Map maintenance trigger。
- Query unavailable 時依 `RC-DOM-003` 重建；仍不可用時使用 bounded live-source fallback。
- Map 與 live source 都無法封閉影響面時標為 `impact_unknown`，不能假裝只影響原 scope。

### 12.5 Observed Result Envelope

```text
verification_subject_id
＋ invocation_id
＋ admitted_test_asset_ids_and_versions
＋ runner_environment_identity
＋ command_arguments_and_cwd
＋ collection_and_phase_results
＋ exit_code_signal_timeout
＋ bounded_failure_excerpt_and_digest
＋ failure_classification
＋ classification_rule_id_and_version
＋ changed_and_failed_nodes
＋ architecture_query_result_ids
＋ mapped_and_live_discovered_affected_nodes
＋ outside_verification_scope_nodes
＋ outside_write_scope_nodes
＋ impact_scope_assessment
＋ required_specification_update_kind
＋ required_route
```

完整 logs 是短期 artifacts，不全部進入 Agent Context，也不成為永久 Evidence Retention。

### 12.6 Classification and Diagnostic Rules

```text
subject identity validation
→ runner self-check
→ test collection
→ fixture／environment setup
→ test execution
→ oracle evaluation
→ cleanup
→ failure classification
→ System Map／live-source impact assessment
→ route
```

- Valid admitted test 到達 assertion 且 actual 不符固定 oracle，才可分類 product failure。
- Runner 啟動、dependency、permission、workspace 或資源故障分類 environment。
- Pytest／fixture／helper／collection implementation defect 分類 test defect。
- Oracle 無唯一合法來源時分類 specification ambiguity，不能由 Agent補值。
- `unknown` 依固定 budget 執行 subject revalidation、runner self-check、一次 exact replay、phase isolation、approved clean runner 與 bounded probes。
- Mixed failure 不得壓成單一類別；已證明 product failure、environment failure 與未驗證 required tests 分別保存。

### 12.7 業務場景：Scope 估小且規格範圍需要更新

**Given**

- Task Specification 的 write scope 只有 Workspace Subsystem。
- Agent 修改 `PathCanonicalizationStateMachine` 產生的 event。
- Initial scope plan 沒有包含 Reporting。
- System Map Q2 reverse-dependency query 顯示 `RevenueRecognitionProjection` 消費該 event，並由 live source 確認。

**When**

- Workspace verification 觸發實際 diff／failure impact query。
- Reporting regression suite 進入 verification closure 並失敗。

**Then**

- Primary classification 是 `product_failure`。
- `impact_scope_assessment` 不能仍標 `within_planned_closure`。
- Reporting 可以自動加入 verification closure，但沒有 write permission。
- 若 Workspace Subsystem 在既有 event contract 內修正即可，保持原 write scope，自動 repair／retest。
- 若必須修改 Reporting source，輸出 `write_scope_expansion_required`，建立新版 Work Package／Task Specification scope proposal。
- 若必須修改 event schema、公開 contract 或架構，輸出 `contract_or_architecture_change_required`。
- 只有 expected behavior 本身需要改變時，才輸出 `behavior_specification_change_required`；不能把 scope 估錯誤誤稱為業務規格錯誤。
- Failure Bundle 與 suite selection 必須引用並消費相同 `architecture_query_result_id`。

### 12.8 場景：System Map 漏掉依賴

**Given**

- Initial Map 沒有 PathNormalizer → ManifestLoader edge。
- Actual import／event subscription／schema usage 顯示 Reporting 確實依賴修改內容。

**Then**

- `impact_scope_assessment=map_live_source_conflict`。
- Live-discovered Reporting node 仍加入 verification closure。
- 產生 System Map maintenance trigger，但本 Contract 不設計或修改 System Map。
- Map 遺漏不能讓 MVE 縮小 suite，也不能自動授予 Reporting write scope。

### 12.9 Stress Contract

- 高 fanout node 使用 bounded Q2／Q3 與分層 closure，不把整張 graph 注入 Agent Context。
- 大量 failures 先按 scenario／root-cause／affected closure 聚類，但不能漏掉任何 outside-scope node。
- Parallel invocation completion order 不得改變 failure classification 或 scope assessment。
- Map query storm 必須 cache／coalesce exact query identities；不能重用過期 diff／failure inputs。
- Query service failure 自動重建／fallback，routine path 的 Agent token cost 為零。

### 12.10 對應機械測試

```text
test_result_has_independent_failure_and_scope_assessment_axes
test_product_failure_does_not_imply_original_scope_is_sufficient
test_actual_diff_requeries_system_map_instead_of_reusing_initial_scope_only
test_out_of_scope_reverse_dependent_is_added_to_verification_closure
test_expanded_verification_never_grants_write_permission
test_out_of_scope_repair_creates_versioned_scope_update_proposal
test_contract_or_architecture_change_routes_to_l3_decision
test_scope_underestimate_does_not_rewrite_expected_behavior
test_expected_behavior_change_requires_behavioral_specification_update
test_live_source_dependency_overrides_missing_map_edge_for_current_closure
test_map_conflict_triggers_maintenance_without_designing_system_map
test_query_result_must_be_consumed_by_result_bundle_and_suite_selection
test_impact_unknown_cannot_complete_work_package
test_high_fanout_impact_query_is_bounded_and_zero_agent
```

### 12.11 Self-Evolution Boundary

OLE 可以改善 failure clustering、query ordering／cache、bounded excerpts、diagnostic scheduling 與 Context Envelope，但不能修改 classification／impact rules、protected scope、System Map consumption requirements、specification update kinds 或 human decision boundary。

## 13. 已確認 Contract：MVE-EXEC-001 Layer/Risk Execution Profiles and Stress Scheduling

### 13.1 執行階段

| Lane | Input／owner | Completion effect |
|---|---|---|
| `diagnostic_feedback` | 施工 Agent、draft tests、temporary probes | 只供診斷，不是正式 MVE |
| `module_provisional` | Immutable Module lane snapshot＋admitted Module assets | 只判定 `PWC-INTEG-003` lane readiness |
| `subsystem_completion` | Frozen integrated Subsystem candidate | 可完成 Subsystem-scope Work Package |
| `domain／global_acceptance` | 規格要求的 higher-layer subject／closure | 依任務施工層級決定 |
| `external_high_risk` | Release、deployment、真實 DB／network／other side effects | 獨立流程，不由一般 Work Package 跨越 |

Test construction 由 PWC／TAQG 管理；MVE 只對 immutable input 執行 admitted assets。Draft diagnostic PASS、Module provisional PASS 或 Agent self-test 都不能冒充 final completion。

### 13.2 Authority Boundary

TAQG 固定：

```text
required suites
＋ scenario coverage
＋ stress applicability
＋ thresholds／SLO sources
＋ seed／repeat policy
＋ skip／xfail policy
＋ oracle
```

MVE Scheduler 只決定：

```text
ordering
＋ sharding
＋ parallelism
＋ runner placement
＋ cache use
＋ resource allocation
＋ approved fail-fast timing
```

排程、成本或 OLE 建議不能減少 TAQG required set。

### 13.3 Execution Plan

```text
verification_subject_id
＋ required_suite_ids
＋ conditional_suite_triggers
＋ stress_requirements
＋ thresholds
＋ seeds
＋ environment_profiles
＋ shard_plan
＋ ordering_constraints
＋ resource_limits
＋ timeouts
＋ retry_rules
＋ fail_fast_policy
＋ execution_plan_generation
```

- Execution Plan 是 Verification Subject／TAQG Contract 的 derived execution projection，不是新 SSOT。
- 只調整語意等價的 shard、ordering、parallelism 或 runner placement 時，可以建立新 plan generation。
- Suites、thresholds、stress requirements、oracle 或 environment semantics 改變時，必須回 TAQG／規格流程並建立必要的新 subject identity。

### 13.4 Default Scheduling Order

```text
subject identity／runner self-check
→ collection／fixture validation
→ affected Module tests
→ Subsystem business scenarios
→ reverse-dependent regression
→ Domain／Global invariants
→ required concurrency／load／soak／fault injection
```

- 這是預設優先順序，不是強迫序列執行。
- 互不干擾的 suites 可以平行。
- Shared DB、port、filesystem、clock、environment、stub 或 fixture state 必須先建立真正隔離資源，否則機械序列化。
- 不得只靠 prompt 要求 Agent 避免 test interference。

### 13.5 Fail-Fast

- Development feedback 與已知錯誤 candidate 可以 fail-fast，停止尚未開始的高成本 invocations。
- 未執行項目必須標成 `not_run_due_to_fail_fast`，不能改寫為 PASS。
- Candidate repair 後建立新 Verification Subject。
- 最終 candidate 仍須完成全部 required acceptance，包括適用的 load／soak／fault injection。

Fail-fast 只節省已知失敗 candidate 的成本，不能縮減最終完成標準。

### 13.6 Fork-Join Integration

```text
Module provisional subjects
→ PWC-INTEG-003 mechanical Join Barrier
→ deterministic integration
→ actual diff／System Map impact reconciliation
→ frozen integrated candidate
→ formal Subsystem Verification Subject
```

Formal Subsystem plan 包含：

```text
required Module acceptance
＋ Subsystem business scenarios
＋ shared-contract integration
＋ affected reverse-dependent regression
＋ Quality Profile required stress／recovery
```

不同 Module provisional snapshots 的 PASS 不能拼成 integrated PASS；正式 required tests 依 final impact closure 對 integrated candidate 執行。

### 13.7 Cache Rules

可以重用：

- TAQG admission。
- Verification Asset Inventory。
- Dependency／impact closure cache。
- Runner environment。
- 完全相同 Verification Subject 內、identity 完全一致的短期 shard result。

不能重用：

- 不同 candidate 的歷史 PASS。
- Spec／test／fixture／profile 變更前的 result。
- Environment identity 不一致的 performance result。
- Module provisional result 冒充 integrated candidate result。

Work Package 結束後不把 cached PASS 當成長期 Evidence Retention。

### 13.8 Budget Rules

Budget 可以改變：

```text
sharding／parallelism／ordering／cache／batch size／approved sampling implementation
```

Budget 不能改變：

```text
required scenarios／suite／threshold／soak duration／required dataset／required environment semantics
```

所有 approved cost optimizations 耗盡後仍不足：

```text
verification_budget_exhausted
＋ completed_invocations
＋ unverified_requirements
＋ attempted_optimizations
＋ additional_budget_required
```

不得宣告完成；Agent 不能自行降低要求。

### 13.9 System Map Consumption

- Changed nodes → affected suites。
- Reverse dependents → regression closure。
- Shared resources → parallelism constraints。
- Node layer → execution profile。
- Scope 外 affected nodes → new execution-plan generation。

Actual diff／failure 使 closure 改變時，必須重新 query、以 live source 確認並建立新 plan generation。只沿用 initial predicted scope 或只呼叫未消費的 query 都不能完成。

### 13.10 業務場景

**低頻 formatter**

- TAQG 已將 high-concurrency soak 標為有業務理由的 N/A。
- MVE 執行 examples、boundary、negative、determinism，不產生假 soak gap。

**高風險 Workspace Subsystem**

- Module calculations、state-machine scenarios、idempotency／concurrency、Ledger／Reporting regression 與 required load／soak 依 dependency constraints 執行。
- 獨立 suites 可以平行，最終 candidate 必須全部通過。

**昂貴 soak 前快速失敗**

- Subsystem test 先證明產品錯誤，尚未開始的 soak 標為 `not_run_due_to_fail_fast`。
- Repair 後的新 candidate 重跑完整 required plan；舊 candidate 未執行的項目不能沿用。

**Shared database**

- Environment Profile 支援 isolated DB instances 時可以平行。
- 不支援時機械序列化；不能接受不受控共享狀態。

**Scope 外 affected node**

- System Map 新增 Reporting suites 後建立新 plan generation。
- Verification 可以擴張但不授予 Reporting write permission；repair 依 `MVE-RESULT-001` 路由。

### 13.11 Stress Contract

- 五萬個 tests 可以建立 deterministic shard plan。
- 數百 workers 亂序完成仍歸屬正確 subject／plan generation／shard。
- Scheduler crash 後由 subject 與短期 completed-shard identities 重建。
- 慢速 suite 不得永久 starvation。
- Resource usage 不超過 environment profile。
- Log storm 不使 memory、disk 或 Agent Context 無界成長。
- Routine scheduling、sharding、cache validation 與 known recovery 的 Agent token cost 為零。

### 13.12 對應機械測試

```text
test_diagnostic_and_module_provisional_results_cannot_complete_work_package
test_final_subsystem_plan_binds_frozen_integrated_candidate
test_scheduler_cannot_remove_required_suite_or_lower_threshold
test_equivalent_sharding_change_creates_new_plan_generation_without_new_acceptance
test_acceptance_semantics_change_requires_taqg_or_specification_route
test_fail_fast_marks_remaining_tests_not_run_instead_of_pass
test_final_candidate_completes_all_required_stress
test_shared_state_tests_parallelize_only_with_real_isolation
test_module_provisional_pass_cannot_be_reused_as_integrated_pass
test_cross_candidate_pass_cache_is_rejected
test_budget_exhaustion_reports_unverified_requirements_without_quality_reduction
test_system_map_closure_change_creates_new_execution_plan_generation
test_large_parallel_plan_is_deterministic_and_zero_agent
```

### 13.13 Self-Evolution Boundary

OLE 可以改善 suite ordering、shard size、parallelism、cache reuse、resource placement、fail-fast ordering 與 approved runner backend selection，但不能修改 required suite、threshold／SLO、stress applicability、final completion lane、cross-candidate cache prohibition、budget fail-closed rule 或 external high-risk boundary。

## 14. 已確認 Contract：MVE-RUN-001 Runner Environment and Cross-Platform Reproducibility

### 14.1 Environment Identity

每次正式 invocation 至少綁定：

```text
operating_system_and_version
＋ architecture
＋ runtime_and_version
＋ dependency_lock_digest
＋ pytest_and_plugin_versions
＋ locale_timezone_encoding
＋ filesystem_semantics
＋ environment_variable_profile
＋ database_service_versions
＋ schema_fixture_identity
＋ network_mode
＋ isolation_backend
＋ resource_limits
＋ clock_and_random_seed_policy
＋ runner_builder_version
```

Secrets 只保存 reference／digest，不得進入 manifest、log 或 Agent Context。

### 14.2 Capability States

| State | Meaning |
|---|---|
| `configured` | 設定宣告 backend 存在 |
| `available` | Binary／runtime／service 可找到 |
| `self_checked` | 已實際執行機械健康檢查 |
| `ready` | 符合本次 Environment Profile |
| `unhealthy` | 健康檢查或執行中故障 |
| `incompatible` | 可執行但不符合本次 verification semantics |

只有 `ready` 可以正式執行 Verification Subject；configured／available 不等於實際生效。

### 14.3 Runner State Machine

```text
requested
→ provisioning
→ self_checking
→ ready
→ running
→ completed
```

```text
provisioning／self_checking／running
→ unhealthy
→ repairing
→ self_checking
```

```text
repairing
→ fallback_selecting
→ provisioning_equivalent_backend
```

所有 approved routes 耗盡後輸出 `platform_blocked`；此狀態不是產品 FAIL 或 PASS。

### 14.4 Self-Check

正式 pytest 前，Runner 必須機械確認：

- Runtime、dependency、pytest 與 plugin identities。
- Test collection 可執行。
- Candidate read-only／等價不可變隔離。
- Temp、cache、output 可寫且不污染 candidate。
- Required DB／service 是本次 isolated instance。
- Port、filesystem、clock、locale、timezone、encoding 與 network policy。
- Resource limits 可量測。
- Runner 結束後可以清理 descendants。

Self-check 使用框架 own known-good probes，不能依產品 tests 判斷 Runner 健康。

### 14.5 Automatic Recovery

| Failure | Automatic route |
|---|---|
| Dependency／pytest plugin 缺失 | 依 lock／profile 重建 environment |
| Disposable cache 損壞 | 僅清除限定 cache，再重建 |
| Port collision | 新 isolated port／namespace |
| Temp path／cwd 錯誤 | 重新 materialize runner workspace |
| Runner crash | 終止 descendants，重建 instance |
| Disposable DB 污染 | 丟棄 instance，從固定 schema／fixture 重建 |
| Resource exhaustion | 降低 parallelism，不降低 required tests |
| Backend unhealthy | 切換 approved equivalent backend |
| Safe routes exhausted | 單次 `platform_blocked` |

Recovery 不得修改產品／tests、降低 threshold、連到未授權真實 DB／network，或 reset／stash／刪除使用者工作區。

### 14.6 Backend Equivalence

Environment Profile 至少宣告：

```text
backend_equivalence_class
＋ supported_test_kinds
＋ filesystem_semantics
＋ network_semantics
＋ database_semantics
＋ clock_semantics
＋ performance_result_portability
＋ fallback_order
```

- Local venv／container 對純計算 tests 可以在 approved profile 中等價。
- SQLite／MySQL 對 transaction／locking 不預設等價。
- 開發筆電／固定 CI machine 的 performance result 不預設可攜。
- Windows／Linux 的 path／case／process semantics 不預設等價。
- 同一 approved equivalence class 可以自動 fallback，Result 綁定 exact environment identity。
- Environment semantics 改變時，建立新 profile／subject；不得為了 fallback 降低要求。

### 14.7 Cross-Platform Profile

```text
required_platforms
＋ optional_platforms
＋ not_applicable_platforms_with_business_reason
```

必須明確處理 path separator、case sensitivity、line endings、file mode、encoding、locale、timezone、process signals、shell invocation 與 temp semantics。

MVE 不要求所有任務永遠跑所有 OS，也不能只在目前平台 PASS 就宣稱跨平台。

### 14.8 業務場景

**Windows PASS／Linux path-case failure**

- Linux 是 required platform 且 Runner self-check 正常。
- `Config.py`／`config.py` case mismatch 分類為產品 cross-platform failure，不是 environment failure。
- Linux 非 required 時不影響本次 completion，但不能宣稱已驗證 Linux。

**缺少 pytest plugin**

- Collection 前發現 plugin 不存在，分類 environment failure。
- 依 lock 重建並對同一 subject 重跑；不得刪 marker 或修改 test。

**Shared DB 污染**

- Profile 要求 disposable isolated DB。
- Fixture checksum 不符時丟棄並重建；不得連到開發者／production DB。

**Performance environment mismatch**

- Local laptop 可提供功能 feedback，但不能滿足固定 server profile 的 latency evidence。
- 等待／建立 approved performance environment，不用本機 PASS 冒充 SLO PASS。

**Equivalent fallback**

- Local venv 持續 crash，而 container 是純計算 tests 的 approved equivalent backend。
- 自動切換、重跑 self-check，Result 記錄 exact container identity，不詢問人類修 venv。

### 14.9 External Side-Effect Boundary

一般 Runner 只使用 disposable DB、local stub／emulator、isolated filesystem 與明確允許的 loopback resources。真實 network、production DB、credentials、deployment 或其他外部副作用仍屬獨立高風險流程。

### 14.10 Stress Contract

- 數百 parallel runners 不發生 port、DB、temp 或 cache identity collision。
- Crash storm 有界重建，不產生無限 descendants。
- 長時間 soak 結束後不殘留可修改 candidate 的 process／resource。
- Cross-platform matrix results 綁定正確 environment identities。
- Backend fallback 不混用不同 semantics。
- Logs 有界且遮罩 secrets。
- Routine self-check、repair、fallback 與 cleanup 的 Agent token cost 為零。

### 14.11 對應機械測試

```text
test_configured_backend_is_not_ready_until_mechanical_self_check
test_runner_environment_identity_binds_platform_runtime_dependencies_and_semantics
test_runner_mounts_candidate_immutably_and_uses_isolated_outputs
test_missing_plugin_rebuilds_environment_without_test_mutation
test_disposable_db_contamination_rebuilds_without_external_database_access
test_resource_exhaustion_reduces_parallelism_not_required_quality
test_fallback_uses_only_approved_backend_equivalence_class
test_performance_result_cannot_cross_nonportable_environment_identity
test_required_linux_path_case_failure_is_product_compatibility_failure
test_nonrequired_platform_pass_is_not_claimed
test_safe_routes_exhausted_emit_platform_blocked_not_product_failure
test_runner_cleanup_removes_descendants_without_mutating_candidate
test_large_runner_matrix_is_isolated_bounded_and_zero_agent
```

### 14.12 Self-Evolution Boundary

OLE 可以改善 approved backend selection、provisioning order、warm pool、cache placement、resource allocation 與 self-check scheduling，但不能修改 backend equivalence classes、required platforms、environment semantics、performance portability、network／credential policy、external high-risk boundary 或 `platform_blocked` fail-closed conditions。

## 15. 已確認 Contract：MVE-OBS-001 Output Hygiene, Bounded Result Buffer and Failure Clustering

### 15.1 第一原則

正常 pytest／stress execution 不應產生數萬行無結構 output、重複 traceback、每個 shard 重複的 environment dump 或完整 metrics stream。

MVE 必須先在 output source 控制：

```text
quiet structured runner protocol
＋ one result record per invocation
＋ failure-only bounded diagnostics
＋ shared-failure aggregation
＋ source-side metric aggregation
＋ no routine PASS logs
```

Bounded Result Buffer 是防止異常 test／runner／product log storm 破壞流程的最後安全網，不是正常輸出設計。

### 15.2 Output Hygiene Contract

**正常 PASS**

只產生：

```text
invocation identity
＋ outcome
＋ duration
＋ required metrics summary
```

**正常 FAIL**

只產生：

```text
phase
＋ exception／assertion type
＋ bounded assertion diff
＋ selected traceback frames
＋ failure fingerprint
＋ reproduction reference
```

**Stress／load／soak**

- 在 runner／metrics collector 端計算 aggregate、percentiles、resource-growth 與 anomaly windows。
- 不把每次 request／sample 逐筆輸出。
- Threshold breach 只保留有界時間窗與重播所需 seed／workload identity。

**Parallel shards**

- Environment identity、suite metadata 與 shared setup failure 只保存一次 reference。
- 每個 shard 回傳 structured outcome；不得各自列印相同完整 traceback／configuration。

### 15.3 Unexpected Output Classification

| Cause | Classification／route |
|---|---|
| Test／fixture／helper 無界 print 或重複 traceback | `test_output_hygiene_defect` → TAQG repair／admission |
| Runner plugin／reporter 重複或無結構輸出 | `runner_output_hygiene_defect` → RC-MVE-004 |
| 產品在測試中發生異常 log storm | 保留產品 failure facts，依 MVE-RESULT-001 分類產品問題 |
| Stress collector 逐 sample dump | Runner／test profile defect；改用 approved source aggregation |
| Secret 出現在 output | Restricted quarantine＋redaction；不改變 observed PASS／FAIL |

Output 超額本身不能讓產品 FAIL 變 PASS，也不能把尚未執行的 required tests 隱藏。

### 15.4 Tiered Buffer

**Tier 0：本次 lifecycle 必要機械事實**

```text
verification_subject_id
＋ invocation_id
＋ test_asset_id_and_version
＋ shard_and_plan_generation
＋ outcome
＋ exit_code_signal_timeout
＋ failure_phase
＋ classification
＋ impact_scope_assessment
＋ duration
＋ environment_identity
＋ output_digest
＋ truncated_flag
```

Tier 0 不得因 budget 淘汰；無法保存時為 `evidence_incomplete`，不能 PASS。

**Tier 1：有界診斷**

```text
failed_specification_and_scenario
＋ normalized_exception_type
＋ bounded_assertion_diff
＋ selected_stack_frames
＋ failure_fingerprint
＋ affected_nodes
＋ architecture_query_result_id
＋ minimal_reproduction
＋ retryability
```

**Tier 2：異常情況的 raw temporary artifacts**

只在目前 diagnosis／repair／replay 仍需要時短期保留 full stdout／stderr、JUnit、coverage raw data、metrics windows、process dump 或 runner diagnostics。

### 15.5 Result Lifecycle and Retention

```text
collecting
→ sealed
→ classified
→ consumed_by_current_repair_or_completion
→ deletion_eligible
→ deleted
```

Raw artifacts 只有在 Tier 0／1 完整、classification／scope 封閉、沒有 active retry／diagnostic 且目前 repair／completion 已消費後才可刪除。

- OLE 只消費 bounded structured facts，不依賴 raw logs。
- Work Package 完成後長期保留可重播 tests／fixtures／configuration／profile／seed／workload model，不保存歷史 PASS logs。
- 不建立永久 deletion receipt chain。

### 15.6 Failure Fingerprint and Clustering

Fingerprint 至少消費：

```text
failure_classification
＋ failure_phase
＋ specification／scenario IDs
＋ normalized exception type
＋ normalized assertion shape
＋ selected owned stack frames
＋ affected node IDs
＋ environment equivalence class
```

Clustering 只去除診斷重複，不修改原始 invocation outcome。每個 cluster 保存 member IDs／count、representative bounded excerpt、classification、scenarios、nodes、environment identities、outside-scope members 與 mixed-failure members。

不得合併：

- 不同 classification。
- Product／test／environment failures。
- 不同 candidate generation 或 environment semantics。
- Scope 內與 scope expansion required。
- Executed failure 與 not-run／blocked。
- 不同規格場景但碰巧錯誤文字相同的 failures。

### 15.7 Agent Context

主代理預設只取得 blocking cluster summaries、counts、representative excerpt、affected nodes、required route 與 remaining diagnostic budget。

更多內容只能透過 `cluster_id＋requested phase／excerpt type` 有界取得；routine PASS 不啟動 Agent。

### 15.8 Overflow and Truncation

異常 buffer 超額時依序淘汰：

1. PASS stdout／stderr。
2. Duplicate failures 的多份 raw output。
3. 已有 representative 的非代表 traceback。
4. 可重建 intermediate metrics。

永不淘汰 Tier 0、獨立 blocking failure、outside-scope member、mixed-failure member 或未驗證 required test。

Truncation 必須保存 `truncated=true`、原始 byte count／digest（若可得）、retained ranges 與 reason。Outcome 由 structured runner protocol／exit／JUnit channel 判定，不依賴尾端文字。

Tier 0 無法保存時：

```text
result_buffer_failure
→ approved temporary spool
→ bounded backpressure／retry
→ evidence_incomplete／platform_blocked
```

### 15.9 Secret Handling

Output 進入一般 buffer／Agent Context 前先經 secret reference redaction、environment masking、credential pattern filter 與 sensitive-test-data policy。

無法安全遮罩時，raw artifact 進 restricted quarantine；一般 Agent只取得無秘密的 classification／reason。遮罩失敗不改變 PASS／FAIL。

### 15.10 業務場景

**共享 fixture 異常**

- Shared fixture 造成大量 tests 同時失敗。
- Source-side reporter 先產生一個 setup failure reference，各 invocation 只記結構化 member outcome。
- 聚類為一個 test defect，不輸出一萬份 traceback。

**Mixed failure**

- Workspace assertions 產品失敗，同時 runner crash 使其他 required tests 未執行。
- 分開保存 product clusters、environment cluster 與 blocked／not-run items，不能全部稱為 DB failure。

**Scope 外節點**

- PathNormalizer／ManifestLoader 出現相似 exception，但 ManifestLoader 在 write scope 外。
- Outside-scope member 不得被純 PathNormalizer cluster 隱藏；依 `MVE-RESULT-001` 路由。

**Soak metrics**

- Collector source-side 聚合 percentiles、growth 與 anomaly windows。
- Raw samples 不逐筆輸出；只有 threshold breach window 短期保留。

**Credential leakage**

- Failure output含 DB credential 時先 quarantine／redact，Agent只取得安全摘要。

### 15.11 Artifact Budgets

```text
bytes_per_invocation
＋ bytes_per_shard
＋ bytes_per_subject
＋ maximum_failure_clusters
＋ representative_excerpt_budget
＋ raw_artifact_retention_window
＋ agent_context_budget
＋ restricted_artifact_budget
```

Budget 只控制異常保存與摘要方式，不能決定 test execution、PASS／FAIL 或 required coverage。

### 15.12 Stress Contract

- 正常 profile 下 output 量與 invocation／failure clusters 成比例，不與內部 log statements 線性成長。
- 百萬行異常 output 下 memory／disk 仍有界。
- 大量相同 failures 共用 bounded representation，但保留完整 member identities／counts。
- 大量真正不同 failures 不因 cluster 上限消失；Tier 0 分批保存與處理。
- Parallel shard arrival order 不改變 cluster identity。
- Buffer crash／restart 不把 partial result 標 completed。
- Secret storm 不洩漏到 Agent Context。
- Routine aggregation、redaction、fingerprinting 與 clustering 的 Agent token cost 為零。

### 15.13 對應機械測試

```text
test_normal_pass_emits_structured_summary_without_routine_log
test_normal_failure_emits_one_bounded_diagnostic_record
test_stress_metrics_are_aggregated_at_source
test_parallel_shards_reference_shared_setup_failure_without_duplicate_tracebacks
test_unbounded_test_output_routes_to_taqg_quality_repair
test_runner_reporter_log_storm_routes_to_runner_recovery
test_product_log_storm_preserves_product_failure_classification
test_tier_zero_facts_cannot_be_evicted
test_clustering_never_merges_mixed_or_outside_scope_failures
test_truncation_cannot_change_outcome
test_buffer_failure_becomes_evidence_incomplete_not_pass
test_raw_artifacts_delete_after_current_consumers_finish
test_secret_output_is_quarantined_and_not_injected_into_agent_context
test_abnormal_million_line_output_remains_bounded_and_zero_agent
```

### 15.14 Self-Evolution Boundary

OLE 可以改善 fingerprint normalization implementation、cluster order、representative excerpt、compression、buffer placement 與 Context summary，但不能修改 Output Hygiene minimum、Tier 0 fields、failure separation、outside-scope／mixed preservation、truncation semantics、secret policy、retention eligibility 或 `evidence_incomplete` fail-closed conditions。

## 16. 已確認 Contract：MVE-PROTO-001 Verification Invocation and Runner Result Protocol

### 16.1 第一原則

MVE 不得依賴自由格式 stdout／stderr 判定正式 PASS、FAIL、timeout、tool error
或 execution completeness。Pytest、stress、load 與 soak runner 必須透過
runner-neutral 的結構化協定，對每次 invocation 回傳一份可驗證的 terminal
result。

本 Contract 固定跨 Subsystem 所需語義，不固定 JSON、JSONL、JUnit、pipe、
檔案、RPC 或特定 runner API。

### 16.2 Verification Invocation 最小語義

每次 invocation 至少綁定：

```text
verification_subject_identity
＋ invocation_identity
＋ execution_plan_generation
＋ selected_suite／test_asset references
＋ shard identity and total partition
＋ runner／environment profile identity
＋ execution budget／deadline
＋ output／metric contract reference
＋ attempt identity
```

完整 test list、environment details 與 profile 內容可以透過 immutable references
取得，不要求複製進每個 envelope。Invocation 不能擴大 Verification Subject、
改寫 required suites、thresholds、skip／xfail policy 或外部副作用權限。

### 16.3 Runner Result 最小語義

每次 invocation 最多產生一份 current terminal result，至少表達：

```text
subject／invocation／plan／shard identity
＋ execution terminal state
＋ executed／passed／failed／skipped／not_run counts
＋ completeness
＋ process facts: exit／signal／timeout／cancellation
＋ bounded failure references／clusters
＋ aggregate metrics and threshold observations
＋ environment identity
＋ output truncation／digest metadata
＋ started／finished duration facts
```

Execution terminal state 至少可區分：

- `passed`
- `failed`
- `timeout`
- `tool_error`
- `cancelled`
- `incomplete`

確切 enum 名稱仍可在正式 schema 設計時調整，但不得合併上述語義差異。
Product／test／specification／environment classification 與 impact routing 由
MVE 依 `MVE-RESULT-001` 判定；Runner 只能回報觀測事實。

### 16.4 Protocol State and Integrity

概念狀態：

```text
planned → dispatched → running → terminal_result_sealed
                             └→ incomplete／protocol_error
```

必要不變量：

- Subject、plan、shard、runner 或 environment identity 不符的 result 不得被消費。
- Duplicate／late delivery 必須 idempotent；不得重複計入或覆蓋不同 terminal fact。
- Out-of-order delivery 可以等待有界 reconciliation，但不能把 partial result 當 PASS。
- Runner crash、missing terminal record、corrupt envelope 或 completeness unknown
  一律不得完成 required verification。
- Exit code、JUnit 或 stdout 可以是 adapter 的輸入證據，但正式 MVE outcome
  來自驗證後的 structured result，而不是文字尾端。
- Protocol failure 走 runner recovery；不能變成 product failure，也不能要求
  Agent 修改產品或測試來配合工具。

### 16.5 Authority Boundary

Runner／adapter 不得：

- 改變 required suites、thresholds、oracle、skip／xfail policy。
- 自行刪除或忽略 failed／not-run tests。
- 擴大 write scope 或 architecture scope。
- 把 tool error、timeout、cancelled 或 incomplete 宣告為 PASS。
- 核准 external side effect 或決定是否需要人類決策。

MVE 可以依已確認 policy 調整 ordering、sharding、parallelism、backend、
bounded retry 與聚合方式，但不能改變固定驗收。

### 16.6 業務場景

**三個 Module 的非同步驗證**

- Module A、B、C 平行施工並分別執行 admitted Module pytest。
- A、B 的所有 shards 回傳完整 PASS。
- C 的一個 shard 回傳 assertion failure，另一個 shard timeout。
- MVE 保留 assertion failure，只對 timeout shard 走 runner recovery。
- C 尚未得到完整結果前不得進入 Subsystem Join；A、B 不必無條件全部重跑。
- C 修復並完成後，整合 candidate 仍依 `PWC-INTEG-003` 執行完整 Subsystem
  scenarios、stress 與 affected regressions。

**巨大 output 但正式結果完整**

- Test 產生異常大量 stdout，但 adapter 已取得完整 structured FAIL。
- Output 依 `MVE-OBS-001` 截斷、聚類與路由 hygiene defect；正式 FAIL 不因
  最後一段文字遺失而改變。

**Runner 死亡只留下部分結果**

- Process 已執行部分 tests 後死亡，沒有 terminal sealed result。
- MVE 標記 incomplete，依 `RC-MVE-004` 對相同 subject／shard 安全重試。
- 已執行部分不能拼接成正式 PASS，也不詢問人類如何修 runner。

### 16.7 Result Lifecycle and Retention

Invocation／Result Envelopes 是目前編排、診斷、repair 與 completion 使用的
短期 runtime artifacts：

```text
produced
→ integrity_validated
→ classified／consumed
→ deletion_eligible
→ deleted
```

- Work Package 結束後不把歷史 PASS envelope、runner logs 或完整 Invocation
  Ledger 當作永久 Evidence Retention。
- 長期保留的仍是可重播 pytest、fixtures、configuration、profiles、seeds 與
  workload models。
- OLE 只能消費有界、結構化結果；其消化與刪除規則依 OLE／Attempt Ledger
  retention contract，不反向建立永久 protocol receipt chain。

### 16.8 Stress Contract

- 數萬 tests、數百 shards 下，protocol processing 不需 Agent／LLM，且 metadata
  與 aggregate results 有界。
- 大量相同 fixture failures 共享 failure reference，但完整保存 member identities
  與 executed／not-run counts。
- Result 重複、亂序、遲到、部分寫入或 process crash 不改變唯一 terminal outcome。
- Candidate／subject／plan generation 高頻變更時，舊 result 無法污染 current run。
- Metrics stream 在 source side 聚合；不得逐 sample 注入 Result Envelope。
- stdout／stderr 達異常規模時，structured terminal fact 仍可獨立驗證。
- Protocol adapter crash storm 走 bounded recovery，不形成無限 retry 或人工
  Checkpoint。
- Routine protocol encode、validate、deduplicate、aggregate 與 retention 的
  Agent token cost 為零。

### 16.9 對應機械測試

```text
test_runner_outcome_never_depends_on_free_form_output_tail
test_invocation_binds_exact_subject_plan_shard_runner_and_environment
test_result_identity_mismatch_is_rejected_without_product_classification
test_duplicate_and_late_results_are_idempotent
test_out_of_order_partial_results_cannot_complete_verification
test_missing_or_corrupt_terminal_result_is_incomplete_not_pass
test_tool_error_timeout_and_cancelled_remain_distinct
test_runner_cannot_change_required_suite_threshold_or_skip_policy
test_timeout_shard_recovers_without_erasing_independent_product_failure
test_large_output_truncation_cannot_change_structured_outcome
test_large_parallel_protocol_processing_is_bounded_and_zero_agent
test_protocol_artifacts_delete_after_current_consumers_finish
```

### 16.10 尚未固定與 Self-Evolution Boundary

尚未固定：

- serialization／transport；
- exact field names and enums；
- schema registry／version negotiation；
- pytest adapter、JUnit adapter 或 stress runner API；
- local file、pipe、message channel 或 RPC 選型。

OLE 可以改善 adapter selection、serialization efficiency、batching、
compression、delivery order 與 retry scheduling，但不能修改最小 identity、
terminal-state distinctions、completeness、authority boundary、fail-closed
conditions 或 retention semantics。

## 17. 已確認 Contract：MVE-VERDICT-001 Subject Result Aggregation and Terminal Verdict

### 17.1 第一原則

單一 invocation、shard、suite、layer 或 platform 的 PASS 不能代表整個
Verification Subject PASS。MVE 只能依該 immutable Subject 固定的 required
result universe，機械聚合出 Subject verdict。

Required result universe 包含：

```text
required Module suites
＋ required Subsystem／Domain／Global scenarios
＋ affected regressions
＋ applicable stress／load／soak profiles
＋ required platform matrix
＋ fixed conditional-suite rules and triggered suites
```

System Map 可以在 Subject 建立前協助產生 affected-suite 候選，但不能在聚合
階段刪除 required acceptance。若 actual impact、candidate、規格、test assets、
environment profile 或 invalidation epoch 改變，舊 Subject 必須 invalidated，
不能偷偷改寫其 required result universe。

### 17.2 Verdict 的兩條獨立軸

Mixed outcomes 不得被單一字串隱藏。Subject verdict 至少分開表達：

```text
acceptance_outcome
＋ verification_completeness
＋ blocking／failure issue set
```

`acceptance_outcome` 的必要語義：

- `passed`：所有 required observed behavior 均通過。
- `failed`：至少一個 required product behavior 已確認不符合固定規格。
- `undetermined`：尚無法對產品 acceptance 作出正式判定。

`verification_completeness` 的必要語義：

- `complete`：所有 required results 均已完整終結並被聚合。
- `incomplete`：required result pending、missing、not-run 或尚未回傳。
- `blocked`：必要 runner、environment、test asset 或資源問題在安全復原路徑
  耗盡後仍使驗證無法完成。
- `invalidated`：Subject、candidate、specification、test assets、plan 或
  environment identity 已不再 current。

確切 enum 與欄位名稱仍可在正式 schema 設計時調整，但不得把這兩條軸合併
而遺失 mixed outcome。例如已確認 product failure 且另一 required platform
blocked 時，必須同時保存 `failed＋blocked`，不能只報其中一個。

### 17.3 `mechanical_verification_passed` 必要條件

只有下列條件全部成立時，MVE 才能發布：

```text
acceptance_outcome = passed
verification_completeness = complete
subject_currentness = current
```

並且：

1. 所有 required suites、shards、layers 與 platforms 都有 identity-matched、
   integrity-validated 的 terminal result。
2. 所有 required results 通過。
3. 所有 fixed conditional rules 已完成 applicability 判定；被觸發 suites
   已執行並通過。
4. 沒有 required test 被意外 skip、漏跑、截斷、cancelled 或標為 `not_run`。
5. 沒有未封閉的 product failure、tool failure、test defect、specification
   ambiguity 或 impact scope。
6. 聚合使用固定 Verification Contract；結果出現後沒有降低 threshold、
   required platform、suite、oracle 或 skip／xfail policy。

通過比例、歷史 PASS、Module provisional PASS、optional suite PASS 或 Agent
claim 都不能替代上述 closure。

### 17.4 Non-pass Aggregation and Routing

| Observed closure | Subject aggregation | 自動下一步 |
|---|---|---|
| Required product failure 已確認，其餘因 fail-fast not-run | `failed＋incomplete` | 依 `RC-DOM-MVE-005` repair；新 candidate 建立新 Subject |
| Product failure 與 required platform blocker 同時存在 | `failed＋blocked` | 分別保留 product repair 與 runner／platform blocker |
| 無 product verdict，required shard timeout 且 recovery 尚有路徑 | `undetermined＋incomplete` | 依 `RC-MVE-004` 自動重試 |
| 所有安全 runner routes 耗盡 | `undetermined＋blocked` | 發布一次 bounded blocker，不宣稱 product failure |
| Subject 聚合中發生 identity／epoch 變更 | `undetermined＋invalidated` | 拒絕舊結果，建立 current Subject |
| 全部 required results current、complete、passed | `passed＋complete` | 發布 `mechanical_verification_passed` |

Optional／informational suites 是否影響 verdict 必須在固定 profile 中事先定義；
MVE 不能在看到 failure 後臨時把 required 改成 optional。Optional unavailable
可以回報但不阻擋 PASS，前提是它確實在固定 Contract 中為 optional。

### 17.5 State and Reconciliation

概念狀態：

```text
collecting
→ reconciling_required_result_universe
→ terminal_nonpass／mechanical_verification_passed
                         └→ invalidated
```

必要不變量：

- Result arrival order 不影響相同輸入的聚合結果。
- Duplicate／late results 依 invocation identity idempotent。
- 舊 generation、舊 Subject 或不同 platform identity 的 PASS 不能污染 current
  Subject。
- Aggregator restart 後可以從 current structured results 與 immutable Subject
  重建，不需要 Agent 閱讀 logs。
- Conditional suite trigger 是固定規則的執行結果，不是 MVE 臨時新增驗收。
- Triggered required suite 未完成時不能 PASS。
- Invalidation 優先阻止 PASS publication；已發布但尚未被上層消費的 stale verdict
  不能完成目前流程。

### 17.6 業務場景

**Workspace Subsystem 的 mixed platform results**

- 三個 Module pytest 與 workspace 狀態機 scenario 已通過。
- 500 個 affected regressions 中一個 shard timeout。
- Required Linux profile 尚未完成。
- Optional Windows profile unavailable。
- MVE 先得到 `undetermined＋incomplete`，只對 timeout shard 走 recovery；
  optional Windows 不阻擋。
- Linux profile 最後出現路徑 canonicalization 錯誤時，聚合為 `failed＋complete`；若 Linux
  runner 安全路徑耗盡，則為 `undetermined＋blocked`。
- 只有 regression recovery、required Linux 與所有其他 required results
  全部通過後，才發布 `mechanical_verification_passed`。

**Fail-fast 不冒充完整驗證**

- 第一個 Domain scenario 已確認 product failure，因此 MVE 停止低價值後續
  invocations，其餘 required items 標 `not_run`。
- Subject 可以發布 `failed＋incomplete` 供 repair loop 使用，但不能宣稱完整
  acceptance run 已執行。
- 修復後的新 candidate 建立新 Subject；final candidate 必須完成全部 required
  acceptance。

### 17.7 Completion Boundary

`mechanical_verification_passed` 只證明一個 immutable Verification Subject 的
required mechanical verification 已完整通過。它不等於：

- Work Package `completed`；
- `subsystem_integrated`；
- `domain_accepted`；
- `release_candidate`；
- deployment／external side effect approved。

上層 completion contract 必須另外核對 task specification closure、scope／diff
closure、未處理 exceptions、必要人工決策與該層級的 acceptance。MVE 無權發布
上述上層狀態。

### 17.8 Result Lifecycle and Retention

Subject verdict 只保留到目前 repair／completion consumer 已可靠消費，之後依
retention policy 刪除：

```text
aggregated
→ published
→ consumed_by_current_transition
→ deletion_eligible
→ deleted
```

不永久保存歷史 PASS verdict、完整 invocation history 或 sealing receipts。
長期 Evidence Retention 仍是可重播 pytest、fixtures、configuration、profiles、
seeds 與 workload models。

### 17.9 Stress Contract

- 數萬 tests、數百 shards、layers 與 platforms 亂序完成時，聚合結果 deterministic。
- 大量 duplicate／late results 不重複計數，也不覆蓋 current terminal fact。
- 聚合期間高頻 invalidation 時，舊 Subject 無法發布或污染 current PASS。
- Required conditional suite 在執行中被觸發時，PASS publication 等待其 closure。
- 同時存在 product failure、timeout、not-run、optional unavailable 與
  environment blocker 時，所有獨立 issue 都被保存。
- Aggregator crash／restart 從 current structured facts 重建，不依賴 raw logs。
- Event storm 可以 coalesce，但不能漏掉 current required result 或 invalidation。
- Routine aggregation、reconciliation、deduplication 與 verdict publication
  的 Agent token cost 為零。

### 17.10 對應機械測試

```text
test_single_invocation_or_module_pass_cannot_complete_subject
test_subject_pass_requires_all_current_required_results
test_required_not_run_or_unexpected_skip_prevents_pass
test_triggered_conditional_suite_must_complete_before_pass
test_optional_unavailable_follows_fixed_profile_without_dynamic_downgrade
test_product_failure_and_platform_blocker_are_both_preserved
test_fail_fast_failure_remains_incomplete_until_new_subject_full_run
test_old_subject_or_generation_pass_cannot_pollute_current_verdict
test_invalidation_racing_pass_publication_prevents_stale_completion
test_duplicate_late_and_out_of_order_results_aggregate_idempotently
test_aggregator_restart_rebuilds_from_structured_current_results
test_mechanical_verification_passed_cannot_publish_work_package_or_domain_state
test_large_result_matrix_aggregation_is_deterministic_bounded_and_zero_agent
test_subject_verdict_deletes_after_current_transition_consumes_it
```

### 17.11 Self-Evolution Boundary

OLE 可以改善 aggregation order、incremental indexing、coalescing、cache、
parallel reduction 與 summary representation，但不能修改 required result
universe、兩軸 verdict semantics、PASS closure、conditional applicability、
required／optional profile、invalidation precedence、completion boundary 或
retention semantics。

## 18. 已確認 Amendment：Adaptive Bounded Timeout

固定短秒數不是timeout contract。Verification Runner必須分離：

- Specification-owned business performance threshold；
- mechanically planned suite／shard execution deadline；
- no-progress／hang deadline；
- process termination與output-drain grace。

Execution Planner在執行前依declared duration、mechanical p95、pytest collection、
shard／platform／isolation profile、approved safety factor與Work Package ceiling
固定Execution Plan generation。估算超出ceiling時回報
`verification_plan_not_ready`，不得先執行到timeout。

Timeout首先是infrastructure／execution incomplete fact，不直接等於product
failure。只有new plan、environment、shard plan或其他approved new information
才能retry；在既有budget內可自動調整，增加user budget才提升人類。主Agent、
Test Auditor與Learning Steward均不能因測試失敗自行延長deadline或改business
performance threshold。

平台驗收用語採「Windows＋至少一個Unix-like平台（MVP預設Linux）」；更精確的
POSIX API差異留在platform adapter specification。

對應必要場景：

```text
test_normal_sixty_second_suite_is_not_killed_by_legacy_thirty_second_default
test_hung_test_uses_no_progress_deadline_not_unbounded_suite_extension
test_estimated_runtime_above_work_package_ceiling_fails_before_execution
test_outer_deadline_reserves_process_termination_and_output_drain_grace
test_timeout_replan_requires_new_mechanical_information_and_budget
test_runner_timeout_cannot_change_business_performance_threshold
```
