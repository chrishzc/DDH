# DDH Execution and Orchestration Domain 討論封存

> **封存說明（2026-08-02）：** 本文件最初以 ownership Subsystem 為範圍，後續逐項討論擴張到 Candidate Integrity、Context Broker、Mechanical Verification 與 Orchestration Evolution。它已不再代表單一 Subsystem 規格。
>
> 已確認內容將拆分至一份 Domain overview 與五份 Subsystem 規格。本文件只保留完整討論脈絡與舊 `OW-F／OW-S／OW-P` ID，不再新增設計，也不作為實作 SSOT。

**狀態：** Functional Design Confirmed／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 功能方向與逐項討論的業務場景已由人類確認；實作機制與數值門檻未確認  
**實作授權：** 無  
**規格層級：** Subsystem

本文件示範如何使用 DDH（Demand-Driven Harness）思維設計平行施工：先描述需要完成的功能、實際施工場景、邊界與壓力驗收，再反推必要的軟體能力。

已確認的用途是：

> 在多個 Agent 平行施工時，分離實作與驗收測試的寫入責任，避免互相覆寫、修改對方產物來製造綠燈，並在固定整合快照上產生可信的最終驗證。

`ownership` 只是其中的寫入衝突控制。本 Subsystem 暫稱「平行施工分區與整合」。它不是施工授權；任務規格與 scope 才決定可修改的總範圍。

本 Subsystem 不負責：

- 決定產品功能規格。
- 決定架構、schema 或公開契約是否可以改變。
- 自動擴大任務 scope。
- 直接宣告 Work Package 完成。
- 授權發佈、部署或其他外部副作用。
- 強迫每次任務都啟用子代理。

### 規格到測試的必要投影

本計畫中的每一項 `OW-Fxx` 功能，在進入實作前都必須具備：

1. 至少一個正常業務場景。
2. 至少一個拒絕、例外或故障場景。
3. 適用的邊界場景。
4. 適用時的壓力／併發場景；不適用時必須說明理由。
5. 可追溯的 pytest case 名稱或測試識別。

實作完成判定必須能形成：

```text
功能需求
→ 業務場景
→ pytest／其他可執行驗證
→ 固定 integration candidate 的結果
```

不能只有元件名稱、class 設計或 prompt 規則而沒有可觀察的業務驗收。

---

## 1. 業務角色

| 角色 | 責任 |
|---|---|
| 使用者 | 寫明 Agent 目標，確認需要人類決策的規格與風險 |
| 主 Agent | 解析任務規格、決定是否平行、切分寫入區、整合候選變更 |
| Implementation Agent | 在分配的產品程式區域內完成實作 |
| Test Agent | 從固定規格獨立撰寫 pytest、fixture 與驗收案例 |
| Write Guard | 依 Agent 身分與有效寫入分區，允許或阻擋寫入 |
| Integration Verifier | 對停止寫入後的固定候選快照執行最終驗證 |

角色名稱只描述責任，不代表必須各自是一個永久 Agent 或固定角色鏈。

---

## 2. 使用範例

### 2.1 任務目標

使用者寫明：

> 帳務 Subsystem 必須支援發票付款；成功付款只能入帳一次，重複請求不得重複入帳，付款失敗不得留下部分狀態。

這段使用者目標及其引用的長期規範，是本次任務規格的權威來源。

### 2.2 主 Agent 決定平行施工

主 Agent 分析後認為：

- 產品實作與驗收測試可由同一份固定規格獨立推導。
- 兩者主要寫入路徑不同。
- 共享的公開契約不能由任何子代理自行修改。
- 平行收益高於上下文載入與整合成本。

因此建立以下寫入分區：

| 寫入區 | 寫入者 | 允許內容 |
|---|---|---|
| `billing_implementation` | Implementation Agent | `src/billing/**` |
| `billing_acceptance_tests` | Test Agent | `tests/billing/**`、`tests/fixtures/billing/**` |
| `shared_contracts` | 主 Agent保留 | 公開 API、schema、跨 Subsystem contract |
| `task_specification` | 無 Agent 可寫 | 已固定的本次任務規格 |

所有 Agent 都能透過 System Map 索引搜尋必要資訊，但不因此自動載入檔案全文。實際內容由最小 Context Envelope、按需 content grant 與 context budget 控制。寫入分區不增加任務 scope。

### 2.3 平行施工

Implementation Agent：

- 實作成功付款。
- 實作 idempotency。
- 實作失敗 rollback。
- 可以執行測試，但不能修改驗收測試。

Test Agent：

- 撰寫成功付款 pytest。
- 撰寫重複付款 pytest。
- 撰寫失敗 rollback pytest。
- 撰寫金額及狀態邊界測試。
- 可以讀取產品程式與執行測試，但不能修改產品實作。

### 2.4 整合

1. 兩個 Agent 回報候選結果。
2. 主 Agent停止新的子代理寫入。
3. 系統確認沒有 active writer。
4. 建立固定 integration snapshot。
5. Integration Verifier 對該 snapshot 執行全部必要 pytest。
6. 只有固定 snapshot 的結果可作為本次完成證據。

平行施工期間的 pytest 結果只屬 provisional feedback 或 RED evidence。

---

## 3. 必要功能規格

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

Context 取得採：

> **寬搜尋、窄載入、按需擴充。**

- `discovery_scope` 讓子代理透過 System Map 搜尋 Entity、關係、位置與摘要。
- 初始 `Context Envelope` 只載入完成子目標所需的最小規格、契約、symbol、程式與測試內容。
- 子代理需要更多資訊時，必須說明請求內容、原因、預期用途及已檢查的替代來源。
- 主 Agent可以提供精確檔案、symbol、片段或摘要，也可以拒絕無關請求、重新切分任務或改為序列施工。
- 每個分區必須有 initial、expansion 與 single-request context budget；可記錄 token 預估、檔案／symbol 數、bytes 與擴充次數。
- 超過 budget 時不得靜默繼續載入；必須摘要、縮小子目標、改為序列施工或提出資訊／規格缺口。
- 敏感資源仍由獨立安全政策限制。

若子代理具有不受限制的 filesystem 讀取工具，context budget 只能算 prompt／編排約束，不能宣稱為機械限制。若要機械控制成本，必須由 Context Broker 或等效內容取得邊界執行 grant 與計量。

分區狀態保持精簡：

```text
planned → active → frozen → submitted
```

例外狀態只有 `revoked` 與 `recovery_required`。

### OW-F03：讀取與寫入分離

**確認狀態：已確認（2026-08-02）**

此功能的業務不變量是：

> 子代理在分區外產生的修改，不得影響使用者工作區或進入主 Agent的整合 candidate。

- 共享工作區可以在寫入前，以 Agent identity、partition generation 與 canonical resource 阻擋。
- 隔離候選區可以允許子代理產生私人 patch，但 Patch Admission 必須拒絕越區成果進入 integration candidate。
- 未分配、已撤回、已凍結、屬於其他 writer 或 protected resource 的修改必須阻擋。
- rename 的來源與目的、symlink／junction 的實際目標、formatter／generator 的間接產物都屬於 touched resources。
- 一次操作或 patch 同時包含合法與越區修改時，整份拒絕；Agent 必須重新產生只含合法範圍的成果。
- prompt 中的「請勿修改」不能宣稱為機械阻擋。
- 如果既無寫入前阻擋，也無隔離 candidate＋Patch Admission，平行化判定必須回到 `parallel_unsafe`。

判定結果：

| 結果 | 意義 |
|---|---|
| `write_allowed` | 所有目標都在 active 分區內 |
| `blocked_outside_partition` | 存在越區資源 |
| `blocked_protected_resource` | 嘗試修改規格或對方主要產物 |
| `blocked_stale_generation` | 分區已撤回或重新分配 |
| `shared_resource_request_required` | 需要主 Agent處理共享資源 |
| `mechanical_enforcement_unavailable` | 目前只有 prompt 約束，不能安全平行 |

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

跨區變更請求只處理「需要寫入其他資源」。只要求取得更多唯讀 Context 的情況，使用 OW-F02 content request，不能混用。

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

### OW-F08：固定整合快照

**確認狀態：已確認（2026-08-02）**

最終驗證前必須：

- 停止所有相關 writer。
- 確認不存在 active write。
- 整合已接受的 implementation、pytest、fixture、configuration、dependency 與必要 asset 變更。
- 固定規格版本與完整 source candidate。
- 產生可重現的 integration snapshot identity。

最終 PASS 必須綁定該 snapshot。

integration snapshot 必須能辨識：

- 任務規格版本及固定引用。
- 起始 baseline。
- 被接受的各 partition delta。
- 實際納入驗證的產品程式、測試、fixture、設定、dependency／lockfile 與必要 assets。
- tracked、untracked、rename 及 generated resources 中哪些屬於 candidate。
- snapshot generation 與穩定 identity。

Snapshot identity 的具體實作可以是 content hash、VCS tree、隔離 worktree identity 或其他可重現形式，本規格不預先指定。

必要不變量：

- 子代理各自 PASS 不等於 integration snapshot PASS。
- snapshot 建立後的任何 candidate 修改，都必須產生新的 identity。
- 舊 snapshot 的測試結果不得自動套用到新 candidate。
- 驗證工具若修改 source、tests、golden files 或設定，該次 snapshot 驗證必須失效或明確使用可拋棄副本。
- 規格版本在驗證期間改變時，原結果只能保留為歷史證據，不能完成新規格。
- 無法證明 candidate 穩定或內容完整時，不得開始 final verification。

### OW-F09：執行期間的機械觀測

**確認狀態：已確認（2026-08-02）**

此功能只服務當下施工、完成判定與失敗診斷。它不是長期 Evidence Retention，不建立永久簽章、receipt chain 或歷史 PASS 檔案。

在 Work Package active 期間，系統至少暫時持有以下 material events：

- 平行化判定及簡短理由。
- 分區的建立、Context grant、修改、凍結、撤回與移交。
- Agent／execution identity、partition generation、base candidate 與規格版本。
- 被阻擋的越區寫入，以及成功操作形成的 aggregate delta 摘要。
- 每個 writer 提交的候選 patch 與 Patch Admission 結果。
- 最終 integration snapshot identity 與 manifest。
- 驗證 invocation、failure classification 與結果。
- scope／specification exception report。

每個 verification invocation 至少包含：

- 實際 argv／命令。
- cwd。
- 非敏感 environment fingerprint。
- timeout 與輸出上限。
- 開始／結束時間。
- exit code 或 timeout／crash／environment failure。
- 綁定的 specification version 與 snapshot identity。
- 實際選取的 tests。
- stdout／stderr 的受控摘要或 artifact reference。

執行期觀測規則：

- Agent 自述 `PASS`、`已執行` 或 `無越界` 只能算 claim，不能取代 observed tool result。
- `unverified`、`not_applicable`、`blocked`、`environment_failure` 與 `pass` 必須分開。
- 成功的細粒度寫入可以依 tool operation 或 candidate delta 聚合；不要求永久記錄每一次正常檔案寫入。
- 越界阻擋、scope expansion、stale patch 與驗收弱化等重要例外必須個別記錄。
- stdout／stderr 必須有大小上限、截斷標記及敏感資訊遮罩；不能因截斷而把失敗誤報為 PASS。
- 原始 log、invocation 與 observed result 是短期工作資料，不得直接成為編排長期記憶。
- 完成判定當下仍必須由機械 runner 觀察到目前 verification subject 的 PASS；Agent claim 不能取代。
- 一般節點完成後，不保留歷史 invocation、PASS log、snapshot report 或 Ledger 作為長期證據。
- 完成後留下的 Evidence Retention 是可再次機械執行的 pytest／fixture／configuration／profile 等驗證資產。
- 日後需要證明功能仍正常時，重新執行 active 且未過期的 pytest，不引用歷史 PASS。
- 發佈、法遵、外部副作用或其他高風險流程若需要額外歷史留存，必須由其獨立規格明確要求，不由一般 Work Package 默認保留。

### OW-F10：故障復原

**確認狀態：已確認（2026-08-02）**

當 Agent crash、失聯或留下不完整變更時：

- 不得自動讓其他 Agent 接管該分區。
- 主 Agent 必須先保存並檢查殘留 diff。
- 必須檢查 execution identity、process 狀態、cwd、environment、sandbox／permission 與 candidate generation。
- 必須區分產品／測試失敗、環境失敗、工具失敗、Agent 中斷、規格缺口、scope 缺口及外部副作用不確定。
- 必須判定可續作、環境修復後重試、需重新分配、保留後放棄或需人類介入。
- 不得破壞任務開始前已存在的使用者差異。
- 不得為了恢復乾淨狀態而自動 reset、stash、delete 或覆寫共享工作區。
- 隔離候選可以被放棄，但仍須先保存有診斷價值的 patch 與 evidence。
- 相同 failure fingerprint 反覆發生且沒有新增證據時，不得無限重試；必須消耗 attempt budget 並在門檻後結構化回報。

每次復原判定至少使用短期 Attempt Ledger：

- attempt／invocation identity。
- partition、generation 與 base candidate。
- failure classification 與 fingerprint。
- 已採取的修正。
- 本次新增證據。
- 保留的 candidate delta。
- 剩餘重試／Context／工具預算。

復原結果至少能表達：

