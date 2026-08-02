# DDH Operational Telemetry and Health Model

**Contract ID：** `DDH-OBS-001`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 DDH 自身運行健康、成本與 recovery observability 語義；
不授權 runtime、collector、storage、dashboard 或 alert implementation  

---

## 1. 第一原則

DDH 必須機械觀測自己的運行狀況，及早發現 Harness、runner、queue、Context、
System Map consumer 或 recovery path 的故障與成本退化。

Telemetry 必須：

- 將 Harness／environment failure 與 product failure 分開。
- 依 capability 與任務需求局部判定 health，不用單一全域紅綠燈。
- 優先觸發已確認 recovery，不為一般工具問題建立人工 Checkpoint。
- 維持有界 retention、cardinality、storage 與 Agent Context 成本。
- 不成為 SSOT、施工授權、驗收證據、Attempt Ledger 或長期記憶。

## 2. 觀測範圍

| Subsystem／boundary | Required observations |
|---|---|
| PWC | partitions、parallel lanes、handoff、serialization、writer status |
| Context Broker | Context bytes／tokens、expansion、cache、Map query／live fallback |
| CIM | mutation boundary、blocked writes、freeze、admission、recovery |
| TAQG | inventory、admission／validity queues、suspect／stale assets、Critic workload |
| MVE | runner readiness、invocations、shards、timeouts、resource use |
| Completion | pending evaluations、invalidation、completion latency |
| OLE | Ledger backlog、prefilter、Analyzer／Critic availability、expiration |
| System Map consumer | query latency、completeness、fallback、maintenance pending |

DDH 只觀測自身對 System Map query capability 的使用狀況；System Map 內部
telemetry 仍由其獨立設計負責。

## 3. Signal Families

### 3.1 Metrics

聚合：

- active Work Packages／partitions；
- token、Context、verification compute 與 wall time；
- runner startup／rebuild latency；
- pytest pass／fail／timeout／blocked counts；
- mutation boundary violations；
- queue depth／backlog age；
- retry／fallback／recovery success rate；
- System Map query unavailable／live fallback rate；
- completion latency。

### 3.2 Structured Events

描述狀態改變，例如：

```text
partition_activated
runner_became_unhealthy
candidate_invalidated
system_map_fallback_used
ledger_expired_without_analysis
completion_published
```

Event 只作快速通知；protected transition 前仍讀 canonical current state。

### 3.3 Traces

只追蹤一次 execution 的跨 Subsystem correlation：

```text
Work Package
→ partition
→ candidate
→ test admission
→ verification subject
→ completion
→ Ledger handoff
```

Trace 不保存完整 prompt、source、diff、pytest output 或 secret。

### 3.4 Logs

Logs 必須 bounded、優先 structured、failure-oriented、secret-redacted 且短期。
Routine PASS、每次 tool call 與重複 traceback 不得默認永久保存。

## 4. Local Capability Health

Health 依 capability 與 consumer requirement 判定：

```text
PWC mutation coordination = healthy
MVE Linux runner = unavailable
MVE Windows runner = ready
OLE Analyzer = degraded
System Map query = fallback_active
```

必要語義：

| Health semantic | Meaning |
|---|---|
| Healthy | Required capability 正常 |
| Degraded | 使用 approved fallback，仍維持必要語義 |
| Unavailable | Capability 目前無法提供 |
| Unknown | Telemetry／probe 不足，不能假裝 Healthy |

Exact enum、SLO 與 thresholds 由 versioned Observability Profile 決定，但不能
合併上述差異。

同一 health 對不同任務可能有不同影響：

- OLE unavailable 不阻擋產品 completion。
- Linux-required acceptance 在 Linux runner unavailable 時 blocked。
- System Map query unavailable 但 bounded live-source fallback 足夠時可以繼續。
- 純文件任務不因無關 runner unavailable 而阻擋。

## 5. Health-to-Recovery Boundary

```text
health signal
→ stable reason family
→ confirmed Recovery Contract
→ mechanical action
→ health re-check
```

- Telemetry 只發現、分類與關聯，不自行發明 recovery。
- 沒有 confirmed safe route 時只能回報 unavailable／unknown。
- Telemetry status 不能取代 CIM quiescence、MVE result、TAQG admission、
  Completion closure 或其他 canonical fact。
- Known recovery route 自動執行；只有需要改 specification、architecture、
  risk policy、external environment 或高風險權限時才提升人類。

例：

| Signal | Route |
|---|---|
| runner crash rate 上升 | `RC-MVE-004` rebuild／approved backend fallback |
| System Map query failure | reindex；失敗後 bounded live-source fallback |
| OLE backlog full | `OLE-PROFILE-001` circuit breaker／expiration |
| writer quiescence unknown | PWC／CIM draining／isolation recovery |

## 6. Consumers

### Mechanical Recovery Controllers

消費完整 structured health signals，執行固定 recovery 並 re-check。

### Main Agent

只在目前工作受影響時取得有界摘要：

```text
affected capability
＋ current health
＋ reason
＋ automatic recovery status
＋ remaining safe routes
＋ impact on current task
```

不自動載入完整 metrics、traces 或 logs。

### OLE

