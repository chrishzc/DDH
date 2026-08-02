# Memory Evolution, Critic Trial and Rollback Contract

**Contract ID：** `OLE-EVOL-001`  
**狀態：** Confirmed Functional Design／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 Memory Candidate、Critic、Replay、Canary、Promotion 與
Rollback 語義；不授權 runtime、model provider、trial scheduler 或 Registry
implementation  

---

## 1. 第一原則

Analyzer 只能提出 Candidate；Critic 不能修改 Candidate；Trial Controller 執行
回放與試用；Memory Registry 只依完整機械結果發布 immutable active version。

```text
Analyzer proposal
→ mechanical policy validation
→ independent Critic
→ offline replay
→ shadow evaluation
→ bounded canary trial
→ promote／reject
→ continuous monitoring
→ rollback on regression
```

同一個 Agent／execution identity 不得同時成為 Candidate 作者、Critic、Trial
result writer 與 Registry publisher。

## 2. Candidate Triggers

只有以下 confirmed signals 可以形成 Candidate：

- 多個 Ledgers 顯示相同 partition／Context／handoff 問題；
- repeated no-progress／budget waste；
- active Memory 的有效 counterexample；
- Agent／Context／tool profile version change；
- Operational Telemetry 顯示 orchestration strategy 持續退化；
- active Memories 形成無法機械解決的 material conflict；
- prompt／Context template change gate。

單一 product bug、一次 assertion failure、自由文字 Agent 偏好或沒有 observed
evidence 的心得不能形成 Candidate。

## 3. Candidate Content

```text
candidate identity
memory type
base memory version

proposed change
applicability
expected orchestration effect
prohibited uses

support evidence
counterevidence
profile compatibility

evaluation metrics
replay plan
canary scope
rollback conditions
```

Candidate 不包含 full Ledger、conversation、prompt、source、diff、raw logs 或
secrets。

## 4. Mechanical Policy Validation

進入 Critic 前，零 Agent validator 阻擋：

- 非 `OLE-MEM-001` 白名單 Memory Type；
- 修改 Task Specification／scope／risk／acceptance；
- 修改 pytest oracle／threshold／measurement logic；
- 修改 human escalation；
- 新增 external-side-effect permission；
- Child Agent讀取 entire Memory Store；
- 缺少 applicability、counterevidence、evaluation 或 rollback；
- Analyzer 直接寫 active Registry。

Policy validation failure 不能由 Critic prompt 解釋後放行。

## 5. Critic Independence

Analyzer 與 Critic 必須有：

- different execution identities；
- isolated Context；
- separated candidate／evaluation write zones；
- candidate author 無法修改 replay corpus、expected outcomes 或 trial results；
- Critic 無法修改 Candidate 使其通過。

Critic 只能回傳：

- `accept_for_replay`
- `reject`
- `revise_and_resubmit`
- `insufficient_evidence`

Exact enum 可調整，但語義不能合併。Evolution Profile 可對較高影響的 candidate
要求不同 model／profile；核心機械保障是 identity、Context、write boundary 與
evaluation data separation，不能只依賴 prompt。

## 6. Offline Replay

Replay corpus 包含：

- supporting cases；
- counterexamples；
- same-shape baseline cases；
- scope／risk／profile boundary cases；
- Memory conflicts；
- Context budget pressure；
- parallel write overlap；
- degraded Agent／System Map／tool capability。

只使用 de-identified Task Feature Envelopes、orchestration decisions 與 bounded
outcome metrics，不使用產品規格正文或完整對話。

Replay 檢查：

- applicability；
- profile compatibility；
- false-positive task matching；
- scope／permission／verification invariants；
- expected orchestration metric；
- counterexample exclusion。

## 7. Shadow Evaluation

Candidate 可以在真實任務計算 shadow recommendation，但不影響 actual plan：

```text
actual plan uses active Memory／baseline
candidate computes shadow plan
→ compare decisions and predicted effects
```

Shadow 只驗證 applicability 與 decision differences，不能宣稱已證明真實改善。

## 8. Bounded Canary Trial

通過 replay 後只在 profile 允許範圍試用：

- low-risk、recoverable task shapes；
- bounded Work Package percentage／count；
- no production／external side effect；
- no L3 architecture／schema／public contract；
- no verification reduction；
- immediate baseline fallback available。

Canary count、duration、scope、metrics 與 thresholds 由 versioned Evolution Profile
固定，Analyzer 不能即席決定。

## 9. Promotion

全部成立才能 promotion：

1. Policy validation PASS。
2. Critic accepts replay。
3. Replay 無 authority／safety violation。
4. Canary 不降低 completion quality 或 required verification。
5. Expected orchestration metrics 相較 baseline 改善達 profile 門檻。
6. Counterexamples 已由 applicability 排除或處理。
7. Results 跨 execution runs 可重現。
8. Rollback route 已驗證。