| 結果 | 意義 |
|---|---|
| `safe_to_retry` | 狀態明確，可在同一規格與 scope 內重試 |
| `retry_after_environment_fix` | 先修復依賴、權限、cwd 或執行環境 |
| `repartition_required` | 原分區或 Agent 能力不適合，需要安全移交 |
| `preserve_and_stop` | 保留有用成果，但目前不再自動繼續 |
| `human_spec_scope_or_risk_decision` | 需要改規格、scope、風險政策或處理不確定外部副作用 |

### OW-F11：防止接受過期成果

**確認狀態：已確認（2026-08-02）**

每個子代理成果必須綁定：

- 任務規格版本。
- 起始 candidate／baseline identity。
- writer identity。
- 分區 generation。
- 實際 touched resources。

主 Agent套用成果前必須判定：

- 起始 candidate 之後，相關資源或依賴契約是否已改變。
- patch 是否仍可安全套用。
- 是否需要刷新 Context Envelope、重新產生 patch 或重新驗證。
- 舊 owner 或舊 generation 的遲到成果是否必須拒絕。

子代理回報 `PASS` 不足以讓舊成果自動進入目前 candidate。

Patch freshness 判定至少能表達：

| 結果 | 意義 |
|---|---|
| `current_candidate` | base、generation、specification 與依賴均仍有效 |
| `non_overlapping_but_revalidation_required` | 可重新套用，但 candidate 已變更，必須重驗影響閉包 |
| `stale_generation` | writer／partition generation 已被撤回或取代 |
| `stale_specification` | 任務規格或固定引用已變更 |
| `stale_dependency_contract` | touched paths 未重疊，但所依賴契約已變更 |
| `conflicting_candidate_delta` | 實際 path、rename、delete 或 logical resource 發生衝突 |
| `freshness_unknown` | 依賴、base 或實際 touched resources 無法可靠判定 |

System Map 可提供候選依賴與影響範圍，但不能單獨證明 freshness。若 live source、schema、configuration、API 或 dependency manifest 顯示不同關係，必須依實際證據擴大檢查並回報 Map drift。

可安全重新套用不代表舊 PASS 仍有效；除非 verification 綁定的完整 snapshot identity 完全相同，否則至少要重跑受影響驗證。

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

### OW-F14：建立 Mutation Mediation Boundary

**確認狀態：已確認（2026-08-02）**

Write Guard 與 Patch Admission 的需求不是「檢查某一種 edit tool」，而是：

> 所有可能改變受保護 candidate 的 mutation，都必須經過可信 execution identity、active partition、canonical resource 與 candidate generation 的機械判定。

共享防護模式至少需要三層：

1. **Pre-operation admission：** 對可預先辨識目標的 patch、move、delete、write 等操作，在執行前檢查全部目標。
2. **Execution containment：** 對 formatter、generator、package manager、compiler plugin 或一般 shell process 等無法完整預知目標的工具，以 sandbox／filesystem boundary 限制可影響範圍。
3. **Post-operation reconciliation：** 操作結束後比較 baseline／candidate delta，確認沒有間接越區、rename、generated 或未追蹤產物。

隔離 candidate 模式至少需要：

1. 子代理只能影響自己的私人 candidate，不得直接改變 integration candidate 或使用者工作區。
2. 提交時產生完整 touched-resource／patch manifest。
3. Patch Admission 重新檢查 scope、partition、generation、freshness、logical resource 與 protected resources。
4. 只有 accepted patch 能形成新的 integration candidate。

可信邊界：

- Agent／execution identity 必須由實際執行通道提供，不能信任 Agent 自己填寫的字串。
- partition、generation 與 candidate identity 必須由核心查得，不能由 tool caller 任意宣告。
- path 必須依實際 filesystem semantics canonicalize，包含大小寫、separator、`..`、symlink／junction、rename old／new 與 mount boundary。
- 一次操作包含任何非法目標時，整個操作或 patch 拒絕。
- 如果 precheck 後、落盤前的狀態可能改變，必須採原子 admission、filesystem containment 或以 post-delta fail closed；不得忽略 TOCTOU。
- Mutation Mediation 無法使用或狀態不確定時，相關 partition 必須 freeze／recovery，不能降級成 prompt-only。
- filesystem boundary 不處理 DB、network、credential、deployment 等外部副作用；它們仍轉入 OW-F13 的高風險流程。

判定結果至少能表達：

| 結果 | 意義 |
|---|---|
| `mutation_admitted` | mutation 在可信身分與 active partition 內 |
| `mutation_blocked_resource` | 目標越區、protected 或 shared |
| `mutation_blocked_identity` | 執行身分不符或不可驗證 |
| `mutation_blocked_generation` | partition／candidate generation 已過期 |
| `mutation_requires_isolation` | 工具影響範圍無法在共享模式安全預測或限制 |
| `mutation_reconciliation_failed` | post-operation delta 出現未預期變更 |
| `mutation_boundary_unavailable` | 機械邊界失效，必須 freeze／recovery |

### OW-F15：Candidate Identity 與 Snapshot Manifest

**確認狀態：已確認（2026-08-02）**

系統必須分開三種概念：

| 概念 | 回答的問題 |
|---|---|
| `source_snapshot_id` | 實際被驗證的程式、測試、設定與資產內容是否完全相同？ |
| `candidate_generation` | 這個 candidate 在本次整合與 ownership 時序中的位置？ |
| `verification_subject_id` | 哪份 source snapshot 依哪份規格與驗證契約接受判定？ |

建議關係：

```text
Snapshot Manifest
→ source_snapshot_id

source_snapshot_id
＋ specification version
＋ verification contract version
＋ environment profile
→ verification_subject_id
```

`candidate_generation` 是單調的協調序號，不是內容 hash。同一份內容可以在不同 generation 再次出現；不同規格也可以驗證相同 source snapshot，但必須得到不同 verification subject。

Snapshot Manifest 至少描述：

- repository／workspace logical root identity，不使用機器絕對路徑作內容身分。
- canonical relative path。
- resource type：regular file、symlink／junction representation、directory marker 或必要特殊資產。
- content digest。
- 會影響執行時的 mode／executable bit 或 platform semantics。
- tracked、untracked、generated、configuration、test、fixture、dependency／lockfile 與必要 asset 的納入狀態。
- 明確排除的 cache、log、temporary output 及排除理由／profile。
- manifest format version。

Candidate provenance 另外記錄，不放入內容 hash：

- baseline identity。
- pre-existing user changes。
- accepted patch ids。
- partition／writer／generation。
- parent candidate。
- 建立時間與執行環境。

必要不變量：

- mtime、絕對路徑、使用者名稱、隨機 temporary path 等非內容資訊不得造成 source identity 漂移。
- 任一會影響產品、測試選取、驗收結果或重現性的內容變更，都必須改變 `source_snapshot_id`。
- 同一 source snapshot 套用不同 specification／verification contract，必須改變 `verification_subject_id`。
- manifest 有 unreadable、unknown 或必要 untracked dependency 未分類時，不得建立 final verification subject。
- identity algorithm 必須穩定、collision-resistant、versioned 且採 canonical serialization；具體採 SHA-256、BLAKE3 或其他演算法留待實作比較。
- verification result 必須綁定 `verification_subject_id`，不能只綁 candidate generation。

### OW-F16：Context Broker 與 Context Budget

**確認狀態：已確認（2026-08-02）**

Context Broker 的業務責任是：

> 讓子代理可以透過 System Map 廣泛定位資訊，但只把完成子目標所需的最小、最新且可追溯內容載入模型 Context。

Context 流程：

```text
System Map／symbol／path discovery
→ metadata、關係與摘要
→ 子代理提出 content request
→ 主 Agent／Broker 判斷相關性、版本與預算
→ exact symbol、excerpt、summary 或拒絕
→ 計入 Context Ledger
```

成本單位：

- 主要單位：實際或可靠估算的 input tokens。
- 輔助護欄：files、symbols、raw bytes、request count、dependency traversal depth。
- Context budget 只代表載入成本；模型總預算、工具預算與 Work Package budget 仍分開計算。

每個 partition 至少具有：

- `initial_context_budget`。
- `expansion_context_budget`。
- `single_grant_limit`。
- 保留給規格、驗收、必要輸出與後續診斷的 reserve。
- Context Ledger：已載入 artifact、版本／digest、token cost、來源與用途。

內容優先順序：

1. 使用者目標、固定規格條目與 acceptance。
2. 必要契約、不變量與禁止事項。
3. 直接相關的 implementation／test symbols。
4. 相鄰依賴的摘要與最小片段。
5. 廣泛文件、歷史紀錄與大範圍 source，只在有具體理由時提供。

Grant 結果至少能表達：

| 結果 | 意義 |
|---|---|
| `grant_exact_content` | 提供必要完整 symbol／小型檔案 |
| `grant_excerpt` | 只提供相關範圍與必要周邊 |
| `grant_summary_or_index` | 先提供摘要、位置與關係 |
| `deny_irrelevant_or_duplicate` | 無關或已載入，不重複消耗 |
| `repartition_or_serialize_required` | 子目標需要過多共享 Context，原切分失去價值 |
| `context_budget_exhausted` | 不再靜默擴充，必須重整或停止 |
| `specification_gap` | 缺少的是 expected behavior，不是更多 source |

必要不變量：

- 規格、acceptance 與禁止事項屬 pinned context，不得為騰出空間而被摘要成改變語意的版本或直接移除。
- loaded source 必須綁定 digest／candidate；內容變更後舊 Context 標記 stale，不能假裝仍是最新。
- System Map 只提供 discovery；Map 與 live evidence 衝突時提供實際 source，並產生 Map drift 待辦。
- 同一 artifact 不重複注入全文；使用 reference／cache 或增量差異。
- 子代理要求整個 Domain 時，Broker 應先提供 index／summary，要求說明具體決策需要。
- 反覆要求大量 Context 表示 partition 可能切錯；主 Agent必須重新執行 OW-F01。
- 如果子代理仍有不受 Broker 控制的 filesystem 讀取通道，只能稱為編排 budget，不能宣稱機械限制。
- 敏感內容的拒絕或遮罩由獨立安全政策決定；Context grant 不擴大資料存取權。

具體 token 數不在此預先固定。預設 profile 應依模型 context limit、任務層級、子目標、Context reuse 能力與 Work Package 預算產生，並保留可完成推理與輸出的空間。

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

### OW-F18：Attempt Ledger 暫存與自進化消化

**確認狀態：已確認（2026-08-02）**

Attempt Ledger 的責任是：

> 在 Agent 自主執行「施工／驗證／診斷／修正／重驗」時，判斷是否有新進展、是否正在重複同一失敗，並作為編排自進化的短期原料。

一個 Attempt 代表一次可辨識的：

```text
起始 candidate
→ action／delta
→ verification invocation
→ observed result
→ recovery／next decision
```

Ledger 每筆至少保存：

- Work Package、specification、verification subject。
- attempt、partition、writer／execution、generation identity。
- base candidate 與產生的 candidate／patch identity。
- 實際 verification invocation ids。
- failure classification 與 mechanically normalized fingerprint。
- 本次採取的修正摘要。
- 相較前次新增的證據。
- Context、token、tool、verification compute 與時間預算消耗。
- 結果：continue、retry、repartition、preserve-and-stop 或 human decision。
- bounded artifacts references。

不得直接放入 Ledger：

- 完整 Agent prompt。
- 完整對話。
- 無上限 stdout／stderr。
- credential、個資或未遮罩秘密。
- 沒有證據支持的 Agent 心得。

Failure fingerprint 應優先由機械資訊建立，例如：

- test node id／scenario id。
- failure category。
- normalized exception／assertion location。
- exit／signal／timeout。
- environment fingerprint。
- candidate／verification subject。

Agent 摘要可以附加，但不能取代 observed fingerprint。

### 進展與停止判定

- 相同 fingerprint、相同 relevant candidate、相同修正策略且沒有新增證據，視為 no-progress repeat。
- failure 改變、找到新根因證據、candidate 有實質相關變化或 environment 已修復，視為新的診斷狀態。
- 新證據不會把已消耗預算歸零，但可以允許依 Work Package policy 繼續。
- 達到 no-progress、attempt、token、tool 或時間預算時，機械 runner／orchestrator 必須停止自動循環並產生結構化報告。

### Ledger 生命週期

```text
Active Work Package 產生 Attempt Ledger
→ Work Package 結束
→ Evolution Analyzer 讀取 Ledger
→ 與既有長期編排記憶比較、聚合與判斷
→ Critic／既定流程接受、拒絕或更新記憶候選
→ 標記 Ledger 已消化
→ 刪除原始 Attempt Ledger 與一般執行 logs
```

已確認的原則：

- Attempt Ledger 不永久保存。
- Ledger 被自進化流程參考、與長期記憶比對並完成整合處理後，就應刪除。
- 沒有產生新長期記憶也是合法的消化結果；仍可標記 consumed 後刪除。
- 原始 log、完整對話與 Ledger 內容不直接複製進長期記憶。
- 長期記憶只保留經驗結論、適用條件、證據摘要、信心、版本、失效條件與衝突處理。
- Ledger 尚未完成消化時屬短期 pending material，不是 Evidence Retention。
- 何時觸發消化、等待多久、批次大小、失敗重試及長期無法消化時如何處理，留待後續確認。

