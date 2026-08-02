# Legacy ADAD Capability Migration Matrix and DDH MVP Plan

**狀態：** Proposed for item-by-item human confirmation  
**日期：** 2026-08-02  
**規範效力：** 現況盤點、遷移提案與實作前計畫；不授權 runtime、schema、
CLI、hook、System Map 或 migration implementation  
**Legacy evidence source：** `C:\Users\chris\Desktop\project\ADAD`

---

## 0. 邊界與證據狀態

本文件回答三個問題：

1. legacy ADAD 的哪些能力值得帶入 DDH。
2. 能力應如何脫離 Frozen Task、Source Lock、Checkpoint、System Map SSOT 與
   permanent evidence chain。
3. DDH 的最小可信端到端流程與施工順序為何。

本次盤點直接讀取 legacy ADAD 的 current working tree、設定、測試與文件。該
working tree 位於 `development` branch，且包含大量 tracked modifications、
untracked source、tests、Checkpoint 與設計文件。因此：

- 它可證明目前存在的實作與測試意圖。
- 它不能被描述成乾淨 release、已部署版本或已核准 current baseline。
- 本次沒有執行 legacy pytest；不能宣稱這些測試目前 PASS。
- 沒有修改 legacy ADAD、其 Git 設定、Task、Source Lock、Checkpoint 或
  System Map。

靜態 inventory 顯示：

- 74 個 `tests/**/*.py`，其中 72 個為 `test_*.py`。
- 約 1,045 個 `test_*` functions。
- 171 處 `pytest.mark.parametrize`、16 處 `temporary` marker 與 6 處
  `regression_backlog` marker。
- canonical workflow scripts 同時出現在 `adad_source`、`.agents` 與 packaged
  `adad_cli/resources` projection。
- Canonical workflow共有58支Python scripts、約26,639行；其中
  `adad_core.py`單檔約7,264個非空行。這個耦合量支持「抽取能力」而非整體搬移。
- 測試量最大群組集中於 Task lifecycle、Source Lock、submission evidence、
  recovery barrier 與 reviewer chain；test count 本身不構成遷移理由。

約 669／1,045 個 tests 直接集中在 Task、Source Lock、Checkpoint／receipt、
Map-SSOT 與相關 authority chain。相反地，現有測試沒有證明真正的
latency、throughput、p95／p99、CPU、memory、soak、pytest-benchmark、
property-based 或 xdist stress profile；少量多執行緒與 payload size boundary
不能被描述成各 DDH Subsystem 的成本效益式壓力驗證。

本次另執行 legacy managed-asset parity check。結果為 FAIL：

- canonical `adad_source/.../read_context.py` 與 `.agents`／package replica 不同。
- 因此 asset sync 是值得移植的能力與失敗場景，不是「目前 replicas 已同步」
  的現況證明。
- 現有 `_copy_tree()` 使用 remove-then-copy，不具 atomic apply 與 crash
  preservation，不能直接移植。

Legacy CI 目前只執行 Ubuntu／Python 3.12。雖然存在 Windows／Unix-like path、
quoting、temp、encoding 與 process unit tests，三平台 runtime parity 尚未被
CI 證明。

### 0.1 必須修正的 legacy capability claims

唯讀 source audit 顯示，下列能力不能按legacy文件名稱直接宣稱為硬性保證：

1. **PreToolUse不是跨Agent mutation lock。** 它主要安裝於Claude Code；
   Codex `apply_patch`不會觸發。部分解析／Task mechanism例外會fail-open。
2. **Pre-commit不是不可繞過邊界。** `git commit --no-verify`可跳過，且多個
   parse／tool unavailable路徑採best-effort skip。
3. **Source binding缺失可能使gate不執行。** `unbound`可以只是soft結果，主要
   staged-file gate依賴非空binding map。
4. **Isolation workspace不等於execution sandbox。** 它建立／複製workspace，
   但不能機械阻止Agent從原工作樹寫入，也沒有network／credential／DB隔離。
5. **Verification runner只有cwd／temp／process isolation。** 它可繼承environment、
   允許project cwd，不能宣稱任意command沒有external side effect。
6. **Output cap只存在於部分display layer。** subprocess result仍可能持有完整
   stdout／stderr；DDH必須在drain／protocol層限制bytes。
7. **Current loop runner不是完整autonomous executor。** 單node CLI、
   scheduler tests與實際dispatch adapters之間存在drift。
8. **Legacy System Map v1 library未形成可用產品閉環。** bootstrap diagnostic
   指向不存在的migration CLI，且package list未包含該subpackage。
9. **`deployed`只是Map治理state。** 現有release advance沒有真實deployment
   executor，不能作部署證據。
10. **部分installer failure最後仍回報success。** DDH asset／adapter setup需要
    typed partial-success、automatic retry與capability health，不可把工具缺口
    留給Agent臨場查錯。

## 1. 遷移判定原則

### 1.1 四種判定

| 判定 | 意義 |
|---|---|
| 保留 | 能力語意與主要機械核心適合 DDH；仍須去除 legacy authority coupling |
| 規格包化 | 能力只在 Task Specification／Work Package、風險或特定 execution profile 適用時啟用 |
| 替換 | 保留業務目的，但使用已確認的 DDH Contract 重新實作 |
| 淘汰 | 目的已不適用，或其成本／錯誤 authority 高於保留價值 |

「保留」不代表直接複製 source。任何 legacy code 只有在其 input、output、
failure semantics、business scenarios 與 tests 重新被 DDH 規格接受後，才可
選擇性移植。

