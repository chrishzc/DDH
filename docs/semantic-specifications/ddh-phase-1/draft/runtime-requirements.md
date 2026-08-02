# Phase 1 Runtime Requirements

## 1. Required Vertical Slice

```text
confirmed Task Specification
→ readiness／risk／budget projection
→ System Map consumption or bounded live fallback
→ bounded Context Envelope
→ Host-pull Agent Work Request
→ patch proposal or isolated Candidate
→ actual-diff admission and impact reconciliation
→ immutable Candidate
→ independent Verification Asset admission
→ tool-neutral no-Agent verification
→ Completion Judge
→ portable Candidate Bundle
→ non-blocking terminal event
```

Routine execution、Context expansion、tool recovery、repair and retest continue
without human checkpoints. Only authority-bearing changes produce a structured
exception.

## 2. Required Capabilities

### Specification Compiler

- Strictly validate one Specification Package closure.
- Reject missing executable expected behavior before product writes.
- Bind the exact confirmed version and digest.
- Generate Work Package projections without becoming a second authority.

### System Map Consumer

- Resolve selected Global／Domain／Subsystem／Module nodes.
- Query hierarchy、direct dependencies、direct reverse dependencies and
  resource bindings.
- Bind results to repository、branch／ref、resolved commit and Map view.
- Record which query facts downstream artifacts actually consume.
- Use bounded live discovery for only the affected unavailable／partial area.
- Never grant scope、risk、test、completion or write authority.

### Context Curator

- Materialize the minimum initial Context Envelope.
- Process purpose-bound incremental Context Requests.
- Charge Context budget without duplicating unchanged content.
- Deny irrelevant／duplicate requests without blocking independent progress.
- Never turn a Context grant into write authority.

### Host-pull Agent Driver Port

- Publish a typed Work Request and accept a typed Agent Result.
- Support `patch_proposal` and capability-proven `isolated_candidate`.
- Prohibit `direct_user_workspace`.
- Treat Agent-declared touched paths、usage and completion as untrusted claims.
- Automatically route context insufficiency、stale result、timeout、
  protocol conflict and no-progress.

### Change Guard and Candidate Controller

- Materialize a disposable repository copy from the actual working tree.
- Keep the original user workspace untouched.
- Exclude VCS control metadata that could reference the original repository.
- Record a baseline manifest that includes unrelated dirty state.
- Recompute actual changed paths、renames、deletes、untracked and generated
  resources.
- Reject a mixed valid／invalid result as one admission unit while preserving
  its private delta for bounded rework.
- Expand verification closure from actual impact without expanding writes.
- Freeze an immutable content-addressed Candidate and reject late generations.

### Test Auditor

- Map proposed Verification Assets to specification scenarios and current
  Candidate identity.
- Block assertion deletion、expected-value widening、threshold lowering、
  fixture shrinking、case removal and new skip／xfail.
- Keep immutable acceptance assets outside Agent write scope.
- Require independent admission whenever Verification Assets changed.

### Verification Runner

- Execute admitted tool-neutral Verification Assets against one immutable
  Subject、Candidate、Environment and plan.
- Provide a pytest reference adapter and one non-pytest fixed-command adapter.
- Never accept a generic shell executor.
- Use direct argv、adaptive bounded timeout、bounded output and process-tree
  cleanup.
- Separate product failure、suspected asset defect、environment／runner failure、
  timeout、cancelled and incomplete.
- Publish typed result independently from stdout、stderr and exit code.

### Completion Judge

- Read canonical current Specification、Candidate、admitted assets、verification
  verdict、actual-diff closure and exception closure.
- Publish only `work_package_completed`.
- Refuse incomplete、stale、wrong-subject or mixed required results.
- Require no additional human completion approval.

### Minimal Recovery and Telemetry

- Apply only confirmed safe routes for Context、Agent Driver、Change Guard and
  runner failures.
- Do not retry identical inputs／strategy／failure fingerprint without new
  evidence.
- Maintain local capability health and bounded per-Invocation JSONL events.
- Keep raw output、prompts、source and secrets out of long-lived records.
- Emit a non-blocking terminal event; do not implement Learning Analyzer、
  Critic or Memory Registry.

## 3. Contract Envelope and Identity

All handoffs use UTF-8 strict JSON Contract Envelope v1 and minimal typed
references:

- Versioned Authority Reference.
- Lifecycle Reference.
- Content Reference.
- Invocation Reference.

JCS／SHA-256 content identity、duplicate-key rejection、atomic publication and
fail-closed unknown authoritative fields are required. No permanent provenance
chain is created.

## 4. Work Request、Context Request and Agent Result

Work Request binds exact Task Specification、Work Package、Candidate baseline、
Invocation、Agent Goal projection and source、Context、Map query、mutation mode、
write／test boundaries、acceptance、budgets and escalation conditions.

Context Request binds purpose、current Context generation、requested selectors、
supporting evidence、estimated value／cost and whether work can continue. Its
disposition can grant、partially grant、deny or require replanning; it always
reports `write_authority_changed: false`.

Agent Result can propose a Candidate、request Context、request a scope change、
report an implementation block or cancel. It cannot declare verification PASS、
completion、higher-layer state、acceptance change or scope expansion.

## 5. Confirmation Channels

The core exposes one Confirmation Port:

- Local CLI confirmation is the always-available offline fallback.
- A typed Host UI／MCP channel is valid only when the host mechanically
  distinguishes a human interaction from model-produced content.
- Either channel confirms one exact package digest; double confirmation is not
  required.
- If host capability is absent or unknown, fall back to CLI.

The record is stored outside Agent-writable scope and is not a cryptographic
approval chain or legacy Checkpoint.

## 6. State、Events and Restart

- Runtime state uses per-Invocation Atomic JSON with generation compare-and-
  swap and atomic replace.
- Bounded JSONL events provide short-lived observability, not canonical state.
- Same identity＋same digest is idempotent; same identity＋different digest is a
  protocol conflict.
- Restart reconstructs pending work from Specification、Candidate and
  Invocation state.
- Terminal cleanup never removes user source、dirty diff、accepted Verification
  Assets or an unconsumed Candidate Bundle.

## 7. Candidate Handoff

Phase 1 exports a Portable Candidate Bundle containing:

```text
candidate-manifest.json
changes.patch
blobs/
verification-assets/
typed-verification-result.json
```

The Bundle binds Specification、baseline、Candidate、changed resources、
Verification Subject、admitted assets and Completion Judge result. It is a
short-lived handoff artifact and is not automatically applied to the user
workspace.

