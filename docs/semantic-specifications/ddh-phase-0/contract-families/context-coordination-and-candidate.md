# Context, Coordination, and Candidate Contract Family

- Contract family: `P0-CONTEXT-COORDINATION-CANDIDATE`
- Projection authority: `DDH-P0-SPEC-001` version `1.1.0`
- Status: Phase 0 executable semantic projection
- Runtime implementation authority: None

## 1. Purpose

This family projects the accepted behavior for bounded Agent context, parallel
work coordination, local mutation mediation, central patch admission, writer
handoff, mechanical quiescence, deterministic join, and immutable Candidate
freeze.

It defines expected outcomes without choosing a runtime API, process model,
filesystem backend, database, queue, or permanent ownership mechanism.

## 2. Authority

| Concern | Authority |
|---|---|
| Phase 0 scope and required coverage | `DDH-P0-SPEC-001` |
| Parallel decision, partition activation, handoff and join | Decision 0007; `OW-F01`, `OW-F02`, `OW-F05`, `OW-F06`, `OW-F07`, `OW-F12`, `OW-F13`, `PWC-CIM-001`, `PWC-CIM-002`, `PWC-INTEG-003` |
| Context Envelope and grants | `OW-F16`, `SMQ-001`, `RC-DOM-003` |
| Mutation mediation and Candidate integrity | Decision 0018; `OW-F03`, `OW-F08`, `OW-F10`, `OW-F11`, `OW-F14`, `OW-F15` |
| Handoff identity | Decision 0017 |
| System Map use | Decision 0019; `SMQ-001` |
| Context budget | Decision 0021 |

Normative source files:

- [Task Specification](../task-specification-v1.md)
- [Parallel Work Decision](../../../decisions/0007-phase-3-parallel-work-and-central-integration.md)
- [Typed Identity Decision](../../../decisions/0017-minimal-typed-identity-references.md)
- [Mutation Mediation Decision](../../../decisions/0018-tiered-local-mutation-mediation.md)
- [System Map Consumer Decision](../../../decisions/0019-capability-based-system-map-consumer-port.md)
- [Budget Decision](../../../decisions/0021-separated-budget-ledgers-and-bootstrap-policy.md)
- [Context Broker Contract](../../../proposals/context_broker_subsystem_specification.md)
- [Parallel Coordination Contract](../../../proposals/parallel_work_coordination_subsystem_specification.md)
- [Candidate Integrity Contract](../../../proposals/candidate_integrity_and_mutation_subsystem_specification.md)

## 3. Contract Vocabulary

### 3.1 Context Envelope

A Context Envelope is a rebuildable, Candidate-bound projection containing only
the material needed by one lane:

- Work Package and Task Specification references;
- partition, generation and sub-goal;
- pinned goal, acceptance, prohibitions and required contracts;
- bounded architecture index summaries and source references;
- allowed and prohibited write resources as information, not permission;
- local verification, budget and escalation conditions;
- Context Ledger reference and invalidation epoch.

The Envelope does not grant write authority. A content grant expands only the
lane's readable working context. Actual read permission remains a property of
the execution environment; actual write permission comes only from an active
mechanical mutation boundary.

### 3.2 Minimal identity bindings

Each atomic handoff carries only the identity references needed to reject
stale, wrong-subject, or cross-run results:

- versioned authority reference for the Task Specification;
- lifecycle references for Work Package, partition and Candidate generations;
- content references for base Candidate, resource set, delta and manifest;
- trusted execution identity supplied by the execution channel;
- invocation reference when a mechanical operation is executed.

Paths, timestamps, prompts, Agent claims and System Map node IDs are not
substitutes for these bindings.

### 3.3 Parallel decision

The coordination decision is one of:

| Result | Meaning |
|---|---|
| `parallel_allowed` | Independent work and measurable benefit justify mechanically separated lanes |
| `parallel_not_worthwhile` | Work is separable, but Context, environment or integration cost removes the benefit; use serial work |
| `parallel_unsafe` | Write or semantic boundaries cannot be made safe; use serial work |
| `needs_human_decision` | Parallelization would require a specification, architecture, scope or risk-policy change |

Uncertain overlap cannot produce `parallel_allowed`.

### 3.4 Mutation modes

The authoritative local modes are:

