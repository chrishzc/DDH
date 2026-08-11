# Phase 3 Reference Parallel Subsystem Fixture

## Purpose

The reference fixture extends the disposable portable workspace used by Phase
1/2. It proves real coordination semantics without adding an unrelated product
domain, invoking a remote Agent or modifying the user's workspace.

## Business Scenario

The `PortableWorkspace` Subsystem contains three Modules:

1. `PathNormalizer` canonicalizes platform-aware workspace paths and rejects
   escape attempts;
2. `ManifestLoader` reads and validates portable manifest entries; and
3. `ManifestIndex` joins normalized paths with loaded entries and rejects
   duplicate logical resources.

The confirmed Subsystem behavior is:

```text
raw workspace root + manifest document
→ validated entries
→ canonical portable paths
→ deterministic searchable index
```

The final index must be independent of worker completion order, reject paths
outside the workspace, preserve distinct case semantics by platform profile,
reject duplicate logical resources, and never publish a partially built index.

## Required Parallel Shape

The fixture declares three Module Work Groups. Each group has:

- one product lane with a disjoint `src/portable_workspace/<module>/**` zone;
- one independent acceptance lane with a disjoint
  `tests/acceptance/portable_workspace/<module>/**` zone; and
- fixed Module scenarios and a shared Subsystem contract.

One additional Subsystem acceptance lane writes only
`tests/acceptance/portable_workspace/subsystem/**`. It may prepare the
cross-Module scenarios while product work is active, but its assets require
independent Test Auditor admission and cannot complete the Work Package.

The shared manifest event contract and shared fixture schema are owned by the
integration lane. No child lane may change them.

## Normal Flow

1. A branch/Candidate-bound System Map query locates the three Modules and their
   intersections; the partition plan records the consumed nodes and relations.
2. Cost and safety assessment returns `parallel_allowed`.
3. The Change Guard activates exact write assignments before drivers receive
   write capability.
4. Product and acceptance lanes execute asynchronously. `PathNormalizer` and
   `ManifestIndex` finish before `ManifestLoader` and wait with no Agent use.
5. Each Module becomes ready only after product quiescence, test admission and
   current Module verification.
6. The Join Barrier admits all current deltas in the fixed order
   `PathNormalizer`, `ManifestLoader`, `ManifestIndex`, `SubsystemAcceptance`.
7. Actual diff and reverse-dependency closure are refreshed and consumed.
8. The Change Guard freezes one immutable Subsystem Candidate.
9. Required Module assets rerun against the integrated Candidate, followed by
   Subsystem scenarios and affected regressions.
10. Completion Judge evaluates Work Package completion and Subsystem integration
    separately; both pass for this fixture.

## Required Fault Injections

The fixture must deterministically support:

- implementation lane and acceptance lane both request one shared fixture;
- an acceptance patch arrives before its product implementation and is
  provisionally RED;
- a child tries a cross-zone product/test write;
- a formatter declares narrow output but touches a protected root resource;
- an old writer submits after handoff;
- a writer disappears with mutation closure known and unknown variants;
- only two of three Modules are quiescent at a freeze request;
- two individually valid patches conflict semantically after integration;
- patch application order changes output;
- a shared contract change invalidates only two dependent groups;
- actual touched resources reveal one missed reverse dependent;
- a necessary repair lies outside write scope;
- expected parallel benefit disappears after repeated cross-lane requests;
- a post-fence background write races with Candidate freeze;
- restart replays duplicate and out-of-order coordination events.

## Invariants

- User baseline and Agent delta remain distinguishable.
- Test assets are construction writes and cannot self-admit.
- No lane is active before the matching mechanical boundary.
- No shared logical resource has two active writers.
- No stale generation, mixed-scope patch or late write enters the Candidate.
- No final Candidate exists until all required writers are quiescent.
- Worker finish order does not change integration content or completion.
- Waiting and join reevaluation use zero Agent tokens.
- System Map data is consumed as actual-index evidence only.
- Serial fallback preserves valid delta and all fixed acceptance.

## Completion

The fixture completes only when:

- both the independent product/test mode and three-Module fork/join mode pass;
- the frozen Candidate is immutable and fully bound to current assets;
- Module tests rerun on the integrated Candidate;
- all fixed Subsystem scenarios and affected regressions pass;
- `work_package_completed` and `subsystem_integrated` are independently true;
- `domain_accepted` and `release_candidate` are `not_evaluated`; and
- no human checkpoint occurs during routine activation, waiting, handoff,
  recovery, fallback, join, verification or completion.

