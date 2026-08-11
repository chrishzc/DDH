# Phase 4 Implementation Boundary

## Before confirmation

Only this new Phase 4 specification package may be written. No files under
`src/`, `tests/`, existing Phase 0–3 packages, decisions, architecture, System
Map, governance state, CI configuration, or external system may be modified.

## After exact confirmation (future authority only)

The future Phase 4 implementation scope is limited to new or explicitly
authorized DDH Verification Asset contracts, deterministic local catalog
rebuild/admission/currentness/runner adapters, their focused tests, and an
operations guide. Any public contract, schema, credential, database, network,
deployment, remote runner, or external pipeline action requires separately
confirmed authority. This package grants none now.

The side-effect budget is zero. Package validation must operate offline using
only local files and Python standard library. It must not require a database,
network, credential, deployment, CI service, or external runner.

## Evidence and completion boundary

Admitted rerunnable manifests and their declared dependencies are retained
evidence. Attempt Ledgers, complete raw logs, individual PASS receipts, shard
receipts, and repeated tracebacks are operationally bounded rather than
permanently retained. Passing Phase 4 package validation proves only package
integrity; it does not implement or integrate a subsystem/domain/release.