| Mode | Required behavior |
|---|---|
| `serial_reconciled` | One writer; baseline, obvious precheck and complete post-delta admission |
| `guarded_shared` | Multiple non-overlapping writers only when the platform proves trusted identity, interception, containment, canonicalization, reconciliation and revoke |
| `isolated_candidate` | Private writer Candidate followed by central local Patch Admission |

`serialized_shared_resource` is a coordination strategy: one writer handles the
shared logical resource while independent lanes may continue. It is not a
fourth mutation mode. External side effects are outside all three modes.

The safe routing order is:

```text
guarded_shared unavailable
→ isolated_candidate
→ eligible serial_reconciled
→ one platform_blocked result when no safe mode remains
```

Prompt instructions and configured hooks cannot satisfy a missing mechanical
capability.

### 3.5 Shared and logical resources

A shared resource may be a physical file or a logical fixture, interface,
schema, state transition, manifest, generator/output group, root configuration,
lockfile, test helper, or database resource.

- An unapproved public contract remains frozen.
- An approved shared change has one writer at a time.
- A request to change another zone does not grant write access.
- A changed shared resource invalidates only dependent active lanes.
- Independent lanes are not stopped by a repository-wide lock.

### 3.6 Patch Admission

Admission into the integration Candidate is serialized by Candidate generation
and checks, in order:

1. current Work Package and Task Specification;
2. partition, writer, generation and base Candidate;
3. actual touched resources against scope and partition;
4. protected, shared and logical-resource conflicts;
5. dependency and content freshness;
6. complete application with no undeclared delta;
7. new Candidate identity;
8. required provisional or integration revalidation.

A patch mixing permitted and forbidden changes is rejected as a whole. Useful
private delta may be retained briefly for narrowing or rework, but it is not
absorbed into the integration Candidate.

### 3.7 Handoff

A handoff first fences the old generation, settles or classifies in-flight
operations, preserves distinguishable user and Agent deltas, proves mutation
closure, revokes the old generation, then creates a new generation from the
latest admitted Candidate and minimal Context increment.

Timeout, missing heartbeat, process exit, prompt acknowledgement or Agent claim
alone cannot prove a safe handoff.

### 3.8 Join and Candidate freeze

Join is event-driven and automatic, not a human Checkpoint. A final integration
Candidate requires:

- every required lane at its current generation;
- all registered product writers mechanically quiescent;
- required test writer generations sealed;
- required test assets admitted;
- no unresolved shared-resource mutation;
- pinned shared contracts;
- deterministic integration order;
- live reconciliation of actual changed resources and affected architecture.

Freeze first establishes a fence for every target generation, drains admitted
pre-fence operations, and rejects post-fence or stale operations. Agent
completion claims, process exit and coordinator state are not quiescence
evidence. A frozen Candidate is immutable and bound to its manifest digest.

## 4. Invariants

1. No partition becomes `active` before the exact activation tuple receives
   `boundary_active`.
2. No content grant expands Task Specification scope, write scope or data
   permission.
3. No two active writers may own the same shared logical resource.
4. No stale generation, late writer or mixed-scope patch enters the integration
   Candidate.
5. User pre-existing changes remain distinguishable from Agent delta and are
   never reset, stashed, overwritten or silently omitted.
6. No final Candidate is created from partial quiescence.
7. No verification starts against a Candidate that can still be mutated.
8. Parallel-to-serial fallback preserves accepted delta and fixed acceptance.
9. System Map results affect discovery, partitioning, Context and impact
   closure, but never grant authority.
10. Routine Context, join, waiting and invalidation decisions require zero Agent
    tokens.

## 5. Scenario Catalog

The fixture file
[context-coordination-and-candidate.json](../fixtures/context-coordination-and-candidate.json)
contains the executable details and immutable fields for every scenario below.

### 5.1 Context scenarios

