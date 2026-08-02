# System Map Bundle Specification 1.1

> 中文名稱：精簡版 System Map Bundle 規格書  
> 狀態：設計草案；穩定權威邊界以 Decision 0002 為準  
> 規格版本：`1.1.0`  
> 格式識別：`system-map-bundle`  
> 取代目標：legacy `system_map.md`／`system_map.yaml`  
> 日期：2026-08-01  
> 本版取代本文件先前的 1.0 內容；移除 Frozen Task、JIT Source Ownership、
> 跨版本 stable identity／freshness、重型 evidence／recovery 與 Control Plane。

> **Authority amendment（2026-08-02）：** Decision 0002 已取代本文件中
> 「架構 SSOT」與「雙 SSOT」的權威定位。System Map 是長期維護、
> actual-only 的真實架構 index，不是 SSOT、施工授權或驗收權威。
> 本文件尚未完全落地；既有 schema、欄位、狀態、API、currentness 與更新流程
> 均屬可修訂設計。後續解讀必須先遵守 Decision 0002 的穩定語義邊界。

## 1. 文件定位

本文件描述新 ADHD 的 System Map Bundle 候選格式、載入協定、查詢邊界與
寫入邊界。其目的為形成可維護、可查詢的 actual architecture index。

1. **System Map**：索引有實作證據的系統結構、組成、位置、關係與結構完整度。
2. **任務規格書**：固定本次 Agent 目標、範圍、限制、要求行為與完成判定。
3. **長期規格與決策**：由任務規格固定引用，不由 System Map 取代。

System Map 不再承載施工任務、檔案鎖、審核收據、部署收據或跨版本身份治理。
ADHD Orchestrator 以人類指定的架構範圍為施工邊界，讀取該範圍所連結的語意規格，
自主施工與修正，直到分層驗證達到該語意規格的完成標準。

相關產品設計：

- [System Map Visualization Backend Specification v1](system_map_visualization_backend_specification_v1.md)
- [System Map Visualization UI Design](system_map_visualization_ui_design.md)
- [Entity Visual Encoding Matrix](system_map_visualization_entity_visual_encoding_matrix.md)
- [Full-screen Wireframe v1](system_map_full_screen_wireframe_v1.md)

本文件使用：

- **MUST／不得**：相容實作必須遵守。
- **SHOULD／建議**：除非有明確理由，否則應遵守。
- **MAY／可以**：可選能力；不得破壞核心不變量。

## 2. 新方向的正式取捨

### 2.1 保留

- System Map 作為長期維護的 actual architecture index。
- Project → Domain → Subsystem → Module → Internal／External Entity 的階層。
- 架構關係、來源位置、完整度與可重建 Query Index。
- 原子發布與 Bundle schema／hash 完整性檢查。
- 風險分級 Gate，但它屬於 ADHD Orchestrator policy，不是 Bundle 內的 Task Gate。
- 分層驗證，但驗證內容由語意規格與風險等級共同決定。
- Dogfood、Adoption 與 Release 可作為 Orchestrator 的後續流程。

### 2.2 移除

以下能力不屬於新 System Map，也不得透過 extension 偷渡回來：

- Frozen Task、Task snapshot、Task lifecycle 與 Task freshness。
- JIT Source Ownership、Source Lock、lease 與檔案所有權治理。
- 跨 Bundle 保持不變的 Entity／Relation stable identity。
- source revision freshness、watcher freshness barrier 與 `ensure_current`。
- Checkpoint／receipt／audit Control Plane。
- provenance evidence artifact 與逐筆 evidence identity。
- Pin、Retention、Quota、Rollback guard、Detached View 與 recovery proof。
- publication-history 作為必要治理鏈。
- contract hash、implementation hash 與依 freshness 判定的失效鏈。

### 2.3 延後

- 子代理的精準上下文投影與分工協定。
- Runtime Trace。
- 完整 Human／Agent capability matrix。
- Dogfood、Adoption、Release 的具體狀態機。

延後項目不得阻礙 System Map Bundle 核心落地。

## 3. System Map 與任務規格的邊界

