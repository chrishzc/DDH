# Partition, Candidate, and Handoff State Tables

- State-table family: `P0-PARTITION-CANDIDATE-HANDOFF`
- Projection authority: `DDH-P0-SPEC-001` version `1.0.0`
- Related contract family:
  [context-coordination-and-candidate.md](../contract-families/context-coordination-and-candidate.md)

These are local lifecycle tables. They do not create a global Task lifecycle,
Frozen Task, Source Lock, Checkpoint, lease registry, receipt, or recovery
control plane.

## 1. Context Request

| Current | Event/guard | Next/result | Required mechanical action |
|---|---|---|---|
| `requested` | exact necessary content; within budget; current Candidate | `granted_exact` or `granted_excerpt` | Bind grant to partition, Candidate digest and Context Ledger; charge once |
| `requested` | broad request without a concrete decision question | `granted_summary` or `denied` | Return bounded index/summary; request a narrower purpose |
| `requested` | duplicate content already loaded | `denied_duplicate` | Return reference without reinjecting or recharging content |
| `requested` | expansion budget exhausted | `budget_exhausted` | Route to summary, repartition or serial work |
| `requested` | expected behavior is missing | `specification_gap` | Do not substitute more source for missing authority |
| `granted_exact` / `granted_excerpt` / `granted_summary` | Candidate, contract or invalidation epoch changes | `stale` | Block direct freshness admission and materialize only the required increment |
| any | Envelope artifact is corrupt but authority is fixed | same semantic state after rebuild | Rebuild deterministically; do not grant new scope |

Goal, Task Specification, acceptance and prohibitions are pinned across every
transition.

## 2. Parallel Decision and Mode Routing

| Inputs | Decision | Next action |
|---|---|---|
| At least two writers; fixed semantics; separable resources; benefit exceeds Context and integration cost | `parallel_allowed` | Resolve resources and select a mechanically supported mode |
| Separable work; benefit does not exceed total parallel cost | `parallel_not_worthwhile` | Use one serial writer |
| Overlap is uncertain, semantic contracts are shared/unfixed, or no safe separation exists | `parallel_unsafe` | Use serial work without weakening boundaries |
| Separation requires changing scope, specification, architecture or risk | `needs_human_decision` | Stop only affected work and issue structured exception |

Mode routing:

| Current attempt | Capability result | Next |
|---|---|---|
| `guarded_shared` requested | All trusted interception, containment, canonicalization, reconciliation and revoke capabilities proven | Activate `guarded_shared` |
| `guarded_shared` requested | Any required capability unavailable or unknown | Try `isolated_candidate` |
| `isolated_candidate` requested | Private Candidate and Patch Admission available | Activate `isolated_candidate` |
| `isolated_candidate` requested | Unavailable; work is eligible for one-writer reconciliation | Activate `serial_reconciled` |
| `serial_reconciled` requested | Safe baseline/delta separation unavailable | `platform_blocked` once |
| any local mode | External side effect required | `external_high_risk_flow_required` |

## 3. Partition Lifecycle

| Current | Event/guard | Next | Invariant |
|---|---|---|---|
| `planned` | Exact activation tuple submitted to Change Guard | `activating` | No write tools are exposed |
| `activating` | Exact tuple receives `boundary_active` | `active` | Work Package, partition generation, trusted writer, base Candidate, resource-set digest and boundary instance all match |
| `activating` | Provisioning failure, mismatch or stale generation | `activation_failed` | Partition never becomes writable; route to safe fallback/recovery |
| `active` | Freeze fence accepted | `frozen` after mutation closure | No new operations for that generation; admitted pre-fence operations settle |
| `frozen` | Delta is admitted/submitted | `submitted` | Frozen generation cannot resume writing |
| `planned` / `activating` / `active` | Generation withdrawn safely | `revoked` | Later output is stale |
| `active` / `frozen` | Mutation closure or delta ownership is unknown | `recovery_required` | No replacement writer or final Candidate yet |

`active` is a mechanical fact, not a prompt or coordinator declaration.

## 4. Cross-zone and Shared-resource Requests

| Request condition | Result | Effect |
|---|---|---|
| Required change belongs to a current in-scope writer | `route_to_current_writer` | Send minimal failure evidence; requester gains no write access |
| Required change remains in scope but partitioning is wrong | `repartition_within_scope` | Fence, preserve delta, then create new generations |
| Approved shared logical resource requires one writer | `serialize_shared_change` | Freeze affected writers; assign one writer; refresh dependants |
| Evidence does not justify the change | `reject_unnecessary_request` | Existing boundaries remain |
| Change requires scope, specification, public contract, architecture or risk change | `human_scope_or_spec_decision` | Stop only affected work |

At all times a shared logical resource has at most one active writer. A pending
request is never a temporary grant.

## 5. Patch Submission and Admission

| Current | Check/result | Next | Candidate effect |
|---|---|---|---|
| `submitted` | All authority, identity, scope, resource, freshness and completeness checks pass | `accepted` | Create new Candidate generation |
| `submitted` | Content can integrate, but dependency/impact closure changed | `accepted_revalidation_required` | Create new Candidate generation and invalidate affected prior results |
| `submitted` | Any touched resource is outside scope/partition or patch mixes allowed and forbidden changes | `rejected_scope_or_partition` | No Candidate change; retain bounded private delta for narrowing |
| `submitted` | Specification, generation, base Candidate or dependency is stale | `rejected_stale_result` | No Candidate change; current generation continues |
| `submitted` | Physical or semantic integration conflict | `integration_conflict_rework_required` | Preserve evidence and start bounded rework |
| `submitted` | Admission requires a human-owned change | `human_change_decision_required` | Preserve current Candidate and stop affected integration |

