import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ddh.candidate import AdmissionRejected, CandidateController
from ddh.contracts import CandidateReference, ContractError
from ddh.test_auditor import TestAuditor, VerificationAsset


def asset(
    candidate: CandidateReference,
    assertions: tuple[str, ...] = ("canonical path matches",),
    expected_values: tuple[str, ...] = ("src/module.py",),
    cases: tuple[str, ...] = ("windows_separator", "workspace_escape"),
    markers: tuple[str, ...] = (),
    known_bad_probes: tuple[str, ...] = (),
) -> VerificationAsset:
    return VerificationAsset(
        "workspace-acceptance",
        1,
        ("PATH-001",),
        assertions,
        expected_values,
        (("case_count", "2"),),
        len(cases),
        cases,
        markers,
        candidate,
        ("python", "-m", "unittest"),
        "fixed_command",
        known_bad_probes,
    )


class CandidateTests(unittest.TestCase):
    def test_materialization_preserves_original_and_excludes_git(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / ".git").mkdir()
            (source / ".git" / "config").write_text("private")
            (source / "user.txt").write_text("dirty")
            controller = CandidateController(
                source,
                root / "candidate",
                ("src/**",),
            )
            controller.materialize()
            self.assertEqual("dirty", (controller.root / "user.txt").read_text())
            self.assertFalse((controller.root / ".git").exists())

    def test_mixed_change_is_rejected_as_one_unit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            (source / "src").mkdir(parents=True)
            (source / "src" / "module.py").write_text("old")
            controller = CandidateController(source, root / "candidate", ("src/**",))
            controller.materialize()
            changes = {"src/module.py": "new", "notes/outside.txt": "invalid"}
            with self.assertRaises(AdmissionRejected) as captured:
                controller.admit(changes)
            self.assertIn("notes/outside.txt", captured.exception.invalid_paths)
            self.assertEqual("old", (controller.root / "src" / "module.py").read_text())
            self.assertEqual(changes, controller.rejected_private_delta)

    def test_frozen_candidate_detects_late_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            (source / "src").mkdir(parents=True)
            (source / "src" / "module.py").write_text("old")
            controller = CandidateController(source, root / "candidate", ("src/**",))
            controller.materialize()
            controller.admit({"src/module.py": "new"})
            frozen = controller.freeze()
            controller.assert_current(frozen.reference)
            (controller.root / "src" / "module.py").write_text("late")
            with self.assertRaisesRegex(ContractError, "changed_after_freeze"):
                controller.assert_current(frozen.reference)

    def test_rename_is_detected_by_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            (source / "src").mkdir(parents=True)
            (source / "src" / "old.py").write_text("same")
            controller = CandidateController(source, root / "candidate", ("src/**",))
            controller.materialize()
            changes = controller.admit({"src/old.py": None, "src/new.py": "same"})
            self.assertEqual((("src/old.py", "src/new.py"),), changes.renamed)


class TestAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candidate = CandidateReference("candidate", 1, "sha256:digest")
        self.auditor = TestAuditor()

    def test_independent_admission_accepts_non_weakened_asset(self) -> None:
        baseline = asset(self.candidate)
        proposed = asset(
            self.candidate,
            assertions=("canonical path matches", "escape is rejected"),
            cases=("windows_separator", "workspace_escape", "known_bad_escape"),
            known_bad_probes=("known_bad_escape",),
        )
        admission = self.auditor.audit(
            baseline,
            proposed,
            ("PATH-001",),
            independent_reviewer=True,
        )
        self.assertEqual("admitted", admission.outcome)

    def test_assertion_deletion_is_rejected(self) -> None:
        baseline = asset(
            self.candidate,
            assertions=("canonical path matches", "escape is rejected"),
        )
        with self.assertRaisesRegex(ContractError, "weakening_rejected"):
            self.auditor.audit(
                baseline,
                asset(self.candidate),
                ("PATH-001",),
                independent_reviewer=True,
            )

    def test_skip_marker_is_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "weakening_rejected"):
            self.auditor.audit(
                asset(self.candidate),
                asset(self.candidate, markers=("skip",)),
                ("PATH-001",),
                independent_reviewer=True,
            )

    def test_self_admission_is_rejected(self) -> None:
        with self.assertRaisesRegex(ContractError, "independent_test_admission"):
            self.auditor.audit(
                None,
                asset(self.candidate),
                ("PATH-001",),
                independent_reviewer=False,
            )

    def test_repaired_asset_requires_an_executed_known_bad_probe(self) -> None:
        baseline = asset(self.candidate)
        repaired_without_probe = asset(
            self.candidate,
            assertions=("canonical path matches", "new oracle"),
        )
        with self.assertRaisesRegex(ContractError, "repair_probe_required"):
            self.auditor.audit(
                baseline,
                repaired_without_probe,
                ("PATH-001",),
                independent_reviewer=True,
            )

    def test_candidate_rebinding_alone_is_not_asset_repair(self) -> None:
        baseline = asset(CandidateReference("old", 1, "sha256:old"))
        proposed = asset(CandidateReference("current", 2, "sha256:current"))
        admission = self.auditor.audit(
            baseline,
            proposed,
            ("PATH-001",),
            independent_reviewer=True,
        )
        self.assertEqual("admitted", admission.outcome)

    def test_all_mechanical_weakening_dimensions_are_rejected(self) -> None:
        baseline = asset(
            self.candidate,
            assertions=("canonical path matches", "escape rejects"),
            cases=("separator", "escape", "absolute"),
        )
        weakened = (
            replace(baseline, assertions=("canonical path matches",)),
            replace(baseline, expected_values=("any path",)),
            replace(baseline, thresholds=(("case_count", "1"),)),
            replace(baseline, fixture_case_count=2),
            replace(baseline, cases=("separator", "escape")),
            replace(baseline, markers=("xfail",)),
        )
        for proposed in weakened:
            with self.subTest(proposed=proposed):
                with self.assertRaisesRegex(ContractError, "weakening_rejected"):
                    self.auditor.audit(
                        baseline,
                        proposed,
                        ("PATH-001",),
                        independent_reviewer=True,
                    )


if __name__ == "__main__":
    unittest.main()
