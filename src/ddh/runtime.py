from __future__ import annotations

import shutil
import tempfile
from dataclasses import asdict, dataclass
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
)
from ddh.completion import CompletionDecision, CompletionJudge
from ddh.context import (
    ContextCurator,
    ContextEnvelope,
    ContextItem,
    ContextSourcePort,
)
from ddh.contracts import CandidateReference, ContractError
from ddh.recovery import AttemptFingerprint, RecoveryController
from ddh.specification import (
    ConfirmationRecord,
    SpecificationCompiler,
    WorkloadSpecification,
)
from ddh.state import AtomicJsonStateStore, InvocationState
from ddh.system_map import ImpactClosure, ImpactResolver, MapQuery
from ddh.telemetry import JsonlTelemetry, TelemetryEvent
from ddh.test_auditor import AssetAdmission, TestAuditor, VerificationAsset
from ddh.verification import (
    FixedCommandAdapter,
    PytestAdapter,
    VerificationResult,
    VerificationRunner,
    adaptive_timeout_seconds,
)


class VerificationAssetProvider(Protocol):
    def build(
        self,
        candidate: FrozenCandidate,
    ) -> tuple[tuple[VerificationAsset | None, VerificationAsset], ...]: ...


@dataclass(frozen=True)
class RuntimeOutcome:
    invocation_id: str
    completion: CompletionDecision
    candidate: FrozenCandidate | None
    results: tuple[VerificationResult, ...]
    bundle_path: Path | None
    exception_report: ExceptionReport | None = None


@dataclass(frozen=True)
class ExceptionReport:
    reason_code: str
    requested_paths: tuple[str, ...]
    current_write_scope: tuple[str, ...]
    evidence: tuple[str, ...]
    allowed_next_steps: tuple[str, ...]


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


@dataclass(frozen=True)
class _CandidateEvidence:
    impact: ImpactClosure
    admissions: tuple[AssetAdmission, ...]
    results: tuple[VerificationResult, ...]


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
            return self._runner.run(plan)

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
            (),
            None,
            report,
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


def _context_selectors(map_facts: tuple[str, ...]) -> set[str]:
    selectors: set[str] = set()
    for fact in map_facts:
        if fact.startswith("node:"):
            selectors.add(fact.removeprefix("node:"))
        if fact.startswith("resource:"):
            binding = fact.removeprefix("resource:")
            selectors.add(binding.split("->", 1)[0])
    return selectors


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
    bundle_value = value["bundle_path"]
    return RuntimeOutcome(
        value["invocation_id"],
        CompletionDecision(**value["completion"]),
        candidate,
        results,
        Path(bundle_value) if bundle_value else None,
        report,
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
    return ExceptionReport(
        value["reason_code"],
        tuple(value["requested_paths"]),
        tuple(value["current_write_scope"]),
        tuple(value["evidence"]),
        tuple(value["allowed_next_steps"]),
    )


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