### 1.2 不遷移 authority

下列內容不因 legacy 存在 source、schema、test、receipt 或 Checkpoint 而取得
DDH authority：

- System Map 的 architecture SSOT／task authorization 語意。
- Frozen Task snapshot 與 Task state machine。
- Source Lock 或 repository-wide evidence lease。
- CP-1／CP-2／CP-3／CP-4 的逐關人工 lifecycle。
- stable cross-version entity／contract identity 與 global freshness chain。
- permanent provenance receipt、evidence sealing 與 proof-recovery control plane。
- `task_index.json` 或其他 discovery metadata 的授權語意。

## 2. Legacy ADAD 能力盤點與遷移矩陣

### 2.1 任務、權限與編排

| Legacy capability | 現有證據與主要行為 | 判定 | DDH 歸屬與理由 |
|---|---|---|---|
| Frozen single-node Task snapshot | `generate_task.py`、`adad_task.py`、`task_schema.json`；固定單一 node、source hash、status 與 submission lifecycle | 替換 | `SPEC-WP-001`：human-confirmed Task Specification 是 SSOT；Work Package 是可重建 execution projection，可選 Module、Subsystem、Domain、Model 或多 node scope |
| Task lifecycle state machine | `assigned → in_progress → submitted → approved/rejected/blocked` 與大量 rollback／audit tests | 淘汰 | 不建立永久 Task control plane；各 Subsystem 只保留 owned local state，terminal result 由 Completion Evaluator 判定 |
| `task_index.json` | `adad_task.py index`；README 已承認只供 discovery／scheduling | 淘汰 | DDH 不需要 Frozen Task index；未來 run discovery 若需要，只能是 Telemetry projection |
| Source Lock | `.agents/tasks/.source_locks`、`source_lock_repository.py`、audit／prune／reconcile；同 source 一次只准一個 Task | 替換 | PWC＋CIM 的 conditional partition／mutation boundary；只有平行或共享資源時啟用，不以單檔作常態 ownership |
| Repository evidence barrier | acquire／record／release、repository-wide winner 與 recovery semantics | 替換 | CIM candidate freeze、writer quiescence、generation 與 TOCTOU-safe handoff；不得把整個 repo 常態鎖成治理 prerequisite |
| Per-Task authorized write set | `task_write_set_policy.py`、workspace comparator 與 outside-scope rejection；legacy policy要求恰好一個source | 保留 | Work Package projection 產生多node／multi-lane bounded resource set；CIM 作真正 mutation admission，prompt 白名單只作說明 |
| PreToolUse state gate | `adad_pretooluse_gate.py`；主要綁Claude hook，Codex `apply_patch`不觸發，部分exception fail-open | 替換 | 只阻擋 invalid Task Specification／Work Package、明顯越界 mutation 與未授權 external side effect；未機械覆蓋的平台不得聲稱強制 |
| Pre-commit architecture gate | staged source、map state、invariants、verification；可被 `--no-verify` 繞過，部分dependency failure best-effort skip | 替換 | 保留 CI／local guard 作 defense-in-depth；主要 authority 位於 runtime mutation boundary、candidate reconciliation 與 MVE，不把 Git hook 當唯一安全邊界 |
| CP-1～CP-4 Checkpoints | architecture、environment、module review、schema update、architecture optimization；完整 YAML audit | 替換 | 一次確認 Task Specification version；一般實作／測試／修復自動續作，只在 L3 authority change 或獨立 external high-risk flow 詢問人類 |
| Fixed self-fix limit then human review | README 定義 bounded retry 後停止進 CP-2 | 替換 | Automation Continuity、budget、no-progress 與 exception contract；工具／runner 問題走固定自動 recovery route，只有 policy／authority 缺口升級 |
| Fixed role chain／reviewer loop | architecture、planner、implementer、reviewer、verifier profiles 與 reviewer receipts | 替換 | 單一主 Agent 預設；PWC 只在獨立性、寫入重疊、Context、整合成本、收益、風險與預算支持時派工 |
| Parallel scheduler | scheduler claim、dead-owner recovery 與 bounded role authority tests | 保留 | 重寫為 PWC partition／fork-join／central integration；不得沿用 Task claim 或 Source Lock authority |
| Blocked report | packaged blocked-report schema／MCP reporter | 保留 | 對應 `DDH-RISK-001` structured exception；報告只描述 evidence、缺口、選項與所需 authority，不是 approval |

### 2.2 架構、Scope、Context 與影響分析

