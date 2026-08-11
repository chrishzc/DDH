import unittest
from datetime import UTC, datetime, timedelta

from ddh.contracts import ContractError
from ddh.learning import AttemptLedger, LearningHandoff, LearningIntake, MemoryRegistry, OrchestrationMemory, PromotionEvidence, prefilter


NOW = datetime(2026, 8, 8, tzinfo=UTC)


def ledger(**changes):
    values = dict(ledger_id="l1", execution_identity="wp-1", specification_identity="spec", scope_identity="scope", risk_profile="L2", orchestration_versions=("template@1",), attempts=("attempt",), cost_summary=(("agent", 0),), failure_fingerprint="context-expansion", recovery_route="serial", new_information=True, priority="P2", terminal_outcome="failed")
    values.update(changes)
    return AttemptLedger(**values)


def evidence(**changes):
    values = dict(author_identity="author", critic_identity="critic", replay_identity="replay", trial_writer_identity="trial", policy_valid=True, replay_passed=True, shadow_passed=True, canary_passed=True, metric_improved=True, counterexamples_handled=True, rollback_ready=True)
    values.update(changes)
    return PromotionEvidence(**values)


class Phase6LearningTests(unittest.TestCase):
    def test_sealed_ledger_is_bounded_and_rejects_prohibited_content(self):
        self.assertTrue(ledger().seal().sealed)
        with self.assertRaisesRegex(ContractError, "prohibited_content"):
            ledger(attempts=("prompt",)).seal()

    def test_prefilter_is_zero_agent_and_non_blocking(self):
        routine = ledger(new_information=False, terminal_outcome="routine_success").seal()
        self.assertEqual("consumed_deleted", prefilter(routine).outcome)
        self.assertFalse(prefilter(routine).requires_agent)
        self.assertEqual("learning_input_unavailable_deleted", prefilter(ledger().seal(), False).outcome)

    def test_terminal_handoff_preserves_product_result_when_learning_fails(self):
        class BrokenIntake:
            def ingest(self, *_): raise OSError("queue down")
        product = {"completion": "published"}
        result, disposition = LearningHandoff().publish_terminal_then_ingest(product, ledger(), BrokenIntake(), NOW)
        self.assertIs(product, result)
        self.assertEqual("learning_input_unavailable", disposition.reason_code)

    def test_fold_is_idempotent_and_raw_ledger_is_not_retained(self):
        intake = LearningIntake()
        first = intake.ingest(ledger(), NOW)
        second = intake.ingest(ledger(), NOW)
        self.assertEqual("fold_candidate", first.outcome)
        self.assertEqual("ledger_already_disposed", second.reason_code)
        candidate = next(item for item in intake._candidates.values())
        self.assertEqual(1, candidate.support_count)

    def test_priority_trigger_and_expiration(self):
        intake = LearningIntake()
        for index in range(3): intake.ingest(ledger(ledger_id=f"l{index}", execution_identity=f"wp-{index % 2}"), NOW)
        candidate = next(item for item in intake._candidates.values())
        self.assertTrue(intake.analysis_due(candidate, NOW))
        self.assertEqual((candidate.candidate_id,), intake.expire(NOW + timedelta(days=15)))

    def test_memory_whitelist_guidance_access_and_unavailable_baseline(self):
        registry = MemoryRegistry()
        memory = OrchestrationMemory("m", 1, "initial_context", "L1", "use summary", ("change scope",), 3, 0, 900, NOW + timedelta(days=1))
        registry.promote(memory, evidence())
        self.assertEqual(1, len(registry.guidance("planning", True, NOW)))
        with self.assertRaisesRegex(ContractError, "child_agent_memory_access"):
            registry.guidance("planning", False, NOW)
        self.assertEqual(("single_main_agent", "bounded_initial_context", False), registry.unavailable_baseline())
        with self.assertRaisesRegex(ContractError, "category_prohibited"):
            OrchestrationMemory("bad", 1, "product_behavior", "x", "bad", (), 0, 0, 1, NOW)

    def test_promotion_requires_separated_identities_and_regression_suspends_memory(self):
        registry = MemoryRegistry()
        memory = OrchestrationMemory("m", 1, "recovery_ordering", "L2", "try safe route", (), 3, 1, 800, NOW + timedelta(days=1))
        with self.assertRaisesRegex(ContractError, "promotion_rejected"):
            registry.promote(memory, evidence(critic_identity="author"))
        registry.promote(memory, evidence())
        self.assertEqual("suspended", registry.suspend_on_regression("m@1").state)


if __name__ == "__main__": unittest.main()
