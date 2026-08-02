# ADHD Product Architecture v0

> Status: confirmed product direction; module boundaries remain discussion-stage.

## Product boundary

ADHD accepts a human-selected architecture scope and autonomously develops
within that scope until high-standard verification demonstrates conformance
with linked semantic specifications.

## Proposed top-level domains

```text
Architecture
  → Scope selection and structural queries

Semantic Specifications
  → Behavior, invariants, acceptance, and completion standards

Risk
  → Change-risk classification and required verification strength

Orchestrator
  → Plan, implement, verify, diagnose, and auto-correct within scope

Verification
  → Structural, behavioral, integration, semantic, and risk-specific layers

Adapters
  → Human, Agent, MCP, CLI, repository, and optional release integrations
```

## Dependency direction

```text
Adapters
  → Orchestrator
      → Architecture
      → Semantic Specifications
      → Risk
      → Verification
```

Architecture, Semantic Specifications, Risk, and Verification must not depend
on a concrete Agent platform. Adapters depend inward; domain policy does not
depend outward.

## Confirmed removals

- Frozen Task and Task state machine.
- JIT Source Ownership and Source Lock.
- Stable cross-version identity and freshness chains.
- Checkpoint, provenance receipt, evidence sealing, and recovery control plane.

## Open architecture discussions

- Architecture-scope transaction and central patch application boundary.
- Exact risk classes and escalation rules.
- Layered verification contracts and semantic verifier independence.
- Child-agent context and delegation protocol.
- Dogfood, Adoption, and Release boundaries.
