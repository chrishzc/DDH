# Change Guard Role Specification

**Canonical role name：** `Change Guard`  
**歷史名稱／ID：** Candidate Integrity and Mutation／CIM  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 本文件保存已逐項確認的功能與驗收方向；實作技術與未確認門檻仍需後續決策  
**歷史來源：** `ddh_execution_domain_discussion_archive.md`

---

## 1. 責任

保護使用者工作區與 integration candidate，處理寫入邊界、快照、stale result、故障復原、Mutation Mediation 與可重現 candidate identity。

## 2. 不負責

- 不自行改變使用者目標、任務規格、架構決策、公開契約或人類升級條件。
- 不把 System Map、discovery metadata、Agent claim 或 prompt 約束當成授權或機械證據。
- 不因本 Subsystem 的局部 PASS 宣告 DDH Domain、release candidate 或 production 完成。

## 3. 依賴與協作

- Parallel Work Coordination 提供 active partition、writer 與 generation。
- Mechanical Verification 提供需要綁定的 verification subject。
- System Map 只協助 dependency discovery；live filesystem、source、schema 與 configuration 決定實際狀態。

## 4. 已確認功能

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

### OW-F14：建立 Mutation Mediation Boundary

**確認狀態：已確認（2026-08-02）**

Write Guard 與 Patch Admission 的需求不是「所有 edit 都必須先經過同一種
hook」，而是：

> 所有進入受保護 integration candidate 的 mutation，都必須經過可信
> execution identity、active partition、canonical resource 與 candidate
> generation 的機械 admission。L1 single-writer可以post-operation
> reconciliation作為admission boundary；L2 parallel或shared mutation必須使用
> verified containment或isolated Patch Admission。

Decision 0018採三種backend modes：

- `Serial Reconciled`：baseline＋明顯越界precheck＋post-delta admission。
- `Guarded Shared`：只有platform adapter證明完整mechanical capabilities時使用。
- `Isolated Candidate`：private candidate＋centralized local Patch Admission，
  是L2 parallel與未知輸出工具的預設。

Git hook只作advisory／defense-in-depth，不是mutation authority。第一版不建立
常駐central Patch Service。

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
- 目前mode的Mutation Mediation無法使用或狀態不確定時，相關partition必須
  freeze／recovery，並依序嘗試Isolated Candidate或符合條件的Serial
  Reconciled；不能降級成prompt-only parallel mutation。
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

## 5. 已確認業務場景

### OW-S12：合法的分區內寫入

**對應功能：** OW-F03

**Given**

- Test Agent 持有 active 的 `tests/workspace/**` 寫入分區。

**When**

- 它只修改 `tests/workspace/test_path_normalizer.py`。

**Then**

- 結果為 `write_allowed`。
- 其他不重疊 writer 不應被全域鎖錯誤阻擋。

### OW-S13：同一 patch 混合合法與越區修改

**對應功能：** OW-F03

**Given**

- Test Agent 只擁有 `tests/workspace/**`。

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

- Agent A 從 candidate `C1` 修改 Path Normalizer Module。
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

### OW-S85：直接 Patch 混合合法與非法目標

**對應功能：** OW-F14

**Given**

- Test Agent 的 active partition 只包含 `tests/workspace/**`。

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

## 6. 壓力與對抗場景

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

### OW-P19：Crash／timeout storm

- 多個 Agent 在取得分區後隨機 crash、timeout、失聯或留下部分 delta。
- 系統最終必須恢復可施工狀態，不留下永久 active partition。
- unknown execution state 不得被危險地自動清理或重派。
- 遲到 patch 不得污染新 generation。
- 所有可辨識的使用者原有差異與有用 Agent delta 都必須保留。

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

## 7. pytest 投影規則