節點任務完成後，長期留下的 Evidence Retention 只有可重複執行的 pytest 驗證資產及其必要 fixture／configuration／profile。歷史 PASS 不保存；節點日後被修改時，重新執行仍 active、未 stale 的既有 pytest，以檢查原有功能是否正常。

### OW-F18.1：Attempt Ledger 最小資料模型

**確認狀態：已確認（2026-08-02）**

Ledger 不採通用的逐工具 Event Store，而是三段式短期資料：

```text
Work Package Summary
＋ Partition Summaries
＋ Attempt Rows
```

#### Work Package Summary

| 欄位 | 用途 |
|---|---|
| `ledger_id` | 本次短期 Ledger identity |
| `work_package_id` | 關聯本次任務 |
| `specification_reference` | 使用的規格版本 |
| `scope_level` | Global／Domain／Subsystem／Module |
| `risk_class` | 本次風險分類 |
| `parallelization_result` | OW-F01 判定與理由分類 |
| `started_at`／`ended_at` | 計算整體時間成本 |
| `terminal_outcome` | completed／stopped／cancelled／human-decision |

#### Partition Summary

| 欄位 | 用途 |
|---|---|
| `partition_id`／`generation` | 對應本次施工分區 |
| `subgoal_id` | 不保存完整 prompt，只引用結構化子目標 |
| `agent_profile` | 角色、模型／能力 profile 與模板版本 |
| `write_zone_digest` | 寫入區摘要，不複製所有檔案內容 |
| `initial_context_profile` | 初始 Context 類型與 token 成本 |
| `context_expansion_summary` | 額外請求次數、成本、拒絕與重新切分 |
| `partition_outcome` | submitted／repartitioned／recovery／cancelled |

#### Attempt Row

| 欄位 | 用途 |
|---|---|
| `attempt_id`／`sequence` | 同一 partition 內的嘗試順序 |
| `input_candidate_id` | 本次開始的 candidate |
| `action_class` | implement／test-authoring／diagnose／repair／integrate／environment-fix |
| `output_candidate_id` | 有產生內容時記錄新 candidate |
| `verification_suite_ids` | 本次機械執行的 pytest suites |
| `observed_outcome` | pass／test-fail／timeout／crash／environment-fail／blocked |
| `failure_fingerprint` | 機械正規化的失敗特徵 |
| `new_evidence` | 是否取得新證據及其短摘要／digest |
| `coordination_events` | Context request、cross-zone request、handoff、conflict 的計數與分類 |
| `cost_delta` | agent tokens、verification compute、environment setup、wall time |
| `next_decision` | continue／retry／repartition／serialize／stop／human-decision |

必要限制：

- 不保存完整使用者需求、Agent prompt 或對話；使用已固定規格與子目標 reference。
- 不保存完整 source diff；只在 active execution 期間引用 candidate／patch。
- 不保存完整 stdout／stderr；只保留 fingerprint 與短期 artifact reference。
- 正常 tool read／write 不逐筆寫入 Ledger。
- 只有形成一次施工、驗證或決策循環時才新增 Attempt Row。
- 同一 Attempt 的後續欄位可以在 active 期間完成；一旦 closed，不改寫事實，錯誤以 correction 欄位或新 row 說明。
- Ledger 被 Evolution Analyzer 消化後整體刪除，不留下 compact copy。

### OW-F18.2：短期 Log Buffer 與輸出邊界

**確認狀態：已確認（2026-08-02）**

Log 的責任只有：

> 在 active execution 期間協助機械判定、Agent 診斷與 failure replay；它不是 Ledger、不是 Evidence Retention，也不直接成為長期記憶原料。

Log 來源包括：

- pytest／mechanical runner 的 stdout、stderr 與 structured report。
- tool／process 的 stdout、stderr、exit、signal 與 timeout。
- Write Guard、Patch Admission、freeze／handoff 的錯誤詳情。
- stress／race test 的 seed 與必要 replay trace。

一般成功 read、write 與每個 filesystem syscall 不建立詳細 log。重要結果應優先使用 JUnit、JSON 或其他結構化 runner output，而不是再由 Agent閱讀文字猜測。

每個 invocation 使用有界短期 buffer：

- `max_stdout_bytes`。
- `max_stderr_bytes`。
- `max_structured_report_bytes`。
- `max_replay_trace_bytes`。
- `timeout`。
- `repetition_collapse_policy`。
- `sensitivity_policy`。

超出上限時：

- 保留機械 exit／timeout／crash outcome。
- 明確標記 `truncated: true`。
- 優先保存 test id、assertion／exception location、頭尾片段與 failure fingerprint 所需內容。
- 重複行可機械聚合為 count。
- 不得因 log 被截斷就把 FAIL 改成 PASS 或 unknown。

Agent Context 規則：

- Routine PASS 只提供 suite、pass count、duration 與成本摘要。
- FAIL 只提供規格條目、test id、fingerprint、必要 stack／assertion excerpt 與相關最小 Context。
- 相同 fingerprint 的完整 excerpt 不反覆注入；只提供新增差異。
- Agent 明確需要更多 log 時，使用有 budget 的 diagnostic content request。
- 整份 log 不自動進入 prompt。

安全規則：

- credential、token、個資與受保護值在寫入一般 buffer 或送入 Agent 前遮罩。
- binary dump、core dump 與大型 trace 預設不載入 Context；只有獨立安全／診斷規格允許才暫存。
- 無法安全遮罩的敏感輸出不得進入一般 Ledger 或 Evolution Analyzer。

Evolution 規則：

- Evolution Analyzer 預設只讀三段式 Attempt Ledger。
- 原始 log 不直接提供給長期記憶模型。
- 只有 Ledger 顯示某個編排模式需要額外判定時，Critic／Analyzer 才能在 log 尚存在期間請求最小、遮罩後的 failure excerpt。
- 不論是否被請求，原始 log 都不會被複製進長期記憶。

具體 buffer 大小與刪除時機留待 profile／生命週期討論；核心要求是有界、可截斷、可遮罩、非永久，且不隨輸出量線性消耗 Agent tokens。

### OW-F18.3：Ledger 消化觸發與刪除時機

**確認狀態：已確認（2026-08-02）**

Ledger 生命週期採：

```text
active
→ sealed_pending_evolution
→ mechanically_prefiltered
→ selected_for_model_analysis（必要時）
→ critic_decided
→ consumed
→ deleted
```

Work Package 進入 completed、stopped、cancelled 或 human-decision 時，立即 seal Ledger，不再新增 Attempt Row；後續 correction 必須在消化前以明確修正資料加入。

### 先機械比對，再決定是否使用模型

Mechanical Prefilter 不使用 Agent／LLM，依三段式 Ledger 比較：

- scope level、risk class、agent／template profile。
- parallelization result。
- Context expansion 與 cross-zone／handoff／conflict 模式。
- failure fingerprints、no-progress 與 terminal outcome。
- token、compute、environment 與 wall-time 成本。
- 既有長期記憶的 applicability、version 與已知 pattern。

Prefilter 結果：

| 結果 | 後續 |
|---|---|
| `known_pattern_no_change` | 更新既有記憶的機械支持計數／最近觀察摘要，Ledger consumed |
| `routine_no_orchestration_signal` | 不建立記憶，Ledger consumed |
| `candidate_new_pattern` | 進入模型 Analyzer |
| `candidate_repeated_pattern` | 與同群組 Ledgers 批次進入 Analyzer |
| `critical_orchestration_failure` | 優先進入 Analyzer／Critic |
| `prefilter_unknown` | 保持 pending，等待修復或人工政策 |

只有下列編排訊號需要模型分析：

- 任務切分反覆造成跨區請求、整合衝突或序列回退。
- Context template 造成大量擴充、budget exhaustion 或無關載入。
- Agent profile／能力與子目標不匹配。
- 同 failure fingerprint 無進展重試。
- recovery、handoff、stale patch 或 isolation mode 反覆出現問題。
- 某種派工方式在相似條件下持續顯著成功或失敗。

產品本身的一次性 bug、單一 assertion failure 或普通實作錯誤，若沒有編排訊號，不啟動自進化模型。

### 觸發策略

採混合觸發：

1. **Terminal prefilter：** 每個 Ledger seal 後立即執行無 Agent prefilter。
2. **Critical trigger：** 嚴重編排失敗、反覆 no-progress、危險 ownership／recovery 問題優先送 Analyzer。
3. **Batch trigger：** 相似候選累積到設定數量、等待時間或 backlog／storage 門檻時批次分析。
4. **Evolution change gate：** 修改角色 prompt、Context template 或派工 policy 前，先分析相關 pending candidates 並交由 Critic 驗證。
5. **Idle／maintenance trigger：** 有可用預算時處理低優先候選。

具體數量、等待時間與 token budget 由 Evolution Profile 設定，不在核心規格寫死。

### 模型分析與 Critic

- Analyzer 只接收 Ledger features、相關既有記憶與必要最小 failure excerpt，不接收完整 prompt、source、diff 或 logs。
- Analyzer 產生 memory candidate：適用條件、問題／成功模式、建議派工調整、證據摘要、信心、版本與失效條件。
- Critic 以 replay、歷史對照或小範圍試用決定 accepted、updated、rejected 或 insufficient-evidence。
- rejected pattern 可以留下有期限、可失效的 suppression summary，避免相同候選反覆消耗 token；不保存原始 Ledger。

### 刪除條件

只有出現以下任一完整結果，Ledger 才能標記 consumed：

- 已確認更新既有長期記憶。
- 已確認建立新長期記憶。
- Critic 拒絕候選。
- 證據不足並完成 suppression／重新累積決策。
- Mechanical Prefilter 確認沒有編排訊號或只是已知模式。

`consumed` 後刪除：

- Work Package Summary。
- Partition Summaries。
- Attempt Rows。
- 一般 execution logs 與短期 artifacts。

不刪除：

- 產品 source。
- active pytest／fixture／configuration／profile。
- 使用者工作區差異。
- 已接受的長期編排記憶。

Analyzer／Critic／prefilter 失敗或狀態未知時，不得標記 consumed。如何處理長期 pending backlog、最長等待與最終降級策略，需由 Evolution Profile 另行確認。

---

## 4. 業務驗收場景

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

### OW-S12：合法的分區內寫入

**對應功能：** OW-F03

**Given**

- Test Agent 持有 active 的 `tests/billing/**` 寫入分區。

**When**

- 它只修改 `tests/workspace/test_path_normalizer.py`。

**Then**

- 結果為 `write_allowed`。
- 其他不重疊 writer 不應被全域鎖錯誤阻擋。

### OW-S13：同一 patch 混合合法與越區修改

**對應功能：** OW-F03

**Given**

- Test Agent 只擁有 `tests/billing/**`。

**When**

- patch 同時修改 `tests/workspace/test_path_normalizer.py` 與 `src/workspace/path_normalizer.py`。

**Then**

- 整份 patch 結果為 `blocked_outside_partition`。
- 兩個修改都不得進入 integration candidate。
- Agent 必須重新產生只含合法測試變更的 patch。

### OW-S14：間接工具造成越區修改

**對應功能：** OW-F03

**Given**

- Agent 執行 formatter 或 generator。

**When**

- 工具除了分區內檔案，也修改 root configuration 或其他 Agent 的產物。

**Then**

- 所有實際 touched resources 都必須被檢查。
- 不得因命令本身在允許清單中，就忽略其越區結果。
- 共享工作區應阻擋或復原該原子操作；隔離候選區則拒絕整份 patch admission。

### OW-S15：沒有機械寫入邊界

**對應功能：** OW-F03

**Given**

- 子代理具有不受限制的共享工作區寫入工具。
- 系統沒有 Write Guard、sandbox 或隔離 candidate 的 Patch Admission。

**When**

- 主 Agent評估是否啟動平行施工。

**Then**

- 結果必須包含 `mechanical_enforcement_unavailable`。
- OW-F01 必須判定為 `parallel_unsafe`。
- 不得把 prompt 白名單描述為機械 ownership。

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

- Implementation Agent 的分區明確包含 `tests/unit/billing/**`。
- Test Agent 負責的是 `tests/acceptance/billing/**`。

**When**

- Implementation Agent 為內部計算新增 unit tests。

**Then**

- 寫入應被允許。
- unit tests 不得取代獨立 acceptance。
- Implementation Agent 仍不得修改 `tests/acceptance/billing/**`。

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

- Billing 分區正在序列修改自己的 shared fixture。
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

- Billing 任務的核准 scope 不包含 Customer Profile Module。
- Agent 認為修改 Customer Profile 可以讓本次實作更容易。

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

### OW-S40：正常建立整合快照

**對應功能：** OW-F08

**Given**

- Implementation Agent 與 Test Agent 均已提交候選 delta。
- 所有相關 partitions 已 frozen。

**When**

- 主 Agent接受兩份 delta，連同必要 fixture 與設定建立 integration snapshot。

**Then**

- snapshot 綁定固定任務規格版本。
- snapshot identity 可重複計算且一致。
- final pytest 只對該 snapshot 執行。
- PASS 報告能回指實際納入的 source 與 test candidate。

### OW-S41：仍存在 active writer

**對應功能：** OW-F08

**Given**

- 一個相關 partition 仍為 active，或存在未完成寫入。

**When**

- 主 Agent要求建立 final integration snapshot。

**Then**

- snapshot 建立必須被拒絕或保持非 final 狀態。
- 不得在變動中的共享工作區產生可宣告完成的 PASS。

### OW-S42：Snapshot 建立後又發生修改

