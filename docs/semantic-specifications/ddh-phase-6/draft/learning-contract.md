# Phase 6 Learning Contract

```text
AttemptLedger {
  ledger_id, execution_identity, specification_identity, scope_identity,
  risk_profile, orchestration_versions, attempts, cost_summary,
  priority, terminal_outcome, sealed, serialized_size, truncation_facts
}

LearningCandidate {
  candidate_id, normalized_pattern, priority, applicability,
  support_count, counterevidence_count, work_package_count,
  cost_summary, minimal_examples, created_at, expires_at, state
}

OrchestrationMemory {
  memory_id, immutable_version, category, applicability, recommendation,
  prohibited_uses, support, counterevidence, confidence,
  profile_compatibility, expiration, conflicts, rollback_version, state
}

GuidanceCard {
  memory_identity, transition_kind, bounded_recommendation,
  applicability, confidence, prohibited_uses
}
```

Ledger lifecycle: `open → sealed → prefiltering → consumed_deleted | folded_deleted | learning_input_unavailable_deleted`.
Candidate lifecycle: `pending → analyzing → critic_review → replay → shadow → canary → promoted | rejected | expired`, followed by deletion.
Memory lifecycle: `active → suspended | superseded | expired | rolled_back`.