- 每個場景以舊 ID 作 traceability key，例如 `@pytest.mark.ddh_scenario("OW-S12")`。
- pytest／fixture／configuration／profile 必須能在沒有 Agent／LLM service 時重跑。
- Test asset 存放、admission 與 stale 判定由 TAQG 管理；正式 suite 執行由 MVE 管理。
- 原 archive 中的示範 test names 只作歷史參考，不是新規格的檔案配置決策。

## 8. 舊 ID 遷移

### 功能

| 舊 ID | 已確認項目 |
|---|---|
| OW-F03 | 讀取與寫入分離 |
| OW-F08 | 固定整合快照 |
| OW-F10 | 故障復原 |
| OW-F11 | 防止接受過期成果 |
| OW-F14 | 建立 Mutation Mediation Boundary |
| OW-F15 | Candidate Identity 與 Snapshot Manifest |

### 場景

| 舊 ID | 已確認項目 |
|---|---|
| OW-S12 | 合法的分區內寫入 |
| OW-S13 | 同一 patch 混合合法與越區修改 |
| OW-S14 | 間接工具造成越區修改 |
| OW-S15 | 沒有機械寫入邊界 |
| OW-S40 | 正常建立整合快照 |
| OW-S41 | 仍存在 active writer |
| OW-S42 | Snapshot 建立後又發生修改 |
| OW-S43 | 驗證工具修改 candidate |
| OW-S44 | Snapshot 包含既有使用者差異 |
| OW-S45 | 各子代理個別 PASS，但整合 candidate 失敗 |
| OW-S46 | 遺漏 untracked 或 generated dependency |
| OW-S47 | 驗證期間規格版本更新 |
| OW-S56 | Agent crash 但沒有產生新差異 |
| OW-S57 | Agent crash 並留下有用的部分實作 |
| OW-S58 | 相同失敗反覆發生且沒有新證據 |
| OW-S59 | 環境失敗不得誤修產品程式 |
| OW-S60 | 外部副作用狀態不確定 |
| OW-S61 | 復原操作可能覆寫使用者差異 |
| OW-S62 | Work Package 取消後保留候選成果 |
| OW-S63 | 舊 baseline 但修改資源不重疊 |
| OW-S64 | 同一 logical resource 發生衝突 |
| OW-S65 | 路徑不重疊但依賴契約已變更 |
| OW-S66 | 任務規格版本已更新 |
| OW-S67 | 舊 generation 遲交看似可套用的 patch |
| OW-S68 | System Map 遺漏實際依賴 |
| OW-S69 | 重用完全相同 Snapshot 的驗證結果 |
| OW-S85 | 直接 Patch 混合合法與非法目標 |
| OW-S86 | 無法預知輸出的 Formatter |
| OW-S87 | 透過 Symlink／Junction 越出分區 |
| OW-S88 | Agent 偽造 Execution Identity |
| OW-S89 | Mutation Boundary 執行中失效 |
| OW-S90 | Precheck 通過但產生間接越區 Delta |
| OW-S91 | Precheck 與落盤之間 Generation 改變 |
| OW-S92 | 內容相同但非內容 Metadata 不同 |
| OW-S93 | Acceptance Test 內容改變 |
| OW-S94 | 相同 Source 套用不同規格 |
| OW-S95 | 不同 Generation 回到相同內容 |
| OW-S96 | 必要 Untracked Fixture 未納入 Manifest |
| OW-S97 | 跨平台路徑與 Mode 語意 |
| OW-S98 | 使用者差異與 Agent Delta 的內容相同 |
| OW-S99 | Manifest 損毀或格式版本未知 |

### 壓力

