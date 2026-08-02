# Mechanical Verification and Test Governance Split Archive

> **已拆分：** 本文件只保留拆分前的討論與舊 ID 遷移來源，不再作為現行 Subsystem specification。  
> Test 品質治理 authority 移至 `test_asset_quality_governance_subsystem_specification.md`。  
> 機械驗證執行 authority 移至 `mechanical_verification_execution_subsystem_specification.md`。  
> 新討論不得繼續新增 MVTG authority；未遷移細節必須明確分派至 TAQG 或 MVE。

**中文名稱：** 機械驗證與測試治理拆分封存  
**狀態：** Superseded Split Archive  
**日期：** 2026-08-02  
**規範效力：** 只保存拆分前內容與 traceability；現行 authority 以 TAQG／MVE 規格為準  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

---

## 1. 責任

把固定規格投影成獨立 acceptance 與可無 Agent 重跑的 pytest／壓力測試，保護 expected behavior，並管理測試資產後續的有效性。

## 2. 不負責

- 不自行改變使用者目標、任務規格、架構決策、公開契約或人類升級條件。
- 不把 System Map、discovery metadata、Agent claim 或 prompt 約束當成授權或機械證據。
- 不因本 Subsystem 的局部 PASS 宣告 DDH Domain、release candidate 或 production 完成。

## 3. 依賴與協作

- 任務規格提供 expected behavior、acceptance、boundary 與 Stress Contract。
- Candidate Integrity 提供固定 verification subject。
- Parallel Work Coordination 分離 Implementation Agent 與 Test Agent 的寫入責任。

## 4. 已確認功能

### OW-F04：保護規格與獨立驗收

**確認狀態：已確認（2026-08-02）**

- 子代理不得修改本次任務規格。
- Implementation Agent 不得修改由 Test Agent 負責的 acceptance tests。
- Test Agent 不得修改產品實作來使測試通過。
- 測試 expected behavior 必須能追溯到固定規格條目。
- 發現規格矛盾或缺口時必須回報，不能自行選擇新的業務語意。
- 保護對象是獨立 acceptance 的 expected behavior，不代表 Implementation Agent 永遠不能新增或維護自己分區內的 unit tests。
- 規格明確而 pytest 的 fixture、setup、收集方式或 assertion 實作有錯時，可以修正 test implementation defect；修正前後必須指向同一規格期待。
- 刪除案例、加入無正當理由的 skip／xfail、放寬 assertion、降低門檻或縮小 fixture 以避開失敗，均不得被當成一般測試修正。
- Agent 可以讀取對方產物以整合與診斷，但不能把目前實作行為反向當成 expected behavior 的權威來源。

### OW-F17：可重用的無 Agent 機械驗證

**確認狀態：已確認（2026-08-02）**

所有由本 Subsystem 規格產生的 pytest 與壓力驗證，都必須滿足：

> Agent 可以建立、維護或觸發驗證，但測試選取、執行、門檻判定與結果產生必須能在沒有 Agent／模型服務的情況下，以固定流程重複執行。

每個 verification subject 必須具有機械可讀的 Verification Manifest，至少包含：

- specification／verification contract version。
- source snapshot／verification subject identity。
- 必跑 test ids 或可確定展開的 suite selectors。
- conditional tests 的機械 trigger。
- `not_applicable` 項目及已確認理由。
- pytest／其他 runner 的實際 argv、cwd、timeout 與 environment profile。
- stress profile、資料規模、random seed、重複次數與正式門檻。
- expected exit semantics、output limit 與 artifact location。

必要不變量：

- Human、CI 或一般 deterministic runner 能從相同 snapshot 與 manifest 重跑，不需要模型重新解讀自然語言規格。
- Agent 不得在執行當下自行刪除 tests、改 selectors、降低 threshold 或改 `required` 為 `not_applicable`。
- Verification Manifest 凍結後的修改屬於 verification contract 變更，必須走規格修訂與獨立監督。
- 正常測試執行不得呼叫 Agent／LLM API；失敗後是否要求 Agent診斷是另一個可選階段。
- pytest 的完整 stdout／stderr 保存為受控 artifact；只把機械摘要、failure fingerprint 與必要片段送入 Agent Context。
- test execution compute、時間與 storage 成本和 Agent token 成本分開計量。
- 測試重跑不得因 Agent prompt、對話狀態或模型版本不同而改變 selectors 與 expected behavior。
- 隨機、property-based、fuzz 或競態測試必須記錄 seed 與 profile，失敗案例可以無 Agent 重播。
- 測試資產可以跨 Work Package 重用；是否 stale 由規格／契約／snapshot 關係機械判定，不由 Agent每次重新生成。

