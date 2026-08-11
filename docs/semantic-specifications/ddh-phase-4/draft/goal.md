# Phase 4 Agent Goal

Define the confirmed, tool-neutral model for reusable Verification Assets that
protects specified behavior from accidental or strategic test weakening. A
Verification Asset may be a pytest suite, generic fixed command, compiler,
linter, type checker, schema check, security scan, integration check, or
performance check. Its formal meaning does not depend on pytest.

The package must permit a repository-derived Verification Asset Catalog for
discovery and suite selection while preserving confirmed semantic
specifications, fixed asset manifests, and live source as the only behavioral
evidence. The Catalog is never an authorization, admission, or behavior SSOT.

## Terminal boundary

This Phase 4 package succeeds only as a specification package. It must not
claim `work_package_completed`, `subsystem_integrated`, `domain_accepted`, or
`release_candidate`. Those are future, separate decisions made from a frozen
candidate and current admitted assets.

Phase 3 is an uncommitted local baseline. `phase3-source-snapshot.json` binds
the specifically observed Phase 3 files by path and SHA-256 without creating,
requiring, or pretending to have a Git commit. A changed snapshot requires a
new Phase 4 package version or explicit baseline reconciliation; it never
silently changes this package's confirmation closure.

