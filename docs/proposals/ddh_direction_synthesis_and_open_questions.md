# DDH 開發方向整理與待釐清事項

**狀態：** Discussion Synthesis  
**日期：** 2026-08-02  
**規範效力：** 無  
**實作授權：** 無

本文件整理目前討論中已明確確認的方向、仍待決策的提案、與既有文件的衝突，以及 DDH 尚未納入或尚未具體設計的能力。

本文件不是規格書、Architecture Decision、System Map 或施工授權。未經人類明確確認，不得把「候選方向」或「建議」轉成已核准規範。

---

## 1. 核心治理命題

DDH 的治理重心，是證明使用者期待的功能確實完成，而不是證明 Agent 經過了足夠多的治理儀式。

這項治理成立的前提是：

1. 使用者期待已被整理成足夠完整、可判定的功能敘述。
2. 規格中的業務場景能投影成可執行驗證。
3. pytest、邊界案例、錯誤案例與必要的壓力／效能測試，足以對應該次任務的風險。
4. 測試通過只能證明「目前候選實作符合已表達的規格」，不能反向證明規格本身完整。
5. Agent 不得藉由弱化驗收、改寫預期結果或避開真實執行，製造表面上的綠燈。

最重要的權責分離是：

> 使用者期待存在任務規格書；pytest 等測試是可執行證明；System Map 是理解專案與規劃 scope 使用的真實架構索引。三者不能互相冒充權威。

---

## 2. 目前已確定的方向

### 2.0 專案名稱

專案名稱已確認由 **ADHD** 改為：

> **DDH — Demand-Driven Harness（需求驅動框架）**

名稱代表：

- **Demand：** 使用者寫明的 Agent 目標，以及任務規格固定引用的長期規範。
- **Driven：** scope、施工分層、Agent 分工、驗證強度與停止條件，都從需求與業務風險反推。
- **Harness：** 提供足以證明需求落地並阻擋明顯越界的測試、邊界、整合、證據與例外升級能力。

這項命名不表示回到舊 ADAD 的重型治理；Harness 的存在與強度必須能由需求、業務場景或風險推出。

現有檔名、ADR、目錄、程式識別字與歷史文件仍可能使用 ADHD。它們屬於待規劃的名稱遷移範圍，不能因改名而抹除歷史決策來源。

### 2.1 每次任務以規格書作為完成判定的 SSOT

- 每次施工都要有足以判定成功與失敗的規格。
- 規格書定義使用者希望「做成什麼」，以及什麼證據足以算完成。
- 規格形式與驗證深度要依施工層級、業務風險與外部副作用調整，不採所有任務一律同等嚴格。
- 規格確認仍是必要動作；要討論的是確認方式與嚴格程度，而不是取消確認。

已確認的權威模型如下：

| 資產 | 定位 | 對本次任務的作用 |
|---|---|---|
| 已核准的 Architecture Decision／架構規範 | 保存長期有效的架構限制 | 由任務規格固定版本引用 |
| 長期業務規格 | 保存跨任務持續有效的業務規則 | 由任務規格固定版本引用 |
| 本次任務規格書 | 固定引用版本、目標、scope、驗收與風險 | 本次任務唯一的完成判定 SSOT |
| System Map | 記錄 live project 的實際架構與關係 | 只供理解、查詢、視覺化與 scope 規劃 |

因此不再採用「System Map＋Semantic Specification 雙 SSOT」：

- 任務執行只依本次已確認並凍結的任務規格判定。
- 長期架構規範與業務規格是任務規格引用的規範來源，不各自形成另一個任務控制面。
- live source、schema、configuration 與 API 是判斷目前實際狀態的證據，不另命名為 SSOT。
- planned architecture 應存在 proposal、Architecture Decision 或任務規格中，不得提前寫入 System Map 成為 actual state。

### 2.2 採 Global → Domain → Subsystem → Module 分層

各層級規格應從業務場景產生對應測試：

| 層級 | 驗證焦點 | 目前例子 |
|---|---|---|
| Global | 整體產品或跨 Domain 的使用者旅程 | 完整產品流程能否成立 |
| Domain | 一個業務領域能否正常運作 | Workspace Domain 能否完成路徑解析、資產發現與驗證編排 |
| Subsystem | 協作、狀態與業務流程是否成立 | 狀態機能否處理規格中的業務場景 |
| Module | 局部契約、計算與輸入輸出是否正確 | Server Module 的計算輸入能否得到正確輸出 |

施工範圍可以是整個 Domain、Subsystem 或單一 Module，不預設所有工作都必須拆成小 Task。

### 2.3 驗證強度由規格與風險決定

- 一般正向功能測試不足以單獨代表完成。
- 必須依規格加入適當的邊界值、反向案例、錯誤路徑與不變量。
- 當功能具有容量、延遲、併發或穩定性要求時，規格必須定義對應壓力／效能測試。
- 測試強度應與語意風險成比例，不應由檔案數量或實作複雜度單獨決定。

### 2.4 同層級驗證失敗時，以該層整體重新分析

- Module 測試失敗時，不應只為 failing assertion 做局部補丁，而要重新檢查該 Module 的契約與實作。
- Subsystem 場景失敗時，要回到整個 Subsystem 的狀態、互動、錯誤處理與相關 Module 檢查。
- Domain 驗證失敗時，要重新分析 Domain 內跨 Subsystem 的業務流程與一致性。
- 「整層重新分析」目前不等於自動取得整層所有檔案的寫入權；如果根因超出已核准 scope，仍需提出 scope 變更。

