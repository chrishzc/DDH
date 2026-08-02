import unittest

from ddh.contracts import AuthorityReference, CandidateReference, ContractError
from ddh.failure import (
    ExceptionReport,
    FailureBundleBuilder,
    FailureBundleLimits,
    FailureClassifier,
    FailureObservation,
)
from ddh.recovery import (
    AttemptFingerprint,
    ProgressIdentity,
    RecoveryLedger,
    RecoveryPolicy,
    RecoveryRouteRequest,
    RecoveryRouter,
)
from ddh.verification import (
    VerificationBackend,
    VerificationBackendRegistry,
    VerificationResult,
)


AUTHORITY = AuthorityReference("WORKLOAD", "1.0.0", "sha256:spec")
CANDIDATE = CandidateReference("candidate", 2, "sha256:candidate")


def observation(
    failure_class: str,
    *,
    reason_code: str = "failure",
    remaining_budget: int = 3,
    **values,
) -> FailureObservation:
    return FailureObservation(
        failure_class,
        reason_code,
        AUTHORITY,
        "invocation",
        CANDIDATE,
        remaining_budget=remaining_budget,
        external_side_effect_uncertain=(
            failure_class == "external_side_effect_uncertain"
        ),
        **values,
    )


def verification_result(
    *,
    outcome: str = "failed",
    completeness: str = "complete",
    retryable: bool = False,
) -> VerificationResult:
    return VerificationResult(
        "plan",
        CANDIDATE,
        "sha256:asset",
        "failed",
        outcome,
        completeness,
        "verification_failed",
        retryable,
        1,
        10,
        "",
        "",
        False,
    )


def route_request(
    bundle,
    *,
    progress: ProgressIdentity | None = None,
    remaining_budget: int = 3,
    current_backend: str = "",
    available_backends: tuple[str, ...] = (),
) -> RecoveryRouteRequest:
    return RecoveryRouteRequest(
        bundle,
        AttemptFingerprint(
            "sha256:input",
            "sha256:candidate",
            "strategy",
            bundle.reason_code,
        ),
        progress or ProgressIdentity(approved_strategy="strategy"),
        remaining_budget,
        current_backend,
        available_backends,
    )


class FailureBundleTests(unittest.TestCase):
    def test_bundle_is_bounded_and_deduplicates_references(self) -> None:
        repeated = "Traceback: synthetic failure\n" * 1_000_000
        bundle = FailureBundleBuilder().build(
            observation(
                "runner_failed",
                failed_scenario_ids=("S2", "S1", "S2"),
                affected_resources=tuple(f"src/file-{index}.py" for index in range(2000)),
                traceback_location="檔案位置\n" * 10_000,
                stdout=repeated,
                stderr=repeated,
            )
        )
        self.assertLessEqual(bundle.encoded_size, 32_768)
        self.assertEqual(("S1", "S2"), bundle.failed_scenario_ids)
        self.assertTrue(bundle.diagnostics.output_truncated)
        self.assertGreater(bundle.diagnostics.omitted_traceback_bytes, 0)
        self.assertGreater(bundle.omitted_reference_count, 0)

    def test_bundle_redacts_secret_like_diagnostics(self) -> None:
        bundle = FailureBundleBuilder().build(
            observation(
                "runner_failed",
                stdout="Authorization: Bearer exposed-value\nsafe line\n",
                stderr="password=not-for-retention\n",
            )
        )
        diagnostics = bundle.diagnostics
        self.assertNotIn("exposed-value", diagnostics.stdout)
        self.assertNotIn("not-for-retention", diagnostics.stderr)
        self.assertTrue(diagnostics.redacted)

    def test_bundle_rejects_unknown_class_and_external_fact_mismatch(self) -> None:
        builder = FailureBundleBuilder()
        with self.assertRaisesRegex(ContractError, "failure_class_invalid"):
            builder.build(observation("unknown"))
        invalid = FailureObservation(
            "external_side_effect_uncertain",
            "external",
            AUTHORITY,
            "invocation",
        )
        with self.assertRaisesRegex(ContractError, "external_uncertainty_fact_missing"):
            builder.build(invalid)

    def test_total_limit_fails_closed_when_minimum_cannot_fit(self) -> None:
        builder = FailureBundleBuilder(FailureBundleLimits(maximum_total_bytes=8))
        with self.assertRaisesRegex(
            ContractError,
            "failure_bundle_minimum_exceeds_limit",
        ):
            builder.build(observation("product_failed"))

    def test_same_normalized_facts_have_same_bundle_identity(self) -> None:
        first = FailureBundleBuilder().build(
            observation(
                "product_failed",
                affected_nodes=("B", "A", "B"),
            )
        )
        second = FailureBundleBuilder().build(
            observation(
                "product_failed",
                affected_nodes=("A", "B"),
            )
        )
        self.assertEqual(first.bundle_id, second.bundle_id)


