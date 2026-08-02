# Decision 0018: Tiered Local Mutation Mediation

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH第一版Mutation Mediation採單一Python Runtime內的local `Change Guard`，
組合：

```text
pre-operation admission
＋ available platform containment
＋ candidate baseline／delta
＋ local Patch Admission
＋ post-operation reconciliation
```

第一版不建立常駐central Patch Service。Git hook是advisory／defense-in-depth，
不是mutation authority或MVP必要依賴。

## Modes

### Serial Reconciled

適用L0／L1、單一writer、可逆、scope清楚且使用者existing delta可安全區分的
施工。以baseline、明顯越界precheck與post-delta reconciliation形成admission
boundary，不要求每次edit都先經過hook。

### Guarded Shared

只有platform adapter已mechanically self-check trusted execution identity、
write interception、filesystem containment、path canonicalization、
post-delta reconciliation與writer revoke時可用。Configured hook或prompt
constraint不能聲稱具備此能力。

### Isolated Candidate

適用L2 parallel、dirty／shared workspace、未知輸出工具或無法安全共享的資源。
Writer只修改private candidate；local Patch Admission檢查scope、partition、
generation、protected／shared resources、actual delta、rename／delete／untracked／
generated resources與freshness後，才能形成integration candidate。

External database、deployment、credential、publication與其他產品副作用不屬於
上述模式，仍使用Phase 7 Trusted Executor。

## Routing

```text
Guarded Shared unavailable
→ Isolated Candidate
→ eligible Serial Reconciled
→ one platform_blocked result when no safe mode exists
```

未知輸出工具優先自動路由至Isolated Candidate，不要求人類逐次核准，也不讓
Agent研究Harness工具故障。不得從失效mechanical boundary降級成prompt-only
parallel mutation。

PreTool Gate只硬阻擋：

1. 無有效Task Specification的mutation。
2. 明確scope外或protected resource。
3. 未授權external／irreversible side effect。

## Admission Semantics

所有進入protected integration candidate的mutation都必須mechanically admit。
L1 single-writer可以post-operation reconciliation作admission boundary；L2
parallel或shared mutation必須使用verified containment或isolated Patch
Admission。

Mixed valid／invalid patch整份不吸收。系統保留可用delta並自動安排產生縮小後
patch；不得破壞性reset使用者workspace。

## Required Scenarios

- Single Agent連續修改產品與tests，不逐次詢問。
- Unknown-output formatter自動切到isolation。
- Product與test writers同時碰shared fixture時不互相覆寫。
- Dirty worktree中的existing user delta保持完整。
- Boundary故障時revoke writer並自動換安全模式。
- Late writer、stale generation與background process不污染frozen candidate。
- Symlink／junction不能繞過scope。
- 大量small edits不因per-file admission造成顯著治理延遲。
- 所有安全模式不可用時只形成一次machine-actionable blocked result。

