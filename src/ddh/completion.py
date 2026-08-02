from __future__ import annotations

from dataclasses import dataclass

from ddh.candidate import FrozenCandidate
from ddh.system_map import ImpactClosure
from ddh.test_auditor import AssetAdmission
from ddh.verification import VerificationResult


@dataclass(frozen=True)
class CompletionDecision:
    terminal_state: str
    acceptance_outcome: str
    verification_completeness: str
    reason_code: str
    work_package_completed: bool
    subsystem_integrated: str = "not_evaluated"
    domain_accepted: str = "not_evaluated"
    release_candidate: str = "not_evaluated"


class CompletionJudge:
    def evaluate(
        self,
        candidate: FrozenCandidate,
        impact: ImpactClosure,
        admissions: tuple[AssetAdmission, ...],
        results: tuple[VerificationResult, ...],
        open_exceptions: tuple[str, ...] = (),
    ) -> CompletionDecision:
        reason = self._failure_reason(
            candidate,
            impact,
            admissions,
            results,
            open_exceptions,
        )
        if reason == "required_verification_incomplete":
            return _incomplete_decision(reason)
        if reason:
            return _failed_decision(reason)
        return _completed_decision()

    def _failure_reason(
        self,
        candidate: FrozenCandidate,
        impact: ImpactClosure,
        admissions: tuple[AssetAdmission, ...],
        results: tuple[VerificationResult, ...],
        open_exceptions: tuple[str, ...],
    ) -> str | None:
        if open_exceptions:
            return "open_exception"
        if not impact.complete or not impact.consumed_facts:
            return "impact_closure_incomplete"
        if not admissions or not results:
            return "required_verification_missing"
        return self._result_failure_reason(candidate, admissions, results)

    def _result_failure_reason(
        self,
        candidate: FrozenCandidate,
        admissions: tuple[AssetAdmission, ...],
        results: tuple[VerificationResult, ...],
    ) -> str | None:
        admitted = {item.asset.digest for item in admissions if item.outcome == "admitted"}
        if any(result.candidate != candidate.reference for result in results):
            return "verification_wrong_subject"
        if any(result.asset_digest not in admitted for result in results):
            return "verification_asset_not_admitted"
        if any(result.verification_completeness != "complete" for result in results):
            return "required_verification_incomplete"
        if any(not _result_passed(result) for result in results):
            return "required_verification_failed"
        if admitted != {result.asset_digest for result in results}:
            return "verification_completeness_incomplete"
        return None


def _incomplete_decision(reason: str) -> CompletionDecision:
    return CompletionDecision(
        "blocked",
        "undetermined",
        "incomplete",
        reason,
        False,
    )


def _failed_decision(reason: str) -> CompletionDecision:
    return CompletionDecision("failed", "failed", "incomplete", reason, False)


def _completed_decision() -> CompletionDecision:
    return CompletionDecision(
        "succeeded",
        "passed",
        "complete",
        "work_package_completed",
        True,
    )


def _result_passed(result: VerificationResult) -> bool:
    return (
        result.terminal_state == "succeeded"
        and result.acceptance_outcome == "passed"
        and result.verification_completeness == "complete"
    )
