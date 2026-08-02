# Phase 2 Agent Goal

Extend the confirmed Phase 1 reference runtime with deterministic automatic
recovery and exception routing from the exact confirmed version of
`DDH-P2-SPEC-001`.

The runtime must classify failures from the single-main-Agent execution lane,
build a bounded Failure Bundle, select only pre-approved recovery routes,
continue automatically when authority and budgets remain valid, and publish a
structured exception when a human-owned boundary or exhausted safe route is
reached.

Routine product repair, test implementation repair, runner recovery, bounded
Context expansion, System Map fallback, stale-generation rejection and
verification-closure expansion must not become step-by-step human debugging.

## Authority

- This Agent Goal and its source reference in `manifest.json` are the Phase 2
  implementation goal source.
- The workload Task Specification remains the runtime execution SSOT.
- Recovery policy, budgets and routes are projections of confirmed inputs; the
  Main Agent cannot invent a route, increase a budget or change acceptance.
- System Map, telemetry, discovery metadata, tool output, prompts and Agent
  claims provide facts only and cannot grant authority.
- A structured exception is a request for a decision, not an approval.

## Terminal Boundary

Phase 2 succeeds when all required failure classes have deterministic,
replayable routes in one serial main-Agent lane and the Completion Judge cannot
accept stale, incomplete or exception-open evidence.

It publishes only Work Package completion. It does not publish
`subsystem_integrated`, `domain_accepted`, `release_candidate`, deployment or
external-operation authority.
