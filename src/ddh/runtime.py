from __future__ import annotations

import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from ddh.agent_driver import (
    AgentDriverPort,
    AgentResult,
    AgentResultValidator,
    IsolatedCandidateCapabilityPort,
    WorkRequest,
)
from ddh.bundle import BundleExportRequest, CandidateBundleExporter
from ddh.candidate import (
    AdmissionRejected,
    CandidateController,
    ChangeSet,
    FrozenCandidate,
    workspace_manifest_digest,
)
from ddh.coordination import (
    LaneSubmission,
    ModuleWorkGroup,
    ParallelAssessmentInput,
    WorkCoordinator,
    WorkLane,
)
from ddh.integration import CentralIntegrator, JoinBarrier
from ddh.mutation import ChangeGuard, WriteAssignment
from ddh.completion import CompletionDecision, CompletionJudge
from ddh.context import (
    ContextCurator,
    ContextEnvelope,
    ContextItem,
    ContextSourcePort,
)
from ddh.contracts import AuthorityReference, CandidateReference, ContractError, content_digest
from ddh.failure import (
    DiagnosticExcerpt,
    ExceptionReport,
    FailureBundle,
    FailureBundleBuilder,
    FailureClassifier,
    FailureObservation,
    FailureProgress,
)
from ddh.recovery import (
    AttemptFingerprint,
    ProgressIdentity,
    RecoveryController,
    RecoveryLedger,
    RecoveryPolicy,
    RecoveryRoute,
    RecoveryRouteRequest,
    RecoveryRouter,
)
from ddh.specification import (
    ConfirmationRecord,
    SpecificationCompiler,
    WorkloadSpecification,
)
from ddh.state import AtomicJsonStateStore, InvocationState
from ddh.system_map import ImpactClosure, ImpactResolver, MapQuery
from ddh.telemetry import JsonlTelemetry, TelemetryEvent
from ddh.test_auditor import (
    AssetAdmission,
    TestAuditor,
    TestRepairCoordinator,
    TestRepairPort,
    TestRepairProbePort,
    VerificationAsset,
)
from ddh.verification import (
    FixedCommandAdapter,
    PytestAdapter,
    VerificationResult,
    VerificationRunner,
    VerificationBackend,
    VerificationBackendRegistry,
    VerificationExecutorPort,
    adaptive_timeout_seconds,
)


class VerificationAssetProvider(Protocol):
    def build(
        self,
        candidate: FrozenCandidate,
    ) -> tuple[tuple[VerificationAsset | None, VerificationAsset], ...]: ...


class ImpactAwareVerificationAssetProvider(Protocol):
    def build_for_impact(
        self,
        candidate: FrozenCandidate,
        impact: ImpactClosure,
    ) -> tuple[tuple[VerificationAsset | None, VerificationAsset], ...]: ...


@dataclass(frozen=True)
class RuntimeOutcome:
    invocation_id: str
    completion: CompletionDecision
    candidate: FrozenCandidate | None
    results: tuple[VerificationResult, ...]
    bundle_path: Path | None
    exception_report: ExceptionReport | None = None
    failure_bundle: FailureBundle | None = None


@dataclass(frozen=True)
class RuntimeRequest:
    workload_document: dict[str, object]
    confirmation: ConfirmationRecord
    source_root: Path
    invocation_root: Path
    repository_id: str
    requested_ref: str
    resolved_commit: str
    invocation_id: str | None = None


@dataclass
class _ExecutionSession:
    invocation_id: str
    specification: WorkloadSpecification
    context: ContextEnvelope
    request: RuntimeRequest
    failure_bundle: FailureBundle | None = None
    attempt: int = 0
    attempted_routes: tuple[str, ...] = ()
    last_failed_candidate: FrozenCandidate | None = None
    last_failed_results: tuple[VerificationResult, ...] = ()
    state_store: AtomicJsonStateStore | None = None


@dataclass(frozen=True)
class _CandidateEvidence:
    impact: ImpactClosure
    admissions: tuple[AssetAdmission, ...]
    results: tuple[VerificationResult, ...]
    failure_bundles: tuple[FailureBundle, ...] = ()


