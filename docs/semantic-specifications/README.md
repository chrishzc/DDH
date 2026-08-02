# Semantic Specifications

This directory is the behavioral SSOT for DDH (repository historical name:
ADHD).

Each specification should eventually define:

1. Purpose and real-world scenario.
2. In-scope and out-of-scope behavior.
3. Inputs, outputs, state changes, and failure semantics.
4. Invariants and security boundaries.
5. Acceptance scenarios.
6. Required verification layers.
7. Completion criteria.

The general format remains adaptable. The current Phase 0 package
`DDH-P0-SPEC-001@1.1.0` under `ddh-phase-0/` uses Markdown scenarios plus UTF-8 JSON Contract Envelope
fixtures according to Decisions 0016、0026 and 0029; this does not force unrelated
project specifications into the same physical format. Phase 0 completion does
not authorize Phase 1.

Historical Phase 0 versions live under `archive/ddh-phase-0/` and are not
current behavioral authority.

System Map entities may reference these files and sections, but must not copy
their full content into Bundle records.
