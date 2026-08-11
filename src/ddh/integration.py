"""Central, deterministic integration of current Phase 3 lane submissions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ddh.candidate import AdmissionRejected, CandidateController, FrozenCandidate
from ddh.contracts import AuthorityReference, CandidateReference, ContractError
from ddh.coordination import LaneSubmission, WorkLane
from ddh.mutation import ChangeGuard, WriteAssignment


@dataclass(frozen=True)
class PatchAdmission:
    lane_id: str
    outcome: str
    resulting_generation: int | None
    reason_code: str = ""


@dataclass(frozen=True)
class IntegrationResult:
    candidate: FrozenCandidate | None
    admissions: tuple[PatchAdmission, ...]
    outcome: str


@dataclass(frozen=True)
class IntegrationPreparation:
    controller: CandidateController | None
    admissions: tuple[PatchAdmission, ...]
    outcome: str


class CentralIntegrator:
    """The only component that applies lane deltas to an integration Candidate."""

    def __init__(self, guard: ChangeGuard) -> None:
        self._guard = guard

    def admit(
        self,
        source_root: Path,
        candidate_root: Path,
        specification: AuthorityReference,
        lanes: tuple[WorkLane, ...],
        assignments: tuple[WriteAssignment, ...],
        submissions: tuple[LaneSubmission, ...],
        integration_order: tuple[str, ...],
        write_scope: tuple[str, ...],
        protected: tuple[str, ...] = (),
    ) -> IntegrationPreparation:
        lane_by_id = {lane.lane_id: lane for lane in lanes}
        assignment_by_lane = {item.lane_id: item for item in assignments}
        submission_by_lane = {item.lane_id: item for item in submissions}
        self._validate_exact_set(integration_order, lane_by_id, submission_by_lane)
        controller = CandidateController(
            source_root,
            candidate_root,
            write_scope,
            protected,
        )
        controller.materialize()
        admissions: list[PatchAdmission] = []
        for lane_id in integration_order:
            lane = lane_by_id[lane_id]
            assignment = assignment_by_lane.get(lane_id)
            submission = submission_by_lane[lane_id]
            result = self._admit_one(
                controller,
                specification,
                lane,
                assignment,
                submission,
            )
            admissions.append(result)
            if result.outcome not in {
                "accepted_into_candidate",
                "accepted_revalidation_required",
            }:
                return IntegrationPreparation(None, tuple(admissions), result.outcome)
        return IntegrationPreparation(controller, tuple(admissions), "admitted_pending_freeze")

    def freeze(self, preparation: IntegrationPreparation) -> IntegrationResult:
        if preparation.controller is None:
            return IntegrationResult(None, preparation.admissions, preparation.outcome)
        candidate = preparation.controller.freeze()
        preparation.controller.assert_current(candidate.reference)
        return IntegrationResult(candidate, preparation.admissions, "candidate_frozen")

    def _admit_one(
        self,
        controller: CandidateController,
        specification: AuthorityReference,
        lane: WorkLane,
        assignment: WriteAssignment | None,
        submission: LaneSubmission,
    ) -> PatchAdmission:
        if assignment is None:
            return PatchAdmission(lane.lane_id, "rejected_scope_or_partition", None, "assignment_missing")
        if submission.specification != specification:
            return PatchAdmission(lane.lane_id, "rejected_stale_result", None, "specification_stale")
        if submission.generation != lane.generation:
            return PatchAdmission(lane.lane_id, "rejected_stale_result", None, "generation_stale")
        if submission.trusted_writer != lane.trusted_writer:
            return PatchAdmission(lane.lane_id, "rejected_scope_or_partition", None, "writer_mismatch")
        if submission.base_candidate_digest != controller.baseline_digest:
            return PatchAdmission(lane.lane_id, "rejected_stale_result", None, "base_candidate_stale")
        try:
            self._guard.authorize_changes(
                assignment,
                lane.resources,
                submission.trusted_writer,
                dict(submission.changes),
                controller.root,
            )
            controller.admit(submission.changes)
        except AdmissionRejected:
            return PatchAdmission(lane.lane_id, "rejected_scope_or_partition", None, "mixed_scope_patch")
        except ContractError as error:
            reason = str(error)
            outcome = (
                "rejected_stale_result"
                if "generation" in reason or "identity" in reason
                else "rejected_scope_or_partition"
            )
            return PatchAdmission(lane.lane_id, outcome, None, reason)
        outcome = (
            "accepted_into_candidate"
            if controller.generation == 1
            else "accepted_revalidation_required"
        )
        return PatchAdmission(lane.lane_id, outcome, controller.generation)

    def _validate_exact_set(
        self,
        integration_order: tuple[str, ...],
        lane_by_id: dict[str, WorkLane],
        submission_by_lane: dict[str, LaneSubmission],
    ) -> None:
        if len(integration_order) != len(set(integration_order)):
            raise ContractError("integration_order_duplicate")
        if set(integration_order) != set(lane_by_id):
            raise ContractError("integration_order_incomplete")
        if set(integration_order) != set(submission_by_lane):
            raise ContractError("integration_submission_incomplete")


class JoinBarrier:
    """Makes the all-current-groups and all-writers-quiescent rule explicit."""

    def __init__(self, guard: ChangeGuard) -> None:
        self._guard = guard

    def ensure_quiescent(
        self,
        lanes: tuple[WorkLane, ...],
    ) -> tuple[WriteAssignment, ...]:
        assignments: list[WriteAssignment] = []
        for lane in lanes:
            assignment = self._guard.fence(lane.lane_id, lane.generation)
            assignments.append(self._guard.quiesce(lane.lane_id, lane.generation))
        return tuple(assignments)
