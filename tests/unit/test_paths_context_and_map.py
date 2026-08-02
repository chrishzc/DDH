import tempfile
import unittest
from pathlib import Path

from ddh.context import ContextCurator, ContextItem, ContextRequest
from ddh.contracts import ContractError
from ddh.paths import PathBoundaryError, normalize_repository_path
from ddh.system_map import (
    ImpactResolver,
    MapQuery,
    MapResult,
    StaticLiveSourceAdapter,
    StaticSystemMapAdapter,
)


def map_result(outcome: str, omitted: tuple[str, ...] = ()) -> MapResult:
    return MapResult(
        outcome,
        "repository",
        "main",
        "commit-1",
        "view-1",
        ("Workspace/PathNormalizer", "Workspace/ManifestLoader"),
        (("Workspace/ManifestLoader", "Workspace/PathNormalizer"),),
        (("src/path_normalizer.py", "Workspace/PathNormalizer"),),
        omitted,
    )


class PathTests(unittest.TestCase):
    def test_separator_and_parent_segments_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = normalize_repository_path(
                Path(directory),
                r".\src\package\..\package\module.py",
            )
        self.assertEqual("src/package/module.py", result.canonical_path)

    def test_workspace_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(PathBoundaryError, "workspace_escape"):
                normalize_repository_path(Path(directory), "../secret.txt")

    def test_absolute_and_unc_paths_are_typed_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(PathBoundaryError, "absolute_path_prohibited"):
                normalize_repository_path(root, "C:/secret.txt")
            with self.assertRaisesRegex(PathBoundaryError, "unsupported_path_class"):
                normalize_repository_path(root, "//server/share/file.txt")

    def test_symlink_escape_is_rejected_when_platform_supports_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "workspace"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            try:
                (root / "link").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(PathBoundaryError, "workspace_escape"):
                normalize_repository_path(root, "link/secret.txt")


class SystemMapTests(unittest.TestCase):
    def test_map_facts_are_consumed(self) -> None:
        result = map_result("usable_actual")
        resolver = ImpactResolver(
            StaticSystemMapAdapter(result),
            StaticLiveSourceAdapter(result),
        )
        closure = resolver.resolve(MapQuery("repository", "main", "commit-1", (), "scope"))
        self.assertTrue(closure.complete)
        self.assertIn("node:Workspace/PathNormalizer", closure.consumed_facts)
        self.assertFalse(closure.used_live_fallback)

    def test_partial_map_uses_bounded_fallback(self) -> None:
        partial = map_result("partial", ("Workspace/PathNormalizer",))
        live = StaticLiveSourceAdapter(map_result("usable_actual"))
        closure = ImpactResolver(StaticSystemMapAdapter(partial), live).resolve(
            MapQuery("repository", "main", "commit-1", (), "impact")
        )
        self.assertTrue(closure.complete)
        self.assertTrue(closure.used_live_fallback)
        self.assertEqual(partial.omitted_areas, live.requested_areas)

    def test_wrong_commit_fails_closed(self) -> None:
        wrong = MapResult(
            "usable_actual",
            "repository",
            "main",
            "other-commit",
            "view",
            (),
            (),
            (),
        )
        resolver = ImpactResolver(
            StaticSystemMapAdapter(wrong),
            StaticLiveSourceAdapter(wrong),
        )
        with self.assertRaisesRegex(ContractError, "view_mismatch"):
            resolver.resolve(MapQuery("repository", "main", "commit-1", (), "scope"))

    def test_unmapped_actual_change_uses_live_impact_fallback(self) -> None:
        indexed = map_result("usable_actual")
        live = StaticLiveSourceAdapter(
            MapResult(
                "usable_actual",
                "repository",
                "main",
                "commit-1",
                "live-view",
                indexed.nodes,
                indexed.relations,
                indexed.resource_bindings
                + (("src/new_module.py", "Workspace/PathNormalizer"),),
            )
        )
        resolver = ImpactResolver(StaticSystemMapAdapter(indexed), live)
        closure = resolver.resolve(
            MapQuery(
                "repository",
                "main",
                "commit-1",
                (),
                "actual_delta",
                changed_resources=("src/new_module.py",),
            )
        )
        self.assertTrue(closure.complete)
        self.assertEqual(("src/new_module.py",), live.requested_areas)


class ContextTests(unittest.TestCase):
    def test_context_deduplicates_unchanged_content(self) -> None:
        impact = ImpactResolver(
            StaticSystemMapAdapter(map_result("usable_actual")),
            StaticLiveSourceAdapter(map_result("usable_actual")),
        ).resolve(MapQuery("repository", "main", "commit-1", (), "scope"))
        item = ContextItem("one", "same content", "implementation")
        envelope = ContextCurator(1000).materialize((item, item), impact)
        self.assertEqual(1, len(envelope.items))

    def test_duplicate_request_does_not_charge_again(self) -> None:
        impact = ImpactResolver(
            StaticSystemMapAdapter(map_result("usable_actual")),
            StaticLiveSourceAdapter(map_result("usable_actual")),
        ).resolve(MapQuery("repository", "main", "commit-1", (), "scope"))
        curator = ContextCurator(1000)
        envelope = curator.materialize(
            (ContextItem("goal", "small", "implementation"),),
            impact,
        )
        disposition = curator.expand(
            envelope,
            ContextRequest("goal", "implementation", "needed", 1, 2),
            "small",
        )
        self.assertEqual("denied_duplicate", disposition.outcome)
        self.assertEqual(envelope.charged_tokens, disposition.envelope.charged_tokens)

    def test_ten_thousand_unrelated_records_are_not_ingested(self) -> None:
        impact = ImpactResolver(
            StaticSystemMapAdapter(map_result("usable_actual")),
            StaticLiveSourceAdapter(map_result("usable_actual")),
        ).resolve(MapQuery("repository", "main", "commit-1", (), "scope"))
        unrelated = tuple(
            ContextItem(f"dirty:{index}", f"digest-{index}", "inventory")
            for index in range(10_000)
        )
        required = ContextItem("goal", "repair paths", "implementation")
        envelope = ContextCurator(1000).materialize(
            (required, *unrelated),
            impact,
            required_selectors=("goal",),
        )
        self.assertEqual(("goal",), tuple(item.selector for item in envelope.items))

    def test_irrelevant_and_duplicate_content_requests_are_denied(self) -> None:
        impact = ImpactResolver(
            StaticSystemMapAdapter(map_result("usable_actual")),
            StaticLiveSourceAdapter(map_result("usable_actual")),
        ).resolve(MapQuery("repository", "main", "commit-1", (), "scope"))
        curator = ContextCurator(1000)
        envelope = curator.materialize(
            (ContextItem("goal", "small", "implementation"),),
            impact,
        )
        duplicate = curator.expand(
            envelope,
            ContextRequest("alias", "implementation", "needed", 1, 2),
            "small",
        )
        irrelevant = curator.expand(
            envelope,
            ContextRequest("logs", "inventory", "maybe", 1, 1),
            "new",
        )
        self.assertEqual("denied_duplicate", duplicate.outcome)
        self.assertEqual("denied_irrelevant", irrelevant.outcome)


if __name__ == "__main__":
    unittest.main()
