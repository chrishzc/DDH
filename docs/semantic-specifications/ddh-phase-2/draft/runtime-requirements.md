# Phase 2 Runtime Requirements

## 1. Required Vertical Slice

```text
Phase 1 typed result or execution failure
→ deterministic failure classification
→ bounded Failure Bundle
→ approved Recovery Policy projection
→ progress and budget admission
→ automatic route or structured exception
→ new typed generation when facts changed
→ repair, re-freeze and re-verify
→ Completion Judge
```

This remains one serial main-Agent execution lane. Phase 2 does not implement
parallel workers, ownership handoff or Join Barrier.

## 2. Failure Model

A `FailureObservation` binds:

- failure class and reason code;
- Specification, Invocation, Candidate and Verification Subject identities;
- current Verification Asset identities and failed scenario IDs;
- affected nodes, resources, actual-diff summary and consumed impact query;
- retryability and external-side-effect uncertainty;
- bounded diagnostic bytes and the first useful traceback location;
- current Context, environment and strategy generations.

The classifier is deterministic and does not call an Agent or model. Unknown or
mixed facts remain unknown or mixed; they are never guessed into product
failure or PASS.

## 3. Required Classes and Routes

| Failure class | Fixed route |
|---|---|
| `product_failed` | Main Agent repairs inside current scope, creates a new Candidate and reruns fixed acceptance. |
| `test_implementation_defect` | Test repair proposal, anti-weakening audit, independent admission and known-bad probe. |
| `test_semantics_uncertain` | Stop affected work with a specification-gap exception; do not choose an oracle. |
| `runner_failed` | Rebuild disposable environment or select one approved equivalent backend for the same immutable Subject. |
| `tool_backend_unavailable` | Select only a configured approved backend; never invent policy or install packages. |
| `context_insufficient` | Provide a purpose-bound, budgeted Context increment without granting writes. |
| `system_map_unavailable` | Use bounded live-source fallback only for the affected query area. |
| `candidate_stale` | Reject the old result and create or select the current Candidate generation. |
| `test_asset_stale` | Re-evaluate validity and admit a current asset version before execution. |
| `impact_underestimated` | Expand read and verification closure; write authority remains unchanged. |
| `scope_expansion_required` | Preserve Candidate and diff, then emit a structured scope exception. |
| `external_side_effect_uncertain` | Do not execute or retry; route to the independent high-risk boundary. |

## 4. Failure Bundle

`FailureBundle` is a bounded, typed projection and must contain:

- failure class and normalized reason code;
- exact Candidate, Subject, asset and scenario references;
- first useful traceback location and bounded output excerpts;
- affected nodes and resources plus actual-diff summary;
- consumed System Map query or live-source fallback facts;
- attempted routes, retryability, progress dimensions and remaining budgets;
- allowed machine actions and required human authority, if any.

The Bundle must exclude complete logs, repeated tracebacks, source files,
prompts, conversations, secrets and unrelated metrics. Truncation and omitted
counts remain explicit.

## 5. Recovery Policy and Progress

Recovery Policy is compiled from the confirmed Task Specification, approved
project profile and fixed bootstrap profile. It cannot add authority.

Every continuing attempt must change at least one progress dimension:

- Candidate generation;
- Verification Asset generation;
- environment generation;
- approved Context generation;
- impact discovery generation;
- approved recovery strategy.

An identical input, failure fingerprint and strategy without new evidence is
rejected before consuming another Agent or runner attempt. New evidence does
not reset budget already consumed.

## 6. Test Repair Boundary

Phase 2 orchestrates a bounded test-repair route; it does not implement the
full test portfolio lifecycle.

- Expected behavior, required scenarios and thresholds stay immutable.
- The repair proposer cannot admit its own asset.
- Anti-weakening checks block assertion deletion, expected-value widening,
  threshold lowering, fixture shrinking, case removal, skip, xfail and suite
  exclusion.
- The repaired asset requires independent admission, original-scenario replay
  and an executed known-bad probe.
- If semantics are uncertain or the Critic/admission route is unavailable,
  Phase 2 emits a structured exception instead of self-approval.

## 7. Runner and Tool Recovery

- Capability state distinguishes configured, available, self-checked, ready,
  unhealthy and incompatible.
- Recovery may rebuild temp workspace, process instance or environment cache.
- Fallback may select only an approved equivalent backend.
- The Candidate, Subject and acceptance identities remain unchanged across
  runner recovery.
- Recovery cannot edit product or tests, lower required verification, access a
  real external service or mutate the user workspace.
- Exhausted safe routes produce one `platform_blocked` exception, not product
  failure.

## 8. Context, System Map and Impact

- Context expansion is purpose-bound, deduplicated and budgeted.
- System Map remains an actual-architecture index, not an authority source.
- Map unavailable or partial routes to bounded live-source fallback.
- Actual diff and failed scenarios trigger a fresh impact query.
- Discovered reverse dependents may expand verification automatically.
- Outside-scope repair produces `scope_expansion_required`; it never grants a
  hidden write.

## 9. Structured Exception

The report binds:

- current and requested authority class;
- blocked lane and transition;
- trigger, observed evidence and failure Bundle identity;
- affected nodes, resources and contracts;
- consumed Map query and live-source confirmation;
- safe actions attempted and remaining budget;
- preserved Candidate, diff and Verification Subject;
- requested authority change;
- verification and external impact;
- bounded options, tradeoffs and unaffected work.

Report creation is idempotent for the same subject and reason. It cannot update
the current Task Specification or confirmation.

## 10. State, Restart and Telemetry

- Recovery state is local per Invocation and is not a global governance state
  machine.
- Atomic JSON generation and compare-and-swap protect current route state.
- Restart reconstructs the current attempt ledger from canonical identities
  and bounded attempt summaries.
- Duplicate and stale observations are idempotent or rejected.
- Telemetry remains bounded, contains no raw diagnostics or secrets, and is not
  completion evidence.
- Temporary attempts may be deleted after terminal handoff; Candidate and diff
  required by an exception remain available.

## 11. Completion Boundary

Completion Judge rejects:

- stale Candidate, Subject or asset identities;
- incomplete or unknown verification;
- required scenarios without current results;
- open authority, budget, platform or external exceptions;
- verification closure that did not consume newly discovered impact.

Only Work Package completion may be published. Higher-layer completion remains
not evaluated.
