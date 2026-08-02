# 規格包驅動執行模組：開發方向提案

- Status: Proposed
- Decision authority: Pending human review
- Recorded: 2026-08-02
- Implementation authority: None
- Scope: ADHD successor architecture with selective migration from legacy ADAD

## 0. 提案邊界

本文件記錄待討論的開發方向，不是 Accepted Decision、runtime specification、
schema 或實作授權。

> Authority amendment（2026-08-02）：Decision 0002 已取代本文的「雙 SSOT」
> 方向。System Map 是 actual-only architecture index，不是 SSOT 或授權來源；
> 本次人類確認的任務規格書才是 Agent 目標與完成判定的 SSOT。
>
> Package amendment：`SPEC-WP-001` 已確認 Task Specification 是 task SSOT，
> Work Package 是可自動重建的 execution projection；本文任何把 Work Package
> 描述為獨立執行契約權威的段落，都須依該 Contract 解讀。

在取得明確核准前，不得因本文件：

- 修改原始碼、System Map、Task、Checkpoint 或任何治理狀態。
- 建立 runtime、CLI、hook、schema、generated Bundle 或 migration tool。
- 將 legacy ADAD 的 Task、Source Lock、Checkpoint、freshness chain、
  receipt 或 recovery Control Plane 直接搬入 ADHD。
- 將本文的「應」「必須」誤讀為已核准的產品規格；它們目前只描述提案意圖。

後續工作必須先完成：

1. legacy ADAD 現況盤點。
2. 新模組設計提案。
3. 舊機制遷移矩陣。
4. 與現行 ADHD 架構規格的衝突協調。
5. 人類逐項核准。

## 1. 目標

為 legacy ADAD 重構一個新的「規格包驅動」執行模組，降低下列舊流程成本：

- 小 Task 過度切分。
- 細粒度、常態性的單檔 Source Lock。
- 每個測試關卡都需要人工 Checkpoint。
- 每次施工都建立完整隔離環境。
- 每個小 Task 都套用固定角色鏈。

同時保留真正必要的：

- 安全邊界。
- 高標準驗證。
- 適度且可操作的追溯能力。
- 失敗後保留使用者 diff 的復原能力。
- 外部副作用的獨立人工控制。

## 2. Work Package／規格包

### 2.1 定位

以 Work Package 取代小型、單節點 Task，作為一次自主開發循環的執行契約。

Work Package 不是 legacy Frozen Task 的直接改名。它的目的不是建立永久 Task
lifecycle，而是清楚界定一次開發工作的目標、權限、驗收與停止條件。

### 2.2 使用者定義內容

每次 Work Package 由使用者定義或核准：

- 目標。
- 允許修改的架構範圍。
- 禁止修改或禁止執行的項目。
- 連結的語意規格與驗收條件。
- 必須通過的測試關卡。
- token、時間、嘗試次數或其他執行預算。
- 需要獨立高風險流程的操作。

允許修改範圍應依任務選取任意層級的 System Map Entity，例如：

- 整個 Domain。
- 一個 Subsystem。
- 一個 Module。
- Module 內更細的 Model 或 Internal Entity。
- 多個彼此相關的架構節點。

實際範圍表示法、descendant 涵蓋規則、跨範圍依賴與最小可選粒度尚待討論。

### 2.3 核准與變更

Work Package 核准後，提案方向要求固定：

- 規格包版本。
- 允許修改範圍。
- 禁止項目。
- 驗收條件。
- 測試關卡。
- 預算與外部副作用權限。

若來源、System Map Ready Snapshot、語意規格或其他執行前提發生足以影響
Work Package 的變化，不得靜默沿用原規格包；必須提出結構化更新提案。

此處的「漂移檢查」只考慮當次 Work Package 的執行前提是否仍成立，不表示恢復：

- 跨版本 stable Entity identity。
- legacy contract freshness chain。
- Task lifecycle 自我失效。
- watcher freshness barrier。
- 由 discovery metadata 提供施工授權。

確切的版本投影、比較欄位、fail-closed 條件與更新流程尚待設計。

### 2.4 自主循環

Work Package 核准後，主 Agent 可在範圍內自主：

1. 規劃。
2. 實作。
3. 執行測試。
4. 診斷失敗。
5. 修正實作或測試環境。
6. 重複驗證。
7. 在達到驗收標準後完成並呈報。

