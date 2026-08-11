# Phase 3 Implementation Boundary

## Allowed Repository Writes After Exact Confirmation

The future Phase 3 implementation may write only:

```text
src/ddh/__init__.py
src/ddh/agent_driver.py
src/ddh/candidate.py
src/ddh/completion.py
src/ddh/context.py
src/ddh/coordination.py
src/ddh/failure.py
src/ddh/integration.py
src/ddh/mutation.py
src/ddh/recovery.py
src/ddh/runtime.py
src/ddh/state.py
src/ddh/system_map.py
src/ddh/telemetry.py
src/ddh/test_auditor.py
src/ddh/verification.py
tests/unit/**
tests/contract/**
tests/integration/**
tests/fixtures/parallel_subsystem_workspace/**
docs/operations/ddh-phase-3-parallel-integration.md
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
docs/semantic-specifications/ddh-phase-3/**
.github/workflows/**
AGENTS.md
.git/**
legacy ADAD repository and snapshots
```

Implementation may read these sources but must not rewrite confirmed
specifications, decisions, earlier Phase evidence or CI policy to make Phase 3
pass.

## Runtime Scope

Phase 3 may add:

- typed parallel assessment, Module work groups, work lanes and write
  assignments;
- deterministic asynchronous scheduling through a worker-driver port;
- exact-generation activation, fence, revoke, quiescence and safe handoff;
- physical and logical resource overlap detection;
- shared-resource serialization and dependent-lane invalidation;
- current lane submission, serialized Patch Admission and fixed integration
  order;
- event-driven Join Barrier and immutable integrated Candidate creation;
- System Map query-consumption records at required coordination points;
- separate Work Package and Subsystem completion evaluation;
- reference adapters, deterministic scheduling controls and fault injection used
  only by tests.

Existing Phase 1/2 Contracts, Candidate isolation, Context, recovery, Test
Auditor, Verification Runner and Completion Judge may be extended only where
required to consume these Phase 3 contracts.

## Coding Profile

The confirmed Clean Code self-check profile remains applicable:

- intention-revealing names and role-oriented public vocabulary;
- single responsibility and one abstraction level;
- approximately 20 lines per function as a refactoring trigger, with justified
  readability exceptions;
- guard clauses and shallow nesting where they improve clarity;
- comments explain non-obvious reasons, not visible behavior;
- no unrelated cross-module refactoring.

These are Agent self-check expectations unless a corresponding mechanical test
exists.

## External and Destructive Boundary

Phase 3 prohibits:

- network calls initiated by DDH or connection to a real Agent service;
- credentials, databases, deployments, publication or release operations;
- package installation or unapproved backend creation;
- branch switch, commit, push, PR or mutation of the real user workspace;
- reset, stash, destructive cleanup or deletion of unrelated user changes;
- prompt-only claims of guarded shared mutation;
- modification of acceptance, thresholds, risk policy, architecture, schema,
  public contract or write scope;
- treating a System Map result as authorization;
- allowing a child worker to integrate, complete the Work Package or publish a
  higher-layer completion claim.

## Explicitly Deferred

- Full Verification Asset portfolio quality/currentness lifecycle (Phase 4).
- Production System Map backend/schema/query-engine design.
- Real remote Agent fleet, distributed queue or cross-host mutation service.
- Long-term learning, Attempt Ledger analysis and self-evolution.
- Candidate application to the user workspace.
- Domain acceptance, release candidate and external high-risk execution.

