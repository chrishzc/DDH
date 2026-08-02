# Learning Steward Role Specification

**Canonical role name：** `Learning Steward`  
**歷史名稱／ID：** Orchestration Learning and Evolution／OLE  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 本文件保存已逐項確認的功能與驗收方向；實作技術與未確認門檻仍需後續決策  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

---

## 1. 責任

使用短期機械觀測、Attempt Ledger 與有界 log 分析派工、Context、平行化與復原模式，經 Analyzer／Critic 處理後更新長期編排記憶並刪除原始資料。

## 2. 不負責

- 不自行改變使用者目標、任務規格、架構決策、公開契約或人類升級條件。
- 不把 System Map、discovery metadata、Agent claim 或 prompt 約束當成授權或機械證據。
- 不因本 Subsystem 的局部 PASS 宣告 DDH Domain、release candidate 或 production 完成。

## 3. 依賴與協作

- 其他 Subsystems 只提供結構化短期執行特徵，不提供完整 prompt、source、diff 或永久 logs。
- Mechanical Verification 的 pytest 資產是完成後留下的 Evidence Retention。
- 自進化不得修改規格、權限、驗收、風險政策或人工升級條件。
- Terminal execution 與 Ledger seal／enqueue 的原子交接遵守
  `terminal_completion_attempt_ledger_handoff_contract.md`（`DOM-OLE-001`）；
  completion 不等待 Analyzer／Critic。
- Pending Ledger 的 prefilter、priority、resource budgets、Analyzer outage 與
  expiration 遵守 `evolution_profile_pending_ledger_policy.md`
  （`OLE-PROFILE-001`）。
- DDH runtime health、metrics、events、traces、logs 與 bounded OLE telemetry
  遵守 `operational_telemetry_and_health_model.md`（`DDH-OBS-001`）；
  telemetry 原文不得直接成為 long-term memory。
- Long-term Memory object、query／resolver、main-Agent consumption 與
  Registry／Reconciler maintenance 遵守
  `long_term_orchestration_memory_model.md`（`OLE-MEM-001`）。
- Memory Candidate、independent Critic、Replay、Shadow、Canary、Promotion 與
  Rollback 遵守 `memory_evolution_critic_trial_rollback_contract.md`
  （`OLE-EVOL-001`）。

## 4. 已確認功能

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
| `terminal_outcome` | completed／blocked／budget-exhausted／escalation-required／cancelled／superseded 等 terminal family |

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
- Ledger 經完整 mechanical disposition，或成功 atomically fold into
  Learning Candidate 後整體刪除，不留下 compact Ledger copy。Learning
  Candidate 只能保存 normalized aggregate facts，不得成為原始 Ledger 副本。

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

Individual Ledger 與聚合候選採兩段生命週期：

```text
active
→ sealed_pending_evolution
→ mechanically_prefiltered
→ consumed
→ deleted

或

mechanically_prefiltered
→ atomically_folded_into_learning_candidate
→ source_ledger_deleted

Learning Candidate
→ selected_for_model_analysis
→ critic_decided／known-no-change／insufficient／superseded／expired
→ deleted
```

Execution run 進入 completed、blocked、budget-exhausted、escalation-required、
cancelled 或 superseded 等 terminal outcome 時，依 `DOM-OLE-001` 立即 seal
Ledger，不再新增 Attempt Row。後續 lifecycle correction 只能形成明確 metadata
projection；新 attempt 必須使用新的 execution run／Ledger。

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
| `candidate_new_pattern` | 建立／更新短期 Learning Candidate，依 profile 判斷是否分析 |
| `candidate_repeated_pattern` | 與同群組 Candidate 機械聚合，達門檻後批次進入 Analyzer |
| `critical_orchestration_failure` | 建立 P0 Candidate，在目前 mutation transaction 安全終止後優先進入 Analyzer／Critic |
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
2. **Critical trigger：** P0單次即在目前 mutation transaction 安全終止後排程。
3. **Batch trigger：** P1相同pattern兩次或最長一小時；P2跨至少兩個Work
   Packages且三次或每日idle batch；P3五次才取得專用model call。
4. **Evolution change gate：** 修改角色 prompt、Context template 或派工 policy 前，先分析相關 pending candidates 並交由 Critic 驗證。
5. **Idle／maintenance trigger：** 有可用預算時處理低優先候選。

上述數量與時間是Decision 0023固定的MVP bootstrap profile；它們不是架構
常數，只能由明確核准、版本化的Evolution Profile修改。Evolution token
budget仍由profile設定，且與active Work Package預算分離。

### 模型分析與 Critic

