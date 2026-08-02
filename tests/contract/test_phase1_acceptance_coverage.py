import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "semantic-specifications"
    / "ddh-phase-1"
    / "draft"
    / "acceptance-scenarios.json"
)

SCENARIO_TEST_MAP = {
    "P1-AUTH-001": "tests/unit/test_contracts_and_specification.py:test_missing_expected_behavior_rejects_before_work",
    "P1-FLOW-001": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
    "P1-MAP-001": "tests/unit/test_paths_context_and_map.py:test_map_facts_are_consumed",
    "P1-MAP-002": "tests/unit/test_paths_context_and_map.py:test_partial_map_uses_bounded_fallback",
    "P1-CONTEXT-001": "tests/unit/test_paths_context_and_map.py:test_ten_thousand_unrelated_records_are_not_ingested",
    "P1-CONTEXT-002": "tests/unit/test_paths_context_and_map.py:test_irrelevant_and_duplicate_content_requests_are_denied",
    "P1-AGENT-001": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
    "P1-GUARD-001": "tests/unit/test_candidate_and_auditor.py:test_materialization_preserves_original_and_excludes_git",
    "P1-GUARD-002": "tests/unit/test_candidate_and_auditor.py:test_mixed_change_is_rejected_as_one_unit",
    "P1-IMPACT-001": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
    "P1-IMPACT-002": "tests/integration/test_phase1_vertical_slice.py:test_required_read_only_change_produces_revision_report",
    "P1-TEST-001": "tests/unit/test_candidate_and_auditor.py:test_all_mechanical_weakening_dimensions_are_rejected",
    "P1-TEST-002": "tests/unit/test_candidate_and_auditor.py:test_repaired_asset_requires_an_executed_known_bad_probe",
    "P1-RUNNER-001": "tests/unit/test_verification_and_completion.py:test_sixty_second_estimate_is_not_given_thirty_second_deadline",
    "P1-RUNNER-002": "tests/unit/test_verification_and_completion.py:test_timeout_terminates_child_process_tree",
    "P1-RUNNER-003": "tests/unit/test_verification_and_completion.py:test_output_is_bounded",
    "P1-CANDIDATE-001": "tests/unit/test_agent_result_stress.py:test_ten_thousand_stale_duplicate_and_late_results_are_bounded",
    "P1-RECOVERY-001": "tests/unit/test_state_recovery_and_telemetry.py:test_identical_failure_without_evidence_is_no_progress",
    "P1-RECOVERY-002": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
    "P1-PORTABILITY-001": "tests/contract/test_ci_profile_contract.py:test_required_and_latest_profiles_are_declared",
    "P1-FIXTURE-001": "tests/fixtures/portable_workspace/workspace/tests/acceptance/test_workspace.py:test_symlink_escape_is_rejected",
    "P1-ADAPTER-001": "tests/unit/test_verification_and_completion.py:test_fixed_command_rejects_generic_shell",
    "P1-COMPLETION-001": "tests/unit/test_verification_and_completion.py:test_only_work_package_completion_is_published",
    "P1-BUNDLE-001": "tests/integration/test_phase1_vertical_slice.py:test_repair_retest_completion_and_portable_bundle",
}


class Phase1AcceptanceCoverageTests(unittest.TestCase):
    def test_every_fixed_scenario_maps_to_an_executable_test(self) -> None:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        scenario_ids = {
            scenario["scenario_id"]
            for scenario in catalog["scenarios"]
        }
        self.assertEqual(scenario_ids, set(SCENARIO_TEST_MAP))
        for target in SCENARIO_TEST_MAP.values():
            relative_path, test_name = target.split(":", 1)
            source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