成本記錄至少區分：

| 成本 | 例子 |
|---|---|
| `agent_token_cost` | 規格整理、Context、程式與測試撰寫、失敗診斷 |
| `verification_compute_cost` | pytest CPU／memory／worker time |
| `environment_setup_cost` | dependency、fixture、isolated candidate 建立 |
| `artifact_storage_cost` | logs、reports、snapshots、failure reproducer |

例行 PASS 不應把完整 log 注入 Agent Context。只有失敗、漂移、規格缺口或需要決策的摘要才消耗額外 token。

## 5. 已確認業務場景

### OW-S16：Implementation Agent 嘗試改寫 acceptance expectation

**對應功能：** OW-F04

**Given**

- `PAY-02` 規格要求重複付款不得再次入帳。
- 對應 acceptance test 由 Test Agent 分區負責。

**When**

- Implementation Agent 嘗試把 assertion 從「入帳一次」改為「入帳兩次也接受」，或刪除該案例。

**Then**

- 修改必須被 `blocked_protected_resource` 阻擋。
- 即使修改後 pytest PASS，也不得接受該結果。
- 事件必須回指被保護的 `PAY-02`。

### OW-S17：修正 pytest 本身的實作錯誤

**對應功能：** OW-F04

**Given**

- `PAY-03` 明確要求付款失敗後 ledger 不得增加資料。
- pytest 因 fixture 使用錯誤帳戶 id 而失敗。

**When**

- Test Agent 修正 fixture，使測試觀察正確帳戶。

**Then**

- 允許在 Test Agent 分區內修正。
- 修正前後 expected behavior 均維持「ledger 不增加」。
- 結果標記為 `test_implementation_defect_fixed`，而不是規格變更。
- 最終仍須在 integration candidate 重跑。

### OW-S18：兩個 Agent 對規格產生不同解讀

**對應功能：** OW-F04

**Given**

- Test Agent 預期非法付款狀態回傳 `409`。
- Implementation Agent 實作 `422`。

**When**

- 固定規格沒有定義應使用哪個 status。

**Then**

- 兩個 Agent 都不得自行選擇並改寫規格。
- 分歧部分停止施工並回報規格缺口。
- 不受影響、可獨立完成的分區可以繼續。
- 人類或被授權的規格決策程序補足語意後，建立新規格版本再繼續。

### OW-S19：Implementation Agent 新增自己的 unit tests

**對應功能：** OW-F04

**Given**

- Implementation Agent 的分區明確包含 `tests/unit/workspace/**`。
- Test Agent 負責的是 `tests/acceptance/workspace/**`。

**When**

- Implementation Agent 為內部計算新增 unit tests。

**Then**

- 寫入應被允許。
- unit tests 不得取代獨立 acceptance。
- Implementation Agent 仍不得修改 `tests/acceptance/workspace/**`。

### OW-S20：以 skip 或放寬門檻製造綠燈

**對應功能：** OW-F04

**Given**

- 壓力或 acceptance test 在 integration candidate 失敗。

**When**

- Agent 加入無規格依據的 `skip`／`xfail`、降低性能門檻、縮小資料集或放寬 assertion。

**Then**

- 變更不得被分類為一般 test implementation fix。
- 必須拒絕進入 integration candidate，或提出規格／驗收變更報告。
- 原失敗結果與修改嘗試必須保留供診斷。

### OW-S109：CI 在沒有 Agent 的情況重跑驗證

**對應功能：** OW-F17

**Given**

- 固定 source snapshot、Verification Manifest 與 environment profile。
- 沒有任何 Agent／LLM service 可用。

**When**

- CI 或人類執行機械 runner。

**Then**

- runner 展開相同 tests、門檻與 seed。
- 產生結構化 verification result。
- PASS／FAIL 判定不依賴自然語言推理。

### OW-S110：相同 Subject 的可重複驗證

**對應功能：** OW-F17

**Given**

- 相同 verification subject 與可重現 environment。

**When**

