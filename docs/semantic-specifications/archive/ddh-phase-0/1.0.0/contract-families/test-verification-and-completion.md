# Test, Verification, and Completion Contract Family

- Contract family: `P0-TEST-VERIFY-COMP`
- Task Specification: `DDH-P0-SPEC-001` version `1.0.0`
- Status: Phase 0 executable semantic projection
- Runtime authority: None

## 1. Purpose

This family defines how reusable Verification Assets become admissible, how a
Verification Runner evaluates one immutable Verification Subject, and how a
Completion Judge decides each completion layer without treating a lower-layer
PASS as an upper-layer completion.

The family is runner-neutral. Pytest is the Python reference adapter; a fixed
command, build, lint, type, schema, security, integration, load, or soak check
uses the same subject, result, verdict, and completion semantics.

## 2. Authority

Behavior and acceptance come from the pinned Task or Layer Specification.
Applicable accepted authority inputs are:

- Decision 0008: Verification Assets and layered verification.
- Decision 0009: runner hardening and adaptive bounded timeouts.
- Decision 0020: layered quality profiles and independent add-ons.
- Decision 0021: separated budgets and timeout bootstrap parameters.
- `TAQG-QUAL-001`, `TAQG-QUAL-003`, `TAQG-ASSET-001`, and
  `TAQG-PORT-001`.
- `CIM-MVE-001`, `MVE-RESULT-001`, `MVE-EXEC-001`, `MVE-RUN-001`,
  `MVE-OBS-001`, `MVE-PROTO-001`, and `MVE-VERDICT-001`.
- `DDH-COMP-001`.

Test names, paths, discovery metadata, System Map results, runner output, Agent
claims, and prior PASS results are not acceptance authority.

## 3. Verification Asset contracts

### P0-TEST-001: Rebuildable Verification Asset inventory

A project-owned, versioned Test Layout Profile declares discovery roots or
colocation rules, discovery adapter, include and exclude rules, dependency
roots, metadata extraction, generated-asset handling, and path normalization.

Discovery produces a rebuildable inventory. Every formal acceptance asset must
resolve:

```text
specification reference
+ business scenario reference
+ verification layer
+ behavior class
+ target node references
+ fixture/helper/configuration dependency closure
+ exact content identities
```

The inventory is a derived index. A path, filename, marker, or discovered item
cannot grant admission or required status. Missing or ambiguous mapping creates
a coverage or inventory defect; it must not be guessed from naming similarity.

### P0-TEST-002: Three independent asset state axes

Each asset version keeps independent state:

```text
admission:
  draft | under_review | admitted | rejected | quarantined

semantic validity:
  current | suspect | stale | retired

candidate execution:
  not_run | passed | failed | error | invalidated
```

`superseded_by` is a version relation, not an execution result. An admitted
asset may be `current + not_run` for a new candidate. A product source change
requires a rerun but does not by itself make the test semantics stale.

Only `admitted + current` assets may enter a formal immutable Test Asset
Manifest. A required flaky, suspect, stale, quarantined, retired, unmapped, or
missing asset makes formal verification not ready unless an equivalent admitted
asset already preserves the fixed scenario and oracle.

### P0-TEST-003: Quality applicability compilation

The Test Auditor deterministically compiles:

```text
verification scope layer
+ independent quality add-ons
+ specification-sourced product thresholds
```

Scope is one of `Static`, `Module`, `Subsystem`, `Domain`, or `Global`.
Independent add-ons include boundary/negative, state transition, data
integrity, idempotency, concurrency, failure/recovery,
compatibility/migration, security, performance/load, soak, and external-effect
isolation.

Before admission, every add-on is either:

- `required`; or
- `not_applicable_with_business_reason`.

`conditional` is permitted only while a mechanically obtainable fact is
pending. If the specification, approved profile, System Map facts, and bounded
live-source facts cannot resolve a material quality choice, the result is
`quality_policy_gap`; an Agent cannot guess N/A.

System Map fanout may require dependency regression. It cannot alone invent
load, rate, latency, or soak requirements. Product thresholds come only from
the specification or an approved versioned default.

### P0-TEST-004: Admission and independent anti-weakening

Formal admission follows:

