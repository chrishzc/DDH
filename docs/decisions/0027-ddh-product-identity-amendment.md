# Decision 0027: DDH Product Identity Amendment

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: None

## Human Direction

The human renamed the successor framework:

> DDH = Demand-Driven Harness

## Decision

The product、future distribution、Python package and CLI use:

```text
Product: DDH
Expansion: Demand-Driven Harness
Python package: ddh
CLI: ddh
```

The existing repository directory name `ADHD` is historical filesystem state.
It does not change the product identity and does not require a destructive
repository rename before Phase 1.

This decision supersedes only the product-name and expansion fields in
Decision 0001. Decision 0001 remains authoritative for creating a clean
successor repository and keeping legacy ADAD read-only.

## Boundary

- Do not create compatibility aliases merely to preserve the abandoned ADHD
  product name.
- Historical filenames and quotations may remain when changing them would
  damage traceability.
- New runtime、package、CLI and user-facing specifications must prefer `DDH`
  and `ddh`.
- This identity decision does not authorize runtime implementation.