```text
System Map actual architecture index
  ├─ 系統有哪些架構範圍與元件
  ├─ 階層與結構關係
  ├─ 元件位於哪些 source／schema／config
  ├─ 元件之間有哪些依賴／呼叫／資料關係
  └─ 該結構資料的 complete／partial／unknown 狀態

Task Specification
  ├─ 本次 Agent 目標與施工範圍
  ├─ 禁止事項與風險邊界
  ├─ 要解決的業務情境
  ├─ 正式行為與邊界
  ├─ invariants／exceptions／non-goals
  ├─ acceptance scenarios
  └─ 分層測試與完成標準

ADHD Orchestrator
  ├─ 接受人類確認的 task specification scope
  ├─ 以 System Map 加速定位並以 live assets 確認現況
  ├─ 依風險選擇施工與驗證強度
  ├─ 自主施工、測試、診斷與修正
  └─ 達標後呈報結果；架構或語意規格改變時才要求人類決策
```

不變量：

- System Map 不是 SSOT、施工授權、風險核准或驗收權威。
- Active view 只包含有實作證據的 actual architecture；planned／proposed／
  declared-only 內容不得冒充 actual。
- 本次任務規格書是本次 Agent 目標與完成判定的 SSOT。
- System Map 可以引用語意規格書；不得把自由文字規格複製成第二份。
- Query Index、UI projection 與 Agent context 都是可重建投影，也不是 SSOT。
- System Map 與 live assets 衝突、局部 currentness 不足或結果 unavailable 時，
  DDH 對受影響範圍使用 bounded live-source discovery。
- 風險判定與測試結果不寫回 Entity／Relation。

## 4. 產品目標

新 System Map 必須：

1. 讓 Human UI、Agent、MCP 與 ADHD Orchestrator 讀取同一個 Active Bundle。
2. 不依賴 LLM 記憶維持架構資料一致。
3. 支援完整階層與多類型架構關係。
4. 正式區分 zero、unknown、partial、not applicable 與 query omission。
5. 支援從 Bundle 完整重建 Query Index。
6. 已發布 Bundle immutable；寫入只能產生新 Bundle 並原子切換 Active。
7. 不保存 Secret、UI state、Runtime event、Task、Lock、Checkpoint 或測試結果。
8. 正常啟動只讀新 Config＋Bundle，絕不 fallback 到 legacy System Map。

## 5. 資料流

```text
Formal Architecture Authoring／Source Adapters
                         ↓
SystemMapRepository Authoring Transaction
                         ↓
Validated Immutable System Map Bundle
                         ↓
Atomic Active Pointer
                         ↓
Rebuildable Architecture Query Index
                         ↓
Human UI／Agent／MCP／ADHD Orchestrator
```

Legacy System Map 只允許由顯式 migration importer 讀取，不屬於正常資料流。

## 6. Project Root 與檔案配置

Project Root 只由 `system-map.config.json` 識別：

```text
<project>/
├─ system-map.config.json
├─ .system-mapignore
├─ .system-map/
│  ├─ active.json
│  ├─ bundles/
│  │  └─ <bundle_id>/
│  │     ├─ manifest.json
│  │     ├─ entities.jsonl
│  │     ├─ relations.jsonl
│  │     ├─ relation-coverage.jsonl
│  │     └─ omissions.jsonl              # 有 omission 時
│  ├─ indexes/
│  │  └─ <bundle_id>.sqlite3
│  ├─ diagnostics/
│  └─ staging/
└─ semantic-specifications/
```

路徑規則：

- Bundle path MUST 是 project-relative 或 Bundle-relative normalized path。
- 不得包含 `..`、絕對路徑、使用者 home path或外部 filesystem URI。
- `.system-map/bundles/<bundle_id>/` 發布後不得原地修改。
- `.system-map/indexes/`、`diagnostics/`、`staging/` 是可重建 runtime data。
- 不建立 `.system-map/control/`。

## 7. `system-map.config.json`

