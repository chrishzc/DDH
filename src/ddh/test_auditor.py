from __future__ import annotations

from dataclasses import dataclass

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


def _duration_profile(
    asset: VerificationAsset,
) -> tuple[int | None, int | None, int | None]:
    return (
        asset.declared_duration_seconds,
        asset.historical_p95_seconds,
        asset.reliable_estimate_seconds,
    )
