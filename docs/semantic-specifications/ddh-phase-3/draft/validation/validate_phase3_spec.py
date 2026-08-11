from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PACKAGE_ROOT / "manifest.json"
SPECIFICATION = "DDH-P3-SPEC-001@1.0.0"
REQUIRED_CAPABILITY_GROUPS = {
    "parallel_decision",
    "context_and_activation",
    "independent_test_construction",
    "shared_resource_coordination",
    "handoff_and_staleness",
    "central_admission",
    "quiescence_and_join",
    "integrated_verification",
    "system_map_consumption",
    "completion_separation",
    "automatic_fallback_and_recovery",
    "stress_and_cost",
}
REQUIRED_MODULES = {
    "PathNormalizer",
    "ManifestLoader",
    "ManifestIndex",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_bytes().decode("utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )


def calculate_file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate_closure_digest(asset_digests: dict[str, str]) -> str:
    lines = [
        f"{path}:{asset_digests[path]}"
        for path in sorted(asset_digests)
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def validate_manifest(manifest: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "status": "ready_for_confirmation",
        "implementation_authority": "none_until_exact_human_confirmation",
        "risk_class": "L2",
        "runtime_mode": "parallel_when_beneficial_with_serial_fallback",
        "external_side_effects": "prohibited",
        "system_map_authority": "actual_architecture_index_not_ssot",
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            errors.append(f"manifest {field} must be {value}")
    baseline = manifest.get("phase2_baseline_commit")
    if not isinstance(baseline, str) or len(baseline) != 40:
        errors.append("phase2 baseline commit must be an exact SHA-1 identity")
    confirmation = manifest.get("confirmation", {})
    if confirmation.get("confirmed") is not False:
        errors.append("draft confirmation must remain false")
    if manifest.get("higher_layer_completion_outcome") != {
        "domain_accepted": "not_evaluated",
        "release_candidate": "not_evaluated",
    }:
        errors.append("Domain and release completion must remain not_evaluated")


def validate_assets(
    manifest: dict[str, Any],
    errors: list[str],
) -> dict[str, str]:
    actual_digests: dict[str, str] = {}
    assets = manifest.get("assets", [])
    if len(assets) != 8:
        errors.append("manifest must contain exactly eight closure assets")
    for asset in assets:
        relative_path = asset.get("path")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append("manifest contains an invalid asset path")
            continue
        asset_path = PACKAGE_ROOT / relative_path
        if not asset_path.is_file():
            errors.append(f"missing asset: {relative_path}")
            continue
        actual_digest = calculate_file_digest(asset_path)
        actual_digests[relative_path] = actual_digest
        if actual_digest != asset.get("sha256"):
            errors.append(f"asset digest mismatch: {relative_path}")
    return actual_digests


def validate_closure(
    manifest: dict[str, Any],
    asset_digests: dict[str, str],
    errors: list[str],
) -> None:
    actual = calculate_closure_digest(asset_digests)
    if actual != manifest.get("closure_digest"):
        errors.append("closure digest mismatch")


def validate_acceptance(errors: list[str]) -> int:
    catalog = load_json(PACKAGE_ROOT / "acceptance-scenarios.json")
    if catalog.get("specification") != SPECIFICATION:
        errors.append("acceptance catalog specification mismatch")
    scenarios = catalog.get("scenarios", [])
    scenario_ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("acceptance scenario IDs must be unique")
    required_fields = {
        "scenario_id",
        "capability_group",
        "class",
        "given",
        "when",
        "expected",
    }
    observed_groups: set[str] = set()
    for index, scenario in enumerate(scenarios):
        missing = required_fields - scenario.keys()
        if missing:
            errors.append(f"scenario {index} missing fields: {sorted(missing)}")
        group = scenario.get("capability_group")
        if isinstance(group, str):
            observed_groups.add(group)
    if len(scenarios) < 40:
        errors.append("acceptance catalog must contain at least 40 scenarios")
    declared = set(catalog.get("required_capability_groups", []))
    if declared != REQUIRED_CAPABILITY_GROUPS:
        errors.append("declared required capability groups are incomplete")
    if not REQUIRED_CAPABILITY_GROUPS.issubset(observed_groups):
        errors.append("not every required capability group has a scenario")
    return len(scenarios)


def validate_bootstrap(errors: list[str]) -> None:
    profile = load_json(PACKAGE_ROOT / "bootstrap-profile.json")
    if profile.get("runtime_mode") != (
        "parallel_when_beneficial_with_serial_fallback"
    ):
        errors.append("bootstrap runtime mode must allow safe serial fallback")
    worker = profile.get("worker_execution", {})
    if worker.get("child_scope_expansion") is not False:
        errors.append("child workers must not expand scope")
    if worker.get("child_central_integration") is not False:
        errors.append("child workers must not perform central integration")
    admission = profile.get("parallel_admission", {})
    if admission.get("requires_positive_net_benefit") is not True:
        errors.append("parallel work must require positive net benefit")
    if admission.get("requires_mechanical_write_separation") is not True:
        errors.append("parallel work must require mechanical write separation")
    budgets = profile.get("budgets", {})
    required_budgets = {
        "agent_model_usage",
        "context_ingestion",
        "work_package_wall_time",
        "verification_execution",
        "recovery_attempts",
        "coordination",
        "stress_execution",
    }
    missing = required_budgets - budgets.keys()
    if missing:
        errors.append(f"bootstrap profile missing budgets: {sorted(missing)}")
    coordination = budgets.get("coordination", {})
    zero_token_fields = {
        "routine_event_agent_token_budget",
        "wait_polling_agent_token_budget",
        "join_evaluation_agent_token_budget",
        "invalidation_routing_agent_token_budget",
    }
    for field in zero_token_fields:
        if coordination.get(field) != 0:
            errors.append(f"coordination {field} must be zero")
    verification = budgets.get("verification_execution", {})
    if verification.get("unknown_duration_hard_deadline_seconds", 0) < 600:
        errors.append("unknown verification deadline must not restore 30s failure")
    if profile.get("external_operation_budget") != 0:
        errors.append("external operation budget must remain zero")


def validate_authority_text(errors: list[str]) -> None:
    goal = (PACKAGE_ROOT / "goal.md").read_text(encoding="utf-8")
    runtime = (PACKAGE_ROOT / "runtime-requirements.md").read_text(
        encoding="utf-8"
    )
    boundary = (PACKAGE_ROOT / "implementation-boundary.md").read_text(
        encoding="utf-8"
    )
    fixture = (
        PACKAGE_ROOT / "reference-parallel-subsystem-fixture.md"
    ).read_text(encoding="utf-8")
    contract = (PACKAGE_ROOT / "coordination-contract.md").read_text(
        encoding="utf-8"
    )
    combined = "\n".join([goal, runtime, boundary, fixture, contract])
    for module in REQUIRED_MODULES:
        if module not in fixture:
            errors.append(f"reference fixture missing Module: {module}")
    required_phrases = {
        "System Map is a maintained actual-architecture index": goal,
        "parallel_not_worthwhile": runtime,
        "boundary_active": runtime,
        "waiting_for_subsystem_join": runtime,
        "work_package_completed": combined,
        "subsystem_integrated": combined,
        "domain_accepted": combined,
        "release_candidate": combined,
        "not_evaluated": combined,
        "WriteAssignment": contract,
        "ContextEnvelope": contract,
        "IntegratedCandidateManifest": contract,
        "Full Verification Asset portfolio": boundary,
    }
    for phrase, text in required_phrases.items():
        if phrase not in text:
            errors.append(f"required authority phrase missing: {phrase}")


def build_result(errors: list[str], scenario_count: int) -> dict[str, Any]:
    passed = not errors
    return {
        "specification": SPECIFICATION,
        "terminal_state": "succeeded" if passed else "failed",
        "acceptance_outcome": "passed" if passed else "failed",
        "verification_completeness": "complete" if passed else "incomplete",
        "checked_assets": 8,
        "checked_scenarios": scenario_count,
        "checked_capability_groups": len(REQUIRED_CAPABILITY_GROUPS),
        "total_error_count": len(errors),
        "errors": errors,
    }


def main() -> int:
    errors: list[str] = []
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest, errors)
    asset_digests = validate_assets(manifest, errors)
    validate_closure(manifest, asset_digests, errors)
    scenario_count = validate_acceptance(errors)
    validate_bootstrap(errors)
    validate_authority_text(errors)
    result = build_result(errors, scenario_count)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