```json
{
  "format": "system-map-project-config",
  "config_schema_version": "1.1.0",
  "project": {
    "project_id": "prj_adhd",
    "name": "ADHD"
  },
  "storage_root": ".system-map",
  "required_bundle_schema": "1.x",
  "authority_profile": "ssd-dual-ssot-v1",
  "semantic_spec_roots": [
    "semantic-specifications"
  ],
  "adapters": []
}
```

規則：

- `project_id` 是專案設定值，用於避免不同專案資料混用；它不是跨版本 Entity identity。
- `semantic_spec_roots` 只能指向 project 內的 normalized relative path。
- Config 不得包含 Secret、Task policy、Source Lock policy 或 receipt location。
- Config schema 或 Bundle major version不支援時啟動 fail closed。

## 8. 唯一啟動載入協定

ADHD、UI Backend、Agent Service 與 MCP 必須共用同一個 `SystemMapBootstrap`。

### 8.1 啟動順序

```text
0. 載入內建 Schema Registry
1. 向上尋找 system-map.config.json，確定 Project Root
2. Strict UTF-8 解析並驗證 Config
3. 讀取並驗證 .system-map/active.json
4. 讀取 Active manifest
5. 驗證 artifact path、size、record count、SHA-256 與 Schema
6. 驗證 Entity／Relation／Coverage／Omission integrity
7. 開啟相同 bundle_id 的 Index；缺失或不符時只從 Bundle re-index
8. 原子建立 Ready Snapshot，供所有 consumer 共用
```

### 8.2 啟動狀態

| 狀態 | 條件 | 行為 |
|---|---|---|
| `ready` | Config、Active Bundle 與 Index 有效 | 開放讀取 |
| `reindexing` | Bundle 有效但 Index 缺失／損毀／版本不符 | 只從 Bundle 重建 |
| `migration_required` | 無新 Config／Bundle但偵測到 legacy map | 只允許 migration preview／import |
| `uninitialized` | 新舊格式皆不存在 | 要求 `system-map init` |
| `blocked` | Config／Active／Bundle 無效或 schema 不支援 | 不提供猜測結果 |

不再有 legacy 的全域 Bootstrap `stale`、`degraded` 或 rollback 狀態。
這不排除未來以局部 evidence binding 表達 currentness、semantic conflict 或
observation unavailable；其資料模型與狀態名稱尚待 System Map 設計確認。

### 8.3 明確禁止

- 不得因 Config、Active 或 Bundle 損毀而讀取 `system_map.md`／`system_map.yaml`。
- 不得因 Bundle 無效而切換到 previous Bundle。
- 不得跳過 artifact hash／Schema 驗證後直接開 SQLite。
- 不得在 Bootstrap 完成前向不同 consumer 暴露不同版本。
- 不得由任何 legacy ADAD loader 繞過 `SystemMapBootstrap`。

## 9. Schema Registry

公開 Schema Registry 至少包含：

```text
schemas/system-map/1.1/
├─ project-config.schema.json
├─ active.schema.json
├─ manifest.schema.json
├─ entity.schema.json
├─ relation.schema.json
├─ relation-coverage.schema.json
└─ omission.schema.json
```

要求：

- 使用 JSON Schema Draft 2020-12。
- 核心 record 預設 `additionalProperties: false`。
- Python models、TypeScript types、CLI validation 與 fixtures 必須由同一 Registry
  產生或驗證。
- Bundle Schema、Index Schema、Query API 與 Semantic Specification Schema 分開版本。
- 不提供 Task、Source Lock、Checkpoint、Governance 或 Provenance schema。

## 10. `active.json`

```json
{
  "format": "system-map-active-pointer",
  "schema_version": "1.1.0",
  "project_id": "prj_adhd",
  "active_bundle_id": "sha256:...",
  "active_index": {
    "path": "indexes/sha256-....sqlite3",
    "index_schema_version": "1.0.0",
    "bundle_id": "sha256:..."
  }
}
```

規則：

- `active_bundle_id` 與 `active_index.bundle_id` MUST 相同。
- 只有 Candidate Bundle 與 staging Index 完成驗證後才能原子切換。
- 發布失敗時 Active 不變。
- Active 不保存 previous Bundle、時間、source revision、approval 或 rollback metadata。

