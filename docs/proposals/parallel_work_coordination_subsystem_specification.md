# Work Coordinator Role Specification

**Canonical role name：** `Work Coordinator`  
**歷史名稱／ID：** Parallel Work Coordination／PWC  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 本文件保存已逐項確認的功能與驗收方向；實作技術與未確認門檻仍需後續決策  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

---

## 1. 責任

判斷是否值得平行施工，建立寫入分區，協調共享資源、跨區請求與安全移交，並由主 Agent集中組裝 integration candidate。

## 2. 不負責

- 不自行改變使用者目標、任務規格、架構決策、公開契約或人類升級條件。
- 不把 System Map、discovery metadata、Agent claim 或 prompt 約束當成授權或機械證據。
- 不因本 Subsystem 的局部 PASS 宣告 DDH Domain、release candidate 或 production 完成。

## 3. 依賴與協作

- 任務規格與 Work Package 提供 scope、禁止事項與升級條件。
- Candidate Integrity and Mutation 提供寫入邊界、candidate identity 與 patch admission。
- Context Broker 提供子代理最小 Context。
- Mechanical Verification 對整合 candidate 執行最終驗證。

## 4. 已確認功能

### OW-F01：判斷是否需要平行寫入分區

**確認狀態：已確認（2026-08-02）**

系統必須只在以下條件同時成立時啟用：

1. 存在兩個以上可能寫入的 Agent。
2. 工作可依固定規格獨立進行。
3. 平行收益高於上下文與整合成本。
4. 可以定義不互相覆蓋的主要寫入區，或能明確識別共享資源。

單一寫入者不建立 ownership 流程。

判定結果固定為：

| 結果 | 後續行為 |
|---|---|
| `parallel_allowed` | 建立施工分區並平行派工 |
| `parallel_not_worthwhile` | 可以切分，但收益不足，改由單一 Agent施工 |
| `parallel_unsafe` | 寫入或契約無法安全分離，改為序列施工 |
| `needs_human_decision` | 平行化前必須改變規格、架構、scope 或風險政策 |

不確定是否重疊時，不得判定為 `parallel_allowed`。System Map 只能協助辨識候選範圍，仍須解析實際路徑及共享資源。判斷必須留下簡短理由，但不使用固定分數強迫派工。

### OW-F02：建立寫入分區

**確認狀態：已確認（2026-08-02）**

主 Agent 必須能為每個 writer 指定：

- 分區 id 與 generation。
- Agent 身分。
- 子目標。
- 固定的任務規格版本及相關驗收條目。
- 起始 candidate／baseline identity。
- 允許寫入的邏輯資源與實際路徑。
- 明確禁止寫入的資源。
- 分區狀態。
- 子成果的驗收要求。
- 必須升級的條件。
- Context Envelope 與 context budget。

預算、timeout 與工具限制預設繼承 Work Package；只有需要更窄限制時才在分區覆寫。

本 Subsystem 只在 partition 中保存 `context_requirement_reference` 與 `context_budget_reference`。System Map discovery、Context Envelope 組裝、content request、計量、stale Context 與機械限制的語意，由 `context_broker_subsystem_specification.md` 負責。

分區狀態保持精簡：

```text
planned → active → frozen → submitted
```

例外狀態只有 `revoked` 與 `recovery_required`。

### OW-F05：管理共享資源

**確認狀態：已確認（2026-08-02）**

共享資源包括公開介面、schema、跨 Subsystem contract、root configuration、lockfile、共用 fixture、manifest，以及 generator 與其 outputs 等無法安全獨立修改的資源。

主 Agent必須先區分：

| 類型 | 處理 |
|---|---|
| 本次規格未允許變更的共享契約 | 凍結，任何子代理都不得修改 |
| 本次規格已允許變更的共享資源 | 由主 Agent集中控制，序列交給一個 writer |
| 需要新增但尚未獲准的契約／schema 變更 | 停止相關分歧並提出人類例外報告 |

必要行為：

- 任一共享資源同一時間最多只能有一個 writer。
- 主 Agent可以自己處理，也可以在凍結其他相關 writer、保存 diff 並確認 scope 後，指定一個子代理處理。
- generator source 與無法獨立驗證的 generated outputs 必須視為同一 logical resource group。
- 共享資源變更後，依賴該資源的 active partitions 必須被標記為需要刷新，不能繼續依舊契約施工。
- 刷新至少包含新的 candidate identity、必要 Context Envelope 增量，以及受影響驗收重新判定。
- 不相依的分區不得因存在某個共享資源而被全域鎖住。

### OW-F06：處理跨區變更請求

**確認狀態：已確認（2026-08-02）**

跨區變更請求只處理「需要寫入其他資源」。只要求取得更多唯讀 Context 的情況，使用 Context Broker 的 OW-F16 content request，不能混用。

Agent 發現需要修改其他分區時，必須提出最小但足以判斷的內容：

- 目標資源。
- 預計修改類型。
- 需要修改的原因。
- 對應的規格／驗收條目。
- 已取得的根因證據。
- 目前 owner 或可能重疊的分區。
- 不修改時對子目標的影響。
- 對規格與測試的影響。
- 對 Context、預算與整合的影響。
- 建議由原 owner 修改、重新分區、改為序列或擴大 scope。

主 Agent 必須區分：

- `route_to_current_writer`：仍在核准 scope，由目前 owner 修正。
- `repartition_within_scope`：仍在核准 scope，凍結後重新分區。
- `serialize_shared_change`：共享資源由主 Agent集中序列處理。
- `reject_unnecessary_request`：證據不足或不是完成規格所必需。
- `human_scope_or_spec_decision`：超出 scope，或涉及架構、schema、公開契約、規格與外部副作用。

提出請求本身不會取得寫入權。主 Agent完成判定並建立新的 active generation 之前，原 protected resource 仍不可修改。

不受請求影響、可獨立完成的工作可以繼續。若跨區請求持續反覆發生，主 Agent必須重新評估原分區是否錯誤、平行收益是否已消失，必要時改為序列施工。

### OW-F07：安全移交

**確認狀態：已確認（2026-08-02）**

重新分配寫入區之前必須：

