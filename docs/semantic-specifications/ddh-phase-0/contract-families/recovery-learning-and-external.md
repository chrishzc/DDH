# Recovery, Learning Intake, and External Boundary Scenarios

## Contract References

- `docs/decisions/0006-phase-2-automatic-recovery-and-exception-routing.md`
- `docs/decisions/0010-phase-6-learning-steward-and-controlled-evolution.md`
- `docs/decisions/0011-phase-7-external-high-risk-operations.md`
- `docs/decisions/0023-bounded-learning-intake-and-retention-profile.md`
- `docs/decisions/0024-staged-external-high-risk-adapter-productization.md`
- `docs/proposals/evolution_profile_pending_ledger_policy.md`
- `docs/proposals/managed_assets_and_external_high_risk_operations_contract.md`

## Recovery Scenarios

### P0-REC-001 — Tool backend unavailable

**Given:** The candidate and acceptance remain current, but the selected local
runner backend cannot initialize.

**When:** Capability health reports the backend unavailable before product
tests start.

**Expected:** Select another already approved safe backend or isolated mode,
rebuild only the execution projection and retry the same subject. Do not ask
the Agent to change product code or ask the human how to repair the tool.

### P0-REC-002 — Same failure without new evidence

**Given:** Two attempts have the same normalized failure fingerprint,
hypothesis, candidate and environment.

**When:** Recovery routing evaluates another retry.

**Expected:** Reject the retry as no-progress, preserve the current candidate
and route to a different fixed diagnosis／recovery path or bounded terminal
report. Acceptance cannot be weakened.

### P0-REC-003 — Scope underestimation

**Given:** Actual diff or verification failure identifies a reverse dependent
outside the initial impact closure.

**When:** The System Map Consumer Port returns the dependent, or bounded live
discovery finds it because the Map result is incomplete.

**Expected:** Expand read／verification closure automatically. If repair needs
outside-scope writes, stop only that lane and request a versioned scope
revision.

### P0-REC-004 — Budget exhausted

**Given:** The current route has consumed its recovery budget.

**When:** A new attempt would exceed the fixed ceiling.

**Expected:** Do not reduce required tests. Emit attempted routes、evidence、
gap and bounded options; preserve useful candidate work.

## Learning Intake Scenarios

### P0-LEARN-001 — Routine success

**Expected:** Zero-Agent prefilter returns
`routine_no_orchestration_signal`; no model call and immediate Ledger
deletion.

### P0-LEARN-002 — Repeated Context inflation

**Given:** The same pattern appears three times across at least two Work
Packages.

**Expected:** Atomically fold normalized facts into one P2 Learning Candidate,
delete source Ledgers within 24 hours and schedule the daily／idle batch.

### P0-LEARN-003 — Unsafe recovery signal

**Expected:** Create one P0 Candidate after the current mutation transaction is
safe. Product completion does not wait for Analyzer or Critic.

### P0-LEARN-004 — Analyzer outage and expiry

**Expected:** Circuit-break repeated model retries, continue zero-Agent
prefilter／aggregation, then expire P0／P1／P2／P3 material at their fixed upper
bounds without creating permanent failure receipts.

### P0-LEARN-005 — Known pattern without change

The zero-Agent prefilter updates only the bounded support observation for a
current Memory and deletes the source Ledger. No Analyzer call or Memory
version change occurs.

### P0-LEARN-006 — 64 KiB Ledger cap

Repeated attempts、tracebacks、metrics and tool events exceed 64 KiB.
Deterministic aggregation preserves classification、count、first／last
occurrence、new evidence、cost and truncation facts without model use.

### P0-LEARN-007 — P1 trigger

A comparable P1 pattern is scheduled when it occurs twice or waits one hour,
whichever comes first. It never borrows the active Work Package budget.

### P0-LEARN-008 — P3 trigger

A low-confidence P3 candidate gets no dedicated model call before five
occurrences. It may only ride an already scheduled batch.