**對應功能：** OW-F08

**Given**

- candidate `C10` 已建立 snapshot identity。

**When**

- 任一 source、test、fixture、configuration 或必要 asset 被修改。

**Then**

- 產生新的 candidate identity `C11`。
- `C10` 的驗證結果不得標記為 `C11` PASS。
- 必須依影響閉包決定 `C11` 要重跑的驗證。

### OW-S43：驗證工具修改 candidate

**對應功能：** OW-F08

**Given**

- pytest plugin、formatter 或 snapshot test 會更新 golden files 或 source-adjacent assets。

**When**

- final verification 直接修改原 integration snapshot。

**Then**

- 該次 verification 不得產生 final PASS。
- 系統必須使用可拋棄副本，或把產物變更形成新 candidate 後重新驗證。
- 不得忽略測試執行造成的工作區 delta。

### OW-S44：Snapshot 包含既有使用者差異

**對應功能：** OW-F08

**Given**

- 使用者原有 dirty changes 與本次 Agent delta 同時存在。

**When**

- 主 Agent建立 integration snapshot。

**Then**

- snapshot manifest 必須指出哪些是 baseline 既有內容、哪些是本次接受的 delta。
- 不得為建立快照而 reset、stash 或覆寫使用者變更。
- 若無法安全組成可驗證 candidate，必須回報而不是假裝使用乾淨版本。

### OW-S45：各子代理個別 PASS，但整合 candidate 失敗

**對應功能：** OW-F08

**Given**

- Implementation Agent 與 Test Agent各自回報 PASS。

**When**

- 兩者成果整合後的 Subsystem pytest 失敗。

**Then**

- Work Package 不得完成。
- 回到 Subsystem 層級分析整合契約與互動。
- 個別 PASS 保留為診斷證據，但不具有完成效力。

### OW-S46：遺漏 untracked 或 generated dependency

**對應功能：** OW-F08

**Given**

- 測試依賴一個新產生但尚未納入 snapshot manifest 的 fixture 或 generated file。

**When**

- 主 Agent建立 snapshot 或在隔離環境重現。

**Then**

- candidate completeness check 必須失敗。
- 不得只在原工作區偶然 PASS 就宣告可重現。
- 缺漏資源納入新 candidate 後重新驗證。

### OW-S47：驗證期間規格版本更新

**對應功能：** OW-F08

**Given**

- final verification 綁定規格 `v3`。

**When**

- 人類確認新的規格 `v4`。

**Then**

- `v3` 結果保留為歷史證據。
- `v3` PASS 不得完成 `v4`。
- 必須建立引用 `v4` 的新 candidate／verification cycle。

### OW-S48：正常產生完成證據

**對應功能：** OW-F09

**Given**

- final pytest 對固定 integration snapshot 執行。

**When**

- invocation 正常結束並通過。

**Then**

- 記錄實際命令、cwd、timeout、test selection、exit code、規格版本與 snapshot identity。
- 完成報告可以從 observed result 產生。
- 不需要永久記錄每一次成功的底層檔案寫入。

### OW-S49：Agent 宣稱測試通過但沒有執行證據

**對應功能：** OW-F09

**Given**

- 子代理文字回報「全部 pytest 已通過」。
- 系統找不到綁定目前 snapshot 的 verification invocation。

**When**

- 主 Agent評估完成狀態。

**Then**

- 狀態為 `unverified`，不是 `pass`。
- Agent claim 保留作為訊息，但不能建立完成證據。

### OW-S50：區分產品失敗與執行環境失敗

**對應功能：** OW-F09

**Given**

- pytest process 因 timeout、crash、dependency missing 或權限問題結束。

**When**

- 系統記錄 invocation。

**Then**

- 結果分別標記為 test failure、timeout、process crash 或 environment failure。
- 不得把機械環境失敗直接解讀為產品不符合規格。
- 需要重試時仍綁定新的 invocation identity。

### OW-S51：驗證輸出包含敏感資訊

**對應功能：** OW-F09

**Given**

- stdout／stderr 意外包含 credential、token 或受保護資料。

**When**

- 系統保存診斷證據。

**Then**

- 敏感內容在持久化前被遮罩或隔離到受控 artifact。
- 一般完成報告不得回顯秘密。
- 遮罩不能刪除 exit status、failure classification 與必要錯誤位置。

### OW-S52：大量正常寫入採聚合證據

**對應功能：** OW-F09

**Given**

- formatter 在合法分區內修改大量檔案。

**When**

- 操作成功且沒有越區。

**Then**

- 可記錄單一 operation summary 與 candidate delta，而非每個 byte／write syscall。
- touched resources 仍必須可供 admission 與 scope 檢查。
- 不能以聚合為由忽略越區檔案。

### OW-S53：證據儲存暫時不可用

**對應功能：** OW-F09

**Given**

- Agent 可以繼續在隔離候選區進行診斷。
- 但系統無法可靠保存 final snapshot 或 verification evidence。

**When**

- 測試看似通過。

**Then**

- 可以保留 provisional 狀態並嘗試恢復。
- 不得宣告 Work Package 完成。
- 不得用 Agent 摘要替代遺失的 observed result。

### OW-S54：Agent claim 與 observed result 衝突

**對應功能：** OW-F09

**Given**

- Agent 回報 PASS。
- 實際 invocation exit code、timeout 或 test selection 顯示未通過完整驗證。

**When**

- 主 Agent產生完成報告。

**Then**

- 以 observed result 判定。
- 衝突被標示供診斷。
- 不得靜默把 claim 改寫成機械證據。

### OW-S55：短期事件不得直接進入長期記憶

**對應功能：** OW-F09

**Given**

- 一個 Work Package 產生大量原始 tool logs、對話與失敗輸出。

**When**

- 編排記憶流程分析本次工作。

**Then**

- 原始事件保留在其短期 retention 範圍。
- 只有經獨立分析、具重複證據與適用條件的編排經驗，才能成為長期記憶候選。
- 不得直接把完整 log 或對話放入未來 Agent prompt。

### OW-S56：Agent crash 但沒有產生新差異

**對應功能：** OW-F10

**Given**

- Test Agent 在讀取 Context 後 crash。
- 相對 baseline 沒有 Agent delta，也沒有 active process。

**When**

- 主 Agent執行復原檢查。

**Then**

- 使用者既有差異保持不變。
- 結果可以是 `safe_to_retry` 或 `repartition_required`。
- 新 writer 使用新 generation，舊 Agent 遲到結果仍被阻擋。

### OW-S57：Agent crash 並留下有用的部分實作

**對應功能：** OW-F10

**Given**

- Implementation Agent 完成部分 rollback 邏輯後 crash。
- diff 可辨識且沒有未完成 process。

**When**

- 主 Agent檢查殘留 candidate。

**Then**

- 保存並描述有用 delta 與未完成事項。
- 不自動刪除部分實作。
- 可以在新 generation 中交由其他 Agent接續，並重新驗證完整規格。
- 部分實作本身不得被誤報為完成。

### OW-S58：相同失敗反覆發生且沒有新證據

**對應功能：** OW-F10

**Given**

- 相同 test failure／tool failure fingerprint 已多次出現。
- 每次嘗試都沒有新增診斷證據。

**When**

- Agent 要求再次執行相同修正與命令。

**Then**

- Attempt Ledger 消耗預算並阻止無限循環。
- 達到規格設定門檻後結果為 `preserve_and_stop` 或結構化人類報告。
- 報告包含已嘗試內容、證據、缺口與可選下一步。

### OW-S59：環境失敗不得誤修產品程式

**對應功能：** OW-F10

**Given**

- pytest 因 dependency missing、錯誤 cwd、permission 或 sandbox 差異而失敗。

**When**

- 主 Agent分類根因。

**Then**

- 結果為 `retry_after_environment_fix`。
- 不得為了繞過環境問題而改變產品語意或放寬測試。
- 環境修復後建立新的 verification invocation。

### OW-S60：外部副作用狀態不確定

**對應功能：** OW-F10

**Given**

- Agent 在未完成回報前觸發可能影響外部資料庫、網路服務或部署狀態的操作。
- 系統無法確認操作是否已生效。

**When**

- 主 Agent進行復原。

**Then**

- 不得盲目重試或執行反向操作。
- 結果為 `human_spec_scope_or_risk_decision`。
- 報告保存已知 invocation、外部狀態缺口與安全查證選項。

### OW-S61：復原操作可能覆寫使用者差異

**對應功能：** OW-F10

**Given**

- 共享工作區同時包含使用者原有 dirty changes 與 Agent 部分 delta。
- 無法可靠分離兩者。

**When**

- 自動復原考慮 reset、restore、stash 或檔案覆寫。

**Then**

- 破壞性復原被阻擋。
- 結果為 `preserve_and_stop` 或人類決策。
- 系統保留現況與差異證據，不為追求乾淨狀態犧牲使用者工作。

### OW-S62：Work Package 取消後保留候選成果

**對應功能：** OW-F10

**Given**

- 人類取消 Work Package。
- 多個 partitions 已有部分 diff 與測試結果。

**When**

- 主 Agent結束執行。

**Then**

- 停止新的 Agent 寫入。
- 保留可識別的候選 diff 與短期證據。
- 不自動整合、刪除、提交或宣告完成。
- 後續是否重用由新的任務規格決定。

### OW-S63：舊 baseline 但修改資源不重疊

**對應功能：** OW-F11

**Given**

- Agent A 從 candidate `C1` 修改 Billing Module。
- 主 Agent在此期間把不相依的 Documentation delta 整合成 `C2`。

**When**

- Agent A 提交基於 `C1` 的 patch。

**Then**

- 系統檢查實際 touched resources 與依賴。
- 若確定不重疊且契約未變，結果為 `non_overlapping_but_revalidation_required`。
- patch 可以重新套用到新 candidate，但必須建立新 identity 並重跑影響驗證。
- Agent A 在 `C1` 上的 PASS 不得直接轉移。

### OW-S64：同一 logical resource 發生衝突

**對應功能：** OW-F11

**Given**

- 兩份 patch 表面修改不同檔案。
- 其中一份修改 generator source，另一份修改其 generated output。

**When**

- 主 Agent進行 freshness 與 conflict check。

**Then**

- 兩者被辨識為同一 logical resource group。
- 結果為 `conflicting_candidate_delta`。
- 不得依檔名不同就自動接受。

### OW-S65：路徑不重疊但依賴契約已變更

**對應功能：** OW-F11

**Given**

- Test Agent 的 patch 只修改 acceptance tests。
- 施工期間 `PathResolutionResult` 從 `v1` 更新為 `v2`。

**When**

- Test Agent提交仍依賴 `v1` 的成果。

**Then**

- 結果為 `stale_dependency_contract`。
- 主 Agent提供最小契約差異並要求刷新 Context。
- 舊 patch 不得直接進入目前 candidate。

### OW-S66：任務規格版本已更新

**對應功能：** OW-F11

**Given**

- Agent 的成果綁定規格 `v3`。
- 人類已確認規格 `v4`。

**When**

- Agent提交舊成果。

**Then**

- 結果為 `stale_specification`。
- `v3` 成果可保留為歷史候選，但不能完成 `v4`。
- 必須依 `v3 → v4` 差異重新判斷可重用範圍。

### OW-S67：舊 generation 遲交看似可套用的 patch

**對應功能：** OW-F11

**Given**

- generation 1 已撤回並由 generation 2 接手。
- generation 1 遲交一份目前看似沒有文字衝突的 patch。

**When**

- Patch Admission 檢查 writer generation。

**Then**

- 結果仍為 `stale_generation`。
- 不得靜默自動套用。
- 主 Agent可以提取其中想法或重新產生新 patch，但必須使用目前 generation 與 candidate 重驗。

### OW-S68：System Map 遺漏實際依賴

**對應功能：** OW-F11

**Given**

- System Map 顯示兩個 Module 不相依。
- live import、schema reference 或 configuration 顯示實際依賴。

**When**

- 主 Agent判斷 patch freshness。

**Then**

- 以 live evidence 擴大 dependency check。
- 不得因 Map 沒有 relation 就自動接受。
- 產生 Map drift／sync 待辦，但該 metadata 不改變本次任務授權。

### OW-S69：重用完全相同 Snapshot 的驗證結果

**對應功能：** OW-F11

**Given**

- verification result 綁定完整 snapshot identity `S1`。

**When**

- 系統再次評估內容完全相同的 `S1`。

**Then**

- 同一次 active execution 中可使用短期機械 cache，前提是 verification subject 完全相同。
- 節點完成並清除執行資料後，不保留歷史 PASS 供未來直接重用。
- 日後即使 source 看似相同，仍重新執行 active pytest 驗證目前狀態。

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

- Implementation Agent 只寫 `src/billing/**`。
- Test Agent 只寫 `tests/acceptance/billing/**`。
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

### OW-S85：直接 Patch 混合合法與非法目標

**對應功能：** OW-F14

**Given**

- Test Agent 的 active partition 只包含 `tests/billing/**`。

**When**

- 一份 patch 同時指向合法測試檔與 `src/workspace/path_normalizer.py`。

**Then**

- Pre-operation admission 拒絕整份操作。
- 結果為 `mutation_blocked_resource`。
- 不得留下只套用部分檔案的 candidate。

### OW-S86：無法預知輸出的 Formatter

**對應功能：** OW-F14

**Given**