Promotion 建立 immutable active Memory version，不覆寫舊版本。

## 10. Rollback

Rollback 只影響 orchestration Memory，不回滾 product source、tests、candidate 或
user diff。

Triggers：

- scope／permission／acceptance guardrail violation；
- integration conflicts 顯著上升；
- Context／token cost 超過 regression threshold；
- completion latency、retry、no-progress 退化；
- new counterexample 證明 applicability unsafe；
- Agent／tool profile change；
- trial effect 無法可靠量測。

```text
active candidate
→ suspended
→ Resolver stops selection
→ previous compatible version or fixed baseline
→ new analysis candidate
```

Guardrail violation 立即停用。一般 metric regression 依 profile 的樣本與門檻。
已 materialize 的 Task Specification／scope／candidate／acceptance 不因 rollback
改變；current execution 只在安全 replan transition 才重新查詢 Memory。

## 11. Human Boundary

白名單內、low-risk orchestration improvement 可經 Critic／Trial 自動 promotion。

需要人類：

- 新 Memory Type；
- baseline safety policy change；
- Risk Gate／measurement definition／promotion threshold authority change；
- Memory 影響 specification／scope／permission／acceptance；
- Canary 擴大至 L3／external-side-effect flow；
- human escalation condition change。

## 12. Artifact Retention

Candidate、replay、shadow、trial 與 Critic artifacts 只保留到 promotion／reject／
insufficient-evidence／rollback decision 被目前流程可靠消費。

- Active Memory 只保留 `OLE-MEM-001` 定義的 bounded evidence／counterevidence
  summaries。
- Rejected candidate 可以留下有期限 suppression summary，不能保留 full
  Ledger／corpus。
- Trial logs、raw metrics 與 model conversations 不成為 long-term Memory。
- Decision 後短期 artifacts 依 profile 刪除，不建立永久 evolution receipt chain。

## 13. 業務場景

Candidate 建議跨 Module state-machine 任務替 Test Agent初始 Context 加入公開
data-contract 摘要：

1. Offline replay 20 個 de-identified cases。
2. Shadow 確認只影響 matching tasks。
3. 五個 low-risk Canary Work Packages。
4. Context expansion 平均五次降到一次。
5. Initial Context tokens 增加 10%，total Context tokens 降低 20%。
6. Verification、scope、integration conflicts 無退化。
7. Candidate promotion。

之後 Agent profile 已自動提供相同摘要，Memory 造成 duplicate Context。
Telemetry 偵測 regression，Registry suspend 該版本，Resolver 回 baseline，建立
重新評估 Candidate。

## 14. Stress Contract

- Candidate flood 不繞過 Critic／Trial。
- Analyzer 無法 self-promote。
- Candidate author 無法修改 replay corpus。
- Critic／Trial crash 不產生 promotion。
- Corpus 有矛盾案例時保留 counterevidence。
- Shadow improvement、Canary regression 不 promotion。
- Noise 與 persistent regression 可由 profile 區分。
- Multiple simultaneous promotion／rollback deterministic。
- Agent／tool profile 在 trial 中改版會 invalidates trial。
- Registry unavailable 維持 current compatible version或 baseline。
- Rollback storm 不影響 product candidate。
- Candidate／replay／trial artifacts 有界且決策後刪除。
- Routine validation、routing、monitoring、rollback 的 Agent token cost 為零。

## 15. 對應機械測試

```text
test_analyzer_cannot_publish_or_self_promote_memory
test_policy_validation_blocks_non_whitelisted_or_authority_changing_candidate
test_critic_identity_context_and_write_zone_are_separate
test_candidate_author_cannot_modify_replay_corpus_or_trial_result
test_replay_includes_support_counterexamples_boundaries_and_degraded_cases
test_shadow_result_cannot_claim_real_improvement
test_canary_excludes_l3_and_external_side_effects
test_promotion_requires_policy_critic_replay_canary_and_rollback_readiness
test_guardrail_violation_immediately_suspends_memory
test_metric_regression_uses_fixed_profile_threshold
test_rollback_changes_orchestration_memory_not_product_artifacts
test_profile_change_invalidates_incompatible_trial
test_evolution_artifacts_delete_after_decision_without_permanent_receipt
test_candidate_flood_and_rollback_storm_are_bounded_and_zero_agent
```

## 16. Self-Evolution Boundary

OLE 可改善白名單 Memory Candidate，但不能修改自己的 type whitelist、policy
validator、Critic independence、replay corpus authority、Canary safety scope、
promotion threshold authority、rollback guardrails、measurement logic 或 human
escalation conditions。

