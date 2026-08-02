# Test Asset, Verification Subject, Verdict, and Completion State Tables

- Task Specification: `DDH-P0-SPEC-001` version `1.0.0`
- Contract references: `P0-TEST-001` through `P0-TEST-006`,
  `P0-VERIFY-001` through `P0-VERIFY-007`, and `P0-COMP-001` through
  `P0-COMP-006`

These are local state machines. They do not create a global Task lifecycle or
a permanent receipt chain.

## 1. Verification Asset independent axes

| Axis | Current state | Event or condition | Next state | Mechanical result |
|---|---|---|---|---|
| Admission | `draft` | proposer submits fixed mappings and dependency closure | `under_review` | Begin static, guard, critic, replay, probe, and reliability checks |
| Admission | `under_review` | every required admission check passes | `admitted` | Asset version may enter a current manifest |
| Admission | `under_review` | invalid mapping, weakening, failed oracle/probe, or non-reproducibility | `rejected` | Create bounded repair item; do not use formally |
| Admission | any non-final review state | secret, corruption, unsafe fixture, or unclassifiable integrity issue | `quarantined` | Isolate asset; formal selection prohibited |
| Admission | `rejected` | semantics-preserving repair proposed | `draft` on a new version | Repeat full admission; old version is unchanged |
| Semantic validity | `current` | product Candidate changes, test meaning unchanged | `current` | Set execution to `not_run`; rerun required |
| Semantic validity | `current` | dependency/schema/contract fact may change meaning | `suspect` | Perform deterministic impact and validity evaluation |
| Semantic validity | `suspect` | pinned specification and dependency closure prove same meaning | `current` | Reuse admission where approved; rerun on Candidate |
| Semantic validity | `suspect` | specification/oracle applicability no longer matches | `stale` | Exclude from formal manifest; repair or replace |
| Semantic validity | `stale` | admitted replacement closes every reference and scenario | `retired` | Physical deletion may be proposed if write-authorized |
| Candidate execution | any | new immutable Candidate/Subject | `not_run` | Historical execution cannot be reused as Candidate PASS |
| Candidate execution | `not_run` | identity-matched terminal PASS | `passed` | Contributes only to this Subject aggregation |
| Candidate execution | `not_run` | identity-matched terminal assertion failure | `failed` | Classify and route; not an automatic asset validity change |
| Candidate execution | `not_run` | runner/protocol/environment failure | `error` | Runner recovery; not product failure |
| Candidate execution | any | bound identity or invalidation epoch changes | `invalidated` | Result cannot contribute to a current verdict |

Only the conjunction `admission=admitted` and
`semantic_validity=current` is selectable for formal verification.

## 2. Test repair and defect classification

| Given | Required classification | Permitted automatic action | Prohibited action |
|---|---|---|---|
| Valid admitted asset reaches fixed oracle; actual product result differs | `product_failure` | Repair product within authorized scope and create a new Candidate/Subject | Change test oracle, fixture, threshold, or suite to match implementation |
| Fixture points to the wrong account while specification uniquely identifies the correct account | `test_implementation_defect` | Propose new fixture/asset version and repeat independent admission | Treat repaired draft diagnostic PASS as formal PASS |
| Oracle has two plausible expected values and specification chooses neither | `specification_ambiguity` | Emit structured specification decision report | Agent chooses one value or calls it a test repair |
| Runner dependency, permission, workspace, process, or protocol fails | `runner_environment_failure` | Approved runner recovery on exact Subject | Modify product or tests to accommodate a broken runner |
| Product failure and runner blocker occur in separate required shards | `mixed_failure` | Preserve and route both issue sets | Collapse to one status or erase the other failure |

## 3. Verification Subject lifecycle

| Current state | Event or condition | Next state | Result and automatic action |
|---|---|---|---|
| `intake_received` | canonical identity validation begins | `subject_validating` | Read exact pinned specification, Candidate, manifest, environment, and epoch |
| `subject_validating` | every identity matches and all required assets are admitted/current | `subject_ready` | Build immutable Execution Plan generation |
| `subject_validating` | required asset missing or admission unfinished | `verification_not_ready` | Wait for/rebuild current manifest without routine human confirmation |
| `subject_validating` | digest, Candidate, specification, environment, or epoch mismatch | `subject_rejected` | Reject stale intake and request current generation |
| `subject_ready` | plan passes budget and environment self-check | `running` | Dispatch bounded invocations |
| `subject_ready` | required work estimate exceeds remaining verification ceiling | `verification_not_ready` | Optimize equivalent schedule or emit budget conflict before execution |
| `running` | valid terminal results arrive | `aggregating` | Deduplicate, preserve mixed issues, reconcile required universe |
| `running` or `aggregating` | any bound identity changes | `invalidated` | Stop stale publication; create current Subject identity |
| `running` | runner/environment failure with safe recovery remaining | `subject_ready` | New plan/environment generation; same immutable Subject |
| `running` | safe runner routes exhausted | `aggregating` | Record bounded platform blocker once |
| `aggregating` | closure is terminal | `terminal_verdict` | Publish the two-axis verdict |

Subject readiness does not mean execution or PASS.

## 4. Invocation and runner-result lifecycle

