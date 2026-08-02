import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ddh.agent_driver import AgentResult, WorkRequest
from ddh.confirmation import (
    authority_for_document,
    create_confirmation,
    expected_confirmation_phrase,
)
from ddh.context import ContextRequest
from ddh.contracts import CandidateReference
from ddh.recovery import RecoveryPolicy
from ddh.runtime import Phase2Runtime, RuntimeRequest
from ddh.system_map import (
    ImpactResolver,
    StaticLiveSourceAdapter,
    StaticSystemMapAdapter,
)
from ddh.telemetry import JsonlTelemetry
from ddh.test_auditor import (
    TestRepairEvidence as DdhTestRepairEvidence,
    TestRepairProposal as DdhTestRepairProposal,
)
from ddh.verification import (
    VerificationBackend,
    VerificationBackendRegistry,
    VerificationResult,
)
from tests.integration.test_phase1_vertical_slice import (
    COMPLETE_REPAIR,
    FIXTURE_ROOT,
    FixtureContextSource,
    PARTIAL_REPAIR,
    WorkspaceAssetProvider,
    live_map,
    workload_document,
)


class FailureAwareRepairAgent:
    def __init__(self) -> None:
        self.calls = 0
        self.received_failure_bundle = None

    def pull(self, request: WorkRequest) -> AgentResult:
        self.calls += 1
        if self.calls == 1:
            repair = PARTIAL_REPAIR
        else:
            self.received_failure_bundle = request.failure_bundle
            repair = COMPLETE_REPAIR
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": repair},
        )


class CompleteRepairAgent:
    def pull(self, request: WorkRequest) -> AgentResult:
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": COMPLETE_REPAIR},
        )


class NoProgressAgent:
    def __init__(self) -> None:
        self.calls = 0

    def pull(self, request: WorkRequest) -> AgentResult:
        self.calls += 1
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": PARTIAL_REPAIR},
        )


class InterruptingAgent:
    def __init__(self) -> None:
        self.calls = 0

    def pull(self, request: WorkRequest) -> AgentResult:
        self.calls += 1
        if self.calls == 1:
            return AgentResult(
                request.invocation_id,
                request.specification,
                request.candidate_generation,
                "context_request",
                {},
                context_request=ContextRequest(
                    "src/manifest_loader.py",
                    "impact",
                    "required reverse dependent",
                    5,
                    20,
                ),
            )
        if self.calls > 2:
            raise KeyboardInterrupt("synthetic process interruption")
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": PARTIAL_REPAIR},
        )


class CapturingCompleteAgent(CompleteRepairAgent):
    def __init__(self) -> None:
        self.request = None

    def pull(self, request: WorkRequest) -> AgentResult:
        self.request = request
        return super().pull(request)


class BoundaryAgent:
    def __init__(self, result_type: str) -> None:
        self.result_type = result_type

    def pull(self, request: WorkRequest) -> AgentResult:
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            self.result_type,
            {},
        )


class ScopeBoundaryAgent:
    def pull(self, request: WorkRequest) -> AgentResult:
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "scope_change_required",
            {"src/manifest_loader.py": "required reverse-dependent repair"},
        )


class PassingExecutor:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, plan) -> VerificationResult:
        self.calls += 1
        return VerificationResult(
            plan.plan_id,
            plan.candidate,
            plan.asset_digest,
            "succeeded",
            "passed",
            "complete",
            "verification_passed",
            False,
            0,
            1,
            "",
            "",
            False,
        )


class ImpactAwareAssetProvider:
    def __init__(self) -> None:
        self.impacts = []
        self.delegate = WorkspaceAssetProvider()

    def build_for_impact(self, candidate, impact):
        self.impacts.append(impact)
        primary = self.delegate.build(candidate)
        _, primary_asset = primary[0]
        regression = replace(
            primary_asset,
            asset_id="manifest-loader-regression",
            scenario_ids=("MANIFEST-REGRESSION-001",),
            assertions=("manifest loader consumes canonical paths",),
        )
        return primary + ((regression, regression),)


class StaleThenCurrentAssetProvider:
    def __init__(self) -> None:
        self.calls = 0
        self.delegate = WorkspaceAssetProvider()

    def build(self, candidate):
        self.calls += 1
        proposals = self.delegate.build(candidate)
        if self.calls > 1:
            return proposals
        baseline, proposed = proposals[0]
        stale = replace(
            proposed,
            candidate=CandidateReference("stale", 0, "sha256:stale"),
        )
        return ((baseline, stale),)