class Phase1Runtime:
    def __init__(
        self,
        impact_resolver: ImpactResolver,
        agent_driver: AgentDriverPort,
        asset_provider: VerificationAssetProvider,
        telemetry: JsonlTelemetry,
        context_source: ContextSourcePort | None = None,
        isolated_candidate_capability: IsolatedCandidateCapabilityPort | None = None,
    ) -> None:
        self._impact_resolver = impact_resolver
        self._agent_driver = agent_driver
        self._asset_provider = asset_provider
        self._telemetry = telemetry
        self._context_source = context_source
        self._isolated_candidate_capability = isolated_candidate_capability
        self._compiler = SpecificationCompiler()
        self._agent_validator = AgentResultValidator()
        self._auditor = TestAuditor()
        self._runner = VerificationRunner()
        self._judge = CompletionJudge()

    def execute(self, request: RuntimeRequest) -> RuntimeOutcome:
        invocation_id = request.invocation_id or str(uuid4())
        state_store = AtomicJsonStateStore(request.invocation_root / "state")
        specification = self._compiler.compile(
            request.workload_document,
            request.confirmation,
        )
        existing = state_store.load(invocation_id)
        restored = self._restore_if_terminal(existing, specification.authority.digest)
        if restored is not None:
            return restored
        session = self._start_session(invocation_id, specification, request)
        session.state_store = state_store
        self._record_started(state_store, session, existing)
        outcome = self._attempt_loop(session)
        self._record_terminal(
            state_store,
            outcome,
            specification.authority.digest,
        )
        return outcome

    def _start_session(
        self,
        invocation_id: str,
        specification: WorkloadSpecification,
        request: RuntimeRequest,
    ) -> _ExecutionSession:
        impact = self._resolve_impact(
            specification,
            request,
            "initial_scope",
            (),
        )
        context = self._build_context(specification, impact)
        return _ExecutionSession(invocation_id, specification, context, request)

    def _record_started(
        self,
        state_store: AtomicJsonStateStore,
        session: _ExecutionSession,
        existing: InvocationState | None,
    ) -> None:
        if existing is not None:
            return
        state_store.compare_and_swap(
            session.invocation_id,
            None,
            {
                "stage": "started",
                "specification": session.specification.authority.digest,
            },
        )

    def _record_terminal(
        self,
        state_store: AtomicJsonStateStore,
        outcome: RuntimeOutcome,
        specification_digest: str,
    ) -> None:
        current = state_store.load(outcome.invocation_id)
        state_store.compare_and_swap(
            outcome.invocation_id,
            current.generation,
            {
                "stage": "terminal",
                "specification": specification_digest,
                "reason_code": outcome.completion.reason_code,
                "work_package_completed": outcome.completion.work_package_completed,
                "outcome": _serialize_outcome(outcome),
            },
        )

    def _restore_if_terminal(
        self,
        existing: InvocationState | None,
        specification_digest: str,
    ) -> RuntimeOutcome | None:
        if existing is None:
            return None
        payload = existing.payload
        if payload.get("specification") != specification_digest:
            raise ContractError("invocation_identity_digest_conflict")
        if payload.get("stage") != "terminal":
            return None
        return _restore_outcome(payload["outcome"])

    def _attempt_loop(self, session: _ExecutionSession) -> RuntimeOutcome:
        current_source = session.request.source_root
        previous_failure: str | None = None
        max_attempts = int(session.specification.budgets.get("agent_attempts", 3))
        for attempt in range(1, max_attempts + 1):
            attempt_result = self._run_attempt(session, attempt, current_source)
            if not self._requires_product_repair(attempt_result):
                return attempt_result
            candidate = attempt_result.candidate
            if candidate is None:
                return self._no_progress_from_attempt(session, attempt_result)
            failure = self._failure_fingerprint(candidate, attempt_result.results)
            if failure == previous_failure:
                return self._no_progress_from_attempt(session, attempt_result)
            previous_failure = failure
            current_source = candidate.root
        return self._budget_exhausted(
            session.invocation_id,
            candidate,
            attempt_result.results,
        )

    def _requires_product_repair(self, outcome: RuntimeOutcome) -> bool:
        return (
            not outcome.completion.work_package_completed
            and outcome.completion.reason_code == "required_verification_failed"
        )

    def _no_progress_from_attempt(
        self,
        session: _ExecutionSession,
        outcome: RuntimeOutcome,
    ) -> RuntimeOutcome:
        return self._no_progress(
            session.invocation_id,
            outcome.candidate,
            outcome.results,
        )

    def _run_attempt(
        self,
        session: _ExecutionSession,
        attempt: int,
        current_source: Path,
    ) -> RuntimeOutcome:
        controller = self._materialize_candidate(session, attempt, current_source)
        resolution = self._resolve_agent_result(
            session,
            attempt,
            controller.baseline_digest,
        )
        if isinstance(resolution, RuntimeOutcome):
            return resolution
        result = resolution
        exception = self._agent_result_exception(session, result)
        if exception is not None:
            return exception
        return self._admit_and_evaluate(session, controller, result)

    def _admit_and_evaluate(
        self,
        session: _ExecutionSession,
        controller: CandidateController,
        result: AgentResult,
    ) -> RuntimeOutcome:
        try:
            controller.admit(result.proposed_changes)
        except AdmissionRejected as error:
            return self._scope_admission_exception(session, error)
        candidate = controller.freeze()
        try:
            controller.assert_current(candidate.reference)
            return self._evaluate_candidate(session, controller, candidate)
        except ContractError as error:
            return self._candidate_exception(session, candidate, str(error))

    def _agent_result_exception(
        self,
        session: _ExecutionSession,
        result: AgentResult,
    ) -> RuntimeOutcome | None:
        if result.result_type == "scope_change_required":
            return self._scope_change_exception(session, result)
        if not self._candidate_mode_allowed(result):
            return self._protocol_exception(
                session,
                "isolated_candidate_capability_unproven",
            )
        if result.result_type not in {"patch_proposal", "isolated_candidate"}:
            return self._agent_exception(session.invocation_id, result.result_type)
        return None

    def _candidate_mode_allowed(self, result: AgentResult) -> bool:
        if result.result_type != "isolated_candidate":
            return True
        if self._isolated_candidate_capability is None:
            return False
        return self._isolated_candidate_capability.proves(result)

    def _materialize_candidate(
        self,
        session: _ExecutionSession,
        attempt: int,
        current_source: Path,
    ) -> CandidateController:
        controller = CandidateController(
            current_source,
            self._candidate_root(session.request.invocation_root, attempt),
            session.specification.write_scope,
            starting_generation=attempt - 1,
        )
        controller.materialize()
        return controller

    def _candidate_root(self, invocation_root: Path, attempt: int) -> Path:
        preferred = invocation_root / f"candidate-{attempt}"
        if not preferred.exists():
            return preferred
        return invocation_root / f"candidate-{attempt}-resume-{uuid4()}"

    def _build_work_request(
        self,
        session: _ExecutionSession,
        attempt: int,
        baseline_digest: str,
        dispositions: tuple[str, ...] = (),
    ) -> WorkRequest:
        # One projection keeps every authority-bearing field auditable together.
        return WorkRequest(
            session.invocation_id,
            session.specification.authority,
            attempt,
            session.specification.goal,
            session.specification.write_scope,
            session.specification.acceptance_scenarios,
            session.context,
            context_dispositions=dispositions,
            risk_class=session.specification.risk_class,
            candidate_baseline_digest=baseline_digest,
            repository_id=session.request.repository_id,
            requested_ref=session.request.requested_ref,
            resolved_commit=session.request.resolved_commit,
            prohibitions=session.specification.prohibitions,
            budgets=dict(session.specification.budgets),
            escalation_conditions=(
                "architecture_change",
                "semantic_change",
                "scope_change",
                "external_side_effect",
            ),
            failure_bundle=session.failure_bundle,
        )

    def _resolve_agent_result(
        self,
        session: _ExecutionSession,
        attempt: int,
        baseline_digest: str,
    ) -> AgentResult | RuntimeOutcome:
        dispositions: tuple[str, ...] = ()
        for _ in range(4):
            request = self._build_work_request(
                session, attempt, baseline_digest, dispositions
            )
            result = self._pull_and_validate(session, request)
            if isinstance(result, RuntimeOutcome):
                return result
            if result.result_type != "context_request":
                return result
            disposition = self._expand_context(session, result)
            dispositions += (f"{result.context_request.selector}:{disposition}",)
        return self._agent_exception(
            session.invocation_id,
            "context_request_no_progress",
        )

    def _pull_and_validate(
        self,
        session: _ExecutionSession,
        request: WorkRequest,
    ) -> AgentResult | RuntimeOutcome:
        result = self._pull_with_safe_retry(request)
        if result is None:
            return self._agent_exception(
                session.invocation_id,
                "agent_driver_recovery_exhausted",
            )
        try:
            self._agent_validator.validate(request, result)
        except ContractError as error:
            return self._protocol_exception(session, str(error))
        return result

    def _pull_with_safe_retry(self, request: WorkRequest) -> AgentResult | None:
        for _ in range(2):
            try:
                return self._agent_driver.pull(request)
            except (OSError, TimeoutError):
                continue
        return None

    def _expand_context(
        self,
        session: _ExecutionSession,
        result: AgentResult,
    ) -> str:
        request = result.context_request
        if request is None:
            return "denied_protocol_invalid"
        content = self._read_context(
            session.context,
            request.selector,
            request.purpose,
        )
        tokens = self._context_token_budget(session.specification)
        disposition = ContextCurator(tokens).expand(
            session.context,
            request,
            content,
        )
        session.context = disposition.envelope
        return disposition.outcome

    def _context_token_budget(
        self,
        specification: WorkloadSpecification,
    ) -> int:
        return int(specification.budgets.get("effective_context_tokens", 20_000))

    def _read_context(
        self,
        current: ContextEnvelope,
        selector: str,
        purpose: str,
    ) -> str | None:
        if self._context_source is None:
            return None
        if selector not in _context_selectors(current.map_facts):
            return None
        return self._context_source.read(selector, purpose)

    def _evaluate_candidate(
        self,
        session: _ExecutionSession,
        controller: CandidateController,
        candidate: FrozenCandidate,
    ) -> RuntimeOutcome:
        evidence = self._collect_candidate_evidence(session, candidate)
        if not self._candidate_remained_current(controller, candidate):
            return self._candidate_changed(
                session.invocation_id,
                candidate,
                evidence.results,
            )
        return self._complete_candidate(session, candidate, evidence)

    def _collect_candidate_evidence(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
    ) -> _CandidateEvidence:
        impact = self._resolve_impact(
            session.specification,
            session.request,
            "actual_delta_reconciliation",
            candidate.changes.changed_paths,
        )
        admissions = self._admit_assets(session.specification, candidate)
        results = self._verify(candidate, admissions)
        return _CandidateEvidence(impact, admissions, results)

    def _complete_candidate(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        evidence: _CandidateEvidence,
    ) -> RuntimeOutcome:
        completion = self._judge_evidence(candidate, evidence)
        bundle = self._export_if_complete(
            session.request.invocation_root,
            session.request.source_root,
            session.specification,
            candidate,
            evidence.admissions,
            evidence.results,
            completion,
        )
        self._emit(session.invocation_id, "attempt_completed", completion.reason_code)
        return RuntimeOutcome(
            session.invocation_id,
            completion,
            candidate,
            evidence.results,
            bundle,
        )

    def _judge_evidence(
        self,
        candidate: FrozenCandidate,
        evidence: _CandidateEvidence,
    ) -> CompletionDecision:
        return self._judge.evaluate(
            candidate,
            evidence.impact,
            evidence.admissions,
            evidence.results,
        )

    def _resolve_impact(
        self,
        specification: WorkloadSpecification,
        request: RuntimeRequest,
        purpose: str,
        changed_resources: tuple[str, ...],
    ) -> ImpactClosure:
        query = MapQuery(
            request.repository_id,
            request.requested_ref,
            request.resolved_commit,
            specification.selected_nodes,
            purpose,
            changed_resources=changed_resources,
        )
        return self._impact_resolver.resolve(query)

    def _build_context(
        self,
        specification: WorkloadSpecification,
        impact: ImpactClosure,
    ) -> ContextEnvelope:
        tokens = int(specification.budgets.get("effective_context_tokens", 20_000))
        curator = ContextCurator(tokens)
        items = (
            ContextItem("goal", specification.goal, "implementation"),
            ContextItem(
                "expected_behavior",
                "\n".join(specification.expected_behavior),
                "acceptance",
            ),
        )
        return curator.materialize(
            items,
            impact,
            required_selectors=("goal", "expected_behavior"),
        )

    def _candidate_remained_current(
        self,
        controller: CandidateController,
        candidate: FrozenCandidate,
    ) -> bool:
        try:
            controller.assert_current(candidate.reference)
            return True
        except ContractError:
            return False

    def _candidate_changed(
        self,
        invocation_id: str,
        candidate: FrozenCandidate,
        results: tuple[VerificationResult, ...],
    ) -> RuntimeOutcome:
        decision = CompletionDecision(
            "blocked",
            "undetermined",
            "incomplete",
            "candidate_content_changed_after_freeze",
            False,
        )
        return RuntimeOutcome(invocation_id, decision, candidate, results, None)

    def _admit_assets(
        self,
        specification: WorkloadSpecification,
        candidate: FrozenCandidate,
    ) -> tuple[AssetAdmission, ...]:
        proposals = self._asset_provider.build(candidate)
        return tuple(
            self._auditor.audit(
                baseline,
                proposed,
                specification.acceptance_scenarios,
                independent_reviewer=True,
            )
            for baseline, proposed in proposals
        )

    def _verify(
        self,
        candidate: FrozenCandidate,
        admissions: tuple[AssetAdmission, ...],
    ) -> tuple[VerificationResult, ...]:
        return tuple(
            self._verify_asset(candidate, admission)
            for admission in admissions
        )

    def _verify_asset(
        self,
        candidate: FrozenCandidate,
        admission: AssetAdmission,
    ) -> VerificationResult:
        recovery = RecoveryController()
        while True:
            result = self._run_asset_in_fresh_workspace(candidate, admission)
            if not result.retryable:
                return result
            fingerprint = AttemptFingerprint(
                admission.asset.digest,
                candidate.reference.digest,
                "fresh_runner_environment",
                result.reason_code,
            )
            disposition = recovery.evaluate(
                fingerprint,
                has_new_evidence=False,
                transient_infrastructure_failure=True,
            )
            if not disposition.may_continue:
                return result

    def _run_asset_in_fresh_workspace(
        self,
        candidate: FrozenCandidate,
        admission: AssetAdmission,
        executor: VerificationExecutorPort | None = None,
    ) -> VerificationResult:
        with tempfile.TemporaryDirectory() as directory:
            runner_root = Path(directory) / "subject"
            shutil.copytree(candidate.root, runner_root, symlinks=True)
            asset = admission.asset
            timeout = adaptive_timeout_seconds(
                asset.declared_duration_seconds,
                asset.historical_p95_seconds,
                asset.reliable_estimate_seconds,
            )
            adapter = self._verification_adapter(asset)
            plan = adapter.build_plan(asset, runner_root, timeout)
            return (executor or self._runner).run(plan)

    def _verification_adapter(
        self,
        asset: VerificationAsset,
    ) -> PytestAdapter | FixedCommandAdapter:
        if asset.adapter_id == "pytest":
            return PytestAdapter()
        return FixedCommandAdapter()

    def _export_if_complete(
        self,
        invocation_root: Path,
        original_source: Path,
        specification: WorkloadSpecification,
        candidate: FrozenCandidate,
        admissions: tuple[AssetAdmission, ...],
        results: tuple[VerificationResult, ...],
        completion: CompletionDecision,
    ) -> Path | None:
        if not completion.work_package_completed:
            return None
        request = BundleExportRequest(
            invocation_root / "bundle",
            original_source,
            candidate,
            specification.authority,
            admissions,
            results,
            completion,
        )
        return CandidateBundleExporter().export(request)

    def _failure_fingerprint(
        self,
        candidate: FrozenCandidate,
        results: tuple[VerificationResult, ...],
    ) -> str:
        reason = results[0].reason_code if results else "verification_missing"
        fingerprint = AttemptFingerprint(
            "current_work_request",
            candidate.reference.digest,
            "agent_repair",
            reason,
        )
        return fingerprint.digest

    def _agent_exception(self, invocation_id: str, reason: str) -> RuntimeOutcome:
        decision = CompletionDecision("blocked", "undetermined", "incomplete", reason, False)
        self._emit(invocation_id, "structured_exception", reason)
        return RuntimeOutcome(invocation_id, decision, None, (), None)

    def _protocol_exception(
        self,
        session: _ExecutionSession,
        reason: str,
    ) -> RuntimeOutcome:
        report = ExceptionReport(
            reason,
            (),
            session.specification.write_scope,
            ("agent_result_rejected_before_admission",),
            ("submit_current_generation_result", "cancel_work_package"),
        )
        return self._reported_exception(session.invocation_id, report)

    def _scope_change_exception(
        self,
        session: _ExecutionSession,
        result: AgentResult,
    ) -> RuntimeOutcome:
        requested = tuple(sorted(result.proposed_changes))
        report = ExceptionReport(
            "scope_change_required",
            requested,
            session.specification.write_scope,
            ("agent_reported_required_change_outside_current_authority",),
            ("propose_specification_revision", "retain_current_scope"),
        )
        return self._reported_exception(session.invocation_id, report)

    def _scope_admission_exception(
        self,
        session: _ExecutionSession,
        error: AdmissionRejected,
    ) -> RuntimeOutcome:
        report = ExceptionReport(
            "scope_admission_rejected",
            error.invalid_paths,
            session.specification.write_scope,
            ("mixed_or_out_of_scope_admission_unit_rejected",),
            ("rework_within_scope", "propose_specification_revision"),
        )
        return self._reported_exception(session.invocation_id, report)

    def _candidate_exception(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        reason: str,
    ) -> RuntimeOutcome:
        report = ExceptionReport(
            reason,
            candidate.changes.changed_paths,
            session.specification.write_scope,
            ("candidate_or_verification_contract_rejected",),
            ("repair_candidate_or_asset", "cancel_work_package"),
        )
        return self._reported_exception(
            session.invocation_id,
            report,
            candidate,
        )

    def _reported_exception(
        self,
        invocation_id: str,
        report: ExceptionReport,
        candidate: FrozenCandidate | None = None,
        failure_bundle: FailureBundle | None = None,
        results: tuple[VerificationResult, ...] = (),
    ) -> RuntimeOutcome:
        decision = CompletionDecision(
            "blocked",
            "undetermined",
            "incomplete",
            report.reason_code,
            False,
        )
        self._emit(invocation_id, "structured_exception", report.reason_code)
        return RuntimeOutcome(
            invocation_id,
            decision,
            candidate,
            results,
            None,
            report,
            failure_bundle,
        )

    def _no_progress(
        self,
        invocation_id: str,
        candidate: FrozenCandidate | None,
        results: tuple[VerificationResult, ...],
    ) -> RuntimeOutcome:
        decision = CompletionDecision("blocked", "failed", "incomplete", "no_progress", False)
        self._emit(invocation_id, "execution_blocked", "no_progress")
        return RuntimeOutcome(invocation_id, decision, candidate, results, None)

    def _budget_exhausted(
        self,
        invocation_id: str,
        candidate: FrozenCandidate | None,
        results: tuple[VerificationResult, ...],
    ) -> RuntimeOutcome:
        decision = CompletionDecision(
            "blocked",
            "undetermined",
            "incomplete",
            "agent_budget_exhausted",
            False,
        )
        self._emit(invocation_id, "execution_blocked", decision.reason_code)
        return RuntimeOutcome(invocation_id, decision, candidate, results, None)

    def _emit(self, invocation_id: str, event_type: str, reason_code: str) -> None:
        self._telemetry.emit(
            TelemetryEvent(event_type, invocation_id, {"reason_code": reason_code})
        )