只消費聚合 orchestration signals，例如 Context expansion rate、parallel-to-serial
fallback、runner profile rebuild waste 或 Map fallback rate。Telemetry 原文不得
直接成為 long-term memory，仍須經 Ledger／Analyzer／Critic。

### Human

只在 confirmed recovery routes 耗盡且影響 required capability、需要新的
architecture／specification／risk decision，或涉及 production／credential／
database／network／irreversible side effect 時通知。一般暫時工具故障不詢問。

## 7. Retention Tiers

| Data | Retention semantics |
|---|---|
| Current health／gauges | 只保存 current state |
| Metrics | bounded window，逐步 rollup／降低解析度 |
| Structured events | reconciliation 後短期刪除 |
| Traces | current execution／diagnosis 完成後刪除 |
| Raw logs | 最短 retention，診斷完成即可刪除 |
| Incident summaries | current recovery／repair 消費後刪除 |
| Long-term learning | 只能透過 OLE Memory，不保留 telemetry 原文 |

Exact durations、capacity 與 rollup 由 versioned Observability Profile 決定。
高風險 release／compliance 如需額外留存，必須由獨立規格要求。

## 8. Cardinality, Cost and Privacy

禁止：

- 每個 test ID、source path、prompt 或自由 exception message 作為長期 metric
  label。
- 每次 request／sample／tool call 永久記錄。
- 完整 traces／logs 自動注入 Agent Context。
- Telemetry 成本隨歷史 Work Packages、tests 或 logs 無界線性增長。
- Credentials、personal data、source content 或未遮罩 values 進入 labels。

要求：

- source-side aggregation；
- bounded labels；
- bounded incident exemplars／references；
- failure fingerprint clustering；
- rollup／expiration；
- sampling 可調整，但不能漏掉 mutation boundary、安全、required verification
  或 external-side-effect events。

## 9. 業務場景

### 9.1 System Map Query 故障

Workspace Domain repair 需要 reverse dependencies，但 query unavailable：

1. 標記 System Map consumer capability degraded。
2. 自動嘗試 rebuild query index。
3. 仍失敗時使用 bounded live-source discovery。
4. Impact closure 可安全完成，因此 Agent 繼續。
5. 記錄 fallback rate 與 Map maintenance pending。
6. 不建立人工 Checkpoint。

### 9.2 Runner Crash Storm

大量 pytest shards 因 runner plugin crash：

1. MVE 聚合為 runner health incident。
2. 不輸出數千份相同 traceback。
3. Circuit breaker 停止派往 unhealthy pool。
4. `RC-MVE-004` rebuild／approved equivalent backend fallback。
5. 所有 safe backends 失敗時 required verification blocked，不是 product FAIL。

### 9.3 OLE Analyzer 離線

Analyzer 離線三天：

- OLE health degraded。
- Completion、pytest 與新 Work Packages 正常繼續。
- Ledgers 依 `OLE-PROFILE-001` 有界保存與 expiration。
- Telemetry 不反覆喚醒 Agent 或消耗 current development tokens。

## 10. Stress Contract

- 數百 Work Packages、數萬 tests 同時產生 telemetry。
- Runner crash storm 不形成 log storm。
- High-cardinality input 被聚合、拒絕或轉成 bounded reference。
- Metrics storage unavailable 時 health 不能誤報 Healthy。
- Telemetry pipeline crash 時核心 safety gates 仍依 canonical state 運作。
- Duplicate／late／out-of-order events 不破壞 current health。
- Optional capability degraded 不阻擋無關任務。
- Required capability unavailable 正確阻擋相關 transition。
- Secret／personal／source content 不出現在 labels 或 Agent Context。
- Retention cleanup 不刪除 pytest Evidence、source 或 user diff。
- Routine collection、aggregation、health evaluation 與 recovery routing
  不使用 Agent／LLM。
- Telemetry 開銷有 profile 上限，不反向拖垮 DDH。

## 11. 對應機械測試

```text
test_harness_failure_never_becomes_product_failure
test_health_is_local_to_capability_and_current_task_requirement
test_unknown_telemetry_cannot_report_healthy
test_optional_ole_outage_does_not_block_product_completion
test_required_runner_unavailable_blocks_only_relevant_verification
test_system_map_query_failure_rebuilds_or_uses_bounded_live_fallback
test_health_signal_uses_only_confirmed_recovery_contract
test_telemetry_event_never_authorizes_mutation_or_completion
test_agent_receives_bounded_affected_health_summary_not_full_telemetry
test_high_cardinality_labels_are_rejected_or_aggregated
test_runner_crash_storm_clusters_logs_and_trips_mechanical_breaker
test_telemetry_pipeline_failure_does_not_bypass_canonical_safety_gate
test_retention_cleanup_preserves_tests_source_and_user_diff
test_large_telemetry_load_is_bounded_cross_platform_and_zero_agent
```

## 12. Self-Evolution Boundary

OLE 可以提出 sampling／aggregation implementation、dashboard summary、Agent
health-context selection 與已允許 recovery ordering 的改善候選，但不能自行修改：

- measurement definitions；
- Health／SLO thresholds；
- required safety events；
- recovery safety boundary；
- completion／acceptance／risk policy；
- human escalation conditions；
- compliance retention；
- System Map、Task Specification 或 permission authority。