- 機械流程重跑多次。

**Then**

- test selection 與 expected thresholds 完全相同。
- 非決定性結果必須被辨識為 flaky／environment variance，不能由 Agent臨時解釋成 PASS。

### OW-S111：Agent 嘗試在執行前放寬 Manifest

**對應功能：** OW-F17

**Given**

- Verification Manifest 已凍結。
- 某項壓力測試目前失敗。

**When**

- Agent 嘗試移除 selector、降低 threshold 或改成 `not_applicable`。

**Then**

- 現有 verification run 拒絕使用被未授權修改的 manifest。
- 變更被分類為 verification contract amendment。
- 必須交由後續獨立測試監督流程判斷。

### OW-S112：Property／競態失敗的機械重播

**對應功能：** OW-F17

**Given**

- 隨機競態測試在 seed `R42` 失敗。

**When**

- 人類或 CI 在無 Agent 情況下使用相同 profile 與 seed 重播。

**Then**

- 能重建相同測試輸入與操作順序，或明確報告環境無法重現。
- 不需要原始 Agent 對話。

### OW-S113：大量成功輸出不進入 Agent Context

**對應功能：** OW-F17

**Given**

- 完整 P1 suite 通過並產生大量 stdout。

**When**

- 系統產生完成證據。

**Then**

- 原始輸出保存在 artifact。
- Agent 只取得 suite id、subject id、pass count、duration 與必要摘要。
- 不為閱讀例行成功 log 消耗大量 token。

### OW-S114：失敗後才啟用 Agent 診斷

**對應功能：** OW-F17

**Given**

- 機械 runner 產生 FAIL、failure fingerprint 與受控錯誤片段。

**When**

- Work Package 政策允許 Agent 自主修正。

**Then**

- 只有相關 failure summary、規格條目與最小 source Context 被提供給 Agent。
- Agent 修正後仍由相同無 Agent runner 重驗。
- Agent 的診斷文字不取代機械結果。

### OW-S115：重用既有測試資產

**對應功能：** OW-F17

**Given**

- 新 Work Package 引用既有且仍 active 的 Subsystem acceptance suite。

**When**

- 規格、契約與 test asset 的版本關係仍有效。

**Then**

- Verification Manifest 可以引用並重跑既有 suite。
- 不需要 Agent重新生成相同 pytest。
- 若關係已 stale，機械流程報告 stale，而不是默默沿用。

## 6. 壓力與對抗場景

### OW-P08：Acceptance 保護的對抗測試

OW-F04 的重點不是一般吞吐量，而是驗收期待能否承受反覆的弱化嘗試。

- 對受保護 acceptance 產生刪除案例、加入 skip／xfail、放寬 assertion、降低門檻與縮小 fixture 等變更。
- 所有未引用規格變更的弱化操作都不得被分類為一般 test implementation fix。
- false allow 必須為 0。
- 測試數量應覆蓋支援的弱化類型與語言／pytest profile，不先把任意固定次數寫成業務真理。

### OW-P33：大規模無 Agent 驗證重跑

- 在沒有 Agent／LLM service 的環境執行 P0～P2 適用 suites。
- 所有 test selection、threshold、seed 與結果判定都由 manifest＋runner 完成。
- Agent token cost 必須為 0。
- 失敗仍要產生足以供後續機械重播與選擇性 Agent 診斷的 artifact。

### OW-P34：輸出與 Token 成本隔離

- 產生大量 PASS logs、重複 failure traces 與大型測試 artifacts。
- Artifact storage 可以成長至 profile 上限，但 Agent Context 只接收有界摘要。
- 同一 failure fingerprint 不得重複注入相同完整輸出。
- 例行 verification 的 token 消耗不得隨 pytest 總輸出線性增長。

## 7. pytest 投影規則

- 每個場景以舊 ID 作 traceability key，例如 `@pytest.mark.ddh_scenario("OW-S16")`。
- pytest／fixture／configuration／profile 必須能在沒有 Agent／LLM service 時重跑。
- 實際檔名、suite 組裝、stale 判定與監督流程由 Mechanical Verification and Test Governance 規格統一管理。
- 原 archive 中的示範 test names 只作歷史參考，不是新規格的檔案配置決策。

## 8. 舊 ID 遷移

### 功能

