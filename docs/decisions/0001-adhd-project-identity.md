# Decision 0001: Establish ADHD as a clean successor

- Status: Accepted
- Date: 2026-08-02

> Amendment: Decision 0002 supersedes this document's statement that System Map
> participates in a dual SSOT. System Map is a maintained actual architecture
> index, not an SSOT. The task specification is the Agent goal and completion
> SSOT for each task.

## Decision

Create a new independent project named:

**ADHD — Architecture-Driven Harnessed Development**

The project lives at:

`C:\Users\chris\Desktop\project\ADHD`

Legacy `ADAD` remains a separate, preserved reference. ADHD is not an
in-place rename, worktree, compatibility branch, or subdirectory of ADAD.

## Meaning of Harnessed

AI development is constrained by:

- a human-selected architecture scope;
- a human-confirmed task specification that fixes the Agent goal, scope,
  constraints, required behavior, and completion criteria;
- long-term architecture and semantic specifications referenced by that task;
- risk-classified execution policy;
- high-standard layered verification.

Within those boundaries, the Orchestrator autonomously implements and repairs
ordinary failures. Human intervention is reserved for architecture, semantic
specification, risk-policy, and irreversible-action decisions.

## Naming boundary

- Product and future CLI/package name: `ADHD` / `adhd`.
- Generic architecture format name remains `system-map-bundle`.
- Legacy ADAD-specific extension and Control Plane names are not carried over.

## Removed mechanisms

- Frozen Task.
- JIT Source Ownership and Source Lock.
- Stable cross-version identity and freshness.
- Heavy evidence, receipt, sealing, and recovery infrastructure.

## Consequence

No legacy source tree is copied wholesale. Capabilities may be brought over
only one at a time after their semantics, architecture fit, and tests are
accepted for ADHD.