1. 對原 partition 建立 freeze fence，使舊 generation 不能開始新的寫入。
2. 等待或中止已進行中的工具操作，取得明確完成、失敗或未知結果。
3. 取得並保存原 writer 的候選 diff、base candidate、執行狀態與尚未完成事項。
4. 確認使用者原有差異與 Agent delta 仍可區分。
5. 確認沒有可繼續影響受保護 candidate 的 active write。
6. 撤回原分區。
7. 以最新 candidate、必要 Context 增量及新的 generation 建立新 writer 分區。

時間到期、heartbeat 消失或 prompt 回報停止，都不得單獨視為安全移交。若執行身分、落盤結果或 active write 狀態不確定，分區必須進入 `recovery_required` 並 fail closed。

移交結果至少能表達：

| 結果 | 意義 |
|---|---|
| `handoff_completed` | 原 writer 已安全凍結，新 generation 已建立 |
| `handoff_no_agent_delta` | 原 writer 沒有產生本次變更，可安全重派 |
| `handoff_recovery_required` | 執行或差異狀態不確定，不可直接重派 |
| `handoff_cancelled` | 不再需要接續施工，但仍保留既有候選證據 |

### OW-F12：保留中央整合權

**確認狀態：已確認（2026-08-02）**

主 Agent保留邏輯上的中央整合權。Patch 可以平行進行靜態檢查、freshness 分析或預備驗證，但真正改變 integration candidate 的 admission 必須依 candidate generation 序列化。

只有主 Agent或其受控 integration service 可以：

- 接受、拒絕或要求重做子代理 patch。
- 處理整合衝突。
- 組裝最終 candidate。
- 決定需要重新派工、改為序列施工或提出例外。
- 啟動對整合 candidate 的完整規格驗證。

子代理完成只代表「候選子成果已提交」，不代表 Work Package 完成。

Patch Admission 至少依序確認：

1. Work Package 與規格版本仍有效。
2. partition、writer、generation 與 base candidate 可辨識。
3. touched resources 位於核准 scope 與寫入分區。
4. 沒有 protected-resource、shared-resource 或 logical-resource 衝突。
5. freshness 與 dependency contract 仍可接受。
6. patch 可完整套用，且沒有留下未宣告的工作區 delta。
7. 產生新的 candidate identity。
8. 依影響閉包執行必要的 provisional／integration verification。

Admission 結果至少能表達：

| 結果 | 意義 |
|---|---|
| `accepted_into_candidate` | patch 已進入新的 candidate generation |
| `accepted_revalidation_required` | patch 可套用，但整合後必須重驗 |
| `rejected_scope_or_partition` | 越出核准 scope 或寫入分區 |
| `rejected_stale_result` | generation、specification、base 或 dependency 已過期 |
| `integration_conflict_rework_required` | patch 間有實體或語意衝突，需要重新施工 |
| `human_change_decision_required` | 整合需要改架構、契約、規格、scope 或風險政策 |

主 Agent若為整合而修改 glue code、shared fixture 或其他檔案，也必須成為可辨識 writer，產生自己的 delta 並接受相同 scope、snapshot 與驗證規則。不得在整合時靜默改寫子代理成果或驗收期待。

若相同 patch 集合因套用順序不同產生不同最終內容或語意，必須判定為整合不穩定並重新處理，不能任選一個看似通過的順序。

### OW-F13：選擇施工隔離模式

**確認狀態：已確認（2026-08-02）**

當 OW-F01 判定工作值得平行後，主 Agent必須依實際風險選擇施工模式，而不是所有任務一律完整隔離或一律共享工作區。

判斷輸入至少包含：

- 寫入資源是否實際重疊。
- formatter、generator、package manager 等工具是否可能間接越區。
- 是否具備可證明有效的共享工作區 Write Guard。
- 是否需要高度獨立的 implementation／acceptance 候選。
- pre-existing dirty changes 能否安全納入 baseline。
- 隔離環境的建置、依賴安裝、Context 與整合成本。
- 是否存在 filesystem 隔離無法涵蓋的資料庫、網路或其他外部副作用。

模式至少能表達：

| 模式 | 適用情況 |
|---|---|
| `shared_guarded_workspace` | 寫入區不重疊，且所有 mutation 都有機械 Write Guard／delta boundary |
| `isolated_candidates_central_integration` | 需要強隔離、工具可能間接越區，或 acceptance independence 優先 |
| `serialized_shared_resource` | 共享契約或資源無法安全平行，不因 worktree 隔離就假裝語意獨立 |
| `external_high_risk_flow_required` | 涉及 DB、部署、憑證、網路或其他外部副作用，需獨立流程 |

必要原則：

- 隔離 worktree／workspace 只能隔離 filesystem candidate，不能自行解決共享契約、資料庫或外部服務衝突。
- 若共享工作區沒有機械寫入邊界，不能選擇 `shared_guarded_workspace`。
- 若隔離建置成本高於平行收益，可以改為序列施工，不能因此降低安全不變量。
- pre-existing dirty changes 不得因模式選擇而被 reset、stash、覆寫或遺漏；無法安全物化 baseline 時應停止或改用可保留現況的模式。
- 不同模式產生的候選成果仍須經相同 Patch Admission、integration snapshot 與最終規格驗證。

## 5. 已確認業務場景

### OW-S21：未獲准的公開契約變更

**對應功能：** OW-F05

**Given**

- 本次規格沒有允許改變 `PathResolutionResult` 公開契約。
- Test Agent 發現目前契約無法表達它假設的錯誤結果。

**When**

- Test Agent 請求修改公開契約。

**Then**

- 契約保持凍結。
- Test Agent 不得直接修改。
- 主 Agent先判斷固定規格是否已有明確語意。
- 若確實需要改變公開介面，提出人類例外報告。

### OW-S22：核准 scope 內修改共用 fixture

**對應功能：** OW-F05

**Given**

- Implementation Agent 與 Test Agent 都依賴 `tests/fixtures/workspace_tree.py`。
- 本次規格與 scope 允許修正該 fixture。

**When**

- Test Agent 提出修改請求。

**Then**