## 11. Bundle Manifest

```json
{
  "format": "system-map-bundle",
  "bundle_schema_version": "1.1.0",
  "bundle_id": "sha256:...",
  "hash_algorithm": "sha256",
  "canonicalization_version": "sm-jcs-jsonl-1",
  "project": {
    "project_id": "prj_adhd",
    "name": "ADHD",
    "root_entity_id": "ent_project"
  },
  "generator": {
    "name": "adhd-system-map",
    "version": "1.0.0"
  },
  "artifacts": [],
  "capabilities": [],
  "completeness": {
    "overall": "partial",
    "dimensions": {
      "hierarchy": "complete",
      "relations": "partial",
      "source_bindings": "complete",
      "semantic_spec_links": "partial"
    },
    "omissions_artifact": "omissions.jsonl"
  },
  "statistics": {
    "entity_count": 0,
    "relation_count": 0,
    "relation_coverage_count": 0,
    "omission_count": 0
  }
}
```

### 11.1 Artifact Descriptor

每筆 descriptor 必須包含：

- `role`
- `path`
- `media_type`
- `schema_ref`
- `record_count`
- `byte_length`
- `sha256`
- `required`

Required roles：

- `entities`
- `relations`
- `relation_coverage`
- 有 omission 時的 `omissions`

Manifest 不包含 semantic hash、source snapshot、provenance、publication history、
previous Bundle、runtime diagnostics 或 legacy ADAD governance extension。

## 12. Canonicalization 與 Bundle Integrity

### 12.1 文字與 JSON

- 所有文字 artifact MUST 使用 UTF-8、無 BOM、LF。
- JSON 不得有 duplicate key、NaN 或 Infinity。
- 每個 JSONL record 使用單行 canonical JSON，不得有空白 record。
- Object key 依 Unicode code point lexicographic order排序。
- set-semantics array 必須去重並確定性排序。

### 12.2 Record 排序

| Artifact | Primary sort key |
|---|---|
| `entities.jsonl` | `entity_id` |
| `relations.jsonl` | `relation_id` |
| `relation-coverage.jsonl` | `coverage_id` |
| `omissions.jsonl` | `omission_id` |

Primary key 在單一 Bundle 內必須唯一。

### 12.3 Bundle-scoped ID

- `entity_id`、`relation_id`、`coverage_id`、`omission_id` 只保證在單一 Bundle 內唯一。
- Reader 不得假設同一 ID 在下一個 Bundle 仍代表同一物件。
- Rename、Move、Split、Merge 可以改變 ID，不需要 continuity receipt。
- Writer 可以使用 deterministic path／hierarchy projection 產生 ID，以利相同輸入重建；
  但此規則只服務可重現建置，不形成跨版本 identity authority。
- 跨 Bundle diff 可以用 name、location、hierarchy 進行 best-effort matching，
  結果必須標示為 comparison heuristic，不得作 Gate 或授權依據。

### 12.4 Bundle ID

1. 先產生 canonical artifact bytes 與各自 SHA-256。
2. 建立不含 `bundle_id` 的 canonical Manifest projection。
3. 依 artifact role／path 排序 hash descriptor。
4. 對 projection 計算 SHA-256，得到 `bundle_id`。

`bundle_id` 是 Bundle bytes 的完整性位址，不是 Entity lifecycle、Task freshness 或
跨版本合約 identity。

## 13. Entity Record

```json
{
  "entity_id": "ent_generate_task",
  "project_id": "prj_adhd",
  "entity_kind": "module",
  "entity_type": "tool",
  "name": "generate_task",
  "architecture_role": "code_structure",
  "role_subtypes": ["workflow_tool"],
  "technologies": [
    {
      "name": "Python",
      "kind": "language"
    }
  ],
  "locations": [
    {
      "locator_id": "loc_source",
      "kind": "source_code",
      "path": "src/generate_task.py",
      "language": "python"
    }
  ],
  "spec_refs": [
    {
      "path": "semantic-specifications/development-orchestrator.md",
      "section": "generate-task-replacement"
    }
  ],
  "facets": {},
  "completeness": {
    "overall": "complete",
    "omission_refs": []
  },
  "sensitivity": "internal",
  "policy_labels": [],
  "extensions": {}
}
```

