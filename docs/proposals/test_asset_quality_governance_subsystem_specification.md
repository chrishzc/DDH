# Test Auditor Role Specification

**Canonical role name：** `Test Auditor`  
**歷史名稱／ID：** Test Asset Quality Governance／TAQG  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存已確認的tool-neutral Verification Asset品質治理責任；不授權 runtime 實作  
**拆分來源：** `mechanical_verification_and_test_governance_subsystem_specification.md`

---

## 1. 責任

Test Auditor確保pytest與其他CI-style checks、fixture／helper／configuration／profile在成為正式acceptance asset前，忠實對應任務規格、能偵測錯誤、穩定可重播，且未被Agent放寬。pytest是Python reference adapter，不是必要tool。

負責：

- 從任務規格編譯 Test Quality Contract。
- 管理 specification／scenario／test／fixture／profile mapping。
- 分別管理 admission、semantic validity 與 candidate execution 三條狀態軸；`superseded_by` 是版本關係，不再把 `archived` 當成正式驗收狀態。
- Mechanical Acceptance Guard。
- Independent Test Critic orchestration。
- Mutation、known-bad、property／metamorphic、determinism 與 isolation admission。
- Test repair proposal、invalidation 與新版本 admission。
- 產生 immutable Test Asset Manifest 交給 MVE。

## 2. 不負責

- 不執行產品 candidate 的正式 Verification Subject。
- 不發布產品 PASS／FAIL。
- 不修改產品 source。
- 不把 Test Agent 撰寫 pytest／fixture／helper／configuration 的活動誤稱為 verification；這些是受 PWC write partition 管理的 Test Asset 施工。
- 不決定任務規格、expected behavior、write scope 或外部副作用。
- 不設計 System Map；只消費其 impact query。

## 3. 已確認品質模型

| 品質軸 | 核心證據 |
|---|---|
| Semantic fidelity | 固定 specification／scenario mapping、oracle source、Independent Critic |
| Fault sensitivity | mutation、known-bad、property／metamorphic、negative／boundary probes |
| Execution reliability | isolation、repeat、order randomization、seed control、flaky detection |
| Lifecycle validity | System Map impact query、live-source verification、invalidation／stale rules |

四軸分別判定，不壓成單一總分。Code coverage、pytest PASS、測試數量或 Critic 評語都不能單獨 admission。

Decision 0020進一步固定：verification使用`Static／Module／Subsystem／Domain／
Global` scope layer加上independent quality add-ons；既有V0～V3只作歷史alias。
Scope layer不自動觸發所有high-cost stress／mutation／Critic requirements。

## 4. Test Quality Contract

Test Quality Contract 由任務規格編譯，不是新的 SSOT：

```text
task_specification_id_and_version
＋ target_layer_and_node_ids
＋ required_scenario_ids
＋ oracle_sources
＋ required_case_classes
＋ property_or_invariant_requirements
＋ mutation_profile_and_threshold
＋ determinism_profile
＋ isolation_requirements
＋ stress_applicability
＋ critic_profile
＋ invalidation_triggers
＋ execution_cost_budget
```

品質強度依 Module／Subsystem／Domain／Global 與風險調整，不採全專案單一門檻。

## 5. Test Asset Admission

```text
fixed specification and scenarios
→ compile Test Quality Contract
→ Test Agent implements draft pytest
→ collect／lint／marker validation
→ mechanical acceptance weakening guard
→ independent Test Critic
→ scenario replay
→ mutation／known-bad／property probes
→ determinism／isolation checks
→ admitted Test Asset Manifest
```

必要不變量：

- Test Agent 只能提出資產，不能自行 admission。
- Implementation Agent 的 unit／diagnostic tests 不能取代 protected acceptance。
- Draft Test Asset 可以在產品施工期間平行撰寫與 diagnostic run，但正式完成只能使用 writers quiescent 後 admitted 的 immutable version。
- Expected behavior、threshold、scenario boundary、required suite、skip／xfail 的改變不是一般 test repair。
- Critic prompt 不是機械 authority；admission 必須有固定規格與可重播證據。
- Required test flaky 時不得作為 PASS gate；沒有等價 admitted coverage 時 verification 為 `not_ready`。
- Quality metadata 嵌入 pytest／fixture／configuration／profile，不另存歷史 PASS logs。

## 6. 已確認 Contract：TAQG-MVE-001 Admitted Test Asset Handoff

TAQG 只向 MVE 發布 immutable admitted manifest：

```text
task_specification_id_and_version
＋ test_quality_contract_id_and_version
＋ test_asset_manifest_id_and_digest
＋ admitted_asset_ids_and_versions
＋ required_scenario_mapping
＋ execution_profile_ids_and_versions
＋ invalidation_epoch
```

狀態：

```text
TAQG: draft → candidate → admission_validating → admitted
                                      └→ rejected／quarantined

MVE: manifest_received → manifest_validating → manifest_usable
                                           └→ manifest_rejected
```

必要不變量：

- MVE 不得把 draft／candidate asset 用於正式 acceptance。
- Manifest identity／digest／invalidation epoch 不符時必須拒絕。
- 新 test asset version 不覆寫舊 Verification Subject；MVE 必須建立新 subject。
- MVE 只能回報 suspected test defect，不能修改或 admission test asset。
- Handoff 是機械流程，不增加人工 Checkpoint。

Machine routing：

| Result | TAQG 責任 |
|---|---|
| `manifest_not_yet_admitted` | 完成既有 admission；不建立人工核准 |
| `manifest_rejected_or_quarantined` | 自動建立 Test Repair work item |
| `manifest_stale_or_superseded` | 發布最新 admitted version 或重新 admission |
| `asset_missing_or_digest_mismatch` | 重建 derived manifest；內容改變時建立新 candidate version |
| `required_scenario_unmapped` | 撤回有缺陷 manifest，修復 mapping 並重跑 admission |
| `invalidation_during_validation` | 發布新 epoch，讓 MVE 原子重試 |

業務場景與 Stress Contract authority 位於 Domain overview。

## 7. 已確認 Recovery Chain：RC-MVE-TAQG-006

Test implementation defect repair flow 尚待逐項確認。最低邊界：

- Repair proposer 與 admission execution identity 分離。
- Mechanical guard 阻擋 assertion deletion、threshold lowering、fixture shrinking、case removal、skip／xfail 與 suite exclusion。
- Independent Critic、scenario replay 與 mutation probes 通過後，才能 admission 新版本。
- Critic unavailable 時不能降級成 proposer 自批。
- Acceptance semantics 不變時自動續作；語意改變或不明時才進入人類決策。

## 8. System Map 使用

