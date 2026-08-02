# Decision 0021: Separated Budget Ledgers and Bootstrap Policy

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH分開管理六類budget：

- Agent model usage
- Context ingestion
- Work Package wall time
- Verification execution
- Recovery attempts
- Stress execution

External operation的金錢與side-effect budget保持獨立。任何budget不足都不能修改
Task Specification、required scenarios、threshold、oracle或external authority。

Budget來源優先序：

```text
Task Specification explicit
→ approved project budget profile
→ calibrated DDH bootstrap profile
```

Runtime無法取得actual usage時必須標記`estimated`，不能宣稱hard enforcement。

## Agent and Context Bootstrap

- Work Coordinator預留至少15% Agent budget作unallocated recovery／integration
  reserve。
- 是否parallel必須計入額外Context、integration與Critic成本，不只比較wall time。
- Progress持續且total budget足夠時，不設固定Agent repair attempt上限。
- 相同inputs、candidate、strategy、failure fingerprint且沒有新證據時，不得
  重複消耗Agent budget。

每個subagent以model effective context計算bootstrap：

- initial Context Envelope最多約15%；
- source全文累計預設最多30%；
- single expansion grant最多5%；
- 至少保留50%給reasoning、tool results與output。

超過Context profile時先summary、repartition或serialize，不靜默擴張。

## Recovery Bootstrap

- Exact same inputs／strategy／fingerprint：不重試。
- Transient infrastructure failure：最多嘗試兩種approved recovery actions。
- 每個approved equivalent backend最多嘗試一次。
- Agent repair只要產生相關delta、新證據或不同有效策略，且總預算仍足夠，
  可以繼續。
- Safe strategies耗盡時形成一次`no_progress`；new evidence不重置已消耗budget。

## Adaptive Timeout Bootstrap

沿用Decision 0009的四種時間語意與公式。Bootstrap parameters：

- safety factor：`2.0`；
- startup margin：`30 seconds`；
- same-suite／same-platform history存在時使用p95；
- 無declared duration、history或reliable estimate的一般Verification Asset，
  hard execution deadline預設`10 minutes`；
- stress／soak duration必須來自Task Specification或approved profile；
- process termination／output drain grace最多`30 seconds`。

沒有stdout不是no-progress。只有adapter提供可信progress／test events、
heartbeat或其他mechanical activity signal時才能使用no-progress deadline；
bootstrap為：

```text
max(2 × expected progress interval, 120 seconds)
```

沒有可信progress signal時依hard deadline，不猜測hang。

## Verification and Stress

- Required business scenarios優先。
- Stress add-on為N/A時stress budget為零。
- Performance／load workload與product SLO必須來自規格。
- 預估required verification超過remaining budget時，在執行前回報
  `verification_plan_not_ready`。
- Budget pressure可調整cache、sharding、ordering、parallelism、Context與
  approved equivalent runner；不得少跑required work。

## Required Scenarios

- 正常60秒suite在無history時不被短timeout誤殺。
- Silent normal generic command不因沒有stdout被判hang。
- Instrumented deadlock由no-progress deadline終止。
- Exact no-progress repeat不消耗更多token。
- New relevant delta／evidence允許repair繼續。
- Broad Context request先得到summary。
- Parallel total-token成本過高時維持serial。
- N/A stress不產生hidden cost。
- Required suite預估超出budget時不先啟動。
- Unobservable usage標記estimated。

