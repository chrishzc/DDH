# Managed Assets and External High-Risk Operations Contract

**Contract ID：** `DDH-OPS-001`  
**狀態：** Confirmed Architecture Proposal／Implementation Pending  
**日期：** 2026-08-02  
**規範效力：** 保存 managed asset、configuration、branch-bound architecture
view 與 external high-risk operation 邊界；不授權 deployment、migration、network、
credential、System Map 或 executor implementation  

---

> **產品化階段（Decision 0024）：** DDH MVP只交付本Contract的executable
> fixtures與deterministic external-operation simulator（Phase 7A），不持有
> production credentials或執行真實external writes。真實provider Adapter
> （Phase 7B）須在核心MVP通過後，由獨立Task Specification與人類核准逐個加入；
> 不提供generic shell／HTTP Trusted Executor。

## 1. 第一原則

在 repository 內準備、生成與驗證 deployment／migration assets，和真的修改
external system 是不同流程：

```text
General Work Package
→ prepare／validate assets
→ release candidate
→ dedicated high-risk plan
→ exact human approval
→ trusted execution
→ verification／reconciliation
```

Release candidate、dry run、preview、System Map branch view 或 command exit code
都不等於 external operation 已獲授權或完成。

## 2. Asset Classes

### Source-controlled Canonical

Configuration templates、migration scripts、generators、deployment manifests、
API／schema definitions、test profiles、CI／runner configuration。Task
Specification scope 內可由一般 Work Package 修改與測試。

### Derived／Generated

Generated source、compiled schema、lockfile、rendered configuration、bundled
assets。必須有 canonical source 與 deterministic generation path；不得任意雙向
修改。

### Local Environment

Virtual environment、disposable DB、cache、temporary runner configuration。
可以機械重建，不是長期 SSOT。

### External Managed State

Production deployment、real database、credential／secret store、DNS／network／
firewall、cloud resources、package publication、external service configuration。
一般 Work Package不能直接修改。

## 3. Managed Asset Manifest

概念欄位：

```text
asset identity／kind
canonical source
derived targets／consumers
generation／sync procedure
validation procedure
sensitivity
supported platforms
dry-run／preview support
backup／rollback capability
external-side-effect classification
```

禁止：

- two writable canonical sources；
- unknown-source overwrite；
- mtime-only sync；
- discovery metadata authorization；
- Agent在 drift 時任選一邊覆蓋。

## 4. Repository-local Synchronization

```text
read canonical source
→ generate／transform in isolated output
→ compare exact delta
→ validate
→ apply to authorized candidate
→ rerun affected checks
```

要求：

- deterministic output where practical；
- exact added／changed／removed preview；
- atomic apply／recoverable transition；
- preserve existing user diff；
- cross-platform path／encoding／line-ending validation；
- generator／output version compatibility；
- failure 保留原 candidate，不留下 partial sync。

這些是一般 Work Package 的 autonomous work。

## 5. Drift

| Drift | Route |
|---|---|
| Canonical changed，derived old | regenerate／validate |
| Derived manually changed | preserve and classify user diff／unauthorized drift |
| Generator version changed | new projection generation／regenerate |
| External target changed | invalidate high-risk plan／preview／approval |
| System Map differs from live assets | live assets as current evidence＋Map maintenance |
| Canonical source unknown | stop sync＋specification／ownership decision |

## 6. System Map Branch Mode Consumer Boundary

System Map 可以支援 branch mode，讓 Human／Agent 查詢不同 branch 的 actual
architecture。DDH 只固定如何安全消費，不設計 branch index、storage、matching
或 UI。

### 6.1 Exact Source-view Binding

每個 query／projection 至少要能區分概念上的：

```text
repository identity
branch／reference
resolved commit／source revision
worktree／candidate identity when applicable
System Map branch-view version
```

Branch name 本身不足，因為 branch pointer 可以移動。Execution 必須把 query
結果綁定 exact current candidate／worktree；只綁 branch name 的 view 只能作
planning hint，仍需 live-source confirmation。

### 6.2 Actual-only per Branch