- Source／contract／dependency 改變時，消費 `SMQ-001` affected-node query 建立 test invalidation candidate。
- System Map 只提供 affected tests 候選；任務規格與 live source 決定實際 stale closure。
- Query result 未被消費或被當成 authority 時，admission contract 失敗並自動重查／fallback。
- 本 Subsystem 不設計 System Map schema、index 或 query engine。

## 9. 已確認驗收方向

```text
test_every_required_scenario_has_admitted_test_mapping
test_orphan_acceptance_asset_is_rejected_or_classified_as_diagnostic
test_acceptance_weakening_changes_are_mechanically_rejected
test_mutation_probe_detects_weakened_test_asset
test_required_suite_meets_selected_determinism_profile
test_stale_test_asset_cannot_enter_new_verification_subject
test_new_test_asset_version_requires_new_manifest_identity
test_quality_admission_mechanics_run_without_agent_or_llm_service
```

## 10. 尚未決定

- 正式資料模型與 test asset 儲存路徑。
- Layer／risk-specific mutation、property、repeat、randomization 與 stress profiles。
- Critic model isolation、成本預算與 fallback。
- Hidden／holdout probes 與可重播 Evidence Retention 的相容方式。
- Equivalent mutants 與外部依賴 tests 的處理。
- Quality health check 觸發與批次策略。

## 11. 已確認 Contract：TAQG-QUAL-001 Test Quality Applicability

### 11.1 目的

測試品質強度必須依業務需求、架構層級、影響面與風險調整。不得對所有節點套用同一套最高成本檢查，也不得讓 Agent 以「成本太高」為由，在看到失敗後自行降低已固定的品質要求。

測試品質不另創一套模糊風險分數，直接沿用 Work Package 的 L0–L3 Gate 作基線，再依可機械判定的業務／架構 facts 增加品質維度。

Draft 編譯期間可以出現：

```text
required
conditional
not_applicable_with_business_reason
```

但 `conditional` 只是等待 fact 的暫態狀態。Test Quality Contract 在 admission 前必須全部解析成：

```text
required
not_applicable_with_business_reason
```

#### 11.1.1 L0–L3 品質基線

| Gate | 明確情況 | Test Quality 基線 |
|---|---|---|
| L0 | 文件、非治理資產、純整理，不改變 runtime behavior | 文件格式／連結／產物驗證；一般產品 pytest `not_applicable`，除非文件本身是可執行規格或生成輸入 |
| L1 | 核准架構內、單一 Module、無公開契約變更、無共享可變狀態、影響可局部封閉 | 規格 examples、happy／negative／boundary、determinism；核心決策邏輯 mutation sample |
| L2 | 核准架構內，但涉及 Subsystem／Domain 業務流程、共享狀態、跨 Module interaction、confirmed reverse dependents、concurrency／recovery／重要資料一致性 | 完整業務場景、state transition、interaction／regression、property／invariant、mutation、適用的 concurrency／recovery／stress |
| L3 | 架構、schema、公開介面、跨 Subsystem contract、不可逆或外部高風險操作 | 人類先核准變更；施工後除 L2 外，依變更類型加入 compatibility、migration、rollback、fault injection、external-effect isolation 與更高層 acceptance |

**Gate 判定優先於檔案數與程式複雜度。** 一個只有十行但修改公開 schema 的變更仍是 L3；大型純函式內部重構若能局部封閉，仍可維持 L1。

#### 11.1.2 維度 Trigger Table

下列 trigger 任一成立，對應維度即為 `required`；全部不成立且 approved rule 允許排除時，才可標為 `not_applicable_with_business_reason`。

| 品質維度 | `required` 的明確 triggers |
|---|---|
| Negative／boundary | 任何 runtime behavior change；規格有 invalid input、上限／下限、空值、錯誤狀態或例外 |
| State transition | 節點保存狀態，或規格含狀態、生命週期、重試、取消、恢復、順序 |
| Idempotency／duplicate | 規格允許 retry／重送，或 live source 使用 queue、event、job、webhook、batch replay |
| Concurrency／race | 預期同時執行大於一，或存在 shared mutable state、lock、transaction、async worker、parallel writer |
| Property／invariant | 輸入空間不能靠有限 examples 完整列舉，且規格存在守恆、單調性、排序、唯一性、可逆性等 invariant |
| Mutation／known-bad | 存在業務分支、計算、狀態轉移、權限、資料轉換或 failure handling；純宣告／無行為 wrapper 才可能排除 |
| Dependency regression | System Map 查到 confirmed reverse dependents，且 live source 確認契約／資料／控制流相依 |
| Load／burst | 任務規格或 approved profile 提供 request rate、batch size、資料量、burst 或 latency requirement |
| Soak | daemon／scheduler／長連線／cache／resource pool／長生命週期 state，或規格有持續時間與資源穩定要求 |
| Failure／recovery | 節點含 IO、transaction、retry、checkpoint、partial write、external dependency 或規格要求復原 |
| Compatibility／migration | Schema、公開 API、serialized format、persistent data、versioned contract 改變 |
| External-effect isolation | Database、network、deployment、credential、external transaction、message publish 或不可逆操作 |

System Map fanout 只觸發 dependency regression，不會單獨推導 load／soak；load 與 soak 必須有業務量、生命週期或 approved profile 依據。

### 11.2 編譯輸入

```text
task_specification_requirements
＋ target_layer
＋ business_scenarios_and_invariants
＋ failure_impact
＋ statefulness_and_recovery
＋ concurrency_and_ordering
＋ data_volume_and_duration
＋ usage_frequency_and_burst
＋ external_side_effects
＋ System_Map_dependency_fanout
＋ live_source_change_surface
＋ execution_cost_budget
＋ approved_DDH_default_profiles
```

System Map 提供 dependency／reverse-dependency fanout 與 node layer 候選；任務規格與 live source 才是品質要求的 authority。

#### 11.2.1 已確認：標記責任與 Authority

**責任分配**

| 角色／來源 | 責任 | 不具備的權限 |
|---|---|---|
| 使用者／任務規格 | 提供目標、業務場景、驗收、已知風險、預算與明確 required／禁止項目 | 不需要逐項人工標記所有技術性品質維度 |
| Approved DDH Quality Defaults | 提供各 layer／risk 的預設 applicability rules 與缺省 fallback | 不能覆寫任務規格 |
| System Map query | 提供 node layer、dependency／reverse-dependency fanout 與 contract 關係候選 | 不能標記 required／N/A，也不是驗收 authority |
| Live source／schema／configuration | 驗證 statefulness、concurrency、external interaction 與 Map assumptions | 不能自行產生業務 expected behavior |
| 主 Agent | 組裝固定 inputs、觸發 query、處理缺口與協調流程 | 不是品質要求的來源，不能任意降低標記 |
| TAQG Quality Contract Compiler | 依固定 inputs 與 approved rules 產生每個 dimension mark | 不能創造新規格或使用未核准 heuristics |
| Independent Test Critic | 從固定規格重新檢查標記與理由，拒絕遺漏或錯誤 N/A | 只審查，不是 authority，也不能自行 admission |
| Implementation／Test Agent | 提供 source／test proposal 與可觀察事實 | 不能決定自己工作的 required／N/A 或降低 profile |

