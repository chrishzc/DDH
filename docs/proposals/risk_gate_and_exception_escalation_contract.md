# Risk Gate and Exception Escalation Contract

**Contract ID：** `DDH-RISK-001`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 Change Authority、Verification Intensity、動態重分類與
exception escalation 語義；不授權 runtime、classifier、schema 或 external action  

---

## 1. 第一原則

Change Authority 與 Verification Intensity 是兩條獨立軸：

```text
Change Authority Class：能否自主修改
Verification Intensity：需要多強的驗證
```

低權限風險不代表低業務驗證。一行 financial rounding 可以是 L1 change，但
需要 Domain／high-assurance verification。

## 2. Change Authority

### L0：Non-behavioral Work

- documentation；
- non-governance asset cleanup；
- formatting／organization without runtime behavior；
- read-only analysis 不算施工。

使用 user goal 作 minimal Task Specification，direct modification＋lightweight
confirmation。碰到 behavior、governance、contract 或 external side effect 時立即
reclassify。

### L1：Localized Change within Existing Contracts

- confirmed scope；
- one primary Module／Model／node；
- architecture responsibility unchanged；
- schema／public／data contract unchanged；
- no external side effect；
- reversible；
- bounded write／impact closure；
- no shared multi-writer integration。

Task Specification confirmed 後自主 implementation、test、repair、review 與
completion，不逐關人工確認。

### L2：Cross-node Change within Existing Contracts

- multiple Modules／Subsystem／Domain internal work；
- parallel product／pytest construction；
- shared-state／integration coordination；
- large internal refactor with observable contracts unchanged；
- Candidate、Join Barrier、stronger isolation／regression closure。

仍不得修改 architecture responsibility、schema／public／data contract、expected
behavior 或 external-side-effect authority。Task Specification confirmed 後自主
施工與整合。

### L3：Human Decision Required

任一成立：

- architecture boundary／responsibility change；
- database schema／data contract；
- public API／cross-module contract；
- expected behavior／acceptance；
- write scope expansion；
- security／permission／risk policy；
- irreversible operation；
- production／deployment／credential／network／real database；
- user budget increase；
- confirmed safe routes exhausted and new policy required。

L3 confirmation 只允許建立新的 Task Specification／dedicated flow，不自動授權
production side effect。External operations 仍需獨立高風險流程。

依Decision 0025，L0的明確人類修改要求可以是最小確認；L1／L2確認一次exact
Task Specification version後自主施工；L3由相應Architecture／Demand authority
先確認變更。Main Agent、System Map、prompt或risk classifier不能代替human
authority source。

## 3. Verification Intensity

Decision 0020將獨立Verification Profile正式拆成：

```text
Static／Module／Subsystem／Domain／Global scope layer
＋ independent quality add-ons
＋ specification-sourced product thresholds
```

既有V0～V3只保留為歷史alias，不再作single severity scale。External lane仍是
real side-effect dedicated verification／human control。

決定因素：

- Task Specification scenarios；
- changed layer；
- business criticality；
- data consistency／security；
- concurrency／load／soak applicability；
- actual diff＋System Map impact closure；
- escaped bugs；
- failure cost／reversibility；
- stress cost-benefit。

Verification Profile 只能增加 verification，不能授予 write scope。

## 4. Classification Authority

Mechanical classifier 消費：

- confirmed Task Specification；
- selected scope；
- System Map impact candidates；
- live source／schema／API confirmation；
- external-side-effect declarations；
- actual touched resources；
- failure impact closure；
- current capability health。

Main Agent 可以提出分類／升級理由，但不能自行降低 class。Memory、Telemetry、
System Map 或 discovery metadata 都不能提供 authority。

- Unknown verification risk → stronger Verification Profile。
- Unknown permission／authority → human decision；不能假設允許。

## 5. Dynamic Reclassification

### Automatic Harness Strengthening

L1 發現影響多個已授權 nodes，但仍在原 Task Specification、contracts 與
permissions 內：

```text
L1 projection
→ L2 coordination／isolation／verification
```

只加強 Harness，不修改 authority，因此不需人類。

