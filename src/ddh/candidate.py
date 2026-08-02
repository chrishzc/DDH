from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from uuid import uuid4

from ddh.contracts import CandidateReference, ContractError
from ddh.paths import normalize_repository_path, path_matches_any


@dataclass(frozen=True)
class FileRecord:
    path: str
    digest: str
    size: int


@dataclass(frozen=True)
class ChangeSet:
    added: tuple[str, ...]
    modified: tuple[str, ...]
    deleted: tuple[str, ...]
    renamed: tuple[tuple[str, str], ...]

    @property
    def changed_paths(self) -> tuple[str, ...]:
        paths = set(self.added + self.modified + self.deleted)
        return tuple(sorted(paths))


@dataclass(frozen=True)
class FrozenCandidate:
    reference: CandidateReference
    root: Path
    baseline: tuple[FileRecord, ...]
    current: tuple[FileRecord, ...]
    changes: ChangeSet


class AdmissionRejected(ContractError):
    def __init__(self, invalid_paths: tuple[str, ...]) -> None:
        super().__init__("mixed_or_out_of_scope_change")
        self.invalid_paths = invalid_paths


class CandidateController:
    def __init__(
        self,
        source_root: Path,
        candidate_root: Path,
        write_scope: tuple[str, ...],
        protected: tuple[str, ...] = (),
        starting_generation: int = 0,
    ) -> None:
        self.source_root = source_root.resolve()
        self.root = candidate_root.resolve()
        self.write_scope = write_scope
        self.protected = protected
        self.generation = starting_generation
        self.frozen: FrozenCandidate | None = None
        self.rejected_private_delta: Mapping[str, str | None] | None = None
        self._baseline: dict[str, FileRecord] = {}
        self._materialized = False

    def materialize(self) -> None:
        if self.root.exists():
            raise ContractError("candidate_root_already_exists")
        self._reject_junctions()
        shutil.copytree(
            self.source_root,
            self.root,
            symlinks=True,
            ignore=shutil.ignore_patterns(".git"),
        )
        self._baseline = self._scan()
        self._materialized = True

    def _reject_junctions(self) -> None:
        for root, directories, files in self.source_root.walk(
            top_down=True,
            follow_symlinks=False,
        ):
            for name in (*directories, *files):
                path = root / name
                is_junction = getattr(path, "is_junction", lambda: False)
                if is_junction():
                    raise ContractError("workspace_junction_materialization_unsupported")

    @property
    def baseline_digest(self) -> str:
        if not self._materialized:
            raise ContractError("candidate_not_materialized")
        return manifest_digest(self._baseline)

    def admit(self, changes: Mapping[str, str | None]) -> ChangeSet:
        if self.frozen is not None:
            raise ContractError("candidate_frozen")
        canonical_changes, invalid = self._classify_paths(changes)
        if invalid:
            self.rejected_private_delta = dict(changes)
            raise AdmissionRejected(tuple(sorted(invalid)))
        for path, content in canonical_changes.items():
            self._apply(path, content)
        self.generation += 1
        return calculate_changes(self._baseline, self._scan())

    def freeze(self) -> FrozenCandidate:
        current = self._scan()
        changes = calculate_changes(self._baseline, current)
        digest = manifest_digest(current)
        reference = CandidateReference(str(uuid4()), self.generation, digest)
        self.frozen = FrozenCandidate(
            reference,
            self.root,
            tuple(self._baseline.values()),
            tuple(current.values()),
            changes,
        )
        return self.frozen

    def assert_current(self, reference: CandidateReference) -> None:
        if self.frozen is None or self.frozen.reference != reference:
            raise ContractError("candidate_reference_mismatch")
        if manifest_digest(self._scan()) != reference.digest:
            raise ContractError("candidate_content_changed_after_freeze")

    def _classify_paths(
        self,
        changes: Mapping[str, str | None],
    ) -> tuple[dict[str, str | None], set[str]]:
        canonical: dict[str, str | None] = {}
        invalid: set[str] = set()
        for requested_path, content in changes.items():
            try:
                path = normalize_repository_path(self.root, requested_path).canonical_path
            except ValueError:
                invalid.add(requested_path)
                continue
            if not path_matches_any(path, self.write_scope):
                invalid.add(path)
            elif path_matches_any(path, self.protected):
                invalid.add(path)
            elif self._contains_link(path):
                invalid.add(path)
            canonical[path] = content
        return canonical, invalid

    def _contains_link(self, relative_path: str) -> bool:
        current = self.root
        for part in Path(relative_path).parts:
            current = current / part
            is_junction = getattr(current, "is_junction", lambda: False)
            if current.is_symlink() or is_junction():
                return True
        return False

    def _apply(self, relative_path: str, content: str | None) -> None:
        target = self.root / Path(relative_path)
        if content is None:
            if target.exists() and target.is_file():
                target.unlink()
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    def _scan(self) -> dict[str, FileRecord]:
        records: dict[str, FileRecord] = {}
        for path in sorted(self.root.rglob("*")):
            if ".git" in path.parts:
                continue
            relative = path.relative_to(self.root).as_posix()
            if path.is_symlink():
                records[relative] = link_record(path, relative)
            elif path.is_file():
                records[relative] = file_record(path, relative)
        return records


def file_record(path: Path, relative: str) -> FileRecord:
    data = path.read_bytes()
    return FileRecord(relative, hashlib.sha256(data).hexdigest(), len(data))


def link_record(path: Path, relative: str) -> FileRecord:
    target = os.readlink(path).encode("utf-8")
    digest = hashlib.sha256(b"symlink:" + target).hexdigest()
    return FileRecord(relative, digest, len(target))


def manifest_digest(records: Mapping[str, FileRecord]) -> str:
    lines = [
        f"{path}:{record.digest}:{record.size}"
        for path, record in sorted(records.items())
    ]
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def calculate_changes(
    baseline: Mapping[str, FileRecord],
    current: Mapping[str, FileRecord],
) -> ChangeSet:
    deleted = set(baseline) - set(current)
    added = set(current) - set(baseline)
    modified = {
        path
        for path in set(baseline) & set(current)
        if baseline[path].digest != current[path].digest
    }
    renamed = detect_renames(baseline, current, deleted, added)
    return ChangeSet(
        tuple(sorted(added)),
        tuple(sorted(modified)),
        tuple(sorted(deleted)),
        renamed,
    )


def detect_renames(
    baseline: Mapping[str, FileRecord],
    current: Mapping[str, FileRecord],
    deleted: set[str],
    added: set[str],
) -> tuple[tuple[str, str], ...]:
    pairs: list[tuple[str, str]] = []
    for old_path in sorted(deleted):
        matches = [
            new_path
            for new_path in sorted(added)
            if baseline[old_path].digest == current[new_path].digest
        ]
        if matches:
            pairs.append((old_path, matches[0]))
    return tuple(pairs)
