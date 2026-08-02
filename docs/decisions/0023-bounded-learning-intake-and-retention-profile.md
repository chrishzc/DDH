# Decision 0023: Bounded Learning Intake and Retention Profile

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH 將自進化輸入分為三層，避免把 Attempt Ledger 變成永久 log 或讓每次
execution 都啟動模型：

1. `Individual Attempt Ledger`：單一 execution run 的有界結構化事實。
2. `Learning Candidate`：相似 Ledgers 經零 Agent 機械聚合後的短期候選。
3. `Long-term Orchestration Memory`：通過 Analyzer、獨立 Critic、Replay／
   Trial 後才可發佈的版本化編排記憶。

Learning Candidate 只保存 normalized pattern、applicability、support／
counterevidence counts、cost summary 與必要最小例證，不得成為原始 Ledgers
的壓縮副本。

## Non-blocking Intake

每個 execution terminal 時立即 seal Ledger，並在不阻塞 terminal result 的
情況下執行零 Agent prefilter：

```text
terminal result published
→ Ledger sealed
→ mechanical prefilter
   ├─ routine／one-off product failure → consumed and deleted
   ├─ known pattern without change → bounded support update and deleted
   └─ orchestration signal → atomically fold into Learning Candidate
                              → delete Individual Ledger
```

Analyzer、Critic、queue 或 Memory unavailable 不得撤銷 completion、阻止新
Work Package，或消耗目前施工的 Agent／Context／Verification budget。

## Bootstrap Trigger Profile

| Priority | Initial model-analysis trigger |
|---|---|
| P0 | 單次 unsafe mutation／recovery／permission／scope 或 evolution regression；目前 mutation transaction 安全終止後立即排程 |
| P1 | 相同可比較 pattern 出現 2 次，或最長等待 1 小時 |
| P2 | 至少跨 2 個 Work Packages 且累積 3 次，或每日 idle／maintenance batch |
| P3 | 累積 5 次；未達門檻不建立專用 model call，只能隨已排定 batch 處理 |

System restart 時可以進行非阻塞 catch-up。Storage pressure 可以提早執行既有
batch，但不能降低 evidence threshold、改變 priority、借用 active Work Package
預算或逐 Ledger 呼叫模型。

上述數值是 DDH MVP bootstrap profile，不是不可演進的架構常數。專案可以用
明確核准、版本化的 Evolution Profile 改寫；Main Agent、Analyzer、Critic 與
單次 Work Package 均不得即席修改。

## Retention Upper Bounds

### Individual Attempt Ledger

- 單份 serialized Ledger hard cap：64 KiB。
- `routine_no_orchestration_signal`、`known_pattern_no_change` 與一次性產品／
  測試實作錯誤：prefilter terminal disposition 後立即刪除。
- 成功 atomically fold into Learning Candidate：立即可刪除，最遲 24 小時。
- 尚未成功 fold／prefilter 的 outage upper bound：
  - P3：24 小時；
  - P2：72 小時；
  - P1：7 天；
  - P0：14 天。

超過 64 KiB 時，重複 attempts、tracebacks、metrics 與 tool events 必須由零
Agent deterministic aggregation／truncation 處理，同時保留 classification、
count、first／last occurrence、new-evidence、cost 與 truncation facts。

### Learning Candidate

| Priority | Maximum age |
|---|---:|
| P3 | 7 days |
| P2 | 14 days |
| P1 | 30 days |
| P0 | 90 days |

Maximum age 是 Analyzer／Critic outage 或證據不足時的最終上限，不是正常保存
目標。到期後必須得到 `analysis_expired_without_memory_change`，刪除 candidate
與短期 artifacts；P0／P1 也不能永久保存。

## Deletion and Memory Boundary

- Individual Ledger 在「完整機械 disposition」或「成功 atomic fold」後刪除。
- Learning Candidate 在 promoted、known-no-change、rejected、
  insufficient-evidence、superseded 或 expired 等 terminal learning
  disposition 後刪除。
- Crash 發生在 disposition／fold 與 deletion 之間時，cleanup 必須 idempotent；
  不得重複增加 support count 或重複啟動分析。
- Long-term Memory 保存自足的 normalized evidence summary、support／
  counterevidence counts、applicability、confidence、version、失效與衝突規則；
  不保存 raw Ledger、完整 log 或會因 Ledger 刪除而失效的必要引用。
- 不建立永久 deletion receipt。Operational telemetry 只能留下不含個別 Ledger
  內容的有界 aggregate health metrics。

## Business Scenarios

### Repeated Context Expansion

三個相似 Context expansion 分布於至少兩個 Work Packages 時，Individual
Ledgers 被聚合成 P2 Learning Candidate。Analyzer 提出 Context Envelope
調整，Critic 回放成本與越界讀取風險；只有驗證通過才發佈新 Memory version，
之後刪除 Candidate。

### Unsafe Recovery

一次 recovery 嘗試可能破壞 mutation boundary 時即成為 P0。系統先安全終止
目前 mutation transaction，再立即排程分析；產品 terminal result 不等待。

### Analyzer Outage

Analyzer 離線時，routine Ledgers 仍由零 Agent prefilter 刪除，相似 signals
仍可聚合。Restart 後非阻塞 catch-up；任何 material 最終依 priority TTL
expire，不形成永久 backlog。

## Acceptance

- 每個 sealed Ledger 都先經零 Agent prefilter。
- Routine execution 不產生 model call。
- Individual Ledger 與 Learning Candidate 的 lifecycle、TTL 與 deletion 分開。
- Atomic fold 後刪除 source Ledger 不會遺失 applicability、反例或支持計數。
- P0 優先但不阻塞 completion，也不永久保存。
- Same candidate 不因 crash／restart 重複計數或重複分析。
- Evolution budget 與 active Work Package 六本帳分離。
- 長期 Memory 不依賴已刪除 Ledger 才能解讀或失效。