| Scenario | Given | When | Then |
|---|---|---|---|
| `P0-CTX-001` | A Test lane has two acceptance items and a bounded budget | Its initial Context Envelope is materialized | Only pinned requirements, required contracts, relevant index references and its test zone are included |
| `P0-CTX-002` | A lane identifies one missing symbol and explains its purpose | It requests content | An exact or excerpt grant is Candidate-bound and charged once |
| `P0-CTX-003` | A lane asks for an entire Domain without a decision question | The request is evaluated | It receives a bounded index/summary or denial, not the Domain contents |
| `P0-CTX-004` | Expansion budget is exhausted | Another broad request arrives | The result is `context_budget_exhausted`; the coordinator summarizes, repartitions or serializes |
| `P0-CTX-005` | Loaded source is bound to Candidate C1 | Integration creates C2 | C1 material is stale; only a bounded increment is issued and C1 output cannot pass freshness admission |
| `P0-CTX-006` | Context compaction is required | Low-value material is removed | Goal, specification, acceptance and prohibitions remain pinned without semantic weakening |
| `P0-CTX-007` | A lane has an uncontrolled filesystem read tool | DDH reports Context control | The guarantee is labelled orchestration-only and cannot claim mechanical cost or data containment |
| `P0-CTX-008` | Many lanes issue duplicate, stale and irrelevant requests | Ten thousand references are evaluated conceptually | Grants are deduplicated, bounded and correctly charged without creating a permanent ten-thousand-item fixture |
| `P0-CTX-009` | System Map location conflicts with live source | Context is resolved | Live source is supplied, drift is reported, and the index grants no scope |

### 5.2 Coordination scenarios

| Scenario | Given | When | Then |
|---|---|---|---|
| `P0-COORD-001` | Product and independent acceptance work have fixed semantics and separate writes | Benefit and risk are evaluated | Result is `parallel_allowed` with separate Context and boundaries |
| `P0-COORD-002` | Work is separable but isolation and Context cost exceed saved time | Benefit is evaluated | Result is `parallel_not_worthwhile`; serial work retains all safety invariants |
| `P0-COORD-003` | Two lanes need the same unfixed public contract | Safety is evaluated | Result is `parallel_unsafe` or `needs_human_decision`; filesystem isolation cannot make semantics independent |
| `P0-COORD-004` | A planned partition has an exact activation tuple | Change Guard confirms that tuple | Only then does the partition become `active` and receive write tools |
| `P0-COORD-005` | Boundary provisioning returns a mismatched tuple or stale generation | Activation completes | The partition never becomes active and automatically routes to a safe fallback or recovery |
| `P0-COORD-006` | Product and Test lanes both need one approved shared fixture | The change is scheduled | One writer is selected, other dependent lanes refresh, and unrelated lanes continue |
| `P0-COORD-007` | A lane has requested another zone | It writes before a new generation is active | The mutation remains blocked; a request is not a grant |
| `P0-COORD-008` | Writer A has an admitted partial delta | Work transfers to B | A is fenced and quiescent; B receives a new generation, current Candidate and bounded handoff summary |
| `P0-COORD-009` | A writer disappears during an operation | Reassignment is attempted | Result is `handoff_recovery_required` until mutation closure is mechanically known |
| `P0-COORD-010` | Two lanes repeatedly request each other's resources | Parallel benefit disappears | Deltas are preserved and work falls back to deterministic serial integration |
| `P0-COORD-011` | Three Module lanes complete out of order | The join condition is evaluated | Early lanes wait without Agent cost; only all-current readiness creates the Subsystem Candidate |
| `P0-COORD-012` | A shared contract changes after lanes start | Invalidation is routed | Only dependent lanes get a new generation and Context increment |
| `P0-COORD-013` | A lane requires a database, deployment or credential side effect | An execution mode is selected | It is routed to `external_high_risk_flow_required`; no local mutation mode grants authority |

### 5.3 Candidate scenarios

