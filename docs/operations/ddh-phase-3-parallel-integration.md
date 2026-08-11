# DDH Phase 3 Parallel Integration Operations

Phase 3 implements the L2 reference slice fixed by
`DDH-P3-SPEC-001@1.0.0` with closure digest
`8add85a45d96bdbc8b158405d87c510efcbe3403639c036034d8f83584053a00`.

## Runtime Boundary

`Phase3Runtime` accepts a confirmed L2 workload, a `ParallelWorkPlan`, typed
lane drivers, a mechanical local-lane verifier, a verification-asset provider,
and capability-based System Map adapters.

The plan describes Module Work Groups, product and acceptance lanes, fixed
integration order and projected parallel/serial cost. The runtime only enables
parallel work when the projected parallel cost is lower and isolated Candidate
write separation is available. Otherwise it returns
`parallel_not_worthwhile` or `parallel_unsafe` before dispatching workers.

## Normal Sequence

```text
System Map query consumed
→ assessment
→ exact Change Guard activation
→ asynchronous lane submissions
→ central admission in fixed order
→ fence and quiescence
→ immutable integrated Candidate
→ refreshed System Map impact query
→ integrated verification
→ separate Work Package / Subsystem decisions
```

Workers submit private deltas only. A worker result, prompt instruction or local
PASS never directly changes the integration Candidate. The `CentralIntegrator`
is the only writer that admits lane delta. `JoinBarrier` fences every current
writer and fails closed when an in-flight operation remains.

## Operational Constraints

- Use `isolated_candidate` for the Phase 3 reference slice.
- Product and acceptance assets must occupy separate Work Lanes.
- A required test asset is not final evidence until the Test Auditor admits it
  and it reruns against the frozen integrated Candidate.
- System Map results must be bound to repository/ref/commit and consumed before
  fork and after actual integration delta. They remain architecture facts, not
  authorization.
- `domain_accepted` and `release_candidate` are not produced by this runtime.
- Database, network, credentials, deployment, release and mutation of a real
  user workspace remain outside Phase 3.

## Reference Evidence

The PortableWorkspace fixture runs three Module product/acceptance pairs plus
one Subsystem acceptance lane. It proves asynchronous dispatch, deterministic
central order, late/mixed-scope rejection, quiescence before freeze, integrated
rerun and separate completion outcomes.