class FailureClassifierTests(unittest.TestCase):
    def test_verification_facts_select_exact_failure_class(self) -> None:
        classifier = FailureClassifier()
        failed = verification_result()
        retryable = verification_result(
            outcome="undetermined",
            completeness="incomplete",
            retryable=True,
        )
        cases = (
            ({"candidate_current": False}, "candidate_stale"),
            ({"asset_current": False}, "test_asset_stale"),
            ({"semantics_known": False}, "test_semantics_uncertain"),
            ({"test_implementation_defect": True}, "test_implementation_defect"),
        )
        for arguments, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    expected,
                    classifier.classify_verification(failed, **arguments),
                )
        self.assertEqual(
            "runner_failed",
            classifier.classify_verification(retryable),
        )
        self.assertEqual(
            "product_failed",
            classifier.classify_verification(failed),
        )


class RecoveryRouterTests(unittest.TestCase):
    def test_all_nonhuman_classes_have_fixed_automatic_routes(self) -> None:
        expected_actions = {
            "product_failed": "repair_product_in_scope",
            "test_implementation_defect": "repair_and_readmit_test_asset",
            "context_insufficient": "expand_context",
            "system_map_unavailable": "query_bounded_live_source",
            "candidate_stale": "create_current_candidate_generation",
            "test_asset_stale": "readmit_current_test_asset",
            "impact_underestimated": "expand_verification_closure",
        }
        for failure_class, action in expected_actions.items():
            with self.subTest(failure_class=failure_class):
                bundle = FailureBundleBuilder().build(observation(failure_class))
                route = RecoveryRouter().route(route_request(bundle))
                self.assertTrue(route.may_continue)
                self.assertEqual(action, route.action)
                self.assertFalse(route.requires_human)

    def test_human_boundaries_never_continue_automatically(self) -> None:
        expected_authority = {
            "test_semantics_uncertain": "expected_behavior",
            "scope_expansion_required": "write_scope",
            "external_side_effect_uncertain": "external_operation",
        }
        for failure_class, authority in expected_authority.items():
            with self.subTest(failure_class=failure_class):
                bundle = FailureBundleBuilder().build(observation(failure_class))
                route = RecoveryRouter().route(route_request(bundle))
                self.assertFalse(route.may_continue)
                self.assertTrue(route.requires_human)
                self.assertIn(authority, route.required_authority)

    def test_runner_rebuilds_twice_then_uses_approved_backend(self) -> None:
        bundle = FailureBundleBuilder().build(observation("runner_failed"))
        router = RecoveryRouter(
            RecoveryPolicy(
                transient_action_limit=2,
                equivalent_backend_attempt_limit=1,
                approved_backends=("local", "fallback"),
            )
        )
        routes = [
            router.route(
                route_request(
                    bundle,
                    progress=ProgressIdentity(
                        environment_generation=generation,
                        approved_strategy="runner_recovery",
                    ),
                    current_backend="local",
                    available_backends=("fallback",),
                )
            )
            for generation in range(3)
        ]
        self.assertEqual(
            [
                "rebuild_runner_environment",
                "rebuild_runner_environment",
                "select_approved_backend",
            ],
            [route.action for route in routes],
        )
        self.assertEqual("fallback", routes[-1].selected_backend)

    def test_backend_fallback_is_allowlisted_and_exhaustion_is_platform_blocked(
        self,
    ) -> None:
        bundle = FailureBundleBuilder().build(
            observation("tool_backend_unavailable")
        )
        router = RecoveryRouter(
            RecoveryPolicy(approved_backends=("approved",))
        )
        denied = router.route(
            route_request(
                bundle,
                current_backend="local",
                available_backends=("unapproved",),
            )
        )
        self.assertEqual("platform_blocked", denied.reason_code)
        self.assertTrue(denied.requires_human)

    def test_identical_attempt_is_no_progress_before_execution(self) -> None:
        bundle = FailureBundleBuilder().build(observation("product_failed"))
        router = RecoveryRouter()
        request = route_request(bundle)
        first = router.route(request)
        second = router.route(request)
        self.assertTrue(first.may_continue)
        self.assertEqual("no_progress", second.reason_code)
        self.assertFalse(second.may_continue)
        self.assertEqual(1, len(router.ledger.attempted_routes))

    def test_new_progress_allows_retry_without_resetting_ledger(self) -> None:
        bundle = FailureBundleBuilder().build(observation("product_failed"))
        router = RecoveryRouter()
        first = route_request(
            bundle,
            progress=ProgressIdentity(
                candidate_generation=1,
                approved_strategy="repair",
            ),
        )
        second = route_request(
            bundle,
            progress=ProgressIdentity(
                candidate_generation=2,
                approved_strategy="repair",
            ),
        )
        self.assertTrue(router.route(first).may_continue)
        self.assertTrue(router.route(second).may_continue)
        self.assertEqual(2, len(router.ledger.seen_attempts))

    def test_exhausted_budget_preserves_policy_and_requests_authority(self) -> None:
        bundle = FailureBundleBuilder().build(observation("runner_failed"))
        route = RecoveryRouter().route(
            route_request(bundle, remaining_budget=0)
        )
        self.assertEqual("recovery_budget_exhausted", route.reason_code)
        self.assertFalse(route.may_continue)
        self.assertIn("budget_increase", route.required_authority)

    def test_ledger_snapshot_restores_idempotency(self) -> None:
        bundle = FailureBundleBuilder().build(observation("product_failed"))
        router = RecoveryRouter()
        request = route_request(bundle)
        router.route(request)
        restored = RecoveryRouter(ledger=RecoveryLedger.restore(router.ledger.snapshot()))
        self.assertEqual("no_progress", restored.route(request).reason_code)

    def test_ten_thousand_duplicate_observations_are_mechanically_bounded(
        self,
    ) -> None:
        bundle = FailureBundleBuilder().build(observation("candidate_stale"))
        router = RecoveryRouter()
        request = route_request(bundle)
        first = router.route(request)
        self.assertTrue(first.may_continue)
        for _ in range(10_000):
            self.assertEqual("no_progress", router.route(request).reason_code)
        self.assertEqual(1, len(router.ledger.seen_attempts))
        self.assertEqual(1, len(router.ledger.attempted_routes))


