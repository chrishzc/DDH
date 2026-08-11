# Phase 3 Runtime Requirements

## 1. Required Vertical Slice

```text
confirmed L2 Subsystem Task Specification
→ actual-only System Map scope and dependency query consumed
→ parallel benefit and safety decision
→ Module work groups, product/test lanes and bounded Context Envelopes
→ Change Guard boundary activation for exact lane generation
→ asynchronous construction, local feedback and bounded recovery
→ shared-resource requests, invalidation or safe handoff as needed
→ current lane submissions and serialized central Patch Admission
→ mechanical quiescence, deterministic Join Barrier and Candidate freeze
→ refreshed System Map impact closure plus live reconciliation
→ integrated Module, Subsystem and affected regression verification
→ Completion Judge
```

Phase 3 orchestrates multiple writers through typed ports. The reference
implementation may use deterministic in-process worker adapters and disposable
private Candidates; it must not embed a specific coding model, vendor Agent API,
remote queue or permanent service.

## 2. Parallel Decision

The Work Coordinator returns exactly one result:

| Result | Required action |
|---|---|
| `parallel_allowed` | Build mechanically separated lanes because independence, capability and net benefit are demonstrated. |
| `parallel_not_worthwhile` | Preserve the fixed work and execute serially because Context, environment, Critic or integration cost removes the benefit. |
| `parallel_unsafe` | Execute serially because physical or logical write boundaries cannot be made safe. |
| `needs_human_decision` | Stop only affected work because parallelization would change specification, architecture, scope or risk policy. |

The decision consumes work independence, physical and logical overlap, Module
coupling, Context cost, environment setup, integration cost, expected wall-time
benefit, recovery risk, worker capability and all separated budgets. It records
reasons, inputs and the selected safe mode without imposing a universal score.
Uncertain overlap cannot yield `parallel_allowed`.

The decision is reevaluated when cross-zone requests, shared-resource churn,
Context expansion or integration rework erase the expected benefit. A safe
parallel-to-serial fallback preserves admitted delta, fixed acceptance and
remaining budgets without asking a human.

## 3. Work Groups, Lanes and Context

A Module Work Group binds one Module sub-goal to:

- a product lane;
- an independent acceptance-asset lane where required;
- fixed Module and Subsystem acceptance references;
- current Candidate and group generation;
- shared-contract dependencies;
- composite readiness and join membership.

Each write lane binds its own trusted writer, generation, base Candidate,
allowed physical and logical resources, protected resources, Context Envelope,
local feedback, budget, escalation rules and submission contract. Test assets,
fixtures, helpers and test configuration are writes. Product writers may create
diagnostic checks for local feedback, but cannot author or admit the protected
acceptance assets used as final evidence.

Context Envelopes contain only pinned goal, relevant acceptance, needed
contracts, bounded System Map summaries, source selectors, read/write
information, budget and escalation conditions. A Context grant changes readable
working material only. It never activates writes or expands scope. Duplicate or
broad requests are summarized, denied or charged according to the confirmed
Context profile without blocking unrelated lanes.

## 4. Mechanical Activation and Write Assignment

Public runtime vocabulary uses the role names `Work Coordinator`, `Change
Guard` and `Test Auditor`. Historical PWC/CIM abbreviations are not required in
public APIs.

The Work Coordinator first creates a planned write assignment. The Change Guard
resolves actual resources and returns `boundary_active` only for the exact:

```text
Work Package + lane + generation + trusted writer
+ base Candidate + resource-set digest + mutation mode + boundary instance
```

Only after that matching result may the coordinator mark the lane active and
expose a write-capable driver. A prompt whitelist is not a boundary. Missing,
stale or mismatched activation automatically tries an approved isolated or
serial route and otherwise emits one `platform_blocked` result.

Supported local modes remain:

- `serial_reconciled` for one eligible writer;
- `guarded_shared` only when the platform self-check proves identity,
  interception, containment, canonicalization, reconciliation and revoke; and
- `isolated_candidate` for private writes followed by central admission.

`serialized_shared_resource` is a coordination strategy, not a fourth mutation
mode. External side effects are outside all local modes.

## 5. Shared Resources and Cross-Lane Requests

Resources are physical paths and logical units such as public interfaces,
schemas, state definitions, root configuration, lockfiles, shared fixtures,
manifests and generator/output groups.

- Unapproved shared contracts remain frozen.
- An approved shared change has exactly one active writer.
- Independent lanes continue while a shared resource is serialized.
- A cross-lane request does not grant a write.
- An admitted shared change creates a new Candidate generation and invalidates
  only dependent active lanes.
- Repeated reciprocal requests trigger repartition or serial fallback.
- A required scope, architecture, schema or public-contract expansion creates a
  structured exception and preserves existing Candidate delta.

