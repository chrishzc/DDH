# Decision 0030: Release-preflight Windows 11 Compatibility Gate

- Status: Accepted
- Date: 2026-08-11
- Implementation authority: CI profile and project documentation only

## Human Direction

The human directs that the trusted self-hosted Windows 11 / Python 3.13
profile is a release-preflight compatibility gate, rather than a required
daily-commit gate.

## Decision

Daily DDH verification uses the hosted matrix:

- Ubuntu 24.04 / Python 3.13;
- latest stable Ubuntu; and
- latest stable Windows.

The self-hosted Windows 11 / Python 3.13 profile is invoked manually before a
release candidate. It provides evidence for the actual Windows desktop
environment, including Windows-specific process, path, filesystem, and
service behavior.

## Boundary

This decision changes CI scheduling and project-level compatibility evidence
only. It does not weaken any Phase 2 or Phase 3 semantic scenario, alter a
confirmed Phase package, or authorize release, deployment, or external
operation.

## Acceptance

- Daily hosted CI remains required and blocking.
- Windows 11 validation is explicitly labelled release preflight.
- A release candidate requires a successful Windows 11 / Python 3.13 run.