### 2.5 Scope 內保留 Agent 的實作自主性

- 在規格、scope、禁止事項與風險邊界內，Agent 可以自主實作、執行測試、診斷、修正並重驗。
- 一般測試關卡通過後自動繼續，不要求逐關人工 Checkpoint。
- 不恢復舊 ADAD 的小 Task、單檔常態鎖、固定角色鏈或每模組人工核准。
- Scope 內的程式風格應以模組化、可理解、必要註解與不越界重構為主，避免用大量固定形式限制解法。

### 2.6 採例外升級

以下情況應停止自主施工並向人類提出結構化報告：

- 必須改變架構方向、資料契約、公開介面或既有規格。
- 必須擴大核准的修改範圍或改變驗收標準。
- 涉及未明確允許的部署、發佈、資料庫、憑證、網路或其他外部副作用。
- 規格資訊不足，無法判定正確行為。
- 驗收反覆失敗且沒有新增診斷資訊。
- 風險或預算已超出規格允許範圍。

報告至少要說明已嘗試內容、證據、失敗分類、目前缺口與可選下一步。

### 2.7 System Map 不是 SSOT

System Map 的角色已確認為：

- 長期維護的「實際架構」紀錄。
- 可查詢、可視覺化的 architecture index 與 relationship graph。
- 人與 Agent 快速理解專案、規劃任務 scope、組裝必要上下文與分析影響範圍的入口。
- 架構施工完成後，依真實專案狀態同步更新的索引。

System Map 不具有以下權力：

- 不授權 Agent 修改任何檔案。
- 不定義未來或理想架構。
- 不取代任務規格書的驗收語意。
- 不得在與 live source、schema、configuration 或 API 衝突時，被當成真實狀態的最終證據。
- discovery metadata 也不得被當作施工授權。

### 2.8 目前仍是設計討論階段

尚未授權修改 runtime、CLI、hook、schema、System Map、既有治理狀態或專案原始碼。本整理也不構成上述授權。

---

## 3. 已提出但尚未確認的設計

以下內容具方向性，但目前不能標記為定案：

### 3.1 Work Package 與任務規格書

`SPEC-WP-001` 已確認：

- Task Specification 是每次任務 SSOT。
- Work Package 是從 Task Specification＋current state 產生、可自動重建的
  execution projection。
- 兩者邏輯分離，小型任務可以存在同一 Specification Package。
- Human 一次確認 Task Specification version；不逐次批准 projection。
- Goal／behavior／acceptance／scope／risk／external authority change 才建立新
  Task Specification version。
- Partition／Context／runner／recovery／ordering change 只建立 projection
  generation。
- Layered readiness 以能否形成 executable expected behavior 判定，不以文件
  長度或欄位填滿率判定。

Exact schema、實體檔案 layout 與 runtime projection mechanism 留待實作設計。

### 3.2 L0～L3 風險 Gate

`DDH-RISK-001` 已確認 Change Authority 與 Verification Intensity 分軸：

| 等級 | 候選情況 | 候選流程 |
|---|---|---|
| L0 | 文件、非治理資產、純整理 | 使用者寫明的 Agent 目標作為任務 SSOT；直接修改＋輕量驗證 |
| L1/L2 | 已確認架構範圍內的程式修改 | 規格／執行封套＋必要 ownership＋驗證＋自動審查 |
| L3 | 架構、schema、跨模組契約、不可逆操作 | 人類核准後施工 |

L1 是 localized existing-contract change；L2 是 cross-node／integration work
within existing contracts；L3 涵蓋 architecture、schema、public／data contract、
expected behavior、scope expansion、permission、external／irreversible operation
與 budget increase。

L0 已確認的規則：

- 使用者明確寫下的 Agent 目標，就是該次 L0 任務的 SSOT 來源。
- Agent 可以從該目標整理修改 scope、禁止事項與驗證方式，但整理結果只是執行投影，不能改寫或取代使用者目標。
- 不建立正式 Work Package、版本凍結、ownership、獨立審批或完整證據包。
- 純討論與唯讀分析不屬於施工，不要求 L0 任務規格。
- 如果實際工作涉及程式行為、治理資產、架構規範、契約或外部副作用，就必須重新分類，不能繼續使用 L0。

L1 → L2 Harness strengthening 可自動進行；任何 L3 authority change 只停止
affected lanes，保留 candidate／diff 並提出 structured exception。Verification
Profile V0～V3／external lane 依 business scenarios、criticality、impact 與 stress
applicability 決定，不能提供 write authority。

### 3.3 Clean Code Harness

`DDH-CODE-001` 已確認：

- 五條規則是 versioned Agent Clean Code Self-Check Profile，不是假裝成機械
  proof。
- 20 行、兩層 nesting、avoid else 是 soft defaults／review signals；合理例外
  允許 bounded Why。
- Comments 只解釋 Why，不設定數量。
- 童軍營地法則的 scope relevance 是 self-check，actual write boundary 由 CIM
  mechanical enforcement。
- Self-check result 是 Agent claim，不能取代 pytest、scope／diff 或 review。
- Syntax、configured lint／type、scope、secret、dependency、test integrity、
  generated／vendor write 與 broad suppression 才是 high-confidence hard gates。