**標記來源優先序**

```text
user_explicit
→ referenced_approved_specification
→ approved_DDH_quality_default
→ mechanically_derived_fact_under_approved_rule
```

若來源衝突，高順位來源優先；System Map／live source 只提供 fact，不越過上述 authority。

**每個 dimension mark 至少包含**

```text
dimension_id
＋ applicability_status
＋ decision_source_kind
＋ source_references
＋ approved_rule_id_and_version
＋ condition_predicate_if_any
＋ business_reason_if_not_applicable
＋ architecture_and_live_source_facts
＋ invalidation_triggers
```

**三種標記的產生規則**

- `required`：任務規格明示，或 approved rule 在已確認 facts 下必然觸發。
- `conditional`：Draft 編譯時仍缺少可自動取得的 fact；必須保存 predicate 與 fact source，取得資料後解析成 `required` 或 `not_applicable_with_business_reason`。
- `not_applicable_with_business_reason`：approved rule 明確允許排除，且規格、System Map facts 與 live source 都沒有觸發條件；必須保存業務理由。

Test admission 前不得殘留 `conditional`。若 predicate 沒有資料來源或無法求值，不能讓 Agent 自行猜測為 N/A，必須走 approved default 或 `quality_policy_gap`。

**避免日常人工詢問**

- 常見缺省情況應由已核准 DDH Quality Defaults 覆蓋，TAQG 自動編譯。
- 缺少單一 runtime fact 時，Context Broker／System Map／live-source adapter 自動補取，不先問人類。
- 只有現有任務規格與 approved defaults 都沒有規則，且不同選擇會實質改變驗收成本或風險時，才產生一次 `quality_policy_gap`。
- `quality_policy_gap` 的人類決策應優先形成可重用 default rule，避免後續每個 Work Package 重複詢問。

**例子**

- 任務規格明示「同一檔案變更事件可能同時重送」，TAQG 依 approved idempotency rule 將 duplicate／concurrency dimension 標為 `required`。
- 任務規格說明 formatter 只在單執行緒每日批次使用，System Map 與 live source 確認無共享狀態；TAQG 可依 approved rule 將 high-concurrency soak 標為 `not_applicable_with_business_reason`。
- Test Agent 主張「壓測太慢所以 N/A」不構成合法 decision source。

### 11.3 輸出維度

| 維度 | 可能輸出 |
|---|---|
| Scenario classes | happy path、negative、boundary、state transition、failure／recovery |
| Oracle strength | exact expected value、invariant、property、metamorphic relation、reference／differential |
| Fault sensitivity | mutation scope、known-bad probes、minimum detection threshold |
| Reliability | repeat profile、order randomization、seed policy、isolation |
| Interaction | dependency contract、reverse-dependent regression、concurrency／race |
| Stress | load、burst、volume、soak、fault injection 或 `not_applicable` |
| Review | mechanical-only、standard Critic、enhanced independent Critic |
| Cost | parallelism、sampling、cache／reuse 與最大 execution budget |

門檻數值必須來自使用者明示、引用的固定規格或已核准 DDH default profile；主 Agent只是編譯者，不能憑空成為規格來源。

### 11.4 層級基線

Decision 0020 amendment：本表正式視為scope layer defaults，而非由低到高的
single quality severity。State、integrity、concurrency、recovery、
compatibility、security、performance、soak與external isolation分別依trigger
編譯為independent add-ons。

| 層級 | 預設關注點 |
|---|---|
| Module | examples、boundary／negative、核心 property、風險相符 mutation sample |
| Subsystem | 業務狀態轉移、failure／recovery、contract boundary、必要 concurrency |
| Domain | 跨 Subsystem workflow、一致性、reverse-dependent regression、適用的 load／soak |
| Global | 跨 Domain invariants、相容性與全域不可破壞條件 |

層級基線只是 approved default 的候選，不能覆寫任務規格。

### 11.5 業務場景

#### TAQG-QUAL-S01：低頻、無共享狀態的 Module

**Given**

- 一個內部報表欄位 formatter，每日批次只呼叫一次。
- 無共享狀態、無 concurrency、失敗只影響單一可重跑報表。
- 任務規格明確定義輸入、輸出與邊界格式。

**Then**

- Exact examples、boundary、negative 與 determinism 為 `required`。
- 小範圍 mutation sample 在 Draft 可為 `conditional`，依核准 default 取得 facts 後必須解析成 `required` 或有理由的 N/A。
- High-concurrency、burst load 與長時間 soak 可以是 `not_applicable`，但必須附上述業務理由。
- 不因「Subsystem 一律要壓測」而支付不具收益的成本。

#### TAQG-QUAL-S02：高影響、具狀態與高 Fanout 的 Subsystem

**Given**

- Workspace indexing state machine 被多個 ManifestLoader／DependencyScanner nodes 消費。
- 具有重試、路徑逃逸、重複事件、並行索引更新與資料一致性風險。
- System Map Q2 顯示多個 reverse dependents，並經 live source 確認。

**Then**

- 完整狀態轉移、negative、failure／recovery、idempotency 與 concurrency 為 `required`。
- Mutation／known-bad probes 必須涵蓋路徑、狀態與重複處理錯誤。
- Reverse-dependent regression closure 為 `required`。
- Load／burst／fault injection 依業務量與 failure impact 編譯；不由檔案數或程式複雜度決定。

### 11.6 成本與凍結

- Test Quality Applicability 必須在正式 test admission 前固定；看到 candidate／test failure 後不得降低。
- 成本預算影響 scheduling、parallelism、sampling implementation 與 cache reuse，不得移除 required scenario 或最低 detection requirement。
- 若固定 requirement 無法在預算內完成，先使用等價、已驗證的成本優化；仍不足時回報 budget／requirement conflict，不能靜默降級。
- Test asset 未變時重用既有 quality admission，不在每次產品 verification 重付 Critic／mutation 成本。

### 11.7 對應機械測試

```text
test_quality_applicability_is_deterministic_for_same_inputs_and_profile
test_low_frequency_stateless_module_can_mark_unrelated_soak_not_applicable
test_not_applicable_requires_business_reason
test_high_fanout_stateful_subsystem_requires_interaction_regression
test_system_map_fanout_is_verified_against_live_source_before_use
test_agent_cannot_lower_quality_requirements_after_observing_failure
test_cost_budget_changes_scheduling_not_required_acceptance
test_unchanged_test_assets_reuse_existing_quality_admission
```