- 主 Agent凍結相關 writer 並保存各自 diff。
- fixture 在任一時刻只交給一個 writer。
- 修改完成後建立新的 candidate identity。
- 依賴它的分區取得最小 Context Envelope 增量並重新驗證。

### OW-S23：Generator 與 generated outputs

**對應功能：** OW-F05

**Given**

- Agent A 需要修改 API generator。
- Agent B 的分區包含由該 generator 產生的 client file。

**When**

- 兩項修改可能同時發生。

**Then**

- generator 與相關 outputs 被視為同一 logical resource group。
- 不得分配給兩個同時 active 的 writer。
- 必須由單一 writer 產生一致結果，再由主 Agent刷新依賴分區。

### OW-S24：兩個 Agent 都會修改 lockfile

**對應功能：** OW-F05

**Given**

- 兩個 Module 子工作分別新增依賴。
- 兩者都會間接修改同一 lockfile。

**When**

- 主 Agent規劃平行施工。

**Then**

- Module source 可以在不重疊時平行。
- lockfile 更新必須集中或序列執行。
- 不得接受兩份各自基於舊 lockfile 的最終結果。

### OW-S25：共享契約更新使 active partition 過期

**對應功能：** OW-F05

**Given**

- Implementation Agent 與 Test Agent 都從 `PathResolutionResult v1` 開始施工。
- 經核准後，主 Agent將契約更新為 `v2`。

**When**

- 兩個 Agent 尚未提交最終成果。

**Then**

- 依賴 `v1` 的 partitions 被標記為需要刷新。
- 舊 generation 的成果不得直接整合。
- 主 Agent提供 `v1 → v2` 的最小契約差異。
- Agent 更新候選成果並重跑受影響驗收。

### OW-S26：不相依分區不被共享資源全域阻擋

**對應功能：** OW-F05

**Given**

- Workspace 分區正在序列修改自己的 shared fixture。
- Reporting 分區不讀取或修改該 fixture。

**When**

- Reporting Agent 繼續寫入自己的 active partition。

**Then**

- Reporting 寫入應保持允許。
- 系統不得因任何共享資源正在修改，就建立全域寫入鎖。

### OW-S27：Test Agent 發現產品實作缺陷

**對應功能：** OW-F06

**Given**

- Test Agent 只擁有 acceptance test 分區。
- 它取得證據顯示 `src/workspace/path_normalizer.py` 沒有正確 rollback。
- 該產品檔案屬於 Implementation Agent，且仍在核准 scope。

**When**

- Test Agent 提出跨區變更請求。

**Then**

- 結果為 `route_to_current_writer`。
- Test Agent 不取得產品程式寫入權。
- 主 Agent把失敗場景與最小證據交給 Implementation Agent。
- Test Agent 可以繼續不受影響的測試工作。

### OW-S28：Scope 內需要重新分配測試 fixture

**對應功能：** OW-F06

**Given**

- Implementation Agent 發現自己的 unit test 需要修改一個目前屬於 Test Agent 的 fixture。
- 該 fixture 不是公開契約，且修改仍在核准 scope。

**When**

- 它提出包含根因與影響的跨區請求。

**Then**

- 主 Agent可以選擇由 Test Agent 修正，或凍結原分區後執行 `repartition_within_scope`。
- 在新 generation active 前，Implementation Agent 仍不得修改 fixture。
- 移交後必須重驗受影響測試。

### OW-S29：請求修改 scope 外相鄰 Module

**對應功能：** OW-F06

**Given**

- Workspace 任務的核准 scope 不包含 Plugin Registry Module。
- Agent 認為修改 Plugin Registry 可以讓本次實作更容易。

**When**

- Agent 提出跨區請求。

**Then**

- 主 Agent不能自行擴大 Work Package。
- 若不是完成固定規格的必要條件，結果為 `reject_unnecessary_request`。
- 若確實必要，結果為 `human_scope_or_spec_decision`，並附上證據與替代方案。

### OW-S30：兩個 Agent 互相要求對方資源

**對應功能：** OW-F06

**Given**

- Agent A 要求 Agent B 的 fixture。
- Agent B 同時要求 Agent A 的 implementation helper。

**When**

- 兩個請求可能形成循環等待。

**Then**

- 系統不得讓兩者各自等待對方釋放而永久阻塞。
- 主 Agent凍結相關變更、保存 diff，並選擇重新切分或序列施工。
- 任一資源同一時間仍只能有一個 active writer。

### OW-S31：提出請求後立即越區寫入

**對應功能：** OW-F06

**Given**

- Agent 已提交跨區變更請求，但主 Agent尚未作出判定。

**When**

- Agent 嘗試修改請求中的 protected resource。

**Then**

- 寫入仍被 `blocked_outside_partition` 阻擋。
- 請求狀態不得被視為臨時寫入 grant。

### OW-S32：跨區請求反覆發生

**對應功能：** OW-F06

**Given**

- 同一組 partitions 持續提出彼此資源的變更請求。

**When**

- 協調與重新載入 Context 的成本已抵銷平行收益。

**Then**

- 主 Agent重新執行 OW-F01。
- 結果可改為 `parallel_not_worthwhile` 或 `parallel_unsafe`。
- 保存已完成的有效 diff，後續改為序列整合，不為維持平行而繼續增加治理成本。

### OW-S33：正常 writer 移交

**對應功能：** OW-F07

**Given**

- Test Agent A 持有 generation 1，並已完成部分 acceptance tests。
- 主 Agent決定由 Test Agent B 接續。

**When**

- 主 Agent凍結 generation 1、等待進行中操作結束並保存 A 的候選 diff。

**Then**

- generation 1 不再能開始新寫入。
- B 從包含已接受候選變更的最新 candidate 開始。
- B 取得 generation 2 與必要的未完成事項摘要。
- 結果為 `handoff_completed`。

### OW-S34：Writer 失聯且仍有操作狀態未知

**對應功能：** OW-F07

**Given**

- Agent A 失聯。
- 最後一個 formatter／generator 操作沒有明確完成結果。

**When**

- 主 Agent嘗試把分區交給 Agent B。

**Then**

