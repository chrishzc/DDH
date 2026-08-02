# Phase 0 Package Validation Contract

Validation is deterministic and requires no Agent judgment.

## Structural Checks

1. Every `.json` file parses as one UTF-8 JSON document.
2. Fixture family files conform to `fixture-family.schema.json`.
3. Contract Envelope examples conform or fail according to
   `contract-envelope-expected-results.json`.
4. Scenario IDs are globally unique.
5. Fixture family and package manifest contract references resolve to files
   inside the repository.
6. Every manifest asset resolves under `docs/semantic-specifications/ddh-phase-0/`.
7. No machine-readable asset contains an absolute Windows／POSIX path.

## Semantic Projection Checks

1. Every fixture scenario has an authority source and immutable fields.
2. Every contract family includes success and rejection.
3. Applicable families include stale／invalidation、recovery and race cases.
4. L1 and L2 golden flows reference existing scenario IDs.
5. Phase 7A cases never produce a real external write.
6. System Map cases use it as an actual index and never as task authority.
7. No fixture activates Frozen Task、Source Lock、Checkpoint、receipt、
   provenance chain or legacy System Map fallback.

## Scale Design Check

The package must define a deterministic validator capable of processing 10,000
synthetic reference records without creating a permanent generated corpus.
The test input is produced in-memory from existing IDs, and validation checks
bounded iteration、duplicate detection and missing-reference reporting.

## Result Shape

```text
terminal_state
acceptance_outcome
verification_completeness
reason_codes[]
checked_assets
checked_scenarios
errors[]
```

A validator process exit code alone is not the result contract. Any truncated
error list must include total error count and truncation status.