- formatter 接收 project root，可能修改分區外檔案。

**When**

- 子代理在 shared workspace 要求執行。

**Then**

- 若 containment 無法限制輸出，結果為 `mutation_requires_isolation`。
- 主 Agent改用隔離 candidate 或序列施工。
- 不能只因 formatter 命令在工具 allowlist 就直接執行。

### OW-S87：透過 Symlink／Junction 越出分區

**對應功能：** OW-F14

**Given**

- 分區內路徑實際指向分區外 target。

**When**

- Agent 透過該 alias 嘗試寫入。

**Then**

- canonical target 被識別為越區。
- 結果為 `mutation_blocked_resource`。
- System Map 或文字路徑名稱不能覆蓋 filesystem 實際結果。

### OW-S88：Agent 偽造 Execution Identity

**對應功能：** OW-F14

**Given**

- Tool request payload 自稱是另一個具有寫入權的 Agent。
- 實際執行通道 identity 不同。

**When**

- Mutation Mediation 判斷請求。

**Then**

- 以可信執行通道 identity 為準。
- 結果為 `mutation_blocked_identity`。
- caller-supplied identity 不得產生權限。

### OW-S89：Mutation Boundary 執行中失效

**對應功能：** OW-F14

**Given**

- shared workspace 的 guard／sandbox 在施工中途無法回應或狀態不確定。

**When**

- Agent 發出新的 mutation。

**Then**

- 結果為 `mutation_boundary_unavailable`。
- 相關 partition freeze 並進入 recovery check。
- 不得自動降級為 prompt-only 繼續施工。

### OW-S90：Precheck 通過但產生間接越區 Delta

**對應功能：** OW-F14

**Given**

- 命令的明示目標位於合法分區。
- hook、plugin 或 generated output 修改其他路徑。

**When**

- Post-operation reconciliation 比較 candidate delta。

**Then**

- 結果為 `mutation_reconciliation_failed`。
- 該操作不得進入受保護 candidate。
- 若共享工作區無法安全回復，保留現況並進入 recovery，而不是破壞性清理。

### OW-S91：Precheck 與落盤之間 Generation 改變

**對應功能：** OW-F14

**Given**

- mutation precheck 時 partition generation 仍 active。
- 真正落盤前，主 Agent已 freeze 並撤回該 generation。

**When**

- 操作嘗試完成。

**Then**

- 原子 boundary 應阻止落盤，或 post-delta 將結果標記為 stale／reconciliation failure。
- 舊 generation 的結果不得影響 integration candidate。
- 不得因 precheck 曾通過就接受遲到 mutation。

### OW-S92：內容相同但非內容 Metadata 不同

**對應功能：** OW-F15

**Given**

- 兩份 snapshot 的檔案內容、relative paths 與必要 mode 完全相同。
- mtime、absolute workspace path 或建立時間不同。

**When**

- 系統計算 source identity。

**Then**

- `source_snapshot_id` 必須相同。
- provenance metadata 可以不同。

### OW-S93：Acceptance Test 內容改變

**對應功能：** OW-F15

**Given**

- 產品程式未改變。
- 一個被納入 candidate 的 acceptance assertion 被修改。

**When**

- 系統重新產生 manifest。

**Then**

- `source_snapshot_id` 必須改變。
- 舊 verification result 不得套用。

### OW-S94：相同 Source 套用不同規格

**對應功能：** OW-F15

**Given**

- source snapshot 完全相同。
- 任務規格從 `v3` 更新為 `v4`。

**When**

- 系統建立 verification subject。

**Then**

- `source_snapshot_id` 保持相同。
- `verification_subject_id` 必須不同。
- `v3` PASS 不能完成 `v4`。

### OW-S95：不同 Generation 回到相同內容

**對應功能：** OW-F15

**Given**

- generation 10 新增一項變更。
- generation 11 完整撤銷該變更，內容回到 generation 9。

**When**

- 系統計算 identity。

**Then**

- generation 9 與 11 的 `source_snapshot_id` 可以相同。
- generation 與 provenance history 仍不同。
- 是否重用舊驗證仍受 verification contract、environment profile 與 retention policy 限制。

### OW-S96：必要 Untracked Fixture 未納入 Manifest

**對應功能：** OW-F15

**Given**

- pytest 依賴一個工作區中的 untracked fixture。
- manifest 未納入或明確分類該檔案。

**When**

- 系統建立 final verification subject。

**Then**

- completeness check 失敗。
- 不得因本機 pytest 偶然 PASS 就宣告 snapshot 可重現。

### OW-S97：跨平台路徑與 Mode 語意

**對應功能：** OW-F15

**Given**

- 同一專案在 case-insensitive Windows 與 case-sensitive filesystem 建立 snapshot。

**When**

- 路徑大小寫碰撞、separator 或 executable mode 會影響執行。

**Then**

- manifest 必須明確反映或拒絕不可攜差異。
- 不得用簡單字串排序掩蓋實際 filesystem 衝突。
- environment profile 必須指出相關平台語意。

### OW-S98：使用者差異與 Agent Delta 的內容相同

**對應功能：** OW-F15

**Given**

- 最終 snapshot 內容固定。
- 其中部分內容來自使用者既有差異，另一部分來自 accepted Agent patches。

**When**

- 系統計算 source identity 與 provenance。

**Then**

- source identity 只反映最終內容。
- provenance 仍正確區分 baseline user changes 與 Agent deltas。
- 不得為了內容 hash 而失去變更來源。

### OW-S99：Manifest 損毀或格式版本未知

**對應功能：** OW-F15

**Given**

- manifest 缺少 entries、digest 不符，或使用未知 format version。

**When**

- 系統嘗試建立或重用 verification subject。

**Then**

- 結果為 invalid／unknown，不得建立 final PASS。
- 必須重新掃描 candidate 或使用相容的版本轉換程序。

### OW-S100：最小初始 Context Envelope

**對應功能：** OW-F16

**Given**

- Test Agent 只負責 `PAY-02` 與 `PAY-03` acceptance。

**When**

- 主 Agent建立初始 Context Envelope。

**Then**

- 包含使用者目標、兩個規格條目、必要契約、相關 symbol index 與 test write zone。
- 不自動載入整個 Billing Domain。
- 所有載入內容與 token estimate 記入 Context Ledger。

### OW-S101：請求額外 Symbol

**對應功能：** OW-F16

**Given**

- Test Agent 無法判斷 rollback 的可觀察錯誤結果。
- 它已檢查目前 Context 中的 `PathResolutionResult` 與 `PathResolutionState`。

**When**

- 它請求 `src/workspace/errors.py::PathResolutionFailure`，並說明預期用途。

**Then**

- Broker 可以回傳 `grant_exact_content` 或 `grant_excerpt`。
- 只載入該 symbol 與必要周邊，不載入整個檔案樹。
- Grant 綁定目前 candidate digest。

### OW-S102：要求整個 Domain

**對應功能：** OW-F16

**Given**

- 子代理沒有指出具體缺少的決策資訊。

**When**

- 它要求載入整個 Billing Domain。

**Then**

- Broker 先回傳 `grant_summary_or_index` 或 `deny_irrelevant_or_duplicate`。
- 要求子代理說明需要回答的問題與已檢查來源。
- 不得直接把整個 Domain 全文塞入 Context。

### OW-S103：Context Budget 耗盡

**對應功能：** OW-F16

**Given**

- 子代理已用完 expansion budget，仍持續要求大量相鄰 Module。

**When**

- 新請求到達。

**Then**

- 結果為 `context_budget_exhausted`。
- 主 Agent選擇摘要、縮小子目標、重新分區或改為序列施工。
- 不得偷偷超額載入後把成本隱藏。

### OW-S104：已載入 Source 在施工中改變

**對應功能：** OW-F16

**Given**

- 子代理 Context 中的契約綁定 candidate `C1`。
- 主 Agent整合共享契約變更形成 `C2`。

**When**

- 子代理繼續使用舊 Context。

**Then**

- 舊 artifact 被標記 stale。
- 主 Agent提供 `C1 → C2` 的最小 Context 增量。
- 舊 Context 產生的成果不得直接通過 freshness admission。

### OW-S105：System Map Index 已漂移

**對應功能：** OW-F16

**Given**

- System Map 指向舊 Module 位置。
- live source 顯示 Entity 已移動或依賴已改變。

**When**

- Broker 解析 content request。

**Then**

- 使用 live source 提供目前內容。
- 產生 Map drift／sync 待辦。
- 不得把 Map metadata 當成舊路徑的讀取或寫入授權。

### OW-S106：Context 縮減不得移除規格

**對應功能：** OW-F16

**Given**

- Context 接近預算上限，需要摘要或移除低優先內容。

**When**

- Broker 執行 Context compaction。

**Then**

- 使用者目標、固定規格、acceptance 與禁止事項保持 pinned。
- 優先移除重複 source、歷史 log 與低相關摘要。
- 壓縮後不得改變 expected behavior。

### OW-S107：敏感資源請求

**對應功能：** OW-F16

**Given**

- 子代理要求讀取 credential 或包含個資的資料。
- 其 ownership 分區並未提供相應安全授權。

**When**

- Broker 判斷請求。

**Then**

- Context grant 不得擴大資料權限。
- 依安全政策拒絕、遮罩或轉入高風險流程。
- 不得因內容可能有助於測試就自動提供。

### OW-S108：存在繞過 Broker 的讀取通道

**對應功能：** OW-F16

**Given**

- 子代理可以直接用不受限制的 filesystem tool 讀取任何檔案。

**When**

- DDH 報告 Context budget 保證。

**Then**

- 必須標記為 orchestration-only／non-mechanical。
- 不得宣稱 Broker 能阻止超額載入。
- 若任務需要硬成本或資料邊界，必須限制工具通道或改用受控執行環境。

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

### OW-S116：第一次驗證失敗

**對應功能：** OW-F18

**Given**

- integration candidate 的 `PAY-03` acceptance 首次失敗。

**When**

- 機械 runner 產生 observed result。

**Then**

- Ledger 記錄 invocation、candidate、scenario id、normalized fingerprint 與受控 artifact reference。
- Agent只收到規格條目、failure summary 與最小相關 Context。
- 狀態可進入自主診斷。

### OW-S117：相同失敗無新進展地重複

**對應功能：** OW-F18

**Given**

- 相同 candidate 關聯、fingerprint 與修正策略已反覆執行。
- 沒有新增 source、environment 或診斷證據。

**When**

- 再次提出相同重試。

**Then**

- no-progress counter 與預算增加。
- 達到 Work Package 門檻後停止自動循環。
- 產生包含已嘗試內容、證據、缺口與下一步的結構化報告。

### OW-S118：相似錯誤但出現新證據

**對應功能：** OW-F18

**Given**

- pytest 仍在同一 scenario 失敗。
- 新 invocation 顯示根因從 environment failure 轉為產品 assertion failure，或 candidate 已有相關修正。

**When**

- Ledger 比較新舊狀態。

**Then**

- 不得只因 test node 相同就誤判成完全無進展。
- 記錄新的 classification／fingerprint 與證據差異。
- 已消耗預算保留，但可以依 policy 繼續診斷。

### OW-S119：節點完成後只留下可重跑測試

**對應功能：** OW-F18

**Given**

- Routine Work Package 已完成且不屬高風險／release。

**When**

- 完成當下的機械 pytest 已對固定 verification subject 通過。

**Then**

- 長期 Evidence Retention 只留下 active pytest、fixture、configuration 與 profile。
- 不永久保存 final PASS、invocation、snapshot report 或 compact Ledger。
- Attempt Ledger 進入等待自進化消化的短期狀態。

### OW-S120：自進化完成後刪除 Attempt Ledger

**對應功能：** OW-F18

**Given**

- Work Package 已結束。
- Evolution Analyzer 已讀取 Ledger，與長期記憶比較並完成接受、拒絕或無新記憶的處理。

**When**

- Ledger 被標記為 consumed。

**Then**

- 原始 Attempt Ledger 與一般執行 logs 被刪除。
- 長期記憶只保留經處理後的經驗資料，不包含完整 Ledger。
- pytest 資產不因 Ledger 刪除而消失。

### OW-S121：自進化尚未完成

**對應功能：** OW-F18

**Given**

- Work Package 已結束，但 Evolution Analyzer 尚未成功處理 Ledger。

**When**

- 清理程序執行。

**Then**

- Ledger 暫時保持 pending，不得假裝已整合後刪除。
- 何時重試、最長等待與無法處理時的政策留待後續確認。
- pending Ledger 仍不是長期 Evidence Retention。

### OW-S122：完成後查詢歷史 PASS

**對應功能：** OW-F18

**Given**

- 節點已完成且舊 Ledger／logs 已刪除。

**When**

- 使用者或新任務需要確認功能目前是否正常。

**Then**

- 系統重新執行 active、未 stale 的 pytest。
- 不得虛構或宣稱仍持有當時的歷史 PASS 證據。
- 新結果只證明目前 verification subject 的狀態。

### OW-S123：原始事件不能直接成為長期記憶

**對應功能：** OW-F18

**Given**

- 多個 Work Packages 產生大量相似失敗 logs。

**When**

- 編排記憶流程要建立長期經驗。

**Then**

- 必須先由獨立分析流程確認重複模式、適用條件、證據與失效條件。
- 不得直接複製 Ledger、prompt 或完整對話到未來 Agent Context。