class Phase2Runtime(Phase1Runtime):
    def __init__(
        self,
        impact_resolver: ImpactResolver,
        agent_driver: AgentDriverPort,
        asset_provider: VerificationAssetProvider,
        telemetry: JsonlTelemetry,
        context_source: ContextSourcePort | None = None,
        isolated_candidate_capability: IsolatedCandidateCapabilityPort | None = None,
        backend_registry: VerificationBackendRegistry | None = None,
        recovery_policy: RecoveryPolicy | None = None,
        impact_asset_provider: ImpactAwareVerificationAssetProvider | None = None,
        test_repair_port: TestRepairPort | None = None,
        test_repair_probe_port: TestRepairProbePort | None = None,
    ) -> None:
        super().__init__(
            impact_resolver,
            agent_driver,
            asset_provider,
            telemetry,
            context_source,
            isolated_candidate_capability,
        )
        self._failure_builder = FailureBundleBuilder()
        self._failure_classifier = FailureClassifier()
        self._backend_registry = backend_registry or VerificationBackendRegistry(
            (
                VerificationBackend(
                    "local-process",
                    "local-process",
                    "ready",
                    self._runner,
                ),
            ),
            "local-process",
        )
        self._recovery_policy = recovery_policy or RecoveryPolicy(
            approved_backends=self._backend_registry.backend_ids,
        )
        self._impact_asset_provider = impact_asset_provider
        self._test_repair = (
            TestRepairCoordinator(
                self._auditor,
                test_repair_port,
                test_repair_probe_port,
            )
            if (
                test_repair_port is not None
                and test_repair_probe_port is not None
            )
            else None
        )

    def _start_session(
        self,
        invocation_id: str,
        specification: WorkloadSpecification,
        request: RuntimeRequest,
    ) -> _ExecutionSession:
        existing = AtomicJsonStateStore(
            request.invocation_root / "state"
        ).load(invocation_id)
        if (
            existing is not None
            and existing.payload.get("stage") == "recovery_pending"
        ):
            context = _restore_context(existing.payload["context"])
            return _ExecutionSession(
                invocation_id,
                specification,
                context,
                request,
            )
        return super()._start_session(
            invocation_id,
            specification,
            request,
        )

    def _attempt_loop(self, session: _ExecutionSession) -> RuntimeOutcome:
        current_source = session.request.source_root
        router = RecoveryRouter(self._recovery_policy)
        observed_candidates: dict[str, int] = {}
        max_attempts = int(session.specification.budgets.get("agent_attempts", 3))
        start_attempt = 1
        restored = self._restore_recovery_checkpoint(session)
        if restored is not None:
            current_source, router, start_attempt = restored
            if start_attempt > max_attempts:
                return self._route_terminal(
                    session,
                    RuntimeOutcome(
                        session.invocation_id,
                        CompletionDecision(
                            "blocked",
                            "undetermined",
                            "incomplete",
                            "recovery_budget_exhausted",
                            False,
                        ),
                        session.last_failed_candidate,
                        session.last_failed_results,
                        None,
                        failure_bundle=session.failure_bundle,
                    ),
                    RecoveryRoute(
                        "exception",
                        "recovery_budget_exhausted",
                        "preserve_and_report",
                        False,
                        True,
                        required_authority=("budget_increase",),
                    ),
                )
        for attempt in range(start_attempt, max_attempts + 1):
            session.attempt = attempt
            outcome = self._run_attempt(session, attempt, current_source)
            if outcome.completion.work_package_completed:
                return outcome
            outcome = self._ensure_failure_bundle(session, outcome)
            if outcome.candidate is not None:
                session.last_failed_candidate = outcome.candidate
                session.last_failed_results = outcome.results
            route = self._route_for_outcome(
                session,
                outcome,
                router,
                observed_candidates,
                max_attempts - attempt,
            )
            if route is None:
                return outcome
            self._emit(
                session.invocation_id,
                "recovery_route_selected",
                route.reason_code,
            )
            if route.may_continue:
                session.failure_bundle = outcome.failure_bundle
                session.attempted_routes += (route.action,)
                if (
                    route.action == "repair_product_in_scope"
                    and outcome.candidate is not None
                ):
                    current_source = outcome.candidate.root
                self._record_recovery_checkpoint(
                    session,
                    outcome,
                    router,
                    current_source,
                    attempt + 1,
                )
                continue
            return self._route_terminal(session, outcome, route)
        return self._route_terminal(
            session,
            outcome,
            RecoveryRoute(
                "exception",
                "recovery_budget_exhausted",
                "preserve_and_report",
                False,
                True,
                required_authority=("budget_increase",),
            ),
        )

    def _record_recovery_checkpoint(
        self,
        session: _ExecutionSession,
        outcome: RuntimeOutcome,
        router: RecoveryRouter,
        current_source: Path,
        next_attempt: int,
    ) -> None:
        store = session.state_store
        if store is None:
            return
        current = store.load(session.invocation_id)
        store.compare_and_swap(
            session.invocation_id,
            current.generation,
            {
                "stage": "recovery_pending",
                "specification": session.specification.authority.digest,
                "next_attempt": next_attempt,
                "current_source": str(current_source),
                "attempted_routes": session.attempted_routes,
                "recovery_ledger": router.ledger.snapshot(),
                "context": _serialize_context(session.context),
                "outcome": _serialize_outcome(outcome),
            },
        )

    def _restore_recovery_checkpoint(
        self,
        session: _ExecutionSession,
    ) -> tuple[Path, RecoveryRouter, int] | None:
        store = session.state_store
        if store is None:
            return None
        current = store.load(session.invocation_id)
        if current is None or current.payload.get("stage") != "recovery_pending":
            return None
        payload = current.payload
        outcome = _restore_outcome(payload["outcome"])
        session.failure_bundle = outcome.failure_bundle
        session.attempted_routes = tuple(payload.get("attempted_routes", ()))
        session.context = _restore_context(payload["context"])
        session.last_failed_candidate = outcome.candidate
        session.last_failed_results = outcome.results
        ledger = RecoveryLedger.restore(payload["recovery_ledger"])
        return (
            Path(payload["current_source"]),
            RecoveryRouter(self._recovery_policy, ledger),
            int(payload["next_attempt"]),
        )

    def _admit_and_evaluate(
        self,
        session: _ExecutionSession,
        controller: CandidateController,
        result: AgentResult,
    ) -> RuntimeOutcome:
        try:
            controller.admit(result.proposed_changes)
        except AdmissionRejected as error:
            return self._scope_admission_exception(session, error)
        candidate = controller.freeze()
        previous = session.last_failed_candidate
        if (
            previous is not None
            and candidate.reference.digest == previous.reference.digest
        ):
            return self._no_progress(
                session.invocation_id,
                previous,
                session.last_failed_results,
            )
        try:
            controller.assert_current(candidate.reference)
            return self._evaluate_candidate(session, controller, candidate)
        except ContractError as error:
            return self._candidate_exception(session, candidate, str(error))

    def _collect_candidate_evidence(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
    ) -> _CandidateEvidence:
        impact = self._resolve_impact(
            session.specification,
            session.request,
            self._impact_reconciliation_purpose(session),
            candidate.changes.changed_paths,
        )
        proposals = self._build_phase2_proposals(candidate, impact)
        if any(
            proposed.candidate != candidate.reference
            for _, proposed in proposals
        ):
            proposals = self._build_phase2_proposals(candidate, impact)
        if any(
            proposed.candidate != candidate.reference
            for _, proposed in proposals
        ):
            raise ContractError("verification_asset_candidate_stale")
        admissions = self._admit_phase2_proposals(
            session.specification,
            proposals,
        )
        results, failure_bundles = self._verify_phase2(
            session,
            candidate,
            admissions,
        )
        return _CandidateEvidence(
            impact,
            admissions,
            results,
            failure_bundles,
        )

    def _impact_reconciliation_purpose(
        self,
        session: _ExecutionSession,
    ) -> str:
        failure = session.failure_bundle
        if failure is None or not failure.failed_scenario_ids:
            return "actual_delta_reconciliation"
        scenario_projection = ",".join(failure.failed_scenario_ids)
        return (
            "failed_scenario_reconciliation:"
            + scenario_projection[:480]
        )

    def _build_phase2_proposals(
        self,
        candidate: FrozenCandidate,
        impact: ImpactClosure,
    ) -> tuple[tuple[VerificationAsset | None, VerificationAsset], ...]:
        if self._impact_asset_provider is not None:
            return self._impact_asset_provider.build_for_impact(
                candidate,
                impact,
            )
        return self._asset_provider.build(candidate)

    def _admit_phase2_proposals(
        self,
        specification: WorkloadSpecification,
        proposals: tuple[
            tuple[VerificationAsset | None, VerificationAsset],
            ...,
        ],
    ) -> tuple[AssetAdmission, ...]:
        if self._test_repair is None:
            return tuple(
                self._auditor.audit(
                    baseline,
                    proposed,
                    _authorized_asset_scenarios(
                        specification,
                        baseline,
                    ),
                    independent_reviewer=True,
                )
                for baseline, proposed in proposals
            )
        return tuple(
            self._test_repair.admit(
                baseline,
                proposed,
                _authorized_asset_scenarios(
                    specification,
                    baseline,
                ),
            )
            for baseline, proposed in proposals
        )

    def _complete_candidate(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        evidence: _CandidateEvidence,
    ) -> RuntimeOutcome:
        platform_result = next(
            (
                result
                for result in evidence.results
                if result.reason_code == "platform_blocked"
            ),
            None,
        )
        if platform_result is not None:
            return RuntimeOutcome(
                session.invocation_id,
                CompletionDecision(
                    "blocked",
                    "undetermined",
                    "incomplete",
                    "platform_blocked",
                    False,
                ),
                candidate,
                evidence.results,
                None,
                failure_bundle=self._build_evidence_bundle(
                    session,
                    candidate,
                    evidence,
                    "platform_blocked",
                ),
            )
        outcome = super()._complete_candidate(session, candidate, evidence)
        if outcome.completion.work_package_completed:
            return outcome
        return replace(
            outcome,
            failure_bundle=self._build_evidence_bundle(
                session,
                candidate,
                evidence,
                outcome.completion.reason_code,
            ),
        )

    def _agent_result_exception(
        self,
        session: _ExecutionSession,
        result: AgentResult,
    ) -> RuntimeOutcome | None:
        boundary_classes = {
            "test_semantics_uncertain": "test_semantics_uncertain",
            "external_side_effect_uncertain": "external_side_effect_uncertain",
        }
        failure_class = boundary_classes.get(result.result_type)
        if failure_class is None:
            return super()._agent_result_exception(session, result)
        bundle = self._failure_builder.build(
            FailureObservation(
                failure_class,
                result.result_type,
                session.specification.authority,
                session.invocation_id,
                affected_resources=tuple(sorted(result.proposed_changes)),
                remaining_budget=self._remaining_agent_budget(session),
                remaining_budgets=(
                    (
                        "agent_attempts",
                        self._remaining_agent_budget(session),
                    ),
                ),
                progress=FailureProgress(
                    context_generation=session.context.generation,
                    approved_strategy=result.result_type,
                ),
                external_side_effect_uncertain=(
                    failure_class == "external_side_effect_uncertain"
                ),
                required_human_authority=self._required_authority(failure_class),
            )
        )
        route = RecoveryRouter(self._recovery_policy).route(
            self._route_request(bundle, session, None, 0, result.result_type)
        )
        empty = RuntimeOutcome(
            session.invocation_id,
            CompletionDecision(
                "blocked",
                "undetermined",
                "incomplete",
                result.result_type,
                False,
            ),
            None,
            (),
            None,
            failure_bundle=bundle,
        )
        return self._route_terminal(session, empty, route)

    def _candidate_exception(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        reason: str,
    ) -> RuntimeOutcome:
        if not _is_test_asset_failure(reason):
            return super()._candidate_exception(session, candidate, reason)
        failure_class = (
            "test_asset_stale"
            if reason == "verification_asset_candidate_stale"
            else "test_implementation_defect"
        )
        bundle = self._failure_builder.build(
            FailureObservation(
                failure_class,
                reason,
                session.specification.authority,
                session.invocation_id,
                candidate.reference,
                failed_scenario_ids=(
                    session.specification.acceptance_scenarios
                ),
                affected_resources=candidate.changes.changed_paths,
                attempted_routes=session.attempted_routes,
                remaining_budget=self._remaining_agent_budget(session),
                allowed_machine_actions=self._allowed_actions(failure_class),
                remaining_budgets=(
                    (
                        "agent_attempts",
                        self._remaining_agent_budget(session),
                    ),
                ),
                progress=FailureProgress(
                    candidate_generation=candidate.reference.generation,
                    context_generation=session.context.generation,
                    approved_strategy="test_asset_repair",
                ),
            )
        )
        blocked = RuntimeOutcome(
            session.invocation_id,
            CompletionDecision(
                "blocked",
                "undetermined",
                "incomplete",
                reason,
                False,
            ),
            candidate,
            (),
            None,
            failure_bundle=bundle,
        )
        return self._route_terminal(
            session,
            blocked,
            RecoveryRoute(
                "exception",
                "test_repair_route_unavailable",
                "provide_independent_test_repair",
                False,
                False,
            ),
        )

    def _ensure_failure_bundle(
        self,
        session: _ExecutionSession,
        outcome: RuntimeOutcome,
    ) -> RuntimeOutcome:
        if outcome.failure_bundle is not None:
            return outcome
        failure_class = self._class_for_outcome(outcome)
        observation = FailureObservation(
            failure_class,
            outcome.completion.reason_code,
            session.specification.authority,
            session.invocation_id,
            outcome.candidate.reference if outcome.candidate else None,
            verification_subject_id=(
                outcome.results[0].plan_id if outcome.results else ""
            ),
            test_asset_digests=tuple(
                result.asset_digest for result in outcome.results
            ),
            failed_scenario_ids=session.specification.acceptance_scenarios,
            affected_resources=(
                outcome.candidate.changes.changed_paths
                if outcome.candidate
                else ()
            ),
            attempted_routes=session.attempted_routes,
            remaining_budget=self._remaining_agent_budget(session),
            retryable=any(result.retryable for result in outcome.results),
            external_side_effect_uncertain=(
                failure_class == "external_side_effect_uncertain"
            ),
            stdout=outcome.results[0].stdout if outcome.results else "",
            stderr=outcome.results[0].stderr if outcome.results else "",
            allowed_machine_actions=self._allowed_actions(failure_class),
            required_human_authority=self._required_authority(failure_class),
            remaining_budgets=(
                (
                    "agent_attempts",
                    self._remaining_agent_budget(session),
                ),
            ),
            progress=FailureProgress(
                candidate_generation=(
                    outcome.candidate.reference.generation
                    if outcome.candidate
                    else 0
                ),
                context_generation=session.context.generation,
                approved_strategy=self._strategy_for(failure_class),
            ),
        )
        return replace(outcome, failure_bundle=self._failure_builder.build(observation))

    def _class_for_outcome(self, outcome: RuntimeOutcome) -> str:
        reason = outcome.completion.reason_code
        if reason in {"scope_change_required"}:
            return "scope_expansion_required"
        if reason == "test_semantics_uncertain":
            return "test_semantics_uncertain"
        if reason == "external_side_effect_uncertain":
            return "external_side_effect_uncertain"
        if reason in {
            "candidate_content_changed_after_freeze",
            "agent_result_stale_generation",
        }:
            return "candidate_stale"
        if reason == "impact_closure_incomplete":
            return "system_map_unavailable"
        if reason == "context_request_no_progress":
            return "context_insufficient"
        if reason in {
            "platform_blocked",
            "runner_start_failed",
            "verification_timeout",
            "required_verification_incomplete",
        }:
            return "runner_failed"
        if reason == "agent_driver_recovery_exhausted":
            return "tool_backend_unavailable"
        return "product_failed"

    def _route_for_outcome(
        self,
        session: _ExecutionSession,
        outcome: RuntimeOutcome,
        router: RecoveryRouter,
        observed_candidates: dict[str, int],
        remaining_budget: int,
    ) -> RecoveryRoute | None:
        bundle = outcome.failure_bundle
        if bundle is None:
            return None
        reason = outcome.completion.reason_code
        if reason in {
            "platform_blocked",
            "agent_driver_recovery_exhausted",
            "required_verification_incomplete",
        }:
            return RecoveryRoute(
                "exception",
                "platform_blocked",
                "preserve_and_report",
                False,
                True,
                required_authority=("new_recovery_policy",),
            )
        if reason == "impact_closure_incomplete":
            return RecoveryRoute(
                "exception",
                "impact_discovery_blocked",
                "preserve_and_report",
                False,
                False,
            )
        if reason == "context_request_no_progress":
            return RecoveryRoute(
                "exception",
                "context_recovery_blocked",
                "preserve_and_report",
                False,
                False,
            )
        if reason == "required_verification_missing":
            return RecoveryRoute(
                "exception",
                "test_repair_route_unavailable",
                "provide_independent_test_admission",
                False,
                False,
            )
        routable = {
            "required_verification_failed",
            "scope_admission_rejected",
            "candidate_content_changed_after_freeze",
            "agent_result_stale_generation",
            "scope_change_required",
            "test_semantics_uncertain",
            "external_side_effect_uncertain",
        }
        if reason not in routable:
            return None
        candidate_digest = bundle.candidate.digest if bundle.candidate else ""
        if candidate_digest not in observed_candidates:
            observed_candidates[candidate_digest] = len(observed_candidates)
        progress = ProgressIdentity(
            candidate_generation=observed_candidates[candidate_digest],
            context_generation=session.context.generation,
            approved_strategy=self._strategy_for(bundle.failure_class),
        )
        request = RecoveryRouteRequest(
            bundle,
            AttemptFingerprint(
                session.specification.authority.digest,
                candidate_digest,
                progress.approved_strategy,
                bundle.reason_code,
            ),
            progress,
            remaining_budget,
        )
        return router.route(request)

    def _route_terminal(
        self,
        session: _ExecutionSession,
        outcome: RuntimeOutcome,
        route: RecoveryRoute,
    ) -> RuntimeOutcome:
        bundle = outcome.failure_bundle
        report = ExceptionReport(
            route.reason_code,
            (
                outcome.exception_report.requested_paths
                if outcome.exception_report
                else ()
            ),
            session.specification.write_scope,
            (bundle.bundle_id,) if bundle else (),
            (route.action,),
            current_authority_class=session.specification.risk_class,
            requested_authority_class=(
                "L3" if route.requires_human else session.specification.risk_class
            ),
            blocked_transition=route.action,
            failure_bundle_id=bundle.bundle_id if bundle else "",
            affected_nodes=bundle.affected_nodes if bundle else (),
            affected_resources=bundle.affected_resources if bundle else (),
            affected_contracts=(
                bundle.failed_scenario_ids if bundle else ()
            ),
            architecture_query_result_id=(
                bundle.architecture_query_result_id if bundle else ""
            ),
            live_source_confirmations=(
                bundle.live_source_confirmations if bundle else ()
            ),
            attempted_actions=tuple(
                dict.fromkeys(session.attempted_routes + (route.action,))
            ),
            remaining_budget=bundle.remaining_budget if bundle else 0,
            preserved_candidate_digest=(
                outcome.candidate.reference.digest if outcome.candidate else ""
            ),
            preserved_diff=(
                outcome.candidate.changes.changed_paths
                if outcome.candidate
                else ()
            ),
            requested_authority_change=",".join(route.required_authority),
            verification_impact=(
                bundle.failed_scenario_ids if bundle else ()
            ),
            external_impact=(
                ("external_side_effect_uncertain",)
                if bundle and bundle.external_side_effect_uncertain
                else ()
            ),
            options=(route.action,),
            preserved_verification_subject=(
                bundle.verification_subject_id if bundle else ""
            ),
            option_tradeoffs=(
                (
                    "current_authority_and_acceptance_remain_unchanged",
                )
                if route.requires_human
                else ("safe_automatic_routes_exhausted",)
            ),
        )
        return self._reported_exception(
            session.invocation_id,
            report,
            outcome.candidate,
            bundle,
            outcome.results,
        )

    def _build_evidence_bundle(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        evidence: _CandidateEvidence,
        reason_code: str,
    ) -> FailureBundle:
        failure_class = self._class_from_evidence(
            reason_code,
            evidence,
            candidate,
        )
        failed_assets = {
            result.asset_digest
            for result in evidence.results
            if not _verification_passed(result)
        }
        failed_scenarios = tuple(
            scenario
            for admission in evidence.admissions
            if admission.asset.digest in failed_assets
            for scenario in admission.asset.scenario_ids
        )
        first_result = next(
            (
                result
                for result in evidence.results
                if not _verification_passed(result)
            ),
            evidence.results[0] if evidence.results else None,
        )
        runner_bundle = next(iter(evidence.failure_bundles), None)
        if runner_bundle is not None:
            failure_class = runner_bundle.failure_class
        observation = FailureObservation(
            failure_class,
            (
                runner_bundle.reason_code
                if runner_bundle is not None
                else first_result.reason_code
                if first_result
                else reason_code
            ),
            session.specification.authority,
            session.invocation_id,
            candidate.reference,
            verification_subject_id=first_result.plan_id if first_result else "",
            test_asset_digests=tuple(
                admission.asset.digest for admission in evidence.admissions
            ),
            failed_scenario_ids=failed_scenarios,
            affected_nodes=evidence.impact.nodes,
            affected_resources=candidate.changes.changed_paths,
            actual_diff_summary=candidate.changes.changed_paths,
            architecture_query_result_id=_impact_identity(evidence.impact),
            live_source_confirmations=(
                ("bounded_live_source_fallback",)
                if evidence.impact.used_live_fallback
                else ()
            ),
            attempted_routes=(
                runner_bundle.attempted_routes
                if runner_bundle is not None
                else session.attempted_routes
            ),
            remaining_budget=(
                runner_bundle.remaining_budget
                if runner_bundle is not None
                else self._remaining_agent_budget(session)
            ),
            retryable=first_result.retryable if first_result else False,
            stdout=(
                runner_bundle.diagnostics.stdout
                if runner_bundle is not None
                else first_result.stdout
                if first_result
                else ""
            ),
            stderr=(
                runner_bundle.diagnostics.stderr
                if runner_bundle is not None
                else first_result.stderr
                if first_result
                else ""
            ),
            traceback_location=(
                _first_traceback_location(first_result.stderr)
                if first_result
                else ""
            ),
            allowed_machine_actions=self._allowed_actions(failure_class),
            required_human_authority=self._required_authority(failure_class),
            progress=(
                runner_bundle.progress
                if runner_bundle is not None
                else FailureProgress(
                    candidate_generation=candidate.reference.generation,
                    test_asset_generation=max(
                        (
                            admission.asset.version
                            for admission in evidence.admissions
                        ),
                        default=0,
                    ),
                    context_generation=session.context.generation,
                    impact_generation=session.attempt,
                    approved_strategy=self._strategy_for(failure_class),
                )
            ),
            remaining_budgets=(
                runner_bundle.remaining_budgets
                if runner_bundle is not None
                else (
                    (
                        "agent_attempts",
                        self._remaining_agent_budget(session),
                    ),
                )
            ),
            consumed_architecture_facts=evidence.impact.consumed_facts,
        )
        return self._failure_builder.build(observation)

    def _class_from_evidence(
        self,
        reason_code: str,
        evidence: _CandidateEvidence,
        candidate: FrozenCandidate,
    ) -> str:
        if reason_code == "impact_closure_incomplete":
            return "system_map_unavailable"
        if reason_code == "verification_wrong_subject":
            return "candidate_stale"
        if reason_code in {
            "verification_asset_not_admitted",
            "verification_completeness_incomplete",
        }:
            return "test_asset_stale"
        if not evidence.results:
            return "runner_failed"
        first = next(
            (
                result
                for result in evidence.results
                if not _verification_passed(result)
            ),
            evidence.results[0],
        )
        if first.reason_code == "tool_backend_unavailable":
            return "tool_backend_unavailable"
        return self._failure_classifier.classify_verification(first)

    def _verify_phase2(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        admissions: tuple[AssetAdmission, ...],
    ) -> tuple[tuple[VerificationResult, ...], tuple[FailureBundle, ...]]:
        executions = tuple(
            self._verify_asset_phase2(session, candidate, admission)
            for admission in admissions
        )
        return (
            tuple(result for result, _ in executions),
            tuple(bundle for _, bundle in executions if bundle is not None),
        )

    def _verify_asset_phase2(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        admission: AssetAdmission,
    ) -> tuple[VerificationResult, FailureBundle | None]:
        backend_id = self._backend_registry.default_backend_id
        policy = self._recovery_policy
        router = RecoveryRouter(policy)
        router.ledger.backend_attempts[backend_id] = (
            policy.equivalent_backend_attempt_limit
        )
        environment_generation = 0
        maximum_actions = (
            policy.transient_action_limit + len(policy.approved_backends) + 1
        )
        for action_index in range(maximum_actions):
            backend = self._backend_registry.backend(backend_id)
            result = self._run_backend(candidate, admission, backend)
            if not result.retryable:
                return result, None
            failure_class = (
                "tool_backend_unavailable"
                if result.reason_code == "tool_backend_unavailable"
                else "runner_failed"
            )
            bundle = self._runner_failure_bundle(
                session,
                candidate,
                admission,
                result,
                failure_class,
                router,
                maximum_actions - action_index,
                environment_generation,
            )
            progress = ProgressIdentity(
                environment_generation=environment_generation,
                approved_strategy="runner_recovery",
            )
            route = router.route(
                RecoveryRouteRequest(
                    bundle,
                    AttemptFingerprint(
                        admission.asset.digest,
                        candidate.reference.digest,
                        "runner_recovery",
                        result.reason_code,
                    ),
                    progress,
                    maximum_actions - action_index,
                    backend_id,
                    self._backend_registry.ready_equivalent_backends(backend_id),
                )
            )
            self._emit(
                session.invocation_id,
                "runner_recovery_route_selected",
                route.reason_code,
            )
            if not route.may_continue:
                terminal = self._runner_failure_bundle(
                    session,
                    candidate,
                    admission,
                    result,
                    failure_class,
                    router,
                    maximum_actions - action_index,
                    environment_generation,
                    (route.action,),
                )
                return (
                    replace(
                        result,
                        reason_code=route.reason_code,
                        retryable=False,
                    ),
                    terminal,
                )
            environment_generation += 1
            if route.selected_backend:
                backend_id = route.selected_backend
        terminal = self._runner_failure_bundle(
            session,
            candidate,
            admission,
            result,
            failure_class,
            router,
            0,
            environment_generation,
            ("preserve_and_report",),
        )
        return (
            replace(result, reason_code="platform_blocked", retryable=False),
            terminal,
        )

    def _run_backend(
        self,
        candidate: FrozenCandidate,
        admission: AssetAdmission,
        backend: VerificationBackend,
    ) -> VerificationResult:
        if not backend.ready:
            return VerificationResult(
                f"backend:{backend.backend_id}",
                candidate.reference,
                admission.asset.digest,
                "failed",
                "undetermined",
                "incomplete",
                "tool_backend_unavailable",
                True,
                None,
                0,
                "",
                "",
                False,
            )
        return self._run_asset_in_fresh_workspace(
            candidate,
            admission,
            backend.executor,
        )

    def _runner_failure_bundle(
        self,
        session: _ExecutionSession,
        candidate: FrozenCandidate,
        admission: AssetAdmission,
        result: VerificationResult,
        failure_class: str,
        router: RecoveryRouter,
        remaining_budget: int,
        environment_generation: int,
        additional_routes: tuple[str, ...] = (),
    ) -> FailureBundle:
        return self._failure_builder.build(
            FailureObservation(
                failure_class,
                result.reason_code,
                session.specification.authority,
                session.invocation_id,
                candidate.reference,
                result.plan_id,
                (admission.asset.digest,),
                admission.asset.scenario_ids,
                affected_resources=candidate.changes.changed_paths,
                attempted_routes=(
                    tuple(router.ledger.attempted_routes) + additional_routes
                ),
                remaining_budget=remaining_budget,
                retryable=True,
                stdout=result.stdout,
                stderr=result.stderr,
                allowed_machine_actions=self._allowed_actions(failure_class),
                progress=FailureProgress(
                    candidate_generation=candidate.reference.generation,
                    test_asset_generation=admission.asset.version,
                    environment_generation=environment_generation,
                    context_generation=session.context.generation,
                    impact_generation=session.attempt,
                    approved_strategy="runner_recovery",
                ),
                remaining_budgets=(
                    ("runner_recovery_actions", remaining_budget),
                ),
            )
        )

    def _route_request(
        self,
        bundle: FailureBundle,
        session: _ExecutionSession,
        candidate: FrozenCandidate | None,
        remaining_budget: int,
        strategy: str,
    ) -> RecoveryRouteRequest:
        return RecoveryRouteRequest(
            bundle,
            AttemptFingerprint(
                session.specification.authority.digest,
                candidate.reference.digest if candidate else "",
                strategy,
                bundle.reason_code,
            ),
            ProgressIdentity(approved_strategy=strategy),
            remaining_budget,
        )

    def _remaining_agent_budget(self, session: _ExecutionSession) -> int:
        maximum = int(session.specification.budgets.get("agent_attempts", 3))
        return max(0, maximum - session.attempt)

    def _strategy_for(self, failure_class: str) -> str:
        strategies = {
            "product_failed": "agent_product_repair",
            "candidate_stale": "candidate_generation_refresh",
            "scope_expansion_required": "scope_revision",
            "test_semantics_uncertain": "specification_revision",
            "external_side_effect_uncertain": "external_high_risk_flow",
        }
        return strategies.get(failure_class, "bounded_recovery")

    def _allowed_actions(self, failure_class: str) -> tuple[str, ...]:
        actions = {
            "product_failed": ("repair_product_in_scope",),
            "test_implementation_defect": ("repair_and_readmit_test_asset",),
            "runner_failed": (
                "rebuild_runner_environment",
                "select_approved_backend",
            ),
            "tool_backend_unavailable": ("select_approved_backend",),
            "context_insufficient": ("expand_context",),
            "system_map_unavailable": ("query_bounded_live_source",),
            "candidate_stale": ("create_current_candidate_generation",),
            "test_asset_stale": ("readmit_current_test_asset",),
            "impact_underestimated": ("expand_verification_closure",),
        }
        return actions.get(failure_class, ())

    def _required_authority(self, failure_class: str) -> tuple[str, ...]:
        authority = {
            "test_semantics_uncertain": ("expected_behavior", "acceptance"),
            "scope_expansion_required": ("write_scope",),
            "external_side_effect_uncertain": ("external_operation",),
        }
        return authority.get(failure_class, ())


