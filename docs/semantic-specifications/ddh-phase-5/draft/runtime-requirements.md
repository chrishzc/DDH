# Phase 5 Runtime Requirements

## Environment and isolation

Each Verification Subject binds an immutable Environment Profile containing
platform/runtime/tool versions, dependency identity, cwd, locale, timezone,
encoding, environment allowlist, fixture/service requirements, network and
database capability, isolation profile, resource budget, and output limits.
Isolation is `light`, `standard`, `high_assurance`, or a separately authorized
`external` lane. A temporary workspace is not network, credential, or database
isolation.

## Adaptive bounded timeout

Business performance threshold, execution deadline, no-progress deadline, and
termination/output-drain grace are separate fields. The fixed Execution Plan
uses the maximum of declared duration, same-suite/platform p95, collected-work
estimate, and profile floor; it then applies the approved safety factor and
startup margin without changing product thresholds.

Bootstrap uses safety factor 2.0, startup margin 30 seconds, a 600-second hard
deadline when no reliable estimate exists, and at most 30 seconds termination
grace. No-progress is enabled only with a trustworthy mechanical progress
signal and is `max(2 × expected progress interval, 120 seconds)`. Silence alone
does not mean a hang. A plan exceeding the Work Package ceiling returns
`verification_plan_not_ready` before process start. Timeout is infrastructure
or incomplete execution, not product failure.

## Output, process, and temporary roots

Byte, line, and event limits apply while draining subprocess output. Repeated
tracebacks are aggregated by root fingerprint. Timeout/crash cleanup proves the
Windows process tree or Unix process group is stopped. Temporary cleanup occurs
only for a tool-created root whose ownership identity still matches. Uncertain
symlink, junction, reparse, permission, or identity state is preserved and
quarantined rather than recursively removed.

## Capability, managed assets, Map, and telemetry

Capability Health is `available`, `degraded`, `unavailable`, or `unknown` and
may choose only an approved semantically equivalent fallback. It cannot change
specification, scope, acceptance, or external authority.

Managed asset changes require manifest identity, dry-run, isolated output,
delta preview, compatibility verification, atomic apply, and post-apply parity.
They cannot remove-then-copy a target tree or overwrite user-customized assets.
Second application of the same current manifest is idempotent.

System Map consumption binds repository, branch, resolved commit, worktree,
Candidate, and Map view. Same branch with a different commit invalidates prior
Context, impact, and preview. Query-only operations never switch the user's Git
working tree. Operational telemetry is bounded, non-authoritative, and not a
permanent raw log or completion input.