- Legacy 採 new／worsened incremental policy，不要求全庫先清理。

Exact linter／reviewer／language profile implementation 尚未授權。

### 3.4 主 Agent 與子代理

- 主 Agent 預設單一執行。
- 只有當工作可獨立、寫入範圍不衝突、整合成本合理且平行收益明確時，才啟用子代理。
- 子代理只取得最小 Context Envelope，不得自行擴大 scope。
- 主 Agent 保留完整規格解釋與整合權。

這個方向已形成共識，但風險評分、上下文請求、驗證整合與失敗回收的資料模型尚未確認。

### 3.5 條件式寫入所有權租約

已確認 ownership 的完整用途：

- 多個 Agent 可以平行施工，最典型情境是產品實作與 pytest 撰寫同時進行。
- 主 Agent先依固定規格建立「平行施工寫入分區」。
- Implementation Agent 不得修改由 Test Agent 負責的驗收測試。
- Test Agent 不得修改產品實作來使測試通過。
- 共享契約由主 Agent集中處理；跨區需求必須重新分配或升級。
- 平行期間的測試只算 provisional；所有 writer 停止後，必須對固定 integration snapshot 執行最終驗證。
- Agent 失聯或分區到期時，先檢查並保存殘留 diff，不得直接讓其他 Agent接手。
- 不恢復逐檔常態 Source Lock，單一 Agent 施工也不啟用此流程。

尚未決定的是 Write Guard、分區 registry、Candidate Identity、Patch Admission、隔離工作區與復原協調器等實作方式。原始規格先行討論已封存於 `ddh_execution_domain_discussion_archive.md`，並拆分為：

- `ddh_execution_and_orchestration_domain_overview.md`
- `parallel_work_coordination_subsystem_specification.md`
- `candidate_integrity_and_mutation_subsystem_specification.md`
- `context_broker_subsystem_specification.md`
- `test_asset_quality_governance_subsystem_specification.md`
- `mechanical_verification_execution_subsystem_specification.md`
- `mechanical_verification_and_test_governance_subsystem_specification.md`（split archive）
- `orchestration_learning_and_evolution_subsystem_specification.md`

### 3.6 編排長期記憶與受控演進

候選方向包括：

- 原始 log 與對話只是短期事件。
- 只把重複、具證據的派工問題整理成長期編排經驗。
- 每條記憶具有適用條件、證據、信心、版本、失效條件與衝突處理。
- 演進 Agent 只提出角色 prompt 或 Context Envelope 模板候選。
- 獨立 Critic 以回放及小範圍試用驗證，效果變差則回滾。
- 不得由自我演進修改規格、權限、架構判定、驗收、量測或人工升級條件。

此能力尚未進入資料模型與最小流程設計。

---

## 4. 目前存在的主要衝突

| 衝突主題 | 一側想法 | 另一側想法 | 需要處理的問題 |
|---|---|---|---|
| System Map 權威性 | 既有文件稱它為 Architecture SSOT | 最新決定是 actual architecture index | **已解決：** Decision 0002 固定 actual-only、非 SSOT 邊界；詳細 System Map 模型仍可調整 |
| SSOT 數量 | 既有文件採 System Map＋Semantic Specification 雙 SSOT | 已確認由任務規格固定引用長期架構規範與業務規格 | **已解決：** 本次任務規格是完成判定 SSOT；System Map 退出權威鏈 |
| 完成順序 | 先通過 System Map architecture conformance，再驗證功能 | 先依任務規格證明功能，架構改變後同步 Map | **部分解決：** Map 不是 acceptance authority；同步時點與 maintenance gate 仍待 System Map 方案確認 |
| Risk Gate | L0 可直接修改 | 每次施工都要有可追溯的任務 SSOT | **已解決：** L0 以使用者寫明的 Agent 目標為 SSOT 來源；Agent 整理內容只作執行投影 |
| Ownership | 舊的逐檔常態 Source Lock 應淘汰 | 平行實作與 pytest 需要避免交叉寫入 | **已解決用途：** 採主 Agent管理的平行施工寫入分區；機械實作仍待由場景反推 |
| 實作與測試平行 | 可一邊寫程式、一邊寫 pytest | 同一 Agent 可藉修改測試配合錯誤實作 | 如何固定 expected behavior、保持測試獨立性並允許修正測試程式本身 |
| 分層失敗處理 | 測試未通過就以該層為整體修改 | Scope 不能被 Agent 自行擴大 | 「整體」應先代表分析與重驗範圍，不自動代表寫入權 |
| Coding Harness | 需要具體且可阻擋的硬規則 | DDH 要避免 ADAD 式過度嚴格 | 哪些規則是機械門檻、review 指引或可配置 profile |
| 註解規則 | Scope 內要求寫註解 | Clean Code 只允許必要的 why 註解 | 應改成「必要處寫出原因」，不能要求註解數量 |
| 壓力測試 | 通過壓力測試才能完成 | 並非每種變更都有可用或有意義的負載模型 | 是否允許規格標示 required／not applicable，及誰判定 |
| 驗證工具 | 目前討論大量使用 pytest | DDH 可能治理多語言專案 | 要決定 pytest 是目前實作選擇，還是規格模型中的硬依賴 |
| Global 階層 | 最新說法為 Global → Domain → Subsystem → Module | 既有 Map 為 Project → Domain → Subsystem → Module | Global 是驗證層名稱、Project root 別名或新 Entity type |
| 人類核准 | 規格確認一定要有 | 例外升級、不逐關審批 | 哪些低風險規格可用極簡確認，哪些必須明確批准 |

