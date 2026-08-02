import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "semantic-specifications"
    / "ddh-phase-2"
    / "draft"
    / "acceptance-scenarios.json"
)

SCENARIO_TEST_MAP = {
    "P2-FLOW-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_product_failure_bundle_drives_repair_to_completion",
    "P2-CLASS-001": "tests/unit/test_phase2_failure_and_recovery.py:test_verification_facts_select_exact_failure_class",
    "P2-TEST-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_test_helper_repair_requires_separate_proposal_and_admission",
    "P2-TEST-002": "tests/integration/test_phase2_recovery_vertical_slice.py:test_semantics_and_external_boundaries_do_not_execute_candidate",
    "P2-TEST-003": "tests/unit/test_candidate_and_auditor.py:test_all_mechanical_weakening_dimensions_are_rejected",
    "P2-RUNNER-001": "tests/unit/test_phase2_failure_and_recovery.py:test_runner_rebuilds_twice_then_uses_approved_backend",
    "P2-RUNNER-002": "tests/integration/test_phase2_recovery_vertical_slice.py:test_approved_equivalent_backend_continues_without_human",
    "P2-RUNNER-003": "tests/integration/test_phase2_recovery_vertical_slice.py:test_unapproved_backend_exhaustion_is_platform_exception",
    "P2-CONTEXT-001": "tests/integration/test_phase1_vertical_slice.py:test_context_request_uses_trusted_source_and_continues",
    "P2-CONTEXT-002": "tests/unit/test_paths_context_and_map.py:test_irrelevant_and_duplicate_content_requests_are_denied",
    "P2-MAP-001": "tests/unit/test_paths_context_and_map.py:test_partial_map_uses_bounded_fallback",
    "P2-MAP-002": "tests/integration/test_phase2_recovery_vertical_slice.py:test_actual_impact_selects_verification_without_expanding_write_scope",
    "P2-STALE-001": "tests/unit/test_phase2_failure_and_recovery.py:test_verification_facts_select_exact_failure_class",
    "P2-STALE-002": "tests/integration/test_phase2_recovery_vertical_slice.py:test_stale_asset_is_rebuilt_before_execution",
    "P2-IMPACT-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_actual_impact_selects_verification_without_expanding_write_scope",
    "P2-SCOPE-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_scope_exception_preserves_authority_and_impact_fields",
    "P2-EXTERNAL-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_semantics_and_external_boundaries_do_not_execute_candidate",
    "P2-BUNDLE-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_product_failure_bundle_drives_repair_to_completion",
    "P2-BUNDLE-002": "tests/unit/test_phase2_failure_and_recovery.py:test_bundle_is_bounded_and_deduplicates_references",
    "P2-RETRY-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_same_candidate_stops_before_duplicate_verification",
    "P2-RETRY-002": "tests/unit/test_phase2_failure_and_recovery.py:test_new_progress_allows_retry_without_resetting_ledger",
    "P2-BUDGET-001": "tests/unit/test_phase2_failure_and_recovery.py:test_exhausted_budget_preserves_policy_and_requests_authority",
    "P2-EXCEPTION-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_scope_exception_preserves_authority_and_impact_fields",
    "P2-EXCEPTION-002": "tests/integration/test_phase2_recovery_vertical_slice.py:test_semantics_and_external_boundaries_do_not_execute_candidate",
    "P2-SAFETY-001": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
    "P2-STATE-001": "tests/integration/test_phase2_recovery_vertical_slice.py:test_restart_resumes_from_recovery_checkpoint",
    "P2-COMPLETION-001": "tests/unit/test_verification_and_completion.py:test_only_work_package_completion_is_published",
    "P2-STRESS-001": "tests/unit/test_phase2_failure_and_recovery.py:test_ten_thousand_duplicate_observations_are_mechanically_bounded",
}


class Phase2AcceptanceCoverageTests(unittest.TestCase):
    def test_every_fixed_scenario_maps_to_an_executable_test(self) -> None:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        scenario_ids = {
            scenario["scenario_id"]
            for scenario in catalog["scenarios"]
        }
        self.assertEqual(scenario_ids, set(SCENARIO_TEST_MAP))
        for target in SCENARIO_TEST_MAP.values():
            relative_path, test_name = target.split(":", 1)
            source = (REPOSITORY_ROOT / relative_path).read_text(
                encoding="utf-8",
            )
            self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
