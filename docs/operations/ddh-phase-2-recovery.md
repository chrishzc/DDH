# DDH Phase 2 Recovery Operations

Phase 2 implements the serial recovery slice fixed by
`DDH-P2-SPEC-001@1.0.0` with closure digest
`e0c0edab20ecdc3ec888ba15dcbd03d9e21d11c9037a376db9dc03a214a87f5e`.
It extends `Phase1Runtime`; it does not add parallel workers, deployment or
external execution.

## Host integration

Hosts instantiate `Phase2Runtime` with the Phase 1 Ports and may additionally
provide:

- `VerificationBackendRegistry` plus an explicit `RecoveryPolicy`;
- `ImpactAwareVerificationAssetProvider` to select tests from reconciled
  actual impact;
- `TestRepairPort` and a separate `TestRepairProbePort`.

Test repair is enabled only when both repair and mechanical probe Ports exist.
The repair proposer, probe verifier and independent admission identity must be
different. Missing separation produces a structured exception rather than
self-admission.

## Automatic routes

| Failure fact | Automatic action |
|---|---|
| Product assertion failure | Repair inside current write scope and verify a new Candidate. |
| Test implementation defect | Propose repair, mechanically replay original scenarios and known-bad probes, then independently readmit. |
| Transient runner failure | Rebuild a disposable runner environment at most twice. |
| Backend unavailable | Select one ready, equivalent and explicitly approved backend. |
| Context request | Add a purpose-bound, deduplicated increment within the Context budget. |
| Partial System Map result | Consume bounded live-source fallback facts. |
| Stale test asset | Rebuild and admit an asset bound to the current Candidate. |
| Underestimated impact | Select verification from the reconciled impact closure without expanding write scope. |

An identical Candidate and failure cannot consume another verification run.
Recovery budgets already consumed are retained when new evidence appears.

## Human and blocked boundaries

The affected lane stops with an `ExceptionReport` for:

- uncertain expected behavior or acceptance semantics;
- required writes outside the confirmed scope;
- uncertain external or irreversible effects;
- exhausted approved recovery, Context, test-admission, impact or platform
  routes.

An exception report records evidence and requested authority; it is not
confirmation and cannot change the active specification.

## Failure Bundle retention

`FailureBundle` keeps typed Candidate, Verification Subject, asset, scenario,
impact, progress and remaining-budget identities. Diagnostics are redacted,
deduplicated and bounded to the confirmed bootstrap limits. Complete logs,
source contents, prompts and conversations are not retained.

The terminal Invocation state stores only the bounded Bundle and typed result.
Telemetry records route reason codes without raw diagnostics and is not
completion evidence.

## Restart behavior

Before an automatic route continues, Phase 2 atomically records:

- the next Candidate attempt;
- current isolated source root;
- bounded Failure Bundle;
- consumed route ledger and budgets;
- preserved Candidate and typed results.

A restart with the same Invocation and specification digest resumes this
checkpoint. A conflicting specification digest is rejected.

## Verification

Run the repository verification without installing test tools:

```powershell
$env:PYTHONPATH = (Resolve-Path src)
py -3 -m unittest discover -s tests -v
python docs/semantic-specifications/ddh-phase-2/draft/validation/validate_phase2_spec.py
```

`pytest` remains one optional target-project adapter. DDH does not install it
or weaken required verification as recovery.
