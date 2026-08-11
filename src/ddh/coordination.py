"""Typed, bounded coordination for DDH parallel work packages."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from ddh.contracts import AuthorityReference, CandidateReference, ContractError, content_digest
from ddh.paths import path_matches_any


PARALLEL_RESULTS = {
    "parallel_allowed",
    "parallel_not_worthwhile",
    "parallel_unsafe",
    "needs_human_decision",
}
LANE_KINDS = {"product", "acceptance", "subsystem_acceptance", "integration"}


@dataclass(frozen=True)
class ParallelAssessmentInput:
    independent_work_units: int
    physical_overlap: tuple[str, ...] = ()
    logical_overlap: tuple[str, ...] = ()
    unknown_overlap: bool = False
    mechanical_write_separation: bool = False
    requires_human_change: bool = False
    projected_parallel_cost: int = 0
    projected_serial_cost: int = 0


@dataclass(frozen=True)
class ParallelAssessment:
    result: str
    reasons: tuple[str, ...]
    projected_parallel_cost: int
    projected_serial_cost: int


@dataclass(frozen=True)
class ResourceSet:
    physical_paths: tuple[str, ...]
    logical_resources: tuple[str, ...] = ()
    protected_paths: tuple[str, ...] = ()

    @property
    def digest(self) -> str:
        return content_digest(
            {
                "physical_paths": self.physical_paths,
                "logical_resources": self.logical_resources,
                "protected_paths": self.protected_paths,
            }
        )

    def permits(self, path: str) -> bool:
        return path_matches_any(path, self.physical_paths) and not path_matches_any(
            path,
            self.protected_paths,
        )


@dataclass(frozen=True)
class WorkLane:
    lane_id: str
    group_id: str
    kind: str
    generation: int
    trusted_writer: str
    resources: ResourceSet
    required_scenarios: tuple[str, ...]
    state: str = "planned"
    boundary_id: str | None = None

    def __post_init__(self) -> None:
        if not self.lane_id or not self.group_id or not self.trusted_writer:
            raise ContractError("work_lane_identity_missing")
        if self.kind not in LANE_KINDS:
            raise ContractError("work_lane_kind_invalid")
        if self.generation < 1:
            raise ContractError("work_lane_generation_invalid")
        if not self.resources.physical_paths:
            raise ContractError("work_lane_resources_missing")


@dataclass(frozen=True)
class ModuleWorkGroup:
    group_id: str
    module_node: str
    lane_ids: tuple[str, ...]
    required_scenarios: tuple[str, ...]
    state: str = "planned"


@dataclass(frozen=True)
class LaneSubmission:
    lane_id: str
    generation: int
    trusted_writer: str
    specification: AuthorityReference
    base_candidate_digest: str
    changes: Mapping[str, str | None]
    local_verification_passed: bool
    provisional_red: bool = False

    @property
    def delta_digest(self) -> str:
        return content_digest(
            {
                "lane_id": self.lane_id,
                "generation": self.generation,
                "writer": self.trusted_writer,
                "changes": dict(self.changes),
            }
        )


@dataclass(frozen=True)
class CrossLaneChangeRequest:
    requesting_lane: str
    target_resource: str
    reason: str
    acceptance_reference: str
    root_cause_evidence: str


@dataclass(frozen=True)
class CrossLaneDecision:
    outcome: str
    affected_lanes: tuple[str, ...]


@dataclass
class WorkCoordinator:
    """Owns partition state and semantic routing, never write authority."""

    lanes: dict[str, WorkLane] = field(default_factory=dict)
    groups: dict[str, ModuleWorkGroup] = field(default_factory=dict)
    shared_owners: dict[str, str] = field(default_factory=dict)

    def assess(self, value: ParallelAssessmentInput) -> ParallelAssessment:
        if value.requires_human_change:
            return self._assessment("needs_human_decision", "authority_change_required", value)
        if value.independent_work_units < 2:
            return self._assessment("parallel_not_worthwhile", "single_writer", value)
        if value.unknown_overlap or not value.mechanical_write_separation:
            return self._assessment("parallel_unsafe", "mechanical_separation_missing", value)
        if value.logical_overlap:
            return self._assessment("parallel_unsafe", "logical_overlap_unresolved", value)
        if value.projected_parallel_cost >= value.projected_serial_cost:
            return self._assessment("parallel_not_worthwhile", "net_benefit_not_positive", value)
        return self._assessment("parallel_allowed", "independent_safe_positive_benefit", value)

    def register_group(self, group: ModuleWorkGroup) -> None:
        if group.group_id in self.groups:
            raise ContractError("work_group_duplicate")
        self.groups[group.group_id] = group

    def register_lane(self, lane: WorkLane) -> None:
        if lane.lane_id in self.lanes:
            raise ContractError("work_lane_duplicate")
        if lane.group_id not in self.groups:
            raise ContractError("work_lane_group_missing")
        self.lanes[lane.lane_id] = lane

    def activate(self, lane_id: str, boundary_id: str) -> WorkLane:
        lane = self._lane(lane_id)
        if lane.state != "planned" or not boundary_id:
            raise ContractError("work_lane_activation_invalid")
        active = replace(lane, state="active", boundary_id=boundary_id)
        self.lanes[lane_id] = active
        return active

    def submit(self, submission: LaneSubmission) -> WorkLane:
        lane = self._lane(submission.lane_id)
        if lane.state != "active":
            raise ContractError("lane_submission_not_active")
        if submission.generation != lane.generation:
            raise ContractError("lane_submission_stale_generation")
        if submission.trusted_writer != lane.trusted_writer:
            raise ContractError("lane_submission_writer_mismatch")
        if not submission.local_verification_passed and not submission.provisional_red:
            raise ContractError("lane_local_verification_failed")
        submitted = replace(lane, state="submitted")
        self.lanes[lane.lane_id] = submitted
        return submitted

    def mark_module_verified(self, group_id: str) -> ModuleWorkGroup:
        group = self._group(group_id)
        lanes = tuple(self._lane(lane_id) for lane_id in group.lane_ids)
        if any(lane.state != "submitted" for lane in lanes):
            raise ContractError("module_group_lanes_not_submitted")
        verified = replace(group, state="module_verified")
        self.groups[group_id] = verified
        for lane in lanes:
            self.lanes[lane.lane_id] = replace(
                lane,
                state="waiting_for_subsystem_join",
            )
        return verified

    def shared_owner(self, logical_resource: str, lane_id: str) -> str:
        lane = self._lane(lane_id)
        if lane.state not in {"planned", "active"}:
            raise ContractError("shared_resource_lane_ineligible")
        owner = self.shared_owners.get(logical_resource)
        if owner is None:
            self.shared_owners[logical_resource] = lane_id
            return lane_id
        return owner

    def route_cross_lane_request(
        self,
        request: CrossLaneChangeRequest,
    ) -> CrossLaneDecision:
        requester = self._lane(request.requesting_lane)
        if not request.reason or not request.acceptance_reference or not request.root_cause_evidence:
            return CrossLaneDecision("reject_unnecessary_request", ())
        owner = self.shared_owners.get(request.target_resource)
        if owner:
            return CrossLaneDecision("route_to_current_writer", (owner,))
        if request.target_resource in requester.resources.logical_resources:
            return CrossLaneDecision("repartition_within_scope", (requester.lane_id,))
        return CrossLaneDecision("human_scope_or_spec_decision", ())

    def invalidate_dependents(
        self,
        logical_resource: str,
    ) -> tuple[WorkLane, ...]:
        invalidated: list[WorkLane] = []
        for lane in tuple(self.lanes.values()):
            if logical_resource not in lane.resources.logical_resources:
                continue
            if lane.state not in {"active", "submitted", "waiting_for_subsystem_join"}:
                continue
            refreshed = replace(
                lane,
                generation=lane.generation + 1,
                state="planned",
                boundary_id=None,
            )
            self.lanes[lane.lane_id] = refreshed
            invalidated.append(refreshed)
        return tuple(invalidated)

    def ready_to_join(self, group_ids: tuple[str, ...]) -> bool:
        return all(
            self._group(group_id).state == "module_verified"
            for group_id in group_ids
        )

    def _assessment(
        self,
        result: str,
        reason: str,
        value: ParallelAssessmentInput,
    ) -> ParallelAssessment:
        if result not in PARALLEL_RESULTS:
            raise ContractError("parallel_assessment_result_invalid")
        return ParallelAssessment(
            result,
            (reason,),
            value.projected_parallel_cost,
            value.projected_serial_cost,
        )

    def _lane(self, lane_id: str) -> WorkLane:
        try:
            return self.lanes[lane_id]
        except KeyError as error:
            raise ContractError("work_lane_missing") from error

    def _group(self, group_id: str) -> ModuleWorkGroup:
        try:
            return self.groups[group_id]
        except KeyError as error:
            raise ContractError("work_group_missing") from error
