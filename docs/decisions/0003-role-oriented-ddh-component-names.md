# Decision 0003: Role-oriented DDH Component Names

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH 使用下列人類可讀的角色名稱描述執行與治理責任：

| Canonical role name | Historical design name／ID |
|---|---|
| `Work Coordinator` | Parallel Work Coordination／PWC |
| `Change Guard` | Candidate Integrity and Mutation／CIM |
| `Context Curator` | Context Broker |
| `Test Auditor` | Test Asset Quality Governance／TAQG |
| `Verification Runner` | Mechanical Verification Execution／MVE |
| `Completion Judge` | Completion Evaluator／`DDH-COMP-001` |
| `Learning Steward` | Orchestration Learning and Evolution／OLE |

後續人類討論、架構圖與新文件優先使用 canonical role name。既有 Contract ID、
scenario ID、檔名與歷史引用可保留原縮寫，避免破壞 traceability；它們不再是
首選顯示名稱。

## Role Does Not Mean Agent

角色名稱描述責任，不固定 runtime placement，也不表示每個角色都由獨立 LLM
Agent 執行。

- `Work Coordinator` 可由主 Agent 加固定協調規則組成。
- `Change Guard` 必須以機械 mutation boundary 為主，不能只靠 prompt。
- `Context Curator` 可包含 deterministic query／budget logic 與主 Agent 決策。
- `Test Auditor` 可包含機械 guard 與獨立 Critic。
- `Verification Runner` 應是無 Agent 驅動、可重複執行的 runner。
- `Completion Judge` 應依 canonical current facts 作機械判定。
- `Learning Steward` 可使用獨立模型分析，但不能修改規格、權限或驗收。

## Responsibility Separation

- `Test Auditor` 判斷測試資產是否可信，不執行後自行修改標準。
- `Verification Runner` 執行 admitted tests，不修改測試資產。
- `Completion Judge` 消費驗證與 closure facts，不核准 external side effects。
- `Work Coordinator` 安排工作與整合，不授予超出 Task Specification 的權限。
- `Change Guard` 執行寫入與 Candidate 安全，不決定 expected behavior。

## Non-decision

本決策不固定 class、package、process、service、Agent、schema、CLI 或 wire-format
名稱，也不授權重新命名 runtime source；目前尚無 runtime implementation。