| Legacy capability | 現有證據與主要行為 | 判定 | DDH 歸屬與理由 |
|---|---|---|---|
| System Map architecture SSOT | `system_map.md` 編譯 `system_map.yaml`；node state、source hash、task gate 與 cascade 依此運作 | 淘汰 | Decision 0002：System Map 只是不具 authority 的 actual architecture index |
| Map compile／state transition／cascade dirty | `compile_map.py`、`transit_state.py`、`analyze_cascade.py` | 淘汰 | DDH 不維護 planned／dirty／validated／deployed architecture lifecycle；currentness 與 Map maintenance 由獨立 System Map 設計負責 |
| Architecture query／context projection | `read_context.py` 讀 target、dependency interface、references，並有 deterministic／bounded tests | 替換 | Context Broker 使用 branch-bound actual-only Map query；conflict／stale／unavailable 時對 affected scope 作 bounded live-source fallback |
| Source binding resolution | file／function binding、duplicate binding、target resolver | 規格包化 | 可作 actual source-location confirmation 與 mutation resource resolution；不能把 Map binding 當 permission |
| Dependency／Domain boundary check | `check_domain_boundary.py`、declared dependencies、cross-domain tests | 保留 | 以 Task Specification contracts、actual Map relations 與 live source 重新實作，供 impact closure、verification expansion 與 architecture exception detection |
| Executable invariants | denied imports／calls、function-level source 與 no-op behavior | 保留 | 轉為 architecture／coding／security Harness；由 fixed policy 或 Task Specification 引用，不綁 node lifecycle |
| Complexity／algorithm gate | compile 時對高複雜度 node 要求 algorithm metadata | 替換 | 改為 risk／verification／partition input；不能因靜態 complexity 自動創造 expected behavior 或要求人工 Checkpoint |
| System Map query usage enforcement | legacy 有 index/read-context 能力，但 workflow 可跳過；README 也承認 PreTool 不保證先讀 context | 替換 | `SMQ-001` 固定 fork 前、actual diff 後、join／higher-layer failure 等 query trigger，且 downstream partition／context／suite selection 必須消費結果 |
| Branch／worktree binding | legacy workspace evidence有 repository／worktree identity，但 Map authority與 branch view未分離 | 替換 | `DDH-OPS-001`：query 綁 exact branch、resolved commit、worktree/candidate 與 Map view；branch change 使 projection 失效，query-only switch 不等於 checkout |

### 2.3 驗證、測試資產與工作區安全

| Legacy capability | 現有證據與主要行為 | 判定 | DDH 歸屬與理由 |
|---|---|---|---|
| AST must-have assertion verification | `verify_implementation.py`／`verify_against_spec.py` 支援 named callable、AST assertion | 規格包化 | 可成為 V1 static／structural suite；不能替代 business pytest 或 higher-layer acceptance |
| Empty verification semantics | Legacy `no verification defined` 可成為成功 no-op | 淘汰 | DDH只允許規格明示且可追溯的 `not_applicable`；缺少required executable acceptance必須是`verification_not_ready` |
| Executable `case` verification | function input／expected result、exceptions 與 fixtures | 保留 | MVE runner primitive；由 TAQG admitted test asset／Verification Contract 決定是否 required |
| `command` verification | argv、cwd、expected exit、explicit 1–300s timeout、`shell=False` | 保留 | `MVE-PROTO-001`／`MVE-RUN-001` 的可重用 runner primitive |
| Multi-step `integration_case` | ordered steps、fail-fast、shared isolation workspace | 保留 | 支援 Subsystem／Domain business workflow，但需要新的 subject／result protocol，不沿用 Task snapshot |
| Verification fixture resolver | path containment、Windows／Unix-like absolute path、UNC、duplicate input、invalid JSON tests | 保留 | TAQG 管 test asset；MVE materialize fixed fixture identity，禁止 traversal 與 candidate mutation |
| Pytest isolated basetemp | owned two-layer temp root、unowned explicit root、failure preservation、cleanup safety；不提供network／credential／DB isolation | 規格包化 | 依 V profile／risk／tool health 啟用；不是每次完整 isolation。保留 fail-closed cleanup 與 diagnostic workspace，外部副作用另走trusted boundary |
| Timeout／process-tree termination | process group／Windows Job Object、bounded drain、timeout cleanup | 保留 | MVE runner 必要能力；infrastructure failure 自動 recovery，不改驗收 |
| UTF-8／portable subprocess | `platform_io.py`、fallback decode、Windows／Unix-like hook command tests | 保留 | MVE cross-platform environment contract；正式 runner 不依 Agent 驅動，可重跑 |
| Output bounding／failure diagnostics | legacy只在部分diagnostic display裁切；runner result仍可保存完整stdout／stderr | 替換 | `MVE-OBS-001`：在subprocess drain／protocol層做byte cap，成功只保留摘要，失敗cluster／excerpt有界 |
| Workspace status／baseline／delta | status reader、file evidence、baseline comparator、dirty worktree與 outside-scope tests | 保留 | CIM baseline＋actual mutation inventory；保護使用者既有 diff、發現越界與 scope 漏估 |
| Canonical delta／evidence codecs | deterministic encoding、UTF-8 ordering、size bounds、alias／cycle rejection | 規格包化 | 僅在需要 deterministic identity／protocol 的 projection 使用；不建立 permanent receipt chain |
| Preserve diff on failure／reject | `preserve_diff`、failed isolation workspace、hashes | 保留 | candidate／diagnostic safety；禁止自動 reset／delete，不要求永久 Attempt evidence |
| Verification subject/result binding | legacy frozen evidence、identity observer 與 semantic receipts | 替換 | CIM fixed candidate → MVE immutable subject → typed result → `MVE-VERDICT-001`；只保留 current identity binding，不搬 permanent provenance |
| Semantic reviewer independence | `semantic_spec_reviewer.py`、reviewer loop、closed result／replay tests | 替換 | TAQG independent Critic、anti-weakening、replay／mutation probe；Reviewer 不可修改 Task Specification 或自行發布 PASS |
| Pytest quality／lifecycle | legacy 主要證明 runner與治理工具，沒有完整 active／stale／superseded、quality dimensions與防放寬 portfolio | 替換 | TAQG `QUAL-001/002/003`：由 Task Specification 編譯 quality contract，分離 admission、semantic validity、candidate execution |
| Temporary pytest cleanup | legacy temporary tests成功後可按marker清除，並有完整cleanup lifecycle | 替換 | 探索性test可短期存在；任何支撐completion的business／boundary pytest在完成前必須admit／promote為可重跑資產，不能因PASS自動刪除 |
| Historical proof-recovery suites | proof policy、command plan、evidence comparator、frozen collector、repository barrier | 淘汰 | 只將 timeout、workspace preservation、identity mismatch、bounded output等失敗場景移入 MVE/CIM；不移植 proof receipt/control plane |

