"""Tool-neutral Phase 4 Verification Asset governance contracts.

This module is intentionally local and deterministic: it neither discovers
authority from a Catalog nor performs network, credential, or CI operations.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Literal

from ddh.contracts import CandidateReference, ContractError, content_digest


ScopeLayer = Literal["Module", "Subsystem", "Domain", "Global"]
AdmissionState = Literal[
    "draft", "candidate", "admission_validating", "admitted", "rejected"
]
ValidityDisposition = Literal[
    "current", "rerun_required", "suspect", "stale", "quarantined", "retired"
]
ExecutionOutcome = Literal[
    "not_run", "passed", "failed", "error", "timeout", "unavailable", "invalidated"
]

SCOPE_LAYERS = {"Module", "Subsystem", "Domain", "Global"}
DEPENDENCY_KINDS = {
    "source", "asset", "fixture", "helper", "config", "semantic_spec",
    "contract", "schema", "quality_profile", "runner", "toolchain",
}
FORBIDDEN_MARKERS = {"skip", "xfail", "exclusion"}


@dataclass(frozen=True)
class SpecificationNotReady:
    missing: tuple[str, ...]
    blocked_asset_ids: tuple[str, ...]
    exception_type: str = "specification_not_ready"
    allowed_action: str = "obtain_confirmed_specification"
    automatic_relaxation: bool = False


@dataclass(frozen=True)
class QualityAddOn:
    name: str
    applicability: Literal["required", "not_applicable_with_business_reason"]
    business_reason: str = ""

    def __post_init__(self) -> None:
        if self.applicability == "not_applicable_with_business_reason" and not self.business_reason:
            raise ContractError("quality_add_on_na_reason_required")


@dataclass(frozen=True)
class VerificationAssetManifest:
    asset_id: str
    version: str
    asset_kind: str
    tool_adapter: str
    scope_layer: ScopeLayer
    architecture_targets: tuple[str, ...]
    requirement_refs: tuple[str, ...]
    scenario_refs: tuple[str, ...]
    semantic_spec_refs: tuple[str, ...]
    quality_profile_ref: str
    dependencies: tuple[tuple[str, str], ...]
    fixed_entrypoint: tuple[str, ...]
    environment_profile_digest: str
    oracle_definition: str
    expected_result: str
    assertions: tuple[str, ...]
    expected_values: tuple[str, ...]
    thresholds: tuple[tuple[str, str], ...]
    fixture_case_count: int
    cases: tuple[str, ...]
    markers: tuple[str, ...] = ()
    quality_add_ons: tuple[QualityAddOn, ...] = ()
    timeout_seconds: int = 600
    output_limit_bytes: int = 65_536
    supersedes: str | None = None

    def __post_init__(self) -> None:
        if not all((self.asset_id, self.version, self.asset_kind, self.tool_adapter)):
            raise ContractError("verification_asset_identity_missing")
        if self.scope_layer not in SCOPE_LAYERS:
            raise ContractError("verification_asset_scope_invalid")
        if not self.requirement_refs or not self.scenario_refs:
            raise ContractError("specification_not_ready:requirement_or_scenario_mapping")
        if not self.semantic_spec_refs or not self.quality_profile_ref:
            raise ContractError("specification_not_ready:semantic_or_quality_profile")
        if not self.fixed_entrypoint or not self.oracle_definition or not self.expected_result:
            raise ContractError("specification_not_ready:execution_or_oracle")
        if not self.assertions or self.fixture_case_count < 1 or not self.cases:
            raise ContractError("verification_asset_not_executable")
        if self.timeout_seconds <= 0 or self.output_limit_bytes <= 0:
            raise ContractError("verification_asset_execution_limits_invalid")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ContractError("verification_asset_dependency_duplicate")
        if any(kind not in DEPENDENCY_KINDS or not value for kind, value in self.dependencies):
            raise ContractError("verification_asset_dependency_invalid")

    @property
    def immutable_digest(self) -> str:
        value = dict(self.__dict__)
        value["quality_add_ons"] = tuple(item.__dict__ for item in self.quality_add_ons)
        return content_digest(value)

    @property
    def identity(self) -> str:
        return f"{self.asset_id}@{self.version}:{self.immutable_digest}"


@dataclass(frozen=True)
class AssetRecord:
    manifest: VerificationAssetManifest
    admission_state: AdmissionState = "draft"
    validity: ValidityDisposition = "current"
    execution_outcome: ExecutionOutcome = "not_run"
    independent_auditor: bool = False
    known_bad_detected: bool = False

    @property
    def active(self) -> bool:
        return self.admission_state == "admitted" and self.validity == "current"


@dataclass(frozen=True)
class ExecutionResult:
    asset_identity: str
    outcome: ExecutionOutcome
    reason_code: str
    stdout_summary: str = ""
    stderr_summary: str = ""
    output_truncated: bool = False


class VerificationAssetCatalog:
    """A derived discovery index; it owns no admission or behavioral authority."""

    def __init__(self, records: tuple[AssetRecord, ...]) -> None:
        keys = [(item.manifest.asset_id, item.manifest.version) for item in records]
        if len(keys) != len(set(keys)):
            raise ContractError("verification_catalog_duplicate_identity")
        self._records = tuple(sorted(records, key=lambda item: item.manifest.identity))

    @classmethod
    def rebuild(cls, manifests: tuple[VerificationAssetManifest, ...]) -> "VerificationAssetCatalog":
        return cls(tuple(AssetRecord(manifest) for manifest in manifests))

    def discover(self, layer: ScopeLayer, active_only: bool = False) -> tuple[AssetRecord, ...]:
        return tuple(
            item for item in self._records
            if item.manifest.scope_layer == layer and (not active_only or item.active)
        )

    @property
    def catalog_digest(self) -> str:
        return content_digest(tuple(item.manifest.immutable_digest for item in self._records))


class VerificationAssetAuditor:
    """Admission authority. Execution selection is deliberately absent."""

    def admit(
        self,
        candidate: AssetRecord,
        required_scenarios: tuple[str, ...],
        baseline: AssetRecord | None = None,
        *,
        independent_auditor: bool,
        known_bad_detected: bool,
    ) -> AssetRecord | SpecificationNotReady:
        manifest = candidate.manifest
        missing = _missing_specification(manifest, required_scenarios)
        if missing:
            return SpecificationNotReady(tuple(missing), (manifest.identity,))
        if not independent_auditor:
            raise ContractError("independent_test_auditor_required")
        if baseline is not None:
            self._reject_weakening(baseline.manifest, manifest)
            if baseline.manifest.immutable_digest != manifest.immutable_digest and not known_bad_detected:
                raise ContractError("known_bad_probe_required")
        return AssetRecord(
            manifest, "admitted", "current", "not_run", True, known_bad_detected
        )

    def _reject_weakening(
        self, baseline: VerificationAssetManifest, proposed: VerificationAssetManifest
    ) -> None:
        checks = (
            set(baseline.assertions).issubset(proposed.assertions),
            set(baseline.expected_values).issubset(proposed.expected_values),
            dict(baseline.thresholds).items() <= dict(proposed.thresholds).items(),
            proposed.fixture_case_count >= baseline.fixture_case_count,
            set(baseline.cases).issubset(proposed.cases),
            not (set(proposed.markers) - set(baseline.markers)) & FORBIDDEN_MARKERS,
            set(baseline.scenario_refs).issubset(proposed.scenario_refs),
        )
        if not all(checks):
            raise ContractError("verification_asset_weakening_rejected")


class MechanicalVerificationExecutor:
    """Executes only a fixed active asset; it cannot alter selection or semantics."""

    def execute(
        self,
        record: AssetRecord,
        candidate: CandidateReference,
        environment_profile_digest: str,
        invoke: Callable[[tuple[str, ...]], ExecutionResult],
    ) -> ExecutionResult:
        manifest = record.manifest
        if record.admission_state != "admitted":
            return ExecutionResult(manifest.identity, "invalidated", "manifest_not_yet_admitted")
        if not record.active:
            return ExecutionResult(manifest.identity, "invalidated", "manifest_not_active")
        if candidate.digest not in {value for kind, value in manifest.dependencies if kind == "source"}:
            return ExecutionResult(manifest.identity, "invalidated", "candidate_binding_mismatch")
        if environment_profile_digest != manifest.environment_profile_digest:
            return ExecutionResult(manifest.identity, "invalidated", "environment_binding_mismatch")
        result = invoke(manifest.fixed_entrypoint)
        if result.asset_identity != manifest.identity:
            raise ContractError("executor_result_asset_binding_mismatch")
        if result.outcome == "passed":
            return result
        return result


@dataclass(frozen=True)
class ImpactEvidence:
    changed_dependencies: tuple[tuple[str, str], ...]
    consumed_map_facts: tuple[str, ...]
    used_live_source_fallback: bool = False

    def __post_init__(self) -> None:
        if not self.consumed_map_facts and not self.used_live_source_fallback:
            raise ContractError("system_map_facts_not_consumed")


class CurrentnessEvaluator:
    def reevaluate(self, record: AssetRecord, impact: ImpactEvidence) -> AssetRecord:
        dependencies = set(record.manifest.dependencies)
        changed = dependencies & set(impact.changed_dependencies)
        if not changed:
            return record
        validity: ValidityDisposition = (
            "rerun_required" if all(kind == "source" for kind, _ in changed) else "stale"
        )
        return replace(record, validity=validity, execution_outcome="invalidated")

    def mark_suspect(self, record: AssetRecord) -> AssetRecord:
        return replace(record, validity="suspect")

    def quarantine(self, record: AssetRecord) -> AssetRecord:
        return replace(record, validity="quarantined")

    def retire(self, record: AssetRecord) -> AssetRecord:
        return replace(record, validity="retired")


def optimize_fixed_suite(
    records: tuple[AssetRecord, ...],
    *,
    order: Literal["deterministic", "cost_aware"] = "deterministic",
    shards: int = 1,
    cache_enabled: bool = False,
    parallelism: int = 1,
    runner_placement: str = "local",
) -> tuple[AssetRecord, ...]:
    if shards < 1 or parallelism < 1 or not runner_placement:
        raise ContractError("verification_optimization_invalid")
    if order not in {"deterministic", "cost_aware"}:
        raise ContractError("verification_order_invalid")
    # These settings only schedule the exact complete input set.
    return tuple(sorted(records, key=lambda item: item.manifest.identity))


def evidence_retention(record: AssetRecord) -> dict[str, object]:
    """Return only rerunnable evidence; never logs, receipts, or attempt ledgers."""
    manifest = record.manifest
    return {
        "asset_identity": manifest.identity,
        "dependencies": manifest.dependencies,
        "environment_profile_digest": manifest.environment_profile_digest,
        "entrypoint": manifest.fixed_entrypoint,
        "retained_raw_logs": False,
        "retained_pass_receipts": False,
        "retained_attempt_ledger": False,
    }


def _missing_specification(
    manifest: VerificationAssetManifest, required_scenarios: tuple[str, ...]
) -> list[str]:
    missing: list[str] = []
    if not set(required_scenarios).issubset(manifest.scenario_refs):
        missing.append("required_scenario_mapping")
    if not manifest.oracle_definition:
        missing.append("oracle_definition")
    if not manifest.expected_result:
        missing.append("expected_result")
    return missing