| 舊 ID | 已確認項目 |
|---|---|
| OW-F04 | 保護規格與獨立驗收 |
| OW-F17 | 可重用的無 Agent 機械驗證 |

### 場景

| 舊 ID | 已確認項目 |
|---|---|
| OW-S16 | Implementation Agent 嘗試改寫 acceptance expectation |
| OW-S17 | 修正 pytest 本身的實作錯誤 |
| OW-S18 | 兩個 Agent 對規格產生不同解讀 |
| OW-S19 | Implementation Agent 新增自己的 unit tests |
| OW-S20 | 以 skip 或放寬門檻製造綠燈 |
| OW-S109 | CI 在沒有 Agent 的情況重跑驗證 |
| OW-S110 | 相同 Subject 的可重複驗證 |
| OW-S111 | Agent 嘗試在執行前放寬 Manifest |
| OW-S112 | Property／競態失敗的機械重播 |
| OW-S113 | 大量成功輸出不進入 Agent Context |
| OW-S114 | 失敗後才啟用 Agent 診斷 |
| OW-S115 | 重用既有測試資產 |

### 壓力

| 舊 ID | 已確認項目 |
|---|---|
| OW-P08 | Acceptance 保護的對抗測試 |
| OW-P33 | 大規模無 Agent 驗證重跑 |
| OW-P34 | 輸出與 Token 成本隔離 |

## 9. 拆分後待補

### 已確認但尚未形成完整內部規格

- P0 功能／基本競態、P1 Subsystem 完整驗收、P2 高競爭／對抗、P3 Soak／故障風暴四層 Profile。
- 每個 Subsystem 依使用頻率、burst、concurrency、data volume、state duration、recovery、failure impact、external side effects 與成本建立 Stress Applicability。
- Stress test 標記 `required`、`conditional` 或 `not_applicable`，後者必須附業務理由。
- 主 Agent是 Verification／Stress Contract 編譯者，不是規格來源。
- `user_explicit`、`referenced_approved_spec`、已核准 `ddh_default_invariant` 可形成驗收；未確認假設不能。
- 一般節點完成後只留下可重跑 pytest／fixture／configuration／profile，不保存歷史 PASS。

### 待補

- Test asset 依 Global／Domain／Subsystem／Module 的存放與索引。
- 規格條目、場景、pytest、fixture、profile 與 node identity 的 schema。
- active、stale、superseded、quarantined、deprecated／archived 生命週期。
- 修改節點後的 impact closure 與 suite selection。
- Test implementation defect 與 acceptance change 的判定。
- skip／xfail、assertion weakening、threshold lowering、fixture shrinking 的獨立監督。
- Independent Critic／不同模型／mutation testing 的角色與機械邊界。
- Verification Manifest authority、freeze、amendment 與無 Agent runner interface。
- 本 Subsystem 自己的完成判準與 Stress Contract。

以上仍是 gap，不構成實作決策。

## 10. 已確認的跨 Subsystem Contract

### CIM-MVTG-001：Frozen Candidate to Verification Subject

- MVTG 收到 verification intake 後，必須核對 task specification、frozen candidate、Verification Contract、test asset manifest、environment profile 與 invalidation epoch。
- 只有完整 identity 與 digest 一致、必要驗收均有無 Agent 可執行資產時，才能建立 `verification_subject_ready`。
- Missing required tests、stale assets、identity mismatch 或 specification drift 必須回報 `verification_not_ready`／`subject_rejected`，不得自行移除驗收。
- Required suites、stress applicability、threshold、skip／xfail policy 與 fixtures 必須在執行前固定。
- Subject 建立後，runner 不得臨時替換 candidate、漏跑 required suites 或降低 threshold。
- Candidate、規格、Contract、test assets 或 environment profile 改變時，舊 subject 必須失效並建立新 identity。

本 Contract 的 authority 在 Domain overview；本節只保存 MVTG 的責任投影。

## 11. 已確認的 Recovery Chain

### RC-DOM-003：Rebuildable Artifact Failure

- Verification intake、suite selection 與 runner plan 是 derived artifacts，可從固定 subject inputs 重建。
- Rebuild 不得改變 required suites、stress applicability、threshold、fixtures 或 skip／xfail policy。
- Identity mismatch 時，舊 subject／result 必須失效，不得覆寫成等價。
- Primary builder 故障時可使用已驗證 fallback builder；所有安全路徑耗盡才輸出 `platform_blocked`。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-MVTG-004：Runner Environment Failure