### Stop Affected Work

需要 public contract、schema、scope-external write、unknown expected behavior 或
real external action 時：

```text
affected lane stops
→ preserve candidate／diff
→ structured exception
→ unaffected safe lanes may continue
```

### No Ad-hoc Downgrade

Main Agent、Memory、Analyzer 不能因成本高把 L2 降 L1、required 改 optional 或
移除 isolation。只有 fixed classifier 在新 projection generation 以 canonical
facts 證明，且不能降低 Task Specification acceptance。

## 6. Automatic vs Human Routes

### Automatic

- runner／tool／environment recovery；
- Context expansion；
- legal repartition／serialization；
- candidate rebuild；
- approved backend fallback；
- System Map query → bounded live-source fallback；
- confirmed retry／recovery；
- verification closure expansion without write；
- L1 → L2 Harness strengthening。

### Human

- specification ambiguity／change；
- architecture／schema／public contract；
- write scope expansion；
- permission／risk policy；
- external／irreversible operation；
- budget increase；
- new recovery policy；
- verification threshold change；
- repair requiring unauthorized node。

## 7. Structured Exception

沿用 `SPEC-WP-001` 並加入：

```text
current authority class
proposed class
blocked transition／lane
trigger and observed evidence
actual affected nodes／contracts
System Map query＋live-source confirmation
safe actions attempted
preserved candidate／diff
requested authority change
verification／budget／external impact
options and tradeoffs
unaffected work that can continue
```

Report 不是 approval。只有 human-confirmed new Task Specification／dedicated
high-risk flow 可以解除 affected boundary。

## 8. 業務場景

### Cross-platform Path Canonicalization

One Module、API／schema unchanged：L1＋V3。執行 Module、Workspace Domain、
path escape／separator boundaries 與 affected regressions，不因一行 diff 降低驗證。

### Three-module Internal Refactor

Behavior／contracts unchanged：L2。Parallel ownership、Join Barrier、
Subsystem／Domain regressions；integration defects 自主 repair。

### New Database Field Required

原 L1 發現現有 schema 無法表達需求：停止 affected lane、保存 diff、提出 L3
schema proposal。批准後建立新 Task Specification／migration flow；production
migration 仍需額外授權。

### Scope-external Manifest Loader Impact

PathNormalizer 影響 ManifestLoader：ManifestLoader 加入 verification closure，不自動加入 write
scope。若需 repair，提出 scope expansion。Map 缺 relation 時以 live source 為
現況並安排 Map maintenance。

## 9. Stress Contract

- High-volume L1 tasks 不誤升重型 L2。
- High-criticality small diff 不低估 verification。
- L2 parallel work 發現 L3 只停止 affected lanes。
- Main Agent／Memory downgrade attempt 被阻擋。
- Actual diff 與 predicted scope 不符會 reclassify。
- Map stale／unavailable 不授權或降低 risk。
- Concurrent exceptions 不混合 approval。
- External tool call 沒有 permission 被阻擋。
- Restart 從 current canonical inputs 重建 classification。
- Classification／routing 不依賴 Agent／LLM runtime。

## 10. 對應機械測試

```text
test_change_authority_and_verification_intensity_are_independent
test_financial_one_line_change_can_be_l1_v3
test_l0_reclassifies_when_runtime_behavior_is_touched
test_l1_to_l2_strengthening_does_not_require_human
test_l3_requirement_stops_only_affected_lanes
test_main_agent_memory_or_telemetry_cannot_downgrade_authority
test_unknown_permission_requires_decision_not_assumed_access
test_verification_expansion_never_grants_write_scope
test_l3_confirmation_does_not_authorize_production_side_effect
test_exception_report_preserves_candidate_and_unaffected_progress
test_system_map_discovery_never_authorizes_risk_class
test_large_concurrent_reclassification_is_deterministic_and_zero_agent
```

## 11. Self-Evolution Boundary

OLE 可以改善 classifier implementation、explanation、ordering 與 bounded Context，
不能修改 class semantics、verification authority、unknown handling、downgrade
rules、exception fields、external high-risk boundary、measurement logic 或 human
escalation。