- 每個 branch view 只呈現該 branch 已實作的 actual architecture。
- Planned／declared-only architecture 仍不能進入 Active actual view。
- 不把 branch A 的 Entity／Relation 混入 branch B 的 execution closure。
- 不假設 Entity ID 跨 branches／versions 永久穩定。
- Cross-branch comparison 可以做 bounded structural matching／delta projection，
  但不能把 best-effort match 當 stable identity 或 authority。

### 6.3 Query-only Branch Switch

System Map branch selection 不等於 Git checkout、workspace mutation 或 write
permission。DDH 可以查詢另一 branch 作 comparison／planning，而不切換目前
worktree。

如果真的要切換 execution worktree／branch，仍遵守 workspace baseline、
dirty-diff preservation、candidate identity 與使用者授權邊界。

### 6.4 Invalidation

Branch／commit／worktree／candidate source view 改變時，使下列 derived artifacts
局部失效並重建：

- System Map query result；
- architecture Context summary；
- impact／regression closure；
- managed-asset generation preview；
- high-risk external plan／approval；
- release candidate binding。

不自動修改 Task Specification。若 branch change 導致 scope、behavior、contract
或 risk authority 改變，依 `SPEC-WP-001／DDH-RISK-001` 建立 revision／exception。

### 6.5 Dirty Worktree／Uncommitted Candidate

若 System Map branch view 只反映 committed branch：

- 它可以協助 initial planning；
- actual touched resources、candidate diff 與 live worktree 必須作 completion
  前確認；
- uncommitted architecture change 以 bounded live-source discovery補足；
- 不得把 committed Map view 當成目前 candidate 已一致。

## 7. External High-Risk Plan

```text
candidate／release identity
exact target environment
requested operations
expected external delta
preconditions
dry-run／preview result
backup／rollback plan
idempotency／retry semantics
verification procedure
credential reference
approval scope and expiry
```

Human approval 綁定 exact candidate、resolved source／commit、target、operation set、
risk 與 rollback assumptions。Candidate、branch pointer、target 或 operations
改變後，舊 approval失效。

此 approval 只存在真正 external side-effect boundary，不恢復一般 Work Package
逐關 Checkpoint。

## 8. Trusted Executor

Agent 可以準備 artifacts、isolated rehearsal、dry run、preview、delta analysis
與 high-risk plan。

Agent不能取得 raw credentials、任意 production command、改 target、擴大
operations、把 preview 當 success 或使用未批准 recovery。

Trusted Executor：

- resolve credential references；
- verify plan／candidate／commit／target／approval identities；
- execute exact operations；
- emit structured observed result；
- perform only approved safe retry／rollback。
- 沒有已安裝且capability-scoped的provider Adapter時，回報
  `adapter_unavailable`；不得退回任意shell、URL或network工具。

Prompt constraint 不是 capability boundary；Executor 必須有實際機械限制。

## 9. External Operation State

```text
draft
→ previewed
→ approval_required
→ approved
→ executing
→ verified／failed／partially_applied／state_unknown
→ reconciled
```

Exact enum 可調整，但：

- previewed ≠ executed；
- exit 0 ≠ business verified；
- partial apply ≠ no effect；
- unknown ≠ rolled back；
- release candidate ≠ production deployed。

## 10. Recovery Boundary

可以自動：

- approved idempotent retry；
- temporary connection recovery；
- Executor restart；
- exact external-state read；
- approved reversible rollback；
- verification retry without new side effect。

停止並報告：

- target／branch／candidate drift；
- approval expired／identity mismatch；
- partial side effect without approved recovery；
- rollback assumption invalid；
- insufficient credential scope；
- external state unknown；
- new operation／destructive recovery required。

報告包含 executed operations、confirmed effects／non-effects、unknowns、remaining
risks、attempted approved routes、new decision options。

## 11. Database

Preserve-data migration：

1. backup／snapshot first；
2. prefer additive／new target；
3. isolated rehearsal with representative data；
4. precondition schema／row checks；
5. exact target；
6. post schema／row／business reconciliation；
7. explicit reversible application config switch where possible；
8. destructive operation clearly named and separately approved。

