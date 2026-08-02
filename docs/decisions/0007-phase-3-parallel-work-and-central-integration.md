# Decision 0007: Phase 3 Parallel Work and Central Integration

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 3 是 DDH MVP 的第二條 end-to-end vertical slice。它必須證明
`Work Coordinator` 能在平行確實有收益且可安全切分時，讓多個 Agent 非同步
施工，再由主 Agent 中央整合並執行 higher-layer verification。

L2 不強制平行。`Work Coordinator` 必須能輸出：

```text
parallel_beneficial
parallel_not_beneficial
parallel_unsafe
```

後兩者採 serial。平行期間收益消失時，允許自動
`parallel-to-serial fallback`。

## Required Parallel Modes

Phase 3 至少證明：

1. Product implementation 與 independent acceptance Verification Assets 分離。
2. 同一 Subsystem 內多個 Modules 非同步施工，各lane可建立code＋local
   checks，Join後再執行Subsystem驗證。

## Partition Activation Invariant

正式啟用順序：

```text
Work Coordinator creates partition plan
→ Change Guard resolves actual resources
→ Change Guard activates mechanical mutation boundary
→ boundary_active + generation
→ Work Coordinator publishes partition_active
→ Agent may write
```

Change Guard 尚未確認邊界生效時，partition不得顯示為active。Prompt白名單不構成
這項保證。

## Partition and Context Boundary

每個partition至少包含：

- identity／generation與sub-goal；
- Context Envelope；
- allowed／prohibited write resources；
- shared-resource policy；
- local verification；
- budget、automatic recovery與escalation；
- submission result contract。

子Agent可請求具體增量Context，但不能自行擴大read／write scope、修改Task
Specification、合併主Candidate或發布completion。

## Shared Resources

Shared resource包含physical file與logical fixture、interface、state transition、
generated asset、manifest、test helper或database resource。

處理優先序：

1. 拆成不重疊resources。
2. 指定單一owner。
3. 其他lane提交change request。
4. 短期序列化。
5. 無法安全拆分則fallback serial。

## Central Integration and Join

```text
stop new writes
→ writers quiesce／in-flight mutation settles
→ validate partition generations
→ reject late／stale patches
→ main Agent centrally admits patches
→ resolve integration defects
→ System Map impact query + live confirmation
→ Change Guard freezes integrated Candidate
→ Test Auditor fixes admitted assets
→ Verification Runner executes Subsystem suites
→ Completion Judge evaluates each applicable level separately
```

Writer quiescence、Candidate freeze與verification start之間不得存在TOCTOU空窗。

Module-local PASS不等於`subsystem_integrated`；Work Package completion與
Subsystem integration也分開判定。

## Required Scenarios

Phase 3至少涵蓋：

- product／acceptance-test parallel lanes；
- three-Module asynchronous completion；
- shared fixture ownership conflict；
- lost Agent、generation revoke與handoff；
- local PASS但integrated Candidate FAIL；
- actual impact超出預估scope；
- late patch after Join；
- parallel收益消失後自動serial fallback。

System Map query必須在fork前、resource resolution、lane actual diff後、join前與
Subsystem failure後被實際消費；只呼叫但不影響partition、Context或suite
selection不算符合。

## Acceptance

Phase 3只有在mechanical write separation、central integration、safe handoff、
late-writer rejection、writer quiescence、immutable integrated Candidate、
higher-layer verification與parallel cost-benefit fallback均可重跑證明時完成。
