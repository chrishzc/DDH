# Decision 0009: Phase 5 Operational Hardening and Adaptive Timeouts

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

Phase 5強化Verification Runner environment、cross-platform reproducibility、
bounded output、process／temporary-root safety、Capability Health、managed assets、
branch-aware System Map consumption與non-authoritative operational telemetry。

Decision 0022已將最低release-blocking平台矩陣固定為：

```text
vendor-supported Windows 11 x86_64
＋ Ubuntu 24.04 LTS x86_64
```

兩者驗證Python 3.13與latest stable。macOS、ARM64、WSL2及其他Linux先列
preview；network-share writable candidate與vendor-EOL OS不列MVP正式支援。
POSIX可保留在具體OS／API compatibility實作文件中。

## Environment and Isolation

每個Verification Subject綁定Environment Profile，至少描述runtime／tool
versions、dependency identity、cwd、locale／timezone／encoding、environment
allowlist、fixture/service requirements、network／database capability、isolation
profile、resource budget與output limits。

隔離依風險採`light`、`standard`、`high_assurance`或獨立`external` lane。一般
Work Package不得以temp workspace冒充network／credential／database isolation。

## Adaptive Bounded Timeout

Runner timeout不能使用單一固定短秒數。必須分開：

1. **Business performance threshold**：Specification authority，不可由Runner調整。
2. **Execution deadline**：本次suite／shard可使用的執行預算。
3. **No-progress deadline**：偵測hang／deadlock。
4. **Termination／output-drain grace**：執行期限後的安全清理時間。

執行前由機械Execution Planner根據：

- specification-declared expected duration；
- same-suite mechanical p95；
- collected tests、markers、fixtures與shard plan；
- platform／isolation profile；
- startup margin與approved safety factor；
- Work Package time ceiling；

固定本次Execution Plan generation。概念公式：

```text
reference =
  max(declared duration, historical p95, collected-work estimate, profile floor)

execution deadline =
  reference × approved safety factor + startup margin
```

如果估算超出Work Package ceiling，執行前回報
`verification_plan_not_ready`，不得先跑到timeout才反覆重試。

Timeout先分類為infrastructure／execution incomplete，不直接等於product failure。
只有產生new Execution Plan、new environment、new shard plan或其他approved new
information時才能retry。機械Planner可在既有budget內自動調整；主Agent、
Test Auditor或Learning Steward不能因失敗自行延長deadline。需要增加user budget
時才提升人類。

正常60秒suite不得因legacy式固定30秒timeout誤判；真正no-progress test也不得
只靠無限延長suite deadline繼續。

Decision 0021確認第一版bootstrap：safety factor `2.0`、startup margin
`30 seconds`；無declared duration、history或reliable estimate的一般asset使用
`10 minutes` hard deadline，termination／drain grace最多`30 seconds`。
No-progress不能用「沒有stdout」判定；只有可信progress signal存在時使用
`max(2 × expected progress interval, 120 seconds)`。

## Output, Process and Cleanup

- Byte／line／event limits必須在subprocess drain層生效。
- 重複traceback依root fingerprint聚合。
- Timeout／crash後確認Windows process tree或Unix-like process group。
- 只清理由工具建立且identity仍相符的temporary root。
- Symlink／junction／reparse／permission／identity不確定時保留並quarantine。

## Capability Health and Managed Assets

工具能力使用`available`、`degraded`、`unavailable`、`unknown`短期狀態，只供
Work Coordinator選擇approved fallback；不能改spec、scope、acceptance或external
authority。

Repository-local managed assets使用Manifest、dry-run、isolated output、
delta preview、compatibility verification、atomic apply與post-apply parity。
不得remove-then-copy整棵target，也不得靜默覆蓋user-customized assets。

## Branch-aware System Map

DDH query consumption綁repository、branch、resolved commit、worktree、
Candidate與Map view。Branch name相同但commit改變時，舊Context／impact／asset
preview失效。Query-only branch switch不得修改使用者Git working tree。

## Acceptance

Phase 5必須證明：

- Windows與MVP Linux profile產生相同驗收語意；
- 正常長時間suite不被固定短timeout誤殺，hang仍能有界終止；
- output、process與cleanup維持bounded且安全；
- degraded tool自動走approved fallback；
- managed assets可preview、atomic apply並保護user changes；
- exact branch／commit／worktree／Candidate binding；
- telemetry不成為SSOT、completion authority或永久raw log。