### 11.8 Stress Contract 候選

- 大量 nodes 同時編譯 applicability 時，結果必須 deterministic，且不能因排程順序產生不同 requirement。
- System Map fanout 很大時採 bounded query 與分層 closure，不把整張 graph 注入 Agent Context。
- Quality profile／task specification 高頻更新時，stale contracts 不得被 admission 或 MVE 使用。

## 12. 已確認 Contract：TAQG-QUAL-002 Threshold Calibration and Default Profiles

### 12.1 問題

`required` 只決定要做某項品質驗證，尚未回答 mutation detection、repeat、randomization、load、latency 或 soak 要做到多少。具體數值不能由 Agent 臨時生成，也不能使用全專案單一百分比。

### 12.2 Authority

門檻來源優先序：

```text
user_explicit_in_task_specification
→ referenced_approved_quality_profile
→ versioned_DDH_default_profile
```

- 主 Agent與 TAQG 只選用／編譯已存在門檻，不創造數值。
- System Map 提供 layer／fanout facts，不提供 mutation percentage、repeat count 或性能 SLO。
- 看見測試失敗、執行過慢或預算不足後，不得修改已 pinned profile。
- Default profile 更新會改變未來驗收政策，必須形成獨立版本化 policy proposal；不能由單一 Work Package 自動改寫。

### 12.3 Profile Key

Default threshold 不只依 L0–L3，至少依下列 key 選擇：

```text
gate_level
＋ architecture_layer
＋ behavior_class
＋ failure_impact_class
＋ execution_environment_class
＋ test_toolchain
```

例如 L2 的純計算 Subsystem 與 L2 的並行交易 Subsystem，不應共享完全相同的 concurrency／soak profile。

### 12.4 Calibration 方法

初始與更新 profile 必須由可重播 calibration suite 產生證據：

1. 選擇代表性的 Module／Subsystem／Domain fixtures。
2. 建立已知錯誤 mutants／fault injections／flaky patterns。
3. 測量不同 threshold／repeat／sampling 下的 detection rate、false-positive、flaky detection 與 execution cost。
4. 找出能滿足最低 detection requirement 的最低成本組合。
5. 由獨立 Critic 檢查代表性與盲點。
6. 形成 versioned default profile proposal。
7. 人類只核准 profile policy 版本，不逐個 Work Package 核准數字。

### 12.5 各類門檻

| 類型 | Calibration 輸出 |
|---|---|
| Mutation／known-bad | 依 behavior class 的 required mutant classes、sampling strategy、minimum detection floor |
| Determinism／flaky | repeat／seed／order permutations 與 required zero-flake gate |
| Property | case generation budget、seed persistence、shrinking／replay requirements |
| Concurrency | worker／interleaving profile、race injection 與 invariant checks |
| Load／burst | 規格 workload model、warm-up、measurement window、latency／throughput oracle |
| Soak | duration class、resource growth／leak oracle、recovery observation window |
| Critic | review depth、independence requirement、fallback profile 與 token budget |

性能／load 的 pass threshold 若屬產品 SLO，仍必須來自任務規格；calibration 只能決定如何可靠測量，不能創造產品 SLO。

### 12.6 執行與版本規則

- Work Package 凍結時 pin `quality_profile_id／version`。
- Profile 新版本不追溯改變已建立的 Verification Subject。
- Source／spec 未變但 profile policy 更新時，是否需要重 admission 由 profile 的 declared invalidation scope 決定。
- Test assets 未變且 pinned profile 相同時，重用既有 admission。
- 新專案尚無本地 calibration 時，使用已核准 bootstrap profile；執行資料只能形成未來 proposal，不能在當次任務中自動放寬。
- Calibration raw logs 是短期資料；確認 profile 後長期保存 versioned profile、可重播 calibration tests／fixtures，而不是歷史完整輸出。

### 12.7 業務場景

**Given**

- 新的 L2 Workspace Subsystem 需要 mutation、concurrency 與 determinism。
- 專案尚未建立 Workspace-specific threshold baseline。

**When**

- TAQG 編譯 Test Quality Contract。

**Then**

- 選用與 gate／layer／behavior／impact／toolchain 相符的 approved bootstrap profile。
- Agent 不得自行填寫 mutation percentage 或 repeat count。
- 本次 admission 使用 pinned bootstrap version。
- Calibration 結果可以提出新版 Workspace profile，但不回頭改變本次 Contract。

### 12.8 對應機械測試

```text
test_thresholds_resolve_only_from_explicit_or_approved_profile_sources
test_agent_cannot_invent_or_lower_threshold_after_failure
test_profile_selection_uses_gate_layer_behavior_impact_and_toolchain
test_product_slo_cannot_be_created_by_calibration
test_profile_version_is_pinned_before_test_admission
test_new_profile_version_does_not_rewrite_existing_subject
test_bootstrap_profile_allows_new_project_to_continue_without_human_checkpoint
test_unchanged_assets_and_profile_reuse_existing_admission
```

### 12.9 Stress Contract 候選

- 多個 profile candidates 同時 calibration 時，結果與 selection 不得因執行順序漂移。
- 大型 mutation matrix 必須採 approved sampling／sharding，不讓成本或 temporary logs 無界成長。
- Profile 頻繁更新時，MVE 不得混用 threshold versions 或錯誤重用舊 admission。

### 12.10 已確認：Self-Evolution Boundary

Orchestration self-evolution 不得直接或間接修改：

- `required／not_applicable` applicability。
- Mutation classes、detection floor 或 sampling policy 的最低要求。
- Repeat／randomization／determinism gate。
- Concurrency、load、soak、fault-injection requirements。
- Product SLO、threshold、oracle 或 measurement logic。
- Invalidation triggers、Critic independence requirement 或 human decision boundary。

OLE 可以改善但不得改變驗收語意的項目：

- 如何切分 Test Agent／Critic 子工作。
- Context Envelope 內容與摘要格式。
- Mutation／pytest 的 sharding、parallelism、cache、ordering 與 batching。
- Failure clustering、failure bundle 與 token 使用。
- 在多個已核准且語意等價的 runner／builder 間選擇成本較低者。

若執行資料顯示 profile 過慢、偵測不足或成本不合理：

```text
OLE may identify orchestration inefficiency
→ independent TAQG calibration reproduces evidence
→ versioned quality profile proposal
→ independent Critic／benchmark
→ human policy approval
→ future Work Packages may use new version
```

- OLE 的記憶或建議不能直接成為 threshold evidence。
- Calibration 必須用自己的可重播 tests／fixtures 重新證明效果。
- 新 profile 不追溯修改已 pinned Work Package／Verification Subject。

