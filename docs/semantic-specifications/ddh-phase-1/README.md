# DDH Phase 1 Task Specification Package

This directory contains the confirmation-ready Task Specification Package for
the first DDH runtime vertical slice.

It remains specification work only until the human confirms the exact
`DDH-P1-SPEC-001@1.0.0` closure digest. The manifest status
`ready_for_confirmation` and
`implementation_authority: none_until_exact_human_confirmation` mean that no
runtime、CLI、fixture repository or CI workflow may be implemented yet.

## Package Layout

```text
draft/
├─ manifest.json
├─ goal.md
├─ runtime-requirements.md
├─ implementation-boundary.md
├─ reference-workspace-fixture.md
├─ acceptance-scenarios.json
├─ bootstrap-profile.json
└─ validation/
   └─ validate_phase1_spec.py
```

`manifest.json` is the authority root. Referenced Markdown and JSON files form
one package closure; they are not independent SSOTs.

The final human action is one confirmation of an exact version and closure
digest. Work Package Projection、Context、Candidate generations and runner
recovery do not require repeated confirmation while authority fields remain
unchanged.
