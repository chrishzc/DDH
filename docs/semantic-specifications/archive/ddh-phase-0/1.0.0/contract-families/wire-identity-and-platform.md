# Wire, Identity, and Platform Contract Scenarios

## Contract References

- `docs/decisions/0016-json-contract-envelope-v1.md`
- `docs/decisions/0017-minimal-typed-identity-references.md`
- `docs/decisions/0022-mvp-supported-platform-matrix.md`

## Scenarios

### P0-WIRE-001 — Valid Contract Envelope

A UTF-8 JSON message containing the common envelope fields, current typed
subject references and a message-specific payload is accepted. The execution
channel, not a producer field in JSON, supplies trusted execution identity.

### P0-WIRE-002 — Unsupported major

An otherwise valid message with protocol version `2.0.0` is rejected as
`protocol_incompatible`. The consumer does not guess compatible fields.

### P0-WIRE-003 — Unknown authoritative field

An unknown field in the common envelope or authoritative payload is rejected.
Optional extension data is accepted only under an approved namespaced
`extensions` member defined by that payload schema.

### P0-WIRE-004 — Duplicate JSON key

Input containing duplicate keys is rejected before schema validation. The last
duplicate value must not silently win.

### P0-WIRE-005 — Pending result after crash

`result.pending` exists after backend termination and `result.json` does not.
The consumer reports incomplete transport and never consumes the pending file
as a formal result.

### P0-WIRE-006 — Cross-language canonical digest

Python、Rust and Go conformance adapters receive the same decimal-string and
Unicode fixture. RFC 8785 canonical bytes and SHA-256 digest must be identical;
a mismatched digest is rejected, not normalized by consumer preference.

### P0-WIRE-007 — Invalid authoritative enum

An unknown terminal／completeness enum is rejected as
`protocol_invalid_enum`. It cannot be treated as `unknown`, PASS or retryable.

### P0-WIRE-008 — Oversized or overdeep payload

Input beyond the fixed byte、nesting、array or string limit is rejected before
unbounded allocation and produces a bounded reason.

### P0-WIRE-009 — Concurrent invocation isolation

Ten thousand logical invocations use distinct invocation directories.
Request、pending and result files cannot cross directories or Work Packages.

### P0-WIRE-010 — Fuzzed malformed input

Malformed UTF-8、truncated JSON、unexpected types and adversarial nesting are
boundedly rejected without Harness crash or model invocation.

### P0-ID-001 — Specification digest drift

The same specification ID／version arrives with a different content digest.
The consumer reports authority drift and rejects the handoff.

### P0-ID-002 — Late partition generation

A valid patch is bound to an older partition generation. Patch Admission
returns stale and does not merge it into the current candidate.

### P0-ID-003 — Same subject retry

A safe retry preserves the Verification Subject reference but creates a new
Invocation Reference. Reusing an invocation ID with a different result is a
protocol conflict.

### P0-ID-004 — Duplicate, late, and out-of-order result

Duplicate current results are idempotent; a late old generation is stale; an
out-of-order result waits for or reconciles against current lifecycle facts.
None can replace the current subject result by arrival order.

### P0-ID-005 — Candidate or environment mismatch

A result bound to a different Candidate or Environment Profile is rejected
even when the suite names and apparent PASS output match.

### P0-ID-006 — Same Candidate with different acceptance

Changing Verification Contract／acceptance produces a different Verification
Subject even if product Candidate bytes are unchanged.

### P0-ID-007 — Conflicting reuse of invocation ID

The same invocation ID carrying different structured results is
`protocol_conflict`; neither result is selected by timestamp.

### P0-ID-008 — Same Map reference, changed branch

An unchanged System Map node reference cannot preserve a result after actual
branch／resolved commit／Candidate changes.

### P0-ID-009 — Parallel cross-Work-Package absorption

Many parallel invocations with equal suite names remain isolated by typed Work
Package、Subject and Invocation references; cross-Work-Package absorption is
rejected.

### P0-ID-010 — Restart reconstruction

After runtime restart, current Specification、Work Package、Candidate、Asset
Manifest and Environment facts rebuild the required references. No permanent
identity history、Checkpoint or Attempt Ledger is required.

### P0-PLAT-001 — Required platform semantics

Windows 11 x86_64 and Ubuntu 24.04 LTS x86_64 interpret the same logical
Unicode repository path and strict UTF-8 artifact identically. Machine
absolute paths never participate in portable content identity.

### P0-PLAT-002 — Preview platform

A result from macOS、ARM64、WSL2 or another preview platform may be diagnostic
but cannot satisfy the required release matrix.

### P0-PLAT-003 — Unbounded output

Large stdout／stderr is bounded and summarized outside the control result. It
cannot corrupt、replace or expand the formal result envelope.
