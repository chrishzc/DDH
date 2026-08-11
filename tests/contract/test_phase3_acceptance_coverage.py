import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPOSITORY_ROOT / "docs" / "semantic-specifications" / "ddh-phase-3" / "draft" / "acceptance-scenarios.json"

UNIT = "tests/unit/test_phase3_coordination.py"
INTEGRATION = "tests/integration/test_phase3_parallel_vertical_slice.py"

SCENARIO_TEST_MAP = {
    "P3-FLOW-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-DECIDE-001": f"{UNIT}:test_parallel_assessment_requires_benefit_and_boundary",
    "P3-DECIDE-002": f"{INTEGRATION}:test_parallel_cost_fallback_continues_through_serial_workers",
    "P3-DECIDE-003": f"{UNIT}:test_parallel_assessment_requires_benefit_and_boundary",
    "P3-DECIDE-004": f"{UNIT}:test_parallel_assessment_requires_benefit_and_boundary",
    "P3-ACTIVATE-001": f"{UNIT}:test_activation_submission_and_targeted_invalidation",
    "P3-ACTIVATE-002": f"{UNIT}:test_guard_rejects_late_or_mixed_scope_write",
    "P3-CONTEXT-001": "tests/unit/test_paths_context_and_map.py:test_context_deduplicates_unchanged_content",
    "P3-CONTEXT-002": "tests/unit/test_paths_context_and_map.py:test_irrelevant_and_duplicate_content_requests_are_denied",
    "P3-TEST-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-TEST-002": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-TEST-003": f"{UNIT}:test_activation_submission_and_targeted_invalidation",
    "P3-SHARED-001": f"{UNIT}:test_cross_lane_request_never_grants_write",
    "P3-SHARED-002": f"{UNIT}:test_cross_lane_request_never_grants_write",
    "P3-SHARED-003": f"{UNIT}:test_cross_lane_request_never_grants_write",
    "P3-SHARED-004": f"{UNIT}:test_activation_submission_and_targeted_invalidation",
    "P3-HANDOFF-001": f"{UNIT}:test_handoff_requires_known_mutation_closure",
    "P3-HANDOFF-002": f"{UNIT}:test_handoff_requires_known_mutation_closure",
    "P3-HANDOFF-003": f"{UNIT}:test_guard_rejects_late_or_mixed_scope_write",
    "P3-ADMIT-001": f"{UNIT}:test_central_admission_rejects_mixed_patch_as_whole",
    "P3-ADMIT-002": f"{UNIT}:test_central_admission_rejects_mixed_patch_as_whole",
    "P3-ADMIT-003": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-ADMIT-004": f"{UNIT}:test_central_admission_rejects_mixed_patch_as_whole",
    "P3-JOIN-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-JOIN-002": f"{UNIT}:test_join_requires_every_writer_to_quiesce",
    "P3-JOIN-003": f"{UNIT}:test_join_requires_every_writer_to_quiesce",
    "P3-JOIN-004": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-VERIFY-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-VERIFY-002": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-MAP-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-MAP-002": "tests/unit/test_paths_context_and_map.py:test_unmapped_actual_change_uses_live_impact_fallback",
    "P3-MAP-003": "tests/unit/test_paths_context_and_map.py:test_partial_map_uses_bounded_fallback",
    "P3-MAP-004": "tests/unit/test_paths_context_and_map.py:test_map_facts_are_consumed",
    "P3-COMPLETE-001": f"{INTEGRATION}:test_three_modules_construct_product_and_tests_asynchronously_then_join",
    "P3-COMPLETE-002": "tests/unit/test_verification_and_completion.py:test_only_work_package_completion_is_published",
    "P3-RECOVER-001": f"{INTEGRATION}:test_parallel_cost_fallback_continues_through_serial_workers",
    "P3-RECOVER-002": "tests/unit/test_state_recovery_and_telemetry.py:test_restart_loads_current_atomic_state",
    "P3-RECOVER-003": "tests/integration/test_phase2_recovery_vertical_slice.py:test_scope_exception_preserves_authority_and_impact_fields",
    "P3-RECOVER-004": "tests/integration/test_phase2_recovery_vertical_slice.py:test_semantics_and_external_boundaries_do_not_execute_candidate",
    "P3-STRESS-001": "tests/unit/test_agent_result_stress.py:test_ten_thousand_stale_duplicate_and_late_results_are_bounded",
    "P3-STRESS-002": f"{UNIT}:test_activation_submission_and_targeted_invalidation",
    "P3-STRESS-003": f"{INTEGRATION}:test_parallel_cost_fallback_continues_through_serial_workers",
    "P3-STRESS-004": "tests/unit/test_candidate_and_auditor.py:test_materialization_preserves_original_and_excludes_git",
}


class Phase3AcceptanceCoverageTests(unittest.TestCase):
    def test_every_fixed_scenario_maps_to_an_executable_test(self) -> None:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        scenario_ids = {item["scenario_id"] for item in catalog["scenarios"]}
        self.assertEqual(scenario_ids, set(SCENARIO_TEST_MAP))
        for target in SCENARIO_TEST_MAP.values():
            relative_path, test_name = target.split(":", 1)
            source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
