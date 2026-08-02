from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ddh.contracts import CandidateReference, ContractError, content_digest


@dataclass(frozen=True)
class VerificationAsset:
    asset_id: str
    version: int
    scenario_ids: tuple[str, ...]
    assertions: tuple[str, ...]
    expected_values: tuple[str, ...]
    thresholds: tuple[tuple[str, str], ...]
    fixture_case_count: int
    cases: tuple[str, ...]
    markers: tuple[str, ...]
    candidate: CandidateReference
    command: tuple[str, ...]
    adapter_id: str
    known_bad_probes: tuple[str, ...] = ()
    declared_duration_seconds: int | None = None
    historical_p95_seconds: int | None = None
    reliable_estimate_seconds: int | None = None

    @property
    def digest(self) -> str:
        identity = self._implementation_identity()
        identity["candidate"] = self.candidate.__dict__
        return content_digest(identity)

    @property
    def implementation_digest(self) -> str:
        return content_digest(self._implementation_identity())

    def _implementation_identity(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "version": self.version,
            "scenario_ids": self.scenario_ids,
            "assertions": self.assertions,
            "expected_values": self.expected_values,
            "thresholds": self.thresholds,
            "fixture_case_count": self.fixture_case_count,
            "cases": self.cases,
            "markers": self.markers,
            "command": self.command,
            "adapter_id": self.adapter_id,
            "known_bad_probes": self.known_bad_probes,
            "declared_duration_seconds": self.declared_duration_seconds,
            "historical_p95_seconds": self.historical_p95_seconds,
            "reliable_estimate_seconds": self.reliable_estimate_seconds,
        }


@dataclass(frozen=True)
class AssetAdmission:
    asset: VerificationAsset
    outcome: str
    reason_code: str
    independently_admitted: bool


@dataclass(frozen=True)
class TestRepairRequest:
    baseline: VerificationAsset | None
    rejected_asset: VerificationAsset
    required_scenarios: tuple[str, ...]
    rejection_reason: str


@dataclass(frozen=True)
class TestRepairProposal:
    asset: VerificationAsset
    proposer_identity: str


class TestRepairPort(Protocol):
    def repair(self, request: TestRepairRequest) -> TestRepairProposal: ...


@dataclass(frozen=True)
class TestRepairEvidence:
    asset_digest: str
    original_scenario_ids: tuple[str, ...]
    known_bad_probe_ids: tuple[str, ...]
    original_scenarios_passed: bool
    known_bad_product_rejected: bool
    verifier_identity: str


class TestRepairProbePort(Protocol):
    def verify(
        self,
        asset: VerificationAsset,
        original_scenarios: tuple[str, ...],
    ) -> TestRepairEvidence: ...


class TestAuditor:
    def audit(
        self,
        baseline: VerificationAsset | None,
        proposed: VerificationAsset,
        required_scenarios: tuple[str, ...],
        independent_reviewer: bool,
    ) -> AssetAdmission:
        self._validate_mapping(proposed, required_scenarios)
        if baseline is not None:
            self._reject_weakening(baseline, proposed)
            self._require_repair_probe(baseline, proposed)
        if not independent_reviewer:
            raise ContractError("independent_test_admission_required")
        return AssetAdmission(proposed, "admitted", "asset_current", True)

    def _validate_mapping(
        self,
        proposed: VerificationAsset,
        required_scenarios: tuple[str, ...],
    ) -> None:
        if not set(proposed.scenario_ids).issubset(required_scenarios):
            raise ContractError("verification_scenario_mapping_invalid")
        if not proposed.scenario_ids or not proposed.assertions:
            raise ContractError("verification_asset_not_executable")
        if proposed.adapter_id not in {"pytest", "fixed_command"}:
            raise ContractError("verification_adapter_invalid")
        durations = (
            proposed.declared_duration_seconds,
            proposed.historical_p95_seconds,
            proposed.reliable_estimate_seconds,
        )
        if any(
            value is not None and (type(value) is not int or value <= 0)
            for value in durations
        ):
            raise ContractError("verification_duration_profile_invalid")

    def _reject_weakening(
        self,
        baseline: VerificationAsset,
        proposed: VerificationAsset,
    ) -> None:
        checks = (
            set(baseline.assertions).issubset(proposed.assertions),
            baseline.expected_values == proposed.expected_values,
            dict(baseline.thresholds) == dict(proposed.thresholds),
            proposed.fixture_case_count >= baseline.fixture_case_count,
            set(baseline.cases).issubset(proposed.cases),
            not (set(proposed.markers) - set(baseline.markers)) & {"skip", "xfail"},
            _duration_profile(proposed) == _duration_profile(baseline),
        )
        if not all(checks):
            raise ContractError("verification_asset_weakening_rejected")

    def _require_repair_probe(
        self,
        baseline: VerificationAsset,
        proposed: VerificationAsset,
    ) -> None:
        if baseline.implementation_digest == proposed.implementation_digest:
            return
        if not proposed.known_bad_probes:
            raise ContractError("verification_asset_repair_probe_required")
        if not set(proposed.known_bad_probes).issubset(proposed.cases):
            raise ContractError("verification_asset_repair_probe_not_executed")


