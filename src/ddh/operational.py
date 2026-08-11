"""Phase 5 operational hardening contracts and deterministic local adapters."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ddh.contracts import ContractError, content_digest
from ddh.system_map import MapQuery, SystemMapPort


@dataclass(frozen=True)
class EnvironmentProfile:
    profile_id: str
    support_tier: Literal["release_blocking", "preview", "unsupported"]
    os_name: str
    architecture: str
    runtime_versions: tuple[str, ...]
    tool_versions: tuple[tuple[str, str], ...]
    dependency_digest: str
    cwd: str
    locale: str
    timezone: str
    encoding: str
    environment_allowlist: tuple[str, ...]
    isolation_profile: Literal["light", "standard", "high_assurance", "external"]
    network_capability: bool
    database_capability: bool
    filesystem_profile: str
    output_byte_limit: int = 65_536
    output_line_limit: int = 2_000
    output_event_limit: int = 2_000

    def __post_init__(self) -> None:
        if self.output_byte_limit <= 0 or self.output_line_limit <= 0 or self.output_event_limit <= 0:
            raise ContractError("environment_output_limit_invalid")
        if self.support_tier == "release_blocking":
            supported = {("windows_11", "x86_64"), ("ubuntu_24_04", "x86_64")}
            if (self.os_name, self.architecture) not in supported:
                raise ContractError("release_blocking_platform_invalid")
        if self.isolation_profile == "high_assurance" and self.filesystem_profile in {"unc", "smb", "nfs", "wsl_mnt_c", "unknown"}:
            raise ContractError("filesystem_profile_unsupported")

    @property
    def digest(self) -> str:
        return content_digest(self.__dict__)


@dataclass(frozen=True)
class EnvironmentObservation:
    os_name: str
    architecture: str
    runtime_versions: tuple[str, ...]
    tool_versions: tuple[tuple[str, str], ...]
    dependency_digest: str
    cwd: str
    locale: str
    timezone: str
    encoding: str
    filesystem_profile: str


@dataclass(frozen=True)
class EnvironmentBinding:
    bound: bool
    reason_code: str
    evidence_tier: str


def bind_environment(profile: EnvironmentProfile, observed: EnvironmentObservation) -> EnvironmentBinding:
    expected = (
        profile.os_name, profile.architecture, profile.runtime_versions,
        profile.tool_versions, profile.dependency_digest, profile.cwd,
        profile.locale, profile.timezone, profile.encoding, profile.filesystem_profile,
    )
    actual = (
        observed.os_name, observed.architecture, observed.runtime_versions,
        observed.tool_versions, observed.dependency_digest, observed.cwd,
        observed.locale, observed.timezone, observed.encoding, observed.filesystem_profile,
    )
    return EnvironmentBinding(expected == actual, "environment_profile_bound" if expected == actual else "environment_profile_mismatch", profile.support_tier)


@dataclass(frozen=True)
class ExecutionEstimate:
    declared_seconds: int | None = None
    same_platform_p95_seconds: int | None = None
    collected_work_seconds: int | None = None
    profile_floor_seconds: int | None = None
    expected_progress_interval_seconds: int | None = None


@dataclass(frozen=True)
class BoundedExecutionPlan:
    generation: int
    environment_digest: str
    execution_deadline_seconds: int
    no_progress_deadline_seconds: int | None
    termination_grace_seconds: int
    business_threshold: str
    reason_code: str = "execution_plan_ready"


class ExecutionPlanner:
    def build(
        self,
        environment: EnvironmentProfile,
        estimate: ExecutionEstimate,
        work_package_ceiling_seconds: int,
        business_threshold: str,
        generation: int = 1,
    ) -> BoundedExecutionPlan:
        references = tuple(
            value for value in (
                estimate.declared_seconds,
                estimate.same_platform_p95_seconds,
                estimate.collected_work_seconds,
                estimate.profile_floor_seconds,
            ) if value is not None
        )
        if any(value <= 0 for value in references) or work_package_ceiling_seconds <= 0:
            raise ContractError("execution_estimate_invalid")
        deadline = 600 if not references else max(references) * 2 + 30
        progress = estimate.expected_progress_interval_seconds
        no_progress = None if progress is None else max(progress * 2, 120)
        reason = "execution_plan_ready" if deadline <= work_package_ceiling_seconds else "verification_plan_not_ready"
        return BoundedExecutionPlan(
            generation, environment.digest, deadline, no_progress, 30,
            business_threshold, reason,
        )

    def retry_allowed(self, previous: BoundedExecutionPlan, proposed: BoundedExecutionPlan) -> bool:
        return proposed.generation > previous.generation and proposed != previous


@dataclass(frozen=True)
class BoundedOutput:
    text: str
    byte_count: int
    line_count: int
    event_count: int
    truncated: bool
    repeated_fingerprints: tuple[tuple[str, int], ...]


class OutputDrainLimiter:
    def consume(self, chunks: tuple[str, ...], profile: EnvironmentProfile) -> BoundedOutput:
        accepted: list[str] = []
        bytes_used = 0
        lines_used = 0
        events_used = 0
        truncated = False
        fingerprints: dict[str, int] = {}
        for chunk in chunks:
            fingerprint = hashlib.sha256(chunk.encode("utf-8")).hexdigest()[:16]
            fingerprints[fingerprint] = fingerprints.get(fingerprint, 0) + 1
            encoded = chunk.encode("utf-8")
            new_lines = chunk.count("\n") + (1 if chunk and not chunk.endswith("\n") else 0)
            if events_used + 1 > profile.output_event_limit or lines_used + new_lines > profile.output_line_limit or bytes_used + len(encoded) > profile.output_byte_limit:
                truncated = True
                break
            accepted.append(chunk)
            bytes_used += len(encoded)
            lines_used += new_lines
            events_used += 1
        repeats = tuple(sorted((key, count) for key, count in fingerprints.items() if count > 1))
        return BoundedOutput("".join(accepted), bytes_used, lines_used, events_used, truncated, repeats)


@dataclass(frozen=True)
class TempRootDisposition:
    outcome: Literal["removed", "temporary_root_quarantined"]
    path: Path


class OwnedTemporaryRoot:
    MARKER = ".ddh-owned-root"

    def mark(self, root: Path, identity: str) -> None:
        root.mkdir(parents=True, exist_ok=False)
        (root / self.MARKER).write_text(identity, encoding="utf-8")

    def cleanup(self, root: Path, identity: str) -> TempRootDisposition:
        marker = root / self.MARKER
        if root.is_symlink() or not marker.is_file() or marker.read_text(encoding="utf-8") != identity:
            return TempRootDisposition("temporary_root_quarantined", root)
        for item in root.rglob("*"):
            if item.is_symlink():
                return TempRootDisposition("temporary_root_quarantined", root)
        shutil.rmtree(root)
        return TempRootDisposition("removed", root)


@dataclass(frozen=True)
class Capability:
    capability_id: str
    equivalence_class: str
    state: Literal["available", "degraded", "unavailable", "unknown"]
    approved_fallback: bool = False


class CapabilityHealthRegistry:
    def __init__(self, capabilities: tuple[Capability, ...]) -> None:
        self._items = {item.capability_id: item for item in capabilities}
        if len(self._items) != len(capabilities):
            raise ContractError("capability_identity_duplicate")

    def select(self, requested: str) -> tuple[str | None, str]:
        current = self._items.get(requested)
        if current is None or current.state in {"unavailable", "unknown"}:
            return None, "capability_unavailable"
        if current.state == "available":
            return current.capability_id, "capability_available"
        fallbacks = sorted(
            item.capability_id for item in self._items.values()
            if item.equivalence_class == current.equivalence_class
            and item.state == "available" and item.approved_fallback
        )
        return (fallbacks[0], "approved_fallback_selected") if fallbacks else (None, "capability_unavailable")


@dataclass(frozen=True)
class ManagedAssetPreview:
    target: Path
    expected_digest: str
    current_digest: str | None
    delta: bool
    outcome: str


class ManagedAssetController:
    def preview(self, target: Path, expected: bytes, known_current_digest: str | None) -> ManagedAssetPreview:
        current = _file_digest(target) if target.is_file() else None
        expected_digest = hashlib.sha256(expected).hexdigest()
        if current is not None and known_current_digest not in {None, current}:
            return ManagedAssetPreview(target, expected_digest, current, True, "managed_asset_user_change_conflict")
        return ManagedAssetPreview(target, expected_digest, current, current != expected_digest, "preview_ready")

    def apply(self, preview: ManagedAssetPreview, expected: bytes) -> str:
        if preview.outcome != "preview_ready":
            raise ContractError(preview.outcome)
        current = _file_digest(preview.target) if preview.target.is_file() else None
        if current != preview.current_digest:
            raise ContractError("managed_asset_target_changed_after_preview")
        if not preview.delta:
            return "already_current"
        preview.target.parent.mkdir(parents=True, exist_ok=True)
        pending = preview.target.with_name(f"{preview.target.name}.ddh-pending")
        pending.write_bytes(expected)
        os.replace(pending, preview.target)
        if _file_digest(preview.target) != preview.expected_digest:
            raise ContractError("managed_asset_post_apply_parity_failed")
        return "applied_with_parity"


@dataclass(frozen=True)
class BranchMapBinding:
    repository_id: str
    branch: str
    resolved_commit: str
    worktree_id: str
    candidate_identity: str
    map_view_id: str
    consumed_facts: tuple[str, ...]

    @property
    def digest(self) -> str:
        return content_digest(self.__dict__)

    def compatible_with(self, other: "BranchMapBinding") -> bool:
        return self == other


@dataclass(frozen=True)
class BranchMapSubject:
    repository_id: str
    branch: str
    resolved_commit: str
    worktree_id: str
    candidate_identity: str


class BranchBoundMapConsumer:
    def consume(self, subject: BranchMapSubject, adapter: SystemMapPort, purpose: str) -> BranchMapBinding:
        query = MapQuery(subject.repository_id, subject.branch, subject.resolved_commit, (), purpose)
        result = adapter.query(query)
        if (result.repository_id, result.requested_ref, result.resolved_commit) != (
            subject.repository_id, subject.branch, subject.resolved_commit,
        ) or not result.view_id:
            raise ContractError("branch_map_binding_invalidated")
        facts = tuple(
            [f"node:{item}" for item in result.nodes]
            + [f"relation:{left}->{right}" for left, right in result.relations]
            + [f"resource:{resource}->{node}" for resource, node in result.resource_bindings]
        )
        if not facts:
            raise ContractError("system_map_facts_not_consumed")
        return BranchMapBinding(
            subject.repository_id, subject.branch, subject.resolved_commit,
            subject.worktree_id, subject.candidate_identity, result.view_id, facts,
        )


@dataclass(frozen=True)
class OperationalTelemetrySummary:
    event_type: str
    counts: tuple[tuple[str, int], ...]
    authoritative: bool = False
    retained_raw_logs: bool = False
    completion_input: bool = False


class BoundedOperationalTelemetry:
    PROHIBITED = {"prompt", "source", "stdout", "stderr", "secret", "credential"}

    def __init__(self, path: Path, max_events: int = 100, max_total_bytes: int = 65_536) -> None:
        if max_events <= 0 or max_total_bytes <= 0:
            raise ContractError("telemetry_bounds_invalid")
        self._path = path
        self._max_events = max_events
        self._max_total_bytes = max_total_bytes

    def emit(self, event_type: str, fields: dict[str, object]) -> OperationalTelemetrySummary:
        if _contains_prohibited(fields, self.PROHIBITED):
            raise ContractError("telemetry_sensitive_field_prohibited")
        events = self._load()
        events.append({"event_type": event_type, "fields": fields})
        events = events[-self._max_events:]
        while events and len(json.dumps(events, sort_keys=True).encode("utf-8")) > self._max_total_bytes:
            events.pop(0)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        pending = self._path.with_name(f"{self._path.name}.pending")
        pending.write_text(json.dumps(events, sort_keys=True), encoding="utf-8")
        os.replace(pending, self._path)
        counts: dict[str, int] = {}
        for event in events:
            key = str(event["event_type"])
            counts[key] = counts.get(key, 0) + 1
        return OperationalTelemetrySummary(event_type, tuple(sorted(counts.items())))

    def _load(self) -> list[dict[str, object]]:
        if not self._path.is_file():
            return []
        value = json.loads(self._path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contains_prohibited(value: object, prohibited: set[str]) -> bool:
    if isinstance(value, dict):
        return bool(prohibited & value.keys()) or any(_contains_prohibited(item, prohibited) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_prohibited(item, prohibited) for item in value)
    return False