- Analyzer 只接收 Ledger features、相關既有記憶與必要最小 failure excerpt，不接收完整 prompt、source、diff 或 logs。
- Analyzer 產生 memory candidate：適用條件、問題／成功模式、建議派工調整、證據摘要、信心、版本與失效條件。
- Critic 以 replay、歷史對照或小範圍試用決定 accepted、updated、rejected 或 insufficient-evidence。
- rejected pattern 可以留下有期限、可失效的 suppression summary，避免相同候選反覆消耗 token；不保存原始 Ledger。

### 刪除條件

Individual Ledger只有出現以下任一完整結果，才能標記 consumed／folded：

- 已確認更新既有長期記憶。
- 已確認建立新長期記憶。
- Critic 拒絕候選。
- 證據不足並完成 suppression／重新累積決策。
- Mechanical Prefilter 確認沒有編排訊號或只是已知模式。
- 已成功 atomically fold 成不依賴 source Ledger 的 Learning Candidate。

Individual Ledger `consumed`／`folded` 後刪除：

- Work Package Summary。
- Partition Summaries。
- Attempt Rows。
- 一般 execution logs 與短期 artifacts。

不刪除：

- 產品 source。
- active pytest／fixture／configuration／profile。
- 使用者工作區差異。
- 已接受的長期編排記憶。

Routine／known-no-change／one-off material立即刪除；成功fold的source Ledger
最遲24小時刪除。尚未完成fold／prefilter的outage upper bound為P3 24小時、
P2 72小時、P1 7天、P0 14天。單份serialized Ledger hard cap為64 KiB。

Learning Candidate在promoted、known-no-change、rejected、
insufficient-evidence、superseded或`analysis_expired_without_memory_change`
後刪除；maximum age為P3 7天、P2 14天、P1 30天、P0 90天。

Analyzer／Critic／prefilter 失敗或狀態未知時，不能假裝已產生一般 accepted／
rejected decision。已成功fold時不必保留Individual Ledger；尚未成功fold的
source Ledger與Candidate各自遵守期限。Completion不等待此流程；完整profile
依`OLE-PROFILE-001`與Decision 0023處理。

## 5. 已確認業務場景

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

- 至少跨兩個 Work Packages 累積三次後，相關 normalized features 聚合成
  Learning Candidate並批次送入Analyzer。
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
- 成功fold後刪除原Ledger；P0 Learning Candidate在決策完成或90天上限前
  保持pending。

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
- Learning Candidate取得terminal disposition後刪除；原始Ledgers應已在
  atomic fold後刪除。

### OW-S145：Analyzer 暫時失敗

**對應功能：** OW-F18.3

**Given**

- Ledger 已被選入分析。
- Analyzer／Critic 因模型、預算或系統錯誤未完成。

**When**

- 清理程序執行。

**Then**

- Learning Candidate保持pending，不假裝已被accepted／rejected。
- 已成功fold的原始Ledger不因Analyzer失敗而恢復或延長保存。
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

## 6. 壓力與對抗場景

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

### OW-P20：重複失敗與預算耗盡

- 產生大量相同及不同 failure fingerprints。
- 相同 fingerprint 且無新增證據的重試必須受 attempt budget 限制。
- 新 fingerprint 或新增診斷證據不能被錯誤當成相同無進展循環。
- 預算耗盡後必須產生一次結構化停止結果，而不是繼續重試或遺失候選成果。

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

## 7. pytest 投影規則

- 每個場景以舊 ID 作 traceability key，例如 `@pytest.mark.ddh_scenario("OW-S48")`。
- pytest／fixture／configuration／profile 必須能在沒有 Agent／LLM service 時重跑。
- Test asset admission／stale 判定由 TAQG 管理；正式 suite execution 由 MVE 管理。
- 原 archive 中的示範 test names 只作歷史參考，不是新規格的檔案配置決策。

## 8. 舊 ID 遷移

### 功能

| 舊 ID | 已確認項目 |
|---|---|
| OW-F09 | 執行期間的機械觀測 |
| OW-F18 | Attempt Ledger 暫存與自進化消化 |
| OW-F18.1 | Attempt Ledger 最小資料模型 |
| OW-F18.2 | 短期 Log Buffer 與輸出邊界 |
| OW-F18.3 | Ledger 消化觸發與刪除時機 |

### 場景

