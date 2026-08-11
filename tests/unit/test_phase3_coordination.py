import tempfile
import unittest
from pathlib import Path

from ddh.contracts import AuthorityReference, CandidateReference, ContractError
from ddh.coordination import (
    CrossLaneChangeRequest,
    LaneSubmission,
    ModuleWorkGroup,
    ParallelAssessmentInput,
    ResourceSet,
    WorkCoordinator,
    WorkLane,
)
from ddh.integration import CentralIntegrator, JoinBarrier
from ddh.mutation import ChangeGuard


AUTHORITY = AuthorityReference("P3", "1", "sha256:p3")
BASE = CandidateReference("base", 0, "sha256:base")


def lane(lane_id: str, group_id: str, path: str, generation: int = 1) -> WorkLane:
    return WorkLane(
        lane_id,
        group_id,
        "product",
        generation,
        f"writer-{lane_id}",
        ResourceSet((path,)),
        ("S1",),
    )


class Phase3CoordinationTests(unittest.TestCase):
    def test_parallel_assessment_requires_benefit_and_boundary(self) -> None:
        coordinator = WorkCoordinator()
        allowed = coordinator.assess(
            ParallelAssessmentInput(2, mechanical_write_separation=True, projected_parallel_cost=3, projected_serial_cost=8)
        )
        too_costly = coordinator.assess(
            ParallelAssessmentInput(2, mechanical_write_separation=True, projected_parallel_cost=8, projected_serial_cost=8)
        )
        unsafe = coordinator.assess(ParallelAssessmentInput(2, unknown_overlap=True))
        self.assertEqual("parallel_allowed", allowed.result)
        self.assertEqual("parallel_not_worthwhile", too_costly.result)
        self.assertEqual("parallel_unsafe", unsafe.result)

    def test_activation_submission_and_targeted_invalidation(self) -> None:
        coordinator = WorkCoordinator()
        coordinator.register_group(ModuleWorkGroup("group", "Module", ("lane",), ("S1",)))
        original = WorkLane("lane", "group", "product", 1, "writer", ResourceSet(("src/a.py",), ("shared",)), ("S1",))
        coordinator.register_lane(original)
        guard = ChangeGuard()
        assignment = guard.activate(original, BASE, "isolated_candidate")
        active = coordinator.activate("lane", assignment.boundary_id)
        submission = LaneSubmission("lane", 1, "writer", AUTHORITY, BASE.digest, {"src/a.py": "ok"}, True)
        coordinator.submit(submission)
        invalidated = coordinator.invalidate_dependents("shared")
        self.assertEqual("active", active.state)
        self.assertEqual(2, invalidated[0].generation)
        self.assertEqual("planned", invalidated[0].state)

    def test_cross_lane_request_never_grants_write(self) -> None:
        coordinator = WorkCoordinator()
        coordinator.register_group(ModuleWorkGroup("group", "Module", ("lane",), ("S1",)))
        current = lane("lane", "group", "src/a.py")
        coordinator.register_lane(current)
        coordinator.shared_owner("shared", "lane")
        decision = coordinator.route_cross_lane_request(
            CrossLaneChangeRequest("lane", "shared", "needed", "S1", "repro")
        )
        self.assertEqual("route_to_current_writer", decision.outcome)
        self.assertEqual(("lane",), decision.affected_lanes)

    def test_guard_rejects_late_or_mixed_scope_write(self) -> None:
        guard = ChangeGuard()
        current = lane("lane", "group", "src/a.py")
        assignment = guard.activate(current, BASE, "isolated_candidate")
        with self.assertRaisesRegex(ContractError, "mutation_blocked_resource"):
            guard.authorize_changes(
                assignment,
                current.resources,
                current.trusted_writer,
                {"src/a.py": "ok", "docs/protected.md": "bad"},
                Path.cwd(),
            )
        guard.fence("lane", 1)
        with self.assertRaisesRegex(ContractError, "mutation_blocked_generation"):
            guard.authorize_changes(
                assignment,
                current.resources,
                current.trusted_writer,
                {"src/a.py": "late"},
                Path.cwd(),
            )

    def test_handoff_requires_known_mutation_closure(self) -> None:
        guard = ChangeGuard()
        current = lane("lane", "group", "src/a.py")
        guard.activate(current, BASE, "isolated_candidate")
        outcome = guard.handoff(current, BASE, "isolated_candidate", False)
        self.assertEqual("handoff_recovery_required", outcome.outcome)
        self.assertIsNone(outcome.new_assignment)

    def test_central_admission_rejects_mixed_patch_as_whole(self) -> None:
        current = lane("lane", "group", "src/a.py")
        guard = ChangeGuard()
        assignment = guard.activate(current, BASE, "isolated_candidate")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("old", encoding="utf-8")
            from ddh.candidate import workspace_manifest_digest

            submission = LaneSubmission(
                "lane", 1, current.trusted_writer, AUTHORITY,
                workspace_manifest_digest(root),
                {"src/a.py": "new", "docs/x.md": "bad"}, True,
            )
            result = CentralIntegrator(guard).admit(
                root, root / "candidate", AUTHORITY, (current,), (assignment,),
                (submission,), ("lane",), ("src/**",),
            )
        self.assertEqual("rejected_scope_or_partition", result.outcome)
        self.assertIsNone(result.controller)

    def test_join_requires_every_writer_to_quiesce(self) -> None:
        guard = ChangeGuard()
        first = lane("a", "group", "src/a.py")
        second = lane("b", "group", "src/b.py")
        guard.activate(first, BASE, "isolated_candidate")
        guard.activate(second, BASE, "isolated_candidate")
        guard.begin_operation("b", 1, second.trusted_writer)
        with self.assertRaisesRegex(ContractError, "waiting_for_quiescence"):
            JoinBarrier(guard).ensure_quiescent((first, second))


if __name__ == "__main__":
    unittest.main()