- 分區進入 `recovery_required`。
- 不得只依 timeout 自動建立新 writer。
- 必須先檢查 process、workspace delta 與可能的部分落盤。
- 狀態明確前結果為 `handoff_recovery_required`。

### OW-S35：原 writer 沒有產生 Agent delta

**對應功能：** OW-F07

**Given**

- Agent A 已取得分區，但尚未寫入任何資源。

**When**

- 主 Agent凍結並檢查相對 baseline 的 delta。

**Then**

- 使用者既有 dirty changes 仍被保留且不歸屬於 A。
- 結果為 `handoff_no_agent_delta`。
- 可以從同一有效 candidate 建立新的 generation。

### OW-S36：多檔案操作進行中觸發 freeze

**對應功能：** OW-F07

**Given**

- Agent 正在執行可能修改多個檔案的 generator。

**When**

- 主 Agent要求 freeze。

**Then**

- freeze fence 先阻擋新的操作。
- 已開始的操作必須得到成功、失敗、已終止或未知的明確分類。
- 未知或部分落盤時不得建立新 writer，必須進入 recovery。
- 不得把半套 generated outputs 當成可直接接續的 candidate。

### OW-S37：移交時存在使用者原有差異

**對應功能：** OW-F07

**Given**

- 任務開始前，使用者已修改分區中的一個檔案。
- Agent A 在同一分區產生額外修改。

**When**

- 分區移交給 Agent B。

**Then**

- baseline 必須區分使用者原有差異與 Agent A delta。
- 兩者都不得因移交而被 reset、stash、覆寫或錯誤歸屬。
- Agent B 的新 generation 必須以保留兩者的明確 candidate 開始，或因無法安全區分而進入 recovery。

### OW-S38：舊 writer 在移交後遲到寫入

**對應功能：** OW-F07

**Given**

- generation 1 已撤回。
- generation 2 已交給新 writer。

**When**

- 舊 writer 使用 generation 1 嘗試寫入或提交 patch。

**Then**

- 寫入結果為 `blocked_stale_generation`。
- 舊 patch 不得覆蓋 generation 2。
- 可保存為診斷候選，但必須重新審查才能利用其中內容。

### OW-S39：取消而不是移交

**對應功能：** OW-F07

**Given**

- 主 Agent重新評估後，確認該子工作不再需要。

**When**

- 它凍結並取消原 partition。

**Then**

- 結果為 `handoff_cancelled`。
- 已存在的有用 diff 與測試證據仍保留。
- 不建立新 writer，也不能把取消誤報為完成。

### OW-S70：正常整合實作與 acceptance patch

**對應功能：** OW-F12

**Given**

- Implementation Agent 與 Test Agent從同一規格及 base candidate 提交不重疊 patch。
- 兩份 patch 均通過 partition、scope 與 freshness 檢查。

**When**

- 主 Agent依序 admission 兩份 patch。

**Then**

- 每次 admission 都建立新的 candidate generation。
- 最終 candidate 同時包含產品實作與 acceptance tests。
- Work Package 只有在最終 candidate 通過規格要求的整合驗證後才能完成。

### OW-S71：Acceptance patch 先於實作完成

**對應功能：** OW-F12

**Given**

- Test Agent 先提交 acceptance patch。
- 對目前 candidate 執行時因功能尚未實作而 RED。

**When**

- patch 本身符合規格、scope 與分區。

**Then**

- RED 可以作為預期的 provisional evidence，不等同 Test Agent 失敗。
- acceptance patch 可以先進入候選 candidate。
- 後續整合 implementation patch 後，必須重新執行相同 acceptance。

### OW-S72：兩份個別有效 patch 產生整合衝突

**對應功能：** OW-F12

**Given**

- 兩份 patch 各自在自己的 candidate 上通過局部驗證。
- 整合後產生 API、狀態或實際路徑衝突。

**When**

- 主 Agent執行 admission 或 integration tests。

**Then**

- 結果為 `integration_conflict_rework_required`。
- 不得用兩份局部 PASS 宣告完成。
- 回到受影響的 Subsystem 層級重新分析與施工。

### OW-S73：主 Agent新增整合 glue code

**對應功能：** OW-F12

**Given**

- 兩個 Module patch 需要在已核准 scope 內新增 glue code 才能完成既定 Subsystem 契約。

**When**

- 主 Agent決定直接完成該整合修改。

**Then**

- 主 Agent登記為該 delta 的 writer。
- glue code 受相同 scope、Coding Harness 與測試要求。
- 產生新 candidate identity 並重跑受影響驗證。
- 若 glue code 實際改變契約，改為 `human_change_decision_required`。

### OW-S74：子代理嘗試宣告 Work Package 完成

**對應功能：** OW-F12

**Given**

- 子代理完成自己的 subgoal 並回報全部局部測試通過。

**When**

- 它將自己的狀態標示為 Work Package completed。

**Then**

- 系統只能接受 `candidate_subresult_submitted`。
- Work Package 狀態不改變。
- 必須等待中央整合與固定 snapshot 驗證。

### OW-S75：Patch 套用順序影響最終結果

**對應功能：** OW-F12

**Given**

- 同一組 patch 以 A→B 與 B→A 套用時產生不同內容或行為。

**When**

- Integration service 偵測到順序相依。

**Then**

- 不得任選通過測試的順序作為完成證據。
- 結果為 `integration_conflict_rework_required`。
- 必須重新定義共享資源、依賴或整合策略。

### OW-S76：被拒絕的 Patch 仍保留診斷價值

**對應功能：** OW-F12

**Given**

- 一份 patch 因 stale generation 或 scope 越界被拒絕。

**When**

- 主 Agent完成 admission。

**Then**

- patch 不得影響 integration candidate。
- 拒絕理由、base、generation 與候選 diff 被保留。
- 後續可以重新派工或從中提取想法，但不能靜默重送。

### OW-S77：整合發現必須擴大 scope

**對應功能：** OW-F12

**Given**

- 既有 patch 只有修改 scope 外 Module 才能完成整合。

**When**

- 主 Agent判斷該變更確實必要。

**Then**

- 結果為 `human_change_decision_required`。
- 目前 candidate 與失敗證據保留。
- 未取得更新任務規格前，不得擴大 scope 繼續整合。