- MVTG 必須區分 infrastructure failure 與 product／test failure。
- Workspace、environment、cache、resource collision 或 runner crash 由無 Agent recovery 重建，並重跑完全相同的 Verification Subject。
- Environment recovery 不得修改 candidate、tests、threshold、fixtures 或 suite selection。
- Failure origin 不明時只在 clean runner 做一次分類重播；安全路徑耗盡才輸出單次 `platform_blocked`。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-DOM-MVTG-005：Product Verification Failure

- MVTG 必須先排除 infrastructure／test implementation failure，再發布 product Failure Bundle。
- Impact closure 必須消費 System Map query 並經 live source 確認；suite expansion 不授予 write scope。
- Candidate 修改後建立新 Verification Subject，沿用相同 task specification 與 protected acceptance。
- 修復循環自動執行，直到 PASS、需要變更人類決策邊界或 attempt budget 依規則耗盡。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

## 12. 已確認的 System Map 使用 Contract

### SMQ-001：Architecture Impact Query

- Product verification failure 的 impact closure 必須消費 failed-node reverse-dependency query。
- Verification Subject 的 suite candidate selection 必須消費 changed-node／affected-dependent query。
- System Map 只能產生受影響 tests 候選；required acceptance 仍由 task specification 與 Verification Contract 決定。
- Query result 未被消費、已 stale 或被當成驗收 authority 時，transition contract 必須失敗並自動重查／fallback。

System Map 本身的資料與查詢設計不屬於 MVTG。

## 13. 已確認的大型能力：Test Asset Quality Governance

### 13.1 問題定義

pytest 可以作為 Work Package 完成與後續 regression 的長期可重播 evidence，前提是先證明測試：

1. 忠實對應固定任務規格與業務場景。
2. 對錯誤實作具有足夠偵測力。
3. 不因環境、順序、時間或共享狀態產生不穩定結果。
4. 沒有被 Agent 透過 assertion、fixture、threshold、skip／xfail 或 suite selection 放寬。
5. 在 source、contract、specification 或 dependency 改變後仍然適用。

單一 code coverage 百分比、pytest PASS、Agent／Critic 評語或測試數量都不能單獨證明品質。

### 13.2 建議的四個品質軸

| 品質軸 | 要回答的問題 | 主要證明方式 |
|---|---|---|
| Semantic fidelity | Test 是否真的驗證規格要求，而不是實作細節？ | specification／scenario mapping、oracle source、independent Critic |
| Fault sensitivity | 錯誤實作是否會讓 Test 失敗？ | mutation testing、known-bad probes、property／metamorphic tests、negative／boundary cases |
| Execution reliability | 相同 Subject 是否能穩定重跑？ | isolation、repeat runs、order randomization、seed control、flaky detection |
| Lifecycle validity | 節點改變後 Test 是否仍有效且覆蓋 impact closure？ | System Map impact query、live-source verification、invalidation／stale／supersede rules |

這四軸分開判定，不壓成容易被鑽漏洞的單一總分。

### 13.3 Test Quality Contract

每組 required test assets 在實作前，先由任務規格編譯 Test Quality Contract。它不是新 SSOT，只是可機械執行的品質要求：

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

不同層級使用不同最低要求，不採全域同一嚴格度：

| 層級 | 最小品質重點 |
|---|---|
| Module | examples、boundary／negative cases、核心 properties、風險相符的 mutation sample |
| Subsystem | 完整業務狀態轉移、failure／recovery、contract boundaries、必要 concurrency |
| Domain | 跨 Subsystem 業務流程、資料一致性、reverse-dependent regression、風險相符的 load／soak |
| Global | 跨 Domain invariants、架構／相容性與全域不可破壞條件 |

### 13.4 Test Asset Admission Pipeline

```text
fixed specification and scenarios
→ compile Test Quality Contract
→ Test Agent implements pytest in parallel
→ collect／lint／schema and marker validation
→ mechanical acceptance weakening guard
→ independent Test Critic
→ scenario replay
→ mutation／known-bad／property probes
→ determinism／isolation checks
→ admitted test asset version
```

Admission 原則：