## 13. 已確認 Contract：TAQG-QUAL-003 Test Asset Lifecycle, Validity and Disposition

### 13.1 目的與第一性原則

可重播Verification Assets是長期Evidence Retention的核心；pytest只是其中一種。任何asset「曾經admitted」不代表永遠適用，也不代表已對目前candidate執行。

TAQG 必須分開回答：

1. 測試資產目前是否仍忠實代表固定規格與場景。
2. 有效測試是否已對目前 immutable candidate 執行。
3. 測試失效、受懷疑或 coverage 出現缺口時，下一步是重跑、修復、新增、替換、退休或要求規格決策。

產品 source 改變通常只使目前 candidate 的執行結果需要重跑；只有規格、oracle、測試資產、必要 contract／schema、quality policy 或執行相容性改變時，pytest 本身才可能失效。

### 13.2 三條獨立狀態軸

**Admission lifecycle**

```text
draft → candidate → admission_validating → admitted
                                      └→ rejected／quarantined
```

**Semantic validity**

| 狀態 | 語意 |
|---|---|
| `active` | 仍對應目前固定規格，可進入 suite selection |
| `suspect` | 有可能影響語意或執行相容性的變化，尚待機械解析 |
| `stale` | 已確認規格、oracle、必要 contract 或 test identity 不相容，不得驗收 |
| `quarantined` | flaky、fixture／helper 錯誤或 test implementation defect，不能作為 required PASS gate |
| `retired` | 規格場景已移除，或 admitted replacement 已完成 coverage closure |

`superseded_by` 是 immutable asset versions 之間的關係，不是可以模糊覆寫歷史 identity 的狀態。DDH 不要求永久保存 retired pytest 的工作樹副本；版本控制歷史足以保存一般來源演進。

**Candidate execution state**

| 狀態 | 語意 |
|---|---|
| `not_run` | 有效測試尚未對目前 candidate 執行 |
| `passed` | 已對完整 Verification Subject 執行並通過 |
| `failed` | 已執行且得到產品或測試失敗 |
| `blocked` | runner／環境／依賴故障，尚未得到產品判定 |

`active` 不等於 `passed`；歷史 PASS 也不能替代目前 candidate 的 `not_run`。

### 13.3 Authority 與責任

| 角色／元件 | 責任 | 不具備的權限 |
|---|---|---|
| TAQG Validity Evaluator | 比對固定 identity 與 facts，產生 validity／reason | 不解釋新業務語意 |
| TAQG Disposition Compiler | 依版本化規則產生 required action | 不以成本或 Agent 建議降低 coverage |
| 主 Agent | 觸發判定、依 disposition 派工、追蹤 coverage closure | 不能自行把 stale 改為 active 或 admission 自己的 test change |
| Test Agent | 提出修復、新增或替換 pytest／fixture／helper | 不能決定舊資產仍有效或自行 admission |
| Independent Test Critic | 審查 oracle、mapping、刪除、替換與 anti-weakening | 不是規格 authority |
| System Map query | 提供 changed／affected／reverse-dependent nodes 候選 | 不能判定 test validity、required action 或驗收 |
| Live-source adapter | 確認 contract、schema、fixture、toolchain 與 Map assumptions | 不能創造 expected behavior |
| MVE | 對 admitted／active assets 執行並回報 candidate execution state | 不修改、刪除、repair 或 admission test assets |
| 人類 | 處理規格缺口、語意改變或 quality policy 改變 | 不需要批准一般重跑與 semantics-preserving repair |

Test Agent 可以由單一主 Agent 承擔，但該 Agent 不能核准自己的 test asset change；只有測試資產實際改變時才支付獨立 Critic／admission 成本，單純重跑不重付。

### 13.4 最小資料與狀態保存

Immutable admitted Test Asset Manifest 至少綁定：

```text
test_asset_id_and_version
＋ test_source_digest
＋ fixture_helper_configuration_digests
＋ covered_specification_item_ids_and_digests
＋ covered_business_scenario_ids
＋ quality_profile_id_and_version
＋ architecture_node_references
＋ referenced_contract_schema_versions
＋ toolchain_compatibility_class
＋ invalidation_rule_ids_and_versions
```

Validity evaluation 輸出至少包含：

```text
validity_status
＋ reason_code
＋ required_action
＋ affected_specification_items
＋ affected_scenarios
＋ affected_nodes
＋ replacement_required
＋ coverage_gap
＋ critic_required
＋ human_decision_required
＋ evaluated_input_identities
```

- Quality mapping 與必要 metadata 必須與 pytest／fixture／configuration／profile 一起受版本控制。
- Test Asset Manifest 與目前 validity status 是可由上述 canonical inputs 重建的 derived artifacts，不是新的行為 SSOT，也不是永久 admission receipt。
- `superseded_by` 由獨立、版本化的 supersession declaration 綁定 old／new asset identities；舊 immutable manifest 不得為了記錄未來 replacement 而回寫。
- 可保存有界 status cache 加速查詢，但 cache、discovery index、檔名、marker 或 Agent claim 不能單獨授予 `active／admitted`。
- 不永久保存每次 pytest PASS log；MVE 在當次 Work Package 內仍須暫時保有完成機械判定所需的 subject result。

### 13.5 判定時機與成本控制

| 時機 | 動作 |
|---|---|
| 純討論、規格尚未固定 | 只形成 test proposal，不發布正式 validity |
| Work Package 啟動、規格與 profile 已 pinned | 計算既有 active／stale assets、coverage gap 與初始 required suite |
| 施工中的 product source mutation | 便宜地標記 affected candidate tests 為 `not_run／rerun_required`，不直接使 test stale |
| 施工中的 spec／test／fixture／helper／contract／schema／toolchain mutation | 發出精確 suspect／stale candidate event，不在每次寫入跑全庫 Critic |
| 全部 product writers quiescent、Candidate Freeze boundary | Freeze 前封閉 mutation inventory；CIM 發布 immutable product candidate 後，TAQG 對該精確 identity 執行正式 validity／impact closure |
| MVE 建立 Verification Subject 前 | 只重驗 identity／digest／epoch；不重做完整語意 review |
| escaped bug、surviving mutant 或 flaky evidence 出現 | 立即觸發相關 fault-sensitivity／reliability disposition |

Product candidate Freeze 後的遲到 product write 由 freeze fence 阻擋並建立新 candidate generation。Test Agent 的 repair 可以建立新 test asset version／manifest，不要求重做未受影響的 frozen product candidate；MVE 最後以兩者的新組合建立 Verification Subject。

### 13.6 固定 Disposition 規則