### 2.4 資產、Release、可觀測性與演進

| Legacy capability | 現有證據與主要行為 | 判定 | DDH 歸屬與理由 |
|---|---|---|---|
| Canonical managed assets | `adad_source` → `.agents`／`adad_cli/resources`，`sync_assets.py` compare／copy／idempotency；本次live parity check已發現`read_context.py` drift | 規格包化 | `DDH-OPS-001` Managed Asset Manifest、dry-run、exact parity、unmanaged-file preservation；現有remove-then-copy tree sync須替換為isolated output＋delta preview＋atomic apply |
| Package resource locator | `importlib.resources.as_file`，不依賴caller cwd並支援wheel／zip | 保留 | 可作DDH packaged resource基礎能力；仍須由Managed Asset Manifest決定authority與version |
| Project init／upgrade／backup／remove | `adad_cli/core.py`、CLI、backup與managed-file handling | 規格包化 | Repository-local reversible operations可自主；branch switch、overwrite、delete與external state依 risk／explicit authority |
| Installer partial-success semantics | legacy部分compile／Git／hook failure只warning，最後仍可能`success=True` | 替換 | DDH adapter setup需typed capability result、partial-success、retryable route與health input；缺能力時不可宣稱Harness active |
| Package build hygiene | package-data、cache exclusion、package parity tests | 保留 | 供 DDH adapters／runner packaging；canonical source與derived assets必須清楚分離 |
| Agent platform config | Antigravity／Claude／Codex assets與role config | 替換 | Adapter layer；能力聲明必須區分 prompt convention、hook coverage、sandbox enforcement 與真正 mutation mediation |
| Release candidate manifest／preflight／delivery gate | tree/blob identity、approved source hash、replica parity、preflight timeout | 保留 | 映射 `DDH-COMP-001 release_candidate` 與 `DDH-OPS-001`；不得綁 deployed node state，也不等於 deployment approval |
| Release advance to deployed Map state | `adad_release_advance.py` 推 node 到 deployed | 淘汰 | System Map 不發布治理 completion；release candidate、deployment approval與external execution分開 |
| Database／network／credential／deployment | legacy 部分透過 environment／release Checkpoint 管理 | 替換 | 獨立 external high-risk plan＋trusted executor；一般 Work Package PASS不授權執行 |
| Runtime observability／logs | observability metadata、runner diagnostics、Checkpoint／evidence files分散保存 | 替換 | `DDH-OBS-001` bounded telemetry；不成為 completion authority或永久 raw log |
| Attempt history | Task retries、Checkpoint、reviewer／recovery receipts | 替換 | OLE short-lived Attempt Ledger；terminal seal/enqueue後可供分析，整合成 memory後按 policy刪除 |
| Workflow self-evolution | legacy design／reviewer loop候選 | 替換 | `OLE-MEM-001`＋`OLE-EVOL-001`；只演進派工、Context Envelope與摘要模板，需 Critic、trial、rollback |
| Cross-platform reproducibility | Windows／Unix-like hook、temp、encoding、path、junction/reparse tests；CI目前只有Ubuntu/Python 3.12 | 保留 | MVE runner environment＋明示supported platform matrix；strict artifact decode與lossy bounded diagnostic decode分離，不得把unit tests誤稱三平台runtime parity |

## 3. 新舊流程對照

| Legacy ADAD | DDH |
|---|---|
| 人類先寫 architecture SSOT／Map node | 人類確認本次 Task Specification；System Map只查 actual architecture |
| 每個 node 核發 Frozen Task | 依人類選定層級建立 Work Package projection |
| 每個 source 常態鎖定 | 單 Agent預設不租約；平行／共享資源才啟用 partition mutation boundary |
| 固定 architecture→planner→implementer→reviewer→verifier | 主 Agent預設；只有風險收益支持才 fork |
| 每個 Module過 CP-2才釋放 | 範圍內 implementation／pytest／repair自動續作 |
| Map state／source hash／receipt決定可否提交 | current spec＋candidate＋test asset＋verification identities作當次機械判定 |
| 最多固定次數 self-fix後問人 | runner/tool自動 recovery；no-progress、budget或authority gap才 structured exception |
| PASS＋人工 approve推 deployed | MVE PASS只是 completion input；Work Package、Subsystem、Domain、Release分層獨立判定 |
| Checkpoint／receipt／proof長期保存 | pytest與必要規格是可重跑 evidence；Attempt Ledger／raw log短期保存後消化刪除 |
| Release advance改 Map治理狀態 | release candidate只代表可進高風險流程；部署／DB／network仍獨立授權 |

## 4. 最小可信端到端流程

DDH MVP 不能只展示「Agent寫完後跑 pytest」。最小可信流程必須同時證明一條
單 Agent L1 lane與一條 implementation／pytest平行的L2 lane。

> **已確認決策（2026-08-02）：** DDH MVP 必須在同一個 MVP acceptance
> package 中，同時以端到端案例證明「單代理完整施工」與「多代理平行施工／
> 整合」兩種能力。這不表示每個 L2 任務都必須平行；PWC 仍須依工作獨立性、
> 寫入重疊、耦合、Context與整合成本、預期收益、風險及預算判斷採平行、
> serial或parallel-to-serial fallback。