def _context_selectors(map_facts: tuple[str, ...]) -> set[str]:
    selectors: set[str] = set()
    for fact in map_facts:
        if fact.startswith("node:"):
            selectors.add(fact.removeprefix("node:"))
        if fact.startswith("resource:"):
            binding = fact.removeprefix("resource:")
            selectors.add(binding.split("->", 1)[0])
    return selectors


def _verification_passed(result: VerificationResult) -> bool:
    return (
        result.terminal_state == "succeeded"
        and result.acceptance_outcome == "passed"
        and result.verification_completeness == "complete"
    )


def _is_test_asset_failure(reason: str) -> bool:
    prefixes = (
        "verification_",
        "independent_test_",
        "test_repair_",
    )
    return reason.startswith(prefixes)


def _authorized_asset_scenarios(
    specification: WorkloadSpecification,
    baseline: VerificationAsset | None,
) -> tuple[str, ...]:
    inherited = baseline.scenario_ids if baseline is not None else ()
    return tuple(
        sorted(
            set(specification.acceptance_scenarios + inherited)
        )
    )


def _impact_identity(impact: ImpactClosure) -> str:
    return content_digest(
        {
            "nodes": impact.nodes,
            "relations": impact.relations,
            "consumed_facts": impact.consumed_facts,
            "used_live_fallback": impact.used_live_fallback,
            "complete": impact.complete,
        }
    )


