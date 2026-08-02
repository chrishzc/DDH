# ADHD Agent Rules

## Current phase

ADHD is in architecture and specification design. Do not create runtime code,
CLI commands, hooks, schemas, generated Bundles, or migration tools unless the
human explicitly authorizes implementation.

## SSOT

- Structural architecture authority lives under `docs/architecture/`.
- Behavioral and acceptance authority lives under
  `docs/semantic-specifications/`.
- Decision history lives under `docs/decisions/`.
- Do not silently turn a proposal into an approved decision.

## Development model

- Work from a human-selected architecture scope.
- Within an authorized scope, implementation defects and mechanical failures
  should be diagnosed and corrected autonomously.
- Stop for human input only when architecture, semantic behavior, risk policy,
  or an irreversible external action must change.
- Verification strength follows semantic specifications and risk, not file
  size or implementation complexity alone.

## Removed legacy mechanisms

Do not introduce Frozen Tasks, Source Locks, Checkpoints, contract freshness,
stable cross-version entity identity, provenance receipts, recovery control
planes, or legacy System Map fallback.

## Safety

- Preserve unrelated user changes.
- Do not commit, push, delete, deploy, release, or mutate external systems
  without explicit authority.
- Legacy ADAD assets are read-only references; copy only a deliberately
  selected capability after its semantics and tests are accepted for ADHD.
