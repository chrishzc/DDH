"""Mechanical local write boundary state for DDH Phase 3."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from uuid import uuid4

from ddh.contracts import CandidateReference, ContractError, content_digest
from ddh.coordination import ResourceSet, WorkLane
from ddh.paths import normalize_repository_path


MUTATION_MODES = {"serial_reconciled", "guarded_shared", "isolated_candidate"}


@dataclass(frozen=True)
class WriteAssignment:
    lane_id: str
    generation: int
    trusted_writer: str
    base_candidate: CandidateReference
    resource_digest: str
    mutation_mode: str
    boundary_id: str
    state: str = "boundary_active"
    fence_epoch: int = 0
    in_flight_operations: int = 0


@dataclass(frozen=True)
class HandoffOutcome:
    outcome: str
    old_assignment: WriteAssignment
    new_assignment: WriteAssignment | None


class ChangeGuard:
    """Provides mechanical state that prompts and Agent claims cannot replace."""

    def __init__(self) -> None:
        self._assignments: dict[str, WriteAssignment] = {}

    def activate(
        self,
        lane: WorkLane,
        base_candidate: CandidateReference,
        mutation_mode: str,
    ) -> WriteAssignment:
        if mutation_mode not in MUTATION_MODES:
            raise ContractError("mutation_mode_invalid")
        if lane.state != "planned":
            raise ContractError("boundary_activation_lane_invalid")
        previous = self._assignments.get(lane.lane_id)
        if previous is not None and previous.state not in {"revoked", "quiescent"}:
            raise ContractError("boundary_assignment_still_active")
        assignment = WriteAssignment(
            lane.lane_id,
            lane.generation,
            lane.trusted_writer,
            base_candidate,
            lane.resources.digest,
            mutation_mode,
            f"boundary-{uuid4()}",
        )
        self._assignments[lane.lane_id] = assignment
        return assignment

    def begin_operation(
        self,
        lane_id: str,
        generation: int,
        trusted_writer: str,
    ) -> WriteAssignment:
        assignment = self._current(lane_id, generation, trusted_writer)
        if assignment.state != "boundary_active":
            raise ContractError("mutation_blocked_generation")
        updated = replace(
            assignment,
            in_flight_operations=assignment.in_flight_operations + 1,
        )
        self._assignments[lane_id] = updated
        return updated

    def settle_operation(
        self,
        lane_id: str,
        generation: int,
        trusted_writer: str,
    ) -> WriteAssignment:
        assignment = self._current(lane_id, generation, trusted_writer)
        if assignment.in_flight_operations < 1:
            raise ContractError("mutation_operation_missing")
        updated = replace(
            assignment,
            in_flight_operations=assignment.in_flight_operations - 1,
        )
        self._assignments[lane_id] = updated
        return updated

    def authorize_changes(
        self,
        assignment: WriteAssignment,
        resources: ResourceSet,
        trusted_writer: str,
        changes: dict[str, str | None],
        candidate_root: Path,
    ) -> tuple[str, ...]:
        current = self._current(
            assignment.lane_id,
            assignment.generation,
            trusted_writer,
        )
        if current.boundary_id != assignment.boundary_id:
            raise ContractError("mutation_blocked_generation")
        if current.state != "boundary_active":
            raise ContractError("mutation_blocked_generation")
        canonical: list[str] = []
        invalid: list[str] = []
        for path in changes:
            try:
                normalized = normalize_repository_path(
                    candidate_root,
                    path,
                ).canonical_path
            except ValueError:
                invalid.append(path)
                continue
            canonical.append(normalized)
            if not resources.permits(normalized):
                invalid.append(normalized)
        if invalid:
            raise ContractError("mutation_blocked_resource")
        return tuple(sorted(canonical))

    def fence(self, lane_id: str, generation: int) -> WriteAssignment:
        assignment = self._assignment(lane_id)
        if assignment.generation != generation:
            raise ContractError("mutation_blocked_generation")
        if assignment.state not in {"boundary_active", "fenced"}:
            raise ContractError("mutation_fence_invalid")
        updated = replace(
            assignment,
            state="fenced",
            fence_epoch=assignment.fence_epoch + 1,
        )
        self._assignments[lane_id] = updated
        return updated

    def quiesce(self, lane_id: str, generation: int) -> WriteAssignment:
        assignment = self._assignment(lane_id)
        if assignment.generation != generation or assignment.state != "fenced":
            raise ContractError("quiescence_identity_mismatch")
        if assignment.in_flight_operations:
            raise ContractError("waiting_for_quiescence")
        updated = replace(assignment, state="quiescent")
        self._assignments[lane_id] = updated
        return updated

    def handoff(
        self,
        lane: WorkLane,
        base_candidate: CandidateReference,
        mutation_mode: str,
        mutation_closure_known: bool,
    ) -> HandoffOutcome:
        old = self.fence(lane.lane_id, lane.generation)
        if not mutation_closure_known or old.in_flight_operations:
            return HandoffOutcome("handoff_recovery_required", old, None)
        revoked = replace(old, state="revoked")
        self._assignments[lane.lane_id] = revoked
        next_lane = replace(lane, generation=lane.generation + 1, state="planned")
        new = self.activate(next_lane, base_candidate, mutation_mode)
        return HandoffOutcome("handoff_completed", revoked, new)

    def assignment(self, lane_id: str) -> WriteAssignment:
        return self._assignment(lane_id)

    def _current(
        self,
        lane_id: str,
        generation: int,
        trusted_writer: str,
    ) -> WriteAssignment:
        assignment = self._assignment(lane_id)
        if assignment.generation != generation or assignment.trusted_writer != trusted_writer:
            raise ContractError("mutation_blocked_identity")
        return assignment

    def _assignment(self, lane_id: str) -> WriteAssignment:
        try:
            return self._assignments[lane_id]
        except KeyError as error:
            raise ContractError("mutation_boundary_missing") from error