class ExceptionReportTests(unittest.TestCase):
    def test_report_identity_is_deterministic_and_is_not_authority(self) -> None:
        report = ExceptionReport(
            "scope_expansion_required",
            ("src/outside.py",),
            ("src/inside.py",),
            ("failure-bundle",),
            ("request_scope_revision",),
            requested_authority_change="write_scope",
        )
        replay = ExceptionReport(
            "scope_expansion_required",
            ("src/outside.py",),
            ("src/inside.py",),
            ("failure-bundle",),
            ("request_scope_revision",),
            requested_authority_change="write_scope",
        )
        self.assertEqual(report.report_id, replay.report_id)
        self.assertNotEqual("", report.requested_authority_change)


class VerificationBackendRegistryTests(unittest.TestCase):
    def test_only_ready_equivalent_backends_are_candidates(self) -> None:
        executor = object()
        registry = VerificationBackendRegistry(
            (
                VerificationBackend("primary", "python", "unhealthy", executor),
                VerificationBackend("approved", "python", "ready", executor),
                VerificationBackend("not-ready", "python", "configured", executor),
                VerificationBackend("other", "node", "ready", executor),
            ),
            "primary",
        )
        self.assertEqual(
            ("approved",),
            registry.ready_equivalent_backends("primary"),
        )

    def test_unknown_backend_fails_closed(self) -> None:
        registry = VerificationBackendRegistry(
            (VerificationBackend("primary", "python", "ready", object()),),
            "primary",
        )
        with self.assertRaisesRegex(ContractError, "verification_backend_unknown"):
            registry.backend("invented")

    def test_backend_capability_state_is_typed(self) -> None:
        with self.assertRaisesRegex(
            ContractError,
            "verification_backend_state_invalid",
        ):
            VerificationBackendRegistry(
                (
                    VerificationBackend(
                        "primary",
                        "python",
                        "probably-ready",
                        object(),
                    ),
                ),
                "primary",
            )
