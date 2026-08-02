import sys
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from ddh.candidate import ChangeSet, FrozenCandidate
from ddh.completion import CompletionJudge
from ddh.contracts import CandidateReference
from ddh.contracts import ContractError
from ddh.system_map import ImpactClosure
from ddh.test_auditor import AssetAdmission, VerificationAsset
from ddh.verification import (
    ExecutionPlan,
    FixedCommandAdapter,
    PytestAdapter,
    VerificationRunner,
    adaptive_timeout_seconds,
)


def candidate(root: Path) -> FrozenCandidate:
    reference = CandidateReference("candidate", 1, "sha256:digest")
    return FrozenCandidate(reference, root, (), (), ChangeSet((), (), (), ()))


def verification_asset(reference: CandidateReference, command: tuple[str, ...]) -> VerificationAsset:
    return VerificationAsset(
        "asset",
        1,
        ("SCENARIO",),
        ("assertion",),
        ("expected",),
        (),
        1,
        ("case",),
        (),
        reference,
        command,
        "fixed_command",
    )


class VerificationTests(unittest.TestCase):
    def test_sixty_second_estimate_is_not_given_thirty_second_deadline(self) -> None:
        self.assertEqual(150.0, adaptive_timeout_seconds(60, None, None))
        self.assertEqual(600.0, adaptive_timeout_seconds(None, None, None))

    def test_fixed_command_passes_with_typed_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", "print('ok')"),
            )
            plan = FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            result = VerificationRunner().run(plan)
            self.assertEqual("passed", result.acceptance_outcome)
            self.assertEqual("verification_passed", result.reason_code)

    def test_output_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", "print('x' * 1000)"),
            )
            plan = FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            result = VerificationRunner(stdout_limit=64).run(plan)
            self.assertTrue(result.output_truncated)
            self.assertLessEqual(len(result.stdout.encode()), 64)

    def test_multibyte_output_respects_byte_ceiling(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (
                    sys.executable,
                    "-c",
                    "import sys; sys.stdout.buffer.write('界'.encode('utf-8') * 1000)",
                ),
            )
            plan = FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            result = VerificationRunner(stdout_limit=65).run(plan)
            self.assertTrue(result.output_truncated)
            self.assertLessEqual(len(result.stdout.encode("utf-8")), 65)

    def test_timeout_terminates_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", "import time; time.sleep(30)"),
            )
            plan = FixedCommandAdapter().build_plan(asset, frozen.root, 0.1)
            result = VerificationRunner(drain_grace_seconds=2).run(plan)
            self.assertEqual("verification_timeout", result.reason_code)
            self.assertTrue(result.retryable)

    def test_timeout_terminates_child_process_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started_marker = root / "child-started.txt"
            marker = root / "child-survived.txt"
            child = (
                "import pathlib,time; "
                f"pathlib.Path({str(started_marker)!r}).write_text('started'); "
                "time.sleep(0.6); "
                f"pathlib.Path({str(marker)!r}).write_text('alive')"
            )
            parent = (
                "import subprocess,sys,time; "
                f"subprocess.Popen([sys.executable,'-c',{child!r}]); "
                "time.sleep(30)"
            )
            frozen = candidate(root)
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", parent),
            )
            plan = FixedCommandAdapter().build_plan(asset, frozen.root, 0.3)
            result = VerificationRunner(drain_grace_seconds=2).run(plan)
            time.sleep(0.8)
            self.assertEqual("verification_timeout", result.reason_code)
            self.assertTrue(started_marker.exists())
            self.assertFalse(marker.exists())

    def test_pytest_adapter_uses_module_direct_argv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(frozen.reference, ("tests/test_example.py",))
            asset = VerificationAsset(**{**asset.__dict__, "adapter_id": "pytest"})
            plan = PytestAdapter().build_plan(asset, frozen.root, 10)
            self.assertEqual((sys.executable, "-m", "pytest"), plan.argv[:3])

    def test_fixed_command_rejects_generic_shell(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(frozen.reference, ("cmd.exe", "/c", "echo bad"))
            with self.assertRaisesRegex(ContractError, "generic_shell_executor"):
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)

    def test_missing_executable_is_runner_failure_not_product_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                ("definitely-missing-ddh-executable",),
            )
            result = VerificationRunner().run(
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            )
            self.assertEqual("runner_start_failed", result.reason_code)
            self.assertEqual("undetermined", result.acceptance_outcome)
            self.assertEqual("incomplete", result.verification_completeness)

    def test_pytest_no_tests_exit_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            plan = ExecutionPlan(
                "plan",
                frozen.reference,
                "sha256:asset",
                "pytest",
                (sys.executable, "-c", "raise SystemExit(5)"),
                frozen.root,
                10,
            )
            result = VerificationRunner().run(plan)
            self.assertEqual("required_tests_not_collected", result.reason_code)
            self.assertEqual("incomplete", result.verification_completeness)

    def test_reserved_skip_exit_is_incomplete_for_fixed_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", "raise SystemExit(125)"),
            )
            result = VerificationRunner().run(
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            )
            self.assertEqual("required_tests_skipped", result.reason_code)
            self.assertEqual("undetermined", result.acceptance_outcome)
            self.assertEqual("incomplete", result.verification_completeness)

    def test_unittest_runner_converts_skip_to_incomplete_exit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_required.py").write_text(
                "import unittest\n"
                "class RequiredTest(unittest.TestCase):\n"
                "    @unittest.skip('unavailable')\n"
                "    def test_required(self): pass\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                (sys.executable, "-m", "ddh.unittest_runner", str(root)),
                capture_output=True,
                check=False,
            )
            self.assertEqual(125, completed.returncode)