```text
Human confirms Task Specification vN
  → readiness checks executable expected behavior
  → Risk compiles authority class + verification profile
  → System Map query locates actual scope/impact
  → bounded live-source confirmation closes uncertain parts
  → Work Package generation is built
  → workspace baseline + mutation boundaries become active
  → main Agent executes serially, or PWC forks product/test partitions
  → agents implement, test and auto-repair inside granted boundaries
  → actual diff triggers impact-query refresh and suite closure update
  → all writers quiesce; CIM admits patches and freezes candidate
  → TAQG admits current test assets and fixes Verification Contract
  → MVE builds immutable Verification Subject and runs no-Agent pytest
  → typed result and terminal verdict are produced
  → failure routes automatically to product repair, test repair or runner recovery
  → Completion Evaluator publishes only the applicable layer result
  → terminal Attempt Ledger is sealed/enqueued; it does not block completion
```

### 4.1 MVP normal business scenarios

#### MVP-S01：單一 Module 計算修正

- Task Specification固定 input、output、rounding boundary與不變行為。
- L1＋V3，即使diff很小仍跑Module與受影響Domain pytest。
- 無scope／contract變化時，Agent自主修正直到current subject PASS。

#### MVP-S02：三個 Modules 非同步施工

- 三個Module各自生成產品code與其pytest。
- PWC只在CIM確認mutation boundary已生效後把partition標成active。
- 三條lane完成後停止writer、中央整合、固定Subsystem candidate。
- 個別Module PASS不能替代Subsystem business scenarios與stress profile。

#### MVP-S03：測試本身有bug

- TAQG分類為test implementation defect，不是產品不符合規格。
- Test repair可以自動提出，但Mechanical Acceptance Guard阻止 assertion刪除、
  expected value放寬、threshold降低、fixture縮小、case移除與新增skip／xfail。
- Independent Critic＋replay／mutation probe通過後才admit新test asset。

#### MVP-S04：影響範圍估算錯誤

- Actual diff與failure觸發System Map reverse-dependency query。
- Map不足時只對affected area做live-source discovery。
- Verification closure可在原write scope外擴張；write repair不可偷渡。
- 若scope外node需要修改，affected lane停止並提出L3 scope revision。

#### MVP-S05：工具／runner故障

- timeout、temp root、path、encoding、process cleanup或Map query backend故障，
  依固定recovery route重建runner／candidate／query fallback。
- 工具問題不得要求人類教Agent修Harness。
- 只有safe routes耗盡、authority不明或需要新policy時才升級。

### 4.2 MVP stress／failure scenarios

- 既有dirty worktree含無關使用者diff。
- implementation與test Agent嘗試交叉修改對方資產。
- late writer在candidate freeze後提交。
- branch／commit／worktree identity在query或approval後改變。
- System Map回傳stale／conflicted／incomplete結果。
- 大量pytest shards同時回傳重複traceback。
- runner timeout／crash storm與process tree殘留不確定。
- test asset在execution前被修改、標為skip或降低threshold。
- actual diff出現原scope未估到的reverse dependent。
- repeated failure沒有新假設、預算即將耗盡。

## 5. 分階段實作計畫

### Phase 0：Executable Contract Fixtures

> **已確認決策（2026-08-02）：** Phase 0 是 DDH runtime 施工前的必要規格
> 準備階段。其 authority 與完成標準記錄於 Decision 0004。
>
> **已授權施工（2026-08-02）：** Human已明確指示依確認版本開始Phase 0；
> `DDH-P0-SPEC-001` v1.0.0與Decision 0026固定原始scope。其歷史封包已
> 封存；Human後續以Decision 0029授權建立v1.1.0開發工具場景投影。授權只涵蓋
> specification scenarios、state tables、golden fixtures、traceability與
> deterministic validation，不涵蓋Phase 1或任何DDH runtime。
>
> **已完成（2026-08-02）：** 現行Phase 0 v1.1.0 package通過deterministic validator與
> independent Critic複核；完成證據記錄於
> `docs/semantic-specifications/ddh-phase-0/completion-report.md`。此狀態不
> 授權Phase 1。

**範圍**

- 將已確認Contracts轉成technology-neutral input/output examples、state tables、
  rejection cases與golden fixtures。
- 固定shared identity vocabulary，但不先固定JSON／database／message bus。
- 選出legacy tests只作需求證據，不直接搬Task／Lock／receipt fixtures。

**驗收**

- 每個跨Subsystem handoff都有正常、拒絕、失效、重試與race scenario。
- 能清楚區分prompt convention、mechanical validation、mutation enforcement與
  external authority。

**主要風險**

- 過早固定storage schema。
- 把legacy fixture欄位當成DDH authority。

### Phase 1：Single-Agent Vertical Slice

> **已確認決策（2026-08-02）：** Phase 1 是 DDH runtime 第一條正式
> end-to-end vertical slice。功能、場景、可靠性與排除邊界記錄於
> Decision 0005。

**範圍**

- Task Specification readiness、risk projection、System Map consumer adapter＋
  live fallback、Work Package generation。
- Workspace baseline、bounded write set、candidate freeze。
- 最小TAQG admission、MVE no-Agent pytest runner、typed verdict與Work Package
  completion。

**驗收**

- MVP-S01完整通過。
- 無Map backend時安全fallback，不因index工具bug阻塞安全施工。
- Dirty worktree的無關diff被保存，越界diff被拒絕。
- pytest可在無Agent情況重跑並產生同一subject的可比較結果。

