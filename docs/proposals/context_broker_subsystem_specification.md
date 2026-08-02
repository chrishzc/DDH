# Context Curator Role Specification

**Canonical role name：** `Context Curator`  
**歷史名稱：** Context Broker  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 本文件保存已逐項確認的功能與驗收方向；實作技術與未確認門檻仍需後續決策  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

---

## 1. 責任

使用 System Map 作為 discovery index，以最小 Context Envelope、按需 content grant 與 token budget 控制子代理上下文成本。

## 2. 不負責

- 不自行改變使用者目標、任務規格、架構決策、公開契約或人類升級條件。
- 不把 System Map、discovery metadata、Agent claim 或 prompt 約束當成授權或機械證據。
- 不因本 Subsystem 的局部 PASS 宣告 DDH Domain、release candidate 或 production 完成。

## 3. 依賴與協作

- Parallel Work Coordination 提供 subgoal、partition 與 Context 需求。
- System Map 提供 Entity、relation、path 與摘要索引，但不提供授權。
- Live source 提供目前內容與 drift 證據。

## 4. 已確認功能

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

具體absolute token數不在此預先固定。依Decision 0021，每個subagent的bootstrap
以model effective context計算：initial envelope最多約15%、source全文累計
預設最多30%、single grant最多5%，且至少保留50%給reasoning、tool results與
output。Project profile可依模型、任務層級、Context reuse與Work Package budget
校準。

## 5. 已確認業務場景

### OW-S100：最小初始 Context Envelope

**對應功能：** OW-F16

**Given**

- Test Agent 只負責 `PAY-02` 與 `PAY-03` acceptance。

**When**

- 主 Agent建立初始 Context Envelope。

**Then**

- 包含使用者目標、兩個規格條目、必要契約、相關 symbol index 與 test write zone。
- 不自動載入整個 Workspace Domain。
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

- 它要求載入整個 Workspace Domain。

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

## 6. 壓力與對抗場景

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

## 7. pytest 投影規則

- 每個場景以舊 ID 作 traceability key，例如 `@pytest.mark.ddh_scenario("OW-S100")`。
- pytest／fixture／configuration／profile 必須能在沒有 Agent／LLM service 時重跑。
- Test asset admission／stale 判定由 TAQG 管理；正式 suite execution 由 MVE 管理。
- 原 archive 中的示範 test names 只作歷史參考，不是新規格的檔案配置決策。

## 8. 舊 ID 遷移

### 功能

| 舊 ID | 已確認項目 |
|---|---|
| OW-F16 | Context Broker 與 Context Budget |

### 場景

| 舊 ID | 已確認項目 |
|---|---|
| OW-S100 | 最小初始 Context Envelope |
| OW-S101 | 請求額外 Symbol |
| OW-S102 | 要求整個 Domain |
| OW-S103 | Context Budget 耗盡 |
| OW-S104 | 已載入 Source 在施工中改變 |
| OW-S105 | System Map Index 已漂移 |
| OW-S106 | Context 縮減不得移除規格 |
| OW-S107 | 敏感資源請求 |
| OW-S108 | 存在繞過 Broker 的讀取通道 |

### 壓力

| 舊 ID | 已確認項目 |
|---|---|
| OW-P31 | Context Request Storm |
| OW-P32 | 大型 System Map 與依賴 Traversal |

## 9. 拆分後待補

- Context Envelope 與 content request／grant 的正式 schema。
- System Map query／summary interface，以及 live source verification adapter。
- Token estimation、actual usage reconciliation 與 model-specific profiles。
- Pinned specification／acceptance 在 compaction 後的語意完整性。
- Sensitive content policy 與 Context Broker 成本控制的分離。
- Candidate／contract invalidation 後 stale Context 的機械通知。
- 大型 graph traversal 的 bounded query 與重複 artifact cache。
- 本 Subsystem 自己的完成判準與 Stress Contract。

以上仍是 gap，不構成實作決策。

## 10. 已確認的 Recovery Chain

### RC-DOM-003：Rebuildable Artifact Failure

- Context Envelope 與 temporary query／index results 是 derived artifacts，可從固定規格、live source 與有效 System Map index 重新 materialize。
- Rebuild 不得讓 System Map、cache 或摘要取代 task specification authority。
- Rebuild 後必須重新核對 Context identity、content grant、token budget 與 invalidation epoch。
- 完整內部 rebuild log 不進入 Agent Context，只提供有界結果摘要。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

## 11. 已確認的 System Map 使用 Contract

### SMQ-001：Architecture Impact Query

- Context Broker 接收 query purpose、seed nodes 與 Q0～Q3 bounds，透過外部 System Map query interface 取得結果。
- Agent 預設只取得有界摘要與 node IDs，不載入整份 System Map。
- Context artifact 必須引用 `architecture_query_result_id`、map／index version、traversal bounds 與 omission metadata。
- Query／index 故障時先重建 derived artifact，再使用 bounded live-source fallback。

System Map schema、Bundle、index、query engine、freshness 與更新設計由獨立 System Map 規格負責。

## 12. 已確認的 Recovery Chain

### RC-DOM-MVE-005：Product Verification Failure

- Context Broker 依 `architecture_query_result_id`、failure layer 與 impact closure 建立有界 Failure Bundle。
- Agent Context 只接收失敗場景、最小 assertion diff、相關 nodes／contracts、已嘗試摘要與剩餘預算。
- 完整 PASS logs、重複 traceback 與整份 System Map 不進入 Agent Context。
- Scope 內 repair 可自動補充必要 Context；跨 write-scope 內容仍需獨立 scope decision。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。
