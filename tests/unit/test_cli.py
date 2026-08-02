import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKLOAD = (
    REPOSITORY_ROOT
    / "tests"
    / "fixtures"
    / "portable_workspace"
    / "workload-specification.json"
)


class CliTests(unittest.TestCase):
    def test_specification_digest_command_is_non_mutating(self) -> None:
        completed = subprocess.run(
            (
                sys.executable,
                "-m",
                "ddh.cli",
                "specification-digest",
                str(WORKLOAD),
            ),
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = json.loads(completed.stdout)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("PORTABLE-WORKSPACE-WP", output["authority_id"])
        self.assertTrue(output["digest"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