| 舊 ID | 已確認項目 |
|---|---|
| OW-P02 | 平行寫入判定 |
| OW-P03 | 路徑繞過 |
| OW-P04 | 反覆失聯與移交 |
| OW-P05 | 整合凍結競態 |
| OW-P06 | 大型工作區 |
| OW-P07 | Candidate 快速變動與遲到成果 |
| OW-P14 | Freeze 與多檔案操作競態 |
| OW-P15 | 大量 Candidate 與結果綁定 |
| OW-P16 | 長時間驗證期間持續產生新 Candidate |
| OW-P19 | Crash／timeout storm |
| OW-P21 | Candidate churn 下的 freshness 分類 |
| OW-P22 | 大型依賴圖的間接 stale 偵測 |
| OW-P27 | Mutation Admission 高競爭 |
| OW-P28 | Identity、Path 與 TOCTOU 對抗 |
| OW-P29 | 大型 Snapshot Manifest |
| OW-P30 | 大量 Generation 與 Verification Subject |

## 9. 拆分後待補

- Canonical logical resource／path model 與跨平台語意。
- Mutation boundary freeze／revoke 的後續原子狀態機。
- Shared workspace、isolated candidate 與 patch admission 的 backend 選擇。
- Dirty baseline 的安全物化與 Agent delta 分離。
- Candidate identity、manifest canonical serialization 與 digest algorithm。
- Writer stopped、candidate frozen 與 verification subject handoff。
- 規格／契約／dependency invalidation 的接收與 fail-closed 行為。
- Recovery 在共享工作區無法安全回復時的正式結果。
- 本 Subsystem 自己的完成判準與 Stress Contract。

以上仍是 gap，不構成實作決策。

## 10. 已確認的跨 Subsystem Contract

### PWC-CIM-001：Partition Activation

- CIM 只接受可驗證的 Work Package、partition、generation、trusted writer、base candidate、write resource digest 與 boundary mode。
- Boundary 進入 `boundary_active` 前，不得回報 partition 可安全施工。
- `boundary_active` 回應必須綁定完整 identity tuple。
- Provisioning 失敗、generation stale、identity mismatch 或 boundary 隨後失效時，CIM 必須回報 PWC，不能默默降級。

本 Contract 的 authority 在 Domain overview；本節只保存 CIM 的責任投影。

## 11. 已確認的跨 Subsystem Contract

### PWC-CIM-002：Writer Quiescence and Candidate Freeze

- CIM 收到 freeze request 後，先對所有目標 generations 建立 fence，再排空已核准的 in-flight mutations。
- CIM 必須納入間接 writer、shared resources、實際 touched resources 與 submitted delta admission。
- Agent claim、程序退出或 PWC 狀態都不是 quiescence 證據。
- 任一 writer 的 mutation closure 未知、外部副作用狀態未知、identity mismatch、stale generation 或未核准 delta，都不得建立 frozen candidate。單純遺失 exit code 但已證明 mutation closure 時，可以依實際 snapshot 繼續。
- `candidate_frozen` 必須綁定 immutable candidate identity 與 manifest；fence 後的遲到寫入不得改變它。
- 使用者既有差異必須在 baseline／manifest 中保持可區分。

本 Contract 的 authority 在 Domain overview；本節只保存 CIM 的責任投影。

### 已確認場景 DDH-EO-E2E-002A：Agent 宣告完成但背景 Writer 尚未停止

- CIM 必須把已核准但未結束的 operation 與 descendant writer 納入 draining。
- Writer 正常排空後，CIM 核對 touched resources 與 delta，再自動繼續 freeze。
- Drain budget 耗盡或 mutation closure unknown 時不得建立 frozen candidate。
- Fence 後的新 mutation 必須被拒絕；合法 Agent delta 與使用者 baseline 必須保留。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002B：只有部分 Writers 已靜止

- CIM 可以 seal 已達 mechanical quiescence 且通過 admission 的 partition delta。
- 只要任一目標 partition 仍 active、draining 或 unknown，就不得建立完整 integration candidate manifest。
- Sealed generation 不得恢復寫入；其合法 delta 與使用者 baseline 必須保持可區分。
- 所有目標 generations 達成 quiescence 後，才能自動建立完整 frozen candidate。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002C：工具結果未知但 Mutation 狀態可或不可封閉