| 原因 | Required action |
|---|---|
| 只有產品實作改變 | 保留 pytest；對新 candidate 重跑 |
| test／fixture／helper 內容改變 | 新 asset version 回到 admission；不能沿用舊 admission |
| test implementation defect／flaky | quarantine；Test Agent semantics-preserving repair；Critic／admission |
| expected behavior 或規格條款改變 | stale；依新固定規格修改／新增 tests；不得自動改 oracle |
| 規格場景正式移除 | retired candidate；通過引用與 coverage closure 後才可刪除 |
| Module 搬移／拆分且行為未變 | 優先重用，更新 mapping／invocation；必要 mapping validation |
| 新行為、invariant、狀態轉移或 contract boundary | 產生 coverage gap，新增對應 tests |
| schema／公開契約／dependency behavior 改變 | suspect；先做 impact closure，再決定 compatibility／integration tests |
| escaped bug／surviving mutant | 保留仍正確的舊 tests，新增 regression／fault-sensitive test |
| 新 reverse dependent | 重新選取 regression closure；不自動使原 test stale |
| runner／toolchain 改變 | 先做 determinism／compatibility revalidation；不得修改 tests 配合 runner |

Disposition 是自動路由，不是人工 Checkpoint。只有固定規格與 approved defaults 無法決定 expected behavior 或 quality requirement 時，才輸出 `human_decision_required=true`。

### 13.7 新節點、測試新增與刪除規則

DDH 以 `specification item → business scenario → test coverage` 管理驗收，不採「每個 System Map node 固定配置 pytest 數量」。

新增 node 只有在引入下列內容時才必須新增對應 test：

- 新業務場景或 expected behavior。
- 新 invariant 或 state transition。
- 新 contract boundary。
- 新 failure／recovery path。
- 新 concurrency、ordering 或 consistency risk。
- 既有 admitted assets 無法觀察的新責任。

若只是行為等價的移動、拆分或內部重構，優先重用既有 Module／Subsystem／Domain tests 並更新 mapping；System Map 只協助找到受影響節點。

刪除 pytest 必須同時滿足：

1. 對應場景已由固定規格正式移除，或已有 admitted replacement。
2. System Map query 與 live source 確認沒有其他有效規格、node 或 contract 仍引用。
3. `specification → scenario → test` coverage closure 沒有缺口。
4. Independent Critic 確認沒有放寬 assertion、threshold、dataset 或 suite selection。
5. 刪除位於本次允許 write scope。

不符合時只能保持 stale／retired candidate 或建立 replacement，不能為了讓 candidate PASS 而刪除測試。

### 13.8 業務場景：Workspace Discovery Subsystem 拆分

**Given**

- `workspace.discovery_service` 同時負責路徑資格、manifest 解析與索引寫入。
- 固定規格與既有 Subsystem／Domain discovery tests 均未改變。
- 本次架構內重構拆成 `path_policy`、`manifest_parser` 與 `index_writer`。

**When**

- Implementation Agent 完成產品修改。
- Test Agent 提出必要的 Module test changes。
- Product writers quiescent，CIM 凍結 product candidate；TAQG 再對該 identity 執行正式 validity／disposition。

**Then**

- 仍經公開業務入口驗證 workspace discovery 成功的 Subsystem test 保持 `active`，更新 mapping 後對新 candidate 重跑。
- 直接呼叫已移除 internal function 的舊 Module test 標為 `stale(invocation_contract_removed)`，建立對應新 Module tests。
- 驗證重建後 manifest index 一致性的 Domain test 保持 `active`，因 impact closure 對新 candidate 重跑。
- 不因新增三個 nodes 就機械建立三份無業務意義的測試。
- 舊 Module test 只有在 replacement admitted 且 scenario coverage closure 完整後才可 retired／刪除。
- 若重構同時要新增「workspace 外部路徑白名單」，先產生規格更新提案；Test Agent 不能自行創造 expected behavior。

### 13.9 Stress Contract

- 數萬個 test assets 中只有一個 Module 改變時，使用 bounded System Map query、mutation inventory 與索引做增量 invalidation，不掃描或注入整個測試庫到 Agent Context。
- 大量 assets 同時 invalidation 時，publication 必須 atomic；MVE 只能看到舊完整 epoch 或新完整 epoch。
- 同一組 pinned inputs、rule versions 與 live facts 必須得到相同 validity／disposition，不因 Agent、排程或事件順序漂移。
- Event storm 必須 coalesce，但不得漏掉 spec、test、fixture、contract、schema 或 toolchain mutation。
- Routine rerun 與 identity validation 不需要 Agent token；只有 repair proposal、semantic ambiguity 或 selected Critic review 使用 Agent。

### 13.10 對應機械測試

```text
test_discussion_stage_does_not_publish_formal_test_validity
test_product_source_change_requires_rerun_without_staling_test_semantics
test_specification_change_marks_mapped_test_asset_stale
test_test_fixture_or_helper_change_requires_new_asset_admission
test_active_test_is_not_treated_as_passed_for_new_candidate
test_main_or_test_agent_cannot_extend_its_own_asset_validity
test_disposition_is_deterministic_for_pinned_inputs_and_rules
test_new_node_without_new_behavior_does_not_require_artificial_test_count
test_new_behavior_creates_scenario_coverage_gap
test_removed_scenario_requires_reference_and_coverage_closure_before_deletion
test_escaped_bug_adds_regression_without_erasing_valid_existing_tests
test_new_reverse_dependency_reselects_regression_without_staling_original_test
test_late_product_write_creates_new_candidate_without_mutating_frozen_identity
test_test_asset_repair_creates_new_manifest_without_refreezing_unchanged_product_candidate
test_mve_rejects_suspect_stale_quarantined_or_retired_assets
test_large_test_repository_uses_incremental_invalidation_without_agent_context_growth
```

### 13.11 與既有 DDH 邊界

- 本 Contract 是每個 Work Package 內對 pinned 規格、目前資產與 candidate 的局部 validity 計算，不恢復 legacy ADAD 的全專案 contract freshness chain。
- 不建立跨版本永久穩定的 System Map entity identity；node references 由目前 Map query 提供候選並以 live source／固定規格確認。
- System Map 仍是 actual architecture index，不是 test validity 或驗收 authority。
- Test Asset Manifest 是 derived artifact；規格仍是行為與 expected behavior 的 SSOT。
- Self-evolution 只能改善 invalidation batching、cache、query ordering 與派工，不能改 invalidation rules、disposition policy、刪除條件、Critic independence 或 human decision boundary。

## 14. 已確認 Contract：TAQG-ASSET-001 Test Asset Layout and Discovery

### 14.1 目的

DDH必須能從不同專案既有的CI／verification結構，穩定找到pytest、其他test commands、build／lint／type／schema／security／integration／stress checks及其fixture、helper、configuration與profile，建立可重建的Verification Asset Inventory。DDH core不以特定目錄或tool作為admission authority，也不要求所有專案為框架搬動資產。

