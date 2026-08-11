import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "docs" / "semantic-specifications" / "ddh-phase-5" / "draft" / "acceptance-scenarios.json"

SCENARIO_TEST_MAP = {
    "P5-ENV-001": ("tests/unit/test_phase5_operational.py", "test_release_profiles_and_unsupported_filesystems_fail_closed"),
    "P5-ENV-002": ("tests/unit/test_phase5_operational.py", "test_profile_identity_changes_with_environment_facts"),
    "P5-ENV-003": ("tests/unit/test_phase5_operational.py", "test_release_profiles_and_unsupported_filesystems_fail_closed"),
    "P5-ENV-004": ("tests/unit/test_phase5_operational.py", "test_profile_identity_changes_with_environment_facts"),
    "P5-TIME-001": ("tests/unit/test_phase5_operational.py", "test_adaptive_timeout_keeps_business_threshold_separate"),
    "P5-TIME-002": ("tests/unit/test_phase5_operational.py", "test_unknown_duration_and_no_progress_rules"),
    "P5-TIME-003": ("tests/unit/test_phase5_operational.py", "test_unknown_duration_and_no_progress_rules"),
    "P5-TIME-004": ("tests/unit/test_phase5_operational.py", "test_unknown_duration_and_no_progress_rules"),
    "P5-TIME-005": ("tests/unit/test_phase5_operational.py", "test_over_budget_plan_does_not_start_and_exact_retry_is_rejected"),
    "P5-TIME-006": ("tests/unit/test_phase5_operational.py", "test_over_budget_plan_does_not_start_and_exact_retry_is_rejected"),
    "P5-PROC-001": ("tests/unit/test_phase5_operational.py", "test_output_is_bounded_and_repeats_aggregated"),
    "P5-PROC-002": ("tests/unit/test_verification_and_completion.py", "test_timeout_terminates_child_process_tree"),
    "P5-PROC-003": ("tests/unit/test_phase5_operational.py", "test_owned_temp_root_is_removed_but_uncertain_root_is_quarantined"),
    "P5-PROC-004": ("tests/unit/test_phase5_operational.py", "test_owned_temp_root_is_removed_but_uncertain_root_is_quarantined"),
    "P5-CAP-001": ("tests/unit/test_phase5_operational.py", "test_capability_uses_only_approved_equivalent_fallback"),
    "P5-CAP-002": ("tests/unit/test_phase5_operational.py", "test_capability_uses_only_approved_equivalent_fallback"),
    "P5-ASSET-001": ("tests/unit/test_phase5_operational.py", "test_managed_asset_preview_atomic_apply_conflict_and_idempotency"),
    "P5-ASSET-002": ("tests/unit/test_phase5_operational.py", "test_managed_asset_preview_atomic_apply_conflict_and_idempotency"),
    "P5-ASSET-003": ("tests/unit/test_phase5_operational.py", "test_managed_asset_preview_atomic_apply_conflict_and_idempotency"),
    "P5-ASSET-004": ("tests/unit/test_phase5_operational.py", "test_managed_asset_preview_atomic_apply_conflict_and_idempotency"),
    "P5-MAP-001": ("tests/unit/test_phase5_operational.py", "test_branch_consumer_binds_all_identities_and_consumed_facts"),
    "P5-MAP-002": ("tests/unit/test_phase5_operational.py", "test_branch_binding_invalidates_same_branch_new_commit"),
    "P5-MAP-003": ("tests/unit/test_phase5_operational.py", "test_branch_consumer_binds_all_identities_and_consumed_facts"),
    "P5-TEL-001": ("tests/unit/test_phase5_operational.py", "test_operational_telemetry_is_never_authority_or_completion"),
    "P5-TEL-002": ("tests/unit/test_phase5_operational.py", "test_bounded_telemetry_rejects_nested_sensitive_fields"),
    "P5-TEL-003": ("tests/unit/test_phase5_operational.py", "test_operational_telemetry_is_never_authority_or_completion"),
}


class Phase5AcceptanceCoverageTests(unittest.TestCase):
    def test_every_phase5_scenario_maps_to_an_executable_test(self) -> None:
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        ids = {item["scenario_id"] for item in catalog["scenarios"]}
        self.assertEqual(ids, set(SCENARIO_TEST_MAP))
        for relative, test_name in SCENARIO_TEST_MAP.values():
            with self.subTest(test_name=test_name):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
