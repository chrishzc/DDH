# Phase 2 Reference Recovery Fixture

## Purpose

The reference fixture extends the Phase 1 disposable portable workspace with
deterministic fault injection. It proves recovery routing without adding a DDH
product-domain feature or invoking a real external system.

## Business Scenario

A confirmed path-normalization Work Package must repair a localized product
defect. During execution, controlled adapters inject failures that commonly
cause an Agent workflow to stop and ask a human how to repair its own tools.

Phase 2 must instead distinguish product, test, runner, Context, System Map,
stale identity, impact and authority failures, then follow the fixed route for
each class.

## Required Fault Injections

The fixture must provide deterministic, no-network adapters for:

1. product verification failure followed by a relevant source delta;
2. Verification Asset implementation defect with unchanged semantics;
3. ambiguous expected behavior that cannot be repaired automatically;
4. unavailable runner backend with one approved equivalent fallback;
5. unavailable backend with no approved route remaining;
6. insufficient Context followed by one purpose-bound grant;
7. unavailable or partial System Map followed by bounded live-source facts;
8. stale Candidate generation and stale Verification Asset identity;
9. an actual reverse dependent outside the predicted verification closure;
10. a required repair outside current write scope;
11. an uncertain external-side-effect request that must not execute or retry;
12. repeated identical failure and a later attempt with genuine new evidence;
13. recovery budget exhaustion with preserved Candidate and diff.

## Invariants

- Every run starts from the same immutable Phase 1 baseline fixture.
- Fault injection changes adapter facts, not Task Specification authority.
- Product and test repair never mutate the original user workspace.
- Approved fallback keeps the exact Candidate, Verification Subject,
  acceptance and required scenarios.
- A new Candidate, asset, environment, Context, impact fact or approved
  strategy receives a new generation identity.
- The same inputs, fingerprint and strategy without new evidence are rejected
  before another Agent or runner action.
- External operations, network, credentials and real databases remain absent.

## Failure Bundle Corpus

Synthetic diagnostics include repeated tracebacks, multibyte text, duplicate
scenario references and out-of-order stale results. The runtime must retain
only bounded useful excerpts and normalized identities; the full synthetic
corpus must not enter Agent Context or long-lived state.

## Completion

The fixture completes only when:

- every automatic route preserves authority and required verification;
- every human-owned boundary produces one structured exception;
- exhausted routes stop without weakening acceptance;
- stale or incomplete evidence cannot satisfy Completion Judge;
- safe product repair reaches `work_package_completed` without intermediate
  human checkpoints.