### OW-S124：取消任務的 Ledger 仍進入消化流程

**對應功能：** OW-F18

**Given**

- Work Package 被取消，已有部分 patch 與測試結果。

**When**

- 系統結束本次執行。

**Then**

- 不自動整合或提交候選成果。
- Attempt Ledger 可作為「切分錯誤、成本浪費或取消原因」的自進化原料。
- 消化完成後刪除 Ledger 與一般 logs。
- 後續是否重用 patch 由新的任務規格與 workspace 狀態決定，不由 Ledger 提供授權。

### OW-S125：一次成功的最小 Ledger

**對應功能：** OW-F18.1

**Given**

- 單一 partition 第一次實作後即通過 pytest。

**When**

- Work Package 完成。

**Then**

- Ledger 只有一份 Work Package Summary、一份 Partition Summary 與一筆 Attempt Row。
- 不因中間有多次正常 read／write tool calls 而產生大量事件列。
- Evolution Analyzer 仍能辨識「單 Agent、低 Context、首次成功」的派工結果。

### OW-S126：一次 Attempt 內包含多個 Tool Calls

**對應功能：** OW-F18.1

**Given**

- Agent 在一次 repair attempt 中讀取數個 symbols、修改三個檔案並執行 formatter。

**When**

- 最後執行一組機械 pytest。

**Then**

- Ledger 建立一筆 repair Attempt Row。
- tool 細節只存在短期執行資料，不逐筆複製進 Ledger。
- Row 記錄 input／output candidate、suite、outcome、成本與必要 coordination summary。

### OW-S127：失敗後修正形成兩個 Attempts

**對應功能：** OW-F18.1

**Given**

- Attempt 1 產生 `PAY-03` failure fingerprint。
- Agent 根據新證據修正後執行 Attempt 2 並通過。

**When**

- Ledger 關閉。

**Then**

- 兩筆 rows 各自保留 candidate、outcome、fingerprint／new evidence 與 cost delta。
- Evolution Analyzer 能比較修正是否有效，不需要完整 Agent 對話。

### OW-S128：比較兩種派工的 Context 成本

**對應功能：** OW-F18.1

**Given**

- 多個相似 Work Packages 使用不同 Context template 或 parallelization result。

**When**

- Evolution Analyzer 比較 Ledger。

**Then**

- 可由 agent profile、template version、initial context、expansion summary、成本與 outcome 分析派工效果。
- 不需要保存 Context 全文。

### OW-S129：Ledger 欄位寫錯後修正

**對應功能：** OW-F18.1

**Given**

- 一筆 closed Attempt Row 的 environment failure 被錯誤分類為 product failure。

**When**

- 機械檢查發現分類錯誤。

**Then**

- 不靜默覆寫原始 closed row。
- 以 correction 欄位或新 correction row 指出舊值、新值與理由。
- Evolution Analyzer 使用修正後投影。

### OW-S130：消化後完整刪除 Ledger

**對應功能：** OW-F18.1

**Given**

- Evolution Analyzer 已讀取三段式 Ledger 並完成長期記憶比較。

**When**

- Ledger 標記 consumed。

**Then**

- Work Package Summary、Partition Summaries、Attempt Rows 與一般 logs 一起刪除。
- 不留下 compact Ledger shadow copy。
- 已接受的長期記憶與 pytest 資產維持獨立。

### OW-S131：成功 pytest 產生大量輸出

**對應功能：** OW-F18.2

**Given**

- P1 suite 全部通過，但產生大量 stdout。

**When**

- runner 完成 Attempt Row。

**Then**

- Ledger 只記錄 suite ids、PASS、duration 與成本。
- Agent Context 只收到有界成功摘要。
- 原始輸出不成為 Evidence Retention。

### OW-S132：失敗 pytest 提供最小診斷片段

**對應功能：** OW-F18.2

**Given**

- `PAY-03` 失敗並產生長 stack trace。

**When**

- Agent 進入自主診斷。

**Then**

- 只提供規格條目、test id、fingerprint、assertion／exception location 與必要 stack excerpt。
- 完整 log 暫時留在有界 buffer，不自動載入 Context。

### OW-S133：相同失敗反覆輸出相同 Log

**對應功能：** OW-F18.2

**Given**

- 多次 Attempts 產生相同 failure fingerprint 與幾乎相同 log。

**When**

- Agent 再次取得診斷 Context。

**Then**

- 不重複注入相同完整 excerpt。
- 只提供 repeat count、成本與新增差異。
- Attempt Ledger 仍能判定 no-progress。

### OW-S134：Log 含敏感資訊

**對應功能：** OW-F18.2

**Given**

- stderr 含 credential 或個資。

**When**

- 系統建立短期 buffer 與 failure excerpt。

**Then**

- 一般 buffer／Context 使用遮罩內容。
- Ledger 不保存原始秘密。
- 無法安全處理時停止輸出傳遞並轉入安全例外流程。

### OW-S135：輸出超過 Buffer 上限

**對應功能：** OW-F18.2

**Given**

- Tool 產生超過 profile 上限的 stdout／stderr。

**When**

- Buffer 截斷輸出。

**Then**

- `truncated: true`。
- exit、timeout、test id 與 failure classification 保持可用。
- FAIL 不得因缺少完整尾端輸出變成 PASS。

### OW-S136：Process Timeout 仍保留必要片段

**對應功能：** OW-F18.2

**Given**

- pytest／tool 在 timeout 前持續輸出。

**When**

- runner 終止 process。

**Then**

- outcome 為 timeout。
- 有界頭尾片段、已知 test id 與 partial structured result 可供診斷。
- Agent 不得把 timeout 自行解讀成產品 test failure。

### OW-S137：Evolution Analyzer 要求額外 Failure Excerpt

**對應功能：** OW-F18.2

**Given**

- Ledger 顯示多個 Work Packages 反覆發生相似 Context／派工失敗。
- 原始 log 尚在短期 buffer。

**When**

- Analyzer／Critic 需要區分兩個可能模式。

**Then**

- 只能請求有理由、最小、遮罩且有 budget 的 excerpt。
- 請求結果用於當次分析，不複製進長期記憶。
- Log 已刪除時，誠實標記 unavailable，不重新虛構。

### OW-S138：Log Buffer Crash Recovery

**對應功能：** OW-F18.2

**Given**

- Runner 在完成 Attempt Row 前 crash。

**When**

- 主 Agent進行 recovery。

**Then**

- 若短期 buffer 可用，提取 exit／partial output 形成 crash fingerprint。
- 若不可用，標記 evidence unavailable。
- 不因缺少 log 而編造分類或破壞 candidate。

### OW-S139：例行首次成功不啟動模型分析

**對應功能：** OW-F18.3

**Given**

- Module 任務使用既有模板首次成功。
- 沒有 Context expansion、handoff、conflict、recovery 或成本異常。

**When**

- Ledger seal 後執行 mechanical prefilter。

**Then**

- 結果為 `routine_no_orchestration_signal`。
- 不呼叫 Analyzer／Critic。
- Ledger 標記 consumed 並刪除。

### OW-S140：已知模式只更新支持摘要

**對應功能：** OW-F18.3

**Given**

- Ledger 特徵符合仍有效的既有長期記憶。
- 本次沒有新衝突或失效證據。

**When**

- Mechanical Prefilter 比對。

**Then**

- 結果為 `known_pattern_no_change`。
- 只更新該記憶的機械支持計數／最近觀察摘要。
- 不啟動模型分析，Ledger consumed 後刪除。

### OW-S141：重複 Context 膨脹觸發批次分析

**對應功能：** OW-F18.3

**Given**

- 多個相似 Subsystem partitions 使用同一 Context template。
- 都發生大量 expansion、budget exhaustion 或改為序列施工。

**When**

- 相似候選達到 Evolution Profile 的批次觸發條件。

**Then**

- 相關 Ledger features 批次送入 Analyzer。
- Analyzer 產生 Context template 改善候選。
- Critic 驗證前不得直接修改正式模板。

### OW-S142：嚴重編排失敗優先分析

**對應功能：** OW-F18.3

**Given**

- 發生 repeated no-progress、stale patch 污染嘗試或 unsafe recovery 問題。

**When**

- Terminal prefilter 分類為 `critical_orchestration_failure`。

**Then**

- 不等待一般 batch 數量，優先送 Analyzer／Critic。
- 原 Ledger 在決策完成前保持 pending。

### OW-S143：一次性產品 Bug 不進入自進化

**對應功能：** OW-F18.3

**Given**

- Agent 正常找到並修正一次性 calculation bug。
- 派工、Context、ownership 與成本沒有異常。

**When**

- Prefilter 檢查 Ledger。

**Then**

- 不因存在 test failure 就啟動編排自進化。
- 結果為 `routine_no_orchestration_signal`。
- 產品知識不被錯誤寫入編排長期記憶。

### OW-S144：Critic 拒絕 Memory Candidate

**對應功能：** OW-F18.3

**Given**

- Analyzer 認為應修改派工模板。
- Critic replay 顯示改善不穩定或成本更高。

**When**

- Critic 回傳 rejected。

**Then**

- 正式模板不變。
- 可以保存有期限的 suppression summary，避免相同候選立即重複分析。
- 原始 Ledgers 標記 consumed 並刪除。

### OW-S145：Analyzer 暫時失敗

**對應功能：** OW-F18.3

**Given**

- Ledger 已被選入分析。
- Analyzer／Critic 因模型、預算或系統錯誤未完成。

**When**

- 清理程序執行。

**Then**

- Ledger 保持 pending，不標記 consumed。
- 不刪除原始 Ledger。
- 依 Evolution Profile 安排重試或降級處理。

### OW-S146：正式模板變更前的 Evolution Gate

**對應功能：** OW-F18.3

**Given**

- 系統準備更新 Context Envelope 或角色 prompt template。
- 存在與該模板相關的 pending memory candidates。

**When**

- 進入模板變更流程。

**Then**

- 先分析相關候選並由 Critic 驗證。
- 未完成驗證的候選不能直接修改正式模板。
- 模板變更仍不得修改規格、權限、驗收或人工升級條件。

---

## 5. 邊界驗收

至少需要覆蓋：

1. Windows 大小寫不敏感路徑。
2. `..`、相對路徑與 canonical path。
3. symlink／junction 指向分區外。
4. 新增未追蹤檔案。
5. rename 或 move 從分區內移到分區外。
6. 一次操作同時修改多個檔案，部分在分區外。
7. generated files 與 formatter 產生的跨區修改。
8. 共用設定、root fixture 與測試收集設定。
9. 分區在寫入檢查後、真正落盤前被撤回的競態。
10. 相同 Agent 的舊 execution identity 重送寫入。

對無法提供原子檢查與寫入的工具，不得宣稱完全防止競態；必須使用隔離工作區、序列化或事後 delta 阻擋作為替代。

---

## 6. 壓力與併發驗收候選

以下數值是用來討論的第一版 profile，不是已核准門檻。

### OW-P01：同一資源競爭

- 100 個並行分配請求競爭同一共享資源。
- 任一時刻最多只能有一個 active writer。
- 不得出現雙重成功。

### OW-P02：平行寫入判定

- 8 個 Agent。
- 每個 Agent 對其分區內、外各提出 1,000 次寫入判定。
- 分區外 false allow 必須為 0。
- 分區內合法寫入不得因其他不重疊 writer 而被錯誤阻擋。

### OW-P03：路徑繞過

- 對相對路徑、大小寫變形、junction、rename 與 path traversal 建立至少 1,000 組混合案例。
- 越界寫入不得因路徑表示不同而通過。

### OW-P04：反覆失聯與移交

- 連續執行 100 次 writer crash／recovery／reassignment。
- 每次移交均須保留原候選 diff。
- 不得存在 owner overlap。
- 不得把 crash 前殘留變更歸給新 writer。

### OW-P05：整合凍結競態

- 8 個 writer 同時完成或仍嘗試寫入時，觸發 integration freeze。
- freeze 完成後不得再有成功寫入。
- 相同 snapshot 重複計算 identity 必須一致。
- freeze 前未完成的操作必須有明確成功或失敗結果，不得處於未知狀態。

### OW-P06：大型工作區

- 在至少 100,000 個受索引路徑、10,000 個本次變更路徑的候選工作區執行分區解析與 delta 檢查。
- 不得因規模而跳過越界檢查。
- 延遲門檻必須在選定實作環境完成 baseline 後再固定；目前不憑空指定毫秒數。

### OW-P07：Candidate 快速變動與遲到成果

- 主 Agent連續整合多個互不重疊的 patch，建立多個 candidate generation。
- 其他 Agent從不同舊 baseline 陸續回傳成果。
- 系統必須正確區分可安全套用、需要刷新／重驗與必須拒絕。
- 舊 generation 的成果不得覆蓋較新的 writer 成果。
- 不得把舊 candidate 的 PASS 快取套用到新的整合 candidate。

### OW-P08：Acceptance 保護的對抗測試

OW-F04 的重點不是一般吞吐量，而是驗收期待能否承受反覆的弱化嘗試。

- 對受保護 acceptance 產生刪除案例、加入 skip／xfail、放寬 assertion、降低門檻與縮小 fixture 等變更。
- 所有未引用規格變更的弱化操作都不得被分類為一般 test implementation fix。
- false allow 必須為 0。
- 測試數量應覆蓋支援的弱化類型與語言／pytest profile，不先把任意固定次數寫成業務真理。

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

