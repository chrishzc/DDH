# Phase 5 Operational Contract

```text
EnvironmentProfile {
  profile_id, version, platform_support_tier, os, architecture,
  runtime_versions, tool_versions, dependency_digest, cwd,
  locale, timezone, encoding, environment_allowlist,
  fixture_and_service_requirements, network_capability,
  database_capability, isolation_profile, resource_budget,
  output_limits, filesystem_profile
}

ExecutionPlanGeneration {
  subject_identity, asset_identities, environment_profile_digest,
  shard_plan, business_thresholds, execution_deadline,
  progress_signal_kind, no_progress_deadline?, termination_grace,
  output_limits, work_package_ceiling, plan_generation
}

ManagedAssetPlan {
  manifest_identity, target_identity, dry_run, isolated_output_digest,
  delta_preview, compatibility_verdict, user_customization_conflicts,
  atomic_apply_strategy, parity_expectation
}

BranchMapBinding {
  repository_id, branch, resolved_commit, worktree_id,
  candidate_identity, map_view_id, consumed_facts
}
```

Required structured outcomes include `verification_plan_not_ready`,
`verification_timeout`, `no_progress_detected`, `capability_unavailable`,
`approved_fallback_selected`, `temporary_root_quarantined`,
`managed_asset_user_change_conflict`, `filesystem_profile_unsupported`, and
`branch_map_binding_invalidated`. None is automatically a product failure.

