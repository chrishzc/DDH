# Phase 3 Coordination Contract and Data Model

This document fixes behavior and serializable fields without fixing a storage
engine, process model, queue, Agent vendor, System Map schema or remote service.

## 1. Typed References

The runtime reuses the minimal identities from Decision 0017:

- `VersionedAuthorityReference(id, version, content_digest)`;
- `LifecycleReference(id, generation)`;
- `ContentReference(id, content_digest)`; and
- `InvocationReference(invocation_id, attempt)`.

Absolute paths, timestamps, prompts, Agent-provided identity, logs and System
Map node IDs cannot substitute for these references.

## 2. Parallel Assessment

```text
ParallelAssessment
├─ work_package: LifecycleReference
├─ candidate: LifecycleReference + ContentReference
├─ selected_scope_nodes[]
├─ consumed_architecture_query: ContentReference
├─ independent_work_units[]
├─ physical_overlap[]
├─ logical_overlap[]
├─ coupling_and_contract_facts[]
├─ worker_capabilities[]
├─ projected_costs
│  ├─ agent_usage
│  ├─ context_ingestion
│  ├─ environment_setup
│  ├─ critic_and_test_admission
│  └─ central_integration
├─ projected_wall_time_benefit
├─ result
└─ reasons[]
```

`result` is one of `parallel_allowed`, `parallel_not_worthwhile`,
`parallel_unsafe` or `needs_human_decision`.

## 3. Module Work Group and Work Lane

```text
ModuleWorkGroup
├─ group: LifecycleReference
├─ module_node_reference
├─ sub_goal
├─ product_lane: LifecycleReference
├─ acceptance_lane: LifecycleReference
├─ shared_contract_references[]
├─ required_module_scenarios[]
├─ required_subsystem_scenarios[]
├─ fixed_integration_order
├─ readiness_components
└─ state
```

```text
WorkLane
├─ lane: LifecycleReference
├─ work_group: LifecycleReference
├─ lane_kind: product | acceptance | subsystem_acceptance | integration
├─ trusted_writer_reference
├─ task_specification: VersionedAuthorityReference
├─ work_package: LifecycleReference
├─ base_candidate: LifecycleReference + ContentReference
├─ sub_goal
├─ acceptance_references[]
├─ allowed_resources: ResourceSet
├─ prohibited_resources: ResourceSet
├─ shared_resource_policy_references[]
├─ context_envelope: ContentReference
├─ budget_references[]
├─ local_feedback_requirements[]
├─ escalation_conditions[]
├─ submission_contract
└─ state
```

Lane states are:

```text
planned → activating → active → implementation_ready
→ module_verified → waiting_for_subsystem_join → frozen → submitted
```

Exceptional terminal or holding states are `revoked` and
`recovery_required`. A lane may skip Module-specific intermediate states when
its lane kind does not use them, but it cannot skip mechanical activation,
quiescence or submission binding.

## 4. Resource Set and Write Assignment

```text
ResourceSet
├─ canonical_physical_resources[]
├─ logical_resources[]
├─ protected_resources[]
├─ generated_resource_groups[]
├─ shared_resource_references[]
├─ source_snapshot_reference
└─ content_digest
```

```text
WriteAssignment
├─ work_package
├─ lane
├─ lane_generation
├─ trusted_writer_reference
├─ base_candidate
├─ resource_set_digest
├─ mutation_mode
├─ boundary_instance
├─ activation_epoch
└─ state: planned | boundary_active | fenced | draining | quiescent | revoked
```

The Write Assignment is scoped execution ownership, not a permanent Source
Lock. It exists only while parallel/shared work needs a mechanically identified
writer. The same logical resource has at most one `boundary_active` writer.

## 5. Context Envelope

```text
ContextEnvelope
├─ task_specification
├─ work_package
├─ lane and generation
├─ base_candidate
├─ pinned_goal
├─ acceptance_and_prohibitions[]
├─ required_contracts[]
├─ architecture_query_reference
├─ consumed_nodes_and_relations[]
├─ source_selectors[]
├─ write_boundary_information
├─ local_feedback_requirements[]
├─ budget_references[]
├─ escalation_conditions[]
└─ invalidation_epoch
```

It is rebuildable and Candidate-bound. It carries no write permission.

## 6. Cross-Lane Change Request