```text
fixed specification and scenarios
→ deterministic mapping/static validation
→ Mechanical Acceptance Guard
→ independent Test Critic
→ scenario replay
→ required fault-sensitivity probes
→ determinism/isolation checks
→ immutable admitted manifest
```

The proposer cannot admit its own asset. The guard rejects unapproved:

- assertion deletion or weakening;
- expected-value widening;
- product threshold lowering;
- fixture or workload shrinking;
- case removal;
- new skip or xfail;
- required marker removal;
- suite exclusion.

Critic prose is not mechanical authority. Admission requires fixed authority
references and reproducible results. A critic outage cannot become
self-approval.

### P0-TEST-005: Currentness, repair, supersession, and deletion

Validity evaluation occurs:

- when a Work Package begins, to project reusable current assets;
- while constructing tests, when specification/test/fixture/helper/contract/
  schema/toolchain identities change;
- after Candidate freeze, against the fixed Candidate and current
  specification;
- before immutable manifest publication;
- during verification when any bound identity or invalidation epoch changes.

A test implementation defect may be repaired automatically only when its
expected behavior remains identical. The proposer creates a new asset version;
the full guard, critic, replay, and applicable probes readmit it. An oracle
ambiguity or changed expected behavior is a specification decision, not a test
repair.

Physical deletion requires either formal scenario removal or an admitted
replacement, reference and coverage closure, independent anti-weakening review,
and write authority. Otherwise an old asset remains stale or retired.

### P0-TEST-006: Long-term evidence and portfolio health

Long-term evidence consists of the confirmed specification plus admitted,
rerunnable Verification Assets and their required fixtures, helpers,
configuration, environment profiles, seeds, and workload models. Routine
stdout, traceback, historical PASS receipts, shard results, Agent conversation,
and complete Attempt Ledgers are not permanent evidence.

Portfolio health reports semantic fidelity, fault sensitivity, execution
reliability, lifecycle validity, and cost separately. It must not hide a
blocking gap in a single aggregate score. Deduplication requires proof that
scenario coverage, input partitions, oracle strength, layer coverage, and
fault detection do not decrease.

## 4. Verification execution contracts

### P0-VERIFY-001: Immutable Verification Subject

Formal verification intake binds at least:

```text
work_package_id
+ task_specification identity/version/digest
+ frozen_candidate identity/manifest digest
+ verification_contract identity/version
+ admitted_test_asset_manifest identity/digest
+ execution_environment_profile identity/version
+ invalidation_epoch
```

Every identity must match canonical current state. The Runner has read-only
access to the Candidate and admitted asset set. Missing required coverage,
non-current assets, digest mismatch, or an epoch race produces
`verification_not_ready`, `subject_rejected`, or `subject_invalidated`; the
Runner cannot silently omit work.

A Candidate, specification, asset, fixture/helper closure, environment
semantics, or invalidation epoch change creates a new Subject identity. Old
results cannot be relabeled for it.

### P0-VERIFY-002: Execution Plan and budgets

An Execution Plan is a derived, immutable-generation projection of the Subject
and admitted quality contract. It fixes suites, triggered conditions,
thresholds, seeds, environments, shards, ordering constraints, resource
limits, deadlines, retry policy, and fail-fast policy.

The scheduler may change only semantics-preserving ordering, sharding,
parallelism, runner placement, and approved cache use. It cannot drop a
required suite, lower a threshold, change an oracle, or turn required into
optional/N/A.

Required verification has priority. If the estimated required work exceeds the
remaining verification budget, planning returns
`verification_plan_not_ready` before execution. It may optimize with caching,
sharding, ordering, parallelism, or an approved equivalent backend; it cannot
buy budget by weakening acceptance.

### P0-VERIFY-003: Structured invocation and observed result

Each invocation binds exact Subject, plan generation, suite/assets, shard,
runner/environment, deadline, output contract, and attempt. Each invocation has
at most one current sealed terminal result.

Terminal execution facts distinguish at least:

- passed;
- failed;
- timeout;
- tool error;
- cancelled;
- incomplete.

