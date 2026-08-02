from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


class PathBoundaryError(ValueError):
    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


@dataclass(frozen=True)
class PathResolution:
    canonical_path: str


def _normalize_parts(user_path: str) -> list[str]:
    normalized = user_path.replace("\\", "/")
    parts: list[str] = []
    for part in PurePosixPath(normalized).parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise PathBoundaryError("workspace_escape")
            parts.pop()
            continue
        parts.append(part)
    return parts


def normalize_repository_path(workspace_root: Path, user_path: str) -> PathResolution:
    if user_path.startswith(("//", "\\\\")):
        raise PathBoundaryError("unsupported_path_class")
    if user_path.startswith("/") or WINDOWS_ABSOLUTE.match(user_path):
        raise PathBoundaryError("absolute_path_prohibited")
    canonical = "/".join(_normalize_parts(user_path))
    if not canonical:
        raise PathBoundaryError("empty_repository_path")
    _reject_resolved_escape(workspace_root, canonical)
    return PathResolution(canonical)


def _reject_resolved_escape(workspace_root: Path, canonical: str) -> None:
    root = workspace_root.resolve()
    candidate = (root / Path(canonical)).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise PathBoundaryError("workspace_escape") from error


def path_matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    canonical = path.replace("\\", "/")
    return any(fnmatch.fnmatchcase(canonical, pattern) for pattern in patterns)

