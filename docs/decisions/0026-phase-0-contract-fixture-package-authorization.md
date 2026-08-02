# Decision 0026: Phase 0 Contract Fixture Package Authorization

- Status: Accepted and Authorized
- Date: 2026-08-02
- Implementation authority: Phase 0 specification assets only

## Human Authorization

Human directive:

> 採用 下一步依該版本開始 Phase 0

This directive confirms the Phase 0 scope proposed immediately before it and
authorizes `DDH-P0-SPEC-001` version `1.0.0`.

## Authorized Scope

Create the complete DDH MVP Executable Contract Fixture Package:

- Task Specification／Work Package／risk／authority fixtures;
- System Map Consumer Port and bounded fallback fixtures;
- Context、partition、mutation、handoff、join and candidate fixtures;
- Test Asset admission、verification、verdict and layered completion fixtures;
- recovery、no-progress、budget and Attempt Ledger learning fixtures;
- Phase 7A external-operation simulator fixtures;
- L1 serial and L2 parallel end-to-end golden cases;
- traceability and deterministic package validation assets.

The package may project already accepted decisions into scenarios, state
tables, JSON Envelope examples and expected outcomes. It may not change those
decisions without a new human-confirmed specification version.

## Explicit Exclusions

This authorization does not permit:

- DDH runtime or Python package implementation;
- CLI、hooks、scheduler、services or background workers;
- a System Map backend、schema redesign or Bundle generation;
- actual repository mutation enforcement or test execution engine;
- real provider Adapters、credentials、network or external writes;
- copying legacy ADAD runtime code;
- Phase 1 implementation.

## Terminal Boundary

Phase 0 completion produces specification and reusable contract fixtures. It
does not automatically authorize Phase 1. Any ambiguity that would change
architecture、behavior、scope、acceptance、risk or external authority must be
reported as a structured exception.

