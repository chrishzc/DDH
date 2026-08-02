import json
import sys
import tempfile
import unittest
from pathlib import Path

from ddh.agent_driver import AgentResult, WorkRequest
from ddh.confirmation import (
    authority_for_document,
    create_confirmation,
    expected_confirmation_phrase,
)
from ddh.context import ContextRequest
from ddh.contracts import ContractError
from ddh.runtime import Phase1Runtime, RuntimeRequest
from ddh.system_map import (
    ImpactResolver,
    MapResult,
    StaticLiveSourceAdapter,
    StaticSystemMapAdapter,
)
from ddh.telemetry import JsonlTelemetry
from ddh.test_auditor import VerificationAsset
from ddh.verification import VerificationResult, VerificationRunner


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = (
    REPOSITORY_ROOT
    / "tests"
    / "fixtures"
    / "portable_workspace"
    / "workspace"
)

PARTIAL_REPAIR = """\
def normalize_path(workspace_root, user_path: str, platform_profile: str) -> str:
    return user_path.replace("\\\\", "/")
"""

COMPLETE_REPAIR = """\
import re
from pathlib import Path


WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:/")


def normalize_path(
    workspace_root: Path,
    user_path: str,
    platform_profile: str,
) -> str:
    normalized = user_path.replace("\\\\", "/")
    if normalized.startswith("//"):
        raise ValueError("unsupported_path_class")
    if normalized.startswith("/") or WINDOWS_ABSOLUTE.match(normalized):
        raise ValueError("absolute_path_prohibited")
    parts = []
    for part in normalized.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise ValueError("workspace_escape")
            parts.pop()
            continue
        parts.append(part)
    canonical = "/".join(parts)
    root = workspace_root.resolve()
    candidate = (root / Path(canonical)).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise ValueError("workspace_escape") from error
    return canonical
"""


def workload_document() -> dict[str, object]:
    return {
        "specification_id": "PORTABLE-WORKSPACE-WP",
        "version": "1.0.0",
        "risk_class": "L1",
        "goal": "Repair cross-platform repository path normalization.",
        "expected_behavior": [
            "Normalize separators and parent segments.",
            "Reject workspace escape, absolute and UNC inputs.",
        ],
        "write_scope": ["src/path_normalizer.py"],
        "prohibitions": ["modify_manifest_loader", "external_side_effects"],
        "acceptance_scenarios": ["PATH-001", "PATH-002"],
        "budgets": {
            "agent_attempts": 3,
            "effective_context_tokens": 10000,
        },
        "selected_nodes": ["PortableWorkspace/PathNormalizer"],
    }


class RepairingAgent:
    def __init__(self) -> None:
        self.calls = 0
        self.last_request: WorkRequest | None = None

    def pull(self, request: WorkRequest) -> AgentResult:
        self.calls += 1
        self.last_request = request
        repair = PARTIAL_REPAIR if request.candidate_generation == 1 else COMPLETE_REPAIR
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": repair},
            ("src/manifest_loader.py",),
            True,
        )


class TimeoutOnceRepairingAgent(RepairingAgent):
    def __init__(self) -> None:
        super().__init__()
        self.timeout_injected = False

    def pull(self, request: WorkRequest) -> AgentResult:
        if not self.timeout_injected:
            self.timeout_injected = True
            raise TimeoutError("transient host timeout")
        return super().pull(request)


class ScopeChangeAgent:
    def pull(self, request: WorkRequest) -> AgentResult:
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "scope_change_required",
            {"src/manifest_loader.py": "required contract repair"},
        )


class ContextRequestingAgent:
    def __init__(self) -> None:
        self.calls = 0

    def pull(self, request: WorkRequest) -> AgentResult:
        self.calls += 1
        if not request.context_dispositions:
            return AgentResult(
                request.invocation_id,
                request.specification,
                request.candidate_generation,
                "context_request",
                {},
                context_request=ContextRequest(
                    "src/manifest_loader.py",
                    "impact",
                    "downstream canonical path consumer",
                    5,
                    20,
                ),
            )
        return AgentResult(
            request.invocation_id,
            request.specification,
            request.candidate_generation,
            "patch_proposal",
            {"src/path_normalizer.py": COMPLETE_REPAIR},
        )