- CIM 必須區分 `operation_result_unknown_but_mutation_closed` 與 `mutation_state_unknown`。
- 前者可以依完整實際 snapshot 繼續 freeze，但不能宣稱工具成功。
- 後者不得 freeze；未知外部副作用必須移交獨立高風險流程。
- Agent claim 或推測性 log 不能取代 mechanical mutation closure。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

### 已確認場景 DDH-EO-E2E-002D：Freeze Fence 與遲到寫入競態

- CIM 必須以 fence epoch 區分 fence 前已核准的 in-flight operation 與 fence 後的新 operation。
- 前者可以 draining 並納入 manifest；後者與 stale generation 必須被阻擋。
- 所有 fence 前 operations 結束前不得回報 quiescent。
- Frozen snapshot 必須 immutable；若 mutation 仍成功落入，必須使 candidate 與 verification subject 失效並進入 recovery。

完整 Given／When／Then 與測試要求以 Domain overview 為準。

## 12. 已確認的跨 Subsystem Contract

### CIM-MVE-001：Frozen Candidate to Verification Subject

- CIM 只發布綁定 immutable candidate identity 與 manifest digest 的 verification intake。
- Intake 必須同時帶入 task specification、Verification Contract、test asset manifest、environment profile 與 invalidation epoch 的 identities。
- CIM 不決定 business acceptance，也不得把 `candidate_frozen` 宣告成驗證通過。
- Candidate 在 intake 後若改變，CIM 必須產生新 candidate identity 並使舊 verification subject 失效。
- MVE 回報 identity mismatch、stale input 或必要資產缺失時，CIM 不得重用或覆寫舊 manifest 來繼續驗證。

本 Contract 的 authority 在 Domain overview；本節只保存 CIM 的責任投影。

## 13. 已確認的 Recovery Chain

### RC-PWC-CIM-001：Registered Writer Not Quiescent

- CIM 必須依 operation profile 區分仍有 progress 與 confirmed stall。
- 只可終止精確綁定 trusted writer、partition generation 與 boundary instance，且 profile 明確允許的程序。
- Termination 後必須 reconciliation；無法安全終止時 quarantine 舊 boundary 並支援 isolated candidate materialization。
- Recovery 不得破壞使用者 baseline 或放寬 mutation boundary。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-PWC-CIM-002：Stale Generation Result

- CIM 必須在 mutation／patch admission 前機械比對 generation。
- 未落地 stale request 直接阻擋；隔離 stale delta quarantine 為短期 artifact。
- Stale mutation 已落地時，立即使 candidate／verification subject 失效並 circuit-break 故障 boundary。
- Candidate 可安全重建時自動切換 isolated fresh generation；所有安全路徑耗盡才輸出一次 `platform_blocked`。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

### RC-DOM-003：Rebuildable Artifact Failure

- CIM 可以從 immutable snapshot 與固定 identity inputs 重建 candidate／snapshot manifests。
- 等價重建後自動續作；identity mismatch 時使所有 dependent artifacts／PASS 失效。
- Mutation boundary 是 active safety component，故障時不得靠重建 metadata 宣告恢復。
- Primary builder 故障時使用已驗證 fallback；不可用時才輸出單次 `platform_blocked`。

完整 transition table、業務測試與 Stress Contract 以 Domain overview 為準。

## 14. 已確認的 System Map 使用 Contract

### SMQ-001：Architecture Impact Query

- 實際 touched resources 超出 predicted closure 時，CIM 必須觸發 resource-to-node 與 reverse-dependent query。
- Query 結果用於建立 impact／Map drift candidate，不得替代 live snapshot、baseline 或 mutation authority。
- Frozen candidate 的 changed-node projection 必須引用對應 `architecture_query_result_id`，供後續 suite selection 使用。
- Index 不可用時使用 bounded live-source discovery，並依 automation continuity 自動續作。

System Map 本身的 schema、index 與 query engine 不屬於本 Subsystem 規格。