---

## 5. 尚未加入或尚未具體化的功能

### 5.1 規格完整度與 readiness

- 分層 Task Specification 資料模型。
- 各層最低必要欄位。
- 施工前的規格完整度檢查。
- 無法驗證、矛盾或缺少 expected behavior 時的回報格式。
- 規格凍結、修訂、diff 與核准方式。
- 長期 Domain 規範與單次任務規格之間的版本固定、解析及失效檢查機制。

### 5.2 規格到測試的可追溯性

- `spec item → business scenario → test case → invocation → result → source candidate` 的完整關聯。
- 正向、反向、邊界、absence／null、錯誤與恢復案例。
- 測試是否真正執行，以及 unverified 與 pass 的明確區別。
- 測試程式錯誤的修正流程。
- 禁止藉刪測試、放寬 assertion 或修改 expected outcome 做綠的 anti-gaming 規則。

### 5.3 分層驗證與影響閉包

- Global、Domain、Subsystem、Module 各自的必跑測試與可選測試。
- 修改下層後，哪些上層驗證必須失效並重跑。
- 同層失敗時的整體診斷、修正、重驗循環。
- 根因跨出 scope 時的變更提案。
- 跨層規格與跨 Domain 情境的表示方式。

### 5.3.1 pytest 資產管理與獨立驗收監督

`TAQG-QUAL-001／002／003` 已確認：

- Test quality applicability、門檻來源、profile calibration 與 self-evolution boundary。
- Admission、semantic validity 與 candidate execution 是三條獨立狀態軸。
- pytest 是否過期由 TAQG 依固定 identity、versioned invalidation rules、System Map bounded query 與 live source 機械判定；主 Agent 只協調 disposition。
- Product source change 通常要求重跑，不使 pytest semantics 自動 stale。
- Spec／oracle／test／fixture／helper／必要 contract 或 schema 改變時，才依規則產生 suspect／stale／quarantined／retired。
- 修改、替換、新增與刪除由固定 Disposition rules 路由；Test Agent 不能 admission 自己的變更。
- 新 System Map node 不等於固定新增 pytest；以 `specification → business scenario → test coverage` 判定。
- 刪除測試前必須有規格移除或 admitted replacement、引用檢查、coverage closure、Independent Critic 與 write scope。
- 大型 test repository 使用增量 invalidation、bounded query、atomic manifest epoch 與零 Agent routine rerun。

`TAQG-ASSET-001` 亦已確認：

- 每個專案以 versioned Test Layout Profile 描述 layered、colocated 或既有測試結構。
- Path／檔名與 discovery index 只協助找資產，不具 admission authority。
- Python MVP 只要求 pytest adapter；DDH schema 保持 runner-neutral，不提前實作其他語言。
- Fixture／helper／configuration 必須進入 dependency digest closure。
- Test Asset Inventory 是可自動重建的 derived cache。
- 不從 rename／move 猜測跨版本永久 identity；替代關係使用 explicit supersession declaration。

`DDH-INV-001` Domain-wide Invalidation and Reconciliation 已確認：

- Event 只作快速通知；protected transition 前以 current canonical identities reconciliation。
- 各 Subsystem 保有自己的 local state machine，不建立中央全域狀態機。
- At-least-once delivery、idempotent consumers、generation 局部順序與 bounded coalescing。
- Event／queue 遺失時由 canonical current state 自動重建。
- Raw events reconciliation 後刪除，不形成永久 Evidence 或 legacy freshness chain。

`TAQG-PORT-001` Test Portfolio Health and Maintenance 已確認：

- Semantic fidelity、fault sensitivity、execution reliability、lifecycle validity 與 cost observation 分開判定，不使用單一總分。
- Routine audit 無 Agent 執行；只有 repair、非機械語意比較、dedup proposal 或規格缺口使用 Agent。
- Similarity 只能找 duplicate candidates；consolidation 必須證明 coverage／fault detection 不降低並通過 Independent Critic。
- 一般 product source change 不觸發全庫 audit；test／spec／profile／inventory change、escaped bug 或 approved full-audit trigger 才執行相應 audit。
- Maintenance budget 只能改變 sharding、cache 與 approved sampling，不能降低 required quality。

`MVE-RESULT-001` Observed Result Classification, Impact Assessment and Routing 已確認：

- Failure classification 與 impact scope assessment 是兩條獨立判定軸。
- Product failure 不代表原 verification／write scope 足夠；actual diff、failed scenario 與完成前都必須消費 System Map query。
- 原 scope 外 nodes 可以自動加入 verification closure，但不能自動取得 write permission。
- 需要修改 scope 時更新 versioned Work Package／Task Specification scope；只有 expected behavior 改變時才修改 behavioral specification。
- System Map 漏掉 relation 時以 live source 作現況證據，擴張 verification closure 並觸發 Map maintenance。
- `impact_unknown`、query 未被下游消費或 outside-scope repair 未核准時不能宣告完成。

`PWC-INTEG-003` Asynchronous Module Fork-Join and Subsystem Verification 已確認：

