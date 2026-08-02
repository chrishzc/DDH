# Decision 0017: Minimal Typed Identity References

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Decision

DDH不建立一個所有欄位皆optional的全域identity object，也不恢復legacy ADAD
的permanent cross-version identity／freshness／provenance chain。Shared identity
分成四種語意：

1. `VersionedAuthorityReference`：`id`＋`version`＋`content_digest`。
2. `LifecycleReference`：`id`＋`generation`。
3. `ContentReference`：`id`＋`content_digest`。
4. `InvocationReference`：`invocation_id`＋`attempt`。

每個原子handoff只攜帶防止stale、wrong-subject或cross-run absorption所需的
最小references，不重複傳遞完整歷史。

## Semantics

- `version`表示人類核准或受控發布的規格／Contract版本。
- `generation`表示本次執行中的協調時序，不是內容hash。
- `content_digest`只證明特定內容相同，不建立永久entity identity。
- `invocation_id`區分實際機械執行；相同subject的retry必須取得新invocation。
- Trusted execution identity由execution channel提供，不能信任message或Agent
  自行宣告。

## Minimum Handoff Bindings

- Partition activation：Work Package、partition generation、base candidate、
  write-resource-set digest與boundary instance。
- Candidate freeze：Work Package、candidate generation、candidate manifest
  digest與freeze request。
- Verification intake：Task Specification reference、Work Package、frozen
  candidate與Verification Subject manifest reference。
- Runner result：Verification Subject reference、invocation、execution plan
  generation與asset／suite／shard reference。
- Completion decision：Task Specification、Work Package、Verification Subject、
  mechanical verdict與completion layer。

Verification Subject Manifest固定Verification Contract、Verification Asset
Manifest、Environment Profile與invalidation epoch；個別result不重複整份tuple。

## Invalidation Rules

- 同subject retry：subject不變，invocation改變。
- Source改變：新candidate與新subject。
- Verification Asset、threshold、Verification Contract或Environment Profile
  改變：新subject。
- Task Specification改變：新version與新Work Package。
- Branch／candidate改變：舊PASS不能沿用。
- 相同內容再次出現：digest可相同，但lifecycle identity／generation不同。

## Exclusions

Protected identity不得依賴absolute／temporary path、user name、timestamp／mtime、
prompt、raw log、Attempt Ledger、Checkpoint、Source Lock或permanent provenance。
System Map node identity只能作discovery／impact-query reference，不能作
authorization或取代actual candidate／specification／asset binding。

## Issuers

- Human-confirmed specification flow建立Task Specification ID／version。
- Mechanical serializer計算content digest。
- Work Coordinator建立Work Package／partition lifecycle references。
- Change Guard建立candidate／delta／boundary／freeze references。
- Test Auditor建立Verification Contract／Asset Manifest references。
- Verification Runner建立invocation reference。
- Runtime／platform adapter提供trusted execution identity。
- Completion Judge只消費，不補造缺少的authority。

## Required Scenarios

- 相同specification version但digest不同時判定drift。
- 相同invocation ID對應不同結果時判定protocol conflict。
- Late partition generation被拒絕。
- 相同candidate搭配不同acceptance時產生不同subject。
- System Map reference相同但actual branch／candidate改變時舊結果失效。
- 大量parallel invocations不碰撞或cross-Work-Package absorption。
- Runtime restart可從current specification與manifests重建references，不需要
  permanent identity history。