def _first_traceback_location(stderr: str) -> str:
    for line in stderr.splitlines():
        normalized = line.strip()
        if normalized.startswith("File ") or normalized.startswith("Traceback"):
            return normalized
    return ""


def _serialize_context(context: ContextEnvelope) -> dict[str, object]:
    return {
        "generation": context.generation,
        "items": [asdict(item) for item in context.items],
        "map_facts": context.map_facts,
        "charged_tokens": context.charged_tokens,
        "digest": context.digest,
    }


def _restore_context(value: dict[str, object]) -> ContextEnvelope:
    items = tuple(ContextItem(**item) for item in value["items"])
    context = ContextEnvelope(
        int(value["generation"]),
        items,
        tuple(value["map_facts"]),
        int(value["charged_tokens"]),
        str(value["digest"]),
    )
    expected = content_digest(
        {
            "generation": context.generation,
            "items": [
                {
                    "selector": item.selector,
                    "purpose": item.purpose,
                    "content_digest": content_digest(item.content),
                }
                for item in context.items
            ],
            "map_facts": context.map_facts,
            "charged_tokens": context.charged_tokens,
        }
    )
    if context.digest != expected:
        raise ContractError("recovery_context_digest_mismatch")
    return context


def _serialize_outcome(outcome: RuntimeOutcome) -> dict[str, object]:
    candidate = None
    if outcome.candidate is not None:
        candidate = {
            "reference": asdict(outcome.candidate.reference),
            "root": str(outcome.candidate.root),
            "changed_paths": outcome.candidate.changes.changed_paths,
        }
    return {
        "invocation_id": outcome.invocation_id,
        "completion": asdict(outcome.completion),
        "candidate": candidate,
        "results": [_serialize_result(result) for result in outcome.results],
        "bundle_path": str(outcome.bundle_path) if outcome.bundle_path else None,
        "exception_report": (
            asdict(outcome.exception_report)
            if outcome.exception_report is not None
            else None
        ),
        "failure_bundle": (
            asdict(outcome.failure_bundle)
            if outcome.failure_bundle is not None
            else None
        ),
    }