Central admission is serialized by Candidate generation. Static analysis may
run in parallel, but it cannot mutate the integration Candidate.

## 6. Handoff Lifecycle

| Current | Event/guard | Next/result | Required action |
|---|---|---|---|
| `requested` | Freeze fence established for old generation | `draining` | Block new operations and inspect all registered/descendant writers |
| `draining` | Pre-fence operations settle; mutation closure and deltas known | `old_generation_sealed` | Preserve user baseline and Agent delta separately |
| `old_generation_sealed` | Useful continuation is required | `handoff_completed` | Revoke old generation; create a new generation from current Candidate with bounded Context increment |
| `old_generation_sealed` | No Agent delta exists | `handoff_no_agent_delta` | Revoke and reassign without attributing user delta to the Agent |
| `requested` / `draining` | Operation, trusted identity, mutation closure or delta state remains unknown | `handoff_recovery_required` | Fail closed; reconcile or isolate before reassigning |
| `old_generation_sealed` | Continuation is no longer needed | `handoff_cancelled` | Preserve accepted Candidate evidence; create no replacement |

Timeout, heartbeat loss, process exit and Agent claims do not bypass
`draining`.

## 7. Join Barrier

| Current | Event/guard | Next | Action |
|---|---|---|---|
| `collecting_lanes` | A current lane reaches composite readiness | `collecting_lanes` | Seal its generation; release Agent/runner resources |
| `collecting_lanes` | Any required lane is incomplete, stale, active or has unresolved shared mutation | `waiting_for_lanes` | Continue only affected bounded work |
| `waiting_for_lanes` | Shared contract changes | `waiting_for_lanes` | Invalidate and reopen only dependent lanes with new generations |
| `waiting_for_lanes` / `collecting_lanes` | Every join invariant holds | `integration_ready` | Integrate in fixed order |
| `integration_ready` | Actual diff and live impact reconciliation succeed | `freeze_requested` | Ask Change Guard to freeze one integrated Candidate |
| `integration_ready` | Scope must expand or shared semantics conflict | `human_change_decision_required` | Preserve lane deltas; do not guess |

Worker completion order never chooses integration order. Waiting and join
evaluation consume zero Agent tokens.

## 8. Freeze and Candidate Lifecycle

| Current | Event/guard | Next | Rule |
|---|---|---|---|
| `mutable_generation` | Complete integration group freeze requested | `freeze_pending` | Establish a sortable fence epoch for every target generation |
| `freeze_pending` | Some pre-fence operations still run | `draining` | Post-fence and stale operations are rejected |
| `draining` | Some partitions are quiescent, others active/draining/unknown | `partial_sealed` | Ready deltas may seal, but no final Candidate manifest exists |
| `draining` / `partial_sealed` | All mutation closures proven; submitted deltas admitted; snapshot complete | `candidate_frozen` | Publish immutable Candidate identity and manifest digest |
| `draining` / `partial_sealed` | Mutation closure or external side-effect state unknown | `freeze_recovery_required` | Do not freeze; route to recovery/high-risk handling |
| `candidate_frozen` | Late mutation is blocked before landing | `candidate_frozen` | Record stale rejection; immutable content is unchanged |
| `candidate_frozen` | Mutation actually changes the protected snapshot | `candidate_invalidated` | Invalidate dependent verification subject and rebuild through a safe fresh generation |
| `candidate_frozen` | Manifest omits required tracked, untracked or generated input | `candidate_invalidated` | Re-scan actual snapshot; do not admit verification |

An unknown tool result with mechanically proven mutation closure may continue
from the complete actual snapshot, but it cannot be reported as tool success.

## 9. Dirty-worktree Preservation

| Condition | Allowed transition |
|---|---|
| User delta can be materialized and distinguished | Establish it as explicit baseline input, then create Agent delta |
| A clean HEAD-only isolated Candidate would omit required user delta | Reject that materialization |
| Shared mode can protect and reconcile the existing baseline | Use it only if the required mechanical capabilities are proven |
| No mode can preserve and distinguish the baseline | Stop parallel work or emit one `platform_blocked`; never reset, stash, overwrite or silently omit |

## 10. Recovery Routing

| Failure | Automatic route | Terminal only when |
|---|---|---|
| Boundary artifact corrupt | Stop exposing writes; rebuild; rerun exact partition activation | Rebuild and isolation/serial fallback are all unavailable |
| Writer stalled | Bounded drain; safe termination if profile allows; reconciliation; isolated fresh generation | Mutation closure cannot be made safe by any allowed route |
| Stale request blocked before landing | Keep current generation running | Never terminal by itself |
| Stale mutation landed | Circuit-break boundary; invalidate Candidate; preserve delta; rebuild isolated fresh generation | All safe modes are exhausted |
| Context artifact stale/corrupt | Rebuild from fixed authority and live source | Missing behavior requires a human specification decision |
| Repeated cross-zone requests | Preserve deltas and fall back to serial | Human decision only if scope/specification must change |

Recovery preserves fixed goal, scope, acceptance and user changes. It does not
create a human Checkpoint for ordinary mechanical repair.