一般測試關卡通過後依規格包自動繼續，不需要逐關人工確認。

### 2.5 人類已確認的任務規格 SSOT 與 System Map index 分工

> Confirmation status: Direction confirmed; verification strictness remains pending.

DDH 依下列權責判定與執行工作：

1. 任務規格書：本次 Agent 目標、scope、限制、功能行為、業務情境、
   驗收條件、壓力條件與完成標準的 SSOT。
2. System Map：actual-only 的真實架構 index，用於快速定位位置、關係、
   依賴與候選 impact closure，不提供施工或驗收 authority。
3. live project assets：目前實作狀態的證據；與 index 不一致時對受影響
   範圍進行 bounded live-source discovery，並安排 Map maintenance。

Work Package 範圍內不應預設大量細部編碼約束。除使用者或規格包明確要求外，
主要只保留必要的工程指引，例如：

- 維持 Module／Model 的模組化責任。
- 在需要說明意圖、限制或非顯而易見行為時撰寫註解。
- 遵守本次範圍列出的其他注意事項。
- 不得違反任務規格固定引用的架構規範；System Map 用於快速發現可能相關
  的責任、依賴與 source location，再以 live assets 確認。

Agent 在此邊界內可以自主選擇實作方式，不應被 legacy ADAD 的固定角色鏈、
逐模組 Checkpoint、常態 Source Lock 或過度細粒度的實作規則限制。

建議的核心完成流程為：

```text
Work Package scope 內自主實作
  → System Map architecture conformance
  → Semantic Specification functional verification
  → Semantic Specification stress／load verification
  → Work Package completed
```

因此，Work Package 只有在下列兩類必要證明都成立時才算完成：

1. 實作符合 System Map 的架構範圍與結構規範。
2. 實作通過語意規格書所定義的功能檢測、壓力測試與完成條件。

`subsystem_integrated`、`domain_accepted` 或其他中間名稱不是框架強制建立的固定
lifecycle。當 Work Package 本身選取 Subsystem 或 Domain 作為 scope 時，該層級的
整合或業務驗收應直接由相連的語意規格定義；只有產品確實需要時，才建立額外的
可重建驗證 projection。

ADHD 必須提供驗證能力，但不得把所有可能的高保證檢查預設套用到每個 Work Package。
下列細節仍待逐項討論：

- 每種 scope 的最低 System Map conformance 檢查。
- 功能驗收案例的必要深度。
- 壓力／負載測試是否適用及其門檻。
- 何時需要 integration、端到端、安全、資料或獨立語意 Reviewer。
- 風險如何提高驗證強度。
- 哪些測試失敗可在原 scope 內自動修正。
- 驗證預算與停止條件。

## 3. 例外升級

新流程採例外升級，不採逐關審批。

### 3.1 必須停止並提出變更報告

需要改變下列任一項時，主 Agent 必須停止自主施工：

- 架構。
- 資料契約。
- 公開介面。
- 既有語意規格。
- Work Package 允許修改範圍。
- 驗收標準或風險政策。
- 未被明確允許的外部副作用。

### 3.2 無法完成時的結構化回報

下列情況也必須停止並提出結構化例外報告：

- 必要資訊不足。
- 驗收反覆失敗且沒有新證據或新修正路徑。
- 預算耗盡。
- 風險已超出 Work Package 的自主處理權限。

例外報告至少應包含：

- 原目標與目前 Work Package 版本。
- 已嘗試的方案。
- 已執行的驗證與結果。
- 保留的 diff 與工作區狀態。
- 已知缺口與根因判斷。
- 是否需要擴大架構或寫入範圍。
- 可選下一步及其風險、成本與權限需求。

## 4. 單一主 Agent 與子代理

### 4.1 預設模式

主 Agent 預設單一執行。不能因為可以建立子代理就自動平行化。

只有風險分析明確支持時，才啟用子代理。分析至少考量：

- 工作是否真正獨立。
- 寫入範圍是否重疊。
- 模組耦合程度。
- 子代理載入必要上下文的成本。
- 最終整合與重新驗證成本。
- 預期平行收益。
- 額外風險。
- Work Package 剩餘預算。

### 4.2 主 Agent 權責

主 Agent保留：

- 完整 Work Package。
- 完整架構與語意規格上下文。
- 分工決策。
- 寫入範圍分配。
- patch 整合權。
- 範圍與風險判定權。
- 最終驗證與例外升級責任。

