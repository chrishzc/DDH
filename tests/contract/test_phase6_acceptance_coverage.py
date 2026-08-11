import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "semantic-specifications" / "ddh-phase-6" / "draft" / "acceptance-scenarios.json"
TEST = "tests/unit/test_phase6_learning.py"
MAP = {
    "P6-TERM-001":"test_terminal_handoff_preserves_product_result_when_learning_fails", "P6-TERM-002":"test_sealed_ledger_is_bounded_and_rejects_prohibited_content",
    "P6-LEDGER-001":"test_sealed_ledger_is_bounded_and_rejects_prohibited_content", "P6-LEDGER-002":"test_prefilter_is_zero_agent_and_non_blocking", "P6-LEDGER-003":"test_prefilter_is_zero_agent_and_non_blocking", "P6-LEDGER-004":"test_fold_is_idempotent_and_raw_ledger_is_not_retained",
    "P6-CAND-001":"test_priority_trigger_and_expiration", "P6-CAND-002":"test_priority_trigger_and_expiration", "P6-CAND-003":"test_priority_trigger_and_expiration", "P6-CAND-004":"test_prefilter_is_zero_agent_and_non_blocking",
    "P6-MEM-001":"test_memory_whitelist_guidance_access_and_unavailable_baseline", "P6-MEM-002":"test_memory_whitelist_guidance_access_and_unavailable_baseline", "P6-MEM-003":"test_memory_whitelist_guidance_access_and_unavailable_baseline", "P6-MEM-004":"test_memory_whitelist_guidance_access_and_unavailable_baseline", "P6-MEM-005":"test_memory_whitelist_guidance_access_and_unavailable_baseline",
    "P6-EVO-001":"test_promotion_requires_separated_identities_and_regression_suspends_memory", "P6-EVO-002":"test_promotion_requires_separated_identities_and_regression_suspends_memory", "P6-EVO-003":"test_promotion_requires_separated_identities_and_regression_suspends_memory", "P6-EVO-004":"test_promotion_requires_separated_identities_and_regression_suspends_memory", "P6-EVO-005":"test_priority_trigger_and_expiration",
    "P6-FAIL-001":"test_terminal_handoff_preserves_product_result_when_learning_fails", "P6-FAIL-002":"test_prefilter_is_zero_agent_and_non_blocking", "P6-FAIL-003":"test_memory_whitelist_guidance_access_and_unavailable_baseline", "P6-FAIL-004":"test_terminal_handoff_preserves_product_result_when_learning_fails", "P6-FAIL-005":"test_fold_is_idempotent_and_raw_ledger_is_not_retained",
}


class Phase6AcceptanceCoverageTests(unittest.TestCase):
    def test_every_phase6_scenario_maps_to_an_executable_test(self):
        scenarios = json.loads(CATALOG.read_text(encoding="utf-8"))["scenarios"]
        self.assertEqual({item["scenario_id"] for item in scenarios}, set(MAP))
        source = (ROOT / TEST).read_text(encoding="utf-8")
        for test_name in MAP.values():
            with self.subTest(test_name=test_name): self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__": unittest.main()