### OW-S78：共享工作區內安全平行

**對應功能：** OW-F13

**Given**

- Implementation Agent 只寫 `src/workspace/**`。
- Test Agent 只寫 `tests/acceptance/workspace/**`。
- 所有 mutation tools 都經過可驗證的 Write Guard。

**When**

- 主 Agent選擇執行模式。

**Then**

- 可以選擇 `shared_guarded_workspace`。
- 任一越區操作仍須整份阻擋。
- 最終仍要停止 writer 並建立固定 integration snapshot。

### OW-S79：Formatter／generator 可能廣泛修改

**對應功能：** OW-F13

**Given**

- 子工作需要執行可能修改 root config、generated outputs 或大量非預期路徑的工具。
- 共享工作區無法在落盤前完整限制 touched resources。

**When**

- 工作仍具有明確平行收益。

**Then**

- 選擇 `isolated_candidates_central_integration`。
- 工具產物只能存在私人 candidate。
- 越區 patch 在中央 admission 時整份拒絕。

### OW-S80：兩個 Agent 都需要修改同一公開契約

**對應功能：** OW-F13

**Given**

- Implementation 與 acceptance 工作都需要改變同一公開 API。

**When**

- 即使可以建立兩個獨立 worktrees。

**Then**

- 不得因 filesystem 隔離就判定可以安全平行修改契約。
- 選擇 `serialized_shared_resource`，或先完成契約決策再重新分區。

### OW-S81：存在 pre-existing dirty changes

**對應功能：** OW-F13

**Given**

- 使用者的未提交變更是本次 candidate 必須保留的實際基線。

**When**

- 主 Agent考慮建立隔離 candidate。

**Then**

- 隔離 candidate 必須明確物化並識別必要 baseline 內容。
- 不得只從 HEAD 建立乾淨 worktree 而遺漏使用者變更。
- 若無法安全物化，停止平行或使用受保護共享模式。

### OW-S82：隔離環境成本高於平行收益

**對應功能：** OW-F13

**Given**

- 每個隔離 candidate 都需要昂貴依賴安裝或大型資料準備。
- 子工作本身很小。

**When**

- 主 Agent比較 Context、環境與整合成本。

**Then**

- 回到 OW-F01，判定 `parallel_not_worthwhile` 並改為單一／序列施工。
- 不得為維持平行而浪費預算。
- 也不得為省成本而在沒有 Write Guard 的共享工作區危險平行。

### OW-S83：Filesystem 隔離無法涵蓋外部副作用

**對應功能：** OW-F13

**Given**

- 子代理操作會存取共享資料庫、部署環境、credential 或外部網路服務。

**When**

- 主 Agent選擇 execution mode。

**Then**

- 結果為 `external_high_risk_flow_required`。
- 一般 ownership 分區與 worktree 不構成外部副作用授權。
- 必須轉入另行確認的高風險隔離、dry run 或人工流程。

### OW-S84：沒有共享 Write Guard，也無法建立隔離 Candidate

**對應功能：** OW-F13

**Given**

- 共享工作區只有 prompt 寫入約束。
- 目前環境無法提供獨立 candidate 與 Patch Admission。

**When**

- 主 Agent評估兩個 writer 的平行施工。

**Then**

- 不得啟動平行寫入。
- 回到 OW-F01，判定 `parallel_unsafe` 並改為序列施工。
- 不得降低「越區修改不能進入 candidate」的不變量。

## 6. 壓力與對抗場景

### OW-P01：同一資源競爭

- 100 個並行分配請求競爭同一共享資源。
- 任一時刻最多只能有一個 active writer。
- 不得出現雙重成功。

### OW-P09：共享資源高競爭與非相關吞吐

- 多個模擬 writer 同時要求同一共享資源時，任一時刻只能有一個 active writer。
- 競爭共享資源期間，不依賴該資源的 partitions 必須仍可正常寫入。
- 不得以全域鎖簡化共享資源協調。
- worker 數量與等待門檻應由目標執行環境的平行規模決定。

### OW-P10：共享契約變更的依賴展開

- 建立大量直接及間接依賴同一契約的 partitions。
- 契約 generation 更新後，所有受影響 partitions 都必須被標記為需要刷新。
- 不相依 partitions 不得被錯誤失效。
- 不得遺漏間接依賴或接受舊 generation 的成果。
- 具體 partition 數量需依 DDH 預期支援的最大專案規模固定。

### OW-P11：循環跨區請求與死鎖回復

- 建立多組互相要求對方資源的 partitions，包含鏈狀與環狀依賴。
- 系統必須偵測無法前進的循環等待。
- 主 Agent必須能凍結、保存候選 diff，並透過重新切分或序列施工恢復進展。
- 不得產生雙 writer、遺失有效 diff 或永久等待。

### OW-P12：大量請求不得造成隱性 scope expansion

- 對同一 Work Package 提交大量 scope 內、scope 外、證據不足及共享資源請求。
- 每個請求都必須得到上述明確結果之一。
- 未經人類確認的 scope 外資源，成功取得寫入權的數量必須為 0。
- 大量請求不得繞過 Context、預算或 generation 檢查。

### OW-P13：快速反覆移交

- 對同一 logical resource 連續執行大量 freeze／handoff／new-generation 循環。
- 任一時刻只能有一個 active generation。
- 每個 generation 的候選 diff 都能追溯，且不得遺失使用者原有差異。
- 所有舊 generation 的遲到寫入都必須被阻擋。
- 循環次數應依預期最壞的自動重派與故障復原規模固定。

### OW-P23：大量非重疊 Patch 的中央 Admission

- 多個 partitions 同時提交互不重疊 patch。
- 靜態檢查與 freshness 分析可以平行。
- 改變 candidate 的 admission 必須依 generation 序列化，不得遺失或重複套用 patch。
- 對相同 patch 集合，最終內容必須可重現。
- 不得以單一全域鎖阻擋仍在進行的獨立分析與測試。

### OW-P24：衝突、重試與亂序提交