Dry run／`--check`／script PASS 不等於 production migration。

## 12. Credentials and Network

- Agent只見 credential reference／capability。
- Secrets 不進 Task Specification、Ledger、Telemetry、logs、Memory。
- Executor controlled resolution。
- Network destination／method／resource exact allowlist。
- Redirect／dynamic host／new destination 不沿用 approval。
- Credential rotation／revocation 是獨立 external operation。

## 13. 業務場景

### Configuration Generator

修改 canonical template，在 isolated output生成多平台 configs，顯示 diff，驗證
schema／encoding／paths，apply candidate，重跑 tests。無 external approval。

### Feature Branch Architecture Preview

Feature branch 實作新 Module dependency。System Map branch mode 顯示該 branch
actual graph，Main branch 保持原 graph。DDH 對 feature candidate 選 tests／impact，
不把兩個 branch views 混合，也不假設跨 branch stable Entity IDs。

### Production Database Migration

Migration artifacts、rollback、rehearsal、reconciliation tests 形成 release
candidate。Trusted Executor preview exact production target，Human批准 exact
candidate／resolved commit／operations，Executor backup、apply、reconcile、
config switch，發布 verified／partial／unknown result。

### Approval after Branch Moved

Approval 綁定 commit X；branch 隨後移到 X+1。Executor identity precheck 失敗，
不執行外部 operation，重新生成 preview／plan／approval。

### Dirty Worktree

Map branch view 只含 committed revision，但 execution candidate 有 user／Agent
uncommitted diff。DDH 使用 Map planning＋live candidate diff mapping，不用舊
branch view宣稱 impact closure 完整。

## 14. Retention

Repository sync 長期留下 canonical／derived assets 與 tests，不永久保存 generation
logs／PASS receipts。

External high-risk retention 由 operational／compliance specification決定，可以
要求更強 evidence，但不能反向讓一般 Work Package保存 heavy history。

## 15. Stress Contract

- Large deterministic asset regeneration。
- Concurrent generators 不產生 partial output。
- Existing user diff 不被覆蓋。
- Cross-platform path／encoding parity。
- Generator crash／disk full 保留 candidate。
- Branch query切換不混合 identities／Contexts。
- Branch pointer、candidate、target 在 approval 後 drift。
- Duplicate external request／Executor mid-operation crash。
- Partial migration／rollback failure／state unknown。
- Secret 不進 logs／Ledger／Telemetry。
- Network redirect 不擴張 destination。
- Exit 0 不掩蓋 external verification failure。
- General Work Package 無 external capability。
- Internal sync／external execution routine paths 不依賴 Agent／LLM。

## 16. 對應機械測試

```text
test_managed_asset_has_one_canonical_source_and_validated_generation
test_internal_sync_preserves_user_diff_and_never_leaves_partial_output
test_system_map_branch_view_binds_exact_resolved_source_identity
test_branch_name_alone_cannot_bind_execution_or_external_approval
test_cross_branch_comparison_never_assumes_stable_entity_identity
test_query_only_branch_switch_does_not_mutate_worktree_or_grant_scope
test_dirty_candidate_uses_live_diff_confirmation_beyond_committed_map_view
test_external_plan_binds_candidate_commit_target_operations_and_expiry
test_release_candidate_preview_or_exit_zero_cannot_claim_deployment
test_agent_cannot_access_raw_credentials_or_direct_external_capability
test_target_or_branch_drift_invalidates_approval_before_execution
test_partial_or_unknown_external_state_never_claims_rollback
test_preserve_data_migration_backs_up_rehearses_and_reconciles
test_large_asset_and_external_operation_load_is_bounded_and_zero_agent
```

## 17. Self-Evolution Boundary

OLE 可以改善 generation scheduling、preview summary、approved retry ordering 與
bounded Context，但不能修改 canonical source authority、branch identity binding、
Task／scope authority、approval semantics、credential／network capability、
external recovery、database safety、retention compliance 或 human boundary。