class TestRepairCoordinator:
    def __init__(
        self,
        auditor: TestAuditor,
        repair_port: TestRepairPort,
        probe_port: TestRepairProbePort,
        admission_identity: str = "independent-test-admission",
    ) -> None:
        self._auditor = auditor
        self._repair_port = repair_port
        self._probe_port = probe_port
        self._admission_identity = admission_identity

    def admit(
        self,
        baseline: VerificationAsset | None,
        proposed: VerificationAsset,
        required_scenarios: tuple[str, ...],
    ) -> AssetAdmission:
        try:
            return self._auditor.audit(
                baseline,
                proposed,
                required_scenarios,
                independent_reviewer=True,
            )
        except ContractError as error:
            request = TestRepairRequest(
                baseline,
                proposed,
                required_scenarios,
                str(error),
            )
        repair = self._repair_port.repair(request)
        evidence = self._probe_port.verify(
            repair.asset,
            proposed.scenario_ids,
        )
        self._validate_separation(
            repair,
            evidence,
            proposed.scenario_ids,
        )
        return self._auditor.audit(
            baseline,
            repair.asset,
            required_scenarios,
            independent_reviewer=True,
        )

    def _validate_separation(
        self,
        repair: TestRepairProposal,
        evidence: TestRepairEvidence,
        original_scenarios: tuple[str, ...],
    ) -> None:
        if not repair.proposer_identity:
            raise ContractError("test_repair_proposer_identity_missing")
        if repair.proposer_identity == self._admission_identity:
            raise ContractError("test_repair_self_admission_prohibited")
        if not evidence.verifier_identity:
            raise ContractError("test_repair_verifier_identity_missing")
        if evidence.verifier_identity in {
            repair.proposer_identity,
            self._admission_identity,
        }:
            raise ContractError("test_repair_probe_independence_required")
        if evidence.asset_digest != repair.asset.digest:
            raise ContractError("test_repair_probe_asset_mismatch")
        if not evidence.original_scenarios_passed:
            raise ContractError("test_repair_original_scenario_replay_required")
        if not evidence.known_bad_product_rejected:
            raise ContractError("test_repair_known_bad_probe_required")
        if not set(original_scenarios).issubset(
            evidence.original_scenario_ids
        ):
            raise ContractError("test_repair_required_scenario_missing")
        if not set(repair.asset.known_bad_probes).issubset(
            evidence.known_bad_probe_ids
        ):
            raise ContractError("test_repair_known_bad_probe_not_executed")


def _duration_profile(
    asset: VerificationAsset,
) -> tuple[int | None, int | None, int | None]:
    return (
        asset.declared_duration_seconds,
        asset.historical_p95_seconds,
        asset.reliable_estimate_seconds,
    )