Free-form stdout, exit code, or an Agent interpretation cannot alone publish a
formal outcome. Identity mismatch, corrupt or missing terminal result, unknown
completeness, duplicate conflicting terminal facts, or a partial result is not
PASS.

Duplicate and late identical delivery is idempotent. Out-of-order delivery may
wait for bounded reconciliation. A stale generation cannot overwrite a current
terminal fact.

### P0-VERIFY-004: Failure classification and routing

Observed execution facts produce two independent decisions:

```text
failure_classification
+ impact_scope_assessment
```

Failure classification distinguishes `pass`, `product_failure`,
`test_implementation_defect`, `runner_environment_failure`,
`specification_ambiguity`, `mixed_failure`, and `unknown`. `not_run` and
`blocked` are execution/closure states, not product failure.

Impact assessment distinguishes within planned closure, expanded verification
closure, write-scope expansion required, architecture/contract change
required, behavior specification change required, Map/live-source conflict,
and impact unknown.

Expanded verification never grants write permission. System Map is queried
with actual diff or failed-scenario facts and its result must be consumed in
suite and impact closure. Live source corrects a missing Map relation for the
current closure and triggers Map maintenance. If neither can bound impact,
completion is blocked.

### P0-VERIFY-005: Adaptive bounded timeout and automatic runner recovery

The Runner keeps four distinct time concepts:

1. specification-owned business performance threshold;
2. planned execution deadline;
3. no-progress deadline, only with a trustworthy progress signal;
4. process termination and output-drain grace.

Bootstrap planning uses:

```text
reference =
  max(declared duration, same-suite/platform p95,
      collected-work estimate, profile floor)

execution deadline =
  reference * approved safety factor + startup margin
```

The bootstrap safety factor is `2.0`, startup margin is `30 seconds`, and a
normal asset without a declared duration, history, or reliable estimate gets a
`10 minute` hard execution deadline. Termination/output drain grace is at most
`30 seconds`. With trustworthy progress, no-progress is
`max(2 * expected progress interval, 120 seconds)`. Silence alone is not a
hang.

Timeout is infrastructure/execution-incomplete evidence, not product failure.
Retry requires new mechanical information such as a repaired environment, new
plan generation, or approved shard/backend change. Exact inputs, strategy, and
failure fingerprint without new evidence must not consume another attempt.
Safe runner recovery may rebuild workspace/environment/cache or use an approved
equivalent backend while preserving the exact Subject. Exhaustion produces one
bounded `platform_blocked`.

### P0-VERIFY-006: Bounded output and evidence completeness

Byte, line, and event limits apply while draining subprocess output. Repeated
tracebacks are clustered by root fingerprint, stress metrics aggregate at
source, and parallel shards may share one setup-failure reference while
preserving member identities and executed/not-run counts.

Truncation never changes the structured terminal outcome. Minimum identity,
terminal, completeness, threshold, mixed-failure, and outside-scope facts
cannot be evicted. If buffer failure makes those facts unverifiable, the result
is `evidence_incomplete`, never PASS.

Routine PASS provides a bounded structured summary to current consumers.
Unbounded output from tests routes to Test Asset repair; runner reporter storms
route to runner recovery; product log storms preserve the product
classification. Secret-like output is quarantined and never injected into an
Agent context.

### P0-VERIFY-007: Subject verdict

The fixed required-result universe includes all required suites, layers,
affected regressions, applicable stress profiles, platforms, and suites
triggered by fixed conditional rules.

Verdict has independent axes:

```text
acceptance_outcome:
  passed | failed | undetermined

verification_completeness:
  complete | incomplete | blocked | invalidated
```

`mechanical_verification_passed` exists only for:

```text
passed + complete + current Subject
```

All required terminal results must be identity-matched and integrity-validated;
required unexpected skip/not-run/cancelled/incomplete results, unresolved
failures, ambiguity, tool defects, or impact closure prevent PASS. Mixed
product and infrastructure outcomes remain visible together.

Fail-fast may produce `failed + incomplete` for a disposable failed Candidate.
After repair, a new Candidate creates a new Subject whose final acceptance
must execute the complete required universe.

## 5. Layered completion contracts

### P0-COMP-001: Independent completion levels

The Completion Judge evaluates each level separately:

```text
work_package_completed
!= subsystem_integrated
!= domain_accepted
!= release_candidate
!= external_operation_approved
```

Each evaluation binds its own current Candidate, specification, required child
results, required mechanical verdict, scope/diff closure, exception closure,
and risk/external boundary.

### P0-COMP-002: Work Package completion

`work_package_completed` requires:

- the Agent goal, required behavior, and acceptance scenarios are closed;
- current immutable Candidate has matching
  `mechanical_verification_passed`;
- actual diff and created/deleted resources are within allowed scope;
- no prohibited mutation or unclassified baseline contamination exists;
- all required assets are admitted/current with no required missing,
  unexpected skip, not-run, suspect, or stale coverage;
- specification, scope, architecture, contract, risk, and external exceptions
  are closed;
- touched-resource and failure impact closure has no unknown outside-scope
  product effect;
- all bound identities remain current at publication.

This completion says nothing about integration with another Work Package.

### P0-COMP-003: Subsystem integration

`subsystem_integrated` additionally requires all required Modules/Work Packages
to operate on the same integrated Candidate, Module contracts and state/data/
error interaction to pass, affected Module regressions to rerun on that
Candidate, and required Subsystem business, boundary, recovery, and
risk-adjusted stress scenarios to pass.

Even a Work Package scoped to a whole Subsystem does not gain this status from
its name. It needs its own integrated-candidate evaluation.

### P0-COMP-004: Domain acceptance

`domain_accepted` requires all required Subsystems on the same Domain Candidate,
Domain end-to-end workflows and invariants, cross-Subsystem transactions,
consistency, compensation, permissions, recovery, and applicable capacity/
concurrency/load/soak/degradation checks. System Map and bounded live-source
impact closure must cover affected external nodes; scope-external repairs need
separate write authority.

### P0-COMP-005: Release candidacy

`release_candidate` requires all required Domain/Global acceptance on one
Candidate plus cross-Domain regressions, security, compatibility, migration,
packaging, configuration, operational readiness, required platform matrix, and
release performance profile closure.

It grants no deployment, production database, credential, network,
publication, or other external-side-effect authority.

### P0-COMP-006: Invalidation and recovery

Completion events are at-least-once notifications. Before publication the Judge
reconciles current canonical identities. Duplicate, late, and out-of-order
events are idempotent. A changed child completion, Candidate, specification,
verdict, scope closure, or exception invalidates only the affected completion
level and its dependents.

A higher-layer integration defect does not automatically revoke valid
lower-layer completion. If evidence proves a lower-layer implementation,
specification, or test gap, only the proven affected lower result is
invalidated. If impact is unknown, Map and bounded live-source discovery must
close it before completion.

The Judge may rebuild current evaluation after restart without historical PASS
receipts or an Agent.

## 6. Required scenario classes

The machine-readable fixture family covers:

- normal asset admission, Subject PASS, and Work Package completion;
- rejected assertion weakening and missing/stale asset use;
- test implementation defect versus product defect;
- Subject invalidation racing PASS publication;
- duplicate/out-of-order Runner and completion events;
- automatic runner recovery and semantics-preserving test repair;
- verification budget insufficiency without quality weakening;
- adaptive timeout for normal long and truly stalled execution;
- bounded million-line output and 10,000-reference aggregation;
- Module completion without automatic Subsystem integration;
- successful same-Candidate Subsystem integration after all required Module,
  interaction, recovery and stress checks pass;
- all required child Work Packages first complete against that same integrated
  Candidate before Subsystem evaluation starts;
- Subsystem integration failure with unaffected lower completion;
- Domain and release separation, including no deployment authority.

## 7. Immutable authority boundaries

Automation and self-evolution may optimize discovery, caching, batching,
sharding, scheduling, failure clustering, summaries, and equivalent runner
selection. They cannot change:

- specification-owned expected behavior or product thresholds;
- required scenario, layer, add-on, suite, platform, or oracle;
- asset admission, validity, anti-weakening, and retirement rules;
- immutable Subject identity and invalidation precedence;
- failure/impact classification semantics;
- PASS closure or completion-level semantics;
- write scope, architecture, contract, risk, or external authority;
- Evidence Retention and fail-closed requirements.