def _serialize_result(result: VerificationResult) -> dict[str, object]:
    value = asdict(result)
    value["stdout"] = ""
    value["stderr"] = ""
    return value


def _restore_outcome(value: dict[str, object]) -> RuntimeOutcome:
    candidate = _restore_candidate(value["candidate"])
    results = tuple(_restore_result(item) for item in value["results"])
    report_value = value["exception_report"]
    report = _restore_exception_report(report_value)
    failure_bundle = _restore_failure_bundle(value.get("failure_bundle"))
    bundle_value = value["bundle_path"]
    return RuntimeOutcome(
        value["invocation_id"],
        CompletionDecision(**value["completion"]),
        candidate,
        results,
        Path(bundle_value) if bundle_value else None,
        report,
        failure_bundle,
    )


def _restore_candidate(value: dict[str, object] | None) -> FrozenCandidate | None:
    if value is None:
        return None
    reference = CandidateReference(**value["reference"])
    changes = ChangeSet((), tuple(value["changed_paths"]), (), ())
    return FrozenCandidate(reference, Path(value["root"]), (), (), changes)


def _restore_exception_report(
    value: dict[str, object] | None,
) -> ExceptionReport | None:
    if value is None:
        return None
    tuple_fields = {
        "requested_paths",
        "current_write_scope",
        "evidence",
        "allowed_next_steps",
        "affected_nodes",
        "affected_resources",
        "affected_contracts",
        "live_source_confirmations",
        "attempted_actions",
        "preserved_diff",
        "verification_impact",
        "external_impact",
        "options",
        "unaffected_work",
        "option_tradeoffs",
    }
    normalized = dict(value)
    for field in tuple_fields:
        if field in normalized:
            normalized[field] = tuple(normalized[field])
    return ExceptionReport(**normalized)


