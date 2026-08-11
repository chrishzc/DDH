# Verification Asset Data Model and Governance Contract

## Manifest model

```text
VerificationAssetManifest {
  asset_id, version, immutable_digest, supersedes?
  asset_kind, tool_adapter, scope_layer, architecture_targets
  requirement_refs, scenario_refs, semantic_spec_refs, contract_refs
  quality_profile_ref, quality_add_ons, applicability_reasons
  source_dependencies, asset_dependencies, fixture_dependencies,
  helper_dependencies, config_dependencies, schema_dependencies,
  runner_and_toolchain_dependencies
  fixed_entrypoint, selectors, environment_profile, timeout, output_limit
  oracle_definition, expected_result, result_protocol
  admission_state, validity_disposition, execution_eligibility
}
```

`asset_id + version + immutable_digest` is the manifest identity. Supersession
is a version relation, never an execution result. Every required scenario has
at least one admitted asset mapping before the corresponding completion can be
evaluated.

## Independent state axes

```text
admission: draft | candidate | admission_validating | admitted | rejected
validity: current | rerun_required | suspect | stale | quarantined | retired
execution: not_run | passed | failed | error | timeout | unavailable | invalidated
```

Only `admitted + current + execution-eligible` becomes `active`. `rerun_required`
means the asset remains semantically admissible but must rerun for the new
Candidate. `suspect` awaits a deterministic validity inquiry; `stale` has an
invalid dependency binding; `quarantined` is excluded pending repair/inquiry;
`retired` is excluded permanently. No state transition infers a PASS.

## Admission guard

The Mechanical Acceptance Guard rejects any unapproved difference that deletes
assertions, widens expected values, lowers thresholds, shrinks fixtures, removes
cases, adds/abuses skip/xfail/exclusion, removes required markers, or weakens an
oracle. Independent Test Auditor review plus known-bad/mutation-style probes
must show fault sensitivity. The proposer cannot repair an asset and self-admit
it; critic/probe evidence is independent of the implementation/test author.

## Structured exception envelope

```json
{
  "exception_type": "specification_not_ready",
  "missing": ["oracle_definition"],
  "blocked_asset_ids": ["VA-example@1.0.0"],
  "allowed_action": "obtain_confirmed_specification",
  "automatic_relaxation": false
}
```

`quality_policy_gap` and `quality_budget_conflict` use the same envelope shape.
The latter permits equivalent cost optimization only; neither permits reduced
semantic coverage, oracle, required threshold, or external side effect.