```text
CrossLaneChangeRequest
├─ requesting_lane and generation
├─ target_resource
├─ requested_change_kind
├─ reason and root_cause_evidence
├─ specification_and_acceptance_references[]
├─ current_owner_or_overlap[]
├─ consequence_if_denied
├─ test_context_budget_and_integration_impact
└─ recommendation
```

The coordinator returns `route_to_current_writer`,
`repartition_within_scope`, `serialize_shared_change`,
`reject_unnecessary_request` or `human_scope_or_spec_decision`.

## 7. Lane Submission and Patch Admission

```text
LaneSubmission
├─ task_specification and work_package
├─ lane, writer and generation
├─ base_candidate
├─ delta: ContentReference
├─ touched_resource_manifest: ContentReference
├─ local_feedback_results[]
├─ admitted_test_asset_references[]
├─ unresolved_requests[]
└─ submission_identity
```

```text
PatchAdmissionDecision
├─ submission_identity
├─ expected_candidate_generation
├─ actual_physical_and_logical_delta[]
├─ freshness_classification
├─ consumed_impact_query
├─ result
├─ reason_codes[]
├─ resulting_candidate
└─ required_revalidation[]
```

Admission results are `accepted_into_candidate`,
`accepted_revalidation_required`, `rejected_scope_or_partition`,
`rejected_stale_result`, `integration_conflict_rework_required` or
`human_change_decision_required`.

## 8. Handoff and Quiescence

```text
HandoffRecord
├─ old_lane_generation
├─ freeze_fence_epoch
├─ in_flight_operation_classifications[]
├─ user_baseline_reference
├─ preserved_agent_delta_reference
├─ mutation_closure
├─ revoked_boundary_reference
├─ new_lane_generation
├─ bounded_context_increment
└─ outcome
```

```text
QuiescenceReport
├─ integration_group
├─ target_lane_generations[]
├─ trusted_writers_and_boundaries[]
├─ fence_epochs[]
├─ pre_fence_operations[]
├─ post_fence_rejections[]
├─ admitted_delta_references[]
├─ unknown_mutation_states[]
├─ sealed_lane_generations[]
└─ outcome
```

Handoff outcomes are `handoff_completed`, `handoff_no_agent_delta`,
`handoff_recovery_required` or `handoff_cancelled`. Quiescence cannot be inferred
from an Agent result or process exit.

## 9. Join and Integrated Candidate

```text
JoinPlan
├─ task_specification and work_package
├─ integration_group
├─ required_work_groups[]
├─ required_lane_generations[]
├─ fixed_integration_order[]
├─ shared_contract_references[]
├─ required_test_asset_references[]
├─ pre_join_architecture_query
├─ live_reconciliation_profile
└─ join_condition_digest
```

```text
IntegratedCandidateManifest
├─ source_snapshot_id
├─ candidate_generation
├─ parent_candidate
├─ baseline_and_user_delta_references[]
├─ accepted_submission_references[]
├─ complete_resource_manifest
├─ quiescence_report
├─ consumed_architecture_queries[]
├─ changed_nodes_and_reverse_dependents[]
├─ integration_order
├─ invalidation_epoch
└─ manifest_digest
```

`JoinResult` is `waiting_for_current_lanes`, `waiting_for_quiescence`,
`integration_rework_required`, `candidate_frozen`, `freeze_recovery_required`
or `human_change_decision_required`.

## 10. Completion Projection

```text
LayerCompletionDecision
├─ task_specification
├─ work_package
├─ verification_subject
├─ completion_layer
├─ required_scenarios[]
├─ current_mechanical_verdict
├─ impact_closure_reference
├─ open_exceptions[]
└─ outcome
```

The reference flow evaluates `work_package_completed` and
`subsystem_integrated` independently. The object must represent
`domain_accepted` and `release_candidate` as `not_evaluated`, never infer them.

## 11. Persistence and Retention

Canonical state contains only current Work Package, lanes, active/fenced
assignments, admitted submissions, Candidate manifests, Verification Subjects
and open exceptions needed for restart. Routine raw logs and conversations are
not state.

Short-term attempt summaries and rejected private deltas may be retained only
for bounded recovery. Reusable CI verification assets remain the durable
functional evidence. Long-term learning and Attempt Ledger digestion remain
deferred; Phase 3 must expose bounded events without creating permanent raw-log
retention.

