import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def run_validator(path: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        (sys.executable, str(path)),
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, json.loads(completed.stdout)


class Phase3SpecificationContractTests(unittest.TestCase):
    def test_exact_phase3_package_still_validates(self) -> None:
        validator = (
            REPOSITORY_ROOT
            / "docs"
            / "semantic-specifications"
            / "ddh-phase-3"
            / "draft"
            / "validation"
            / "validate_phase3_spec.py"
        )
        completed, result = run_validator(validator)
        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertEqual("passed", result["acceptance_outcome"])
        self.assertEqual(43, result["checked_scenarios"])
        self.assertEqual(12, result["checked_capability_groups"])
        self.assertEqual(0, result["total_error_count"])

    def test_earlier_phase_packages_still_validate(self) -> None:
        validators = (
            REPOSITORY_ROOT / "docs" / "semantic-specifications" / "ddh-phase-0" / "validation" / "validate_phase0.py",
            REPOSITORY_ROOT / "docs" / "semantic-specifications" / "ddh-phase-1" / "draft" / "validation" / "validate_phase1_spec.py",
            REPOSITORY_ROOT / "docs" / "semantic-specifications" / "ddh-phase-2" / "draft" / "validation" / "validate_phase2_spec.py",
        )
        for validator in validators:
            with self.subTest(validator=validator):
                completed, result = run_validator(validator)
                self.assertEqual(0, completed.returncode, completed.stdout)
                self.assertEqual("passed", result["acceptance_outcome"])


if __name__ == "__main__":
    unittest.main()