class RepairingTestPort:
    def __init__(self) -> None:
        self.calls = 0

    def repair(self, request):
        self.calls += 1
        known_bad = "known_bad_helper_invocation"
        repaired = replace(
            request.rejected_asset,
            cases=request.rejected_asset.cases + (known_bad,),
            fixture_case_count=request.rejected_asset.fixture_case_count + 1,
            known_bad_probes=(known_bad,),
        )
        return DdhTestRepairProposal(
            repaired,
            "test-repair-proposer",
        )


class MechanicalTestProbe:
    def __init__(self) -> None:
        self.calls = 0

    def verify(self, asset, original_scenarios):
        self.calls += 1
        return DdhTestRepairEvidence(
            asset.digest,
            original_scenarios,
            asset.known_bad_probes,
            True,
            True,
            "mechanical-probe-runner",
        )


class RepairableAssetProvider:
    def build(self, candidate):
        baseline, current = WorkspaceAssetProvider().build(candidate)[0]
        baseline = current
        broken_helper = replace(
            current,
            assertions=current.assertions + ("helper invokes scenario",),
        )
        return ((baseline, broken_helper),)


def confirmed_request(invocation_root: Path, invocation_id: str) -> RuntimeRequest:
    document = workload_document()
    authority = authority_for_document(document)
    confirmation = create_confirmation(
        document,
        expected_confirmation_phrase(authority),
        "trusted_host_ui",
    )
    return RuntimeRequest(
        document,
        confirmation,
        FIXTURE_ROOT,
        invocation_root,
        "portable-workspace",
        "main",
        "fixture-commit-001",
        invocation_id,
    )


def resolver() -> ImpactResolver:
    result = live_map()
    return ImpactResolver(
        StaticSystemMapAdapter(result),
        StaticLiveSourceAdapter(result),
    )


