import unittest
from pathlib import Path
from unittest.mock import patch

from src.manifest_loader import load_manifest_path
from src.path_normalizer import normalize_path


class PortableWorkspaceAcceptanceTests(unittest.TestCase):
    workspace_root = Path(__file__).resolve().parents[2]

    def test_windows_separator_is_canonicalized(self) -> None:
        normalized = normalize_path(
            self.workspace_root,
            r"src\package\module.py",
            "windows-11",
        )
        self.assertEqual("src/package/module.py", normalized)
        self.assertEqual(normalized, load_manifest_path(normalized))

    def test_parent_segments_are_collapsed(self) -> None:
        normalized = normalize_path(
            self.workspace_root,
            "./src/package/../package/module.py",
            "ubuntu-24.04",
        )
        self.assertEqual("src/package/module.py", normalized)

    def test_workspace_escape_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "workspace_escape"):
            normalize_path(self.workspace_root, "../secrets.txt", "ubuntu-24.04")

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute_path_prohibited"):
            normalize_path(self.workspace_root, "C:/secrets.txt", "windows-11")

    def test_unc_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported_path_class"):
            normalize_path(
                self.workspace_root,
                "//server/share/file.txt",
                "windows-11",
            )

    def test_symlink_escape_is_rejected(self) -> None:
        root = self.workspace_root.resolve()
        outside_target = root.parent / "outside" / "secret.txt"
        with patch(
            "src.path_normalizer.Path.resolve",
            side_effect=(root, outside_target),
        ):
            with self.assertRaisesRegex(ValueError, "workspace_escape"):
                normalize_path(root, "link/secret.txt", "ubuntu-24.04")


if __name__ == "__main__":
    unittest.main()
