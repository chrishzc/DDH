# Phase 0 Contract Traceability Matrix

Each JSON fixture scenario contains its own `contract_refs`,
`authority_source`, `expected`, and `immutable_fields`. This table is the
human-readable index; `contract-registry.json` and the fixture files form the
machine-readable traceability.

| Contract family | Scenario prefixes | Count | Fixture | State table | Golden flow use |
|---|---|---:|---|---|---|
| Task authority／scope／risk／System Map consumption | `P0-AUTH`、`P0-SM`、`P0-RISK` | 32 | `fixtures/authority-scope-and-risk.json` | `state-tables/authority-work-package-and-risk.md` | L1, L2 |
| Context／coordination／candidate | `P0-CTX`、`P0-COORD`、`P0-CAND` | 38 | `fixtures/context-coordination-and-candidate.json` | `state-tables/partition-candidate-and-handoff.md` | L1, L2 |
| Test Asset／verification／completion | `P0-TEST`、`P0-VERIFY`、`P0-COMP` | 27 | `fixtures/test-verification-and-completion.json` | `state-tables/test-subject-verdict-and-completion.md` | L1, L2 |
| Recovery／learning／external simulation | `P0-REC`、`P0-LEARN`、`P0-EXT` | 32 | `fixtures/recovery-learning-and-external.json` | `state-tables/recovery-learning-and-external.md` | L1, L2, Phase 7A |
| Wire／identity／platform | `P0-WIRE`、`P0-ID`、`P0-PLAT` | 23 | `fixtures/wire-identity-and-platform.json` | `state-tables/wire-transport-and-identity.md` | all transports |
| **Total** | 15 prefixes | **152** | 5 families | 5 tables | 3 flows |

## Required Coverage Projection

| Required class | Representative scenario IDs |
|---|---|
| Normal success | `P0-AUTH-001`, `P0-COORD-001`, `P0-VERIFY-S001`, `P0-COMP-S009` |
| Rejection／boundary | `P0-AUTH-002`, `P0-CAND-004`, `P0-TEST-S004`, `P0-EXT-004` |
| Stale／wrong subject | `P0-AUTH-005`, `P0-CTX-005`, `P0-CAND-006`, `P0-VERIFY-S002` |
| Automatic recovery | `P0-SM-005`, `P0-COORD-005`, `P0-REC-001`, `P0-VERIFY-S003` |
| Race／ordering／duplicate | `P0-AUTH-009`, `P0-CAND-014`, `P0-WIRE-005`, `P0-COMP-S007` |
| Budget／bounded resources | `P0-AUTH-010`, `P0-CTX-004`, `P0-REC-004`, `P0-VERIFY-S010` |
| System Map non-authority | `P0-SM-001`, `P0-SM-004`, `P0-SM-010`, `P0-REC-003B` |
| Test anti-weakening | `P0-TEST-S002`, `P0-TEST-S003`, `P0-TEST-S004`, `P0-TEST-S006` |
| Layer separation | `P0-COMP-S001`, `P0-COMP-S005`, `P0-COMP-S006`, `P0-COMP-S009` |
| Learning bounded retention | `P0-LEARN-001` through `P0-LEARN-013` |
| External simulator／uncertain result | `P0-EXT-001` through `P0-EXT-013` |
| Cross-platform protocol／identity | `P0-WIRE-001` through `P0-WIRE-010`, `P0-ID-001` through `P0-ID-010`, `P0-PLAT-001` through `P0-PLAT-003` |

## Authority Notes

- Fixture expected values do not override their accepted contract references.
- A fixture conflict with an accepted decision is an exception, not a new rule.
- Scenario IDs are package-local and are not stable cross-version entities.
- Historical `OW-*` aliases remain traceability pointers only.