Required fields：

- `entity_id`
- `project_id`
- `entity_kind`
- `entity_type`
- `name`
- `architecture_role`
- `role_subtypes`
- `technologies`
- `locations`
- `spec_refs`
- `facets`
- `completeness`
- `sensitivity`
- `policy_labels`
- `extensions`

Entity 不再包含 `identity`、`provenance_refs`、contract hash、lifecycle、Task status、
Source Lock 或 Checkpoint。

### 13.1 Entity Kind

封閉列舉：

- `project`
- `domain`
- `subsystem`
- `module`
- `internal`
- `external`
- `unresolved`

一個 Bundle 必須恰好有一個 Project Entity，且 Manifest 的 `root_entity_id`
必須指向它。

### 13.2 Location

Location kind：

- `source_code`
- `database`
- `api_contract`
- `configuration`
- `logical`

Location path 必須 project-relative；可帶 symbol、language、line range。
Location 不得包含 credential、Token、private key 或本機使用者目錄。

### 13.3 Semantic Specification Reference

`spec_refs` 只保存：

- project-relative `path`
- 可選的 `section`
- 可選的 `schema_ref`

規則：

- System Map 不複製規格正文。
- 指向不存在檔案或不存在 section 時，Bundle completeness 至少為 `partial`。
- 一個 Entity 可以引用多份規格；同一規格也可覆蓋一個架構 scope。
- 規格內容變更不靠 System Map freshness hash 判定；Orchestrator 每次施工讀取
  人類確認的任務規格及其固定引用，並把 System Map 當作 actual index 使用。

## 14. Relation Record

```json
{
  "relation_id": "rel_module_depends_on_repository",
  "project_id": "prj_adhd",
  "source_entity_id": "ent_module",
  "target_entity_id": "ent_repository",
  "directionality": "directed",
  "relation_type": "depends_on",
  "category": "dependency",
  "facets": {},
  "completeness": {
    "overall": "complete",
    "omission_refs": []
  },
  "assertion_kind": "observed",
  "sensitivity": "internal",
  "policy_labels": [],
  "extensions": {}
}
```

Required fields：

- `relation_id`
- `project_id`
- `source_entity_id`
- `target_entity_id`
- `directionality`
- `relation_type`
- `category`
- `facets`
- `completeness`
- `assertion_kind`
- `sensitivity`
- `policy_labels`
- `extensions`

Actual-only invariant：

- Active view 中的 Relation 必須有目前實作的觀測證據。
- `declared` 若在後續設計中保留，只能表示尚未進入 Active actual view 的 proposal，
  或採用更細粒度模型後的 authored semantic field；不得讓 declared-only Relation
  成為 actual architecture。
- `assertion_kind` 的最終 enum、evidence binding 與 field-level authority
  仍由後續 System Map 規格決定。

Relation 不包含 stable identity 或 provenance refs。

Core relation types：

- `contains`
- `depends_on`
- `calls`
- `reads`
- `writes`
- `references`
- `imports`
- `implements`
- `extends`
- `exposes`
- `publishes`
- `consumes`
- `routes`
- `protects`
- `deploys_to`
- `runs_on`
- `connects_to`

規則：

- 正式方向固定為 source → target。
- Relation endpoint 必須存在；未知端點使用 `unresolved` Entity。
- Project Root 無 incoming `contains`。
- 每個非 Project Entity 恰好有一條 incoming `contains`。
- `contains` graph 必須無環且全部可由 Project Root 抵達。
- parent、children、reverse adjacency、path 與 aggregate count 都由 Index 衍生。

## 15. Relation Coverage 與 Omission

Coverage 用於區分：

- 已確認零筆關係。
- 已知部分關係。
- 關係未知。
- 關係不適用。