| Scenario | Given | When | Then |
|---|---|---|---|
| `P0-CAND-001` | One L1 writer has clear reversible scope | It performs several local edits | `serial_reconciled` admits the complete post-delta without per-edit approval |
| `P0-CAND-002` | Non-overlapping writers share a workspace | Guarded mode is requested | `guarded_shared` is allowed only with all mechanical platform capabilities |
| `P0-CAND-003` | A formatter may touch unknown paths | Parallel benefit remains | Work moves to `isolated_candidate`; only its admitted patch may integrate |
| `P0-CAND-004` | One patch mixes allowed and forbidden paths | Admission runs | The whole patch is rejected and useful private delta is retained only for bounded rework |
| `P0-CAND-005` | A non-overlapping patch is based on an older Candidate | Admission proves content safety but dependency closure changed | Result is `accepted_revalidation_required` with a new Candidate identity |
| `P0-CAND-006` | An old generation submits after handoff or freeze | Admission compares generation | Result is `rejected_stale_result`; the current generation continues |
| `P0-CAND-007` | The workspace starts with necessary user changes | A Candidate baseline is materialized | User delta is preserved and distinguishable; a clean HEAD-only Candidate is rejected |
| `P0-CAND-008` | An Agent says done while a descendant writer is draining | Freeze is requested | The fence blocks new writes and bounded drain completes before freeze |
| `P0-CAND-009` | Only some required writers are quiescent | Freeze is evaluated | Ready partition deltas may be sealed, but no final Candidate is created |
| `P0-CAND-010` | Tool outcome is missing | Mutation closure is inspected | Closed mutation may continue from the actual snapshot; unknown mutation cannot freeze |
| `P0-CAND-011` | A mutation lands after Candidate freeze | Reconciliation detects it | Candidate and dependent verification subject are invalidated and recovery starts |
| `P0-CAND-012` | A stale mutation already landed due to boundary failure | Recovery starts | The boundary is circuit-broken, useful delta preserved, and a fresh safe Candidate is rebuilt |
| `P0-CAND-013` | An untracked fixture or generated dependency is omitted | Manifest completeness is checked | Freeze/verification intake is rejected until the actual snapshot is complete |
| `P0-CAND-014` | Equivalent patch sets arrive in different orders | Central integration runs | A fixed order produces one content result; order-sensitive semantics require rework |
| `P0-CAND-015` | Guarded, isolated and eligible serial modes are unavailable | Automatic routing is exhausted | One machine-actionable `platform_blocked` result is emitted without a repeated loop |
| `P0-CAND-016` | Eight writers issue permitted, forbidden, shared and stale operations | Eight thousand admissions are evaluated conceptually | False allow is zero and unrelated valid partitions are not globally serialized |

## 6. Expected Mechanical Outcomes

| Outcome class | Allowed outcomes |
|---|---|
| Context | `grant_exact_content`, `grant_excerpt`, `grant_summary_or_index`, `deny_irrelevant_or_duplicate`, `repartition_or_serialize_required`, `context_budget_exhausted`, `specification_gap`, `context_stale` |
| Parallel decision | `parallel_allowed`, `parallel_not_worthwhile`, `parallel_unsafe`, `needs_human_decision` |
| Activation | `boundary_active`, `activation_failed` |
| Cross-zone request | `route_to_current_writer`, `repartition_within_scope`, `serialize_shared_change`, `reject_unnecessary_request`, `human_scope_or_spec_decision` |
| Handoff | `handoff_completed`, `handoff_no_agent_delta`, `handoff_recovery_required`, `handoff_cancelled` |
| Patch Admission | `accepted_into_candidate`, `accepted_revalidation_required`, `rejected_scope_or_partition`, `rejected_stale_result`, `integration_conflict_rework_required`, `human_change_decision_required` |
| Freeze | `waiting_for_quiescence`, `partition_delta_sealed`, `candidate_frozen`, `freeze_recovery_required`, `candidate_invalidated` |
| Terminal local routing | `external_high_risk_flow_required`, `platform_blocked` |

## 7. Automation Boundary

Automation may:

- rebuild a Context Envelope from fixed authority and current source;
- deduplicate and meter content grants;
- choose serial or a mechanically supported parallel mode;
- freeze, drain, revoke, hand off and create fresh generations;
- reject stale or out-of-scope mutations;
- preserve delta and retry through a safer local mode;
- execute deterministic join and create a frozen Candidate.

Automation may not:

- change the user goal, Task Specification, acceptance or prohibitions;
- expand write scope or approve a public contract, schema or architecture change;
- treat System Map, prompt constraints, Agent claims or hooks as authority;
- weaken a mutation boundary to preserve parallelism;
- erase user changes or accept a partial final Candidate;
- authorize an external side effect;
- convert `platform_blocked` into success.

## 8. Phase 1 Capability Derivation

These fixtures require Phase 1 or later runtime capabilities for:

1. deterministic Context Envelope materialization, ledgering, deduplication and
   stale notification;
2. parallel benefit/risk evaluation with serial fallback;
3. exact-tuple partition activation through a trusted Change Guard;
4. platform capability detection and mutation-mode routing;
5. canonical resource and logical-resource resolution;
6. private Candidate materialization and local Patch Admission;
7. baseline, dirty-worktree and actual-delta reconciliation;
8. generation fencing, writer drain, revoke and safe handoff;
9. deterministic central integration and event-driven join;
10. immutable Candidate manifest creation and post-freeze invalidation;
11. bounded automatic recovery without changing specification authority;
12. capability-based System Map queries and bounded live-source fallback.

No item in this derivation authorizes runtime implementation.