class CompletionTests(unittest.TestCase):
    def test_only_work_package_completion_is_published(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                (sys.executable, "-c", "raise SystemExit(0)"),
            )
            admission = AssetAdmission(asset, "admitted", "asset_current", True)
            result = VerificationRunner().run(
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            )
            impact = ImpactClosure(
                ("Workspace/PathNormalizer",),
                (),
                ("node:Workspace/PathNormalizer",),
                False,
                True,
            )
            decision = CompletionJudge().evaluate(
                frozen,
                impact,
                (admission,),
                (result,),
            )
            self.assertTrue(decision.work_package_completed)
            self.assertEqual("not_evaluated", decision.subsystem_integrated)
            self.assertEqual("not_evaluated", decision.domain_accepted)
            self.assertEqual("not_evaluated", decision.release_candidate)

    def test_wrong_candidate_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            other = CandidateReference("other", 1, "sha256:other")
            asset = verification_asset(other, (sys.executable, "-c", ""))
            admission = AssetAdmission(asset, "admitted", "asset_current", True)
            result = VerificationRunner().run(
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            )
            impact = ImpactClosure(("node",), (), ("node:node",), False, True)
            decision = CompletionJudge().evaluate(
                frozen,
                impact,
                (admission,),
                (result,),
            )
            self.assertEqual("verification_wrong_subject", decision.reason_code)

    def test_runner_failure_is_not_sent_to_product_repair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen = candidate(Path(directory))
            asset = verification_asset(
                frozen.reference,
                ("definitely-missing-ddh-executable",),
            )
            admission = AssetAdmission(asset, "admitted", "asset_current", True)
            result = VerificationRunner().run(
                FixedCommandAdapter().build_plan(asset, frozen.root, 10)
            )
            impact = ImpactClosure(("node",), (), ("node:node",), False, True)
            decision = CompletionJudge().evaluate(
                frozen,
                impact,
                (admission,),
                (result,),
            )
            self.assertEqual(
                "required_verification_incomplete",
                decision.reason_code,
            )
            self.assertEqual("blocked", decision.terminal_state)
            self.assertEqual("undetermined", decision.acceptance_outcome)


if __name__ == "__main__":
    unittest.main()
