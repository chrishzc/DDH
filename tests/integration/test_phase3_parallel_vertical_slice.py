import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from ddh.agent_driver import AgentResult, WorkRequest
from ddh.confirmation import authority_for_document, create_confirmation, expected_confirmation_phrase
from ddh.coordination import ModuleWorkGroup, ResourceSet, WorkLane
from ddh.runtime import ParallelRuntimeRequest, ParallelWorkPlan, Phase3Runtime, RuntimeRequest
from ddh.system_map import ImpactResolver, MapResult, StaticLiveSourceAdapter, StaticSystemMapAdapter
from ddh.telemetry import JsonlTelemetry
from ddh.test_auditor import VerificationAsset


def workload_document() -> dict[str, object]:
    return {
        "specification_id": "P3-WORKSPACE-001",
        "version": "1.0.0",
        "risk_class": "L2",
        "goal": "Build the portable workspace index from validated manifest paths.",
        "expected_behavior": ["canonical paths", "deterministic index", "duplicate rejection"],
        "write_scope": ["src/**", "tests/**"],
        "prohibitions": ["docs/**", ".git/**"],
        "acceptance_scenarios": ["PATH-001", "MANIFEST-001", "INDEX-001"],
        "budgets": {"agent_attempts": 4, "effective_context_tokens": 20000},
        "selected_nodes": ["PortableWorkspace"],
    }


@dataclass
class LaneDriver:
    changes: dict[str, str]

    def pull(self, request: WorkRequest) -> AgentResult:
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "isolated_candidate",
            self.changes,
            tuple(self.changes),
            True,
        )


class MechanicalLaneVerifier:
    def __init__(self) -> None:
        self.seen: list[str] = []

    def verify(self, lane, submission) -> bool:
        self.seen.append(lane.lane_id)
        return bool(submission.changes)


class IntegratedAssetProvider:
    def build(self, candidate):
        asset = VerificationAsset(
            "portable-workspace-subsystem", 1,
            ("PATH-001", "MANIFEST-001", "INDEX-001"),
            ("integrated subsystem passes",), ("deterministic",), (), 3,
            ("normal", "escape", "duplicate"), (), candidate.reference,
            (sys.executable, "-c", "from pathlib import Path; assert (Path('src') / 'path_normalizer.py').is_file(); assert (Path('src') / 'manifest_loader.py').is_file(); assert (Path('src') / 'manifest_index.py').is_file()"),
            "fixed_command", declared_duration_seconds=1,
            historical_p95_seconds=1, reliable_estimate_seconds=1,
        )
        return ((None, asset),)


def map_result() -> MapResult:
    bindings = (
        ("src/path_normalizer.py", "PortableWorkspace/PathNormalizer"),
        ("src/manifest_loader.py", "PortableWorkspace/ManifestLoader"),
        ("src/manifest_index.py", "PortableWorkspace/ManifestIndex"),
        ("tests/path_normalizer_acceptance.py", "PortableWorkspace/PathNormalizer"),
        ("tests/manifest_loader_acceptance.py", "PortableWorkspace/ManifestLoader"),
        ("tests/manifest_index_acceptance.py", "PortableWorkspace/ManifestIndex"),
        ("tests/portable_workspace_subsystem_acceptance.py", "PortableWorkspace"),
    )
    return MapResult(
        "usable_actual", "portable-workspace", "main", "fixture-commit-3",
        "fixture-view", ("PortableWorkspace",),
        (("PortableWorkspace/PathNormalizer", "PortableWorkspace/ManifestLoader"),), bindings,
    )


def plan() -> ParallelWorkPlan:
    modules = (
        ("path", "PathNormalizer", "src/path_normalizer.py", "tests/path_normalizer_acceptance.py"),
        ("loader", "ManifestLoader", "src/manifest_loader.py", "tests/manifest_loader_acceptance.py"),
        ("index", "ManifestIndex", "src/manifest_index.py", "tests/manifest_index_acceptance.py"),
    )
    groups = []
    lanes = []
    for identifier, node, product_path, test_path in modules:
        product_id = f"{identifier}-product"
        test_id = f"{identifier}-acceptance"
        groups.append(ModuleWorkGroup(identifier, f"PortableWorkspace/{node}", (product_id, test_id), (f"{identifier.upper()}-001",)))
        lanes.append(WorkLane(product_id, identifier, "product", 1, f"writer-{product_id}", ResourceSet((product_path,)), ("PATH-001", "MANIFEST-001", "INDEX-001")))
        lanes.append(WorkLane(test_id, identifier, "acceptance", 1, f"writer-{test_id}", ResourceSet((test_path,)), ("PATH-001", "MANIFEST-001", "INDEX-001")))
    groups.append(ModuleWorkGroup("subsystem", "PortableWorkspace", ("subsystem-acceptance",), ("PATH-001", "MANIFEST-001", "INDEX-001")))
    lanes.append(WorkLane("subsystem-acceptance", "subsystem", "subsystem_acceptance", 1, "writer-subsystem-acceptance", ResourceSet(("tests/portable_workspace_subsystem_acceptance.py",)), ("PATH-001", "MANIFEST-001", "INDEX-001")))
    return ParallelWorkPlan(tuple(groups), tuple(lanes), tuple(lane.lane_id for lane in lanes), 3, 9)


