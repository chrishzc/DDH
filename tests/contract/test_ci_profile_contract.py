import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "ddh-ci.yml"


class CiProfileContractTests(unittest.TestCase):
    def test_required_and_latest_profiles_are_declared(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        required_fragments = (
            "workflow_dispatch:",
            "run_windows_11:",
            "github.actor == 'chrishzc'",
            "required-windows-11:",
            "ddh-windows-11",
            "required-ubuntu:",
            "runs-on: ubuntu-24.04",
            'python-version: "3.13"',
            "latest-stable-compatibility",
            'python-version: "3.x"',
            "PYTHONPATH: ${{ github.workspace }}/src",
            "persist-credentials: false",
            "permissions:",
            "contents: read",
            "GIT_CONFIG_KEY_0: core.autocrlf",
            'GIT_CONFIG_VALUE_0: "false"',
        )
        for fragment in required_fragments:
            self.assertIn(fragment, workflow)


if __name__ == "__main__":
    unittest.main()