### 14.2 Project Test Layout Profile

每個專案固定一份 versioned Test Layout Profile，允許：

- 依 `tests/module／subsystem／domain／global` 分層存放。
- 測試與產品 Module colocated。
- 沿用專案既有的其他測試結構。

Layout Profile 至少宣告：

```text
test_roots_or_colocation_rules
＋ discovery_adapter_id_and_version
＋ include_exclude_rules
＋ fixture_helper_configuration_roots
＋ metadata_extraction_rules
＋ generated_asset_policy
＋ path_normalization_policy
```

目錄、檔名與 discovery result 只協助尋找資產，不能單獨證明 test admission、validity 或 required coverage。

### 14.3 最小機械 Mapping

每個正式 acceptance asset 必須能由 adapter 解析：

```text
specification_reference
＋ business_scenario_reference
＋ verification_layer
＋ behavior_class
＋ target_node_references
＋ fixture_helper_configuration_closure
```

- Python MVP 可以使用 pytest markers／configuration 表達必要 mapping。
- DDH schema保持runner-neutral；第一版除pytest reference adapter外，至少要求
  一個non-pytest／generic fixed-command adapter證明tool neutrality。
- Path 不是跨版本 identity。每個 asset version 以精確 source 與 dependency content identities 識別。
- 新舊版本的延續或替換必須由 explicit supersession declaration 表達，不能從 rename、函式名稱或 Agent claim 猜測。

### 14.4 Discovery Adapter Contract

```text
collect assets
→ extract normalized DDH metadata
→ resolve fixture／helper／configuration dependency closure
→ compute exact content identities
→ validate missing／ambiguous／duplicate mappings
→ publish rebuildable Verification Asset Inventory
```

必要規則：

- Inventory 是 derived cache，不是 SSOT 或 admission receipt。
- Inventory 遺失、損壞或版本不相容時，從 Layout Profile 與 version-controlled test assets 自動重建。
- Adapter 只能回報 discovered facts，不能把未映射測試自動提升為 acceptance。
- Required scenario 無 mapping 時輸出 coverage gap，不得用相似檔名猜測。
- Fixture／helper／configuration 變化必須進入 asset digest closure，防止只比較 pytest 檔案。
- Path normalization、case sensitivity、separator、symlink／junction 與 generated tests 必須由 profile 明確定義，保持跨平台可重現。

### 14.5 業務場景

**TAQG-ASSET-S01：專案沿用既有 colocated tests**

- Workspace modules 把 tests 放在各自 package 中，沒有 `tests/subsystem` 目錄。
- Layout Profile 宣告 colocation 與 pytest marker extraction。
- Adapter 正確建立 scenario／layer／node mapping，不要求搬移測試。
- 路徑結構不同不影響 admission；缺少必要 marker 才形成 mapping gap。

**TAQG-ASSET-S02：Fixture 改變但 pytest 檔案未變**

- 一個共享路徑 fixture 改變 separator 與 casing input。
- Adapter 重新計算 dependency closure，所有引用該 fixture 的 asset identities 改變並回到 `TAQG-QUAL-003` disposition。
- 系統不能因 pytest source digest 未變就沿用 admission。

**TAQG-ASSET-S03：測試 rename／move**

- 測試內容與場景 mapping 不變，但檔案搬到新路徑。
- Adapter 產生新的精確 asset identity；是否延續 admission 依 approved mapping／content rule 處理。
- 不建立永久跨版本 identity，也不因路徑相似自動宣告相同資產。

### 14.6 Stress Contract

- 五萬個 tests 中只改一個共享 fixture 時，增量 dependency closure 必須找到所有受影響 assets，不全庫重新 admission。
- 大型 inventory 不得完整注入 Agent Context；routine discovery 的 Agent token cost 為零。
- 大量 parallel collection 結果必須 deterministic，不因 worker completion order 改變 mapping 或 digest。
- Generated tests、symlink／junction、case-only rename 與跨平台 path differences 不得造成重複或漏掉資產。
- Inventory cache 損壞時能自動重建；工具故障不要求 Agent 理解 cache 格式。

### 14.7 對應機械測試

```text
test_project_layout_profile_supports_layered_and_colocated_tests
test_path_or_filename_alone_cannot_grant_test_admission
test_pytest_adapter_extracts_required_spec_scenario_layer_and_node_mapping
test_missing_required_mapping_produces_coverage_gap
test_fixture_helper_and_configuration_are_in_asset_digest_closure
test_inventory_is_rebuildable_and_not_acceptance_authority
test_asset_identity_does_not_assume_cross_version_continuity_from_rename
test_first_implementation_proves_pytest_and_non_pytest_adapters_share_protocol
test_large_repository_uses_incremental_discovery_without_agent_context_growth
test_parallel_discovery_is_deterministic_across_worker_order
test_cross_platform_path_rules_prevent_duplicate_or_missing_assets
```

### 14.8 Self-Evolution Boundary

OLE 可以改善 discovery sharding、cache、ordering、batching 與 Context 摘要，但不能修改 Layout Profile authority、必要 mapping、identity closure、include／exclude policy 或 admission rules。

## 15. 已確認 Contract：TAQG-PORT-001 Test Portfolio Health and Maintenance

### 15.1 目的

單一 test asset admission 通過後，TAQG 仍須檢查整個 portfolio 是否遺漏必要業務場景、存在無價值重複、無法偵測已知錯誤、包含 flaky／order-dependent／uncollectable assets，或讓成本持續增加但沒有增加驗證價值。

Portfolio Health 只改善 suite 組合與維護效率，不能以去重、成本或 maintenance 為理由降低 specification coverage、oracle strength 或 fault sensitivity。

### 15.2 分維度判定，不使用單一總分

| 維度 | Portfolio 檢查 |
|---|---|
| Semantic fidelity | 規格／場景 coverage、錯誤 mapping、orphan assets |
| Fault sensitivity | known-bad／mutation detection、永遠不會失敗的 assertion |
| Execution reliability | flaky、order dependence、fixture leakage、collection failure |
| Lifecycle validity | stale、quarantined、retired、失效 dependency |
| Cost observation | runtime、resource、重複執行與維護成本；不混入品質總分 |

每個 finding 獨立標記：

```text
blocking
maintenance
informational
```

- 必要場景沒有 admitted executable coverage、required test flaky、必要 mutation floor 未達成是 `blocking`。
- 完全重複但不降低 coverage 的候選是 `maintenance`。
- 慢但仍符合 approved profile 的測試可以是 `informational`。
- 不得以 aggregate score 掩蓋任一 blocking gap。

### 15.3 Portfolio Health Subject

每次 audit 固定：

```text
task_or_long_term_specification_versions
＋ quality_profile_id_and_version
＋ test_asset_inventory_digest
＋ fixture_helper_configuration_closure
＋ toolchain_profile
＋ audit_rule_versions
```

