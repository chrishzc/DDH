import tempfile
import unittest
from pathlib import Path

from ddh.contracts import ContractError
from ddh.operational import (
    BoundedOperationalTelemetry, BranchBoundMapConsumer, BranchMapBinding,
    BranchMapSubject, Capability, CapabilityHealthRegistry, EnvironmentObservation, EnvironmentProfile,
    ExecutionEstimate, ExecutionPlanner, ManagedAssetController,
    OperationalTelemetrySummary, OutputDrainLimiter, OwnedTemporaryRoot,
    bind_environment,
)
from ddh.system_map import MapResult, StaticSystemMapAdapter


def environment(**changes):
    values = dict(
        profile_id="env", support_tier="release_blocking", os_name="windows_11",
        architecture="x86_64", runtime_versions=("3.13",), tool_versions=(("python", "3.13"),),
        dependency_digest="sha256:deps", cwd="workspace", locale="C", timezone="UTC",
        encoding="utf-8", environment_allowlist=("PATH",), isolation_profile="standard",
        network_capability=False, database_capability=False, filesystem_profile="ntfs",
    )
    values.update(changes)
    return EnvironmentProfile(**values)


class Phase5OperationalTests(unittest.TestCase):
    def test_release_profiles_and_unsupported_filesystems_fail_closed(self):
        self.assertEqual("release_blocking", environment().support_tier)
        self.assertEqual("release_blocking", environment(os_name="ubuntu_24_04", filesystem_profile="ext4").support_tier)
        with self.assertRaisesRegex(ContractError, "release_blocking_platform_invalid"):
            environment(os_name="macos")
        with self.assertRaisesRegex(ContractError, "filesystem_profile_unsupported"):
            environment(isolation_profile="high_assurance", filesystem_profile="unc")

    def test_profile_identity_changes_with_environment_facts(self):
        self.assertNotEqual(environment().digest, environment(timezone="Asia/Taipei").digest)
        profile = environment()
        observation = EnvironmentObservation(
            profile.os_name, profile.architecture, profile.runtime_versions,
            profile.tool_versions, profile.dependency_digest, profile.cwd,
            profile.locale, profile.timezone, profile.encoding, profile.filesystem_profile,
        )
        self.assertTrue(bind_environment(profile, observation).bound)
        self.assertFalse(bind_environment(profile, replace_observation(observation, timezone="Asia/Taipei")).bound)

    def test_adaptive_timeout_keeps_business_threshold_separate(self):
        plan = ExecutionPlanner().build(environment(), ExecutionEstimate(declared_seconds=60), 300, "latency<1s")
        self.assertEqual(150, plan.execution_deadline_seconds)
        self.assertEqual("latency<1s", plan.business_threshold)
        self.assertEqual("execution_plan_ready", plan.reason_code)

    def test_unknown_duration_and_no_progress_rules(self):
        planner = ExecutionPlanner()
        silent = planner.build(environment(), ExecutionEstimate(), 700, "none")
        instrumented = planner.build(environment(), ExecutionEstimate(expected_progress_interval_seconds=30), 700, "none")
        self.assertEqual(600, silent.execution_deadline_seconds)
        self.assertIsNone(silent.no_progress_deadline_seconds)
        self.assertEqual(120, instrumented.no_progress_deadline_seconds)

    def test_over_budget_plan_does_not_start_and_exact_retry_is_rejected(self):
        planner = ExecutionPlanner()
        plan = planner.build(environment(), ExecutionEstimate(declared_seconds=60), 100, "fixed")
        self.assertEqual("verification_plan_not_ready", plan.reason_code)
        self.assertFalse(planner.retry_allowed(plan, plan))

    def test_output_is_bounded_and_repeats_aggregated(self):
        profile = environment(output_byte_limit=8, output_line_limit=2, output_event_limit=3)
        result = OutputDrainLimiter().consume(("same", "same", "overflow"), profile)
        self.assertTrue(result.truncated)
        self.assertEqual(1, len(result.repeated_fingerprints))

    def test_owned_temp_root_is_removed_but_uncertain_root_is_quarantined(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            owned = base / "owned"
            adapter = OwnedTemporaryRoot()
            adapter.mark(owned, "identity")
            (owned / "data").write_text("x")
            self.assertEqual("removed", adapter.cleanup(owned, "identity").outcome)
            uncertain = base / "uncertain"
            uncertain.mkdir()
            self.assertEqual("temporary_root_quarantined", adapter.cleanup(uncertain, "identity").outcome)

    def test_capability_uses_only_approved_equivalent_fallback(self):
        registry = CapabilityHealthRegistry((
            Capability("primary", "runner", "degraded"),
            Capability("fallback", "runner", "available", True),
            Capability("wrong", "other", "available", True),
        ))
        self.assertEqual(("fallback", "approved_fallback_selected"), registry.select("primary"))
        self.assertEqual((None, "capability_unavailable"), registry.select("missing"))

    def test_managed_asset_preview_atomic_apply_conflict_and_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "asset.txt"
            controller = ManagedAssetController()
            preview = controller.preview(target, b"expected", None)
            self.assertEqual("applied_with_parity", controller.apply(preview, b"expected"))
            current = controller.preview(target, b"expected", preview.expected_digest)
            self.assertFalse(current.delta)
            self.assertEqual("already_current", controller.apply(current, b"expected"))
            target.write_bytes(b"user")
            conflict = controller.preview(target, b"new", preview.expected_digest)
            self.assertEqual("managed_asset_user_change_conflict", conflict.outcome)

    def test_branch_binding_invalidates_same_branch_new_commit(self):
        first = BranchMapBinding("repo", "main", "a", "wt", "candidate", "view", ("node:n",))
        second = BranchMapBinding("repo", "main", "b", "wt", "candidate", "view", ("node:n",))
        self.assertFalse(first.compatible_with(second))

    def test_branch_consumer_binds_all_identities_and_consumed_facts(self):
        subject = BranchMapSubject("repo", "main", "commit", "worktree", "candidate")
        adapter = StaticSystemMapAdapter(MapResult("usable_actual", "repo", "main", "commit", "view", ("node",), (), ()))
        binding = BranchBoundMapConsumer().consume(subject, adapter, "impact")
        self.assertEqual("worktree", binding.worktree_id)
        self.assertEqual(("node:node",), binding.consumed_facts)
        self.assertEqual(1, len(adapter.queries))

    def test_operational_telemetry_is_never_authority_or_completion(self):
        summary = OperationalTelemetrySummary("runner_health", (("ok", 1),))
        self.assertFalse(summary.authoritative)
        self.assertFalse(summary.retained_raw_logs)
        self.assertFalse(summary.completion_input)

    def test_bounded_telemetry_rejects_nested_sensitive_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.json"
            telemetry = BoundedOperationalTelemetry(path, max_events=2, max_total_bytes=256)
            telemetry.emit("one", {"status": "ok"})
            telemetry.emit("two", {"status": "ok"})
            summary = telemetry.emit("three", {"status": "ok"})
            self.assertEqual(2, sum(count for _, count in summary.counts))
            with self.assertRaisesRegex(ContractError, "sensitive_field"):
                telemetry.emit("bad", {"nested": {"stdout": "raw"}})


def replace_observation(value: EnvironmentObservation, **changes) -> EnvironmentObservation:
    fields = dict(value.__dict__)
    fields.update(changes)
    return EnvironmentObservation(**fields)


if __name__ == "__main__":
    unittest.main()
