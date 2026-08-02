import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class Phase1SpecificationContractTests(unittest.TestCase):
    def test_exact_phase1_package_still_validates(self) -> None:
        validator = (
            REPOSITORY_ROOT
            / "docs"
            / "semantic-specifications"
            / "ddh-phase-1"
            / "draft"
            / "validation"
            / "validate_phase1_spec.py"
        )
        completed = subprocess.run(
            (sys.executable, str(validator)),
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertEqual("passed", result["acceptance_outcome"])
        self.assertEqual(0, result["total_error_count"])

    def test_phase0_regression_package_still_validates(self) -> None:
        validator = (
            REPOSITORY_ROOT
            / "docs"
            / "semantic-specifications"
            / "ddh-phase-0"
            / "validation"
            / "validate_phase0.py"
        )
        completed = subprocess.run(
            (sys.executable, str(validator)),
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertEqual("passed", result["acceptance_outcome"])


if __name__ == "__main__":
    unittest.main()
