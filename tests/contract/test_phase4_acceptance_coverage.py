import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPOSITORY_ROOT / "docs" / "semantic-specifications" / "ddh-phase-4" / "draft" / "acceptance-scenarios.json"
TEST_FILE = "tests/unit/test_phase4_verification_assets.py"

SCENARIO_TEST_MAP = {
    "P4-CAT-001": "test_catalog_is_rebuildable_and_tool_neutral",
    "P4-CAT-002": "test_catalog_is_rebuildable_and_tool_neutral",
    "P4-CAT-003": "test_missing_mapping_returns_structured_not_ready",
    "P4-CAT-004": "test_catalog_is_rebuildable_and_tool_neutral",
    "P4-ADM-001": "test_admission_requires_independent_auditor_and_known_bad_for_repair",
    "P4-ADM-002": "test_executor_cannot_bypass_admission_or_bindings",
    "P4-ADM-003": "test_executor_uses_fixed_entrypoint_and_unavailable_is_not_pass",
    "P4-ADM-004": "test_executor_uses_fixed_entrypoint_and_unavailable_is_not_pass",
    "P4-LIFE-001": "test_admission_requires_independent_auditor_and_known_bad_for_repair",
    "P4-LIFE-002": "test_missing_mapping_returns_structured_not_ready",
    "P4-LIFE-003": "test_quality_na_requires_business_reason_and_retirement_is_inactive",
    "P4-LIFE-004": "test_quality_na_requires_business_reason_and_retirement_is_inactive",
    "P4-WEAK-001": "test_mechanical_guard_rejects_each_weakening_form",
    "P4-WEAK-002": "test_mechanical_guard_rejects_each_weakening_form",
    "P4-WEAK-003": "test_mechanical_guard_rejects_each_weakening_form",
    "P4-WEAK-004": "test_admission_requires_independent_auditor_and_known_bad_for_repair",
    "P4-CUR-001": "test_currentness_is_minimal_and_source_only_requires_rerun",
    "P4-CUR-002": "test_currentness_is_minimal_and_source_only_requires_rerun",
    "P4-CUR-003": "test_map_consumption_and_live_fallback_are_required",
    "P4-CUR-004": "test_map_consumption_and_live_fallback_are_required",
    "P4-COST-001": "test_catalog_is_rebuildable_and_tool_neutral",
    "P4-COST-002": "test_quality_na_requires_business_reason_and_retirement_is_inactive",
    "P4-COST-003": "test_quality_na_requires_business_reason_and_retirement_is_inactive",
    "P4-COST-004": "test_cost_optimization_retains_every_required_asset_and_evidence_is_bounded",
    "P4-COST-005": "test_cost_optimization_retains_every_required_asset_and_evidence_is_bounded",
    "P4-EVID-001": "test_cost_optimization_retains_every_required_asset_and_evidence_is_bounded",
    "P4-EVID-002": "test_executor_cannot_bypass_admission_or_bindings",
    "P4-EVID-003": "test_catalog_is_rebuildable_and_tool_neutral",
}


class Phase4AcceptanceCoverageTests(unittest.TestCase):
    def test_every_fixed_phase4_scenario_maps_to_an_executable_test(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        scenario_ids = {item["scenario_id"] for item in catalog["scenarios"]}
        self.assertEqual(scenario_ids, set(SCENARIO_TEST_MAP))
        source = (REPOSITORY_ROOT / TEST_FILE).read_text(encoding="utf-8")
        for test_name in SCENARIO_TEST_MAP.values():
            with self.subTest(test_name=test_name):
                self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