## 6. Submission, Handoff and Central Admission

A lane submission is only `candidate_subresult_submitted`. It binds the current
Task Specification, Work Package, lane generation, trusted writer, base
Candidate, actual touched resources, delta manifest, local feedback and
unresolved requests.

Central Patch Admission is serialized by Candidate generation and checks:

1. current specification, Work Package, lane, writer and generation;
2. complete actual delta against physical and logical scope;
3. protected and shared-resource conflicts;
4. base, dependency and content freshness;
5. complete deterministic application with no undeclared delta;
6. new Candidate identity and required revalidation.

A patch mixing allowed and forbidden resources is rejected as a whole. The
private delta may be retained for bounded rework but does not enter the
integration Candidate. Order-sensitive patch sets are an integration conflict;
the runtime cannot choose the order that happens to pass.

Safe handoff fences the old generation, settles or classifies in-flight writes,
preserves distinguishable user and Agent delta, proves mutation closure, revokes
the old boundary and activates a new generation from the latest admitted
Candidate and bounded Context increment. Timeout, heartbeat loss, process exit
or Agent acknowledgement alone cannot prove handoff safety.

## 7. Module Readiness and Join Barrier

A Module Work Group is ready only when all are true:

```text
product writer quiescent
+ immutable current Module snapshot
+ required independent Module assets admitted
+ Module verification passed on that snapshot
+ no unresolved shared-contract request
+ actual diff mapped through a consumed System Map query or bounded fallback
```

Early groups enter `waiting_for_subsystem_join`, release Agent/runner resources
and consume no tokens while waiting. A changed shared dependency wakes only
affected groups and gives them new generations.

The automatic Join Barrier requires every required group current and ready, all
registered product writers mechanically quiescent, all required test writer
generations sealed, all required test assets admitted, no unresolved shared
mutation and pinned shared contracts. It then:

1. admits deltas in the fixed integration order;
2. reconciles the actual integrated diff;
3. consumes fresh System Map changed-node, dependency and reverse-dependency
   facts, with bounded live-source fallback where needed;
4. freezes one immutable Subsystem Candidate and manifest; and
5. creates the integrated Verification Subject.

Fence creation precedes drain. Post-fence and stale operations are rejected.
Verification cannot begin while any target writer or candidate mutation remains
possible. A late mutation invalidates the Candidate and Subject and enters
bounded Phase 2 recovery.

## 8. Integrated Verification and Completion

The integrated Verification Subject contains:

- all required Module acceptance assets rebound to the integrated Candidate;
- Subsystem business scenarios and state/contract integration checks;
- affected reverse-dependent regression assets selected from consumed impact
  facts; and
- only the concurrency, load, soak or recovery profiles required by the fixed
  specification or approved project profile.

Module-local PASS cannot be combined into Subsystem PASS. Required Module tests
rerun against the integrated Candidate. A Subsystem failure expands analysis to
the Subsystem level, but the Work Coordinator reopens only the Module lanes
whose actual responsibility is demonstrated. A necessary outside-scope repair
creates an exception; impact discovery does not grant write authority.

`work_package_completed` and `subsystem_integrated` are separate decisions with
separate inputs. The reference Subsystem fixture requires both. Domain and
release completion remain `not_evaluated`.

## 9. Failure, Restart and Cost Boundary

- Phase 2 failure classification, bounded Failure Bundles, progress dimensions,
  no-progress rejection and structured exceptions remain applicable per lane
  and integration generation.
- Coordinator and Change Guard state uses atomic generation updates and
  idempotent event handling; restart reconstructs current lanes, boundaries,
  submissions and Candidate generations from bounded manifests.
- Duplicate, stale and late events are ignored or rejected without reopening a
  sealed generation.
- Waiting, join evaluation, invalidation routing and deterministic scheduling
  require zero Agent tokens.
- Parallel work is not admitted unless projected wall-time benefit exceeds
  additional Agent, Context, environment, Critic and integration cost.
- No budget pressure may weaken scope, acceptance, oracle, mutation boundary,
  required verification or external authority.

## 10. System Map Consumption

The System Map adapter remains capability-based and schema-neutral. Phase 3
must consume a branch/ref/commit/Candidate-bound result:

1. before the fork decision;
2. while resolving physical and logical write assignments;
3. when materializing each bounded Context Envelope;
4. when reconciling every admitted actual delta;
5. immediately before join/freeze;
6. after an integrated Subsystem failure; and
7. before impact closure and completion.

Consumption means the downstream decision stores the query result identity and
the nodes/relations actually used. Query invocation alone is insufficient.
Partial, conflicted or unavailable areas use bounded live-source discovery.
Only unresolved `impact_unknown` blocks an impact-complete claim. Pending System
Map maintenance does not normally block functional completion.

