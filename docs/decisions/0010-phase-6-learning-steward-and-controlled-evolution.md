# Decision 0010: Phase 6 Learning Steward and Controlled Evolution

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 6建立非阻塞、短期、有界的Attempt Ledger處理、長期編排Memory與受控
self-evolution。Learning Steward不得成為completion critical path，也不得修改
Task Specification、architecture、scope、risk、pytest oracle、verification
threshold、completion logic、human escalation或external authority。

## Terminal Handoff

```text
execution terminal
├─ publish terminal result immediately
└─ seal Attempt Ledger
   → asynchronous Learning Steward handoff
```

Analyzer、Critic、queue、storage或Memory unavailable不撤銷或延遲產品結果。
Ledger storage不可用時有界retry/fallback後可回報`learning_input_unavailable`並
繼續。

每個實際產生attempts的execution run有一份Ledger。Terminal後再次施工建立新
run／Ledger，不重開sealed Ledger。

## Ledger Boundary

Ledger只保存bounded orchestration facts：execution／spec／scope／risk／profile
identity、Agent／template／Context versions、partition／generation、attempt
sequence、cost、failure fingerprint、recovery route、new-information signal與
terminal outcome。

不得保存full prompt／conversation、chain of thought、source diff、workspace
copy、unbounded output、duplicate traceback、secret或無證據Agent心得。Ledger
不是acceptance evidence或permanent audit log。

## Zero-Agent Prefilter and Pending Policy

每份sealed Ledger先由零Agent prefilter：

- routine success、one-off product/test defect → consumed／delete；
- known pattern without change → bounded support observation／delete；
- new／repeated orchestration signal → bounded pending candidate；
- unsafe boundary／recovery signal → high priority；
- prefilter unknown → bounded mechanical repair。

Evolution Profile固定maximum pending age／bytes／items、model token budget、
batch size與priority weights。Pending最終必須analyzed、consumed或
`analysis_expired_without_memory_change`並刪除；P0／P1也不能永久保存。

Decision 0023進一步固定MVP bootstrap profile：Individual Ledger、聚合後的
Learning Candidate與Long-term Memory三層分離；source Ledger上限64 KiB，
成功fold後最遲24小時刪除。P0／P1／P2／P3採不同事件、重複與批次觸發，
Candidate最長分別保留90／30／14／7天。這些預設只能由明確核准的版本化
Evolution Profile修改。

## Long-term Orchestration Memory

只允許白名單內的編排經驗：

- parallelization／partitioning；
- initial／expanded Context；
- Agent／tool profile choice；
- integration／handoff sequence；
- approved recovery ordering；
- summary／Context template；
- parallel-to-serial fallback。

每條Memory有immutable version、applicability、recommendation、prohibited uses、
support／counterevidence、confidence、profile compatibility、expiration、
conflict與rollback。

Memory query只在planning、Context materialization／expansion、repartition、
integration／handoff與合法recovery-route selection等orchestration transitions
執行。Main Agent只收bounded Guidance Cards，可拒絕但不能直接修改Registry。
Child Agent不讀Memory Store。Store unavailable時採single-main-Agent、bounded
initial Context、no optional parallelism baseline。

## Controlled Evolution

```text
Analyzer candidate
→ zero-Agent policy validation
→ independent Critic
→ offline replay
→ shadow evaluation
→ bounded low-risk canary
→ promote／reject
→ continuous monitoring
→ rollback on regression
```

Analyzer、Critic、Trial result writer與Registry publisher必須分離execution
identity、Context與write zones。Candidate author不能修改replay corpus、expected
metrics或trial results。

Promotion需要policy、Critic、Replay、Canary、metric improvement、
counterexample handling、reproducibility與rollback readiness全部成立。Rollback
只影響orchestration Memory，不能回滾product source、pytest、Candidate或user
diff。

## Acceptance

Phase 6必須證明：

- Completion不等待Learning Steward；
- routine prefilter／priority／expiration／cleanup為零Agent；
- backlog、storage、age與token有界；
- Memory只包含編排白名單；
- Main／Child Agent無法越權讀寫Registry；
- Memory unavailable安全fallback；
- Candidate不能self-promote；
- independent Critic、Replay、Canary與Rollback可重跑；
- regression自動suspend Memory，不影響產品Candidate；
- raw Ledgers／trial artifacts最終刪除。
