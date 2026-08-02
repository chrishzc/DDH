from __future__ import annotations

import difflib
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from ddh.candidate import FrozenCandidate
from ddh.completion import CompletionDecision
from ddh.contracts import AuthorityReference, publish_atomic_json
from ddh.test_auditor import AssetAdmission
from ddh.verification import VerificationResult


@dataclass(frozen=True)
class BundleExportRequest:
    destination: Path
    original_root: Path
    candidate: FrozenCandidate
    specification: AuthorityReference
    admissions: tuple[AssetAdmission, ...]
    results: tuple[VerificationResult, ...]
    completion: CompletionDecision


class CandidateBundleExporter:
    def export(self, request: BundleExportRequest) -> Path:
        if request.destination.exists():
            raise FileExistsError("candidate_bundle_destination_exists")
        request.destination.mkdir(parents=True)
        (request.destination / "blobs").mkdir()
        (request.destination / "verification-assets").mkdir()
        self._write_patch(request.destination, request.original_root, request.candidate)
        self._write_blobs(request.destination, request.candidate)
        self._write_assets(request.destination, request.admissions)
        self._write_results(request.destination, request.results)
        self._write_manifest(
            request.destination,
            request.candidate,
            request.specification,
            request.completion,
            request.admissions,
        )
        return request.destination

    def _write_patch(
        self,
        destination: Path,
        original_root: Path,
        candidate: FrozenCandidate,
    ) -> None:
        chunks: list[str] = []
        for path in candidate.changes.changed_paths:
            before = _read_text(original_root / path)
            after = _read_text(candidate.root / path)
            chunks.extend(
                difflib.unified_diff(
                    before,
                    after,
                    fromfile=f"a/{path}",
                    tofile=f"b/{path}",
                    lineterm="",
                )
            )
        (destination / "changes.patch").write_text(
            "\n".join(chunks),
            encoding="utf-8",
            newline="\n",
        )

    def _write_blobs(self, destination: Path, candidate: FrozenCandidate) -> None:
        for path in candidate.changes.added + candidate.changes.modified:
            source = candidate.root / path
            if not source.exists():
                continue
            blob_name = path.replace("/", "__")
            shutil.copyfile(source, destination / "blobs" / blob_name)

    def _write_assets(
        self,
        destination: Path,
        admissions: tuple[AssetAdmission, ...],
    ) -> None:
        for admission in admissions:
            target = destination / "verification-assets" / (
                f"{admission.asset.asset_id}.json"
            )
            publish_atomic_json(target, asdict(admission))

    def _write_results(
        self,
        destination: Path,
        results: tuple[VerificationResult, ...],
    ) -> None:
        sanitized = [
            {
                key: value
                for key, value in asdict(result).items()
                if key not in {"stdout", "stderr"}
            }
            for result in results
        ]
        publish_atomic_json(
            destination / "typed-verification-result.json",
            {"results": sanitized},
        )

    def _write_manifest(
        self,
        destination: Path,
        candidate: FrozenCandidate,
        specification: AuthorityReference,
        completion: CompletionDecision,
        admissions: tuple[AssetAdmission, ...],
    ) -> None:
        manifest = {
            "specification": asdict(specification),
            "candidate": asdict(candidate.reference),
            "changed_resources": candidate.changes.changed_paths,
            "verification_assets": [item.asset.digest for item in admissions],
            "completion": asdict(completion),
            "automatically_applied": False,
        }
        publish_atomic_json(destination / "candidate-manifest.json", manifest)


def _read_text(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return ["<binary content stored in blobs>"]
