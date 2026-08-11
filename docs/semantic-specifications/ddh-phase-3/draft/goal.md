# Phase 3 Agent Goal

Extend the confirmed Phase 2 reference runtime with deterministic parallel work
coordination and central Subsystem integration from the exact confirmed version
of `DDH-P3-SPEC-001`.

The runtime must decide whether parallel work has enough benefit, build bounded
Module work groups and product/test lanes, activate writes only after the Change
Guard establishes the matching mechanical boundary, coordinate shared
resources, preserve useful partial results, and assemble one immutable
Subsystem Candidate through serialized central admission.

Three independent Modules may implement product code and independently authored
acceptance assets asynchronously. Early lanes must wait without Agent cost.
Only current, quiescent, admitted lanes may cross the Join Barrier, after which
the integrated Candidate reruns required Module verification and executes the
Subsystem business scenarios and affected regression closure.

## Authority

- This Agent Goal and its source reference in `manifest.json` are the Phase 3
  implementation goal source.
- The workload Task Specification remains the runtime execution SSOT.
- The Work Coordinator projects partitions, Context and execution choices; it
  cannot change goal, scope, behavior, acceptance, budget ceiling or risk.
- The System Map is a maintained actual-architecture index. Its query results
  must be consumed for scope and impact decisions, but never grant authority.
- Prompt instructions, Agent claims, discovery metadata and local PASS results
  are not mechanical write, quiescence, integration or completion evidence.

## Terminal Boundary

Phase 3 succeeds when both required modes are executable and replayable:

1. product implementation and independent acceptance construction proceed in
   separate write lanes and are centrally integrated; and
2. three Module work groups complete out of order, join deterministically, and
   pass current integrated Subsystem verification.

The reference Work Package may publish `work_package_completed` and its exact
Subsystem-level fixture may separately publish `subsystem_integrated`.
`domain_accepted`, `release_candidate`, deployment and external-operation
authority remain `not_evaluated`.