| 舊 ID | 已確認項目 |
|---|---|
| OW-S48 | 正常產生完成證據 |
| OW-S49 | Agent 宣稱測試通過但沒有執行證據 |
| OW-S50 | 區分產品失敗與執行環境失敗 |
| OW-S51 | 驗證輸出包含敏感資訊 |
| OW-S52 | 大量正常寫入採聚合證據 |
| OW-S53 | 證據儲存暫時不可用 |
| OW-S54 | Agent claim 與 observed result 衝突 |
| OW-S55 | 短期事件不得直接進入長期記憶 |
| OW-S116 | 第一次驗證失敗 |
| OW-S117 | 相同失敗無新進展地重複 |
| OW-S118 | 相似錯誤但出現新證據 |
| OW-S119 | 節點完成後只留下可重跑測試 |
| OW-S120 | 自進化完成後刪除 Attempt Ledger |
| OW-S121 | 自進化尚未完成 |
| OW-S122 | 完成後查詢歷史 PASS |
| OW-S123 | 原始事件不能直接成為長期記憶 |
| OW-S124 | 取消任務的 Ledger 仍進入消化流程 |
| OW-S125 | 一次成功的最小 Ledger |
| OW-S126 | 一次 Attempt 內包含多個 Tool Calls |
| OW-S127 | 失敗後修正形成兩個 Attempts |
| OW-S128 | 比較兩種派工的 Context 成本 |
| OW-S129 | Ledger 欄位寫錯後修正 |
| OW-S130 | 消化後完整刪除 Ledger |
| OW-S131 | 成功 pytest 產生大量輸出 |
| OW-S132 | 失敗 pytest 提供最小診斷片段 |
| OW-S133 | 相同失敗反覆輸出相同 Log |
| OW-S134 | Log 含敏感資訊 |
| OW-S135 | 輸出超過 Buffer 上限 |
| OW-S136 | Process Timeout 仍保留必要片段 |
| OW-S137 | Evolution Analyzer 要求額外 Failure Excerpt |
| OW-S138 | Log Buffer Crash Recovery |
| OW-S139 | 例行首次成功不啟動模型分析 |
| OW-S140 | 已知模式只更新支持摘要 |
| OW-S141 | 重複 Context 膨脹觸發批次分析 |
| OW-S142 | 嚴重編排失敗優先分析 |
| OW-S143 | 一次性產品 Bug 不進入自進化 |
| OW-S144 | Critic 拒絕 Memory Candidate |
| OW-S145 | Analyzer 暫時失敗 |
| OW-S146 | 正式模板變更前的 Evolution Gate |

### 壓力

| 舊 ID | 已確認項目 |
|---|---|
| OW-P17 | 高輸出與大量正常事件 |
| OW-P18 | 多 Agent 事件關聯 |
| OW-P20 | 重複失敗與預算耗盡 |
| OW-P35 | 大量 Attempt 的自進化消化 |
| OW-P36 | Ledger 消化與刪除競態 |
| OW-P37 | 大量 Tool Calls 不造成 Ledger 線性膨脹 |
| OW-P38 | 大量 Ledgers 的自進化特徵比較 |
| OW-P39 | Log Storm 與固定記憶體上限 |
| OW-P40 | 重複、敏感與截斷輸出組合 |
| OW-P41 | 大量 Terminal Ledgers 的機械 Prefilter |
| OW-P42 | Analyzer Backlog 與刪除安全 |

## 9. 拆分後待補

- OLE 與 TAQG／MVE 的切割：test quality／admission 由 TAQG 擁有，verification invocation／outcome 由 MVE 擁有，OLE 只引用結構化結果。
- Work Package terminal event 與 Ledger seal／enqueue 契約。
- 確認一般任務完成不等待 Analyzer／Critic，避免自進化 backlog 阻塞施工。
- Evolution Profile的三層input、MVP trigger與retention defaults已由Decision
  0023確認；item／storage總量、model token額度、batch size與retry細節仍待
  Implementation Readiness profile固定。
- Mechanical Prefilter 的 pattern schema 與既有 memory comparison。
- Long-term memory 的正式資料模型、support count、confidence、version、invalidation 與 conflict handling。
- Analyzer 與 Critic 的獨立性、replay corpus、小範圍試用與 rollback。
- suppression summary 的內容、期限與失效條件。
- consumed marker 與刪除操作的機械安全，但不建立永久 deletion receipt。
- 本 Subsystem 自己的完成判準與 Stress Contract。

以上仍是 gap，不構成實作決策。

## 10. 已確認的 TAQG Quality Profile 邊界

- OLE 不得修改 Test Quality Applicability、Quality Profile thresholds、required dimensions、oracle、SLO、measurement logic、invalidation triggers 或 Critic independence。
- OLE 只能改善 Test Agent／Critic 派工、Context Envelope、sharding、parallelism、cache、ordering、batching、failure clustering 與摘要格式。
- OLE 發現測試成本或偵測問題時，只能形成 orchestration observation；TAQG 必須以獨立 calibration tests／fixtures 重現後，才能提出 versioned profile proposal。
- Quality Profile proposal 必須經獨立 benchmark／Critic 與人類 policy approval，不能由 self-evolution 自動生效。
- 新 profile 只適用未來依該版本建立的 Work Packages，不追溯修改 pinned subjects。