class FixtureContextSource:
    def __init__(self) -> None:
        self.reads: list[str] = []

    def read(self, selector: str, purpose: str) -> str | None:
        self.reads.append(selector)
        path = FIXTURE_ROOT / selector
        return path.read_text(encoding="utf-8") if path.is_file() else None


class FailOnceRunner:
    def __init__(self) -> None:
        self.calls = 0
        self.injected_failures = 0
        self.delegate = VerificationRunner()

    def run(self, plan) -> VerificationResult:
        self.calls += 1
        if self.injected_failures == 0:
            self.injected_failures += 1
            return VerificationResult(
                plan.plan_id,
                plan.candidate,
                plan.asset_digest,
                "failed",
                "undetermined",
                "incomplete",
                "runner_start_failed",
                True,
                None,
                0,
                "",
                "",
                False,
            )
        return self.delegate.run(plan)


class WorkspaceAssetProvider:
    def build(self, candidate):
        asset = VerificationAsset(
            "portable-workspace-acceptance",
            1,
            ("PATH-001", "PATH-002"),
            (
                "separators normalize",
                "parent segments collapse",
                "unsafe path classes reject",
            ),
            (
                "src/package/module.py",
                "workspace_escape",
                "absolute_path_prohibited",
                "unsupported_path_class",
            ),
            (),
            6,
            (
                "windows_separator",
                "parent_segment",
                "workspace_escape",
                "absolute_path",
                "unc_path",
                "symlink_escape",
            ),
            (),
            candidate.reference,
            (
                sys.executable,
                "-m",
                "ddh.unittest_runner",
                "tests/acceptance",
            ),
            "fixed_command",
        )
        return ((None, asset),)


def partial_map() -> MapResult:
    return MapResult(
        "partial",
        "portable-workspace",
        "main",
        "fixture-commit-001",
        "fixture-view-partial",
        ("PortableWorkspace/PathNormalizer",),
        (),
        (("src/path_normalizer.py", "PortableWorkspace/PathNormalizer"),),
        ("PortableWorkspace/ManifestLoader",),
    )


def live_map() -> MapResult:
    return MapResult(
        "usable_actual",
        "portable-workspace",
        "main",
        "fixture-commit-001",
        "live-fallback-001",
        (
            "PortableWorkspace/PathNormalizer",
            "PortableWorkspace/ManifestLoader",
        ),
        (
            (
                "PortableWorkspace/ManifestLoader",
                "PortableWorkspace/PathNormalizer",
            ),
        ),
        (
            ("src/path_normalizer.py", "PortableWorkspace/PathNormalizer"),
            ("src/manifest_loader.py", "PortableWorkspace/ManifestLoader"),
        ),
    )