def _restore_failure_bundle(
    value: dict[str, object] | None,
) -> FailureBundle | None:
    if value is None:
        return None
    tuple_fields = {
        "test_asset_digests",
        "failed_scenario_ids",
        "affected_nodes",
        "affected_resources",
        "actual_diff_summary",
        "live_source_confirmations",
        "attempted_routes",
        "allowed_machine_actions",
        "required_human_authority",
        "consumed_architecture_facts",
    }
    normalized = dict(value)
    for field in tuple_fields:
        normalized[field] = tuple(normalized[field])
    normalized["specification"] = AuthorityReference(**normalized["specification"])
    candidate = normalized["candidate"]
    normalized["candidate"] = (
        CandidateReference(**candidate) if candidate is not None else None
    )
    normalized["diagnostics"] = DiagnosticExcerpt(**normalized["diagnostics"])
    progress = normalized.get("progress")
    normalized["progress"] = (
        FailureProgress(**progress)
        if progress is not None
        else FailureProgress()
    )
    normalized["remaining_budgets"] = tuple(
        tuple(item)
        for item in normalized.get("remaining_budgets", ())
    )
    return FailureBundle(**normalized)


def _restore_result(value: dict[str, object]) -> VerificationResult:
    candidate = CandidateReference(**value["candidate"])
    return VerificationResult(
        plan_id=value["plan_id"],
        candidate=candidate,
        asset_digest=value["asset_digest"],
        terminal_state=value["terminal_state"],
        acceptance_outcome=value["acceptance_outcome"],
        verification_completeness=value["verification_completeness"],
        reason_code=value["reason_code"],
        retryable=value["retryable"],
        exit_code=value["exit_code"],
        duration_milliseconds=value["duration_milliseconds"],
        stdout=value["stdout"],
        stderr=value["stderr"],
        output_truncated=value["output_truncated"],
    )


class LaneVerificationPort(Protocol):
    """Runs local lane checks without trusting the worker's completion claim."""

    def verify(self, lane: WorkLane, submission: LaneSubmission) -> bool: ...


@dataclass(frozen=True)
class ParallelWorkPlan:
    groups: tuple[ModuleWorkGroup, ...]
    lanes: tuple[WorkLane, ...]
    integration_order: tuple[str, ...]
    projected_parallel_cost: int
    projected_serial_cost: int
    mutation_mode: str = "isolated_candidate"
    shared_resource_owners: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ParallelRuntimeRequest:
    runtime_request: RuntimeRequest
    plan: ParallelWorkPlan


@dataclass(frozen=True)
class Phase3Outcome:
    completion: CompletionDecision
    candidate: FrozenCandidate | None
    lane_submissions: tuple[LaneSubmission, ...]
    results: tuple[VerificationResult, ...]
    parallel_result: str
    consumed_impact_facts: tuple[str, ...]