**主要風險**

- mutation boundary在目標Agent平台無法真正強制。
- 規格ready但test quality不足，產生虛假PASS。

### Phase 2：Automatic Recovery and Exception Routing

> **已確認決策（2026-08-02）：** Phase 2 將scope內產品、test
> implementation、Runner、Context、stale與impact underestimation失敗導入
> fixed automatic routes；human escalation只處理authority、policy、budget
> increase與external boundary。完整決策記錄於Decision 0006。

**範圍**

- Product failure、test implementation defect、runner infrastructure failure、
  context insufficiency與impact underestimation分類。
- Bounded automatic recovery、no-progress、budget與structured exception。

**驗收**

- MVP-S03～S05不需逐關詢問人類。
- 修復不能改Task Specification、acceptance或write authority。
- Safe recovery耗盡後保留candidate／diff並回報已嘗試路徑。

**主要風險**

- failure classifier誤把產品bug當測試bug。
- retry loop消耗token而沒有新資訊。

### Phase 3：Parallel Product／Test Fork-Join

> **已確認決策（2026-08-02）：** Phase 3 是第二條MVP vertical slice，
> 證明product／acceptance-test分離、multi-Module asynchronous fork-join、
> mechanical partition activation、central integration與Subsystem verification。
> 完整決策記錄於Decision 0007。

**範圍**

- PWC risk/benefit decision、Context Envelope、partition activation、shared
  resource serialization、central patch admission、join barrier。
- implementation／pytest dual lane與three-Module asynchronous fork-join。

**驗收**

- MVP-S02與交叉寫入、late writer、handoff、shared fixture、integration failure
  scenarios通過。
- PWC只有在CIM boundary active後才發布partition active。
- 所有writer停止、candidate freeze、verification start之間沒有TOCTOU空窗。

**主要風險**

- Context載入與整合成本高於平行收益。
- partition plan漏掉shared logical resource。

### Phase 4：Full Test Asset Quality and Layered Verification

> **已確認決策（2026-08-02）：** Phase 4 建立Test Asset Catalog、
> admission／semantic-validity／candidate-execution三軸、anti-weakening、
> currentness evaluation、pytest-as-rerunnable-evidence與layer/risk calibrated
> stress。完整決策記錄於Decision 0008。

**範圍**

- Test Quality Contract dimensions/default profiles。
- admission／semantic validity／candidate execution三軸。
- stale／suspect／quarantine／superseded與independent Critic。
- Module→Subsystem→Domain→Global suite selection及成本效益式stress。

**驗收**

- test weakening對抗、stale detection、fixture/helper change、false stale與
  conditional stress applicability scenarios通過。
- higher-layer PASS／FAIL依`DDH-COMP-001`獨立判定，不向上自動冒泡。

**主要風險**

- pytest數量與portfolio成本失控。
- quality defaults過嚴，重現ADAD摩擦；過鬆則產生虛假完成。

### Phase 5：Operational Hardening

> **已確認決策（2026-08-02）：** Phase 5 建立Windows＋MVP Linux
> reproducibility、risk-based isolation、subprocess-level output bounds、
> process／temp safety、Capability Health、atomic managed assets、branch-aware
> Map consumption與non-authoritative telemetry。Runner採Adaptive Bounded
> Timeout，不使用legacy式固定短秒數。完整決策記錄於Decision 0009。

**範圍**

- Cross-platform runner matrix、bounded output、health telemetry。
- Managed Asset Manifest、dry-run sync、parity、package/upgrade safety。
- branch-mode System Map consumption與invalidations。

**驗收**

- Windows＋至少一個Unix-like環境（MVP預設Linux）重現subject semantics。
- cache、temp、junction／symlink、encoding、timeout與cleanup failure scenarios通過。
- asset sync二次執行idempotent，且不覆蓋unmanaged assets。

**主要風險**

- 平台特有process／filesystem semantics。
- Telemetry被誤當completion或authority。

### Phase 6：OLE Memory and Controlled Evolution

> **已確認決策（2026-08-02）：** Phase 6 由`Learning Steward`負責
> non-blocking terminal handoff、zero-Agent prefilter、bounded pending、
> orchestration-only Memory與Analyzer／Critic／Replay／Canary／Rollback。
> Completion不等待學習，raw Ledgers與trial artifacts最終刪除。完整決策記錄於
> Decision 0010。
>
> **已確認補充（2026-08-02）：** Decision 0023採Individual Ledger、
> Learning Candidate、Long-term Memory三層；零Agent prefilter後才聚合／
> 批次分析。MVP固定priority trigger、64 KiB source Ledger上限與分層TTL，
> 但允許未來以明確核准的版本化Evolution Profile調整。

**範圍**

- Short-lived Attempt Ledger、terminal seal/enqueue、bounded log。
- Memory Analyzer、applicability/confidence/conflict/expiry。
- Prompt／Context Envelope template candidate、Critic、trial、rollback。

**驗收**

- 任務完成不等待Analyzer。
- Raw ledger在安全消化後刪除；pytest與規格仍可重跑。
- 演進不能修改spec、scope、risk、acceptance、measurement或human escalation。

**主要風險**

- Ledger backlog、隱私與token成本。
- 自進化根據偏誤樣本優化錯誤目標。

### Phase 7：Release and External High-Risk Adapters