### P0-LEARN-009 — Independent TTL tiers

Unfolded Individual Ledgers expire at P3 24h、P2 72h、P1 7d、P0 14d.
Learning Candidates expire at P3 7d、P2 14d、P1 30d、P0 90d.

### P0-LEARN-010 — Crash-safe atomic fold

A crash after candidate fold but before source deletion is recovered
idempotently. Support counts and model scheduling are not duplicated.

### P0-LEARN-011 — Evolution budget isolation

Analyzer backlog cannot consume Agent、Context、Verification or Recovery
budget reserved by an active Work Package.

### P0-LEARN-012 — Aggregate evidence preservation

Atomic fold retains applicability、support／counterevidence counts、cost
summary and necessary bounded examples, but not a compressed raw Ledger copy.

### P0-LEARN-013 — Self-contained Memory

A promoted Memory remains interpretable and invalidatable after all source
Ledgers and the Candidate are deleted; it stores normalized evidence summary,
confidence、version、applicability、conflict and expiry rules.

## External Phase 7A Scenarios

### P0-EXT-001 — Plan ready but no Adapter

**Given:** A release candidate has a valid deployment plan but no real provider
Adapter or external approval.

**Expected:** Simulator can validate the plan; real execution returns
`adapter_unavailable` or `approval_required`. No external write occurs.

### P0-EXT-002 — Approval drift

**Given:** Human approval is bound to exact plan digest、candidate、target and
ordered operations.

**When:** Configuration or target changes.

**Expected:** Invalidate approval and return `approval_required`; never
silently update the plan.

### P0-EXT-003 — Timeout after request delivery

**Given:** The simulator models a provider receiving the request but the
response is lost.

**Expected:** Stop retry, inspect simulated current target state and classify
`succeeded`、`not_executed` or `uncertain`. Unknown remains a human decision.

### P0-EXT-004 — Generic escape rejected

**When:** An Agent submits an arbitrary shell command or URL as an operation.

**Expected:** Reject it because no typed operation class、capability-scoped
Adapter or exact approved plan exists.

### P0-EXT-005 — Rollback failure

**Expected:** Preserve current observed external facts in the bounded operation
result, stop automated mutation and require a new high-risk decision. Do not
claim that the pre-operation state was restored.

### P0-EXT-006 — Exact plan and credential-reference binding

Plan admission fixes Candidate、commit、artifact、configuration、target、
operation order and credential reference. Raw credential material is rejected
from the Plan、Agent Context、Ledger and result.

### P0-EXT-007 — Simulated success

The simulator executes no real write but returns a structured succeeded result
only after the modeled target postcondition matches the exact plan.

### P0-EXT-008 — Simulated provider failure

A provider rejection before any modeled effect produces `failed/not_executed`;
retry is permitted only when the Plan's fixed safety guard still holds.

### P0-EXT-009 — Late response

After timeout enters reconciliation, a late response is evidence only. Current
simulated target state decides the result; arrival order cannot trigger a
second operation.

### P0-EXT-010 — Partial effect

The simulator applies only part of an ordered operation. Result is
`partially_applied`／`uncertain`, automatic continuation stops, and the exact
compensation or human route is selected.

### P0-EXT-011 — Duplicate request

A duplicate request with the same idempotency key is counted once. Without a
valid idempotency guarantee, the duplicate is rejected rather than resent.

### P0-EXT-012A — Reconciliation proves success

Current target state proves all exact postconditions, so the uncertain
operation becomes `succeeded` without another write.

### P0-EXT-012B — Reconciliation proves not executed

Current target preconditions prove no effect occurred; result becomes
`not_executed`, and retry eligibility is reevaluated against the still-current
approval.

### P0-EXT-013 — Reconciliation unavailable

The target cannot be queried or facts conflict. State remains `uncertain`,
retry stops and human decision is required.