### OW-P14：Freeze 與多檔案操作競態

- 在多個 writer 執行 formatter、generator、rename 或批次 patch 時反覆觸發 freeze。
- 每次操作必須得到明確成功、失敗、終止或 unknown 結果。
- unknown 狀態不得被自動重派。
- freeze 完成後不得再有舊 generation 成功影響受保護 candidate。

### OW-P15：大量 Candidate 與結果綁定

- 連續建立大量只差少量內容的 integration candidates。
- 每個內容不同的 candidate 必須具有不同 identity。
- 相同內容重複計算必須得到相同 identity。
- 驗證快取或歷史 PASS 不得錯綁到其他 candidate。
- 具體數量依預期同時進行的 Work Package 與 CI 規模固定。

### OW-P16：長時間驗證期間持續產生新 Candidate

- 在舊 snapshot 執行長時間壓力測試時，主 Agent持續整合後續變更形成新 candidates。
- 舊執行只能更新其綁定 snapshot 的結果。
- 新 candidate 不得繼承舊測試的 final PASS。
- 不得因 candidate churn 中止或覆寫仍有診斷價值的舊結果。

### OW-P17：高輸出與大量正常事件

- 產生大量合法寫入事件與超過輸出上限的 pytest stdout／stderr。
- 系統必須保持 event correlation、touched-resource summary、exit status 與 failure classification。
- 超額輸出必須截斷並明確標記，不得導致記憶體或 context 無界成長。
- 聚合後仍不得漏掉任何越區或 protected-resource 事件。

### OW-P18：多 Agent 事件關聯

- 多個 Agent 同時提交 Context request、寫入、patch、handoff 與 verification events。
- 每個事件都必須正確綁定 Work Package、partition、generation、candidate 與 invocation。
- 事件到達順序不同時，不得把舊 generation 的 PASS 或 patch 歸給目前 candidate。
- 不要求建立全域永久總排序，但每個完成判定的因果關係必須可重建。

### OW-P19：Crash／timeout storm

- 多個 Agent 在取得分區後隨機 crash、timeout、失聯或留下部分 delta。
- 系統最終必須恢復可施工狀態，不留下永久 active partition。
- unknown execution state 不得被危險地自動清理或重派。
- 遲到 patch 不得污染新 generation。
- 所有可辨識的使用者原有差異與有用 Agent delta 都必須保留。

### OW-P20：重複失敗與預算耗盡

- 產生大量相同及不同 failure fingerprints。
- 相同 fingerprint 且無新增證據的重試必須受 attempt budget 限制。
- 新 fingerprint 或新增診斷證據不能被錯誤當成相同無進展循環。
- 預算耗盡後必須產生一次結構化停止結果，而不是繼續重試或遺失候選成果。

### OW-P21：Candidate churn 下的 freshness 分類

- 主 Agent快速產生多個 candidates，子代理從不同舊 baseline 亂序回傳 patch。
- 系統必須正確分類不重疊但需重驗、stale generation、stale specification、stale dependency 與直接衝突。
- 不得把所有舊 base 一律接受，也不得把所有可安全重用成果一律丟棄。
- 任一自動接受的成果都必須產生目前 candidate identity。

### OW-P22：大型依賴圖的間接 stale 偵測

- 建立大量直接與間接契約依賴，混入 System Map 遺漏或過期 relation。
- 變更底層契約後，所有實際受影響成果都必須被標記需要刷新。
- 不相依成果不得被無理由全部失效。
- 具體 Entity 與 relation 數量需依新版 System Map 的目標專案規模固定。

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

### OW-P27：Mutation Admission 高競爭

- 多個 execution identities 同時對合法、非法、shared 與 stale resources 發出 mutation。
- 任一 mutation 都必須取得唯一、可追溯且符合當下 generation 的結果。
- false allow 必須為 0。
- 不相依合法分區不得因全域鎖而全部串行。

### OW-P28：Identity、Path 與 TOCTOU 對抗

- 組合偽造 caller identity、大小寫、Unicode normalization、separator、`..`、symlink／junction、rename 與 generation race。
- 所有實際越區或 stale mutation 都不得進入受保護 candidate。
- boundary 無法確定結果時必須 fail closed，並保留 recovery evidence。

### OW-P29：大型 Snapshot Manifest

- 對目標規模的大型專案建立完整與增量 manifest。
- 相同內容重複計算 identity 必須一致。
- 新增、修改、刪除、rename、untracked 與 generated resource 都必須正確反映。
- 不得因規模跳過 completeness 或 collision/canonicalization 檢查。
- 時間與記憶體門檻在 reference environment baseline 後固定。

### OW-P30：大量 Generation 與 Verification Subject

- 快速建立大量 generations，包含內容變更、撤銷回原內容、規格升版與 environment profile 改變。
- generation 必須保持時序可追溯。
- source identity 只隨內容變化。
- verification subject 必須隨 source、specification、verification contract 或 environment profile 變化。
- Result cache 不得錯綁。

### OW-P31：Context Request Storm

- 多個子代理同時進行 discovery 與 content requests，混合重複、無關、stale 與合法請求。
- 同一 artifact 不得重複注入全文或重複計費。
- 每個 grant 必須正確綁定 partition、candidate 與 Context Ledger。
- Budget 耗盡後不得繼續無界載入。

### OW-P32：大型 System Map 與依賴 Traversal

- 在目標規模的 Entity／relation index 上進行大量查詢。
- discovery 結果必須有數量、深度與 token 上限。
- 只因圖上存在大量鄰接節點，不得自動載入所有 source。
- Map drift 與 live verification 不得造成無界 recursive context expansion。

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

### OW-P35：大量 Attempt 的自進化消化

- 多個 Work Packages 產生大量成功、失敗、重試與 Context events。
- Ledger 大小必須受 profile 限制，raw output 透過 artifact references 分離。
- 重複 fingerprint 能機械聚合，但不得合併實際不同的 candidate／environment failure。
- Evolution Analyzer 必須能批次比較既有長期記憶，產生接受、拒絕或無新記憶結果。
- 被標記 consumed 的 Ledger 必須能安全刪除，不留下完整複本。

### OW-P36：Ledger 消化與刪除競態

- 在大量 active、completed、cancelled 與 processing Ledgers 中同時執行分析與清理。
- 只有已完成消化處理的 Ledger 可以刪除。
- active 或仍在 processing 的 Ledger 不得被誤刪。
- 刪除 Ledger 不得刪除 active pytest 資產、產品程式或使用者工作區差異。
- 清理結果只需機械可確認，不建立 legacy 式永久 deletion receipt chain。

### OW-P37：大量 Tool Calls 不造成 Ledger 線性膨脹

- 在少量 Attempts 中執行大量正常 read／write／format tool calls。
- Ledger row 數量應隨 Attempts 與 partitions 成長，不隨每個 tool call 線性成長。
- 仍須保留 observed verification、coordination exceptions、成本與停止判定所需資訊。

### OW-P38：大量 Ledgers 的自進化特徵比較

- Evolution Analyzer 比較大量不同 scope、agent profile、Context template 與 outcome 的三段式 Ledgers。
- 不載入完整 prompt、source、diff 或 logs，仍能找出重複的派工／Context／平行化問題。
- 分析完成後，consumed Ledgers 可完整刪除。

### OW-P39：Log Storm 與固定記憶體上限

- 多個 processes 同時產生超量 stdout、stderr 與重複 failure traces。
- 每個 invocation 與整體 Work Package 都必須遵守 buffer profile。
- 記憶體、disk 與 Agent Context 使用量不得隨原始輸出無界增長。
- Exit、timeout、fingerprint 與截斷狀態仍保持正確。

### OW-P40：重複、敏感與截斷輸出組合

- 混合大量重複行、敏感值、長 stack、binary output 與 timeout。
- 重複內容被聚合、敏感內容被遮罩、超額內容被截斷。
- 不得漏洩秘密，也不得因處理輸出而改變 PASS／FAIL／timeout 的機械結果。

### OW-P41：大量 Terminal Ledgers 的機械 Prefilter

- 大量 completed、stopped 與 cancelled Ledgers 同時 seal。
- Prefilter 在不呼叫模型的情況完成分類、已知記憶比對與 candidate grouping。
- Routine／known cases 不得產生 Agent token cost。
- 只有選定候選進入有 budget 的 Analyzer queue。

### OW-P42：Analyzer Backlog 與刪除安全

- 混合 routine、critical、batch candidates 與 analyzer failures 形成 backlog。
- consumed Ledgers 可以刪除；pending／processing Ledgers 不得誤刪。
- Critical candidates 優先但不能造成低優先候選永久無界累積。
- Backlog、token、storage 與最長等待必須受 Evolution Profile 控制。

---

## 7. 由規格反推的必要能力

只有在上述功能與場景成立後，才能推出以下候選元件：

| 反推出的能力 | 來源需求 |
|---|---|
| Parallelization Decision | OW-F01 |
| Write Zone Model | OW-F02、OW-F05 |
| Canonical Path Resolver | OW-F03、邊界 1～5 |
| Agent-aware Write Guard | OW-F03、OW-S02、OW-S03 |
| Immutable Specification Reference | OW-F04、OW-F08 |
| Cross-zone Change Request | OW-F06 |
| Freeze／Reassign Coordinator | OW-F07、OW-S05、OW-S06 |
| Integration Snapshot Coordinator | OW-F08、OW-S07 |
| Baseline／Delta Recorder | OW-F09、OW-S09 |
| Recovery Inspector | OW-F10 |
| Verification Invocation Recorder | OW-F09 |
| Ephemeral Attempt Ledger | OW-F18 |
| Evolution Intake／Consumption Marker | OW-F18 |
| Candidate Identity／Generation | OW-F11、OW-S10 |
| Patch Admission／Stale-result Guard | OW-F11、OW-P07 |
| Central Integration Coordinator | OW-F12、OW-S11 |

目前不能單憑需求推出：

- 必須使用資料庫。
- 必須使用檔案鎖。
- 必須有中央網路服務。
- 必須用 TTL 自動釋放。
- 每個檔案都要建立 ownership record。
- 單一 Agent 也要建立 ownership。
- 所有任務都要使用獨立 worktree。

這些都屬於後續實作方案，而不是業務需求。

---

## 8. 建議 pytest 投影

以下名稱僅示範規格如何投影成測試：

