# Phase 1 Agent Goal

Build the minimum usable single-main-Agent DDH runtime vertical slice from the
exact confirmed version of `DDH-P1-SPEC-001`.

The runtime must accept a human-confirmed workload Task Specification, consume
a current actual-only System Map index or bounded live-source fallback, prepare
bounded Agent Context, admit only authorized changes into an isolated immutable
Candidate, independently audit Verification Asset changes, execute repeatable
no-Agent CI/CD verification and mechanically publish
`work_package_completed` only when the current closure passes.

The Phase 1 reference workload is a disposable cross-platform workspace-path
fixture. It is not a DDH product feature.

## Authority

- This Agent Goal and its source reference in `manifest.json` are the Phase 1
  implementation goal source.
- The workload Task Specification is the runtime execution SSOT for the
  disposable target repository.
- System Map、source code、tests、discovery metadata、prompts and Agent claims
  cannot add authority or change acceptance.
- Agent results are candidate inputs. Change admission、Verification Asset
  validity、verification verdict and completion are separate mechanical
  decisions.

## Terminal Boundary

Phase 1 succeeds only at Work Package completion for the accepted portable
Candidate Bundle. It does not publish `subsystem_integrated`、
`domain_accepted`、`release_candidate`、deployment or external authority.