class Phase2RecoveryVerticalSliceTests(unittest.TestCase):
    def test_product_failure_bundle_drives_repair_to_completion(self) -> None:
        original = (FIXTURE_ROOT / "src" / "path_normalizer.py").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = FailureAwareRepairAgent()
            map_adapter = StaticSystemMapAdapter(live_map())
            runtime = Phase2Runtime(
                ImpactResolver(
                    map_adapter,
                    StaticLiveSourceAdapter(live_map()),
                ),
                agent,
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-product-repair"),
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(2, agent.calls)
            self.assertEqual(
                "product_failed",
                agent.received_failure_bundle.failure_class,
            )
            self.assertIn(
                "repair_product_in_scope",
                agent.received_failure_bundle.allowed_machine_actions,
            )
            self.assertLessEqual(
                agent.received_failure_bundle.encoded_size,
                32_768,
            )
            self.assertEqual(
                1,
                agent.received_failure_bundle.progress.candidate_generation,
            )
            self.assertTrue(
                agent.received_failure_bundle.consumed_architecture_facts,
            )
            self.assertIn(
                ("agent_attempts", 2),
                agent.received_failure_bundle.remaining_budgets,
            )
            self.assertTrue(
                map_adapter.queries[-1].purpose.startswith(
                    "failed_scenario_reconciliation:",
                )
            )
        self.assertEqual(
            original,
            (FIXTURE_ROOT / "src" / "path_normalizer.py").read_bytes(),
        )

    def test_same_candidate_stops_before_duplicate_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = NoProgressAgent()
            runtime = Phase2Runtime(
                resolver(),
                agent,
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-no-progress"),
            )
            self.assertEqual("no_progress", outcome.completion.reason_code)
            self.assertEqual(2, agent.calls)
            self.assertIsNotNone(outcome.failure_bundle)

    def test_restart_resumes_from_recovery_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = confirmed_request(root, "phase2-restart")
            first_runtime = Phase2Runtime(
                resolver(),
                InterruptingAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
                FixtureContextSource(),
            )
            with self.assertRaises(KeyboardInterrupt):
                first_runtime.execute(request)
            state = json.loads(
                (root / "state" / "phase2-restart.json").read_text(
                    encoding="utf-8",
                )
            )
            self.assertEqual(
                "recovery_pending",
                state["payload"]["stage"],
            )
            resumed_agent = CapturingCompleteAgent()
            resumed_runtime = Phase2Runtime(
                resolver(),
                resumed_agent,
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = resumed_runtime.execute(request)
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(2, resumed_agent.request.candidate_generation)
            self.assertEqual(
                "product_failed",
                resumed_agent.request.failure_bundle.failure_class,
            )
            self.assertEqual(1, resumed_agent.request.context.generation)
            self.assertIn(
                "src/manifest_loader.py",
                {
                    item.selector
                    for item in resumed_agent.request.context.items
                },
            )

    def test_semantics_and_external_boundaries_do_not_execute_candidate(
        self,
    ) -> None:
        cases = (
            ("test_semantics_uncertain", "specification_gap"),
            (
                "external_side_effect_uncertain",
                "external_high_risk_flow_required",
            ),
        )
        for result_type, expected_reason in cases:
            with self.subTest(result_type=result_type):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    runtime = Phase2Runtime(
                        resolver(),
                        BoundaryAgent(result_type),
                        WorkspaceAssetProvider(),
                        JsonlTelemetry(root / "events.jsonl"),
                    )
                    outcome = runtime.execute(
                        confirmed_request(root, f"phase2-{result_type}"),
                    )
                    self.assertEqual(
                        expected_reason,
                        outcome.completion.reason_code,
                    )
                    self.assertIsNone(outcome.candidate)
                    self.assertIsNotNone(outcome.exception_report)

    def test_scope_exception_preserves_authority_and_impact_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = Phase2Runtime(
                resolver(),
                ScopeBoundaryAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-scope-boundary"),
            )
            report = outcome.exception_report
            self.assertEqual(
                "scope_expansion_required",
                outcome.completion.reason_code,
            )
            self.assertEqual("L1", report.current_authority_class)
            self.assertEqual("L3", report.requested_authority_class)
            self.assertEqual(
                ("src/manifest_loader.py",),
                report.requested_paths,
            )
            self.assertEqual("write_scope", report.requested_authority_change)
            self.assertTrue(report.failure_bundle_id)

    def test_approved_equivalent_backend_continues_without_human(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fallback = PassingExecutor()
            registry = VerificationBackendRegistry(
                (
                    VerificationBackend(
                        "unavailable",
                        "python",
                        "unhealthy",
                        object(),
                    ),
                    VerificationBackend(
                        "approved-fallback",
                        "python",
                        "ready",
                        fallback,
                    ),
                ),
                "unavailable",
            )
            runtime = Phase2Runtime(
                resolver(),
                CompleteRepairAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
                backend_registry=registry,
                recovery_policy=RecoveryPolicy(
                    approved_backends=("approved-fallback",),
                ),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-runner-fallback"),
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(1, fallback.calls)
            self.assertIsNone(outcome.exception_report)

    def test_unapproved_backend_exhaustion_is_platform_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = VerificationBackendRegistry(
                (
                    VerificationBackend(
                        "unavailable",
                        "python",
                        "unhealthy",
                        object(),
                    ),
                ),
                "unavailable",
            )
            runtime = Phase2Runtime(
                resolver(),
                CompleteRepairAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
                backend_registry=registry,
                recovery_policy=RecoveryPolicy(approved_backends=()),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-platform-blocked"),
            )
            self.assertEqual(
                "platform_blocked",
                outcome.completion.reason_code,
            )
            self.assertIsNotNone(outcome.exception_report)
            self.assertIn(
                "preserve_and_report",
                outcome.failure_bundle.attempted_routes,
            )
            self.assertTrue(
                outcome.failure_bundle.consumed_architecture_facts,
            )

    def test_actual_impact_selects_verification_without_expanding_write_scope(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            impact_provider = ImpactAwareAssetProvider()
            runtime = Phase2Runtime(
                resolver(),
                CompleteRepairAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
                impact_asset_provider=impact_provider,
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-impact-expansion"),
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertIn(
                "PortableWorkspace/ManifestLoader",
                impact_provider.impacts[-1].nodes,
            )
            self.assertEqual(
                ("src/path_normalizer.py",),
                outcome.candidate.changes.changed_paths,
            )
            self.assertEqual(2, len(outcome.results))

    def test_stale_asset_is_rebuilt_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            provider = StaleThenCurrentAssetProvider()
            runtime = Phase2Runtime(
                resolver(),
                CompleteRepairAgent(),
                provider,
                JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-stale-asset"),
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(2, provider.calls)

    def test_test_helper_repair_requires_separate_proposal_and_admission(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            test_repair = RepairingTestPort()
            test_probe = MechanicalTestProbe()
            runtime = Phase2Runtime(
                resolver(),
                CompleteRepairAgent(),
                RepairableAssetProvider(),
                JsonlTelemetry(root / "events.jsonl"),
                test_repair_port=test_repair,
                test_repair_probe_port=test_probe,
            )
            outcome = runtime.execute(
                confirmed_request(root, "phase2-test-repair"),
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(1, test_repair.calls)
            self.assertEqual(1, test_probe.calls)


if __name__ == "__main__":
    unittest.main()