- Test Agent 可以實作與修正測試，但不能自行 admission。
- Implementation Agent 可以新增自己的 unit／diagnostic tests，但不能用它們取代 protected acceptance。
- Critic 只提供獨立語意審查，不是 authority；admission 仍須固定規格映射與機械證據。
- Expected behavior、threshold、scenario boundary 或 required suite 的改變不是 test repair，必須走規格變更流程。
- 新功能沒有 known-good implementation 時，以規格 examples／invariants、property／metamorphic relations、known-bad mutants 與獨立 scenario derivation 建立偵測力，不能讓測試照抄實作。

### 13.5 生命周期與過期

```text
draft → candidate → admitted → active
                     ├→ stale
                     ├→ quarantined
                     ├→ superseded
                     └→ archived
```

- Test 不因時間經過自動過期，而由 specification、source contract、node dependencies、fixture schema、runner profile 或 mapped impact closure 改變觸發 invalidation。
- System Map 只提供 affected tests 候選；live source 與固定規格決定實際 stale closure。
- Required test flaky 時不能作為 PASS gate；先 quarantine 並由等價、已 admission 的 coverage 接手，否則 verification 為 `not_ready`。
- 一般 Work Package 完成後仍只長期保留 pytest／fixture／configuration／profile；quality mapping、scenario IDs、invalidation metadata 應嵌入這些可重播資產，不額外保存歷史 PASS logs。

### 13.6 如何防止同一模型放寬測試

需要多層防線，而不是只指定「另一個模型」：

1. Proposer 與 admission execution identity 分離。
2. Protected acceptance manifest 固定 expected behavior、threshold、fixtures classes 與 required suites。
3. Mechanical diff guard 阻擋 assertion deletion、threshold lowering、fixture shrinking、skip／xfail 與 case removal。
4. Mutation／known-bad probes 證明修改後仍能抓住違規行為。
5. Independent Critic 重新從規格推導場景，不採用 proposer 結論作為 authority。
6. Test asset 變更後建立新 identity 與 Verification Subject，不能回填舊 PASS。

是否強制使用不同模型／model family，應以盲測與 mutation-detection 成效相對 token 成本決定；但同一執行實例不得自審自批是最低要求。

### 13.7 建議驗收標準

- 每個 required specification／scenario 都有 admitted test mapping；不得有無測試的 required requirement。
- 每個 test 都能回指規格或明確標記為 diagnostic，避免 orphan acceptance。
- Required suite 在選定 determinism profile 下無 flaky result。
- Mutation threshold 依 layer／risk profile 固定；不使用全專案單一百分比。
- System Map 查出的 affected nodes 已轉成 regression candidate，並經 live source確認是否納入。
- Admission 可以在沒有 Agent／LLM service 時重播必要的 mechanical guards、pytest、mutation probes 與 determinism checks。
- Test Quality Contract 未滿足時為 `verification_not_ready`，不能以產品 PASS 宣告完成。

### 13.8 尚未決定

- Test Asset Quality Governance 是否從目前 MVTG 拆成獨立 Subsystem，或保留為 MVTG 內部大型 component。
- Specification／scenario／test／fixture／profile 的正式資料模型與儲存路徑。
- 不同 layer／risk 的 mutation、property、repeat、randomization 與 stress profiles。
- Independent Critic 的模型隔離要求、成本預算與 fallback。
- Hidden／holdout probes 是否需要，以及如何同時維持可重播 Evidence Retention。
- Equivalent mutants、不可穩定重現 tests 與外部依賴 tests 的處理。
- Test quality health check 的觸發時機與批次策略。

本節的問題邊界、四軸品質模型、Test Quality Contract、Admission Pipeline、生命週期、防放寬機制與驗收原則已確認；不構成 Subsystem 拆分或實作核准。

## 14. 待確認架構決策：拆分 Test Governance 與 Verification Execution

### 14.1 方案

| 方案 | 結構 | 優點 | 主要風險 |
|---|---|---|---|
| A：維持單一 MVTG | 同一 Subsystem 內分成 governance 與 runner components | 文件與 interface 較少 | Admission authority 與執行責任容易再次混合；大型功能持續膨脹 |
| B：拆成兩個 Subsystems | Test Asset Quality Governance（TAQG）＋ Mechanical Verification Execution（MVE） | 權責、identity、成本與 failure routing 清楚；runner 可維持純機械、唯讀 | 多一組正式 handoff contract 與 identity |

