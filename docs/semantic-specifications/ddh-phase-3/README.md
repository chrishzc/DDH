# DDH Phase 3 Task Specification Package

This directory contains the confirmation-ready Task Specification Package for
DDH parallel work coordination and central Subsystem integration.

It remains specification work only until the human confirms the exact
`DDH-P3-SPEC-001@1.0.0` closure digest. The manifest status
`ready_for_confirmation` and
`implementation_authority: none_until_exact_human_confirmation` mean that no
Phase 3 runtime or operational asset may be implemented yet.

## Package Layout

```text
draft/
├─ manifest.json
├─ goal.md
├─ runtime-requirements.md
├─ coordination-contract.md
├─ implementation-boundary.md
├─ reference-parallel-subsystem-fixture.md
├─ acceptance-scenarios.json
├─ bootstrap-profile.json
└─ validation/
   └─ validate_phase3_spec.py
```

`manifest.json` is the authority root. Referenced Markdown and JSON files form
one package closure; they are not independent SSOTs.

One exact human confirmation authorizes the bounded Phase 3 implementation
scope. Lane scheduling, Context increments, safe handoff, Candidate
generations, parallel-to-serial fallback, integration repair and verification
reruns do not require repeated confirmation while authority fields remain
unchanged.