> **已確認決策（2026-08-02）：** Phase 7 將release candidate、exact
> operation-plan approval、Trusted Executor、external postconditions與
> uncertain-side-effect reconciliation分離。一般Work Package永遠不因PASS取得
> production authority。完整決策記錄於Decision 0011。
>
> **已確認產品化時點（2026-08-02）：** Decision 0024將Phase 7拆成MVP必備的
> 7A Contract／fixtures／deterministic simulator，以及核心MVP通過後才依需求
> 個別核准的7B real provider Adapters。7A不執行真實external write；7B不得
> 提供generic shell／HTTP escape。

**範圍**

- Release candidate evaluation。
- Database、deployment、credential、network與publication plan。
- Human approval、trusted executor、postcondition與uncertain-side-effect recovery。

**驗收**

- 一般Work Package／Domain PASS不能觸發real side effect。
- Approval綁exact branch／commit／candidate／plan；任一漂移即失效。
- uncertain execution不自動重試可能重複副作用的操作。

**主要風險**

- 把release readiness誤當deployment authority。
- 外部系統回應不確定造成重複副作用。

## 6. DDH MVP 整體完成標準

最低可稱為DDH MVP，必須同時證明：

1. Task Specification是唯一task authority，Work Package可重建且不成為第二SSOT。
2. System Map被實際查詢與消費，但stale／missing時可bounded fallback。
3. Scope內產品與pytest可以自主施工、失敗分類、修復與重跑。
4. 至少一條L1 serial與一條L2 parallel fork-join流程通過。
5. Mutation boundary是可觀察的機械能力；沒有覆蓋的平台明確標示unsupported，
   不以prompt冒充強制。
6. Current candidate、test assets、environment與verification result identity一致。
7. Pytest可無Agent重跑，且quality guard阻止同一施工者靜默放寬驗收。
8. Dirty worktree、outside-scope impact、late writer、runner crash與high output有
   固定自動route。
9. Work Package completion與Subsystem／Domain／Release／Deployment分開判定。
10. External side effect永遠不由一般Work Package PASS自動取得權限。

## 7. 實作前仍需人類決策

| 決策 | 為何必須由人類決定 |
|---|---|
| 選定哪個legacy ADAD snapshot／commit作移植參考 | **已確認：** commit `53a26b43d7fd5b0a22f93842a637dfb27b64e232`（Release ADAD 1.6.5）為主要reference baseline；dirty working tree只作secondary discovery evidence |
| DDH MVP是否必須同版交付L2 parallel，或先交L1再以Phase 3補齊 | **已確認：** 同一個MVP acceptance package必須同時證明L1 serial與L2 parallel端到端案例；個別L2任務仍可依PWC判斷採serial |
| Runtime語言、package layout與supported Agent adapters | **已確認：** language-neutral Contracts＋單一模組化Python reference runtime＋Ports／Adapters；Python最低版本為3.13，required CI驗證最低版本與最新穩定版，且目標專案runtime保持獨立。Rust／Go只在可重現、可量測且無法合理修正的能力缺口下提出，經人類核准後漸進演進；default promotion與Python retirement另行決策 |
| Mutation mediation backend | **已確認：** 第一版採local Change Guard的`Serial Reconciled`、`Guarded Shared`與`Isolated Candidate`三種模式；L1可用post-delta admission，L2使用verified containment或isolated Patch Admission。Git hook只作advisory，第一版不建立central Patch Service；mode故障自動換安全路徑，不降級為prompt-only parallel |
| Shared identity的最小欄位與wire/storage format | **已確認：** wire採UTF-8 JSON Contract Envelope v1＋JSON Schema Draft 2020-12；初始transport為isolated invocation directory＋atomic result file，digest profile採JCS／SHA-256。Identity採Versioned Authority、Lifecycle、Content、Invocation四種minimal typed references；每個handoff只綁防止stale／wrong-subject absorption所需欄位，不建立永久provenance |
| System Map consumer API readiness與branch-view最低facts | **已確認：** DDH採capability-based Consumer Port，只要求node resolution、hierarchy、direct dependency／reverse dependency、resource binding、local currentness與repository／branch／resolved commit／view binding；不固定System Map schema或backend。Candidate以baseline view＋actual delta＋bounded live discovery形成overlay，query必須被下游artifact實際消費 |
| Test Quality default profiles與threshold authority | **已確認：** 採`Static／Module／Subsystem／Domain／Global` scope layer＋independent quality add-ons＋specification-sourced thresholds；V0～V3只作歷史alias。Bootstrap只固定scenario mapping、required PASS／completeness、有效oracle、behavior change boundary／negative與new／changed asset admission，不設定全域coverage、mutation、load或soak數字 |
| Token、time、retry、context與stress budgets的default | **已確認：** Agent、Context、wall time、Verification、Recovery、Stress六本帳分離；來源為Task explicit→project profile→calibrated bootstrap。Subagent initial context約15%、全文累計30%、single grant 5%、保留50%；same no-progress不重試，有新證據可在總budget內繼續；unknown-duration一般verification預設10分鐘hard deadline，無stdout不等於hang；stress N/A時budget為零 |
| Supported platform matrix | **已確認：** MVP release-blocking為vendor-supported Windows 11 x86_64＋Ubuntu 24.04 LTS x86_64，驗證Python 3.13與latest stable；PR跑兩個OS的3.13，release跑OS×Python四格。macOS、ARM64、WSL2與其他Linux先列preview；UNC／network-share writable candidate、32-bit與vendor-EOL OS不正式支援 |
| Attempt Ledger消化排程與retention upper bound | **已確認：** 採Individual Ledger→Learning Candidate→Long-term Memory三層。Terminal立即零Agent prefilter；P0單次安全終止後排程、P1兩次或一小時、P2跨兩個Work Packages三次或每日batch、P3五次。Ledger上限64 KiB，成功fold後最遲24小時刪除；outage上限P3 24h／P2 72h／P1 7d／P0 14d。Candidate上限P3 7d／P2 14d／P1 30d／P0 90d |
| External high-risk adapters何時進產品範圍 | **已確認：** Phase 7A Contract／fixtures／deterministic simulator列為MVP必備；Phase 7B真實provider Adapter不阻塞核心MVP，須待核心acceptance通過後依實際需求、隔離target、獨立Task Specification與人類核准逐個加入。不得提供generic shell／HTTP Executor |
| Human decision owners與確認時點 | **已確認：** Demand／Architecture／Profile Policy／External Authority分離但可由同一人兼任；Main Agent只起草與編譯。L0明確請求作最小確認，L1／L2一次確認exact Task Specification，L3先確認authority change；執行中只對authority-bearing change例外升級，completion不再人工過關 |
| 正式 implementation authorization | **Phase 0已完成：** Decision 0026授權原始`DDH-P0-SPEC-001` v1.0.0，Decision 0029授權現行v1.1.0開發工具場景投影；規格資產通過deterministic validation與語意負面掃描。仍未授權Phase 1或任何DDH runtime、CLI、hook、service、System Map backend或真實external operation |