### 14.2 建議採用方案 B

#### Test Asset Quality Governance Subsystem（TAQG）

負責：

- 從任務規格編譯 Test Quality Contract。
- 管理 specification／scenario／test／fixture／profile mapping。
- Test draft、candidate、admitted、active、stale、quarantined、superseded、archived lifecycle。
- Mechanical Acceptance Guard。
- Independent Critic orchestration。
- Mutation／known-bad／property／determinism quality admission。
- Test asset invalidation、repair proposal 與新版本 admission。

不負責：

- 執行產品 candidate 的正式 Verification Subject。
- 修改產品 source。
- 決定規格、expected behavior 或人類 write scope。

#### Mechanical Verification Execution Subsystem（MVE）

負責：

- 接收 immutable Verification Subject。
- 驗證 subject 只引用 admitted test asset manifest。
- 建立／修復 runner environment。
- 無 Agent 執行 pytest／stress suites。
- 分類 infrastructure、product、suspected test defect 與 specification ambiguity。
- 發布綁定 subject identity 的機械結果。

不負責：

- 修改 pytest、fixture、threshold、suite selection 或 Test Quality Contract。
- Admission test asset。
- 重新解釋規格。

### 14.3 核心 Handoff

```text
Task Specification
→ TAQG compiles Test Quality Contract
→ Test Agent produces draft assets
→ TAQG admits immutable Test Asset Manifest
→ CIM provides Frozen Candidate
→ MVE creates Verification Subject
→ MVE executes admitted assets
   ├─ product failure → Agent repair loop
   ├─ infrastructure failure → MVE automatic recovery
   └─ suspected test defect → TAQG supervised repair flow
```

必要不變量：

- MVE 只能讀取 admitted test asset version，不得執行 draft／candidate tests 作為正式 acceptance。
- TAQG admission 新版本後，既有 Verification Subject 不被覆寫；必須建立新 subject。
- MVE 懷疑 test defect 時只能送出 defect candidate，不能直接改 test 或忽略失敗。
- TAQG Critic unavailable 時，不得降級為 MVE／Repair Agent 自行 admission。
- 拆分只增加機械 handoff，不增加人工 Checkpoint。
- Quality admission 可在 test asset 改變時執行；頻繁的產品 verification 只使用已 admitted assets，避免每次都支付 Critic／mutation 成本。

### 14.4 業務場景

**Given**

- `workspace_path_escape_scenario` 的 pytest 已是 admitted version 3。
- MVE 驗證新產品 candidate 時發現 test helper setup error。
- Test Repair Agent 提出 draft version 4。

**When**

- MVE 將 suspected defect 與固定 subject 送交 TAQG。
- TAQG 執行 guard、Critic、replay 與 mutation probes。

**Then**

- Version 4 admission 前，MVE 不得把 draft 4 用於正式 PASS。
- Version 4 admission 後，建立新 Test Asset Manifest 與新 Verification Subject。
- MVE 以新 subject 重跑；不覆寫 version 3 的歷史 identity。
- 全流程不需要人工 Checkpoint，除非 expected behavior／threshold／scenario semantics 必須改變。

### 14.5 對應機械測試

```text
test_mve_accepts_only_admitted_test_asset_manifest
test_mve_cannot_modify_or_admit_test_assets
test_taqg_cannot_publish_product_verification_result
test_suspected_test_defect_routes_from_mve_to_taqg
test_new_test_asset_version_always_creates_new_verification_subject
test_unavailable_critic_never_falls_back_to_self_admission
test_split_handoff_adds_no_human_checkpoint_for_semantics_preserving_repair
test_quality_admission_cost_is_not_repaid_for_unchanged_test_assets
```

### 14.6 決策影響

若採用方案 B：

- 現有 MVTG 規格拆成 TAQG 與 MVE 兩份 Subsystem specification。
- `CIM-MVTG-001` 重新命名並拆成：
  - `TAQG-MVE-001 Admitted Test Asset Handoff`
  - `CIM-MVE-001 Frozen Candidate to Verification Subject`
- `RC-MVTG-004` 歸 MVE。
- `RC-DOM-MVTG-005` 由 MVE 發出 failure，Domain／主 Agent負責 repair routing。
- `RC-MVTG-006` 改為 `RC-MVE-TAQG-006`。

以上是架構提案，尚未採用。