```json
{
  "coverage_id": "cov_module_outgoing_dependencies",
  "project_id": "prj_adhd",
  "entity_id": "ent_module",
  "direction": "outgoing",
  "relation_types": ["depends_on"],
  "scope": {},
  "status": "complete",
  "reason_code": "formal_authoring_complete",
  "extensions": {}
}
```

規則：

- `status` 為 `complete`、`partial`、`unknown` 或 `not_applicable`。
- Relation count 為 0 且 Coverage complete 時，才能回答正式 zero。
- `partial` 回傳所有已知 Relation，數量語意為「至少 N」。
- `unknown` 或缺少 Coverage 時不得把無 edge 解讀為零。
- 缺漏資料以 Omission record 描述，不用 provenance receipt。
- Omission 至少保存 subject、reason code、affected fields 與可否重新分析。

## 16. Authoring Transaction

所有寫入必須透過 `SystemMapRepository`：

```text
begin_transaction(base_bundle_id)
  → apply_patch
  → validate_candidate
  → build_index
  → publish
  → abort
```

禁止功能模組直接修改 Manifest、JSONL artifact、Active 或 SQLite table。

Authoring Patch 至少包含：

- `base_bundle_id`
- operations
- optional human rationale

Operations：

- upsert／remove Entity
- upsert／remove Relation
- set Relation Coverage
- set／resolve Omission
- update semantic specification references

規則：

- `base_bundle_id` 不等於目前 Active 時回報 conflict，不得 last-write-wins。
- Candidate 必須通過 Schema、hierarchy、endpoint、coverage、path、Secret 檢查。
- 發布是單一 writer、stage → validate → index → atomic Active switch。
- 不建立 Task、Source Lock、Checkpoint、receipt 或 rollback guard。

## 17. Architecture Query Index

Index 是指定 Bundle 的可重建 projection，最低能力：

- Entity ID／name／alias／path／source location lookup。
- FTS search。
- parent／children／ancestors／descendants。
- adjacency／reverse adjacency。
- relation direction／type／category filter。
- Relation Coverage lookup。
- spec reference lookup。
- child／descendant／incoming／outgoing aggregate count。
- bounded neighborhood。
- Human render projection。

Index metadata MUST 保存：

- `bundle_id`
- `index_schema_version`
- `bundle_schema_version`
- `project_id`
- build integrity state

規則：

- metadata 與 Active Bundle 不符時拒絕混用並 re-index。
- Index 可以刪除後只靠 Bundle重建。
- FTS token、reverse edge、canonical path、closure、aggregate count 與視覺群組都是衍生資料。
- 不在 Index 保存 Task、Lock、Checkpoint、freshness 或測試結果。

## 18. QueryService 與 Consumer Policy

Human、Agent、MCP 與 Orchestrator 使用同一 QueryService。

最低查詢：

- Entity lookup。
- Search。
- Hierarchy。
- Adjacency／reverse adjacency。
- Relation type／direction。
- Group statistics／pagination。
- Agent bounded context。
- explicit zero／unknown／partial／omitted。
- semantic specification links。

每個 request 必須指定 Bundle version；cursor 綁定 `bundle_id`。
Active 改變後舊 cursor 失效，是 query snapshot isolation，不是架構 freshness Gate。

MVP local single-user 可以讓 Human 與 Agent 使用相同架構可見範圍；
Secret 對所有 consumer 都不可見。精準子代理 context policy 延後定義。

## 19. 風險 Gate 的整合邊界

風險分級是新 ADHD 核心，但不存成 System Map lifecycle：

```text
Human selected architecture scope
  + current System Map structure
  + linked semantic specifications
  + proposed change set
                         ↓
Risk Classifier
                         ↓
required implementation／verification policy
```

規則：

- 風險以實際變更範圍、語意影響、資料／安全／部署後果判定。
- `complexity` 不等於風險。
- 未知風險採較高驗證要求。
- 低風險可由 Orchestrator 自主修正與推進。
- 架構範圍、語意規格或不可逆高風險行為改變時，才要求人類決策。
- Risk result 是單次開發循環的 policy input，不寫入 Bundle Entity 或 Relation。

## 20. 自主施工與分層驗證邊界

System Map 只提供架構範圍；施工循環由獨立 ADHD Orchestrator 規格定義：