- 同一組 inputs 必須得到相同 findings／disposition。
- Health Snapshot 是 derived state，可重建，不是 Evidence SSOT 或永久 audit log。
- Routine audit 由無 Agent runner 執行；只有 test repair、非機械語意比較、dedup／deletion proposal 或規格缺口才使用 Agent。

### 15.4 Mechanical Audit Pipeline

```text
collectability check
→ specification／scenario coverage closure
→ stale／quarantined／orphan detection
→ duplicate candidate clustering
→ known-bad／mutation sampling
→ determinism／order／isolation audit
→ execution cost analysis
→ disposition
```

Directory、test name、程式碼相似度或 code coverage 都只能提供候選，不能單獨決定 duplicate、quality 或 deletion。

Output hygiene 也是 execution reliability 的一部分：

- Routine PASS 不應輸出無界 logs。
- Test／fixture／helper 不得以 uncontrolled print、每個 case 重複 traceback 或逐 sample metrics dump 作為正常診斷介面。
- 超出 approved Output Hygiene Profile 時，test asset 進入 repair／re-admission；不能把 MVE buffer 當成永久吸收噪音的替代品。

### 15.5 Duplicate Classification

| 情況 | 判定 |
|---|---|
| 相同 scenario、input partition、oracle、fixture closure 與 fault sensitivity | Dedup candidate |
| 相同 scenario，但驗證不同 boundary／failure partition | 不是重複 |
| 相同產品路徑，但分屬 Module 與 Domain invariant | 不是重複 |
| Example test 與 property／metamorphic test | 通常互補 |
| 名稱或 source 很像 | 只能作 discovery hint |
| Admitted replacement 完整覆蓋舊 asset | 可以提出 retirement |

Similarity model／Agent 只能提出候選，不能刪除或 admission consolidation。

### 15.6 Deduplication and Retirement

```text
mechanical duplicate candidate
→ compare specification／scenario mappings
→ compare input partitions／oracle／dependency closure
→ replay known-bad／mutation suite before and after consolidation
→ verify no coverage or detection loss
→ Independent Critic
→ admitted replacement
→ old asset retired
→ physical deletion if within write scope
```

任何 scenario 遺失、oracle 變弱、fault detection 降低或 required layer coverage 消失，都必須拒絕 dedup。

### 15.7 Audit Triggers

**Incremental audit**

- pytest／fixture／helper／configuration 變更。
- 規格場景新增、修改或移除。
- Quality Profile／audit rules 更新。
- `TAQG-ASSET-001` inventory／dependency closure 改變。
- Escaped bug、surviving mutant、flaky 或 collection failure。
- Suite cost 超過 approved profile budget。

**Full portfolio audit**

- Domain／Global 重大規格版本。
- 大量 contract／architecture change。
- Approved release-candidate profile。
- Approved periodic maintenance profile。
- 人類明確要求。

一般 product source change 只重跑 affected suites，不重新審查整個 portfolio。

### 15.8 Maintenance Budget

Approved Quality Profile 分別提供：

```text
routine_audit_compute_budget
＋ mutation_sampling_profile
＋ determinism_repeat_profile
＋ maximum_inventory_scan_cost
＋ critic_token_budget
＋ full_audit_triggers
```

- 先使用 sharding、cache、incremental closure 與 approved sampling。
- Required audit 仍無法在 budget 內完成時輸出 `quality_budget_conflict`。
- 不得自行刪除 required tests、降低 mutation threshold、縮小必要 dataset 或跳過 scenario。

### 15.9 業務場景

**TAQG-PORT-S01：平行 Test Agents 產生重複路徑逃逸測試**

- 三個 assets 名稱不同，但 scenario、input、oracle 與 dependency closure 相同。
- Audit 只產生 duplicate candidates，不直接刪除。
- Consolidation 後重播 mutation／known-bad probes；Critic 確認 detection 不降低。
- 新 consolidated asset admitted 後，舊 assets 才能 retired／刪除。

**TAQG-PORT-S02：看似重複但 boundary 互補**

- 一個 test 驗證 `..` 片段逃逸，另一個驗證 junction 指向 workspace 外部。
- 因 input partitions 不同，不能合併。

**TAQG-PORT-S03：低頻 Subsystem 沒有 soak test**

- Approved Quality Profile 已以業務理由將 soak 標為 N/A。
- Portfolio Health 不建立 coverage gap。
- 只有使用頻率、共享狀態或 profile facts 改變時才重新計算 applicability。

**TAQG-PORT-S04：Escaped duplicate-refund bug**

- 保留仍正確的舊 tests。
- Audit 證明現有 portfolio 無法偵測 duplicate event。
- 新增 regression／idempotency asset 並重新 admission。
- 只標記明確 fault-sensitivity gap，不宣稱所有歷史 tests 無效。

### 15.10 Stress Contract

- 五萬個 assets 的 routine audit 使用增量 inventory，不全庫重新分析。
- Duplicate clustering 必須有 memory、candidate count 與 runtime 上限。
- Mutation matrix 使用 approved sampling／sharding，不無界展開。
- Parallel audit 結果不因 worker completion order 改變。
- Routine audit、duplicate candidate search 與 cost analysis 的 Agent token cost 為零。
- Full logs 不進入 Agent Context，只提供 bounded findings。
- 大量 maintenance findings 不阻擋無關 Work Package；只有 blocking findings 影響 admission／completion。

### 15.11 對應機械測試

```text
test_portfolio_health_reports_dimensions_without_single_aggregate_score
test_required_scenario_without_admitted_coverage_is_blocking
test_required_flaky_asset_is_blocking
test_similarity_alone_cannot_delete_or_merge_tests
test_different_input_partitions_are_not_deduplicated
test_module_and_domain_tests_are_not_duplicates_by_shared_product_path
test_dedup_requires_no_coverage_or_mutation_detection_loss
test_retirement_requires_admitted_replacement_and_independent_critic
test_approved_not_applicable_stress_does_not_create_false_gap
test_escaped_bug_adds_fault_sensitive_regression_without_erasing_valid_tests
test_product_only_change_does_not_trigger_full_portfolio_audit
test_quality_budget_conflict_cannot_lower_required_quality
test_large_portfolio_uses_incremental_zero_agent_audit
```

### 15.12 Self-Evolution Boundary

OLE 可以改善 audit scheduling、sharding、cache、batching、candidate search、failure clustering 與 Critic Context Envelope，但不能修改：

- Blocking finding 定義。
- Duplicate equivalence rules。
- Mutation／known-bad requirements。
- Audit trigger policy。
- Deletion／retirement conditions。
- Quality requirement 與 maintenance budget 的衝突邊界。