## 8. 建議核准順序

本文件不建議一次核准全部legacy source。建議依序確認：

1. 本遷移矩陣的四種判定。
2. Minimum credible MVP包含L1 serial＋L2 parallel兩條端到端案例
   （已確認）。
3. Phase 0是runtime施工前的必要規格準備階段（已確認）。
4. Phase 1單代理完整施工流程的功能與驗收邊界（已確認）。
5. Phase 2自動恢復與例外分流（已確認）。
6. Phase 3多代理平行施工與中央整合（已確認）；接續確認Phase 4。
7. Phase 4 pytest資產品質、過期管理與分層驗證（已確認）；接續確認
   Phase 5。
8. Phase 5執行環境、跨平台與營運強化（已確認）；接續確認Phase 6。
9. Phase 6 Learning Steward、短期Attempt Ledger與受控自我演進
   （已確認）；接續確認Phase 7。
10. Phase 7 Release與外部高風險操作（已確認）。
11. 進入Implementation Readiness Review，逐項關閉剩餘human decisions。
12. Legacy ADAD主要移植基準採`53a26b4`，dirty tree只作secondary discovery
    evidence（已確認）。
13. Runtime採language-neutral Contracts＋單一模組化Python reference runtime，
    長期選擇性演進Rust／Go high-assurance backends；Verification Assets
    tool-neutral，pytest只作Python reference adapter（已確認）。
14. DDH Reference Runtime最低版本採Python 3.13，required CI驗證最低版本與
    最新穩定版；目標專案runtime保持獨立（已確認）。
15. Rust／Go backend採evidence-gated evolution；先做有界Python修正，再由
    結構化證據、人類architecture approval、跨語言conformance與有限試用決定，
    不進行預定式重寫（已確認）。
16. 跨語言wire採UTF-8 JSON Contract Envelope v1＋message-specific schemas；
    初始backend transport採atomic file profile，wire不取代任務規格authority，
    也不建立永久provenance（已確認）。
17. Shared identity採四種minimal typed references；區分version、generation、
    content digest與invocation，trusted execution identity來自實際channel，
    不恢復legacy permanent identity chain（已確認）。
18. Mutation Mediation採三種local modes；L1 single-writer避免per-edit hook，
    L2 parallel以verified containment或isolated Patch Admission保護，工具故障
    自動換安全模式（已確認）。
19. System Map整合採capability-based Consumer Port；使用exact branch／commit
    actual view、candidate delta overlay與bounded fallback，不鎖死尚未落地的
    Map schema／API，且query必須被實際消費（已確認）。
20. Test Quality Defaults採scope layer＋independent add-ons，不使用單一最高
    強度階梯；high-cost checks依business facts觸發，threshold只能來自Task
    Specification或approved profiles（已確認）。
21. Budget分成六本獨立ledger；Context用relative bootstrap、Recovery依progress、
    Runner使用adaptive timeout，budget不足不得降低acceptance（已確認）。
22. MVP release-blocking平台採Windows 11 x86_64＋Ubuntu 24.04 LTS x86_64，
    並驗證Python 3.13／latest stable；其餘平台依preview／unsupported誠實分級
    （已確認）。
23. Attempt Ledger採三層learning intake、priority-based trigger與分層TTL；
    routine path零Agent刪除，模型分析不阻塞completion或借用施工預算
    （已確認）。
24. External high-risk能力採7A MVP simulator＋7B post-MVP real Adapters；
    provider整合不阻塞核心，且逐個取得獨立authority（已確認）。
25. Human authority採Demand／Architecture／Profile Policy／External分工；
    L0最小確認、L1／L2整包一次確認、L3先確認authority change，routine
    execution與completion不逐關審批（已確認）。
26. 第一次formal implementation authorization採完整Phase 0 Executable Contract
    Fixture Package；`DDH-P0-SPEC-001` v1.0.0已封存，現行v1.1.0依Decision
    0029完成開發工具場景投影，Phase 1仍未授權（已確認）。

只有上述設計核准後，才建立實作Task Specification；該規格必須再明確選定
source snapshot、scope、acceptance、tests、risk、budget與external boundary。