```text
test_parallel_implementation_and_acceptance_test_writers_integrate
test_implementation_writer_cannot_modify_acceptance_tests
test_test_writer_cannot_modify_product_source
test_shared_contract_change_requires_escalation
test_reassignment_preserves_previous_writer_delta
test_agent_crash_does_not_auto_transfer_write_zone
test_provisional_pass_cannot_complete_work_package
test_integration_snapshot_rejects_post_freeze_write
test_preexisting_user_diff_is_not_attributed_to_agent
test_windows_path_alias_cannot_bypass_write_zone
test_rename_from_owned_to_unowned_path_is_blocked
test_late_patch_from_old_generation_is_not_silently_applied
test_individual_passes_do_not_replace_integrated_candidate_verification
test_write_inside_active_partition_is_allowed
test_patch_mixing_allowed_and_forbidden_paths_is_rejected_as_a_whole
test_formatter_indirect_changes_are_checked_against_partition
test_parallel_execution_is_unsafe_without_mechanical_write_boundary
test_implementation_writer_cannot_change_acceptance_expectation
test_test_implementation_defect_can_be_fixed_without_changing_expected_behavior
test_ambiguous_specification_stops_only_the_divergent_work
test_implementation_writer_can_add_unit_tests_inside_its_partition
test_skip_xfail_or_weakened_threshold_cannot_manufacture_acceptance
test_unapproved_public_contract_change_requires_escalation
test_shared_fixture_is_modified_by_only_one_writer
test_generator_and_outputs_are_one_logical_resource_group
test_parallel_dependency_changes_serialize_lockfile_update
test_shared_contract_update_invalidates_dependent_partitions
test_unrelated_partition_is_not_blocked_by_shared_resource_update
test_product_defect_request_is_routed_to_implementation_writer
test_fixture_can_be_repartitioned_only_after_freeze
test_out_of_scope_change_request_requires_rejection_or_human_decision
test_cyclic_cross_partition_requests_fall_back_to_serial_execution
test_pending_change_request_does_not_grant_write_access
test_repeated_cross_partition_requests_trigger_parallelization_reassessment
test_normal_handoff_preserves_delta_and_uses_new_generation
test_unresponsive_writer_with_unknown_operation_requires_recovery
test_handoff_without_agent_delta_preserves_user_changes
test_freeze_during_multi_file_operation_does_not_expose_partial_candidate
test_handoff_preserves_preexisting_user_diff
test_late_write_after_handoff_is_blocked_as_stale_generation
test_cancelled_partition_preserves_evidence_without_claiming_completion
test_integrated_snapshot_binds_spec_source_tests_and_configuration
test_final_snapshot_cannot_be_created_with_active_writer
test_post_snapshot_change_creates_new_candidate_identity
test_verification_that_mutates_candidate_cannot_report_final_pass
test_snapshot_manifest_preserves_preexisting_user_diff
test_individual_agent_passes_do_not_complete_failed_integration
test_untracked_or_generated_dependency_must_be_in_snapshot_manifest
test_new_specification_version_invalidates_old_completion_result
test_observed_verification_evidence_can_generate_completion_report
test_agent_pass_claim_without_invocation_is_unverified
test_test_failure_timeout_crash_and_environment_failure_are_distinct
test_sensitive_output_is_redacted_without_losing_failure_classification
test_successful_writes_are_aggregated_without_hiding_out_of_scope_changes
test_missing_evidence_store_blocks_completion_but_allows_provisional_diagnosis
test_observed_result_wins_when_agent_claim_conflicts
test_raw_events_are_not_directly_promoted_to_long_term_memory
test_agent_crash_without_delta_can_be_safely_retried
test_partial_useful_delta_is_preserved_after_agent_crash
test_repeated_failure_without_new_evidence_consumes_attempt_budget
test_environment_failure_does_not_trigger_product_semantic_change
test_uncertain_external_side_effect_requires_human_decision
test_recovery_cannot_overwrite_preexisting_user_changes
test_cancelled_work_package_preserves_candidate_without_integrating_it
test_non_overlapping_old_base_patch_requires_revalidation
test_generator_source_and_output_are_detected_as_conflicting_resource
test_dependency_contract_change_marks_non_overlapping_patch_stale
test_new_specification_version_rejects_old_completion_candidate
test_late_patch_from_revoked_generation_is_not_auto_applied
test_live_dependency_evidence_overrides_missing_system_map_relation
test_verification_result_is_reused_only_for_identical_snapshot
test_main_agent_integrates_implementation_and_acceptance_patches
test_acceptance_red_before_implementation_is_valid_provisional_evidence
test_individually_valid_patches_can_require_subsystem_rework_after_conflict
test_main_agent_glue_change_is_attributed_and_revalidated
test_subagent_cannot_mark_work_package_completed
test_patch_order_dependency_requires_integration_rework
test_rejected_patch_is_preserved_without_entering_candidate
test_scope_expansion_discovered_during_integration_requires_human_decision
test_disjoint_writers_can_use_mechanically_guarded_shared_workspace
test_wide_formatter_or_generator_uses_isolated_candidate
test_filesystem_isolation_does_not_make_shared_contract_parallel_safe
test_isolated_candidate_includes_required_dirty_baseline
test_expensive_isolation_can_fall_back_to_serial_execution
test_external_side_effects_require_separate_high_risk_flow
test_parallel_writes_are_rejected_without_guard_or_isolation
test_multi_target_patch_is_rejected_when_any_target_is_outside_partition
test_unbounded_formatter_requires_isolated_candidate
test_symlink_or_junction_cannot_escape_write_partition
test_caller_supplied_agent_identity_cannot_grant_mutation
test_mutation_boundary_failure_freezes_partition
test_post_operation_delta_detects_indirect_out_of_partition_change
test_generation_change_between_precheck_and_write_blocks_candidate_admission
test_non_content_metadata_does_not_change_source_snapshot_identity
test_acceptance_test_change_changes_source_snapshot_identity
test_same_source_under_new_specification_has_new_verification_subject
test_later_generation_can_return_to_same_source_content_identity
test_required_untracked_fixture_must_be_in_snapshot_manifest
test_cross_platform_path_and_mode_semantics_are_explicit
test_content_identity_and_provenance_are_stored_separately
test_corrupt_or_unknown_manifest_cannot_create_final_verification_subject
test_initial_context_envelope_contains_only_required_spec_contracts_and_index
test_context_request_grants_exact_symbol_or_excerpt
test_whole_domain_request_returns_index_before_full_content
test_context_budget_exhaustion_requires_repartition_or_stop
test_changed_source_marks_loaded_context_stale
test_live_source_corrects_stale_system_map_discovery
test_context_compaction_preserves_specification_and_acceptance
test_context_grant_does_not_expand_sensitive_data_access
test_unbrokered_filesystem_read_is_not_reported_as_mechanical_context_control
test_ci_can_run_verification_manifest_without_agent_service
test_same_verification_subject_reuses_identical_selection_thresholds_and_seeds
test_agent_cannot_weaken_frozen_verification_manifest
test_randomized_failure_can_be_replayed_without_agent_context
test_successful_suite_output_is_stored_without_loading_full_log_into_agent
test_agent_diagnosis_is_optional_after_mechanical_failure
test_active_test_asset_is_reused_without_regeneration
test_first_failure_records_mechanical_fingerprint_and_bounded_artifact
test_repeated_failure_without_new_evidence_stops_at_attempt_budget
test_new_failure_evidence_is_not_collapsed_into_no_progress_repeat
test_node_completion_retains_rerunnable_pytest_assets_only
test_consumed_attempt_ledger_is_deleted_after_evolution_processing
test_pending_evolution_ledger_is_not_deleted_before_processing
test_historical_function_status_is_checked_by_rerunning_active_pytest
test_raw_attempt_events_require_independent_analysis_before_memory_promotion
test_cancelled_attempt_ledger_is_consumed_then_deleted
test_first_attempt_success_creates_one_minimal_attempt_row
test_many_tool_calls_inside_one_attempt_do_not_create_event_rows
test_failure_then_repair_creates_comparable_attempt_rows
test_evolution_can_compare_context_cost_without_context_content
test_closed_attempt_correction_preserves_original_fact
test_consumed_three_part_ledger_is_deleted_without_shadow_copy
test_large_success_output_produces_bounded_summary_only
test_failure_context_contains_minimal_diagnostic_excerpt
test_repeated_failure_log_is_not_reinjected_into_agent_context
test_sensitive_log_content_is_redacted_before_buffer_and_context
test_truncated_output_preserves_failure_outcome
test_timeout_preserves_bounded_partial_diagnostics
test_evolution_requests_only_minimal_redacted_failure_excerpt
test_missing_crash_log_is_reported_without_fabricated_classification
test_routine_success_is_consumed_without_model_analysis
test_known_memory_pattern_updates_support_without_model_call
test_repeated_context_expansion_triggers_batched_evolution_analysis
test_critical_orchestration_failure_bypasses_normal_batch_wait
test_one_off_product_bug_does_not_enter_orchestration_memory
test_rejected_memory_candidate_consumes_ledger_without_template_change
test_failed_analyzer_keeps_ledger_pending
test_template_change_waits_for_critic_decision
```

pytest 是本專案目前討論的測試投影；規格本身描述可觀察行為，不應依賴 pytest 語法才能成立。

---

## 9. 確認狀態與剩餘設計

### 已確認

- 採「平行施工分區與整合 Subsystem」定位。
- OW-F01～OW-F18 功能方向。
- 使用者逐項確認的正常、拒絕、邊界、故障與壓力測試類型。
- Implementation Agent 與 Test Agent 不得交叉修改對方主要產物。
- 共享資源由主 Agent集中控制分配。
- provisional feedback 與 final integration verification 必須分開。
- 越區修改不得進入受保護 candidate；prompt 約束不能冒充機械強制。
- Candidate generation、stale result protection 與中央 Patch Admission。
- System Map 提供寬搜尋 index；Context Envelope 採窄載入與按需擴充。
- Subsystem 級完成判準。

### 已確認的 Subsystem 完成判準

只有同時符合下列條件，才能標記：

```text
parallel_work_partitioning_subsystem_implementation_verified
```

1. OW-F01～OW-F18 均有實際功能實現。
2. 每項功能對應的正常、拒絕、邊界與故障測試，都在同一固定 integration snapshot 通過。
3. 所選環境 profile 的併發、競態與壓力測試通過。
4. 越區修改確實被機械阻擋或隔離於 candidate 外，不能只靠 prompt。
5. Implementation Agent 無法改寫獨立 acceptance，Test Agent 無法修改產品實作。
6. stale generation、舊規格、舊契約與遲到 patch 無法污染目前 candidate。
7. crash、timeout、證據故障及使用者 dirty changes 場景能保留成果並安全停止。
8. `spec → scenario → pytest → invocation → snapshot result` 追溯完整。
9. 不適用的測試必須有具體理由，不能只標記跳過。
10. 如果實作改變真實架構，System Map 已依 live project 同步；Map 本身不參與功能 PASS 判定。

此狀態不自動代表：

- DDH 已完成整合。
- Domain 已驗收。
- release candidate 已成立。
- production 已部署。

### 已確認的壓力測試 Profile

| Profile | 用途 | 執行時機 |
|---|---|---|
| P0 功能與基本競態 | 兩個 writer 的基本分區、阻擋、freeze、handoff 與 stale generation | 每次 ownership Subsystem 功能修改 |
| P1 Subsystem 完整驗收 | 最高 8 個 partitions、大型路徑／delta、反覆移交與全部功能場景 | 判定 Subsystem implementation verified |
| P2 高競爭與對抗 | 32 個模擬 workers、亂序／遲到 patch、路徑繞過與驗收弱化 | concurrency、安全邊界或 release candidate |
| P3 Soak 與故障風暴 | 長時間 candidate churn、隨機 crash／timeout／evidence failure | 重大版本或 Recovery 核心修改 |

Profile 是可選驗證強度，不是所有 Subsystem 或每次 Work Package 的固定套餐。具體規模仍須由各 Subsystem 的 Stress Applicability 與 reference environment baseline 決定。

### 已確認的 Stress Applicability

每個 Subsystem 必須依真實業務風險判斷下列維度，而不是只依呼叫頻率或套用固定最大負載：

- 正常、尖峰與突發使用模式。
- 並行競爭。
- 資料／路徑／Entity 規模。
- 狀態持續時間。
- crash 與故障復原。
- 單次失敗的影響範圍。
- 外部副作用。
- 已明確要求的 latency／throughput。
- 執行壓力測試的時間、模型、硬體及環境成本。

每種壓力測試必須標記為 `required`、`conditional` 或 `not_applicable`；`not_applicable` 必須有具體業務理由。

每個 Subsystem 規格應包含 Stress Contract：

```yaml
stress_contract:
  workload:
    normal:
    peak:
    burst:

  risk_dimensions:
    concurrency:
    data_volume:
    state_duration:
    recovery:
    failure_impact:
    external_side_effects:

  required_tests: []
  conditional_tests: []
  not_applicable: []

  execution_budget:
    routine:
    subsystem_acceptance:
    release:
```

Ownership Subsystem 目前判定為：

- 高 QPS 與嚴格 latency：低適用或 conditional，先建立 baseline。
- 同資源競爭、candidate churn、大型路徑、crash／handoff、驗收弱化對抗：required。
- 長時間 soak：重大版本或 Recovery 核心變更時 conditional。
- 外部服務負載：not applicable。

### 已確認的規格來源與缺漏處理

主 Agent是規格編譯者，不是規格權威來源：

```text
使用者目標＋固定引用的長期規範
→ 主 Agent分析、推導與起草
→ 依風險取得必要確認
→ 凍結的任務規格
→ 本次任務 SSOT
```

Stress／Verification Contract 的每個條目應標示來源：

| 來源 | 驗收效力 |
|---|---|
| `user_explicit` | 可直接形成驗收 |
| `referenced_approved_spec` | 可直接形成驗收 |
| `ddh_default_invariant` | 已成為長期核准規則時可形成驗收 |
| `derived_from_live_evidence` | 可決定測試類型；正式門檻仍需證據 |
| `assumption_needs_confirmation` | 不得直接作為完成門檻 |

缺漏分流：

- 已核准技術不變量：主 Agent可直接投影成測試。
- 可由 live project 推導負載類型但沒有門檻：先做 characterization／baseline，只報 measured，不報 pass。
- 缺少業務 expected behavior：停止相關分歧並提出規格缺口。
- 測試確實不適用：標記 `not_applicable`，附 scope 與依賴證據。

確認強度：

- L0：使用者寫明的 Agent 目標為 SSOT，採輕量驗證。
- L1／L2：主 Agent依規格與已核准 DDH defaults 組裝 Verification Contract，由使用者確認整份任務規格。
- L3：架構、schema、公開契約、不可逆操作及新的業務門檻需明確確認。
- test implementation 可在不改 expected behavior 的前提下修正；正式門檻與驗收語意不得由 Agent 自行改變。

### 尚待確認

1. OW-F18 的 Ledger event schema、artifact 分層、retention profiles、failure fingerprint、compaction 與查詢細節。
2. System Map dependency index 與 live dependency verification 的整合方式。

### 後續獨立議題：pytest 資產與驗收監督

本 Subsystem 產生大量可執行驗收案例，但不在此文件內決定它們的長期治理。後續必須另行討論：

- pytest 依 Global／Domain／Subsystem／Module 規格如何存放與索引。
- 規格條目、業務場景、pytest 與歷史結果的版本關係。
- 規格、契約、架構、fixture 或 production behavior 改變後，哪些測試過期。
- stale、superseded、quarantined、deprecated 與 active 測試狀態。
- 影響閉包、測試選取、去重、封存及執行成本。
- flaky、無效 assertion、錯誤 fixture、從未被觸發的測試及 suite health。
- 如何區分 test implementation defect 與 acceptance standard change。
- 如何監督刪除、skip／xfail、放寬 assertion、降低壓力門檻或縮小資料集。
- 如何讓獨立 Critic／不同模型或機械 mutation 檢查驗收變更，避免同一模型自行放寬標準。
- 哪些變更可由 Test Agent 自主修復，哪些必須由人類確認新的 expected behavior。

此議題暫稱：

> **Executable Acceptance Asset Management and Independent Test Supervision**

名稱、層級與是否拆成一個或多個 Subsystem，留待後續逐項確認。
