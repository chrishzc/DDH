# DDH Phase 2 Task Specification Package

This directory contains the confirmation-ready Task Specification Package for
DDH automatic recovery and exception routing.

It remains specification work only until the human confirms the exact
`DDH-P2-SPEC-001@1.0.0` closure digest. The manifest status
`ready_for_confirmation` and
`implementation_authority: none_until_exact_human_confirmation` mean that no
Phase 2 runtime or operational asset may be implemented yet.

## Package Layout

```text
draft/
├─ manifest.json
├─ goal.md
├─ runtime-requirements.md
├─ implementation-boundary.md
├─ reference-recovery-fixture.md
├─ acceptance-scenarios.json
├─ bootstrap-profile.json
└─ validation/
   └─ validate_phase2_spec.py
```

`manifest.json` is the authority root. Referenced Markdown and JSON files form
one package closure; they are not independent SSOTs.

One exact human confirmation authorizes the bounded Phase 2 implementation
scope. Individual recovery attempts, Candidate generations and verification
reruns do not require repeated confirmation while authority fields remain
unchanged.
