# Phase 2 Implementation Boundary

## Allowed Repository Writes After Exact Confirmation

The future Phase 2 implementation may write only:

```text
src/ddh/__init__.py
src/ddh/agent_driver.py
src/ddh/completion.py
src/ddh/context.py
src/ddh/failure.py
src/ddh/recovery.py
src/ddh/runtime.py
src/ddh/state.py
src/ddh/telemetry.py
src/ddh/test_auditor.py
src/ddh/verification.py
tests/unit/**
tests/contract/**
tests/integration/**
tests/fixtures/recovery_workspace/**
docs/operations/ddh-phase-2-recovery.md
README.md
```

This list is implementation authority only after the exact package is
human-confirmed. The current draft grants no runtime writes.

## Protected and Read-only Inputs

```text
docs/architecture/**
docs/decisions/**
docs/proposals/**
docs/semantic-specifications/ddh-phase-0/**
docs/semantic-specifications/ddh-phase-1/**
docs/semantic-specifications/ddh-phase-2/**
.github/workflows/**
AGENTS.md
.git/**
legacy ADAD repository and snapshots
```

Implementation may read these sources but must not rewrite confirmed
specifications, decisions, Phase 1 evidence or CI policy to make Phase 2 pass.

## Runtime Scope

Phase 2 may add:

- typed failure observations and classifications;
- bounded Failure Bundles;
- deterministic approved-route selection;
- progress-aware retry and recovery-budget accounting;
- structured authority, budget and platform exceptions;
- bounded failure information in Agent Work Requests;
- restart-safe local recovery state;
- reference adapters and fault injection used only by tests.

Existing Phase 1 Contracts, Candidate isolation, Test Auditor, Verification
Runner and Completion Judge may be extended only where required to consume
these Phase 2 contracts.

## Coding Profile

The confirmed Clean Code self-check profile remains applicable:

- intention-revealing names;
- single responsibility and one abstraction level;
- approximately 20 lines per function as a refactoring trigger, with justified
  readability exceptions;
- guard clauses and shallow nesting where they improve clarity;
- comments explain non-obvious reasons, not visible behavior;
- no unrelated cross-module refactoring.

These are Agent self-check expectations unless a corresponding mechanical test
exists.

## External and Destructive Boundary

Phase 2 prohibits:

- network calls initiated by DDH;
- credentials, secret stores or real external providers;
- package installation or unapproved backend creation as recovery;
- database, deployment, publication or release operations;
- branch switch, commit, push, PR or mutation of the real user workspace;
- reset, stash, destructive cleanup or deletion of unrelated user changes;
- automatic retry of uncertain external side effects;
- modification of acceptance, thresholds, risk policy, architecture, schema,
  public contract or write scope.

## Explicitly Deferred

- Multi-Agent partitioning, worker loss, handoff and Join Barrier.
- Full Verification Asset portfolio lifecycle and permanent test inventory.
- Production System Map backend design.
- Long-term learning, Attempt Ledger analysis and self-evolution.
- Candidate application to the user workspace.
- Subsystem, Domain and release completion.
- External high-risk execution.