```text
Select architecture scope
  → load linked semantic specifications
  → classify risk
  → plan within scope
  → implement
  → fast structural/static checks
  → behavior and invariant tests
  → integration and boundary tests
  → independent semantic verification when required
  → diagnose and auto-correct
  → repeat until acceptance standard is met
```

分層驗證至少區分：

1. 結構／Schema／靜態邊界。
2. 單元行為與 invariants。
3. 跨模組／跨 Domain integration。
4. 語意規格 acceptance scenarios。
5. 依風險追加的安全、資料遷移、效能或部署驗證。

此循環不使用 Frozen Task、Source Lock 或 stable freshness。子代理的寫入約束由
Orchestrator 的中央 patch application、scope policy 與驗證層控制；具體協定另定。

## 21. Search、Projection 與 UI State Boundary

以下只存在 Projection／Client State：

- Star Map layout、Camera、LOD、renderer profile。
- Mind Map layout、collapse、focus。
- Hover、Click、Pinned、Current Focus、Search Preview。
- panel width、mode controls、loading／error。
- Aggregate Group、merged routes、viewport culling。

這些資料不得寫入 Bundle。

## 22. 錯誤與最低行為

| Failure | Required behavior |
|---|---|
| Config invalid | `blocked`；不猜 project root |
| Bundle schema 不支援 | `blocked` |
| Active pointer invalid | `blocked`；不得 legacy／previous fallback |
| Artifact missing／hash mismatch | Bundle invalid；不開 Index |
| Candidate invalid | 不發布，Active 不變 |
| Index missing／corrupt／ID mismatch | 從 Active Bundle re-index |
| Equal-authority structure conflict | Candidate invalid |
| Query budget exceeded | partial＋omission metadata |
| Semantic spec link missing | scope partial；Orchestrator 不得宣稱語意驗證完成 |

所有 diagnostics 必須移除 Secret 與本機敏感 path。

## 23. Legacy Migration

Migration 是顯式一次性流程：

```text
legacy preflight
  → strict parse／field inventory
  → migration preview
  → Entity／Relation／Coverage conversion
  → semantic specification link mapping
  → omission／conflict report
  → Candidate Bundle＋Index
  → structural parity verification
  → explicit cutover
```

規則：

- Migration 不直接覆寫或刪除 legacy files。
- Preview 必須列出 transformed、derived、dropped、unknown 與 conflicting fields。
- Legacy hierarchy、dependency、source 與 description 可進 System Map。
- Legacy input/output/invariant/verification 等行為契約應遷入語意規格書，不嵌入 Entity。
- Legacy state、todo、checkpoint、Task、Lock、fan-in snapshot、known symbols 不遷移。
- 不建立 stable ID mapping。
- 相同 legacy input 與 importer version SHOULD 產生相同 Bundle bytes。

### 23.1 Cutover Gates

1. Public Schema Registry 與 fixtures 通過。
2. Legacy field inventory 全部被分類。
3. Entity／Relation／Coverage／Omission integrity 通過。
4. 語意欄位已遷入語意規格或明確列為尚未遷移。
5. Query Index 可完全重建。
6. 啟動只載入 Config＋Bundle，不讀 legacy map。
7. legacy map 存在、缺失或損毀時，正常 runtime 行為皆不改變。
8. Windows 與主要支援平台的 path／atomic switch 測試通過。

### 23.2 Retirement

Cutover 後：

- `system_map.md`／`system_map.yaml` 不再是 Live SSOT。
- Legacy compiler、direct reader與 mtime staleness gate 退出正常啟動流程。
- Legacy importer 可以保留為離線工具。
- 不永久維護 legacy map 與新 actual architecture index 兩套競爭中的架構資料。

## 24. Legacy ADAD Rewrite Mapping

