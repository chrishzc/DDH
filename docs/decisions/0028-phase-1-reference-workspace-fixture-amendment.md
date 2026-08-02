# Decision 0028: Phase 1 Reference Workspace Fixture Amendment

- Status: Superseded by Decision 0029
- Date: 2026-08-02
- Implementation authority: None

## Human Direction

The human identified that order／billing behavior is not a DDH product
capability and accepted replacing that example with a developer-tool-native
workspace fixture.

## Decision

Accounting、order、fee and currency-rounding scenarios in earlier architecture
documents are `example-only`. They illustrate that DDH can modify an arbitrary
target repository; they are not DDH business features and must not determine
the Phase 1 reference workload.

Phase 1 uses an isolated cross-platform workspace-path fixture:

- `PathNormalizer` converts accepted Windows／POSIX relative inputs into one
  repository-relative canonical path.
- absolute、UNC and workspace-escape inputs produce typed rejection.
- `ManifestLoader` is a read-only downstream consumer used to prove dependency
  impact and verification-scope expansion.
- the Agent may modify only the authorized product Module and propose bounded
  Verification Asset changes.

## Phase 0 Compatibility

`DDH-P0-SPEC-001@1.0.0` was initially retained as a historical package.
Decision 0029 superseded this projection, and a later explicit human cleanup
directive sanitized residual example vocabulary across the repository.

No Phase 0 PASS authorizes implementation of the accounting example or Phase 1
runtime.

## Boundary

- The fixture is disposable test data, not a DDH runtime feature.
- It must not add order、billing or monetary concepts to the DDH package.
- It must exercise System Map consumption、bounded live fallback、dirty-diff
  preservation、actual-impact reconciliation and cross-platform verification.
- This decision does not authorize runtime implementation.