| Current state | Input | Next state | Invariant |
|---|---|---|---|
| `planned` | exact Subject/plan/shard invocation dispatched | `dispatched` | Invocation cannot expand required work or write scope |
| `dispatched` | identity-matched runner starts | `running` | Runner/environment identity remains pinned |
| `running` | one complete structured terminal result seals | `terminal_result_sealed` | Free-form output cannot override it |
| `running` | process dies, terminal record missing/corrupt, or completeness unknown | `incomplete` | Never PASS; use bounded runner recovery |
| any | duplicate identical terminal delivery | unchanged | Idempotent; do not double-count |
| any | conflicting terminal fact for the same invocation | `protocol_error` | Quarantine conflict; never choose by arrival order |
| any | late result from old plan/Subject generation | unchanged | Ignore for current aggregation while retaining bounded diagnostic fact |

## 5. Adaptive timeout table

| Condition | Mechanical decision |
|---|---|
| Specification defines a business latency/SLO | Keep it immutable and separate from runner deadlines |
| Same suite/platform p95 exists | Include p95 in execution reference |
| Reliable collected-work estimate exists | Include estimate in execution reference |
| No declared duration, history, or reliable estimate | Use `10 minutes` bootstrap hard deadline |
| Planned reference is available | Deadline is reference × `2.0` + `30 seconds` startup margin |
| Trustworthy progress heartbeat exists | No-progress deadline is max(2 × expected interval, 120 seconds) |
| Process is silent but no trustworthy progress signal exists | Do not infer hang; use hard deadline |
| Deadline expires | Classify execution incomplete/infrastructure first; preserve product failures from other shards |
| Exact replay has no new plan, environment, strategy, or evidence | Do not retry or spend another recovery attempt |
| Termination begins | Bound process-tree termination and output drain to at most `30 seconds` grace |
| Estimate exceeds Work Package ceiling | Return `verification_plan_not_ready` before dispatch |

## 6. Subject verdict aggregation

| Required-result closure | Acceptance outcome | Completeness | Publication/routing |
|---|---|---|---|
| All required results identity-match, are complete/current, and pass | `passed` | `complete` | Publish `mechanical_verification_passed` |
| Required product failure exists; fail-fast leaves required work not run | `failed` | `incomplete` | Product repair, then a new Candidate and full final Subject |
| Product failure and exhausted required platform blocker coexist | `failed` | `blocked` | Preserve and route both |
| Required timeout has safe recovery remaining; no product verdict | `undetermined` | `incomplete` | Automatic runner recovery |
| All safe runner routes are exhausted; no product verdict | `undetermined` | `blocked` | One bounded `platform_blocked`; never product FAIL/PASS |
| Required unexpected skip, missing result, cancellation, or unknown completeness | `undetermined` unless product failure is known | `incomplete` | Finish or repair required closure |
| Bound identity changes before publication | `undetermined` | `invalidated` | Reject old aggregation; create current Subject |
| Optional result unavailable and fixed profile marks it optional | Determined only by required set | Determined only by required set | Report optional issue without dynamic downgrade |

`mechanical_verification_passed` is valid only for
`passed + complete + current`.

## 7. Completion evaluation lifecycle

Each completion level independently follows:

```text
inputs_collecting
→ canonical_reconciliation
→ closure_evaluating
→ completed | not_ready | nonpass | escalation_required
→ invalidated when a bound current input changes
```

| Level | Required current inputs | Success state | Does not imply |
|---|---|---|---|
| Work Package | Goal/scenario closure, exact Candidate/verdict, admitted/current assets, allowed diff, scope/impact/exception closure | `work_package_completed` | Subsystem integration |
| Subsystem | Required child completions, same integrated Candidate, Module interaction/regression, Subsystem scenarios/recovery/stress | `subsystem_integrated` | Domain acceptance |
| Domain | Required integrated Subsystems on same Domain Candidate, workflows/invariants/transactions/impact closure | `domain_accepted` | Release candidacy |
| Release | Required Domain/Global closure on same Candidate, cross-Domain and release/platform readiness | `release_candidate` | Deployment or external authority |

## 8. Completion transition and invalidation table

| Current fact pattern | Mechanical decision |
|---|---|
| All Module Work Packages completed on isolated Candidates | Do not publish `subsystem_integrated` |
| Required Modules and Subsystem scenarios pass on one integrated Candidate | Publish `subsystem_integrated` if all other closure is current |
| Higher-layer integration defect is isolated and lower contracts remain proven | Keep unaffected lower completion; create higher-layer repair |
| Higher-layer failure proves a lower implementation/specification/test gap | Invalidate only proven affected lower result and dependent levels |
| Child completions refer to different Candidate identities | `not_ready`; never combine them |
| Outside-scope regression is required but repair needs new write authority | Verification may expand; completion waits for versioned scope decision |
| Map misses a live dependency | Include live-discovered node, trigger Map maintenance, and reassess closure |
| Map unavailable but bounded live-source fallback closes impact | Continue; Map status is not acceptance authority |
| Neither Map nor fallback can bound impact | `not_ready`/`impact_unknown`; no completion |
| Invalidation races a completion publication | Invalidation wins; stale completion is not consumable |
| Duplicate/late/out-of-order child events arrive | Reconcile canonical identities; result is idempotent |
| Judge restarts after event loss | Rebuild from current canonical facts; no historical PASS chain required |
| Release candidate is published | Remain outside deployment/credential/database/network authority |

## 9. Retention

Asset source, required fixtures/helpers/configuration, environment declarations,
seeds, and workload models remain rerunnable evidence. Invocation/result
envelopes, verdicts, completion decisions, raw output, and temporary
reconciliation state remain only until their current repair/completion consumer
has reliably consumed them, then become deletion-eligible.