class Phase3ParallelVerticalSliceTests(unittest.TestCase):
    def test_three_modules_construct_product_and_tests_asynchronously_then_join(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(document, expected_confirmation_phrase(authority), "trusted_host_ui")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            drivers = {
                "path-product": LaneDriver({"src/path_normalizer.py": "VALUE = 'path'\n"}),
                "path-acceptance": LaneDriver({"tests/path_normalizer_acceptance.py": "assert True\n"}),
                "loader-product": LaneDriver({"src/manifest_loader.py": "VALUE = 'loader'\n"}),
                "loader-acceptance": LaneDriver({"tests/manifest_loader_acceptance.py": "assert True\n"}),
                "index-product": LaneDriver({"src/manifest_index.py": "VALUE = 'index'\n"}),
                "index-acceptance": LaneDriver({"tests/manifest_index_acceptance.py": "assert True\n"}),
                "subsystem-acceptance": LaneDriver({"tests/portable_workspace_subsystem_acceptance.py": "assert True\n"}),
            }
            verifier = MechanicalLaneVerifier()
            result = map_result()
            map_adapter = StaticSystemMapAdapter(result)
            runtime = Phase3Runtime(
                ImpactResolver(map_adapter, StaticLiveSourceAdapter(result)),
                drivers,
                IntegratedAssetProvider(),
                verifier,
                JsonlTelemetry(root / "events.jsonl"),
            )
            request = ParallelRuntimeRequest(
                RuntimeRequest(document, confirmation, source, root / "run", "portable-workspace", "main", "fixture-commit-3", "phase3-fork-join"),
                plan(),
            )
            outcome = runtime.execute(request)
            self.assertEqual("parallel_allowed", outcome.parallel_result)
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual("subsystem_integrated", outcome.completion.subsystem_integrated)
            self.assertEqual("not_evaluated", outcome.completion.domain_accepted)
            self.assertEqual("not_evaluated", outcome.completion.release_candidate)
            self.assertEqual(7, len(outcome.lane_submissions))
            self.assertEqual(7, len(verifier.seen))
            self.assertGreaterEqual(len(map_adapter.queries), 2)
            self.assertTrue(outcome.consumed_impact_facts)

    def test_parallel_cost_fallback_continues_through_serial_workers(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(document, expected_confirmation_phrase(authority), "trusted_host_ui")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            expensive = plan()
            expensive = ParallelWorkPlan(expensive.groups, expensive.lanes, expensive.integration_order, 9, 3)
            result = map_result()
            drivers = {
                "path-product": LaneDriver({"src/path_normalizer.py": "VALUE = 'path'\n"}),
                "path-acceptance": LaneDriver({"tests/path_normalizer_acceptance.py": "assert True\n"}),
                "loader-product": LaneDriver({"src/manifest_loader.py": "VALUE = 'loader'\n"}),
                "loader-acceptance": LaneDriver({"tests/manifest_loader_acceptance.py": "assert True\n"}),
                "index-product": LaneDriver({"src/manifest_index.py": "VALUE = 'index'\n"}),
                "index-acceptance": LaneDriver({"tests/manifest_index_acceptance.py": "assert True\n"}),
                "subsystem-acceptance": LaneDriver({"tests/portable_workspace_subsystem_acceptance.py": "assert True\n"}),
            }
            runtime = Phase3Runtime(
                ImpactResolver(StaticSystemMapAdapter(result), StaticLiveSourceAdapter(result)),
                drivers, IntegratedAssetProvider(), MechanicalLaneVerifier(), JsonlTelemetry(root / "events.jsonl"),
            )
            outcome = runtime.execute(ParallelRuntimeRequest(RuntimeRequest(document, confirmation, source, root / "run", "portable-workspace", "main", "fixture-commit-3", "phase3-cost"), expensive))
            self.assertEqual("parallel_not_worthwhile", outcome.parallel_result)
            self.assertTrue(outcome.completion.work_package_completed)


if __name__ == "__main__":
    unittest.main()