- pytest／fixture／helper／test configuration 的寫入是 Test Asset 施工；draft diagnostic PASS 不是正式 MVE。
- Subsystem 內可分離的 Modules 可以非同步進行 product／test construction。
- Test Agent 與 Implementation Agent 分開擁有 acceptance／product write partitions；shared contracts 使用單一 owner。
- 每條 Module lane 必須同時滿足 product writer quiescent、required tests admitted、module verification PASS、無 shared-contract gap 與 actual diff mapping。
- 全部 current lanes ready 後由 mechanical Join Barrier 依固定順序整合，重新消費 System Map impact closure，再凍結 Subsystem candidate。
- Module PASS 不能拼成 Subsystem PASS；integrated candidate 必須重跑 required Module tests，再執行 Subsystem scenarios、stress 與 affected regressions。
- Subsystem failure 提升整體分析／重驗範圍，但不自動授予所有 Modules 或 scope 外 nodes 寫入權。

`MVE-EXEC-001` Layer/Risk Execution Profiles and Stress Scheduling 已確認：

- Diagnostic feedback、Module provisional、Subsystem completion、Domain／Global acceptance 與 external high-risk lanes 分離。
- TAQG 固定 required suites、stress applicability、thresholds 與 oracle；MVE 只調整 ordering、sharding、parallelism、runner placement、cache 與 resource。
- Fail-fast 可以節省錯誤 candidate 成本，但未執行項目必須標 `not_run`，final candidate 仍跑完所有 required acceptance。
- Module provisional PASS 不能跨 candidate cache 成 integrated PASS。
- Shared-state tests 只有真正隔離時能平行，否則機械序列化。
- Budget 耗盡只能輸出 unverified requirements／additional budget，不得降低品質。
- Actual diff／failure closure 改變時必須重新消費 System Map 並建立新 execution-plan generation。

`MVE-RUN-001` Runner Environment and Cross-Platform Reproducibility 已確認：

- Environment identity 綁定 OS／architecture／runtime／dependencies／pytest plugins／filesystem／locale／DB／network／isolation／resource semantics。
- Configured／available／self-checked／ready／unhealthy／incompatible 分開；只有 ready backend 可正式執行。
- Self-check 使用框架 own probes，Runner 故障依 bounded routes 自動重建／切換，不修改產品或 tests。
- Backend fallback 只限 approved equivalence class；performance、DB locking、filesystem 等 semantics 不預設可攜。
- Required／optional／N/A platforms 由固定 profile 決定，不能在單一目前平台 PASS 就宣稱跨平台。
- 一般 Runner 只使用 disposable／isolated resources；真實 network、production DB、credentials 與 deployment 維持獨立高風險邊界。

`MVE-OBS-001` Output Hygiene, Bounded Result Buffer and Failure Clustering 已確認：

- 正常 pytest／stress execution 必須 source-side quiet／structured／aggregated；Result Buffer 是異常安全網，不是容許無界輸出的正常設計。
- Unbounded test／fixture output 路由 TAQG repair，runner reporter log storm 路由 RC-MVE-004，產品 log storm 保留 product classification。
- Tier 0 必要結果、Tier 1 有界診斷與 Tier 2 raw temporary artifacts 分層；Tier 0 不可因 budget 淘汰。
- Clustering 只去除重複診斷，不得合併 mixed、outside-scope、不同 candidate／environment 或未驗證項目。
- Raw artifacts 在目前 repair／completion 消費後刪除；長期 Evidence 仍是可重播 test assets。
- Secret 先遮罩／quarantine，output 截斷與 buffer failure 不得改變 observed result。

`MVE-PROTO-001` Verification Invocation and Runner Result Protocol 已確認：

- MVE 不依賴自由格式 stdout／stderr 判定正式結果；每次 invocation 透過
  runner-neutral structured result 表達 terminal state 與 completeness。
- Invocation 固定 subject、plan、suite／test references、shard、runner／
  environment、budget 與 attempt identity，不能改變 fixed acceptance。
- Result 分開表達 PASS、FAIL、timeout、tool error、cancelled 與 incomplete；
  exact schema、field names、serialization、transport 與 adapter API 尚未固定。
- Duplicate／late／out-of-order／partial／identity-mismatched result 必須
  idempotent 或 fail closed，不能污染 current verification。
- Runner 只回報觀測事實；MVE 依 `MVE-RESULT-001` 做 failure classification
  與 impact routing。
- Protocol artifacts 是短期 runtime data；長期 Evidence 仍是可重播 test assets。

`MVE-VERDICT-001` Subject Result Aggregation and Terminal Verdict 已確認：

- Required Module／Subsystem／Domain scenarios、affected regressions、stress、
  platform matrix 與 conditional suites 共同形成 Subject required result universe。
- Verdict 分開表達 `acceptance_outcome` 與 `verification_completeness`，不能用
  單一狀態隱藏 `failed＋blocked` 等 mixed outcomes。
- 只有 current Subject 的所有 required results 完整通過，才能發布
  `mechanical_verification_passed`。
- Required not-run／unexpected skip／missing／blocked／invalidated result 都
  不能因通過比例或歷史 PASS 被忽略。
- MVE verdict 只屬於單一 immutable Verification Subject，不發布 Work Package
  completed、subsystem integrated、domain accepted 或 release candidate。
- Verdict 是短期 transition data；長期 Evidence 仍是可重播 test assets。

`DDH-COMP-001` Layered Completion Contract 已確認：