class Phase1VerticalSliceTests(unittest.TestCase):
    def test_repair_retest_completion_and_portable_bundle(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        original_product = (FIXTURE_ROOT / "src" / "path_normalizer.py").read_bytes()
        original_dirty = (FIXTURE_ROOT / "notes" / "user-local-change.txt").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            invocation_root = Path(directory)
            live = StaticLiveSourceAdapter(live_map())
            map_adapter = StaticSystemMapAdapter(partial_map())
            agent = TimeoutOnceRepairingAgent()
            runtime = Phase1Runtime(
                ImpactResolver(map_adapter, live),
                agent,
                WorkspaceAssetProvider(),
                JsonlTelemetry(invocation_root / "events.jsonl"),
            )
            runner = FailOnceRunner()
            runtime._runner = runner
            request = RuntimeRequest(
                document,
                confirmation,
                FIXTURE_ROOT,
                invocation_root,
                "portable-workspace",
                "main",
                "fixture-commit-001",
                "stable-reference-invocation",
            )
            outcome = runtime.execute(request)
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual("work_package_completed", outcome.completion.reason_code)
            self.assertIsNotNone(outcome.bundle_path)
            self.assertTrue((outcome.bundle_path / "candidate-manifest.json").is_file())
            self.assertTrue((outcome.bundle_path / "changes.patch").is_file())
            self.assertTrue((outcome.bundle_path / "typed-verification-result.json").is_file())
            self.assertEqual(
                original_dirty,
                (outcome.candidate.root / "notes" / "user-local-change.txt").read_bytes(),
            )
            self.assertEqual(
                ("PortableWorkspace/ManifestLoader",),
                live.requested_areas,
            )
            self.assertEqual(
                ("src/path_normalizer.py",),
                map_adapter.queries[-1].changed_resources,
            )
            self.assertTrue(agent.timeout_injected)
            self.assertTrue(agent.last_request.candidate_baseline_digest.startswith("sha256:"))
            self.assertEqual("L1", agent.last_request.risk_class)
            self.assertIn("external_side_effects", agent.last_request.prohibitions)
            self.assertIn("scope_change", agent.last_request.escalation_conditions)
            self.assertEqual(1, runner.injected_failures)
            state_path = invocation_root / "state" / f"{outcome.invocation_id}.json"
            self.assertEqual(
                "terminal",
                json.loads(state_path.read_text())["payload"]["stage"],
            )
            agent_calls = agent.calls
            map_queries = len(map_adapter.queries)
            replayed = runtime.execute(request)
            self.assertTrue(replayed.completion.work_package_completed)
            self.assertEqual(agent_calls, agent.calls)
            self.assertEqual(map_queries, len(map_adapter.queries))
            changed_document = {**document, "goal": "Different authority."}
            changed_authority = authority_for_document(changed_document)
            changed_confirmation = create_confirmation(
                changed_document,
                expected_confirmation_phrase(changed_authority),
                "trusted_host_ui",
            )
            with self.assertRaisesRegex(ContractError, "identity_digest_conflict"):
                runtime.execute(
                    RuntimeRequest(
                        changed_document,
                        changed_confirmation,
                        FIXTURE_ROOT,
                        invocation_root,
                        "portable-workspace",
                        "main",
                        "fixture-commit-001",
                        "stable-reference-invocation",
                    )
                )
        self.assertEqual(original_product, (FIXTURE_ROOT / "src" / "path_normalizer.py").read_bytes())
        self.assertEqual(original_dirty, (FIXTURE_ROOT / "notes" / "user-local-change.txt").read_bytes())

    def test_required_read_only_change_produces_revision_report(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        with tempfile.TemporaryDirectory() as directory:
            invocation_root = Path(directory)
            runtime = Phase1Runtime(
                ImpactResolver(
                    StaticSystemMapAdapter(live_map()),
                    StaticLiveSourceAdapter(live_map()),
                ),
                ScopeChangeAgent(),
                WorkspaceAssetProvider(),
                JsonlTelemetry(invocation_root / "events.jsonl"),
            )
            outcome = runtime.execute(
                RuntimeRequest(
                    document,
                    confirmation,
                    FIXTURE_ROOT,
                    invocation_root,
                    "portable-workspace",
                    "main",
                    "fixture-commit-001",
                )
            )
            self.assertEqual("scope_change_required", outcome.completion.reason_code)
            self.assertIsNotNone(outcome.exception_report)
            self.assertEqual(
                ("src/manifest_loader.py",),
                outcome.exception_report.requested_paths,
            )
            self.assertFalse(outcome.completion.work_package_completed)

    def test_context_request_uses_trusted_source_and_continues(self) -> None:
        document = workload_document()
        authority = authority_for_document(document)
        confirmation = create_confirmation(
            document,
            expected_confirmation_phrase(authority),
            "trusted_host_ui",
        )
        with tempfile.TemporaryDirectory() as directory:
            invocation_root = Path(directory)
            agent = ContextRequestingAgent()
            context_source = FixtureContextSource()
            runtime = Phase1Runtime(
                ImpactResolver(
                    StaticSystemMapAdapter(live_map()),
                    StaticLiveSourceAdapter(live_map()),
                ),
                agent,
                WorkspaceAssetProvider(),
                JsonlTelemetry(invocation_root / "events.jsonl"),
                context_source,
            )
            outcome = runtime.execute(
                RuntimeRequest(
                    document,
                    confirmation,
                    FIXTURE_ROOT,
                    invocation_root,
                    "portable-workspace",
                    "main",
                    "fixture-commit-001",
                )
            )
            self.assertTrue(outcome.completion.work_package_completed)
            self.assertEqual(2, agent.calls)
            self.assertEqual(
                ["src/manifest_loader.py"],
                context_source.reads,
            )


if __name__ == "__main__":
    unittest.main()