- 混合有效、stale、越界、衝突與需要人類決策的 patch，並以亂序及重複方式提交。
- 每份 patch 必須得到唯一且可追溯的 admission 結果。
- rejected patch 不得污染 candidate。
- 同一 patch 不得因重送而重複套用。
- candidate generation 必須保持單調、可重建的因果順序。

### OW-P25：不同隔離模式的候選一致性

- 對同一固定規格與相同合法 patch 集合，分別以 shared guarded 與 isolated candidate 模式執行。
- 經中央 admission 後的 integration candidate 必須在語意與必要內容上等價。
- 任一模式都不得遺漏 dirty baseline、untracked dependency 或 generated asset。
- 模式差異不得改變驗收 expected behavior。

### OW-P26：隔離建立與銷毀故障

- 在大量建立 candidate、依賴準備、Agent crash、整合與回收過程中注入失敗。
- 不得污染主工作區、遺失使用者差異或留下被誤認為 active 的 candidate。
- 隔離資源無法安全回收時應保留診斷資訊並標記，不得以破壞性清理冒險處理。

## 7. pytest 投影規則

- 每個場景以舊 ID 作 traceability key，例如 `@pytest.mark.ddh_scenario("OW-S21")`。
- pytest／fixture／configuration／profile 必須能在沒有 Agent／LLM service 時重跑。
- Test asset admission 與 stale 判定由 TAQG 管理；正式 suite 組裝與執行由 MVE 管理。
- 原 archive 中的示範 test names 只作歷史參考，不是新規格的檔案配置決策。

## 8. 舊 ID 遷移

### 功能

| 舊 ID | 已確認項目 |
|---|---|
| OW-F01 | 判斷是否需要平行寫入分區 |
| OW-F02 | 建立寫入分區 |
| OW-F05 | 管理共享資源 |
| OW-F06 | 處理跨區變更請求 |
| OW-F07 | 安全移交 |
| OW-F12 | 保留中央整合權 |
| OW-F13 | 選擇施工隔離模式 |

### 場景

| 舊 ID | 已確認項目 |
|---|---|
| OW-S21 | 未獲准的公開契約變更 |
| OW-S22 | 核准 scope 內修改共用 fixture |
| OW-S23 | Generator 與 generated outputs |
| OW-S24 | 兩個 Agent 都會修改 lockfile |
| OW-S25 | 共享契約更新使 active partition 過期 |
| OW-S26 | 不相依分區不被共享資源全域阻擋 |
| OW-S27 | Test Agent 發現產品實作缺陷 |
| OW-S28 | Scope 內需要重新分配測試 fixture |
| OW-S29 | 請求修改 scope 外相鄰 Module |
| OW-S30 | 兩個 Agent 互相要求對方資源 |
| OW-S31 | 提出請求後立即越區寫入 |
| OW-S32 | 跨區請求反覆發生 |
| OW-S33 | 正常 writer 移交 |
| OW-S34 | Writer 失聯且仍有操作狀態未知 |
| OW-S35 | 原 writer 沒有產生 Agent delta |
| OW-S36 | 多檔案操作進行中觸發 freeze |
| OW-S37 | 移交時存在使用者原有差異 |
| OW-S38 | 舊 writer 在移交後遲到寫入 |
| OW-S39 | 取消而不是移交 |
| OW-S70 | 正常整合實作與 acceptance patch |
| OW-S71 | Acceptance patch 先於實作完成 |
| OW-S72 | 兩份個別有效 patch 產生整合衝突 |
| OW-S73 | 主 Agent新增整合 glue code |
| OW-S74 | 子代理嘗試宣告 Work Package 完成 |
| OW-S75 | Patch 套用順序影響最終結果 |
| OW-S76 | 被拒絕的 Patch 仍保留診斷價值 |
| OW-S77 | 整合發現必須擴大 scope |
| OW-S78 | 共享工作區內安全平行 |
| OW-S79 | Formatter／generator 可能廣泛修改 |
| OW-S80 | 兩個 Agent 都需要修改同一公開契約 |
| OW-S81 | 存在 pre-existing dirty changes |
| OW-S82 | 隔離環境成本高於平行收益 |
| OW-S83 | Filesystem 隔離無法涵蓋外部副作用 |
| OW-S84 | 沒有共享 Write Guard，也無法建立隔離 Candidate |

### 壓力

| 舊 ID | 已確認項目 |
|---|---|
| OW-P01 | 同一資源競爭 |
| OW-P09 | 共享資源高競爭與非相關吞吐 |
| OW-P10 | 共享契約變更的依賴展開 |
| OW-P11 | 循環跨區請求與死鎖回復 |
| OW-P12 | 大量請求不得造成隱性 scope expansion |
| OW-P13 | 快速反覆移交 |
| OW-P23 | 大量非重疊 Patch 的中央 Admission |
| OW-P24 | 衝突、重試與亂序提交 |
| OW-P25 | 不同隔離模式的候選一致性 |
| OW-P26 | 隔離建立與銷毀故障 |

## 9. 拆分後待補

- Partition grant 的正式資料模型與 state machine。
- **已確認：** PWC 與 CIM 啟用 mutation boundary 的原子交接。
- PWC 與 Context Broker 的 `context_requirement_reference` 契約。
- Shared resource、cross-zone request、deadlock 與 fairness 的確切調度策略。
- Writer stop、freeze、submit 與中央整合的交接事件。
- Agent Capability Registry：configured、available 與 mechanically active 的區分。
- 本 Subsystem 自己的完成判準與 Stress Contract，不沿用原 Domain 混合 profile。

以上仍是 gap，不構成實作決策。

## 10. 已確認的跨 Subsystem Contract

### PWC-CIM-001：Partition Activation

- PWC 建立 `planned` partition 後進入 `activating`。
- PWC 將 Work Package、partition、generation、trusted writer、base candidate、write resource digest 與 boundary mode 交給 CIM。
- 只有 CIM 對完全相同 tuple 回報 `boundary_active`，PWC 才進入 `active`。
- `activating` 期間不得向子代理暴露可寫施工工具。
- Boundary 失效、tuple mismatch 或 stale generation 時進入 `activation_failed`，改走隔離、序列或 recovery。

本 Contract 的 authority 在 Domain overview；本節只保存 PWC 的責任投影。