### 4.3 Context Envelope

子代理只接收完成子工作所需的最小 Context Envelope：

- 子目標。
- 允許讀取範圍。
- 允許寫入範圍。
- 必要架構與行為契約。
- 驗收條件。
- 預算。
- 必須升級的條件。
- 回傳格式。

子代理不得：

- 自行擴大讀寫範圍。
- 自行修改 Work Package。
- 自行改變架構、規格、驗收或權限。
- 將 discovery metadata 當成 authority。

子代理可以請求更多上下文，但只能由主 Agent 判斷是否提供，並記錄對範圍、
風險與預算的影響。

## 5. Legacy ADAD 能力取捨方向

下表是待盤點與驗證的初始分類，不代表現況已證明或遷移已核准。

| Legacy capability | 初始方向 | 提案理由 |
|---|---|---|
| 架構理解與 impact index | 保留並改造 | 改接 actual-only System Map QueryService；不遷移其 SSOT 或授權語義 |
| 新鮮度檢查 | 規格包化 | 只檢查當次 Work Package 前提，不恢復跨版本 freshness chain |
| Harness／不變量驗證 | 保留並改造 | 作為分層驗證的一部分 |
| 依賴／Domain 邊界檢查 | 保留並改造 | 由目前 System Map scope 與關係判定 |
| workspace baseline／diff 證據 | 規格包化 | 支援越界檢查、失敗診斷與保留使用者修改 |
| 真正的執行隔離 | 條件式保留 | 依風險與外部副作用啟用，不再每次完整隔離 |
| 失敗復原與保留 diff | 替換 | 保留能力，避免恢復重型 recovery Control Plane |
| 資產與設定同步 | 保留並改造 | 需定義 canonical source、dry-run 與 parity verification |
| 可觀測性 | 保留並改造 | 服務診斷與改善，不成為第二治理 SSOT |
| 跨平台可重現性 | 保留並改造 | 由明確環境契約與驗證矩陣負責 |
| Source Lock | 替換 | 改為條件式 Work Package／子代理寫入所有權租約 |
| PreTool gate | 替換 | 只機械阻擋無有效規格包、明顯越界與未允許副作用 |
| 發布／部署／資料庫／憑證／網路 | 獨立高風險流程 | 一般 Work Package 不得自主跨越 |
| 單節點小 Task | 淘汰 | 改由任意架構範圍的 Work Package 取代 |
| 單檔常態鎖 | 淘汰 | 只有真實共享寫入風險才啟用租約 |
| 每模組人工 Checkpoint | 淘汰 | 改採例外升級 |
| 每次完整隔離 | 淘汰 | 改為風險驅動隔離 |
| 每小 Task 固定角色鏈 | 淘汰 | 改為單一主 Agent預設、風險支持才分工 |

正式遷移矩陣必須以 legacy ADAD 的 current source、設定、測試與文件為證據，
逐項標示：

- 實際落地位置。
- 目前行為。
- 現有測試強度。
- 已知缺陷與歷史摩擦。
- 保留／規格包化／替換／淘汰結論。
- 新 ADHD 責任歸屬。
- 不遷移的 legacy governance 資產。

## 6. 寫入所有權租約

寫入所有權租約只在下列情況啟用：

- 多個 Agent 平行修改。
- 多個 Work Package 同時存取共享可變資源。
- 外部工具無法提供安全的原子合併或衝突偵測。

它不應成為：

- 每個 Work Package 的必經步驟。
- 永久單檔鎖。
- System Map Entity 的 lifecycle。
- discovery index 中的 authority。
- 缺少有效 Work Package 時的替代授權。

租約的資料模型、原子性、失效、續租、回收、衝突與 crash semantics 尚待設計。

## 7. 編排長期記憶與受控自我演進

### 7.1 記憶目的

原始執行與除錯紀錄是短期事件。獨立分析 Agent 可以從重複且有證據的派工問題中，
整理長期編排經驗，用於改善主 Agent：

- 任務切分。
- Context Envelope 組裝。
- 是否派工的判斷。
- 子代理摘要與回傳格式。

### 7.2 長期記憶最小要求

每條記憶至少包含：

- 適用條件。
- 支持證據。
- 信心程度。
- 版本。
- 失效條件。
- 與其他記憶衝突時的處理規則。

不得把以下內容直接加入 prompt：

