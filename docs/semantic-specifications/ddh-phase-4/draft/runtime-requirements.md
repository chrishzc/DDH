# Phase 4 Runtime Requirements

## 1. Verification Asset and Catalog

Every formal asset has an immutable manifest with: asset identity and version;
asset kind/tool adapter; Module, Subsystem, Domain, or Global scope; requirement
and scenario mappings; quality profile identity; source, fixture, helper,
configuration, semantic-specification, contract, schema, and toolchain
dependencies; fixed execution entrypoint; environment profile; timeout; output
bound; oracle; expected result; and result-classification semantics.

The repository can rebuild its Catalog solely from admitted manifests and their
declared locations. The Catalog may index discovery, dependency candidates, and
layered suite selection, but cannot admit an asset, change its behavior, grant
execution authority, or replace a manifest/specification.

## 2. Non-bypassable roles

Test Auditor owns admission, quality review, currentness determination, and
disposition. Mechanical Verification Executor (MVE) only executes an immutable,
admitted, active manifest bound to the exact Candidate and environment profile.
It cannot decide test semantics, lower a threshold, omit required cases, select
an easier suite, or convert unavailable/error/timeout/incomplete to PASS.

Candidate -> Test Auditor -> admitted immutable manifest -> MVE is mandatory.
A candidate or draft asset cannot directly reach MVE. Candidate waiting for
admission is automatic waiting, not a human gate. Missing required semantics,
quality facts, oracle, or mapping returns structured `specification_not_ready`;
the runtime must not guess or relax acceptance.

## 3. Lifecycle and currentness

Admission states are `draft`, `candidate`, `admission_validating`, `admitted`,
and `active`; `rejected` is a terminal admission disposition. Validity and
execution facts remain separate: `rerun_required`, `suspect`, `stale`,
`quarantined`, and `retired` are explicit dispositions, not PASS states.
`active` requires admitted plus current validity plus no quarantine/retirement.

Changes to source, asset, fixture, helper, configuration, semantic
specification, contract, schema, quality profile, runner, or toolchain produce
the minimal affected re-evaluation candidate. Source-only change first creates
`rerun_required`; it does not automatically declare test semantics stale.
Suspect/stale/quarantined/retired assets cannot satisfy completion.

System Map is a maintained actual architecture index. Impact evaluation must
actually consume its query result when available. It is not SSOT or authority.
For stale, partial, unavailable, or omitted map areas, a bounded live-source
fallback examines only the affected closure; source and semantic specifications
remain behavior authority.

## 4. Quality, scope, and controlled cost

Selection supports Module, Subsystem, Domain, and Global suites. Strength comes
from semantic specification, risk, and independent quality add-ons, never file
size. Stress/load/soak is required only when the specification, quality profile,
or SLO makes it applicable; otherwise it must carry an explicit business N/A
reason. Fixed runners may use ordering, sharding, cache, parallelism, and
placement to control cost, but may not reduce required cases, oracle strength,
or thresholds. Routine re-evaluation consumes zero agent tokens.

Runner output is bounded and deduplicates repeated tracebacks. Flake signals
produce suspect/quarantine/re-evaluation evidence rather than a false PASS.
Long-term evidence is the admitted rerunnable asset plus required dependencies
and environment declaration—not permanent raw logs, PASS receipts, or Attempt
Ledgers.