## 11. 已確認的跨 Subsystem Contract

### PWC-CIM-002：Writer Quiescence and Candidate Freeze

- PWC 只能以完整 integration group 發出 freeze request；Agent 的完成宣告只是觸發條件。
- Freeze request 必須綁定 partitions、generations、trusted writers、boundary instances、base candidate 與 submitted deltas。
- PWC 發出 request 後進入 `waiting_for_quiescence`，不得自行推定 writer 已停止。
- 只有 CIM 對相同 identity 回報 mechanical quiescence 並建立 frozen candidate manifest，PWC 才能進入 `writers_stopped`。
- 任一 writer 的 mutation closure 未知、外部副作用狀態未知或只有部分 partitions 靜止時，PWC 必須等待或進入 `freeze_failed`／`recovery_required`，不能提交部分 final candidate。單純遺失 exit code 但 mutation closure 已證明時可以繼續。

本 Contract 的 authority 在 Domain overview；本節只保存 PWC 的責任投影。

### 已確認場景 DDH-EO-E2E-002A：Agent 宣告完成但背景 Writer 尚未停止

- Agent 完成宣告只能觸發 freeze request。
- CIM 尚未證明 quiescence 時，PWC 必須維持 `waiting_for_quiescence`。
- Writer 在 bounded drain budget 內安全結束後自動續作；失聯、逾時或 mutation closure unknown 時轉入 `recovery_required`。
- PWC 不得以 reset、stash 或刪除方式製造 writer 已停止的假象。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002B：只有部分 Writers 已靜止

- PWC 必須以完整 integration group 判斷 freeze，不得用部分 quiescent partitions 建立 final candidate。
- 已靜止 partition 的 delta 可個別 seal 並保留，該 generation 不得恢復寫入。
- 剩餘 writers 正常靜止後自動續作；失敗或重派時必須建立新 generation。
- 局部 candidate 不得用於最終 Work Package 驗收。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002C：工具結果未知但 Mutation 狀態可或不可封閉

- PWC 不得把缺少 exit code 直接當成 freeze failure。
- CIM 證明 mutation closure 且完整 snapshot 可取得時，PWC 可以自動繼續 verification。
- Mutation closure 或外部副作用狀態未知時，PWC 必須轉入 recovery／高風險流程。
- `operation_result_unknown_but_mutation_closed` 不得被對外宣告成工具成功。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002D：Freeze Fence 與遲到寫入競態

- PWC 發出的 freeze request 必須建立可排序的 fence epoch。
- Fence 前已核准的 operations 可以 draining；fence 後的新 operation 與 stale generation 必須被拒絕。
- PWC 只能在 CIM 完成所有 fence 前 operation 的 reconciliation 後接受 quiescence。
- Frozen 後實際落入受驗證 snapshot 的 mutation 必須使 candidate 與 verification subject 失效。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

## 12. 已確認的 Recovery Chain

### RC-PWC-CIM-001：Registered Writer Not Quiescent

- PWC 必須將 writer stall 路由為 bounded drain、安全 termination 或 isolated new generation。
- Termination 不允許或失敗時，PWC 自動撤回舊 generation、保存可辨識 delta 並建立新 generation。
- Recovery 維持原 task specification、scope 與 acceptance，不建立人工 Checkpoint。
- 所有安全路徑耗盡時只輸出一次 `platform_blocked`。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-PWC-CIM-002：Stale Generation Result

- 被成功阻擋的 stale mutation 不得中斷 current generation。
- 隔離區中的 stale delta 只能 quarantine 為短期 reuse candidate，不得自動 admission。
- Current writer 可以在原授權 scope 內以 current generation 重新產生或明確採納需要的內容。
- Stale mutation 若已落地，PWC 必須建立 fresh generation 並切換安全 candidate，不建立人工 Checkpoint。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-DOM-003：Rebuildable Artifact Failure

- PWC 遇到 active boundary artifact 故障時，先停止暴露 writes，再協調 reprovision 或 isolation fallback。
- Rebuild 後必須重新執行 Partition Activation Contract，不能只恢復 metadata 狀態。
- Identity mismatch 必須 invalidate 依賴舊 identity 的 partitions／candidates。
- Recovery 不改變原 task specification、scope 或 acceptance。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-DOM-MVE-005：Product Verification Failure

- PWC 依 Failure Bundle 與 System Map／live-source impact closure，讓主 Agent 在原授權 scope 內建立 repair generation。
- 只擴大 verification closure 不授予額外 write scope。
- Candidate 修正後必須重新 freeze 並建立新 Verification Subject。
- 一般 repair／retest 循環不建立人工 Checkpoint；需要擴大 write scope 或改變規格／契約時才提升。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

## 13. 已確認的 System Map 使用 Contract

### SMQ-001：Architecture Impact Query

- PWC 在 initial scope plan 與 parallel partitioning 前，必須消費 selected node neighborhood 與 dependency intersection query。
- Query 結果只提供 partition／impact 候選，不授予 write scope 或 mutation permission。
- 下游 partition plan 必須引用 `architecture_query_result_id`，證明結果被實際消費。
- Index 不可用時走 bounded live-source fallback，不阻塞一般編排。

System Map 本身的 schema、index 與 query engine 不屬於本 Subsystem 規格。

## 14. 已確認 Contract：PWC-INTEG-003 Asynchronous Module Fork-Join and Subsystem Verification

### 14.1 目的

當一個 Subsystem 內的多個 Modules 具有可分離寫入範圍與固定 contract 時，PWC 可以同時啟動多條 Module lanes；各 lane 非同步實作、產生 Test Assets、自測與修復。只有全部 required lanes 滿足 mechanical join condition 後，才建立整合後 Subsystem candidate 並執行 Subsystem acceptance。

### 14.2 Fork 前條件

```text
pinned Subsystem specification and scenarios
＋ selected Module nodes
＋ System Map dependency／reverse-dependency intersection query
＋ live-source confirmation
＋ product and test write partitions
＋ shared resource ownership
＋ per-lane Context Envelope and budget
＋ join condition
```