- Work Package completed、subsystem integrated、domain accepted、release
  candidate 與 deployment approved 是互不等同的獨立判定。
- Higher-layer completion 必須使用同一 current integrated candidate、自己的
  layer specification、mechanical verification、scope／diff 與 exception closure；
  不能把 child PASS 相加。
- Higher-layer failure 不自動撤銷全部 lower completion；只 invalidates 被證明
  原完成條件有缺口的 affected completion。
- System Map 用於 nodes、dependencies、impact 與 regression discovery，不提供
  completion authority；詳細 maintenance status 保持可調整。
- Map maintenance pending 原則上不取代功能驗收，除非 Map 更新是規格交付內容，
  或缺少 Map 與 live fallback 後已無法安全封閉 impact。
- Release candidate 不授權 deployment、production DB、credential、network、
  migration 或其他 external side effect。

`DDH-OBS-001` Operational Telemetry and Health Model 已確認：

- Metrics、structured events、traces 與 bounded logs 分工，且不成為 SSOT、
  completion evidence、Attempt Ledger 或 long-term memory。
- Health 依 capability 與 current task requirement 局部判定；Healthy、Degraded、
  Unavailable、Unknown 語義分離。
- Telemetry 只觸發 confirmed Recovery Contract，不能取代 canonical state 或
  自行發明 recovery。
- Main Agent 只取得影響目前工作的 bounded health summary；routine collection
  與 recovery routing 不使用 Agent／LLM。
- Retention、cardinality、labels、rollup 與 secret handling 有界；實際 SLO、
  數值與天數由 versioned Observability Profile 決定。
- OLE 只消費聚合 orchestration signals，Telemetry 原文不得直接成為 memory。

`DDH-OPS-001` Managed Assets and External High-Risk Operations 已確認：

- Canonical、derived、local environment 與 external managed state 分類，repository
  sync 可以自主，external state 必須 dedicated plan／approval／Trusted Executor。
- Asset sync 要 deterministic preview、atomic／recoverable apply、user diff
  preservation 與 cross-platform validation。
- System Map branch mode 查詢綁定 exact branch／resolved commit／worktree／
  candidate view；branch name alone 不足。
- 每個 branch view 維持 actual-only，不混合 cross-branch facts，也不假設 stable
  cross-version Entity identity。
- Query-only branch switch 不等於 Git checkout、workspace mutation 或 scope
  authority；dirty／uncommitted candidate 仍需 live diff confirmation。
- External approval 綁定 candidate、resolved source、target、operation 與 expiry；
  任一 drift 使舊 approval失效。
- Release candidate／preview／exit 0 不等於 production deployed；database、
  credential、network 與 irreversible operation 保持獨立高風險流程。

`OLE-MEM-001` Long-term Orchestration Memory Model 已確認：

- Memory Type 限於 task partitioning、parallelization、Agent profile、Context、
  integration／handoff 與 approved recovery ordering。
- 每條 Memory 保存可機械比對 applicability、support／counterevidence、
  confidence reason、profile compatibility、version、invalidation 與 conflict。
- Main Agent 是 consumer，不是 maintainer；Analyzer proposes、Critic validates、
  Registry publishes、Reconciler 維護 lifecycle。
- T1 planning、T2 Context materialization、T3 evidence-driven repartition／
  expansion、T4 integration／handoff、T5 approved recovery ordering 才查詢。
- Resolver 只提供 bounded Guidance Cards；Orchestration Plan 必須引用 query
  result 與 applied／declined disposition。
- Child Agent只取得主 Agent決定後的 Context Envelope，不讀 Memory Store。
- Memory unavailable／conflict 時回到 single-main-Agent bounded-context baseline，
  不阻擋施工或建立人工 Checkpoint。

`OLE-EVOL-001` Memory Evolution, Critic Trial and Rollback 已確認：

- Analyzer 只提出 Candidate；mechanical policy validator、independent Critic、
  Trial Controller 與 Registry responsibility 分離。
- Candidate 依序經 policy validation、offline replay、shadow、bounded canary，
  全部達標才 promotion immutable active version。
- Candidate 作者不能修改 replay corpus／trial results，Critic 不能修改
  Candidate 使其通過；不能只靠 prompt 宣稱獨立。
- Canary 只限 low-risk recoverable tasks，不含 L3 或 external side effects，
  且不能降低 verification。
- Guardrail violation 立即 suspend；metric regression 依 versioned profile
  rollback 到 previous compatible Memory 或 baseline。
- Rollback 只改 orchestration Memory，不改 product source、tests、candidate、
  specification、scope 或 acceptance。
- Candidate／trial artifacts 決策後刪除，不建立永久 evolution receipt chain。

已確認的跨 Subsystem 原則：

