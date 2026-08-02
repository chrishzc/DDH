# Decision 0029: Phase 0 Developer-tool Scenario Projection

- Status: Accepted
- Date: 2026-08-02
- Implementation authority: Specification assets only

## Human Direction

The human directed that Phase 0 itself receive a new version so the currently
effective package contains only DDH-native developer-tool examples.

## Decision

`DDH-P0-SPEC-001@1.1.0` is the currently effective Phase 0 package.

Its business scenarios use DDH-native developer-tool subjects:

- cross-platform workspace-path normalization;
- manifest loading and indexing;
- bounded System Map consumption and live-source fallback;
- Candidate integrity、parallel product／test work and integration;
- Verification Asset quality、runner recovery and layered completion.

These examples replace the earlier generic target-repository projection. They
do not change the accepted DDH contracts, risk boundaries, scenario coverage,
expected mechanical outcomes or prohibition on runtime implementation.

## Version and Archive Boundary

- `docs/semantic-specifications/ddh-phase-0/` is the current `1.1.0` package.
- `docs/semantic-specifications/archive/ddh-phase-0/1.0.0/` preserves the
  historical package structure but may be vocabulary-sanitized by an explicit
  human cleanup directive; it is not current behavioral authority.
- Decision 0028 is superseded as current projection authority but remains
  decision history.
- Contract Envelope protocol version `1.0.0` is unchanged; it is independent
  from the Phase 0 package version.

## Authorization Boundary

This decision authorizes only the specification-version correction、fixture
projection、indexes and deterministic validation necessary for Phase 0
`1.1.0`. It does not authorize Phase 1 runtime、CLI、hook、service、System Map
backend、deployment or any external mutation.