- System Map query result 必須被 partition plan 實際消費，不得只呼叫。
- Shared public interface、schema、Subsystem state definition、generated client、configuration 與 shared fixture 必須有單一 owner 或明確序列化規則。
- Module 間 contract 尚未固定、寫入範圍高度重疊或整合成本高於平行收益時，PWC 必須減少 lanes 或改為序列施工。

### 14.3 Test Asset 施工邊界

- 新增／修改 pytest、fixture、helper 或 test configuration 是 Test Asset 施工。
- Implementation Agent 不得修改 protected acceptance assets；Test Agent 不得修改 product source。
- Implementation Agent 自行建立的 diagnostic／unit tests 只能提供 provisional feedback，不能取代 TAQG admitted acceptance。
- Test Agent 與 Subsystem Test Agent 可以在 Module product construction 期間平行撰寫 tests，只要 expected behavior 與 shared contracts 已固定。
- Draft tests 的 diagnostic PASS 不完成 Module lane 或 Work Package。

### 14.4 Module Lane Readiness

每條 lane 的 readiness 是 composite state：

```text
module_product_writer_quiescent
＋ immutable_module_lane_snapshot_identity
＋ required_module_test_assets_admitted
＋ module_verification_passed
＋ no_unresolved_shared_contract_request
＋ actual_diff_mapped_to_System_Map_nodes
```

建議狀態：

```text
planned
→ active
→ implementation_ready
→ module_verified
→ waiting_for_subsystem_join
```

Test authoring／admission 可以和 product implementation 非同步完成；狀態機必須等待 composite readiness，不能依 Agent 完成宣告推定。

Module lane snapshot 是短期、immutable 的 provisional verification input，不是 final Subsystem candidate。

### 14.5 Join Barrier

```text
all required lanes = module_verified
＋ all registered product writers quiescent
＋ all required test writer generations sealed
＋ all required test assets admitted
＋ no unresolved shared-resource mutation
＋ shared contracts remain pinned
＋ all lane generations are current
```

滿足後：

1. 依固定 integration order 組合 Module candidates／deltas。
2. 取得實際 integrated diff。
3. 重新消費 System Map changed-node、shared-dependency 與 reverse-dependent closure。
4. 完成 live-source reconciliation。
5. 由 CIM 凍結 immutable Subsystem candidate。
6. 由 MVE 建立包含 Module、Subsystem 與 affected regression assets 的 Verification Subject。

Join Barrier 是事件驅動自動轉換，不是人工 Checkpoint。

### 14.6 非同步等待與 Invalidation

- 先完成的 Module 進入 `waiting_for_subsystem_join`，停止 writer 並保留 current generation；不持續消耗 Agent。
- 其他 Module 繼續 bounded repair，不要求已完成 lanes 重做未受影響施工。
- Shared contract／fixture／configuration 或 dependency change 依 `DDH-INV-001` 只喚醒受影響 lanes。
- Stale lane generation 不得進入 join。
- Test Asset repair 建立新 manifest，不要求重做未受影響 product candidate。

### 14.7 Subsystem Acceptance

整合後 Verification Subject 至少包含：

```text
all required Module acceptance
＋ Subsystem business scenarios
＋ Module contract integration tests
＋ System Map affected reverse-dependent regression
＋ Quality Profile required concurrency／load／soak／recovery
```

- Module-level PASS 不是 Work Package completion。
- Module tests 必須依目前 integrated candidate 的 required closure 重跑；不能拿各自舊 candidate 的 PASS 拼成 Subsystem PASS。
- Subsystem test failure 使分析與重驗範圍提升到整個 Subsystem，但不自動授予每個 Module 寫入權。
- System Map／live source 找出實際責任 nodes 後，PWC 只重新開啟必要 Module partitions。
- Scope 外 repair 依 `MVE-RESULT-001` 建立 scope／contract／specification update proposal。

### 14.8 業務場景

**Given**

- Workspace Subsystem 包含 Path Normalizer、Manifest Loader 與 Manifest Index Adapter。
- 三個 Module product paths 與 test paths 可分離。
- Shared event contract 由主 Agent 單一擁有。

**When**

- 三條 Module lanes 非同步實作；各 Test Agent 平行建立 Module acceptance。
- Subsystem Test Agent 依固定業務規格提前建立跨 Module state-machine tests。
- Module A、C 先完成，Module B 仍在 repair。

**Then**

- A、C 進入 `waiting_for_subsystem_join`，writer 停止且不重複消耗 token。
- B 繼續 repair；沒有 shared dependency change 時不喚醒 A、C。
- B ready 後 mechanical Join Barrier 建立 integrated candidate。
- Integrated candidate 重跑 required Module tests，再執行 Subsystem scenarios 與 affected regressions。
- 若 Subsystem 場景失敗，PWC 以整個 Workspace Subsystem 分析，但只開啟實際需要修改的 Module partitions。

### 14.9 Stress Contract

- 大量 Module lanes 亂序完成時，Join Barrier 只能接受 current generations。
- 一個慢 lane 不得讓已完成 lanes 持續持有 Agent／runner 資源；fairness、timeout 與 repair budget 仍受 profile 控制。
- Shared contract event storm 必須 coalesce，但不得漏掉受影響 lanes。
- Integration order 必須 deterministic；worker completion order 不得改變 candidate content。
- 大型 Subsystem 的 join 不把全部 Module Context 注入每個 Agent。
- Routine waiting、join evaluation、invalidation 與 suite assembly 的 Agent token cost 為零。

### 14.10 對應機械測試

```text
test_independent_modules_can_construct_product_and_tests_asynchronously
test_test_asset_write_is_tracked_as_construction
test_draft_test_pass_cannot_complete_module_lane
test_module_lane_readiness_requires_product_quiescence_and_admitted_tests
test_early_module_waits_without_consuming_agent_resources
test_join_waits_for_all_current_module_generations
test_shared_contract_change_invalidates_only_affected_lanes
test_worker_completion_order_does_not_change_integration_order
test_module_passes_cannot_be_combined_without_integrated_candidate
test_integrated_candidate_reruns_required_module_and_subsystem_tests
test_subsystem_failure_expands_analysis_without_granting_all_module_writes
test_system_map_query_is_consumed_before_fork_join_and_subsystem_verification
```