| Legacy component／behavior | New responsibility |
|---|---|
| `ADADCore` 直接讀 YAML | `SystemMapBootstrap`＋`SystemMapRepository` |
| `compile_map.py` | 顯式 legacy importer；正常 authoring 改走 Repository |
| `validate_schema.py` | Schema Registry＋Bundle Validator |
| `read_context(node_name)` | QueryService 依當前 Bundle 查詢 scope |
| `resolve_target_file` | Resolve parent Entity／authoring scope |
| `analyze_cascade` | Relation／reverse adjacency query |
| `transit_state` | 移除；System Map 不保存 lifecycle |
| `generate_task`／Task snapshot | 移除；Orchestrator 直接接受 architecture scope |
| `.source_locks`／Source ownership | 移除；改由中央 patch application 與 scope policy 約束 |
| Checkpoint／receipt／audit | 不屬於 System Map；不遷移 |
| `task_index.json` | 移除，不作 Graph 或開發流程 SSOT |
| `fan_in_snapshot` | Index derived aggregate |
| `known_symbols` | Adapter／Index cache |
| PreToolUse YAML root discovery | 只找 `system-map.config.json` |
| resume YAML scan | QueryService scope summary |
| contract hash／freshness | 移除 global freshness chain；依任務規格固定引用，並對受影響範圍查詢 actual index／live assets |

所有重寫後架構讀寫必須經 Repository／Query boundary；不得把 JSONL 當成另一份
可任意手改的 YAML。

## 25. 最小施工順序

1. 建立 1.1 Schema Registry 與 canonical JSON／hash library。
2. 建立 Config、Bootstrap、Manifest、Entity、Relation、Coverage、Omission validator。
3. 建立 immutable Bundle Repository、Active pointer 與 publication transaction。
4. 建立 read-only Query Index：lookup、hierarchy、adjacency、reverse adjacency、spec refs。
5. 建立 legacy importer preview 與 loss-visible report。
6. 建立 task specification reference 與 actual-index binding validation。
7. 將所有正常 startup／reader 改接 Bootstrap／Repository／QueryService。
8. 驗證 legacy 檔存在時仍不會被正常 runtime 讀取。
9. 再另行設計 architecture-scope Orchestrator、risk policy 與高保證 verification。

本順序不建立或恢復 Task、Source Lock、Checkpoint、stable identity、freshness 或
evidence／recovery infrastructure。

## 26. Conformance Checklist

Reader／Writer 宣稱 System Map Bundle 1.1 相容前必須證明：

- [ ] Strict UTF-8／LF／canonical JSON／JSONL。
- [ ] Schema Registry version negotiation。
- [ ] Bundle-scoped ID 唯一，無跨版本 identity 假設。
- [ ] Artifact hash 與 Bundle ID 可重現。
- [ ] 唯一 Project Root 與合法 `contains` tree。
- [ ] 無 dangling Relation endpoint。
- [ ] Relation＋Coverage 正確區分 zero／partial／unknown／not applicable。
- [ ] Omission 不被空值或猜測取代。
- [ ] Immutable publication＋Active／Index atomic pairing。
- [ ] Index 可只靠 Bundle 完整重建。
- [ ] semantic specification links 可驗證且不複製正文。
- [ ] legacy migration deterministic、loss-visible。
- [ ] 正常啟動不讀 legacy System Map。
- [ ] Secret、絕對路徑、UI／Runtime／Task／Lock／Checkpoint state 不進 Bundle。
- [ ] 沒有 provenance、freshness、rollback 或 recovery dependency。

## 27. 延後且不阻礙 Bundle 核心的項目

- Python model／TypeScript type codegen 工具。
- SQLite exact DDL 與 benchmark tuning。
- Source Adapter parser package。
- QueryPolicy Human／Agent capability matrix。
- 精準子代理 context projection。
- Architecture-scope autonomous Orchestrator 詳細規格。
- 風險分級 policy matrix。
- 高保證分層驗證與 semantic verifier 詳細規格。
- Dogfood、Adoption 與 Release state machine。
- Runtime Trace 與測試視覺化。

這些後續規格不得重新引入 Frozen Task、JIT Source Ownership、跨版本 stable identity、
freshness chain 或重型 evidence／recovery Control Plane。若未來確有新的業務需求，
必須以新架構提案說明必要性，不得以 legacy 相容為理由默默恢復。