- pytest／壓力測試必須能在沒有 Agent／LLM service 的情況下機械執行與重跑。
- Agent 可以撰寫、維護、觸發或診斷測試，但不能成為 test selection、threshold 或 PASS／FAIL 判定的 runtime 依賴。
- 凍結的 Verification Manifest 保存 suites、selectors、conditional triggers、thresholds、environment profile 與 seeds。
- 正常驗證的 Agent token cost 應為 0；完整輸出保存為 artifact，只在失敗或決策時向 Agent提供有界摘要。
- 測試資產應跨 Work Package 重用，stale／superseded 判定由版本關係與機械規則執行。
- 一般節點完成後，不永久保存歷史 PASS、Invocation Record、執行 log、snapshot report 或 Attempt Ledger 作為 Evidence Retention。
- Evidence Retention 的核心是可再次執行的 pytest 及其必要 fixture、configuration 與 profile；日後節點被修改時，重新執行仍 active、未 stale 的既有測試。
- Attempt Ledger 是編排自進化的短期原料；與長期記憶比較、聚合並完成接受／拒絕／無新增記憶處理後，刪除原始 Ledger 與一般 logs。
- `DOM-OLE-001` 已固定 terminal completion、Ledger seal、非同步 ingestion、
  idempotent replay 與 completion 不等待 Analyzer。
- `OW-F18.3` 已固定 terminal prefilter、critical／batch／idle triggers 與
  consumed 後刪除。
- `OLE-PROFILE-001` 已固定 pending priority、profile resource categories、
  backlog pressure、Analyzer circuit breaker 與
  `analysis_expired_without_memory_change`；具體數值留給 versioned profile。

### 5.4 壓力、效能與可靠性驗證

- 測試環境、資料規模、負載模型、暖機、重複次數與容許波動。
- baseline、回歸門檻與硬體／環境差異。
- flaky test、順序相依與不穩定環境的判定。
- property-based、mutation、併發、耐久與故障注入的選用規則。
- 哪些測試可標示 `not_applicable`，以及必要理由。

### 5.5 真實執行與測試資料

- mock、simulation、isolated integration 與真實執行的證據等級。
- fixture 是否代表實際業務資料與邊界。
- 資料隱私、機密資訊與可重現測試資料的處理。
- 依風險決定是否要求真實資料格式、真實資料庫或接近 production 的環境。

### 5.6 驗證呼叫契約

每次驗證至少需要可辨識：

- 執行命令與參數。
- cwd、環境與必要依賴。
- timeout、預期 exit code 與輸出上限。
- 實際執行身分與隔離方式。
- 測試失敗、timeout、process crash、環境漂移及權限問題的分類。

### 5.7 工作區基線與差異證據

- 保留使用者原有 dirty changes。
- 在 Work Package 開始時建立 canonical baseline。
- 區分既有差異與本次新增差異。
- rename、untracked、generated asset 與設定變更的處理。
- 只阻擋本次新增的越界修改，不把既有差異誤判為 Agent 違規。
- 完成報告綁定精確 source candidate 與規格版本。

### 5.8 Attempt Ledger 與失敗復原

- invocation id、嘗試次數、failure fingerprint 與失敗分類。
- 已採取的修正、得到的新證據與剩餘預算。
- 無新進展循環的判定。
- 失敗現場、log 與 diff 的保留。
- 可安全重試、需改規格、需改 scope 與需人類介入的分類。

### 5.9 System Map 作為 actual architecture index

- live source、schema、configuration 與 API 的掃描及人工補充方式。
- actual-only policy；planned architecture 必須存放在規格或 proposal。
- Entity、Relation、Coverage、Omission 與 Query Index 的保留方式。
- `unknown`、`partial`、`manual`、confidence 與 source evidence 的語意。
- Map drift／sync report。
- 任務規劃後對 live source 做輕量再確認。
- 架構變動後的同步時點、責任與失敗處理。
- Map snapshot 與 discovery metadata 均不構成施工授權的機械邊界。

### 5.10 Risk 與 Coding Harness

- L0／L1／L2／L3 的正式分類條件。
- 將「變更風險」與「驗證強度」設計成同一軸或兩個獨立維度。
- 自動分類、人工覆寫與高估／低估風險的處理。
- 各級最低規格、驗證、隔離、review 與外部副作用政策。
- Clean Code 規則的 lint、AST validator、review guidance 分工。
- 語言 profile、generated code、legacy code 與測試資料宣告例外。
- 規則造成無價值重構時的豁免或降級機制。

### 5.11 執行者與子代理

- Trusted executor facade：執行者只接收 package id／version，由核心解析核准 scope、命令與證據需求。
- Context Envelope 的確定性建構與內容上限。
- Agent capability registry／doctor，區分「已設定」、「已安裝」與「機械上確實生效」。
- 子代理的風險／收益評分。
- 平行 code／test 工作的獨立性與整合規則。
- 條件式 lease 的原子取得、續租、釋放、owner death 與孤兒回收。

### 5.12 資產、設定與生命週期邊界

- managed asset／configuration 的所有權、同步、dry run、backup 與 parity。
- Work Package 完成、Subsystem 整合、Domain 驗收、release candidate 與 production deployment 的獨立判定。
- 發佈、部署、資料庫、憑證、網路與不可逆操作的專用高風險流程。
- dogfood、adoption 與真實使用證據。

### 5.13 編排記憶與自我演進

- 長期記憶的資料模型與去識別／摘要規則。
- 證據、信心、版本、適用條件、失效條件及衝突解決。
- Critic replay corpus、試用範圍與回滾門檻。
- 防止演進 Agent 修改規格、權限、驗收或風險政策的機械隔離。

---

## 6. 與現有 ADHD 時期文件的直接衝突

Decision 0002 已正式確認：System Map 是長期維護、actual-only 的 actual
architecture index，不是 SSOT、施工授權或驗收權威。下列核心文件已加上
權威修正；其餘歷史提案中的舊語句仍須在該提案重新啟用時逐項校正：