- 未篩選的原始 log。
- 完整對話。
- 未驗證的單次經驗。
- 無適用條件或失效條件的結論。

### 7.3 自我演進邊界

演進 Agent 只能提出：

- 角色 prompt 候選。
- Context Envelope 模板候選。
- 派工或摘要格式候選。

獨立 Critic Agent 必須透過回放測試與小範圍試用驗證候選效果，並保留回滾能力。

自我演進機制不得修改：

- Work Package 規格邊界。
- 架構判定。
- 權限。
- 驗收標準。
- 量測邏輯。
- 人工升級條件。

長期記憶不是架構 SSOT、語意規格 SSOT 或授權來源。

## 8. 外部副作用

下列能力維持獨立高風險流程：

- 發布與部署。
- 資料庫 migration 或資料破壞性操作。
- 憑證與 Secret。
- 網路及外部服務 mutation。
- 不可逆 filesystem 操作。
- 對外訊息、release 或正式狀態變更。

一般 Work Package 即使測試全部通過，也不得自動取得上述權限。

## 9. 必須維持的 authority 原則

- `task_index.json` 或任何 discovery metadata 只能協助尋找資料，不能授權施工。
- prompt 中的白名單、禁止事項與角色描述不是機械強制。
- 機械強制只能由實際 boundary、validator、sandbox、lease、transaction 或 gate 提供。
- System Map 提供結構與範圍資料，但不自行授予外部副作用權限。
- 測試通過證明的是特定驗收，不自動等於發布、部署或人工決策已完成。
- 日誌、Index、projection、memory 與報告都是 derived data，不是額外 SSOT。

## 10. 與現行 ADHD 規格的待協調事項

本提案與現行文件存在以下需由人類逐項決定的差異：

| 主題 | 現行 ADHD 方向 | 本提案方向 | 待決定邊界 |
|---|---|---|---|
| Task 替代 | 不建立 Frozen Task | 建立 Work Package | Work Package 如何避免重新形成 Task lifecycle |
| Freshness | 移除 freshness chain | 保留規格包前提漂移檢查 | 限定比較欄位、版本與更新提案規則 |
| Source Lock | 移除 Source Lock／lease | 條件式寫入所有權租約 | 只在平行或共享資源時存在 |
| Evidence | 移除重型 receipts | 保留 baseline／diff／結果證據 | 最小證據集與保存期限 |
| Recovery | 移除 recovery Control Plane | 保留失敗復原與 diff | 實作為工作區安全能力，不形成治理狀態機 |
| Agent 模式 | 子代理協定延後 | 單主 Agent＋風險式派工 | 風險評估與 Context Envelope 契約 |
| Long-term memory | 尚未定義 | 受控編排記憶與演進 | 權威隔離、驗證、版本與回滾 |

在上述差異完成決策前，本提案不得覆蓋：

- `AGENTS.md` 的禁止事項。
- `docs/architecture/adhd_product_architecture_v0.md` 的 confirmed removals。
- `docs/architecture/system_map_bundle_specification_v1.md` 的 Bundle 邊界。
- `docs/decisions/0001-adhd-project-identity.md` 的 Accepted Decision。

## 11. 待交付設計成果

後續討論與設計階段應交付：

1. legacy ADAD 能力盤點與正式遷移矩陣。
2. Work Package 資料模型草案。
3. Context Envelope 資料模型草案。
4. 例外報告資料模型草案。
5. 寫入所有權租約資料模型草案。
6. 編排長期記憶資料模型草案。
7. 單一主 Agent 與子代理的風險分流規則。
8. 新舊流程對照。
9. 最小可行端到端流程。
10. 分階段實作計畫。
11. 各階段風險與驗收標準。
12. 必須由人類決定的架構與權限事項。

這些成果現階段都是設計文件，不包含 runtime implementation。

## 12. 建議討論順序

為避免一次同時定義過多治理機制，建議逐項討論：

1. Work Package 的責任與非責任。
2. Work Package 的架構範圍表示。
3. 核准後固定內容與允許自動更新的內容。
4. 漂移檢查的精確語意。
5. 例外升級條件與報告格式。
6. 單一主 Agent／子代理分流規則。
7. Context Envelope。
8. 條件式寫入所有權租約。
9. 最小 evidence 與失敗復原。
10. 編排長期記憶與演進隔離。
11. legacy ADAD 遷移矩陣。
12. MVP 端到端流程與分階段計畫。
