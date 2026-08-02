# Decision 0025: Human Authority Roles and Confirmation Timing

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH 使用 authority-source separation，不建立固定人工審批角色鏈。人類只在
建立或改變需求、架構、project policy、scope、acceptance、budget authority
或 external authority 時確認；一般施工、驗證、修復、重新分區與完成不逐關
詢問人類。

同一個人可以同時持有多種 human authority。角色名稱用來區分決策來源，不要求
成立委員會、多人簽署或每個 Work Package 都配置不同人員。

## Authority Roles

| Authority role | Responsibility |
|---|---|
| Demand Owner | 使用者目標、功能語意、scope、禁止項目、acceptance與task budget |
| Architecture Owner | architecture、schema、public／cross-domain contract與L3 boundary |
| Profile Policy Owner | project-level risk、quality、timeout、budget、retention defaults |
| External Authority Owner | exact provider／target／operation plan與真實external side effect |
| Main Agent | 起草、整理、readiness檢查、projection與exception proposal；沒有核准權 |
| Mechanical DDH components | enforcement、admission、verification、completion；沒有規格或權限創設能力 |

Task Specification可以由Agent起草，但只有human-confirmed version是task
authority。System Map、source、test、discovery metadata、prompt與Agent claim
都不能取代相應的人類authority。

## Confirmation Timing

### Project Profile

Project-level defaults在首次建立或版本改變時確認一次。Work Package只引用固定
profile version，不逐項重複核准。

### Work Package Admission

每個會改變產品行為或受治理資產的Work Package，在施工前確認一份Task
Specification：

- L0：人類明確要求＋最小goal／prohibition／lightweight verification即可；
  明確請求本身可構成確認，不建立厚重lifecycle。
- L1／L2：人類一次確認完整Task Specification version；不逐欄、逐test或逐
  execution projection確認。
- L3：先確認architecture／schema／contract等authority change，再確認引用該
  decision的Task Specification。

一般local work不要求cryptographic signature或legacy Checkpoint。確認必須清楚
指向exact Task Specification version，例如「依Task Specification v3開始實作」；
模糊討論、proposal acceptance或單純閱讀文件不構成施工權。

### Active Execution

Task Specification authority fields不變時，下列動作自動進行：

- implementation／test construction；
- test admission／verification／repair／retest；
- Context expansion；
- repartition／parallel-to-serial fallback；
- runner／tool recovery；
- Work Package Projection regeneration；
- Completion Judge evaluation。

只有要改變goal、behavior、architecture、schema、public contract、write scope、
prohibition、acceptance、risk policy、budget ceiling或external authority時，
affected work停止並提交structured exception／revision proposal。

### Completion and Higher Layers

Work Package completion由固定Task Specification與current Verification Assets
機械判定，不要求完工簽核。Subsystem integration、Domain acceptance與release
candidate分別依其層級規格判定；只有相應規格明定human business judgment時才
需要人類輸入。

### External Operation

Release candidate不取得external authority。External Authority Owner只在真實
side-effect boundary核准綁定exact plan／candidate／target的operation；這不是
一般施工Checkpoint。

## DDH Implementation Authorization Sequence

DDH本身的首次施工也遵守相同模型：

```text
architecture discussion accepted
→ Implementation Readiness Review
→ Phase 0 Task Specification confirmed
→ executable contracts／fixtures completed
→ first Runtime Task Specification confirmed
→ autonomous in-scope execution with exception escalation
```

Phase 0是runtime施工前的必要規格準備，但不是對所有未來runtime scope的空白
授權。後續授權單位是human-selected Task Specification／Work Package，而不是
每個Phase的固定Checkpoint。

## Acceptance

- Main Agent可起草但不能self-confirm Task Specification。
- L0仍有明確人類意圖來源，但不承擔L1／L2規格成本。
- L1／L2只有一次admission確認，routine execution不詢問人類。
- L3 architecture decision與external approval不能被一般Task確認取代。
- Projection／Context／runner／partition change不造成confirmation storm。
- Completion PASS不要求額外人工Checkpoint。
- Higher-layer acceptance不從Work Package completion自動推導。
- Proposal acceptance與implementation authorization可被機械區分。

