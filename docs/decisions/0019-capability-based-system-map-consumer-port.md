# Decision 0019: Capability-based System Map Consumer Port

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH只固定消費System Map所需的capabilities與normalized outcomes，不固定
System Map的schema、enum、API method、storage、query engine或backend。

MVP最低capabilities：

1. 將human-selected Global／Domain／Subsystem／Module scope解析為node。
2. 查詢node ancestors與architecture level。
3. 查詢direct dependencies與direct reverse dependencies。
4. 將source／schema／configuration resources映射至nodes。
5. 回報coverage、omission與local currentness是否足以支援該query。
6. 將result綁定repository、branch／ref、resolved commit與System Map
   view／Bundle。

DDH可以反覆使用bounded Q1建立Q2 closure；MVP不要求System Map先提供完整
graph analysis engine。

## Authority Boundary

System Map是published actual-only architecture index，不授予write scope、
completion、risk、Verification Asset selection或scope expansion authority。
它不保存Work Package、ownership、runner或test governance state。

Node到Verification Asset的映射可由DDH將System Map與Verification Asset
Catalog join，不要求System Map擁有test governance data。

## View Binding

每個query至少能辨認：

```text
repository identity
requested branch／ref
resolved commit
worktree／candidate reference when applicable
System Map view／Bundle identity
actual-only requirement
query purpose and bounded depth
```

Branch name alone不足。Query-only view switch不得執行checkout或修改workspace；
不同branch的actual facts不得混入同一result。

## Candidate Overlay

Candidate尚未published進System Map是正常狀態。DDH使用：

```text
baseline branch view
＋ actual candidate delta
＋ resource-to-node binding
＋ bounded live-source discovery for changed area
```

形成candidate impact closure。Map maintenance candidate可在整合後建立；pending
maintenance通常不阻擋功能完成。

## Adapter Outcomes

System Map維持自己的狀態名稱；DDH adapter只需標準化為：

- `usable_actual`
- `partial`
- `conflicted`
- `view_mismatch`
- `unavailable`
- `impact_unknown`

Partial／conflicted／unavailable只對受影響區域使用bounded live fallback。只有
fallback後仍為`impact_unknown`時，不能宣稱impact closure完成。

## Required Consumption

System Map query在initial scope、parallel partitioning、Context materialization、
actual delta reconciliation、join／freeze、verification selection、failure repair
與completion前依適用情況機械觸發。

僅呼叫query不算完成；partition plan、Context Envelope、impact closure、
Verification Asset selection或completion input必須引用query result並列出實際
消費的nodes／relations。

Initial planning可使用current-enough actual view，不重讀完整專案。只有protected
transition、local currentness不足、candidate delta或Map／live conflict才做
bounded reconciliation，避免抵消index效益。

## Required Scenarios

- Same branch name但resolved commit改變時舊query失效。
- Query另一branch不修改current worktree。
- Candidate新增依賴但Map未更新時由delta＋live discovery補足。
- Local stale只fallback該區域。
- Map unavailable時eligible L1仍可安全繼續。
- Planned／declared-only overlay不進入actual closure。
- Large Domain只將bounded Q0／Q1 summary放進Agent Context。
- Concurrent branch queries不混合facts。
- Query未被下游消費時Completion Judge拒絕impact-complete claim。
- Outside-scope affected node可加入verification closure，但不取得write authority。

