# Phase 1 Capability Derivation from Phase 0 Fixtures

This document identifies capabilities required by the fixtures. It does not
authorize or prescribe Phase 1 implementation.

| Required capability | Input fixture families | Minimum observable behavior |
|---|---|---|
| Task Specification intake and readiness | AUTH, RISK | reject missing behavior; bind exact confirmed version |
| Work Package projection compiler | AUTH, SM, RISK | derive scope／profile／budget without becoming authority |
| System Map Consumer Port | SM, REC | exact view binding, material consumption, bounded live fallback |
| Context Curator | CTX | bounded pinned context, incremental grants, budget disposition |
| Work Coordinator | COORD | parallel benefit decision, partition activation, handoff and join |
| Change Guard | CAND, ID | three mediation modes, patch admission, stale writer rejection, freeze |
| Test Auditor | TEST | inventory, scenario mapping, currentness, independent anti-weakening admission |
| Verification Runner | VERIFY, WIRE, PLAT | immutable Subject, adaptive timeout, bounded output, typed result |
| Completion Judge | COMP | separate Work Package／Subsystem／Domain／release evaluation |
| Recovery Router | REC, SM, VERIFY | fixed safe next action, no-progress and impact-underestimation routing |
| Learning Steward intake | LEARN | terminal seal, zero-Agent prefilter, atomic fold and bounded expiry |
| External Plan simulator | EXT | plan drift, uncertain reconciliation and no generic escape |
| Contract transport adapter | WIRE, ID | atomic file result, strict JSON, typed minimal identity |
| Platform adapter | PLAT | required Windows／Ubuntu semantics and honest preview classification |

## Phase 1 Minimum Vertical Slice

A future Phase 1 Task Specification must select a bounded subset that can
replay `P0-FLOW-L1-001` end to end:

```text
confirmed Task Specification
→ scope／risk projection
→ bounded Context
→ Serial Reconciled mutation
→ candidate freeze
→ Test Asset admission
→ no-Agent Verification Runner
→ Work Package completion
→ non-blocking routine learning handoff
```

It must also preserve interfaces needed by the later L2 flow. Implementing only
an Agent wrapper around pytest would not satisfy the derived capability set.

## Deferred from Phase 1

- Full parallel product／test fork-join implementation.
- Full Learning Steward Analyzer／Critic／Memory Registry.
- Real external provider Adapters.
- Native Rust／Go backends.
- System Map backend or schema implementation.

Deferral cannot replace required rejection behavior with prompt advice.

