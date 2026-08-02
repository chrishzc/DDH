# Phase 1 Implementation Boundary

## Allowed Repository Writes After Exact Confirmation

The future Phase 1 implementation may write only:

```text
pyproject.toml
src/ddh/**
tests/unit/**
tests/contract/**
tests/integration/**
tests/fixtures/portable_workspace/**
.github/workflows/ddh-ci.yml
docs/operations/ddh-phase-1-cli.md
README.md
```

This list is implementation authority only after the exact package is
human-confirmed. The current draft grants no writes.

## Protected and Read-only Inputs

```text
docs/architecture/**
docs/decisions/**
docs/proposals/**
docs/semantic-specifications/ddh-phase-0/**
docs/semantic-specifications/ddh-phase-1/**
AGENTS.md
.git/**
legacy ADAD repository and snapshots
```

Implementation may read these sources according to Context budget. It may not
rewrite accepted decisions、Phase 0 fixtures or the confirmed Task
Specification to make tests pass.

## Runtime Package Boundary

The modular Python distribution must separate:

- language-neutral contracts and schemas;
- Task Specification／risk projection;
- role logic;
- Ports;
- concrete local Adapters;
- runtime composition;
- thin CLI entrypoints.

Roles depend on Contracts／Ports, not concrete Agent、Git、System Map、test tool
or external SDK implementations. Exact module filenames may follow Clean Code
and cohesion without changing these dependency boundaries.

## Coding Profile

The confirmed self-check profile applies:

- intention-revealing names;
- single responsibility and one abstraction level;
- approximately 20 lines per function as a refactoring trigger, with justified
  readability exceptions;
- guard clauses and shallow nesting where they improve clarity;
- comments explain non-obvious reasons, not visible code behavior;
- clean touched code without unrelated cross-module refactoring.

These are Agent self-check expectations. Only mechanically implemented checks
may be described as mechanical enforcement.

## External and Destructive Boundary

Phase 1 prohibits:

- network calls initiated by DDH;
- credentials or secret stores;
- package installation as an automatic recovery;
- database、deployment、publication or release operations;
- branch switch、commit、push、PR or modification of the real user worktree;
- arbitrary shell／HTTP execution;
- System Map backend、Bundle generation or schema redesign;
- deletion of user files or unrelated dirty changes.

CI workflow files may be authored and locally validated. Pushing them or
running remote CI is not authorized by this Task Specification.

## Explicitly Deferred

- Multi-Agent parallel runtime and Join Barrier.
- Full Test Asset portfolio lifecycle.
- Long-term learning and self-evolution.
- Git worktree／virtual overlay Candidate materializers.
- SQLite／daemon／production MCP Server.
- Candidate apply Adapter.
- Subsystem／Domain／release completion.
- External high-risk operations.