- `README.md`
- `docs/SSOT.md`
- `docs/decisions/0001-adhd-project-identity.md`
- `docs/architecture/system_map_bundle_specification_v1.md`
- `docs/proposals/work_package_driven_execution_module_proposal.md`

其中既有 Work Package proposal 把「System Map architecture conformance」放在功能驗證之前，並把它標為人類已確認的 SSOT；該段不得再作為目前方向的依據。

可能保留的 System Map 能力包括 snapshot、Entity、Relation、Coverage、Omission、查詢索引與視覺化；需要移除的是它的授權與規範權威語意。

現有 `docs/semantic-specifications/README.md` 也尚未表達：

- Global／Domain／Subsystem／Module 的規格差異。
- 每次任務如何取得或組裝其 SSOT。
- 規格到 pytest 的追溯。
- 邊界、錯誤與壓力測試。
- 同層級失敗後整體重新分析的語意。

---

## 7. 建議的後續討論順序

### 階段 0：先固定詞彙與權威邊界

下列權威模型已確認：

1. System Map 是 actual architecture index，不是 SSOT 或施工授權。
2. 本次任務規格書是本次完成判定的 SSOT。
3. live project assets 是目前狀態的證據。
4. 長期業務規範與 Architecture Decision 由任務規格固定版本引用。
5. Active System Map 維持 actual-only；planned／proposed／declared-only
   architecture 不得進入 DDH 消費的 Active view。
6. Currentness／stale 採局部 evidence-binding 語義；詳細模型等 System Map
   規格落地後再定，不建立全專案 freshness gate。

仍需設計引用格式、版本固定、漂移檢查與修訂程序。

### 階段 1：System Map

1. Global／Project、Domain、Subsystem、Module 的階層語意。
2. Entity、Relation、evidence、unknown 與 partial。
3. 更新、漂移、同步與 freshness。
4. 查詢、圖譜、Context Envelope 與 scope 規劃。
5. Map 與 live source 衝突時的處理。

### 階段 2：分層任務規格

1. 四個層級各自的最低欄位。
2. 長期規範與任務規格的引用／覆寫規則。
3. 正向、反向、邊界、錯誤與壓力情境。
4. 凍結、修訂、diff 與人類確認強度。

### 階段 3：Scope 與執行封套

1. Work Package 是否保留，以及與規格書是否合併。
2. 可寫範圍、禁止事項、預算、工具與外部副作用。
3. Scope expansion 與結構化例外報告。
4. L0 已確認以使用者寫明的 Agent 目標為 SSOT 來源；仍需定義升級分類器。

### 階段 4：驗證模型

1. 所有任務的最低驗證基線。
2. 依風險與規格選擇的加強驗證。
3. 分層測試與影響閉包。
4. anti-gaming、test validity、真實執行與證據。
5. 壓力／效能測試的 applicability 與契約。

### 階段 5：Coding Harness

逐條決定 Clean Code 規則屬於：

- 機械硬門檻。
- 可配置 profile。
- 自動 review。
- Agent 指引。

### 階段 6：Agent 編排

1. 單一主 Agent 的預設流程。
2. 子代理風險分流。
3. 平行 code／test 的獨立性。
4. Context Envelope 與條件式 lease。

### 階段 7：失敗、證據與復原

1. workspace baseline／delta。
2. Attempt Ledger 與 failure fingerprint。
3. 驗證 invocation contract。
4. diff、現場與證據保留。
5. 無進展、預算耗盡與例外報告。

### 階段 8：完成之後的生命週期

分開定義：

- Work Package implementation verified。
- subsystem integrated。
- domain accepted。
- release candidate。
- production deployed。

### 階段 9：編排長期記憶與受控演進

先固定主要執行模型後，再設計記憶與 prompt／Context Envelope 模板演進，避免它反過來影響規格與權限。

### 階段 10：舊 ADAD 遷移矩陣與實作計畫

等上述語意確認後，才逐項判定舊能力為：

- 保留。
- 規格包化。
- 替換。
- 淘汰。

---

## 8. 下一個最適合先確認的問題

PWC partition／fork-join、TAQG admission／validity／discovery／portfolio、MVE handoff／result classification／impact assessment／execution scheduling／runner environment／output handling／Runner Protocol／Subject Verdict、Layered Completion、Ledger／Telemetry、Orchestration Memory／Evolution、Task Specification／Work Package、Risk Gate、Coding Harness、Operational Lifecycle 與 Domain invalidation已確認。下一步應完成收斂：

> 以現有 legacy ADAD source／config／tests／docs 做 capability migration matrix，
> 固定 DDH MVP end-to-end flow、phases、risks、acceptance 與 human decisions。

這是目前討論主線最後一個核心包；完成後才能形成可核准的 implementation
proposal，仍不會直接授權實作。

---

## 9. 參考理念：old-coder

目前可吸收的理念是：

- 先以 SPEC 固定可觀察行為，再用 executable examples 驗證。
- 保留 RED → GREEN → REFACTOR 的證據意義。
- 依風險選擇 verification gauntlet，而非所有工作執行相同強度。
- 不弱化測試、不宣稱未執行的檢查已通過。
- 明確承認驗證只能證明實作符合已表達的規格，不能證明規格沒有遺漏。

DDH 不應直接照搬一套固定重型流程；需要把這些理念轉成分層規格與風險校準的驗證能力。
