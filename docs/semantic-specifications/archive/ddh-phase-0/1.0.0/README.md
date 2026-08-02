# DDH Phase 0 Executable Contract Fixtures

This directory is the authorized output of `DDH-P0-SPEC-001` version `1.0.0`.

It contains specification assets and reusable contract fixtures, not DDH
runtime implementation.

Phase 0 completed on 2026-08-02. The deterministic result and independent
review are recorded in `completion-report.md`.

## Layout

```text
task-specification-v1.md
shared/
contract-families/
golden-flows/
fixtures/
state-tables/
traceability/
validation/
```

All machine-readable files use UTF-8 JSON with LF line endings. Scenario
semantics remain readable in Markdown; JSON fixtures carry stable package-local
IDs and expected mechanical outcomes.

## Authority Boundary

- The Task Specification is the Phase 0 task SSOT.
- Accepted decisions and referenced semantic contracts define expected
  behavior.
- Fixtures are executable projections, not a second authority source.
- System Map facts help locate architecture but cannot grant authority.
- Phase 0 completion does not authorize Phase 1.

## Validation

From repository root:

```powershell
py -3 docs/semantic-specifications/ddh-phase-0/validation/validate_phase0.py
```

The validator uses only the Python standard library and performs no external
write.
