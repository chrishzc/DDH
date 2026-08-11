from dataclasses import replace
import unittest

from ddh.contracts import CandidateReference, ContractError
from ddh.verification_assets import (
    AssetRecord, CurrentnessEvaluator, ExecutionResult, ImpactEvidence,
    MechanicalVerificationExecutor, QualityAddOn, SpecificationNotReady,
    VerificationAssetAuditor, VerificationAssetCatalog, VerificationAssetManifest,
    evidence_retention, optimize_fixed_suite,
)


CANDIDATE = CandidateReference("candidate", 1, "sha256:source")


def manifest(**changes):
    value = VerificationAssetManifest(
        "asset", "1.0.0", "test", "pytest", "Module", ("node",),
        ("REQ-1",), ("SCN-1",), ("SPEC@1",), "PROFILE@1",
        (("source", CANDIDATE.digest), ("fixture", "fixture@1"), ("toolchain", "python@3.13")),
        ("tests/test_asset.py",), "env@1", "exact equality", "passed",
        ("assertion-a",), ("expected-a",), (("minimum", "2"),), 2,
        ("case-a", "known-bad"), (), (QualityAddOn("Performance", "not_applicable_with_business_reason", "no SLO"),),
    )
    return replace(value, **changes)


class Phase4VerificationAssetTests(unittest.TestCase):
    def test_catalog_is_rebuildable_and_tool_neutral(self):
        pytest_asset = manifest()
        command_asset = manifest(asset_id="compile", tool_adapter="fixed_command", asset_kind="compile")
        catalog = VerificationAssetCatalog.rebuild((command_asset, pytest_asset))
        self.assertEqual(["asset", "compile"], [r.manifest.asset_id for r in catalog.discover("Module")])
        self.assertEqual((), catalog.discover("Module", active_only=True))

    def test_missing_mapping_returns_structured_not_ready(self):
        record = AssetRecord(manifest(scenario_refs=("OTHER",)), "candidate")
        result = VerificationAssetAuditor().admit(record, ("SCN-1",), independent_auditor=True, known_bad_detected=True)
        self.assertIsInstance(result, SpecificationNotReady)
        self.assertFalse(result.automatic_relaxation)

    def test_admission_requires_independent_auditor_and_known_bad_for_repair(self):
        auditor = VerificationAssetAuditor()
        baseline = AssetRecord(manifest(), "admitted")
        with self.assertRaisesRegex(ContractError, "independent_test_auditor_required"):
            auditor.admit(AssetRecord(manifest(), "candidate"), ("SCN-1",), independent_auditor=False, known_bad_detected=True)
        with self.assertRaisesRegex(ContractError, "known_bad_probe_required"):
            auditor.admit(AssetRecord(manifest(assertions=("assertion-a", "assertion-b")), "candidate"), ("SCN-1",), baseline, independent_auditor=True, known_bad_detected=False)

    def test_mechanical_guard_rejects_each_weakening_form(self):
        auditor = VerificationAssetAuditor()
        baseline = AssetRecord(manifest(), "admitted")
        with self.assertRaisesRegex(ContractError, "not_executable"):
            manifest(assertions=())
        weakened = (
            manifest(expected_values=()),
            manifest(thresholds=(("minimum", "1"),)),
            manifest(fixture_case_count=1),
            manifest(cases=("case-a",)),
            manifest(markers=("skip",)),
        )
        for item in weakened:
            with self.subTest(item=item):
                with self.assertRaisesRegex(ContractError, "weakening_rejected"):
                    auditor.admit(AssetRecord(item, "candidate"), ("SCN-1",), baseline, independent_auditor=True, known_bad_detected=True)

    def test_executor_cannot_bypass_admission_or_bindings(self):
        executor = MechanicalVerificationExecutor()
        record = AssetRecord(manifest(), "candidate")
        invoked = []
        result = executor.execute(record, CANDIDATE, "env@1", lambda argv: invoked.append(argv))
        self.assertEqual("manifest_not_yet_admitted", result.reason_code)
        self.assertEqual([], invoked)
        admitted = VerificationAssetAuditor().admit(record, ("SCN-1",), independent_auditor=True, known_bad_detected=True)
        assert isinstance(admitted, AssetRecord)
        wrong_env = executor.execute(admitted, CANDIDATE, "env@other", lambda argv: None)
        self.assertEqual("environment_binding_mismatch", wrong_env.reason_code)

    def test_executor_uses_fixed_entrypoint_and_unavailable_is_not_pass(self):
        record = VerificationAssetAuditor().admit(AssetRecord(manifest(), "candidate"), ("SCN-1",), independent_auditor=True, known_bad_detected=True)
        assert isinstance(record, AssetRecord)
        result = MechanicalVerificationExecutor().execute(
            record, CANDIDATE, "env@1",
            lambda argv: ExecutionResult(record.manifest.identity, "unavailable", "tool_unavailable"),
        )
        self.assertEqual("unavailable", result.outcome)

    def test_currentness_is_minimal_and_source_only_requires_rerun(self):
        record = AssetRecord(manifest(), "admitted")
        evaluator = CurrentnessEvaluator()
        unaffected = evaluator.reevaluate(record, ImpactEvidence((("schema", "other"),), ("node:n",)))
        self.assertEqual("current", unaffected.validity)
        source = evaluator.reevaluate(record, ImpactEvidence((("source", CANDIDATE.digest),), ("node:n",)))
        self.assertEqual("rerun_required", source.validity)
        fixture = evaluator.reevaluate(record, ImpactEvidence((("fixture", "fixture@1"),), (), True))
        self.assertEqual("stale", fixture.validity)

    def test_map_consumption_and_live_fallback_are_required(self):
        with self.assertRaisesRegex(ContractError, "facts_not_consumed"):
            ImpactEvidence((("source", CANDIDATE.digest),), ())
        self.assertTrue(ImpactEvidence((), (), True).used_live_source_fallback)

    def test_cost_optimization_retains_every_required_asset_and_evidence_is_bounded(self):
        first = AssetRecord(manifest(asset_id="b"), "admitted")
        second = AssetRecord(manifest(asset_id="a"), "admitted")
        selected = optimize_fixed_suite((first, second), order="cost_aware", shards=2, cache_enabled=True, parallelism=2)
        self.assertEqual({"a", "b"}, {item.manifest.asset_id for item in selected})
        retained = evidence_retention(first)
        self.assertFalse(retained["retained_raw_logs"])
        self.assertFalse(retained["retained_pass_receipts"])
        self.assertFalse(retained["retained_attempt_ledger"])

    def test_quality_na_requires_business_reason_and_retirement_is_inactive(self):
        with self.assertRaisesRegex(ContractError, "na_reason_required"):
            QualityAddOn("Soak", "not_applicable_with_business_reason")
        retired = CurrentnessEvaluator().retire(AssetRecord(manifest(), "admitted"))
        self.assertFalse(retired.active)


if __name__ == "__main__":
    unittest.main()