class Phase3Runtime:
    """Reference L2 fork/join runtime with central Candidate integration."""

    def __init__(
        self,
        impact_resolver: ImpactResolver,
        lane_drivers: dict[str, AgentDriverPort],
        asset_provider: VerificationAssetProvider,
        lane_verifier: LaneVerificationPort,
        telemetry: JsonlTelemetry,
    ) -> None:
        self._impact_resolver = impact_resolver
        self._lane_drivers = dict(lane_drivers)
        self._asset_provider = asset_provider
        self._lane_verifier = lane_verifier
        self._telemetry = telemetry
        self._compiler = SpecificationCompiler()
        self._agent_validator = AgentResultValidator()
        self._auditor = TestAuditor()
        self._runner = VerificationRunner()

    # This orchestration stays linear so authority transitions remain auditable.
    def execute(self, request: ParallelRuntimeRequest) -> Phase3Outcome:
        runtime_request = request.runtime_request
        specification = self._compiler.compile(
            runtime_request.workload_document,
            runtime_request.confirmation,
        )
        if specification.risk_class != "L2":
            raise ContractError("phase3_requires_l2_specification")
        plan = request.plan
        impact = self._resolve_impact(specification, runtime_request, "parallel_partitioning", ())
        coordinator = WorkCoordinator()
        for group in plan.groups:
            coordinator.register_group(group)
        for lane in plan.lanes:
            coordinator.register_lane(lane)
        for resource, lane_id in plan.shared_resource_owners:
            if coordinator.shared_owner(resource, lane_id) != lane_id:
                return self._blocked("parallel_unsafe", impact)
        assessment = coordinator.assess(
            ParallelAssessmentInput(
                independent_work_units=len(plan.lanes),
                logical_overlap=self._unowned_logical_overlap(
                    plan.lanes,
                    dict(plan.shared_resource_owners),
                ),
                mechanical_write_separation=plan.mutation_mode == "isolated_candidate",
                projected_parallel_cost=plan.projected_parallel_cost,
                projected_serial_cost=plan.projected_serial_cost,
            )
        )
        if assessment.result not in {"parallel_allowed", "parallel_not_worthwhile"}:
            return self._blocked(assessment.result, impact)
        base_candidate = CandidateReference(
            f"baseline-{runtime_request.invocation_id or 'phase3'}",
            0,
            workspace_manifest_digest(runtime_request.source_root),
        )
        guard = ChangeGuard()
        active_lanes, assignments = self._activate_lanes(
            coordinator,
            guard,
            plan.lanes,
            base_candidate,
            plan.mutation_mode,
        )
        submissions = self._run_lanes(
            specification,
            runtime_request,
            impact,
            active_lanes,
            base_candidate,
            coordinator,
            parallel=assessment.result == "parallel_allowed",
        )
        self._mark_groups_verified(coordinator, plan.groups)
        if not coordinator.ready_to_join(tuple(group.group_id for group in plan.groups)):
            return self._blocked("waiting_for_current_lanes", impact, submissions)
        integrator = CentralIntegrator(guard)
        preparation = integrator.admit(
            runtime_request.source_root,
            runtime_request.invocation_root / "phase3-integration-candidate",
            specification.authority,
            tuple(coordinator.lanes[lane.lane_id] for lane in plan.lanes),
            assignments,
            submissions,
            plan.integration_order,
            specification.write_scope,
            specification.prohibitions,
        )
        if preparation.controller is None:
            return self._blocked(preparation.outcome, impact, submissions)
        JoinBarrier(guard).ensure_quiescent(
            tuple(coordinator.lanes[lane.lane_id] for lane in plan.lanes)
        )
        integrated = integrator.freeze(preparation)
        if integrated.candidate is None:
            return self._blocked(integrated.outcome, impact, submissions)
        refreshed_impact = self._resolve_impact(
            specification,
            runtime_request,
            "pre_join_actual_delta_reconciliation",
            integrated.candidate.changes.changed_paths,
        )
        outcome = self._verify_integrated(
            specification,
            integrated.candidate,
            refreshed_impact,
        )
        self._telemetry.emit(
            TelemetryEvent(
                "phase3_join_completed",
                runtime_request.invocation_id or "phase3",
                {
                    "parallel_result": assessment.result,
                    "candidate_generation": integrated.candidate.reference.generation,
                    "subsystem_integrated": outcome.completion.subsystem_integrated,
                },
            )
        )
        return Phase3Outcome(
            outcome.completion,
            integrated.candidate,
            submissions,
            outcome.results,
            assessment.result,
            refreshed_impact.consumed_facts,
        )

    def _activate_lanes(
        self,
        coordinator: WorkCoordinator,
        guard: ChangeGuard,
        lanes: tuple[WorkLane, ...],
        base_candidate: CandidateReference,
        mode: str,
    ) -> tuple[tuple[WorkLane, ...], tuple[WriteAssignment, ...]]:
        active: list[WorkLane] = []
        assignments: list[WriteAssignment] = []
        for lane in lanes:
            assignment = guard.activate(lane, base_candidate, mode)
            active.append(coordinator.activate(lane.lane_id, assignment.boundary_id))
            assignments.append(assignment)
        return tuple(active), tuple(assignments)

    # Request construction and concurrent collection stay adjacent to bind one generation.
    def _run_lanes(
        self,
        specification: WorkloadSpecification,
        runtime_request: RuntimeRequest,
        impact: ImpactClosure,
        lanes: tuple[WorkLane, ...],
        base_candidate: CandidateReference,
        coordinator: WorkCoordinator,
        parallel: bool,
    ) -> tuple[LaneSubmission, ...]:
        requests = {
            lane.lane_id: WorkRequest(
                runtime_request.invocation_id or "phase3",
                specification.authority,
                lane.generation,
                specification.goal,
                lane.resources.physical_paths,
                lane.required_scenarios,
                ContextCurator(
                    int(specification.budgets.get("effective_context_tokens", 20_000))
                ).materialize((), impact),
                mutation_mode="isolated_candidate",
                risk_class="L2",
                candidate_baseline_digest=base_candidate.digest,
                repository_id=runtime_request.repository_id,
                requested_ref=runtime_request.requested_ref,
                resolved_commit=runtime_request.resolved_commit,
                prohibitions=specification.prohibitions + lane.resources.protected_paths,
                budgets=dict(specification.budgets),
                escalation_conditions=(
                    "architecture_change",
                    "semantic_change",
                    "scope_change",
                    "external_side_effect",
                ),
            )
            for lane in lanes
        }
        results = self._collect_lane_results(lanes, requests, parallel)
        submissions: list[LaneSubmission] = []
        for lane in lanes:
            result = results[lane.lane_id]
            if result.result_type not in {"patch_proposal", "isolated_candidate"}:
                raise ContractError("phase3_lane_requires_patch_submission")
            submission = LaneSubmission(
                lane.lane_id,
                lane.generation,
                lane.trusted_writer,
                specification.authority,
                base_candidate.digest,
                result.proposed_changes,
                self._lane_verifier.verify(
                    lane,
                    LaneSubmission(
                        lane.lane_id,
                        lane.generation,
                        lane.trusted_writer,
                        specification.authority,
                        base_candidate.digest,
                        result.proposed_changes,
                        False,
                    ),
                ),
            )
            coordinator.submit(submission)
            submissions.append(submission)
        return tuple(submissions)

    def _collect_lane_results(
        self,
        lanes: tuple[WorkLane, ...],
        requests: dict[str, WorkRequest],
        parallel: bool,
    ) -> dict[str, AgentResult]:
        if not parallel:
            return {
                lane.lane_id: self._pull_lane(lane, requests[lane.lane_id])
                for lane in lanes
            }
        results: dict[str, AgentResult] = {}
        with ThreadPoolExecutor(max_workers=len(lanes)) as executor:
            futures = {
                executor.submit(self._pull_lane, lane, requests[lane.lane_id]): lane
                for lane in lanes
            }
            for future in as_completed(futures):
                lane = futures[future]
                results[lane.lane_id] = future.result()
        return results

    def _pull_lane(self, lane: WorkLane, request: WorkRequest) -> AgentResult:
        try:
            driver = self._lane_drivers[lane.lane_id]
        except KeyError as error:
            raise ContractError("phase3_lane_driver_missing") from error
        result = self._pull_with_recovery(driver, request)
        self._agent_validator.validate(request, result)
        return result

    def _pull_with_recovery(
        self,
        driver: AgentDriverPort,
        request: WorkRequest,
    ) -> AgentResult:
        for attempt in range(2):
            try:
                return driver.pull(request)
            except (OSError, TimeoutError):
                if attempt:
                    break
        raise ContractError("phase3_lane_driver_recovery_exhausted")

    def _mark_groups_verified(
        self,
        coordinator: WorkCoordinator,
        groups: tuple[ModuleWorkGroup, ...],
    ) -> None:
        for group in groups:
            coordinator.mark_module_verified(group.group_id)

    # The asset/audit/run sequence stays adjacent to prevent subject rebinding gaps.
    def _verify_integrated(
        self,
        specification: WorkloadSpecification,
        candidate: FrozenCandidate,
        impact: ImpactClosure,
    ) -> RuntimeOutcome:
        proposals = self._asset_provider.build(candidate)
        admissions = tuple(
            self._auditor.audit(
                baseline,
                proposed,
                specification.acceptance_scenarios,
                independent_reviewer=True,
            )
            for baseline, proposed in proposals
        )
        results = tuple(
            self._runner.run(
                PytestAdapter().build_plan(
                    admission.asset,
                    candidate.root,
                    adaptive_timeout_seconds(
                        admission.asset.declared_duration_seconds,
                        admission.asset.historical_p95_seconds,
                        admission.asset.reliable_estimate_seconds,
                    ),
                )
                if admission.asset.adapter_id == "pytest"
                else FixedCommandAdapter().build_plan(
                    admission.asset,
                    candidate.root,
                    adaptive_timeout_seconds(
                        admission.asset.declared_duration_seconds,
                        admission.asset.historical_p95_seconds,
                        admission.asset.reliable_estimate_seconds,
                    ),
                )
            )
            for admission in admissions
        )
        decision = CompletionJudge().evaluate(candidate, impact, admissions, results)
        if decision.work_package_completed:
            decision = replace(decision, subsystem_integrated="subsystem_integrated")
        else:
            decision = replace(decision, subsystem_integrated="failed")
        return RuntimeOutcome("phase3", decision, candidate, results, None)

    def _resolve_impact(
        self,
        specification: WorkloadSpecification,
        request: RuntimeRequest,
        purpose: str,
        changed_resources: tuple[str, ...],
    ) -> ImpactClosure:
        return self._impact_resolver.resolve(
            MapQuery(
                request.repository_id,
                request.requested_ref,
                request.resolved_commit,
                specification.selected_nodes,
                purpose,
                changed_resources=changed_resources,
            )
        )

    def _unowned_logical_overlap(
        self,
        lanes: tuple[WorkLane, ...],
        shared_owners: dict[str, str],
    ) -> tuple[str, ...]:
        owners: dict[str, str] = {}
        overlap: set[str] = set()
        for lane in lanes:
            for resource in lane.resources.logical_resources:
                previous = owners.setdefault(resource, lane.lane_id)
                declared_owner = shared_owners.get(resource)
                if previous != lane.lane_id and declared_owner not in {
                    previous,
                    lane.lane_id,
                }:
                    overlap.add(resource)
        return tuple(sorted(overlap))

    def _blocked(
        self,
        reason: str,
        impact: ImpactClosure,
        submissions: tuple[LaneSubmission, ...] = (),
    ) -> Phase3Outcome:
        return Phase3Outcome(
            CompletionDecision("blocked", "undetermined", "incomplete", reason, False),
            None,
            submissions,
            (),
            reason,
            impact.consumed_facts,
        )
